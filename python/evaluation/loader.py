"""Load synthetic candidate scores and expected actions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from evaluation.models import FORBIDDEN_INPUT_FIELDS, ExpectedAction


class EvaluationInputError(ValueError):
    """Raised when evaluation input is malformed or unsafe."""


def load_score_sets(path: str | Path) -> list[dict[str, Any]]:
    input_path = Path(path)
    score_sets: list[dict[str, Any]] = []
    with input_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError as error:
                raise EvaluationInputError(
                    f"line {line_number}: malformed JSON: {error.msg}"
                ) from error
            if not isinstance(value, dict):
                raise EvaluationInputError(
                    f"line {line_number}: expected JSON object"
                )
            validate_score_set(value, line_number=line_number)
            score_sets.append(value)
    return score_sets


def load_expected_actions(path: str | Path) -> dict[str, ExpectedAction]:
    input_path = Path(path)
    expected_actions: dict[str, ExpectedAction] = {}
    with input_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError as error:
                raise EvaluationInputError(
                    f"line {line_number}: malformed JSON: {error.msg}"
                ) from error
            if not isinstance(value, dict):
                raise EvaluationInputError(
                    f"line {line_number}: expected JSON object"
                )
            expected = validate_expected_action(value, line_number=line_number)
            if expected.episode_id in expected_actions:
                raise EvaluationInputError(
                    f"line {line_number}: duplicate episode_id: {expected.episode_id}"
                )
            expected_actions[expected.episode_id] = expected
    return expected_actions


def validate_score_set(score_set: dict[str, Any], *, line_number: int) -> None:
    location = f"line {line_number}: "
    forbidden = sorted(find_forbidden_field_names(score_set))
    if forbidden:
        joined = ", ".join(forbidden)
        raise EvaluationInputError(
            f"{location}forbidden no-oracle field(s): {joined}"
        )
    required_fields = ("candidate_score_set_id", "episode_id", "candidate_scores")
    missing = [field for field in required_fields if field not in score_set]
    if missing:
        joined = ", ".join(missing)
        raise EvaluationInputError(f"{location}missing required field(s): {joined}")
    candidate_scores = score_set["candidate_scores"]
    if not isinstance(candidate_scores, list):
        raise EvaluationInputError(f"{location}candidate_scores must be a list")
    for index, candidate_score in enumerate(candidate_scores, start=1):
        if not isinstance(candidate_score, dict):
            raise EvaluationInputError(
                f"{location}candidate score {index} must be a JSON object"
            )
        validate_candidate_score(candidate_score, location=location, index=index)


def validate_candidate_score(
    candidate_score: dict[str, Any], *, location: str, index: int
) -> None:
    required_fields = (
        "candidate_id",
        "episode_id",
        "action_type",
        "weighted_score",
        "blocked",
        "rank",
        "no_oracle_safe",
    )
    missing = [field for field in required_fields if field not in candidate_score]
    if missing:
        joined = ", ".join(missing)
        raise EvaluationInputError(
            f"{location}candidate score {index} missing required field(s): {joined}"
        )


def validate_expected_action(
    expected: dict[str, Any], *, line_number: int
) -> ExpectedAction:
    location = f"line {line_number}: "
    forbidden = sorted(find_forbidden_field_names(expected))
    if forbidden:
        joined = ", ".join(forbidden)
        raise EvaluationInputError(
            f"{location}forbidden no-oracle field(s): {joined}"
        )
    required_fields = (
        "episode_id",
        "expected_action_type",
        "expected_source",
        "synthetic_only",
        "notes",
    )
    missing = [field for field in required_fields if field not in expected]
    if missing:
        joined = ", ".join(missing)
        raise EvaluationInputError(f"{location}missing required field(s): {joined}")
    if expected["synthetic_only"] is not True:
        raise EvaluationInputError(
            f"{location}expected action must be synthetic_only=true"
        )
    return ExpectedAction(
        episode_id=str(expected["episode_id"]),
        expected_action_type=str(expected["expected_action_type"]),
        expected_source=str(expected["expected_source"]),
        synthetic_only=True,
        notes=str(expected["notes"]),
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
