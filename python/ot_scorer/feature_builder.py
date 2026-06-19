"""Build simple structural features from CandidateSet JSON objects."""

from __future__ import annotations

import string
from typing import Any

from ot_scorer.leakage_audit import audit_candidate, audit_candidate_set
from ot_scorer.loader import validate_candidate_set
from ot_scorer.models import (
    GRAMMAR_PLACEHOLDER_ACTIONS,
    LOCAL_EDIT_ACTIONS,
    CandidateFeature,
    CandidateFeatureSet,
)

FEATURE_SCHEMA_VERSION = "candidate_feature_schema_v0_3"


def build_feature_sets(
    candidate_sets: list[dict[str, Any]],
) -> list[CandidateFeatureSet]:
    return [build_feature_set(candidate_set) for candidate_set in candidate_sets]


def build_feature_set(candidate_set: dict[str, Any]) -> CandidateFeatureSet:
    validate_candidate_set(candidate_set)
    set_flags = audit_candidate_set(candidate_set)
    local_context_before = candidate_set.get("local_context_before", {})
    local_context_before_text = (
        local_context_before.get("text", "")
        if isinstance(local_context_before, dict)
        else ""
    )
    if not isinstance(local_context_before_text, str):
        local_context_before_text = ""
    cursor_pos_before = optional_int(candidate_set.get("cursor_pos_before"))
    doc_len_before = optional_int(candidate_set.get("doc_len_before"))
    selection_start_before = optional_int(candidate_set.get("selection_start_before"))
    selection_end_before = optional_int(candidate_set.get("selection_end_before"))
    candidate_features = [
        build_candidate_feature(
            candidate,
            set_flags=set_flags,
            local_context_before_text=local_context_before_text,
            cursor_pos_before=cursor_pos_before,
            doc_len_before=doc_len_before,
            selection_start_before=selection_start_before,
            selection_end_before=selection_end_before,
        )
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
    candidate: dict[str, Any],
    *,
    set_flags: list[str] | None = None,
    local_context_before_text: str = "",
    cursor_pos_before: int | None = None,
    doc_len_before: int | None = None,
    selection_start_before: int | None = None,
    selection_end_before: int | None = None,
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
    left_class = left_char_class(local_context_before_text)

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
        context_before_length_bucket=context_before_length_bucket(
            local_context_before_text
        ),
        cursor_at_document_start=cursor_pos_before == 0,
        cursor_at_document_end_before=(
            cursor_pos_before is not None
            and doc_len_before is not None
            and cursor_pos_before == doc_len_before
        ),
        selection_is_collapsed_before=selection_is_collapsed(
            selection_start_before, selection_end_before
        ),
        selection_span_length_bucket=selection_span_length_bucket(
            selection_start_before, selection_end_before
        ),
        left_context_ends_with_space=left_class == "whitespace",
        left_context_ends_with_punctuation=left_class == "punctuation",
        left_char_class=left_class,
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


def context_before_length_bucket(text: str) -> str:
    length = len(text)
    if length == 0:
        return "empty"
    if length <= 10:
        return "short"
    if length <= 30:
        return "medium"
    return "long"


def selection_span_length(start: int | None, end: int | None) -> int:
    if start is None or end is None or end < start:
        return 0
    return end - start


def selection_is_collapsed(start: int | None, end: int | None) -> bool:
    return start is not None and end is not None and start == end


def selection_span_length_bucket(start: int | None, end: int | None) -> str:
    length = selection_span_length(start, end)
    if length == 0:
        return "collapsed"
    if length <= 5:
        return "short"
    if length <= 20:
        return "medium"
    return "long"


def left_char_class(text: str) -> str:
    if not text:
        return "none"
    char = text[-1]
    if char.isspace():
        return "whitespace"
    if char in string.punctuation:
        return "punctuation"
    if char.isdigit():
        return "digit"
    if char.isalpha() and char.isupper():
        return "uppercase_letter"
    if char.isalpha() and char.islower():
        return "lowercase_letter"
    if char.isalpha():
        return "other_letter"
    return "other"


def optional_int(value: object) -> int | None:
    return value if isinstance(value, int) else None
