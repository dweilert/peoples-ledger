from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.phase2_acceptance import run_phase2_acceptance


REPO_ROOT = Path(__file__).resolve().parents[1]
PHASE3_BOUNDARY_PATH = REPO_ROOT / "docs" / "phase-3-boundary.md"


class Phase3BoundaryTests(unittest.TestCase):
    def test_phase3_boundary_is_planning_only(self) -> None:
        body = PHASE3_BOUNDARY_PATH.read_text(encoding="utf-8")

        for phrase in (
            "planning-only",
            "disabled-by-default candidate promotion request evaluator",
            "does not authorize candidate promotion",
            "never mutates candidates",
            "never appends to the live AI Decision Ledger",
            "never adds candidate content to public reports",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_phase3_boundary_documents_gate_order(self) -> None:
        body = PHASE3_BOUNDARY_PATH.read_text(encoding="utf-8")
        expected = [
            "1. schema",
            "2. source",
            "3. extraction_prompt",
            "4. privacy",
            "5. human_review",
            "6. ledger",
            "7. public_report",
            "8. risk",
            "9. promotion_disabled",
        ]

        positions = [body.index(item) for item in expected]
        self.assertEqual(positions, sorted(positions))

    def test_phase3_boundary_preserves_out_of_scope_blocks(self) -> None:
        body = PHASE3_BOUNDARY_PATH.read_text(encoding="utf-8")

        for phrase in (
            "candidate promotion execution",
            "public report inclusion for candidates",
            "live AI provider use",
            "public source registry mutation",
            "broad bill ingestion",
            "live congressional monitoring",
            "full tax microsimulation",
            "state-level modeling",
            "household financial data transmission or storage",
            "final licensing/IP decisions",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_phase3_boundary_lists_future_evaluator_tests_without_implementation(self) -> None:
        body = PHASE3_BOUNDARY_PATH.read_text(encoding="utf-8")

        for phrase in (
            "the evaluator is disabled by default",
            "gate order is deterministic",
            "fail schema first",
            "fail source before prompt or review gates",
            "fail extraction_prompt",
            "fail privacy",
            "fail human_review",
            "fail ledger",
            "fail public_report",
            "promotion_disabled remains a hard stop",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_phase3_boundary_does_not_add_implementation_modules(self) -> None:
        forbidden_paths = (
            "src/peoples_ledger/candidate_promotion_evaluator.py",
            "src/peoples_ledger/bill_ingestion.py",
            "src/peoples_ledger/live_congressional_monitoring.py",
            "src/peoples_ledger/microsimulation.py",
            "src/peoples_ledger/state_modeling.py",
        )

        for relative_path in forbidden_paths:
            with self.subTest(relative_path=relative_path):
                self.assertFalse((REPO_ROOT / relative_path).exists())

    def test_phase2_acceptance_still_passes_under_phase3_planning(self) -> None:
        self.assertTrue(run_phase2_acceptance().passed)


if __name__ == "__main__":
    unittest.main()
