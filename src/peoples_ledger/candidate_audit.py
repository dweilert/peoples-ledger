from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from .candidate_extraction import record_candidate_locator_extraction
from .candidate_promotion import evaluate_candidate_queue_promotion
from .candidate_queue import load_candidate_analysis_queue
from .candidate_review import load_candidate_review_records, record_candidate_review_decision
from .candidate_status import build_candidate_status
from .decision_ledger import DecisionLedger
from .paths import CANDIDATE_AUDIT_ARTIFACT_DIR
from .privacy import assert_no_household_financial_data


def build_candidate_audit_bundle() -> dict[str, Any]:
    candidates = load_candidate_analysis_queue()
    review_records = load_candidate_review_records()
    extraction_entries = [
        _dry_run_entry(lambda ledger, candidate=candidate: record_candidate_locator_extraction(candidate, ledger))
        for candidate in candidates
    ]
    review_entries = [
        _dry_run_entry(lambda ledger, review=review: record_candidate_review_decision(review, ledger))
        for review in review_records
    ]
    candidate_ids = {candidate["id"] for candidate in candidates}
    public_report_analysis_unit_id = "tcja_2017_representative_provisions"

    bundle = {
        "bundle_id": "candidate_audit_phase2_poc",
        "phase": "phase2_candidate_audit",
        "publication_scope": "internal_candidate_audit_only",
        "public_report_includes_candidates": public_report_analysis_unit_id in candidate_ids,
        "candidate_status": build_candidate_status(),
        "promotion_gate_reports": evaluate_candidate_queue_promotion(candidates),
        "review_records": review_records,
        "dry_run_ledger_summaries": {
            "candidate_extraction": extraction_entries,
            "candidate_review": review_entries,
        },
    }
    assert_no_household_financial_data(bundle)
    if bundle["public_report_includes_candidates"]:
        raise ValueError("candidate audit bundle detected candidate leakage into public report")
    return bundle


def export_candidate_audit_bundle(output_dir: Path = CANDIDATE_AUDIT_ARTIFACT_DIR) -> dict[str, Any]:
    bundle = build_candidate_audit_bundle()
    output_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = output_dir / f"{bundle['bundle_id']}.json"
    manifest_path = output_dir / f"{bundle['bundle_id']}.manifest.json"
    bundle_body = json.dumps(bundle, sort_keys=True, indent=2) + "\n"
    bundle_path.write_text(bundle_body, encoding="utf-8")
    manifest = {
        "bundle_id": bundle["bundle_id"],
        "publication_scope": bundle["publication_scope"],
        "artifacts": [_artifact_entry("candidate_audit_json", bundle_path, bundle_body)],
    }
    manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return {**manifest, "manifest_path": str(manifest_path)}


def validate_candidate_audit_bundle() -> None:
    bundle = build_candidate_audit_bundle()
    if bundle["publication_scope"] != "internal_candidate_audit_only":
        raise ValueError("candidate audit bundle publication scope is unsafe")
    if bundle["public_report_includes_candidates"]:
        raise ValueError("candidate audit bundle includes public-report candidate leakage")


def _dry_run_entry(record_fn: Any) -> dict[str, Any]:
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        ledger = DecisionLedger(Path(tmpdir) / "candidate_audit_ledger.jsonl")
        entry = record_fn(ledger)
        ledger.read_all()
    return {
        "id": entry["id"],
        "analysis_unit_id": entry["analysis_unit_id"],
        "action": entry["action"],
        "decision_type": entry["decision_type"],
        "publication_state": entry["publication_state"],
        "disclosure_class": entry["disclosure_class"],
        "human_review_required": entry["human_review_required"],
        "review_triggers": entry["review_triggers"],
        "entry_hash": entry["entry_hash"],
    }


def _artifact_entry(kind: str, path: Path, body: str) -> dict[str, Any]:
    encoded = body.encode("utf-8")
    return {
        "kind": kind,
        "path": str(path),
        "content_hash": "sha256:" + sha256(encoded).hexdigest(),
        "bytes": len(encoded),
    }
