from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.analysis import load_analysis_unit
from peoples_ledger.assurance import run_assurance_gate
from peoples_ledger.challenge_agents import ChallengeReview, DeterministicChallengeAgent
from peoples_ledger.risk import score_risk


class RiskTests(unittest.TestCase):
    def test_risk_score_uses_dimensions_for_current_poc(self) -> None:
        unit = load_analysis_unit()
        score = score_risk(unit, run_assurance_gate(), DeterministicChallengeAgent().review(unit))
        self.assertEqual(score.tier, 2)
        self.assertEqual(score.dimensions["assurance_failures"], 1)
        self.assertEqual(score.dimensions["unknown_indicator_count"], 2)
        self.assertIn("unknown_indicator_count:2", score.rationale)

    def test_assurance_failure_increases_risk(self) -> None:
        unit = load_analysis_unit()
        with patch("peoples_ledger.assurance.load_source_snapshots", side_effect=ValueError("bad snapshot")):
            assurance = run_assurance_gate()
        score = score_risk(unit, assurance)
        self.assertEqual(score.dimensions["assurance_failures"], 2)
        self.assertEqual(score.tier, 2)

    def test_blocking_challenge_increases_risk(self) -> None:
        unit = load_analysis_unit()
        challenge = ChallengeReview(
            agent="test",
            model={"provider": "test", "name": "test", "version": "1.0"},
            model_disagreement=0.4,
            findings=["blocking"],
            review_triggers=["challenge:blocking"],
            blocking=True,
        )
        score = score_risk(unit, run_assurance_gate(), challenge)
        self.assertEqual(score.dimensions["challenge_disagreement"], 3)
        self.assertEqual(score.tier, 3)

    def test_under_representative_coverage_increases_risk(self) -> None:
        unit = load_analysis_unit()
        unit["provisions"] = unit["provisions"][:3]
        score = score_risk(unit, run_assurance_gate())
        self.assertEqual(score.dimensions["representative_coverage"], 3)
        self.assertEqual(score.tier, 3)


if __name__ == "__main__":
    unittest.main()
