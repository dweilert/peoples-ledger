from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


PROMOTION_CONTRACT_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "phase-2-promotion-contract.md"
)


class Phase2PromotionContractTests(unittest.TestCase):
    def test_promotion_contract_names_required_gates(self) -> None:
        body = PROMOTION_CONTRACT_PATH.read_text(encoding="utf-8")
        for phrase in (
            "Schema Gate",
            "Source Gate",
            "Extraction And Prompt Gate",
            "Privacy Gate",
            "Human Review Gate",
            "Ledger Gate",
            "Public Report Gate",
            "Risk Gate",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_promotion_contract_preserves_phase2_non_goals(self) -> None:
        body = PROMOTION_CONTRACT_PATH.read_text(encoding="utf-8")
        for phrase in (
            "candidate promotion implementation in the current slice",
            "public report inclusion for candidate records",
            "live AI provider use",
            "broad bill ingestion",
            "live congressional monitoring",
            "full tax microsimulation",
            "state-level modeling",
            "household financial data transmission or storage",
            "final licensing/IP decisions",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_promotion_contract_documents_current_blocked_status(self) -> None:
        body = PROMOTION_CONTRACT_PATH.read_text(encoding="utf-8")
        for phrase in (
            "promotion_disabled",
            "no promotion-specific prompt template is approved",
            "human review records cannot approve promotion",
            "no promotion decision AI Decision Ledger entry exists",
            "candidate records remain excluded from public reports",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_promotion_contract_names_future_artifacts(self) -> None:
        body = PROMOTION_CONTRACT_PATH.read_text(encoding="utf-8")
        for phrase in (
            "candidate_promotion_request",
            "source promotion manifest",
            "promoted analysis-unit expected fixture",
            "promotion decision AI Decision Ledger entry fixture",
            "promotion-specific prompt-template fixture",
            "promotion regression tests",
            "candidate-to-exemplar acceptance gate",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    @unittest.skip(
        "Promotion implementation intentionally blocked until the Phase 2 "
        "promotion contract is implemented"
    )
    def test_future_candidate_promotion_requires_all_gates(self) -> None:
        self.fail("Future implementation must require schema, source, prompt, privacy, review, ledger, report, and risk gates.")

    @unittest.skip(
        "Promotion implementation intentionally blocked until the Phase 2 "
        "promotion contract is implemented"
    )
    def test_future_candidate_promotion_writes_promotion_decision_ledger_entry(self) -> None:
        self.fail("Future implementation must append a complete promotion decision AI Decision Ledger entry.")

    @unittest.skip(
        "Promotion implementation intentionally blocked until the Phase 2 "
        "promotion contract is implemented"
    )
    def test_future_promoted_candidate_can_enter_public_report_only_after_promotion(self) -> None:
        self.fail("Future implementation must exclude all candidates until promoted and validated.")


if __name__ == "__main__":
    unittest.main()
