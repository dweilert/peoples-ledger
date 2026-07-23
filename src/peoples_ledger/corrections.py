from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .assurance import run_assurance_gate, validation_results_from_report
from .decision_ledger import DecisionLedger
from .paths import SCHEMA_DIR
from .schema_validator import SchemaRegistry
from .source_registry import SourceRegistry


DEFAULT_CORRECTION_FIXTURE_PATH = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "corrections" / "tcja_locator_correction.json"


def load_correction_record(path: Path = DEFAULT_CORRECTION_FIXTURE_PATH) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        correction = json.load(handle)
    SchemaRegistry(SCHEMA_DIR).validate("correction_record", correction)
    source_registry = SourceRegistry.load()
    for source_id in correction["source_record_ids"]:
        source_registry.require(source_id)
    return correction


def record_correction(
    correction: dict[str, Any] | None = None,
    ledger: DecisionLedger | None = None,
) -> dict[str, Any]:
    correction = correction or load_correction_record()
    source_registry = SourceRegistry.load()
    assurance = run_assurance_gate()
    ledger = ledger or DecisionLedger()

    return ledger.append(
        analysis_unit_id=correction["analysis_unit_id"],
        actor="deterministic-correction-recorder",
        action="record_correction",
        decision_type="correction",
        model={"provider": "deterministic-correction-recorder", "name": "correction-poc-v1", "version": "1.0"},
        prompt_template_version="correction-record-poc-v1",
        source_snapshot_ids=correction["source_record_ids"],
        source_hashes=[
            source_registry.require(source_id)["integrity"]["content_hash"]
            for source_id in correction["source_record_ids"]
        ],
        baseline_id="current-law-2017-11-01",
        model_scenario_id="canonical_base_v1",
        structured_output={"correction": correction},
        calibrated_confidence=1.0,
        model_disagreement=0.0,
        validation_results=validation_results_from_report(assurance),
        risk_tier=max(assurance.risk_tier, 2),
        publication_lane="provisional_analytical",
        publication_state="corrected",
        human_review_required=False,
        review_triggers=[],
        supersedes_decision_id=correction["supersedes_decision_id"],
        input_refs=correction["source_record_ids"],
        output_refs=[correction["corrected_output_ref"]],
        rationale=correction["root_cause"],
        payload=correction,
    )
