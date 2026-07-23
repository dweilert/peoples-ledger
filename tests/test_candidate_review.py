from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.candidate_review import (
    CandidateReviewError,
    candidate_review_summary,
    load_candidate_review_records,
    record_candidate_review_decision,
    validate_candidate_review_ledger_stub,
    validate_candidate_review_records,
)
from peoples_ledger.decision_ledger import DecisionLedger
from peoples_ledger.paths import SCHEMA_DIR
from peoples_ledger.schema_validator import SchemaRegistry


class CandidateReviewTests(unittest.TestCase):
    def test_candidate_review_records_validate_and_block_promotion(self) -> None:
        records = load_candidate_review_records()

        self.assertEqual(len(records), 1)
        record = records[0]
        SchemaRegistry(SCHEMA_DIR).validate("candidate_review_record", record)
        self.assertEqual(record["candidate_analysis_unit_id"], "candidate_ira_2022_energy_tax_provisions")
        self.assertEqual(record["review_status"], "review_required")
        self.assertEqual(record["promotion_recommendation"], "blocked")
        self.assertEqual(record["publication_state_after_review"], "draft")
        self.assertTrue(record["ledger_entry_required"])
        self.assertFalse(record["uses_household_financial_data"])
        self.assertIn("blocking", {finding["severity"] for finding in record["findings"]})

    def test_candidate_review_summary_indexes_by_candidate_id(self) -> None:
        summary = candidate_review_summary()

        self.assertIn("candidate_ira_2022_energy_tax_provisions", summary)
        self.assertEqual(
            summary["candidate_ira_2022_energy_tax_provisions"]["id"],
            "candidate_review_ira_2022_energy_tax_provisions_initial",
        )

    def test_candidate_review_rejects_approved_status(self) -> None:
        records = _review_records()
        records[0]["review_status"] = "approved"

        with self.assertRaises(CandidateReviewError):
            validate_candidate_review_records(_write_reviews(records))

    def test_candidate_review_rejects_ready_for_promotion(self) -> None:
        records = _review_records()
        records[0]["promotion_recommendation"] = "ready_for_promotion"

        with self.assertRaises(CandidateReviewError):
            validate_candidate_review_records(_write_reviews(records))

    def test_candidate_review_rejects_unknown_candidate(self) -> None:
        records = _review_records()
        records[0]["candidate_analysis_unit_id"] = "unknown_candidate"

        with self.assertRaises(CandidateReviewError):
            validate_candidate_review_records(_write_reviews(records))

    def test_candidate_review_rejects_source_mismatch(self) -> None:
        records = _review_records()
        records[0]["source_snapshot_ids"] = ["pl117_169_public_law"]

        with self.assertRaises(CandidateReviewError):
            validate_candidate_review_records(_write_reviews(records))

    def test_candidate_review_rejects_household_data_flag(self) -> None:
        records = _review_records()
        records[0]["uses_household_financial_data"] = True

        with self.assertRaises(CandidateReviewError):
            validate_candidate_review_records(_write_reviews(records))

    def test_candidate_review_decision_records_restricted_ledger_entry(self) -> None:
        review = load_candidate_review_records()[0]
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger = DecisionLedger(Path(tmpdir) / "ledger.jsonl")
            entry = record_candidate_review_decision(review, ledger)

            self.assertEqual(entry["analysis_unit_id"], review["candidate_analysis_unit_id"])
            self.assertEqual(entry["action"], "candidate_human_review")
            self.assertEqual(entry["decision_type"], "candidate_review_blocked")
            self.assertEqual(entry["publication_state"], "machine_parsed")
            self.assertEqual(entry["disclosure_class"], "restricted")
            self.assertTrue(entry["human_review_required"])
            self.assertFalse(entry["structured_output"]["candidate_approval_granted"])
            self.assertEqual(entry["structured_output"]["promotion_recommendation"], "blocked")
            self.assertEqual(entry["structured_output"]["publication_state_after_review"], "draft")
            self.assertIn("candidate_review:blocked", entry["review_triggers"])
            self.assertEqual(ledger.read_all()[0]["id"], entry["id"])

    def test_candidate_review_ledger_stub_validates_with_temporary_ledger(self) -> None:
        validate_candidate_review_ledger_stub(load_candidate_review_records())


def _review_records() -> list[dict[str, object]]:
    return [copy.deepcopy(record) for record in load_candidate_review_records()]


def _write_reviews(records: list[dict[str, object]]) -> Path:
    tempdir = tempfile.TemporaryDirectory()
    path = Path(tempdir.name) / "candidate_review_records.json"
    path.write_text(json.dumps(records), encoding="utf-8")
    _TEMP_DIRS.append(tempdir)
    return path


_TEMP_DIRS: list[tempfile.TemporaryDirectory[str]] = []


if __name__ == "__main__":
    unittest.main()
