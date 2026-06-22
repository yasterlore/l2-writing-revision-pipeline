"""Safe synthetic selective prediction fixture validation.

This module validates calibration / selective prediction fixtures before any
future calibration, selective prediction, or estimator implementation consumes
them. It returns only safe metadata summaries; it does not fit calibration
parameters, tune thresholds, compute metrics, or train a model.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PREDICTIONS_FILE = "predictions.jsonl"
LABELS_FILE = "labels.jsonl"
SPLIT_METADATA_FILE = "split_metadata.json"
CALIBRATION_POLICY_FILE = "calibration_policy.json"
EXPECTED_CALIBRATION_VALIDATION_RESULT_FILE = (
    "expected_calibration_validation_result.json"
)

VALIDATION_SCHEMA_VERSION = "learner_state_selective_prediction_validation_v0.1"
PREDICTION_SCHEMA_VERSION = "learner_state_selective_prediction_v0.1"
LABEL_SCHEMA_VERSION = "learner_state_selective_label_v0.1"
SPLIT_METADATA_SCHEMA_VERSION = "learner_state_selective_split_metadata_v0.1"
CALIBRATION_POLICY_SCHEMA_VERSION = "learner_state_calibration_policy_v0.1"

REQUIRED_FILES = (
    PREDICTIONS_FILE,
    LABELS_FILE,
    SPLIT_METADATA_FILE,
    CALIBRATION_POLICY_FILE,
    EXPECTED_CALIBRATION_VALIDATION_RESULT_FILE,
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
LABEL_IN_PREDICTION_KEYS = frozenset(
    {
        "expected_action",
        "expected_action_family",
        "expected_action_type",
        "gold_label",
        "label_aggregate",
        "label_aggregates",
        "label_family_counts",
        "expected_action_aggregate",
        "expected_action_family_aggregate",
    }
)
FUTURE_LABEL_LEAKAGE_KEYS = frozenset(
    {
        "future_label_aggregate",
        "future_label_aggregates",
        "future_label_family_counts",
        "future_action_summary",
        "future_action_family",
        "future_episode_count",
        "future_episode",
        "next_label_family",
        "next_action_family",
        "next_expected_action",
    }
)
RAW_TEXT_KEYS = frozenset(
    {
        "raw_text",
        "raw_learner_text",
        "learner_text",
        "final_text",
        "observed_after_text",
        "teacher_correction",
        "human_correction",
        "correction_text",
    }
)


@dataclass(frozen=True)
class SelectivePredictionFixture:
    predictions: list[dict[str, Any]]
    labels: list[dict[str, Any]]
    split_metadata: dict[str, Any]
    calibration_policy: dict[str, Any]
    expected_validation_result: dict[str, Any]


@dataclass(frozen=True)
class ExpectedCalibrationValidationResult:
    values: dict[str, Any]

    def to_safe_dict(self) -> dict[str, Any]:
        return dict(self.values)


@dataclass(frozen=True)
class SelectivePredictionValidationMismatch:
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
class SelectivePredictionValidationResult:
    validation_status: str
    reason_codes: list[str] = field(default_factory=list)
    failure_categories: list[str] = field(default_factory=list)
    failed_checks: list[dict[str, str]] = field(default_factory=list)
    checked_files_count: int = 0
    prediction_row_count: int = 0
    label_row_count: int = 0
    split_counts: dict[str, dict[str, int]] = field(default_factory=dict)
    policy_status: str = "safe"
    content_suppressed: bool = True
    no_raw_rows: bool = True
    synthetic_only_checked: bool = True
    no_oracle_checked: bool = True
    test_tuning_checked: bool = True
    validation_schema_version: str = VALIDATION_SCHEMA_VERSION

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "validation_schema_version": self.validation_schema_version,
            "validation_status": self.validation_status,
            "reason_codes": list(self.reason_codes),
            "failure_categories": list(self.failure_categories),
            "failed_checks": [dict(check) for check in self.failed_checks],
            "checked_files_count": self.checked_files_count,
            "prediction_row_count": self.prediction_row_count,
            "label_row_count": self.label_row_count,
            "split_counts": self.split_counts,
            "policy_status": self.policy_status,
            "content_suppressed": self.content_suppressed,
            "no_raw_rows": self.no_raw_rows,
            "synthetic_only_checked": self.synthetic_only_checked,
            "no_oracle_checked": self.no_oracle_checked,
            "test_tuning_checked": self.test_tuning_checked,
        }


class SelectivePredictionValidationFailure(Exception):
    """Safe validation failure without raw row, split, or policy bodies."""

    def __init__(
        self,
        reason_code: str,
        failure_category: str,
        *,
        stage: str = "calibration_fixture_validation",
        check_name: str | None = None,
        file_role: str | None = None,
    ) -> None:
        self.reason_code = reason_code
        self.failure_category = failure_category
        self.stage = stage
        self.check_name = check_name or failure_category
        self.file_role = file_role or "input"
        super().__init__(
            "selective_prediction_validation_failed:"
            f"stage={stage};category={failure_category};reason={reason_code}"
        )


def load_selective_prediction_fixture(
    case_dir: str | Path,
) -> SelectivePredictionFixture:
    """Load a synthetic selective prediction fixture or raise a safe failure."""

    path = Path(case_dir)
    _assert_path_safe(path)
    for file_name in REQUIRED_FILES:
        if not (path / file_name).exists():
            _fail("missing_input_file", "input_file_presence", file_role=file_name)

    predictions = _load_jsonl(path / PREDICTIONS_FILE, PREDICTIONS_FILE)
    labels = _load_jsonl(path / LABELS_FILE, LABELS_FILE)
    split_metadata = _load_json(path / SPLIT_METADATA_FILE, SPLIT_METADATA_FILE)
    calibration_policy = _load_json(
        path / CALIBRATION_POLICY_FILE,
        CALIBRATION_POLICY_FILE,
    )
    expected = _load_json(
        path / EXPECTED_CALIBRATION_VALIDATION_RESULT_FILE,
        EXPECTED_CALIBRATION_VALIDATION_RESULT_FILE,
    )
    return SelectivePredictionFixture(
        predictions=predictions,
        labels=labels,
        split_metadata=split_metadata,
        calibration_policy=calibration_policy,
        expected_validation_result=expected,
    )


def validate_selective_prediction_fixture(
    case_dir: str | Path,
) -> SelectivePredictionValidationResult:
    """Validate a synthetic calibration fixture and return safe metadata."""

    try:
        fixture = load_selective_prediction_fixture(case_dir)
        _validate_loaded_fixture(fixture)
    except SelectivePredictionValidationFailure as exc:
        return _failure_result(exc, case_dir)

    return _success_result(fixture)


def load_expected_calibration_validation_result(
    case_dir: str | Path,
) -> ExpectedCalibrationValidationResult:
    data = _load_json(
        Path(case_dir) / EXPECTED_CALIBRATION_VALIDATION_RESULT_FILE,
        EXPECTED_CALIBRATION_VALIDATION_RESULT_FILE,
    )
    return ExpectedCalibrationValidationResult(values=data)


def compare_calibration_validation_result_to_expected(
    result: SelectivePredictionValidationResult,
    expected: ExpectedCalibrationValidationResult | dict[str, Any],
) -> list[SelectivePredictionValidationMismatch]:
    expected_values = (
        expected.to_safe_dict()
        if isinstance(expected, ExpectedCalibrationValidationResult)
        else dict(expected)
    )
    actual_failure_reason = result.reason_codes[0] if result.reason_codes else None
    actual_failure_category = (
        result.failure_categories[0] if result.failure_categories else None
    )
    actual_stage = (
        result.failed_checks[0].get("stage")
        if result.failed_checks
        else "calibration_fixture_validation"
    )
    comparisons = {
        "validation_status": result.validation_status,
        "expected_failure_reason": actual_failure_reason,
        "expected_failure_category": actual_failure_category,
        "expected_stage": actual_stage,
        "expected_prediction_row_count": result.prediction_row_count,
        "expected_label_row_count": result.label_row_count,
        "expected_split_counts": result.split_counts,
        "expected_policy_status": result.policy_status,
        "content_suppressed": result.content_suppressed,
        "no_raw_rows": result.no_raw_rows,
        "synthetic_only": result.synthetic_only_checked,
    }

    mismatches: list[SelectivePredictionValidationMismatch] = []
    for key, actual_value in comparisons.items():
        if key in expected_values and expected_values[key] != actual_value:
            mismatches.append(
                SelectivePredictionValidationMismatch(
                    field_name=key,
                    expected_value=expected_values[key],
                    actual_value=actual_value,
                )
            )
    return mismatches


def discover_selective_prediction_fixture_cases(root: str | Path) -> list[Path]:
    root_path = Path(root)
    return sorted(
        path.parent
        for path in root_path.rglob(EXPECTED_CALIBRATION_VALIDATION_RESULT_FILE)
        if path.is_file()
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate synthetic selective prediction calibration fixtures with "
            "safe count/reason-code output."
        )
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--fixture-case",
        help="Synthetic selective prediction fixture case directory.",
    )
    mode.add_argument(
        "--fixture-root",
        help="Synthetic selective prediction fixture root directory.",
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
    result = validate_selective_prediction_fixture(case_dir)
    expected_path = case_dir / EXPECTED_CALIBRATION_VALIDATION_RESULT_FILE
    if expected_path.exists():
        try:
            expected = load_expected_calibration_validation_result(case_dir)
        except SelectivePredictionValidationFailure as exc:
            return _input_error_summary("fixture_case", exc), 2
        mismatches = compare_calibration_validation_result_to_expected(
            result,
            expected,
        )
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
    except SelectivePredictionValidationFailure as exc:
        return _input_error_summary("fixture_root", exc), 2
    if not root_dir.exists() or not root_dir.is_dir():
        return _input_error_summary(
            "fixture_root",
            SelectivePredictionValidationFailure(
                "missing_input_file",
                "input_file_presence",
                file_role="fixture_root",
            ),
        ), 2

    cases = discover_selective_prediction_fixture_cases(root_dir)
    if not cases:
        return _input_error_summary(
            "fixture_root",
            SelectivePredictionValidationFailure(
                "missing_input_file",
                "fixture_discovery",
                file_role=EXPECTED_CALIBRATION_VALIDATION_RESULT_FILE,
            ),
        ), 2

    matched_cases = 0
    mismatched_cases = 0
    input_error_cases = 0
    reason_code_counts: dict[str, int] = {}
    case_summaries: list[dict[str, Any]] = []

    for case_dir in cases:
        result = validate_selective_prediction_fixture(case_dir)
        for reason_code in result.reason_codes:
            reason_code_counts[reason_code] = reason_code_counts.get(reason_code, 0) + 1
        try:
            expected = load_expected_calibration_validation_result(case_dir)
        except SelectivePredictionValidationFailure as exc:
            input_error_cases += 1
            case_summaries.append(_safe_case_error(case_dir, exc))
            continue

        mismatches = compare_calibration_validation_result_to_expected(
            result,
            expected,
        )
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
        "test_tuning_checked": True,
    }
    if input_error_cases:
        return summary, 2
    if mismatched_cases:
        return summary, 3
    return summary, 0


def _single_case_summary(
    case_dir: Path,
    result: SelectivePredictionValidationResult,
    mismatches: list[SelectivePredictionValidationMismatch],
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
    result: SelectivePredictionValidationResult,
    mismatches: list[SelectivePredictionValidationMismatch],
) -> dict[str, Any]:
    return {
        "case": _safe_case_label(case_dir),
        "validation_status": result.validation_status,
        "reason_codes": list(result.reason_codes),
        "prediction_row_count": result.prediction_row_count,
        "label_row_count": result.label_row_count,
        "policy_status": result.policy_status,
        "expected_result_matched": not mismatches,
        "mismatch_fields": [mismatch.field_name for mismatch in mismatches],
    }


def _safe_case_error(
    case_dir: Path,
    exc: SelectivePredictionValidationFailure,
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
    exc: SelectivePredictionValidationFailure,
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
        "test_tuning_checked": True,
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
        "prediction_row_count",
        "label_row_count",
        "split_counts",
        "policy_status",
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
        "test_tuning_checked",
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


def _is_usage_like_result(result: SelectivePredictionValidationResult) -> bool:
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


def _validate_loaded_fixture(fixture: SelectivePredictionFixture) -> None:
    if not fixture.predictions:
        _fail("empty_input", "input_cardinality", file_role=PREDICTIONS_FILE)
    if not fixture.labels:
        _fail("empty_input", "input_cardinality", file_role=LABELS_FILE)

    _validate_schema_versions(fixture)
    _validate_split_metadata(fixture)
    _validate_calibration_policy(fixture.calibration_policy)
    _validate_prediction_fields(fixture.predictions)
    _validate_join_completeness(fixture.predictions, fixture.labels)
    _validate_split_leakage(fixture.predictions)
    _validate_validation_split_presence(fixture.predictions)


def _validate_schema_versions(fixture: SelectivePredictionFixture) -> None:
    if (
        fixture.split_metadata.get("split_metadata_schema_version")
        != SPLIT_METADATA_SCHEMA_VERSION
    ):
        _fail(
            "unknown_schema_version",
            "schema_version",
            file_role=SPLIT_METADATA_FILE,
        )
    if (
        fixture.calibration_policy.get("policy_schema_version")
        != CALIBRATION_POLICY_SCHEMA_VERSION
    ):
        _fail(
            "unknown_schema_version",
            "schema_version",
            file_role=CALIBRATION_POLICY_FILE,
        )
    for row in fixture.predictions:
        if row.get("prediction_schema_version") != PREDICTION_SCHEMA_VERSION:
            _fail(
                "unknown_schema_version",
                "schema_version",
                file_role=PREDICTIONS_FILE,
            )
    for row in fixture.labels:
        if row.get("label_schema_version") != LABEL_SCHEMA_VERSION:
            _fail("unknown_schema_version", "schema_version", file_role=LABELS_FILE)


def _validate_split_metadata(fixture: SelectivePredictionFixture) -> None:
    split_metadata = fixture.split_metadata
    for key in ("synthetic_only", "content_suppressed"):
        if split_metadata.get(key) is not True:
            _fail("policy_count_mismatch", "split_metadata", file_role=SPLIT_METADATA_FILE)
    if split_metadata.get("row_bodies_included") is not False:
        _fail("policy_count_mismatch", "split_metadata", file_role=SPLIT_METADATA_FILE)
    if split_metadata.get("label_dependent_split") is not False:
        _fail("split_leakage", "split", file_role=SPLIT_METADATA_FILE)

    actual_split_counts = _split_counts(fixture.predictions, fixture.labels)
    if "splits" in split_metadata and split_metadata.get("splits") != actual_split_counts:
        _fail(
            "policy_count_mismatch",
            "split_metadata",
            file_role=SPLIT_METADATA_FILE,
        )


def _validate_calibration_policy(policy: dict[str, Any]) -> None:
    if policy.get("synthetic_only") is not True:
        _fail("policy_count_mismatch", "policy", file_role=CALIBRATION_POLICY_FILE)
    if policy.get("raw_output_included") is not False:
        _fail("policy_count_mismatch", "policy", file_role=CALIBRATION_POLICY_FILE)
    if policy.get("metric_results_included") is not False:
        _fail("policy_count_mismatch", "policy", file_role=CALIBRATION_POLICY_FILE)
    if policy.get("test_tuning_forbidden") is not True:
        _fail(
            "test_threshold_tuning",
            "policy",
            file_role=CALIBRATION_POLICY_FILE,
        )
    if policy.get("frozen_policy_required") is False:
        _fail("policy_count_mismatch", "policy", file_role=CALIBRATION_POLICY_FILE)

    temperature_values = [
        policy.get("temperature_tuning_split"),
        policy.get("selected_temperature_source"),
        policy.get("temperature_selection_source"),
    ]
    threshold_values = [
        policy.get("threshold_tuning_split"),
        policy.get("selected_threshold_source"),
        policy.get("threshold_selection_source"),
    ]
    if _mentions_test(temperature_values):
        _fail(
            "test_temperature_tuning",
            "policy",
            file_role=CALIBRATION_POLICY_FILE,
        )
    if _mentions_test(threshold_values):
        _fail(
            "test_threshold_tuning",
            "policy",
            file_role=CALIBRATION_POLICY_FILE,
        )
    if policy.get("validation_only_tuning") is not True:
        _fail(
            "test_threshold_tuning",
            "policy",
            file_role=CALIBRATION_POLICY_FILE,
        )

    allowed_abstention_rate = policy.get("allowed_abstention_rate")
    if allowed_abstention_rate is not None and not (
        isinstance(allowed_abstention_rate, (int, float))
        and not isinstance(allowed_abstention_rate, bool)
        and 0.0 <= allowed_abstention_rate <= 1.0
    ):
        _fail("policy_count_mismatch", "policy", file_role=CALIBRATION_POLICY_FILE)


def _validate_prediction_fields(predictions: list[dict[str, Any]]) -> None:
    for row in predictions:
        keys = _nested_keys(row)
        if keys & FUTURE_LABEL_LEAKAGE_KEYS:
            _fail("future_label_leakage", "no_oracle", file_role=PREDICTIONS_FILE)
        if keys & LABEL_IN_PREDICTION_KEYS:
            _fail("label_in_prediction_row", "no_oracle", file_role=PREDICTIONS_FILE)
        if keys & RAW_TEXT_KEYS:
            _fail(
                "raw_text_in_prediction_row",
                "content_safety",
                file_role=PREDICTIONS_FILE,
            )
        if "confidence" not in row:
            _fail("missing_confidence", "prediction_confidence", file_role=PREDICTIONS_FILE)
        confidence = row.get("confidence")
        if not (
            isinstance(confidence, (int, float))
            and not isinstance(confidence, bool)
            and 0.0 <= confidence <= 1.0
        ):
            _fail(
                "invalid_confidence_value",
                "prediction_confidence",
                file_role=PREDICTIONS_FILE,
            )


def _validate_join_completeness(
    predictions: list[dict[str, Any]],
    labels: list[dict[str, Any]],
) -> None:
    prediction_keys = [_join_key(row) for row in predictions]
    label_keys = [_join_key(row) for row in labels]
    if len(set(prediction_keys)) != len(prediction_keys):
        _fail("join_key_mismatch", "join_completeness", file_role=PREDICTIONS_FILE)
    if len(set(label_keys)) != len(label_keys):
        _fail("join_key_mismatch", "join_completeness", file_role=LABELS_FILE)

    prediction_key_set = set(prediction_keys)
    label_key_set = set(label_keys)
    missing_labels = prediction_key_set - label_key_set
    extra_labels = label_key_set - prediction_key_set
    if missing_labels and extra_labels:
        _fail("join_key_mismatch", "join_completeness", file_role="join_keys")
    if missing_labels:
        _fail("missing_label_row", "join_completeness", file_role=LABELS_FILE)
    if extra_labels:
        _fail("extra_label_row", "join_completeness", file_role=LABELS_FILE)


def _validate_split_leakage(predictions: list[dict[str, Any]]) -> None:
    splits_by_participant: dict[str, set[str]] = {}
    for row in predictions:
        participant_id = _safe_str(row.get("synthetic_participant_id"))
        split_id = _normalize_split(_safe_str(row.get("split") or "train"))
        splits_by_participant.setdefault(participant_id, set()).add(split_id)
    for split_ids in splits_by_participant.values():
        if len(split_ids & {"train", "validation", "test"}) > 1:
            _fail("split_leakage", "split", file_role="split")


def _validate_validation_split_presence(predictions: list[dict[str, Any]]) -> None:
    split_ids = {_normalize_split(_safe_str(row.get("split") or "train")) for row in predictions}
    if "validation" not in split_ids:
        _fail("missing_validation_split", "split", file_role="split")


def _failure_result(
    exc: SelectivePredictionValidationFailure,
    case_dir: str | Path,
) -> SelectivePredictionValidationResult:
    prediction_count, label_count, split_counts, checked_files = _safe_counts_for_failure(
        Path(case_dir)
    )
    return SelectivePredictionValidationResult(
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
        prediction_row_count=prediction_count,
        label_row_count=label_count,
        split_counts=split_counts,
        policy_status=f"unsafe_{exc.reason_code}",
    )


def _success_result(
    fixture: SelectivePredictionFixture,
) -> SelectivePredictionValidationResult:
    return SelectivePredictionValidationResult(
        validation_status="pass",
        checked_files_count=len(REQUIRED_FILES),
        prediction_row_count=len(fixture.predictions),
        label_row_count=len(fixture.labels),
        split_counts=_split_counts(fixture.predictions, fixture.labels),
        policy_status="safe",
    )


def _safe_counts_for_failure(
    case_dir: Path,
) -> tuple[int, int, dict[str, dict[str, int]], int]:
    if set(case_dir.parts) & UNSAFE_PATH_PARTS:
        return 0, 0, {}, 0
    checked_files = sum(1 for file_name in REQUIRED_FILES if (case_dir / file_name).exists())
    try:
        predictions = _load_jsonl(case_dir / PREDICTIONS_FILE, PREDICTIONS_FILE)
        labels = _load_jsonl(case_dir / LABELS_FILE, LABELS_FILE)
    except SelectivePredictionValidationFailure:
        return 0, 0, {}, checked_files
    return (
        len(predictions),
        len(labels),
        _split_counts(predictions, labels),
        checked_files,
    )


def _split_counts(
    predictions: list[dict[str, Any]],
    labels: list[dict[str, Any]],
) -> dict[str, dict[str, int]]:
    prediction_rows_by_split: dict[str, int] = {}
    label_rows_by_split: dict[str, int] = {}
    participant_by_split: dict[str, set[str]] = {}
    split_by_key: dict[tuple[Any, ...], str] = {
        _join_key(row): _normalize_split(_safe_str(row.get("split") or "train"))
        for row in predictions
    }

    for row in predictions:
        split_id = _normalize_split(_safe_str(row.get("split") or "train"))
        prediction_rows_by_split[split_id] = prediction_rows_by_split.get(split_id, 0) + 1
        participant_by_split.setdefault(split_id, set()).add(
            _safe_str(row.get("synthetic_participant_id"))
        )
    for row in labels:
        split_id = split_by_key.get(
            _join_key(row),
            _normalize_split(_safe_str(row.get("split") or "train")),
        )
        label_rows_by_split[split_id] = label_rows_by_split.get(split_id, 0) + 1

    split_ids = sorted(
        set(prediction_rows_by_split) | set(label_rows_by_split) | set(participant_by_split)
    )
    return {
        split_id: {
            "prediction_rows": prediction_rows_by_split.get(split_id, 0),
            "label_rows": label_rows_by_split.get(split_id, 0),
            "participants": len(participant_by_split.get(split_id, set())),
        }
        for split_id in split_ids
    }


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
        raise SelectivePredictionValidationFailure(
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
        raise SelectivePredictionValidationFailure(
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


def _mentions_test(values: list[Any]) -> bool:
    return any(isinstance(value, str) and "test" in value.lower() for value in values)


def _normalize_split(value: str) -> str:
    return "validation" if value == "val" else value


def _fail(
    reason_code: str,
    failure_category: str,
    *,
    file_role: str | None = None,
) -> None:
    raise SelectivePredictionValidationFailure(
        reason_code,
        failure_category,
        file_role=file_role,
    )


def _safe_str(value: Any) -> str:
    return value if isinstance(value, str) else ""


if __name__ == "__main__":
    raise SystemExit(main())
