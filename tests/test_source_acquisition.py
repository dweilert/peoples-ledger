from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.paths import SCHEMA_DIR
from peoples_ledger.reporting import build_public_report
from peoples_ledger.schema_validator import SchemaRegistry
from peoples_ledger.source_acquisition import (
    SourceAcquisitionError,
    acquire_source_records_from_manifest,
    load_source_acquisition_manifest,
)
from peoples_ledger.source_ingestion import SourceIngestionError, content_hash
from peoples_ledger.source_registry import SourceRegistry


class SourceAcquisitionTests(unittest.TestCase):
    def test_manifest_validates_and_preserves_candidate_policy(self) -> None:
        manifest = load_source_acquisition_manifest()
        SchemaRegistry(SCHEMA_DIR).validate("source_acquisition_manifest", manifest)

        self.assertEqual(manifest["phase"], "phase2_source_acquisition")
        self.assertEqual(manifest["candidate_publication_state"], "draft")
        self.assertEqual(manifest["report_visibility"], "excluded_until_promoted")
        self.assertEqual(manifest["retrieval_policy"]["mode"], "fixture_only")
        self.assertFalse(manifest["retrieval_policy"]["network_allowed"])
        self.assertEqual(manifest["retrieval_policy"]["storage_mode"], "metadata_only")

    def test_acquisition_manifest_produces_candidate_records_and_snapshots(self) -> None:
        records, snapshots = acquire_source_records_from_manifest()
        candidate_ids = {"pl117_169_public_law", "jct_ira_estimated_budget_effects_2022"}

        self.assertEqual({record["id"] for record in records}, candidate_ids)
        self.assertEqual({snapshot["source_record_id"] for snapshot in snapshots}, candidate_ids)
        for record in records:
            SchemaRegistry(SCHEMA_DIR).validate("source_record", record)
            self.assertTrue(record["integrity"]["content_hash"].startswith("sha256:"))
        for snapshot in snapshots:
            SchemaRegistry(SCHEMA_DIR).validate("source_snapshot", snapshot)
            self.assertEqual(snapshot["storage"]["mode"], "metadata_only")
            self.assertIsNone(snapshot["storage"]["path"])

    def test_expected_hashes_match_manifest_fixture_text(self) -> None:
        manifest = load_source_acquisition_manifest()
        for source in manifest["sources"]:
            self.assertEqual(source["expected_content_hash"], content_hash(source["raw_snapshot_text"]))

    def test_changed_manifest_text_fails_hash_check(self) -> None:
        manifest = load_source_acquisition_manifest()
        manifest["sources"][0] = dict(manifest["sources"][0])
        manifest["sources"][0]["raw_snapshot_text"] += " changed"

        with self.assertRaises(SourceIngestionError):
            acquire_source_records_from_manifest(_write_manifest(manifest))

    def test_missing_source_identity_fails_schema_validation(self) -> None:
        manifest = load_source_acquisition_manifest()
        manifest["sources"][0] = dict(manifest["sources"][0])
        del manifest["sources"][0]["publisher"]

        with self.assertRaises(ValueError):
            load_source_acquisition_manifest(_write_manifest(manifest))

    def test_live_retrieval_policy_is_rejected_until_approved(self) -> None:
        manifest = load_source_acquisition_manifest()
        manifest["retrieval_policy"] = dict(manifest["retrieval_policy"])
        manifest["retrieval_policy"]["network_allowed"] = True

        with self.assertRaises(SourceAcquisitionError):
            load_source_acquisition_manifest(_write_manifest(manifest))

    def test_candidate_publication_state_cannot_advance_in_acquisition_manifest(self) -> None:
        manifest = load_source_acquisition_manifest()
        manifest["candidate_publication_state"] = "machine_parsed"

        with self.assertRaises(SourceAcquisitionError):
            load_source_acquisition_manifest(_write_manifest(manifest))

    def test_candidate_sources_are_not_in_registry_or_public_report(self) -> None:
        records, _snapshots = acquire_source_records_from_manifest()
        candidate_ids = {record["id"] for record in records}

        self.assertFalse(candidate_ids & set(SourceRegistry.load().records))
        report_source_ids = {source["id"] for source in build_public_report()["source_manifest"]}
        self.assertFalse(candidate_ids & report_source_ids)


def _write_manifest(manifest: dict[str, object]) -> Path:
    tempdir = tempfile.TemporaryDirectory()
    path = Path(tempdir.name) / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    _TEMP_DIRS.append(tempdir)
    return path


_TEMP_DIRS: list[tempfile.TemporaryDirectory[str]] = []


if __name__ == "__main__":
    unittest.main()
