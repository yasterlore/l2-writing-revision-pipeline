from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_artifact_body_generation_integration_fixture_validation import (
    validate_artifact_body_generation_integration_fixture_root,
)
from learner_state.frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation import (
    validate_safe_metadata_fixture_root,
)
from learner_state.frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation import (
    EXPECTED_FAIL_CLOSED_CASES,
    EXPECTED_INVALID_CASES,
    EXPECTED_MISMATCH_CASES,
    EXPECTED_PASS_CASES,
    EXPECTED_TOTAL_CASES,
    EXPECTED_TOTAL_JSON_FILES,
    EXPECTED_USAGE_ERROR_CASES,
    EXPECTED_VALID_CASES,
    JSON_FILES_PER_CASE,
    REQUIRED_FILES,
    summarize_runtime_invocation_fixture_validation,
    validate_runtime_invocation_fixture_case,
    validate_runtime_invocation_fixture_root,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation"
)
ACTIVE_FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_body_generation_integration"
)
PLANNED_SAFE_METADATA_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_body_generation_integration_"
    "planned_safe_metadata_v0_2"
)
MODULE = (
    "learner_state."
    "frozen_policy_generation_artifact_body_generation_runtime_invocation_"
    "fixture_validation"
)


class RuntimeInvocationFixtureValidationTests(unittest.TestCase):
    def test_root_aggregate_pass(self) -> None:
        summary = validate_runtime_invocation_fixture_root(FIXTURE_ROOT)
        payload = summarize_runtime_invocation_fixture_validation(
            summary, fixture_root=FIXTURE_ROOT
        )

        self.assertTrue(summary.all_matched)
        self.assertEqual(
            payload["mode"],
            "artifact_body_generation_runtime_invocation_fixture_validation",
        )
        self.assertEqual(
            payload["validation_schema_version"],
            "learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation_v0.1",
        )
        self.assertEqual(payload["total_cases"], EXPECTED_TOTAL_CASES)
        self.assertEqual(payload["valid_cases"], EXPECTED_VALID_CASES)
        self.assertEqual(payload["invalid_cases"], EXPECTED_INVALID_CASES)
        self.assertEqual(payload["total_json_files"], EXPECTED_TOTAL_JSON_FILES)
        self.assertEqual(payload["json_files_per_case"], JSON_FILES_PER_CASE)
        self.assertEqual(payload["matched_cases"], EXPECTED_TOTAL_CASES)
        self.assertEqual(payload["mismatched_cases"], 0)
        self.assertEqual(payload["input_error_cases"], 0)
        self.assertEqual(payload["pass_cases"], EXPECTED_PASS_CASES)
        self.assertEqual(payload["usage_error_cases"], EXPECTED_USAGE_ERROR_CASES)
        self.assertEqual(payload["fail_closed_cases"], EXPECTED_FAIL_CLOSED_CASES)
        self.assertEqual(payload["mismatch_cases"], EXPECTED_MISMATCH_CASES)
        self.assertFalse(payload["production_readiness_claimed"])
        self.assertFalse(payload["real_data_readiness_claimed"])
        self.assertFalse(payload["performance_claims_present"])
        assert_safe_output(self, json.dumps(payload, sort_keys=True))

    def test_every_case_has_seven_files(self) -> None:
        self.assertEqual(JSON_FILES_PER_CASE, 7)
        for case_dir in sorted(path for path in FIXTURE_ROOT.glob("*/*") if path.is_dir()):
            with self.subTest(case=case_label(case_dir)):
                self.assertEqual(
                    sorted(path.name for path in case_dir.glob("*.json")),
                    sorted(REQUIRED_FILES),
                )

    def test_all_json_parse(self) -> None:
        for path in sorted(FIXTURE_ROOT.rglob("*.json")):
            with self.subTest(path=path.name):
                with path.open(encoding="utf-8") as handle:
                    self.assertIsInstance(json.load(handle), dict)

    def test_valid_cases_map_to_pass(self) -> None:
        for case_dir in sorted((FIXTURE_ROOT / "valid").iterdir()):
            with self.subTest(case=case_dir.name):
                result = validate_runtime_invocation_fixture_case(case_dir)

                self.assertTrue(result.matched)
                self.assertEqual(result.expected_status, "pass")
                self.assertEqual(result.expected_reason_code, "none")

    def test_unsupported_schema_maps_to_usage_error(self) -> None:
        result = validate_case("invalid/invalid_unsupported_schema")

        self.assertTrue(result.matched)
        self.assertEqual(result.expected_status, "usage_error")
        self.assertEqual(result.expected_reason_code, "unsupported_schema")

    def test_mismatched_expected_status_maps_to_mismatch(self) -> None:
        result = validate_case("invalid/invalid_mismatched_expected_status")

        self.assertTrue(result.matched)
        self.assertEqual(result.expected_status, "mismatch")
        self.assertEqual(result.expected_reason_code, "mismatched_expected_status")

    def test_other_invalid_unsafe_cases_map_to_fail_closed(self) -> None:
        expected_reasons = {
            "invalid_absolute_path_present": "absolute_path_present",
            "invalid_active_root_merge_attempted": "active_root_merge_attempted",
            "invalid_artifact_body_payload_present": "artifact_body_payload_present",
            "invalid_expected_body_present": "expected_body_present",
            "invalid_file_writing_requested": "file_writing_requested",
            "invalid_generated_policy_body_present": "generated_policy_body_present",
            "invalid_logits_present": "logits_present",
            "invalid_manifest_body_present": "manifest_body_present",
            "invalid_manifest_writer_requested": "manifest_writer_requested",
            "invalid_no_oracle_forbidden_field": "no_oracle_forbidden_field",
            "invalid_performance_metric_body_present": (
                "performance_metric_body_present"
            ),
            "invalid_pointer_body_present": "pointer_body_present",
            "invalid_private_path_present": "private_path_present",
            "invalid_probabilities_present": "probabilities_present",
            "invalid_raw_learner_text_present": "raw_learner_text_present",
            "invalid_raw_rows_present": "raw_rows_present",
            "invalid_raw_stderr_body_present": "raw_stderr_body_present",
            "invalid_raw_stdout_body_present": "raw_stdout_body_present",
            "invalid_real_data_marker_present": "real_data_marker_present",
            "invalid_request_body_present": "request_body_present",
            "invalid_unsafe_artifact_body_runtime_mode": (
                "unsafe_artifact_body_runtime_mode"
            ),
            "invalid_unsafe_output_residue_risk": "unsafe_output_residue_risk",
        }

        for case_name, reason in sorted(expected_reasons.items()):
            with self.subTest(case=case_name):
                result = validate_case(f"invalid/{case_name}")

                self.assertTrue(result.matched)
                self.assertEqual(result.expected_status, "fail_closed")
                self.assertEqual(result.expected_reason_code, reason)

    def test_reason_code_counts_are_count_only_and_expected(self) -> None:
        payload = summarize_runtime_invocation_fixture_validation(
            validate_runtime_invocation_fixture_root(FIXTURE_ROOT),
            fixture_root=FIXTURE_ROOT,
        )
        reason_counts = payload["reason_code_counts"]

        self.assertEqual(reason_counts["none"], 6)
        self.assertEqual(reason_counts["unsupported_schema"], 1)
        self.assertEqual(reason_counts["mismatched_expected_status"], 1)
        self.assertEqual(reason_counts["request_body_present"], 1)
        self.assertEqual(reason_counts["probabilities_present"], 1)
        self.assertEqual(len(reason_counts), 25)
        self.assertTrue(all(isinstance(value, int) for value in reason_counts.values()))

    def test_validator_output_includes_required_public_safe_flags(self) -> None:
        payload = summarize_runtime_invocation_fixture_validation(
            validate_runtime_invocation_fixture_root(FIXTURE_ROOT),
            fixture_root=FIXTURE_ROOT,
        )

        for key in (
            "content_suppressed",
            "body_suppressed",
            "metadata_only_checked",
            "synthetic_only_checked",
            "no_oracle_checked",
            "no_request_body",
            "no_pointer_body",
            "no_expected_body",
            "no_artifact_body_payload",
            "no_manifest_body",
            "no_generated_policy_body",
            "no_raw_stdout_body",
            "no_raw_stderr_body",
            "no_raw_rows",
            "no_logits_dump",
            "no_probabilities_dump",
            "no_private_paths",
            "no_absolute_paths",
            "no_raw_learner_text",
            "no_real_participant_data",
            "no_performance_metric_body",
            "file_writing_checked",
            "manifest_writer_integration_checked",
            "artifact_body_generation_runtime_invocation_checked",
        ):
            with self.subTest(key=key):
                self.assertIs(payload[key], True)

    def test_output_does_not_include_raw_body_fields_or_path_values(self) -> None:
        marker = "synthetic_forbidden_payload_marker"
        with temp_root_copy() as root:
            target = (
                root
                / "valid/valid_minimal_safe_metadata_runtime_invocation"
                / "artifact_body_request_metadata.json"
            )
            payload = json.loads(target.read_text(encoding="utf-8"))
            payload["request_body"] = marker
            target.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")

            summary = validate_runtime_invocation_fixture_root(root)
            rendered = json.dumps(
                summarize_runtime_invocation_fixture_validation(summary, fixture_root=root),
                sort_keys=True,
            )

        self.assertFalse(summary.all_matched)
        self.assertNotIn(marker, rendered)
        assert_safe_output(self, rendered)

    def test_missing_root_maps_to_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "missing"
            summary = validate_runtime_invocation_fixture_root(root)

        self.assertFalse(summary.all_matched)
        self.assertEqual(summary.root_errors, ("fixture_root_missing",))
        self.assertEqual(summary.input_error_cases, 0)

    def test_missing_required_file_maps_to_input_error(self) -> None:
        with temp_root_copy() as root:
            target = (
                root
                / "valid/valid_minimal_safe_metadata_runtime_invocation"
                / "expected_error.json"
            )
            target.unlink()

            summary = validate_runtime_invocation_fixture_root(root)

        self.assertFalse(summary.all_matched)
        self.assertEqual(summary.input_error_cases, 1)
        self.assertEqual(summary.missing_required_file_cases, 1)
        self.assertIn("missing_required_metadata_file", summary.reason_code_counts)

    def test_unexpected_json_file_maps_to_input_error(self) -> None:
        with temp_root_copy() as root:
            target = (
                root
                / "valid/valid_minimal_safe_metadata_runtime_invocation"
                / "unexpected_metadata.json"
            )
            target.write_text('{"schema_version":"synthetic_extra_v0"}\n', encoding="utf-8")

            summary = validate_runtime_invocation_fixture_root(root)

        self.assertFalse(summary.all_matched)
        self.assertEqual(summary.input_error_cases, 1)
        self.assertEqual(summary.unexpected_json_file_cases, 1)
        self.assertIn("unexpected_json_file", summary.reason_code_counts)

    def test_invalid_json_maps_to_input_error(self) -> None:
        with temp_root_copy() as root:
            target = (
                root
                / "valid/valid_minimal_safe_metadata_runtime_invocation"
                / "case_metadata.json"
            )
            target.write_text("{not json}\n", encoding="utf-8")

            summary = validate_runtime_invocation_fixture_root(root)

        self.assertFalse(summary.all_matched)
        self.assertEqual(summary.input_error_cases, 1)
        self.assertIn("malformed_json", summary.reason_code_counts)

    def test_duplicate_case_id_maps_to_input_error(self) -> None:
        with temp_root_copy() as root:
            source = root / "valid/valid_minimal_safe_metadata_runtime_invocation"
            duplicate = root / "valid/valid_duplicate_runtime_invocation"
            shutil.copytree(source, duplicate)

            summary = validate_runtime_invocation_fixture_root(root)

        self.assertFalse(summary.all_matched)
        self.assertIn("total_cases_mismatch", summary.root_errors)
        self.assertGreaterEqual(summary.input_error_cases, 1)

    def test_existing_active_root_validator_still_passes(self) -> None:
        summary = validate_artifact_body_generation_integration_fixture_root(
            ACTIVE_FIXTURE_ROOT
        )

        self.assertTrue(summary.all_matched)
        self.assertEqual(summary.total_cases, 28)
        self.assertEqual(summary.actual_json_files, 196)

    def test_existing_planned_safe_metadata_validator_still_passes(self) -> None:
        summary = validate_safe_metadata_fixture_root(PLANNED_SAFE_METADATA_ROOT)

        self.assertTrue(summary.all_matched)
        self.assertEqual(summary.total_cases, 24)
        self.assertEqual(summary.actual_json_files, 168)

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

        self.assertIn(
            "mode=artifact_body_generation_runtime_invocation_fixture_validation",
            completed.stdout,
        )
        self.assertIn("total_cases=30", completed.stdout)
        self.assertIn("fail_closed_cases=22", completed.stdout)
        self.assertIn("reason_code_counts=", completed.stdout)
        assert_safe_output(self, completed.stdout)
        assert_safe_output(self, completed.stderr)

    def test_no_file_writing_or_residue(self) -> None:
        before = sorted(path.relative_to(FIXTURE_ROOT) for path in FIXTURE_ROOT.rglob("*"))
        summary = validate_runtime_invocation_fixture_root(FIXTURE_ROOT)
        after = sorted(path.relative_to(FIXTURE_ROOT) for path in FIXTURE_ROOT.rglob("*"))

        self.assertTrue(summary.all_matched)
        self.assertEqual(before, after)


def validate_case(case_id: str):
    return validate_runtime_invocation_fixture_case(FIXTURE_ROOT / case_id)


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
