"""Run an actual-controlled v0.4 invalid-case fail-closed runtime smoke.

This runner executes the existing v0.4 controlled metadata-only runtime helper
over the selected invalid fail-closed fixture matrix and emits an aggregate
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
    ACTUAL_CONTROLLED_RUNTIME_SCHEMA_VERSION,
    run_artifact_body_generation_runtime_integration_for_fixture_case,
)

DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation"
    "_actual_controlled"
)

MODE = "actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke"
SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_actual_controlled_v0_4_"
    "invalid_case_runtime_fail_closed_smoke_v0.1"
)
MATRIX_NAME = "actual_controlled_v0_4_invalid_fail_closed_runtime_smoke"
CASE_SELECTION_FAIL_CLOSED_INVALID = "fail-closed-invalid"

PASS_STATUS = "pass"
USAGE_ERROR_STATUS = "usage_error"
FAIL_CLOSED_STATUS = "fail_closed"
MISMATCH_STATUS = "mismatch"

SELECTED_FAIL_CLOSED_INVALID_CASE_IDS: tuple[str, ...] = (
    "invalid/invalid_absolute_path_present",
    "invalid/invalid_artifact_body_cli_nonzero_exit",
    "invalid/invalid_artifact_body_cli_output_not_body_free",
    "invalid/invalid_artifact_body_payload_present",
    "invalid/invalid_expected_body_present",
    "invalid/invalid_file_writing_detected",
    "invalid/invalid_file_writing_requested",
    "invalid/invalid_generated_policy_body_present",
    "invalid/invalid_logits_present",
    "invalid/invalid_manifest_body_present",
    "invalid/invalid_manifest_writer_invoked",
    "invalid/invalid_manifest_writer_requested",
    "invalid/invalid_no_oracle_forbidden_field",
    "invalid/invalid_performance_metric_body_present",
    "invalid/invalid_pointer_body_present",
    "invalid/invalid_private_path_present",
    "invalid/invalid_probabilities_present",
    "invalid/invalid_raw_learner_text_present",
    "invalid/invalid_raw_rows_present",
    "invalid/invalid_raw_stderr_body_present",
    "invalid/invalid_raw_stdout_body_present",
    "invalid/invalid_real_data_marker_present",
    "invalid/invalid_request_body_present",
    "invalid/invalid_unexpected_artifact_body_generation_request",
    "invalid/invalid_unsafe_artifact_body_runtime_mode",
    "invalid/invalid_unsafe_output_residue_risk",
)
DEFERRED_INVALID_CASE_IDS: tuple[str, ...] = (
    "invalid/invalid_malformed_metadata_json",
    "invalid/invalid_missing_required_metadata_file",
    "invalid/invalid_mismatched_expected_status",
    "invalid/invalid_unsupported_schema",
)
EXPECTED_SELECTED_CASE_COUNT = 26
EXPECTED_DEFERRED_CASE_COUNT = 4

SUMMARY_KEYS = (
    "mode",
    "schema_version",
    "status",
    "reason_code",
    "matrix_name",
    "case_selection",
    "selected_case_count",
    "selected_invalid_case_count",
    "selected_valid_case_count",
    "deferred_case_count",
    "executed_case_count",
    "pass_case_count",
    "expected_fail_closed_case_count",
    "observed_fail_closed_case_count",
    "usage_error_case_count",
    "mismatch_case_count",
    "input_error_case_count",
    "runtime_schema_version",
    "integration_mode",
    "all_selected_cases_failed_closed",
    "artifact_body_payload_emitted_case_count",
    "manifest_writer_invoked_case_count",
    "file_writing_enabled_case_count",
    "artifact_file_written_case_count",
    "manifest_file_written_case_count",
    "raw_stdout_body_suppressed_case_count",
    "raw_stderr_body_suppressed_case_count",
    "forbidden_body_emitted_case_count",
    "unsafe_signal_total_count",
    "residue_file_count",
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
class InvalidCaseRuntimeFailClosedSmokeSummary:
    status: str
    reason_code: str
    case_selection: str = CASE_SELECTION_FAIL_CLOSED_INVALID
    selected_case_count: int = 0
    selected_invalid_case_count: int = 0
    selected_valid_case_count: int = 0
    deferred_case_count: int = EXPECTED_DEFERRED_CASE_COUNT
    executed_case_count: int = 0
    pass_case_count: int = 0
    expected_fail_closed_case_count: int = 0
    observed_fail_closed_case_count: int = 0
    usage_error_case_count: int = 0
    mismatch_case_count: int = 0
    input_error_case_count: int = 0
    all_selected_cases_failed_closed: bool = False
    artifact_body_payload_emitted_case_count: int = 0
    manifest_writer_invoked_case_count: int = 0
    file_writing_enabled_case_count: int = 0
    artifact_file_written_case_count: int = 0
    manifest_file_written_case_count: int = 0
    raw_stdout_body_suppressed_case_count: int = 0
    raw_stderr_body_suppressed_case_count: int = 0
    forbidden_body_emitted_case_count: int = 0
    unsafe_signal_total_count: int = 0
    residue_file_count: int = 0
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
            "selected_invalid_case_count": self.selected_invalid_case_count,
            "selected_valid_case_count": self.selected_valid_case_count,
            "deferred_case_count": self.deferred_case_count,
            "executed_case_count": self.executed_case_count,
            "pass_case_count": self.pass_case_count,
            "expected_fail_closed_case_count": self.expected_fail_closed_case_count,
            "observed_fail_closed_case_count": self.observed_fail_closed_case_count,
            "usage_error_case_count": self.usage_error_case_count,
            "mismatch_case_count": self.mismatch_case_count,
            "input_error_case_count": self.input_error_case_count,
            "runtime_schema_version": ACTUAL_CONTROLLED_RUNTIME_SCHEMA_VERSION,
            "integration_mode": ACTUAL_CONTROLLED_ARTIFACT_BODY_RUNTIME_INVOCATION_MODE,
            "all_selected_cases_failed_closed": self.all_selected_cases_failed_closed,
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
            "forbidden_body_emitted_case_count": self.forbidden_body_emitted_case_count,
            "unsafe_signal_total_count": self.unsafe_signal_total_count,
            "residue_file_count": self.residue_file_count,
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


def discover_fail_closed_invalid_case_ids(
    fixture_root: str | Path,
) -> tuple[list[str], str]:
    root = Path(fixture_root)
    if not root.is_dir():
        return [], "missing_fixture_root"
    invalid_dir = root / "invalid"
    if not invalid_dir.is_dir():
        return [], "invalid_directory_missing"

    discovered_case_ids: list[str] = []
    for entry in sorted(invalid_dir.iterdir(), key=lambda path: path.name):
        if entry.name.startswith(".") or not entry.is_dir():
            return [], "unexpected_non_directory_entry"
        discovered_case_ids.append(f"invalid/{entry.name}")

    expected_all_case_ids = sorted(
        [*SELECTED_FAIL_CLOSED_INVALID_CASE_IDS, *DEFERRED_INVALID_CASE_IDS]
    )
    if discovered_case_ids != expected_all_case_ids:
        return discovered_case_ids, "unexpected_invalid_case_matrix"
    return list(SELECTED_FAIL_CLOSED_INVALID_CASE_IDS), "none"


def run_invalid_case_runtime_fail_closed_smoke(
    fixture_root: str | Path,
    *,
    case_selection: str,
    summary_only: bool,
    no_file_writing: bool,
    no_manifest_writer: bool,
    fail_closed_on_unsafe_output: bool,
    selected_case_ids: Sequence[str] | None = None,
    expected_executed_case_count: int = EXPECTED_SELECTED_CASE_COUNT,
) -> InvalidCaseRuntimeFailClosedSmokeSummary:
    if case_selection != CASE_SELECTION_FAIL_CLOSED_INVALID:
        return _usage_error("invalid_case_selection", case_selection=case_selection)
    if not (
        summary_only
        and no_file_writing
        and no_manifest_writer
        and fail_closed_on_unsafe_output
    ):
        return _usage_error("missing_required_cli_flag", case_selection=case_selection)

    if selected_case_ids is None:
        case_ids, discovery_reason = discover_fail_closed_invalid_case_ids(fixture_root)
        if discovery_reason != "none":
            return _usage_error(
                discovery_reason,
                selected_case_count=len(case_ids),
                selected_invalid_case_count=_count_invalid(case_ids),
                selected_valid_case_count=_count_valid(case_ids),
            )
    else:
        case_ids = list(selected_case_ids)
        validation_reason = _validate_selected_case_ids(case_ids)
        if validation_reason != "none":
            return _usage_error(
                validation_reason,
                selected_case_count=len(case_ids),
                selected_invalid_case_count=_count_invalid(case_ids),
                selected_valid_case_count=_count_valid(case_ids),
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
) -> InvalidCaseRuntimeFailClosedSmokeSummary:
    executed_case_count = len(summaries)
    pass_case_count = _count_status(summaries, PASS_STATUS)
    observed_fail_closed_case_count = _count_status(summaries, FAIL_CLOSED_STATUS)
    usage_error_case_count = _count_status(summaries, USAGE_ERROR_STATUS)
    mismatch_case_count = _count_status(summaries, MISMATCH_STATUS)

    status = PASS_STATUS
    reason_code = "none"
    consistency_reason = _first_consistency_mismatch_reason(summaries)
    if usage_error_case_count:
        status = USAGE_ERROR_STATUS
        reason_code = _first_non_expected_fail_closed_reason(summaries)
    elif pass_case_count:
        status = MISMATCH_STATUS
        reason_code = "selected_invalid_case_passed"
    elif mismatch_case_count:
        status = MISMATCH_STATUS
        reason_code = _first_non_expected_fail_closed_reason(summaries)
    elif observed_fail_closed_case_count != len(case_ids):
        status = MISMATCH_STATUS
        reason_code = "expected_fail_closed_count_mismatch"
    elif consistency_reason != "none":
        status = MISMATCH_STATUS
        reason_code = consistency_reason

    return InvalidCaseRuntimeFailClosedSmokeSummary(
        status=status,
        reason_code=reason_code,
        selected_case_count=len(case_ids),
        selected_invalid_case_count=_count_invalid(case_ids),
        selected_valid_case_count=_count_valid(case_ids),
        executed_case_count=executed_case_count,
        pass_case_count=pass_case_count,
        expected_fail_closed_case_count=len(case_ids),
        observed_fail_closed_case_count=observed_fail_closed_case_count,
        usage_error_case_count=usage_error_case_count,
        mismatch_case_count=mismatch_case_count,
        all_selected_cases_failed_closed=(
            executed_case_count > 0 and observed_fail_closed_case_count == len(case_ids)
        ),
        artifact_body_payload_emitted_case_count=0,
        manifest_writer_invoked_case_count=0,
        file_writing_enabled_case_count=0,
        artifact_file_written_case_count=0,
        manifest_file_written_case_count=0,
        raw_stdout_body_suppressed_case_count=observed_fail_closed_case_count,
        raw_stderr_body_suppressed_case_count=observed_fail_closed_case_count,
        forbidden_body_emitted_case_count=0,
        unsafe_signal_total_count=sum(
            max(1 if summary.status == FAIL_CLOSED_STATUS else 0, _safe_int(summary.unsafe_signal_count))
            for summary in summaries
        ),
        residue_file_count=sum(_safe_int(summary.residue_file_count) for summary in summaries),
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
        return "zero_selected_cases"
    if len(case_ids) != len(set(case_ids)):
        return "duplicate_case_id"
    if any(not case_id.startswith("invalid/") for case_id in case_ids):
        return "unexpected_valid_case_selected"
    if tuple(case_ids) != SELECTED_FAIL_CLOSED_INVALID_CASE_IDS:
        return "unexpected_invalid_case_matrix"
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
        if summary.status == FAIL_CLOSED_STATUS and (
            summary.content_suppressed is not True
            or summary.body_suppressed is not True
            or summary.residue_file_count != 0
        ):
            return "expected_safety_flag_mismatch"
    return "none"


def _usage_error(
    reason_code: str,
    *,
    case_selection: str = CASE_SELECTION_FAIL_CLOSED_INVALID,
    selected_case_count: int = 0,
    selected_invalid_case_count: int = 0,
    selected_valid_case_count: int = 0,
) -> InvalidCaseRuntimeFailClosedSmokeSummary:
    return InvalidCaseRuntimeFailClosedSmokeSummary(
        status=USAGE_ERROR_STATUS,
        reason_code=reason_code,
        case_selection=case_selection,
        selected_case_count=selected_case_count,
        selected_invalid_case_count=selected_invalid_case_count,
        selected_valid_case_count=selected_valid_case_count,
    )


def _replace_status(
    summary: InvalidCaseRuntimeFailClosedSmokeSummary,
    *,
    status: str,
    reason_code: str,
) -> InvalidCaseRuntimeFailClosedSmokeSummary:
    return InvalidCaseRuntimeFailClosedSmokeSummary(
        status=status,
        reason_code=reason_code,
        case_selection=summary.case_selection,
        selected_case_count=summary.selected_case_count,
        selected_invalid_case_count=summary.selected_invalid_case_count,
        selected_valid_case_count=summary.selected_valid_case_count,
        deferred_case_count=summary.deferred_case_count,
        executed_case_count=summary.executed_case_count,
        pass_case_count=summary.pass_case_count,
        expected_fail_closed_case_count=summary.expected_fail_closed_case_count,
        observed_fail_closed_case_count=summary.observed_fail_closed_case_count,
        usage_error_case_count=summary.usage_error_case_count,
        mismatch_case_count=summary.mismatch_case_count,
        input_error_case_count=summary.input_error_case_count,
        all_selected_cases_failed_closed=summary.all_selected_cases_failed_closed,
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
        forbidden_body_emitted_case_count=summary.forbidden_body_emitted_case_count,
        unsafe_signal_total_count=summary.unsafe_signal_total_count,
        residue_file_count=summary.residue_file_count,
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


def _first_non_expected_fail_closed_reason(summaries: Sequence[Any]) -> str:
    for summary in summaries:
        if summary.status != FAIL_CLOSED_STATUS:
            return summary.reason_code
    return "none"


def _safe_int(value: Any) -> int:
    return value if isinstance(value, int) else 0


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run an actual-controlled v0.4 invalid-case fail-closed runtime "
            "smoke over synthetic metadata-only fixture cases."
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
        summary = run_invalid_case_runtime_fail_closed_smoke(
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
