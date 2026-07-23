from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.reporting import build_public_report


class ReportingTests(unittest.TestCase):
    def test_public_report_preserves_traceability(self) -> None:
        report = build_public_report()
        self.assertEqual(report["analysis_unit_id"], "tcja_2017_representative_provisions")
        self.assertEqual(report["publication"]["state"], "provisional_analysis")
        self.assertTrue(report["publication"]["allowed"])
        self.assertEqual(report["risk"]["tier"], 2)
        self.assertIn("unknown_indicator_count", report["risk"]["dimensions"])
        self.assertEqual(len(report["provisions"]), 10)
        self.assertEqual(len(report["perspective_profiles"]), 3)
        for provision in report["provisions"]:
            with self.subTest(provision=provision["id"]):
                self.assertGreater(len(provision["source_spans"]), 0)
                self.assertGreater(len(provision["decision_ids"]), 0)
                self.assertEqual(provision["baseline_id"], "current-law-2017-11-01")

    def test_public_report_links_sources_snapshots_and_decisions(self) -> None:
        report = build_public_report()
        source_ids = {source["id"] for source in report["source_manifest"]}
        decision_ids = {decision["id"] for decision in report["decision_trace"]}
        self.assertEqual(
            source_ids,
            {"pl115_97_public_law", "jct_tcja_distribution_2017", "crs_salt_cap_2018"},
        )
        for source in report["source_manifest"]:
            self.assertTrue(source["snapshot"]["content_hash"])
            self.assertEqual(source["snapshot"]["storage"]["mode"], "metadata_only")
        for provision in report["provisions"]:
            self.assertTrue(set(provision["decision_ids"]).issubset(decision_ids))

    def test_public_report_snapshot_shape_is_stable(self) -> None:
        report = build_public_report()
        snapshot = {
            "report_id": report["report_id"],
            "analysis_unit_id": report["analysis_unit_id"],
            "publication": report["publication"],
            "risk": report["risk"],
            "provision_ids": [provision["id"] for provision in report["provisions"]],
            "claim_ids": [claim["id"] for claim in report["claims"]],
            "indicator_ids": [indicator["id"] for indicator in report["narrow_benefit_indicators"]],
            "perspective_ids": [profile["id"] for profile in report["perspective_profiles"]],
            "source_ids": [source["id"] for source in report["source_manifest"]],
        }
        self.assertEqual(
            json.dumps(snapshot, sort_keys=True),
            json.dumps(
                {
                    "analysis_unit_id": "tcja_2017_representative_provisions",
                    "claim_ids": [
                        "claim_representative_subset_scope",
                        "claim_distribution_varies",
                        "claim_sunset_interactions",
                    ],
                    "indicator_ids": [
                        "indicator_geographic_concentration",
                        "indicator_entity_form_advantage",
                        "indicator_sunset_budget_window",
                        "indicator_household_specific_exclusion",
                    ],
                    "perspective_ids": [
                        "profile_general_public",
                        "profile_policy_reviewer",
                        "profile_fiscal_restraint",
                    ],
                    "provision_ids": [
                        "tcja_individual_rate_brackets",
                        "tcja_standard_deduction_personal_exemption",
                        "tcja_child_tax_credit",
                        "tcja_salt_cap_10000",
                        "tcja_qbi_deduction",
                        "tcja_corporate_rate",
                        "tcja_bonus_depreciation",
                        "tcja_estate_tax_exemption",
                        "tcja_international_transition_tax",
                        "tcja_gilti_fdii_beats",
                    ],
                    "publication": {
                        "allowed": True,
                        "lane": "provisional_analytical",
                        "rationale": "Assurance checks passed and no blocking disagreement was found.",
                        "review_triggers": [],
                        "risk_tier": 1,
                        "state": "provisional_analysis",
                    },
                    "report_id": "report_tcja_2017_representative_provisions_phase1_poc",
                    "risk": {
                        "dimensions": {
                            "assurance_failures": 1,
                            "challenge_disagreement": 1,
                            "representative_coverage": 1,
                            "unknown_indicator_count": 2,
                        },
                        "rationale": ["unknown_indicator_count:2"],
                        "tier": 2,
                    },
                    "source_ids": [
                        "pl115_97_public_law",
                        "jct_tcja_distribution_2017",
                        "crs_salt_cap_2018",
                    ],
                },
                sort_keys=True,
            ),
        )


if __name__ == "__main__":
    unittest.main()
