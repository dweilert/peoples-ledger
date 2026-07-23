from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .paths import CANDIDATE_EXTRACTION_POLICY_PATH, SCHEMA_DIR
from .privacy import assert_no_household_financial_data
from .schema_validator import SchemaRegistry
from .source_acquisition import acquire_source_records_from_manifest


class CandidateExtractionPolicyError(ValueError):
    """Raised when Phase 2 candidate extraction policy is unsafe or inconsistent."""


@dataclass(frozen=True)
class CandidateExtractionPolicyRegistry:
    policies: dict[str, dict[str, Any]]

    @classmethod
    def load(cls, path: Path = CANDIDATE_EXTRACTION_POLICY_PATH) -> "CandidateExtractionPolicyRegistry":
        with path.open(encoding="utf-8") as handle:
            records = json.load(handle)
        schema_registry = SchemaRegistry(SCHEMA_DIR)
        candidate_source_ids = {record["id"] for record in acquire_source_records_from_manifest()[0]}
        versions: set[str] = set()
        for record in records:
            schema_registry.validate("candidate_extraction_policy", record)
            assert_no_household_financial_data(record)
            if record["version"] in versions:
                raise CandidateExtractionPolicyError(f"duplicate candidate extraction policy version: {record['version']}")
            versions.add(record["version"])
            if not record["provider"].startswith("deterministic-"):
                raise CandidateExtractionPolicyError(f"candidate extraction provider must be deterministic: {record['version']}")
            if record["live_provider_authorized"]:
                raise CandidateExtractionPolicyError(f"live providers are not authorized for candidate extraction: {record['version']}")
            if record["promotion_use_allowed"]:
                raise CandidateExtractionPolicyError(f"candidate extraction policy cannot be used for promotion: {record['version']}")
            missing = sorted(set(record["required_candidate_source_refs"]) - candidate_source_ids)
            if missing:
                raise CandidateExtractionPolicyError(f"unknown candidate source refs for {record['version']}: {missing}")
        return cls({record["version"]: record for record in records})

    def require_dry_run(self, version: str, task: str, source_refs: list[str]) -> dict[str, Any]:
        try:
            policy = self.policies[version]
        except KeyError as exc:
            raise CandidateExtractionPolicyError(f"unknown candidate extraction policy version: {version}") from exc
        if policy["status"] != "approved_for_dry_run":
            raise CandidateExtractionPolicyError(f"candidate extraction policy is not approved for dry run: {version}")
        if task not in policy["allowed_tasks"]:
            raise CandidateExtractionPolicyError(f"task {task!r} is not allowed for {version}")
        missing = sorted(set(policy["required_candidate_source_refs"]) - set(source_refs))
        if missing:
            raise CandidateExtractionPolicyError(f"missing candidate source refs for {version}: {missing}")
        return policy


def validate_candidate_extraction_policy_registry(path: Path = CANDIDATE_EXTRACTION_POLICY_PATH) -> CandidateExtractionPolicyRegistry:
    return CandidateExtractionPolicyRegistry.load(path)
