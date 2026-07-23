from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .paths import SCHEMA_DIR, SOURCE_ACQUISITION_MANIFEST_PATH
from .schema_validator import SchemaRegistry
from .source_ingestion import SourceIngestionError, content_hash


class SourceAcquisitionError(ValueError):
    """Raised when a Phase 2 source-acquisition manifest is not publishable as a candidate."""


def load_source_acquisition_manifest(path: Path = SOURCE_ACQUISITION_MANIFEST_PATH) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    SchemaRegistry(SCHEMA_DIR).validate("source_acquisition_manifest", manifest)
    _validate_candidate_policy(manifest)
    return manifest


def acquire_source_records_from_manifest(path: Path = SOURCE_ACQUISITION_MANIFEST_PATH) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    manifest = load_source_acquisition_manifest(path)
    records: list[dict[str, Any]] = []
    snapshots: list[dict[str, Any]] = []
    for source in manifest["sources"]:
        source_record, source_snapshot = _candidate_source_records(source, manifest)
        records.append(source_record)
        snapshots.append(source_snapshot)
    return records, snapshots


def validate_source_acquisition_manifest(path: Path = SOURCE_ACQUISITION_MANIFEST_PATH) -> None:
    acquire_source_records_from_manifest(path)


def _validate_candidate_policy(manifest: dict[str, Any]) -> None:
    if manifest["candidate_publication_state"] != "draft":
        raise SourceAcquisitionError("Phase 2 acquisition candidates must remain draft until promotion gates exist")
    if manifest["report_visibility"] != "excluded_until_promoted":
        raise SourceAcquisitionError("Phase 2 acquisition candidates must be excluded from public reports")
    policy = manifest["retrieval_policy"]
    if policy["mode"] != "fixture_only" or policy["network_allowed"]:
        raise SourceAcquisitionError("Phase 2 source acquisition must remain fixture-only until live retrieval is approved")
    if policy["storage_mode"] != "metadata_only":
        raise SourceAcquisitionError("Phase 2 source acquisition stores metadata only in this POC")


def _candidate_source_records(source: dict[str, Any], manifest: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    actual_hash = content_hash(source["raw_snapshot_text"])
    if actual_hash != source["expected_content_hash"]:
        raise SourceIngestionError(f"source acquisition hash mismatch for {source['id']}")

    source_record = {
        "id": source["id"],
        "title": source["title"],
        "publisher": source["publisher"],
        "url": source["url"],
        "snapshot_date": source["snapshot_date"],
        "source_type": source["source_type"],
        "integrity": {
            "snapshot_method": source["snapshot_method"],
            "content_hash": actual_hash,
        },
    }
    source_snapshot = {
        "source_record_id": source["id"],
        "retrieved_at": source["retrieved_at"],
        "url": source["url"],
        "content_hash": actual_hash,
        "locator_policy": source["locator_policy"],
        "storage": {
            "mode": manifest["retrieval_policy"]["storage_mode"],
            "path": None,
        },
    }
    schema_registry = SchemaRegistry(SCHEMA_DIR)
    schema_registry.validate("source_record", source_record)
    schema_registry.validate("source_snapshot", source_snapshot)
    return source_record, source_snapshot
