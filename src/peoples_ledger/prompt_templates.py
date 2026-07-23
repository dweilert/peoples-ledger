from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .paths import PROMPT_TEMPLATE_REGISTRY_PATH, SCHEMA_DIR
from .privacy import assert_no_household_financial_data
from .schema_validator import SchemaRegistry
from .source_registry import SourceRegistry


class PromptTemplateRegistryError(ValueError):
    """Raised when prompt-template governance records are invalid."""


@dataclass(frozen=True)
class PromptTemplateRegistry:
    templates: dict[str, dict[str, Any]]

    @classmethod
    def load(cls, path: Path = PROMPT_TEMPLATE_REGISTRY_PATH) -> "PromptTemplateRegistry":
        with path.open(encoding="utf-8") as handle:
            records = json.load(handle)
        schema_registry = SchemaRegistry(SCHEMA_DIR)
        source_registry = SourceRegistry.load()
        versions: set[str] = set()
        for record in records:
            schema_registry.validate("prompt_template", record)
            assert_no_household_financial_data(record)
            if record["version"] in versions:
                raise PromptTemplateRegistryError(f"duplicate prompt template version: {record['version']}")
            versions.add(record["version"])
            for source_id in record["required_source_refs"]:
                source_registry.require(source_id)
            if record["status"] == "approved" and not record["approved_providers"]:
                raise PromptTemplateRegistryError(f"approved template has no providers: {record['version']}")
            if not record["live_provider_authorized"]:
                live_providers = [
                    provider
                    for provider in record["approved_providers"]
                    if not provider.startswith("deterministic-")
                ]
                if live_providers:
                    raise PromptTemplateRegistryError(
                        f"live providers require explicit authorization for {record['version']}: {live_providers}"
                    )
        return cls({record["version"]: record for record in records})

    def require_approved(self, version: str, provider: str, task: str, source_refs: list[str]) -> dict[str, Any]:
        try:
            template = self.templates[version]
        except KeyError as exc:
            raise PromptTemplateRegistryError(f"unknown prompt template version: {version}") from exc
        if template["status"] != "approved":
            raise PromptTemplateRegistryError(f"prompt template is not approved: {version}")
        if provider not in template["approved_providers"]:
            raise PromptTemplateRegistryError(f"provider {provider!r} is not approved for {version}")
        if task not in template["allowed_tasks"]:
            raise PromptTemplateRegistryError(f"task {task!r} is not approved for {version}")
        missing_refs = sorted(set(template["required_source_refs"]) - set(source_refs))
        if missing_refs:
            raise PromptTemplateRegistryError(f"missing required source refs for {version}: {missing_refs}")
        return template


def validate_prompt_template_registry(path: Path = PROMPT_TEMPLATE_REGISTRY_PATH) -> PromptTemplateRegistry:
    return PromptTemplateRegistry.load(path)
