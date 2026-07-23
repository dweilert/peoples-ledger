from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.candidate_promotion import (
    evaluate_candidate_promotion,
    evaluate_candidate_queue_promotion,
    validate_candidate_promotion_gate_reports,
)
from peoples_ledger.candidate_queue import load_candidate_analysis_queue
from peoples_ledger.paths import SCHEMA_DIR
from peoples_ledger.schema_validator import SchemaRegistry


class CandidatePromotionTests(unittest.TestCase):
    def test_promotion_report_is_structured_and_non_mutating(self) -> None:
        candidate = load_candidate_analysis_queue()[0]
        original = copy.deepcopy(candidate)

        report = evaluate_candidate_promotion(candidate)

        self.assertEqual(candidate, original)
        SchemaRegistry(SCHEMA_DIR).validate("candidate_promotion_gate_report", report)
        self.assertEqual(report["candidate_analysis_unit_id"], candidate["id"])
        self.assertEqual(report["publication_state_after_evaluation"], "draft")
        self.assertFalse(report["promotable"])

    def test_default_candidate_blocks_on_missing_phase2_gates(self) -> None:
        candidate = load_candidate_analysis_queue()[0]
        report = evaluate_candidate_promotion(candidate)

        self.assertEqual(
            [blocker["gate"] for blocker in report["blockers"]],
            ["prompt_template", "human_review", "ledger", "promotion_disabled"],
        )

    def test_schema_failure_returns_schema_blocker(self) -> None:
        candidate = copy.deepcopy(load_candidate_analysis_queue()[0])
        del candidate["title"]

        report = evaluate_candidate_promotion(candidate)

        self.assertEqual(report["candidate_analysis_unit_id"], candidate["id"])
        self.assertEqual([blocker["gate"] for blocker in report["blockers"]], ["schema"])
        self.assertFalse(report["promotable"])

    def test_source_snapshot_failure_returns_source_blocker(self) -> None:
        candidate = copy.deepcopy(load_candidate_analysis_queue()[0])
        candidate["source_snapshot_refs"][0]["content_hash"] = "sha256:wrong"

        report = evaluate_candidate_promotion(candidate)

        self.assertIn("source_snapshots", {blocker["gate"] for blocker in report["blockers"]})
        self.assertFalse(report["promotable"])

    def test_privacy_failure_returns_privacy_blocker(self) -> None:
        candidate = copy.deepcopy(load_candidate_analysis_queue()[0])
        candidate["privacy"]["egress_allowed"] = True

        report = evaluate_candidate_promotion(candidate)

        self.assertIn("privacy", {blocker["gate"] for blocker in report["blockers"]})
        self.assertFalse(report["promotable"])

    def test_all_nominal_requirements_still_block_until_promotion_is_implemented(self) -> None:
        candidate = copy.deepcopy(load_candidate_analysis_queue()[0])
        for gate in candidate["promotion_requirements"]:
            candidate["promotion_requirements"][gate] = True

        report = evaluate_candidate_promotion(candidate)

        self.assertEqual([blocker["gate"] for blocker in report["blockers"]], ["promotion_disabled"])
        self.assertFalse(report["promotable"])
        self.assertEqual(report["publication_state_after_evaluation"], "draft")

    def test_queue_promotion_reports_validate(self) -> None:
        candidates = load_candidate_analysis_queue()
        reports = evaluate_candidate_queue_promotion(candidates)

        self.assertEqual(len(reports), len(candidates))
        validate_candidate_promotion_gate_reports(candidates)


if __name__ == "__main__":
    unittest.main()
