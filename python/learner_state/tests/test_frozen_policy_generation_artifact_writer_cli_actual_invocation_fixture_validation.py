from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation import (
    EXPECTED_FAIL_CLOSED_CASES,
    EXPECTED_INVALID_CASES,
    EXPECTED_MISMATCH_CASES,
    EXPECTED_PASS_CASES,
    EXPECTED_TOTAL_CASES,
    EXPECTED_TOTAL_JSON_FILES,
    EXPECTED_USAGE_ERROR_CASES,
    EXPECTED_VALID_CASES,
    summarize_artifact_writer_cli_actual_invocation_fixture_validation,
    validate_artifact_writer_cli_actual_invocation_fixture_case,
    validate_artifact_writer_cli_actual_invocation_fixture_root,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation"
)
MODULE = (
    "learner_state."
    "frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation"
)


class ArtifactWriterCliActualInvocationFixtureValidationTests(unittest.TestCase):
    def test_full_root_validation_success(self) -> None:
        summary = validate_artifact_writer_cli_actual_invocation_fixture_root(
            FIXTURE_ROOT
        )
        payload = summarize_artifact_writer_cli_actual_invocation_fixture_validation(
            summary
        )

        self.assertTrue(summary.all_matched)
        self.assertEqual(payload["total_cases"], EXPECTED_TOTAL_CASES)
        self.assertEqual(payload["valid_cases"], EXPECTED_VALID_CASES)
        self.assertEqual(payload["invalid_cases"], EXPECTED_INVALID_CASES)
        self.assertEqual(payload["total_json_files"], EXPECTED_TOTAL_JSON_FILES)
        self.assertEqual(payload["json_files_per_case"], 6)
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

    def test_all_valid_cases_pass(self) -> None:
        summary = validate_artifact_writer_cli_actual_invocation_fixture_root(
            FIXTURE_ROOT
        )
        valid_results = [
            result for result in summary.case_results if result.case_kind == "valid"
        ]

        self.assertEqual(len(valid_results), EXPECTED_VALID_CASES)
        self.assertTrue(all(result.matched for result in valid_results))
        self.assertTrue(
            all(result.expected_status == "pass" for result in valid_results)
        )
        self.assertTrue(
            all(result.expected_reason_code == "none" for result in valid_results)
        )

    def test_all_invalid_cases_match_expected_status_and_reason(self) -> None:
        summary = validate_artifact_writer_cli_actual_invocation_fixture_root(
            FIXTURE_ROOT
        )
        invalid_results = [
            result for result in summary.case_results if result.case_kind == "invalid"
        ]

        self.assertEqual(len(invalid_results), EXPECTED_INVALID_CASES)
        self.assertTrue(all(result.matched for result in invalid_results))
        self.assertEqual(
            {result.expected_status for result in invalid_results},
            {"fail_closed", "usage_error", "mismatch"},
        )
        self.assertIn(
            "request_body_present",
            {result.expected_reason_code for result in invalid_results},
        )
        self.assertIn(
            "duplicate_case_id",
            {result.expected_reason_code for result in invalid_results},
        )

    def test_specific_expected_failure_cases_are_detected(self) -> None:
        expectations = {
            "invalid/invalid_duplicate_case_id": ("usage_error", "duplicate_case_id"),
            "invalid/invalid_missing_required_metadata_file": (
                "usage_error",
                "missing_required_metadata_file",
            ),
            "invalid/invalid_mismatched_expected_status": (
                "mismatch",
                "mismatched_expected_status",
            ),
            "invalid/invalid_unsupported_artifact_writer_schema": (
                "usage_error",
                "unsupported_artifact_writer_schema",
            ),
        }

        for case_id, (status, reason) in expectations.items():
            with self.subTest(case_id=case_id):
                result = validate_artifact_writer_cli_actual_invocation_fixture_case(
                    FIXTURE_ROOT / case_id
                )
                self.assertTrue(result.matched)
                self.assertEqual(result.expected_status, status)
                self.assertEqual(result.expected_reason_code, reason)

    def test_forbidden_body_sentinels_fail_closed(self) -> None:
        for case_id, reason in (
            ("invalid/invalid_request_body_present", "request_body_present"),
            ("invalid/invalid_pointer_body_present", "pointer_body_present"),
            ("invalid/invalid_expected_body_present", "expected_body_present"),
            (
                "invalid/invalid_artifact_body_payload_present",
                "artifact_body_payload_present",
            ),
            ("invalid/invalid_manifest_body_present", "manifest_body_present"),
            (
                "invalid/invalid_generated_policy_body_present",
                "generated_policy_body_present",
            ),
        ):
            with self.subTest(case_id=case_id):
                result = validate_artifact_writer_cli_actual_invocation_fixture_case(
                    FIXTURE_ROOT / case_id
                )
                self.assertTrue(result.matched)
                self.assertEqual(result.expected_status, "fail_closed")
                self.assertEqual(result.expected_reason_code, reason)

    def test_no_oracle_and_quality_sentinels_fail_closed(self) -> None:
        for case_id, reason in (
            ("invalid/invalid_final_text_present", "final_text_present"),
            (
                "invalid/invalid_observed_after_text_present",
                "observed_after_text_present",
            ),
            ("invalid/invalid_gold_label_present", "gold_label_present"),
            (
                "invalid/invalid_post_hoc_annotation_present",
                "post_hoc_annotation_present",
            ),
            ("invalid/invalid_raw_learner_text_present", "raw_learner_text_present"),
            ("invalid/invalid_raw_rows_present", "raw_rows_present"),
            ("invalid/invalid_logits_present", "logits_present"),
        ):
            with self.subTest(case_id=case_id):
                result = validate_artifact_writer_cli_actual_invocation_fixture_case(
                    FIXTURE_ROOT / case_id
                )
                self.assertTrue(result.matched)
                self.assertEqual(result.expected_status, "fail_closed")
                self.assertEqual(result.expected_reason_code, reason)

    def test_path_and_output_sentinels_fail_closed(self) -> None:
        for case_id, reason in (
            ("invalid/invalid_private_path_present", "private_path_present"),
            ("invalid/invalid_absolute_path_present", "absolute_path_present"),
            ("invalid/invalid_raw_stdout_body_present", "raw_stdout_body_present"),
            ("invalid/invalid_raw_stderr_body_present", "raw_stderr_body_present"),
        ):
            with self.subTest(case_id=case_id):
                result = validate_artifact_writer_cli_actual_invocation_fixture_case(
                    FIXTURE_ROOT / case_id
                )
                self.assertTrue(result.matched)
                self.assertEqual(result.expected_status, "fail_closed")
                self.assertEqual(result.expected_reason_code, reason)

    def test_downstream_boundary_sentinels_fail_closed(self) -> None:
        for case_id, reason in (
            (
                "invalid/invalid_artifact_body_generation_invoked",
                "artifact_body_generation_invoked",
            ),
            ("invalid/invalid_manifest_writer_invoked", "manifest_writer_invoked"),
            (
                "invalid/invalid_unsafe_actual_invocation_output",
                "unsafe_actual_invocation_output",
            ),
            ("invalid/invalid_file_writing_requested", "file_writing_requested"),
        ):
            with self.subTest(case_id=case_id):
                result = validate_artifact_writer_cli_actual_invocation_fixture_case(
                    FIXTURE_ROOT / case_id
                )
                self.assertTrue(result.matched)
                self.assertEqual(result.expected_status, "fail_closed")
                self.assertEqual(result.expected_reason_code, reason)

    def test_valid_cases_contain_no_forbidden_sentinels(self) -> None:
        for case_dir in sorted((FIXTURE_ROOT / "valid").iterdir()):
            if not case_dir.is_dir():
                continue
            result = validate_artifact_writer_cli_actual_invocation_fixture_case(
                case_dir
            )
            self.assertTrue(result.matched)
            self.assertEqual(result.expected_reason_code, "none")
            assert_safe_output(self, json.dumps(result.to_safe_dict(), sort_keys=True))

    def test_deterministic_sorted_traversal(self) -> None:
        first = validate_artifact_writer_cli_actual_invocation_fixture_root(
            FIXTURE_ROOT
        )
        second = validate_artifact_writer_cli_actual_invocation_fixture_root(
            FIXTURE_ROOT
        )

        first_ids = [result.case_id for result in first.case_results]
        second_ids = [result.case_id for result in second.case_results]
        self.assertEqual(first_ids, sorted(first_ids))
        self.assertEqual(first_ids, second_ids)

    def test_required_file_missing_in_temp_copy_fails(self) -> None:
        with temp_root_copy() as root:
            target = (
                root
                / "valid/valid_minimal_metadata_only_actual_invocation_plan"
                / "runtime_request_metadata.json"
            )
            target.unlink()

            summary = validate_artifact_writer_cli_actual_invocation_fixture_root(root)

        self.assertFalse(summary.all_matched)
        self.assertEqual(summary.input_error_cases, 1)
        self.assertEqual(summary.missing_required_file_cases, 2)
        self.assertIn("total_json_file_count_mismatch", summary.root_errors)

    def test_duplicate_case_id_in_temp_copy_fails(self) -> None:
        with temp_root_copy() as root:
            source = (
                root
                / "valid/valid_minimal_metadata_only_actual_invocation_plan"
                / "case_metadata.json"
            )
            duplicate = (
                root
                / "valid/valid_artifact_writer_cli_summary_body_free"
                / "case_metadata.json"
            )
            data = load_json(source)
            write_json(duplicate, data)

            summary = validate_artifact_writer_cli_actual_invocation_fixture_root(root)

        self.assertFalse(summary.all_matched)
        self.assertEqual(summary.duplicate_case_id_cases, 2)
        self.assertIn("duplicate_case_id_detected", summary.root_errors)

    def test_forbidden_actual_key_in_temp_copy_fails(self) -> None:
        with temp_root_copy() as root:
            path = (
                root
                / "valid/valid_minimal_metadata_only_actual_invocation_plan"
                / "expected_invocation_summary.json"
            )
            data = load_json(path)
            data["generated_policy_body"] = "metadata_only_marker"
            write_json(path, data)
            result = validate_artifact_writer_cli_actual_invocation_fixture_case(
                path.parent
            )

        self.assertFalse(result.matched)
        self.assertIn(
            "forbidden_actual_key:generated_policy_body",
            result.mismatch_reasons,
        )

    def test_private_or_absolute_path_key_in_temp_copy_fails(self) -> None:
        with temp_root_copy() as root:
            path = (
                root
                / "valid/valid_minimal_metadata_only_actual_invocation_plan"
                / "runtime_pointer_metadata.json"
            )
            data = load_json(path)
            data["absolute_path"] = "metadata_only_marker"
            write_json(path, data)
            result = validate_artifact_writer_cli_actual_invocation_fixture_case(
                path.parent
            )

        self.assertFalse(result.matched)
        self.assertIn("forbidden_actual_key:absolute_path", result.mismatch_reasons)

    def test_valid_case_sentinel_present_in_temp_copy_fails(self) -> None:
        with temp_root_copy() as root:
            path = (
                root
                / "valid/valid_minimal_metadata_only_actual_invocation_plan"
                / "runtime_request_metadata.json"
            )
            data = load_json(path)
            data["prohibited_field_present"] = True
            write_json(path, data)
            result = validate_artifact_writer_cli_actual_invocation_fixture_case(
                path.parent
            )

        self.assertFalse(result.matched)
        self.assertIn("valid_case_prohibited_field_present", result.mismatch_reasons)

    def test_malformed_json_returns_input_error_safely(self) -> None:
        with temp_root_copy() as root:
            path = (
                root
                / "valid/valid_minimal_metadata_only_actual_invocation_plan"
                / "case_metadata.json"
            )
            path.write_text("{", encoding="utf-8")

            summary = validate_artifact_writer_cli_actual_invocation_fixture_root(root)

        self.assertFalse(summary.all_matched)
        self.assertEqual(summary.input_error_cases, 1)
        assert_safe_output(
            self,
            json.dumps(
                summarize_artifact_writer_cli_actual_invocation_fixture_validation(
                    summary
                ),
                sort_keys=True,
            ),
        )

    def test_root_not_found_returns_input_error_safely(self) -> None:
        summary = validate_artifact_writer_cli_actual_invocation_fixture_root(
            Path("tests/fixtures/not_a_fixture_root_for_actual_invocation")
        )
        payload = summarize_artifact_writer_cli_actual_invocation_fixture_validation(
            summary
        )

        self.assertFalse(summary.all_matched)
        self.assertIn("fixture_root_missing", payload["root_errors"])
        self.assertEqual(payload["total_cases"], 0)
        assert_safe_output(self, json.dumps(payload, sort_keys=True))

    def test_cli_json_output_parseable_and_body_free(self) -> None:
        completed = run_cli("--json")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["total_cases"], EXPECTED_TOTAL_CASES)
        self.assertEqual(payload["total_json_files"], EXPECTED_TOTAL_JSON_FILES)
        self.assertEqual(payload["matched_cases"], EXPECTED_TOTAL_CASES)
        assert_safe_output(self, completed.stdout)
        assert_safe_output(self, completed.stderr)

    def test_cli_human_output_body_free(self) -> None:
        completed = run_cli()

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("total_cases=32", completed.stdout)
        self.assertIn("matched_cases=32", completed.stdout)
        assert_safe_output(self, completed.stdout)
        assert_safe_output(self, completed.stderr)

    def test_cli_single_valid_case(self) -> None:
        completed = run_cli(
            "--fixture-case",
            "valid/valid_minimal_metadata_only_actual_invocation_plan",
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("total_cases=1", completed.stdout)
        self.assertIn("pass_cases=1", completed.stdout)
        assert_safe_output(self, completed.stdout)

    def test_cli_single_invalid_case(self) -> None:
        completed = run_cli(
            "--fixture-case",
            "invalid/invalid_generated_policy_body_present",
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("total_cases=1", completed.stdout)
        self.assertIn("fail_closed_cases=1", completed.stdout)
        assert_safe_output(self, completed.stdout)

    def test_cli_help_output(self) -> None:
        completed = run_cli("--help")

        self.assertEqual(completed.returncode, 0)
        self.assertIn("--fixture-root", completed.stdout)
        self.assertIn("--fixture-case", completed.stdout)
        self.assertIn("--json", completed.stdout)
        assert_safe_output(self, completed.stdout)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", MODULE, *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


class temp_root_copy:
    def __enter__(self) -> Path:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "fixtures"
        shutil.copytree(FIXTURE_ROOT, self.root)
        return self.root

    def __exit__(self, *args: object) -> None:
        self._tmp.cleanup()


def assert_safe_output(test_case: unittest.TestCase, text: str) -> None:
    forbidden_body_keys = (
        "request_body",
        "pointer_body",
        "expected_body",
        "written_file_json_body",
        "manifest_body",
        "artifact_body_payload",
        "generated_policy_body",
        "raw_stdout_body",
        "raw_stderr_body",
        "raw_rows",
        "logits",
        "probabilities",
        "private_path",
        "absolute_path",
        "raw_learner_text",
        "real_participant_data",
    )
    assert_no_forbidden_fragments(
        test_case,
        text,
        [
            '"case_metadata":',
            '"runtime_request_metadata":',
            '"runtime_pointer_metadata":',
            '"artifact_writer_cli_invocation_metadata":',
            '"expected_invocation_summary":',
            '"expected_error":',
            "file" + "://",
            _slash_wrapped("Users"),
            _slash_wrapped("private"),
        ]
        + [f'"{key}":' for key in forbidden_body_keys],
    )


def _slash_wrapped(value: str) -> str:
    return "/" + value + "/"


if __name__ == "__main__":
    unittest.main()
