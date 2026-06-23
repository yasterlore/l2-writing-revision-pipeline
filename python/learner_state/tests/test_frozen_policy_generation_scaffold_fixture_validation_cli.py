from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path("tests/fixtures/learner_state_frozen_policy_generation_scaffold")
VALID_CASE = FIXTURE_ROOT / "valid" / "minimal_fixed_threshold_dry_run"
INVALID_TEMPERATURE_CASE = FIXTURE_ROOT / "invalid" / "test_temperature_tuning"


class FrozenPolicyGenerationScaffoldFixtureValidationCliTests(unittest.TestCase):
    def test_help_exits_zero(self) -> None:
        completed = run_cli("--help")

        self.assertEqual(completed.returncode, 0)
        self.assertIn("--fixture-root", completed.stdout)
        self.assertIn("--fixture-case", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_root_mode_exits_zero_and_reports_all_matches(self) -> None:
        completed = run_cli("--fixture-root", str(FIXTURE_ROOT))

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=fixture_root", completed.stdout)
        self.assertIn("total_cases=11", completed.stdout)
        self.assertIn("matched_cases=11", completed.stdout)
        self.assertIn("mismatched_cases=0", completed.stdout)
        self.assertIn("input_error_cases=0", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_root_mode_json_is_parseable_and_safe(self) -> None:
        completed = run_cli("--fixture-root", str(FIXTURE_ROOT), "--json")

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "fixture_root")
        self.assertEqual(payload["total_cases"], 11)
        self.assertEqual(payload["matched_cases"], 11)
        self.assertEqual(payload["mismatched_cases"], 0)
        self.assertEqual(payload["input_error_cases"], 0)
        self.assertTrue(payload["content_suppressed"])
        self.assertTrue(payload["no_raw_rows"])
        self.assertTrue(payload["synthetic_only_checked"])
        self.assertTrue(payload["no_oracle_checked"])
        assert_safe_cli_output(self, completed)

    def test_valid_case_exits_zero(self) -> None:
        completed = run_cli("--fixture-case", str(VALID_CASE))

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=fixture_case", completed.stdout)
        self.assertIn("fixture_case_label=valid/minimal_fixed_threshold_dry_run", completed.stdout)
        self.assertIn("scaffold_status=pass", completed.stdout)
        self.assertIn("expected_result_matched=true", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_invalid_case_expected_fail_exits_zero(self) -> None:
        completed = run_cli("--fixture-case", str(INVALID_TEMPERATURE_CASE))

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=fixture_case", completed.stdout)
        self.assertIn("scaffold_status=fail", completed.stdout)
        self.assertIn("reason_codes=test_temperature_tuning", completed.stdout)
        self.assertIn("expected_result_matched=true", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_missing_root_exits_two(self) -> None:
        completed = run_cli(
            "--fixture-root",
            "tests/fixtures/learner_state_frozen_policy_generation_scaffold_missing",
        )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("input_error_cases=1", completed.stdout)
        self.assertIn("reason_code_counts", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_no_args_exits_two(self) -> None:
        completed = run_cli()

        self.assertEqual(completed.returncode, 2)
        assert_safe_cli_output(self, completed)

    def test_both_fixture_args_exit_two(self) -> None:
        completed = run_cli(
            "--fixture-root",
            str(FIXTURE_ROOT),
            "--fixture-case",
            str(VALID_CASE),
        )

        self.assertEqual(completed.returncode, 2)
        assert_safe_cli_output(self, completed)

    def test_temp_expected_mismatch_exits_three(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_case = Path(tmpdir) / "valid" / "minimal_fixed_threshold_dry_run"
            shutil.copytree(VALID_CASE, tmp_case)
            expected_path = tmp_case / "expected_scaffold_result.json"
            expected = json.loads(expected_path.read_text(encoding="utf-8"))
            expected["input_validation_status"] = "expected_mismatch_marker"
            expected_path.write_text(
                json.dumps(expected, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            completed = run_cli("--fixture-case", str(tmp_case), "--json")

        self.assertEqual(completed.returncode, 3)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "fixture_case")
        self.assertFalse(payload["expected_result_matched"])
        self.assertEqual(payload["mismatch_count"], 1)
        self.assertEqual(payload["mismatch_fields"], ["input_validation_status"])
        assert_safe_cli_output(self, completed)

    def test_malformed_temp_fixture_returns_input_error_without_panic(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_case = Path(tmpdir) / "minimal_fixed_threshold_dry_run"
            shutil.copytree(VALID_CASE, tmp_case)
            (tmp_case / "generation_request.json").write_text("{", encoding="utf-8")

            completed = run_cli("--fixture-case", str(tmp_case))

        self.assertEqual(completed.returncode, 2)
        self.assertIn("scaffold_status=input_error", completed.stdout)
        self.assertIn("reason_codes=malformed_fixture_file", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_output_ordering_is_deterministic(self) -> None:
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
            "learner_state.frozen_policy_generation_scaffold_fixture_validation",
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
        '"/Users/',
        '"/home/',
        '"/private/',
        '"real_data/',
        '"private_data/',
        '"participant_data/',
        '"manual_outputs/',
    ]
    assert_no_forbidden_fragments(
        test_case,
        output,
        forbidden_fragments,
        normalize_paths=True,
    )


if __name__ == "__main__":
    unittest.main()
