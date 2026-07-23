from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.paths import SCHEMA_DIR
from peoples_ledger.schema_validator import SchemaRegistry
from peoples_ledger.source_ingestion import (
    DEFAULT_FIXTURE_PATH,
    SourceIngestionError,
    content_hash,
    ingest_source_fixtures,
    load_source_ingestion_fixtures,
)
from peoples_ledger.source_registry import SourceRegistry, load_source_snapshots


class SourceIngestionTests(unittest.TestCase):
    def test_fixture_ingestion_produces_valid_source_records_and_snapshots(self) -> None:
        records, snapshots = ingest_source_fixtures()
        schema_registry = SchemaRegistry(SCHEMA_DIR)
        self.assertEqual(len(records), 3)
        self.assertEqual({record["id"] for record in records}, {snapshot["source_record_id"] for snapshot in snapshots})
        for record in records:
            schema_registry.validate("source_record", record)
            self.assertTrue(record["integrity"]["content_hash"].startswith("sha256:"))
        for snapshot in snapshots:
            schema_registry.validate("source_snapshot", snapshot)
            self.assertEqual(snapshot["storage"]["mode"], "metadata_only")

    def test_expected_hashes_match_fixture_text(self) -> None:
        for fixture in load_source_ingestion_fixtures():
            with self.subTest(fixture=fixture["id"]):
                self.assertEqual(fixture["expected_content_hash"], content_hash(fixture["raw_snapshot_text"]))

    def test_fixture_ingestion_matches_checked_in_registry_and_snapshot_manifest(self) -> None:
        generated_records, generated_snapshots = ingest_source_fixtures()
        registry_records = SourceRegistry.load().records
        manifest_snapshots = {snapshot["source_record_id"]: snapshot for snapshot in load_source_snapshots()}
        for record in generated_records:
            with self.subTest(record=record["id"]):
                self.assertEqual(record, registry_records[record["id"]])
        for snapshot in generated_snapshots:
            with self.subTest(snapshot=snapshot["source_record_id"]):
                self.assertEqual(snapshot, manifest_snapshots[snapshot["source_record_id"]])

    def test_hash_mismatch_fails_ingestion(self) -> None:
        fixtures = load_source_ingestion_fixtures()
        fixtures[0] = dict(fixtures[0])
        fixtures[0]["raw_snapshot_text"] = fixtures[0]["raw_snapshot_text"] + " changed"
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "fixtures.json"
            path.write_text(json.dumps(fixtures), encoding="utf-8")
            with self.assertRaises(SourceIngestionError):
                ingest_source_fixtures(path)

    def test_fixture_schema_rejects_missing_metadata(self) -> None:
        fixtures = load_source_ingestion_fixtures()
        bad_fixture = dict(fixtures[0])
        del bad_fixture["retrieved_at"]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "fixtures.json"
            path.write_text(json.dumps([bad_fixture]), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_source_ingestion_fixtures(path)

    def test_default_fixture_path_is_under_repo_data(self) -> None:
        self.assertTrue(DEFAULT_FIXTURE_PATH.exists())
        self.assertIn("data/fixtures/source_ingestion", DEFAULT_FIXTURE_PATH.as_posix())


if __name__ == "__main__":
    unittest.main()
