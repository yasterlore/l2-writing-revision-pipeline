from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from learner_state import (
    frozen_policy_generation_artifact_body_fixture_validation as validator_module,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path(
    "tests/fixtures/learner_state_frozen_policy_generation_artifact_body"
)
VALID_CASE_LABEL = "valid/minimal_suppressed_metadata_only_body"
INVALID_CASE_LABEL = "invalid/raw_rows_in_artifact_body"


class FrozenPolicyGenerationArtifactBodyFixtureValidationCliTests(unittest.TestCase):
    def test_help_exits_zero(self) -> None:
        completed = run_cli("--help")

        self.assertEqual(completed.returncode, 0)
        self.assertIn("--fixture-root", completed.stdout)
        self.assertIn("--fixture-case", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_no_args_uses_default_fixture_root_and_exits_zero(self) -> None:
        completed = run_cli()

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=fixture_root", completed.stdout)
        self.assertIn("total_cases=18", completed.stdout)
        self.assertIn("matched_cases=18", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_root_human_output_exits_zero(self) -> None:
        completed = run_cli("--fixture-root", str(FIXTURE_ROOT))

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=fixture_root", completed.stdout)
        self.assertIn("total_cases=18", completed.stdout)
        self.assertIn("valid_cases=4", completed.stdout)
        self.assertIn("invalid_cases=14", completed.stdout)
        self.assertIn("matched_cases=18", completed.stdout)
        self.assertIn("mismatched_cases=0", completed.stdout)
        self.assertIn("input_error_cases=0", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_root_json_output_exits_zero_and_is_parseable(self) -> None:
        completed = run_cli("--fixture-root", str(FIXTURE_ROOT), "--json")

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "fixture_root")
        self.assertEqual(payload["total_cases"], 18)
        self.assertEqual(payload["valid_cases"], 4)
        self.assertEqual(payload["invalid_cases"], 14)
        self.assertEqual(payload["matched_cases"], 18)
        self.assertEqual(payload["mismatched_cases"], 0)
        self.assertEqual(payload["input_error_cases"], 0)
        self.assertTrue(payload["content_suppressed"])
        self.assertTrue(payload["no_raw_rows"])
        self.assertTrue(payload["no_logits_dump"])
        self.assertTrue(payload["no_private_paths"])
        assert_safe_cli_output(self, completed)

    def test_root_json_output_is_deterministic(self) -> None:
        first = run_cli("--fixture-root", str(FIXTURE_ROOT), "--json")
        second = run_cli("--fixture-root", str(FIXTURE_ROOT), "--json")

        self.assertEqual(first.returncode, 0)
        self.assertEqual(second.returncode, 0)
        self.assertEqual(first.stdout, second.stdout)
        assert_safe_cli_output(self, first)
        assert_safe_cli_output(self, second)

    def test_single_valid_case_human_and_json_exit_zero(self) -> None:
        human = run_cli("--fixture-case", VALID_CASE_LABEL)
        as_json = run_cli("--fixture-case", VALID_CASE_LABEL, "--json")

        self.assertEqual(human.returncode, 0)
        self.assertIn("mode=fixture_case", human.stdout)
        self.assertIn(f"case_id={VALID_CASE_LABEL}", human.stdout)
        self.assertIn("category=valid", human.stdout)
        self.assertIn("validation_status=pass", human.stdout)
        self.assertIn("matched=true", human.stdout)

        self.assertEqual(as_json.returncode, 0)
        payload = json.loads(as_json.stdout)
        self.assertEqual(payload["mode"], "fixture_case")
        self.assertEqual(payload["case_id"], VALID_CASE_LABEL)
        self.assertEqual(payload["category"], "valid")
        self.assertEqual(payload["validation_status"], "pass")
        self.assertTrue(payload["matched"])
        self.assertEqual(payload["reason_codes"], [])
        self.assertNotIn("safe_marker_flags", payload)
        assert_safe_cli_output(self, human)
        assert_safe_cli_output(self, as_json)

    def test_single_invalid_expected_fail_closed_case_human_and_json_exit_zero(
        self,
    ) -> None:
        human = run_cli("--fixture-case", INVALID_CASE_LABEL)
        as_json = run_cli("--fixture-case", INVALID_CASE_LABEL, "--json")

        self.assertEqual(human.returncode, 0)
        self.assertIn("mode=fixture_case", human.stdout)
        self.assertIn(f"case_id={INVALID_CASE_LABEL}", human.stdout)
        self.assertIn("category=invalid", human.stdout)
        self.assertIn("validation_status=fail", human.stdout)
        self.assertIn("body_status=fail_closed", human.stdout)
        self.assertIn("reason_codes=raw_rows_in_artifact_body", human.stdout)
        self.assertIn("matched=true", human.stdout)

        self.assertEqual(as_json.returncode, 0)
        payload = json.loads(as_json.stdout)
        self.assertEqual(payload["mode"], "fixture_case")
        self.assertEqual(payload["case_id"], INVALID_CASE_LABEL)
        self.assertEqual(payload["category"], "invalid")
        self.assertEqual(payload["validation_status"], "fail")
        self.assertEqual(payload["body_status"], "fail_closed")
        self.assertTrue(payload["matched"])
        self.assertEqual(payload["reason_codes"], ["raw_rows_in_artifact_body"])
        self.assertNotIn("safe_marker_flags", payload)
        assert_safe_cli_output(self, human)
        assert_safe_cli_output(self, as_json)

    def test_missing_fixture_root_exits_two(self) -> None:
        completed = run_cli("--fixture-root", "missing_artifact_body_fixture_root")

        self.assertEqual(completed.returncode, 2)
        self.assertIn("mode=fixture_root", completed.stdout)
        self.assertIn("input_error_cases=1", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_missing_case_exits_two(self) -> None:
        completed = run_cli("--fixture-case", "valid/missing_case")

        self.assertEqual(completed.returncode, 2)
        self.assertIn("mode=fixture_case", completed.stdout)
        self.assertIn("validation_status=input_error", completed.stdout)
        self.assertIn("reason_codes=missing_fixture_case", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_unknown_option_exits_two(self) -> None:
        completed = run_cli("--unknown-option")

        self.assertEqual(completed.returncode, 2)
        assert_safe_cli_output(self, completed)

    def test_mutually_exclusive_root_and_case_exits_two(self) -> None:
        completed = run_cli(
            "--fixture-root",
            str(FIXTURE_ROOT),
            "--fixture-case",
            VALID_CASE_LABEL,
        )

        self.assertEqual(completed.returncode, 2)
        assert_safe_cli_output(self, completed)

    def test_malformed_json_temp_root_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir) / "artifact_body"
            shutil.copytree(FIXTURE_ROOT, tmp_root)
            malformed_path = (
                tmp_root
                / "valid"
                / "minimal_suppressed_metadata_only_body"
                / "artifact_body_request.json"
            )
            malformed_path.write_text("{", encoding="utf-8")
            completed = run_cli("--fixture-root", str(tmp_root))

        self.assertEqual(completed.returncode, 2)
        self.assertIn("mode=fixture_root", completed.stdout)
        self.assertIn("input_error_cases=1", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_missing_required_file_temp_root_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_root = Path(tmp_dir) / "artifact_body"
            shutil.copytree(FIXTURE_ROOT, tmp_root)
            missing_path = (
                tmp_root
                / "valid"
                / "minimal_suppressed_metadata_only_body"
                / "artifact_body_request.json"
            )
            missing_path.unlink()
            completed = run_cli("--fixture-root", str(tmp_root))

        self.assertEqual(completed.returncode, 2)
        self.assertIn("mode=fixture_root", completed.stdout)
        self.assertIn("input_error_cases=1", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_cli_uses_existing_validator_api_for_root(self) -> None:
        with mock.patch.object(
            validator_module,
            "validate_artifact_body_fixture_root",
            wraps=validator_module.validate_artifact_body_fixture_root,
        ) as validate_root:
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                exit_code = validator_module.main(["--fixture-root", str(FIXTURE_ROOT)])

        self.assertEqual(exit_code, 0)
        self.assertTrue(validate_root.called)
        self.assertIn("mode=fixture_root", buffer.getvalue())


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "learner_state.frozen_policy_generation_artifact_body_fixture_validation",
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
            '"expected_artifact_body_result":',
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
