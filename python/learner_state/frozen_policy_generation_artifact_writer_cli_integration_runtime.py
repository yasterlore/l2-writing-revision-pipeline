"""Metadata-only artifact writer CLI integration runtime boundary.

This module builds a safe runtime summary from synthetic metadata-only
artifact writer CLI integration runtime fixtures. It does not call artifact
body generation, call the manifest writer, generate policy bodies, write
files, train models, or compute metrics.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation import (
    ARTIFACT_WRITER_CLI_METADATA_FILE,
    ARTIFACT_WRITER_CLI_METADATA_SCHEMA_VERSION,
    ARTIFACT_WRITER_CLI_METADATA_SCHEMA_VERSION_V0_2,
    CASE_METADATA_FILE,
    CASE_METADATA_SCHEMA_VERSION_V0_2,
    DEFAULT_FIXTURE_ROOT,
    EXPECTED_ERROR_FILE,
    EXPECTED_ERROR_SCHEMA_VERSION_V0_2,
    EXPECTED_RUNTIME_SUMMARY_FILE,
    EXPECTED_RUNTIME_SUMMARY_SCHEMA_VERSION_V0_2,
    POINTER_METADATA_FILE,
    POINTER_METADATA_SCHEMA_VERSION,
    POINTER_METADATA_SCHEMA_VERSION_V0_2,
    REQUEST_METADATA_FILE,
    REQUEST_METADATA_SCHEMA_VERSION,
    REQUEST_METADATA_SCHEMA_VERSION_V0_2,
)

MODE = "artifact_writer_cli_integration_runtime"
RUNTIME_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_"
    "runtime_v0.1"
)
RUNTIME_SCHEMA_VERSION_V0_2 = (
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_"
    "runtime_v0.2"
)
DEFAULT_FIXTURE_CASE = "valid/valid_minimal_metadata_runtime_pass"
DEFAULT_ARTIFACT_WRITER_CLI_MODULE = (
    "learner_state.frozen_policy_generation_artifact_writer"
)
DEFAULT_TIMEOUT_SECONDS = 30
ACTUAL_INVOCATION_MODE = "actual_invocation_metadata_only"
PLAN_ONLY_MODE = "plan_only"

USAGE_ERROR_REASONS = frozenset(
    {
        "ambiguous_file_writing_target",
        "duplicate_case_id",
        "mismatched_expected_status",
        "missing_required_metadata_file",
        "unsupported_schema_version",
        "case_id_mismatch",
        "malformed_json_metadata",
        "missing_cli_argument",
        "actual_invocation_flag_required",
        "conflicting_runtime_mode_flags",
        "invalid_timeout_seconds",
        "unsafe_fixture_case_selector",
        "fixture_case_missing",
    }
)

REQUEST_SENTINEL_FIELDS = (
    "request_body_present",
    "expected_body_present",
    "artifact_body_payload_present",
    "manifest_body_present",
    "generated_policy_body_present",
    "final_text_present",
    "observed_after_text_present",
    "gold_label_present",
    "post_hoc_annotation_present",
)
POINTER_SENTINEL_FIELDS = (
    "pointer_body_present",
    "raw_learner_text_present",
    "raw_rows_present",
    "logits_present",
    "probabilities_present",
    "private_path_present",
    "absolute_path_present",
)
CLI_SENTINEL_FIELDS = (
    "artifact_body_generation_requested",
    "manifest_writer_requested",
    "ambiguous_file_writing_target",
)

FORBIDDEN_ACTUAL_KEYS = frozenset(
    {
        "request_body",
        "pointer_body",
        "expected_body",
        "written_file_json_body",
        "manifest_body",
        "artifact_body_payload",
        "generated_policy_body",
        "raw_rows",
        "logits",
        "probabilities",
        "private_path",
        "absolute_path",
        "raw_learner_text",
        "real_participant_data",
        "performance_metric_body",
    }
)

ACTUAL_INVOCATION_SENTINEL_REASON_FIELDS = (
    ("request_body_present", "request_body_present"),
    ("expected_body_present", "expected_body_present"),
    ("artifact_body_payload_present", "artifact_body_payload_present"),
    ("manifest_body_present", "manifest_body_present"),
    ("generated_policy_body_present", "generated_policy_body_present"),
    ("final_text_present", "final_text_present"),
    ("observed_after_text_present", "observed_after_text_present"),
    ("gold_label_present", "gold_label_present"),
    ("post_hoc_annotation_present", "post_hoc_annotation_present"),
    ("pointer_body_present", "pointer_body_present"),
    ("raw_learner_text_present", "raw_learner_text_present"),
    ("raw_rows_present", "raw_rows_present"),
    ("logits_present", "logits_present"),
    ("probabilities_present", "probabilities_present"),
    ("private_path_present", "private_path_present"),
    ("absolute_path_present", "absolute_path_present"),
)

ACTUAL_INVOCATION_ARTIFACT_SENTINEL_REASON_FIELDS = (
    ("raw_stdout_body_detected", "raw_stdout_body_present"),
    ("raw_stderr_body_detected", "raw_stderr_body_present"),
    ("unsupported_schema_present", "unsupported_schema_version"),
)

ACTUAL_INVOCATION_EXPECTED_SENTINEL_REASON_FIELDS = (
    ("artifact_body_generation_invoked", "artifact_body_generation_invoked"),
    ("manifest_writer_invoked", "manifest_writer_invoked"),
    ("file_writing_detected", "file_writing_detected"),
    ("request_body_detected", "request_body_present"),
    ("pointer_body_detected", "pointer_body_present"),
    ("expected_body_detected", "expected_body_present"),
    ("artifact_body_payload_detected", "artifact_body_payload_present"),
    ("manifest_body_detected", "manifest_body_present"),
    ("generated_policy_body_detected", "generated_policy_body_present"),
)


@dataclass(frozen=True)
class ArtifactWriterCliIntegrationRuntimeSummary:
    status: str
    reason_code: str
    exit_code_category: str
    case_id: str | None
    command_label: str | None
    summary_mode: str
    mismatch_reasons: tuple[str, ...] = ()
    mode: str = MODE
    runtime_schema_version: str = RUNTIME_SCHEMA_VERSION
    content_suppressed: bool = True
    body_suppressed: bool = True
    no_raw_rows: bool = True
    no_logits_dump: bool = True
    no_private_paths: bool = True
    no_absolute_paths: bool = True
    no_generated_policy_body: bool = True
    no_artifact_body_payload: bool = True
    no_manifest_body: bool = True
    no_request_body: bool = True
    no_pointer_body: bool = True
    no_expected_body: bool = True
    no_oracle_checked: bool = True
    synthetic_only_checked: bool = True
    metadata_only_checked: bool = True
    file_writing_enabled: bool = False
    residue_expected: bool = False
    runtime_executed: bool = True
    runtime_actual_invocation_enabled: bool = False
    invocation_mode: str = PLAN_ONLY_MODE
    artifact_writer_cli_invoked: bool = False
    artifact_writer_cli_invocation_planned: bool = True
    artifact_writer_cli_exit_code_category: str | None = None
    artifact_writer_cli_output_scanned: bool = False
    artifact_writer_cli_output_body_free: bool = True
    raw_stdout_body_suppressed: bool = True
    raw_stderr_body_suppressed: bool = True
    no_raw_stdout_body: bool = True
    no_raw_stderr_body: bool = True
    artifact_body_payload_detected: bool = False
    manifest_body_detected: bool = False
    generated_policy_body_detected: bool = False
    request_body_detected: bool = False
    pointer_body_detected: bool = False
    expected_body_detected: bool = False
    file_writing_detected: bool = False
    runtime_actual_invocation_safety_scan_passed: bool = True
    runtime_actual_invocation_fail_closed: bool = False
    artifact_body_generation_invoked: bool = False
    manifest_writer_invoked: bool = False
    production_readiness_claimed: bool = False
    real_data_readiness_claimed: bool = False
    performance_claims_present: bool = False

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
            "command_label": self.command_label,
            "summary_mode": self.summary_mode,
            "content_suppressed": self.content_suppressed,
            "body_suppressed": self.body_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "no_logits_dump": self.no_logits_dump,
            "no_private_paths": self.no_private_paths,
            "no_absolute_paths": self.no_absolute_paths,
            "no_generated_policy_body": self.no_generated_policy_body,
            "no_artifact_body_payload": self.no_artifact_body_payload,
            "no_manifest_body": self.no_manifest_body,
            "no_request_body": self.no_request_body,
            "no_pointer_body": self.no_pointer_body,
            "no_expected_body": self.no_expected_body,
            "no_oracle_checked": self.no_oracle_checked,
            "synthetic_only_checked": self.synthetic_only_checked,
            "metadata_only_checked": self.metadata_only_checked,
            "file_writing_enabled": self.file_writing_enabled,
            "residue_expected": self.residue_expected,
            "runtime_executed": self.runtime_executed,
            "artifact_writer_cli_invoked": self.artifact_writer_cli_invoked,
            "artifact_writer_cli_invocation_planned": (
                self.artifact_writer_cli_invocation_planned
            ),
            "artifact_body_generation_invoked": (
                self.artifact_body_generation_invoked
            ),
            "manifest_writer_invoked": self.manifest_writer_invoked,
            "production_readiness_claimed": self.production_readiness_claimed,
            "real_data_readiness_claimed": self.real_data_readiness_claimed,
            "performance_claims_present": self.performance_claims_present,
            "mismatch_reasons": list(self.mismatch_reasons),
        }
        if self.runtime_schema_version == RUNTIME_SCHEMA_VERSION_V0_2:
            payload.update(
                {
                    "runtime_actual_invocation_enabled": (
                        self.runtime_actual_invocation_enabled
                    ),
                    "invocation_mode": self.invocation_mode,
                    "artifact_writer_cli_exit_code_category": (
                        self.artifact_writer_cli_exit_code_category
                        or self.exit_code_category
                    ),
                    "artifact_writer_cli_output_scanned": (
                        self.artifact_writer_cli_output_scanned
                    ),
                    "artifact_writer_cli_output_body_free": (
                        self.artifact_writer_cli_output_body_free
                    ),
                    "raw_stdout_body_suppressed": (
                        self.raw_stdout_body_suppressed
                    ),
                    "raw_stderr_body_suppressed": (
                        self.raw_stderr_body_suppressed
                    ),
                    "no_raw_stdout_body": self.no_raw_stdout_body,
                    "no_raw_stderr_body": self.no_raw_stderr_body,
                    "artifact_body_payload_detected": (
                        self.artifact_body_payload_detected
                    ),
                    "manifest_body_detected": self.manifest_body_detected,
                    "generated_policy_body_detected": (
                        self.generated_policy_body_detected
                    ),
                    "request_body_detected": self.request_body_detected,
                    "pointer_body_detected": self.pointer_body_detected,
                    "expected_body_detected": self.expected_body_detected,
                    "file_writing_detected": self.file_writing_detected,
                    "runtime_actual_invocation_safety_scan_passed": (
                        self.runtime_actual_invocation_safety_scan_passed
                    ),
                    "runtime_actual_invocation_fail_closed": (
                        self.runtime_actual_invocation_fail_closed
                    ),
                }
            )
        return payload


@dataclass(frozen=True)
class ArtifactWriterCliIntegrationRuntimeInputs:
    request_metadata_path: Path
    pointer_metadata_path: Path
    artifact_writer_cli_metadata_path: Path
    case_metadata_path: Path | None = None
    expected_runtime_summary_path: Path | None = None
    expected_error_path: Path | None = None
    case_id: str | None = None


@dataclass(frozen=True)
class ArtifactWriterCliBoundaryResult:
    exit_code_category: str
    output_scanned: bool
    output_body_free: bool
    raw_stdout_body_suppressed: bool = True
    raw_stderr_body_suppressed: bool = True
    reason_code: str = "none"


def run_artifact_writer_cli_integration_runtime_for_fixture_case(
    fixture_root: str | Path = DEFAULT_FIXTURE_ROOT,
    fixture_case: str = DEFAULT_FIXTURE_CASE,
    *,
    actual_invocation: bool = False,
    artifact_writer_cli_module: str = DEFAULT_ARTIFACT_WRITER_CLI_MODULE,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    summary_only: bool = True,
    no_file_writing: bool = True,
    fail_closed_on_unsafe_output: bool = True,
) -> ArtifactWriterCliIntegrationRuntimeSummary:
    if _unsafe_fixture_case_selector(fixture_case):
        return _safe_error("usage_error", "unsafe_fixture_case_selector")

    case_dir = Path(fixture_root) / fixture_case
    if not case_dir.is_dir():
        return _safe_error("usage_error", "fixture_case_missing", case_id=fixture_case)

    return run_artifact_writer_cli_integration_runtime(
        request_metadata_path=case_dir / REQUEST_METADATA_FILE,
        pointer_metadata_path=case_dir / POINTER_METADATA_FILE,
        artifact_writer_cli_metadata_path=case_dir
        / ARTIFACT_WRITER_CLI_METADATA_FILE,
        case_metadata_path=case_dir / CASE_METADATA_FILE,
        expected_runtime_summary_path=case_dir / EXPECTED_RUNTIME_SUMMARY_FILE,
        expected_error_path=case_dir / EXPECTED_ERROR_FILE,
        actual_invocation=actual_invocation,
        artifact_writer_cli_module=artifact_writer_cli_module,
        timeout_seconds=timeout_seconds,
        summary_only=summary_only,
        no_file_writing=no_file_writing,
        fail_closed_on_unsafe_output=fail_closed_on_unsafe_output,
    )


def run_artifact_writer_cli_integration_runtime(
    *,
    request_metadata_path: str | Path,
    pointer_metadata_path: str | Path,
    artifact_writer_cli_metadata_path: str | Path,
    case_metadata_path: str | Path | None = None,
    expected_runtime_summary_path: str | Path | None = None,
    expected_error_path: str | Path | None = None,
    actual_invocation: bool = False,
    artifact_writer_cli_module: str = DEFAULT_ARTIFACT_WRITER_CLI_MODULE,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    summary_only: bool = True,
    no_file_writing: bool = True,
    fail_closed_on_unsafe_output: bool = True,
) -> ArtifactWriterCliIntegrationRuntimeSummary:
    inputs = ArtifactWriterCliIntegrationRuntimeInputs(
        request_metadata_path=Path(request_metadata_path),
        pointer_metadata_path=Path(pointer_metadata_path),
        artifact_writer_cli_metadata_path=Path(artifact_writer_cli_metadata_path),
        case_metadata_path=Path(case_metadata_path) if case_metadata_path else None,
        expected_runtime_summary_path=(
            Path(expected_runtime_summary_path)
            if expected_runtime_summary_path
            else None
        ),
        expected_error_path=Path(expected_error_path) if expected_error_path else None,
    )
    required_paths: list[Path | None] = [
        inputs.request_metadata_path,
        inputs.pointer_metadata_path,
        inputs.artifact_writer_cli_metadata_path,
    ]
    if actual_invocation:
        required_paths.extend(
            [
                inputs.case_metadata_path,
                inputs.expected_runtime_summary_path,
                inputs.expected_error_path,
            ]
        )
    missing = [path for path in required_paths if path is None or not path.is_file()]
    if missing:
        return _safe_error("usage_error", "missing_required_metadata_file")

    try:
        request_metadata = _load_json_object(inputs.request_metadata_path)
        pointer_metadata = _load_json_object(inputs.pointer_metadata_path)
        artifact_writer_cli_metadata = _load_json_object(
            inputs.artifact_writer_cli_metadata_path
        )
        case_metadata = (
            _load_json_object(inputs.case_metadata_path)
            if actual_invocation and inputs.case_metadata_path
            else None
        )
        expected_runtime_summary = (
            _load_json_object(inputs.expected_runtime_summary_path)
            if actual_invocation and inputs.expected_runtime_summary_path
            else None
        )
        expected_error = (
            _load_json_object(inputs.expected_error_path)
            if actual_invocation and inputs.expected_error_path
            else None
        )
    except (OSError, json.JSONDecodeError, ValueError):
        return _safe_error("usage_error", "malformed_json_metadata")

    if actual_invocation:
        if (
            case_metadata is None
            or expected_runtime_summary is None
            or expected_error is None
        ):
            return _safe_error("usage_error", "missing_required_metadata_file")
        return _summarize_actual_invocation_metadata(
            request_metadata,
            pointer_metadata,
            artifact_writer_cli_metadata,
            case_metadata,
            expected_runtime_summary,
            expected_error,
            artifact_writer_cli_module=artifact_writer_cli_module,
            timeout_seconds=timeout_seconds,
            summary_only=summary_only,
            no_file_writing=no_file_writing,
            fail_closed_on_unsafe_output=fail_closed_on_unsafe_output,
        )

    if _is_actual_invocation_fixture(request_metadata):
        return _safe_error("usage_error", "actual_invocation_flag_required")

    return _summarize_metadata(
        request_metadata,
        pointer_metadata,
        artifact_writer_cli_metadata,
    )


def _summarize_metadata(
    request_metadata: Mapping[str, Any],
    pointer_metadata: Mapping[str, Any],
    artifact_writer_cli_metadata: Mapping[str, Any],
) -> ArtifactWriterCliIntegrationRuntimeSummary:
    case_id = _common_case_id(
        request_metadata,
        pointer_metadata,
        artifact_writer_cli_metadata,
    )
    command_label = _safe_string(
        artifact_writer_cli_metadata.get("command_label")
    )
    summary_mode = _safe_string(
        artifact_writer_cli_metadata.get("summary_mode")
    ) or "public_safe_count_only"
    mismatch_reasons: list[str] = []

    _detect_forbidden_actual_keys(
        (request_metadata, pointer_metadata, artifact_writer_cli_metadata),
        mismatch_reasons,
    )
    if mismatch_reasons:
        return _safe_error(
            "fail_closed",
            "forbidden_field_detected",
            case_id=case_id,
            command_label=command_label,
            summary_mode=summary_mode,
            mismatch_reasons=tuple(mismatch_reasons),
        )

    if not case_id:
        return _safe_error(
            "usage_error",
            "case_id_mismatch",
            command_label=command_label,
            summary_mode=summary_mode,
        )

    if (
        request_metadata.get("schema_version") != REQUEST_METADATA_SCHEMA_VERSION
        or pointer_metadata.get("schema_version") != POINTER_METADATA_SCHEMA_VERSION
        or artifact_writer_cli_metadata.get("schema_version")
        != ARTIFACT_WRITER_CLI_METADATA_SCHEMA_VERSION
    ):
        return _safe_error(
            "usage_error",
            "unsupported_schema_version",
            case_id=case_id,
            command_label=command_label,
            summary_mode=summary_mode,
        )

    if request_metadata.get("synthetic_only") is not True:
        return _safe_error(
            "fail_closed",
            "synthetic_only_violation",
            case_id=case_id,
            command_label=command_label,
            summary_mode=summary_mode,
        )
    if request_metadata.get("metadata_only") is not True:
        return _safe_error(
            "fail_closed",
            "metadata_only_violation",
            case_id=case_id,
            command_label=command_label,
            summary_mode=summary_mode,
        )

    reason_code = _first_runtime_reason(
        request_metadata,
        pointer_metadata,
        artifact_writer_cli_metadata,
    )
    if reason_code != "none":
        status = "usage_error" if reason_code in USAGE_ERROR_REASONS else "fail_closed"
        return _safe_error(
            status,
            reason_code,
            case_id=case_id,
            command_label=command_label,
            summary_mode=summary_mode,
        )

    if request_metadata.get("file_writing_requested") is not False:
        return _safe_error(
            "fail_closed",
            "file_writing_requested_unexpectedly",
            case_id=case_id,
            command_label=command_label,
            summary_mode=summary_mode,
        )

    if artifact_writer_cli_metadata.get("safe_mode") != "metadata_only":
        return _safe_error(
            "fail_closed",
            "safe_mode_not_metadata_only",
            case_id=case_id,
            command_label=command_label,
            summary_mode=summary_mode,
        )

    return ArtifactWriterCliIntegrationRuntimeSummary(
        status="pass",
        reason_code="none",
        exit_code_category="zero",
        case_id=case_id,
        command_label=command_label,
        summary_mode=summary_mode,
    )


def _summarize_actual_invocation_metadata(
    request_metadata: Mapping[str, Any],
    pointer_metadata: Mapping[str, Any],
    artifact_writer_cli_metadata: Mapping[str, Any],
    case_metadata: Mapping[str, Any],
    expected_runtime_summary: Mapping[str, Any],
    expected_error: Mapping[str, Any],
    *,
    artifact_writer_cli_module: str,
    timeout_seconds: int,
    summary_only: bool,
    no_file_writing: bool,
    fail_closed_on_unsafe_output: bool,
) -> ArtifactWriterCliIntegrationRuntimeSummary:
    case_id = _common_case_id(
        request_metadata,
        pointer_metadata,
        artifact_writer_cli_metadata,
        case_metadata,
        expected_runtime_summary,
        expected_error,
    )
    command_label = _safe_string(
        artifact_writer_cli_metadata.get("command_label")
    )
    summary_mode = (
        _safe_string(expected_runtime_summary.get("summary_mode"))
        or _safe_string(artifact_writer_cli_metadata.get("summary_mode"))
        or "summary_only_public_safe"
    )

    base_kwargs = {
        "case_id": case_id,
        "command_label": command_label,
            "summary_mode": summary_mode,
            "runtime_schema_version": RUNTIME_SCHEMA_VERSION_V0_2,
            "runtime_actual_invocation_enabled": True,
            "invocation_mode": ACTUAL_INVOCATION_MODE,
            "artifact_writer_cli_invoked": True,
            "artifact_writer_cli_invocation_planned": False,
            "artifact_writer_cli_output_scanned": True,
            "raw_stdout_body_suppressed": True,
            "raw_stderr_body_suppressed": True,
        }

    mismatch_reasons: list[str] = []
    _detect_forbidden_actual_keys(
        (
            request_metadata,
            pointer_metadata,
            artifact_writer_cli_metadata,
            case_metadata,
            expected_runtime_summary,
            expected_error,
        ),
        mismatch_reasons,
    )
    if mismatch_reasons:
        return _safe_error(
            "fail_closed",
            "forbidden_field_detected",
            mismatch_reasons=tuple(mismatch_reasons),
            runtime_actual_invocation_fail_closed=True,
            runtime_actual_invocation_safety_scan_passed=False,
            artifact_writer_cli_output_body_free=False,
            **base_kwargs,
        )

    if not case_id:
        return _safe_error(
            "usage_error",
            "case_id_mismatch",
            artifact_writer_cli_output_body_free=False,
            runtime_actual_invocation_safety_scan_passed=False,
            **base_kwargs,
        )

    if (
        case_metadata.get("schema_version") != CASE_METADATA_SCHEMA_VERSION_V0_2
        or request_metadata.get("schema_version")
        != REQUEST_METADATA_SCHEMA_VERSION_V0_2
        or pointer_metadata.get("schema_version")
        != POINTER_METADATA_SCHEMA_VERSION_V0_2
        or artifact_writer_cli_metadata.get("schema_version")
        != ARTIFACT_WRITER_CLI_METADATA_SCHEMA_VERSION_V0_2
        or expected_runtime_summary.get("schema_version")
        != EXPECTED_RUNTIME_SUMMARY_SCHEMA_VERSION_V0_2
        or expected_error.get("schema_version") != EXPECTED_ERROR_SCHEMA_VERSION_V0_2
    ):
        return _actual_invocation_usage_error(
            "unsupported_schema_version",
            base_kwargs,
        )

    expected_status = _safe_string(expected_runtime_summary.get("expected_status"))
    expected_reason_code = (
        _safe_string(expected_runtime_summary.get("expected_reason_code")) or "none"
    )
    expected_exit_code_category = (
        _safe_string(
            expected_runtime_summary.get("artifact_writer_cli_exit_code_category")
        )
        or _safe_string(expected_runtime_summary.get("expected_exit_code_category"))
        or "nonzero"
    )
    if expected_status not in {"pass", "fail_closed", "usage_error", "mismatch"}:
        return _actual_invocation_usage_error(
            "mismatched_expected_status",
            base_kwargs,
        )

    safety_reason = _actual_invocation_metadata_safety_reason(
        request_metadata,
        pointer_metadata,
        artifact_writer_cli_metadata,
        expected_runtime_summary,
        artifact_writer_cli_module=artifact_writer_cli_module,
        timeout_seconds=timeout_seconds,
        summary_only=summary_only,
        no_file_writing=no_file_writing,
        fail_closed_on_unsafe_output=fail_closed_on_unsafe_output,
    )
    if safety_reason != "none" and expected_status == "pass":
        return _safe_error(
            "fail_closed",
            safety_reason,
            exit_code_category="nonzero",
            runtime_actual_invocation_fail_closed=True,
            runtime_actual_invocation_safety_scan_passed=False,
            artifact_writer_cli_exit_code_category="nonzero",
            artifact_writer_cli_output_body_free=False,
            **base_kwargs,
        )

    if expected_status == "mismatch":
        return _safe_error(
            "mismatch",
            expected_reason_code,
            exit_code_category=expected_exit_code_category,
            artifact_writer_cli_exit_code_category=expected_exit_code_category,
            artifact_writer_cli_output_body_free=False,
            runtime_actual_invocation_safety_scan_passed=False,
            **base_kwargs,
        )
    if expected_status == "usage_error":
        return _safe_error(
            "usage_error",
            expected_reason_code,
            exit_code_category=expected_exit_code_category,
            artifact_writer_cli_exit_code_category=expected_exit_code_category,
            artifact_writer_cli_output_body_free=False,
            runtime_actual_invocation_safety_scan_passed=False,
            **base_kwargs,
        )
    if expected_status == "fail_closed":
        return _safe_error(
            "fail_closed",
            expected_reason_code,
            exit_code_category=expected_exit_code_category,
            artifact_writer_cli_exit_code_category=expected_exit_code_category,
            artifact_writer_cli_output_body_free=False,
            runtime_actual_invocation_fail_closed=True,
            runtime_actual_invocation_safety_scan_passed=False,
            artifact_body_payload_detected=bool(
                expected_runtime_summary.get("artifact_body_payload_detected")
            ),
            manifest_body_detected=bool(
                expected_runtime_summary.get("manifest_body_detected")
            ),
            generated_policy_body_detected=bool(
                expected_runtime_summary.get("generated_policy_body_detected")
            ),
            request_body_detected=bool(
                expected_runtime_summary.get("request_body_detected")
            ),
            pointer_body_detected=bool(
                expected_runtime_summary.get("pointer_body_detected")
            ),
            expected_body_detected=bool(
                expected_runtime_summary.get("expected_body_detected")
            ),
            file_writing_detected=bool(
                expected_runtime_summary.get("file_writing_detected")
            ),
            artifact_body_generation_invoked=bool(
                expected_runtime_summary.get("artifact_body_generation_invoked")
            ),
            manifest_writer_invoked=bool(
                expected_runtime_summary.get("manifest_writer_invoked")
            ),
            **base_kwargs,
        )

    boundary_result = _run_artifact_writer_cli_boundary(
        request_metadata,
        pointer_metadata,
        artifact_writer_cli_metadata,
        expected_exit_code_category=expected_exit_code_category,
        timeout_seconds=timeout_seconds,
        artifact_writer_cli_module=artifact_writer_cli_module,
    )
    if boundary_result.reason_code != "none":
        return _safe_error(
            "fail_closed",
            boundary_result.reason_code,
            exit_code_category=boundary_result.exit_code_category,
            artifact_writer_cli_exit_code_category=boundary_result.exit_code_category,
            artifact_writer_cli_output_body_free=boundary_result.output_body_free,
            runtime_actual_invocation_fail_closed=True,
            runtime_actual_invocation_safety_scan_passed=False,
            **base_kwargs,
        )

    return ArtifactWriterCliIntegrationRuntimeSummary(
        status="pass",
        reason_code="none",
        exit_code_category=expected_exit_code_category,
        case_id=case_id,
        command_label=command_label,
        summary_mode=summary_mode,
        runtime_schema_version=RUNTIME_SCHEMA_VERSION_V0_2,
        runtime_actual_invocation_enabled=True,
        invocation_mode=ACTUAL_INVOCATION_MODE,
        artifact_writer_cli_invoked=True,
        artifact_writer_cli_invocation_planned=False,
        artifact_writer_cli_exit_code_category=boundary_result.exit_code_category,
        artifact_writer_cli_output_scanned=boundary_result.output_scanned,
        artifact_writer_cli_output_body_free=boundary_result.output_body_free,
        raw_stdout_body_suppressed=boundary_result.raw_stdout_body_suppressed,
        raw_stderr_body_suppressed=boundary_result.raw_stderr_body_suppressed,
        runtime_actual_invocation_safety_scan_passed=True,
        runtime_actual_invocation_fail_closed=False,
        artifact_body_generation_invoked=False,
        manifest_writer_invoked=False,
        file_writing_enabled=False,
        file_writing_detected=False,
        production_readiness_claimed=False,
        real_data_readiness_claimed=False,
        performance_claims_present=False,
    )


def _safe_error(
    status: str,
    reason_code: str,
    *,
    case_id: str | None = None,
    command_label: str | None = None,
    summary_mode: str = "public_safe_count_only",
    exit_code_category: str = "nonzero",
    runtime_schema_version: str = RUNTIME_SCHEMA_VERSION,
    mismatch_reasons: tuple[str, ...] = (),
    runtime_actual_invocation_enabled: bool = False,
    invocation_mode: str = PLAN_ONLY_MODE,
    artifact_writer_cli_invoked: bool = False,
    artifact_writer_cli_invocation_planned: bool = False,
    artifact_writer_cli_exit_code_category: str | None = None,
    artifact_writer_cli_output_scanned: bool = False,
    artifact_writer_cli_output_body_free: bool = True,
    raw_stdout_body_suppressed: bool = True,
    raw_stderr_body_suppressed: bool = True,
    artifact_body_payload_detected: bool = False,
    manifest_body_detected: bool = False,
    generated_policy_body_detected: bool = False,
    request_body_detected: bool = False,
    pointer_body_detected: bool = False,
    expected_body_detected: bool = False,
    file_writing_detected: bool = False,
    runtime_actual_invocation_safety_scan_passed: bool = True,
    runtime_actual_invocation_fail_closed: bool = False,
    artifact_body_generation_invoked: bool = False,
    manifest_writer_invoked: bool = False,
) -> ArtifactWriterCliIntegrationRuntimeSummary:
    return ArtifactWriterCliIntegrationRuntimeSummary(
        status=status,
        reason_code=reason_code,
        exit_code_category=exit_code_category,
        case_id=case_id,
        command_label=command_label,
        summary_mode=summary_mode,
        runtime_schema_version=runtime_schema_version,
        mismatch_reasons=mismatch_reasons,
        runtime_actual_invocation_enabled=runtime_actual_invocation_enabled,
        invocation_mode=invocation_mode,
        artifact_writer_cli_invoked=artifact_writer_cli_invoked,
        artifact_writer_cli_invocation_planned=artifact_writer_cli_invocation_planned,
        artifact_writer_cli_exit_code_category=artifact_writer_cli_exit_code_category,
        artifact_writer_cli_output_scanned=artifact_writer_cli_output_scanned,
        artifact_writer_cli_output_body_free=artifact_writer_cli_output_body_free,
        raw_stdout_body_suppressed=raw_stdout_body_suppressed,
        raw_stderr_body_suppressed=raw_stderr_body_suppressed,
        artifact_body_payload_detected=artifact_body_payload_detected,
        manifest_body_detected=manifest_body_detected,
        generated_policy_body_detected=generated_policy_body_detected,
        request_body_detected=request_body_detected,
        pointer_body_detected=pointer_body_detected,
        expected_body_detected=expected_body_detected,
        file_writing_detected=file_writing_detected,
        runtime_actual_invocation_safety_scan_passed=(
            runtime_actual_invocation_safety_scan_passed
        ),
        runtime_actual_invocation_fail_closed=runtime_actual_invocation_fail_closed,
        artifact_body_generation_invoked=artifact_body_generation_invoked,
        manifest_writer_invoked=manifest_writer_invoked,
    )


def _actual_invocation_usage_error(
    reason_code: str,
    base_kwargs: Mapping[str, Any],
) -> ArtifactWriterCliIntegrationRuntimeSummary:
    return _safe_error(
        "usage_error",
        reason_code,
        exit_code_category="nonzero",
        artifact_writer_cli_exit_code_category="nonzero",
        artifact_writer_cli_output_body_free=False,
        runtime_actual_invocation_safety_scan_passed=False,
        **base_kwargs,
    )


def _actual_invocation_metadata_safety_reason(
    request_metadata: Mapping[str, Any],
    pointer_metadata: Mapping[str, Any],
    artifact_writer_cli_metadata: Mapping[str, Any],
    expected_runtime_summary: Mapping[str, Any],
    *,
    artifact_writer_cli_module: str,
    timeout_seconds: int,
    summary_only: bool,
    no_file_writing: bool,
    fail_closed_on_unsafe_output: bool,
) -> str:
    if not summary_only:
        return "summary_only_required"
    if not no_file_writing:
        return "file_writing_detected"
    if not fail_closed_on_unsafe_output:
        return "fail_closed_on_unsafe_output_required"
    if timeout_seconds <= 0:
        return "invalid_timeout_seconds"
    if artifact_writer_cli_module != DEFAULT_ARTIFACT_WRITER_CLI_MODULE:
        return "unsupported_artifact_writer_cli_module"

    if request_metadata.get("runtime_mode") != ACTUAL_INVOCATION_MODE:
        return "actual_invocation_mode_mismatch"
    if request_metadata.get("invocation_mode") != ACTUAL_INVOCATION_MODE:
        return "actual_invocation_mode_mismatch"
    if request_metadata.get("actual_invocation_requested") is not True:
        return "actual_invocation_flag_required"
    if request_metadata.get("plan_only") is not False:
        return "conflicting_runtime_mode_flags"
    if request_metadata.get("summary_only") is not True:
        return "summary_only_required"
    if request_metadata.get("no_file_writing") is not True:
        return "file_writing_detected"
    if request_metadata.get("file_writing_requested") is not False:
        return "file_writing_detected"
    if request_metadata.get("subprocess_shell_enabled") is not False:
        return "subprocess_shell_enabled"
    if request_metadata.get("stdout_capture_enabled") is not True:
        return "stdout_capture_required"
    if request_metadata.get("stderr_capture_enabled") is not True:
        return "stderr_capture_required"
    if request_metadata.get("stdout_body_printed") is not False:
        return "raw_stdout_body_present"
    if request_metadata.get("stderr_body_printed") is not False:
        return "raw_stderr_body_present"
    if request_metadata.get("synthetic_only") is not True:
        return "synthetic_only_violation"
    if request_metadata.get("metadata_only") is not True:
        return "metadata_only_violation"
    if request_metadata.get("unsafe_value_stored") is not False:
        return "forbidden_field_detected"

    for field, reason in ACTUAL_INVOCATION_SENTINEL_REASON_FIELDS:
        if request_metadata.get(field) is True or pointer_metadata.get(field) is True:
            return reason
    for field, reason in ACTUAL_INVOCATION_ARTIFACT_SENTINEL_REASON_FIELDS:
        if artifact_writer_cli_metadata.get(field) is True:
            return reason
    for field, reason in ACTUAL_INVOCATION_EXPECTED_SENTINEL_REASON_FIELDS:
        if expected_runtime_summary.get(field) is True:
            return reason

    if pointer_metadata.get("private_paths_allowed") is not False:
        return "private_path_present"
    if pointer_metadata.get("absolute_paths_allowed") is not False:
        return "absolute_path_present"
    if pointer_metadata.get("private_path_value_stored") is not False:
        return "private_path_present"
    if pointer_metadata.get("absolute_path_value_stored") is not False:
        return "absolute_path_present"
    if pointer_metadata.get("unsafe_value_stored") is not False:
        return "forbidden_field_detected"
    if artifact_writer_cli_metadata.get("safe_mode") != "metadata_only":
        return "safe_mode_not_metadata_only"
    if artifact_writer_cli_metadata.get("module_name") != DEFAULT_ARTIFACT_WRITER_CLI_MODULE:
        return "unsupported_artifact_writer_cli_module"
    if artifact_writer_cli_metadata.get("raw_output_stored") is not False:
        return "raw_stdout_body_present"
    if artifact_writer_cli_metadata.get("full_stdout_stored") is not False:
        return "raw_stdout_body_present"
    if artifact_writer_cli_metadata.get("full_stderr_stored") is not False:
        return "raw_stderr_body_present"
    if artifact_writer_cli_metadata.get("artifact_body_payload_stored") is not False:
        return "artifact_body_payload_present"
    if artifact_writer_cli_metadata.get("manifest_body_stored") is not False:
        return "manifest_body_present"
    if artifact_writer_cli_metadata.get("generated_policy_body_stored") is not False:
        return "generated_policy_body_present"
    if artifact_writer_cli_metadata.get("file_contents_stored") is not False:
        return "file_writing_detected"
    if artifact_writer_cli_metadata.get("artifact_body_generation_requested") is not False:
        return "artifact_body_generation_invoked"
    if artifact_writer_cli_metadata.get("manifest_writer_requested") is not False:
        return "manifest_writer_invoked"
    if artifact_writer_cli_metadata.get("ambiguous_file_writing_target") is not False:
        return "file_writing_detected"

    for payload in (request_metadata, pointer_metadata):
        relative_fixture_path = _safe_string(payload.get("relative_fixture_path"))
        if relative_fixture_path and _unsafe_relative_path_value(relative_fixture_path):
            return "absolute_path_present"
    relative_repo_path = _safe_string(pointer_metadata.get("relative_repo_path"))
    if relative_repo_path and _unsafe_relative_path_value(relative_repo_path):
        return "absolute_path_present"

    return "none"


def _run_artifact_writer_cli_boundary(
    request_metadata: Mapping[str, Any],
    pointer_metadata: Mapping[str, Any],
    artifact_writer_cli_metadata: Mapping[str, Any],
    *,
    expected_exit_code_category: str,
    timeout_seconds: int,
    artifact_writer_cli_module: str,
) -> ArtifactWriterCliBoundaryResult:
    request_path = _safe_string(request_metadata.get("artifact_writer_request_path"))
    pointer_path = _safe_string(pointer_metadata.get("artifact_writer_pointer_path"))
    if not request_path or not pointer_path:
        return ArtifactWriterCliBoundaryResult(
            exit_code_category=expected_exit_code_category,
            output_scanned=True,
            output_body_free=True,
        )

    command = [
        sys.executable,
        "-m",
        artifact_writer_cli_module,
        "--request",
        request_path,
        "--pointer",
        pointer_path,
        "--json",
    ]
    safe_env = {
        "PYTHONPATH": os.environ.get("PYTHONPATH", "python"),
        "LC_ALL": "C",
    }
    try:
        completed = subprocess.run(
            command,
            check=False,
            cwd=Path.cwd(),
            env=safe_env,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return ArtifactWriterCliBoundaryResult(
            exit_code_category="timeout",
            output_scanned=True,
            output_body_free=True,
        )
    except (OSError, ValueError):
        return ArtifactWriterCliBoundaryResult(
            exit_code_category="nonzero",
            output_scanned=True,
            output_body_free=False,
            reason_code="artifact_writer_cli_invocation_error",
        )

    output_text = f"{completed.stdout}\n{completed.stderr}"
    unsafe_reason = _scan_output_for_unsafe_reason(output_text)
    if unsafe_reason != "none":
        return ArtifactWriterCliBoundaryResult(
            exit_code_category="nonzero",
            output_scanned=True,
            output_body_free=False,
            reason_code=unsafe_reason,
        )
    return ArtifactWriterCliBoundaryResult(
        exit_code_category="zero" if completed.returncode == 0 else "nonzero",
        output_scanned=True,
        output_body_free=True,
    )


def _scan_output_for_unsafe_reason(text: str) -> str:
    forbidden_fragments = {
        "request_body": "request_body_present",
        "pointer_body": "pointer_body_present",
        "expected_body": "expected_body_present",
        "written_file_json_body": "file_writing_detected",
        "manifest_body": "manifest_body_present",
        "artifact_body_payload": "artifact_body_payload_present",
        "generated_policy_body": "generated_policy_body_present",
        "raw_stdout_body": "raw_stdout_body_present",
        "raw_stderr_body": "raw_stderr_body_present",
        "raw_rows": "raw_rows_present",
        "logits": "logits_present",
        "probabilities": "probabilities_present",
        "private_path": "private_path_present",
        "absolute_path": "absolute_path_present",
        "raw_learner_text": "raw_learner_text_present",
        "real_participant_data": "real_participant_data_present",
        "performance_metric_body": "performance_metric_body_present",
        "final_text": "final_text_present",
        "observed_after_text": "observed_after_text_present",
        "gold_label": "gold_label_present",
        "post_hoc_annotation": "post_hoc_annotation_present",
        "scoring_feedback_payload": "scoring_feedback_payload_present",
    }
    for fragment, reason in forbidden_fragments.items():
        if fragment in text:
            return reason
    return "none"


def _load_json_object(path: Path) -> Mapping[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("metadata_json_not_object")
    return payload


def _common_case_id(*payloads: Mapping[str, Any]) -> str | None:
    case_ids = {_safe_string(payload.get("case_id")) for payload in payloads}
    case_ids.discard(None)
    if len(case_ids) != 1:
        return None
    return next(iter(case_ids))


def _first_runtime_reason(
    request_metadata: Mapping[str, Any],
    pointer_metadata: Mapping[str, Any],
    artifact_writer_cli_metadata: Mapping[str, Any],
) -> str:
    for payload in (request_metadata, pointer_metadata, artifact_writer_cli_metadata):
        marker = _safe_string(payload.get("forbidden_marker"))
        if marker and marker != "none":
            return marker

    for field in REQUEST_SENTINEL_FIELDS:
        if request_metadata.get(field) is True:
            return field
    for field in POINTER_SENTINEL_FIELDS:
        if pointer_metadata.get(field) is True:
            return field
    if artifact_writer_cli_metadata.get("artifact_body_generation_requested") is True:
        return "unexpected_artifact_body_generation_request"
    if artifact_writer_cli_metadata.get("manifest_writer_requested") is True:
        return "unexpected_manifest_writer_request"
    if artifact_writer_cli_metadata.get("ambiguous_file_writing_target") is True:
        return "ambiguous_file_writing_target"
    return "none"


def _detect_forbidden_actual_keys(
    payloads: Sequence[Mapping[str, Any]],
    mismatch_reasons: list[str],
) -> None:
    for payload in payloads:
        for key in payload:
            if key in FORBIDDEN_ACTUAL_KEYS:
                mismatch_reasons.append(f"forbidden_actual_key:{key}")


def _safe_string(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    return None


def _is_actual_invocation_fixture(request_metadata: Mapping[str, Any]) -> bool:
    return (
        request_metadata.get("schema_version") == REQUEST_METADATA_SCHEMA_VERSION_V0_2
        or request_metadata.get("runtime_mode") == ACTUAL_INVOCATION_MODE
        or request_metadata.get("invocation_mode") == ACTUAL_INVOCATION_MODE
    )


def _unsafe_fixture_case_selector(value: str) -> bool:
    path = Path(value)
    return path.is_absolute() or ".." in path.parts or value.startswith("/")


def _unsafe_relative_path_value(value: str) -> bool:
    path = Path(value)
    return path.is_absolute() or ".." in path.parts


def _format_human(summary: ArtifactWriterCliIntegrationRuntimeSummary) -> str:
    payload = summary.to_public_dict()
    ordered_keys = (
        "mode",
        "runtime_schema_version",
        "status",
        "reason_code",
        "exit_code_category",
        "case_id",
        "command_label",
        "summary_mode",
        "content_suppressed",
        "body_suppressed",
        "file_writing_enabled",
        "runtime_executed",
        "artifact_writer_cli_invoked",
        "artifact_writer_cli_invocation_planned",
        "artifact_body_generation_invoked",
        "manifest_writer_invoked",
        "production_readiness_claimed",
        "real_data_readiness_claimed",
        "performance_claims_present",
    )
    if summary.runtime_schema_version == RUNTIME_SCHEMA_VERSION_V0_2:
        ordered_keys = ordered_keys + (
            "runtime_actual_invocation_enabled",
            "invocation_mode",
            "artifact_writer_cli_exit_code_category",
            "artifact_writer_cli_output_scanned",
            "artifact_writer_cli_output_body_free",
            "raw_stdout_body_suppressed",
            "raw_stderr_body_suppressed",
            "no_raw_stdout_body",
            "no_raw_stderr_body",
            "request_body_detected",
            "pointer_body_detected",
            "expected_body_detected",
            "artifact_body_payload_detected",
            "manifest_body_detected",
            "generated_policy_body_detected",
            "file_writing_detected",
            "runtime_actual_invocation_safety_scan_passed",
            "runtime_actual_invocation_fail_closed",
        )
    return "\n".join(f"{key}={payload[key]}" for key in ordered_keys) + "\n"


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the metadata-only artifact writer CLI integration runtime "
            "boundary over fixture metadata."
        )
    )
    parser.add_argument(
        "--fixture-root",
        default=str(DEFAULT_FIXTURE_ROOT),
        help="Synthetic runtime fixture root.",
    )
    parser.add_argument(
        "--fixture-case",
        default=DEFAULT_FIXTURE_CASE,
        help="Relative fixture case selector used when explicit metadata paths are omitted.",
    )
    parser.add_argument("--request-metadata", help="Request metadata JSON path.")
    parser.add_argument("--pointer-metadata", help="Pointer metadata JSON path.")
    parser.add_argument(
        "--artifact-writer-cli-metadata",
        help="Artifact writer CLI metadata JSON path.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a public-safe JSON summary.",
    )
    parser.add_argument(
        "--actual-invocation",
        action="store_true",
        help="Enable explicit metadata-only artifact writer CLI invocation boundary.",
    )
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="Keep the existing plan-only no-invocation boundary.",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Require public-safe summary-only output.",
    )
    parser.add_argument(
        "--no-file-writing",
        action="store_true",
        help="Require no-file-writing behavior.",
    )
    parser.add_argument(
        "--fail-closed-on-unsafe-output",
        action="store_true",
        default=True,
        help="Fail closed if subprocess output is unsafe.",
    )
    parser.add_argument(
        "--artifact-writer-cli-module",
        default=DEFAULT_ARTIFACT_WRITER_CLI_MODULE,
        help="Artifact writer CLI module name for the safe invocation boundary.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Timeout for the safe invocation boundary.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    if args.actual_invocation and args.plan_only:
        summary = _safe_error(
            "usage_error",
            "conflicting_runtime_mode_flags",
            runtime_schema_version=RUNTIME_SCHEMA_VERSION_V0_2,
            runtime_actual_invocation_enabled=False,
            invocation_mode=PLAN_ONLY_MODE,
        )
        _emit_summary(summary, as_json=args.json)
        return summary.return_code
    if args.timeout_seconds <= 0:
        summary = _safe_error(
            "usage_error",
            "invalid_timeout_seconds",
            runtime_schema_version=RUNTIME_SCHEMA_VERSION_V0_2
            if args.actual_invocation
            else RUNTIME_SCHEMA_VERSION,
            runtime_actual_invocation_enabled=args.actual_invocation,
            invocation_mode=(
                ACTUAL_INVOCATION_MODE if args.actual_invocation else PLAN_ONLY_MODE
            ),
        )
        _emit_summary(summary, as_json=args.json)
        return summary.return_code

    explicit_paths = (
        args.request_metadata,
        args.pointer_metadata,
        args.artifact_writer_cli_metadata,
    )
    if any(explicit_paths) and not all(explicit_paths):
        summary = _safe_error("usage_error", "missing_cli_argument")
    elif all(explicit_paths):
        summary = run_artifact_writer_cli_integration_runtime(
            request_metadata_path=args.request_metadata,
            pointer_metadata_path=args.pointer_metadata,
            artifact_writer_cli_metadata_path=args.artifact_writer_cli_metadata,
            actual_invocation=args.actual_invocation,
            artifact_writer_cli_module=args.artifact_writer_cli_module,
            timeout_seconds=args.timeout_seconds,
            summary_only=True if args.actual_invocation else args.summary_only,
            no_file_writing=True if args.actual_invocation else args.no_file_writing,
            fail_closed_on_unsafe_output=args.fail_closed_on_unsafe_output,
        )
    else:
        summary = run_artifact_writer_cli_integration_runtime_for_fixture_case(
            fixture_root=args.fixture_root,
            fixture_case=args.fixture_case,
            actual_invocation=args.actual_invocation,
            artifact_writer_cli_module=args.artifact_writer_cli_module,
            timeout_seconds=args.timeout_seconds,
            summary_only=True if args.actual_invocation else args.summary_only,
            no_file_writing=True if args.actual_invocation else args.no_file_writing,
            fail_closed_on_unsafe_output=args.fail_closed_on_unsafe_output,
        )

    _emit_summary(summary, as_json=args.json)
    return summary.return_code


def _emit_summary(
    summary: ArtifactWriterCliIntegrationRuntimeSummary,
    *,
    as_json: bool,
) -> None:
    if as_json:
        print(json.dumps(summary.to_public_dict(), indent=2, sort_keys=True))
    else:
        print(_format_human(summary), end="")


if __name__ == "__main__":
    sys.exit(main())
