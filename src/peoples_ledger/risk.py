from __future__ import annotations

from dataclasses import dataclass

from .assurance import AssuranceReport
from .challenge_agents import ChallengeReview
from .source_registry import SourceRegistry


@dataclass(frozen=True)
class RiskScore:
    tier: int
    dimensions: dict[str, int]
    rationale: list[str]


def score_risk(
    analysis_unit: dict,
    assurance: AssuranceReport,
    challenge_review: ChallengeReview | None = None,
    source_records: dict[str, dict] | None = None,
) -> RiskScore:
    source_records = source_records or SourceRegistry.load().records
    dimensions = {
        "assurance_failures": _assurance_failure_score(assurance),
        "challenge_disagreement": _challenge_score(challenge_review),
        "unknown_indicator_count": _unknown_indicator_score(analysis_unit),
        "representative_coverage": _coverage_score(analysis_unit),
        "source_diversity": _source_diversity_score(analysis_unit),
        "provision_source_spans": _provision_source_span_score(analysis_unit),
        "official_source_mix": _official_source_mix_score(analysis_unit, source_records),
        "publication_readiness": _publication_readiness_score(analysis_unit),
    }
    tier = max(dimensions.values())
    rationale = [f"{name}:{score}" for name, score in dimensions.items() if score > 1]
    if not rationale:
        rationale = ["all_dimensions_low"]
    return RiskScore(tier=tier, dimensions=dimensions, rationale=rationale)


def _assurance_failure_score(assurance: AssuranceReport) -> int:
    failures = len([check for check in assurance.checks if not check.passed])
    if failures == 0:
        return 1
    if failures == 1:
        return 2
    if failures == 2:
        return 3
    return 4


def _challenge_score(challenge_review: ChallengeReview | None) -> int:
    if challenge_review is None:
        return 1
    if challenge_review.blocking:
        return 3
    if challenge_review.model_disagreement >= 0.25:
        return 2
    return 1


def _unknown_indicator_score(analysis_unit: dict) -> int:
    unknown_count = len([
        indicator
        for indicator in analysis_unit["narrow_benefit_indicators"]
        if indicator["signal"] == "unknown"
    ])
    if unknown_count == 0:
        return 1
    if unknown_count <= 2:
        return 2
    return 3


def _coverage_score(analysis_unit: dict) -> int:
    count = len(analysis_unit["provisions"])
    if 8 <= count <= 12:
        return 1
    if 5 <= count <= 15:
        return 2
    return 3


def _source_diversity_score(analysis_unit: dict) -> int:
    source_ids: set[str] = set(analysis_unit.get("source_record_ids", []))
    for provision in analysis_unit["provisions"]:
        source_ids.update(provision.get("source_record_ids", []))
        source_ids.update(span["source_record_id"] for span in provision.get("source_spans", []))
    for claim in analysis_unit["claims"]:
        for evidence in claim.get("evidence", []):
            source_ids.add(evidence["source_record_id"])

    if len(source_ids) >= 3:
        return 1
    if len(source_ids) == 2:
        return 2
    return 3


def _provision_source_span_score(analysis_unit: dict) -> int:
    provisions = analysis_unit["provisions"]
    if not provisions:
        return 3
    missing_spans = len([provision for provision in provisions if not provision.get("source_spans")])
    if missing_spans == 0:
        return 1
    if missing_spans <= 2:
        return 2
    return 3


def _official_source_mix_score(analysis_unit: dict, source_records: dict[str, dict]) -> int:
    source_ids = _referenced_source_ids(analysis_unit)
    if not source_ids:
        return 3

    found_source_ids = {source_id for source_id in source_ids if source_id in source_records}
    if found_source_ids != source_ids:
        return 3
    source_types = {source_records[source_id]["source_type"] for source_id in source_ids}
    if "other" in source_types:
        return 3
    if "academic" in source_types:
        return 2
    if "statute" in source_types and source_types.issubset({"statute", "government_analysis", "committee_report", "agency_guidance"}):
        return 1
    return 2


def _publication_readiness_score(analysis_unit: dict) -> int:
    if analysis_unit["status"] == "draft":
        return 2

    publication_states = {
        item["publication_state"]
        for collection in ("provisions", "claims")
        for item in analysis_unit[collection]
    }
    if "superseded" in publication_states:
        return 3
    if "machine_parsed" in publication_states:
        return 2
    return 1


def _referenced_source_ids(analysis_unit: dict) -> set[str]:
    source_ids: set[str] = set(analysis_unit.get("source_record_ids", []))
    source_ids.update(analysis_unit["legislative_document"].get("source_record_ids", []))
    for provision in analysis_unit["provisions"]:
        source_ids.update(provision.get("source_record_ids", []))
        source_ids.update(span["source_record_id"] for span in provision.get("source_spans", []))
    for transformation in analysis_unit["statutory_transformations"]:
        source_ids.add(transformation["source_span"]["source_record_id"])
    for claim in analysis_unit["claims"]:
        for evidence in claim.get("evidence", []):
            source_ids.add(evidence["source_record_id"])
    return source_ids
