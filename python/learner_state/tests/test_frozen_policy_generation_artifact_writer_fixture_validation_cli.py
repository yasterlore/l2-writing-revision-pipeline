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
    "tests/fixtures/learner_state_frozen_policy_generation_artifact_writer"
)
VALID_CASE = FIXTURE_ROOT / "valid" / "minimal_metadata_only_artifact_plan"
INVALID_CASE = FIXTURE_ROOT / "invalid" / "generated_policy_body_leakage"


class FrozenPolicyGenerationArtifactWriterFixtureValidationCliTests(unittest.TestCase):
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

    def test_missing_root_exits_two(self) -> None:
        completed = run_cli(
            "--fixture-root",
            "tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_missing",
        )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("mode=fixture_root", completed.stdout)
        self.assertIn("input_error_cases=1", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_missing_case_exits_two(self) -> None:
        completed = run_cli(
            "--fixture-case",
            "tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/valid/missing_case",
        )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("mode=fixture_case", completed.stdout)
        self.assertIn("writer_status=input_error", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_root_human_exits_zero(self) -> None:
        completed = run_cli("--fixture-root", str(FIXTURE_ROOT))

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=fixture_root", completed.stdout)
        self.assertIn("total_cases=17", completed.stdout)
        self.assertIn("valid_cases=3", completed.stdout)
        self.assertIn("invalid_cases=14", completed.stdout)
        self.assertIn("matched_cases=17", completed.stdout)
        self.assertIn("mismatched_cases=0", completed.stdout)
        self.assertIn("input_error_cases=0", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_root_json_exits_zero_and_is_parseable(self) -> None:
        completed = run_cli("--fixture-root", str(FIXTURE_ROOT), "--json")

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "fixture_root")
        self.assertEqual(payload["total_cases"], 17)
        self.assertEqual(payload["matched_cases"], 17)
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
        self.assertIn("case_id=valid/minimal_metadata_only_artifact_plan", completed.stdout)
        self.assertIn("category=valid", completed.stdout)
        self.assertIn("writer_status=pass", completed.stdout)
        self.assertIn("matched=true", completed.stdout)
        self.assertIn("reason_codes=none", completed.stdout)
        self.assertIn("failed_checks=none", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_valid_case_json_exits_zero_and_is_parseable(self) -> None:
        completed = run_cli("--fixture-case", str(VALID_CASE), "--json")

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "fixture_case")
        self.assertEqual(payload["case_id"], "valid/minimal_metadata_only_artifact_plan")
        self.assertEqual(payload["category"], "valid")
        self.assertEqual(payload["writer_status"], "pass")
        self.assertTrue(payload["matched"])
        self.assertEqual(payload["reason_codes"], [])
        assert_safe_cli_output(self, completed)

    def test_invalid_expected_fail_closed_case_human_exits_zero(self) -> None:
        completed = run_cli("--fixture-case", str(INVALID_CASE))

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=fixture_case", completed.stdout)
        self.assertIn("case_id=invalid/generated_policy_body_leakage", completed.stdout)
        self.assertIn("category=invalid", completed.stdout)
        self.assertIn("writer_status=fail", completed.stdout)
        self.assertIn("matched=true", completed.stdout)
        self.assertIn("reason_codes=generated_policy_body_leakage", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_invalid_expected_fail_closed_case_json_exits_zero(self) -> None:
        completed = run_cli("--fixture-case", str(INVALID_CASE), "--json")

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "fixture_case")
        self.assertEqual(payload["case_id"], "invalid/generated_policy_body_leakage")
        self.assertEqual(payload["category"], "invalid")
        self.assertEqual(payload["writer_status"], "fail")
        self.assertTrue(payload["matched"])
        self.assertEqual(payload["reason_codes"], ["generated_policy_body_leakage"])
        assert_safe_cli_output(self, completed)

    def test_malformed_json_temp_case_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "malformed_case"
            shutil.copytree(VALID_CASE, tmp_case)
            (tmp_case / "artifact_writer_request.json").write_text(
                "{", encoding="utf-8"
            )

            completed = run_cli("--fixture-case", str(tmp_case))

        self.assertEqual(completed.returncode, 2)
        self.assertIn("mode=fixture_case", completed.stdout)
        self.assertIn("writer_status=input_error", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_mismatch_temp_case_exits_three(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "mismatch_case"
            shutil.copytree(VALID_CASE, tmp_case)
            expected_path = tmp_case / "expected_artifact_writer_result.json"
            expected = json.loads(expected_path.read_text(encoding="utf-8"))
            expected["count_summary"]["validation_reference_count"] = 99
            expected_path.write_text(
                json.dumps(expected, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            completed = run_cli("--fixture-case", str(tmp_case), "--json")

        self.assertEqual(completed.returncode, 3)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "fixture_case")
        self.assertFalse(payload["matched"])
        self.assertGreaterEqual(payload["mismatch_count"], 1)
        self.assertIn("validation_reference_count_mismatch", payload["mismatch_fields"])
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
            "learner_state.frozen_policy_generation_artifact_writer_fixture_validation",
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
            '"artifact_writer_request":',
            '"generator_result_pointer":',
            '"expected_artifact_writer_result":',
            '"generated_policy_body":',
            '"generated_artifact_body":',
            '"artifact_body":',
            '"manifest_body":',
            '"policy_body":',
            '"raw_rows":',
            '"logits":',
            '"probabilities":',
            '"raw_learner_text":',
            '"observed_after_text":',
            '"final_text":',
            '"gold_label":',
            '"performance_metrics":',
            '"request_body":',
            '"pointer_body":',
            '"expected_result_body":',
            "/Users/",
            "/home/",
            "/private/",
            "/var/folders/",
            "real_data/",
            "participant_data/",
            "manual_outputs/",
        ],
    )


if __name__ == "__main__":
    unittest.main()
