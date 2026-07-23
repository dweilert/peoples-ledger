from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .candidate_queue import load_candidate_analysis_queue
from .paths import CANDIDATE_REVIEW_RECORDS_PATH, SCHEMA_DIR
from .privacy import assert_no_household_financial_data
from .schema_validator import SchemaRegistry


class CandidateReviewError(ValueError):
    """Raised when Phase 2 candidate review records imply unsafe promotion."""


def load_candidate_review_records(path: Path = CANDIDATE_REVIEW_RECORDS_PATH) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        records = json.load(handle)
    schema_registry = SchemaRegistry(SCHEMA_DIR)
    for record in records:
        assert_no_household_financial_data(record)
        schema_registry.validate("candidate_review_record", record)
    _validate_review_links(records)
    return records


def validate_candidate_review_records(path: Path = CANDIDATE_REVIEW_RECORDS_PATH) -> None:
    load_candidate_review_records(path)


def candidate_review_summary() -> dict[str, dict[str, Any]]:
    records = load_candidate_review_records()
    return {record["candidate_analysis_unit_id"]: record for record in records}


def _validate_review_links(records: list[dict[str, Any]]) -> None:
    candidates = {candidate["id"]: candidate for candidate in load_candidate_analysis_queue()}
    seen: set[str] = set()
    for record in records:
        if record["id"] in seen:
            raise CandidateReviewError(f"duplicate candidate review record id: {record['id']}")
        seen.add(record["id"])
        try:
            candidate = candidates[record["candidate_analysis_unit_id"]]
        except KeyError as exc:
            raise CandidateReviewError(f"review references unknown candidate: {record['candidate_analysis_unit_id']}") from exc
        candidate_source_ids = {ref["source_record_id"] for ref in candidate["source_snapshot_refs"]}
        if set(record["source_snapshot_ids"]) != candidate_source_ids:
            raise CandidateReviewError(f"review source refs do not match candidate: {record['id']}")
        candidate_provision_ids = {provision["id"] for provision in candidate["candidate_provisions"]}
        if set(record["candidate_provision_ids"]) != candidate_provision_ids:
            raise CandidateReviewError(f"review provision refs do not match candidate: {record['id']}")
        if record["review_status"] == "approved":
            raise CandidateReviewError(f"Phase 2 review records cannot approve promotion: {record['id']}")
        if record["promotion_recommendation"] != "blocked":
            raise CandidateReviewError(f"Phase 2 review records must block promotion: {record['id']}")
        if record["publication_state_after_review"] != "draft":
            raise CandidateReviewError(f"Phase 2 review records must keep candidates draft: {record['id']}")
        if not record["ledger_entry_required"]:
            raise CandidateReviewError(f"Phase 2 review records must require a ledger entry: {record['id']}")
        if record["uses_household_financial_data"]:
            raise CandidateReviewError(f"candidate review uses household data: {record['id']}")
        if not any(finding["severity"] == "blocking" for finding in record["findings"]):
            raise CandidateReviewError(f"candidate review must include a blocking finding: {record['id']}")
