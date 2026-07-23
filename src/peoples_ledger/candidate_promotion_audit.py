from __future__ import annotations

from typing import Any

from .candidate_promotion import evaluate_candidate_queue_promotion
from .candidate_promotion_decision import load_candidate_promotion_decision_ledger_stubs
from .candidate_promotion_request import load_candidate_promotion_requests
from .candidate_queue import load_candidate_analysis_queue
from .candidate_review import load_candidate_review_records
from .candidate_status import build_candidate_status
from .decision_ledger import DecisionLedger
from .privacy import assert_no_household_financial_data
from .source_promotion import load_source_promotion_manifest


PUBLIC_REPORT_ANALYSIS_UNIT_ID = "tcja_2017_representative_provisions"


class CandidatePromotionAuditError(ValueError):
    """Raised when Phase 2 promotion artifacts disagree."""


def build_candidate_promotion_audit_cross_check() -> dict[str, Any]:
    candidates = load_candidate_analysis_queue()
    reports = evaluate_candidate_queue_promotion(candidates)
    requests = load_candidate_promotion_requests()
    reviews = load_candidate_review_records()
    decision_stubs = load_candidate_promotion_decision_ledger_stubs()
    source_manifest = load_source_promotion_manifest()
    status = build_candidate_status()
    live_ledger_ids = {entry["id"] for entry in DecisionLedger().read_all()}
    public_report_analysis_unit_id = _public_report_analysis_unit_id()

    candidate_ids = {candidate["id"] for candidate in candidates}
    status_ids = {candidate["id"] for candidate in status["candidates"]}
    request_ids_by_candidate = {request["candidate_analysis_unit_id"] for request in requests}
    review_ids_by_candidate = {review["candidate_analysis_unit_id"] for review in reviews}
    decision_ids_by_candidate = {entry["analysis_unit_id"] for entry in decision_stubs}
    proposed_source_ids = {source["source_record"]["id"] for source in source_manifest["proposed_sources"]}

    candidate_summaries = []
    for candidate in candidates:
        candidate_id = candidate["id"]
        report = _one([item for item in reports if item["candidate_analysis_unit_id"] == candidate_id], candidate_id)
        request = _one([item for item in requests if item["candidate_analysis_unit_id"] == candidate_id], candidate_id)
        review = _one([item for item in reviews if item["candidate_analysis_unit_id"] == candidate_id], candidate_id)
        decision = _one([item for item in decision_stubs if item["analysis_unit_id"] == candidate_id], candidate_id)
        status_record = _one([item for item in status["candidates"] if item["id"] == candidate_id], candidate_id)

        report_blockers = {blocker["gate"] for blocker in report["blockers"]}
        request_blockers = {blocker["gate"] for blocker in request["current_blockers"]}
        decision_blockers = set(decision["structured_output"]["blocker_gates"])
        candidate_source_ids = {ref["source_record_id"] for ref in candidate["source_snapshot_refs"]}

        candidate_summaries.append(
            {
                "candidate_analysis_unit_id": candidate_id,
                "status": candidate["status"],
                "publication_state": candidate["publication_state"],
                "promotable": report["promotable"],
                "status_surface_promotable": status_record["promotable"],
                "review_recommendation": review["promotion_recommendation"],
                "promotion_request_status": request["request_status"],
                "promotion_decision": decision["structured_output"]["promotion_decision"],
                "blocker_gates": sorted(report_blockers),
                "blockers_match": report_blockers == request_blockers == decision_blockers,
                "source_refs_match": candidate_source_ids
                == set(decision["source_snapshot_ids"])
                == proposed_source_ids,
                "decision_stub_in_live_ledger": decision["id"] in live_ledger_ids,
                "public_report_includes_candidate": public_report_analysis_unit_id == candidate_id,
            }
        )

    cross_check = {
        "id": "phase2_promotion_audit_cross_check_v1",
        "phase": "phase2_promotion_audit",
        "candidate_ids_match": candidate_ids
        == status_ids
        == request_ids_by_candidate
        == review_ids_by_candidate
        == decision_ids_by_candidate,
        "public_report_includes_candidates": public_report_analysis_unit_id in candidate_ids,
        "source_promotion_state": source_manifest["promotion_state"],
        "source_registry_update_allowed": source_manifest["registry_update_allowed"],
        "candidate_summaries": candidate_summaries,
    }
    assert_no_household_financial_data(cross_check)
    _validate_cross_check(cross_check)
    return cross_check


def validate_candidate_promotion_audit_cross_check() -> None:
    build_candidate_promotion_audit_cross_check()


def _validate_cross_check(cross_check: dict[str, Any]) -> None:
    if not cross_check["candidate_ids_match"]:
        raise CandidatePromotionAuditError("promotion audit candidate ids do not match")
    if cross_check["public_report_includes_candidates"]:
        raise CandidatePromotionAuditError("promotion audit found candidate in public report")
    if cross_check["source_promotion_state"] != "blocked":
        raise CandidatePromotionAuditError("promotion audit source promotion is not blocked")
    if cross_check["source_registry_update_allowed"]:
        raise CandidatePromotionAuditError("promotion audit source registry update is allowed")
    for summary in cross_check["candidate_summaries"]:
        if summary["publication_state"] != "draft":
            raise CandidatePromotionAuditError(f"candidate is not draft: {summary['candidate_analysis_unit_id']}")
        if summary["promotable"] or summary["status_surface_promotable"]:
            raise CandidatePromotionAuditError(f"candidate is promotable: {summary['candidate_analysis_unit_id']}")
        if summary["review_recommendation"] != "blocked":
            raise CandidatePromotionAuditError(f"candidate review does not block: {summary['candidate_analysis_unit_id']}")
        if summary["promotion_request_status"] != "blocked":
            raise CandidatePromotionAuditError(f"promotion request is not blocked: {summary['candidate_analysis_unit_id']}")
        if summary["promotion_decision"] != "blocked":
            raise CandidatePromotionAuditError(f"promotion decision is not blocked: {summary['candidate_analysis_unit_id']}")
        if not summary["blockers_match"]:
            raise CandidatePromotionAuditError(f"promotion blockers do not match: {summary['candidate_analysis_unit_id']}")
        if not summary["source_refs_match"]:
            raise CandidatePromotionAuditError(f"promotion source refs do not match: {summary['candidate_analysis_unit_id']}")
        if summary["decision_stub_in_live_ledger"]:
            raise CandidatePromotionAuditError(f"promotion decision stub is in live ledger: {summary['candidate_analysis_unit_id']}")
        if summary["public_report_includes_candidate"]:
            raise CandidatePromotionAuditError(f"candidate appears in public report: {summary['candidate_analysis_unit_id']}")


def _one(items: list[dict[str, Any]], candidate_id: str) -> dict[str, Any]:
    if len(items) != 1:
        raise CandidatePromotionAuditError(f"expected exactly one artifact for candidate: {candidate_id}")
    return items[0]


def _public_report_analysis_unit_id() -> str:
    return PUBLIC_REPORT_ANALYSIS_UNIT_ID
