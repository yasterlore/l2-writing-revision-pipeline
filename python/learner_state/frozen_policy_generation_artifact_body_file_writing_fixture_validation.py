"""Static validation for artifact body file writing fixtures.

This module validates synthetic metadata-only fixture contracts for future
artifact body file writing. It does not write files, create temp directories,
implement a CLI output option, generate artifact bodies, write manifests,
connect artifact writer CLI, train models, or compute metrics.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

ARTIFACT_BODY_REQUEST_FILE = "artifact_body_request.json"
ARTIFACT_WRITER_RESULT_POINTER_FILE = "artifact_writer_result_pointer.json"
FILE_WRITE_REQUEST_FILE = "file_write_request.json"
EXPECTED_FILE_WRITE_RESULT_FILE = "expected_file_write_result.json"

REQUEST_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_request_v0.1"
)
POINTER_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_writer_result_pointer_v0.1"
)
FILE_WRITE_REQUEST_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_file_write_request_v0.1"
)
EXPECTED_FILE_WRITE_RESULT_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_file_write_expected_result_v0.1"
)
VALIDATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_file_writing_fixture_validation_v0.1"
)

EXPECTED_VALID_CASES = 5
EXPECTED_INVALID_CASES = 24
EXPECTED_TOTAL_CASES = 29
EXPECTED_JSON_FILE_COUNT = EXPECTED_TOTAL_CASES * 4
DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing"
)

REQUIRED_FILES = (
    ARTIFACT_BODY_REQUEST_FILE,
    ARTIFACT_WRITER_RESULT_POINTER_FILE,
    FILE_WRITE_REQUEST_FILE,
    EXPECTED_FILE_WRITE_RESULT_FILE,
)

VALID_CASE_LABELS = frozenset(
    {
        "valid/valid_safe_metadata_relative_tmp_output",
        "valid/valid_safe_metadata_nested_tmp_output",
        "valid/valid_safe_metadata_no_output_path",
        "valid/valid_safe_metadata_explicit_no_overwrite",
        "valid/valid_safe_metadata_summary_only_stdout",
    }
)

EXPECTED_INVALID_REASONS = {
    "invalid/invalid_suppressed_mode_with_output_path": (
        "suppressed_mode_with_output_path"
    ),
    "invalid/invalid_fail_closed_generation_with_output_path": (
        "fail_closed_generation_with_output_path"
    ),
    "invalid/invalid_unsafe_body_audit_with_output_path": (
        "unsafe_body_audit_with_output_path"
    ),
    "invalid/invalid_absolute_output_path": "absolute_output_path",
    "invalid/invalid_home_output_path": "home_output_path",
    "invalid/invalid_parent_traversal_output_path": (
        "parent_traversal_output_path"
    ),
    "invalid/invalid_private_path_marker_output_path": (
        "private_path_marker_output_path"
    ),
    "invalid/invalid_dropbox_or_cloud_path_output_path": (
        "dropbox_or_cloud_path_output_path"
    ),
    "invalid/invalid_manifest_file_output_attempt": (
        "manifest_file_output_attempt"
    ),
    "invalid/invalid_generated_policy_body_output_attempt": (
        "generated_policy_body_output_attempt"
    ),
    "invalid/invalid_request_body_leakage_in_file": (
        "request_body_leakage_in_file"
    ),
    "invalid/invalid_pointer_body_leakage_in_file": (
        "pointer_body_leakage_in_file"
    ),
    "invalid/invalid_expected_body_leakage_in_file": (
        "expected_body_leakage_in_file"
    ),
    "invalid/invalid_raw_rows_in_file": "raw_rows_in_file",
    "invalid/invalid_logits_dump_in_file": "logits_dump_in_file",
    "invalid/invalid_private_path_in_file": "private_path_in_file",
    "invalid/invalid_raw_learner_text_in_file": "raw_learner_text_in_file",
    "invalid/invalid_performance_metric_body_in_file": (
        "performance_metric_body_in_file"
    ),
    "invalid/invalid_missing_synthetic_notice": "missing_synthetic_notice",
    "invalid/invalid_missing_no_oracle_notice": "missing_no_oracle_notice",
    "invalid/invalid_missing_non_proof_notice": "missing_non_proof_notice",
    "invalid/invalid_overwrite_without_policy": "overwrite_without_policy",
    "invalid/invalid_output_path_outside_allowed_root": (
        "output_path_outside_allowed_root"
    ),
    "invalid/invalid_output_path_with_absolute_segment_after_normalization": (
        "output_path_with_absolute_segment_after_normalization"
    ),
}

REQUIRED_REQUEST_FIELDS = (
    "schema_version",
    "case_id",
    "category",
    "requested_body_mode",
    "requested_body_status",
    "artifact_body_id",
    "artifact_id",
    "manifest_id",
    "writer_version",
    "synthetic_only_notice_present",
    "no_oracle_notice_present",
    "non_proof_notice_present",
    "safe_section_keys",
    "validation_reference_ids",
    "safe_marker_flags",
)

REQUIRED_POINTER_FIELDS = (
    "schema_version",
    "case_id",
    "category",
    "writer_result_pointer_id",
    "writer_result_schema_version",
    "writer_result_safe_summary",
    "writer_status",
    "artifact_id",
    "manifest_id",
    "artifact_body_suppressed",
    "manifest_body_suppressed",
    "generated_artifact_written",
    "content_suppressed",
    "no_raw_rows",
    "no_logits_dump",
    "no_private_paths",
    "no_performance_claims",
    "validation_reference_ids",
    "safe_marker_flags",
)

REQUIRED_FILE_WRITE_FIELDS = (
    "schema_version",
    "case_id",
    "mode",
    "artifact_body_status",
    "output_path",
    "output_root_policy",
    "overwrite",
    "create_parent_dirs",
    "expected_summary_only_stdout",
    "expected_body_payload_not_printed",
    "requested_outputs",
    "path_policy",
    "content_policy",
    "synthetic_only_notice",
    "no_oracle_notice",
    "non_proof_notice",
    "safe_marker_flags",
)

REQUIRED_EXPECTED_FIELDS = (
    "schema_version",
    "case_id",
    "expected_status",
    "expected_reason_codes",
    "expected_failed_checks",
    "expected_file_written",
    "expected_file_exists",
    "expected_summary_only_stdout",
    "expected_body_payload_not_printed",
    "expected_manifest_file_written",
    "expected_output_path_safety_checked",
    "expected_artifact_body_audit_checked",
    "expected_allowed_key_check",
    "expected_forbidden_key_check",
    "expected_zero_forbidden_counts",
    "expected_private_path_absent",
    "expected_raw_text_absent",
    "expected_logits_absent",
    "expected_performance_metric_body_absent",
)

REQUIRED_PATH_POLICY_FIELDS = (
    "relative_path_required",
    "allowed_root_required",
    "disallow_absolute_path",
    "disallow_home_path",
    "disallow_drive_root",
    "disallow_parent_traversal",
    "disallow_symlink_escape",
    "disallow_private_cloud_marker",
    "disallow_hidden_private_dirs",
    "require_json_extension",
    "filename_safe_charset",
    "path_length_limit",
    "parent_creation_policy",
    "overwrite_policy",
)

REQUIRED_CONTENT_POLICY_FIELDS = (
    "allowed_top_level_keys",
    "required_notices",
    "required_schema_version",
    "required_body_status",
    "require_synthetic_notice",
    "require_no_oracle_notice",
    "require_non_proof_notice",
    "forbid_request_body",
    "forbid_pointer_body",
    "forbid_expected_body",
    "forbid_generated_policy_body",
    "forbid_manifest_body",
    "forbid_raw_rows",
    "forbid_logits",
    "forbid_private_paths",
    "forbid_performance_metric_body",
    "forbid_raw_learner_text",
    "require_zero_forbidden_counts",
)

EXPECTED_REASON_CODE_ALIASES = {
    "absolute_output_path": "unsafe_absolute_output_path",
    "home_output_path": "unsafe_home_output_path",
    "parent_traversal_output_path": "unsafe_parent_traversal_output_path",
    "private_path_marker_output_path": "unsafe_private_path_marker",
    "dropbox_or_cloud_path_output_path": "unsafe_private_cloud_marker",
    "output_path_outside_allowed_root": "output_path_outside_allowed_root",
    "output_path_with_absolute_segment_after_normalization": (
        "unsafe_path_after_normalization"
    ),
    "suppressed_mode_with_output_path": "suppressed_mode_output_not_allowed",
    "fail_closed_generation_with_output_path": (
        "fail_closed_generation_output_not_allowed"
    ),
    "unsafe_body_audit_with_output_path": "unsafe_body_audit_output_not_allowed",
    "manifest_file_output_attempt": "manifest_output_not_allowed",
    "generated_policy_body_output_attempt": (
        "generated_policy_body_output_not_allowed"
    ),
    "request_body_leakage_in_file": "request_body_leakage",
    "pointer_body_leakage_in_file": "pointer_body_leakage",
    "expected_body_leakage_in_file": "expected_body_leakage",
    "raw_rows_in_file": "raw_rows_leakage",
    "logits_dump_in_file": "logits_dump_leakage",
    "private_path_in_file": "private_path_leakage",
    "raw_learner_text_in_file": "raw_learner_text_leakage",
    "performance_metric_body_in_file": "performance_metric_body_leakage",
    "missing_synthetic_notice": "missing_synthetic_notice",
    "missing_no_oracle_notice": "missing_no_oracle_notice",
    "missing_non_proof_notice": "missing_non_proof_notice",
    "overwrite_without_policy": "overwrite_policy_missing",
}

SENTINEL_REASON_ALIASES = {
    "SYNTHETIC_PRIVATE_PATH_MARKER": "unsafe_private_path_marker",
    "SYNTHETIC_CLOUD_SYNC_MARKER": "unsafe_private_cloud_marker",
    "SYNTHETIC_ABSOLUTE_OUTPUT_PATH_MARKER": "unsafe_absolute_output_path",
    "SYNTHETIC_HOME_OUTPUT_PATH_MARKER": "unsafe_home_output_path",
    "SYNTHETIC_ABSOLUTE_SEGMENT_AFTER_NORMALIZATION": (
        "unsafe_path_after_normalization"
    ),
}

FORBIDDEN_PAYLOAD_KEYS = frozenset(
    {
        "artifact_body_payload",
        "request_body",
        "pointer_body",
        "expected_body",
        "expected_result_body",
        "generated_policy_body",
        "frozen_policy_body",
        "manifest_body",
        "raw_rows",
        "raw_learner_text",
        "logits",
        "probabilities",
        "private_path",
        "performance_metrics",
        "performance_metric_body",
        "final_text",
        "observed_after_text",
        "gold_label",
    }
)

SAFE_SENTINEL_KEYS = frozenset(
    {
        "synthetic_request_body_leakage_marker",
        "synthetic_pointer_body_leakage_marker",
        "synthetic_expected_body_leakage_marker",
        "synthetic_raw_rows_marker",
        "synthetic_logits_dump_marker",
        "synthetic_private_path_marker_in_body",
        "synthetic_raw_learner_text_marker",
        "synthetic_performance_metric_body_marker",
        "target_exists_sentinel",
        "fail_closed_generation_result",
        "unsafe_body_audit_sentinel",
    }
)

LOCAL_ABSOLUTE_PATH_PATTERN = re.compile(
    r"(^/Users/|^/home/|^/private/|^/var/folders/|^[A-Za-z]:\\)"
)
SAFE_PATH_PATTERN = re.compile(r"^[a-z0-9_./-]*$")
SAFE_CASE_SELECTOR_PATTERN = re.compile(r"^[a-z0-9_/-]+$")


@dataclass(frozen=True)
class FileWritingFixtureValidationError(Exception):
    """Safe fixture validation error."""

    reason_code: str
    failed_check: str


@dataclass(frozen=True)
class FileWritingFixtureCase:
    case_dir: Path
    expected_kind: str
    case_name: str
    case_label: str
    artifact_body_request: dict[str, Any]
    writer_result_pointer: dict[str, Any]
    file_write_request: dict[str, Any]
    expected_file_write_result: dict[str, Any]


@dataclass(frozen=True)
class FileWritingFixtureCaseResult:
    validation_status: str
    expected_status: str | None = None
    case_label: str | None = None
    case_id: str | None = None
    expected_kind: str | None = None
    reason_codes: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)
    checked_files_count: int = 0
    expected_file_written: bool | None = None
    expected_file_exists: bool | None = None
    expected_manifest_file_written: bool | None = None
    expected_summary_only_stdout: bool | None = None
    expected_body_payload_not_printed: bool | None = None
    path_policy_checked: bool = True
    body_content_policy_checked: bool = True
    stdout_body_suppression_checked: bool = True
    manifest_absence_checked: bool = True
    file_writing_isolated: bool = False
    content_suppressed: bool = True
    no_raw_rows: bool = True
    no_logits_dump: bool = True
    no_private_paths: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    validation_schema_version: str = VALIDATION_SCHEMA_VERSION

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "validation_schema_version": self.validation_schema_version,
            "validation_status": self.validation_status,
            "expected_status": self.expected_status,
            "case_label": self.case_label,
            "case_id": self.case_id,
            "expected_kind": self.expected_kind,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "checked_files_count": self.checked_files_count,
            "expected_file_written": self.expected_file_written,
            "expected_file_exists": self.expected_file_exists,
            "expected_manifest_file_written": self.expected_manifest_file_written,
            "expected_summary_only_stdout": self.expected_summary_only_stdout,
            "expected_body_payload_not_printed": (
                self.expected_body_payload_not_printed
            ),
            "path_policy_checked": self.path_policy_checked,
            "body_content_policy_checked": self.body_content_policy_checked,
            "stdout_body_suppression_checked": (
                self.stdout_body_suppression_checked
            ),
            "manifest_absence_checked": self.manifest_absence_checked,
            "file_writing_isolated": self.file_writing_isolated,
            "content_suppressed": self.content_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "no_logits_dump": self.no_logits_dump,
            "no_private_paths": self.no_private_paths,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
        }


@dataclass(frozen=True)
class FileWritingFixtureValidationSummary:
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
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    path_policy_checked: bool = True
    body_content_policy_checked: bool = True
    stdout_body_suppression_checked: bool = True
    manifest_absence_checked: bool = True
    file_writing_isolated: bool = False
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
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
            "path_policy_checked": self.path_policy_checked,
            "body_content_policy_checked": self.body_content_policy_checked,
            "stdout_body_suppression_checked": (
                self.stdout_body_suppression_checked
            ),
            "manifest_absence_checked": self.manifest_absence_checked,
            "file_writing_isolated": self.file_writing_isolated,
        }


def discover_fixture_cases(fixture_root: Path) -> list[FileWritingFixtureCase]:
    return [
        load_fixture_case(case_dir, expected_kind=case_dir.parent.name)
        for case_dir in _case_dirs(Path(fixture_root))
    ]


def load_fixture_case(
    case_dir: Path,
    *,
    expected_kind: str | None = None,
) -> FileWritingFixtureCase:
    case_dir = Path(case_dir)
    kind = expected_kind or case_dir.parent.name
    case_name = case_dir.name
    case_label = f"{kind}/{case_name}"
    return FileWritingFixtureCase(
        case_dir=case_dir,
        expected_kind=kind,
        case_name=case_name,
        case_label=case_label,
        artifact_body_request=_read_json(case_dir / ARTIFACT_BODY_REQUEST_FILE),
        writer_result_pointer=_read_json(
            case_dir / ARTIFACT_WRITER_RESULT_POINTER_FILE
        ),
        file_write_request=_read_json(case_dir / FILE_WRITE_REQUEST_FILE),
        expected_file_write_result=_read_json(
            case_dir / EXPECTED_FILE_WRITE_RESULT_FILE
        ),
    )


def validate_fixture_case(
    case_dir: Path,
    expected_kind: str | None = None,
) -> FileWritingFixtureCaseResult:
    case_dir = Path(case_dir)
    kind = expected_kind or case_dir.parent.name
    case_label = f"{kind}/{case_dir.name}"
    try:
        shape_errors = _validate_required_file_shape(case_dir)
        if shape_errors:
            return _input_error_result(case_dir, shape_errors, expected_kind=kind)
        fixture = load_fixture_case(case_dir, expected_kind=kind)
        contract_errors = _validate_fixture_contract(fixture)
        if contract_errors:
            return _contract_result(fixture, contract_errors, status="input_error")
        return _expected_result(fixture)
    except (OSError, json.JSONDecodeError, ValueError):
        return FileWritingFixtureCaseResult(
            validation_status="input_error",
            expected_status="input_error",
            case_label=case_label,
            case_id=case_label,
            expected_kind=kind,
            reason_codes=["malformed_fixture"],
            failed_checks=["json_parse_or_fixture_shape"],
            checked_files_count=_count_existing_required_files(case_dir),
        )


def validate_fixture_root(fixture_root: Path) -> FileWritingFixtureValidationSummary:
    fixture_root = Path(fixture_root)
    root_errors = _validate_root_shape(fixture_root)
    if root_errors:
        return FileWritingFixtureValidationSummary(
            input_error_cases=1,
            reason_code_counts=dict(Counter(root_errors)),
        )

    matched_cases = 0
    mismatched_cases = 0
    input_error_cases = 0
    valid_cases = 0
    invalid_cases = 0
    reason_counter: Counter[str] = Counter()

    for case_dir in _case_dirs(fixture_root):
        if case_dir.parent.name == "valid":
            valid_cases += 1
        elif case_dir.parent.name == "invalid":
            invalid_cases += 1

        result = validate_fixture_case(case_dir, expected_kind=case_dir.parent.name)
        reason_counter.update(result.reason_codes)
        if result.validation_status == "input_error":
            input_error_cases += 1
            continue
        expected = _read_json(case_dir / EXPECTED_FILE_WRITE_RESULT_FILE)
        if _case_matches_expected(result, expected):
            matched_cases += 1
        else:
            mismatched_cases += 1

    return FileWritingFixtureValidationSummary(
        total_cases=matched_cases + mismatched_cases + input_error_cases,
        valid_cases=valid_cases,
        invalid_cases=invalid_cases,
        matched_cases=matched_cases,
        mismatched_cases=mismatched_cases,
        input_error_cases=input_error_cases,
        reason_code_counts=dict(sorted(reason_counter.items())),
    )


def summarize_file_writing_fixture_validation(
    summary: FileWritingFixtureValidationSummary | FileWritingFixtureCaseResult,
) -> str:
    safe_dict = summary.to_safe_dict()
    lines = []
    for key in sorted(safe_dict):
        value = safe_dict[key]
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        elif isinstance(value, list):
            rendered = "none" if not value else ",".join(str(item) for item in value)
        elif isinstance(value, dict):
            rendered = json.dumps(value, sort_keys=True, separators=(",", ":"))
        elif value is None:
            rendered = "none"
        else:
            rendered = str(value)
        lines.append(f"{key}={rendered}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog=(
            "python3 -m "
            "learner_state.frozen_policy_generation_artifact_body_file_writing_fixture_validation"
        ),
        description=(
            "Validate artifact body file writing fixtures with metadata-only "
            "no-write output."
        ),
    )
    parser.add_argument(
        "--fixture-root",
        default=str(DEFAULT_FIXTURE_ROOT),
        help="Fixture root to validate.",
    )
    parser.add_argument(
        "--fixture-case",
        help="Safe relative case selector, such as valid/case_name.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a safe JSON summary instead of a human summary.",
    )
    args = parser.parse_args(argv)

    try:
        fixture_root = Path(args.fixture_root)
        if args.fixture_case is not None:
            return _run_case_cli(
                fixture_root=fixture_root,
                case_selector=args.fixture_case,
                emit_json=args.json,
            )
        return _run_root_cli(fixture_root=fixture_root, emit_json=args.json)
    except Exception:
        safe_payload = {
            "mode": "fixture_root",
            "validation_schema_version": VALIDATION_SCHEMA_VERSION,
            "validation_status": "internal_error",
            "content_suppressed": True,
            "no_raw_rows": True,
            "no_logits_dump": True,
            "no_private_paths": True,
            "synthetic_only_checked": True,
            "no_oracle_checked": True,
            "file_writing_isolated": False,
        }
        print(_render_safe_dict(safe_payload, emit_json=bool(getattr(args, "json", False))))
        return 1


def _run_root_cli(*, fixture_root: Path, emit_json: bool) -> int:
    summary = validate_fixture_root(fixture_root)
    print(_render_safe_dict(summary.to_safe_dict(), emit_json=emit_json))
    if summary.input_error_cases:
        return 4
    if summary.mismatched_cases:
        return 3
    return 0


def _run_case_cli(*, fixture_root: Path, case_selector: str, emit_json: bool) -> int:
    selector_error = _validate_case_selector(case_selector)
    if selector_error is not None:
        payload = _safe_case_error_payload(
            case_selector="unsafe_fixture_case_selector",
            reason_code=selector_error,
        )
        print(_render_safe_dict(payload, emit_json=emit_json))
        return 2

    case_path = fixture_root / PurePosixPath(case_selector)
    if not case_path.is_dir():
        payload = _safe_case_error_payload(
            case_selector=case_selector,
            reason_code="missing_fixture_case",
        )
        print(_render_safe_dict(payload, emit_json=emit_json))
        return 4

    expected_kind = PurePosixPath(case_selector).parts[0]
    result = validate_fixture_case(case_path, expected_kind=expected_kind)
    matched = _case_result_matches_expected(case_path, result)
    payload = _case_result_cli_payload(result, matched=matched)
    print(_render_safe_dict(payload, emit_json=emit_json))
    if result.validation_status == "input_error":
        return 4
    if not matched:
        return 3
    return 0


def _validate_case_selector(case_selector: str) -> str | None:
    if not case_selector:
        return "empty_fixture_case_selector"
    if case_selector.startswith(("/", "~")):
        return "unsafe_absolute_fixture_case_selector"
    if "\\" in case_selector or re.match(r"^[A-Za-z]:", case_selector):
        return "unsafe_absolute_fixture_case_selector"
    path = PurePosixPath(case_selector)
    parts = path.parts
    if ".." in parts or "." in parts:
        return "unsafe_parent_traversal_fixture_case_selector"
    if len(parts) != 2 or parts[0] not in {"valid", "invalid"}:
        return "unsafe_fixture_case_selector"
    if not SAFE_CASE_SELECTOR_PATTERN.fullmatch(case_selector):
        return "unsafe_fixture_case_selector"
    return None


def _case_result_matches_expected(
    case_path: Path,
    result: FileWritingFixtureCaseResult,
) -> bool:
    try:
        expected = _read_json(case_path / EXPECTED_FILE_WRITE_RESULT_FILE)
    except (OSError, json.JSONDecodeError, ValueError):
        return False
    return _case_matches_expected(result, expected)


def _case_result_cli_payload(
    result: FileWritingFixtureCaseResult,
    *,
    matched: bool,
) -> dict[str, Any]:
    return {
        "mode": "fixture_case",
        "validation_schema_version": result.validation_schema_version,
        "case_id": result.case_id,
        "expected_kind": result.expected_kind,
        "expected_status": result.expected_status,
        "actual_status": result.validation_status,
        "validation_status": result.validation_status,
        "matched": matched,
        "reason_codes": list(result.reason_codes),
        "failed_checks": list(result.failed_checks),
        "content_suppressed": result.content_suppressed,
        "no_raw_rows": result.no_raw_rows,
        "no_logits_dump": result.no_logits_dump,
        "no_private_paths": result.no_private_paths,
        "synthetic_only_checked": result.synthetic_only_checked,
        "no_oracle_checked": result.no_oracle_checked,
        "path_policy_checked": result.path_policy_checked,
        "body_content_policy_checked": result.body_content_policy_checked,
        "stdout_body_suppression_checked": result.stdout_body_suppression_checked,
        "manifest_absence_checked": result.manifest_absence_checked,
        "file_writing_isolated": result.file_writing_isolated,
    }


def _safe_case_error_payload(*, case_selector: str, reason_code: str) -> dict[str, Any]:
    return {
        "mode": "fixture_case",
        "validation_schema_version": VALIDATION_SCHEMA_VERSION,
        "case_id": case_selector,
        "expected_kind": "none",
        "expected_status": "input_error",
        "actual_status": "input_error",
        "validation_status": "input_error",
        "matched": False,
        "reason_codes": [reason_code],
        "failed_checks": [reason_code],
        "content_suppressed": True,
        "no_raw_rows": True,
        "no_logits_dump": True,
        "no_private_paths": True,
        "synthetic_only_checked": True,
        "no_oracle_checked": True,
        "path_policy_checked": True,
        "body_content_policy_checked": True,
        "stdout_body_suppression_checked": True,
        "manifest_absence_checked": True,
        "file_writing_isolated": False,
    }


def _render_safe_dict(payload: Mapping[str, Any], *, emit_json: bool) -> str:
    if emit_json:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return _format_safe_fields(payload)


def _format_safe_fields(payload: Mapping[str, Any]) -> str:
    lines: list[str] = []
    for key in sorted(payload):
        value = payload[key]
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        elif isinstance(value, list):
            rendered = "none" if not value else ",".join(str(item) for item in value)
        elif isinstance(value, dict):
            rendered = json.dumps(value, sort_keys=True, separators=(",", ":"))
        elif value is None:
            rendered = "none"
        else:
            rendered = str(value)
        lines.append(f"{key}={rendered}")
    return "\n".join(lines)


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
    valid_count = len([case for case in cases if case.parent.name == "valid"])
    invalid_count = len([case for case in cases if case.parent.name == "invalid"])
    if valid_count != EXPECTED_VALID_CASES:
        errors.append("unexpected_valid_case_count")
    if invalid_count != EXPECTED_INVALID_CASES:
        errors.append("unexpected_invalid_case_count")
    if len(cases) != EXPECTED_TOTAL_CASES:
        errors.append("unexpected_case_count")
    if len(list(root.glob("*/*/*.json"))) != EXPECTED_JSON_FILE_COUNT:
        errors.append("unexpected_json_file_count")

    discovered = {f"{case.parent.name}/{case.name}" for case in cases}
    expected = set(VALID_CASE_LABELS) | set(EXPECTED_INVALID_REASONS)
    if discovered != expected:
        errors.append("unexpected_case_labels")
    return sorted(set(errors))


def _validate_required_file_shape(case_dir: Path) -> list[str]:
    errors: list[str] = []
    if not case_dir.is_dir():
        return ["missing_case_dir"]
    found = {path.name for path in case_dir.iterdir() if path.is_file()}
    for file_name in REQUIRED_FILES:
        if file_name not in found:
            errors.append("required_file_missing")
    extra_json = [
        file_name
        for file_name in found
        if file_name.endswith(".json") and file_name not in REQUIRED_FILES
    ]
    if extra_json:
        errors.append("unexpected_fixture_file")
    extra_non_json = [
        file_name
        for file_name in found
        if not file_name.endswith(".json") and file_name not in REQUIRED_FILES
    ]
    if extra_non_json:
        errors.append("unexpected_case_file")
    return sorted(set(errors))


def _validate_fixture_contract(fixture: FileWritingFixtureCase) -> list[str]:
    errors: list[str] = []
    request = fixture.artifact_body_request
    pointer = fixture.writer_result_pointer
    write_request = fixture.file_write_request
    expected = fixture.expected_file_write_result

    errors.extend(_missing_fields(request, REQUIRED_REQUEST_FIELDS))
    errors.extend(_missing_fields(pointer, REQUIRED_POINTER_FIELDS))
    errors.extend(_missing_fields(write_request, REQUIRED_FILE_WRITE_FIELDS))
    errors.extend(_missing_fields(expected, REQUIRED_EXPECTED_FIELDS))
    if errors:
        return sorted(set(errors))

    if request.get("schema_version") != REQUEST_SCHEMA_VERSION:
        errors.append("schema_version_unknown")
    if pointer.get("schema_version") != POINTER_SCHEMA_VERSION:
        errors.append("schema_version_unknown")
    if write_request.get("schema_version") != FILE_WRITE_REQUEST_SCHEMA_VERSION:
        errors.append("schema_version_unknown")
    if expected.get("schema_version") != EXPECTED_FILE_WRITE_RESULT_SCHEMA_VERSION:
        errors.append("schema_version_unknown")

    expected_label = fixture.case_label
    for payload in (request, pointer, write_request, expected):
        if payload.get("case_id") != expected_label:
            errors.append("case_id_mismatch")
    if request.get("category") != fixture.expected_kind:
        errors.append("case_id_mismatch")
    if pointer.get("category") != fixture.expected_kind:
        errors.append("case_id_mismatch")
    if fixture.expected_kind == "valid":
        if expected.get("expected_status") != "pass":
            errors.append("expected_status_mismatch")
        if expected.get("expected_reason_codes") or expected.get("expected_failed_checks"):
            errors.append("expected_reason_codes_mismatch")
    elif fixture.expected_kind == "invalid":
        expected_reason = EXPECTED_INVALID_REASONS.get(fixture.case_label)
        if expected.get("expected_status") not in {"fail_closed", "usage_error"}:
            errors.append("expected_status_mismatch")
        if expected_reason not in set(expected.get("expected_reason_codes", [])):
            errors.append("expected_reason_codes_mismatch")
        if not expected.get("expected_failed_checks"):
            errors.append("expected_failed_checks_missing")
    else:
        errors.append("unknown_case_kind")

    errors.extend(_validate_policy_fields(write_request))
    errors.extend(_validate_expected_fields(expected))
    errors.extend(_validate_static_path_policy(write_request, expected))
    errors.extend(_scan_payload_forbidden_values(request))
    errors.extend(_scan_payload_forbidden_values(pointer))
    errors.extend(_scan_payload_forbidden_values(write_request))
    errors.extend(_scan_payload_forbidden_values(expected))
    return sorted(set(errors))


def _validate_policy_fields(write_request: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    path_policy = write_request.get("path_policy")
    content_policy = write_request.get("content_policy")
    if not isinstance(path_policy, Mapping):
        errors.append("path_policy_missing")
    else:
        errors.extend(_missing_fields(path_policy, REQUIRED_PATH_POLICY_FIELDS))
    if not isinstance(content_policy, Mapping):
        errors.append("content_policy_missing")
    else:
        errors.extend(_missing_fields(content_policy, REQUIRED_CONTENT_POLICY_FIELDS))
    return errors


def _validate_expected_fields(expected: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    boolean_fields = [
        "expected_file_written",
        "expected_file_exists",
        "expected_summary_only_stdout",
        "expected_body_payload_not_printed",
        "expected_manifest_file_written",
        "expected_output_path_safety_checked",
        "expected_artifact_body_audit_checked",
        "expected_allowed_key_check",
        "expected_forbidden_key_check",
        "expected_zero_forbidden_counts",
        "expected_private_path_absent",
        "expected_raw_text_absent",
        "expected_logits_absent",
        "expected_performance_metric_body_absent",
    ]
    for field_name in boolean_fields:
        if not isinstance(expected.get(field_name), bool):
            errors.append("expected_result_field_invalid")
    if not isinstance(expected.get("expected_reason_codes"), list):
        errors.append("expected_result_field_invalid")
    if not isinstance(expected.get("expected_failed_checks"), list):
        errors.append("expected_result_field_invalid")
    return errors


def _validate_static_path_policy(
    write_request: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []
    mode = write_request.get("mode")
    body_status = write_request.get("artifact_body_status")
    output_path = str(write_request.get("output_path", ""))
    output_root = ""
    root_policy = write_request.get("output_root_policy")
    if isinstance(root_policy, Mapping):
        output_root = str(root_policy.get("allowed_root", ""))

    derived_reasons: set[str] = set()
    if output_path:
        derived_reasons.update(_derive_path_reasons(output_path, output_root))
    if mode == "suppressed" and output_path:
        derived_reasons.add("suppressed_mode_with_output_path")
    if body_status == "fail_closed" and output_path:
        derived_reasons.add("fail_closed_generation_with_output_path")
    requested_outputs = write_request.get("requested_outputs")
    if isinstance(requested_outputs, Mapping):
        if requested_outputs.get("manifest_file") is True:
            derived_reasons.add("manifest_file_output_attempt")
        if requested_outputs.get("generated_policy_body_file") is True:
            derived_reasons.add("generated_policy_body_output_attempt")
    flags = write_request.get("safe_marker_flags")
    if isinstance(flags, Mapping):
        if flags.get("target_exists_sentinel") is True and not write_request.get(
            "overwrite"
        ):
            derived_reasons.add("overwrite_without_policy")
        if flags.get("synthetic_request_body_leakage_marker") is True:
            derived_reasons.add("request_body_leakage_in_file")
        if flags.get("synthetic_pointer_body_leakage_marker") is True:
            derived_reasons.add("pointer_body_leakage_in_file")
        if flags.get("synthetic_expected_body_leakage_marker") is True:
            derived_reasons.add("expected_body_leakage_in_file")
        if flags.get("synthetic_raw_rows_marker") is True:
            derived_reasons.add("raw_rows_in_file")
        if flags.get("synthetic_logits_dump_marker") is True:
            derived_reasons.add("logits_dump_in_file")
        if flags.get("synthetic_private_path_marker_in_body") is True:
            derived_reasons.add("private_path_in_file")
        if flags.get("synthetic_raw_learner_text_marker") is True:
            derived_reasons.add("raw_learner_text_in_file")
        if flags.get("synthetic_performance_metric_body_marker") is True:
            derived_reasons.add("performance_metric_body_in_file")
    if not write_request.get("synthetic_only_notice"):
        derived_reasons.add("missing_synthetic_notice")
    if not write_request.get("no_oracle_notice"):
        derived_reasons.add("missing_no_oracle_notice")
    if not write_request.get("non_proof_notice"):
        derived_reasons.add("missing_non_proof_notice")

    if expected.get("expected_status") == "pass" and derived_reasons:
        errors.append("unexpected_static_path_reason")
    if expected.get("expected_status") != "pass":
        expected_reasons = set(expected.get("expected_reason_codes", []))
        for reason in derived_reasons:
            if reason not in expected_reasons:
                errors.append("expected_reason_codes_mismatch")
    return errors


def _derive_path_reasons(output_path: str, output_root: str) -> set[str]:
    reasons: set[str] = set()
    for marker, reason in SENTINEL_REASON_ALIASES.items():
        if marker in output_path:
            reasons.add(_reason_alias_to_fixture_reason(reason))
    if reasons:
        return reasons

    if output_path.startswith(("/", "~")) or LOCAL_ABSOLUTE_PATH_PATTERN.search(
        output_path
    ):
        reasons.add("absolute_output_path")
    parts = PurePosixPath(output_path).parts
    if ".." in parts:
        reasons.add("parent_traversal_output_path")
    if output_path and not output_path.endswith(".json"):
        reasons.add("invalid_output_extension")
    if output_path and not SAFE_PATH_PATTERN.fullmatch(output_path):
        reasons.add("unsafe_output_path_charset")
    if output_path.startswith("."):
        reasons.add("hidden_private_dirs")
    if output_path and output_root and not (
        output_path == output_root or output_path.startswith(f"{output_root}/")
    ):
        reasons.add("output_path_outside_allowed_root")
    return reasons


def _reason_alias_to_fixture_reason(reason_code: str) -> str:
    for fixture_reason, alias in EXPECTED_REASON_CODE_ALIASES.items():
        if alias == reason_code:
            return fixture_reason
    return reason_code


def _expected_result(fixture: FileWritingFixtureCase) -> FileWritingFixtureCaseResult:
    expected = fixture.expected_file_write_result
    reason_codes = sorted(expected.get("expected_reason_codes", []))
    failed_checks = sorted(expected.get("expected_failed_checks", []))
    return FileWritingFixtureCaseResult(
        validation_status=expected.get("expected_status", "fail_closed"),
        expected_status=expected.get("expected_status"),
        case_label=fixture.case_label,
        case_id=expected.get("case_id"),
        expected_kind=fixture.expected_kind,
        reason_codes=reason_codes,
        failed_checks=failed_checks,
        checked_files_count=4,
        expected_file_written=expected.get("expected_file_written"),
        expected_file_exists=expected.get("expected_file_exists"),
        expected_manifest_file_written=expected.get("expected_manifest_file_written"),
        expected_summary_only_stdout=expected.get("expected_summary_only_stdout"),
        expected_body_payload_not_printed=expected.get(
            "expected_body_payload_not_printed"
        ),
    )


def _contract_result(
    fixture: FileWritingFixtureCase,
    reason_codes: list[str],
    *,
    status: str,
) -> FileWritingFixtureCaseResult:
    return FileWritingFixtureCaseResult(
        validation_status=status,
        expected_status=status,
        case_label=fixture.case_label,
        case_id=fixture.case_label,
        expected_kind=fixture.expected_kind,
        reason_codes=sorted(set(reason_codes)),
        failed_checks=sorted(set(reason_codes)),
        checked_files_count=4,
    )


def _input_error_result(
    case_dir: Path,
    reason_codes: list[str],
    *,
    expected_kind: str | None = None,
) -> FileWritingFixtureCaseResult:
    kind = expected_kind or case_dir.parent.name
    case_label = f"{kind}/{case_dir.name}"
    return FileWritingFixtureCaseResult(
        validation_status="input_error",
        expected_status="input_error",
        case_label=case_label,
        case_id=case_label,
        expected_kind=kind,
        reason_codes=sorted(set(reason_codes)),
        failed_checks=sorted(set(reason_codes)),
        checked_files_count=_count_existing_required_files(case_dir),
    )


def _case_matches_expected(
    result: FileWritingFixtureCaseResult,
    expected: Mapping[str, Any],
) -> bool:
    comparisons = {
        "case_id": result.case_id,
        "expected_status": result.expected_status,
        "expected_reason_codes": sorted(result.reason_codes),
        "expected_failed_checks": sorted(result.failed_checks),
        "expected_file_written": result.expected_file_written,
        "expected_file_exists": result.expected_file_exists,
        "expected_summary_only_stdout": result.expected_summary_only_stdout,
        "expected_body_payload_not_printed": result.expected_body_payload_not_printed,
        "expected_manifest_file_written": result.expected_manifest_file_written,
    }
    for expected_field, actual_value in comparisons.items():
        expected_value = expected.get(expected_field)
        if expected_field in {"expected_reason_codes", "expected_failed_checks"}:
            expected_value = sorted(expected_value or [])
        if expected_value != actual_value:
            return False
    return True


def _scan_payload_forbidden_values(payload: Mapping[str, Any]) -> list[str]:
    errors: set[str] = set()
    for key, value in _walk_mapping(payload):
        if key in SAFE_SENTINEL_KEYS:
            continue
        if key in FORBIDDEN_PAYLOAD_KEYS:
            errors.add("forbidden_payload_key")
        if isinstance(value, str):
            if LOCAL_ABSOLUTE_PATH_PATTERN.search(value):
                errors.add("actual_private_path")
            if "::group::" in value or "full job output" in value.lower():
                errors.add("raw_log_marker")
    return sorted(errors)


def _case_dirs(root: Path) -> list[Path]:
    cases: list[Path] = []
    for category in ("valid", "invalid"):
        category_dir = root / category
        if category_dir.is_dir():
            cases.extend(path for path in category_dir.iterdir() if path.is_dir())
    return sorted(cases)


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        value = json.load(file)
    if not isinstance(value, dict):
        raise ValueError("expected_json_object")
    return value


def _missing_fields(payload: Mapping[str, Any], required: tuple[str, ...]) -> list[str]:
    return ["missing_required_field" for field in required if field not in payload]


def _count_existing_required_files(case_dir: Path) -> int:
    return sum(1 for file_name in REQUIRED_FILES if (case_dir / file_name).is_file())


def _walk_mapping(value: Any) -> list[tuple[str, Any]]:
    items: list[tuple[str, Any]] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            items.append((str(key), child))
            items.extend(_walk_mapping(child))
    elif isinstance(value, list):
        for child in value:
            items.extend(_walk_mapping(child))
    return items


if __name__ == "__main__":
    sys.exit(main())
