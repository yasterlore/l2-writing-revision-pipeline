"""Static validation for artifact writer CLI actual invocation fixtures.

This validator checks synthetic metadata-only fixture contracts for a future
artifact writer CLI actual invocation boundary. It does not execute the
artifact writer CLI, call artifact body generation, call the manifest writer,
write files, train models, or compute metrics.
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
RUNTIME_REQUEST_METADATA_FILE = "runtime_request_metadata.json"
RUNTIME_POINTER_METADATA_FILE = "runtime_pointer_metadata.json"
ARTIFACT_WRITER_CLI_INVOCATION_METADATA_FILE = (
    "artifact_writer_cli_invocation_metadata.json"
)
EXPECTED_INVOCATION_SUMMARY_FILE = "expected_invocation_summary.json"
EXPECTED_ERROR_FILE = "expected_error.json"

DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation"
)

CASE_METADATA_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation_"
    "case_metadata_v0.1"
)
RUNTIME_REQUEST_METADATA_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation_"
    "runtime_request_metadata_v0.1"
)
RUNTIME_POINTER_METADATA_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation_"
    "runtime_pointer_metadata_v0.1"
)
ARTIFACT_WRITER_CLI_INVOCATION_METADATA_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation_"
    "metadata_v0.1"
)
EXPECTED_INVOCATION_SUMMARY_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation_"
    "expected_summary_v0.1"
)
EXPECTED_ERROR_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation_"
    "expected_error_v0.1"
)
RUNTIME_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_"
    "v0.1"
)

VALIDATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation_"
    "fixture_validation_v0.1"
)
MODE = "artifact_writer_cli_actual_invocation_fixture_validation"

EXPECTED_TOTAL_CASES = 32
EXPECTED_VALID_CASES = 6
EXPECTED_INVALID_CASES = 26
JSON_FILES_PER_CASE = 6
EXPECTED_TOTAL_JSON_FILES = EXPECTED_TOTAL_CASES * JSON_FILES_PER_CASE
EXPECTED_PASS_CASES = 6
EXPECTED_USAGE_ERROR_CASES = 3
EXPECTED_FAIL_CLOSED_CASES = 22
EXPECTED_MISMATCH_CASES = 1

REQUIRED_FILES = (
    CASE_METADATA_FILE,
    RUNTIME_REQUEST_METADATA_FILE,
    RUNTIME_POINTER_METADATA_FILE,
    ARTIFACT_WRITER_CLI_INVOCATION_METADATA_FILE,
    EXPECTED_INVOCATION_SUMMARY_FILE,
    EXPECTED_ERROR_FILE,
)

VALID_CASE_LABELS = frozenset(
    {
        "valid/valid_minimal_metadata_only_actual_invocation_plan",
        "valid/valid_artifact_writer_cli_summary_body_free",
        "valid/valid_relative_fixture_paths_only",
        "valid/valid_file_writing_disabled_actual_invocation",
        "valid/valid_no_oracle_flags_preserved",
        "valid/valid_invocation_output_safety_flags",
    }
)

EXPECTED_INVALID_REASONS = {
    "invalid/invalid_request_body_present": "request_body_present",
    "invalid/invalid_pointer_body_present": "pointer_body_present",
    "invalid/invalid_expected_body_present": "expected_body_present",
    "invalid/invalid_artifact_body_payload_present": "artifact_body_payload_present",
    "invalid/invalid_manifest_body_present": "manifest_body_present",
    "invalid/invalid_generated_policy_body_present": "generated_policy_body_present",
    "invalid/invalid_raw_learner_text_present": "raw_learner_text_present",
    "invalid/invalid_raw_rows_present": "raw_rows_present",
    "invalid/invalid_logits_present": "logits_present",
    "invalid/invalid_probabilities_present": "probabilities_present",
    "invalid/invalid_private_path_present": "private_path_present",
    "invalid/invalid_absolute_path_present": "absolute_path_present",
    "invalid/invalid_final_text_present": "final_text_present",
    "invalid/invalid_observed_after_text_present": "observed_after_text_present",
    "invalid/invalid_gold_label_present": "gold_label_present",
    "invalid/invalid_post_hoc_annotation_present": "post_hoc_annotation_present",
    "invalid/invalid_raw_stdout_body_present": "raw_stdout_body_present",
    "invalid/invalid_raw_stderr_body_present": "raw_stderr_body_present",
    "invalid/invalid_file_writing_requested": "file_writing_requested",
    "invalid/invalid_artifact_body_generation_invoked": (
        "artifact_body_generation_invoked"
    ),
    "invalid/invalid_manifest_writer_invoked": "manifest_writer_invoked",
    "invalid/invalid_unsupported_artifact_writer_schema": (
        "unsupported_artifact_writer_schema"
    ),
    "invalid/invalid_unsafe_actual_invocation_output": (
        "unsafe_actual_invocation_output"
    ),
    "invalid/invalid_mismatched_expected_status": "mismatched_expected_status",
    "invalid/invalid_missing_required_metadata_file": (
        "missing_required_metadata_file"
    ),
    "invalid/invalid_duplicate_case_id": "duplicate_case_id",
}
ALLOWED_REASON_CODES = frozenset(EXPECTED_INVALID_REASONS.values()) | {"none"}
ALLOWED_STATUS_CATEGORIES = {
    "pass",
    "usage_error",
    "fail_closed",
    "input_error",
    "mismatch",
}

CASE_METADATA_FIELDS = frozenset(
    {
        "schema_version",
        "case_id",
        "case_kind",
        "case_title",
        "case_intent",
        "expected_status",
        "expected_reason_code",
        "expected_exit_code_category",
        "synthetic_only",
        "metadata_only",
        "no_oracle",
        "content_suppressed",
        "body_suppressed",
        "forbidden_marker",
    }
)

RUNTIME_REQUEST_METADATA_FIELDS = frozenset(
    {
        "schema_version",
        "case_id",
        "mode",
        "invocation_mode",
        "artifact_writer_cli_module",
        "runtime_schema_version",
        "fixture_source",
        "relative_fixture_path",
        "suppression_policy",
        "no_oracle_policy",
        "synthetic_only",
        "metadata_only",
        "file_writing_requested",
        "artifact_writer_cli_actual_invocation_requested",
        "prohibited_field_present",
        "prohibited_body_value_stored",
        "forbidden_marker",
    }
)

RUNTIME_POINTER_METADATA_FIELDS = frozenset(
    {
        "schema_version",
        "case_id",
        "pointer_mode",
        "relative_repo_path",
        "relative_fixture_path",
        "safe_path_policy",
        "absolute_paths_allowed",
        "private_paths_allowed",
        "pointer_body_present",
        "metadata_only",
        "absolute_path_value_stored",
        "private_path_value_stored",
        "forbidden_marker",
    }
)

ARTIFACT_WRITER_CLI_INVOCATION_METADATA_FIELDS = frozenset(
    {
        "schema_version",
        "case_id",
        "command_label",
        "module_name",
        "safe_mode",
        "summary_mode",
        "expected_exit_code_category",
        "relative_request_pointer",
        "relative_artifact_writer_pointer",
        "suppression_flags",
        "no_oracle_flags",
        "expected_invocation_flags",
        "raw_stdout_stored",
        "raw_stderr_stored",
        "artifact_body_payload_stored",
        "manifest_body_stored",
        "generated_policy_body_stored",
        "file_contents_stored",
        "artifact_writer_schema",
        "unsafe_output_sentinel_present",
        "forbidden_marker",
    }
)

EXPECTED_INVOCATION_SUMMARY_FIELDS = frozenset(
    {
        "schema_version",
        "case_id",
        "expected_status",
        "expected_reason_code",
        "expected_exit_code_category",
        "expected_summary_mode",
        "artifact_writer_cli_invoked",
        "artifact_writer_cli_exit_code_category",
        "artifact_writer_cli_invocation_planned",
        "artifact_body_generation_invoked",
        "manifest_writer_invoked",
        "file_writing_enabled",
        "content_suppressed",
        "body_suppressed",
        "no_raw_rows",
        "no_logits_dump",
        "no_private_paths",
        "no_absolute_paths",
        "no_generated_policy_body",
        "no_artifact_body_payload",
        "no_manifest_body",
        "no_request_body",
        "no_pointer_body",
        "no_expected_body",
        "synthetic_only_checked",
        "metadata_only_checked",
        "no_oracle_checked",
        "production_readiness_claimed",
        "real_data_readiness_claimed",
        "performance_claims_present",
        "residue_expected",
        "forbidden_marker",
    }
)

EXPECTED_ERROR_FIELDS = frozenset(
    {
        "schema_version",
        "case_id",
        "expected_error_category",
        "expected_reason_code",
        "expected_exit_code_category",
        "fail_closed",
        "usage_error",
        "input_error",
        "mismatch",
        "public_safe_error",
        "error_body_suppressed",
        "raw_content_suppressed",
        "prohibited_body_value_stored",
        "forbidden_marker",
    }
)

TRUE_METADATA_FLAGS = (
    "content_suppressed",
    "body_suppressed",
    "synthetic_only",
    "metadata_only",
)

TRUE_SUMMARY_FLAGS = (
    "content_suppressed",
    "body_suppressed",
    "no_raw_rows",
    "no_logits_dump",
    "no_private_paths",
    "no_absolute_paths",
    "no_generated_policy_body",
    "no_artifact_body_payload",
    "no_manifest_body",
    "no_request_body",
    "no_pointer_body",
    "no_expected_body",
    "synthetic_only_checked",
    "metadata_only_checked",
    "no_oracle_checked",
)

FORBIDDEN_ACTUAL_KEYS = frozenset(
    {
        "request_body",
        "pointer_body",
        "expected_body",
        "written_file_json_body",
        "manifest_body",
        "artifact_body_payload",
        "generated_policy_body",
        "raw_stdout_body",
        "raw_stderr_body",
        "raw_learner_text",
        "raw_rows",
        "logits",
        "probabilities",
        "private_path",
        "absolute_path",
        "final_text",
        "observed_after_text",
        "gold_label",
        "gold_labels",
        "post_hoc_annotation",
        "post_hoc_annotations",
        "test_set_tuning",
        "test_tuning_payload",
        "scoring_feedback",
        "scoring_feedback_payload",
        "real_participant_data",
        "real_data_marker",
        "performance_metric_body",
        "performance_metrics",
    }
)

ALLOWED_SENTINEL_KEYS = frozenset(
    {
        "forbidden_marker",
        "prohibited_field_present",
        "prohibited_body_value_stored",
        "pointer_body_present",
        "absolute_path_value_stored",
        "private_path_value_stored",
        "raw_stdout_stored",
        "raw_stderr_stored",
        "artifact_body_payload_stored",
        "manifest_body_stored",
        "generated_policy_body_stored",
        "file_contents_stored",
        "unsafe_output_sentinel_present",
    }
)

_SLASH = "/"
_BACKSLASH = "\\"
_LOCAL_PATH_PREFIXES = ("Users", "home", "private", "var", "tmp")
_FILE_URI_MARKER = "file" + "://"
_RAW_LOG_MARKER = "##" + "["
LOCAL_ABSOLUTE_PATH_PATTERN = re.compile(
    r"(^|[=\s\"'])"
    + re.escape(_SLASH)
    + r"("
    + "|".join(_LOCAL_PATH_PREFIXES)
    + r")"
    + re.escape(_SLASH)
    + r"|[A-Za-z]:\\|"
    + re.escape(_FILE_URI_MARKER)
    + r"|"
    + re.escape(_BACKSLASH + "Users" + _BACKSLASH)
)
PRIVATE_PATH_MARKERS = (
    "icloud",
    "dropbox",
    "onedrive",
    "google drive",
    "s3://",
    "gs://",
)


class ArtifactWriterCliActualInvocationFixtureValidationError(Exception):
    """Raised when fixture validation cannot be performed safely."""


@dataclass(frozen=True)
class ArtifactWriterCliActualInvocationFixtureCaseResult:
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
class ArtifactWriterCliActualInvocationFixtureValidationSummary:
    case_results: list[ArtifactWriterCliActualInvocationFixtureCaseResult] = field(
        default_factory=list
    )
    reason_code_counts: Counter[str] = field(default_factory=Counter)
    root_errors: tuple[str, ...] = ()
    actual_json_files: int = 0
    duplicate_case_id_cases: int = 0
    missing_required_file_cases: int = 0

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
    def total_json_files(self) -> int:
        return self.actual_json_files

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


def discover_artifact_writer_cli_actual_invocation_fixture_cases(
    root: Path,
) -> list[Path]:
    """Return sorted case directories under valid/ and invalid/."""

    case_dirs: list[Path] = []
    for group in ("valid", "invalid"):
        group_dir = root / group
        if not group_dir.is_dir():
            continue
        case_dirs.extend(path for path in group_dir.iterdir() if path.is_dir())
    return sorted(case_dirs, key=_case_id_from_dir)


def validate_artifact_writer_cli_actual_invocation_fixture_root(
    fixture_root: str | Path = DEFAULT_FIXTURE_ROOT,
    *,
    fixture_case: str | None = None,
) -> ArtifactWriterCliActualInvocationFixtureValidationSummary:
    root = Path(fixture_root)
    root_errors: list[str] = []
    if not root.is_dir():
        root_errors.append("fixture_root_missing")
        return ArtifactWriterCliActualInvocationFixtureValidationSummary(
            root_errors=tuple(root_errors)
        )

    actual_json_files = len(list(root.rglob("*.json")))
    duplicate_case_ids = _find_duplicate_case_ids(root)
    duplicate_case_id_cases = len(duplicate_case_ids)
    missing_required_file_cases = 0
    if duplicate_case_ids:
        root_errors.append("duplicate_case_id_detected")

    if fixture_case:
        if _unsafe_case_selector(fixture_case):
            root_errors.append("unsafe_fixture_case_selector")
            return ArtifactWriterCliActualInvocationFixtureValidationSummary(
                root_errors=tuple(root_errors),
                actual_json_files=actual_json_files,
                duplicate_case_id_cases=duplicate_case_id_cases,
            )
        case_dirs = [root / fixture_case]
        if not case_dirs[0].is_dir():
            root_errors.append("fixture_case_missing")
            return ArtifactWriterCliActualInvocationFixtureValidationSummary(
                root_errors=tuple(root_errors),
                actual_json_files=actual_json_files,
                duplicate_case_id_cases=duplicate_case_id_cases,
            )
        actual_json_files = len(list(case_dirs[0].glob("*.json")))
    else:
        case_dirs = discover_artifact_writer_cli_actual_invocation_fixture_cases(root)
        _check_root_counts(root, case_dirs, actual_json_files, root_errors)

    case_results: list[ArtifactWriterCliActualInvocationFixtureCaseResult] = []
    reason_counts: Counter[str] = Counter()
    for case_dir in case_dirs:
        if _required_file_error(case_dir) == "required_file_missing":
            missing_required_file_cases += 1
        result = validate_artifact_writer_cli_actual_invocation_fixture_case(case_dir)
        case_results.append(result)
        reason_counts.update([result.expected_reason_code])
        if result.expected_reason_code == "duplicate_case_id":
            duplicate_case_id_cases += 1
        if result.expected_reason_code == "missing_required_metadata_file":
            missing_required_file_cases += 1

    return ArtifactWriterCliActualInvocationFixtureValidationSummary(
        case_results=case_results,
        reason_code_counts=reason_counts,
        root_errors=tuple(root_errors),
        actual_json_files=actual_json_files,
        duplicate_case_id_cases=duplicate_case_id_cases,
        missing_required_file_cases=missing_required_file_cases,
    )


def validate_artifact_writer_cli_actual_invocation_fixture_case(
    case_dir: str | Path,
) -> ArtifactWriterCliActualInvocationFixtureCaseResult:
    path = Path(case_dir)
    case_id = _case_id_from_dir(path)
    case_kind = path.parent.name if path.parent.name in {"valid", "invalid"} else "unknown"

    file_error = _required_file_error(path)
    if file_error:
        return _case_input_error(path, file_error)

    try:
        case_metadata = _load_json(path / CASE_METADATA_FILE)
        runtime_request_metadata = _load_json(path / RUNTIME_REQUEST_METADATA_FILE)
        runtime_pointer_metadata = _load_json(path / RUNTIME_POINTER_METADATA_FILE)
        artifact_writer_cli_invocation_metadata = _load_json(
            path / ARTIFACT_WRITER_CLI_INVOCATION_METADATA_FILE
        )
        expected_invocation_summary = _load_json(path / EXPECTED_INVOCATION_SUMMARY_FILE)
        expected_error = _load_json(path / EXPECTED_ERROR_FILE)
    except (
        OSError,
        json.JSONDecodeError,
        ArtifactWriterCliActualInvocationFixtureValidationError,
    ):
        return _case_input_error(path, "malformed_json")

    payloads = (
        case_metadata,
        runtime_request_metadata,
        runtime_pointer_metadata,
        artifact_writer_cli_invocation_metadata,
        expected_invocation_summary,
        expected_error,
    )
    mismatches: list[str] = []
    _validate_field_sets(
        case_metadata,
        runtime_request_metadata,
        runtime_pointer_metadata,
        artifact_writer_cli_invocation_metadata,
        expected_invocation_summary,
        expected_error,
        mismatches,
    )
    _validate_schema_and_identity(
        case_id,
        case_kind,
        case_metadata,
        runtime_request_metadata,
        runtime_pointer_metadata,
        artifact_writer_cli_invocation_metadata,
        expected_invocation_summary,
        expected_error,
        mismatches,
    )
    _validate_reason_and_status_policy(
        case_id,
        case_kind,
        case_metadata,
        expected_invocation_summary,
        expected_error,
        mismatches,
    )
    _validate_suppression_and_no_oracle_policy(
        case_metadata,
        runtime_request_metadata,
        runtime_pointer_metadata,
        artifact_writer_cli_invocation_metadata,
        expected_invocation_summary,
        expected_error,
        mismatches,
    )
    _validate_path_safety_policy(
        runtime_pointer_metadata,
        expected_invocation_summary,
        mismatches,
    )
    _validate_file_writing_and_residue_policy(
        runtime_request_metadata,
        artifact_writer_cli_invocation_metadata,
        expected_invocation_summary,
        mismatches,
    )
    _validate_downstream_boundary_policy(
        artifact_writer_cli_invocation_metadata,
        expected_invocation_summary,
        mismatches,
    )
    _validate_sentinel_policy(
        case_kind,
        case_metadata,
        runtime_request_metadata,
        runtime_pointer_metadata,
        artifact_writer_cli_invocation_metadata,
        expected_error,
        mismatches,
    )
    _scan_for_forbidden_content(payloads, mismatches)

    expected_status = _expected_status(expected_invocation_summary, expected_error)
    expected_reason = _string_value(
        expected_invocation_summary,
        "expected_reason_code",
        "input_error",
    )
    expected_exit_code = _string_value(
        expected_invocation_summary,
        "expected_exit_code_category",
        "nonzero",
    )
    return ArtifactWriterCliActualInvocationFixtureCaseResult(
        case_id=case_id,
        case_kind=case_kind,
        expected_status=expected_status,
        expected_reason_code=expected_reason,
        expected_exit_code_category=expected_exit_code,
        matched=not mismatches,
        input_error=False,
        mismatch_reasons=tuple(sorted(set(mismatches))),
    )


def summarize_artifact_writer_cli_actual_invocation_fixture_validation(
    summary: ArtifactWriterCliActualInvocationFixtureValidationSummary,
    *,
    fixture_root_display: str | None = None,
) -> dict[str, Any]:
    return {
        "mode": MODE,
        "validation_schema_version": VALIDATION_SCHEMA_VERSION,
        "fixture_root": fixture_root_display or str(DEFAULT_FIXTURE_ROOT),
        "total_cases": summary.total_cases,
        "valid_cases": summary.valid_cases,
        "invalid_cases": summary.invalid_cases,
        "total_json_files": summary.total_json_files,
        "json_files_per_case": JSON_FILES_PER_CASE,
        "matched_cases": summary.matched_cases,
        "mismatched_cases": summary.mismatched_cases,
        "input_error_cases": summary.input_error_cases,
        "pass_cases": summary.pass_cases,
        "usage_error_cases": summary.usage_error_cases,
        "fail_closed_cases": summary.fail_closed_cases,
        "mismatch_cases": summary.mismatch_cases,
        "duplicate_case_id_cases": summary.duplicate_case_id_cases,
        "missing_required_file_cases": summary.missing_required_file_cases,
        "content_suppressed": True,
        "body_suppressed": True,
        "no_raw_rows": True,
        "no_logits_dump": True,
        "no_private_paths": True,
        "no_absolute_paths": True,
        "no_generated_policy_body": True,
        "no_artifact_body_payload": True,
        "no_manifest_body": True,
        "no_request_body": True,
        "no_pointer_body": True,
        "no_expected_body": True,
        "no_raw_stdout_body": True,
        "no_raw_stderr_body": True,
        "no_oracle_checked": True,
        "synthetic_only_checked": True,
        "metadata_only_checked": True,
        "file_writing_checked": True,
        "artifact_writer_cli_actual_invocation_fixture_checked": True,
        "artifact_body_generation_integration_checked": True,
        "manifest_writer_integration_checked": True,
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
    valid_dir = root / "valid"
    invalid_dir = root / "invalid"
    if not valid_dir.is_dir():
        root_errors.append("valid_dir_missing")
    if not invalid_dir.is_dir():
        root_errors.append("invalid_dir_missing")

    valid_cases = sum(path.parent.name == "valid" for path in case_dirs)
    invalid_cases = sum(path.parent.name == "invalid" for path in case_dirs)
    if len(case_dirs) != EXPECTED_TOTAL_CASES:
        root_errors.append("total_case_count_mismatch")
    if valid_cases != EXPECTED_VALID_CASES:
        root_errors.append("valid_case_count_mismatch")
    if invalid_cases != EXPECTED_INVALID_CASES:
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
        return "extra_json_file"
    if required - json_names:
        return "required_file_missing"
    return None


def _validate_field_sets(
    case_metadata: Mapping[str, Any],
    runtime_request_metadata: Mapping[str, Any],
    runtime_pointer_metadata: Mapping[str, Any],
    artifact_writer_cli_invocation_metadata: Mapping[str, Any],
    expected_invocation_summary: Mapping[str, Any],
    expected_error: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    _field_set(case_metadata, CASE_METADATA_FIELDS, "case_metadata", mismatches)
    _field_set(
        runtime_request_metadata,
        RUNTIME_REQUEST_METADATA_FIELDS,
        "runtime_request_metadata",
        mismatches,
    )
    _field_set(
        runtime_pointer_metadata,
        RUNTIME_POINTER_METADATA_FIELDS,
        "runtime_pointer_metadata",
        mismatches,
    )
    _field_set(
        artifact_writer_cli_invocation_metadata,
        ARTIFACT_WRITER_CLI_INVOCATION_METADATA_FIELDS,
        "artifact_writer_cli_invocation_metadata",
        mismatches,
    )
    _field_set(
        expected_invocation_summary,
        EXPECTED_INVOCATION_SUMMARY_FIELDS,
        "expected_invocation_summary",
        mismatches,
    )
    _field_set(expected_error, EXPECTED_ERROR_FIELDS, "expected_error", mismatches)


def _validate_schema_and_identity(
    case_id: str,
    case_kind: str,
    case_metadata: Mapping[str, Any],
    runtime_request_metadata: Mapping[str, Any],
    runtime_pointer_metadata: Mapping[str, Any],
    artifact_writer_cli_invocation_metadata: Mapping[str, Any],
    expected_invocation_summary: Mapping[str, Any],
    expected_error: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    _schema(case_metadata, CASE_METADATA_SCHEMA_VERSION, "case_metadata", mismatches)
    _schema(
        runtime_request_metadata,
        RUNTIME_REQUEST_METADATA_SCHEMA_VERSION,
        "runtime_request_metadata",
        mismatches,
    )
    _schema(
        runtime_pointer_metadata,
        RUNTIME_POINTER_METADATA_SCHEMA_VERSION,
        "runtime_pointer_metadata",
        mismatches,
    )
    _schema(
        artifact_writer_cli_invocation_metadata,
        ARTIFACT_WRITER_CLI_INVOCATION_METADATA_SCHEMA_VERSION,
        "artifact_writer_cli_invocation_metadata",
        mismatches,
    )
    _schema(
        expected_invocation_summary,
        EXPECTED_INVOCATION_SUMMARY_SCHEMA_VERSION,
        "expected_invocation_summary",
        mismatches,
    )
    _schema(expected_error, EXPECTED_ERROR_SCHEMA_VERSION, "expected_error", mismatches)

    for label, payload in (
        ("case_metadata", case_metadata),
        ("runtime_request_metadata", runtime_request_metadata),
        ("runtime_pointer_metadata", runtime_pointer_metadata),
        ("artifact_writer_cli_invocation_metadata", artifact_writer_cli_invocation_metadata),
        ("expected_invocation_summary", expected_invocation_summary),
        ("expected_error", expected_error),
    ):
        if payload.get("case_id") != case_id:
            mismatches.append(f"{label}_case_id_mismatch")

    if case_metadata.get("case_kind") != case_kind:
        mismatches.append("case_kind_mismatch")
    if runtime_request_metadata.get("mode") != (
        "artifact_writer_cli_actual_invocation_fixture_contract"
    ):
        mismatches.append("runtime_request_mode_mismatch")
    if runtime_request_metadata.get("invocation_mode") != (
        "metadata_only_actual_invocation_boundary"
    ):
        mismatches.append("runtime_request_invocation_mode_mismatch")
    if runtime_request_metadata.get("artifact_writer_cli_module") != (
        "learner_state.frozen_policy_generation_artifact_writer"
    ):
        mismatches.append("artifact_writer_cli_module_mismatch")
    if runtime_request_metadata.get("runtime_schema_version") != RUNTIME_SCHEMA_VERSION:
        mismatches.append("runtime_schema_version_mismatch")
    if artifact_writer_cli_invocation_metadata.get("module_name") != (
        "learner_state.frozen_policy_generation_artifact_writer"
    ):
        mismatches.append("artifact_writer_cli_invocation_module_mismatch")


def _validate_reason_and_status_policy(
    case_id: str,
    case_kind: str,
    case_metadata: Mapping[str, Any],
    expected_invocation_summary: Mapping[str, Any],
    expected_error: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    summary_status = _string_value(expected_invocation_summary, "expected_status", "")
    expected_status = _expected_status(expected_invocation_summary, expected_error)
    expected_reason = _string_value(
        expected_invocation_summary,
        "expected_reason_code",
        "",
    )
    expected_exit_code = _string_value(
        expected_invocation_summary,
        "expected_exit_code_category",
        "",
    )
    expected_error_category = _string_value(
        expected_error,
        "expected_error_category",
        "",
    )

    if expected_reason not in ALLOWED_REASON_CODES:
        mismatches.append("unknown_reason_code")
    if expected_status not in ALLOWED_STATUS_CATEGORIES:
        mismatches.append("unknown_expected_status")
    if case_metadata.get("expected_reason_code") != expected_reason:
        mismatches.append("metadata_expected_reason_code_mismatch")
    if case_metadata.get("expected_exit_code_category") != expected_exit_code:
        mismatches.append("metadata_expected_exit_code_mismatch")
    if expected_error.get("expected_reason_code") != expected_reason:
        mismatches.append("expected_error_reason_code_mismatch")
    if expected_error.get("expected_exit_code_category") != expected_exit_code:
        mismatches.append("expected_error_exit_code_mismatch")

    if expected_status == "mismatch":
        if summary_status != "pass_expected_by_fixture_sentinel":
            mismatches.append("mismatch_summary_status_sentinel_missing")
        if case_metadata.get("expected_status") != summary_status:
            mismatches.append("mismatch_metadata_expected_status_mismatch")
    elif case_metadata.get("expected_status") != summary_status:
        mismatches.append("metadata_expected_status_mismatch")

    if case_kind == "valid":
        if case_id not in VALID_CASE_LABELS:
            mismatches.append("unknown_valid_case")
        if expected_status != "pass":
            mismatches.append("valid_case_status_not_pass")
        if expected_reason != "none":
            mismatches.append("valid_case_reason_not_none")
        if expected_exit_code != "zero":
            mismatches.append("valid_case_exit_code_not_zero")
        if expected_error_category != "none":
            mismatches.append("valid_expected_error_category_not_none")
    elif case_kind == "invalid":
        expected_reason_for_case = EXPECTED_INVALID_REASONS.get(case_id)
        if expected_reason_for_case is None:
            mismatches.append("unknown_invalid_case")
        if expected_status not in {"usage_error", "fail_closed", "mismatch"}:
            mismatches.append("invalid_case_status_not_error")
        if expected_exit_code != "nonzero":
            mismatches.append("invalid_case_exit_code_not_nonzero")
        if expected_reason_for_case is not None and expected_reason != expected_reason_for_case:
            mismatches.append("reason_code_case_mismatch")
        if expected_error_category != expected_status:
            mismatches.append("expected_error_category_status_mismatch")
    else:
        mismatches.append("case_kind_unknown")

    _validate_expected_error_flags(expected_status, expected_error, mismatches)


def _validate_expected_error_flags(
    expected_status: str,
    expected_error: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    if expected_status == "pass":
        if expected_error.get("fail_closed") is not False:
            mismatches.append("pass_case_fail_closed_not_false")
        if expected_error.get("usage_error") is not False:
            mismatches.append("pass_case_usage_error_not_false")
        if expected_error.get("input_error") is not False:
            mismatches.append("pass_case_input_error_not_false")
        if expected_error.get("mismatch") is not False:
            mismatches.append("pass_case_mismatch_not_false")
    elif expected_status == "usage_error":
        if expected_error.get("usage_error") is not True:
            mismatches.append("usage_error_flag_not_true")
        if expected_error.get("fail_closed") is not False:
            mismatches.append("usage_error_fail_closed_not_false")
    elif expected_status == "fail_closed":
        if expected_error.get("fail_closed") is not True:
            mismatches.append("fail_closed_flag_not_true")
        if expected_error.get("usage_error") is not False:
            mismatches.append("fail_closed_usage_error_not_false")
    elif expected_status == "mismatch":
        if expected_error.get("mismatch") is not True:
            mismatches.append("mismatch_flag_not_true")
        if expected_error.get("usage_error") is not False:
            mismatches.append("mismatch_usage_error_not_false")
        if expected_error.get("fail_closed") is not False:
            mismatches.append("mismatch_fail_closed_not_false")


def _validate_suppression_and_no_oracle_policy(
    case_metadata: Mapping[str, Any],
    runtime_request_metadata: Mapping[str, Any],
    runtime_pointer_metadata: Mapping[str, Any],
    artifact_writer_cli_invocation_metadata: Mapping[str, Any],
    expected_invocation_summary: Mapping[str, Any],
    expected_error: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    for field_name in TRUE_METADATA_FLAGS:
        if case_metadata.get(field_name) is not True:
            mismatches.append(f"case_metadata_{field_name}_not_true")
    if case_metadata.get("no_oracle") is not True:
        mismatches.append("case_metadata_no_oracle_not_true")
    if runtime_request_metadata.get("synthetic_only") is not True:
        mismatches.append("runtime_request_synthetic_only_not_true")
    if runtime_request_metadata.get("metadata_only") is not True:
        mismatches.append("runtime_request_metadata_only_not_true")
    if runtime_pointer_metadata.get("metadata_only") is not True:
        mismatches.append("runtime_pointer_metadata_only_not_true")

    reason = _string_value(expected_invocation_summary, "expected_reason_code", "")
    if reason == "none":
        for field_name in TRUE_SUMMARY_FLAGS:
            if expected_invocation_summary.get(field_name) is not True:
                mismatches.append(f"expected_invocation_summary_{field_name}_not_true")
    if expected_invocation_summary.get("production_readiness_claimed") is not False:
        mismatches.append("production_readiness_claimed_not_false")
    if expected_invocation_summary.get("real_data_readiness_claimed") is not False:
        mismatches.append("real_data_readiness_claimed_not_false")
    if expected_invocation_summary.get("performance_claims_present") is not False:
        mismatches.append("performance_claims_present_not_false")
    expected_status = _expected_status(expected_invocation_summary, expected_error)
    expected_public_safe_error = expected_status != "pass"
    if expected_error.get("public_safe_error") is not expected_public_safe_error:
        mismatches.append("public_safe_error_flag_mismatch")
    if expected_error.get("error_body_suppressed") is not True:
        mismatches.append("error_body_suppressed_not_true")
    if expected_error.get("raw_content_suppressed") is not True:
        mismatches.append("raw_content_suppressed_not_true")
    if expected_error.get("prohibited_body_value_stored") is not False:
        mismatches.append("prohibited_body_value_stored_not_false")

    if runtime_request_metadata.get("suppression_policy") != "body_free_summary_only":
        mismatches.append("suppression_policy_mismatch")
    if runtime_request_metadata.get("no_oracle_policy") != "no_future_or_gold_fields":
        mismatches.append("no_oracle_policy_mismatch")

    suppression_flags = artifact_writer_cli_invocation_metadata.get("suppression_flags")
    if not isinstance(suppression_flags, Mapping):
        mismatches.append("suppression_flags_not_object")
    else:
        for field_name in (
            "content_suppressed",
            "body_suppressed",
            "raw_output_suppressed",
        ):
            if suppression_flags.get(field_name) is not True:
                mismatches.append(f"suppression_flag_{field_name}_not_true")

    no_oracle_flags = artifact_writer_cli_invocation_metadata.get("no_oracle_flags")
    if not isinstance(no_oracle_flags, Mapping):
        mismatches.append("no_oracle_flags_not_object")
    else:
        for field_name in (
            "synthetic_only",
            "metadata_only",
            "no_oracle",
        ):
            if no_oracle_flags.get(field_name) is not True:
                mismatches.append(f"no_oracle_flag_{field_name}_not_true")


def _validate_path_safety_policy(
    runtime_pointer_metadata: Mapping[str, Any],
    expected_invocation_summary: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    reason = _string_value(expected_invocation_summary, "expected_reason_code", "")
    if runtime_pointer_metadata.get("safe_path_policy") != "relative_paths_only":
        mismatches.append("safe_path_policy_not_relative_only")
    if runtime_pointer_metadata.get("absolute_paths_allowed") is not False:
        mismatches.append("absolute_paths_allowed_not_false")
    if runtime_pointer_metadata.get("private_paths_allowed") is not False:
        mismatches.append("private_paths_allowed_not_false")
    if runtime_pointer_metadata.get("absolute_path_value_stored") is not False:
        mismatches.append("absolute_path_value_stored_not_false")
    if runtime_pointer_metadata.get("private_path_value_stored") is not False:
        mismatches.append("private_path_value_stored_not_false")
    if runtime_pointer_metadata.get("pointer_body_present") is not False:
        if reason != "pointer_body_present":
            mismatches.append("pointer_body_present_not_false")


def _validate_file_writing_and_residue_policy(
    runtime_request_metadata: Mapping[str, Any],
    artifact_writer_cli_invocation_metadata: Mapping[str, Any],
    expected_invocation_summary: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    reason = _string_value(expected_invocation_summary, "expected_reason_code", "")
    if runtime_request_metadata.get("file_writing_requested") is not False:
        if reason != "file_writing_requested":
            mismatches.append("file_writing_requested_not_false")
    if expected_invocation_summary.get("file_writing_enabled") is not False:
        if reason != "file_writing_requested":
            mismatches.append("file_writing_enabled_not_false")
    if expected_invocation_summary.get("residue_expected") is not False:
        mismatches.append("residue_expected_not_false")
    if artifact_writer_cli_invocation_metadata.get("file_contents_stored") is not False:
        mismatches.append("file_contents_stored_not_false")


def _validate_downstream_boundary_policy(
    artifact_writer_cli_invocation_metadata: Mapping[str, Any],
    expected_invocation_summary: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    reason = _string_value(expected_invocation_summary, "expected_reason_code", "")
    if expected_invocation_summary.get("artifact_body_generation_invoked") is not False:
        if reason != "artifact_body_generation_invoked":
            mismatches.append("artifact_body_generation_invoked_not_false")
    if expected_invocation_summary.get("manifest_writer_invoked") is not False:
        if reason != "manifest_writer_invoked":
            mismatches.append("manifest_writer_invoked_not_false")
    if artifact_writer_cli_invocation_metadata.get("artifact_body_payload_stored") is not False:
        mismatches.append("artifact_body_payload_stored_not_false")
    if artifact_writer_cli_invocation_metadata.get("manifest_body_stored") is not False:
        mismatches.append("manifest_body_stored_not_false")
    if artifact_writer_cli_invocation_metadata.get("generated_policy_body_stored") is not False:
        mismatches.append("generated_policy_body_stored_not_false")
    if artifact_writer_cli_invocation_metadata.get("raw_stdout_stored") is not False:
        mismatches.append("raw_stdout_stored_not_false")
    if artifact_writer_cli_invocation_metadata.get("raw_stderr_stored") is not False:
        mismatches.append("raw_stderr_stored_not_false")
    if artifact_writer_cli_invocation_metadata.get("unsafe_output_sentinel_present") is not False:
        if reason != "unsafe_actual_invocation_output":
            mismatches.append("unsafe_output_sentinel_present_not_false")


def _validate_sentinel_policy(
    case_kind: str,
    case_metadata: Mapping[str, Any],
    runtime_request_metadata: Mapping[str, Any],
    runtime_pointer_metadata: Mapping[str, Any],
    artifact_writer_cli_invocation_metadata: Mapping[str, Any],
    expected_error: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    reason = _string_value(case_metadata, "expected_reason_code", "")
    marker = _string_value(case_metadata, "forbidden_marker", "")
    if case_kind == "valid":
        if marker != "none":
            mismatches.append("valid_case_forbidden_marker_not_none")
    elif marker != reason:
        mismatches.append("forbidden_marker_reason_mismatch")

    for label, payload in (
        ("runtime_request", runtime_request_metadata),
        ("runtime_pointer", runtime_pointer_metadata),
        ("artifact_writer_cli_invocation", artifact_writer_cli_invocation_metadata),
        ("expected_error", expected_error),
    ):
        payload_marker = _string_value(payload, "forbidden_marker", "")
        if case_kind == "valid" and payload_marker != "none":
            mismatches.append(f"{label}_forbidden_marker_not_none")
        elif case_kind == "invalid" and payload_marker != reason:
            mismatches.append(f"{label}_forbidden_marker_reason_mismatch")

    if runtime_request_metadata.get("prohibited_body_value_stored") is not False:
        mismatches.append("runtime_request_prohibited_body_value_stored_not_false")
    if expected_error.get("prohibited_body_value_stored") is not False:
        mismatches.append("expected_error_prohibited_body_value_stored_not_false")

    sentinel_values = {
        "pointer_body_present": runtime_pointer_metadata.get("pointer_body_present"),
        "file_writing_requested": runtime_request_metadata.get("file_writing_requested"),
        "artifact_body_generation_invoked": expected_error.get(
            "expected_reason_code"
        )
        == "artifact_body_generation_invoked"
        and expected_error.get("fail_closed") is True,
        "manifest_writer_invoked": expected_error.get("expected_reason_code")
        == "manifest_writer_invoked"
        and expected_error.get("fail_closed") is True,
        "unsafe_actual_invocation_output": artifact_writer_cli_invocation_metadata.get(
            "unsafe_output_sentinel_present"
        ),
    }
    true_sentinels = {key for key, value in sentinel_values.items() if value is True}

    if case_kind == "valid":
        if runtime_request_metadata.get("prohibited_field_present") is not False:
            mismatches.append("valid_case_prohibited_field_present")
        if true_sentinels:
            mismatches.append("valid_case_sentinel_present")
    elif reason != "none":
        if runtime_request_metadata.get("prohibited_field_present") is not True:
            mismatches.append("prohibited_field_present_missing")
        if reason in sentinel_values and reason not in true_sentinels:
            mismatches.append("expected_sentinel_not_present")


def _scan_for_forbidden_content(
    payloads: Sequence[Mapping[str, Any]],
    mismatches: list[str],
) -> None:
    for payload in payloads:
        _scan_value(payload, mismatches)


def _scan_value(value: Any, mismatches: list[str], key_path: tuple[str, ...] = ()) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if _is_forbidden_actual_key(key):
                mismatches.append(f"forbidden_actual_key:{key}")
            _scan_value(item, mismatches, (*key_path, key))
    elif isinstance(value, list):
        for item in value:
            _scan_value(item, mismatches, key_path)
    elif isinstance(value, str):
        lowered = value.lower()
        if LOCAL_ABSOLUTE_PATH_PATTERN.search(value) or value.startswith(("~", "/")):
            mismatches.append("actual_absolute_or_private_path")
        if ".." in value.replace("\\", "/").split("/"):
            mismatches.append("parent_traversal_path_value")
        if any(marker in lowered for marker in PRIVATE_PATH_MARKERS):
            mismatches.append("private_path_marker_value")
        if "real participant" in lowered:
            mismatches.append("real_participant_marker")
        if _RAW_LOG_MARKER in value:
            mismatches.append("raw_log_marker")


def _is_forbidden_actual_key(key: str) -> bool:
    if key in FORBIDDEN_ACTUAL_KEYS:
        return True
    if key.startswith("no_"):
        return False
    if key in ALLOWED_SENTINEL_KEYS:
        return False
    if key.endswith("_present") or key.endswith("_stored"):
        return False
    if key.endswith("_allowed"):
        return False
    return False


def _load_json(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ArtifactWriterCliActualInvocationFixtureValidationError(
            "json_root_not_object"
        )
    return payload


def _case_id_from_dir(case_dir: Path) -> str:
    return f"{case_dir.parent.name}/{case_dir.name}"


def _case_input_error(
    case_dir: Path,
    reason: str,
) -> ArtifactWriterCliActualInvocationFixtureCaseResult:
    case_kind = case_dir.parent.name
    if case_kind not in {"valid", "invalid"}:
        case_kind = "unknown"
    return ArtifactWriterCliActualInvocationFixtureCaseResult(
        case_id=_case_id_from_dir(case_dir),
        case_kind=case_kind,
        expected_status="input_error",
        expected_reason_code=reason,
        expected_exit_code_category="nonzero",
        matched=False,
        input_error=True,
        mismatch_reasons=(reason,),
    )


def _field_set(
    payload: Mapping[str, Any],
    expected_fields: frozenset[str],
    label: str,
    mismatches: list[str],
) -> None:
    actual = set(payload)
    missing = expected_fields - actual
    extra = actual - expected_fields
    if missing:
        mismatches.append(f"{label}_missing_fields")
    if extra:
        mismatches.append(f"{label}_extra_fields")


def _schema(
    payload: Mapping[str, Any],
    expected_schema: str,
    label: str,
    mismatches: list[str],
) -> None:
    if payload.get("schema_version") != expected_schema:
        mismatches.append(f"{label}_schema_version_mismatch")


def _find_duplicate_case_ids(root: Path) -> set[str]:
    seen: set[str] = set()
    duplicate: set[str] = set()
    for path in sorted(root.glob("*/*/case_metadata.json")):
        try:
            payload = _load_json(path)
        except (
            OSError,
            json.JSONDecodeError,
            ArtifactWriterCliActualInvocationFixtureValidationError,
        ):
            continue
        case_id = payload.get("case_id")
        if not isinstance(case_id, str):
            continue
        if case_id in seen:
            duplicate.add(case_id)
        seen.add(case_id)
    return duplicate


def _expected_status(
    expected_invocation_summary: Mapping[str, Any],
    expected_error: Mapping[str, Any],
) -> str:
    category = _string_value(expected_error, "expected_error_category", "")
    if category == "none":
        return "pass"
    if category in {"usage_error", "fail_closed", "input_error", "mismatch"}:
        return category
    return _string_value(expected_invocation_summary, "expected_status", "input_error")


def _string_value(payload: Mapping[str, Any], key: str, fallback: str) -> str:
    value = payload.get(key)
    return value if isinstance(value, str) else fallback


def _unsafe_case_selector(selector: str) -> bool:
    if not selector or selector.startswith(("/", "~")) or "\\" in selector:
        return True
    parts = selector.split("/")
    return len(parts) != 2 or parts[0] not in {"valid", "invalid"} or ".." in parts


def _format_human_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return str(value)


def _print_human_summary(payload: Mapping[str, Any]) -> None:
    for key, value in payload.items():
        print(f"{key}={_format_human_value(value)}")


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate synthetic metadata-only artifact writer CLI actual "
            "invocation fixture contracts."
        )
    )
    parser.add_argument(
        "--fixture-root",
        default=str(DEFAULT_FIXTURE_ROOT),
        help="Fixture root to validate.",
    )
    parser.add_argument(
        "--fixture-case",
        help=(
            "Optional safe relative case id such as "
            "valid/valid_minimal_metadata_only_actual_invocation_plan."
        ),
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

    summary = validate_artifact_writer_cli_actual_invocation_fixture_root(
        args.fixture_root,
        fixture_case=args.fixture_case,
    )
    payload = summarize_artifact_writer_cli_actual_invocation_fixture_validation(
        summary,
        fixture_root_display=args.fixture_root,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        _print_human_summary(payload)
    return 0 if summary.all_matched else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
