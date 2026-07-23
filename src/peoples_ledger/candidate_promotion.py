from __future__ import annotations

from typing import Any

from .paths import SCHEMA_DIR, SOURCE_ACQUISITION_MANIFEST_PATH
from .privacy import assert_no_household_financial_data
from .schema_validator import SchemaRegistry
from .source_acquisition import acquire_source_records_from_manifest, load_source_acquisition_manifest


POLICY_VERSION = "phase2-promotion-gate-poc-v1"


def evaluate_candidate_promotion(candidate: dict[str, Any]) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    schema_registry = SchemaRegistry(SCHEMA_DIR)
    candidate_id = candidate.get("id", "unknown_candidate")

    try:
        schema_registry.validate("candidate_analysis_unit", candidate)
    except Exception as exc:
        blockers.append({"gate": "schema", "reason": str(exc)})
        return _report(candidate_id, blockers)

    try:
        assert_no_household_financial_data(candidate)
    except Exception as exc:
        blockers.append({"gate": "privacy", "reason": str(exc)})

    _evaluate_source_snapshot_gate(candidate, blockers)
    _evaluate_policy_flags(candidate, blockers)
    blockers.append(
        {
            "gate": "promotion_disabled",
            "reason": "Phase 2 promotion gates are evaluative only and cannot advance candidate publication state.",
        }
    )
    return _report(candidate_id, blockers)


def evaluate_candidate_queue_promotion(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [evaluate_candidate_promotion(candidate) for candidate in candidates]


def validate_candidate_promotion_gate_reports(candidates: list[dict[str, Any]]) -> None:
    reports = evaluate_candidate_queue_promotion(candidates)
    for report in reports:
        SchemaRegistry(SCHEMA_DIR).validate("candidate_promotion_gate_report", report)
        if report["promotable"]:
            raise ValueError("Phase 2 candidate promotion reports must remain non-promotable")


def _evaluate_source_snapshot_gate(candidate: dict[str, Any], blockers: list[dict[str, str]]) -> None:
    try:
        manifest = load_source_acquisition_manifest(SOURCE_ACQUISITION_MANIFEST_PATH)
        records, snapshots = acquire_source_records_from_manifest(SOURCE_ACQUISITION_MANIFEST_PATH)
        if candidate["source_acquisition_manifest_id"] != manifest["id"]:
            raise ValueError("candidate references a different source acquisition manifest")

        record_ids = {record["id"] for record in records}
        snapshot_hashes = {snapshot["source_record_id"]: snapshot["content_hash"] for snapshot in snapshots}
        document_source_ids = set(candidate["legislative_document"]["source_record_ids"])
        snapshot_source_ids = {ref["source_record_id"] for ref in candidate["source_snapshot_refs"]}
        if document_source_ids != snapshot_source_ids:
            raise ValueError("candidate source snapshots do not match legislative document source refs")

        missing_sources = sorted(document_source_ids - record_ids)
        if missing_sources:
            raise ValueError(f"candidate references unknown source records: {missing_sources}")
        for ref in candidate["source_snapshot_refs"]:
            if ref["content_hash"] != snapshot_hashes.get(ref["source_record_id"]):
                raise ValueError(f"snapshot hash mismatch for {ref['source_record_id']}")
        for provision in candidate["candidate_provisions"]:
            missing = sorted(set(provision["source_record_ids"]) - record_ids)
            if missing:
                raise ValueError(f"candidate provision {provision['id']} references unknown source records: {missing}")
    except Exception as exc:
        blockers.append({"gate": "source_snapshots", "reason": str(exc)})


def _evaluate_policy_flags(candidate: dict[str, Any], blockers: list[dict[str, str]]) -> None:
    requirements = candidate["promotion_requirements"]
    if not requirements["schema_valid"]:
        blockers.append({"gate": "schema", "reason": "candidate has not passed schema validation for promotion"})
    if not requirements["source_snapshots_verified"]:
        blockers.append({"gate": "source_snapshots", "reason": "candidate source snapshots are not verified for promotion"})
    if not requirements["prompt_template_approved"]:
        blockers.append({"gate": "prompt_template", "reason": "candidate extraction prompt template is not approved"})
    if not requirements["privacy_checked"]:
        blockers.append({"gate": "privacy", "reason": "candidate privacy review is not complete"})
    if candidate["privacy"]["uses_household_financial_data"] or candidate["privacy"]["egress_allowed"]:
        blockers.append({"gate": "privacy", "reason": "candidate privacy policy permits prohibited household-data use or egress"})
    if not requirements["human_reviewed"]:
        blockers.append({"gate": "human_review", "reason": "candidate has not received required human review"})
    if not requirements["ledger_entry_recorded"]:
        blockers.append({"gate": "ledger", "reason": "candidate promotion decision has no AI Decision Ledger entry"})


def _report(candidate_id: str, blockers: list[dict[str, str]]) -> dict[str, Any]:
    report = {
        "candidate_analysis_unit_id": candidate_id,
        "policy_version": POLICY_VERSION,
        "target_publication_state": "provisional_analysis",
        "publication_state_after_evaluation": "draft",
        "promotable": False,
        "blockers": blockers,
    }
    SchemaRegistry(SCHEMA_DIR).validate("candidate_promotion_gate_report", report)
    return report
