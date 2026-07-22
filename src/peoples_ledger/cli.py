from __future__ import annotations

import argparse
import json

from .ai_adapter import AIRequest, DeterministicTCJAProvider, ProviderNeutralAIAdapter
from .analysis import load_analysis_unit
from .decision_ledger import DecisionLedger
from .source_registry import SourceRegistry


def main() -> int:
    parser = argparse.ArgumentParser(description="The People's Ledger POC")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("validate", help="validate bundled schemas and exemplar data")
    subcommands.add_parser("summarize-tcja", help="run deterministic TCJA exemplar summary")
    args = parser.parse_args()

    if args.command == "validate":
        SourceRegistry.load()
        unit = load_analysis_unit()
        print(json.dumps({"status": "ok", "analysis_unit": unit["id"]}, sort_keys=True))
        return 0

    if args.command == "summarize-tcja":
        unit = load_analysis_unit()
        adapter = ProviderNeutralAIAdapter(DeterministicTCJAProvider())
        response = adapter.complete(
            AIRequest(
                task="summarize_analysis_unit",
                prompt=unit["expected_outputs"]["plain_language_summary"],
                source_refs=unit["legislative_document"]["source_record_ids"],
            )
        )
        DecisionLedger().append(
            actor=response.provider,
            action="summarize_analysis_unit",
            input_refs=response.source_refs,
            output_refs=[unit["id"]],
            rationale="Deterministic POC summary for the manually curated TCJA exemplar.",
            payload=response.__dict__,
        )
        print(json.dumps(response.__dict__, sort_keys=True))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
