from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from .paths import REPORT_ARTIFACT_DIR
from .reporting import build_public_report, build_public_report_html


def export_report_artifacts(output_dir: Path = REPORT_ARTIFACT_DIR) -> dict[str, Any]:
    report = build_public_report()
    html = build_public_report_html(report)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / f"{report['report_id']}.json"
    html_path = output_dir / f"{report['report_id']}.html"
    manifest_path = output_dir / f"{report['report_id']}.manifest.json"

    json_body = json.dumps(report, sort_keys=True, indent=2) + "\n"
    html_body = html
    json_path.write_text(json_body, encoding="utf-8")
    html_path.write_text(html_body, encoding="utf-8")

    manifest = {
        "report_id": report["report_id"],
        "analysis_unit_id": report["analysis_unit_id"],
        "artifacts": [
            _artifact_entry("json", json_path, json_body),
            _artifact_entry("html", html_path, html_body),
        ],
    }
    manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return {**manifest, "manifest_path": str(manifest_path)}


def _artifact_entry(kind: str, path: Path, body: str) -> dict[str, Any]:
    return {
        "kind": kind,
        "path": str(path),
        "content_hash": "sha256:" + sha256(body.encode("utf-8")).hexdigest(),
        "bytes": len(body.encode("utf-8")),
    }
