from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime import (
    ACTUAL_INVOCATION_MODE,
    MODE,
    RUNTIME_SCHEMA_VERSION,
    RUNTIME_SCHEMA_VERSION_V0_2,
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

    def test_default_remains_plan_only_for_v0_1_case(self) -> None:
        summary = run_artifact_writer_cli_integration_runtime_for_fixture_case(
            FIXTURE_ROOT,
            "valid/valid_minimal_metadata_runtime_pass",
        )

        self.assertEqual(summary.runtime_schema_version, RUNTIME_SCHEMA_VERSION)
        self.assertFalse(summary.runtime_actual_invocation_enabled)
        self.assertFalse(summary.artifact_writer_cli_invoked)
        self.assertTrue(summary.artifact_writer_cli_invocation_planned)

    def test_actual_invocation_flag_required_for_v0_2_case(self) -> None:
        summary = run_artifact_writer_cli_integration_runtime_for_fixture_case(
            FIXTURE_ROOT,
            "valid/valid_actual_invocation_minimal_metadata_only",
        )

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "actual_invocation_flag_required")
        self.assertFalse(summary.artifact_writer_cli_invoked)

    def test_actual_invocation_mode_returns_schema_v0_2(self) -> None:
        summary = run_actual_case("valid/valid_actual_invocation_minimal_metadata_only")
        payload = summary.to_public_dict()

        self.assertEqual(payload["runtime_schema_version"], RUNTIME_SCHEMA_VERSION_V0_2)
        self.assertEqual(payload["invocation_mode"], ACTUAL_INVOCATION_MODE)
        self.assertTrue(payload["runtime_actual_invocation_enabled"])
        self.assertTrue(payload["artifact_writer_cli_invoked"])
        self.assertFalse(payload["artifact_writer_cli_invocation_planned"])
        self.assertTrue(payload["artifact_writer_cli_output_scanned"])
        self.assertTrue(payload["artifact_writer_cli_output_body_free"])
        self.assertTrue(payload["raw_stdout_body_suppressed"])
        self.assertTrue(payload["raw_stderr_body_suppressed"])
        assert_safe_output(self, json.dumps(payload, sort_keys=True))

    def test_valid_actual_invocation_cases_pass(self) -> None:
        cases = (
            "valid/valid_actual_invocation_minimal_metadata_only",
            "valid/valid_actual_invocation_body_free_output",
            "valid/valid_actual_invocation_file_writing_disabled",
            "valid/valid_actual_invocation_no_downstream_invocation",
        )
        for case in cases:
            with self.subTest(case=case):
                summary = run_actual_case(case)
                self.assertEqual(summary.status, "pass")
                self.assertEqual(summary.reason_code, "none")
                self.assertFalse(summary.file_writing_enabled)
                self.assertFalse(summary.artifact_body_generation_invoked)
                self.assertFalse(summary.manifest_writer_invoked)

    def test_valid_actual_invocation_nonzero_exit_safe_summary(self) -> None:
        summary = run_actual_case(
            "valid/valid_actual_invocation_nonzero_exit_safe_summary"
        )

        self.assertEqual(summary.status, "pass")
        self.assertEqual(summary.exit_code_category, "nonzero")
        self.assertEqual(summary.artifact_writer_cli_exit_code_category, "nonzero")
        self.assertTrue(summary.artifact_writer_cli_output_body_free)

    def test_valid_actual_invocation_timeout_safe_summary(self) -> None:
        summary = run_actual_case("valid/valid_actual_invocation_timeout_safe_summary")

        self.assertEqual(summary.status, "pass")
        self.assertEqual(summary.exit_code_category, "timeout")
        self.assertEqual(summary.artifact_writer_cli_exit_code_category, "timeout")
        self.assertTrue(summary.artifact_writer_cli_output_body_free)

    def test_valid_actual_invocation_file_writing_and_downstream_disabled(
        self,
    ) -> None:
        file_summary = run_actual_case(
            "valid/valid_actual_invocation_file_writing_disabled"
        )
        downstream_summary = run_actual_case(
            "valid/valid_actual_invocation_no_downstream_invocation"
        )

        self.assertFalse(file_summary.file_writing_enabled)
        self.assertFalse(file_summary.file_writing_detected)
        self.assertFalse(downstream_summary.artifact_body_generation_invoked)
        self.assertFalse(downstream_summary.manifest_writer_invoked)

    def test_actual_invocation_output_body_sentinels_fail_closed(self) -> None:
        expectations = {
            "invalid/invalid_actual_invocation_raw_stdout_body": (
                "raw_stdout_body_present"
            ),
            "invalid/invalid_actual_invocation_raw_stderr_body": (
                "raw_stderr_body_present"
            ),
            "invalid/invalid_actual_invocation_artifact_body_payload": (
                "artifact_body_payload_present"
            ),
            "invalid/invalid_actual_invocation_manifest_body": (
                "manifest_body_present"
            ),
            "invalid/invalid_actual_invocation_generated_policy_body": (
                "generated_policy_body_present"
            ),
        }
        for case, reason_code in expectations.items():
            with self.subTest(case=case):
                summary = run_actual_case(case)
                self.assertEqual(summary.status, "fail_closed")
                self.assertEqual(summary.reason_code, reason_code)
                self.assertTrue(summary.runtime_actual_invocation_fail_closed)
                self.assertFalse(summary.runtime_actual_invocation_safety_scan_passed)

    def test_actual_invocation_request_pointer_expected_sentinels_fail_closed(
        self,
    ) -> None:
        expectations = {
            "invalid/invalid_actual_invocation_request_body": "request_body_present",
            "invalid/invalid_actual_invocation_pointer_body": "pointer_body_present",
            "invalid/invalid_actual_invocation_expected_body": "expected_body_present",
        }
        for case, reason_code in expectations.items():
            with self.subTest(case=case):
                summary = run_actual_case(case)
                self.assertEqual(summary.status, "fail_closed")
                self.assertEqual(summary.reason_code, reason_code)

    def test_actual_invocation_private_absolute_and_oracle_sentinels_fail_closed(
        self,
    ) -> None:
        expectations = {
            "invalid/invalid_actual_invocation_private_path": "private_path_present",
            "invalid/invalid_actual_invocation_absolute_path": "absolute_path_present",
            "invalid/invalid_actual_invocation_raw_learner_text": (
                "raw_learner_text_present"
            ),
            "invalid/invalid_actual_invocation_raw_rows": "raw_rows_present",
            "invalid/invalid_actual_invocation_logits": "logits_present",
        }
        for case, reason_code in expectations.items():
            with self.subTest(case=case):
                summary = run_actual_case(case)
                self.assertEqual(summary.status, "fail_closed")
                self.assertEqual(summary.reason_code, reason_code)

    def test_actual_invocation_file_writing_and_downstream_sentinels_fail_closed(
        self,
    ) -> None:
        expectations = {
            "invalid/invalid_actual_invocation_file_writing_detected": (
                "file_writing_detected"
            ),
            "invalid/invalid_actual_invocation_artifact_body_generation_invoked": (
                "artifact_body_generation_invoked"
            ),
            "invalid/invalid_actual_invocation_manifest_writer_invoked": (
                "manifest_writer_invoked"
            ),
        }
        for case, reason_code in expectations.items():
            with self.subTest(case=case):
                summary = run_actual_case(case)
                self.assertEqual(summary.status, "fail_closed")
                self.assertEqual(summary.reason_code, reason_code)

    def test_actual_invocation_unsupported_schema_usage_error(self) -> None:
        summary = run_actual_case("invalid/invalid_actual_invocation_unsupported_schema")

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "unsupported_schema_version")
        self.assertEqual(summary.return_code, 2)

    def test_actual_invocation_mismatched_expected_status_reports_mismatch(
        self,
    ) -> None:
        summary = run_actual_case(
            "invalid/invalid_actual_invocation_mismatched_expected_status"
        )

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "mismatched_expected_status")
        self.assertEqual(summary.return_code, 1)

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
        self.assertIn("--actual-invocation", completed.stdout)
        self.assertIn("--summary-only", completed.stdout)
        self.assertIn("--no-file-writing", completed.stdout)
        self.assertIn("--json", completed.stdout)
        assert_safe_output(self, completed.stdout)

    def test_cli_actual_invocation_output_body_free(self) -> None:
        completed = run_cli(
            "--fixture-case",
            "valid/valid_actual_invocation_minimal_metadata_only",
            "--actual-invocation",
            "--summary-only",
            "--no-file-writing",
            "--json",
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["runtime_schema_version"], RUNTIME_SCHEMA_VERSION_V0_2)
        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["runtime_actual_invocation_enabled"])
        self.assertTrue(payload["artifact_writer_cli_invoked"])
        self.assertTrue(payload["artifact_writer_cli_output_body_free"])
        assert_safe_output(self, completed.stdout)
        assert_safe_output(self, completed.stderr)

    def test_cli_actual_invocation_fail_closed_output_body_free(self) -> None:
        completed = run_cli(
            "--fixture-case",
            "invalid/invalid_actual_invocation_raw_stdout_body",
            "--actual-invocation",
            "--summary-only",
            "--no-file-writing",
            "--json",
        )

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "fail_closed")
        self.assertEqual(payload["reason_code"], "raw_stdout_body_present")
        self.assertTrue(payload["runtime_actual_invocation_fail_closed"])
        assert_safe_output(self, completed.stdout)
        assert_safe_output(self, completed.stderr)

    def test_cli_actual_invocation_conflicting_flags_usage_error(self) -> None:
        completed = run_cli(
            "--fixture-case",
            "valid/valid_actual_invocation_minimal_metadata_only",
            "--actual-invocation",
            "--plan-only",
            "--json",
        )

        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "usage_error")
        self.assertEqual(payload["reason_code"], "conflicting_runtime_mode_flags")
        assert_safe_output(self, completed.stdout)

    def test_cli_actual_invocation_invalid_timeout_usage_error(self) -> None:
        completed = run_cli(
            "--fixture-case",
            "valid/valid_actual_invocation_minimal_metadata_only",
            "--actual-invocation",
            "--timeout-seconds",
            "0",
            "--json",
        )

        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "usage_error")
        self.assertEqual(payload["reason_code"], "invalid_timeout_seconds")
        assert_safe_output(self, completed.stdout)

    def test_actual_invocation_no_residue_and_deterministic_summary(self) -> None:
        before = {path.as_posix() for path in FIXTURE_ROOT.rglob("*")}
        first = run_actual_case("valid/valid_actual_invocation_minimal_metadata_only")
        second = run_actual_case("valid/valid_actual_invocation_minimal_metadata_only")
        after = {path.as_posix() for path in FIXTURE_ROOT.rglob("*")}

        self.assertEqual(before, after)
        self.assertEqual(first.to_public_dict(), second.to_public_dict())


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", MODULE, *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_actual_case(case: str):
    return run_artifact_writer_cli_integration_runtime_for_fixture_case(
        FIXTURE_ROOT,
        case,
        actual_invocation=True,
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
