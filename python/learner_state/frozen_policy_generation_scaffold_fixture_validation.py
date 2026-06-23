"""Safe synthetic frozen policy generation scaffold fixture validation.

This module validates metadata-only scaffold fixtures. It does not implement a
scaffold runtime, generate frozen policies, fit calibration, run selective
prediction, train an estimator, or compute metrics.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

GENERATION_REQUEST_FILE = "generation_request.json"
INPUT_FIXTURE_POINTER_FILE = "input_fixture_pointer.json"
EXPECTED_SCAFFOLD_RESULT_FILE = "expected_scaffold_result.json"

REQUEST_SCHEMA_VERSION = "frozen_policy_generation_scaffold_request_schema_v0_1"
POINTER_SCHEMA_VERSION = "frozen_policy_generation_scaffold_pointer_schema_v0_1"
SCAFFOLD_RESULT_SCHEMA_VERSION = "frozen_policy_generation_scaffold_result_schema_v0_1"
VALIDATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_scaffold_fixture_validation_v0.1"
)

EXPECTED_TOTAL_CASES = 11
EXPECTED_VALID_CASES = 3
EXPECTED_INVALID_CASES = 8
EXPECTED_JSON_FILE_COUNT = EXPECTED_TOTAL_CASES * 3

VALID_CASE_NAMES = frozenset(
    {
        "minimal_fixed_abstention_rate_dry_run",
        "minimal_fixed_threshold_dry_run",
        "validation_nll_temperature_metadata_only_dry_run",
    }
)
EXPECTED_INVALID_REASONS = {
    "generated_artifact_body_leakage": "generated_artifact_body_leakage",
    "logits_dump_carryover": "logits_dump_carryover",
    "missing_validation_split": "missing_validation_split",
    "private_path_output": "private_path_output",
    "raw_rows_carryover": "raw_rows_carryover",
    "scoring_feedback_violation": "scoring_feedback_violation",
    "test_temperature_tuning": "test_temperature_tuning",
    "test_threshold_tuning": "test_threshold_tuning",
}

REQUIRED_FILES = (
    GENERATION_REQUEST_FILE,
    INPUT_FIXTURE_POINTER_FILE,
    EXPECTED_SCAFFOLD_RESULT_FILE,
)
REQUIRED_REQUEST_FIELDS = (
    "request_schema_version",
    "request_id",
    "generation_mode",
    "dry_run",
    "temperature_policy",
    "threshold_policy",
    "abstention_policy",
    "output_policy",
    "validation_split_source",
    "synthetic_only",
    "no_oracle",
    "no_body_dump",
    "no_raw_rows",
    "no_logits_dump",
    "metadata_only",
)
REQUIRED_POINTER_FIELDS = (
    "pointer_schema_version",
    "fixture_family",
    "fixture_case_label",
    "input_validation_status",
    "validation_split_available",
    "selective_prediction_validation_status",
    "frozen_policy_validation_status",
    "relative_fixture_reference",
    "synthetic_only",
    "no_oracle",
    "metadata_only",
)
REQUIRED_EXPECTED_RESULT_FIELDS = (
    "scaffold_schema_version",
    "scaffold_status",
    "reason_codes",
    "failed_checks",
    "generation_request_schema_version",
    "pointer_schema_version",
    "input_validation_status",
    "selective_prediction_validation_status",
    "frozen_policy_validation_status",
    "validation_split_available",
    "temperature_policy_status",
    "threshold_policy_status",
    "abstention_policy_status",
    "output_policy_status",
    "safety_status",
    "content_suppressed",
    "no_raw_rows",
    "no_logits_dump",
    "no_request_body",
    "no_generated_artifact_body",
    "artifact_body_suppressed",
    "synthetic_only_checked",
    "no_oracle_checked",
    "test_tuning_checked",
    "private_path_scan_checked",
    "performance_claim_scan_checked",
    "would_write_artifact",
    "artifact_write_mode",
    "metadata_only",
)
EXPECTED_RESULT_TRUE_FLAGS = (
    "content_suppressed",
    "no_raw_rows",
    "no_logits_dump",
    "no_request_body",
    "no_generated_artifact_body",
    "artifact_body_suppressed",
    "synthetic_only_checked",
    "no_oracle_checked",
    "test_tuning_checked",
    "private_path_scan_checked",
    "performance_claim_scan_checked",
    "metadata_only",
)

UNSAFE_PATH_MARKERS = (
    "/Users/",
    "/home/",
    "/var/folders/",
    "C:\\",
    "real_data/",
    "participant_data/",
    "private_data/",
    "manual_outputs/",
)
UNSAFE_CLI_PATH_PARTS = frozenset(
    {
        "real_data",
        "participant_data",
        "private_data",
        "manual_outputs",
    }
)
RAW_ROW_PAYLOAD_KEYS = frozenset(
    {
        "raw_rows",
        "raw_prediction_rows",
        "raw_label_rows",
        "prediction_rows",
        "label_rows",
        "row_body",
    }
)
LOGITS_PAYLOAD_KEYS = frozenset(
    {
        "logits",
        "logits_dump",
        "probabilities",
        "probability_dump",
        "probability_values",
    }
)
BODY_PAYLOAD_KEYS = frozenset(
    {
        "generated_artifact_body",
        "generated_frozen_policy_body",
        "frozen_policy_artifact_body",
        "policy_body",
        "raw_learner_text",
        "raw_text",
        "final_text",
        "observed_after_text",
        "gold_label",
        "label_body",
        "split_body",
        "calibration_policy_body",
        "teacher_correction",
        "human_correction",
        "expected_action_body",
    }
)
PERFORMANCE_PAYLOAD_KEYS = frozenset(
    {
        "accuracy",
        "f1",
        "ece",
        "aurcc",
        "metric_results",
        "metrics",
        "performance_metric_body",
        "performance_claim",
    }
)
RAW_LOG_PAYLOAD_KEYS = frozenset(
    {
        "github_actions_raw_log",
        "raw_github_log",
        "full_job_output",
        "copied_log_block",
    }
)
MARKER_KEYS = frozenset(
    {
        "expected_failure_marker",
        "unsafe_marker_label",
        "body_exposure_request",
        "fixture_case_label",
        "relative_fixture_reference",
        "reason_codes",
        "failed_checks",
    }
)


@dataclass(frozen=True)
class FrozenPolicyGenerationScaffoldFixtureCase:
    case_dir: Path
    case_category: str
    case_name: str
    generation_request: dict[str, Any]
    input_fixture_pointer: dict[str, Any]
    expected_scaffold_result: dict[str, Any]


@dataclass(frozen=True)
class ExpectedScaffoldResult:
    values: dict[str, Any]

    def to_safe_dict(self) -> dict[str, Any]:
        return dict(self.values)


@dataclass(frozen=True)
class ScaffoldFixtureValidationMismatch:
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
class ScaffoldFixtureSafetyScanResult:
    forbidden_field_scan_checked: bool = True
    private_path_scan_checked: bool = True
    raw_row_scan_checked: bool = True
    logits_scan_checked: bool = True
    artifact_body_scan_checked: bool = True
    performance_claim_scan_checked: bool = True
    raw_log_scan_checked: bool = True
    reason_codes: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "forbidden_field_scan_checked": self.forbidden_field_scan_checked,
            "private_path_scan_checked": self.private_path_scan_checked,
            "raw_row_scan_checked": self.raw_row_scan_checked,
            "logits_scan_checked": self.logits_scan_checked,
            "artifact_body_scan_checked": self.artifact_body_scan_checked,
            "performance_claim_scan_checked": self.performance_claim_scan_checked,
            "raw_log_scan_checked": self.raw_log_scan_checked,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
        }


@dataclass(frozen=True)
class FrozenPolicyGenerationScaffoldFixtureValidationResult:
    scaffold_status: str
    reason_codes: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)
    failure_categories: list[str] = field(default_factory=list)
    checked_files_count: int = 0
    case_category: str | None = None
    case_name: str | None = None
    generation_request_schema_version: str | None = None
    pointer_schema_version: str | None = None
    scaffold_schema_version: str | None = None
    input_validation_status: str | None = None
    selective_prediction_validation_status: str | None = None
    frozen_policy_validation_status: str | None = None
    validation_split_available: bool | None = None
    temperature_policy_status: str | None = None
    threshold_policy_status: str | None = None
    abstention_policy_status: str | None = None
    output_policy_status: str | None = None
    safety_status: str | None = None
    content_suppressed: bool = True
    no_raw_rows: bool = True
    no_logits_dump: bool = True
    no_request_body: bool = True
    no_generated_artifact_body: bool = True
    artifact_body_suppressed: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    test_tuning_checked: bool = True
    private_path_scan_checked: bool = True
    performance_claim_scan_checked: bool = True
    would_write_artifact: bool = False
    artifact_write_mode: str = "dry_run_metadata_only"
    metadata_only: bool = True
    validation_schema_version: str = VALIDATION_SCHEMA_VERSION

    @property
    def validation_status(self) -> str:
        return self.scaffold_status

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "validation_schema_version": self.validation_schema_version,
            "scaffold_status": self.scaffold_status,
            "validation_status": self.validation_status,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "failure_categories": list(self.failure_categories),
            "checked_files_count": self.checked_files_count,
            "case_category": self.case_category,
            "case_name": self.case_name,
            "generation_request_schema_version": (
                self.generation_request_schema_version
            ),
            "pointer_schema_version": self.pointer_schema_version,
            "scaffold_schema_version": self.scaffold_schema_version,
            "input_validation_status": self.input_validation_status,
            "selective_prediction_validation_status": (
                self.selective_prediction_validation_status
            ),
            "frozen_policy_validation_status": self.frozen_policy_validation_status,
            "validation_split_available": self.validation_split_available,
            "temperature_policy_status": self.temperature_policy_status,
            "threshold_policy_status": self.threshold_policy_status,
            "abstention_policy_status": self.abstention_policy_status,
            "output_policy_status": self.output_policy_status,
            "safety_status": self.safety_status,
            "content_suppressed": self.content_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "no_logits_dump": self.no_logits_dump,
            "no_request_body": self.no_request_body,
            "no_generated_artifact_body": self.no_generated_artifact_body,
            "artifact_body_suppressed": self.artifact_body_suppressed,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
            "test_tuning_checked": self.test_tuning_checked,
            "private_path_scan_checked": self.private_path_scan_checked,
            "performance_claim_scan_checked": self.performance_claim_scan_checked,
            "would_write_artifact": self.would_write_artifact,
            "artifact_write_mode": self.artifact_write_mode,
            "metadata_only": self.metadata_only,
        }


@dataclass(frozen=True)
class ScaffoldFixtureRootValidationSummary:
    mode: str = "fixture_root"
    total_cases: int = 0
    matched_cases: int = 0
    mismatched_cases: int = 0
    input_error_cases: int = 0
    reason_code_counts: dict[str, int] = field(default_factory=dict)
    content_suppressed: bool = True
    no_raw_rows: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    private_path_scan_checked: bool = True
    performance_claim_scan_checked: bool = True
    validation_schema_version: str = VALIDATION_SCHEMA_VERSION

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "validation_schema_version": self.validation_schema_version,
            "mode": self.mode,
            "total_cases": self.total_cases,
            "matched_cases": self.matched_cases,
            "mismatched_cases": self.mismatched_cases,
            "input_error_cases": self.input_error_cases,
            "reason_code_counts": dict(self.reason_code_counts),
            "content_suppressed": self.content_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
            "private_path_scan_checked": self.private_path_scan_checked,
            "performance_claim_scan_checked": self.performance_claim_scan_checked,
        }


def discover_frozen_policy_generation_scaffold_fixture_cases(
    root: Path,
) -> list[Path]:
    root = Path(root)
    cases: list[Path] = []
    for category in ("valid", "invalid"):
        category_dir = root / category
        if category_dir.exists():
            cases.extend(path for path in category_dir.iterdir() if path.is_dir())
    return sorted(cases)


def load_scaffold_fixture_case(
    case_dir: Path,
) -> FrozenPolicyGenerationScaffoldFixtureCase:
    case_dir = Path(case_dir)
    generation_request = _read_json(case_dir / GENERATION_REQUEST_FILE)
    input_fixture_pointer = _read_json(case_dir / INPUT_FIXTURE_POINTER_FILE)
    expected_scaffold_result = _read_json(case_dir / EXPECTED_SCAFFOLD_RESULT_FILE)
    return FrozenPolicyGenerationScaffoldFixtureCase(
        case_dir=case_dir,
        case_category=case_dir.parent.name,
        case_name=case_dir.name,
        generation_request=generation_request,
        input_fixture_pointer=input_fixture_pointer,
        expected_scaffold_result=expected_scaffold_result,
    )


def load_expected_scaffold_result(case_dir: Path) -> ExpectedScaffoldResult:
    return ExpectedScaffoldResult(
        values=_read_json(Path(case_dir) / EXPECTED_SCAFFOLD_RESULT_FILE)
    )


def validate_scaffold_fixture_case(
    case_dir: Path,
) -> FrozenPolicyGenerationScaffoldFixtureValidationResult:
    case_dir = Path(case_dir)
    try:
        _check_required_files(case_dir)
        fixture = load_scaffold_fixture_case(case_dir)
        errors = _validate_case_contract(fixture)
        if errors:
            return _input_error_result(fixture, errors)
        return _build_contract_result(fixture)
    except (OSError, json.JSONDecodeError, ValueError):
        return FrozenPolicyGenerationScaffoldFixtureValidationResult(
            scaffold_status="input_error",
            reason_codes=["malformed_fixture_file"],
            failed_checks=["json_parse"],
            failure_categories=["input_error"],
            checked_files_count=_count_existing_required_files(case_dir),
            case_category=case_dir.parent.name,
            case_name=case_dir.name,
        )


def compare_scaffold_result_to_expected(
    result: FrozenPolicyGenerationScaffoldFixtureValidationResult,
    expected: ExpectedScaffoldResult | dict[str, Any],
) -> list[ScaffoldFixtureValidationMismatch]:
    expected_values = expected.values if isinstance(expected, ExpectedScaffoldResult) else expected
    actual_values = result.to_safe_dict()
    field_map = {
        "scaffold_status": "scaffold_status",
        "reason_codes": "reason_codes",
        "failed_checks": "failed_checks",
        "generation_request_schema_version": "generation_request_schema_version",
        "pointer_schema_version": "pointer_schema_version",
        "input_validation_status": "input_validation_status",
        "selective_prediction_validation_status": (
            "selective_prediction_validation_status"
        ),
        "frozen_policy_validation_status": "frozen_policy_validation_status",
        "validation_split_available": "validation_split_available",
        "temperature_policy_status": "temperature_policy_status",
        "threshold_policy_status": "threshold_policy_status",
        "abstention_policy_status": "abstention_policy_status",
        "output_policy_status": "output_policy_status",
        "safety_status": "safety_status",
        "content_suppressed": "content_suppressed",
        "no_raw_rows": "no_raw_rows",
        "no_logits_dump": "no_logits_dump",
        "no_request_body": "no_request_body",
        "no_generated_artifact_body": "no_generated_artifact_body",
        "artifact_body_suppressed": "artifact_body_suppressed",
        "synthetic_only_checked": "synthetic_only_checked",
        "no_oracle_checked": "no_oracle_checked",
        "test_tuning_checked": "test_tuning_checked",
        "private_path_scan_checked": "private_path_scan_checked",
        "performance_claim_scan_checked": "performance_claim_scan_checked",
        "would_write_artifact": "would_write_artifact",
        "artifact_write_mode": "artifact_write_mode",
        "metadata_only": "metadata_only",
    }
    mismatches: list[ScaffoldFixtureValidationMismatch] = []
    for expected_field, actual_field in field_map.items():
        if expected_field in expected_values:
            expected_value = expected_values[expected_field]
            actual_value = actual_values.get(actual_field)
            if expected_value != actual_value:
                mismatches.append(
                    ScaffoldFixtureValidationMismatch(
                        field_name=expected_field,
                        expected_value=expected_value,
                        actual_value=actual_value,
                    )
                )
    return mismatches


def validate_scaffold_fixture_root(root: Path) -> ScaffoldFixtureRootValidationSummary:
    root = Path(root)
    root_errors = _validate_root_shape(root)
    if root_errors:
        return ScaffoldFixtureRootValidationSummary(
            total_cases=0,
            matched_cases=0,
            mismatched_cases=0,
            input_error_cases=1,
            reason_code_counts=dict(Counter(root_errors)),
        )

    matched_cases = 0
    mismatched_cases = 0
    input_error_cases = 0
    reason_counter: Counter[str] = Counter()

    for case_dir in discover_frozen_policy_generation_scaffold_fixture_cases(root):
        result = validate_scaffold_fixture_case(case_dir)
        reason_counter.update(result.reason_codes)
        if result.scaffold_status == "input_error":
            input_error_cases += 1
            continue
        expected = load_expected_scaffold_result(case_dir)
        mismatches = compare_scaffold_result_to_expected(result, expected)
        if mismatches:
            mismatched_cases += 1
        else:
            matched_cases += 1

    total_cases = matched_cases + mismatched_cases + input_error_cases
    return ScaffoldFixtureRootValidationSummary(
        total_cases=total_cases,
        matched_cases=matched_cases,
        mismatched_cases=mismatched_cases,
        input_error_cases=input_error_cases,
        reason_code_counts=dict(sorted(reason_counter.items())),
    )


def summarize_scaffold_fixture_validation_result(
    result: (
        FrozenPolicyGenerationScaffoldFixtureValidationResult
        | ScaffoldFixtureRootValidationSummary
        | ScaffoldFixtureSafetyScanResult
    ),
) -> dict[str, Any]:
    return result.to_safe_dict()


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        value = json.load(file)
    if not isinstance(value, dict):
        raise ValueError("expected_json_object")
    return value


def _check_required_files(case_dir: Path) -> None:
    for file_name in REQUIRED_FILES:
        if not (case_dir / file_name).is_file():
            raise ValueError("missing_required_file")


def _count_existing_required_files(case_dir: Path) -> int:
    return sum(1 for file_name in REQUIRED_FILES if (case_dir / file_name).is_file())


def _validate_root_shape(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return ["missing_root"]
    if not (root / "README.md").is_file():
        errors.append("missing_readme")
    for category in ("valid", "invalid"):
        if not (root / category).is_dir():
            errors.append(f"missing_{category}_dir")
    for path in root.rglob("*"):
        if path.is_file() and path.name != "README.md" and path.suffix != ".json":
            errors.append("unexpected_file_extension")
    cases = discover_frozen_policy_generation_scaffold_fixture_cases(root)
    valid_cases = [case for case in cases if case.parent.name == "valid"]
    invalid_cases = [case for case in cases if case.parent.name == "invalid"]
    if len(cases) != EXPECTED_TOTAL_CASES:
        errors.append("unexpected_case_count")
    if len(valid_cases) != EXPECTED_VALID_CASES:
        errors.append("unexpected_valid_case_count")
    if len(invalid_cases) != EXPECTED_INVALID_CASES:
        errors.append("unexpected_invalid_case_count")
    if len(list(root.rglob("*.json"))) != EXPECTED_JSON_FILE_COUNT:
        errors.append("unexpected_json_file_count")
    for case_dir in cases:
        for file_name in REQUIRED_FILES:
            if not (case_dir / file_name).is_file():
                errors.append("missing_required_file")
    json_values: list[Any] = []
    for path in sorted(root.rglob("*.json")):
        try:
            json_values.append(_read_json(path))
        except (OSError, json.JSONDecodeError, ValueError):
            errors.append("malformed_json_file")
    scan = _scan_forbidden_payloads(json_values)
    errors.extend(scan.reason_codes)
    return sorted(set(errors))


def _validate_case_contract(
    fixture: FrozenPolicyGenerationScaffoldFixtureCase,
) -> list[str]:
    errors: list[str] = []
    request = fixture.generation_request
    pointer = fixture.input_fixture_pointer
    expected = fixture.expected_scaffold_result

    errors.extend(_missing_fields(request, REQUIRED_REQUEST_FIELDS))
    errors.extend(_missing_fields(pointer, REQUIRED_POINTER_FIELDS))
    errors.extend(_missing_fields(expected, REQUIRED_EXPECTED_RESULT_FIELDS))
    if errors:
        return errors

    if request.get("request_schema_version") != REQUEST_SCHEMA_VERSION:
        errors.append("unknown_request_schema_version")
    if pointer.get("pointer_schema_version") != POINTER_SCHEMA_VERSION:
        errors.append("unknown_pointer_schema_version")
    if expected.get("scaffold_schema_version") != SCAFFOLD_RESULT_SCHEMA_VERSION:
        errors.append("unknown_scaffold_schema_version")
    if expected.get("generation_request_schema_version") != request.get(
        "request_schema_version"
    ):
        errors.append("request_schema_version_mismatch")
    if expected.get("pointer_schema_version") != pointer.get("pointer_schema_version"):
        errors.append("pointer_schema_version_mismatch")

    category = fixture.case_category
    if category == "valid":
        if fixture.case_name not in VALID_CASE_NAMES:
            errors.append("unknown_valid_fixture_case")
        if expected.get("scaffold_status") != "pass":
            errors.append("valid_case_expected_status_mismatch")
        if expected.get("reason_codes") != []:
            errors.append("valid_case_reason_codes_not_empty")
        if expected.get("failed_checks") != []:
            errors.append("valid_case_failed_checks_not_empty")
    elif category == "invalid":
        expected_reason = EXPECTED_INVALID_REASONS.get(fixture.case_name)
        if expected_reason is None:
            errors.append("unknown_invalid_fixture_case")
        if expected.get("scaffold_status") != "fail":
            errors.append("invalid_case_expected_status_mismatch")
        if expected_reason is not None and expected.get("reason_codes") != [
            expected_reason
        ]:
            errors.append("invalid_case_reason_code_mismatch")
        if not expected.get("failed_checks"):
            errors.append("invalid_case_failed_checks_empty")
    else:
        errors.append("unknown_case_category")

    for flag in EXPECTED_RESULT_TRUE_FLAGS:
        if expected.get(flag) is not True:
            errors.append(f"expected_flag_false:{flag}")
    if expected.get("would_write_artifact") is not False:
        errors.append("would_write_artifact_not_false")
    if expected.get("artifact_write_mode") != "dry_run_metadata_only":
        errors.append("artifact_write_mode_mismatch")
    if request.get("synthetic_only") is not True:
        errors.append("request_not_synthetic_only")
    if pointer.get("synthetic_only") is not True:
        errors.append("pointer_not_synthetic_only")
    if request.get("metadata_only") is not True:
        errors.append("request_not_metadata_only")
    if pointer.get("metadata_only") is not True:
        errors.append("pointer_not_metadata_only")
    if not isinstance(request.get("temperature_policy"), dict):
        errors.append("invalid_temperature_policy")
    if not isinstance(request.get("threshold_policy"), dict):
        errors.append("invalid_threshold_policy")
    if not isinstance(request.get("abstention_policy"), dict):
        errors.append("invalid_abstention_policy")
    if not isinstance(request.get("output_policy"), dict):
        errors.append("invalid_output_policy")

    scan = _scan_forbidden_payloads([request, pointer, expected])
    errors.extend(scan.reason_codes)
    return sorted(set(errors))


def _missing_fields(value: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f"missing_required_field:{field}" for field in fields if field not in value]


def _build_contract_result(
    fixture: FrozenPolicyGenerationScaffoldFixtureCase,
) -> FrozenPolicyGenerationScaffoldFixtureValidationResult:
    request = fixture.generation_request
    pointer = fixture.input_fixture_pointer
    expected = fixture.expected_scaffold_result
    reason_codes = _expected_reason_codes(fixture)
    scaffold_status = "pass" if fixture.case_category == "valid" else "fail"
    return FrozenPolicyGenerationScaffoldFixtureValidationResult(
        scaffold_status=scaffold_status,
        reason_codes=reason_codes,
        failed_checks=list(expected.get("failed_checks", [])),
        failure_categories=([] if scaffold_status == "pass" else ["expected_failure"]),
        checked_files_count=len(REQUIRED_FILES),
        case_category=fixture.case_category,
        case_name=fixture.case_name,
        generation_request_schema_version=request.get("request_schema_version"),
        pointer_schema_version=pointer.get("pointer_schema_version"),
        scaffold_schema_version=expected.get("scaffold_schema_version"),
        input_validation_status=pointer.get("input_validation_status"),
        selective_prediction_validation_status=pointer.get(
            "selective_prediction_validation_status"
        ),
        frozen_policy_validation_status=pointer.get("frozen_policy_validation_status"),
        validation_split_available=pointer.get("validation_split_available"),
        temperature_policy_status=_policy_status(request.get("temperature_policy")),
        threshold_policy_status=_policy_status(request.get("threshold_policy")),
        abstention_policy_status=_policy_status(request.get("abstention_policy")),
        output_policy_status=_policy_status(request.get("output_policy")),
        safety_status=("pass" if scaffold_status == "pass" else "fail_closed"),
        content_suppressed=True,
        no_raw_rows=True,
        no_logits_dump=True,
        no_request_body=True,
        no_generated_artifact_body=True,
        artifact_body_suppressed=True,
        synthetic_only_checked=True,
        no_oracle_checked=True,
        test_tuning_checked=True,
        private_path_scan_checked=True,
        performance_claim_scan_checked=True,
        would_write_artifact=False,
        artifact_write_mode="dry_run_metadata_only",
        metadata_only=True,
    )


def _input_error_result(
    fixture: FrozenPolicyGenerationScaffoldFixtureCase,
    errors: list[str],
) -> FrozenPolicyGenerationScaffoldFixtureValidationResult:
    return FrozenPolicyGenerationScaffoldFixtureValidationResult(
        scaffold_status="input_error",
        reason_codes=["fixture_contract_error"],
        failed_checks=sorted(errors),
        failure_categories=["input_error"],
        checked_files_count=len(REQUIRED_FILES),
        case_category=fixture.case_category,
        case_name=fixture.case_name,
        generation_request_schema_version=fixture.generation_request.get(
            "request_schema_version"
        ),
        pointer_schema_version=fixture.input_fixture_pointer.get(
            "pointer_schema_version"
        ),
        scaffold_schema_version=fixture.expected_scaffold_result.get(
            "scaffold_schema_version"
        ),
    )


def _expected_reason_codes(
    fixture: FrozenPolicyGenerationScaffoldFixtureCase,
) -> list[str]:
    if fixture.case_category == "valid":
        return []
    expected_reason = EXPECTED_INVALID_REASONS.get(fixture.case_name)
    return [expected_reason] if expected_reason else ["unknown_invalid_fixture_case"]


def _policy_status(policy: Any) -> str | None:
    if not isinstance(policy, dict):
        return None
    status = policy.get("status")
    if status == "invalid":
        return "fail"
    return status


def _scan_forbidden_payloads(values: list[Any]) -> ScaffoldFixtureSafetyScanResult:
    reason_codes: list[str] = []
    failed_checks: list[str] = []

    def visit(value: Any, key_context: str | None = None) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                key_lower = str(key).lower()
                if key_lower in RAW_ROW_PAYLOAD_KEYS:
                    reason_codes.append("raw_rows_payload")
                    failed_checks.append("raw_row_scan")
                elif key_lower in LOGITS_PAYLOAD_KEYS:
                    reason_codes.append("logits_payload")
                    failed_checks.append("logits_scan")
                elif key_lower in BODY_PAYLOAD_KEYS:
                    reason_codes.append("body_payload")
                    failed_checks.append("artifact_body_scan")
                elif key_lower in PERFORMANCE_PAYLOAD_KEYS:
                    reason_codes.append("performance_metric_payload")
                    failed_checks.append("performance_claim_scan")
                elif key_lower in RAW_LOG_PAYLOAD_KEYS:
                    reason_codes.append("raw_log_payload")
                    failed_checks.append("raw_log_scan")
                visit(nested, key_lower)
        elif isinstance(value, list):
            for item in value:
                visit(item, key_context)
        elif isinstance(value, str):
            if _is_marker_string(value, key_context):
                return
            lower = value.lower()
            if any(marker.lower() in lower for marker in UNSAFE_PATH_MARKERS):
                reason_codes.append("unsafe_path_payload")
                failed_checks.append("private_path_scan")

    for item in values:
        visit(item)

    unique_reasons = sorted(set(reason_codes))
    unique_checks = sorted(set(failed_checks))
    return ScaffoldFixtureSafetyScanResult(
        reason_codes=unique_reasons,
        failed_checks=unique_checks,
    )


def _is_marker_string(value: str, key_context: str | None) -> bool:
    if key_context in MARKER_KEYS:
        return True
    if value in EXPECTED_INVALID_REASONS:
        return True
    if value in EXPECTED_INVALID_REASONS.values():
        return True
    if value.startswith("invalid/") or value.startswith("valid/"):
        return True
    if value.startswith("learner_state_frozen_policy_generation/"):
        return True
    if value.startswith("synthetic_") and value.endswith("_marker_only"):
        return True
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate synthetic frozen policy generation scaffold fixtures "
            "with safe metadata-only output."
        )
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--fixture-root",
        type=Path,
        help="Synthetic scaffold fixture root to validate.",
    )
    group.add_argument(
        "--fixture-case",
        type=Path,
        help="Single synthetic scaffold fixture case to validate.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit safe machine-readable summary JSON.",
    )
    args = parser.parse_args(argv)

    selected_path = args.fixture_root or args.fixture_case
    if _is_unsafe_cli_path(selected_path):
        payload = _input_error_payload("unsafe_path")
        _emit_cli_payload(payload, args.json)
        return 2

    if args.fixture_root is not None:
        return _run_fixture_root_cli(args.fixture_root, args.json)
    return _run_fixture_case_cli(args.fixture_case, args.json)


def _run_fixture_root_cli(fixture_root: Path, json_output: bool) -> int:
    summary = validate_scaffold_fixture_root(fixture_root)
    payload = summary.to_safe_dict()
    _emit_cli_payload(payload, json_output)
    if summary.input_error_cases:
        return 2
    if summary.mismatched_cases:
        return 3
    return 0


def _run_fixture_case_cli(fixture_case: Path, json_output: bool) -> int:
    result = validate_scaffold_fixture_case(fixture_case)
    payload = result.to_safe_dict()
    payload["mode"] = "fixture_case"
    payload["fixture_case_label"] = _safe_case_label(fixture_case)

    if result.scaffold_status == "input_error":
        payload["expected_result_matched"] = False
        payload["mismatch_count"] = 0
        payload["mismatch_fields"] = []
        _emit_cli_payload(payload, json_output)
        return 2

    try:
        expected = load_expected_scaffold_result(fixture_case)
        mismatches = compare_scaffold_result_to_expected(result, expected)
    except (OSError, json.JSONDecodeError, ValueError):
        payload["scaffold_status"] = "input_error"
        payload["validation_status"] = "input_error"
        payload["reason_codes"] = ["malformed_fixture_file"]
        payload["failed_checks"] = ["expected_scaffold_result"]
        payload["expected_result_matched"] = False
        payload["mismatch_count"] = 0
        payload["mismatch_fields"] = []
        _emit_cli_payload(payload, json_output)
        return 2

    payload["expected_result_matched"] = not mismatches
    payload["mismatch_count"] = len(mismatches)
    payload["mismatch_fields"] = [mismatch.field_name for mismatch in mismatches]
    payload["mismatches"] = [
        _safe_mismatch_summary(mismatch) for mismatch in mismatches
    ]
    _emit_cli_payload(payload, json_output)
    return 0 if not mismatches else 3


def _safe_mismatch_summary(
    mismatch: ScaffoldFixtureValidationMismatch,
) -> dict[str, Any]:
    return {
        "field_name": mismatch.field_name,
        "expected_value": _safe_scalar_or_list(mismatch.expected_value),
        "actual_value": _safe_scalar_or_list(mismatch.actual_value),
    }


def _safe_scalar_or_list(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        return [
            item
            for item in value
            if isinstance(item, (str, int, float, bool)) or item is None
        ]
    if isinstance(value, dict):
        return "metadata_object_suppressed"
    return str(type(value).__name__)


def _input_error_payload(reason_code: str) -> dict[str, Any]:
    return {
        "validation_schema_version": VALIDATION_SCHEMA_VERSION,
        "mode": "input_error",
        "scaffold_status": "input_error",
        "validation_status": "input_error",
        "reason_codes": [reason_code],
        "failed_checks": [reason_code],
        "content_suppressed": True,
        "no_raw_rows": True,
        "synthetic_only_checked": True,
        "no_oracle_checked": True,
        "private_path_scan_checked": True,
        "performance_claim_scan_checked": True,
    }


def _emit_cli_payload(payload: dict[str, Any], json_output: bool) -> None:
    if json_output:
        print(json.dumps(payload, sort_keys=True))
        return
    for key in sorted(payload):
        value = payload[key]
        if isinstance(value, bool):
            value_text = "true" if value else "false"
        elif isinstance(value, (list, tuple)):
            value_text = ",".join(str(item) for item in value) if value else "none"
        elif isinstance(value, dict):
            value_text = json.dumps(value, sort_keys=True, separators=(",", ":"))
        else:
            value_text = str(value)
        print(f"{key}={value_text}")


def _is_unsafe_cli_path(path: Path) -> bool:
    text = str(path)
    parts = set(Path(path).parts)
    if parts.intersection(UNSAFE_CLI_PATH_PARTS):
        return True
    return any(marker in text for marker in UNSAFE_CLI_PATH_PARTS)


def _safe_case_label(path: Path) -> str:
    path = Path(path)
    parts = path.parts
    for marker in ("valid", "invalid"):
        if marker in parts:
            index = parts.index(marker)
            return "/".join(parts[index:])
    return path.name


if __name__ == "__main__":
    raise SystemExit(main())
