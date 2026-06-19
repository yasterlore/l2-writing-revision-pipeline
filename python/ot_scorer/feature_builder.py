"""Build simple structural features from CandidateSet JSON objects."""

from __future__ import annotations

from typing import Any

from ot_scorer.leakage_audit import audit_candidate, audit_candidate_set
from ot_scorer.loader import validate_candidate_set
from ot_scorer.models import (
    GRAMMAR_PLACEHOLDER_ACTIONS,
    LOCAL_EDIT_ACTIONS,
    CandidateFeature,
    CandidateFeatureSet,
)

FEATURE_SCHEMA_VERSION = "candidate_feature_schema_v0_2"


def build_feature_sets(
    candidate_sets: list[dict[str, Any]],
) -> list[CandidateFeatureSet]:
    return [build_feature_set(candidate_set) for candidate_set in candidate_sets]


def build_feature_set(candidate_set: dict[str, Any]) -> CandidateFeatureSet:
    validate_candidate_set(candidate_set)
    set_flags = audit_candidate_set(candidate_set)
    candidate_features = [
        build_candidate_feature(candidate, set_flags=set_flags)
        for candidate in candidate_set["candidates"]
    ]
    all_flags = sorted(
        {
            *set_flags,
            *(
                flag
                for feature in candidate_features
                for flag in feature.leakage_flags
            ),
        }
    )

    return CandidateFeatureSet(
        candidate_feature_set_id=f"{candidate_set['candidate_set_id']}:features",
        candidate_set_id=str(candidate_set["candidate_set_id"]),
        episode_id=str(candidate_set["episode_id"]),
        no_oracle_safe=not all_flags,
        feature_schema_version=FEATURE_SCHEMA_VERSION,
        leakage_flags=all_flags,
        candidate_features=candidate_features,
    )


def build_candidate_feature(
    candidate: dict[str, Any], *, set_flags: list[str] | None = None
) -> CandidateFeature:
    flags = [*(set_flags or []), *audit_candidate(candidate)]
    action_type = str(candidate["action_type"])
    generation_rule = str(candidate["generation_rule"])
    family = action_family(action_type)
    description = candidate.get("description", "")
    feature_notes = candidate.get("feature_notes", [])
    if not isinstance(description, str):
        description = ""
    if not isinstance(feature_notes, list):
        feature_notes = []
    no_oracle_safe = candidate.get("no_oracle_safe") is True
    uses_observed_edit_text = candidate.get("uses_observed_edit_text") is True
    is_hold = action_type == "hold"
    is_local_edit = action_type in LOCAL_EDIT_ACTIONS
    is_grammar_placeholder = action_type in GRAMMAR_PLACEHOLDER_ACTIONS
    is_placeholder = action_type.endswith("_placeholder")
    candidate_metadata_complete = all(
        [
            bool(str(candidate["candidate_id"])),
            bool(str(candidate["episode_id"])),
            bool(action_type),
            bool(generation_rule),
            bool(family),
        ]
    )
    is_safety_relevant_candidate = (
        bool(flags) or uses_observed_edit_text or not no_oracle_safe
    )

    return CandidateFeature(
        candidate_id=str(candidate["candidate_id"]),
        episode_id=str(candidate["episode_id"]),
        action_type=action_type,
        generation_rule=generation_rule,
        no_oracle_safe=no_oracle_safe,
        uses_observed_edit_text=uses_observed_edit_text,
        action_family=family,
        candidate_metadata_complete=candidate_metadata_complete,
        has_generation_rule=bool(generation_rule),
        has_action_family=bool(family),
        is_safety_relevant_candidate=is_safety_relevant_candidate,
        is_placeholder_candidate=is_placeholder,
        is_grammar_family_candidate=family == "grammar_placeholder",
        is_local_edit_family_candidate=family == "local_edit",
        is_hold_candidate=family == "hold",
        candidate_family_bucket=family,
        is_placeholder=is_placeholder,
        is_hold=is_hold,
        is_local_edit=is_local_edit,
        is_grammar_placeholder=is_grammar_placeholder,
        candidate_description_length=len(description),
        feature_notes_count=len(feature_notes),
        leakage_flags=sorted(set(flags)),
    )


def action_family(action_type: str) -> str:
    if action_type == "hold":
        return "hold"
    if action_type in LOCAL_EDIT_ACTIONS:
        return "local_edit"
    if action_type in GRAMMAR_PLACEHOLDER_ACTIONS:
        return "grammar_placeholder"
    if action_type.endswith("_placeholder"):
        return "other_placeholder"
    return "other"
