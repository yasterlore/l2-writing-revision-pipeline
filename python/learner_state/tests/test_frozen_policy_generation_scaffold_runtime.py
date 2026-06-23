"""Tests for the minimal frozen policy generation scaffold runtime skeleton."""

from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from learner_state.frozen_policy_generation import (
    build_frozen_policy_generation_plan,
    load_frozen_policy_generation_input_pointer,
    load_frozen_policy_generation_request,
    run_frozen_policy_generation_scaffold,
    summarize_frozen_policy_generation_scaffold_result,
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

FORBIDDEN_SUMMARY_KEYS = {
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

BOOLEAN_SUMMARY_KEYS = (
    "content_suppressed",
    "artifact_body_suppressed",
    "no_raw_rows",
    "no_logits_dump",
    "no_request_body",
    "no_generated_artifact_body",
    "no_private_paths",
    "no_performance_claims",
    "synthetic_only_checked",
    "no_oracle_checked",
    "test_tuning_checked",
    "scoring_feedback_checked",
    "private_path_scan_checked",
    "performance_claim_scan_checked",
    "generated_artifact_written",
    "generated_artifact_body_available",
    "would_write_artifact",
    "metadata_only",
)


class FrozenPolicyGenerationScaffoldRuntimeTests(unittest.TestCase):
    def test_valid_fixtures_return_pass(self) -> None:
        for case_name in VALID_CASES:
            with self.subTest(case_name=case_name):
                result = self._run_valid_case(case_name)
                self.assertEqual("pass", result.scaffold_status)
                self.assertEqual((), result.reason_codes)

    def test_invalid_fixtures_return_expected_reason_code(self) -> None:
        for case_name, reason_code in INVALID_CASES.items():
            with self.subTest(case_name=case_name):
                result = self._run_invalid_case(case_name)
                self.assertEqual("fail", result.scaffold_status)
                self.assertEqual((reason_code,), result.reason_codes)

    def test_private_path_output_does_not_echo_private_path(self) -> None:
        result = self._run_invalid_case("private_path_output")
        summary_text = json.dumps(
            summarize_frozen_policy_generation_scaffold_result(result),
            sort_keys=True,
        )
        self.assertIn("private_path_output", summary_text)
        self.assertNotIn("/Users/", summary_text)
        self.assertNotIn("/home/", summary_text)
        self.assertNotIn("private_data", summary_text)

    def test_malformed_request_returns_input_error_without_panic(self) -> None:
        pointer_path = self._valid_case_dir("minimal_fixed_threshold_dry_run") / (
            "input_fixture_pointer.json"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            request_path = Path(tmp_dir) / "generation_request.json"
            request_path.write_text("{", encoding="utf-8")
            result = run_frozen_policy_generation_scaffold(request_path, pointer_path)
        self.assertEqual("input_error", result.scaffold_status)
        self.assertEqual(("malformed_request",), result.reason_codes)

    def test_malformed_pointer_returns_input_error_without_panic(self) -> None:
        request_path = self._valid_case_dir("minimal_fixed_threshold_dry_run") / (
            "generation_request.json"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            pointer_path = Path(tmp_dir) / "input_fixture_pointer.json"
            pointer_path.write_text("{", encoding="utf-8")
            result = run_frozen_policy_generation_scaffold(request_path, pointer_path)
        self.assertEqual("input_error", result.scaffold_status)
        self.assertEqual(("malformed_pointer",), result.reason_codes)

    def test_missing_request_path_returns_input_error_without_panic(self) -> None:
        pointer_path = self._valid_case_dir("minimal_fixed_threshold_dry_run") / (
            "input_fixture_pointer.json"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            request_path = Path(tmp_dir) / "missing_generation_request.json"
            result = run_frozen_policy_generation_scaffold(request_path, pointer_path)
        self.assertEqual("input_error", result.scaffold_status)
        self.assertEqual(("missing_request",), result.reason_codes)

    def test_missing_pointer_path_returns_input_error_without_panic(self) -> None:
        request_path = self._valid_case_dir("minimal_fixed_threshold_dry_run") / (
            "generation_request.json"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            pointer_path = Path(tmp_dir) / "missing_input_fixture_pointer.json"
            result = run_frozen_policy_generation_scaffold(request_path, pointer_path)
        self.assertEqual("input_error", result.scaffold_status)
        self.assertEqual(("missing_pointer",), result.reason_codes)

    def test_summary_contains_no_body_keys_and_is_json_serializable(self) -> None:
        result = self._run_valid_case("minimal_fixed_threshold_dry_run")
        summary = summarize_frozen_policy_generation_scaffold_result(result)
        self.assertTrue(FORBIDDEN_SUMMARY_KEYS.isdisjoint(summary))
        json.dumps(summary, sort_keys=True)

    def test_reason_codes_are_deterministically_ordered(self) -> None:
        case_dir = self._valid_case_dir("minimal_fixed_threshold_dry_run")
        request = load_frozen_policy_generation_request(
            case_dir / "generation_request.json"
        )
        pointer = load_frozen_policy_generation_input_pointer(
            case_dir / "input_fixture_pointer.json"
        )
        request = replace(request, no_raw_rows=False, no_logits_dump=False)
        pointer = replace(pointer, validation_split_available=False)
        plan = build_frozen_policy_generation_plan(request, pointer)
        self.assertEqual(
            (
                "missing_validation_split",
                "raw_rows_carryover",
                "logits_dump_carryover",
            ),
            plan.reason_codes,
        )

    def test_safety_flags_are_explicit_booleans(self) -> None:
        result = self._run_valid_case("minimal_fixed_threshold_dry_run")
        summary = summarize_frozen_policy_generation_scaffold_result(result)
        for key in BOOLEAN_SUMMARY_KEYS:
            with self.subTest(key=key):
                self.assertIsInstance(summary[key], bool)
        self.assertFalse(summary["generated_artifact_written"])
        self.assertFalse(summary["generated_artifact_body_available"])
        self.assertTrue(summary["artifact_body_suppressed"])

    def _run_valid_case(self, case_name: str):
        case_dir = self._valid_case_dir(case_name)
        return run_frozen_policy_generation_scaffold(
            case_dir / "generation_request.json",
            case_dir / "input_fixture_pointer.json",
        )

    def _run_invalid_case(self, case_name: str):
        case_dir = FIXTURE_ROOT / "invalid" / case_name
        return run_frozen_policy_generation_scaffold(
            case_dir / "generation_request.json",
            case_dir / "input_fixture_pointer.json",
        )

    def _valid_case_dir(self, case_name: str) -> Path:
        return FIXTURE_ROOT / "valid" / case_name


if __name__ == "__main__":
    unittest.main()
