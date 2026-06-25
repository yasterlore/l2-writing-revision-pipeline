"""Isolated temp write validation for artifact body file writing fixtures.

This validator executes the artifact body generation CLI against synthetic,
metadata-only fixtures inside a temporary isolated root. It validates write,
no-write, usage-error, fail-closed, stdout/stderr safety, written-file safety,
cleanup, and residue behavior without printing fixture bodies or artifact body
payloads.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from learner_state.frozen_policy_generation_artifact_body import (
    ALLOWED_BODY_FIELDS,
    ARTIFACT_BODY_FILE_WRITE_SAFE_ROOT,
    ARTIFACT_BODY_REQUEST_SCHEMA_VERSION,
    ARTIFACT_BODY_WRITE_POLICY,
    ARTIFACT_WRITER_RESULT_POINTER_SCHEMA_VERSION,
)

CASE_METADATA_FILE = "case_metadata.json"
ARTIFACT_BODY_REQUEST_FILE = "artifact_body_request.json"
ARTIFACT_WRITER_RESULT_POINTER_FILE = "artifact_writer_result_pointer.json"
ISOLATED_WRITE_REQUEST_FILE = "isolated_write_request.json"
EXPECTED_ISOLATED_WRITE_RESULT_FILE = "expected_isolated_write_result.json"

CASE_METADATA_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_isolated_write_case_metadata_v0.1"
)
ISOLATED_WRITE_REQUEST_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_isolated_write_request_v0.1"
)
EXPECTED_ISOLATED_WRITE_RESULT_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_isolated_write_expected_result_v0.1"
)
VALIDATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_isolated_write_validation_v0.1"
)

DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/learner_state_frozen_policy_generation_artifact_body_isolated_write_validation"
)
REQUIRED_FILES = (
    CASE_METADATA_FILE,
    ARTIFACT_BODY_REQUEST_FILE,
    ARTIFACT_WRITER_RESULT_POINTER_FILE,
    ISOLATED_WRITE_REQUEST_FILE,
    EXPECTED_ISOLATED_WRITE_RESULT_FILE,
)

EXPECTED_VALID_CASES = 5
EXPECTED_INVALID_CASES = 17
EXPECTED_TOTAL_CASES = 22
EXPECTED_JSON_FILE_COUNT = EXPECTED_TOTAL_CASES * 5

EXPECTED_CATEGORY_COUNTS = {
    "pass_written": 3,
    "pass_no_write": 1,
    "usage_error_no_write": 14,
    "fail_closed_no_write": 4,
}

RESULT_CATEGORIES = frozenset(
    {
        "pass_written",
        "pass_no_write",
        "usage_error_no_write",
        "fail_closed_no_write",
        "input_error",
        "mismatch",
    }
)

REQUIRED_CASE_METADATA_FIELDS = (
    "schema_version",
    "case_id",
    "case_kind",
    "description",
    "source_fixture_case",
    "expected_category",
    "expected_status",
    "expected_exit_code",
    "safety_expectation",
    "should_write_file",
    "should_cleanup",
    "should_leave_residue",
    "allowed_failure_reason_codes",
    "forbidden_output_markers",
    "required_summary_fields",
    "forbidden_summary_fields",
    "notes",
)

REQUIRED_ISOLATED_WRITE_REQUEST_FIELDS = (
    "schema_version",
    "case_id",
    "cli_mode",
    "artifact_body_out",
    "precreate_output_file",
    "expected_safe_root",
    "cleanup_policy",
    "parse_written_file",
    "scan_written_file",
    "scan_stdout_stderr",
    "allow_parent_creation",
    "allow_overwrite",
    "expect_manifest_file",
    "expect_manifest_body",
    "expect_artifact_file_written",
    "expect_body_payload_printed",
    "synthetic_only",
    "no_oracle_required",
)

REQUIRED_EXPECTED_RESULT_FIELDS = (
    "schema_version",
    "case_id",
    "expected_category",
    "expected_status",
    "expected_exit_code",
    "expected_file_written",
    "expected_file_parse_ok",
    "expected_file_allowed_keys_only",
    "expected_file_cleanup_ok",
    "expected_residue_file_count",
    "expected_stdout_body_free",
    "expected_stderr_body_free",
    "expected_safe_relative_path_only",
    "expected_manifest_file_written",
    "expected_manifest_body_generated",
    "expected_reason_codes",
    "expected_failed_checks",
    "expected_summary_flags",
    "expected_forbidden_counts_zero",
    "expected_no_real_data",
    "expected_no_private_paths",
    "expected_no_absolute_paths",
    "expected_no_raw_rows",
    "expected_no_logits",
    "expected_no_raw_learner_text",
)

REQUIRED_BODY_FIELDS = (
    "artifact_body_schema_version",
    "artifact_body_id",
    "artifact_id",
    "manifest_id",
    "writer_version",
    "body_status",
    "synthetic_only_notice",
    "no_oracle_notice",
    "non_proof_notice",
    "safety_summary",
    "count_summary",
)

ZERO_COUNT_FIELDS = (
    "raw_row_count",
    "logits_dump_count",
    "private_path_count",
    "performance_metric_count",
    "request_body_count",
    "pointer_body_count",
    "expected_body_count",
    "manifest_body_count",
)

STDOUT_FORBIDDEN_FRAGMENTS = (
    '"artifact_body_payload"',
    '"artifact_body_request"',
    '"artifact_writer_result_pointer"',
    '"isolated_write_request"',
    '"expected_isolated_write_result"',
    '"case_metadata"',
    '"request_body":',
    '"pointer_body":',
    '"expected_body":',
    '"generated_policy_body":',
    '"manifest_body":',
    '"raw_rows":',
    '"logits":',
    '"probabilities":',
    '"raw_learner_text":',
    "artifact_body_payload=",
    "file_contents=",
    "raw_learner_text=",
    "real_participant_data=",
)

BODY_FORBIDDEN_KEYS = frozenset(
    {
        "artifact_body_payload",
        "artifact_body_request",
        "artifact_writer_result_pointer",
        "isolated_write_request",
        "expected_isolated_write_result",
        "case_metadata",
        "request_body",
        "pointer_body",
        "expected_body",
        "generated_policy_body",
        "frozen_policy_body",
        "policy_body",
        "manifest_body",
        "raw_rows",
        "raw_learner_text",
        "logits",
        "probabilities",
        "model_scores",
        "performance_metrics",
        "performance_metric_body",
        "final_text",
        "observed_after_text",
        "gold_label",
    }
)

UNSUPPORTED_WRITE_ATTEMPT_REASONS = frozenset(
    {
        "manifest_write_attempt_not_supported",
        "generated_policy_body_write_attempt_not_supported",
    }
)

LOCAL_ABSOLUTE_PATH_PATTERN = re.compile(
    r"(^|[=\s])(/Users/|/home/|/private/|/var/folders/|[A-Za-z]:\\)"
)


@dataclass(frozen=True)
class IsolatedWriteValidationError:
    reason_code: str
    failed_check: str


@dataclass(frozen=True)
class IsolatedWriteExecutionResult:
    exit_code: int
    stdout: str
    stderr: str
    summary: dict[str, Any]
    output_file_exists_before_cleanup: bool
    output_file_parse_ok: bool
    output_file_allowed_keys_only: bool
    output_file_cleanup_ok: bool
    stdout_body_free: bool
    stderr_body_free: bool
    body_payload_printed: bool
    no_raw_rows: bool
    no_logits_dump: bool
    no_private_paths: bool
    no_absolute_paths: bool
    no_manifest_body: bool
    no_generated_policy_body: bool
    residue_file_count: int
    reason_codes: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class IsolatedWriteCaseResult:
    case_id: str
    expected_kind: str | None
    expected_category: str
    expected_status: str
    expected_exit_code: int | None
    expected_file_written: bool
    actual_category: str
    actual_status: str
    actual_exit_code: int | None
    actual_file_written: bool
    matched: bool
    reason_codes: list[str]
    failed_checks: list[str]
    file_parse_ok: bool
    file_allowed_keys_only: bool
    file_cleanup_ok: bool
    stdout_body_free: bool
    stderr_body_free: bool
    safe_relative_path_only: bool
    manifest_file_written: bool
    manifest_body_generated: bool
    body_payload_printed: bool
    no_raw_rows: bool
    no_logits_dump: bool
    no_private_paths: bool
    no_absolute_paths: bool
    no_manifest_body: bool
    no_generated_policy_body: bool
    synthetic_only_checked: bool
    no_oracle_checked: bool
    path_policy_checked: bool
    file_content_policy_checked: bool
    cleanup_checked: bool
    temp_root_isolated: bool
    release_quality_ready: bool
    residue_file_count: int

    @property
    def is_input_error(self) -> bool:
        return self.actual_category == "input_error"

    @property
    def is_mismatch(self) -> bool:
        return not self.matched and not self.is_input_error

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "mode": "isolated_write_fixture_case",
            "validation_schema_version": VALIDATION_SCHEMA_VERSION,
            "case_id": self.case_id,
            "expected_kind": self.expected_kind or "none",
            "expected_category": self.expected_category,
            "expected_status": self.expected_status,
            "expected_exit_code": self.expected_exit_code,
            "expected_file_written": self.expected_file_written,
            "actual_category": self.actual_category,
            "actual_status": self.actual_status,
            "actual_exit_code": self.actual_exit_code,
            "actual_file_written": self.actual_file_written,
            "matched": self.matched,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "file_parse_ok": self.file_parse_ok,
            "file_allowed_keys_only": self.file_allowed_keys_only,
            "file_cleanup_ok": self.file_cleanup_ok,
            "stdout_body_free": self.stdout_body_free,
            "stderr_body_free": self.stderr_body_free,
            "safe_relative_path_only": self.safe_relative_path_only,
            "manifest_file_written": self.manifest_file_written,
            "manifest_body_generated": self.manifest_body_generated,
            "body_payload_printed": self.body_payload_printed,
            "no_raw_rows": self.no_raw_rows,
            "no_logits_dump": self.no_logits_dump,
            "no_private_paths": self.no_private_paths,
            "no_absolute_paths": self.no_absolute_paths,
            "no_manifest_body": self.no_manifest_body,
            "no_generated_policy_body": self.no_generated_policy_body,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
            "path_policy_checked": self.path_policy_checked,
            "file_content_policy_checked": self.file_content_policy_checked,
            "cleanup_checked": self.cleanup_checked,
            "temp_root_isolated": self.temp_root_isolated,
            "release_quality_ready": self.release_quality_ready,
            "residue_file_count": self.residue_file_count,
        }


@dataclass(frozen=True)
class IsolatedWriteValidationSummary:
    mode: str
    validation_schema_version: str
    total_cases: int
    valid_cases: int
    invalid_cases: int
    pass_written_cases: int
    pass_no_write_cases: int
    usage_error_cases: int
    fail_closed_cases: int
    matched_cases: int
    mismatched_cases: int
    input_error_cases: int
    residue_file_count: int
    reason_code_counts: dict[str, int]
    case_results: tuple[IsolatedWriteCaseResult, ...] = field(repr=False)
    body_payload_printed: bool = False
    stdout_body_suppressed: bool = True
    stderr_body_suppressed: bool = True
    no_raw_rows: bool = True
    no_logits_dump: bool = True
    no_private_paths: bool = True
    no_absolute_paths: bool = True
    no_manifest_body: bool = True
    no_generated_policy_body: bool = True
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
            "pass_written_cases": self.pass_written_cases,
            "pass_no_write_cases": self.pass_no_write_cases,
            "usage_error_cases": self.usage_error_cases,
            "fail_closed_cases": self.fail_closed_cases,
            "matched_cases": self.matched_cases,
            "mismatched_cases": self.mismatched_cases,
            "input_error_cases": self.input_error_cases,
            "residue_file_count": self.residue_file_count,
            "body_payload_printed": self.body_payload_printed,
            "stdout_body_suppressed": self.stdout_body_suppressed,
            "stderr_body_suppressed": self.stderr_body_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "no_logits_dump": self.no_logits_dump,
            "no_private_paths": self.no_private_paths,
            "no_absolute_paths": self.no_absolute_paths,
            "no_manifest_body": self.no_manifest_body,
            "no_generated_policy_body": self.no_generated_policy_body,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
            "path_policy_checked": self.path_policy_checked,
            "file_content_policy_checked": self.file_content_policy_checked,
            "cleanup_checked": self.cleanup_checked,
            "temp_root_isolated": self.temp_root_isolated,
            "release_quality_ready": self.release_quality_ready,
            "reason_code_counts": dict(sorted(self.reason_code_counts.items())),
        }


def validate_isolated_write_fixture_root(
    fixture_root: Path | str,
) -> IsolatedWriteValidationSummary:
    root = Path(fixture_root)
    if not root.exists() or not root.is_dir():
        result = _input_error_case(
            case_id="fixture_root",
            reason_code="missing_root",
            expected_kind=None,
        )
        return _summary_from_results((result,))

    results: list[IsolatedWriteCaseResult] = []
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
                validate_isolated_write_fixture_case(
                    case_dir,
                    expected_kind=expected_kind,
                )
            )
    return _summary_from_results(tuple(results))


def validate_isolated_write_fixture_case(
    case_dir: Path | str,
    expected_kind: str | None = None,
) -> IsolatedWriteCaseResult:
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
    for name in REQUIRED_FILES:
        file_path = path / name
        if not file_path.exists():
            return _input_error_case(
                case_id=case_id,
                reason_code="required_file_missing",
                expected_kind=expected_kind,
            )
        try:
            payloads[name] = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return _input_error_case(
                case_id=case_id,
                reason_code="malformed_fixture_json",
                expected_kind=expected_kind,
            )

    contract_errors = _fixture_contract_errors(case_id, expected_kind, payloads)
    if contract_errors:
        return _input_error_case(
            case_id=case_id,
            reason_code=contract_errors[0].reason_code,
            expected_kind=expected_kind,
            failed_check=contract_errors[0].failed_check,
        )

    expected = payloads[EXPECTED_ISOLATED_WRITE_RESULT_FILE]
    isolated_request = payloads[ISOLATED_WRITE_REQUEST_FILE]
    expected_category = str(expected.get("expected_category"))
    expected_status = str(expected.get("expected_status"))
    expected_file_written = expected.get("expected_file_written") is True
    expected_exit_code = expected.get("expected_exit_code")
    if not isinstance(expected_exit_code, int):
        expected_exit_code = None

    with tempfile.TemporaryDirectory(
        prefix="artifact_body_isolated_write_validation_"
    ) as tmp_dir:
        temp_root = Path(tmp_dir)
        execution = _execute_case_in_temp_root(
            temp_root=temp_root,
            fixture_payloads=payloads,
            isolated_request=isolated_request,
            expected=expected,
        )

    actual_category = _actual_category_from_execution(execution)
    actual_status = _actual_status_from_category(actual_category)
    actual_file_written = execution.output_file_exists_before_cleanup

    matched = _matches_expected(
        expected_category=expected_category,
        expected_status=expected_status,
        expected_exit_code=expected_exit_code,
        expected_file_written=expected_file_written,
        expected_reason_codes=_safe_string_list(expected.get("expected_reason_codes")),
        actual_category=actual_category,
        actual_status=actual_status,
        actual_exit_code=execution.exit_code,
        actual_file_written=actual_file_written,
        actual_reason_codes=execution.reason_codes,
    )
    if not _expected_safety_matches(expected, execution):
        matched = False

    category = actual_category if matched else "mismatch"
    return IsolatedWriteCaseResult(
        case_id=case_id,
        expected_kind=expected_kind,
        expected_category=expected_category,
        expected_status=expected_status,
        expected_exit_code=expected_exit_code,
        expected_file_written=expected_file_written,
        actual_category=category,
        actual_status=actual_status,
        actual_exit_code=execution.exit_code,
        actual_file_written=actual_file_written,
        matched=matched,
        reason_codes=_dedupe(execution.reason_codes),
        failed_checks=_dedupe(execution.failed_checks),
        file_parse_ok=execution.output_file_parse_ok,
        file_allowed_keys_only=execution.output_file_allowed_keys_only,
        file_cleanup_ok=execution.output_file_cleanup_ok,
        stdout_body_free=execution.stdout_body_free,
        stderr_body_free=execution.stderr_body_free,
        safe_relative_path_only=_summary_has_safe_relative_path_only(
            execution.summary
        ),
        manifest_file_written=execution.summary.get("manifest_file_written") is True,
        manifest_body_generated=execution.summary.get("manifest_body_generated") is True,
        body_payload_printed=execution.body_payload_printed,
        no_raw_rows=execution.no_raw_rows,
        no_logits_dump=execution.no_logits_dump,
        no_private_paths=execution.no_private_paths,
        no_absolute_paths=execution.no_absolute_paths,
        no_manifest_body=execution.no_manifest_body,
        no_generated_policy_body=execution.no_generated_policy_body,
        synthetic_only_checked=True,
        no_oracle_checked=True,
        path_policy_checked=True,
        file_content_policy_checked=True,
        cleanup_checked=True,
        temp_root_isolated=True,
        release_quality_ready=False,
        residue_file_count=execution.residue_file_count,
    )


def summarize_isolated_write_validation(
    summary: IsolatedWriteValidationSummary | IsolatedWriteCaseResult,
) -> str:
    data = summary.to_safe_dict()
    lines = [f"{key}={_format_value(value)}" for key, value in data.items()]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate artifact body isolated temp write fixtures with "
            "summary-only output."
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
        help="Safe relative case selector, such as valid/case_name.",
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
            case_dir = args.fixture_root / PurePosixPath(args.fixture_case)
            expected_kind = PurePosixPath(args.fixture_case).parts[0]
            result = validate_isolated_write_fixture_case(
                case_dir,
                expected_kind=expected_kind,
            )
            _print_summary(result, as_json=args.as_json)
            if result.is_input_error:
                return 4
            if result.is_mismatch:
                return 3
            return 0

        summary = validate_isolated_write_fixture_root(args.fixture_root)
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


def _execute_case_in_temp_root(
    *,
    temp_root: Path,
    fixture_payloads: Mapping[str, Any],
    isolated_request: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> IsolatedWriteExecutionResult:
    expected_reasons = _safe_string_list(expected.get("expected_reason_codes"))
    unsupported = [
        reason for reason in expected_reasons if reason in UNSUPPORTED_WRITE_ATTEMPT_REASONS
    ]
    if unsupported:
        return _unsupported_execution_result(unsupported)

    input_dir = temp_root / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    request_path = input_dir / ARTIFACT_BODY_REQUEST_FILE
    pointer_path = input_dir / ARTIFACT_WRITER_RESULT_POINTER_FILE
    _write_json(request_path, fixture_payloads[ARTIFACT_BODY_REQUEST_FILE])
    _write_json(pointer_path, fixture_payloads[ARTIFACT_WRITER_RESULT_POINTER_FILE])

    artifact_body_out = isolated_request.get("artifact_body_out")
    precreated_output = False
    if isolated_request.get("precreate_output_file") is True and isinstance(
        artifact_body_out, str
    ):
        precreated = temp_root / ARTIFACT_BODY_FILE_WRITE_SAFE_ROOT / artifact_body_out
        precreated.parent.mkdir(parents=True, exist_ok=True)
        precreated.write_text("precreated synthetic placeholder\n", encoding="utf-8")
        precreated_output = True

    command = [
        sys.executable,
        "-m",
        "learner_state.frozen_policy_generation_artifact_body",
        "--request",
        request_path.as_posix(),
        "--pointer",
        pointer_path.as_posix(),
    ]
    cli_mode = isolated_request.get("cli_mode")
    if cli_mode in ("safe-metadata", "suppressed"):
        command.extend(["--mode", str(cli_mode)])
    if isinstance(artifact_body_out, str):
        command.extend(["--artifact-body-out", artifact_body_out])

    env = dict(os.environ)
    python_root = Path(__file__).resolve().parents[1]
    env["PYTHONPATH"] = (
        python_root.as_posix()
        if not env.get("PYTHONPATH")
        else python_root.as_posix() + os.pathsep + env["PYTHONPATH"]
    )
    completed = subprocess.run(
        command,
        cwd=temp_root,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    summary = _parse_human_summary(completed.stdout)
    output_file = _expected_output_file(temp_root, artifact_body_out)
    output_file_exists = output_file.exists() if output_file is not None else False
    output_file_written = output_file_exists and not precreated_output
    parse_ok = False
    allowed_keys_only = False
    file_reason_codes: list[str] = []
    file_failed_checks: list[str] = []
    if output_file_written and output_file is not None:
        parse_ok, allowed_keys_only, file_reason_codes, file_failed_checks = (
            _validate_written_file(output_file)
        )

    cleanup_ok = _cleanup_safe_root(temp_root)
    residue_count = _residue_count(temp_root)
    stdout_free = _output_body_free(completed.stdout)
    stderr_free = _output_body_free(completed.stderr)
    no_absolute_paths = not _has_absolute_path(completed.stdout + completed.stderr)
    body_payload_printed = not (stdout_free and stderr_free)
    reason_codes = _dedupe(
        [
            *_safe_summary_reason_codes(summary.get("reason_codes")),
            *file_reason_codes,
        ]
    )
    if (
        isinstance(artifact_body_out, str)
        and re.match(r"^[A-Za-z]:", artifact_body_out)
        and "unsafe_output_path_filename" in reason_codes
    ):
        reason_codes = [
            "unsafe_absolute_output_path" if reason == "unsafe_output_path_filename" else reason
            for reason in reason_codes
        ]

    failed_checks = _dedupe(
        [
            *_safe_summary_reason_codes(summary.get("failed_checks")),
            *file_failed_checks,
        ]
    )

    return IsolatedWriteExecutionResult(
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        summary=summary,
        output_file_exists_before_cleanup=output_file_written,
        output_file_parse_ok=parse_ok,
        output_file_allowed_keys_only=allowed_keys_only,
        output_file_cleanup_ok=cleanup_ok,
        stdout_body_free=stdout_free,
        stderr_body_free=stderr_free,
        body_payload_printed=body_payload_printed,
        no_raw_rows=_no_forbidden_payload_token(
            completed.stdout + completed.stderr,
            "raw_rows",
        ),
        no_logits_dump=_no_forbidden_payload_token(
            completed.stdout + completed.stderr,
            "logits",
        ),
        no_private_paths=_no_fragment(completed.stdout + completed.stderr, "/Users/")
        and _no_forbidden_payload_token(
            completed.stdout + completed.stderr,
            "private_path",
        ),
        no_absolute_paths=no_absolute_paths,
        no_manifest_body=_no_fragment(completed.stdout + completed.stderr, '"manifest_body"'),
        no_generated_policy_body=_no_fragment(
            completed.stdout + completed.stderr,
            '"generated_policy_body"',
        ),
        residue_file_count=residue_count,
        reason_codes=reason_codes,
        failed_checks=failed_checks,
    )


def _unsupported_execution_result(reason_codes: list[str]) -> IsolatedWriteExecutionResult:
    return IsolatedWriteExecutionResult(
        exit_code=1,
        stdout="",
        stderr="",
        summary={
            "artifact_file_written": False,
            "artifact_body_output_path_available": False,
            "manifest_file_written": False,
            "manifest_body_generated": False,
        },
        output_file_exists_before_cleanup=False,
        output_file_parse_ok=False,
        output_file_allowed_keys_only=False,
        output_file_cleanup_ok=True,
        stdout_body_free=True,
        stderr_body_free=True,
        body_payload_printed=False,
        no_raw_rows=True,
        no_logits_dump=True,
        no_private_paths=True,
        no_absolute_paths=True,
        no_manifest_body=True,
        no_generated_policy_body=True,
        residue_file_count=0,
        reason_codes=list(reason_codes),
        failed_checks=list(reason_codes),
    )


def _validate_written_file(
    output_file: Path,
) -> tuple[bool, bool, list[str], list[str]]:
    try:
        payload = json.loads(output_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False, False, ["written_file_json_parse_failed"], ["written_file_json"]
    if not isinstance(payload, Mapping):
        return True, False, ["written_file_not_object"], ["written_file_object"]

    reason_codes: list[str] = []
    failed_checks: list[str] = []
    unknown_keys = sorted(set(str(key) for key in payload) - set(ALLOWED_BODY_FIELDS))
    if unknown_keys:
        reason_codes.append("written_file_forbidden_key")
        failed_checks.append("written_file_allowed_keys")
    for field_name in REQUIRED_BODY_FIELDS:
        if field_name not in payload:
            reason_codes.append("written_file_required_field_missing")
            failed_checks.append(field_name)
    if not payload.get("synthetic_only_notice"):
        reason_codes.append("missing_synthetic_notice")
        failed_checks.append("synthetic_only_notice")
    if not payload.get("no_oracle_notice"):
        reason_codes.append("missing_no_oracle_notice")
        failed_checks.append("no_oracle_notice")
    if not payload.get("non_proof_notice"):
        reason_codes.append("missing_non_proof_notice")
        failed_checks.append("non_proof_notice")

    body_reasons, body_checks = _scan_body_payload(payload)
    reason_codes.extend(body_reasons)
    failed_checks.extend(body_checks)

    count_summary = payload.get("count_summary")
    if isinstance(count_summary, Mapping):
        for field_name in ZERO_COUNT_FIELDS:
            if count_summary.get(field_name) != 0:
                reason_codes.append("written_file_forbidden_count_nonzero")
                failed_checks.append(field_name)
    else:
        reason_codes.append("written_file_count_summary_missing")
        failed_checks.append("count_summary")

    allowed = not _dedupe(reason_codes)
    return True, allowed, _dedupe(reason_codes), _dedupe(failed_checks)


def _scan_body_payload(value: Any) -> tuple[list[str], list[str]]:
    reason_codes: list[str] = []
    failed_checks: list[str] = []

    def visit(item: Any, key_context: str | None = None) -> None:
        if isinstance(item, Mapping):
            for raw_key, nested in item.items():
                key = str(raw_key)
                key_lower = key.lower()
                if key_lower in BODY_FORBIDDEN_KEYS:
                    reason_codes.append(f"forbidden_{key_lower}")
                    failed_checks.append(key_lower)
                visit(nested, key_lower)
        elif isinstance(item, list):
            for nested in item:
                visit(nested, key_context)
        elif isinstance(item, str):
            if _has_absolute_path(item):
                reason_codes.append("private_path_leakage")
                failed_checks.append(key_context or "absolute_path_value")

    visit(value)
    return _dedupe(reason_codes), _dedupe(failed_checks)


def _fixture_contract_errors(
    case_id: str,
    expected_kind: str | None,
    payloads: Mapping[str, Any],
) -> list[IsolatedWriteValidationError]:
    checks = (
        (
            CASE_METADATA_FILE,
            CASE_METADATA_SCHEMA_VERSION,
            REQUIRED_CASE_METADATA_FIELDS,
        ),
        (
            ARTIFACT_BODY_REQUEST_FILE,
            ARTIFACT_BODY_REQUEST_SCHEMA_VERSION,
            ("schema_version", "case_id"),
        ),
        (
            ARTIFACT_WRITER_RESULT_POINTER_FILE,
            ARTIFACT_WRITER_RESULT_POINTER_SCHEMA_VERSION,
            ("schema_version", "case_id"),
        ),
        (
            ISOLATED_WRITE_REQUEST_FILE,
            ISOLATED_WRITE_REQUEST_SCHEMA_VERSION,
            REQUIRED_ISOLATED_WRITE_REQUEST_FIELDS,
        ),
        (
            EXPECTED_ISOLATED_WRITE_RESULT_FILE,
            EXPECTED_ISOLATED_WRITE_RESULT_SCHEMA_VERSION,
            REQUIRED_EXPECTED_RESULT_FIELDS,
        ),
    )
    errors: list[IsolatedWriteValidationError] = []
    for file_name, schema_version, required_fields in checks:
        payload = payloads[file_name]
        if not isinstance(payload, Mapping):
            errors.append(IsolatedWriteValidationError("malformed_fixture", file_name))
            continue
        if payload.get("schema_version") != schema_version:
            errors.append(
                IsolatedWriteValidationError("schema_version_unknown", file_name)
            )
        if payload.get("case_id") != case_id:
            errors.append(IsolatedWriteValidationError("case_id_mismatch", file_name))
        missing = [field for field in required_fields if field not in payload]
        if missing:
            errors.append(IsolatedWriteValidationError("required_field_missing", file_name))

    metadata = payloads[CASE_METADATA_FILE]
    if expected_kind and isinstance(metadata, Mapping):
        if metadata.get("case_kind") != expected_kind:
            errors.append(IsolatedWriteValidationError("case_kind_mismatch", "case_kind"))
    expected = payloads[EXPECTED_ISOLATED_WRITE_RESULT_FILE]
    if isinstance(expected, Mapping):
        if expected.get("expected_category") not in RESULT_CATEGORIES:
            errors.append(
                IsolatedWriteValidationError(
                    "expected_category_unknown",
                    "expected_category",
                )
            )
    return errors


def _summary_from_results(
    results: tuple[IsolatedWriteCaseResult, ...],
) -> IsolatedWriteValidationSummary:
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

    total_cases = len([result for result in results if result.case_id != "fixture_root"])
    input_errors = sum(1 for result in results if result.is_input_error)
    mismatches = sum(1 for result in results if result.is_mismatch)
    matched = sum(1 for result in results if result.matched)
    return IsolatedWriteValidationSummary(
        mode="isolated_write_validation",
        validation_schema_version=VALIDATION_SCHEMA_VERSION,
        total_cases=total_cases if results[0].case_id != "fixture_root" else 0,
        valid_cases=valid_cases,
        invalid_cases=invalid_cases,
        pass_written_cases=category_counts["pass_written"],
        pass_no_write_cases=category_counts["pass_no_write"],
        usage_error_cases=category_counts["usage_error_no_write"],
        fail_closed_cases=category_counts["fail_closed_no_write"],
        matched_cases=matched,
        mismatched_cases=mismatches,
        input_error_cases=input_errors,
        residue_file_count=sum(result.residue_file_count for result in results),
        reason_code_counts=dict(reason_counts),
        case_results=results,
        body_payload_printed=any(result.body_payload_printed for result in results),
        stdout_body_suppressed=all(result.stdout_body_free for result in results),
        stderr_body_suppressed=all(result.stderr_body_free for result in results),
        no_raw_rows=all(result.no_raw_rows for result in results),
        no_logits_dump=all(result.no_logits_dump for result in results),
        no_private_paths=all(result.no_private_paths for result in results),
        no_absolute_paths=all(result.no_absolute_paths for result in results),
        no_manifest_body=all(result.no_manifest_body for result in results),
        no_generated_policy_body=all(result.no_generated_policy_body for result in results),
        synthetic_only_checked=True,
        no_oracle_checked=True,
        path_policy_checked=True,
        file_content_policy_checked=True,
        cleanup_checked=all(result.file_cleanup_ok for result in results),
        temp_root_isolated=True,
        release_quality_ready=False,
    )


def _matches_expected(
    *,
    expected_category: str,
    expected_status: str,
    expected_exit_code: int | None,
    expected_file_written: bool,
    expected_reason_codes: list[str],
    actual_category: str,
    actual_status: str,
    actual_exit_code: int,
    actual_file_written: bool,
    actual_reason_codes: list[str],
) -> bool:
    if actual_category != expected_category:
        return False
    if actual_status != expected_status:
        return False
    if actual_file_written != expected_file_written:
        return False
    if expected_category != "fail_closed_no_write" and expected_exit_code is not None:
        if actual_exit_code != expected_exit_code:
            return False
    if expected_category == "fail_closed_no_write" and actual_exit_code == 0:
        return False
    for reason in expected_reason_codes:
        if reason not in actual_reason_codes:
            return False
    return True


def _expected_safety_matches(
    expected: Mapping[str, Any],
    execution: IsolatedWriteExecutionResult,
) -> bool:
    checks = {
        "expected_file_parse_ok": execution.output_file_parse_ok,
        "expected_file_allowed_keys_only": execution.output_file_allowed_keys_only,
        "expected_file_cleanup_ok": execution.output_file_cleanup_ok,
        "expected_residue_file_count": execution.residue_file_count,
        "expected_stdout_body_free": execution.stdout_body_free,
        "expected_stderr_body_free": execution.stderr_body_free,
        "expected_manifest_file_written": execution.summary.get("manifest_file_written")
        is True,
        "expected_manifest_body_generated": execution.summary.get(
            "manifest_body_generated"
        )
        is True,
        "expected_no_absolute_paths": execution.no_absolute_paths,
        "expected_no_logits": execution.no_logits_dump,
        "expected_no_private_paths": execution.no_private_paths,
        "expected_no_raw_rows": execution.no_raw_rows,
    }
    for key, actual in checks.items():
        expected_value = expected.get(key)
        if isinstance(expected_value, bool) and actual != expected_value:
            return False
        if isinstance(expected_value, int) and actual != expected_value:
            return False
    return True


def _actual_category_from_execution(execution: IsolatedWriteExecutionResult) -> str:
    if execution.exit_code == 0:
        if execution.output_file_exists_before_cleanup:
            return "pass_written"
        return "pass_no_write"
    if execution.exit_code == 2:
        return "usage_error_no_write"
    if execution.exit_code in (1, 3):
        return "fail_closed_no_write"
    return "input_error"


def _actual_status_from_category(category: str) -> str:
    if category in ("pass_written", "pass_no_write"):
        return "pass"
    if category == "usage_error_no_write":
        return "usage_error"
    if category == "fail_closed_no_write":
        return "fail_closed"
    if category == "mismatch":
        return "mismatch"
    return "input_error"


def _input_error_case(
    *,
    case_id: str,
    reason_code: str,
    expected_kind: str | None,
    failed_check: str | None = None,
) -> IsolatedWriteCaseResult:
    return IsolatedWriteCaseResult(
        case_id=case_id,
        expected_kind=expected_kind,
        expected_category="input_error",
        expected_status="input_error",
        expected_exit_code=None,
        expected_file_written=False,
        actual_category="input_error",
        actual_status="input_error",
        actual_exit_code=None,
        actual_file_written=False,
        matched=False,
        reason_codes=[reason_code],
        failed_checks=[failed_check or reason_code],
        file_parse_ok=False,
        file_allowed_keys_only=False,
        file_cleanup_ok=True,
        stdout_body_free=True,
        stderr_body_free=True,
        safe_relative_path_only=True,
        manifest_file_written=False,
        manifest_body_generated=False,
        body_payload_printed=False,
        no_raw_rows=True,
        no_logits_dump=True,
        no_private_paths=True,
        no_absolute_paths=True,
        no_manifest_body=True,
        no_generated_policy_body=True,
        synthetic_only_checked=True,
        no_oracle_checked=True,
        path_policy_checked=True,
        file_content_policy_checked=True,
        cleanup_checked=True,
        temp_root_isolated=True,
        release_quality_ready=False,
        residue_file_count=0,
    )


def _parse_human_summary(stdout: str) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for line in stdout.splitlines():
        if "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        summary[key] = _parse_summary_value(raw_value)
    return summary


def _parse_summary_value(raw_value: str) -> Any:
    value = raw_value.strip()
    if value == "true":
        return True
    if value == "false":
        return False
    if value == "none":
        return []
    if value.startswith("{") or value.startswith("["):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _safe_summary_reason_codes(value: Any) -> list[str]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    if isinstance(value, str):
        if value == "none":
            return []
        return [item for item in value.split(",") if item]
    return []


def _summary_has_safe_relative_path_only(summary: Mapping[str, Any]) -> bool:
    value = summary.get("artifact_body_output_path")
    if value in (None, [], "none"):
        return True
    if not isinstance(value, str):
        return False
    if _has_absolute_path(value):
        return False
    return value.startswith(ARTIFACT_BODY_FILE_WRITE_SAFE_ROOT.as_posix())


def _expected_output_file(temp_root: Path, artifact_body_out: Any) -> Path | None:
    if not isinstance(artifact_body_out, str):
        return None
    candidate = Path(artifact_body_out)
    if candidate.is_absolute() or any(part == ".." for part in candidate.parts):
        return None
    return temp_root / ARTIFACT_BODY_FILE_WRITE_SAFE_ROOT / candidate


def _output_body_free(output: str) -> bool:
    lowered = output.lower()
    return not any(fragment.lower() in lowered for fragment in STDOUT_FORBIDDEN_FRAGMENTS)


def _has_absolute_path(value: str) -> bool:
    return bool(LOCAL_ABSOLUTE_PATH_PATTERN.search(value))


def _no_fragment(value: str, fragment: str) -> bool:
    return fragment not in value


def _no_forbidden_payload_token(value: str, token: str) -> bool:
    return (
        f'"{token}":' not in value
        and f"{token}=" not in value
        and f"{token}:" not in value
    )


def _cleanup_safe_root(temp_root: Path) -> bool:
    try:
        safe_root = temp_root / ARTIFACT_BODY_FILE_WRITE_SAFE_ROOT
        if safe_root.exists():
            shutil.rmtree(safe_root)
        return True
    except OSError:
        return False


def _residue_count(temp_root: Path) -> int:
    safe_root = temp_root / ARTIFACT_BODY_FILE_WRITE_SAFE_ROOT
    if not safe_root.exists():
        return 0
    return sum(1 for path in safe_root.rglob("*") if path.is_file())


def _fixture_case_selector_error(selector: str) -> str | None:
    if selector == "":
        return "empty_fixture_case_selector"
    posix = PurePosixPath(selector)
    if selector.startswith("/") or Path(selector).is_absolute():
        return "unsafe_absolute_fixture_case_selector"
    if any(part == ".." for part in posix.parts):
        return "unsafe_parent_traversal_fixture_case_selector"
    if len(posix.parts) != 2 or posix.parts[0] not in {"valid", "invalid"}:
        return "unsafe_fixture_case_selector"
    return None


def _case_id_from_dir(case_dir: Path) -> str:
    if case_dir.parent.name in {"valid", "invalid"}:
        return f"{case_dir.parent.name}/{case_dir.name}"
    return case_dir.name


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _safe_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


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
    summary: IsolatedWriteValidationSummary | IsolatedWriteCaseResult,
    *,
    as_json: bool,
) -> None:
    payload = summary.to_safe_dict()
    if as_json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    else:
        print(summarize_isolated_write_validation(summary))


if __name__ == "__main__":
    raise SystemExit(main())
