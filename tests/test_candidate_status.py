from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.candidate_status import build_candidate_status
from peoples_ledger.paths import DECISION_LEDGER_PATH


class CandidateStatusTests(unittest.TestCase):
    def test_candidate_status_summarizes_draft_queue_without_reporting_or_ledger_append(self) -> None:
        before = DECISION_LEDGER_PATH.read_text(encoding="utf-8") if DECISION_LEDGER_PATH.exists() else ""

        status = build_candidate_status()

        after = DECISION_LEDGER_PATH.read_text(encoding="utf-8") if DECISION_LEDGER_PATH.exists() else ""
        self.assertEqual(after, before)
        self.assertEqual(status["status"], "ok")
        self.assertEqual(status["candidate_count"], 1)
        self.assertFalse(status["public_report_includes_candidates"])
        self.assertFalse(status["ledger_appended"])
        candidate = status["candidates"][0]
        self.assertEqual(candidate["id"], "candidate_ira_2022_energy_tax_provisions")
        self.assertEqual(candidate["publication_state"], "draft")
        self.assertFalse(candidate["model_scenario_allowed"])
        self.assertFalse(candidate["perspective_allowed"])
        self.assertFalse(candidate["uses_household_financial_data"])
        self.assertFalse(candidate["egress_allowed"])
        self.assertFalse(candidate["promotable"])
        self.assertIn("promotion_disabled", {blocker["gate"] for blocker in candidate["promotion_blockers"]})

    def test_candidate_status_cli_outputs_json(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "peoples_ledger.cli", "candidate-status"],
            check=True,
            capture_output=True,
            cwd=Path(__file__).resolve().parents[1],
            env={"PYTHONPATH": "src"},
            text=True,
        )

        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["candidate_count"], 1)
        self.assertEqual(payload["candidates"][0]["publication_state"], "draft")


if __name__ == "__main__":
    unittest.main()
