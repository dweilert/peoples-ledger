from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "docs" / "phase-3-promotion-evaluator-contract.md"
BOUNDARY_PATH = REPO_ROOT / "docs" / "phase-3-boundary.md"
README_PATH = REPO_ROOT / "README.md"
HANDOFF_PATH = REPO_ROOT / "docs" / "project-handoff.md"


class Phase3PromotionEvaluatorContractTests(unittest.TestCase):
    def test_contract_is_planning_only_and_names_future_interface(self) -> None:
        body = CONTRACT_PATH.read_text(encoding="utf-8")

        for phrase in (
            "planning artifact for Phase 3",
            "does not implement promotion",
            "does not authorize promotion",
            "peoples_ledger.promotion_request_evaluator",
            "evaluate_promotion_request",
            "schema, source, extraction-prompt, privacy, human-review, ledger, public-report, and risk fixture cases only",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_contract_documents_required_read_only_inputs(self) -> None:
        body = CONTRACT_PATH.read_text(encoding="utf-8")

        for phrase in (
            "candidate_promotion_request",
            "candidate_analysis_unit",
            "candidate_promotion_gate_report",
            "source_promotion_manifest",
            "candidate_review_record",
            "promotion_decision_ledger_stub",
            "public_report_candidate_leak_check",
            "risk_review_status",
            "Inputs must be read-only",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_contract_documents_result_and_blocker_shapes(self) -> None:
        body = CONTRACT_PATH.read_text(encoding="utf-8")

        for phrase in (
            'status: "blocked"',
            "first_failing_gate: str",
            "gate_order: list[str]",
            "mutation_performed: false",
            "ledger_appended: false",
            "public_report_changed: false",
            "live_provider_called: false",
            "household_financial_data_detected: bool",
            "gate: str",
            "code: str",
            "source_artifact: str",
            "remediation_hint: str",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_contract_gate_order_matches_phase3_boundary(self) -> None:
        contract = CONTRACT_PATH.read_text(encoding="utf-8")
        boundary = BOUNDARY_PATH.read_text(encoding="utf-8")
        expected = [
            "schema",
            "source",
            "extraction_prompt",
            "privacy",
            "human_review",
            "ledger",
            "public_report",
            "risk",
            "promotion_disabled",
        ]

        for index, gate in enumerate(expected, start=1):
            marker = f"{index}. {gate}"
            with self.subTest(marker=marker):
                self.assertIn(marker, contract)
                self.assertIn(marker, boundary)

        positions = [contract.index(f"{index}. {gate}") for index, gate in enumerate(expected, start=1)]
        self.assertEqual(positions, sorted(positions))

    def test_contract_documents_stable_blocker_codes(self) -> None:
        body = CONTRACT_PATH.read_text(encoding="utf-8")
        expected_codes = (
            "schema.invalid_request",
            "schema.missing_candidate",
            "source.manifest_missing",
            "source.snapshot_hash_mismatch",
            "source.registry_mutation_required",
            "extraction_prompt.template_unapproved",
            "extraction_prompt.live_provider_unapproved",
            "privacy.household_financial_data_detected",
            "privacy.egress_requested",
            "human_review.not_approved",
            "human_review.blocking_findings_present",
            "ledger.decision_stub_missing",
            "ledger.live_append_required",
            "public_report.candidate_leakage_detected",
            "risk.unresolved_review_trigger",
            "promotion_disabled.phase3_hard_stop",
        )

        for code in expected_codes:
            with self.subTest(code=code):
                self.assertIn(code, body)

    def test_contract_preserves_privacy_precedence_and_mutation_blocks(self) -> None:
        body = CONTRACT_PATH.read_text(encoding="utf-8")

        for phrase in (
            "must fail `privacy` before review, ledger, report, risk, or promotion-disabled gates",
            "must not redact and continue",
            "append to the live AI Decision Ledger",
            "mark a candidate as approved",
            "mark a candidate as promotable",
            "create a promoted analysis unit",
            "update source registry records",
            "update public JSON, HTML, export, or downloadable report bundles",
            "call a live AI provider",
            "transmit or store household financial data",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_required_future_fixtures_are_named(self) -> None:
        body = CONTRACT_PATH.read_text(encoding="utf-8")

        for phrase in (
            "invalid request fails `schema`",
            "source hash mismatch fails `source`",
            "unapproved prompt template fails `extraction_prompt`",
            "household data marker fails `privacy`",
            "blocking review record fails `human_review`",
            "missing decision ledger stub fails `ledger`",
            "candidate leak marker fails `public_report`",
            "unresolved risk trigger fails `risk`",
            "clean request still fails `promotion_disabled`",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_contract_is_linked_from_readme_and_handoff(self) -> None:
        for path in (README_PATH, HANDOFF_PATH):
            with self.subTest(path=path.name):
                self.assertIn(
                    "docs/phase-3-promotion-evaluator-contract.md",
                    path.read_text(encoding="utf-8"),
                )

    def test_promotion_request_evaluator_is_limited_to_approved_fixture_cases(self) -> None:
        self.assertTrue((REPO_ROOT / "src" / "peoples_ledger" / "promotion_request_evaluator.py").exists())
        forbidden_paths = (REPO_ROOT / "src" / "peoples_ledger" / "candidate_promotion_evaluator.py",)

        for path in forbidden_paths:
            with self.subTest(path=path.name):
                self.assertFalse(path.exists())

    def test_contract_blocks_forbidden_claim_language(self) -> None:
        body = CONTRACT_PATH.read_text(encoding="utf-8")

        self.assertIn("must not claim motive, corruption, or loophole findings", body)


if __name__ == "__main__":
    unittest.main()
