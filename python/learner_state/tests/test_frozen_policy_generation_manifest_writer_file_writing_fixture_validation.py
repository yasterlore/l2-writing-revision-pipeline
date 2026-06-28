from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from learner_state.frozen_policy_generation_manifest_writer_file_writing_fixture_validation import (
    DEFAULT_FIXTURE_ROOT,
    EXPECTED_FAIL_CLOSED_CASES,
    EXPECTED_INVALID_CASES,
    EXPECTED_PASS_METADATA_FILE_WRITTEN_CASES,
    EXPECTED_PASS_METADATA_NO_FILE_CASES,
    EXPECTED_TOTAL_CASES,
    EXPECTED_TOTAL_JSON_FILES,
    EXPECTED_USAGE_ERROR_CASES,
    EXPECTED_VALID_CASES,
    REASON_CODES,
    REQUIRED_FILES,
    main,
    summarize_manifest_writer_file_writing_fixture_validation,
    validate_manifest_writer_file_writing_fixture_case,
    validate_manifest_writer_file_writing_fixture_root,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments


FIXTURE_ROOT = DEFAULT_FIXTURE_ROOT


class FrozenPolicyGenerationManifestWriterFileWritingFixtureValidationTests(
    unittest.TestCase
):
    def test_fixture_root_has_expected_shape_and_json_count(self) -> None:
        case_dirs = sorted(path for path in FIXTURE_ROOT.glob("*/*") if path.is_dir())
        json_files = sorted(FIXTURE_ROOT.glob("*/*/*.json"))

        self.assertEqual(len(case_dirs), EXPECTED_TOTAL_CASES)
        self.assertEqual(len(json_files), EXPECTED_TOTAL_JSON_FILES)
        self.assertEqual(sum(path.parent.name == "valid" for path in case_dirs), 6)
        self.assertEqual(sum(path.parent.name == "invalid" for path in case_dirs), 33)

    def test_every_case_has_required_files_and_json_parses(self) -> None:
        required = set(REQUIRED_FILES)
        for case_dir in sorted(path for path in FIXTURE_ROOT.glob("*/*") if path.is_dir()):
            with self.subTest(case=f"{case_dir.parent.name}/{case_dir.name}"):
                names = {path.name for path in case_dir.glob("*.json")}
                self.assertEqual(names, required)
                for file_name in REQUIRED_FILES:
                    self.assertIsInstance(
                        json.loads((case_dir / file_name).read_text()), dict
                    )

    def test_root_validation_matches_all_expected_cases(self) -> None:
        summary = validate_manifest_writer_file_writing_fixture_root(FIXTURE_ROOT)

        self.assertEqual(summary.total_cases, EXPECTED_TOTAL_CASES)
        self.assertEqual(summary.valid_cases, EXPECTED_VALID_CASES)
        self.assertEqual(summary.invalid_cases, EXPECTED_INVALID_CASES)
        self.assertEqual(summary.total_json_files, EXPECTED_TOTAL_JSON_FILES)
        self.assertEqual(
            summary.pass_metadata_file_written_cases,
            EXPECTED_PASS_METADATA_FILE_WRITTEN_CASES,
        )
        self.assertEqual(
            summary.pass_metadata_no_file_cases, EXPECTED_PASS_METADATA_NO_FILE_CASES
        )
        self.assertEqual(summary.usage_error_cases, EXPECTED_USAGE_ERROR_CASES)
        self.assertEqual(summary.fail_closed_cases, EXPECTED_FAIL_CLOSED_CASES)
        self.assertEqual(summary.matched_cases, EXPECTED_TOTAL_CASES)
        self.assertEqual(summary.mismatched_cases, 0)
        self.assertEqual(summary.input_error_cases, 0)

    def test_single_valid_file_written_case_matches(self) -> None:
        result = validate_manifest_writer_file_writing_fixture_case(
            FIXTURE_ROOT / "valid" / "metadata_file_minimal_safe_relative_json",
            "valid",
        )

        self.assertTrue(result.matched)
        self.assertFalse(result.input_error)
        self.assertEqual(result.expected_category, "pass_metadata_file_written")
        self.assertEqual(result.expected_writer_status, "pass")
        self.assertEqual(result.expected_reason_codes, ())

    def test_single_valid_no_file_case_matches(self) -> None:
        result = validate_manifest_writer_file_writing_fixture_case(
            FIXTURE_ROOT / "valid" / "metadata_no_file_existing_runtime_mode",
            "valid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(result.expected_category, "pass_metadata_no_file")
        self.assertEqual(result.expected_manifest_writer_mode, "metadata_only_no_file")

    def test_single_invalid_usage_error_path_case_matches(self) -> None:
        result = validate_manifest_writer_file_writing_fixture_case(
            FIXTURE_ROOT / "invalid" / "absolute_manifest_output_path",
            "invalid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(result.expected_category, "usage_error_no_write")
        self.assertEqual(result.expected_writer_status, "usage_error")
        self.assertEqual(result.expected_reason_codes, ("absolute_manifest_output_path",))

    def test_single_invalid_fail_closed_payload_case_matches(self) -> None:
        result = validate_manifest_writer_file_writing_fixture_case(
            FIXTURE_ROOT / "invalid" / "artifact_body_payload_leakage",
            "invalid",
        )

        self.assertTrue(result.matched)
        self.assertEqual(result.expected_category, "fail_closed_no_write")
        self.assertEqual(result.expected_writer_status, "fail_closed")
        self.assertEqual(result.expected_reason_codes, ("artifact_body_payload_leakage",))

    def test_reason_code_count_matching(self) -> None:
        summary = validate_manifest_writer_file_writing_fixture_root(FIXTURE_ROOT)

        self.assertEqual(set(summary.reason_code_counts), REASON_CODES)
        for reason in REASON_CODES:
            with self.subTest(reason=reason):
                self.assertEqual(summary.reason_code_counts[reason], 1)

    def test_summary_output_is_body_free_and_safe(self) -> None:
        rendered = summarize_manifest_writer_file_writing_fixture_validation(
            validate_manifest_writer_file_writing_fixture_root(FIXTURE_ROOT)
        )

        assert_no_forbidden_fragments(
            self,
            rendered,
            [
                '"manifest_writer_request":',
                '"artifact_writer_result_pointer":',
                '"artifact_body_generation_result_pointer":',
                '"expected_manifest_writer_file_writing_result":',
                '"case_metadata":',
                '"request_body":',
                '"pointer_body":',
                '"expected_body":',
                '"artifact_body_payload":',
                '"generated_policy_body":',
                '"manifest_body":',
                '"raw_rows":',
                '"probabilities":',
                '"/Users/',
                '"/private/',
            ],
        )

    def test_json_output_parseable_and_body_free(self) -> None:
        rendered = summarize_manifest_writer_file_writing_fixture_validation(
            validate_manifest_writer_file_writing_fixture_root(FIXTURE_ROOT),
            as_json=True,
        )
        payload = json.loads(rendered)

        self.assertEqual(payload["total_cases"], EXPECTED_TOTAL_CASES)
        self.assertFalse(payload["validator_wrote_files"])
        self.assertFalse(payload["runtime_writer_executed"])
        self.assertFalse(payload["isolated_write_executed"])
        self.assertEqual(payload["release_quality_ready"], False)
        assert_no_forbidden_fragments(
            self,
            rendered,
            [
                '"manifest_writer_request":',
                '"artifact_writer_result_pointer":',
                '"artifact_body_generation_result_pointer":',
                '"expected_manifest_writer_file_writing_result":',
                '"/Users/',
                '"/private/',
            ],
        )

    def test_cli_help_exits_zero(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "learner_state.frozen_policy_generation_manifest_writer_file_writing_fixture_validation",
                "--help",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0)
        self.assertIn("--fixture-root", completed.stdout)
        self.assertIn("--fixture-case", completed.stdout)

    def test_cli_root_json_parseable(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "learner_state.frozen_policy_generation_manifest_writer_file_writing_fixture_validation",
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["total_cases"], EXPECTED_TOTAL_CASES)
        self.assertEqual(payload["matched_cases"], EXPECTED_TOTAL_CASES)

    def test_cli_single_valid_and_invalid_cases(self) -> None:
        selectors = {
            "valid/metadata_file_minimal_safe_relative_json": (
                "pass_metadata_file_written_cases"
            ),
            "valid/metadata_no_file_existing_runtime_mode": (
                "pass_metadata_no_file_cases"
            ),
            "invalid/absolute_manifest_output_path": "usage_error_cases",
            "invalid/artifact_body_payload_leakage": "fail_closed_cases",
        }

        for selector, count_key in selectors.items():
            with self.subTest(selector=selector):
                completed = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "learner_state.frozen_policy_generation_manifest_writer_file_writing_fixture_validation",
                        "--fixture-case",
                        selector,
                        "--json",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                payload = json.loads(completed.stdout)
                self.assertEqual(completed.returncode, 0)
                self.assertEqual(payload["total_cases"], 1)
                self.assertEqual(payload["matched_cases"], 1)
                self.assertEqual(payload[count_key], 1)

    def test_unsafe_selector_returns_usage_error(self) -> None:
        with redirect_stdout(StringIO()):
            exit_code = main(["--fixture-case", "../invalid/case"])
        self.assertEqual(exit_code, 2)

    def test_missing_required_file_temp_fixture_is_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = self._copy_case(
                tmp_dir, "valid/metadata_file_minimal_safe_relative_json", "valid/missing_file"
            )
            (tmp_case / "manifest_writer_request.json").unlink()
            result = validate_manifest_writer_file_writing_fixture_case(
                tmp_case, "valid"
            )

        self.assertTrue(result.input_error)
        self.assertIn("required_file_missing", result.mismatch_reasons)

    def test_malformed_json_temp_fixture_is_input_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = self._copy_case(
                tmp_dir, "valid/metadata_file_minimal_safe_relative_json", "valid/malformed"
            )
            (tmp_case / "manifest_writer_request.json").write_text("{", encoding="utf-8")
            result = validate_manifest_writer_file_writing_fixture_case(
                tmp_case, "valid"
            )

        self.assertTrue(result.input_error)
        self.assertIn("json_parse_error", result.mismatch_reasons)

    def test_schema_mismatch_temp_fixture_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = self._copy_case(
                tmp_dir,
                "valid/metadata_file_minimal_safe_relative_json",
                "valid/schema_mismatch",
            )
            self._patch_json(
                tmp_case / "case_metadata.json",
                {"schema_version": "unknown_schema_v0"},
            )
            result = validate_manifest_writer_file_writing_fixture_case(
                tmp_case, "valid"
            )

        self.assertFalse(result.matched)
        self.assertFalse(result.input_error)
        self.assertIn("case_metadata_schema_version", result.mismatch_reasons)

    def test_case_id_mismatch_temp_fixture_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = self._copy_case(
                tmp_dir,
                "valid/metadata_file_minimal_safe_relative_json",
                "valid/case_id_mismatch",
            )
            self._patch_json(
                tmp_case / "expected_manifest_writer_file_writing_result.json",
                {"case_id": "valid/different_case_id"},
            )
            result = validate_manifest_writer_file_writing_fixture_case(
                tmp_case, "valid"
            )

        self.assertFalse(result.matched)
        self.assertIn("expected_case_id_mismatch", result.mismatch_reasons)

    def test_category_mismatch_temp_fixture_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = self._copy_case(
                tmp_dir,
                "valid/metadata_file_minimal_safe_relative_json",
                "valid/category_mismatch",
            )
            self._patch_json(
                tmp_case / "expected_manifest_writer_file_writing_result.json",
                {"expected_category": "usage_error_no_write"},
            )
            result = validate_manifest_writer_file_writing_fixture_case(
                tmp_case, "valid"
            )

        self.assertFalse(result.matched)
        self.assertIn("valid_case_category_not_pass", result.mismatch_reasons)

    def test_validator_does_not_write_files_or_create_residue(self) -> None:
        before = sorted(path.relative_to(FIXTURE_ROOT) for path in FIXTURE_ROOT.rglob("*"))

        validate_manifest_writer_file_writing_fixture_root(FIXTURE_ROOT)

        after = sorted(path.relative_to(FIXTURE_ROOT) for path in FIXTURE_ROOT.rglob("*"))
        self.assertEqual(after, before)
        residue_root = Path("tmp/frozen_policy_generation_manifest")
        residue_count = (
            len([path for path in residue_root.rglob("*") if path.is_file()])
            if residue_root.exists()
            else 0
        )
        self.assertEqual(residue_count, 0)

    def _copy_case(self, tmp_dir: str, source_selector: str, target_selector: str) -> Path:
        source = FIXTURE_ROOT / source_selector
        target = Path(tmp_dir) / target_selector
        shutil.copytree(source, target)
        return target

    def _patch_json(self, path: Path, updates: dict[str, object]) -> None:
        payload = json.loads(path.read_text())
        payload.update(updates)
        path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
