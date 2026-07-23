from __future__ import annotations

import json
import sys
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peoples_ledger.report_artifacts import export_report_artifacts


class ReportArtifactTests(unittest.TestCase):
    def test_export_report_artifacts_writes_json_html_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = export_report_artifacts(Path(tmpdir))
            manifest_path = Path(manifest["manifest_path"])
            self.assertTrue(manifest_path.exists())
            self.assertEqual(manifest["analysis_unit_id"], "tcja_2017_representative_provisions")
            self.assertEqual({artifact["kind"] for artifact in manifest["artifacts"]}, {"json", "html"})
            for artifact in manifest["artifacts"]:
                path = Path(artifact["path"])
                body = path.read_bytes()
                self.assertTrue(path.exists())
                self.assertEqual(artifact["bytes"], len(body))
                self.assertEqual(artifact["content_hash"], "sha256:" + sha256(body).hexdigest())

    def test_exported_manifest_is_stable_and_readable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = export_report_artifacts(Path(tmpdir))
            saved = json.loads(Path(manifest["manifest_path"]).read_text(encoding="utf-8"))
        self.assertEqual(saved["report_id"], "report_tcja_2017_representative_provisions_phase1_poc")
        self.assertNotIn("manifest_path", saved)
        self.assertEqual(len(saved["artifacts"]), 2)


if __name__ == "__main__":
    unittest.main()
