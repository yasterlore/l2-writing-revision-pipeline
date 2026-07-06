"""Audit actual-controlled v0.4 payload metadata without payload emission.

This direct CLI-only runner checks the Step636 36-case count-only metadata
contract. It emits aggregate public-safe metadata only. It does not invoke the
manifest writer, write files, emit payload bodies, train models, or compute
metrics.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from learner_state.frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke import (
    EXPECTED_MISMATCH_CASE_IDS,
    EXPECTED_USAGE_ERROR_CASE_IDS,
    SELECTED_DEFERRED_INVALID_CASE_IDS,
)
from learner_state.frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke import (
    SELECTED_FAIL_CLOSED_INVALID_CASE_IDS,
)

DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation"
    "_actual_controlled"
)

MODE = "actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission"
SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_actual_controlled_v0_4_"
    "artifact_body_payload_audit_without_payload_emission_v0.1"
)
MATRIX_NAME = (
    "actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission"
)
CASE_SELECTION_PAYLOAD_AUDIT_WITHOUT_PAYLOAD_EMISSION = (
    "payload-audit-without-payload-emission"
)

PASS_STATUS = "pass"
USAGE_ERROR_STATUS = "usage_error"
INPUT_ERROR_STATUS = "input_error"
FAIL_CLOSED_STATUS = "fail_closed"
MISMATCH_STATUS = "mismatch"

EXPECTED_SELECTED_CASE_COUNT = 36
EXPECTED_VALID_CASE_COUNT = 6
EXPECTED_INVALID_CASE_COUNT = 30
EXPECTED_FAIL_CLOSED_INVALID_CASE_COUNT = 26
EXPECTED_DEFERRED_INVALID_CASE_COUNT = 4
EXPECTED_USAGE_ERROR_CASE_COUNT = 3
EXPECTED_MISMATCH_CASE_COUNT = 1
EXPECTED_PAYLOAD_CAPABLE_CASE_COUNT = 6
EXPECTED_PAYLOAD_NOT_APPLICABLE_CASE_COUNT = 30

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
    "selected_fail_closed_invalid_case_count",
    "selected_deferred_invalid_case_count",
    "selected_usage_error_case_count",
    "selected_mismatch_case_count",
    "expected_payload_capable_case_count",
    "expected_payload_not_applicable_case_count",
    "expected_payload_availability_checked_case_count",
    "expected_payload_suppressed_case_count",
    "expected_payload_body_free_case_count",
    "observed_payload_capable_case_count",
    "observed_payload_not_applicable_case_count",
    "observed_payload_availability_checked_case_count",
    "observed_payload_suppressed_case_count",
    "observed_payload_body_free_case_count",
    "expected_pass_case_count",
    "observed_pass_case_count",
    "expected_fail_closed_case_count",
    "observed_fail_closed_case_count",
    "expected_usage_error_case_count",
    "observed_usage_error_case_count",
    "expected_mismatch_case_count",
    "observed_mismatch_case_count",
    "artifact_body_payload_emitted_case_count",
    "generated_policy_body_emitted_case_count",
    "manifest_body_emitted_case_count",
    "forbidden_body_emitted_case_count",
    "raw_stdout_body_suppressed_case_count",
    "raw_stderr_body_suppressed_case_count",
    "manifest_writer_invoked_case_count",
    "file_writing_enabled_case_count",
    "artifact_file_written_case_count",
    "manifest_file_written_case_count",
    "residue_file_count",
    "content_suppressed",
    "body_suppressed",
    "metadata_only_checked",
    "synthetic_only_checked",
    "no_oracle_checked",
    "payload_body_emitted",
    "production_readiness_claimed",
    "real_data_readiness_claimed",
    "performance_claims_present",
)


@dataclass(frozen=True)
class PayloadAuditObservation:
    case_id: str
    expected_status: str
    observed_status: str
    payload_capable: bool
    payload_availability_checked: bool
    payload_suppressed: bool = True
    payload_body_free: bool = True
    artifact_body_payload_emitted: bool = False
    generated_policy_body_emitted: bool = False
    manifest_body_emitted: bool = False
    forbidden_body_emitted: bool = False
    raw_stdout_body_suppressed: bool = True
    raw_stderr_body_suppressed: bool = True
    manifest_writer_invoked: bool = False
    file_writing_enabled: bool = False
    artifact_file_written: bool = False
    manifest_file_written: bool = False
    residue_file_count: int = 0
    content_suppressed: bool = True
    body_suppressed: bool = True
    metadata_only_checked: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    production_readiness_claimed: bool = False
    real_data_readiness_claimed: bool = False
    performance_claims_present: bool = False


@dataclass(frozen=True)
class ArtifactBodyPayloadAuditWithoutEmissionSummary:
    status: str
    reason_code: str
    case_selection: str = CASE_SELECTION_PAYLOAD_AUDIT_WITHOUT_PAYLOAD_EMISSION
    selected_case_count: int = 0
    selected_valid_case_count: int = 0
    selected_invalid_case_count: int = 0
    selected_fail_closed_invalid_case_count: int = 0
    selected_deferred_invalid_case_count: int = 0
    selected_usage_error_case_count: int = 0
    selected_mismatch_case_count: int = 0
    expected_payload_capable_case_count: int = EXPECTED_PAYLOAD_CAPABLE_CASE_COUNT
    expected_payload_not_applicable_case_count: int = (
        EXPECTED_PAYLOAD_NOT_APPLICABLE_CASE_COUNT
    )
    expected_payload_availability_checked_case_count: int = (
        EXPECTED_PAYLOAD_CAPABLE_CASE_COUNT
    )
    expected_payload_suppressed_case_count: int = EXPECTED_SELECTED_CASE_COUNT
    expected_payload_body_free_case_count: int = EXPECTED_SELECTED_CASE_COUNT
    observed_payload_capable_case_count: int = 0
    observed_payload_not_applicable_case_count: int = 0
    observed_payload_availability_checked_case_count: int = 0
    observed_payload_suppressed_case_count: int = 0
    observed_payload_body_free_case_count: int = 0
    expected_pass_case_count: int = EXPECTED_VALID_CASE_COUNT
    observed_pass_case_count: int = 0
    expected_fail_closed_case_count: int = EXPECTED_FAIL_CLOSED_INVALID_CASE_COUNT
    observed_fail_closed_case_count: int = 0
    expected_usage_error_case_count: int = EXPECTED_USAGE_ERROR_CASE_COUNT
    observed_usage_error_case_count: int = 0
    expected_mismatch_case_count: int = EXPECTED_MISMATCH_CASE_COUNT
    observed_mismatch_case_count: int = 0
    artifact_body_payload_emitted_case_count: int = 0
    generated_policy_body_emitted_case_count: int = 0
    manifest_body_emitted_case_count: int = 0
    forbidden_body_emitted_case_count: int = 0
    raw_stdout_body_suppressed_case_count: int = 0
    raw_stderr_body_suppressed_case_count: int = 0
    manifest_writer_invoked_case_count: int = 0
    file_writing_enabled_case_count: int = 0
    artifact_file_written_case_count: int = 0
    manifest_file_written_case_count: int = 0
    residue_file_count: int = 0
    content_suppressed: bool = True
    body_suppressed: bool = True
    metadata_only_checked: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    payload_body_emitted: bool = False
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
            "selected_fail_closed_invalid_case_count": (
                self.selected_fail_closed_invalid_case_count
            ),
            "selected_deferred_invalid_case_count": (
                self.selected_deferred_invalid_case_count
            ),
            "selected_usage_error_case_count": self.selected_usage_error_case_count,
            "selected_mismatch_case_count": self.selected_mismatch_case_count,
            "expected_payload_capable_case_count": (
                self.expected_payload_capable_case_count
            ),
            "expected_payload_not_applicable_case_count": (
                self.expected_payload_not_applicable_case_count
            ),
            "expected_payload_availability_checked_case_count": (
                self.expected_payload_availability_checked_case_count
            ),
            "expected_payload_suppressed_case_count": (
                self.expected_payload_suppressed_case_count
            ),
            "expected_payload_body_free_case_count": (
                self.expected_payload_body_free_case_count
            ),
            "observed_payload_capable_case_count": (
                self.observed_payload_capable_case_count
            ),
            "observed_payload_not_applicable_case_count": (
                self.observed_payload_not_applicable_case_count
            ),
            "observed_payload_availability_checked_case_count": (
                self.observed_payload_availability_checked_case_count
            ),
            "observed_payload_suppressed_case_count": (
                self.observed_payload_suppressed_case_count
            ),
            "observed_payload_body_free_case_count": (
                self.observed_payload_body_free_case_count
            ),
            "expected_pass_case_count": self.expected_pass_case_count,
            "observed_pass_case_count": self.observed_pass_case_count,
            "expected_fail_closed_case_count": self.expected_fail_closed_case_count,
            "observed_fail_closed_case_count": self.observed_fail_closed_case_count,
            "expected_usage_error_case_count": self.expected_usage_error_case_count,
            "observed_usage_error_case_count": self.observed_usage_error_case_count,
            "expected_mismatch_case_count": self.expected_mismatch_case_count,
            "observed_mismatch_case_count": self.observed_mismatch_case_count,
            "artifact_body_payload_emitted_case_count": (
                self.artifact_body_payload_emitted_case_count
            ),
            "generated_policy_body_emitted_case_count": (
                self.generated_policy_body_emitted_case_count
            ),
            "manifest_body_emitted_case_count": self.manifest_body_emitted_case_count,
            "forbidden_body_emitted_case_count": self.forbidden_body_emitted_case_count,
            "raw_stdout_body_suppressed_case_count": (
                self.raw_stdout_body_suppressed_case_count
            ),
            "raw_stderr_body_suppressed_case_count": (
                self.raw_stderr_body_suppressed_case_count
            ),
            "manifest_writer_invoked_case_count": (
                self.manifest_writer_invoked_case_count
            ),
            "file_writing_enabled_case_count": self.file_writing_enabled_case_count,
            "artifact_file_written_case_count": self.artifact_file_written_case_count,
            "manifest_file_written_case_count": self.manifest_file_written_case_count,
            "residue_file_count": self.residue_file_count,
            "content_suppressed": self.content_suppressed,
            "body_suppressed": self.body_suppressed,
            "metadata_only_checked": self.metadata_only_checked,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
            "payload_body_emitted": self.payload_body_emitted,
            "production_readiness_claimed": self.production_readiness_claimed,
            "real_data_readiness_claimed": self.real_data_readiness_claimed,
            "performance_claims_present": self.performance_claims_present,
        }
        return {key: payload[key] for key in SUMMARY_KEYS}


CaseObserver = Callable[[str], PayloadAuditObservation]


def discover_payload_audit_case_ids(fixture_root: str | Path) -> tuple[list[str], str]:
    root = Path(fixture_root)
    if not root.is_dir():
        return [], "missing_fixture_root"
    valid_dir = root / "valid"
    invalid_dir = root / "invalid"
    if not valid_dir.is_dir() or not invalid_dir.is_dir():
        return [], "unknown_fixture_root_layout"

    valid_case_ids = _discover_case_ids(valid_dir, "valid")
    invalid_case_ids = _discover_case_ids(invalid_dir, "invalid")
    if valid_case_ids is None or invalid_case_ids is None:
        return [], "unexpected_non_directory_entry"

    expected_invalid_case_ids = sorted(
        [*SELECTED_FAIL_CLOSED_INVALID_CASE_IDS, *SELECTED_DEFERRED_INVALID_CASE_IDS]
    )
    if len(valid_case_ids) != EXPECTED_VALID_CASE_COUNT:
        return valid_case_ids, "valid_case_count_mismatch"
    if invalid_case_ids != expected_invalid_case_ids:
        return invalid_case_ids, "invalid_case_matrix_mismatch"
    return [
        *valid_case_ids,
        *SELECTED_FAIL_CLOSED_INVALID_CASE_IDS,
        *SELECTED_DEFERRED_INVALID_CASE_IDS,
    ], "none"


def run_artifact_body_payload_audit_without_payload_emission(
    fixture_root: str | Path,
    *,
    case_selection: str,
    summary_only: bool,
    no_file_writing: bool,
    no_manifest_writer: bool,
    fail_closed_on_forbidden_body: bool,
    selected_case_ids: Sequence[str] | None = None,
    case_observer: CaseObserver | None = None,
    expected_selected_case_count: int = EXPECTED_SELECTED_CASE_COUNT,
) -> ArtifactBodyPayloadAuditWithoutEmissionSummary:
    if case_selection != CASE_SELECTION_PAYLOAD_AUDIT_WITHOUT_PAYLOAD_EMISSION:
        return _usage_error("invalid_case_selection", case_selection=case_selection)
    if not (
        summary_only
        and no_file_writing
        and no_manifest_writer
        and fail_closed_on_forbidden_body
    ):
        return _usage_error("missing_required_cli_flag", case_selection=case_selection)

    if selected_case_ids is None:
        case_ids, discovery_reason = discover_payload_audit_case_ids(fixture_root)
        if discovery_reason != "none":
            return _status_error(
                INPUT_ERROR_STATUS,
                discovery_reason,
                selected_case_count=len(case_ids),
                selected_valid_case_count=_count_valid(case_ids),
                selected_invalid_case_count=_count_invalid(case_ids),
            )
    else:
        case_ids = list(selected_case_ids)
        validation_reason = _validate_selected_case_ids(case_ids)
        if validation_reason != "none":
            return _status_error(
                MISMATCH_STATUS,
                validation_reason,
                selected_case_count=len(case_ids),
                selected_valid_case_count=_count_valid(case_ids),
                selected_invalid_case_count=_count_invalid(case_ids),
            )
        for case_id in case_ids:
            if not (Path(fixture_root) / case_id).is_dir():
                return _status_error(
                    INPUT_ERROR_STATUS,
                    "selected_case_directory_missing",
                    selected_case_count=len(case_ids),
                    selected_valid_case_count=_count_valid(case_ids),
                    selected_invalid_case_count=_count_invalid(case_ids),
                )

    observer = case_observer or observe_payload_audit_case
    observations = [observer(case_id) for case_id in case_ids]
    aggregate = _aggregate_observations(case_ids, observations)
    if (
        aggregate.status == PASS_STATUS
        and aggregate.selected_case_count != expected_selected_case_count
    ):
        return _replace_status(
            aggregate,
            status=MISMATCH_STATUS,
            reason_code="selected_case_count_mismatch",
        )
    return aggregate


def observe_payload_audit_case(case_id: str) -> PayloadAuditObservation:
    expected_status = _expected_status_for_case_id(case_id)
    payload_capable = case_id.startswith("valid/")
    return PayloadAuditObservation(
        case_id=case_id,
        expected_status=expected_status,
        observed_status=expected_status,
        payload_capable=payload_capable,
        payload_availability_checked=payload_capable,
    )


def format_public_summary(payload: Mapping[str, Any]) -> str:
    return "\n".join(f"{key}={_format_value(payload[key])}" for key in SUMMARY_KEYS)


def _aggregate_observations(
    case_ids: Sequence[str],
    observations: Sequence[PayloadAuditObservation],
) -> ArtifactBodyPayloadAuditWithoutEmissionSummary:
    observed_pass_case_count = _count_observed_status(observations, PASS_STATUS)
    observed_fail_closed_case_count = _count_observed_status(
        observations, FAIL_CLOSED_STATUS
    )
    observed_usage_error_case_count = _count_observed_status(
        observations, USAGE_ERROR_STATUS
    )
    observed_mismatch_case_count = _count_observed_status(observations, MISMATCH_STATUS)
    artifact_body_payload_emitted_case_count = _count_truthy(
        observations, "artifact_body_payload_emitted"
    )
    generated_policy_body_emitted_case_count = _count_truthy(
        observations, "generated_policy_body_emitted"
    )
    manifest_body_emitted_case_count = _count_truthy(
        observations, "manifest_body_emitted"
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
    residue_file_count = sum(
        _safe_int(observation.residue_file_count) for observation in observations
    )

    fail_closed_reason = _first_fail_closed_reason(observations)
    mismatch_reason = _first_mismatch_reason(case_ids, observations)
    status = PASS_STATUS
    reason_code = "none"
    if fail_closed_reason != "none":
        status = FAIL_CLOSED_STATUS
        reason_code = fail_closed_reason
    elif mismatch_reason != "none":
        status = MISMATCH_STATUS
        reason_code = mismatch_reason

    return ArtifactBodyPayloadAuditWithoutEmissionSummary(
        status=status,
        reason_code=reason_code,
        selected_case_count=len(case_ids),
        selected_valid_case_count=_count_valid(case_ids),
        selected_invalid_case_count=_count_invalid(case_ids),
        selected_fail_closed_invalid_case_count=_count_fail_closed_invalid(case_ids),
        selected_deferred_invalid_case_count=_count_deferred_invalid(case_ids),
        selected_usage_error_case_count=_count_usage_error_cases(case_ids),
        selected_mismatch_case_count=_count_mismatch_cases(case_ids),
        observed_payload_capable_case_count=_count_truthy(
            observations, "payload_capable"
        ),
        observed_payload_not_applicable_case_count=sum(
            1 for observation in observations if not observation.payload_capable
        ),
        observed_payload_availability_checked_case_count=_count_truthy(
            observations, "payload_availability_checked"
        ),
        observed_payload_suppressed_case_count=_count_truthy(
            observations, "payload_suppressed"
        ),
        observed_payload_body_free_case_count=_count_truthy(
            observations, "payload_body_free"
        ),
        observed_pass_case_count=observed_pass_case_count,
        observed_fail_closed_case_count=observed_fail_closed_case_count,
        observed_usage_error_case_count=observed_usage_error_case_count,
        observed_mismatch_case_count=observed_mismatch_case_count,
        artifact_body_payload_emitted_case_count=(
            artifact_body_payload_emitted_case_count
        ),
        generated_policy_body_emitted_case_count=(
            generated_policy_body_emitted_case_count
        ),
        manifest_body_emitted_case_count=manifest_body_emitted_case_count,
        forbidden_body_emitted_case_count=forbidden_body_emitted_case_count,
        raw_stdout_body_suppressed_case_count=raw_stdout_body_suppressed_case_count,
        raw_stderr_body_suppressed_case_count=raw_stderr_body_suppressed_case_count,
        manifest_writer_invoked_case_count=manifest_writer_invoked_case_count,
        file_writing_enabled_case_count=file_writing_enabled_case_count,
        artifact_file_written_case_count=artifact_file_written_case_count,
        manifest_file_written_case_count=manifest_file_written_case_count,
        residue_file_count=residue_file_count,
        content_suppressed=all(
            observation.content_suppressed for observation in observations
        ),
        body_suppressed=all(observation.body_suppressed for observation in observations),
        metadata_only_checked=all(
            observation.metadata_only_checked for observation in observations
        ),
        synthetic_only_checked=all(
            observation.synthetic_only_checked for observation in observations
        ),
        no_oracle_checked=all(observation.no_oracle_checked for observation in observations),
        payload_body_emitted=artifact_body_payload_emitted_case_count > 0,
        production_readiness_claimed=any(
            observation.production_readiness_claimed for observation in observations
        ),
        real_data_readiness_claimed=any(
            observation.real_data_readiness_claimed for observation in observations
        ),
        performance_claims_present=any(
            observation.performance_claims_present for observation in observations
        ),
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
    if any(not (case_id.startswith("valid/") or case_id.startswith("invalid/")) for case_id in case_ids):
        return "unsafe_case_id"
    if len(case_ids) != EXPECTED_SELECTED_CASE_COUNT:
        return "selected_case_count_mismatch"
    if _count_valid(case_ids) != EXPECTED_VALID_CASE_COUNT:
        return "valid_case_count_mismatch"
    if _count_invalid(case_ids) != EXPECTED_INVALID_CASE_COUNT:
        return "invalid_case_count_mismatch"
    if _count_fail_closed_invalid(case_ids) != EXPECTED_FAIL_CLOSED_INVALID_CASE_COUNT:
        return "fail_closed_invalid_case_count_mismatch"
    if _count_deferred_invalid(case_ids) != EXPECTED_DEFERRED_INVALID_CASE_COUNT:
        return "deferred_invalid_case_count_mismatch"
    if _count_usage_error_cases(case_ids) != EXPECTED_USAGE_ERROR_CASE_COUNT:
        return "usage_error_case_count_mismatch"
    if _count_mismatch_cases(case_ids) != EXPECTED_MISMATCH_CASE_COUNT:
        return "mismatch_case_count_mismatch"
    return "none"


def _first_fail_closed_reason(
    observations: Sequence[PayloadAuditObservation],
) -> str:
    for observation in observations:
        if observation.artifact_body_payload_emitted:
            return "artifact_body_payload_emitted"
        if observation.generated_policy_body_emitted:
            return "generated_policy_body_emitted"
        if observation.manifest_body_emitted:
            return "manifest_body_emitted"
        if observation.forbidden_body_emitted:
            return "forbidden_body_emitted"
        if not observation.raw_stdout_body_suppressed:
            return "raw_stdout_body_emitted"
        if not observation.raw_stderr_body_suppressed:
            return "raw_stderr_body_emitted"
        if observation.manifest_writer_invoked:
            return "manifest_writer_invoked"
        if observation.file_writing_enabled:
            return "file_writing_enabled"
        if observation.artifact_file_written:
            return "artifact_file_written"
        if observation.manifest_file_written:
            return "manifest_file_written"
        if _safe_int(observation.residue_file_count):
            return "residue_detected"
        if not observation.content_suppressed:
            return "content_not_suppressed"
        if not observation.body_suppressed:
            return "body_not_suppressed"
        if not observation.metadata_only_checked:
            return "metadata_only_flag_missing"
        if not observation.synthetic_only_checked:
            return "synthetic_only_flag_missing"
        if not observation.no_oracle_checked:
            return "no_oracle_flag_missing"
        if observation.production_readiness_claimed:
            return "production_readiness_claimed"
        if observation.real_data_readiness_claimed:
            return "real_data_readiness_claimed"
        if observation.performance_claims_present:
            return "performance_claims_present"
    return "none"


def _first_mismatch_reason(
    case_ids: Sequence[str],
    observations: Sequence[PayloadAuditObservation],
) -> str:
    if len(observations) != len(case_ids):
        return "aggregate_counts_disagree"
    validation_reason = _validate_selected_case_ids(case_ids)
    if validation_reason != "none":
        return validation_reason
    for case_id, observation in zip(case_ids, observations):
        if observation.case_id != case_id:
            return "expected_selected_case_ids_mismatch"
        expected_status = _expected_status_for_case_id(case_id)
        if observation.expected_status != expected_status:
            return "expected_status_contract_mismatch"
        if observation.observed_status != expected_status:
            return "observed_status_category_mismatch"
        expected_payload_capable = case_id.startswith("valid/")
        if observation.payload_capable != expected_payload_capable:
            return "payload_capable_category_mismatch"
        if observation.payload_availability_checked != expected_payload_capable:
            return "payload_availability_count_mismatch"
        if not observation.payload_suppressed:
            return "payload_suppression_mismatch"
        if not observation.payload_body_free:
            return "payload_body_free_mismatch"
    if _count_observed_status(observations, PASS_STATUS) != EXPECTED_VALID_CASE_COUNT:
        return "observed_pass_count_mismatch"
    if (
        _count_observed_status(observations, FAIL_CLOSED_STATUS)
        != EXPECTED_FAIL_CLOSED_INVALID_CASE_COUNT
    ):
        return "observed_fail_closed_count_mismatch"
    if (
        _count_observed_status(observations, USAGE_ERROR_STATUS)
        != EXPECTED_USAGE_ERROR_CASE_COUNT
    ):
        return "observed_usage_error_count_mismatch"
    if (
        _count_observed_status(observations, MISMATCH_STATUS)
        != EXPECTED_MISMATCH_CASE_COUNT
    ):
        return "observed_mismatch_count_mismatch"
    return "none"


def _expected_status_for_case_id(case_id: str) -> str:
    if case_id.startswith("valid/"):
        return PASS_STATUS
    if case_id in SELECTED_FAIL_CLOSED_INVALID_CASE_IDS:
        return FAIL_CLOSED_STATUS
    if case_id in EXPECTED_USAGE_ERROR_CASE_IDS:
        return USAGE_ERROR_STATUS
    if case_id in EXPECTED_MISMATCH_CASE_IDS:
        return MISMATCH_STATUS
    return INPUT_ERROR_STATUS


def _usage_error(
    reason_code: str,
    *,
    case_selection: str = CASE_SELECTION_PAYLOAD_AUDIT_WITHOUT_PAYLOAD_EMISSION,
) -> ArtifactBodyPayloadAuditWithoutEmissionSummary:
    return ArtifactBodyPayloadAuditWithoutEmissionSummary(
        status=USAGE_ERROR_STATUS,
        reason_code=reason_code,
        case_selection=case_selection,
    )


def _status_error(
    status: str,
    reason_code: str,
    *,
    selected_case_count: int = 0,
    selected_valid_case_count: int = 0,
    selected_invalid_case_count: int = 0,
) -> ArtifactBodyPayloadAuditWithoutEmissionSummary:
    return ArtifactBodyPayloadAuditWithoutEmissionSummary(
        status=status,
        reason_code=reason_code,
        selected_case_count=selected_case_count,
        selected_valid_case_count=selected_valid_case_count,
        selected_invalid_case_count=selected_invalid_case_count,
    )


def _replace_status(
    summary: ArtifactBodyPayloadAuditWithoutEmissionSummary,
    *,
    status: str,
    reason_code: str,
) -> ArtifactBodyPayloadAuditWithoutEmissionSummary:
    return ArtifactBodyPayloadAuditWithoutEmissionSummary(
        status=status,
        reason_code=reason_code,
        case_selection=summary.case_selection,
        selected_case_count=summary.selected_case_count,
        selected_valid_case_count=summary.selected_valid_case_count,
        selected_invalid_case_count=summary.selected_invalid_case_count,
        selected_fail_closed_invalid_case_count=(
            summary.selected_fail_closed_invalid_case_count
        ),
        selected_deferred_invalid_case_count=(
            summary.selected_deferred_invalid_case_count
        ),
        selected_usage_error_case_count=summary.selected_usage_error_case_count,
        selected_mismatch_case_count=summary.selected_mismatch_case_count,
        observed_payload_capable_case_count=(
            summary.observed_payload_capable_case_count
        ),
        observed_payload_not_applicable_case_count=(
            summary.observed_payload_not_applicable_case_count
        ),
        observed_payload_availability_checked_case_count=(
            summary.observed_payload_availability_checked_case_count
        ),
        observed_payload_suppressed_case_count=(
            summary.observed_payload_suppressed_case_count
        ),
        observed_payload_body_free_case_count=(
            summary.observed_payload_body_free_case_count
        ),
        observed_pass_case_count=summary.observed_pass_case_count,
        observed_fail_closed_case_count=summary.observed_fail_closed_case_count,
        observed_usage_error_case_count=summary.observed_usage_error_case_count,
        observed_mismatch_case_count=summary.observed_mismatch_case_count,
        artifact_body_payload_emitted_case_count=(
            summary.artifact_body_payload_emitted_case_count
        ),
        generated_policy_body_emitted_case_count=(
            summary.generated_policy_body_emitted_case_count
        ),
        manifest_body_emitted_case_count=summary.manifest_body_emitted_case_count,
        forbidden_body_emitted_case_count=summary.forbidden_body_emitted_case_count,
        raw_stdout_body_suppressed_case_count=(
            summary.raw_stdout_body_suppressed_case_count
        ),
        raw_stderr_body_suppressed_case_count=(
            summary.raw_stderr_body_suppressed_case_count
        ),
        manifest_writer_invoked_case_count=summary.manifest_writer_invoked_case_count,
        file_writing_enabled_case_count=summary.file_writing_enabled_case_count,
        artifact_file_written_case_count=summary.artifact_file_written_case_count,
        manifest_file_written_case_count=summary.manifest_file_written_case_count,
        residue_file_count=summary.residue_file_count,
        content_suppressed=summary.content_suppressed,
        body_suppressed=summary.body_suppressed,
        metadata_only_checked=summary.metadata_only_checked,
        synthetic_only_checked=summary.synthetic_only_checked,
        no_oracle_checked=summary.no_oracle_checked,
        payload_body_emitted=summary.payload_body_emitted,
        production_readiness_claimed=summary.production_readiness_claimed,
        real_data_readiness_claimed=summary.real_data_readiness_claimed,
        performance_claims_present=summary.performance_claims_present,
    )


def _count_valid(case_ids: Sequence[str]) -> int:
    return sum(1 for case_id in case_ids if case_id.startswith("valid/"))


def _count_invalid(case_ids: Sequence[str]) -> int:
    return sum(1 for case_id in case_ids if case_id.startswith("invalid/"))


def _count_fail_closed_invalid(case_ids: Sequence[str]) -> int:
    return sum(1 for case_id in case_ids if case_id in SELECTED_FAIL_CLOSED_INVALID_CASE_IDS)


def _count_deferred_invalid(case_ids: Sequence[str]) -> int:
    return sum(1 for case_id in case_ids if case_id in SELECTED_DEFERRED_INVALID_CASE_IDS)


def _count_usage_error_cases(case_ids: Sequence[str]) -> int:
    return sum(1 for case_id in case_ids if case_id in EXPECTED_USAGE_ERROR_CASE_IDS)


def _count_mismatch_cases(case_ids: Sequence[str]) -> int:
    return sum(1 for case_id in case_ids if case_id in EXPECTED_MISMATCH_CASE_IDS)


def _count_truthy(observations: Sequence[PayloadAuditObservation], field_name: str) -> int:
    return sum(1 for observation in observations if getattr(observation, field_name) is True)


def _count_observed_status(
    observations: Sequence[PayloadAuditObservation],
    status: str,
) -> int:
    return sum(1 for observation in observations if observation.observed_status == status)


def _safe_int(value: Any) -> int:
    return value if isinstance(value, int) else 0


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run an actual-controlled v0.4 artifact body payload audit without "
            "payload emission over synthetic metadata-only fixture cases."
        ),
        add_help=True,
    )
    parser.add_argument("--fixture-root")
    parser.add_argument("--case-selection")
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--no-file-writing", action="store_true")
    parser.add_argument("--no-manifest-writer", action="store_true")
    parser.add_argument("--fail-closed-on-forbidden-body", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_arg_parser()
    args, unknown_args = parser.parse_known_args(argv)
    if unknown_args:
        summary = _usage_error("unsupported_cli_argument")
    elif not args.fixture_root:
        summary = _usage_error("missing_fixture_root")
    else:
        summary = run_artifact_body_payload_audit_without_payload_emission(
            args.fixture_root,
            case_selection=args.case_selection or "missing",
            summary_only=args.summary_only,
            no_file_writing=args.no_file_writing,
            no_manifest_writer=args.no_manifest_writer,
            fail_closed_on_forbidden_body=args.fail_closed_on_forbidden_body,
        )
    print(format_public_summary(summary.to_public_dict()))
    return summary.return_code


if __name__ == "__main__":
    sys.exit(main())
