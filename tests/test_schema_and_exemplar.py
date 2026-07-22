from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.analysis import assert_perspective_invariance, load_analysis_unit, perspective_invariance_fingerprint
from peoples_ledger.paths import SCHEMA_DIR, SOURCE_REGISTRY_PATH, TCJA_ANALYSIS_UNIT_PATH
from peoples_ledger.schema_validator import SchemaRegistry
from peoples_ledger.source_registry import SourceRegistry


class SchemaAndExemplarTests(unittest.TestCase):
    def test_all_schema_files_are_valid_json(self) -> None:
        for path in SCHEMA_DIR.glob("*.schema.json"):
            with self.subTest(path=path.name):
                with path.open(encoding="utf-8") as handle:
                    self.assertEqual(json.load(handle)["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_source_registry_records_validate(self) -> None:
        registry = SourceRegistry.load()
        self.assertIn("pl115_97_public_law", registry.records)

    def test_tcja_analysis_unit_validates_and_links_sources(self) -> None:
        unit = load_analysis_unit()
        self.assertEqual(unit["id"], "tcja_2017_representative_provisions")
        self.assertGreaterEqual(len(unit["provisions"]), 8)
        self.assertLessEqual(len(unit["provisions"]), 12)
        self.assertEqual(len(unit["provisions"]), len(unit["statutory_transformations"]))
        self.assertFalse(unit["model_scenarios"][0]["uses_household_financial_data"])
        self.assertEqual(unit["statutory_transformations"][0]["validation"]["deterministic"], True)

    def test_validator_rejects_missing_required_field(self) -> None:
        with SOURCE_REGISTRY_PATH.open(encoding="utf-8") as handle:
            record = json.load(handle)[0]
        del record["publisher"]
        with self.assertRaises(ValueError):
            SchemaRegistry(SCHEMA_DIR).validate("source_record", record)

    def test_exemplar_expected_summary_is_stable(self) -> None:
        with TCJA_ANALYSIS_UNIT_PATH.open(encoding="utf-8") as handle:
            unit = json.load(handle)
        self.assertEqual(
            unit["expected_outputs"]["plain_language_summary"],
            "Public Law 115-97 made many federal tax changes. This Phase 0 POC records ten "
            "representative TCJA provisions, evidence, statutory-transformation snapshots, uncertainty, "
            "and qualitative distribution questions without household-level tax modeling.",
        )

    def test_perspective_profiles_preserve_invariant_evidence_layer(self) -> None:
        unit = load_analysis_unit()
        before = perspective_invariance_fingerprint(unit)
        assert_perspective_invariance(unit)
        after = perspective_invariance_fingerprint(unit)
        self.assertEqual(before, after)
        self.assertEqual(len(unit["perspective_profiles"]), 3)

    def test_manual_decision_ledger_entry_validates_against_v03_fields(self) -> None:
        ledger_path = Path(__file__).resolve().parents[1] / "data" / "ledger" / "ai_decision_ledger.jsonl"
        registry = SchemaRegistry(SCHEMA_DIR)
        with ledger_path.open(encoding="utf-8") as handle:
            entries = [json.loads(line) for line in handle if line.strip()]
        self.assertEqual(entries[0]["analysis_unit_id"], "tcja_2017_representative_provisions")
        self.assertEqual(entries[0]["model_scenario_id"], "canonical_base_v1")
        self.assertEqual(entries[0]["structured_output"]["provision_count"], 10)
        self.assertEqual(entries[0]["disclosure_class"], "public_summary")
        self.assertIsNone(entries[0]["redaction_reason"])
        self.assertIsNone(entries[0]["supersedes_decision_id"])
        registry.validate("ai_decision_ledger_entry", entries[0])


if __name__ == "__main__":
    unittest.main()
