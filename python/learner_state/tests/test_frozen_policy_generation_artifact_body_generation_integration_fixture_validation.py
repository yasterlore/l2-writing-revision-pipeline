from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_artifact_body_generation_integration_fixture_validation import (
    EXPECTED_FAIL_CLOSED_CASES,
    EXPECTED_MISMATCH_CASES,
    EXPECTED_PASS_CASES,
    EXPECTED_TOTAL_CASES,
    EXPECTED_TOTAL_JSON_FILES,
    EXPECTED_USAGE_ERROR_CASES,
    JSON_FILES_PER_CASE,
    REQUIRED_FILES,
    summarize_artifact_body_generation_integration_fixture_validation,
    validate_artifact_body_generation_integration_fixture_case,
    validate_artifact_body_generation_integration_fixture_root,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_body_generation_integration"
)
MODULE = (
    "learner_state."
    "frozen_policy_generation_artifact_body_generation_integration_fixture_validation"
)


class ArtifactBodyGenerationIntegrationFixtureValidationTests(unittest.TestCase):
    def test_valid_aggregate_pass(self) -> None:
        summary = validate_artifact_body_generation_integration_fixture_root(
            FIXTURE_ROOT
        )
        payload = summarize_artifact_body_generation_integration_fixture_validation(
            summary
        )

        self.assertTrue(summary.all_matched)
        self.assertEqual(payload["mode"], "artifact_body_generation_integration_fixture_validation")
        self.assertEqual(
            payload["validation_schema_version"],
            "learner_state_frozen_policy_generation_artifact_body_generation_integration_fixture_validation_v0.1",
        )
        self.assertEqual(payload["matched_cases"], EXPECTED_TOTAL_CASES)
        self.assertEqual(payload["mismatched_cases"], 0)
        self.assertEqual(payload["input_error_cases"], 0)
        self.assertEqual(payload["pass_cases"], EXPECTED_PASS_CASES)
        self.assertEqual(payload["usage_error_cases"], EXPECTED_USAGE_ERROR_CASES)
        self.assertEqual(payload["fail_closed_cases"], EXPECTED_FAIL_CLOSED_CASES)
        self.assertEqual(payload["mismatch_cases"], EXPECTED_MISMATCH_CASES)
        self.assertTrue(payload["content_suppressed"])
        self.assertTrue(payload["body_suppressed"])
        self.assertFalse(payload["production_readiness_claimed"])
        self.assertFalse(payload["real_data_readiness_claimed"])
        self.assertFalse(payload["performance_claims_present"])
        assert_safe_output(self, json.dumps(payload, sort_keys=True))

    def test_total_counts(self) -> None:
        summary = validate_artifact_body_generation_integration_fixture_root(
            FIXTURE_ROOT
        )

        self.assertEqual(summary.total_cases, EXPECTED_TOTAL_CASES)
        self.assertEqual(summary.valid_cases, 6)
        self.assertEqual(summary.invalid_cases, 22)
        self.assertEqual(summary.actual_json_files, EXPECTED_TOTAL_JSON_FILES)
        self.assertEqual(JSON_FILES_PER_CASE, 7)

    def test_required_files(self) -> None:
        for case_dir in sorted(path for path in FIXTURE_ROOT.glob("*/*") if path.is_dir()):
            with self.subTest(case=case_label(case_dir)):
                self.assertEqual(
                    sorted(path.name for path in case_dir.glob("*.json")),
                    sorted(REQUIRED_FILES),
                )

    def test_missing_required_file(self) -> None:
        with temp_root_copy() as root:
            target = (
                root
                / "valid/valid_minimal_suppressed_metadata_only_bridge"
                / "expected_error.json"
            )
            target.unlink()

            summary = validate_artifact_body_generation_integration_fixture_root(root)

        self.assertFalse(summary.all_matched)
        self.assertEqual(summary.input_error_cases, 1)
        self.assertEqual(summary.missing_required_file_cases, 1)

    def test_unexpected_json_file(self) -> None:
        with temp_root_copy() as root:
            target = (
                root
                / "valid/valid_minimal_suppressed_metadata_only_bridge"
                / "unexpected_metadata.json"
            )
            target.write_text('{"schema_version":"synthetic_extra_v0"}\n', encoding="utf-8")

            summary = validate_artifact_body_generation_integration_fixture_root(root)

        self.assertFalse(summary.all_matched)
        self.assertEqual(summary.input_error_cases, 1)
        self.assertEqual(summary.unexpected_json_file_cases, 1)

    def test_invalid_runtime_summary_schema_usage_error(self) -> None:
        result = validate_case("invalid/invalid_runtime_summary_schema")

        self.assertTrue(result.matched)
        self.assertEqual(result.expected_status, "usage_error")
        self.assertEqual(result.expected_reason_code, "runtime_summary_schema")

    def test_invalid_cases_match_expected_status_and_reason_codes(self) -> None:
        expected = {
            "invalid_runtime_summary_status": ("fail_closed", "runtime_summary_status"),
            "invalid_runtime_summary_body_detected": (
                "fail_closed",
                "runtime_summary_body_detected",
            ),
            "invalid_runtime_summary_raw_stdout_body": (
                "fail_closed",
                "runtime_summary_raw_stdout_body",
            ),
            "invalid_runtime_summary_raw_stderr_body": (
                "fail_closed",
                "runtime_summary_raw_stderr_body",
            ),
            "invalid_artifact_body_payload_requested": (
                "fail_closed",
                "artifact_body_payload_requested",
            ),
            "invalid_manifest_body_requested": (
                "fail_closed",
                "manifest_body_requested",
            ),
            "invalid_generated_policy_body_requested": (
                "fail_closed",
                "generated_policy_body_requested",
            ),
            "invalid_request_body_present": ("fail_closed", "request_body_present"),
            "invalid_pointer_body_present": ("fail_closed", "pointer_body_present"),
            "invalid_expected_body_present": ("fail_closed", "expected_body_present"),
            "invalid_raw_rows_present": ("fail_closed", "raw_rows_present"),
            "invalid_logits_present": ("fail_closed", "logits_present"),
            "invalid_private_path_present": ("fail_closed", "private_path_present"),
            "invalid_absolute_path_present": ("fail_closed", "absolute_path_present"),
            "invalid_raw_learner_text_present": (
                "fail_closed",
                "raw_learner_text_present",
            ),
            "invalid_file_writing_requested": (
                "fail_closed",
                "file_writing_requested",
            ),
            "invalid_manifest_writer_requested": (
                "fail_closed",
                "manifest_writer_requested",
            ),
            "invalid_artifact_body_generation_unsafe_mode": (
                "fail_closed",
                "artifact_body_generation_unsafe_mode",
            ),
            "invalid_real_data_marker_present": (
                "fail_closed",
                "real_data_marker_present",
            ),
            "invalid_performance_metric_body_present": (
                "fail_closed",
                "performance_metric_body_present",
            ),
        }

        for case_name, (status, reason) in sorted(expected.items()):
            with self.subTest(case=case_name):
                result = validate_case(f"invalid/{case_name}")

                self.assertTrue(result.matched)
                self.assertEqual(result.expected_status, status)
                self.assertEqual(result.expected_reason_code, reason)

    def test_mismatched_expected_status(self) -> None:
        result = validate_case("invalid/invalid_mismatched_expected_status")

        self.assertTrue(result.matched)
        self.assertEqual(result.expected_status, "mismatch")
        self.assertEqual(result.expected_reason_code, "mismatched_expected_status")

    def test_reason_code_counts(self) -> None:
        payload = summarize_artifact_body_generation_integration_fixture_validation(
            validate_artifact_body_generation_integration_fixture_root(FIXTURE_ROOT)
        )
        reason_counts = payload["reason_code_counts"]

        self.assertEqual(reason_counts["none"], 6)
        self.assertEqual(reason_counts["runtime_summary_schema"], 1)
        self.assertEqual(reason_counts["mismatched_expected_status"], 1)
        self.assertEqual(reason_counts["performance_metric_body_present"], 1)
        self.assertEqual(len(reason_counts), 23)

    def test_cli_output_suppresses_bodies(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                MODULE,
                "--fixture-root",
                str(FIXTURE_ROOT),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("matched_cases=28", completed.stdout)
        self.assertIn("reason_code_counts=", completed.stdout)
        assert_safe_output(self, completed.stdout)
        assert_safe_output(self, completed.stderr)

    def test_deterministic_traversal(self) -> None:
        first = summarize_artifact_body_generation_integration_fixture_validation(
            validate_artifact_body_generation_integration_fixture_root(FIXTURE_ROOT)
        )
        second = summarize_artifact_body_generation_integration_fixture_validation(
            validate_artifact_body_generation_integration_fixture_root(FIXTURE_ROOT)
        )

        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))

    def test_no_runtime_invocation(self) -> None:
        payload = summarize_artifact_body_generation_integration_fixture_validation(
            validate_artifact_body_generation_integration_fixture_root(FIXTURE_ROOT)
        )

        self.assertTrue(payload["artifact_body_generation_integration_checked"])
        self.assertTrue(payload["manifest_writer_integration_checked"])
        self.assertTrue(payload["file_writing_checked"])


def validate_case(case_id: str):
    return validate_artifact_body_generation_integration_fixture_case(
        FIXTURE_ROOT / case_id
    )


def case_label(path: Path) -> str:
    return f"{path.parent.name}/{path.name}"


class temp_root_copy:
    def __enter__(self) -> Path:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "fixture_root"
        shutil.copytree(FIXTURE_ROOT, self.root)
        return self.root

    def __exit__(self, exc_type, exc, tb) -> None:
        self._tmp.cleanup()


def assert_safe_output(
    test_case: unittest.TestCase,
    rendered: str,
) -> None:
    assert_no_forbidden_fragments(
        test_case,
        rendered,
        [
            '"fixture_json_body":',
            '"request_body":',
            '"pointer_body":',
            '"expected_body":',
            '"written_file_json_body":',
            '"manifest_body":',
            '"artifact_body_payload":',
            '"generated_policy_body":',
            '"raw_stdout_body":',
            '"raw_stderr_body":',
            '"raw_rows":',
            '"logits":',
            '"probabilities":',
            '"private_path":',
            '"absolute_path":',
            '"raw_learner_text":',
            '"real_participant_data":',
            '"performance_metric_body":',
            "raw GitHub Actions logs",
            "full job output",
            "copied GitHub log blocks",
        ],
    )


if __name__ == "__main__":
    unittest.main()
