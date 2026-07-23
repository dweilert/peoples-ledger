from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.assurance import run_assurance_gate
from peoples_ledger.analysis import load_analysis_unit
from peoples_ledger.challenge_agents import ChallengeReview, DeterministicChallengeAgent
from peoples_ledger.publication import decide_publication_state


class PublicationTests(unittest.TestCase):
    def test_publication_advances_when_assurance_and_challenge_pass(self) -> None:
        assurance = run_assurance_gate()
        challenge = DeterministicChallengeAgent().review(load_analysis_unit())
        decision = decide_publication_state(assurance, challenge)
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.state, "provisional_analysis")
        self.assertEqual(decision.lane, "provisional_analytical")
        self.assertEqual(decision.review_triggers, [])

    def test_publication_blocks_on_assurance_failure(self) -> None:
        with patch("peoples_ledger.assurance.load_source_snapshots", side_effect=ValueError("bad snapshot")):
            assurance = run_assurance_gate()
        decision = decide_publication_state(assurance)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.state, "blocked")
        self.assertIn("assurance_failed:source_snapshots", decision.review_triggers)

    def test_publication_blocks_on_challenge_disagreement(self) -> None:
        assurance = run_assurance_gate()
        challenge = ChallengeReview(
            agent="test",
            model={"provider": "test", "name": "test", "version": "1.0"},
            model_disagreement=0.4,
            findings=["blocking"],
            review_triggers=["challenge:blocking"],
            blocking=True,
        )
        decision = decide_publication_state(assurance, challenge)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.state, "machine_parsed")
        self.assertEqual(decision.risk_tier, 3)
        self.assertIn("challenge:blocking", decision.review_triggers)

    def test_high_risk_requires_review(self) -> None:
        assurance = run_assurance_gate()
        assurance = type(assurance)(
            checks=assurance.checks,
            risk_tier=3,
            publication_allowed=True,
            publication_state="provisional_analysis",
            review_triggers=[],
        )
        decision = decide_publication_state(assurance)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.state, "machine_parsed")
        self.assertIn("publication_review:risk_tier_threshold", decision.review_triggers)


if __name__ == "__main__":
    unittest.main()
