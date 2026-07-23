from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class FrontendPrivacyTests(unittest.TestCase):
    def test_local_household_controls_are_not_named_for_form_submission(self) -> None:
        html = (REPO_ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
        local_controls = re.findall(r"<(?:input|select)[^>]*data-local-only=\"true\"[^>]*>", html)
        self.assertGreaterEqual(len(local_controls), 3)
        for control in local_controls:
            self.assertNotIn(" name=", control)

    def test_frontend_does_not_collect_financial_household_fields(self) -> None:
        combined = "\n".join(
            [
                (REPO_ROOT / "frontend" / "index.html").read_text(encoding="utf-8"),
                (REPO_ROOT / "frontend" / "app.js").read_text(encoding="utf-8"),
            ]
        ).lower()
        forbidden = ("household_income", "income", "agi", "adjusted_gross_income", "ssn", "taxpayer_id")
        for term in forbidden:
            self.assertNotIn(term, combined)

    def test_frontend_network_calls_are_allowlisted(self) -> None:
        app_js = (REPO_ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
        fetch_paths = set(re.findall(r'fetchJson\("([^"]+)"', app_js))
        self.assertEqual(
            fetch_paths,
            {
                "/analysis-units/tcja-2017-representative-provisions",
                "/sources",
                "/ai-decision-ledger",
                "/reports/tcja-2017-representative-provisions",
                "/candidates/status",
                "/analysis-units/tcja-2017-representative-provisions/summarize",
            },
        )
        self.assertEqual(app_js.count("fetch("), 1)


if __name__ == "__main__":
    unittest.main()
