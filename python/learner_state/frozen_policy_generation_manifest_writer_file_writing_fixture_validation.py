"""Static validation for manifest writer file writing fixtures.

This validator checks synthetic metadata-only fixture contracts. It does not
write manifest files, execute the runtime writer, perform isolated write
validation, connect artifact writer CLI, train models, or compute metrics.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

CASE_METADATA_FILE = "case_metadata.json"
MANIFEST_WRITER_REQUEST_FILE = "manifest_writer_request.json"
ARTIFACT_WRITER_RESULT_POINTER_FILE = "artifact_writer_result_pointer.json"
ARTIFACT_BODY_GENERATION_RESULT_POINTER_FILE = (
    "artifact_body_generation_result_pointer.json"
)
EXPECTED_RESULT_FILE = "expected_manifest_writer_file_writing_result.json"

DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_manifest_writer_file_writing"
)

CASE_METADATA_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_"
    "file_writing_case_metadata_v0.1"
)
REQUEST_SCHEMA_VERSION = (
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
EXPECTED_RESULT_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_"
    "file_writing_expected_result_v0.1"
)
RESULT_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_result_v0.1"
)
VALIDATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_"
    "file_writing_fixture_validation_v0.1"
)

MODE = "manifest_writer_file_writing_fixture_validation"
SAFE_ROOT = PurePosixPath("tmp/frozen_policy_generation_manifest")
JSON_FILES_PER_CASE = 5

EXPECTED_TOTAL_CASES = 39
EXPECTED_VALID_CASES = 6
EXPECTED_INVALID_CASES = 33
EXPECTED_TOTAL_JSON_FILES = EXPECTED_TOTAL_CASES * JSON_FILES_PER_CASE
EXPECTED_PASS_METADATA_FILE_WRITTEN_CASES = 5
EXPECTED_PASS_METADATA_NO_FILE_CASES = 1
EXPECTED_USAGE_ERROR_CASES = 15
EXPECTED_FAIL_CLOSED_CASES = 18

REQUIRED_FILES = (
    CASE_METADATA_FILE,
    MANIFEST_WRITER_REQUEST_FILE,
    ARTIFACT_WRITER_RESULT_POINTER_FILE,
    ARTIFACT_BODY_GENERATION_RESULT_POINTER_FILE,
    EXPECTED_RESULT_FILE,
)

CASE_METADATA_FIELDS = frozenset(
    {
        "schema_version",
        "case_id",
        "case_kind",
        "description",
        "expected_category",
        "expected_writer_status",
        "expected_manifest_writer_mode",
        "expected_reason_codes",
        "required_files",
        "json_files_per_case",
        "should_write_manifest_file",
        "should_leave_residue",
        "safety_expectation",
        "forbidden_output_markers",
        "notes",
    }
)

REQUEST_FIELDS = frozenset(
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
        "expected_manifest_writer_mode",
        "expected_reason_codes",
        "expected_failed_checks",
        "expected_manifest_body_available",
        "expected_manifest_file_written",
        "expected_manifest_output_path_available",
        "expected_written_file_count",
        "expected_release_quality_ready",
        "expected_safety_flags",
        "expected_count_summary",
        "expected_safe_summary",
        "expected_output_residue_count",
    }
)

SAFETY_FLAGS = (
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

EXPECTED_CATEGORIES = frozenset(
    {
        "pass_metadata_file_written",
        "pass_metadata_no_file",
        "usage_error_no_write",
        "fail_closed_no_write",
    }
)

VALID_CATEGORIES = frozenset(
    {"pass_metadata_file_written", "pass_metadata_no_file"}
)
INVALID_CATEGORIES = frozenset(
    {"usage_error_no_write", "fail_closed_no_write"}
)

REASON_CODES = frozenset(
    {
        "absolute_manifest_output_path",
        "parent_traversal_manifest_output_path",
        "manifest_output_path_outside_safe_root",
        "home_manifest_output_path",
        "hidden_private_manifest_directory",
        "cloud_marker_manifest_output_path",
        "non_json_manifest_extension",
        "unsafe_manifest_filename",
        "too_long_manifest_path",
        "overwrite_without_policy",
        "manifest_body_requested",
        "manifest_json_body_requested",
        "artifact_body_payload_leakage",
        "generated_policy_body_leakage",
        "request_body_leakage",
        "pointer_body_leakage",
        "expected_body_leakage",
        "raw_rows_leakage",
        "logits_dump_leakage",
        "private_path_leakage",
        "absolute_path_leakage",
        "raw_learner_text_leakage",
        "performance_claim_body",
        "missing_synthetic_notice",
        "missing_no_oracle_notice",
        "missing_non_proof_notice",
        "real_data_marker",
        "unsupported_artifact_writer_cli_integration",
        "unknown_schema_version",
        "malformed_artifact_result_pointer",
        "malformed_artifact_body_result_pointer",
        "missing_artifact_result_pointer",
        "missing_artifact_body_result_pointer",
    }
)

USAGE_ERROR_REASONS = frozenset(
    {
        "absolute_manifest_output_path",
        "parent_traversal_manifest_output_path",
        "manifest_output_path_outside_safe_root",
        "home_manifest_output_path",
        "hidden_private_manifest_directory",
        "cloud_marker_manifest_output_path",
        "non_json_manifest_extension",
        "unsafe_manifest_filename",
        "too_long_manifest_path",
        "overwrite_without_policy",
        "unknown_schema_version",
        "malformed_artifact_result_pointer",
        "malformed_artifact_body_result_pointer",
        "missing_artifact_result_pointer",
        "missing_artifact_body_result_pointer",
    }
)

FAIL_CLOSED_REASONS = REASON_CODES - USAGE_ERROR_REASONS
SAFE_FILENAME_RE = re.compile(r"^[A-Za-z0-9._/-]+$")


class ManifestWriterFileWritingFixtureValidationError(Exception):
    """Raised when a fixture root or selector cannot be validated safely."""


@dataclass(frozen=True)
class ManifestWriterFileWritingFixtureCaseResult:
    case_id: str
    case_kind: str
    expected_category: str
    expected_writer_status: str
    expected_manifest_writer_mode: str
    expected_reason_codes: tuple[str, ...]
    matched: bool
    input_error: bool
    mismatch_reasons: tuple[str, ...] = ()


@dataclass
class ManifestWriterFileWritingFixtureValidationSummary:
    case_results: list[ManifestWriterFileWritingFixtureCaseResult] = field(
        default_factory=list
    )
    reason_code_counts: Counter[str] = field(default_factory=Counter)

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
        return self.total_cases * JSON_FILES_PER_CASE

    @property
    def pass_metadata_file_written_cases(self) -> int:
        return sum(
            result.expected_category == "pass_metadata_file_written"
            for result in self.case_results
        )

    @property
    def pass_metadata_no_file_cases(self) -> int:
        return sum(
            result.expected_category == "pass_metadata_no_file"
            for result in self.case_results
        )

    @property
    def usage_error_cases(self) -> int:
        return sum(
            result.expected_category == "usage_error_no_write"
            for result in self.case_results
        )

    @property
    def fail_closed_cases(self) -> int:
        return sum(
            result.expected_category == "fail_closed_no_write"
            for result in self.case_results
        )

    @property
    def matched_cases(self) -> int:
        return sum(result.matched for result in self.case_results)

    @property
    def mismatched_cases(self) -> int:
        return sum(
            (not result.matched) and (not result.input_error)
            for result in self.case_results
        )

    @property
    def input_error_cases(self) -> int:
        return sum(result.input_error for result in self.case_results)

    @property
    def all_matched(self) -> bool:
        return self.total_cases > 0 and self.matched_cases == self.total_cases


def _load_json(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ManifestWriterFileWritingFixtureValidationError(
            f"{path.name}: json_root_not_object"
        )
    return payload


def _case_id_from_dir(case_dir: Path) -> str:
    return f"{case_dir.parent.name}/{case_dir.name}"


def _is_missing_pointer_reason(reason: str, file_name: str) -> bool:
    return (
        reason == "missing_artifact_result_pointer"
        and file_name == ARTIFACT_WRITER_RESULT_POINTER_FILE
    ) or (
        reason == "missing_artifact_body_result_pointer"
        and file_name == ARTIFACT_BODY_GENERATION_RESULT_POINTER_FILE
    )


def _result_for_input_error(
    case_dir: Path,
    expected_kind: str | None,
    reason: str,
) -> ManifestWriterFileWritingFixtureCaseResult:
    case_kind = expected_kind or case_dir.parent.name
    if case_kind not in {"valid", "invalid"}:
        case_kind = "unknown"
    return ManifestWriterFileWritingFixtureCaseResult(
        case_id=_case_id_from_dir(case_dir),
        case_kind=case_kind,
        expected_category="input_error",
        expected_writer_status="input_error",
        expected_manifest_writer_mode="unknown",
        expected_reason_codes=(reason,),
        matched=False,
        input_error=True,
        mismatch_reasons=(reason,),
    )


def _field_set_matches(
    payload: Mapping[str, Any],
    expected_fields: frozenset[str],
    label: str,
    mismatches: list[str],
) -> None:
    actual = set(payload)
    missing = sorted(expected_fields - actual)
    extra = sorted(actual - expected_fields)
    if missing:
        mismatches.append(f"{label}_missing_fields")
    if extra:
        mismatches.append(f"{label}_extra_fields")


def _require_schema(
    payload: Mapping[str, Any],
    expected_schema: str,
    label: str,
    mismatches: list[str],
    *,
    allow_unknown_schema_reason: bool = False,
) -> None:
    schema = payload.get("schema_version")
    if schema == expected_schema:
        return
    if allow_unknown_schema_reason and schema == "UNKNOWN_SCHEMA_VERSION_SENTINEL":
        return
    mismatches.append(f"{label}_schema_version")


def _is_safe_manifest_output_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    if "\\" in value or "\x00" in value:
        return False
    if value.startswith(("/", "~")):
        return False
    if not SAFE_FILENAME_RE.fullmatch(value):
        return False
    path = PurePosixPath(value)
    if path.suffix != ".json":
        return False
    if any(part in {"", ".", ".."} for part in path.parts):
        return False
    return path == SAFE_ROOT or SAFE_ROOT in (path, *path.parents)


def _has_actual_private_or_absolute_path(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(_has_actual_private_or_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(_has_actual_private_or_absolute_path(item) for item in value)
    if not isinstance(value, str):
        return False
    forbidden_fragments = (
        "/Users/",
        "/private/",
        "/var/folders/",
        "file://",
        "\\Users\\",
    )
    if any(fragment in value for fragment in forbidden_fragments):
        return True
    return value.startswith(("/", "~"))


def _list_field(payload: Mapping[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    return value if isinstance(value, list) else []


def _check_expected_result_policy(
    expected: Mapping[str, Any],
    category: str,
    writer_status: str,
    writer_mode: str,
    reason_codes: Sequence[str],
    mismatches: list[str],
) -> None:
    if expected.get("expected_category") != category:
        mismatches.append("expected_category_mismatch")
    if expected.get("expected_writer_status") != writer_status:
        mismatches.append("expected_writer_status_mismatch")
    if expected.get("expected_manifest_writer_mode") != writer_mode:
        mismatches.append("expected_manifest_writer_mode_mismatch")
    if expected.get("expected_reason_codes") != list(reason_codes):
        mismatches.append("expected_reason_codes_mismatch")
    if expected.get("expected_failed_checks") != list(reason_codes):
        mismatches.append("expected_failed_checks_mismatch")
    if expected.get("expected_manifest_body_available") is not False:
        mismatches.append("expected_manifest_body_available_not_false")
    if expected.get("expected_release_quality_ready") is not False:
        mismatches.append("expected_release_quality_ready_not_false")
    if expected.get("expected_output_residue_count") != 0:
        mismatches.append("expected_output_residue_count_not_zero")

    if category == "pass_metadata_file_written":
        if expected.get("expected_manifest_file_written") is not True:
            mismatches.append("expected_file_written_not_true")
        if expected.get("expected_manifest_output_path_available") is not True:
            mismatches.append("expected_output_path_available_not_true")
        if expected.get("expected_written_file_count") != 1:
            mismatches.append("expected_written_file_count_not_one")
    else:
        if expected.get("expected_manifest_file_written") is not False:
            mismatches.append("expected_file_written_not_false")
        if expected.get("expected_manifest_output_path_available") is not False:
            mismatches.append("expected_output_path_available_not_false")
        if expected.get("expected_written_file_count") != 0:
            mismatches.append("expected_written_file_count_not_zero")

    flags = expected.get("expected_safety_flags")
    if not isinstance(flags, Mapping):
        mismatches.append("expected_safety_flags_not_object")
    else:
        for flag in SAFETY_FLAGS:
            if flags.get(flag) is not True:
                mismatches.append(f"expected_safety_flag_{flag}_not_true")

    counts = expected.get("expected_count_summary")
    if not isinstance(counts, Mapping):
        mismatches.append("expected_count_summary_not_object")
    else:
        zero_count_fields = (
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
        )
        for field_name in zero_count_fields:
            if counts.get(field_name) != 0:
                mismatches.append(f"expected_count_{field_name}_not_zero")
        if counts.get("written_file_count") != expected.get("expected_written_file_count"):
            mismatches.append("expected_written_file_count_summary_mismatch")

    safe_summary = expected.get("expected_safe_summary")
    if not isinstance(safe_summary, (str, Mapping)):
        mismatches.append("expected_safe_summary_not_safe_token")


def _check_request_policy(
    request: Mapping[str, Any],
    category: str,
    reason_codes: Sequence[str],
    mismatches: list[str],
) -> None:
    mode = request.get("manifest_writer_mode")
    manifest_out = request.get("manifest_out")
    if category == "pass_metadata_file_written":
        if mode != "metadata_only_file":
            mismatches.append("request_file_written_mode_mismatch")
        if request.get("include_manifest_body") is not False:
            mismatches.append("request_include_manifest_body_not_false")
        if request.get("allow_manifest_file_writing") is not True:
            mismatches.append("request_allow_file_writing_not_true")
        if not _is_safe_manifest_output_path(manifest_out):
            mismatches.append("request_manifest_out_not_safe")
    elif category == "pass_metadata_no_file":
        if mode != "metadata_only_no_file":
            mismatches.append("request_no_file_mode_mismatch")
        if request.get("allow_manifest_file_writing") is not False:
            mismatches.append("request_no_file_allow_writing_not_false")
        if manifest_out is not None:
            mismatches.append("request_no_file_manifest_out_present")
    else:
        if mode not in {"metadata_only_file", "metadata_only_no_file"}:
            mismatches.append("request_manifest_writer_mode_unsupported")
        if "manifest_body_requested" not in reason_codes:
            if request.get("include_manifest_body") is not False:
                mismatches.append("request_include_manifest_body_unexpected")
        if "unknown_schema_version" not in reason_codes:
            if request.get("schema_version") != REQUEST_SCHEMA_VERSION:
                mismatches.append("request_schema_unexpected")

    notice_expectations = (
        ("synthetic_notice", "missing_synthetic_notice"),
        ("no_oracle_notice", "missing_no_oracle_notice"),
        ("non_proof_notice", "missing_non_proof_notice"),
    )
    for field_name, reason in notice_expectations:
        present = bool(request.get(field_name))
        if reason in reason_codes:
            if present:
                mismatches.append(f"{field_name}_unexpectedly_present")
        elif not present:
            mismatches.append(f"{field_name}_missing")


def _check_pointer_policy(
    artifact_pointer: Mapping[str, Any],
    artifact_body_pointer: Mapping[str, Any],
    reason_codes: Sequence[str],
    mismatches: list[str],
) -> None:
    if "artifact_body_payload_leakage" in reason_codes:
        if artifact_pointer.get("include_body_payload") is not True:
            mismatches.append("artifact_pointer_payload_leakage_missing")
        if artifact_body_pointer.get("include_body_payload") is not True:
            mismatches.append("artifact_body_pointer_payload_leakage_missing")
    else:
        if artifact_pointer.get("include_body_payload") is not False:
            mismatches.append("artifact_pointer_payload_flag_not_false")
        if artifact_body_pointer.get("include_body_payload") is not False:
            mismatches.append("artifact_body_pointer_payload_flag_not_false")

    if "raw_rows_leakage" in reason_codes:
        if artifact_pointer.get("include_raw_rows") is not True:
            mismatches.append("artifact_pointer_raw_rows_leakage_missing")
        if artifact_body_pointer.get("include_raw_rows") is not True:
            mismatches.append("artifact_body_pointer_raw_rows_leakage_missing")
    else:
        if artifact_pointer.get("include_raw_rows") is not False:
            mismatches.append("artifact_pointer_raw_rows_flag_not_false")
        if artifact_body_pointer.get("include_raw_rows") is not False:
            mismatches.append("artifact_body_pointer_raw_rows_flag_not_false")

    if "private_path_leakage" in reason_codes:
        if artifact_pointer.get("include_private_paths") is not True:
            mismatches.append("artifact_pointer_private_path_leakage_missing")
        if artifact_body_pointer.get("include_private_paths") is not True:
            mismatches.append("artifact_body_pointer_private_path_leakage_missing")
    else:
        if artifact_pointer.get("include_private_paths") is not False:
            mismatches.append("artifact_pointer_private_paths_flag_not_false")
        if artifact_body_pointer.get("include_private_paths") is not False:
            mismatches.append("artifact_body_pointer_private_paths_flag_not_false")


def _check_reason_policy(
    case_kind: str,
    category: str,
    writer_status: str,
    reason_codes: Sequence[str],
    mismatches: list[str],
) -> None:
    if case_kind == "valid":
        if category not in VALID_CATEGORIES:
            mismatches.append("valid_case_category_not_pass")
        if writer_status != "pass":
            mismatches.append("valid_case_writer_status_not_pass")
        if reason_codes:
            mismatches.append("valid_case_reason_codes_present")
    elif case_kind == "invalid":
        if category not in INVALID_CATEGORIES:
            mismatches.append("invalid_case_category_not_invalid")
        if category == "usage_error_no_write" and writer_status != "usage_error":
            mismatches.append("usage_error_status_mismatch")
        if category == "fail_closed_no_write" and writer_status != "fail_closed":
            mismatches.append("fail_closed_status_mismatch")
        if len(reason_codes) != 1:
            mismatches.append("invalid_reason_code_count_mismatch")
        for reason in reason_codes:
            if reason not in REASON_CODES:
                mismatches.append("unknown_reason_code")
            if category == "usage_error_no_write" and reason not in USAGE_ERROR_REASONS:
                mismatches.append("usage_error_reason_taxonomy_mismatch")
            if category == "fail_closed_no_write" and reason not in FAIL_CLOSED_REASONS:
                mismatches.append("fail_closed_reason_taxonomy_mismatch")
    else:
        mismatches.append("case_kind_unknown")


def _check_safe_path_policy(
    request: Mapping[str, Any],
    category: str,
    reason_codes: Sequence[str],
    mismatches: list[str],
) -> None:
    manifest_out = request.get("manifest_out")
    if category == "pass_metadata_file_written":
        if not _is_safe_manifest_output_path(manifest_out):
            mismatches.append("safe_path_policy_valid_manifest_out")
    elif category == "pass_metadata_no_file":
        if manifest_out is not None:
            mismatches.append("safe_path_policy_no_file_manifest_out")
    elif reason_codes and reason_codes[0] in USAGE_ERROR_REASONS:
        if reason_codes[0] not in {
            "unknown_schema_version",
            "malformed_artifact_result_pointer",
            "malformed_artifact_body_result_pointer",
            "missing_artifact_result_pointer",
            "missing_artifact_body_result_pointer",
        }:
            if not isinstance(manifest_out, str) or not manifest_out:
                mismatches.append("unsafe_path_sentinel_missing")


def validate_manifest_writer_file_writing_fixture_case(
    case_dir: str | Path,
    expected_kind: str | None = None,
) -> ManifestWriterFileWritingFixtureCaseResult:
    """Validate a single manifest writer file writing fixture case."""

    case_path = Path(case_dir)
    case_kind = expected_kind or case_path.parent.name
    if case_kind not in {"valid", "invalid"}:
        return _result_for_input_error(case_path, expected_kind, "case_kind_unknown")

    file_names = {path.name for path in case_path.glob("*.json")}
    missing = sorted(set(REQUIRED_FILES) - file_names)
    extra = sorted(file_names - set(REQUIRED_FILES))
    if missing:
        return _result_for_input_error(case_path, case_kind, "required_file_missing")
    if extra:
        return _result_for_input_error(case_path, case_kind, "unexpected_json_file")

    payloads: dict[str, Mapping[str, Any]] = {}
    try:
        for file_name in REQUIRED_FILES:
            payloads[file_name] = _load_json(case_path / file_name)
    except (OSError, json.JSONDecodeError, ManifestWriterFileWritingFixtureValidationError):
        return _result_for_input_error(case_path, case_kind, "json_parse_error")

    case_metadata = payloads[CASE_METADATA_FILE]
    request = payloads[MANIFEST_WRITER_REQUEST_FILE]
    artifact_pointer = payloads[ARTIFACT_WRITER_RESULT_POINTER_FILE]
    artifact_body_pointer = payloads[ARTIFACT_BODY_GENERATION_RESULT_POINTER_FILE]
    expected = payloads[EXPECTED_RESULT_FILE]

    mismatches: list[str] = []
    case_id = _case_id_from_dir(case_path)
    category = str(expected.get("expected_category", "unknown"))
    writer_status = str(expected.get("expected_writer_status", "unknown"))
    writer_mode = str(expected.get("expected_manifest_writer_mode", "unknown"))
    reason_codes = tuple(str(item) for item in _list_field(expected, "expected_reason_codes"))

    _field_set_matches(case_metadata, CASE_METADATA_FIELDS, "case_metadata", mismatches)
    _field_set_matches(request, REQUEST_FIELDS, "request", mismatches)
    _field_set_matches(
        artifact_pointer, ARTIFACT_POINTER_FIELDS, "artifact_pointer", mismatches
    )
    _field_set_matches(
        artifact_body_pointer,
        ARTIFACT_BODY_POINTER_FIELDS,
        "artifact_body_pointer",
        mismatches,
    )
    _field_set_matches(expected, EXPECTED_RESULT_FIELDS, "expected_result", mismatches)

    _require_schema(
        case_metadata, CASE_METADATA_SCHEMA_VERSION, "case_metadata", mismatches
    )
    _require_schema(
        request,
        REQUEST_SCHEMA_VERSION,
        "request",
        mismatches,
        allow_unknown_schema_reason="unknown_schema_version" in reason_codes,
    )
    _require_schema(
        artifact_pointer,
        ARTIFACT_POINTER_SCHEMA_VERSION,
        "artifact_pointer",
        mismatches,
    )
    _require_schema(
        artifact_body_pointer,
        ARTIFACT_BODY_POINTER_SCHEMA_VERSION,
        "artifact_body_pointer",
        mismatches,
    )
    _require_schema(expected, EXPECTED_RESULT_SCHEMA_VERSION, "expected", mismatches)

    for label, payload in (
        ("case_metadata", case_metadata),
        ("expected", expected),
    ):
        if payload.get("case_id") != case_id:
            mismatches.append(f"{label}_case_id_mismatch")
    for label, payload in (
        ("artifact_pointer", artifact_pointer),
        ("artifact_body_pointer", artifact_body_pointer),
    ):
        if payload.get("source_fixture_id") != case_id:
            mismatches.append(f"{label}_source_fixture_id_mismatch")

    if case_metadata.get("case_kind") != case_kind:
        mismatches.append("case_metadata_kind_mismatch")
    if case_metadata.get("expected_category") != category:
        mismatches.append("case_metadata_category_mismatch")
    if case_metadata.get("expected_writer_status") != writer_status:
        mismatches.append("case_metadata_writer_status_mismatch")
    if case_metadata.get("expected_manifest_writer_mode") != writer_mode:
        mismatches.append("case_metadata_writer_mode_mismatch")
    if case_metadata.get("expected_reason_codes") != list(reason_codes):
        mismatches.append("case_metadata_reason_codes_mismatch")
    if set(case_metadata.get("required_files", [])) != set(REQUIRED_FILES):
        mismatches.append("case_metadata_required_files_mismatch")
    if case_metadata.get("json_files_per_case") != JSON_FILES_PER_CASE:
        mismatches.append("case_metadata_json_files_per_case_mismatch")

    _check_reason_policy(case_kind, category, writer_status, reason_codes, mismatches)
    _check_request_policy(request, category, reason_codes, mismatches)
    _check_pointer_policy(artifact_pointer, artifact_body_pointer, reason_codes, mismatches)
    _check_expected_result_policy(
        expected, category, writer_status, writer_mode, reason_codes, mismatches
    )
    _check_safe_path_policy(request, category, reason_codes, mismatches)

    if category == "pass_metadata_file_written":
        if case_metadata.get("should_write_manifest_file") is not True:
            mismatches.append("case_metadata_should_write_not_true")
    else:
        if case_metadata.get("should_write_manifest_file") is not False:
            mismatches.append("case_metadata_should_write_not_false")
    if case_metadata.get("should_leave_residue") is not False:
        mismatches.append("case_metadata_should_leave_residue_not_false")

    for payload in payloads.values():
        if _has_actual_private_or_absolute_path(payload):
            mismatches.append("actual_private_or_absolute_path_found")
            break

    return ManifestWriterFileWritingFixtureCaseResult(
        case_id=case_id,
        case_kind=case_kind,
        expected_category=category,
        expected_writer_status=writer_status,
        expected_manifest_writer_mode=writer_mode,
        expected_reason_codes=reason_codes,
        matched=not mismatches,
        input_error=False,
        mismatch_reasons=tuple(sorted(set(mismatches))),
    )


def _discover_case_dirs(root: Path) -> list[tuple[Path, str]]:
    case_dirs: list[tuple[Path, str]] = []
    for kind in ("valid", "invalid"):
        kind_dir = root / kind
        if not kind_dir.is_dir():
            raise ManifestWriterFileWritingFixtureValidationError(
                f"{kind}_directory_missing"
            )
        for case_dir in sorted(path for path in kind_dir.iterdir() if path.is_dir()):
            case_dirs.append((case_dir, kind))
    return case_dirs


def validate_manifest_writer_file_writing_fixture_root(
    fixture_root: str | Path = DEFAULT_FIXTURE_ROOT,
) -> ManifestWriterFileWritingFixtureValidationSummary:
    """Validate all fixture cases below the given fixture root."""

    root = Path(fixture_root)
    if not root.is_dir():
        raise ManifestWriterFileWritingFixtureValidationError("fixture_root_missing")

    summary = ManifestWriterFileWritingFixtureValidationSummary()
    for case_dir, expected_kind in _discover_case_dirs(root):
        result = validate_manifest_writer_file_writing_fixture_case(
            case_dir, expected_kind
        )
        summary.case_results.append(result)
        summary.reason_code_counts.update(result.expected_reason_codes)
    return summary


def _summary_to_dict(
    summary: ManifestWriterFileWritingFixtureValidationSummary,
) -> dict[str, Any]:
    return {
        "mode": MODE,
        "validation_schema_version": VALIDATION_SCHEMA_VERSION,
        "total_cases": summary.total_cases,
        "valid_cases": summary.valid_cases,
        "invalid_cases": summary.invalid_cases,
        "total_json_files": summary.total_json_files,
        "json_files_per_case": JSON_FILES_PER_CASE,
        "pass_metadata_file_written_cases": (
            summary.pass_metadata_file_written_cases
        ),
        "pass_metadata_no_file_cases": summary.pass_metadata_no_file_cases,
        "usage_error_cases": summary.usage_error_cases,
        "fail_closed_cases": summary.fail_closed_cases,
        "matched_cases": summary.matched_cases,
        "mismatched_cases": summary.mismatched_cases,
        "input_error_cases": summary.input_error_cases,
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
        "file_writing_checked": True,
        "validator_wrote_files": False,
        "runtime_writer_executed": False,
        "isolated_write_executed": False,
        "release_quality_ready": False,
        "reason_code_counts": dict(sorted(summary.reason_code_counts.items())),
    }


def summarize_manifest_writer_file_writing_fixture_validation(
    summary: ManifestWriterFileWritingFixtureValidationSummary,
    *,
    as_json: bool = False,
) -> str:
    """Render a body-free validation summary."""

    payload = _summary_to_dict(summary)
    if as_json:
        return json.dumps(payload, sort_keys=True)
    lines: list[str] = []
    for key, value in payload.items():
        if isinstance(value, bool):
            rendered = str(value).lower()
        elif isinstance(value, Mapping):
            rendered = json.dumps(value, sort_keys=True)
        else:
            rendered = str(value)
        lines.append(f"{key}={rendered}")
    return "\n".join(lines)


def _validate_selector(selector: str) -> PurePosixPath:
    if not selector:
        raise ManifestWriterFileWritingFixtureValidationError("empty_selector")
    if selector.startswith("/") or "\\" in selector:
        raise ManifestWriterFileWritingFixtureValidationError("unsafe_selector")
    if any(ord(char) < 32 for char in selector):
        raise ManifestWriterFileWritingFixtureValidationError("unsafe_selector")
    path = PurePosixPath(selector)
    if len(path.parts) != 2 or path.parts[0] not in {"valid", "invalid"}:
        raise ManifestWriterFileWritingFixtureValidationError("unsafe_selector")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ManifestWriterFileWritingFixtureValidationError("unsafe_selector")
    return path


def _summary_exit_code(
    summary: ManifestWriterFileWritingFixtureValidationSummary,
) -> int:
    if summary.input_error_cases:
        return 4
    if summary.mismatched_cases:
        return 3
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate synthetic metadata-only manifest writer file writing "
            "fixture contracts without writing files."
        )
    )
    parser.add_argument(
        "--fixture-root",
        default=str(DEFAULT_FIXTURE_ROOT),
        help="Fixture root to validate.",
    )
    parser.add_argument(
        "--fixture-case",
        help="Optional safe selector such as valid/metadata_file_minimal_safe_relative_json.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(argv)

    try:
        if args.fixture_case:
            selector = _validate_selector(args.fixture_case)
            case_dir = Path(args.fixture_root) / selector
            if not case_dir.is_dir():
                raise ManifestWriterFileWritingFixtureValidationError(
                    "fixture_case_missing"
                )
            result = validate_manifest_writer_file_writing_fixture_case(
                case_dir, selector.parts[0]
            )
            summary = ManifestWriterFileWritingFixtureValidationSummary(
                [result], Counter(result.expected_reason_codes)
            )
        else:
            summary = validate_manifest_writer_file_writing_fixture_root(
                args.fixture_root
            )
    except ManifestWriterFileWritingFixtureValidationError as exc:
        safe_message = f"usage_error={exc}"
        if args.json:
            print(json.dumps({"mode": MODE, "usage_error": str(exc)}, sort_keys=True))
        else:
            print(safe_message)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary.
        if args.json:
            print(json.dumps({"mode": MODE, "internal_error": type(exc).__name__}))
        else:
            print(f"internal_error={type(exc).__name__}")
        return 1

    print(
        summarize_manifest_writer_file_writing_fixture_validation(
            summary, as_json=args.json
        )
    )
    return _summary_exit_code(summary)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
