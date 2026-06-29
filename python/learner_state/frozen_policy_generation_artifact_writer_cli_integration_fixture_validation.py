"""Static validation for artifact writer CLI integration fixtures.

This validator checks synthetic metadata-only fixture contracts. It does not
execute artifact writer CLI integration, connect artifact body generation,
connect the manifest writer, write files, train models, or compute metrics.
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
GENERATOR_REQUEST_FILE = "generator_request.json"
GENERATOR_INPUT_POINTER_FILE = "generator_input_fixture_pointer.json"
ARTIFACT_WRITER_REQUEST_FILE = "artifact_writer_request.json"
GENERATOR_RESULT_POINTER_FILE = "generator_result_pointer.json"
EXPECTED_RESULT_FILE = "expected_artifact_writer_cli_integration_result.json"

DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration"
)

CASE_METADATA_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_"
    "case_metadata_v0.1"
)
GENERATOR_REQUEST_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_generator_cli_integration_request_v0.1"
)
GENERATOR_INPUT_POINTER_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_generator_input_fixture_pointer_v0.1"
)
ARTIFACT_WRITER_REQUEST_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_"
    "artifact_writer_cli_integration_request_v0.1"
)
GENERATOR_RESULT_POINTER_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_generator_result_pointer_v0.1"
)
GENERATOR_RESULT_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_generator_scaffold_result_v0.1"
)
EXPECTED_RESULT_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_"
    "result_v0.1"
)
VALIDATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_"
    "fixture_validation_v0.1"
)

MODE = "artifact_writer_cli_integration_fixture_validation"
INTEGRATION_STEP = "generator_scaffold_to_artifact_writer"
JSON_FILES_PER_CASE = 6

EXPECTED_TOTAL_CASES = 28
EXPECTED_VALID_CASES = 6
EXPECTED_INVALID_CASES = 22
EXPECTED_TOTAL_JSON_FILES = EXPECTED_TOTAL_CASES * JSON_FILES_PER_CASE
EXPECTED_PASS_CASES = 6
EXPECTED_USAGE_ERROR_CASES = 9
EXPECTED_FAIL_CLOSED_CASES = 13

REQUIRED_FILES = (
    CASE_METADATA_FILE,
    GENERATOR_REQUEST_FILE,
    GENERATOR_INPUT_POINTER_FILE,
    ARTIFACT_WRITER_REQUEST_FILE,
    GENERATOR_RESULT_POINTER_FILE,
    EXPECTED_RESULT_FILE,
)

CASE_METADATA_FIELDS = frozenset(
    {
        "schema_version",
        "case_id",
        "case_group",
        "expected_status",
        "expected_reason_codes",
        "integration_step",
        "synthetic_only",
        "no_oracle",
        "metadata_only",
        "body_free",
        "artifact_body_generation_expected",
        "manifest_writer_expected",
        "file_writing_expected",
        "release_quality_ready",
        "safe_marker_policy",
    }
)

GENERATOR_REQUEST_FIELDS = frozenset(
    {
        "schema_version",
        "request_id",
        "generator_version",
        "synthetic_only_notice",
        "no_oracle_notice",
        "validation_reference_ids",
        "release_quality_reference_ids",
        "body_suppressed",
        "content_suppressed",
        "file_writing_allowed",
    }
)

GENERATOR_INPUT_POINTER_FIELDS = frozenset(
    {
        "schema_version",
        "pointer_id",
        "fixture_reference_id",
        "validation_status",
        "synthetic_only",
        "no_oracle",
        "body_suppressed",
        "content_suppressed",
    }
)

ARTIFACT_WRITER_REQUEST_FIELDS = frozenset(
    {
        "schema_version",
        "request_id",
        "artifact_writer_version",
        "synthetic_only_notice",
        "no_oracle_notice",
        "body_suppressed",
        "artifact_body_suppressed",
        "manifest_body_suppressed",
        "file_writing_allowed",
        "artifact_body_generation_requested",
        "manifest_writer_requested",
        "release_quality_ready",
    }
)

GENERATOR_RESULT_POINTER_FIELDS = frozenset(
    {
        "schema_version",
        "pointer_id",
        "generator_result_schema_version",
        "generation_status",
        "validation_status",
        "generator_scaffold_executed",
        "generated_artifact_written",
        "generated_artifact_body_available",
        "artifact_file_path_available",
        "body_suppressed",
        "content_suppressed",
        "no_raw_rows",
        "no_logits_dump",
        "no_private_paths",
        "no_generated_policy_body",
        "synthetic_only_checked",
        "no_oracle_checked",
    }
)

EXPECTED_RESULT_FIELDS = frozenset(
    {
        "schema_version",
        "case_id",
        "mode",
        "integration_status",
        "expected_reason_codes",
        "integration_step",
        "generator_scaffold_executed",
        "artifact_writer_executed",
        "artifact_body_generation_executed",
        "manifest_writer_executed",
        "generated_artifact_written",
        "artifact_file_written",
        "manifest_file_written",
        "written_file_count",
        "artifact_body_available",
        "generated_artifact_body_available",
        "manifest_body_available",
        "body_suppressed",
        "artifact_body_suppressed",
        "manifest_body_suppressed",
        "content_suppressed",
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
        "no_performance_claims",
        "synthetic_only_checked",
        "no_oracle_checked",
        "file_writing_checked",
        "artifact_writer_cli_integration_checked",
        "release_quality_ready",
        "count_summary",
        "safe_summary",
    }
)

VALID_CASE_LABELS = frozenset(
    {
        "valid/minimal_generator_to_artifact_writer_metadata_only",
        "valid/generator_with_validation_references_metadata_only",
        "valid/generator_with_release_quality_reference_metadata_only",
        "valid/artifact_writer_preserves_safe_ids_metadata_only",
        "valid/no_file_writing_default_metadata_only",
        "valid/body_suppressed_metadata_only",
    }
)

EXPECTED_INVALID_REASONS = {
    "invalid/missing_generator_request": "missing_generator_request",
    "invalid/missing_generator_input_pointer": "missing_generator_input_pointer",
    "invalid/missing_artifact_writer_request": "missing_artifact_writer_request",
    "invalid/missing_generator_result_pointer": "missing_generator_result_pointer",
    "invalid/malformed_generator_result_pointer": "malformed_generator_result_pointer",
    "invalid/unknown_generator_result_schema": "unknown_generator_result_schema",
    "invalid/unvalidated_generator_result": "unvalidated_generator_result",
    "invalid/generated_policy_body_leakage": "generated_policy_body_leakage",
    "invalid/artifact_body_payload_leakage": "artifact_body_payload_leakage",
    "invalid/manifest_body_leakage": "manifest_body_leakage",
    "invalid/request_body_leakage": "request_body_leakage",
    "invalid/pointer_body_leakage": "pointer_body_leakage",
    "invalid/raw_rows_leakage": "raw_rows_leakage",
    "invalid/logits_dump_leakage": "logits_dump_leakage",
    "invalid/private_path_leakage": "private_path_leakage",
    "invalid/absolute_path_leakage": "absolute_path_leakage",
    "invalid/raw_learner_text_leakage": "raw_learner_text_leakage",
    "invalid/performance_claim_in_artifact": "performance_claim_in_artifact",
    "invalid/non_synthetic_input": "non_synthetic_input",
    "invalid/no_oracle_violation": "no_oracle_violation",
    "invalid/unsupported_file_writing_mode": "unsupported_file_writing_mode",
    "invalid/unsupported_artifact_body_generation_integration": (
        "unsupported_artifact_body_generation_integration"
    ),
}

ALLOWED_REASON_CODES = frozenset(EXPECTED_INVALID_REASONS.values())

EXPECTED_STATUS_COUNTS = {
    "pass": EXPECTED_PASS_CASES,
    "usage_error": EXPECTED_USAGE_ERROR_CASES,
    "fail_closed": EXPECTED_FAIL_CLOSED_CASES,
}

ZERO_COUNTER_FIELDS = (
    "body_field_count",
    "raw_row_count",
    "logits_dump_count",
    "private_path_count",
    "absolute_path_count",
    "performance_metric_count",
    "written_file_count",
)

BOOLEAN_TRUE_EXPECTED_FIELDS = (
    "body_suppressed",
    "artifact_body_suppressed",
    "manifest_body_suppressed",
    "content_suppressed",
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
    "no_performance_claims",
    "synthetic_only_checked",
    "no_oracle_checked",
    "file_writing_checked",
    "artifact_writer_cli_integration_checked",
)

FORBIDDEN_ACTUAL_KEYS = frozenset(
    {
        "raw_learner_text",
        "raw_rows",
        "logits",
        "probabilities",
        "generated_policy_body",
        "artifact_body_payload",
        "artifact_body",
        "manifest_body",
        "manifest_json_body",
        "request_body",
        "pointer_body",
        "expected_body",
        "expected_result_body",
        "private_path",
        "absolute_path",
        "performance_metric_body",
        "performance_metrics",
        "real_participant_data",
        "final_text",
        "observed_after_text",
        "gold_label",
        "gold_labels",
        "scoring_feedback",
        "scoring_feedback_payload",
        "post_hoc_annotation",
        "test_tuning_payload",
    }
)

SAFE_MARKER_SUFFIXES = ("_marker", "_leakage_marker")
LOCAL_ABSOLUTE_PATH_PATTERN = re.compile(
    r"(^|[=\s\"'])/(Users|home|private|var|tmp)/|[A-Za-z]:\\|file://|\\Users\\"
)


class ArtifactWriterCliIntegrationFixtureValidationError(Exception):
    """Raised when fixture validation cannot be performed safely."""


@dataclass(frozen=True)
class ArtifactWriterCliIntegrationFixtureCaseResult:
    case_id: str
    case_group: str
    integration_status: str
    reason_codes: tuple[str, ...]
    generator_scaffold_executed: bool
    artifact_writer_executed: bool
    matched: bool
    input_error: bool
    mismatch_reasons: tuple[str, ...] = ()

    @property
    def is_mismatch(self) -> bool:
        return (not self.matched) and (not self.input_error)

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "case_group": self.case_group,
            "integration_status": self.integration_status,
            "reason_codes": list(self.reason_codes),
            "generator_scaffold_executed": self.generator_scaffold_executed,
            "artifact_writer_executed": self.artifact_writer_executed,
            "matched": self.matched,
            "input_error": self.input_error,
            "mismatch_reasons": list(self.mismatch_reasons),
        }


@dataclass
class ArtifactWriterCliIntegrationFixtureValidationSummary:
    case_results: list[ArtifactWriterCliIntegrationFixtureCaseResult] = field(
        default_factory=list
    )
    reason_code_counts: Counter[str] = field(default_factory=Counter)
    root_errors: tuple[str, ...] = ()
    actual_json_files: int = 0

    @property
    def total_cases(self) -> int:
        return len(self.case_results)

    @property
    def valid_cases(self) -> int:
        return sum(result.case_group == "valid" for result in self.case_results)

    @property
    def invalid_cases(self) -> int:
        return sum(result.case_group == "invalid" for result in self.case_results)

    @property
    def total_json_files(self) -> int:
        return self.actual_json_files

    @property
    def pass_cases(self) -> int:
        return sum(result.integration_status == "pass" for result in self.case_results)

    @property
    def usage_error_cases(self) -> int:
        return sum(
            result.integration_status == "usage_error" for result in self.case_results
        )

    @property
    def fail_closed_cases(self) -> int:
        return sum(
            result.integration_status == "fail_closed" for result in self.case_results
        )

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
    def all_matched(self) -> bool:
        return (
            not self.root_errors
            and self.total_cases > 0
            and self.matched_cases == self.total_cases
            and self.input_error_cases == 0
            and self.mismatched_cases == 0
        )


def discover_artifact_writer_cli_integration_fixture_cases(root: Path) -> list[Path]:
    """Return sorted case directories under valid/ and invalid/."""

    case_dirs: list[Path] = []
    for group in ("valid", "invalid"):
        group_dir = root / group
        if not group_dir.is_dir():
            continue
        case_dirs.extend(path for path in group_dir.iterdir() if path.is_dir())
    return sorted(case_dirs)


def validate_artifact_writer_cli_integration_fixture_root(
    fixture_root: str | Path = DEFAULT_FIXTURE_ROOT,
    *,
    fixture_case: str | None = None,
) -> ArtifactWriterCliIntegrationFixtureValidationSummary:
    root = Path(fixture_root)
    root_errors: list[str] = []
    if not root.is_dir():
        root_errors.append("fixture_root_missing")
        return ArtifactWriterCliIntegrationFixtureValidationSummary(
            root_errors=tuple(root_errors)
        )

    actual_json_files = len(list(root.rglob("*.json")))
    if fixture_case:
        if _unsafe_case_selector(fixture_case):
            root_errors.append("unsafe_fixture_case_selector")
            return ArtifactWriterCliIntegrationFixtureValidationSummary(
                root_errors=tuple(root_errors),
                actual_json_files=actual_json_files,
            )
        case_dirs = [root / fixture_case]
        if not case_dirs[0].is_dir():
            root_errors.append("fixture_case_missing")
            return ArtifactWriterCliIntegrationFixtureValidationSummary(
                root_errors=tuple(root_errors),
                actual_json_files=actual_json_files,
            )
        selected_json_count = len(list(case_dirs[0].glob("*.json")))
        actual_json_files = selected_json_count
    else:
        case_dirs = discover_artifact_writer_cli_integration_fixture_cases(root)
        _check_root_counts(root, case_dirs, actual_json_files, root_errors)

    case_results: list[ArtifactWriterCliIntegrationFixtureCaseResult] = []
    reason_counts: Counter[str] = Counter()
    for case_dir in case_dirs:
        result = validate_artifact_writer_cli_integration_fixture_case(case_dir)
        case_results.append(result)
        reason_counts.update(result.reason_codes)

    return ArtifactWriterCliIntegrationFixtureValidationSummary(
        case_results=case_results,
        reason_code_counts=reason_counts,
        root_errors=tuple(root_errors),
        actual_json_files=actual_json_files,
    )


def validate_artifact_writer_cli_integration_fixture_case(
    case_dir: str | Path,
) -> ArtifactWriterCliIntegrationFixtureCaseResult:
    path = Path(case_dir)
    case_id = _case_id_from_dir(path)
    case_group = path.parent.name if path.parent.name in {"valid", "invalid"} else "unknown"

    file_error = _required_file_error(path)
    if file_error:
        return _case_input_error(path, file_error)

    try:
        case_metadata = _load_json(path / CASE_METADATA_FILE)
        generator_request = _load_json(path / GENERATOR_REQUEST_FILE)
        generator_input_pointer = _load_json(path / GENERATOR_INPUT_POINTER_FILE)
        artifact_writer_request = _load_json(path / ARTIFACT_WRITER_REQUEST_FILE)
        generator_result_pointer = _load_json(path / GENERATOR_RESULT_POINTER_FILE)
        expected_result = _load_json(path / EXPECTED_RESULT_FILE)
    except (OSError, json.JSONDecodeError, ArtifactWriterCliIntegrationFixtureValidationError):
        return _case_input_error(path, "malformed_json")

    payloads = (
        case_metadata,
        generator_request,
        generator_input_pointer,
        artifact_writer_request,
        generator_result_pointer,
        expected_result,
    )
    mismatches: list[str] = []
    _validate_field_sets(
        case_metadata,
        generator_request,
        generator_input_pointer,
        artifact_writer_request,
        generator_result_pointer,
        expected_result,
        mismatches,
    )
    _validate_schema_and_identity(
        case_id,
        case_group,
        case_metadata,
        generator_request,
        generator_input_pointer,
        artifact_writer_request,
        generator_result_pointer,
        expected_result,
        mismatches,
    )
    _validate_reason_policy(case_id, case_group, case_metadata, expected_result, mismatches)
    _validate_case_rules(case_group, expected_result, mismatches)
    _validate_no_oracle_policy(case_metadata, generator_input_pointer, expected_result, mismatches)
    _validate_file_writing_policy(case_metadata, generator_request, artifact_writer_request, expected_result, mismatches)
    _validate_artifact_body_manifest_separation(case_metadata, artifact_writer_request, expected_result, mismatches)
    _scan_for_forbidden_content(payloads, mismatches)

    integration_status = _string_value(expected_result, "integration_status", "input_error")
    reason_codes = tuple(_list_of_strings(expected_result.get("expected_reason_codes")))
    return ArtifactWriterCliIntegrationFixtureCaseResult(
        case_id=case_id,
        case_group=case_group,
        integration_status=integration_status,
        reason_codes=reason_codes,
        generator_scaffold_executed=expected_result.get("generator_scaffold_executed")
        is True,
        artifact_writer_executed=expected_result.get("artifact_writer_executed") is True,
        matched=not mismatches,
        input_error=False,
        mismatch_reasons=tuple(sorted(set(mismatches))),
    )


def summarize_artifact_writer_cli_integration_fixture_validation(
    summary: ArtifactWriterCliIntegrationFixtureValidationSummary,
) -> dict[str, Any]:
    return {
        "mode": MODE,
        "validation_schema_version": VALIDATION_SCHEMA_VERSION,
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
        "no_performance_claims": True,
        "synthetic_only_checked": True,
        "no_oracle_checked": True,
        "file_writing_checked": True,
        "artifact_body_generation_integration_checked": True,
        "manifest_writer_integration_checked": True,
        "artifact_writer_cli_integration_checked": True,
        "release_quality_ready": False,
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
    generator_request: Mapping[str, Any],
    generator_input_pointer: Mapping[str, Any],
    artifact_writer_request: Mapping[str, Any],
    generator_result_pointer: Mapping[str, Any],
    expected_result: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    _field_set(case_metadata, CASE_METADATA_FIELDS, "case_metadata", mismatches)
    _field_set(generator_request, GENERATOR_REQUEST_FIELDS, "generator_request", mismatches)
    _field_set(
        generator_input_pointer,
        GENERATOR_INPUT_POINTER_FIELDS,
        "generator_input_pointer",
        mismatches,
    )
    _field_set(
        artifact_writer_request,
        ARTIFACT_WRITER_REQUEST_FIELDS,
        "artifact_writer_request",
        mismatches,
    )
    _field_set(
        generator_result_pointer,
        GENERATOR_RESULT_POINTER_FIELDS,
        "generator_result_pointer",
        mismatches,
    )
    _field_set(expected_result, EXPECTED_RESULT_FIELDS, "expected_result", mismatches)


def _validate_schema_and_identity(
    case_id: str,
    case_group: str,
    case_metadata: Mapping[str, Any],
    generator_request: Mapping[str, Any],
    generator_input_pointer: Mapping[str, Any],
    artifact_writer_request: Mapping[str, Any],
    generator_result_pointer: Mapping[str, Any],
    expected_result: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    _schema(case_metadata, CASE_METADATA_SCHEMA_VERSION, "case_metadata", mismatches)
    _schema(generator_request, GENERATOR_REQUEST_SCHEMA_VERSION, "generator_request", mismatches)
    _schema(
        generator_input_pointer,
        GENERATOR_INPUT_POINTER_SCHEMA_VERSION,
        "generator_input_pointer",
        mismatches,
    )
    _schema(
        artifact_writer_request,
        ARTIFACT_WRITER_REQUEST_SCHEMA_VERSION,
        "artifact_writer_request",
        mismatches,
    )
    _schema(
        generator_result_pointer,
        GENERATOR_RESULT_POINTER_SCHEMA_VERSION,
        "generator_result_pointer",
        mismatches,
    )
    _schema(expected_result, EXPECTED_RESULT_SCHEMA_VERSION, "expected_result", mismatches)

    if case_id != case_metadata.get("case_id") or case_id != expected_result.get("case_id"):
        mismatches.append("case_id_mismatch")
    if case_group != case_metadata.get("case_group"):
        mismatches.append("case_group_mismatch")
    if case_metadata.get("integration_step") != INTEGRATION_STEP:
        mismatches.append("case_metadata_integration_step_mismatch")
    if expected_result.get("integration_step") != INTEGRATION_STEP:
        mismatches.append("expected_result_integration_step_mismatch")
    if expected_result.get("mode") != MODE:
        mismatches.append("expected_result_mode_mismatch")
    if case_metadata.get("expected_status") != expected_result.get("integration_status"):
        mismatches.append("expected_status_alignment_mismatch")
    if case_metadata.get("expected_reason_codes") != expected_result.get(
        "expected_reason_codes"
    ):
        mismatches.append("expected_reason_codes_alignment_mismatch")
    if case_metadata.get("release_quality_ready") is not False:
        mismatches.append("case_metadata_release_quality_ready_not_false")
    if artifact_writer_request.get("release_quality_ready") is not False:
        mismatches.append("artifact_writer_request_release_quality_ready_not_false")
    if expected_result.get("release_quality_ready") is not False:
        mismatches.append("expected_result_release_quality_ready_not_false")

    expected_reason = EXPECTED_INVALID_REASONS.get(case_id)
    if expected_reason == "unknown_generator_result_schema":
        if generator_result_pointer.get("generator_result_schema_version") == (
            GENERATOR_RESULT_SCHEMA_VERSION
        ):
            mismatches.append("unknown_generator_result_schema_marker_missing")
    elif generator_result_pointer.get("generator_result_schema_version") != (
        GENERATOR_RESULT_SCHEMA_VERSION
    ):
        mismatches.append("generator_result_schema_version_mismatch")


def _validate_reason_policy(
    case_id: str,
    case_group: str,
    case_metadata: Mapping[str, Any],
    expected_result: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    reason_codes = _list_of_strings(expected_result.get("expected_reason_codes"))
    for reason in reason_codes:
        if reason not in ALLOWED_REASON_CODES:
            mismatches.append("unknown_reason_code")

    if case_group == "valid":
        if case_id not in VALID_CASE_LABELS:
            mismatches.append("unknown_valid_case")
        if expected_result.get("integration_status") != "pass":
            mismatches.append("valid_case_status_not_pass")
        if reason_codes:
            mismatches.append("valid_case_reason_codes_present")
    elif case_group == "invalid":
        expected_reason = EXPECTED_INVALID_REASONS.get(case_id)
        if expected_reason is None:
            mismatches.append("unknown_invalid_case")
        if expected_result.get("integration_status") not in {"usage_error", "fail_closed"}:
            mismatches.append("invalid_case_status_not_error")
        if not reason_codes:
            mismatches.append("invalid_reason_codes_missing")
        if expected_reason is not None and reason_codes != [expected_reason]:
            mismatches.append("reason_code_case_mismatch")
    else:
        mismatches.append("case_group_unknown")

    if case_metadata.get("expected_reason_codes") != reason_codes:
        mismatches.append("metadata_reason_code_mismatch")


def _validate_case_rules(
    case_group: str,
    expected_result: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    if case_group == "valid":
        if expected_result.get("generator_scaffold_executed") is not True:
            mismatches.append("valid_generator_scaffold_not_executed")
        if expected_result.get("artifact_writer_executed") is not True:
            mismatches.append("valid_artifact_writer_not_executed")

    false_fields = (
        "artifact_body_generation_executed",
        "manifest_writer_executed",
        "generated_artifact_written",
        "artifact_file_written",
        "manifest_file_written",
        "artifact_body_available",
        "generated_artifact_body_available",
        "manifest_body_available",
    )
    for field_name in false_fields:
        if expected_result.get(field_name) is not False:
            mismatches.append(f"{field_name}_not_false")
    for field_name in BOOLEAN_TRUE_EXPECTED_FIELDS:
        if expected_result.get(field_name) is not True:
            mismatches.append(f"{field_name}_not_true")
    if expected_result.get("written_file_count") != 0:
        mismatches.append("written_file_count_not_zero")

    count_summary = expected_result.get("count_summary")
    if not isinstance(count_summary, Mapping):
        mismatches.append("count_summary_not_object")
        return
    for field_name in ZERO_COUNTER_FIELDS:
        if count_summary.get(field_name) != 0:
            mismatches.append(f"{field_name}_not_zero")


def _validate_no_oracle_policy(
    case_metadata: Mapping[str, Any],
    generator_input_pointer: Mapping[str, Any],
    expected_result: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    if case_metadata.get("synthetic_only") is not True:
        mismatches.append("case_metadata_synthetic_only_not_true")
    if case_metadata.get("no_oracle") is not True:
        mismatches.append("case_metadata_no_oracle_not_true")
    if case_metadata.get("metadata_only") is not True:
        mismatches.append("case_metadata_metadata_only_not_true")
    if case_metadata.get("body_free") is not True:
        mismatches.append("case_metadata_body_free_not_true")
    if generator_input_pointer.get("synthetic_only") is not True:
        mismatches.append("generator_input_pointer_synthetic_only_not_true")
    if generator_input_pointer.get("no_oracle") is not True:
        mismatches.append("generator_input_pointer_no_oracle_not_true")
    if expected_result.get("synthetic_only_checked") is not True:
        mismatches.append("expected_synthetic_only_checked_not_true")
    if expected_result.get("no_oracle_checked") is not True:
        mismatches.append("expected_no_oracle_checked_not_true")


def _validate_file_writing_policy(
    case_metadata: Mapping[str, Any],
    generator_request: Mapping[str, Any],
    artifact_writer_request: Mapping[str, Any],
    expected_result: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    if case_metadata.get("file_writing_expected") is not False:
        mismatches.append("file_writing_expected_not_false")
    if generator_request.get("file_writing_allowed") is not False:
        mismatches.append("generator_file_writing_allowed_not_false")
    if artifact_writer_request.get("file_writing_allowed") is not False:
        mismatches.append("artifact_writer_file_writing_allowed_not_false")
    if expected_result.get("generated_artifact_written") is not False:
        mismatches.append("generated_artifact_written_not_false")
    if expected_result.get("artifact_file_written") is not False:
        mismatches.append("artifact_file_written_not_false")
    if expected_result.get("manifest_file_written") is not False:
        mismatches.append("manifest_file_written_not_false")
    if expected_result.get("written_file_count") != 0:
        mismatches.append("written_file_count_not_zero")


def _validate_artifact_body_manifest_separation(
    case_metadata: Mapping[str, Any],
    artifact_writer_request: Mapping[str, Any],
    expected_result: Mapping[str, Any],
    mismatches: list[str],
) -> None:
    if case_metadata.get("artifact_body_generation_expected") is not False:
        mismatches.append("artifact_body_generation_expected_not_false")
    if artifact_writer_request.get("artifact_body_generation_requested") is not False:
        reason_codes = _list_of_strings(expected_result.get("expected_reason_codes"))
        if reason_codes != ["unsupported_artifact_body_generation_integration"]:
            mismatches.append("artifact_body_generation_requested_not_false")
    if expected_result.get("artifact_body_generation_executed") is not False:
        mismatches.append("artifact_body_generation_executed_not_false")
    if case_metadata.get("manifest_writer_expected") is not False:
        mismatches.append("manifest_writer_expected_not_false")
    if artifact_writer_request.get("manifest_writer_requested") is not False:
        mismatches.append("manifest_writer_requested_not_false")
    if expected_result.get("manifest_writer_executed") is not False:
        mismatches.append("manifest_writer_executed_not_false")


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
        if LOCAL_ABSOLUTE_PATH_PATTERN.search(value) or value.startswith(("~", "/")):
            mismatches.append("actual_absolute_or_private_path")
        lowered = value.lower()
        if "real participant" in lowered or "participant data sample" in lowered:
            mismatches.append("real_participant_marker")


def _is_forbidden_actual_key(key: str) -> bool:
    if key in FORBIDDEN_ACTUAL_KEYS:
        return True
    if key.startswith("no_"):
        return False
    if key in ALLOWED_REASON_CODES:
        return False
    if key.endswith(SAFE_MARKER_SUFFIXES):
        return False
    return False


def _load_json(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ArtifactWriterCliIntegrationFixtureValidationError("json_root_not_object")
    return payload


def _case_id_from_dir(case_dir: Path) -> str:
    return f"{case_dir.parent.name}/{case_dir.name}"


def _case_input_error(
    case_dir: Path,
    reason: str,
) -> ArtifactWriterCliIntegrationFixtureCaseResult:
    case_group = case_dir.parent.name
    if case_group not in {"valid", "invalid"}:
        case_group = "unknown"
    return ArtifactWriterCliIntegrationFixtureCaseResult(
        case_id=_case_id_from_dir(case_dir),
        case_group=case_group,
        integration_status="input_error",
        reason_codes=(reason,),
        generator_scaffold_executed=False,
        artifact_writer_executed=False,
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
    extra = actual - _allowed_fields_for_payload(expected_fields, payload)
    if missing:
        mismatches.append(f"{label}_missing_fields")
    if extra:
        mismatches.append(f"{label}_extra_fields")


def _allowed_fields_for_payload(
    expected_fields: frozenset[str],
    payload: Mapping[str, Any],
) -> set[str]:
    allowed = set(expected_fields)
    for key in payload:
        if key.endswith(SAFE_MARKER_SUFFIXES):
            allowed.add(key)
        if key in {
            "controlled_invalid_marker",
            "unsupported_file_writing_mode_requested",
        }:
            allowed.add(key)
    return allowed


def _schema(
    payload: Mapping[str, Any],
    expected_schema: str,
    label: str,
    mismatches: list[str],
) -> None:
    if payload.get("schema_version") != expected_schema:
        mismatches.append(f"{label}_schema_version_mismatch")


def _list_of_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


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
            "fixture contracts."
        )
    )
    parser.add_argument(
        "--fixture-root",
        default=str(DEFAULT_FIXTURE_ROOT),
        help="Fixture root to validate.",
    )
    parser.add_argument(
        "--fixture-case",
        help="Optional relative case selector such as valid/example_case.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a parseable body-free JSON summary.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    summary = validate_artifact_writer_cli_integration_fixture_root(
        args.fixture_root,
        fixture_case=args.fixture_case,
    )
    payload = summarize_artifact_writer_cli_integration_fixture_validation(summary)
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        _print_human_summary(payload)
    return 0 if summary.all_matched else 1


if __name__ == "__main__":
    sys.exit(main())
