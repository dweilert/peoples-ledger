from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.ai_adapter import AIRequest, DeterministicTCJAProvider, ProviderNeutralAIAdapter
from peoples_ledger.decision_ledger import DecisionLedger
from peoples_ledger.privacy import HouseholdFinancialDataError, assert_no_household_financial_data


class PrivacyAiLedgerTests(unittest.TestCase):
    def test_privacy_guard_rejects_household_financial_keys(self) -> None:
        with self.assertRaises(HouseholdFinancialDataError):
            assert_no_household_financial_data({"household_income": 123})

    def test_deterministic_ai_adapter_returns_stable_output(self) -> None:
        adapter = ProviderNeutralAIAdapter(DeterministicTCJAProvider())
        response = adapter.complete(AIRequest(task="summarize", prompt="Summarize.", source_refs=["pl115_97_public_law"]))
        self.assertEqual(response.provider, "deterministic-test-double")
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
                actor="test",
                action="first",
                input_refs=["in"],
                output_refs=["out"],
                rationale="test append",
                payload={"public": "only"},
            )
            second = ledger.append(
                actor="test",
                action="second",
                input_refs=["in"],
                output_refs=["out"],
                rationale="test append again",
                payload={"public": "only"},
            )
            self.assertNotEqual(first["id"], second["id"])
            self.assertEqual([entry["action"] for entry in ledger.read_all()], ["first", "second"])

    def test_decision_ledger_rejects_private_payload_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger = DecisionLedger(Path(tmpdir) / "ledger.jsonl")
            with self.assertRaises(HouseholdFinancialDataError):
                ledger.append(
                    actor="test",
                    action="bad",
                    input_refs=[],
                    output_refs=[],
                    rationale="reject private data",
                    payload={"ssn": "000-00-0000"},
                )


if __name__ == "__main__":
    unittest.main()
