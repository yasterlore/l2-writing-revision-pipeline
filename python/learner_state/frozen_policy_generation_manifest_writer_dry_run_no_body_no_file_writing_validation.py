"""Validate manifest-writer dry-run metadata without body or file output.

This runner reads a synthetic 34-case fixture contract and emits aggregate
public-safe metadata only. It does not invoke the manifest writer, generate or
emit manifest bodies, write files, create output directories, emit payload
bodies, train models, or compute metrics.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_dry_run_no_body_no_file_writing"
)

MODE = "manifest_writer_dry_run_no_body_no_file_writing_validation"
SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_dry_run_no_body_no_file_writing_v0.1"
)
CONTRACT_NAME = "manifest_writer_dry_run_no_body_no_file_writing_contract"
DRY_RUN_MODE = "manifest_writer_dry_run_no_body_no_file_writing"
BOUNDARY_NAME = "manifest_writer_dry_run_no_body_no_file_writing"
SOURCE_BOUNDARY = "manifest_writer_handoff_input_validation"
SOURCE_BOUNDARY_STATUS = "accepted_with_limitation"
SOURCE_CHAIN_STEP = "Step659-Step669"
PREFLIGHT_STEP = "Step671"
CONTRACT_DESIGN_STEP = "Step672"
FIXTURE_MATRIX_CONTRACT_STEP = "Step673"
MATRIX_NAME = "manifest_writer_dry_run_no_body_no_file_writing_contract_matrix"
CASE_SELECTION = "manifest-writer-dry-run-no-body-no-file-writing-contract"

PASS_STATUS = "pass"
USAGE_ERROR_STATUS = "usage_error"
FAIL_CLOSED_STATUS = "fail_closed"
MISMATCH_STATUS = "mismatch"

EXPECTED_VALID_CASE_IDS = (
    "valid/minimal_no_body_no_file_writing_contract_metadata",
    "valid/complete_source_boundary_and_safety_flags",
    "valid/local_manual_status_limitation_notice_present",
    "valid/non_claims_and_notices_present",
)

EXPECTED_USAGE_ERROR_CASE_IDS = (
    "invalid/usage_error_missing_schema_version",
    "invalid/usage_error_unsupported_schema_version",
    "invalid/usage_error_missing_required_identity_field",
    "invalid/usage_error_missing_required_safety_flag",
    "invalid/usage_error_malformed_metadata",
)

EXPECTED_MISMATCH_CASE_IDS = (
    "invalid/mismatch_source_boundary_status",
    "invalid/mismatch_source_remote_status_recorded",
    "invalid/mismatch_source_case_count",
    "invalid/mismatch_source_observed_counts",
    "invalid/mismatch_source_safety_counts",
)

EXPECTED_FAIL_CLOSED_CASE_IDS = (
    "invalid/fail_closed_manifest_writer_invocation_allowed",
    "invalid/fail_closed_manifest_writer_invoked",
    "invalid/fail_closed_manifest_body_generation_requested",
    "invalid/fail_closed_manifest_body_present",
    "invalid/fail_closed_generated_policy_body_present",
    "invalid/fail_closed_payload_body_present",
    "invalid/fail_closed_artifact_body_payload_present",
    "invalid/fail_closed_request_pointer_expected_body_present",
    "invalid/fail_closed_manifest_file_writing_requested",
    "invalid/fail_closed_artifact_file_writing_requested",
    "invalid/fail_closed_file_writing_enabled",
    "invalid/fail_closed_output_directory_created",
    "invalid/fail_closed_residue_detected",
    "invalid/fail_closed_private_or_absolute_path_present",
    "invalid/fail_closed_raw_learner_text_present",
    "invalid/fail_closed_real_data_marker_present",
    "invalid/fail_closed_no_oracle_forbidden_field_present",
    "invalid/fail_closed_raw_log_or_full_job_output_present",
    "invalid/fail_closed_performance_metric_body_present",
    "invalid/fail_closed_production_or_real_data_or_model_performance_claim",
)

EXPECTED_CASE_IDS = (
    *EXPECTED_VALID_CASE_IDS,
    *EXPECTED_USAGE_ERROR_CASE_IDS,
    *EXPECTED_MISMATCH_CASE_IDS,
    *EXPECTED_FAIL_CLOSED_CASE_IDS,
)

EXPECTED_SELECTED_CASE_COUNT = 34
EXPECTED_VALID_CASE_COUNT = 4
EXPECTED_INVALID_CASE_COUNT = 30
EXPECTED_FAIL_CLOSED_CASE_COUNT = 20
EXPECTED_USAGE_ERROR_CASE_COUNT = 5
EXPECTED_MISMATCH_CASE_COUNT = 5
EXPECTED_PASS_CASE_COUNT = 4
EXPECTED_MANIFEST_WRITER_INVOCATION_CASE_COUNT = 0
EXPECTED_MANIFEST_BODY_GENERATION_CASE_COUNT = 0
EXPECTED_MANIFEST_BODY_OUTPUT_CASE_COUNT = 0
EXPECTED_FILE_WRITING_CASE_COUNT = 0
EXPECTED_OUTPUT_DIRECTORY_CREATION_CASE_COUNT = 0
EXPECTED_PAYLOAD_BODY_EMISSION_CASE_COUNT = 0
EXPECTED_ARTIFACT_BODY_PAYLOAD_OUTPUT_CASE_COUNT = 0
EXPECTED_GENERATED_POLICY_BODY_OUTPUT_CASE_COUNT = 0
EXPECTED_RESIDUE_FILE_COUNT = 0

FIXTURE_FILE_NAMES = (
    "dry_run_input_metadata.json",
    "expected_summary_metadata.json",
    "safety_expectations.json",
)

ALLOWED_METADATA_KEYS = frozenset(
    {
        "case_id",
        "schema_version",
        "contract_name",
        "dry_run_id",
        "dry_run_mode",
        "boundary_name",
        "matrix_name",
        "case_selection",
        "expected_status",
        "expected_category",
        "unsafe_condition_category",
        "source_boundary",
        "source_boundary_status",
        "source_chain_step",
        "source_local_fallback_used",
        "source_remote_status_recorded",
        "source_case_selection",
        "source_matrix_name",
        "source_selected_case_count",
        "source_observed_pass_case_count",
        "source_observed_fail_closed_case_count",
        "source_observed_usage_error_case_count",
        "source_observed_mismatch_case_count",
        "source_processed_case_count",
        "source_input_error_case_count",
        "source_manifest_writer_invocation_requested_count",
        "source_manifest_writer_invoked_count",
        "source_manifest_body_generated_count",
        "source_file_writing_enabled_count",
        "source_payload_body_emitted_count",
        "source_artifact_body_payload_output_count",
        "source_generated_policy_body_emitted_count",
        "source_residue_file_count",
        "dry_run_requested",
        "dry_run_no_body_required",
        "dry_run_no_file_writing_required",
        "dry_run_summary_only_required",
        "manifest_writer_invocation_allowed",
        "manifest_writer_invoked",
        "manifest_body_generation_allowed",
        "manifest_body_generation_requested",
        "manifest_body_generated",
        "manifest_body_output_allowed",
        "manifest_body_output",
        "generated_policy_body_output_allowed",
        "generated_policy_body_emitted",
        "artifact_body_payload_output_allowed",
        "artifact_body_payload_output",
        "payload_body_emission_allowed",
        "payload_body_emitted",
        "request_body_output",
        "pointer_body_output",
        "expected_body_output",
        "manifest_file_writing_allowed",
        "manifest_file_writing_requested",
        "manifest_file_written",
        "artifact_file_writing_allowed",
        "artifact_file_writing_requested",
        "artifact_file_written",
        "file_writing_allowed",
        "file_writing_enabled",
        "output_directory_creation_allowed",
        "output_directory_created",
        "residue_file_count",
        "raw_stdout_body_suppressed",
        "raw_stderr_body_suppressed",
        "forbidden_body_detected",
        "private_path_detected",
        "absolute_path_detected",
        "raw_learner_text_detected",
        "real_data_marker_detected",
        "no_oracle_forbidden_field_detected",
        "raw_log_or_full_job_output_detected",
        "performance_metric_body_detected",
        "content_suppressed",
        "body_suppressed",
        "metadata_only_checked",
        "synthetic_only_checked",
        "no_oracle_checked",
        "production_readiness_claimed",
        "real_data_readiness_claimed",
        "performance_claims_present",
        "non_claims_present",
        "required_notices_present",
        "preflight_step",
        "contract_design_step",
        "fixture_matrix_contract_step",
        "reason_code",
    }
)

FORBIDDEN_METADATA_KEYS = frozenset(
    {
        "payload_body",
        "artifact_body_payload",
        "generated_policy_body",
        "manifest_body",
        "manifest_json_body",
        "request_body",
        "pointer_body",
        "expected_body",
        "raw_stdout_body",
        "raw_stderr_body",
        "raw_rows",
        "logits",
        "probabilities",
        "private_path_value",
        "absolute_path_value",
        "raw_learner_text",
        "real_participant_data",
        "final_text",
        "observed_after_text",
        "gold_label",
        "post_hoc_annotation",
        "scoring_feedback_payload",
        "test_set_tuning_payload",
        "performance_metric_body",
        "raw_github_actions_logs",
        "full_job_output",
        "copied_log_block",
    }
)

ACTUAL_FLAG_TO_COUNT_FIELD = {
    "manifest_writer_invocation_allowed": "manifest_writer_invocation_allowed_count",
    "manifest_writer_invoked": "manifest_writer_invoked_count",
    "manifest_body_generation_allowed": "manifest_body_generation_allowed_count",
    "manifest_body_generation_requested": "manifest_body_generation_requested_count",
    "manifest_body_generated": "manifest_body_generated_count",
    "manifest_body_output_allowed": "manifest_body_output_allowed_count",
    "manifest_body_output": "manifest_body_output_count",
    "generated_policy_body_output_allowed": "generated_policy_body_output_allowed_count",
    "generated_policy_body_emitted": "generated_policy_body_emitted_count",
    "artifact_body_payload_output_allowed": "artifact_body_payload_output_allowed_count",
    "artifact_body_payload_output": "artifact_body_payload_output_count",
    "payload_body_emission_allowed": "payload_body_emission_allowed_count",
    "payload_body_emitted": "payload_body_emitted_count",
    "request_body_output": "request_body_output_count",
    "pointer_body_output": "pointer_body_output_count",
    "expected_body_output": "expected_body_output_count",
    "manifest_file_writing_allowed": "manifest_file_writing_allowed_count",
    "manifest_file_writing_requested": "manifest_file_writing_requested_count",
    "manifest_file_written": "manifest_file_written_count",
    "artifact_file_writing_allowed": "artifact_file_writing_allowed_count",
    "artifact_file_writing_requested": "artifact_file_writing_requested_count",
    "artifact_file_written": "artifact_file_written_count",
    "file_writing_allowed": "file_writing_allowed_count",
    "file_writing_enabled": "file_writing_enabled_count",
    "output_directory_creation_allowed": "output_directory_creation_allowed_count",
    "output_directory_created": "output_directory_created_count",
    "forbidden_body_detected": "forbidden_body_detected_count",
    "private_path_detected": "private_path_detected_count",
    "absolute_path_detected": "absolute_path_detected_count",
    "raw_learner_text_detected": "raw_learner_text_detected_count",
    "real_data_marker_detected": "real_data_marker_detected_count",
    "no_oracle_forbidden_field_detected": "no_oracle_forbidden_field_detected_count",
    "raw_log_or_full_job_output_detected": "raw_log_or_full_job_output_detected_count",
    "performance_metric_body_detected": "performance_metric_body_detected_count",
}

FAIL_CLOSED_REASON_BY_FLAG = {
    field_name: field_name for field_name in ACTUAL_FLAG_TO_COUNT_FIELD
}

SUMMARY_KEYS = (
    "mode",
    "schema_version",
    "contract_name",
    "matrix_name",
    "case_selection",
    "status",
    "reason_code",
    "selected_case_count",
    "selected_valid_case_count",
    "selected_invalid_case_count",
    "selected_fail_closed_case_count",
    "selected_usage_error_case_count",
    "selected_mismatch_case_count",
    "expected_pass_case_count",
    "observed_pass_case_count",
    "expected_fail_closed_case_count",
    "observed_fail_closed_case_count",
    "expected_usage_error_case_count",
    "observed_usage_error_case_count",
    "expected_mismatch_case_count",
    "observed_mismatch_case_count",
    "processed_case_count",
    "input_error_case_count",
    "expected_manifest_writer_invocation_case_count",
    "expected_manifest_body_generation_case_count",
    "expected_manifest_body_output_case_count",
    "expected_file_writing_case_count",
    "expected_output_directory_creation_case_count",
    "expected_payload_body_emission_case_count",
    "expected_artifact_body_payload_output_case_count",
    "expected_generated_policy_body_output_case_count",
    "expected_residue_file_count",
    *tuple(ACTUAL_FLAG_TO_COUNT_FIELD.values()),
    "residue_file_count",
    "raw_stdout_body_suppressed_count",
    "raw_stderr_body_suppressed_count",
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
class DryRunObservation:
    case_id: str
    dry_run_id: str
    schema_version: str
    contract_name: str
    dry_run_mode: str
    boundary_name: str
    matrix_name: str
    case_selection: str
    expected_status: str
    expected_category: str
    unsafe_condition_category: str
    source_boundary: str
    source_boundary_status: str
    source_chain_step: str
    source_local_fallback_used: bool
    source_remote_status_recorded: bool
    source_case_selection: str
    source_matrix_name: str
    source_selected_case_count: int
    source_observed_pass_case_count: int
    source_observed_fail_closed_case_count: int
    source_observed_usage_error_case_count: int
    source_observed_mismatch_case_count: int
    source_processed_case_count: int
    source_input_error_case_count: int
    source_manifest_writer_invocation_requested_count: int
    source_manifest_writer_invoked_count: int
    source_manifest_body_generated_count: int
    source_file_writing_enabled_count: int
    source_payload_body_emitted_count: int
    source_artifact_body_payload_output_count: int
    source_generated_policy_body_emitted_count: int
    source_residue_file_count: int
    observed_status: str
    reason_code: str
    dry_run_requested: bool = True
    dry_run_no_body_required: bool = True
    dry_run_no_file_writing_required: bool = True
    dry_run_summary_only_required: bool = True
    manifest_writer_invocation_allowed: bool = False
    manifest_writer_invoked: bool = False
    manifest_body_generation_allowed: bool = False
    manifest_body_generation_requested: bool = False
    manifest_body_generated: bool = False
    manifest_body_output_allowed: bool = False
    manifest_body_output: bool = False
    generated_policy_body_output_allowed: bool = False
    generated_policy_body_emitted: bool = False
    artifact_body_payload_output_allowed: bool = False
    artifact_body_payload_output: bool = False
    payload_body_emission_allowed: bool = False
    payload_body_emitted: bool = False
    request_body_output: bool = False
    pointer_body_output: bool = False
    expected_body_output: bool = False
    manifest_file_writing_allowed: bool = False
    manifest_file_writing_requested: bool = False
    manifest_file_written: bool = False
    artifact_file_writing_allowed: bool = False
    artifact_file_writing_requested: bool = False
    artifact_file_written: bool = False
    file_writing_allowed: bool = False
    file_writing_enabled: bool = False
    output_directory_creation_allowed: bool = False
    output_directory_created: bool = False
    residue_file_count: int = 0
    raw_stdout_body_suppressed: bool = True
    raw_stderr_body_suppressed: bool = True
    forbidden_body_detected: bool = False
    private_path_detected: bool = False
    absolute_path_detected: bool = False
    raw_learner_text_detected: bool = False
    real_data_marker_detected: bool = False
    no_oracle_forbidden_field_detected: bool = False
    raw_log_or_full_job_output_detected: bool = False
    performance_metric_body_detected: bool = False
    content_suppressed: bool = True
    body_suppressed: bool = True
    metadata_only_checked: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    production_readiness_claimed: bool = False
    real_data_readiness_claimed: bool = False
    performance_claims_present: bool = False
    non_claims_present: bool = True
    required_notices_present: bool = True
    preflight_step: str = PREFLIGHT_STEP
    contract_design_step: str = CONTRACT_DESIGN_STEP
    fixture_matrix_contract_step: str = FIXTURE_MATRIX_CONTRACT_STEP


@dataclass(frozen=True)
class DryRunSummary:
    status: str
    reason_code: str
    case_selection: str = CASE_SELECTION
    selected_case_count: int = 0
    selected_valid_case_count: int = 0
    selected_invalid_case_count: int = 0
    selected_fail_closed_case_count: int = 0
    selected_usage_error_case_count: int = 0
    selected_mismatch_case_count: int = 0
    observed_pass_case_count: int = 0
    observed_fail_closed_case_count: int = 0
    observed_usage_error_case_count: int = 0
    observed_mismatch_case_count: int = 0
    processed_case_count: int = 0
    input_error_case_count: int = 0
    manifest_writer_invocation_allowed_count: int = 0
    manifest_writer_invoked_count: int = 0
    manifest_body_generation_allowed_count: int = 0
    manifest_body_generation_requested_count: int = 0
    manifest_body_generated_count: int = 0
    manifest_body_output_allowed_count: int = 0
    manifest_body_output_count: int = 0
    generated_policy_body_output_allowed_count: int = 0
    generated_policy_body_emitted_count: int = 0
    artifact_body_payload_output_allowed_count: int = 0
    artifact_body_payload_output_count: int = 0
    payload_body_emission_allowed_count: int = 0
    payload_body_emitted_count: int = 0
    request_body_output_count: int = 0
    pointer_body_output_count: int = 0
    expected_body_output_count: int = 0
    manifest_file_writing_allowed_count: int = 0
    manifest_file_writing_requested_count: int = 0
    manifest_file_written_count: int = 0
    artifact_file_writing_allowed_count: int = 0
    artifact_file_writing_requested_count: int = 0
    artifact_file_written_count: int = 0
    file_writing_allowed_count: int = 0
    file_writing_enabled_count: int = 0
    output_directory_creation_allowed_count: int = 0
    output_directory_created_count: int = 0
    forbidden_body_detected_count: int = 0
    private_path_detected_count: int = 0
    absolute_path_detected_count: int = 0
    raw_learner_text_detected_count: int = 0
    real_data_marker_detected_count: int = 0
    no_oracle_forbidden_field_detected_count: int = 0
    raw_log_or_full_job_output_detected_count: int = 0
    performance_metric_body_detected_count: int = 0
    residue_file_count: int = 0
    raw_stdout_body_suppressed_count: int = 0
    raw_stderr_body_suppressed_count: int = 0
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
            "contract_name": CONTRACT_NAME,
            "matrix_name": MATRIX_NAME,
            "case_selection": self.case_selection,
            "status": self.status,
            "reason_code": self.reason_code,
            "selected_case_count": self.selected_case_count,
            "selected_valid_case_count": self.selected_valid_case_count,
            "selected_invalid_case_count": self.selected_invalid_case_count,
            "selected_fail_closed_case_count": self.selected_fail_closed_case_count,
            "selected_usage_error_case_count": self.selected_usage_error_case_count,
            "selected_mismatch_case_count": self.selected_mismatch_case_count,
            "expected_pass_case_count": EXPECTED_PASS_CASE_COUNT,
            "observed_pass_case_count": self.observed_pass_case_count,
            "expected_fail_closed_case_count": EXPECTED_FAIL_CLOSED_CASE_COUNT,
            "observed_fail_closed_case_count": self.observed_fail_closed_case_count,
            "expected_usage_error_case_count": EXPECTED_USAGE_ERROR_CASE_COUNT,
            "observed_usage_error_case_count": self.observed_usage_error_case_count,
            "expected_mismatch_case_count": EXPECTED_MISMATCH_CASE_COUNT,
            "observed_mismatch_case_count": self.observed_mismatch_case_count,
            "processed_case_count": self.processed_case_count,
            "input_error_case_count": self.input_error_case_count,
            "expected_manifest_writer_invocation_case_count": (
                EXPECTED_MANIFEST_WRITER_INVOCATION_CASE_COUNT
            ),
            "expected_manifest_body_generation_case_count": (
                EXPECTED_MANIFEST_BODY_GENERATION_CASE_COUNT
            ),
            "expected_manifest_body_output_case_count": (
                EXPECTED_MANIFEST_BODY_OUTPUT_CASE_COUNT
            ),
            "expected_file_writing_case_count": EXPECTED_FILE_WRITING_CASE_COUNT,
            "expected_output_directory_creation_case_count": (
                EXPECTED_OUTPUT_DIRECTORY_CREATION_CASE_COUNT
            ),
            "expected_payload_body_emission_case_count": (
                EXPECTED_PAYLOAD_BODY_EMISSION_CASE_COUNT
            ),
            "expected_artifact_body_payload_output_case_count": (
                EXPECTED_ARTIFACT_BODY_PAYLOAD_OUTPUT_CASE_COUNT
            ),
            "expected_generated_policy_body_output_case_count": (
                EXPECTED_GENERATED_POLICY_BODY_OUTPUT_CASE_COUNT
            ),
            "expected_residue_file_count": EXPECTED_RESIDUE_FILE_COUNT,
            **{key: getattr(self, key) for key in ACTUAL_FLAG_TO_COUNT_FIELD.values()},
            "residue_file_count": self.residue_file_count,
            "raw_stdout_body_suppressed_count": self.raw_stdout_body_suppressed_count,
            "raw_stderr_body_suppressed_count": self.raw_stderr_body_suppressed_count,
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


def run_manifest_writer_dry_run_no_body_no_file_writing_validation(
    fixture_root: str | Path,
    *,
    case_selection: str,
    summary_only: bool,
    dry_run_mode: str,
    no_manifest_writer: bool,
    no_manifest_body: bool,
    no_generated_policy_body: bool,
    no_file_writing: bool,
    no_output_directory: bool,
    fail_closed_on_forbidden_body: bool,
    fail_closed_on_file_writing: bool,
) -> DryRunSummary:
    if case_selection != CASE_SELECTION:
        return _usage_error("invalid_case_selection", case_selection=case_selection)
    if dry_run_mode != DRY_RUN_MODE:
        return _usage_error("invalid_dry_run_mode", case_selection=case_selection)
    if not (
        summary_only
        and no_manifest_writer
        and no_manifest_body
        and no_generated_policy_body
        and no_file_writing
        and no_output_directory
        and fail_closed_on_forbidden_body
        and fail_closed_on_file_writing
    ):
        return _usage_error("missing_required_cli_flag", case_selection=case_selection)

    observations, reason_code, status = _load_observations(Path(fixture_root))
    if reason_code != "none":
        return _summary_from_observations(
            observations,
            status=status,
            reason_code=reason_code,
            input_error_case_count=1 if status == USAGE_ERROR_STATUS else 0,
            selected_case_count=len(observations),
        )

    return _summary_from_observations(
        observations,
        status=PASS_STATUS,
        reason_code="none",
    )


def discover_manifest_writer_dry_run_case_ids(
    fixture_root: str | Path,
) -> tuple[list[str], str]:
    observations, reason_code, _status = _load_observations(Path(fixture_root))
    if reason_code != "none":
        return [observation.case_id for observation in observations], reason_code
    return [observation.case_id for observation in observations], "none"


def format_public_summary(payload: Mapping[str, Any]) -> str:
    return "\n".join(f"{key}={_format_value(payload[key])}" for key in SUMMARY_KEYS)


def _load_observations(
    fixture_root: Path,
) -> tuple[list[DryRunObservation], str, str]:
    if not fixture_root.is_dir():
        return [], "missing_fixture_root", USAGE_ERROR_STATUS

    discovered_case_ids, discovery_reason = _discover_case_dir_ids(fixture_root)
    if discovery_reason != "none":
        return [], discovery_reason, MISMATCH_STATUS
    if tuple(discovered_case_ids) != EXPECTED_CASE_IDS:
        return [], "selected_case_ids_mismatch", MISMATCH_STATUS

    observations: list[DryRunObservation] = []
    seen_case_ids: set[str] = set()
    seen_dry_run_ids: set[str] = set()
    for case_id in EXPECTED_CASE_IDS:
        case_dir = fixture_root / case_id
        if not case_dir.is_dir():
            return observations, "missing_case_directory", MISMATCH_STATUS
        observation, reason_code, status = _load_case_observation(case_dir)
        observations.append(observation)
        if reason_code != "none":
            return observations, reason_code, status
        if observation.case_id in seen_case_ids:
            return observations, "duplicate_case_id", USAGE_ERROR_STATUS
        if observation.dry_run_id in seen_dry_run_ids:
            return observations, "duplicate_dry_run_id", USAGE_ERROR_STATUS
        seen_case_ids.add(observation.case_id)
        seen_dry_run_ids.add(observation.dry_run_id)

    validation_reason = _validate_observations(observations)
    if validation_reason != "none":
        status = (
            USAGE_ERROR_STATUS
            if validation_reason in {"duplicate_case_id", "duplicate_dry_run_id"}
            else MISMATCH_STATUS
        )
        return observations, validation_reason, status

    fail_closed_reason = _first_actual_fail_closed_reason(observations)
    if fail_closed_reason != "none":
        return observations, fail_closed_reason, FAIL_CLOSED_STATUS

    count_reason = _validate_expected_observed_counts(observations)
    if count_reason != "none":
        return observations, count_reason, MISMATCH_STATUS

    return observations, "none", PASS_STATUS


def _load_case_observation(
    case_dir: Path,
) -> tuple[DryRunObservation, str, str]:
    merged: dict[str, Any] = {}
    for file_name in FIXTURE_FILE_NAMES:
        path = case_dir / file_name
        if not path.is_file():
            return _empty_observation(), "missing_fixture_metadata_file", USAGE_ERROR_STATUS
        try:
            with path.open(encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return _empty_observation(), "malformed_fixture_metadata", USAGE_ERROR_STATUS
        if not isinstance(payload, dict):
            return _empty_observation(), "malformed_fixture_metadata", USAGE_ERROR_STATUS
        forbidden_reason = _scan_metadata_keys(payload)
        if forbidden_reason != "none":
            return _observation_from_payload(
                merged,
                observed_status=FAIL_CLOSED_STATUS,
                reason_code=forbidden_reason,
                forbidden_body_detected=True,
            ), forbidden_reason, FAIL_CLOSED_STATUS
        merged.update(payload)

    unknown_keys = sorted(set(merged) - ALLOWED_METADATA_KEYS)
    if unknown_keys:
        return _observation_from_payload(
            merged,
            observed_status=FAIL_CLOSED_STATUS,
            reason_code="unknown_metadata_field",
            forbidden_body_detected=True,
        ), "unknown_metadata_field", FAIL_CLOSED_STATUS
    return _observation_from_payload(merged), "none", PASS_STATUS


def _discover_case_dir_ids(fixture_root: Path) -> tuple[list[str], str]:
    case_ids: list[str] = []
    for prefix in ("valid", "invalid"):
        parent = fixture_root / prefix
        if not parent.is_dir():
            return [], "unknown_fixture_root_layout"
        for entry in sorted(parent.iterdir(), key=lambda path: path.name):
            if entry.name.startswith("."):
                continue
            if not entry.is_dir():
                return [], "unexpected_fixture_entry"
            case_ids.append(f"{prefix}/{entry.name}")
    if any(case_id not in set(case_ids) for case_id in EXPECTED_CASE_IDS):
        return case_ids, "missing_case_directory"
    if set(case_ids) != set(EXPECTED_CASE_IDS) or len(case_ids) != len(
        EXPECTED_CASE_IDS
    ):
        return case_ids, "none"
    return list(EXPECTED_CASE_IDS), "none"


def _scan_metadata_keys(payload: Any) -> str:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in FORBIDDEN_METADATA_KEYS:
                return "forbidden_metadata_field"
            nested_reason = _scan_metadata_keys(value)
            if nested_reason != "none":
                return nested_reason
    elif isinstance(payload, list):
        for item in payload:
            nested_reason = _scan_metadata_keys(item)
            if nested_reason != "none":
                return nested_reason
    return "none"


def _observation_from_payload(
    payload: Mapping[str, Any],
    **overrides: Any,
) -> DryRunObservation:
    expected_status = str(payload.get("expected_status", USAGE_ERROR_STATUS))
    reason_code = str(payload.get("reason_code", "none"))
    observation = DryRunObservation(
        case_id=str(payload.get("case_id", "unknown")),
        dry_run_id=str(payload.get("dry_run_id", "unknown")),
        schema_version=str(payload.get("schema_version", "unknown")),
        contract_name=str(payload.get("contract_name", "unknown")),
        dry_run_mode=str(payload.get("dry_run_mode", "unknown")),
        boundary_name=str(payload.get("boundary_name", "unknown")),
        matrix_name=str(payload.get("matrix_name", "unknown")),
        case_selection=str(payload.get("case_selection", "unknown")),
        expected_status=expected_status,
        expected_category=str(payload.get("expected_category", "unknown")),
        unsafe_condition_category=str(
            payload.get("unsafe_condition_category", "none")
        ),
        source_boundary=str(payload.get("source_boundary", "unknown")),
        source_boundary_status=str(payload.get("source_boundary_status", "unknown")),
        source_chain_step=str(payload.get("source_chain_step", "unknown")),
        source_local_fallback_used=_as_bool(
            payload.get("source_local_fallback_used")
        ),
        source_remote_status_recorded=_as_bool(
            payload.get("source_remote_status_recorded")
        ),
        source_case_selection=str(payload.get("source_case_selection", "unknown")),
        source_matrix_name=str(payload.get("source_matrix_name", "unknown")),
        source_selected_case_count=_as_int(payload.get("source_selected_case_count")),
        source_observed_pass_case_count=_as_int(
            payload.get("source_observed_pass_case_count")
        ),
        source_observed_fail_closed_case_count=_as_int(
            payload.get("source_observed_fail_closed_case_count")
        ),
        source_observed_usage_error_case_count=_as_int(
            payload.get("source_observed_usage_error_case_count")
        ),
        source_observed_mismatch_case_count=_as_int(
            payload.get("source_observed_mismatch_case_count")
        ),
        source_processed_case_count=_as_int(payload.get("source_processed_case_count")),
        source_input_error_case_count=_as_int(payload.get("source_input_error_case_count")),
        source_manifest_writer_invocation_requested_count=_as_int(
            payload.get("source_manifest_writer_invocation_requested_count")
        ),
        source_manifest_writer_invoked_count=_as_int(
            payload.get("source_manifest_writer_invoked_count")
        ),
        source_manifest_body_generated_count=_as_int(
            payload.get("source_manifest_body_generated_count")
        ),
        source_file_writing_enabled_count=_as_int(
            payload.get("source_file_writing_enabled_count")
        ),
        source_payload_body_emitted_count=_as_int(
            payload.get("source_payload_body_emitted_count")
        ),
        source_artifact_body_payload_output_count=_as_int(
            payload.get("source_artifact_body_payload_output_count")
        ),
        source_generated_policy_body_emitted_count=_as_int(
            payload.get("source_generated_policy_body_emitted_count")
        ),
        source_residue_file_count=_as_int(payload.get("source_residue_file_count")),
        observed_status=expected_status,
        reason_code=reason_code,
        dry_run_requested=_as_bool(payload.get("dry_run_requested"), default=True),
        dry_run_no_body_required=_as_bool(
            payload.get("dry_run_no_body_required"), default=True
        ),
        dry_run_no_file_writing_required=_as_bool(
            payload.get("dry_run_no_file_writing_required"), default=True
        ),
        dry_run_summary_only_required=_as_bool(
            payload.get("dry_run_summary_only_required"), default=True
        ),
        manifest_writer_invocation_allowed=_as_bool(
            payload.get("manifest_writer_invocation_allowed")
        ),
        manifest_writer_invoked=_as_bool(payload.get("manifest_writer_invoked")),
        manifest_body_generation_allowed=_as_bool(
            payload.get("manifest_body_generation_allowed")
        ),
        manifest_body_generation_requested=_as_bool(
            payload.get("manifest_body_generation_requested")
        ),
        manifest_body_generated=_as_bool(payload.get("manifest_body_generated")),
        manifest_body_output_allowed=_as_bool(
            payload.get("manifest_body_output_allowed")
        ),
        manifest_body_output=_as_bool(payload.get("manifest_body_output")),
        generated_policy_body_output_allowed=_as_bool(
            payload.get("generated_policy_body_output_allowed")
        ),
        generated_policy_body_emitted=_as_bool(
            payload.get("generated_policy_body_emitted")
        ),
        artifact_body_payload_output_allowed=_as_bool(
            payload.get("artifact_body_payload_output_allowed")
        ),
        artifact_body_payload_output=_as_bool(
            payload.get("artifact_body_payload_output")
        ),
        payload_body_emission_allowed=_as_bool(
            payload.get("payload_body_emission_allowed")
        ),
        payload_body_emitted=_as_bool(payload.get("payload_body_emitted")),
        request_body_output=_as_bool(payload.get("request_body_output")),
        pointer_body_output=_as_bool(payload.get("pointer_body_output")),
        expected_body_output=_as_bool(payload.get("expected_body_output")),
        manifest_file_writing_allowed=_as_bool(
            payload.get("manifest_file_writing_allowed")
        ),
        manifest_file_writing_requested=_as_bool(
            payload.get("manifest_file_writing_requested")
        ),
        manifest_file_written=_as_bool(payload.get("manifest_file_written")),
        artifact_file_writing_allowed=_as_bool(
            payload.get("artifact_file_writing_allowed")
        ),
        artifact_file_writing_requested=_as_bool(
            payload.get("artifact_file_writing_requested")
        ),
        artifact_file_written=_as_bool(payload.get("artifact_file_written")),
        file_writing_allowed=_as_bool(payload.get("file_writing_allowed")),
        file_writing_enabled=_as_bool(payload.get("file_writing_enabled")),
        output_directory_creation_allowed=_as_bool(
            payload.get("output_directory_creation_allowed")
        ),
        output_directory_created=_as_bool(payload.get("output_directory_created")),
        residue_file_count=_as_int(payload.get("residue_file_count")),
        raw_stdout_body_suppressed=_as_bool(
            payload.get("raw_stdout_body_suppressed"), default=True
        ),
        raw_stderr_body_suppressed=_as_bool(
            payload.get("raw_stderr_body_suppressed"), default=True
        ),
        forbidden_body_detected=_as_bool(payload.get("forbidden_body_detected")),
        private_path_detected=_as_bool(payload.get("private_path_detected")),
        absolute_path_detected=_as_bool(payload.get("absolute_path_detected")),
        raw_learner_text_detected=_as_bool(payload.get("raw_learner_text_detected")),
        real_data_marker_detected=_as_bool(payload.get("real_data_marker_detected")),
        no_oracle_forbidden_field_detected=_as_bool(
            payload.get("no_oracle_forbidden_field_detected")
        ),
        raw_log_or_full_job_output_detected=_as_bool(
            payload.get("raw_log_or_full_job_output_detected")
        ),
        performance_metric_body_detected=_as_bool(
            payload.get("performance_metric_body_detected")
        ),
        content_suppressed=_as_bool(payload.get("content_suppressed"), default=True),
        body_suppressed=_as_bool(payload.get("body_suppressed"), default=True),
        metadata_only_checked=_as_bool(payload.get("metadata_only_checked"), default=True),
        synthetic_only_checked=_as_bool(payload.get("synthetic_only_checked"), default=True),
        no_oracle_checked=_as_bool(payload.get("no_oracle_checked"), default=True),
        production_readiness_claimed=_as_bool(
            payload.get("production_readiness_claimed")
        ),
        real_data_readiness_claimed=_as_bool(
            payload.get("real_data_readiness_claimed")
        ),
        performance_claims_present=_as_bool(payload.get("performance_claims_present")),
        non_claims_present=_as_bool(payload.get("non_claims_present"), default=True),
        required_notices_present=_as_bool(
            payload.get("required_notices_present"), default=True
        ),
        preflight_step=str(payload.get("preflight_step", PREFLIGHT_STEP)),
        contract_design_step=str(
            payload.get("contract_design_step", CONTRACT_DESIGN_STEP)
        ),
        fixture_matrix_contract_step=str(
            payload.get("fixture_matrix_contract_step", FIXTURE_MATRIX_CONTRACT_STEP)
        ),
    )
    if not overrides:
        return observation
    data = observation.__dict__.copy()
    data.update(overrides)
    return DryRunObservation(**data)


def _empty_observation() -> DryRunObservation:
    return DryRunObservation(
        case_id="unknown",
        dry_run_id="unknown",
        schema_version="unknown",
        contract_name="unknown",
        dry_run_mode="unknown",
        boundary_name="unknown",
        matrix_name="unknown",
        case_selection="unknown",
        expected_status=USAGE_ERROR_STATUS,
        expected_category="unknown",
        unsafe_condition_category="unknown",
        source_boundary="unknown",
        source_boundary_status="unknown",
        source_chain_step="unknown",
        source_local_fallback_used=False,
        source_remote_status_recorded=False,
        source_case_selection="unknown",
        source_matrix_name="unknown",
        source_selected_case_count=0,
        source_observed_pass_case_count=0,
        source_observed_fail_closed_case_count=0,
        source_observed_usage_error_case_count=0,
        source_observed_mismatch_case_count=0,
        source_processed_case_count=0,
        source_input_error_case_count=0,
        source_manifest_writer_invocation_requested_count=0,
        source_manifest_writer_invoked_count=0,
        source_manifest_body_generated_count=0,
        source_file_writing_enabled_count=0,
        source_payload_body_emitted_count=0,
        source_artifact_body_payload_output_count=0,
        source_generated_policy_body_emitted_count=0,
        source_residue_file_count=0,
        observed_status=USAGE_ERROR_STATUS,
        reason_code="unknown",
    )


def _validate_observations(observations: Sequence[DryRunObservation]) -> str:
    if len(observations) != EXPECTED_SELECTED_CASE_COUNT:
        return "selected_case_count_mismatch"
    if tuple(observation.case_id for observation in observations) != EXPECTED_CASE_IDS:
        return "selected_case_ids_mismatch"
    if len({observation.case_id for observation in observations}) != len(observations):
        return "duplicate_case_id"
    if len({observation.dry_run_id for observation in observations}) != len(observations):
        return "duplicate_dry_run_id"

    for observation in observations:
        if observation.case_id not in EXPECTED_USAGE_ERROR_CASE_IDS:
            reason = _validate_common_identity(observation)
            if reason != "none":
                return reason
        if observation.case_id in EXPECTED_VALID_CASE_IDS:
            reason = _validate_valid_case(observation)
            if reason != "none":
                return reason
        elif observation.case_id in EXPECTED_FAIL_CLOSED_CASE_IDS:
            if observation.expected_status != FAIL_CLOSED_STATUS:
                return "expected_status_mismatch"
            if observation.expected_category != "invalid_fail_closed":
                return "expected_category_mismatch"
        elif observation.case_id in EXPECTED_USAGE_ERROR_CASE_IDS:
            if observation.expected_status != USAGE_ERROR_STATUS:
                return "expected_status_mismatch"
            if observation.expected_category != "invalid_usage_error":
                return "expected_category_mismatch"
        elif observation.case_id in EXPECTED_MISMATCH_CASE_IDS:
            if observation.expected_status != MISMATCH_STATUS:
                return "expected_status_mismatch"
            if observation.expected_category != "invalid_mismatch":
                return "expected_category_mismatch"
    return "none"


def _validate_common_identity(observation: DryRunObservation) -> str:
    if observation.schema_version != SCHEMA_VERSION:
        return "schema_version_mismatch"
    if observation.contract_name != CONTRACT_NAME:
        return "contract_name_mismatch"
    if observation.dry_run_mode != DRY_RUN_MODE:
        return "dry_run_mode_mismatch"
    if observation.boundary_name != BOUNDARY_NAME:
        return "boundary_name_mismatch"
    if observation.matrix_name != MATRIX_NAME:
        return "matrix_name_mismatch"
    if observation.case_selection != CASE_SELECTION:
        return "case_selection_mismatch"
    if observation.source_boundary != SOURCE_BOUNDARY:
        return "source_boundary_mismatch"
    if observation.source_boundary_status != SOURCE_BOUNDARY_STATUS:
        return "source_boundary_status_mismatch"
    if observation.source_chain_step != SOURCE_CHAIN_STEP:
        return "source_chain_step_mismatch"
    if observation.preflight_step != PREFLIGHT_STEP:
        return "preflight_step_mismatch"
    if observation.contract_design_step != CONTRACT_DESIGN_STEP:
        return "contract_design_step_mismatch"
    if observation.fixture_matrix_contract_step != FIXTURE_MATRIX_CONTRACT_STEP:
        return "fixture_matrix_contract_step_mismatch"
    return "none"


def _validate_valid_case(observation: DryRunObservation) -> str:
    if observation.expected_status != PASS_STATUS:
        return "expected_status_mismatch"
    if observation.expected_category != "valid_metadata_only_no_body_no_file_writing":
        return "expected_category_mismatch"
    if not observation.source_local_fallback_used:
        return "source_local_fallback_mismatch"
    if observation.source_remote_status_recorded:
        return "source_remote_status_mismatch"
    if observation.source_selected_case_count != 23:
        return "source_case_count_mismatch"
    if observation.source_observed_pass_case_count != 3:
        return "source_observed_counts_mismatch"
    if observation.source_observed_fail_closed_case_count != 11:
        return "source_observed_counts_mismatch"
    if observation.source_observed_usage_error_case_count != 5:
        return "source_observed_counts_mismatch"
    if observation.source_observed_mismatch_case_count != 4:
        return "source_observed_counts_mismatch"
    if observation.source_processed_case_count != 23:
        return "source_case_count_mismatch"
    if observation.source_input_error_case_count != 0:
        return "source_observed_counts_mismatch"
    source_safety_counts = (
        observation.source_manifest_writer_invocation_requested_count,
        observation.source_manifest_writer_invoked_count,
        observation.source_manifest_body_generated_count,
        observation.source_file_writing_enabled_count,
        observation.source_payload_body_emitted_count,
        observation.source_artifact_body_payload_output_count,
        observation.source_generated_policy_body_emitted_count,
        observation.source_residue_file_count,
    )
    if any(count != 0 for count in source_safety_counts):
        return "source_safety_counts_mismatch"
    if not observation.dry_run_requested:
        return "dry_run_requested_mismatch"
    if not observation.dry_run_no_body_required:
        return "dry_run_no_body_required_mismatch"
    if not observation.dry_run_no_file_writing_required:
        return "dry_run_no_file_writing_required_mismatch"
    if not observation.dry_run_summary_only_required:
        return "dry_run_summary_only_required_mismatch"
    if not observation.non_claims_present:
        return "non_claims_missing"
    if not observation.required_notices_present:
        return "required_notices_missing"
    return "none"


def _validate_expected_observed_counts(
    observations: Sequence[DryRunObservation],
) -> str:
    if _count_by_expected_status(observations, PASS_STATUS) != EXPECTED_PASS_CASE_COUNT:
        return "pass_case_count_mismatch"
    if (
        _count_by_expected_status(observations, FAIL_CLOSED_STATUS)
        != EXPECTED_FAIL_CLOSED_CASE_COUNT
    ):
        return "fail_closed_case_count_mismatch"
    if (
        _count_by_expected_status(observations, USAGE_ERROR_STATUS)
        != EXPECTED_USAGE_ERROR_CASE_COUNT
    ):
        return "usage_error_case_count_mismatch"
    if (
        _count_by_expected_status(observations, MISMATCH_STATUS)
        != EXPECTED_MISMATCH_CASE_COUNT
    ):
        return "mismatch_case_count_mismatch"
    return "none"


def _first_actual_fail_closed_reason(
    observations: Sequence[DryRunObservation],
) -> str:
    for observation in observations:
        for field_name, reason_code in FAIL_CLOSED_REASON_BY_FLAG.items():
            if _as_bool(getattr(observation, field_name)):
                return reason_code
        if observation.residue_file_count > 0:
            return "residue_detected"
        if not observation.raw_stdout_body_suppressed:
            return "raw_stdout_body_output"
        if not observation.raw_stderr_body_suppressed:
            return "raw_stderr_body_output"
        if not observation.content_suppressed:
            return "content_not_suppressed"
        if not observation.body_suppressed:
            return "body_not_suppressed"
        if not observation.metadata_only_checked:
            return "metadata_only_check_missing"
        if not observation.synthetic_only_checked:
            return "synthetic_only_check_missing"
        if not observation.no_oracle_checked:
            return "no_oracle_check_missing"
        if observation.production_readiness_claimed:
            return "production_readiness_claim_detected"
        if observation.real_data_readiness_claimed:
            return "real_data_readiness_claim_detected"
        if observation.performance_claims_present:
            return "performance_claim_detected"
    return "none"


def _summary_from_observations(
    observations: Sequence[DryRunObservation],
    *,
    status: str,
    reason_code: str,
    input_error_case_count: int = 0,
    selected_case_count: int | None = None,
) -> DryRunSummary:
    counts = _actual_counts(observations)
    selected = selected_case_count if selected_case_count is not None else len(observations)
    return DryRunSummary(
        status=status,
        reason_code=reason_code,
        selected_case_count=selected,
        selected_valid_case_count=sum(
            1 for observation in observations if observation.case_id.startswith("valid/")
        ),
        selected_invalid_case_count=sum(
            1 for observation in observations if observation.case_id.startswith("invalid/")
        ),
        selected_fail_closed_case_count=sum(
            1 for observation in observations if observation.case_id in EXPECTED_FAIL_CLOSED_CASE_IDS
        ),
        selected_usage_error_case_count=sum(
            1 for observation in observations if observation.case_id in EXPECTED_USAGE_ERROR_CASE_IDS
        ),
        selected_mismatch_case_count=sum(
            1 for observation in observations if observation.case_id in EXPECTED_MISMATCH_CASE_IDS
        ),
        observed_pass_case_count=_count_by_expected_status(observations, PASS_STATUS),
        observed_fail_closed_case_count=_count_by_expected_status(
            observations, FAIL_CLOSED_STATUS
        ),
        observed_usage_error_case_count=_count_by_expected_status(
            observations, USAGE_ERROR_STATUS
        ),
        observed_mismatch_case_count=_count_by_expected_status(
            observations, MISMATCH_STATUS
        ),
        processed_case_count=len(observations),
        input_error_case_count=input_error_case_count,
        raw_stdout_body_suppressed_count=sum(
            1 for observation in observations if observation.raw_stdout_body_suppressed
        ),
        raw_stderr_body_suppressed_count=sum(
            1 for observation in observations if observation.raw_stderr_body_suppressed
        ),
        residue_file_count=sum(
            observation.residue_file_count for observation in observations
        ),
        content_suppressed=all(
            observation.content_suppressed for observation in observations
        )
        if observations
        else True,
        body_suppressed=all(observation.body_suppressed for observation in observations)
        if observations
        else True,
        metadata_only_checked=all(
            observation.metadata_only_checked for observation in observations
        )
        if observations
        else True,
        synthetic_only_checked=all(
            observation.synthetic_only_checked for observation in observations
        )
        if observations
        else True,
        no_oracle_checked=all(
            observation.no_oracle_checked for observation in observations
        )
        if observations
        else True,
        production_readiness_claimed=any(
            observation.production_readiness_claimed for observation in observations
        ),
        real_data_readiness_claimed=any(
            observation.real_data_readiness_claimed for observation in observations
        ),
        performance_claims_present=any(
            observation.performance_claims_present for observation in observations
        ),
        **counts,
    )


def _actual_counts(
    observations: Sequence[DryRunObservation],
) -> dict[str, int]:
    counts = {count_field: 0 for count_field in ACTUAL_FLAG_TO_COUNT_FIELD.values()}
    for observation in observations:
        for field_name, count_field in ACTUAL_FLAG_TO_COUNT_FIELD.items():
            if _as_bool(getattr(observation, field_name)):
                counts[count_field] += 1
    return counts


def _count_by_expected_status(
    observations: Sequence[DryRunObservation],
    status: str,
) -> int:
    return sum(1 for observation in observations if observation.expected_status == status)


def _usage_error(
    reason_code: str,
    *,
    case_selection: str,
) -> DryRunSummary:
    return DryRunSummary(
        status=USAGE_ERROR_STATUS,
        reason_code=reason_code,
        case_selection=case_selection,
        input_error_case_count=1,
    )


def _as_bool(value: Any, *, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return bool(value)


def _as_int(value: Any, *, default: int = 0) -> int:
    if value is None:
        return default
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate manifest-writer dry-run metadata without body or file output."
        )
    )
    parser.add_argument("--fixture-root", type=Path, default=DEFAULT_FIXTURE_ROOT)
    parser.add_argument("--case-selection", required=True)
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--dry-run-mode", required=True)
    parser.add_argument("--no-manifest-writer", action="store_true")
    parser.add_argument("--no-manifest-body", action="store_true")
    parser.add_argument("--no-generated-policy-body", action="store_true")
    parser.add_argument("--no-file-writing", action="store_true")
    parser.add_argument("--no-output-directory", action="store_true")
    parser.add_argument("--fail-closed-on-forbidden-body", action="store_true")
    parser.add_argument("--fail-closed-on-file-writing", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    summary = run_manifest_writer_dry_run_no_body_no_file_writing_validation(
        args.fixture_root,
        case_selection=args.case_selection,
        summary_only=args.summary_only,
        dry_run_mode=args.dry_run_mode,
        no_manifest_writer=args.no_manifest_writer,
        no_manifest_body=args.no_manifest_body,
        no_generated_policy_body=args.no_generated_policy_body,
        no_file_writing=args.no_file_writing,
        no_output_directory=args.no_output_directory,
        fail_closed_on_forbidden_body=args.fail_closed_on_forbidden_body,
        fail_closed_on_file_writing=args.fail_closed_on_file_writing,
    )
    sys.stdout.write(format_public_summary(summary.to_public_dict()))
    sys.stdout.write("\n")
    return summary.return_code


if __name__ == "__main__":
    raise SystemExit(main())
