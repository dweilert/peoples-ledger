from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.candidate_extraction import (
    PROMPT_TEMPLATE_VERSION,
    record_candidate_locator_extraction,
    validate_candidate_extraction_stub,
)
from peoples_ledger.candidate_queue import load_candidate_analysis_queue
from peoples_ledger.decision_ledger import DecisionLedger
from peoples_ledger.privacy import HouseholdFinancialDataError


class CandidateExtractionTests(unittest.TestCase):
    def test_candidate_locator_extraction_records_restricted_ledger_entry(self) -> None:
        candidate = load_candidate_analysis_queue()[0]
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger = DecisionLedger(Path(tmpdir) / "ledger.jsonl")
            entry = record_candidate_locator_extraction(candidate, ledger)

            self.assertEqual(entry["analysis_unit_id"], candidate["id"])
            self.assertEqual(entry["action"], "candidate_locator_extraction")
            self.assertEqual(entry["decision_type"], "candidate_extraction_request")
            self.assertEqual(entry["prompt_template_version"], PROMPT_TEMPLATE_VERSION)
            self.assertEqual(entry["publication_state"], "machine_parsed")
            self.assertEqual(entry["disclosure_class"], "restricted")
            self.assertTrue(entry["human_review_required"])
            self.assertFalse(entry["structured_output"]["live_provider_called"])
            self.assertFalse(entry["structured_output"]["prompt_template_approved_for_promotion"])
            self.assertIn("candidate_promotion:disabled", entry["review_triggers"])
            self.assertEqual(ledger.read_all()[0]["id"], entry["id"])

    def test_candidate_locator_extraction_keeps_candidate_draft(self) -> None:
        candidate = load_candidate_analysis_queue()[0]
        original = copy.deepcopy(candidate)
        with tempfile.TemporaryDirectory() as tmpdir:
            record_candidate_locator_extraction(candidate, DecisionLedger(Path(tmpdir) / "ledger.jsonl"))

        self.assertEqual(candidate, original)
        self.assertEqual(candidate["publication_state"], "draft")

    def test_candidate_locator_extraction_uses_candidate_snapshot_hashes(self) -> None:
        candidate = load_candidate_analysis_queue()[0]
        with tempfile.TemporaryDirectory() as tmpdir:
            entry = record_candidate_locator_extraction(candidate, DecisionLedger(Path(tmpdir) / "ledger.jsonl"))

        self.assertEqual(
            entry["source_snapshot_ids"],
            [ref["source_record_id"] for ref in candidate["source_snapshot_refs"]],
        )
        self.assertEqual(entry["source_hashes"], [ref["content_hash"] for ref in candidate["source_snapshot_refs"]])

    def test_candidate_locator_extraction_rejects_household_payloads(self) -> None:
        candidate = copy.deepcopy(load_candidate_analysis_queue()[0])
        candidate["household_income"] = "private"

        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(HouseholdFinancialDataError):
                record_candidate_locator_extraction(candidate, DecisionLedger(Path(tmpdir) / "ledger.jsonl"))

    def test_candidate_extraction_stub_validates_without_real_ledger_append(self) -> None:
        candidates = load_candidate_analysis_queue()

        validate_candidate_extraction_stub(candidates)


if __name__ == "__main__":
    unittest.main()
