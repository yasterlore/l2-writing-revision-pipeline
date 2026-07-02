from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_artifact_body_generation_runtime_integration import (
    DEFAULT_FIXTURE_CASE,
    DEFAULT_FIXTURE_ROOT,
    MODE,
    PLAN_ONLY_BRIDGE_MODE,
    RUNTIME_SCHEMA_VERSION,
    SAFE_METADATA_RUNTIME_SCHEMA_VERSION,
    SAFE_METADATA_SMOKE_MODE,
    format_public_summary,
    run_artifact_body_generation_runtime_integration_for_fixture_case,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

MODULE = (
    "learner_state."
    "frozen_policy_generation_artifact_body_generation_runtime_integration"
)
SELECTED_CASE = DEFAULT_FIXTURE_CASE
SAFE_METADATA_FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_body_generation_integration"
    "_planned_safe_metadata_v0_2"
)
SAFE_METADATA_SELECTED_CASE = "valid/valid_safe_metadata_explicit_runtime_bridge"


class ArtifactBodyGenerationRuntimeIntegrationTests(unittest.TestCase):
    def test_plan_only_bridge_valid_case_pass(self) -> None:
        summary = run_runtime()
        payload = summary.to_public_dict()

        self.assertEqual(payload["mode"], MODE)
        self.assertEqual(payload["runtime_schema_version"], RUNTIME_SCHEMA_VERSION)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["reason_code"], "none")
        self.assertEqual(payload["exit_code_category"], "zero")
        self.assertEqual(payload["case_id"], SELECTED_CASE)
        self.assertEqual(payload["integration_mode"], PLAN_ONLY_BRIDGE_MODE)
        self.assertFalse(payload["artifact_body_runtime_invoked"])
        self.assertEqual(payload["artifact_body_runtime_mode"], "not_invoked")
        self.assertTrue(payload["content_suppressed"])
        self.assertTrue(payload["body_suppressed"])
        self.assertTrue(payload["summary_only"])
        self.assertFalse(payload["request_body_detected"])
        self.assertFalse(payload["pointer_body_detected"])
        self.assertFalse(payload["expected_body_detected"])
        self.assertFalse(payload["artifact_body_payload_detected"])
        self.assertFalse(payload["manifest_body_detected"])
        self.assertFalse(payload["generated_policy_body_detected"])
        self.assertTrue(payload["raw_stdout_body_suppressed"])
        self.assertTrue(payload["raw_stderr_body_suppressed"])
        self.assertFalse(payload["file_writing_enabled"])
        self.assertFalse(payload["file_writing_detected"])
        self.assertFalse(payload["manifest_writer_invoked"])
        self.assertFalse(payload["artifact_file_written"])
        self.assertFalse(payload["manifest_file_written"])
        self.assertTrue(payload["runtime_safety_scan_passed"])
        self.assertFalse(payload["runtime_fail_closed"])
        self.assertEqual(payload["metadata_file_count"], 7)
        self.assertEqual(payload["unsafe_signal_count"], 0)

    def test_cli_explicit_mode_behavior(self) -> None:
        completed = run_cli()

        self.assertEqual(completed.returncode, 0)
        self.assertIn("status=pass", completed.stdout)
        self.assertIn("integration_mode=plan-only-bridge", completed.stdout)
        self.assertIn("artifact_body_runtime_invoked=False", completed.stdout)
        assert_safe_output(self, completed.stdout)
        assert_safe_output(self, completed.stderr)

    def test_reserved_suppressed_smoke_usage_error(self) -> None:
        summary = run_runtime(mode="suppressed-smoke")

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "unsupported_mode")

    def test_safe_metadata_smoke_primary_valid_case_pass(self) -> None:
        summary = run_safe_metadata_runtime()
        payload = summary.to_public_dict()

        self.assertEqual(payload["mode"], MODE)
        self.assertEqual(
            payload["runtime_schema_version"],
            SAFE_METADATA_RUNTIME_SCHEMA_VERSION,
        )
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["reason_code"], "none")
        self.assertEqual(payload["exit_code_category"], "zero")
        self.assertEqual(payload["case_id"], SAFE_METADATA_SELECTED_CASE)
        self.assertEqual(payload["integration_mode"], SAFE_METADATA_SMOKE_MODE)
        self.assertTrue(payload["planned_root"])
        self.assertTrue(payload["safe_metadata_v0_2_planned_checked"])
        self.assertFalse(payload["artifact_body_runtime_invoked"])
        self.assertEqual(payload["artifact_body_runtime_mode"], "not_invoked")
        self.assertFalse(payload["artifact_body_payload_available"])
        self.assertFalse(payload["artifact_body_payload_emitted"])
        self.assertTrue(payload["safe_metadata_body_available"])
        self.assertEqual(payload["safe_metadata_body_field_count"], 4)
        self.assertTrue(payload["content_suppressed"])
        self.assertTrue(payload["body_suppressed"])
        self.assertTrue(payload["summary_only"])
        self.assertFalse(payload["request_body_detected"])
        self.assertFalse(payload["artifact_body_payload_detected"])
        self.assertFalse(payload["manifest_body_detected"])
        self.assertFalse(payload["generated_policy_body_detected"])
        self.assertTrue(payload["raw_stdout_body_suppressed"])
        self.assertTrue(payload["raw_stderr_body_suppressed"])
        self.assertFalse(payload["file_writing_enabled"])
        self.assertFalse(payload["file_writing_detected"])
        self.assertFalse(payload["manifest_writer_invoked"])
        self.assertFalse(payload["artifact_file_written"])
        self.assertFalse(payload["manifest_file_written"])
        self.assertTrue(payload["runtime_safety_scan_passed"])
        self.assertFalse(payload["runtime_fail_closed"])
        self.assertFalse(payload["production_readiness_claimed"])
        self.assertFalse(payload["real_data_readiness_claimed"])
        self.assertFalse(payload["performance_claims_present"])
        self.assertEqual(payload["metadata_file_count"], 7)
        self.assertEqual(payload["unsafe_signal_count"], 0)

    def test_safe_metadata_cli_output_public_safe(self) -> None:
        completed = run_safe_metadata_cli()

        self.assertEqual(completed.returncode, 0)
        self.assertIn(
            "runtime_schema_version="
            "learner_state_frozen_policy_generation_artifact_body_generation_"
            "runtime_integration_v0.2",
            completed.stdout,
        )
        self.assertIn("status=pass", completed.stdout)
        self.assertIn("integration_mode=safe-metadata-smoke", completed.stdout)
        self.assertIn("artifact_body_runtime_invoked=False", completed.stdout)
        self.assertIn("manifest_writer_invoked=False", completed.stdout)
        self.assertIn("file_writing_enabled=False", completed.stdout)
        self.assertIn("unsafe_signal_count=0", completed.stdout)
        assert_safe_output(self, completed.stdout)
        assert_safe_output(self, completed.stderr)

    def test_unsupported_mode_usage_error(self) -> None:
        summary = run_runtime(mode="unsupported-mode")

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "unsupported_mode")

    def test_missing_fixture_usage_error(self) -> None:
        summary = run_runtime(fixture_case="valid/missing_case")

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_fixture")

    def test_safe_metadata_missing_fixture_root_usage_error(self) -> None:
        summary = run_safe_metadata_runtime(fixture_root=Path("missing_fixture_root"))

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_fixture")
        self.assertEqual(summary.runtime_schema_version, SAFE_METADATA_RUNTIME_SCHEMA_VERSION)

    def test_safe_metadata_missing_fixture_case_usage_error(self) -> None:
        summary = run_safe_metadata_runtime(fixture_case="valid/missing_case")

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_fixture")

    def test_missing_required_metadata_file_usage_error(self) -> None:
        with temp_root_copy() as root:
            (root / SELECTED_CASE / "expected_error.json").unlink()

            summary = run_runtime(fixture_root=root)

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_required_metadata_file")

    def test_runtime_summary_status_fail_closed(self) -> None:
        self.assert_mutation_fail_closed(
            "actual_invocation_runtime_summary_metadata.json",
            "status",
            "fail_closed",
            "runtime_summary_status",
        )

    def test_request_body_sentinel_fail_closed(self) -> None:
        self.assert_mutation_fail_closed(
            "artifact_body_request_metadata.json",
            "request_body_present",
            True,
            "request_body_present",
        )

    def test_pointer_body_sentinel_fail_closed(self) -> None:
        self.assert_mutation_fail_closed(
            "artifact_body_pointer_metadata.json",
            "pointer_body_present",
            True,
            "pointer_body_present",
        )

    def test_expected_body_sentinel_fail_closed(self) -> None:
        self.assert_mutation_fail_closed(
            "artifact_body_generation_metadata.json",
            "expected_body_present",
            True,
            "expected_body_present",
        )

    def test_artifact_body_payload_sentinel_fail_closed(self) -> None:
        self.assert_mutation_fail_closed(
            "artifact_body_generation_metadata.json",
            "artifact_body_payload_present",
            True,
            "artifact_body_payload_detected",
        )

    def test_safe_metadata_artifact_body_payload_marker_fail_closed(self) -> None:
        self.assert_safe_metadata_mutation(
            "artifact_body_generation_metadata.json",
            "artifact_body_payload_present",
            True,
            "fail_closed",
            "artifact_body_payload_present",
        )

    def test_safe_metadata_request_body_marker_fail_closed(self) -> None:
        self.assert_safe_metadata_mutation(
            "artifact_body_request_metadata.json",
            "request_body_present",
            True,
            "fail_closed",
            "request_body_present",
        )

    def test_manifest_body_sentinel_fail_closed(self) -> None:
        self.assert_mutation_fail_closed(
            "artifact_body_generation_metadata.json",
            "manifest_body_present",
            True,
            "manifest_body_detected",
        )

    def test_generated_policy_body_sentinel_fail_closed(self) -> None:
        self.assert_mutation_fail_closed(
            "artifact_body_generation_metadata.json",
            "generated_policy_body_present",
            True,
            "generated_policy_body_detected",
        )

    def test_raw_stdout_body_sentinel_fail_closed(self) -> None:
        self.assert_mutation_fail_closed(
            "artifact_body_generation_metadata.json",
            "raw_stdout_body_present",
            True,
            "raw_stdout_body_detected",
        )

    def test_raw_stderr_body_sentinel_fail_closed(self) -> None:
        self.assert_mutation_fail_closed(
            "artifact_body_generation_metadata.json",
            "raw_stderr_body_present",
            True,
            "raw_stderr_body_detected",
        )

    def test_raw_rows_sentinel_fail_closed(self) -> None:
        self.assert_mutation_fail_closed(
            "artifact_body_generation_metadata.json",
            "raw_rows_present",
            True,
            "raw_rows_detected",
        )

    def test_logits_sentinel_fail_closed(self) -> None:
        self.assert_mutation_fail_closed(
            "artifact_body_generation_metadata.json",
            "logits_present",
            True,
            "logits_detected",
        )

    def test_private_path_sentinel_fail_closed(self) -> None:
        self.assert_mutation_fail_closed(
            "artifact_body_pointer_metadata.json",
            "private_path_present",
            True,
            "private_path_detected",
        )

    def test_absolute_path_sentinel_fail_closed(self) -> None:
        self.assert_mutation_fail_closed(
            "artifact_body_pointer_metadata.json",
            "absolute_path_present",
            True,
            "absolute_path_detected",
        )

    def test_raw_learner_text_sentinel_fail_closed(self) -> None:
        self.assert_mutation_fail_closed(
            "artifact_body_pointer_metadata.json",
            "raw_learner_text_present",
            True,
            "raw_learner_text_detected",
        )

    def test_real_data_marker_fail_closed(self) -> None:
        self.assert_mutation_fail_closed(
            "artifact_body_request_metadata.json",
            "real_data_marker_present",
            True,
            "real_data_marker_detected",
        )

    def test_performance_metric_body_fail_closed(self) -> None:
        self.assert_mutation_fail_closed(
            "artifact_body_request_metadata.json",
            "performance_metric_body_present",
            True,
            "performance_metric_body_detected",
        )

    def test_file_writing_detected_fail_closed(self) -> None:
        self.assert_mutation_fail_closed(
            "artifact_body_generation_metadata.json",
            "artifact_file_written",
            True,
            "file_writing_detected",
        )

    def test_safe_metadata_file_writing_requested_fail_closed(self) -> None:
        self.assert_safe_metadata_mutation(
            "artifact_body_request_metadata.json",
            "file_writing_requested",
            True,
            "fail_closed",
            "file_writing_requested",
        )

    def test_manifest_writer_invocation_fail_closed(self) -> None:
        self.assert_mutation_fail_closed(
            "artifact_body_generation_metadata.json",
            "manifest_file_written",
            True,
            "manifest_writer_invoked",
        )

    def test_safe_metadata_manifest_writer_requested_fail_closed(self) -> None:
        self.assert_safe_metadata_mutation(
            "artifact_body_request_metadata.json",
            "manifest_writer_requested",
            True,
            "fail_closed",
            "manifest_writer_requested",
        )

    def test_safe_metadata_unsupported_schema_usage_error(self) -> None:
        self.assert_safe_metadata_mutation(
            "case_metadata.json",
            "schema_version",
            "unsupported_safe_metadata_fixture_schema_v0.0",
            "usage_error",
            "unsupported_schema",
        )

    def test_safe_metadata_mismatched_expected_status(self) -> None:
        self.assert_safe_metadata_mutation(
            "expected_integration_summary.json",
            "expected_status_mismatch",
            True,
            "mismatch",
            "mismatched_expected_status",
        )

    def test_output_suppresses_unsafe_values(self) -> None:
        with temp_root_copy() as root:
            mutate(
                root,
                "artifact_body_request_metadata.json",
                "request_body_present",
                True,
            )

            summary = run_runtime(fixture_root=root)
            rendered = format_public_summary(summary.to_public_dict())

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "request_body_present")
        assert_safe_output(self, rendered)

    def test_no_runtime_invocation_in_plan_only_mode(self) -> None:
        payload = run_runtime().to_public_dict()

        self.assertFalse(payload["artifact_body_runtime_invoked"])
        self.assertEqual(payload["artifact_body_runtime_mode"], "not_invoked")
        self.assertFalse(payload["manifest_writer_invoked"])
        self.assertFalse(payload["file_writing_enabled"])

    def test_no_runtime_invocation_in_safe_metadata_mode(self) -> None:
        payload = run_safe_metadata_runtime().to_public_dict()

        self.assertFalse(payload["artifact_body_runtime_invoked"])
        self.assertEqual(payload["artifact_body_runtime_mode"], "not_invoked")
        self.assertFalse(payload["manifest_writer_invoked"])
        self.assertFalse(payload["file_writing_enabled"])

    def test_no_file_residue(self) -> None:
        before = sorted(path.relative_to(DEFAULT_FIXTURE_ROOT) for path in DEFAULT_FIXTURE_ROOT.rglob("*"))

        summary = run_runtime()

        after = sorted(path.relative_to(DEFAULT_FIXTURE_ROOT) for path in DEFAULT_FIXTURE_ROOT.rglob("*"))
        self.assertEqual(summary.status, "pass")
        self.assertEqual(before, after)

    def test_safe_metadata_no_file_residue(self) -> None:
        before = sorted(
            path.relative_to(SAFE_METADATA_FIXTURE_ROOT)
            for path in SAFE_METADATA_FIXTURE_ROOT.rglob("*")
        )

        summary = run_safe_metadata_runtime()

        after = sorted(
            path.relative_to(SAFE_METADATA_FIXTURE_ROOT)
            for path in SAFE_METADATA_FIXTURE_ROOT.rglob("*")
        )
        self.assertEqual(summary.status, "pass")
        self.assertEqual(before, after)

    def test_deterministic_output(self) -> None:
        first = format_public_summary(run_runtime().to_public_dict())
        second = format_public_summary(run_runtime().to_public_dict())

        self.assertEqual(first, second)

    def assert_mutation_fail_closed(
        self,
        file_name: str,
        field_name: str,
        value: object,
        reason_code: str,
    ) -> None:
        with temp_root_copy() as root:
            mutate(root, file_name, field_name, value)

            summary = run_runtime(fixture_root=root)

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, reason_code)
        self.assertEqual(summary.exit_code_category, "fail_closed")
        self.assertTrue(summary.runtime_fail_closed)
        self.assertFalse(summary.runtime_safety_scan_passed)

    def assert_safe_metadata_mutation(
        self,
        file_name: str,
        field_name: str,
        value: object,
        expected_status: str,
        expected_reason_code: str,
    ) -> None:
        with temp_root_copy(SAFE_METADATA_FIXTURE_ROOT) as root:
            mutate(root, file_name, field_name, value, case_id=SAFE_METADATA_SELECTED_CASE)

            summary = run_safe_metadata_runtime(fixture_root=root)

        self.assertEqual(summary.status, expected_status)
        self.assertEqual(summary.reason_code, expected_reason_code)
        if expected_status == "fail_closed":
            self.assertEqual(summary.exit_code_category, "fail_closed")
            self.assertTrue(summary.runtime_fail_closed)
            self.assertFalse(summary.runtime_safety_scan_passed)


def run_runtime(
    *,
    fixture_root: Path = DEFAULT_FIXTURE_ROOT,
    fixture_case: str = SELECTED_CASE,
    mode: str = PLAN_ONLY_BRIDGE_MODE,
):
    return run_artifact_body_generation_runtime_integration_for_fixture_case(
        fixture_root,
        fixture_case,
        mode=mode,
        summary_only=True,
        no_file_writing=True,
        no_manifest_writer=True,
        fail_closed_on_unsafe_output=True,
    )


def run_safe_metadata_runtime(
    *,
    fixture_root: Path = SAFE_METADATA_FIXTURE_ROOT,
    fixture_case: str = SAFE_METADATA_SELECTED_CASE,
):
    return run_artifact_body_generation_runtime_integration_for_fixture_case(
        fixture_root,
        fixture_case,
        mode=SAFE_METADATA_SMOKE_MODE,
        summary_only=True,
        no_file_writing=True,
        no_manifest_writer=True,
        fail_closed_on_unsafe_output=True,
    )


def run_cli() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            MODULE,
            "--fixture-root",
            str(DEFAULT_FIXTURE_ROOT),
            "--fixture-case",
            SELECTED_CASE,
            "--mode",
            PLAN_ONLY_BRIDGE_MODE,
            "--summary-only",
            "--no-file-writing",
            "--no-manifest-writer",
            "--fail-closed-on-unsafe-output",
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def run_safe_metadata_cli() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            MODULE,
            "--fixture-root",
            str(SAFE_METADATA_FIXTURE_ROOT),
            "--fixture-case",
            SAFE_METADATA_SELECTED_CASE,
            "--mode",
            SAFE_METADATA_SMOKE_MODE,
            "--summary-only",
            "--no-file-writing",
            "--no-manifest-writer",
            "--fail-closed-on-unsafe-output",
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def mutate(
    root: Path,
    file_name: str,
    field_name: str,
    value: object,
    *,
    case_id: str = SELECTED_CASE,
) -> None:
    path = root / case_id / file_name
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload[field_name] = value
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


class temp_root_copy:
    def __init__(self, source_root: Path = DEFAULT_FIXTURE_ROOT) -> None:
        self.source_root = source_root

    def __enter__(self) -> Path:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "fixture_root"
        shutil.copytree(self.source_root, self.root)
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
            "actions-log-unsafe-marker",
            "job-output-unsafe-marker",
            "copied-log-block-unsafe-marker",
        ],
    )


if __name__ == "__main__":
    unittest.main()
