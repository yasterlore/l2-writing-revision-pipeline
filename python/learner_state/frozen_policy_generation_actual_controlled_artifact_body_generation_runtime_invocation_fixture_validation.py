"""Validate actual-controlled artifact body generation runtime invocation fixtures.

This standalone validator checks a synthetic, metadata-only fixture root for a
future controlled runtime invocation boundary. It does not invoke artifact body
generation runtime, call manifest writer code, write files, emit payload bodies,
train models, or compute metrics.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

CASE_METADATA_FILE = "case_metadata.json"
REQUEST_METADATA_FILE = "artifact_body_runtime_request_metadata.json"
POINTER_METADATA_FILE = "artifact_body_runtime_pointer_metadata.json"
CLI_METADATA_FILE = "artifact_body_generation_cli_metadata.json"
EXPECTED_SUMMARY_FILE = "expected_runtime_invocation_summary.json"
RESIDUE_POLICY_FILE = "residue_policy_metadata.json"
EXPECTED_ERROR_FILE = "expected_error.json"

DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled"
)

VALIDATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_runtime_"
    "invocation_actual_controlled_fixture_validation_v0.1"
)
MODE = "artifact_body_generation_runtime_invocation_actual_controlled_fixture_validation"
FIXTURE_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_runtime_"
    "invocation_actual_controlled_fixture_v0.1"
)
FUTURE_RUNTIME_SCHEMA = (
    "learner_state_frozen_policy_generation_artifact_body_generation_runtime_"
    "integration_v0.4"
)
INTEGRATION_MODE = "artifact-body-runtime-invocation-controlled"
UNSUPPORTED_FIXTURE_SCHEMA_VERSION = "unsupported_actual_controlled_fixture_schema_v0"
CONTROLLED_RUNTIME_MODE = "controlled_metadata_only_invocation"

EXPECTED_TOTAL_CASES = 36
EXPECTED_VALID_CASES = 6
EXPECTED_INVALID_CASES = 30
JSON_FILES_PER_CASE = 7
EXPECTED_TOTAL_JSON_FILES = EXPECTED_TOTAL_CASES * JSON_FILES_PER_CASE
EXPECTED_PASS_CASES = 6
EXPECTED_USAGE_ERROR_CASES = 3
EXPECTED_FAIL_CLOSED_CASES = 26
EXPECTED_MISMATCH_CASES = 1
EXPECTED_MISSING_REQUIRED_METADATA_FILE_CASES = 1
EXPECTED_MALFORMED_METADATA_JSON_CASES = 1

REQUIRED_FILES = (
    CASE_METADATA_FILE,
    REQUEST_METADATA_FILE,
    POINTER_METADATA_FILE,
    CLI_METADATA_FILE,
    EXPECTED_SUMMARY_FILE,
    RESIDUE_POLICY_FILE,
    EXPECTED_ERROR_FILE,
)

VALID_CASE_NAMES = frozenset(
    {
        "valid_actual_controlled_safe_metadata_invocation",
        "valid_actual_controlled_cli_output_body_free",
        "valid_actual_controlled_no_file_writing",
        "valid_actual_controlled_no_manifest_writer",
        "valid_actual_controlled_stdout_stderr_suppressed",
        "valid_actual_controlled_no_residue",
    }
)
VALID_CASE_LABELS = frozenset(f"valid/{name}" for name in VALID_CASE_NAMES)

USAGE_ERROR_CASE_NAMES = frozenset(
    {
        "invalid_unsupported_schema",
        "invalid_missing_required_metadata_file",
        "invalid_malformed_metadata_json",
    }
)
MISMATCH_CASE_NAMES = frozenset({"invalid_mismatched_expected_status"})
INVALID_CASE_NAMES = frozenset(
    {
        *USAGE_ERROR_CASE_NAMES,
        *MISMATCH_CASE_NAMES,
        "invalid_request_body_present",
        "invalid_pointer_body_present",
        "invalid_expected_body_present",
        "invalid_artifact_body_payload_present",
        "invalid_manifest_body_present",
        "invalid_generated_policy_body_present",
        "invalid_raw_stdout_body_present",
        "invalid_raw_stderr_body_present",
        "invalid_raw_rows_present",
        "invalid_logits_present",
        "invalid_probabilities_present",
        "invalid_private_path_present",
        "invalid_absolute_path_present",
        "invalid_raw_learner_text_present",
        "invalid_real_data_marker_present",
        "invalid_performance_metric_body_present",
        "invalid_file_writing_requested",
        "invalid_file_writing_detected",
        "invalid_manifest_writer_requested",
        "invalid_manifest_writer_invoked",
        "invalid_unsafe_artifact_body_runtime_mode",
        "invalid_no_oracle_forbidden_field",
        "invalid_unsafe_output_residue_risk",
        "invalid_artifact_body_cli_nonzero_exit",
        "invalid_artifact_body_cli_output_not_body_free",
        "invalid_unexpected_artifact_body_generation_request",
    }
)
INVALID_CASE_LABELS = frozenset(f"invalid/{name}" for name in INVALID_CASE_NAMES)

EXPECTED_INVALID_REASONS = {
    "invalid/invalid_unsupported_schema": "unsupported_schema",
    "invalid/invalid_missing_required_metadata_file": "missing_required_metadata_file",
    "invalid/invalid_malformed_metadata_json": "malformed_metadata_json",
    "invalid/invalid_mismatched_expected_status": "expected_status_mismatch",
    "invalid/invalid_request_body_present": "request_body_present",
    "invalid/invalid_pointer_body_present": "pointer_body_present",
    "invalid/invalid_expected_body_present": "expected_body_present",
    "invalid/invalid_artifact_body_payload_present": "artifact_body_payload_present",
    "invalid/invalid_manifest_body_present": "manifest_body_present",
    "invalid/invalid_generated_policy_body_present": "generated_policy_body_present",
    "invalid/invalid_raw_stdout_body_present": "raw_stdout_body_present",
    "invalid/invalid_raw_stderr_body_present": "raw_stderr_body_present",
    "invalid/invalid_raw_rows_present": "raw_rows_present",
    "invalid/invalid_logits_present": "logits_present",
    "invalid/invalid_probabilities_present": "probabilities_present",
    "invalid/invalid_private_path_present": "private_path_present",
    "invalid/invalid_absolute_path_present": "absolute_path_present",
    "invalid/invalid_raw_learner_text_present": "raw_learner_text_present",
    "invalid/invalid_real_data_marker_present": "real_data_marker_present",
    "invalid/invalid_performance_metric_body_present": "performance_metric_body_present",
    "invalid/invalid_file_writing_requested": "file_writing_requested",
    "invalid/invalid_file_writing_detected": "file_writing_detected",
    "invalid/invalid_manifest_writer_requested": "manifest_writer_requested",
    "invalid/invalid_manifest_writer_invoked": "manifest_writer_invoked",
    "invalid/invalid_unsafe_artifact_body_runtime_mode": "unsafe_artifact_body_runtime_mode",
    "invalid/invalid_no_oracle_forbidden_field": "no_oracle_forbidden_field",
    "invalid/invalid_unsafe_output_residue_risk": "unsafe_output_residue_risk",
    "invalid/invalid_artifact_body_cli_nonzero_exit": "artifact_body_cli_nonzero_exit",
    "invalid/invalid_artifact_body_cli_output_not_body_free": "artifact_body_cli_output_not_body_free",
    "invalid/invalid_unexpected_artifact_body_generation_request": "unexpected_artifact_body_generation_request",
}

EXPECTED_STATUS_BY_CASE = {
    **{f"valid/{name}": "pass" for name in VALID_CASE_NAMES},
    **{f"invalid/{name}": "usage_error" for name in USAGE_ERROR_CASE_NAMES},
    **{f"invalid/{name}": "mismatch" for name in MISMATCH_CASE_NAMES},
    **{
        f"invalid/{name}": "fail_closed"
        for name in INVALID_CASE_NAMES - USAGE_ERROR_CASE_NAMES - MISMATCH_CASE_NAMES
    },
}
EXPECTED_EXIT_CODE_BY_STATUS = {
    "pass": "zero",
    "usage_error": "usage_error",
    "fail_closed": "fail_closed",
    "mismatch": "mismatch",
}

MARKER_FIELDS_BY_REASON: Mapping[str, tuple[tuple[str, str], ...]] = {
    "request_body_present": (
        (EXPECTED_SUMMARY_FILE, "request_body_present_marker"),
        (REQUEST_METADATA_FILE, "request_body_present_marker"),
    ),
    "pointer_body_present": (
        (EXPECTED_SUMMARY_FILE, "pointer_body_present_marker"),
        (POINTER_METADATA_FILE, "pointer_body_present_marker"),
    ),
    "expected_body_present": ((EXPECTED_SUMMARY_FILE, "expected_body_present_marker"),),
    "artifact_body_payload_present": (
        (EXPECTED_SUMMARY_FILE, "artifact_body_payload_present_marker"),
        (CLI_METADATA_FILE, "artifact_body_payload_present_marker"),
    ),
    "manifest_body_present": ((EXPECTED_SUMMARY_FILE, "manifest_body_present_marker"),),
    "generated_policy_body_present": (
        (EXPECTED_SUMMARY_FILE, "generated_policy_body_present_marker"),
    ),
    "raw_stdout_body_present": (
        (EXPECTED_SUMMARY_FILE, "raw_stdout_body_present_marker"),
        (CLI_METADATA_FILE, "raw_stdout_body_present_marker"),
    ),
    "raw_stderr_body_present": (
        (EXPECTED_SUMMARY_FILE, "raw_stderr_body_present_marker"),
        (CLI_METADATA_FILE, "raw_stderr_body_present_marker"),
    ),
    "raw_rows_present": ((EXPECTED_SUMMARY_FILE, "raw_rows_present_marker"),),
    "logits_present": ((EXPECTED_SUMMARY_FILE, "logits_present_marker"),),
    "probabilities_present": ((EXPECTED_SUMMARY_FILE, "probabilities_present_marker"),),
    "private_path_present": ((EXPECTED_SUMMARY_FILE, "private_path_present_marker"),),
    "absolute_path_present": ((EXPECTED_SUMMARY_FILE, "absolute_path_present_marker"),),
    "raw_learner_text_present": (
        (EXPECTED_SUMMARY_FILE, "raw_learner_text_present_marker"),
    ),
    "real_data_marker_present": ((EXPECTED_SUMMARY_FILE, "real_data_marker_present"),),
    "performance_metric_body_present": (
        (EXPECTED_SUMMARY_FILE, "performance_metric_body_present_marker"),
    ),
    "file_writing_requested": (
        (EXPECTED_SUMMARY_FILE, "file_writing_requested_marker"),
        (RESIDUE_POLICY_FILE, "file_writing_requested_marker"),
    ),
    "file_writing_detected": (
        (EXPECTED_SUMMARY_FILE, "file_writing_detected_marker"),
        (RESIDUE_POLICY_FILE, "file_writing_detected"),
    ),
    "manifest_writer_requested": (
        (EXPECTED_SUMMARY_FILE, "manifest_writer_requested_marker"),
        (RESIDUE_POLICY_FILE, "manifest_writer_requested_marker"),
    ),
    "manifest_writer_invoked": (
        (EXPECTED_SUMMARY_FILE, "manifest_writer_invoked_marker"),
        (RESIDUE_POLICY_FILE, "manifest_writer_invoked"),
    ),
    "unsafe_artifact_body_runtime_mode": (
        (EXPECTED_SUMMARY_FILE, "unsafe_artifact_body_runtime_mode_marker"),
    ),
    "no_oracle_forbidden_field": (
        (EXPECTED_SUMMARY_FILE, "no_oracle_forbidden_field_marker"),
    ),
    "unsafe_output_residue_risk": (
        (EXPECTED_SUMMARY_FILE, "unsafe_output_residue_risk_marker"),
        (RESIDUE_POLICY_FILE, "unsafe_output_residue_risk_marker"),
    ),
    "artifact_body_cli_nonzero_exit": (
        (EXPECTED_SUMMARY_FILE, "artifact_body_generation_cli_exit_code_category"),
        (CLI_METADATA_FILE, "artifact_body_generation_cli_exit_code_category"),
    ),
    "artifact_body_cli_output_not_body_free": (
        (EXPECTED_SUMMARY_FILE, "artifact_body_cli_output_not_body_free_marker"),
        (CLI_METADATA_FILE, "artifact_body_cli_output_not_body_free_marker"),
    ),
    "unexpected_artifact_body_generation_request": (
        (EXPECTED_SUMMARY_FILE, "unexpected_artifact_body_generation_request_marker"),
        (REQUEST_METADATA_FILE, "unexpected_artifact_body_generation_request_marker"),
    ),
}

RAW_VALUE_KEYS = frozenset(
    {
        "fixture_json_body",
        "request_body",
        "pointer_body",
        "expected_body",
        "written_file_json_body",
        "manifest_body",
        "artifact_body_payload",
        "generated_policy_body",
        "raw_stdout_body",
        "raw_stderr_body",
        "raw_rows",
        "logits",
        "probabilities",
        "private_path",
        "absolute_path",
        "participant_data",
        "performance_metric_body",
    }
)
FORBIDDEN_KEY_SUFFIXES = ("_body_value", "_payload_value", "_path_value")
LOCAL_ABSOLUTE_PATH_PATTERN = re.compile(
    r"(^|[=\s\"'])/(Users|home|private|var|tmp)/|[A-Za-z]:\\|file://|\\Users\\"
)


@dataclass(frozen=True)
class ActualControlledFixtureCaseResult:
    case_id: str
    case_kind: str
    expected_status: str
    expected_reason_code: str
    expected_exit_code_category: str
    matched: bool
    input_error: bool
    mismatch_reasons: tuple[str, ...] = ()

    @property
    def is_mismatch(self) -> bool:
        return (not self.matched) and (not self.input_error)


@dataclass
class ActualControlledFixtureValidationSummary:
    case_results: list[ActualControlledFixtureCaseResult] = field(default_factory=list)
    reason_code_counts: Counter[str] = field(default_factory=Counter)
    root_errors: tuple[str, ...] = ()
    actual_json_files: int = 0
    physical_missing_required_file_cases: int = 0
    physical_malformed_json_cases: int = 0
    unexpected_json_file_cases: int = 0
    duplicate_case_id_cases: int = 0

    @property
    def total_cases(self) -> int:
        return len(self.case_results)

    @property
    def valid_cases(self) -> int:
        return sum(result.case_kind == "valid" for result in self.case_results)

    @property
    def invalid_cases(self) -> int:
        return sum(result.case_kind == "invalid" for result in self.case_results)

    @property
    def matched_cases(self) -> int:
        return sum(result.matched for result in self.case_results)

    @property
    def mismatched_cases(self) -> int:
        return sum(result.is_mismatch for result in self.case_results)

    @property
    def input_error_cases(self) -> int:
        return sum(result.input_error for result in self.case_results)

    @property
    def pass_cases(self) -> int:
        return sum(result.expected_status == "pass" for result in self.case_results)

    @property
    def usage_error_cases(self) -> int:
        return sum(result.expected_status == "usage_error" for result in self.case_results)

    @property
    def fail_closed_cases(self) -> int:
        return sum(result.expected_status == "fail_closed" for result in self.case_results)

    @property
    def mismatch_cases(self) -> int:
        return sum(result.expected_status == "mismatch" for result in self.case_results)

    @property
    def all_matched(self) -> bool:
        return (
            not self.root_errors
            and self.total_cases == EXPECTED_TOTAL_CASES
            and self.matched_cases == self.total_cases
            and self.input_error_cases == 0
            and self.mismatched_cases == 0
        )


def discover_fixture_cases(root: Path) -> list[Path]:
    case_dirs: list[Path] = []
    for group in ("valid", "invalid"):
        group_dir = root / group
        if group_dir.is_dir():
            case_dirs.extend(path for path in group_dir.iterdir() if path.is_dir())
    return sorted(case_dirs)


def validate_actual_controlled_fixture_root(
    fixture_root: str | Path = DEFAULT_FIXTURE_ROOT,
) -> ActualControlledFixtureValidationSummary:
    root = Path(fixture_root)
    if not root.is_dir():
        return ActualControlledFixtureValidationSummary(root_errors=("fixture_root_missing",))

    case_dirs = discover_fixture_cases(root)
    actual_json_files = len(list(root.rglob("*.json")))
    root_errors = _root_errors(root, case_dirs, actual_json_files)

    results: list[ActualControlledFixtureCaseResult] = []
    reason_counts: Counter[str] = Counter()
    physical_missing = 0
    physical_malformed = 0
    unexpected_json = 0
    duplicate_cases = _duplicate_case_id_labels(case_dirs)

    for case_dir in case_dirs:
        physical_error = _required_file_error(case_dir)
        if physical_error == "missing_required_metadata_file":
            physical_missing += 1
        if physical_error == "unexpected_json_file":
            unexpected_json += 1
        result = validate_actual_controlled_fixture_case(case_dir, duplicate_cases)
        if "malformed_json" in result.mismatch_reasons:
            physical_malformed += 1
        results.append(result)
        reason_counts.update([result.expected_reason_code])

    return ActualControlledFixtureValidationSummary(
        case_results=results,
        reason_code_counts=reason_counts,
        root_errors=tuple(root_errors),
        actual_json_files=actual_json_files,
        physical_missing_required_file_cases=physical_missing,
        physical_malformed_json_cases=physical_malformed,
        unexpected_json_file_cases=unexpected_json,
        duplicate_case_id_cases=len(duplicate_cases),
    )


def validate_actual_controlled_fixture_case(
    case_dir: str | Path,
    duplicate_case_ids: frozenset[str] = frozenset(),
) -> ActualControlledFixtureCaseResult:
    path = Path(case_dir)
    case_id = _case_id_from_dir(path)
    case_kind = path.parent.name if path.parent.name in {"valid", "invalid"} else "unknown"

    file_error = _required_file_error(path)
    if file_error:
        return _case_input_error(path, file_error)

    try:
        payloads = {file_name: _load_json(path / file_name) for file_name in REQUIRED_FILES}
    except (OSError, json.JSONDecodeError):
        return _case_input_error(path, "malformed_json")

    case_metadata_id = _str_field(payloads[CASE_METADATA_FILE], "case_id")
    if not case_metadata_id or case_metadata_id != case_id:
        return _case_input_error(path, "case_id_mismatch")
    if case_metadata_id in duplicate_case_ids:
        return _case_input_error(path, "duplicate_case_id")

    expected_status, expected_reason, expected_exit = _expected_result_for_case(case_id)
    mismatches = _case_mismatch_reasons(
        path, payloads, expected_status, expected_reason, expected_exit
    )
    return ActualControlledFixtureCaseResult(
        case_id=case_id,
        case_kind=case_kind,
        expected_status=expected_status,
        expected_reason_code=expected_reason,
        expected_exit_code_category=expected_exit,
        matched=not mismatches,
        input_error=False,
        mismatch_reasons=tuple(mismatches),
    )


def summarize_actual_controlled_fixture_validation(
    summary: ActualControlledFixtureValidationSummary,
    *,
    fixture_root: str | Path = DEFAULT_FIXTURE_ROOT,
) -> dict[str, Any]:
    root = Path(fixture_root)
    return {
        "mode": MODE,
        "validation_schema_version": VALIDATION_SCHEMA_VERSION,
        "fixture_root": _public_root_label(root),
        "total_cases": summary.total_cases,
        "valid_cases": summary.valid_cases,
        "invalid_cases": summary.invalid_cases,
        "total_json_files": summary.actual_json_files,
        "json_files_per_case": JSON_FILES_PER_CASE,
        "matched_cases": summary.matched_cases,
        "mismatched_cases": summary.mismatched_cases,
        "input_error_cases": summary.input_error_cases,
        "pass_cases": summary.pass_cases,
        "usage_error_cases": summary.usage_error_cases,
        "fail_closed_cases": summary.fail_closed_cases,
        "mismatch_cases": summary.mismatch_cases,
        "expected_missing_required_metadata_file_cases": (
            EXPECTED_MISSING_REQUIRED_METADATA_FILE_CASES
        ),
        "expected_malformed_metadata_json_cases": EXPECTED_MALFORMED_METADATA_JSON_CASES,
        "physical_missing_required_file_cases": summary.physical_missing_required_file_cases,
        "physical_malformed_json_cases": summary.physical_malformed_json_cases,
        "content_suppressed": True,
        "body_suppressed": True,
        "metadata_only_checked": True,
        "synthetic_only_checked": True,
        "no_oracle_checked": True,
        "no_request_body": True,
        "no_pointer_body": True,
        "no_expected_body": True,
        "no_artifact_body_payload": True,
        "no_manifest_body": True,
        "no_generated_policy_body": True,
        "no_raw_stdout_body": True,
        "no_raw_stderr_body": True,
        "no_raw_rows": True,
        "no_logits_dump": True,
        "no_probabilities_dump": True,
        "no_private_paths": True,
        "no_absolute_paths": True,
        "no_raw_learner_text": True,
        "no_real_participant_data": True,
        "no_performance_metric_body": True,
        "file_writing_checked": True,
        "manifest_writer_integration_checked": True,
        "actual_controlled_runtime_invocation_checked": True,
        "production_readiness_claimed": False,
        "real_data_readiness_claimed": False,
        "performance_claims_present": False,
        "reason_code_counts": dict(sorted(summary.reason_code_counts.items())),
        "root_errors": list(summary.root_errors),
    }


def print_public_summary(payload: Mapping[str, Any]) -> None:
    for key, value in payload.items():
        if isinstance(value, bool):
            rendered = str(value).lower()
        elif isinstance(value, (dict, list)):
            rendered = json.dumps(value, sort_keys=True)
        else:
            rendered = str(value)
        print(f"{key}={rendered}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate actual-controlled runtime invocation fixtures."
    )
    parser.add_argument("--fixture-root", default=str(DEFAULT_FIXTURE_ROOT))
    args = parser.parse_args(argv)

    summary = validate_actual_controlled_fixture_root(args.fixture_root)
    payload = summarize_actual_controlled_fixture_validation(
        summary, fixture_root=args.fixture_root
    )
    print_public_summary(payload)
    return 0 if summary.all_matched else 1


def _root_errors(root: Path, case_dirs: list[Path], actual_json_files: int) -> list[str]:
    errors: list[str] = []
    child_dirs = sorted(path.name for path in root.iterdir() if path.is_dir())
    if child_dirs != ["invalid", "valid"]:
        errors.append("unexpected_root_layout")
    if any(path.suffix == ".json" for path in root.iterdir() if path.is_file()):
        errors.append("unexpected_top_level_json_file")
    if not (root / "README.md").is_file():
        errors.append("root_readme_missing")
    case_labels = {_case_id_from_dir(path) for path in case_dirs}
    if case_labels != VALID_CASE_LABELS | INVALID_CASE_LABELS:
        errors.append("case_taxonomy_mismatch")
    if len(case_dirs) != EXPECTED_TOTAL_CASES:
        errors.append("total_cases_mismatch")
    if sum(path.parent.name == "valid" for path in case_dirs) != EXPECTED_VALID_CASES:
        errors.append("valid_cases_mismatch")
    if sum(path.parent.name == "invalid" for path in case_dirs) != EXPECTED_INVALID_CASES:
        errors.append("invalid_cases_mismatch")
    if actual_json_files != EXPECTED_TOTAL_JSON_FILES:
        errors.append("total_json_files_mismatch")
    if _duplicate_case_id_labels(case_dirs):
        errors.append("duplicate_case_id")
    return errors


def _required_file_error(case_dir: Path) -> str | None:
    json_names = sorted(path.name for path in case_dir.glob("*.json"))
    required_names = sorted(REQUIRED_FILES)
    if any(name not in json_names for name in required_names):
        return "missing_required_metadata_file"
    if json_names != required_names:
        return "unexpected_json_file"
    return None


def _duplicate_case_id_labels(case_dirs: list[Path]) -> frozenset[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for case_dir in case_dirs:
        metadata = case_dir / CASE_METADATA_FILE
        if not metadata.is_file():
            continue
        try:
            payload = _load_json(metadata)
        except (OSError, json.JSONDecodeError):
            continue
        case_id = _str_field(payload, "case_id")
        if not case_id:
            continue
        if case_id in seen:
            duplicates.add(case_id)
        seen.add(case_id)
    return frozenset(duplicates)


def _case_input_error(case_dir: Path, reason: str) -> ActualControlledFixtureCaseResult:
    return ActualControlledFixtureCaseResult(
        case_id=_case_id_from_dir(case_dir),
        case_kind=case_dir.parent.name if case_dir.parent.name in {"valid", "invalid"} else "unknown",
        expected_status="usage_error",
        expected_reason_code=reason,
        expected_exit_code_category="usage_error",
        matched=False,
        input_error=True,
        mismatch_reasons=(reason,),
    )


def _case_mismatch_reasons(
    case_dir: Path,
    payloads: Mapping[str, Mapping[str, Any]],
    expected_status: str,
    expected_reason: str,
    expected_exit: str,
) -> list[str]:
    case_id = _case_id_from_dir(case_dir)
    case_kind = case_dir.parent.name
    mismatches: list[str] = []

    if case_kind not in {"valid", "invalid"}:
        mismatches.append("unexpected_case_kind")
    if case_kind == "valid" and case_id not in VALID_CASE_LABELS:
        mismatches.append("unexpected_valid_case")
    if case_kind == "invalid" and EXPECTED_INVALID_REASONS.get(case_id) != expected_reason:
        mismatches.append("unexpected_invalid_reason")

    for file_name, payload in payloads.items():
        if "case_id" in payload and _str_field(payload, "case_id") != case_id:
            mismatches.append(f"{file_name}:case_id_mismatch")
        if _str_field(payloads[CASE_METADATA_FILE], "case_group") != case_kind:
            mismatches.append(f"{CASE_METADATA_FILE}:case_group")

    mismatches.extend(_schema_mismatches(payloads, expected_reason))
    mismatches.extend(
        _expected_result_mismatches(payloads, expected_status, expected_reason, expected_exit)
    )
    mismatches.extend(_runtime_boundary_mismatches(payloads, expected_status, expected_reason))
    mismatches.extend(_marker_mismatches(payloads, expected_reason))
    unsafe_value_reason = _unsafe_value_reason(payloads)
    if unsafe_value_reason:
        mismatches.append(unsafe_value_reason)
    return mismatches


def _schema_mismatches(
    payloads: Mapping[str, Mapping[str, Any]], expected_reason: str
) -> list[str]:
    mismatches: list[str] = []
    metadata = payloads[CASE_METADATA_FILE]
    schema = _str_field(metadata, "fixture_schema_version")
    if expected_reason == "unsupported_schema" and schema != FIXTURE_SCHEMA_VERSION:
        pass
    elif schema != FIXTURE_SCHEMA_VERSION:
        mismatches.append(f"{CASE_METADATA_FILE}:fixture_schema_version")
    if _str_field(metadata, "validation_schema_version") != VALIDATION_SCHEMA_VERSION:
        mismatches.append(f"{CASE_METADATA_FILE}:validation_schema_version")
    if _str_field(metadata, "future_runtime_schema") != FUTURE_RUNTIME_SCHEMA:
        mismatches.append(f"{CASE_METADATA_FILE}:future_runtime_schema")
    if _str_field(metadata, "future_integration_mode") != INTEGRATION_MODE:
        mismatches.append(f"{CASE_METADATA_FILE}:future_integration_mode")

    summary = payloads[EXPECTED_SUMMARY_FILE]
    if _str_field(summary, "runtime_schema_version") != FUTURE_RUNTIME_SCHEMA:
        mismatches.append(f"{EXPECTED_SUMMARY_FILE}:runtime_schema_version")
    if _str_field(summary, "integration_mode") != INTEGRATION_MODE:
        mismatches.append(f"{EXPECTED_SUMMARY_FILE}:integration_mode")
    return mismatches


def _expected_result_mismatches(
    payloads: Mapping[str, Mapping[str, Any]],
    expected_status: str,
    expected_reason: str,
    expected_exit: str,
) -> list[str]:
    mismatches: list[str] = []
    metadata = payloads[CASE_METADATA_FILE]
    expected_error = payloads[EXPECTED_ERROR_FILE]
    summary = payloads[EXPECTED_SUMMARY_FILE]
    for file_name, payload in (
        (CASE_METADATA_FILE, metadata),
        (EXPECTED_ERROR_FILE, expected_error),
    ):
        if _str_field(payload, "expected_status") != expected_status:
            mismatches.append(f"{file_name}:expected_status")
        if _str_field(payload, "expected_reason_code") != expected_reason:
            mismatches.append(f"{file_name}:expected_reason_code")
    if _str_field(metadata, "expected_exit_code_category") != expected_exit:
        mismatches.append(f"{CASE_METADATA_FILE}:expected_exit_code_category")
    expected_error_class = "none" if expected_status == "pass" else expected_status
    if _str_field(expected_error, "expected_error_class") != expected_error_class:
        mismatches.append(f"{EXPECTED_ERROR_FILE}:expected_error_class")
    if expected_status == "pass" and expected_error.get("error_expected") is not False:
        mismatches.append(f"{EXPECTED_ERROR_FILE}:error_expected")
    if expected_status != "pass" and expected_error.get("error_expected") is not True:
        mismatches.append(f"{EXPECTED_ERROR_FILE}:error_expected")
    if expected_reason == "expected_status_mismatch":
        if summary.get("mismatched_expected_status_marker") is not True:
            mismatches.append(f"{EXPECTED_SUMMARY_FILE}:mismatched_expected_status_marker")
    else:
        if _str_field(summary, "status") != expected_status:
            mismatches.append(f"{EXPECTED_SUMMARY_FILE}:status")
        if _str_field(summary, "reason_code") != expected_reason:
            mismatches.append(f"{EXPECTED_SUMMARY_FILE}:reason_code")
    if _str_field(summary, "exit_code_category") != expected_exit:
        mismatches.append(f"{EXPECTED_SUMMARY_FILE}:exit_code_category")
    return mismatches


def _runtime_boundary_mismatches(
    payloads: Mapping[str, Mapping[str, Any]],
    expected_status: str,
    expected_reason: str,
) -> list[str]:
    mismatches: list[str] = []
    metadata = payloads[CASE_METADATA_FILE]
    summary = payloads[EXPECTED_SUMMARY_FILE]
    cli = payloads[CLI_METADATA_FILE]
    residue = payloads[RESIDUE_POLICY_FILE]

    if metadata.get("actual_runtime_invocation_performed") is not False:
        mismatches.append(f"{CASE_METADATA_FILE}:actual_runtime_invocation_performed")
    if metadata.get("runtime_implementation_changed") is not False:
        mismatches.append(f"{CASE_METADATA_FILE}:runtime_implementation_changed")
    if metadata.get("validator_implemented") is not False:
        mismatches.append(f"{CASE_METADATA_FILE}:validator_implemented")
    if metadata.get("manifest_writer_integrated") is not False:
        mismatches.append(f"{CASE_METADATA_FILE}:manifest_writer_integrated")
    if metadata.get("file_writing_performed") is not False:
        mismatches.append(f"{CASE_METADATA_FILE}:file_writing_performed")

    if summary.get("artifact_body_runtime_invocation_planned") is not False:
        mismatches.append(f"{EXPECTED_SUMMARY_FILE}:artifact_body_runtime_invocation_planned")
    if expected_status == "usage_error":
        expected_runtime_invoked = False
        expected_cli_invoked = False
    else:
        expected_runtime_invoked = True
        expected_cli_invoked = True
    if summary.get("artifact_body_runtime_invoked") is not expected_runtime_invoked:
        mismatches.append(f"{EXPECTED_SUMMARY_FILE}:artifact_body_runtime_invoked")
    if expected_status != "fail_closed" or expected_reason != "unsafe_artifact_body_runtime_mode":
        if _str_field(summary, "artifact_body_runtime_mode") != CONTROLLED_RUNTIME_MODE:
            mismatches.append(f"{EXPECTED_SUMMARY_FILE}:artifact_body_runtime_mode")
    if summary.get("artifact_body_generation_cli_invoked") is not expected_cli_invoked:
        mismatches.append(f"{EXPECTED_SUMMARY_FILE}:artifact_body_generation_cli_invoked")
    if cli.get("artifact_body_generation_cli_invoked") is not expected_cli_invoked:
        mismatches.append(f"{CLI_METADATA_FILE}:artifact_body_generation_cli_invoked")

    if expected_status == "pass":
        pass_invariants = (
            (summary, EXPECTED_SUMMARY_FILE, "artifact_body_generation_cli_output_body_free", True),
            (summary, EXPECTED_SUMMARY_FILE, "manifest_writer_invoked", False),
            (summary, EXPECTED_SUMMARY_FILE, "file_writing_enabled", False),
            (summary, EXPECTED_SUMMARY_FILE, "file_writing_detected", False),
            (summary, EXPECTED_SUMMARY_FILE, "residue_file_count", 0),
            (summary, EXPECTED_SUMMARY_FILE, "unsafe_signal_count", 0),
            (cli, CLI_METADATA_FILE, "artifact_body_generation_cli_output_body_free", True),
            (residue, RESIDUE_POLICY_FILE, "residue_file_count", 0),
            (residue, RESIDUE_POLICY_FILE, "file_writing_enabled", False),
            (residue, RESIDUE_POLICY_FILE, "file_writing_detected", False),
            (residue, RESIDUE_POLICY_FILE, "manifest_writer_invoked", False),
        )
        for payload, file_name, key, expected_value in pass_invariants:
            if payload.get(key) != expected_value:
                mismatches.append(f"{file_name}:{key}")
    return mismatches


def _marker_mismatches(
    payloads: Mapping[str, Mapping[str, Any]], expected_reason: str
) -> list[str]:
    mismatches: list[str] = []
    expected_count = 0 if expected_reason in {"none", "artifact_body_cli_nonzero_exit"} else 1
    summary = payloads[EXPECTED_SUMMARY_FILE]
    metadata = payloads[CASE_METADATA_FILE]
    if _int_field(summary, "unsafe_signal_count") != expected_count:
        mismatches.append(f"{EXPECTED_SUMMARY_FILE}:unsafe_signal_count")
    if expected_reason == "missing_required_metadata_file":
        if metadata.get("required_metadata_file_missing_marker") is not True:
            mismatches.append("missing_required_metadata_file_marker_missing")
        if summary.get("required_metadata_file_missing_marker") is not True:
            mismatches.append("missing_required_metadata_file_summary_marker_missing")
    if expected_reason == "malformed_metadata_json":
        if metadata.get("malformed_metadata_json_marker") is not True:
            mismatches.append("malformed_metadata_json_marker_missing")
        if summary.get("malformed_metadata_json_marker") is not True:
            mismatches.append("malformed_metadata_json_summary_marker_missing")
    if expected_reason == "unsupported_schema" and metadata.get("unsupported_schema_marker") is not True:
        mismatches.append("unsupported_schema_marker_missing")
    if expected_reason == "expected_status_mismatch" and metadata.get(
        "mismatched_expected_status_marker"
    ) is not True:
        mismatches.append("mismatched_expected_status_marker_missing")
    if expected_reason == "none":
        return mismatches

    marker_fields = MARKER_FIELDS_BY_REASON.get(expected_reason, ())
    if marker_fields:
        if not any(_marker_is_set(payloads[file_name], field_name) for file_name, field_name in marker_fields):
            mismatches.append(f"{expected_reason}:marker_missing")
    return mismatches


def _marker_is_set(payload: Mapping[str, Any], field_name: str) -> bool:
    value = payload.get(field_name)
    if isinstance(value, bool):
        return value is True
    if isinstance(value, str):
        return value not in {"", "zero", "none"}
    return False


def _expected_result_for_case(case_id: str) -> tuple[str, str, str]:
    status = EXPECTED_STATUS_BY_CASE.get(case_id, "usage_error")
    reason = "none" if case_id.startswith("valid/") else EXPECTED_INVALID_REASONS.get(case_id, "unknown_case")
    if reason == "artifact_body_cli_nonzero_exit":
        exit_code = "nonzero"
    elif status == "usage_error":
        exit_code = "not_applicable"
    else:
        exit_code = "zero"
    return status, reason, exit_code


def _unsafe_value_reason(payloads: Mapping[str, Mapping[str, Any]]) -> str | None:
    def walk(value: Any) -> str | None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                if key in RAW_VALUE_KEYS or key.endswith(FORBIDDEN_KEY_SUFFIXES):
                    return "unsafe_output_surface"
                reason = walk(child)
                if reason:
                    return reason
        elif isinstance(value, list):
            for child in value:
                reason = walk(child)
                if reason:
                    return reason
        elif isinstance(value, str) and LOCAL_ABSOLUTE_PATH_PATTERN.search(value):
            return "unsafe_output_surface"
        return None

    for payload in payloads.values():
        reason = walk(payload)
        if reason:
            return reason
    return None


def _load_json(path: Path) -> Mapping[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, Mapping):
        raise json.JSONDecodeError("expected object", doc="", pos=0)
    return data


def _case_id_from_dir(case_dir: Path) -> str:
    return f"{case_dir.parent.name}/{case_dir.name}"


def _str_field(payload: Mapping[str, Any], key: str, default: str = "") -> str:
    value = payload.get(key, default)
    return value if isinstance(value, str) else default


def _int_field(payload: Mapping[str, Any], key: str) -> int:
    value = payload.get(key, 0)
    return value if isinstance(value, int) else 0


def _public_root_label(root: Path) -> str:
    if root.is_absolute():
        try:
            return str(root.relative_to(Path.cwd()))
        except ValueError:
            return root.name
    return str(root)


if __name__ == "__main__":
    sys.exit(main())
