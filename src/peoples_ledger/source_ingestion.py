from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from .paths import SCHEMA_DIR
from .schema_validator import SchemaRegistry


DEFAULT_FIXTURE_PATH = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "source_ingestion" / "tcja_manual_sources.json"


class SourceIngestionError(ValueError):
    """Raised when a source fixture cannot be ingested deterministically."""


def load_source_ingestion_fixtures(path: Path = DEFAULT_FIXTURE_PATH) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        fixtures = json.load(handle)
    schema_registry = SchemaRegistry(SCHEMA_DIR)
    for fixture in fixtures:
        schema_registry.validate("source_ingestion_fixture", fixture)
    return fixtures


def content_hash(raw_snapshot_text: str) -> str:
    body = raw_snapshot_text.encode("utf-8")
    return "sha256:" + sha256(body).hexdigest()


def ingest_source_fixture(fixture: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    actual_hash = content_hash(fixture["raw_snapshot_text"])
    if actual_hash != fixture["expected_content_hash"]:
        raise SourceIngestionError(f"fixture hash mismatch for {fixture['id']}")

    source_record = {
        "id": fixture["id"],
        "title": fixture["title"],
        "publisher": fixture["publisher"],
        "url": fixture["url"],
        "snapshot_date": fixture["snapshot_date"],
        "source_type": fixture["source_type"],
        "integrity": {
            "snapshot_method": fixture["snapshot_method"],
            "content_hash": actual_hash,
        },
    }
    source_snapshot = {
        "source_record_id": fixture["id"],
        "retrieved_at": fixture["retrieved_at"],
        "url": fixture["url"],
        "content_hash": actual_hash,
        "locator_policy": fixture["locator_policy"],
        "storage": {
            "mode": "metadata_only",
            "path": None,
        },
    }
    schema_registry = SchemaRegistry(SCHEMA_DIR)
    schema_registry.validate("source_record", source_record)
    schema_registry.validate("source_snapshot", source_snapshot)
    return source_record, source_snapshot


def ingest_source_fixtures(path: Path = DEFAULT_FIXTURE_PATH) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    snapshots: list[dict[str, Any]] = []
    for fixture in load_source_ingestion_fixtures(path):
        source_record, source_snapshot = ingest_source_fixture(fixture)
        records.append(source_record)
        snapshots.append(source_snapshot)
    return records, snapshots


def validate_source_ingestion_fixtures(path: Path = DEFAULT_FIXTURE_PATH) -> None:
    ingest_source_fixtures(path)
