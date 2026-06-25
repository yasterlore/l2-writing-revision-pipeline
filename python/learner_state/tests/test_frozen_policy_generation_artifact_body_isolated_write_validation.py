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
    validate_isolated_write_fixture_case,
    validate_isolated_write_fixture_root,
)

FIXTURE_ROOT = DEFAULT_FIXTURE_ROOT
VALID_PASS_WRITTEN = "valid/safe_metadata_flat_relative_output"
VALID_USAGE_ERROR = "valid/safe_metadata_existing_output_rejected_after_precreate"
INVALID_FAIL_CLOSED = "invalid/generation_fail_closed_no_file"


class FrozenPolicyGenerationArtifactBodyIsolatedWriteValidationTests(
    unittest.TestCase
):
    def test_root_validates_expected_counts(self) -> None:
        summary = validate_isolated_write_fixture_root(FIXTURE_ROOT)

        self.assertEqual(summary.total_cases, 22)
        self.assertEqual(summary.valid_cases, 5)
        self.assertEqual(summary.invalid_cases, 17)
        self.assertEqual(summary.pass_written_cases, 3)
        self.assertEqual(summary.pass_no_write_cases, 1)
        self.assertEqual(summary.usage_error_cases, 14)
        self.assertEqual(summary.fail_closed_cases, 4)
        self.assertEqual(summary.matched_cases, 22)
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
        self.assertFalse(summary.release_quality_ready)

    def test_single_pass_written_case_matches(self) -> None:
        result = validate_isolated_write_fixture_case(
            FIXTURE_ROOT / VALID_PASS_WRITTEN,
            expected_kind="valid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(result.actual_category, "pass_written")
        self.assertEqual(result.actual_status, "pass")
        self.assertEqual(result.actual_exit_code, 0)
        self.assertTrue(result.actual_file_written)
        self.assertTrue(result.file_parse_ok)
        self.assertTrue(result.file_allowed_keys_only)
        self.assertEqual(result.residue_file_count, 0)

    def test_single_usage_error_no_write_case_matches(self) -> None:
        result = validate_isolated_write_fixture_case(
            FIXTURE_ROOT / VALID_USAGE_ERROR,
            expected_kind="valid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(result.actual_category, "usage_error_no_write")
        self.assertEqual(result.actual_status, "usage_error")
        self.assertFalse(result.actual_file_written)
        self.assertIn("artifact_body_output_path_exists", result.reason_codes)

    def test_single_fail_closed_no_write_case_matches(self) -> None:
        result = validate_isolated_write_fixture_case(
            FIXTURE_ROOT / INVALID_FAIL_CLOSED,
            expected_kind="invalid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(result.actual_category, "fail_closed_no_write")
        self.assertEqual(result.actual_status, "fail_closed")
        self.assertFalse(result.actual_file_written)
        self.assertIn("unknown_artifact_body_schema_version", result.reason_codes)

    def test_malformed_fixture_root_reports_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir) / "isolated_write"
            shutil.copytree(FIXTURE_ROOT, tmp_root)
            malformed = (
                tmp_root
                / "valid"
                / "safe_metadata_flat_relative_output"
                / "case_metadata.json"
            )
            malformed.write_text("{", encoding="utf-8")
            summary = validate_isolated_write_fixture_root(tmp_root)

        self.assertEqual(summary.input_error_cases, 1)
        self.assertEqual(summary.matched_cases, 21)
        self.assertEqual(summary.mismatched_cases, 0)

    def test_missing_required_file_reports_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "safe_metadata_flat_relative_output"
            shutil.copytree(FIXTURE_ROOT / VALID_PASS_WRITTEN, tmp_case)
            (tmp_case / "isolated_write_request.json").unlink()
            result = validate_isolated_write_fixture_case(
                tmp_case,
                expected_kind="valid",
            )

        self.assertTrue(result.is_input_error)
        self.assertIn("required_file_missing", result.reason_codes)

    def test_case_id_mismatch_reports_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "safe_metadata_flat_relative_output"
            shutil.copytree(FIXTURE_ROOT / VALID_PASS_WRITTEN, tmp_case)
            metadata_path = tmp_case / "case_metadata.json"
            payload = json.loads(metadata_path.read_text(encoding="utf-8"))
            payload["case_id"] = "valid/wrong_case_id"
            metadata_path.write_text(
                json.dumps(payload, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            result = validate_isolated_write_fixture_case(
                tmp_case,
                expected_kind="valid",
            )

        self.assertTrue(result.is_input_error)
        self.assertIn("case_id_mismatch", result.reason_codes)

    def test_cli_default_root_human_output_is_body_free(self) -> None:
        completed = run_cli()

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=isolated_write_validation", completed.stdout)
        self.assertIn("total_cases=22", completed.stdout)
        self.assertIn("matched_cases=22", completed.stdout)
        self.assertIn("residue_file_count=0", completed.stdout)
        assert_body_free_output(self, completed.stdout + completed.stderr)

    def test_cli_default_root_json_output_is_parseable_and_body_free(self) -> None:
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
        self.assertEqual(payload["residue_file_count"], 0)
        self.assertFalse(payload["body_payload_printed"])
        self.assertNotIn("case_results", payload)
        assert_body_free_output(self, completed.stdout + completed.stderr)

    def test_cli_single_valid_case_exits_zero(self) -> None:
        completed = run_cli("--fixture-case", VALID_PASS_WRITTEN)

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=isolated_write_fixture_case", completed.stdout)
        self.assertIn(f"case_id={VALID_PASS_WRITTEN}", completed.stdout)
        self.assertIn("actual_category=pass_written", completed.stdout)
        self.assertIn("matched=true", completed.stdout)
        assert_body_free_output(self, completed.stdout + completed.stderr)

    def test_cli_single_invalid_expected_failure_exits_zero(self) -> None:
        completed = run_cli("--fixture-case", INVALID_FAIL_CLOSED)

        self.assertEqual(completed.returncode, 0)
        self.assertIn(f"case_id={INVALID_FAIL_CLOSED}", completed.stdout)
        self.assertIn("actual_category=fail_closed_no_write", completed.stdout)
        self.assertIn("matched=true", completed.stdout)
        assert_body_free_output(self, completed.stdout + completed.stderr)

    def test_cli_rejects_unsafe_fixture_selector(self) -> None:
        completed = run_cli("--fixture-case", "../escape")

        self.assertEqual(completed.returncode, 2)
        self.assertIn(
            "reason_codes=unsafe_parent_traversal_fixture_case_selector",
            completed.stdout,
        )
        assert_body_free_output(self, completed.stdout + completed.stderr)

    def test_cli_missing_fixture_root_exits_four(self) -> None:
        completed = run_cli("--fixture-root", "tests/fixtures/missing_isolated_write_root")

        self.assertEqual(completed.returncode, 4)
        self.assertIn("input_error_cases=1", completed.stdout)
        self.assertIn("reason_code_counts={\"missing_root\":1}", completed.stdout)
        assert_body_free_output(self, completed.stdout + completed.stderr)

    def test_cli_help_exits_zero(self) -> None:
        completed = run_cli("--help")

        self.assertEqual(completed.returncode, 0)
        self.assertIn("--fixture-root", completed.stdout)
        self.assertIn("--fixture-case", completed.stdout)
        self.assertIn("--json", completed.stdout)
        assert_body_free_output(self, completed.stdout + completed.stderr)

    def test_no_absolute_temp_path_or_private_path_in_summary(self) -> None:
        completed = run_cli("--fixture-case", VALID_PASS_WRITTEN)

        self.assertEqual(completed.returncode, 0)
        self.assertNotIn("/Users/", completed.stdout + completed.stderr)
        self.assertNotIn("/private/", completed.stdout + completed.stderr)
        self.assertNotIn("/var/folders/", completed.stdout + completed.stderr)

    def test_written_file_cleanup_leaves_no_residue(self) -> None:
        result = validate_isolated_write_fixture_case(
            FIXTURE_ROOT / VALID_PASS_WRITTEN,
            expected_kind="valid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(result.residue_file_count, 0)
        self.assertTrue(result.file_cleanup_ok)

    def test_root_reason_code_counts_include_expected_reasons(self) -> None:
        summary = validate_isolated_write_fixture_root(FIXTURE_ROOT)

        self.assertEqual(
            summary.reason_code_counts["artifact_body_output_requires_safe_metadata_mode"],
            2,
        )
        self.assertEqual(summary.reason_code_counts["artifact_body_output_path_exists"], 2)
        self.assertEqual(summary.reason_code_counts["unsafe_absolute_output_path"], 2)
        self.assertEqual(summary.reason_code_counts["manifest_write_attempt_not_supported"], 1)
        self.assertEqual(
            summary.reason_code_counts["generated_policy_body_write_attempt_not_supported"],
            1,
        )

    def test_stdout_body_free_scan_detects_forbidden_marker(self) -> None:
        from learner_state.frozen_policy_generation_artifact_body_isolated_write_validation import (
            _output_body_free,
        )

        self.assertFalse(_output_body_free('"artifact_body_payload":{}'))
        self.assertTrue(_output_body_free("mode=isolated_write_validation"))

    def test_written_file_allowed_key_scan_detects_forbidden_key(self) -> None:
        from learner_state.frozen_policy_generation_artifact_body_isolated_write_validation import (
            _validate_written_file,
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "body.json"
            path.write_text(
                json.dumps(
                    {
                        "artifact_body_schema_version": (
                            "learner_state_frozen_policy_generation_artifact_body_v0.1"
                        ),
                        "artifact_body_id": "synthetic_body",
                        "artifact_id": "synthetic_artifact",
                        "manifest_id": "synthetic_manifest",
                        "writer_version": "synthetic_writer",
                        "body_status": "generated_safe_metadata_body",
                        "synthetic_only_notice": "synthetic-only metadata summary",
                        "no_oracle_notice": "no-oracle metadata summary",
                        "non_proof_notice": "not proof",
                        "safety_summary": {},
                        "count_summary": {
                            "raw_row_count": 0,
                            "logits_dump_count": 0,
                            "private_path_count": 0,
                            "performance_metric_count": 0,
                            "request_body_count": 0,
                            "pointer_body_count": 0,
                            "expected_body_count": 0,
                            "manifest_body_count": 0,
                        },
                        "raw_rows": [],
                    }
                ),
                encoding="utf-8",
            )
            parse_ok, allowed, reasons, _checks = _validate_written_file(path)

        self.assertTrue(parse_ok)
        self.assertFalse(allowed)
        self.assertIn("written_file_forbidden_key", reasons)


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


def assert_body_free_output(test_case: unittest.TestCase, output: str) -> None:
    forbidden = [
        '"artifact_body_payload":',
        '"artifact_body_request":',
        '"artifact_writer_result_pointer":',
        '"isolated_write_request":',
        '"expected_isolated_write_result":',
        '"case_metadata":',
        '"request_body":',
        '"pointer_body":',
        '"expected_body":',
        '"generated_policy_body":',
        '"manifest_body":',
        '"raw_rows":',
        '"logits":',
        '"probabilities":',
        '"raw_learner_text":',
        "/Users/",
        "/private/",
        "/var/folders/",
        "real_data/",
        "participant_data/",
    ]
    for fragment in forbidden:
        test_case.assertNotIn(fragment, output)


if __name__ == "__main__":
    unittest.main()
