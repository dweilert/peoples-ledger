from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HANDOFF_PATH = REPO_ROOT / "docs" / "project-handoff.md"
README_PATH = REPO_ROOT / "README.md"


class ProjectHandoffTests(unittest.TestCase):
    def test_handoff_records_current_phase2_status(self) -> None:
        body = HANDOFF_PATH.read_text(encoding="utf-8")

        for phrase in (
            "Phase 2 is complete for the bounded POC",
            "137f6a2 Add Phase 2 closure checklist (#16)",
            "Ran 197 tests",
            "10 skipped tests",
            "10 intentionally skipped future-promotion contract tests",
            "Phase 3 implementation has started",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_handoff_includes_resumable_prompt_and_boundaries(self) -> None:
        body = HANDOFF_PATH.read_text(encoding="utf-8")

        self.assertIn("```text", body)
        for phrase in (
            "Continue work on The People's Ledger repository",
            "Do not implement promotion",
            "docs/phase-3-boundary.md",
            "candidate promotion execution",
            "household financial data transmission or storage",
            "Keep going autonomously unless user input is genuinely required",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_handoff_explains_pull_request_workflow(self) -> None:
        body = HANDOFF_PATH.read_text(encoding="utf-8")

        for phrase in (
            "Why Use Pull Requests Instead Of Direct Commits To Main",
            "GitHub Actions runs on the proposed change",
            "`main` stays stable as the known-good branch",
            "traceability",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_readme_links_handoff(self) -> None:
        self.assertIn("docs/project-handoff.md", README_PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
