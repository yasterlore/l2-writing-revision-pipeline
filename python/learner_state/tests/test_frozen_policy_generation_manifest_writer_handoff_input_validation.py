from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_manifest_writer_handoff_input_validation import (
    CASE_SELECTION,
    DEFAULT_FIXTURE_ROOT,
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
    discover_manifest_writer_handoff_case_ids,
    format_public_summary,
    run_manifest_writer_handoff_input_validation,
)
from learner_state.tests.test_frozen_policy_generation_artifact_body_generation_runtime_integration import (
    assert_safe_output,
)

MODULE = "learner_state.frozen_policy_generation_manifest_writer_handoff_input_validation"


class ManifestWriterHandoffInputValidationTests(unittest.TestCase):
    def test_discovers_fixed_23_case_contract(self) -> None:
        case_ids, reason = discover_manifest_writer_handoff_case_ids(
            DEFAULT_FIXTURE_ROOT
        )

        self.assertEqual(reason, "none")
        self.assertEqual(len(case_ids), EXPECTED_SELECTED_CASE_COUNT)
        self.assertEqual(count_valid(case_ids), EXPECTED_VALID_CASE_COUNT)
        self.assertEqual(count_invalid(case_ids), EXPECTED_INVALID_CASE_COUNT)

    def test_runner_passes_with_body_free_count_only_summary(self) -> None:
        summary = run_handoff()
        payload = summary.to_public_dict()

        self.assertEqual(payload["mode"], MODE)
        self.assertEqual(payload["schema_version"], SCHEMA_VERSION)
        self.assertEqual(payload["contract_name"], "manifest_writer_handoff_input_contract")
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["reason_code"], "none")
        self.assertEqual(payload["matrix_name"], MATRIX_NAME)
        self.assertEqual(payload["case_selection"], CASE_SELECTION)
        self.assertEqual(payload["selected_case_count"], 23)
        self.assertEqual(payload["selected_valid_case_count"], 3)
        self.assertEqual(payload["selected_invalid_case_count"], 20)
        self.assertEqual(payload["selected_fail_closed_case_count"], 11)
        self.assertEqual(payload["selected_usage_error_case_count"], 5)
        self.assertEqual(payload["selected_mismatch_case_count"], 4)
        self.assertEqual(payload["expected_pass_case_count"], 3)
        self.assertEqual(payload["observed_pass_case_count"], 3)
        self.assertEqual(payload["expected_fail_closed_case_count"], 11)
        self.assertEqual(payload["observed_fail_closed_case_count"], 11)
        self.assertEqual(payload["expected_usage_error_case_count"], 5)
        self.assertEqual(payload["observed_usage_error_case_count"], 5)
        self.assertEqual(payload["expected_mismatch_case_count"], 4)
        self.assertEqual(payload["observed_mismatch_case_count"], 4)
        self.assertEqual(payload["processed_case_count"], 23)
        self.assertEqual(payload["input_error_case_count"], 0)
        self.assertEqual(payload["expected_manifest_writer_invocation_case_count"], 0)
        self.assertEqual(payload["expected_manifest_body_generation_case_count"], 0)
        self.assertEqual(payload["expected_file_writing_case_count"], 0)
        self.assertEqual(payload["expected_payload_body_emission_case_count"], 0)
        self.assertEqual(payload["expected_artifact_body_payload_output_case_count"], 0)
        self.assertEqual(
            payload["expected_generated_policy_body_output_case_count"], 0
        )
        self.assertEqual(payload["expected_residue_file_count"], 0)
        self.assert_zero_unsafe_counts(payload)
        self.assertEqual(payload["raw_stdout_body_suppressed_count"], 23)
        self.assertEqual(payload["raw_stderr_body_suppressed_count"], 23)
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
        self.assertIn("selected_case_count=23", completed.stdout)
        self.assertIn("observed_pass_case_count=3", completed.stdout)
        self.assertIn("observed_fail_closed_case_count=11", completed.stdout)
        self.assertIn("observed_usage_error_case_count=5", completed.stdout)
        self.assertIn("observed_mismatch_case_count=4", completed.stdout)
        self.assertIn("manifest_writer_invoked_count=0", completed.stdout)
        self.assertIn("residue_file_count=0", completed.stdout)
        self.assertNotIn("minimal_handoff_input_metadata_only", completed.stdout)
        self.assertNotIn("fail_closed_manifest_writer_invocation_requested", completed.stdout)
        assert_safe_output(self, completed.stdout)
        assert_safe_output(self, completed.stderr)

    def test_public_summary_format_is_stable(self) -> None:
        rendered = format_public_summary(run_handoff().to_public_dict())
        lines = rendered.splitlines()

        self.assertEqual(lines[0], f"mode={MODE}")
        self.assertIn(f"schema_version={SCHEMA_VERSION}", lines)
        self.assertIn(f"matrix_name={MATRIX_NAME}", lines)
        self.assertIn(f"case_selection={CASE_SELECTION}", lines)
        self.assertIn("selected_case_count=23", lines)
        self.assertIn("production_readiness_claimed=False", lines)
        assert_safe_output(self, rendered)

    def test_missing_summary_only_flag_maps_to_usage_error(self) -> None:
        summary = run_handoff(summary_only=False)

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_required_cli_flag")
        self.assertEqual(summary.return_code, 2)

    def test_missing_no_manifest_writer_flag_maps_to_usage_error(self) -> None:
        summary = run_handoff(no_manifest_writer=False)

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_required_cli_flag")

    def test_missing_no_file_writing_flag_maps_to_usage_error(self) -> None:
        summary = run_handoff(no_file_writing=False)

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_required_cli_flag")

    def test_missing_fail_closed_flag_maps_to_usage_error(self) -> None:
        summary = run_handoff(fail_closed_on_forbidden_body=False)

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_required_cli_flag")

    def test_invalid_case_selection_maps_to_usage_error(self) -> None:
        summary = run_handoff(case_selection="unsupported-selection")

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "invalid_case_selection")

    def test_missing_fixture_root_maps_to_usage_error(self) -> None:
        summary = run_handoff(fixture_root=Path("missing-manifest-handoff-root"))

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_fixture_root")

    def test_missing_case_directory_maps_to_mismatch(self) -> None:
        with temp_root_copy() as root:
            shutil.rmtree(root / "invalid" / "mismatch_count_summary_mismatch")

            summary = run_handoff(fixture_root=root)

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "missing_case_directory")

    def test_unknown_case_id_maps_to_mismatch(self) -> None:
        summary = run_with_metadata_change(
            "valid/minimal_handoff_input_metadata_only",
            case_id="valid/unknown_manifest_handoff_case",
        )

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "selected_case_ids_mismatch")

    def test_valid_schema_mismatch_maps_to_mismatch(self) -> None:
        summary = run_with_metadata_change(
            "valid/minimal_handoff_input_metadata_only",
            schema_version="unsupported_schema",
        )

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "schema_version_mismatch")

    def test_source_case_count_mismatch_maps_to_mismatch(self) -> None:
        summary = run_with_metadata_change(
            "valid/complete_handoff_input_count_summary",
            source_selected_case_count=7,
        )

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "source_case_count_mismatch")

    def test_source_remote_status_mismatch_maps_to_mismatch(self) -> None:
        summary = run_with_metadata_change(
            "valid/non_claims_and_notices_present",
            source_remote_status_recorded=False,
        )

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "source_remote_status_mismatch")

    def test_manifest_writer_invocation_requested_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_manifest_writer_invocation_requested",
            manifest_writer_invocation_requested=True,
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "manifest_writer_invocation_requested")
        self.assertEqual(summary.manifest_writer_invocation_requested_count, 1)

    def test_manifest_writer_invoked_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_manifest_writer_invocation_requested",
            manifest_writer_invoked=True,
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "manifest_writer_invoked")
        self.assertEqual(summary.manifest_writer_invoked_count, 1)

    def test_manifest_body_generation_requested_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_manifest_body_generation_requested",
            manifest_body_generation_requested=True,
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "manifest_body_generation_requested")
        self.assertEqual(summary.manifest_body_generation_requested_count, 1)

    def test_manifest_body_output_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_manifest_body_present",
            manifest_body_output=True,
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "manifest_body_output")
        self.assertEqual(summary.manifest_body_output_count, 1)

    def test_file_writing_enabled_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_file_writing_requested",
            file_writing_enabled=True,
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "file_writing_enabled")
        self.assertEqual(summary.file_writing_enabled_count, 1)

    def test_payload_body_emission_requested_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_payload_body_present",
            payload_body_emission_requested=True,
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "payload_body_emission_requested")
        self.assertEqual(summary.payload_body_emission_requested_count, 1)

    def test_generated_policy_body_emitted_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_generated_policy_body_present",
            generated_policy_body_emitted=True,
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "generated_policy_body_emitted")
        self.assertEqual(summary.generated_policy_body_emitted_count, 1)

    def test_private_path_detection_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_private_or_absolute_path_present",
            private_path_detected=True,
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "private_path_detected")
        self.assertEqual(summary.private_path_detected_count, 1)

    def test_raw_log_or_full_job_output_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_raw_log_or_full_job_output_present",
            raw_log_or_full_job_output_detected=True,
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "raw_log_or_full_job_output_detected")
        self.assertEqual(summary.raw_log_or_full_job_output_detected_count, 1)

    def test_residue_maps_to_fail_closed(self) -> None:
        summary = run_with_safety_change(
            "invalid/fail_closed_residue_detected",
            residue_file_count=1,
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "residue_detected")
        self.assertEqual(summary.residue_file_count, 1)

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

            summary = run_handoff(fixture_root=root)
            rendered = format_public_summary(summary.to_public_dict())

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "forbidden_metadata_field")
        self.assertEqual(summary.forbidden_body_detected_count, 1)
        self.assertNotIn("blocked_fixture_field", rendered)
        assert_safe_output(self, rendered)

    def test_fixture_json_not_mutated(self) -> None:
        before = snapshot_fixture_tree(DEFAULT_FIXTURE_ROOT)

        summary = run_handoff()

        after = snapshot_fixture_tree(DEFAULT_FIXTURE_ROOT)
        self.assertEqual(summary.status, "pass")
        self.assertEqual(before, after)

    def assert_zero_unsafe_counts(self, payload: dict[str, object]) -> None:
        zero_keys = [
            "manifest_writer_invocation_requested_count",
            "manifest_writer_invoked_count",
            "manifest_body_generation_requested_count",
            "manifest_body_generated_count",
            "manifest_body_output_count",
            "manifest_file_writing_requested_count",
            "manifest_file_written_count",
            "artifact_file_writing_requested_count",
            "artifact_file_written_count",
            "file_writing_enabled_count",
            "payload_body_emission_requested_count",
            "payload_body_emitted_count",
            "artifact_body_payload_output_count",
            "generated_policy_body_emitted_count",
            "request_body_output_count",
            "pointer_body_output_count",
            "expected_body_output_count",
            "forbidden_body_detected_count",
            "private_path_detected_count",
            "absolute_path_detected_count",
            "raw_learner_text_detected_count",
            "real_data_marker_detected_count",
            "no_oracle_forbidden_field_detected_count",
            "raw_log_or_full_job_output_detected_count",
            "residue_file_count",
        ]
        for key in zero_keys:
            self.assertEqual(payload[key], 0, key)


def run_handoff(
    *,
    fixture_root: Path = DEFAULT_FIXTURE_ROOT,
    case_selection: str = CASE_SELECTION,
    summary_only: bool = True,
    no_manifest_writer: bool = True,
    no_file_writing: bool = True,
    fail_closed_on_forbidden_body: bool = True,
):
    return run_manifest_writer_handoff_input_validation(
        fixture_root,
        case_selection=case_selection,
        summary_only=summary_only,
        no_manifest_writer=no_manifest_writer,
        no_file_writing=no_file_writing,
        fail_closed_on_forbidden_body=fail_closed_on_forbidden_body,
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
            "--no-manifest-writer",
            "--no-file-writing",
            "--fail-closed-on-forbidden-body",
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def run_with_metadata_change(target_case_id: str, **changes):
    with temp_root_copy() as root:
        for file_name in (
            "handoff_input_metadata.json",
            "expected_summary_metadata.json",
            "safety_expectations.json",
        ):
            patch_json(root / target_case_id / file_name, **changes)
        return run_handoff(fixture_root=root)


def run_with_safety_change(case_id: str, **changes):
    with temp_root_copy() as root:
        metadata_path = root / case_id / "safety_expectations.json"
        patch_json(metadata_path, **changes)
        return run_handoff(fixture_root=root)


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
