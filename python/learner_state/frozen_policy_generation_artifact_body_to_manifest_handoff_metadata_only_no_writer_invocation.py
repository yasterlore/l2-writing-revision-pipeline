"""Check artifact-body-to-manifest handoff metadata without writer invocation.

This runner reads a synthetic 8-case fixture contract and emits aggregate
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
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_body_to_manifest_handoff_"
    "metadata_only_no_writer_invocation"
)

MODE = "artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation"
SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_to_manifest_handoff_"
    "metadata_only_no_writer_invocation_v0.1"
)
MATRIX_NAME = (
    "artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation_matrix"
)
CASE_SELECTION = "artifact-body-to-manifest-handoff-metadata-only-no-writer"

PASS_STATUS = "pass"
USAGE_ERROR_STATUS = "usage_error"
FAIL_CLOSED_STATUS = "fail_closed"
MISMATCH_STATUS = "mismatch"

EXPECTED_VALID_CASE_IDS = (
    "valid/valid_handoff_metadata_minimal_no_writer",
    "valid/valid_handoff_metadata_count_only_summary",
    "valid/valid_handoff_metadata_no_residue",
)
EXPECTED_INVALID_FAIL_CLOSED_CASE_IDS = (
    "invalid/invalid_manifest_writer_invoked",
    "invalid/invalid_manifest_body_generated",
    "invalid/invalid_manifest_file_written",
    "invalid/invalid_artifact_or_payload_body_emitted",
    "invalid/invalid_private_or_absolute_path_detected",
)
EXPECTED_CASE_IDS = (*EXPECTED_VALID_CASE_IDS, *EXPECTED_INVALID_FAIL_CLOSED_CASE_IDS)

EXPECTED_SELECTED_CASE_COUNT = 8
EXPECTED_VALID_METADATA_ONLY_CASE_COUNT = 3
EXPECTED_INVALID_FAIL_CLOSED_CASE_COUNT = 5
EXPECTED_PASS_CASE_COUNT = 3
EXPECTED_FAIL_CLOSED_CASE_COUNT = 5
EXPECTED_USAGE_ERROR_CASE_COUNT = 0
EXPECTED_MISMATCH_CASE_COUNT = 0

FIXTURE_FILE_NAMES = (
    "case_metadata.json",
    "expected_summary_metadata.json",
    "safe_handoff_metadata.json",
)

ALLOWED_METADATA_KEYS = frozenset(
    {
        "case_id",
        "schema_version",
        "matrix_name",
        "case_selection",
        "handoff_mode",
        "expected_status",
        "expected_category",
        "unsafe_condition_category",
        "writer_invocation_enabled",
        "writer_invoked_actual",
        "manifest_body_generated_actual",
        "manifest_file_written_actual",
        "artifact_file_written_actual",
        "file_writing_enabled_actual",
        "payload_body_emitted_actual",
        "generated_policy_body_emitted_actual",
        "artifact_body_payload_output_actual",
        "request_body_output_actual",
        "pointer_body_output_actual",
        "expected_body_output_actual",
        "raw_stdout_body_suppressed",
        "raw_stderr_body_suppressed",
        "metadata_only_checked",
        "body_suppressed",
        "synthetic_only_checked",
        "no_oracle_checked",
        "forbidden_body_detected_actual",
        "private_path_detected_actual",
        "absolute_path_detected_actual",
        "raw_learner_text_detected_actual",
        "real_data_marker_detected_actual",
        "no_oracle_forbidden_field_detected_actual",
        "residue_file_count",
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
    }
)

ACTUAL_FLAG_TO_COUNT_FIELD = {
    "writer_invoked_actual": "manifest_writer_invoked_count",
    "manifest_body_generated_actual": "manifest_body_generated_count",
    "manifest_file_written_actual": "manifest_file_written_count",
    "artifact_file_written_actual": "artifact_file_written_count",
    "file_writing_enabled_actual": "file_writing_enabled_count",
    "payload_body_emitted_actual": "payload_body_emitted_count",
    "generated_policy_body_emitted_actual": "generated_policy_body_emitted_count",
    "artifact_body_payload_output_actual": "artifact_body_payload_output_count",
    "request_body_output_actual": "request_body_output_count",
    "pointer_body_output_actual": "pointer_body_output_count",
    "expected_body_output_actual": "expected_body_output_count",
    "forbidden_body_detected_actual": "forbidden_body_detected_count",
    "private_path_detected_actual": "private_path_detected_count",
    "absolute_path_detected_actual": "absolute_path_detected_count",
    "raw_learner_text_detected_actual": "raw_learner_text_detected_count",
    "real_data_marker_detected_actual": "real_data_marker_detected_count",
    "no_oracle_forbidden_field_detected_actual": (
        "no_oracle_forbidden_field_detected_count"
    ),
}

SUMMARY_KEYS = (
    "mode",
    "schema_version",
    "status",
    "reason_code",
    "matrix_name",
    "case_selection",
    "selected_case_count",
    "selected_valid_metadata_only_case_count",
    "selected_invalid_fail_closed_case_count",
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
    "manifest_writer_invoked_count",
    "manifest_body_generated_count",
    "manifest_body_output_count",
    "manifest_file_written_count",
    "artifact_file_written_count",
    "file_writing_enabled_count",
    "payload_body_emitted_count",
    "generated_policy_body_emitted_count",
    "artifact_body_payload_output_count",
    "request_body_output_count",
    "pointer_body_output_count",
    "expected_body_output_count",
    "raw_stdout_body_suppressed_count",
    "raw_stderr_body_suppressed_count",
    "forbidden_body_detected_count",
    "private_path_detected_count",
    "absolute_path_detected_count",
    "raw_learner_text_detected_count",
    "real_data_marker_detected_count",
    "no_oracle_forbidden_field_detected_count",
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
class HandoffCaseObservation:
    case_id: str
    schema_version: str
    matrix_name: str
    case_selection: str
    handoff_mode: str
    expected_status: str
    expected_category: str
    unsafe_condition_category: str
    observed_status: str
    writer_invoked_actual: bool = False
    manifest_body_generated_actual: bool = False
    manifest_file_written_actual: bool = False
    artifact_file_written_actual: bool = False
    file_writing_enabled_actual: bool = False
    payload_body_emitted_actual: bool = False
    generated_policy_body_emitted_actual: bool = False
    artifact_body_payload_output_actual: bool = False
    request_body_output_actual: bool = False
    pointer_body_output_actual: bool = False
    expected_body_output_actual: bool = False
    raw_stdout_body_suppressed: bool = True
    raw_stderr_body_suppressed: bool = True
    metadata_only_checked: bool = True
    body_suppressed: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    forbidden_body_detected_actual: bool = False
    private_path_detected_actual: bool = False
    absolute_path_detected_actual: bool = False
    raw_learner_text_detected_actual: bool = False
    real_data_marker_detected_actual: bool = False
    no_oracle_forbidden_field_detected_actual: bool = False
    residue_file_count: int = 0


@dataclass(frozen=True)
class HandoffSummary:
    status: str
    reason_code: str
    case_selection: str = CASE_SELECTION
    selected_case_count: int = 0
    selected_valid_metadata_only_case_count: int = 0
    selected_invalid_fail_closed_case_count: int = 0
    observed_pass_case_count: int = 0
    observed_fail_closed_case_count: int = 0
    observed_usage_error_case_count: int = 0
    observed_mismatch_case_count: int = 0
    processed_case_count: int = 0
    input_error_case_count: int = 0
    manifest_writer_invoked_count: int = 0
    manifest_body_generated_count: int = 0
    manifest_body_output_count: int = 0
    manifest_file_written_count: int = 0
    artifact_file_written_count: int = 0
    file_writing_enabled_count: int = 0
    payload_body_emitted_count: int = 0
    generated_policy_body_emitted_count: int = 0
    artifact_body_payload_output_count: int = 0
    request_body_output_count: int = 0
    pointer_body_output_count: int = 0
    expected_body_output_count: int = 0
    raw_stdout_body_suppressed_count: int = 0
    raw_stderr_body_suppressed_count: int = 0
    forbidden_body_detected_count: int = 0
    private_path_detected_count: int = 0
    absolute_path_detected_count: int = 0
    raw_learner_text_detected_count: int = 0
    real_data_marker_detected_count: int = 0
    no_oracle_forbidden_field_detected_count: int = 0
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
            "selected_valid_metadata_only_case_count": (
                self.selected_valid_metadata_only_case_count
            ),
            "selected_invalid_fail_closed_case_count": (
                self.selected_invalid_fail_closed_case_count
            ),
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
            "manifest_writer_invoked_count": self.manifest_writer_invoked_count,
            "manifest_body_generated_count": self.manifest_body_generated_count,
            "manifest_body_output_count": self.manifest_body_output_count,
            "manifest_file_written_count": self.manifest_file_written_count,
            "artifact_file_written_count": self.artifact_file_written_count,
            "file_writing_enabled_count": self.file_writing_enabled_count,
            "payload_body_emitted_count": self.payload_body_emitted_count,
            "generated_policy_body_emitted_count": (
                self.generated_policy_body_emitted_count
            ),
            "artifact_body_payload_output_count": (
                self.artifact_body_payload_output_count
            ),
            "request_body_output_count": self.request_body_output_count,
            "pointer_body_output_count": self.pointer_body_output_count,
            "expected_body_output_count": self.expected_body_output_count,
            "raw_stdout_body_suppressed_count": (
                self.raw_stdout_body_suppressed_count
            ),
            "raw_stderr_body_suppressed_count": (
                self.raw_stderr_body_suppressed_count
            ),
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


def run_artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation(
    fixture_root: str | Path,
    *,
    case_selection: str,
    summary_only: bool,
    no_manifest_writer: bool,
    no_file_writing: bool,
    fail_closed_on_forbidden_body: bool,
) -> HandoffSummary:
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
        selected_case_count = len(observations)
        return _summary_from_observations(
            observations,
            status=status,
            reason_code=reason_code,
            input_error_case_count=1 if status == USAGE_ERROR_STATUS else 0,
            selected_case_count=selected_case_count,
        )

    return _summary_from_observations(
        observations,
        status=PASS_STATUS,
        reason_code="none",
    )


def discover_handoff_case_ids(fixture_root: str | Path) -> tuple[list[str], str]:
    observations, reason_code, _status = _load_observations(Path(fixture_root))
    if reason_code != "none":
        return [observation.case_id for observation in observations], reason_code
    return [observation.case_id for observation in observations], "none"


def format_public_summary(payload: Mapping[str, Any]) -> str:
    return "\n".join(f"{key}={_format_value(payload[key])}" for key in SUMMARY_KEYS)


def _load_observations(
    fixture_root: Path,
) -> tuple[list[HandoffCaseObservation], str, str]:
    if not fixture_root.is_dir():
        return [], "missing_fixture_root", USAGE_ERROR_STATUS
    discovered_case_ids, discovery_reason = _discover_case_dir_ids(fixture_root)
    if discovery_reason != "none":
        return [], discovery_reason, MISMATCH_STATUS
    if tuple(discovered_case_ids) != EXPECTED_CASE_IDS:
        return [], "selected_case_ids_mismatch", MISMATCH_STATUS

    observations: list[HandoffCaseObservation] = []
    seen_case_ids: set[str] = set()
    for case_id in EXPECTED_CASE_IDS:
        case_dir = fixture_root / case_id
        if not case_dir.is_dir():
            return observations, "missing_case_directory", MISMATCH_STATUS
        observation, reason_code, status = _load_case_observation(case_dir)
        if reason_code != "none":
            if status == FAIL_CLOSED_STATUS:
                observations.append(observation)
            return observations, reason_code, status
        if observation.case_id in seen_case_ids:
            return observations, "duplicate_case_id", USAGE_ERROR_STATUS
        seen_case_ids.add(observation.case_id)
        observations.append(observation)

    validation_reason = _validate_observations(observations)
    if validation_reason != "none":
        status = (
            USAGE_ERROR_STATUS
            if validation_reason == "duplicate_case_id"
            else MISMATCH_STATUS
        )
        return observations, validation_reason, status

    fail_closed_reason = _first_fail_closed_reason(observations)
    if fail_closed_reason != "none":
        return observations, fail_closed_reason, FAIL_CLOSED_STATUS
    return observations, "none", PASS_STATUS


def _load_case_observation(
    case_dir: Path,
) -> tuple[HandoffCaseObservation, str, str]:
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
                forbidden_body_detected_actual=True,
            ), forbidden_reason, FAIL_CLOSED_STATUS
        merged.update(payload)

    unknown_keys = sorted(set(merged) - ALLOWED_METADATA_KEYS)
    if unknown_keys:
        return _observation_from_payload(
            merged,
            forbidden_body_detected_actual=True,
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
    if set(case_ids) != set(EXPECTED_CASE_IDS) or len(case_ids) != len(EXPECTED_CASE_IDS):
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
) -> HandoffCaseObservation:
    case_id = str(payload.get("case_id", "unknown"))
    expected_status = str(payload.get("expected_status", "unknown"))
    observation = HandoffCaseObservation(
        case_id=case_id,
        schema_version=str(payload.get("schema_version", "unknown")),
        matrix_name=str(payload.get("matrix_name", "unknown")),
        case_selection=str(payload.get("case_selection", "unknown")),
        handoff_mode=str(payload.get("handoff_mode", "unknown")),
        expected_status=expected_status,
        expected_category=str(payload.get("expected_category", "unknown")),
        unsafe_condition_category=str(
            payload.get("unsafe_condition_category", "unknown")
        ),
        observed_status=expected_status,
        writer_invoked_actual=_as_bool(payload.get("writer_invoked_actual")),
        manifest_body_generated_actual=_as_bool(
            payload.get("manifest_body_generated_actual")
        ),
        manifest_file_written_actual=_as_bool(
            payload.get("manifest_file_written_actual")
        ),
        artifact_file_written_actual=_as_bool(
            payload.get("artifact_file_written_actual")
        ),
        file_writing_enabled_actual=_as_bool(
            payload.get("file_writing_enabled_actual")
        ),
        payload_body_emitted_actual=_as_bool(
            payload.get("payload_body_emitted_actual")
        ),
        generated_policy_body_emitted_actual=_as_bool(
            payload.get("generated_policy_body_emitted_actual")
        ),
        artifact_body_payload_output_actual=_as_bool(
            payload.get("artifact_body_payload_output_actual")
        ),
        request_body_output_actual=_as_bool(
            payload.get("request_body_output_actual")
        ),
        pointer_body_output_actual=_as_bool(
            payload.get("pointer_body_output_actual")
        ),
        expected_body_output_actual=_as_bool(
            payload.get("expected_body_output_actual")
        ),
        raw_stdout_body_suppressed=_as_bool(
            payload.get("raw_stdout_body_suppressed"), default=True
        ),
        raw_stderr_body_suppressed=_as_bool(
            payload.get("raw_stderr_body_suppressed"), default=True
        ),
        metadata_only_checked=_as_bool(
            payload.get("metadata_only_checked"), default=True
        ),
        body_suppressed=_as_bool(payload.get("body_suppressed"), default=True),
        synthetic_only_checked=_as_bool(
            payload.get("synthetic_only_checked"), default=True
        ),
        no_oracle_checked=_as_bool(payload.get("no_oracle_checked"), default=True),
        forbidden_body_detected_actual=_as_bool(
            payload.get("forbidden_body_detected_actual")
        ),
        private_path_detected_actual=_as_bool(
            payload.get("private_path_detected_actual")
        ),
        absolute_path_detected_actual=_as_bool(
            payload.get("absolute_path_detected_actual")
        ),
        raw_learner_text_detected_actual=_as_bool(
            payload.get("raw_learner_text_detected_actual")
        ),
        real_data_marker_detected_actual=_as_bool(
            payload.get("real_data_marker_detected_actual")
        ),
        no_oracle_forbidden_field_detected_actual=_as_bool(
            payload.get("no_oracle_forbidden_field_detected_actual")
        ),
        residue_file_count=_as_int(payload.get("residue_file_count")),
    )
    if not overrides:
        return observation
    data = observation.__dict__.copy()
    data.update(overrides)
    return HandoffCaseObservation(**data)


def _empty_observation() -> HandoffCaseObservation:
    return HandoffCaseObservation(
        case_id="unknown",
        schema_version="unknown",
        matrix_name="unknown",
        case_selection="unknown",
        handoff_mode="unknown",
        expected_status=USAGE_ERROR_STATUS,
        expected_category="unknown",
        unsafe_condition_category="unknown",
        observed_status=USAGE_ERROR_STATUS,
    )


def _validate_observations(observations: Sequence[HandoffCaseObservation]) -> str:
    case_ids = [observation.case_id for observation in observations]
    if len(case_ids) != len(set(case_ids)):
        return "duplicate_case_id"
    if len(case_ids) != EXPECTED_SELECTED_CASE_COUNT:
        return "selected_case_count_mismatch"
    if tuple(case_ids) != EXPECTED_CASE_IDS:
        return "selected_case_ids_mismatch"
    if _count_valid(case_ids) != EXPECTED_VALID_METADATA_ONLY_CASE_COUNT:
        return "valid_metadata_only_case_count_mismatch"
    if _count_invalid(case_ids) != EXPECTED_INVALID_FAIL_CLOSED_CASE_COUNT:
        return "invalid_fail_closed_case_count_mismatch"

    for observation in observations:
        if observation.schema_version != SCHEMA_VERSION:
            return "schema_version_mismatch"
        if observation.matrix_name != MATRIX_NAME:
            return "matrix_name_mismatch"
        if observation.case_selection != CASE_SELECTION:
            return "case_selection_mismatch"
        if observation.handoff_mode != MODE:
            return "handoff_mode_mismatch"
        if observation.expected_status != _expected_status_for_case_id(
            observation.case_id
        ):
            return "expected_status_contract_mismatch"
        if observation.expected_category != _expected_category_for_case_id(
            observation.case_id
        ):
            return "expected_category_contract_mismatch"
        if observation.case_id.startswith("valid/"):
            if observation.unsafe_condition_category != "none":
                return "valid_unsafe_condition_mismatch"
        elif observation.unsafe_condition_category != _expected_unsafe_category(
            observation.case_id
        ):
            return "unsafe_condition_category_mismatch"
    return "none"


def _summary_from_observations(
    observations: Sequence[HandoffCaseObservation],
    *,
    status: str,
    reason_code: str,
    input_error_case_count: int = 0,
    selected_case_count: int | None = None,
) -> HandoffSummary:
    selected_count = len(observations) if selected_case_count is None else selected_case_count
    if status == PASS_STATUS:
        observed_pass_case_count = _count_observed_status(observations, PASS_STATUS)
        observed_fail_closed_case_count = _count_observed_status(
            observations, FAIL_CLOSED_STATUS
        )
        observed_usage_error_case_count = 0
        observed_mismatch_case_count = 0
    elif status == FAIL_CLOSED_STATUS:
        observed_pass_case_count = _count_observed_status(observations, PASS_STATUS)
        observed_fail_closed_case_count = _count_observed_status(
            observations, FAIL_CLOSED_STATUS
        )
        observed_usage_error_case_count = 0
        observed_mismatch_case_count = 0
    elif status == USAGE_ERROR_STATUS:
        observed_pass_case_count = 0
        observed_fail_closed_case_count = 0
        observed_usage_error_case_count = 1
        observed_mismatch_case_count = 0
    else:
        observed_pass_case_count = 0
        observed_fail_closed_case_count = 0
        observed_usage_error_case_count = 0
        observed_mismatch_case_count = 1

    count_fields = {field: 0 for field in ACTUAL_FLAG_TO_COUNT_FIELD.values()}
    for observation in observations:
        for flag_name, count_field in ACTUAL_FLAG_TO_COUNT_FIELD.items():
            if getattr(observation, flag_name) is True:
                count_fields[count_field] += 1
    residue_file_count = sum(_as_int(item.residue_file_count) for item in observations)
    manifest_body_output_count = 0
    if (
        reason_code == "forbidden_metadata_field"
        and count_fields["forbidden_body_detected_count"] == 0
    ):
        count_fields["forbidden_body_detected_count"] += 1

    return HandoffSummary(
        status=status,
        reason_code=reason_code,
        selected_case_count=selected_count,
        selected_valid_metadata_only_case_count=_count_valid(
            [observation.case_id for observation in observations]
        ),
        selected_invalid_fail_closed_case_count=_count_invalid(
            [observation.case_id for observation in observations]
        ),
        observed_pass_case_count=observed_pass_case_count,
        observed_fail_closed_case_count=observed_fail_closed_case_count,
        observed_usage_error_case_count=observed_usage_error_case_count,
        observed_mismatch_case_count=observed_mismatch_case_count,
        processed_case_count=len(observations),
        input_error_case_count=input_error_case_count,
        manifest_writer_invoked_count=count_fields["manifest_writer_invoked_count"],
        manifest_body_generated_count=count_fields["manifest_body_generated_count"],
        manifest_body_output_count=manifest_body_output_count,
        manifest_file_written_count=count_fields["manifest_file_written_count"],
        artifact_file_written_count=count_fields["artifact_file_written_count"],
        file_writing_enabled_count=count_fields["file_writing_enabled_count"],
        payload_body_emitted_count=count_fields["payload_body_emitted_count"],
        generated_policy_body_emitted_count=count_fields[
            "generated_policy_body_emitted_count"
        ],
        artifact_body_payload_output_count=count_fields[
            "artifact_body_payload_output_count"
        ],
        request_body_output_count=count_fields["request_body_output_count"],
        pointer_body_output_count=count_fields["pointer_body_output_count"],
        expected_body_output_count=count_fields["expected_body_output_count"],
        raw_stdout_body_suppressed_count=sum(
            1 for observation in observations if observation.raw_stdout_body_suppressed
        ),
        raw_stderr_body_suppressed_count=sum(
            1 for observation in observations if observation.raw_stderr_body_suppressed
        ),
        forbidden_body_detected_count=count_fields["forbidden_body_detected_count"],
        private_path_detected_count=count_fields["private_path_detected_count"],
        absolute_path_detected_count=count_fields["absolute_path_detected_count"],
        raw_learner_text_detected_count=count_fields[
            "raw_learner_text_detected_count"
        ],
        real_data_marker_detected_count=count_fields["real_data_marker_detected_count"],
        no_oracle_forbidden_field_detected_count=count_fields[
            "no_oracle_forbidden_field_detected_count"
        ],
        residue_file_count=residue_file_count,
        content_suppressed=all(observation.body_suppressed for observation in observations),
        body_suppressed=all(observation.body_suppressed for observation in observations),
        metadata_only_checked=all(
            observation.metadata_only_checked for observation in observations
        ),
        synthetic_only_checked=all(
            observation.synthetic_only_checked for observation in observations
        ),
        no_oracle_checked=all(observation.no_oracle_checked for observation in observations),
    )


def _first_fail_closed_reason(observations: Sequence[HandoffCaseObservation]) -> str:
    for observation in observations:
        if observation.writer_invoked_actual:
            return "manifest_writer_invoked"
        if observation.manifest_body_generated_actual:
            return "manifest_body_generated"
        if observation.manifest_file_written_actual:
            return "manifest_file_written"
        if observation.artifact_file_written_actual:
            return "artifact_file_written"
        if observation.file_writing_enabled_actual:
            return "file_writing_enabled"
        if observation.payload_body_emitted_actual:
            return "payload_body_emitted"
        if observation.generated_policy_body_emitted_actual:
            return "generated_policy_body_emitted"
        if observation.artifact_body_payload_output_actual:
            return "artifact_body_payload_output"
        if observation.request_body_output_actual:
            return "request_body_output"
        if observation.pointer_body_output_actual:
            return "pointer_body_output"
        if observation.expected_body_output_actual:
            return "expected_body_output"
        if not observation.raw_stdout_body_suppressed:
            return "raw_stdout_body_output"
        if not observation.raw_stderr_body_suppressed:
            return "raw_stderr_body_output"
        if observation.forbidden_body_detected_actual:
            return "forbidden_body_detected"
        if observation.private_path_detected_actual:
            return "private_path_detected"
        if observation.absolute_path_detected_actual:
            return "absolute_path_detected"
        if observation.raw_learner_text_detected_actual:
            return "raw_learner_text_detected"
        if observation.real_data_marker_detected_actual:
            return "real_data_marker_detected"
        if observation.no_oracle_forbidden_field_detected_actual:
            return "no_oracle_forbidden_field_detected"
        if _as_int(observation.residue_file_count) > 0:
            return "residue_detected"
        if not observation.body_suppressed:
            return "body_not_suppressed"
        if not observation.metadata_only_checked:
            return "metadata_only_flag_missing"
        if not observation.synthetic_only_checked:
            return "synthetic_only_flag_missing"
        if not observation.no_oracle_checked:
            return "no_oracle_flag_missing"
    return "none"


def _expected_status_for_case_id(case_id: str) -> str:
    if case_id in EXPECTED_VALID_CASE_IDS:
        return PASS_STATUS
    if case_id in EXPECTED_INVALID_FAIL_CLOSED_CASE_IDS:
        return FAIL_CLOSED_STATUS
    return MISMATCH_STATUS


def _expected_category_for_case_id(case_id: str) -> str:
    if case_id in EXPECTED_VALID_CASE_IDS:
        return "valid_metadata_only"
    if case_id in EXPECTED_INVALID_FAIL_CLOSED_CASE_IDS:
        return "invalid_fail_closed"
    return "unknown"


def _expected_unsafe_category(case_id: str) -> str:
    return {
        "invalid/invalid_manifest_writer_invoked": "manifest_writer_invoked",
        "invalid/invalid_manifest_body_generated": "manifest_body_generated",
        "invalid/invalid_manifest_file_written": "manifest_file_written",
        "invalid/invalid_artifact_or_payload_body_emitted": (
            "artifact_or_payload_body_emitted"
        ),
        "invalid/invalid_private_or_absolute_path_detected": (
            "private_or_absolute_path_detected"
        ),
    }.get(case_id, "unknown")


def _count_valid(case_ids: Sequence[str]) -> int:
    return sum(1 for case_id in case_ids if case_id.startswith("valid/"))


def _count_invalid(case_ids: Sequence[str]) -> int:
    return sum(1 for case_id in case_ids if case_id.startswith("invalid/"))


def _count_observed_status(
    observations: Sequence[HandoffCaseObservation],
    status: str,
) -> int:
    return sum(1 for observation in observations if observation.observed_status == status)


def _usage_error(
    reason_code: str,
    *,
    case_selection: str = CASE_SELECTION,
) -> HandoffSummary:
    return HandoffSummary(
        status=USAGE_ERROR_STATUS,
        reason_code=reason_code,
        case_selection=case_selection,
        observed_usage_error_case_count=1,
        input_error_case_count=1,
    )


def _as_bool(value: Any, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    return default


def _as_int(value: Any) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return 0


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run an artifact body to manifest handoff metadata-only "
            "no-writer-invocation check over synthetic fixtures."
        ),
        add_help=True,
    )
    parser.add_argument("--fixture-root")
    parser.add_argument("--case-selection")
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--no-manifest-writer", action="store_true")
    parser.add_argument("--no-file-writing", action="store_true")
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
        summary = run_artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation(
            args.fixture_root,
            case_selection=args.case_selection or "missing",
            summary_only=args.summary_only,
            no_manifest_writer=args.no_manifest_writer,
            no_file_writing=args.no_file_writing,
            fail_closed_on_forbidden_body=args.fail_closed_on_forbidden_body,
        )
    print(format_public_summary(summary.to_public_dict()))
    return summary.return_code


if __name__ == "__main__":
    sys.exit(main())
