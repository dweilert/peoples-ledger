from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.analysis import load_analysis_unit
from peoples_ledger.challenge_agents import (
    DeterministicChallengeAgent,
    SourceCoverageChallengeAgent,
    compare_challenge_agents,
    record_challenge_comparison,
    record_challenge_review,
)
from peoples_ledger.decision_ledger import DecisionLedger


class ChallengeAgentTests(unittest.TestCase):
    def test_deterministic_challenge_agent_reports_nonblocking_disagreement(self) -> None:
        review = DeterministicChallengeAgent().review(load_analysis_unit())
        self.assertFalse(review.blocking)
        self.assertGreater(review.model_disagreement, 0)
        self.assertIn("Unknown indicator signals remain visible", " ".join(review.findings))
        self.assertEqual(review.review_triggers, [])

    def test_challenge_review_records_complete_decision_ledger_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger = DecisionLedger(Path(tmpdir) / "ledger.jsonl")
            entry = record_challenge_review(ledger)
            entries = ledger.read_all()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entry["decision_type"], "challenge_review")
        self.assertEqual(entry["actor"], "deterministic-challenge-agent")
        self.assertEqual(entry["model_disagreement"], 0.1)
        self.assertFalse(entry["human_review_required"])
        self.assertEqual(entry["review_triggers"], [])
        self.assertTrue(entry["validation_results"]["schema_valid"])
        self.assertTrue(entry["entry_hash"].startswith("sha256:"))

    def test_challenge_agent_blocks_under_representative_subset(self) -> None:
        unit = load_analysis_unit()
        unit["provisions"] = unit["provisions"][:3]
        review = DeterministicChallengeAgent().review(unit)
        self.assertTrue(review.blocking)
        self.assertIn("challenge:fewer_than_eight_provisions", review.review_triggers)
        self.assertGreaterEqual(review.model_disagreement, 0.28)

    def test_source_coverage_challenge_agent_checks_public_law_spans(self) -> None:
        review = SourceCoverageChallengeAgent().review(load_analysis_unit())
        self.assertFalse(review.blocking)
        self.assertEqual(review.model_disagreement, 0.06)
        self.assertIn("public-law spans for every provision", " ".join(review.findings))

    def test_source_coverage_challenge_blocks_missing_public_law_span(self) -> None:
        unit = load_analysis_unit()
        unit["provisions"][0]["source_spans"] = [{"source_record_id": "crs_salt_cap_2018", "locator": "x", "text_hash": "x"}]
        review = SourceCoverageChallengeAgent().review(unit)
        self.assertTrue(review.blocking)
        self.assertIn("challenge:missing_public_law_span", review.review_triggers)

    def test_challenge_agent_comparison_aggregates_reviews(self) -> None:
        comparison = compare_challenge_agents(load_analysis_unit())
        self.assertEqual(comparison["agent_count"], 2)
        self.assertFalse(comparison["blocking"])
        self.assertEqual(comparison["max_model_disagreement"], 0.1)
        self.assertEqual(comparison["review_triggers"], [])

    def test_challenge_agent_comparison_records_ledger_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger = DecisionLedger(Path(tmpdir) / "ledger.jsonl")
            entry = record_challenge_comparison(ledger)
            entries = ledger.read_all()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entry["decision_type"], "challenge_comparison")
        self.assertEqual(entry["structured_output"]["agent_count"], 2)
        self.assertEqual(entry["model_disagreement"], 0.1)
        self.assertFalse(entry["human_review_required"])


if __name__ == "__main__":
    unittest.main()
