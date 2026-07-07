"""Validate manifest-writer handoff input metadata without writer invocation.

This runner reads a synthetic 23-case fixture contract and emits aggregate
public-safe metadata only. It does not invoke the manifest writer, generate
manifest bodies, write files, emit payload bodies, train models, or compute
metrics.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_handoff_input"
)

MODE = "manifest_writer_handoff_input_validation"
SCHEMA_VERSION = "learner_state_frozen_policy_generation_manifest_writer_handoff_input_v0.1"
CONTRACT_NAME = "manifest_writer_handoff_input_contract"
HANDOFF_INPUT_MODE = "manifest_writer_handoff_input_metadata_only_no_invocation"
BOUNDARY_NAME = "manifest_writer_handoff_input_metadata_only_no_writer_invocation"
SOURCE_BOUNDARY = "artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation"
SOURCE_BOUNDARY_STATUS = "accepted_with_explicit_boundary"
SOURCE_CHAIN_STEP = "Step647-Step657"
MATRIX_NAME = "manifest_writer_handoff_input_contract_matrix"
CASE_SELECTION = "manifest-writer-handoff-input-contract"

PASS_STATUS = "pass"
USAGE_ERROR_STATUS = "usage_error"
FAIL_CLOSED_STATUS = "fail_closed"
MISMATCH_STATUS = "mismatch"

EXPECTED_VALID_CASE_IDS = (
    "valid/minimal_handoff_input_metadata_only",
    "valid/complete_handoff_input_count_summary",
    "valid/non_claims_and_notices_present",
)

EXPECTED_FAIL_CLOSED_CASE_IDS = (
    "invalid/fail_closed_manifest_writer_invocation_requested",
    "invalid/fail_closed_manifest_body_generation_requested",
    "invalid/fail_closed_file_writing_requested",
    "invalid/fail_closed_payload_body_present",
    "invalid/fail_closed_manifest_body_present",
    "invalid/fail_closed_generated_policy_body_present",
    "invalid/fail_closed_private_or_absolute_path_present",
    "invalid/fail_closed_raw_learner_text_present",
    "invalid/fail_closed_no_oracle_forbidden_field_present",
    "invalid/fail_closed_raw_log_or_full_job_output_present",
    "invalid/fail_closed_residue_detected",
)

EXPECTED_USAGE_ERROR_CASE_IDS = (
    "invalid/usage_error_missing_schema_version",
    "invalid/usage_error_unsupported_schema_version",
    "invalid/usage_error_missing_required_identity_field",
    "invalid/usage_error_malformed_metadata",
    "invalid/usage_error_duplicate_handoff_input_id",
)

EXPECTED_MISMATCH_CASE_IDS = (
    "invalid/mismatch_source_case_count_mismatch",
    "invalid/mismatch_source_status_mismatch",
    "invalid/mismatch_source_remote_status_mismatch",
    "invalid/mismatch_count_summary_mismatch",
)

EXPECTED_CASE_IDS = (
    *EXPECTED_VALID_CASE_IDS,
    *EXPECTED_FAIL_CLOSED_CASE_IDS,
    *EXPECTED_USAGE_ERROR_CASE_IDS,
    *EXPECTED_MISMATCH_CASE_IDS,
)

EXPECTED_SELECTED_CASE_COUNT = 23
EXPECTED_VALID_CASE_COUNT = 3
EXPECTED_INVALID_CASE_COUNT = 20
EXPECTED_FAIL_CLOSED_CASE_COUNT = 11
EXPECTED_USAGE_ERROR_CASE_COUNT = 5
EXPECTED_MISMATCH_CASE_COUNT = 4
EXPECTED_PASS_CASE_COUNT = 3
EXPECTED_MANIFEST_WRITER_INVOCATION_CASE_COUNT = 0
EXPECTED_MANIFEST_BODY_GENERATION_CASE_COUNT = 0
EXPECTED_FILE_WRITING_CASE_COUNT = 0
EXPECTED_PAYLOAD_BODY_EMISSION_CASE_COUNT = 0
EXPECTED_ARTIFACT_BODY_PAYLOAD_OUTPUT_CASE_COUNT = 0
EXPECTED_GENERATED_POLICY_BODY_OUTPUT_CASE_COUNT = 0
EXPECTED_RESIDUE_FILE_COUNT = 0

FIXTURE_FILE_NAMES = (
    "handoff_input_metadata.json",
    "expected_summary_metadata.json",
    "safety_expectations.json",
)

ALLOWED_METADATA_KEYS = frozenset(
    {
        "case_id",
        "schema_version",
        "contract_name",
        "handoff_input_id",
        "handoff_input_mode",
        "boundary_name",
        "matrix_name",
        "case_selection",
        "expected_status",
        "expected_category",
        "unsafe_condition_category",
        "source_boundary",
        "source_boundary_status",
        "source_chain_step",
        "source_release_quality_status",
        "source_remote_status_recorded",
        "source_local_fallback_used",
        "source_target_command",
        "source_case_selection",
        "source_matrix_name",
        "source_selected_case_count",
        "source_selected_valid_metadata_only_case_count",
        "source_selected_invalid_fail_closed_case_count",
        "source_expected_pass_case_count",
        "source_observed_pass_case_count",
        "source_expected_fail_closed_case_count",
        "source_observed_fail_closed_case_count",
        "source_expected_usage_error_case_count",
        "source_observed_usage_error_case_count",
        "source_expected_mismatch_case_count",
        "source_observed_mismatch_case_count",
        "source_processed_case_count",
        "source_input_error_case_count",
        "manifest_writer_handoff_ready",
        "manifest_writer_invocation_requested",
        "manifest_writer_invoked",
        "manifest_body_generation_requested",
        "manifest_body_generated",
        "manifest_body_output",
        "manifest_file_writing_requested",
        "manifest_file_written",
        "artifact_file_writing_requested",
        "artifact_file_written",
        "file_writing_enabled",
        "payload_body_emission_requested",
        "payload_body_emitted",
        "artifact_body_payload_output",
        "generated_policy_body_emitted",
        "request_body_output",
        "pointer_body_output",
        "expected_body_output",
        "raw_stdout_body_suppressed",
        "raw_stderr_body_suppressed",
        "forbidden_body_detected",
        "private_path_detected",
        "absolute_path_detected",
        "raw_learner_text_detected",
        "real_data_marker_detected",
        "no_oracle_forbidden_field_detected",
        "raw_log_or_full_job_output_detected",
        "residue_file_count",
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
    "manifest_writer_invocation_requested": "manifest_writer_invocation_requested_count",
    "manifest_writer_invoked": "manifest_writer_invoked_count",
    "manifest_body_generation_requested": "manifest_body_generation_requested_count",
    "manifest_body_generated": "manifest_body_generated_count",
    "manifest_body_output": "manifest_body_output_count",
    "manifest_file_writing_requested": "manifest_file_writing_requested_count",
    "manifest_file_written": "manifest_file_written_count",
    "artifact_file_writing_requested": "artifact_file_writing_requested_count",
    "artifact_file_written": "artifact_file_written_count",
    "file_writing_enabled": "file_writing_enabled_count",
    "payload_body_emission_requested": "payload_body_emission_requested_count",
    "payload_body_emitted": "payload_body_emitted_count",
    "artifact_body_payload_output": "artifact_body_payload_output_count",
    "generated_policy_body_emitted": "generated_policy_body_emitted_count",
    "request_body_output": "request_body_output_count",
    "pointer_body_output": "pointer_body_output_count",
    "expected_body_output": "expected_body_output_count",
    "forbidden_body_detected": "forbidden_body_detected_count",
    "private_path_detected": "private_path_detected_count",
    "absolute_path_detected": "absolute_path_detected_count",
    "raw_learner_text_detected": "raw_learner_text_detected_count",
    "real_data_marker_detected": "real_data_marker_detected_count",
    "no_oracle_forbidden_field_detected": "no_oracle_forbidden_field_detected_count",
    "raw_log_or_full_job_output_detected": (
        "raw_log_or_full_job_output_detected_count"
    ),
}

FAIL_CLOSED_REASON_BY_FLAG = {
    "manifest_writer_invocation_requested": "manifest_writer_invocation_requested",
    "manifest_writer_invoked": "manifest_writer_invoked",
    "manifest_body_generation_requested": "manifest_body_generation_requested",
    "manifest_body_generated": "manifest_body_generated",
    "manifest_body_output": "manifest_body_output",
    "manifest_file_writing_requested": "manifest_file_writing_requested",
    "manifest_file_written": "manifest_file_written",
    "artifact_file_writing_requested": "artifact_file_writing_requested",
    "artifact_file_written": "artifact_file_written",
    "file_writing_enabled": "file_writing_enabled",
    "payload_body_emission_requested": "payload_body_emission_requested",
    "payload_body_emitted": "payload_body_emitted",
    "artifact_body_payload_output": "artifact_body_payload_output",
    "generated_policy_body_emitted": "generated_policy_body_emitted",
    "request_body_output": "request_body_output",
    "pointer_body_output": "pointer_body_output",
    "expected_body_output": "expected_body_output",
    "forbidden_body_detected": "forbidden_body_detected",
    "private_path_detected": "private_path_detected",
    "absolute_path_detected": "absolute_path_detected",
    "raw_learner_text_detected": "raw_learner_text_detected",
    "real_data_marker_detected": "real_data_marker_detected",
    "no_oracle_forbidden_field_detected": "no_oracle_forbidden_field_detected",
    "raw_log_or_full_job_output_detected": "raw_log_or_full_job_output_detected",
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
    "expected_file_writing_case_count",
    "expected_payload_body_emission_case_count",
    "expected_artifact_body_payload_output_case_count",
    "expected_generated_policy_body_output_case_count",
    "expected_residue_file_count",
    "manifest_writer_invocation_requested_count",
    "manifest_writer_invoked_count",
    "manifest_body_generation_requested_count",
    "manifest_body_generated_count",
    "manifest_body_output_count",
    "manifest_file_writing_requested_count",
    "manifest_file_written_count",
    "artifact_file_writing_requested_count",
    "artifact_file_written_count",
    "file_writing_enabled_count",
    "payload_body_emission_requested_count",
    "payload_body_emitted_count",
    "artifact_body_payload_output_count",
    "generated_policy_body_emitted_count",
    "request_body_output_count",
    "pointer_body_output_count",
    "expected_body_output_count",
    "forbidden_body_detected_count",
    "private_path_detected_count",
    "absolute_path_detected_count",
    "raw_learner_text_detected_count",
    "real_data_marker_detected_count",
    "no_oracle_forbidden_field_detected_count",
    "raw_log_or_full_job_output_detected_count",
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
class HandoffInputObservation:
    case_id: str
    handoff_input_id: str
    schema_version: str
    contract_name: str
    handoff_input_mode: str
    boundary_name: str
    matrix_name: str
    case_selection: str
    expected_status: str
    expected_category: str
    unsafe_condition_category: str
    source_boundary: str
    source_boundary_status: str
    source_chain_step: str
    source_release_quality_status: str
    source_remote_status_recorded: bool
    source_local_fallback_used: bool
    source_target_command: str
    source_case_selection: str
    source_matrix_name: str
    source_selected_case_count: int
    source_selected_valid_metadata_only_case_count: int
    source_selected_invalid_fail_closed_case_count: int
    source_expected_pass_case_count: int
    source_observed_pass_case_count: int
    source_expected_fail_closed_case_count: int
    source_observed_fail_closed_case_count: int
    source_expected_usage_error_case_count: int
    source_observed_usage_error_case_count: int
    source_expected_mismatch_case_count: int
    source_observed_mismatch_case_count: int
    source_processed_case_count: int
    source_input_error_case_count: int
    observed_status: str
    reason_code: str
    manifest_writer_handoff_ready: bool = True
    manifest_writer_invocation_requested: bool = False
    manifest_writer_invoked: bool = False
    manifest_body_generation_requested: bool = False
    manifest_body_generated: bool = False
    manifest_body_output: bool = False
    manifest_file_writing_requested: bool = False
    manifest_file_written: bool = False
    artifact_file_writing_requested: bool = False
    artifact_file_written: bool = False
    file_writing_enabled: bool = False
    payload_body_emission_requested: bool = False
    payload_body_emitted: bool = False
    artifact_body_payload_output: bool = False
    generated_policy_body_emitted: bool = False
    request_body_output: bool = False
    pointer_body_output: bool = False
    expected_body_output: bool = False
    raw_stdout_body_suppressed: bool = True
    raw_stderr_body_suppressed: bool = True
    forbidden_body_detected: bool = False
    private_path_detected: bool = False
    absolute_path_detected: bool = False
    raw_learner_text_detected: bool = False
    real_data_marker_detected: bool = False
    no_oracle_forbidden_field_detected: bool = False
    raw_log_or_full_job_output_detected: bool = False
    residue_file_count: int = 0
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


@dataclass(frozen=True)
class HandoffInputSummary:
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
    manifest_writer_invocation_requested_count: int = 0
    manifest_writer_invoked_count: int = 0
    manifest_body_generation_requested_count: int = 0
    manifest_body_generated_count: int = 0
    manifest_body_output_count: int = 0
    manifest_file_writing_requested_count: int = 0
    manifest_file_written_count: int = 0
    artifact_file_writing_requested_count: int = 0
    artifact_file_written_count: int = 0
    file_writing_enabled_count: int = 0
    payload_body_emission_requested_count: int = 0
    payload_body_emitted_count: int = 0
    artifact_body_payload_output_count: int = 0
    generated_policy_body_emitted_count: int = 0
    request_body_output_count: int = 0
    pointer_body_output_count: int = 0
    expected_body_output_count: int = 0
    forbidden_body_detected_count: int = 0
    private_path_detected_count: int = 0
    absolute_path_detected_count: int = 0
    raw_learner_text_detected_count: int = 0
    real_data_marker_detected_count: int = 0
    no_oracle_forbidden_field_detected_count: int = 0
    raw_log_or_full_job_output_detected_count: int = 0
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
            "expected_file_writing_case_count": EXPECTED_FILE_WRITING_CASE_COUNT,
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
            "manifest_writer_invocation_requested_count": (
                self.manifest_writer_invocation_requested_count
            ),
            "manifest_writer_invoked_count": self.manifest_writer_invoked_count,
            "manifest_body_generation_requested_count": (
                self.manifest_body_generation_requested_count
            ),
            "manifest_body_generated_count": self.manifest_body_generated_count,
            "manifest_body_output_count": self.manifest_body_output_count,
            "manifest_file_writing_requested_count": (
                self.manifest_file_writing_requested_count
            ),
            "manifest_file_written_count": self.manifest_file_written_count,
            "artifact_file_writing_requested_count": (
                self.artifact_file_writing_requested_count
            ),
            "artifact_file_written_count": self.artifact_file_written_count,
            "file_writing_enabled_count": self.file_writing_enabled_count,
            "payload_body_emission_requested_count": (
                self.payload_body_emission_requested_count
            ),
            "payload_body_emitted_count": self.payload_body_emitted_count,
            "artifact_body_payload_output_count": (
                self.artifact_body_payload_output_count
            ),
            "generated_policy_body_emitted_count": (
                self.generated_policy_body_emitted_count
            ),
            "request_body_output_count": self.request_body_output_count,
            "pointer_body_output_count": self.pointer_body_output_count,
            "expected_body_output_count": self.expected_body_output_count,
            "forbidden_body_detected_count": self.forbidden_body_detected_count,
            "private_path_detected_count": self.private_path_detected_count,
            "absolute_path_detected_count": self.absolute_path_detected_count,
            "raw_learner_text_detected_count": (
                self.raw_learner_text_detected_count
            ),
            "real_data_marker_detected_count": self.real_data_marker_detected_count,
            "no_oracle_forbidden_field_detected_count": (
                self.no_oracle_forbidden_field_detected_count
            ),
            "raw_log_or_full_job_output_detected_count": (
                self.raw_log_or_full_job_output_detected_count
            ),
            "residue_file_count": self.residue_file_count,
            "raw_stdout_body_suppressed_count": (
                self.raw_stdout_body_suppressed_count
            ),
            "raw_stderr_body_suppressed_count": (
                self.raw_stderr_body_suppressed_count
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


def run_manifest_writer_handoff_input_validation(
    fixture_root: str | Path,
    *,
    case_selection: str,
    summary_only: bool,
    no_manifest_writer: bool,
    no_file_writing: bool,
    fail_closed_on_forbidden_body: bool,
) -> HandoffInputSummary:
    if case_selection != CASE_SELECTION:
        return _usage_error("invalid_case_selection", case_selection=case_selection)
    if not (
        summary_only
        and no_manifest_writer
        and no_file_writing
        and fail_closed_on_forbidden_body
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


def discover_manifest_writer_handoff_case_ids(
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
) -> tuple[list[HandoffInputObservation], str, str]:
    if not fixture_root.is_dir():
        return [], "missing_fixture_root", USAGE_ERROR_STATUS

    discovered_case_ids, discovery_reason = _discover_case_dir_ids(fixture_root)
    if discovery_reason != "none":
        return [], discovery_reason, MISMATCH_STATUS
    if tuple(discovered_case_ids) != EXPECTED_CASE_IDS:
        return [], "selected_case_ids_mismatch", MISMATCH_STATUS

    observations: list[HandoffInputObservation] = []
    seen_case_ids: set[str] = set()
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
        seen_case_ids.add(observation.case_id)

    validation_reason = _validate_observations(observations)
    if validation_reason != "none":
        status = (
            USAGE_ERROR_STATUS
            if validation_reason in {"duplicate_case_id", "duplicate_handoff_input_id"}
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
) -> tuple[HandoffInputObservation, str, str]:
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
) -> HandoffInputObservation:
    expected_status = str(payload.get("expected_status", USAGE_ERROR_STATUS))
    reason_code = str(payload.get("reason_code", "none"))
    observation = HandoffInputObservation(
        case_id=str(payload.get("case_id", "unknown")),
        handoff_input_id=str(payload.get("handoff_input_id", "unknown")),
        schema_version=str(payload.get("schema_version", "unknown")),
        contract_name=str(payload.get("contract_name", "unknown")),
        handoff_input_mode=str(payload.get("handoff_input_mode", "unknown")),
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
        source_release_quality_status=str(
            payload.get("source_release_quality_status", "unknown")
        ),
        source_remote_status_recorded=_as_bool(
            payload.get("source_remote_status_recorded")
        ),
        source_local_fallback_used=_as_bool(
            payload.get("source_local_fallback_used")
        ),
        source_target_command=str(payload.get("source_target_command", "unknown")),
        source_case_selection=str(payload.get("source_case_selection", "unknown")),
        source_matrix_name=str(payload.get("source_matrix_name", "unknown")),
        source_selected_case_count=_as_int(
            payload.get("source_selected_case_count")
        ),
        source_selected_valid_metadata_only_case_count=_as_int(
            payload.get("source_selected_valid_metadata_only_case_count")
        ),
        source_selected_invalid_fail_closed_case_count=_as_int(
            payload.get("source_selected_invalid_fail_closed_case_count")
        ),
        source_expected_pass_case_count=_as_int(
            payload.get("source_expected_pass_case_count")
        ),
        source_observed_pass_case_count=_as_int(
            payload.get("source_observed_pass_case_count")
        ),
        source_expected_fail_closed_case_count=_as_int(
            payload.get("source_expected_fail_closed_case_count")
        ),
        source_observed_fail_closed_case_count=_as_int(
            payload.get("source_observed_fail_closed_case_count")
        ),
        source_expected_usage_error_case_count=_as_int(
            payload.get("source_expected_usage_error_case_count")
        ),
        source_observed_usage_error_case_count=_as_int(
            payload.get("source_observed_usage_error_case_count")
        ),
        source_expected_mismatch_case_count=_as_int(
            payload.get("source_expected_mismatch_case_count")
        ),
        source_observed_mismatch_case_count=_as_int(
            payload.get("source_observed_mismatch_case_count")
        ),
        source_processed_case_count=_as_int(
            payload.get("source_processed_case_count")
        ),
        source_input_error_case_count=_as_int(
            payload.get("source_input_error_case_count")
        ),
        observed_status=expected_status,
        reason_code=reason_code,
        manifest_writer_handoff_ready=_as_bool(
            payload.get("manifest_writer_handoff_ready"), default=True
        ),
        manifest_writer_invocation_requested=_as_bool(
            payload.get("manifest_writer_invocation_requested")
        ),
        manifest_writer_invoked=_as_bool(payload.get("manifest_writer_invoked")),
        manifest_body_generation_requested=_as_bool(
            payload.get("manifest_body_generation_requested")
        ),
        manifest_body_generated=_as_bool(payload.get("manifest_body_generated")),
        manifest_body_output=_as_bool(payload.get("manifest_body_output")),
        manifest_file_writing_requested=_as_bool(
            payload.get("manifest_file_writing_requested")
        ),
        manifest_file_written=_as_bool(payload.get("manifest_file_written")),
        artifact_file_writing_requested=_as_bool(
            payload.get("artifact_file_writing_requested")
        ),
        artifact_file_written=_as_bool(payload.get("artifact_file_written")),
        file_writing_enabled=_as_bool(payload.get("file_writing_enabled")),
        payload_body_emission_requested=_as_bool(
            payload.get("payload_body_emission_requested")
        ),
        payload_body_emitted=_as_bool(payload.get("payload_body_emitted")),
        artifact_body_payload_output=_as_bool(
            payload.get("artifact_body_payload_output")
        ),
        generated_policy_body_emitted=_as_bool(
            payload.get("generated_policy_body_emitted")
        ),
        request_body_output=_as_bool(payload.get("request_body_output")),
        pointer_body_output=_as_bool(payload.get("pointer_body_output")),
        expected_body_output=_as_bool(payload.get("expected_body_output")),
        raw_stdout_body_suppressed=_as_bool(
            payload.get("raw_stdout_body_suppressed"), default=True
        ),
        raw_stderr_body_suppressed=_as_bool(
            payload.get("raw_stderr_body_suppressed"), default=True
        ),
        forbidden_body_detected=_as_bool(payload.get("forbidden_body_detected")),
        private_path_detected=_as_bool(payload.get("private_path_detected")),
        absolute_path_detected=_as_bool(payload.get("absolute_path_detected")),
        raw_learner_text_detected=_as_bool(
            payload.get("raw_learner_text_detected")
        ),
        real_data_marker_detected=_as_bool(
            payload.get("real_data_marker_detected")
        ),
        no_oracle_forbidden_field_detected=_as_bool(
            payload.get("no_oracle_forbidden_field_detected")
        ),
        raw_log_or_full_job_output_detected=_as_bool(
            payload.get("raw_log_or_full_job_output_detected")
        ),
        residue_file_count=_as_int(payload.get("residue_file_count")),
        content_suppressed=_as_bool(payload.get("content_suppressed"), default=True),
        body_suppressed=_as_bool(payload.get("body_suppressed"), default=True),
        metadata_only_checked=_as_bool(
            payload.get("metadata_only_checked"), default=True
        ),
        synthetic_only_checked=_as_bool(
            payload.get("synthetic_only_checked"), default=True
        ),
        no_oracle_checked=_as_bool(payload.get("no_oracle_checked"), default=True),
        production_readiness_claimed=_as_bool(
            payload.get("production_readiness_claimed")
        ),
        real_data_readiness_claimed=_as_bool(
            payload.get("real_data_readiness_claimed")
        ),
        performance_claims_present=_as_bool(
            payload.get("performance_claims_present")
        ),
        non_claims_present=_as_bool(payload.get("non_claims_present"), default=True),
        required_notices_present=_as_bool(
            payload.get("required_notices_present"), default=True
        ),
    )
    if not overrides:
        return observation
    data = observation.__dict__.copy()
    data.update(overrides)
    return HandoffInputObservation(**data)


def _empty_observation() -> HandoffInputObservation:
    return HandoffInputObservation(
        case_id="unknown",
        handoff_input_id="unknown",
        schema_version="unknown",
        contract_name="unknown",
        handoff_input_mode="unknown",
        boundary_name="unknown",
        matrix_name="unknown",
        case_selection="unknown",
        expected_status=USAGE_ERROR_STATUS,
        expected_category="unknown",
        unsafe_condition_category="unknown",
        source_boundary="unknown",
        source_boundary_status="unknown",
        source_chain_step="unknown",
        source_release_quality_status="unknown",
        source_remote_status_recorded=False,
        source_local_fallback_used=False,
        source_target_command="unknown",
        source_case_selection="unknown",
        source_matrix_name="unknown",
        source_selected_case_count=0,
        source_selected_valid_metadata_only_case_count=0,
        source_selected_invalid_fail_closed_case_count=0,
        source_expected_pass_case_count=0,
        source_observed_pass_case_count=0,
        source_expected_fail_closed_case_count=0,
        source_observed_fail_closed_case_count=0,
        source_expected_usage_error_case_count=0,
        source_observed_usage_error_case_count=0,
        source_expected_mismatch_case_count=0,
        source_observed_mismatch_case_count=0,
        source_processed_case_count=0,
        source_input_error_case_count=0,
        observed_status=USAGE_ERROR_STATUS,
        reason_code="unknown",
    )


def _validate_observations(observations: Sequence[HandoffInputObservation]) -> str:
    if len(observations) != EXPECTED_SELECTED_CASE_COUNT:
        return "selected_case_count_mismatch"
    if tuple(observation.case_id for observation in observations) != EXPECTED_CASE_IDS:
        return "selected_case_ids_mismatch"
    if len({observation.case_id for observation in observations}) != len(observations):
        return "duplicate_case_id"

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


def _validate_common_identity(observation: HandoffInputObservation) -> str:
    if observation.schema_version != SCHEMA_VERSION:
        return "schema_version_mismatch"
    if observation.contract_name != CONTRACT_NAME:
        return "contract_name_mismatch"
    if observation.handoff_input_mode != HANDOFF_INPUT_MODE:
        return "handoff_input_mode_mismatch"
    if observation.boundary_name != BOUNDARY_NAME:
        return "boundary_name_mismatch"
    if observation.matrix_name != MATRIX_NAME:
        return "matrix_name_mismatch"
    if observation.case_selection != CASE_SELECTION:
        return "case_selection_mismatch"
    if observation.source_boundary != SOURCE_BOUNDARY:
        return "source_boundary_mismatch"
    if observation.source_boundary_status != SOURCE_BOUNDARY_STATUS:
        return "source_status_mismatch"
    if observation.source_chain_step != SOURCE_CHAIN_STEP:
        return "source_chain_step_mismatch"
    return "none"


def _validate_valid_case(observation: HandoffInputObservation) -> str:
    if observation.expected_status != PASS_STATUS:
        return "expected_status_mismatch"
    if observation.expected_category != "valid_metadata_only":
        return "expected_category_mismatch"
    if not observation.manifest_writer_handoff_ready:
        return "handoff_ready_mismatch"
    if not observation.source_remote_status_recorded:
        return "source_remote_status_mismatch"
    if observation.source_local_fallback_used:
        return "source_local_fallback_mismatch"
    if observation.source_selected_case_count != 8:
        return "source_case_count_mismatch"
    if observation.source_selected_valid_metadata_only_case_count != 3:
        return "source_valid_case_count_mismatch"
    if observation.source_selected_invalid_fail_closed_case_count != 5:
        return "source_fail_closed_case_count_mismatch"
    if observation.source_observed_pass_case_count != 3:
        return "source_status_mismatch"
    if observation.source_observed_fail_closed_case_count != 5:
        return "source_status_mismatch"
    if observation.source_observed_usage_error_case_count != 0:
        return "source_status_mismatch"
    if observation.source_observed_mismatch_case_count != 0:
        return "source_status_mismatch"
    return "none"


def _validate_expected_observed_counts(
    observations: Sequence[HandoffInputObservation],
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
    observations: Sequence[HandoffInputObservation],
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
    observations: Sequence[HandoffInputObservation],
    *,
    status: str,
    reason_code: str,
    input_error_case_count: int = 0,
    selected_case_count: int | None = None,
) -> HandoffInputSummary:
    counts = _actual_counts(observations)
    selected = selected_case_count if selected_case_count is not None else len(observations)
    return HandoffInputSummary(
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
    observations: Sequence[HandoffInputObservation],
) -> dict[str, int]:
    counts = {count_field: 0 for count_field in ACTUAL_FLAG_TO_COUNT_FIELD.values()}
    for observation in observations:
        for field_name, count_field in ACTUAL_FLAG_TO_COUNT_FIELD.items():
            if _as_bool(getattr(observation, field_name)):
                counts[count_field] += 1
    return counts


def _count_by_expected_status(
    observations: Sequence[HandoffInputObservation],
    status: str,
) -> int:
    return sum(1 for observation in observations if observation.expected_status == status)


def _usage_error(
    reason_code: str,
    *,
    case_selection: str,
) -> HandoffInputSummary:
    return HandoffInputSummary(
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
            "Validate manifest-writer handoff input metadata without writer "
            "invocation."
        )
    )
    parser.add_argument("--fixture-root", type=Path, default=DEFAULT_FIXTURE_ROOT)
    parser.add_argument("--case-selection", required=True)
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--no-manifest-writer", action="store_true")
    parser.add_argument("--no-file-writing", action="store_true")
    parser.add_argument("--fail-closed-on-forbidden-body", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    summary = run_manifest_writer_handoff_input_validation(
        args.fixture_root,
        case_selection=args.case_selection,
        summary_only=args.summary_only,
        no_manifest_writer=args.no_manifest_writer,
        no_file_writing=args.no_file_writing,
        fail_closed_on_forbidden_body=args.fail_closed_on_forbidden_body,
    )
    sys.stdout.write(format_public_summary(summary.to_public_dict()))
    sys.stdout.write("\n")
    return summary.return_code


if __name__ == "__main__":
    raise SystemExit(main())
