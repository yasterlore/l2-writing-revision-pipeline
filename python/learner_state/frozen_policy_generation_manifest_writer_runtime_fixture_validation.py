"""Static validation for manifest writer runtime fixtures.

This module validates synthetic metadata-only runtime fixture contracts for a
future manifest writer. It does not implement or execute a manifest writer,
generate manifest bodies, write manifest files, connect artifact writer CLI
output, train models, or compute metrics.
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
EXPECTED_RUNTIME_RESULT_FILE = "expected_manifest_writer_runtime_result.json"

CASE_METADATA_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_runtime_case_metadata_v0.1"
)
MANIFEST_WRITER_REQUEST_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_runtime_request_v0.1"
)
ARTIFACT_WRITER_RESULT_POINTER_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_runtime_artifact_writer_result_pointer_v0.1"
)
ARTIFACT_BODY_GENERATION_RESULT_POINTER_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_runtime_artifact_body_generation_result_pointer_v0.1"
)
EXPECTED_RUNTIME_RESULT_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_runtime_expected_result_v0.1"
)
FUTURE_RUNTIME_RESULT_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_result_v0.1"
)
VALIDATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_runtime_fixture_validation_v0.1"
)

DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime"
)
EXPECTED_VALID_CASES = 5
EXPECTED_INVALID_CASES = 26
EXPECTED_TOTAL_CASES = 31
EXPECTED_JSON_FILE_COUNT = EXPECTED_TOTAL_CASES * 5
EXPECTED_JSON_FILES_PER_CASE = 5

ARTIFACT_WRITER_RESULT_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_result_v0.1"
)
ARTIFACT_BODY_GENERATION_RESULT_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_result_v0.1"
)

REQUIRED_FILES = (
    CASE_METADATA_FILE,
    MANIFEST_WRITER_REQUEST_FILE,
    ARTIFACT_WRITER_RESULT_POINTER_FILE,
    ARTIFACT_BODY_GENERATION_RESULT_POINTER_FILE,
    EXPECTED_RUNTIME_RESULT_FILE,
)

EXPECTED_CATEGORY_COUNTS = {
    "pass_metadata_only_no_file": 5,
    "usage_error_no_write": 8,
    "fail_closed_no_write": 18,
}

RESULT_CATEGORIES = frozenset(
    {
        "pass_metadata_only_no_file",
        "usage_error_no_write",
        "fail_closed_no_write",
        "input_error",
        "mismatch",
    }
)

EXPECTED_STATUS_BY_CATEGORY = {
    "pass_metadata_only_no_file": "pass",
    "usage_error_no_write": "usage_error",
    "fail_closed_no_write": "fail_closed",
}

VALID_CASE_LABELS = frozenset(
    {
        "valid/metadata_only_minimal_no_file",
        "valid/metadata_only_with_artifact_body_reference",
        "valid/metadata_only_with_release_quality_reference",
        "valid/metadata_only_safe_ids_and_counts",
        "valid/metadata_only_no_artifact_body_available",
    }
)

EXPECTED_INVALID_REASONS = {
    "invalid/missing_artifact_result_pointer": "missing_artifact_result_pointer",
    "invalid/missing_artifact_body_result_pointer": (
        "missing_artifact_body_result_pointer"
    ),
    "invalid/malformed_artifact_result_pointer": "malformed_artifact_result_pointer",
    "invalid/malformed_artifact_body_result_pointer": (
        "malformed_artifact_body_result_pointer"
    ),
    "invalid/unknown_artifact_writer_result_schema": (
        "unknown_artifact_writer_result_schema"
    ),
    "invalid/unknown_artifact_body_generation_result_schema": (
        "unknown_artifact_body_generation_result_schema"
    ),
    "invalid/generated_policy_body_leakage": "generated_policy_body_leakage",
    "invalid/artifact_body_payload_leakage": "artifact_body_payload_leakage",
    "invalid/manifest_body_requested": "manifest_body_requested",
    "invalid/manifest_json_body_requested": "manifest_json_body_requested",
    "invalid/request_body_leakage": "request_body_leakage",
    "invalid/pointer_body_leakage": "pointer_body_leakage",
    "invalid/expected_body_leakage": "expected_body_leakage",
    "invalid/raw_rows_leakage": "raw_rows_leakage",
    "invalid/logits_dump_leakage": "logits_dump_leakage",
    "invalid/private_path_leakage": "private_path_leakage",
    "invalid/absolute_path_leakage": "absolute_path_leakage",
    "invalid/raw_learner_text_leakage": "raw_learner_text_leakage",
    "invalid/performance_claim": "performance_claim",
    "invalid/missing_synthetic_notice": "missing_synthetic_notice",
    "invalid/missing_no_oracle_notice": "missing_no_oracle_notice",
    "invalid/missing_non_proof_notice": "missing_non_proof_notice",
    "invalid/unsafe_manifest_output_path": "unsafe_manifest_output_path",
    "invalid/overwrite_without_policy": "overwrite_without_policy",
    "invalid/unsupported_artifact_writer_cli_integration": (
        "unsupported_artifact_writer_cli_integration"
    ),
    "invalid/real_data_marker": "real_data_marker",
}

EXPECTED_REASON_CODES = frozenset(EXPECTED_INVALID_REASONS.values())

REQUIRED_CASE_METADATA_FIELDS = (
    "schema_version",
    "case_id",
    "case_kind",
    "description",
    "source_artifact_writer_case",
    "source_artifact_body_case",
    "expected_category",
    "expected_exit_code",
    "expected_manifest_writer_mode",
    "expected_reason_codes",
    "expected_writer_status",
    "forbidden_output_markers",
    "forbidden_summary_fields",
    "notes",
    "required_summary_fields",
    "safety_expectation",
    "should_leave_residue",
    "should_write_manifest_file",
)

REQUIRED_REQUEST_FIELDS = (
    "schema_version",
    "request_id",
    "manifest_writer_mode",
    "include_manifest_body",
    "allow_manifest_file_writing",
    "manifest_out",
    "overwrite_policy",
    "synthetic_notice",
    "no_oracle_notice",
    "non_proof_notice",
    "validation_reference_ids",
    "release_quality_reference_ids",
)

REQUIRED_POINTER_FIELDS = (
    "schema_version",
    "pointer_id",
    "source_kind",
    "source_fixture_id",
    "safe_metadata_reference_id",
    "include_body_payload",
    "include_raw_rows",
    "include_private_paths",
)

REQUIRED_EXPECTED_RESULT_FIELDS = (
    "schema_version",
    "case_id",
    "expected_category",
    "expected_writer_status",
    "expected_manifest_writer_mode",
    "expected_reason_codes",
    "expected_failed_checks",
    "expected_manifest_body_available",
    "expected_manifest_file_written",
    "expected_manifest_output_path_available",
    "expected_release_quality_ready",
    "expected_safety_flags",
    "expected_count_summary",
    "expected_safe_summary",
)

REQUIRED_TRUE_SAFETY_FLAGS = (
    "content_suppressed",
    "manifest_body_suppressed",
    "no_raw_rows",
    "no_logits_dump",
    "no_private_paths",
    "no_absolute_paths",
    "no_artifact_body_payload",
    "no_generated_policy_body",
    "no_manifest_body_nesting",
    "no_request_body",
    "no_pointer_body",
    "no_expected_body",
    "no_performance_claims",
    "synthetic_only_checked",
    "no_oracle_checked",
    "non_proof_notice_checked",
    "path_policy_checked",
    "content_policy_checked",
    "file_writing_checked",
)

REQUIRED_ZERO_COUNT_FIELDS = (
    "raw_row_count",
    "logits_dump_count",
    "private_path_count",
    "absolute_path_count",
    "artifact_body_payload_count",
    "generated_policy_body_count",
    "manifest_body_count",
    "request_body_count",
    "pointer_body_count",
    "expected_body_count",
    "performance_metric_count",
    "written_file_count",
)

EXPECTED_MISSING_NOTICE_REASONS = {
    "synthetic_notice": "missing_synthetic_notice",
    "no_oracle_notice": "missing_no_oracle_notice",
    "non_proof_notice": "missing_non_proof_notice",
}

SAFE_CASE_SELECTOR_PATTERN = re.compile(r"^[a-z0-9_/-]+$")

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
    "manifest json body" " value",
    "request body" " value",
    "pointer body" " value",
    "expected body" " value",
    "logit" "_values",
    "probability" "_values",
    "real" "_participant",
    "participant_id" "_real",
    "production_data" "_reference",
)


@dataclass(frozen=True)
class ManifestWriterRuntimeFixtureValidationError(Exception):
    """Safe runtime fixture validation error."""

    reason_code: str
    failed_check: str


@dataclass(frozen=True)
class ManifestWriterRuntimeFixtureCase:
    case_dir: Path
    expected_kind: str
    case_name: str
    case_label: str
    case_metadata: dict[str, Any]
    manifest_writer_request: dict[str, Any]
    artifact_writer_result_pointer: dict[str, Any]
    artifact_body_generation_result_pointer: dict[str, Any]
    expected_manifest_writer_runtime_result: dict[str, Any]


@dataclass(frozen=True)
class ManifestWriterRuntimeFixtureCaseResult:
    validation_status: str
    expected_status: str | None = None
    expected_category: str | None = None
    case_label: str | None = None
    case_id: str | None = None
    expected_kind: str | None = None
    reason_codes: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)
    checked_files_count: int = 0
    expected_manifest_writer_mode: str | None = None
    expected_manifest_body_available: bool | None = None
    expected_manifest_file_written: bool | None = None
    expected_manifest_output_path_available: bool | None = None
    expected_release_quality_ready: bool | None = None
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
    runtime_writer_executed: bool = False
    manifest_file_written: bool = False
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
            "expected_manifest_writer_mode": self.expected_manifest_writer_mode,
            "expected_manifest_body_available": (
                self.expected_manifest_body_available
            ),
            "expected_manifest_file_written": self.expected_manifest_file_written,
            "expected_manifest_output_path_available": (
                self.expected_manifest_output_path_available
            ),
            "expected_release_quality_ready": self.expected_release_quality_ready,
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
            "runtime_writer_executed": self.runtime_writer_executed,
            "manifest_file_written": self.manifest_file_written,
            "release_quality_ready": self.release_quality_ready,
        }


@dataclass(frozen=True)
class ManifestWriterRuntimeFixtureValidationSummary:
    mode: str = "manifest_writer_runtime_fixture_validation"
    total_cases: int = 0
    valid_cases: int = 0
    invalid_cases: int = 0
    pass_metadata_only_no_file_cases: int = 0
    usage_error_cases: int = 0
    fail_closed_cases: int = 0
    matched_cases: int = 0
    mismatched_cases: int = 0
    input_error_cases: int = 0
    total_json_files: int = 0
    json_files_per_case: int = EXPECTED_JSON_FILES_PER_CASE
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
    runtime_writer_executed: bool = False
    manifest_file_written: bool = False
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
            "usage_error_cases": self.usage_error_cases,
            "fail_closed_cases": self.fail_closed_cases,
            "matched_cases": self.matched_cases,
            "mismatched_cases": self.mismatched_cases,
            "input_error_cases": self.input_error_cases,
            "total_json_files": self.total_json_files,
            "json_files_per_case": self.json_files_per_case,
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
            "runtime_writer_executed": self.runtime_writer_executed,
            "manifest_file_written": self.manifest_file_written,
            "release_quality_ready": self.release_quality_ready,
        }


def validate_manifest_writer_runtime_fixture_case(
    case_dir: Path,
    expected_kind: str | None = None,
) -> ManifestWriterRuntimeFixtureCaseResult:
    case_dir = Path(case_dir)
    kind = expected_kind or case_dir.parent.name
    case_label = f"{kind}/{case_dir.name}"
    try:
        shape_errors = _validate_required_file_shape(case_dir)
        if shape_errors:
            return _input_error_result(case_dir, shape_errors, expected_kind=kind)
        fixture = _load_fixture_case(case_dir, expected_kind=kind)
        contract_errors = _validate_fixture_contract(fixture)
        if contract_errors:
            return _contract_error_result(fixture, contract_errors)
        return _expected_case_result(fixture)
    except (OSError, json.JSONDecodeError, ValueError):
        return ManifestWriterRuntimeFixtureCaseResult(
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


def validate_manifest_writer_runtime_fixture_root(
    fixture_root: Path,
) -> ManifestWriterRuntimeFixtureValidationSummary:
    fixture_root = Path(fixture_root)
    root_errors = _validate_root_shape(fixture_root)
    if root_errors:
        return ManifestWriterRuntimeFixtureValidationSummary(
            input_error_cases=1,
            reason_code_counts=dict(Counter(root_errors)),
            total_json_files=_count_json_files(fixture_root),
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

        result = validate_manifest_writer_runtime_fixture_case(
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

    return ManifestWriterRuntimeFixtureValidationSummary(
        total_cases=matched_cases + mismatched_cases + input_error_cases,
        valid_cases=valid_cases,
        invalid_cases=invalid_cases,
        pass_metadata_only_no_file_cases=category_counter[
            "pass_metadata_only_no_file"
        ],
        usage_error_cases=category_counter["usage_error_no_write"],
        fail_closed_cases=category_counter["fail_closed_no_write"],
        matched_cases=matched_cases,
        mismatched_cases=mismatched_cases,
        input_error_cases=input_error_cases,
        total_json_files=_count_json_files(fixture_root),
        reason_code_counts=dict(sorted(reason_counter.items())),
    )


def summarize_manifest_writer_runtime_fixture_validation(
    summary: (
        ManifestWriterRuntimeFixtureValidationSummary
        | ManifestWriterRuntimeFixtureCaseResult
    ),
) -> str:
    return _format_safe_fields(summary.to_safe_dict())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog=(
            "python3 -m "
            "learner_state.frozen_policy_generation_manifest_writer_runtime_fixture_validation"
        ),
        description=(
            "Validate frozen policy generation manifest writer runtime fixtures "
            "with body-free metadata-only output."
        ),
    )
    parser.add_argument(
        "--fixture-root",
        default=str(DEFAULT_FIXTURE_ROOT),
        help="Runtime fixture root to validate.",
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
            "mode": "manifest_writer_runtime_fixture_validation",
            "validation_schema_version": VALIDATION_SCHEMA_VERSION,
            "validation_status": "internal_error",
            "content_suppressed": True,
            "manifest_body_suppressed": True,
            "no_raw_rows": True,
            "no_logits_dump": True,
            "no_private_paths": True,
            "no_absolute_paths": True,
            "runtime_writer_executed": False,
            "manifest_file_written": False,
            "release_quality_ready": False,
        }
        print(_render_safe_dict(safe_payload, emit_json=bool(args.json)))
        return 1


def _run_root_cli(*, fixture_root: Path, emit_json: bool) -> int:
    summary = validate_manifest_writer_runtime_fixture_root(fixture_root)
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
    result = validate_manifest_writer_runtime_fixture_case(
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


def _load_fixture_case(
    case_dir: Path,
    *,
    expected_kind: str,
) -> ManifestWriterRuntimeFixtureCase:
    case_dir = Path(case_dir)
    case_name = case_dir.name
    return ManifestWriterRuntimeFixtureCase(
        case_dir=case_dir,
        expected_kind=expected_kind,
        case_name=case_name,
        case_label=f"{expected_kind}/{case_name}",
        case_metadata=_read_json(case_dir / CASE_METADATA_FILE),
        manifest_writer_request=_read_json(case_dir / MANIFEST_WRITER_REQUEST_FILE),
        artifact_writer_result_pointer=_read_json(
            case_dir / ARTIFACT_WRITER_RESULT_POINTER_FILE
        ),
        artifact_body_generation_result_pointer=_read_json(
            case_dir / ARTIFACT_BODY_GENERATION_RESULT_POINTER_FILE
        ),
        expected_manifest_writer_runtime_result=_read_json(
            case_dir / EXPECTED_RUNTIME_RESULT_FILE
        ),
    )


def _case_result_matches_expected(
    case_path: Path,
    result: ManifestWriterRuntimeFixtureCaseResult,
) -> bool:
    try:
        expected = _read_json(case_path / EXPECTED_RUNTIME_RESULT_FILE)
    except (OSError, json.JSONDecodeError, ValueError):
        return False
    return _case_matches_expected(result, expected)


def _case_matches_expected(
    result: ManifestWriterRuntimeFixtureCaseResult,
    expected: Mapping[str, Any],
) -> bool:
    return (
        result.validation_status == expected.get("expected_writer_status")
        and result.expected_category == expected.get("expected_category")
        and result.expected_manifest_writer_mode
        == expected.get("expected_manifest_writer_mode")
        and sorted(result.reason_codes)
        == sorted(_normalize_reason_codes(expected.get("expected_reason_codes")))
        and sorted(result.failed_checks)
        == sorted(_normalize_reason_codes(expected.get("expected_failed_checks")))
        and result.expected_manifest_body_available
        == expected.get("expected_manifest_body_available")
        and result.expected_manifest_file_written
        == expected.get("expected_manifest_file_written")
        and result.expected_manifest_output_path_available
        == expected.get("expected_manifest_output_path_available")
        and result.expected_release_quality_ready
        == expected.get("expected_release_quality_ready")
    )


def _case_result_cli_payload(
    result: ManifestWriterRuntimeFixtureCaseResult,
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
        "runtime_writer_executed": False,
        "manifest_file_written": False,
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
    if _count_json_files(root) != EXPECTED_JSON_FILE_COUNT:
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


def _validate_fixture_contract(
    fixture: ManifestWriterRuntimeFixtureCase,
) -> list[str]:
    errors: list[str] = []
    metadata = fixture.case_metadata
    request = fixture.manifest_writer_request
    artifact_pointer = fixture.artifact_writer_result_pointer
    body_pointer = fixture.artifact_body_generation_result_pointer
    expected = fixture.expected_manifest_writer_runtime_result

    errors.extend(_missing_fields(metadata, REQUIRED_CASE_METADATA_FIELDS))
    errors.extend(_missing_fields(request, REQUIRED_REQUEST_FIELDS))
    errors.extend(_missing_fields(artifact_pointer, REQUIRED_POINTER_FIELDS))
    errors.extend(_missing_fields(body_pointer, REQUIRED_POINTER_FIELDS))
    errors.extend(_missing_fields(expected, REQUIRED_EXPECTED_RESULT_FIELDS))
    if errors:
        return sorted(set(errors))

    errors.extend(_validate_schema_versions(fixture))
    errors.extend(_validate_case_identity(fixture))
    errors.extend(_validate_expected_category_and_status(fixture))
    errors.extend(_validate_request_policy(fixture))
    errors.extend(_validate_pointer_policy(fixture))
    errors.extend(_validate_expected_result_policy(fixture))
    errors.extend(_validate_path_policy(fixture))
    errors.extend(_validate_content_policy(fixture))
    errors.extend(_validate_notice_policy(fixture))
    errors.extend(_validate_reason_code_contract(fixture))
    for payload in (metadata, request, artifact_pointer, body_pointer, expected):
        errors.extend(_scan_forbidden_values(payload))
    return sorted(set(errors))


def _validate_schema_versions(
    fixture: ManifestWriterRuntimeFixtureCase,
) -> list[str]:
    errors: list[str] = []
    if fixture.case_metadata.get("schema_version") != CASE_METADATA_SCHEMA_VERSION:
        errors.append("schema_version_unknown")
    if (
        fixture.manifest_writer_request.get("schema_version")
        != MANIFEST_WRITER_REQUEST_SCHEMA_VERSION
    ):
        errors.append("schema_version_unknown")
    if (
        fixture.artifact_writer_result_pointer.get("schema_version")
        != ARTIFACT_WRITER_RESULT_POINTER_SCHEMA_VERSION
    ):
        errors.append("schema_version_unknown")
    if (
        fixture.artifact_body_generation_result_pointer.get("schema_version")
        != ARTIFACT_BODY_GENERATION_RESULT_POINTER_SCHEMA_VERSION
    ):
        errors.append("schema_version_unknown")
    expected = fixture.expected_manifest_writer_runtime_result
    if expected.get("schema_version") != EXPECTED_RUNTIME_RESULT_SCHEMA_VERSION:
        errors.append("schema_version_unknown")
    if expected.get("future_result_schema_version") != FUTURE_RUNTIME_RESULT_SCHEMA_VERSION:
        errors.append("schema_version_unknown")
    return errors


def _validate_case_identity(
    fixture: ManifestWriterRuntimeFixtureCase,
) -> list[str]:
    errors: list[str] = []
    if fixture.case_metadata.get("case_id") != fixture.case_name:
        errors.append("case_id_mismatch")
    if (
        fixture.expected_manifest_writer_runtime_result.get("case_id")
        != fixture.case_name
    ):
        errors.append("case_id_mismatch")
    if fixture.case_metadata.get("case_kind") != fixture.expected_kind:
        errors.append("case_id_mismatch")
    if fixture.expected_kind == "valid":
        if fixture.case_label not in VALID_CASE_LABELS:
            errors.append("unexpected_case_label")
    elif fixture.expected_kind == "invalid":
        if fixture.case_label not in EXPECTED_INVALID_REASONS:
            errors.append("unexpected_case_label")
    else:
        errors.append("unknown_case_kind")
    return errors


def _validate_expected_category_and_status(
    fixture: ManifestWriterRuntimeFixtureCase,
) -> list[str]:
    errors: list[str] = []
    metadata = fixture.case_metadata
    expected = fixture.expected_manifest_writer_runtime_result
    expected_category = expected.get("expected_category")
    expected_status = expected.get("expected_writer_status")
    if expected_category not in RESULT_CATEGORIES:
        errors.append("expected_category_unknown")
    if metadata.get("expected_category") != expected_category:
        errors.append("expected_category_mismatch")
    if metadata.get("expected_writer_status") != expected_status:
        errors.append("expected_status_mismatch")
    if metadata.get("expected_manifest_writer_mode") != expected.get(
        "expected_manifest_writer_mode"
    ):
        errors.append("expected_mode_mismatch")
    if metadata.get("expected_reason_codes") != expected.get("expected_reason_codes"):
        errors.append("expected_reason_codes_mismatch")
    if EXPECTED_STATUS_BY_CATEGORY.get(str(expected_category)) != expected_status:
        errors.append("expected_status_mismatch")
    return errors


def _validate_request_policy(
    fixture: ManifestWriterRuntimeFixtureCase,
) -> list[str]:
    errors: list[str] = []
    request = fixture.manifest_writer_request
    if request.get("manifest_writer_mode") != "metadata_only_no_file":
        errors.append("request_policy_mismatch")
    if not isinstance(request.get("validation_reference_ids"), list):
        errors.append("request_policy_mismatch")
    if not isinstance(request.get("release_quality_reference_ids"), list):
        errors.append("request_policy_mismatch")

    expected_reasons = _expected_reason_codes(fixture)
    if fixture.expected_kind == "valid":
        if request.get("include_manifest_body") is not False:
            errors.append("request_policy_mismatch")
        if request.get("allow_manifest_file_writing") is not False:
            errors.append("request_policy_mismatch")
        if request.get("manifest_out") is not None:
            errors.append("request_policy_mismatch")
        for field_name in EXPECTED_MISSING_NOTICE_REASONS:
            if request.get(field_name) is not True:
                errors.append("request_policy_mismatch")
        if request.get("requested_artifact_writer_cli_integration") is True:
            errors.append("request_policy_mismatch")
    else:
        if (
            request.get("include_manifest_body") is True
            and "manifest_body_requested" not in expected_reasons
        ):
            errors.append("request_policy_mismatch")
        if (
            request.get("requested_artifact_writer_cli_integration") is True
            and "unsupported_artifact_writer_cli_integration" not in expected_reasons
        ):
            errors.append("request_policy_mismatch")
        for field_name, reason in EXPECTED_MISSING_NOTICE_REASONS.items():
            if request.get(field_name) is not True and reason not in expected_reasons:
                errors.append("request_policy_mismatch")
    return errors


def _validate_pointer_policy(
    fixture: ManifestWriterRuntimeFixtureCase,
) -> list[str]:
    errors: list[str] = []
    expected_reasons = _expected_reason_codes(fixture)
    artifact_pointer = fixture.artifact_writer_result_pointer
    body_pointer = fixture.artifact_body_generation_result_pointer

    errors.extend(
        _validate_pointer_common(
            artifact_pointer,
            expected_source_kind="artifact_writer_result_summary",
            expected_schema=ARTIFACT_WRITER_RESULT_SCHEMA_VERSION,
            missing_reason="missing_artifact_result_pointer",
            malformed_reason="malformed_artifact_result_pointer",
            unknown_schema_reason="unknown_artifact_writer_result_schema",
            expected_reasons=expected_reasons,
        )
    )
    errors.extend(
        _validate_pointer_common(
            body_pointer,
            expected_source_kind="artifact_body_generation_result_summary",
            expected_schema=ARTIFACT_BODY_GENERATION_RESULT_SCHEMA_VERSION,
            missing_reason="missing_artifact_body_result_pointer",
            malformed_reason="malformed_artifact_body_result_pointer",
            unknown_schema_reason="unknown_artifact_body_generation_result_schema",
            expected_reasons=expected_reasons,
        )
    )
    return errors


def _validate_pointer_common(
    pointer: Mapping[str, Any],
    *,
    expected_source_kind: str,
    expected_schema: str,
    missing_reason: str,
    malformed_reason: str,
    unknown_schema_reason: str,
    expected_reasons: list[str],
) -> list[str]:
    errors: list[str] = []
    if pointer.get("source_kind") != expected_source_kind:
        errors.append("pointer_policy_mismatch")
    if not pointer.get("safe_metadata_reference_id"):
        if missing_reason not in expected_reasons:
            errors.append("pointer_policy_mismatch")
    if pointer.get("safe_violation_sentinel") == malformed_reason:
        if malformed_reason not in expected_reasons:
            errors.append("pointer_policy_mismatch")
    if pointer.get("result_schema_version") != expected_schema:
        if unknown_schema_reason not in expected_reasons:
            errors.append("pointer_policy_mismatch")
    if pointer.get("safe_reference_only") is not True:
        errors.append("pointer_policy_mismatch")
    if pointer.get("include_body_payload") is True:
        if "artifact_body_payload_leakage" not in expected_reasons:
            errors.append("pointer_policy_mismatch")
    if pointer.get("include_raw_rows") is True:
        if "raw_rows_leakage" not in expected_reasons:
            errors.append("pointer_policy_mismatch")
    if pointer.get("include_private_paths") is True:
        if not {
            "private_path_leakage",
            "absolute_path_leakage",
        }.intersection(expected_reasons):
            errors.append("pointer_policy_mismatch")
    return errors


def _validate_expected_result_policy(
    fixture: ManifestWriterRuntimeFixtureCase,
) -> list[str]:
    errors: list[str] = []
    expected = fixture.expected_manifest_writer_runtime_result
    boolean_fields = (
        "expected_manifest_body_available",
        "expected_manifest_file_written",
        "expected_manifest_output_path_available",
        "expected_release_quality_ready",
        "expected_no_real_data",
    )
    for field_name in boolean_fields:
        if not isinstance(expected.get(field_name), bool):
            errors.append("expected_result_policy_mismatch")
    if expected.get("expected_manifest_body_available") is not False:
        errors.append("expected_result_policy_mismatch")
    if expected.get("expected_manifest_file_written") is not False:
        errors.append("expected_result_policy_mismatch")
    if expected.get("expected_release_quality_ready") is not False:
        errors.append("expected_result_policy_mismatch")
    if expected.get("expected_no_real_data") is not True:
        errors.append("expected_result_policy_mismatch")

    flags = expected.get("expected_safety_flags")
    if not isinstance(flags, Mapping):
        errors.append("expected_safety_flags_mismatch")
    else:
        for field_name in REQUIRED_TRUE_SAFETY_FLAGS:
            if flags.get(field_name) is not True:
                errors.append("expected_safety_flags_mismatch")

    counts = expected.get("expected_count_summary")
    if not isinstance(counts, Mapping):
        errors.append("expected_count_summary_mismatch")
    else:
        for field_name in REQUIRED_ZERO_COUNT_FIELDS:
            if counts.get(field_name) != 0:
                errors.append("expected_count_summary_mismatch")
        for field_name in (
            "manifest_metadata_field_count",
            "validation_reference_count",
            "release_quality_reference_count",
        ):
            if not isinstance(counts.get(field_name), int):
                errors.append("expected_count_summary_mismatch")
    if expected.get("expected_safe_summary") != "metadata_only_manifest_writer_result":
        errors.append("expected_result_policy_mismatch")
    return errors


def _validate_path_policy(
    fixture: ManifestWriterRuntimeFixtureCase,
) -> list[str]:
    errors: list[str] = []
    request = fixture.manifest_writer_request
    expected_reasons = _expected_reason_codes(fixture)
    manifest_out = request.get("manifest_out")

    if fixture.expected_kind == "valid" and manifest_out is not None:
        errors.append("path_policy_mismatch")
    if request.get("allow_manifest_file_writing") is True:
        errors.append("path_policy_mismatch")
    if manifest_out is not None:
        if "unsafe_manifest_output_path" not in expected_reasons and (
            "overwrite_without_policy" not in expected_reasons
        ):
            errors.append("path_policy_mismatch")
        if not isinstance(manifest_out, str):
            errors.append("path_policy_mismatch")
        elif _looks_like_absolute_or_private_path(manifest_out):
            errors.append("path_policy_mismatch")
    if request.get("overwrite_policy") not in {"no_write", "reject_existing"}:
        errors.append("path_policy_mismatch")
    return errors


def _validate_content_policy(
    fixture: ManifestWriterRuntimeFixtureCase,
) -> list[str]:
    errors: list[str] = []
    expected_reasons = _expected_reason_codes(fixture)
    request = fixture.manifest_writer_request
    artifact_pointer = fixture.artifact_writer_result_pointer
    body_pointer = fixture.artifact_body_generation_result_pointer

    sentinel_reasons = {
        request.get("safe_violation_sentinel"),
        artifact_pointer.get("safe_violation_sentinel"),
        body_pointer.get("safe_violation_sentinel"),
    }
    for reason in sentinel_reasons:
        if reason and reason not in expected_reasons:
            errors.append("content_policy_mismatch")

    if request.get("include_manifest_body") is True:
        if "manifest_body_requested" not in expected_reasons:
            errors.append("content_policy_mismatch")
    for pointer in (artifact_pointer, body_pointer):
        if pointer.get("include_body_payload") is True:
            if "artifact_body_payload_leakage" not in expected_reasons:
                errors.append("content_policy_mismatch")
        if pointer.get("include_raw_rows") is True:
            if "raw_rows_leakage" not in expected_reasons:
                errors.append("content_policy_mismatch")
        if pointer.get("include_private_paths") is True:
            if not {
                "private_path_leakage",
                "absolute_path_leakage",
            }.intersection(expected_reasons):
                errors.append("content_policy_mismatch")
    return errors


def _validate_notice_policy(
    fixture: ManifestWriterRuntimeFixtureCase,
) -> list[str]:
    errors: list[str] = []
    expected_reasons = _expected_reason_codes(fixture)
    request = fixture.manifest_writer_request
    for field_name, reason in EXPECTED_MISSING_NOTICE_REASONS.items():
        if request.get(field_name) is not True and reason not in expected_reasons:
            errors.append("notice_policy_mismatch")
    return errors


def _validate_reason_code_contract(
    fixture: ManifestWriterRuntimeFixtureCase,
) -> list[str]:
    errors: list[str] = []
    metadata_reasons = _normalize_reason_codes(
        fixture.case_metadata.get("expected_reason_codes")
    )
    expected = fixture.expected_manifest_writer_runtime_result
    expected_reasons = _normalize_reason_codes(expected.get("expected_reason_codes"))
    expected_failed = _normalize_reason_codes(expected.get("expected_failed_checks"))

    if sorted(metadata_reasons) != sorted(expected_reasons):
        errors.append("expected_reason_codes_mismatch")
    if sorted(expected_failed) != sorted(expected_reasons):
        errors.append("expected_failed_checks_mismatch")
    if fixture.expected_kind == "valid":
        if expected_reasons:
            errors.append("expected_reason_codes_mismatch")
    elif fixture.expected_kind == "invalid":
        expected_reason = EXPECTED_INVALID_REASONS.get(fixture.case_label)
        if expected_reasons != [expected_reason]:
            errors.append("expected_reason_codes_mismatch")
        if expected_reason not in EXPECTED_REASON_CODES:
            errors.append("expected_reason_codes_mismatch")
    return errors


def _expected_case_result(
    fixture: ManifestWriterRuntimeFixtureCase,
) -> ManifestWriterRuntimeFixtureCaseResult:
    expected = fixture.expected_manifest_writer_runtime_result
    reason_codes = _normalize_reason_codes(expected.get("expected_reason_codes"))
    failed_checks = _normalize_reason_codes(expected.get("expected_failed_checks"))
    return ManifestWriterRuntimeFixtureCaseResult(
        validation_status=str(expected.get("expected_writer_status")),
        expected_status=str(expected.get("expected_writer_status")),
        expected_category=str(expected.get("expected_category")),
        case_label=fixture.case_label,
        case_id=fixture.case_name,
        expected_kind=fixture.expected_kind,
        reason_codes=reason_codes,
        failed_checks=failed_checks,
        checked_files_count=EXPECTED_JSON_FILES_PER_CASE,
        expected_manifest_writer_mode=str(
            expected.get("expected_manifest_writer_mode")
        ),
        expected_manifest_body_available=bool(
            expected.get("expected_manifest_body_available")
        ),
        expected_manifest_file_written=bool(
            expected.get("expected_manifest_file_written")
        ),
        expected_manifest_output_path_available=bool(
            expected.get("expected_manifest_output_path_available")
        ),
        expected_release_quality_ready=bool(
            expected.get("expected_release_quality_ready")
        ),
    )


def _input_error_result(
    case_dir: Path,
    errors: list[str],
    *,
    expected_kind: str,
) -> ManifestWriterRuntimeFixtureCaseResult:
    return ManifestWriterRuntimeFixtureCaseResult(
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


def _contract_error_result(
    fixture: ManifestWriterRuntimeFixtureCase,
    errors: list[str],
) -> ManifestWriterRuntimeFixtureCaseResult:
    return ManifestWriterRuntimeFixtureCaseResult(
        validation_status="input_error",
        expected_status="input_error",
        expected_category="input_error",
        case_label=fixture.case_label,
        case_id=fixture.case_name,
        expected_kind=fixture.expected_kind,
        reason_codes=sorted(set(errors)),
        failed_checks=sorted(set(errors)),
        checked_files_count=_count_existing_required_files(fixture.case_dir),
    )


def _expected_reason_codes(fixture: ManifestWriterRuntimeFixtureCase) -> list[str]:
    return _normalize_reason_codes(
        fixture.expected_manifest_writer_runtime_result.get("expected_reason_codes")
    )


def _normalize_reason_codes(value: Any) -> list[str]:
    if value in (None, "", "none"):
        return []
    if not isinstance(value, list):
        return [str(value)]
    return [str(item) for item in value]


def _missing_fields(payload: Mapping[str, Any], required: tuple[str, ...]) -> list[str]:
    return [f"missing_field_{field_name}" for field_name in required if field_name not in payload]


def _scan_forbidden_values(payload: Any) -> list[str]:
    errors: list[str] = []
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            key_text = str(key)
            if key_text in {
                "forbidden_output_markers",
                "forbidden_summary_fields",
                "expected_reason_codes",
                "expected_failed_checks",
            }:
                continue
            if key_text in {
                "final_text",
                "observed_after_text",
                "gold_label",
                "expected_action_payload",
                "scoring_feedback_payload",
                "real_participant_id",
            }:
                errors.append("forbidden_content_marker")
            errors.extend(_scan_forbidden_values(value))
    elif isinstance(payload, list):
        for item in payload:
            errors.extend(_scan_forbidden_values(item))
    elif isinstance(payload, str):
        lowered = payload.lower()
        for fragment in FORBIDDEN_VALUE_FRAGMENTS:
            if fragment.lower() in lowered:
                errors.append("forbidden_content_marker")
    return errors


def _looks_like_absolute_or_private_path(value: str) -> bool:
    return (
        value.startswith("/")
        or value.startswith("~")
        or "\\" in value
        or re.match(r"^[A-Za-z]:", value) is not None
        or ".." in PurePosixPath(value).parts
    )


def _count_existing_required_files(case_dir: Path) -> int:
    return sum(1 for file_name in REQUIRED_FILES if (case_dir / file_name).is_file())


def _count_json_files(root: Path) -> int:
    if not root.exists():
        return 0
    return len(list(root.glob("*/*/*.json")))


def _case_dirs(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(
        path
        for category in ("valid", "invalid")
        for path in (root / category).iterdir()
        if path.is_dir()
    )


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("fixture JSON must be an object")
    return payload


if __name__ == "__main__":
    sys.exit(main())
