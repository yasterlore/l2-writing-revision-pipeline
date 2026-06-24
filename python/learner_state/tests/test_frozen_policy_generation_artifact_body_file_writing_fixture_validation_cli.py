from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_artifact_body_file_writing_fixture_validation import (
    DEFAULT_FIXTURE_ROOT,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = DEFAULT_FIXTURE_ROOT
VALID_CASE_LABEL = "valid/valid_safe_metadata_relative_tmp_output"
INVALID_CASE_LABEL = "invalid/invalid_suppressed_mode_with_output_path"


class FrozenPolicyGenerationArtifactBodyFileWritingFixtureValidationCliTests(
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
        self.assertIn("mode=fixture_root", completed.stdout)
        self.assertIn("total_cases=29", completed.stdout)
        self.assertIn("valid_cases=5", completed.stdout)
        self.assertIn("invalid_cases=24", completed.stdout)
        self.assertIn("matched_cases=29", completed.stdout)
        self.assertIn("input_error_cases=0", completed.stdout)
        self.assertIn("file_writing_isolated=false", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_default_root_json_output_exits_zero_and_is_body_free(self) -> None:
        completed = run_cli("--json")

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "fixture_root")
        self.assertEqual(payload["total_cases"], 29)
        self.assertEqual(payload["valid_cases"], 5)
        self.assertEqual(payload["invalid_cases"], 24)
        self.assertEqual(payload["matched_cases"], 29)
        self.assertEqual(payload["mismatched_cases"], 0)
        self.assertEqual(payload["input_error_cases"], 0)
        self.assertTrue(payload["content_suppressed"])
        self.assertTrue(payload["no_raw_rows"])
        self.assertTrue(payload["no_logits_dump"])
        self.assertTrue(payload["no_private_paths"])
        self.assertFalse(payload["file_writing_isolated"])
        self.assertNotIn("artifact_body_request", payload)
        self.assertNotIn("file_write_request", payload)
        assert_safe_cli_output(self, completed)

    def test_single_valid_case_exits_zero(self) -> None:
        completed = run_cli("--fixture-case", VALID_CASE_LABEL)

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=fixture_case", completed.stdout)
        self.assertIn(f"case_id={VALID_CASE_LABEL}", completed.stdout)
        self.assertIn("expected_kind=valid", completed.stdout)
        self.assertIn("expected_status=pass", completed.stdout)
        self.assertIn("actual_status=pass", completed.stdout)
        self.assertIn("matched=true", completed.stdout)
        self.assertIn("reason_codes=none", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_single_invalid_expected_failure_exits_zero(self) -> None:
        completed = run_cli("--fixture-case", INVALID_CASE_LABEL)

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=fixture_case", completed.stdout)
        self.assertIn(f"case_id={INVALID_CASE_LABEL}", completed.stdout)
        self.assertIn("expected_kind=invalid", completed.stdout)
        self.assertIn("expected_status=fail_closed", completed.stdout)
        self.assertIn("actual_status=fail_closed", completed.stdout)
        self.assertIn("matched=true", completed.stdout)
        self.assertIn("reason_codes=suppressed_mode_with_output_path", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_single_case_json_output_is_parseable_and_body_free(self) -> None:
        completed = run_cli("--fixture-case", VALID_CASE_LABEL, "--json")

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "fixture_case")
        self.assertEqual(payload["case_id"], VALID_CASE_LABEL)
        self.assertEqual(payload["expected_kind"], "valid")
        self.assertEqual(payload["actual_status"], "pass")
        self.assertTrue(payload["matched"])
        self.assertEqual(payload["reason_codes"], [])
        self.assertNotIn("artifact_body_request", payload)
        self.assertNotIn("file_write_request", payload)
        assert_safe_cli_output(self, completed)

    def test_unsafe_absolute_fixture_case_selector_exits_two(self) -> None:
        completed = run_cli("--fixture-case", "/not_allowed")

        self.assertEqual(completed.returncode, 2)
        self.assertIn("mode=fixture_case", completed.stdout)
        self.assertIn(
            "reason_codes=unsafe_absolute_fixture_case_selector",
            completed.stdout,
        )
        self.assertNotIn("/not_allowed", completed.stdout + completed.stderr)
        assert_safe_cli_output(self, completed)

    def test_parent_traversal_fixture_case_selector_exits_two(self) -> None:
        completed = run_cli("--fixture-case", "../valid/escape")

        self.assertEqual(completed.returncode, 2)
        self.assertIn("mode=fixture_case", completed.stdout)
        self.assertIn(
            "reason_codes=unsafe_parent_traversal_fixture_case_selector",
            completed.stdout,
        )
        self.assertNotIn("../valid/escape", completed.stdout + completed.stderr)
        assert_safe_cli_output(self, completed)

    def test_empty_fixture_case_selector_exits_two(self) -> None:
        completed = run_cli("--fixture-case", "")

        self.assertEqual(completed.returncode, 2)
        self.assertIn("reason_codes=empty_fixture_case_selector", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_missing_fixture_case_exits_four_with_safe_summary(self) -> None:
        completed = run_cli("--fixture-case", "valid/missing_case")

        self.assertEqual(completed.returncode, 4)
        self.assertIn("mode=fixture_case", completed.stdout)
        self.assertIn("case_id=valid/missing_case", completed.stdout)
        self.assertIn("reason_codes=missing_fixture_case", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_malformed_temp_fixture_root_exits_four(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir) / "file_writing"
            shutil.copytree(FIXTURE_ROOT, tmp_root)
            malformed_path = (
                tmp_root
                / "valid"
                / "valid_safe_metadata_relative_tmp_output"
                / "artifact_body_request.json"
            )
            malformed_path.write_text("{", encoding="utf-8")
            completed = run_cli("--fixture-root", str(tmp_root))

        self.assertEqual(completed.returncode, 4)
        self.assertIn("mode=fixture_root", completed.stdout)
        self.assertIn("input_error_cases=1", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_validator_cli_does_not_write_files(self) -> None:
        before = sorted(path.relative_to(FIXTURE_ROOT) for path in FIXTURE_ROOT.rglob("*"))

        completed = run_cli()

        after = sorted(path.relative_to(FIXTURE_ROOT) for path in FIXTURE_ROOT.rglob("*"))
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(after, before)
        assert_safe_cli_output(self, completed)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "learner_state.frozen_policy_generation_artifact_body_file_writing_fixture_validation",
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
    output = completed.stdout + completed.stderr
    assert_no_forbidden_fragments(
        test_case,
        output,
        [
            '"artifact_body_request":',
            '"artifact_writer_result_pointer":',
            '"file_write_request":',
            '"expected_file_write_result":',
            '"request_body":',
            '"pointer_body":',
            '"expected_body":',
            '"artifact_body_payload":',
            '"generated_policy_body":',
            '"manifest_body":',
            '"raw_rows":',
            '"logits":',
            '"probabilities":',
            '"private_path":',
            '"raw_learner_text":',
            '"performance_metrics":',
            "/Users/",
            "/home/",
            "/private/",
            "/var/folders/",
            "real_data/",
            "participant_data/",
            "manual_outputs/",
        ],
        normalize_paths=True,
    )


if __name__ == "__main__":
    unittest.main()
