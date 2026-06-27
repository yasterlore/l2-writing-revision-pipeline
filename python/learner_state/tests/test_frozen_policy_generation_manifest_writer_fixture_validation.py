from __future__ import annotations

import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_manifest_writer_fixture_validation import (
    DEFAULT_FIXTURE_ROOT,
    EXPECTED_CATEGORY_COUNTS,
    EXPECTED_INVALID_CASES,
    EXPECTED_JSON_FILE_COUNT,
    EXPECTED_TOTAL_CASES,
    EXPECTED_VALID_CASES,
    ManifestWriterFixtureValidationError,
    main,
    summarize_manifest_writer_fixture_validation,
    validate_manifest_writer_fixture_case,
    validate_manifest_writer_fixture_root,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = DEFAULT_FIXTURE_ROOT
REQUIRED_FILES = {
    "case_metadata.json",
    "manifest_writer_request.json",
    "artifact_writer_result_pointer.json",
    "artifact_body_generation_result_pointer.json",
    "expected_manifest_writer_result.json",
}


class FrozenPolicyGenerationManifestWriterFixtureValidationTests(unittest.TestCase):
    def test_validation_error_dataclass_is_available(self) -> None:
        error = ManifestWriterFixtureValidationError(
            reason_code="synthetic_reason",
            failed_check="synthetic_check",
        )

        self.assertEqual(error.reason_code, "synthetic_reason")
        self.assertEqual(error.failed_check, "synthetic_check")

    def test_fixture_root_has_expected_shape_and_json_count(self) -> None:
        case_dirs = sorted(path for path in FIXTURE_ROOT.glob("*/*") if path.is_dir())
        json_files = sorted(FIXTURE_ROOT.glob("*/*/*.json"))

        self.assertEqual(len(case_dirs), EXPECTED_TOTAL_CASES)
        self.assertEqual(len(json_files), EXPECTED_JSON_FILE_COUNT)
        self.assertEqual(sum(path.parent.name == "valid" for path in case_dirs), 5)
        self.assertEqual(sum(path.parent.name == "invalid" for path in case_dirs), 25)

    def test_every_case_has_required_files_and_json_parses(self) -> None:
        for case_dir in sorted(path for path in FIXTURE_ROOT.glob("*/*") if path.is_dir()):
            with self.subTest(case=f"{case_dir.parent.name}/{case_dir.name}"):
                names = {path.name for path in case_dir.glob("*.json")}
                self.assertEqual(names, REQUIRED_FILES)
                for file_name in REQUIRED_FILES:
                    payload = json.loads((case_dir / file_name).read_text())
                    self.assertIsInstance(payload, dict)

    def test_root_validation_matches_all_expected_cases(self) -> None:
        summary = validate_manifest_writer_fixture_root(FIXTURE_ROOT)

        self.assertEqual(summary.total_cases, EXPECTED_TOTAL_CASES)
        self.assertEqual(summary.valid_cases, EXPECTED_VALID_CASES)
        self.assertEqual(summary.invalid_cases, EXPECTED_INVALID_CASES)
        self.assertEqual(
            summary.pass_metadata_only_no_file_cases,
            EXPECTED_CATEGORY_COUNTS["pass_metadata_only_no_file"],
        )
        self.assertEqual(
            summary.pass_manifest_file_written_cases,
            EXPECTED_CATEGORY_COUNTS["pass_manifest_file_written"],
        )
        self.assertEqual(
            summary.usage_error_cases,
            EXPECTED_CATEGORY_COUNTS["usage_error_no_write"],
        )
        self.assertEqual(
            summary.fail_closed_cases,
            EXPECTED_CATEGORY_COUNTS["fail_closed_no_write"],
        )
        self.assertEqual(summary.matched_cases, EXPECTED_TOTAL_CASES)
        self.assertEqual(summary.mismatched_cases, 0)
        self.assertEqual(summary.input_error_cases, 0)
        self.assertTrue(summary.content_suppressed)
        self.assertTrue(summary.manifest_body_suppressed)
        self.assertTrue(summary.no_raw_rows)
        self.assertTrue(summary.no_logits_dump)
        self.assertTrue(summary.no_private_paths)
        self.assertTrue(summary.no_absolute_paths)
        self.assertTrue(summary.no_artifact_body_payload)
        self.assertTrue(summary.no_generated_policy_body)
        self.assertTrue(summary.no_manifest_body_nesting)
        self.assertTrue(summary.synthetic_only_checked)
        self.assertTrue(summary.no_oracle_checked)
        self.assertTrue(summary.non_proof_notice_checked)
        self.assertTrue(summary.path_policy_checked)
        self.assertTrue(summary.content_policy_checked)
        self.assertFalse(summary.release_quality_ready)

    def test_single_valid_case_passes(self) -> None:
        result = validate_manifest_writer_fixture_case(
            FIXTURE_ROOT / "valid" / "metadata_only_manifest_no_file",
            "valid",
        )

        self.assertEqual(result.validation_status, "pass")
        self.assertEqual(result.expected_category, "pass_metadata_only_no_file")
        self.assertEqual(result.reason_codes, [])
        self.assertEqual(result.failed_checks, [])

    def test_single_invalid_case_passes_as_expected_failure_contract(self) -> None:
        result = validate_manifest_writer_fixture_case(
            FIXTURE_ROOT / "invalid" / "generated_policy_body_leakage",
            "invalid",
        )

        self.assertEqual(result.validation_status, "fail_closed")
        self.assertEqual(result.expected_category, "fail_closed_no_write")
        self.assertEqual(result.reason_codes, ["generated_policy_body_leakage"])

    def test_safe_rejection_valid_case_passes(self) -> None:
        result = validate_manifest_writer_fixture_case(
            FIXTURE_ROOT
            / "valid"
            / "manifest_existing_output_rejected_after_precreate",
            "valid",
        )

        self.assertEqual(result.validation_status, "usage_error")
        self.assertEqual(result.expected_category, "usage_error_no_write")
        self.assertEqual(result.reason_codes, ["overwrite_without_policy"])

    def test_reason_code_counts_match_expected(self) -> None:
        summary = validate_manifest_writer_fixture_root(FIXTURE_ROOT)

        self.assertEqual(summary.reason_code_counts.get("overwrite_without_policy"), 2)
        for reason in (
            "generated_policy_body_leakage",
            "artifact_body_payload_leakage",
            "request_body_leakage",
            "pointer_body_leakage",
            "expected_body_leakage",
            "raw_rows_leakage",
            "logits_dump_leakage",
            "private_path_leakage",
            "raw_learner_text_leakage",
            "manifest_body_nesting",
            "performance_claim_body",
            "missing_synthetic_notice",
            "missing_no_oracle_notice",
            "missing_non_proof_notice",
            "unknown_schema_version",
            "absolute_manifest_output_path",
            "home_manifest_output_path",
            "parent_traversal_manifest_output_path",
            "cloud_marker_manifest_output_path",
            "private_marker_manifest_output_path",
            "hidden_private_manifest_directory",
            "non_json_manifest_extension",
            "unsafe_manifest_filename",
            "too_long_manifest_path",
        ):
            with self.subTest(reason=reason):
                self.assertEqual(summary.reason_code_counts.get(reason), 1)

    def test_summary_output_is_body_free_and_safe(self) -> None:
        rendered = summarize_manifest_writer_fixture_validation(
            validate_manifest_writer_fixture_root(FIXTURE_ROOT)
        )

        assert_no_forbidden_fragments(
            self,
            rendered,
            [
                '"case_metadata":',
                '"manifest_writer_request":',
                '"expected_manifest_writer_result":',
                '"artifact_body_generation_result_pointer":',
                '"artifact_writer_result_pointer":',
                '"request_body":',
                '"pointer_body":',
                '"expected_body":',
                '"artifact_body_payload":',
                '"generated_policy_body":',
                '"manifest_body":',
                '"raw_rows":',
                '"logits":',
                '"probabilities":',
                '"raw_learner_text":',
                '"performance_metrics":',
                "/Us" "ers/",
                "/private/",
                "/var/fold" "ers",
            ],
        )

    def test_json_output_parseable_and_body_free(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = main(["--json"])

        self.assertEqual(exit_code, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["total_cases"], EXPECTED_TOTAL_CASES)
        self.assertEqual(payload["matched_cases"], EXPECTED_TOTAL_CASES)
        self.assertFalse(payload["release_quality_ready"])
        assert_no_forbidden_fragments(
            self,
            output.getvalue(),
            [
                '"manifest_writer_request":',
                '"expected_manifest_writer_result":',
                '"artifact_body_payload":',
                '"generated_policy_body":',
                '"manifest_body":',
                "/Us" "ers/",
                "/private/",
                "/var/fold" "ers",
            ],
        )

    def test_human_output_body_free(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = main([])

        self.assertEqual(exit_code, 0)
        self.assertIn("mode=manifest_writer_fixture_validation", output.getvalue())
        assert_no_forbidden_fragments(
            self,
            output.getvalue(),
            [
                '"manifest_writer_request":',
                '"expected_manifest_writer_result":',
                '"artifact_body_payload":',
                '"generated_policy_body":',
                '"manifest_body":',
                "/Us" "ers/",
                "/private/",
                "/var/fold" "ers",
            ],
        )

    def test_unsafe_selector_rejected_with_usage_error(self) -> None:
        for selector in ("", "../valid/case", "/valid/case", "valid\\case", "other/case"):
            with self.subTest(selector=selector):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    exit_code = main(["--fixture-case", selector])
                self.assertEqual(exit_code, 2)
                self.assertIn("unsafe", output.getvalue())

    def test_single_case_cli_valid_and_invalid(self) -> None:
        for selector in (
            "valid/metadata_only_manifest_no_file",
            "invalid/generated_policy_body_leakage",
        ):
            with self.subTest(selector=selector):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    exit_code = main(["--fixture-case", selector])
                self.assertEqual(exit_code, 0)
                self.assertIn("matched=true", output.getvalue())

    def test_required_file_missing_temp_fixture_is_detected(self) -> None:
        source = FIXTURE_ROOT / "valid" / "metadata_only_manifest_no_file"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "missing_file"
            shutil.copytree(source, tmp_case)
            (tmp_case / "manifest_writer_request.json").unlink()
            result = validate_manifest_writer_fixture_case(tmp_case, "valid")

        self.assertEqual(result.validation_status, "input_error")
        self.assertIn("required_file_missing", result.reason_codes)

    def test_malformed_json_temp_fixture_is_detected(self) -> None:
        source = FIXTURE_ROOT / "valid" / "metadata_only_manifest_no_file"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "malformed_json"
            shutil.copytree(source, tmp_case)
            (tmp_case / "manifest_writer_request.json").write_text("{", encoding="utf-8")
            result = validate_manifest_writer_fixture_case(tmp_case, "valid")

        self.assertEqual(result.validation_status, "input_error")
        self.assertIn("malformed_fixture", result.reason_codes)

    def test_case_id_mismatch_temp_fixture_is_detected(self) -> None:
        source = FIXTURE_ROOT / "valid" / "metadata_only_manifest_no_file"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "case_id_mismatch"
            shutil.copytree(source, tmp_case)
            path = tmp_case / "case_metadata.json"
            payload = json.loads(path.read_text())
            payload["case_id"] = "different_case_id"
            path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            result = validate_manifest_writer_fixture_case(tmp_case, "valid")

        self.assertEqual(result.validation_status, "input_error")
        self.assertIn("case_id_mismatch", result.reason_codes)

    def test_schema_mismatch_temp_fixture_is_detected(self) -> None:
        source = FIXTURE_ROOT / "valid" / "metadata_only_manifest_no_file"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "schema_mismatch"
            shutil.copytree(source, tmp_case)
            path = tmp_case / "manifest_writer_request.json"
            payload = json.loads(path.read_text())
            payload["schema_version"] = "unknown_schema_v0"
            path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            result = validate_manifest_writer_fixture_case(tmp_case, "valid")

        self.assertEqual(result.validation_status, "input_error")
        self.assertIn("schema_version_unknown", result.reason_codes)

    def test_validator_does_not_write_manifest_files_or_create_residue(self) -> None:
        manifest_tmp = Path("tmp/frozen_policy_generation_manifest")
        before_files = sorted(manifest_tmp.rglob("*")) if manifest_tmp.exists() else []

        validate_manifest_writer_fixture_root(FIXTURE_ROOT)

        after_files = sorted(manifest_tmp.rglob("*")) if manifest_tmp.exists() else []
        self.assertEqual(after_files, before_files)


if __name__ == "__main__":
    unittest.main()
