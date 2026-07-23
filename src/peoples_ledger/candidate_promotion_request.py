from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .candidate_promotion import evaluate_candidate_promotion
from .candidate_queue import load_candidate_analysis_queue
from .paths import CANDIDATE_PROMOTION_REQUESTS_PATH, SCHEMA_DIR
from .privacy import HOUSEHOLD_FINANCIAL_KEYS, assert_no_household_financial_data
from .schema_validator import SchemaRegistry


REQUIRED_GATES = {
    "schema",
    "source",
    "extraction_prompt",
    "privacy",
    "human_review",
    "ledger",
    "public_report",
    "risk",
}


class CandidatePromotionRequestError(ValueError):
    """Raised when a promotion request weakens the Phase 2 blocked boundary."""


def load_candidate_promotion_requests(
    path: Path = CANDIDATE_PROMOTION_REQUESTS_PATH,
) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        requests = json.load(handle)
    _validate_requests(requests)
    return requests


def validate_candidate_promotion_requests(
    path: Path = CANDIDATE_PROMOTION_REQUESTS_PATH,
) -> None:
    load_candidate_promotion_requests(path)


def _validate_requests(requests: list[dict[str, Any]]) -> None:
    schema_registry = SchemaRegistry(SCHEMA_DIR)
    candidates = {candidate["id"]: candidate for candidate in load_candidate_analysis_queue()}

    request_ids: set[str] = set()
    for request in requests:
        assert_no_household_financial_data(request)
        _assert_no_household_markers(request)
        schema_registry.validate("candidate_promotion_request", request)
        if request["id"] in request_ids:
            raise CandidatePromotionRequestError(f"duplicate promotion request id: {request['id']}")
        request_ids.add(request["id"])
        candidate = candidates.get(request["candidate_analysis_unit_id"])
        if candidate is None:
            raise CandidatePromotionRequestError(
                f"promotion request references unknown candidate: {request['candidate_analysis_unit_id']}"
            )
        _validate_request_is_blocked(request)
        _validate_required_gates(request)
        _validate_source_refs(request, candidate)
        _validate_current_blockers(request, candidate)


def _validate_request_is_blocked(request: dict[str, Any]) -> None:
    if request["request_status"] != "blocked":
        raise CandidatePromotionRequestError(f"promotion request must remain blocked: {request['id']}")
    for field, allowed in request["execution_policy"].items():
        if allowed:
            raise CandidatePromotionRequestError(
                f"promotion request {request['id']} enables prohibited execution policy: {field}"
            )


def _assert_no_household_markers(request: dict[str, Any]) -> None:
    serialized = json.dumps(request, sort_keys=True).lower().replace("-", "_")
    markers = sorted(marker for marker in HOUSEHOLD_FINANCIAL_KEYS if marker in serialized)
    if markers:
        raise CandidatePromotionRequestError(
            f"promotion request contains household financial data markers: {markers}"
        )


def _validate_required_gates(request: dict[str, Any]) -> None:
    gates = set(request["required_gates"])
    missing = sorted(REQUIRED_GATES - gates)
    if missing:
        raise CandidatePromotionRequestError(f"promotion request missing required gates: {missing}")


def _validate_source_refs(request: dict[str, Any], candidate: dict[str, Any]) -> None:
    expected_refs = {
        (ref["source_record_id"], ref["content_hash"])
        for ref in candidate["source_snapshot_refs"]
    }
    actual_refs = {
        (ref["source_record_id"], ref["content_hash"])
        for ref in request["candidate_source_refs"]
    }
    if actual_refs != expected_refs:
        raise CandidatePromotionRequestError(
            f"promotion request source refs do not match candidate snapshots: {request['id']}"
        )


def _validate_current_blockers(request: dict[str, Any], candidate: dict[str, Any]) -> None:
    report = evaluate_candidate_promotion(candidate)
    expected_gates = {blocker["gate"] for blocker in report["blockers"]}
    actual_gates = {blocker["gate"] for blocker in request["current_blockers"]}
    missing = sorted(expected_gates - actual_gates)
    if missing:
        raise CandidatePromotionRequestError(
            f"promotion request blockers do not include current promotion report gates: {missing}"
        )
    if report["promotable"]:
        raise CandidatePromotionRequestError(
            f"promotion request unexpectedly references promotable candidate: {request['id']}"
        )
