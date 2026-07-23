from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.candidate_promotion_audit import (
    CandidatePromotionAuditError,
    build_candidate_promotion_audit_cross_check,
    validate_candidate_promotion_audit_cross_check,
)


class CandidatePromotionAuditTests(unittest.TestCase):
    def test_promotion_audit_cross_check_passes_for_current_poc(self) -> None:
        cross_check = build_candidate_promotion_audit_cross_check()

        self.assertEqual(cross_check["id"], "phase2_promotion_audit_cross_check_v1")
        self.assertTrue(cross_check["candidate_ids_match"])
        self.assertFalse(cross_check["public_report_includes_candidates"])
        self.assertEqual(cross_check["source_promotion_state"], "blocked")
        self.assertFalse(cross_check["source_registry_update_allowed"])

    def test_promotion_audit_candidate_summary_keeps_candidate_blocked(self) -> None:
        summary = build_candidate_promotion_audit_cross_check()["candidate_summaries"][0]

        self.assertEqual(summary["candidate_analysis_unit_id"], "candidate_ira_2022_energy_tax_provisions")
        self.assertEqual(summary["publication_state"], "draft")
        self.assertFalse(summary["promotable"])
        self.assertFalse(summary["status_surface_promotable"])
        self.assertEqual(summary["review_recommendation"], "blocked")
        self.assertEqual(summary["promotion_request_status"], "blocked")
        self.assertEqual(summary["promotion_decision"], "blocked")
        self.assertTrue(summary["blockers_match"])
        self.assertTrue(summary["source_refs_match"])
        self.assertFalse(summary["decision_stub_in_live_ledger"])
        self.assertFalse(summary["public_report_includes_candidate"])

    def test_promotion_audit_validation_passes(self) -> None:
        validate_candidate_promotion_audit_cross_check()

    def test_promotion_audit_fails_on_decision_blocker_mismatch(self) -> None:
        entries = _decision_stubs()
        entries[0]["structured_output"]["blocker_gates"] = ["promotion_disabled"]

        with patch(
            "peoples_ledger.candidate_promotion_audit.load_candidate_promotion_decision_ledger_stubs",
            return_value=entries,
        ):
            with self.assertRaises(CandidatePromotionAuditError):
                build_candidate_promotion_audit_cross_check()

    def test_promotion_audit_fails_on_public_report_leakage(self) -> None:
        with patch(
            "peoples_ledger.candidate_promotion_audit._public_report_analysis_unit_id",
            return_value="candidate_ira_2022_energy_tax_provisions",
        ):
            with self.assertRaises(CandidatePromotionAuditError):
                build_candidate_promotion_audit_cross_check()


def _decision_stubs() -> list[dict[str, object]]:
    from peoples_ledger.candidate_promotion_decision import load_candidate_promotion_decision_ledger_stubs

    return copy.deepcopy(load_candidate_promotion_decision_ledger_stubs())


if __name__ == "__main__":
    unittest.main()
