from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_manifest_writer_production_file_writing_fixture_validation import (
    DEFAULT_FIXTURE_ROOT,
    EXPECTED_FAIL_CLOSED_CASES,
    EXPECTED_INVALID_CASES,
    EXPECTED_PASS_NO_WRITE_CASES,
    EXPECTED_PASS_WRITTEN_CASES,
    EXPECTED_TOTAL_CASES,
    EXPECTED_TOTAL_JSON_FILES,
    EXPECTED_USAGE_ERROR_CASES,
    EXPECTED_VALID_CASES,
    REQUIRED_FILES,
    summarize_manifest_writer_production_file_writing_fixture_validation,
    validate_manifest_writer_production_file_writing_fixture_case,
    validate_manifest_writer_production_file_writing_fixture_root,
)

FIXTURE_ROOT = DEFAULT_FIXTURE_ROOT
VALID_PASS_WRITTEN = "valid/minimal_manifest_out_file_written"
VALID_PASS_NO_WRITE = "valid/no_manifest_out_default_no_file"
VALID_OVERWRITE_ALLOWED = "valid/overwrite_allowed_existing_file"
INVALID_USAGE_ERROR = "invalid/unsafe_absolute_manifest_output_path"
INVALID_OUTPUT_EXISTS = "invalid/output_exists_without_overwrite"
INVALID_FAIL_CLOSED = "invalid/manifest_body_requested"
GROUPED_REQUEST_POINTER_EXPECTED = "invalid/request_pointer_expected_body_leakage"
GROUPED_RAW_LOGIT_PRIVATE_TEXT = "invalid/raw_rows_logits_private_raw_text_leakage"


class FrozenPolicyGenerationManifestWriterProductionFileWritingFixtureValidationTests(
    unittest.TestCase
):
    def test_fixture_root_shape_and_json_count(self) -> None:
        case_dirs = sorted(path for path in FIXTURE_ROOT.glob("*/*") if path.is_dir())
        json_files = sorted(FIXTURE_ROOT.glob("*/*/*.json"))

        self.assertEqual(len(case_dirs), EXPECTED_TOTAL_CASES)
        self.assertEqual(len(json_files), EXPECTED_TOTAL_JSON_FILES)
        self.assertEqual(sum(path.parent.name == "valid" for path in case_dirs), 8)
        self.assertEqual(sum(path.parent.name == "invalid" for path in case_dirs), 24)

    def test_every_case_has_required_files_and_json_parses(self) -> None:
        required = set(REQUIRED_FILES)
        for case_dir in sorted(path for path in FIXTURE_ROOT.glob("*/*") if path.is_dir()):
            with self.subTest(case=f"{case_dir.parent.name}/{case_dir.name}"):
                names = {path.name for path in case_dir.glob("*.json")}
                self.assertEqual(names, required)
                for file_name in REQUIRED_FILES:
                    payload = json.loads((case_dir / file_name).read_text())
                    self.assertIsInstance(payload, dict)
                    self.assertIn("schema_version", payload)

    def test_root_validation_matches_expected_counts(self) -> None:
        summary = validate_manifest_writer_production_file_writing_fixture_root(
            FIXTURE_ROOT
        )

        self.assertEqual(summary.total_cases, EXPECTED_TOTAL_CASES)
        self.assertEqual(summary.valid_cases, EXPECTED_VALID_CASES)
        self.assertEqual(summary.invalid_cases, EXPECTED_INVALID_CASES)
        self.assertEqual(summary.total_json_files, EXPECTED_TOTAL_JSON_FILES)
        self.assertEqual(summary.pass_written_cases, EXPECTED_PASS_WRITTEN_CASES)
        self.assertEqual(summary.pass_no_write_cases, EXPECTED_PASS_NO_WRITE_CASES)
        self.assertEqual(summary.usage_error_cases, EXPECTED_USAGE_ERROR_CASES)
        self.assertEqual(summary.fail_closed_cases, EXPECTED_FAIL_CLOSED_CASES)
        self.assertEqual(summary.matched_cases, EXPECTED_TOTAL_CASES)
        self.assertEqual(summary.mismatched_cases, 0)
        self.assertEqual(summary.input_error_cases, 0)

    def test_single_valid_pass_written_case_matches(self) -> None:
        result = validate_manifest_writer_production_file_writing_fixture_case(
            FIXTURE_ROOT / VALID_PASS_WRITTEN,
            expected_kind="valid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(result.actual_category, "pass_written")
        self.assertEqual(result.actual_writer_status, "pass")
        self.assertTrue(result.manifest_file_written)
        self.assertEqual(result.written_file_count, 1)
        self.assertEqual(result.reason_codes, ())

    def test_single_valid_pass_no_write_case_matches(self) -> None:
        result = validate_manifest_writer_production_file_writing_fixture_case(
            FIXTURE_ROOT / VALID_PASS_NO_WRITE,
            expected_kind="valid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(result.actual_category, "pass_no_write")
        self.assertFalse(result.manifest_file_written)
        self.assertEqual(result.written_file_count, 0)

    def test_single_invalid_usage_error_path_case_matches(self) -> None:
        result = validate_manifest_writer_production_file_writing_fixture_case(
            FIXTURE_ROOT / INVALID_USAGE_ERROR,
            expected_kind="invalid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(result.actual_category, "usage_error")
        self.assertEqual(
            result.reason_codes, ("unsafe_absolute_manifest_output_path",)
        )

    def test_single_invalid_fail_closed_body_case_matches(self) -> None:
        result = validate_manifest_writer_production_file_writing_fixture_case(
            FIXTURE_ROOT / INVALID_FAIL_CLOSED,
            expected_kind="invalid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(result.actual_category, "fail_closed")
        self.assertEqual(result.reason_codes, ("manifest_body_requested",))

    def test_overwrite_allowed_valid_case_matches(self) -> None:
        result = validate_manifest_writer_production_file_writing_fixture_case(
            FIXTURE_ROOT / VALID_OVERWRITE_ALLOWED,
            expected_kind="valid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(result.actual_category, "pass_written")
        self.assertEqual(result.written_file_count, 1)

    def test_output_exists_without_overwrite_invalid_case_matches(self) -> None:
        result = validate_manifest_writer_production_file_writing_fixture_case(
            FIXTURE_ROOT / INVALID_OUTPUT_EXISTS,
            expected_kind="invalid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(result.actual_category, "usage_error")
        self.assertEqual(result.reason_codes, ("output_exists_without_overwrite",))

    def test_grouped_request_pointer_expected_reason_case_matches(self) -> None:
        result = validate_manifest_writer_production_file_writing_fixture_case(
            FIXTURE_ROOT / GROUPED_REQUEST_POINTER_EXPECTED,
            expected_kind="invalid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(
            set(result.reason_codes),
            {"request_body_leakage", "pointer_body_leakage", "expected_body_leakage"},
        )

    def test_grouped_raw_logit_private_text_reason_case_matches(self) -> None:
        result = validate_manifest_writer_production_file_writing_fixture_case(
            FIXTURE_ROOT / GROUPED_RAW_LOGIT_PRIVATE_TEXT,
            expected_kind="invalid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(
            set(result.reason_codes),
            {
                "raw_rows_leakage",
                "logits_dump_leakage",
                "private_path_leakage",
                "absolute_path_leakage",
                "raw_learner_text_leakage",
            },
        )

    def test_missing_required_file_reports_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / VALID_PASS_WRITTEN
            shutil.copytree(FIXTURE_ROOT / VALID_PASS_WRITTEN, tmp_case)
            (tmp_case / "manifest_writer_request.json").unlink()
            result = validate_manifest_writer_production_file_writing_fixture_case(
                tmp_case,
                expected_kind="valid",
            )

        self.assertTrue(result.input_error)
        self.assertIn("required_file_missing", result.reason_codes)

    def test_malformed_json_reports_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / VALID_PASS_WRITTEN
            shutil.copytree(FIXTURE_ROOT / VALID_PASS_WRITTEN, tmp_case)
            (tmp_case / "case_metadata.json").write_text("{", encoding="utf-8")
            result = validate_manifest_writer_production_file_writing_fixture_case(
                tmp_case,
                expected_kind="valid",
            )

        self.assertTrue(result.input_error)
        self.assertIn("malformed_fixture_json", result.reason_codes)

    def test_schema_mismatch_reports_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / VALID_PASS_WRITTEN
            shutil.copytree(FIXTURE_ROOT / VALID_PASS_WRITTEN, tmp_case)
            target = tmp_case / "case_metadata.json"
            payload = json.loads(target.read_text(encoding="utf-8"))
            payload["schema_version"] = "wrong_schema"
            target.write_text(json.dumps(payload), encoding="utf-8")
            result = validate_manifest_writer_production_file_writing_fixture_case(
                tmp_case,
                expected_kind="valid",
            )

        self.assertTrue(result.is_mismatch)
        self.assertIn("case_metadata_schema_version_mismatch", result.mismatch_reasons)

    def test_case_id_mismatch_reports_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / VALID_PASS_WRITTEN
            shutil.copytree(FIXTURE_ROOT / VALID_PASS_WRITTEN, tmp_case)
            target = tmp_case / "case_metadata.json"
            payload = json.loads(target.read_text(encoding="utf-8"))
            payload["case_id"] = "valid/wrong_case_id"
            target.write_text(json.dumps(payload), encoding="utf-8")
            result = validate_manifest_writer_production_file_writing_fixture_case(
                tmp_case,
                expected_kind="valid",
            )

        self.assertTrue(result.is_mismatch)
        self.assertIn("case_metadata_case_id_mismatch", result.mismatch_reasons)

    def test_category_mismatch_reports_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / VALID_PASS_WRITTEN
            shutil.copytree(FIXTURE_ROOT / VALID_PASS_WRITTEN, tmp_case)
            target = tmp_case / "expected_production_file_writing_result.json"
            payload = json.loads(target.read_text(encoding="utf-8"))
            payload["expected_category"] = "pass_no_write"
            target.write_text(json.dumps(payload), encoding="utf-8")
            result = validate_manifest_writer_production_file_writing_fixture_case(
                tmp_case,
                expected_kind="valid",
            )

        self.assertTrue(result.is_mismatch)
        self.assertIn("expected_manifest_file_written_not_false", result.mismatch_reasons)

    def test_unsafe_selector_cli_returns_usage_error(self) -> None:
        completed = run_cli("--fixture-case", "../escape")

        self.assertEqual(completed.returncode, 2)
        self.assertIn("input_error_cases=1", completed.stdout)
        assert_body_free_output(self, completed.stdout + completed.stderr)

    def test_body_free_human_output(self) -> None:
        rendered = summarize_manifest_writer_production_file_writing_fixture_validation(
            validate_manifest_writer_production_file_writing_fixture_root(FIXTURE_ROOT)
        )

        self.assertIn(
            "mode=manifest_writer_production_file_writing_fixture_validation",
            rendered,
        )
        self.assertIn("total_cases=32", rendered)
        self.assertIn("public_absolute_path_suppressed=true", rendered)
        assert_body_free_output(self, rendered)

    def test_json_output_parseable_and_body_free(self) -> None:
        rendered = summarize_manifest_writer_production_file_writing_fixture_validation(
            validate_manifest_writer_production_file_writing_fixture_root(FIXTURE_ROOT),
            as_json=True,
        )
        payload = json.loads(rendered)

        self.assertEqual(payload["total_cases"], EXPECTED_TOTAL_CASES)
        self.assertEqual(payload["matched_cases"], EXPECTED_TOTAL_CASES)
        self.assertNotIn("case_results", payload)
        self.assertTrue(payload["public_absolute_path_suppressed"])
        self.assertFalse(payload["release_quality_ready"])
        assert_body_free_output(self, rendered)

    def test_cli_single_cases(self) -> None:
        selectors = (
            (VALID_PASS_WRITTEN, "pass_written_cases"),
            (VALID_PASS_NO_WRITE, "pass_no_write_cases"),
            (INVALID_USAGE_ERROR, "usage_error_cases"),
            (INVALID_FAIL_CLOSED, "fail_closed_cases"),
        )
        for selector, count_key in selectors:
            with self.subTest(selector=selector):
                completed = run_cli("--fixture-case", selector, "--json")
                self.assertEqual(completed.returncode, 0)
                payload = json.loads(completed.stdout)
                self.assertEqual(payload["total_cases"], 1)
                self.assertEqual(payload["matched_cases"], 1)
                self.assertEqual(payload[count_key], 1)
                assert_body_free_output(self, completed.stdout + completed.stderr)

    def test_cli_help_exits_zero(self) -> None:
        completed = run_cli("--help")

        self.assertEqual(completed.returncode, 0)
        self.assertIn("--fixture-root", completed.stdout)
        self.assertIn("--fixture-case", completed.stdout)
        self.assertIn("--json", completed.stdout)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "learner_state.frozen_policy_generation_manifest_writer_production_file_writing_fixture_validation",
            *args,
        ],
        check=False,
        cwd=Path.cwd(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def assert_body_free_output(test_case: unittest.TestCase, output: str) -> None:
    forbidden = [
        '"case_metadata":',
        '"manifest_writer_request":',
        '"artifact_writer_result_pointer":',
        '"artifact_body_generation_result_pointer":',
        '"expected_production_file_writing_result":',
        '"written_file_json_body":',
        '"manifest_body":',
        '"manifest_json_body":',
        '"artifact_body_payload":',
        '"generated_policy_body":',
        '"request_body":',
        '"pointer_body":',
        '"expected_body":',
        '"raw_rows":',
        '"logits":',
        '"probabilities":',
        '"raw_learner_text":',
        "/Users/",
        "/private/",
        "/var/folders/",
        "real_data/",
        "participant_data/",
        "file_contents=",
    ]
    for fragment in forbidden:
        test_case.assertNotIn(fragment, output)


if __name__ == "__main__":
    unittest.main()
