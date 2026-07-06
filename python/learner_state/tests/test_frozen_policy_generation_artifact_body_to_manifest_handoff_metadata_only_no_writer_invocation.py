from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation import (
    CASE_SELECTION,
    DEFAULT_FIXTURE_ROOT,
    EXPECTED_FAIL_CLOSED_CASE_COUNT,
    EXPECTED_INVALID_FAIL_CLOSED_CASE_COUNT,
    EXPECTED_PASS_CASE_COUNT,
    EXPECTED_SELECTED_CASE_COUNT,
    EXPECTED_VALID_METADATA_ONLY_CASE_COUNT,
    MATRIX_NAME,
    MODE,
    SCHEMA_VERSION,
    discover_handoff_case_ids,
    format_public_summary,
    run_artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation,
)
from learner_state.tests.test_frozen_policy_generation_artifact_body_generation_runtime_integration import (
    assert_safe_output,
)

MODULE = (
    "learner_state."
    "frozen_policy_generation_artifact_body_to_manifest_handoff_metadata_only_"
    "no_writer_invocation"
)


class ArtifactBodyToManifestHandoffMetadataOnlyNoWriterInvocationTests(
    unittest.TestCase
):
    def test_discovers_fixed_8_case_contract(self) -> None:
        case_ids, reason = discover_handoff_case_ids(DEFAULT_FIXTURE_ROOT)

        self.assertEqual(reason, "none")
        self.assertEqual(len(case_ids), EXPECTED_SELECTED_CASE_COUNT)
        self.assertEqual(count_valid(case_ids), EXPECTED_VALID_METADATA_ONLY_CASE_COUNT)
        self.assertEqual(count_invalid(case_ids), EXPECTED_INVALID_FAIL_CLOSED_CASE_COUNT)

    def test_runner_passes_with_body_free_count_only_summary(self) -> None:
        summary = run_handoff()
        payload = summary.to_public_dict()

        self.assertEqual(payload["mode"], MODE)
        self.assertEqual(payload["schema_version"], SCHEMA_VERSION)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["reason_code"], "none")
        self.assertEqual(payload["matrix_name"], MATRIX_NAME)
        self.assertEqual(payload["case_selection"], CASE_SELECTION)
        self.assertEqual(payload["selected_case_count"], 8)
        self.assertEqual(payload["selected_valid_metadata_only_case_count"], 3)
        self.assertEqual(payload["selected_invalid_fail_closed_case_count"], 5)
        self.assertEqual(payload["expected_pass_case_count"], 3)
        self.assertEqual(payload["observed_pass_case_count"], 3)
        self.assertEqual(payload["expected_fail_closed_case_count"], 5)
        self.assertEqual(payload["observed_fail_closed_case_count"], 5)
        self.assertEqual(payload["expected_usage_error_case_count"], 0)
        self.assertEqual(payload["observed_usage_error_case_count"], 0)
        self.assertEqual(payload["expected_mismatch_case_count"], 0)
        self.assertEqual(payload["observed_mismatch_case_count"], 0)
        self.assertEqual(payload["processed_case_count"], 8)
        self.assertEqual(payload["input_error_case_count"], 0)
        self.assertEqual(payload["manifest_writer_invoked_count"], 0)
        self.assertEqual(payload["manifest_body_generated_count"], 0)
        self.assertEqual(payload["manifest_body_output_count"], 0)
        self.assertEqual(payload["manifest_file_written_count"], 0)
        self.assertEqual(payload["artifact_file_written_count"], 0)
        self.assertEqual(payload["file_writing_enabled_count"], 0)
        self.assertEqual(payload["payload_body_emitted_count"], 0)
        self.assertEqual(payload["generated_policy_body_emitted_count"], 0)
        self.assertEqual(payload["artifact_body_payload_output_count"], 0)
        self.assertEqual(payload["request_body_output_count"], 0)
        self.assertEqual(payload["pointer_body_output_count"], 0)
        self.assertEqual(payload["expected_body_output_count"], 0)
        self.assertEqual(payload["raw_stdout_body_suppressed_count"], 8)
        self.assertEqual(payload["raw_stderr_body_suppressed_count"], 8)
        self.assertEqual(payload["forbidden_body_detected_count"], 0)
        self.assertEqual(payload["private_path_detected_count"], 0)
        self.assertEqual(payload["absolute_path_detected_count"], 0)
        self.assertEqual(payload["raw_learner_text_detected_count"], 0)
        self.assertEqual(payload["real_data_marker_detected_count"], 0)
        self.assertEqual(payload["no_oracle_forbidden_field_detected_count"], 0)
        self.assertEqual(payload["residue_file_count"], 0)
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
        self.assertIn("selected_case_count=8", completed.stdout)
        self.assertIn("observed_pass_case_count=3", completed.stdout)
        self.assertIn("observed_fail_closed_case_count=5", completed.stdout)
        self.assertIn("manifest_writer_invoked_count=0", completed.stdout)
        self.assertIn("residue_file_count=0", completed.stdout)
        self.assertNotIn("valid_handoff_metadata_minimal_no_writer", completed.stdout)
        self.assertNotIn("invalid_manifest_writer_invoked", completed.stdout)
        assert_safe_output(self, completed.stdout)
        assert_safe_output(self, completed.stderr)

    def test_public_summary_format_is_stable(self) -> None:
        rendered = format_public_summary(run_handoff().to_public_dict())
        lines = rendered.splitlines()

        self.assertEqual(lines[0], f"mode={MODE}")
        self.assertIn(f"schema_version={SCHEMA_VERSION}", lines)
        self.assertIn(f"matrix_name={MATRIX_NAME}", lines)
        self.assertIn(f"case_selection={CASE_SELECTION}", lines)
        self.assertIn("selected_case_count=8", lines)
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
        summary = run_handoff(fixture_root=Path("missing-handoff-fixture-root"))

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_fixture_root")

    def test_missing_case_directory_maps_to_mismatch(self) -> None:
        with temp_root_copy() as root:
            shutil.rmtree(root / "invalid" / "invalid_manifest_writer_invoked")

            summary = run_handoff(fixture_root=root)

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "missing_case_directory")

    def test_duplicate_case_id_maps_to_usage_error(self) -> None:
        with temp_root_copy() as root:
            metadata_path = (
                root
                / "valid"
                / "valid_handoff_metadata_count_only_summary"
                / "case_metadata.json"
            )
            patch_json(metadata_path, case_id="valid/valid_handoff_metadata_minimal_no_writer")

            summary = run_handoff(fixture_root=root)

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "duplicate_case_id")

    def test_unknown_case_id_maps_to_mismatch(self) -> None:
        with temp_root_copy() as root:
            metadata_path = (
                root
                / "valid"
                / "valid_handoff_metadata_minimal_no_writer"
                / "case_metadata.json"
            )
            patch_json(metadata_path, case_id="valid/unknown_handoff_metadata_case")

            summary = run_handoff(fixture_root=root)

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "selected_case_ids_mismatch")

    def test_schema_mismatch_maps_to_mismatch(self) -> None:
        with temp_root_copy() as root:
            metadata_path = (
                root
                / "valid"
                / "valid_handoff_metadata_minimal_no_writer"
                / "case_metadata.json"
            )
            patch_json(metadata_path, schema_version="unsupported_schema")

            summary = run_handoff(fixture_root=root)

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "schema_version_mismatch")

    def test_manifest_writer_invocation_maps_to_fail_closed(self) -> None:
        summary = run_with_actual_flag(
            "invalid/invalid_manifest_writer_invoked",
            writer_invoked_actual=True,
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "manifest_writer_invoked")
        self.assertEqual(summary.manifest_writer_invoked_count, 1)

    def test_manifest_body_generation_maps_to_fail_closed(self) -> None:
        summary = run_with_actual_flag(
            "invalid/invalid_manifest_body_generated",
            manifest_body_generated_actual=True,
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "manifest_body_generated")
        self.assertEqual(summary.manifest_body_generated_count, 1)

    def test_manifest_file_written_maps_to_fail_closed(self) -> None:
        summary = run_with_actual_flag(
            "invalid/invalid_manifest_file_written",
            manifest_file_written_actual=True,
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "manifest_file_written")
        self.assertEqual(summary.manifest_file_written_count, 1)

    def test_artifact_payload_body_output_maps_to_fail_closed(self) -> None:
        summary = run_with_actual_flag(
            "invalid/invalid_artifact_or_payload_body_emitted",
            artifact_body_payload_output_actual=True,
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "artifact_body_payload_output")
        self.assertEqual(summary.artifact_body_payload_output_count, 1)

    def test_private_path_detection_maps_to_fail_closed(self) -> None:
        summary = run_with_actual_flag(
            "invalid/invalid_private_or_absolute_path_detected",
            private_path_detected_actual=True,
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "private_path_detected")
        self.assertEqual(summary.private_path_detected_count, 1)

    def test_residue_maps_to_fail_closed(self) -> None:
        summary = run_with_actual_flag(
            "valid/valid_handoff_metadata_no_residue",
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
                / "invalid_manifest_body_generated"
                / "safe_handoff_metadata.json"
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


def run_handoff(
    *,
    fixture_root: Path = DEFAULT_FIXTURE_ROOT,
    case_selection: str = CASE_SELECTION,
    summary_only: bool = True,
    no_manifest_writer: bool = True,
    no_file_writing: bool = True,
    fail_closed_on_forbidden_body: bool = True,
):
    return run_artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation(
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


def run_with_actual_flag(case_id: str, **changes):
    with temp_root_copy() as root:
        metadata_path = root / case_id / "safe_handoff_metadata.json"
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
