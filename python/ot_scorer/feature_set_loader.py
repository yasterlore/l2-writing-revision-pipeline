"""CandidateFeatureSet JSONL loader for constraint generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ot_scorer.loader import CandidateFeatureError, find_forbidden_field_names


def load_candidate_feature_sets(path: str | Path) -> list[dict[str, Any]]:
    input_path = Path(path)
    feature_sets: list[dict[str, Any]] = []
    with input_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError as error:
                raise CandidateFeatureError(
                    f"line {line_number}: malformed JSON: {error.msg}"
                ) from error
            if not isinstance(value, dict):
                raise CandidateFeatureError(
                    f"line {line_number}: expected JSON object"
                )
            validate_candidate_feature_set(value, line_number=line_number)
            feature_sets.append(value)
    return feature_sets


def validate_candidate_feature_set(
    feature_set: dict[str, Any], *, line_number: int | None = None
) -> None:
    location = f"line {line_number}: " if line_number is not None else ""
    forbidden = sorted(find_forbidden_field_names(feature_set))
    if forbidden:
        joined = ", ".join(forbidden)
        raise CandidateFeatureError(
            f"{location}forbidden no-oracle field(s): {joined}"
        )

    required_fields = (
        "candidate_feature_set_id",
        "candidate_set_id",
        "episode_id",
        "candidate_features",
    )
    missing = [field for field in required_fields if field not in feature_set]
    if missing:
        joined = ", ".join(missing)
        raise CandidateFeatureError(f"{location}missing required field(s): {joined}")

    candidate_features = feature_set["candidate_features"]
    if not isinstance(candidate_features, list):
        raise CandidateFeatureError(f"{location}candidate_features must be a list")
    for index, candidate_feature in enumerate(candidate_features, start=1):
        if not isinstance(candidate_feature, dict):
            raise CandidateFeatureError(
                f"{location}candidate feature {index} must be a JSON object"
            )
        validate_candidate_feature(candidate_feature, location=location, index=index)


def validate_candidate_feature(
    candidate_feature: dict[str, Any], *, location: str, index: int
) -> None:
    required_fields = (
        "candidate_id",
        "episode_id",
        "action_type",
        "no_oracle_safe",
        "uses_observed_edit_text",
        "candidate_metadata_complete",
        "has_generation_rule",
        "has_action_family",
        "is_safety_relevant_candidate",
        "is_placeholder_candidate",
        "is_grammar_family_candidate",
        "is_local_edit_family_candidate",
        "is_hold_candidate",
        "candidate_family_bucket",
        "context_before_length_bucket",
        "cursor_at_document_start",
        "cursor_at_document_end_before",
        "selection_is_collapsed_before",
        "selection_span_length_bucket",
        "left_context_ends_with_space",
        "left_context_ends_with_punctuation",
        "left_char_class",
        "is_hold",
        "is_local_edit",
        "is_grammar_placeholder",
        "is_placeholder",
        "leakage_flags",
    )
    missing = [field for field in required_fields if field not in candidate_feature]
    if missing:
        joined = ", ".join(missing)
        raise CandidateFeatureError(
            f"{location}candidate feature {index} missing required field(s): {joined}"
        )
    if not isinstance(candidate_feature["leakage_flags"], list):
        raise CandidateFeatureError(
            f"{location}candidate feature {index} leakage_flags must be a list"
        )
