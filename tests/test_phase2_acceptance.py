from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.phase2_acceptance import run_phase2_acceptance


REPO_ROOT = Path(__file__).resolve().parents[1]


class Phase2AcceptanceTests(unittest.TestCase):
    def test_phase2_acceptance_passes_for_current_poc(self) -> None:
        report = run_phase2_acceptance()

        self.assertTrue(report.passed)
        self.assertEqual(
            {check.name for check in report.checks},
            {
                "source_acquisition_candidates_validate",
                "candidate_queue_draft_only",
                "candidate_promotion_reports_block",
                "candidate_extraction_stub_validates",
                "candidate_status_surfaces_blockers",
                "frontend_candidate_status_target_defined",
                "public_report_excludes_candidates",
                "phase2_privacy_boundaries_preserved",
                "phase2_scope_boundaries_preserved",
                "ci_phase2_gate_defined",
                "assurance_gate_passes",
            },
        )

    def test_phase2_acceptance_reports_failed_check(self) -> None:
        with patch("peoples_ledger.phase2_acceptance.validate_candidate_analysis_queue", side_effect=ValueError("bad queue")):
            report = run_phase2_acceptance()

        self.assertFalse(report.passed)
        failures = [check for check in report.checks if not check.passed]
        self.assertIn("candidate_queue_draft_only", {failure.name for failure in failures})

    def test_phase2_acceptance_cli_outputs_status(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "peoples_ledger.cli", "phase2-acceptance"],
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
