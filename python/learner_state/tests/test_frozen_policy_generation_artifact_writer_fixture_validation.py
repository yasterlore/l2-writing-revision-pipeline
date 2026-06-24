from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_artifact_writer_fixture_validation import (
    EXPECTED_ARTIFACT_FLAG_VALUES,
    EXPECTED_INVALID_REASONS,
    EXPECTED_TOTAL_CASES,
    EXPECTED_VALID_CASES,
    POINTER_SCHEMA_VERSION,
    REQUEST_SCHEMA_VERSION,
    RESULT_SCHEMA_VERSION,
    VALID_CASE_LABELS,
    compare_artifact_writer_fixture_to_expected,
    discover_artifact_writer_fixture_cases,
    load_artifact_writer_fixture_case,
    load_expected_artifact_writer_result,
    scan_artifact_writer_fixture_for_forbidden_markers,
    summarize_artifact_writer_fixture_validation_result,
    validate_artifact_writer_fixture_case,
    validate_artifact_writer_fixture_root,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path(
    "tests/fixtures/learner_state_frozen_policy_generation_artifact_writer"
)


class FrozenPolicyGenerationArtifactWriterFixtureValidationTests(unittest.TestCase):
    def test_discovery_counts_are_deterministic(self) -> None:
        cases = discover_artifact_writer_fixture_cases(FIXTURE_ROOT)
        labels = [f"{path.parent.name}/{path.name}" for path in cases]

        self.assertEqual(cases, sorted(cases))
        self.assertEqual(len(cases), EXPECTED_TOTAL_CASES)
        self.assertEqual(sum(label.startswith("valid/") for label in labels), 3)
        self.assertEqual(sum(label.startswith("invalid/") for label in labels), 14)
        self.assertEqual(
            set(VALID_CASE_LABELS),
            {label for label in labels if label.startswith("valid/")},
        )
        self.assertEqual(
            set(EXPECTED_INVALID_REASONS),
            {label for label in labels if label.startswith("invalid/")},
        )

    def test_required_files_present_and_json_parse(self) -> None:
        json_files = sorted(FIXTURE_ROOT.rglob("*.json"))

        self.assertEqual(len(json_files), 51)
        for case_dir in discover_artifact_writer_fixture_cases(FIXTURE_ROOT):
            with self.subTest(case=f"{case_dir.parent.name}/{case_dir.name}"):
                self.assertTrue((case_dir / "artifact_writer_request.json").is_file())
                self.assertTrue((case_dir / "generator_result_pointer.json").is_file())
                self.assertTrue(
                    (case_dir / "expected_artifact_writer_result.json").is_file()
                )
                loaded = load_artifact_writer_fixture_case(case_dir)
                self.assertEqual(loaded.case_name, case_dir.name)
        for path in json_files:
            with self.subTest(json_path=path.as_posix()):
                with path.open(encoding="utf-8") as file:
                    self.assertIsInstance(json.load(file), dict)

    def test_schema_version_checks(self) -> None:
        for case_dir in discover_artifact_writer_fixture_cases(FIXTURE_ROOT):
            fixture = load_artifact_writer_fixture_case(case_dir)
            with self.subTest(case=fixture.case_label):
                if fixture.case_label == "invalid/unknown_schema_version":
                    self.assertNotEqual(
                        fixture.request_metadata["schema_version"],
                        REQUEST_SCHEMA_VERSION,
                    )
                else:
                    self.assertEqual(
                        fixture.request_metadata["schema_version"],
                        REQUEST_SCHEMA_VERSION,
                    )
                self.assertEqual(
                    fixture.generator_result_pointer_metadata["schema_version"],
                    POINTER_SCHEMA_VERSION,
                )
                self.assertEqual(
                    fixture.expected_result_metadata["result_schema_version"],
                    RESULT_SCHEMA_VERSION,
                )

    def test_root_validation_counts_expected_matches(self) -> None:
        result = validate_artifact_writer_fixture_root(FIXTURE_ROOT)

        self.assertEqual(result.total_cases, 17)
        self.assertEqual(result.valid_cases, EXPECTED_VALID_CASES)
        self.assertEqual(result.invalid_cases, 14)
        self.assertEqual(result.matched_cases, 17)
        self.assertEqual(result.mismatched_cases, 0)
        self.assertEqual(result.input_error_cases, 0)
        self.assertTrue(result.content_suppressed)
        self.assertTrue(result.no_raw_rows)
        self.assertTrue(result.no_logits_dump)
        self.assertTrue(result.no_private_paths)

    def test_valid_cases_pass_and_match_expected(self) -> None:
        for case_dir in sorted((FIXTURE_ROOT / "valid").iterdir()):
            if not case_dir.is_dir():
                continue
            with self.subTest(case_name=case_dir.name):
                result = validate_artifact_writer_fixture_case(case_dir)
                expected = load_expected_artifact_writer_result(case_dir)

                self.assertEqual(result.writer_status, "pass")
                self.assertEqual(result.reason_codes, [])
                self.assertEqual(result.failed_checks, [])
                self.assertEqual(expected["writer_status"], result.writer_status)
                self.assertEqual([], compare_artifact_writer_fixture_to_expected(case_dir))
                assert_safe_artifact_writer_text(
                    self, json.dumps(result.to_safe_dict(), sort_keys=True)
                )

    def test_invalid_cases_fail_with_expected_reason_and_match_expected(self) -> None:
        for case_label, expected_reason in sorted(EXPECTED_INVALID_REASONS.items()):
            case_dir = FIXTURE_ROOT / case_label
            with self.subTest(case_label=case_label):
                result = validate_artifact_writer_fixture_case(case_dir)

                self.assertEqual(result.writer_status, "fail")
                self.assertEqual(result.reason_codes, [expected_reason])
                self.assertEqual(result.failed_checks, [expected_reason])
                self.assertEqual([], compare_artifact_writer_fixture_to_expected(case_dir))
                assert_safe_artifact_writer_text(
                    self, json.dumps(result.to_safe_dict(), sort_keys=True)
                )

    def test_artifact_flags_required_and_fixed_values(self) -> None:
        for case_dir in discover_artifact_writer_fixture_cases(FIXTURE_ROOT):
            result = validate_artifact_writer_fixture_case(case_dir)
            with self.subTest(case=result.case_label):
                self.assertEqual(result.artifact_flags, EXPECTED_ARTIFACT_FLAG_VALUES)

    def test_safety_flags_required_and_true_values(self) -> None:
        for case_dir in discover_artifact_writer_fixture_cases(FIXTURE_ROOT):
            result = validate_artifact_writer_fixture_case(case_dir)
            with self.subTest(case=result.case_label):
                self.assertTrue(all(result.safety_flags.values()))
                self.assertTrue(result.content_suppressed)
                self.assertTrue(result.no_raw_rows)
                self.assertTrue(result.no_logits_dump)
                self.assertTrue(result.no_private_paths)

    def test_count_summary_zero_constraints(self) -> None:
        zero_fields = (
            "body_field_count",
            "raw_row_count",
            "logits_dump_count",
            "private_path_count",
            "performance_metric_count",
            "generated_artifact_count",
            "written_file_count",
            "manifest_body_count",
        )
        for case_dir in discover_artifact_writer_fixture_cases(FIXTURE_ROOT):
            result = validate_artifact_writer_fixture_case(case_dir)
            with self.subTest(case=result.case_label):
                for field_name in zero_fields:
                    self.assertEqual(result.count_summary[field_name], 0)
                self.assertGreaterEqual(
                    result.count_summary["validation_reference_count"], 1
                )

    def test_safe_marker_booleans_are_allowed(self) -> None:
        for case_dir in discover_artifact_writer_fixture_cases(FIXTURE_ROOT):
            scan = scan_artifact_writer_fixture_for_forbidden_markers(case_dir)
            with self.subTest(case=f"{case_dir.parent.name}/{case_dir.name}"):
                self.assertEqual(scan.reason_codes, [])
                self.assertEqual(scan.failed_checks, [])

    def test_unsafe_body_key_scan_detects_forbidden_keys(self) -> None:
        source = FIXTURE_ROOT / "valid" / "minimal_metadata_only_artifact_plan"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "unsafe_body_key"
            shutil.copytree(source, tmp_case)
            request_path = tmp_case / "artifact_writer_request.json"
            request = json.loads(request_path.read_text(encoding="utf-8"))
            request["artifact_body"] = "synthetic_body_marker"
            request_path.write_text(json.dumps(request), encoding="utf-8")

            scan = scan_artifact_writer_fixture_for_forbidden_markers(tmp_case)

        self.assertIn("forbidden_payload_key", scan.reason_codes)
        self.assertIn("artifact_body", scan.failed_checks)

    def test_summary_is_json_serializable_and_body_free(self) -> None:
        root_result = validate_artifact_writer_fixture_root(FIXTURE_ROOT)
        payload = summarize_artifact_writer_fixture_validation_result(root_result)
        rendered = json.dumps(payload, sort_keys=True)

        json.loads(rendered)
        assert_safe_artifact_writer_text(self, rendered)

    def test_summary_is_deterministic(self) -> None:
        first = summarize_artifact_writer_fixture_validation_result(
            validate_artifact_writer_fixture_root(FIXTURE_ROOT)
        )
        second = summarize_artifact_writer_fixture_validation_result(
            validate_artifact_writer_fixture_root(FIXTURE_ROOT)
        )

        self.assertEqual(first, second)

    def test_temp_missing_required_file_returns_input_error(self) -> None:
        source = FIXTURE_ROOT / "valid" / "minimal_metadata_only_artifact_plan"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "missing_request"
            shutil.copytree(source, tmp_case)
            (tmp_case / "artifact_writer_request.json").unlink()

            result = validate_artifact_writer_fixture_case(tmp_case)

        self.assertEqual(result.writer_status, "input_error")
        self.assertIn("malformed_fixture_file", result.reason_codes)
        assert_safe_artifact_writer_text(
            self, json.dumps(result.to_safe_dict(), sort_keys=True)
        )

    def test_temp_malformed_json_returns_input_error(self) -> None:
        source = FIXTURE_ROOT / "valid" / "minimal_metadata_only_artifact_plan"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "malformed_request"
            shutil.copytree(source, tmp_case)
            (tmp_case / "artifact_writer_request.json").write_text(
                "{", encoding="utf-8"
            )

            result = validate_artifact_writer_fixture_case(tmp_case)

        self.assertEqual(result.writer_status, "input_error")
        self.assertIn("malformed_fixture_file", result.reason_codes)
        assert_safe_artifact_writer_text(
            self, json.dumps(result.to_safe_dict(), sort_keys=True)
        )


def assert_safe_artifact_writer_text(
    test_case: unittest.TestCase,
    text: str,
) -> None:
    assert_no_forbidden_fragments(
        test_case,
        text,
        [
            '"artifact_writer_request":',
            '"generator_result_pointer":',
            '"expected_artifact_writer_result":',
            '"request_body":',
            '"pointer_body":',
            '"expected_result_body":',
            '"artifact_body":',
            '"generated_policy_body":',
            '"generated_artifact_body":',
            '"manifest_body":',
            '"policy_body":',
            '"raw_rows":',
            '"logits":',
            '"probabilities":',
            '"raw_learner_text":',
            '"observed_after_text":',
            '"final_text":',
            '"gold_label":',
            '"private_path":',
            '"absolute_path":',
            '"real_participant_data":',
            '"performance_metrics":',
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
