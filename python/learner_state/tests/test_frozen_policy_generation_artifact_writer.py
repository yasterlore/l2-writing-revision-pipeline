import json
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_artifact_writer import (
    FrozenPolicyGenerationArtifactPointer,
    FrozenPolicyGenerationArtifactWriterError,
    FrozenPolicyGenerationArtifactWriterRequest,
    audit_artifact_writer_safety,
    load_artifact_writer_request,
    load_generator_result_pointer,
    run_artifact_writer,
    summarize_artifact_writer_result,
    to_expected_result_dict,
)


FIXTURE_ROOT = Path(
    "tests/fixtures/learner_state_frozen_policy_generation_artifact_writer"
)
REQUIRED_CASE_FILES = (
    "artifact_writer_request.json",
    "generator_result_pointer.json",
    "expected_artifact_writer_result.json",
)
EXPECTED_INVALID_REASONS = {
    "invalid/artifact_file_writing_not_allowed": "artifact_file_writing_not_allowed",
    "invalid/generated_artifact_body_leakage": "generated_artifact_body_leakage",
    "invalid/generated_policy_body_leakage": "generated_policy_body_leakage",
    "invalid/logits_dump_carryover": "logits_dump_carryover",
    "invalid/manifest_body_leakage": "manifest_body_leakage",
    "invalid/manifest_file_writing_not_allowed": "manifest_file_writing_not_allowed",
    "invalid/missing_required_field": "missing_required_field",
    "invalid/no_oracle_violation": "no_oracle_violation",
    "invalid/non_synthetic_input": "non_synthetic_input",
    "invalid/performance_claim_in_artifact": "performance_claim_in_artifact",
    "invalid/private_path_output": "private_path_output",
    "invalid/raw_rows_carryover": "raw_rows_carryover",
    "invalid/scoring_feedback_violation": "scoring_feedback_violation",
    "invalid/unknown_schema_version": "unknown_schema_version",
}
EXPECTED_ZERO_COUNT_FIELDS = (
    "body_field_count",
    "raw_row_count",
    "logits_dump_count",
    "private_path_count",
    "performance_metric_count",
    "generated_artifact_count",
    "written_file_count",
    "manifest_body_count",
)
FORBIDDEN_RESULT_KEYS = {
    "generated_policy_body",
    "generated_artifact_body",
    "artifact_body",
    "manifest_body",
    "policy_body",
    "raw_rows",
    "logits",
    "probabilities",
    "raw_learner_text",
    "observed_after_text",
    "final_text",
    "gold_label",
    "expected_action",
    "scoring_feedback_payload",
    "request_body",
    "pointer_body",
    "expected_result_body",
    "private_path",
    "absolute_path",
    "real_participant_data",
    "calibration_body",
    "label_body",
    "split_body",
    "performance_metrics",
}
UNSAFE_STRING_MARKERS = (
    "/Users/",
    "/home/",
    "/private/",
    "/var/folders/",
    "C:\\",
    "real_data/",
    "participant_data/",
    "private_data/",
)


class FrozenPolicyGenerationArtifactWriterTests(unittest.TestCase):
    def test_valid_cases_pass(self):
        for case_dir in self._case_dirs("valid"):
            with self.subTest(case=case_dir.name):
                result = self._run_case(case_dir)
                self.assertEqual(result.writer_status, "pass")
                self.assertEqual(result.reason_codes, [])
                self.assertEqual(result.failed_checks, [])

    def test_invalid_cases_fail_with_expected_reason_code(self):
        for case_dir in self._case_dirs("invalid"):
            case_label = f"invalid/{case_dir.name}"
            with self.subTest(case=case_label):
                result = self._run_case(case_dir)
                self.assertEqual(result.writer_status, "fail")
                self.assertEqual(
                    result.reason_codes,
                    [EXPECTED_INVALID_REASONS[case_label]],
                )
                self.assertEqual(
                    result.failed_checks,
                    [EXPECTED_INVALID_REASONS[case_label]],
                )

    def test_all_cases_match_expected_fixture_metadata(self):
        for case_dir in self._case_dirs("valid") + self._case_dirs("invalid"):
            with self.subTest(case=case_dir.relative_to(FIXTURE_ROOT)):
                result = self._run_case(case_dir)
                expected = json.loads(
                    (case_dir / "expected_artifact_writer_result.json").read_text()
                )
                self.assertEqual(to_expected_result_dict(result), expected)

    def test_artifact_flags_are_safe_for_all_cases(self):
        for case_dir in self._all_case_dirs():
            with self.subTest(case=case_dir.relative_to(FIXTURE_ROOT)):
                flags = self._run_case(case_dir).artifact_flags
                self.assertIs(flags["generated_artifact_written"], False)
                self.assertIs(flags["generated_artifact_body_available"], False)
                self.assertIs(flags["artifact_body_suppressed"], True)
                self.assertIs(flags["artifact_file_path_available"], False)
                self.assertIs(flags["artifact_manifest_available"], True)
                self.assertIs(flags["artifact_manifest_body_available"], False)
                self.assertIs(flags["artifact_validation_summary_available"], True)
                self.assertIs(flags["file_writing_allowed"], False)
                self.assertIs(flags["manifest_body_suppressed"], True)

    def test_safety_flags_are_true_for_all_cases(self):
        for case_dir in self._all_case_dirs():
            with self.subTest(case=case_dir.relative_to(FIXTURE_ROOT)):
                flags = self._run_case(case_dir).safety_flags
                self.assertTrue(flags)
                self.assertTrue(all(flags.values()))

    def test_count_summary_has_zero_body_raw_logits_private_and_written_counts(self):
        for case_dir in self._all_case_dirs():
            with self.subTest(case=case_dir.relative_to(FIXTURE_ROOT)):
                counts = self._run_case(case_dir).count_summary
                self.assertGreaterEqual(counts["validation_reference_count"], 1)
                for field_name in EXPECTED_ZERO_COUNT_FIELDS:
                    self.assertEqual(counts[field_name], 0)

    def test_result_has_no_body_or_private_payload_keys(self):
        for case_dir in self._all_case_dirs():
            with self.subTest(case=case_dir.relative_to(FIXTURE_ROOT)):
                result_dict = summarize_artifact_writer_result(self._run_case(case_dir))
                self.assertFalse(
                    FORBIDDEN_RESULT_KEYS.intersection(_collect_keys(result_dict))
                )
                self.assertFalse(_contains_unsafe_string(result_dict))

    def test_manifest_and_artifact_bodies_are_not_output(self):
        result_dict = summarize_artifact_writer_result(
            self._run_case(FIXTURE_ROOT / "valid/minimal_metadata_only_artifact_plan")
        )
        self.assertNotIn("artifact_body", _collect_keys(result_dict))
        self.assertNotIn("generated_policy_body", _collect_keys(result_dict))
        self.assertNotIn("manifest_body", _collect_keys(result_dict))
        self.assertFalse(
            result_dict["manifest_summary"]["manifest_body_available"]
        )

    def test_writer_does_not_write_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            before = set(Path(temp_dir).iterdir())
            self._run_case(FIXTURE_ROOT / "valid/minimal_metadata_only_artifact_plan")
            after = set(Path(temp_dir).iterdir())
            self.assertEqual(before, after)

    def test_summary_is_json_serializable(self):
        result = self._run_case(FIXTURE_ROOT / "valid/minimal_metadata_only_artifact_plan")
        json.dumps(summarize_artifact_writer_result(result), sort_keys=True)
        json.dumps(to_expected_result_dict(result), sort_keys=True)

    def test_output_is_deterministic(self):
        case_dir = FIXTURE_ROOT / "valid/synthetic_generator_result_reference"
        first = to_expected_result_dict(self._run_case(case_dir))
        second = to_expected_result_dict(self._run_case(case_dir))
        self.assertEqual(first, second)

    def test_malformed_request_is_safe_error_without_panic(self):
        pointer = load_generator_result_pointer(
            FIXTURE_ROOT
            / "valid/minimal_metadata_only_artifact_plan/generator_result_pointer.json"
        )
        self.assertIsInstance(pointer, FrozenPolicyGenerationArtifactPointer)
        with tempfile.TemporaryDirectory() as temp_dir:
            malformed = Path(temp_dir) / "artifact_writer_request.json"
            malformed.write_text("{not-json", encoding="utf-8")
            request = load_artifact_writer_request(malformed)
        self.assertIsInstance(request, FrozenPolicyGenerationArtifactWriterError)
        result = run_artifact_writer(request, pointer)
        self.assertEqual(result.writer_status, "input_error")
        self.assertEqual(result.safe_summary, "input_error_metadata_only_artifact_writer_result")
        self.assertFalse(FORBIDDEN_RESULT_KEYS.intersection(_collect_keys(result.to_safe_dict())))

    def test_missing_request_file_is_safe_error_without_panic(self):
        pointer = load_generator_result_pointer(
            FIXTURE_ROOT
            / "valid/minimal_metadata_only_artifact_plan/generator_result_pointer.json"
        )
        self.assertIsInstance(pointer, FrozenPolicyGenerationArtifactPointer)
        request = load_artifact_writer_request(
            FIXTURE_ROOT / "valid/minimal_metadata_only_artifact_plan/missing.json"
        )
        self.assertIsInstance(request, FrozenPolicyGenerationArtifactWriterError)
        result = run_artifact_writer(request, pointer)
        self.assertEqual(result.writer_status, "input_error")
        self.assertIn("missing_request_file", result.reason_codes)

    def test_audit_reports_no_safety_reasons_for_fixture_outputs(self):
        for case_dir in self._all_case_dirs():
            with self.subTest(case=case_dir.relative_to(FIXTURE_ROOT)):
                result = self._run_case(case_dir)
                audit = audit_artifact_writer_safety(result)
                self.assertEqual(audit.reason_codes, [])
                self.assertEqual(audit.failed_checks, [])

    def _run_case(self, case_dir: Path):
        for filename in REQUIRED_CASE_FILES:
            self.assertTrue((case_dir / filename).exists(), filename)
        request = load_artifact_writer_request(case_dir / "artifact_writer_request.json")
        pointer = load_generator_result_pointer(case_dir / "generator_result_pointer.json")
        self.assertIsInstance(request, FrozenPolicyGenerationArtifactWriterRequest)
        self.assertIsInstance(pointer, FrozenPolicyGenerationArtifactPointer)
        return run_artifact_writer(request, pointer)

    def _all_case_dirs(self):
        return self._case_dirs("valid") + self._case_dirs("invalid")

    def _case_dirs(self, category: str):
        return sorted(path for path in (FIXTURE_ROOT / category).iterdir() if path.is_dir())


def _collect_keys(value):
    keys = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            keys.add(str(key))
            keys.update(_collect_keys(nested))
    elif isinstance(value, list):
        for nested in value:
            keys.update(_collect_keys(nested))
    return keys


def _contains_unsafe_string(value):
    if isinstance(value, dict):
        return any(_contains_unsafe_string(nested) for nested in value.values())
    if isinstance(value, list):
        return any(_contains_unsafe_string(nested) for nested in value)
    if isinstance(value, str):
        return any(marker in value for marker in UNSAFE_STRING_MARKERS)
    return False


if __name__ == "__main__":
    unittest.main()
