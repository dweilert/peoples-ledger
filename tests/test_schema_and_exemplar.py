from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.analysis import load_analysis_unit
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
        self.assertEqual(unit["id"], "tcja_2017_salt_cap")
        self.assertFalse(unit["model_scenarios"][0]["uses_household_financial_data"])

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
            "Public Law 115-97 capped the federal itemized deduction for state and local taxes. "
            "This POC records the provision, evidence, uncertainty, and qualitative distribution "
            "questions without household-level tax modeling.",
        )


if __name__ == "__main__":
    unittest.main()
