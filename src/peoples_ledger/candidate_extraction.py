from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from .candidate_extraction_policy import CandidateExtractionPolicyRegistry
from .candidate_promotion import evaluate_candidate_promotion
from .decision_ledger import DecisionLedger
from .privacy import assert_no_household_financial_data
from .schema_validator import SchemaRegistry
from .paths import SCHEMA_DIR


PROMPT_TEMPLATE_VERSION = "candidate-locator-extraction-poc-v1"
DETERMINISTIC_PROVIDER = "deterministic-candidate-extractor"


def record_candidate_locator_extraction(candidate: dict[str, Any], ledger: DecisionLedger | None = None) -> dict[str, Any]:
    assert_no_household_financial_data(candidate)
    SchemaRegistry(SCHEMA_DIR).validate("candidate_analysis_unit", candidate)
    ledger = ledger or DecisionLedger()
    source_snapshot_ids = [ref["source_record_id"] for ref in candidate["source_snapshot_refs"]]
    source_hashes = [ref["content_hash"] for ref in candidate["source_snapshot_refs"]]
    policy = CandidateExtractionPolicyRegistry.load().require_dry_run(
        version=PROMPT_TEMPLATE_VERSION,
        task="candidate_locator_extraction",
        source_refs=source_snapshot_ids,
    )
    provision_outputs = [
        {
            "candidate_provision_id": provision["id"],
            "label": provision["label"],
            "locator_hints": provision["locator_hints"],
            "extraction_state": provision["extraction_state"],
        }
        for provision in candidate["candidate_provisions"]
    ]
    promotion_report = evaluate_candidate_promotion(candidate)

    return ledger.append(
        analysis_unit_id=candidate["id"],
        actor=DETERMINISTIC_PROVIDER,
        action="candidate_locator_extraction",
        decision_type="candidate_extraction_request",
        model={"provider": policy["provider"], "name": policy["model"]["name"], "version": policy["model"]["version"]},
        prompt_template_version=policy["version"],
        source_snapshot_ids=source_snapshot_ids,
        source_hashes=source_hashes,
        baseline_id="phase2_candidate_no_model",
        model_scenario_id="phase2_no_model_scenario",
        structured_output={
            "candidate_analysis_unit_id": candidate["id"],
            "candidate_provisions": provision_outputs,
            "prompt_template_approved_for_promotion": False,
            "candidate_extraction_policy_status": policy["status"],
            "live_provider_called": False,
            "promotion_gate_report": promotion_report,
        },
        calibrated_confidence=0.0,
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
            "candidate_prompt_template:not_approved_for_promotion",
            "candidate_promotion:disabled",
            "candidate_publication:draft_only",
        ],
        disclosure_class="restricted",
        redaction_reason="Phase 2 candidate extraction requests are not public report material.",
        structured_input_pointer="none://candidate-queue-fixture",
        input_storage_class="none",
        input_retention_days=0,
        input_refs=source_snapshot_ids,
        output_refs=[candidate["id"], *[provision["id"] for provision in candidate["candidate_provisions"]]],
        rationale="Deterministic Phase 2 locator-extraction ledger stub for a draft candidate analysis unit.",
        payload={"candidate_id": candidate["id"], "source_snapshot_ids": source_snapshot_ids},
    )


def validate_candidate_extraction_stub(candidates: list[dict[str, Any]]) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger = DecisionLedger(Path(tmpdir) / "candidate_extraction_ledger.jsonl")
        for candidate in candidates:
            entry = record_candidate_locator_extraction(candidate, ledger)
            SchemaRegistry(SCHEMA_DIR).validate("ai_decision_ledger_entry", entry)
        ledger.read_all()
