from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path(
    "tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold"
)
VALID_CASE = FIXTURE_ROOT / "valid" / "minimal_metadata_only_generation_plan"
INVALID_TEMPERATURE_CASE = FIXTURE_ROOT / "invalid" / "test_temperature_tuning"


class FrozenPolicyGenerationGeneratorScaffoldFixtureValidationCliTests(
    unittest.TestCase
):
    def test_help_exits_zero(self) -> None:
        completed = run_cli("--help")

        self.assertEqual(completed.returncode, 0)
        self.assertIn("--fixture-root", completed.stdout)
        self.assertIn("--fixture-case", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_no_args_exits_two(self) -> None:
        completed = run_cli()

        self.assertEqual(completed.returncode, 2)
        assert_safe_cli_output(self, completed)

    def test_both_root_and_case_exit_two(self) -> None:
        completed = run_cli(
            "--fixture-root",
            str(FIXTURE_ROOT),
            "--fixture-case",
            str(VALID_CASE),
        )

        self.assertEqual(completed.returncode, 2)
        assert_safe_cli_output(self, completed)

    def test_root_human_exits_zero(self) -> None:
        completed = run_cli("--fixture-root", str(FIXTURE_ROOT))

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=fixture_root", completed.stdout)
        self.assertIn("total_cases=18", completed.stdout)
        self.assertIn("matched_cases=18", completed.stdout)
        self.assertIn("mismatched_cases=0", completed.stdout)
        self.assertIn("input_error_cases=0", completed.stdout)
        self.assertIn("content_suppressed=true", completed.stdout)
        self.assertIn("no_raw_rows=true", completed.stdout)
        self.assertIn("no_logits_dump=true", completed.stdout)
        self.assertIn("no_private_paths=true", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_root_json_exits_zero_and_is_parseable(self) -> None:
        completed = run_cli("--fixture-root", str(FIXTURE_ROOT), "--json")

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "fixture_root")
        self.assertEqual(payload["total_cases"], 18)
        self.assertEqual(payload["matched_cases"], 18)
        self.assertEqual(payload["mismatched_cases"], 0)
        self.assertEqual(payload["input_error_cases"], 0)
        self.assertTrue(payload["content_suppressed"])
        self.assertTrue(payload["no_raw_rows"])
        self.assertTrue(payload["no_logits_dump"])
        self.assertTrue(payload["no_private_paths"])
        assert_safe_cli_output(self, completed)

    def test_valid_case_human_exits_zero(self) -> None:
        completed = run_cli("--fixture-case", str(VALID_CASE))

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=fixture_case", completed.stdout)
        self.assertIn("case_label=valid/minimal_metadata_only_generation_plan", completed.stdout)
        self.assertIn("generation_status=pass", completed.stdout)
        self.assertIn("expected_status=pass", completed.stdout)
        self.assertIn("matched=true", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_invalid_case_human_exits_zero_with_expected_reason(self) -> None:
        completed = run_cli("--fixture-case", str(INVALID_TEMPERATURE_CASE))

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=fixture_case", completed.stdout)
        self.assertIn("generation_status=fail", completed.stdout)
        self.assertIn("expected_status=fail", completed.stdout)
        self.assertIn("reason_codes=test_temperature_tuning", completed.stdout)
        self.assertIn("matched=true", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_case_json_exits_zero_and_is_parseable(self) -> None:
        completed = run_cli("--fixture-case", str(VALID_CASE), "--json")

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "fixture_case")
        self.assertEqual(
            payload["case_label"],
            "valid/minimal_metadata_only_generation_plan",
        )
        self.assertEqual(payload["generation_status"], "pass")
        self.assertTrue(payload["matched"])
        self.assertEqual(payload["reason_codes"], [])
        assert_safe_cli_output(self, completed)

    def test_missing_root_path_exits_two(self) -> None:
        completed = run_cli(
            "--fixture-root",
            "tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold_missing",
        )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("mode=fixture_root", completed.stdout)
        self.assertIn("input_error_cases=1", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_malformed_temp_case_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "malformed_case"
            shutil.copytree(VALID_CASE, tmp_case)
            (tmp_case / "generation_request.json").write_text("{", encoding="utf-8")

            completed = run_cli("--fixture-case", str(tmp_case))

        self.assertEqual(completed.returncode, 2)
        self.assertIn("generation_status=input_error", completed.stdout)
        self.assertIn("reason_codes=malformed_fixture_file", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_forced_mismatch_temp_case_exits_three(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "invalid" / "test_temperature_tuning"
            shutil.copytree(INVALID_TEMPERATURE_CASE, tmp_case)
            expected_path = tmp_case / "expected_generator_scaffold_result.json"
            expected = json.loads(expected_path.read_text(encoding="utf-8"))
            expected["failed_checks"] = ["safe_mismatch_marker"]
            expected_path.write_text(
                json.dumps(expected, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            completed = run_cli("--fixture-case", str(tmp_case), "--json")

        self.assertEqual(completed.returncode, 3)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "fixture_case")
        self.assertFalse(payload["matched"])
        self.assertFalse(payload["expected_result_matched"])
        self.assertEqual(payload["mismatch_count"], 1)
        self.assertEqual(payload["mismatch_fields"], ["failed_checks"])
        assert_safe_cli_output(self, completed)

    def test_output_is_deterministic(self) -> None:
        first = run_cli("--fixture-root", str(FIXTURE_ROOT))
        second = run_cli("--fixture-root", str(FIXTURE_ROOT))

        self.assertEqual(first.returncode, 0)
        self.assertEqual(second.returncode, 0)
        self.assertEqual(first.stdout, second.stdout)
        assert_safe_cli_output(self, first)
        assert_safe_cli_output(self, second)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "learner_state.frozen_policy_generation_generator_scaffold_fixture_validation",
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
        normalize_paths=True,
    )


if __name__ == "__main__":
    unittest.main()
