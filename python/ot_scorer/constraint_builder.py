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

LINGUISTIC_PLACEHOLDER_CONSTRAINTS: dict[str, str] = {
    "article_fix_placeholder": "ARTICLE-PLACEHOLDER-CANDIDATE",
    "number_fix_placeholder": "NUMBER-PLACEHOLDER-CANDIDATE",
    "sva_fix_placeholder": "SVA-PLACEHOLDER-CANDIDATE",
    "tense_fix_placeholder": "TENSE-PLACEHOLDER-CANDIDATE",
    "preposition_fix_placeholder": "PREPOSITION-PLACEHOLDER-CANDIDATE",
    "punctuation_fix_placeholder": "PUNCTUATION-PLACEHOLDER-CANDIDATE",
}

LOCAL_CONTEXT_AVAILABLE_CONSTRAINTS: dict[str, str] = {
    "article_fix_placeholder": "ARTICLE-CANDIDATE-LOCAL-CONTEXT-AVAILABLE",
    "number_fix_placeholder": "NUMBER-CANDIDATE-LOCAL-CONTEXT-AVAILABLE",
    "sva_fix_placeholder": "SVA-CANDIDATE-LOCAL-CONTEXT-AVAILABLE",
    "tense_fix_placeholder": "TENSE-CANDIDATE-LOCAL-CONTEXT-AVAILABLE",
    "preposition_fix_placeholder": "PREPOSITION-CANDIDATE-LOCAL-CONTEXT-AVAILABLE",
}

CONTEXT_BEFORE_LENGTH_CONSTRAINTS: dict[str, str] = {
    "empty": "CONTEXT-BEFORE-EMPTY",
    "short": "CONTEXT-BEFORE-SHORT",
    "medium": "CONTEXT-BEFORE-MEDIUM",
    "long": "CONTEXT-BEFORE-LONG",
}

SELECTION_SPAN_CONSTRAINTS: dict[str, str] = {
    "short": "SELECTION-SPAN-SHORT",
    "medium": "SELECTION-SPAN-MEDIUM",
    "long": "SELECTION-SPAN-LONG",
}

LEFT_CHAR_CLASS_CONSTRAINTS: dict[str, str] = {
    "none": "LEFT-CHAR-CLASS-NONE",
    "whitespace": "LEFT-CHAR-CLASS-WHITESPACE",
    "punctuation": "LEFT-CHAR-CLASS-PUNCTUATION",
    "digit": "LEFT-CHAR-CLASS-DIGIT",
    "uppercase_letter": "LEFT-CHAR-CLASS-UPPERCASE-LETTER",
    "lowercase_letter": "LEFT-CHAR-CLASS-LOWERCASE-LETTER",
    "other_letter": "LEFT-CHAR-CLASS-OTHER-LETTER",
    "other": "LEFT-CHAR-CLASS-OTHER",
}

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
    Constraint(
        constraint_id="ARTICLE-PLACEHOLDER-CANDIDATE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the candidate is an article placeholder.",
    ),
    Constraint(
        constraint_id="NUMBER-PLACEHOLDER-CANDIDATE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the candidate is a number placeholder.",
    ),
    Constraint(
        constraint_id="SVA-PLACEHOLDER-CANDIDATE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the candidate is a subject-verb-agreement placeholder.",
    ),
    Constraint(
        constraint_id="TENSE-PLACEHOLDER-CANDIDATE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the candidate is a tense placeholder.",
    ),
    Constraint(
        constraint_id="PREPOSITION-PLACEHOLDER-CANDIDATE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the candidate is a preposition placeholder.",
    ),
    Constraint(
        constraint_id="PUNCTUATION-PLACEHOLDER-CANDIDATE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the candidate is a punctuation placeholder.",
    ),
    Constraint(
        constraint_id="CONTEXT-BEFORE-EMPTY",
        constraint_type="descriptive",
        severity="info",
        explanation="Records an empty pre-edit left context bucket.",
    ),
    Constraint(
        constraint_id="CONTEXT-BEFORE-SHORT",
        constraint_type="descriptive",
        severity="info",
        explanation="Records a short pre-edit left context bucket.",
    ),
    Constraint(
        constraint_id="CONTEXT-BEFORE-MEDIUM",
        constraint_type="descriptive",
        severity="info",
        explanation="Records a medium pre-edit left context bucket.",
    ),
    Constraint(
        constraint_id="CONTEXT-BEFORE-LONG",
        constraint_type="descriptive",
        severity="info",
        explanation="Records a long pre-edit left context bucket.",
    ),
    Constraint(
        constraint_id="CURSOR-AT-DOCUMENT-START",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the pre-edit cursor is at document start.",
    ),
    Constraint(
        constraint_id="CURSOR-AT-DOCUMENT-END-BEFORE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the pre-edit cursor is at document end.",
    ),
    Constraint(
        constraint_id="SELECTION-COLLAPSED-BEFORE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the pre-edit selection is collapsed.",
    ),
    Constraint(
        constraint_id="SELECTION-NONCOLLAPSED-BEFORE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the pre-edit selection is non-collapsed.",
    ),
    Constraint(
        constraint_id="SELECTION-SPAN-SHORT",
        constraint_type="descriptive",
        severity="info",
        explanation="Records a short pre-edit selection span bucket.",
    ),
    Constraint(
        constraint_id="SELECTION-SPAN-MEDIUM",
        constraint_type="descriptive",
        severity="info",
        explanation="Records a medium pre-edit selection span bucket.",
    ),
    Constraint(
        constraint_id="SELECTION-SPAN-LONG",
        constraint_type="descriptive",
        severity="info",
        explanation="Records a long pre-edit selection span bucket.",
    ),
    Constraint(
        constraint_id="LEFT-CONTEXT-ENDS-WITH-SPACE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the pre-edit left context ends with whitespace.",
    ),
    Constraint(
        constraint_id="LEFT-CONTEXT-ENDS-WITH-PUNCTUATION",
        constraint_type="descriptive",
        severity="info",
        explanation="Records whether the pre-edit left context ends with punctuation.",
    ),
    Constraint(
        constraint_id="LEFT-CHAR-CLASS-NONE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records that no pre-edit left character is available.",
    ),
    Constraint(
        constraint_id="LEFT-CHAR-CLASS-WHITESPACE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records a whitespace pre-edit left-character class.",
    ),
    Constraint(
        constraint_id="LEFT-CHAR-CLASS-PUNCTUATION",
        constraint_type="descriptive",
        severity="info",
        explanation="Records a punctuation pre-edit left-character class.",
    ),
    Constraint(
        constraint_id="LEFT-CHAR-CLASS-DIGIT",
        constraint_type="descriptive",
        severity="info",
        explanation="Records a digit pre-edit left-character class.",
    ),
    Constraint(
        constraint_id="LEFT-CHAR-CLASS-UPPERCASE-LETTER",
        constraint_type="descriptive",
        severity="info",
        explanation="Records an uppercase-letter pre-edit left-character class.",
    ),
    Constraint(
        constraint_id="LEFT-CHAR-CLASS-LOWERCASE-LETTER",
        constraint_type="descriptive",
        severity="info",
        explanation="Records a lowercase-letter pre-edit left-character class.",
    ),
    Constraint(
        constraint_id="LEFT-CHAR-CLASS-OTHER-LETTER",
        constraint_type="descriptive",
        severity="info",
        explanation="Records another-letter pre-edit left-character class.",
    ),
    Constraint(
        constraint_id="LEFT-CHAR-CLASS-OTHER",
        constraint_type="descriptive",
        severity="info",
        explanation="Records an other pre-edit left-character class.",
    ),
    Constraint(
        constraint_id="ARTICLE-CANDIDATE-LOCAL-CONTEXT-AVAILABLE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records that an article candidate has non-empty abstract pre-edit context.",
    ),
    Constraint(
        constraint_id="NUMBER-CANDIDATE-LOCAL-CONTEXT-AVAILABLE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records that a number candidate has non-empty abstract pre-edit context.",
    ),
    Constraint(
        constraint_id="SVA-CANDIDATE-LOCAL-CONTEXT-AVAILABLE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records that an SVA candidate has non-empty abstract pre-edit context.",
    ),
    Constraint(
        constraint_id="TENSE-CANDIDATE-LOCAL-CONTEXT-AVAILABLE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records that a tense candidate has non-empty abstract pre-edit context.",
    ),
    Constraint(
        constraint_id="PREPOSITION-CANDIDATE-LOCAL-CONTEXT-AVAILABLE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records that a preposition candidate has non-empty abstract pre-edit context.",
    ),
    Constraint(
        constraint_id="PUNCTUATION-CANDIDATE-LEFT-PUNCTUATION-AWARE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records that a punctuation candidate has an abstract left-punctuation flag.",
    ),
    Constraint(
        constraint_id="PUNCTUATION-CANDIDATE-LEFT-SPACE-AWARE",
        constraint_type="descriptive",
        severity="info",
        explanation="Records that a punctuation candidate has an abstract left-space flag.",
    ),
    Constraint(
        constraint_id="GRAMMAR-CANDIDATE-LEFT-CHAR-CLASS-RECORDED",
        constraint_type="descriptive",
        severity="info",
        explanation="Records that a grammar candidate has a non-empty abstract left-character class.",
    ),
    Constraint(
        constraint_id="GRAMMAR-CANDIDATE-SELECTION-CONTEXT-RECORDED",
        constraint_type="descriptive",
        severity="info",
        explanation="Records that a grammar candidate has abstract pre-edit selection context.",
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
        *linguistic_placeholder_violations(candidate_feature),
        *local_pattern_diagnostic_violations(candidate_feature),
        *non_leaky_linguistic_diagnostic_violations(candidate_feature),
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


def linguistic_placeholder_violations(
    candidate_feature: dict[str, Any],
) -> list[ConstraintViolation]:
    return [
        descriptive_violation(
            candidate_feature,
            constraint_id,
            is_linguistic_placeholder_candidate(candidate_feature, action_type),
        )
        for action_type, constraint_id in LINGUISTIC_PLACEHOLDER_CONSTRAINTS.items()
    ]


def is_linguistic_placeholder_candidate(
    candidate_feature: dict[str, Any], action_type: str
) -> bool:
    return (
        candidate_feature.get("action_type") == action_type
        and candidate_feature.get("action_family") == "grammar_placeholder"
        and candidate_feature.get("candidate_family_bucket") == "grammar_placeholder"
        and candidate_feature.get("is_grammar_family_candidate") is True
        and candidate_feature.get("is_placeholder_candidate") is True
    )


def local_pattern_diagnostic_violations(
    candidate_feature: dict[str, Any],
) -> list[ConstraintViolation]:
    return [
        *bucket_violations(
            candidate_feature,
            value=str(candidate_feature.get("context_before_length_bucket", "")),
            mapping=CONTEXT_BEFORE_LENGTH_CONSTRAINTS,
        ),
        descriptive_violation(
            candidate_feature,
            "CURSOR-AT-DOCUMENT-START",
            candidate_feature.get("cursor_at_document_start") is True,
        ),
        descriptive_violation(
            candidate_feature,
            "CURSOR-AT-DOCUMENT-END-BEFORE",
            candidate_feature.get("cursor_at_document_end_before") is True,
        ),
        descriptive_violation(
            candidate_feature,
            "SELECTION-COLLAPSED-BEFORE",
            candidate_feature.get("selection_is_collapsed_before") is True,
        ),
        descriptive_violation(
            candidate_feature,
            "SELECTION-NONCOLLAPSED-BEFORE",
            candidate_feature.get("selection_is_collapsed_before") is False,
        ),
        *bucket_violations(
            candidate_feature,
            value=str(candidate_feature.get("selection_span_length_bucket", "")),
            mapping=SELECTION_SPAN_CONSTRAINTS,
        ),
        descriptive_violation(
            candidate_feature,
            "LEFT-CONTEXT-ENDS-WITH-SPACE",
            candidate_feature.get("left_context_ends_with_space") is True,
        ),
        descriptive_violation(
            candidate_feature,
            "LEFT-CONTEXT-ENDS-WITH-PUNCTUATION",
            candidate_feature.get("left_context_ends_with_punctuation") is True,
        ),
        *bucket_violations(
            candidate_feature,
            value=str(candidate_feature.get("left_char_class", "")),
            mapping=LEFT_CHAR_CLASS_CONSTRAINTS,
        ),
    ]


def non_leaky_linguistic_diagnostic_violations(
    candidate_feature: dict[str, Any],
) -> list[ConstraintViolation]:
    return [
        *local_context_available_violations(candidate_feature),
        descriptive_violation(
            candidate_feature,
            "PUNCTUATION-CANDIDATE-LEFT-PUNCTUATION-AWARE",
            is_linguistic_placeholder_candidate(
                candidate_feature,
                "punctuation_fix_placeholder",
            )
            and candidate_feature.get("left_context_ends_with_punctuation") is True,
        ),
        descriptive_violation(
            candidate_feature,
            "PUNCTUATION-CANDIDATE-LEFT-SPACE-AWARE",
            is_linguistic_placeholder_candidate(
                candidate_feature,
                "punctuation_fix_placeholder",
            )
            and candidate_feature.get("left_context_ends_with_space") is True,
        ),
        descriptive_violation(
            candidate_feature,
            "GRAMMAR-CANDIDATE-LEFT-CHAR-CLASS-RECORDED",
            is_grammar_family_candidate(candidate_feature)
            and str(candidate_feature.get("left_char_class", "")) != "none",
        ),
        descriptive_violation(
            candidate_feature,
            "GRAMMAR-CANDIDATE-SELECTION-CONTEXT-RECORDED",
            is_grammar_family_candidate(candidate_feature)
            and isinstance(candidate_feature.get("selection_is_collapsed_before"), bool),
        ),
    ]


def local_context_available_violations(
    candidate_feature: dict[str, Any],
) -> list[ConstraintViolation]:
    has_context = str(candidate_feature.get("context_before_length_bucket", "")) != "empty"
    return [
        descriptive_violation(
            candidate_feature,
            constraint_id,
            is_linguistic_placeholder_candidate(candidate_feature, action_type)
            and has_context,
        )
        for action_type, constraint_id in LOCAL_CONTEXT_AVAILABLE_CONSTRAINTS.items()
    ]


def is_grammar_family_candidate(candidate_feature: dict[str, Any]) -> bool:
    return (
        candidate_feature.get("action_family") == "grammar_placeholder"
        and candidate_feature.get("candidate_family_bucket") == "grammar_placeholder"
        and candidate_feature.get("is_grammar_family_candidate") is True
    )


def bucket_violations(
    candidate_feature: dict[str, Any],
    *,
    value: str,
    mapping: dict[str, str],
) -> list[ConstraintViolation]:
    return [
        descriptive_violation(candidate_feature, constraint_id, value == bucket)
        for bucket, constraint_id in mapping.items()
    ]


def constraint_by_id(constraint_id: str) -> Constraint:
    for constraint in CONSTRAINTS:
        if constraint.constraint_id == constraint_id:
            return constraint
    raise AssertionError(f"unknown constraint id: {constraint_id}")
