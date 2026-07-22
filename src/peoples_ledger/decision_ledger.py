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
        actor: str,
        action: str,
        input_refs: list[str],
        output_refs: list[str],
        rationale: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if payload is not None:
            assert_no_household_financial_data(payload)

        entry = {
            "id": f"adl_{uuid4().hex}",
            "timestamp": datetime.now(UTC).isoformat(),
            "actor": actor,
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
