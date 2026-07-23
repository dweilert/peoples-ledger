from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.candidate_audit import (
    build_candidate_audit_bundle,
    export_candidate_audit_bundle,
    validate_candidate_audit_bundle,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class CandidateAuditTests(unittest.TestCase):
    def test_candidate_audit_bundle_is_internal_and_excludes_public_report_leakage(self) -> None:
        bundle = build_candidate_audit_bundle()

        self.assertEqual(bundle["bundle_id"], "candidate_audit_phase2_poc")
        self.assertEqual(bundle["publication_scope"], "internal_candidate_audit_only")
        self.assertFalse(bundle["public_report_includes_candidates"])
        self.assertEqual(bundle["candidate_status"]["candidate_count"], 1)
        self.assertFalse(bundle["candidate_status"]["candidates"][0]["promotable"])
        self.assertTrue(bundle["promotion_gate_reports"][0]["blockers"])
        self.assertEqual(bundle["review_records"][0]["promotion_recommendation"], "blocked")

    def test_candidate_audit_bundle_contains_dry_run_ledger_summaries_only(self) -> None:
        bundle = build_candidate_audit_bundle()
        extraction = bundle["dry_run_ledger_summaries"]["candidate_extraction"][0]
        review = bundle["dry_run_ledger_summaries"]["candidate_review"][0]

        self.assertEqual(extraction["action"], "candidate_locator_extraction")
        self.assertEqual(review["action"], "candidate_human_review")
        self.assertEqual(extraction["disclosure_class"], "restricted")
        self.assertEqual(review["disclosure_class"], "restricted")
        self.assertTrue(extraction["entry_hash"].startswith("sha256:"))
        self.assertTrue(review["entry_hash"].startswith("sha256:"))
        self.assertNotIn("structured_output", extraction)
        self.assertNotIn("structured_output", review)

    def test_export_candidate_audit_bundle_writes_json_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = export_candidate_audit_bundle(Path(tmpdir))
            manifest_path = Path(manifest["manifest_path"])
            saved_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            artifact = saved_manifest["artifacts"][0]
            artifact_path = Path(artifact["path"])
            body = artifact_path.read_bytes()

        self.assertEqual(saved_manifest["bundle_id"], "candidate_audit_phase2_poc")
        self.assertEqual(saved_manifest["publication_scope"], "internal_candidate_audit_only")
        self.assertEqual(artifact["kind"], "candidate_audit_json")
        self.assertEqual(artifact["bytes"], len(body))
        self.assertEqual(artifact["content_hash"], "sha256:" + sha256(body).hexdigest())

    def test_candidate_audit_validation_passes(self) -> None:
        validate_candidate_audit_bundle()

    def test_export_candidate_audit_cli_outputs_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [sys.executable, "-m", "peoples_ledger.cli", "export-candidate-audit", "--output-dir", tmpdir],
                cwd=REPO_ROOT,
                env={"PYTHONPATH": "src"},
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["bundle_id"], "candidate_audit_phase2_poc")
            self.assertTrue(Path(payload["manifest_path"]).exists())


if __name__ == "__main__":
    unittest.main()
