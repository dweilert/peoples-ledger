from __future__ import annotations

import json
import sys
import tempfile
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.backend.server import Handler
from peoples_ledger.decision_ledger import DecisionLedger


class BackendIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.thread.join(timeout=2)
        cls.server.server_close()

    def get_json(self, path: str) -> dict:
        with urllib.request.urlopen(f"{self.base_url}{path}", timeout=3) as response:
            return json.loads(response.read().decode("utf-8"))

    def test_health_endpoint(self) -> None:
        self.assertEqual(self.get_json("/health"), {"status": "ok"})

    def test_analysis_unit_endpoint(self) -> None:
        unit = self.get_json("/analysis-units/tcja-2017-representative-provisions")
        self.assertEqual(unit["id"], "tcja_2017_representative_provisions")
        self.assertEqual(unit["status"], "manual_exemplar")

    def test_sources_endpoint(self) -> None:
        payload = self.get_json("/sources")
        self.assertGreaterEqual(len(payload["sources"]), 3)

    def test_html_report_endpoint(self) -> None:
        with urllib.request.urlopen(f"{self.base_url}/reports/tcja-2017-representative-provisions.html", timeout=3) as response:
            body = response.read().decode("utf-8")
        self.assertIn("<h1>TCJA 2017 representative federal tax provision subset</h1>", body)

    def test_summarize_endpoint_does_not_store_submitted_household_values(self) -> None:
        captured_logs: list[str] = []

        class CapturingHandler(Handler):
            def log_message(self, format: str, *args: object) -> None:
                captured_logs.append(format % args)

        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"

            def ledger_factory() -> DecisionLedger:
                return DecisionLedger(ledger_path)

            with patch("peoples_ledger.backend.server.DecisionLedger", side_effect=ledger_factory):
                server = ThreadingHTTPServer(("127.0.0.1", 0), CapturingHandler)
                base_url = f"http://127.0.0.1:{server.server_port}"
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    body = json.dumps(
                        {
                            "household_income": 123456,
                            "sentinel_local_privacy_value": "do-not-store-or-log",
                        }
                    ).encode("utf-8")
                    request = urllib.request.Request(
                        f"{base_url}/analysis-units/tcja-2017-representative-provisions/summarize",
                        data=body,
                        headers={"content-type": "application/json"},
                        method="POST",
                    )
                    with urllib.request.urlopen(request, timeout=3) as response:
                        payload = json.loads(response.read().decode("utf-8"))
                finally:
                    server.shutdown()
                    thread.join(timeout=2)
                    server.server_close()

            entries = DecisionLedger(ledger_path).read_all()

        serialized = json.dumps({"response": payload, "entries": entries, "logs": captured_logs}, sort_keys=True)
        self.assertNotIn("household_income", serialized)
        self.assertNotIn("123456", serialized)
        self.assertNotIn("sentinel_local_privacy_value", serialized)
        self.assertNotIn("do-not-store-or-log", serialized)


if __name__ == "__main__":
    unittest.main()
