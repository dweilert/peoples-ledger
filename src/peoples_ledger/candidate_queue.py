from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .paths import CANDIDATE_ANALYSIS_QUEUE_PATH, SCHEMA_DIR, SOURCE_ACQUISITION_MANIFEST_PATH
from .privacy import assert_no_household_financial_data
from .schema_validator import SchemaRegistry
from .source_acquisition import acquire_source_records_from_manifest, load_source_acquisition_manifest


class CandidateQueueError(ValueError):
    """Raised when Phase 2 candidate analysis units violate queue boundaries."""


class CandidatePromotionError(ValueError):
    """Raised when a draft candidate is asked to advance without complete promotion gates."""


def load_candidate_analysis_queue(path: Path = CANDIDATE_ANALYSIS_QUEUE_PATH) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        candidates = json.load(handle)
    schema_registry = SchemaRegistry(SCHEMA_DIR)
    for candidate in candidates:
        assert_no_household_financial_data(candidate)
        schema_registry.validate("candidate_analysis_unit", candidate)
    _validate_candidate_links(candidates)
    return candidates


def validate_candidate_analysis_queue(path: Path = CANDIDATE_ANALYSIS_QUEUE_PATH) -> None:
    load_candidate_analysis_queue(path)


def assert_candidate_is_not_promotable(candidate: dict[str, Any]) -> None:
    if candidate["status"] != "draft" or candidate["publication_state"] != "draft":
        raise CandidateQueueError("Phase 2 candidate analysis units must remain draft-only")
    missing = [name for name, passed in candidate["promotion_requirements"].items() if not passed]
    if missing:
        raise CandidatePromotionError(f"candidate promotion blocked by missing gates: {missing}")
    raise CandidatePromotionError("candidate promotion is disabled until Phase 2 promotion gates are implemented")


def _validate_candidate_links(candidates: list[dict[str, Any]]) -> None:
    manifest = load_source_acquisition_manifest(SOURCE_ACQUISITION_MANIFEST_PATH)
    records, snapshots = acquire_source_records_from_manifest(SOURCE_ACQUISITION_MANIFEST_PATH)
    record_ids = {record["id"] for record in records}
    snapshot_hashes = {snapshot["source_record_id"]: snapshot["content_hash"] for snapshot in snapshots}

    candidate_ids: set[str] = set()
    for candidate in candidates:
        if candidate["id"] in candidate_ids:
            raise CandidateQueueError(f"duplicate candidate analysis unit id: {candidate['id']}")
        candidate_ids.add(candidate["id"])
        if candidate["source_acquisition_manifest_id"] != manifest["id"]:
            raise CandidateQueueError(f"candidate {candidate['id']} references unknown acquisition manifest")
        if candidate["status"] != "draft" or candidate["publication_state"] != "draft":
            raise CandidateQueueError(f"candidate {candidate['id']} must remain draft-only")
        if candidate["privacy"]["uses_household_financial_data"] or candidate["privacy"]["egress_allowed"]:
            raise CandidateQueueError(f"candidate {candidate['id']} violates Phase 2 privacy boundaries")
        if candidate["model_scenario_policy"]["allowed"] or candidate["perspective_policy"]["allowed"]:
            raise CandidateQueueError(f"candidate {candidate['id']} enables reporting behavior before promotion gates")

        document_source_ids = set(candidate["legislative_document"]["source_record_ids"])
        _require_known_sources(candidate["id"], document_source_ids, record_ids)

        snapshot_source_ids = {ref["source_record_id"] for ref in candidate["source_snapshot_refs"]}
        if document_source_ids != snapshot_source_ids:
            raise CandidateQueueError(f"candidate {candidate['id']} source snapshots do not match document sources")
        for ref in candidate["source_snapshot_refs"]:
            expected_hash = snapshot_hashes.get(ref["source_record_id"])
            if ref["content_hash"] != expected_hash:
                raise CandidateQueueError(f"candidate {candidate['id']} source snapshot hash mismatch")

        for provision in candidate["candidate_provisions"]:
            _require_known_sources(candidate["id"], set(provision["source_record_ids"]), record_ids)


def _require_known_sources(candidate_id: str, source_ids: set[str], allowed_source_ids: set[str]) -> None:
    missing = sorted(source_ids - allowed_source_ids)
    if missing:
        raise CandidateQueueError(f"candidate {candidate_id} references unknown candidate sources: {missing}")
