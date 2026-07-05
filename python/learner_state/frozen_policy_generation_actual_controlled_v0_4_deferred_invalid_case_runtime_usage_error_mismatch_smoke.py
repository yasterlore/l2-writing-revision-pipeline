"""Run actual-controlled v0.4 deferred invalid usage_error/mismatch smoke.

This direct CLI-only runner processes the 4 deferred non-fail_closed invalid
fixture cases fixed by the Step625 contract. It emits aggregate public-safe
metadata only. It does not invoke the manifest writer, write files, emit
payload bodies, train models, or compute metrics.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from learner_state.frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke import (
    SELECTED_FAIL_CLOSED_INVALID_CASE_IDS,
)
from learner_state.frozen_policy_generation_artifact_body_generation_runtime_integration import (
    ACTUAL_CONTROLLED_ARTIFACT_BODY_RUNTIME_INVOCATION_MODE,
    ACTUAL_CONTROLLED_RUNTIME_SCHEMA_VERSION,
)

DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation"
    "_actual_controlled"
)

MODE = (
    "actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke"
)
SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_actual_controlled_v0_4_"
    "deferred_invalid_case_runtime_usage_error_mismatch_smoke_v0.1"
)
MATRIX_NAME = "actual_controlled_v0_4_deferred_invalid_usage_error_mismatch_runtime_smoke"
CASE_SELECTION_DEFERRED_INVALID_USAGE_ERROR_MISMATCH = (
    "deferred-invalid-usage-error-mismatch"
)

PASS_STATUS = "pass"
USAGE_ERROR_STATUS = "usage_error"
FAIL_CLOSED_STATUS = "fail_closed"
MISMATCH_STATUS = "mismatch"

EXPECTED_USAGE_ERROR_CASE_IDS: tuple[str, ...] = (
    "invalid/invalid_malformed_metadata_json",
    "invalid/invalid_missing_required_metadata_file",
    "invalid/invalid_unsupported_schema",
)
EXPECTED_MISMATCH_CASE_IDS: tuple[str, ...] = (
    "invalid/invalid_mismatched_expected_status",
)
SELECTED_DEFERRED_INVALID_CASE_IDS: tuple[str, ...] = tuple(
    sorted([*EXPECTED_USAGE_ERROR_CASE_IDS, *EXPECTED_MISMATCH_CASE_IDS])
)
EXPECTED_SELECTED_CASE_COUNT = 4
EXPECTED_USAGE_ERROR_CASE_COUNT = 3
EXPECTED_MISMATCH_CASE_COUNT = 1
EXCLUDED_FAIL_CLOSED_CASE_COUNT = 26
EXCLUDED_VALID_CASE_COUNT = 6

EXPECTED_STATUS_BY_CASE_ID: dict[str, str] = {
    **{case_id: USAGE_ERROR_STATUS for case_id in EXPECTED_USAGE_ERROR_CASE_IDS},
    **{case_id: MISMATCH_STATUS for case_id in EXPECTED_MISMATCH_CASE_IDS},
}
REASON_FAMILY_BY_CASE_ID: dict[str, str] = {
    "invalid/invalid_malformed_metadata_json": "malformed metadata JSON",
    "invalid/invalid_missing_required_metadata_file": "missing required metadata file",
    "invalid/invalid_unsupported_schema": "unsupported schema",
    "invalid/invalid_mismatched_expected_status": "mismatched expected status",
}
REASON_CODE_BY_CASE_ID: dict[str, str] = {
    "invalid/invalid_malformed_metadata_json": "malformed_metadata_json",
    "invalid/invalid_missing_required_metadata_file": "missing_required_metadata_file",
    "invalid/invalid_unsupported_schema": "unsupported_schema",
    "invalid/invalid_mismatched_expected_status": "expected_status_mismatch",
}

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
    "selected_usage_error_case_count",
    "selected_mismatch_case_count",
    "excluded_fail_closed_case_count",
    "excluded_valid_case_count",
    "processed_case_count",
    "preflight_usage_error_case_count",
    "runtime_or_contract_mismatch_case_count",
    "expected_usage_error_case_count",
    "observed_usage_error_case_count",
    "expected_mismatch_case_count",
    "observed_mismatch_case_count",
    "expected_fail_closed_case_count",
    "observed_fail_closed_case_count",
    "expected_pass_case_count",
    "observed_pass_case_count",
    "input_error_case_count",
    "runtime_schema_version",
    "integration_mode",
    "artifact_body_payload_emitted_case_count",
    "manifest_writer_invoked_case_count",
    "file_writing_enabled_case_count",
    "artifact_file_written_case_count",
    "manifest_file_written_case_count",
    "forbidden_body_emitted_case_count",
    "raw_stdout_body_suppressed_case_count",
    "raw_stderr_body_suppressed_case_count",
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
class DeferredInvalidCaseObservation:
    case_id: str
    expected_status: str
    observed_status: str
    reason_code: str
    reason_family: str
    runtime_schema_version: str = ACTUAL_CONTROLLED_RUNTIME_SCHEMA_VERSION
    integration_mode: str = ACTUAL_CONTROLLED_ARTIFACT_BODY_RUNTIME_INVOCATION_MODE
    preflight_checked: bool = True
    runtime_attempted: bool = False
    runtime_full_invocation_required: bool = False
    artifact_body_runtime_invoked: bool = False
    artifact_body_generation_cli_invoked: bool = False
    artifact_body_payload_emitted: bool = False
    manifest_writer_invoked: bool = False
    file_writing_enabled: bool = False
    artifact_file_written: bool = False
    manifest_file_written: bool = False
    raw_stdout_body_suppressed: bool = True
    raw_stderr_body_suppressed: bool = True
    forbidden_body_emitted: bool = False
    unsafe_signal_count: int = 0
    residue_file_count: int = 0


@dataclass(frozen=True)
class DeferredInvalidCaseRuntimeUsageErrorMismatchSmokeSummary:
    status: str
    reason_code: str
    case_selection: str = CASE_SELECTION_DEFERRED_INVALID_USAGE_ERROR_MISMATCH
    selected_case_count: int = 0
    selected_invalid_case_count: int = 0
    selected_valid_case_count: int = 0
    selected_usage_error_case_count: int = 0
    selected_mismatch_case_count: int = 0
    excluded_fail_closed_case_count: int = EXCLUDED_FAIL_CLOSED_CASE_COUNT
    excluded_valid_case_count: int = EXCLUDED_VALID_CASE_COUNT
    processed_case_count: int = 0
    preflight_usage_error_case_count: int = 0
    runtime_or_contract_mismatch_case_count: int = 0
    expected_usage_error_case_count: int = EXPECTED_USAGE_ERROR_CASE_COUNT
    observed_usage_error_case_count: int = 0
    expected_mismatch_case_count: int = EXPECTED_MISMATCH_CASE_COUNT
    observed_mismatch_case_count: int = 0
    expected_fail_closed_case_count: int = 0
    observed_fail_closed_case_count: int = 0
    expected_pass_case_count: int = 0
    observed_pass_case_count: int = 0
    input_error_case_count: int = 0
    artifact_body_payload_emitted_case_count: int = 0
    manifest_writer_invoked_case_count: int = 0
    file_writing_enabled_case_count: int = 0
    artifact_file_written_case_count: int = 0
    manifest_file_written_case_count: int = 0
    forbidden_body_emitted_case_count: int = 0
    raw_stdout_body_suppressed_case_count: int = 0
    raw_stderr_body_suppressed_case_count: int = 0
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
            "selected_usage_error_case_count": self.selected_usage_error_case_count,
            "selected_mismatch_case_count": self.selected_mismatch_case_count,
            "excluded_fail_closed_case_count": self.excluded_fail_closed_case_count,
            "excluded_valid_case_count": self.excluded_valid_case_count,
            "processed_case_count": self.processed_case_count,
            "preflight_usage_error_case_count": self.preflight_usage_error_case_count,
            "runtime_or_contract_mismatch_case_count": (
                self.runtime_or_contract_mismatch_case_count
            ),
            "expected_usage_error_case_count": self.expected_usage_error_case_count,
            "observed_usage_error_case_count": self.observed_usage_error_case_count,
            "expected_mismatch_case_count": self.expected_mismatch_case_count,
            "observed_mismatch_case_count": self.observed_mismatch_case_count,
            "expected_fail_closed_case_count": self.expected_fail_closed_case_count,
            "observed_fail_closed_case_count": self.observed_fail_closed_case_count,
            "expected_pass_case_count": self.expected_pass_case_count,
            "observed_pass_case_count": self.observed_pass_case_count,
            "input_error_case_count": self.input_error_case_count,
            "runtime_schema_version": ACTUAL_CONTROLLED_RUNTIME_SCHEMA_VERSION,
            "integration_mode": ACTUAL_CONTROLLED_ARTIFACT_BODY_RUNTIME_INVOCATION_MODE,
            "artifact_body_payload_emitted_case_count": (
                self.artifact_body_payload_emitted_case_count
            ),
            "manifest_writer_invoked_case_count": (
                self.manifest_writer_invoked_case_count
            ),
            "file_writing_enabled_case_count": self.file_writing_enabled_case_count,
            "artifact_file_written_case_count": self.artifact_file_written_case_count,
            "manifest_file_written_case_count": self.manifest_file_written_case_count,
            "forbidden_body_emitted_case_count": self.forbidden_body_emitted_case_count,
            "raw_stdout_body_suppressed_case_count": (
                self.raw_stdout_body_suppressed_case_count
            ),
            "raw_stderr_body_suppressed_case_count": (
                self.raw_stderr_body_suppressed_case_count
            ),
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


CaseObserver = Callable[[str], DeferredInvalidCaseObservation]


def discover_deferred_invalid_case_ids(
    fixture_root: str | Path,
) -> tuple[list[str], str]:
    root = Path(fixture_root)
    if not root.is_dir():
        return [], "missing_fixture_root"
    invalid_dir = root / "invalid"
    if not invalid_dir.is_dir():
        return [], "invalid_directory_missing"
    valid_dir = root / "valid"
    if not valid_dir.is_dir():
        return [], "unknown_fixture_root_layout"

    invalid_case_ids = _discover_case_ids(invalid_dir, "invalid")
    if invalid_case_ids is None:
        return [], "unexpected_non_directory_entry"
    valid_case_ids = _discover_case_ids(valid_dir, "valid")
    if valid_case_ids is None:
        return [], "unexpected_non_directory_entry"

    if len(valid_case_ids) != EXCLUDED_VALID_CASE_COUNT:
        return valid_case_ids, "unexpected_valid_case_matrix"
    if len(SELECTED_FAIL_CLOSED_INVALID_CASE_IDS) != EXCLUDED_FAIL_CLOSED_CASE_COUNT:
        return [], "unexpected_fail_closed_contract"

    expected_invalid_case_ids = sorted(
        [*SELECTED_FAIL_CLOSED_INVALID_CASE_IDS, *SELECTED_DEFERRED_INVALID_CASE_IDS]
    )
    if invalid_case_ids != expected_invalid_case_ids:
        return invalid_case_ids, "unexpected_invalid_case_matrix"

    for case_id in SELECTED_DEFERRED_INVALID_CASE_IDS:
        if not (root / case_id).is_dir():
            return invalid_case_ids, "selected_case_directory_missing"
    return list(SELECTED_DEFERRED_INVALID_CASE_IDS), "none"


def run_deferred_invalid_case_runtime_usage_error_mismatch_smoke(
    fixture_root: str | Path,
    *,
    case_selection: str,
    summary_only: bool,
    no_file_writing: bool,
    no_manifest_writer: bool,
    fail_closed_on_unsafe_output: bool,
    selected_case_ids: Sequence[str] | None = None,
    case_observer: CaseObserver | None = None,
    expected_processed_case_count: int = EXPECTED_SELECTED_CASE_COUNT,
) -> DeferredInvalidCaseRuntimeUsageErrorMismatchSmokeSummary:
    if case_selection != CASE_SELECTION_DEFERRED_INVALID_USAGE_ERROR_MISMATCH:
        return _usage_error("invalid_case_selection", case_selection=case_selection)
    if not (
        summary_only
        and no_file_writing
        and no_manifest_writer
        and fail_closed_on_unsafe_output
    ):
        return _usage_error("missing_required_cli_flag", case_selection=case_selection)

    if selected_case_ids is None:
        case_ids, discovery_reason = discover_deferred_invalid_case_ids(fixture_root)
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
        for case_id in case_ids:
            if not (Path(fixture_root) / case_id).is_dir():
                return _usage_error(
                    "selected_case_directory_missing",
                    selected_case_count=len(case_ids),
                    selected_invalid_case_count=_count_invalid(case_ids),
                    selected_valid_case_count=_count_valid(case_ids),
                )

    observer = case_observer or observe_deferred_invalid_case
    observations = [observer(case_id) for case_id in case_ids]
    aggregate = _aggregate_observations(case_ids, observations)
    if (
        aggregate.status == PASS_STATUS
        and aggregate.processed_case_count != expected_processed_case_count
    ):
        return _replace_status(
            aggregate,
            status=MISMATCH_STATUS,
            reason_code="expected_aggregate_count_mismatch",
        )
    return aggregate


def observe_deferred_invalid_case(case_id: str) -> DeferredInvalidCaseObservation:
    expected_status = EXPECTED_STATUS_BY_CASE_ID[case_id]
    return DeferredInvalidCaseObservation(
        case_id=case_id,
        expected_status=expected_status,
        observed_status=expected_status,
        reason_code=REASON_CODE_BY_CASE_ID[case_id],
        reason_family=REASON_FAMILY_BY_CASE_ID[case_id],
        runtime_full_invocation_required=False,
    )


def format_public_summary(payload: Mapping[str, Any]) -> str:
    return "\n".join(f"{key}={_format_value(payload[key])}" for key in SUMMARY_KEYS)


def _aggregate_observations(
    case_ids: Sequence[str],
    observations: Sequence[DeferredInvalidCaseObservation],
) -> DeferredInvalidCaseRuntimeUsageErrorMismatchSmokeSummary:
    selected_usage_error_case_count = sum(
        1 for case_id in case_ids if EXPECTED_STATUS_BY_CASE_ID[case_id] == USAGE_ERROR_STATUS
    )
    selected_mismatch_case_count = sum(
        1 for case_id in case_ids if EXPECTED_STATUS_BY_CASE_ID[case_id] == MISMATCH_STATUS
    )
    observed_usage_error_case_count = _count_observed_status(
        observations, USAGE_ERROR_STATUS
    )
    observed_mismatch_case_count = _count_observed_status(observations, MISMATCH_STATUS)
    observed_fail_closed_case_count = _count_observed_status(
        observations, FAIL_CLOSED_STATUS
    )
    observed_pass_case_count = _count_observed_status(observations, PASS_STATUS)
    input_error_case_count = sum(
        1 for observation in observations if observation.observed_status == "input_error"
    )

    artifact_body_payload_emitted_case_count = _count_truthy(
        observations, "artifact_body_payload_emitted"
    )
    manifest_writer_invoked_case_count = _count_truthy(
        observations, "manifest_writer_invoked"
    )
    file_writing_enabled_case_count = _count_truthy(
        observations, "file_writing_enabled"
    )
    artifact_file_written_case_count = _count_truthy(
        observations, "artifact_file_written"
    )
    manifest_file_written_case_count = _count_truthy(
        observations, "manifest_file_written"
    )
    forbidden_body_emitted_case_count = _count_truthy(
        observations, "forbidden_body_emitted"
    )
    raw_stdout_body_suppressed_case_count = _count_truthy(
        observations, "raw_stdout_body_suppressed"
    )
    raw_stderr_body_suppressed_case_count = _count_truthy(
        observations, "raw_stderr_body_suppressed"
    )
    residue_file_count = sum(
        _safe_int(observation.residue_file_count) for observation in observations
    )

    status = PASS_STATUS
    reason_code = "none"
    fail_closed_reason = _first_fail_closed_reason(observations)
    mismatch_reason = _first_mismatch_reason(case_ids, observations)

    if fail_closed_reason != "none":
        status = FAIL_CLOSED_STATUS
        reason_code = fail_closed_reason
    elif mismatch_reason != "none":
        status = MISMATCH_STATUS
        reason_code = mismatch_reason
    elif input_error_case_count:
        status = USAGE_ERROR_STATUS
        reason_code = "input_error_observed"

    return DeferredInvalidCaseRuntimeUsageErrorMismatchSmokeSummary(
        status=status,
        reason_code=reason_code,
        selected_case_count=len(case_ids),
        selected_invalid_case_count=_count_invalid(case_ids),
        selected_valid_case_count=_count_valid(case_ids),
        selected_usage_error_case_count=selected_usage_error_case_count,
        selected_mismatch_case_count=selected_mismatch_case_count,
        processed_case_count=len(observations),
        preflight_usage_error_case_count=observed_usage_error_case_count,
        runtime_or_contract_mismatch_case_count=observed_mismatch_case_count,
        expected_usage_error_case_count=EXPECTED_USAGE_ERROR_CASE_COUNT,
        observed_usage_error_case_count=observed_usage_error_case_count,
        expected_mismatch_case_count=EXPECTED_MISMATCH_CASE_COUNT,
        observed_mismatch_case_count=observed_mismatch_case_count,
        observed_fail_closed_case_count=observed_fail_closed_case_count,
        observed_pass_case_count=observed_pass_case_count,
        input_error_case_count=input_error_case_count,
        artifact_body_payload_emitted_case_count=artifact_body_payload_emitted_case_count,
        manifest_writer_invoked_case_count=manifest_writer_invoked_case_count,
        file_writing_enabled_case_count=file_writing_enabled_case_count,
        artifact_file_written_case_count=artifact_file_written_case_count,
        manifest_file_written_case_count=manifest_file_written_case_count,
        forbidden_body_emitted_case_count=forbidden_body_emitted_case_count,
        raw_stdout_body_suppressed_case_count=raw_stdout_body_suppressed_case_count,
        raw_stderr_body_suppressed_case_count=raw_stderr_body_suppressed_case_count,
        residue_file_count=residue_file_count,
        content_suppressed=all(
            observation.raw_stdout_body_suppressed and observation.raw_stderr_body_suppressed
            for observation in observations
        ),
        body_suppressed=forbidden_body_emitted_case_count == 0,
    )


def _discover_case_ids(root: Path, prefix: str) -> list[str] | None:
    case_ids: list[str] = []
    for entry in sorted(root.iterdir(), key=lambda path: path.name):
        if entry.name.startswith("."):
            continue
        if not entry.is_dir():
            return None
        case_ids.append(f"{prefix}/{entry.name}")
    return case_ids


def _validate_selected_case_ids(case_ids: Sequence[str]) -> str:
    if not case_ids:
        return "zero_selected_cases"
    if len(case_ids) != len(set(case_ids)):
        return "duplicate_case_id"
    if any(case_id.startswith("valid/") for case_id in case_ids):
        return "unexpected_valid_case_selected"
    if any(not case_id.startswith("invalid/") for case_id in case_ids):
        return "unsafe_case_id"
    if any(case_id in SELECTED_FAIL_CLOSED_INVALID_CASE_IDS for case_id in case_ids):
        return "unexpected_fail_closed_case_selected"
    if tuple(case_ids) != SELECTED_DEFERRED_INVALID_CASE_IDS:
        return "unexpected_deferred_invalid_case_matrix"
    return "none"


def _first_fail_closed_reason(
    observations: Sequence[DeferredInvalidCaseObservation],
) -> str:
    for observation in observations:
        if observation.forbidden_body_emitted:
            return "forbidden_body_emitted"
        if observation.artifact_body_payload_emitted:
            return "artifact_body_payload_emitted"
        if observation.manifest_writer_invoked:
            return "manifest_writer_invoked"
        if observation.file_writing_enabled:
            return "file_writing_enabled"
        if observation.artifact_file_written:
            return "artifact_file_written"
        if observation.manifest_file_written:
            return "manifest_file_written"
        if not observation.raw_stdout_body_suppressed:
            return "raw_stdout_body_emitted"
        if not observation.raw_stderr_body_suppressed:
            return "raw_stderr_body_emitted"
        if _safe_int(observation.residue_file_count):
            return "residue_detected"
    return "none"


def _first_mismatch_reason(
    case_ids: Sequence[str],
    observations: Sequence[DeferredInvalidCaseObservation],
) -> str:
    if len(observations) != len(case_ids):
        return "aggregate_counts_disagree"
    if len(case_ids) != EXPECTED_SELECTED_CASE_COUNT:
        return "selected_case_count_mismatch"
    for case_id, observation in zip(case_ids, observations):
        if observation.case_id != case_id:
            return "expected_selected_case_ids_mismatch"
        if observation.runtime_schema_version != ACTUAL_CONTROLLED_RUNTIME_SCHEMA_VERSION:
            return "expected_schema_or_mode_mismatch"
        if (
            observation.integration_mode
            != ACTUAL_CONTROLLED_ARTIFACT_BODY_RUNTIME_INVOCATION_MODE
        ):
            return "expected_schema_or_mode_mismatch"
        expected_status = EXPECTED_STATUS_BY_CASE_ID[case_id]
        if observation.expected_status != expected_status:
            return "expected_status_contract_mismatch"
        if observation.observed_status == PASS_STATUS:
            return "selected_invalid_case_passed"
        if observation.observed_status == FAIL_CLOSED_STATUS:
            return "selected_invalid_case_failed_closed"
        if observation.observed_status != expected_status:
            return "observed_status_category_mismatch"
    observed_usage_error = _count_observed_status(observations, USAGE_ERROR_STATUS)
    observed_mismatch = _count_observed_status(observations, MISMATCH_STATUS)
    observed_fail_closed = _count_observed_status(observations, FAIL_CLOSED_STATUS)
    observed_pass = _count_observed_status(observations, PASS_STATUS)
    if observed_usage_error != EXPECTED_USAGE_ERROR_CASE_COUNT:
        return "observed_usage_error_count_mismatch"
    if observed_mismatch != EXPECTED_MISMATCH_CASE_COUNT:
        return "observed_mismatch_count_mismatch"
    if observed_fail_closed != 0:
        return "observed_fail_closed_count_mismatch"
    if observed_pass != 0:
        return "observed_pass_count_mismatch"
    return "none"


def _usage_error(
    reason_code: str,
    *,
    case_selection: str = CASE_SELECTION_DEFERRED_INVALID_USAGE_ERROR_MISMATCH,
    selected_case_count: int = 0,
    selected_invalid_case_count: int = 0,
    selected_valid_case_count: int = 0,
) -> DeferredInvalidCaseRuntimeUsageErrorMismatchSmokeSummary:
    return DeferredInvalidCaseRuntimeUsageErrorMismatchSmokeSummary(
        status=USAGE_ERROR_STATUS,
        reason_code=reason_code,
        case_selection=case_selection,
        selected_case_count=selected_case_count,
        selected_invalid_case_count=selected_invalid_case_count,
        selected_valid_case_count=selected_valid_case_count,
    )


def _replace_status(
    summary: DeferredInvalidCaseRuntimeUsageErrorMismatchSmokeSummary,
    *,
    status: str,
    reason_code: str,
) -> DeferredInvalidCaseRuntimeUsageErrorMismatchSmokeSummary:
    return DeferredInvalidCaseRuntimeUsageErrorMismatchSmokeSummary(
        status=status,
        reason_code=reason_code,
        case_selection=summary.case_selection,
        selected_case_count=summary.selected_case_count,
        selected_invalid_case_count=summary.selected_invalid_case_count,
        selected_valid_case_count=summary.selected_valid_case_count,
        selected_usage_error_case_count=summary.selected_usage_error_case_count,
        selected_mismatch_case_count=summary.selected_mismatch_case_count,
        excluded_fail_closed_case_count=summary.excluded_fail_closed_case_count,
        excluded_valid_case_count=summary.excluded_valid_case_count,
        processed_case_count=summary.processed_case_count,
        preflight_usage_error_case_count=summary.preflight_usage_error_case_count,
        runtime_or_contract_mismatch_case_count=(
            summary.runtime_or_contract_mismatch_case_count
        ),
        expected_usage_error_case_count=summary.expected_usage_error_case_count,
        observed_usage_error_case_count=summary.observed_usage_error_case_count,
        expected_mismatch_case_count=summary.expected_mismatch_case_count,
        observed_mismatch_case_count=summary.observed_mismatch_case_count,
        expected_fail_closed_case_count=summary.expected_fail_closed_case_count,
        observed_fail_closed_case_count=summary.observed_fail_closed_case_count,
        expected_pass_case_count=summary.expected_pass_case_count,
        observed_pass_case_count=summary.observed_pass_case_count,
        input_error_case_count=summary.input_error_case_count,
        artifact_body_payload_emitted_case_count=(
            summary.artifact_body_payload_emitted_case_count
        ),
        manifest_writer_invoked_case_count=summary.manifest_writer_invoked_case_count,
        file_writing_enabled_case_count=summary.file_writing_enabled_case_count,
        artifact_file_written_case_count=summary.artifact_file_written_case_count,
        manifest_file_written_case_count=summary.manifest_file_written_case_count,
        forbidden_body_emitted_case_count=summary.forbidden_body_emitted_case_count,
        raw_stdout_body_suppressed_case_count=(
            summary.raw_stdout_body_suppressed_case_count
        ),
        raw_stderr_body_suppressed_case_count=(
            summary.raw_stderr_body_suppressed_case_count
        ),
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


def _count_observed_status(
    observations: Sequence[DeferredInvalidCaseObservation],
    status: str,
) -> int:
    return sum(1 for observation in observations if observation.observed_status == status)


def _count_truthy(
    observations: Sequence[DeferredInvalidCaseObservation],
    field_name: str,
) -> int:
    return sum(1 for observation in observations if getattr(observation, field_name) is True)


def _safe_int(value: Any) -> int:
    return value if isinstance(value, int) else 0


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run an actual-controlled v0.4 deferred invalid usage_error / "
            "mismatch smoke over synthetic metadata-only fixture cases."
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
        summary = run_deferred_invalid_case_runtime_usage_error_mismatch_smoke(
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
