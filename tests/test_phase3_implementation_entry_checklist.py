from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKLIST_PATH = REPO_ROOT / "docs" / "phase-3-implementation-entry-checklist.md"
README_PATH = REPO_ROOT / "README.md"
HANDOFF_PATH = REPO_ROOT / "docs" / "project-handoff.md"


class Phase3ImplementationEntryChecklistTests(unittest.TestCase):
    def test_checklist_is_documentation_only_and_blocks_implementation(self) -> None:
        body = CHECKLIST_PATH.read_text(encoding="utf-8")

        for phrase in (
            "documentation and test scope only",
            "does not approve implementation",
            "promotion execution is blocked",
            "project-owner approval explicitly names evaluator implementation",
            "implementation starts by unskipping or adding one focused failing test",
            "keeps `promotion_disabled` as a hard stop",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_checklist_names_required_preimplementation_artifacts(self) -> None:
        body = CHECKLIST_PATH.read_text(encoding="utf-8")

        for phrase in (
            "docs/phase-3-boundary.md",
            "docs/phase-3-promotion-evaluator-contract.md",
            "data/fixtures/phase3/promotion_evaluator_contract_examples.json",
            "tests/test_phase3_promotion_evaluator_contract.py",
            "tests/test_phase3_promotion_evaluator_fixtures.py",
            "tests/test_phase3_promotion_evaluator_future.py",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)
                self.assertTrue((REPO_ROOT / phrase).exists())

    def test_first_implementation_slice_remains_read_only_and_fixture_only(self) -> None:
        body = CHECKLIST_PATH.read_text(encoding="utf-8")

        for phrase in (
            "read-only and fixture-only",
            "return deterministic blocked result shapes",
            "evaluate only local fixtures",
            "keep mutation flags false",
            "keep live provider flags false",
            "keep public report change flags false",
            "keep ledger append flags false",
            "keep `promotion_disabled` active",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_checklist_preserves_out_of_scope_boundaries(self) -> None:
        body = CHECKLIST_PATH.read_text(encoding="utf-8")

        for phrase in (
            "promote a candidate",
            "create a promoted analysis unit",
            "append to the live AI Decision Ledger",
            "update public JSON, HTML, export, or downloadable report bundles",
            "update the public source registry",
            "approve human review",
            "approve a promotion prompt template for live use",
            "call a live AI provider",
            "transmit or store household financial data",
            "infer motive, corruption, or loophole findings",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_checklist_defines_test_first_sequence(self) -> None:
        body = CHECKLIST_PATH.read_text(encoding="utf-8")
        expected_sequence = [
            "1. unskip or add the schema-first failing test",
            "2. implement the smallest read-only code needed for that test",
            "3. run the focused future evaluator test",
            "4. run fixture, contract, boundary, and handoff tests",
            "5. run `make validate`",
            "6. run `make assure`",
            "7. run `make phase1-acceptance`",
            "8. run `make phase2-acceptance`",
            "9. run `make test`",
            "10. run `make test-browser`",
            "11. open a pull request",
            "12. wait for checks",
            "13. merge only after checks pass",
        ]

        positions = [body.index(item) for item in expected_sequence]
        self.assertEqual(positions, sorted(positions))

    def test_checklist_preserves_privacy_entry_bar(self) -> None:
        body = CHECKLIST_PATH.read_text(encoding="utf-8")

        for phrase in (
            "household-specific amounts, filing facts, tax facts, and financial profile values remain absent",
            "synthetic markers may be boolean or descriptive only",
            "privacy failures return before human review, ledger, public report, risk, or disabled gates",
            "no evaluator output may contain a household value",
            "no evaluator path may store browser-local or API-submitted household values",
            "no evaluator path may transmit candidate or household payloads to a live provider",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_readme_and_handoff_link_checklist(self) -> None:
        for path in (README_PATH, HANDOFF_PATH):
            with self.subTest(path=path.name):
                self.assertIn(
                    "docs/phase-3-implementation-entry-checklist.md",
                    path.read_text(encoding="utf-8"),
                )

    def test_evaluator_implementation_is_limited_to_approved_fixture_cases(self) -> None:
        self.assertTrue((REPO_ROOT / "src" / "peoples_ledger" / "promotion_request_evaluator.py").exists())
        self.assertFalse((REPO_ROOT / "src" / "peoples_ledger" / "candidate_promotion_evaluator.py").exists())


if __name__ == "__main__":
    unittest.main()
