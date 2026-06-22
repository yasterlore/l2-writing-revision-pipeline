from __future__ import annotations

import json
import unittest
from pathlib import Path

from learner_state.selective_prediction_validation import (
    SelectivePredictionValidationResult,
    compare_calibration_validation_result_to_expected,
    discover_selective_prediction_fixture_cases,
    load_expected_calibration_validation_result,
    load_selective_prediction_fixture,
    validate_selective_prediction_fixture,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path("tests/fixtures/learner_state_selective_prediction")
VALID_CASE = FIXTURE_ROOT / "valid" / "minimal_validation_test_split"
EXPECTED_INVALID_REASONS = {
    "future_label_aggregate": "future_label_leakage",
    "label_in_confidence_feature": "label_in_prediction_row",
    "missing_validation_split": "missing_validation_split",
    "raw_text_in_prediction_row": "raw_text_in_prediction_row",
    "same_participant_across_splits": "split_leakage",
    "test_temperature_tuning": "test_temperature_tuning",
    "test_threshold_tuning": "test_threshold_tuning",
}


class SelectivePredictionValidationTests(unittest.TestCase):
    def test_loads_valid_fixture_without_calibration_or_metrics(self) -> None:
        fixture = load_selective_prediction_fixture(VALID_CASE)

        self.assertEqual(len(fixture.predictions), 4)
        self.assertEqual(len(fixture.labels), 4)
        self.assertEqual(
            fixture.expected_validation_result["validation_status"],
            "pass",
        )
        self.assertTrue(fixture.calibration_policy["validation_only_tuning"])

    def test_valid_fixture_passes_and_matches_expected_result(self) -> None:
        result = validate_selective_prediction_fixture(VALID_CASE)
        expected = load_expected_calibration_validation_result(VALID_CASE)

        self.assertEqual(result.validation_status, "pass")
        self.assertEqual(result.reason_codes, [])
        self.assertEqual(result.prediction_row_count, 4)
        self.assertEqual(result.label_row_count, 4)
        self.assertEqual(result.policy_status, "safe")
        self.assertTrue(result.content_suppressed)
        self.assertTrue(result.no_raw_rows)
        self.assertTrue(result.synthetic_only_checked)
        self.assertTrue(result.no_oracle_checked)
        self.assertTrue(result.test_tuning_checked)
        self.assertEqual(
            [],
            compare_calibration_validation_result_to_expected(result, expected),
        )
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
                result = validate_selective_prediction_fixture(case_dir)
                expected = load_expected_calibration_validation_result(case_dir)

                self.assertEqual(result.validation_status, "fail")
                self.assertEqual(
                    first_reason(result),
                    EXPECTED_INVALID_REASONS[case_dir.name],
                )
                self.assertEqual(
                    [],
                    compare_calibration_validation_result_to_expected(
                        result,
                        expected,
                    ),
                    msg=f"safe_expected_result_mismatch:{case_dir.name}",
                )
                assert_safe_validation_result(self, result)

    def test_all_fixture_cases_are_discovered_deterministically(self) -> None:
        cases = discover_selective_prediction_fixture_cases(FIXTURE_ROOT)

        self.assertEqual(cases, sorted(cases))
        self.assertEqual(len(cases), 8)
        self.assertIn(VALID_CASE, cases)
        self.assertEqual(
            sorted(EXPECTED_INVALID_REASONS),
            sorted(path.name for path in cases if path.parent.name == "invalid"),
        )

    def test_validation_result_is_safe_json_metadata(self) -> None:
        result = validate_selective_prediction_fixture(
            FIXTURE_ROOT / "invalid" / "label_in_confidence_feature"
        )
        payload = result.to_safe_dict()
        rendered = json.dumps(payload, sort_keys=True)

        self.assertEqual(payload["validation_status"], "fail")
        self.assertIn("label_in_prediction_row", payload["reason_codes"])
        json.loads(rendered)
        assert_safe_validation_text(self, rendered)

    def test_expected_result_mismatch_summary_is_safe(self) -> None:
        result = validate_selective_prediction_fixture(VALID_CASE)
        expected = {
            "validation_status": "fail",
            "expected_failure_reason": "synthetic_mismatch_marker",
        }
        mismatches = compare_calibration_validation_result_to_expected(result, expected)

        self.assertTrue(mismatches)
        rendered = json.dumps(
            [mismatch.to_safe_dict() for mismatch in mismatches],
            sort_keys=True,
        )
        assert_safe_validation_text(self, rendered)


def first_reason(result: SelectivePredictionValidationResult) -> str | None:
    return result.reason_codes[0] if result.reason_codes else None


def assert_safe_validation_result(
    test_case: unittest.TestCase,
    result: SelectivePredictionValidationResult,
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
        '"raw_text":',
        '"raw_learner_text":',
        '"learner_text":',
        "future_label_family_counts",
        "probabilities",
        "logits",
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
