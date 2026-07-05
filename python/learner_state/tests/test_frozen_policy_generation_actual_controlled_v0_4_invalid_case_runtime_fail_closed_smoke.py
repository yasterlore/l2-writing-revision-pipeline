from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke import (
    CASE_SELECTION_FAIL_CLOSED_INVALID,
    DEFAULT_FIXTURE_ROOT,
    DEFERRED_INVALID_CASE_IDS,
    MODE,
    SCHEMA_VERSION,
    SELECTED_FAIL_CLOSED_INVALID_CASE_IDS,
    discover_fail_closed_invalid_case_ids,
    format_public_summary,
    run_invalid_case_runtime_fail_closed_smoke,
)
from learner_state.frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke import (
    CASE_SELECTION_ALL_VALID,
    run_multi_case_runtime_smoke,
)
from learner_state.frozen_policy_generation_artifact_body_generation_runtime_integration import (
    ACTUAL_CONTROLLED_ARTIFACT_BODY_RUNTIME_INVOCATION_MODE,
    ACTUAL_CONTROLLED_RUNTIME_SCHEMA_VERSION,
    ARTIFACT_BODY_RUNTIME_INVOCATION_MODE,
    RUNTIME_INVOCATION_RUNTIME_SCHEMA_VERSION,
    run_artifact_body_generation_runtime_integration_for_fixture_case,
)
from learner_state.tests.test_frozen_policy_generation_artifact_body_generation_runtime_integration import (
    assert_safe_output,
)

MODULE = (
    "learner_state."
    "frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke"
)
PRIMARY_ACTUAL_CONTROLLED_CASE = "valid/valid_actual_controlled_safe_metadata_invocation"
PLANNED_RUNTIME_INVOCATION_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation"
)
PLANNED_RUNTIME_INVOCATION_CASE = "valid/valid_minimal_safe_metadata_runtime_invocation"


class ActualControlledV04InvalidCaseRuntimeFailClosedSmokeTests(unittest.TestCase):
    def test_selected_invalid_case_ids_match_contract_and_are_sorted(self) -> None:
        self.assertEqual(len(SELECTED_FAIL_CLOSED_INVALID_CASE_IDS), 26)
        self.assertEqual(
            list(SELECTED_FAIL_CLOSED_INVALID_CASE_IDS),
            sorted(SELECTED_FAIL_CLOSED_INVALID_CASE_IDS),
        )
        self.assertTrue(
            all(case_id.startswith("invalid/") for case_id in SELECTED_FAIL_CLOSED_INVALID_CASE_IDS)
        )

    def test_deferred_invalid_case_ids_match_contract_and_are_sorted(self) -> None:
        self.assertEqual(len(DEFERRED_INVALID_CASE_IDS), 4)
        self.assertEqual(len(set(DEFERRED_INVALID_CASE_IDS)), 4)
        self.assertTrue(
            all(case_id.startswith("invalid/") for case_id in DEFERRED_INVALID_CASE_IDS)
        )

    def test_selected_and_deferred_invalid_cases_do_not_overlap(self) -> None:
        self.assertFalse(
            set(SELECTED_FAIL_CLOSED_INVALID_CASE_IDS).intersection(DEFERRED_INVALID_CASE_IDS)
        )

    def test_discovers_fixed_fail_closed_invalid_case_ids(self) -> None:
        case_ids, reason = discover_fail_closed_invalid_case_ids(DEFAULT_FIXTURE_ROOT)

        self.assertEqual(reason, "none")
        self.assertEqual(case_ids, list(SELECTED_FAIL_CLOSED_INVALID_CASE_IDS))

    def test_invalid_case_fail_closed_smoke_passes(self) -> None:
        summary = run_smoke()
        payload = summary.to_public_dict()

        self.assertEqual(payload["mode"], MODE)
        self.assertEqual(payload["schema_version"], SCHEMA_VERSION)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["reason_code"], "none")
        self.assertEqual(payload["matrix_name"], "actual_controlled_v0_4_invalid_fail_closed_runtime_smoke")
        self.assertEqual(payload["case_selection"], CASE_SELECTION_FAIL_CLOSED_INVALID)
        self.assertEqual(payload["selected_case_count"], 26)
        self.assertEqual(payload["selected_invalid_case_count"], 26)
        self.assertEqual(payload["selected_valid_case_count"], 0)
        self.assertEqual(payload["deferred_case_count"], 4)
        self.assertEqual(payload["executed_case_count"], 26)
        self.assertEqual(payload["pass_case_count"], 0)
        self.assertEqual(payload["expected_fail_closed_case_count"], 26)
        self.assertEqual(payload["observed_fail_closed_case_count"], 26)
        self.assertEqual(payload["usage_error_case_count"], 0)
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
        self.assertTrue(payload["all_selected_cases_failed_closed"])
        self.assertEqual(payload["artifact_body_payload_emitted_case_count"], 0)
        self.assertEqual(payload["manifest_writer_invoked_case_count"], 0)
        self.assertEqual(payload["file_writing_enabled_case_count"], 0)
        self.assertEqual(payload["artifact_file_written_case_count"], 0)
        self.assertEqual(payload["manifest_file_written_case_count"], 0)
        self.assertEqual(payload["raw_stdout_body_suppressed_case_count"], 26)
        self.assertEqual(payload["raw_stderr_body_suppressed_case_count"], 26)
        self.assertEqual(payload["forbidden_body_emitted_case_count"], 0)
        self.assertGreater(payload["unsafe_signal_total_count"], 0)
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
        self.assertIn("mode=actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke", completed.stdout)
        self.assertIn("status=pass", completed.stdout)
        self.assertIn("selected_case_count=26", completed.stdout)
        self.assertIn("observed_fail_closed_case_count=26", completed.stdout)
        self.assertIn("unsafe_signal_total_count=26", completed.stdout)
        self.assertIn("residue_file_count=0", completed.stdout)
        for case_id in SELECTED_FAIL_CLOSED_INVALID_CASE_IDS:
            self.assertNotIn(case_id, completed.stdout)
        for case_id in DEFERRED_INVALID_CASE_IDS:
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
        summary = run_smoke(case_selection="all-valid")

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "invalid_case_selection")

    def test_duplicate_case_id_maps_to_usage_error(self) -> None:
        summary = run_smoke(
            selected_case_ids=[
                *SELECTED_FAIL_CLOSED_INVALID_CASE_IDS,
                SELECTED_FAIL_CLOSED_INVALID_CASE_IDS[0],
            ]
        )

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "duplicate_case_id")

    def test_selected_valid_case_maps_to_usage_error(self) -> None:
        summary = run_smoke(
            selected_case_ids=[
                *SELECTED_FAIL_CLOSED_INVALID_CASE_IDS[:-1],
                PRIMARY_ACTUAL_CONTROLLED_CASE,
            ]
        )

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "unexpected_valid_case_selected")

    def test_deferred_case_selected_maps_to_usage_error(self) -> None:
        summary = run_smoke(
            selected_case_ids=[
                *SELECTED_FAIL_CLOSED_INVALID_CASE_IDS[:-1],
                DEFERRED_INVALID_CASE_IDS[0],
            ]
        )

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "unexpected_invalid_case_matrix")

    def test_missing_invalid_fixture_directory_maps_to_usage_error(self) -> None:
        with temp_root_copy() as root:
            shutil.rmtree(root / SELECTED_FAIL_CLOSED_INVALID_CASE_IDS[0])

            summary = run_smoke(fixture_root=root)

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "unexpected_invalid_case_matrix")

    def test_unexpected_non_directory_entry_maps_to_usage_error(self) -> None:
        with temp_root_copy() as root:
            (root / "invalid" / "tooling_artifact").write_text(
                "metadata-only-non-directory\n",
                encoding="utf-8",
            )

            summary = run_smoke(fixture_root=root)

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "unexpected_non_directory_entry")

    def test_expected_count_mismatch_maps_to_mismatch(self) -> None:
        summary = run_smoke(expected_executed_case_count=27)

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "expected_aggregate_count_mismatch")
        self.assertEqual(summary.return_code, 1)

    def test_public_summary_format_is_stable(self) -> None:
        rendered = format_public_summary(run_smoke().to_public_dict())
        lines = rendered.splitlines()

        self.assertEqual(lines[0], f"mode={MODE}")
        self.assertIn(f"schema_version={SCHEMA_VERSION}", lines)
        self.assertIn("case_selection=fail-closed-invalid", lines)
        self.assertIn("all_selected_cases_failed_closed=True", lines)
        assert_safe_output(self, rendered)

    def test_all_valid_multi_case_runtime_behavior_remains_unchanged(self) -> None:
        summary = run_multi_case_runtime_smoke(
            DEFAULT_FIXTURE_ROOT,
            case_selection=CASE_SELECTION_ALL_VALID,
            summary_only=True,
            no_file_writing=True,
            no_manifest_writer=True,
            fail_closed_on_unsafe_output=True,
        )

        self.assertEqual(summary.status, "pass")
        self.assertEqual(summary.selected_case_count, 6)
        self.assertEqual(summary.pass_case_count, 6)
        self.assertEqual(summary.unsafe_signal_total_count, 0)

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
    case_selection: str = CASE_SELECTION_FAIL_CLOSED_INVALID,
    summary_only: bool = True,
    no_file_writing: bool = True,
    no_manifest_writer: bool = True,
    fail_closed_on_unsafe_output: bool = True,
    selected_case_ids: list[str] | None = None,
    expected_executed_case_count: int = 26,
):
    return run_invalid_case_runtime_fail_closed_smoke(
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
            CASE_SELECTION_FAIL_CLOSED_INVALID,
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
