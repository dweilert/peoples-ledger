from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.candidate_extraction_policy import (
    CandidateExtractionPolicyError,
    CandidateExtractionPolicyRegistry,
    validate_candidate_extraction_policy_registry,
)
from peoples_ledger.paths import SCHEMA_DIR
from peoples_ledger.schema_validator import SchemaRegistry


class CandidateExtractionPolicyTests(unittest.TestCase):
    def test_candidate_extraction_policy_registry_validates(self) -> None:
        registry = validate_candidate_extraction_policy_registry()

        policy = registry.require_dry_run(
            "candidate-locator-extraction-poc-v1",
            "candidate_locator_extraction",
            ["pl117_169_public_law", "jct_ira_estimated_budget_effects_2022"],
        )
        SchemaRegistry(SCHEMA_DIR).validate("candidate_extraction_policy", policy)
        self.assertEqual(policy["status"], "approved_for_dry_run")
        self.assertEqual(policy["provider"], "deterministic-candidate-extractor")
        self.assertFalse(policy["live_provider_authorized"])
        self.assertFalse(policy["promotion_use_allowed"])

    def test_candidate_extraction_policy_rejects_live_provider_authorization(self) -> None:
        records = _policy_records()
        records[0]["live_provider_authorized"] = True

        with self.assertRaises(CandidateExtractionPolicyError):
            validate_candidate_extraction_policy_registry(_write_policies(records))

    def test_candidate_extraction_policy_rejects_non_deterministic_provider(self) -> None:
        records = _policy_records()
        records[0]["provider"] = "live-provider"

        with self.assertRaises(CandidateExtractionPolicyError):
            validate_candidate_extraction_policy_registry(_write_policies(records))

    def test_candidate_extraction_policy_rejects_promotion_use(self) -> None:
        records = _policy_records()
        records[0]["promotion_use_allowed"] = True

        with self.assertRaises(CandidateExtractionPolicyError):
            validate_candidate_extraction_policy_registry(_write_policies(records))

    def test_candidate_extraction_policy_rejects_unknown_candidate_source(self) -> None:
        records = _policy_records()
        records[0]["required_candidate_source_refs"] = ["unknown_candidate_source"]

        with self.assertRaises(CandidateExtractionPolicyError):
            validate_candidate_extraction_policy_registry(_write_policies(records))

    def test_require_dry_run_rejects_missing_source_refs(self) -> None:
        registry = CandidateExtractionPolicyRegistry.load()

        with self.assertRaises(CandidateExtractionPolicyError):
            registry.require_dry_run(
                "candidate-locator-extraction-poc-v1",
                "candidate_locator_extraction",
                ["pl117_169_public_law"],
            )

    def test_require_dry_run_rejects_unapproved_task(self) -> None:
        registry = CandidateExtractionPolicyRegistry.load()

        with self.assertRaises(CandidateExtractionPolicyError):
            registry.require_dry_run(
                "candidate-locator-extraction-poc-v1",
                "summarize_analysis_unit",
                ["pl117_169_public_law", "jct_ira_estimated_budget_effects_2022"],
            )


def _policy_records() -> list[dict[str, object]]:
    registry = CandidateExtractionPolicyRegistry.load()
    return [copy.deepcopy(policy) for policy in registry.policies.values()]


def _write_policies(records: list[dict[str, object]]) -> Path:
    tempdir = tempfile.TemporaryDirectory()
    path = Path(tempdir.name) / "candidate_extraction_policies.json"
    path.write_text(json.dumps(records), encoding="utf-8")
    _TEMP_DIRS.append(tempdir)
    return path


_TEMP_DIRS: list[tempfile.TemporaryDirectory[str]] = []


if __name__ == "__main__":
    unittest.main()
