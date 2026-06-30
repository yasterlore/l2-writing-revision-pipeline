from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime import (
    MODE,
    RUNTIME_SCHEMA_VERSION,
    run_artifact_writer_cli_integration_runtime,
    run_artifact_writer_cli_integration_runtime_for_fixture_case,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime"
)
MODULE = (
    "learner_state."
    "frozen_policy_generation_artifact_writer_cli_integration_runtime"
)


class ArtifactWriterCliIntegrationRuntimeTests(unittest.TestCase):
    def test_valid_minimal_metadata_runtime_summary(self) -> None:
        summary = run_artifact_writer_cli_integration_runtime_for_fixture_case(
            FIXTURE_ROOT,
            "valid/valid_minimal_metadata_runtime_pass",
        )
        payload = summary.to_public_dict()

        self.assertEqual(payload["mode"], MODE)
        self.assertEqual(payload["runtime_schema_version"], RUNTIME_SCHEMA_VERSION)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["reason_code"], "none")
        self.assertEqual(payload["exit_code_category"], "zero")
        self.assertTrue(payload["runtime_executed"])
        self.assertFalse(payload["artifact_writer_cli_invoked"])
        self.assertTrue(payload["artifact_writer_cli_invocation_planned"])
        self.assertFalse(payload["artifact_body_generation_invoked"])
        self.assertFalse(payload["manifest_writer_invoked"])
        self.assertFalse(payload["file_writing_enabled"])
        self.assertFalse(payload["production_readiness_claimed"])
        self.assertFalse(payload["real_data_readiness_claimed"])
        self.assertFalse(payload["performance_claims_present"])
        assert_safe_output(self, json.dumps(payload, sort_keys=True))

    def test_valid_suppressed_artifact_writer_summary(self) -> None:
        summary = run_artifact_writer_cli_integration_runtime_for_fixture_case(
            FIXTURE_ROOT,
            "valid/valid_suppressed_artifact_writer_summary_pass",
        )

        self.assertEqual(summary.status, "pass")
        self.assertTrue(summary.content_suppressed)
        self.assertTrue(summary.body_suppressed)
        self.assertTrue(summary.no_request_body)
        self.assertTrue(summary.no_pointer_body)
        self.assertTrue(summary.no_expected_body)

    def test_valid_relative_fixture_path(self) -> None:
        case_dir = FIXTURE_ROOT / "valid/valid_safe_relative_repo_path_pass"
        summary = run_artifact_writer_cli_integration_runtime(
            request_metadata_path=case_dir / "request_metadata.json",
            pointer_metadata_path=case_dir / "pointer_metadata.json",
            artifact_writer_cli_metadata_path=case_dir
            / "artifact_writer_cli_metadata.json",
        )

        self.assertEqual(summary.status, "pass")
        self.assertTrue(summary.no_private_paths)
        self.assertTrue(summary.no_absolute_paths)

    def test_forbidden_request_body_fails_closed(self) -> None:
        summary = run_artifact_writer_cli_integration_runtime_for_fixture_case(
            FIXTURE_ROOT,
            "invalid/invalid_request_body_present",
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "request_body_present")
        self.assertEqual(summary.exit_code_category, "nonzero")
        self.assertFalse(summary.artifact_writer_cli_invocation_planned)

    def test_forbidden_pointer_body_fails_closed(self) -> None:
        summary = run_artifact_writer_cli_integration_runtime_for_fixture_case(
            FIXTURE_ROOT,
            "invalid/invalid_pointer_body_present",
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "pointer_body_present")

    def test_forbidden_artifact_body_payload_fails_closed(self) -> None:
        summary = run_artifact_writer_cli_integration_runtime_for_fixture_case(
            FIXTURE_ROOT,
            "invalid/invalid_artifact_body_payload_present",
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "artifact_body_payload_present")
        self.assertTrue(summary.no_artifact_body_payload)

    def test_forbidden_manifest_body_fails_closed(self) -> None:
        summary = run_artifact_writer_cli_integration_runtime_for_fixture_case(
            FIXTURE_ROOT,
            "invalid/invalid_manifest_body_present",
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "manifest_body_present")
        self.assertTrue(summary.no_manifest_body)

    def test_forbidden_generated_policy_body_fails_closed(self) -> None:
        summary = run_artifact_writer_cli_integration_runtime_for_fixture_case(
            FIXTURE_ROOT,
            "invalid/invalid_generated_policy_body_present",
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "generated_policy_body_present")
        self.assertTrue(summary.no_generated_policy_body)

    def test_raw_learner_text_fails_closed(self) -> None:
        summary = run_artifact_writer_cli_integration_runtime_for_fixture_case(
            FIXTURE_ROOT,
            "invalid/invalid_raw_learner_text_present",
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "raw_learner_text_present")

    def test_raw_rows_and_logits_fail_closed(self) -> None:
        raw_rows_summary = run_artifact_writer_cli_integration_runtime_for_fixture_case(
            FIXTURE_ROOT,
            "invalid/invalid_raw_rows_present",
        )
        logits_summary = run_artifact_writer_cli_integration_runtime_for_fixture_case(
            FIXTURE_ROOT,
            "invalid/invalid_logits_present",
        )

        self.assertEqual(raw_rows_summary.status, "fail_closed")
        self.assertEqual(raw_rows_summary.reason_code, "raw_rows_present")
        self.assertEqual(logits_summary.status, "fail_closed")
        self.assertEqual(logits_summary.reason_code, "logits_present")

    def test_private_and_absolute_path_fail_closed(self) -> None:
        private_summary = run_artifact_writer_cli_integration_runtime_for_fixture_case(
            FIXTURE_ROOT,
            "invalid/invalid_private_path_present",
        )
        absolute_summary = run_artifact_writer_cli_integration_runtime_for_fixture_case(
            FIXTURE_ROOT,
            "invalid/invalid_absolute_path_present",
        )

        self.assertEqual(private_summary.status, "fail_closed")
        self.assertEqual(private_summary.reason_code, "private_path_present")
        self.assertEqual(absolute_summary.status, "fail_closed")
        self.assertEqual(absolute_summary.reason_code, "absolute_path_present")

    def test_unsupported_schema_usage_error(self) -> None:
        summary = run_artifact_writer_cli_integration_runtime_for_fixture_case(
            FIXTURE_ROOT,
            "invalid/invalid_unsupported_schema_version",
        )

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "unsupported_schema_version")
        self.assertEqual(summary.return_code, 2)

    def test_no_runtime_output_residue_and_no_downstream_invocation(self) -> None:
        before = {path.as_posix() for path in FIXTURE_ROOT.rglob("*")}
        summary = run_artifact_writer_cli_integration_runtime_for_fixture_case(
            FIXTURE_ROOT,
            "valid/valid_file_writing_disabled_pass",
        )
        after = {path.as_posix() for path in FIXTURE_ROOT.rglob("*")}

        self.assertEqual(summary.status, "pass")
        self.assertEqual(before, after)
        self.assertFalse(summary.file_writing_enabled)
        self.assertFalse(summary.artifact_body_generation_invoked)
        self.assertFalse(summary.manifest_writer_invoked)

    def test_cli_json_output_body_free(self) -> None:
        completed = run_cli(
            "--fixture-case",
            "valid/valid_minimal_metadata_runtime_pass",
            "--json",
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], MODE)
        self.assertEqual(payload["status"], "pass")
        self.assertFalse(payload["artifact_writer_cli_invoked"])
        assert_safe_output(self, completed.stdout)
        assert_safe_output(self, completed.stderr)

    def test_cli_human_output_body_free(self) -> None:
        completed = run_cli(
            "--fixture-case",
            "valid/valid_minimal_metadata_runtime_pass",
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("mode=artifact_writer_cli_integration_runtime", completed.stdout)
        self.assertIn("status=pass", completed.stdout)
        self.assertIn("artifact_writer_cli_invoked=False", completed.stdout)
        assert_safe_output(self, completed.stdout)
        assert_safe_output(self, completed.stderr)

    def test_cli_invalid_case_returns_nonzero_body_free(self) -> None:
        completed = run_cli(
            "--fixture-case",
            "invalid/invalid_generated_policy_body_present",
            "--json",
        )

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "fail_closed")
        self.assertEqual(payload["reason_code"], "generated_policy_body_present")
        assert_safe_output(self, completed.stdout)
        assert_safe_output(self, completed.stderr)

    def test_cli_usage_error_returns_nonzero_body_free(self) -> None:
        completed = run_cli(
            "--fixture-case",
            "invalid/invalid_missing_required_metadata_file",
            "--json",
        )

        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "usage_error")
        self.assertEqual(payload["reason_code"], "missing_required_metadata_file")
        assert_safe_output(self, completed.stdout)

    def test_cli_help_output_body_free(self) -> None:
        completed = run_cli("--help")

        self.assertEqual(completed.returncode, 0)
        self.assertIn("--fixture-root", completed.stdout)
        self.assertIn("--fixture-case", completed.stdout)
        self.assertIn("--json", completed.stdout)
        assert_safe_output(self, completed.stdout)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", MODULE, *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def assert_safe_output(test_case: unittest.TestCase, text: str) -> None:
    assert_no_forbidden_fragments(
        test_case,
        text,
        [
            '"request_metadata":',
            '"pointer_metadata":',
            '"artifact_writer_cli_metadata":',
            '"request_body":',
            '"pointer_body":',
            '"expected_body":',
            '"written_file_json_body":',
            '"manifest_body":',
            '"artifact_body_payload":',
            '"generated_policy_body":',
            '"raw_rows":',
            '"logits":',
            '"probabilities":',
            '"private_path":',
            '"absolute_path":',
            '"raw_learner_text":',
            '"real_participant_data":',
        ],
    )


if __name__ == "__main__":
    unittest.main()
