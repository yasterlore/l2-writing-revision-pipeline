"""Run an actual-controlled v0.4 multi-case runtime smoke boundary.

This runner executes the existing v0.4 controlled metadata-only runtime helper
over the all-valid actual-controlled fixture matrix and emits an aggregate
public-safe summary. It does not call the manifest writer, write files, emit
payload bodies, train models, or compute metrics.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from learner_state.frozen_policy_generation_artifact_body_generation_runtime_integration import (
    ACTUAL_CONTROLLED_ARTIFACT_BODY_RUNTIME_INVOCATION_MODE,
    ACTUAL_CONTROLLED_RUNTIME_MODE,
    ACTUAL_CONTROLLED_RUNTIME_SCHEMA_VERSION,
    run_artifact_body_generation_runtime_integration_for_fixture_case,
)

DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation"
    "_actual_controlled"
)

MODE = "actual_controlled_v0_4_multi_case_runtime_smoke"
SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_actual_controlled_v0_4_"
    "multi_case_runtime_smoke_v0.1"
)
MATRIX_NAME = "actual_controlled_v0_4_all_valid_runtime_smoke"
CASE_SELECTION_ALL_VALID = "all-valid"
EXPECTED_VALID_CASE_COUNT = 6

PASS_STATUS = "pass"
USAGE_ERROR_STATUS = "usage_error"
FAIL_CLOSED_STATUS = "fail_closed"
MISMATCH_STATUS = "mismatch"

SUMMARY_KEYS = (
    "mode",
    "schema_version",
    "status",
    "reason_code",
    "matrix_name",
    "case_selection",
    "selected_case_count",
    "selected_valid_case_count",
    "selected_invalid_case_count",
    "executed_case_count",
    "pass_case_count",
    "usage_error_case_count",
    "fail_closed_case_count",
    "mismatch_case_count",
    "input_error_case_count",
    "runtime_schema_version",
    "integration_mode",
    "all_cases_artifact_body_runtime_invoked",
    "all_cases_controlled_metadata_only_invocation",
    "artifact_body_generation_cli_invoked_case_count",
    "artifact_body_generation_cli_output_scanned_case_count",
    "artifact_body_generation_cli_output_body_free_case_count",
    "artifact_body_payload_emitted_case_count",
    "manifest_writer_invoked_case_count",
    "file_writing_enabled_case_count",
    "artifact_file_written_case_count",
    "manifest_file_written_case_count",
    "raw_stdout_body_suppressed_case_count",
    "raw_stderr_body_suppressed_case_count",
    "request_body_detected_case_count",
    "pointer_body_detected_case_count",
    "expected_body_detected_case_count",
    "artifact_body_payload_detected_case_count",
    "manifest_body_detected_case_count",
    "generated_policy_body_detected_case_count",
    "raw_rows_detected_case_count",
    "logits_detected_case_count",
    "probabilities_detected_case_count",
    "private_path_detected_case_count",
    "absolute_path_detected_case_count",
    "raw_learner_text_detected_case_count",
    "real_data_marker_detected_case_count",
    "performance_metric_body_detected_case_count",
    "runtime_safety_scan_passed_case_count",
    "unsafe_signal_total_count",
    "residue_file_count",
    "safe_metadata_body_field_count_min",
    "safe_metadata_body_field_count_max",
    "safe_metadata_body_field_count_unique_values",
    "content_suppressed",
    "body_suppressed",
    "metadata_only_checked",
    "synthetic_only_checked",
    "no_oracle_checked",
    "production_readiness_claimed",
    "real_data_readiness_claimed",
    "performance_claims_present",
)


@dataclass(frozen=True)
class MultiCaseRuntimeSmokeSummary:
    status: str
    reason_code: str
    case_selection: str = CASE_SELECTION_ALL_VALID
    selected_case_count: int = 0
    selected_valid_case_count: int = 0
    selected_invalid_case_count: int = 0
    executed_case_count: int = 0
    pass_case_count: int = 0
    usage_error_case_count: int = 0
    fail_closed_case_count: int = 0
    mismatch_case_count: int = 0
    input_error_case_count: int = 0
    all_cases_artifact_body_runtime_invoked: bool = False
    all_cases_controlled_metadata_only_invocation: bool = False
    artifact_body_generation_cli_invoked_case_count: int = 0
    artifact_body_generation_cli_output_scanned_case_count: int = 0
    artifact_body_generation_cli_output_body_free_case_count: int = 0
    artifact_body_payload_emitted_case_count: int = 0
    manifest_writer_invoked_case_count: int = 0
    file_writing_enabled_case_count: int = 0
    artifact_file_written_case_count: int = 0
    manifest_file_written_case_count: int = 0
    raw_stdout_body_suppressed_case_count: int = 0
    raw_stderr_body_suppressed_case_count: int = 0
    request_body_detected_case_count: int = 0
    pointer_body_detected_case_count: int = 0
    expected_body_detected_case_count: int = 0
    artifact_body_payload_detected_case_count: int = 0
    manifest_body_detected_case_count: int = 0
    generated_policy_body_detected_case_count: int = 0
    raw_rows_detected_case_count: int = 0
    logits_detected_case_count: int = 0
    probabilities_detected_case_count: int = 0
    private_path_detected_case_count: int = 0
    absolute_path_detected_case_count: int = 0
    raw_learner_text_detected_case_count: int = 0
    real_data_marker_detected_case_count: int = 0
    performance_metric_body_detected_case_count: int = 0
    runtime_safety_scan_passed_case_count: int = 0
    unsafe_signal_total_count: int = 0
    residue_file_count: int = 0
    safe_metadata_body_field_count_min: int = 0
    safe_metadata_body_field_count_max: int = 0
    safe_metadata_body_field_count_unique_values: str = "none"
    content_suppressed: bool = True
    body_suppressed: bool = True
    metadata_only_checked: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    production_readiness_claimed: bool = False
    real_data_readiness_claimed: bool = False
    performance_claims_present: bool = False

    @property
    def return_code(self) -> int:
        if self.status == PASS_STATUS:
            return 0
        if self.status == USAGE_ERROR_STATUS:
            return 2
        return 1

    def to_public_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "mode": MODE,
            "schema_version": SCHEMA_VERSION,
            "status": self.status,
            "reason_code": self.reason_code,
            "matrix_name": MATRIX_NAME,
            "case_selection": self.case_selection,
            "selected_case_count": self.selected_case_count,
            "selected_valid_case_count": self.selected_valid_case_count,
            "selected_invalid_case_count": self.selected_invalid_case_count,
            "executed_case_count": self.executed_case_count,
            "pass_case_count": self.pass_case_count,
            "usage_error_case_count": self.usage_error_case_count,
            "fail_closed_case_count": self.fail_closed_case_count,
            "mismatch_case_count": self.mismatch_case_count,
            "input_error_case_count": self.input_error_case_count,
            "runtime_schema_version": ACTUAL_CONTROLLED_RUNTIME_SCHEMA_VERSION,
            "integration_mode": ACTUAL_CONTROLLED_ARTIFACT_BODY_RUNTIME_INVOCATION_MODE,
            "all_cases_artifact_body_runtime_invoked": (
                self.all_cases_artifact_body_runtime_invoked
            ),
            "all_cases_controlled_metadata_only_invocation": (
                self.all_cases_controlled_metadata_only_invocation
            ),
            "artifact_body_generation_cli_invoked_case_count": (
                self.artifact_body_generation_cli_invoked_case_count
            ),
            "artifact_body_generation_cli_output_scanned_case_count": (
                self.artifact_body_generation_cli_output_scanned_case_count
            ),
            "artifact_body_generation_cli_output_body_free_case_count": (
                self.artifact_body_generation_cli_output_body_free_case_count
            ),
            "artifact_body_payload_emitted_case_count": (
                self.artifact_body_payload_emitted_case_count
            ),
            "manifest_writer_invoked_case_count": (
                self.manifest_writer_invoked_case_count
            ),
            "file_writing_enabled_case_count": self.file_writing_enabled_case_count,
            "artifact_file_written_case_count": self.artifact_file_written_case_count,
            "manifest_file_written_case_count": self.manifest_file_written_case_count,
            "raw_stdout_body_suppressed_case_count": (
                self.raw_stdout_body_suppressed_case_count
            ),
            "raw_stderr_body_suppressed_case_count": (
                self.raw_stderr_body_suppressed_case_count
            ),
            "request_body_detected_case_count": self.request_body_detected_case_count,
            "pointer_body_detected_case_count": self.pointer_body_detected_case_count,
            "expected_body_detected_case_count": self.expected_body_detected_case_count,
            "artifact_body_payload_detected_case_count": (
                self.artifact_body_payload_detected_case_count
            ),
            "manifest_body_detected_case_count": self.manifest_body_detected_case_count,
            "generated_policy_body_detected_case_count": (
                self.generated_policy_body_detected_case_count
            ),
            "raw_rows_detected_case_count": self.raw_rows_detected_case_count,
            "logits_detected_case_count": self.logits_detected_case_count,
            "probabilities_detected_case_count": (
                self.probabilities_detected_case_count
            ),
            "private_path_detected_case_count": self.private_path_detected_case_count,
            "absolute_path_detected_case_count": self.absolute_path_detected_case_count,
            "raw_learner_text_detected_case_count": (
                self.raw_learner_text_detected_case_count
            ),
            "real_data_marker_detected_case_count": (
                self.real_data_marker_detected_case_count
            ),
            "performance_metric_body_detected_case_count": (
                self.performance_metric_body_detected_case_count
            ),
            "runtime_safety_scan_passed_case_count": (
                self.runtime_safety_scan_passed_case_count
            ),
            "unsafe_signal_total_count": self.unsafe_signal_total_count,
            "residue_file_count": self.residue_file_count,
            "safe_metadata_body_field_count_min": (
                self.safe_metadata_body_field_count_min
            ),
            "safe_metadata_body_field_count_max": (
                self.safe_metadata_body_field_count_max
            ),
            "safe_metadata_body_field_count_unique_values": (
                self.safe_metadata_body_field_count_unique_values
            ),
            "content_suppressed": self.content_suppressed,
            "body_suppressed": self.body_suppressed,
            "metadata_only_checked": self.metadata_only_checked,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
            "production_readiness_claimed": self.production_readiness_claimed,
            "real_data_readiness_claimed": self.real_data_readiness_claimed,
            "performance_claims_present": self.performance_claims_present,
        }
        return {key: payload[key] for key in SUMMARY_KEYS}


def discover_all_valid_case_ids(fixture_root: str | Path) -> tuple[list[str], str]:
    root = Path(fixture_root)
    if not root.is_dir():
        return [], "missing_fixture_root"
    valid_dir = root / "valid"
    if not valid_dir.is_dir():
        return [], "valid_directory_missing"

    case_ids: list[str] = []
    for entry in sorted(valid_dir.iterdir(), key=lambda path: path.name):
        if entry.name.startswith(".") or not entry.is_dir():
            return [], "unexpected_non_directory_entry"
        case_ids.append(f"valid/{entry.name}")

    if not case_ids:
        return [], "zero_valid_cases"
    if len(case_ids) != len(set(case_ids)):
        return [], "duplicate_case_id"
    if len(case_ids) != EXPECTED_VALID_CASE_COUNT:
        return case_ids, "unexpected_valid_case_count"
    return case_ids, "none"


def run_multi_case_runtime_smoke(
    fixture_root: str | Path,
    *,
    case_selection: str,
    summary_only: bool,
    no_file_writing: bool,
    no_manifest_writer: bool,
    fail_closed_on_unsafe_output: bool,
    selected_case_ids: Sequence[str] | None = None,
    expected_executed_case_count: int = EXPECTED_VALID_CASE_COUNT,
) -> MultiCaseRuntimeSmokeSummary:
    if case_selection != CASE_SELECTION_ALL_VALID:
        return _usage_error("invalid_case_selection", case_selection=case_selection)
    if not (summary_only and no_file_writing and no_manifest_writer and fail_closed_on_unsafe_output):
        return _usage_error("missing_required_cli_flag", case_selection=case_selection)

    if selected_case_ids is None:
        case_ids, discovery_reason = discover_all_valid_case_ids(fixture_root)
        if discovery_reason != "none":
            return _usage_error(
                discovery_reason,
                case_selection=case_selection,
                selected_case_count=len(case_ids),
                selected_valid_case_count=_count_valid(case_ids),
                selected_invalid_case_count=_count_invalid(case_ids),
            )
    else:
        case_ids = list(selected_case_ids)
        validation_reason = _validate_selected_case_ids(case_ids)
        if validation_reason != "none":
            return _usage_error(
                validation_reason,
                case_selection=case_selection,
                selected_case_count=len(case_ids),
                selected_valid_case_count=_count_valid(case_ids),
                selected_invalid_case_count=_count_invalid(case_ids),
            )

    summaries = [
        run_artifact_body_generation_runtime_integration_for_fixture_case(
            fixture_root,
            case_id,
            mode=ACTUAL_CONTROLLED_ARTIFACT_BODY_RUNTIME_INVOCATION_MODE,
            summary_only=True,
            no_file_writing=True,
            no_manifest_writer=True,
            fail_closed_on_unsafe_output=True,
            actual_invocation=True,
        )
        for case_id in case_ids
    ]

    aggregate = _aggregate_summaries(case_ids, summaries)
    if aggregate.status == PASS_STATUS and aggregate.executed_case_count != expected_executed_case_count:
        return _replace_status(
            aggregate,
            status=MISMATCH_STATUS,
            reason_code="expected_aggregate_count_mismatch",
        )
    return aggregate


def format_public_summary(payload: Mapping[str, Any]) -> str:
    return "\n".join(f"{key}={_format_value(payload[key])}" for key in SUMMARY_KEYS)


def _aggregate_summaries(
    case_ids: Sequence[str],
    summaries: Sequence[Any],
) -> MultiCaseRuntimeSmokeSummary:
    executed_case_count = len(summaries)
    pass_case_count = _count_status(summaries, PASS_STATUS)
    usage_error_case_count = _count_status(summaries, USAGE_ERROR_STATUS)
    fail_closed_case_count = _count_status(summaries, FAIL_CLOSED_STATUS)
    mismatch_case_count = _count_status(summaries, MISMATCH_STATUS)
    safe_metadata_counts = [
        summary.safe_metadata_body_field_count
        for summary in summaries
        if isinstance(summary.safe_metadata_body_field_count, int)
    ]

    status = PASS_STATUS
    reason_code = "none"
    consistency_reason = _first_consistency_mismatch_reason(summaries)
    if usage_error_case_count:
        status = USAGE_ERROR_STATUS
        reason_code = _first_non_pass_reason(summaries)
    elif fail_closed_case_count:
        status = FAIL_CLOSED_STATUS
        reason_code = _first_non_pass_reason(summaries)
    elif mismatch_case_count:
        status = MISMATCH_STATUS
        reason_code = _first_non_pass_reason(summaries)
    elif consistency_reason != "none":
        status = MISMATCH_STATUS
        reason_code = consistency_reason

    return MultiCaseRuntimeSmokeSummary(
        status=status,
        reason_code=reason_code,
        selected_case_count=len(case_ids),
        selected_valid_case_count=_count_valid(case_ids),
        selected_invalid_case_count=_count_invalid(case_ids),
        executed_case_count=executed_case_count,
        pass_case_count=pass_case_count,
        usage_error_case_count=usage_error_case_count,
        fail_closed_case_count=fail_closed_case_count,
        mismatch_case_count=mismatch_case_count,
        all_cases_artifact_body_runtime_invoked=(
            executed_case_count > 0
            and all(summary.artifact_body_runtime_invoked is True for summary in summaries)
        ),
        all_cases_controlled_metadata_only_invocation=(
            executed_case_count > 0
            and all(
                summary.artifact_body_runtime_mode == ACTUAL_CONTROLLED_RUNTIME_MODE
                for summary in summaries
            )
        ),
        artifact_body_generation_cli_invoked_case_count=_count_truthy(
            summaries, "artifact_body_generation_cli_invoked"
        ),
        artifact_body_generation_cli_output_scanned_case_count=_count_truthy(
            summaries, "artifact_body_generation_cli_output_scanned"
        ),
        artifact_body_generation_cli_output_body_free_case_count=_count_truthy(
            summaries, "artifact_body_generation_cli_output_body_free"
        ),
        artifact_body_payload_emitted_case_count=_count_truthy(
            summaries, "artifact_body_payload_emitted"
        ),
        manifest_writer_invoked_case_count=_count_truthy(
            summaries, "manifest_writer_invoked"
        ),
        file_writing_enabled_case_count=_count_truthy(summaries, "file_writing_enabled"),
        artifact_file_written_case_count=_count_truthy(summaries, "artifact_file_written"),
        manifest_file_written_case_count=_count_truthy(summaries, "manifest_file_written"),
        raw_stdout_body_suppressed_case_count=_count_truthy(
            summaries, "raw_stdout_body_suppressed"
        ),
        raw_stderr_body_suppressed_case_count=_count_truthy(
            summaries, "raw_stderr_body_suppressed"
        ),
        request_body_detected_case_count=_count_truthy(summaries, "request_body_detected"),
        pointer_body_detected_case_count=_count_truthy(summaries, "pointer_body_detected"),
        expected_body_detected_case_count=_count_truthy(
            summaries, "expected_body_detected"
        ),
        artifact_body_payload_detected_case_count=_count_truthy(
            summaries, "artifact_body_payload_detected"
        ),
        manifest_body_detected_case_count=_count_truthy(summaries, "manifest_body_detected"),
        generated_policy_body_detected_case_count=_count_truthy(
            summaries, "generated_policy_body_detected"
        ),
        raw_rows_detected_case_count=_count_truthy(summaries, "raw_rows_detected"),
        logits_detected_case_count=_count_truthy(summaries, "logits_detected"),
        probabilities_detected_case_count=_count_truthy(summaries, "probabilities_detected"),
        private_path_detected_case_count=_count_truthy(summaries, "private_path_detected"),
        absolute_path_detected_case_count=_count_truthy(summaries, "absolute_path_detected"),
        raw_learner_text_detected_case_count=_count_truthy(
            summaries, "raw_learner_text_detected"
        ),
        real_data_marker_detected_case_count=_count_truthy(
            summaries, "real_data_marker_detected"
        ),
        performance_metric_body_detected_case_count=_count_truthy(
            summaries, "performance_metric_body_detected"
        ),
        runtime_safety_scan_passed_case_count=_count_truthy(
            summaries, "runtime_safety_scan_passed"
        ),
        unsafe_signal_total_count=sum(
            _safe_int(summary.unsafe_signal_count) for summary in summaries
        ),
        residue_file_count=sum(_safe_int(summary.residue_file_count) for summary in summaries),
        safe_metadata_body_field_count_min=(
            min(safe_metadata_counts) if safe_metadata_counts else 0
        ),
        safe_metadata_body_field_count_max=(
            max(safe_metadata_counts) if safe_metadata_counts else 0
        ),
        safe_metadata_body_field_count_unique_values=_unique_values_text(
            safe_metadata_counts
        ),
        content_suppressed=all(summary.content_suppressed is True for summary in summaries),
        body_suppressed=all(summary.body_suppressed is True for summary in summaries),
        production_readiness_claimed=any(
            summary.production_readiness_claimed is True for summary in summaries
        ),
        real_data_readiness_claimed=any(
            summary.real_data_readiness_claimed is True for summary in summaries
        ),
        performance_claims_present=any(
            summary.performance_claims_present is True for summary in summaries
        ),
    )


def _validate_selected_case_ids(case_ids: Sequence[str]) -> str:
    if not case_ids:
        return "zero_valid_cases"
    if len(case_ids) != len(set(case_ids)):
        return "duplicate_case_id"
    if any(not case_id.startswith("valid/") for case_id in case_ids):
        return "unexpected_invalid_case_selected"
    if len(case_ids) != EXPECTED_VALID_CASE_COUNT:
        return "unexpected_valid_case_count"
    return "none"


def _first_consistency_mismatch_reason(summaries: Sequence[Any]) -> str:
    for summary in summaries:
        if summary.runtime_schema_version != ACTUAL_CONTROLLED_RUNTIME_SCHEMA_VERSION:
            return "expected_schema_or_mode_mismatch"
        if (
            summary.integration_mode
            != ACTUAL_CONTROLLED_ARTIFACT_BODY_RUNTIME_INVOCATION_MODE
        ):
            return "expected_schema_or_mode_mismatch"
        if summary.status == PASS_STATUS and (
            summary.artifact_body_runtime_invoked is not True
            or summary.artifact_body_runtime_mode != ACTUAL_CONTROLLED_RUNTIME_MODE
            or summary.artifact_body_payload_emitted is not False
            or summary.manifest_writer_invoked is not False
            or summary.file_writing_enabled is not False
            or summary.runtime_safety_scan_passed is not True
            or summary.unsafe_signal_count != 0
        ):
            return "expected_safety_flag_mismatch"
    return "none"


def _usage_error(
    reason_code: str,
    *,
    case_selection: str = CASE_SELECTION_ALL_VALID,
    selected_case_count: int = 0,
    selected_valid_case_count: int = 0,
    selected_invalid_case_count: int = 0,
) -> MultiCaseRuntimeSmokeSummary:
    return MultiCaseRuntimeSmokeSummary(
        status=USAGE_ERROR_STATUS,
        reason_code=reason_code,
        case_selection=case_selection,
        selected_case_count=selected_case_count,
        selected_valid_case_count=selected_valid_case_count,
        selected_invalid_case_count=selected_invalid_case_count,
    )


def _replace_status(
    summary: MultiCaseRuntimeSmokeSummary,
    *,
    status: str,
    reason_code: str,
) -> MultiCaseRuntimeSmokeSummary:
    return MultiCaseRuntimeSmokeSummary(
        status=status,
        reason_code=reason_code,
        case_selection=summary.case_selection,
        selected_case_count=summary.selected_case_count,
        selected_valid_case_count=summary.selected_valid_case_count,
        selected_invalid_case_count=summary.selected_invalid_case_count,
        executed_case_count=summary.executed_case_count,
        pass_case_count=summary.pass_case_count,
        usage_error_case_count=summary.usage_error_case_count,
        fail_closed_case_count=summary.fail_closed_case_count,
        mismatch_case_count=summary.mismatch_case_count,
        input_error_case_count=summary.input_error_case_count,
        all_cases_artifact_body_runtime_invoked=(
            summary.all_cases_artifact_body_runtime_invoked
        ),
        all_cases_controlled_metadata_only_invocation=(
            summary.all_cases_controlled_metadata_only_invocation
        ),
        artifact_body_generation_cli_invoked_case_count=(
            summary.artifact_body_generation_cli_invoked_case_count
        ),
        artifact_body_generation_cli_output_scanned_case_count=(
            summary.artifact_body_generation_cli_output_scanned_case_count
        ),
        artifact_body_generation_cli_output_body_free_case_count=(
            summary.artifact_body_generation_cli_output_body_free_case_count
        ),
        artifact_body_payload_emitted_case_count=(
            summary.artifact_body_payload_emitted_case_count
        ),
        manifest_writer_invoked_case_count=summary.manifest_writer_invoked_case_count,
        file_writing_enabled_case_count=summary.file_writing_enabled_case_count,
        artifact_file_written_case_count=summary.artifact_file_written_case_count,
        manifest_file_written_case_count=summary.manifest_file_written_case_count,
        raw_stdout_body_suppressed_case_count=(
            summary.raw_stdout_body_suppressed_case_count
        ),
        raw_stderr_body_suppressed_case_count=(
            summary.raw_stderr_body_suppressed_case_count
        ),
        request_body_detected_case_count=summary.request_body_detected_case_count,
        pointer_body_detected_case_count=summary.pointer_body_detected_case_count,
        expected_body_detected_case_count=summary.expected_body_detected_case_count,
        artifact_body_payload_detected_case_count=(
            summary.artifact_body_payload_detected_case_count
        ),
        manifest_body_detected_case_count=summary.manifest_body_detected_case_count,
        generated_policy_body_detected_case_count=(
            summary.generated_policy_body_detected_case_count
        ),
        raw_rows_detected_case_count=summary.raw_rows_detected_case_count,
        logits_detected_case_count=summary.logits_detected_case_count,
        probabilities_detected_case_count=summary.probabilities_detected_case_count,
        private_path_detected_case_count=summary.private_path_detected_case_count,
        absolute_path_detected_case_count=summary.absolute_path_detected_case_count,
        raw_learner_text_detected_case_count=summary.raw_learner_text_detected_case_count,
        real_data_marker_detected_case_count=summary.real_data_marker_detected_case_count,
        performance_metric_body_detected_case_count=(
            summary.performance_metric_body_detected_case_count
        ),
        runtime_safety_scan_passed_case_count=(
            summary.runtime_safety_scan_passed_case_count
        ),
        unsafe_signal_total_count=summary.unsafe_signal_total_count,
        residue_file_count=summary.residue_file_count,
        safe_metadata_body_field_count_min=summary.safe_metadata_body_field_count_min,
        safe_metadata_body_field_count_max=summary.safe_metadata_body_field_count_max,
        safe_metadata_body_field_count_unique_values=(
            summary.safe_metadata_body_field_count_unique_values
        ),
        content_suppressed=summary.content_suppressed,
        body_suppressed=summary.body_suppressed,
        metadata_only_checked=summary.metadata_only_checked,
        synthetic_only_checked=summary.synthetic_only_checked,
        no_oracle_checked=summary.no_oracle_checked,
        production_readiness_claimed=summary.production_readiness_claimed,
        real_data_readiness_claimed=summary.real_data_readiness_claimed,
        performance_claims_present=summary.performance_claims_present,
    )


def _count_valid(case_ids: Sequence[str]) -> int:
    return sum(1 for case_id in case_ids if case_id.startswith("valid/"))


def _count_invalid(case_ids: Sequence[str]) -> int:
    return sum(1 for case_id in case_ids if case_id.startswith("invalid/"))


def _count_status(summaries: Sequence[Any], status: str) -> int:
    return sum(1 for summary in summaries if summary.status == status)


def _count_truthy(summaries: Sequence[Any], field_name: str) -> int:
    return sum(1 for summary in summaries if getattr(summary, field_name) is True)


def _first_non_pass_reason(summaries: Sequence[Any]) -> str:
    for summary in summaries:
        if summary.status != PASS_STATUS:
            return summary.reason_code
    return "none"


def _safe_int(value: Any) -> int:
    return value if isinstance(value, int) else 0


def _unique_values_text(values: Sequence[int]) -> str:
    unique_values = sorted(set(values))
    if not unique_values:
        return "none"
    return ",".join(str(value) for value in unique_values)


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run an actual-controlled v0.4 multi-case runtime smoke over "
            "synthetic metadata-only fixture cases."
        ),
        add_help=True,
    )
    parser.add_argument("--fixture-root")
    parser.add_argument("--case-selection")
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--no-file-writing", action="store_true")
    parser.add_argument("--no-manifest-writer", action="store_true")
    parser.add_argument("--fail-closed-on-unsafe-output", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_arg_parser()
    args, unknown_args = parser.parse_known_args(argv)
    if unknown_args:
        summary = _usage_error("unsupported_cli_argument")
    elif not args.fixture_root:
        summary = _usage_error("missing_fixture_root")
    else:
        summary = run_multi_case_runtime_smoke(
            args.fixture_root,
            case_selection=args.case_selection or "missing",
            summary_only=args.summary_only,
            no_file_writing=args.no_file_writing,
            no_manifest_writer=args.no_manifest_writer,
            fail_closed_on_unsafe_output=args.fail_closed_on_unsafe_output,
        )
    print(format_public_summary(summary.to_public_dict()))
    return summary.return_code


if __name__ == "__main__":
    sys.exit(main())
