"""Runtime compatibility tests for scaffold fixture expected results."""

from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from learner_state.frozen_policy_generation import (
    run_frozen_policy_generation_scaffold,
    summarize_frozen_policy_generation_scaffold_result,
)
from learner_state.frozen_policy_generation_scaffold_fixture_validation import (
    compare_scaffold_result_to_expected,
    discover_frozen_policy_generation_scaffold_fixture_cases,
    load_expected_scaffold_result,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_ROOT = (
    REPO_ROOT / "tests/fixtures/learner_state_frozen_policy_generation_scaffold"
)

VALID_CASES = (
    "minimal_fixed_threshold_dry_run",
    "minimal_fixed_abstention_rate_dry_run",
    "validation_nll_temperature_metadata_only_dry_run",
)

INVALID_CASES = {
    "missing_validation_split": "missing_validation_split",
    "test_temperature_tuning": "test_temperature_tuning",
    "test_threshold_tuning": "test_threshold_tuning",
    "raw_rows_carryover": "raw_rows_carryover",
    "logits_dump_carryover": "logits_dump_carryover",
    "generated_artifact_body_leakage": "generated_artifact_body_leakage",
    "private_path_output": "private_path_output",
    "scoring_feedback_violation": "scoring_feedback_violation",
}

FORBIDDEN_EXACT_KEYS = {
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
    "performance_claim",
}

FORBIDDEN_VALUE_MARKERS = (
    "/Users/",
    "/home/",
    "/var/folders/",
    "C:\\",
    "real_data",
    "participant_data",
    "private_data",
    "manual_outputs",
    "raw learner text",
    "final_text",
    "observed_after_text",
    "gold_label",
    "generated_artifact_body",
    "frozen_policy_artifact_body",
    "policy_body",
)

BOOLEAN_SUMMARY_KEYS = (
    "content_suppressed",
    "artifact_body_suppressed",
    "no_raw_rows",
    "no_logits_dump",
    "no_private_paths",
    "no_performance_claims",
    "synthetic_only_checked",
    "no_oracle_checked",
    "test_tuning_checked",
    "scoring_feedback_checked",
    "generated_artifact_written",
    "generated_artifact_body_available",
)


@dataclass(frozen=True)
class RuntimeSummaryAdapter:
    values: dict[str, Any]

    def to_safe_dict(self) -> dict[str, Any]:
        return dict(self.values)


class FrozenPolicyGenerationScaffoldRuntimeFixtureCompatibilityTests(
    unittest.TestCase
):
    def test_all_scaffold_fixtures_are_compatible_with_expected_results(
        self,
    ) -> None:
        case_dirs = discover_frozen_policy_generation_scaffold_fixture_cases(
            FIXTURE_ROOT
        )
        self.assertEqual(11, len(case_dirs))
        for case_dir in case_dirs:
            case_label = self._case_label(case_dir)
            with self.subTest(case=case_label):
                summary = self._runtime_summary_for_case(case_dir)
                expected = load_expected_scaffold_result(case_dir)
                mismatches = compare_scaffold_result_to_expected(
                    RuntimeSummaryAdapter(summary),
                    expected,
                )
                self.assertEqual(
                    [],
                    [mismatch.field_name for mismatch in mismatches],
                    msg=f"runtime fixture compatibility mismatch: {case_label}",
                )

    def test_valid_cases_return_pass(self) -> None:
        for case_name in VALID_CASES:
            with self.subTest(case_name=case_name):
                summary = self._runtime_summary_for_case(
                    FIXTURE_ROOT / "valid" / case_name
                )
                self.assertEqual("pass", summary["scaffold_status"])
                self.assertEqual([], summary["reason_codes"])
                self.assertEqual([], summary["failed_checks"])
                self.assertFalse(summary["generated_artifact_written"])
                self.assertFalse(summary["generated_artifact_body_available"])

    def test_invalid_cases_return_expected_fail_reason(self) -> None:
        for case_name, reason_code in INVALID_CASES.items():
            with self.subTest(case_name=case_name):
                summary = self._runtime_summary_for_case(
                    FIXTURE_ROOT / "invalid" / case_name
                )
                self.assertEqual("fail", summary["scaffold_status"])
                self.assertEqual([reason_code], summary["reason_codes"])

    def test_malformed_and_missing_inputs_return_input_error_without_panic(
        self,
    ) -> None:
        valid_case = FIXTURE_ROOT / "valid" / "minimal_fixed_threshold_dry_run"
        request_path = valid_case / "generation_request.json"
        pointer_path = valid_case / "input_fixture_pointer.json"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir)
            malformed_request = tmp_root / "generation_request.json"
            malformed_request.write_text("{", encoding="utf-8")
            malformed_pointer = tmp_root / "input_fixture_pointer.json"
            malformed_pointer.write_text("{", encoding="utf-8")

            checks = (
                (
                    malformed_request,
                    pointer_path,
                    "malformed_request",
                ),
                (
                    request_path,
                    malformed_pointer,
                    "malformed_pointer",
                ),
                (
                    tmp_root / "missing_generation_request.json",
                    pointer_path,
                    "missing_request",
                ),
                (
                    request_path,
                    tmp_root / "missing_input_fixture_pointer.json",
                    "missing_pointer",
                ),
            )

            for request_candidate, pointer_candidate, reason_code in checks:
                with self.subTest(reason_code=reason_code):
                    result = run_frozen_policy_generation_scaffold(
                        request_candidate,
                        pointer_candidate,
                    )
                    summary = summarize_frozen_policy_generation_scaffold_result(
                        result
                    )
                    self.assertEqual("input_error", summary["scaffold_status"])
                    self.assertEqual([reason_code], summary["reason_codes"])
                    self._assert_no_body_leakage(summary, reason_code)

    def test_no_body_leakage_in_all_runtime_summaries(self) -> None:
        for case_dir in discover_frozen_policy_generation_scaffold_fixture_cases(
            FIXTURE_ROOT
        ):
            case_label = self._case_label(case_dir)
            with self.subTest(case=case_label):
                summary = self._runtime_summary_for_case(case_dir)
                self._assert_no_body_leakage(summary, case_label)

    def test_deterministic_runtime_summary_for_same_fixture(self) -> None:
        case_dir = FIXTURE_ROOT / "invalid" / "test_threshold_tuning"
        first = self._runtime_summary_for_case(case_dir)
        second = self._runtime_summary_for_case(case_dir)
        self.assertEqual(first, second)
        self.assertEqual(
            first["reason_codes"],
            list(first["reason_codes"]),
        )
        self.assertEqual(
            first["failed_checks"],
            list(first["failed_checks"]),
        )
        self.assertEqual(
            json.dumps(first, sort_keys=True),
            json.dumps(second, sort_keys=True),
        )
        self.assertEqual(list(first.keys()), list(second.keys()))

    def test_safety_flags_are_explicit_booleans(self) -> None:
        for case_dir in discover_frozen_policy_generation_scaffold_fixture_cases(
            FIXTURE_ROOT
        ):
            case_label = self._case_label(case_dir)
            summary = self._runtime_summary_for_case(case_dir)
            for key in BOOLEAN_SUMMARY_KEYS:
                with self.subTest(case=case_label, key=key):
                    self.assertIsInstance(summary[key], bool)
            self.assertFalse(summary["generated_artifact_written"])
            self.assertFalse(summary["generated_artifact_body_available"])
            self.assertTrue(summary["artifact_body_suppressed"])

    def _runtime_summary_for_case(self, case_dir: Path) -> dict[str, Any]:
        result = run_frozen_policy_generation_scaffold(
            case_dir / "generation_request.json",
            case_dir / "input_fixture_pointer.json",
        )
        return summarize_frozen_policy_generation_scaffold_result(result)

    def _assert_no_body_leakage(
        self,
        summary: dict[str, Any],
        case_label: str,
    ) -> None:
        self.assertTrue(
            FORBIDDEN_EXACT_KEYS.isdisjoint(summary.keys()),
            msg=f"forbidden summary key for {case_label}",
        )
        for value in self._iter_string_values(summary):
            if self._is_safe_marker_value(value):
                continue
            for marker in FORBIDDEN_VALUE_MARKERS:
                with self.subTest(case=case_label, marker=marker):
                    self.assertNotIn(marker, value)

    def _iter_string_values(self, value: Any) -> list[str]:
        if isinstance(value, str):
            return [value]
        if isinstance(value, dict):
            values: list[str] = []
            for nested_value in value.values():
                values.extend(self._iter_string_values(nested_value))
            return values
        if isinstance(value, (list, tuple)):
            values = []
            for nested_value in value:
                values.extend(self._iter_string_values(nested_value))
            return values
        return []

    def _is_safe_marker_value(self, value: str) -> bool:
        if value in INVALID_CASES or value in INVALID_CASES.values():
            return True
        return (
            value.startswith("valid/")
            or value.startswith("invalid/")
            or value.startswith("synthetic_scaffold_")
            or value.startswith("learner_state_frozen_policy_generation/")
        )

    def _case_label(self, case_dir: Path) -> str:
        return f"{case_dir.parent.name}/{case_dir.name}"


if __name__ == "__main__":
    unittest.main()
