from __future__ import annotations

from typing import Any

from .candidate_promotion import evaluate_candidate_promotion
from .candidate_queue import load_candidate_analysis_queue
from .candidate_review import candidate_review_summary


def build_candidate_status() -> dict[str, Any]:
    candidates = load_candidate_analysis_queue()
    review_by_candidate_id = candidate_review_summary()
    candidate_views = []
    for candidate in candidates:
        promotion = evaluate_candidate_promotion(candidate)
        review = review_by_candidate_id.get(candidate["id"])
        candidate_views.append(
            {
                "id": candidate["id"],
                "title": candidate["title"],
                "status": candidate["status"],
                "publication_state": candidate["publication_state"],
                "source_record_ids": candidate["legislative_document"]["source_record_ids"],
                "candidate_provision_ids": [provision["id"] for provision in candidate["candidate_provisions"]],
                "model_scenario_allowed": candidate["model_scenario_policy"]["allowed"],
                "perspective_allowed": candidate["perspective_policy"]["allowed"],
                "uses_household_financial_data": candidate["privacy"]["uses_household_financial_data"],
                "egress_allowed": candidate["privacy"]["egress_allowed"],
                "promotable": promotion["promotable"],
                "promotion_blockers": promotion["blockers"],
                "review_status": review["review_status"] if review else "review_required",
                "review_findings": review["findings"] if review else [],
                "review_promotion_recommendation": review["promotion_recommendation"] if review else "blocked",
            }
        )
    return {
        "status": "ok",
        "candidate_count": len(candidate_views),
        "public_report_includes_candidates": False,
        "ledger_appended": False,
        "candidates": candidate_views,
    }
