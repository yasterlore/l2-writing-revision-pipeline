"""Safe synthetic artifact writer fixture validation.

This module validates metadata-only frozen policy generation artifact writer
fixtures. It does not implement or run an artifact writer, generate artifact
bodies, generate policy bodies, write manifests, write files, train models, or
compute metrics.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ARTIFACT_WRITER_REQUEST_FILE = "artifact_writer_request.json"
GENERATOR_RESULT_POINTER_FILE = "generator_result_pointer.json"
EXPECTED_ARTIFACT_WRITER_RESULT_FILE = "expected_artifact_writer_result.json"

REQUEST_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_request_v0.1"
)
POINTER_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_generator_result_pointer_v0.1"
)
EXPECTED_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_expected_result_v0.1"
)
RESULT_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_result_v0.1"
)
VALIDATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_fixture_validation_v0.1"
)

EXPECTED_VALID_CASES = 3
EXPECTED_INVALID_CASES = 14
EXPECTED_TOTAL_CASES = 17
EXPECTED_JSON_FILE_COUNT = EXPECTED_TOTAL_CASES * 3

VALID_CASE_LABELS = frozenset(
    {
        "valid/minimal_metadata_only_artifact_plan",
        "valid/metadata_manifest_summary_only",
        "valid/synthetic_generator_result_reference",
    }
)

EXPECTED_INVALID_REASONS = {
    "invalid/artifact_file_writing_not_allowed": (
        "artifact_file_writing_not_allowed"
    ),
    "invalid/generated_artifact_body_leakage": "generated_artifact_body_leakage",
    "invalid/generated_policy_body_leakage": "generated_policy_body_leakage",
    "invalid/logits_dump_carryover": "logits_dump_carryover",
    "invalid/manifest_body_leakage": "manifest_body_leakage",
    "invalid/manifest_file_writing_not_allowed": (
        "manifest_file_writing_not_allowed"
    ),
    "invalid/missing_required_field": "missing_required_field",
    "invalid/no_oracle_violation": "no_oracle_violation",
    "invalid/non_synthetic_input": "non_synthetic_input",
    "invalid/performance_claim_in_artifact": "performance_claim_in_artifact",
    "invalid/private_path_output": "private_path_output",
    "invalid/raw_rows_carryover": "raw_rows_carryover",
    "invalid/scoring_feedback_violation": "scoring_feedback_violation",
    "invalid/unknown_schema_version": "unknown_schema_version",
}

REQUIRED_FILES = (
    ARTIFACT_WRITER_REQUEST_FILE,
    GENERATOR_RESULT_POINTER_FILE,
    EXPECTED_ARTIFACT_WRITER_RESULT_FILE,
)

REQUIRED_REQUEST_FIELDS = (
    "schema_version",
    "request_id",
    "generator_result_id",
    "generator_result_pointer_id",
    "policy_id",
    "artifact_id",
    "manifest_id",
    "generator_version",
    "artifact_writer_version",
    "validation_reference_ids",
    "artifact_policy_label",
    "requested_artifact_body",
    "requested_file_writing",
    "requested_manifest",
    "synthetic_only",
    "no_oracle_required",
    "safe_output_mode",
    "safe_notes",
    "expected_status",
    "expected_reason_codes",
    "expected_failed_checks",
    "count_summary_hint",
)

REQUIRED_POINTER_FIELDS = (
    "schema_version",
    "generator_result_pointer_id",
    "generator_result_id",
    "generator_result_schema_version",
    "generator_version",
    "policy_id",
    "artifact_id",
    "validation_reference_ids",
    "safe_summary",
    "safe_pointer_notes",
    "synthetic_only",
    "no_oracle_required",
    "content_suppressed",
)

REQUIRED_EXPECTED_FIELDS = (
    "schema_version",
    "result_schema_version",
    "writer_status",
    "reason_codes",
    "failed_checks",
    "request_id",
    "generator_result_id",
    "policy_id",
    "artifact_id",
    "manifest_id",
    "artifact_writer_version",
    "artifact_policy_label",
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
    "artifact_manifest_body_available",
    "artifact_validation_summary_available",
    "file_writing_allowed",
    "manifest_body_suppressed",
)

EXPECTED_ARTIFACT_FLAG_VALUES = {
    "generated_artifact_written": False,
    "generated_artifact_body_available": False,
    "artifact_body_suppressed": True,
    "artifact_file_path_available": False,
    "artifact_manifest_available": True,
    "artifact_manifest_body_available": False,
    "artifact_validation_summary_available": True,
    "file_writing_allowed": False,
    "manifest_body_suppressed": True,
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
    "manifest_body_suppression_checked",
    "output_path_safety_checked",
)

REQUIRED_COUNT_SUMMARY_FIELDS = (
    "validation_reference_count",
    "artifact_metadata_field_count",
    "manifest_metadata_field_count",
    "body_field_count",
    "raw_row_count",
    "logits_dump_count",
    "private_path_count",
    "performance_metric_count",
    "generated_artifact_count",
    "written_file_count",
    "manifest_body_count",
)

EXPECTED_ZERO_COUNT_FIELDS = (
    "body_field_count",
    "raw_row_count",
    "logits_dump_count",
    "private_path_count",
    "performance_metric_count",
    "generated_artifact_count",
    "written_file_count",
    "manifest_body_count",
)

FORBIDDEN_PAYLOAD_KEYS = frozenset(
    {
        "generated_policy_body",
        "generated_artifact_body",
        "artifact_body",
        "manifest_body",
        "policy_body",
        "raw_rows",
        "logits",
        "probabilities",
        "raw_learner_text",
        "observed_after_text",
        "final_text",
        "gold_label",
        "expected_action",
        "scoring_feedback_payload",
        "request_body",
        "pointer_body",
        "expected_result_body",
        "private_path",
        "absolute_path",
        "real_participant_data",
        "calibration_body",
        "label_body",
        "split_body",
        "performance_metrics",
    }
)

SAFE_MARKER_KEYS = frozenset(
    {
        "generated_policy_body_present",
        "generated_artifact_body_present",
        "manifest_body_present",
        "raw_rows_present",
        "logits_dump_present",
        "private_path_marker_present",
        "artifact_file_writing_requested",
        "manifest_file_writing_requested",
        "non_synthetic_input_present",
        "no_oracle_violation_present",
        "scoring_feedback_marker_present",
        "performance_claim_marker_present",
        "missing_required_field_marker_present",
        "unknown_schema_version_marker_present",
        # Step302 fixture aliases, kept body-free and marker-only.
        "requested_manifest_file_writing",
        "non_synthetic_marker_present",
        "no_oracle_violation_marker_present",
        "scoring_feedback_payload_present",
    }
)

SAFE_STRING_CONTEXT_KEYS = frozenset(
    {
        "request_id",
        "generator_result_id",
        "generator_result_pointer_id",
        "policy_id",
        "artifact_id",
        "manifest_id",
        "generator_version",
        "artifact_writer_version",
        "artifact_policy_label",
        "validation_reference_ids",
        "safe_output_mode",
        "safe_notes",
        "expected_status",
        "expected_reason_codes",
        "expected_failed_checks",
        "generator_result_schema_version",
        "safe_summary",
        "safe_pointer_notes",
        "reason_codes",
        "failed_checks",
    }
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

RAW_LOG_MARKERS = (
    "::group::",
    "::endgroup::",
    "##[group]",
    "##[endgroup]",
    "github actions raw log",
    "full job output",
)


@dataclass(frozen=True)
class ArtifactWriterFixtureCase:
    case_dir: Path
    case_category: str
    case_name: str
    case_label: str
    request_metadata: dict[str, Any]
    generator_result_pointer_metadata: dict[str, Any]
    expected_result_metadata: dict[str, Any]
    request_schema_version: str | None
    pointer_schema_version: str | None
    expected_schema_version: str | None
    result_schema_version: str | None


@dataclass(frozen=True)
class ArtifactWriterFixtureSafetySummary:
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
    manifest_body_suppression_checked: bool = True
    output_path_safety_checked: bool = True
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
            "manifest_body_suppression_checked": (
                self.manifest_body_suppression_checked
            ),
            "output_path_safety_checked": self.output_path_safety_checked,
            "forbidden_marker_scan_checked": self.forbidden_marker_scan_checked,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
        }


@dataclass(frozen=True)
class ArtifactWriterFixtureComparisonResult:
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
class ArtifactWriterFixtureInputError:
    error_code: str
    failed_check: str
    case_label: str | None = None
    file_role: str | None = None
    content_suppressed: bool = True

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "error_code": self.error_code,
            "failed_check": self.failed_check,
            "case_label": self.case_label,
            "file_role": self.file_role,
            "content_suppressed": self.content_suppressed,
        }


@dataclass(frozen=True)
class ArtifactWriterFixtureValidationResult:
    writer_status: str
    reason_codes: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)
    failure_categories: list[str] = field(default_factory=list)
    checked_files_count: int = 0
    case_category: str | None = None
    case_name: str | None = None
    case_label: str | None = None
    request_id: str | None = None
    generator_result_id: str | None = None
    policy_id: str | None = None
    artifact_id: str | None = None
    manifest_id: str | None = None
    artifact_writer_version: str | None = None
    artifact_policy_label: str | None = None
    request_schema_version: str | None = None
    pointer_schema_version: str | None = None
    expected_schema_version: str | None = None
    result_schema_version: str | None = None
    artifact_flags: dict[str, bool] = field(default_factory=dict)
    safety_flags: dict[str, bool] = field(default_factory=dict)
    count_summary: dict[str, int] = field(default_factory=dict)
    safe_summary: str | None = None
    validation_schema_version: str = VALIDATION_SCHEMA_VERSION

    @property
    def validation_status(self) -> str:
        return self.writer_status

    @property
    def content_suppressed(self) -> bool:
        return self.safety_flags.get("content_suppressed", True)

    @property
    def no_raw_rows(self) -> bool:
        return self.safety_flags.get("no_raw_rows", True)

    @property
    def no_logits_dump(self) -> bool:
        return self.safety_flags.get("no_logits_dump", True)

    @property
    def no_private_paths(self) -> bool:
        return self.safety_flags.get("no_private_paths", True)

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "validation_schema_version": self.validation_schema_version,
            "writer_status": self.writer_status,
            "validation_status": self.validation_status,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "failure_categories": list(self.failure_categories),
            "checked_files_count": self.checked_files_count,
            "case_category": self.case_category,
            "case_name": self.case_name,
            "case_label": self.case_label,
            "request_id": self.request_id,
            "generator_result_id": self.generator_result_id,
            "policy_id": self.policy_id,
            "artifact_id": self.artifact_id,
            "manifest_id": self.manifest_id,
            "artifact_writer_version": self.artifact_writer_version,
            "artifact_policy_label": self.artifact_policy_label,
            "request_schema_version": self.request_schema_version,
            "pointer_schema_version": self.pointer_schema_version,
            "expected_schema_version": self.expected_schema_version,
            "result_schema_version": self.result_schema_version,
            "artifact_flags": dict(self.artifact_flags),
            "safety_flags": dict(self.safety_flags),
            "count_summary": dict(self.count_summary),
            "safe_summary": self.safe_summary,
            "content_suppressed": self.content_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "no_logits_dump": self.no_logits_dump,
            "no_private_paths": self.no_private_paths,
        }


@dataclass(frozen=True)
class ArtifactWriterFixtureRootValidationResult:
    mode: str = "fixture_root"
    total_cases: int = 0
    valid_cases: int = 0
    invalid_cases: int = 0
    matched_cases: int = 0
    mismatched_cases: int = 0
    input_error_cases: int = 0
    reason_code_counts: dict[str, int] = field(default_factory=dict)
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
    manifest_body_suppression_checked: bool = True
    output_path_safety_checked: bool = True
    validation_schema_version: str = VALIDATION_SCHEMA_VERSION

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "validation_schema_version": self.validation_schema_version,
            "mode": self.mode,
            "total_cases": self.total_cases,
            "valid_cases": self.valid_cases,
            "invalid_cases": self.invalid_cases,
            "matched_cases": self.matched_cases,
            "mismatched_cases": self.mismatched_cases,
            "input_error_cases": self.input_error_cases,
            "reason_code_counts": dict(self.reason_code_counts),
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
            "manifest_body_suppression_checked": (
                self.manifest_body_suppression_checked
            ),
            "output_path_safety_checked": self.output_path_safety_checked,
        }


def discover_artifact_writer_fixture_cases(fixture_root: Path) -> list[Path]:
    root = Path(fixture_root)
    cases: list[Path] = []
    for category in ("valid", "invalid"):
        category_dir = root / category
        if category_dir.exists():
            cases.extend(path for path in category_dir.iterdir() if path.is_dir())
    return sorted(cases)


def load_artifact_writer_fixture_case(case_dir: Path) -> ArtifactWriterFixtureCase:
    case_dir = Path(case_dir)
    case_category = case_dir.parent.name
    case_name = case_dir.name
    case_label = f"{case_category}/{case_name}"
    request = _read_json(case_dir / ARTIFACT_WRITER_REQUEST_FILE)
    pointer = _read_json(case_dir / GENERATOR_RESULT_POINTER_FILE)
    expected = _read_json(case_dir / EXPECTED_ARTIFACT_WRITER_RESULT_FILE)
    return ArtifactWriterFixtureCase(
        case_dir=case_dir,
        case_category=case_category,
        case_name=case_name,
        case_label=case_label,
        request_metadata=request,
        generator_result_pointer_metadata=pointer,
        expected_result_metadata=expected,
        request_schema_version=request.get("schema_version"),
        pointer_schema_version=pointer.get("schema_version"),
        expected_schema_version=expected.get("schema_version"),
        result_schema_version=expected.get("result_schema_version"),
    )


def load_expected_artifact_writer_result(case_dir: Path) -> dict[str, Any]:
    case_dir = Path(case_dir)
    expected_path = (
        case_dir
        if case_dir.name == EXPECTED_ARTIFACT_WRITER_RESULT_FILE
        else case_dir / EXPECTED_ARTIFACT_WRITER_RESULT_FILE
    )
    return _read_json(expected_path)


def validate_artifact_writer_fixture_case(
    case: ArtifactWriterFixtureCase | Path,
) -> ArtifactWriterFixtureValidationResult:
    try:
        fixture = (
            load_artifact_writer_fixture_case(Path(case))
            if not isinstance(case, ArtifactWriterFixtureCase)
            else case
        )
        shape_errors = _validate_required_file_shape(fixture.case_dir)
        if shape_errors:
            return _input_error_result(fixture, shape_errors)
        return _build_expected_contract_result(fixture)
    except (OSError, json.JSONDecodeError, ValueError):
        case_dir = (
            Path(case) if not isinstance(case, ArtifactWriterFixtureCase) else case.case_dir
        )
        return ArtifactWriterFixtureValidationResult(
            writer_status="input_error",
            reason_codes=["malformed_fixture_file"],
            failed_checks=["json_parse_or_fixture_shape"],
            failure_categories=["input_error"],
            checked_files_count=_count_existing_required_files(case_dir),
            case_category=case_dir.parent.name,
            case_name=case_dir.name,
            case_label=f"{case_dir.parent.name}/{case_dir.name}",
        )


def compare_artifact_writer_fixture_to_expected(
    case: ArtifactWriterFixtureCase | ArtifactWriterFixtureValidationResult | Path,
) -> list[ArtifactWriterFixtureComparisonResult]:
    fixture = _coerce_fixture_case(case)
    result = (
        case
        if isinstance(case, ArtifactWriterFixtureValidationResult)
        else validate_artifact_writer_fixture_case(fixture)
    )
    expected = fixture.expected_result_metadata
    actual = result.to_safe_dict()
    field_map = {
        "writer_status": "writer_status",
        "reason_codes": "reason_codes",
        "failed_checks": "failed_checks",
        "request_id": "request_id",
        "generator_result_id": "generator_result_id",
        "policy_id": "policy_id",
        "artifact_id": "artifact_id",
        "manifest_id": "manifest_id",
        "artifact_writer_version": "artifact_writer_version",
        "artifact_policy_label": "artifact_policy_label",
        "artifact_flags": "artifact_flags",
        "safety_flags": "safety_flags",
        "count_summary": "count_summary",
        "safe_summary": "safe_summary",
        "result_schema_version": "result_schema_version",
    }
    mismatches: list[ArtifactWriterFixtureComparisonResult] = []
    for expected_field, actual_field in field_map.items():
        if expected.get(expected_field) != actual.get(actual_field):
            mismatches.append(
                ArtifactWriterFixtureComparisonResult(
                    field_name=expected_field,
                    expected_value=expected.get(expected_field),
                    actual_value=actual.get(actual_field),
                )
            )

    for error in _validate_case_contract(fixture):
        mismatches.append(
            ArtifactWriterFixtureComparisonResult(
                field_name=error,
                expected_value="contract_ok",
                actual_value="contract_mismatch",
            )
        )
    return mismatches


def validate_artifact_writer_fixture_root(
    fixture_root: Path,
) -> ArtifactWriterFixtureRootValidationResult:
    root = Path(fixture_root)
    root_errors = _validate_root_shape(root)
    if root_errors:
        return ArtifactWriterFixtureRootValidationResult(
            total_cases=0,
            matched_cases=0,
            mismatched_cases=0,
            input_error_cases=1,
            reason_code_counts=dict(Counter(root_errors)),
        )

    matched_cases = 0
    mismatched_cases = 0
    input_error_cases = 0
    valid_cases = 0
    invalid_cases = 0
    reason_counter: Counter[str] = Counter()

    for case_dir in discover_artifact_writer_fixture_cases(root):
        if case_dir.parent.name == "valid":
            valid_cases += 1
        elif case_dir.parent.name == "invalid":
            invalid_cases += 1
        result = validate_artifact_writer_fixture_case(case_dir)
        reason_counter.update(result.reason_codes)
        if result.writer_status == "input_error":
            input_error_cases += 1
            continue
        mismatches = compare_artifact_writer_fixture_to_expected(case_dir)
        if mismatches:
            mismatched_cases += 1
        else:
            matched_cases += 1

    return ArtifactWriterFixtureRootValidationResult(
        total_cases=matched_cases + mismatched_cases + input_error_cases,
        valid_cases=valid_cases,
        invalid_cases=invalid_cases,
        matched_cases=matched_cases,
        mismatched_cases=mismatched_cases,
        input_error_cases=input_error_cases,
        reason_code_counts=dict(sorted(reason_counter.items())),
    )


def summarize_artifact_writer_fixture_validation_result(
    result: (
        ArtifactWriterFixtureValidationResult
        | ArtifactWriterFixtureRootValidationResult
        | ArtifactWriterFixtureSafetySummary
        | ArtifactWriterFixtureInputError
    ),
) -> dict[str, Any]:
    return result.to_safe_dict()


def scan_artifact_writer_fixture_for_forbidden_markers(
    case: ArtifactWriterFixtureCase | Path,
) -> ArtifactWriterFixtureSafetySummary:
    fixture = (
        load_artifact_writer_fixture_case(Path(case))
        if not isinstance(case, ArtifactWriterFixtureCase)
        else case
    )
    return _scan_forbidden_payloads(
        [
            fixture.request_metadata,
            fixture.generator_result_pointer_metadata,
            fixture.expected_result_metadata,
        ]
    )


def _coerce_fixture_case(
    case: ArtifactWriterFixtureCase | ArtifactWriterFixtureValidationResult | Path,
) -> ArtifactWriterFixtureCase:
    if isinstance(case, ArtifactWriterFixtureCase):
        return case
    if isinstance(case, ArtifactWriterFixtureValidationResult):
        if case.case_category is None or case.case_name is None:
            raise ValueError("cannot_load_case_from_result_without_label")
        raise ValueError("case_result_requires_explicit_expected_fixture_case")
    return load_artifact_writer_fixture_case(Path(case))


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
        if path.is_file() and path.name != "README.md" and path.suffix != ".json":
            errors.append("unexpected_file_extension")

    cases = discover_artifact_writer_fixture_cases(root)
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
            fixture = load_artifact_writer_fixture_case(case_dir)
        except (OSError, json.JSONDecodeError, ValueError):
            errors.append("malformed_json_file")
            continue
        scan = scan_artifact_writer_fixture_for_forbidden_markers(fixture)
        errors.extend(scan.reason_codes)
    return sorted(set(errors))


def _validate_required_file_shape(case_dir: Path) -> list[str]:
    errors: list[str] = []
    found_files = [path.name for path in case_dir.iterdir() if path.is_file()]
    for file_name in REQUIRED_FILES:
        if file_name not in found_files:
            errors.append("missing_required_file")
    if sorted(set(found_files) - set(REQUIRED_FILES)):
        errors.append("unexpected_case_file")
    return errors


def _validate_case_contract(fixture: ArtifactWriterFixtureCase) -> list[str]:
    errors: list[str] = []
    request = fixture.request_metadata
    pointer = fixture.generator_result_pointer_metadata
    expected = fixture.expected_result_metadata
    expected_reason = EXPECTED_INVALID_REASONS.get(fixture.case_label)

    errors.extend(_missing_fields(request, REQUIRED_REQUEST_FIELDS))
    errors.extend(_missing_fields(pointer, REQUIRED_POINTER_FIELDS))
    errors.extend(_missing_fields(expected, REQUIRED_EXPECTED_FIELDS))

    if fixture.case_label == "invalid/missing_required_field":
        errors = [
            error
            for error in errors
            if error != "missing_required_field:artifact_id"
        ]
    if errors:
        return sorted(set(errors))

    if (
        request.get("schema_version") != REQUEST_SCHEMA_VERSION
        and expected_reason != "unknown_schema_version"
    ):
        errors.append("unknown_request_schema_version")
    if pointer.get("schema_version") != POINTER_SCHEMA_VERSION:
        errors.append("unknown_pointer_schema_version")
    if expected.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        errors.append("unknown_expected_schema_version")
    if expected.get("result_schema_version") != RESULT_SCHEMA_VERSION:
        errors.append("unknown_result_schema_version")

    errors.extend(_validate_type_shapes(request, pointer, expected))
    errors.extend(_validate_category_contract(fixture))
    errors.extend(_validate_artifact_flags(expected.get("artifact_flags")))
    errors.extend(_validate_safety_flags(expected.get("safety_flags")))
    errors.extend(
        _validate_count_summary(
            expected.get("count_summary"),
            require_positive=fixture.case_category == "valid",
        )
    )
    errors.extend(_validate_identity_links(request, pointer, expected))
    errors.extend(scan_artifact_writer_fixture_for_forbidden_markers(fixture).reason_codes)
    return sorted(set(errors))


def _validate_type_shapes(
    request: dict[str, Any],
    pointer: dict[str, Any],
    expected: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    for field_name in ("validation_reference_ids", "expected_reason_codes", "expected_failed_checks"):
        if not isinstance(request.get(field_name), list):
            errors.append(f"invalid_list_field:{field_name}")
    for field_name in ("validation_reference_ids", "safe_pointer_notes"):
        if not isinstance(pointer.get(field_name), list):
            errors.append(f"invalid_pointer_list_field:{field_name}")
    for field_name in ("reason_codes", "failed_checks"):
        if not isinstance(expected.get(field_name), list):
            errors.append(f"invalid_expected_list_field:{field_name}")
    for field_name in (
        "requested_artifact_body",
        "requested_file_writing",
        "requested_manifest",
        "synthetic_only",
        "no_oracle_required",
    ):
        if not isinstance(request.get(field_name), bool):
            errors.append(f"invalid_bool_field:{field_name}")
    for field_name in ("synthetic_only", "no_oracle_required", "content_suppressed"):
        if not isinstance(pointer.get(field_name), bool):
            errors.append(f"invalid_pointer_bool_field:{field_name}")
    for field_name in ("artifact_flags", "safety_flags", "count_summary"):
        if not isinstance(expected.get(field_name), dict):
            errors.append(f"invalid_expected_object_field:{field_name}")
    return errors


def _validate_category_contract(fixture: ArtifactWriterFixtureCase) -> list[str]:
    errors: list[str] = []
    request = fixture.request_metadata
    expected = fixture.expected_result_metadata
    if fixture.case_category == "valid":
        if fixture.case_label not in VALID_CASE_LABELS:
            errors.append("unknown_valid_fixture_case")
        if expected.get("writer_status") != "pass":
            errors.append("valid_case_status_mismatch")
        if request.get("expected_status") != "pass":
            errors.append("valid_case_request_status_mismatch")
        if expected.get("reason_codes") != [] or request.get("expected_reason_codes") != []:
            errors.append("valid_case_reason_codes_not_empty")
        if expected.get("failed_checks") != [] or request.get("expected_failed_checks") != []:
            errors.append("valid_case_failed_checks_not_empty")
        if expected.get("safe_summary") != "metadata_only_artifact_writer_result":
            errors.append("valid_case_safe_summary_mismatch")
    elif fixture.case_category == "invalid":
        expected_reason = EXPECTED_INVALID_REASONS.get(fixture.case_label)
        if expected_reason is None:
            errors.append("unknown_invalid_fixture_case")
        if expected.get("writer_status") != "fail":
            errors.append("invalid_case_status_mismatch")
        if request.get("expected_status") != "fail":
            errors.append("invalid_case_request_status_mismatch")
        if expected_reason is not None:
            if expected.get("reason_codes") != [expected_reason]:
                errors.append("invalid_case_reason_code_mismatch")
            if request.get("expected_reason_codes") != [expected_reason]:
                errors.append("invalid_case_request_reason_code_mismatch")
            if expected.get("failed_checks") != [expected_reason]:
                errors.append("invalid_case_failed_check_mismatch")
            if request.get("expected_failed_checks") != [expected_reason]:
                errors.append("invalid_case_request_failed_check_mismatch")
        if expected.get("safe_summary") != "fail_closed_metadata_only_artifact_writer_result":
            errors.append("invalid_case_safe_summary_mismatch")
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
        elif value.get(field_name) is not True:
            errors.append(f"safety_flag_value_mismatch:{field_name}")
    return errors


def _validate_count_summary(value: Any, *, require_positive: bool) -> list[str]:
    if not isinstance(value, dict):
        return ["invalid_count_summary"]
    errors: list[str] = []
    for field_name in REQUIRED_COUNT_SUMMARY_FIELDS:
        if field_name not in value:
            errors.append(f"missing_count_summary_field:{field_name}")
        elif not isinstance(value.get(field_name), int):
            errors.append(f"count_summary_not_int:{field_name}")
        elif value[field_name] < 0:
            errors.append(f"count_summary_negative:{field_name}")
    for field_name in EXPECTED_ZERO_COUNT_FIELDS:
        if value.get(field_name) != 0:
            errors.append(f"count_summary_zero_mismatch:{field_name}")
    if value.get("validation_reference_count", 0) < 1:
        errors.append("validation_reference_count_too_low")
    if require_positive:
        if value.get("artifact_metadata_field_count", 0) <= 0:
            errors.append("artifact_metadata_field_count_too_low")
        if value.get("manifest_metadata_field_count", 0) <= 0:
            errors.append("manifest_metadata_field_count_too_low")
    return errors


def _validate_identity_links(
    request: dict[str, Any],
    pointer: dict[str, Any],
    expected: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    expected_reason_codes = expected.get("reason_codes")
    allow_missing_artifact_id = expected_reason_codes == ["missing_required_field"]
    direct_fields = (
        "request_id",
        "generator_result_id",
        "policy_id",
        "artifact_id",
        "manifest_id",
        "artifact_writer_version",
        "artifact_policy_label",
    )
    for field_name in direct_fields:
        if field_name in request and field_name in expected:
            if expected.get(field_name) != request.get(field_name):
                errors.append(f"identity_mismatch:{field_name}")
    if pointer.get("generator_result_id") != request.get("generator_result_id"):
        errors.append("pointer_generator_result_id_mismatch")
    if pointer.get("policy_id") != request.get("policy_id"):
        errors.append("pointer_policy_id_mismatch")
    if (
        pointer.get("artifact_id") != request.get("artifact_id")
        and not allow_missing_artifact_id
    ):
        errors.append("pointer_artifact_id_mismatch")
    if pointer.get("validation_reference_ids") != request.get("validation_reference_ids"):
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
    fixture: ArtifactWriterFixtureCase,
) -> ArtifactWriterFixtureValidationResult:
    request = fixture.request_metadata
    expected = fixture.expected_result_metadata
    return ArtifactWriterFixtureValidationResult(
        writer_status=expected.get("writer_status", "input_error"),
        reason_codes=list(expected.get("reason_codes", [])),
        failed_checks=list(expected.get("failed_checks", [])),
        failure_categories=(
            [] if expected.get("writer_status") == "pass" else ["expected_failure"]
        ),
        checked_files_count=len(REQUIRED_FILES),
        case_category=fixture.case_category,
        case_name=fixture.case_name,
        case_label=fixture.case_label,
        request_id=expected.get("request_id"),
        generator_result_id=expected.get("generator_result_id"),
        policy_id=expected.get("policy_id"),
        artifact_id=expected.get("artifact_id"),
        manifest_id=expected.get("manifest_id"),
        artifact_writer_version=expected.get("artifact_writer_version"),
        artifact_policy_label=expected.get("artifact_policy_label"),
        request_schema_version=request.get("schema_version"),
        pointer_schema_version=fixture.pointer_schema_version,
        expected_schema_version=fixture.expected_schema_version,
        result_schema_version=expected.get("result_schema_version"),
        artifact_flags=dict(expected.get("artifact_flags", {})),
        safety_flags=dict(expected.get("safety_flags", {})),
        count_summary=dict(expected.get("count_summary", {})),
        safe_summary=expected.get("safe_summary"),
    )


def _input_error_result(
    fixture: ArtifactWriterFixtureCase,
    errors: list[str],
) -> ArtifactWriterFixtureValidationResult:
    return ArtifactWriterFixtureValidationResult(
        writer_status="input_error",
        reason_codes=["fixture_contract_error"],
        failed_checks=sorted(errors),
        failure_categories=["input_error"],
        checked_files_count=_count_existing_required_files(fixture.case_dir),
        case_category=fixture.case_category,
        case_name=fixture.case_name,
        case_label=fixture.case_label,
        request_id=fixture.request_metadata.get("request_id"),
        generator_result_id=fixture.request_metadata.get("generator_result_id"),
        request_schema_version=fixture.request_schema_version,
        pointer_schema_version=fixture.pointer_schema_version,
        expected_schema_version=fixture.expected_schema_version,
        result_schema_version=fixture.result_schema_version,
    )


def _count_existing_required_files(case_dir: Path) -> int:
    return sum(1 for file_name in REQUIRED_FILES if (case_dir / file_name).is_file())


def _scan_forbidden_payloads(values: list[Any]) -> ArtifactWriterFixtureSafetySummary:
    reason_codes: list[str] = []
    failed_checks: list[str] = []

    def visit(value: Any, key_context: str | None = None) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                key_text = str(key)
                key_lower = key_text.lower()
                if key_lower in SAFE_MARKER_KEYS:
                    if not isinstance(nested, bool):
                        reason_codes.append("unsafe_marker_value")
                        failed_checks.append(key_lower)
                    continue
                if key_lower in FORBIDDEN_PAYLOAD_KEYS:
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
            if any(marker in lower for marker in RAW_LOG_MARKERS):
                reason_codes.append("raw_log_marker_payload")
                failed_checks.append("raw_log_scan")

    for item in values:
        visit(item)

    return ArtifactWriterFixtureSafetySummary(
        reason_codes=sorted(set(reason_codes)),
        failed_checks=sorted(set(failed_checks)),
    )


def _is_safe_marker_string(value: str, key_context: str | None) -> bool:
    if key_context in SAFE_STRING_CONTEXT_KEYS:
        return True
    if value.startswith("valid/") or value.startswith("invalid/"):
        return True
    if value.startswith("synthetic_"):
        return True
    if value.startswith("learner_state_"):
        return True
    if value.startswith("frozen_policy_"):
        return True
    if value.startswith("metadata_"):
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
