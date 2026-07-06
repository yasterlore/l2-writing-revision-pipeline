from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from learner_state.frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission import (
    CASE_SELECTION_PAYLOAD_AUDIT_WITHOUT_PAYLOAD_EMISSION,
    DEFAULT_FIXTURE_ROOT,
    EXPECTED_DEFERRED_INVALID_CASE_COUNT,
    EXPECTED_FAIL_CLOSED_INVALID_CASE_COUNT,
    EXPECTED_INVALID_CASE_COUNT,
    EXPECTED_MISMATCH_CASE_COUNT,
    EXPECTED_PAYLOAD_CAPABLE_CASE_COUNT,
    EXPECTED_PAYLOAD_NOT_APPLICABLE_CASE_COUNT,
    EXPECTED_SELECTED_CASE_COUNT,
    EXPECTED_USAGE_ERROR_CASE_COUNT,
    EXPECTED_VALID_CASE_COUNT,
    MATRIX_NAME,
    MODE,
    SCHEMA_VERSION,
    PayloadAuditObservation,
    discover_payload_audit_case_ids,
    format_public_summary,
    observe_payload_audit_case,
    run_artifact_body_payload_audit_without_payload_emission,
)
from learner_state.frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke import (
    CASE_SELECTION_DEFERRED_INVALID_USAGE_ERROR_MISMATCH,
    SELECTED_DEFERRED_INVALID_CASE_IDS,
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
from learner_state.tests.test_frozen_policy_generation_artifact_body_generation_runtime_integration import (
    assert_safe_output,
)

MODULE = (
    "learner_state."
    "frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_"
    "without_payload_emission"
)


class ActualControlledV04ArtifactBodyPayloadAuditWithoutEmissionTests(
    unittest.TestCase
):
    def test_discovers_fixed_36_case_contract(self) -> None:
        case_ids, reason = discover_payload_audit_case_ids(DEFAULT_FIXTURE_ROOT)

        self.assertEqual(reason, "none")
        self.assertEqual(len(case_ids), EXPECTED_SELECTED_CASE_COUNT)
        self.assertEqual(count_valid(case_ids), EXPECTED_VALID_CASE_COUNT)
        self.assertEqual(count_invalid(case_ids), EXPECTED_INVALID_CASE_COUNT)
        self.assertEqual(
            len(set(case_ids).intersection(SELECTED_FAIL_CLOSED_INVALID_CASE_IDS)),
            EXPECTED_FAIL_CLOSED_INVALID_CASE_COUNT,
        )
        self.assertEqual(
            len(set(case_ids).intersection(SELECTED_DEFERRED_INVALID_CASE_IDS)),
            EXPECTED_DEFERRED_INVALID_CASE_COUNT,
        )

    def test_observation_contract_for_valid_case_is_payload_capable(self) -> None:
        case_ids, reason = discover_payload_audit_case_ids(DEFAULT_FIXTURE_ROOT)
        self.assertEqual(reason, "none")
        valid_case_id = next(case_id for case_id in case_ids if case_id.startswith("valid/"))

        observation = observe_payload_audit_case(valid_case_id)

        self.assertEqual(observation.observed_status, "pass")
        self.assertTrue(observation.payload_capable)
        self.assertTrue(observation.payload_availability_checked)
        self.assertTrue(observation.payload_suppressed)
        self.assertTrue(observation.payload_body_free)

    def test_observation_contract_for_invalid_case_is_payload_not_applicable(self) -> None:
        observation = observe_payload_audit_case(SELECTED_FAIL_CLOSED_INVALID_CASE_IDS[0])

        self.assertEqual(observation.observed_status, "fail_closed")
        self.assertFalse(observation.payload_capable)
        self.assertFalse(observation.payload_availability_checked)
        self.assertTrue(observation.payload_suppressed)
        self.assertTrue(observation.payload_body_free)

    def test_payload_audit_passes_with_count_only_summary(self) -> None:
        summary = run_audit()
        payload = summary.to_public_dict()

        self.assertEqual(payload["mode"], MODE)
        self.assertEqual(payload["schema_version"], SCHEMA_VERSION)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["reason_code"], "none")
        self.assertEqual(payload["matrix_name"], MATRIX_NAME)
        self.assertEqual(
            payload["case_selection"],
            CASE_SELECTION_PAYLOAD_AUDIT_WITHOUT_PAYLOAD_EMISSION,
        )
        self.assertEqual(payload["selected_case_count"], 36)
        self.assertEqual(payload["selected_valid_case_count"], 6)
        self.assertEqual(payload["selected_invalid_case_count"], 30)
        self.assertEqual(payload["selected_fail_closed_invalid_case_count"], 26)
        self.assertEqual(payload["selected_deferred_invalid_case_count"], 4)
        self.assertEqual(payload["selected_usage_error_case_count"], 3)
        self.assertEqual(payload["selected_mismatch_case_count"], 1)
        self.assertEqual(payload["expected_payload_capable_case_count"], 6)
        self.assertEqual(payload["expected_payload_not_applicable_case_count"], 30)
        self.assertEqual(payload["observed_payload_capable_case_count"], 6)
        self.assertEqual(payload["observed_payload_not_applicable_case_count"], 30)
        self.assertEqual(payload["observed_payload_availability_checked_case_count"], 6)
        self.assertEqual(payload["observed_payload_suppressed_case_count"], 36)
        self.assertEqual(payload["observed_payload_body_free_case_count"], 36)
        self.assertEqual(payload["expected_pass_case_count"], 6)
        self.assertEqual(payload["observed_pass_case_count"], 6)
        self.assertEqual(payload["expected_fail_closed_case_count"], 26)
        self.assertEqual(payload["observed_fail_closed_case_count"], 26)
        self.assertEqual(payload["expected_usage_error_case_count"], 3)
        self.assertEqual(payload["observed_usage_error_case_count"], 3)
        self.assertEqual(payload["expected_mismatch_case_count"], 1)
        self.assertEqual(payload["observed_mismatch_case_count"], 1)
        self.assertEqual(payload["artifact_body_payload_emitted_case_count"], 0)
        self.assertEqual(payload["generated_policy_body_emitted_case_count"], 0)
        self.assertEqual(payload["manifest_body_emitted_case_count"], 0)
        self.assertEqual(payload["forbidden_body_emitted_case_count"], 0)
        self.assertEqual(payload["raw_stdout_body_suppressed_case_count"], 36)
        self.assertEqual(payload["raw_stderr_body_suppressed_case_count"], 36)
        self.assertEqual(payload["manifest_writer_invoked_case_count"], 0)
        self.assertEqual(payload["file_writing_enabled_case_count"], 0)
        self.assertEqual(payload["artifact_file_written_case_count"], 0)
        self.assertEqual(payload["manifest_file_written_case_count"], 0)
        self.assertEqual(payload["residue_file_count"], 0)
        self.assertTrue(payload["content_suppressed"])
        self.assertTrue(payload["body_suppressed"])
        self.assertTrue(payload["metadata_only_checked"])
        self.assertTrue(payload["synthetic_only_checked"])
        self.assertTrue(payload["no_oracle_checked"])
        self.assertFalse(payload["payload_body_emitted"])
        self.assertFalse(payload["production_readiness_claimed"])
        self.assertFalse(payload["real_data_readiness_claimed"])
        self.assertFalse(payload["performance_claims_present"])

    def test_cli_output_is_aggregate_only_and_public_safe(self) -> None:
        completed = run_cli()

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn(f"mode={MODE}", completed.stdout)
        self.assertIn("status=pass", completed.stdout)
        self.assertIn("selected_case_count=36", completed.stdout)
        self.assertIn("observed_payload_capable_case_count=6", completed.stdout)
        self.assertIn("observed_payload_not_applicable_case_count=30", completed.stdout)
        self.assertIn("artifact_body_payload_emitted_case_count=0", completed.stdout)
        self.assertIn("residue_file_count=0", completed.stdout)
        for case_id in SELECTED_FAIL_CLOSED_INVALID_CASE_IDS:
            self.assertNotIn(case_id, completed.stdout)
        for case_id in SELECTED_DEFERRED_INVALID_CASE_IDS:
            self.assertNotIn(case_id, completed.stdout)
        assert_safe_output(self, completed.stdout)
        assert_safe_output(self, completed.stderr)

    def test_missing_summary_only_flag_maps_to_usage_error(self) -> None:
        summary = run_audit(summary_only=False)

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_required_cli_flag")
        self.assertEqual(summary.return_code, 2)

    def test_missing_no_file_writing_flag_maps_to_usage_error(self) -> None:
        summary = run_audit(no_file_writing=False)

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_required_cli_flag")

    def test_missing_no_manifest_writer_flag_maps_to_usage_error(self) -> None:
        summary = run_audit(no_manifest_writer=False)

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_required_cli_flag")

    def test_missing_fail_closed_flag_maps_to_usage_error(self) -> None:
        summary = run_audit(fail_closed_on_forbidden_body=False)

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "missing_required_cli_flag")

    def test_invalid_case_selection_maps_to_usage_error(self) -> None:
        summary = run_audit(case_selection="all-valid")

        self.assertEqual(summary.status, "usage_error")
        self.assertEqual(summary.reason_code, "invalid_case_selection")

    def test_missing_fixture_root_maps_to_input_error(self) -> None:
        summary = run_audit(fixture_root=Path("missing-fixture-root"))

        self.assertEqual(summary.status, "input_error")
        self.assertEqual(summary.reason_code, "missing_fixture_root")

    def test_missing_case_directory_maps_to_input_error(self) -> None:
        with temp_root_copy() as root:
            shutil.rmtree(root / SELECTED_DEFERRED_INVALID_CASE_IDS[0])

            summary = run_audit(fixture_root=root)

        self.assertEqual(summary.status, "input_error")
        self.assertEqual(summary.reason_code, "invalid_case_matrix_mismatch")

    def test_selected_count_mismatch_maps_to_mismatch(self) -> None:
        case_ids, reason = discover_payload_audit_case_ids(DEFAULT_FIXTURE_ROOT)
        self.assertEqual(reason, "none")

        summary = run_audit(selected_case_ids=case_ids[:-1])

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "selected_case_count_mismatch")

    def test_duplicate_case_id_maps_to_mismatch(self) -> None:
        case_ids, reason = discover_payload_audit_case_ids(DEFAULT_FIXTURE_ROOT)
        self.assertEqual(reason, "none")

        summary = run_audit(selected_case_ids=[*case_ids, case_ids[0]])

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "duplicate_case_id")

    def test_observed_status_category_mismatch_maps_to_mismatch(self) -> None:
        case_ids, reason = discover_payload_audit_case_ids(DEFAULT_FIXTURE_ROOT)
        self.assertEqual(reason, "none")
        valid_case_id = next(case_id for case_id in case_ids if case_id.startswith("valid/"))

        summary = run_audit(
            case_observer=replace_observation(valid_case_id, observed_status="mismatch")
        )

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "observed_status_category_mismatch")

    def test_payload_capable_category_mismatch_maps_to_mismatch(self) -> None:
        case_ids, reason = discover_payload_audit_case_ids(DEFAULT_FIXTURE_ROOT)
        self.assertEqual(reason, "none")
        valid_case_id = next(case_id for case_id in case_ids if case_id.startswith("valid/"))

        summary = run_audit(
            case_observer=replace_observation(valid_case_id, payload_capable=False)
        )

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "payload_capable_category_mismatch")

    def test_missing_payload_availability_check_maps_to_mismatch(self) -> None:
        case_ids, reason = discover_payload_audit_case_ids(DEFAULT_FIXTURE_ROOT)
        self.assertEqual(reason, "none")
        valid_case_id = next(case_id for case_id in case_ids if case_id.startswith("valid/"))

        summary = run_audit(
            case_observer=replace_observation(
                valid_case_id,
                payload_availability_checked=False,
            )
        )

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "payload_availability_count_mismatch")

    def test_payload_not_suppressed_maps_to_mismatch(self) -> None:
        summary = run_audit(
            case_observer=replace_observation(
                SELECTED_FAIL_CLOSED_INVALID_CASE_IDS[0],
                payload_suppressed=False,
            )
        )

        self.assertEqual(summary.status, "mismatch")
        self.assertEqual(summary.reason_code, "payload_suppression_mismatch")

    def test_payload_body_emission_maps_to_fail_closed(self) -> None:
        summary = run_audit(
            case_observer=replace_observation(
                SELECTED_FAIL_CLOSED_INVALID_CASE_IDS[0],
                artifact_body_payload_emitted=True,
            )
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "artifact_body_payload_emitted")
        self.assertEqual(summary.artifact_body_payload_emitted_case_count, 1)
        self.assertTrue(summary.payload_body_emitted)

    def test_generated_policy_body_emission_maps_to_fail_closed(self) -> None:
        summary = run_audit(
            case_observer=replace_observation(
                SELECTED_FAIL_CLOSED_INVALID_CASE_IDS[0],
                generated_policy_body_emitted=True,
            )
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "generated_policy_body_emitted")

    def test_manifest_body_emission_maps_to_fail_closed(self) -> None:
        summary = run_audit(
            case_observer=replace_observation(
                SELECTED_FAIL_CLOSED_INVALID_CASE_IDS[0],
                manifest_body_emitted=True,
            )
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "manifest_body_emitted")

    def test_manifest_writer_invocation_maps_to_fail_closed(self) -> None:
        summary = run_audit(
            case_observer=replace_observation(
                SELECTED_FAIL_CLOSED_INVALID_CASE_IDS[0],
                manifest_writer_invoked=True,
            )
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "manifest_writer_invoked")

    def test_file_writing_maps_to_fail_closed(self) -> None:
        summary = run_audit(
            case_observer=replace_observation(
                SELECTED_FAIL_CLOSED_INVALID_CASE_IDS[0],
                file_writing_enabled=True,
            )
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "file_writing_enabled")

    def test_residue_maps_to_fail_closed(self) -> None:
        summary = run_audit(
            case_observer=replace_observation(
                SELECTED_FAIL_CLOSED_INVALID_CASE_IDS[0],
                residue_file_count=1,
            )
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "residue_detected")

    def test_production_readiness_claim_flag_maps_to_fail_closed(self) -> None:
        summary = run_audit(
            case_observer=replace_observation(
                SELECTED_FAIL_CLOSED_INVALID_CASE_IDS[0],
                production_readiness_claimed=True,
            )
        )

        self.assertEqual(summary.status, "fail_closed")
        self.assertEqual(summary.reason_code, "production_readiness_claimed")

    def test_public_summary_format_is_stable(self) -> None:
        rendered = format_public_summary(run_audit().to_public_dict())
        lines = rendered.splitlines()

        self.assertEqual(lines[0], f"mode={MODE}")
        self.assertIn(f"schema_version={SCHEMA_VERSION}", lines)
        self.assertIn(
            f"case_selection={CASE_SELECTION_PAYLOAD_AUDIT_WITHOUT_PAYLOAD_EMISSION}",
            lines,
        )
        self.assertIn("selected_case_count=36", lines)
        self.assertIn("payload_body_emitted=False", lines)
        assert_safe_output(self, rendered)

    def test_fixture_json_not_mutated(self) -> None:
        before = snapshot_fixture_tree(DEFAULT_FIXTURE_ROOT)

        summary = run_audit()

        after = snapshot_fixture_tree(DEFAULT_FIXTURE_ROOT)
        self.assertEqual(summary.status, "pass")
        self.assertEqual(before, after)

    def test_existing_all_valid_runner_behavior_remains_unchanged(self) -> None:
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

    def test_existing_fail_closed_runner_behavior_remains_unchanged(self) -> None:
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

    def test_existing_deferred_runner_behavior_remains_unchanged(self) -> None:
        summary = run_deferred_invalid_case_runtime_usage_error_mismatch_smoke(
            DEFAULT_FIXTURE_ROOT,
            case_selection=CASE_SELECTION_DEFERRED_INVALID_USAGE_ERROR_MISMATCH,
            summary_only=True,
            no_file_writing=True,
            no_manifest_writer=True,
            fail_closed_on_unsafe_output=True,
        )

        self.assertEqual(summary.status, "pass")
        self.assertEqual(summary.processed_case_count, 4)


def run_audit(
    *,
    fixture_root: Path = DEFAULT_FIXTURE_ROOT,
    case_selection: str = CASE_SELECTION_PAYLOAD_AUDIT_WITHOUT_PAYLOAD_EMISSION,
    summary_only: bool = True,
    no_file_writing: bool = True,
    no_manifest_writer: bool = True,
    fail_closed_on_forbidden_body: bool = True,
    selected_case_ids: list[str] | None = None,
    case_observer=None,
):
    return run_artifact_body_payload_audit_without_payload_emission(
        fixture_root,
        case_selection=case_selection,
        summary_only=summary_only,
        no_file_writing=no_file_writing,
        no_manifest_writer=no_manifest_writer,
        fail_closed_on_forbidden_body=fail_closed_on_forbidden_body,
        selected_case_ids=selected_case_ids,
        case_observer=case_observer,
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
            CASE_SELECTION_PAYLOAD_AUDIT_WITHOUT_PAYLOAD_EMISSION,
            "--summary-only",
            "--no-file-writing",
            "--no-manifest-writer",
            "--fail-closed-on-forbidden-body",
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def replace_observation(case_id: str, **changes):
    def observer(observed_case_id: str) -> PayloadAuditObservation:
        observation = observe_payload_audit_case(observed_case_id)
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


def count_valid(case_ids: list[str]) -> int:
    return sum(1 for case_id in case_ids if case_id.startswith("valid/"))


def count_invalid(case_ids: list[str]) -> int:
    return sum(1 for case_id in case_ids if case_id.startswith("invalid/"))


if __name__ == "__main__":
    unittest.main()
