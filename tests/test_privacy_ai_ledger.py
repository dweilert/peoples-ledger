from __future__ import annotations

import sys
import tempfile
import unittest
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.ai_adapter import AIRequest, DeterministicTCJAProvider, ProviderNeutralAIAdapter
from peoples_ledger.decision_ledger import DecisionLedger, DecisionLedgerIntegrityError
from peoples_ledger.privacy import HouseholdFinancialDataError, assert_no_household_financial_data


class PrivacyAiLedgerTests(unittest.TestCase):
    def test_privacy_guard_rejects_household_financial_keys(self) -> None:
        with self.assertRaises(HouseholdFinancialDataError):
            assert_no_household_financial_data({"household_income": 123})

    def test_deterministic_ai_adapter_returns_stable_output(self) -> None:
        adapter = ProviderNeutralAIAdapter(DeterministicTCJAProvider())
        response = adapter.complete(
            AIRequest(
                task="summarize",
                prompt="Summarize.",
                source_refs=["pl115_97_public_law"],
                prompt_template_version="plain-language-summary-poc-v1",
            )
        )
        self.assertEqual(response.provider, "deterministic-test-double")
        self.assertEqual(response.model_version, "1.0")
        self.assertIn("ten representative federal tax provisions", response.text)
        self.assertIn("does not run household-level tax calculations", response.text)

    def test_ai_adapter_rejects_private_payload_keys(self) -> None:
        adapter = ProviderNeutralAIAdapter(DeterministicTCJAProvider())
        request = AIRequest(task="summarize", prompt="x", source_refs=["ok"])
        object.__setattr__(request, "income", "bad")
        with self.assertRaises(HouseholdFinancialDataError):
            adapter.complete(request)

    def test_decision_ledger_appends_jsonl_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "ledger.jsonl"
            ledger = DecisionLedger(path)
            first = ledger.append(
                analysis_unit_id="tcja_2017_salt_cap",
                actor="test",
                action="first",
                decision_type="test_decision",
                model={"provider": "test", "name": "test-model", "version": "1.0"},
                prompt_template_version="test-template-v1",
                source_snapshot_ids=["in"],
                source_hashes=["hash"],
                baseline_id="current-law-2017-11-01",
                model_scenario_id="canonical_base_v1",
                structured_output={"result": "first"},
                input_refs=["in"],
                output_refs=["out"],
                rationale="test append",
                payload={"public": "only"},
            )
            second = ledger.append(
                analysis_unit_id="tcja_2017_salt_cap",
                actor="test",
                action="second",
                decision_type="test_decision",
                model={"provider": "test", "name": "test-model", "version": "1.0"},
                prompt_template_version="test-template-v1",
                source_snapshot_ids=["in"],
                source_hashes=["hash"],
                baseline_id="current-law-2017-11-01",
                model_scenario_id="canonical_base_v1",
                structured_output={"result": "second"},
                input_refs=["in"],
                output_refs=["out"],
                rationale="test append again",
                payload={"public": "only"},
            )
            self.assertNotEqual(first["id"], second["id"])
            self.assertIsNone(first["previous_entry_hash"])
            self.assertEqual(second["previous_entry_hash"], first["entry_hash"])
            self.assertEqual([entry["action"] for entry in ledger.read_all()], ["first", "second"])

    def test_decision_ledger_detects_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "ledger.jsonl"
            ledger = DecisionLedger(path)
            entry = ledger.append(
                analysis_unit_id="tcja_2017_representative_provisions",
                actor="test",
                action="first",
                decision_type="test_decision",
                model={"provider": "test", "name": "test-model", "version": "1.0"},
                prompt_template_version="test-template-v1",
                source_snapshot_ids=["in"],
                source_hashes=["hash"],
                baseline_id="current-law-2017-11-01",
                model_scenario_id="canonical_base_v1",
                structured_output={"result": "first"},
                input_refs=["in"],
                output_refs=["out"],
                rationale="test append",
                payload={"public": "only"},
            )
            entry["action"] = "mutated"
            path.write_text(json.dumps(entry, sort_keys=True) + "\n", encoding="utf-8")
            with self.assertRaises(DecisionLedgerIntegrityError):
                ledger.read_all()

    def test_decision_ledger_rejects_private_payload_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger = DecisionLedger(Path(tmpdir) / "ledger.jsonl")
            with self.assertRaises(HouseholdFinancialDataError):
                ledger.append(
                    analysis_unit_id="tcja_2017_salt_cap",
                    actor="test",
                    action="bad",
                    decision_type="test_decision",
                    model={"provider": "test", "name": "test-model", "version": "1.0"},
                    prompt_template_version="test-template-v1",
                    source_snapshot_ids=[],
                    source_hashes=[],
                    baseline_id="current-law-2017-11-01",
                    model_scenario_id="canonical_base_v1",
                    structured_output={"result": "bad"},
                    input_refs=[],
                    output_refs=[],
                    rationale="reject private data",
                    payload={"ssn": "000-00-0000"},
                )


if __name__ == "__main__":
    unittest.main()
