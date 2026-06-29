from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_artifact_writer_cli_integration_fixture_validation import (
    EXPECTED_FAIL_CLOSED_CASES,
    EXPECTED_PASS_CASES,
    EXPECTED_TOTAL_CASES,
    EXPECTED_TOTAL_JSON_FILES,
    EXPECTED_USAGE_ERROR_CASES,
    validate_artifact_writer_cli_integration_fixture_case,
    validate_artifact_writer_cli_integration_fixture_root,
    summarize_artifact_writer_cli_integration_fixture_validation,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path(
    "tests/fixtures/"
    "learner_state_frozen_policy_generation_artifact_writer_cli_integration"
)
MODULE = (
    "learner_state."
    "frozen_policy_generation_artifact_writer_cli_integration_fixture_validation"
)


class ArtifactWriterCliIntegrationFixtureValidationTests(unittest.TestCase):
    def test_full_root_validation_success(self) -> None:
        summary = validate_artifact_writer_cli_integration_fixture_root(FIXTURE_ROOT)
        payload = summarize_artifact_writer_cli_integration_fixture_validation(summary)

        self.assertTrue(summary.all_matched)
        self.assertEqual(payload["total_cases"], EXPECTED_TOTAL_CASES)
        self.assertEqual(payload["valid_cases"], 6)
        self.assertEqual(payload["invalid_cases"], 22)
        self.assertEqual(payload["total_json_files"], EXPECTED_TOTAL_JSON_FILES)
        self.assertEqual(payload["matched_cases"], EXPECTED_TOTAL_CASES)
        self.assertEqual(payload["mismatched_cases"], 0)
        self.assertEqual(payload["input_error_cases"], 0)
        self.assertEqual(payload["pass_cases"], EXPECTED_PASS_CASES)
        self.assertEqual(payload["usage_error_cases"], EXPECTED_USAGE_ERROR_CASES)
        self.assertEqual(payload["fail_closed_cases"], EXPECTED_FAIL_CLOSED_CASES)
        self.assertFalse(payload["release_quality_ready"])
        assert_safe_output(self, json.dumps(payload, sort_keys=True))

    def test_single_valid_case_validation(self) -> None:
        case_dir = FIXTURE_ROOT / "valid/minimal_generator_to_artifact_writer_metadata_only"
        result = validate_artifact_writer_cli_integration_fixture_case(case_dir)

        self.assertTrue(result.matched)
        self.assertFalse(result.input_error)
        self.assertEqual(result.integration_status, "pass")
        self.assertEqual(result.reason_codes, ())
        self.assertTrue(result.generator_scaffold_executed)
        self.assertTrue(result.artifact_writer_executed)
        assert_safe_output(self, json.dumps(result.to_safe_dict(), sort_keys=True))

    def test_single_invalid_case_validation(self) -> None:
        case_dir = FIXTURE_ROOT / "invalid/generated_policy_body_leakage"
        result = validate_artifact_writer_cli_integration_fixture_case(case_dir)

        self.assertTrue(result.matched)
        self.assertFalse(result.input_error)
        self.assertEqual(result.integration_status, "fail_closed")
        self.assertEqual(result.reason_codes, ("generated_policy_body_leakage",))
        self.assertTrue(result.generator_scaffold_executed)
        self.assertFalse(result.artifact_writer_executed)
        assert_safe_output(self, json.dumps(result.to_safe_dict(), sort_keys=True))

    def test_required_file_missing_in_temp_copy_fails(self) -> None:
        with temp_root_copy() as root:
            target = (
                root
                / "valid/minimal_generator_to_artifact_writer_metadata_only"
                / "generator_request.json"
            )
            target.unlink()

            summary = validate_artifact_writer_cli_integration_fixture_root(root)

        self.assertFalse(summary.all_matched)
        self.assertEqual(summary.input_error_cases, 1)
        self.assertIn("total_json_file_count_mismatch", summary.root_errors)

    def test_extra_json_file_in_temp_copy_fails(self) -> None:
        with temp_root_copy() as root:
            target = (
                root
                / "valid/minimal_generator_to_artifact_writer_metadata_only"
                / "extra.json"
            )
            target.write_text("{}", encoding="utf-8")

            summary = validate_artifact_writer_cli_integration_fixture_root(root)

        self.assertFalse(summary.all_matched)
        self.assertEqual(summary.input_error_cases, 1)
        self.assertIn("total_json_file_count_mismatch", summary.root_errors)

    def test_schema_mismatch_in_temp_copy_fails(self) -> None:
        with mutated_expected_result() as path:
            data = load_json(path)
            data["schema_version"] = "wrong_schema"
            write_json(path, data)
            result = validate_artifact_writer_cli_integration_fixture_case(path.parent)

        self.assertFalse(result.matched)
        self.assertIn("expected_result_schema_version_mismatch", result.mismatch_reasons)

    def test_case_id_mismatch_in_temp_copy_fails(self) -> None:
        with mutated_expected_result() as path:
            data = load_json(path)
            data["case_id"] = "valid/wrong_case"
            write_json(path, data)
            result = validate_artifact_writer_cli_integration_fixture_case(path.parent)

        self.assertFalse(result.matched)
        self.assertIn("case_id_mismatch", result.mismatch_reasons)

    def test_reason_code_mismatch_in_temp_copy_fails(self) -> None:
        with temp_root_copy() as root:
            path = (
                root
                / "invalid/generated_policy_body_leakage"
                / "expected_artifact_writer_cli_integration_result.json"
            )
            data = load_json(path)
            data["expected_reason_codes"] = ["manifest_body_leakage"]
            write_json(path, data)
            result = validate_artifact_writer_cli_integration_fixture_case(path.parent)

        self.assertFalse(result.matched)
        self.assertIn("reason_code_case_mismatch", result.mismatch_reasons)

    def test_forbidden_body_marker_in_temp_copy_fails(self) -> None:
        with temp_root_copy() as root:
            path = (
                root
                / "valid/minimal_generator_to_artifact_writer_metadata_only"
                / "generator_result_pointer.json"
            )
            data = load_json(path)
            data["generated_policy_body"] = "body_payload_marker"
            write_json(path, data)
            result = validate_artifact_writer_cli_integration_fixture_case(path.parent)

        self.assertFalse(result.matched)
        self.assertIn("forbidden_actual_key:generated_policy_body", result.mismatch_reasons)

    def test_actual_absolute_path_sentinel_in_temp_copy_fails(self) -> None:
        with temp_root_copy() as root:
            path = (
                root
                / "valid/minimal_generator_to_artifact_writer_metadata_only"
                / "generator_input_fixture_pointer.json"
            )
            data = load_json(path)
            data["fixture_reference_id"] = "/tmp/not_public_safe"
            write_json(path, data)
            result = validate_artifact_writer_cli_integration_fixture_case(path.parent)

        self.assertFalse(result.matched)
        self.assertIn("actual_absolute_or_private_path", result.mismatch_reasons)

    def test_file_writing_true_in_temp_copy_fails(self) -> None:
        with temp_root_copy() as root:
            path = (
                root
                / "valid/minimal_generator_to_artifact_writer_metadata_only"
                / "artifact_writer_request.json"
            )
            data = load_json(path)
            data["file_writing_allowed"] = True
            write_json(path, data)
            result = validate_artifact_writer_cli_integration_fixture_case(path.parent)

        self.assertFalse(result.matched)
        self.assertIn(
            "artifact_writer_file_writing_allowed_not_false",
            result.mismatch_reasons,
        )

    def test_artifact_body_generation_true_in_temp_copy_fails(self) -> None:
        with mutated_expected_result() as path:
            data = load_json(path)
            data["artifact_body_generation_executed"] = True
            write_json(path, data)
            result = validate_artifact_writer_cli_integration_fixture_case(path.parent)

        self.assertFalse(result.matched)
        self.assertIn(
            "artifact_body_generation_executed_not_false",
            result.mismatch_reasons,
        )

    def test_manifest_writer_true_in_temp_copy_fails(self) -> None:
        with mutated_expected_result() as path:
            data = load_json(path)
            data["manifest_writer_executed"] = True
            write_json(path, data)
            result = validate_artifact_writer_cli_integration_fixture_case(path.parent)

        self.assertFalse(result.matched)
        self.assertIn("manifest_writer_executed_not_false", result.mismatch_reasons)

    def test_cli_json_output_parseable_and_body_free(self) -> None:
        completed = run_cli("--json")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["total_cases"], EXPECTED_TOTAL_CASES)
        self.assertEqual(payload["total_json_files"], EXPECTED_TOTAL_JSON_FILES)
        assert_safe_output(self, completed.stdout)
        assert_safe_output(self, completed.stderr)

    def test_cli_human_output_body_free(self) -> None:
        completed = run_cli()

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("total_cases=28", completed.stdout)
        self.assertIn("matched_cases=28", completed.stdout)
        assert_safe_output(self, completed.stdout)
        assert_safe_output(self, completed.stderr)

    def test_cli_single_valid_case(self) -> None:
        completed = run_cli(
            "--fixture-case",
            "valid/minimal_generator_to_artifact_writer_metadata_only",
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("total_cases=1", completed.stdout)
        self.assertIn("pass_cases=1", completed.stdout)
        assert_safe_output(self, completed.stdout)

    def test_cli_single_invalid_case(self) -> None:
        completed = run_cli(
            "--fixture-case",
            "invalid/generated_policy_body_leakage",
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
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class temp_root_copy:
    def __enter__(self) -> Path:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "fixtures"
        shutil.copytree(FIXTURE_ROOT, self.root)
        return self.root

    def __exit__(self, *args: object) -> None:
        self._tmp.cleanup()


class mutated_expected_result:
    def __enter__(self) -> Path:
        self._tmp = tempfile.TemporaryDirectory()
        self.case_dir = (
            Path(self._tmp.name)
            / "valid"
            / "minimal_generator_to_artifact_writer_metadata_only"
        )
        shutil.copytree(
            FIXTURE_ROOT / "valid/minimal_generator_to_artifact_writer_metadata_only",
            self.case_dir,
        )
        return self.case_dir / "expected_artifact_writer_cli_integration_result.json"

    def __exit__(self, *args: object) -> None:
        self._tmp.cleanup()


def assert_safe_output(test_case: unittest.TestCase, text: str) -> None:
    assert_no_forbidden_fragments(
        test_case,
        text,
        [
            '"case_metadata":',
            '"generator_request":',
            '"generator_input_fixture_pointer":',
            '"artifact_writer_request":',
            '"generator_result_pointer":',
            '"expected_artifact_writer_cli_integration_result":',
            '"request_body":',
            '"pointer_body":',
            '"expected_body":',
            '"written_file_json_body":',
            '"manifest_body":',
            '"manifest_json_body":',
            '"artifact_body_payload":',
            '"generated_policy_body":',
            '"raw_rows":',
            '"logits":',
            '"probabilities":',
            '"private_path":',
            '"absolute_path":',
            '"raw_learner_text":',
            '"real_participant_data":',
            "/Users/",
            "/home/",
            "/private/",
            "/tmp/",
        ],
    )


if __name__ == "__main__":
    unittest.main()
