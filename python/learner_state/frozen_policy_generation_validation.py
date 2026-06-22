"""Safe synthetic frozen policy generation fixture validation.

This module validates metadata-only frozen policy generation fixtures. It does
not generate frozen policies, fit calibration, run selective prediction, train
an estimator, or compute metrics.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

GENERATION_REQUEST_FILE = "generation_request.json"
INPUT_FIXTURE_POINTER_FILE = "input_fixture_pointer.json"
EXPECTED_GENERATION_RESULT_FILE = "expected_generation_result.json"
EXPECTED_FROZEN_POLICY_VALIDATION_RESULT_FILE = (
    "expected_frozen_policy_validation_result.json"
)

VALIDATION_SCHEMA_VERSION = "learner_state_frozen_policy_generation_validation_v0.1"
GENERATION_REQUEST_SCHEMA_VERSION = "frozen_policy_generation_request_schema_v0_1"
INPUT_POINTER_SCHEMA_VERSION = "frozen_policy_generation_input_pointer_schema_v0_1"

REQUIRED_FILES = (
    GENERATION_REQUEST_FILE,
    INPUT_FIXTURE_POINTER_FILE,
    EXPECTED_GENERATION_RESULT_FILE,
    EXPECTED_FROZEN_POLICY_VALIDATION_RESULT_FILE,
)
REQUIRED_GENERATION_REQUEST_FIELDS = (
    "generation_request_schema_version",
    "request_id",
    "source_selective_prediction_fixture",
    "temperature_policy",
    "threshold_policy",
    "output_policy",
    "safety_policy",
    "synthetic_only",
    "content_suppressed",
)
REQUIRED_POINTER_FIELDS = (
    "pointer_schema_version",
    "source_selective_prediction_fixture",
    "expected_selective_prediction_validation_status",
    "validation_split_available",
    "learner_disjoint_expected",
    "label_in_prediction_row_expected",
    "test_tuning_expected",
    "content_suppressed",
    "no_raw_rows",
)
VALID_TEMPERATURE_METHODS = frozenset(
    {
        "none_identity",
        "validation_nll_minimization",
    }
)
VALID_TEMPERATURE_SOURCES = frozenset({"validation", "none_identity"})
VALID_THRESHOLD_METHODS = frozenset(
    {
        "fixed_confidence_threshold",
        "fixed_abstention_rate",
    }
)
SAFETY_POLICY_REQUIRED_TRUE_FIELDS = (
    "forbid_content_rows",
    "forbid_label_body",
    "forbid_metric_claims",
    "forbid_model_score_vector_dump",
    "forbid_policy_body_dump",
    "forbid_private_paths",
    "forbid_probability_vectors",
    "forbid_test_tuning",
    "require_learner_disjoint_split",
    "require_selective_prediction_validator_pass",
    "require_validation_split",
)
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
        "raw_row_carryover",
        "raw_rows_carryover_marker",
        "contains_raw_prediction_rows",
        "prediction_rows",
        "label_rows",
    }
)
LOGITS_DUMP_KEYS = frozenset(
    {
        "logits",
        "logits_dump",
        "logits_dump_carryover_marker",
        "contains_logits_dump",
        "contains_probability_dump",
        "probabilities",
        "probability_dump",
        "probabilities_dump",
    }
)
PERFORMANCE_CLAIM_KEYS = frozenset(
    {
        "final_test_performance_claim",
        "final_test_performance_claim_marker",
        "performance_claim",
        "metric_results",
        "metrics",
        "claims_accuracy",
        "claims_f1",
        "claims_ece",
        "claims_aurcc",
        "f1",
        "accuracy",
        "ece",
        "aurcc",
    }
)
FORBIDDEN_BODY_KEYS = frozenset(
    {
        "generated_frozen_policy",
        "generated_frozen_policy_body",
        "frozen_policy_artifact_body",
        "expected_action",
        "expected_action_body",
        "final_text",
        "observed_after_text",
        "gold_label",
        "teacher_correction",
        "human_correction",
        "raw_text",
        "raw_learner_text",
        "learner_text",
        "label_body",
        "split_body",
        "calibration_policy_body",
    }
)


@dataclass(frozen=True)
class FrozenPolicyGenerationFixture:
    generation_request: dict[str, Any]
    input_fixture_pointer: dict[str, Any]
    expected_generation_result: dict[str, Any]
    expected_frozen_policy_validation_result: dict[str, Any]


@dataclass(frozen=True)
class ExpectedFrozenPolicyGenerationResult:
    values: dict[str, Any]

    def to_safe_dict(self) -> dict[str, Any]:
        return dict(self.values)


@dataclass(frozen=True)
class FrozenPolicyGenerationValidationMismatch:
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
class FrozenPolicyGenerationValidationResult:
    validation_status: str
    reason_codes: list[str] = field(default_factory=list)
    failure_categories: list[str] = field(default_factory=list)
    failed_checks: list[dict[str, str]] = field(default_factory=list)
    checked_files_count: int = 0
    generation_request_schema_version: str | None = None
    pointer_schema_version: str | None = None
    generation_status: str = "pass"
    expected_output_status: str = "safe_metadata_expected"
    expected_frozen_policy_validation_status: str = "pass"
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
            "generation_request_schema_version": (
                self.generation_request_schema_version
            ),
            "pointer_schema_version": self.pointer_schema_version,
            "generation_status": self.generation_status,
            "expected_output_status": self.expected_output_status,
            "expected_frozen_policy_validation_status": (
                self.expected_frozen_policy_validation_status
            ),
            "content_suppressed": self.content_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
            "test_tuning_checked": self.test_tuning_checked,
            "forbidden_field_scan_checked": self.forbidden_field_scan_checked,
            "private_path_scan_checked": self.private_path_scan_checked,
            "performance_claim_scan_checked": self.performance_claim_scan_checked,
        }


class FrozenPolicyGenerationValidationFailure(Exception):
    """Safe validation failure without fixture or artifact bodies."""

    def __init__(
        self,
        reason_code: str,
        failure_category: str,
        *,
        stage: str = "generation_validation",
        check_name: str | None = None,
        file_role: str | None = None,
    ) -> None:
        self.reason_code = reason_code
        self.failure_category = failure_category
        self.stage = stage
        self.check_name = check_name or failure_category
        self.file_role = file_role or "input"
        super().__init__(
            "frozen_policy_generation_validation_failed:"
            f"stage={stage};category={failure_category};reason={reason_code}"
        )


def load_frozen_policy_generation_fixture(
    case_dir: str | Path,
) -> FrozenPolicyGenerationFixture:
    """Load a synthetic frozen policy generation fixture or fail safely."""

    path = Path(case_dir)
    _assert_path_safe(path)
    for file_name in REQUIRED_FILES:
        if not (path / file_name).exists():
            _fail("missing_generation_file", "file_presence", file_role=file_name)

    return FrozenPolicyGenerationFixture(
        generation_request=_load_json(path / GENERATION_REQUEST_FILE),
        input_fixture_pointer=_load_json(path / INPUT_FIXTURE_POINTER_FILE),
        expected_generation_result=_load_json(path / EXPECTED_GENERATION_RESULT_FILE),
        expected_frozen_policy_validation_result=_load_json(
            path / EXPECTED_FROZEN_POLICY_VALIDATION_RESULT_FILE
        ),
    )


def validate_frozen_policy_generation_fixture(
    case_dir: str | Path,
) -> FrozenPolicyGenerationValidationResult:
    """Validate a synthetic generation fixture and return safe metadata."""

    try:
        fixture = load_frozen_policy_generation_fixture(case_dir)
        _validate_loaded_fixture(fixture)
    except FrozenPolicyGenerationValidationFailure as exc:
        return _failure_result(exc, case_dir)

    return _success_result(fixture)


def load_expected_generation_result(
    case_dir: str | Path,
) -> ExpectedFrozenPolicyGenerationResult:
    data = _load_json(Path(case_dir) / EXPECTED_GENERATION_RESULT_FILE)
    return ExpectedFrozenPolicyGenerationResult(values=data)


def compare_frozen_policy_generation_result_to_expected(
    result: FrozenPolicyGenerationValidationResult,
    expected: ExpectedFrozenPolicyGenerationResult | dict[str, Any],
) -> list[FrozenPolicyGenerationValidationMismatch]:
    expected_values = (
        expected.to_safe_dict()
        if isinstance(expected, ExpectedFrozenPolicyGenerationResult)
        else dict(expected)
    )
    actual_failure_reason = result.reason_codes[0] if result.reason_codes else None
    actual_failure_category = (
        result.failure_categories[0] if result.failure_categories else None
    )
    actual_stage = (
        result.failed_checks[0].get("stage") if result.failed_checks else None
    )
    comparisons = {
        "generation_status": result.generation_status,
        "expected_failure_reason": actual_failure_reason,
        "expected_failure_category": actual_failure_category,
        "expected_stage": actual_stage,
        "expected_output_status": result.expected_output_status,
        "expected_frozen_policy_validation_status": (
            result.expected_frozen_policy_validation_status
        ),
        "content_suppressed": result.content_suppressed,
        "no_raw_rows": result.no_raw_rows,
        "synthetic_only": result.synthetic_only_checked,
        "no_oracle_checked": result.no_oracle_checked,
        "test_tuning_checked": result.test_tuning_checked,
    }

    mismatches: list[FrozenPolicyGenerationValidationMismatch] = []
    for key, actual_value in comparisons.items():
        if key in expected_values and expected_values[key] != actual_value:
            mismatches.append(
                FrozenPolicyGenerationValidationMismatch(
                    field_name=key,
                    expected_value=expected_values[key],
                    actual_value=actual_value,
                )
            )
    return mismatches


def discover_frozen_policy_generation_fixture_cases(root: str | Path) -> list[Path]:
    root_path = Path(root)
    return sorted(
        path.parent
        for path in root_path.rglob(EXPECTED_GENERATION_RESULT_FILE)
        if path.is_file()
    )


def _validate_loaded_fixture(fixture: FrozenPolicyGenerationFixture) -> None:
    request = fixture.generation_request
    pointer = fixture.input_fixture_pointer
    expected_generation = fixture.expected_generation_result
    expected_frozen = fixture.expected_frozen_policy_validation_result

    _validate_schema_versions(request, pointer)
    _validate_required_fields(request, pointer)
    _validate_pointer(pointer)
    _validate_temperature_policy(request["temperature_policy"])
    _validate_threshold_policy(request["threshold_policy"])
    _validate_output_policy(request["output_policy"])
    _validate_safety_policy(request, pointer)
    _scan_forbidden_fields(request, allow_manual_outputs=False)
    _scan_forbidden_fields(pointer, allow_manual_outputs=False)
    _validate_expected_frozen_policy_consistency(
        request,
        expected_generation,
        expected_frozen,
    )


def _validate_schema_versions(
    request: dict[str, Any],
    pointer: dict[str, Any],
) -> None:
    request_version = request.get("generation_request_schema_version")
    pointer_version = pointer.get("pointer_schema_version")
    if request_version is None:
        _fail(
            "missing_required_field",
            "schema_version",
            stage="schema_version",
            file_role=GENERATION_REQUEST_FILE,
        )
    if request_version != GENERATION_REQUEST_SCHEMA_VERSION:
        _fail(
            "unknown_generation_request_schema_version",
            "schema_version",
            stage="schema_version",
            file_role=GENERATION_REQUEST_FILE,
        )
    if pointer_version is None:
        _fail(
            "missing_required_field",
            "schema_version",
            stage="schema_version",
            file_role=INPUT_FIXTURE_POINTER_FILE,
        )
    if pointer_version != INPUT_POINTER_SCHEMA_VERSION:
        _fail(
            "unknown_pointer_schema_version",
            "schema_version",
            stage="schema_version",
            file_role=INPUT_FIXTURE_POINTER_FILE,
        )


def _validate_required_fields(
    request: dict[str, Any],
    pointer: dict[str, Any],
) -> None:
    for field_name in REQUIRED_GENERATION_REQUEST_FIELDS:
        if field_name not in request:
            _fail(
                "missing_required_field",
                "required_field",
                stage="required_fields",
                file_role=GENERATION_REQUEST_FILE,
            )
    for field_name in REQUIRED_POINTER_FIELDS:
        if field_name not in pointer:
            _fail(
                "missing_required_field",
                "required_field",
                stage="required_fields",
                file_role=INPUT_FIXTURE_POINTER_FILE,
            )


def _validate_pointer(pointer: dict[str, Any]) -> None:
    source = pointer.get("source_selective_prediction_fixture")
    if not isinstance(source, str) or _is_unsafe_path_value(source):
        _fail("unsafe_path", "path_safety", stage="input_fixture_pointer")
    if Path(source).is_absolute():
        _fail("unsafe_path", "path_safety", stage="input_fixture_pointer")
    expected_status = pointer.get("expected_selective_prediction_validation_status")
    if expected_status == "not_run":
        _fail(
            "unvalidated_input",
            "input_validation_gate",
            stage="selective_prediction_validation_gate",
        )
    if expected_status != "pass":
        _fail(
            "selective_prediction_validator_failure",
            "input_validation_gate",
            stage="selective_prediction_validation_gate",
        )
    if pointer.get("validation_split_available") is not True:
        _fail(
            "missing_validation_split",
            "split_policy",
            stage="input_fixture_pointer",
        )
    if pointer.get("learner_disjoint_expected") is not True:
        _fail(
            "selective_prediction_validator_failure",
            "input_validation_gate",
            stage="input_fixture_pointer",
        )
    if pointer.get("label_in_prediction_row_expected") is not False:
        _fail(
            "selective_prediction_validator_failure",
            "input_validation_gate",
            stage="selective_prediction_validation_gate",
        )
    if pointer.get("test_tuning_expected") is not False:
        _fail("test_threshold_tuning", "test_tuning_leakage", stage="threshold_policy")
    if pointer.get("content_suppressed") is not True:
        _fail("invalid_safety_policy", "safety_policy", stage="input_fixture_pointer")
    if pointer.get("no_raw_rows") is not True:
        _fail("invalid_safety_policy", "safety_policy", stage="input_fixture_pointer")


def _validate_temperature_policy(policy: Any) -> None:
    if not isinstance(policy, dict):
        _fail(
            "invalid_temperature_policy",
            "temperature_policy",
            stage="temperature_policy",
        )
    method = policy.get("selection_method")
    source = policy.get("source_split")
    if source == "test" or (isinstance(method, str) and "test" in method):
        _fail(
            "test_temperature_tuning",
            "test_tuning_leakage",
            stage="temperature_policy",
        )
    if method not in VALID_TEMPERATURE_METHODS:
        _fail(
            "invalid_temperature_policy",
            "temperature_policy",
            stage="temperature_policy",
        )
    if source not in VALID_TEMPERATURE_SOURCES:
        _fail(
            "invalid_temperature_policy",
            "temperature_policy",
            stage="temperature_policy",
        )
    if policy.get("metadata_only") is not True or policy.get("validation_only") is not True:
        _fail(
            "invalid_temperature_policy",
            "temperature_policy",
            stage="temperature_policy",
        )
    value = policy.get("temperature_value")
    if value is not None and not _is_finite_number(value):
        _fail(
            "invalid_temperature_policy",
            "temperature_policy",
            stage="temperature_policy",
        )


def _validate_threshold_policy(policy: Any) -> None:
    if not isinstance(policy, dict):
        _fail(
            "invalid_threshold_policy",
            "threshold_policy",
            stage="threshold_policy",
        )
    method = policy.get("selection_method")
    source = policy.get("source_split")
    if source == "test" or (isinstance(method, str) and "test" in method):
        _fail(
            "test_threshold_tuning",
            "test_tuning_leakage",
            stage="threshold_policy",
        )
    if method not in VALID_THRESHOLD_METHODS:
        _fail(
            "invalid_threshold_policy",
            "threshold_policy",
            stage="threshold_policy",
        )
    if source != "validation":
        _fail(
            "invalid_threshold_policy",
            "threshold_policy",
            stage="threshold_policy",
        )
    if policy.get("metadata_only") is not True or policy.get("validation_only") is not True:
        _fail(
            "invalid_threshold_policy",
            "threshold_policy",
            stage="threshold_policy",
        )
    for field_name in ("threshold_value", "allowed_abstention_rate"):
        if field_name in policy and not _is_unit_interval(policy[field_name]):
            _fail(
                "invalid_threshold_policy",
                "threshold_policy",
                stage="threshold_policy",
            )


def _validate_output_policy(policy: Any) -> None:
    if not isinstance(policy, dict):
        _fail("invalid_output_policy", "output_policy", stage="output_policy")
    for value in policy.values():
        if isinstance(value, str) and _is_unsafe_path_value(value):
            _fail("unsafe_path", "path_safety", stage="output_policy")
    if policy.get("output_path_policy") == "unsafe_private_marker":
        _fail("unsafe_path", "path_safety", stage="output_policy")
    if "generated_frozen_policy_body" in policy:
        _fail("forbidden_field", "forbidden_field", stage="output_policy")
    if policy.get("do_not_write_manual_run_outputs") is not True:
        _fail("invalid_output_policy", "output_policy", stage="output_policy")
    if policy.get("expected_artifact_filename") != "frozen_selective_prediction_policy.json":
        _fail("invalid_output_policy", "output_policy", stage="output_policy")
    if policy.get("require_frozen_policy_validator_pass") is not True:
        _fail("invalid_output_policy", "output_policy", stage="output_policy")


def _validate_safety_policy(
    request: dict[str, Any],
    pointer: dict[str, Any],
) -> None:
    if request.get("synthetic_only") is not True:
        _fail("invalid_safety_policy", "safety_policy", stage="safety_policy")
    if request.get("content_suppressed") is not True:
        _fail("invalid_safety_policy", "safety_policy", stage="safety_policy")
    policy = request.get("safety_policy")
    if not isinstance(policy, dict):
        _fail("invalid_safety_policy", "safety_policy", stage="safety_policy")
    for field_name in SAFETY_POLICY_REQUIRED_TRUE_FIELDS:
        if policy.get(field_name) is not True:
            _fail("invalid_safety_policy", "safety_policy", stage="safety_policy")
    if pointer.get("content_suppressed") is not True:
        _fail("invalid_safety_policy", "safety_policy", stage="safety_policy")
    if pointer.get("no_raw_rows") is not True:
        _fail("invalid_safety_policy", "safety_policy", stage="safety_policy")


def _scan_forbidden_fields(value: Any, *, allow_manual_outputs: bool) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            _scan_key(key, allow_manual_outputs=allow_manual_outputs)
            _scan_forbidden_fields(item, allow_manual_outputs=allow_manual_outputs)
    elif isinstance(value, list):
        for item in value:
            _scan_forbidden_fields(item, allow_manual_outputs=allow_manual_outputs)
    elif isinstance(value, str):
        if _is_unsafe_path_value(value) and not (
            allow_manual_outputs and "manual_outputs" in value
        ):
            _fail("unsafe_path", "path_safety", stage="pre_write_safety_scan")


def _scan_key(key: str, *, allow_manual_outputs: bool) -> None:
    normalized = key.lower()
    if normalized in RAW_ROW_KEYS:
        _fail(
            "raw_rows_in_generated_policy",
            "forbidden_body_carryover",
            stage="pre_write_safety_scan",
        )
    if normalized in LOGITS_DUMP_KEYS:
        _fail(
            "logits_dump_in_generated_policy",
            "forbidden_body_carryover",
            stage="pre_write_safety_scan",
        )
    if normalized in PERFORMANCE_CLAIM_KEYS:
        _fail(
            "performance_claim_in_generated_policy",
            "performance_claim",
            stage="pre_write_safety_scan",
        )
    if normalized in FORBIDDEN_BODY_KEYS:
        _fail("forbidden_field", "forbidden_field", stage="pre_write_safety_scan")


def _validate_expected_frozen_policy_consistency(
    request: dict[str, Any],
    expected_generation: dict[str, Any],
    expected_frozen: dict[str, Any],
) -> None:
    generation_status = expected_generation.get("generation_status")
    frozen_status = expected_frozen.get("validation_status")
    expected_frozen_status = expected_generation.get(
        "expected_frozen_policy_validation_status"
    )
    if generation_status == "pass":
        if expected_frozen_status != "pass" or frozen_status != "pass":
            _fail(
                "expected_result_mismatch",
                "expected_result_matching",
                stage="expected_frozen_policy_validation_result",
            )
        return
    if request.get("expected_generated_policy_status") == (
        "synthetic_policy_would_fail_frozen_policy_validator"
    ):
        _fail(
            "frozen_policy_validator_failure",
            "frozen_policy_validator_gate",
            stage="frozen_policy_validation",
        )
    if expected_frozen_status not in {"not_applicable", "skipped"}:
        _fail(
            "expected_result_mismatch",
            "expected_result_matching",
            stage="expected_frozen_policy_validation_result",
        )
    if frozen_status not in {"not_applicable", "skipped", "fail"}:
        _fail(
            "expected_result_mismatch",
            "expected_result_matching",
            stage="expected_frozen_policy_validation_result",
        )


def _success_result(
    fixture: FrozenPolicyGenerationFixture,
) -> FrozenPolicyGenerationValidationResult:
    return FrozenPolicyGenerationValidationResult(
        validation_status="pass",
        checked_files_count=len(REQUIRED_FILES),
        generation_request_schema_version=fixture.generation_request.get(
            "generation_request_schema_version"
        ),
        pointer_schema_version=fixture.input_fixture_pointer.get(
            "pointer_schema_version"
        ),
        generation_status="pass",
        expected_output_status="safe_metadata_expected",
        expected_frozen_policy_validation_status="pass",
    )


def _failure_result(
    exc: FrozenPolicyGenerationValidationFailure,
    case_dir: str | Path,
) -> FrozenPolicyGenerationValidationResult:
    generation_request_version: str | None = None
    pointer_version: str | None = None
    try:
        path = Path(case_dir)
        request_path = path / GENERATION_REQUEST_FILE
        pointer_path = path / INPUT_FIXTURE_POINTER_FILE
        if request_path.exists():
            request = _load_json(request_path)
            if isinstance(request, dict):
                generation_request_version = request.get(
                    "generation_request_schema_version"
                )
        if pointer_path.exists():
            pointer = _load_json(pointer_path)
            if isinstance(pointer, dict):
                pointer_version = pointer.get("pointer_schema_version")
    except FrozenPolicyGenerationValidationFailure:
        pass

    return FrozenPolicyGenerationValidationResult(
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
        checked_files_count=_checked_files_count(case_dir),
        generation_request_schema_version=generation_request_version,
        pointer_schema_version=pointer_version,
        generation_status="fail",
        expected_output_status="not_written",
        expected_frozen_policy_validation_status="not_applicable",
    )


def _checked_files_count(case_dir: str | Path) -> int:
    path = Path(case_dir)
    return sum(1 for file_name in REQUIRED_FILES if (path / file_name).exists())


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise FrozenPolicyGenerationValidationFailure(
            "malformed_generation_request",
            "json_parse",
            stage="json_parse",
            file_role=path.name,
        ) from exc
    if not isinstance(data, dict):
        _fail("malformed_generation_request", "json_parse", stage="json_parse")
    return data


def _assert_path_safe(path: Path) -> None:
    for part in path.parts:
        if part in UNSAFE_PATH_PARTS:
            _fail("unsafe_path", "path_safety", stage="path_safety")
    rendered = str(path)
    if any(marker in rendered for marker in ("/Users/", "/home/", "C:\\")):
        # Absolute local paths are not needed for fixture validation. Relative
        # workspace paths remain allowed.
        if path.is_absolute():
            _fail("unsafe_path", "path_safety", stage="path_safety")


def _is_unsafe_path_value(value: str) -> bool:
    if any(marker in value for marker in UNSAFE_PATH_MARKERS):
        return True
    return Path(value).is_absolute()


def _is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def _is_unit_interval(value: Any) -> bool:
    return _is_finite_number(value) and 0.0 <= float(value) <= 1.0


def _fail(
    reason_code: str,
    failure_category: str,
    *,
    stage: str = "generation_validation",
    check_name: str | None = None,
    file_role: str | None = None,
) -> None:
    raise FrozenPolicyGenerationValidationFailure(
        reason_code,
        failure_category,
        stage=stage,
        check_name=check_name,
        file_role=file_role,
    )
