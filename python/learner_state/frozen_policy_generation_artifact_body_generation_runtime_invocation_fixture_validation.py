"""Validate artifact body generation runtime invocation fixtures.

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
RUNTIME_SUMMARY_FILE = "safe_metadata_runtime_summary_metadata.json"
REQUEST_METADATA_FILE = "artifact_body_request_metadata.json"
POINTER_METADATA_FILE = "artifact_body_pointer_metadata.json"
INVOCATION_METADATA_FILE = "artifact_body_generation_invocation_metadata.json"
EXPECTED_SUMMARY_FILE = "expected_runtime_invocation_summary.json"
EXPECTED_ERROR_FILE = "expected_error.json"

DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation"
)

MODE = "artifact_body_generation_runtime_invocation_fixture_validation"
VALIDATION_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_runtime_"
    "invocation_fixture_validation_v0.1"
)
FIXTURE_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_runtime_"
    "invocation_fixture_v0.1"
)
UNSUPPORTED_FIXTURE_SCHEMA_VERSION = "unsupported_runtime_invocation_fixture_schema_v0.0"
RUNTIME_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_"
    "runtime_integration_v0.3"
)
INTEGRATION_MODE = "artifact-body-runtime-invocation"
FIXTURE_STAGE = "planned_runtime_invocation_contract"
PLANNED_FIXTURE_ROOT_LABEL = (
    "learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation"
)

EXPECTED_TOTAL_CASES = 30
EXPECTED_VALID_CASES = 6
EXPECTED_INVALID_CASES = 24
JSON_FILES_PER_CASE = 7
EXPECTED_TOTAL_JSON_FILES = EXPECTED_TOTAL_CASES * JSON_FILES_PER_CASE
EXPECTED_PASS_CASES = 6
EXPECTED_USAGE_ERROR_CASES = 1
EXPECTED_FAIL_CLOSED_CASES = 22
EXPECTED_MISMATCH_CASES = 1

REQUIRED_FILES = (
    CASE_METADATA_FILE,
    RUNTIME_SUMMARY_FILE,
    REQUEST_METADATA_FILE,
    POINTER_METADATA_FILE,
    INVOCATION_METADATA_FILE,
    EXPECTED_SUMMARY_FILE,
    EXPECTED_ERROR_FILE,
)

VALID_CASE_LABELS = frozenset(
    {
        "valid/valid_minimal_safe_metadata_runtime_invocation",
        "valid/valid_safe_metadata_count_only_runtime_invocation",
        "valid/valid_invocation_no_manifest_writer",
        "valid/valid_invocation_no_file_writing",
        "valid/valid_invocation_body_payload_suppressed",
        "valid/valid_invocation_artifact_body_available_count_only",
    }
)

EXPECTED_INVALID_REASONS = {
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
    "invalid/invalid_manifest_writer_requested": "manifest_writer_requested",
    "invalid/invalid_unsafe_artifact_body_runtime_mode": (
        "unsafe_artifact_body_runtime_mode"
    ),
    "invalid/invalid_unsupported_schema": "unsupported_schema",
    "invalid/invalid_mismatched_expected_status": "mismatched_expected_status",
    "invalid/invalid_no_oracle_forbidden_field": "no_oracle_forbidden_field",
    "invalid/invalid_unsafe_output_residue_risk": "unsafe_output_residue_risk",
    "invalid/invalid_active_root_merge_attempted": "active_root_merge_attempted",
}

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
EXPECTED_REASON_CODE_COUNTS = Counter(
    {
        "none": EXPECTED_PASS_CASES,
        **{reason: 1 for reason in EXPECTED_INVALID_REASONS.values()},
    }
)
UNSAFE_REASONS = frozenset(
    reason
    for reason in EXPECTED_INVALID_REASONS.values()
    if reason not in {"unsupported_schema", "mismatched_expected_status"}
)

MARKER_FIELDS_BY_REASON: Mapping[str, tuple[tuple[str, str], ...]] = {
    "request_body_present": (
        (RUNTIME_SUMMARY_FILE, "request_body_present"),
        (REQUEST_METADATA_FILE, "request_body_present"),
    ),
    "pointer_body_present": (
        (RUNTIME_SUMMARY_FILE, "pointer_body_present"),
        (POINTER_METADATA_FILE, "pointer_body_present"),
    ),
    "expected_body_present": (
        (RUNTIME_SUMMARY_FILE, "expected_body_present"),
        (INVOCATION_METADATA_FILE, "expected_body_present"),
    ),
    "artifact_body_payload_present": (
        (RUNTIME_SUMMARY_FILE, "artifact_body_payload_present"),
        (INVOCATION_METADATA_FILE, "artifact_body_payload_present"),
    ),
    "manifest_body_present": (
        (RUNTIME_SUMMARY_FILE, "manifest_body_present"),
        (POINTER_METADATA_FILE, "manifest_body_present"),
    ),
    "generated_policy_body_present": (
        (RUNTIME_SUMMARY_FILE, "generated_policy_body_present"),
        (INVOCATION_METADATA_FILE, "generated_policy_body_present"),
    ),
    "raw_stdout_body_present": (
        (RUNTIME_SUMMARY_FILE, "raw_stdout_body_present"),
        (INVOCATION_METADATA_FILE, "raw_stdout_body_present"),
    ),
    "raw_stderr_body_present": (
        (RUNTIME_SUMMARY_FILE, "raw_stderr_body_present"),
        (INVOCATION_METADATA_FILE, "raw_stderr_body_present"),
    ),
    "raw_rows_present": (
        (RUNTIME_SUMMARY_FILE, "raw_rows_present"),
        (INVOCATION_METADATA_FILE, "raw_rows_present"),
    ),
    "logits_present": (
        (RUNTIME_SUMMARY_FILE, "logits_present"),
        (INVOCATION_METADATA_FILE, "logits_present"),
    ),
    "probabilities_present": (
        (RUNTIME_SUMMARY_FILE, "probabilities_present"),
        (INVOCATION_METADATA_FILE, "probabilities_present"),
    ),
    "private_path_present": (
        (RUNTIME_SUMMARY_FILE, "private_path_present"),
        (POINTER_METADATA_FILE, "private_path_present"),
    ),
    "absolute_path_present": (
        (RUNTIME_SUMMARY_FILE, "absolute_path_present"),
        (POINTER_METADATA_FILE, "absolute_path_present"),
    ),
    "raw_learner_text_present": (
        (RUNTIME_SUMMARY_FILE, "raw_learner_text_present"),
        (REQUEST_METADATA_FILE, "raw_learner_text_present"),
    ),
    "real_data_marker_present": (
        (RUNTIME_SUMMARY_FILE, "real_data_marker_present"),
        (REQUEST_METADATA_FILE, "real_data_marker_present"),
    ),
    "performance_metric_body_present": (
        (RUNTIME_SUMMARY_FILE, "performance_metric_body_present"),
        (INVOCATION_METADATA_FILE, "performance_metric_body_present"),
    ),
    "file_writing_requested": (
        (RUNTIME_SUMMARY_FILE, "file_writing_requested"),
        (INVOCATION_METADATA_FILE, "file_writing_requested"),
    ),
    "manifest_writer_requested": (
        (RUNTIME_SUMMARY_FILE, "manifest_writer_requested"),
        (INVOCATION_METADATA_FILE, "manifest_writer_requested"),
    ),
    "unsafe_artifact_body_runtime_mode": (
        (RUNTIME_SUMMARY_FILE, "unsafe_artifact_body_runtime_mode"),
        (INVOCATION_METADATA_FILE, "unsafe_artifact_body_runtime_mode"),
    ),
    "no_oracle_forbidden_field": (
        (RUNTIME_SUMMARY_FILE, "no_oracle_forbidden_field"),
        (REQUEST_METADATA_FILE, "no_oracle_forbidden_field_present"),
    ),
    "unsafe_output_residue_risk": (
        (RUNTIME_SUMMARY_FILE, "unsafe_output_residue_risk"),
        (INVOCATION_METADATA_FILE, "unsafe_output_residue_risk"),
    ),
    "active_root_merge_attempted": (
        (RUNTIME_SUMMARY_FILE, "active_root_merge_attempted"),
        (INVOCATION_METADATA_FILE, "active_root_merge_attempted"),
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
class RuntimeInvocationFixtureCaseResult:
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
class RuntimeInvocationFixtureValidationSummary:
    case_results: list[RuntimeInvocationFixtureCaseResult] = field(default_factory=list)
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


def discover_runtime_invocation_fixture_cases(root: Path) -> list[Path]:
    case_dirs: list[Path] = []
    for group in ("valid", "invalid"):
        group_dir = root / group
        if group_dir.is_dir():
            case_dirs.extend(path for path in group_dir.iterdir() if path.is_dir())
    return sorted(case_dirs)


def validate_runtime_invocation_fixture_root(
    fixture_root: str | Path = DEFAULT_FIXTURE_ROOT,
) -> RuntimeInvocationFixtureValidationSummary:
    root = Path(fixture_root)
    if not root.is_dir():
        return RuntimeInvocationFixtureValidationSummary(root_errors=("fixture_root_missing",))

    case_dirs = discover_runtime_invocation_fixture_cases(root)
    actual_json_files = len(list(root.rglob("*.json")))
    root_errors = _root_errors(root, case_dirs, actual_json_files)

    results: list[RuntimeInvocationFixtureCaseResult] = []
    reason_counts: Counter[str] = Counter()
    missing_required_file_cases = 0
    unexpected_json_file_cases = 0
    for case_dir in case_dirs:
        file_error = _required_file_error(case_dir)
        if file_error == "missing_required_metadata_file":
            missing_required_file_cases += 1
        if file_error == "unexpected_json_file":
            unexpected_json_file_cases += 1
        result = validate_runtime_invocation_fixture_case(case_dir)
        results.append(result)
        reason_counts.update([result.expected_reason_code])

    return RuntimeInvocationFixtureValidationSummary(
        case_results=results,
        reason_code_counts=reason_counts,
        root_errors=tuple(root_errors),
        actual_json_files=actual_json_files,
        missing_required_file_cases=missing_required_file_cases,
        unexpected_json_file_cases=unexpected_json_file_cases,
    )


def validate_runtime_invocation_fixture_case(
    case_dir: str | Path,
) -> RuntimeInvocationFixtureCaseResult:
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

    if _str_field(payloads[CASE_METADATA_FILE], "case_id") != case_id:
        return _case_input_error(path, "case_id_mismatch")

    expected_status, expected_reason, expected_exit = _expected_result(payloads)
    mismatch_reasons = _case_mismatch_reasons(
        path, payloads, expected_status, expected_reason, expected_exit
    )

    return RuntimeInvocationFixtureCaseResult(
        case_id=case_id,
        case_kind=case_kind,
        expected_status=expected_status,
        expected_reason_code=expected_reason,
        expected_exit_code_category=expected_exit,
        matched=not mismatch_reasons,
        input_error=False,
        mismatch_reasons=tuple(mismatch_reasons),
    )


def summarize_runtime_invocation_fixture_validation(
    summary: RuntimeInvocationFixtureValidationSummary,
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
        "missing_required_file_cases": summary.missing_required_file_cases,
        "unexpected_json_file_cases": summary.unexpected_json_file_cases,
        "content_suppressed": True,
        "body_suppressed": True,
        "metadata_only_checked": True,
        "synthetic_only_checked": True,
        "no_oracle_checked": True,
        "runtime_invocation_fixture_root_checked": True,
        "runtime_schema_checked": True,
        "integration_mode_checked": True,
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
        description="Validate artifact body generation runtime invocation fixtures."
    )
    parser.add_argument("--fixture-root", default=str(DEFAULT_FIXTURE_ROOT))
    args = parser.parse_args(argv)

    summary = validate_runtime_invocation_fixture_root(args.fixture_root)
    payload = summarize_runtime_invocation_fixture_validation(
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


def _case_input_error(case_dir: Path, reason: str) -> RuntimeInvocationFixtureCaseResult:
    return RuntimeInvocationFixtureCaseResult(
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
        if _str_field(payload, "case_id") != case_id:
            mismatches.append(f"{file_name}:case_id_mismatch")
        if _str_field(payload, "case_kind") != case_kind:
            mismatches.append(f"{file_name}:case_kind_mismatch")

    mismatches.extend(_schema_mismatches(payloads, expected_reason))
    mismatches.extend(_common_contract_mismatches(payloads))
    mismatches.extend(
        _expected_result_mismatches(
            payloads, expected_status, expected_reason, expected_exit
        )
    )
    mismatches.extend(_unsafe_marker_mismatches(payloads, expected_reason))
    unsafe_value_reason = _unsafe_value_reason(payloads)
    if unsafe_value_reason:
        mismatches.append(unsafe_value_reason)
    return mismatches


def _schema_mismatches(
    payloads: Mapping[str, Mapping[str, Any]], expected_reason: str
) -> list[str]:
    mismatches: list[str] = []
    for file_name, payload in payloads.items():
        schema = _str_field(payload, "fixture_schema_version")
        if expected_reason == "unsupported_schema" and schema == UNSUPPORTED_FIXTURE_SCHEMA_VERSION:
            continue
        if schema != FIXTURE_SCHEMA_VERSION:
            mismatches.append(f"{file_name}:fixture_schema_version")
        if _str_field(payload, "runtime_schema_version") != RUNTIME_SCHEMA_VERSION:
            mismatches.append(f"{file_name}:runtime_schema_version")
        if _str_field(payload, "validation_schema_version") != VALIDATION_SCHEMA_VERSION:
            mismatches.append(f"{file_name}:validation_schema_version")
        if _str_field(payload, "integration_mode") != INTEGRATION_MODE:
            mismatches.append(f"{file_name}:integration_mode")
    return mismatches


def _common_contract_mismatches(
    payloads: Mapping[str, Mapping[str, Any]]
) -> list[str]:
    mismatches: list[str] = []
    for file_name, payload in payloads.items():
        if _str_field(payload, "fixture_stage") != FIXTURE_STAGE:
            mismatches.append(f"{file_name}:fixture_stage")
        if _str_field(payload, "planned_fixture_root") != PLANNED_FIXTURE_ROOT_LABEL:
            mismatches.append(f"{file_name}:planned_fixture_root")
        for key in ("synthetic_only", "metadata_only", "no_oracle", "body_free"):
            if payload.get(key) is not True:
                mismatches.append(f"{file_name}:{key}")
        if "count_only_where_applicable" in payload and payload.get(
            "count_only_where_applicable"
        ) is not True:
            mismatches.append(f"{file_name}:count_only_where_applicable")
        if "validator_implemented" in payload and payload.get("validator_implemented") is not False:
            mismatches.append(f"{file_name}:validator_implemented")
        if "runtime_invocation_implemented" in payload and payload.get(
            "runtime_invocation_implemented"
        ) is not False:
            mismatches.append(f"{file_name}:runtime_invocation_implemented")
        if "release_quality_integrated" in payload and payload.get(
            "release_quality_integrated"
        ) is not False:
            mismatches.append(f"{file_name}:release_quality_integrated")
        if "manifest_writer_integrated" in payload and payload.get(
            "manifest_writer_integrated"
        ) is not False:
            mismatches.append(f"{file_name}:manifest_writer_integrated")
        if "file_writing_enabled" in payload and payload.get("file_writing_enabled") is not False:
            mismatches.append(f"{file_name}:file_writing_enabled")
    return mismatches


def _expected_result_mismatches(
    payloads: Mapping[str, Mapping[str, Any]],
    expected_status: str,
    expected_reason: str,
    expected_exit: str,
) -> list[str]:
    mismatches: list[str] = []
    for file_name in (
        CASE_METADATA_FILE,
        EXPECTED_SUMMARY_FILE,
        EXPECTED_ERROR_FILE,
    ):
        payload = payloads[file_name]
        status_key = "expected_runtime_status" if file_name != EXPECTED_ERROR_FILE else "expected_status"
        reason_key = "expected_reason_code"
        if _str_field(payload, status_key) != expected_status:
            mismatches.append(f"{file_name}:{status_key}")
        if _str_field(payload, reason_key) != expected_reason:
            mismatches.append(f"{file_name}:expected_reason_code")

    runtime_summary = payloads[RUNTIME_SUMMARY_FILE]
    if _str_field(runtime_summary, "status") != expected_status:
        mismatches.append(f"{RUNTIME_SUMMARY_FILE}:status")
    if _str_field(runtime_summary, "reason_code") != expected_reason:
        mismatches.append(f"{RUNTIME_SUMMARY_FILE}:reason_code")
    if _str_field(runtime_summary, "exit_code_category") != expected_exit:
        mismatches.append(f"{RUNTIME_SUMMARY_FILE}:exit_code_category")

    expected_error = payloads[EXPECTED_ERROR_FILE]
    if expected_error.get("public_safe_reason_only") is not True:
        mismatches.append(f"{EXPECTED_ERROR_FILE}:public_safe_reason_only")
    if expected_error.get("unsafe_values_echoed") is not False:
        mismatches.append(f"{EXPECTED_ERROR_FILE}:unsafe_values_echoed")
    if expected_status == "pass":
        if expected_error.get("expected_error_present") is not False:
            mismatches.append(f"{EXPECTED_ERROR_FILE}:expected_error_present")
    elif expected_error.get("expected_error_present") is not True:
        mismatches.append(f"{EXPECTED_ERROR_FILE}:expected_error_present")
    return mismatches


def _unsafe_marker_mismatches(
    payloads: Mapping[str, Mapping[str, Any]],
    expected_reason: str,
) -> list[str]:
    mismatches: list[str] = []
    expected_count = 0 if expected_reason == "none" else 1
    if _int_field(payloads[CASE_METADATA_FILE], "unsafe_signal_count") != expected_count:
        mismatches.append(f"{CASE_METADATA_FILE}:unsafe_signal_count")
    if _int_field(payloads[RUNTIME_SUMMARY_FILE], "unsafe_signal_count") != expected_count:
        mismatches.append(f"{RUNTIME_SUMMARY_FILE}:unsafe_signal_count")
    if "expected_unsafe_signal_count" in payloads[EXPECTED_SUMMARY_FILE] and _int_field(
        payloads[EXPECTED_SUMMARY_FILE], "expected_unsafe_signal_count"
    ) != expected_count:
        mismatches.append(f"{EXPECTED_SUMMARY_FILE}:expected_unsafe_signal_count")

    if expected_reason == "none":
        return mismatches

    if expected_reason in MARKER_FIELDS_BY_REASON:
        if not any(
            payloads[file_name].get(field_name) is True
            for file_name, field_name in MARKER_FIELDS_BY_REASON[expected_reason]
        ):
            mismatches.append(f"{expected_reason}:marker_missing")
    if expected_reason == "unsupported_schema" and payloads[CASE_METADATA_FILE].get(
        "fixture_schema_version"
    ) != UNSUPPORTED_FIXTURE_SCHEMA_VERSION:
        mismatches.append("unsupported_schema_marker_missing")
    if expected_reason == "mismatched_expected_status" and payloads[RUNTIME_SUMMARY_FILE].get(
        "reason_code"
    ) != "mismatched_expected_status":
        mismatches.append("mismatched_expected_status_marker_missing")
    return mismatches


def _expected_result(payloads: Mapping[str, Mapping[str, Any]]) -> tuple[str, str, str]:
    expected_error = payloads[EXPECTED_ERROR_FILE]
    expected_summary = payloads[EXPECTED_SUMMARY_FILE]
    status = _str_field(expected_error, "expected_status", "usage_error")
    reason = _str_field(expected_error, "expected_reason_code", "malformed_expected_error")
    exit_code = _str_field(
        expected_summary,
        "expected_exit_code_category",
        _str_field(
            expected_error,
            "expected_exit_code_category",
            EXPECTED_EXIT_CODE_BY_STATUS.get(status, "usage_error"),
        ),
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


def _str_field(payload: Mapping[str, Any], key: str, default: str = "") -> str:
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
