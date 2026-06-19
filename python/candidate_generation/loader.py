"""Loader and no-oracle input checks for safe-view JSONL."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from candidate_generation.models import FORBIDDEN_INPUT_FIELDS


class CandidateGenerationError(ValueError):
    """Raised when candidate generation input is malformed or no-oracle unsafe."""


def load_safe_episode_views(path: str | Path) -> list[dict[str, Any]]:
    """Load one NoOracleSafeEpisodeView object per JSONL line."""

    input_path = Path(path)
    episodes: list[dict[str, Any]] = []
    with input_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError as error:
                raise CandidateGenerationError(
                    f"line {line_number}: malformed JSON: {error.msg}"
                ) from error
            if not isinstance(value, dict):
                raise CandidateGenerationError(
                    f"line {line_number}: expected JSON object"
                )
            validate_safe_episode_view(value, line_number=line_number)
            episodes.append(value)
    return episodes


def validate_safe_episode_view(
    episode: dict[str, Any], *, line_number: int | None = None
) -> None:
    """Reject forbidden fields and require the minimal safe-view shape."""

    location = f"line {line_number}: " if line_number is not None else ""
    forbidden = sorted(find_forbidden_field_names(episode))
    if forbidden:
        joined = ", ".join(forbidden)
        raise CandidateGenerationError(
            f"{location}forbidden no-oracle field(s): {joined}"
        )

    required_fields = ("episode_id", "local_context_before", "no_oracle_safe_view")
    missing = [field for field in required_fields if field not in episode]
    if missing:
        joined = ", ".join(missing)
        raise CandidateGenerationError(f"{location}missing required field(s): {joined}")

    if episode.get("no_oracle_safe_view") is not True:
        raise CandidateGenerationError(
            f"{location}input must be marked no_oracle_safe_view=true"
        )

    context = episode["local_context_before"]
    if not isinstance(context, dict):
        raise CandidateGenerationError(
            f"{location}local_context_before must be a JSON object"
        )
    if "text" not in context:
        raise CandidateGenerationError(
            f"{location}local_context_before.text is required"
        )


def find_forbidden_field_names(value: Any) -> set[str]:
    """Find forbidden keys recursively without inspecting values semantically."""

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
