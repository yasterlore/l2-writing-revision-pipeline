from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_artifact_body_fixture_validation import (
    EXPECTED_INVALID_REASONS,
    EXPECTED_TOTAL_CASES,
    EXPECTED_VALID_CASES,
    SAFE_MARKER_KEYS,
    compare_expected_result,
    discover_fixture_cases,
    load_expected_artifact_body_result,
    scan_forbidden_payload,
    scan_safe_markers,
    summarize_fixture_root,
    validate_artifact_body_fixture_case,
    validate_artifact_body_fixture_root,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path(
    "tests/fixtures/learner_state_frozen_policy_generation_artifact_body"
)


class FrozenPolicyGenerationArtifactBodyFixtureValidationTests(unittest.TestCase):
    def test_discovery_finds_expected_cases_in_deterministic_order(self) -> None:
        cases = discover_fixture_cases(FIXTURE_ROOT)
        labels = [case.case_label for case in cases]

        self.assertEqual(labels, sorted(labels))
        self.assertEqual(len(cases), EXPECTED_TOTAL_CASES)
        self.assertEqual(sum(label.startswith("valid/") for label in labels), 4)
        self.assertEqual(sum(label.startswith("invalid/") for label in labels), 14)

    def test_required_files_present_and_json_parse(self) -> None:
        json_files = sorted(FIXTURE_ROOT.rglob("*.json"))
        case_dirs = sorted(path for path in FIXTURE_ROOT.glob("*/*") if path.is_dir())

        self.assertEqual(len(json_files), 54)
        self.assertEqual(len(case_dirs), 18)
        for case_dir in case_dirs:
            with self.subTest(case=f"{case_dir.parent.name}/{case_dir.name}"):
                self.assertTrue((case_dir / "artifact_body_request.json").is_file())
                self.assertTrue(
                    (case_dir / "artifact_writer_result_pointer.json").is_file()
                )
                self.assertTrue(
                    (case_dir / "expected_artifact_body_result.json").is_file()
                )
        for path in json_files:
            with self.subTest(file_name=path.name):
                self.assertIsInstance(json.loads(path.read_text()), dict)

    def test_root_validation_counts_expected_matches(self) -> None:
        result = validate_artifact_body_fixture_root(FIXTURE_ROOT)

        self.assertEqual(result.total_cases, 18)
        self.assertEqual(result.valid_cases, EXPECTED_VALID_CASES)
        self.assertEqual(result.invalid_cases, 14)
        self.assertEqual(result.matched_cases, 18)
        self.assertEqual(result.mismatched_cases, 0)
        self.assertEqual(result.input_error_cases, 0)
        self.assertTrue(result.content_suppressed)
        self.assertTrue(result.no_raw_rows)
        self.assertTrue(result.no_logits_dump)
        self.assertTrue(result.no_private_paths)

    def test_valid_cases_pass_and_match_expected(self) -> None:
        for case in discover_fixture_cases(FIXTURE_ROOT):
            if case.case_category != "valid":
                continue
            with self.subTest(case=case.case_label):
                result = validate_artifact_body_fixture_case(case)
                expected = load_expected_artifact_body_result(
                    case.case_dir / "expected_artifact_body_result.json"
                )
                comparison = compare_expected_result(result.to_safe_dict(), expected)

                self.assertEqual(result.validation_status, "pass")
                self.assertIn(
                    result.body_status,
                    {"suppressed_metadata_only", "generated_safe_metadata_body"},
                )
                self.assertEqual(result.reason_codes, [])
                self.assertEqual(result.failed_checks, [])
                self.assertEqual(comparison.mismatches, [])

    def test_invalid_cases_fail_closed_with_expected_reason(self) -> None:
        for case_label, reason_code in sorted(EXPECTED_INVALID_REASONS.items()):
            case_dir = FIXTURE_ROOT / case_label
            with self.subTest(case=case_label):
                result = validate_artifact_body_fixture_case(case_dir)
                expected = load_expected_artifact_body_result(
                    case_dir / "expected_artifact_body_result.json"
                )
                comparison = compare_expected_result(result.to_safe_dict(), expected)

                self.assertEqual(result.validation_status, "fail")
                self.assertEqual(result.body_status, "fail_closed")
                self.assertEqual(result.reason_codes, [reason_code])
                self.assertEqual(len(result.failed_checks), 1)
                self.assertEqual(comparison.mismatches, [])

    def test_safe_marker_fields_are_boolean_and_not_forbidden(self) -> None:
        for case in discover_fixture_cases(FIXTURE_ROOT):
            marker_flags = case.expected_artifact_body_result["safe_marker_flags"]
            with self.subTest(case=case.case_label):
                self.assertLessEqual(set(marker_flags), set(SAFE_MARKER_KEYS))
                self.assertTrue(
                    all(isinstance(value, bool) for value in marker_flags.values())
                )
                marker_scan = scan_safe_markers(case.expected_artifact_body_result)
                forbidden_scan = scan_forbidden_payload(
                    case.expected_artifact_body_result
                )
                self.assertEqual(marker_scan.reason_codes, [])
                self.assertEqual(forbidden_scan.reason_codes, [])

    def test_forbidden_payload_scan_catches_keys_without_payload_text(self) -> None:
        payload = {
            "case_id": "synthetic_temp_forbidden_payload",
            "artifact_body_payload": "synthetic unsafe body marker",
            "nested": {"logits": [0.1, 0.9]},
        }

        scan = scan_forbidden_payload(payload)
        rendered = json.dumps(scan.to_safe_dict(), sort_keys=True)

        self.assertEqual(scan.reason_codes, ["forbidden_payload_key"])
        self.assertEqual(scan.forbidden_key_count, 2)
        self.assertNotIn("synthetic unsafe body marker", rendered)
        self.assertNotIn("0.1", rendered)

    def test_extra_json_file_triggers_unexpected_fixture_file(self) -> None:
        source = FIXTURE_ROOT / "valid" / "minimal_suppressed_metadata_only_body"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "extra_json"
            shutil.copytree(source, tmp_case)
            (tmp_case / "unexpected_fixture_file.json").write_text(
                json.dumps({"schema_version": "synthetic_extra_v0"}),
                encoding="utf-8",
            )
            result = validate_artifact_body_fixture_case(tmp_case)

        self.assertEqual(result.validation_status, "fail")
        self.assertIn("unexpected_fixture_file", result.reason_codes)

    def test_malformed_json_temp_case_becomes_input_error(self) -> None:
        source = FIXTURE_ROOT / "valid" / "minimal_suppressed_metadata_only_body"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "malformed_json"
            shutil.copytree(source, tmp_case)
            (tmp_case / "artifact_body_request.json").write_text(
                "{", encoding="utf-8"
            )
            result = validate_artifact_body_fixture_case(tmp_case)

        self.assertEqual(result.validation_status, "input_error")
        self.assertIn("malformed_fixture_file", result.reason_codes)

    def test_missing_required_file_temp_case_becomes_input_error(self) -> None:
        source = FIXTURE_ROOT / "valid" / "minimal_suppressed_metadata_only_body"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "missing_required"
            shutil.copytree(source, tmp_case)
            (tmp_case / "artifact_body_request.json").unlink()
            result = validate_artifact_body_fixture_case(tmp_case)

        self.assertEqual(result.validation_status, "input_error")
        self.assertIn("missing_required_file", result.reason_codes)

    def test_summary_is_safe_metadata_only_and_json_serializable(self) -> None:
        result = validate_artifact_body_fixture_root(FIXTURE_ROOT)
        summary = summarize_fixture_root(result)
        rendered = json.dumps(summary, sort_keys=True)

        json.loads(rendered)
        assert_no_forbidden_fragments(
            self,
            rendered,
            [
                '"request_body":',
                '"pointer_body":',
                '"expected_result_body":',
                '"artifact_body_payload":',
                '"generated_policy_body":',
                '"manifest_body":',
                '"raw_rows":',
                '"logits":',
                '"probabilities":',
                '"private_path":',
                '"raw_learner_text":',
                '"performance_metrics":',
            ],
        )

    def test_case_results_do_not_include_payload_fields(self) -> None:
        for case in discover_fixture_cases(FIXTURE_ROOT):
            with self.subTest(case=case.case_label):
                rendered = json.dumps(
                    validate_artifact_body_fixture_case(case).to_safe_dict(),
                    sort_keys=True,
                )
                assert_no_forbidden_fragments(
                    self,
                    rendered,
                    [
                        '"request_body":',
                        '"pointer_body":',
                        '"expected_result_body":',
                        '"artifact_body_payload":',
                        '"generated_policy_body":',
                        '"manifest_body":',
                        '"raw_rows":',
                        '"logits":',
                        '"probabilities":',
                        '"private_path":',
                        '"raw_learner_text":',
                        '"performance_metrics":',
                    ],
                )


if __name__ == "__main__":
    unittest.main()
