from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


PHASE2_BOUNDARY_PATH = Path(__file__).resolve().parents[1] / "docs" / "phase-2-boundary.md"


class Phase2BoundaryTests(unittest.TestCase):
    def test_phase2_boundary_defines_fixture_first_source_acquisition(self) -> None:
        body = PHASE2_BOUNDARY_PATH.read_text(encoding="utf-8")
        self.assertIn("fixture-first source acquisition manifest", body)
        self.assertIn("source-acquisition manifest schema", body)
        self.assertIn("fixture content hashes match expected hashes", body)

    def test_phase2_boundary_keeps_candidates_draft_until_promotion(self) -> None:
        body = PHASE2_BOUNDARY_PATH.read_text(encoding="utf-8")
        self.assertIn("candidate analysis units as draft-only records", body)
        self.assertIn("draft candidates cannot be reported as provisional analysis", body)
        self.assertIn("public reports still include only validated/provisional analysis records", body)

    def test_phase2_boundary_preserves_privacy_and_scope_limits(self) -> None:
        body = PHASE2_BOUNDARY_PATH.read_text(encoding="utf-8")
        for phrase in (
            "household financial data transmission or server storage",
            "broad bill ingestion",
            "live congressional monitoring",
            "full tax microsimulation",
            "state-level modeling",
            "live providers disabled",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)


if __name__ == "__main__":
    unittest.main()
