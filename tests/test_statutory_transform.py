from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.schema_validator import SchemaRegistry
from peoples_ledger.paths import SCHEMA_DIR
from peoples_ledger.statutory_transform import (
    AffectedAuthority,
    SourceSpan,
    TransformRequest,
    apply_transform,
    reverse_transform,
    stable_text_hash,
)


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "data" / "fixtures" / "statutory_transform" / "tcja_transform_fixtures.json"


def request_from_fixture(fixture: dict) -> TransformRequest:
    return TransformRequest(
        id=f"transform_{fixture['id']}",
        analysis_unit_id="tcja_2017_representative_provisions",
        operation=fixture["operation"],
        current_text=fixture["current_text"],
        source_span=SourceSpan(**fixture["source_span"]),
        affected_authority=[AffectedAuthority(**item) for item in fixture["affected_authority"]],
        target_text=fixture["target_text"],
        replacement_text=fixture.get("replacement_text"),
        insertion_text=fixture.get("insertion_text"),
    )


class StatutoryTransformTests(unittest.TestCase):
    def test_replace_text_fixture_applies_deterministically(self) -> None:
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))[0]
        result = apply_transform(request_from_fixture(fixture))
        self.assertEqual(result.status, "applied")
        self.assertEqual(result.after_text, fixture["expected_after_text"])
        self.assertEqual(result.transformation["operation"], "modify")
        self.assertEqual(result.transformation["before_text_hash"], stable_text_hash(fixture["current_text"]))
        self.assertEqual(result.transformation["after_text_hash"], stable_text_hash(fixture["expected_after_text"]))
        self.assertTrue(result.transformation["validation"]["round_trip_valid"])
        self.assertEqual(reverse_transform(request_from_fixture(fixture), result.after_text), fixture["expected_round_trip_text"])
        SchemaRegistry(SCHEMA_DIR).validate("statutory_transformation", result.transformation)

    def test_insert_after_fixture_applies_deterministically(self) -> None:
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))[1]
        result = apply_transform(request_from_fixture(fixture))
        self.assertEqual(result.status, "applied")
        self.assertEqual(result.after_text, fixture["expected_after_text"])
        self.assertEqual(result.transformation["operation"], "add")
        self.assertTrue(result.transformation["validation"]["deterministic"])
        self.assertEqual(reverse_transform(request_from_fixture(fixture), result.after_text), fixture["expected_round_trip_text"])
        SchemaRegistry(SCHEMA_DIR).validate("statutory_transformation", result.transformation)

    def test_delete_text_fixture_applies_deterministically(self) -> None:
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))[2]
        result = apply_transform(request_from_fixture(fixture))
        self.assertEqual(result.status, "applied")
        self.assertEqual(result.after_text, fixture["expected_after_text"])
        self.assertEqual(result.transformation["operation"], "delete")
        self.assertEqual(result.transformation["before_text_hash"], stable_text_hash(fixture["current_text"]))
        self.assertEqual(result.transformation["after_text_hash"], stable_text_hash(fixture["expected_after_text"]))
        self.assertTrue(result.transformation["validation"]["round_trip_valid"])
        self.assertEqual(reverse_transform(request_from_fixture(fixture), result.after_text), fixture["expected_round_trip_text"])
        SchemaRegistry(SCHEMA_DIR).validate("statutory_transformation", result.transformation)

    def test_renumber_text_fixture_applies_deterministically(self) -> None:
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))[3]
        result = apply_transform(request_from_fixture(fixture))
        self.assertEqual(result.status, "applied")
        self.assertEqual(result.after_text, fixture["expected_after_text"])
        self.assertEqual(result.transformation["operation"], "renumber")
        self.assertTrue(result.transformation["validation"]["deterministic"])
        self.assertTrue(result.transformation["validation"]["round_trip_valid"])
        self.assertEqual(reverse_transform(request_from_fixture(fixture), result.after_text), fixture["expected_round_trip_text"])
        SchemaRegistry(SCHEMA_DIR).validate("statutory_transformation", result.transformation)

    def test_reverse_transform_abstains_when_reverse_match_is_ambiguous(self) -> None:
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))[0]
        request = request_from_fixture(fixture)
        self.assertIsNone(reverse_transform(request, "a flat corporate rate of 21 percent and a flat corporate rate of 21 percent"))

    def test_unmatched_target_abstains(self) -> None:
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))[0]
        fixture["target_text"] = "text that is not present"
        result = apply_transform(request_from_fixture(fixture))
        self.assertEqual(result.status, "abstained")
        self.assertIsNone(result.transformation)
        self.assertEqual(result.unresolved_reason, "target_text_not_found")
        self.assertIn("statutory_transform_abstained:target_text_not_found", result.review_triggers)

    def test_ambiguous_target_abstains(self) -> None:
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))[0]
        fixture["current_text"] = "rate rate"
        fixture["target_text"] = "rate"
        fixture["replacement_text"] = "amount"
        result = apply_transform(request_from_fixture(fixture))
        self.assertEqual(result.status, "abstained")
        self.assertIsNone(result.transformation)
        self.assertEqual(result.unresolved_reason, "target_text_ambiguous")
        self.assertIn("statutory_transform_abstained:target_text_ambiguous", result.review_triggers)

    def test_missing_operation_payload_abstains(self) -> None:
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))[0]
        del fixture["replacement_text"]
        result = apply_transform(request_from_fixture(fixture))
        self.assertEqual(result.status, "abstained")
        self.assertEqual(result.unresolved_reason, "replacement_text_required")

    def test_delete_text_ambiguous_target_abstains(self) -> None:
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))[2]
        fixture["current_text"] = "delete this and delete this"
        fixture["target_text"] = "delete this"
        result = apply_transform(request_from_fixture(fixture))
        self.assertEqual(result.status, "abstained")
        self.assertEqual(result.unresolved_reason, "target_text_ambiguous")


if __name__ == "__main__":
    unittest.main()
