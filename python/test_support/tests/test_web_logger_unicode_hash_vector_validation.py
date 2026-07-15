from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from web_logger_unicode_hash_vector_validation import (
    FAIL_CLOSED_STATUS,
    MISMATCH_STATUS,
    PASS_STATUS,
    SCHEMA_VERSION,
    USAGE_ERROR_STATUS,
    validate_data,
    validate_fixture,
)


FIXTURE_PATH = Path("tests/fixtures/web_logger_unicode_hash_vectors/vectors.json")


class WebLoggerUnicodeHashVectorValidationTests(unittest.TestCase):
    def test_valid_current_vectors_fixture_passes(self) -> None:
        summary = validate_fixture(FIXTURE_PATH)

        self.assertEqual(summary.status, PASS_STATUS)
        self.assertEqual(summary.reason_code, "none")
        self.assertEqual(summary.vector_count, 15)
        self.assertEqual(summary.valid_offset_case_count, 35)
        self.assertEqual(summary.expected_failure_count, 11)

    def test_unsupported_schema_version_fails(self) -> None:
        data = self._fixture_data()
        data["vector_schema_version"] = "unsupported"

        summary = validate_data(data)

        self.assertEqual(summary.status, USAGE_ERROR_STATUS)
        self.assertEqual(summary.reason_code, "unsupported_schema_version")

    def test_missing_top_level_field_fails(self) -> None:
        data = self._fixture_data()
        del data["position_unit"]

        summary = validate_data(data)

        self.assertEqual(summary.status, USAGE_ERROR_STATUS)
        self.assertEqual(summary.reason_code, "missing_required_field")

    def test_unsupported_position_unit_fails(self) -> None:
        data = self._fixture_data()
        data["position_unit"] = "utf8_byte"

        summary = validate_data(data)

        self.assertEqual(summary.status, FAIL_CLOSED_STATUS)
        self.assertEqual(summary.reason_code, "unsupported_position_unit")

    def test_hash_mismatch_fails(self) -> None:
        data = self._fixture_data()
        data["vectors"][1]["hash_sha256_utf8_lowercase_hex"] = "0" * 64

        summary = validate_data(data)

        self.assertEqual(summary.status, MISMATCH_STATUS)
        self.assertEqual(summary.reason_code, "hash_mismatch")

    def test_invalid_hash_format_fails(self) -> None:
        data = self._fixture_data()
        data["vectors"][1]["hash_sha256_utf8_lowercase_hex"] = "NOT_HEX"

        summary = validate_data(data)

        self.assertEqual(summary.status, MISMATCH_STATUS)
        self.assertEqual(summary.reason_code, "invalid_hash_format")

    def test_utf16_length_mismatch_fails(self) -> None:
        data = self._fixture_data()
        data["vectors"][4]["utf16_code_unit_length"] = 1

        summary = validate_data(data)

        self.assertEqual(summary.status, MISMATCH_STATUS)
        self.assertEqual(summary.reason_code, "utf16_length_mismatch")

    def test_utf8_byte_length_mismatch_fails(self) -> None:
        data = self._fixture_data()
        data["vectors"][2]["utf8_byte_length"] = 2

        summary = validate_data(data)

        self.assertEqual(summary.status, MISMATCH_STATUS)
        self.assertEqual(summary.reason_code, "utf8_length_mismatch")

    def test_code_point_count_mismatch_fails(self) -> None:
        data = self._fixture_data()
        data["vectors"][4]["code_point_count"] = 2

        summary = validate_data(data)

        self.assertEqual(summary.status, MISMATCH_STATUS)
        self.assertEqual(summary.reason_code, "code_point_count_mismatch")

    def test_offset_mapping_mismatch_fails(self) -> None:
        data = self._fixture_data()
        data["vectors"][2]["offset_cases"][0]["expected_utf8_end_byte"] = 1

        summary = validate_data(data)

        self.assertEqual(summary.status, MISMATCH_STATUS)
        self.assertEqual(summary.reason_code, "offset_mapping_mismatch")

    def test_surrogate_pair_internal_offset_in_valid_offset_cases_fails(self) -> None:
        data = self._fixture_data()
        data["vectors"][4]["offset_cases"][0]["utf16_end"] = 1

        summary = validate_data(data)

        self.assertEqual(summary.status, MISMATCH_STATUS)
        self.assertEqual(summary.reason_code, "invalid_utf16_boundary")

    def test_expected_failure_inside_surrogate_pair_is_accepted(self) -> None:
        summary = validate_fixture(FIXTURE_PATH)

        self.assertEqual(summary.status, PASS_STATUS)
        self.assertGreaterEqual(
            self._reason_count("offset_inside_surrogate_pair"), 1
        )

    def test_beyond_length_expected_failure_is_accepted(self) -> None:
        summary = validate_fixture(FIXTURE_PATH)

        self.assertEqual(summary.status, PASS_STATUS)
        self.assertGreaterEqual(self._reason_count("offset_out_of_range"), 1)

    def test_start_greater_than_end_expected_failure_is_accepted(self) -> None:
        summary = validate_fixture(FIXTURE_PATH)

        self.assertEqual(summary.status, PASS_STATUS)
        self.assertGreaterEqual(self._reason_count("offset_range_inverted"), 1)

    def test_forbidden_content_marker_fails(self) -> None:
        data = self._fixture_data()
        data["vectors"][0]["source_text_description"] = "real participant data marker"

        summary = validate_data(data)

        self.assertEqual(summary.status, FAIL_CLOSED_STATUS)
        self.assertEqual(summary.reason_code, "forbidden_content_marker")
        self.assertEqual(summary.real_data_marker_detected_count, 1)

    def test_cli_summary_output_suppresses_raw_source_text(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "web_logger_unicode_hash_vector_validation",
                "--fixture",
                str(FIXTURE_PATH),
                "--summary-only",
            ],
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status=pass", result.stdout)
        self.assertIn("vector_count=15", result.stdout)
        self.assertNotIn("abcde", result.stdout)
        self.assertNotIn("expected_selected_text", result.stdout)
        self.assertNotIn("source_text", result.stdout)

    def test_missing_fixture_file_is_usage_error(self) -> None:
        missing_path = Path(tempfile.gettempdir()) / "missing_unicode_vectors.json"

        summary = validate_fixture(missing_path)

        self.assertEqual(summary.status, USAGE_ERROR_STATUS)
        self.assertEqual(summary.reason_code, "fixture_missing")

    def test_malformed_json_is_usage_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "vectors.json"
            path.write_text("{not-json", encoding="utf-8")

            summary = validate_fixture(path)

        self.assertEqual(summary.status, USAGE_ERROR_STATUS)
        self.assertEqual(summary.reason_code, "malformed_json")

    def _fixture_data(self) -> dict:
        data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(data["vector_schema_version"], SCHEMA_VERSION)
        return copy.deepcopy(data)

    def _reason_count(self, reason_code: str) -> int:
        data = self._fixture_data()
        return sum(
            1
            for vector in data["vectors"]
            for failure in vector["expected_failures"]
            if failure["reason_code"] == reason_code
        )


if __name__ == "__main__":
    unittest.main()
