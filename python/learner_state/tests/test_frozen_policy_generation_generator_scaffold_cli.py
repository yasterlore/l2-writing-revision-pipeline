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


class FrozenPolicyGenerationGeneratorScaffoldCliTests(unittest.TestCase):
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
        completed = run_cli("--pointer", str(VALID_CASE / "input_fixture_pointer.json"))

        self.assertEqual(completed.returncode, 2)
        assert_safe_cli_output(self, completed)

    def test_valid_case_human_exits_zero(self) -> None:
        completed = run_case_cli(VALID_CASE)

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=generator_scaffold", completed.stdout)
        self.assertIn("generation_status=pass", completed.stdout)
        self.assertIn("reason_codes=none", completed.stdout)
        self.assertIn("failed_checks=none", completed.stdout)
        self.assertIn(
            "safe_summary=metadata_only_generator_scaffold_result",
            completed.stdout,
        )
        self.assertIn('"generated_artifact_written":false', completed.stdout)
        self.assertIn('"artifact_body_suppressed":true', completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_valid_case_json_exits_zero_and_is_parseable(self) -> None:
        completed = run_case_cli(VALID_CASE, "--json")

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "generator_scaffold")
        self.assertEqual(payload["generation_status"], "pass")
        self.assertEqual(payload["reason_codes"], [])
        self.assertEqual(payload["failed_checks"], [])
        self.assertEqual(
            payload["safe_summary"],
            "metadata_only_generator_scaffold_result",
        )
        self.assertFalse(payload["artifact_flags"]["generated_artifact_written"])
        self.assertTrue(payload["artifact_flags"]["artifact_body_suppressed"])
        self.assertTrue(payload["safety_flags"]["content_suppressed"])
        self.assertEqual(payload["count_summary"]["body_field_count"], 0)
        assert_safe_cli_output(self, completed)

    def test_invalid_expected_fail_closed_human_exits_zero(self) -> None:
        completed = run_case_cli(INVALID_TEMPERATURE_CASE)

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=generator_scaffold", completed.stdout)
        self.assertIn("generation_status=fail", completed.stdout)
        self.assertIn("reason_codes=test_temperature_tuning", completed.stdout)
        self.assertIn(
            "safe_summary=fail_closed_metadata_only_generator_scaffold_result",
            completed.stdout,
        )
        assert_safe_cli_output(self, completed)

    def test_invalid_expected_fail_closed_json_exits_zero_and_is_parseable(self) -> None:
        completed = run_case_cli(INVALID_TEMPERATURE_CASE, "--json")

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "generator_scaffold")
        self.assertEqual(payload["generation_status"], "fail")
        self.assertEqual(payload["reason_codes"], ["test_temperature_tuning"])
        self.assertEqual(
            payload["safe_summary"],
            "fail_closed_metadata_only_generator_scaffold_result",
        )
        self.assertFalse(payload["artifact_flags"]["generated_artifact_written"])
        assert_safe_cli_output(self, completed)

    def test_malformed_request_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "case"
            shutil.copytree(VALID_CASE, tmp_case)
            (tmp_case / "generation_request.json").write_text("{", encoding="utf-8")

            completed = run_case_cli(tmp_case)

        self.assertEqual(completed.returncode, 2)
        self.assertIn("generation_status=input_error", completed.stdout)
        self.assertIn("reason_codes=malformed_request", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_missing_pointer_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "case"
            shutil.copytree(VALID_CASE, tmp_case)
            (tmp_case / "input_fixture_pointer.json").unlink()

            completed = run_case_cli(tmp_case, "--json")

        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["generation_status"], "input_error")
        self.assertEqual(payload["reason_codes"], ["missing_pointer_file"])
        assert_safe_cli_output(self, completed)

    def test_generated_artifact_body_request_fail_closed_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "case"
            shutil.copytree(VALID_CASE, tmp_case)
            before = sorted(path.relative_to(tmp_case) for path in tmp_case.rglob("*"))
            request_path = tmp_case / "generation_request.json"
            request_payload = json.loads(request_path.read_text(encoding="utf-8"))
            request_payload["requested_artifact_body"] = True
            request_path.write_text(
                json.dumps(request_payload, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            completed = run_case_cli(tmp_case, "--json")
            after = sorted(path.relative_to(tmp_case) for path in tmp_case.rglob("*"))

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["generation_status"], "fail")
        self.assertEqual(payload["reason_codes"], ["generated_artifact_body_leakage"])
        self.assertFalse(payload["artifact_flags"]["generated_artifact_body_available"])
        self.assertEqual(before, after)
        assert_safe_cli_output(self, completed)

    def test_artifact_file_writing_request_fail_closed_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "case"
            shutil.copytree(VALID_CASE, tmp_case)
            before = sorted(path.relative_to(tmp_case) for path in tmp_case.rglob("*"))
            request_path = tmp_case / "generation_request.json"
            request_payload = json.loads(request_path.read_text(encoding="utf-8"))
            request_payload["requested_file_writing"] = True
            request_path.write_text(
                json.dumps(request_payload, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            completed = run_case_cli(tmp_case, "--json")
            after = sorted(path.relative_to(tmp_case) for path in tmp_case.rglob("*"))

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["generation_status"], "fail")
        self.assertEqual(payload["reason_codes"], ["artifact_file_writing_not_allowed"])
        self.assertFalse(payload["artifact_flags"]["generated_artifact_written"])
        self.assertEqual(before, after)
        assert_safe_cli_output(self, completed)

    def test_output_is_deterministic(self) -> None:
        first = run_case_cli(VALID_CASE)
        second = run_case_cli(VALID_CASE)

        self.assertEqual(first.returncode, 0)
        self.assertEqual(second.returncode, 0)
        self.assertEqual(first.stdout, second.stdout)
        assert_safe_cli_output(self, first)
        assert_safe_cli_output(self, second)


def run_case_cli(case_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run_cli(
        "--request",
        str(case_dir / "generation_request.json"),
        "--pointer",
        str(case_dir / "input_fixture_pointer.json"),
        *args,
    )


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "learner_state.frozen_policy_generation_generator_scaffold",
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
            '"expected_result_body":',
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
