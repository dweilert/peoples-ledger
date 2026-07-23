from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.corrections import load_correction_record, record_correction
from peoples_ledger.decision_ledger import DecisionLedger
from peoples_ledger.paths import SCHEMA_DIR
from peoples_ledger.reporting import build_public_report
from peoples_ledger.schema_validator import SchemaRegistry


class CorrectionTests(unittest.TestCase):
    def test_correction_fixture_validates_and_preserves_regression_reference(self) -> None:
        correction = load_correction_record()
        SchemaRegistry(SCHEMA_DIR).validate("correction_record", correction)
        self.assertEqual(correction["publication_state"], "corrected")
        self.assertIn("tests/test_corrections.py", correction["regression_test_ref"])
        self.assertEqual(correction["supersedes_decision_id"], "adl_manual_tcja_representative_subset")

    def test_record_correction_writes_superseding_ledger_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger = DecisionLedger(Path(tmpdir) / "ledger.jsonl")
            entry = record_correction(ledger=ledger)
            entries = ledger.read_all()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entry["decision_type"], "correction")
        self.assertEqual(entry["publication_state"], "corrected")
        self.assertEqual(entry["supersedes_decision_id"], "adl_manual_tcja_representative_subset")
        self.assertEqual(entry["structured_output"]["correction"]["id"], "corr_tcja_salt_locator_poc")
        self.assertTrue(entry["entry_hash"].startswith("sha256:"))

    def test_public_report_surfaces_correction_records(self) -> None:
        report = build_public_report()
        self.assertEqual(len(report["corrections"]), 1)
        self.assertEqual(report["corrections"][0]["id"], "corr_tcja_salt_locator_poc")
        self.assertEqual(report["corrections"][0]["publication_state"], "corrected")


if __name__ == "__main__":
    unittest.main()
