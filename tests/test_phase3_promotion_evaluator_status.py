from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.paths import DECISION_LEDGER_PATH
from peoples_ledger.promotion_request_evaluator import build_promotion_evaluator_status


REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_CONTRACT_PATH = REPO_ROOT / "data" / "fixtures" / "phase3" / "promotion_evaluator_status_contract.json"


def _status_contract_view(status: dict) -> dict:
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


class Phase3PromotionEvaluatorStatusTests(unittest.TestCase):
    def test_evaluator_status_is_read_only_and_blocked(self) -> None:
        before = DECISION_LEDGER_PATH.read_text(encoding="utf-8") if DECISION_LEDGER_PATH.exists() else ""

        status = build_promotion_evaluator_status()

        after = DECISION_LEDGER_PATH.read_text(encoding="utf-8") if DECISION_LEDGER_PATH.exists() else ""
        self.assertEqual(after, before)
        self.assertEqual(status["status"], "blocked")
        self.assertEqual(status["evaluation_count"], 9)
        self.assertFalse(status["promotion_execution_allowed"])
        self.assertFalse(status["ledger_appended"])
        self.assertFalse(status["public_report_changed"])
        self.assertFalse(status["live_provider_called"])
        self.assertFalse(status["household_financial_data_storage_allowed"])
        self.assertIn("promotion_disabled", status["first_failing_gates"])

    def test_evaluator_status_lists_deterministic_gate_order(self) -> None:
        status = build_promotion_evaluator_status()

        self.assertEqual(
            status["first_failing_gates"],
            [
                "schema",
                "source",
                "extraction_prompt",
                "privacy",
                "human_review",
                "ledger",
                "public_report",
                "risk",
                "promotion_disabled",
            ],
        )

    def test_evaluator_status_cli_outputs_json_without_ledger_append(self) -> None:
        before = DECISION_LEDGER_PATH.read_text(encoding="utf-8") if DECISION_LEDGER_PATH.exists() else ""
        result = subprocess.run(
            [sys.executable, "-m", "peoples_ledger.cli", "promotion-evaluator-status"],
            check=True,
            capture_output=True,
            cwd=Path(__file__).resolve().parents[1],
            env={"PYTHONPATH": "src"},
            text=True,
        )
        after = DECISION_LEDGER_PATH.read_text(encoding="utf-8") if DECISION_LEDGER_PATH.exists() else ""

        payload = json.loads(result.stdout)
        self.assertEqual(after, before)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["evaluation_count"], 9)
        self.assertFalse(payload["public_report_changed"])
        self.assertFalse(payload["live_provider_called"])

    def test_evaluator_status_matches_checked_contract_snapshot(self) -> None:
        expected = json.loads(STATUS_CONTRACT_PATH.read_text(encoding="utf-8"))

        self.assertEqual(_status_contract_view(build_promotion_evaluator_status()), expected)


if __name__ == "__main__":
    unittest.main()
