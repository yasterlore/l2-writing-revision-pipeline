from __future__ import annotations

import json
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
INVALID_BODY_CASE = FIXTURE_ROOT / "invalid" / "generated_policy_body_leakage"


class FrozenPolicyGenerationArtifactWriterCliTests(unittest.TestCase):
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
        completed = run_cli(
            "--request",
            str(VALID_CASE / "artifact_writer_request.json"),
        )

        self.assertEqual(completed.returncode, 2)
        assert_safe_cli_output(self, completed)

    def test_pointer_only_exits_two(self) -> None:
        completed = run_cli(
            "--pointer",
            str(VALID_CASE / "generator_result_pointer.json"),
        )

        self.assertEqual(completed.returncode, 2)
        assert_safe_cli_output(self, completed)

    def test_unknown_option_exits_two(self) -> None:
        completed = run_cli("--unknown-option")

        self.assertEqual(completed.returncode, 2)
        assert_safe_cli_output(self, completed)

    def test_missing_request_path_exits_two(self) -> None:
        completed = run_cli(
            "--request",
            "tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/valid/minimal_metadata_only_artifact_plan/missing_request.json",
            "--pointer",
            str(VALID_CASE / "generator_result_pointer.json"),
        )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("writer_status=input_error", completed.stdout)
        self.assertIn("reason_codes=missing_request_file", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_missing_pointer_path_exits_two(self) -> None:
        completed = run_cli(
            "--request",
            str(VALID_CASE / "artifact_writer_request.json"),
            "--pointer",
            "tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/valid/minimal_metadata_only_artifact_plan/missing_pointer.json",
            "--json",
        )

        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["writer_status"], "input_error")
        self.assertEqual(payload["reason_codes"], ["missing_pointer_file"])
        assert_safe_cli_output(self, completed)

    def test_malformed_json_temp_request_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            request_path = Path(tmp_dir) / "artifact_writer_request.json"
            request_path.write_text("{not-json", encoding="utf-8")

            completed = run_cli(
                "--request",
                str(request_path),
                "--pointer",
                str(VALID_CASE / "generator_result_pointer.json"),
            )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("writer_status=input_error", completed.stdout)
        self.assertIn("reason_codes=malformed_request", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_valid_case_human_exits_zero(self) -> None:
        completed = run_case_cli(VALID_CASE)

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=artifact_writer", completed.stdout)
        self.assertIn("writer_status=pass", completed.stdout)
        self.assertIn("reason_codes=none", completed.stdout)
        self.assertIn("failed_checks=none", completed.stdout)
        self.assertIn("safe_summary=metadata_only_artifact_writer_result", completed.stdout)
        self.assertIn('"generated_artifact_written":false', completed.stdout)
        self.assertIn('"artifact_body_suppressed":true', completed.stdout)
        self.assertIn('"manifest_body_suppressed":true', completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_valid_case_json_exits_zero_and_is_parseable(self) -> None:
        completed = run_case_cli(VALID_CASE, "--json")

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "artifact_writer")
        self.assertEqual(payload["writer_status"], "pass")
        self.assertEqual(payload["reason_codes"], [])
        self.assertEqual(payload["failed_checks"], [])
        self.assertEqual(
            payload["safe_summary"],
            "metadata_only_artifact_writer_result",
        )
        self.assertFalse(payload["artifact_flags"]["generated_artifact_written"])
        self.assertTrue(payload["artifact_flags"]["artifact_body_suppressed"])
        self.assertTrue(payload["artifact_flags"]["manifest_body_suppressed"])
        self.assertTrue(payload["safety_flags"]["content_suppressed"])
        self.assertEqual(payload["count_summary"]["body_field_count"], 0)
        assert_safe_cli_output(self, completed)

    def test_invalid_expected_fail_closed_case_human_exits_zero(self) -> None:
        completed = run_case_cli(INVALID_BODY_CASE)

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=artifact_writer", completed.stdout)
        self.assertIn("writer_status=fail", completed.stdout)
        self.assertIn("reason_codes=generated_policy_body_leakage", completed.stdout)
        self.assertIn(
            "safe_summary=fail_closed_metadata_only_artifact_writer_result",
            completed.stdout,
        )
        assert_safe_cli_output(self, completed)

    def test_invalid_expected_fail_closed_case_json_exits_zero_and_is_parseable(
        self,
    ) -> None:
        completed = run_case_cli(INVALID_BODY_CASE, "--json")

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "artifact_writer")
        self.assertEqual(payload["writer_status"], "fail")
        self.assertEqual(payload["reason_codes"], ["generated_policy_body_leakage"])
        self.assertEqual(
            payload["safe_summary"],
            "fail_closed_metadata_only_artifact_writer_result",
        )
        self.assertFalse(payload["artifact_flags"]["generated_artifact_written"])
        self.assertFalse(payload["artifact_flags"]["artifact_manifest_body_available"])
        assert_safe_cli_output(self, completed)

    def test_output_is_deterministic(self) -> None:
        first = run_case_cli(VALID_CASE, "--json")
        second = run_case_cli(VALID_CASE, "--json")

        self.assertEqual(first.returncode, 0)
        self.assertEqual(second.returncode, 0)
        self.assertEqual(first.stdout, second.stdout)
        assert_safe_cli_output(self, first)
        assert_safe_cli_output(self, second)


def run_case_cli(case_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run_cli(
        "--request",
        str(case_dir / "artifact_writer_request.json"),
        "--pointer",
        str(case_dir / "generator_result_pointer.json"),
        *args,
    )


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "learner_state.frozen_policy_generation_artifact_writer",
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
            '"request_body":',
            '"pointer_body":',
            '"expected_result_body":',
            '"artifact_body":',
            '"generated_artifact_body":',
            '"generated_policy_body":',
            '"manifest_body":',
            '"policy_body":',
            '"raw_rows":',
            '"logits":',
            '"probabilities":',
            '"raw_learner_text":',
            '"observed_after_text":',
            '"final_text":',
            '"gold_label":',
            '"expected_action":',
            '"scoring_feedback_payload":',
            '"private_path":',
            '"absolute_path":',
            '"real_participant_data":',
            '"calibration_body":',
            '"label_body":',
            '"split_body":',
            '"performance_metrics":',
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
