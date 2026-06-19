"""CandidateSet JSONL loader with no-oracle leakage guards."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ot_scorer.models import FORBIDDEN_INPUT_FIELDS


class CandidateFeatureError(ValueError):
    """Raised when candidate feature input is malformed or unsafe."""


def load_candidate_sets(path: str | Path) -> list[dict[str, Any]]:
    input_path = Path(path)
    candidate_sets: list[dict[str, Any]] = []
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
            validate_candidate_set(value, line_number=line_number)
            candidate_sets.append(value)
    return candidate_sets


def validate_candidate_set(
    candidate_set: dict[str, Any], *, line_number: int | None = None
) -> None:
    location = f"line {line_number}: " if line_number is not None else ""
    forbidden = sorted(find_forbidden_field_names(candidate_set))
    if forbidden:
        joined = ", ".join(forbidden)
        raise CandidateFeatureError(
            f"{location}forbidden no-oracle field(s): {joined}"
        )

    required_fields = ("candidate_set_id", "episode_id", "candidates")
    missing = [field for field in required_fields if field not in candidate_set]
    if missing:
        joined = ", ".join(missing)
        raise CandidateFeatureError(f"{location}missing required field(s): {joined}")

    candidates = candidate_set["candidates"]
    if not isinstance(candidates, list):
        raise CandidateFeatureError(f"{location}candidates must be a list")
    for index, candidate in enumerate(candidates, start=1):
        if not isinstance(candidate, dict):
            raise CandidateFeatureError(
                f"{location}candidate {index} must be a JSON object"
            )
        validate_candidate(candidate, location=location, index=index)


def validate_candidate(
    candidate: dict[str, Any], *, location: str, index: int
) -> None:
    required_fields = (
        "candidate_id",
        "episode_id",
        "action_type",
        "generation_rule",
        "no_oracle_safe",
        "uses_observed_edit_text",
    )
    missing = [field for field in required_fields if field not in candidate]
    if missing:
        joined = ", ".join(missing)
        raise CandidateFeatureError(
            f"{location}candidate {index} missing required field(s): {joined}"
        )


def find_forbidden_field_names(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in FORBIDDEN_INPUT_FIELDS:
                found.add(key)
            found.update(find_forbidden_field_names(nested))
    elif isinstance(value, list):
        for item in value:
            found.update(find_forbidden_field_names(item))
    return found
