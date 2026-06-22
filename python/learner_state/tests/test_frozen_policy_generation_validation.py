from __future__ import annotations

import json
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_validation import (
    FrozenPolicyGenerationValidationResult,
    compare_frozen_policy_generation_result_to_expected,
    discover_frozen_policy_generation_fixture_cases,
    load_expected_generation_result,
    load_frozen_policy_generation_fixture,
    validate_frozen_policy_generation_fixture,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path("tests/fixtures/learner_state_frozen_policy_generation")
VALID_CASES = {
    "identity_temperature_fixed_abstention_rate",
    "identity_temperature_fixed_threshold",
    "validation_nll_temperature_metadata_only",
}
EXPECTED_INVALID_REASONS = {
    "frozen_policy_validator_failure": "frozen_policy_validator_failure",
    "logits_dump_carryover": "logits_dump_in_generated_policy",
    "missing_validation_split": "missing_validation_split",
    "performance_claim_generation": "performance_claim_in_generated_policy",
    "private_path_output": "unsafe_path",
    "raw_rows_carryover": "raw_rows_in_generated_policy",
    "selective_prediction_validator_failure": (
        "selective_prediction_validator_failure"
    ),
    "test_derived_temperature": "test_temperature_tuning",
    "test_derived_threshold": "test_threshold_tuning",
    "unvalidated_input": "unvalidated_input",
}


class FrozenPolicyGenerationValidationTests(unittest.TestCase):
    def test_loads_valid_fixture_without_generation_or_metrics(self) -> None:
        case_dir = FIXTURE_ROOT / "valid" / "identity_temperature_fixed_threshold"

        fixture = load_frozen_policy_generation_fixture(case_dir)

        self.assertEqual(
            fixture.generation_request["generation_request_schema_version"],
            "frozen_policy_generation_request_schema_v0_1",
        )
        self.assertEqual(
            fixture.input_fixture_pointer["pointer_schema_version"],
            "frozen_policy_generation_input_pointer_schema_v0_1",
        )
        self.assertTrue(fixture.generation_request["synthetic_only"])
        self.assertTrue(fixture.generation_request["content_suppressed"])
        self.assertEqual(
            fixture.expected_generation_result["generation_status"],
            "pass",
        )

    def test_valid_fixtures_pass_and_match_expected_results(self) -> None:
        valid_cases = sorted(
            path for path in (FIXTURE_ROOT / "valid").iterdir() if path.is_dir()
        )
        self.assertEqual(VALID_CASES, {path.name for path in valid_cases})

        for case_dir in valid_cases:
            with self.subTest(case_name=case_dir.name):
                result = validate_frozen_policy_generation_fixture(case_dir)
                expected = load_expected_generation_result(case_dir)

                self.assertEqual(result.validation_status, "pass")
                self.assertEqual(result.reason_codes, [])
                self.assertEqual(result.generation_status, "pass")
                self.assertEqual(
                    result.expected_output_status,
                    "safe_metadata_expected",
                )
                self.assertEqual(
                    result.expected_frozen_policy_validation_status,
                    "pass",
                )
                self.assertEqual(
                    [],
                    compare_frozen_policy_generation_result_to_expected(
                        result,
                        expected,
                    ),
                )
                assert_safe_generation_result(self, result)

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
                result = validate_frozen_policy_generation_fixture(case_dir)
                expected = load_expected_generation_result(case_dir)

                self.assertEqual(result.validation_status, "fail")
                self.assertEqual(
                    first_reason(result),
                    EXPECTED_INVALID_REASONS[case_dir.name],
                )
                self.assertEqual(
                    [],
                    compare_frozen_policy_generation_result_to_expected(
                        result,
                        expected,
                    ),
                    msg=f"safe_expected_result_mismatch:{case_dir.name}",
                )
                assert_safe_generation_result(self, result)

    def test_all_fixture_cases_are_discovered_deterministically(self) -> None:
        cases = discover_frozen_policy_generation_fixture_cases(FIXTURE_ROOT)

        self.assertEqual(cases, sorted(cases))
        self.assertEqual(len(cases), 13)
        self.assertEqual(
            VALID_CASES,
            {path.name for path in cases if path.parent.name == "valid"},
        )
        self.assertEqual(
            sorted(EXPECTED_INVALID_REASONS),
            sorted(path.name for path in cases if path.parent.name == "invalid"),
        )

    def test_all_expected_generation_result_files_are_exercised(self) -> None:
        cases = discover_frozen_policy_generation_fixture_cases(FIXTURE_ROOT)

        self.assertEqual(
            len(cases),
            len(list(FIXTURE_ROOT.glob("*/*/expected_generation_result.json"))),
        )
        for case_dir in cases:
            with self.subTest(case_name=f"{case_dir.parent.name}/{case_dir.name}"):
                expected = load_expected_generation_result(case_dir)
                self.assertIn(
                    expected.values["generation_status"],
                    {"pass", "fail"},
                )

    def test_validation_result_is_safe_json_metadata(self) -> None:
        result = validate_frozen_policy_generation_fixture(
            FIXTURE_ROOT / "invalid" / "logits_dump_carryover"
        )
        payload = result.to_safe_dict()
        rendered = json.dumps(payload, sort_keys=True)

        self.assertEqual(payload["validation_status"], "fail")
        self.assertIn("logits_dump_in_generated_policy", payload["reason_codes"])
        json.loads(rendered)
        assert_safe_generation_text(self, rendered)

    def test_expected_result_mismatch_summary_is_safe(self) -> None:
        result = validate_frozen_policy_generation_fixture(
            FIXTURE_ROOT / "valid" / "identity_temperature_fixed_threshold"
        )
        mismatches = compare_frozen_policy_generation_result_to_expected(
            result,
            {
                "generation_status": "fail",
                "expected_failure_reason": "synthetic_mismatch_marker",
            },
        )

        self.assertTrue(mismatches)
        rendered = json.dumps(
            [mismatch.to_safe_dict() for mismatch in mismatches],
            sort_keys=True,
        )
        assert_safe_generation_text(self, rendered)

    def test_private_path_failure_output_does_not_include_private_path(self) -> None:
        result = validate_frozen_policy_generation_fixture(
            FIXTURE_ROOT / "invalid" / "private_path_output"
        )
        rendered = json.dumps(result.to_safe_dict(), sort_keys=True)

        self.assertEqual(first_reason(result), "unsafe_path")
        assert_safe_generation_text(self, rendered)


def first_reason(result: FrozenPolicyGenerationValidationResult) -> str | None:
    return result.reason_codes[0] if result.reason_codes else None


def assert_safe_generation_result(
    test_case: unittest.TestCase,
    result: FrozenPolicyGenerationValidationResult,
) -> None:
    assert_safe_generation_text(test_case, json.dumps(result.to_safe_dict()))


def assert_safe_generation_text(test_case: unittest.TestCase, text: str) -> None:
    forbidden_fragments = [
        '"generation_request":',
        '"input_fixture_pointer":',
        '"generated_frozen_policy":',
        '"generated_frozen_policy_body":',
        '"raw_prediction_rows":',
        '"raw_label_rows":',
        '"raw_rows_carryover_marker":',
        '"logits_dump":',
        '"probability_dump":',
        '"final_test_performance_claim":',
        '"claims_accuracy":',
        '"claims_f1":',
        '"claims_ece":',
        '"claims_aurcc":',
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
