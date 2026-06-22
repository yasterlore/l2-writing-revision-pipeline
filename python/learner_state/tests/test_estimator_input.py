from __future__ import annotations

import json
import unittest
from pathlib import Path

from learner_state.estimator_input import (
    EstimatorInputValidationResult,
    compare_validation_result_to_expected,
    discover_estimator_input_fixture_cases,
    load_estimator_input_fixture,
    load_expected_input_validation_result,
    validate_estimator_input_fixture,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path("tests/fixtures/learner_state_estimator_input")
VALID_CASE = FIXTURE_ROOT / "valid" / "minimal_single_sequence"
EXPECTED_INVALID_REASONS = {
    "extra_label_row": "extra_label_row",
    "forbidden_feature_field": "forbidden_feature_field",
    "future_feature_leakage": "future_feature_leakage",
    "join_key_mismatch": "join_key_mismatch",
    "label_in_features": "label_in_features",
    "missing_label_row": "missing_label_row",
    "split_leakage_same_participant": "split_leakage",
    "unknown_schema_version": "unknown_schema_version",
}


class LearnerStateEstimatorInputTests(unittest.TestCase):
    def test_loads_valid_fixture_without_training_estimator(self) -> None:
        fixture = load_estimator_input_fixture(VALID_CASE)

        self.assertEqual(len(fixture.features), 3)
        self.assertEqual(len(fixture.labels), 3)
        self.assertEqual(fixture.manifest["sequence_count"], 1)
        self.assertEqual(
            fixture.expected_validation_result["validation_status"],
            "pass",
        )

    def test_valid_fixture_passes_and_matches_expected_result(self) -> None:
        result = validate_estimator_input_fixture(VALID_CASE)
        expected = load_expected_input_validation_result(VALID_CASE)

        self.assertEqual(result.validation_status, "pass")
        self.assertEqual(result.reason_codes, [])
        self.assertEqual(result.feature_row_count, 3)
        self.assertEqual(result.label_row_count, 3)
        self.assertEqual(result.sequence_count, 1)
        self.assertTrue(result.content_suppressed)
        self.assertTrue(result.no_raw_rows)
        self.assertTrue(result.synthetic_only_checked)
        self.assertTrue(result.no_oracle_checked)
        self.assertEqual([], compare_validation_result_to_expected(result, expected))
        assert_safe_validation_result(self, result)

    def test_invalid_fixtures_fail_closed_with_expected_reason(self) -> None:
        invalid_cases = sorted(
            path for path in (FIXTURE_ROOT / "invalid").iterdir() if path.is_dir()
        )
        self.assertEqual(
            sorted(EXPECTED_INVALID_REASONS),
            [path.name for path in invalid_cases],
        )

        for case_dir in invalid_cases:
            with self.subTest(case_name=case_dir.name):
                result = validate_estimator_input_fixture(case_dir)
                expected = load_expected_input_validation_result(case_dir)

                self.assertEqual(result.validation_status, "fail")
                self.assertEqual(
                    first_reason(result),
                    EXPECTED_INVALID_REASONS[case_dir.name],
                )
                self.assertEqual(
                    [],
                    compare_validation_result_to_expected(result, expected),
                    msg=f"safe_expected_result_mismatch:{case_dir.name}",
                )
                assert_safe_validation_result(self, result)

    def test_all_fixture_cases_are_discovered_deterministically(self) -> None:
        cases = discover_estimator_input_fixture_cases(FIXTURE_ROOT)

        self.assertEqual(cases, sorted(cases))
        self.assertEqual(len(cases), 9)
        self.assertIn(VALID_CASE, cases)
        self.assertEqual(
            sorted(EXPECTED_INVALID_REASONS),
            sorted(path.name for path in cases if path.parent.name == "invalid"),
        )

    def test_validation_result_is_safe_json_metadata(self) -> None:
        result = validate_estimator_input_fixture(
            FIXTURE_ROOT / "invalid" / "label_in_features"
        )
        payload = result.to_safe_dict()
        rendered = json.dumps(payload, sort_keys=True)

        self.assertEqual(payload["validation_status"], "fail")
        self.assertIn("label_in_features", payload["reason_codes"])
        json.loads(rendered)
        assert_safe_validation_text(self, rendered)

    def test_expected_result_mismatch_summary_is_safe(self) -> None:
        result = validate_estimator_input_fixture(VALID_CASE)
        expected = {
            "validation_status": "fail",
            "expected_failure_reason": "synthetic_mismatch_marker",
        }
        mismatches = compare_validation_result_to_expected(result, expected)

        self.assertTrue(mismatches)
        rendered = json.dumps(
            [mismatch.to_safe_dict() for mismatch in mismatches],
            sort_keys=True,
        )
        assert_safe_validation_text(self, rendered)


def first_reason(result: EstimatorInputValidationResult) -> str | None:
    return result.reason_codes[0] if result.reason_codes else None


def assert_safe_validation_result(
    test_case: unittest.TestCase,
    result: EstimatorInputValidationResult,
) -> None:
    assert_safe_validation_text(test_case, json.dumps(result.to_safe_dict()))


def assert_safe_validation_text(test_case: unittest.TestCase, text: str) -> None:
    forbidden_fragments = [
        "expected_action_family",
        "expected_action_type",
        "final_text",
        "observed_after_text",
        "gold_label",
        "teacher_correction",
        "human_correction",
        "raw_text",
        "learner_text",
        "future_episode_count",
        "/Users/",
        "/home/",
        "real_data",
        "private_data",
        "participant_data",
        "manual_outputs",
    ]
    assert_no_forbidden_fragments(test_case, text, forbidden_fragments)


if __name__ == "__main__":
    unittest.main()
