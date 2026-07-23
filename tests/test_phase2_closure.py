from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.candidate_promotion_audit import build_candidate_promotion_audit_cross_check
from peoples_ledger.candidate_promotion_decision import load_candidate_promotion_decision_ledger_stubs
from peoples_ledger.candidate_promotion_request import load_candidate_promotion_requests
from peoples_ledger.candidate_queue import load_candidate_analysis_queue
from peoples_ledger.phase2_acceptance import run_phase2_acceptance
from peoples_ledger.reporting import build_public_report
from peoples_ledger.source_promotion import load_source_promotion_manifest
from peoples_ledger.source_registry import SourceRegistry


REPO_ROOT = Path(__file__).resolve().parents[1]
PHASE2_CLOSURE_PATH = REPO_ROOT / "docs" / "phase-2-closure-checklist.md"
PHASE2_STATUS_PATH = REPO_ROOT / "docs" / "phase-2-status.md"


class Phase2ClosureTests(unittest.TestCase):
    def test_phase2_closure_document_declares_bounded_completion(self) -> None:
        body = PHASE2_CLOSURE_PATH.read_text(encoding="utf-8")

        self.assertIn("Status: complete for the bounded Phase 2 POC.", body)
        for phrase in (
            "IRA 2022 federal-tax source acquisition runs from checked-in fixtures only",
            "Candidate analysis units remain `draft`",
            "Candidate analysis units remain absent from public reports",
            "Promotion decision ledger stubs remain offline fixtures",
            "Household financial data is not transmitted or stored",
            "make phase2-acceptance",
            "make test-browser",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_phase2_closure_preserves_intentional_blockers(self) -> None:
        body = PHASE2_CLOSURE_PATH.read_text(encoding="utf-8")

        for phrase in (
            "candidate promotion to provisional analysis",
            "public report inclusion for candidates",
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

    def test_phase2_closure_documents_phase3_without_starting_it(self) -> None:
        body = PHASE2_CLOSURE_PATH.read_text(encoding="utf-8")

        self.assertIn("Phase 3 Entry Criteria", body)
        self.assertIn("disabled-by-default", body)
        self.assertIn("without starting Phase 3 work", PHASE2_STATUS_PATH.read_text(encoding="utf-8"))

    def test_phase2_runtime_state_matches_closure_claims(self) -> None:
        candidates = load_candidate_analysis_queue()
        candidate_ids = {candidate["id"] for candidate in candidates}
        public_report = build_public_report()
        public_source_ids = set(SourceRegistry.load().records)
        source_manifest = load_source_promotion_manifest()
        promotion_requests = load_candidate_promotion_requests()
        promotion_decisions = load_candidate_promotion_decision_ledger_stubs()
        cross_check = build_candidate_promotion_audit_cross_check()

        self.assertTrue(run_phase2_acceptance().passed)
        self.assertEqual({candidate["publication_state"] for candidate in candidates}, {"draft"})
        self.assertNotIn(public_report["analysis_unit_id"], candidate_ids)
        self.assertFalse(
            public_source_ids & {source["source_record"]["id"] for source in source_manifest["proposed_sources"]}
        )
        self.assertEqual({request["request_status"] for request in promotion_requests}, {"blocked"})
        self.assertEqual(
            {decision["structured_output"]["promotion_decision"] for decision in promotion_decisions},
            {"blocked"},
        )
        self.assertFalse(cross_check["public_report_includes_candidates"])
        self.assertTrue(cross_check["candidate_ids_match"])


if __name__ == "__main__":
    unittest.main()
