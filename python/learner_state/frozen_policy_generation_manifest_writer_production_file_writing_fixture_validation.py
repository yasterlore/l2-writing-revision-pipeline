"""Static validation for production manifest writer file writing fixtures.

This validator checks synthetic metadata-only fixture contracts. It does not
write manifest files, execute the runtime writer, expose public --manifest-out,
connect artifact writer CLI, train models, or compute metrics.
"""

from __future__ import annotations

import argparse
import json
import re
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
EXPECTED_RESULT_FILE = "expected_production_file_writing_result.json"

DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_manifest_writer_production_file_writing"
)

CASE_METADATA_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_"
    "production_file_writing_case_metadata_v0.1"
)
MANIFEST_WRITER_REQUEST_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_runtime_request_v0.1"
)
ARTIFACT_POINTER_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_result_pointer_v0.1"
)
ARTIFACT_BODY_POINTER_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_"
    "artifact_body_generation_result_pointer_v0.1"
)
EXPECTED_RESULT_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_"
    "production_file_writing_expected_result_v0.1"
)
VALIDATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_"
    "production_file_writing_validation_v0.1"
)

MODE = "manifest_writer_production_file_writing_fixture_validation"
JSON_FILES_PER_CASE = 5

EXPECTED_TOTAL_CASES = 32
EXPECTED_VALID_CASES = 8
EXPECTED_INVALID_CASES = 24
EXPECTED_TOTAL_JSON_FILES = EXPECTED_TOTAL_CASES * JSON_FILES_PER_CASE
EXPECTED_PASS_WRITTEN_CASES = 7
EXPECTED_PASS_NO_WRITE_CASES = 1
EXPECTED_USAGE_ERROR_CASES = 12
EXPECTED_FAIL_CLOSED_CASES = 12

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
        "case_category",
        "expected_reason_codes",
        "synthetic_notice",
        "no_oracle_notice",
        "non_proof_notice",
        "production_readiness_notice",
        "fixture_kind",
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
        "allow_overwrite",
        "overwrite_policy",
        "safe_output_root_policy",
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
        "artifact_writer_cli_integration_requested",
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
        "expected_manifest_output_path_available",
        "expected_manifest_body_available",
        "expected_manifest_body_suppressed",
        "expected_output_path_safety_checked",
        "expected_content_policy_checked",
        "expected_stdout_body_printed",
        "expected_stderr_body_printed",
        "expected_public_absolute_path_printed",
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
        "unsafe_absolute_manifest_output_path",
        "unsafe_parent_traversal_manifest_output_path",
        "unsafe_manifest_output_path_outside_allowed_root",
        "unsafe_home_manifest_output_path",
        "unsafe_private_path_marker_manifest_output_path",
        "unsafe_cloud_marker_manifest_output_path",
        "unsafe_hidden_private_manifest_directory",
        "unsafe_manifest_output_path_extension",
        "unsafe_manifest_output_filename",
        "unsafe_manifest_output_path_too_long",
        "output_exists_without_overwrite",
        "unsafe_symlink_manifest_output_path",
        "manifest_body_requested",
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
        "performance_metric_body_leakage",
        "manifest_write_failure",
        "manifest_write_parse_failure",
        "manifest_written_forbidden_content",
        "partial_write_cleanup_failure",
        "unsupported_artifact_writer_cli_integration",
        "unsupported_manifest_writer_mode",
    }
)

USAGE_ERROR_REASONS = frozenset(
    {
        "unsafe_absolute_manifest_output_path",
        "unsafe_parent_traversal_manifest_output_path",
        "unsafe_manifest_output_path_outside_allowed_root",
        "unsafe_home_manifest_output_path",
        "unsafe_private_path_marker_manifest_output_path",
        "unsafe_cloud_marker_manifest_output_path",
        "unsafe_hidden_private_manifest_directory",
        "unsafe_manifest_output_path_extension",
        "unsafe_manifest_output_filename",
        "unsafe_manifest_output_path_too_long",
        "output_exists_without_overwrite",
        "unsafe_symlink_manifest_output_path",
    }
)
FAIL_CLOSED_REASONS = REASON_CODES - USAGE_ERROR_REASONS

GROUPED_REASON_CASES = {
    "invalid/request_pointer_expected_body_leakage": frozenset(
        {"request_body_leakage", "pointer_body_leakage", "expected_body_leakage"}
    ),
    "invalid/raw_rows_logits_private_raw_text_leakage": frozenset(
        {
            "raw_rows_leakage",
            "logits_dump_leakage",
            "private_path_leakage",
            "absolute_path_leakage",
            "raw_learner_text_leakage",
        }
    ),
}

EXPECTED_SAFETY_FLAGS = (
    "content_suppressed",
    "manifest_body_suppressed",
    "no_artifact_body_payload",
    "no_expected_body",
    "no_generated_policy_body",
    "no_logits_dump",
    "no_oracle_checked",
    "no_pointer_body",
    "no_private_paths",
    "no_raw_rows",
    "no_request_body",
    "output_path_safety_checked",
    "synthetic_only_checked",
)

BODY_FORBIDDEN_KEYS = frozenset(
    {
        "manifest_body",
        "manifest_json_body",
        "written_file_json_body",
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
        "gold_labels",
        "scoring_feedback",
        "real_participant_data",
        "performance_metric_body",
    }
)

OUTPUT_FORBIDDEN_FRAGMENTS = (
    '"case_metadata":',
    '"manifest_writer_request":',
    '"artifact_writer_result_pointer":',
    '"artifact_body_generation_result_pointer":',
    '"expected_production_file_writing_result":',
    '"written_file_json_body":',
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

SAFE_RELATIVE_RE = re.compile(r"^[A-Za-z0-9._/-]+$")
LOCAL_ABSOLUTE_PATH_PATTERN = re.compile(
    r"(^|[=\s])(/Users/|/home/|/private/|/var/folders/|[A-Za-z]:\\)"
)


class ManifestWriterProductionFileWritingFixtureValidationError(Exception):
    """Raised when a fixture root or selector cannot be validated safely."""


@dataclass(frozen=True)
class ManifestWriterProductionFileWritingFixtureCaseResult:
    case_id: str
    case_kind: str
    actual_category: str
    actual_writer_status: str
    reason_codes: tuple[str, ...]
    manifest_file_written: bool
    written_file_count: int
    matched: bool
    input_error: bool
    mismatch_reasons: tuple[str, ...] = ()

    @property
    def is_mismatch(self) -> bool:
        return (not self.matched) and (not self.input_error)


@dataclass
class ManifestWriterProductionFileWritingFixtureValidationSummary:
    case_results: list[ManifestWriterProductionFileWritingFixtureCaseResult] = field(
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
    def pass_written_cases(self) -> int:
        return sum(
            result.actual_category == "pass_written" for result in self.case_results
        )

    @property
    def pass_no_write_cases(self) -> int:
        return sum(
            result.actual_category == "pass_no_write" for result in self.case_results
        )

    @property
    def usage_error_cases(self) -> int:
        return sum(
            result.actual_category == "usage_error" for result in self.case_results
        )

    @property
    def fail_closed_cases(self) -> int:
        return sum(
            result.actual_category == "fail_closed" for result in self.case_results
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
        return self.total_cases > 0 and self.matched_cases == self.total_cases


def _load_json(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ManifestWriterProductionFileWritingFixtureValidationError(
            "json_root_not_object"
        )
    return payload


def _case_id_from_dir(case_dir: Path) -> str:
    return f"{case_dir.parent.name}/{case_dir.name}"


def _list_field(payload: Mapping[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    return value if isinstance(value, list) else []


def _result_for_input_error(
    case_dir: Path,
    expected_kind: str | None,
    reason: str,
) -> ManifestWriterProductionFileWritingFixtureCaseResult:
    case_kind = expected_kind or case_dir.parent.name
    if case_kind not in {"valid", "invalid"}:
        case_kind = "unknown"
    return ManifestWriterProductionFileWritingFixtureCaseResult(
        case_id=_case_id_from_dir(case_dir),
        case_kind=case_kind,
        actual_category="input_error",
        actual_writer_status="input_error",
        reason_codes=(reason,),
        manifest_file_written=False,
        written_file_count=0,
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
    if expected_fields - actual:
        mismatches.append(f"{label}_missing_fields")
    if actual - expected_fields:
        mismatches.append(f"{label}_extra_fields")


def _require_schema(
    payload: Mapping[str, Any],
    expected_schema: str,
    label: str,
    mismatches: list[str],
) -> None:
    if payload.get("schema_version") != expected_schema:
        mismatches.append(f"{label}_schema_version_mismatch")


def _is_safe_manifest_out(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    if "\\" in value or "\x00" in value:
        return False
    if value.startswith(("/", "~")):
        return False
    if not SAFE_RELATIVE_RE.fullmatch(value):
        return False
    path = PurePosixPath(value)
    if path.suffix != ".json":
        return False
    if any(part in {"", ".", ".."} for part in path.parts):
        return False
    if any(part.startswith(".") for part in path.parts):
        return False
    return True


def _has_actual_private_or_absolute_path(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(_has_actual_private_or_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(_has_actual_private_or_absolute_path(item) for item in value)
    if not isinstance(value, str):
        return False
    if LOCAL_ABSOLUTE_PATH_PATTERN.search(value):
        return True
    if "file://" in value or "\\Users\\" in value:
        return True
    return value.startswith(("/", "~"))


def _contains_forbidden_body_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key in BODY_FORBIDDEN_KEYS:
                return True
            if _contains_forbidden_body_key(item):
                return True
    elif isinstance(value, list):
        return any(_contains_forbidden_body_key(item) for item in value)
    return False


def _check_reason_policy(
    case_id: str,
    case_kind: str,
    category: str,
    writer_status: str,
    reason_codes: Sequence[str],
    mismatches: list[str],
) -> None:
    if category not in EXPECTED_CATEGORIES:
        mismatches.append("unknown_expected_category")
    for reason in reason_codes:
        if reason not in REASON_CODES:
            mismatches.append("unknown_reason_code")

    if case_kind == "valid":
        if category not in {"pass_written", "pass_no_write"}:
            mismatches.append("valid_case_category_not_pass")
        if writer_status != "pass":
            mismatches.append("valid_case_writer_status_not_pass")
        if reason_codes:
            mismatches.append("valid_case_reason_codes_present")
    elif case_kind == "invalid":
        if category not in {"usage_error", "fail_closed"}:
            mismatches.append("invalid_case_category_not_error")
        if category == "usage_error" and writer_status != "usage_error":
            mismatches.append("usage_error_status_mismatch")
        if category == "fail_closed" and writer_status != "fail_closed":
            mismatches.append("fail_closed_status_mismatch")
        if not reason_codes:
            mismatches.append("invalid_reason_codes_missing")
        for reason in reason_codes:
            if category == "usage_error" and reason not in USAGE_ERROR_REASONS:
                mismatches.append("usage_error_reason_taxonomy_mismatch")
            if category == "fail_closed" and reason not in FAIL_CLOSED_REASONS:
                mismatches.append("fail_closed_reason_taxonomy_mismatch")
    else:
        mismatches.append("case_kind_unknown")

    if case_id in GROUPED_REASON_CASES:
        if set(reason_codes) != set(GROUPED_REASON_CASES[case_id]):
            mismatches.append("grouped_reason_codes_mismatch")
    elif case_kind == "invalid" and len(reason_codes) != 1:
        mismatches.append("ungrouped_invalid_reason_count_mismatch")


def _check_request_policy(
    request: Mapping[str, Any],
    category: str,
    reason_codes: Sequence[str],
    mismatches: list[str],
) -> None:
    mode = request.get("manifest_writer_mode")
    manifest_out = request.get("manifest_out")

    if request.get("safe_output_root_policy") != (
        "tmp_frozen_policy_generation_manifest_safe_relative_only"
    ):
        mismatches.append("safe_output_root_policy_mismatch")

    if category == "pass_written":
        if mode != "metadata_only_file":
            mismatches.append("request_manifest_writer_mode_not_file")
        if request.get("include_manifest_body") is not False:
            mismatches.append("request_include_manifest_body_not_false")
        if request.get("allow_manifest_file_writing") is not True:
            mismatches.append("request_allow_file_writing_not_true")
        if not _is_safe_manifest_out(manifest_out):
            mismatches.append("request_manifest_out_not_safe_relative_json")
        if request.get("allow_overwrite") is True:
            if request.get("overwrite_policy") != "allow_overwrite":
                mismatches.append("overwrite_allowed_policy_mismatch")
        else:
            if request.get("overwrite_policy") != "fail_if_exists":
                mismatches.append("default_overwrite_policy_mismatch")
    elif category == "pass_no_write":
        if mode != "metadata_only_no_file":
            mismatches.append("request_manifest_writer_mode_not_no_file")
        if request.get("include_manifest_body") is not False:
            mismatches.append("request_no_file_include_manifest_body_not_false")
        if request.get("allow_manifest_file_writing") is not False:
            mismatches.append("request_no_file_allow_writing_not_false")
        if manifest_out is not None:
            mismatches.append("request_no_file_manifest_out_present")
    else:
        if "unsupported_manifest_writer_mode" not in reason_codes:
            if mode not in {"metadata_only_file", "metadata_only_no_file"}:
                mismatches.append("request_manifest_writer_mode_unsupported")
        if "manifest_body_requested" not in reason_codes:
            if request.get("include_manifest_body") is not False:
                mismatches.append("request_include_manifest_body_unexpected")
        if reason_codes and set(reason_codes).issubset(USAGE_ERROR_REASONS):
            if reason_codes[0] == "output_exists_without_overwrite":
                if request.get("allow_overwrite") is not False:
                    mismatches.append("output_exists_allow_overwrite_not_false")
            elif not isinstance(manifest_out, str) or not manifest_out:
                mismatches.append("unsafe_path_sentinel_missing")

    for field_name in (
        "synthetic_notice",
        "no_oracle_notice",
        "non_proof_notice",
    ):
        if not request.get(field_name):
            mismatches.append(f"{field_name}_missing")
    if not isinstance(request.get("validation_reference_ids"), list):
        mismatches.append("validation_reference_ids_not_list")
    if not isinstance(request.get("release_quality_reference_ids"), list):
        mismatches.append("release_quality_reference_ids_not_list")


def _check_pointer_policy(
    artifact_pointer: Mapping[str, Any],
    artifact_body_pointer: Mapping[str, Any],
    reason_codes: Sequence[str],
    mismatches: list[str],
) -> None:
    if "unsupported_artifact_writer_cli_integration" in reason_codes:
        if artifact_pointer.get("artifact_writer_cli_integration_requested") is not True:
            mismatches.append("artifact_writer_cli_integration_sentinel_missing")
    elif artifact_pointer.get("artifact_writer_cli_integration_requested") is not False:
        mismatches.append("artifact_writer_cli_integration_requested_not_false")
    for label, payload in (
        ("artifact_pointer", artifact_pointer),
        ("artifact_body_pointer", artifact_body_pointer),
    ):
        if not payload.get("safe_metadata_reference_id"):
            mismatches.append(f"{label}_safe_metadata_reference_id_missing")
        if "artifact_body_payload_leakage" in reason_codes:
            if payload.get("include_body_payload") is not True:
                mismatches.append(f"{label}_body_payload_sentinel_missing")
        elif payload.get("include_body_payload") is not False:
            mismatches.append(f"{label}_include_body_payload_not_false")
        if "raw_rows_leakage" in reason_codes:
            if payload.get("include_raw_rows") is not True:
                mismatches.append(f"{label}_raw_rows_sentinel_missing")
        elif payload.get("include_raw_rows") is not False:
            mismatches.append(f"{label}_include_raw_rows_not_false")
        if "private_path_leakage" in reason_codes:
            if payload.get("include_private_paths") is not True:
                mismatches.append(f"{label}_private_paths_sentinel_missing")
        elif payload.get("include_private_paths") is not False:
            mismatches.append(f"{label}_include_private_paths_not_false")


def _check_expected_result_policy(
    expected: Mapping[str, Any],
    category: str,
    writer_status: str,
    reason_codes: Sequence[str],
    mismatches: list[str],
) -> None:
    if expected.get("expected_category") != category:
        mismatches.append("expected_category_mismatch")
    if expected.get("expected_writer_status") != writer_status:
        mismatches.append("expected_writer_status_mismatch")
    if expected.get("expected_reason_codes") != list(reason_codes):
        mismatches.append("expected_reason_codes_mismatch")
    if expected.get("expected_failed_checks") != list(reason_codes):
        mismatches.append("expected_failed_checks_mismatch")

    if expected.get("expected_manifest_body_available") is not False:
        mismatches.append("expected_manifest_body_available_not_false")
    if expected.get("expected_manifest_body_suppressed") is not True:
        mismatches.append("expected_manifest_body_suppressed_not_true")
    if expected.get("expected_output_path_safety_checked") is not True:
        mismatches.append("expected_output_path_safety_checked_not_true")
    if expected.get("expected_content_policy_checked") is not True:
        mismatches.append("expected_content_policy_checked_not_true")
    if expected.get("expected_stdout_body_printed") is not False:
        mismatches.append("expected_stdout_body_printed_not_false")
    if expected.get("expected_stderr_body_printed") is not False:
        mismatches.append("expected_stderr_body_printed_not_false")
    if expected.get("expected_public_absolute_path_printed") is not False:
        mismatches.append("expected_public_absolute_path_printed_not_false")
    if expected.get("expected_safe_summary") != (
        "metadata_only_manifest_writer_production_file_writing_result"
    ):
        mismatches.append("expected_safe_summary_mismatch")

    if category == "pass_written":
        if expected.get("expected_manifest_file_written") is not True:
            mismatches.append("expected_manifest_file_written_not_true")
        if expected.get("expected_written_file_count") != 1:
            mismatches.append("expected_written_file_count_not_one")
        if expected.get("expected_manifest_output_path_available") is not True:
            mismatches.append("expected_manifest_output_path_available_not_true")
    else:
        if expected.get("expected_manifest_file_written") is not False:
            mismatches.append("expected_manifest_file_written_not_false")
        if expected.get("expected_written_file_count") != 0:
            mismatches.append("expected_written_file_count_not_zero")
        if expected.get("expected_manifest_output_path_available") is not False:
            mismatches.append("expected_manifest_output_path_available_not_false")

    flags = expected.get("expected_safety_flags")
    if not isinstance(flags, Mapping):
        mismatches.append("expected_safety_flags_not_object")
    else:
        for flag in EXPECTED_SAFETY_FLAGS:
            if flags.get(flag) is not True:
                mismatches.append(f"expected_safety_flag_{flag}_not_true")


def validate_manifest_writer_production_file_writing_fixture_case(
    case_dir: str | Path,
    expected_kind: str | None = None,
) -> ManifestWriterProductionFileWritingFixtureCaseResult:
    """Validate one production file writing fixture case without writing files."""

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
    except (OSError, json.JSONDecodeError, ManifestWriterProductionFileWritingFixtureValidationError):
        return _result_for_input_error(case_path, case_kind, "malformed_fixture_json")

    case_metadata = payloads[CASE_METADATA_FILE]
    request = payloads[MANIFEST_WRITER_REQUEST_FILE]
    artifact_pointer = payloads[ARTIFACT_WRITER_RESULT_POINTER_FILE]
    artifact_body_pointer = payloads[ARTIFACT_BODY_GENERATION_RESULT_POINTER_FILE]
    expected = payloads[EXPECTED_RESULT_FILE]

    mismatches: list[str] = []
    case_id = _case_id_from_dir(case_path)
    category = str(expected.get("expected_category", "unknown"))
    writer_status = str(expected.get("expected_writer_status", "unknown"))
    reason_codes = tuple(str(item) for item in _list_field(expected, "expected_reason_codes"))

    _field_set_matches(case_metadata, CASE_METADATA_FIELDS, "case_metadata", mismatches)
    _field_set_matches(request, MANIFEST_WRITER_REQUEST_FIELDS, "request", mismatches)
    _field_set_matches(
        artifact_pointer, ARTIFACT_POINTER_FIELDS, "artifact_pointer", mismatches
    )
    _field_set_matches(
        artifact_body_pointer,
        ARTIFACT_BODY_POINTER_FIELDS,
        "artifact_body_pointer",
        mismatches,
    )
    _field_set_matches(expected, EXPECTED_RESULT_FIELDS, "expected", mismatches)

    _require_schema(
        case_metadata, CASE_METADATA_SCHEMA_VERSION, "case_metadata", mismatches
    )
    _require_schema(
        request, MANIFEST_WRITER_REQUEST_SCHEMA_VERSION, "request", mismatches
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

    if case_metadata.get("case_id") != case_id:
        mismatches.append("case_metadata_case_id_mismatch")
    if expected.get("case_id") != case_id:
        mismatches.append("expected_case_id_mismatch")
    if case_metadata.get("case_category") != category:
        mismatches.append("case_metadata_category_mismatch")
    if case_metadata.get("expected_reason_codes") != list(reason_codes):
        mismatches.append("case_metadata_reason_codes_mismatch")
    if case_metadata.get("fixture_kind") != "production_file_writing_contract":
        mismatches.append("case_metadata_fixture_kind_mismatch")
    for notice in (
        "synthetic_notice",
        "no_oracle_notice",
        "non_proof_notice",
        "production_readiness_notice",
    ):
        if not case_metadata.get(notice):
            mismatches.append(f"case_metadata_{notice}_missing")

    for label, payload in (
        ("artifact_pointer", artifact_pointer),
        ("artifact_body_pointer", artifact_body_pointer),
    ):
        if payload.get("source_fixture_id") != case_id:
            mismatches.append(f"{label}_source_fixture_id_mismatch")

    _check_reason_policy(
        case_id, case_kind, category, writer_status, reason_codes, mismatches
    )
    _check_request_policy(request, category, reason_codes, mismatches)
    _check_pointer_policy(
        artifact_pointer, artifact_body_pointer, reason_codes, mismatches
    )
    _check_expected_result_policy(
        expected, category, writer_status, reason_codes, mismatches
    )

    for payload in payloads.values():
        if _contains_forbidden_body_key(payload):
            mismatches.append("forbidden_body_key_found")
            break
    for payload in payloads.values():
        if _has_actual_private_or_absolute_path(payload):
            mismatches.append("actual_private_or_absolute_path_found")
            break

    return ManifestWriterProductionFileWritingFixtureCaseResult(
        case_id=case_id,
        case_kind=case_kind,
        actual_category=category,
        actual_writer_status=writer_status,
        reason_codes=reason_codes,
        manifest_file_written=bool(expected.get("expected_manifest_file_written")),
        written_file_count=int(expected.get("expected_written_file_count", 0)),
        matched=not mismatches,
        input_error=False,
        mismatch_reasons=tuple(sorted(set(mismatches))),
    )


def _discover_case_dirs(root: Path) -> list[tuple[Path, str]]:
    case_dirs: list[tuple[Path, str]] = []
    for kind in ("valid", "invalid"):
        kind_dir = root / kind
        if not kind_dir.is_dir():
            raise ManifestWriterProductionFileWritingFixtureValidationError(
                f"{kind}_directory_missing"
            )
        for case_dir in sorted(path for path in kind_dir.iterdir() if path.is_dir()):
            case_dirs.append((case_dir, kind))
    return case_dirs


def validate_manifest_writer_production_file_writing_fixture_root(
    fixture_root: str | Path = DEFAULT_FIXTURE_ROOT,
) -> ManifestWriterProductionFileWritingFixtureValidationSummary:
    """Validate all production file writing fixture cases."""

    root = Path(fixture_root)
    if not root.is_dir():
        raise ManifestWriterProductionFileWritingFixtureValidationError(
            "fixture_root_missing"
        )

    summary = ManifestWriterProductionFileWritingFixtureValidationSummary()
    for case_dir, expected_kind in _discover_case_dirs(root):
        result = validate_manifest_writer_production_file_writing_fixture_case(
            case_dir, expected_kind
        )
        summary.case_results.append(result)
        summary.reason_code_counts.update(result.reason_codes)
    return summary


def _summary_to_dict(
    summary: ManifestWriterProductionFileWritingFixtureValidationSummary,
) -> dict[str, Any]:
    return {
        "mode": MODE,
        "validation_schema_version": VALIDATION_SCHEMA_VERSION,
        "total_cases": summary.total_cases,
        "valid_cases": summary.valid_cases,
        "invalid_cases": summary.invalid_cases,
        "total_json_files": summary.total_json_files,
        "json_files_per_case": JSON_FILES_PER_CASE,
        "pass_written_cases": summary.pass_written_cases,
        "pass_no_write_cases": summary.pass_no_write_cases,
        "usage_error_cases": summary.usage_error_cases,
        "fail_closed_cases": summary.fail_closed_cases,
        "matched_cases": summary.matched_cases,
        "mismatched_cases": summary.mismatched_cases,
        "input_error_cases": summary.input_error_cases,
        "content_suppressed": True,
        "manifest_body_suppressed": True,
        "no_written_file_body": True,
        "no_manifest_body": True,
        "no_manifest_json_body": True,
        "no_artifact_body_payload": True,
        "no_generated_policy_body": True,
        "no_request_body": True,
        "no_pointer_body": True,
        "no_expected_body": True,
        "no_raw_rows": True,
        "no_logits_dump": True,
        "no_private_paths": True,
        "no_absolute_paths": True,
        "no_performance_claims": True,
        "synthetic_only_checked": True,
        "no_oracle_checked": True,
        "path_policy_checked": True,
        "overwrite_policy_checked": True,
        "stdout_stderr_policy_checked": True,
        "public_absolute_path_suppressed": True,
        "artifact_writer_cli_integration_checked": True,
        "release_quality_ready": False,
        "reason_code_counts": dict(sorted(summary.reason_code_counts.items())),
    }


def summarize_manifest_writer_production_file_writing_fixture_validation(
    summary: ManifestWriterProductionFileWritingFixtureValidationSummary,
    *,
    as_json: bool = False,
) -> str:
    """Render a body-free production file writing fixture validation summary."""

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
        raise ManifestWriterProductionFileWritingFixtureValidationError(
            "empty_selector"
        )
    if selector.startswith("/") or "\\" in selector:
        raise ManifestWriterProductionFileWritingFixtureValidationError(
            "unsafe_fixture_case_selector"
        )
    if any(ord(char) < 32 for char in selector):
        raise ManifestWriterProductionFileWritingFixtureValidationError(
            "unsafe_fixture_case_selector"
        )
    path = PurePosixPath(selector)
    if len(path.parts) != 2 or path.parts[0] not in {"valid", "invalid"}:
        raise ManifestWriterProductionFileWritingFixtureValidationError(
            "unsafe_fixture_case_selector"
        )
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ManifestWriterProductionFileWritingFixtureValidationError(
            "unsafe_parent_traversal_fixture_case_selector"
        )
    return path


def _summary_exit_code(
    summary: ManifestWriterProductionFileWritingFixtureValidationSummary,
) -> int:
    if summary.input_error_cases:
        return 4
    if summary.mismatched_cases:
        return 3
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate synthetic metadata-only production manifest writer file "
            "writing fixture contracts without writing files."
        )
    )
    parser.add_argument(
        "--fixture-root",
        default=str(DEFAULT_FIXTURE_ROOT),
        help="Fixture root to validate.",
    )
    parser.add_argument(
        "--fixture-case",
        help="Optional safe selector such as valid/minimal_manifest_out_file_written.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args(argv)

    try:
        root = Path(args.fixture_root)
        if args.fixture_case:
            selector = _validate_selector(args.fixture_case)
            result = validate_manifest_writer_production_file_writing_fixture_case(
                root / selector,
                expected_kind=selector.parts[0],
            )
            summary = ManifestWriterProductionFileWritingFixtureValidationSummary(
                case_results=[result],
                reason_code_counts=Counter(result.reason_codes),
            )
        else:
            summary = validate_manifest_writer_production_file_writing_fixture_root(root)
    except ManifestWriterProductionFileWritingFixtureValidationError as exc:
        error_result = ManifestWriterProductionFileWritingFixtureCaseResult(
            case_id="input_error",
            case_kind="input_error",
            actual_category="input_error",
            actual_writer_status="input_error",
            reason_codes=(str(exc),),
            manifest_file_written=False,
            written_file_count=0,
            matched=False,
            input_error=True,
            mismatch_reasons=(str(exc),),
        )
        summary = ManifestWriterProductionFileWritingFixtureValidationSummary(
            case_results=[error_result],
            reason_code_counts=Counter(error_result.reason_codes),
        )
        print(
            summarize_manifest_writer_production_file_writing_fixture_validation(
                summary, as_json=args.json
            )
        )
        return 2

    print(
        summarize_manifest_writer_production_file_writing_fixture_validation(
            summary, as_json=args.json
        )
    )
    return _summary_exit_code(summary)


if __name__ == "__main__":
    raise SystemExit(main())
