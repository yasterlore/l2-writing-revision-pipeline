"""Build OT-style constraint violation records from candidate features."""

from __future__ import annotations

from typing import Any

from ot_scorer.feature_set_loader import validate_candidate_feature_set
from ot_scorer.models import (
    CandidateConstraintViolations,
    Constraint,
    ConstraintViolation,
    ConstraintViolationSet,
)

CONSTRAINT_SCHEMA_VERSION = "ot_constraint_schema_v0_2"

CONSTRAINTS: tuple[Constraint, ...] = (
    Constraint(
        constraint_id="NO-LEAKAGE-FLAG",
        constraint_type="penalty",
        severity="blocking",
        explanation="Candidate leakage_flags must be empty before scoring.",
    ),
    Constraint(
        constraint_id="NO-OBSERVED-EDIT-TEXT",
        constraint_type="penalty",
        severity="blocking",
        explanation="Candidate must not use observed edit text.",
    ),
    Constraint(
        constraint_id="NO-UNSAFE-CANDIDATE",
        constraint_type="penalty",
        severity="blocking",
        explanation="Candidate must be marked no_oracle_safe=true.",
    ),
    Constraint(
        constraint_id="HOLD-CANDIDATE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the candidate is a hold baseline.",
    ),
    Constraint(
        constraint_id="LOCAL-EDIT-CANDIDATE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the candidate is a local edit placeholder.",
    ),
    Constraint(
        constraint_id="GRAMMAR-PLACEHOLDER-CANDIDATE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the candidate is a grammar placeholder.",
    ),
    Constraint(
        constraint_id="PLACEHOLDER-CANDIDATE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the candidate is any placeholder candidate.",
    ),
    Constraint(
        constraint_id="HAS-GENERATION-RULE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the candidate has a generation rule.",
    ),
    Constraint(
        constraint_id="HAS-ACTION-FAMILY",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the candidate has an action family.",
    ),
    Constraint(
        constraint_id="CANDIDATE-METADATA-COMPLETE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether required candidate metadata is complete.",
    ),
    Constraint(
        constraint_id="HOLD-FAMILY-CANDIDATE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the candidate belongs to the hold family.",
    ),
    Constraint(
        constraint_id="LOCAL-EDIT-FAMILY-CANDIDATE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the candidate belongs to the local-edit family.",
    ),
    Constraint(
        constraint_id="GRAMMAR-FAMILY-CANDIDATE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the candidate belongs to the grammar family.",
    ),
    Constraint(
        constraint_id="PLACEHOLDER-FAMILY-CANDIDATE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the candidate belongs to a placeholder family.",
    ),
    Constraint(
        constraint_id="SAFETY-RELEVANT-CANDIDATE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the candidate has safety-relevant metadata.",
    ),
    Constraint(
        constraint_id="CANDIDATE-FAMILY-BUCKET",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the candidate has a structural family bucket.",
    ),
)


def build_constraint_violation_sets(
    feature_sets: list[dict[str, Any]],
) -> list[ConstraintViolationSet]:
    return [build_constraint_violation_set(feature_set) for feature_set in feature_sets]


def build_constraint_violation_set(
    feature_set: dict[str, Any],
) -> ConstraintViolationSet:
    validate_candidate_feature_set(feature_set)
    candidate_violations = [
        build_candidate_constraint_violations(candidate_feature)
        for candidate_feature in feature_set["candidate_features"]
    ]

    return ConstraintViolationSet(
        constraint_violation_set_id=(
            f"{feature_set['candidate_feature_set_id']}:constraints"
        ),
        candidate_feature_set_id=str(feature_set["candidate_feature_set_id"]),
        episode_id=str(feature_set["episode_id"]),
        constraint_schema_version=CONSTRAINT_SCHEMA_VERSION,
        candidate_violations=candidate_violations,
    )


def build_candidate_constraint_violations(
    candidate_feature: dict[str, Any],
) -> CandidateConstraintViolations:
    violations = [
        penalty_violation(
            candidate_feature,
            "NO-LEAKAGE-FLAG",
            bool(candidate_feature.get("leakage_flags")),
        ),
        penalty_violation(
            candidate_feature,
            "NO-OBSERVED-EDIT-TEXT",
            candidate_feature.get("uses_observed_edit_text") is True,
        ),
        penalty_violation(
            candidate_feature,
            "NO-UNSAFE-CANDIDATE",
            candidate_feature.get("no_oracle_safe") is not True,
        ),
        descriptive_violation(
            candidate_feature,
            "HOLD-CANDIDATE",
            candidate_feature.get("is_hold") is True,
        ),
        descriptive_violation(
            candidate_feature,
            "LOCAL-EDIT-CANDIDATE",
            candidate_feature.get("is_local_edit") is True,
        ),
        descriptive_violation(
            candidate_feature,
            "GRAMMAR-PLACEHOLDER-CANDIDATE",
            candidate_feature.get("is_grammar_placeholder") is True,
        ),
        descriptive_violation(
            candidate_feature,
            "PLACEHOLDER-CANDIDATE",
            candidate_feature.get("is_placeholder") is True,
        ),
        descriptive_violation(
            candidate_feature,
            "HAS-GENERATION-RULE",
            candidate_feature.get("has_generation_rule") is True,
        ),
        descriptive_violation(
            candidate_feature,
            "HAS-ACTION-FAMILY",
            candidate_feature.get("has_action_family") is True,
        ),
        descriptive_violation(
            candidate_feature,
            "CANDIDATE-METADATA-COMPLETE",
            candidate_feature.get("candidate_metadata_complete") is True,
        ),
        descriptive_violation(
            candidate_feature,
            "HOLD-FAMILY-CANDIDATE",
            candidate_feature.get("is_hold_candidate") is True,
        ),
        descriptive_violation(
            candidate_feature,
            "LOCAL-EDIT-FAMILY-CANDIDATE",
            candidate_feature.get("is_local_edit_family_candidate") is True,
        ),
        descriptive_violation(
            candidate_feature,
            "GRAMMAR-FAMILY-CANDIDATE",
            candidate_feature.get("is_grammar_family_candidate") is True,
        ),
        descriptive_violation(
            candidate_feature,
            "PLACEHOLDER-FAMILY-CANDIDATE",
            candidate_feature.get("is_placeholder_candidate") is True,
        ),
        descriptive_violation(
            candidate_feature,
            "SAFETY-RELEVANT-CANDIDATE",
            candidate_feature.get("is_safety_relevant_candidate") is True,
        ),
        descriptive_violation(
            candidate_feature,
            "CANDIDATE-FAMILY-BUCKET",
            bool(candidate_feature.get("candidate_family_bucket")),
        ),
    ]
    return CandidateConstraintViolations(
        candidate_id=str(candidate_feature["candidate_id"]),
        episode_id=str(candidate_feature["episode_id"]),
        action_type=str(candidate_feature["action_type"]),
        generation_rule=str(candidate_feature["generation_rule"]),
        action_family=str(candidate_feature["action_family"]),
        violations=violations,
    )


def penalty_violation(
    candidate_feature: dict[str, Any],
    constraint_id: str,
    condition: bool,
) -> ConstraintViolation:
    constraint = constraint_by_id(constraint_id)
    return ConstraintViolation(
        candidate_id=str(candidate_feature["candidate_id"]),
        episode_id=str(candidate_feature["episode_id"]),
        constraint_id=constraint.constraint_id,
        constraint_type=constraint.constraint_type,
        violation_count=1 if condition else 0,
        severity=constraint.severity,
        explanation=constraint.explanation,
        observed=condition,
    )


def descriptive_violation(
    candidate_feature: dict[str, Any],
    constraint_id: str,
    observed: bool,
) -> ConstraintViolation:
    constraint = constraint_by_id(constraint_id)
    return ConstraintViolation(
        candidate_id=str(candidate_feature["candidate_id"]),
        episode_id=str(candidate_feature["episode_id"]),
        constraint_id=constraint.constraint_id,
        constraint_type=constraint.constraint_type,
        violation_count=0,
        severity=constraint.severity,
        explanation=constraint.explanation,
        observed=observed,
    )


def constraint_by_id(constraint_id: str) -> Constraint:
    for constraint in CONSTRAINTS:
        if constraint.constraint_id == constraint_id:
            return constraint
    raise AssertionError(f"unknown constraint id: {constraint_id}")
