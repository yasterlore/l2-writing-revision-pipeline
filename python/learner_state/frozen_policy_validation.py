"""Safe synthetic frozen selective prediction policy validation.

This module validates frozen selective prediction policy fixtures before any
future calibration scaffold, selective prediction evaluation, or estimator
work consumes them. It returns only safe metadata summaries; it does not fit
calibration parameters, tune thresholds, compute metrics, or train a model.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

FROZEN_POLICY_FILE = "frozen_selective_prediction_policy.json"
EXPECTED_FROZEN_POLICY_VALIDATION_RESULT_FILE = (
    "expected_frozen_policy_validation_result.json"
)

VALIDATION_SCHEMA_VERSION = "learner_state_frozen_policy_validation_v0.1"
FROZEN_POLICY_SCHEMA_VERSION = "frozen_selective_prediction_policy_schema_v0_1"

REQUIRED_FILES = (
    FROZEN_POLICY_FILE,
    EXPECTED_FROZEN_POLICY_VALIDATION_RESULT_FILE,
)
REQUIRED_POLICY_FIELDS = (
    "policy_schema_version",
    "policy_id",
    "source_fixture_id",
    "created_by_step",
    "synthetic_only",
    "content_suppressed",
    "no_raw_rows",
    "no_oracle_checked",
    "test_tuning_forbidden",
    "confidence_definition",
    "temperature",
    "temperature_source_split",
    "temperature_selection_method",
    "threshold",
    "threshold_source_split",
    "threshold_selection_method",
    "allowed_abstention_rate",
    "label_space_version",
    "split_policy_summary",
    "validation_input_summary",
    "safety_review",
)
TOP_LEVEL_REQUIRED_TRUE_FIELDS = (
    "synthetic_only",
    "no_oracle_checked",
    "test_tuning_forbidden",
    "no_raw_rows",
    "content_suppressed",
)
SAFETY_REVIEW_REQUIRED_TRUE_FIELDS = (
    "synthetic_only",
    "no_oracle_checked",
    "test_tuning_forbidden",
    "no_raw_rows",
    "content_suppressed",
    "no_private_paths",
    "prediction_label_separated",
    "expected_action_not_in_prediction_rows",
    "future_leakage_checked",
)
SPLIT_POLICY_EXPECTED_VALUES = {
    "learner_disjoint": True,
    "validation_used_for_tuning": True,
    "test_used_for_tuning": False,
    "label_dependent_split": False,
}
OPTIONAL_SPLIT_POLICY_EXPECTED_VALUES = {
    "test_evaluation_future_only": True,
}
VALIDATION_INPUT_COUNT_FIELDS = (
    "validation_prediction_count",
    "validation_label_count",
    "validation_participant_count",
)
ALLOWED_CONFIDENCE_DEFINITIONS = frozenset({"max_softmax_probability"})
UNSAFE_PATH_PARTS = frozenset(
    {
        "manual_outputs",
        "private_data",
        "real_data",
        "participant_data",
    }
)
UNSAFE_PATH_MARKERS = (
    "manual_outputs",
    "private_data",
    "real_data",
    "participant_data",
    "/Users/",
    "/home/",
    "C:\\",
)
RAW_ROW_KEYS = frozenset(
    {
        "raw_rows",
        "raw_prediction_rows",
        "raw_label_rows",
        "prediction_rows",
        "label_rows",
        "row_bodies",
        "raw_row_body",
    }
)
LOGITS_DUMP_KEYS = frozenset(
    {
        "logits",
        "logits_dump",
        "probabilities",
        "probability_dump",
        "probabilities_dump",
    }
)
FORBIDDEN_BODY_KEYS = frozenset(
    {
        "calibration_policy",
        "calibration_policy_body",
        "split_metadata",
        "split_metadata_body",
        "expected_action",
        "expected_action_body",
        "expected_action_family",
        "final_text",
        "observed_after_text",
        "gold_label",
        "teacher_correction",
        "human_correction",
        "raw_text",
        "raw_learner_text",
        "learner_text",
        "real_participant_id",
        "participant_id",
    }
)
PERFORMANCE_CLAIM_KEYS = frozenset(
    {
        "final_test_performance_claim",
        "performance_claim",
        "metric_results",
        "metrics",
        "f1",
        "macro_f1",
        "accuracy",
        "ece",
        "aurcc",
    }
)


@dataclass(frozen=True)
class FrozenPolicyFixture:
    policy: dict[str, Any]
    expected_validation_result: dict[str, Any]


@dataclass(frozen=True)
class ExpectedFrozenPolicyValidationResult:
    values: dict[str, Any]

    def to_safe_dict(self) -> dict[str, Any]:
        return dict(self.values)


@dataclass(frozen=True)
class FrozenPolicyValidationMismatch:
    field_name: str
    expected_value: Any
    actual_value: Any

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "field_name": self.field_name,
            "expected_value": self.expected_value,
            "actual_value": self.actual_value,
        }


@dataclass(frozen=True)
class FrozenPolicyValidationResult:
    validation_status: str
    reason_codes: list[str] = field(default_factory=list)
    failure_categories: list[str] = field(default_factory=list)
    failed_checks: list[dict[str, str]] = field(default_factory=list)
    checked_files_count: int = 0
    policy_schema_version: str | None = None
    policy_status: str = "safe"
    content_suppressed: bool = True
    no_raw_rows: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    test_tuning_checked: bool = True
    forbidden_field_scan_checked: bool = True
    private_path_scan_checked: bool = True
    performance_claim_scan_checked: bool = True
    validation_schema_version: str = VALIDATION_SCHEMA_VERSION

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "validation_schema_version": self.validation_schema_version,
            "validation_status": self.validation_status,
            "reason_codes": list(self.reason_codes),
            "failure_categories": list(self.failure_categories),
            "failed_checks": [dict(check) for check in self.failed_checks],
            "checked_files_count": self.checked_files_count,
            "policy_schema_version": self.policy_schema_version,
            "policy_status": self.policy_status,
            "content_suppressed": self.content_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
            "test_tuning_checked": self.test_tuning_checked,
            "forbidden_field_scan_checked": self.forbidden_field_scan_checked,
            "private_path_scan_checked": self.private_path_scan_checked,
            "performance_claim_scan_checked": self.performance_claim_scan_checked,
        }


class FrozenPolicyValidationFailure(Exception):
    """Safe validation failure without frozen policy artifact bodies."""

    def __init__(
        self,
        reason_code: str,
        failure_category: str,
        *,
        stage: str = "frozen_policy_validation",
        check_name: str | None = None,
        file_role: str | None = None,
    ) -> None:
        self.reason_code = reason_code
        self.failure_category = failure_category
        self.stage = stage
        self.check_name = check_name or failure_category
        self.file_role = file_role or "input"
        super().__init__(
            "frozen_policy_validation_failed:"
            f"stage={stage};category={failure_category};reason={reason_code}"
        )


def load_frozen_policy_fixture(case_dir: str | Path) -> FrozenPolicyFixture:
    """Load a synthetic frozen policy fixture or raise a safe failure."""

    path = Path(case_dir)
    _assert_path_safe(path)
    for file_name in REQUIRED_FILES:
        if not (path / file_name).exists():
            _fail("missing_input_file", "input_file_presence", file_role=file_name)

    policy = _load_json(path / FROZEN_POLICY_FILE, FROZEN_POLICY_FILE)
    expected = _load_json(
        path / EXPECTED_FROZEN_POLICY_VALIDATION_RESULT_FILE,
        EXPECTED_FROZEN_POLICY_VALIDATION_RESULT_FILE,
    )
    return FrozenPolicyFixture(
        policy=policy,
        expected_validation_result=expected,
    )


def validate_frozen_policy_fixture(
    case_dir: str | Path,
) -> FrozenPolicyValidationResult:
    """Validate a synthetic frozen policy fixture and return safe metadata."""

    try:
        fixture = load_frozen_policy_fixture(case_dir)
        _validate_loaded_fixture(fixture)
    except FrozenPolicyValidationFailure as exc:
        return _failure_result(exc, case_dir)

    return _success_result(fixture)


def load_expected_frozen_policy_validation_result(
    case_dir: str | Path,
) -> ExpectedFrozenPolicyValidationResult:
    data = _load_json(
        Path(case_dir) / EXPECTED_FROZEN_POLICY_VALIDATION_RESULT_FILE,
        EXPECTED_FROZEN_POLICY_VALIDATION_RESULT_FILE,
    )
    return ExpectedFrozenPolicyValidationResult(values=data)


def compare_frozen_policy_validation_result_to_expected(
    result: FrozenPolicyValidationResult,
    expected: ExpectedFrozenPolicyValidationResult | dict[str, Any],
) -> list[FrozenPolicyValidationMismatch]:
    expected_values = (
        expected.to_safe_dict()
        if isinstance(expected, ExpectedFrozenPolicyValidationResult)
        else dict(expected)
    )
    actual_failure_reason = result.reason_codes[0] if result.reason_codes else None
    actual_failure_category = (
        result.failure_categories[0] if result.failure_categories else None
    )
    actual_stage = (
        result.failed_checks[0].get("stage") if result.failed_checks else "complete"
    )
    comparisons = {
        "validation_status": result.validation_status,
        "expected_failure_reason": actual_failure_reason,
        "expected_failure_category": actual_failure_category,
        "expected_stage": actual_stage,
        "expected_policy_schema_version": result.policy_schema_version,
        "expected_policy_status": result.policy_status,
        "content_suppressed": result.content_suppressed,
        "no_raw_rows": result.no_raw_rows,
        "synthetic_only": result.synthetic_only_checked,
        "no_oracle_checked": result.no_oracle_checked,
        "test_tuning_checked": result.test_tuning_checked,
    }

    mismatches: list[FrozenPolicyValidationMismatch] = []
    for key, actual_value in comparisons.items():
        if key in expected_values and expected_values[key] != actual_value:
            mismatches.append(
                FrozenPolicyValidationMismatch(
                    field_name=key,
                    expected_value=expected_values[key],
                    actual_value=actual_value,
                )
            )
    return mismatches


def discover_frozen_policy_fixture_cases(root: str | Path) -> list[Path]:
    root_path = Path(root)
    return sorted(
        path.parent
        for path in root_path.rglob(EXPECTED_FROZEN_POLICY_VALIDATION_RESULT_FILE)
        if path.is_file()
    )


def _validate_loaded_fixture(fixture: FrozenPolicyFixture) -> None:
    policy = fixture.policy
    _validate_schema_version(policy)
    _validate_required_fields(policy)
    _scan_forbidden_fields(policy)
    _validate_safety_booleans(policy)
    _validate_temperature(policy)
    _validate_threshold(policy)
    _validate_abstention_rate(policy)
    _validate_confidence_definition(policy)
    _validate_split_policy_summary(policy)
    _validate_validation_input_summary(policy)


def _validate_schema_version(policy: dict[str, Any]) -> None:
    schema_version = policy.get("policy_schema_version")
    if schema_version is None:
        _fail(
            "missing_schema_version",
            "schema_version",
            stage="schema_version",
            file_role=FROZEN_POLICY_FILE,
        )
    if schema_version != FROZEN_POLICY_SCHEMA_VERSION:
        _fail(
            "unknown_schema_version",
            "schema_version",
            stage="schema_version",
            file_role=FROZEN_POLICY_FILE,
        )


def _validate_required_fields(policy: dict[str, Any]) -> None:
    for field_name in REQUIRED_POLICY_FIELDS:
        if field_name not in policy:
            _fail(
                "missing_required_field",
                "schema_required_field",
                stage="required_fields",
                file_role=FROZEN_POLICY_FILE,
            )


def _scan_forbidden_fields(policy: dict[str, Any]) -> None:
    keys = _nested_keys(policy)
    if keys & RAW_ROW_KEYS:
        _fail(
            "raw_rows_in_policy",
            "forbidden_body",
            stage="forbidden_field_scan",
            file_role=FROZEN_POLICY_FILE,
        )
    if keys & LOGITS_DUMP_KEYS:
        _fail(
            "logits_dump_in_policy",
            "forbidden_body",
            stage="forbidden_field_scan",
            file_role=FROZEN_POLICY_FILE,
        )
    if _contains_unsafe_path_value(policy):
        _fail(
            "unsafe_path",
            "path_safety",
            stage="path_safety",
            file_role=FROZEN_POLICY_FILE,
        )
    if keys & PERFORMANCE_CLAIM_KEYS:
        _fail(
            "performance_claim_in_policy",
            "performance_claim",
            stage="performance_claim_scan",
            file_role=FROZEN_POLICY_FILE,
        )
    if keys & FORBIDDEN_BODY_KEYS:
        _fail(
            "forbidden_field",
            "forbidden_body",
            stage="forbidden_field_scan",
            file_role=FROZEN_POLICY_FILE,
        )


def _validate_safety_booleans(policy: dict[str, Any]) -> None:
    for field_name in TOP_LEVEL_REQUIRED_TRUE_FIELDS:
        if policy.get(field_name) is not True:
            _fail(
                "invalid_safety_review",
                "safety_review",
                stage="safety_review",
                file_role=FROZEN_POLICY_FILE,
            )

    safety_review = policy.get("safety_review")
    if not isinstance(safety_review, dict):
        _fail(
            "invalid_safety_review",
            "safety_review",
            stage="safety_review",
            file_role=FROZEN_POLICY_FILE,
        )
    for field_name in SAFETY_REVIEW_REQUIRED_TRUE_FIELDS:
        if safety_review.get(field_name) is not True:
            _fail(
                "invalid_safety_review",
                "safety_review",
                stage="safety_review",
                file_role=FROZEN_POLICY_FILE,
            )
    if safety_review.get("performance_claims_absent") is False:
        _fail(
            "performance_claim_in_policy",
            "performance_claim",
            stage="performance_claim_scan",
            file_role=FROZEN_POLICY_FILE,
        )


def _validate_temperature(policy: dict[str, Any]) -> None:
    temperature_source = policy.get("temperature_source_split")
    temperature_method = policy.get("temperature_selection_method")
    if _mentions_test([temperature_source, temperature_method]):
        _fail(
            "test_temperature_tuning",
            "test_tuning_leakage",
            stage="temperature_provenance",
            file_role=FROZEN_POLICY_FILE,
        )
    if temperature_source not in {"validation", "none_identity"}:
        _fail(
            "invalid_temperature",
            "numeric_range",
            stage="temperature_validation",
            file_role=FROZEN_POLICY_FILE,
        )
    temperature = policy.get("temperature")
    if not _is_finite_number(temperature) or float(temperature) <= 0.0:
        _fail(
            "invalid_temperature",
            "numeric_range",
            stage="temperature_validation",
            file_role=FROZEN_POLICY_FILE,
        )
    if temperature_source == "none_identity" and temperature_method != "none_identity":
        _fail(
            "invalid_temperature",
            "numeric_range",
            stage="temperature_validation",
            file_role=FROZEN_POLICY_FILE,
        )


def _validate_threshold(policy: dict[str, Any]) -> None:
    threshold_source = policy.get("threshold_source_split")
    threshold_method = policy.get("threshold_selection_method")
    if _mentions_test([threshold_source, threshold_method]):
        _fail(
            "test_threshold_tuning",
            "test_tuning_leakage",
            stage="threshold_provenance",
            file_role=FROZEN_POLICY_FILE,
        )
    if threshold_source != "validation":
        _fail(
            "invalid_threshold",
            "numeric_range",
            stage="threshold_validation",
            file_role=FROZEN_POLICY_FILE,
        )
    threshold = policy.get("threshold")
    if not _is_finite_number(threshold) or not 0.0 <= float(threshold) <= 1.0:
        _fail(
            "invalid_threshold",
            "numeric_range",
            stage="threshold_validation",
            file_role=FROZEN_POLICY_FILE,
        )


def _validate_abstention_rate(policy: dict[str, Any]) -> None:
    abstention_rate = policy.get("allowed_abstention_rate")
    if not _is_finite_number(abstention_rate) or not (
        0.0 <= float(abstention_rate) <= 1.0
    ):
        _fail(
            "invalid_abstention_rate",
            "numeric_range",
            stage="abstention_rate_validation",
            file_role=FROZEN_POLICY_FILE,
        )


def _validate_confidence_definition(policy: dict[str, Any]) -> None:
    if policy.get("confidence_definition") not in ALLOWED_CONFIDENCE_DEFINITIONS:
        _fail(
            "invalid_confidence_definition",
            "confidence_definition",
            stage="confidence_definition",
            file_role=FROZEN_POLICY_FILE,
        )


def _validate_split_policy_summary(policy: dict[str, Any]) -> None:
    split_policy = policy.get("split_policy_summary")
    if not isinstance(split_policy, dict):
        _fail(
            "invalid_split_policy",
            "split_policy",
            stage="split_policy",
            file_role=FROZEN_POLICY_FILE,
        )
    for key, expected_value in SPLIT_POLICY_EXPECTED_VALUES.items():
        if split_policy.get(key) is not expected_value:
            _fail(
                "invalid_split_policy",
                "split_policy",
                stage="split_policy",
                file_role=FROZEN_POLICY_FILE,
            )
    for key, expected_value in OPTIONAL_SPLIT_POLICY_EXPECTED_VALUES.items():
        if key in split_policy and split_policy.get(key) is not expected_value:
            _fail(
                "invalid_split_policy",
                "split_policy",
                stage="split_policy",
                file_role=FROZEN_POLICY_FILE,
            )


def _validate_validation_input_summary(policy: dict[str, Any]) -> None:
    summary = policy.get("validation_input_summary")
    if not isinstance(summary, dict):
        _fail(
            "policy_count_mismatch",
            "validation_input_summary",
            stage="validation_input_summary",
            file_role=FROZEN_POLICY_FILE,
        )
    for key in VALIDATION_INPUT_COUNT_FIELDS:
        if key in summary and not _is_non_negative_int(summary.get(key)):
            _fail(
                "policy_count_mismatch",
                "validation_input_summary",
                stage="validation_input_summary",
                file_role=FROZEN_POLICY_FILE,
            )
    # Reuse the recursive scan on the summary to keep this boundary explicit.
    _scan_forbidden_fields(summary)


def _failure_result(
    exc: FrozenPolicyValidationFailure,
    case_dir: str | Path,
) -> FrozenPolicyValidationResult:
    case_path = Path(case_dir)
    return FrozenPolicyValidationResult(
        validation_status="fail",
        reason_codes=[exc.reason_code],
        failure_categories=[exc.failure_category],
        failed_checks=[
            {
                "stage": exc.stage,
                "check_name": exc.check_name,
                "file_role": exc.file_role,
                "reason_code": exc.reason_code,
                "failure_category": exc.failure_category,
            }
        ],
        checked_files_count=_checked_files_count(case_path),
        policy_schema_version=_safe_policy_schema_version(case_path),
        policy_status=_policy_status_for_reason(exc.reason_code),
    )


def _success_result(fixture: FrozenPolicyFixture) -> FrozenPolicyValidationResult:
    return FrozenPolicyValidationResult(
        validation_status="pass",
        checked_files_count=len(REQUIRED_FILES),
        policy_schema_version=fixture.policy.get("policy_schema_version"),
        policy_status="safe",
    )


def _policy_status_for_reason(reason_code: str) -> str:
    return "unsafe_path" if reason_code == "unsafe_path" else f"unsafe_{reason_code}"


def _checked_files_count(case_dir: Path) -> int:
    if set(case_dir.parts) & UNSAFE_PATH_PARTS:
        return 0
    return sum(1 for file_name in REQUIRED_FILES if (case_dir / file_name).exists())


def _safe_policy_schema_version(case_dir: Path) -> str | None:
    if set(case_dir.parts) & UNSAFE_PATH_PARTS:
        return None
    policy_path = case_dir / FROZEN_POLICY_FILE
    if not policy_path.exists():
        return None
    try:
        policy = _load_json(policy_path, FROZEN_POLICY_FILE)
    except FrozenPolicyValidationFailure:
        return None
    schema_version = policy.get("policy_schema_version")
    return schema_version if isinstance(schema_version, str) else None


def _load_json(path: Path, file_role: str) -> dict[str, Any]:
    if not path.exists():
        _fail("missing_input_file", "input_file_presence", file_role=file_role)
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise FrozenPolicyValidationFailure(
            "malformed_input",
            "json_parse",
            stage="json_parse",
            file_role=file_role,
        ) from exc
    if not isinstance(data, dict):
        _fail("malformed_input", "json_parse", stage="json_parse", file_role=file_role)
    return data


def _assert_path_safe(path: Path) -> None:
    if set(path.parts) & UNSAFE_PATH_PARTS:
        _fail("unsafe_path", "path_safety", stage="path_safety", file_role="input_path")


def _nested_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(key, str):
                keys.add(key)
            keys.update(_nested_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_nested_keys(child))
    return keys


def _contains_unsafe_path_value(value: Any) -> bool:
    if isinstance(value, dict):
        return any(_contains_unsafe_path_value(child) for child in value.values())
    if isinstance(value, list):
        return any(_contains_unsafe_path_value(child) for child in value)
    if isinstance(value, str):
        return any(marker in value for marker in UNSAFE_PATH_MARKERS)
    return False


def _mentions_test(values: list[Any]) -> bool:
    return any(isinstance(value, str) and "test" in value.lower() for value in values)


def _is_finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _is_non_negative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _fail(
    reason_code: str,
    failure_category: str,
    *,
    stage: str = "frozen_policy_validation",
    file_role: str | None = None,
) -> None:
    raise FrozenPolicyValidationFailure(
        reason_code,
        failure_category,
        stage=stage,
        file_role=file_role,
    )
