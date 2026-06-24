"""Safe metadata-only artifact body generation.

This module implements the first artifact body generation boundary for frozen
policy generation artifacts. It only builds synthetic metadata bodies. It does
not include learner text, raw rows, logits, private paths, performance metrics,
request or pointer bodies, generated policy bodies, manifest bodies, or file
writing.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Mapping

ARTIFACT_BODY_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_v0.1"
)
ARTIFACT_BODY_GENERATION_RESULT_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_generation_result_v0.1"
)
ARTIFACT_BODY_REQUEST_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_request_v0.1"
)
ARTIFACT_WRITER_RESULT_POINTER_SCHEMA_VERSION = (
    "learner_state_frozen_policy_generation_artifact_body_writer_result_pointer_v0.1"
)

DEFAULT_WRITER_VERSION = "frozen_policy_generation_artifact_body_v0_1"
SUPPRESSED_SAFE_SUMMARY = "suppressed_metadata_only_artifact_body_result"
GENERATED_SAFE_SUMMARY = "generated_safe_metadata_artifact_body_result"
FAIL_CLOSED_SAFE_SUMMARY = "fail_closed_metadata_only_artifact_body_result"

BODY_STATUS_SUPPRESSED = "suppressed_metadata_only"
BODY_STATUS_GENERATED_SAFE = "generated_safe_metadata_body"
BODY_STATUS_FAIL_CLOSED = "fail_closed"

ALLOWED_BODY_FIELDS = frozenset(
    {
        "artifact_body_schema_version",
        "artifact_id",
        "manifest_id",
        "writer_version",
        "body_type",
        "body_status",
        "content_suppressed",
        "synthetic_only_notice",
        "no_oracle_notice",
        "allowed_sections",
        "safety_summary",
        "count_summary",
        "validation_references",
        "non_proof_notice",
        "reason_codes",
        "failed_checks",
        "safe_metadata_field_names",
        "created_by_version",
        "body_suppression_policy",
        "file_writing_policy",
    }
)

DEFAULT_ALLOWED_SECTIONS = (
    "schema_version",
    "safe_ids",
    "validation_references",
    "safety_summary",
    "count_summary",
)

SAFETY_FLAG_FIELDS = (
    "content_suppressed",
    "no_raw_rows",
    "no_logits_dump",
    "no_private_paths",
    "no_performance_claims",
    "synthetic_only_checked",
    "no_oracle_checked",
    "artifact_policy_checked",
    "body_suppression_checked",
    "artifact_body_audit_checked",
)

COUNT_SUMMARY_FIELDS = (
    "body_field_count",
    "raw_row_count",
    "logits_dump_count",
    "private_path_count",
    "performance_metric_count",
    "request_body_count",
    "pointer_body_count",
    "expected_body_count",
    "manifest_body_count",
    "validation_reference_count",
)

ZERO_COUNT_FIELDS = (
    "raw_row_count",
    "logits_dump_count",
    "private_path_count",
    "performance_metric_count",
    "request_body_count",
    "pointer_body_count",
    "expected_body_count",
    "manifest_body_count",
)

FORBIDDEN_KEY_REASONS = {
    "raw_learner_text": "raw_learner_text_in_artifact_body",
    "raw_event_rows": "raw_rows_in_artifact_body",
    "revision_event_raw_rows": "raw_rows_in_artifact_body",
    "micro_episode_raw_rows": "raw_rows_in_artifact_body",
    "raw_rows": "raw_rows_in_artifact_body",
    "logits": "logits_dump_in_artifact_body",
    "probabilities": "logits_dump_in_artifact_body",
    "model_scores": "logits_dump_in_artifact_body",
    "private_path": "private_path_in_artifact_body",
    "absolute_path": "private_path_in_artifact_body",
    "performance_metrics": "performance_claim_in_artifact_body",
    "performance_metric_body": "performance_claim_in_artifact_body",
    "request_body": "request_body_leakage",
    "artifact_writer_request_json_body": "request_body_leakage",
    "pointer_body": "pointer_body_leakage",
    "generator_result_pointer_json_body": "pointer_body_leakage",
    "expected_body": "expected_result_body_leakage",
    "expected_result_body": "expected_result_body_leakage",
    "expected_artifact_writer_result_json_body": "expected_result_body_leakage",
    "generated_policy_body": "generated_policy_body_leakage",
    "frozen_policy_body": "generated_policy_body_leakage",
    "policy_body": "generated_policy_body_leakage",
    "manifest_body": "manifest_body_leakage",
    "observed_after_text": "raw_learner_text_in_artifact_body",
    "final_text": "raw_learner_text_in_artifact_body",
    "gold_label": "raw_learner_text_in_artifact_body",
    "expected_action_payload": "request_body_leakage",
    "expected_action": "request_body_leakage",
    "scoring_feedback_payload": "request_body_leakage",
    "real_participant_metadata": "raw_learner_text_in_artifact_body",
    "github_raw_logs": "raw_learner_text_in_artifact_body",
    "full_job_output": "raw_learner_text_in_artifact_body",
}

SAFE_MARKER_REASON_CODES = {
    "raw_learner_text_marker_present": "raw_learner_text_in_artifact_body",
    "raw_rows_marker_present": "raw_rows_in_artifact_body",
    "logits_dump_marker_present": "logits_dump_in_artifact_body",
    "private_path_marker_present": "private_path_in_artifact_body",
    "performance_claim_marker_present": "performance_claim_in_artifact_body",
    "request_body_marker_present": "request_body_leakage",
    "pointer_body_marker_present": "pointer_body_leakage",
    "expected_result_body_marker_present": "expected_result_body_leakage",
    "generated_policy_body_marker_present": "generated_policy_body_leakage",
    "manifest_body_marker_present": "manifest_body_leakage",
    "unsafe_schema_marker_present": "unsafe_artifact_body_schema",
    "missing_synthetic_notice_marker_present": "missing_synthetic_notice",
    "missing_no_oracle_notice_marker_present": "missing_no_oracle_notice",
    "unknown_schema_version_marker_present": "unknown_artifact_body_schema_version",
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
)

RAW_LOG_MARKERS = (
    "::group::",
    "::endgroup::",
    "##[group]",
    "##[endgroup]",
    "github actions raw log",
    "full job output",
)

LOCAL_ABSOLUTE_PATH_PATTERN = re.compile(
    r"(^/Users/|^/home/|^/private/|^/var/folders/|^[A-Za-z]:\\)"
)


@dataclass(frozen=True)
class ArtifactBodyGenerationRequest:
    schema_version: str | None
    case_id: str | None
    artifact_body_id: str | None
    artifact_id: str | None
    manifest_id: str | None
    writer_version: str
    requested_body_mode: str
    requested_body_status: str
    synthetic_only_notice_present: bool
    no_oracle_notice_present: bool
    validation_reference_ids: list[str]
    safe_section_keys: list[str]
    safe_marker_flags: dict[str, bool]
    marker_reason_codes: list[str] = field(default_factory=list)
    missing_required_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ArtifactBodyWriterResultPointer:
    schema_version: str | None
    writer_result_pointer_id: str | None
    writer_status: str | None
    artifact_id: str | None
    manifest_id: str | None
    validation_reference_ids: list[str]
    content_suppressed: bool
    no_raw_rows: bool
    no_logits_dump: bool
    no_private_paths: bool
    no_performance_claims: bool
    generated_artifact_written: bool
    artifact_body_suppressed: bool
    manifest_body_suppressed: bool
    marker_reason_codes: list[str] = field(default_factory=list)
    missing_required_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ArtifactBodyCountSummary:
    body_field_count: int = 0
    raw_row_count: int = 0
    logits_dump_count: int = 0
    private_path_count: int = 0
    performance_metric_count: int = 0
    request_body_count: int = 0
    pointer_body_count: int = 0
    expected_body_count: int = 0
    manifest_body_count: int = 0
    validation_reference_count: int = 0

    def to_safe_dict(self) -> dict[str, int]:
        return {field_name: int(getattr(self, field_name)) for field_name in COUNT_SUMMARY_FIELDS}


@dataclass(frozen=True)
class ArtifactBodySafetySummary:
    content_suppressed: bool = True
    no_raw_rows: bool = True
    no_logits_dump: bool = True
    no_private_paths: bool = True
    no_performance_claims: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    artifact_policy_checked: bool = True
    body_suppression_checked: bool = True
    artifact_body_audit_checked: bool = True
    artifact_body_allowed: bool = True
    reason_codes: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)
    count_summary: ArtifactBodyCountSummary = field(
        default_factory=ArtifactBodyCountSummary
    )

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "content_suppressed": self.content_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "no_logits_dump": self.no_logits_dump,
            "no_private_paths": self.no_private_paths,
            "no_performance_claims": self.no_performance_claims,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
            "artifact_policy_checked": self.artifact_policy_checked,
            "body_suppression_checked": self.body_suppression_checked,
            "artifact_body_audit_checked": self.artifact_body_audit_checked,
            "artifact_body_allowed": self.artifact_body_allowed,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "count_summary": self.count_summary.to_safe_dict(),
        }


@dataclass(frozen=True)
class ArtifactBodyGenerationError:
    error_status: str
    reason_codes: list[str]
    failed_checks: list[str]
    content_suppressed: bool = True
    safe_summary: str = FAIL_CLOSED_SAFE_SUMMARY

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "error_status": self.error_status,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "content_suppressed": self.content_suppressed,
            "safe_summary": self.safe_summary,
        }


@dataclass(frozen=True)
class ArtifactBodyGenerationResult:
    result_schema_version: str
    body_status: str
    validation_status: str
    reason_codes: list[str]
    failed_checks: list[str]
    artifact_body_schema_version: str
    artifact_body_id: str | None
    artifact_id: str | None
    manifest_id: str | None
    writer_version: str
    writer_result_pointer_id: str | None
    validation_reference_ids: list[str]
    safety_summary: ArtifactBodySafetySummary
    count_summary: ArtifactBodyCountSummary
    artifact_body: dict[str, Any] | None = None
    artifact_file_written: bool = False
    manifest_file_written: bool = False
    safe_summary: str = SUPPRESSED_SAFE_SUMMARY

    @property
    def artifact_body_available(self) -> bool:
        return self.artifact_body is not None

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "result_schema_version": self.result_schema_version,
            "body_status": self.body_status,
            "validation_status": self.validation_status,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "artifact_body_schema_version": self.artifact_body_schema_version,
            "artifact_body_id": self.artifact_body_id,
            "artifact_id": self.artifact_id,
            "manifest_id": self.manifest_id,
            "writer_version": self.writer_version,
            "writer_result_pointer_id": self.writer_result_pointer_id,
            "validation_reference_ids": list(self.validation_reference_ids),
            "safety_flags": _safety_flags(self.safety_summary),
            "count_summary": self.count_summary.to_safe_dict(),
            "artifact_body_available": self.artifact_body_available,
            "artifact_file_written": self.artifact_file_written,
            "manifest_file_written": self.manifest_file_written,
            "safe_summary": self.safe_summary,
        }


def build_suppressed_metadata_only_body(
    request: Mapping[str, Any],
    writer_result_pointer: Mapping[str, Any],
) -> dict[str, Any]:
    request_model = _request_from_mapping(request)
    pointer_model = _pointer_from_mapping(writer_result_pointer)
    validation_references = _validation_references(request_model, pointer_model)
    return _base_body(
        request_model=request_model,
        pointer_model=pointer_model,
        body_status=BODY_STATUS_SUPPRESSED,
        allowed_sections=[],
        body_field_count=0,
        validation_references=validation_references,
    )


def build_safe_metadata_body(
    request: Mapping[str, Any],
    writer_result_pointer: Mapping[str, Any],
) -> dict[str, Any]:
    request_model = _request_from_mapping(request)
    pointer_model = _pointer_from_mapping(writer_result_pointer)
    validation_references = _validation_references(request_model, pointer_model)
    allowed_sections = request_model.safe_section_keys or list(DEFAULT_ALLOWED_SECTIONS)
    return _base_body(
        request_model=request_model,
        pointer_model=pointer_model,
        body_status=BODY_STATUS_GENERATED_SAFE,
        allowed_sections=allowed_sections,
        body_field_count=len(allowed_sections),
        validation_references=validation_references,
    )


def audit_artifact_body_safety(
    body: Mapping[str, Any],
) -> ArtifactBodySafetySummary:
    reason_codes: list[str] = []
    failed_checks: list[str] = []

    schema_version = _safe_optional_string(body.get("artifact_body_schema_version"))
    if schema_version != ARTIFACT_BODY_SCHEMA_VERSION:
        reason_codes.append("unknown_artifact_body_schema_version")
        failed_checks.append("artifact_body_schema_version")

    body_keys = set(str(key) for key in body)
    unknown_body_fields = sorted(body_keys - ALLOWED_BODY_FIELDS)
    if unknown_body_fields:
        reason_codes.append("unsafe_artifact_body_schema")
        failed_checks.append("artifact_body_allowed_fields")

    if not body.get("synthetic_only_notice"):
        reason_codes.append("missing_synthetic_notice")
        failed_checks.append("synthetic_only_notice")
    if not body.get("no_oracle_notice"):
        reason_codes.append("missing_no_oracle_notice")
        failed_checks.append("no_oracle_notice")

    forbidden_reasons, forbidden_checks, counts = _scan_forbidden_content(body)
    reason_codes.extend(forbidden_reasons)
    failed_checks.extend(forbidden_checks)

    count_summary = _count_summary_from_body(body, counts)
    for count_name in ZERO_COUNT_FIELDS:
        if count_summary.to_safe_dict().get(count_name) != 0:
            reason_codes.append(_reason_for_count(count_name))
            failed_checks.append(count_name)

    deduped_reason_codes = _dedupe(reason_codes)
    deduped_failed_checks = _dedupe(failed_checks)
    return ArtifactBodySafetySummary(
        artifact_body_allowed=not deduped_reason_codes,
        reason_codes=deduped_reason_codes,
        failed_checks=deduped_failed_checks,
        count_summary=count_summary,
    )


def generate_artifact_body(
    request: Mapping[str, Any],
    writer_result_pointer: Mapping[str, Any],
) -> ArtifactBodyGenerationResult:
    request_model = _request_from_mapping(request)
    pointer_model = _pointer_from_mapping(writer_result_pointer)
    validation_references = _validation_references(request_model, pointer_model)
    input_reasons = _dedupe(
        [
            *request_model.marker_reason_codes,
            *pointer_model.marker_reason_codes,
            *_input_contract_reasons(request_model, pointer_model),
        ]
    )
    if input_reasons:
        return _fail_closed_result(
            request_model=request_model,
            pointer_model=pointer_model,
            validation_references=validation_references,
            reason_codes=input_reasons,
            failed_checks=input_reasons,
        )

    if request_model.requested_body_mode == BODY_STATUS_GENERATED_SAFE:
        body = build_safe_metadata_body(request, writer_result_pointer)
        safe_summary = GENERATED_SAFE_SUMMARY
    else:
        body = build_suppressed_metadata_only_body(request, writer_result_pointer)
        safe_summary = SUPPRESSED_SAFE_SUMMARY

    safety = audit_artifact_body_safety(body)
    if safety.reason_codes:
        return _fail_closed_result(
            request_model=request_model,
            pointer_model=pointer_model,
            validation_references=validation_references,
            reason_codes=safety.reason_codes,
            failed_checks=safety.failed_checks,
        )

    body_status = _safe_optional_string(body.get("body_status")) or BODY_STATUS_SUPPRESSED
    count_summary = safety.count_summary
    artifact_body = body if body_status == BODY_STATUS_GENERATED_SAFE else None
    return ArtifactBodyGenerationResult(
        result_schema_version=ARTIFACT_BODY_GENERATION_RESULT_SCHEMA_VERSION,
        body_status=body_status,
        validation_status="pass",
        reason_codes=[],
        failed_checks=[],
        artifact_body_schema_version=ARTIFACT_BODY_SCHEMA_VERSION,
        artifact_body_id=request_model.artifact_body_id,
        artifact_id=request_model.artifact_id or pointer_model.artifact_id,
        manifest_id=request_model.manifest_id or pointer_model.manifest_id,
        writer_version=request_model.writer_version,
        writer_result_pointer_id=pointer_model.writer_result_pointer_id,
        validation_reference_ids=validation_references,
        safety_summary=safety,
        count_summary=count_summary,
        artifact_body=artifact_body,
        safe_summary=safe_summary,
    )


def summarize_artifact_body_result(
    result: ArtifactBodyGenerationResult,
) -> dict[str, Any]:
    return result.to_safe_dict()


def _base_body(
    *,
    request_model: ArtifactBodyGenerationRequest,
    pointer_model: ArtifactBodyWriterResultPointer,
    body_status: str,
    allowed_sections: list[str],
    body_field_count: int,
    validation_references: list[str],
) -> dict[str, Any]:
    count_summary = ArtifactBodyCountSummary(
        body_field_count=body_field_count,
        validation_reference_count=len(validation_references),
    )
    safety_summary = ArtifactBodySafetySummary(
        count_summary=count_summary,
        artifact_body_allowed=(body_status == BODY_STATUS_GENERATED_SAFE),
    )
    safe_metadata_field_names = [
        "artifact_body_schema_version",
        "artifact_id",
        "manifest_id",
        "writer_version",
        "body_status",
        "content_suppressed",
        "validation_references",
        "safety_summary",
        "count_summary",
    ]
    return {
        "artifact_body_schema_version": ARTIFACT_BODY_SCHEMA_VERSION,
        "artifact_id": request_model.artifact_id or pointer_model.artifact_id,
        "manifest_id": request_model.manifest_id or pointer_model.manifest_id,
        "writer_version": request_model.writer_version,
        "body_type": "metadata_only",
        "body_status": body_status,
        "content_suppressed": True,
        "synthetic_only_notice": "synthetic-only metadata summary",
        "no_oracle_notice": "no-oracle metadata summary",
        "allowed_sections": sorted(_safe_string_list(allowed_sections)),
        "safety_summary": _safety_flags(safety_summary),
        "count_summary": count_summary.to_safe_dict(),
        "validation_references": validation_references,
        "non_proof_notice": "not performance, quality, real-data, or production-readiness evidence",
        "reason_codes": [],
        "failed_checks": [],
        "safe_metadata_field_names": sorted(safe_metadata_field_names),
        "created_by_version": DEFAULT_WRITER_VERSION,
        "body_suppression_policy": "suppress payload bodies by default",
        "file_writing_policy": "file writing disabled",
    }


def _request_from_mapping(
    payload: Mapping[str, Any],
) -> ArtifactBodyGenerationRequest:
    marker_reason_codes = _marker_reason_codes(payload)
    marker_reason_codes.extend(_scan_mapping_for_reason_codes(payload))
    missing_required_fields = _missing_fields(
        payload,
        (
            "schema_version",
            "artifact_body_id",
            "artifact_id",
            "manifest_id",
            "writer_version",
            "requested_body_mode",
            "synthetic_only_notice_present",
            "no_oracle_notice_present",
            "validation_reference_ids",
        ),
    )
    return ArtifactBodyGenerationRequest(
        schema_version=_safe_optional_string(payload.get("schema_version")),
        case_id=_safe_optional_string(payload.get("case_id")),
        artifact_body_id=_safe_optional_string(payload.get("artifact_body_id")),
        artifact_id=_safe_optional_string(payload.get("artifact_id")),
        manifest_id=_safe_optional_string(payload.get("manifest_id")),
        writer_version=_safe_string(payload.get("writer_version"), DEFAULT_WRITER_VERSION),
        requested_body_mode=_safe_string(
            payload.get("requested_body_mode"),
            BODY_STATUS_SUPPRESSED,
        ),
        requested_body_status=_safe_string(
            payload.get("requested_body_status"),
            BODY_STATUS_SUPPRESSED,
        ),
        synthetic_only_notice_present=(
            payload.get("synthetic_only_notice_present") is True
        ),
        no_oracle_notice_present=payload.get("no_oracle_notice_present") is True,
        validation_reference_ids=_safe_string_list(
            payload.get("validation_reference_ids")
        ),
        safe_section_keys=_safe_string_list(payload.get("safe_section_keys")),
        safe_marker_flags=_safe_bool_mapping(payload.get("safe_marker_flags")),
        marker_reason_codes=_dedupe(marker_reason_codes),
        missing_required_fields=missing_required_fields,
    )


def _pointer_from_mapping(
    payload: Mapping[str, Any],
) -> ArtifactBodyWriterResultPointer:
    missing_required_fields = _missing_fields(
        payload,
        (
            "schema_version",
            "writer_result_pointer_id",
            "writer_status",
            "artifact_id",
            "manifest_id",
            "validation_reference_ids",
            "content_suppressed",
            "no_raw_rows",
            "no_logits_dump",
            "no_private_paths",
            "no_performance_claims",
            "generated_artifact_written",
            "artifact_body_suppressed",
            "manifest_body_suppressed",
        ),
    )
    return ArtifactBodyWriterResultPointer(
        schema_version=_safe_optional_string(payload.get("schema_version")),
        writer_result_pointer_id=_safe_optional_string(
            payload.get("writer_result_pointer_id")
        ),
        writer_status=_safe_optional_string(payload.get("writer_status")),
        artifact_id=_safe_optional_string(payload.get("artifact_id")),
        manifest_id=_safe_optional_string(payload.get("manifest_id")),
        validation_reference_ids=_safe_string_list(
            payload.get("validation_reference_ids")
        ),
        content_suppressed=payload.get("content_suppressed") is True,
        no_raw_rows=payload.get("no_raw_rows") is True,
        no_logits_dump=payload.get("no_logits_dump") is True,
        no_private_paths=payload.get("no_private_paths") is True,
        no_performance_claims=payload.get("no_performance_claims") is True,
        generated_artifact_written=payload.get("generated_artifact_written") is True,
        artifact_body_suppressed=payload.get("artifact_body_suppressed") is True,
        manifest_body_suppressed=payload.get("manifest_body_suppressed") is True,
        marker_reason_codes=_scan_mapping_for_reason_codes(payload),
        missing_required_fields=missing_required_fields,
    )


def _input_contract_reasons(
    request: ArtifactBodyGenerationRequest,
    pointer: ArtifactBodyWriterResultPointer,
) -> list[str]:
    reasons: list[str] = []
    if request.schema_version != ARTIFACT_BODY_REQUEST_SCHEMA_VERSION:
        reasons.append("unsafe_artifact_body_schema")
    if pointer.schema_version != ARTIFACT_WRITER_RESULT_POINTER_SCHEMA_VERSION:
        reasons.append("unsafe_artifact_body_schema")
    if request.missing_required_fields or pointer.missing_required_fields:
        reasons.append("unsafe_artifact_body_schema")
    if not request.synthetic_only_notice_present:
        reasons.append("missing_synthetic_notice")
    if not request.no_oracle_notice_present:
        reasons.append("missing_no_oracle_notice")
    if pointer.writer_status != "pass":
        reasons.append("unsafe_artifact_body_schema")
    if not pointer.content_suppressed:
        reasons.append("raw_learner_text_in_artifact_body")
    if not pointer.no_raw_rows:
        reasons.append("raw_rows_in_artifact_body")
    if not pointer.no_logits_dump:
        reasons.append("logits_dump_in_artifact_body")
    if not pointer.no_private_paths:
        reasons.append("private_path_in_artifact_body")
    if not pointer.no_performance_claims:
        reasons.append("performance_claim_in_artifact_body")
    if pointer.generated_artifact_written:
        reasons.append("unsafe_artifact_body_schema")
    if not pointer.manifest_body_suppressed:
        reasons.append("manifest_body_leakage")
    return reasons


def _fail_closed_result(
    *,
    request_model: ArtifactBodyGenerationRequest,
    pointer_model: ArtifactBodyWriterResultPointer,
    validation_references: list[str],
    reason_codes: list[str],
    failed_checks: list[str],
) -> ArtifactBodyGenerationResult:
    count_summary = ArtifactBodyCountSummary(
        validation_reference_count=len(validation_references)
    )
    safety = ArtifactBodySafetySummary(
        artifact_body_allowed=False,
        reason_codes=_dedupe(reason_codes),
        failed_checks=_dedupe(failed_checks),
        count_summary=count_summary,
    )
    return ArtifactBodyGenerationResult(
        result_schema_version=ARTIFACT_BODY_GENERATION_RESULT_SCHEMA_VERSION,
        body_status=BODY_STATUS_FAIL_CLOSED,
        validation_status="fail",
        reason_codes=safety.reason_codes,
        failed_checks=safety.failed_checks,
        artifact_body_schema_version=ARTIFACT_BODY_SCHEMA_VERSION,
        artifact_body_id=request_model.artifact_body_id,
        artifact_id=request_model.artifact_id or pointer_model.artifact_id,
        manifest_id=request_model.manifest_id or pointer_model.manifest_id,
        writer_version=request_model.writer_version,
        writer_result_pointer_id=pointer_model.writer_result_pointer_id,
        validation_reference_ids=validation_references,
        safety_summary=safety,
        count_summary=count_summary,
        artifact_body=None,
        safe_summary=FAIL_CLOSED_SAFE_SUMMARY,
    )


def _count_summary_from_body(
    body: Mapping[str, Any],
    counts: Mapping[str, int],
) -> ArtifactBodyCountSummary:
    body_count_summary = body.get("count_summary")
    body_field_count = 0
    validation_reference_count = len(_safe_string_list(body.get("validation_references")))
    if isinstance(body_count_summary, Mapping):
        body_field_count = _safe_int(body_count_summary.get("body_field_count"))
        validation_reference_count = _safe_int(
            body_count_summary.get("validation_reference_count"),
            validation_reference_count,
        )
    return ArtifactBodyCountSummary(
        body_field_count=body_field_count,
        raw_row_count=_safe_int(counts.get("raw_row_count")),
        logits_dump_count=_safe_int(counts.get("logits_dump_count")),
        private_path_count=_safe_int(counts.get("private_path_count")),
        performance_metric_count=_safe_int(counts.get("performance_metric_count")),
        request_body_count=_safe_int(counts.get("request_body_count")),
        pointer_body_count=_safe_int(counts.get("pointer_body_count")),
        expected_body_count=_safe_int(counts.get("expected_body_count")),
        manifest_body_count=_safe_int(counts.get("manifest_body_count")),
        validation_reference_count=validation_reference_count,
    )


def _scan_forbidden_content(
    value: Any,
) -> tuple[list[str], list[str], dict[str, int]]:
    reason_codes: list[str] = []
    failed_checks: list[str] = []
    counts = {field_name: 0 for field_name in ZERO_COUNT_FIELDS}

    def visit(item: Any, key_context: str | None = None) -> None:
        if isinstance(item, Mapping):
            for raw_key, nested in item.items():
                key = str(raw_key)
                key_lower = key.lower()
                if key_lower in FORBIDDEN_KEY_REASONS:
                    reason = FORBIDDEN_KEY_REASONS[key_lower]
                    reason_codes.append(reason)
                    failed_checks.append(key_lower)
                    _increment_count_for_reason(counts, reason)
                visit(nested, key_lower)
        elif isinstance(item, list):
            for nested in item:
                visit(nested, key_context)
        elif isinstance(item, str):
            reason = _forbidden_string_reason(item)
            if reason:
                reason_codes.append(reason)
                failed_checks.append(key_context or "forbidden_string_value")
                _increment_count_for_reason(counts, reason)

    visit(value)
    return _dedupe(reason_codes), _dedupe(failed_checks), counts


def _scan_mapping_for_reason_codes(payload: Mapping[str, Any]) -> list[str]:
    reasons, _failed_checks, _counts = _scan_forbidden_content(payload)
    return reasons


def _marker_reason_codes(payload: Mapping[str, Any]) -> list[str]:
    marker_flags = payload.get("safe_marker_flags")
    if not isinstance(marker_flags, Mapping):
        return []
    return _dedupe(
        reason
        for marker_name, reason in SAFE_MARKER_REASON_CODES.items()
        if marker_flags.get(marker_name) is True
    )


def _increment_count_for_reason(counts: dict[str, int], reason: str) -> None:
    if reason == "raw_rows_in_artifact_body":
        counts["raw_row_count"] += 1
    elif reason == "logits_dump_in_artifact_body":
        counts["logits_dump_count"] += 1
    elif reason == "private_path_in_artifact_body":
        counts["private_path_count"] += 1
    elif reason == "performance_claim_in_artifact_body":
        counts["performance_metric_count"] += 1
    elif reason == "request_body_leakage":
        counts["request_body_count"] += 1
    elif reason == "pointer_body_leakage":
        counts["pointer_body_count"] += 1
    elif reason == "expected_result_body_leakage":
        counts["expected_body_count"] += 1
    elif reason == "manifest_body_leakage":
        counts["manifest_body_count"] += 1


def _forbidden_string_reason(value: str) -> str | None:
    lower_value = value.lower()
    if any(marker.lower() in lower_value for marker in RAW_LOG_MARKERS):
        return "raw_learner_text_in_artifact_body"
    if any(marker.lower() in lower_value for marker in UNSAFE_PATH_MARKERS):
        return "private_path_in_artifact_body"
    if LOCAL_ABSOLUTE_PATH_PATTERN.search(value):
        return "private_path_in_artifact_body"
    return None


def _reason_for_count(count_name: str) -> str:
    return {
        "raw_row_count": "raw_rows_in_artifact_body",
        "logits_dump_count": "logits_dump_in_artifact_body",
        "private_path_count": "private_path_in_artifact_body",
        "performance_metric_count": "performance_claim_in_artifact_body",
        "request_body_count": "request_body_leakage",
        "pointer_body_count": "pointer_body_leakage",
        "expected_body_count": "expected_result_body_leakage",
        "manifest_body_count": "manifest_body_leakage",
    }.get(count_name, "unsafe_artifact_body_schema")


def _validation_references(
    request: ArtifactBodyGenerationRequest,
    pointer: ArtifactBodyWriterResultPointer,
) -> list[str]:
    references = request.validation_reference_ids or pointer.validation_reference_ids
    return sorted(_safe_string_list(references))


def _safety_flags(summary: ArtifactBodySafetySummary) -> dict[str, bool]:
    return {field_name: bool(getattr(summary, field_name)) for field_name in SAFETY_FLAG_FIELDS}


def _safe_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _safe_bool_mapping(value: Any) -> dict[str, bool]:
    if not isinstance(value, Mapping):
        return {}
    return {str(key): bool(raw_value) for key, raw_value in value.items()}


def _safe_optional_string(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _safe_string(value: Any, default: str) -> str:
    return value if isinstance(value, str) and value else default


def _safe_int(value: Any, default: int = 0) -> int:
    return value if isinstance(value, int) else default


def _missing_fields(payload: Mapping[str, Any], required_fields: tuple[str, ...]) -> list[str]:
    return sorted(field_name for field_name in required_fields if field_name not in payload)


def _dedupe(values: Any) -> list[str]:
    return sorted({str(value) for value in values if isinstance(value, str) and value})


def _assert_json_serializable(value: Mapping[str, Any]) -> None:
    json.dumps(value, sort_keys=True)


__all__ = [
    "ARTIFACT_BODY_GENERATION_RESULT_SCHEMA_VERSION",
    "ARTIFACT_BODY_SCHEMA_VERSION",
    "ArtifactBodyCountSummary",
    "ArtifactBodyGenerationError",
    "ArtifactBodyGenerationRequest",
    "ArtifactBodyGenerationResult",
    "ArtifactBodySafetySummary",
    "audit_artifact_body_safety",
    "build_safe_metadata_body",
    "build_suppressed_metadata_only_body",
    "generate_artifact_body",
    "summarize_artifact_body_result",
]
