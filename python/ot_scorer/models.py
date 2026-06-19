"""Dataclasses for candidate feature extraction."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

FORBIDDEN_INPUT_FIELDS: frozenset[str] = frozenset(
    {
        "final_text",
        "final_corrected_text",
        "observed_after_text",
        "local_context_after_observed",
        "gold_label",
        "teacher_correction",
        "human_correction",
        "post_hoc_annotation",
        "target_label",
        "answer_key",
        "corrected_sentence",
        "future_edit",
        "future_context",
        "inserted_text_observed",
        "deleted_text_observed",
    }
)

LOCAL_EDIT_ACTIONS: frozenset[str] = frozenset(
    {
        "local_insert_placeholder",
        "local_delete_placeholder",
        "local_replace_placeholder",
    }
)

GRAMMAR_PLACEHOLDER_ACTIONS: frozenset[str] = frozenset(
    {
        "article_fix_placeholder",
        "number_fix_placeholder",
        "sva_fix_placeholder",
        "tense_fix_placeholder",
        "preposition_fix_placeholder",
        "punctuation_fix_placeholder",
    }
)


@dataclass(frozen=True)
class CandidateFeature:
    candidate_id: str
    episode_id: str
    action_type: str
    generation_rule: str
    no_oracle_safe: bool
    uses_observed_edit_text: bool
    action_family: str
    is_placeholder: bool
    is_hold: bool
    is_local_edit: bool
    is_grammar_placeholder: bool
    candidate_description_length: int
    feature_notes_count: int
    leakage_flags: list[str]

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CandidateFeatureSet:
    candidate_feature_set_id: str
    candidate_set_id: str
    episode_id: str
    no_oracle_safe: bool
    feature_schema_version: str
    leakage_flags: list[str]
    candidate_features: list[CandidateFeature]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["candidate_features"] = [
            candidate_feature.to_json_dict()
            for candidate_feature in self.candidate_features
        ]
        return data


@dataclass(frozen=True)
class Constraint:
    constraint_id: str
    constraint_type: str
    severity: str
    explanation: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ConstraintViolation:
    candidate_id: str
    episode_id: str
    constraint_id: str
    constraint_type: str
    violation_count: int
    severity: str
    explanation: str
    observed: bool

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CandidateConstraintViolations:
    candidate_id: str
    episode_id: str
    action_type: str
    violations: list[ConstraintViolation]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["violations"] = [violation.to_json_dict() for violation in self.violations]
        return data


@dataclass(frozen=True)
class ConstraintViolationSet:
    constraint_violation_set_id: str
    candidate_feature_set_id: str
    episode_id: str
    constraint_schema_version: str
    candidate_violations: list[CandidateConstraintViolations]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["candidate_violations"] = [
            candidate_violation.to_json_dict()
            for candidate_violation in self.candidate_violations
        ]
        return data


@dataclass(frozen=True)
class ConstraintWeight:
    constraint_id: str
    weight: float
    is_blocking: bool
    rationale: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ConstraintContribution:
    constraint_id: str
    constraint_type: str
    violation_count: int
    weight: float
    contribution: float
    observed: bool

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CandidateScore:
    candidate_id: str
    episode_id: str
    weighted_score: float
    blocked: bool
    block_reasons: list[str]
    rank: int
    constraint_contributions: list[ConstraintContribution]
    scoring_policy_version: str
    no_oracle_safe: bool

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["constraint_contributions"] = [
            contribution.to_json_dict()
            for contribution in self.constraint_contributions
        ]
        return data


@dataclass(frozen=True)
class CandidateScoreSet:
    candidate_score_set_id: str
    constraint_violation_set_id: str
    episode_id: str
    scoring_policy_version: str
    candidate_scores: list[CandidateScore]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["candidate_scores"] = [
            candidate_score.to_json_dict() for candidate_score in self.candidate_scores
        ]
        return data
