from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .candidate_promotion_request import load_candidate_promotion_requests
from .decision_ledger import DecisionLedger, compute_entry_hash
from .paths import CANDIDATE_PROMOTION_DECISION_LEDGER_STUB_PATH, SCHEMA_DIR
from .privacy import assert_no_household_financial_data
from .schema_validator import SchemaRegistry


class CandidatePromotionDecisionError(ValueError):
    """Raised when a promotion decision ledger stub implies live promotion."""


def load_candidate_promotion_decision_ledger_stubs(
    path: Path = CANDIDATE_PROMOTION_DECISION_LEDGER_STUB_PATH,
) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        entries = json.load(handle)
    _validate_promotion_decision_stubs(entries)
    return entries


def validate_candidate_promotion_decision_ledger_stubs(
    path: Path = CANDIDATE_PROMOTION_DECISION_LEDGER_STUB_PATH,
) -> None:
    load_candidate_promotion_decision_ledger_stubs(path)


def _validate_promotion_decision_stubs(entries: list[dict[str, Any]]) -> None:
    schema_registry = SchemaRegistry(SCHEMA_DIR)
    requests = {request["id"]: request for request in load_candidate_promotion_requests()}
    live_ledger_ids = {entry["id"] for entry in DecisionLedger().read_all()}

    seen: set[str] = set()
    for entry in entries:
        assert_no_household_financial_data(entry)
        schema_registry.validate("ai_decision_ledger_entry", entry)
        if entry["id"] in seen:
            raise CandidatePromotionDecisionError(f"duplicate promotion decision stub id: {entry['id']}")
        seen.add(entry["id"])
        if entry["id"] in live_ledger_ids:
            raise CandidatePromotionDecisionError(
                f"promotion decision stub was appended to the live ledger: {entry['id']}"
            )
        _validate_entry_hash(entry)
        _validate_blocked_decision(entry)
        _validate_request_links(entry, requests)


def _validate_entry_hash(entry: dict[str, Any]) -> None:
    if entry["entry_hash"] != compute_entry_hash(entry):
        raise CandidatePromotionDecisionError(f"promotion decision stub hash mismatch: {entry['id']}")


def _validate_blocked_decision(entry: dict[str, Any]) -> None:
    output = entry["structured_output"]
    if entry["decision_type"] != "candidate_promotion_blocked":
        raise CandidatePromotionDecisionError(f"promotion decision stub has unsafe decision type: {entry['id']}")
    if entry["action"] != "candidate_promotion_decision_stub":
        raise CandidatePromotionDecisionError(f"promotion decision stub has unsafe action: {entry['id']}")
    if output["promotion_decision"] != "blocked":
        raise CandidatePromotionDecisionError(f"promotion decision stub is not blocked: {entry['id']}")
    prohibited_fields = (
        "promotion_executed",
        "live_provider_called",
        "public_report_inclusion_allowed",
        "live_ledger_append_allowed",
    )
    for field in prohibited_fields:
        if output[field]:
            raise CandidatePromotionDecisionError(f"promotion decision stub enables prohibited output: {field}")
    if output["publication_state_after_decision"] != "draft":
        raise CandidatePromotionDecisionError(f"promotion decision stub does not keep candidate draft: {entry['id']}")
    if not entry["human_review_required"]:
        raise CandidatePromotionDecisionError(f"promotion decision stub must require human review: {entry['id']}")
    if entry["disclosure_class"] != "restricted":
        raise CandidatePromotionDecisionError(f"promotion decision stub must remain restricted: {entry['id']}")
    if entry["household_financial_data_present"]:
        raise CandidatePromotionDecisionError(f"promotion decision stub flags household data: {entry['id']}")


def _validate_request_links(
    entry: dict[str, Any],
    requests: dict[str, dict[str, Any]],
) -> None:
    output = entry["structured_output"]
    request_id = output["candidate_promotion_request_id"]
    request = requests.get(request_id)
    if request is None:
        raise CandidatePromotionDecisionError(f"promotion decision stub references unknown request: {request_id}")
    if entry["analysis_unit_id"] != request["candidate_analysis_unit_id"]:
        raise CandidatePromotionDecisionError("promotion decision stub candidate does not match request")
    if output["candidate_analysis_unit_id"] != request["candidate_analysis_unit_id"]:
        raise CandidatePromotionDecisionError("promotion decision structured output candidate does not match request")
    if set(entry["source_snapshot_ids"]) != {ref["source_record_id"] for ref in request["candidate_source_refs"]}:
        raise CandidatePromotionDecisionError("promotion decision source refs do not match request")
    if set(entry["source_hashes"]) != {ref["content_hash"] for ref in request["candidate_source_refs"]}:
        raise CandidatePromotionDecisionError("promotion decision source hashes do not match request")

    if {blocker["gate"] for blocker in request["current_blockers"]} - set(output["blocker_gates"]):
        raise CandidatePromotionDecisionError("promotion decision blocker gates do not cover request blockers")
