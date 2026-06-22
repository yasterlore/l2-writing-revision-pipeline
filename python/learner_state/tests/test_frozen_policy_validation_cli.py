from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path("tests/fixtures/learner_state_frozen_selective_prediction_policy")
VALID_CASE = FIXTURE_ROOT / "valid" / "minimal_validation_only_policy"
INVALID_TEMPERATURE_CASE = FIXTURE_ROOT / "invalid" / "test_derived_temperature"


class FrozenPolicyValidationCliTests(unittest.TestCase):
    def test_help_exits_zero(self) -> None:
        completed = run_cli("--help")

        self.assertEqual(completed.returncode, 0)
        self.assertIn("--fixture-case", completed.stdout)
        self.assertIn("--fixture-root", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_valid_single_case_exits_zero(self) -> None:
        completed = run_cli("--fixture-case", str(VALID_CASE))

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=fixture_case", completed.stdout)
        self.assertIn("validation_status=pass", completed.stdout)
        self.assertIn("expected_result_matched=true", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_invalid_single_case_exits_zero_when_expected_matches(self) -> None:
        completed = run_cli("--fixture-case", str(INVALID_TEMPERATURE_CASE))

        self.assertEqual(completed.returncode, 0)
        self.assertIn("validation_status=fail", completed.stdout)
        self.assertIn("reason_codes=test_temperature_tuning", completed.stdout)
        self.assertIn("expected_result_matched=true", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_fixture_root_exits_zero_and_reports_all_matches(self) -> None:
        completed = run_cli("--fixture-root", str(FIXTURE_ROOT))

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=fixture_root", completed.stdout)
        self.assertIn("total_cases=12", completed.stdout)
        self.assertIn("matched_cases=12", completed.stdout)
        self.assertIn("mismatched_cases=0", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_fixture_root_json_is_parseable_and_safe(self) -> None:
        completed = run_cli("--fixture-root", str(FIXTURE_ROOT), "--json")

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "fixture_root")
        self.assertEqual(payload["total_cases"], 12)
        self.assertEqual(payload["matched_cases"], 12)
        self.assertEqual(payload["mismatched_cases"], 0)
        self.assertTrue(payload["content_suppressed"])
        self.assertTrue(payload["no_raw_rows"])
        self.assertTrue(payload["test_tuning_checked"])
        self.assertTrue(payload["forbidden_field_scan_checked"])
        self.assertTrue(payload["private_path_scan_checked"])
        self.assertTrue(payload["performance_claim_scan_checked"])
        assert_safe_cli_output(self, completed)

    def test_missing_fixture_exits_two(self) -> None:
        completed = run_cli(
            "--fixture-case",
            "tests/fixtures/learner_state_frozen_selective_prediction_policy/missing_case",
        )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("validation_status=input_error", completed.stdout)
        self.assertIn("reason_codes=missing_input_file", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_mutually_exclusive_args_exit_two(self) -> None:
        completed = run_cli(
            "--fixture-case",
            str(VALID_CASE),
            "--fixture-root",
            str(FIXTURE_ROOT),
        )

        self.assertEqual(completed.returncode, 2)
        assert_safe_cli_output(self, completed)

    def test_no_args_exit_two(self) -> None:
        completed = run_cli()

        self.assertEqual(completed.returncode, 2)
        assert_safe_cli_output(self, completed)

    def test_expected_mismatch_exits_three_with_safe_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_case = Path(tmpdir) / "minimal_validation_only_policy"
            shutil.copytree(VALID_CASE, tmp_case)
            expected_path = tmp_case / "expected_frozen_policy_validation_result.json"
            expected = json.loads(expected_path.read_text(encoding="utf-8"))
            expected["validation_status"] = "fail"
            expected["expected_failure_reason"] = "synthetic_mismatch_marker"
            expected_path.write_text(
                json.dumps(expected, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            completed = run_cli("--fixture-case", str(tmp_case), "--json")

        self.assertEqual(completed.returncode, 3)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "fixture_case")
        self.assertFalse(payload["expected_result_matched"])
        self.assertIn("validation_status", payload["mismatch_fields"])
        assert_safe_cli_output(self, completed)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "learner_state.frozen_policy_validation", *args],
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
        '"policy_id":',
        '"source_fixture_id":',
        '"created_by_step":',
        '"temperature":',
        '"threshold":',
        '"allowed_abstention_rate":',
        '"split_policy_summary":',
        '"validation_input_summary":',
        '"safety_review":',
        '"raw_prediction_rows":',
        '"raw_label_rows":',
        '"prediction_rows":',
        '"label_rows":',
        '"logits":',
        '"logits_dump":',
        '"probability_dump":',
        '"probabilities":',
        '"calibration_policy":',
        '"split_metadata":',
        '"expected_action":',
        '"final_text":',
        '"observed_after_text":',
        '"gold_label":',
        '"teacher_correction":',
        '"human_correction":',
        '"raw_learner_text":',
        '"final_test_performance_claim":',
        '"metric_results":',
        '"metrics":',
        '"/Users/',
        '"/home/',
        '"real_data',
        '"private_data',
        '"participant_data',
        '"manual_outputs',
    ]
    assert_no_forbidden_fragments(
        test_case,
        output,
        forbidden_fragments,
        normalize_paths=True,
    )


if __name__ == "__main__":
    unittest.main()
