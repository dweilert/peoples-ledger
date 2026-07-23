from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.candidate_promotion_request import (
    REQUIRED_GATES,
    load_candidate_promotion_requests,
    validate_candidate_promotion_requests,
)
from peoples_ledger.paths import SCHEMA_DIR
from peoples_ledger.schema_validator import SchemaRegistry


class CandidatePromotionRequestTests(unittest.TestCase):
    def test_promotion_request_fixture_validates(self) -> None:
        requests = load_candidate_promotion_requests()

        self.assertEqual(len(requests), 1)
        request = requests[0]
        SchemaRegistry(SCHEMA_DIR).validate("candidate_promotion_request", request)
        self.assertEqual(request["request_status"], "blocked")
        self.assertEqual(set(request["required_gates"]), REQUIRED_GATES)

    def test_promotion_request_cannot_enable_execution_or_public_reporting(self) -> None:
        request = load_candidate_promotion_requests()[0]

        self.assertFalse(request["execution_policy"]["promotion_execution_allowed"])
        self.assertFalse(request["execution_policy"]["public_report_inclusion_allowed"])
        self.assertFalse(request["execution_policy"]["ledger_append_allowed"])
        self.assertFalse(request["execution_policy"]["live_provider_allowed"])
        self.assertFalse(request["execution_policy"]["household_financial_data_allowed"])

    def test_promotion_request_tracks_current_blockers(self) -> None:
        request = load_candidate_promotion_requests()[0]

        self.assertEqual(
            [blocker["gate"] for blocker in request["current_blockers"]],
            ["prompt_template", "human_review", "ledger", "promotion_disabled"],
        )

    def test_promotion_request_source_refs_match_candidate_snapshots(self) -> None:
        request = load_candidate_promotion_requests()[0]

        self.assertEqual(
            [ref["source_record_id"] for ref in request["candidate_source_refs"]],
            ["pl117_169_public_law", "jct_ira_estimated_budget_effects_2022"],
        )
        for ref in request["candidate_source_refs"]:
            self.assertTrue(ref["content_hash"].startswith("sha256:"))

    def test_modified_request_with_unknown_candidate_fails(self) -> None:
        requests = _fixture_copy()
        requests[0]["candidate_analysis_unit_id"] = "missing_candidate"

        with self.assertRaises(ValueError):
            _validate_temp_fixture(requests)

    def test_modified_request_with_missing_gate_fails(self) -> None:
        requests = _fixture_copy()
        requests[0]["required_gates"].remove("risk")

        with self.assertRaises(ValueError):
            _validate_temp_fixture(requests)

    def test_modified_request_with_enabled_execution_fails_schema(self) -> None:
        requests = _fixture_copy()
        requests[0]["execution_policy"]["promotion_execution_allowed"] = True

        with self.assertRaises(ValueError):
            _validate_temp_fixture(requests)

    def test_modified_request_with_household_data_marker_fails_privacy(self) -> None:
        requests = _fixture_copy()
        requests[0]["privacy"]["notes"] = "contains household_income"

        with self.assertRaises(ValueError):
            _validate_temp_fixture(requests)


def _fixture_copy() -> list[dict[str, object]]:
    return copy.deepcopy(load_candidate_promotion_requests())


def _validate_temp_fixture(requests: list[dict[str, object]]) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "candidate_promotion_requests.json"
        path.write_text(json.dumps(requests), encoding="utf-8")
        validate_candidate_promotion_requests(path)


if __name__ == "__main__":
    unittest.main()
