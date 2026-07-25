from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.paths import DECISION_LEDGER_PATH
from peoples_ledger.promotion_request_evaluator import build_promotion_evaluator_status


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


if __name__ == "__main__":
    unittest.main()
