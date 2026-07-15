"""Validate shared Web logger Unicode/hash vector fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

MODE = "web_logger_unicode_hash_vector_validation"
SCHEMA_VERSION = "web_logger_unicode_hash_vectors_v0.1"

PASS_STATUS = "pass"
USAGE_ERROR_STATUS = "usage_error"
FAIL_CLOSED_STATUS = "fail_closed"
MISMATCH_STATUS = "mismatch"

EXPECTED_TOP_LEVEL_METADATA: Mapping[str, Any] = {
    "vector_schema_version": SCHEMA_VERSION,
    "position_unit": "utf16_code_unit",
    "hash_algorithm": "SHA-256",
    "hash_encoding": "UTF-8",
    "unicode_normalization": "none",
    "newline_normalization": "none",
    "trailing_newline_policy": "preserve_as_is",
    "hash_output_format": "lowercase_hex",
    "source_text_policy": "synthetic_minimal_text_only",
    "real_data_allowed": False,
}

REQUIRED_TOP_LEVEL_FIELDS = (
    *EXPECTED_TOP_LEVEL_METADATA.keys(),
    "vectors",
)

REQUIRED_VECTOR_FIELDS = (
    "vector_id",
    "category",
    "priority",
    "source_text",
    "source_text_description",
    "utf16_code_unit_length",
    "utf8_byte_length",
    "code_point_count",
    "hash_sha256_utf8_lowercase_hex",
    "offset_cases",
    "expected_failures",
    "notes",
)

REQUIRED_OFFSET_CASE_FIELDS = (
    "case_id",
    "utf16_start",
    "utf16_end",
    "expected_utf8_start_byte",
    "expected_utf8_end_byte",
    "expected_selected_text",
    "expected_status",
    "reason_code",
)

REQUIRED_FAILURE_FIELDS = (
    "failure_id",
    "utf16_start",
    "utf16_end",
    "expected_status",
    "reason_code",
    "raw_text_emission_allowed",
    "public_safe_note",
)

HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")
VECTOR_ID_PATTERN = re.compile(r"^V[0-9]{3}$")
PRIORITIES = frozenset({"P0", "P1", "P2"})
VALID_OFFSET_STATUSES = frozenset({"pass", "valid"})
EXPECTED_FAILURE_STATUSES = frozenset({"validation_error", "fail_closed"})


@dataclass(frozen=True)
class ValidationIssue:
    status: str
    reason_code: str
    vector_id: str = ""
    case_id: str = ""
    field_name: str = ""


@dataclass
class ValidationSummary:
    schema_version: str = SCHEMA_VERSION
    status: str = PASS_STATUS
    reason_code: str = "none"
    vector_count: int = 0
    valid_offset_case_count: int = 0
    expected_failure_count: int = 0
    hash_checked_count: int = 0
    utf16_length_checked_count: int = 0
    utf8_length_checked_count: int = 0
    offset_mapping_checked_count: int = 0
    invalid_offset_case_count: int = 0
    forbidden_content_detected_count: int = 0
    real_data_marker_detected_count: int = 0
    private_path_detected_count: int = 0
    absolute_path_detected_count: int = 0
    raw_payload_detected_count: int = 0
    content_suppressed: bool = True
    public_safe_output: bool = True
    production_readiness_claimed: bool = False
    real_data_readiness_claimed: bool = False
    performance_claims_present: bool = False
    issues: list[ValidationIssue] = field(default_factory=list)

    def add_issue(
        self,
        status: str,
        reason_code: str,
        *,
        vector_id: str = "",
        case_id: str = "",
        field_name: str = "",
    ) -> None:
        self.issues.append(
            ValidationIssue(
                status=status,
                reason_code=reason_code,
                vector_id=vector_id,
                case_id=case_id,
                field_name=field_name,
            )
        )
        if self.status == PASS_STATUS:
            self.status = status
            self.reason_code = reason_code


def validate_fixture(fixture: str | Path) -> ValidationSummary:
    path = Path(fixture)
    summary = ValidationSummary()
    if not path.exists():
        summary.add_issue(USAGE_ERROR_STATUS, "fixture_missing", field_name="fixture")
        return summary
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        summary.add_issue(USAGE_ERROR_STATUS, "malformed_json", field_name="fixture")
        return summary
    except OSError:
        summary.add_issue(USAGE_ERROR_STATUS, "fixture_read_error", field_name="fixture")
        return summary
    return validate_data(data)


def validate_data(data: Any) -> ValidationSummary:
    summary = ValidationSummary()
    if not isinstance(data, Mapping):
        summary.add_issue(USAGE_ERROR_STATUS, "fixture_not_object", field_name="fixture")
        return summary

    _validate_top_level(data, summary)
    vectors = data.get("vectors")
    if not isinstance(vectors, list) or not vectors:
        return summary

    summary.vector_count = len(vectors)
    seen_ids: set[str] = set()
    for index, vector in enumerate(vectors):
        if not isinstance(vector, Mapping):
            summary.add_issue(
                USAGE_ERROR_STATUS,
                "vector_not_object",
                vector_id=f"index_{index}",
                field_name="vectors",
            )
            continue
        _validate_vector(vector, seen_ids, summary)

    _scan_forbidden_markers(data, summary)
    return summary


def render_summary(summary: ValidationSummary) -> str:
    fields: Sequence[tuple[str, Any]] = (
        ("mode", MODE),
        ("schema_version", summary.schema_version),
        ("status", summary.status),
        ("reason_code", summary.reason_code),
        ("vector_count", summary.vector_count),
        ("valid_offset_case_count", summary.valid_offset_case_count),
        ("expected_failure_count", summary.expected_failure_count),
        ("hash_checked_count", summary.hash_checked_count),
        ("utf16_length_checked_count", summary.utf16_length_checked_count),
        ("utf8_length_checked_count", summary.utf8_length_checked_count),
        ("offset_mapping_checked_count", summary.offset_mapping_checked_count),
        ("invalid_offset_case_count", summary.invalid_offset_case_count),
        ("forbidden_content_detected_count", summary.forbidden_content_detected_count),
        ("real_data_marker_detected_count", summary.real_data_marker_detected_count),
        ("private_path_detected_count", summary.private_path_detected_count),
        ("absolute_path_detected_count", summary.absolute_path_detected_count),
        ("raw_payload_detected_count", summary.raw_payload_detected_count),
        ("content_suppressed", summary.content_suppressed),
        ("public_safe_output", summary.public_safe_output),
        ("production_readiness_claimed", summary.production_readiness_claimed),
        ("real_data_readiness_claimed", summary.real_data_readiness_claimed),
        ("performance_claims_present", summary.performance_claims_present),
    )
    return "\n".join(f"{key}={_format_value(value)}" for key, value in fields)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Web logger Unicode/hash vector fixtures."
    )
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--summary-only", action="store_true", required=True)
    args = parser.parse_args(argv)

    try:
        summary = validate_fixture(args.fixture)
    except Exception:
        summary = ValidationSummary()
        summary.add_issue(FAIL_CLOSED_STATUS, "internal_exception")
    print(render_summary(summary))
    return 0 if summary.status == PASS_STATUS else 1


def _validate_top_level(data: Mapping[str, Any], summary: ValidationSummary) -> None:
    for field_name in REQUIRED_TOP_LEVEL_FIELDS:
        if field_name not in data:
            summary.add_issue(
                USAGE_ERROR_STATUS,
                "missing_required_field",
                field_name=field_name,
            )
            return

    summary.schema_version = str(data.get("vector_schema_version", SCHEMA_VERSION))
    if data.get("vector_schema_version") != SCHEMA_VERSION:
        summary.add_issue(
            USAGE_ERROR_STATUS,
            "unsupported_schema_version",
            field_name="vector_schema_version",
        )
        return

    for field_name, expected in EXPECTED_TOP_LEVEL_METADATA.items():
        actual = data.get(field_name)
        if actual != expected:
            reason_code = _top_level_reason_code(field_name)
            summary.add_issue(
                FAIL_CLOSED_STATUS,
                reason_code,
                field_name=field_name,
            )
            return

    vectors = data.get("vectors")
    if not isinstance(vectors, list):
        summary.add_issue(USAGE_ERROR_STATUS, "vectors_not_array", field_name="vectors")
        return
    if not vectors:
        summary.add_issue(USAGE_ERROR_STATUS, "vectors_empty", field_name="vectors")


def _validate_vector(
    vector: Mapping[str, Any],
    seen_ids: set[str],
    summary: ValidationSummary,
) -> None:
    vector_id = str(vector.get("vector_id", ""))
    for field_name in REQUIRED_VECTOR_FIELDS:
        if field_name not in vector:
            summary.add_issue(
                USAGE_ERROR_STATUS,
                "missing_required_field",
                vector_id=vector_id,
                field_name=field_name,
            )
            return

    if not VECTOR_ID_PATTERN.match(vector_id):
        summary.add_issue(
            USAGE_ERROR_STATUS,
            "invalid_vector_id_format",
            vector_id=vector_id,
            field_name="vector_id",
        )
        return
    if vector_id in seen_ids:
        summary.add_issue(
            USAGE_ERROR_STATUS,
            "duplicate_vector_id",
            vector_id=vector_id,
            field_name="vector_id",
        )
        return
    seen_ids.add(vector_id)

    if not _is_nonempty_string(vector.get("category")):
        summary.add_issue(
            USAGE_ERROR_STATUS,
            "invalid_category",
            vector_id=vector_id,
            field_name="category",
        )
        return
    if vector.get("priority") not in PRIORITIES:
        summary.add_issue(
            USAGE_ERROR_STATUS,
            "invalid_priority",
            vector_id=vector_id,
            field_name="priority",
        )
        return

    source_text = vector.get("source_text")
    if not isinstance(source_text, str):
        summary.add_issue(
            USAGE_ERROR_STATUS,
            "source_text_not_string",
            vector_id=vector_id,
            field_name="source_text",
        )
        return
    if not _is_nonempty_string(vector.get("source_text_description")):
        summary.add_issue(
            USAGE_ERROR_STATUS,
            "invalid_source_text_description",
            vector_id=vector_id,
            field_name="source_text_description",
        )
        return

    boundary_map = _utf16_to_utf8_boundary_map(source_text)
    if boundary_map is None:
        summary.add_issue(
            FAIL_CLOSED_STATUS,
            "invalid_unicode_text",
            vector_id=vector_id,
            field_name="source_text",
        )
        return

    _validate_lengths_and_hash(vector, source_text, vector_id, summary)
    _validate_offset_cases(vector, source_text, boundary_map, vector_id, summary)
    _validate_expected_failures(vector, boundary_map, vector_id, summary)


def _validate_lengths_and_hash(
    vector: Mapping[str, Any],
    source_text: str,
    vector_id: str,
    summary: ValidationSummary,
) -> None:
    expected_utf16_length = _utf16_code_unit_length(source_text)
    if vector.get("utf16_code_unit_length") != expected_utf16_length:
        summary.add_issue(
            MISMATCH_STATUS,
            "utf16_length_mismatch",
            vector_id=vector_id,
            field_name="utf16_code_unit_length",
        )
        return
    summary.utf16_length_checked_count += 1

    expected_utf8_length = len(source_text.encode("utf-8"))
    if vector.get("utf8_byte_length") != expected_utf8_length:
        summary.add_issue(
            MISMATCH_STATUS,
            "utf8_length_mismatch",
            vector_id=vector_id,
            field_name="utf8_byte_length",
        )
        return
    summary.utf8_length_checked_count += 1

    if vector.get("code_point_count") != len(source_text):
        summary.add_issue(
            MISMATCH_STATUS,
            "code_point_count_mismatch",
            vector_id=vector_id,
            field_name="code_point_count",
        )
        return

    hash_value = vector.get("hash_sha256_utf8_lowercase_hex")
    if not isinstance(hash_value, str) or not HASH_PATTERN.fullmatch(hash_value):
        summary.add_issue(
            MISMATCH_STATUS,
            "invalid_hash_format",
            vector_id=vector_id,
            field_name="hash_sha256_utf8_lowercase_hex",
        )
        return
    expected_hash = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    if hash_value != expected_hash:
        summary.add_issue(
            MISMATCH_STATUS,
            "hash_mismatch",
            vector_id=vector_id,
            field_name="hash_sha256_utf8_lowercase_hex",
        )
        return
    summary.hash_checked_count += 1


def _validate_offset_cases(
    vector: Mapping[str, Any],
    source_text: str,
    boundary_map: Mapping[int, int],
    vector_id: str,
    summary: ValidationSummary,
) -> None:
    offset_cases = vector.get("offset_cases")
    if not isinstance(offset_cases, list):
        summary.add_issue(
            USAGE_ERROR_STATUS,
            "offset_cases_not_array",
            vector_id=vector_id,
            field_name="offset_cases",
        )
        return

    source_bytes = source_text.encode("utf-8")
    for offset_case in offset_cases:
        if not isinstance(offset_case, Mapping):
            summary.add_issue(
                USAGE_ERROR_STATUS,
                "offset_case_not_object",
                vector_id=vector_id,
                field_name="offset_cases",
            )
            return
        case_id = str(offset_case.get("case_id", ""))
        for field_name in REQUIRED_OFFSET_CASE_FIELDS:
            if field_name not in offset_case:
                summary.add_issue(
                    USAGE_ERROR_STATUS,
                    "missing_required_field",
                    vector_id=vector_id,
                    case_id=case_id,
                    field_name=field_name,
                )
                return
        start = offset_case.get("utf16_start")
        end = offset_case.get("utf16_end")
        if not _is_nonnegative_int(start) or not _is_nonnegative_int(end):
            summary.add_issue(
                MISMATCH_STATUS,
                "invalid_offset_type",
                vector_id=vector_id,
                case_id=case_id,
            )
            return
        if start > end:
            summary.add_issue(
                MISMATCH_STATUS,
                "offset_range_inverted",
                vector_id=vector_id,
                case_id=case_id,
            )
            return
        if start not in boundary_map or end not in boundary_map:
            summary.add_issue(
                MISMATCH_STATUS,
                "invalid_utf16_boundary",
                vector_id=vector_id,
                case_id=case_id,
            )
            return
        if offset_case.get("expected_status") not in VALID_OFFSET_STATUSES:
            summary.add_issue(
                USAGE_ERROR_STATUS,
                "invalid_expected_status",
                vector_id=vector_id,
                case_id=case_id,
                field_name="expected_status",
            )
            return
        if offset_case.get("reason_code") != "none":
            summary.add_issue(
                MISMATCH_STATUS,
                "unexpected_reason_code",
                vector_id=vector_id,
                case_id=case_id,
                field_name="reason_code",
            )
            return

        expected_start = boundary_map[start]
        expected_end = boundary_map[end]
        if (
            offset_case.get("expected_utf8_start_byte") != expected_start
            or offset_case.get("expected_utf8_end_byte") != expected_end
        ):
            summary.add_issue(
                MISMATCH_STATUS,
                "offset_mapping_mismatch",
                vector_id=vector_id,
                case_id=case_id,
            )
            return
        selected = source_bytes[expected_start:expected_end].decode("utf-8")
        if offset_case.get("expected_selected_text") != selected:
            summary.add_issue(
                MISMATCH_STATUS,
                "selected_text_mismatch",
                vector_id=vector_id,
                case_id=case_id,
            )
            return

        summary.valid_offset_case_count += 1
        summary.offset_mapping_checked_count += 1


def _validate_expected_failures(
    vector: Mapping[str, Any],
    boundary_map: Mapping[int, int],
    vector_id: str,
    summary: ValidationSummary,
) -> None:
    expected_failures = vector.get("expected_failures")
    if not isinstance(expected_failures, list):
        summary.add_issue(
            USAGE_ERROR_STATUS,
            "expected_failures_not_array",
            vector_id=vector_id,
            field_name="expected_failures",
        )
        return

    for failure in expected_failures:
        if not isinstance(failure, Mapping):
            summary.add_issue(
                USAGE_ERROR_STATUS,
                "expected_failure_not_object",
                vector_id=vector_id,
                field_name="expected_failures",
            )
            return
        failure_id = str(failure.get("failure_id", ""))
        for field_name in REQUIRED_FAILURE_FIELDS:
            if field_name not in failure:
                summary.add_issue(
                    USAGE_ERROR_STATUS,
                    "missing_required_field",
                    vector_id=vector_id,
                    case_id=failure_id,
                    field_name=field_name,
                )
                return
        if failure.get("expected_status") not in EXPECTED_FAILURE_STATUSES:
            summary.add_issue(
                USAGE_ERROR_STATUS,
                "invalid_expected_status",
                vector_id=vector_id,
                case_id=failure_id,
                field_name="expected_status",
            )
            return
        if not _is_nonempty_string(failure.get("reason_code")):
            summary.add_issue(
                USAGE_ERROR_STATUS,
                "missing_reason_code",
                vector_id=vector_id,
                case_id=failure_id,
                field_name="reason_code",
            )
            return
        if failure.get("raw_text_emission_allowed") is not False:
            summary.add_issue(
                FAIL_CLOSED_STATUS,
                "raw_text_emission_allowed",
                vector_id=vector_id,
                case_id=failure_id,
                field_name="raw_text_emission_allowed",
            )
            return
        if not _is_nonempty_string(failure.get("public_safe_note")):
            summary.add_issue(
                USAGE_ERROR_STATUS,
                "missing_public_safe_note",
                vector_id=vector_id,
                case_id=failure_id,
                field_name="public_safe_note",
            )
            return

        if not _is_expected_failure_invalid(failure, boundary_map):
            summary.add_issue(
                MISMATCH_STATUS,
                "expected_failure_condition_valid",
                vector_id=vector_id,
                case_id=failure_id,
            )
            return
        summary.expected_failure_count += 1
        summary.invalid_offset_case_count += 1


def _scan_forbidden_markers(data: Mapping[str, Any], summary: ValidationSummary) -> None:
    counts = {
        "real_data": 0,
        "private_path": 0,
        "absolute_path": 0,
        "raw_payload": 0,
        "other": 0,
    }
    for key_path, value in _iter_text_fields(data):
        if key_path.endswith(".non_real_data_notice") or key_path.endswith(".no_oracle_notice"):
            continue
        lowered = value.lower()
        if "real participant data marker" in lowered or "real_participant_data" in lowered:
            counts["real_data"] += 1
        if "raw learner text marker" in lowered or "raw_learner_text" in lowered:
            counts["other"] += 1
        if "private path marker" in lowered or "private_path" in lowered:
            counts["private_path"] += 1
        if (
            "absolute local path marker" in lowered
            or lowered.startswith("/users/")
            or lowered.startswith("/home/")
            or lowered.startswith("c:\\")
        ):
            counts["absolute_path"] += 1
        if "raw event payload body marker" in lowered or "raw_event_payload" in lowered:
            counts["raw_payload"] += 1
        if (
            "logits marker" in lowered
            or "probabilities marker" in lowered
            or "performance metric body marker" in lowered
            or "performance_metric_body" in lowered
        ):
            counts["other"] += 1

    summary.real_data_marker_detected_count = counts["real_data"]
    summary.private_path_detected_count = counts["private_path"]
    summary.absolute_path_detected_count = counts["absolute_path"]
    summary.raw_payload_detected_count = counts["raw_payload"]
    summary.forbidden_content_detected_count = sum(counts.values())
    if summary.forbidden_content_detected_count:
        summary.add_issue(FAIL_CLOSED_STATUS, "forbidden_content_marker")


def _is_expected_failure_invalid(
    failure: Mapping[str, Any],
    boundary_map: Mapping[int, int],
) -> bool:
    start = failure.get("utf16_start")
    end = failure.get("utf16_end")
    if not _is_nonnegative_int(start) or not _is_nonnegative_int(end):
        return True
    if start > end:
        return True
    if start not in boundary_map or end not in boundary_map:
        return True
    return False


def _utf16_code_unit_length(source_text: str) -> int:
    return len(source_text.encode("utf-16-le")) // 2


def _utf16_to_utf8_boundary_map(source_text: str) -> dict[int, int] | None:
    mapping = {0: 0}
    utf16_offset = 0
    utf8_offset = 0
    try:
        for character in source_text:
            utf16_offset += _utf16_code_unit_length(character)
            utf8_offset += len(character.encode("utf-8"))
            mapping[utf16_offset] = utf8_offset
    except UnicodeEncodeError:
        return None
    return mapping


def _top_level_reason_code(field_name: str) -> str:
    if field_name == "position_unit":
        return "unsupported_position_unit"
    if field_name == "hash_algorithm":
        return "unsupported_hash_algorithm"
    if field_name == "hash_encoding":
        return "unsupported_hash_encoding"
    if field_name in {"unicode_normalization", "newline_normalization"}:
        return "unsupported_normalization_policy"
    if field_name == "real_data_allowed":
        return "real_data_allowed_not_false"
    return "metadata_policy_mismatch"


def _iter_text_fields(value: Any, key_path: str = "root") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield key_path, value
    elif isinstance(value, Mapping):
        for key, item in value.items():
            yield from _iter_text_fields(item, f"{key_path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _iter_text_fields(item, f"{key_path}[{index}]")


def _is_nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value)


if __name__ == "__main__":
    sys.exit(main())
