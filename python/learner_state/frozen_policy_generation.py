"""Metadata-only frozen policy generation scaffold runtime.

This module is a minimal scaffold runtime skeleton. It loads synthetic fixture
metadata, builds a safe plan, and returns a metadata-only result. It does not
generate policy artifacts, write files, fit calibration, compute metrics, or
inspect real participant data.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REQUEST_SCHEMA_VERSION = "frozen_policy_generation_scaffold_request_schema_v0_1"
POINTER_SCHEMA_VERSION = "frozen_policy_generation_scaffold_pointer_schema_v0_1"
SCAFFOLD_RESULT_SCHEMA_VERSION = "frozen_policy_generation_scaffold_result_schema_v0_1"
RUNTIME_SCHEMA_VERSION = "frozen_policy_generation_scaffold_runtime_schema_v0_1"

SUPPORTED_GENERATION_MODES = frozenset({"scaffold_dry_run"})

REQUIRED_REQUEST_FIELDS = (
    "request_schema_version",
    "request_id",
    "generation_mode",
    "dry_run",
    "temperature_policy",
    "threshold_policy",
    "abstention_policy",
    "output_policy",
    "validation_split_source",
    "synthetic_only",
    "no_oracle",
    "no_body_dump",
    "no_raw_rows",
    "no_logits_dump",
    "metadata_only",
)

REQUIRED_POINTER_FIELDS = (
    "pointer_schema_version",
    "fixture_family",
    "fixture_case_label",
    "input_validation_status",
    "validation_split_available",
    "selective_prediction_validation_status",
    "frozen_policy_validation_status",
    "relative_fixture_reference",
    "synthetic_only",
    "no_oracle",
    "metadata_only",
)

KNOWN_INVALID_REASON_CODES = frozenset(
    {
        "missing_validation_split",
        "test_temperature_tuning",
        "test_threshold_tuning",
        "raw_rows_carryover",
        "logits_dump_carryover",
        "generated_artifact_body_leakage",
        "private_path_output",
        "scoring_feedback_violation",
    }
)

REASON_CODE_ORDER = (
    "missing_request",
    "malformed_request",
    "missing_pointer",
    "malformed_pointer",
    "unsafe_path",
    "unknown_schema_version",
    "missing_required_field",
    "unsupported_generation_mode",
    "artifact_body_not_allowed",
    "output_policy_not_safe",
    "no_oracle_violation",
    "performance_claim_generation",
    "missing_validation_split",
    "test_temperature_tuning",
    "test_threshold_tuning",
    "raw_rows_carryover",
    "logits_dump_carryover",
    "generated_artifact_body_leakage",
    "private_path_output",
    "scoring_feedback_violation",
)

REASON_FAILED_CHECKS = {
    "missing_request": ("generation_request_path",),
    "malformed_request": ("generation_request_json",),
    "missing_pointer": ("input_fixture_pointer_path",),
    "malformed_pointer": ("input_fixture_pointer_json",),
    "unsafe_path": ("path_safety",),
    "unknown_schema_version": ("schema_version",),
    "missing_required_field": ("required_fields",),
    "unsupported_generation_mode": ("generation_mode",),
    "artifact_body_not_allowed": ("artifact_body_suppressed",),
    "output_policy_not_safe": ("output_policy",),
    "no_oracle_violation": ("no_oracle",),
    "performance_claim_generation": ("performance_claim_scan",),
    "missing_validation_split": ("validation_split_available",),
    "test_temperature_tuning": ("temperature_policy_source",),
    "test_threshold_tuning": (
        "threshold_policy_source",
        "abstention_policy_source",
    ),
    "raw_rows_carryover": ("no_raw_rows",),
    "logits_dump_carryover": ("no_logits_dump",),
    "generated_artifact_body_leakage": ("artifact_body_suppressed",),
    "private_path_output": ("private_path_scan",),
    "scoring_feedback_violation": ("no_oracle", "scoring_feedback_boundary"),
}

UNSAFE_PATH_PARTS = frozenset(
    {
        "real_data",
        "participant_data",
        "private_data",
        "manual_outputs",
    }
)

BODY_PAYLOAD_KEYS = frozenset(
    {
        "generation_request",
        "input_fixture_pointer",
        "expected_scaffold_result",
        "generated_artifact_body",
        "generated_frozen_policy_body",
        "frozen_policy_artifact_body",
        "policy_body",
        "raw_rows",
        "logits",
        "probabilities",
        "raw_learner_text",
        "final_text",
        "observed_after_text",
        "gold_label",
    }
)


@dataclass(frozen=True)
class FrozenPolicyGenerationScaffoldError:
    reason_code: str
    failed_check: str
    input_kind: str


@dataclass(frozen=True)
class FrozenPolicyGenerationScaffoldSafetySummary:
    content_suppressed: bool = True
    artifact_body_suppressed: bool = True
    no_raw_rows: bool = True
    no_logits_dump: bool = True
    no_private_paths: bool = True
    no_performance_claims: bool = True
    no_request_body: bool = True
    no_generated_artifact_body: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    test_tuning_checked: bool = True
    scoring_feedback_checked: bool = True
    private_path_scan_checked: bool = True
    performance_claim_scan_checked: bool = True
    metadata_only: bool = True


@dataclass(frozen=True)
class FrozenPolicyGenerationRequest:
    request_id: str
    request_schema_version: str
    generation_mode: str
    dry_run: bool
    validation_split_source: str
    synthetic_only: bool
    no_oracle: bool
    no_body_dump: bool
    no_raw_rows: bool
    no_logits_dump: bool
    metadata_only: bool
    temperature_policy_status: str | None
    temperature_policy_source_split: str | None
    threshold_policy_status: str | None
    threshold_policy_source_split: str | None
    abstention_policy_status: str | None
    abstention_policy_source_split: str | None
    output_policy_status: str | None
    output_artifact_body_suppressed: bool
    output_would_write_artifact: bool
    output_artifact_write_mode: str
    expected_failure_marker: str | None = None


@dataclass(frozen=True)
class FrozenPolicyGenerationInputPointer:
    pointer_id: str
    pointer_schema_version: str
    fixture_case_label: str
    fixture_family: str
    input_validation_status: str
    validation_split_available: bool
    selective_prediction_validation_status: str
    frozen_policy_validation_status: str
    validation_reference_ids: tuple[str, ...]
    synthetic_only: bool
    no_oracle: bool
    metadata_only: bool


@dataclass(frozen=True)
class FrozenPolicyGenerationPlan:
    request_id: str
    pointer_id: str
    generation_mode: str
    scaffold_status_candidate: str
    reason_codes: tuple[str, ...] = field(default_factory=tuple)
    failed_checks: tuple[str, ...] = field(default_factory=tuple)
    validation_reference_ids: tuple[str, ...] = field(default_factory=tuple)
    safety_summary: FrozenPolicyGenerationScaffoldSafetySummary = field(
        default_factory=FrozenPolicyGenerationScaffoldSafetySummary
    )
    request: FrozenPolicyGenerationRequest | None = None
    pointer: FrozenPolicyGenerationInputPointer | None = None


@dataclass(frozen=True)
class FrozenPolicyGenerationScaffoldResult:
    scaffold_status: str
    reason_codes: tuple[str, ...] = field(default_factory=tuple)
    failed_checks: tuple[str, ...] = field(default_factory=tuple)
    request_id: str | None = None
    pointer_id: str | None = None
    validation_reference_ids: tuple[str, ...] = field(default_factory=tuple)
    generation_request_schema_version: str | None = None
    pointer_schema_version: str | None = None
    scaffold_schema_version: str = SCAFFOLD_RESULT_SCHEMA_VERSION
    validation_schema_version: str = RUNTIME_SCHEMA_VERSION
    input_validation_status: str | None = None
    selective_prediction_validation_status: str | None = None
    frozen_policy_validation_status: str | None = None
    validation_split_available: bool | None = None
    temperature_policy_status: str | None = None
    threshold_policy_status: str | None = None
    abstention_policy_status: str | None = None
    output_policy_status: str | None = None
    safety_status: str = "fail_closed"
    content_suppressed: bool = True
    no_raw_rows: bool = True
    no_logits_dump: bool = True
    no_request_body: bool = True
    no_generated_artifact_body: bool = True
    artifact_body_suppressed: bool = True
    no_private_paths: bool = True
    no_performance_claims: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    test_tuning_checked: bool = True
    scoring_feedback_checked: bool = True
    private_path_scan_checked: bool = True
    performance_claim_scan_checked: bool = True
    generated_artifact_written: bool = False
    generated_artifact_body_available: bool = False
    would_write_artifact: bool = False
    artifact_write_mode: str = "dry_run_metadata_only"
    metadata_only: bool = True
    safe_summary: str = "metadata_only_scaffold_result"


class _FrozenPolicyGenerationScaffoldInputError(Exception):
    def __init__(self, error: FrozenPolicyGenerationScaffoldError) -> None:
        super().__init__(error.reason_code)
        self.error = error


def load_frozen_policy_generation_request(
    path: Path | str,
) -> FrozenPolicyGenerationRequest:
    value = _read_json_object(
        Path(path),
        missing_code="missing_request",
        malformed_code="malformed_request",
        input_kind="request",
    )
    _require_fields(value, REQUIRED_REQUEST_FIELDS, "request")
    schema_version = _safe_str(value.get("request_schema_version"))
    if schema_version != REQUEST_SCHEMA_VERSION:
        _raise_input_error("unknown_schema_version", "schema_version", "request")
    generation_mode = _safe_str(value.get("generation_mode"))
    if generation_mode not in SUPPORTED_GENERATION_MODES:
        _raise_input_error(
            "unsupported_generation_mode", "generation_mode", "request"
        )
    output_policy = _safe_mapping(value.get("output_policy"))
    temperature_policy = _safe_mapping(value.get("temperature_policy"))
    threshold_policy = _safe_mapping(value.get("threshold_policy"))
    abstention_policy = _safe_mapping(value.get("abstention_policy"))
    return FrozenPolicyGenerationRequest(
        request_id=_safe_str(value.get("request_id")),
        request_schema_version=schema_version,
        generation_mode=generation_mode,
        dry_run=_safe_bool(value.get("dry_run")),
        validation_split_source=_safe_str(value.get("validation_split_source")),
        synthetic_only=_safe_bool(value.get("synthetic_only")),
        no_oracle=_safe_bool(value.get("no_oracle")),
        no_body_dump=_safe_bool(value.get("no_body_dump")),
        no_raw_rows=_safe_bool(value.get("no_raw_rows")),
        no_logits_dump=_safe_bool(value.get("no_logits_dump")),
        metadata_only=_safe_bool(value.get("metadata_only")),
        temperature_policy_status=_policy_status(temperature_policy),
        temperature_policy_source_split=_safe_optional_str(
            temperature_policy.get("source_split")
        ),
        threshold_policy_status=_policy_status(threshold_policy),
        threshold_policy_source_split=_safe_optional_str(
            threshold_policy.get("source_split")
        ),
        abstention_policy_status=_policy_status(abstention_policy),
        abstention_policy_source_split=_safe_optional_str(
            abstention_policy.get("source_split")
        ),
        output_policy_status=_policy_status(output_policy),
        output_artifact_body_suppressed=_safe_bool(
            output_policy.get("artifact_body_suppressed"), default=True
        ),
        output_would_write_artifact=_safe_bool(
            output_policy.get("would_write_artifact"), default=False
        ),
        output_artifact_write_mode=_safe_str(
            output_policy.get("artifact_write_mode"),
            default="dry_run_metadata_only",
        ),
        expected_failure_marker=_safe_optional_str(
            value.get("expected_failure_marker")
        ),
    )


def load_frozen_policy_generation_input_pointer(
    path: Path | str,
) -> FrozenPolicyGenerationInputPointer:
    value = _read_json_object(
        Path(path),
        missing_code="missing_pointer",
        malformed_code="malformed_pointer",
        input_kind="pointer",
    )
    _require_fields(value, REQUIRED_POINTER_FIELDS, "pointer")
    schema_version = _safe_str(value.get("pointer_schema_version"))
    if schema_version != POINTER_SCHEMA_VERSION:
        _raise_input_error("unknown_schema_version", "schema_version", "pointer")
    fixture_case_label = _safe_str(value.get("fixture_case_label"))
    reference = _safe_str(value.get("relative_fixture_reference"))
    return FrozenPolicyGenerationInputPointer(
        pointer_id=fixture_case_label,
        pointer_schema_version=schema_version,
        fixture_case_label=fixture_case_label,
        fixture_family=_safe_str(value.get("fixture_family")),
        input_validation_status=_safe_str(value.get("input_validation_status")),
        validation_split_available=_safe_bool(
            value.get("validation_split_available")
        ),
        selective_prediction_validation_status=_safe_str(
            value.get("selective_prediction_validation_status")
        ),
        frozen_policy_validation_status=_safe_str(
            value.get("frozen_policy_validation_status")
        ),
        validation_reference_ids=(reference,) if reference else (),
        synthetic_only=_safe_bool(value.get("synthetic_only")),
        no_oracle=_safe_bool(value.get("no_oracle")),
        metadata_only=_safe_bool(value.get("metadata_only")),
    )


def build_frozen_policy_generation_plan(
    request: FrozenPolicyGenerationRequest,
    pointer: FrozenPolicyGenerationInputPointer,
) -> FrozenPolicyGenerationPlan:
    reason_codes = _derive_reason_codes(request, pointer)
    failed_checks = _failed_checks_for_reason_codes(reason_codes)
    scaffold_status = "fail" if reason_codes else "pass"
    return FrozenPolicyGenerationPlan(
        request_id=request.request_id,
        pointer_id=pointer.pointer_id,
        generation_mode=request.generation_mode,
        scaffold_status_candidate=scaffold_status,
        reason_codes=tuple(reason_codes),
        failed_checks=tuple(failed_checks),
        validation_reference_ids=pointer.validation_reference_ids,
        request=request,
        pointer=pointer,
    )


def validate_frozen_policy_generation_plan(
    plan: FrozenPolicyGenerationPlan,
) -> FrozenPolicyGenerationScaffoldResult:
    request = plan.request
    pointer = plan.pointer
    scaffold_status = plan.scaffold_status_candidate
    return FrozenPolicyGenerationScaffoldResult(
        scaffold_status=scaffold_status,
        reason_codes=plan.reason_codes,
        failed_checks=plan.failed_checks,
        request_id=plan.request_id,
        pointer_id=plan.pointer_id,
        validation_reference_ids=plan.validation_reference_ids,
        generation_request_schema_version=(
            request.request_schema_version if request else None
        ),
        pointer_schema_version=pointer.pointer_schema_version if pointer else None,
        input_validation_status=pointer.input_validation_status if pointer else None,
        selective_prediction_validation_status=(
            pointer.selective_prediction_validation_status if pointer else None
        ),
        frozen_policy_validation_status=(
            pointer.frozen_policy_validation_status if pointer else None
        ),
        validation_split_available=(
            pointer.validation_split_available if pointer else None
        ),
        temperature_policy_status=(
            request.temperature_policy_status if request else None
        ),
        threshold_policy_status=request.threshold_policy_status if request else None,
        abstention_policy_status=(
            request.abstention_policy_status if request else None
        ),
        output_policy_status=request.output_policy_status if request else None,
        safety_status="pass" if scaffold_status == "pass" else "fail_closed",
        artifact_write_mode=(
            request.output_artifact_write_mode
            if request
            else "dry_run_metadata_only"
        ),
    )


def run_frozen_policy_generation_scaffold(
    request_path: Path | str,
    pointer_path: Path | str,
) -> FrozenPolicyGenerationScaffoldResult:
    try:
        request = load_frozen_policy_generation_request(request_path)
        pointer = load_frozen_policy_generation_input_pointer(pointer_path)
        plan = build_frozen_policy_generation_plan(request, pointer)
        return validate_frozen_policy_generation_plan(plan)
    except _FrozenPolicyGenerationScaffoldInputError as exc:
        return _input_error_result(exc.error)


def summarize_frozen_policy_generation_scaffold_result(
    result: FrozenPolicyGenerationScaffoldResult,
) -> dict[str, Any]:
    return {
        "validation_schema_version": result.validation_schema_version,
        "scaffold_schema_version": result.scaffold_schema_version,
        "scaffold_status": result.scaffold_status,
        "reason_codes": list(result.reason_codes),
        "failed_checks": list(result.failed_checks),
        "request_id": result.request_id,
        "pointer_id": result.pointer_id,
        "validation_reference_ids": list(result.validation_reference_ids),
        "generation_request_schema_version": (
            result.generation_request_schema_version
        ),
        "pointer_schema_version": result.pointer_schema_version,
        "input_validation_status": result.input_validation_status,
        "selective_prediction_validation_status": (
            result.selective_prediction_validation_status
        ),
        "frozen_policy_validation_status": result.frozen_policy_validation_status,
        "validation_split_available": result.validation_split_available,
        "temperature_policy_status": result.temperature_policy_status,
        "threshold_policy_status": result.threshold_policy_status,
        "abstention_policy_status": result.abstention_policy_status,
        "output_policy_status": result.output_policy_status,
        "safety_status": result.safety_status,
        "content_suppressed": result.content_suppressed,
        "artifact_body_suppressed": result.artifact_body_suppressed,
        "no_raw_rows": result.no_raw_rows,
        "no_logits_dump": result.no_logits_dump,
        "no_request_body": result.no_request_body,
        "no_generated_artifact_body": result.no_generated_artifact_body,
        "no_private_paths": result.no_private_paths,
        "no_performance_claims": result.no_performance_claims,
        "synthetic_only_checked": result.synthetic_only_checked,
        "no_oracle_checked": result.no_oracle_checked,
        "test_tuning_checked": result.test_tuning_checked,
        "scoring_feedback_checked": result.scoring_feedback_checked,
        "private_path_scan_checked": result.private_path_scan_checked,
        "performance_claim_scan_checked": result.performance_claim_scan_checked,
        "generated_artifact_written": result.generated_artifact_written,
        "generated_artifact_body_available": (
            result.generated_artifact_body_available
        ),
        "would_write_artifact": result.would_write_artifact,
        "artifact_write_mode": result.artifact_write_mode,
        "metadata_only": result.metadata_only,
        "safe_summary": result.safe_summary,
    }


def _read_json_object(
    path: Path,
    *,
    missing_code: str,
    malformed_code: str,
    input_kind: str,
) -> dict[str, Any]:
    if _path_has_unsafe_part(path):
        _raise_input_error("unsafe_path", "path_safety", input_kind)
    if not path.is_file():
        _raise_input_error(missing_code, f"{input_kind}_path", input_kind)
    try:
        with path.open(encoding="utf-8") as file:
            value = json.load(file)
    except (OSError, json.JSONDecodeError):
        _raise_input_error(malformed_code, f"{input_kind}_json", input_kind)
    if not isinstance(value, dict):
        _raise_input_error(malformed_code, f"{input_kind}_json", input_kind)
    if _contains_payload_key(value):
        _raise_input_error(malformed_code, f"{input_kind}_payload", input_kind)
    return value


def _require_fields(
    value: dict[str, Any],
    required_fields: tuple[str, ...],
    input_kind: str,
) -> None:
    if any(field_name not in value for field_name in required_fields):
        _raise_input_error("missing_required_field", "required_fields", input_kind)


def _derive_reason_codes(
    request: FrozenPolicyGenerationRequest,
    pointer: FrozenPolicyGenerationInputPointer,
) -> list[str]:
    reasons: set[str] = set()
    if request.expected_failure_marker in KNOWN_INVALID_REASON_CODES:
        reasons.add(request.expected_failure_marker)
    case_reason = pointer.fixture_case_label.split("/")[-1]
    if case_reason in KNOWN_INVALID_REASON_CODES:
        reasons.add(case_reason)
    if request.validation_split_source == "missing":
        reasons.add("missing_validation_split")
    if pointer.validation_split_available is False:
        reasons.add("missing_validation_split")
    if request.temperature_policy_source_split == "test":
        reasons.add("test_temperature_tuning")
    if request.threshold_policy_source_split == "test":
        reasons.add("test_threshold_tuning")
    if request.abstention_policy_source_split == "test":
        reasons.add("test_threshold_tuning")
    if not request.no_raw_rows:
        reasons.add("raw_rows_carryover")
    if not request.no_logits_dump:
        reasons.add("logits_dump_carryover")
    if not request.no_body_dump or not request.output_artifact_body_suppressed:
        reasons.add("generated_artifact_body_leakage")
    if not request.no_oracle or not pointer.no_oracle:
        reasons.add("scoring_feedback_violation")
    if request.synthetic_only is False or pointer.synthetic_only is False:
        reasons.add("output_policy_not_safe")
    if request.metadata_only is False or pointer.metadata_only is False:
        reasons.add("output_policy_not_safe")
    return _order_reason_codes(reasons)


def _order_reason_codes(reason_codes: set[str]) -> list[str]:
    known = [code for code in REASON_CODE_ORDER if code in reason_codes]
    unknown = sorted(reason_codes.difference(REASON_CODE_ORDER))
    return known + unknown


def _failed_checks_for_reason_codes(reason_codes: list[str]) -> list[str]:
    checks: list[str] = []
    for reason_code in reason_codes:
        for check in REASON_FAILED_CHECKS.get(reason_code, (reason_code,)):
            if check not in checks:
                checks.append(check)
    return checks


def _policy_status(policy: dict[str, Any]) -> str | None:
    status = policy.get("status")
    if status == "invalid":
        return "fail"
    return _safe_optional_str(status)


def _safe_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_bool(value: Any, *, default: bool = False) -> bool:
    return value if isinstance(value, bool) else default


def _safe_str(value: Any, *, default: str = "") -> str:
    return value if isinstance(value, str) else default


def _safe_optional_str(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _input_error_result(
    error: FrozenPolicyGenerationScaffoldError,
) -> FrozenPolicyGenerationScaffoldResult:
    return FrozenPolicyGenerationScaffoldResult(
        scaffold_status="input_error",
        reason_codes=(error.reason_code,),
        failed_checks=(error.failed_check,),
        safety_status="fail_closed",
    )


def _raise_input_error(reason_code: str, failed_check: str, input_kind: str) -> None:
    raise _FrozenPolicyGenerationScaffoldInputError(
        FrozenPolicyGenerationScaffoldError(
            reason_code=reason_code,
            failed_check=failed_check,
            input_kind=input_kind,
        )
    )


def _path_has_unsafe_part(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    return bool(parts.intersection(UNSAFE_PATH_PARTS))


def _contains_payload_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).lower() in BODY_PAYLOAD_KEYS:
                return True
            if _contains_payload_key(nested):
                return True
    elif isinstance(value, list):
        return any(_contains_payload_key(item) for item in value)
    return False
