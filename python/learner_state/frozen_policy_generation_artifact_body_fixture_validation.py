"""Safe synthetic artifact body fixture validation.

This module validates metadata-only frozen policy generation artifact body
fixtures. It does not implement artifact body generation, generate payload
bodies, write artifact files, write manifests, train models, or compute
metrics.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

ARTIFACT_BODY_REQUEST_FILE = "artifact_body_request.json"
ARTIFACT_WRITER_RESULT_POINTER_FILE = "artifact_writer_result_pointer.json"
EXPECTED_ARTIFACT_BODY_RESULT_FILE = "expected_artifact_body_result.json"

REQUEST_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_request_v0.1"
)
POINTER_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_writer_result_pointer_v0.1"
)
EXPECTED_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_expected_result_v0.1"
)
RESULT_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_result_v0.1"
)
VALIDATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_fixture_validation_v0.1"
)

EXPECTED_VALID_CASES = 4
EXPECTED_INVALID_CASES = 14
EXPECTED_TOTAL_CASES = 18
EXPECTED_JSON_FILE_COUNT = EXPECTED_TOTAL_CASES * 3
DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/learner_state_frozen_policy_generation_artifact_body"
)

VALID_CASE_LABELS = frozenset(
    {
        "valid/minimal_suppressed_metadata_only_body",
        "valid/safe_metadata_body_summary",
        "valid/safe_reason_code_body_summary",
        "valid/safe_validation_reference_body_summary",
    }
)

EXPECTED_INVALID_REASONS = {
    "invalid/raw_learner_text_in_artifact_body": (
        "raw_learner_text_in_artifact_body"
    ),
    "invalid/raw_rows_in_artifact_body": "raw_rows_in_artifact_body",
    "invalid/logits_dump_in_artifact_body": "logits_dump_in_artifact_body",
    "invalid/private_path_in_artifact_body": "private_path_in_artifact_body",
    "invalid/performance_claim_in_artifact_body": (
        "performance_claim_in_artifact_body"
    ),
    "invalid/request_body_leakage": "request_body_leakage",
    "invalid/pointer_body_leakage": "pointer_body_leakage",
    "invalid/expected_result_body_leakage": "expected_result_body_leakage",
    "invalid/generated_policy_body_leakage": "generated_policy_body_leakage",
    "invalid/manifest_body_leakage": "manifest_body_leakage",
    "invalid/unsafe_artifact_body_schema": "unsafe_artifact_body_schema",
    "invalid/missing_synthetic_notice": "missing_synthetic_notice",
    "invalid/missing_no_oracle_notice": "missing_no_oracle_notice",
    "invalid/unknown_artifact_body_schema_version": (
        "unknown_artifact_body_schema_version"
    ),
}

EXPECTED_REASON_MARKERS = {
    "raw_learner_text_in_artifact_body": "raw_learner_text_marker_present",
    "raw_rows_in_artifact_body": "raw_rows_marker_present",
    "logits_dump_in_artifact_body": "logits_dump_marker_present",
    "private_path_in_artifact_body": "private_path_marker_present",
    "performance_claim_in_artifact_body": "performance_claim_marker_present",
    "request_body_leakage": "request_body_marker_present",
    "pointer_body_leakage": "pointer_body_marker_present",
    "expected_result_body_leakage": "expected_result_body_marker_present",
    "generated_policy_body_leakage": "generated_policy_body_marker_present",
    "manifest_body_leakage": "manifest_body_marker_present",
    "unsafe_artifact_body_schema": "unsafe_schema_marker_present",
    "missing_synthetic_notice": "missing_synthetic_notice_marker_present",
    "missing_no_oracle_notice": "missing_no_oracle_notice_marker_present",
    "unknown_artifact_body_schema_version": "unknown_schema_version_marker_present",
}

SAFE_MARKER_KEYS = frozenset(EXPECTED_REASON_MARKERS.values())

REQUIRED_FILES = (
    ARTIFACT_BODY_REQUEST_FILE,
    ARTIFACT_WRITER_RESULT_POINTER_FILE,
    EXPECTED_ARTIFACT_BODY_RESULT_FILE,
)

REQUIRED_REQUEST_FIELDS = (
    "schema_version",
    "case_id",
    "category",
    "artifact_body_id",
    "artifact_id",
    "manifest_id",
    "writer_version",
    "requested_body_mode",
    "requested_body_status",
    "synthetic_only_notice_present",
    "no_oracle_notice_present",
    "validation_reference_ids",
    "safe_section_keys",
    "safe_marker_flags",
)

REQUIRED_POINTER_FIELDS = (
    "schema_version",
    "case_id",
    "category",
    "writer_result_pointer_id",
    "writer_result_schema_version",
    "writer_status",
    "writer_result_safe_summary",
    "artifact_id",
    "manifest_id",
    "validation_reference_ids",
    "content_suppressed",
    "no_raw_rows",
    "no_logits_dump",
    "no_private_paths",
    "no_performance_claims",
    "generated_artifact_written",
    "artifact_body_suppressed",
    "manifest_body_suppressed",
)

REQUIRED_EXPECTED_FIELDS = (
    "schema_version",
    "result_schema_version",
    "case_id",
    "category",
    "artifact_body_id",
    "artifact_id",
    "manifest_id",
    "writer_result_pointer_id",
    "writer_version",
    "body_status",
    "validation_status",
    "reason_codes",
    "failed_checks",
    "synthetic_only_notice_present",
    "no_oracle_notice_present",
    "validation_reference_ids",
    "artifact_flags",
    "safety_flags",
    "count_summary",
    "safe_marker_flags",
    "safe_summary",
    "artifact_file_written",
    "manifest_file_written",
)

REQUIRED_ARTIFACT_FLAGS = (
    "artifact_body_file_available",
    "artifact_file_written",
    "body_metadata_available",
    "body_output_suppressed",
    "content_suppressed",
    "manifest_body_available",
    "manifest_file_written",
)

REQUIRED_SAFETY_FLAGS = (
    "artifact_body_audit_checked",
    "artifact_policy_checked",
    "body_suppression_checked",
    "content_suppressed",
    "no_logits_dump",
    "no_oracle_checked",
    "no_performance_claims",
    "no_private_paths",
    "no_raw_rows",
    "synthetic_only_checked",
)

REQUIRED_COUNT_SUMMARY_FIELDS = (
    "body_field_count",
    "expected_body_count",
    "logits_dump_count",
    "manifest_body_count",
    "performance_metric_count",
    "pointer_body_count",
    "private_path_count",
    "raw_row_count",
    "request_body_count",
    "safe_marker_count",
    "validation_reference_count",
)

ZERO_COUNT_FIELDS = (
    "expected_body_count",
    "logits_dump_count",
    "manifest_body_count",
    "performance_metric_count",
    "pointer_body_count",
    "private_path_count",
    "raw_row_count",
    "request_body_count",
)

FORBIDDEN_PAYLOAD_KEYS = frozenset(
    {
        "raw_learner_text",
        "raw_rows",
        "logits",
        "probabilities",
        "private_path",
        "absolute_path",
        "request_body",
        "pointer_body",
        "expected_result_body",
        "generated_policy_body",
        "artifact_body_payload",
        "manifest_body",
        "final_text",
        "observed_after_text",
        "gold_label",
        "expected_action",
        "scoring_feedback_payload",
        "performance_metrics",
    }
)

RAW_LOG_MARKERS = (
    "::group::",
    "::endgroup::",
    "##[group]",
    "##[endgroup]",
    "github actions raw log",
    "full job output",
)

LOCAL_ABSOLUTE_PATH_PATTERN = re.compile(
    r"(^/Users/|^/home/|^/private/|^/var/folders/|^[A-Za-z]:\\)"
)


@dataclass(frozen=True)
class ArtifactBodyFixtureCase:
    case_dir: Path
    case_category: str
    case_name: str
    case_label: str
    artifact_body_request: dict[str, Any]
    writer_result_pointer: dict[str, Any]
    expected_artifact_body_result: dict[str, Any]
    request_schema_version: str | None
    pointer_schema_version: str | None
    expected_schema_version: str | None
    result_schema_version: str | None


@dataclass(frozen=True)
class ArtifactBodySafeMarkerScanResult:
    reason_codes: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)
    marker_true_count: int = 0
    marker_false_count: int = 0
    marker_non_boolean_count: int = 0
    content_suppressed: bool = True

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "marker_true_count": self.marker_true_count,
            "marker_false_count": self.marker_false_count,
            "marker_non_boolean_count": self.marker_non_boolean_count,
            "content_suppressed": self.content_suppressed,
        }


@dataclass(frozen=True)
class ArtifactBodyForbiddenScanResult:
    reason_codes: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)
    forbidden_key_count: int = 0
    forbidden_value_count: int = 0
    content_suppressed: bool = True

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "forbidden_key_count": self.forbidden_key_count,
            "forbidden_value_count": self.forbidden_value_count,
            "content_suppressed": self.content_suppressed,
        }


@dataclass(frozen=True)
class ArtifactBodyFixtureSafetySummary:
    content_suppressed: bool = True
    no_raw_rows: bool = True
    no_logits_dump: bool = True
    no_private_paths: bool = True
    no_performance_claims: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    artifact_policy_checked: bool = True
    body_suppression_checked: bool = True
    artifact_body_audit_checked: bool = True
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
            "artifact_body_audit_checked": self.artifact_body_audit_checked,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
        }


@dataclass(frozen=True)
class ArtifactBodyFixtureInputError:
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
class ArtifactBodyFixtureComparisonResult:
    field_name: str
    expected_value: Any
    actual_value: Any

    @property
    def mismatches(self) -> list[str]:
        if isinstance(self.actual_value, list):
            return [str(item) for item in self.actual_value]
        if self.actual_value == "match":
            return []
        return [str(self.field_name)]

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "field_name": self.field_name,
            "expected_value": _safe_scalar_or_collection(self.expected_value),
            "actual_value": _safe_scalar_or_collection(self.actual_value),
        }


@dataclass(frozen=True)
class ArtifactBodyFixtureValidationResult:
    validation_status: str
    body_status: str | None = None
    reason_codes: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)
    failure_categories: list[str] = field(default_factory=list)
    checked_files_count: int = 0
    case_category: str | None = None
    case_name: str | None = None
    case_label: str | None = None
    case_id: str | None = None
    artifact_body_id: str | None = None
    artifact_id: str | None = None
    manifest_id: str | None = None
    writer_result_pointer_id: str | None = None
    writer_version: str | None = None
    request_schema_version: str | None = None
    pointer_schema_version: str | None = None
    expected_schema_version: str | None = None
    result_schema_version: str | None = None
    synthetic_only_notice_present: bool | None = None
    no_oracle_notice_present: bool | None = None
    validation_reference_ids: list[str] = field(default_factory=list)
    artifact_flags: dict[str, bool] = field(default_factory=dict)
    safety_flags: dict[str, bool] = field(default_factory=dict)
    count_summary: dict[str, int] = field(default_factory=dict)
    safe_marker_flags: dict[str, bool] = field(default_factory=dict)
    safe_summary: str | None = None
    artifact_file_written: bool = False
    manifest_file_written: bool = False
    validation_schema_version: str = VALIDATION_SCHEMA_VERSION

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

    @property
    def no_performance_claims(self) -> bool:
        return self.safety_flags.get("no_performance_claims", True)

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "validation_schema_version": self.validation_schema_version,
            "validation_status": self.validation_status,
            "body_status": self.body_status,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "failure_categories": list(self.failure_categories),
            "checked_files_count": self.checked_files_count,
            "case_category": self.case_category,
            "case_name": self.case_name,
            "case_label": self.case_label,
            "case_id": self.case_id,
            "artifact_body_id": self.artifact_body_id,
            "artifact_id": self.artifact_id,
            "manifest_id": self.manifest_id,
            "writer_result_pointer_id": self.writer_result_pointer_id,
            "writer_version": self.writer_version,
            "request_schema_version": self.request_schema_version,
            "pointer_schema_version": self.pointer_schema_version,
            "expected_schema_version": self.expected_schema_version,
            "result_schema_version": self.result_schema_version,
            "synthetic_only_notice_present": self.synthetic_only_notice_present,
            "no_oracle_notice_present": self.no_oracle_notice_present,
            "validation_reference_ids": list(self.validation_reference_ids),
            "artifact_flags": dict(self.artifact_flags),
            "safety_flags": dict(self.safety_flags),
            "count_summary": dict(self.count_summary),
            "safe_marker_flags": dict(self.safe_marker_flags),
            "safe_summary": self.safe_summary,
            "artifact_file_written": self.artifact_file_written,
            "manifest_file_written": self.manifest_file_written,
            "content_suppressed": self.content_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "no_logits_dump": self.no_logits_dump,
            "no_private_paths": self.no_private_paths,
            "no_performance_claims": self.no_performance_claims,
        }


@dataclass(frozen=True)
class ArtifactBodyFixtureRootValidationResult:
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
    artifact_body_audit_checked: bool = True
    request_body_count: int = 0
    pointer_body_count: int = 0
    expected_body_count: int = 0
    raw_row_count: int = 0
    logits_dump_count: int = 0
    private_path_count: int = 0
    performance_metric_count: int = 0
    manifest_body_count: int = 0
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
            "artifact_body_audit_checked": self.artifact_body_audit_checked,
            "request_body_count": self.request_body_count,
            "pointer_body_count": self.pointer_body_count,
            "expected_body_count": self.expected_body_count,
            "raw_row_count": self.raw_row_count,
            "logits_dump_count": self.logits_dump_count,
            "private_path_count": self.private_path_count,
            "performance_metric_count": self.performance_metric_count,
            "manifest_body_count": self.manifest_body_count,
        }


def discover_fixture_cases(root: Path) -> list[ArtifactBodyFixtureCase]:
    return [load_artifact_body_fixture_case(case_dir) for case_dir in _case_dirs(root)]


def load_artifact_body_request(path: Path) -> dict[str, Any]:
    return _read_json(path)


def load_writer_result_pointer(path: Path) -> dict[str, Any]:
    return _read_json(path)


def load_expected_artifact_body_result(path: Path) -> dict[str, Any]:
    return _read_json(path)


def load_artifact_body_fixture_case(case_dir: Path) -> ArtifactBodyFixtureCase:
    case_dir = Path(case_dir)
    case_category = case_dir.parent.name
    case_name = case_dir.name
    case_label = f"{case_category}/{case_name}"
    request = load_artifact_body_request(case_dir / ARTIFACT_BODY_REQUEST_FILE)
    pointer = load_writer_result_pointer(
        case_dir / ARTIFACT_WRITER_RESULT_POINTER_FILE
    )
    expected = load_expected_artifact_body_result(
        case_dir / EXPECTED_ARTIFACT_BODY_RESULT_FILE
    )
    return ArtifactBodyFixtureCase(
        case_dir=case_dir,
        case_category=case_category,
        case_name=case_name,
        case_label=case_label,
        artifact_body_request=request,
        writer_result_pointer=pointer,
        expected_artifact_body_result=expected,
        request_schema_version=request.get("schema_version"),
        pointer_schema_version=pointer.get("schema_version"),
        expected_schema_version=expected.get("schema_version"),
        result_schema_version=expected.get("result_schema_version"),
    )


def validate_artifact_body_fixture_case(
    case: ArtifactBodyFixtureCase | Path,
) -> ArtifactBodyFixtureValidationResult:
    case_dir = (
        case.case_dir if isinstance(case, ArtifactBodyFixtureCase) else Path(case)
    )
    try:
        shape_errors = _validate_required_file_shape(case_dir)
        if any(error == "missing_required_file" for error in shape_errors):
            return _input_error_result(case_dir, shape_errors)
        fixture = (
            case
            if isinstance(case, ArtifactBodyFixtureCase)
            else load_artifact_body_fixture_case(case_dir)
        )
        if shape_errors:
            return _contract_failure_result(fixture, shape_errors)
        return _build_expected_contract_result(fixture)
    except (OSError, json.JSONDecodeError, ValueError):
        return ArtifactBodyFixtureValidationResult(
            validation_status="input_error",
            body_status="input_error",
            reason_codes=["malformed_fixture_file"],
            failed_checks=["json_parse_or_fixture_shape"],
            failure_categories=["input_error"],
            checked_files_count=_count_existing_required_files(case_dir),
            case_category=case_dir.parent.name,
            case_name=case_dir.name,
            case_label=f"{case_dir.parent.name}/{case_dir.name}",
        )


def validate_artifact_body_fixture_root(
    root: Path,
) -> ArtifactBodyFixtureRootValidationResult:
    root = Path(root)
    root_errors = _validate_root_shape(root)
    if root_errors:
        return ArtifactBodyFixtureRootValidationResult(
            total_cases=0,
            input_error_cases=1,
            reason_code_counts=dict(Counter(root_errors)),
        )

    matched_cases = 0
    mismatched_cases = 0
    input_error_cases = 0
    valid_cases = 0
    invalid_cases = 0
    reason_counter: Counter[str] = Counter()

    for case_dir in _case_dirs(root):
        if case_dir.parent.name == "valid":
            valid_cases += 1
        elif case_dir.parent.name == "invalid":
            invalid_cases += 1
        result = validate_artifact_body_fixture_case(case_dir)
        reason_counter.update(result.reason_codes)
        if result.validation_status == "input_error":
            input_error_cases += 1
            continue
        mismatches = compare_expected_result(
            result.to_safe_dict(),
            load_expected_artifact_body_result(
                case_dir / EXPECTED_ARTIFACT_BODY_RESULT_FILE
            ),
        )
        if mismatches.mismatches:
            mismatched_cases += 1
        else:
            matched_cases += 1

    return ArtifactBodyFixtureRootValidationResult(
        total_cases=matched_cases + mismatched_cases + input_error_cases,
        valid_cases=valid_cases,
        invalid_cases=invalid_cases,
        matched_cases=matched_cases,
        mismatched_cases=mismatched_cases,
        input_error_cases=input_error_cases,
        reason_code_counts=dict(sorted(reason_counter.items())),
    )


def compare_expected_result(
    actual: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> ArtifactBodyFixtureComparisonResult:
    mismatches: list[str] = []
    field_map = {
        "result_schema_version": "result_schema_version",
        "case_id": "case_id",
        "category": "case_category",
        "artifact_body_id": "artifact_body_id",
        "artifact_id": "artifact_id",
        "manifest_id": "manifest_id",
        "writer_result_pointer_id": "writer_result_pointer_id",
        "writer_version": "writer_version",
        "body_status": "body_status",
        "validation_status": "validation_status",
        "reason_codes": "reason_codes",
        "failed_checks": "failed_checks",
        "synthetic_only_notice_present": "synthetic_only_notice_present",
        "no_oracle_notice_present": "no_oracle_notice_present",
        "validation_reference_ids": "validation_reference_ids",
        "artifact_flags": "artifact_flags",
        "safety_flags": "safety_flags",
        "count_summary": "count_summary",
        "safe_marker_flags": "safe_marker_flags",
        "safe_summary": "safe_summary",
        "artifact_file_written": "artifact_file_written",
        "manifest_file_written": "manifest_file_written",
    }
    for expected_field, actual_field in field_map.items():
        expected_value = expected.get(expected_field)
        actual_value = actual.get(actual_field)
        if expected_field in {
            "reason_codes",
            "failed_checks",
            "validation_reference_ids",
        }:
            expected_value = sorted(expected_value or [])
            actual_value = sorted(actual_value or [])
        if expected_value != actual_value:
            mismatches.append(expected_field)
    return ArtifactBodyFixtureComparisonResult(
        field_name="expected_result_metadata",
        expected_value="match",
        actual_value="match" if not mismatches else sorted(mismatches),
    )


def scan_safe_markers(payload: Mapping[str, Any]) -> ArtifactBodySafeMarkerScanResult:
    marker_values = _collect_marker_values(payload)
    reason_codes: list[str] = []
    failed_checks: list[str] = []
    marker_true_count = 0
    marker_false_count = 0
    marker_non_boolean_count = 0
    for marker_name, marker_value in marker_values:
        if marker_name not in SAFE_MARKER_KEYS:
            reason_codes.append("unknown_safe_marker")
            failed_checks.append("safe_marker_name")
        if isinstance(marker_value, bool):
            if marker_value:
                marker_true_count += 1
            else:
                marker_false_count += 1
        else:
            marker_non_boolean_count += 1
            reason_codes.append("non_boolean_safe_marker")
            failed_checks.append("safe_marker_boolean")
    return ArtifactBodySafeMarkerScanResult(
        reason_codes=sorted(set(reason_codes)),
        failed_checks=sorted(set(failed_checks)),
        marker_true_count=marker_true_count,
        marker_false_count=marker_false_count,
        marker_non_boolean_count=marker_non_boolean_count,
    )


def scan_forbidden_payload(
    payload: Mapping[str, Any],
) -> ArtifactBodyForbiddenScanResult:
    forbidden_keys = 0
    forbidden_values = 0
    failed_checks: set[str] = set()
    for key, value in _walk_mapping(payload):
        if key in SAFE_MARKER_KEYS:
            continue
        if key in FORBIDDEN_PAYLOAD_KEYS:
            forbidden_keys += 1
            failed_checks.add(key)
        if isinstance(value, str) and _string_contains_forbidden_value(value):
            forbidden_values += 1
            failed_checks.add("forbidden_string_value")
    reason_codes = []
    if forbidden_keys:
        reason_codes.append("forbidden_payload_key")
    if forbidden_values:
        reason_codes.append("forbidden_payload_value")
    return ArtifactBodyForbiddenScanResult(
        reason_codes=reason_codes,
        failed_checks=sorted(failed_checks),
        forbidden_key_count=forbidden_keys,
        forbidden_value_count=forbidden_values,
    )


def summarize_fixture_root(
    result: (
        ArtifactBodyFixtureRootValidationResult
        | ArtifactBodyFixtureValidationResult
        | ArtifactBodyFixtureSafetySummary
        | ArtifactBodyFixtureInputError
        | ArtifactBodyForbiddenScanResult
        | ArtifactBodySafeMarkerScanResult
    ),
) -> dict[str, Any]:
    return result.to_safe_dict()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate frozen policy generation artifact body fixtures with "
            "metadata-only output."
        )
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--fixture-root", type=Path)
    group.add_argument("--fixture-case")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    try:
        if args.fixture_case is not None:
            summary, exit_code = _validate_cli_case(
                args.fixture_case,
                fixture_root=args.fixture_root or DEFAULT_FIXTURE_ROOT,
            )
        else:
            root = args.fixture_root or DEFAULT_FIXTURE_ROOT
            result = validate_artifact_body_fixture_root(root)
            summary = summarize_fixture_root(result)
            exit_code = _cli_exit_code_for_root(result)

        if args.as_json:
            print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
        else:
            print(_format_cli_human_summary(summary))
        return exit_code
    except Exception:
        error_summary = {
            "mode": "artifact_body_fixture_validator",
            "validation_status": "input_error",
            "body_status": "input_error",
            "reason_codes": ["unexpected_internal_error"],
            "failed_checks": ["unexpected_internal_error"],
            "content_suppressed": True,
            "no_raw_rows": True,
            "no_logits_dump": True,
            "no_private_paths": True,
            "validation_schema_version": VALIDATION_SCHEMA_VERSION,
        }
        if args.as_json:
            print(json.dumps(error_summary, sort_keys=True, separators=(",", ":")))
        else:
            print(_format_cli_human_summary(error_summary))
        return 1


def _validate_cli_case(
    case_arg: str,
    *,
    fixture_root: Path,
) -> tuple[dict[str, Any], int]:
    case_dir = _resolve_fixture_case(case_arg, fixture_root=fixture_root)
    if case_dir is None:
        result = ArtifactBodyFixtureValidationResult(
            validation_status="input_error",
            body_status="input_error",
            reason_codes=["missing_fixture_case"],
            failed_checks=["fixture_case_lookup"],
            failure_categories=["input_error"],
            case_label=_safe_case_label(case_arg),
            case_id=_safe_case_label(case_arg),
        )
        return _summarize_cli_case_result(result, ["missing_fixture_case"]), 2

    result = validate_artifact_body_fixture_case(case_dir)
    if result.validation_status == "input_error":
        return _summarize_cli_case_result(result, []), 2

    try:
        expected = load_expected_artifact_body_result(
            case_dir / EXPECTED_ARTIFACT_BODY_RESULT_FILE
        )
        comparison = compare_expected_result(result.to_safe_dict(), expected)
        mismatch_fields = comparison.mismatches
        forbidden_scan = scan_forbidden_payload(expected)
        safe_marker_scan = scan_safe_markers(expected)
        mismatch_fields.extend(
            f"forbidden_payload_scan:{reason}"
            for reason in forbidden_scan.reason_codes
        )
        mismatch_fields.extend(
            f"safe_marker_scan:{reason}"
            for reason in safe_marker_scan.reason_codes
        )
        summary = _summarize_cli_case_result(result, sorted(set(mismatch_fields)))
        return summary, 3 if mismatch_fields else 0
    except (OSError, json.JSONDecodeError, ValueError):
        return _summarize_cli_case_result(result, ["malformed_fixture_file"]), 2


def _resolve_fixture_case(case_arg: str, *, fixture_root: Path) -> Path | None:
    candidate = Path(case_arg)
    if candidate.is_dir():
        return candidate
    if candidate.is_absolute() or candidate.parts[:1] == (".",):
        return None
    rooted_candidate = Path(fixture_root) / candidate
    return rooted_candidate if rooted_candidate.is_dir() else None


def _safe_case_label(case_arg: str) -> str:
    candidate = Path(case_arg)
    if len(candidate.parts) >= 2 and candidate.parts[-2] in {"valid", "invalid"}:
        return f"{candidate.parts[-2]}/{candidate.parts[-1]}"
    if "/" in case_arg and not case_arg.startswith("/"):
        return case_arg
    return "missing_fixture_case"


def _summarize_cli_case_result(
    result: ArtifactBodyFixtureValidationResult,
    mismatch_fields: list[str],
) -> dict[str, Any]:
    payload = result.to_safe_dict()
    safe_marker_flags = payload.pop("safe_marker_flags", {})
    case_id = result.case_label or result.case_id or "unknown_case"
    payload.update(
        {
            "mode": "fixture_case",
            "case_id": case_id,
            "category": result.case_category,
            "matched": result.validation_status != "input_error"
            and not mismatch_fields,
            "mismatch_count": len(mismatch_fields),
            "mismatch_fields": sorted(mismatch_fields),
            "safe_marker_true_count": sum(
                1 for value in safe_marker_flags.values() if value is True
            ),
            "safe_marker_false_count": sum(
                1 for value in safe_marker_flags.values() if value is False
            ),
        }
    )
    return payload


def _cli_exit_code_for_root(result: ArtifactBodyFixtureRootValidationResult) -> int:
    if result.input_error_cases:
        return 2
    if result.mismatched_cases:
        return 3
    return 0


def _format_cli_human_summary(summary: dict[str, Any]) -> str:
    lines: list[str] = []
    for key in sorted(summary):
        lines.append(f"{key}={_format_cli_value(summary[key])}")
    return "\n".join(lines)


def _format_cli_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "none"
    if isinstance(value, list):
        if not value:
            return "none"
        return ",".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return str(value)


def _case_dirs(root: Path) -> list[Path]:
    root = Path(root)
    cases: list[Path] = []
    for category in ("valid", "invalid"):
        category_dir = root / category
        if category_dir.exists():
            cases.extend(path for path in category_dir.iterdir() if path.is_dir())
    return sorted(cases)


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

    cases = _case_dirs(root)
    valid_case_count = len([case for case in cases if case.parent.name == "valid"])
    invalid_case_count = len(
        [case for case in cases if case.parent.name == "invalid"]
    )
    if valid_case_count != EXPECTED_VALID_CASES:
        errors.append("unexpected_valid_case_count")
    if invalid_case_count != EXPECTED_INVALID_CASES:
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
            fixture = load_artifact_body_fixture_case(case_dir)
        except (OSError, json.JSONDecodeError, ValueError):
            errors.append("malformed_json_file")
            continue
        errors.extend(_validate_case_contract(fixture))
    return sorted(set(errors))


def _validate_required_file_shape(case_dir: Path) -> list[str]:
    errors: list[str] = []
    found_files = [path.name for path in case_dir.iterdir() if path.is_file()]
    for file_name in REQUIRED_FILES:
        if file_name not in found_files:
            errors.append("missing_required_file")
    extra_json = [
        file_name
        for file_name in found_files
        if file_name.endswith(".json") and file_name not in REQUIRED_FILES
    ]
    if extra_json:
        errors.append("unexpected_fixture_file")
    extra_non_json = [
        file_name
        for file_name in found_files
        if not file_name.endswith(".json") and file_name not in REQUIRED_FILES
    ]
    if extra_non_json:
        errors.append("unexpected_case_file")
    return sorted(set(errors))


def _validate_case_contract(fixture: ArtifactBodyFixtureCase) -> list[str]:
    errors: list[str] = []
    request = fixture.artifact_body_request
    pointer = fixture.writer_result_pointer
    expected = fixture.expected_artifact_body_result
    expected_reason = EXPECTED_INVALID_REASONS.get(fixture.case_label)

    errors.extend(_missing_fields(request, REQUIRED_REQUEST_FIELDS))
    errors.extend(_missing_fields(pointer, REQUIRED_POINTER_FIELDS))
    errors.extend(_missing_fields(expected, REQUIRED_EXPECTED_FIELDS))
    if errors:
        return sorted(set(errors))

    if (
        request.get("schema_version") != REQUEST_SCHEMA_VERSION
        and expected_reason != "unknown_artifact_body_schema_version"
    ):
        errors.append("unknown_request_schema_version")
    if pointer.get("schema_version") != POINTER_SCHEMA_VERSION:
        errors.append("unknown_pointer_schema_version")
    if expected.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        errors.append("unknown_expected_schema_version")
    if expected.get("result_schema_version") != RESULT_SCHEMA_VERSION:
        errors.append("unknown_result_schema_version")

    errors.extend(_validate_category_contract(fixture))
    errors.extend(_validate_identity_links(request, pointer, expected))
    errors.extend(_validate_artifact_flags(expected.get("artifact_flags")))
    errors.extend(_validate_safety_flags(expected.get("safety_flags")))
    errors.extend(_validate_count_summary(expected.get("count_summary")))
    errors.extend(_validate_safe_marker_contract(fixture))

    forbidden_scan = scan_forbidden_payload(request)
    errors.extend(forbidden_scan.reason_codes)
    forbidden_scan = scan_forbidden_payload(pointer)
    errors.extend(forbidden_scan.reason_codes)
    forbidden_scan = scan_forbidden_payload(expected)
    errors.extend(forbidden_scan.reason_codes)
    return sorted(set(errors))


def _build_expected_contract_result(
    fixture: ArtifactBodyFixtureCase,
) -> ArtifactBodyFixtureValidationResult:
    expected = fixture.expected_artifact_body_result
    contract_errors = _validate_case_contract(fixture)
    if contract_errors:
        return _contract_failure_result(fixture, contract_errors)
    return ArtifactBodyFixtureValidationResult(
        validation_status=expected.get("validation_status", "fail"),
        body_status=expected.get("body_status"),
        reason_codes=sorted(expected.get("reason_codes", [])),
        failed_checks=sorted(expected.get("failed_checks", [])),
        failure_categories=[],
        checked_files_count=3,
        case_category=fixture.case_category,
        case_name=fixture.case_name,
        case_label=fixture.case_label,
        case_id=expected.get("case_id"),
        artifact_body_id=expected.get("artifact_body_id"),
        artifact_id=expected.get("artifact_id"),
        manifest_id=expected.get("manifest_id"),
        writer_result_pointer_id=expected.get("writer_result_pointer_id"),
        writer_version=expected.get("writer_version"),
        request_schema_version=fixture.request_schema_version,
        pointer_schema_version=fixture.pointer_schema_version,
        expected_schema_version=fixture.expected_schema_version,
        result_schema_version=fixture.result_schema_version,
        synthetic_only_notice_present=expected.get("synthetic_only_notice_present"),
        no_oracle_notice_present=expected.get("no_oracle_notice_present"),
        validation_reference_ids=sorted(expected.get("validation_reference_ids", [])),
        artifact_flags=dict(expected.get("artifact_flags", {})),
        safety_flags=dict(expected.get("safety_flags", {})),
        count_summary=dict(expected.get("count_summary", {})),
        safe_marker_flags=dict(expected.get("safe_marker_flags", {})),
        safe_summary=expected.get("safe_summary"),
        artifact_file_written=bool(expected.get("artifact_file_written", False)),
        manifest_file_written=bool(expected.get("manifest_file_written", False)),
    )


def _contract_failure_result(
    fixture: ArtifactBodyFixtureCase,
    errors: list[str],
) -> ArtifactBodyFixtureValidationResult:
    expected = fixture.expected_artifact_body_result
    return ArtifactBodyFixtureValidationResult(
        validation_status="fail",
        body_status="fail_closed",
        reason_codes=sorted(set(errors)),
        failed_checks=sorted(set(errors)),
        failure_categories=["contract_mismatch"],
        checked_files_count=_count_existing_required_files(fixture.case_dir),
        case_category=fixture.case_category,
        case_name=fixture.case_name,
        case_label=fixture.case_label,
        case_id=expected.get("case_id"),
        artifact_body_id=expected.get("artifact_body_id"),
        artifact_id=expected.get("artifact_id"),
        manifest_id=expected.get("manifest_id"),
        writer_result_pointer_id=expected.get("writer_result_pointer_id"),
        writer_version=expected.get("writer_version"),
        request_schema_version=fixture.request_schema_version,
        pointer_schema_version=fixture.pointer_schema_version,
        expected_schema_version=fixture.expected_schema_version,
        result_schema_version=fixture.result_schema_version,
        synthetic_only_notice_present=expected.get("synthetic_only_notice_present"),
        no_oracle_notice_present=expected.get("no_oracle_notice_present"),
        validation_reference_ids=sorted(expected.get("validation_reference_ids", [])),
        artifact_flags=dict(expected.get("artifact_flags", {})),
        safety_flags=dict(expected.get("safety_flags", {})),
        count_summary=dict(expected.get("count_summary", {})),
        safe_marker_flags=dict(expected.get("safe_marker_flags", {})),
        safe_summary=expected.get("safe_summary"),
    )


def _input_error_result(
    case_dir: Path,
    errors: list[str],
) -> ArtifactBodyFixtureValidationResult:
    return ArtifactBodyFixtureValidationResult(
        validation_status="input_error",
        body_status="input_error",
        reason_codes=sorted(set(errors or ["malformed_fixture_file"])),
        failed_checks=["fixture_shape"],
        failure_categories=["input_error"],
        checked_files_count=_count_existing_required_files(case_dir),
        case_category=case_dir.parent.name,
        case_name=case_dir.name,
        case_label=f"{case_dir.parent.name}/{case_dir.name}",
    )


def _validate_category_contract(fixture: ArtifactBodyFixtureCase) -> list[str]:
    expected = fixture.expected_artifact_body_result
    expected_reason = EXPECTED_INVALID_REASONS.get(fixture.case_label)
    errors: list[str] = []
    if fixture.case_label in VALID_CASE_LABELS:
        if expected.get("validation_status") != "pass":
            errors.append("valid_case_status_mismatch")
        if expected.get("body_status") not in {
            "suppressed_metadata_only",
            "generated_safe_metadata_body",
        }:
            errors.append("valid_case_body_status_mismatch")
        if expected.get("reason_codes") != []:
            errors.append("valid_case_reason_codes_not_empty")
        if expected.get("failed_checks") != []:
            errors.append("valid_case_failed_checks_not_empty")
    elif expected_reason:
        if expected.get("validation_status") != "fail":
            errors.append("invalid_case_status_mismatch")
        if expected.get("body_status") != "fail_closed":
            errors.append("invalid_case_body_status_mismatch")
        if expected.get("reason_codes") != [expected_reason]:
            errors.append("invalid_case_reason_code_mismatch")
        if len(expected.get("failed_checks", [])) != 1:
            errors.append("invalid_case_failed_check_mismatch")
    else:
        errors.append("unexpected_case_label")
    return errors


def _validate_identity_links(
    request: Mapping[str, Any],
    pointer: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []
    for field_name in ("case_id", "category", "artifact_id", "manifest_id"):
        values = {
            request.get(field_name),
            pointer.get(field_name),
            expected.get(field_name),
        }
        if len(values) != 1:
            errors.append(f"identity_mismatch:{field_name}")
    if request.get("artifact_body_id") != expected.get("artifact_body_id"):
        errors.append("identity_mismatch:artifact_body_id")
    if request.get("writer_version") != expected.get("writer_version"):
        errors.append("identity_mismatch:writer_version")
    if pointer.get("writer_result_pointer_id") != expected.get(
        "writer_result_pointer_id"
    ):
        errors.append("identity_mismatch:writer_result_pointer_id")
    if sorted(request.get("validation_reference_ids", [])) != sorted(
        expected.get("validation_reference_ids", [])
    ):
        errors.append("identity_mismatch:validation_reference_ids")
    if sorted(pointer.get("validation_reference_ids", [])) != sorted(
        expected.get("validation_reference_ids", [])
    ):
        errors.append("identity_mismatch:pointer_validation_reference_ids")
    return errors


def _validate_artifact_flags(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["artifact_flags_not_object"]
    errors: list[str] = []
    for key in REQUIRED_ARTIFACT_FLAGS:
        if key not in value:
            errors.append(f"missing_artifact_flag:{key}")
        elif not isinstance(value[key], bool):
            errors.append(f"non_boolean_artifact_flag:{key}")
    if value.get("artifact_file_written") is not False:
        errors.append("artifact_file_written_not_allowed")
    if value.get("manifest_file_written") is not False:
        errors.append("manifest_file_written_not_allowed")
    if value.get("manifest_body_available") is not False:
        errors.append("manifest_body_available_not_allowed")
    return errors


def _validate_safety_flags(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["safety_flags_not_object"]
    errors: list[str] = []
    for key in REQUIRED_SAFETY_FLAGS:
        if key not in value:
            errors.append(f"missing_safety_flag:{key}")
        elif value[key] is not True:
            errors.append(f"safety_flag_not_true:{key}")
    return errors


def _validate_count_summary(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["count_summary_not_object"]
    errors: list[str] = []
    for key in REQUIRED_COUNT_SUMMARY_FIELDS:
        if key not in value:
            errors.append(f"missing_count_summary:{key}")
        elif not isinstance(value[key], int):
            errors.append(f"non_integer_count_summary:{key}")
    for key in ZERO_COUNT_FIELDS:
        if value.get(key) != 0:
            errors.append(f"nonzero_forbidden_count:{key}")
    if value.get("validation_reference_count", 0) < 1:
        errors.append("missing_validation_reference_count")
    return errors


def _validate_safe_marker_contract(fixture: ArtifactBodyFixtureCase) -> list[str]:
    expected = fixture.expected_artifact_body_result
    marker_flags = expected.get("safe_marker_flags")
    if not isinstance(marker_flags, dict):
        return ["safe_marker_flags_not_object"]
    scan = scan_safe_markers(expected)
    errors = list(scan.reason_codes)
    expected_reason = EXPECTED_INVALID_REASONS.get(fixture.case_label)
    true_markers = sorted(key for key, value in marker_flags.items() if value is True)
    if fixture.case_label in VALID_CASE_LABELS and true_markers:
        errors.append("valid_case_marker_true")
    if expected_reason:
        expected_marker = EXPECTED_REASON_MARKERS[expected_reason]
        if true_markers != [expected_marker]:
            errors.append("invalid_case_marker_mismatch")
    return sorted(set(errors))


def _missing_fields(
    payload: Mapping[str, Any],
    required_fields: tuple[str, ...],
) -> list[str]:
    return [
        f"missing_required_field:{field_name}"
        for field_name in required_fields
        if field_name not in payload
    ]


def _count_existing_required_files(case_dir: Path) -> int:
    return sum(1 for file_name in REQUIRED_FILES if (case_dir / file_name).is_file())


def _collect_marker_values(payload: Any) -> list[tuple[str, Any]]:
    markers: list[tuple[str, Any]] = []
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if key == "safe_marker_flags" and isinstance(value, Mapping):
                markers.extend(
                    (str(marker), marker_value)
                    for marker, marker_value in value.items()
                )
            else:
                markers.extend(_collect_marker_values(value))
    elif isinstance(payload, list):
        for item in payload:
            markers.extend(_collect_marker_values(item))
    return markers


def _walk_mapping(payload: Any) -> list[tuple[str, Any]]:
    items: list[tuple[str, Any]] = []
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            items.append((str(key), value))
            items.extend(_walk_mapping(value))
    elif isinstance(payload, list):
        for item in payload:
            items.extend(_walk_mapping(item))
    return items


def _string_contains_forbidden_value(value: str) -> bool:
    lowered = value.lower()
    if any(marker in lowered for marker in RAW_LOG_MARKERS):
        return True
    return bool(LOCAL_ABSOLUTE_PATH_PATTERN.search(value))


def _safe_scalar_or_collection(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        return [_safe_scalar_or_collection(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): _safe_scalar_or_collection(item)
            for key, item in sorted(value.items())
        }
    return str(type(value).__name__)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
