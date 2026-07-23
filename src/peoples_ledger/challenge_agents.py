from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .analysis import load_analysis_unit
from .assurance import run_assurance_gate, validation_results_from_report
from .decision_ledger import DecisionLedger
from .source_registry import SourceRegistry


@dataclass(frozen=True)
class ChallengeReview:
    agent: str
    model: dict[str, str]
    model_disagreement: float
    findings: list[str]
    review_triggers: list[str]
    blocking: bool


class DeterministicChallengeAgent:
    name = "deterministic-challenge-agent"
    model_name = "challenge-poc-v1"
    version = "1.0"

    def review(self, analysis_unit: dict[str, Any]) -> ChallengeReview:
        findings: list[str] = []
        review_triggers: list[str] = []
        blocking = False

        if len(analysis_unit["provisions"]) < 8:
            findings.append("Representative subset contains fewer than eight provisions.")
            review_triggers.append("challenge:fewer_than_eight_provisions")
            blocking = True

        unknown_indicators = [
            indicator["id"]
            for indicator in analysis_unit["narrow_benefit_indicators"]
            if indicator["signal"] == "unknown"
        ]
        if unknown_indicators:
            findings.append("Unknown indicator signals remain visible for reviewer awareness.")

        if not findings:
            findings.append("No blocking disagreement found in deterministic POC challenge review.")

        disagreement = 0.08 + (0.2 if blocking else 0.0) + (0.02 * len(unknown_indicators))
        return ChallengeReview(
            agent=self.name,
            model={"provider": self.name, "name": self.model_name, "version": self.version},
            model_disagreement=round(disagreement, 2),
            findings=findings,
            review_triggers=review_triggers,
            blocking=blocking,
        )


class SourceCoverageChallengeAgent:
    name = "source-coverage-challenge-agent"
    model_name = "source-coverage-poc-v1"
    version = "1.0"

    def review(self, analysis_unit: dict[str, Any]) -> ChallengeReview:
        findings: list[str] = []
        review_triggers: list[str] = []
        blocking = False

        provision_count = len(analysis_unit["provisions"])
        public_law_refs = [
            provision
            for provision in analysis_unit["provisions"]
            if any(span["source_record_id"] == "pl115_97_public_law" for span in provision["source_spans"])
        ]
        if len(public_law_refs) != provision_count:
            findings.append("One or more provisions lack a public law source span.")
            review_triggers.append("challenge:missing_public_law_span")
            blocking = True

        source_ids = {
            span["source_record_id"]
            for provision in analysis_unit["provisions"]
            for span in provision["source_spans"]
        }
        if len(source_ids) < 2:
            findings.append("The exemplar has limited source diversity.")
            review_triggers.append("challenge:limited_source_diversity")

        if not findings:
            findings.append("Source coverage challenge found public-law spans for every provision.")

        disagreement = 0.06 + (0.25 if blocking else 0.0) + (0.05 if len(source_ids) < 2 else 0.0)
        return ChallengeReview(
            agent=self.name,
            model={"provider": self.name, "name": self.model_name, "version": self.version},
            model_disagreement=round(disagreement, 2),
            findings=findings,
            review_triggers=review_triggers,
            blocking=blocking,
        )


def compare_challenge_agents(analysis_unit: dict[str, Any] | None = None) -> dict[str, Any]:
    analysis_unit = analysis_unit or load_analysis_unit()
    agents = [DeterministicChallengeAgent(), SourceCoverageChallengeAgent()]
    reviews = [agent.review(analysis_unit) for agent in agents]
    return {
        "agent_count": len(reviews),
        "max_model_disagreement": max(review.model_disagreement for review in reviews),
        "blocking": any(review.blocking for review in reviews),
        "review_triggers": sorted({trigger for review in reviews for trigger in review.review_triggers}),
        "reviews": [
            {
                "agent": review.agent,
                "model": review.model,
                "model_disagreement": review.model_disagreement,
                "findings": review.findings,
                "review_triggers": review.review_triggers,
                "blocking": review.blocking,
            }
            for review in reviews
        ],
    }


def record_challenge_review(ledger: DecisionLedger | None = None) -> dict[str, Any]:
    analysis_unit = load_analysis_unit()
    agent = DeterministicChallengeAgent()
    review = agent.review(analysis_unit)
    assurance = run_assurance_gate()
    source_registry = SourceRegistry.load()
    source_ids = analysis_unit["legislative_document"]["source_record_ids"]
    ledger = ledger or DecisionLedger()

    return ledger.append(
        analysis_unit_id=analysis_unit["id"],
        actor=review.agent,
        action="challenge_review",
        decision_type="challenge_review",
        model=review.model,
        prompt_template_version="challenge-review-poc-v1",
        source_snapshot_ids=source_ids,
        source_hashes=[source_registry.require(source_id)["integrity"]["content_hash"] for source_id in source_ids],
        baseline_id=analysis_unit["model_scenarios"][0]["baseline_id"],
        model_scenario_id=analysis_unit["model_scenarios"][0]["id"],
        structured_output={
            "findings": review.findings,
            "blocking": review.blocking,
        },
        calibrated_confidence=0.76,
        model_disagreement=review.model_disagreement,
        validation_results=validation_results_from_report(assurance),
        risk_tier=max(assurance.risk_tier, 2 if review.review_triggers else 1),
        publication_lane="provisional_analytical",
        publication_state="provisional_analysis" if not review.blocking else "machine_parsed",
        human_review_required=review.blocking,
        review_triggers=review.review_triggers,
        input_refs=source_ids,
        output_refs=[analysis_unit["id"]],
        rationale="Deterministic challenge-agent review for Phase 1 assurance disagreement recording.",
        payload={"findings": review.findings, "blocking": review.blocking},
    )


def record_challenge_comparison(ledger: DecisionLedger | None = None) -> dict[str, Any]:
    analysis_unit = load_analysis_unit()
    comparison = compare_challenge_agents(analysis_unit)
    assurance = run_assurance_gate()
    source_registry = SourceRegistry.load()
    source_ids = analysis_unit["legislative_document"]["source_record_ids"]
    ledger = ledger or DecisionLedger()

    return ledger.append(
        analysis_unit_id=analysis_unit["id"],
        actor="deterministic-challenge-comparison",
        action="challenge_comparison",
        decision_type="challenge_comparison",
        model={"provider": "deterministic-challenge-comparison", "name": "challenge-comparison-poc-v1", "version": "1.0"},
        prompt_template_version="challenge-comparison-poc-v1",
        source_snapshot_ids=source_ids,
        source_hashes=[source_registry.require(source_id)["integrity"]["content_hash"] for source_id in source_ids],
        baseline_id=analysis_unit["model_scenarios"][0]["baseline_id"],
        model_scenario_id=analysis_unit["model_scenarios"][0]["id"],
        structured_output=comparison,
        calibrated_confidence=0.74,
        model_disagreement=comparison["max_model_disagreement"],
        validation_results=validation_results_from_report(assurance),
        risk_tier=max(assurance.risk_tier, 3 if comparison["blocking"] else 1),
        publication_lane="provisional_analytical",
        publication_state="provisional_analysis" if not comparison["blocking"] else "machine_parsed",
        human_review_required=comparison["blocking"],
        review_triggers=comparison["review_triggers"],
        input_refs=source_ids,
        output_refs=[analysis_unit["id"]],
        rationale="Deterministic multi-agent challenge comparison for Phase 1 assurance.",
        payload=comparison,
    )
