"""Metadata-only frozen policy generation manifest writer runtime.

This module builds a safe metadata-only manifest writer result from synthetic
runtime request and pointer metadata. It does not generate manifest bodies,
write manifest files, connect to artifact writer CLIs, train models, run
calibration, or compute metrics.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REQUEST_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_runtime_request_v0.1"
)
ARTIFACT_WRITER_RESULT_POINTER_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_runtime_artifact_writer_result_pointer_v0.1"
)
ARTIFACT_BODY_GENERATION_RESULT_POINTER_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_runtime_artifact_body_generation_result_pointer_v0.1"
)
ARTIFACT_WRITER_RESULT_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_result_v0.1"
)
ARTIFACT_BODY_GENERATION_RESULT_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_result_v0.1"
)
RESULT_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_manifest_writer_result_v0.1"
)

SUPPORTED_MODE = "metadata_only_no_file"
PASS_SAFE_SUMMARY = "metadata_only_manifest_writer_result"
FAIL_SAFE_SUMMARY = "fail_closed_metadata_only_manifest_writer_result"
USAGE_ERROR_SAFE_SUMMARY = "usage_error_metadata_only_manifest_writer_result"
INPUT_ERROR_SAFE_SUMMARY = "input_error_metadata_only_manifest_writer_result"

REQUIRED_REQUEST_FIELDS = (
    "schema_version",
    "request_id",
    "manifest_writer_mode",
    "include_manifest_body",
    "allow_manifest_file_writing",
    "manifest_out",
    "overwrite_policy",
    "synthetic_notice",
    "no_oracle_notice",
    "non_proof_notice",
    "validation_reference_ids",
    "release_quality_reference_ids",
)

REQUIRED_POINTER_FIELDS = (
    "schema_version",
    "pointer_id",
    "source_kind",
    "source_fixture_id",
    "safe_metadata_reference_id",
    "include_body_payload",
    "include_raw_rows",
    "include_private_paths",
)

COUNT_SUMMARY_FIELDS = (
    "manifest_metadata_field_count",
    "validation_reference_count",
    "release_quality_reference_count",
    "raw_row_count",
    "logits_dump_count",
    "private_path_count",
    "absolute_path_count",
    "artifact_body_payload_count",
    "generated_policy_body_count",
    "manifest_body_count",
    "request_body_count",
    "pointer_body_count",
    "expected_body_count",
    "performance_metric_count",
    "written_file_count",
)

ZERO_COUNT_FIELDS = (
    "raw_row_count",
    "logits_dump_count",
    "private_path_count",
    "absolute_path_count",
    "artifact_body_payload_count",
    "generated_policy_body_count",
    "manifest_body_count",
    "request_body_count",
    "pointer_body_count",
    "expected_body_count",
    "performance_metric_count",
    "written_file_count",
)

SAFETY_FLAGS = {
    "content_suppressed": True,
    "manifest_body_suppressed": True,
    "no_raw_rows": True,
    "no_logits_dump": True,
    "no_private_paths": True,
    "no_absolute_paths": True,
    "no_artifact_body_payload": True,
    "no_generated_policy_body": True,
    "no_manifest_body_nesting": True,
    "no_request_body": True,
    "no_pointer_body": True,
    "no_expected_body": True,
    "no_performance_claims": True,
    "synthetic_only_checked": True,
    "no_oracle_checked": True,
    "non_proof_notice_checked": True,
    "path_policy_checked": True,
    "content_policy_checked": True,
    "file_writing_checked": True,
}

FORBIDDEN_PAYLOAD_KEY_REASONS = {
    "manifest_body": "manifest_body_requested",
    "manifest_json_body": "manifest_json_body_requested",
    "artifact_body_payload": "artifact_body_payload_leakage",
    "generated_policy_body": "generated_policy_body_leakage",
    "request_body": "request_body_leakage",
    "pointer_body": "pointer_body_leakage",
    "expected_body": "expected_body_leakage",
    "expected_result_body": "expected_body_leakage",
    "raw_rows": "raw_rows_leakage",
    "logits": "logits_dump_leakage",
    "probabilities": "logits_dump_leakage",
    "private_path": "private_path_leakage",
    "absolute_path": "absolute_path_leakage",
    "raw_learner_text": "raw_learner_text_leakage",
    "final_text": "raw_learner_text_leakage",
    "observed_after_text": "raw_learner_text_leakage",
    "gold_label": "raw_learner_text_leakage",
    "scoring_feedback_payload": "raw_learner_text_leakage",
    "real_participant_data": "real_data_marker",
    "performance_metric_body": "performance_claim",
    "performance_metrics": "performance_claim",
}

SAFE_SENTINEL_REASON_CODES = frozenset(
    {
        "generated_policy_body_leakage",
        "artifact_body_payload_leakage",
        "manifest_body_requested",
        "manifest_json_body_requested",
        "request_body_leakage",
        "pointer_body_leakage",
        "expected_body_leakage",
        "raw_rows_leakage",
        "logits_dump_leakage",
        "private_path_leakage",
        "absolute_path_leakage",
        "raw_learner_text_leakage",
        "performance_claim",
        "missing_synthetic_notice",
        "missing_no_oracle_notice",
        "missing_non_proof_notice",
        "unsafe_manifest_output_path",
        "overwrite_without_policy",
        "unsupported_artifact_writer_cli_integration",
        "real_data_marker",
    }
)

UNSAFE_PATH_MARKERS = (
    "/Users/",
    "/home/",
    "/private/",
    "/var/folders/",
    "C:\\",
    "real_data/",
    "participant_data/",
    "private_data/",
    "manual_outputs/",
)

CLI_SAFE_SUMMARY_FIELDS = (
    "mode",
    "result_schema_version",
    "writer_status",
    "manifest_writer_mode",
    "manifest_id",
    "artifact_id",
    "artifact_body_id",
    "validation_reference_count",
    "release_quality_reference_count",
    "manifest_body_available",
    "manifest_file_written",
    "manifest_output_path_available",
    "reason_codes",
    "failed_checks",
    "safety_flags",
    "count_summary",
    "safe_summary",
    "runtime_writer_executed",
    "release_quality_ready",
)


@dataclass(frozen=True)
class ManifestWriterRequest:
    schema_version: str | None
    request_id: str | None
    manifest_writer_mode: str | None
    include_manifest_body: bool
    allow_manifest_file_writing: bool
    manifest_out: str | None
    overwrite_policy: str | None
    synthetic_notice: bool
    no_oracle_notice: bool
    non_proof_notice: bool
    validation_reference_ids: list[str]
    release_quality_reference_ids: list[str]
    requested_artifact_writer_cli_integration: bool
    marker_reason_codes: list[str] = field(default_factory=list)
    missing_required_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ArtifactWriterResultPointer:
    schema_version: str | None
    result_schema_version: str | None
    pointer_id: str | None
    source_kind: str | None
    source_fixture_id: str | None
    safe_metadata_reference_id: str | None
    artifact_id: str | None
    manifest_id: str | None
    writer_status: str | None
    artifact_body_available: bool
    include_body_payload: bool
    include_raw_rows: bool
    include_private_paths: bool
    synthetic_only_checked: bool
    no_oracle_checked: bool
    safe_reference_only: bool
    marker_reason_codes: list[str] = field(default_factory=list)
    missing_required_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ArtifactBodyGenerationResultPointer:
    schema_version: str | None
    result_schema_version: str | None
    pointer_id: str | None
    source_kind: str | None
    source_fixture_id: str | None
    safe_metadata_reference_id: str | None
    generation_status: str | None
    artifact_body_status: str | None
    artifact_body_available: bool
    manifest_body_generated: bool
    manifest_file_written: bool
    include_body_payload: bool
    include_raw_rows: bool
    include_private_paths: bool
    synthetic_only_checked: bool
    no_oracle_checked: bool
    safe_reference_only: bool
    marker_reason_codes: list[str] = field(default_factory=list)
    missing_required_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ManifestWriterSafetyFlags:
    content_suppressed: bool = True
    manifest_body_suppressed: bool = True
    no_raw_rows: bool = True
    no_logits_dump: bool = True
    no_private_paths: bool = True
    no_absolute_paths: bool = True
    no_artifact_body_payload: bool = True
    no_generated_policy_body: bool = True
    no_manifest_body_nesting: bool = True
    no_request_body: bool = True
    no_pointer_body: bool = True
    no_expected_body: bool = True
    no_performance_claims: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    non_proof_notice_checked: bool = True
    path_policy_checked: bool = True
    content_policy_checked: bool = True
    file_writing_checked: bool = True

    def to_safe_dict(self) -> dict[str, bool]:
        return {
            "content_suppressed": self.content_suppressed,
            "manifest_body_suppressed": self.manifest_body_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "no_logits_dump": self.no_logits_dump,
            "no_private_paths": self.no_private_paths,
            "no_absolute_paths": self.no_absolute_paths,
            "no_artifact_body_payload": self.no_artifact_body_payload,
            "no_generated_policy_body": self.no_generated_policy_body,
            "no_manifest_body_nesting": self.no_manifest_body_nesting,
            "no_request_body": self.no_request_body,
            "no_pointer_body": self.no_pointer_body,
            "no_expected_body": self.no_expected_body,
            "no_performance_claims": self.no_performance_claims,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
            "non_proof_notice_checked": self.non_proof_notice_checked,
            "path_policy_checked": self.path_policy_checked,
            "content_policy_checked": self.content_policy_checked,
            "file_writing_checked": self.file_writing_checked,
        }


@dataclass(frozen=True)
class ManifestWriterCountSummary:
    manifest_metadata_field_count: int
    validation_reference_count: int
    release_quality_reference_count: int
    raw_row_count: int = 0
    logits_dump_count: int = 0
    private_path_count: int = 0
    absolute_path_count: int = 0
    artifact_body_payload_count: int = 0
    generated_policy_body_count: int = 0
    manifest_body_count: int = 0
    request_body_count: int = 0
    pointer_body_count: int = 0
    expected_body_count: int = 0
    performance_metric_count: int = 0
    written_file_count: int = 0

    def to_safe_dict(self) -> dict[str, int]:
        return {
            "manifest_metadata_field_count": self.manifest_metadata_field_count,
            "validation_reference_count": self.validation_reference_count,
            "release_quality_reference_count": self.release_quality_reference_count,
            "raw_row_count": self.raw_row_count,
            "logits_dump_count": self.logits_dump_count,
            "private_path_count": self.private_path_count,
            "absolute_path_count": self.absolute_path_count,
            "artifact_body_payload_count": self.artifact_body_payload_count,
            "generated_policy_body_count": self.generated_policy_body_count,
            "manifest_body_count": self.manifest_body_count,
            "request_body_count": self.request_body_count,
            "pointer_body_count": self.pointer_body_count,
            "expected_body_count": self.expected_body_count,
            "performance_metric_count": self.performance_metric_count,
            "written_file_count": self.written_file_count,
        }


@dataclass(frozen=True)
class ManifestWriterError:
    error_status: str
    reason_codes: list[str]
    failed_checks: list[str]
    manifest_writer_mode: str | None = SUPPORTED_MODE
    manifest_id: str | None = None
    artifact_id: str | None = None
    artifact_body_id: str | None = None
    safe_summary: str = INPUT_ERROR_SAFE_SUMMARY


@dataclass(frozen=True)
class ManifestWriterResult:
    mode: str
    result_schema_version: str
    writer_status: str
    manifest_writer_mode: str | None
    manifest_id: str | None
    artifact_id: str | None
    artifact_body_id: str | None
    validation_reference_count: int
    release_quality_reference_count: int
    manifest_body_available: bool
    manifest_file_written: bool
    manifest_output_path_available: bool
    reason_codes: list[str]
    failed_checks: list[str]
    safety_flags: dict[str, bool]
    count_summary: dict[str, int]
    safe_summary: str
    runtime_writer_executed: bool
    release_quality_ready: bool

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "result_schema_version": self.result_schema_version,
            "writer_status": self.writer_status,
            "manifest_writer_mode": self.manifest_writer_mode,
            "manifest_id": self.manifest_id,
            "artifact_id": self.artifact_id,
            "artifact_body_id": self.artifact_body_id,
            "validation_reference_count": self.validation_reference_count,
            "release_quality_reference_count": self.release_quality_reference_count,
            "manifest_body_available": self.manifest_body_available,
            "manifest_file_written": self.manifest_file_written,
            "manifest_output_path_available": self.manifest_output_path_available,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "safety_flags": dict(self.safety_flags),
            "count_summary": dict(self.count_summary),
            "safe_summary": self.safe_summary,
            "runtime_writer_executed": self.runtime_writer_executed,
            "release_quality_ready": self.release_quality_ready,
        }


def load_manifest_writer_request(
    path: Path | str,
) -> ManifestWriterRequest | ManifestWriterError:
    payload = _read_json_object(Path(path), input_kind="request")
    if isinstance(payload, ManifestWriterError):
        return payload
    return _request_from_payload(payload)


def load_artifact_writer_result_pointer(
    path: Path | str,
) -> ArtifactWriterResultPointer | ManifestWriterError:
    payload = _read_json_object(Path(path), input_kind="artifact_result_pointer")
    if isinstance(payload, ManifestWriterError):
        return payload
    marker_reasons = _scan_payload_for_reasons(payload)
    marker_reasons.extend(_safe_sentinel_reason(payload.get("safe_violation_sentinel")))
    return ArtifactWriterResultPointer(
        schema_version=_safe_optional_string(payload.get("schema_version")),
        result_schema_version=_safe_optional_string(payload.get("result_schema_version")),
        pointer_id=_safe_optional_string(payload.get("pointer_id")),
        source_kind=_safe_optional_string(payload.get("source_kind")),
        source_fixture_id=_safe_optional_string(payload.get("source_fixture_id")),
        safe_metadata_reference_id=_safe_optional_string(
            payload.get("safe_metadata_reference_id")
        ),
        artifact_id=_safe_optional_string(payload.get("artifact_id")),
        manifest_id=_safe_optional_string(payload.get("manifest_id")),
        writer_status=_safe_optional_string(payload.get("writer_status")),
        artifact_body_available=payload.get("artifact_body_available") is True,
        include_body_payload=payload.get("include_body_payload") is True,
        include_raw_rows=payload.get("include_raw_rows") is True,
        include_private_paths=payload.get("include_private_paths") is True,
        synthetic_only_checked=payload.get("synthetic_only_checked") is True,
        no_oracle_checked=payload.get("no_oracle_checked") is True,
        safe_reference_only=payload.get("safe_reference_only") is True,
        marker_reason_codes=_dedupe(marker_reasons),
        missing_required_fields=_missing_fields(payload, REQUIRED_POINTER_FIELDS),
    )


def load_artifact_body_generation_result_pointer(
    path: Path | str,
) -> ArtifactBodyGenerationResultPointer | ManifestWriterError:
    payload = _read_json_object(Path(path), input_kind="artifact_body_result_pointer")
    if isinstance(payload, ManifestWriterError):
        return payload
    marker_reasons = _scan_payload_for_reasons(payload)
    marker_reasons.extend(_safe_sentinel_reason(payload.get("safe_violation_sentinel")))
    return ArtifactBodyGenerationResultPointer(
        schema_version=_safe_optional_string(payload.get("schema_version")),
        result_schema_version=_safe_optional_string(payload.get("result_schema_version")),
        pointer_id=_safe_optional_string(payload.get("pointer_id")),
        source_kind=_safe_optional_string(payload.get("source_kind")),
        source_fixture_id=_safe_optional_string(payload.get("source_fixture_id")),
        safe_metadata_reference_id=_safe_optional_string(
            payload.get("safe_metadata_reference_id")
        ),
        generation_status=_safe_optional_string(payload.get("generation_status")),
        artifact_body_status=_safe_optional_string(payload.get("artifact_body_status")),
        artifact_body_available=payload.get("artifact_body_available") is True,
        manifest_body_generated=payload.get("manifest_body_generated") is True,
        manifest_file_written=payload.get("manifest_file_written") is True,
        include_body_payload=payload.get("include_body_payload") is True,
        include_raw_rows=payload.get("include_raw_rows") is True,
        include_private_paths=payload.get("include_private_paths") is True,
        synthetic_only_checked=payload.get("synthetic_only_checked") is True,
        no_oracle_checked=payload.get("no_oracle_checked") is True,
        safe_reference_only=payload.get("safe_reference_only") is True,
        marker_reason_codes=_dedupe(marker_reasons),
        missing_required_fields=_missing_fields(payload, REQUIRED_POINTER_FIELDS),
    )


def build_metadata_only_manifest_result(
    request: ManifestWriterRequest,
    artifact_pointer: ArtifactWriterResultPointer,
    artifact_body_pointer: ArtifactBodyGenerationResultPointer,
) -> ManifestWriterResult:
    reason_codes = _dedupe(
        [
            *_reason_codes_for_request(request),
            *_reason_codes_for_artifact_pointer(artifact_pointer),
            *_reason_codes_for_artifact_body_pointer(artifact_body_pointer),
        ]
    )
    failed_checks = list(reason_codes)
    writer_status = "fail_closed" if reason_codes else "pass"
    count_summary = _count_summary_for_result(
        request,
        artifact_pointer,
        artifact_body_pointer,
    ).to_safe_dict()
    return ManifestWriterResult(
        mode="manifest_writer",
        result_schema_version=RESULT_SCHEMA_VERSION,
        writer_status=writer_status,
        manifest_writer_mode=request.manifest_writer_mode,
        manifest_id=artifact_pointer.manifest_id,
        artifact_id=artifact_pointer.artifact_id,
        artifact_body_id=artifact_body_pointer.safe_metadata_reference_id,
        validation_reference_count=count_summary["validation_reference_count"],
        release_quality_reference_count=count_summary[
            "release_quality_reference_count"
        ],
        manifest_body_available=False,
        manifest_file_written=False,
        manifest_output_path_available=False,
        reason_codes=reason_codes,
        failed_checks=failed_checks,
        safety_flags=dict(SAFETY_FLAGS),
        count_summary=count_summary,
        safe_summary=PASS_SAFE_SUMMARY if not reason_codes else FAIL_SAFE_SUMMARY,
        runtime_writer_executed=True,
        release_quality_ready=False,
    )


def audit_manifest_result_safety(result: ManifestWriterResult) -> ManifestWriterError:
    reason_codes: list[str] = []
    failed_checks: list[str] = []
    if result.manifest_body_available is not False:
        reason_codes.append("manifest_body_requested")
        failed_checks.append("manifest_body_available")
    if result.manifest_file_written is not False:
        reason_codes.append("unsafe_manifest_output_path")
        failed_checks.append("manifest_file_written")
    if result.manifest_output_path_available is not False:
        reason_codes.append("unsafe_manifest_output_path")
        failed_checks.append("manifest_output_path_available")
    for flag_name in SAFETY_FLAGS:
        if result.safety_flags.get(flag_name) is not True:
            reason_codes.append(_reason_for_safety_flag(flag_name))
            failed_checks.append(flag_name)
    for count_name in ZERO_COUNT_FIELDS:
        if result.count_summary.get(count_name) != 0:
            reason_codes.append(_reason_for_count_field(count_name))
            failed_checks.append(count_name)
    return ManifestWriterError(
        error_status="pass" if not reason_codes else "fail_closed",
        reason_codes=_dedupe(reason_codes),
        failed_checks=_dedupe(failed_checks),
        manifest_writer_mode=result.manifest_writer_mode,
        manifest_id=result.manifest_id,
        artifact_id=result.artifact_id,
        artifact_body_id=result.artifact_body_id,
        safe_summary=result.safe_summary,
    )


def summarize_manifest_writer_result(result: ManifestWriterResult) -> dict[str, Any]:
    return result.to_safe_dict()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the synthetic frozen policy generation manifest writer runtime "
            "with metadata-only no-file output."
        )
    )
    parser.add_argument("--request", type=Path, help="manifest_writer_request path.")
    parser.add_argument(
        "--artifact-result",
        type=Path,
        help="artifact_writer_result_pointer path.",
    )
    parser.add_argument(
        "--artifact-body-result",
        type=Path,
        help="artifact_body_generation_result_pointer path.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a safe JSON summary instead of a human summary.",
    )
    try:
        args, unknown = parser.parse_known_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 1

    if "--manifest-out" in unknown or any(
        item.startswith("--manifest-out=") for item in unknown
    ):
        result = _error_to_result(
            ManifestWriterError(
                error_status="usage_error",
                reason_codes=["manifest_out_not_supported"],
                failed_checks=["manifest_out"],
                safe_summary=USAGE_ERROR_SAFE_SUMMARY,
            )
        )
        _emit_cli_payload(result.to_safe_dict(), args.json)
        return 2
    if unknown:
        result = _error_to_result(
            ManifestWriterError(
                error_status="usage_error",
                reason_codes=["unknown_cli_argument"],
                failed_checks=["cli_arguments"],
                safe_summary=USAGE_ERROR_SAFE_SUMMARY,
            )
        )
        _emit_cli_payload(result.to_safe_dict(), args.json)
        return 2

    missing_cli_reasons = _missing_cli_argument_reasons(args)
    if missing_cli_reasons:
        result = _error_to_result(
            ManifestWriterError(
                error_status="usage_error",
                reason_codes=missing_cli_reasons,
                failed_checks=missing_cli_reasons,
                safe_summary=USAGE_ERROR_SAFE_SUMMARY,
            )
        )
        _emit_cli_payload(result.to_safe_dict(), args.json)
        return 2

    try:
        request = load_manifest_writer_request(args.request)
        artifact_pointer = load_artifact_writer_result_pointer(args.artifact_result)
        artifact_body_pointer = load_artifact_body_generation_result_pointer(
            args.artifact_body_result
        )
        result = run_manifest_writer(request, artifact_pointer, artifact_body_pointer)
        _emit_cli_payload(result.to_safe_dict(), args.json)
        if result.writer_status == "pass":
            return 0
        if result.writer_status == "usage_error":
            return 2
        if result.writer_status == "input_error":
            return 4
        return 3
    except Exception:
        result = _error_to_result(
            ManifestWriterError(
                error_status="input_error",
                reason_codes=["manifest_writer_internal_error"],
                failed_checks=["internal_error"],
                safe_summary=INPUT_ERROR_SAFE_SUMMARY,
            )
        )
        _emit_cli_payload(result.to_safe_dict(), args.json)
        return 1


def run_manifest_writer(
    request: ManifestWriterRequest | ManifestWriterError,
    artifact_pointer: ArtifactWriterResultPointer | ManifestWriterError,
    artifact_body_pointer: ArtifactBodyGenerationResultPointer | ManifestWriterError,
) -> ManifestWriterResult:
    if isinstance(request, ManifestWriterError):
        return _error_to_result(request)
    if isinstance(artifact_pointer, ManifestWriterError):
        return _error_to_result(artifact_pointer, request=request)
    if isinstance(artifact_body_pointer, ManifestWriterError):
        return _error_to_result(
            artifact_body_pointer,
            request=request,
            artifact_pointer=artifact_pointer,
        )
    result = build_metadata_only_manifest_result(
        request,
        artifact_pointer,
        artifact_body_pointer,
    )
    audit = audit_manifest_result_safety(result)
    if audit.reason_codes or audit.failed_checks:
        reason_codes = _dedupe([*result.reason_codes, *audit.reason_codes])
        failed_checks = _dedupe([*result.failed_checks, *audit.failed_checks])
        return ManifestWriterResult(
            **{
                **result.to_safe_dict(),
                "writer_status": "fail_closed",
                "reason_codes": reason_codes,
                "failed_checks": failed_checks,
                "safe_summary": FAIL_SAFE_SUMMARY,
            }
        )
    return result


def _request_from_payload(payload: dict[str, Any]) -> ManifestWriterRequest:
    marker_reasons = _scan_payload_for_reasons(payload)
    marker_reasons.extend(_safe_sentinel_reason(payload.get("safe_violation_sentinel")))
    return ManifestWriterRequest(
        schema_version=_safe_optional_string(payload.get("schema_version")),
        request_id=_safe_optional_string(payload.get("request_id")),
        manifest_writer_mode=_safe_optional_string(payload.get("manifest_writer_mode")),
        include_manifest_body=payload.get("include_manifest_body") is True,
        allow_manifest_file_writing=(
            payload.get("allow_manifest_file_writing") is True
        ),
        manifest_out=_safe_optional_string(payload.get("manifest_out")),
        overwrite_policy=_safe_optional_string(payload.get("overwrite_policy")),
        synthetic_notice=payload.get("synthetic_notice") is True,
        no_oracle_notice=payload.get("no_oracle_notice") is True,
        non_proof_notice=payload.get("non_proof_notice") is True,
        validation_reference_ids=_safe_string_list(
            payload.get("validation_reference_ids")
        ),
        release_quality_reference_ids=_safe_string_list(
            payload.get("release_quality_reference_ids")
        ),
        requested_artifact_writer_cli_integration=(
            payload.get("requested_artifact_writer_cli_integration") is True
        ),
        marker_reason_codes=_dedupe(marker_reasons),
        missing_required_fields=_missing_fields(payload, REQUIRED_REQUEST_FIELDS),
    )


def _reason_codes_for_request(request: ManifestWriterRequest) -> list[str]:
    reasons = list(request.marker_reason_codes)
    if request.schema_version != REQUEST_SCHEMA_VERSION:
        reasons.append("unknown_request_schema_version")
    if request.missing_required_fields:
        reasons.append("missing_required_field")
    if request.manifest_writer_mode != SUPPORTED_MODE:
        reasons.append("unsupported_manifest_writer_mode")
    if request.include_manifest_body is True:
        reasons.append("manifest_body_requested")
    if request.allow_manifest_file_writing is True:
        reasons.append("manifest_file_writing_not_supported")
    if request.manifest_out is not None:
        if request.overwrite_policy == "reject_existing":
            reasons.append("overwrite_without_policy")
        else:
            reasons.append("unsafe_manifest_output_path")
    if request.synthetic_notice is not True:
        reasons.append("missing_synthetic_notice")
    if request.no_oracle_notice is not True:
        reasons.append("missing_no_oracle_notice")
    if request.non_proof_notice is not True:
        reasons.append("missing_non_proof_notice")
    if request.requested_artifact_writer_cli_integration is True:
        reasons.append("unsupported_artifact_writer_cli_integration")
    return _dedupe(reasons)


def _reason_codes_for_artifact_pointer(
    pointer: ArtifactWriterResultPointer,
) -> list[str]:
    reasons = list(pointer.marker_reason_codes)
    if pointer.schema_version != ARTIFACT_WRITER_RESULT_POINTER_SCHEMA_VERSION:
        reasons.append("unknown_artifact_result_pointer_schema")
    if pointer.result_schema_version != ARTIFACT_WRITER_RESULT_SCHEMA_VERSION:
        reasons.append("unknown_artifact_writer_result_schema")
    if pointer.missing_required_fields:
        reasons.append("missing_artifact_result_pointer")
    if pointer.source_kind != "artifact_writer_result_summary":
        reasons.append("malformed_artifact_result_pointer")
    if pointer.include_body_payload is True:
        reasons.append("artifact_body_payload_leakage")
    if pointer.include_raw_rows is True:
        reasons.append("raw_rows_leakage")
    if pointer.include_private_paths is True:
        reasons.append("private_path_leakage")
    if pointer.synthetic_only_checked is not True:
        reasons.append("missing_synthetic_notice")
    if pointer.no_oracle_checked is not True:
        reasons.append("missing_no_oracle_notice")
    if pointer.safe_reference_only is not True:
        reasons.append("pointer_body_leakage")
    return _dedupe(reasons)


def _reason_codes_for_artifact_body_pointer(
    pointer: ArtifactBodyGenerationResultPointer,
) -> list[str]:
    reasons = list(pointer.marker_reason_codes)
    if pointer.schema_version != ARTIFACT_BODY_GENERATION_RESULT_POINTER_SCHEMA_VERSION:
        reasons.append("unknown_artifact_body_result_pointer_schema")
    if pointer.result_schema_version != ARTIFACT_BODY_GENERATION_RESULT_SCHEMA_VERSION:
        reasons.append("unknown_artifact_body_generation_result_schema")
    if pointer.missing_required_fields:
        reasons.append("missing_artifact_body_result_pointer")
    if pointer.source_kind != "artifact_body_generation_result_summary":
        reasons.append("malformed_artifact_body_result_pointer")
    if pointer.include_body_payload is True:
        reasons.append("artifact_body_payload_leakage")
    if pointer.include_raw_rows is True:
        reasons.append("raw_rows_leakage")
    if pointer.include_private_paths is True:
        if "absolute_path_leakage" not in reasons:
            reasons.append("private_path_leakage")
    if pointer.manifest_body_generated is True:
        reasons.append("manifest_body_requested")
    if pointer.manifest_file_written is True:
        reasons.append("unsafe_manifest_output_path")
    if pointer.synthetic_only_checked is not True:
        reasons.append("missing_synthetic_notice")
    if pointer.no_oracle_checked is not True:
        reasons.append("missing_no_oracle_notice")
    if pointer.safe_reference_only is not True:
        reasons.append("pointer_body_leakage")
    return _dedupe(reasons)


def _count_summary_for_result(
    request: ManifestWriterRequest,
    artifact_pointer: ArtifactWriterResultPointer,
    artifact_body_pointer: ArtifactBodyGenerationResultPointer,
) -> ManifestWriterCountSummary:
    validation_reference_count = len(request.validation_reference_ids)
    if request.release_quality_reference_ids and artifact_pointer.safe_metadata_reference_id:
        validation_reference_count += 1
    manifest_metadata_field_count = 12
    if artifact_body_pointer.safe_metadata_reference_id:
        manifest_metadata_field_count += 1
    return ManifestWriterCountSummary(
        manifest_metadata_field_count=manifest_metadata_field_count,
        validation_reference_count=validation_reference_count,
        release_quality_reference_count=len(request.release_quality_reference_ids),
    )


def _error_to_result(
    error: ManifestWriterError,
    *,
    request: ManifestWriterRequest | None = None,
    artifact_pointer: ArtifactWriterResultPointer | None = None,
    artifact_body_pointer: ArtifactBodyGenerationResultPointer | None = None,
) -> ManifestWriterResult:
    count_summary = _error_count_summary(request).to_safe_dict()
    return ManifestWriterResult(
        mode="manifest_writer",
        result_schema_version=RESULT_SCHEMA_VERSION,
        writer_status=error.error_status,
        manifest_writer_mode=error.manifest_writer_mode,
        manifest_id=error.manifest_id or (artifact_pointer.manifest_id if artifact_pointer else None),
        artifact_id=error.artifact_id or (artifact_pointer.artifact_id if artifact_pointer else None),
        artifact_body_id=error.artifact_body_id
        or (
            artifact_body_pointer.safe_metadata_reference_id
            if artifact_body_pointer
            else None
        ),
        validation_reference_count=count_summary["validation_reference_count"],
        release_quality_reference_count=count_summary[
            "release_quality_reference_count"
        ],
        manifest_body_available=False,
        manifest_file_written=False,
        manifest_output_path_available=False,
        reason_codes=list(error.reason_codes),
        failed_checks=list(error.failed_checks),
        safety_flags=dict(SAFETY_FLAGS),
        count_summary=count_summary,
        safe_summary=error.safe_summary,
        runtime_writer_executed=True,
        release_quality_ready=False,
    )


def _error_count_summary(
    request: ManifestWriterRequest | None,
) -> ManifestWriterCountSummary:
    return ManifestWriterCountSummary(
        manifest_metadata_field_count=0,
        validation_reference_count=(
            len(request.validation_reference_ids) if request is not None else 0
        ),
        release_quality_reference_count=(
            len(request.release_quality_reference_ids) if request is not None else 0
        ),
    )


def _read_json_object(
    path: Path,
    *,
    input_kind: str,
) -> dict[str, Any] | ManifestWriterError:
    try:
        with path.open(encoding="utf-8") as file:
            payload = json.load(file)
    except FileNotFoundError:
        return ManifestWriterError(
            error_status="input_error",
            reason_codes=[f"missing_{input_kind}_file"],
            failed_checks=[f"{input_kind}_file"],
            safe_summary=INPUT_ERROR_SAFE_SUMMARY,
        )
    except (OSError, json.JSONDecodeError):
        return ManifestWriterError(
            error_status="input_error",
            reason_codes=[f"malformed_{input_kind}"],
            failed_checks=[f"{input_kind}_json_parse"],
            safe_summary=INPUT_ERROR_SAFE_SUMMARY,
        )
    if not isinstance(payload, dict):
        return ManifestWriterError(
            error_status="input_error",
            reason_codes=[f"malformed_{input_kind}"],
            failed_checks=[f"{input_kind}_json_object"],
            safe_summary=INPUT_ERROR_SAFE_SUMMARY,
        )
    return payload


def _scan_payload_for_reasons(value: Any) -> list[str]:
    reasons: list[str] = []

    def visit(item: Any) -> None:
        if isinstance(item, dict):
            for key, nested in item.items():
                key_lower = str(key).lower()
                if key_lower in FORBIDDEN_PAYLOAD_KEY_REASONS:
                    reasons.append(FORBIDDEN_PAYLOAD_KEY_REASONS[key_lower])
                visit(nested)
        elif isinstance(item, list):
            for nested in item:
                visit(nested)
        elif isinstance(item, str):
            lowered = item.lower()
            if any(marker.lower() in lowered for marker in UNSAFE_PATH_MARKERS):
                if item.startswith(("/", "C:\\")):
                    reasons.append("absolute_path_leakage")
                else:
                    reasons.append("private_path_leakage")

    visit(value)
    return _dedupe(reasons)


def _safe_sentinel_reason(value: Any) -> list[str]:
    if isinstance(value, str) and value in SAFE_SENTINEL_REASON_CODES:
        return [value]
    if isinstance(value, list):
        return [item for item in value if item in SAFE_SENTINEL_REASON_CODES]
    return []


def _missing_cli_argument_reasons(args: argparse.Namespace) -> list[str]:
    reasons: list[str] = []
    if args.request is None:
        reasons.append("missing_request_path")
    if args.artifact_result is None:
        reasons.append("missing_artifact_pointer_path")
    if args.artifact_body_result is None:
        reasons.append("missing_artifact_body_pointer_path")
    return reasons


def _missing_fields(payload: dict[str, Any], required: tuple[str, ...]) -> list[str]:
    return [field_name for field_name in required if field_name not in payload]


def _safe_optional_string(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _safe_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _reason_for_safety_flag(flag_name: str) -> str:
    if flag_name in {
        "content_suppressed",
        "manifest_body_suppressed",
        "no_manifest_body_nesting",
    }:
        return "manifest_body_requested"
    if flag_name in {"no_raw_rows"}:
        return "raw_rows_leakage"
    if flag_name in {"no_logits_dump"}:
        return "logits_dump_leakage"
    if flag_name in {"no_private_paths"}:
        return "private_path_leakage"
    if flag_name in {"no_absolute_paths", "path_policy_checked"}:
        return "absolute_path_leakage"
    if flag_name in {"no_artifact_body_payload"}:
        return "artifact_body_payload_leakage"
    if flag_name in {"no_generated_policy_body"}:
        return "generated_policy_body_leakage"
    if flag_name in {"no_request_body"}:
        return "request_body_leakage"
    if flag_name in {"no_pointer_body"}:
        return "pointer_body_leakage"
    if flag_name in {"no_expected_body"}:
        return "expected_body_leakage"
    if flag_name in {"no_performance_claims"}:
        return "performance_claim"
    return "real_data_marker"


def _reason_for_count_field(count_name: str) -> str:
    return {
        "raw_row_count": "raw_rows_leakage",
        "logits_dump_count": "logits_dump_leakage",
        "private_path_count": "private_path_leakage",
        "absolute_path_count": "absolute_path_leakage",
        "artifact_body_payload_count": "artifact_body_payload_leakage",
        "generated_policy_body_count": "generated_policy_body_leakage",
        "manifest_body_count": "manifest_body_requested",
        "request_body_count": "request_body_leakage",
        "pointer_body_count": "pointer_body_leakage",
        "expected_body_count": "expected_body_leakage",
        "performance_metric_count": "performance_claim",
        "written_file_count": "unsafe_manifest_output_path",
    }.get(count_name, "real_data_marker")


def _emit_cli_payload(payload: dict[str, Any], json_output: bool) -> None:
    if json_output:
        print(json.dumps(payload, sort_keys=True))
        return
    for key in CLI_SAFE_SUMMARY_FIELDS:
        value = payload.get(key)
        if isinstance(value, bool):
            value_text = "true" if value else "false"
        elif isinstance(value, (list, tuple)):
            value_text = ",".join(str(item) for item in value) if value else "none"
        elif isinstance(value, dict):
            value_text = json.dumps(value, sort_keys=True, separators=(",", ":"))
        elif value is None:
            value_text = "none"
        else:
            value_text = str(value)
        print(f"{key}={value_text}")


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            result.append(value)
            seen.add(value)
    return result


if __name__ == "__main__":
    sys.exit(main())
