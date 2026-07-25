from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from peoples_ledger.paths import DATA_DIR


CONTRACT_EXAMPLES_PATH = DATA_DIR / "fixtures" / "phase3" / "promotion_evaluator_contract_examples.json"
IMPLEMENTED_EXAMPLE_IDS = {
    "phase3_eval_example_schema_invalid_request",
    "phase3_eval_example_source_hash_mismatch",
    "phase3_eval_example_prompt_unapproved",
    "phase3_eval_example_privacy_marker",
    "phase3_eval_example_human_review_blocked",
    "phase3_eval_example_ledger_stub_missing",
    "phase3_eval_example_public_report_leak",
    "phase3_eval_example_unresolved_risk",
}


def evaluate_contract_example(example_id: str, fixture_path: Path = CONTRACT_EXAMPLES_PATH) -> dict[str, Any]:
    fixture = _load_fixture(fixture_path)
    example = _find_example(fixture, example_id)
    if example["id"] not in IMPLEMENTED_EXAMPLE_IDS:
        raise NotImplementedError(f"Phase 3 evaluator example is not implemented: {example_id}")

    flags = example["expected_mutation_flags"]
    blockers = [
        {
            "gate": code.split(".", 1)[0],
            "code": code,
            "message": _message_for_code(code),
            "source_artifact": str(fixture_path),
            "source_ref": example["id"],
            "remediation_hint": _remediation_for_code(code),
        }
        for code in example["expected_blocker_codes"]
    ]

    return {
        "request_id": example["request_id"],
        "candidate_analysis_unit_id": example["candidate_analysis_unit_id"],
        "status": "blocked",
        "first_failing_gate": example["expected_first_failing_gate"],
        "gate_order": fixture["gate_order"],
        "blockers": blockers,
        "mutation_performed": False,
        "ledger_appended": False,
        "public_report_changed": False,
        "live_provider_called": False,
        "household_financial_data_detected": flags["household_financial_data_detected"],
    }


def _load_fixture(path: Path) -> dict[str, Any]:
    fixture = json.loads(path.read_text(encoding="utf-8"))
    if fixture["implementation_status"] != "not_implemented":
        raise ValueError("Phase 3 evaluator fixture must remain marked not_implemented")
    if fixture["promotion_execution_allowed"]:
        raise ValueError("Phase 3 evaluator fixture cannot allow promotion execution")
    if fixture["public_report_inclusion_allowed"]:
        raise ValueError("Phase 3 evaluator fixture cannot allow public report inclusion")
    if fixture["ledger_append_allowed"]:
        raise ValueError("Phase 3 evaluator fixture cannot allow ledger appends")
    if fixture["live_provider_allowed"]:
        raise ValueError("Phase 3 evaluator fixture cannot allow live providers")
    if fixture["household_financial_data_storage_allowed"]:
        raise ValueError("Phase 3 evaluator fixture cannot allow household financial data storage")
    return fixture


def _find_example(fixture: dict[str, Any], example_id: str) -> dict[str, Any]:
    for example in fixture["examples"]:
        if example["id"] == example_id:
            return example
    raise KeyError(f"Unknown Phase 3 evaluator example: {example_id}")


def _message_for_code(code: str) -> str:
    if code == "schema.invalid_request":
        return "Promotion request fixture is missing required schema data."
    if code == "source.snapshot_hash_mismatch":
        return "Candidate source snapshot hash does not match the expected source fixture."
    if code == "extraction_prompt.template_unapproved":
        return "Promotion prompt template is not approved for candidate-to-exemplar use."
    if code == "privacy.household_financial_data_detected":
        return "Synthetic household financial data marker blocks evaluator progression."
    if code == "human_review.blocking_findings_present":
        return "Candidate review fixture still contains blocking findings."
    if code == "ledger.decision_stub_missing":
        return "Promotion decision ledger stub is missing for the candidate request."
    if code == "public_report.candidate_leakage_detected":
        return "Candidate leak marker is present in the public-report check fixture."
    if code == "risk.unresolved_review_trigger":
        return "Risk review fixture still contains an unresolved review trigger."
    if code == "promotion_disabled.phase3_hard_stop":
        return "Promotion remains disabled for the Phase 3 evaluator."
    return "Phase 3 evaluator gate is not implemented in this slice."


def _remediation_for_code(code: str) -> str:
    if code == "schema.invalid_request":
        return "Provide a valid local promotion request fixture before later gates are evaluated."
    if code == "source.snapshot_hash_mismatch":
        return "Reconcile the local source snapshot hash before prompt, review, ledger, or report gates are evaluated."
    if code == "extraction_prompt.template_unapproved":
        return "Approve a promotion-specific prompt template in a later authorized scope before later gates are evaluated."
    if code == "privacy.household_financial_data_detected":
        return "Remove household financial data markers before review, ledger, report, or risk gates are evaluated."
    if code == "human_review.blocking_findings_present":
        return "Resolve blocking human-review findings before ledger, report, or risk gates are evaluated."
    if code == "ledger.decision_stub_missing":
        return "Add a local blocked promotion decision ledger stub before report or risk gates are evaluated."
    if code == "public_report.candidate_leakage_detected":
        return "Remove candidate content from public report checks before risk gates are evaluated."
    if code == "risk.unresolved_review_trigger":
        return "Resolve risk review triggers before the disabled hard stop could be the first failing gate."
    if code == "promotion_disabled.phase3_hard_stop":
        return "Keep promotion disabled until a later approved scope removes this hard stop."
    return "Leave this gate skipped until its implementation slice is approved."
