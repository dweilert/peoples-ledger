from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLOSURE_PATH = REPO_ROOT / "docs" / "phase-3-planning-closure-checklist.md"
README_PATH = REPO_ROOT / "README.md"
HANDOFF_PATH = REPO_ROOT / "docs" / "project-handoff.md"


class Phase3PlanningClosureTests(unittest.TestCase):
    def test_closure_is_planning_only(self) -> None:
        body = CLOSURE_PATH.read_text(encoding="utf-8")

        for phrase in (
            "documentation-only Phase 3 planning pass",
            "does not approve implementation",
            "does not enable promotion",
            "Without explicit approval, continue documentation-only work only",
            "Do not implement promotion",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_closure_lists_planning_artifacts(self) -> None:
        body = CLOSURE_PATH.read_text(encoding="utf-8")

        for path in (
            "docs/phase-3-boundary.md",
            "docs/phase-3-promotion-evaluator-contract.md",
            "data/fixtures/phase3/promotion_evaluator_contract_examples.json",
            "data/fixtures/phase3/promotion_evaluator_status_contract.json",
            "schemas/phase3_promotion_evaluator_status.schema.json",
            "tests/test_phase3_promotion_evaluator_future.py",
            "docs/phase-3-implementation-entry-checklist.md",
            "docs/phase-3-evaluator-risk-review.md",
        ):
            with self.subTest(path=path):
                self.assertIn(path, body)
                self.assertTrue((REPO_ROOT / path).exists())

    def test_closure_lists_executable_planning_tests(self) -> None:
        body = CLOSURE_PATH.read_text(encoding="utf-8")

        for path in (
            "tests/test_phase3_boundary.py",
            "tests/test_phase3_promotion_evaluator_contract.py",
            "tests/test_phase3_promotion_evaluator_fixtures.py",
            "tests/test_phase3_promotion_evaluator_future.py",
            "tests/test_phase3_promotion_evaluator_status.py",
            "tests/test_backend_integration.py",
            "tests/test_browser_privacy_hardening.py",
            "tests/test_assurance.py",
            "tests/test_phase3_implementation_entry_checklist.py",
            "tests/test_phase3_evaluator_risk_review.py",
            "tests/test_project_handoff.py",
        ):
            with self.subTest(path=path):
                self.assertIn(path, body)
                self.assertTrue((REPO_ROOT / path).exists())

    def test_closure_records_validation_standard_and_skip_count(self) -> None:
        body = CLOSURE_PATH.read_text(encoding="utf-8")

        for phrase in (
            "make validate",
            "make assure",
            "make phase1-acceptance",
            "make phase2-acceptance",
            "make test",
            "make test-browser",
            "264 tests with 3 intentional future-promotion skips",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_closure_preserves_blocked_scope(self) -> None:
        body = CLOSURE_PATH.read_text(encoding="utf-8")

        for phrase in (
            "evaluator implementation",
            "candidate promotion execution",
            "candidate public-report inclusion",
            "public source registry mutation",
            "live AI provider use",
            "live AI Decision Ledger promotion append",
            "human-review approval",
            "household financial data transmission or storage",
            "broad bill ingestion",
            "live congressional monitoring",
            "full tax microsimulation",
            "state-level modeling",
            "final licensing/IP decisions",
            "motive, corruption, or loophole findings",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_readme_and_handoff_link_closure(self) -> None:
        for path in (README_PATH, HANDOFF_PATH):
            with self.subTest(path=path.name):
                self.assertIn("docs/phase-3-planning-closure-checklist.md", path.read_text(encoding="utf-8"))

    def test_evaluator_implementation_is_limited_to_approved_fixture_cases(self) -> None:
        self.assertTrue((REPO_ROOT / "src" / "peoples_ledger" / "promotion_request_evaluator.py").exists())
        self.assertFalse((REPO_ROOT / "src" / "peoples_ledger" / "candidate_promotion_evaluator.py").exists())


if __name__ == "__main__":
    unittest.main()
