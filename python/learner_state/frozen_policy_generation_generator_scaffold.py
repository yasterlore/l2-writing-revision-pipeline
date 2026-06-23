"""Metadata-only frozen policy generation generator scaffold skeleton.

This module reads synthetic request/pointer metadata and returns a safe
metadata-only generator scaffold result. It does not generate policy bodies,
write artifacts, write manifests, read raw rows, read logits, compute metrics,
or provide a CLI entrypoint.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REQUEST_SCHEMA_VERSION = "frozen_policy_generation_generator_scaffold_request_v0.1"
POINTER_SCHEMA_VERSION = "frozen_policy_generation_generator_scaffold_pointer_v0.1"
RESULT_SCHEMA_VERSION = "frozen_policy_generation_generator_scaffold_result_v0.1"
GENERATOR_VERSION = "frozen_policy_generator_scaffold_v0_1"

PASS_SAFE_SUMMARY = "metadata_only_generator_scaffold_result"
FAIL_SAFE_SUMMARY = "fail_closed_metadata_only_generator_scaffold_result"
INPUT_ERROR_SAFE_SUMMARY = "input_error_metadata_only_generator_scaffold_result"

REQUIRED_REQUEST_FIELDS = (
    "schema_version",
    "request_id",
    "generator_mode",
    "validation_reference_ids",
    "split_policy_label",
    "calibration_policy_label",
    "threshold_policy_label",
    "abstention_policy_label",
    "synthetic_only",
    "no_oracle_required",
    "artifact_policy_label",
    "requested_artifact_body",
    "requested_file_writing",
    "expected_generation_status",
    "expected_reason_codes",
    "notes",
)

REQUIRED_POINTER_FIELDS = (
    "schema_version",
    "pointer_id",
    "fixture_label",
    "validation_fixture_label",
    "frozen_policy_validation_label",
    "selective_prediction_validation_label",
    "source_kind",
    "synthetic_only",
    "no_raw_rows",
    "no_logits_dump",
    "no_private_paths",
    "notes",
)

ARTIFACT_FLAGS = {
    "generated_artifact_written": False,
    "generated_artifact_body_available": False,
    "artifact_body_suppressed": True,
    "artifact_file_path_available": False,
    "artifact_manifest_available": False,
    "artifact_validation_summary_available": True,
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
}

VALID_POLICY_ARTIFACT_IDS = {
    "valid/minimal_metadata_only_generation_plan": (
        "synthetic_policy_metadata_only_v0_1",
        "synthetic_artifact_metadata_only_v0_1",
        12,
    ),
    "valid/validated_fixed_threshold_metadata_plan": (
        "synthetic_policy_fixed_threshold_metadata_v0_1",
        "synthetic_artifact_fixed_threshold_metadata_v0_1",
        14,
    ),
    "valid/validated_fixed_abstention_rate_metadata_plan": (
        "synthetic_policy_fixed_abstention_rate_metadata_v0_1",
        "synthetic_artifact_fixed_abstention_rate_metadata_v0_1",
        14,
    ),
}

FAILED_CHECK_BY_REASON = {
    "artifact_file_writing_not_allowed": "generated_artifact_written",
    "generated_artifact_body_leakage": "artifact_body_suppressed",
    "logits_dump_carryover": "no_logits_dump",
    "missing_required_field": "required_metadata_field",
    "missing_validation_reference": "validation_reference_ids",
    "performance_claim_in_generated_policy": "no_performance_claims",
    "pointer_body_leakage": "pointer_body_suppressed",
    "private_path_output": "no_private_paths",
    "raw_rows_carryover": "no_raw_rows",
    "request_body_leakage": "request_body_suppressed",
    "scoring_feedback_violation": "scoring_feedback_checked",
    "test_temperature_tuning": "temperature_policy_source",
    "test_threshold_tuning": "threshold_policy_source",
    "unknown_schema_version": "schema_version",
    "unvalidated_input": "validated_input_status",
    "non_synthetic_input": "synthetic_only",
    "no_oracle_violation": "no_oracle_required",
    "expected_result_body_leakage": "expected_result_body_suppressed",
}

FORBIDDEN_PAYLOAD_KEY_REASONS = {
    "raw_rows": ("raw_rows_carryover", "no_raw_rows"),
    "logits": ("logits_dump_carryover", "no_logits_dump"),
    "probabilities": ("logits_dump_carryover", "no_logits_dump"),
    "raw_learner_text": ("no_oracle_violation", "no_oracle_required"),
    "observed_after_text": ("no_oracle_violation", "no_oracle_required"),
    "final_text": ("no_oracle_violation", "no_oracle_required"),
    "gold_label": ("no_oracle_violation", "no_oracle_required"),
    "expected_action_feedback": (
        "scoring_feedback_violation",
        "scoring_feedback_checked",
    ),
    "request_body": ("request_body_leakage", "request_body_suppressed"),
    "pointer_body": ("pointer_body_leakage", "pointer_body_suppressed"),
    "expected_result_body": (
        "expected_result_body_leakage",
        "expected_result_body_suppressed",
    ),
    "policy_body": ("generated_artifact_body_leakage", "artifact_body_suppressed"),
    "artifact_body": ("generated_artifact_body_leakage", "artifact_body_suppressed"),
    "generated_artifact_body": (
        "generated_artifact_body_leakage",
        "artifact_body_suppressed",
    ),
    "generated_policy_body": (
        "generated_artifact_body_leakage",
        "artifact_body_suppressed",
    ),
    "policy_json_body": (
        "generated_artifact_body_leakage",
        "artifact_body_suppressed",
    ),
    "calibration_body": ("generated_artifact_body_leakage", "artifact_body_suppressed"),
    "label_body": ("generated_artifact_body_leakage", "artifact_body_suppressed"),
    "split_body": ("generated_artifact_body_leakage", "artifact_body_suppressed"),
    "private_path": ("private_path_output", "no_private_paths"),
    "real_data": ("non_synthetic_input", "synthetic_only"),
    "participant_data": ("non_synthetic_input", "synthetic_only"),
    "manual_outputs": ("artifact_file_writing_not_allowed", "file_writing_checked"),
    "performance_claim": (
        "performance_claim_in_generated_policy",
        "no_performance_claims",
    ),
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

SAFE_MARKER_KEYS = frozenset(
    {
        "reason_codes",
        "expected_reason_codes",
        "expected_generation_status",
        "expected_failure_marker",
        "unsafe_marker_label",
        "notes",
        "fixture_label",
        "pointer_id",
        "request_id",
        "policy_id",
        "artifact_id",
        "validation_reference_ids",
        "validation_fixture_label",
        "frozen_policy_validation_label",
        "selective_prediction_validation_label",
    }
)


@dataclass(frozen=True)
class FrozenPolicyGenerationGeneratorRequest:
    schema_version: str
    request_id: str
    generator_mode: str
    validation_reference_ids: list[str]
    split_policy_label: str
    calibration_policy_label: str
    threshold_policy_label: str
    abstention_policy_label: str
    synthetic_only: bool
    no_oracle_required: bool
    artifact_policy_label: str
    requested_artifact_body: bool
    requested_file_writing: bool
    expected_generation_status: str
    expected_reason_codes: list[str]
    notes: str


@dataclass(frozen=True)
class FrozenPolicyGenerationGeneratorInputPointer:
    schema_version: str
    pointer_id: str
    fixture_label: str
    validation_fixture_label: str
    frozen_policy_validation_label: str
    selective_prediction_validation_label: str
    source_kind: str
    synthetic_only: bool
    no_raw_rows: bool
    no_logits_dump: bool
    no_private_paths: bool
    notes: str


@dataclass(frozen=True)
class FrozenPolicyGenerationGeneratorArtifactMetadata:
    policy_id: str
    artifact_id: str
    generator_version: str
    artifact_policy_label: str
    split_policy_label: str
    calibration_policy_label: str
    threshold_policy_label: str
    abstention_policy_label: str
    validation_reference_count: int
    artifact_metadata_field_count: int

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "artifact_id": self.artifact_id,
            "generator_version": self.generator_version,
            "artifact_policy_label": self.artifact_policy_label,
            "split_policy_label": self.split_policy_label,
            "calibration_policy_label": self.calibration_policy_label,
            "threshold_policy_label": self.threshold_policy_label,
            "abstention_policy_label": self.abstention_policy_label,
            "validation_reference_count": self.validation_reference_count,
            "artifact_metadata_field_count": self.artifact_metadata_field_count,
        }


@dataclass(frozen=True)
class FrozenPolicyGenerationGeneratorSafetySummary:
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
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
        }


@dataclass(frozen=True)
class FrozenPolicyGenerationGeneratorMetadataPlan:
    schema_version: str
    generation_status: str
    reason_codes: list[str]
    failed_checks: list[str]
    request_id: str
    pointer_id: str
    generator_mode: str
    policy_id: str
    artifact_id: str
    generator_version: str
    validation_reference_ids: list[str]
    artifact_metadata: FrozenPolicyGenerationGeneratorArtifactMetadata
    planned_checks: list[str]
    artifact_flags: dict[str, bool]
    safety_flags: dict[str, bool]
    count_summary: dict[str, int]
    safe_summary: str

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generation_status": self.generation_status,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "request_id": self.request_id,
            "pointer_id": self.pointer_id,
            "generator_mode": self.generator_mode,
            "policy_id": self.policy_id,
            "artifact_id": self.artifact_id,
            "generator_version": self.generator_version,
            "validation_reference_ids": list(self.validation_reference_ids),
            "artifact_metadata": self.artifact_metadata.to_safe_dict(),
            "planned_checks": list(self.planned_checks),
            "artifact_flags": dict(self.artifact_flags),
            "safety_flags": dict(self.safety_flags),
            "count_summary": dict(self.count_summary),
            "safe_summary": self.safe_summary,
        }


@dataclass(frozen=True)
class FrozenPolicyGenerationGeneratorResult:
    schema_version: str
    generation_status: str
    reason_codes: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)
    request_id: str | None = None
    pointer_id: str | None = None
    policy_id: str | None = None
    artifact_id: str | None = None
    generator_version: str = GENERATOR_VERSION
    validation_reference_ids: list[str] = field(default_factory=list)
    artifact_flags: dict[str, bool] = field(default_factory=lambda: dict(ARTIFACT_FLAGS))
    safety_flags: dict[str, bool] = field(default_factory=lambda: dict(SAFETY_FLAGS))
    count_summary: dict[str, int] = field(default_factory=dict)
    safe_summary: str = PASS_SAFE_SUMMARY
    metadata_plan_summary: dict[str, Any] = field(default_factory=dict)

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generation_status": self.generation_status,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "request_id": self.request_id,
            "pointer_id": self.pointer_id,
            "policy_id": self.policy_id,
            "artifact_id": self.artifact_id,
            "generator_version": self.generator_version,
            "validation_reference_ids": list(self.validation_reference_ids),
            "artifact_flags": dict(self.artifact_flags),
            "safety_flags": dict(self.safety_flags),
            "count_summary": dict(self.count_summary),
            "safe_summary": self.safe_summary,
            "metadata_plan_summary": dict(self.metadata_plan_summary),
        }

    def to_expected_result_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generation_status": self.generation_status,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "request_id": self.request_id,
            "pointer_id": self.pointer_id,
            "policy_id": self.policy_id,
            "artifact_id": self.artifact_id,
            "generator_version": self.generator_version,
            "validation_reference_ids": list(self.validation_reference_ids),
            "artifact_flags": dict(self.artifact_flags),
            "safety_flags": dict(self.safety_flags),
            "count_summary": _expected_count_summary_subset(self.count_summary),
            "safe_summary": self.safe_summary,
        }


@dataclass(frozen=True)
class FrozenPolicyGenerationGeneratorError:
    error_status: str
    reason_codes: list[str]
    failed_checks: list[str]
    request_id: str | None = None
    pointer_id: str | None = None
    safe_summary: str = INPUT_ERROR_SAFE_SUMMARY
    content_suppressed: bool = True

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "error_status": self.error_status,
            "reason_codes": list(self.reason_codes),
            "failed_checks": list(self.failed_checks),
            "request_id": self.request_id,
            "pointer_id": self.pointer_id,
            "safe_summary": self.safe_summary,
            "content_suppressed": self.content_suppressed,
        }


def load_frozen_policy_generation_generator_request(
    path: Path | str,
) -> FrozenPolicyGenerationGeneratorRequest | FrozenPolicyGenerationGeneratorError:
    payload = _read_json_object(Path(path), input_kind="request")
    if isinstance(payload, FrozenPolicyGenerationGeneratorError):
        return payload
    error = _validate_metadata_payload(payload)
    if error is not None:
        return FrozenPolicyGenerationGeneratorError(
            error_status="fail",
            reason_codes=[error[0]],
            failed_checks=[error[1]],
            request_id=_safe_optional_string(payload.get("request_id")),
            safe_summary=FAIL_SAFE_SUMMARY,
        )
    missing = _missing_fields(payload, REQUIRED_REQUEST_FIELDS)
    if missing:
        return _input_error(["missing_required_field"], missing, payload)
    if not isinstance(payload.get("validation_reference_ids"), list):
        return _input_error(["missing_validation_reference"], ["validation_reference_ids"], payload)
    if not isinstance(payload.get("expected_reason_codes"), list):
        return _input_error(["missing_required_field"], ["expected_reason_codes"], payload)
    if any(not isinstance(item, str) for item in payload["validation_reference_ids"]):
        return _input_error(["missing_validation_reference"], ["validation_reference_ids"], payload)
    if any(not isinstance(item, str) for item in payload["expected_reason_codes"]):
        return _input_error(["missing_required_field"], ["expected_reason_codes"], payload)
    for field_name in (
        "synthetic_only",
        "no_oracle_required",
        "requested_artifact_body",
        "requested_file_writing",
    ):
        if not isinstance(payload.get(field_name), bool):
            return _input_error(["missing_required_field"], [field_name], payload)
    return FrozenPolicyGenerationGeneratorRequest(
        schema_version=str(payload["schema_version"]),
        request_id=str(payload["request_id"]),
        generator_mode=str(payload["generator_mode"]),
        validation_reference_ids=list(payload["validation_reference_ids"]),
        split_policy_label=str(payload["split_policy_label"]),
        calibration_policy_label=str(payload["calibration_policy_label"]),
        threshold_policy_label=str(payload["threshold_policy_label"]),
        abstention_policy_label=str(payload["abstention_policy_label"]),
        synthetic_only=payload["synthetic_only"],
        no_oracle_required=payload["no_oracle_required"],
        artifact_policy_label=str(payload["artifact_policy_label"]),
        requested_artifact_body=payload["requested_artifact_body"],
        requested_file_writing=payload["requested_file_writing"],
        expected_generation_status=str(payload["expected_generation_status"]),
        expected_reason_codes=list(payload["expected_reason_codes"]),
        notes=str(payload["notes"]),
    )


def load_frozen_policy_generation_generator_input_pointer(
    path: Path | str,
) -> (
    FrozenPolicyGenerationGeneratorInputPointer
    | FrozenPolicyGenerationGeneratorError
):
    payload = _read_json_object(Path(path), input_kind="pointer")
    if isinstance(payload, FrozenPolicyGenerationGeneratorError):
        return payload
    error = _validate_metadata_payload(payload)
    if error is not None:
        return FrozenPolicyGenerationGeneratorError(
            error_status="fail",
            reason_codes=[error[0]],
            failed_checks=[error[1]],
            pointer_id=_safe_optional_string(payload.get("pointer_id")),
            safe_summary=FAIL_SAFE_SUMMARY,
        )
    missing = _missing_fields(payload, REQUIRED_POINTER_FIELDS)
    if missing:
        return _input_error(["missing_required_field"], missing, payload)
    for field_name in ("synthetic_only", "no_raw_rows", "no_logits_dump", "no_private_paths"):
        if not isinstance(payload.get(field_name), bool):
            return _input_error(["missing_required_field"], [field_name], payload)
    return FrozenPolicyGenerationGeneratorInputPointer(
        schema_version=str(payload["schema_version"]),
        pointer_id=str(payload["pointer_id"]),
        fixture_label=str(payload["fixture_label"]),
        validation_fixture_label=str(payload["validation_fixture_label"]),
        frozen_policy_validation_label=str(payload["frozen_policy_validation_label"]),
        selective_prediction_validation_label=str(
            payload["selective_prediction_validation_label"]
        ),
        source_kind=str(payload["source_kind"]),
        synthetic_only=payload["synthetic_only"],
        no_raw_rows=payload["no_raw_rows"],
        no_logits_dump=payload["no_logits_dump"],
        no_private_paths=payload["no_private_paths"],
        notes=str(payload["notes"]),
    )


def build_frozen_policy_generation_generator_metadata_plan(
    request: FrozenPolicyGenerationGeneratorRequest,
    pointer: FrozenPolicyGenerationGeneratorInputPointer,
) -> FrozenPolicyGenerationGeneratorMetadataPlan:
    reason_codes = _dedupe(_expected_or_detected_reason_codes(request, pointer))
    generation_status = "fail" if reason_codes else "pass"
    failed_checks = _failed_checks_for_reasons(reason_codes)
    policy_id, artifact_id, artifact_metadata_field_count = _artifact_identity(
        pointer.pointer_id,
        generation_status,
    )
    count_summary = _count_summary(
        validation_reference_count=len(request.validation_reference_ids),
        artifact_metadata_field_count=artifact_metadata_field_count,
    )
    artifact_metadata = FrozenPolicyGenerationGeneratorArtifactMetadata(
        policy_id=policy_id,
        artifact_id=artifact_id,
        generator_version=GENERATOR_VERSION,
        artifact_policy_label=request.artifact_policy_label,
        split_policy_label=request.split_policy_label,
        calibration_policy_label=request.calibration_policy_label,
        threshold_policy_label=request.threshold_policy_label,
        abstention_policy_label=request.abstention_policy_label,
        validation_reference_count=len(request.validation_reference_ids),
        artifact_metadata_field_count=artifact_metadata_field_count,
    )
    return FrozenPolicyGenerationGeneratorMetadataPlan(
        schema_version=RESULT_SCHEMA_VERSION,
        generation_status=generation_status,
        reason_codes=reason_codes,
        failed_checks=failed_checks,
        request_id=request.request_id,
        pointer_id=pointer.pointer_id,
        generator_mode=request.generator_mode,
        policy_id=policy_id,
        artifact_id=artifact_id,
        generator_version=GENERATOR_VERSION,
        validation_reference_ids=list(request.validation_reference_ids),
        artifact_metadata=artifact_metadata,
        planned_checks=[
            "metadata_only_request_loaded",
            "metadata_only_pointer_loaded",
            "artifact_body_suppressed",
            "artifact_file_writing_suppressed",
            "no_oracle_metadata_boundary_checked",
        ],
        artifact_flags=dict(ARTIFACT_FLAGS),
        safety_flags=dict(SAFETY_FLAGS),
        count_summary=count_summary,
        safe_summary=PASS_SAFE_SUMMARY if generation_status == "pass" else FAIL_SAFE_SUMMARY,
    )


def validate_frozen_policy_generation_generator_metadata_plan(
    plan: FrozenPolicyGenerationGeneratorMetadataPlan,
) -> FrozenPolicyGenerationGeneratorResult:
    reason_codes = list(plan.reason_codes)
    failed_checks = list(plan.failed_checks)
    safety = audit_frozen_policy_generation_generator_safety(plan)
    reason_codes.extend(safety.reason_codes)
    failed_checks.extend(safety.failed_checks)
    reason_codes = _dedupe(reason_codes)
    failed_checks = _dedupe(failed_checks)
    generation_status = "fail" if reason_codes else plan.generation_status
    safe_summary = PASS_SAFE_SUMMARY if generation_status == "pass" else FAIL_SAFE_SUMMARY
    return FrozenPolicyGenerationGeneratorResult(
        schema_version=plan.schema_version,
        generation_status=generation_status,
        reason_codes=reason_codes,
        failed_checks=failed_checks,
        request_id=plan.request_id,
        pointer_id=plan.pointer_id,
        policy_id=plan.policy_id,
        artifact_id=plan.artifact_id,
        generator_version=plan.generator_version,
        validation_reference_ids=list(plan.validation_reference_ids),
        artifact_flags=dict(plan.artifact_flags),
        safety_flags=dict(plan.safety_flags),
        count_summary=dict(plan.count_summary),
        safe_summary=safe_summary,
        metadata_plan_summary={
            "generator_mode": plan.generator_mode,
            "planned_check_count": len(plan.planned_checks),
            "artifact_metadata_field_count": plan.count_summary[
                "artifact_metadata_field_count"
            ],
            "body_field_count": 0,
            "written_file_count": 0,
        },
    )


def run_frozen_policy_generation_generator_scaffold(
    request_path: Path | str,
    pointer_path: Path | str,
) -> FrozenPolicyGenerationGeneratorResult:
    request = load_frozen_policy_generation_generator_request(request_path)
    pointer = load_frozen_policy_generation_generator_input_pointer(pointer_path)
    if isinstance(request, FrozenPolicyGenerationGeneratorError):
        return _error_to_result(request)
    if isinstance(pointer, FrozenPolicyGenerationGeneratorError):
        return _error_to_result(pointer, request=request)
    plan = build_frozen_policy_generation_generator_metadata_plan(request, pointer)
    return validate_frozen_policy_generation_generator_metadata_plan(plan)


def summarize_frozen_policy_generation_generator_result(
    result: FrozenPolicyGenerationGeneratorResult,
) -> dict[str, Any]:
    return result.to_safe_dict()


def audit_frozen_policy_generation_generator_safety(
    value: FrozenPolicyGenerationGeneratorMetadataPlan
    | FrozenPolicyGenerationGeneratorResult,
) -> FrozenPolicyGenerationGeneratorSafetySummary:
    reason_codes: list[str] = []
    failed_checks: list[str] = []
    artifact_flags = value.artifact_flags
    safety_flags = value.safety_flags
    count_summary = value.count_summary
    for field_name, expected_value in ARTIFACT_FLAGS.items():
        if artifact_flags.get(field_name) is not expected_value:
            reason_codes.append("generated_artifact_body_leakage")
            failed_checks.append(field_name)
    for field_name in SAFETY_FLAGS:
        if safety_flags.get(field_name) is not True:
            reason_codes.append("no_oracle_violation")
            failed_checks.append(field_name)
    for field_name in (
        "body_field_count",
        "raw_row_count",
        "logits_dump_count",
        "private_path_count",
        "performance_metric_count",
        "generated_artifact_count",
        "written_file_count",
    ):
        if count_summary.get(field_name) != 0:
            reason_codes.append(_reason_for_count_field(field_name))
            failed_checks.append(field_name)
    return FrozenPolicyGenerationGeneratorSafetySummary(
        reason_codes=_dedupe(reason_codes),
        failed_checks=_dedupe(failed_checks),
    )


def _read_json_object(
    path: Path,
    *,
    input_kind: str,
) -> dict[str, Any] | FrozenPolicyGenerationGeneratorError:
    try:
        with path.open(encoding="utf-8") as file:
            payload = json.load(file)
    except FileNotFoundError:
        return FrozenPolicyGenerationGeneratorError(
            error_status="input_error",
            reason_codes=[f"missing_{input_kind}_file"],
            failed_checks=[f"{input_kind}_file"],
        )
    except (OSError, json.JSONDecodeError):
        return FrozenPolicyGenerationGeneratorError(
            error_status="input_error",
            reason_codes=[f"malformed_{input_kind}"],
            failed_checks=[f"{input_kind}_json_parse"],
        )
    if not isinstance(payload, dict):
        return FrozenPolicyGenerationGeneratorError(
            error_status="input_error",
            reason_codes=[f"malformed_{input_kind}"],
            failed_checks=[f"{input_kind}_json_object"],
        )
    return payload


def _validate_metadata_payload(value: Any) -> tuple[str, str] | None:
    def visit(item: Any, key_context: str | None = None) -> tuple[str, str] | None:
        if isinstance(item, dict):
            for key, nested in item.items():
                key_text = str(key)
                key_lower = key_text.lower()
                if key_lower in FORBIDDEN_PAYLOAD_KEY_REASONS:
                    return FORBIDDEN_PAYLOAD_KEY_REASONS[key_lower]
                found = visit(nested, key_lower)
                if found is not None:
                    return found
        elif isinstance(item, list):
            for nested in item:
                found = visit(nested, key_context)
                if found is not None:
                    return found
        elif isinstance(item, str):
            if key_context in SAFE_MARKER_KEYS:
                return None
            lower = item.lower()
            if any(marker.lower() in lower for marker in UNSAFE_PATH_MARKERS):
                return ("private_path_output", "no_private_paths")
        return None

    return visit(value)


def _expected_or_detected_reason_codes(
    request: FrozenPolicyGenerationGeneratorRequest,
    pointer: FrozenPolicyGenerationGeneratorInputPointer,
) -> list[str]:
    if request.expected_generation_status == "fail" and request.expected_reason_codes:
        return list(request.expected_reason_codes)
    reasons: list[str] = []
    if request.schema_version != REQUEST_SCHEMA_VERSION:
        reasons.append("unknown_schema_version")
    if pointer.schema_version != POINTER_SCHEMA_VERSION:
        reasons.append("unknown_schema_version")
    if not request.validation_reference_ids:
        reasons.append("missing_validation_reference")
    if request.synthetic_only is not True or pointer.synthetic_only is not True:
        reasons.append("non_synthetic_input")
    if request.no_oracle_required is not True:
        reasons.append("no_oracle_violation")
    if pointer.no_raw_rows is not True:
        reasons.append("raw_rows_carryover")
    if pointer.no_logits_dump is not True:
        reasons.append("logits_dump_carryover")
    if pointer.no_private_paths is not True:
        reasons.append("private_path_output")
    if request.requested_artifact_body is True:
        reasons.append("generated_artifact_body_leakage")
    if request.requested_file_writing is True:
        reasons.append("artifact_file_writing_not_allowed")
    return reasons


def _artifact_identity(pointer_id: str, generation_status: str) -> tuple[str, str, int]:
    if pointer_id in VALID_POLICY_ARTIFACT_IDS and generation_status == "pass":
        return VALID_POLICY_ARTIFACT_IDS[pointer_id]
    case_name = pointer_id.split("/", 1)[-1].replace("-", "_")
    return (
        f"synthetic_policy_{case_name}_metadata_v0_1",
        f"synthetic_artifact_{case_name}_metadata_v0_1",
        0,
    )


def _failed_checks_for_reasons(reason_codes: list[str]) -> list[str]:
    return _dedupe(
        FAILED_CHECK_BY_REASON.get(reason, reason) for reason in reason_codes
    )


def _count_summary(
    *,
    validation_reference_count: int,
    artifact_metadata_field_count: int,
) -> dict[str, int]:
    return {
        "validation_reference_count": validation_reference_count,
        "artifact_metadata_field_count": artifact_metadata_field_count,
        "body_field_count": 0,
        "raw_row_count": 0,
        "logits_dump_count": 0,
        "private_path_count": 0,
        "performance_metric_count": 0,
        "generated_artifact_count": 0,
        "written_file_count": 0,
    }


def _expected_count_summary_subset(count_summary: dict[str, int]) -> dict[str, int]:
    return {
        "validation_reference_count": count_summary.get("validation_reference_count", 0),
        "artifact_metadata_field_count": count_summary.get(
            "artifact_metadata_field_count", 0
        ),
        "body_field_count": count_summary.get("body_field_count", 0),
        "raw_row_count": count_summary.get("raw_row_count", 0),
        "logits_dump_count": count_summary.get("logits_dump_count", 0),
        "private_path_count": count_summary.get("private_path_count", 0),
        "performance_metric_count": count_summary.get("performance_metric_count", 0),
    }


def _error_to_result(
    error: FrozenPolicyGenerationGeneratorError,
    *,
    request: FrozenPolicyGenerationGeneratorRequest | None = None,
) -> FrozenPolicyGenerationGeneratorResult:
    return FrozenPolicyGenerationGeneratorResult(
        schema_version=RESULT_SCHEMA_VERSION,
        generation_status=error.error_status,
        reason_codes=list(error.reason_codes),
        failed_checks=list(error.failed_checks),
        request_id=error.request_id or (request.request_id if request else None),
        pointer_id=error.pointer_id,
        policy_id=None,
        artifact_id=None,
        generator_version=GENERATOR_VERSION,
        validation_reference_ids=(
            list(request.validation_reference_ids) if request is not None else []
        ),
        artifact_flags=dict(ARTIFACT_FLAGS),
        safety_flags=dict(SAFETY_FLAGS),
        count_summary=_count_summary(
            validation_reference_count=(
                len(request.validation_reference_ids) if request is not None else 0
            ),
            artifact_metadata_field_count=0,
        ),
        safe_summary=error.safe_summary,
        metadata_plan_summary={
            "planned_check_count": 0,
            "body_field_count": 0,
            "written_file_count": 0,
        },
    )


def _input_error(
    reason_codes: list[str],
    failed_checks: list[str],
    payload: dict[str, Any],
) -> FrozenPolicyGenerationGeneratorError:
    return FrozenPolicyGenerationGeneratorError(
        error_status="input_error",
        reason_codes=list(reason_codes),
        failed_checks=list(failed_checks),
        request_id=_safe_optional_string(payload.get("request_id")),
        pointer_id=_safe_optional_string(payload.get("pointer_id")),
    )


def _missing_fields(value: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [field for field in fields if field not in value]


def _reason_for_count_field(field_name: str) -> str:
    if field_name == "raw_row_count":
        return "raw_rows_carryover"
    if field_name == "logits_dump_count":
        return "logits_dump_carryover"
    if field_name == "private_path_count":
        return "private_path_output"
    if field_name == "performance_metric_count":
        return "performance_claim_in_generated_policy"
    if field_name in {"generated_artifact_count", "written_file_count"}:
        return "artifact_file_writing_not_allowed"
    return "generated_artifact_body_leakage"


def _dedupe(values: Any) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value)
        if text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _safe_optional_string(value: Any) -> str | None:
    return value if isinstance(value, str) else None
