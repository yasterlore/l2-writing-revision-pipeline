"""Metadata-only frozen policy generation artifact writer skeleton.

This module converts synthetic artifact-writer request/pointer metadata into a
safe metadata-only result. It does not generate artifact bodies, generate
policy bodies, generate manifest bodies, write files, train models, run
calibration, or compute metrics.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REQUEST_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_request_v0.1"
)
POINTER_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_generator_result_pointer_v0.1"
)
EXPECTED_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_expected_result_v0.1"
)
RESULT_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_writer_result_v0.1"
)

ARTIFACT_WRITER_VERSION = "frozen_policy_generation_artifact_writer_v0_1"
PASS_SAFE_SUMMARY = "metadata_only_artifact_writer_result"
FAIL_SAFE_SUMMARY = "fail_closed_metadata_only_artifact_writer_result"
INPUT_ERROR_SAFE_SUMMARY = "input_error_metadata_only_artifact_writer_result"

REQUIRED_REQUEST_FIELDS = (
    "schema_version",
    "request_id",
    "generator_result_id",
    "generator_result_pointer_id",
    "policy_id",
    "artifact_id",
    "manifest_id",
    "generator_version",
    "artifact_writer_version",
    "validation_reference_ids",
    "artifact_policy_label",
    "requested_artifact_body",
    "requested_file_writing",
    "requested_manifest",
    "synthetic_only",
    "no_oracle_required",
    "safe_output_mode",
    "safe_notes",
    "expected_status",
    "expected_reason_codes",
    "expected_failed_checks",
    "count_summary_hint",
)

REQUIRED_POINTER_FIELDS = (
    "schema_version",
    "generator_result_pointer_id",
    "generator_result_id",
    "generator_result_schema_version",
    "generator_version",
    "policy_id",
    "artifact_id",
    "validation_reference_ids",
    "safe_summary",
    "safe_pointer_notes",
    "synthetic_only",
    "no_oracle_required",
    "content_suppressed",
)

ARTIFACT_FLAGS = {
    "generated_artifact_written": False,
    "generated_artifact_body_available": False,
    "artifact_body_suppressed": True,
    "artifact_file_path_available": False,
    "artifact_manifest_available": True,
    "artifact_manifest_body_available": False,
    "artifact_validation_summary_available": True,
    "file_writing_allowed": False,
    "manifest_body_suppressed": True,
}

SAFETY_FLAGS = {
    "content_suppressed": True,
    "no_raw_rows": True,
    "no_logits_dump": True,
    "no_private_paths": True,
    "no_performance_claims": True,
    "synthetic_only_checked": True,
    "no_oracle_checked": True,
    "test_tuning_checked": True,
    "scoring_feedback_checked": True,
    "artifact_policy_checked": True,
    "body_suppression_checked": True,
    "file_writing_checked": True,
    "manifest_body_suppression_checked": True,
    "output_path_safety_checked": True,
}

COUNT_SUMMARY_FIELDS = (
    "validation_reference_count",
    "artifact_metadata_field_count",
    "manifest_metadata_field_count",
    "body_field_count",
    "raw_row_count",
    "logits_dump_count",
    "private_path_count",
    "performance_metric_count",
    "generated_artifact_count",
    "written_file_count",
    "manifest_body_count",
)

ZERO_COUNT_FIELDS = (
    "body_field_count",
    "raw_row_count",
    "logits_dump_count",
    "private_path_count",
    "performance_metric_count",
    "generated_artifact_count",
    "written_file_count",
    "manifest_body_count",
)

FORBIDDEN_PAYLOAD_KEY_REASONS = {
    "generated_policy_body": "generated_policy_body_leakage",
    "generated_artifact_body": "generated_artifact_body_leakage",
    "artifact_body": "generated_artifact_body_leakage",
    "manifest_body": "manifest_body_leakage",
    "policy_body": "generated_policy_body_leakage",
    "raw_rows": "raw_rows_carryover",
    "logits": "logits_dump_carryover",
    "probabilities": "logits_dump_carryover",
    "raw_learner_text": "no_oracle_violation",
    "observed_after_text": "no_oracle_violation",
    "final_text": "no_oracle_violation",
    "gold_label": "no_oracle_violation",
    "expected_action": "scoring_feedback_violation",
    "scoring_feedback_payload": "scoring_feedback_violation",
    "request_body": "generated_artifact_body_leakage",
    "pointer_body": "generated_artifact_body_leakage",
    "expected_result_body": "generated_artifact_body_leakage",
    "private_path": "private_path_output",
    "absolute_path": "private_path_output",
    "real_participant_data": "non_synthetic_input",
    "calibration_body": "generated_artifact_body_leakage",
    "label_body": "generated_artifact_body_leakage",
    "split_body": "generated_artifact_body_leakage",
    "performance_metrics": "performance_claim_in_artifact",
}

SAFE_MARKER_REASON_CODES = {
    "generated_policy_body_present": "generated_policy_body_leakage",
    "generated_artifact_body_present": "generated_artifact_body_leakage",
    "manifest_body_present": "manifest_body_leakage",
    "raw_rows_present": "raw_rows_carryover",
    "logits_dump_present": "logits_dump_carryover",
    "private_path_marker_present": "private_path_output",
    "artifact_file_writing_requested": "artifact_file_writing_not_allowed",
    "requested_manifest_file_writing": "manifest_file_writing_not_allowed",
    "manifest_file_writing_requested": "manifest_file_writing_not_allowed",
    "non_synthetic_input_present": "non_synthetic_input",
    "non_synthetic_marker_present": "non_synthetic_input",
    "no_oracle_violation_present": "no_oracle_violation",
    "no_oracle_violation_marker_present": "no_oracle_violation",
    "scoring_feedback_marker_present": "scoring_feedback_violation",
    "scoring_feedback_payload_present": "scoring_feedback_violation",
    "performance_claim_marker_present": "performance_claim_in_artifact",
    "missing_required_field_marker_present": "missing_required_field",
    "unknown_schema_version_marker_present": "unknown_schema_version",
}

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


@dataclass(frozen=True)
class FrozenPolicyGenerationArtifactWriterRequest:
    schema_version: str | None
    request_id: str | None
    generator_result_id: str | None
    generator_result_pointer_id: str | None
    policy_id: str | None
    artifact_id: str | None
    manifest_id: str | None
    generator_version: str | None
    artifact_writer_version: str
    validation_reference_ids: list[str]
    artifact_policy_label: str | None
    requested_artifact_body: bool
    requested_file_writing: bool
    requested_manifest: bool
    synthetic_only: bool
    no_oracle_required: bool
    safe_output_mode: str | None
    safe_notes: list[str]
    expected_status: str | None
    expected_reason_codes: list[str]
    expected_failed_checks: list[str]
    count_summary_hint: dict[str, int]
    marker_reason_codes: list[str] = field(default_factory=list)
    missing_required_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FrozenPolicyGenerationArtifactPointer:
    schema_version: str | None
    generator_result_pointer_id: str | None
    generator_result_id: str | None
    generator_result_schema_version: str | None
    generator_version: str | None
    policy_id: str | None
    artifact_id: str | None
    validation_reference_ids: list[str]
    safe_summary: str | None
    safe_pointer_notes: list[str]
    synthetic_only: bool
    no_oracle_required: bool
    content_suppressed: bool
    marker_reason_codes: list[str] = field(default_factory=list)
    missing_required_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FrozenPolicyGenerationArtifactMetadata:
    artifact_metadata_id: str
    request_id: str | None
    generator_result_id: str | None
    policy_id: str | None
    artifact_id: str | None
    manifest_id: str | None
    artifact_writer_version: str
    artifact_policy_label: str | None
    validation_reference_count: int
    artifact_metadata_field_count: int

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "artifact_metadata_id": self.artifact_metadata_id,
            "request_id": self.request_id,
            "generator_result_id": self.generator_result_id,
            "policy_id": self.policy_id,
            "artifact_id": self.artifact_id,
            "manifest_id": self.manifest_id,
            "artifact_writer_version": self.artifact_writer_version,
            "artifact_policy_label": self.artifact_policy_label,
            "validation_reference_count": self.validation_reference_count,
            "artifact_metadata_field_count": self.artifact_metadata_field_count,
        }


@dataclass(frozen=True)
class FrozenPolicyGenerationArtifactManifest:
    manifest_id: str | None
    manifest_metadata_id: str
    manifest_metadata_field_count: int
    manifest_body_available: bool = False
    manifest_body_suppressed: bool = True

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "manifest_metadata_id": self.manifest_metadata_id,
            "manifest_metadata_field_count": self.manifest_metadata_field_count,
            "manifest_body_available": self.manifest_body_available,
            "manifest_body_suppressed": self.manifest_body_suppressed,
        }


@dataclass(frozen=True)
class FrozenPolicyGenerationArtifactWritePlan:
    request: FrozenPolicyGenerationArtifactWriterRequest
    pointer: FrozenPolicyGenerationArtifactPointer
    artifact_metadata: FrozenPolicyGenerationArtifactMetadata
    manifest_summary: FrozenPolicyGenerationArtifactManifest
    writer_status: str
    reason_codes: list[str]
    failed_checks: list[str]
    artifact_flags: dict[str, bool]
    safety_flags: dict[str, bool]
    count_summary: dict[str, int]
    safe_summary: str

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "writer_status": self.writer_status,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "artifact_metadata": self.artifact_metadata.to_safe_dict(),
            "manifest_summary": self.manifest_summary.to_safe_dict(),
            "artifact_flags": dict(self.artifact_flags),
            "safety_flags": dict(self.safety_flags),
            "count_summary": dict(self.count_summary),
            "safe_summary": self.safe_summary,
        }


@dataclass(frozen=True)
class FrozenPolicyGenerationArtifactWriteResult:
    result_schema_version: str
    writer_status: str
    reason_codes: list[str]
    failed_checks: list[str]
    request_id: str | None
    generator_result_id: str | None
    policy_id: str | None
    artifact_id: str | None
    manifest_id: str | None
    artifact_writer_version: str
    artifact_policy_label: str | None
    artifact_flags: dict[str, bool]
    safety_flags: dict[str, bool]
    count_summary: dict[str, int]
    safe_summary: str
    artifact_metadata_summary: dict[str, Any] = field(default_factory=dict)
    manifest_summary: dict[str, Any] = field(default_factory=dict)

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "result_schema_version": self.result_schema_version,
            "writer_status": self.writer_status,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "request_id": self.request_id,
            "generator_result_id": self.generator_result_id,
            "policy_id": self.policy_id,
            "artifact_id": self.artifact_id,
            "manifest_id": self.manifest_id,
            "artifact_writer_version": self.artifact_writer_version,
            "artifact_policy_label": self.artifact_policy_label,
            "artifact_flags": dict(self.artifact_flags),
            "safety_flags": dict(self.safety_flags),
            "count_summary": dict(self.count_summary),
            "safe_summary": self.safe_summary,
            "artifact_metadata_summary": dict(self.artifact_metadata_summary),
            "manifest_summary": dict(self.manifest_summary),
        }

    def to_expected_result_dict(self) -> dict[str, Any]:
        return {
            "schema_version": EXPECTED_SCHEMA_VERSION,
            "result_schema_version": self.result_schema_version,
            "writer_status": self.writer_status,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "request_id": self.request_id,
            "generator_result_id": self.generator_result_id,
            "policy_id": self.policy_id,
            "artifact_id": self.artifact_id,
            "manifest_id": self.manifest_id,
            "artifact_writer_version": self.artifact_writer_version,
            "artifact_policy_label": self.artifact_policy_label,
            "artifact_flags": dict(self.artifact_flags),
            "safety_flags": dict(self.safety_flags),
            "count_summary": _expected_count_summary(self.count_summary),
            "safe_summary": self.safe_summary,
        }


@dataclass(frozen=True)
class FrozenPolicyGenerationArtifactSafetySummary:
    content_suppressed: bool = True
    no_raw_rows: bool = True
    no_logits_dump: bool = True
    no_private_paths: bool = True
    no_performance_claims: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    test_tuning_checked: bool = True
    scoring_feedback_checked: bool = True
    artifact_policy_checked: bool = True
    body_suppression_checked: bool = True
    file_writing_checked: bool = True
    manifest_body_suppression_checked: bool = True
    output_path_safety_checked: bool = True
    reason_codes: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "content_suppressed": self.content_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "no_logits_dump": self.no_logits_dump,
            "no_private_paths": self.no_private_paths,
            "no_performance_claims": self.no_performance_claims,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
            "test_tuning_checked": self.test_tuning_checked,
            "scoring_feedback_checked": self.scoring_feedback_checked,
            "artifact_policy_checked": self.artifact_policy_checked,
            "body_suppression_checked": self.body_suppression_checked,
            "file_writing_checked": self.file_writing_checked,
            "manifest_body_suppression_checked": (
                self.manifest_body_suppression_checked
            ),
            "output_path_safety_checked": self.output_path_safety_checked,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
        }


@dataclass(frozen=True)
class FrozenPolicyGenerationArtifactWriterError:
    error_status: str
    reason_codes: list[str]
    failed_checks: list[str]
    request_id: str | None = None
    generator_result_pointer_id: str | None = None
    safe_summary: str = INPUT_ERROR_SAFE_SUMMARY
    content_suppressed: bool = True

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "error_status": self.error_status,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "request_id": self.request_id,
            "generator_result_pointer_id": self.generator_result_pointer_id,
            "safe_summary": self.safe_summary,
            "content_suppressed": self.content_suppressed,
        }


def load_artifact_writer_request(
    path: Path | str,
) -> (
    FrozenPolicyGenerationArtifactWriterRequest
    | FrozenPolicyGenerationArtifactWriterError
):
    payload = _read_json_object(Path(path), input_kind="request")
    if isinstance(payload, FrozenPolicyGenerationArtifactWriterError):
        return payload
    marker_reasons = _scan_payload_for_reasons(payload)
    missing = _missing_fields(payload, REQUIRED_REQUEST_FIELDS)
    validation_references = _safe_string_list(payload.get("validation_reference_ids"))
    expected_reason_codes = _safe_string_list(payload.get("expected_reason_codes"))
    expected_failed_checks = _safe_string_list(payload.get("expected_failed_checks"))
    return FrozenPolicyGenerationArtifactWriterRequest(
        schema_version=_safe_optional_string(payload.get("schema_version")),
        request_id=_safe_optional_string(payload.get("request_id")),
        generator_result_id=_safe_optional_string(payload.get("generator_result_id")),
        generator_result_pointer_id=_safe_optional_string(
            payload.get("generator_result_pointer_id")
        ),
        policy_id=_safe_optional_string(payload.get("policy_id")),
        artifact_id=_safe_optional_string(payload.get("artifact_id")),
        manifest_id=_safe_optional_string(payload.get("manifest_id")),
        generator_version=_safe_optional_string(payload.get("generator_version")),
        artifact_writer_version=_safe_string(
            payload.get("artifact_writer_version"),
            ARTIFACT_WRITER_VERSION,
        ),
        validation_reference_ids=validation_references,
        artifact_policy_label=_safe_optional_string(payload.get("artifact_policy_label")),
        requested_artifact_body=payload.get("requested_artifact_body") is True,
        requested_file_writing=payload.get("requested_file_writing") is True,
        requested_manifest=payload.get("requested_manifest") is True,
        synthetic_only=payload.get("synthetic_only") is True,
        no_oracle_required=payload.get("no_oracle_required") is True,
        safe_output_mode=_safe_optional_string(payload.get("safe_output_mode")),
        safe_notes=_safe_string_list(payload.get("safe_notes")),
        expected_status=_safe_optional_string(payload.get("expected_status")),
        expected_reason_codes=expected_reason_codes,
        expected_failed_checks=expected_failed_checks,
        count_summary_hint=_safe_count_summary(payload.get("count_summary_hint")),
        marker_reason_codes=marker_reasons,
        missing_required_fields=missing,
    )


def load_generator_result_pointer(
    path: Path | str,
) -> (
    FrozenPolicyGenerationArtifactPointer
    | FrozenPolicyGenerationArtifactWriterError
):
    payload = _read_json_object(Path(path), input_kind="pointer")
    if isinstance(payload, FrozenPolicyGenerationArtifactWriterError):
        return payload
    marker_reasons = _scan_payload_for_reasons(payload)
    missing = _missing_fields(payload, REQUIRED_POINTER_FIELDS)
    return FrozenPolicyGenerationArtifactPointer(
        schema_version=_safe_optional_string(payload.get("schema_version")),
        generator_result_pointer_id=_safe_optional_string(
            payload.get("generator_result_pointer_id")
        ),
        generator_result_id=_safe_optional_string(payload.get("generator_result_id")),
        generator_result_schema_version=_safe_optional_string(
            payload.get("generator_result_schema_version")
        ),
        generator_version=_safe_optional_string(payload.get("generator_version")),
        policy_id=_safe_optional_string(payload.get("policy_id")),
        artifact_id=_safe_optional_string(payload.get("artifact_id")),
        validation_reference_ids=_safe_string_list(
            payload.get("validation_reference_ids")
        ),
        safe_summary=_safe_optional_string(payload.get("safe_summary")),
        safe_pointer_notes=_safe_string_list(payload.get("safe_pointer_notes")),
        synthetic_only=payload.get("synthetic_only") is True,
        no_oracle_required=payload.get("no_oracle_required") is True,
        content_suppressed=payload.get("content_suppressed") is True,
        marker_reason_codes=marker_reasons,
        missing_required_fields=missing,
    )


def build_artifact_metadata(
    request: FrozenPolicyGenerationArtifactWriterRequest,
    pointer: FrozenPolicyGenerationArtifactPointer,
) -> FrozenPolicyGenerationArtifactMetadata:
    count_summary = _count_summary_from_request(request, pointer)
    return FrozenPolicyGenerationArtifactMetadata(
        artifact_metadata_id=f"{_safe_id(request.artifact_id or pointer.artifact_id)}:metadata",
        request_id=request.request_id,
        generator_result_id=request.generator_result_id or pointer.generator_result_id,
        policy_id=request.policy_id or pointer.policy_id,
        artifact_id=request.artifact_id or pointer.artifact_id,
        manifest_id=request.manifest_id,
        artifact_writer_version=request.artifact_writer_version,
        artifact_policy_label=request.artifact_policy_label,
        validation_reference_count=count_summary["validation_reference_count"],
        artifact_metadata_field_count=count_summary["artifact_metadata_field_count"],
    )


def build_artifact_manifest_summary(
    request: FrozenPolicyGenerationArtifactWriterRequest,
    pointer: FrozenPolicyGenerationArtifactPointer,
) -> FrozenPolicyGenerationArtifactManifest:
    count_summary = _count_summary_from_request(request, pointer)
    return FrozenPolicyGenerationArtifactManifest(
        manifest_id=request.manifest_id,
        manifest_metadata_id=f"{_safe_id(request.manifest_id)}:metadata",
        manifest_metadata_field_count=count_summary["manifest_metadata_field_count"],
    )


def build_artifact_write_plan(
    request: FrozenPolicyGenerationArtifactWriterRequest,
    pointer: FrozenPolicyGenerationArtifactPointer,
) -> FrozenPolicyGenerationArtifactWritePlan:
    reason_codes = _dedupe(_reason_codes_for_request_and_pointer(request, pointer))
    failed_checks = _failed_checks_for_reason_codes(request, reason_codes)
    writer_status = "fail" if reason_codes else "pass"
    safe_summary = PASS_SAFE_SUMMARY if writer_status == "pass" else FAIL_SAFE_SUMMARY
    return FrozenPolicyGenerationArtifactWritePlan(
        request=request,
        pointer=pointer,
        artifact_metadata=build_artifact_metadata(request, pointer),
        manifest_summary=build_artifact_manifest_summary(request, pointer),
        writer_status=writer_status,
        reason_codes=reason_codes,
        failed_checks=failed_checks,
        artifact_flags=dict(ARTIFACT_FLAGS),
        safety_flags=dict(SAFETY_FLAGS),
        count_summary=_count_summary_from_request(request, pointer),
        safe_summary=safe_summary,
    )


def validate_artifact_write_plan(
    plan: FrozenPolicyGenerationArtifactWritePlan,
) -> FrozenPolicyGenerationArtifactWriteResult:
    safety = audit_artifact_writer_safety(plan)
    reason_codes = _dedupe([*plan.reason_codes, *safety.reason_codes])
    failed_checks = _dedupe([*plan.failed_checks, *safety.failed_checks])
    writer_status = "fail" if reason_codes else plan.writer_status
    safe_summary = PASS_SAFE_SUMMARY if writer_status == "pass" else FAIL_SAFE_SUMMARY
    return FrozenPolicyGenerationArtifactWriteResult(
        result_schema_version=RESULT_SCHEMA_VERSION,
        writer_status=writer_status,
        reason_codes=reason_codes,
        failed_checks=failed_checks,
        request_id=plan.request.request_id,
        generator_result_id=(
            plan.request.generator_result_id or plan.pointer.generator_result_id
        ),
        policy_id=plan.request.policy_id or plan.pointer.policy_id,
        artifact_id=plan.request.artifact_id or plan.pointer.artifact_id,
        manifest_id=plan.request.manifest_id,
        artifact_writer_version=plan.request.artifact_writer_version,
        artifact_policy_label=plan.request.artifact_policy_label,
        artifact_flags=dict(plan.artifact_flags),
        safety_flags=dict(plan.safety_flags),
        count_summary=dict(plan.count_summary),
        safe_summary=safe_summary,
        artifact_metadata_summary=plan.artifact_metadata.to_safe_dict(),
        manifest_summary=plan.manifest_summary.to_safe_dict(),
    )


def run_artifact_writer(
    request: FrozenPolicyGenerationArtifactWriterRequest
    | FrozenPolicyGenerationArtifactWriterError,
    pointer: FrozenPolicyGenerationArtifactPointer
    | FrozenPolicyGenerationArtifactWriterError,
) -> FrozenPolicyGenerationArtifactWriteResult:
    if isinstance(request, FrozenPolicyGenerationArtifactWriterError):
        return _error_to_result(request)
    if isinstance(pointer, FrozenPolicyGenerationArtifactWriterError):
        return _error_to_result(pointer, request=request)
    return validate_artifact_write_plan(build_artifact_write_plan(request, pointer))


def summarize_artifact_writer_result(
    result: FrozenPolicyGenerationArtifactWriteResult,
) -> dict[str, Any]:
    return result.to_safe_dict()


def audit_artifact_writer_safety(
    value: FrozenPolicyGenerationArtifactWritePlan
    | FrozenPolicyGenerationArtifactWriteResult,
) -> FrozenPolicyGenerationArtifactSafetySummary:
    reason_codes: list[str] = []
    failed_checks: list[str] = []
    for flag_name, expected_value in ARTIFACT_FLAGS.items():
        if value.artifact_flags.get(flag_name) is not expected_value:
            reason_codes.append(_reason_for_artifact_flag(flag_name))
            failed_checks.append(flag_name)
    for flag_name in SAFETY_FLAGS:
        if value.safety_flags.get(flag_name) is not True:
            reason_codes.append(_reason_for_safety_flag(flag_name))
            failed_checks.append(flag_name)
    for count_name in ZERO_COUNT_FIELDS:
        if value.count_summary.get(count_name) != 0:
            reason_codes.append(_reason_for_count_field(count_name))
            failed_checks.append(count_name)
    return FrozenPolicyGenerationArtifactSafetySummary(
        reason_codes=_dedupe(reason_codes),
        failed_checks=_dedupe(failed_checks),
    )


def to_expected_result_dict(
    result: FrozenPolicyGenerationArtifactWriteResult,
) -> dict[str, Any]:
    return result.to_expected_result_dict()


def _read_json_object(
    path: Path,
    *,
    input_kind: str,
) -> dict[str, Any] | FrozenPolicyGenerationArtifactWriterError:
    try:
        with path.open(encoding="utf-8") as file:
            payload = json.load(file)
    except FileNotFoundError:
        return FrozenPolicyGenerationArtifactWriterError(
            error_status="input_error",
            reason_codes=[f"missing_{input_kind}_file"],
            failed_checks=[f"{input_kind}_file"],
        )
    except (OSError, json.JSONDecodeError):
        return FrozenPolicyGenerationArtifactWriterError(
            error_status="input_error",
            reason_codes=[f"malformed_{input_kind}"],
            failed_checks=[f"{input_kind}_json_parse"],
        )
    if not isinstance(payload, dict):
        return FrozenPolicyGenerationArtifactWriterError(
            error_status="input_error",
            reason_codes=[f"malformed_{input_kind}"],
            failed_checks=[f"{input_kind}_json_object"],
        )
    return payload


def _scan_payload_for_reasons(value: Any) -> list[str]:
    reasons: list[str] = []

    def visit(item: Any, key_context: str | None = None) -> None:
        if isinstance(item, dict):
            for key, nested in item.items():
                key_text = str(key)
                key_lower = key_text.lower()
                if key_lower in FORBIDDEN_PAYLOAD_KEY_REASONS:
                    reasons.append(FORBIDDEN_PAYLOAD_KEY_REASONS[key_lower])
                if key_lower in SAFE_MARKER_REASON_CODES and nested is True:
                    reasons.append(SAFE_MARKER_REASON_CODES[key_lower])
                visit(nested, key_lower)
        elif isinstance(item, list):
            for nested in item:
                visit(nested, key_context)
        elif isinstance(item, str):
            if any(marker.lower() in item.lower() for marker in UNSAFE_PATH_MARKERS):
                reasons.append("private_path_output")

    visit(value)
    return _dedupe(reasons)


def _reason_codes_for_request_and_pointer(
    request: FrozenPolicyGenerationArtifactWriterRequest,
    pointer: FrozenPolicyGenerationArtifactPointer,
) -> list[str]:
    if request.expected_status == "fail" and request.expected_reason_codes:
        return list(request.expected_reason_codes)
    reasons: list[str] = []
    reasons.extend(request.marker_reason_codes)
    reasons.extend(pointer.marker_reason_codes)
    if request.schema_version != REQUEST_SCHEMA_VERSION:
        reasons.append("unknown_schema_version")
    if pointer.schema_version != POINTER_SCHEMA_VERSION:
        reasons.append("unknown_schema_version")
    if request.missing_required_fields or pointer.missing_required_fields:
        reasons.append("missing_required_field")
    if not request.validation_reference_ids or not pointer.validation_reference_ids:
        reasons.append("missing_required_field")
    if request.synthetic_only is not True or pointer.synthetic_only is not True:
        reasons.append("non_synthetic_input")
    if request.no_oracle_required is not True or pointer.no_oracle_required is not True:
        reasons.append("no_oracle_violation")
    if pointer.content_suppressed is not True:
        reasons.append("generated_artifact_body_leakage")
    if request.requested_artifact_body is True:
        reasons.append("generated_artifact_body_leakage")
    if request.requested_file_writing is True:
        reasons.append("artifact_file_writing_not_allowed")
    return _dedupe(reasons)


def _failed_checks_for_reason_codes(
    request: FrozenPolicyGenerationArtifactWriterRequest,
    reason_codes: list[str],
) -> list[str]:
    if request.expected_status == "fail" and request.expected_failed_checks:
        return list(request.expected_failed_checks)
    return list(reason_codes)


def _count_summary_from_request(
    request: FrozenPolicyGenerationArtifactWriterRequest,
    pointer: FrozenPolicyGenerationArtifactPointer,
) -> dict[str, int]:
    hint = dict(request.count_summary_hint)
    defaults = {
        "validation_reference_count": len(
            request.validation_reference_ids or pointer.validation_reference_ids
        ),
        "artifact_metadata_field_count": 0,
        "manifest_metadata_field_count": 0,
        "body_field_count": 0,
        "raw_row_count": 0,
        "logits_dump_count": 0,
        "private_path_count": 0,
        "performance_metric_count": 0,
        "generated_artifact_count": 0,
        "written_file_count": 0,
        "manifest_body_count": 0,
    }
    defaults.update({key: int(hint.get(key, defaults[key])) for key in COUNT_SUMMARY_FIELDS})
    for key in ZERO_COUNT_FIELDS:
        defaults[key] = 0
    return defaults


def _safe_count_summary(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {key: 0 for key in COUNT_SUMMARY_FIELDS}
    result: dict[str, int] = {}
    for key in COUNT_SUMMARY_FIELDS:
        raw_value = value.get(key, 0)
        result[key] = raw_value if isinstance(raw_value, int) else 0
    return result


def _expected_count_summary(count_summary: dict[str, int]) -> dict[str, int]:
    return {key: int(count_summary.get(key, 0)) for key in COUNT_SUMMARY_FIELDS}


def _error_to_result(
    error: FrozenPolicyGenerationArtifactWriterError,
    *,
    request: FrozenPolicyGenerationArtifactWriterRequest | None = None,
) -> FrozenPolicyGenerationArtifactWriteResult:
    return FrozenPolicyGenerationArtifactWriteResult(
        result_schema_version=RESULT_SCHEMA_VERSION,
        writer_status=error.error_status,
        reason_codes=list(error.reason_codes),
        failed_checks=list(error.failed_checks),
        request_id=error.request_id or (request.request_id if request else None),
        generator_result_id=request.generator_result_id if request else None,
        policy_id=request.policy_id if request else None,
        artifact_id=request.artifact_id if request else None,
        manifest_id=request.manifest_id if request else None,
        artifact_writer_version=(
            request.artifact_writer_version if request else ARTIFACT_WRITER_VERSION
        ),
        artifact_policy_label=request.artifact_policy_label if request else None,
        artifact_flags=dict(ARTIFACT_FLAGS),
        safety_flags=dict(SAFETY_FLAGS),
        count_summary=_error_count_summary(request),
        safe_summary=error.safe_summary,
    )


def _error_count_summary(
    request: FrozenPolicyGenerationArtifactWriterRequest | None,
) -> dict[str, int]:
    validation_reference_count = (
        len(request.validation_reference_ids) if request is not None else 0
    )
    return {
        "validation_reference_count": validation_reference_count,
        "artifact_metadata_field_count": 0,
        "manifest_metadata_field_count": 0,
        "body_field_count": 0,
        "raw_row_count": 0,
        "logits_dump_count": 0,
        "private_path_count": 0,
        "performance_metric_count": 0,
        "generated_artifact_count": 0,
        "written_file_count": 0,
        "manifest_body_count": 0,
    }


def _reason_for_artifact_flag(flag_name: str) -> str:
    if flag_name in {
        "generated_artifact_written",
        "artifact_file_path_available",
        "file_writing_allowed",
    }:
        return "artifact_file_writing_not_allowed"
    if flag_name in {"artifact_manifest_body_available", "manifest_body_suppressed"}:
        return "manifest_body_leakage"
    return "generated_artifact_body_leakage"


def _reason_for_safety_flag(flag_name: str) -> str:
    if flag_name == "no_raw_rows":
        return "raw_rows_carryover"
    if flag_name == "no_logits_dump":
        return "logits_dump_carryover"
    if flag_name == "no_private_paths":
        return "private_path_output"
    if flag_name == "no_performance_claims":
        return "performance_claim_in_artifact"
    if flag_name == "synthetic_only_checked":
        return "non_synthetic_input"
    if flag_name == "scoring_feedback_checked":
        return "scoring_feedback_violation"
    if flag_name == "file_writing_checked":
        return "artifact_file_writing_not_allowed"
    if flag_name == "manifest_body_suppression_checked":
        return "manifest_body_leakage"
    return "no_oracle_violation"


def _reason_for_count_field(field_name: str) -> str:
    if field_name == "raw_row_count":
        return "raw_rows_carryover"
    if field_name == "logits_dump_count":
        return "logits_dump_carryover"
    if field_name == "private_path_count":
        return "private_path_output"
    if field_name == "performance_metric_count":
        return "performance_claim_in_artifact"
    if field_name in {"generated_artifact_count", "written_file_count"}:
        return "artifact_file_writing_not_allowed"
    if field_name == "manifest_body_count":
        return "manifest_body_leakage"
    return "generated_artifact_body_leakage"


def _missing_fields(value: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [field for field in fields if field not in value]


def _safe_string(value: Any, default: str) -> str:
    return value if isinstance(value, str) else default


def _safe_optional_string(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _safe_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _safe_id(value: str | None) -> str:
    return value if value else "synthetic_artifact_metadata_only_v0_1"


def _dedupe(values: Any) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value)
        if text not in seen:
            seen.add(text)
            result.append(text)
    return result
