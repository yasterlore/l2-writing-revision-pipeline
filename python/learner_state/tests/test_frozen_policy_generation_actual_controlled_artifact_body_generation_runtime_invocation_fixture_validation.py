from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validation import (
    EXPECTED_FAIL_CLOSED_CASES,
    EXPECTED_INVALID_CASES,
    EXPECTED_MISMATCH_CASES,
    EXPECTED_PASS_CASES,
    EXPECTED_TOTAL_CASES,
    EXPECTED_TOTAL_JSON_FILES,
    EXPECTED_USAGE_ERROR_CASES,
    EXPECTED_VALID_CASES,
    INVALID_CASE_LABELS,
    JSON_FILES_PER_CASE,
    REQUIRED_FILES,
    VALID_CASE_LABELS,
    summarize_actual_controlled_fixture_validation,
    validate_actual_controlled_fixture_case,
    validate_actual_controlled_fixture_root,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled"
)
MODULE = (
    "learner_state."
    "frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_"
    "invocation_fixture_validation"
)


class ActualControlledFixtureValidationTests(unittest.TestCase):
    def test_direct_aggregate_counts_match_expected(self) -> None:
        summary = validate_actual_controlled_fixture_root(FIXTURE_ROOT)
        payload = summarize_actual_controlled_fixture_validation(
            summary, fixture_root=FIXTURE_ROOT
        )

        self.assertTrue(summary.all_matched)
        self.assertEqual(
            payload["mode"],
            "artifact_body_generation_runtime_invocation_actual_controlled_fixture_validation",
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
        self.assertEqual(payload["physical_missing_required_file_cases"], 0)
        self.assertEqual(payload["physical_malformed_json_cases"], 0)
        self.assertFalse(payload["production_readiness_claimed"])
        self.assertFalse(payload["real_data_readiness_claimed"])
        self.assertFalse(payload["performance_claims_present"])
        assert_safe_output(self, json.dumps(payload, sort_keys=True))

    def test_exact_seven_file_layout_is_enforced(self) -> None:
        self.assertEqual(JSON_FILES_PER_CASE, 7)
        for case_dir in sorted(path for path in FIXTURE_ROOT.glob("*/*") if path.is_dir()):
            with self.subTest(case=case_label(case_dir)):
                self.assertEqual(
                    sorted(path.name for path in case_dir.glob("*.json")),
                    sorted(REQUIRED_FILES),
                )

    def test_all_json_parse_in_canonical_root(self) -> None:
        for path in sorted(FIXTURE_ROOT.rglob("*.json")):
            with self.subTest(path=path.name):
                with path.open(encoding="utf-8") as handle:
                    self.assertIsInstance(json.load(handle), dict)

    def test_required_case_taxonomy_exists(self) -> None:
        actual_cases = {
            case_label(path) for path in FIXTURE_ROOT.glob("*/*") if path.is_dir()
        }

        self.assertEqual(actual_cases, VALID_CASE_LABELS | INVALID_CASE_LABELS)

    def test_valid_cases_map_to_pass(self) -> None:
        for case_dir in sorted((FIXTURE_ROOT / "valid").iterdir()):
            with self.subTest(case=case_dir.name):
                result = validate_actual_controlled_fixture_case(case_dir)

                self.assertTrue(result.matched)
                self.assertEqual(result.expected_status, "pass")
                self.assertEqual(result.expected_reason_code, "none")

    def test_usage_error_markers_map_to_usage_error(self) -> None:
        expected = {
            "invalid_unsupported_schema": "unsupported_schema",
            "invalid_missing_required_metadata_file": "missing_required_metadata_file",
            "invalid_malformed_metadata_json": "malformed_metadata_json",
        }
        for case_name, reason in sorted(expected.items()):
            with self.subTest(case=case_name):
                result = validate_case(f"invalid/{case_name}")

                self.assertTrue(result.matched)
                self.assertEqual(result.expected_status, "usage_error")
                self.assertEqual(result.expected_reason_code, reason)

    def test_mismatched_expected_status_marker_maps_to_mismatch(self) -> None:
        result = validate_case("invalid/invalid_mismatched_expected_status")

        self.assertTrue(result.matched)
        self.assertEqual(result.expected_status, "mismatch")
        self.assertEqual(result.expected_reason_code, "expected_status_mismatch")

    def test_unsafe_invalid_markers_map_to_fail_closed(self) -> None:
        fail_closed_cases = sorted(
            case_id
            for case_id in INVALID_CASE_LABELS
            if case_id
            not in {
                "invalid/invalid_unsupported_schema",
                "invalid/invalid_missing_required_metadata_file",
                "invalid/invalid_malformed_metadata_json",
                "invalid/invalid_mismatched_expected_status",
            }
        )
        for case_id in fail_closed_cases:
            with self.subTest(case=case_id):
                result = validate_case(case_id)

                self.assertTrue(result.matched)
                self.assertEqual(result.expected_status, "fail_closed")
                self.assertNotEqual(result.expected_reason_code, "none")

    def test_reason_code_counts_are_count_only(self) -> None:
        payload = summarize_actual_controlled_fixture_validation(
            validate_actual_controlled_fixture_root(FIXTURE_ROOT),
            fixture_root=FIXTURE_ROOT,
        )
        counts = payload["reason_code_counts"]

        self.assertEqual(counts["none"], 6)
        self.assertEqual(counts["unsupported_schema"], 1)
        self.assertEqual(counts["missing_required_metadata_file"], 1)
        self.assertEqual(counts["malformed_metadata_json"], 1)
        self.assertEqual(counts["expected_status_mismatch"], 1)
        self.assertEqual(len(counts), 31)
        self.assertTrue(all(isinstance(value, int) for value in counts.values()))

    def test_output_includes_required_public_safe_flags(self) -> None:
        payload = summarize_actual_controlled_fixture_validation(
            validate_actual_controlled_fixture_root(FIXTURE_ROOT),
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
            "actual_controlled_runtime_invocation_checked",
        ):
            with self.subTest(key=key):
                self.assertIs(payload[key], True)

    def test_output_does_not_include_raw_body_fields_or_path_values(self) -> None:
        marker = "synthetic_payload_value_marker"
        with temp_root_copy() as root:
            target = (
                root
                / "valid/valid_actual_controlled_safe_metadata_invocation"
                / "artifact_body_runtime_request_metadata.json"
            )
            payload = json.loads(target.read_text(encoding="utf-8"))
            payload["request_body"] = marker
            target.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")

            summary = validate_actual_controlled_fixture_root(root)
            rendered = json.dumps(
                summarize_actual_controlled_fixture_validation(summary, fixture_root=root),
                sort_keys=True,
            )

        self.assertFalse(summary.all_matched)
        self.assertNotIn(marker, rendered)
        assert_safe_output(self, rendered)

    def test_physical_missing_file_in_temp_copy_maps_to_input_error(self) -> None:
        with temp_root_copy() as root:
            target = (
                root
                / "valid/valid_actual_controlled_safe_metadata_invocation"
                / "expected_error.json"
            )
            target.unlink()

            summary = validate_actual_controlled_fixture_root(root)

        self.assertFalse(summary.all_matched)
        self.assertEqual(summary.input_error_cases, 1)
        self.assertEqual(summary.physical_missing_required_file_cases, 1)
        self.assertIn("missing_required_metadata_file", summary.reason_code_counts)

    def test_physical_malformed_json_in_temp_copy_maps_to_input_error(self) -> None:
        with temp_root_copy() as root:
            target = (
                root
                / "valid/valid_actual_controlled_safe_metadata_invocation"
                / "case_metadata.json"
            )
            target.write_text("{not json}\n", encoding="utf-8")

            summary = validate_actual_controlled_fixture_root(root)

        self.assertFalse(summary.all_matched)
        self.assertEqual(summary.input_error_cases, 1)
        self.assertEqual(summary.physical_malformed_json_cases, 1)
        self.assertIn("malformed_json", summary.reason_code_counts)

    def test_unexpected_json_file_in_temp_copy_maps_to_input_error(self) -> None:
        with temp_root_copy() as root:
            target = (
                root
                / "valid/valid_actual_controlled_safe_metadata_invocation"
                / "unexpected_metadata.json"
            )
            target.write_text('{"schema_version":"synthetic_extra_v0"}\n', encoding="utf-8")

            summary = validate_actual_controlled_fixture_root(root)

        self.assertFalse(summary.all_matched)
        self.assertEqual(summary.input_error_cases, 1)
        self.assertEqual(summary.unexpected_json_file_cases, 1)
        self.assertIn("unexpected_json_file", summary.reason_code_counts)

    def test_duplicate_case_id_in_temp_copy_maps_to_input_error(self) -> None:
        with temp_root_copy() as root:
            source = root / "valid/valid_actual_controlled_safe_metadata_invocation"
            duplicate = root / "valid/valid_actual_controlled_duplicate"
            shutil.copytree(source, duplicate)

            summary = validate_actual_controlled_fixture_root(root)

        self.assertFalse(summary.all_matched)
        self.assertIn("case_taxonomy_mismatch", summary.root_errors)
        self.assertIn("duplicate_case_id", summary.root_errors)
        self.assertGreaterEqual(summary.input_error_cases, 1)

    def test_no_fixture_json_mutation(self) -> None:
        before = {
            path.relative_to(FIXTURE_ROOT): path.read_text(encoding="utf-8")
            for path in sorted(FIXTURE_ROOT.rglob("*.json"))
        }
        summary = validate_actual_controlled_fixture_root(FIXTURE_ROOT)
        after = {
            path.relative_to(FIXTURE_ROOT): path.read_text(encoding="utf-8")
            for path in sorted(FIXTURE_ROOT.rglob("*.json"))
        }

        self.assertTrue(summary.all_matched)
        self.assertEqual(before, after)

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
            "mode=artifact_body_generation_runtime_invocation_actual_controlled_fixture_validation",
            completed.stdout,
        )
        self.assertIn("total_cases=36", completed.stdout)
        self.assertIn("fail_closed_cases=26", completed.stdout)
        self.assertIn("reason_code_counts=", completed.stdout)
        assert_safe_output(self, completed.stdout)
        assert_safe_output(self, completed.stderr)


def validate_case(case_id: str):
    return validate_actual_controlled_fixture_case(FIXTURE_ROOT / case_id)


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


def assert_safe_output(test_case: unittest.TestCase, rendered: str) -> None:
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
            '"performance_metric_body":',
            "raw GitHub Actions logs",
            "full job output",
            "copied GitHub log blocks",
        ],
    )


if __name__ == "__main__":
    unittest.main()
