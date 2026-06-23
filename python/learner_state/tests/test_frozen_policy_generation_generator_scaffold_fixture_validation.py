from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_generator_scaffold_fixture_validation import (
    EXPECTED_ARTIFACT_FLAG_VALUES,
    EXPECTED_INVALID_REASONS,
    POINTER_SCHEMA_VERSION,
    REQUEST_SCHEMA_VERSION,
    RESULT_SCHEMA_VERSION,
    VALID_CASE_LABELS,
    compare_generator_scaffold_fixture_to_expected,
    discover_frozen_policy_generation_generator_scaffold_fixture_cases,
    load_expected_generator_scaffold_result,
    load_generator_scaffold_fixture_case,
    scan_generator_scaffold_fixture_for_forbidden_markers,
    summarize_generator_scaffold_fixture_validation_result,
    validate_generator_scaffold_fixture_case,
    validate_generator_scaffold_fixture_root,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path(
    "tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold"
)


class FrozenPolicyGenerationGeneratorScaffoldFixtureValidationTests(
    unittest.TestCase
):
    def test_discovery_counts_are_deterministic(self) -> None:
        cases = discover_frozen_policy_generation_generator_scaffold_fixture_cases(
            FIXTURE_ROOT
        )
        labels = [f"{path.parent.name}/{path.name}" for path in cases]

        self.assertEqual(cases, sorted(cases))
        self.assertEqual(len(cases), 18)
        self.assertEqual(sum(label.startswith("valid/") for label in labels), 3)
        self.assertEqual(sum(label.startswith("invalid/") for label in labels), 15)
        self.assertEqual(set(VALID_CASE_LABELS), set(label for label in labels if label.startswith("valid/")))
        self.assertEqual(set(EXPECTED_INVALID_REASONS), set(label for label in labels if label.startswith("invalid/")))

    def test_required_files_present_and_json_parse(self) -> None:
        json_files = sorted(FIXTURE_ROOT.rglob("*.json"))

        self.assertEqual(len(json_files), 54)
        for case_dir in discover_frozen_policy_generation_generator_scaffold_fixture_cases(
            FIXTURE_ROOT
        ):
            with self.subTest(case=f"{case_dir.parent.name}/{case_dir.name}"):
                self.assertTrue((case_dir / "generation_request.json").is_file())
                self.assertTrue((case_dir / "input_fixture_pointer.json").is_file())
                self.assertTrue(
                    (case_dir / "expected_generator_scaffold_result.json").is_file()
                )
                loaded = load_generator_scaffold_fixture_case(case_dir)
                self.assertEqual(loaded.case_name, case_dir.name)
        for path in json_files:
            with self.subTest(json_path=path.as_posix()):
                with path.open(encoding="utf-8") as file:
                    self.assertIsInstance(json.load(file), dict)

    def test_schema_version_checks(self) -> None:
        for case_dir in discover_frozen_policy_generation_generator_scaffold_fixture_cases(
            FIXTURE_ROOT
        ):
            fixture = load_generator_scaffold_fixture_case(case_dir)
            with self.subTest(case=fixture.case_label):
                self.assertEqual(
                    fixture.generation_request["schema_version"],
                    REQUEST_SCHEMA_VERSION,
                )
                self.assertEqual(
                    fixture.input_fixture_pointer["schema_version"],
                    POINTER_SCHEMA_VERSION,
                )
                self.assertEqual(
                    fixture.expected_generator_scaffold_result["schema_version"],
                    RESULT_SCHEMA_VERSION,
                )

    def test_valid_cases_pass_and_match_expected(self) -> None:
        for case_dir in sorted((FIXTURE_ROOT / "valid").iterdir()):
            if not case_dir.is_dir():
                continue
            with self.subTest(case_name=case_dir.name):
                result = validate_generator_scaffold_fixture_case(case_dir)
                expected = load_expected_generator_scaffold_result(case_dir)

                self.assertEqual(result.generation_status, "pass")
                self.assertEqual(result.reason_codes, [])
                self.assertEqual(result.failed_checks, [])
                self.assertEqual(
                    [],
                    compare_generator_scaffold_fixture_to_expected(result, expected),
                )
                assert_safe_generator_scaffold_text(
                    self, json.dumps(result.to_safe_dict(), sort_keys=True)
                )

    def test_invalid_cases_fail_with_expected_reason_and_match_expected(self) -> None:
        for case_label, expected_reason in sorted(EXPECTED_INVALID_REASONS.items()):
            case_dir = FIXTURE_ROOT / case_label
            with self.subTest(case_label=case_label):
                result = validate_generator_scaffold_fixture_case(case_dir)
                expected = load_expected_generator_scaffold_result(case_dir)

                self.assertEqual(result.generation_status, "fail")
                self.assertEqual(result.reason_codes, [expected_reason])
                self.assertNotEqual(result.failed_checks, [])
                self.assertEqual(
                    [],
                    compare_generator_scaffold_fixture_to_expected(result, expected),
                )
                assert_safe_generator_scaffold_text(
                    self, json.dumps(result.to_safe_dict(), sort_keys=True)
                )

    def test_artifact_flags_required_and_fixed_values(self) -> None:
        for case_dir in discover_frozen_policy_generation_generator_scaffold_fixture_cases(
            FIXTURE_ROOT
        ):
            result = validate_generator_scaffold_fixture_case(case_dir)
            with self.subTest(case=result.case_label):
                self.assertEqual(result.artifact_flags, EXPECTED_ARTIFACT_FLAG_VALUES)

    def test_safety_flags_required_and_true_values(self) -> None:
        for case_dir in discover_frozen_policy_generation_generator_scaffold_fixture_cases(
            FIXTURE_ROOT
        ):
            result = validate_generator_scaffold_fixture_case(case_dir)
            with self.subTest(case=result.case_label):
                self.assertTrue(result.content_suppressed)
                self.assertTrue(result.no_raw_rows)
                self.assertTrue(result.no_logits_dump)
                self.assertTrue(result.no_private_paths)
                self.assertTrue(result.synthetic_only_checked)
                self.assertTrue(result.no_oracle_checked)
                self.assertTrue(result.artifact_policy_checked)
                self.assertTrue(result.body_suppression_checked)
                self.assertTrue(result.file_writing_checked)
                self.assertTrue(all(result.safety_flags.values()))

    def test_count_summary_zero_constraints(self) -> None:
        for case_dir in discover_frozen_policy_generation_generator_scaffold_fixture_cases(
            FIXTURE_ROOT
        ):
            result = validate_generator_scaffold_fixture_case(case_dir)
            with self.subTest(case=result.case_label):
                self.assertEqual(result.count_summary["body_field_count"], 0)
                self.assertEqual(result.count_summary["raw_row_count"], 0)
                self.assertEqual(result.count_summary["logits_dump_count"], 0)
                self.assertEqual(result.count_summary["private_path_count"], 0)
                self.assertEqual(result.count_summary["performance_metric_count"], 0)
                self.assertTrue(
                    all(isinstance(value, int) for value in result.count_summary.values())
                )
                self.assertTrue(all(value >= 0 for value in result.count_summary.values()))

    def test_forbidden_scan_allows_safe_marker_labels(self) -> None:
        for case_dir in discover_frozen_policy_generation_generator_scaffold_fixture_cases(
            FIXTURE_ROOT
        ):
            with self.subTest(case=f"{case_dir.parent.name}/{case_dir.name}"):
                scan = scan_generator_scaffold_fixture_for_forbidden_markers(case_dir)
                self.assertEqual(scan.reason_codes, [])
                self.assertEqual(scan.failed_checks, [])

    def test_temp_malformed_request_returns_input_error(self) -> None:
        source = FIXTURE_ROOT / "valid" / "minimal_metadata_only_generation_plan"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "malformed_request"
            shutil.copytree(source, tmp_case)
            (tmp_case / "generation_request.json").write_text("{", encoding="utf-8")

            result = validate_generator_scaffold_fixture_case(tmp_case)

        self.assertEqual(result.generation_status, "input_error")
        self.assertIn("malformed_fixture_file", result.reason_codes)
        assert_safe_generator_scaffold_text(
            self, json.dumps(result.to_safe_dict(), sort_keys=True)
        )

    def test_temp_missing_request_returns_input_error(self) -> None:
        source = FIXTURE_ROOT / "valid" / "minimal_metadata_only_generation_plan"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "missing_request"
            shutil.copytree(source, tmp_case)
            (tmp_case / "generation_request.json").unlink()

            result = validate_generator_scaffold_fixture_case(tmp_case)

        self.assertEqual(result.generation_status, "input_error")
        self.assertIn("malformed_fixture_file", result.reason_codes)

    def test_temp_unexpected_extra_file_returns_input_error(self) -> None:
        source = FIXTURE_ROOT / "valid" / "minimal_metadata_only_generation_plan"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "unexpected_extra_file"
            shutil.copytree(source, tmp_case)
            (tmp_case / "case_notes.md").write_text(
                "metadata-only marker note\n",
                encoding="utf-8",
            )

            result = validate_generator_scaffold_fixture_case(tmp_case)

        self.assertEqual(result.generation_status, "input_error")
        self.assertIn("fixture_contract_error", result.reason_codes)
        self.assertIn("unexpected_case_file", result.failed_checks)

    def test_summary_is_json_serializable_and_body_free(self) -> None:
        root_result = validate_generator_scaffold_fixture_root(FIXTURE_ROOT)
        payload = summarize_generator_scaffold_fixture_validation_result(root_result)
        rendered = json.dumps(payload, sort_keys=True)

        json.loads(rendered)
        assert_safe_generator_scaffold_text(self, rendered)

    def test_root_validation_counts_expected_matches(self) -> None:
        result = validate_generator_scaffold_fixture_root(FIXTURE_ROOT)

        self.assertEqual(result.total_cases, 18)
        self.assertEqual(result.matched_cases, 18)
        self.assertEqual(result.mismatched_cases, 0)
        self.assertEqual(result.input_error_cases, 0)
        self.assertTrue(result.content_suppressed)
        self.assertTrue(result.no_raw_rows)
        self.assertTrue(result.no_logits_dump)
        self.assertTrue(result.no_private_paths)


def assert_safe_generator_scaffold_text(
    test_case: unittest.TestCase,
    text: str,
) -> None:
    assert_no_forbidden_fragments(
        test_case,
        text,
        [
            '"generation_request":',
            '"input_fixture_pointer":',
            '"expected_generator_scaffold_result":',
            '"request_body":',
            '"pointer_body":',
            '"artifact_body":',
            '"generated_policy_body":',
            '"policy_json_body":',
            '"calibration_body":',
            '"label_body":',
            '"split_body":',
            '"raw_rows":',
            '"logits":',
            '"probabilities":',
            '"raw_learner_text":',
            '"observed_after_text":',
            '"final_text":',
            '"gold_label":',
            '"expected_action_feedback":',
            "/Users/",
            "/home/",
            "/private/",
            "C:\\",
            "real_data/",
            "participant_data/",
            "private_data/",
            "manual_outputs/",
        ],
    )


if __name__ == "__main__":
    unittest.main()
