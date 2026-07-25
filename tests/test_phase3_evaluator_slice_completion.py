from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKLIST_PATH = REPO_ROOT / "docs" / "phase-3-evaluator-slice-completion-checklist.md"
README_PATH = REPO_ROOT / "README.md"
HANDOFF_PATH = REPO_ROOT / "docs" / "project-handoff.md"


class Phase3EvaluatorSliceCompletionTests(unittest.TestCase):
    def test_completion_checklist_records_implemented_but_disabled_state(self) -> None:
        body = CHECKLIST_PATH.read_text(encoding="utf-8")

        for phrase in (
            "implemented but disabled",
            "read-only, fixture-only evaluator status path",
            "does not approve candidate promotion execution",
            "promotion-evaluator-status",
            "/candidates/promotion-evaluator",
            "Phase 3 evaluator status panel",
            "phase3_promotion_evaluator_status_contract",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_completion_checklist_preserves_no_mutation_invariants(self) -> None:
        body = CHECKLIST_PATH.read_text(encoding="utf-8")

        for phrase in (
            "evaluator status remains `blocked`",
            "`promotion_disabled` remains in first-failing gates",
            "promotion execution remains false",
            "live provider calls remain false",
            "live AI Decision Ledger appends remain false",
            "public report changes remain false",
            "household financial data storage remains false",
            "public source registry mutation remains blocked",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_completion_checklist_records_validation_standard(self) -> None:
        body = CHECKLIST_PATH.read_text(encoding="utf-8")

        for phrase in (
            "make validate",
            "make assure",
            "make phase1-acceptance",
            "make phase2-acceptance",
            "make test",
            "make test-browser",
            "269 tests with 3 intentional future-promotion skips",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_completion_checklist_preserves_out_of_scope_boundaries(self) -> None:
        body = CHECKLIST_PATH.read_text(encoding="utf-8")

        for phrase in (
            "candidate promotion execution",
            "promoted analysis-unit creation",
            "public candidate reporting",
            "live AI provider use",
            "live AI Decision Ledger promotion append",
            "public source registry mutation",
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

    def test_readme_and_handoff_link_completion_checklist(self) -> None:
        for path in (README_PATH, HANDOFF_PATH):
            with self.subTest(path=path.name):
                self.assertIn(
                    "docs/phase-3-evaluator-slice-completion-checklist.md",
                    path.read_text(encoding="utf-8"),
                )


if __name__ == "__main__":
    unittest.main()
