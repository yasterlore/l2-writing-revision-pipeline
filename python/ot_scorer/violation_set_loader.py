"""ConstraintViolationSet JSONL loader for weighted scoring."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ot_scorer.loader import CandidateFeatureError, find_forbidden_field_names


def load_constraint_violation_sets(path: str | Path) -> list[dict[str, Any]]:
    input_path = Path(path)
    violation_sets: list[dict[str, Any]] = []
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
            validate_constraint_violation_set(value, line_number=line_number)
            violation_sets.append(value)
    return violation_sets


def validate_constraint_violation_set(
    violation_set: dict[str, Any], *, line_number: int | None = None
) -> None:
    location = f"line {line_number}: " if line_number is not None else ""
    forbidden = sorted(find_forbidden_field_names(violation_set))
    if forbidden:
        joined = ", ".join(forbidden)
        raise CandidateFeatureError(
            f"{location}forbidden no-oracle field(s): {joined}"
        )

    required_fields = (
        "constraint_violation_set_id",
        "episode_id",
        "candidate_violations",
    )
    missing = [field for field in required_fields if field not in violation_set]
    if missing:
        joined = ", ".join(missing)
        raise CandidateFeatureError(f"{location}missing required field(s): {joined}")

    candidate_violations = violation_set["candidate_violations"]
    if not isinstance(candidate_violations, list):
        raise CandidateFeatureError(f"{location}candidate_violations must be a list")
    for index, candidate_violation in enumerate(candidate_violations, start=1):
        if not isinstance(candidate_violation, dict):
            raise CandidateFeatureError(
                f"{location}candidate violation {index} must be a JSON object"
            )
        validate_candidate_constraint_violations(
            candidate_violation, location=location, index=index
        )


def validate_candidate_constraint_violations(
    candidate_violation: dict[str, Any], *, location: str, index: int
) -> None:
    required_fields = (
        "candidate_id",
        "episode_id",
        "action_type",
        "generation_rule",
        "action_family",
        "violations",
    )
    missing = [field for field in required_fields if field not in candidate_violation]
    if missing:
        joined = ", ".join(missing)
        raise CandidateFeatureError(
            f"{location}candidate violation {index} missing required field(s): {joined}"
        )

    violations = candidate_violation["violations"]
    if not isinstance(violations, list):
        raise CandidateFeatureError(
            f"{location}candidate violation {index} violations must be a list"
        )
    for violation_index, violation in enumerate(violations, start=1):
        if not isinstance(violation, dict):
            raise CandidateFeatureError(
                f"{location}candidate violation {index}.{violation_index} must be a JSON object"
            )
        validate_constraint_violation(
            violation,
            location=location,
            candidate_index=index,
            violation_index=violation_index,
        )


def validate_constraint_violation(
    violation: dict[str, Any], *, location: str, candidate_index: int, violation_index: int
) -> None:
    required_fields = (
        "constraint_id",
        "constraint_type",
        "violation_count",
        "severity",
        "observed",
    )
    missing = [field for field in required_fields if field not in violation]
    if missing:
        joined = ", ".join(missing)
        raise CandidateFeatureError(
            f"{location}candidate violation {candidate_index}.{violation_index} "
            f"missing required field(s): {joined}"
        )
