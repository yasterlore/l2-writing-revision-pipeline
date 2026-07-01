"""Static validation for artifact body generation integration fixtures.

This validator checks synthetic metadata-only fixture contracts. It does not
invoke runtime code, generate artifact bodies, call manifest writer code, write
files, train models, or compute metrics.
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
RUNTIME_SUMMARY_FILE = "actual_invocation_runtime_summary_metadata.json"
REQUEST_METADATA_FILE = "artifact_body_request_metadata.json"
POINTER_METADATA_FILE = "artifact_body_pointer_metadata.json"
GENERATION_METADATA_FILE = "artifact_body_generation_metadata.json"
EXPECTED_SUMMARY_FILE = "expected_integration_summary.json"
EXPECTED_ERROR_FILE = "expected_error.json"

DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_body_generation_integration"
)

VALIDATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_integration_"
    "fixture_validation_v0.1"
)
MODE = "artifact_body_generation_integration_fixture_validation"

CASE_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_integration_"
    "case_v0.1"
)
RUNTIME_SUMMARY_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_integration_"
    "runtime_summary_metadata_v0.1"
)
REQUEST_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_integration_"
    "request_metadata_v0.1"
)
POINTER_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_integration_"
    "pointer_metadata_v0.1"
)
GENERATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_integration_"
    "generation_metadata_v0.1"
)
EXPECTED_SUMMARY_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_integration_"
    "expected_summary_v0.1"
)
EXPECTED_ERROR_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_integration_"
    "expected_error_v0.1"
)
RUNTIME_RESULT_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_"
    "runtime_v0.2"
)
UNSUPPORTED_RUNTIME_SUMMARY_SCHEMA_SENTINEL = (
    "unsupported_runtime_summary_metadata_schema_v0.0"
)

EXPECTED_TOTAL_CASES = 28
EXPECTED_VALID_CASES = 6
EXPECTED_INVALID_CASES = 22
JSON_FILES_PER_CASE = 7
EXPECTED_TOTAL_JSON_FILES = EXPECTED_TOTAL_CASES * JSON_FILES_PER_CASE
EXPECTED_PASS_CASES = 6
EXPECTED_USAGE_ERROR_CASES = 1
EXPECTED_FAIL_CLOSED_CASES = 20
EXPECTED_MISMATCH_CASES = 1

REQUIRED_FILES = (
    CASE_METADATA_FILE,
    RUNTIME_SUMMARY_FILE,
    REQUEST_METADATA_FILE,
    POINTER_METADATA_FILE,
    GENERATION_METADATA_FILE,
    EXPECTED_SUMMARY_FILE,
    EXPECTED_ERROR_FILE,
)

EXPECTED_FILE_SCHEMAS = {
    CASE_METADATA_FILE: CASE_SCHEMA_VERSION,
    RUNTIME_SUMMARY_FILE: RUNTIME_SUMMARY_SCHEMA_VERSION,
    REQUEST_METADATA_FILE: REQUEST_SCHEMA_VERSION,
    POINTER_METADATA_FILE: POINTER_SCHEMA_VERSION,
    GENERATION_METADATA_FILE: GENERATION_SCHEMA_VERSION,
    EXPECTED_SUMMARY_FILE: EXPECTED_SUMMARY_SCHEMA_VERSION,
    EXPECTED_ERROR_FILE: EXPECTED_ERROR_SCHEMA_VERSION,
}

VALID_CASE_LABELS = frozenset(
    {
        "valid/valid_minimal_suppressed_metadata_only_bridge",
        "valid/valid_safe_metadata_summary_bridge",
        "valid/valid_runtime_summary_to_suppressed_body_generation",
        "valid/valid_no_file_writing_bridge",
        "valid/valid_no_manifest_writer_bridge",
        "valid/valid_no_downstream_payload_bridge",
    }
)

EXPECTED_INVALID_REASONS = {
    "invalid/invalid_runtime_summary_schema": "runtime_summary_schema",
    "invalid/invalid_runtime_summary_status": "runtime_summary_status",
    "invalid/invalid_runtime_summary_body_detected": (
        "runtime_summary_body_detected"
    ),
    "invalid/invalid_runtime_summary_raw_stdout_body": (
        "runtime_summary_raw_stdout_body"
    ),
    "invalid/invalid_runtime_summary_raw_stderr_body": (
        "runtime_summary_raw_stderr_body"
    ),
    "invalid/invalid_artifact_body_payload_requested": (
        "artifact_body_payload_requested"
    ),
    "invalid/invalid_manifest_body_requested": "manifest_body_requested",
    "invalid/invalid_generated_policy_body_requested": (
        "generated_policy_body_requested"
    ),
    "invalid/invalid_request_body_present": "request_body_present",
    "invalid/invalid_pointer_body_present": "pointer_body_present",
    "invalid/invalid_expected_body_present": "expected_body_present",
    "invalid/invalid_raw_rows_present": "raw_rows_present",
    "invalid/invalid_logits_present": "logits_present",
    "invalid/invalid_private_path_present": "private_path_present",
    "invalid/invalid_absolute_path_present": "absolute_path_present",
    "invalid/invalid_raw_learner_text_present": "raw_learner_text_present",
    "invalid/invalid_file_writing_requested": "file_writing_requested",
    "invalid/invalid_manifest_writer_requested": "manifest_writer_requested",
    "invalid/invalid_artifact_body_generation_unsafe_mode": (
        "artifact_body_generation_unsafe_mode"
    ),
    "invalid/invalid_mismatched_expected_status": "mismatched_expected_status",
    "invalid/invalid_real_data_marker_present": "real_data_marker_present",
    "invalid/invalid_performance_metric_body_present": (
        "performance_metric_body_present"
    ),
}

EXPECTED_REASON_CODE_COUNTS = Counter(
    {"none": EXPECTED_PASS_CASES, **{reason: 1 for reason in EXPECTED_INVALID_REASONS.values()}}
)

EXPECTED_STATUS_BY_REASON = {
    "none": "pass",
    "runtime_summary_schema": "usage_error",
    "mismatched_expected_status": "mismatch",
}
EXPECTED_EXIT_CODE_BY_STATUS = {
    "pass": "zero",
    "usage_error": "usage_error",
    "fail_closed": "fail_closed",
    "mismatch": "mismatch",
}

CASE_METADATA_FIELDS = frozenset(
    {
        "schema_version",
        "case_id",
        "case_kind",
        "description",
        "expected_status",
        "expected_reason_code",
        "synthetic_only",
        "metadata_only",
        "no_oracle",
        "body_free",
        "fixture_contract_version",
    }
)
RUNTIME_SUMMARY_FIELDS = frozenset(
    {
        "schema_version",
        "runtime_schema_version",
        "status",
        "reason_code",
        "exit_code_category",
        "case_id",
        "runtime_source_case_id",
        "invocation_mode",
        "summary_mode",
        "content_suppressed",
        "body_suppressed",
        "runtime_actual_invocation_enabled",
        "artifact_writer_cli_invoked",
        "artifact_writer_cli_output_scanned",
        "artifact_writer_cli_output_body_free",
        "raw_stdout_body_suppressed",
        "raw_stderr_body_suppressed",
        "request_body_detected",
        "pointer_body_detected",
        "expected_body_detected",
        "artifact_body_payload_detected",
        "manifest_body_detected",
        "generated_policy_body_detected",
        "file_writing_detected",
        "artifact_body_generation_invoked",
        "manifest_writer_invoked",
        "file_writing_enabled",
        "production_readiness_claimed",
        "real_data_readiness_claimed",
        "performance_claims_present",
    }
)
REQUEST_METADATA_FIELDS = frozenset(
    {
        "schema_version",
        "request_id",
        "mode",
        "summary_only",
        "no_file_writing",
        "no_manifest_writer",
        "no_payload_output",
        "synthetic_only",
        "metadata_only",
        "no_oracle",
        "request_body_present",
        "artifact_body_payload_requested",
        "manifest_body_requested",
        "generated_policy_body_requested",
        "performance_metric_body_present",
        "real_data_marker_present",
    }
)
POINTER_METADATA_FIELDS = frozenset(
    {
        "schema_version",
        "pointer_id",
        "pointer_kind",
        "fixture_relative_path",
        "metadata_only",
        "synthetic_only",
        "no_oracle",
        "pointer_body_present",
        "private_path_present",
        "absolute_path_present",
        "raw_learner_text_present",
        "raw_rows_present",
        "logits_present",
        "real_data_marker_present",
    }
)
GENERATION_METADATA_FIELDS = frozenset(
    {
        "schema_version",
        "generation_mode",
        "body_status",
        "artifact_body_available",
        "artifact_file_written",
        "manifest_file_written",
        "artifact_body_payload_present",
        "manifest_body_present",
        "generated_policy_body_present",
        "raw_stdout_body_present",
        "raw_stderr_body_present",
        "request_body_present",
        "pointer_body_present",
        "expected_body_present",
        "raw_rows_present",
        "logits_present",
        "private_path_present",
        "absolute_path_present",
        "raw_learner_text_present",
        "real_data_marker_present",
        "performance_metric_body_present",
        "content_suppressed",
        "body_suppressed",
        "safe_summary",
        "validation_status",
        "metadata_field_count",
        "body_field_count",
    }
)
EXPECTED_SUMMARY_FIELDS = frozenset(
    {
        "schema_version",
        "mode",
        "status",
        "reason_code",
        "case_id",
        "integration_mode",
        "runtime_summary_checked",
        "artifact_body_request_checked",
        "artifact_body_pointer_checked",
        "artifact_body_generation_checked",
        "artifact_body_payload_detected",
        "manifest_body_detected",
        "generated_policy_body_detected",
        "request_body_detected",
        "pointer_body_detected",
        "expected_body_detected",
        "raw_stdout_body_detected",
        "raw_stderr_body_detected",
        "file_writing_detected",
        "manifest_writer_invoked",
        "artifact_body_generation_invoked",
        "content_suppressed",
        "body_suppressed",
        "synthetic_only_checked",
        "no_oracle_checked",
        "metadata_only_checked",
        "production_readiness_claimed",
        "real_data_readiness_claimed",
        "performance_claims_present",
    }
)
EXPECTED_ERROR_FIELDS = frozenset(
    {
        "schema_version",
        "expected_status",
        "expected_reason_code",
        "expected_exit_code_category",
        "expected_error_public_safe",
        "body_suppressed",
        "content_suppressed",
        "no_payload_in_error",
    }
)
EXPECTED_FIELD_SETS = {
    CASE_METADATA_FILE: CASE_METADATA_FIELDS,
    RUNTIME_SUMMARY_FILE: RUNTIME_SUMMARY_FIELDS,
    REQUEST_METADATA_FILE: REQUEST_METADATA_FIELDS,
    POINTER_METADATA_FILE: POINTER_METADATA_FIELDS,
    GENERATION_METADATA_FILE: GENERATION_METADATA_FIELDS,
    EXPECTED_SUMMARY_FILE: EXPECTED_SUMMARY_FIELDS,
    EXPECTED_ERROR_FILE: EXPECTED_ERROR_FIELDS,
}
OPTIONAL_FIELD_SETS = {
    RUNTIME_SUMMARY_FILE: frozenset({"expected_status_sentinel"}),
}

BOOL_FALSE_BY_REASON: Mapping[str, tuple[tuple[str, str], ...]] = {
    "runtime_summary_body_detected": (
        (RUNTIME_SUMMARY_FILE, "content_suppressed"),
        (RUNTIME_SUMMARY_FILE, "body_suppressed"),
    ),
    "runtime_summary_raw_stdout_body": (
        (RUNTIME_SUMMARY_FILE, "raw_stdout_body_suppressed"),
    ),
    "runtime_summary_raw_stderr_body": (
        (RUNTIME_SUMMARY_FILE, "raw_stderr_body_suppressed"),
    ),
}

BOOL_TRUE_BY_REASON: Mapping[str, tuple[tuple[str, str], ...]] = {
    "artifact_body_payload_requested": (
        (REQUEST_METADATA_FILE, "artifact_body_payload_requested"),
        (GENERATION_METADATA_FILE, "artifact_body_payload_present"),
    ),
    "manifest_body_requested": (
        (REQUEST_METADATA_FILE, "manifest_body_requested"),
        (GENERATION_METADATA_FILE, "manifest_body_present"),
    ),
    "generated_policy_body_requested": (
        (REQUEST_METADATA_FILE, "generated_policy_body_requested"),
        (GENERATION_METADATA_FILE, "generated_policy_body_present"),
    ),
    "request_body_present": (
        (REQUEST_METADATA_FILE, "request_body_present"),
        (GENERATION_METADATA_FILE, "request_body_present"),
    ),
    "pointer_body_present": (
        (POINTER_METADATA_FILE, "pointer_body_present"),
        (GENERATION_METADATA_FILE, "pointer_body_present"),
    ),
    "expected_body_present": ((GENERATION_METADATA_FILE, "expected_body_present"),),
    "raw_rows_present": (
        (POINTER_METADATA_FILE, "raw_rows_present"),
        (GENERATION_METADATA_FILE, "raw_rows_present"),
    ),
    "logits_present": (
        (POINTER_METADATA_FILE, "logits_present"),
        (GENERATION_METADATA_FILE, "logits_present"),
    ),
    "private_path_present": (
        (POINTER_METADATA_FILE, "private_path_present"),
        (GENERATION_METADATA_FILE, "private_path_present"),
    ),
    "absolute_path_present": (
        (POINTER_METADATA_FILE, "absolute_path_present"),
        (GENERATION_METADATA_FILE, "absolute_path_present"),
    ),
    "raw_learner_text_present": (
        (POINTER_METADATA_FILE, "raw_learner_text_present"),
        (GENERATION_METADATA_FILE, "raw_learner_text_present"),
    ),
    "file_writing_requested": (
        (GENERATION_METADATA_FILE, "artifact_file_written"),
    ),
    "manifest_writer_requested": (
        (GENERATION_METADATA_FILE, "manifest_file_written"),
    ),
    "real_data_marker_present": (
        (REQUEST_METADATA_FILE, "real_data_marker_present"),
        (POINTER_METADATA_FILE, "real_data_marker_present"),
        (GENERATION_METADATA_FILE, "real_data_marker_present"),
    ),
    "performance_metric_body_present": (
        (REQUEST_METADATA_FILE, "performance_metric_body_present"),
        (GENERATION_METADATA_FILE, "performance_metric_body_present"),
    ),
}

SENTINEL_REASON_KEYS = (
    tuple(BOOL_TRUE_BY_REASON.keys())
    + tuple(BOOL_FALSE_BY_REASON.keys())
    + ("artifact_body_generation_unsafe_mode", "runtime_summary_status")
)

FORBIDDEN_VALUE_KEYS = frozenset(
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
        "raw_learner_text",
        "real_participant_data",
        "performance_metric_body",
        "final_text",
        "observed_after_text",
        "gold_label",
        "post_hoc_annotation",
        "scoring_feedback_payload",
    }
)
LOCAL_ABSOLUTE_PATH_PATTERN = re.compile(
    r"(^|[=\s\"'])/(Users|home|private|var|tmp)/|[A-Za-z]:\\|file://|\\Users\\"
)


@dataclass(frozen=True)
class ArtifactBodyGenerationIntegrationFixtureCaseResult:
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

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "case_kind": self.case_kind,
            "expected_status": self.expected_status,
            "expected_reason_code": self.expected_reason_code,
            "expected_exit_code_category": self.expected_exit_code_category,
            "matched": self.matched,
            "input_error": self.input_error,
            "mismatch_reasons": list(self.mismatch_reasons),
        }


@dataclass
class ArtifactBodyGenerationIntegrationFixtureValidationSummary:
    case_results: list[ArtifactBodyGenerationIntegrationFixtureCaseResult] = field(
        default_factory=list
    )
    reason_code_counts: Counter[str] = field(default_factory=Counter)
    root_errors: tuple[str, ...] = ()
    actual_json_files: int = 0
    missing_required_file_cases: int = 0
    unexpected_json_file_cases: int = 0

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
        return sum(
            result.expected_status == "usage_error" for result in self.case_results
        )

    @property
    def fail_closed_cases(self) -> int:
        return sum(
            result.expected_status == "fail_closed" for result in self.case_results
        )

    @property
    def mismatch_cases(self) -> int:
        return sum(result.expected_status == "mismatch" for result in self.case_results)

    @property
    def all_matched(self) -> bool:
        return (
            not self.root_errors
            and self.total_cases > 0
            and self.matched_cases == self.total_cases
            and self.input_error_cases == 0
            and self.mismatched_cases == 0
        )


def discover_artifact_body_generation_integration_fixture_cases(
    root: Path,
) -> list[Path]:
    case_dirs: list[Path] = []
    for group in ("valid", "invalid"):
        group_dir = root / group
        if group_dir.is_dir():
            case_dirs.extend(path for path in group_dir.iterdir() if path.is_dir())
    return sorted(case_dirs)


def validate_artifact_body_generation_integration_fixture_root(
    fixture_root: str | Path = DEFAULT_FIXTURE_ROOT,
) -> ArtifactBodyGenerationIntegrationFixtureValidationSummary:
    root = Path(fixture_root)
    if not root.is_dir():
        return ArtifactBodyGenerationIntegrationFixtureValidationSummary(
            root_errors=("fixture_root_missing",)
        )

    root_errors: list[str] = []
    case_dirs = discover_artifact_body_generation_integration_fixture_cases(root)
    actual_json_files = len(list(root.rglob("*.json")))
    _check_root_counts(root, case_dirs, actual_json_files, root_errors)

    case_results: list[ArtifactBodyGenerationIntegrationFixtureCaseResult] = []
    reason_counts: Counter[str] = Counter()
    missing_required_file_cases = 0
    unexpected_json_file_cases = 0
    for case_dir in case_dirs:
        file_error = _required_file_error(case_dir)
        if file_error == "missing_required_file":
            missing_required_file_cases += 1
        if file_error == "unexpected_json_file":
            unexpected_json_file_cases += 1
        result = validate_artifact_body_generation_integration_fixture_case(case_dir)
        case_results.append(result)
        reason_counts.update([result.expected_reason_code])

    return ArtifactBodyGenerationIntegrationFixtureValidationSummary(
        case_results=case_results,
        reason_code_counts=reason_counts,
        root_errors=tuple(root_errors),
        actual_json_files=actual_json_files,
        missing_required_file_cases=missing_required_file_cases,
        unexpected_json_file_cases=unexpected_json_file_cases,
    )


def validate_artifact_body_generation_integration_fixture_case(
    case_dir: str | Path,
) -> ArtifactBodyGenerationIntegrationFixtureCaseResult:
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

    expected_error = payloads[EXPECTED_ERROR_FILE]
    expected_status = _str_field(expected_error, "expected_status", "input_error")
    expected_reason = _str_field(expected_error, "expected_reason_code", "input_error")
    expected_exit = _str_field(
        expected_error,
        "expected_exit_code_category",
        "input_error",
    )

    mismatches: list[str] = []
    _validate_field_sets(payloads, mismatches)
    _validate_schema_versions(case_id, payloads, mismatches)
    _validate_identity(case_id, case_kind, payloads, mismatches)
    _validate_expected_status_policy(
        case_id,
        case_kind,
        expected_status,
        expected_reason,
        expected_exit,
        payloads,
        mismatches,
    )
    _validate_cross_file_consistency(payloads, mismatches)
    _validate_metadata_policy(case_kind, expected_reason, payloads, mismatches)
    _scan_for_unsafe_values(payloads, mismatches)

    return ArtifactBodyGenerationIntegrationFixtureCaseResult(
        case_id=case_id,
        case_kind=case_kind,
        expected_status=expected_status,
        expected_reason_code=expected_reason,
        expected_exit_code_category=expected_exit,
        matched=not mismatches,
        input_error=False,
        mismatch_reasons=tuple(sorted(set(mismatches))),
    )


def summarize_artifact_body_generation_integration_fixture_validation(
    summary: ArtifactBodyGenerationIntegrationFixtureValidationSummary,
) -> dict[str, Any]:
    return {
        "mode": MODE,
        "validation_schema_version": VALIDATION_SCHEMA_VERSION,
        "fixture_root": str(DEFAULT_FIXTURE_ROOT),
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
        "missing_required_file_cases": summary.missing_required_file_cases,
        "unexpected_json_file_cases": summary.unexpected_json_file_cases,
        "content_suppressed": True,
        "body_suppressed": True,
        "no_raw_rows": True,
        "no_logits_dump": True,
        "no_private_paths": True,
        "no_absolute_paths": True,
        "no_request_body": True,
        "no_pointer_body": True,
        "no_expected_body": True,
        "no_raw_stdout_body": True,
        "no_raw_stderr_body": True,
        "no_artifact_body_payload": True,
        "no_manifest_body": True,
        "no_generated_policy_body": True,
        "synthetic_only_checked": True,
        "no_oracle_checked": True,
        "metadata_only_checked": True,
        "file_writing_checked": True,
        "manifest_writer_integration_checked": True,
        "artifact_body_generation_integration_checked": True,
        "production_readiness_claimed": False,
        "real_data_readiness_claimed": False,
        "performance_claims_present": False,
        "reason_code_counts": dict(sorted(summary.reason_code_counts.items())),
        "root_errors": list(summary.root_errors),
    }


def _check_root_counts(
    root: Path,
    case_dirs: Sequence[Path],
    actual_json_files: int,
    root_errors: list[str],
) -> None:
    if not (root / "valid").is_dir():
        root_errors.append("valid_dir_missing")
    if not (root / "invalid").is_dir():
        root_errors.append("invalid_dir_missing")
    if len(case_dirs) != EXPECTED_TOTAL_CASES:
        root_errors.append("total_case_count_mismatch")
    if sum(path.parent.name == "valid" for path in case_dirs) != EXPECTED_VALID_CASES:
        root_errors.append("valid_case_count_mismatch")
    if sum(path.parent.name == "invalid" for path in case_dirs) != EXPECTED_INVALID_CASES:
        root_errors.append("invalid_case_count_mismatch")
    if actual_json_files != EXPECTED_TOTAL_JSON_FILES:
        root_errors.append("total_json_file_count_mismatch")
    for child in root.iterdir():
        if child.is_dir() and child.name not in {"valid", "invalid"}:
            root_errors.append("unexpected_case_group_directory")


def _required_file_error(case_dir: Path) -> str | None:
    if not case_dir.is_dir():
        return "case_dir_missing"
    json_names = {path.name for path in case_dir.glob("*.json")}
    required = set(REQUIRED_FILES)
    if json_names - required:
        return "unexpected_json_file"
    if required - json_names:
        return "missing_required_file"
    return None


def _case_input_error(
    case_dir: Path,
    reason: str,
) -> ArtifactBodyGenerationIntegrationFixtureCaseResult:
    return ArtifactBodyGenerationIntegrationFixtureCaseResult(
        case_id=_case_id_from_dir(case_dir),
        case_kind=case_dir.parent.name if case_dir.parent.name else "unknown",
        expected_status="input_error",
        expected_reason_code=reason,
        expected_exit_code_category="input_error",
        matched=False,
        input_error=True,
        mismatch_reasons=(reason,),
    )


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise json.JSONDecodeError("fixture root expects JSON objects", "", 0)
    return data


def _case_id_from_dir(path: Path) -> str:
    return f"{path.parent.name}/{path.name}"


def _validate_field_sets(
    payloads: Mapping[str, Mapping[str, Any]],
    mismatches: list[str],
) -> None:
    for file_name, expected_fields in EXPECTED_FIELD_SETS.items():
        optional_fields = OPTIONAL_FIELD_SETS.get(file_name, frozenset())
        fields = set(payloads[file_name])
        missing = expected_fields - fields
        extra = fields - expected_fields - optional_fields
        if missing:
            mismatches.append(f"{file_name}_missing_fields")
        if extra:
            mismatches.append(f"{file_name}_unexpected_fields")


def _validate_schema_versions(
    case_id: str,
    payloads: Mapping[str, Mapping[str, Any]],
    mismatches: list[str],
) -> None:
    for file_name, expected_schema in EXPECTED_FILE_SCHEMAS.items():
        schema = payloads[file_name].get("schema_version")
        if (
            file_name == RUNTIME_SUMMARY_FILE
            and case_id == "invalid/invalid_runtime_summary_schema"
            and schema == UNSUPPORTED_RUNTIME_SUMMARY_SCHEMA_SENTINEL
        ):
            continue
        if schema != expected_schema:
            mismatches.append(f"{file_name}_schema_version")


def _validate_identity(
    case_id: str,
    case_kind: str,
    payloads: Mapping[str, Mapping[str, Any]],
    mismatches: list[str],
) -> None:
    case_metadata = payloads[CASE_METADATA_FILE]
    if case_metadata.get("case_id") != case_id:
        mismatches.append("case_metadata_case_id")
    if case_metadata.get("case_kind") != case_kind:
        mismatches.append("case_metadata_case_kind")
    for file_name in (RUNTIME_SUMMARY_FILE, EXPECTED_SUMMARY_FILE):
        if payloads[file_name].get("case_id") != case_id:
            mismatches.append(f"{file_name}_case_id")
    if payloads[POINTER_METADATA_FILE].get("fixture_relative_path") != case_id:
        mismatches.append("pointer_fixture_relative_path")
    for file_name, id_key in (
        (REQUEST_METADATA_FILE, "request_id"),
        (POINTER_METADATA_FILE, "pointer_id"),
    ):
        value = payloads[file_name].get(id_key)
        if not isinstance(value, str) or not value.startswith(f"{case_id}::"):
            mismatches.append(f"{file_name}_{id_key}")


def _validate_expected_status_policy(
    case_id: str,
    case_kind: str,
    expected_status: str,
    expected_reason: str,
    expected_exit: str,
    payloads: Mapping[str, Mapping[str, Any]],
    mismatches: list[str],
) -> None:
    if case_kind == "valid":
        if case_id not in VALID_CASE_LABELS:
            mismatches.append("unknown_valid_case")
        required_reason = "none"
    else:
        required_reason = EXPECTED_INVALID_REASONS.get(case_id)
        if required_reason is None:
            mismatches.append("unknown_invalid_case")
            required_reason = "input_error"

    required_status = EXPECTED_STATUS_BY_REASON.get(required_reason, "fail_closed")
    required_exit = EXPECTED_EXIT_CODE_BY_STATUS.get(required_status, "input_error")
    if expected_reason != required_reason:
        mismatches.append("expected_reason_code")
    if expected_status != required_status:
        mismatches.append("expected_status")
    if expected_exit != required_exit:
        mismatches.append("expected_exit_code_category")
    case_metadata = payloads[CASE_METADATA_FILE]
    expected_summary = payloads[EXPECTED_SUMMARY_FILE]
    if case_metadata.get("expected_status") != expected_status:
        mismatches.append("case_metadata_expected_status")
    if case_metadata.get("expected_reason_code") != expected_reason:
        mismatches.append("case_metadata_expected_reason_code")
    if expected_summary.get("status") != expected_status:
        mismatches.append("expected_summary_status")
    if expected_summary.get("reason_code") != expected_reason:
        mismatches.append("expected_summary_reason_code")


def _validate_cross_file_consistency(
    payloads: Mapping[str, Mapping[str, Any]],
    mismatches: list[str],
) -> None:
    request = payloads[REQUEST_METADATA_FILE]
    generation = payloads[GENERATION_METADATA_FILE]
    expected_summary = payloads[EXPECTED_SUMMARY_FILE]
    expected_error = payloads[EXPECTED_ERROR_FILE]
    expected_reason = _str_field(expected_error, "expected_reason_code", "")
    if (
        request.get("mode") != generation.get("generation_mode")
        and expected_reason != "artifact_body_generation_unsafe_mode"
    ):
        mismatches.append("request_generation_mode")
    if expected_summary.get("mode") != MODE:
        mismatches.append("expected_summary_mode")
    if expected_summary.get("integration_mode") != (
        "actual_invocation_runtime_to_artifact_body_generation_metadata_bridge"
    ):
        mismatches.append("integration_mode")
    if not expected_error.get("body_suppressed") or not expected_error.get(
        "content_suppressed"
    ):
        mismatches.append("expected_error_suppression")
    if not expected_error.get("no_payload_in_error"):
        mismatches.append("expected_error_payload_policy")


def _validate_metadata_policy(
    case_kind: str,
    expected_reason: str,
    payloads: Mapping[str, Mapping[str, Any]],
    mismatches: list[str],
) -> None:
    _validate_runtime_summary(case_kind, expected_reason, payloads, mismatches)
    _validate_request_and_pointer(case_kind, expected_reason, payloads, mismatches)
    _validate_generation(case_kind, expected_reason, payloads, mismatches)
    _validate_sentinels(case_kind, expected_reason, payloads, mismatches)


def _validate_runtime_summary(
    case_kind: str,
    expected_reason: str,
    payloads: Mapping[str, Mapping[str, Any]],
    mismatches: list[str],
) -> None:
    runtime = payloads[RUNTIME_SUMMARY_FILE]
    if expected_reason != "runtime_summary_schema":
        if runtime.get("runtime_schema_version") != RUNTIME_RESULT_SCHEMA_VERSION:
            mismatches.append("runtime_result_schema")
    if case_kind == "valid":
        required = {
            "status": "pass",
            "reason_code": "none",
            "exit_code_category": "zero",
            "invocation_mode": "actual_invocation_metadata_only",
            "summary_mode": "summary_only_public_safe",
        }
        for key, expected in required.items():
            if runtime.get(key) != expected:
                mismatches.append(f"runtime_{key}")
        for key in (
            "content_suppressed",
            "body_suppressed",
            "runtime_actual_invocation_enabled",
            "artifact_writer_cli_invoked",
            "artifact_writer_cli_output_scanned",
            "artifact_writer_cli_output_body_free",
            "raw_stdout_body_suppressed",
            "raw_stderr_body_suppressed",
        ):
            if runtime.get(key) is not True:
                mismatches.append(f"runtime_{key}")
        for key in (
            "request_body_detected",
            "pointer_body_detected",
            "expected_body_detected",
            "artifact_body_payload_detected",
            "manifest_body_detected",
            "generated_policy_body_detected",
            "file_writing_detected",
            "artifact_body_generation_invoked",
            "manifest_writer_invoked",
            "file_writing_enabled",
            "production_readiness_claimed",
            "real_data_readiness_claimed",
            "performance_claims_present",
        ):
            if runtime.get(key) is not False:
                mismatches.append(f"runtime_{key}")


def _validate_request_and_pointer(
    case_kind: str,
    expected_reason: str,
    payloads: Mapping[str, Mapping[str, Any]],
    mismatches: list[str],
) -> None:
    if case_kind != "valid":
        return
    request = payloads[REQUEST_METADATA_FILE]
    pointer = payloads[POINTER_METADATA_FILE]
    for key in ("synthetic_only", "metadata_only", "no_oracle"):
        if request.get(key) is not True or pointer.get(key) is not True:
            mismatches.append(f"request_pointer_{key}")
    for key in ("summary_only", "no_file_writing", "no_manifest_writer", "no_payload_output"):
        if request.get(key) is not True:
            mismatches.append(f"request_{key}")
    for key in (
        "request_body_present",
        "artifact_body_payload_requested",
        "manifest_body_requested",
        "generated_policy_body_requested",
        "performance_metric_body_present",
        "real_data_marker_present",
    ):
        if request.get(key) is not False:
            mismatches.append(f"request_{key}")
    for key in (
        "pointer_body_present",
        "private_path_present",
        "absolute_path_present",
        "raw_learner_text_present",
        "raw_rows_present",
        "logits_present",
        "real_data_marker_present",
    ):
        if pointer.get(key) is not False:
            mismatches.append(f"pointer_{key}")


def _validate_generation(
    case_kind: str,
    expected_reason: str,
    payloads: Mapping[str, Mapping[str, Any]],
    mismatches: list[str],
) -> None:
    if case_kind != "valid":
        return
    generation = payloads[GENERATION_METADATA_FILE]
    mode = generation.get("generation_mode")
    if mode not in {"suppressed", "safe-metadata"}:
        mismatches.append("generation_mode")
    if generation.get("body_status") not in {
        "suppressed_metadata_only",
        "generated_safe_metadata_body",
    }:
        mismatches.append("generation_body_status")
    if generation.get("artifact_body_available") is not (mode == "safe-metadata"):
        mismatches.append("generation_artifact_body_available")
    for key in (
        "artifact_file_written",
        "manifest_file_written",
        "artifact_body_payload_present",
        "manifest_body_present",
        "generated_policy_body_present",
        "raw_stdout_body_present",
        "raw_stderr_body_present",
        "request_body_present",
        "pointer_body_present",
        "expected_body_present",
        "raw_rows_present",
        "logits_present",
        "private_path_present",
        "absolute_path_present",
        "raw_learner_text_present",
        "real_data_marker_present",
        "performance_metric_body_present",
    ):
        if generation.get(key) is not False:
            mismatches.append(f"generation_{key}")
    for key in ("content_suppressed", "body_suppressed"):
        if generation.get(key) is not True:
            mismatches.append(f"generation_{key}")
    if generation.get("validation_status") != "pass":
        mismatches.append("generation_validation_status")
    if generation.get("safe_summary") != "metadata_only_counts":
        mismatches.append("generation_safe_summary")


def _validate_sentinels(
    case_kind: str,
    expected_reason: str,
    payloads: Mapping[str, Mapping[str, Any]],
    mismatches: list[str],
) -> None:
    if case_kind == "valid":
        for reason in SENTINEL_REASON_KEYS:
            if _reason_sentinel_present(reason, payloads):
                mismatches.append(f"valid_sentinel_{reason}")
        return

    if expected_reason == "none":
        mismatches.append("invalid_reason_none")
        return
    if expected_reason == "runtime_summary_schema":
        if payloads[RUNTIME_SUMMARY_FILE].get("schema_version") != (
            UNSUPPORTED_RUNTIME_SUMMARY_SCHEMA_SENTINEL
        ):
            mismatches.append("runtime_summary_schema_sentinel")
        return
    if expected_reason == "mismatched_expected_status":
        if "expected_status_sentinel" not in payloads[RUNTIME_SUMMARY_FILE]:
            mismatches.append("mismatched_expected_status_sentinel")
        return
    if not _reason_sentinel_present(expected_reason, payloads):
        mismatches.append(f"missing_sentinel_{expected_reason}")


def _reason_sentinel_present(
    reason: str,
    payloads: Mapping[str, Mapping[str, Any]],
) -> bool:
    if reason == "runtime_summary_status":
        return payloads[RUNTIME_SUMMARY_FILE].get("status") == "fail_closed"
    if reason == "artifact_body_generation_unsafe_mode":
        return (
            payloads[GENERATION_METADATA_FILE].get("generation_mode")
            == "unsafe_body_output_requested"
        )
    for file_name, key in BOOL_TRUE_BY_REASON.get(reason, ()):
        if payloads[file_name].get(key) is True:
            return True
    for file_name, key in BOOL_FALSE_BY_REASON.get(reason, ()):
        if payloads[file_name].get(key) is False:
            return True
    return False


def _scan_for_unsafe_values(
    payloads: Mapping[str, Mapping[str, Any]],
    mismatches: list[str],
) -> None:
    def visit(value: Any, *, key: str | None = None) -> None:
        if isinstance(value, Mapping):
            for child_key, child_value in value.items():
                if child_key in FORBIDDEN_VALUE_KEYS:
                    mismatches.append("forbidden_payload_key")
                visit(child_value, key=str(child_key))
        elif isinstance(value, list):
            for child_value in value:
                visit(child_value, key=key)
        elif isinstance(value, str):
            lowered = value.lower()
            if LOCAL_ABSOLUTE_PATH_PATTERN.search(value):
                mismatches.append("forbidden_path_value")
            if any(
                marker in lowered
                for marker in (
                    "github actions raw log",
                    "full job output",
                    "copied github log block",
                    "real participant data",
                    "raw learner text payload",
                )
            ):
                mismatches.append("forbidden_text_value")

    for payload in payloads.values():
        visit(payload)


def _str_field(
    mapping: Mapping[str, Any],
    key: str,
    default: str,
) -> str:
    value = mapping.get(key)
    return value if isinstance(value, str) else default


def _format_human_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return str(value)


def _print_human_summary(payload: Mapping[str, Any]) -> None:
    for key, value in payload.items():
        print(f"{key}={_format_human_value(value)}")


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate synthetic metadata-only artifact body generation "
            "integration fixture contracts."
        )
    )
    parser.add_argument(
        "--fixture-root",
        default=str(DEFAULT_FIXTURE_ROOT),
        help="Fixture root to validate.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a machine-readable public-safe summary.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    summary = validate_artifact_body_generation_integration_fixture_root(
        args.fixture_root
    )
    payload = summarize_artifact_body_generation_integration_fixture_validation(
        summary
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        _print_human_summary(payload)
    return 0 if summary.all_matched else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
