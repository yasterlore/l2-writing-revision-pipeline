"""Feature schema and leakage audit helpers for future OT scoring."""

from ot_scorer.feature_builder import build_feature_set, build_feature_sets
from ot_scorer.loader import CandidateFeatureError, load_candidate_sets
from ot_scorer.constraint_builder import (
    CONSTRAINTS,
    build_constraint_violation_set,
    build_constraint_violation_sets,
)
from ot_scorer.diagnostic_summary import (
    summarize_constraint_violation_file,
    summarize_constraint_violation_sets,
)
from ot_scorer.models import (
    CandidateFeature,
    CandidateFeatureSet,
    CandidateScore,
    CandidateScoreSet,
    Constraint,
    ConstraintContribution,
    ConstraintViolation,
    ConstraintViolationSet,
    ConstraintWeight,
)
from ot_scorer.scorer import (
    CONSTRAINT_WEIGHTS,
    SCORING_POLICY_VERSION,
    build_candidate_score_set,
    build_candidate_score_sets,
)
from ot_scorer.weight_config import (
    CONFIG_SCHEMA_VERSION,
    ConstraintWeightEntry,
    ForbiddenInformationPolicy,
    HandWeightConfig,
    NoOracleReviewInfo,
    WeightConfigError,
    load_hand_weight_config,
    parse_hand_weight_config,
)

__all__ = [
    "CONSTRAINTS",
    "CandidateFeature",
    "CandidateFeatureError",
    "CandidateFeatureSet",
    "CandidateScore",
    "CandidateScoreSet",
    "CONSTRAINT_WEIGHTS",
    "Constraint",
    "ConstraintContribution",
    "ConstraintViolation",
    "ConstraintViolationSet",
    "ConstraintWeight",
    "ConstraintWeightEntry",
    "CONFIG_SCHEMA_VERSION",
    "ForbiddenInformationPolicy",
    "HandWeightConfig",
    "NoOracleReviewInfo",
    "SCORING_POLICY_VERSION",
    "WeightConfigError",
    "build_candidate_score_set",
    "build_candidate_score_sets",
    "build_feature_set",
    "build_feature_sets",
    "build_constraint_violation_set",
    "build_constraint_violation_sets",
    "load_candidate_sets",
    "load_hand_weight_config",
    "parse_hand_weight_config",
    "summarize_constraint_violation_file",
    "summarize_constraint_violation_sets",
]
