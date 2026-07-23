from __future__ import annotations

from typing import Any

from .candidate_promotion import evaluate_candidate_promotion
from .candidate_queue import load_candidate_analysis_queue


def build_candidate_status() -> dict[str, Any]:
    candidates = load_candidate_analysis_queue()
    candidate_views = []
    for candidate in candidates:
        promotion = evaluate_candidate_promotion(candidate)
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
            }
        )
    return {
        "status": "ok",
        "candidate_count": len(candidate_views),
        "public_report_includes_candidates": False,
        "ledger_appended": False,
        "candidates": candidate_views,
    }
