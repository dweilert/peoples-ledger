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
from peoples_ledger.paths import SCHEMA_DIR
from peoples_ledger.promotion_request_evaluator import promotion_evaluator_status_contract_view
from peoples_ledger.schema_validator import SchemaRegistry


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

    def test_candidate_status_endpoint_is_read_only_and_draft_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"

            def ledger_factory() -> DecisionLedger:
                return DecisionLedger(ledger_path)

            with patch("peoples_ledger.backend.server.DecisionLedger", side_effect=ledger_factory):
                server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
                base_url = f"http://127.0.0.1:{server.server_port}"
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    with urllib.request.urlopen(f"{base_url}/candidates/status", timeout=3) as response:
                        payload = json.loads(response.read().decode("utf-8"))
                finally:
                    server.shutdown()
                    thread.join(timeout=2)
                    server.server_close()

            entries = DecisionLedger(ledger_path).read_all()

        self.assertEqual(entries, [])
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["candidate_count"], 1)
        self.assertFalse(payload["public_report_includes_candidates"])
        self.assertFalse(payload["ledger_appended"])
        candidate = payload["candidates"][0]
        self.assertEqual(candidate["publication_state"], "draft")
        self.assertFalse(candidate["uses_household_financial_data"])
        self.assertFalse(candidate["egress_allowed"])
        self.assertFalse(candidate["promotable"])
        self.assertIn("promotion_disabled", {blocker["gate"] for blocker in candidate["promotion_blockers"]})

    def test_promotion_audit_endpoint_is_read_only_and_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"

            def ledger_factory() -> DecisionLedger:
                return DecisionLedger(ledger_path)

            with (
                patch("peoples_ledger.backend.server.DecisionLedger", side_effect=ledger_factory),
                patch("peoples_ledger.candidate_promotion_audit.DecisionLedger", side_effect=ledger_factory),
            ):
                server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
                base_url = f"http://127.0.0.1:{server.server_port}"
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    with urllib.request.urlopen(f"{base_url}/candidates/promotion-audit", timeout=3) as response:
                        payload = json.loads(response.read().decode("utf-8"))
                finally:
                    server.shutdown()
                    thread.join(timeout=2)
                    server.server_close()

            entries = DecisionLedger(ledger_path).read_all()

        self.assertEqual(entries, [])
        self.assertTrue(payload["candidate_ids_match"])
        self.assertFalse(payload["public_report_includes_candidates"])
        self.assertEqual(payload["source_promotion_state"], "blocked")
        self.assertFalse(payload["source_registry_update_allowed"])
        summary = payload["candidate_summaries"][0]
        self.assertEqual(summary["publication_state"], "draft")
        self.assertEqual(summary["promotion_decision"], "blocked")
        self.assertTrue(summary["blockers_match"])
        self.assertTrue(summary["source_refs_match"])
        self.assertFalse(summary["decision_stub_in_live_ledger"])

    def test_promotion_evaluator_endpoint_is_read_only_and_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"

            def ledger_factory() -> DecisionLedger:
                return DecisionLedger(ledger_path)

            with patch("peoples_ledger.backend.server.DecisionLedger", side_effect=ledger_factory):
                server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
                base_url = f"http://127.0.0.1:{server.server_port}"
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    with urllib.request.urlopen(f"{base_url}/candidates/promotion-evaluator", timeout=3) as response:
                        payload = json.loads(response.read().decode("utf-8"))
                finally:
                    server.shutdown()
                    thread.join(timeout=2)
                    server.server_close()

            entries = DecisionLedger(ledger_path).read_all()

        self.assertEqual(entries, [])
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["evaluation_count"], 9)
        self.assertFalse(payload["promotion_execution_allowed"])
        self.assertFalse(payload["ledger_appended"])
        self.assertFalse(payload["public_report_changed"])
        self.assertFalse(payload["live_provider_called"])
        self.assertIn("promotion_disabled", payload["first_failing_gates"])

    def test_promotion_evaluator_endpoint_matches_status_schema(self) -> None:
        payload = self.get_json("/candidates/promotion-evaluator")
        contract_view = promotion_evaluator_status_contract_view(payload)

        SchemaRegistry(SCHEMA_DIR).validate("phase3_promotion_evaluator_status", contract_view)
        self.assertEqual(contract_view["status"], "blocked")
        self.assertFalse(contract_view["mutation_flags"]["promotion_execution_allowed"])

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
