from __future__ import annotations

import json
import unittest
from pathlib import Path

from learner_state.frozen_policy_validation import (
    FrozenPolicyValidationResult,
    compare_frozen_policy_validation_result_to_expected,
    discover_frozen_policy_fixture_cases,
    load_expected_frozen_policy_validation_result,
    load_frozen_policy_fixture,
    validate_frozen_policy_fixture,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path("tests/fixtures/learner_state_frozen_selective_prediction_policy")
VALID_CASE = FIXTURE_ROOT / "valid" / "minimal_validation_only_policy"
EXPECTED_INVALID_REASONS = {
    "logits_dump_in_policy": "logits_dump_in_policy",
    "missing_required_field": "missing_required_field",
    "missing_schema_version": "missing_schema_version",
    "non_numeric_threshold": "invalid_threshold",
    "out_of_range_abstention_rate": "invalid_abstention_rate",
    "performance_claim_in_policy": "performance_claim_in_policy",
    "private_path_in_policy": "unsafe_path",
    "raw_rows_in_policy": "raw_rows_in_policy",
    "test_derived_temperature": "test_temperature_tuning",
    "test_derived_threshold": "test_threshold_tuning",
    "unknown_schema_version": "unknown_schema_version",
}


class FrozenPolicyValidationTests(unittest.TestCase):
    def test_loads_valid_fixture_without_calibration_or_metrics(self) -> None:
        fixture = load_frozen_policy_fixture(VALID_CASE)

        self.assertEqual(
            fixture.policy["policy_schema_version"],
            "frozen_selective_prediction_policy_schema_v0_1",
        )
        self.assertEqual(
            fixture.expected_validation_result["validation_status"],
            "pass",
        )
        self.assertTrue(fixture.policy["synthetic_only"])
        self.assertTrue(fixture.policy["test_tuning_forbidden"])

    def test_valid_fixture_passes_and_matches_expected_result(self) -> None:
        result = validate_frozen_policy_fixture(VALID_CASE)
        expected = load_expected_frozen_policy_validation_result(VALID_CASE)

        self.assertEqual(result.validation_status, "pass")
        self.assertEqual(result.reason_codes, [])
        self.assertEqual(result.policy_status, "safe")
        self.assertTrue(result.content_suppressed)
        self.assertTrue(result.no_raw_rows)
        self.assertTrue(result.synthetic_only_checked)
        self.assertTrue(result.no_oracle_checked)
        self.assertTrue(result.test_tuning_checked)
        self.assertTrue(result.forbidden_field_scan_checked)
        self.assertTrue(result.private_path_scan_checked)
        self.assertTrue(result.performance_claim_scan_checked)
        self.assertEqual(
            [],
            compare_frozen_policy_validation_result_to_expected(result, expected),
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
                result = validate_frozen_policy_fixture(case_dir)
                expected = load_expected_frozen_policy_validation_result(case_dir)

                self.assertEqual(result.validation_status, "fail")
                self.assertEqual(
                    first_reason(result),
                    EXPECTED_INVALID_REASONS[case_dir.name],
                )
                self.assertEqual(
                    [],
                    compare_frozen_policy_validation_result_to_expected(
                        result,
                        expected,
                    ),
                    msg=f"safe_expected_result_mismatch:{case_dir.name}",
                )
                assert_safe_validation_result(self, result)

    def test_all_fixture_cases_are_discovered_deterministically(self) -> None:
        cases = discover_frozen_policy_fixture_cases(FIXTURE_ROOT)

        self.assertEqual(cases, sorted(cases))
        self.assertEqual(len(cases), 12)
        self.assertIn(VALID_CASE, cases)
        self.assertEqual(
            sorted(EXPECTED_INVALID_REASONS),
            sorted(path.name for path in cases if path.parent.name == "invalid"),
        )

    def test_validation_result_is_safe_json_metadata(self) -> None:
        result = validate_frozen_policy_fixture(
            FIXTURE_ROOT / "invalid" / "logits_dump_in_policy"
        )
        payload = result.to_safe_dict()
        rendered = json.dumps(payload, sort_keys=True)

        self.assertEqual(payload["validation_status"], "fail")
        self.assertIn("logits_dump_in_policy", payload["reason_codes"])
        json.loads(rendered)
        assert_safe_validation_text(self, rendered)

    def test_expected_result_mismatch_summary_is_safe(self) -> None:
        result = validate_frozen_policy_fixture(VALID_CASE)
        expected = {
            "validation_status": "fail",
            "expected_failure_reason": "synthetic_mismatch_marker",
        }
        mismatches = compare_frozen_policy_validation_result_to_expected(
            result,
            expected,
        )

        self.assertTrue(mismatches)
        rendered = json.dumps(
            [mismatch.to_safe_dict() for mismatch in mismatches],
            sort_keys=True,
        )
        assert_safe_validation_text(self, rendered)


def first_reason(result: FrozenPolicyValidationResult) -> str | None:
    return result.reason_codes[0] if result.reason_codes else None


def assert_safe_validation_result(
    test_case: unittest.TestCase,
    result: FrozenPolicyValidationResult,
) -> None:
    assert_safe_validation_text(test_case, json.dumps(result.to_safe_dict()))


def assert_safe_validation_text(test_case: unittest.TestCase, text: str) -> None:
    forbidden_fragments = [
        '"raw_prediction_rows":',
        '"raw_label_rows":',
        '"logits_dump":',
        '"probability_dump":',
        '"final_test_performance_claim":',
        '"f1"',
        '"accuracy"',
        '"ece"',
        '"aurcc"',
        "expected_action",
        "final_text",
        "observed_after_text",
        "gold_label",
        "teacher_correction",
        "human_correction",
        "raw_learner_text",
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
