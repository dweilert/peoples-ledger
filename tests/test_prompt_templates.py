from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.ai_adapter import AIRequest, DeterministicTCJAProvider, ProviderNeutralAIAdapter
from peoples_ledger.prompt_templates import (
    PromptTemplateRegistry,
    PromptTemplateRegistryError,
    validate_prompt_template_registry,
)


class PromptTemplateTests(unittest.TestCase):
    def test_prompt_template_registry_validates_bundled_templates(self) -> None:
        registry = validate_prompt_template_registry()
        self.assertIn("plain-language-summary-poc-v1", registry.templates)
        self.assertEqual(registry.templates["plain-language-summary-poc-v1"]["status"], "approved")

    def test_ai_adapter_accepts_approved_prompt_template(self) -> None:
        adapter = ProviderNeutralAIAdapter(DeterministicTCJAProvider())
        response = adapter.complete(
            AIRequest(
                task="summarize_analysis_unit",
                prompt="Summarize.",
                source_refs=["pl115_97_public_law"],
                prompt_template_version="plain-language-summary-poc-v1",
            )
        )
        self.assertEqual(response.provider, "deterministic-test-double")

    def test_registry_rejects_unapproved_provider_for_template(self) -> None:
        registry = PromptTemplateRegistry.load()
        with self.assertRaises(PromptTemplateRegistryError):
            registry.require_approved(
                version="plain-language-summary-poc-v1",
                provider="live-provider",
                task="summarize_analysis_unit",
                source_refs=["pl115_97_public_law"],
            )

    def test_registry_rejects_missing_required_source_refs(self) -> None:
        registry = PromptTemplateRegistry.load()
        with self.assertRaises(PromptTemplateRegistryError):
            registry.require_approved(
                version="challenge-comparison-poc-v1",
                provider="deterministic-challenge-comparison",
                task="challenge_comparison",
                source_refs=["pl115_97_public_law"],
            )

    def test_registry_rejects_duplicate_template_versions(self) -> None:
        records = list(PromptTemplateRegistry.load().templates.values())
        records.append(dict(records[0]))
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "prompt_templates.json"
            path.write_text(json.dumps(records), encoding="utf-8")
            with self.assertRaises(PromptTemplateRegistryError):
                PromptTemplateRegistry.load(path)

    def test_registry_rejects_live_provider_without_authorization(self) -> None:
        records = [dict(record) for record in PromptTemplateRegistry.load().templates.values()]
        records[0]["approved_providers"] = ["live-provider"]
        records[0]["live_provider_authorized"] = False
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "prompt_templates.json"
            path.write_text(json.dumps(records), encoding="utf-8")
            with self.assertRaises(PromptTemplateRegistryError):
                PromptTemplateRegistry.load(path)


if __name__ == "__main__":
    unittest.main()
