from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RISK_REVIEW_PATH = REPO_ROOT / "docs" / "phase-3-evaluator-risk-review.md"
README_PATH = REPO_ROOT / "README.md"
HANDOFF_PATH = REPO_ROOT / "docs" / "project-handoff.md"


class Phase3EvaluatorRiskReviewTests(unittest.TestCase):
    def test_risk_review_is_documentation_only_and_blocked(self) -> None:
        body = RISK_REVIEW_PATH.read_text(encoding="utf-8")

        for phrase in (
            "documentation and test scope only",
            "does not approve implementation",
            "does not create evaluator code",
            "implementation_blocked",
            "blocked evaluation with approval",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_risk_review_names_primary_risks(self) -> None:
        body = RISK_REVIEW_PATH.read_text(encoding="utf-8")

        for phrase in (
            "Approval confusion",
            "Gate-order drift",
            "Privacy regression",
            "Fixture-to-production creep",
            "Live-provider leakage",
            "Human-review overclaim",
            "Ledger integrity gap",
            "Public report leakage",
            "Risk understatement",
            "Claim overreach",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_risk_review_preserves_stop_conditions(self) -> None:
        body = RISK_REVIEW_PATH.read_text(encoding="utf-8")

        for phrase in (
            "remove `promotion_disabled`",
            "mark a candidate as promotable",
            "create or store a promoted analysis unit",
            "append to the live AI Decision Ledger",
            "mutate the public source registry",
            "add candidates to public reports or exports",
            "call or configure a live AI provider",
            "store household financial data",
            "transmit household financial data",
            "approve human review",
            "approve promotion prompt templates for live use",
            "broaden bill ingestion, live monitoring, microsimulation, or state modeling",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_risk_review_defines_review_controls(self) -> None:
        body = RISK_REVIEW_PATH.read_text(encoding="utf-8")

        for phrase in (
            "explicit project-owner approval",
            "failing or unskipped test exists before code changes",
            "reads local fixtures only",
            "returns blocked result shapes only",
            "no mutation flags can become true",
            "no public report artifact includes candidates",
            "no AI Decision Ledger append occurs outside approved ledger APIs",
            "household-data markers fail privacy before later gates",
            "unskipped one gate at a time",
            "all broad-scope non-goals remain absent",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_risk_review_links_from_readme_and_handoff(self) -> None:
        for path in (README_PATH, HANDOFF_PATH):
            with self.subTest(path=path.name):
                self.assertIn("docs/phase-3-evaluator-risk-review.md", path.read_text(encoding="utf-8"))

    def test_evaluator_implementation_is_schema_first_only(self) -> None:
        self.assertTrue((REPO_ROOT / "src" / "peoples_ledger" / "promotion_request_evaluator.py").exists())
        self.assertFalse((REPO_ROOT / "src" / "peoples_ledger" / "candidate_promotion_evaluator.py").exists())


if __name__ == "__main__":
    unittest.main()
