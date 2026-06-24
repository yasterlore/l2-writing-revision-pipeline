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

from learner_state import frozen_policy_generation_artifact_body as artifact_body_module
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path(
    "tests/fixtures/learner_state_frozen_policy_generation_artifact_body"
)
SUPPRESSED_CASE = FIXTURE_ROOT / "valid" / "minimal_suppressed_metadata_only_body"
SAFE_METADATA_CASE = FIXTURE_ROOT / "valid" / "safe_metadata_body_summary"


class FrozenPolicyGenerationArtifactBodyCliTests(unittest.TestCase):
    def test_help_exits_zero(self) -> None:
        completed = run_cli("--help")

        self.assertEqual(completed.returncode, 0)
        self.assertIn("--request", completed.stdout)
        self.assertIn("--pointer", completed.stdout)
        self.assertIn("--mode", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_no_args_exits_two(self) -> None:
        completed = run_cli()

        self.assertEqual(completed.returncode, 2)
        assert_safe_cli_output(self, completed)

    def test_request_only_exits_two(self) -> None:
        completed = run_cli(
            "--request",
            str(SUPPRESSED_CASE / "artifact_body_request.json"),
        )

        self.assertEqual(completed.returncode, 2)
        assert_safe_cli_output(self, completed)

    def test_pointer_only_exits_two(self) -> None:
        completed = run_cli(
            "--pointer",
            str(SUPPRESSED_CASE / "artifact_writer_result_pointer.json"),
        )

        self.assertEqual(completed.returncode, 2)
        assert_safe_cli_output(self, completed)

    def test_unknown_mode_exits_two(self) -> None:
        completed = run_case_cli(SUPPRESSED_CASE, "--mode", "print-body")

        self.assertEqual(completed.returncode, 2)
        assert_safe_cli_output(self, completed)

    def test_unknown_option_exits_two(self) -> None:
        completed = run_cli("--unknown-option")

        self.assertEqual(completed.returncode, 2)
        assert_safe_cli_output(self, completed)

    def test_valid_suppressed_human_exits_zero(self) -> None:
        completed = run_case_cli(SUPPRESSED_CASE)

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=artifact_body_generation", completed.stdout)
        self.assertIn("generation_status=pass", completed.stdout)
        self.assertIn("body_status=suppressed_metadata_only", completed.stdout)
        self.assertIn("artifact_body_available=false", completed.stdout)
        self.assertIn("artifact_file_written=false", completed.stdout)
        self.assertIn("manifest_file_written=false", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_valid_suppressed_json_exits_zero_and_is_parseable(self) -> None:
        completed = run_case_cli(SUPPRESSED_CASE, "--json")

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "artifact_body_generation")
        self.assertEqual(payload["generation_status"], "pass")
        self.assertEqual(payload["body_status"], "suppressed_metadata_only")
        self.assertFalse(payload["artifact_body_available"])
        self.assertFalse(payload["artifact_file_written"])
        self.assertFalse(payload["manifest_file_written"])
        self.assertEqual(payload["reason_codes"], [])
        self.assertEqual(payload["failed_checks"], [])
        self.assertNotIn("artifact_body", payload)
        self.assertNotIn("request_body", payload)
        self.assertNotIn("pointer_body", payload)
        self.assertNotIn("manifest_body", payload)
        assert_safe_cli_output(self, completed)

    def test_valid_safe_metadata_human_exits_zero(self) -> None:
        completed = run_case_cli(SAFE_METADATA_CASE, "--mode", "safe-metadata")

        self.assertEqual(completed.returncode, 0)
        self.assertIn("mode=artifact_body_generation", completed.stdout)
        self.assertIn("generation_status=pass", completed.stdout)
        self.assertIn("body_status=generated_safe_metadata_body", completed.stdout)
        self.assertIn("artifact_body_available=true", completed.stdout)
        self.assertIn("artifact_file_written=false", completed.stdout)
        self.assertIn("manifest_file_written=false", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_valid_safe_metadata_json_exits_zero_and_is_parseable(self) -> None:
        completed = run_case_cli(SAFE_METADATA_CASE, "--mode", "safe-metadata", "--json")

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "artifact_body_generation")
        self.assertEqual(payload["generation_status"], "pass")
        self.assertEqual(payload["body_status"], "generated_safe_metadata_body")
        self.assertTrue(payload["artifact_body_available"])
        self.assertFalse(payload["artifact_file_written"])
        self.assertFalse(payload["manifest_file_written"])
        self.assertTrue(payload["safety_flags"]["content_suppressed"])
        self.assertEqual(payload["count_summary"]["raw_row_count"], 0)
        self.assertEqual(payload["count_summary"]["logits_dump_count"], 0)
        self.assertNotIn("artifact_body", payload)
        assert_safe_cli_output(self, completed)

    def test_json_output_is_deterministic(self) -> None:
        first = run_case_cli(SAFE_METADATA_CASE, "--mode", "safe-metadata", "--json")
        second = run_case_cli(SAFE_METADATA_CASE, "--mode", "safe-metadata", "--json")

        self.assertEqual(first.returncode, 0)
        self.assertEqual(second.returncode, 0)
        self.assertEqual(first.stdout, second.stdout)
        assert_safe_cli_output(self, first)
        assert_safe_cli_output(self, second)

    def test_malformed_request_json_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            request_path = Path(tmp_dir) / "artifact_body_request.json"
            request_path.write_text("{", encoding="utf-8")

            completed = run_cli(
                "--request",
                str(request_path),
                "--pointer",
                str(SUPPRESSED_CASE / "artifact_writer_result_pointer.json"),
            )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("generation_status=input_error", completed.stdout)
        self.assertIn("reason_codes=malformed_request_json", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_malformed_pointer_json_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            pointer_path = Path(tmp_dir) / "artifact_writer_result_pointer.json"
            pointer_path.write_text("{", encoding="utf-8")

            completed = run_cli(
                "--request",
                str(SUPPRESSED_CASE / "artifact_body_request.json"),
                "--pointer",
                str(pointer_path),
            )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("generation_status=input_error", completed.stdout)
        self.assertIn("reason_codes=malformed_pointer_json", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_unsafe_temp_payload_exits_three_without_echoing_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            case_dir = Path(tmp_dir) / "case"
            case_dir.mkdir()
            request_path = case_dir / "artifact_body_request.json"
            pointer_path = case_dir / "artifact_writer_result_pointer.json"
            shutil.copyfile(
                SUPPRESSED_CASE / "artifact_body_request.json",
                request_path,
            )
            shutil.copyfile(
                SUPPRESSED_CASE / "artifact_writer_result_pointer.json",
                pointer_path,
            )
            request = json.loads(request_path.read_text(encoding="utf-8"))
            request["raw_learner_text"] = "synthetic unsafe body marker"
            request_path.write_text(json.dumps(request, sort_keys=True), encoding="utf-8")

            completed = run_cli(
                "--request",
                str(request_path),
                "--pointer",
                str(pointer_path),
            )

        self.assertEqual(completed.returncode, 3)
        self.assertIn("generation_status=fail", completed.stdout)
        self.assertIn("reason_codes=raw_learner_text_in_artifact_body", completed.stdout)
        self.assertNotIn("synthetic unsafe body marker", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_no_output_files_created(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            case_dir = Path(tmp_dir) / "case"
            case_dir.mkdir()
            request_path = case_dir / "artifact_body_request.json"
            pointer_path = case_dir / "artifact_writer_result_pointer.json"
            shutil.copyfile(
                SAFE_METADATA_CASE / "artifact_body_request.json",
                request_path,
            )
            shutil.copyfile(
                SAFE_METADATA_CASE / "artifact_writer_result_pointer.json",
                pointer_path,
            )
            before = sorted(path.name for path in case_dir.iterdir())
            completed = run_cli(
                "--request",
                str(request_path),
                "--pointer",
                str(pointer_path),
                "--mode",
                "safe-metadata",
            )
            after = sorted(path.name for path in case_dir.iterdir())

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(before, after)
        assert_safe_cli_output(self, completed)

    def test_cli_calls_existing_generation_api(self) -> None:
        with mock.patch.object(
            artifact_body_module,
            "generate_artifact_body",
            wraps=artifact_body_module.generate_artifact_body,
        ) as generate:
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                exit_code = artifact_body_module.main(
                    [
                        "--request",
                        str(SUPPRESSED_CASE / "artifact_body_request.json"),
                        "--pointer",
                        str(SUPPRESSED_CASE / "artifact_writer_result_pointer.json"),
                    ]
                )

        self.assertEqual(exit_code, 0)
        self.assertTrue(generate.called)
        self.assertIn("mode=artifact_body_generation", buffer.getvalue())


def run_case_cli(case_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run_cli(
        "--request",
        str(case_dir / "artifact_body_request.json"),
        "--pointer",
        str(case_dir / "artifact_writer_result_pointer.json"),
        *args,
    )


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "learner_state.frozen_policy_generation_artifact_body",
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
            '"request_body":',
            '"pointer_body":',
            '"expected_body":',
            '"expected_result_body":',
            '"artifact_body_payload":',
            '"generated_artifact_body":',
            '"frozen_policy_artifact_body":',
            '"generated_policy_body":',
            '"policy_body":',
            '"manifest_body":',
            '"raw_rows":',
            '"logits":',
            '"probabilities":',
            '"private_path":',
            '"raw_learner_text":',
            '"observed_after_text":',
            '"final_text":',
            '"gold_label":',
            '"performance_metrics":',
            "synthetic unsafe body marker",
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
