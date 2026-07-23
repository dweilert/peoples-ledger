from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.phase1_acceptance import run_phase1_acceptance


REPO_ROOT = Path(__file__).resolve().parents[1]


class Phase1AcceptanceTests(unittest.TestCase):
    def test_phase1_acceptance_passes_for_bundled_poc(self) -> None:
        report = run_phase1_acceptance()
        self.assertTrue(report.passed)
        self.assertEqual(
            {check.name for check in report.checks},
            {
                "fixture_ingestion_validates",
                "deterministic_transform_applies",
                "ambiguous_transform_abstains",
                "report_traceability",
                "ledger_validation_fields",
                "browser_privacy_target_defined",
                "scope_boundaries_preserved",
                "ci_standard_gates_defined",
                "assurance_gate_passes",
            },
        )

    def test_phase1_acceptance_reports_failed_check(self) -> None:
        with patch("peoples_ledger.phase1_acceptance.validate_source_ingestion_fixtures", side_effect=ValueError("bad fixture")):
            report = run_phase1_acceptance()
        self.assertFalse(report.passed)
        failures = [check for check in report.checks if not check.passed]
        self.assertEqual(failures[0].name, "fixture_ingestion_validates")
        self.assertEqual(failures[0].detail, "bad fixture")

    def test_phase1_acceptance_fails_when_scope_boundaries_are_breached(self) -> None:
        unit = {
            "model_scenarios": [
                {
                    "id": "bad_scenario",
                    "uses_household_financial_data": True,
                    "model_type": "microsimulation_stub",
                }
            ]
        }
        with patch("peoples_ledger.phase1_acceptance.load_analysis_unit", return_value=unit):
            report = run_phase1_acceptance()
        failures = [check for check in report.checks if not check.passed]
        self.assertIn("scope_boundaries_preserved", {failure.name for failure in failures})

    def test_phase1_acceptance_cli_outputs_status(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "peoples_ledger.cli", "phase1-acceptance"],
            cwd=REPO_ROOT,
            env={"PYTHONPATH": "src"},
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["checks"])


if __name__ == "__main__":
    unittest.main()
