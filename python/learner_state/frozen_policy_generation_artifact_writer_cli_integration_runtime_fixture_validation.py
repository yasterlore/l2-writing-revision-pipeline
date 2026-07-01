"""Static validation for artifact writer CLI integration runtime fixtures.

This validator checks synthetic metadata-only runtime fixture contracts. It
does not execute artifact writer CLI integration, call the artifact writer CLI,
connect artifact body generation, connect the manifest writer, write files,
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
REQUEST_METADATA_FILE = "request_metadata.json"
POINTER_METADATA_FILE = "pointer_metadata.json"
ARTIFACT_WRITER_CLI_METADATA_FILE = "artifact_writer_cli_metadata.json"
EXPECTED_RUNTIME_SUMMARY_FILE = "expected_runtime_summary.json"
EXPECTED_ERROR_FILE = "expected_error.json"

DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime"
)

CASE_METADATA_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_"
    "case_metadata_v0.1"
)
REQUEST_METADATA_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_"
    "request_metadata_v0.1"
)
POINTER_METADATA_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_"
    "pointer_metadata_v0.1"
)
ARTIFACT_WRITER_CLI_METADATA_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_"
    "artifact_writer_cli_metadata_v0.1"
)
EXPECTED_RUNTIME_SUMMARY_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_"
    "result_v0.1"
)
EXPECTED_ERROR_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_"
    "expected_error_v0.1"
)
REQUEST_VALIDATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_"
    "fixture_contract_v0.1"
)

CASE_METADATA_SCHEMA_VERSION_V0_2 = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_"
    "fixture_case_v0.2"
)
REQUEST_METADATA_SCHEMA_VERSION_V0_2 = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_"
    "request_v0.2"
)
POINTER_METADATA_SCHEMA_VERSION_V0_2 = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_"
    "pointer_v0.2"
)
ARTIFACT_WRITER_CLI_METADATA_SCHEMA_VERSION_V0_2 = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_"
    "artifact_writer_cli_metadata_v0.2"
)
EXPECTED_RUNTIME_SUMMARY_SCHEMA_VERSION_V0_2 = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_"
    "expected_summary_v0.2"
)
EXPECTED_ERROR_SCHEMA_VERSION_V0_2 = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_"
    "expected_error_v0.2"
)
REQUEST_VALIDATION_SCHEMA_VERSION_V0_2 = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_"
    "fixture_contract_v0.2"
)

VALIDATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_"
    "fixture_validation_v0.2"
)
MODE = "artifact_writer_cli_integration_runtime_fixture_validation"

EXPECTED_TOTAL_CASES = 54
EXPECTED_VALID_CASES = 12
EXPECTED_INVALID_CASES = 42
JSON_FILES_PER_CASE = 6
EXPECTED_TOTAL_JSON_FILES = EXPECTED_TOTAL_CASES * JSON_FILES_PER_CASE
EXPECTED_PASS_CASES = 12
EXPECTED_USAGE_ERROR_CASES = 6
EXPECTED_FAIL_CLOSED_CASES = 35
EXPECTED_MISMATCH_CASES = 1
EXPECTED_V0_1_CASES = 30
EXPECTED_V0_2_CASES = 24
EXPECTED_PLAN_ONLY_CASES = 30
EXPECTED_ACTUAL_INVOCATION_CASES = 24
EXPECTED_RUNTIME_ACTUAL_INVOCATION_ENABLED_CASES = 24

REQUIRED_FILES = (
    CASE_METADATA_FILE,
    REQUEST_METADATA_FILE,
    POINTER_METADATA_FILE,
    ARTIFACT_WRITER_CLI_METADATA_FILE,
    EXPECTED_RUNTIME_SUMMARY_FILE,
    EXPECTED_ERROR_FILE,
)

VALID_CASE_LABELS = frozenset(
    {
        "valid/valid_minimal_metadata_runtime_pass",
        "valid/valid_suppressed_artifact_writer_summary_pass",
        "valid/valid_safe_relative_repo_path_pass",
        "valid/valid_file_writing_disabled_pass",
        "valid/valid_no_oracle_flags_pass",
        "valid/valid_fail_safe_suppression_flags_pass",
        "valid/valid_actual_invocation_minimal_metadata_only",
        "valid/valid_actual_invocation_body_free_output",
        "valid/valid_actual_invocation_nonzero_exit_safe_summary",
        "valid/valid_actual_invocation_timeout_safe_summary",
        "valid/valid_actual_invocation_file_writing_disabled",
        "valid/valid_actual_invocation_no_downstream_invocation",
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
    "invalid/invalid_unsupported_schema_version": "unsupported_schema_version",
    "invalid/invalid_ambiguous_file_writing_target": (
        "ambiguous_file_writing_target"
    ),
    "invalid/invalid_unexpected_manifest_writer_request": (
        "unexpected_manifest_writer_request"
    ),
    "invalid/invalid_unexpected_artifact_body_generation_request": (
        "unexpected_artifact_body_generation_request"
    ),
    "invalid/invalid_unsafe_output_residue_risk": "unsafe_output_residue_risk",
    "invalid/invalid_missing_required_metadata_file": (
        "missing_required_metadata_file"
    ),
    "invalid/invalid_mismatched_expected_status": "mismatched_expected_status",
    "invalid/invalid_duplicate_case_id": "duplicate_case_id",
    "invalid/invalid_actual_invocation_raw_stdout_body": "raw_stdout_body_present",
    "invalid/invalid_actual_invocation_raw_stderr_body": "raw_stderr_body_present",
    "invalid/invalid_actual_invocation_artifact_body_payload": (
        "artifact_body_payload_present"
    ),
    "invalid/invalid_actual_invocation_manifest_body": "manifest_body_present",
    "invalid/invalid_actual_invocation_generated_policy_body": (
        "generated_policy_body_present"
    ),
    "invalid/invalid_actual_invocation_request_body": "request_body_present",
    "invalid/invalid_actual_invocation_pointer_body": "pointer_body_present",
    "invalid/invalid_actual_invocation_expected_body": "expected_body_present",
    "invalid/invalid_actual_invocation_private_path": "private_path_present",
    "invalid/invalid_actual_invocation_absolute_path": "absolute_path_present",
    "invalid/invalid_actual_invocation_raw_learner_text": "raw_learner_text_present",
    "invalid/invalid_actual_invocation_raw_rows": "raw_rows_present",
    "invalid/invalid_actual_invocation_logits": "logits_present",
    "invalid/invalid_actual_invocation_file_writing_detected": (
        "file_writing_detected"
    ),
    "invalid/invalid_actual_invocation_artifact_body_generation_invoked": (
        "artifact_body_generation_invoked"
    ),
    "invalid/invalid_actual_invocation_manifest_writer_invoked": (
        "manifest_writer_invoked"
    ),
    "invalid/invalid_actual_invocation_unsupported_schema": (
        "unsupported_schema_version"
    ),
    "invalid/invalid_actual_invocation_mismatched_expected_status": (
        "mismatched_expected_status"
    ),
}
ALLOWED_REASON_CODES = frozenset(EXPECTED_INVALID_REASONS.values()) | {"none"}

EXPECTED_STATUS_COUNTS = {
    "pass": EXPECTED_PASS_CASES,
    "usage_error": EXPECTED_USAGE_ERROR_CASES,
    "fail_closed": EXPECTED_FAIL_CLOSED_CASES,
    "mismatch": EXPECTED_MISMATCH_CASES,
}

REASON_FORBIDDEN_MARKERS = {
    "request_body_present": "request_body",
    "pointer_body_present": "pointer_body",
    "expected_body_present": "expected_body",
    "artifact_body_payload_present": "artifact_body_payload",
    "manifest_body_present": "manifest_body",
    "generated_policy_body_present": "generated_policy_body",
    "raw_learner_text_present": "raw_learner_text",
    "raw_rows_present": "raw_rows",
    "logits_present": "logits",
    "probabilities_present": "probabilities",
    "private_path_present": "private_path",
    "absolute_path_present": "absolute_path",
    "final_text_present": "final_text",
    "observed_after_text_present": "observed_after_text",
    "gold_label_present": "gold_label",
    "post_hoc_annotation_present": "post_hoc_annotation",
    "raw_stdout_body_present": "raw_stdout_body",
    "raw_stderr_body_present": "raw_stderr_body",
    "file_writing_detected": "file_writing",
    "artifact_body_generation_invoked": "artifact_body_generation",
    "manifest_writer_invoked": "manifest_writer",
    "unsupported_schema_version": "unsupported_schema",
}

REASON_ALLOWED_FALSE_SUMMARY_FLAGS = {
    "raw_rows_present": "no_raw_rows",
    "logits_present": "no_logits_dump",
    "private_path_present": "no_private_paths",
    "absolute_path_present": "no_absolute_paths",
    "generated_policy_body_present": "no_generated_policy_body",
    "artifact_body_payload_present": "no_artifact_body_payload",
    "manifest_body_present": "no_manifest_body",
    "request_body_present": "no_request_body",
    "pointer_body_present": "no_pointer_body",
    "expected_body_present": "no_expected_body",
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
        "release_quality_ready",
        "runtime_implementation_present",
        "validator_implemented",
    }
)

CASE_METADATA_FIELDS_V0_2 = CASE_METADATA_FIELDS | {
    "runtime_mode",
    "schema_family",
}

REQUEST_METADATA_FIELDS = frozenset(
    {
        "schema_version",
        "case_id",
        "mode",
        "validation_schema_version",
        "artifact_writer_cli_summary_mode",
        "fixture_source",
        "relative_fixture_path",
        "suppression_policy",
        "no_oracle_policy",
        "synthetic_only",
        "metadata_only",
        "file_writing_requested",
        "request_body_present",
        "expected_body_present",
        "artifact_body_payload_present",
        "manifest_body_present",
        "generated_policy_body_present",
        "final_text_present",
        "observed_after_text_present",
        "gold_label_present",
        "post_hoc_annotation_present",
        "prohibited_field_present",
        "forbidden_marker",
        "unsafe_value_stored",
    }
)

REQUEST_METADATA_FIELDS_V0_2 = REQUEST_METADATA_FIELDS | {
    "actual_invocation_requested",
    "artifact_writer_cli_module",
    "fail_closed_on_unsafe_output",
    "invocation_mode",
    "no_file_writing",
    "plan_only",
    "runtime_mode",
    "stderr_body_printed",
    "stderr_capture_enabled",
    "stdout_body_printed",
    "stdout_capture_enabled",
    "subprocess_shell_enabled",
    "summary_only",
    "timeout_category",
    "timeout_seconds",
}

POINTER_METADATA_FIELDS = frozenset(
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
        "raw_learner_text_present",
        "raw_rows_present",
        "logits_present",
        "probabilities_present",
        "private_path_present",
        "private_path_value_stored",
        "absolute_path_present",
        "absolute_path_value_stored",
        "forbidden_marker",
        "unsafe_value_stored",
    }
)

ARTIFACT_WRITER_CLI_METADATA_FIELDS = frozenset(
    {
        "schema_version",
        "case_id",
        "command_label",
        "safe_mode",
        "summary_mode",
        "expected_exit_code_category",
        "relative_fixture_pointers",
        "suppression_flags",
        "no_oracle_flags",
        "raw_output_stored",
        "full_stdout_stored",
        "full_stderr_stored",
        "artifact_body_payload_stored",
        "manifest_body_stored",
        "generated_policy_body_stored",
        "file_contents_stored",
        "manifest_writer_requested",
        "artifact_body_generation_requested",
        "ambiguous_file_writing_target",
    }
)

ARTIFACT_WRITER_CLI_METADATA_FIELDS_V0_2 = ARTIFACT_WRITER_CLI_METADATA_FIELDS | {
    "module_name",
    "raw_stderr_body_detected",
    "raw_stderr_body_value_stored",
    "raw_stdout_body_detected",
    "raw_stdout_body_value_stored",
    "unsafe_value_stored",
    "unsupported_schema_present",
}

EXPECTED_RUNTIME_SUMMARY_FIELDS = frozenset(
    {
        "schema_version",
        "case_id",
        "expected_status",
        "expected_reason_code",
        "expected_exit_code_category",
        "expected_summary_mode",
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
        "no_oracle_checked",
        "synthetic_only_checked",
        "metadata_only_checked",
        "file_writing_enabled",
        "residue_expected",
        "production_readiness_claimed",
        "real_data_readiness_claimed",
        "performance_claims_present",
        "runtime_implemented",
    }
)

EXPECTED_RUNTIME_SUMMARY_FIELDS_V0_2 = EXPECTED_RUNTIME_SUMMARY_FIELDS | {
    "actual_invocation_output_variant",
    "artifact_body_generation_invoked",
    "artifact_body_payload_detected",
    "artifact_writer_cli_exit_code_category",
    "artifact_writer_cli_invocation_planned",
    "artifact_writer_cli_invoked",
    "artifact_writer_cli_output_body_free",
    "artifact_writer_cli_output_scanned",
    "expected_body_detected",
    "file_writing_detected",
    "forbidden_marker",
    "generated_policy_body_detected",
    "invocation_mode",
    "manifest_body_detected",
    "manifest_writer_invoked",
    "prohibited_body_value_stored",
    "raw_stderr_body_detected",
    "raw_stderr_body_suppressed",
    "raw_stderr_body_value_stored",
    "raw_stdout_body_detected",
    "raw_stdout_body_suppressed",
    "raw_stdout_body_value_stored",
    "request_body_detected",
    "runtime_actual_invocation_enabled",
    "runtime_actual_invocation_fail_closed",
    "runtime_actual_invocation_safety_scan_passed",
    "summary_mode",
    "unsupported_schema_present",
}

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
        "unsafe_value_stored",
    }
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
    "no_oracle_checked",
    "synthetic_only_checked",
    "metadata_only_checked",
)

REQUEST_SENTINEL_FIELDS = frozenset(
    {
        "request_body_present",
        "expected_body_present",
        "artifact_body_payload_present",
        "manifest_body_present",
        "generated_policy_body_present",
        "final_text_present",
        "observed_after_text_present",
        "gold_label_present",
        "post_hoc_annotation_present",
    }
)

POINTER_SENTINEL_FIELDS = frozenset(
    {
        "pointer_body_present",
        "raw_learner_text_present",
        "raw_rows_present",
        "logits_present",
        "probabilities_present",
        "private_path_present",
        "absolute_path_present",
    }
)

ACTUAL_INVOCATION_ARTIFACT_SENTINEL_FIELDS = frozenset(
    {
        "raw_stdout_body_detected",
        "raw_stderr_body_detected",
        "unsupported_schema_present",
    }
)

ACTUAL_INVOCATION_SUMMARY_SENTINEL_FIELDS = frozenset(
    {
        "artifact_body_generation_invoked",
        "artifact_body_payload_detected",
        "expected_body_detected",
        "file_writing_detected",
        "generated_policy_body_detected",
        "manifest_body_detected",
        "manifest_writer_invoked",
        "raw_stderr_body_detected",
        "raw_stdout_body_detected",
        "request_body_detected",
        "unsupported_schema_present",
    }
)

ALLOWED_SENTINEL_FIELDS = (
    REQUEST_SENTINEL_FIELDS
    | POINTER_SENTINEL_FIELDS
    | ACTUAL_INVOCATION_ARTIFACT_SENTINEL_FIELDS
    | ACTUAL_INVOCATION_SUMMARY_SENTINEL_FIELDS
    | {
        "artifact_body_generation_requested",
        "manifest_writer_requested",
        "ambiguous_file_writing_target",
    }
)

FORBIDDEN_ACTUAL_KEYS = frozenset(
    {
        "request_body",
        "pointer_body",
        "expected_body",
        "written_file_json_body",
        "manifest_body",
        "manifest_json_body",
        "artifact_body_payload",
        "generated_policy_body",
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
        "performance_metric_body",
        "performance_metrics",
    }
)

LOCAL_ABSOLUTE_PATH_PATTERN = re.compile(
    r"(^|[=\s\"'])/(Users|home|private|var|tmp)/|[A-Za-z]:\\|file://|\\Users\\"
)


class ArtifactWriterCliIntegrationRuntimeFixtureValidationError(Exception):
    """Raised when fixture validation cannot be performed safely."""


@dataclass(frozen=True)
class ArtifactWriterCliIntegrationRuntimeFixtureCaseResult:
    case_id: str
    case_kind: str
    expected_status: str
    expected_reason_code: str
    expected_exit_code_category: str
    fixture_schema_family: str
    runtime_mode: str
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
            "fixture_schema_family": self.fixture_schema_family,
            "runtime_mode": self.runtime_mode,
            "matched": self.matched,
            "input_error": self.input_error,
            "mismatch_reasons": list(self.mismatch_reasons),
        }


@dataclass
class ArtifactWriterCliIntegrationRuntimeFixtureValidationSummary:
    case_results: list[ArtifactWriterCliIntegrationRuntimeFixtureCaseResult] = field(
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
    def v0_1_case_count(self) -> int:
        return sum(
            result.fixture_schema_family == "v0.1" for result in self.case_results
        )

    @property
    def v0_2_case_count(self) -> int:
        return sum(
            result.fixture_schema_family == "v0.2" for result in self.case_results
        )

    @property
    def plan_only_case_count(self) -> int:
        return sum(result.runtime_mode == "plan_only" for result in self.case_results)

    @property
    def actual_invocation_case_count(self) -> int:
        return sum(
            result.runtime_mode == "actual_invocation_metadata_only"
            for result in self.case_results
        )

    @property
    def runtime_actual_invocation_enabled_cases(self) -> int:
        return self.actual_invocation_case_count

    @property
    def all_matched(self) -> bool:
        return (
            not self.root_errors
            and self.total_cases > 0
            and self.matched_cases == self.total_cases
            and self.input_error_cases == 0
            and self.mismatched_cases == 0
        )


def discover_artifact_writer_cli_integration_runtime_fixture_cases(
    root: Path,
) -> list[Path]:
    """Return sorted case directories under valid/ and invalid/."""

    case_dirs: list[Path] = []
    for group in ("valid", "invalid"):
        group_dir = root / group
        if not group_dir.is_dir():
            continue
        case_dirs.extend(path for path in group_dir.iterdir() if path.is_dir())
    return sorted(case_dirs)


def validate_artifact_writer_cli_integration_runtime_fixture_root(
    fixture_root: str | Path = DEFAULT_FIXTURE_ROOT,
    *,
    fixture_case: str | None = None,
) -> ArtifactWriterCliIntegrationRuntimeFixtureValidationSummary:
    root = Path(fixture_root)
    root_errors: list[str] = []
    if not root.is_dir():
        root_errors.append("fixture_root_missing")
        return ArtifactWriterCliIntegrationRuntimeFixtureValidationSummary(
            root_errors=tuple(root_errors)
        )

    actual_json_files = len(list(root.rglob("*.json")))
    duplicate_case_ids = _find_duplicate_case_ids(root)
    missing_required_file_cases = 0
    if duplicate_case_ids:
        root_errors.append("duplicate_case_id_detected")

    if fixture_case:
        if _unsafe_case_selector(fixture_case):
            root_errors.append("unsafe_fixture_case_selector")
            return ArtifactWriterCliIntegrationRuntimeFixtureValidationSummary(
                root_errors=tuple(root_errors),
                actual_json_files=actual_json_files,
                duplicate_case_id_cases=len(duplicate_case_ids),
            )
        case_dirs = [root / fixture_case]
        if not case_dirs[0].is_dir():
            root_errors.append("fixture_case_missing")
            return ArtifactWriterCliIntegrationRuntimeFixtureValidationSummary(
                root_errors=tuple(root_errors),
                actual_json_files=actual_json_files,
                duplicate_case_id_cases=len(duplicate_case_ids),
            )
        actual_json_files = len(list(case_dirs[0].glob("*.json")))
    else:
        case_dirs = discover_artifact_writer_cli_integration_runtime_fixture_cases(root)
        _check_root_counts(root, case_dirs, actual_json_files, root_errors)

    case_results: list[ArtifactWriterCliIntegrationRuntimeFixtureCaseResult] = []
    reason_counts: Counter[str] = Counter()
    for case_dir in case_dirs:
        file_error = _required_file_error(case_dir)
        if file_error == "required_file_missing":
            missing_required_file_cases += 1
        result = validate_artifact_writer_cli_integration_runtime_fixture_case(case_dir)
        case_results.append(result)
        reason_counts.update([result.expected_reason_code])

    return ArtifactWriterCliIntegrationRuntimeFixtureValidationSummary(
        case_results=case_results,
        reason_code_counts=reason_counts,
        root_errors=tuple(root_errors),
        actual_json_files=actual_json_files,
        duplicate_case_id_cases=len(duplicate_case_ids),
        missing_required_file_cases=missing_required_file_cases,
    )


def validate_artifact_writer_cli_integration_runtime_fixture_case(
    case_dir: str | Path,
) -> ArtifactWriterCliIntegrationRuntimeFixtureCaseResult:
    path = Path(case_dir)
    case_id = _case_id_from_dir(path)
    case_kind = path.parent.name if path.parent.name in {"valid", "invalid"} else "unknown"

    file_error = _required_file_error(path)
    if file_error:
        return _case_input_error(path, file_error)

    try:
        case_metadata = _load_json(path / CASE_METADATA_FILE)
        request_metadata = _load_json(path / REQUEST_METADATA_FILE)
        pointer_metadata = _load_json(path / POINTER_METADATA_FILE)
        artifact_writer_cli_metadata = _load_json(path / ARTIFACT_WRITER_CLI_METADATA_FILE)
        expected_runtime_summary = _load_json(path / EXPECTED_RUNTIME_SUMMARY_FILE)
        expected_error = _load_json(path / EXPECTED_ERROR_FILE)
    except (
        OSError,
        json.JSONDecodeError,
        ArtifactWriterCliIntegrationRuntimeFixtureValidationError,
    ):
        return _case_input_error(path, "malformed_json")

    payloads = (
        case_metadata,
        request_metadata,
        pointer_metadata,
        artifact_writer_cli_metadata,
        expected_runtime_summary,
        expected_error,
    )
    fixture_schema_family = _fixture_schema_family(case_metadata)
    runtime_mode = _runtime_mode(case_metadata)
    mismatches: list[str] = []
    _validate_field_sets(
        case_metadata,
        request_metadata,
        pointer_metadata,
        artifact_writer_cli_metadata,
        expected_runtime_summary,
        expected_error,
        mismatches,
    )
    _validate_schema_and_identity(
        case_id,
        case_kind,
        case_metadata,
        request_metadata,
        pointer_metadata,
        artifact_writer_cli_metadata,
        expected_runtime_summary,
        expected_error,
        mismatches,
    )
    _validate_reason_and_status_policy(
        case_id,
        case_kind,
        case_metadata,
        expected_runtime_summary,
        expected_error,
        mismatches,
    )
    _validate_no_oracle_and_suppression_policy(
        case_metadata,
        request_metadata,
        pointer_metadata,
        artifact_writer_cli_metadata,
        expected_runtime_summary,
        expected_error,
        mismatches,
    )
    _validate_file_writing_policy(
        request_metadata,
        artifact_writer_cli_metadata,
        expected_runtime_summary,
        mismatches,
    )
    _validate_artifact_body_manifest_separation(
        artifact_writer_cli_metadata,
        expected_runtime_summary,
        mismatches,
    )
    _validate_actual_invocation_metadata_only_policy(
        case_kind,
        case_metadata,
        request_metadata,
        pointer_metadata,
        artifact_writer_cli_metadata,
        expected_runtime_summary,
        mismatches,
    )
    _validate_sentinel_policy(
        case_kind,
        case_metadata,
        request_metadata,
        pointer_metadata,
        artifact_writer_cli_metadata,
        expected_runtime_summary,
        expected_error,
        mismatches,
    )
    _scan_for_forbidden_content(payloads, mismatches)

    expected_status = _string_value(expected_runtime_summary, "expected_status", "input_error")
    expected_reason = _string_value(
        expected_runtime_summary,
        "expected_reason_code",
        "input_error",
    )
    expected_exit_code = _string_value(
        expected_runtime_summary,
        "expected_exit_code_category",
        "nonzero",
    )
    return ArtifactWriterCliIntegrationRuntimeFixtureCaseResult(
        case_id=case_id,
        case_kind=case_kind,
        expected_status=expected_status,
        expected_reason_code=expected_reason,
        expected_exit_code_category=expected_exit_code,
        fixture_schema_family=fixture_schema_family,
        runtime_mode=runtime_mode,
        matched=not mismatches,
        input_error=False,
        mismatch_reasons=tuple(sorted(set(mismatches))),
    )


def summarize_artifact_writer_cli_integration_runtime_fixture_validation(
    summary: ArtifactWriterCliIntegrationRuntimeFixtureValidationSummary,
) -> dict[str, Any]:
    return {
        "mode": MODE,
        "validation_schema_version": VALIDATION_SCHEMA_VERSION,
        "fixture_root": str(DEFAULT_FIXTURE_ROOT),
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
        "v0_1_case_count": summary.v0_1_case_count,
        "v0_2_case_count": summary.v0_2_case_count,
        "plan_only_case_count": summary.plan_only_case_count,
        "actual_invocation_case_count": summary.actual_invocation_case_count,
        "runtime_actual_invocation_enabled_cases": (
            summary.runtime_actual_invocation_enabled_cases
        ),
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
        "artifact_writer_cli_integration_runtime_checked": True,
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
    request_metadata: Mapping[str, Any],
    pointer_metadata: Mapping[str, Any],
    artifact_writer_cli_metadata: Mapping[str, Any],
    expected_runtime_summary: Mapping[str, Any],
    expected_error: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    schema_family = _fixture_schema_family(case_metadata)
    if schema_family == "v0.2":
        case_fields = CASE_METADATA_FIELDS_V0_2
        request_fields = REQUEST_METADATA_FIELDS_V0_2
        pointer_fields = POINTER_METADATA_FIELDS
        artifact_fields = ARTIFACT_WRITER_CLI_METADATA_FIELDS_V0_2
        summary_fields = EXPECTED_RUNTIME_SUMMARY_FIELDS_V0_2
    else:
        case_fields = CASE_METADATA_FIELDS
        request_fields = REQUEST_METADATA_FIELDS
        pointer_fields = POINTER_METADATA_FIELDS
        artifact_fields = ARTIFACT_WRITER_CLI_METADATA_FIELDS
        summary_fields = EXPECTED_RUNTIME_SUMMARY_FIELDS

    _field_set(case_metadata, case_fields, "case_metadata", mismatches)
    _field_set(request_metadata, request_fields, "request_metadata", mismatches)
    _field_set(pointer_metadata, pointer_fields, "pointer_metadata", mismatches)
    _field_set(
        artifact_writer_cli_metadata,
        artifact_fields,
        "artifact_writer_cli_metadata",
        mismatches,
    )
    _field_set(
        expected_runtime_summary,
        summary_fields,
        "expected_runtime_summary",
        mismatches,
    )
    _field_set(expected_error, EXPECTED_ERROR_FIELDS, "expected_error", mismatches)


def _validate_schema_and_identity(
    case_id: str,
    case_kind: str,
    case_metadata: Mapping[str, Any],
    request_metadata: Mapping[str, Any],
    pointer_metadata: Mapping[str, Any],
    artifact_writer_cli_metadata: Mapping[str, Any],
    expected_runtime_summary: Mapping[str, Any],
    expected_error: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    schema_family = _fixture_schema_family(case_metadata)
    if schema_family == "v0.2":
        case_schema = CASE_METADATA_SCHEMA_VERSION_V0_2
        request_schema = REQUEST_METADATA_SCHEMA_VERSION_V0_2
        pointer_schema = POINTER_METADATA_SCHEMA_VERSION_V0_2
        artifact_schema = ARTIFACT_WRITER_CLI_METADATA_SCHEMA_VERSION_V0_2
        summary_schema = EXPECTED_RUNTIME_SUMMARY_SCHEMA_VERSION_V0_2
        error_schema = EXPECTED_ERROR_SCHEMA_VERSION_V0_2
        request_validation_schema = REQUEST_VALIDATION_SCHEMA_VERSION_V0_2
    else:
        case_schema = CASE_METADATA_SCHEMA_VERSION
        request_schema = REQUEST_METADATA_SCHEMA_VERSION
        pointer_schema = POINTER_METADATA_SCHEMA_VERSION
        artifact_schema = ARTIFACT_WRITER_CLI_METADATA_SCHEMA_VERSION
        summary_schema = EXPECTED_RUNTIME_SUMMARY_SCHEMA_VERSION
        error_schema = EXPECTED_ERROR_SCHEMA_VERSION
        request_validation_schema = REQUEST_VALIDATION_SCHEMA_VERSION

    _schema(case_metadata, case_schema, "case_metadata", mismatches)
    _schema(request_metadata, request_schema, "request_metadata", mismatches)
    _schema(pointer_metadata, pointer_schema, "pointer_metadata", mismatches)
    _schema(
        artifact_writer_cli_metadata,
        artifact_schema,
        "artifact_writer_cli_metadata",
        mismatches,
    )
    _schema(
        expected_runtime_summary,
        summary_schema,
        "expected_runtime_summary",
        mismatches,
    )
    _schema(expected_error, error_schema, "expected_error", mismatches)

    for label, payload in (
        ("case_metadata", case_metadata),
        ("request_metadata", request_metadata),
        ("pointer_metadata", pointer_metadata),
        ("artifact_writer_cli_metadata", artifact_writer_cli_metadata),
        ("expected_runtime_summary", expected_runtime_summary),
        ("expected_error", expected_error),
    ):
        if payload.get("case_id") != case_id:
            mismatches.append(f"{label}_case_id_mismatch")

    if case_metadata.get("case_kind") != case_kind:
        mismatches.append("case_kind_mismatch")
    if request_metadata.get("validation_schema_version") != request_validation_schema:
        mismatches.append("request_validation_schema_version_mismatch")
    if request_metadata.get("mode") != "artifact_writer_cli_integration_runtime_fixture_contract":
        mismatches.append("request_mode_mismatch")


def _validate_reason_and_status_policy(
    case_id: str,
    case_kind: str,
    case_metadata: Mapping[str, Any],
    expected_runtime_summary: Mapping[str, Any],
    expected_error: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    expected_status = _string_value(expected_runtime_summary, "expected_status", "")
    expected_reason = _string_value(expected_runtime_summary, "expected_reason_code", "")
    expected_exit_code = _string_value(
        expected_runtime_summary,
        "expected_exit_code_category",
        "",
    )

    if expected_reason not in ALLOWED_REASON_CODES:
        mismatches.append("unknown_reason_code")
    if case_metadata.get("expected_status") != expected_status:
        mismatches.append("metadata_expected_status_mismatch")
    if case_metadata.get("expected_reason_code") != expected_reason:
        mismatches.append("metadata_expected_reason_code_mismatch")
    if case_metadata.get("expected_exit_code_category") != expected_exit_code:
        mismatches.append("metadata_expected_exit_code_mismatch")
    if expected_error.get("expected_reason_code") != expected_reason:
        mismatches.append("expected_error_reason_code_mismatch")
    if expected_error.get("expected_exit_code_category") != expected_exit_code:
        mismatches.append("expected_error_exit_code_mismatch")

    if case_kind == "valid":
        if case_id not in VALID_CASE_LABELS:
            mismatches.append("unknown_valid_case")
        if expected_status != "pass":
            mismatches.append("valid_case_status_not_pass")
        if expected_reason != "none":
            mismatches.append("valid_case_reason_not_none")
        if expected_exit_code != "zero":
            mismatches.append("valid_case_exit_code_not_zero")
        if expected_error.get("expected_error_category") != "none":
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
        if expected_error.get("expected_error_category") != expected_status:
            mismatches.append("expected_error_category_status_mismatch")
    else:
        mismatches.append("case_kind_unknown")

    if expected_status == "pass":
        if expected_error.get("fail_closed") is not False:
            mismatches.append("pass_case_fail_closed_not_false")
        if expected_error.get("usage_error") is not False:
            mismatches.append("pass_case_usage_error_not_false")
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
        if expected_error.get("fail_closed") is not False:
            mismatches.append("mismatch_fail_closed_not_false")
        if expected_error.get("usage_error") is not False:
            mismatches.append("mismatch_usage_error_not_false")
    else:
        mismatches.append("unknown_expected_status")


def _validate_no_oracle_and_suppression_policy(
    case_metadata: Mapping[str, Any],
    request_metadata: Mapping[str, Any],
    pointer_metadata: Mapping[str, Any],
    artifact_writer_cli_metadata: Mapping[str, Any],
    expected_runtime_summary: Mapping[str, Any],
    expected_error: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    for label, payload, required in (
        ("case_metadata", case_metadata, ("synthetic_only", "metadata_only", "no_oracle")),
        ("request_metadata", request_metadata, ("synthetic_only", "metadata_only")),
        ("pointer_metadata", pointer_metadata, ("metadata_only",)),
    ):
        for field_name in required:
            if payload.get(field_name) is not True:
                mismatches.append(f"{label}_{field_name}_not_true")

    if case_metadata.get("content_suppressed") is not True:
        mismatches.append("case_metadata_content_suppressed_not_true")
    if case_metadata.get("body_suppressed") is not True:
        mismatches.append("case_metadata_body_suppressed_not_true")
    allowed_false_summary_flag = None
    if _fixture_schema_family(case_metadata) == "v0.2":
        reason = _string_value(expected_runtime_summary, "expected_reason_code", "")
        allowed_false_summary_flag = REASON_ALLOWED_FALSE_SUMMARY_FLAGS.get(reason)
    for field_name in TRUE_SUMMARY_FLAGS:
        if (
            expected_runtime_summary.get(field_name) is not True
            and field_name != allowed_false_summary_flag
        ):
            mismatches.append(f"expected_runtime_summary_{field_name}_not_true")
    if expected_runtime_summary.get("production_readiness_claimed") is not False:
        mismatches.append("production_readiness_claimed_not_false")
    if expected_runtime_summary.get("real_data_readiness_claimed") is not False:
        mismatches.append("real_data_readiness_claimed_not_false")
    if expected_runtime_summary.get("performance_claims_present") is not False:
        mismatches.append("performance_claims_present_not_false")
    if expected_runtime_summary.get("runtime_implemented") is not False:
        mismatches.append("runtime_implemented_not_false")
    if case_metadata.get("runtime_implementation_present") is not False:
        mismatches.append("runtime_implementation_present_not_false")
    if case_metadata.get("validator_implemented") is not False:
        mismatches.append("validator_implemented_not_false")
    if case_metadata.get("release_quality_ready") is not False:
        mismatches.append("release_quality_ready_not_false")
    if expected_error.get("public_safe_error") is not True:
        mismatches.append("public_safe_error_not_true")
    if expected_error.get("error_body_suppressed") is not True:
        mismatches.append("error_body_suppressed_not_true")
    if expected_error.get("raw_content_suppressed") is not True:
        mismatches.append("raw_content_suppressed_not_true")
    if expected_error.get("unsafe_value_stored") is not False:
        mismatches.append("expected_error_unsafe_value_stored_not_false")

    suppression_flags = artifact_writer_cli_metadata.get("suppression_flags")
    if not isinstance(suppression_flags, Mapping):
        mismatches.append("suppression_flags_not_object")
    else:
        for field_name in (
            "content_suppressed",
            "body_suppressed",
            "artifact_body_suppressed",
            "manifest_body_suppressed",
        ):
            if suppression_flags.get(field_name) is not True:
                mismatches.append(f"suppression_flag_{field_name}_not_true")

    no_oracle_flags = artifact_writer_cli_metadata.get("no_oracle_flags")
    if not isinstance(no_oracle_flags, Mapping):
        mismatches.append("no_oracle_flags_not_object")
    else:
        for field_name in (
            "synthetic_only_checked",
            "metadata_only_checked",
            "no_oracle_checked",
        ):
            if no_oracle_flags.get(field_name) is not True:
                mismatches.append(f"no_oracle_flag_{field_name}_not_true")


def _validate_file_writing_policy(
    request_metadata: Mapping[str, Any],
    artifact_writer_cli_metadata: Mapping[str, Any],
    expected_runtime_summary: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    reason = _string_value(expected_runtime_summary, "expected_reason_code", "")
    if (
        request_metadata.get("file_writing_requested") is not False
        and reason != "file_writing_detected"
    ):
        mismatches.append("file_writing_requested_not_false")
    if expected_runtime_summary.get("file_writing_enabled") is not False:
        mismatches.append("file_writing_enabled_not_false")
    if (
        expected_runtime_summary.get("residue_expected") is not False
        and reason != "unsafe_output_residue_risk"
    ):
        mismatches.append("residue_expected_not_false")
    if artifact_writer_cli_metadata.get("file_contents_stored") is not False:
        mismatches.append("file_contents_stored_not_false")


def _validate_artifact_body_manifest_separation(
    artifact_writer_cli_metadata: Mapping[str, Any],
    expected_runtime_summary: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    reason = _string_value(expected_runtime_summary, "expected_reason_code", "")
    if artifact_writer_cli_metadata.get("artifact_body_generation_requested") is not False:
        if reason not in {
            "unexpected_artifact_body_generation_request",
            "artifact_body_generation_invoked",
        }:
            mismatches.append("artifact_body_generation_requested_not_false")
    if artifact_writer_cli_metadata.get("manifest_writer_requested") is not False:
        if reason not in {
            "unexpected_manifest_writer_request",
            "manifest_writer_invoked",
        }:
            mismatches.append("manifest_writer_requested_not_false")
    if artifact_writer_cli_metadata.get("artifact_body_payload_stored") is not False:
        mismatches.append("artifact_body_payload_stored_not_false")
    if artifact_writer_cli_metadata.get("manifest_body_stored") is not False:
        mismatches.append("manifest_body_stored_not_false")
    if artifact_writer_cli_metadata.get("generated_policy_body_stored") is not False:
        mismatches.append("generated_policy_body_stored_not_false")
    if artifact_writer_cli_metadata.get("raw_output_stored") is not False:
        mismatches.append("raw_output_stored_not_false")
    if artifact_writer_cli_metadata.get("full_stdout_stored") is not False:
        mismatches.append("full_stdout_stored_not_false")
    if artifact_writer_cli_metadata.get("full_stderr_stored") is not False:
        mismatches.append("full_stderr_stored_not_false")


def _validate_actual_invocation_metadata_only_policy(
    case_kind: str,
    case_metadata: Mapping[str, Any],
    request_metadata: Mapping[str, Any],
    pointer_metadata: Mapping[str, Any],
    artifact_writer_cli_metadata: Mapping[str, Any],
    expected_runtime_summary: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    if _fixture_schema_family(case_metadata) != "v0.2":
        return

    reason = _string_value(expected_runtime_summary, "expected_reason_code", "")
    expected_status = _string_value(expected_runtime_summary, "expected_status", "")

    if case_metadata.get("runtime_mode") != "actual_invocation_metadata_only":
        mismatches.append("case_metadata_runtime_mode_mismatch")
    if request_metadata.get("runtime_mode") != "actual_invocation_metadata_only":
        mismatches.append("request_runtime_mode_mismatch")
    if request_metadata.get("invocation_mode") != "actual_invocation_metadata_only":
        mismatches.append("request_invocation_mode_mismatch")
    if expected_runtime_summary.get("invocation_mode") != "actual_invocation_metadata_only":
        mismatches.append("summary_invocation_mode_mismatch")
    if request_metadata.get("actual_invocation_requested") is not True:
        mismatches.append("actual_invocation_requested_not_true")
    if request_metadata.get("plan_only") is not False:
        mismatches.append("plan_only_not_false")
    if request_metadata.get("summary_only") is not True:
        mismatches.append("summary_only_not_true")
    if request_metadata.get("no_file_writing") is not True:
        if reason != "file_writing_detected":
            mismatches.append("no_file_writing_not_true")
    if request_metadata.get("fail_closed_on_unsafe_output") is not True:
        mismatches.append("fail_closed_on_unsafe_output_not_true")
    if request_metadata.get("subprocess_shell_enabled") is not False:
        mismatches.append("subprocess_shell_enabled_not_false")
    if request_metadata.get("stdout_capture_enabled") is not True:
        mismatches.append("stdout_capture_enabled_not_true")
    if request_metadata.get("stderr_capture_enabled") is not True:
        mismatches.append("stderr_capture_enabled_not_true")
    if request_metadata.get("stdout_body_printed") is not False:
        mismatches.append("stdout_body_printed_not_false")
    if request_metadata.get("stderr_body_printed") is not False:
        mismatches.append("stderr_body_printed_not_false")

    if expected_runtime_summary.get("runtime_actual_invocation_enabled") is not True:
        mismatches.append("runtime_actual_invocation_enabled_not_true")
    if expected_runtime_summary.get("artifact_writer_cli_invoked") is not True:
        mismatches.append("artifact_writer_cli_invoked_not_true")
    if expected_runtime_summary.get("artifact_writer_cli_invocation_planned") is not False:
        mismatches.append("artifact_writer_cli_invocation_planned_not_false")
    if expected_runtime_summary.get("artifact_writer_cli_output_scanned") is not True:
        mismatches.append("artifact_writer_cli_output_scanned_not_true")
    if expected_runtime_summary.get("raw_stdout_body_suppressed") is not True:
        mismatches.append("raw_stdout_body_suppressed_not_true")
    if expected_runtime_summary.get("raw_stderr_body_suppressed") is not True:
        mismatches.append("raw_stderr_body_suppressed_not_true")
    if expected_runtime_summary.get("raw_stdout_body_value_stored") is not False:
        mismatches.append("raw_stdout_body_value_stored_not_false")
    if expected_runtime_summary.get("raw_stderr_body_value_stored") is not False:
        mismatches.append("raw_stderr_body_value_stored_not_false")
    if expected_runtime_summary.get("prohibited_body_value_stored") is not False:
        mismatches.append("prohibited_body_value_stored_not_false")
    if artifact_writer_cli_metadata.get("unsafe_value_stored") is not False:
        mismatches.append("artifact_writer_cli_unsafe_value_stored_not_false")
    if artifact_writer_cli_metadata.get("raw_stdout_body_value_stored") is not False:
        mismatches.append("artifact_raw_stdout_body_value_stored_not_false")
    if artifact_writer_cli_metadata.get("raw_stderr_body_value_stored") is not False:
        mismatches.append("artifact_raw_stderr_body_value_stored_not_false")

    if case_kind == "valid":
        if expected_runtime_summary.get("artifact_writer_cli_output_body_free") is not True:
            mismatches.append("valid_actual_invocation_output_body_free_not_true")
        if expected_runtime_summary.get("runtime_actual_invocation_safety_scan_passed") is not True:
            mismatches.append("valid_actual_invocation_safety_scan_not_true")
        if expected_runtime_summary.get("runtime_actual_invocation_fail_closed") is not False:
            mismatches.append("valid_actual_invocation_fail_closed_not_false")
        if expected_runtime_summary.get("file_writing_detected") is not False:
            mismatches.append("valid_file_writing_detected_not_false")
        if expected_runtime_summary.get("artifact_body_generation_invoked") is not False:
            mismatches.append("valid_artifact_body_generation_invoked_not_false")
        if expected_runtime_summary.get("manifest_writer_invoked") is not False:
            mismatches.append("valid_manifest_writer_invoked_not_false")
        if _summary_true_sentinels(expected_runtime_summary):
            mismatches.append("valid_actual_invocation_summary_sentinel_present")
    elif expected_status in {"fail_closed", "usage_error", "mismatch"}:
        if expected_runtime_summary.get("runtime_actual_invocation_safety_scan_passed") is not False:
            mismatches.append("invalid_actual_invocation_safety_scan_not_false")
        if reason not in {"unsupported_schema_version", "mismatched_expected_status"}:
            if expected_runtime_summary.get("runtime_actual_invocation_fail_closed") is not True:
                mismatches.append("invalid_actual_invocation_fail_closed_not_true")

    for label, value in (
        ("request_relative_fixture_path", request_metadata.get("relative_fixture_path")),
        ("pointer_relative_fixture_path", pointer_metadata.get("relative_fixture_path")),
        ("pointer_relative_repo_path", pointer_metadata.get("relative_repo_path")),
    ):
        if not isinstance(value, str) or _unsafe_metadata_path(value):
            mismatches.append(f"{label}_unsafe")


def _validate_sentinel_policy(
    case_kind: str,
    case_metadata: Mapping[str, Any],
    request_metadata: Mapping[str, Any],
    pointer_metadata: Mapping[str, Any],
    artifact_writer_cli_metadata: Mapping[str, Any],
    expected_runtime_summary: Mapping[str, Any],
    expected_error: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    reason = _string_value(case_metadata, "expected_reason_code", "")
    marker = _string_value(case_metadata, "forbidden_marker", "")
    if case_kind == "valid":
        if marker != "none":
            mismatches.append("valid_case_forbidden_marker_not_none")
    elif (
        marker
        != (
            REASON_FORBIDDEN_MARKERS.get(reason, reason)
            if _fixture_schema_family(case_metadata) == "v0.2"
            else reason
        )
    ):
        mismatches.append("forbidden_marker_reason_mismatch")

    if expected_error.get("unsafe_value_stored") is not False:
        mismatches.append("unsafe_value_stored_not_false")
    if request_metadata.get("unsafe_value_stored") is not False:
        mismatches.append("request_unsafe_value_stored_not_false")
    if pointer_metadata.get("unsafe_value_stored") is not False:
        mismatches.append("pointer_unsafe_value_stored_not_false")
    if pointer_metadata.get("absolute_paths_allowed") is not False:
        mismatches.append("absolute_paths_allowed_not_false")
    if pointer_metadata.get("private_paths_allowed") is not False:
        mismatches.append("private_paths_allowed_not_false")
    if pointer_metadata.get("absolute_path_value_stored") is not False:
        mismatches.append("absolute_path_value_stored_not_false")
    if pointer_metadata.get("private_path_value_stored") is not False:
        mismatches.append("private_path_value_stored_not_false")

    sentinel_sources = {
        **{field_name: request_metadata.get(field_name) for field_name in REQUEST_SENTINEL_FIELDS},
        **{field_name: pointer_metadata.get(field_name) for field_name in POINTER_SENTINEL_FIELDS},
        "artifact_body_generation_requested": artifact_writer_cli_metadata.get(
            "artifact_body_generation_requested"
        ),
        "manifest_writer_requested": artifact_writer_cli_metadata.get(
            "manifest_writer_requested"
        ),
        "ambiguous_file_writing_target": artifact_writer_cli_metadata.get(
            "ambiguous_file_writing_target"
        ),
        **{
            field_name: artifact_writer_cli_metadata.get(field_name)
            for field_name in ACTUAL_INVOCATION_ARTIFACT_SENTINEL_FIELDS
        },
        **{
            field_name: expected_runtime_summary.get(field_name)
            for field_name in ACTUAL_INVOCATION_SUMMARY_SENTINEL_FIELDS
        },
    }
    true_sentinels = {key for key, value in sentinel_sources.items() if value is True}
    if case_kind == "valid" and true_sentinels:
        mismatches.append("valid_case_sentinel_present")
    schema_family = _fixture_schema_family(case_metadata)
    expected_sentinel = {
        "unexpected_artifact_body_generation_request": (
            "artifact_body_generation_requested"
        ),
        "unexpected_manifest_writer_request": "manifest_writer_requested",
    }.get(reason, reason)
    if schema_family == "v0.2":
        expected_sentinel = {
            "raw_stdout_body_present": "raw_stdout_body_detected",
            "raw_stderr_body_present": "raw_stderr_body_detected",
            "file_writing_detected": "file_writing_detected",
            "artifact_body_generation_invoked": "artifact_body_generation_invoked",
            "manifest_writer_invoked": "manifest_writer_invoked",
            "unsupported_schema_version": "unsupported_schema_present",
        }.get(reason, expected_sentinel)
    if case_kind == "invalid" and expected_sentinel in ALLOWED_SENTINEL_FIELDS:
        if expected_sentinel not in true_sentinels:
            mismatches.append("expected_sentinel_not_present")
    if case_kind == "invalid" and reason not in {"none", *ALLOWED_SENTINEL_FIELDS}:
        if true_sentinels and expected_sentinel not in true_sentinels:
            mismatches.append("unexpected_sentinel_present")
    if request_metadata.get("prohibited_field_present") is True:
        if case_kind != "invalid" or reason == "none":
            mismatches.append("prohibited_field_present_unexpected")
    elif case_kind == "invalid" and reason != "none":
        mismatches.append("prohibited_field_present_missing")


def _scan_for_forbidden_content(
    payloads: Sequence[Mapping[str, Any]],
    mismatches: list[str],
) -> None:
    for payload in payloads:
        _scan_value(payload, mismatches)


def _fixture_schema_family(case_metadata: Mapping[str, Any]) -> str:
    schema_version = case_metadata.get("schema_version")
    if schema_version == CASE_METADATA_SCHEMA_VERSION:
        return "v0.1"
    if schema_version == CASE_METADATA_SCHEMA_VERSION_V0_2:
        return "v0.2"
    return "unknown"


def _runtime_mode(case_metadata: Mapping[str, Any]) -> str:
    if _fixture_schema_family(case_metadata) == "v0.2":
        value = case_metadata.get("runtime_mode")
        return value if isinstance(value, str) else "unknown"
    return "plan_only"


def _summary_true_sentinels(
    expected_runtime_summary: Mapping[str, Any],
) -> set[str]:
    return {
        field_name
        for field_name in ACTUAL_INVOCATION_SUMMARY_SENTINEL_FIELDS
        if expected_runtime_summary.get(field_name) is True
    }


def _unsafe_metadata_path(value: str) -> bool:
    private_markers = (
        "/",
        "~",
        "file://",
        "\\",
        "s3://",
        "gs://",
        "az://",
        ".ssh",
        ".aws",
        ".config",
    )
    parts = value.split("/")
    return (
        not value
        or value.startswith(private_markers)
        or ".." in parts
        or LOCAL_ABSOLUTE_PATH_PATTERN.search(value) is not None
    )


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
        if LOCAL_ABSOLUTE_PATH_PATTERN.search(value) or value.startswith(("~", "/")):
            mismatches.append("actual_absolute_or_private_path")
        lowered = value.lower()
        if "real participant" in lowered:
            mismatches.append("real_participant_marker")


def _is_forbidden_actual_key(key: str) -> bool:
    if key in FORBIDDEN_ACTUAL_KEYS:
        return True
    if key.startswith("no_"):
        return False
    if key.endswith("_present") or key.endswith("_stored"):
        return False
    if key in {"forbidden_marker", "prohibited_field_present"}:
        return False
    return False


def _load_json(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ArtifactWriterCliIntegrationRuntimeFixtureValidationError(
            "json_root_not_object"
        )
    return payload


def _case_id_from_dir(case_dir: Path) -> str:
    return f"{case_dir.parent.name}/{case_dir.name}"


def _case_input_error(
    case_dir: Path,
    reason: str,
) -> ArtifactWriterCliIntegrationRuntimeFixtureCaseResult:
    case_kind = case_dir.parent.name
    if case_kind not in {"valid", "invalid"}:
        case_kind = "unknown"
    return ArtifactWriterCliIntegrationRuntimeFixtureCaseResult(
        case_id=_case_id_from_dir(case_dir),
        case_kind=case_kind,
        expected_status="input_error",
        expected_reason_code=reason,
        expected_exit_code_category="nonzero",
        fixture_schema_family="unknown",
        runtime_mode="unknown",
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
        except (OSError, json.JSONDecodeError, ArtifactWriterCliIntegrationRuntimeFixtureValidationError):
            continue
        case_id = payload.get("case_id")
        if not isinstance(case_id, str):
            continue
        if case_id in seen:
            duplicate.add(case_id)
        seen.add(case_id)
    return duplicate


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
            "Validate synthetic metadata-only artifact writer CLI integration "
            "runtime fixture contracts."
        )
    )
    parser.add_argument(
        "--fixture-root",
        default=str(DEFAULT_FIXTURE_ROOT),
        help="Fixture root to validate.",
    )
    parser.add_argument(
        "--fixture-case",
        help="Optional safe relative case id such as valid/valid_minimal_metadata_runtime_pass.",
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

    summary = validate_artifact_writer_cli_integration_runtime_fixture_root(
        args.fixture_root,
        fixture_case=args.fixture_case,
    )
    payload = summarize_artifact_writer_cli_integration_runtime_fixture_validation(
        summary
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        _print_human_summary(payload)
    return 0 if summary.all_matched else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
