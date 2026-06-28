from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_manifest_writer_isolated_write_validation import (
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
    summarize_manifest_writer_isolated_write_validation,
    validate_manifest_writer_isolated_write_case,
    validate_manifest_writer_isolated_write_root,
)

FIXTURE_ROOT = DEFAULT_FIXTURE_ROOT
VALID_PASS_WRITTEN = "valid/minimal_metadata_file_written"
VALID_PASS_NO_WRITE = "valid/metadata_no_file_existing_runtime_mode"
INVALID_USAGE_ERROR = "invalid/unsafe_absolute_output_path"
INVALID_FAIL_CLOSED = "invalid/manifest_body_requested"
GROUPED_REASON_CASE = "invalid/request_pointer_expected_body_written"


class FrozenPolicyGenerationManifestWriterIsolatedWriteValidationTests(
    unittest.TestCase
):
    def test_fixture_root_shape_and_json_count(self) -> None:
        case_dirs = sorted(path for path in FIXTURE_ROOT.glob("*/*") if path.is_dir())
        json_files = sorted(FIXTURE_ROOT.glob("*/*/*.json"))

        self.assertEqual(len(case_dirs), EXPECTED_TOTAL_CASES)
        self.assertEqual(len(json_files), EXPECTED_TOTAL_JSON_FILES)
        self.assertEqual(sum(path.parent.name == "valid" for path in case_dirs), 6)
        self.assertEqual(sum(path.parent.name == "invalid" for path in case_dirs), 19)

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
        summary = validate_manifest_writer_isolated_write_root(FIXTURE_ROOT)

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
        self.assertEqual(summary.residue_file_count, 0)
        self.assertTrue(summary.stdout_body_suppressed)
        self.assertTrue(summary.stderr_body_suppressed)
        self.assertTrue(summary.temp_root_isolated)
        self.assertFalse(summary.release_quality_ready)

    def test_single_valid_pass_written_case_matches(self) -> None:
        result = validate_manifest_writer_isolated_write_case(
            FIXTURE_ROOT / VALID_PASS_WRITTEN,
            expected_kind="valid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(result.actual_category, "pass_written")
        self.assertEqual(result.actual_writer_status, "pass")
        self.assertTrue(result.manifest_file_written)
        self.assertEqual(result.written_file_count, 1)
        self.assertEqual(result.parseable_json_file_count, 1)
        self.assertEqual(result.forbidden_field_count, 0)
        self.assertEqual(result.residue_file_count, 0)

    def test_single_valid_pass_no_write_case_matches(self) -> None:
        result = validate_manifest_writer_isolated_write_case(
            FIXTURE_ROOT / VALID_PASS_NO_WRITE,
            expected_kind="valid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(result.actual_category, "pass_no_write")
        self.assertFalse(result.manifest_file_written)
        self.assertEqual(result.written_file_count, 0)

    def test_single_invalid_usage_error_path_case_matches(self) -> None:
        result = validate_manifest_writer_isolated_write_case(
            FIXTURE_ROOT / INVALID_USAGE_ERROR,
            expected_kind="invalid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(result.actual_category, "usage_error")
        self.assertFalse(result.manifest_file_written)
        self.assertEqual(result.reason_codes, ("unsafe_absolute_output_path",))

    def test_single_invalid_fail_closed_body_case_matches(self) -> None:
        result = validate_manifest_writer_isolated_write_case(
            FIXTURE_ROOT / INVALID_FAIL_CLOSED,
            expected_kind="invalid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(result.actual_category, "fail_closed")
        self.assertFalse(result.manifest_file_written)
        self.assertEqual(result.reason_codes, ("manifest_body_requested",))

    def test_grouped_reason_code_case_matches(self) -> None:
        result = validate_manifest_writer_isolated_write_case(
            FIXTURE_ROOT / GROUPED_REASON_CASE,
            expected_kind="invalid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(
            set(result.reason_codes),
            {"request_body_written", "pointer_body_written", "expected_body_written"},
        )

    def test_missing_required_file_reports_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / VALID_PASS_WRITTEN
            shutil.copytree(FIXTURE_ROOT / VALID_PASS_WRITTEN, tmp_case)
            (tmp_case / "isolated_write_request.json").unlink()
            result = validate_manifest_writer_isolated_write_case(
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
            result = validate_manifest_writer_isolated_write_case(
                tmp_case,
                expected_kind="valid",
            )

        self.assertTrue(result.input_error)
        self.assertIn("malformed_fixture_json", result.reason_codes)

    def test_schema_mismatch_reports_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / VALID_PASS_WRITTEN
            shutil.copytree(FIXTURE_ROOT / VALID_PASS_WRITTEN, tmp_case)
            target = tmp_case / "case_metadata.json"
            payload = json.loads(target.read_text(encoding="utf-8"))
            payload["schema_version"] = "wrong_schema"
            target.write_text(json.dumps(payload), encoding="utf-8")
            result = validate_manifest_writer_isolated_write_case(
                tmp_case,
                expected_kind="valid",
            )

        self.assertTrue(result.input_error)
        self.assertIn("schema_version_mismatch", result.reason_codes)

    def test_case_id_mismatch_reports_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / VALID_PASS_WRITTEN
            shutil.copytree(FIXTURE_ROOT / VALID_PASS_WRITTEN, tmp_case)
            target = tmp_case / "case_metadata.json"
            payload = json.loads(target.read_text(encoding="utf-8"))
            payload["case_id"] = "valid/wrong_case_id"
            target.write_text(json.dumps(payload), encoding="utf-8")
            result = validate_manifest_writer_isolated_write_case(
                tmp_case,
                expected_kind="valid",
            )

        self.assertTrue(result.input_error)
        self.assertIn("case_id_mismatch", result.reason_codes)

    def test_category_mismatch_reports_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / VALID_PASS_WRITTEN
            shutil.copytree(FIXTURE_ROOT / VALID_PASS_WRITTEN, tmp_case)
            target = tmp_case / "expected_isolated_write_result.json"
            payload = json.loads(target.read_text(encoding="utf-8"))
            payload["expected_category"] = "pass_no_write"
            target.write_text(json.dumps(payload), encoding="utf-8")
            result = validate_manifest_writer_isolated_write_case(
                tmp_case,
                expected_kind="valid",
            )

        self.assertTrue(result.is_mismatch)
        self.assertEqual(result.actual_category, "mismatch")

    def test_unsafe_selector_cli_returns_usage_error(self) -> None:
        completed = run_cli("--fixture-case", "../escape")

        self.assertEqual(completed.returncode, 2)
        self.assertIn(
            "reason_codes=unsafe_parent_traversal_fixture_case_selector",
            completed.stdout,
        )
        assert_body_free_output(self, completed.stdout + completed.stderr)

    def test_body_free_human_output(self) -> None:
        rendered = summarize_manifest_writer_isolated_write_validation(
            validate_manifest_writer_isolated_write_root(FIXTURE_ROOT)
        )

        self.assertIn("mode=manifest_writer_isolated_write_validation", rendered)
        self.assertIn("total_cases=25", rendered)
        assert_body_free_output(self, rendered)

    def test_json_output_parseable_and_body_free(self) -> None:
        rendered = summarize_manifest_writer_isolated_write_validation(
            validate_manifest_writer_isolated_write_root(FIXTURE_ROOT),
            as_json=True,
        )
        payload = json.loads(rendered)

        self.assertEqual(payload["total_cases"], EXPECTED_TOTAL_CASES)
        self.assertEqual(payload["matched_cases"], EXPECTED_TOTAL_CASES)
        self.assertNotIn("case_results", payload)
        self.assertTrue(payload["stdout_body_suppressed"])
        self.assertTrue(payload["stderr_body_suppressed"])
        self.assertTrue(payload["temp_root_isolated"])
        self.assertFalse(payload["release_quality_ready"])
        assert_body_free_output(self, rendered)

    def test_cli_single_cases(self) -> None:
        selectors = (
            (VALID_PASS_WRITTEN, "actual_category=pass_written"),
            (VALID_PASS_NO_WRITE, "actual_category=pass_no_write"),
            (INVALID_USAGE_ERROR, "actual_category=usage_error"),
            (INVALID_FAIL_CLOSED, "actual_category=fail_closed"),
        )
        for selector, expected_fragment in selectors:
            with self.subTest(selector=selector):
                completed = run_cli("--fixture-case", selector)
                self.assertEqual(completed.returncode, 0)
                self.assertIn(expected_fragment, completed.stdout)
                self.assertIn("matched=true", completed.stdout)
                assert_body_free_output(self, completed.stdout + completed.stderr)

    def test_cli_help_exits_zero(self) -> None:
        completed = run_cli("--help")

        self.assertEqual(completed.returncode, 0)
        self.assertIn("--fixture-root", completed.stdout)
        self.assertIn("--fixture-case", completed.stdout)
        self.assertIn("--json", completed.stdout)

    def test_tmp_frozen_policy_generation_manifest_residue_zero(self) -> None:
        validate_manifest_writer_isolated_write_case(
            FIXTURE_ROOT / VALID_PASS_WRITTEN,
            expected_kind="valid",
        )
        residue_root = Path("tmp/frozen_policy_generation_manifest")
        residue_count = (
            sum(1 for path in residue_root.rglob("*") if path.is_file())
            if residue_root.exists()
            else 0
        )
        self.assertEqual(residue_count, 0)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "learner_state.frozen_policy_generation_manifest_writer_isolated_write_validation",
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
        '"isolated_write_request":',
        '"manifest_writer_request":',
        '"artifact_writer_result_pointer":',
        '"artifact_body_generation_result_pointer":',
        '"expected_isolated_write_result":',
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
