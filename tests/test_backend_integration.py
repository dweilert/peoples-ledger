from __future__ import annotations

import json
import sys
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.backend.server import Handler


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


if __name__ == "__main__":
    unittest.main()
