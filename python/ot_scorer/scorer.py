"""Weighted OT scorer prototype from constraint violation records."""

from __future__ import annotations

from typing import Any

from ot_scorer.models import (
    CandidateScore,
    CandidateScoreSet,
    ConstraintContribution,
    ConstraintWeight,
)
from ot_scorer.violation_set_loader import validate_constraint_violation_set

SCORING_POLICY_VERSION = "weighted_ot_scorer_policy_v0_1"
BLOCKING_WEIGHT = 1_000_000.0
BLOCKING_CONSTRAINT_IDS: frozenset[str] = frozenset(
    {
        "NO-LEAKAGE-FLAG",
        "NO-OBSERVED-EDIT-TEXT",
        "NO-UNSAFE-CANDIDATE",
    }
)
CONSTRAINT_WEIGHTS: dict[str, ConstraintWeight] = {
    "NO-LEAKAGE-FLAG": ConstraintWeight(
        constraint_id="NO-LEAKAGE-FLAG",
        weight=BLOCKING_WEIGHT,
        is_blocking=True,
        rationale="Safety constraint: leakage flags block scoring use.",
    ),
    "NO-OBSERVED-EDIT-TEXT": ConstraintWeight(
        constraint_id="NO-OBSERVED-EDIT-TEXT",
        weight=BLOCKING_WEIGHT,
        is_blocking=True,
        rationale="Safety constraint: observed edit text is no-oracle unsafe.",
    ),
    "NO-UNSAFE-CANDIDATE": ConstraintWeight(
        constraint_id="NO-UNSAFE-CANDIDATE",
        weight=BLOCKING_WEIGHT,
        is_blocking=True,
        rationale="Safety constraint: candidate must be no-oracle safe.",
    ),
    "HOLD-CANDIDATE": ConstraintWeight(
        constraint_id="HOLD-CANDIDATE",
        weight=0.0,
        is_blocking=False,
        rationale="Descriptive only in the prototype.",
    ),
    "LOCAL-EDIT-CANDIDATE": ConstraintWeight(
        constraint_id="LOCAL-EDIT-CANDIDATE",
        weight=0.0,
        is_blocking=False,
        rationale="Descriptive only in the prototype.",
    ),
    "GRAMMAR-PLACEHOLDER-CANDIDATE": ConstraintWeight(
        constraint_id="GRAMMAR-PLACEHOLDER-CANDIDATE",
        weight=0.0,
        is_blocking=False,
        rationale="Descriptive only in the prototype.",
    ),
    "PLACEHOLDER-CANDIDATE": ConstraintWeight(
        constraint_id="PLACEHOLDER-CANDIDATE",
        weight=0.0,
        is_blocking=False,
        rationale="Descriptive only in the prototype.",
    ),
}


def build_candidate_score_sets(
    violation_sets: list[dict[str, Any]],
) -> list[CandidateScoreSet]:
    return [build_candidate_score_set(violation_set) for violation_set in violation_sets]


def build_candidate_score_set(violation_set: dict[str, Any]) -> CandidateScoreSet:
    validate_constraint_violation_set(violation_set)
    scores = [
        score_candidate(candidate_violation)
        for candidate_violation in violation_set["candidate_violations"]
    ]
    ranked_scores = assign_ranks(scores)
    return CandidateScoreSet(
        candidate_score_set_id=f"{violation_set['constraint_violation_set_id']}:scores",
        constraint_violation_set_id=str(violation_set["constraint_violation_set_id"]),
        episode_id=str(violation_set["episode_id"]),
        scoring_policy_version=SCORING_POLICY_VERSION,
        candidate_scores=ranked_scores,
    )


def score_candidate(candidate_violation: dict[str, Any]) -> CandidateScore:
    contributions = [
        contribution_from_violation(violation)
        for violation in candidate_violation["violations"]
    ]
    block_reasons = [
        contribution.constraint_id
        for contribution in contributions
        if contribution.constraint_id in BLOCKING_CONSTRAINT_IDS
        and contribution.violation_count > 0
    ]
    weighted_score = sum(contribution.contribution for contribution in contributions)
    return CandidateScore(
        candidate_id=str(candidate_violation["candidate_id"]),
        episode_id=str(candidate_violation["episode_id"]),
        weighted_score=weighted_score,
        blocked=bool(block_reasons),
        block_reasons=block_reasons,
        rank=0,
        constraint_contributions=contributions,
        scoring_policy_version=SCORING_POLICY_VERSION,
        no_oracle_safe=not block_reasons,
    )


def contribution_from_violation(violation: dict[str, Any]) -> ConstraintContribution:
    constraint_id = str(violation["constraint_id"])
    weight = CONSTRAINT_WEIGHTS.get(
        constraint_id,
        ConstraintWeight(
            constraint_id=constraint_id,
            weight=0.0,
            is_blocking=False,
            rationale="Unknown constraints are not weighted in the prototype.",
        ),
    )
    violation_count = int(violation["violation_count"])
    contribution = weight.weight * violation_count
    return ConstraintContribution(
        constraint_id=constraint_id,
        constraint_type=str(violation["constraint_type"]),
        violation_count=violation_count,
        weight=weight.weight,
        contribution=contribution,
        observed=violation.get("observed") is True,
    )


def assign_ranks(scores: list[CandidateScore]) -> list[CandidateScore]:
    ordered = sorted(scores, key=score_sort_key)
    ranked = []
    for index, score in enumerate(ordered, start=1):
        ranked.append(
            CandidateScore(
                candidate_id=score.candidate_id,
                episode_id=score.episode_id,
                weighted_score=score.weighted_score,
                blocked=score.blocked,
                block_reasons=score.block_reasons,
                rank=index,
                constraint_contributions=score.constraint_contributions,
                scoring_policy_version=score.scoring_policy_version,
                no_oracle_safe=score.no_oracle_safe,
            )
        )
    return ranked


def score_sort_key(score: CandidateScore) -> tuple[bool, float, int, str]:
    return (
        score.blocked,
        score.weighted_score,
        tie_break_priority(score),
        score.candidate_id,
    )


def tie_break_priority(score: CandidateScore) -> int:
    observed_constraints = {
        contribution.constraint_id
        for contribution in score.constraint_contributions
        if contribution.observed
    }
    if "HOLD-CANDIDATE" in observed_constraints:
        return 0
    if "LOCAL-EDIT-CANDIDATE" in observed_constraints:
        return 1
    if "GRAMMAR-PLACEHOLDER-CANDIDATE" in observed_constraints:
        return 2
    if "PLACEHOLDER-CANDIDATE" in observed_constraints:
        return 3
    return 4
