from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.phase2_acceptance import run_phase2_acceptance


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "data" / "fixtures" / "phase3" / "promotion_evaluator_contract_examples.json"
CONTRACT_PATH = REPO_ROOT / "docs" / "phase-3-promotion-evaluator-contract.md"
README_PATH = REPO_ROOT / "README.md"
HANDOFF_PATH = REPO_ROOT / "docs" / "project-handoff.md"

EXPECTED_GATE_ORDER = [
    "schema",
    "source",
    "extraction_prompt",
    "privacy",
    "human_review",
    "ledger",
    "public_report",
    "risk",
    "promotion_disabled",
]

EXPECTED_PRIMARY_CODES = {
    "schema": "schema.invalid_request",
    "source": "source.snapshot_hash_mismatch",
    "extraction_prompt": "extraction_prompt.template_unapproved",
    "privacy": "privacy.household_financial_data_detected",
    "human_review": "human_review.blocking_findings_present",
    "ledger": "ledger.decision_stub_missing",
    "public_report": "public_report.candidate_leakage_detected",
    "risk": "risk.unresolved_review_trigger",
    "promotion_disabled": "promotion_disabled.phase3_hard_stop",
}


class Phase3PromotionEvaluatorFixtureTests(unittest.TestCase):
    def test_fixture_file_is_planning_only_and_disabled(self) -> None:
        fixture = _load_fixture()

        self.assertEqual(fixture["phase"], "phase3_planning_contract_examples")
        self.assertEqual(fixture["implementation_status"], "not_implemented")
        self.assertFalse(fixture["promotion_execution_allowed"])
        self.assertFalse(fixture["public_report_inclusion_allowed"])
        self.assertFalse(fixture["ledger_append_allowed"])
        self.assertFalse(fixture["live_provider_allowed"])
        self.assertFalse(fixture["household_financial_data_storage_allowed"])

    def test_fixture_gate_order_matches_contract(self) -> None:
        fixture = _load_fixture()
        contract = CONTRACT_PATH.read_text(encoding="utf-8")

        self.assertEqual(fixture["gate_order"], EXPECTED_GATE_ORDER)
        for index, gate in enumerate(EXPECTED_GATE_ORDER, start=1):
            self.assertIn(f"{index}. {gate}", contract)

    def test_fixture_has_one_example_for_each_first_failing_gate(self) -> None:
        fixture = _load_fixture()
        first_failing_gates = [example["expected_first_failing_gate"] for example in fixture["examples"]]

        self.assertEqual(first_failing_gates, EXPECTED_GATE_ORDER)

    def test_each_example_is_blocked_and_has_expected_primary_code(self) -> None:
        fixture = _load_fixture()

        for example in fixture["examples"]:
            gate = example["expected_first_failing_gate"]
            with self.subTest(example=example["id"]):
                self.assertEqual(example["expected_status"], "blocked")
                self.assertEqual(example["expected_primary_code"], EXPECTED_PRIMARY_CODES[gate])
                self.assertEqual(example["expected_blocker_codes"][0], EXPECTED_PRIMARY_CODES[gate])
                self.assertIn("promotion_disabled.phase3_hard_stop", example["expected_blocker_codes"])

    def test_all_examples_forbid_mutations_live_calls_and_public_report_changes(self) -> None:
        fixture = _load_fixture()

        for example in fixture["examples"]:
            flags = example["expected_mutation_flags"]
            with self.subTest(example=example["id"]):
                self.assertFalse(flags["mutation_performed"])
                self.assertFalse(flags["ledger_appended"])
                self.assertFalse(flags["public_report_changed"])
                self.assertFalse(flags["live_provider_called"])

    def test_privacy_example_uses_marker_only_and_precedes_later_gates(self) -> None:
        fixture = _load_fixture()
        privacy_example = _example_by_gate(fixture, "privacy")

        self.assertTrue(privacy_example["expected_mutation_flags"]["household_financial_data_detected"])
        self.assertIn("Synthetic household-data marker", privacy_example["description"])
        self.assertLess(
            fixture["gate_order"].index("privacy"),
            fixture["gate_order"].index("human_review"),
        )
        self.assertLess(
            fixture["gate_order"].index("privacy"),
            fixture["gate_order"].index("ledger"),
        )
        self.assertNotIn("$", json.dumps(privacy_example))

    def test_fixture_is_linked_from_readme_handoff_and_contract(self) -> None:
        for path in (README_PATH, HANDOFF_PATH, CONTRACT_PATH):
            with self.subTest(path=path.name):
                self.assertIn(
                    "data/fixtures/phase3/promotion_evaluator_contract_examples.json",
                    path.read_text(encoding="utf-8"),
                )

    def test_evaluator_implementation_is_schema_first_only(self) -> None:
        self.assertTrue((REPO_ROOT / "src" / "peoples_ledger" / "promotion_request_evaluator.py").exists())
        forbidden_paths = (REPO_ROOT / "src" / "peoples_ledger" / "candidate_promotion_evaluator.py",)

        for path in forbidden_paths:
            with self.subTest(path=path.name):
                self.assertFalse(path.exists())

    def test_phase2_acceptance_still_passes_with_phase3_fixtures(self) -> None:
        self.assertTrue(run_phase2_acceptance().passed)


def _load_fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _example_by_gate(fixture: dict[str, object], gate: str) -> dict[str, object]:
    examples = fixture["examples"]
    assert isinstance(examples, list)
    for example in examples:
        if example["expected_first_failing_gate"] == gate:
            return example
    raise AssertionError(f"missing example for gate {gate}")


if __name__ == "__main__":
    unittest.main()
