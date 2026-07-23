from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from .candidate_queue import load_candidate_analysis_queue
from .decision_ledger import DecisionLedger
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


def record_candidate_review_decision(review: dict[str, Any], ledger: DecisionLedger | None = None) -> dict[str, Any]:
    assert_no_household_financial_data(review)
    SchemaRegistry(SCHEMA_DIR).validate("candidate_review_record", review)
    _validate_review_links([review])
    ledger = ledger or DecisionLedger()
    blocker_ids = [finding["id"] for finding in review["findings"] if finding["severity"] == "blocking"]

    return ledger.append(
        analysis_unit_id=review["candidate_analysis_unit_id"],
        actor=review["reviewer"],
        action="candidate_human_review",
        decision_type="candidate_review_blocked",
        model={"provider": review["reviewer"], "name": "human-review-stub", "version": "1.0"},
        prompt_template_version="candidate-human-review-stub-v1",
        source_snapshot_ids=review["source_snapshot_ids"],
        source_hashes=[f"candidate-review-source:{source_id}" for source_id in review["source_snapshot_ids"]],
        baseline_id="phase2_candidate_no_model",
        model_scenario_id="phase2_no_model_scenario",
        structured_output={
            "candidate_review_record_id": review["id"],
            "review_status": review["review_status"],
            "promotion_recommendation": review["promotion_recommendation"],
            "publication_state_after_review": review["publication_state_after_review"],
            "blocking_finding_ids": blocker_ids,
            "required_followups": review["required_followups"],
            "candidate_approval_granted": False,
        },
        calibrated_confidence=1.0,
        model_disagreement=0.0,
        validation_results={
            "schema_valid": True,
            "citations_valid": True,
            "statutory_transform_valid": False,
            "calculation_valid": True,
            "privacy_egress_valid": True,
            "perspective_invariance_valid": True,
        },
        risk_tier=3,
        publication_lane="provisional_analytical",
        publication_state="machine_parsed",
        human_review_required=True,
        review_triggers=[
            "candidate_review:blocked",
            "candidate_publication:draft_only",
            "candidate_promotion:disabled",
        ],
        disclosure_class="restricted",
        redaction_reason="Phase 2 candidate review decisions are not public report material.",
        structured_input_pointer=f"fixture://candidate_reviews/{review['id']}",
        input_storage_class="public_summary",
        input_retention_days=0,
        input_refs=[review["id"], *review["source_snapshot_ids"]],
        output_refs=[review["candidate_analysis_unit_id"], *review["candidate_provision_ids"]],
        rationale="Deterministic Phase 2 human-review stub records a blocked candidate review decision.",
        payload={
            "candidate_review_record_id": review["id"],
            "candidate_analysis_unit_id": review["candidate_analysis_unit_id"],
            "blocking_finding_ids": blocker_ids,
        },
    )


def validate_candidate_review_ledger_stub(records: list[dict[str, Any]] | None = None) -> None:
    records = records or load_candidate_review_records()
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger = DecisionLedger(Path(tmpdir) / "candidate_review_ledger.jsonl")
        for review in records:
            entry = record_candidate_review_decision(review, ledger)
            SchemaRegistry(SCHEMA_DIR).validate("ai_decision_ledger_entry", entry)
        ledger.read_all()


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
