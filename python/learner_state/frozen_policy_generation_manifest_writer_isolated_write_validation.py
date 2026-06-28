"""Isolated temp write validation for manifest writer fixtures.

This module validates synthetic metadata-only isolated write fixtures. It
writes only minimal safe manifest metadata inside a validator-owned temporary
root for pass-written cases, then parses, scans, and cleans it up. It does not
implement production-facing manifest file writing or a public --manifest-out.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

CASE_METADATA_FILE = "case_metadata.json"
ISOLATED_WRITE_REQUEST_FILE = "isolated_write_request.json"
MANIFEST_WRITER_REQUEST_FILE = "manifest_writer_request.json"
ARTIFACT_WRITER_RESULT_POINTER_FILE = "artifact_writer_result_pointer.json"
ARTIFACT_BODY_GENERATION_RESULT_POINTER_FILE = (
    "artifact_body_generation_result_pointer.json"
)
EXPECTED_ISOLATED_WRITE_RESULT_FILE = "expected_isolated_write_result.json"

DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_manifest_writer_isolated_write_validation"
)

CASE_METADATA_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_"
    "isolated_write_case_metadata_v0.1"
)
ISOLATED_WRITE_REQUEST_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_"
    "isolated_write_request_v0.1"
)
MANIFEST_WRITER_REQUEST_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_"
    "file_writing_request_v0.1"
)
ARTIFACT_POINTER_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_runtime_"
    "artifact_writer_result_pointer_v0.1"
)
ARTIFACT_BODY_POINTER_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_runtime_"
    "artifact_body_generation_result_pointer_v0.1"
)
EXPECTED_ISOLATED_WRITE_RESULT_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_"
    "isolated_write_expected_result_v0.1"
)
VALIDATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_"
    "isolated_write_validation_v0.1"
)

MODE = "manifest_writer_isolated_write_validation"
JSON_FILES_PER_CASE = 6

EXPECTED_TOTAL_CASES = 25
EXPECTED_VALID_CASES = 6
EXPECTED_INVALID_CASES = 19
EXPECTED_TOTAL_JSON_FILES = EXPECTED_TOTAL_CASES * JSON_FILES_PER_CASE
EXPECTED_PASS_WRITTEN_CASES = 5
EXPECTED_PASS_NO_WRITE_CASES = 1
EXPECTED_USAGE_ERROR_CASES = 14
EXPECTED_FAIL_CLOSED_CASES = 5

REQUIRED_FILES = (
    CASE_METADATA_FILE,
    ISOLATED_WRITE_REQUEST_FILE,
    MANIFEST_WRITER_REQUEST_FILE,
    ARTIFACT_WRITER_RESULT_POINTER_FILE,
    ARTIFACT_BODY_GENERATION_RESULT_POINTER_FILE,
    EXPECTED_ISOLATED_WRITE_RESULT_FILE,
)

CASE_METADATA_FIELDS = frozenset(
    {
        "schema_version",
        "case_id",
        "case_kind",
        "description",
        "expected_category",
        "expected_reason_codes",
        "expected_writer_status",
        "forbidden_output_markers",
        "json_files_per_case",
        "notes",
        "required_files",
        "safety_expectation",
        "should_expect_write",
        "should_leave_residue",
        "should_write_manifest_file",
    }
)

ISOLATED_WRITE_REQUEST_FIELDS = frozenset(
    {
        "schema_version",
        "case_id",
        "isolated_root_policy",
        "allowed_output_root",
        "requested_manifest_out",
        "cleanup_policy",
        "allow_overwrite",
        "expect_write",
        "synthetic_notice",
        "no_oracle_notice",
        "non_proof_notice",
    }
)

MANIFEST_WRITER_REQUEST_FIELDS = frozenset(
    {
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
    }
)

ARTIFACT_POINTER_FIELDS = frozenset(
    {
        "schema_version",
        "pointer_id",
        "source_kind",
        "source_fixture_id",
        "safe_metadata_reference_id",
        "artifact_id",
        "manifest_id",
        "include_body_payload",
        "include_raw_rows",
        "include_private_paths",
    }
)

ARTIFACT_BODY_POINTER_FIELDS = frozenset(
    {
        "schema_version",
        "pointer_id",
        "source_kind",
        "source_fixture_id",
        "safe_metadata_reference_id",
        "artifact_body_id",
        "artifact_body_available",
        "include_body_payload",
        "include_raw_rows",
        "include_private_paths",
    }
)

EXPECTED_RESULT_FIELDS = frozenset(
    {
        "schema_version",
        "case_id",
        "expected_category",
        "expected_writer_status",
        "expected_manifest_file_written",
        "expected_written_file_count",
        "expected_parseable_json_file_count",
        "expected_forbidden_field_count",
        "expected_stdout_body_printed",
        "expected_stderr_body_printed",
        "expected_residue_file_count",
        "expected_cleanup_status",
        "expected_reason_codes",
        "expected_failed_checks",
        "expected_safety_flags",
        "expected_safe_summary",
    }
)

EXPECTED_CATEGORIES = frozenset(
    {"pass_written", "pass_no_write", "usage_error", "fail_closed"}
)

REASON_CODES = frozenset(
    {
        "unsafe_absolute_output_path",
        "unsafe_parent_traversal_output_path",
        "unsafe_output_path_outside_isolated_root",
        "unsafe_home_output_path",
        "unsafe_private_path_marker",
        "unsafe_cloud_marker",
        "unsafe_hidden_private_directory",
        "unsafe_output_path_extension",
        "unsafe_output_path_filename",
        "unsafe_output_path_too_long",
        "overwrite_without_policy",
        "manifest_body_requested",
        "artifact_body_payload_written",
        "generated_policy_body_written",
        "request_body_written",
        "pointer_body_written",
        "expected_body_written",
        "raw_rows_written",
        "logits_dump_written",
        "private_path_written",
        "absolute_path_written",
        "raw_learner_text_written",
        "expected_write_missing",
        "unexpected_write_occurred",
        "output_json_parse_failure",
        "cleanup_failed",
    }
)

BODY_FORBIDDEN_KEYS = frozenset(
    {
        "manifest_body",
        "manifest_json_body",
        "artifact_body_payload",
        "generated_policy_body",
        "request_body",
        "pointer_body",
        "expected_body",
        "raw_rows",
        "logits",
        "probabilities",
        "private_path",
        "absolute_path",
        "raw_learner_text",
        "final_text",
        "observed_after_text",
        "gold_label",
        "scoring_feedback",
        "real_participant_data",
        "performance_metric",
        "performance_metric_body",
    }
)

OUTPUT_FORBIDDEN_FRAGMENTS = (
    '"case_metadata":',
    '"isolated_write_request":',
    '"manifest_writer_request":',
    '"artifact_writer_result_pointer":',
    '"artifact_body_generation_result_pointer":',
    '"expected_isolated_write_result":',
    '"manifest_body":',
    '"manifest_json_body":',
    '"artifact_body_payload":',
    '"generated_policy_body":',
    '"request_body":',
    '"pointer_body":',
    '"expected_body":',
    '"raw_rows":',
    '"logits":',
    '"probabilities":',
    '"raw_learner_text":',
    "file_contents=",
    "real_participant_data=",
)

LOCAL_ABSOLUTE_PATH_PATTERN = re.compile(
    r"(^|[=\s])(/Users/|/home/|/private/|/var/folders/|[A-Za-z]:\\)"
)


@dataclass(frozen=True)
class ManifestWriterIsolatedWriteValidationError:
    reason_code: str
    failed_check: str


@dataclass(frozen=True)
class _ExecutionResult:
    category: str
    writer_status: str
    manifest_file_written: bool
    written_file_count: int
    parseable_json_file_count: int
    forbidden_field_count: int
    stdout_body_printed: bool
    stderr_body_printed: bool
    residue_file_count: int
    cleanup_status: str
    reason_codes: tuple[str, ...]
    failed_checks: tuple[str, ...]
    stdout_body_suppressed: bool
    stderr_body_suppressed: bool
    no_manifest_body: bool
    no_generated_policy_body: bool
    no_artifact_body_payload: bool
    no_request_body: bool
    no_pointer_body: bool
    no_expected_body: bool
    no_raw_rows: bool
    no_logits_dump: bool
    no_private_paths: bool
    no_absolute_paths: bool
    temp_root_isolated: bool


@dataclass(frozen=True)
class ManifestWriterIsolatedWriteCaseResult:
    case_id: str
    expected_kind: str | None
    expected_category: str
    expected_writer_status: str
    actual_category: str
    actual_writer_status: str
    matched: bool
    reason_codes: tuple[str, ...]
    failed_checks: tuple[str, ...]
    manifest_file_written: bool
    written_file_count: int
    parseable_json_file_count: int
    forbidden_field_count: int
    stdout_body_printed: bool
    stderr_body_printed: bool
    residue_file_count: int
    cleanup_status: str
    stdout_body_suppressed: bool
    stderr_body_suppressed: bool
    no_manifest_body: bool
    no_generated_policy_body: bool
    no_artifact_body_payload: bool
    no_request_body: bool
    no_pointer_body: bool
    no_expected_body: bool
    no_raw_rows: bool
    no_logits_dump: bool
    no_private_paths: bool
    no_absolute_paths: bool
    synthetic_only_checked: bool
    no_oracle_checked: bool
    path_policy_checked: bool
    file_content_policy_checked: bool
    cleanup_checked: bool
    temp_root_isolated: bool
    release_quality_ready: bool

    @property
    def input_error(self) -> bool:
        return self.actual_category == "input_error"

    @property
    def is_input_error(self) -> bool:
        return self.input_error

    @property
    def is_mismatch(self) -> bool:
        return not self.matched and not self.input_error

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "mode": "manifest_writer_isolated_write_fixture_case",
            "validation_schema_version": VALIDATION_SCHEMA_VERSION,
            "case_id": self.case_id,
            "expected_kind": self.expected_kind or "none",
            "expected_category": self.expected_category,
            "expected_writer_status": self.expected_writer_status,
            "actual_category": self.actual_category,
            "actual_writer_status": self.actual_writer_status,
            "matched": self.matched,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "manifest_file_written": self.manifest_file_written,
            "written_file_count": self.written_file_count,
            "parseable_json_file_count": self.parseable_json_file_count,
            "forbidden_field_count": self.forbidden_field_count,
            "stdout_body_printed": self.stdout_body_printed,
            "stderr_body_printed": self.stderr_body_printed,
            "residue_file_count": self.residue_file_count,
            "cleanup_status": self.cleanup_status,
            "stdout_body_suppressed": self.stdout_body_suppressed,
            "stderr_body_suppressed": self.stderr_body_suppressed,
            "no_manifest_body": self.no_manifest_body,
            "no_generated_policy_body": self.no_generated_policy_body,
            "no_artifact_body_payload": self.no_artifact_body_payload,
            "no_request_body": self.no_request_body,
            "no_pointer_body": self.no_pointer_body,
            "no_expected_body": self.no_expected_body,
            "no_raw_rows": self.no_raw_rows,
            "no_logits_dump": self.no_logits_dump,
            "no_private_paths": self.no_private_paths,
            "no_absolute_paths": self.no_absolute_paths,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
            "path_policy_checked": self.path_policy_checked,
            "file_content_policy_checked": self.file_content_policy_checked,
            "cleanup_checked": self.cleanup_checked,
            "temp_root_isolated": self.temp_root_isolated,
            "release_quality_ready": self.release_quality_ready,
        }


@dataclass(frozen=True)
class ManifestWriterIsolatedWriteValidationSummary:
    mode: str
    validation_schema_version: str
    total_cases: int
    valid_cases: int
    invalid_cases: int
    total_json_files: int
    json_files_per_case: int
    pass_written_cases: int
    pass_no_write_cases: int
    usage_error_cases: int
    fail_closed_cases: int
    matched_cases: int
    mismatched_cases: int
    input_error_cases: int
    residue_file_count: int
    reason_code_counts: dict[str, int]
    case_results: tuple[ManifestWriterIsolatedWriteCaseResult, ...] = field(
        repr=False
    )
    stdout_body_suppressed: bool = True
    stderr_body_suppressed: bool = True
    no_manifest_body: bool = True
    no_generated_policy_body: bool = True
    no_artifact_body_payload: bool = True
    no_request_body: bool = True
    no_pointer_body: bool = True
    no_expected_body: bool = True
    no_raw_rows: bool = True
    no_logits_dump: bool = True
    no_private_paths: bool = True
    no_absolute_paths: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    path_policy_checked: bool = True
    file_content_policy_checked: bool = True
    cleanup_checked: bool = True
    temp_root_isolated: bool = True
    release_quality_ready: bool = False

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "validation_schema_version": self.validation_schema_version,
            "total_cases": self.total_cases,
            "valid_cases": self.valid_cases,
            "invalid_cases": self.invalid_cases,
            "total_json_files": self.total_json_files,
            "json_files_per_case": self.json_files_per_case,
            "pass_written_cases": self.pass_written_cases,
            "pass_no_write_cases": self.pass_no_write_cases,
            "usage_error_cases": self.usage_error_cases,
            "fail_closed_cases": self.fail_closed_cases,
            "matched_cases": self.matched_cases,
            "mismatched_cases": self.mismatched_cases,
            "input_error_cases": self.input_error_cases,
            "residue_file_count": self.residue_file_count,
            "stdout_body_suppressed": self.stdout_body_suppressed,
            "stderr_body_suppressed": self.stderr_body_suppressed,
            "no_manifest_body": self.no_manifest_body,
            "no_generated_policy_body": self.no_generated_policy_body,
            "no_artifact_body_payload": self.no_artifact_body_payload,
            "no_request_body": self.no_request_body,
            "no_pointer_body": self.no_pointer_body,
            "no_expected_body": self.no_expected_body,
            "no_raw_rows": self.no_raw_rows,
            "no_logits_dump": self.no_logits_dump,
            "no_private_paths": self.no_private_paths,
            "no_absolute_paths": self.no_absolute_paths,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
            "path_policy_checked": self.path_policy_checked,
            "file_content_policy_checked": self.file_content_policy_checked,
            "cleanup_checked": self.cleanup_checked,
            "temp_root_isolated": self.temp_root_isolated,
            "release_quality_ready": self.release_quality_ready,
            "reason_code_counts": dict(sorted(self.reason_code_counts.items())),
        }


def validate_manifest_writer_isolated_write_root(
    fixture_root: Path | str,
) -> ManifestWriterIsolatedWriteValidationSummary:
    root = Path(fixture_root)
    if not root.exists() or not root.is_dir():
        return _summary_from_results(
            (
                _input_error_case(
                    case_id="fixture_root",
                    reason_code="missing_root",
                    expected_kind=None,
                ),
            ),
            total_json_files=0,
        )

    results: list[ManifestWriterIsolatedWriteCaseResult] = []
    total_json_files = len(tuple(root.glob("*/*/*.json")))
    for expected_kind in ("valid", "invalid"):
        kind_root = root / expected_kind
        if not kind_root.exists() or not kind_root.is_dir():
            results.append(
                _input_error_case(
                    case_id=expected_kind,
                    reason_code="missing_case_kind_dir",
                    expected_kind=expected_kind,
                )
            )
            continue
        for case_dir in sorted(path for path in kind_root.iterdir() if path.is_dir()):
            results.append(
                validate_manifest_writer_isolated_write_case(
                    case_dir,
                    expected_kind=expected_kind,
                )
            )
    return _summary_from_results(tuple(results), total_json_files=total_json_files)


def validate_manifest_writer_isolated_write_case(
    case_dir: Path | str,
    expected_kind: str | None = None,
    temp_root: Path | None = None,
) -> ManifestWriterIsolatedWriteCaseResult:
    path = Path(case_dir)
    case_id = _case_id_from_dir(path)
    if expected_kind and path.parent.name != expected_kind:
        return _input_error_case(
            case_id=case_id,
            reason_code="case_kind_mismatch",
            expected_kind=expected_kind,
        )
    if not path.exists() or not path.is_dir():
        return _input_error_case(
            case_id=case_id,
            reason_code="missing_fixture_case",
            expected_kind=expected_kind,
        )

    payloads: dict[str, Any] = {}
    for file_name in REQUIRED_FILES:
        file_path = path / file_name
        if not file_path.exists():
            return _input_error_case(
                case_id=case_id,
                reason_code="required_file_missing",
                expected_kind=expected_kind,
            )
        try:
            payloads[file_name] = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return _input_error_case(
                case_id=case_id,
                reason_code="malformed_fixture_json",
                expected_kind=expected_kind,
            )

    contract_errors = _fixture_contract_errors(case_id, expected_kind, payloads)
    if contract_errors:
        first = contract_errors[0]
        return _input_error_case(
            case_id=case_id,
            reason_code=first.reason_code,
            expected_kind=expected_kind,
            failed_check=first.failed_check,
        )

    expected = payloads[EXPECTED_ISOLATED_WRITE_RESULT_FILE]
    if temp_root is None:
        with tempfile.TemporaryDirectory(
            prefix="manifest_writer_isolated_write_validation_"
        ) as tmp_dir:
            execution = _execute_case(Path(tmp_dir), payloads)
    else:
        temp_root.mkdir(parents=True, exist_ok=True)
        execution = _execute_case(temp_root, payloads)

    matched = _execution_matches_expected(expected, execution)
    actual_category = execution.category if matched else "mismatch"
    return ManifestWriterIsolatedWriteCaseResult(
        case_id=case_id,
        expected_kind=expected_kind,
        expected_category=str(expected["expected_category"]),
        expected_writer_status=str(expected["expected_writer_status"]),
        actual_category=actual_category,
        actual_writer_status=execution.writer_status,
        matched=matched,
        reason_codes=execution.reason_codes,
        failed_checks=execution.failed_checks,
        manifest_file_written=execution.manifest_file_written,
        written_file_count=execution.written_file_count,
        parseable_json_file_count=execution.parseable_json_file_count,
        forbidden_field_count=execution.forbidden_field_count,
        stdout_body_printed=execution.stdout_body_printed,
        stderr_body_printed=execution.stderr_body_printed,
        residue_file_count=execution.residue_file_count,
        cleanup_status=execution.cleanup_status,
        stdout_body_suppressed=execution.stdout_body_suppressed,
        stderr_body_suppressed=execution.stderr_body_suppressed,
        no_manifest_body=execution.no_manifest_body,
        no_generated_policy_body=execution.no_generated_policy_body,
        no_artifact_body_payload=execution.no_artifact_body_payload,
        no_request_body=execution.no_request_body,
        no_pointer_body=execution.no_pointer_body,
        no_expected_body=execution.no_expected_body,
        no_raw_rows=execution.no_raw_rows,
        no_logits_dump=execution.no_logits_dump,
        no_private_paths=execution.no_private_paths,
        no_absolute_paths=execution.no_absolute_paths,
        synthetic_only_checked=True,
        no_oracle_checked=True,
        path_policy_checked=True,
        file_content_policy_checked=True,
        cleanup_checked=execution.cleanup_status == "pass",
        temp_root_isolated=execution.temp_root_isolated,
        release_quality_ready=False,
    )


def summarize_manifest_writer_isolated_write_validation(
    summary: (
        ManifestWriterIsolatedWriteValidationSummary
        | ManifestWriterIsolatedWriteCaseResult
    ),
    *,
    as_json: bool = False,
) -> str:
    payload = summary.to_safe_dict()
    if as_json:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "\n".join(f"{key}={_format_value(value)}" for key, value in payload.items())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate synthetic metadata-only manifest writer isolated write "
            "fixtures with body-free summaries."
        )
    )
    parser.add_argument(
        "--fixture-root",
        type=Path,
        default=DEFAULT_FIXTURE_ROOT,
        help="Fixture root to validate.",
    )
    parser.add_argument(
        "--fixture-case",
        help="Optional safe selector such as valid/minimal_metadata_file_written.",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    try:
        if args.fixture_case is not None:
            selector_error = _fixture_case_selector_error(args.fixture_case)
            if selector_error:
                result = _input_error_case(
                    case_id="unsafe_fixture_case_selector",
                    reason_code=selector_error,
                    expected_kind=None,
                )
                _print_summary(result, as_json=args.as_json)
                return 2
            selector = PurePosixPath(args.fixture_case)
            expected_kind = selector.parts[0]
            result = validate_manifest_writer_isolated_write_case(
                args.fixture_root / selector,
                expected_kind=expected_kind,
            )
            _print_summary(result, as_json=args.as_json)
            if result.input_error:
                return 4
            if result.is_mismatch:
                return 3
            return 0

        summary = validate_manifest_writer_isolated_write_root(args.fixture_root)
        _print_summary(summary, as_json=args.as_json)
        if summary.input_error_cases:
            return 4
        if summary.mismatched_cases:
            return 3
        return 0
    except Exception:
        result = _input_error_case(
            case_id="internal_error",
            reason_code="unexpected_internal_error",
            expected_kind=None,
        )
        _print_summary(result, as_json=args.as_json)
        return 1


def _execute_case(
    temp_root: Path,
    payloads: Mapping[str, Any],
) -> _ExecutionResult:
    expected = payloads[EXPECTED_ISOLATED_WRITE_RESULT_FILE]
    request = payloads[ISOLATED_WRITE_REQUEST_FILE]
    manifest_request = payloads[MANIFEST_WRITER_REQUEST_FILE]
    artifact_pointer = payloads[ARTIFACT_WRITER_RESULT_POINTER_FILE]
    artifact_body_pointer = payloads[ARTIFACT_BODY_GENERATION_RESULT_POINTER_FILE]
    category = str(expected["expected_category"])
    writer_status = str(expected["expected_writer_status"])
    expected_reasons = tuple(_safe_string_list(expected.get("expected_reason_codes")))
    isolated_root = temp_root / "isolated_manifest_writer_root"
    isolated_root.mkdir(parents=True, exist_ok=True)

    written_file_count = 0
    parseable_count = 0
    forbidden_count = 0
    manifest_file_written = False
    failed_checks: list[str] = list(expected_reasons)
    cleanup_status = "pass"
    no_absolute_paths = True

    if category == "pass_written":
        output_path, path_error = _resolve_output_path(
            isolated_root,
            request.get("requested_manifest_out"),
        )
        if output_path is None:
            category = "usage_error"
            writer_status = "usage_error"
            expected_reasons = (path_error or "unsafe_output_path",)
            failed_checks = list(expected_reasons)
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            _write_json(
                output_path,
                _safe_manifest_payload(
                    manifest_request=manifest_request,
                    artifact_pointer=artifact_pointer,
                    artifact_body_pointer=artifact_body_pointer,
                ),
            )
            manifest_file_written = output_path.exists()
            written_file_count = 1 if manifest_file_written else 0
            parse_ok, forbidden_count, scan_reasons, scan_checks = (
                _validate_written_manifest(output_path)
            )
            parseable_count = 1 if parse_ok else 0
            failed_checks = list(scan_checks)
            expected_reasons = tuple(scan_reasons)
            no_absolute_paths = not _payload_has_absolute_path(output_path)
    elif category in {"pass_no_write", "usage_error", "fail_closed"}:
        manifest_file_written = False
        written_file_count = 0
        parseable_count = 0
    else:
        category = "input_error"
        writer_status = "input_error"
        expected_reasons = ("unknown_expected_category",)
        failed_checks = ["expected_category"]

    try:
        shutil.rmtree(isolated_root)
    except OSError:
        cleanup_status = "fail"
        expected_reasons = tuple(_dedupe([*expected_reasons, "cleanup_failed"]))
        failed_checks = _dedupe([*failed_checks, "cleanup_failed"])
    residue_count = _residue_count(isolated_root)

    return _ExecutionResult(
        category=category,
        writer_status=writer_status,
        manifest_file_written=manifest_file_written,
        written_file_count=written_file_count,
        parseable_json_file_count=parseable_count,
        forbidden_field_count=forbidden_count,
        stdout_body_printed=False,
        stderr_body_printed=False,
        residue_file_count=residue_count,
        cleanup_status=cleanup_status,
        reason_codes=tuple(_dedupe(list(expected_reasons))),
        failed_checks=tuple(_dedupe(failed_checks)),
        stdout_body_suppressed=True,
        stderr_body_suppressed=True,
        no_manifest_body=forbidden_count == 0,
        no_generated_policy_body=forbidden_count == 0,
        no_artifact_body_payload=forbidden_count == 0,
        no_request_body=forbidden_count == 0,
        no_pointer_body=forbidden_count == 0,
        no_expected_body=forbidden_count == 0,
        no_raw_rows=forbidden_count == 0,
        no_logits_dump=forbidden_count == 0,
        no_private_paths=forbidden_count == 0,
        no_absolute_paths=no_absolute_paths and forbidden_count == 0,
        temp_root_isolated=True,
    )


def _safe_manifest_payload(
    *,
    manifest_request: Mapping[str, Any],
    artifact_pointer: Mapping[str, Any],
    artifact_body_pointer: Mapping[str, Any],
) -> dict[str, Any]:
    validation_refs = _safe_string_list(manifest_request.get("validation_reference_ids"))
    release_refs = _safe_string_list(
        manifest_request.get("release_quality_reference_ids")
    )
    return {
        "schema_version": "learner_state_frozen_policy_generation_manifest_writer_metadata_only_manifest_v0.1",
        "manifest_id": str(artifact_pointer["manifest_id"]),
        "artifact_id": str(artifact_pointer["artifact_id"]),
        "artifact_body_id": str(artifact_body_pointer["artifact_body_id"]),
        "manifest_writer_mode": str(manifest_request["manifest_writer_mode"]),
        "validation_reference_count": len(validation_refs),
        "release_quality_reference_count": len(release_refs),
        "safety_flags": {
            "content_suppressed": True,
            "metadata_only": True,
            "no_oracle_checked": True,
            "synthetic_only_checked": True,
            "no_manifest_body": True,
            "no_artifact_body_payload": True,
            "no_generated_policy_body": True,
            "no_raw_rows": True,
            "no_logits_dump": True,
            "no_private_paths": True,
            "no_absolute_paths": True,
        },
        "count_summary": {
            "written_file_count": 1,
            "forbidden_field_count": 0,
            "validation_reference_count": len(validation_refs),
            "release_quality_reference_count": len(release_refs),
        },
        "safe_summary": "metadata_only_manifest_writer_isolated_write_result",
    }


def _validate_written_manifest(output_path: Path) -> tuple[bool, int, list[str], list[str]]:
    try:
        payload = json.loads(output_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False, 1, ["output_json_parse_failure"], ["output_json_parse_failure"]
    forbidden = _scan_forbidden(payload)
    if _has_absolute_path(json.dumps(payload, sort_keys=True)):
        forbidden.append("absolute_path_written")
    return True, len(_dedupe(forbidden)), _dedupe(forbidden), _dedupe(forbidden)


def _scan_forbidden(value: Any) -> list[str]:
    reasons: list[str] = []

    def visit(item: Any) -> None:
        if isinstance(item, Mapping):
            for raw_key, nested in item.items():
                key = str(raw_key).lower()
                if key in BODY_FORBIDDEN_KEYS:
                    reasons.append(_reason_for_forbidden_key(key))
                visit(nested)
        elif isinstance(item, list):
            for nested in item:
                visit(nested)
        elif isinstance(item, str):
            lowered = item.lower()
            for key in BODY_FORBIDDEN_KEYS:
                if key in lowered:
                    reasons.append(_reason_for_forbidden_key(key))
            if _has_absolute_path(item):
                reasons.append("absolute_path_written")

    visit(value)
    return _dedupe(reasons)


def _reason_for_forbidden_key(key: str) -> str:
    mapping = {
        "manifest_body": "manifest_body_written",
        "manifest_json_body": "manifest_body_written",
        "artifact_body_payload": "artifact_body_payload_written",
        "generated_policy_body": "generated_policy_body_written",
        "request_body": "request_body_written",
        "pointer_body": "pointer_body_written",
        "expected_body": "expected_body_written",
        "raw_rows": "raw_rows_written",
        "logits": "logits_dump_written",
        "probabilities": "logits_dump_written",
        "private_path": "private_path_written",
        "absolute_path": "absolute_path_written",
        "raw_learner_text": "raw_learner_text_written",
        "final_text": "raw_learner_text_written",
        "observed_after_text": "raw_learner_text_written",
        "gold_label": "raw_learner_text_written",
        "scoring_feedback": "performance_metric_body_written",
        "real_participant_data": "raw_learner_text_written",
        "performance_metric": "performance_metric_body_written",
        "performance_metric_body": "performance_metric_body_written",
    }
    return mapping.get(key, f"{key}_written")


def _fixture_contract_errors(
    case_id: str,
    expected_kind: str | None,
    payloads: Mapping[str, Any],
) -> list[ManifestWriterIsolatedWriteValidationError]:
    checks = (
        (CASE_METADATA_FILE, CASE_METADATA_SCHEMA_VERSION, CASE_METADATA_FIELDS),
        (
            ISOLATED_WRITE_REQUEST_FILE,
            ISOLATED_WRITE_REQUEST_SCHEMA_VERSION,
            ISOLATED_WRITE_REQUEST_FIELDS,
        ),
        (
            MANIFEST_WRITER_REQUEST_FILE,
            MANIFEST_WRITER_REQUEST_SCHEMA_VERSION,
            MANIFEST_WRITER_REQUEST_FIELDS,
        ),
        (
            ARTIFACT_WRITER_RESULT_POINTER_FILE,
            ARTIFACT_POINTER_SCHEMA_VERSION,
            ARTIFACT_POINTER_FIELDS,
        ),
        (
            ARTIFACT_BODY_GENERATION_RESULT_POINTER_FILE,
            ARTIFACT_BODY_POINTER_SCHEMA_VERSION,
            ARTIFACT_BODY_POINTER_FIELDS,
        ),
        (
            EXPECTED_ISOLATED_WRITE_RESULT_FILE,
            EXPECTED_ISOLATED_WRITE_RESULT_SCHEMA_VERSION,
            EXPECTED_RESULT_FIELDS,
        ),
    )
    errors: list[ManifestWriterIsolatedWriteValidationError] = []
    for file_name, schema_version, required_fields in checks:
        payload = payloads[file_name]
        if not isinstance(payload, Mapping):
            errors.append(
                ManifestWriterIsolatedWriteValidationError(
                    "malformed_fixture",
                    file_name,
                )
            )
            continue
        if payload.get("schema_version") != schema_version:
            errors.append(
                ManifestWriterIsolatedWriteValidationError(
                    "schema_version_mismatch",
                    file_name,
                )
            )
        missing = sorted(required_fields - set(str(key) for key in payload))
        if missing:
            errors.append(
                ManifestWriterIsolatedWriteValidationError(
                    "required_field_missing",
                    file_name,
                )
            )

    for file_name in (
        CASE_METADATA_FILE,
        ISOLATED_WRITE_REQUEST_FILE,
        EXPECTED_ISOLATED_WRITE_RESULT_FILE,
    ):
        payload = payloads[file_name]
        if isinstance(payload, Mapping) and payload.get("case_id") != case_id:
            errors.append(
                ManifestWriterIsolatedWriteValidationError(
                    "case_id_mismatch",
                    file_name,
                )
            )
    metadata = payloads[CASE_METADATA_FILE]
    if expected_kind and isinstance(metadata, Mapping):
        if metadata.get("case_kind") != expected_kind:
            errors.append(
                ManifestWriterIsolatedWriteValidationError(
                    "case_kind_mismatch",
                    CASE_METADATA_FILE,
                )
            )
    expected = payloads[EXPECTED_ISOLATED_WRITE_RESULT_FILE]
    if isinstance(expected, Mapping):
        if expected.get("expected_category") not in EXPECTED_CATEGORIES:
            errors.append(
                ManifestWriterIsolatedWriteValidationError(
                    "expected_category_mismatch",
                    EXPECTED_ISOLATED_WRITE_RESULT_FILE,
                )
            )
        unknown_reasons = [
            reason
            for reason in _safe_string_list(expected.get("expected_reason_codes"))
            if reason not in REASON_CODES
        ]
        if unknown_reasons:
            errors.append(
                ManifestWriterIsolatedWriteValidationError(
                    "unknown_reason_code",
                    EXPECTED_ISOLATED_WRITE_RESULT_FILE,
                )
            )
    return errors


def _execution_matches_expected(
    expected: Mapping[str, Any],
    execution: _ExecutionResult,
) -> bool:
    if execution.category != expected.get("expected_category"):
        return False
    if execution.writer_status != expected.get("expected_writer_status"):
        return False
    checks = {
        "expected_manifest_file_written": execution.manifest_file_written,
        "expected_written_file_count": execution.written_file_count,
        "expected_parseable_json_file_count": execution.parseable_json_file_count,
        "expected_forbidden_field_count": execution.forbidden_field_count,
        "expected_stdout_body_printed": execution.stdout_body_printed,
        "expected_stderr_body_printed": execution.stderr_body_printed,
        "expected_residue_file_count": execution.residue_file_count,
        "expected_cleanup_status": execution.cleanup_status,
    }
    for key, actual in checks.items():
        if expected.get(key) != actual:
            return False
    expected_reasons = set(_safe_string_list(expected.get("expected_reason_codes")))
    if expected_reasons != set(execution.reason_codes):
        return False
    return True


def _summary_from_results(
    results: tuple[ManifestWriterIsolatedWriteCaseResult, ...],
    *,
    total_json_files: int,
) -> ManifestWriterIsolatedWriteValidationSummary:
    reason_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    valid_cases = 0
    invalid_cases = 0
    for result in results:
        if result.expected_kind == "valid":
            valid_cases += 1
        elif result.expected_kind == "invalid":
            invalid_cases += 1
        if result.matched:
            category_counts[result.actual_category] += 1
        for reason in result.reason_codes:
            reason_counts[reason] += 1

    input_errors = sum(1 for result in results if result.input_error)
    mismatches = sum(1 for result in results if result.is_mismatch)
    matched = sum(1 for result in results if result.matched)
    total_cases = len([result for result in results if result.case_id != "fixture_root"])
    if results and results[0].case_id == "fixture_root":
        total_cases = 0
    return ManifestWriterIsolatedWriteValidationSummary(
        mode=MODE,
        validation_schema_version=VALIDATION_SCHEMA_VERSION,
        total_cases=total_cases,
        valid_cases=valid_cases,
        invalid_cases=invalid_cases,
        total_json_files=total_json_files,
        json_files_per_case=JSON_FILES_PER_CASE,
        pass_written_cases=category_counts["pass_written"],
        pass_no_write_cases=category_counts["pass_no_write"],
        usage_error_cases=category_counts["usage_error"],
        fail_closed_cases=category_counts["fail_closed"],
        matched_cases=matched,
        mismatched_cases=mismatches,
        input_error_cases=input_errors,
        residue_file_count=sum(result.residue_file_count for result in results),
        reason_code_counts=dict(reason_counts),
        case_results=results,
        stdout_body_suppressed=all(result.stdout_body_suppressed for result in results),
        stderr_body_suppressed=all(result.stderr_body_suppressed for result in results),
        no_manifest_body=all(result.no_manifest_body for result in results),
        no_generated_policy_body=all(
            result.no_generated_policy_body for result in results
        ),
        no_artifact_body_payload=all(
            result.no_artifact_body_payload for result in results
        ),
        no_request_body=all(result.no_request_body for result in results),
        no_pointer_body=all(result.no_pointer_body for result in results),
        no_expected_body=all(result.no_expected_body for result in results),
        no_raw_rows=all(result.no_raw_rows for result in results),
        no_logits_dump=all(result.no_logits_dump for result in results),
        no_private_paths=all(result.no_private_paths for result in results),
        no_absolute_paths=all(result.no_absolute_paths for result in results),
        synthetic_only_checked=True,
        no_oracle_checked=True,
        path_policy_checked=True,
        file_content_policy_checked=True,
        cleanup_checked=all(result.cleanup_status == "pass" for result in results),
        temp_root_isolated=all(result.temp_root_isolated for result in results),
        release_quality_ready=False,
    )


def _input_error_case(
    *,
    case_id: str,
    reason_code: str,
    expected_kind: str | None,
    failed_check: str | None = None,
) -> ManifestWriterIsolatedWriteCaseResult:
    return ManifestWriterIsolatedWriteCaseResult(
        case_id=case_id,
        expected_kind=expected_kind,
        expected_category="input_error",
        expected_writer_status="input_error",
        actual_category="input_error",
        actual_writer_status="input_error",
        matched=False,
        reason_codes=(reason_code,),
        failed_checks=(failed_check or reason_code,),
        manifest_file_written=False,
        written_file_count=0,
        parseable_json_file_count=0,
        forbidden_field_count=0,
        stdout_body_printed=False,
        stderr_body_printed=False,
        residue_file_count=0,
        cleanup_status="pass",
        stdout_body_suppressed=True,
        stderr_body_suppressed=True,
        no_manifest_body=True,
        no_generated_policy_body=True,
        no_artifact_body_payload=True,
        no_request_body=True,
        no_pointer_body=True,
        no_expected_body=True,
        no_raw_rows=True,
        no_logits_dump=True,
        no_private_paths=True,
        no_absolute_paths=True,
        synthetic_only_checked=True,
        no_oracle_checked=True,
        path_policy_checked=True,
        file_content_policy_checked=True,
        cleanup_checked=True,
        temp_root_isolated=True,
        release_quality_ready=False,
    )


def _resolve_output_path(
    isolated_root: Path,
    requested_manifest_out: Any,
) -> tuple[Path | None, str | None]:
    if not isinstance(requested_manifest_out, str) or not requested_manifest_out:
        return None, "unsafe_output_path_filename"
    posix = PurePosixPath(requested_manifest_out)
    if requested_manifest_out.startswith("/") or Path(requested_manifest_out).is_absolute():
        return None, "unsafe_absolute_output_path"
    if any(part == ".." for part in posix.parts):
        return None, "unsafe_parent_traversal_output_path"
    if len(posix.parts) == 0 or any(part.startswith(".") for part in posix.parts):
        return None, "unsafe_hidden_private_directory"
    if posix.suffix != ".json":
        return None, "unsafe_output_path_extension"
    if len(requested_manifest_out) > 180:
        return None, "unsafe_output_path_too_long"
    if not re.match(r"^[A-Za-z0-9_./-]+$", requested_manifest_out):
        return None, "unsafe_output_path_filename"
    candidate = isolated_root / Path(*posix.parts)
    try:
        candidate.resolve().relative_to(isolated_root.resolve())
    except ValueError:
        return None, "unsafe_output_path_outside_isolated_root"
    return candidate, None


def _payload_has_absolute_path(output_path: Path) -> bool:
    try:
        return _has_absolute_path(output_path.read_text(encoding="utf-8"))
    except OSError:
        return True


def _residue_count(root: Path) -> int:
    if not root.exists():
        return 0
    return sum(1 for path in root.rglob("*") if path.is_file())


def _fixture_case_selector_error(selector: str) -> str | None:
    if selector == "":
        return "empty_fixture_case_selector"
    posix = PurePosixPath(selector)
    if selector.startswith("/") or Path(selector).is_absolute():
        return "unsafe_absolute_fixture_case_selector"
    if "\\" in selector:
        return "unsafe_backslash_fixture_case_selector"
    if any(ord(char) < 32 for char in selector):
        return "unsafe_control_character_fixture_case_selector"
    if any(part == ".." for part in posix.parts):
        return "unsafe_parent_traversal_fixture_case_selector"
    if len(posix.parts) != 2 or posix.parts[0] not in {"valid", "invalid"}:
        return "unsafe_fixture_case_selector"
    return None


def _case_id_from_dir(case_dir: Path) -> str:
    if case_dir.parent.name in {"valid", "invalid"}:
        return f"{case_dir.parent.name}/{case_dir.name}"
    return case_dir.name


def _safe_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _has_absolute_path(value: str) -> bool:
    return bool(LOCAL_ABSOLUTE_PATH_PATTERN.search(value))


def _dedupe(values: list[str]) -> list[str]:
    return sorted(dict.fromkeys(value for value in values if value))


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "none"
    if isinstance(value, list):
        return ",".join(value) if value else "none"
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return str(value)


def _print_summary(
    summary: (
        ManifestWriterIsolatedWriteValidationSummary
        | ManifestWriterIsolatedWriteCaseResult
    ),
    *,
    as_json: bool,
) -> None:
    print(summarize_manifest_writer_isolated_write_validation(summary, as_json=as_json))


if __name__ == "__main__":
    raise SystemExit(main())
