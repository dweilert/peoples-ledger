from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.assurance import run_assurance_gate, validation_results_from_report
from peoples_ledger.decision_ledger import DecisionLedger


class AssuranceTests(unittest.TestCase):
    def test_assurance_gate_passes_for_bundled_poc(self) -> None:
        report = run_assurance_gate()
        self.assertTrue(report.passed)
        self.assertTrue(report.publication_allowed)
        self.assertEqual(report.publication_state, "provisional_analysis")
        self.assertEqual(report.risk_tier, 1)
        self.assertEqual(report.review_triggers, [])
        self.assertEqual({check.name for check in report.checks}, {
            "schema_and_analysis_unit",
            "source_registry",
            "source_snapshots",
            "source_ingestion_fixtures",
            "source_acquisition_manifest",
            "candidate_analysis_queue",
            "candidate_promotion_gate_reports",
            "candidate_extraction_policy_registry",
            "candidate_extraction_ledger_stub",
            "candidate_review_records",
            "candidate_review_ledger_stub",
            "candidate_audit_bundle",
            "prompt_template_registry",
            "decision_ledger_integrity",
            "privacy_payload_guard",
        })

    def test_failed_validator_blocks_publication_advancement(self) -> None:
        with patch("peoples_ledger.assurance.load_source_snapshots", side_effect=ValueError("bad snapshot")):
            report = run_assurance_gate()
        self.assertFalse(report.passed)
        self.assertFalse(report.publication_allowed)
        self.assertEqual(report.publication_state, "blocked")
        self.assertEqual(report.risk_tier, 2)
        self.assertIn("assurance_failed:source_snapshots", report.review_triggers)

    def test_validation_results_are_derived_from_report(self) -> None:
        report = run_assurance_gate()
        self.assertEqual(
            validation_results_from_report(report),
            {
                "schema_valid": True,
                "citations_valid": True,
                "statutory_transform_valid": True,
                "calculation_valid": True,
                "privacy_egress_valid": True,
                "perspective_invariance_valid": True,
            },
        )

    def test_ledger_failure_is_reported_as_review_trigger(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"
            ledger_path.write_text('{"bad":"record"}\n', encoding="utf-8")
            with patch("peoples_ledger.assurance.DecisionLedger", return_value=DecisionLedger(ledger_path)):
                report = run_assurance_gate()
        self.assertFalse(report.publication_allowed)
        self.assertIn("assurance_failed:decision_ledger_integrity", report.review_triggers)


if __name__ == "__main__":
    unittest.main()
