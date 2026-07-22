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
    provision_ids = {provision["id"] for provision in unit["provisions"]}
    transformation_ids = {
        transformation["id"].replace("transform_", "", 1) for transformation in unit["statutory_transformations"]
    }
    missing_transformations = sorted(provision_ids - transformation_ids)
    if missing_transformations:
        raise ValueError(f"missing statutory transformations for provisions: {missing_transformations}")
    for provision in unit["provisions"]:
        referenced.update(provision["source_record_ids"])
        for source_span in provision["source_spans"]:
            referenced.add(source_span["source_record_id"])
    for transformation in unit["statutory_transformations"]:
        referenced.add(transformation["source_span"]["source_record_id"])
    for claim in unit["claims"]:
        for evidence in claim["evidence"]:
            referenced.add(evidence["source_record_id"])
    for source_id in sorted(referenced):
        source_registry.require(source_id)


def perspective_invariance_fingerprint(unit: dict[str, Any]) -> dict[str, Any]:
    return {
        "legislative_document": unit["legislative_document"],
        "provisions": unit["provisions"],
        "statutory_transformations": unit["statutory_transformations"],
        "claims": unit["claims"],
        "model_scenarios": unit["model_scenarios"],
    }


def assert_perspective_invariance(unit: dict[str, Any]) -> None:
    scenario_ids = {scenario["id"] for scenario in unit["model_scenarios"]}
    if len(unit["perspective_profiles"]) < 3:
        raise ValueError("v0.3 POC acceptance requires at least three perspective profiles")
    for profile in unit["perspective_profiles"]:
        for scenario_id in profile["permitted_model_scenarios"]:
            if scenario_id not in scenario_ids:
                raise ValueError(f"perspective {profile['id']} references unknown model scenario {scenario_id}")
        constraints = set(profile["hard_constraints"])
        required_constraints = {
            "Do not alter common evidence",
            "Do not alter statutory transformations",
            "Do not alter model-scenario parameters",
            "Do not suppress material counterevidence",
        }
        if not required_constraints.issubset(constraints):
            raise ValueError(f"perspective {profile['id']} is missing required invariance constraints")
