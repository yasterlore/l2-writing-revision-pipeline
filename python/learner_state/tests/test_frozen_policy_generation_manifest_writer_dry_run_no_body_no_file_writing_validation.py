from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_manifest_writer_dry_run_no_body_no_file_writing_validation import (
    CASE_SELECTION,
    DEFAULT_FIXTURE_ROOT,
    DRY_RUN_MODE,
    EXPECTED_FAIL_CLOSED_CASE_COUNT,
    EXPECTED_INVALID_CASE_COUNT,
    EXPECTED_MISMATCH_CASE_COUNT,
    EXPECTED_PASS_CASE_COUNT,
    EXPECTED_SELECTED_CASE_COUNT,
    EXPECTED_USAGE_ERROR_CASE_COUNT,
    EXPECTED_VALID_CASE_COUNT,
    MATRIX_NAME,
    MODE,
    SCHEMA_VERSION,
    discover_manifest_writer_dry_run_case_ids,
    format_public_summary,
    run_manifest_writer_dry_run_no_body_no_file_writing_validation,
)
from learner_state.tests.test_frozen_policy_generation_artifact_body_generation_runtime_integration import (
    assert_safe_output,
)

MODULE = (
    "learner_state."
    "frozen_policy_generation_manifest_writer_dry_run_no_body_no_file_writing_validation"
)


class ManifestWriterDryRunNoBodyNoFileWritingValidationTests(unittest.TestCase):
    def test_discovers_fixed_34_case_contract(self) -> None:
        case_ids, reason = discover_manifest_writer_dry_run_case_ids(
            DEFAULT_FIXTURE_ROOT
        )

        self.assertEqual(reason, "none")
        self.assertEqual(len(case_ids), EXPECTED_SELECTED_CASE_COUNT)
        self.assertEqual(count_valid(case_ids), EXPECTED_VALID_CASE_COUNT)
        self.assertEqual(count_invalid(case_ids), EXPECTED_INVALID_CASE_COUNT)

    def test_runner_passes_with_body_free_count_only_summary(self) -> None:
        summary = run_dry_run()
        payload = summary.to_public_dict()

        self.assertEqual(payload["mode"], MODE)
        self.assertEqual(payload["schema_version"], SCHEMA_VERSION)
        self.assertEqual(
            payload["contract_name"],
            "manifest_writer_dry_run_no_body_no_file_writing_contract",
        )
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["reason_code"], "none")
        self.assertEqual(payload["matrix_name"], MATRIX_NAME)
        self.assertEqual(payload["case_selection"], CASE_SELECTION)
        self.assertEqual(payload["selected_case_count"], 34)
        self.assertEqual(payload["selected_valid_case_count"], 4)
        self.assertEqual(payload["selected_invalid_case_count"], 30)
        self.assertEqual(payload["selected_fail_closed_case_count"], 20)
        self.assertEqual(payload["selected_usage_error_case_count"], 5)
        self.assertEqual(payload["selected_mismatch_case_count"], 5)
        self.assertEqual(payload["expected_pass_case_count"], 4)
        self.assertEqual(payload["observed_pass_case_count"], 4)
        self.assertEqual(payload["expected_fail_closed_case_count"], 20)
        self.assertEqual(payload["observed_fail_closed_case_count"], 20)
        self.assertEqual(payload["expected_usage_error_case_count"], 5)
        self.assertEqual(payload["observed_usage_error_case_count"], 5)
        self.assertEqual(payload["expected_mismatch_case_count"], 5)
        self.assertEqual(payload["observed_mismatch_case_count"], 5)
        self.assertEqual(payload["processed_case_count"], 34)
        self.assertEqual(payload["input_error_case_count"], 0)
        self.assertEqual(payload["expected_manifest_writer_invocation_case_count"], 0)
        self.assertEqual(payload["expected_manifest_body_generation_case_count"], 0)
        self.assertEqual(payload["expected_manifest_body_output_case_count"], 0)
        self.assertEqual(payload["expected_file_writing_case_count"], 0)
        self.assertEqual(payload["expected_output_directory_creation_case_count"], 0)
        self.assertEqual(payload["expected_payload_body_emission_case_count"], 0)
        self.assertEqual(payload["expected_artifact_body_payload_output_case_count"], 0)
        self.assertEqual(
            payload["expected_generated_policy_body_output_case_count"], 0
        )
        self.assertEqual(payload["expected_residue_file_count"], 0)
        self.assert_zero_unsafe_counts(payload)
        self.assertEqual(payload["raw_stdout_body_suppressed_count"], 34)
        self.assertEqual(payload["raw_stderr_body_suppressed_count"], 34)
        self.assertTrue(payload["content_suppressed"])
        self.assertTrue(payload["body_suppressed"])
        self.assertTrue(payload["metadata_only_checked"])
        self.assertTrue(payload["synthetic_only_checked"])
        self.assertTrue(payload["no_oracle_checked"])
        self.assertFalse(payload["production_readiness_claimed"])
        self.assertFalse(payload["real_data_readiness_claimed"])
        self.assertFalse(payload["performance_claims_present"])

    def test_cli_output_is_aggregate_only_and_public_safe(self) -> None:
        completed = run_cli()

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn(f"mode={MODE}", completed.stdout)
        self.assertIn("status=pass", completed.stdout)
        self.assertIn(f"case_selection={CASE_SELECTION}", completed.stdout)
        self.assertIn("selected_case_count=34", completed.stdout)
        self.assertIn("observed_pass_case_count=4", completed.stdout)
        self.assertIn("observed_fail_closed_case_count=20", completed.stdout)
        self.assertIn("observed_usage_error_case_count=5", completed.stdout)
        self.assertIn("observed_mismatch_case_count=5", completed.stdout)
        self.assertIn("manifest_writer_invocation_allowed_count=0", completed.stdout)
        self.assertIn("manifest_writer_invoked_count=0", completed.stdout)
        self.assertIn("manifest_body_output_count=0", completed.stdout)
        self.assertIn("output_directory_created_count=0", completed.stdout)
        self.assertIn("residue_file_count=0", completed.stdout)
        self.assertNotIn("minimal_no_body_no_file_writing_contract_metadata", completed.stdout)
        self.assertNotIn("fail_closed_manifest_writer_invocation_allowed", completed.stdout)
        assert_safe_output(self, completed.stdout)
        assert_safe_output(self, completed.stderr)

    def test_public_summary_format_is_stable(self) -> None:
        rendered = format_public_summary(run_dry_run().to_public_dict())
        lines = rendered.splitlines()

        self.assertEqual(lines[0], f"mode={MODE}")
        self.assertIn(f"schema_version={SCHEMA_VERSION}", lines)
        self.assertIn(f"matrix_name={MATRIX_NAME}", lines)
        self.assertIn(f"case_selection={CASE_SELECTION}", lines)
        self.assertIn("selected_case_count=34", lines)
        self.assertIn("production_readiness_claimed=False", lines)
        assert_safe_output(self, rendered)

    def test_missing_summary_only_flag_maps_to_usage_error(self) -> None:
        summary = run_dry_run(summary_only=False)
        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_required_cli_flag")
        self.assertEqual(summary.return_code, 2)

    def test_invalid_dry_run_mode_maps_to_usage_error(self) -> None:
        summary = run_dry_run(dry_run_mode="unsupported-dry-run-mode")
        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "invalid_dry_run_mode")

    def test_missing_no_manifest_writer_flag_maps_to_usage_error(self) -> None:
        summary = run_dry_run(no_manifest_writer=False)
        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_required_cli_flag")

    def test_missing_no_manifest_body_flag_maps_to_usage_error(self) -> None:
        summary = run_dry_run(no_manifest_body=False)
        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_required_cli_flag")

    def test_missing_no_generated_policy_body_flag_maps_to_usage_error(self) -> None:
        summary = run_dry_run(no_generated_policy_body=False)
        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_required_cli_flag")

    def test_missing_no_file_writing_flag_maps_to_usage_error(self) -> None:
        summary = run_dry_run(no_file_writing=False)
        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_required_cli_flag")

    def test_missing_no_output_directory_flag_maps_to_usage_error(self) -> None:
        summary = run_dry_run(no_output_directory=False)
        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_required_cli_flag")

    def test_missing_forbidden_body_fail_closed_flag_maps_to_usage_error(self) -> None:
        summary = run_dry_run(fail_closed_on_forbidden_body=False)
        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_required_cli_flag")

    def test_missing_file_writing_fail_closed_flag_maps_to_usage_error(self) -> None:
        summary = run_dry_run(fail_closed_on_file_writing=False)
        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_required_cli_flag")

    def test_invalid_case_selection_maps_to_usage_error(self) -> None:
        summary = run_dry_run(case_selection="unsupported-selection")
        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "invalid_case_selection")

    def test_missing_fixture_root_maps_to_usage_error(self) -> None:
        summary = run_dry_run(fixture_root=Path("missing-dry-run-root"))
        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_fixture_root")

    def test_missing_case_directory_maps_to_mismatch(self) -> None:
        with temp_root_copy() as root:
            shutil.rmtree(root / "invalid" / "mismatch_source_safety_counts")
            summary = run_dry_run(fixture_root=root)

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "missing_case_directory")

    def test_unknown_case_id_maps_to_mismatch(self) -> None:
        summary = run_with_metadata_change(
            "valid/minimal_no_body_no_file_writing_contract_metadata",
            case_id="valid/unknown_dry_run_case",
        )
        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "selected_case_ids_mismatch")

    def test_valid_schema_mismatch_maps_to_mismatch(self) -> None:
        summary = run_with_metadata_change(
            "valid/minimal_no_body_no_file_writing_contract_metadata",
            schema_version="unsupported_schema",
        )
        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "schema_version_mismatch")

    def test_source_boundary_status_mismatch_maps_to_mismatch(self) -> None:
        summary = run_with_metadata_change(
            "valid/complete_source_boundary_and_safety_flags",
            source_boundary_status="unexpected_status",
        )
        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "source_boundary_status_mismatch")

    def test_source_remote_status_mismatch_maps_to_mismatch(self) -> None:
        summary = run_with_metadata_change(
            "valid/local_manual_status_limitation_notice_present",
            source_remote_status_recorded=True,
        )
        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "source_remote_status_mismatch")

    def test_source_case_count_mismatch_maps_to_mismatch(self) -> None:
        summary = run_with_metadata_change(
            "valid/complete_source_boundary_and_safety_flags",
            source_selected_case_count=22,
        )
        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "source_case_count_mismatch")

    def test_source_observed_counts_mismatch_maps_to_mismatch(self) -> None:
        summary = run_with_metadata_change(
            "valid/non_claims_and_notices_present",
            source_observed_fail_closed_case_count=10,
        )
        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "source_observed_counts_mismatch")

    def test_source_safety_counts_mismatch_maps_to_mismatch(self) -> None:
        summary = run_with_metadata_change(
            "valid/complete_source_boundary_and_safety_flags",
            source_file_writing_enabled_count=1,
        )
        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "source_safety_counts_mismatch")

    def test_manifest_writer_invocation_allowed_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_manifest_writer_invocation_allowed",
            manifest_writer_invocation_allowed=True,
        )
        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "manifest_writer_invocation_allowed")
        self.assertEqual(summary.manifest_writer_invocation_allowed_count, 1)

    def test_manifest_writer_invoked_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_manifest_writer_invoked",
            manifest_writer_invoked=True,
        )
        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "manifest_writer_invoked")
        self.assertEqual(summary.manifest_writer_invoked_count, 1)

    def test_manifest_body_generation_allowed_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_manifest_body_generation_requested",
            manifest_body_generation_allowed=True,
        )
        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "manifest_body_generation_allowed")
        self.assertEqual(summary.manifest_body_generation_allowed_count, 1)

    def test_manifest_body_output_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_manifest_body_present",
            manifest_body_output=True,
        )
        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "manifest_body_output")
        self.assertEqual(summary.manifest_body_output_count, 1)

    def test_generated_policy_body_emitted_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_generated_policy_body_present",
            generated_policy_body_emitted=True,
        )
        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "generated_policy_body_emitted")
        self.assertEqual(summary.generated_policy_body_emitted_count, 1)

    def test_payload_body_emitted_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_payload_body_present",
            payload_body_emitted=True,
        )
        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "payload_body_emitted")
        self.assertEqual(summary.payload_body_emitted_count, 1)

    def test_artifact_body_payload_output_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_artifact_body_payload_present",
            artifact_body_payload_output=True,
        )
        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "artifact_body_payload_output")
        self.assertEqual(summary.artifact_body_payload_output_count, 1)

    def test_request_body_output_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_request_pointer_expected_body_present",
            request_body_output=True,
        )
        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "request_body_output")
        self.assertEqual(summary.request_body_output_count, 1)

    def test_manifest_file_writing_requested_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_manifest_file_writing_requested",
            manifest_file_writing_requested=True,
        )
        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "manifest_file_writing_requested")
        self.assertEqual(summary.manifest_file_writing_requested_count, 1)

    def test_artifact_file_writing_requested_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_artifact_file_writing_requested",
            artifact_file_writing_requested=True,
        )
        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "artifact_file_writing_requested")
        self.assertEqual(summary.artifact_file_writing_requested_count, 1)

    def test_file_writing_enabled_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_file_writing_enabled",
            file_writing_enabled=True,
        )
        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "file_writing_enabled")
        self.assertEqual(summary.file_writing_enabled_count, 1)

    def test_output_directory_created_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_output_directory_created",
            output_directory_created=True,
        )
        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "output_directory_created")
        self.assertEqual(summary.output_directory_created_count, 1)

    def test_private_path_detection_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_private_or_absolute_path_present",
            private_path_detected=True,
        )
        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "private_path_detected")
        self.assertEqual(summary.private_path_detected_count, 1)

    def test_raw_learner_text_detection_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_raw_learner_text_present",
            raw_learner_text_detected=True,
        )
        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "raw_learner_text_detected")
        self.assertEqual(summary.raw_learner_text_detected_count, 1)

    def test_raw_log_or_full_job_output_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_raw_log_or_full_job_output_present",
            raw_log_or_full_job_output_detected=True,
        )
        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "raw_log_or_full_job_output_detected")
        self.assertEqual(summary.raw_log_or_full_job_output_detected_count, 1)

    def test_performance_metric_body_detected_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_performance_metric_body_present",
            performance_metric_body_detected=True,
        )
        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "performance_metric_body_detected")
        self.assertEqual(summary.performance_metric_body_detected_count, 1)

    def test_residue_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_residue_detected",
            residue_file_count=1,
        )
        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "residue_detected")
        self.assertEqual(summary.residue_file_count, 1)

    def test_production_claim_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_production_or_real_data_or_model_performance_claim",
            production_readiness_claimed=True,
        )
        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "production_readiness_claim_detected")
        self.assertTrue(summary.production_readiness_claimed)

    def test_forbidden_metadata_field_maps_to_fail_closed_without_printing_value(
        self,
    ) -> None:
        with temp_root_copy() as root:
            metadata_path = (
                root
                / "invalid"
                / "fail_closed_manifest_body_present"
                / "safety_expectations.json"
            )
            patch_json(metadata_path, manifest_body="blocked_fixture_field")
            summary = run_dry_run(fixture_root=root)
            rendered = format_public_summary(summary.to_public_dict())

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "forbidden_metadata_field")
        self.assertEqual(summary.forbidden_body_detected_count, 1)
        self.assertNotIn("blocked_fixture_field", rendered)
        assert_safe_output(self, rendered)

    def test_fixture_json_not_mutated(self) -> None:
        before = snapshot_fixture_tree(DEFAULT_FIXTURE_ROOT)
        summary = run_dry_run()
        after = snapshot_fixture_tree(DEFAULT_FIXTURE_ROOT)

        self.assertEqual(summary.status, "pass")
        self.assertEqual(before, after)

    def assert_zero_unsafe_counts(self, payload: dict[str, object]) -> None:
        zero_keys = [
            "manifest_writer_invocation_allowed_count",
            "manifest_writer_invoked_count",
            "manifest_body_generation_allowed_count",
            "manifest_body_generation_requested_count",
            "manifest_body_generated_count",
            "manifest_body_output_allowed_count",
            "manifest_body_output_count",
            "generated_policy_body_output_allowed_count",
            "generated_policy_body_emitted_count",
            "artifact_body_payload_output_allowed_count",
            "artifact_body_payload_output_count",
            "payload_body_emission_allowed_count",
            "payload_body_emitted_count",
            "request_body_output_count",
            "pointer_body_output_count",
            "expected_body_output_count",
            "manifest_file_writing_allowed_count",
            "manifest_file_writing_requested_count",
            "manifest_file_written_count",
            "artifact_file_writing_allowed_count",
            "artifact_file_writing_requested_count",
            "artifact_file_written_count",
            "file_writing_allowed_count",
            "file_writing_enabled_count",
            "output_directory_creation_allowed_count",
            "output_directory_created_count",
            "forbidden_body_detected_count",
            "private_path_detected_count",
            "absolute_path_detected_count",
            "raw_learner_text_detected_count",
            "real_data_marker_detected_count",
            "no_oracle_forbidden_field_detected_count",
            "raw_log_or_full_job_output_detected_count",
            "performance_metric_body_detected_count",
            "residue_file_count",
        ]
        for key in zero_keys:
            self.assertEqual(payload[key], 0, key)


def run_dry_run(
    *,
    fixture_root: Path = DEFAULT_FIXTURE_ROOT,
    case_selection: str = CASE_SELECTION,
    summary_only: bool = True,
    dry_run_mode: str = DRY_RUN_MODE,
    no_manifest_writer: bool = True,
    no_manifest_body: bool = True,
    no_generated_policy_body: bool = True,
    no_file_writing: bool = True,
    no_output_directory: bool = True,
    fail_closed_on_forbidden_body: bool = True,
    fail_closed_on_file_writing: bool = True,
):
    return run_manifest_writer_dry_run_no_body_no_file_writing_validation(
        fixture_root,
        case_selection=case_selection,
        summary_only=summary_only,
        dry_run_mode=dry_run_mode,
        no_manifest_writer=no_manifest_writer,
        no_manifest_body=no_manifest_body,
        no_generated_policy_body=no_generated_policy_body,
        no_file_writing=no_file_writing,
        no_output_directory=no_output_directory,
        fail_closed_on_forbidden_body=fail_closed_on_forbidden_body,
        fail_closed_on_file_writing=fail_closed_on_file_writing,
    )


def run_cli() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            MODULE,
            "--fixture-root",
            str(DEFAULT_FIXTURE_ROOT),
            "--case-selection",
            CASE_SELECTION,
            "--summary-only",
            "--dry-run-mode",
            DRY_RUN_MODE,
            "--no-manifest-writer",
            "--no-manifest-body",
            "--no-generated-policy-body",
            "--no-file-writing",
            "--no-output-directory",
            "--fail-closed-on-forbidden-body",
            "--fail-closed-on-file-writing",
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def run_with_metadata_change(target_case_id: str, **changes):
    with temp_root_copy() as root:
        for file_name in (
            "dry_run_input_metadata.json",
            "expected_summary_metadata.json",
            "safety_expectations.json",
        ):
            patch_json(root / target_case_id / file_name, **changes)
        return run_dry_run(fixture_root=root)


def run_with_safety_change(case_id: str, **changes):
    with temp_root_copy() as root:
        metadata_path = root / case_id / "safety_expectations.json"
        patch_json(metadata_path, **changes)
        return run_dry_run(fixture_root=root)


def patch_json(path: Path, **changes) -> None:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    payload.update(changes)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def temp_root_copy():
    class TempRoot:
        def __enter__(self):
            self._tmpdir = tempfile.TemporaryDirectory()
            root = Path(self._tmpdir.name) / DEFAULT_FIXTURE_ROOT.name
            shutil.copytree(DEFAULT_FIXTURE_ROOT, root)
            return root

        def __exit__(self, exc_type, exc_value, traceback):
            self._tmpdir.cleanup()
            return False

    return TempRoot()


def snapshot_fixture_tree(root: Path) -> list[tuple[str, int, int]]:
    return sorted(
        (
            str(path.relative_to(root)),
            path.stat().st_size,
            path.stat().st_mtime_ns,
        )
        for path in root.rglob("*")
        if path.is_file()
    )


def count_valid(case_ids: list[str]) -> int:
    return sum(1 for case_id in case_ids if case_id.startswith("valid/"))


def count_invalid(case_ids: list[str]) -> int:
    return sum(1 for case_id in case_ids if case_id.startswith("invalid/"))


if __name__ == "__main__":
    unittest.main()
