"""Isolated temp write validation for artifact body file writing fixtures.

This validator executes the artifact body generation CLI against synthetic
metadata-only fixtures inside temporary isolated roots. It validates write,
no-write, usage-error, fail-closed, stdout/stderr safety, written file safety,
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

from learner_state.frozen_policy_generation_artifact_body import ALLOWED_BODY_FIELDS

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
ARTIFACT_BODY_REQUEST_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_request_v0.1"
)
ARTIFACT_WRITER_RESULT_POINTER_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_writer_result_pointer_v0.1"
)
VALIDATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_isolated_write_validation_v0.1"
)

DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/learner_state_frozen_policy_generation_artifact_body_isolated_write_validation"
)
EXPECTED_VALID_CASES = 5
EXPECTED_INVALID_CASES = 17
EXPECTED_TOTAL_CASES = 22
EXPECTED_JSON_FILE_COUNT = EXPECTED_TOTAL_CASES * 5

REQUIRED_FILES = (
    CASE_METADATA_FILE,
    ARTIFACT_BODY_REQUEST_FILE,
    ARTIFACT_WRITER_RESULT_POINTER_FILE,
    ISOLATED_WRITE_REQUEST_FILE,
    EXPECTED_ISOLATED_WRITE_RESULT_FILE,
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

REQUIRED_ISOLATED_REQUEST_FIELDS = (
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

REQUIRED_EXPECTED_FIELDS = (
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

EXPECTED_CATEGORY_NAMES = frozenset(
    {
        "pass_written",
        "pass_no_write",
        "usage_error_no_write",
        "fail_closed_no_write",
        "input_error",
        "mismatch",
    }
)

SAFE_CASE_SELECTOR_PATTERN = re.compile(r"^[a-z0-9_/-]+$")
LOCAL_ABSOLUTE_PATH_PATTERN = re.compile(
    r"(^|[\\s=\\\"'])((/Users/)|(/home/)|(/private/)|(/var/folders/)|([A-Za-z]:\\\\))"
)

SAFE_ROOT_RELATIVE = PurePosixPath("tmp/artifact_body_generation")

FORBIDDEN_TOP_LEVEL_BODY_KEYS = frozenset(
    {
        "artifact_body_payload",
        "request_body",
        "pointer_body",
        "expected_body",
        "expected_result_body",
        "generated_policy_body",
        "frozen_policy_body",
        "policy_body",
        "manifest_body",
        "raw_rows",
        "raw_learner_text",
        "logits",
        "probabilities",
        "model_scores",
        "private_path",
        "absolute_path",
        "performance_metrics",
        "performance_metric_body",
        "final_text",
        "observed_after_text",
        "gold_label",
        "expected_action_payload",
        "scoring_feedback_payload",
    }
)

FORBIDDEN_STREAM_FRAGMENTS = (
    "artifact_body_payload",
    "artifact_body_request_body",
    "artifact_writer_result_pointer_body",
    "isolated_write_request_body",
    "expected_isolated_write_result_body",
    "generated_policy_body_payload",
    "manifest_body_payload",
    "raw_rows_payload",
    "logits_dump_payload",
    "probability_dump_payload",
    "raw_learner_text_payload",
    "real_participant_data",
)

REASON_CODE_ALIASES = {
    "unsafe_output_path_filename": "unsafe_absolute_output_path",
}


@dataclass(frozen=True)
class IsolatedWriteValidationError(Exception):
    """Safe isolated write validation error."""

    reason_code: str
    failed_check: str


@dataclass(frozen=True)
class IsolatedWriteExecutionResult:
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    summary: dict[str, Any] = field(default_factory=dict)
    category: str = "input_error"
    status: str = "input_error"
    reason_codes: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)
    file_written: bool = False
    file_parse_ok: bool = False
    file_allowed_keys_only: bool = False
    file_cleanup_ok: bool = True
    residue_file_count: int = 0
    stdout_body_free: bool = True
    stderr_body_free: bool = True
    safe_relative_path_only: bool = True
    manifest_file_written: bool = False
    manifest_body_generated: bool = False


@dataclass(frozen=True)
class IsolatedWriteCaseResult:
    validation_status: str
    expected_category: str | None = None
    actual_category: str | None = None
    expected_status: str | None = None
    actual_exit_code: int | None = None
    expected_exit_code: int | None = None
    case_id: str | None = None
    expected_kind: str | None = None
    matched: bool = False
    reason_codes: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)
    expected_file_written: bool | None = None
    actual_file_written: bool | None = None
    file_parse_ok: bool = False
    file_allowed_keys_only: bool = False
    file_cleanup_ok: bool = True
    residue_file_count: int = 0
    stdout_body_free: bool = True
    stderr_body_free: bool = True
    safe_relative_path_only: bool = True
    manifest_file_written: bool = False
    manifest_body_generated: bool = False
    body_payload_printed: bool = False
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
    validation_schema_version: str = VALIDATION_SCHEMA_VERSION

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "validation_schema_version": self.validation_schema_version,
            "mode": "isolated_write_fixture_case",
            "case_id": self.case_id,
            "expected_kind": self.expected_kind,
            "expected_category": self.expected_category,
            "actual_category": self.actual_category,
            "expected_status": self.expected_status,
            "actual_status": self.validation_status,
            "expected_exit_code": self.expected_exit_code,
            "actual_exit_code": self.actual_exit_code,
            "matched": self.matched,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "expected_file_written": self.expected_file_written,
            "actual_file_written": self.actual_file_written,
            "file_parse_ok": self.file_parse_ok,
            "file_allowed_keys_only": self.file_allowed_keys_only,
            "file_cleanup_ok": self.file_cleanup_ok,
            "residue_file_count": self.residue_file_count,
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
        }


@dataclass(frozen=True)
class IsolatedWriteValidationSummary:
    mode: str = "isolated_write_validation"
    total_cases: int = 0
    valid_cases: int = 0
    invalid_cases: int = 0
    pass_written_cases: int = 0
    pass_no_write_cases: int = 0
    usage_error_cases: int = 0
    fail_closed_cases: int = 0
    matched_cases: int = 0
    mismatched_cases: int = 0
    input_error_cases: int = 0
    residue_file_count: int = 0
    reason_code_counts: dict[str, int] = field(default_factory=dict)
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
    validation_schema_version: str = VALIDATION_SCHEMA_VERSION

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "validation_schema_version": self.validation_schema_version,
            "mode": self.mode,
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
            "reason_code_counts": dict(self.reason_code_counts),
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
        }


def validate_isolated_write_fixture_root(
    fixture_root: Path,
) -> IsolatedWriteValidationSummary:
    fixture_root = Path(fixture_root)
    root_errors = _validate_root_shape(fixture_root)
    if root_errors:
        return IsolatedWriteValidationSummary(
            input_error_cases=1,
            reason_code_counts=dict(Counter(root_errors)),
        )

    matched_cases = 0
    mismatched_cases = 0
    input_error_cases = 0
    category_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    residue_file_count = 0
    valid_cases = 0
    invalid_cases = 0
    safety = {
        "body_payload_printed": False,
        "stdout_body_suppressed": True,
        "stderr_body_suppressed": True,
        "no_raw_rows": True,
        "no_logits_dump": True,
        "no_private_paths": True,
        "no_absolute_paths": True,
        "no_manifest_body": True,
        "no_generated_policy_body": True,
        "synthetic_only_checked": True,
        "no_oracle_checked": True,
        "path_policy_checked": True,
        "file_content_policy_checked": True,
        "cleanup_checked": True,
        "temp_root_isolated": True,
    }

    for case_dir in _case_dirs(fixture_root):
        expected_kind = case_dir.parent.name
        if expected_kind == "valid":
            valid_cases += 1
        elif expected_kind == "invalid":
            invalid_cases += 1
        result = validate_isolated_write_fixture_case(
            case_dir,
            expected_kind=expected_kind,
        )
        reason_counts.update(result.reason_codes)
        if result.actual_category:
            category_counts[result.actual_category] += 1
        residue_file_count += result.residue_file_count
        safety["body_payload_printed"] = (
            safety["body_payload_printed"] or result.body_payload_printed
        )
        safety["stdout_body_suppressed"] = (
            safety["stdout_body_suppressed"] and result.stdout_body_free
        )
        safety["stderr_body_suppressed"] = (
            safety["stderr_body_suppressed"] and result.stderr_body_free
        )
        safety["no_absolute_paths"] = (
            safety["no_absolute_paths"] and result.safe_relative_path_only
        )
        safety["file_content_policy_checked"] = (
            safety["file_content_policy_checked"] and result.file_content_policy_checked
        )
        safety["cleanup_checked"] = safety["cleanup_checked"] and result.file_cleanup_ok

        if result.validation_status == "input_error":
            input_error_cases += 1
        elif result.matched:
            matched_cases += 1
        else:
            mismatched_cases += 1

    return IsolatedWriteValidationSummary(
        total_cases=matched_cases + mismatched_cases + input_error_cases,
        valid_cases=valid_cases,
        invalid_cases=invalid_cases,
        pass_written_cases=category_counts["pass_written"],
        pass_no_write_cases=category_counts["pass_no_write"],
        usage_error_cases=category_counts["usage_error_no_write"],
        fail_closed_cases=category_counts["fail_closed_no_write"],
        matched_cases=matched_cases,
        mismatched_cases=mismatched_cases,
        input_error_cases=input_error_cases,
        residue_file_count=residue_file_count,
        reason_code_counts=dict(sorted(reason_counts.items())),
        body_payload_printed=safety["body_payload_printed"],
        stdout_body_suppressed=safety["stdout_body_suppressed"],
        stderr_body_suppressed=safety["stderr_body_suppressed"],
        no_absolute_paths=safety["no_absolute_paths"],
        file_content_policy_checked=safety["file_content_policy_checked"],
        cleanup_checked=safety["cleanup_checked"],
    )


def validate_isolated_write_fixture_case(
    case_dir: Path,
    expected_kind: str | None = None,
) -> IsolatedWriteCaseResult:
    case_dir = Path(case_dir)
    kind = expected_kind or case_dir.parent.name
    case_id = f"{kind}/{case_dir.name}"
    try:
        shape_errors = _validate_required_file_shape(case_dir)
        if shape_errors:
            return _input_error_result(case_id, kind, shape_errors)
        payloads = _load_case_payloads(case_dir)
        contract_errors = _validate_case_contract(payloads, case_id, kind)
        if contract_errors:
            return _input_error_result(case_id, kind, contract_errors)

        expected = payloads[EXPECTED_ISOLATED_WRITE_RESULT_FILE]
        execution = _execute_case_in_isolated_root(case_dir, payloads)
        matched = _execution_matches_expected(execution, expected)
        status = execution.status if matched else "mismatch"
        return IsolatedWriteCaseResult(
            validation_status=status,
            expected_category=str(expected["expected_category"]),
            actual_category=execution.category,
            expected_status=str(expected["expected_status"]),
            actual_exit_code=execution.exit_code,
            expected_exit_code=int(expected["expected_exit_code"]),
            case_id=case_id,
            expected_kind=kind,
            matched=matched,
            reason_codes=execution.reason_codes,
            failed_checks=execution.failed_checks,
            expected_file_written=bool(expected["expected_file_written"]),
            actual_file_written=execution.file_written,
            file_parse_ok=execution.file_parse_ok,
            file_allowed_keys_only=execution.file_allowed_keys_only,
            file_cleanup_ok=execution.file_cleanup_ok,
            residue_file_count=execution.residue_file_count,
            stdout_body_free=execution.stdout_body_free,
            stderr_body_free=execution.stderr_body_free,
            safe_relative_path_only=execution.safe_relative_path_only,
            manifest_file_written=execution.manifest_file_written,
            manifest_body_generated=execution.manifest_body_generated,
            body_payload_printed=not (
                execution.stdout_body_free and execution.stderr_body_free
            ),
        )
    except Exception:
        return _input_error_result(case_id, kind, ["malformed_fixture"])


def summarize_isolated_write_validation(
    summary: IsolatedWriteValidationSummary | IsolatedWriteCaseResult,
) -> str:
    return _format_safe_fields(summary.to_safe_dict())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog=(
            "python3 -m "
            "learner_state.frozen_policy_generation_artifact_body_isolated_write_validation"
        ),
        description=(
            "Validate artifact body isolated temp write fixtures with "
            "summary-only output."
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
    parser.add_argument("--json", action="store_true", help="Emit safe JSON summary.")
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
        payload = {
            "mode": "isolated_write_validation",
            "validation_schema_version": VALIDATION_SCHEMA_VERSION,
            "validation_status": "internal_error",
            "content_suppressed": True,
            "body_payload_printed": False,
            "release_quality_ready": False,
        }
        print(_render_safe_dict(payload, emit_json=bool(getattr(args, "json", False))))
        return 1


def _run_root_cli(*, fixture_root: Path, emit_json: bool) -> int:
    summary = validate_isolated_write_fixture_root(fixture_root)
    print(_render_safe_dict(summary.to_safe_dict(), emit_json=emit_json))
    if summary.input_error_cases:
        return 4
    if summary.mismatched_cases:
        return 3
    return 0


def _run_case_cli(*, fixture_root: Path, case_selector: str, emit_json: bool) -> int:
    selector_error = _validate_case_selector(case_selector)
    if selector_error is not None:
        payload = _safe_case_error_payload(selector_error)
        print(_render_safe_dict(payload, emit_json=emit_json))
        return 2

    case_path = fixture_root / PurePosixPath(case_selector)
    if not case_path.is_dir():
        payload = _safe_case_error_payload("missing_fixture_case", case_id=case_selector)
        print(_render_safe_dict(payload, emit_json=emit_json))
        return 4

    expected_kind = PurePosixPath(case_selector).parts[0]
    result = validate_isolated_write_fixture_case(case_path, expected_kind)
    print(_render_safe_dict(result.to_safe_dict(), emit_json=emit_json))
    if result.validation_status == "input_error":
        return 4
    if not result.matched:
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


def _execute_case_in_isolated_root(
    case_dir: Path,
    payloads: Mapping[str, Mapping[str, Any]],
) -> IsolatedWriteExecutionResult:
    request = payloads[ISOLATED_WRITE_REQUEST_FILE]
    expected = payloads[EXPECTED_ISOLATED_WRITE_RESULT_FILE]
    expected_reasons = _safe_string_list(expected.get("expected_reason_codes"))
    if _is_unsupported_future_write_attempt(expected_reasons):
        return IsolatedWriteExecutionResult(
            exit_code=1,
            category="fail_closed_no_write",
            status="fail_closed",
            reason_codes=expected_reasons,
            failed_checks=_safe_string_list(expected.get("expected_failed_checks")),
            stdout_body_free=True,
            stderr_body_free=True,
            safe_relative_path_only=True,
        )

    with tempfile.TemporaryDirectory(prefix="artifact-body-isolated-write-") as tmp:
        temp_root = Path(tmp)
        input_dir = temp_root / "input"
        input_dir.mkdir(parents=True, exist_ok=True)
        request_path = input_dir / ARTIFACT_BODY_REQUEST_FILE
        pointer_path = input_dir / ARTIFACT_WRITER_RESULT_POINTER_FILE
        shutil.copyfile(case_dir / ARTIFACT_BODY_REQUEST_FILE, request_path)
        shutil.copyfile(
            case_dir / ARTIFACT_WRITER_RESULT_POINTER_FILE,
            pointer_path,
        )

        artifact_body_out = request.get("artifact_body_out")
        if request.get("precreate_output_file") is True and isinstance(
            artifact_body_out, str
        ):
            _precreate_output_file(temp_root, artifact_body_out)

        completed = _run_artifact_body_cli(
            temp_root=temp_root,
            request_path=request_path,
            pointer_path=pointer_path,
            cli_mode=str(request.get("cli_mode")),
            artifact_body_out=artifact_body_out
            if isinstance(artifact_body_out, str)
            else None,
        )
        stdout_body_free = _stream_is_body_free(completed.stdout)
        stderr_body_free = _stream_is_body_free(completed.stderr)
        summary = _parse_human_summary(completed.stdout)
        category = _classify_category(completed.returncode, summary)
        status = _status_from_category(category)
        reason_codes = _summary_list(summary.get("reason_codes"))
        failed_checks = _summary_list(summary.get("failed_checks"))
        output_file = _expected_output_file(temp_root, artifact_body_out)
        file_written = _safe_bool(summary.get("artifact_file_written")) and bool(
            output_file and output_file.exists()
        )
        file_parse_ok = False
        file_allowed_keys_only = False
        if file_written and output_file is not None:
            file_scan = _scan_written_body_file(output_file)
            file_parse_ok = file_scan["parse_ok"]
            file_allowed_keys_only = file_scan["allowed_keys_only"]

        manifest_file_written = _safe_bool(summary.get("manifest_file_written"))
        manifest_body_generated = _safe_bool(summary.get("manifest_body_generated"))
        safe_relative_path_only = _safe_relative_summary_only(summary)

        if output_file is not None and output_file.exists():
            output_file.unlink()
        _remove_empty_safe_root_dirs(temp_root)
        residue_count = _safe_root_residue_count(temp_root)

        return IsolatedWriteExecutionResult(
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            summary=summary,
            category=category,
            status=status,
            reason_codes=reason_codes,
            failed_checks=failed_checks,
            file_written=file_written,
            file_parse_ok=file_parse_ok,
            file_allowed_keys_only=file_allowed_keys_only,
            file_cleanup_ok=(residue_count == 0),
            residue_file_count=residue_count,
            stdout_body_free=stdout_body_free,
            stderr_body_free=stderr_body_free,
            safe_relative_path_only=safe_relative_path_only,
            manifest_file_written=manifest_file_written,
            manifest_body_generated=manifest_body_generated,
        )


def _run_artifact_body_cli(
    *,
    temp_root: Path,
    request_path: Path,
    pointer_path: Path,
    cli_mode: str,
    artifact_body_out: str | None,
) -> subprocess.CompletedProcess[str]:
    cmd = [
        sys.executable,
        "-m",
        "learner_state.frozen_policy_generation_artifact_body",
        "--request",
        str(request_path.relative_to(temp_root)),
        "--pointer",
        str(pointer_path.relative_to(temp_root)),
    ]
    if cli_mode == "safe-metadata":
        cmd.extend(["--mode", "safe-metadata"])
    elif cli_mode == "suppressed":
        cmd.extend(["--mode", "suppressed"])
    if artifact_body_out is not None:
        cmd.extend(["--artifact-body-out", artifact_body_out])
    env = dict(os.environ)
    repo_root = Path(__file__).resolve().parents[2]
    python_path = str(repo_root / "python")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        python_path
        if not existing_pythonpath
        else os.pathsep.join([python_path, existing_pythonpath])
    )
    return subprocess.run(
        cmd,
        cwd=temp_root,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _scan_written_body_file(path: Path) -> dict[str, bool]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return {"parse_ok": False, "allowed_keys_only": False}
    if not isinstance(payload, Mapping):
        return {"parse_ok": True, "allowed_keys_only": False}
    top_keys = set(payload)
    required = {
        "artifact_body_schema_version",
        "body_status",
        "synthetic_only_notice",
        "no_oracle_notice",
        "non_proof_notice",
        "safety_summary",
        "count_summary",
    }
    allowed = (
        top_keys.issubset(ALLOWED_BODY_FIELDS)
        and required.issubset(top_keys)
        and not (top_keys & FORBIDDEN_TOP_LEVEL_BODY_KEYS)
        and not _payload_has_forbidden_nested_key(payload)
        and not _payload_has_absolute_path_value(payload)
    )
    return {"parse_ok": True, "allowed_keys_only": allowed}


def _stream_is_body_free(text: str) -> bool:
    lowered = text.lower()
    if any(fragment in lowered for fragment in FORBIDDEN_STREAM_FRAGMENTS):
        return False
    if LOCAL_ABSOLUTE_PATH_PATTERN.search(text):
        return False
    return True


def _load_case_payloads(case_dir: Path) -> dict[str, dict[str, Any]]:
    return {name: _read_json(case_dir / name) for name in REQUIRED_FILES}


def _validate_case_contract(
    payloads: Mapping[str, Mapping[str, Any]],
    case_id: str,
    expected_kind: str,
) -> list[str]:
    errors: list[str] = []
    schema_expectations = {
        CASE_METADATA_FILE: CASE_METADATA_SCHEMA_VERSION,
        ARTIFACT_BODY_REQUEST_FILE: ARTIFACT_BODY_REQUEST_SCHEMA_VERSION,
        ARTIFACT_WRITER_RESULT_POINTER_FILE: ARTIFACT_WRITER_RESULT_POINTER_SCHEMA_VERSION,
        ISOLATED_WRITE_REQUEST_FILE: ISOLATED_WRITE_REQUEST_SCHEMA_VERSION,
        EXPECTED_ISOLATED_WRITE_RESULT_FILE: EXPECTED_ISOLATED_WRITE_RESULT_SCHEMA_VERSION,
    }
    field_expectations = {
        CASE_METADATA_FILE: REQUIRED_CASE_METADATA_FIELDS,
        ISOLATED_WRITE_REQUEST_FILE: REQUIRED_ISOLATED_REQUEST_FIELDS,
        EXPECTED_ISOLATED_WRITE_RESULT_FILE: REQUIRED_EXPECTED_FIELDS,
    }
    for name, payload in payloads.items():
        if not isinstance(payload, Mapping):
            errors.append("malformed_fixture")
            continue
        if payload.get("schema_version") != schema_expectations[name]:
            errors.append("schema_version_unknown")
        if payload.get("case_id") != case_id:
            errors.append("case_id_mismatch")
        for field_name in field_expectations.get(name, ()):
            if field_name not in payload:
                errors.append("missing_required_field")

    metadata = payloads[CASE_METADATA_FILE]
    expected = payloads[EXPECTED_ISOLATED_WRITE_RESULT_FILE]
    if metadata.get("case_kind") != expected_kind:
        errors.append("case_id_mismatch")
    if metadata.get("expected_category") != expected.get("expected_category"):
        errors.append("expected_category_mismatch")
    if expected.get("expected_category") not in EXPECTED_CATEGORY_NAMES:
        errors.append("expected_category_unknown")
    if expected_kind not in {"valid", "invalid"}:
        errors.append("unknown_case_kind")
    if not isinstance(expected.get("expected_reason_codes"), list):
        errors.append("expected_reason_codes_invalid")
    if not isinstance(expected.get("expected_failed_checks"), list):
        errors.append("expected_failed_checks_invalid")
    return sorted(set(errors))


def _execution_matches_expected(
    execution: IsolatedWriteExecutionResult,
    expected: Mapping[str, Any],
) -> bool:
    if execution.category != expected.get("expected_category"):
        return False
    if execution.status != expected.get("expected_status"):
        return False
    if not _exit_code_matches(execution.exit_code, expected):
        return False
    if execution.file_written != bool(expected.get("expected_file_written")):
        return False
    if bool(expected.get("expected_file_parse_ok")) and not execution.file_parse_ok:
        return False
    if bool(expected.get("expected_file_allowed_keys_only")) and not (
        execution.file_allowed_keys_only
    ):
        return False
    if execution.file_cleanup_ok != bool(expected.get("expected_file_cleanup_ok")):
        return False
    if execution.residue_file_count != int(expected.get("expected_residue_file_count", -1)):
        return False
    if execution.stdout_body_free != bool(expected.get("expected_stdout_body_free")):
        return False
    if execution.stderr_body_free != bool(expected.get("expected_stderr_body_free")):
        return False
    if execution.safe_relative_path_only != bool(
        expected.get("expected_safe_relative_path_only")
    ):
        return False
    if execution.manifest_file_written != bool(
        expected.get("expected_manifest_file_written")
    ):
        return False
    if execution.manifest_body_generated != bool(
        expected.get("expected_manifest_body_generated")
    ):
        return False
    if not _reason_codes_match(
        execution.reason_codes,
        _safe_string_list(expected.get("expected_reason_codes")),
    ):
        return False
    return True


def _exit_code_matches(actual: int, expected: Mapping[str, Any]) -> bool:
    expected_category = expected.get("expected_category")
    expected_exit = int(expected.get("expected_exit_code", -1))
    if expected_category == "fail_closed_no_write":
        return actual != 0
    return actual == expected_exit


def _reason_codes_match(actual: list[str], expected: list[str]) -> bool:
    if set(actual) == set(expected):
        return True
    normalized_actual = {REASON_CODE_ALIASES.get(reason, reason) for reason in actual}
    return normalized_actual == set(expected)


def _classify_category(exit_code: int, summary: Mapping[str, str]) -> str:
    artifact_written = _safe_bool(summary.get("artifact_file_written"))
    generation_status = summary.get("generation_status")
    body_status = summary.get("body_status")
    if exit_code == 0 and artifact_written:
        return "pass_written"
    if exit_code == 0:
        return "pass_no_write"
    if exit_code == 2:
        return "usage_error_no_write"
    if generation_status == "fail" or body_status == "fail_closed":
        return "fail_closed_no_write"
    return "input_error"


def _status_from_category(category: str) -> str:
    if category in {"pass_written", "pass_no_write"}:
        return "pass"
    if category == "usage_error_no_write":
        return "usage_error"
    if category == "fail_closed_no_write":
        return "fail_closed"
    return "input_error"


def _safe_relative_summary_only(summary: Mapping[str, str]) -> bool:
    output_path = summary.get("artifact_body_output_path")
    if not output_path or output_path == "none":
        return True
    if LOCAL_ABSOLUTE_PATH_PATTERN.search(output_path):
        return False
    path = PurePosixPath(output_path)
    if path.is_absolute() or ".." in path.parts:
        return False
    return path.parts[:2] == SAFE_ROOT_RELATIVE.parts[:2]


def _parse_human_summary(stdout: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in stdout.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def _precreate_output_file(temp_root: Path, artifact_body_out: str) -> None:
    output_path = _expected_output_file(temp_root, artifact_body_out)
    if output_path is None:
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("synthetic precreated metadata placeholder\n", encoding="utf-8")


def _expected_output_file(temp_root: Path, artifact_body_out: Any) -> Path | None:
    if not isinstance(artifact_body_out, str) or not artifact_body_out:
        return None
    if artifact_body_out.startswith(("/", "~")):
        return None
    path = PurePosixPath(artifact_body_out)
    if ".." in path.parts or "." in path.parts:
        return None
    if any(part.startswith(".") for part in path.parts):
        return None
    if re.match(r"^[A-Za-z]:", artifact_body_out):
        return None
    return temp_root / SAFE_ROOT_RELATIVE / Path(*path.parts)


def _remove_empty_safe_root_dirs(temp_root: Path) -> None:
    safe_root = temp_root / SAFE_ROOT_RELATIVE
    if not safe_root.exists():
        return
    for path in sorted([p for p in safe_root.rglob("*") if p.is_dir()], reverse=True):
        try:
            path.rmdir()
        except OSError:
            pass
    try:
        safe_root.rmdir()
    except OSError:
        pass
    tmp_root = temp_root / "tmp"
    try:
        tmp_root.rmdir()
    except OSError:
        pass


def _safe_root_residue_count(temp_root: Path) -> int:
    safe_root = temp_root / SAFE_ROOT_RELATIVE
    if not safe_root.exists():
        return 0
    return len([path for path in safe_root.rglob("*") if path.is_file()])


def _payload_has_forbidden_nested_key(payload: Any) -> bool:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if key in FORBIDDEN_TOP_LEVEL_BODY_KEYS:
                return True
            if _payload_has_forbidden_nested_key(value):
                return True
    elif isinstance(payload, list):
        return any(_payload_has_forbidden_nested_key(item) for item in payload)
    return False


def _payload_has_absolute_path_value(payload: Any) -> bool:
    if isinstance(payload, str):
        return LOCAL_ABSOLUTE_PATH_PATTERN.search(payload) is not None
    if isinstance(payload, Mapping):
        return any(_payload_has_absolute_path_value(value) for value in payload.values())
    if isinstance(payload, list):
        return any(_payload_has_absolute_path_value(item) for item in payload)
    return False


def _validate_root_shape(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return ["missing_root"]
    if not (root / "valid").is_dir():
        errors.append("missing_valid_dir")
    if not (root / "invalid").is_dir():
        errors.append("missing_invalid_dir")
    if not (root / "README.md").is_file():
        errors.append("missing_readme")
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
    return sorted(set(errors))


def _validate_required_file_shape(case_dir: Path) -> list[str]:
    if not case_dir.is_dir():
        return ["missing_case_dir"]
    found = {path.name for path in case_dir.iterdir() if path.is_file()}
    errors = [name for name in REQUIRED_FILES if name not in found]
    if errors:
        return ["required_file_missing"]
    extra = [
        name
        for name in found
        if name.endswith(".json") and name not in set(REQUIRED_FILES)
    ]
    if extra:
        return ["unexpected_fixture_file"]
    return []


def _case_dirs(root: Path) -> list[Path]:
    cases: list[Path] = []
    for category in ("valid", "invalid"):
        category_dir = root / category
        if category_dir.is_dir():
            cases.extend(path for path in category_dir.iterdir() if path.is_dir())
    return sorted(cases, key=lambda path: f"{path.parent.name}/{path.name}")


def _input_error_result(
    case_id: str,
    expected_kind: str,
    reasons: list[str],
) -> IsolatedWriteCaseResult:
    return IsolatedWriteCaseResult(
        validation_status="input_error",
        expected_category="input_error",
        actual_category="input_error",
        expected_status="input_error",
        case_id=case_id,
        expected_kind=expected_kind,
        matched=False,
        reason_codes=sorted(set(reasons)),
        failed_checks=sorted(set(reasons)),
        actual_file_written=False,
        file_parse_ok=False,
        file_allowed_keys_only=False,
    )


def _safe_case_error_payload(
    reason_code: str,
    *,
    case_id: str = "unsafe_fixture_case_selector",
) -> dict[str, Any]:
    return {
        "mode": "isolated_write_fixture_case",
        "validation_schema_version": VALIDATION_SCHEMA_VERSION,
        "case_id": case_id,
        "expected_kind": "none",
        "expected_category": "input_error",
        "actual_category": "input_error",
        "expected_status": "input_error",
        "actual_status": "input_error",
        "matched": False,
        "reason_codes": [reason_code],
        "failed_checks": [reason_code],
        "body_payload_printed": False,
        "stdout_body_free": True,
        "stderr_body_free": True,
        "release_quality_ready": False,
    }


def _is_unsupported_future_write_attempt(reason_codes: list[str]) -> bool:
    return bool(
        {
            "manifest_write_attempt_not_supported",
            "generated_policy_body_write_attempt_not_supported",
        }
        & set(reason_codes)
    )


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("fixture JSON root must be object")
    return payload


def _safe_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _summary_list(value: str | None) -> list[str]:
    if value is None or value == "" or value == "none":
        return []
    return [part for part in value.split(",") if part]


def _safe_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return False


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


if __name__ == "__main__":
    raise SystemExit(main())
