from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_artifact_body_isolated_write_validation import (
    DEFAULT_FIXTURE_ROOT,
    EXPECTED_INVALID_CASES,
    EXPECTED_JSON_FILE_COUNT,
    EXPECTED_TOTAL_CASES,
    EXPECTED_VALID_CASES,
    _scan_written_body_file,
    _stream_is_body_free,
    summarize_isolated_write_validation,
    validate_isolated_write_fixture_case,
    validate_isolated_write_fixture_root,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = DEFAULT_FIXTURE_ROOT
REQUIRED_FILES = {
    "case_metadata.json",
    "artifact_body_request.json",
    "artifact_writer_result_pointer.json",
    "isolated_write_request.json",
    "expected_isolated_write_result.json",
}


class FrozenPolicyGenerationArtifactBodyIsolatedWriteValidationTests(
    unittest.TestCase
):
    def test_fixture_root_has_expected_shape_and_json_count(self) -> None:
        case_dirs = sorted(path for path in FIXTURE_ROOT.glob("*/*") if path.is_dir())
        json_files = sorted(FIXTURE_ROOT.glob("*/*/*.json"))

        self.assertEqual(len(case_dirs), EXPECTED_TOTAL_CASES)
        self.assertEqual(len(json_files), EXPECTED_JSON_FILE_COUNT)
        self.assertEqual(sum(path.parent.name == "valid" for path in case_dirs), 5)
        self.assertEqual(sum(path.parent.name == "invalid" for path in case_dirs), 17)

    def test_every_case_has_required_files_and_json_parses(self) -> None:
        for case_dir in sorted(path for path in FIXTURE_ROOT.glob("*/*") if path.is_dir()):
            with self.subTest(case=f"{case_dir.parent.name}/{case_dir.name}"):
                names = {path.name for path in case_dir.glob("*.json")}
                self.assertEqual(names, REQUIRED_FILES)
                for file_name in REQUIRED_FILES:
                    self.assertIsInstance(json.loads((case_dir / file_name).read_text()), dict)

    def test_root_validation_matches_all_expected_cases(self) -> None:
        summary = validate_isolated_write_fixture_root(FIXTURE_ROOT)

        self.assertEqual(summary.total_cases, EXPECTED_TOTAL_CASES)
        self.assertEqual(summary.valid_cases, EXPECTED_VALID_CASES)
        self.assertEqual(summary.invalid_cases, EXPECTED_INVALID_CASES)
        self.assertEqual(summary.pass_written_cases, 3)
        self.assertEqual(summary.pass_no_write_cases, 1)
        self.assertEqual(summary.usage_error_cases, 14)
        self.assertEqual(summary.fail_closed_cases, 4)
        self.assertEqual(summary.matched_cases, EXPECTED_TOTAL_CASES)
        self.assertEqual(summary.mismatched_cases, 0)
        self.assertEqual(summary.input_error_cases, 0)
        self.assertEqual(summary.residue_file_count, 0)
        self.assertFalse(summary.body_payload_printed)
        self.assertTrue(summary.stdout_body_suppressed)
        self.assertTrue(summary.stderr_body_suppressed)
        self.assertTrue(summary.no_raw_rows)
        self.assertTrue(summary.no_logits_dump)
        self.assertTrue(summary.no_private_paths)
        self.assertTrue(summary.no_absolute_paths)
        self.assertTrue(summary.no_manifest_body)
        self.assertTrue(summary.no_generated_policy_body)
        self.assertTrue(summary.synthetic_only_checked)
        self.assertTrue(summary.no_oracle_checked)
        self.assertTrue(summary.path_policy_checked)
        self.assertTrue(summary.file_content_policy_checked)
        self.assertTrue(summary.cleanup_checked)
        self.assertTrue(summary.temp_root_isolated)
        self.assertFalse(summary.release_quality_ready)

    def test_single_pass_written_case_passes(self) -> None:
        result = validate_isolated_write_fixture_case(
            FIXTURE_ROOT / "valid" / "safe_metadata_flat_relative_output",
            "valid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(result.actual_category, "pass_written")
        self.assertEqual(result.validation_status, "pass")
        self.assertTrue(result.actual_file_written)
        self.assertTrue(result.file_parse_ok)
        self.assertTrue(result.file_allowed_keys_only)
        self.assertEqual(result.residue_file_count, 0)

    def test_single_usage_error_no_write_case_passes(self) -> None:
        result = validate_isolated_write_fixture_case(
            FIXTURE_ROOT / "valid" / "safe_metadata_existing_output_rejected_after_precreate",
            "valid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(result.actual_category, "usage_error_no_write")
        self.assertEqual(result.validation_status, "usage_error")
        self.assertFalse(result.actual_file_written)

    def test_single_fail_closed_no_write_case_passes(self) -> None:
        result = validate_isolated_write_fixture_case(
            FIXTURE_ROOT / "invalid" / "generation_fail_closed_no_file",
            "invalid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(result.actual_category, "fail_closed_no_write")
        self.assertEqual(result.validation_status, "fail_closed")
        self.assertFalse(result.actual_file_written)

    def test_summary_output_is_body_free_and_has_no_absolute_temp_path(self) -> None:
        rendered = summarize_isolated_write_validation(
            validate_isolated_write_fixture_root(FIXTURE_ROOT)
        )

        assert_safe_output(self, rendered)

    def test_missing_required_file_input_error(self) -> None:
        source = FIXTURE_ROOT / "valid" / "safe_metadata_flat_relative_output"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "missing_file"
            shutil.copytree(source, tmp_case)
            (tmp_case / "isolated_write_request.json").unlink()
            result = validate_isolated_write_fixture_case(tmp_case, "valid")

        self.assertEqual(result.validation_status, "input_error")
        self.assertIn("required_file_missing", result.reason_codes)

    def test_case_id_mismatch_input_error(self) -> None:
        source = FIXTURE_ROOT / "valid" / "safe_metadata_flat_relative_output"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "case_id_mismatch"
            shutil.copytree(source, tmp_case)
            request_path = tmp_case / "case_metadata.json"
            payload = json.loads(request_path.read_text())
            payload["case_id"] = "valid/different_case"
            request_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            result = validate_isolated_write_fixture_case(tmp_case, "valid")

        self.assertEqual(result.validation_status, "input_error")
        self.assertIn("case_id_mismatch", result.reason_codes)

    def test_stdout_stderr_scan_detects_forbidden_marker(self) -> None:
        self.assertFalse(_stream_is_body_free("artifact_body_payload"))
        self.assertFalse(_stream_is_body_free("/Users/example/private"))
        self.assertTrue(_stream_is_body_free("mode=isolated_write_validation"))

    def test_written_file_allowed_key_scan_detects_forbidden_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "body.json"
            path.write_text(json.dumps({"raw_rows": []}), encoding="utf-8")
            result = _scan_written_body_file(path)

        self.assertTrue(result["parse_ok"])
        self.assertFalse(result["allowed_keys_only"])

    def test_cleanup_leaves_no_repo_safe_root_residue(self) -> None:
        validate_isolated_write_fixture_case(
            FIXTURE_ROOT / "valid" / "safe_metadata_flat_relative_output",
            "valid",
        )
        safe_root = Path("tmp/artifact_body_generation")
        residue = list(safe_root.rglob("*")) if safe_root.exists() else []
        self.assertEqual([path for path in residue if path.is_file()], [])


class FrozenPolicyGenerationArtifactBodyIsolatedWriteValidationCliTests(
    unittest.TestCase
):
    def test_help_exits_zero(self) -> None:
        completed = run_cli("--help")

        self.assertEqual(completed.returncode, 0)
        self.assertIn("--fixture-root", completed.stdout)
        self.assertIn("--fixture-case", completed.stdout)
        self.assertIn("--json", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_default_root_human_output_exits_zero(self) -> None:
        completed = run_cli()

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=isolated_write_validation", completed.stdout)
        self.assertIn("total_cases=22", completed.stdout)
        self.assertIn("valid_cases=5", completed.stdout)
        self.assertIn("invalid_cases=17", completed.stdout)
        self.assertIn("matched_cases=22", completed.stdout)
        self.assertIn("mismatched_cases=0", completed.stdout)
        self.assertIn("input_error_cases=0", completed.stdout)
        self.assertIn("residue_file_count=0", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_default_root_json_output_is_parseable_and_body_free(self) -> None:
        completed = run_cli("--json")

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "isolated_write_validation")
        self.assertEqual(payload["total_cases"], 22)
        self.assertEqual(payload["valid_cases"], 5)
        self.assertEqual(payload["invalid_cases"], 17)
        self.assertEqual(payload["matched_cases"], 22)
        self.assertEqual(payload["mismatched_cases"], 0)
        self.assertEqual(payload["input_error_cases"], 0)
        self.assertFalse(payload["body_payload_printed"])
        self.assertFalse(payload["release_quality_ready"])
        self.assertNotIn("artifact_body_request", payload)
        self.assertNotIn("isolated_write_request", payload)
        assert_safe_cli_output(self, completed)

    def test_single_valid_case_exits_zero(self) -> None:
        completed = run_cli("--fixture-case", "valid/safe_metadata_flat_relative_output")

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=isolated_write_fixture_case", completed.stdout)
        self.assertIn("case_id=valid/safe_metadata_flat_relative_output", completed.stdout)
        self.assertIn("actual_category=pass_written", completed.stdout)
        self.assertIn("matched=true", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_single_invalid_expected_failure_exits_zero(self) -> None:
        completed = run_cli("--fixture-case", "invalid/generation_fail_closed_no_file")

        self.assertEqual(completed.returncode, 0)
        self.assertIn("case_id=invalid/generation_fail_closed_no_file", completed.stdout)
        self.assertIn("actual_category=fail_closed_no_write", completed.stdout)
        self.assertIn("matched=true", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_unsafe_fixture_selector_rejected(self) -> None:
        completed = run_cli("--fixture-case", "../valid/escape")

        self.assertEqual(completed.returncode, 2)
        self.assertIn("reason_codes=unsafe_parent_traversal_fixture_case_selector", completed.stdout)
        self.assertNotIn("../valid/escape", completed.stdout + completed.stderr)
        assert_safe_cli_output(self, completed)

    def test_malformed_root_exits_four(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            malformed_root = Path(tmp_dir) / "fixtures"
            malformed_root.mkdir()
            completed = run_cli("--fixture-root", str(malformed_root))

        self.assertEqual(completed.returncode, 4)
        self.assertIn("mode=isolated_write_validation", completed.stdout)
        self.assertIn("input_error_cases=1", completed.stdout)
        assert_safe_cli_output(self, completed)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "learner_state.frozen_policy_generation_artifact_body_isolated_write_validation",
            *args,
        ],
        check=False,
        cwd=Path.cwd(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def assert_safe_cli_output(
    test_case: unittest.TestCase,
    completed: subprocess.CompletedProcess[str],
) -> None:
    assert_safe_output(test_case, completed.stdout + completed.stderr)


def assert_safe_output(test_case: unittest.TestCase, output: str) -> None:
    assert_no_forbidden_fragments(
        test_case,
        output,
        [
            '"artifact_body_request":',
            '"artifact_writer_result_pointer":',
            '"isolated_write_request":',
            '"expected_isolated_write_result":',
            '"case_metadata":',
            '"artifact_body_payload":',
            '"generated_policy_body":',
            '"manifest_body":',
            '"raw_rows":',
            '"logits":',
            '"probabilities":',
            '"private_path":',
            '"raw_learner_text":',
            "artifact_body_payload_json",
            "raw_rows_payload",
            "logits_dump_payload",
            "raw_learner_text_payload",
            "/Users/",
            "/home/",
            "/private/",
            "/var/folders/",
            "real_data/",
            "participant_data/",
        ],
        normalize_paths=True,
    )


if __name__ == "__main__":
    unittest.main()
