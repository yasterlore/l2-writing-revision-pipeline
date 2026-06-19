"""Hand-weight config schema models and strict validation helpers.

The config is intentionally not connected to scoring yet. Loading a config must
not change default weighted scoring behavior.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
from typing import Any

from ot_scorer.constraint_builder import CONSTRAINTS
from ot_scorer.models import FORBIDDEN_INPUT_FIELDS

CONFIG_SCHEMA_VERSION = "hand_weight_config_schema_v0_1"

KNOWN_CONSTRAINT_IDS: frozenset[str] = frozenset(
    constraint.constraint_id for constraint in CONSTRAINTS
)

FORBIDDEN_CONFIG_FIELD_NAMES: frozenset[str] = FORBIDDEN_INPUT_FIELDS | frozenset(
    {
        "expected_action",
        "expected_actions",
        "evaluation_result",
        "exact_match_result",
        "participant_id",
        "participant_identifier",
        "real_participant_data",
        "raw_text",
        "raw_local_context_before",
        "private_data_path",
    }
)

FORBIDDEN_PATH_PARTS: frozenset[str] = frozenset(
    {"manual_outputs", "private_data", "real_data", "participant_data"}
)

FORBIDDEN_PATH_SUFFIXES: tuple[str, ...] = (".real.jsonl", ".private.jsonl")

REQUIRED_TOP_LEVEL_FIELDS: tuple[str, ...] = (
    "config_schema_version",
    "config_name",
    "created_for",
    "default_behavior",
    "score_active_constraint_families",
    "constraint_weights",
    "blocking_constraints",
    "score_neutral_constraints",
    "rationale",
    "no_oracle_review",
    "synthetic_only_notice",
    "expected_action_usage_policy",
    "forbidden_information_policy",
)


class WeightConfigError(ValueError):
    """Raised when a hand-weight config is malformed or unsafe."""


@dataclass(frozen=True)
class NoOracleReviewInfo:
    review_status: str
    allowed_information: list[str]
    forbidden_information: list[str]

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ForbiddenInformationPolicy:
    forbidden_fields: list[str]
    forbidden_path_parts: list[str]
    raw_text_policy: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ConstraintWeightEntry:
    constraint_id: str
    constraint_family: str
    weight: float
    active: bool
    rationale: str
    no_oracle_safe_reason: str
    expected_effect: str
    risk_note: str
    tests_required: list[str]
    last_reviewed: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HandWeightConfig:
    config_schema_version: str
    config_name: str
    created_for: str
    default_behavior: str
    score_active_constraint_families: list[str]
    constraint_weights: list[ConstraintWeightEntry]
    blocking_constraints: list[str]
    score_neutral_constraints: list[str]
    rationale: str
    no_oracle_review: NoOracleReviewInfo
    synthetic_only_notice: str
    expected_action_usage_policy: str
    forbidden_information_policy: ForbiddenInformationPolicy

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["constraint_weights"] = [
            entry.to_json_dict() for entry in self.constraint_weights
        ]
        data["no_oracle_review"] = self.no_oracle_review.to_json_dict()
        data["forbidden_information_policy"] = (
            self.forbidden_information_policy.to_json_dict()
        )
        return data


def load_hand_weight_config(path: str | Path) -> HandWeightConfig:
    """Load and validate one hand-weight config JSON file."""

    config_path = Path(path)
    try:
        raw_text = config_path.read_text(encoding="utf-8")
    except OSError as error:
        raise WeightConfigError(f"could not read config: {config_path}") from error

    try:
        data = json.loads(raw_text, parse_constant=_reject_non_finite_json_constant)
    except json.JSONDecodeError as error:
        raise WeightConfigError(f"malformed config JSON: {error.msg}") from error
    except ValueError as error:
        raise WeightConfigError(str(error)) from error
    return parse_hand_weight_config(data)


def parse_hand_weight_config(data: Any) -> HandWeightConfig:
    """Validate a parsed config object and return typed dataclasses."""

    if not isinstance(data, dict):
        raise WeightConfigError("config root must be a JSON object")

    forbidden_fields = sorted(find_forbidden_config_field_names(data))
    if forbidden_fields:
        joined = ", ".join(forbidden_fields)
        raise WeightConfigError(f"forbidden config field(s): {joined}")

    unsafe_paths = sorted(find_forbidden_path_strings(data))
    if unsafe_paths:
        joined = ", ".join(unsafe_paths)
        raise WeightConfigError(f"forbidden path-like string(s): {joined}")

    missing = [field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in data]
    if missing:
        joined = ", ".join(missing)
        raise WeightConfigError(f"missing required config field(s): {joined}")

    config_schema_version = require_non_empty_string(
        data, "config_schema_version", location="config"
    )
    if config_schema_version != CONFIG_SCHEMA_VERSION:
        raise WeightConfigError(
            "unsupported config_schema_version: "
            f"{config_schema_version}; expected {CONFIG_SCHEMA_VERSION}"
        )

    constraint_weights = parse_constraint_weight_entries(data["constraint_weights"])
    validate_duplicate_constraints(constraint_weights)
    validate_known_constraints(constraint_weights)

    expected_action_usage_policy = require_non_empty_string(
        data, "expected_action_usage_policy", location="config"
    )
    validate_expected_action_usage_policy(expected_action_usage_policy)

    synthetic_only_notice = require_non_empty_string(
        data, "synthetic_only_notice", location="config"
    )
    validate_synthetic_only_notice(synthetic_only_notice)

    blocking_constraints = require_string_list(
        data, "blocking_constraints", location="config"
    )
    validate_named_constraint_list(blocking_constraints, "blocking_constraints")

    return HandWeightConfig(
        config_schema_version=config_schema_version,
        config_name=require_non_empty_string(data, "config_name", location="config"),
        created_for=require_non_empty_string(data, "created_for", location="config"),
        default_behavior=require_non_empty_string(
            data, "default_behavior", location="config"
        ),
        score_active_constraint_families=require_string_list(
            data, "score_active_constraint_families", location="config"
        ),
        constraint_weights=constraint_weights,
        blocking_constraints=blocking_constraints,
        score_neutral_constraints=require_string_list(
            data, "score_neutral_constraints", location="config"
        ),
        rationale=require_non_empty_string(data, "rationale", location="config"),
        no_oracle_review=parse_no_oracle_review(data["no_oracle_review"]),
        synthetic_only_notice=synthetic_only_notice,
        expected_action_usage_policy=expected_action_usage_policy,
        forbidden_information_policy=parse_forbidden_information_policy(
            data["forbidden_information_policy"]
        ),
    )


def parse_constraint_weight_entries(value: Any) -> list[ConstraintWeightEntry]:
    if not isinstance(value, list):
        raise WeightConfigError("constraint_weights must be a list")
    entries: list[ConstraintWeightEntry] = []
    for index, item in enumerate(value, start=1):
        location = f"constraint_weights[{index}]"
        if not isinstance(item, dict):
            raise WeightConfigError(f"{location} must be a JSON object")
        entry = ConstraintWeightEntry(
            constraint_id=require_non_empty_string(
                item, "constraint_id", location=location
            ),
            constraint_family=require_non_empty_string(
                item, "constraint_family", location=location
            ),
            weight=require_finite_weight(item, location=location),
            active=require_bool(item, "active", location=location),
            rationale=require_string(item, "rationale", location=location),
            no_oracle_safe_reason=require_string(
                item, "no_oracle_safe_reason", location=location
            ),
            expected_effect=require_non_empty_string(
                item, "expected_effect", location=location
            ),
            risk_note=require_non_empty_string(item, "risk_note", location=location),
            tests_required=require_string_list(
                item, "tests_required", location=location
            ),
            last_reviewed=require_non_empty_string(
                item, "last_reviewed", location=location
            ),
        )
        if entry.active:
            validate_active_entry(entry, location=location)
        entries.append(entry)
    return entries


def parse_no_oracle_review(value: Any) -> NoOracleReviewInfo:
    if not isinstance(value, dict):
        raise WeightConfigError("no_oracle_review must be a JSON object")
    return NoOracleReviewInfo(
        review_status=require_non_empty_string(
            value, "review_status", location="no_oracle_review"
        ),
        allowed_information=require_string_list(
            value, "allowed_information", location="no_oracle_review"
        ),
        forbidden_information=require_string_list(
            value, "forbidden_information", location="no_oracle_review"
        ),
    )


def parse_forbidden_information_policy(value: Any) -> ForbiddenInformationPolicy:
    if not isinstance(value, dict):
        raise WeightConfigError("forbidden_information_policy must be a JSON object")
    return ForbiddenInformationPolicy(
        forbidden_fields=require_string_list(
            value, "forbidden_fields", location="forbidden_information_policy"
        ),
        forbidden_path_parts=require_string_list(
            value, "forbidden_path_parts", location="forbidden_information_policy"
        ),
        raw_text_policy=require_non_empty_string(
            value, "raw_text_policy", location="forbidden_information_policy"
        ),
    )


def validate_active_entry(entry: ConstraintWeightEntry, *, location: str) -> None:
    if not entry.rationale.strip():
        raise WeightConfigError(f"{location} active weight requires rationale")
    if not entry.no_oracle_safe_reason.strip():
        raise WeightConfigError(
            f"{location} active weight requires no_oracle_safe_reason"
        )
    if not entry.tests_required:
        raise WeightConfigError(f"{location} active weight requires tests_required")


def validate_duplicate_constraints(entries: list[ConstraintWeightEntry]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for entry in entries:
        if entry.constraint_id in seen:
            duplicates.add(entry.constraint_id)
        seen.add(entry.constraint_id)
    if duplicates:
        joined = ", ".join(sorted(duplicates))
        raise WeightConfigError(f"duplicate constraint_id entries: {joined}")


def validate_known_constraints(entries: list[ConstraintWeightEntry]) -> None:
    unknown = sorted(
        entry.constraint_id
        for entry in entries
        if entry.constraint_id not in KNOWN_CONSTRAINT_IDS
    )
    if unknown:
        joined = ", ".join(unknown)
        raise WeightConfigError(f"unknown constraint_id entries: {joined}")


def validate_named_constraint_list(values: list[str], field_name: str) -> None:
    unknown = sorted(value for value in values if value not in KNOWN_CONSTRAINT_IDS)
    if unknown:
        joined = ", ".join(unknown)
        raise WeightConfigError(f"{field_name} contains unknown constraint(s): {joined}")


def validate_expected_action_usage_policy(value: str) -> None:
    lower = value.lower()
    if "not" not in lower and "never" not in lower and "must not" not in lower:
        raise WeightConfigError(
            "expected_action_usage_policy must state expected actions are not used"
        )
    if "scoring" not in lower:
        raise WeightConfigError(
            "expected_action_usage_policy must mention scoring prohibition"
        )
    if "weight" not in lower and "tuning" not in lower:
        raise WeightConfigError(
            "expected_action_usage_policy must mention weight or tuning prohibition"
        )
    unsafe_phrases = (
        "may be used for scoring",
        "can be used for scoring",
        "used for scoring feedback",
        "used to tune",
        "optimize weights",
    )
    for phrase in unsafe_phrases:
        if phrase in lower:
            raise WeightConfigError(
                "expected_action_usage_policy implies scoring or weight tuning"
            )


def validate_synthetic_only_notice(value: str) -> None:
    lower = value.lower()
    if "synthetic" not in lower:
        raise WeightConfigError("synthetic_only_notice must mention synthetic data")
    if "real participant" in lower and "no real participant" not in lower:
        raise WeightConfigError(
            "synthetic_only_notice must not permit real participant data"
        )


def require_string(data: dict[str, Any], field: str, *, location: str) -> str:
    if field not in data:
        raise WeightConfigError(f"{location} missing required field: {field}")
    value = data[field]
    if not isinstance(value, str):
        raise WeightConfigError(f"{location}.{field} must be a string")
    return value


def require_non_empty_string(
    data: dict[str, Any], field: str, *, location: str
) -> str:
    value = require_string(data, field, location=location)
    if not value.strip():
        raise WeightConfigError(f"{location}.{field} must be non-empty")
    return value


def require_string_list(data: dict[str, Any], field: str, *, location: str) -> list[str]:
    if field not in data:
        raise WeightConfigError(f"{location} missing required field: {field}")
    value = data[field]
    if not isinstance(value, list):
        raise WeightConfigError(f"{location}.{field} must be a list")
    if not all(isinstance(item, str) for item in value):
        raise WeightConfigError(f"{location}.{field} must contain only strings")
    return list(value)


def require_bool(data: dict[str, Any], field: str, *, location: str) -> bool:
    if field not in data:
        raise WeightConfigError(f"{location} missing required field: {field}")
    value = data[field]
    if not isinstance(value, bool):
        raise WeightConfigError(f"{location}.{field} must be a boolean")
    return value


def require_finite_weight(data: dict[str, Any], *, location: str) -> float:
    if "weight" not in data:
        raise WeightConfigError(f"{location} missing required field: weight")
    value = data["weight"]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise WeightConfigError(f"{location}.weight must be a finite number")
    weight = float(value)
    if not math.isfinite(weight):
        raise WeightConfigError(f"{location}.weight must be finite")
    return weight


def find_forbidden_config_field_names(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in FORBIDDEN_CONFIG_FIELD_NAMES:
                found.add(key)
            found.update(find_forbidden_config_field_names(nested))
    elif isinstance(value, list):
        for item in value:
            found.update(find_forbidden_config_field_names(item))
    return found


def find_forbidden_path_strings(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for nested in value.values():
            found.update(find_forbidden_path_strings(nested))
    elif isinstance(value, list):
        for item in value:
            found.update(find_forbidden_path_strings(item))
    elif isinstance(value, str) and string_contains_forbidden_path(value):
        found.add(value)
    return found


def string_contains_forbidden_path(value: str) -> bool:
    normalized = value.replace("\\", "/")
    if (
        "/" not in normalized
        and ":" not in normalized
        and not normalized.endswith(FORBIDDEN_PATH_SUFFIXES)
    ):
        return False
    if any(f"{part}/" in normalized for part in FORBIDDEN_PATH_PARTS):
        return True
    parts = [part for part in normalized.split("/") if part]
    if any(part in FORBIDDEN_PATH_PARTS for part in parts):
        return True
    if any(f"{part}:" in normalized for part in FORBIDDEN_PATH_PARTS):
        return True
    return normalized.endswith(FORBIDDEN_PATH_SUFFIXES)


def _reject_non_finite_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number is not allowed: {value}")
