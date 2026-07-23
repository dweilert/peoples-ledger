from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.paths import SCHEMA_DIR
from peoples_ledger.schema_validator import SchemaRegistry
from peoples_ledger.source_promotion import (
    REQUIRED_SOURCE_PROMOTION_GATES,
    SourcePromotionError,
    load_source_promotion_manifest,
    validate_source_promotion_manifest,
)
from peoples_ledger.source_registry import SourceRegistry


class SourcePromotionTests(unittest.TestCase):
    def test_source_promotion_manifest_validates(self) -> None:
        manifest = load_source_promotion_manifest()

        SchemaRegistry(SCHEMA_DIR).validate("source_promotion_manifest", manifest)
        self.assertEqual(manifest["promotion_state"], "blocked")
        self.assertEqual(set(manifest["required_gates"]), REQUIRED_SOURCE_PROMOTION_GATES)
        self.assertEqual(len(manifest["proposed_sources"]), 2)

    def test_source_promotion_manifest_cannot_update_public_registry(self) -> None:
        manifest = load_source_promotion_manifest()

        self.assertFalse(manifest["registry_update_allowed"])
        self.assertFalse(manifest["public_report_inclusion_allowed"])
        self.assertFalse(manifest["ledger_append_allowed"])
        self.assertTrue(all(source["registry_action"] == "proposed_noop" for source in manifest["proposed_sources"]))

    def test_source_promotion_manifest_tracks_review_and_ledger_blockers(self) -> None:
        manifest = load_source_promotion_manifest()

        for proposed in manifest["proposed_sources"]:
            with self.subTest(source=proposed["source_record"]["id"]):
                self.assertEqual(proposed["review_status"], "review_required")
                self.assertEqual(
                    {blocker["gate"] for blocker in proposed["blockers"]},
                    {"human_review", "ledger", "public_registry_diff", "promotion_disabled"},
                )

    def test_source_promotion_sources_are_not_in_public_registry(self) -> None:
        manifest = load_source_promotion_manifest()
        public_ids = set(SourceRegistry.load().records)
        proposed_ids = {source["source_record"]["id"] for source in manifest["proposed_sources"]}

        self.assertFalse(public_ids & proposed_ids)

    def test_modified_manifest_with_enabled_registry_update_fails_schema(self) -> None:
        manifest = _fixture_copy()
        manifest["registry_update_allowed"] = True

        with self.assertRaises(ValueError):
            _validate_temp_fixture(manifest)

    def test_modified_manifest_with_changed_source_hash_fails(self) -> None:
        manifest = _fixture_copy()
        manifest["proposed_sources"][0]["source_record"]["integrity"]["content_hash"] = "sha256:wrong"

        with self.assertRaises(SourcePromotionError):
            _validate_temp_fixture(manifest)

    def test_modified_manifest_with_missing_blocker_fails(self) -> None:
        manifest = _fixture_copy()
        manifest["proposed_sources"][0]["blockers"] = [
            blocker
            for blocker in manifest["proposed_sources"][0]["blockers"]
            if blocker["gate"] != "promotion_disabled"
        ]

        with self.assertRaises(SourcePromotionError):
            _validate_temp_fixture(manifest)

    def test_manifest_fails_if_candidate_source_already_in_public_registry(self) -> None:
        manifest = _fixture_copy()
        leaked_record = manifest["proposed_sources"][0]["source_record"]
        registry = SourceRegistry({leaked_record["id"]: leaked_record})

        with patch("peoples_ledger.source_promotion.SourceRegistry.load", return_value=registry):
            with self.assertRaises(SourcePromotionError):
                _validate_temp_fixture(manifest)


def _fixture_copy() -> dict[str, object]:
    return copy.deepcopy(load_source_promotion_manifest())


def _validate_temp_fixture(manifest: dict[str, object]) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "source_promotion_manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        validate_source_promotion_manifest(path)


if __name__ == "__main__":
    unittest.main()
