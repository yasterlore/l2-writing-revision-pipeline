"""CLI tests for the frozen policy generation scaffold runtime."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_support.safe_output_scan import assert_no_forbidden_fragments


FIXTURE_ROOT = Path("tests/fixtures/learner_state_frozen_policy_generation_scaffold")
VALID_CASE = FIXTURE_ROOT / "valid" / "minimal_fixed_threshold_dry_run"
INVALID_TEMPERATURE_CASE = FIXTURE_ROOT / "invalid" / "test_temperature_tuning"


class FrozenPolicyGenerationScaffoldRuntimeCliTests(unittest.TestCase):
    def test_help_exits_zero(self) -> None:
        completed = run_cli("--help")

        self.assertEqual(completed.returncode, 0)
        self.assertIn("--request", completed.stdout)
        self.assertIn("--pointer", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_no_args_exits_two(self) -> None:
        completed = run_cli()

        self.assertEqual(completed.returncode, 2)
        assert_safe_cli_output(self, completed)

    def test_request_only_exits_two(self) -> None:
        completed = run_cli("--request", str(VALID_CASE / "generation_request.json"))

        self.assertEqual(completed.returncode, 2)
        assert_safe_cli_output(self, completed)

    def test_pointer_only_exits_two(self) -> None:
        completed = run_cli(
            "--pointer",
            str(VALID_CASE / "input_fixture_pointer.json"),
        )

        self.assertEqual(completed.returncode, 2)
        assert_safe_cli_output(self, completed)

    def test_valid_request_pointer_human_output_exits_zero(self) -> None:
        completed = run_cli_for_case(VALID_CASE)

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=scaffold_runtime", completed.stdout)
        self.assertIn("scaffold_status=pass", completed.stdout)
        self.assertIn("reason_codes=none", completed.stdout)
        self.assertIn("content_suppressed=true", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_valid_request_pointer_json_output_is_parseable(self) -> None:
        completed = run_cli_for_case(VALID_CASE, "--json")

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "scaffold_runtime")
        self.assertEqual(payload["scaffold_status"], "pass")
        self.assertEqual(payload["reason_codes"], [])
        self.assertTrue(payload["content_suppressed"])
        self.assertFalse(payload["generated_artifact_written"])
        self.assertFalse(payload["generated_artifact_body_available"])
        assert_safe_cli_output(self, completed)

    def test_invalid_request_pointer_exits_zero_with_fail_reason(self) -> None:
        completed = run_cli_for_case(INVALID_TEMPERATURE_CASE)

        self.assertEqual(completed.returncode, 0)
        self.assertIn("scaffold_status=fail", completed.stdout)
        self.assertIn("reason_codes=test_temperature_tuning", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_malformed_request_exits_two_with_safe_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            request_path = Path(tmp_dir) / "generation_request.json"
            request_path.write_text("{", encoding="utf-8")
            completed = run_cli(
                "--request",
                str(request_path),
                "--pointer",
                str(VALID_CASE / "input_fixture_pointer.json"),
            )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("scaffold_status=input_error", completed.stdout)
        self.assertIn("reason_codes=malformed_request", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_malformed_pointer_exits_two_with_safe_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            pointer_path = Path(tmp_dir) / "input_fixture_pointer.json"
            pointer_path.write_text("{", encoding="utf-8")
            completed = run_cli(
                "--request",
                str(VALID_CASE / "generation_request.json"),
                "--pointer",
                str(pointer_path),
            )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("scaffold_status=input_error", completed.stdout)
        self.assertIn("reason_codes=malformed_pointer", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_missing_request_path_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            completed = run_cli(
                "--request",
                str(Path(tmp_dir) / "missing_generation_request.json"),
                "--pointer",
                str(VALID_CASE / "input_fixture_pointer.json"),
            )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("reason_codes=missing_request", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_missing_pointer_path_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            completed = run_cli(
                "--request",
                str(VALID_CASE / "generation_request.json"),
                "--pointer",
                str(Path(tmp_dir) / "missing_input_fixture_pointer.json"),
            )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("reason_codes=missing_pointer", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_unsafe_path_rejected_without_echo(self) -> None:
        completed = run_cli(
            "--request",
            "manual_outputs/synthetic_generation_request.json",
            "--pointer",
            str(VALID_CASE / "input_fixture_pointer.json"),
        )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("reason_codes=unsafe_path", completed.stdout)
        output = completed.stdout + completed.stderr
        self.assertNotIn("manual_outputs/synthetic_generation_request.json", output)
        assert_safe_cli_output(self, completed)

    def test_output_is_deterministic_for_same_valid_fixture(self) -> None:
        first = run_cli_for_case(VALID_CASE)
        second = run_cli_for_case(VALID_CASE)

        self.assertEqual(first.returncode, 0)
        self.assertEqual(second.returncode, 0)
        self.assertEqual(first.stdout, second.stdout)
        assert_safe_cli_output(self, first)
        assert_safe_cli_output(self, second)


def run_cli_for_case(case_dir: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    return run_cli(
        "--request",
        str(case_dir / "generation_request.json"),
        "--pointer",
        str(case_dir / "input_fixture_pointer.json"),
        *extra_args,
    )


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "learner_state.frozen_policy_generation",
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
    forbidden_fragments = [
        '"generation_request":',
        '"input_fixture_pointer":',
        '"expected_scaffold_result":',
        '"temperature_policy":',
        '"threshold_policy":',
        '"abstention_policy":',
        '"output_policy":',
        '"generated_artifact_body":',
        '"generated_frozen_policy_body":',
        '"frozen_policy_artifact_body":',
        '"policy_body":',
        '"raw_prediction_rows":',
        '"raw_label_rows":',
        '"prediction_rows":',
        '"label_rows":',
        '"logits":',
        '"probabilities":',
        '"probability_values":',
        '"label_body":',
        '"split_body":',
        '"calibration_policy_body":',
        '"expected_action_body":',
        '"final_text":',
        '"observed_after_text":',
        '"gold_label":',
        '"teacher_correction":',
        '"human_correction":',
        '"raw_learner_text":',
        '"performance_metric_body":',
        '"metric_results":',
        '"metrics":',
        "/Users/",
        "/home/",
        "/private/",
        "real_data/",
        "private_data/",
        "participant_data/",
        "manual_outputs/",
    ]
    assert_no_forbidden_fragments(
        test_case,
        output,
        forbidden_fragments,
        normalize_paths=True,
    )


if __name__ == "__main__":
    unittest.main()
