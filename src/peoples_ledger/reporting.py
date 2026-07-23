from __future__ import annotations

from typing import Any

from .analysis import load_analysis_unit
from .assurance import AssuranceReport, run_assurance_gate
from .decision_ledger import DecisionLedger
from .source_registry import SourceRegistry, load_source_snapshots


def build_public_report() -> dict[str, Any]:
    unit = load_analysis_unit()
    sources = SourceRegistry.load()
    snapshots = {snapshot["source_record_id"]: snapshot for snapshot in load_source_snapshots()}
    ledger_entries = DecisionLedger().read_all()
    assurance = run_assurance_gate()

    return {
        "report_id": f"report_{unit['id']}_phase1_poc",
        "analysis_unit_id": unit["id"],
        "title": unit["title"],
        "publication": _publication_block(assurance),
        "summary": unit["expected_outputs"]["plain_language_summary"],
        "known_limits": unit["expected_outputs"]["known_limits"],
        "legislative_document": unit["legislative_document"],
        "model_scenarios": unit["model_scenarios"],
        "provisions": [_provision_view(provision) for provision in unit["provisions"]],
        "claims": unit["claims"],
        "narrow_benefit_indicators": unit["narrow_benefit_indicators"],
        "perspective_profiles": [_perspective_view(profile) for profile in unit["perspective_profiles"]],
        "source_manifest": [_source_view(source, snapshots[source["id"]]) for source in sources.all()],
        "decision_trace": [_decision_view(entry) for entry in ledger_entries],
        "assurance": {
            "checks": [check.__dict__ for check in assurance.checks],
            "review_triggers": assurance.review_triggers,
        },
    }


def _publication_block(assurance: AssuranceReport) -> dict[str, Any]:
    return {
        "lane": "provisional_analytical",
        "state": assurance.publication_state,
        "allowed": assurance.publication_allowed,
        "risk_tier": assurance.risk_tier,
    }


def _provision_view(provision: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": provision["id"],
        "label": provision["label"],
        "summary": provision["summary"],
        "policy_area": provision["policy_area"],
        "baseline_id": provision["baseline_id"],
        "effective_window": provision.get("effective_window"),
        "publication_state": provision["publication_state"],
        "source_spans": provision["source_spans"],
        "decision_ids": provision["decision_ids"],
    }


def _perspective_view(profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": profile["id"],
        "label": profile["label"],
        "version": profile["version"],
        "author": profile["author"],
        "priorities": profile["priorities"],
        "questions": profile["questions"],
        "permitted_model_scenarios": profile["permitted_model_scenarios"],
        "limitations": profile["limitations"],
    }


def _source_view(source: dict[str, Any], snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": source["id"],
        "title": source["title"],
        "publisher": source["publisher"],
        "url": source["url"],
        "source_type": source["source_type"],
        "snapshot": {
            "retrieved_at": snapshot["retrieved_at"],
            "content_hash": snapshot["content_hash"],
            "locator_policy": snapshot["locator_policy"],
            "storage": snapshot["storage"],
        },
    }


def _decision_view(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": entry["id"],
        "decision_type": entry["decision_type"],
        "model": entry["model"],
        "model_scenario_id": entry["model_scenario_id"],
        "source_snapshot_ids": entry["source_snapshot_ids"],
        "validation_results": entry["validation_results"],
        "risk_tier": entry["risk_tier"],
        "publication_lane": entry["publication_lane"],
        "publication_state": entry["publication_state"],
        "disclosure_class": entry["disclosure_class"],
        "entry_hash": entry["entry_hash"],
        "previous_entry_hash": entry["previous_entry_hash"],
    }
