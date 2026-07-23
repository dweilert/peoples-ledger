from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.candidate_queue import (
    CandidatePromotionError,
    CandidateQueueError,
    assert_candidate_is_not_promotable,
    load_candidate_analysis_queue,
)
from peoples_ledger.paths import SCHEMA_DIR
from peoples_ledger.reporting import build_public_report
from peoples_ledger.schema_validator import SchemaRegistry
from peoples_ledger.source_acquisition import acquire_source_records_from_manifest


class CandidateQueueTests(unittest.TestCase):
    def test_candidate_queue_validates_draft_records(self) -> None:
        candidates = load_candidate_analysis_queue()

        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        SchemaRegistry(SCHEMA_DIR).validate("candidate_analysis_unit", candidate)
        self.assertEqual(candidate["status"], "draft")
        self.assertEqual(candidate["publication_state"], "draft")
        self.assertFalse(candidate["model_scenario_policy"]["allowed"])
        self.assertFalse(candidate["perspective_policy"]["allowed"])
        self.assertFalse(candidate["privacy"]["uses_household_financial_data"])
        self.assertFalse(candidate["privacy"]["egress_allowed"])

    def test_candidate_queue_links_to_acquired_source_snapshots(self) -> None:
        candidate = load_candidate_analysis_queue()[0]
        records, snapshots = acquire_source_records_from_manifest()

        self.assertEqual(
            {record["id"] for record in records},
            {ref["source_record_id"] for ref in candidate["source_snapshot_refs"]},
        )
        self.assertEqual(
            {snapshot["content_hash"] for snapshot in snapshots},
            {ref["content_hash"] for ref in candidate["source_snapshot_refs"]},
        )

    def test_candidate_ids_and_publication_states_are_deterministic(self) -> None:
        candidate = load_candidate_analysis_queue()[0]

        self.assertEqual(candidate["id"], "candidate_ira_2022_energy_tax_provisions")
        self.assertEqual(
            [provision["id"] for provision in candidate["candidate_provisions"]],
            ["candidate_ira_energy_credit_extensions", "candidate_ira_corporate_minimum_tax"],
        )
        self.assertEqual({provision["extraction_state"] for provision in candidate["candidate_provisions"]}, {"candidate_locator_only"})

    def test_candidate_is_not_promotable_until_gates_exist(self) -> None:
        candidate = load_candidate_analysis_queue()[0]

        with self.assertRaises(CandidatePromotionError):
            assert_candidate_is_not_promotable(candidate)

    def test_missing_source_snapshot_blocks_candidate_queue(self) -> None:
        candidates = load_candidate_analysis_queue()
        del candidates[0]["source_snapshot_refs"][0]

        with self.assertRaises(CandidateQueueError):
            load_candidate_analysis_queue(_write_candidates(candidates))

    def test_snapshot_hash_mismatch_blocks_candidate_queue(self) -> None:
        candidates = load_candidate_analysis_queue()
        candidates[0]["source_snapshot_refs"][0]["content_hash"] = "sha256:not-the-fixture-hash"

        with self.assertRaises(CandidateQueueError):
            load_candidate_analysis_queue(_write_candidates(candidates))

    def test_unknown_candidate_source_blocks_candidate_queue(self) -> None:
        candidates = load_candidate_analysis_queue()
        candidates[0]["candidate_provisions"][0]["source_record_ids"] = ["unknown_source"]

        with self.assertRaises(CandidateQueueError):
            load_candidate_analysis_queue(_write_candidates(candidates))

    def test_non_draft_candidate_state_fails_schema_validation(self) -> None:
        candidates = load_candidate_analysis_queue()
        candidates[0]["publication_state"] = "provisional_analysis"

        with self.assertRaises(ValueError):
            load_candidate_analysis_queue(_write_candidates(candidates))

    def test_candidate_queue_is_excluded_from_public_report(self) -> None:
        candidate_ids = {candidate["id"] for candidate in load_candidate_analysis_queue()}
        report = build_public_report()

        self.assertNotIn("candidate_analysis_units", report)
        self.assertNotIn(report["analysis_unit_id"], candidate_ids)
        self.assertFalse(candidate_ids & {provision["id"] for provision in report["provisions"]})


def _write_candidates(candidates: list[dict[str, object]]) -> Path:
    tempdir = tempfile.TemporaryDirectory()
    path = Path(tempdir.name) / "candidates.json"
    path.write_text(json.dumps(candidates), encoding="utf-8")
    _TEMP_DIRS.append(tempdir)
    return path


_TEMP_DIRS: list[tempfile.TemporaryDirectory[str]] = []


if __name__ == "__main__":
    unittest.main()
