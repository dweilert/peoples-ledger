from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .paths import SCHEMA_DIR, TCJA_ANALYSIS_UNIT_PATH
from .privacy import assert_no_household_financial_data
from .schema_validator import SchemaRegistry
from .source_registry import SourceRegistry


def load_analysis_unit(path: Path = TCJA_ANALYSIS_UNIT_PATH) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        unit = json.load(handle)
    assert_no_household_financial_data(unit)
    SchemaRegistry(SCHEMA_DIR).validate("analysis_unit", unit)
    _validate_source_links(unit, SourceRegistry.load())
    return unit


def _validate_source_links(unit: dict[str, Any], source_registry: SourceRegistry) -> None:
    referenced = set(unit["legislative_document"]["source_record_ids"])
    for provision in unit["provisions"]:
        referenced.update(provision["source_record_ids"])
    for claim in unit["claims"]:
        for evidence in claim["evidence"]:
            referenced.add(evidence["source_record_id"])
    for source_id in sorted(referenced):
        source_registry.require(source_id)
