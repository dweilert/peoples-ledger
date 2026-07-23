from __future__ import annotations

from dataclasses import dataclass

from .assurance import AssuranceReport
from .challenge_agents import ChallengeReview


@dataclass(frozen=True)
class PublicationDecision:
    lane: str
    state: str
    allowed: bool
    risk_tier: int
    review_triggers: list[str]
    rationale: str


def decide_publication_state(
    assurance: AssuranceReport,
    challenge_review: ChallengeReview | None = None,
) -> PublicationDecision:
    triggers = list(assurance.review_triggers)
    risk_tier = assurance.risk_tier

    if challenge_review is not None:
        triggers.extend(challenge_review.review_triggers)
        risk_tier = max(risk_tier, 3 if challenge_review.blocking else 1)

    if not assurance.passed:
        return PublicationDecision(
            lane="provisional_analytical",
            state="blocked",
            allowed=False,
            risk_tier=risk_tier,
            review_triggers=triggers,
            rationale="Assurance checks failed; publication state cannot advance.",
        )

    if challenge_review is not None and challenge_review.blocking:
        return PublicationDecision(
            lane="provisional_analytical",
            state="machine_parsed",
            allowed=False,
            risk_tier=risk_tier,
            review_triggers=triggers,
            rationale="Challenge review produced blocking disagreement.",
        )

    if risk_tier >= 3:
        return PublicationDecision(
            lane="provisional_analytical",
            state="machine_parsed",
            allowed=False,
            risk_tier=risk_tier,
            review_triggers=triggers or ["publication_review:risk_tier_threshold"],
            rationale="Risk tier requires review before provisional publication.",
        )

    return PublicationDecision(
        lane="provisional_analytical",
        state="provisional_analysis",
        allowed=True,
        risk_tier=risk_tier,
        review_triggers=triggers,
        rationale="Assurance checks passed and no blocking disagreement was found.",
    )
