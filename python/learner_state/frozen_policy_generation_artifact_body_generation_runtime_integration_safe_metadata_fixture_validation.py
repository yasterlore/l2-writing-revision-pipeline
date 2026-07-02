"""Validate planned safe-metadata v0.2 runtime integration fixtures.

This validator checks a synthetic metadata-only fixture contract. It does not
invoke artifact body generation runtime, call manifest writer code, write
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
    "learner_state_frozen_policy_generation_artifact_body_generation_integration_"
    "planned_safe_metadata_v0_2"
)

MODE = "safe_metadata_fixture_validation"
VALIDATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_runtime_"
    "integration_safe_metadata_fixture_validation_v0.1"
)
RUNTIME_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_"
    "runtime_integration_v0.2"
)
RUNTIME_MODE = "safe-metadata-smoke"
PLANNED_MARKER = "v0.2_safe_metadata_planned"
SCHEMA_FAMILY = "artifact_body_generation_integration_safe_metadata_extension"

CASE_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_integration_"
    "case_v0.2_safe_metadata_planned"
)
RUNTIME_SUMMARY_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_integration_"
    "runtime_summary_metadata_v0.2_safe_metadata_planned"
)
REQUEST_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_integration_"
    "request_metadata_v0.2_safe_metadata_planned"
)
POINTER_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_integration_"
    "pointer_metadata_v0.2_safe_metadata_planned"
)
GENERATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_integration_"
    "generation_metadata_v0.2_safe_metadata_planned"
)
EXPECTED_SUMMARY_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_runtime_"
    "integration_expected_summary_v0.2_safe_metadata_planned"
)
EXPECTED_ERROR_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_runtime_"
    "integration_expected_error_v0.2_safe_metadata_planned"
)
UNSUPPORTED_CASE_SCHEMA_VERSION = "unsupported_safe_metadata_fixture_schema_v0.0"

EXPECTED_TOTAL_CASES = 24
EXPECTED_VALID_CASES = 4
EXPECTED_INVALID_CASES = 20
JSON_FILES_PER_CASE = 7
EXPECTED_TOTAL_JSON_FILES = EXPECTED_TOTAL_CASES * JSON_FILES_PER_CASE
EXPECTED_PASS_CASES = 4
EXPECTED_USAGE_ERROR_CASES = 1
EXPECTED_FAIL_CLOSED_CASES = 18
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
        "valid/valid_safe_metadata_explicit_runtime_bridge",
        "valid/valid_safe_metadata_count_only_bridge",
        "valid/valid_safe_metadata_no_file_writing_bridge",
        "valid/valid_safe_metadata_no_manifest_writer_bridge",
    }
)

EXPECTED_INVALID_REASONS = {
    "invalid/invalid_safe_metadata_artifact_body_payload_present": (
        "artifact_body_payload_present"
    ),
    "invalid/invalid_safe_metadata_manifest_body_present": "manifest_body_present",
    "invalid/invalid_safe_metadata_generated_policy_body_present": (
        "generated_policy_body_present"
    ),
    "invalid/invalid_safe_metadata_request_body_present": "request_body_present",
    "invalid/invalid_safe_metadata_pointer_body_present": "pointer_body_present",
    "invalid/invalid_safe_metadata_expected_body_present": "expected_body_present",
    "invalid/invalid_safe_metadata_raw_stdout_body_present": (
        "raw_stdout_body_present"
    ),
    "invalid/invalid_safe_metadata_raw_stderr_body_present": (
        "raw_stderr_body_present"
    ),
    "invalid/invalid_safe_metadata_raw_rows_present": "raw_rows_present",
    "invalid/invalid_safe_metadata_logits_present": "logits_present",
    "invalid/invalid_safe_metadata_private_path_present": "private_path_present",
    "invalid/invalid_safe_metadata_absolute_path_present": "absolute_path_present",
    "invalid/invalid_safe_metadata_raw_learner_text_present": (
        "raw_learner_text_present"
    ),
    "invalid/invalid_safe_metadata_real_data_marker_present": (
        "real_data_marker_present"
    ),
    "invalid/invalid_safe_metadata_performance_metric_body_present": (
        "performance_metric_body_present"
    ),
    "invalid/invalid_safe_metadata_file_writing_requested": (
        "file_writing_requested"
    ),
    "invalid/invalid_safe_metadata_manifest_writer_requested": (
        "manifest_writer_requested"
    ),
    "invalid/invalid_safe_metadata_unsafe_output_surface": "unsafe_output_surface",
    "invalid/invalid_safe_metadata_mismatched_expected_status": (
        "mismatched_expected_status"
    ),
    "invalid/invalid_safe_metadata_unsupported_schema": "unsupported_schema",
}

REASON_ALIASES = {
    "absolute_path_detected": "absolute_path_present",
    "artifact_body_payload_detected": "artifact_body_payload_present",
    "generated_policy_body_detected": "generated_policy_body_present",
    "logits_detected": "logits_present",
    "manifest_body_detected": "manifest_body_present",
    "performance_metric_body_detected": "performance_metric_body_present",
    "private_path_detected": "private_path_present",
    "raw_learner_text_detected": "raw_learner_text_present",
    "raw_rows_detected": "raw_rows_present",
    "raw_stderr_body_detected": "raw_stderr_body_present",
    "raw_stdout_body_detected": "raw_stdout_body_present",
    "real_data_marker_detected": "real_data_marker_present",
}

EXPECTED_REASON_CODE_COUNTS = Counter(
    {"none": EXPECTED_PASS_CASES, **{reason: 1 for reason in EXPECTED_INVALID_REASONS.values()}}
)

EXPECTED_STATUS_BY_REASON = {
    "none": "pass",
    "unsupported_schema": "usage_error",
    "mismatched_expected_status": "mismatch",
}
EXPECTED_EXIT_CODE_BY_STATUS = {
    "pass": "zero",
    "usage_error": "usage_error",
    "fail_closed": "fail_closed",
    "mismatch": "mismatch",
}

UNSAFE_REASONS = frozenset(
    reason
    for reason in EXPECTED_INVALID_REASONS.values()
    if reason not in {"unsupported_schema", "mismatched_expected_status"}
)

MARKER_FIELDS_BY_REASON: Mapping[str, tuple[tuple[str, str], ...]] = {
    "artifact_body_payload_present": (
        (RUNTIME_SUMMARY_FILE, "artifact_body_payload_present"),
        (REQUEST_METADATA_FILE, "artifact_body_payload_present"),
        (GENERATION_METADATA_FILE, "artifact_body_payload_present"),
        (EXPECTED_SUMMARY_FILE, "artifact_body_payload_present"),
    ),
    "manifest_body_present": (
        (RUNTIME_SUMMARY_FILE, "manifest_body_present"),
        (REQUEST_METADATA_FILE, "manifest_body_present"),
        (GENERATION_METADATA_FILE, "manifest_body_present"),
        (EXPECTED_SUMMARY_FILE, "manifest_body_present"),
    ),
    "generated_policy_body_present": (
        (RUNTIME_SUMMARY_FILE, "generated_policy_body_present"),
        (REQUEST_METADATA_FILE, "generated_policy_body_present"),
        (GENERATION_METADATA_FILE, "generated_policy_body_present"),
        (EXPECTED_SUMMARY_FILE, "generated_policy_body_present"),
    ),
    "request_body_present": (
        (RUNTIME_SUMMARY_FILE, "request_body_present"),
        (REQUEST_METADATA_FILE, "request_body_present"),
        (EXPECTED_SUMMARY_FILE, "request_body_present"),
    ),
    "pointer_body_present": (
        (RUNTIME_SUMMARY_FILE, "pointer_body_present"),
        (POINTER_METADATA_FILE, "pointer_body_present"),
        (EXPECTED_SUMMARY_FILE, "pointer_body_present"),
    ),
    "expected_body_present": (
        (RUNTIME_SUMMARY_FILE, "expected_body_present"),
        (EXPECTED_SUMMARY_FILE, "expected_body_present"),
    ),
    "raw_stdout_body_present": (
        (RUNTIME_SUMMARY_FILE, "raw_stdout_body_present"),
        (GENERATION_METADATA_FILE, "raw_stdout_body_present"),
        (EXPECTED_SUMMARY_FILE, "raw_stdout_body_present"),
    ),
    "raw_stderr_body_present": (
        (RUNTIME_SUMMARY_FILE, "raw_stderr_body_present"),
        (GENERATION_METADATA_FILE, "raw_stderr_body_present"),
        (EXPECTED_SUMMARY_FILE, "raw_stderr_body_present"),
    ),
    "raw_rows_present": (
        (RUNTIME_SUMMARY_FILE, "raw_rows_present"),
        (POINTER_METADATA_FILE, "raw_rows_present"),
        (EXPECTED_SUMMARY_FILE, "raw_rows_present"),
    ),
    "logits_present": (
        (RUNTIME_SUMMARY_FILE, "logits_present"),
        (POINTER_METADATA_FILE, "logits_present"),
        (EXPECTED_SUMMARY_FILE, "logits_present"),
    ),
    "private_path_present": (
        (RUNTIME_SUMMARY_FILE, "private_path_present"),
        (POINTER_METADATA_FILE, "private_path_present"),
        (EXPECTED_SUMMARY_FILE, "private_path_present"),
    ),
    "absolute_path_present": (
        (RUNTIME_SUMMARY_FILE, "absolute_path_present"),
        (POINTER_METADATA_FILE, "absolute_path_present"),
        (EXPECTED_SUMMARY_FILE, "absolute_path_present"),
    ),
    "raw_learner_text_present": (
        (RUNTIME_SUMMARY_FILE, "raw_learner_text_present"),
        (POINTER_METADATA_FILE, "raw_learner_text_present"),
        (EXPECTED_SUMMARY_FILE, "raw_learner_text_present"),
    ),
    "real_data_marker_present": (
        (RUNTIME_SUMMARY_FILE, "real_data_marker_present"),
        (REQUEST_METADATA_FILE, "real_data_marker_present"),
        (POINTER_METADATA_FILE, "real_data_marker_present"),
        (EXPECTED_SUMMARY_FILE, "real_data_marker_present"),
    ),
    "performance_metric_body_present": (
        (RUNTIME_SUMMARY_FILE, "performance_metric_body_present"),
        (REQUEST_METADATA_FILE, "performance_metric_body_present"),
        (GENERATION_METADATA_FILE, "performance_metric_body_present"),
        (EXPECTED_SUMMARY_FILE, "performance_metric_body_present"),
    ),
    "file_writing_requested": (
        (RUNTIME_SUMMARY_FILE, "file_writing_requested"),
        (REQUEST_METADATA_FILE, "file_writing_requested"),
        (GENERATION_METADATA_FILE, "file_writing_requested"),
        (EXPECTED_SUMMARY_FILE, "file_writing_requested"),
    ),
    "manifest_writer_requested": (
        (RUNTIME_SUMMARY_FILE, "manifest_writer_requested"),
        (REQUEST_METADATA_FILE, "manifest_writer_requested"),
        (GENERATION_METADATA_FILE, "manifest_writer_requested"),
        (EXPECTED_SUMMARY_FILE, "manifest_writer_requested"),
    ),
    "unsafe_output_surface": (
        (RUNTIME_SUMMARY_FILE, "unsupported_safe_metadata_output_surface"),
        (GENERATION_METADATA_FILE, "unsupported_safe_metadata_output_surface"),
        (EXPECTED_SUMMARY_FILE, "unsupported_safe_metadata_output_surface"),
    ),
}

FORBIDDEN_VALUE_KEYS = frozenset(
    {
        "fixture_json_body",
        "request_body",
        "pointer_body",
        "expected_body",
        "written_file_json_body",
        "written_file_body",
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
        "gold_labels",
        "post_hoc_annotation",
        "scoring_feedback_payload",
    }
)

LOCAL_ABSOLUTE_PATH_PATTERN = re.compile(
    r"(^|[=\s\"'])/(Users|home|private|var|tmp)/|[A-Za-z]:\\|file://|\\Users\\"
)


@dataclass(frozen=True)
class SafeMetadataFixtureCaseResult:
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
class SafeMetadataFixtureValidationSummary:
    case_results: list[SafeMetadataFixtureCaseResult] = field(default_factory=list)
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
            and self.total_cases > 0
            and self.matched_cases == self.total_cases
            and self.input_error_cases == 0
            and self.mismatched_cases == 0
        )


def discover_safe_metadata_fixture_cases(root: Path) -> list[Path]:
    case_dirs: list[Path] = []
    for group in ("valid", "invalid"):
        group_dir = root / group
        if group_dir.is_dir():
            case_dirs.extend(path for path in group_dir.iterdir() if path.is_dir())
    return sorted(case_dirs)


def validate_safe_metadata_fixture_root(
    fixture_root: str | Path = DEFAULT_FIXTURE_ROOT,
) -> SafeMetadataFixtureValidationSummary:
    root = Path(fixture_root)
    if not root.is_dir():
        return SafeMetadataFixtureValidationSummary(root_errors=("fixture_root_missing",))

    case_dirs = discover_safe_metadata_fixture_cases(root)
    actual_json_files = len(list(root.rglob("*.json")))
    root_errors = _root_errors(root, case_dirs, actual_json_files)

    results: list[SafeMetadataFixtureCaseResult] = []
    reason_counts: Counter[str] = Counter()
    missing_required_file_cases = 0
    unexpected_json_file_cases = 0
    for case_dir in case_dirs:
        file_error = _required_file_error(case_dir)
        if file_error == "missing_required_metadata_file":
            missing_required_file_cases += 1
        if file_error == "unexpected_json_file":
            unexpected_json_file_cases += 1
        result = validate_safe_metadata_fixture_case(case_dir)
        results.append(result)
        reason_counts.update([result.expected_reason_code])

    return SafeMetadataFixtureValidationSummary(
        case_results=results,
        reason_code_counts=reason_counts,
        root_errors=tuple(root_errors),
        actual_json_files=actual_json_files,
        missing_required_file_cases=missing_required_file_cases,
        unexpected_json_file_cases=unexpected_json_file_cases,
    )


def validate_safe_metadata_fixture_case(
    case_dir: str | Path,
) -> SafeMetadataFixtureCaseResult:
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

    expected_status, expected_reason, expected_exit = _expected_result(payloads)
    mismatch_reasons = _case_mismatch_reasons(path, payloads, expected_status, expected_reason)

    return SafeMetadataFixtureCaseResult(
        case_id=case_id,
        case_kind=case_kind,
        expected_status=expected_status,
        expected_reason_code=expected_reason,
        expected_exit_code_category=expected_exit,
        matched=not mismatch_reasons,
        input_error=False,
        mismatch_reasons=tuple(mismatch_reasons),
    )


def summarize_safe_metadata_fixture_validation(
    summary: SafeMetadataFixtureValidationSummary,
    *,
    fixture_root: str | Path = DEFAULT_FIXTURE_ROOT,
) -> dict[str, Any]:
    root = Path(fixture_root)
    return {
        "mode": MODE,
        "validation_schema_version": VALIDATION_SCHEMA_VERSION,
        "fixture_root": _public_root_label(root),
        "planned_root": True,
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
        "metadata_only_checked": True,
        "synthetic_only_checked": True,
        "no_oracle_checked": True,
        "safe_metadata_v0_2_planned_checked": True,
        "runtime_mode_checked": True,
        "runtime_schema_checked": True,
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
        "no_private_paths": True,
        "no_absolute_paths": True,
        "no_raw_learner_text": True,
        "no_real_participant_data": True,
        "no_performance_metric_body": True,
        "file_writing_checked": True,
        "manifest_writer_integration_checked": True,
        "artifact_body_generation_runtime_invocation_checked": True,
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
        description="Validate planned safe-metadata v0.2 runtime integration fixtures."
    )
    parser.add_argument("--fixture-root", default=str(DEFAULT_FIXTURE_ROOT))
    args = parser.parse_args(argv)

    summary = validate_safe_metadata_fixture_root(args.fixture_root)
    payload = summarize_safe_metadata_fixture_validation(
        summary, fixture_root=args.fixture_root
    )
    print_public_summary(payload)
    return 0 if summary.all_matched else 1


def _root_errors(root: Path, case_dirs: list[Path], actual_json_files: int) -> list[str]:
    errors: list[str] = []
    child_dirs = sorted(path.name for path in root.iterdir() if path.is_dir())
    if child_dirs != ["invalid", "valid"]:
        errors.append("unexpected_root_layout")
    if len(case_dirs) != EXPECTED_TOTAL_CASES:
        errors.append("total_cases_mismatch")
    valid_cases = sum(path.parent.name == "valid" for path in case_dirs)
    invalid_cases = sum(path.parent.name == "invalid" for path in case_dirs)
    if valid_cases != EXPECTED_VALID_CASES:
        errors.append("valid_cases_mismatch")
    if invalid_cases != EXPECTED_INVALID_CASES:
        errors.append("invalid_cases_mismatch")
    if actual_json_files != EXPECTED_TOTAL_JSON_FILES:
        errors.append("total_json_files_mismatch")
    return errors


def _required_file_error(case_dir: Path) -> str | None:
    json_names = sorted(path.name for path in case_dir.glob("*.json"))
    required_names = sorted(REQUIRED_FILES)
    if any(name not in json_names for name in required_names):
        return "missing_required_metadata_file"
    if json_names != required_names:
        return "unexpected_json_file"
    return None


def _case_input_error(case_dir: Path, reason: str) -> SafeMetadataFixtureCaseResult:
    return SafeMetadataFixtureCaseResult(
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
        if _str_field(payload, "case_id") and _str_field(payload, "case_id") != case_id:
            mismatches.append(f"{file_name}:case_id_mismatch")
        if _str_field(payload, "case_kind") and _str_field(payload, "case_kind") != case_kind:
            mismatches.append(f"{file_name}:case_kind_mismatch")

    mismatches.extend(_schema_mismatches(case_id, payloads, expected_reason))
    mismatches.extend(_common_contract_mismatches(payloads))
    mismatches.extend(_expected_result_mismatches(payloads, expected_status, expected_reason))
    mismatches.extend(_unsafe_marker_mismatches(payloads, expected_reason))
    unsafe_value_reason = _unsafe_value_reason(payloads)
    if unsafe_value_reason:
        mismatches.append(unsafe_value_reason)
    return mismatches


def _schema_mismatches(
    case_id: str,
    payloads: Mapping[str, Mapping[str, Any]],
    expected_reason: str,
) -> list[str]:
    mismatches: list[str] = []
    for file_name, expected_schema in EXPECTED_FILE_SCHEMAS.items():
        schema = _str_field(payloads[file_name], "schema_version")
        if (
            file_name == CASE_METADATA_FILE
            and expected_reason == "unsupported_schema"
            and schema == UNSUPPORTED_CASE_SCHEMA_VERSION
        ):
            continue
        if schema != expected_schema:
            mismatches.append(f"{file_name}:schema_version")

    if expected_reason == "unsupported_schema" and not case_id.endswith("unsupported_schema"):
        mismatches.append("unsupported_schema_case_mismatch")
    return mismatches


def _common_contract_mismatches(
    payloads: Mapping[str, Mapping[str, Any]]
) -> list[str]:
    mismatches: list[str] = []
    for file_name, payload in payloads.items():
        if "fixture_schema_extension_version" in payload and payload.get(
            "fixture_schema_extension_version"
        ) != PLANNED_MARKER:
            mismatches.append(f"{file_name}:planned_marker")
        if "fixture_schema_family" in payload and payload.get("fixture_schema_family") != SCHEMA_FAMILY:
            mismatches.append(f"{file_name}:schema_family")
        if "runtime_mode" in payload and payload.get("runtime_mode") != RUNTIME_MODE:
            mismatches.append(f"{file_name}:runtime_mode")
        if (
            "runtime_expected_summary_schema_version" in payload
            and payload.get("runtime_expected_summary_schema_version") != RUNTIME_SCHEMA_VERSION
        ):
            mismatches.append(f"{file_name}:runtime_schema")
        if (
            "expected_runtime_schema_version" in payload
            and payload.get("expected_runtime_schema_version") != RUNTIME_SCHEMA_VERSION
        ):
            mismatches.append(f"{file_name}:expected_runtime_schema")
        for key in ("synthetic_only", "metadata_only", "no_oracle"):
            if key in payload and payload.get(key) is not True:
                mismatches.append(f"{file_name}:{key}")
        if "body_free" in payload and payload.get("body_free") is not True:
            mismatches.append(f"{file_name}:body_free")
        if "production_readiness_claimed" in payload and payload.get(
            "production_readiness_claimed"
        ) is not False:
            mismatches.append(f"{file_name}:production_readiness_claimed")
        if "real_data_readiness_claimed" in payload and payload.get(
            "real_data_readiness_claimed"
        ) is not False:
            mismatches.append(f"{file_name}:real_data_readiness_claimed")
        if "performance_claims_present" in payload and payload.get(
            "performance_claims_present"
        ) is not False:
            mismatches.append(f"{file_name}:performance_claims_present")
        if "artifact_body_generation_runtime_invoked" in payload and payload.get(
            "artifact_body_generation_runtime_invoked"
        ) is not False:
            mismatches.append(f"{file_name}:artifact_body_generation_runtime_invoked")
    return mismatches


def _expected_result_mismatches(
    payloads: Mapping[str, Mapping[str, Any]],
    expected_status: str,
    expected_reason: str,
) -> list[str]:
    mismatches: list[str] = []
    expected_exit = EXPECTED_EXIT_CODE_BY_STATUS.get(expected_status)
    for file_name in (
        CASE_METADATA_FILE,
        RUNTIME_SUMMARY_FILE,
        REQUEST_METADATA_FILE,
        POINTER_METADATA_FILE,
        GENERATION_METADATA_FILE,
        EXPECTED_SUMMARY_FILE,
    ):
        payload = payloads[file_name]
        if "expected_runtime_status" in payload and payload.get(
            "expected_runtime_status"
        ) != expected_status:
            mismatches.append(f"{file_name}:expected_runtime_status")
        if "expected_runtime_reason_code" in payload and _normalized_reason(
            payload.get("expected_runtime_reason_code")
        ) != expected_reason:
            mismatches.append(f"{file_name}:expected_runtime_reason_code")

    for file_name in (RUNTIME_SUMMARY_FILE, EXPECTED_SUMMARY_FILE):
        payload = payloads[file_name]
        if payload.get("status") != expected_status:
            mismatches.append(f"{file_name}:status")
        if _normalized_reason(payload.get("reason_code")) != expected_reason:
            mismatches.append(f"{file_name}:reason_code")
        if payload.get("exit_code_category") != expected_exit:
            mismatches.append(f"{file_name}:exit_code_category")

    expected_error = payloads[EXPECTED_ERROR_FILE]
    if expected_error.get("expected_status") != expected_status:
        mismatches.append(f"{EXPECTED_ERROR_FILE}:expected_status")
    if _normalized_reason(expected_error.get("expected_reason_code")) != expected_reason:
        mismatches.append(f"{EXPECTED_ERROR_FILE}:expected_reason_code")
    if expected_error.get("expected_exit_code_category") != expected_exit:
        mismatches.append(f"{EXPECTED_ERROR_FILE}:expected_exit_code_category")
    if expected_error.get("public_safe_reason_code_only") is not True:
        mismatches.append(f"{EXPECTED_ERROR_FILE}:public_safe_reason_code_only")
    if expected_error.get("no_payload_in_error") is not True:
        mismatches.append(f"{EXPECTED_ERROR_FILE}:no_payload_in_error")
    return mismatches


def _unsafe_marker_mismatches(
    payloads: Mapping[str, Mapping[str, Any]],
    expected_reason: str,
) -> list[str]:
    mismatches: list[str] = []
    case_unsafe_signal_count = _int_field(payloads[CASE_METADATA_FILE], "unsafe_signal_count")
    if expected_reason == "none" and case_unsafe_signal_count != 0:
        mismatches.append("valid_unsafe_signal_count")
    if expected_reason in UNSAFE_REASONS and case_unsafe_signal_count <= 0:
        mismatches.append("invalid_unsafe_signal_count")

    if expected_reason == "none":
        for file_name, payload in payloads.items():
            if _int_field(payload, "unsafe_signal_count") != 0:
                mismatches.append(f"{file_name}:unsafe_signal_count")
        return mismatches

    if expected_reason in MARKER_FIELDS_BY_REASON:
        if not any(
            payloads[file_name].get(field_name) is True
            for file_name, field_name in MARKER_FIELDS_BY_REASON[expected_reason]
        ):
            mismatches.append(f"{expected_reason}:marker_missing")

    if expected_reason == "unsupported_schema" and payloads[RUNTIME_SUMMARY_FILE].get(
        "unsupported_schema"
    ) is not True:
        mismatches.append("unsupported_schema_marker_missing")
    if expected_reason == "mismatched_expected_status" and payloads[
        RUNTIME_SUMMARY_FILE
    ].get("expected_status_mismatch") is not True:
        mismatches.append("mismatched_expected_status_marker_missing")
    return mismatches


def _expected_result(
    payloads: Mapping[str, Mapping[str, Any]]
) -> tuple[str, str, str]:
    expected_error = payloads[EXPECTED_ERROR_FILE]
    status = _str_field(expected_error, "expected_status", "usage_error")
    reason = _normalized_reason(
        _str_field(expected_error, "expected_reason_code", "malformed_expected_error")
    )
    exit_code = _str_field(
        expected_error,
        "expected_exit_code_category",
        EXPECTED_EXIT_CODE_BY_STATUS.get(status, "usage_error"),
    )
    return status, reason, exit_code


def _unsafe_value_reason(payloads: Mapping[str, Mapping[str, Any]]) -> str | None:
    def walk(value: Any) -> str | None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                if key in FORBIDDEN_VALUE_KEYS:
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


def _normalized_reason(reason: object) -> str:
    text = str(reason)
    return REASON_ALIASES.get(text, text)


def _str_field(
    payload: Mapping[str, Any], key: str, default: str = ""
) -> str:
    value = payload.get(key, default)
    return value if isinstance(value, str) else default


def _int_field(payload: Mapping[str, Any], key: str) -> int:
    value = payload.get(key, 0)
    return value if isinstance(value, int) else 0


def _public_root_label(root: Path) -> str:
    if root.is_absolute():
        return root.name
    return str(root)


if __name__ == "__main__":
    sys.exit(main())
