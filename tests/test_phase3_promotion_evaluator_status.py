from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.paths import DECISION_LEDGER_PATH, SCHEMA_DIR
from peoples_ledger.promotion_request_evaluator import (
    build_promotion_evaluator_status,
    export_promotion_evaluator_status_bundle,
    promotion_evaluator_status_contract_view,
    validate_promotion_evaluator_status_contract,
)
from peoples_ledger.schema_validator import SchemaRegistry, SchemaValidationError


REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_CONTRACT_PATH = REPO_ROOT / "data" / "fixtures" / "phase3" / "promotion_evaluator_status_contract.json"


class Phase3PromotionEvaluatorStatusTests(unittest.TestCase):
    def test_evaluator_status_is_read_only_and_blocked(self) -> None:
        before = DECISION_LEDGER_PATH.read_text(encoding="utf-8") if DECISION_LEDGER_PATH.exists() else ""

        status = build_promotion_evaluator_status()

        after = DECISION_LEDGER_PATH.read_text(encoding="utf-8") if DECISION_LEDGER_PATH.exists() else ""
        self.assertEqual(after, before)
        self.assertEqual(status["status"], "blocked")
        self.assertEqual(status["evaluation_count"], 9)
        self.assertFalse(status["promotion_execution_allowed"])
        self.assertFalse(status["ledger_appended"])
        self.assertFalse(status["public_report_changed"])
        self.assertFalse(status["live_provider_called"])
        self.assertFalse(status["household_financial_data_storage_allowed"])
        self.assertIn("promotion_disabled", status["first_failing_gates"])

    def test_evaluator_status_lists_deterministic_gate_order(self) -> None:
        status = build_promotion_evaluator_status()

        self.assertEqual(
            status["first_failing_gates"],
            [
                "schema",
                "source",
                "extraction_prompt",
                "privacy",
                "human_review",
                "ledger",
                "public_report",
                "risk",
                "promotion_disabled",
            ],
        )

    def test_evaluator_status_cli_outputs_json_without_ledger_append(self) -> None:
        before = DECISION_LEDGER_PATH.read_text(encoding="utf-8") if DECISION_LEDGER_PATH.exists() else ""
        result = subprocess.run(
            [sys.executable, "-m", "peoples_ledger.cli", "promotion-evaluator-status"],
            check=True,
            capture_output=True,
            cwd=Path(__file__).resolve().parents[1],
            env={"PYTHONPATH": "src"},
            text=True,
        )
        after = DECISION_LEDGER_PATH.read_text(encoding="utf-8") if DECISION_LEDGER_PATH.exists() else ""

        payload = json.loads(result.stdout)
        self.assertEqual(after, before)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["evaluation_count"], 9)
        self.assertFalse(payload["public_report_changed"])
        self.assertFalse(payload["live_provider_called"])

    def test_evaluator_status_matches_checked_contract_snapshot(self) -> None:
        expected = json.loads(STATUS_CONTRACT_PATH.read_text(encoding="utf-8"))

        self.assertEqual(promotion_evaluator_status_contract_view(build_promotion_evaluator_status()), expected)

    def test_evaluator_status_contract_snapshot_validates_against_schema(self) -> None:
        registry = SchemaRegistry(SCHEMA_DIR)
        expected = json.loads(STATUS_CONTRACT_PATH.read_text(encoding="utf-8"))

        registry.validate("phase3_promotion_evaluator_status", expected)
        expected["mutation_flags"]["promotion_execution_allowed"] = True
        with self.assertRaises(SchemaValidationError):
            registry.validate("phase3_promotion_evaluator_status", expected)

    def test_evaluator_status_contract_validator_returns_blocked_snapshot(self) -> None:
        snapshot = validate_promotion_evaluator_status_contract()

        self.assertEqual(snapshot["status"], "blocked")
        self.assertFalse(snapshot["mutation_flags"]["promotion_execution_allowed"])

    def test_export_promotion_evaluator_status_bundle_writes_local_artifacts(self) -> None:
        before = DECISION_LEDGER_PATH.read_text(encoding="utf-8") if DECISION_LEDGER_PATH.exists() else ""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = export_promotion_evaluator_status_bundle(Path(tmpdir))
            saved_manifest = json.loads(Path(manifest["manifest_path"]).read_text(encoding="utf-8"))
            artifacts = saved_manifest["artifacts"]
            bodies = {artifact["kind"]: Path(artifact["path"]).read_bytes() for artifact in artifacts}

        after = DECISION_LEDGER_PATH.read_text(encoding="utf-8") if DECISION_LEDGER_PATH.exists() else ""
        self.assertEqual(after, before)
        self.assertEqual(saved_manifest["bundle_id"], "phase3_promotion_evaluator_status_bundle")
        self.assertEqual(saved_manifest["publication_scope"], "internal_phase3_evaluator_diagnostic_only")
        self.assertEqual(saved_manifest["status"], "blocked")
        self.assertFalse(saved_manifest["promotion_execution_allowed"])
        self.assertFalse(saved_manifest["public_report_changed"])
        self.assertFalse(saved_manifest["ledger_appended"])
        self.assertFalse(saved_manifest["live_provider_called"])
        self.assertEqual(
            {artifact["kind"] for artifact in artifacts},
            {"phase3_evaluator_status_json", "phase3_evaluator_status_contract_view_json"},
        )
        for artifact in artifacts:
            body = bodies[artifact["kind"]]
            self.assertEqual(artifact["bytes"], len(body))
            self.assertEqual(artifact["content_hash"], "sha256:" + sha256(body).hexdigest())

    def test_export_promotion_evaluator_status_cli_outputs_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [sys.executable, "-m", "peoples_ledger.cli", "export-promotion-evaluator-status", "--output-dir", tmpdir],
                check=False,
                capture_output=True,
                cwd=REPO_ROOT,
                env={"PYTHONPATH": "src"},
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["bundle_id"], "phase3_promotion_evaluator_status_bundle")
            self.assertFalse(payload["promotion_execution_allowed"])
            self.assertTrue(Path(payload["manifest_path"]).exists())


if __name__ == "__main__":
    unittest.main()
