"""Safe synthetic learner-state estimator input validation.

This module validates exported-shape learner-state estimator inputs before any
future estimator can consume them. It intentionally implements only loading,
validation, and safe metadata summaries; it does not train or evaluate a model.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

FEATURES_FILE = "features.jsonl"
LABELS_FILE = "labels.jsonl"
MANIFEST_FILE = "manifest.json"
EXPECTED_INPUT_VALIDATION_RESULT_FILE = "expected_input_validation_result.json"

VALIDATION_SCHEMA_VERSION = "learner_state_estimator_input_validation_v0.1"
FEATURE_SCHEMA_VERSION = "learner_state_feature_v0.1"
LABEL_SCHEMA_VERSION = "learner_state_label_v0.1"
MANIFEST_SCHEMA_VERSION = "learner_state_sequence_manifest_v0.1"

REQUIRED_FILES = (
    FEATURES_FILE,
    LABELS_FILE,
    MANIFEST_FILE,
    EXPECTED_INPUT_VALIDATION_RESULT_FILE,
)
JOIN_KEY_FIELDS = (
    "synthetic_participant_id",
    "synthetic_session_id",
    "synthetic_task_id",
    "micro_episode_id",
    "episode_order_index",
)
UNSAFE_PATH_PARTS = frozenset(
    {
        "manual_outputs",
        "private_data",
        "real_data",
        "participant_data",
    }
)
LABEL_LEAKAGE_KEYS = frozenset(
    {
        "expected_action",
        "expected_action_family",
        "expected_action_type",
    }
)
FUTURE_LEAKAGE_KEYS = frozenset(
    {
        "future_episode_count",
        "future_episode",
        "future_edit",
        "future_action_summary",
        "next_action_family",
        "next_episode_action",
    }
)
FORBIDDEN_FEATURE_KEYS = frozenset(
    {
        "final_text",
        "observed_after_text",
        "gold_label",
        "raw_text",
        "learner_text",
        "teacher_correction",
        "human_correction",
        "correction_text",
    }
)


@dataclass(frozen=True)
class EstimatorInputFixture:
    features: list[dict[str, Any]]
    labels: list[dict[str, Any]]
    manifest: dict[str, Any]
    expected_validation_result: dict[str, Any]


@dataclass(frozen=True)
class ExpectedInputValidationResult:
    values: dict[str, Any]

    def to_safe_dict(self) -> dict[str, Any]:
        return dict(self.values)


@dataclass(frozen=True)
class EstimatorInputValidationMismatch:
    field_name: str
    expected_value: Any
    actual_value: Any

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "field_name": self.field_name,
            "expected_value": self.expected_value,
            "actual_value": self.actual_value,
        }


@dataclass(frozen=True)
class EstimatorInputValidationResult:
    validation_status: str
    reason_codes: list[str] = field(default_factory=list)
    failure_categories: list[str] = field(default_factory=list)
    failed_checks: list[dict[str, str]] = field(default_factory=list)
    checked_files_count: int = 0
    feature_row_count: int = 0
    label_row_count: int = 0
    sequence_count: int = 0
    split_counts: dict[str, dict[str, int]] = field(default_factory=dict)
    content_suppressed: bool = True
    no_raw_rows: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    validation_schema_version: str = VALIDATION_SCHEMA_VERSION

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "validation_schema_version": self.validation_schema_version,
            "validation_status": self.validation_status,
            "reason_codes": list(self.reason_codes),
            "failure_categories": list(self.failure_categories),
            "failed_checks": [dict(check) for check in self.failed_checks],
            "checked_files_count": self.checked_files_count,
            "feature_row_count": self.feature_row_count,
            "label_row_count": self.label_row_count,
            "sequence_count": self.sequence_count,
            "split_counts": self.split_counts,
            "content_suppressed": self.content_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
        }


class EstimatorInputValidationFailure(Exception):
    """Safe validation failure without raw row or manifest bodies."""

    def __init__(
        self,
        reason_code: str,
        failure_category: str,
        *,
        stage: str = "input_validation",
        check_name: str | None = None,
        file_role: str | None = None,
    ) -> None:
        self.reason_code = reason_code
        self.failure_category = failure_category
        self.stage = stage
        self.check_name = check_name or failure_category
        self.file_role = file_role or "input"
        super().__init__(
            "estimator_input_validation_failed:"
            f"stage={stage};category={failure_category};reason={reason_code}"
        )


def load_estimator_input_fixture(case_dir: str | Path) -> EstimatorInputFixture:
    """Load the estimator input fixture files or raise a safe failure."""

    path = Path(case_dir)
    _assert_path_safe(path)
    for file_name in REQUIRED_FILES:
        if not (path / file_name).exists():
            _fail("missing_input_file", "input_file_presence", file_role=file_name)

    features = _load_jsonl(path / FEATURES_FILE, FEATURES_FILE)
    labels = _load_jsonl(path / LABELS_FILE, LABELS_FILE)
    manifest = _load_json(path / MANIFEST_FILE, MANIFEST_FILE)
    expected = _load_json(
        path / EXPECTED_INPUT_VALIDATION_RESULT_FILE,
        EXPECTED_INPUT_VALIDATION_RESULT_FILE,
    )
    return EstimatorInputFixture(
        features=features,
        labels=labels,
        manifest=manifest,
        expected_validation_result=expected,
    )


def validate_estimator_input_fixture(
    case_dir: str | Path,
) -> EstimatorInputValidationResult:
    """Validate a synthetic estimator input fixture and return safe metadata."""

    try:
        fixture = load_estimator_input_fixture(case_dir)
        _validate_loaded_fixture(fixture)
    except EstimatorInputValidationFailure as exc:
        return _failure_result(exc, case_dir)

    return _success_result(fixture)


def load_expected_input_validation_result(
    case_dir: str | Path,
) -> ExpectedInputValidationResult:
    data = _load_json(
        Path(case_dir) / EXPECTED_INPUT_VALIDATION_RESULT_FILE,
        EXPECTED_INPUT_VALIDATION_RESULT_FILE,
    )
    return ExpectedInputValidationResult(values=data)


def compare_validation_result_to_expected(
    result: EstimatorInputValidationResult,
    expected: ExpectedInputValidationResult | dict[str, Any],
) -> list[EstimatorInputValidationMismatch]:
    expected_values = (
        expected.to_safe_dict()
        if isinstance(expected, ExpectedInputValidationResult)
        else dict(expected)
    )
    actual_failure_reason = result.reason_codes[0] if result.reason_codes else None
    actual_failure_category = (
        result.failure_categories[0] if result.failure_categories else None
    )
    actual_stage = (
        result.failed_checks[0].get("stage")
        if result.failed_checks
        else "input_validation"
    )
    comparisons = {
        "validation_status": result.validation_status,
        "expected_failure_reason": actual_failure_reason,
        "expected_failure_category": actual_failure_category,
        "expected_stage": actual_stage,
        "expected_feature_row_count": result.feature_row_count,
        "expected_label_row_count": result.label_row_count,
        "expected_sequence_count": result.sequence_count,
        "expected_split_counts": result.split_counts,
        "content_suppressed": result.content_suppressed,
        "no_raw_rows": result.no_raw_rows,
        "synthetic_only": result.synthetic_only_checked,
    }

    mismatches: list[EstimatorInputValidationMismatch] = []
    for key, actual_value in comparisons.items():
        if key in expected_values and expected_values[key] != actual_value:
            mismatches.append(
                EstimatorInputValidationMismatch(
                    field_name=key,
                    expected_value=expected_values[key],
                    actual_value=actual_value,
                )
            )
    return mismatches


def discover_estimator_input_fixture_cases(root: str | Path) -> list[Path]:
    root_path = Path(root)
    return sorted(
        path.parent
        for path in root_path.rglob(EXPECTED_INPUT_VALIDATION_RESULT_FILE)
        if path.is_file()
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate synthetic learner-state estimator input fixtures with "
            "safe count/reason-code output."
        )
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--fixture-case",
        help="Synthetic estimator input fixture case directory.",
    )
    mode.add_argument(
        "--fixture-root",
        help="Synthetic estimator input fixture root directory.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a safe JSON summary instead of a human summary.",
    )
    args = parser.parse_args(argv)
    return _run_cli(args)


def _run_cli(args: argparse.Namespace) -> int:
    json_output = bool(args.json)
    if args.fixture_case:
        summary, exit_code = _run_cli_fixture_case(Path(args.fixture_case))
    else:
        summary, exit_code = _run_cli_fixture_root(Path(args.fixture_root))
    _emit_cli_summary(summary, json_output)
    return exit_code


def _run_cli_fixture_case(case_dir: Path) -> tuple[dict[str, Any], int]:
    result = validate_estimator_input_fixture(case_dir)
    expected_path = case_dir / EXPECTED_INPUT_VALIDATION_RESULT_FILE
    if expected_path.exists():
        try:
            expected = load_expected_input_validation_result(case_dir)
        except EstimatorInputValidationFailure as exc:
            return _input_error_summary("fixture_case", exc), 2
        mismatches = compare_validation_result_to_expected(result, expected)
        summary = _single_case_summary(case_dir, result, mismatches)
        return summary, 3 if mismatches else 0

    summary = _single_case_summary(case_dir, result, [])
    if result.validation_status == "pass":
        summary["expected_result_matched"] = False
        return summary, 0
    if _is_usage_like_result(result):
        summary["validation_status"] = "input_error"
        summary["expected_result_matched"] = False
        return summary, 2
    summary["expected_result_matched"] = False
    return summary, 1


def _run_cli_fixture_root(root_dir: Path) -> tuple[dict[str, Any], int]:
    try:
        _assert_path_safe(root_dir)
    except EstimatorInputValidationFailure as exc:
        return _input_error_summary("fixture_root", exc), 2
    if not root_dir.exists() or not root_dir.is_dir():
        return _input_error_summary(
            "fixture_root",
            EstimatorInputValidationFailure(
                "missing_input_file",
                "input_file_presence",
                file_role="fixture_root",
            ),
        ), 2

    cases = discover_estimator_input_fixture_cases(root_dir)
    if not cases:
        return _input_error_summary(
            "fixture_root",
            EstimatorInputValidationFailure(
                "missing_input_file",
                "fixture_discovery",
                file_role=EXPECTED_INPUT_VALIDATION_RESULT_FILE,
            ),
        ), 2

    matched_cases = 0
    mismatched_cases = 0
    input_error_cases = 0
    reason_code_counts: dict[str, int] = {}
    case_summaries: list[dict[str, Any]] = []

    for case_dir in cases:
        result = validate_estimator_input_fixture(case_dir)
        for reason_code in result.reason_codes:
            reason_code_counts[reason_code] = reason_code_counts.get(reason_code, 0) + 1
        try:
            expected = load_expected_input_validation_result(case_dir)
        except EstimatorInputValidationFailure as exc:
            input_error_cases += 1
            case_summaries.append(_safe_case_error(case_dir, exc))
            continue

        mismatches = compare_validation_result_to_expected(result, expected)
        if mismatches:
            mismatched_cases += 1
        else:
            matched_cases += 1
        case_summaries.append(_safe_case_summary(case_dir, result, mismatches))

    summary = {
        "mode": "fixture_root",
        "total_cases": len(cases),
        "matched_cases": matched_cases,
        "mismatched_cases": mismatched_cases,
        "input_error_cases": input_error_cases,
        "reason_code_counts": {
            key: reason_code_counts[key] for key in sorted(reason_code_counts)
        },
        "case_summaries": case_summaries,
        "content_suppressed": True,
        "no_raw_rows": True,
        "synthetic_only_checked": True,
        "no_oracle_checked": True,
    }
    if input_error_cases:
        return summary, 2
    if mismatched_cases:
        return summary, 3
    return summary, 0


def _single_case_summary(
    case_dir: Path,
    result: EstimatorInputValidationResult,
    mismatches: list[EstimatorInputValidationMismatch],
) -> dict[str, Any]:
    return {
        "mode": "fixture_case",
        "case": _safe_case_label(case_dir),
        **result.to_safe_dict(),
        "expected_result_matched": not mismatches,
        "mismatch_fields": [mismatch.field_name for mismatch in mismatches],
    }


def _safe_case_summary(
    case_dir: Path,
    result: EstimatorInputValidationResult,
    mismatches: list[EstimatorInputValidationMismatch],
) -> dict[str, Any]:
    return {
        "case": _safe_case_label(case_dir),
        "validation_status": result.validation_status,
        "reason_codes": list(result.reason_codes),
        "feature_row_count": result.feature_row_count,
        "label_row_count": result.label_row_count,
        "sequence_count": result.sequence_count,
        "expected_result_matched": not mismatches,
        "mismatch_fields": [mismatch.field_name for mismatch in mismatches],
    }


def _safe_case_error(
    case_dir: Path,
    exc: EstimatorInputValidationFailure,
) -> dict[str, Any]:
    return {
        "case": _safe_case_label(case_dir),
        "validation_status": "input_error",
        "reason_codes": [exc.reason_code],
        "failure_categories": [exc.failure_category],
        "expected_result_matched": False,
    }


def _input_error_summary(
    mode: str,
    exc: EstimatorInputValidationFailure,
) -> dict[str, Any]:
    return {
        "mode": mode,
        "validation_status": "input_error",
        "reason_codes": [exc.reason_code],
        "failure_categories": [exc.failure_category],
        "failed_checks": [
            {
                "stage": exc.stage,
                "check_name": exc.check_name,
                "file_role": exc.file_role,
                "reason_code": exc.reason_code,
                "failure_category": exc.failure_category,
            }
        ],
        "content_suppressed": True,
        "no_raw_rows": True,
        "synthetic_only_checked": True,
        "no_oracle_checked": True,
    }


def _emit_cli_summary(summary: dict[str, Any], json_output: bool) -> None:
    if json_output:
        sys.stdout.write(json.dumps(summary, sort_keys=True))
        sys.stdout.write("\n")
        return
    for key in _human_summary_keys(summary):
        sys.stdout.write(f"{key}={_format_summary_value(summary.get(key))}\n")


def _human_summary_keys(summary: dict[str, Any]) -> list[str]:
    preferred = [
        "mode",
        "case",
        "validation_status",
        "reason_codes",
        "failed_checks",
        "feature_row_count",
        "label_row_count",
        "sequence_count",
        "split_counts",
        "expected_result_matched",
        "mismatch_fields",
        "total_cases",
        "matched_cases",
        "mismatched_cases",
        "input_error_cases",
        "reason_code_counts",
        "content_suppressed",
        "no_raw_rows",
        "synthetic_only_checked",
        "no_oracle_checked",
    ]
    return [key for key in preferred if key in summary]


def _format_summary_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        if not value:
            return "none"
        if all(isinstance(item, str) for item in value):
            return ",".join(value)
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    if isinstance(value, dict):
        if not value:
            return "none"
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    if value is None:
        return "none"
    return str(value)


def _safe_case_label(case_dir: Path) -> str:
    parts = case_dir.parts
    if len(parts) >= 2 and parts[-2] in {"valid", "invalid"}:
        return f"{parts[-2]}/{parts[-1]}"
    return case_dir.name or "unknown_case"


def _is_usage_like_result(result: EstimatorInputValidationResult) -> bool:
    return any(
        reason_code
        in {
            "missing_input_file",
            "malformed_input",
            "unsafe_path",
            "empty_input",
        }
        for reason_code in result.reason_codes
    )


def _validate_loaded_fixture(fixture: EstimatorInputFixture) -> None:
    if not fixture.features:
        _fail("empty_input", "input_cardinality", file_role=FEATURES_FILE)
    if not fixture.labels:
        _fail("empty_input", "input_cardinality", file_role=LABELS_FILE)

    _validate_schema_versions(fixture)
    _validate_manifest_counts(fixture)
    _validate_feature_fields(fixture.features)
    _validate_join_completeness(fixture.features, fixture.labels)
    _validate_sequence_grouping(fixture.features)
    _validate_split_leakage(fixture.features)


def _validate_schema_versions(fixture: EstimatorInputFixture) -> None:
    if fixture.manifest.get("manifest_schema_version") != MANIFEST_SCHEMA_VERSION:
        _fail("unknown_schema_version", "schema_version", file_role=MANIFEST_FILE)
    if fixture.manifest.get("feature_schema_version") != FEATURE_SCHEMA_VERSION:
        _fail("unknown_schema_version", "schema_version", file_role=MANIFEST_FILE)
    if fixture.manifest.get("label_schema_version") != LABEL_SCHEMA_VERSION:
        _fail("unknown_schema_version", "schema_version", file_role=MANIFEST_FILE)
    for row in fixture.features:
        if row.get("feature_schema_version") != FEATURE_SCHEMA_VERSION:
            _fail("unknown_schema_version", "schema_version", file_role=FEATURES_FILE)
    for row in fixture.labels:
        if row.get("label_schema_version") != LABEL_SCHEMA_VERSION:
            _fail("unknown_schema_version", "schema_version", file_role=LABELS_FILE)


def _validate_manifest_counts(fixture: EstimatorInputFixture) -> None:
    actual_sequence_count = _sequence_count(fixture.features)
    actual_split_counts = _split_counts(fixture.features, fixture.labels)
    count_checks = {
        "feature_row_count": len(fixture.features),
        "label_row_count": len(fixture.labels),
        "sequence_count": actual_sequence_count,
        "synthetic_participant_count": len(
            {row.get("synthetic_participant_id") for row in fixture.features}
        ),
        "synthetic_session_count": len(
            {row.get("synthetic_session_id") for row in fixture.features}
        ),
        "synthetic_task_count": len(
            {row.get("synthetic_task_id") for row in fixture.features}
        ),
        "episode_count": len(fixture.features),
    }
    for key, actual in count_checks.items():
        if key in fixture.manifest and fixture.manifest.get(key) != actual:
            _fail(
                "manifest_count_mismatch",
                "manifest_consistency",
                file_role=MANIFEST_FILE,
            )
    if (
        "split_counts" in fixture.manifest
        and fixture.manifest.get("split_counts") != actual_split_counts
    ):
        _fail(
            "manifest_count_mismatch",
            "manifest_consistency",
            file_role=MANIFEST_FILE,
        )
    if fixture.manifest.get("synthetic_only") is not True:
        _fail("forbidden_feature_field", "synthetic_policy", file_role=MANIFEST_FILE)
    if fixture.manifest.get("content_suppressed") is not True:
        _fail("forbidden_feature_field", "safe_output", file_role=MANIFEST_FILE)
    if fixture.manifest.get("no_raw_rows") is not True:
        _fail("forbidden_feature_field", "safe_output", file_role=MANIFEST_FILE)


def _validate_feature_fields(features: list[dict[str, Any]]) -> None:
    for row in features:
        keys = _nested_keys(row)
        if keys & LABEL_LEAKAGE_KEYS:
            _fail(
                "label_in_features",
                "feature_label_separation",
                file_role=FEATURES_FILE,
            )
        if keys & FUTURE_LEAKAGE_KEYS:
            _fail(
                "future_feature_leakage",
                "future_leakage",
                file_role=FEATURES_FILE,
            )
        if keys & FORBIDDEN_FEATURE_KEYS:
            _fail(
                "forbidden_feature_field",
                "forbidden_field",
                file_role=FEATURES_FILE,
            )


def _validate_join_completeness(
    features: list[dict[str, Any]],
    labels: list[dict[str, Any]],
) -> None:
    feature_keys = [_join_key(row) for row in features]
    label_keys = [_join_key(row) for row in labels]
    if len(set(feature_keys)) != len(feature_keys):
        _fail("join_key_mismatch", "join_completeness", file_role=FEATURES_FILE)
    if len(set(label_keys)) != len(label_keys):
        _fail("join_key_mismatch", "join_completeness", file_role=LABELS_FILE)

    feature_key_set = set(feature_keys)
    label_key_set = set(label_keys)
    missing_labels = feature_key_set - label_key_set
    extra_labels = label_key_set - feature_key_set
    if missing_labels and extra_labels:
        _fail("join_key_mismatch", "join_completeness", file_role="join_keys")
    if missing_labels:
        _fail("missing_label_row", "join_completeness", file_role=LABELS_FILE)
    if extra_labels:
        _fail("extra_label_row", "join_completeness", file_role=LABELS_FILE)


def _validate_sequence_grouping(features: list[dict[str, Any]]) -> None:
    previous_by_sequence: dict[tuple[str, str, str], int] = {}
    seen_orders: set[tuple[str, str, str, int]] = set()
    for row in features:
        sequence_key = (
            _safe_str(row.get("synthetic_participant_id")),
            _safe_str(row.get("synthetic_session_id")),
            _safe_str(row.get("synthetic_task_id")),
        )
        order = _safe_int(row.get("episode_order_index"))
        order_key = (*sequence_key, order)
        if order_key in seen_orders:
            _fail("sequence_order_error", "sequence_grouping", file_role=FEATURES_FILE)
        seen_orders.add(order_key)
        previous = previous_by_sequence.get(sequence_key)
        if previous is not None and order <= previous:
            _fail("sequence_order_error", "sequence_grouping", file_role=FEATURES_FILE)
        previous_by_sequence[sequence_key] = order


def _validate_split_leakage(features: list[dict[str, Any]]) -> None:
    splits_by_participant: dict[str, set[str]] = {}
    for row in features:
        participant_id = _safe_str(row.get("synthetic_participant_id"))
        split_id = _safe_str(row.get("split_id") or "train")
        splits_by_participant.setdefault(participant_id, set()).add(split_id)
    for split_ids in splits_by_participant.values():
        normalized = {"validation" if split_id == "val" else split_id for split_id in split_ids}
        if len(normalized & {"train", "validation", "test"}) > 1:
            _fail("split_leakage", "split_validation", file_role="split_id")


def _failure_result(
    exc: EstimatorInputValidationFailure,
    case_dir: str | Path,
) -> EstimatorInputValidationResult:
    feature_count, label_count, sequence_count, split_counts, checked_files = (
        _safe_counts_for_failure(Path(case_dir))
    )
    return EstimatorInputValidationResult(
        validation_status="fail",
        reason_codes=[exc.reason_code],
        failure_categories=[exc.failure_category],
        failed_checks=[
            {
                "stage": exc.stage,
                "check_name": exc.check_name,
                "file_role": exc.file_role,
                "reason_code": exc.reason_code,
                "failure_category": exc.failure_category,
            }
        ],
        checked_files_count=checked_files,
        feature_row_count=feature_count,
        label_row_count=label_count,
        sequence_count=sequence_count,
        split_counts=split_counts,
    )


def _success_result(fixture: EstimatorInputFixture) -> EstimatorInputValidationResult:
    return EstimatorInputValidationResult(
        validation_status="pass",
        checked_files_count=len(REQUIRED_FILES),
        feature_row_count=len(fixture.features),
        label_row_count=len(fixture.labels),
        sequence_count=_sequence_count(fixture.features),
        split_counts=_split_counts(fixture.features, fixture.labels),
    )


def _safe_counts_for_failure(
    case_dir: Path,
) -> tuple[int, int, int, dict[str, dict[str, int]], int]:
    checked_files = sum(1 for file_name in REQUIRED_FILES if (case_dir / file_name).exists())
    try:
        features = _load_jsonl(case_dir / FEATURES_FILE, FEATURES_FILE)
        labels = _load_jsonl(case_dir / LABELS_FILE, LABELS_FILE)
    except EstimatorInputValidationFailure:
        return 0, 0, 0, {}, checked_files
    return (
        len(features),
        len(labels),
        _sequence_count(features),
        _split_counts(features, labels),
        checked_files,
    )


def _split_counts(
    features: list[dict[str, Any]],
    labels: list[dict[str, Any]],
) -> dict[str, dict[str, int]]:
    label_split_by_key: dict[str, int] = {}
    feature_split_by_key: dict[tuple[Any, ...], str] = {
        _join_key(row): _safe_str(row.get("split_id") or "train") for row in features
    }
    participant_by_split: dict[str, set[str]] = {}
    sequence_by_split: dict[str, set[tuple[str, str, str]]] = {}
    feature_rows_by_split: dict[str, int] = {}
    label_rows_by_split: dict[str, int] = {}

    for row in features:
        split_id = _safe_str(row.get("split_id") or "train")
        feature_rows_by_split[split_id] = feature_rows_by_split.get(split_id, 0) + 1
        participant_by_split.setdefault(split_id, set()).add(
            _safe_str(row.get("synthetic_participant_id"))
        )
        sequence_by_split.setdefault(split_id, set()).add(
            (
                _safe_str(row.get("synthetic_participant_id")),
                _safe_str(row.get("synthetic_session_id")),
                _safe_str(row.get("synthetic_task_id")),
            )
        )
    for row in labels:
        split_id = feature_split_by_key.get(_join_key(row), _safe_str(row.get("split_id") or "train"))
        label_rows_by_split[split_id] = label_rows_by_split.get(split_id, 0) + 1

    split_ids = sorted(
        set(feature_rows_by_split)
        | set(label_rows_by_split)
        | set(participant_by_split)
        | set(sequence_by_split)
    )
    return {
        split_id: {
            "feature_rows": feature_rows_by_split.get(split_id, 0),
            "label_rows": label_rows_by_split.get(split_id, 0),
            "participants": len(participant_by_split.get(split_id, set())),
            "sequences": len(sequence_by_split.get(split_id, set())),
        }
        for split_id in split_ids
    }


def _sequence_count(features: list[dict[str, Any]]) -> int:
    return len(
        {
            (
                row.get("synthetic_participant_id"),
                row.get("synthetic_session_id"),
                row.get("synthetic_task_id"),
            )
            for row in features
        }
    )


def _join_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(row.get(field_name) for field_name in JOIN_KEY_FIELDS)


def _nested_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(key, str):
                keys.add(key)
            keys.update(_nested_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_nested_keys(child))
    return keys


def _load_jsonl(path: Path, file_role: str) -> list[dict[str, Any]]:
    if not path.exists():
        _fail("missing_input_file", "input_file_presence", file_role=file_role)
    rows: list[dict[str, Any]] = []
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                if not isinstance(row, dict):
                    _fail("malformed_input", "jsonl_parse", file_role=file_role)
                rows.append(row)
    except json.JSONDecodeError as exc:
        raise EstimatorInputValidationFailure(
            "malformed_input",
            "jsonl_parse",
            file_role=file_role,
        ) from exc
    if not rows:
        _fail("empty_input", "input_cardinality", file_role=file_role)
    return rows


def _load_json(path: Path, file_role: str) -> dict[str, Any]:
    if not path.exists():
        _fail("missing_input_file", "input_file_presence", file_role=file_role)
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise EstimatorInputValidationFailure(
            "malformed_input",
            "json_parse",
            file_role=file_role,
        ) from exc
    if not isinstance(data, dict):
        _fail("malformed_input", "json_parse", file_role=file_role)
    return data


def _assert_path_safe(path: Path) -> None:
    if set(path.parts) & UNSAFE_PATH_PARTS:
        _fail("unsafe_path", "path_safety", file_role="input_path")


def _fail(
    reason_code: str,
    failure_category: str,
    *,
    file_role: str | None = None,
) -> None:
    raise EstimatorInputValidationFailure(
        reason_code,
        failure_category,
        file_role=file_role,
    )


def _safe_str(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _safe_int(value: Any) -> int:
    return value if isinstance(value, int) else -1


if __name__ == "__main__":
    raise SystemExit(main())
