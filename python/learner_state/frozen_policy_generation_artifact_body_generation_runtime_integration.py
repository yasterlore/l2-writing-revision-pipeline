"""Plan-only artifact body generation runtime integration boundary.

This module reads one synthetic metadata-only fixture case and emits a
body-free runtime handoff summary. It does not invoke artifact body
generation, call the manifest writer, write files, train models, or compute
metrics.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from learner_state.frozen_policy_generation_artifact_body_generation_integration_fixture_validation import (
    CASE_METADATA_FILE,
    CASE_SCHEMA_VERSION,
    EXPECTED_ERROR_FILE,
    EXPECTED_ERROR_SCHEMA_VERSION,
    EXPECTED_SUMMARY_FILE,
    EXPECTED_SUMMARY_SCHEMA_VERSION,
    GENERATION_METADATA_FILE,
    GENERATION_SCHEMA_VERSION,
    POINTER_METADATA_FILE,
    POINTER_SCHEMA_VERSION,
    REQUEST_METADATA_FILE,
    REQUEST_SCHEMA_VERSION,
    REQUIRED_FILES,
    RUNTIME_RESULT_SCHEMA_VERSION,
    RUNTIME_SUMMARY_FILE,
    RUNTIME_SUMMARY_SCHEMA_VERSION,
)
from learner_state.frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation import (
    EXPECTED_FILE_SCHEMAS as SAFE_METADATA_EXPECTED_FILE_SCHEMAS,
    PLANNED_MARKER as SAFE_METADATA_PLANNED_MARKER,
    RUNTIME_SCHEMA_VERSION as SAFE_METADATA_RUNTIME_SCHEMA_VERSION,
    SCHEMA_FAMILY as SAFE_METADATA_SCHEMA_FAMILY,
)

DEFAULT_FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_body_generation_integration"
)
DEFAULT_FIXTURE_CASE = "valid/valid_minimal_suppressed_metadata_only_bridge"

MODE = "artifact_body_generation_runtime_integration"
RUNTIME_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_"
    "runtime_integration_v0.1"
)
PLAN_ONLY_BRIDGE_MODE = "plan-only-bridge"
SAFE_METADATA_SMOKE_MODE = "safe-metadata-smoke"
SUPPRESSED_SMOKE_MODE = "suppressed-smoke"
RESERVED_MODES = frozenset({SUPPRESSED_SMOKE_MODE})

EXPECTED_FILE_SCHEMAS = {
    CASE_METADATA_FILE: CASE_SCHEMA_VERSION,
    RUNTIME_SUMMARY_FILE: RUNTIME_SUMMARY_SCHEMA_VERSION,
    REQUEST_METADATA_FILE: REQUEST_SCHEMA_VERSION,
    POINTER_METADATA_FILE: POINTER_SCHEMA_VERSION,
    GENERATION_METADATA_FILE: GENERATION_SCHEMA_VERSION,
    EXPECTED_SUMMARY_FILE: EXPECTED_SUMMARY_SCHEMA_VERSION,
    EXPECTED_ERROR_FILE: EXPECTED_ERROR_SCHEMA_VERSION,
}

SUMMARY_KEYS = (
    "mode",
    "runtime_schema_version",
    "status",
    "reason_code",
    "exit_code_category",
    "case_id",
    "integration_mode",
    "planned_root",
    "safe_metadata_v0_2_planned_checked",
    "artifact_body_runtime_invoked",
    "artifact_body_runtime_mode",
    "artifact_body_payload_available",
    "artifact_body_payload_emitted",
    "safe_metadata_body_available",
    "safe_metadata_body_field_count",
    "content_suppressed",
    "body_suppressed",
    "summary_only",
    "request_body_detected",
    "pointer_body_detected",
    "expected_body_detected",
    "artifact_body_payload_detected",
    "manifest_body_detected",
    "generated_policy_body_detected",
    "raw_stdout_body_suppressed",
    "raw_stderr_body_suppressed",
    "raw_rows_detected",
    "logits_detected",
    "private_path_detected",
    "absolute_path_detected",
    "raw_learner_text_detected",
    "real_data_marker_detected",
    "performance_metric_body_detected",
    "file_writing_enabled",
    "file_writing_detected",
    "manifest_writer_invoked",
    "artifact_file_written",
    "manifest_file_written",
    "runtime_safety_scan_passed",
    "runtime_fail_closed",
    "production_readiness_claimed",
    "real_data_readiness_claimed",
    "performance_claims_present",
    "runtime_summary_checked",
    "artifact_body_request_checked",
    "artifact_body_pointer_checked",
    "artifact_body_generation_metadata_checked",
    "metadata_file_count",
    "unsafe_signal_count",
)

USAGE_ERROR_REASONS = frozenset(
    {
        "missing_fixture",
        "missing_required_metadata_file",
        "unsupported_mode",
        "unsupported_schema",
        "missing_required_cli_flag",
    }
)

UNSAFE_REASON_FIELDS = {
    "runtime_summary_body_detected": {"body_suppressed": False},
    "request_body_present": {"request_body_detected": True},
    "pointer_body_present": {"pointer_body_detected": True},
    "expected_body_present": {"expected_body_detected": True},
    "artifact_body_payload_present": {"artifact_body_payload_detected": True},
    "artifact_body_payload_detected": {"artifact_body_payload_detected": True},
    "manifest_body_present": {"manifest_body_detected": True},
    "manifest_body_detected": {"manifest_body_detected": True},
    "generated_policy_body_present": {"generated_policy_body_detected": True},
    "generated_policy_body_detected": {"generated_policy_body_detected": True},
    "raw_stdout_body_present": {"raw_stdout_body_suppressed": False},
    "raw_stdout_body_detected": {"raw_stdout_body_suppressed": False},
    "raw_stderr_body_present": {"raw_stderr_body_suppressed": False},
    "raw_stderr_body_detected": {"raw_stderr_body_suppressed": False},
    "raw_rows_present": {"raw_rows_detected": True},
    "raw_rows_detected": {"raw_rows_detected": True},
    "logits_present": {"logits_detected": True},
    "logits_detected": {"logits_detected": True},
    "private_path_present": {"private_path_detected": True},
    "private_path_detected": {"private_path_detected": True},
    "absolute_path_present": {"absolute_path_detected": True},
    "absolute_path_detected": {"absolute_path_detected": True},
    "raw_learner_text_present": {"raw_learner_text_detected": True},
    "raw_learner_text_detected": {"raw_learner_text_detected": True},
    "real_data_marker_present": {"real_data_marker_detected": True},
    "real_data_marker_detected": {"real_data_marker_detected": True},
    "performance_metric_body_present": {"performance_metric_body_detected": True},
    "performance_metric_body_detected": {"performance_metric_body_detected": True},
    "file_writing_requested": {
        "file_writing_detected": True,
    },
    "file_writing_detected": {
        "file_writing_detected": True,
        "artifact_file_written": True,
    },
    "manifest_writer_requested": {
        "manifest_writer_invoked": True,
    },
    "manifest_writer_invoked": {
        "manifest_writer_invoked": True,
        "manifest_file_written": True,
    },
}

FORBIDDEN_VALUE_KEYS = frozenset(
    {
        "fixture_json_body",
        "request_body",
        "pointer_body",
        "expected_body",
        "written_file_json_body",
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
        "post_hoc_annotation",
        "scoring_feedback_payload",
    }
)

LOCAL_ABSOLUTE_PATH_PATTERN = re.compile(
    r"(^|[=\s\"'])/(Users|home|private|var|tmp)/|[A-Za-z]:\\|file://|\\Users\\"
)
SAFE_FIXTURE_CASE_PATTERN = re.compile(r"^[A-Za-z0-9_./-]+$")


@dataclass(frozen=True)
class ArtifactBodyGenerationRuntimeIntegrationSummary:
    status: str
    reason_code: str
    exit_code_category: str
    case_id: str
    integration_mode: str
    planned_root: bool = False
    safe_metadata_v0_2_planned_checked: bool = False
    artifact_body_payload_available: bool = False
    artifact_body_payload_emitted: bool = False
    safe_metadata_body_available: bool = False
    safe_metadata_body_field_count: int = 0
    content_suppressed: bool = True
    body_suppressed: bool = True
    summary_only: bool = True
    request_body_detected: bool = False
    pointer_body_detected: bool = False
    expected_body_detected: bool = False
    artifact_body_payload_detected: bool = False
    manifest_body_detected: bool = False
    generated_policy_body_detected: bool = False
    raw_stdout_body_suppressed: bool = True
    raw_stderr_body_suppressed: bool = True
    raw_rows_detected: bool = False
    logits_detected: bool = False
    private_path_detected: bool = False
    absolute_path_detected: bool = False
    raw_learner_text_detected: bool = False
    real_data_marker_detected: bool = False
    performance_metric_body_detected: bool = False
    file_writing_enabled: bool = False
    file_writing_detected: bool = False
    manifest_writer_invoked: bool = False
    artifact_file_written: bool = False
    manifest_file_written: bool = False
    runtime_safety_scan_passed: bool = True
    runtime_fail_closed: bool = False
    production_readiness_claimed: bool = False
    real_data_readiness_claimed: bool = False
    performance_claims_present: bool = False
    runtime_summary_checked: bool = False
    artifact_body_request_checked: bool = False
    artifact_body_pointer_checked: bool = False
    artifact_body_generation_metadata_checked: bool = False
    metadata_file_count: int = 0
    unsafe_signal_count: int = 0
    mode: str = MODE
    runtime_schema_version: str = RUNTIME_SCHEMA_VERSION
    artifact_body_runtime_invoked: bool = False
    artifact_body_runtime_mode: str = "not_invoked"

    @property
    def return_code(self) -> int:
        if self.status == "pass":
            return 0
        if self.status == "usage_error":
            return 2
        return 1

    def to_public_dict(self) -> dict[str, Any]:
        payload = {
            "mode": self.mode,
            "runtime_schema_version": self.runtime_schema_version,
            "status": self.status,
            "reason_code": self.reason_code,
            "exit_code_category": self.exit_code_category,
            "case_id": self.case_id,
            "integration_mode": self.integration_mode,
            "planned_root": self.planned_root,
            "safe_metadata_v0_2_planned_checked": (
                self.safe_metadata_v0_2_planned_checked
            ),
            "artifact_body_runtime_invoked": self.artifact_body_runtime_invoked,
            "artifact_body_runtime_mode": self.artifact_body_runtime_mode,
            "artifact_body_payload_available": self.artifact_body_payload_available,
            "artifact_body_payload_emitted": self.artifact_body_payload_emitted,
            "safe_metadata_body_available": self.safe_metadata_body_available,
            "safe_metadata_body_field_count": self.safe_metadata_body_field_count,
            "content_suppressed": self.content_suppressed,
            "body_suppressed": self.body_suppressed,
            "summary_only": self.summary_only,
            "request_body_detected": self.request_body_detected,
            "pointer_body_detected": self.pointer_body_detected,
            "expected_body_detected": self.expected_body_detected,
            "artifact_body_payload_detected": self.artifact_body_payload_detected,
            "manifest_body_detected": self.manifest_body_detected,
            "generated_policy_body_detected": self.generated_policy_body_detected,
            "raw_stdout_body_suppressed": self.raw_stdout_body_suppressed,
            "raw_stderr_body_suppressed": self.raw_stderr_body_suppressed,
            "raw_rows_detected": self.raw_rows_detected,
            "logits_detected": self.logits_detected,
            "private_path_detected": self.private_path_detected,
            "absolute_path_detected": self.absolute_path_detected,
            "raw_learner_text_detected": self.raw_learner_text_detected,
            "real_data_marker_detected": self.real_data_marker_detected,
            "performance_metric_body_detected": (
                self.performance_metric_body_detected
            ),
            "file_writing_enabled": self.file_writing_enabled,
            "file_writing_detected": self.file_writing_detected,
            "manifest_writer_invoked": self.manifest_writer_invoked,
            "artifact_file_written": self.artifact_file_written,
            "manifest_file_written": self.manifest_file_written,
            "runtime_safety_scan_passed": self.runtime_safety_scan_passed,
            "runtime_fail_closed": self.runtime_fail_closed,
            "production_readiness_claimed": self.production_readiness_claimed,
            "real_data_readiness_claimed": self.real_data_readiness_claimed,
            "performance_claims_present": self.performance_claims_present,
            "runtime_summary_checked": self.runtime_summary_checked,
            "artifact_body_request_checked": self.artifact_body_request_checked,
            "artifact_body_pointer_checked": self.artifact_body_pointer_checked,
            "artifact_body_generation_metadata_checked": (
                self.artifact_body_generation_metadata_checked
            ),
            "metadata_file_count": self.metadata_file_count,
            "unsafe_signal_count": self.unsafe_signal_count,
        }
        return {key: payload[key] for key in SUMMARY_KEYS}


def run_artifact_body_generation_runtime_integration_for_fixture_case(
    fixture_root: str | Path,
    fixture_case: str,
    *,
    mode: str,
    summary_only: bool,
    no_file_writing: bool,
    no_manifest_writer: bool,
    fail_closed_on_unsafe_output: bool,
) -> ArtifactBodyGenerationRuntimeIntegrationSummary:
    safe_case_id = _safe_case_id_for_output(fixture_case)
    if not _is_safe_fixture_case_selector(fixture_case):
        return _safe_error("usage_error", "missing_fixture", case_id=safe_case_id)
    if mode not in {PLAN_ONLY_BRIDGE_MODE, SAFE_METADATA_SMOKE_MODE}:
        return _safe_error(
            "usage_error",
            "unsupported_mode",
            case_id=safe_case_id,
            integration_mode="reserved" if mode in RESERVED_MODES else "unsupported",
        )
    if not (
        summary_only
        and no_file_writing
        and no_manifest_writer
        and fail_closed_on_unsafe_output
    ):
        return _safe_error(
            "usage_error",
            "missing_required_cli_flag",
            case_id=safe_case_id,
            integration_mode=mode,
            runtime_schema_version=_runtime_schema_version_for_mode(mode),
            planned_root=mode == SAFE_METADATA_SMOKE_MODE,
            safe_metadata_v0_2_planned_checked=mode == SAFE_METADATA_SMOKE_MODE,
        )

    case_dir = Path(fixture_root) / fixture_case
    if not case_dir.is_dir():
        return _safe_error(
            "usage_error",
            "missing_fixture",
            case_id=safe_case_id,
            integration_mode=mode,
            runtime_schema_version=_runtime_schema_version_for_mode(mode),
            planned_root=mode == SAFE_METADATA_SMOKE_MODE,
            safe_metadata_v0_2_planned_checked=mode == SAFE_METADATA_SMOKE_MODE,
        )

    missing = [name for name in REQUIRED_FILES if not (case_dir / name).is_file()]
    if missing:
        return _safe_error(
            "usage_error",
            "missing_required_metadata_file",
            case_id=safe_case_id,
            integration_mode=mode,
            runtime_schema_version=_runtime_schema_version_for_mode(mode),
            planned_root=mode == SAFE_METADATA_SMOKE_MODE,
            safe_metadata_v0_2_planned_checked=mode == SAFE_METADATA_SMOKE_MODE,
        )

    try:
        payloads = {
            file_name: _load_json_object(case_dir / file_name)
            for file_name in REQUIRED_FILES
        }
    except (OSError, json.JSONDecodeError, ValueError):
        return _safe_error(
            "usage_error",
            "invalid_json",
            case_id=safe_case_id,
            integration_mode=mode,
            runtime_schema_version=_runtime_schema_version_for_mode(mode),
            planned_root=mode == SAFE_METADATA_SMOKE_MODE,
            safe_metadata_v0_2_planned_checked=mode == SAFE_METADATA_SMOKE_MODE,
        )

    if mode == SAFE_METADATA_SMOKE_MODE:
        return _summarize_safe_metadata_smoke(
            payloads,
            expected_case_id=safe_case_id,
        )

    return _summarize_plan_only_bridge(payloads, expected_case_id=safe_case_id)


def format_public_summary(
    payload: Mapping[str, Any],
) -> str:
    return "\n".join(f"{key}={_format_value(payload[key])}" for key in SUMMARY_KEYS)


def _summarize_plan_only_bridge(
    payloads: Mapping[str, Mapping[str, Any]],
    *,
    expected_case_id: str,
) -> ArtifactBodyGenerationRuntimeIntegrationSummary:
    schema_reason = _schema_reason(payloads)
    if schema_reason != "none":
        return _safe_error(
            "usage_error",
            schema_reason,
            case_id=expected_case_id,
            metadata_file_count=len(payloads),
        )

    identity_reason = _identity_reason(payloads, expected_case_id)
    if identity_reason != "none":
        return _safe_error(
            "fail_closed",
            identity_reason,
            case_id=expected_case_id,
            metadata_file_count=len(payloads),
        )

    unsafe_reason = _first_unsafe_reason(payloads)
    if unsafe_reason != "none":
        return _safe_error(
            "fail_closed",
            unsafe_reason,
            case_id=expected_case_id,
            metadata_file_count=len(payloads),
            unsafe_signal_count=1,
        )

    consistency_reason = _first_consistency_reason(payloads)
    if consistency_reason != "none":
        return _safe_error(
            "fail_closed",
            consistency_reason,
            case_id=expected_case_id,
            metadata_file_count=len(payloads),
        )

    return ArtifactBodyGenerationRuntimeIntegrationSummary(
        status="pass",
        reason_code="none",
        exit_code_category="zero",
        case_id=expected_case_id,
        integration_mode=PLAN_ONLY_BRIDGE_MODE,
        runtime_summary_checked=True,
        artifact_body_request_checked=True,
        artifact_body_pointer_checked=True,
        artifact_body_generation_metadata_checked=True,
        metadata_file_count=len(payloads),
    )


def _summarize_safe_metadata_smoke(
    payloads: Mapping[str, Mapping[str, Any]],
    *,
    expected_case_id: str,
) -> ArtifactBodyGenerationRuntimeIntegrationSummary:
    schema_reason = _safe_metadata_schema_reason(payloads)
    if schema_reason != "none":
        return _safe_error(
            "usage_error",
            schema_reason,
            case_id=expected_case_id,
            integration_mode=SAFE_METADATA_SMOKE_MODE,
            runtime_schema_version=SAFE_METADATA_RUNTIME_SCHEMA_VERSION,
            planned_root=True,
            safe_metadata_v0_2_planned_checked=True,
            metadata_file_count=len(payloads),
        )

    identity_reason = _safe_metadata_identity_reason(payloads, expected_case_id)
    if identity_reason != "none":
        return _safe_error(
            "usage_error",
            identity_reason,
            case_id=expected_case_id,
            integration_mode=SAFE_METADATA_SMOKE_MODE,
            runtime_schema_version=SAFE_METADATA_RUNTIME_SCHEMA_VERSION,
            planned_root=True,
            safe_metadata_v0_2_planned_checked=True,
            metadata_file_count=len(payloads),
        )

    unsafe_reason = _first_safe_metadata_unsafe_reason(payloads)
    if unsafe_reason != "none":
        return _safe_error(
            "fail_closed",
            unsafe_reason,
            case_id=expected_case_id,
            integration_mode=SAFE_METADATA_SMOKE_MODE,
            runtime_schema_version=SAFE_METADATA_RUNTIME_SCHEMA_VERSION,
            planned_root=True,
            safe_metadata_v0_2_planned_checked=True,
            metadata_file_count=len(payloads),
            unsafe_signal_count=_safe_metadata_unsafe_signal_count(payloads),
        )

    mismatch_reason = _safe_metadata_mismatch_reason(payloads)
    if mismatch_reason != "none":
        return _safe_error(
            "mismatch",
            mismatch_reason,
            case_id=expected_case_id,
            integration_mode=SAFE_METADATA_SMOKE_MODE,
            runtime_schema_version=SAFE_METADATA_RUNTIME_SCHEMA_VERSION,
            planned_root=True,
            safe_metadata_v0_2_planned_checked=True,
            metadata_file_count=len(payloads),
        )

    return ArtifactBodyGenerationRuntimeIntegrationSummary(
        status="pass",
        reason_code="none",
        exit_code_category="zero",
        case_id=expected_case_id,
        integration_mode=SAFE_METADATA_SMOKE_MODE,
        planned_root=True,
        safe_metadata_v0_2_planned_checked=True,
        artifact_body_payload_available=False,
        artifact_body_payload_emitted=False,
        safe_metadata_body_available=_safe_metadata_body_available(payloads),
        safe_metadata_body_field_count=_safe_metadata_body_field_count(payloads),
        runtime_schema_version=SAFE_METADATA_RUNTIME_SCHEMA_VERSION,
        runtime_summary_checked=True,
        artifact_body_request_checked=True,
        artifact_body_pointer_checked=True,
        artifact_body_generation_metadata_checked=True,
        metadata_file_count=len(payloads),
    )


def _schema_reason(payloads: Mapping[str, Mapping[str, Any]]) -> str:
    for file_name, expected_schema in EXPECTED_FILE_SCHEMAS.items():
        if payloads[file_name].get("schema_version") != expected_schema:
            return "unsupported_schema"
    runtime = payloads[RUNTIME_SUMMARY_FILE]
    if runtime.get("runtime_schema_version") != RUNTIME_RESULT_SCHEMA_VERSION:
        return "unsupported_schema"
    return "none"


def _safe_metadata_schema_reason(payloads: Mapping[str, Mapping[str, Any]]) -> str:
    for file_name, expected_schema in SAFE_METADATA_EXPECTED_FILE_SCHEMAS.items():
        if payloads[file_name].get("schema_version") != expected_schema:
            return "unsupported_schema"
    for file_name, payload in payloads.items():
        if "fixture_schema_extension_version" in payload and payload.get(
            "fixture_schema_extension_version"
        ) != SAFE_METADATA_PLANNED_MARKER:
            return "unsupported_schema"
        if (
            "fixture_schema_family" in payload
            and payload.get("fixture_schema_family") != SAFE_METADATA_SCHEMA_FAMILY
        ):
            return "unsupported_schema"
        if "runtime_mode" in payload and payload.get("runtime_mode") != SAFE_METADATA_SMOKE_MODE:
            return "unsupported_mode"
        if (
            "runtime_expected_summary_schema_version" in payload
            and payload.get("runtime_expected_summary_schema_version")
            != SAFE_METADATA_RUNTIME_SCHEMA_VERSION
        ):
            return "unsupported_schema"
        if (
            "expected_runtime_schema_version" in payload
            and payload.get("expected_runtime_schema_version")
            != SAFE_METADATA_RUNTIME_SCHEMA_VERSION
        ):
            return "unsupported_schema"
    return "none"


def _safe_metadata_identity_reason(
    payloads: Mapping[str, Mapping[str, Any]],
    expected_case_id: str,
) -> str:
    case_metadata = payloads[CASE_METADATA_FILE]
    pointer = payloads[POINTER_METADATA_FILE]
    expected_summary = payloads[EXPECTED_SUMMARY_FILE]
    if case_metadata.get("case_id") != expected_case_id:
        return "missing_required_runtime_metadata"
    if case_metadata.get("case_kind") not in {"valid", "invalid"}:
        return "missing_required_runtime_metadata"
    if pointer.get("fixture_case_id") != expected_case_id:
        return "missing_required_runtime_metadata"
    if expected_summary.get("expected_case_id") != expected_case_id:
        return "missing_required_runtime_metadata"
    for file_name, payload in payloads.items():
        if "case_id" in payload and payload.get("case_id") != expected_case_id:
            return "missing_required_runtime_metadata"
        for key in ("synthetic_only", "metadata_only", "no_oracle", "body_free"):
            if key in payload and payload.get(key) is not True:
                return "missing_required_runtime_metadata"
    return "none"


def _identity_reason(
    payloads: Mapping[str, Mapping[str, Any]],
    expected_case_id: str,
) -> str:
    case_metadata = payloads[CASE_METADATA_FILE]
    runtime = payloads[RUNTIME_SUMMARY_FILE]
    pointer = payloads[POINTER_METADATA_FILE]
    expected_summary = payloads[EXPECTED_SUMMARY_FILE]
    if case_metadata.get("case_kind") != "valid":
        return "unexpected_case_kind"
    if case_metadata.get("case_id") != expected_case_id:
        return "unexpected_case_kind"
    if runtime.get("case_id") != expected_case_id:
        return "runtime_summary_status"
    if pointer.get("fixture_relative_path") != expected_case_id:
        return "pointer_body_present"
    if expected_summary.get("case_id") != expected_case_id:
        return "unexpected_expected_status"
    return "none"


def _safe_metadata_mismatch_reason(
    payloads: Mapping[str, Mapping[str, Any]],
) -> str:
    case_metadata = payloads[CASE_METADATA_FILE]
    runtime = payloads[RUNTIME_SUMMARY_FILE]
    expected_summary = payloads[EXPECTED_SUMMARY_FILE]
    expected_error = payloads[EXPECTED_ERROR_FILE]

    if expected_summary.get("expected_status_mismatch") is True:
        return "mismatched_expected_status"
    if runtime.get("expected_status_mismatch") is True:
        return "mismatched_expected_status"

    expected_status = case_metadata.get("expected_runtime_status")
    expected_reason = case_metadata.get("expected_runtime_reason_code")
    if expected_status != "pass" or expected_reason != "none":
        return "mismatched_expected_status"

    checks = (
        (runtime, "expected_runtime_status", "pass"),
        (runtime, "expected_runtime_reason_code", "none"),
        (runtime, "status", "pass"),
        (runtime, "reason_code", "none"),
        (runtime, "exit_code_category", "zero"),
        (expected_summary, "expected_runtime_status", "pass"),
        (expected_summary, "expected_runtime_reason_code", "none"),
        (expected_summary, "status", "pass"),
        (expected_summary, "reason_code", "none"),
        (expected_summary, "exit_code_category", "zero"),
        (expected_error, "expected_status", "pass"),
        (expected_error, "expected_reason_code", "none"),
        (expected_error, "expected_exit_code_category", "zero"),
    )
    for mapping, key, expected_value in checks:
        if mapping.get(key) != expected_value:
            return "mismatched_expected_status"
    return "none"


def _first_consistency_reason(payloads: Mapping[str, Mapping[str, Any]]) -> str:
    case_metadata = payloads[CASE_METADATA_FILE]
    runtime = payloads[RUNTIME_SUMMARY_FILE]
    request = payloads[REQUEST_METADATA_FILE]
    pointer = payloads[POINTER_METADATA_FILE]
    generation = payloads[GENERATION_METADATA_FILE]
    expected_summary = payloads[EXPECTED_SUMMARY_FILE]
    expected_error = payloads[EXPECTED_ERROR_FILE]

    if (
        case_metadata.get("expected_status") != "pass"
        or case_metadata.get("expected_reason_code") != "none"
        or expected_summary.get("status") != "pass"
        or expected_summary.get("reason_code") != "none"
        or expected_error.get("expected_status") != "pass"
        or expected_error.get("expected_reason_code") != "none"
        or expected_error.get("expected_exit_code_category") != "zero"
    ):
        return "unexpected_expected_status"

    if (
        runtime.get("status") != "pass"
        or runtime.get("reason_code") != "none"
        or runtime.get("exit_code_category") != "zero"
        or runtime.get("invocation_mode") != "actual_invocation_metadata_only"
        or runtime.get("summary_mode") != "summary_only_public_safe"
    ):
        return "runtime_summary_status"

    for key in ("content_suppressed", "body_suppressed"):
        if runtime.get(key) is not True or generation.get(key) is not True:
            return "runtime_summary_body_detected"
    for key in (
        "runtime_actual_invocation_enabled",
        "artifact_writer_cli_invoked",
        "artifact_writer_cli_output_scanned",
        "artifact_writer_cli_output_body_free",
        "raw_stdout_body_suppressed",
        "raw_stderr_body_suppressed",
    ):
        if runtime.get(key) is not True:
            return "runtime_summary_status"

    for key in ("synthetic_only", "metadata_only", "no_oracle"):
        if (
            case_metadata.get(key) is not True
            or request.get(key) is not True
            or pointer.get(key) is not True
        ):
            return "unexpected_case_kind"
    if case_metadata.get("body_free") is not True:
        return "unexpected_case_kind"

    for key in (
        "summary_only",
        "no_file_writing",
        "no_manifest_writer",
        "no_payload_output",
    ):
        if request.get(key) is not True:
            if key == "no_file_writing":
                return "file_writing_detected"
            if key == "no_manifest_writer":
                return "manifest_writer_invoked"
            if key == "no_payload_output":
                return "artifact_body_payload_detected"
            return "unsafe_output_residue_risk"

    generation_mode = generation.get("generation_mode")
    if generation_mode not in {"suppressed", "safe-metadata"}:
        return "artifact_body_payload_detected"
    if request.get("mode") != generation_mode:
        return "unexpected_expected_status"
    if generation.get("body_status") not in {
        "suppressed_metadata_only",
        "generated_safe_metadata_body",
    }:
        return "artifact_body_payload_detected"
    if generation.get("validation_status") != "pass":
        return "runtime_summary_status"
    if generation.get("safe_summary") != "metadata_only_counts":
        return "unsafe_output_residue_risk"
    if generation.get("artifact_body_available") is not (
        generation_mode == "safe-metadata"
    ):
        return "artifact_body_payload_detected"

    if expected_summary.get("mode") != (
        "artifact_body_generation_integration_fixture_validation"
    ):
        return "unexpected_expected_status"
    if expected_summary.get("integration_mode") != (
        "actual_invocation_runtime_to_artifact_body_generation_metadata_bridge"
    ):
        return "unexpected_expected_status"
    if expected_error.get("expected_error_public_safe") is not False:
        return "expected_body_present"
    if expected_error.get("body_suppressed") is not True:
        return "expected_body_present"
    if expected_error.get("content_suppressed") is not True:
        return "expected_body_present"
    if expected_error.get("no_payload_in_error") is not True:
        return "expected_body_present"

    return "none"


def _first_safe_metadata_unsafe_reason(
    payloads: Mapping[str, Mapping[str, Any]]
) -> str:
    recursive_reason = _normalize_safe_metadata_reason(
        _recursive_unsafe_reason(payloads)
    )
    if recursive_reason != "none":
        return recursive_reason

    checks: tuple[tuple[str, str, str], ...] = (
        ("request_body_present", "request_body_present", "request_body_present"),
        ("pointer_body_present", "pointer_body_present", "pointer_body_present"),
        ("expected_body_present", "expected_body_present", "expected_body_present"),
        ("artifact_body_payload_present", "artifact_body_payload_present", "artifact_body_payload_present"),
        ("artifact_body_payload_requested", "artifact_body_payload_requested", "artifact_body_payload_present"),
        ("manifest_body_present", "manifest_body_present", "manifest_body_present"),
        ("manifest_body_requested", "manifest_body_requested", "manifest_body_present"),
        ("generated_policy_body_present", "generated_policy_body_present", "generated_policy_body_present"),
        ("generated_policy_body_requested", "generated_policy_body_requested", "generated_policy_body_present"),
        ("raw_stdout_body_present", "raw_stdout_body_present", "raw_stdout_body_present"),
        ("raw_stderr_body_present", "raw_stderr_body_present", "raw_stderr_body_present"),
        ("raw_rows_present", "raw_rows_present", "raw_rows_present"),
        ("logits_present", "logits_present", "logits_present"),
        ("private_path_present", "private_path_present", "private_path_present"),
        ("absolute_path_present", "absolute_path_present", "absolute_path_present"),
        ("raw_learner_text_present", "raw_learner_text_present", "raw_learner_text_present"),
        ("real_data_marker_present", "real_data_marker_present", "real_data_marker_present"),
        ("performance_metric_body_present", "performance_metric_body_present", "performance_metric_body_present"),
        ("file_writing_requested", "file_writing_requested", "file_writing_requested"),
        ("file_writing_detected", "file_writing_detected", "file_writing_requested"),
        ("artifact_file_written", "artifact_file_written", "file_writing_requested"),
        ("manifest_writer_requested", "manifest_writer_requested", "manifest_writer_requested"),
        ("manifest_writer_invoked", "manifest_writer_invoked", "manifest_writer_requested"),
        ("manifest_file_written", "manifest_file_written", "manifest_writer_requested"),
        ("unsupported_safe_metadata_output_surface", "unsupported_safe_metadata_output_surface", "unsafe_output_surface"),
        ("production_readiness_claimed", "production_readiness_claimed", "unsafe_output_surface"),
        ("real_data_readiness_claimed", "real_data_readiness_claimed", "real_data_marker_present"),
        ("performance_claims_present", "performance_claims_present", "performance_metric_body_present"),
    )
    for _, key, reason in checks:
        for payload in payloads.values():
            if payload.get(key) is True:
                return reason

    for payload in payloads.values():
        if payload.get("content_suppressed") is False:
            return "unsafe_output_surface"
        if payload.get("body_suppressed") is False:
            return "unsafe_output_surface"
        if payload.get("body_payload_suppressed") is False:
            return "artifact_body_payload_present"
        if payload.get("safe_metadata_body_payload_suppressed") is False:
            return "artifact_body_payload_present"
        if payload.get("no_file_writing") is False:
            return "file_writing_requested"
        if payload.get("no_manifest_writer") is False:
            return "manifest_writer_requested"
        if payload.get("no_payload_output") is False:
            return "artifact_body_payload_present"
    return "none"


def _first_unsafe_reason(payloads: Mapping[str, Mapping[str, Any]]) -> str:
    recursive_reason = _recursive_unsafe_reason(payloads)
    if recursive_reason != "none":
        return recursive_reason

    runtime = payloads[RUNTIME_SUMMARY_FILE]
    request = payloads[REQUEST_METADATA_FILE]
    pointer = payloads[POINTER_METADATA_FILE]
    generation = payloads[GENERATION_METADATA_FILE]
    expected_summary = payloads[EXPECTED_SUMMARY_FILE]

    checks: tuple[tuple[Mapping[str, Any], str, str], ...] = (
        (runtime, "request_body_detected", "request_body_present"),
        (runtime, "pointer_body_detected", "pointer_body_present"),
        (runtime, "expected_body_detected", "expected_body_present"),
        (runtime, "artifact_body_payload_detected", "artifact_body_payload_detected"),
        (runtime, "manifest_body_detected", "manifest_body_detected"),
        (runtime, "generated_policy_body_detected", "generated_policy_body_detected"),
        (runtime, "file_writing_detected", "file_writing_detected"),
        (runtime, "manifest_writer_invoked", "manifest_writer_invoked"),
        (runtime, "production_readiness_claimed", "unsafe_output_residue_risk"),
        (runtime, "real_data_readiness_claimed", "real_data_marker_detected"),
        (runtime, "performance_claims_present", "performance_metric_body_detected"),
        (request, "request_body_present", "request_body_present"),
        (request, "artifact_body_payload_requested", "artifact_body_payload_detected"),
        (request, "manifest_body_requested", "manifest_body_detected"),
        (request, "generated_policy_body_requested", "generated_policy_body_detected"),
        (request, "performance_metric_body_present", "performance_metric_body_detected"),
        (request, "real_data_marker_present", "real_data_marker_detected"),
        (pointer, "pointer_body_present", "pointer_body_present"),
        (pointer, "private_path_present", "private_path_detected"),
        (pointer, "absolute_path_present", "absolute_path_detected"),
        (pointer, "raw_learner_text_present", "raw_learner_text_detected"),
        (pointer, "raw_rows_present", "raw_rows_detected"),
        (pointer, "logits_present", "logits_detected"),
        (pointer, "real_data_marker_present", "real_data_marker_detected"),
        (generation, "artifact_body_payload_present", "artifact_body_payload_detected"),
        (generation, "manifest_body_present", "manifest_body_detected"),
        (generation, "generated_policy_body_present", "generated_policy_body_detected"),
        (generation, "raw_stdout_body_present", "raw_stdout_body_detected"),
        (generation, "raw_stderr_body_present", "raw_stderr_body_detected"),
        (generation, "request_body_present", "request_body_present"),
        (generation, "pointer_body_present", "pointer_body_present"),
        (generation, "expected_body_present", "expected_body_present"),
        (generation, "raw_rows_present", "raw_rows_detected"),
        (generation, "logits_present", "logits_detected"),
        (generation, "private_path_present", "private_path_detected"),
        (generation, "absolute_path_present", "absolute_path_detected"),
        (generation, "raw_learner_text_present", "raw_learner_text_detected"),
        (generation, "real_data_marker_present", "real_data_marker_detected"),
        (generation, "performance_metric_body_present", "performance_metric_body_detected"),
        (generation, "artifact_file_written", "file_writing_detected"),
        (generation, "manifest_file_written", "manifest_writer_invoked"),
        (expected_summary, "artifact_body_payload_detected", "artifact_body_payload_detected"),
        (expected_summary, "manifest_body_detected", "manifest_body_detected"),
        (expected_summary, "generated_policy_body_detected", "generated_policy_body_detected"),
        (expected_summary, "request_body_detected", "request_body_present"),
        (expected_summary, "pointer_body_detected", "pointer_body_present"),
        (expected_summary, "expected_body_detected", "expected_body_present"),
        (expected_summary, "raw_stdout_body_detected", "raw_stdout_body_detected"),
        (expected_summary, "raw_stderr_body_detected", "raw_stderr_body_detected"),
        (expected_summary, "file_writing_detected", "file_writing_detected"),
        (expected_summary, "manifest_writer_invoked", "manifest_writer_invoked"),
        (expected_summary, "production_readiness_claimed", "unsafe_output_residue_risk"),
        (expected_summary, "real_data_readiness_claimed", "real_data_marker_detected"),
        (expected_summary, "performance_claims_present", "performance_metric_body_detected"),
    )
    for mapping, key, reason in checks:
        if mapping.get(key) is True:
            return reason

    if runtime.get("content_suppressed") is False or runtime.get("body_suppressed") is False:
        return "runtime_summary_body_detected"
    if runtime.get("raw_stdout_body_suppressed") is False:
        return "raw_stdout_body_detected"
    if runtime.get("raw_stderr_body_suppressed") is False:
        return "raw_stderr_body_detected"
    if request.get("no_file_writing") is False:
        return "file_writing_detected"
    if request.get("no_manifest_writer") is False:
        return "manifest_writer_invoked"
    if request.get("no_payload_output") is False:
        return "artifact_body_payload_detected"
    if request.get("summary_only") is False:
        return "unsafe_output_residue_risk"
    if generation.get("generation_mode") == "unsafe_body_output_requested":
        return "artifact_body_payload_detected"
    return "none"


def _safe_metadata_body_available(
    payloads: Mapping[str, Mapping[str, Any]]
) -> bool:
    return any(payload.get("safe_metadata_body_available") is True for payload in payloads.values())


def _safe_metadata_body_field_count(
    payloads: Mapping[str, Mapping[str, Any]]
) -> int:
    counts = [
        payload.get("safe_metadata_body_field_count")
        for payload in payloads.values()
        if isinstance(payload.get("safe_metadata_body_field_count"), int)
    ]
    return max(counts) if counts else 0


def _safe_metadata_unsafe_signal_count(
    payloads: Mapping[str, Mapping[str, Any]]
) -> int:
    counts = [
        payload.get("unsafe_signal_count")
        for payload in payloads.values()
        if isinstance(payload.get("unsafe_signal_count"), int)
    ]
    return max([1, *counts])


def _normalize_safe_metadata_reason(reason: str) -> str:
    aliases = {
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
    return aliases.get(reason, reason)


def _recursive_unsafe_reason(value: Any, *, key: str | None = None) -> str:
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            if child_key_text in FORBIDDEN_VALUE_KEYS:
                return _reason_for_forbidden_key(child_key_text)
            reason = _recursive_unsafe_reason(child_value, key=child_key_text)
            if reason != "none":
                return reason
    elif isinstance(value, list):
        for child_value in value:
            reason = _recursive_unsafe_reason(child_value, key=key)
            if reason != "none":
                return reason
    elif isinstance(value, str):
        if LOCAL_ABSOLUTE_PATH_PATTERN.search(value):
            return "absolute_path_detected"
        lowered = value.lower()
        if any(
            marker in lowered
            for marker in (
                "actions-log-unsafe-marker",
                "job-output-unsafe-marker",
                "copied-log-block-unsafe-marker",
                "participant-data-unsafe-marker",
            )
        ):
            return "unsafe_output_residue_risk"
        if "learner-text-unsafe-marker" in lowered:
            return "raw_learner_text_detected"
    return "none"


def _reason_for_forbidden_key(key: str) -> str:
    if key in {"request_body"}:
        return "request_body_present"
    if key in {"pointer_body"}:
        return "pointer_body_present"
    if key in {"expected_body"}:
        return "expected_body_present"
    if key in {"artifact_body_payload"}:
        return "artifact_body_payload_detected"
    if key in {"manifest_body"}:
        return "manifest_body_detected"
    if key in {"generated_policy_body"}:
        return "generated_policy_body_detected"
    if key in {"raw_stdout_body"}:
        return "raw_stdout_body_detected"
    if key in {"raw_stderr_body"}:
        return "raw_stderr_body_detected"
    if key in {"raw_rows"}:
        return "raw_rows_detected"
    if key in {"logits", "probabilities"}:
        return "logits_detected"
    if key in {"private_path"}:
        return "private_path_detected"
    if key in {"absolute_path"}:
        return "absolute_path_detected"
    if key in {"raw_learner_text"}:
        return "raw_learner_text_detected"
    if key in {"real_participant_data"}:
        return "real_data_marker_detected"
    if key in {"performance_metric_body"}:
        return "performance_metric_body_detected"
    return "unsafe_output_residue_risk"


def _safe_error(
    status: str,
    reason_code: str,
    *,
    case_id: str = "not_available",
    integration_mode: str = PLAN_ONLY_BRIDGE_MODE,
    runtime_schema_version: str = RUNTIME_SCHEMA_VERSION,
    planned_root: bool = False,
    safe_metadata_v0_2_planned_checked: bool = False,
    metadata_file_count: int = 0,
    unsafe_signal_count: int = 0,
) -> ArtifactBodyGenerationRuntimeIntegrationSummary:
    exit_code_category = "zero" if status == "pass" else status
    kwargs: dict[str, Any] = {}
    if status == "fail_closed":
        kwargs.update(
            {
                "runtime_safety_scan_passed": False,
                "runtime_fail_closed": True,
                "unsafe_signal_count": max(1, unsafe_signal_count),
            }
        )
        kwargs.update(UNSAFE_REASON_FIELDS.get(reason_code, {}))
    else:
        kwargs.update(
            {
                "runtime_safety_scan_passed": False,
                "unsafe_signal_count": unsafe_signal_count,
            }
        )
    return ArtifactBodyGenerationRuntimeIntegrationSummary(
        status=status,
        reason_code=reason_code,
        exit_code_category=exit_code_category,
        case_id=case_id,
        integration_mode=integration_mode,
        runtime_schema_version=runtime_schema_version,
        planned_root=planned_root,
        safe_metadata_v0_2_planned_checked=safe_metadata_v0_2_planned_checked,
        metadata_file_count=metadata_file_count,
        runtime_summary_checked=metadata_file_count == len(REQUIRED_FILES),
        artifact_body_request_checked=metadata_file_count == len(REQUIRED_FILES),
        artifact_body_pointer_checked=metadata_file_count == len(REQUIRED_FILES),
        artifact_body_generation_metadata_checked=metadata_file_count
        == len(REQUIRED_FILES),
        **kwargs,
    )


def _load_json_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("metadata file must contain a JSON object")
    return data


def _is_safe_fixture_case_selector(fixture_case: str) -> bool:
    return (
        bool(SAFE_FIXTURE_CASE_PATTERN.fullmatch(fixture_case))
        and not fixture_case.startswith("/")
        and ".." not in Path(fixture_case).parts
    )


def _safe_case_id_for_output(fixture_case: str) -> str:
    if _is_safe_fixture_case_selector(fixture_case):
        return fixture_case
    return "unsafe_case_selector"


def _runtime_schema_version_for_mode(mode: str) -> str:
    if mode == SAFE_METADATA_SMOKE_MODE:
        return SAFE_METADATA_RUNTIME_SCHEMA_VERSION
    return RUNTIME_SCHEMA_VERSION


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run a public-safe plan-only artifact body generation runtime "
            "integration boundary over one synthetic metadata fixture case."
        )
    )
    parser.add_argument("--fixture-root", required=True)
    parser.add_argument("--fixture-case", required=True)
    parser.add_argument("--mode", required=True)
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--no-file-writing", action="store_true")
    parser.add_argument("--no-manifest-writer", action="store_true")
    parser.add_argument("--fail-closed-on-unsafe-output", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    summary = run_artifact_body_generation_runtime_integration_for_fixture_case(
        args.fixture_root,
        args.fixture_case,
        mode=args.mode,
        summary_only=args.summary_only,
        no_file_writing=args.no_file_writing,
        no_manifest_writer=args.no_manifest_writer,
        fail_closed_on_unsafe_output=args.fail_closed_on_unsafe_output,
    )
    print(format_public_summary(summary.to_public_dict()))
    return summary.return_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
