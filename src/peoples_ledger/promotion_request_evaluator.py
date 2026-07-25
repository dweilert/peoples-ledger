from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from peoples_ledger.paths import DATA_DIR, PHASE3_EVALUATOR_STATUS_ARTIFACT_DIR, SCHEMA_DIR
from peoples_ledger.schema_validator import SchemaRegistry


CONTRACT_EXAMPLES_PATH = DATA_DIR / "fixtures" / "phase3" / "promotion_evaluator_contract_examples.json"
STATUS_CONTRACT_PATH = DATA_DIR / "fixtures" / "phase3" / "promotion_evaluator_status_contract.json"
IMPLEMENTED_EXAMPLE_IDS = {
    "phase3_eval_example_schema_invalid_request",
    "phase3_eval_example_source_hash_mismatch",
    "phase3_eval_example_prompt_unapproved",
    "phase3_eval_example_privacy_marker",
    "phase3_eval_example_human_review_blocked",
    "phase3_eval_example_ledger_stub_missing",
    "phase3_eval_example_public_report_leak",
    "phase3_eval_example_unresolved_risk",
    "phase3_eval_example_disabled_hard_stop",
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


def build_promotion_evaluator_status(fixture_path: Path = CONTRACT_EXAMPLES_PATH) -> dict[str, Any]:
    fixture = _load_fixture(fixture_path)
    evaluations = [evaluate_contract_example(example["id"], fixture_path) for example in fixture["examples"]]

    return {
        "status": "blocked",
        "id": "phase3_promotion_evaluator_status_v1",
        "fixture_id": fixture["id"],
        "contract_ref": fixture["contract_ref"],
        "evaluation_count": len(evaluations),
        "gate_order": fixture["gate_order"],
        "first_failing_gates": [evaluation["first_failing_gate"] for evaluation in evaluations],
        "promotion_execution_allowed": False,
        "ledger_appended": False,
        "public_report_changed": False,
        "live_provider_called": False,
        "household_financial_data_storage_allowed": False,
        "evaluations": evaluations,
    }


def validate_promotion_evaluator_status_contract() -> dict[str, Any]:
    expected = json.loads(STATUS_CONTRACT_PATH.read_text(encoding="utf-8"))
    actual = promotion_evaluator_status_contract_view(build_promotion_evaluator_status())
    if actual != expected:
        raise ValueError("Phase 3 evaluator status contract snapshot mismatch")
    SchemaRegistry(SCHEMA_DIR).validate("phase3_promotion_evaluator_status", expected)
    if expected["status"] != "blocked":
        raise ValueError("Phase 3 evaluator status contract must remain blocked")
    if expected["mutation_flags"]["promotion_execution_allowed"]:
        raise ValueError("Phase 3 evaluator status contract cannot allow promotion execution")
    return expected


def export_promotion_evaluator_status_bundle(output_dir: Path = PHASE3_EVALUATOR_STATUS_ARTIFACT_DIR) -> dict[str, Any]:
    status = build_promotion_evaluator_status()
    contract_view = promotion_evaluator_status_contract_view(status)
    SchemaRegistry(SCHEMA_DIR).validate("phase3_promotion_evaluator_status", contract_view)
    if contract_view["mutation_flags"]["promotion_execution_allowed"]:
        raise ValueError("Phase 3 evaluator export cannot allow promotion execution")

    output_dir.mkdir(parents=True, exist_ok=True)
    status_path = output_dir / "phase3_promotion_evaluator_status.json"
    contract_path = output_dir / "phase3_promotion_evaluator_status_contract_view.json"
    manifest_path = output_dir / "phase3_promotion_evaluator_status.manifest.json"
    status_body = json.dumps(status, sort_keys=True, indent=2) + "\n"
    contract_body = json.dumps(contract_view, sort_keys=True, indent=2) + "\n"
    status_path.write_text(status_body, encoding="utf-8")
    contract_path.write_text(contract_body, encoding="utf-8")
    manifest = {
        "bundle_id": "phase3_promotion_evaluator_status_bundle",
        "publication_scope": "internal_phase3_evaluator_diagnostic_only",
        "status": contract_view["status"],
        "promotion_execution_allowed": contract_view["mutation_flags"]["promotion_execution_allowed"],
        "public_report_changed": contract_view["mutation_flags"]["public_report_changed"],
        "ledger_appended": contract_view["mutation_flags"]["ledger_appended"],
        "live_provider_called": contract_view["mutation_flags"]["live_provider_called"],
        "artifacts": [
            _artifact_entry("phase3_evaluator_status_json", status_path, status_body),
            _artifact_entry("phase3_evaluator_status_contract_view_json", contract_path, contract_body),
        ],
    }
    manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return {**manifest, "manifest_path": str(manifest_path)}


def promotion_evaluator_status_contract_view(status: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract_ref": status["contract_ref"],
        "evaluation_count": status["evaluation_count"],
        "evaluations": [
            {
                "blocker_codes": [blocker["code"] for blocker in evaluation["blockers"]],
                "candidate_analysis_unit_id": evaluation["candidate_analysis_unit_id"],
                "first_failing_gate": evaluation["first_failing_gate"],
                "household_financial_data_detected": evaluation["household_financial_data_detected"],
                "mutation_flags": {
                    "ledger_appended": evaluation["ledger_appended"],
                    "live_provider_called": evaluation["live_provider_called"],
                    "mutation_performed": evaluation["mutation_performed"],
                    "public_report_changed": evaluation["public_report_changed"],
                },
                "request_id": evaluation["request_id"],
                "status": evaluation["status"],
            }
            for evaluation in status["evaluations"]
        ],
        "first_failing_gates": status["first_failing_gates"],
        "fixture_id": status["fixture_id"],
        "gate_order": status["gate_order"],
        "household_financial_data_storage_allowed": status["household_financial_data_storage_allowed"],
        "id": status["id"],
        "mutation_flags": {
            "ledger_appended": status["ledger_appended"],
            "live_provider_called": status["live_provider_called"],
            "promotion_execution_allowed": status["promotion_execution_allowed"],
            "public_report_changed": status["public_report_changed"],
        },
        "status": status["status"],
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


def _artifact_entry(kind: str, path: Path, body: str) -> dict[str, Any]:
    encoded = body.encode("utf-8")
    return {
        "kind": kind,
        "path": str(path),
        "content_hash": "sha256:" + sha256(encoded).hexdigest(),
        "bytes": len(encoded),
    }
