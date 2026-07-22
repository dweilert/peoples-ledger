from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from peoples_ledger.ai_adapter import AIRequest, DeterministicTCJAProvider, ProviderNeutralAIAdapter
from peoples_ledger.analysis import load_analysis_unit
from peoples_ledger.decision_ledger import DecisionLedger
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
        elif self.path == "/analysis-units/tcja-2017-salt-cap":
            self._json(load_analysis_unit())
        elif self.path == "/ai-decision-ledger":
            self._json({"entries": DecisionLedger().read_all()})
        else:
            self._json({"error": "not found"}, status=404)

    def do_POST(self) -> None:
        if self.path != "/analysis-units/tcja-2017-salt-cap/summarize":
            self._json({"error": "not found"}, status=404)
            return
        unit = load_analysis_unit()
        response = ProviderNeutralAIAdapter(DeterministicTCJAProvider()).complete(
            AIRequest(
                task="summarize_analysis_unit",
                prompt=unit["expected_outputs"]["plain_language_summary"],
                source_refs=unit["legislative_document"]["source_record_ids"],
            )
        )
        ledger_entry = DecisionLedger().append(
            actor=response.provider,
            action="summarize_analysis_unit",
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

    def log_message(self, format: str, *args: Any) -> None:
        return


def main() -> int:
    server = ThreadingHTTPServer(("127.0.0.1", 8787), Handler)
    print("Serving The People's Ledger POC at http://127.0.0.1:8787")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
