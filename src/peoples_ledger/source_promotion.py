from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .paths import SCHEMA_DIR, SOURCE_PROMOTION_MANIFEST_PATH
from .privacy import assert_no_household_financial_data
from .schema_validator import SchemaRegistry
from .source_acquisition import acquire_source_records_from_manifest, load_source_acquisition_manifest
from .source_registry import SourceRegistry


REQUIRED_SOURCE_PROMOTION_GATES = {
    "source_hash",
    "locator_policy",
    "human_review",
    "ledger",
    "public_registry_diff",
    "privacy",
}


class SourcePromotionError(ValueError):
    """Raised when a source-promotion manifest weakens the blocked registry boundary."""


def load_source_promotion_manifest(path: Path = SOURCE_PROMOTION_MANIFEST_PATH) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    _validate_source_promotion_manifest(manifest)
    return manifest


def validate_source_promotion_manifest(path: Path = SOURCE_PROMOTION_MANIFEST_PATH) -> None:
    load_source_promotion_manifest(path)


def _validate_source_promotion_manifest(manifest: dict[str, Any]) -> None:
    assert_no_household_financial_data(manifest)
    schema_registry = SchemaRegistry(SCHEMA_DIR)
    schema_registry.validate("source_promotion_manifest", manifest)
    _validate_blocked_policy(manifest)
    _validate_required_gates(manifest)
    _validate_acquisition_links(manifest)
    _validate_public_registry_unchanged(manifest)


def _validate_blocked_policy(manifest: dict[str, Any]) -> None:
    if manifest["promotion_state"] != "blocked":
        raise SourcePromotionError("source promotion manifest must remain blocked")
    for field in ("registry_update_allowed", "public_report_inclusion_allowed", "ledger_append_allowed"):
        if manifest[field]:
            raise SourcePromotionError(f"source promotion manifest enables prohibited action: {field}")
    for proposed in manifest["proposed_sources"]:
        if proposed["registry_action"] != "proposed_noop":
            raise SourcePromotionError(
                f"source promotion action must remain proposed_noop: {proposed['source_record']['id']}"
            )
        if proposed["review_status"] != "review_required":
            raise SourcePromotionError(
                f"source promotion review must remain required: {proposed['source_record']['id']}"
            )
        blocker_gates = {blocker["gate"] for blocker in proposed["blockers"]}
        for gate in ("human_review", "ledger", "public_registry_diff", "promotion_disabled"):
            if gate not in blocker_gates:
                raise SourcePromotionError(
                    f"source promotion blocker missing {gate}: {proposed['source_record']['id']}"
                )


def _validate_required_gates(manifest: dict[str, Any]) -> None:
    missing = sorted(REQUIRED_SOURCE_PROMOTION_GATES - set(manifest["required_gates"]))
    if missing:
        raise SourcePromotionError(f"source promotion manifest missing required gates: {missing}")


def _validate_acquisition_links(manifest: dict[str, Any]) -> None:
    acquisition_manifest = load_source_acquisition_manifest()
    if manifest["source_acquisition_manifest_id"] != acquisition_manifest["id"]:
        raise SourcePromotionError("source promotion manifest references unknown acquisition manifest")

    records, snapshots = acquire_source_records_from_manifest()
    expected_records = {record["id"]: record for record in records}
    expected_snapshots = {snapshot["source_record_id"]: snapshot for snapshot in snapshots}
    actual_ids = {proposed["source_record"]["id"] for proposed in manifest["proposed_sources"]}
    if actual_ids != set(expected_records):
        raise SourcePromotionError("source promotion manifest does not cover acquired candidate sources")

    for proposed in manifest["proposed_sources"]:
        source_id = proposed["source_record"]["id"]
        if proposed["source_record"] != expected_records[source_id]:
            raise SourcePromotionError(f"source promotion record mismatch: {source_id}")
        if proposed["source_snapshot"] != expected_snapshots[source_id]:
            raise SourcePromotionError(f"source promotion snapshot mismatch: {source_id}")


def _validate_public_registry_unchanged(manifest: dict[str, Any]) -> None:
    public_source_ids = set(SourceRegistry.load().records)
    proposed_ids = {proposed["source_record"]["id"] for proposed in manifest["proposed_sources"]}
    leaked = sorted(public_source_ids & proposed_ids)
    if leaked:
        raise SourcePromotionError(f"candidate source already exists in public source registry: {leaked}")
