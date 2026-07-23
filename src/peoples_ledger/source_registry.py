from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .paths import SCHEMA_DIR, SOURCE_REGISTRY_PATH, SOURCE_SNAPSHOT_MANIFEST_PATH
from .schema_validator import SchemaRegistry


@dataclass(frozen=True)
class SourceRegistry:
    records: dict[str, dict[str, Any]]

    @classmethod
    def load(cls, path: Path = SOURCE_REGISTRY_PATH) -> "SourceRegistry":
        with path.open(encoding="utf-8") as handle:
            records = json.load(handle)
        schema_registry = SchemaRegistry(SCHEMA_DIR)
        for record in records:
            schema_registry.validate("source_record", record)
        return cls({record["id"]: record for record in records})

    def require(self, source_id: str) -> dict[str, Any]:
        try:
            return self.records[source_id]
        except KeyError as exc:
            raise KeyError(f"unknown source record: {source_id}") from exc

    def all(self) -> list[dict[str, Any]]:
        return list(self.records.values())


def load_source_snapshots(path: Path = SOURCE_SNAPSHOT_MANIFEST_PATH) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        snapshots = json.load(handle)
    schema_registry = SchemaRegistry(SCHEMA_DIR)
    source_registry = SourceRegistry.load()
    for snapshot in snapshots:
        schema_registry.validate("source_snapshot", snapshot)
        source_record = source_registry.require(snapshot["source_record_id"])
        if snapshot["url"] != source_record["url"]:
            raise ValueError(f"snapshot URL mismatch for {snapshot['source_record_id']}")
        if snapshot["content_hash"] != source_record["integrity"]["content_hash"]:
            raise ValueError(f"snapshot hash mismatch for {snapshot['source_record_id']}")
    return snapshots
