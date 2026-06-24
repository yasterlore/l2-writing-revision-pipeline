from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_artifact_body_file_writing_fixture_validation import (
    EXPECTED_INVALID_REASONS,
    EXPECTED_JSON_FILE_COUNT,
    EXPECTED_TOTAL_CASES,
    EXPECTED_VALID_CASES,
    DEFAULT_FIXTURE_ROOT,
    discover_fixture_cases,
    summarize_file_writing_fixture_validation,
    validate_fixture_case,
    validate_fixture_root,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = DEFAULT_FIXTURE_ROOT
REQUIRED_FILES = {
    "artifact_body_request.json",
    "artifact_writer_result_pointer.json",
    "file_write_request.json",
    "expected_file_write_result.json",
}


class FrozenPolicyGenerationArtifactBodyFileWritingFixtureValidationTests(
    unittest.TestCase
):
    def test_fixture_root_has_expected_shape_and_json_count(self) -> None:
        case_dirs = sorted(path for path in FIXTURE_ROOT.glob("*/*") if path.is_dir())
        json_files = sorted(FIXTURE_ROOT.glob("*/*/*.json"))

        self.assertEqual(len(case_dirs), EXPECTED_TOTAL_CASES)
        self.assertEqual(len(json_files), EXPECTED_JSON_FILE_COUNT)
        self.assertEqual(sum(path.parent.name == "valid" for path in case_dirs), 5)
        self.assertEqual(sum(path.parent.name == "invalid" for path in case_dirs), 24)

    def test_every_case_has_required_files_and_json_parses(self) -> None:
        for case_dir in sorted(path for path in FIXTURE_ROOT.glob("*/*") if path.is_dir()):
            with self.subTest(case=f"{case_dir.parent.name}/{case_dir.name}"):
                names = {path.name for path in case_dir.glob("*.json")}
                self.assertEqual(names, REQUIRED_FILES)
                for file_name in REQUIRED_FILES:
                    self.assertIsInstance(json.loads((case_dir / file_name).read_text()), dict)

    def test_root_validation_matches_all_expected_cases(self) -> None:
        summary = validate_fixture_root(FIXTURE_ROOT)

        self.assertEqual(summary.total_cases, EXPECTED_TOTAL_CASES)
        self.assertEqual(summary.valid_cases, EXPECTED_VALID_CASES)
        self.assertEqual(summary.invalid_cases, 24)
        self.assertEqual(summary.matched_cases, EXPECTED_TOTAL_CASES)
        self.assertEqual(summary.mismatched_cases, 0)
        self.assertEqual(summary.input_error_cases, 0)
        self.assertTrue(summary.content_suppressed)
        self.assertTrue(summary.no_raw_rows)
        self.assertTrue(summary.no_logits_dump)
        self.assertTrue(summary.no_private_paths)
        self.assertTrue(summary.synthetic_only_checked)
        self.assertTrue(summary.no_oracle_checked)
        self.assertTrue(summary.path_policy_checked)
        self.assertTrue(summary.body_content_policy_checked)
        self.assertTrue(summary.stdout_body_suppression_checked)
        self.assertTrue(summary.manifest_absence_checked)
        self.assertFalse(summary.file_writing_isolated)

    def test_valid_cases_match_expected_pass(self) -> None:
        for case in discover_fixture_cases(FIXTURE_ROOT):
            if case.expected_kind != "valid":
                continue
            with self.subTest(case=case.case_label):
                result = validate_fixture_case(case.case_dir, case.expected_kind)
                self.assertEqual(result.validation_status, "pass")
                self.assertEqual(result.expected_status, "pass")
                self.assertEqual(result.reason_codes, [])
                self.assertEqual(result.failed_checks, [])

    def test_invalid_cases_match_expected_fail_closed_or_usage_error(self) -> None:
        for case_label, expected_reason in sorted(EXPECTED_INVALID_REASONS.items()):
            case_dir = FIXTURE_ROOT / case_label
            with self.subTest(case=case_label):
                result = validate_fixture_case(case_dir, "invalid")
                self.assertIn(result.validation_status, {"fail_closed", "usage_error"})
                self.assertIn(result.expected_status, {"fail_closed", "usage_error"})
                self.assertEqual(result.reason_codes, [expected_reason])
                self.assertEqual(len(result.failed_checks), 1)

    def test_reason_code_counts_include_expected_invalid_reasons(self) -> None:
        summary = validate_fixture_root(FIXTURE_ROOT)

        for reason in EXPECTED_INVALID_REASONS.values():
            with self.subTest(reason=reason):
                self.assertEqual(summary.reason_code_counts.get(reason), 1)

    def test_summary_output_is_body_free_and_safe(self) -> None:
        rendered = summarize_file_writing_fixture_validation(
            validate_fixture_root(FIXTURE_ROOT)
        )

        assert_no_forbidden_fragments(
            self,
            rendered,
            [
                '"artifact_body_request":',
                '"artifact_writer_result_pointer":',
                '"file_write_request":',
                '"expected_file_write_result":',
                '"request_body":',
                '"pointer_body":',
                '"expected_body":',
                '"artifact_body_payload":',
                '"manifest_body":',
                '"raw_rows":',
                '"logits":',
                '"probabilities":',
                '"private_path":',
                '"raw_learner_text":',
                '"performance_metrics":',
                "/Users/",
                "/private/",
            ],
        )

    def test_validator_does_not_write_files_or_create_temp_dirs(self) -> None:
        before = sorted(path.relative_to(FIXTURE_ROOT) for path in FIXTURE_ROOT.rglob("*"))

        validate_fixture_root(FIXTURE_ROOT)

        after = sorted(path.relative_to(FIXTURE_ROOT) for path in FIXTURE_ROOT.rglob("*"))
        self.assertEqual(after, before)

    def test_unsafe_path_and_leakage_sentinel_cases_match(self) -> None:
        expected_cases = {
            "invalid/invalid_absolute_output_path": "absolute_output_path",
            "invalid/invalid_parent_traversal_output_path": "parent_traversal_output_path",
            "invalid/invalid_private_path_marker_output_path": "private_path_marker_output_path",
            "invalid/invalid_request_body_leakage_in_file": "request_body_leakage_in_file",
            "invalid/invalid_logits_dump_in_file": "logits_dump_in_file",
            "invalid/invalid_raw_learner_text_in_file": "raw_learner_text_in_file",
            "invalid/invalid_missing_synthetic_notice": "missing_synthetic_notice",
            "invalid/invalid_output_path_outside_allowed_root": "output_path_outside_allowed_root",
        }

        for case_label, reason in expected_cases.items():
            with self.subTest(case=case_label):
                result = validate_fixture_case(FIXTURE_ROOT / case_label, "invalid")
                self.assertEqual(result.reason_codes, [reason])
                self.assertNotEqual(result.validation_status, "input_error")

    def test_schema_version_mismatch_temp_fixture_is_detected(self) -> None:
        source = FIXTURE_ROOT / "valid" / "valid_safe_metadata_relative_tmp_output"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "schema_mismatch"
            shutil.copytree(source, tmp_case)
            request_path = tmp_case / "artifact_body_request.json"
            payload = json.loads(request_path.read_text())
            payload["schema_version"] = "unknown_schema_v0"
            payload["case_id"] = "valid/schema_mismatch"
            request_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            for file_name in (
                "artifact_writer_result_pointer.json",
                "file_write_request.json",
                "expected_file_write_result.json",
            ):
                path = tmp_case / file_name
                data = json.loads(path.read_text())
                data["case_id"] = "valid/schema_mismatch"
                path.write_text(json.dumps(data, sort_keys=True), encoding="utf-8")
            result = validate_fixture_case(tmp_case, "valid")

        self.assertEqual(result.validation_status, "input_error")
        self.assertIn("schema_version_unknown", result.reason_codes)

    def test_required_file_missing_temp_fixture_is_detected(self) -> None:
        source = FIXTURE_ROOT / "valid" / "valid_safe_metadata_relative_tmp_output"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "missing_file"
            shutil.copytree(source, tmp_case)
            (tmp_case / "file_write_request.json").unlink()
            result = validate_fixture_case(tmp_case, "valid")

        self.assertEqual(result.validation_status, "input_error")
        self.assertIn("required_file_missing", result.reason_codes)

    def test_case_id_mismatch_temp_fixture_is_detected(self) -> None:
        source = FIXTURE_ROOT / "valid" / "valid_safe_metadata_relative_tmp_output"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "case_id_mismatch"
            shutil.copytree(source, tmp_case)
            request_path = tmp_case / "artifact_body_request.json"
            payload = json.loads(request_path.read_text())
            payload["case_id"] = "valid/different_case_id"
            request_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            for file_name in (
                "artifact_writer_result_pointer.json",
                "file_write_request.json",
                "expected_file_write_result.json",
            ):
                path = tmp_case / file_name
                data = json.loads(path.read_text())
                data["case_id"] = "valid/case_id_mismatch"
                path.write_text(json.dumps(data, sort_keys=True), encoding="utf-8")
            result = validate_fixture_case(tmp_case, "valid")

        self.assertEqual(result.validation_status, "input_error")
        self.assertIn("case_id_mismatch", result.reason_codes)


if __name__ == "__main__":
    unittest.main()
