from __future__ import annotations

import argparse
import json
from pathlib import Path

from .ai_adapter import AIRequest, DeterministicTCJAProvider, ProviderNeutralAIAdapter
from .analysis import load_analysis_unit
from .candidate_extraction import validate_candidate_extraction_stub
from .candidate_promotion import validate_candidate_promotion_gate_reports
from .candidate_queue import validate_candidate_analysis_queue
from .candidate_queue import load_candidate_analysis_queue
from .decision_ledger import DecisionLedger
from .source_registry import SourceRegistry
from .source_registry import load_source_snapshots
from .source_acquisition import validate_source_acquisition_manifest
from .source_ingestion import validate_source_ingestion_fixtures
from .assurance import run_assurance_gate
from .reporting import build_public_report, build_public_report_html
from .report_artifacts import export_report_artifacts
from .challenge_agents import record_challenge_comparison, record_challenge_review
from .corrections import record_correction
from .phase1_acceptance import run_phase1_acceptance


def main() -> int:
    parser = argparse.ArgumentParser(description="The People's Ledger POC")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("validate", help="validate bundled schemas and exemplar data")
    subcommands.add_parser("assure", help="run the publication assurance gate")
    subcommands.add_parser("phase1-acceptance", help="run executable Phase 1 acceptance checks")
    subcommands.add_parser("report", help="build the public POC report JSON")
    subcommands.add_parser("report-html", help="build the public POC report HTML")
    export_parser = subcommands.add_parser("export-report", help="write report JSON, HTML, and artifact manifest")
    export_parser.add_argument("--output-dir", default=None, help="directory for generated report artifacts")
    subcommands.add_parser("challenge-review", help="record a deterministic challenge-agent review")
    subcommands.add_parser("challenge-compare", help="record deterministic multi-agent challenge comparison")
    subcommands.add_parser("record-correction", help="record the deterministic correction fixture")
    subcommands.add_parser("summarize-tcja", help="run deterministic TCJA exemplar summary")
    args = parser.parse_args()

    if args.command == "validate":
        SourceRegistry.load()
        load_source_snapshots()
        validate_source_ingestion_fixtures()
        validate_source_acquisition_manifest()
        validate_candidate_analysis_queue()
        validate_candidate_promotion_gate_reports(load_candidate_analysis_queue())
        validate_candidate_extraction_stub(load_candidate_analysis_queue())
        unit = load_analysis_unit()
        print(json.dumps({"status": "ok", "analysis_unit": unit["id"]}, sort_keys=True))
        return 0

    if args.command == "assure":
        report = run_assurance_gate()
        print(
            json.dumps(
                {
                    "status": "ok" if report.passed else "blocked",
                    "publication_allowed": report.publication_allowed,
                    "publication_state": report.publication_state,
                    "risk_tier": report.risk_tier,
                    "review_triggers": report.review_triggers,
                    "checks": [check.__dict__ for check in report.checks],
                },
                sort_keys=True,
            )
        )
        return 0 if report.passed else 1

    if args.command == "phase1-acceptance":
        report = run_phase1_acceptance()
        print(
            json.dumps(
                {
                    "status": "ok" if report.passed else "blocked",
                    "checks": [check.__dict__ for check in report.checks],
                },
                sort_keys=True,
            )
        )
        return 0 if report.passed else 1

    if args.command == "report":
        print(json.dumps(build_public_report(), sort_keys=True))
        return 0

    if args.command == "report-html":
        print(build_public_report_html())
        return 0

    if args.command == "export-report":
        output_dir = Path(args.output_dir) if args.output_dir else None
        manifest = export_report_artifacts(output_dir) if output_dir else export_report_artifacts()
        print(json.dumps(manifest, sort_keys=True))
        return 0

    if args.command == "challenge-review":
        print(json.dumps(record_challenge_review(), sort_keys=True))
        return 0

    if args.command == "challenge-compare":
        print(json.dumps(record_challenge_comparison(), sort_keys=True))
        return 0

    if args.command == "record-correction":
        print(json.dumps(record_correction(), sort_keys=True))
        return 0

    if args.command == "summarize-tcja":
        unit = load_analysis_unit()
        adapter = ProviderNeutralAIAdapter(DeterministicTCJAProvider())
        response = adapter.complete(
            AIRequest(
                task="summarize_analysis_unit",
                prompt=unit["expected_outputs"]["plain_language_summary"],
                source_refs=unit["legislative_document"]["source_record_ids"],
                prompt_template_version="plain-language-summary-poc-v1",
            )
        )
        DecisionLedger().append(
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
            rationale="Deterministic POC summary for the manually curated TCJA exemplar.",
            payload=response.__dict__,
        )
        print(json.dumps(response.__dict__, sort_keys=True))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
