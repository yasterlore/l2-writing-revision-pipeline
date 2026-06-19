"""Feature schema and leakage audit helpers for future OT scoring."""

from ot_scorer.feature_builder import build_feature_set, build_feature_sets
from ot_scorer.loader import CandidateFeatureError, load_candidate_sets
from ot_scorer.constraint_builder import (
    CONSTRAINTS,
    build_constraint_violation_set,
    build_constraint_violation_sets,
)
from ot_scorer.models import (
    CandidateFeature,
    CandidateFeatureSet,
    Constraint,
    ConstraintViolation,
    ConstraintViolationSet,
)

__all__ = [
    "CONSTRAINTS",
    "CandidateFeature",
    "CandidateFeatureError",
    "CandidateFeatureSet",
    "Constraint",
    "ConstraintViolation",
    "ConstraintViolationSet",
    "build_feature_set",
    "build_feature_sets",
    "build_constraint_violation_set",
    "build_constraint_violation_sets",
    "load_candidate_sets",
]
