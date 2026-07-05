from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke import (
    CASE_SELECTION_ALL_VALID,
    DEFAULT_FIXTURE_ROOT,
    MODE,
    SCHEMA_VERSION,
    discover_all_valid_case_ids,
    format_public_summary,
    run_multi_case_runtime_smoke,
)
from learner_state.frozen_policy_generation_artifact_body_generation_runtime_integration import (
    ACTUAL_CONTROLLED_ARTIFACT_BODY_RUNTIME_INVOCATION_MODE,
    ACTUAL_CONTROLLED_RUNTIME_SCHEMA_VERSION,
    ARTIFACT_BODY_RUNTIME_INVOCATION_MODE,
    RUNTIME_INVOCATION_RUNTIME_SCHEMA_VERSION,
    run_artifact_body_generation_runtime_integration_for_fixture_case,
)
from learner_state.frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validation import (
    CLI_METADATA_FILE,
    REQUEST_METADATA_FILE,
    RESIDUE_POLICY_FILE,
)
from learner_state.tests.test_frozen_policy_generation_artifact_body_generation_runtime_integration import (
    assert_safe_output,
)

MODULE = (
    "learner_state."
    "frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke"
)
EXPECTED_VALID_CASE_IDS = [
    "valid/valid_actual_controlled_cli_output_body_free",
    "valid/valid_actual_controlled_no_file_writing",
    "valid/valid_actual_controlled_no_manifest_writer",
    "valid/valid_actual_controlled_no_residue",
    "valid/valid_actual_controlled_safe_metadata_invocation",
    "valid/valid_actual_controlled_stdout_stderr_suppressed",
]
PRIMARY_ACTUAL_CONTROLLED_CASE = "valid/valid_actual_controlled_safe_metadata_invocation"
PLANNED_RUNTIME_INVOCATION_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation"
)
PLANNED_RUNTIME_INVOCATION_CASE = "valid/valid_minimal_safe_metadata_runtime_invocation"


class ActualControlledV04MultiCaseRuntimeSmokeTests(unittest.TestCase):
    def test_discovers_all_valid_case_ids_sorted_by_directory_name(self) -> None:
        case_ids, reason = discover_all_valid_case_ids(DEFAULT_FIXTURE_ROOT)

        self.assertEqual(reason, "none")
        self.assertEqual(case_ids, EXPECTED_VALID_CASE_IDS)
        self.assertEqual(case_ids, sorted(case_ids))

    def test_all_valid_selection_does_not_select_invalid_cases(self) -> None:
        case_ids, reason = discover_all_valid_case_ids(DEFAULT_FIXTURE_ROOT)

        self.assertEqual(reason, "none")
        self.assertEqual(len(case_ids), 6)
        self.assertTrue(all(case_id.startswith("valid/") for case_id in case_ids))
        self.assertFalse(any(case_id.startswith("invalid/") for case_id in case_ids))

    def test_all_valid_multi_case_smoke_passes(self) -> None:
        summary = run_smoke()
        payload = summary.to_public_dict()

        self.assertEqual(payload["mode"], MODE)
        self.assertEqual(payload["schema_version"], SCHEMA_VERSION)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["reason_code"], "none")
        self.assertEqual(payload["case_selection"], CASE_SELECTION_ALL_VALID)
        self.assertEqual(payload["selected_case_count"], 6)
        self.assertEqual(payload["selected_valid_case_count"], 6)
        self.assertEqual(payload["selected_invalid_case_count"], 0)
        self.assertEqual(payload["executed_case_count"], 6)
        self.assertEqual(payload["pass_case_count"], 6)
        self.assertEqual(payload["usage_error_case_count"], 0)
        self.assertEqual(payload["fail_closed_case_count"], 0)
        self.assertEqual(payload["mismatch_case_count"], 0)
        self.assertEqual(payload["input_error_case_count"], 0)
        self.assertEqual(
            payload["runtime_schema_version"],
            ACTUAL_CONTROLLED_RUNTIME_SCHEMA_VERSION,
        )
        self.assertEqual(
            payload["integration_mode"],
            ACTUAL_CONTROLLED_ARTIFACT_BODY_RUNTIME_INVOCATION_MODE,
        )
        self.assertTrue(payload["all_cases_artifact_body_runtime_invoked"])
        self.assertTrue(payload["all_cases_controlled_metadata_only_invocation"])
        self.assertEqual(payload["artifact_body_generation_cli_invoked_case_count"], 6)
        self.assertEqual(
            payload["artifact_body_generation_cli_output_body_free_case_count"], 6
        )
        self.assertEqual(payload["artifact_body_payload_emitted_case_count"], 0)
        self.assertEqual(payload["manifest_writer_invoked_case_count"], 0)
        self.assertEqual(payload["file_writing_enabled_case_count"], 0)
        self.assertEqual(payload["raw_stdout_body_suppressed_case_count"], 6)
        self.assertEqual(payload["raw_stderr_body_suppressed_case_count"], 6)
        self.assertEqual(payload["unsafe_signal_total_count"], 0)
        self.assertEqual(payload["residue_file_count"], 0)
        self.assertEqual(payload["safe_metadata_body_field_count_min"], 5)
        self.assertEqual(payload["safe_metadata_body_field_count_max"], 5)
        self.assertEqual(payload["safe_metadata_body_field_count_unique_values"], "5")
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
        self.assertIn("mode=actual_controlled_v0_4_multi_case_runtime_smoke", completed.stdout)
        self.assertIn("status=pass", completed.stdout)
        self.assertIn("selected_case_count=6", completed.stdout)
        self.assertIn("artifact_body_generation_cli_invoked_case_count=6", completed.stdout)
        self.assertIn("unsafe_signal_total_count=0", completed.stdout)
        for case_id in EXPECTED_VALID_CASE_IDS:
            self.assertNotIn(case_id, completed.stdout)
        assert_safe_output(self, completed.stdout)
        assert_safe_output(self, completed.stderr)

    def test_missing_summary_only_flag_maps_to_usage_error(self) -> None:
        summary = run_smoke(summary_only=False)

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_required_cli_flag")
        self.assertEqual(summary.return_code, 2)

    def test_missing_no_file_writing_flag_maps_to_usage_error(self) -> None:
        summary = run_smoke(no_file_writing=False)

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_required_cli_flag")

    def test_missing_no_manifest_writer_flag_maps_to_usage_error(self) -> None:
        summary = run_smoke(no_manifest_writer=False)

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_required_cli_flag")

    def test_missing_fail_closed_flag_maps_to_usage_error(self) -> None:
        summary = run_smoke(fail_closed_on_unsafe_output=False)

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_required_cli_flag")

    def test_invalid_case_selection_maps_to_usage_error(self) -> None:
        summary = run_smoke(case_selection="selected-invalid")

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "invalid_case_selection")

    def test_zero_valid_cases_maps_to_usage_error(self) -> None:
        with temp_root_copy() as root:
            for child in (root / "valid").iterdir():
                if child.is_dir():
                    shutil.rmtree(child)

            summary = run_smoke(fixture_root=root)

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "zero_valid_cases")

    def test_duplicate_case_id_maps_to_usage_error(self) -> None:
        summary = run_smoke(selected_case_ids=[*EXPECTED_VALID_CASE_IDS, EXPECTED_VALID_CASE_IDS[0]])

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "duplicate_case_id")

    def test_unexpected_non_directory_entry_maps_to_usage_error(self) -> None:
        with temp_root_copy() as root:
            (root / "valid" / "tooling_artifact").write_text(
                "metadata-only-non-directory\n",
                encoding="utf-8",
            )

            summary = run_smoke(fixture_root=root)

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "unexpected_non_directory_entry")

    def test_selected_invalid_case_maps_to_usage_error(self) -> None:
        summary = run_smoke(
            selected_case_ids=[
                *EXPECTED_VALID_CASE_IDS[:5],
                "invalid/invalid_request_body_present",
            ]
        )

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "unexpected_invalid_case_selected")

    def test_unsafe_marker_in_one_selected_case_maps_aggregate_to_fail_closed(self) -> None:
        with temp_root_copy() as root:
            mutate(root, PRIMARY_ACTUAL_CONTROLLED_CASE, REQUEST_METADATA_FILE, "request_body_present", True)

            summary = run_smoke(fixture_root=root)
            rendered = format_public_summary(summary.to_public_dict())

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "request_body_present")
        self.assertEqual(summary.fail_closed_case_count, 1)
        self.assertGreaterEqual(summary.unsafe_signal_total_count, 1)
        assert_safe_output(self, rendered)

    def test_artifact_body_cli_nonzero_case_maps_aggregate_to_fail_closed(self) -> None:
        with temp_root_copy() as root:
            mutate(
                root,
                PRIMARY_ACTUAL_CONTROLLED_CASE,
                CLI_METADATA_FILE,
                "artifact_body_generation_cli_exit_code_category",
                "nonzero",
            )

            summary = run_smoke(fixture_root=root)

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "artifact_body_cli_nonzero_exit")
        self.assertEqual(summary.fail_closed_case_count, 1)

    def test_residue_in_one_selected_case_maps_aggregate_to_fail_closed(self) -> None:
        with temp_root_copy() as root:
            mutate(
                root,
                PRIMARY_ACTUAL_CONTROLLED_CASE,
                RESIDUE_POLICY_FILE,
                "unsafe_output_residue_risk_marker",
                True,
            )

            summary = run_smoke(fixture_root=root)

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "unsafe_output_residue_risk")
        self.assertEqual(summary.fail_closed_case_count, 1)

    def test_expected_count_mismatch_maps_to_mismatch(self) -> None:
        summary = run_smoke(expected_executed_case_count=7)

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "expected_aggregate_count_mismatch")
        self.assertEqual(summary.return_code, 1)

    def test_v0_4_single_case_runtime_behavior_remains_unchanged(self) -> None:
        summary = run_artifact_body_generation_runtime_integration_for_fixture_case(
            DEFAULT_FIXTURE_ROOT,
            PRIMARY_ACTUAL_CONTROLLED_CASE,
            mode=ACTUAL_CONTROLLED_ARTIFACT_BODY_RUNTIME_INVOCATION_MODE,
            summary_only=True,
            no_file_writing=True,
            no_manifest_writer=True,
            fail_closed_on_unsafe_output=True,
            actual_invocation=True,
        )

        self.assertEqual(summary.status, "pass")
        self.assertEqual(summary.runtime_schema_version, ACTUAL_CONTROLLED_RUNTIME_SCHEMA_VERSION)
        self.assertEqual(
            summary.integration_mode,
            ACTUAL_CONTROLLED_ARTIFACT_BODY_RUNTIME_INVOCATION_MODE,
        )
        self.assertTrue(summary.artifact_body_runtime_invoked)

    def test_v0_3_planned_only_runtime_behavior_remains_unchanged(self) -> None:
        summary = run_artifact_body_generation_runtime_integration_for_fixture_case(
            PLANNED_RUNTIME_INVOCATION_ROOT,
            PLANNED_RUNTIME_INVOCATION_CASE,
            mode=ARTIFACT_BODY_RUNTIME_INVOCATION_MODE,
            summary_only=True,
            no_file_writing=True,
            no_manifest_writer=True,
            fail_closed_on_unsafe_output=True,
        )

        self.assertEqual(summary.status, "pass")
        self.assertEqual(summary.runtime_schema_version, RUNTIME_INVOCATION_RUNTIME_SCHEMA_VERSION)
        self.assertEqual(summary.integration_mode, ARTIFACT_BODY_RUNTIME_INVOCATION_MODE)
        self.assertFalse(summary.artifact_body_runtime_invoked)

    def test_fixture_json_not_mutated(self) -> None:
        before = snapshot_fixture_tree(DEFAULT_FIXTURE_ROOT)

        summary = run_smoke()

        after = snapshot_fixture_tree(DEFAULT_FIXTURE_ROOT)
        self.assertEqual(summary.status, "pass")
        self.assertEqual(before, after)


def run_smoke(
    *,
    fixture_root: Path = DEFAULT_FIXTURE_ROOT,
    case_selection: str = CASE_SELECTION_ALL_VALID,
    summary_only: bool = True,
    no_file_writing: bool = True,
    no_manifest_writer: bool = True,
    fail_closed_on_unsafe_output: bool = True,
    selected_case_ids: list[str] | None = None,
    expected_executed_case_count: int = 6,
):
    return run_multi_case_runtime_smoke(
        fixture_root,
        case_selection=case_selection,
        summary_only=summary_only,
        no_file_writing=no_file_writing,
        no_manifest_writer=no_manifest_writer,
        fail_closed_on_unsafe_output=fail_closed_on_unsafe_output,
        selected_case_ids=selected_case_ids,
        expected_executed_case_count=expected_executed_case_count,
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
            CASE_SELECTION_ALL_VALID,
            "--summary-only",
            "--no-file-writing",
            "--no-manifest-writer",
            "--fail-closed-on-unsafe-output",
        ],
        check=False,
        capture_output=True,
        text=True,
    )


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


def mutate(
    root: Path,
    case_id: str,
    file_name: str,
    field_name: str,
    value: object,
) -> None:
    path = root / case_id / file_name
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload[field_name] = value
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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


if __name__ == "__main__":
    unittest.main()
