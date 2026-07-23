from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from peoples_ledger.ai_adapter import AIRequest, DeterministicTCJAProvider, ProviderNeutralAIAdapter
from peoples_ledger.analysis import load_analysis_unit
from peoples_ledger.candidate_promotion_audit import build_candidate_promotion_audit_cross_check
from peoples_ledger.candidate_status import build_candidate_status
from peoples_ledger.decision_ledger import DecisionLedger
from peoples_ledger.reporting import build_public_report, build_public_report_html
from peoples_ledger.source_registry import SourceRegistry


class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._send_common_headers(0)
        self.end_headers()

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json({"status": "ok"})
        elif self.path == "/sources":
            self._json({"sources": SourceRegistry.load().all()})
        elif self.path in {"/analysis-units/tcja-2017-salt-cap", "/analysis-units/tcja-2017-representative-provisions"}:
            self._json(load_analysis_unit())
        elif self.path == "/ai-decision-ledger":
            self._json({"entries": DecisionLedger().read_all()})
        elif self.path == "/candidates/status":
            self._json(build_candidate_status())
        elif self.path == "/candidates/promotion-audit":
            self._json(build_candidate_promotion_audit_cross_check())
        elif self.path == "/reports/tcja-2017-representative-provisions":
            self._json(build_public_report())
        elif self.path == "/reports/tcja-2017-representative-provisions.html":
            self._html(build_public_report_html())
        else:
            self._json({"error": "not found"}, status=404)

    def do_POST(self) -> None:
        if self.path not in {
            "/analysis-units/tcja-2017-salt-cap/summarize",
            "/analysis-units/tcja-2017-representative-provisions/summarize",
        }:
            self._json({"error": "not found"}, status=404)
            return
        unit = load_analysis_unit()
        response = ProviderNeutralAIAdapter(DeterministicTCJAProvider()).complete(
            AIRequest(
                task="summarize_analysis_unit",
                prompt=unit["expected_outputs"]["plain_language_summary"],
                source_refs=unit["legislative_document"]["source_record_ids"],
                prompt_template_version="plain-language-summary-poc-v1",
            )
        )
        ledger_entry = DecisionLedger().append(
            analysis_unit_id=unit["id"],
            actor=response.provider,
            action="summarize_analysis_unit",
            decision_type="plain_language_summary",
            model={"provider": response.provider, "name": response.model, "version": response.model_version},
            prompt_template_version="plain-language-summary-poc-v1",
            source_snapshot_ids=response.source_refs,
            source_hashes=[SourceRegistry.load().require(source_id)["integrity"]["content_hash"] for source_id in response.source_refs],
            baseline_id=unit["model_scenarios"][0]["baseline_id"],
            model_scenario_id=unit["model_scenarios"][0]["id"],
            structured_output={"summary": response.text},
            calibrated_confidence=0.82,
            model_disagreement=0.0,
            input_refs=response.source_refs,
            output_refs=[unit["id"]],
            rationale="API-triggered deterministic TCJA summary.",
            payload=response.__dict__,
        )
        self._json({"summary": response.__dict__, "ledger_entry": ledger_entry})

    def _json(self, payload: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self._send_common_headers(len(body))
        self.end_headers()
        self.wfile.write(body)

    def _send_common_headers(self, content_length: int) -> None:
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(content_length))
        self.send_header("access-control-allow-origin", "*")
        self.send_header("access-control-allow-methods", "GET, POST, OPTIONS")
        self.send_header("access-control-allow-headers", "content-type")

    def _html(self, body_text: str, status: int = 200) -> None:
        body = body_text.encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "text/html; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.send_header("access-control-allow-origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        return


def main() -> int:
    server = ThreadingHTTPServer(("127.0.0.1", 8787), Handler)
    print("Serving The People's Ledger POC at http://127.0.0.1:8787")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
