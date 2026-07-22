from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from .paths import DECISION_LEDGER_PATH, SCHEMA_DIR
from .privacy import assert_no_household_financial_data
from .schema_validator import SchemaRegistry


class DecisionLedger:
    def __init__(self, path: Path = DECISION_LEDGER_PATH):
        self.path = path
        self.schema_registry = SchemaRegistry(SCHEMA_DIR)

    def append(
        self,
        *,
        analysis_unit_id: str,
        actor: str,
        action: str,
        input_refs: list[str],
        output_refs: list[str],
        rationale: str,
        decision_type: str,
        model: dict[str, Any],
        prompt_template_version: str,
        source_snapshot_ids: list[str],
        source_hashes: list[str],
        baseline_id: str,
        model_scenario_id: str,
        structured_output: dict[str, Any],
        perspective_id: str | None = None,
        structured_input_pointer: str | None = None,
        input_storage_class: str = "restricted_pointer",
        input_retention_days: int = 30,
        calibrated_confidence: float = 0.0,
        model_disagreement: float = 0.0,
        validation_results: dict[str, bool] | None = None,
        risk_tier: int = 1,
        publication_lane: str = "provisional_analytical",
        publication_state: str = "provisional_analysis",
        human_review_required: bool = False,
        review_triggers: list[str] | None = None,
        disclosure_class: str = "public_summary",
        redaction_reason: str | None = None,
        supersedes_decision_id: str | None = None,
        deletion_authorization: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if payload is not None:
            assert_no_household_financial_data(payload)

        entry_id = f"adl_{uuid4().hex}"
        entry = {
            "id": entry_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "analysis_unit_id": analysis_unit_id,
            "actor": actor,
            "decision_type": decision_type,
            "model": model,
            "prompt_template_version": prompt_template_version,
            "source_snapshot_ids": source_snapshot_ids,
            "source_hashes": source_hashes,
            "baseline_id": baseline_id,
            "model_scenario_id": model_scenario_id,
            "perspective_id": perspective_id,
            "structured_input_pointer": structured_input_pointer or f"restricted://input/{entry_id}",
            "input_storage_class": input_storage_class,
            "input_retention_days": input_retention_days,
            "structured_output": structured_output,
            "calibrated_confidence": calibrated_confidence,
            "model_disagreement": model_disagreement,
            "validation_results": validation_results
            or {
                "schema_valid": True,
                "citations_valid": True,
                "statutory_transform_valid": True,
                "calculation_valid": True,
                "privacy_egress_valid": True,
                "perspective_invariance_valid": True,
            },
            "risk_tier": risk_tier,
            "publication_lane": publication_lane,
            "publication_state": publication_state,
            "human_review_required": human_review_required,
            "review_triggers": review_triggers or [],
            "disclosure_class": disclosure_class,
            "redaction_reason": redaction_reason,
            "supersedes_decision_id": supersedes_decision_id,
            "deletion_authorization": deletion_authorization,
            "action": action,
            "input_refs": input_refs,
            "output_refs": output_refs,
            "rationale": rationale,
            "household_financial_data_present": False
        }
        self.schema_registry.validate("ai_decision_ledger_entry", entry)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, sort_keys=True) + "\n")
        return entry

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        entries = []
        with self.path.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    entry = json.loads(line)
                    self.schema_registry.validate("ai_decision_ledger_entry", entry)
                    entries.append(entry)
        return entries
