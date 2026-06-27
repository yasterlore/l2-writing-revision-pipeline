"""Static validation for frozen policy generation manifest writer fixtures.

This module validates synthetic metadata-only fixture contracts for a future
manifest writer. It does not implement a manifest writer, generate manifest
bodies, write manifest files, connect artifact writer CLI output, train models,
or compute metrics.
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

CASE_METADATA_FILE = "case_metadata.json"
MANIFEST_WRITER_REQUEST_FILE = "manifest_writer_request.json"
ARTIFACT_WRITER_RESULT_POINTER_FILE = "artifact_writer_result_pointer.json"
ARTIFACT_BODY_GENERATION_RESULT_POINTER_FILE = (
    "artifact_body_generation_result_pointer.json"
)
EXPECTED_MANIFEST_WRITER_RESULT_FILE = "expected_manifest_writer_result.json"

CASE_METADATA_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_case_metadata_v0.1"
)
MANIFEST_WRITER_REQUEST_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_request_v0.1"
)
EXPECTED_MANIFEST_WRITER_RESULT_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_expected_result_v0.1"
)
ARTIFACT_WRITER_RESULT_POINTER_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_artifact_writer_result_pointer_v0.1"
)
ARTIFACT_BODY_GENERATION_RESULT_POINTER_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_artifact_body_generation_result_pointer_v0.1"
)
VALIDATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_fixture_validation_v0.1"
)

DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/learner_state_frozen_policy_generation_manifest_writer"
)
EXPECTED_VALID_CASES = 5
EXPECTED_INVALID_CASES = 25
EXPECTED_TOTAL_CASES = 30
EXPECTED_JSON_FILE_COUNT = EXPECTED_TOTAL_CASES * 5
EXPECTED_MANIFEST_OUTPUT_ROOT = "tmp/frozen_policy_generation_manifest/"

REQUIRED_FILES = (
    CASE_METADATA_FILE,
    MANIFEST_WRITER_REQUEST_FILE,
    ARTIFACT_WRITER_RESULT_POINTER_FILE,
    ARTIFACT_BODY_GENERATION_RESULT_POINTER_FILE,
    EXPECTED_MANIFEST_WRITER_RESULT_FILE,
)

EXPECTED_CATEGORY_COUNTS = {
    "pass_metadata_only_no_file": 3,
    "pass_manifest_file_written": 1,
    "usage_error_no_write": 11,
    "fail_closed_no_write": 15,
}

RESULT_CATEGORIES = frozenset(
    {
        "pass_metadata_only_no_file",
        "pass_manifest_file_written",
        "usage_error_no_write",
        "fail_closed_no_write",
        "input_error",
        "mismatch",
    }
)

EXPECTED_STATUS_BY_CATEGORY = {
    "pass_metadata_only_no_file": "pass",
    "pass_manifest_file_written": "pass",
    "usage_error_no_write": "usage_error",
    "fail_closed_no_write": "fail_closed",
}

VALID_CASE_LABELS = frozenset(
    {
        "valid/metadata_only_manifest_no_file",
        "valid/safe_relative_manifest_file",
        "valid/manifest_with_artifact_body_reference",
        "valid/manifest_with_release_quality_reference",
        "valid/manifest_existing_output_rejected_after_precreate",
    }
)

EXPECTED_INVALID_REASONS = {
    "invalid/generated_policy_body_leakage": "generated_policy_body_leakage",
    "invalid/artifact_body_payload_leakage": "artifact_body_payload_leakage",
    "invalid/request_body_leakage": "request_body_leakage",
    "invalid/pointer_body_leakage": "pointer_body_leakage",
    "invalid/expected_body_leakage": "expected_body_leakage",
    "invalid/raw_rows_leakage": "raw_rows_leakage",
    "invalid/logits_dump_leakage": "logits_dump_leakage",
    "invalid/private_path_leakage": "private_path_leakage",
    "invalid/raw_learner_text_leakage": "raw_learner_text_leakage",
    "invalid/manifest_body_nesting": "manifest_body_nesting",
    "invalid/performance_claim_body": "performance_claim_body",
    "invalid/missing_synthetic_notice": "missing_synthetic_notice",
    "invalid/missing_no_oracle_notice": "missing_no_oracle_notice",
    "invalid/missing_non_proof_notice": "missing_non_proof_notice",
    "invalid/unknown_schema_version": "unknown_schema_version",
    "invalid/absolute_manifest_output_path": "absolute_manifest_output_path",
    "invalid/home_manifest_output_path": "home_manifest_output_path",
    "invalid/parent_traversal_manifest_output_path": (
        "parent_traversal_manifest_output_path"
    ),
    "invalid/cloud_marker_manifest_output_path": (
        "cloud_marker_manifest_output_path"
    ),
    "invalid/private_marker_manifest_output_path": (
        "private_marker_manifest_output_path"
    ),
    "invalid/hidden_private_manifest_directory": (
        "hidden_private_manifest_directory"
    ),
    "invalid/non_json_manifest_extension": "non_json_manifest_extension",
    "invalid/unsafe_manifest_filename": "unsafe_manifest_filename",
    "invalid/too_long_manifest_path": "too_long_manifest_path",
    "invalid/overwrite_without_policy": "overwrite_without_policy",
}

VALID_SAFE_REJECTION_REASONS = {
    "valid/manifest_existing_output_rejected_after_precreate": (
        "overwrite_without_policy"
    )
}

REQUIRED_CASE_METADATA_FIELDS = (
    "schema_version",
    "case_id",
    "case_kind",
    "description",
    "source_artifact_writer_case",
    "source_artifact_body_case",
    "expected_category",
    "expected_status",
    "expected_exit_code",
    "safety_expectation",
    "should_write_manifest_file",
    "should_cleanup",
    "should_leave_residue",
    "allowed_failure_reason_codes",
    "forbidden_output_markers",
    "required_summary_fields",
    "forbidden_summary_fields",
    "notes",
)

REQUIRED_MANIFEST_WRITER_REQUEST_FIELDS = (
    "schema_version",
    "request_id",
    "manifest_id",
    "artifact_id",
    "artifact_body_id",
    "artifact_writer_result_pointer_id",
    "artifact_body_generation_result_pointer_id",
    "validation_reference_ids",
    "release_quality_reference_ids",
    "manifest_out",
    "manifest_output_root",
    "allow_overwrite",
    "cleanup_policy",
    "include_artifact_body_payload",
    "include_generated_policy_body",
    "include_manifest_body",
    "include_request_body",
    "include_pointer_body",
    "include_expected_body",
    "include_raw_rows",
    "include_logits",
    "include_private_paths",
    "synthetic_only",
    "no_oracle_required",
    "non_proof_notice_required",
)

REQUIRED_ARTIFACT_WRITER_POINTER_FIELDS = (
    "schema_version",
    "pointer_id",
    "source_case_id",
    "result_schema_version",
    "artifact_id",
    "manifest_id",
    "writer_status",
    "writer_mode",
    "body_payload_suppressed",
    "generated_policy_body_suppressed",
    "manifest_body_suppressed",
    "raw_data_suppressed",
    "synthetic_only_checked",
    "no_oracle_checked",
    "safe_reference_only",
)

REQUIRED_ARTIFACT_BODY_POINTER_FIELDS = (
    "schema_version",
    "pointer_id",
    "source_case_id",
    "result_schema_version",
    "artifact_body_id",
    "artifact_id",
    "generation_status",
    "artifact_body_status",
    "artifact_body_payload_suppressed",
    "artifact_body_file_written",
    "manifest_file_written",
    "manifest_body_generated",
    "raw_data_suppressed",
    "synthetic_only_checked",
    "no_oracle_checked",
    "safe_reference_only",
)

REQUIRED_EXPECTED_RESULT_FIELDS = (
    "schema_version",
    "case_id",
    "expected_category",
    "expected_status",
    "expected_exit_code",
    "expected_manifest_file_written",
    "expected_manifest_body_available",
    "expected_manifest_path_available",
    "expected_manifest_path_safe_relative_only",
    "expected_manifest_json_parse_ok",
    "expected_manifest_allowed_keys_only",
    "expected_manifest_cleanup_ok",
    "expected_residue_file_count",
    "expected_stdout_body_free",
    "expected_stderr_body_free",
    "expected_no_raw_rows",
    "expected_no_logits",
    "expected_no_private_paths",
    "expected_no_absolute_paths",
    "expected_no_raw_learner_text",
    "expected_no_artifact_body_payload",
    "expected_no_generated_policy_body",
    "expected_no_manifest_body_nesting",
    "expected_no_request_body",
    "expected_no_pointer_body",
    "expected_no_expected_body",
    "expected_no_performance_claim",
    "expected_reason_codes",
    "expected_failed_checks",
    "expected_summary_flags",
    "expected_forbidden_counts_zero",
    "expected_no_real_data",
)

FORBIDDEN_INCLUDE_FLAG_REASONS = {
    "include_artifact_body_payload": "artifact_body_payload_leakage",
    "include_generated_policy_body": "generated_policy_body_leakage",
    "include_manifest_body": "manifest_body_nesting",
    "include_request_body": "request_body_leakage",
    "include_pointer_body": "pointer_body_leakage",
    "include_expected_body": "expected_body_leakage",
    "include_raw_rows": "raw_rows_leakage",
    "include_logits": "logits_dump_leakage",
    "include_private_paths": "private_path_leakage",
}

MISSING_NOTICE_REASONS = {
    "synthetic_only": "missing_synthetic_notice",
    "no_oracle_required": "missing_no_oracle_notice",
    "non_proof_notice_required": "missing_non_proof_notice",
}

SAFE_CASE_SELECTOR_PATTERN = re.compile(r"^[a-z0-9_/-]+$")
SAFE_RELATIVE_MANIFEST_OUT_PATTERN = re.compile(r"^[a-z0-9_./-]+$")
LOCAL_ABSOLUTE_PATH_PATTERN = re.compile(
    r"(^/Us" r"ers/|^/home/|^/private/|^/var/fold" r"ers/|^[A-Za-z]:\\|file" r"://)"
)

FORBIDDEN_VALUE_FRAGMENTS = (
    "/Us" "ers/",
    "/private" "/tmp",
    "/var/fold" "ers",
    "file" "://",
    "BEGIN" " RAW",
    "raw learner text" " payload",
    "artifact body payload" " value",
    "generated policy body" " value",
    "manifest body" " value",
    "logit" "_values",
    "probability" "_values",
    "real" "_participant",
    "participant_id" "_real",
    "production_data" "_reference",
)


@dataclass(frozen=True)
class ManifestWriterFixtureValidationError(Exception):
    """Safe fixture validation error."""

    reason_code: str
    failed_check: str


@dataclass(frozen=True)
class ManifestWriterFixtureCase:
    case_dir: Path
    expected_kind: str
    case_name: str
    case_label: str
    case_metadata: dict[str, Any]
    manifest_writer_request: dict[str, Any]
    artifact_writer_result_pointer: dict[str, Any]
    artifact_body_generation_result_pointer: dict[str, Any]
    expected_manifest_writer_result: dict[str, Any]


@dataclass(frozen=True)
class ManifestWriterFixtureCaseResult:
    validation_status: str
    expected_status: str | None = None
    expected_category: str | None = None
    case_label: str | None = None
    case_id: str | None = None
    expected_kind: str | None = None
    reason_codes: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)
    checked_files_count: int = 0
    expected_manifest_file_written: bool | None = None
    expected_manifest_body_available: bool | None = None
    expected_manifest_path_available: bool | None = None
    expected_residue_file_count: int | None = None
    content_suppressed: bool = True
    manifest_body_suppressed: bool = True
    no_raw_rows: bool = True
    no_logits_dump: bool = True
    no_private_paths: bool = True
    no_absolute_paths: bool = True
    no_artifact_body_payload: bool = True
    no_generated_policy_body: bool = True
    no_manifest_body_nesting: bool = True
    no_request_body: bool = True
    no_pointer_body: bool = True
    no_expected_body: bool = True
    no_performance_claims: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    non_proof_notice_checked: bool = True
    path_policy_checked: bool = True
    content_policy_checked: bool = True
    release_quality_ready: bool = False
    validation_schema_version: str = VALIDATION_SCHEMA_VERSION

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "validation_schema_version": self.validation_schema_version,
            "validation_status": self.validation_status,
            "expected_status": self.expected_status,
            "expected_category": self.expected_category,
            "case_label": self.case_label,
            "case_id": self.case_id,
            "expected_kind": self.expected_kind,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "checked_files_count": self.checked_files_count,
            "expected_manifest_file_written": self.expected_manifest_file_written,
            "expected_manifest_body_available": self.expected_manifest_body_available,
            "expected_manifest_path_available": self.expected_manifest_path_available,
            "expected_residue_file_count": self.expected_residue_file_count,
            "content_suppressed": self.content_suppressed,
            "manifest_body_suppressed": self.manifest_body_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "no_logits_dump": self.no_logits_dump,
            "no_private_paths": self.no_private_paths,
            "no_absolute_paths": self.no_absolute_paths,
            "no_artifact_body_payload": self.no_artifact_body_payload,
            "no_generated_policy_body": self.no_generated_policy_body,
            "no_manifest_body_nesting": self.no_manifest_body_nesting,
            "no_request_body": self.no_request_body,
            "no_pointer_body": self.no_pointer_body,
            "no_expected_body": self.no_expected_body,
            "no_performance_claims": self.no_performance_claims,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
            "non_proof_notice_checked": self.non_proof_notice_checked,
            "path_policy_checked": self.path_policy_checked,
            "content_policy_checked": self.content_policy_checked,
            "release_quality_ready": self.release_quality_ready,
        }


@dataclass(frozen=True)
class ManifestWriterFixtureValidationSummary:
    mode: str = "manifest_writer_fixture_validation"
    total_cases: int = 0
    valid_cases: int = 0
    invalid_cases: int = 0
    pass_metadata_only_no_file_cases: int = 0
    pass_manifest_file_written_cases: int = 0
    usage_error_cases: int = 0
    fail_closed_cases: int = 0
    matched_cases: int = 0
    mismatched_cases: int = 0
    input_error_cases: int = 0
    reason_code_counts: dict[str, int] = field(default_factory=dict)
    content_suppressed: bool = True
    manifest_body_suppressed: bool = True
    no_raw_rows: bool = True
    no_logits_dump: bool = True
    no_private_paths: bool = True
    no_absolute_paths: bool = True
    no_artifact_body_payload: bool = True
    no_generated_policy_body: bool = True
    no_manifest_body_nesting: bool = True
    no_request_body: bool = True
    no_pointer_body: bool = True
    no_expected_body: bool = True
    no_performance_claims: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    non_proof_notice_checked: bool = True
    path_policy_checked: bool = True
    content_policy_checked: bool = True
    release_quality_ready: bool = False
    validation_schema_version: str = VALIDATION_SCHEMA_VERSION

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "validation_schema_version": self.validation_schema_version,
            "mode": self.mode,
            "total_cases": self.total_cases,
            "valid_cases": self.valid_cases,
            "invalid_cases": self.invalid_cases,
            "pass_metadata_only_no_file_cases": (
                self.pass_metadata_only_no_file_cases
            ),
            "pass_manifest_file_written_cases": self.pass_manifest_file_written_cases,
            "usage_error_cases": self.usage_error_cases,
            "fail_closed_cases": self.fail_closed_cases,
            "matched_cases": self.matched_cases,
            "mismatched_cases": self.mismatched_cases,
            "input_error_cases": self.input_error_cases,
            "reason_code_counts": dict(self.reason_code_counts),
            "content_suppressed": self.content_suppressed,
            "manifest_body_suppressed": self.manifest_body_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "no_logits_dump": self.no_logits_dump,
            "no_private_paths": self.no_private_paths,
            "no_absolute_paths": self.no_absolute_paths,
            "no_artifact_body_payload": self.no_artifact_body_payload,
            "no_generated_policy_body": self.no_generated_policy_body,
            "no_manifest_body_nesting": self.no_manifest_body_nesting,
            "no_request_body": self.no_request_body,
            "no_pointer_body": self.no_pointer_body,
            "no_expected_body": self.no_expected_body,
            "no_performance_claims": self.no_performance_claims,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
            "non_proof_notice_checked": self.non_proof_notice_checked,
            "path_policy_checked": self.path_policy_checked,
            "content_policy_checked": self.content_policy_checked,
            "release_quality_ready": self.release_quality_ready,
        }


def discover_manifest_writer_fixture_cases(
    fixture_root: Path,
) -> list[ManifestWriterFixtureCase]:
    return [
        load_manifest_writer_fixture_case(case_dir, expected_kind=case_dir.parent.name)
        for case_dir in _case_dirs(Path(fixture_root))
    ]


def load_manifest_writer_fixture_case(
    case_dir: Path,
    *,
    expected_kind: str | None = None,
) -> ManifestWriterFixtureCase:
    case_dir = Path(case_dir)
    kind = expected_kind or case_dir.parent.name
    case_name = case_dir.name
    case_label = f"{kind}/{case_name}"
    return ManifestWriterFixtureCase(
        case_dir=case_dir,
        expected_kind=kind,
        case_name=case_name,
        case_label=case_label,
        case_metadata=_read_json(case_dir / CASE_METADATA_FILE),
        manifest_writer_request=_read_json(case_dir / MANIFEST_WRITER_REQUEST_FILE),
        artifact_writer_result_pointer=_read_json(
            case_dir / ARTIFACT_WRITER_RESULT_POINTER_FILE
        ),
        artifact_body_generation_result_pointer=_read_json(
            case_dir / ARTIFACT_BODY_GENERATION_RESULT_POINTER_FILE
        ),
        expected_manifest_writer_result=_read_json(
            case_dir / EXPECTED_MANIFEST_WRITER_RESULT_FILE
        ),
    )


def validate_manifest_writer_fixture_case(
    case_dir: Path,
    expected_kind: str | None = None,
) -> ManifestWriterFixtureCaseResult:
    case_dir = Path(case_dir)
    kind = expected_kind or case_dir.parent.name
    case_label = f"{kind}/{case_dir.name}"
    try:
        shape_errors = _validate_required_file_shape(case_dir)
        if shape_errors:
            return _input_error_result(case_dir, shape_errors, expected_kind=kind)
        fixture = load_manifest_writer_fixture_case(case_dir, expected_kind=kind)
        contract_errors = _validate_fixture_contract(fixture)
        if contract_errors:
            return _contract_error_result(fixture, contract_errors)
        return _expected_case_result(fixture)
    except (OSError, json.JSONDecodeError, ValueError):
        return ManifestWriterFixtureCaseResult(
            validation_status="input_error",
            expected_status="input_error",
            expected_category="input_error",
            case_label=case_label,
            case_id=case_dir.name,
            expected_kind=kind,
            reason_codes=["malformed_fixture"],
            failed_checks=["json_parse_or_fixture_shape"],
            checked_files_count=_count_existing_required_files(case_dir),
        )


def validate_manifest_writer_fixture_root(
    fixture_root: Path,
) -> ManifestWriterFixtureValidationSummary:
    fixture_root = Path(fixture_root)
    root_errors = _validate_root_shape(fixture_root)
    if root_errors:
        return ManifestWriterFixtureValidationSummary(
            input_error_cases=1,
            reason_code_counts=dict(Counter(root_errors)),
        )

    matched_cases = 0
    mismatched_cases = 0
    input_error_cases = 0
    valid_cases = 0
    invalid_cases = 0
    category_counter: Counter[str] = Counter()
    reason_counter: Counter[str] = Counter()

    for case_dir in _case_dirs(fixture_root):
        if case_dir.parent.name == "valid":
            valid_cases += 1
        elif case_dir.parent.name == "invalid":
            invalid_cases += 1

        result = validate_manifest_writer_fixture_case(
            case_dir, expected_kind=case_dir.parent.name
        )
        reason_counter.update(result.reason_codes)
        if result.validation_status == "input_error":
            input_error_cases += 1
            continue
        if result.expected_category:
            category_counter[result.expected_category] += 1
        if _case_result_matches_expected(case_dir, result):
            matched_cases += 1
        else:
            mismatched_cases += 1

    return ManifestWriterFixtureValidationSummary(
        total_cases=matched_cases + mismatched_cases + input_error_cases,
        valid_cases=valid_cases,
        invalid_cases=invalid_cases,
        pass_metadata_only_no_file_cases=category_counter[
            "pass_metadata_only_no_file"
        ],
        pass_manifest_file_written_cases=category_counter[
            "pass_manifest_file_written"
        ],
        usage_error_cases=category_counter["usage_error_no_write"],
        fail_closed_cases=category_counter["fail_closed_no_write"],
        matched_cases=matched_cases,
        mismatched_cases=mismatched_cases,
        input_error_cases=input_error_cases,
        reason_code_counts=dict(sorted(reason_counter.items())),
    )


def summarize_manifest_writer_fixture_validation(
    summary: (
        ManifestWriterFixtureValidationSummary | ManifestWriterFixtureCaseResult
    ),
) -> str:
    return _format_safe_fields(summary.to_safe_dict())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog=(
            "python3 -m "
            "learner_state.frozen_policy_generation_manifest_writer_fixture_validation"
        ),
        description=(
            "Validate frozen policy generation manifest writer fixtures with "
            "body-free metadata-only output."
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
            "mode": "manifest_writer_fixture_validation",
            "validation_schema_version": VALIDATION_SCHEMA_VERSION,
            "validation_status": "internal_error",
            "content_suppressed": True,
            "manifest_body_suppressed": True,
            "no_raw_rows": True,
            "no_logits_dump": True,
            "no_private_paths": True,
            "no_absolute_paths": True,
            "synthetic_only_checked": True,
            "no_oracle_checked": True,
            "release_quality_ready": False,
        }
        print(_render_safe_dict(safe_payload, emit_json=bool(args.json)))
        return 1


def _run_root_cli(*, fixture_root: Path, emit_json: bool) -> int:
    summary = validate_manifest_writer_fixture_root(fixture_root)
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
    result = validate_manifest_writer_fixture_case(
        case_path, expected_kind=expected_kind
    )
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
    if any(ord(char) < 32 for char in case_selector):
        return "unsafe_fixture_case_selector"
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
    result: ManifestWriterFixtureCaseResult,
) -> bool:
    try:
        expected = _read_json(case_path / EXPECTED_MANIFEST_WRITER_RESULT_FILE)
    except (OSError, json.JSONDecodeError, ValueError):
        return False
    return _case_matches_expected(result, expected)


def _case_result_cli_payload(
    result: ManifestWriterFixtureCaseResult,
    *,
    matched: bool,
) -> dict[str, Any]:
    payload = result.to_safe_dict()
    payload.update(
        {
            "mode": "fixture_case",
            "actual_status": result.validation_status,
            "matched": matched,
        }
    )
    return payload


def _safe_case_error_payload(*, case_selector: str, reason_code: str) -> dict[str, Any]:
    return {
        "mode": "fixture_case",
        "validation_schema_version": VALIDATION_SCHEMA_VERSION,
        "case_id": case_selector,
        "expected_kind": "none",
        "expected_status": "input_error",
        "expected_category": "input_error",
        "actual_status": "input_error",
        "validation_status": "input_error",
        "matched": False,
        "reason_codes": [reason_code],
        "failed_checks": [reason_code],
        "content_suppressed": True,
        "manifest_body_suppressed": True,
        "no_raw_rows": True,
        "no_logits_dump": True,
        "no_private_paths": True,
        "no_absolute_paths": True,
        "no_artifact_body_payload": True,
        "no_generated_policy_body": True,
        "no_manifest_body_nesting": True,
        "no_request_body": True,
        "no_pointer_body": True,
        "no_expected_body": True,
        "no_performance_claims": True,
        "synthetic_only_checked": True,
        "no_oracle_checked": True,
        "non_proof_notice_checked": True,
        "path_policy_checked": True,
        "content_policy_checked": True,
        "release_quality_ready": False,
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


def _validate_fixture_contract(fixture: ManifestWriterFixtureCase) -> list[str]:
    errors: list[str] = []
    metadata = fixture.case_metadata
    request = fixture.manifest_writer_request
    artifact_pointer = fixture.artifact_writer_result_pointer
    body_pointer = fixture.artifact_body_generation_result_pointer
    expected = fixture.expected_manifest_writer_result

    errors.extend(_missing_fields(metadata, REQUIRED_CASE_METADATA_FIELDS))
    errors.extend(_missing_fields(request, REQUIRED_MANIFEST_WRITER_REQUEST_FIELDS))
    errors.extend(
        _missing_fields(artifact_pointer, REQUIRED_ARTIFACT_WRITER_POINTER_FIELDS)
    )
    errors.extend(_missing_fields(body_pointer, REQUIRED_ARTIFACT_BODY_POINTER_FIELDS))
    errors.extend(_missing_fields(expected, REQUIRED_EXPECTED_RESULT_FIELDS))
    if errors:
        return sorted(set(errors))

    if metadata.get("schema_version") != CASE_METADATA_SCHEMA_VERSION:
        errors.append("schema_version_unknown")
    if artifact_pointer.get("schema_version") != ARTIFACT_WRITER_RESULT_POINTER_SCHEMA_VERSION:
        errors.append("schema_version_unknown")
    if body_pointer.get("schema_version") != ARTIFACT_BODY_GENERATION_RESULT_POINTER_SCHEMA_VERSION:
        errors.append("schema_version_unknown")
    if expected.get("schema_version") != EXPECTED_MANIFEST_WRITER_RESULT_SCHEMA_VERSION:
        errors.append("schema_version_unknown")

    request_schema = request.get("schema_version")
    if request_schema != MANIFEST_WRITER_REQUEST_SCHEMA_VERSION:
        if not _is_expected_invalid_reason(fixture, "unknown_schema_version"):
            errors.append("schema_version_unknown")

    if metadata.get("case_id") != fixture.case_name:
        errors.append("case_id_mismatch")
    if expected.get("case_id") != fixture.case_name:
        errors.append("case_id_mismatch")
    if metadata.get("case_kind") != fixture.expected_kind:
        errors.append("case_id_mismatch")

    expected_category = expected.get("expected_category")
    expected_status = expected.get("expected_status")
    expected_exit_code = expected.get("expected_exit_code")
    if expected_category not in RESULT_CATEGORIES:
        errors.append("expected_category_unknown")
    if metadata.get("expected_category") != expected_category:
        errors.append("expected_category_mismatch")
    if metadata.get("expected_status") != expected_status:
        errors.append("expected_status_mismatch")
    if metadata.get("expected_exit_code") != expected_exit_code:
        errors.append("expected_exit_code_mismatch")
    if EXPECTED_STATUS_BY_CATEGORY.get(str(expected_category)) != expected_status:
        errors.append("expected_status_mismatch")

    if fixture.expected_kind == "valid":
        if fixture.case_label not in VALID_CASE_LABELS:
            errors.append("unexpected_case_label")
    elif fixture.expected_kind == "invalid":
        if fixture.case_label not in EXPECTED_INVALID_REASONS:
            errors.append("unexpected_case_label")
    else:
        errors.append("unknown_case_kind")

    errors.extend(_validate_expected_result_fields(expected))
    errors.extend(_validate_reason_code_contract(fixture))
    errors.extend(_validate_static_path_policy(fixture))
    errors.extend(_validate_static_content_policy(fixture))
    for payload in (metadata, request, artifact_pointer, body_pointer, expected):
        errors.extend(_scan_forbidden_values(payload))
    return sorted(set(errors))


def _validate_expected_result_fields(
    expected: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []
    boolean_fields = [
        "expected_manifest_file_written",
        "expected_manifest_body_available",
        "expected_manifest_path_available",
        "expected_manifest_path_safe_relative_only",
        "expected_manifest_json_parse_ok",
        "expected_manifest_allowed_keys_only",
        "expected_manifest_cleanup_ok",
        "expected_stdout_body_free",
        "expected_stderr_body_free",
        "expected_no_raw_rows",
        "expected_no_logits",
        "expected_no_private_paths",
        "expected_no_absolute_paths",
        "expected_no_raw_learner_text",
        "expected_no_artifact_body_payload",
        "expected_no_generated_policy_body",
        "expected_no_manifest_body_nesting",
        "expected_no_request_body",
        "expected_no_pointer_body",
        "expected_no_expected_body",
        "expected_no_performance_claim",
        "expected_no_real_data",
    ]
    for field_name in boolean_fields:
        if not isinstance(expected.get(field_name), bool):
            errors.append("expected_result_field_invalid")
    if not isinstance(expected.get("expected_residue_file_count"), int):
        errors.append("expected_result_field_invalid")
    if not isinstance(expected.get("expected_reason_codes"), list):
        errors.append("expected_result_field_invalid")
    if not isinstance(expected.get("expected_failed_checks"), list):
        errors.append("expected_result_field_invalid")
    flags = expected.get("expected_summary_flags")
    if not isinstance(flags, Mapping):
        errors.append("expected_summary_flags_invalid")
    else:
        required_true_flags = (
            "stdout_body_suppressed",
            "stderr_body_suppressed",
            "no_raw_rows",
            "no_logits_dump",
            "no_private_paths",
            "no_absolute_paths",
            "no_artifact_body_payload",
            "no_generated_policy_body",
            "no_manifest_body_nesting",
            "synthetic_only_checked",
            "no_oracle_checked",
            "non_proof_notice_checked",
            "path_policy_checked",
            "content_policy_checked",
            "cleanup_checked",
        )
        for field_name in required_true_flags:
            if flags.get(field_name) is not True:
                errors.append("expected_summary_flags_invalid")
        if flags.get("body_payload_printed") is not False:
            errors.append("expected_summary_flags_invalid")
        if flags.get("release_quality_ready") is not False:
            errors.append("expected_summary_flags_invalid")
    zero_counts = expected.get("expected_forbidden_counts_zero")
    if not isinstance(zero_counts, Mapping):
        errors.append("expected_forbidden_counts_invalid")
    else:
        for value in zero_counts.values():
            if value != 0:
                errors.append("expected_forbidden_counts_invalid")
    return errors


def _validate_reason_code_contract(
    fixture: ManifestWriterFixtureCase,
) -> list[str]:
    errors: list[str] = []
    metadata = fixture.case_metadata
    expected = fixture.expected_manifest_writer_result
    expected_reasons = _normalize_reason_codes(expected.get("expected_reason_codes"))
    expected_failed = _normalize_reason_codes(expected.get("expected_failed_checks"))
    allowed_reasons = list(metadata.get("allowed_failure_reason_codes", []))

    if sorted(allowed_reasons) != sorted(expected_reasons):
        errors.append("expected_reason_codes_mismatch")
    if sorted(expected_failed) != sorted(expected_reasons):
        errors.append("expected_failed_checks_mismatch")

    if fixture.expected_kind == "valid":
        expected_safe_rejection = VALID_SAFE_REJECTION_REASONS.get(fixture.case_label)
        if expected_safe_rejection:
            if expected_reasons != [expected_safe_rejection]:
                errors.append("expected_reason_codes_mismatch")
        elif expected_reasons:
            errors.append("expected_reason_codes_mismatch")
    elif fixture.expected_kind == "invalid":
        expected_reason = EXPECTED_INVALID_REASONS.get(fixture.case_label)
        if expected_reasons != [expected_reason]:
            errors.append("expected_reason_codes_mismatch")
    return errors


def _validate_static_path_policy(
    fixture: ManifestWriterFixtureCase,
) -> list[str]:
    errors: list[str] = []
    request = fixture.manifest_writer_request
    expected = fixture.expected_manifest_writer_result
    manifest_out = request.get("manifest_out")
    category = expected.get("expected_category")
    expected_reasons = set(
        _normalize_reason_codes(expected.get("expected_reason_codes"))
    )

    if request.get("manifest_output_root") != EXPECTED_MANIFEST_OUTPUT_ROOT:
        errors.append("manifest_output_root_mismatch")
    if expected.get("expected_manifest_path_safe_relative_only") is not True:
        errors.append("manifest_output_path_policy_mismatch")

    if category == "pass_metadata_only_no_file":
        if manifest_out is not None:
            errors.append("manifest_out_unexpected")
        if expected.get("expected_manifest_file_written") is not False:
            errors.append("expected_manifest_file_written_mismatch")
    elif category == "pass_manifest_file_written":
        if not isinstance(manifest_out, str) or not _is_safe_relative_json_path(
            manifest_out
        ):
            errors.append("manifest_out_unsafe")
        if expected.get("expected_manifest_file_written") is not True:
            errors.append("expected_manifest_file_written_mismatch")
    elif category == "usage_error_no_write":
        derived = _derive_path_reasons(manifest_out, request)
        if not expected_reasons.issubset(derived):
            errors.append("path_reason_mismatch")
        if expected.get("expected_manifest_file_written") is not False:
            errors.append("expected_manifest_file_written_mismatch")
    elif category == "fail_closed_no_write":
        if expected.get("expected_manifest_file_written") is not False:
            errors.append("expected_manifest_file_written_mismatch")

    if fixture.expected_kind == "valid" and category != "usage_error_no_write":
        if isinstance(manifest_out, str) and _derive_path_reasons(manifest_out, request):
            errors.append("valid_case_contains_unsafe_output_marker")
    return errors


def _validate_static_content_policy(
    fixture: ManifestWriterFixtureCase,
) -> list[str]:
    errors: list[str] = []
    request = fixture.manifest_writer_request
    artifact_pointer = fixture.artifact_writer_result_pointer
    body_pointer = fixture.artifact_body_generation_result_pointer
    expected = fixture.expected_manifest_writer_result
    expected_reasons = set(
        _normalize_reason_codes(expected.get("expected_reason_codes"))
    )
    category = expected.get("expected_category")

    if category in {"pass_metadata_only_no_file", "pass_manifest_file_written"}:
        for field_name in FORBIDDEN_INCLUDE_FLAG_REASONS:
            if request.get(field_name) is not False:
                errors.append("valid_case_forbidden_include_flag")
        for field_name in MISSING_NOTICE_REASONS:
            if request.get(field_name) is not True:
                errors.append("valid_case_notice_missing")

    for field_name, reason in FORBIDDEN_INCLUDE_FLAG_REASONS.items():
        if request.get(field_name) is True and reason not in expected_reasons:
            errors.append("content_reason_mismatch")
    for field_name, reason in MISSING_NOTICE_REASONS.items():
        if request.get(field_name) is False and reason not in expected_reasons:
            errors.append("content_reason_mismatch")

    for field_name in (
        "body_payload_suppressed",
        "generated_policy_body_suppressed",
        "manifest_body_suppressed",
        "raw_data_suppressed",
        "synthetic_only_checked",
        "no_oracle_checked",
        "safe_reference_only",
    ):
        if artifact_pointer.get(field_name) is not True:
            errors.append("artifact_pointer_safety_flag_mismatch")
    for field_name in (
        "artifact_body_payload_suppressed",
        "raw_data_suppressed",
        "synthetic_only_checked",
        "no_oracle_checked",
        "safe_reference_only",
    ):
        if body_pointer.get(field_name) is not True:
            errors.append("artifact_body_pointer_safety_flag_mismatch")
    if body_pointer.get("manifest_file_written") is not False:
        errors.append("artifact_body_pointer_manifest_file_mismatch")
    if body_pointer.get("manifest_body_generated") is not False:
        errors.append("artifact_body_pointer_manifest_body_mismatch")

    boolean_expected_safety_fields = (
        "expected_stdout_body_free",
        "expected_stderr_body_free",
        "expected_no_raw_rows",
        "expected_no_logits",
        "expected_no_private_paths",
        "expected_no_absolute_paths",
        "expected_no_raw_learner_text",
        "expected_no_artifact_body_payload",
        "expected_no_generated_policy_body",
        "expected_no_manifest_body_nesting",
        "expected_no_request_body",
        "expected_no_pointer_body",
        "expected_no_expected_body",
        "expected_no_performance_claim",
        "expected_no_real_data",
    )
    for field_name in boolean_expected_safety_fields:
        if expected.get(field_name) is not True:
            errors.append("expected_safety_field_mismatch")
    if expected.get("expected_manifest_body_available") is not False:
        errors.append("expected_manifest_body_available_mismatch")
    if expected.get("expected_residue_file_count") != 0:
        errors.append("expected_residue_file_count_mismatch")
    return errors


def _expected_case_result(
    fixture: ManifestWriterFixtureCase,
) -> ManifestWriterFixtureCaseResult:
    expected = fixture.expected_manifest_writer_result
    reason_codes = _normalize_reason_codes(expected.get("expected_reason_codes"))
    failed_checks = _normalize_reason_codes(expected.get("expected_failed_checks"))
    return ManifestWriterFixtureCaseResult(
        validation_status=str(expected.get("expected_status")),
        expected_status=str(expected.get("expected_status")),
        expected_category=str(expected.get("expected_category")),
        case_label=fixture.case_label,
        case_id=fixture.case_name,
        expected_kind=fixture.expected_kind,
        reason_codes=reason_codes,
        failed_checks=failed_checks,
        checked_files_count=len(REQUIRED_FILES),
        expected_manifest_file_written=bool(
            expected.get("expected_manifest_file_written")
        ),
        expected_manifest_body_available=bool(
            expected.get("expected_manifest_body_available")
        ),
        expected_manifest_path_available=bool(
            expected.get("expected_manifest_path_available")
        ),
        expected_residue_file_count=int(expected.get("expected_residue_file_count")),
    )


def _contract_error_result(
    fixture: ManifestWriterFixtureCase,
    errors: list[str],
) -> ManifestWriterFixtureCaseResult:
    return ManifestWriterFixtureCaseResult(
        validation_status="input_error",
        expected_status="input_error",
        expected_category="input_error",
        case_label=fixture.case_label,
        case_id=fixture.case_name,
        expected_kind=fixture.expected_kind,
        reason_codes=sorted(set(errors)),
        failed_checks=sorted(set(errors)),
        checked_files_count=len(REQUIRED_FILES),
    )


def _input_error_result(
    case_dir: Path,
    errors: list[str],
    *,
    expected_kind: str,
) -> ManifestWriterFixtureCaseResult:
    return ManifestWriterFixtureCaseResult(
        validation_status="input_error",
        expected_status="input_error",
        expected_category="input_error",
        case_label=f"{expected_kind}/{case_dir.name}",
        case_id=case_dir.name,
        expected_kind=expected_kind,
        reason_codes=sorted(set(errors)),
        failed_checks=sorted(set(errors)),
        checked_files_count=_count_existing_required_files(case_dir),
    )


def _case_matches_expected(
    result: ManifestWriterFixtureCaseResult,
    expected: Mapping[str, Any],
) -> bool:
    return (
        result.validation_status == expected.get("expected_status")
        and result.expected_status == expected.get("expected_status")
        and result.expected_category == expected.get("expected_category")
        and sorted(result.reason_codes)
        == sorted(_normalize_reason_codes(expected.get("expected_reason_codes")))
        and sorted(result.failed_checks)
        == sorted(_normalize_reason_codes(expected.get("expected_failed_checks")))
    )


def _derive_path_reasons(
    manifest_out: Any,
    request: Mapping[str, Any],
) -> set[str]:
    reasons: set[str] = set()
    path = "" if manifest_out is None else str(manifest_out)
    if not path:
        return reasons
    pure_path = PurePosixPath(path)
    parts = pure_path.parts
    if "ABSOLUTE_PATH_SENTINEL" in path:
        reasons.add("absolute_manifest_output_path")
    if "HOME_PATH_SENTINEL" in path:
        reasons.add("home_manifest_output_path")
    if ".." in parts:
        reasons.add("parent_traversal_manifest_output_path")
    if "CLOUD_MARKER_SENTINEL" in path:
        reasons.add("cloud_marker_manifest_output_path")
    if "PRIVATE_MARKER_SENTINEL" in path:
        reasons.add("private_marker_manifest_output_path")
    if any(part.startswith(".private") for part in parts):
        reasons.add("hidden_private_manifest_directory")
    if not path.endswith(".json"):
        reasons.add("non_json_manifest_extension")
    if not SAFE_RELATIVE_MANIFEST_OUT_PATTERN.fullmatch(path):
        reasons.add("unsafe_manifest_filename")
    if len(path) > 160:
        reasons.add("too_long_manifest_path")
    if "existing_manifest_metadata_only.json" in path and not request.get(
        "allow_overwrite"
    ):
        reasons.add("overwrite_without_policy")
    if LOCAL_ABSOLUTE_PATH_PATTERN.search(path):
        reasons.add("absolute_manifest_output_path")
    return reasons


def _is_safe_relative_json_path(path: str) -> bool:
    pure_path = PurePosixPath(path)
    if path.startswith(("/", "~")) or "\\" in path or re.match(r"^[A-Za-z]:", path):
        return False
    if ".." in pure_path.parts or "." in pure_path.parts:
        return False
    if not path.endswith(".json"):
        return False
    return SAFE_RELATIVE_MANIFEST_OUT_PATTERN.fullmatch(path) is not None


def _scan_forbidden_values(payload: Any) -> list[str]:
    errors: list[str] = []
    if isinstance(payload, Mapping):
        for value in payload.values():
            errors.extend(_scan_forbidden_values(value))
    elif isinstance(payload, list):
        for value in payload:
            errors.extend(_scan_forbidden_values(value))
    elif isinstance(payload, str):
        for fragment in FORBIDDEN_VALUE_FRAGMENTS:
            if fragment in payload:
                errors.append("forbidden_payload_value")
    return errors


def _is_expected_invalid_reason(
    fixture: ManifestWriterFixtureCase,
    reason_code: str,
) -> bool:
    return (
        fixture.expected_kind == "invalid"
        and EXPECTED_INVALID_REASONS.get(fixture.case_label) == reason_code
        and reason_code
        in _normalize_reason_codes(
            fixture.expected_manifest_writer_result.get("expected_reason_codes")
        )
    )


def _normalize_reason_codes(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item) != "none"]


def _missing_fields(
    payload: Mapping[str, Any],
    required_fields: tuple[str, ...],
) -> list[str]:
    return [
        "missing_required_field"
        for field_name in required_fields
        if field_name not in payload
    ]


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"fixture JSON must be an object: {path.name}")
    return payload


def _case_dirs(root: Path) -> list[Path]:
    return sorted(
        path
        for category in ("valid", "invalid")
        for path in (root / category).glob("*")
        if path.is_dir()
    )


def _count_existing_required_files(case_dir: Path) -> int:
    return sum(1 for file_name in REQUIRED_FILES if (case_dir / file_name).is_file())


if __name__ == "__main__":
    sys.exit(main())
