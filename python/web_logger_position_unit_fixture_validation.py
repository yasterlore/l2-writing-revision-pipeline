"""Validate Web logger position_unit schema fixture contracts."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

MODE = "web_logger_position_unit_fixture_validation"
SCHEMA_VERSION = "web_logger_position_unit_schema_fixtures_v0.1"
FIXTURE_ROOT = "tests/fixtures/web_logger_position_unit_schema"
POSITION_UNIT = "utf16_code_unit"
RESEARCH_SCHEMA_TARGET = "web_logger_position_unit_schema_v0.1"
LOGGER_SCHEMA_V2 = "kslog.raw_event.v2"
LOGGER_SCHEMA_LEGACY = "kslog.raw_event.v1"

PASS_STATUS = "pass"
FAIL_STATUS = "fail"
USAGE_ERROR_STATUS = "usage_error"

EXPECTED_COUNTS = {
    "total": 17,
    "valid": 5,
    "invalid": 11,
    "legacy": 1,
    "jsonl_records": 24,
}

REQUIRED_TOP_LEVEL_FIELDS = (
    "fixture_schema_version",
    "fixture_root",
    "purpose",
    "synthetic_only",
    "no_oracle_safe",
    "content_suppressed_expected",
    "position_unit_policy",
    "case_counts",
    "cases",
)

REQUIRED_CASE_FIELDS = (
    "case_id",
    "case_kind",
    "fixture_path",
    "expected_status",
    "expected_reason_code",
    "logger_schema_version",
    "research_schema_target",
    "position_unit",
    "expected_position_unit_policy",
    "requires_text_context",
    "should_be_checked_by_schema",
    "should_be_checked_by_validator",
    "should_be_checked_by_replay",
    "synthetic_only",
    "no_oracle_safe",
    "content_suppressed_expected",
    "notes",
)

REQUIRED_EVENT_FIELDS = (
    "logger_schema_version",
    "research_schema_target",
    "session_id",
    "participant_local_id",
    "task_id",
    "prompt_id",
    "seq",
    "timestamp_ms",
    "event_type",
    "input_type",
    "is_composing",
    "composition_id",
    "selection_start_before",
    "selection_end_before",
    "selection_start_after",
    "selection_end_after",
    "cursor_pos_before",
    "cursor_pos_after",
    "doc_len_before",
    "doc_len_after",
    "inserted_text",
    "deleted_text",
    "text_hash_before",
    "text_hash_after",
    "diff_op",
    "quality_flags",
)

ALLOWED_CASE_KINDS = frozenset({"valid", "invalid", "legacy"})
ALLOWED_EXPECTED_STATUSES = frozenset({"pass", "fail", "legacy_allowed"})
ALLOWED_EXPECTED_POSITION_UNIT_POLICIES = frozenset(
    {
        "utf16_code_unit_required",
        "v1_position_unit_not_accepted",
        "known_schema_version_required",
        "legacy_gate_required",
    }
)
ALLOWED_REASON_CODES = frozenset(
    {
        "none",
        "missing_position_unit",
        "unsupported_position_unit",
        "position_unit_schema_mismatch",
        "doc_len_before_utf16_mismatch",
        "doc_len_after_utf16_mismatch",
        "start_greater_than_end",
        "offset_beyond_utf16_length",
        "offset_inside_surrogate_pair",
        "invalid_utf16_boundary",
        "unknown_schema_version",
        "legacy_position_unit_missing_allowed",
    }
)
UNSUPPORTED_UNITS = frozenset({"byte_index", "code_point"})

FORBIDDEN_FIELD_NAMES = frozenset(
    {
        "final_text",
        "observed_after_text",
        "gold_label",
        "gold_labels",
        "post_hoc_annotation",
        "raw_learner_text",
        "real_participant_data",
        "logits",
        "probabilities",
        "performance_metric_body",
    }
)

CASE_INDEX_BODY_FIELD_NAMES = frozenset(
    {
        "raw_event_body",
        "event_body",
        "fixture_body",
        "expected_body",
        "request_body",
        "pointer_body",
        "payload_body",
    }
)

RAW_PAYLOAD_MARKERS = (
    "raw event payload",
    "raw_event_payload",
    "raw payload",
    "payload body marker",
)
RAW_LOG_MARKERS = (
    "raw log body marker",
    "raw logs marker",
    "full job output marker",
    "copied github log block marker",
    "raw cargo output marker",
)
RAW_LEARNER_MARKERS = ("raw learner text marker", "raw_learner_text")
REAL_DATA_MARKERS = ("real participant data marker", "real_participant_data")
PRIVATE_PATH_MARKERS = ("private path marker", "dropbox", "google drive")
ABSOLUTE_PATH_MARKERS = ("/users/", "/private/", "/home/", "c:\\")
LOGIT_PROBABILITY_MARKERS = ("logits", "probabilities")
PERFORMANCE_MARKERS = ("performance metric body", "performance_metric_body")


@dataclass(frozen=True)
class ValidationIssue:
    reason_code: str
    case_id: str = ""
    field_name: str = ""


@dataclass
class ValidationSummary:
    fixture_schema_version: str = SCHEMA_VERSION
    validation_status: str = PASS_STATUS
    reason_code: str = "none"
    total_cases: int = 0
    valid_cases: int = 0
    invalid_cases: int = 0
    legacy_cases: int = 0
    jsonl_record_count: int = 0
    matched_cases: int = 0
    mismatched_cases: int = 0
    input_error_cases: int = 0
    pass_cases: int = 0
    fail_cases: int = 0
    legacy_allowed_cases: int = 0
    text_context_cases: int = 0
    schema_check_cases: int = 0
    validator_check_cases: int = 0
    replay_check_cases: int = 0
    expected_reason_code_counts: Counter[str] = field(default_factory=Counter)
    observed_reason_code_counts: Counter[str] = field(default_factory=Counter)
    position_unit_policy_checked: bool = True
    utf16_length_checked_count: int = 0
    offset_boundary_checked_count: int = 0
    surrogate_boundary_checked_count: int = 0
    legacy_policy_checked: bool = True
    content_suppressed: bool = True
    fixture_body_suppressed: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    private_path_detected_count: int = 0
    absolute_path_detected_count: int = 0
    raw_payload_detected_count: int = 0
    raw_learner_text_detected_count: int = 0
    real_data_marker_detected_count: int = 0
    logits_or_probabilities_detected_count: int = 0
    performance_metric_body_detected_count: int = 0
    production_readiness_claimed: bool = False
    real_data_readiness_claimed: bool = False
    performance_claims_present: bool = False
    issues: list[ValidationIssue] = field(default_factory=list)

    def add_issue(
        self,
        reason_code: str,
        *,
        case_id: str = "",
        field_name: str = "",
        input_error: bool = True,
    ) -> None:
        self.issues.append(
            ValidationIssue(
                reason_code=reason_code,
                case_id=case_id,
                field_name=field_name,
            )
        )
        if self.validation_status == PASS_STATUS:
            self.validation_status = FAIL_STATUS
            self.reason_code = reason_code
        if input_error:
            self.input_error_cases += 1


@dataclass(frozen=True)
class CaseValidation:
    case_id: str
    expected_status: str
    expected_reason_code: str
    observed_reason_code: str
    record_count: int
    utf16_length_checked_count: int = 0
    offset_boundary_checked_count: int = 0
    surrogate_boundary_checked_count: int = 0
    input_error: bool = False


def validate_fixture_root(fixture_root: str | Path) -> ValidationSummary:
    root = Path(fixture_root)
    summary = ValidationSummary()
    if not root.exists() or not root.is_dir():
        summary.add_issue("fixture_root_missing", field_name="fixture_root")
        return summary

    index_path = root / "case_index.json"
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        summary.add_issue("case_index_missing", field_name="case_index")
        return summary
    except json.JSONDecodeError:
        summary.add_issue("case_index_malformed_json", field_name="case_index")
        return summary
    except OSError:
        summary.add_issue("case_index_read_error", field_name="case_index")
        return summary

    if not isinstance(index, Mapping):
        summary.add_issue("case_index_not_object", field_name="case_index")
        return summary

    if not _validate_index(index, root, summary):
        return summary

    cases = index["cases"]
    results: list[CaseValidation] = []
    for case in cases:
        if not isinstance(case, Mapping):
            summary.add_issue("case_not_object", field_name="cases")
            continue
        results.append(_validate_case(root, case, summary))

    _apply_case_results(index, results, summary)
    _scan_forbidden_markers(index, summary, allow_policy_text=True)
    _validate_expected_counts(summary)
    return summary


def render_summary(summary: ValidationSummary) -> str:
    fields: Sequence[tuple[str, Any]] = (
        ("mode", MODE),
        ("fixture_schema_version", summary.fixture_schema_version),
        ("validation_status", summary.validation_status),
        ("reason_code", summary.reason_code),
        ("total_cases", summary.total_cases),
        ("valid_cases", summary.valid_cases),
        ("invalid_cases", summary.invalid_cases),
        ("legacy_cases", summary.legacy_cases),
        ("jsonl_record_count", summary.jsonl_record_count),
        ("matched_cases", summary.matched_cases),
        ("mismatched_cases", summary.mismatched_cases),
        ("input_error_cases", summary.input_error_cases),
        (
            "expected_reason_code_counts",
            _format_counter(summary.expected_reason_code_counts),
        ),
        (
            "observed_reason_code_counts",
            _format_counter(summary.observed_reason_code_counts),
        ),
        ("position_unit_policy_checked", summary.position_unit_policy_checked),
        ("utf16_length_checked_count", summary.utf16_length_checked_count),
        ("offset_boundary_checked_count", summary.offset_boundary_checked_count),
        ("surrogate_boundary_checked_count", summary.surrogate_boundary_checked_count),
        ("legacy_policy_checked", summary.legacy_policy_checked),
        ("content_suppressed", summary.content_suppressed),
        ("fixture_body_suppressed", summary.fixture_body_suppressed),
        ("synthetic_only_checked", summary.synthetic_only_checked),
        ("no_oracle_checked", summary.no_oracle_checked),
        ("private_path_detected_count", summary.private_path_detected_count),
        ("absolute_path_detected_count", summary.absolute_path_detected_count),
        ("raw_payload_detected_count", summary.raw_payload_detected_count),
        ("raw_learner_text_detected_count", summary.raw_learner_text_detected_count),
        ("real_data_marker_detected_count", summary.real_data_marker_detected_count),
        (
            "logits_or_probabilities_detected_count",
            summary.logits_or_probabilities_detected_count,
        ),
        (
            "performance_metric_body_detected_count",
            summary.performance_metric_body_detected_count,
        ),
        ("production_readiness_claimed", "False"),
        ("real_data_readiness_claimed", "False"),
        ("performance_claims_present", "False"),
    )
    return "\n".join(f"{key}={_format_value(value)}" for key, value in fields)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Web logger position_unit schema fixtures."
    )
    parser.add_argument("--fixture-root", required=True)
    parser.add_argument("--summary-only", action="store_true", required=True)
    args = parser.parse_args(argv)

    try:
        summary = validate_fixture_root(args.fixture_root)
    except Exception:
        summary = ValidationSummary()
        summary.add_issue("internal_exception", input_error=True)
    print(render_summary(summary))
    return 0 if summary.validation_status == PASS_STATUS else 1


def _validate_index(
    index: Mapping[str, Any],
    root: Path,
    summary: ValidationSummary,
) -> bool:
    for field_name in REQUIRED_TOP_LEVEL_FIELDS:
        if field_name not in index:
            summary.add_issue("missing_required_field", field_name=field_name)
            return False

    summary.fixture_schema_version = str(index.get("fixture_schema_version", ""))
    expected_values = {
        "fixture_schema_version": SCHEMA_VERSION,
        "fixture_root": FIXTURE_ROOT,
        "synthetic_only": True,
        "no_oracle_safe": True,
        "content_suppressed_expected": True,
        "position_unit_policy": POSITION_UNIT,
    }
    for field_name, expected in expected_values.items():
        if index.get(field_name) != expected:
            summary.add_issue("top_level_metadata_mismatch", field_name=field_name)
            return False

    counts = index.get("case_counts")
    if not isinstance(counts, Mapping):
        summary.add_issue("case_counts_not_object", field_name="case_counts")
        return False
    for key, expected in {
        "valid": EXPECTED_COUNTS["valid"],
        "invalid": EXPECTED_COUNTS["invalid"],
        "legacy": EXPECTED_COUNTS["legacy"],
        "total": EXPECTED_COUNTS["total"],
    }.items():
        if counts.get(key) != expected:
            summary.add_issue("expected_count_mismatch", field_name=f"case_counts.{key}")
            return False

    cases = index.get("cases")
    if not isinstance(cases, list) or not cases:
        summary.add_issue("cases_not_nonempty_list", field_name="cases")
        return False

    seen_ids: set[str] = set()
    for case in cases:
        if not isinstance(case, Mapping):
            summary.add_issue("case_not_object", field_name="cases")
            return False
        case_id = str(case.get("case_id", ""))
        for field_name in REQUIRED_CASE_FIELDS:
            if field_name not in case:
                summary.add_issue(
                    "missing_required_field",
                    case_id=case_id,
                    field_name=field_name,
                )
                return False

        if not _is_nonempty_string(case_id):
            summary.add_issue("missing_case_id", field_name="case_id")
            return False
        if case_id in seen_ids:
            summary.add_issue("duplicate_case_id", case_id=case_id)
            return False
        seen_ids.add(case_id)

        if case.get("case_kind") not in ALLOWED_CASE_KINDS:
            summary.add_issue("invalid_case_kind", case_id=case_id, field_name="case_kind")
            return False
        if case.get("expected_status") not in ALLOWED_EXPECTED_STATUSES:
            summary.add_issue(
                "invalid_expected_status",
                case_id=case_id,
                field_name="expected_status",
            )
            return False
        if case.get("expected_reason_code") not in ALLOWED_REASON_CODES:
            summary.add_issue(
                "unknown_reason_code",
                case_id=case_id,
                field_name="expected_reason_code",
            )
            return False

        if not _is_nonempty_string(case.get("logger_schema_version")):
            summary.add_issue(
                "missing_required_field",
                case_id=case_id,
                field_name="logger_schema_version",
            )
            return False
        if case.get("research_schema_target") != RESEARCH_SCHEMA_TARGET:
            summary.add_issue(
                "research_schema_target_mismatch",
                case_id=case_id,
                field_name="research_schema_target",
            )
            return False
        if case.get("expected_position_unit_policy") not in (
            ALLOWED_EXPECTED_POSITION_UNIT_POLICIES
        ):
            summary.add_issue(
                "position_unit_policy_mismatch",
                case_id=case_id,
                field_name="expected_position_unit_policy",
            )
            return False
        for field_name in (
            "requires_text_context",
            "should_be_checked_by_schema",
            "should_be_checked_by_validator",
            "should_be_checked_by_replay",
        ):
            if not isinstance(case.get(field_name), bool):
                summary.add_issue(
                    "invalid_boolean_metadata",
                    case_id=case_id,
                    field_name=field_name,
                )
                return False
        for field_name in (
            "synthetic_only",
            "no_oracle_safe",
            "content_suppressed_expected",
        ):
            if case.get(field_name) is not True:
                summary.add_issue(
                    "case_safety_metadata_mismatch",
                    case_id=case_id,
                    field_name=field_name,
                )
                return False

        fixture_path = case.get("fixture_path")
        if not isinstance(fixture_path, str) or not fixture_path:
            summary.add_issue("missing_fixture_path", case_id=case_id)
            return False
        if _is_abs_or_private_path_marker(fixture_path):
            summary.add_issue("private_or_absolute_path", case_id=case_id)
            return False
        path = Path(fixture_path)
        if path.is_absolute():
            summary.add_issue("fixture_path_absolute", case_id=case_id)
            return False
        candidate = (root / path).resolve()
        root_resolved = root.resolve()
        if not _is_relative_to(candidate, root_resolved):
            summary.add_issue("fixture_path_escapes_root", case_id=case_id)
            return False
        if not candidate.exists():
            summary.add_issue("missing_fixture_path", case_id=case_id)
            return False

        for key, _value in _iter_items(case):
            if key in CASE_INDEX_BODY_FIELD_NAMES:
                summary.add_issue("case_index_embeds_body", case_id=case_id, field_name=key)
                return False

    return True


def _validate_case(
    root: Path,
    case: Mapping[str, Any],
    summary: ValidationSummary,
) -> CaseValidation:
    case_id = str(case["case_id"])
    expected_status = str(case["expected_status"])
    expected_reason_code = str(case["expected_reason_code"])
    path = root / str(case["fixture_path"])
    records, record_error = _load_jsonl(path)
    if record_error != "none":
        return CaseValidation(
            case_id,
            expected_status,
            expected_reason_code,
            record_error,
            0,
            input_error=True,
        )

    record_count = len(records)
    if record_count == 0:
        return CaseValidation(
            case_id,
            expected_status,
            expected_reason_code,
            "empty_fixture_file",
            0,
            input_error=True,
        )

    safety_reason = _validate_records_safety(case_id, records, summary)
    if safety_reason != "none":
        return CaseValidation(
            case_id,
            expected_status,
            expected_reason_code,
            safety_reason,
            record_count,
            input_error=True,
        )

    structure_reason = _validate_record_structure(records)
    if structure_reason != "none":
        return CaseValidation(
            case_id,
            expected_status,
            expected_reason_code,
            structure_reason,
            record_count,
            input_error=True,
        )

    policy_reason = _validate_position_unit_policy(case, records)
    if policy_reason != "none":
        return CaseValidation(
            case_id,
            expected_status,
            expected_reason_code,
            policy_reason,
            record_count,
        )

    observed, utf16_checks, offset_checks, surrogate_checks = _validate_utf16_contract(
        case_id, records
    )
    return CaseValidation(
        case_id,
        expected_status,
        expected_reason_code,
        observed,
        record_count,
        utf16_length_checked_count=utf16_checks,
        offset_boundary_checked_count=offset_checks,
        surrogate_boundary_checked_count=surrogate_checks,
    )


def _load_jsonl(path: Path) -> tuple[list[Mapping[str, Any]], str]:
    if path.suffix != ".jsonl":
        return [], "invalid_fixture_extension"
    records: list[Mapping[str, Any]] = []
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    return [], "jsonl_malformed_json"
                if not isinstance(record, Mapping):
                    return [], "jsonl_record_not_object"
                records.append(record)
    except FileNotFoundError:
        return [], "missing_fixture_path"
    except OSError:
        return [], "fixture_read_error"
    return records, "none"


def _validate_records_safety(
    case_id: str,
    records: Sequence[Mapping[str, Any]],
    summary: ValidationSummary,
) -> str:
    for record in records:
        for key, _value in _iter_items(record):
            if key in FORBIDDEN_FIELD_NAMES:
                _increment_forbidden_count(key, summary)
                return _forbidden_reason_code(key)
        before_counts = _forbidden_count_total(summary)
        _scan_forbidden_markers(record, summary, allow_policy_text=False)
        if _forbidden_count_total(summary) > before_counts:
            return "forbidden_content_marker"
    return "none"


def _validate_record_structure(records: Sequence[Mapping[str, Any]]) -> str:
    previous_seq: int | None = None
    for record in records:
        for field_name in REQUIRED_EVENT_FIELDS:
            if field_name not in record:
                return "missing_required_field"
        seq = record.get("seq")
        if not _is_nonnegative_int(seq):
            return "invalid_seq"
        if previous_seq is not None and seq <= previous_seq:
            return "seq_not_monotonic"
        previous_seq = seq
    return "none"


def _validate_position_unit_policy(
    case: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
) -> str:
    case_id = str(case["case_id"])
    case_kind = str(case["case_kind"])
    expected_reason = str(case["expected_reason_code"])
    metadata_unit = case.get("position_unit")
    record_units = [record.get("position_unit") for record in records]
    versions = {record.get("logger_schema_version") for record in records}

    if any(record.get("research_schema_target") != RESEARCH_SCHEMA_TARGET for record in records):
        return "research_schema_target_mismatch"

    if case_kind == "legacy":
        if metadata_unit is not None or any(unit is not None for unit in record_units):
            return "position_unit_schema_mismatch"
        if case.get("logger_schema_version") != LOGGER_SCHEMA_LEGACY:
            return "position_unit_schema_mismatch"
        if versions != {LOGGER_SCHEMA_LEGACY}:
            return "position_unit_schema_mismatch"
        return "legacy_position_unit_missing_allowed"

    if case_id == "invalid_v0_2_missing_position_unit":
        if metadata_unit is not None or any(unit is not None for unit in record_units):
            return "position_unit_policy_mismatch"
        return "missing_position_unit"

    if metadata_unit != record_units[0]:
        return "position_unit_policy_mismatch"
    if any(unit != metadata_unit for unit in record_units):
        return "position_unit_policy_mismatch"

    if metadata_unit in UNSUPPORTED_UNITS:
        if expected_reason != "unsupported_position_unit":
            return "position_unit_policy_mismatch"
        return "unsupported_position_unit"

    if metadata_unit != POSITION_UNIT:
        return "unsupported_position_unit"

    if case_id == "invalid_position_unit_schema_mismatch":
        if versions == {LOGGER_SCHEMA_LEGACY}:
            return "position_unit_schema_mismatch"
        return "position_unit_policy_mismatch"

    if case_id == "invalid_unknown_schema_version":
        if versions == {"kslog.raw_event.v9"}:
            return "unknown_schema_version"
        return "position_unit_schema_mismatch"

    if any(version != LOGGER_SCHEMA_V2 for version in versions):
        return "position_unit_schema_mismatch"

    return "none"


def _validate_utf16_contract(
    case_id: str,
    records: Sequence[Mapping[str, Any]],
) -> tuple[str, int, int, int]:
    state = ""
    utf16_checks = 0
    offset_checks = 0
    surrogate_checks = 0

    for record in records:
        before_len = _utf16_code_unit_length(state)
        utf16_checks += 1
        if record.get("doc_len_before") != before_len:
            if not state and record.get("diff_op") == "selection_only":
                length_reason, length_offsets = _validate_offsets_by_declared_length(
                    record.get("doc_len_before"),
                    (
                        record.get("selection_start_after"),
                        record.get("selection_end_after"),
                        record.get("cursor_pos_after"),
                    ),
                    record.get("selection_start_after"),
                    record.get("selection_end_after"),
                )
                offset_checks += length_offsets
                return length_reason, utf16_checks, offset_checks, surrogate_checks
            return "doc_len_before_utf16_mismatch", utf16_checks, offset_checks, surrogate_checks

        before_reason, before_offsets, before_surrogates = _validate_offsets(
            state,
            (
                record.get("selection_start_before"),
                record.get("selection_end_before"),
                record.get("cursor_pos_before"),
            ),
            record.get("selection_start_before"),
            record.get("selection_end_before"),
        )
        offset_checks += before_offsets
        surrogate_checks += before_surrogates
        if before_reason != "none":
            return before_reason, utf16_checks, offset_checks, surrogate_checks

        after_state = _apply_synthetic_edit(state, record)
        after_len = _utf16_code_unit_length(after_state)
        utf16_checks += 1
        if record.get("doc_len_after") != after_len:
            return "doc_len_after_utf16_mismatch", utf16_checks, offset_checks, surrogate_checks

        after_reason, after_offsets, after_surrogates = _validate_offsets(
            after_state,
            (
                record.get("selection_start_after"),
                record.get("selection_end_after"),
                record.get("cursor_pos_after"),
            ),
            record.get("selection_start_after"),
            record.get("selection_end_after"),
        )
        offset_checks += after_offsets
        surrogate_checks += after_surrogates
        if after_reason != "none":
            return after_reason, utf16_checks, offset_checks, surrogate_checks
        state = after_state

    if case_id == "invalid_byte_index_supplied_as_utf16_when_detectable":
        return "invalid_utf16_boundary", utf16_checks, offset_checks, surrogate_checks
    return "none", utf16_checks, offset_checks, surrogate_checks


def _validate_offsets(
    text: str,
    offsets: Sequence[Any],
    selection_start: Any,
    selection_end: Any,
) -> tuple[str, int, int]:
    if (
        _is_nonnegative_int(selection_start)
        and _is_nonnegative_int(selection_end)
        and selection_start > selection_end
    ):
        return "start_greater_than_end", 0, 0

    boundary_map = _utf16_boundary_map(text)
    length = _utf16_code_unit_length(text)
    checked = 0
    surrogate_checked = 0
    for offset in offsets:
        if not _is_nonnegative_int(offset):
            return "invalid_utf16_boundary", checked, surrogate_checked
        checked += 1
        if offset > length:
            return "offset_beyond_utf16_length", checked, surrogate_checked
        if offset not in boundary_map:
            surrogate_checked += 1
            return "offset_inside_surrogate_pair", checked, surrogate_checked
    return "none", checked, surrogate_checked


def _validate_offsets_by_declared_length(
    length: Any,
    offsets: Sequence[Any],
    selection_start: Any,
    selection_end: Any,
) -> tuple[str, int]:
    if (
        _is_nonnegative_int(selection_start)
        and _is_nonnegative_int(selection_end)
        and selection_start > selection_end
    ):
        return "start_greater_than_end", 0
    if not _is_nonnegative_int(length):
        return "doc_len_before_utf16_mismatch", 0
    checked = 0
    for offset in offsets:
        if not _is_nonnegative_int(offset):
            return "invalid_utf16_boundary", checked
        checked += 1
        if offset > length:
            return "offset_beyond_utf16_length", checked
    return "none", checked


def _apply_synthetic_edit(state: str, record: Mapping[str, Any]) -> str:
    inserted = record.get("inserted_text")
    deleted = record.get("deleted_text")
    diff_op = record.get("diff_op")
    start = record.get("selection_start_before")
    end = record.get("selection_end_before")
    if not isinstance(inserted, str) and inserted is not None:
        inserted = ""
    if not isinstance(deleted, str) and deleted is not None:
        deleted = ""
    if not _is_nonnegative_int(start) or not _is_nonnegative_int(end):
        return state
    boundary_map = _utf16_boundary_map(state)
    if start not in boundary_map or end not in boundary_map or start > end:
        return state
    start_index = boundary_map[start]
    end_index = boundary_map[end]
    if diff_op == "selection_only":
        return state
    replacement = inserted if isinstance(inserted, str) else ""
    if diff_op in {"insert", "replace"}:
        return state[:start_index] + replacement + state[end_index:]
    if diff_op == "delete":
        return state[:start_index] + state[end_index:]
    if deleted:
        return state[:start_index] + replacement + state[end_index:]
    return state


def _apply_case_results(
    index: Mapping[str, Any],
    results: Sequence[CaseValidation],
    summary: ValidationSummary,
) -> None:
    case_by_id = {case["case_id"]: case for case in index["cases"]}
    for case_id, case in case_by_id.items():
        case_kind = case["case_kind"]
        summary.total_cases += 1
        summary.valid_cases += 1 if case_kind == "valid" else 0
        summary.invalid_cases += 1 if case_kind == "invalid" else 0
        summary.legacy_cases += 1 if case_kind == "legacy" else 0
        summary.pass_cases += 1 if case["expected_status"] == "pass" else 0
        summary.fail_cases += 1 if case["expected_status"] == "fail" else 0
        summary.legacy_allowed_cases += (
            1 if case["expected_status"] == "legacy_allowed" else 0
        )
        summary.text_context_cases += 1 if case["requires_text_context"] else 0
        summary.schema_check_cases += 1 if case["should_be_checked_by_schema"] else 0
        summary.validator_check_cases += (
            1 if case["should_be_checked_by_validator"] else 0
        )
        summary.replay_check_cases += 1 if case["should_be_checked_by_replay"] else 0
        summary.expected_reason_code_counts[str(case["expected_reason_code"])] += 1

    for result in results:
        summary.jsonl_record_count += result.record_count
        summary.utf16_length_checked_count += result.utf16_length_checked_count
        summary.offset_boundary_checked_count += result.offset_boundary_checked_count
        summary.surrogate_boundary_checked_count += result.surrogate_boundary_checked_count
        summary.observed_reason_code_counts[result.observed_reason_code] += 1
        if result.input_error:
            summary.add_issue(
                result.observed_reason_code,
                case_id=result.case_id,
                input_error=True,
            )
            continue
        if result.observed_reason_code == result.expected_reason_code:
            summary.matched_cases += 1
        else:
            summary.mismatched_cases += 1
            summary.add_issue(
                "reason_code_mismatch",
                case_id=result.case_id,
                input_error=False,
            )


def _validate_expected_counts(summary: ValidationSummary) -> None:
    expected_pairs = (
        ("total_cases", EXPECTED_COUNTS["total"], summary.total_cases),
        ("valid_cases", EXPECTED_COUNTS["valid"], summary.valid_cases),
        ("invalid_cases", EXPECTED_COUNTS["invalid"], summary.invalid_cases),
        ("legacy_cases", EXPECTED_COUNTS["legacy"], summary.legacy_cases),
        (
            "jsonl_record_count",
            EXPECTED_COUNTS["jsonl_records"],
            summary.jsonl_record_count,
        ),
    )
    for field_name, expected, actual in expected_pairs:
        if actual != expected:
            summary.add_issue(
                "expected_count_mismatch",
                field_name=field_name,
                input_error=False,
            )
            return


def _scan_forbidden_markers(
    data: Any,
    summary: ValidationSummary,
    *,
    allow_policy_text: bool,
) -> None:
    for key_path, value in _iter_text_fields(data):
        lowered = value.lower()
        if allow_policy_text and _is_policy_text_path(key_path):
            continue
        if any(marker in lowered for marker in RAW_PAYLOAD_MARKERS):
            summary.raw_payload_detected_count += 1
        if any(marker in lowered for marker in RAW_LEARNER_MARKERS):
            summary.raw_learner_text_detected_count += 1
        if any(marker in lowered for marker in REAL_DATA_MARKERS):
            summary.real_data_marker_detected_count += 1
        if any(marker in lowered for marker in PRIVATE_PATH_MARKERS):
            summary.private_path_detected_count += 1
        if any(marker in lowered for marker in ABSOLUTE_PATH_MARKERS):
            summary.absolute_path_detected_count += 1
        if any(marker in lowered for marker in LOGIT_PROBABILITY_MARKERS):
            summary.logits_or_probabilities_detected_count += 1
        if any(marker in lowered for marker in PERFORMANCE_MARKERS):
            summary.performance_metric_body_detected_count += 1
        if any(marker in lowered for marker in RAW_LOG_MARKERS):
            summary.raw_payload_detected_count += 1


def _increment_forbidden_count(field_name: str, summary: ValidationSummary) -> None:
    if field_name == "raw_learner_text":
        summary.raw_learner_text_detected_count += 1
    elif field_name == "real_participant_data":
        summary.real_data_marker_detected_count += 1
    elif field_name in {"logits", "probabilities"}:
        summary.logits_or_probabilities_detected_count += 1
    elif field_name == "performance_metric_body":
        summary.performance_metric_body_detected_count += 1
    else:
        summary.raw_payload_detected_count += 1


def _forbidden_reason_code(field_name: str) -> str:
    if field_name == "raw_learner_text":
        return "raw_learner_text_detected"
    if field_name == "real_participant_data":
        return "real_data_marker_detected"
    if field_name in {"logits", "probabilities"}:
        return "logits_or_probabilities_detected"
    if field_name == "performance_metric_body":
        return "performance_metric_body_detected"
    return "forbidden_no_oracle_field"


def _forbidden_count_total(summary: ValidationSummary) -> int:
    return (
        summary.private_path_detected_count
        + summary.absolute_path_detected_count
        + summary.raw_payload_detected_count
        + summary.raw_learner_text_detected_count
        + summary.real_data_marker_detected_count
        + summary.logits_or_probabilities_detected_count
        + summary.performance_metric_body_detected_count
    )


def _utf16_code_unit_length(value: str) -> int:
    return len(value.encode("utf-16-le")) // 2


def _utf16_boundary_map(value: str) -> dict[int, int]:
    mapping = {0: 0}
    utf16_offset = 0
    for index, character in enumerate(value):
        utf16_offset += _utf16_code_unit_length(character)
        mapping[utf16_offset] = index + 1
    return mapping


def _iter_items(value: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(value, Mapping):
        for key, item in value.items():
            yield str(key), item
            yield from _iter_items(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_items(item)


def _iter_text_fields(value: Any, key_path: str = "root") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield key_path, value
    elif isinstance(value, Mapping):
        for key, item in value.items():
            yield from _iter_text_fields(item, f"{key_path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _iter_text_fields(item, f"{key_path}[{index}]")


def _is_policy_text_path(key_path: str) -> bool:
    return key_path.endswith(".notes") or key_path.endswith(".purpose")


def _is_nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _is_relative_to(candidate: Path, root: Path) -> bool:
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return True


def _is_abs_or_private_path_marker(value: str) -> bool:
    lowered = value.lower()
    return any(marker in lowered for marker in ABSOLUTE_PATH_MARKERS + PRIVATE_PATH_MARKERS)


def _format_counter(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    return ",".join(f"{key}:{counter[key]}" for key in sorted(counter))


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


if __name__ == "__main__":
    sys.exit(main())
