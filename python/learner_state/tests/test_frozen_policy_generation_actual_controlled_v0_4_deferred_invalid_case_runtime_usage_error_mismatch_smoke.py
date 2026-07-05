from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from learner_state.frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke import (
    CASE_SELECTION_DEFERRED_INVALID_USAGE_ERROR_MISMATCH,
    DEFAULT_FIXTURE_ROOT,
    EXPECTED_MISMATCH_CASE_COUNT,
    EXPECTED_MISMATCH_CASE_IDS,
    EXPECTED_USAGE_ERROR_CASE_COUNT,
    EXPECTED_USAGE_ERROR_CASE_IDS,
    MODE,
    SCHEMA_VERSION,
    SELECTED_DEFERRED_INVALID_CASE_IDS,
    DeferredInvalidCaseObservation,
    discover_deferred_invalid_case_ids,
    format_public_summary,
    observe_deferred_invalid_case,
    run_deferred_invalid_case_runtime_usage_error_mismatch_smoke,
)
from learner_state.frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke import (
    CASE_SELECTION_FAIL_CLOSED_INVALID,
    SELECTED_FAIL_CLOSED_INVALID_CASE_IDS,
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
    "frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke"
)
PRIMARY_ACTUAL_CONTROLLED_CASE = "valid/valid_actual_controlled_safe_metadata_invocation"
PLANNED_RUNTIME_INVOCATION_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation"
)
PLANNED_RUNTIME_INVOCATION_CASE = "valid/valid_minimal_safe_metadata_runtime_invocation"


class ActualControlledV04DeferredInvalidCaseRuntimeUsageErrorMismatchSmokeTests(
    unittest.TestCase
):
    def test_contract_contains_exactly_4_selected_deferred_invalid_case_ids(self) -> None:
        self.assertEqual(len(SELECTED_DEFERRED_INVALID_CASE_IDS), 4)
        self.assertEqual(set(SELECTED_DEFERRED_INVALID_CASE_IDS), {
            "invalid/invalid_malformed_metadata_json",
            "invalid/invalid_missing_required_metadata_file",
            "invalid/invalid_mismatched_expected_status",
            "invalid/invalid_unsupported_schema",
        })

    def test_selected_case_ids_are_sorted_and_invalid_only(self) -> None:
        self.assertEqual(
            list(SELECTED_DEFERRED_INVALID_CASE_IDS),
            sorted(SELECTED_DEFERRED_INVALID_CASE_IDS),
        )
        self.assertTrue(
            all(case_id.startswith("invalid/") for case_id in SELECTED_DEFERRED_INVALID_CASE_IDS)
        )

    def test_no_valid_or_fail_closed_cases_are_selected(self) -> None:
        self.assertFalse(any(case_id.startswith("valid/") for case_id in SELECTED_DEFERRED_INVALID_CASE_IDS))
        self.assertFalse(
            set(SELECTED_DEFERRED_INVALID_CASE_IDS).intersection(
                SELECTED_FAIL_CLOSED_INVALID_CASE_IDS
            )
        )
        self.assertEqual(len(SELECTED_FAIL_CLOSED_INVALID_CASE_IDS), 26)

    def test_expected_usage_error_and_mismatch_case_counts(self) -> None:
        self.assertEqual(len(EXPECTED_USAGE_ERROR_CASE_IDS), EXPECTED_USAGE_ERROR_CASE_COUNT)
        self.assertEqual(len(EXPECTED_MISMATCH_CASE_IDS), EXPECTED_MISMATCH_CASE_COUNT)
        self.assertEqual(len(set(EXPECTED_USAGE_ERROR_CASE_IDS)), 3)
        self.assertEqual(len(set(EXPECTED_MISMATCH_CASE_IDS)), 1)

    def test_all_selected_case_directories_exist(self) -> None:
        for case_id in SELECTED_DEFERRED_INVALID_CASE_IDS:
            self.assertTrue((DEFAULT_FIXTURE_ROOT / case_id).is_dir(), case_id)

    def test_discovers_fixed_deferred_invalid_case_ids(self) -> None:
        case_ids, reason = discover_deferred_invalid_case_ids(DEFAULT_FIXTURE_ROOT)

        self.assertEqual(reason, "none")
        self.assertEqual(case_ids, list(SELECTED_DEFERRED_INVALID_CASE_IDS))

    def test_deferred_invalid_usage_error_mismatch_smoke_passes(self) -> None:
        summary = run_smoke()
        payload = summary.to_public_dict()

        self.assertEqual(payload["mode"], MODE)
        self.assertEqual(payload["schema_version"], SCHEMA_VERSION)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["reason_code"], "none")
        self.assertEqual(
            payload["matrix_name"],
            "actual_controlled_v0_4_deferred_invalid_usage_error_mismatch_runtime_smoke",
        )
        self.assertEqual(
            payload["case_selection"],
            CASE_SELECTION_DEFERRED_INVALID_USAGE_ERROR_MISMATCH,
        )
        self.assertEqual(payload["selected_case_count"], 4)
        self.assertEqual(payload["selected_invalid_case_count"], 4)
        self.assertEqual(payload["selected_valid_case_count"], 0)
        self.assertEqual(payload["selected_usage_error_case_count"], 3)
        self.assertEqual(payload["selected_mismatch_case_count"], 1)
        self.assertEqual(payload["excluded_fail_closed_case_count"], 26)
        self.assertEqual(payload["excluded_valid_case_count"], 6)
        self.assertEqual(payload["processed_case_count"], 4)
        self.assertEqual(payload["preflight_usage_error_case_count"], 3)
        self.assertEqual(payload["runtime_or_contract_mismatch_case_count"], 1)
        self.assertEqual(payload["expected_usage_error_case_count"], 3)
        self.assertEqual(payload["observed_usage_error_case_count"], 3)
        self.assertEqual(payload["expected_mismatch_case_count"], 1)
        self.assertEqual(payload["observed_mismatch_case_count"], 1)
        self.assertEqual(payload["expected_fail_closed_case_count"], 0)
        self.assertEqual(payload["observed_fail_closed_case_count"], 0)
        self.assertEqual(payload["expected_pass_case_count"], 0)
        self.assertEqual(payload["observed_pass_case_count"], 0)
        self.assertEqual(payload["input_error_case_count"], 0)
        self.assertEqual(
            payload["runtime_schema_version"],
            ACTUAL_CONTROLLED_RUNTIME_SCHEMA_VERSION,
        )
        self.assertEqual(
            payload["integration_mode"],
            ACTUAL_CONTROLLED_ARTIFACT_BODY_RUNTIME_INVOCATION_MODE,
        )
        self.assertEqual(payload["artifact_body_payload_emitted_case_count"], 0)
        self.assertEqual(payload["manifest_writer_invoked_case_count"], 0)
        self.assertEqual(payload["file_writing_enabled_case_count"], 0)
        self.assertEqual(payload["artifact_file_written_case_count"], 0)
        self.assertEqual(payload["manifest_file_written_case_count"], 0)
        self.assertEqual(payload["forbidden_body_emitted_case_count"], 0)
        self.assertEqual(payload["raw_stdout_body_suppressed_case_count"], 4)
        self.assertEqual(payload["raw_stderr_body_suppressed_case_count"], 4)
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
        self.assertIn("selected_case_count=4", completed.stdout)
        self.assertIn("processed_case_count=4", completed.stdout)
        self.assertIn("observed_usage_error_case_count=3", completed.stdout)
        self.assertIn("observed_mismatch_case_count=1", completed.stdout)
        self.assertIn("residue_file_count=0", completed.stdout)
        for case_id in SELECTED_DEFERRED_INVALID_CASE_IDS:
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
        summary = run_smoke(case_selection="fail-closed-invalid")

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "invalid_case_selection")

    def test_missing_selected_case_directory_maps_to_usage_error(self) -> None:
        with temp_root_copy() as root:
            shutil.rmtree(root / SELECTED_DEFERRED_INVALID_CASE_IDS[0])

            summary = run_smoke(fixture_root=root)

        self.assertEqual(summary.status, "usage_error")

    def test_valid_case_included_maps_to_usage_error(self) -> None:
        summary = run_smoke(
            selected_case_ids=[
                *SELECTED_DEFERRED_INVALID_CASE_IDS[:-1],
                PRIMARY_ACTUAL_CONTROLLED_CASE,
            ]
        )

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "unexpected_valid_case_selected")

    def test_fail_closed_case_included_maps_to_usage_error(self) -> None:
        summary = run_smoke(
            selected_case_ids=[
                *SELECTED_DEFERRED_INVALID_CASE_IDS[:-1],
                SELECTED_FAIL_CLOSED_INVALID_CASE_IDS[0],
            ]
        )

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "unexpected_fail_closed_case_selected")

    def test_duplicate_case_id_maps_to_usage_error(self) -> None:
        summary = run_smoke(
            selected_case_ids=[
                *SELECTED_DEFERRED_INVALID_CASE_IDS,
                SELECTED_DEFERRED_INVALID_CASE_IDS[0],
            ]
        )

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "duplicate_case_id")

    def test_selected_case_producing_pass_unexpectedly_maps_to_mismatch(self) -> None:
        summary = run_smoke(
            case_observer=replace_observation(
                SELECTED_DEFERRED_INVALID_CASE_IDS[0],
                observed_status="pass",
                reason_code="unexpected_pass",
            )
        )

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "selected_invalid_case_passed")

    def test_selected_case_producing_fail_closed_unexpectedly_maps_to_mismatch(self) -> None:
        summary = run_smoke(
            case_observer=replace_observation(
                SELECTED_DEFERRED_INVALID_CASE_IDS[0],
                observed_status="fail_closed",
                reason_code="unexpected_fail_closed",
            )
        )

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "selected_invalid_case_failed_closed")

    def test_wrong_observed_category_maps_to_mismatch(self) -> None:
        summary = run_smoke(
            case_observer=replace_observation(
                "invalid/invalid_mismatched_expected_status",
                observed_status="usage_error",
                reason_code="wrong_category",
            )
        )

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "observed_status_category_mismatch")

    def test_selected_case_emitting_forbidden_body_maps_to_fail_closed(self) -> None:
        summary = run_smoke(
            case_observer=replace_observation(
                SELECTED_DEFERRED_INVALID_CASE_IDS[0],
                forbidden_body_emitted=True,
            )
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "forbidden_body_emitted")

    def test_selected_case_invoking_manifest_writer_maps_to_fail_closed(self) -> None:
        summary = run_smoke(
            case_observer=replace_observation(
                SELECTED_DEFERRED_INVALID_CASE_IDS[0],
                manifest_writer_invoked=True,
            )
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "manifest_writer_invoked")

    def test_selected_case_enabling_file_writing_maps_to_fail_closed(self) -> None:
        summary = run_smoke(
            case_observer=replace_observation(
                SELECTED_DEFERRED_INVALID_CASE_IDS[0],
                file_writing_enabled=True,
            )
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "file_writing_enabled")

    def test_selected_case_leaving_residue_maps_to_fail_closed(self) -> None:
        summary = run_smoke(
            case_observer=replace_observation(
                SELECTED_DEFERRED_INVALID_CASE_IDS[0],
                residue_file_count=1,
            )
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "residue_detected")

    def test_aggregate_count_mismatch_maps_to_runner_level_mismatch(self) -> None:
        summary = run_smoke(expected_processed_case_count=5)

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "expected_aggregate_count_mismatch")
        self.assertEqual(summary.return_code, 1)

    def test_public_summary_format_is_stable(self) -> None:
        rendered = format_public_summary(run_smoke().to_public_dict())
        lines = rendered.splitlines()

        self.assertEqual(lines[0], f"mode={MODE}")
        self.assertIn(f"schema_version={SCHEMA_VERSION}", lines)
        self.assertIn(
            f"case_selection={CASE_SELECTION_DEFERRED_INVALID_USAGE_ERROR_MISMATCH}",
            lines,
        )
        self.assertIn("processed_case_count=4", lines)
        assert_safe_output(self, rendered)

    def test_fixture_json_not_mutated(self) -> None:
        before = snapshot_fixture_tree(DEFAULT_FIXTURE_ROOT)

        summary = run_smoke()

        after = snapshot_fixture_tree(DEFAULT_FIXTURE_ROOT)
        self.assertEqual(summary.status, "pass")
        self.assertEqual(before, after)

    def test_existing_fail_closed_invalid_case_runner_behavior_remains_unchanged(self) -> None:
        summary = run_invalid_case_runtime_fail_closed_smoke(
            DEFAULT_FIXTURE_ROOT,
            case_selection=CASE_SELECTION_FAIL_CLOSED_INVALID,
            summary_only=True,
            no_file_writing=True,
            no_manifest_writer=True,
            fail_closed_on_unsafe_output=True,
        )

        self.assertEqual(summary.status, "pass")
        self.assertEqual(summary.selected_case_count, 26)
        self.assertEqual(summary.observed_fail_closed_case_count, 26)
        self.assertEqual(summary.forbidden_body_emitted_case_count, 0)

    def test_existing_all_valid_multi_case_runner_behavior_remains_unchanged(self) -> None:
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


def run_smoke(
    *,
    fixture_root: Path = DEFAULT_FIXTURE_ROOT,
    case_selection: str = CASE_SELECTION_DEFERRED_INVALID_USAGE_ERROR_MISMATCH,
    summary_only: bool = True,
    no_file_writing: bool = True,
    no_manifest_writer: bool = True,
    fail_closed_on_unsafe_output: bool = True,
    selected_case_ids: list[str] | None = None,
    case_observer=None,
    expected_processed_case_count: int = 4,
):
    return run_deferred_invalid_case_runtime_usage_error_mismatch_smoke(
        fixture_root,
        case_selection=case_selection,
        summary_only=summary_only,
        no_file_writing=no_file_writing,
        no_manifest_writer=no_manifest_writer,
        fail_closed_on_unsafe_output=fail_closed_on_unsafe_output,
        selected_case_ids=selected_case_ids,
        case_observer=case_observer,
        expected_processed_case_count=expected_processed_case_count,
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
            CASE_SELECTION_DEFERRED_INVALID_USAGE_ERROR_MISMATCH,
            "--summary-only",
            "--no-file-writing",
            "--no-manifest-writer",
            "--fail-closed-on-unsafe-output",
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def replace_observation(case_id: str, **changes):
    def observer(observed_case_id: str) -> DeferredInvalidCaseObservation:
        observation = observe_deferred_invalid_case(observed_case_id)
        if observed_case_id == case_id:
            return replace(observation, **changes)
        return observation

    return observer


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
