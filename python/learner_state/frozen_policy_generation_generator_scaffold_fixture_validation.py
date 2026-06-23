"""Safe synthetic frozen policy generation generator scaffold fixture validation.

This module validates metadata-only generator scaffold fixtures. It does not
implement or run a generator, write artifacts, generate artifact bodies, fit
calibration, run selective prediction, train an estimator, or compute metrics.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

GENERATION_REQUEST_FILE = "generation_request.json"
INPUT_FIXTURE_POINTER_FILE = "input_fixture_pointer.json"
EXPECTED_GENERATOR_SCAFFOLD_RESULT_FILE = (
    "expected_generator_scaffold_result.json"
)

REQUEST_SCHEMA_VERSION = "frozen_policy_generation_generator_scaffold_request_v0.1"
POINTER_SCHEMA_VERSION = "frozen_policy_generation_generator_scaffold_pointer_v0.1"
RESULT_SCHEMA_VERSION = "frozen_policy_generation_generator_scaffold_result_v0.1"
VALIDATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_generator_scaffold_fixture_validation_v0.1"
)

EXPECTED_VALID_CASES = 3
EXPECTED_INVALID_CASES = 15
EXPECTED_TOTAL_CASES = 18
EXPECTED_JSON_FILE_COUNT = EXPECTED_TOTAL_CASES * 3

VALID_CASE_LABELS = frozenset(
    {
        "valid/minimal_metadata_only_generation_plan",
        "valid/validated_fixed_threshold_metadata_plan",
        "valid/validated_fixed_abstention_rate_metadata_plan",
    }
)

EXPECTED_INVALID_REASONS = {
    "invalid/artifact_file_writing_attempt": "artifact_file_writing_not_allowed",
    "invalid/generated_artifact_body_leakage": "generated_artifact_body_leakage",
    "invalid/logits_dump_carryover": "logits_dump_carryover",
    "invalid/missing_required_field": "missing_required_field",
    "invalid/missing_validation_reference": "missing_validation_reference",
    "invalid/performance_claim_in_generated_policy": (
        "performance_claim_in_generated_policy"
    ),
    "invalid/pointer_body_leakage": "pointer_body_leakage",
    "invalid/private_path_output": "private_path_output",
    "invalid/raw_rows_carryover": "raw_rows_carryover",
    "invalid/request_body_leakage": "request_body_leakage",
    "invalid/scoring_feedback_violation": "scoring_feedback_violation",
    "invalid/test_temperature_tuning": "test_temperature_tuning",
    "invalid/test_threshold_tuning": "test_threshold_tuning",
    "invalid/unknown_schema_version": "unknown_schema_version",
    "invalid/unvalidated_input": "unvalidated_input",
}

REQUIRED_FILES = (
    GENERATION_REQUEST_FILE,
    INPUT_FIXTURE_POINTER_FILE,
    EXPECTED_GENERATOR_SCAFFOLD_RESULT_FILE,
)

REQUIRED_REQUEST_FIELDS = (
    "schema_version",
    "request_id",
    "generator_mode",
    "validation_reference_ids",
    "split_policy_label",
    "calibration_policy_label",
    "threshold_policy_label",
    "abstention_policy_label",
    "synthetic_only",
    "no_oracle_required",
    "artifact_policy_label",
    "requested_artifact_body",
    "requested_file_writing",
    "expected_generation_status",
    "expected_reason_codes",
    "notes",
)

REQUIRED_POINTER_FIELDS = (
    "schema_version",
    "pointer_id",
    "fixture_label",
    "validation_fixture_label",
    "frozen_policy_validation_label",
    "selective_prediction_validation_label",
    "source_kind",
    "synthetic_only",
    "no_raw_rows",
    "no_logits_dump",
    "no_private_paths",
    "notes",
)

REQUIRED_EXPECTED_RESULT_FIELDS = (
    "schema_version",
    "generation_status",
    "reason_codes",
    "failed_checks",
    "request_id",
    "pointer_id",
    "policy_id",
    "artifact_id",
    "generator_version",
    "validation_reference_ids",
    "artifact_flags",
    "safety_flags",
    "count_summary",
    "safe_summary",
)

REQUIRED_ARTIFACT_FLAGS = (
    "generated_artifact_written",
    "generated_artifact_body_available",
    "artifact_body_suppressed",
    "artifact_file_path_available",
    "artifact_manifest_available",
    "artifact_validation_summary_available",
)

EXPECTED_ARTIFACT_FLAG_VALUES = {
    "generated_artifact_written": False,
    "generated_artifact_body_available": False,
    "artifact_body_suppressed": True,
    "artifact_file_path_available": False,
    "artifact_manifest_available": False,
    "artifact_validation_summary_available": True,
}

REQUIRED_SAFETY_FLAGS = (
    "content_suppressed",
    "no_raw_rows",
    "no_logits_dump",
    "no_private_paths",
    "no_performance_claims",
    "synthetic_only_checked",
    "no_oracle_checked",
    "test_tuning_checked",
    "scoring_feedback_checked",
    "artifact_policy_checked",
    "body_suppression_checked",
    "file_writing_checked",
)

EXPECTED_TRUE_SAFETY_FLAGS = REQUIRED_SAFETY_FLAGS

REQUIRED_COUNT_SUMMARY_FIELDS = (
    "validation_reference_count",
    "artifact_metadata_field_count",
    "body_field_count",
    "raw_row_count",
    "logits_dump_count",
    "private_path_count",
    "performance_metric_count",
)

EXPECTED_ZERO_COUNT_FIELDS = (
    "body_field_count",
    "raw_row_count",
    "logits_dump_count",
    "private_path_count",
    "performance_metric_count",
)

UNSAFE_PATH_MARKERS = (
    "/Users/",
    "/home/",
    "/private/",
    "/var/folders/",
    "C:\\",
    "real_data/",
    "participant_data/",
    "private_data/",
    "manual_outputs/",
)

FORBIDDEN_PAYLOAD_KEYS = frozenset(
    {
        "raw_rows",
        "logits",
        "probabilities",
        "raw_learner_text",
        "observed_after_text",
        "final_text",
        "gold_label",
        "expected_action_feedback",
        "request_body",
        "pointer_body",
        "artifact_body",
        "generated_policy_body",
        "policy_json_body",
        "calibration_body",
        "label_body",
        "split_body",
        "private_path",
        "real_data",
        "participant_data",
        "manual_outputs",
        "performance_claim",
    }
)

ALLOWED_MARKER_KEYS = frozenset(
    {
        "reason_codes",
        "failed_checks",
        "expected_reason_codes",
        "expected_generation_status",
        "expected_failure_marker",
        "unsafe_marker_label",
        "notes",
        "fixture_label",
        "pointer_id",
        "request_id",
        "policy_id",
        "artifact_id",
        "validation_reference_ids",
        "validation_fixture_label",
        "frozen_policy_validation_label",
        "selective_prediction_validation_label",
    }
)


@dataclass(frozen=True)
class GeneratorScaffoldFixtureCase:
    case_dir: Path
    case_category: str
    case_name: str
    case_label: str
    generation_request: dict[str, Any]
    input_fixture_pointer: dict[str, Any]
    expected_generator_scaffold_result: dict[str, Any]


@dataclass(frozen=True)
class GeneratorScaffoldFixtureSafetySummary:
    content_suppressed: bool = True
    no_raw_rows: bool = True
    no_logits_dump: bool = True
    no_private_paths: bool = True
    no_performance_claims: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    artifact_policy_checked: bool = True
    body_suppression_checked: bool = True
    file_writing_checked: bool = True
    forbidden_marker_scan_checked: bool = True
    reason_codes: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "content_suppressed": self.content_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "no_logits_dump": self.no_logits_dump,
            "no_private_paths": self.no_private_paths,
            "no_performance_claims": self.no_performance_claims,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
            "artifact_policy_checked": self.artifact_policy_checked,
            "body_suppression_checked": self.body_suppression_checked,
            "file_writing_checked": self.file_writing_checked,
            "forbidden_marker_scan_checked": self.forbidden_marker_scan_checked,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
        }


@dataclass(frozen=True)
class GeneratorScaffoldFixtureValidationResult:
    generation_status: str
    reason_codes: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)
    failure_categories: list[str] = field(default_factory=list)
    checked_files_count: int = 0
    case_category: str | None = None
    case_name: str | None = None
    case_label: str | None = None
    request_id: str | None = None
    pointer_id: str | None = None
    policy_id: str | None = None
    artifact_id: str | None = None
    generator_version: str | None = None
    request_schema_version: str | None = None
    pointer_schema_version: str | None = None
    result_schema_version: str | None = None
    validation_reference_ids: list[str] = field(default_factory=list)
    artifact_flags: dict[str, bool] = field(default_factory=dict)
    safety_flags: dict[str, bool] = field(default_factory=dict)
    count_summary: dict[str, int] = field(default_factory=dict)
    safe_summary: str | None = None
    content_suppressed: bool = True
    no_raw_rows: bool = True
    no_logits_dump: bool = True
    no_private_paths: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    artifact_policy_checked: bool = True
    body_suppression_checked: bool = True
    file_writing_checked: bool = True
    validation_schema_version: str = VALIDATION_SCHEMA_VERSION

    @property
    def validation_status(self) -> str:
        return self.generation_status

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "validation_schema_version": self.validation_schema_version,
            "generation_status": self.generation_status,
            "validation_status": self.validation_status,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "failure_categories": list(self.failure_categories),
            "checked_files_count": self.checked_files_count,
            "case_category": self.case_category,
            "case_name": self.case_name,
            "case_label": self.case_label,
            "request_id": self.request_id,
            "pointer_id": self.pointer_id,
            "policy_id": self.policy_id,
            "artifact_id": self.artifact_id,
            "generator_version": self.generator_version,
            "request_schema_version": self.request_schema_version,
            "pointer_schema_version": self.pointer_schema_version,
            "result_schema_version": self.result_schema_version,
            "validation_reference_ids": list(self.validation_reference_ids),
            "artifact_flags": dict(self.artifact_flags),
            "safety_flags": dict(self.safety_flags),
            "count_summary": dict(self.count_summary),
            "safe_summary": self.safe_summary,
            "content_suppressed": self.content_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "no_logits_dump": self.no_logits_dump,
            "no_private_paths": self.no_private_paths,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
            "artifact_policy_checked": self.artifact_policy_checked,
            "body_suppression_checked": self.body_suppression_checked,
            "file_writing_checked": self.file_writing_checked,
        }


@dataclass(frozen=True)
class GeneratorScaffoldFixtureComparisonResult:
    field_name: str
    expected_value: Any
    actual_value: Any

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "field_name": self.field_name,
            "expected_value": _safe_scalar_or_collection(self.expected_value),
            "actual_value": _safe_scalar_or_collection(self.actual_value),
        }


@dataclass(frozen=True)
class GeneratorScaffoldFixtureInputError:
    reason_code: str
    failed_check: str
    case_label: str | None = None

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "reason_code": self.reason_code,
            "failed_check": self.failed_check,
            "case_label": self.case_label,
        }


@dataclass(frozen=True)
class GeneratorScaffoldFixtureRootValidationResult:
    mode: str = "fixture_root"
    total_cases: int = 0
    matched_cases: int = 0
    mismatched_cases: int = 0
    input_error_cases: int = 0
    reason_code_counts: dict[str, int] = field(default_factory=dict)
    content_suppressed: bool = True
    no_raw_rows: bool = True
    no_logits_dump: bool = True
    no_private_paths: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    artifact_policy_checked: bool = True
    body_suppression_checked: bool = True
    file_writing_checked: bool = True
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
            "no_logits_dump": self.no_logits_dump,
            "no_private_paths": self.no_private_paths,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
            "artifact_policy_checked": self.artifact_policy_checked,
            "body_suppression_checked": self.body_suppression_checked,
            "file_writing_checked": self.file_writing_checked,
        }


def discover_frozen_policy_generation_generator_scaffold_fixture_cases(
    fixture_root: Path,
) -> list[Path]:
    root = Path(fixture_root)
    cases: list[Path] = []
    for category in ("valid", "invalid"):
        category_dir = root / category
        if category_dir.exists():
            cases.extend(path for path in category_dir.iterdir() if path.is_dir())
    return sorted(cases)


def load_generator_scaffold_fixture_case(
    case_dir: Path,
) -> GeneratorScaffoldFixtureCase:
    case_dir = Path(case_dir)
    case_category = case_dir.parent.name
    case_name = case_dir.name
    case_label = f"{case_category}/{case_name}"
    return GeneratorScaffoldFixtureCase(
        case_dir=case_dir,
        case_category=case_category,
        case_name=case_name,
        case_label=case_label,
        generation_request=_read_json(case_dir / GENERATION_REQUEST_FILE),
        input_fixture_pointer=_read_json(case_dir / INPUT_FIXTURE_POINTER_FILE),
        expected_generator_scaffold_result=_read_json(
            case_dir / EXPECTED_GENERATOR_SCAFFOLD_RESULT_FILE
        ),
    )


def load_expected_generator_scaffold_result(path: Path) -> dict[str, Any]:
    path = Path(path)
    expected_path = (
        path
        if path.name == EXPECTED_GENERATOR_SCAFFOLD_RESULT_FILE
        else path / EXPECTED_GENERATOR_SCAFFOLD_RESULT_FILE
    )
    return _read_json(expected_path)


def validate_generator_scaffold_fixture_case(
    case: GeneratorScaffoldFixtureCase | Path,
) -> GeneratorScaffoldFixtureValidationResult:
    try:
        fixture = (
            load_generator_scaffold_fixture_case(Path(case))
            if not isinstance(case, GeneratorScaffoldFixtureCase)
            else case
        )
        errors = _validate_case_contract(fixture)
        if errors:
            return _input_error_result(fixture, errors)
        return _build_expected_contract_result(fixture)
    except (OSError, json.JSONDecodeError, ValueError):
        case_dir = Path(case) if not isinstance(case, GeneratorScaffoldFixtureCase) else case.case_dir
        return GeneratorScaffoldFixtureValidationResult(
            generation_status="input_error",
            reason_codes=["malformed_fixture_file"],
            failed_checks=["json_parse_or_fixture_shape"],
            failure_categories=["input_error"],
            checked_files_count=_count_existing_required_files(case_dir),
            case_category=case_dir.parent.name,
            case_name=case_dir.name,
            case_label=f"{case_dir.parent.name}/{case_dir.name}",
        )


def compare_generator_scaffold_fixture_to_expected(
    case_result: GeneratorScaffoldFixtureValidationResult,
    expected: dict[str, Any],
) -> list[GeneratorScaffoldFixtureComparisonResult]:
    actual = case_result.to_safe_dict()
    field_map = {
        "generation_status": "generation_status",
        "reason_codes": "reason_codes",
        "failed_checks": "failed_checks",
        "request_id": "request_id",
        "pointer_id": "pointer_id",
        "policy_id": "policy_id",
        "artifact_id": "artifact_id",
        "generator_version": "generator_version",
        "validation_reference_ids": "validation_reference_ids",
        "artifact_flags": "artifact_flags",
        "safety_flags": "safety_flags",
        "count_summary": "count_summary",
        "safe_summary": "safe_summary",
    }
    mismatches: list[GeneratorScaffoldFixtureComparisonResult] = []
    for expected_field, actual_field in field_map.items():
        if expected.get(expected_field) != actual.get(actual_field):
            mismatches.append(
                GeneratorScaffoldFixtureComparisonResult(
                    field_name=expected_field,
                    expected_value=expected.get(expected_field),
                    actual_value=actual.get(actual_field),
                )
            )
    return mismatches


def validate_generator_scaffold_fixture_root(
    fixture_root: Path,
) -> GeneratorScaffoldFixtureRootValidationResult:
    root = Path(fixture_root)
    root_errors = _validate_root_shape(root)
    if root_errors:
        return GeneratorScaffoldFixtureRootValidationResult(
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

    for case_dir in discover_frozen_policy_generation_generator_scaffold_fixture_cases(
        root
    ):
        result = validate_generator_scaffold_fixture_case(case_dir)
        reason_counter.update(result.reason_codes)
        if result.generation_status == "input_error":
            input_error_cases += 1
            continue
        expected = load_expected_generator_scaffold_result(case_dir)
        mismatches = compare_generator_scaffold_fixture_to_expected(result, expected)
        if mismatches:
            mismatched_cases += 1
        else:
            matched_cases += 1

    total_cases = matched_cases + mismatched_cases + input_error_cases
    return GeneratorScaffoldFixtureRootValidationResult(
        total_cases=total_cases,
        matched_cases=matched_cases,
        mismatched_cases=mismatched_cases,
        input_error_cases=input_error_cases,
        reason_code_counts=dict(sorted(reason_counter.items())),
    )


def summarize_generator_scaffold_fixture_validation_result(
    result: (
        GeneratorScaffoldFixtureValidationResult
        | GeneratorScaffoldFixtureRootValidationResult
        | GeneratorScaffoldFixtureSafetySummary
        | GeneratorScaffoldFixtureInputError
    ),
) -> dict[str, Any]:
    return result.to_safe_dict()


def scan_generator_scaffold_fixture_for_forbidden_markers(
    case: GeneratorScaffoldFixtureCase | Path,
) -> GeneratorScaffoldFixtureSafetySummary:
    fixture = (
        load_generator_scaffold_fixture_case(Path(case))
        if not isinstance(case, GeneratorScaffoldFixtureCase)
        else case
    )
    return _scan_forbidden_payloads(
        [
            fixture.generation_request,
            fixture.input_fixture_pointer,
            fixture.expected_generator_scaffold_result,
        ]
    )


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        value = json.load(file)
    if not isinstance(value, dict):
        raise ValueError("expected_json_object")
    return value


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
        if path.is_file():
            if path.name == "README.md":
                continue
            if path.suffix != ".json":
                errors.append("unexpected_file_extension")

    cases = discover_frozen_policy_generation_generator_scaffold_fixture_cases(root)
    valid_cases = [case for case in cases if case.parent.name == "valid"]
    invalid_cases = [case for case in cases if case.parent.name == "invalid"]
    if len(valid_cases) != EXPECTED_VALID_CASES:
        errors.append("unexpected_valid_case_count")
    if len(invalid_cases) != EXPECTED_INVALID_CASES:
        errors.append("unexpected_invalid_case_count")
    if len(cases) != EXPECTED_TOTAL_CASES:
        errors.append("unexpected_case_count")
    if len(list(root.rglob("*.json"))) != EXPECTED_JSON_FILE_COUNT:
        errors.append("unexpected_json_file_count")

    expected_labels = set(VALID_CASE_LABELS) | set(EXPECTED_INVALID_REASONS)
    discovered_labels = {f"{case.parent.name}/{case.name}" for case in cases}
    if discovered_labels != expected_labels:
        errors.append("unexpected_case_labels")

    for case_dir in cases:
        errors.extend(_validate_required_file_shape(case_dir))
        try:
            fixture = load_generator_scaffold_fixture_case(case_dir)
        except (OSError, json.JSONDecodeError, ValueError):
            errors.append("malformed_json_file")
            continue
        scan = scan_generator_scaffold_fixture_for_forbidden_markers(fixture)
        errors.extend(scan.reason_codes)

    return sorted(set(errors))


def _validate_required_file_shape(case_dir: Path) -> list[str]:
    errors: list[str] = []
    found_files = [path.name for path in case_dir.iterdir() if path.is_file()]
    for file_name in REQUIRED_FILES:
        if file_name not in found_files:
            errors.append("missing_required_file")
    unexpected = sorted(set(found_files) - set(REQUIRED_FILES))
    if unexpected:
        errors.append("unexpected_case_file")
    return errors


def _validate_case_contract(fixture: GeneratorScaffoldFixtureCase) -> list[str]:
    errors: list[str] = []
    errors.extend(_validate_required_file_shape(fixture.case_dir))
    request = fixture.generation_request
    pointer = fixture.input_fixture_pointer
    expected = fixture.expected_generator_scaffold_result

    errors.extend(_missing_fields(request, REQUIRED_REQUEST_FIELDS))
    errors.extend(_missing_fields(pointer, REQUIRED_POINTER_FIELDS))
    errors.extend(_missing_fields(expected, REQUIRED_EXPECTED_RESULT_FIELDS))
    if errors:
        return sorted(set(errors))

    if request.get("schema_version") != REQUEST_SCHEMA_VERSION:
        errors.append("unknown_request_schema_version")
    if pointer.get("schema_version") != POINTER_SCHEMA_VERSION:
        errors.append("unknown_pointer_schema_version")
    if expected.get("schema_version") != RESULT_SCHEMA_VERSION:
        errors.append("unknown_result_schema_version")

    errors.extend(_validate_required_type_shapes(request, pointer, expected))
    errors.extend(_validate_category_contract(fixture))
    errors.extend(_validate_artifact_flags(expected.get("artifact_flags")))
    errors.extend(_validate_safety_flags(expected.get("safety_flags")))
    errors.extend(_validate_count_summary(expected.get("count_summary")))
    errors.extend(_validate_synthetic_only_contract(request, pointer))
    errors.extend(_validate_identity_links(request, pointer, expected))

    scan = scan_generator_scaffold_fixture_for_forbidden_markers(fixture)
    errors.extend(scan.reason_codes)
    return sorted(set(errors))


def _validate_required_type_shapes(
    request: dict[str, Any],
    pointer: dict[str, Any],
    expected: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(request.get("validation_reference_ids"), list):
        errors.append("invalid_validation_reference_ids")
    if not isinstance(request.get("expected_reason_codes"), list):
        errors.append("invalid_expected_reason_codes")
    if not isinstance(expected.get("validation_reference_ids"), list):
        errors.append("invalid_expected_validation_reference_ids")
    for field_name in (
        "synthetic_only",
        "no_oracle_required",
        "requested_artifact_body",
        "requested_file_writing",
    ):
        if not isinstance(request.get(field_name), bool):
            errors.append(f"invalid_bool_field:{field_name}")
    for field_name in ("synthetic_only", "no_raw_rows", "no_logits_dump", "no_private_paths"):
        if not isinstance(pointer.get(field_name), bool):
            errors.append(f"invalid_bool_field:{field_name}")
    for nested_field in ("artifact_flags", "safety_flags", "count_summary"):
        if not isinstance(expected.get(nested_field), dict):
            errors.append(f"invalid_object_field:{nested_field}")
    return errors


def _validate_category_contract(fixture: GeneratorScaffoldFixtureCase) -> list[str]:
    errors: list[str] = []
    request = fixture.generation_request
    expected = fixture.expected_generator_scaffold_result
    case_label = fixture.case_label

    if fixture.case_category == "valid":
        if case_label not in VALID_CASE_LABELS:
            errors.append("unknown_valid_fixture_case")
        if expected.get("generation_status") != "pass":
            errors.append("valid_case_expected_status_mismatch")
        if request.get("expected_generation_status") != "pass":
            errors.append("valid_case_request_status_mismatch")
        if expected.get("reason_codes") != []:
            errors.append("valid_case_reason_codes_not_empty")
        if request.get("expected_reason_codes") != []:
            errors.append("valid_case_request_reason_codes_not_empty")
        if expected.get("failed_checks") != []:
            errors.append("valid_case_failed_checks_not_empty")
    elif fixture.case_category == "invalid":
        expected_reason = EXPECTED_INVALID_REASONS.get(case_label)
        if expected_reason is None:
            errors.append("unknown_invalid_fixture_case")
        if expected.get("generation_status") != "fail":
            errors.append("invalid_case_expected_status_mismatch")
        if request.get("expected_generation_status") != "fail":
            errors.append("invalid_case_request_status_mismatch")
        if not expected.get("reason_codes"):
            errors.append("invalid_case_reason_codes_empty")
        if not request.get("expected_reason_codes"):
            errors.append("invalid_case_request_reason_codes_empty")
        if not expected.get("failed_checks"):
            errors.append("invalid_case_failed_checks_empty")
        if expected_reason is not None:
            if expected.get("reason_codes") != [expected_reason]:
                errors.append("invalid_case_reason_code_mismatch")
            if request.get("expected_reason_codes") != [expected_reason]:
                errors.append("invalid_case_request_reason_code_mismatch")
    else:
        errors.append("unknown_case_category")
    return errors


def _validate_artifact_flags(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["invalid_artifact_flags"]
    errors: list[str] = []
    for field_name in REQUIRED_ARTIFACT_FLAGS:
        if field_name not in value:
            errors.append(f"missing_artifact_flag:{field_name}")
        elif not isinstance(value.get(field_name), bool):
            errors.append(f"artifact_flag_not_bool:{field_name}")
    for field_name, expected_value in EXPECTED_ARTIFACT_FLAG_VALUES.items():
        if value.get(field_name) is not expected_value:
            errors.append(f"artifact_flag_value_mismatch:{field_name}")
    return errors


def _validate_safety_flags(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["invalid_safety_flags"]
    errors: list[str] = []
    for field_name in REQUIRED_SAFETY_FLAGS:
        if field_name not in value:
            errors.append(f"missing_safety_flag:{field_name}")
        elif not isinstance(value.get(field_name), bool):
            errors.append(f"safety_flag_not_bool:{field_name}")
    for field_name in EXPECTED_TRUE_SAFETY_FLAGS:
        if value.get(field_name) is not True:
            errors.append(f"safety_flag_value_mismatch:{field_name}")
    return errors


def _validate_count_summary(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["invalid_count_summary"]
    errors: list[str] = []
    for field_name in REQUIRED_COUNT_SUMMARY_FIELDS:
        if field_name not in value:
            errors.append(f"missing_count_summary_field:{field_name}")
            continue
        if not isinstance(value.get(field_name), int):
            errors.append(f"count_summary_not_int:{field_name}")
        elif value[field_name] < 0:
            errors.append(f"count_summary_negative:{field_name}")
    for field_name in EXPECTED_ZERO_COUNT_FIELDS:
        if value.get(field_name) != 0:
            errors.append(f"count_summary_zero_mismatch:{field_name}")
    return errors


def _validate_synthetic_only_contract(
    request: dict[str, Any],
    pointer: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if request.get("synthetic_only") is not True:
        errors.append("request_not_synthetic_only")
    if request.get("no_oracle_required") is not True:
        errors.append("request_no_oracle_not_required")
    if pointer.get("synthetic_only") is not True:
        errors.append("pointer_not_synthetic_only")
    return errors


def _validate_identity_links(
    request: dict[str, Any],
    pointer: dict[str, Any],
    expected: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if expected.get("request_id") != request.get("request_id"):
        errors.append("request_id_mismatch")
    if expected.get("pointer_id") != pointer.get("pointer_id"):
        errors.append("pointer_id_mismatch")
    if expected.get("validation_reference_ids") != request.get("validation_reference_ids"):
        errors.append("validation_reference_ids_mismatch")
    count_summary = expected.get("count_summary")
    if isinstance(count_summary, dict):
        if count_summary.get("validation_reference_count") != len(
            request.get("validation_reference_ids", [])
        ):
            errors.append("validation_reference_count_mismatch")
    return errors


def _missing_fields(value: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [f"missing_required_field:{field}" for field in fields if field not in value]


def _build_expected_contract_result(
    fixture: GeneratorScaffoldFixtureCase,
) -> GeneratorScaffoldFixtureValidationResult:
    request = fixture.generation_request
    pointer = fixture.input_fixture_pointer
    expected = fixture.expected_generator_scaffold_result
    artifact_flags = dict(expected.get("artifact_flags", {}))
    safety_flags = dict(expected.get("safety_flags", {}))
    count_summary = dict(expected.get("count_summary", {}))
    return GeneratorScaffoldFixtureValidationResult(
        generation_status=expected.get("generation_status"),
        reason_codes=list(expected.get("reason_codes", [])),
        failed_checks=list(expected.get("failed_checks", [])),
        failure_categories=(
            []
            if expected.get("generation_status") == "pass"
            else ["expected_failure"]
        ),
        checked_files_count=len(REQUIRED_FILES),
        case_category=fixture.case_category,
        case_name=fixture.case_name,
        case_label=fixture.case_label,
        request_id=expected.get("request_id"),
        pointer_id=expected.get("pointer_id"),
        policy_id=expected.get("policy_id"),
        artifact_id=expected.get("artifact_id"),
        generator_version=expected.get("generator_version"),
        request_schema_version=request.get("schema_version"),
        pointer_schema_version=pointer.get("schema_version"),
        result_schema_version=expected.get("schema_version"),
        validation_reference_ids=list(expected.get("validation_reference_ids", [])),
        artifact_flags=artifact_flags,
        safety_flags=safety_flags,
        count_summary=count_summary,
        safe_summary=expected.get("safe_summary"),
        content_suppressed=safety_flags.get("content_suppressed", True),
        no_raw_rows=safety_flags.get("no_raw_rows", True),
        no_logits_dump=safety_flags.get("no_logits_dump", True),
        no_private_paths=safety_flags.get("no_private_paths", True),
        synthetic_only_checked=safety_flags.get("synthetic_only_checked", True),
        no_oracle_checked=safety_flags.get("no_oracle_checked", True),
        artifact_policy_checked=safety_flags.get("artifact_policy_checked", True),
        body_suppression_checked=safety_flags.get("body_suppression_checked", True),
        file_writing_checked=safety_flags.get("file_writing_checked", True),
    )


def _input_error_result(
    fixture: GeneratorScaffoldFixtureCase,
    errors: list[str],
) -> GeneratorScaffoldFixtureValidationResult:
    return GeneratorScaffoldFixtureValidationResult(
        generation_status="input_error",
        reason_codes=["fixture_contract_error"],
        failed_checks=sorted(errors),
        failure_categories=["input_error"],
        checked_files_count=_count_existing_required_files(fixture.case_dir),
        case_category=fixture.case_category,
        case_name=fixture.case_name,
        case_label=fixture.case_label,
        request_id=fixture.generation_request.get("request_id"),
        pointer_id=fixture.input_fixture_pointer.get("pointer_id"),
        request_schema_version=fixture.generation_request.get("schema_version"),
        pointer_schema_version=fixture.input_fixture_pointer.get("schema_version"),
        result_schema_version=fixture.expected_generator_scaffold_result.get(
            "schema_version"
        ),
    )


def _count_existing_required_files(case_dir: Path) -> int:
    return sum(1 for file_name in REQUIRED_FILES if (case_dir / file_name).is_file())


def _scan_forbidden_payloads(
    values: list[Any],
) -> GeneratorScaffoldFixtureSafetySummary:
    reason_codes: list[str] = []
    failed_checks: list[str] = []

    def visit(value: Any, key_context: str | None = None) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                key_lower = str(key).lower()
                if _is_forbidden_payload_key(key_lower):
                    reason_codes.append("forbidden_payload_key")
                    failed_checks.append(key_lower)
                visit(nested, key_lower)
        elif isinstance(value, list):
            for item in value:
                visit(item, key_context)
        elif isinstance(value, str):
            if _is_safe_marker_string(value, key_context):
                return
            lower = value.lower()
            if any(marker.lower() in lower for marker in UNSAFE_PATH_MARKERS):
                reason_codes.append("unsafe_path_payload")
                failed_checks.append("private_path_scan")

    for item in values:
        visit(item)

    return GeneratorScaffoldFixtureSafetySummary(
        reason_codes=sorted(set(reason_codes)),
        failed_checks=sorted(set(failed_checks)),
    )


def _is_forbidden_payload_key(key: str) -> bool:
    if key in FORBIDDEN_PAYLOAD_KEYS:
        return True
    return False


def _is_safe_marker_string(value: str, key_context: str | None) -> bool:
    if key_context in ALLOWED_MARKER_KEYS:
        return True
    if value.startswith("valid/") or value.startswith("invalid/"):
        return True
    if value.startswith("synthetic_"):
        return True
    if value.startswith("learner_state_"):
        return True
    if value in EXPECTED_INVALID_REASONS.values():
        return True
    if value in VALID_CASE_LABELS or value in EXPECTED_INVALID_REASONS:
        return True
    return False


def _safe_scalar_or_collection(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        return [
            item
            for item in value
            if isinstance(item, (str, int, float, bool)) or item is None
        ]
    if isinstance(value, dict):
        return {
            str(key): item
            for key, item in value.items()
            if isinstance(item, (str, int, float, bool)) or item is None
        }
    return type(value).__name__
