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
    summarize_safe_metadata_fixture_validation,
    validate_safe_metadata_fixture_case,
    validate_safe_metadata_fixture_root,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_body_generation_integration_"
    "planned_safe_metadata_v0_2"
)
ACTIVE_FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_body_generation_integration"
)
MODULE = (
    "learner_state."
    "frozen_policy_generation_artifact_body_generation_runtime_integration_"
    "safe_metadata_fixture_validation"
)


class SafeMetadataFixtureValidationTests(unittest.TestCase):
    def test_planned_root_aggregate_pass(self) -> None:
        summary = validate_safe_metadata_fixture_root(FIXTURE_ROOT)
        payload = summarize_safe_metadata_fixture_validation(
            summary, fixture_root=FIXTURE_ROOT
        )

        self.assertTrue(summary.all_matched)
        self.assertEqual(payload["mode"], "safe_metadata_fixture_validation")
        self.assertEqual(
            payload["validation_schema_version"],
            "learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation_v0.1",
        )
        self.assertTrue(payload["planned_root"])
        self.assertEqual(payload["total_cases"], EXPECTED_TOTAL_CASES)
        self.assertEqual(payload["valid_cases"], EXPECTED_VALID_CASES)
        self.assertEqual(payload["invalid_cases"], EXPECTED_INVALID_CASES)
        self.assertEqual(payload["total_json_files"], EXPECTED_TOTAL_JSON_FILES)
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

    def test_valid_cases_map_to_pass(self) -> None:
        for case_dir in sorted((FIXTURE_ROOT / "valid").iterdir()):
            with self.subTest(case=case_dir.name):
                result = validate_safe_metadata_fixture_case(case_dir)

                self.assertTrue(result.matched)
                self.assertEqual(result.expected_status, "pass")
                self.assertEqual(result.expected_reason_code, "none")

    def test_unsupported_schema_maps_to_usage_error(self) -> None:
        result = validate_case("invalid/invalid_safe_metadata_unsupported_schema")

        self.assertTrue(result.matched)
        self.assertEqual(result.expected_status, "usage_error")
        self.assertEqual(result.expected_reason_code, "unsupported_schema")

    def test_mismatched_expected_status_maps_to_mismatch(self) -> None:
        result = validate_case("invalid/invalid_safe_metadata_mismatched_expected_status")

        self.assertTrue(result.matched)
        self.assertEqual(result.expected_status, "mismatch")
        self.assertEqual(result.expected_reason_code, "mismatched_expected_status")

    def test_each_unsafe_marker_case_maps_to_fail_closed(self) -> None:
        expected_reasons = {
            "invalid_safe_metadata_absolute_path_present": "absolute_path_present",
            "invalid_safe_metadata_artifact_body_payload_present": (
                "artifact_body_payload_present"
            ),
            "invalid_safe_metadata_expected_body_present": "expected_body_present",
            "invalid_safe_metadata_file_writing_requested": "file_writing_requested",
            "invalid_safe_metadata_generated_policy_body_present": (
                "generated_policy_body_present"
            ),
            "invalid_safe_metadata_logits_present": "logits_present",
            "invalid_safe_metadata_manifest_body_present": "manifest_body_present",
            "invalid_safe_metadata_manifest_writer_requested": (
                "manifest_writer_requested"
            ),
            "invalid_safe_metadata_performance_metric_body_present": (
                "performance_metric_body_present"
            ),
            "invalid_safe_metadata_pointer_body_present": "pointer_body_present",
            "invalid_safe_metadata_private_path_present": "private_path_present",
            "invalid_safe_metadata_raw_learner_text_present": (
                "raw_learner_text_present"
            ),
            "invalid_safe_metadata_raw_rows_present": "raw_rows_present",
            "invalid_safe_metadata_raw_stderr_body_present": "raw_stderr_body_present",
            "invalid_safe_metadata_raw_stdout_body_present": "raw_stdout_body_present",
            "invalid_safe_metadata_real_data_marker_present": "real_data_marker_present",
            "invalid_safe_metadata_request_body_present": "request_body_present",
            "invalid_safe_metadata_unsafe_output_surface": "unsafe_output_surface",
        }

        for case_name, reason in sorted(expected_reasons.items()):
            with self.subTest(case=case_name):
                result = validate_case(f"invalid/{case_name}")

                self.assertTrue(result.matched)
                self.assertEqual(result.expected_status, "fail_closed")
                self.assertEqual(result.expected_reason_code, reason)

    def test_missing_required_file_maps_to_usage_error(self) -> None:
        with temp_root_copy() as root:
            target = (
                root
                / "valid/valid_safe_metadata_explicit_runtime_bridge"
                / "expected_error.json"
            )
            target.unlink()

            summary = validate_safe_metadata_fixture_root(root)

        self.assertFalse(summary.all_matched)
        self.assertEqual(summary.input_error_cases, 1)
        self.assertEqual(summary.missing_required_file_cases, 1)
        self.assertIn("missing_required_metadata_file", summary.reason_code_counts)

    def test_extra_unexpected_file_maps_to_usage_error(self) -> None:
        with temp_root_copy() as root:
            target = (
                root
                / "valid/valid_safe_metadata_explicit_runtime_bridge"
                / "unexpected_metadata.json"
            )
            target.write_text('{"schema_version":"synthetic_extra_v0"}\n', encoding="utf-8")

            summary = validate_safe_metadata_fixture_root(root)

        self.assertFalse(summary.all_matched)
        self.assertEqual(summary.input_error_cases, 1)
        self.assertEqual(summary.unexpected_json_file_cases, 1)
        self.assertIn("unexpected_json_file", summary.reason_code_counts)

    def test_invalid_json_maps_to_usage_error(self) -> None:
        with temp_root_copy() as root:
            target = (
                root
                / "valid/valid_safe_metadata_explicit_runtime_bridge"
                / "case_metadata.json"
            )
            target.write_text("{not json}\n", encoding="utf-8")

            summary = validate_safe_metadata_fixture_root(root)

        self.assertFalse(summary.all_matched)
        self.assertEqual(summary.input_error_cases, 1)
        self.assertIn("malformed_json", summary.reason_code_counts)

    def test_output_suppresses_unsafe_values(self) -> None:
        marker = "synthetic_forbidden_payload_marker"
        with temp_root_copy() as root:
            target = (
                root
                / "valid/valid_safe_metadata_explicit_runtime_bridge"
                / "artifact_body_request_metadata.json"
            )
            payload = json.loads(target.read_text(encoding="utf-8"))
            payload["request_body"] = marker
            target.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")

            summary = validate_safe_metadata_fixture_root(root)
            rendered = json.dumps(
                summarize_safe_metadata_fixture_validation(summary, fixture_root=root),
                sort_keys=True,
            )

        self.assertFalse(summary.all_matched)
        self.assertNotIn(marker, rendered)
        assert_safe_output(self, rendered)

    def test_reason_code_counts_deterministic(self) -> None:
        payload = summarize_safe_metadata_fixture_validation(
            validate_safe_metadata_fixture_root(FIXTURE_ROOT),
            fixture_root=FIXTURE_ROOT,
        )
        reason_counts = payload["reason_code_counts"]

        self.assertEqual(reason_counts["none"], 4)
        self.assertEqual(reason_counts["unsupported_schema"], 1)
        self.assertEqual(reason_counts["mismatched_expected_status"], 1)
        self.assertEqual(reason_counts["artifact_body_payload_present"], 1)
        self.assertEqual(len(reason_counts), 21)

    def test_traversal_order_deterministic(self) -> None:
        first = summarize_safe_metadata_fixture_validation(
            validate_safe_metadata_fixture_root(FIXTURE_ROOT),
            fixture_root=FIXTURE_ROOT,
        )
        second = summarize_safe_metadata_fixture_validation(
            validate_safe_metadata_fixture_root(FIXTURE_ROOT),
            fixture_root=FIXTURE_ROOT,
        )

        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))

    def test_active_root_remains_unaffected(self) -> None:
        summary = validate_artifact_body_generation_integration_fixture_root(
            ACTIVE_FIXTURE_ROOT
        )

        self.assertTrue(summary.all_matched)
        self.assertEqual(summary.total_cases, 28)
        self.assertEqual(summary.actual_json_files, 196)

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

        self.assertIn("mode=safe_metadata_fixture_validation", completed.stdout)
        self.assertIn("total_cases=24", completed.stdout)
        self.assertIn("fail_closed_cases=18", completed.stdout)
        self.assertIn("reason_code_counts=", completed.stdout)
        assert_safe_output(self, completed.stdout)
        assert_safe_output(self, completed.stderr)

    def test_no_file_writing_or_residue(self) -> None:
        before = sorted(path.relative_to(FIXTURE_ROOT) for path in FIXTURE_ROOT.rglob("*"))
        summary = validate_safe_metadata_fixture_root(FIXTURE_ROOT)
        after = sorted(path.relative_to(FIXTURE_ROOT) for path in FIXTURE_ROOT.rglob("*"))

        self.assertTrue(summary.all_matched)
        self.assertEqual(before, after)


def validate_case(case_id: str):
    return validate_safe_metadata_fixture_case(FIXTURE_ROOT / case_id)


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
