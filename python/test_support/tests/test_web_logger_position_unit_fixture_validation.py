from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from web_logger_position_unit_fixture_validation import (
    FAIL_STATUS,
    PASS_STATUS,
    validate_fixture_root,
)


FIXTURE_ROOT = Path("tests/fixtures/web_logger_position_unit_schema")


class WebLoggerPositionUnitFixtureValidationTests(unittest.TestCase):
    def test_valid_fixture_root_passes(self) -> None:
        summary = validate_fixture_root(FIXTURE_ROOT)

        self.assertEqual(summary.validation_status, PASS_STATUS)
        self.assertEqual(summary.reason_code, "none")
        self.assertEqual(summary.matched_cases, 17)
        self.assertEqual(summary.mismatched_cases, 0)

    def test_expected_total_counts_match(self) -> None:
        summary = validate_fixture_root(FIXTURE_ROOT)

        self.assertEqual(summary.total_cases, 17)
        self.assertEqual(summary.valid_cases, 5)
        self.assertEqual(summary.invalid_cases, 11)
        self.assertEqual(summary.legacy_cases, 1)
        self.assertEqual(summary.jsonl_record_count, 24)

    def test_duplicate_case_id_fails(self) -> None:
        with self._temp_fixture_root() as root:
            index = self._read_index(root)
            index["cases"][1]["case_id"] = index["cases"][0]["case_id"]
            self._write_index(root, index)

            summary = validate_fixture_root(root)

        self.assertEqual(summary.validation_status, FAIL_STATUS)
        self.assertEqual(summary.reason_code, "duplicate_case_id")

    def test_missing_fixture_path_fails(self) -> None:
        with self._temp_fixture_root() as root:
            index = self._read_index(root)
            index["cases"][0]["fixture_path"] = "valid/missing.jsonl"
            self._write_index(root, index)

            summary = validate_fixture_root(root)

        self.assertEqual(summary.validation_status, FAIL_STATUS)
        self.assertEqual(summary.reason_code, "missing_fixture_path")

    def test_fixture_path_escaping_root_fails(self) -> None:
        with self._temp_fixture_root() as root:
            index = self._read_index(root)
            index["cases"][0]["fixture_path"] = "../outside.jsonl"
            self._write_index(root, index)

            summary = validate_fixture_root(root)

        self.assertEqual(summary.validation_status, FAIL_STATUS)
        self.assertEqual(summary.reason_code, "fixture_path_escapes_root")

    def test_invalid_jsonl_fails(self) -> None:
        with self._temp_fixture_root() as root:
            index = self._read_index(root)
            target = root / index["cases"][0]["fixture_path"]
            target.write_text("{", encoding="utf-8")

            summary = validate_fixture_root(root)

        self.assertEqual(summary.validation_status, FAIL_STATUS)
        self.assertEqual(summary.reason_code, "jsonl_malformed_json")

    def test_missing_required_metadata_fails(self) -> None:
        with self._temp_fixture_root() as root:
            index = self._read_index(root)
            del index["fixture_schema_version"]
            self._write_index(root, index)

            summary = validate_fixture_root(root)

        self.assertEqual(summary.validation_status, FAIL_STATUS)
        self.assertEqual(summary.reason_code, "missing_required_field")

    def test_missing_position_unit_case_is_recognized(self) -> None:
        summary = validate_fixture_root(FIXTURE_ROOT)

        self.assertEqual(summary.observed_reason_code_counts["missing_position_unit"], 1)

    def test_unsupported_position_unit_cases_are_recognized(self) -> None:
        summary = validate_fixture_root(FIXTURE_ROOT)

        self.assertEqual(summary.observed_reason_code_counts["unsupported_position_unit"], 2)

    def test_doc_len_before_mismatch_case_is_recognized(self) -> None:
        summary = validate_fixture_root(FIXTURE_ROOT)

        self.assertEqual(
            summary.observed_reason_code_counts["doc_len_before_utf16_mismatch"], 1
        )

    def test_doc_len_after_mismatch_case_is_recognized(self) -> None:
        summary = validate_fixture_root(FIXTURE_ROOT)

        self.assertEqual(
            summary.observed_reason_code_counts["doc_len_after_utf16_mismatch"], 1
        )

    def test_start_greater_than_end_case_is_recognized(self) -> None:
        summary = validate_fixture_root(FIXTURE_ROOT)

        self.assertEqual(summary.observed_reason_code_counts["start_greater_than_end"], 1)

    def test_offset_beyond_utf16_length_case_is_recognized(self) -> None:
        summary = validate_fixture_root(FIXTURE_ROOT)

        self.assertEqual(
            summary.observed_reason_code_counts["offset_beyond_utf16_length"], 2
        )

    def test_surrogate_internal_offset_case_is_recognized(self) -> None:
        summary = validate_fixture_root(FIXTURE_ROOT)

        self.assertEqual(
            summary.observed_reason_code_counts["offset_inside_surrogate_pair"], 1
        )

    def test_legacy_missing_position_unit_is_explicitly_gated(self) -> None:
        summary = validate_fixture_root(FIXTURE_ROOT)

        self.assertEqual(
            summary.observed_reason_code_counts[
                "legacy_position_unit_missing_allowed"
            ],
            1,
        )
        self.assertEqual(summary.legacy_allowed_cases, 1)

    def test_forbidden_no_oracle_fields_fail(self) -> None:
        with self._temp_fixture_root() as root:
            index = self._read_index(root)
            target = root / index["cases"][0]["fixture_path"]
            records = self._read_jsonl(target)
            records[0]["final_text"] = "synthetic"
            self._write_jsonl(target, records)

            summary = validate_fixture_root(root)

        self.assertEqual(summary.validation_status, FAIL_STATUS)
        self.assertEqual(summary.reason_code, "forbidden_no_oracle_field")

    def test_private_absolute_path_markers_fail(self) -> None:
        with self._temp_fixture_root() as root:
            index = self._read_index(root)
            target = root / index["cases"][0]["fixture_path"]
            records = self._read_jsonl(target)
            records[0]["prompt_id"] = "/" + "Users" + "/synthetic/path"
            self._write_jsonl(target, records)

            summary = validate_fixture_root(root)

        self.assertEqual(summary.validation_status, FAIL_STATUS)
        self.assertEqual(summary.reason_code, "forbidden_content_marker")
        self.assertEqual(summary.absolute_path_detected_count, 1)

    def test_cli_output_suppresses_raw_fixture_body(self) -> None:
        result = self._run_cli()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("validation_status=pass", result.stdout)
        self.assertNotIn("inserted_text", result.stdout)
        self.assertNotIn("deleted_text", result.stdout)
        self.assertNotIn("あいう", result.stdout)
        self.assertNotIn("😀", result.stdout)

    def test_summary_only_output_contains_public_safe_fields(self) -> None:
        result = self._run_cli()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("mode=web_logger_position_unit_fixture_validation", result.stdout)
        self.assertIn("total_cases=17", result.stdout)
        self.assertIn("private_path_detected_count=0", result.stdout)
        self.assertIn("performance_claims_present=False", result.stdout)
        self.assertNotIn("session_id", result.stdout)
        self.assertNotIn("participant_local_id", result.stdout)

    def _run_cli(self) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = "python"
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "web_logger_position_unit_fixture_validation",
                "--fixture-root",
                str(FIXTURE_ROOT),
                "--summary-only",
            ],
            check=False,
            text=True,
            capture_output=True,
            env=env,
        )

    def _temp_fixture_root(self):
        return _TemporaryFixtureRoot()

    def _read_index(self, root: Path) -> dict:
        return json.loads((root / "case_index.json").read_text(encoding="utf-8"))

    def _write_index(self, root: Path, index: dict) -> None:
        (root / "case_index.json").write_text(
            json.dumps(index, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _read_jsonl(self, path: Path) -> list[dict]:
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def _write_jsonl(self, path: Path, records: list[dict]) -> None:
        path.write_text(
            "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
            encoding="utf-8",
        )


class _TemporaryFixtureRoot:
    def __enter__(self) -> Path:
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name) / "fixture"
        shutil.copytree(FIXTURE_ROOT, root)
        return root

    def __exit__(self, exc_type, exc, tb) -> None:
        self._tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
