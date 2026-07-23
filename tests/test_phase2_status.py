from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


PHASE2_STATUS_PATH = Path(__file__).resolve().parents[1] / "docs" / "phase-2-status.md"


class Phase2StatusTests(unittest.TestCase):
    def test_phase2_status_names_executable_checkpoint_commands(self) -> None:
        body = PHASE2_STATUS_PATH.read_text(encoding="utf-8")
        for command in (
            "make validate",
            "make assure",
            "make phase2-acceptance",
            "candidate-status",
            "make export-candidate-audit",
            "make test",
            "make test-browser",
        ):
            with self.subTest(command=command):
                self.assertIn(command, body)

    def test_phase2_status_tracks_completed_slices(self) -> None:
        body = PHASE2_STATUS_PATH.read_text(encoding="utf-8")
        for phrase in (
            "Fixture-Only Source Acquisition",
            "Draft Candidate Analysis Queue",
            "Promotion Gate Reports",
            "Candidate Extraction Governance",
            "Candidate Review Governance",
            "Candidate Status Surfaces",
            "Candidate Audit Bundle",
            "Phase 2 Acceptance Gate",
            "Candidate-To-Exemplar Promotion Contract",
            "Candidate Promotion Request Stub",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_phase2_status_preserves_blocked_boundaries(self) -> None:
        body = PHASE2_STATUS_PATH.read_text(encoding="utf-8")
        for phrase in (
            "candidate promotion to provisional analysis",
            "public report inclusion for candidates",
            "live AI provider use",
            "household financial data transmission or storage",
            "broad bill ingestion",
            "live congressional monitoring",
            "full tax microsimulation",
            "state-level modeling",
            "final licensing/IP decisions",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)


if __name__ == "__main__":
    unittest.main()
