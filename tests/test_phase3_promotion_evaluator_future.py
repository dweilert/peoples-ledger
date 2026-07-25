from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "data" / "fixtures" / "phase3" / "promotion_evaluator_contract_examples.json"


class Phase3PromotionEvaluatorFutureTests(unittest.TestCase):
    def test_future_cases_are_defined_before_implementation(self) -> None:
        fixture = _load_fixture()
        self.assertEqual(len(fixture["examples"]), 9)
        self.assertTrue((REPO_ROOT / "src" / "peoples_ledger" / "promotion_request_evaluator.py").exists())

    def test_future_invalid_request_fails_schema_first(self) -> None:
        result = _future_evaluate("phase3_eval_example_schema_invalid_request")
        self.assertEqual(result["first_failing_gate"], "schema")
        self.assertEqual(result["blockers"][0]["code"], "schema.invalid_request")
        self.assertIn("promotion_disabled.phase3_hard_stop", {blocker["code"] for blocker in result["blockers"]})
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["mutation_performed"])
        self.assertFalse(result["ledger_appended"])
        self.assertFalse(result["public_report_changed"])
        self.assertFalse(result["live_provider_called"])

    def test_future_source_hash_mismatch_fails_source_first(self) -> None:
        result = _future_evaluate("phase3_eval_example_source_hash_mismatch")
        self.assertEqual(result["first_failing_gate"], "source")
        self.assertEqual(result["blockers"][0]["code"], "source.snapshot_hash_mismatch")
        self.assertIn("promotion_disabled.phase3_hard_stop", {blocker["code"] for blocker in result["blockers"]})
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["mutation_performed"])
        self.assertFalse(result["ledger_appended"])
        self.assertFalse(result["public_report_changed"])
        self.assertFalse(result["live_provider_called"])

    def test_future_unapproved_prompt_fails_extraction_prompt_first(self) -> None:
        result = _future_evaluate("phase3_eval_example_prompt_unapproved")
        self.assertEqual(result["first_failing_gate"], "extraction_prompt")
        self.assertEqual(result["blockers"][0]["code"], "extraction_prompt.template_unapproved")
        self.assertIn("promotion_disabled.phase3_hard_stop", {blocker["code"] for blocker in result["blockers"]})
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["mutation_performed"])
        self.assertFalse(result["ledger_appended"])
        self.assertFalse(result["public_report_changed"])
        self.assertFalse(result["live_provider_called"])

    @unittest.skip("Future implementation intentionally blocked; household-data marker must fail privacy first.")
    def test_future_household_data_marker_fails_privacy_first(self) -> None:
        result = _future_evaluate("phase3_eval_example_privacy_marker")
        self.assertEqual(result["first_failing_gate"], "privacy")
        self.assertEqual(result["blockers"][0]["code"], "privacy.household_financial_data_detected")
        self.assertTrue(result["household_financial_data_detected"])

    @unittest.skip("Future implementation intentionally blocked; blocking review findings must fail human_review.")
    def test_future_blocking_review_fails_human_review_first(self) -> None:
        result = _future_evaluate("phase3_eval_example_human_review_blocked")
        self.assertEqual(result["first_failing_gate"], "human_review")
        self.assertEqual(result["blockers"][0]["code"], "human_review.blocking_findings_present")

    @unittest.skip("Future implementation intentionally blocked; missing decision stub must fail ledger.")
    def test_future_missing_decision_stub_fails_ledger_first(self) -> None:
        result = _future_evaluate("phase3_eval_example_ledger_stub_missing")
        self.assertEqual(result["first_failing_gate"], "ledger")
        self.assertEqual(result["blockers"][0]["code"], "ledger.decision_stub_missing")

    @unittest.skip("Future implementation intentionally blocked; public candidate leakage must fail public_report.")
    def test_future_candidate_leak_fails_public_report_first(self) -> None:
        result = _future_evaluate("phase3_eval_example_public_report_leak")
        self.assertEqual(result["first_failing_gate"], "public_report")
        self.assertEqual(result["blockers"][0]["code"], "public_report.candidate_leakage_detected")

    @unittest.skip("Future implementation intentionally blocked; unresolved risk trigger must fail risk.")
    def test_future_unresolved_risk_fails_risk_first(self) -> None:
        result = _future_evaluate("phase3_eval_example_unresolved_risk")
        self.assertEqual(result["first_failing_gate"], "risk")
        self.assertEqual(result["blockers"][0]["code"], "risk.unresolved_review_trigger")

    @unittest.skip("Future implementation intentionally blocked; otherwise clean request must still fail promotion_disabled.")
    def test_future_clean_request_still_fails_promotion_disabled(self) -> None:
        result = _future_evaluate("phase3_eval_example_disabled_hard_stop")
        self.assertEqual(result["first_failing_gate"], "promotion_disabled")
        self.assertEqual(result["blockers"][0]["code"], "promotion_disabled.phase3_hard_stop")
        self.assertFalse(result["mutation_performed"])
        self.assertFalse(result["ledger_appended"])
        self.assertFalse(result["public_report_changed"])
        self.assertFalse(result["live_provider_called"])


def _load_fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _future_evaluate(example_id: str) -> dict[str, object]:
    from peoples_ledger.promotion_request_evaluator import evaluate_contract_example

    return evaluate_contract_example(example_id)


if __name__ == "__main__":
    unittest.main()
