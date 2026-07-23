from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.candidate_promotion_decision import (
    CandidatePromotionDecisionError,
    load_candidate_promotion_decision_ledger_stubs,
    validate_candidate_promotion_decision_ledger_stubs,
)
from peoples_ledger.decision_ledger import DecisionLedger, compute_entry_hash
from peoples_ledger.paths import SCHEMA_DIR
from peoples_ledger.schema_validator import SchemaRegistry


class CandidatePromotionDecisionTests(unittest.TestCase):
    def test_promotion_decision_ledger_stub_validates(self) -> None:
        entries = load_candidate_promotion_decision_ledger_stubs()

        self.assertEqual(len(entries), 1)
        entry = entries[0]
        SchemaRegistry(SCHEMA_DIR).validate("ai_decision_ledger_entry", entry)
        self.assertEqual(entry["entry_hash"], compute_entry_hash(entry))
        self.assertEqual(entry["decision_type"], "candidate_promotion_blocked")
        self.assertEqual(entry["action"], "candidate_promotion_decision_stub")

    def test_promotion_decision_stub_is_blocked_and_restricted(self) -> None:
        entry = load_candidate_promotion_decision_ledger_stubs()[0]
        output = entry["structured_output"]

        self.assertEqual(output["promotion_decision"], "blocked")
        self.assertFalse(output["promotion_executed"])
        self.assertFalse(output["live_provider_called"])
        self.assertFalse(output["public_report_inclusion_allowed"])
        self.assertFalse(output["live_ledger_append_allowed"])
        self.assertEqual(output["publication_state_after_decision"], "draft")
        self.assertEqual(entry["disclosure_class"], "restricted")
        self.assertTrue(entry["human_review_required"])
        self.assertFalse(entry["household_financial_data_present"])

    def test_promotion_decision_stub_links_to_request_and_sources(self) -> None:
        entry = load_candidate_promotion_decision_ledger_stubs()[0]

        self.assertEqual(
            entry["structured_output"]["candidate_promotion_request_id"],
            "promotion_request_candidate_ira_2022_energy_tax_provisions_v1",
        )
        self.assertEqual(
            entry["source_snapshot_ids"],
            ["pl117_169_public_law", "jct_ira_estimated_budget_effects_2022"],
        )
        self.assertEqual(
            entry["structured_output"]["blocker_gates"],
            ["prompt_template", "human_review", "ledger", "promotion_disabled"],
        )

    def test_promotion_decision_stub_is_not_in_live_ledger(self) -> None:
        entry = load_candidate_promotion_decision_ledger_stubs()[0]
        live_ids = {ledger_entry["id"] for ledger_entry in DecisionLedger().read_all()}

        self.assertNotIn(entry["id"], live_ids)

    def test_modified_stub_with_bad_hash_fails(self) -> None:
        entries = _fixture_copy()
        entries[0]["rationale"] = "changed after hash"

        with self.assertRaises(CandidatePromotionDecisionError):
            _validate_temp_fixture(entries)

    def test_modified_stub_with_promotion_execution_fails(self) -> None:
        entries = _fixture_copy()
        entries[0]["structured_output"]["promotion_executed"] = True
        entries[0]["entry_hash"] = compute_entry_hash(entries[0])

        with self.assertRaises(CandidatePromotionDecisionError):
            _validate_temp_fixture(entries)

    def test_modified_stub_with_missing_request_ref_fails(self) -> None:
        entries = _fixture_copy()
        entries[0]["structured_output"]["candidate_promotion_request_id"] = "missing_request"
        entries[0]["entry_hash"] = compute_entry_hash(entries[0])

        with self.assertRaises(CandidatePromotionDecisionError):
            _validate_temp_fixture(entries)

    def test_stub_fails_if_already_appended_to_live_ledger(self) -> None:
        entry = _fixture_copy()[0]
        with patch.object(DecisionLedger, "read_all", return_value=[entry]):
            with self.assertRaises(CandidatePromotionDecisionError):
                validate_candidate_promotion_decision_ledger_stubs()


def _fixture_copy() -> list[dict[str, object]]:
    return copy.deepcopy(load_candidate_promotion_decision_ledger_stubs())


def _validate_temp_fixture(entries: list[dict[str, object]]) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "promotion_decision_stub.json"
        path.write_text(json.dumps(entries), encoding="utf-8")
        validate_candidate_promotion_decision_ledger_stubs(path)


if __name__ == "__main__":
    unittest.main()
