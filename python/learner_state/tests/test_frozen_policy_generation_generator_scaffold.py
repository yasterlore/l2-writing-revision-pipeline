from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_generator_scaffold import (
    FrozenPolicyGenerationGeneratorInputPointer,
    FrozenPolicyGenerationGeneratorRequest,
    FrozenPolicyGenerationGeneratorResult,
    load_frozen_policy_generation_generator_input_pointer,
    load_frozen_policy_generation_generator_request,
    run_frozen_policy_generation_generator_scaffold,
    summarize_frozen_policy_generation_generator_result,
)
from learner_state.frozen_policy_generation_generator_scaffold_fixture_validation import (
    EXPECTED_INVALID_REASONS,
    RESULT_SCHEMA_VERSION,
    VALID_CASE_LABELS,
    load_expected_generator_scaffold_result,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path(
    "tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold"
)


class FrozenPolicyGenerationGeneratorScaffoldTests(unittest.TestCase):
    def test_load_valid_request_and_pointer(self) -> None:
        case_dir = FIXTURE_ROOT / "valid" / "minimal_metadata_only_generation_plan"

        request = load_frozen_policy_generation_generator_request(
            case_dir / "generation_request.json"
        )
        pointer = load_frozen_policy_generation_generator_input_pointer(
            case_dir / "input_fixture_pointer.json"
        )

        self.assertIsInstance(request, FrozenPolicyGenerationGeneratorRequest)
        self.assertIsInstance(pointer, FrozenPolicyGenerationGeneratorInputPointer)
        if isinstance(request, FrozenPolicyGenerationGeneratorRequest):
            self.assertEqual(
                request.request_id,
                "synthetic_generator_scaffold_minimal_metadata_only",
            )
        if isinstance(pointer, FrozenPolicyGenerationGeneratorInputPointer):
            self.assertEqual(
                pointer.pointer_id,
                "valid/minimal_metadata_only_generation_plan",
            )

    def test_minimal_valid_returns_pass(self) -> None:
        result = self._run_case("valid/minimal_metadata_only_generation_plan")

        self.assertEqual(result.generation_status, "pass")
        self.assertEqual(result.reason_codes, [])
        self.assertEqual(result.failed_checks, [])
        self.assertEqual(result.safe_summary, "metadata_only_generator_scaffold_result")

    def test_fixed_threshold_valid_returns_pass(self) -> None:
        result = self._run_case("valid/validated_fixed_threshold_metadata_plan")

        self.assertEqual(result.generation_status, "pass")
        self.assertEqual(result.reason_codes, [])
        self.assertEqual(result.policy_id, "synthetic_policy_fixed_threshold_metadata_v0_1")

    def test_fixed_abstention_rate_valid_returns_pass(self) -> None:
        result = self._run_case("valid/validated_fixed_abstention_rate_metadata_plan")

        self.assertEqual(result.generation_status, "pass")
        self.assertEqual(result.reason_codes, [])
        self.assertEqual(
            result.artifact_id,
            "synthetic_artifact_fixed_abstention_rate_metadata_v0_1",
        )

    def test_all_invalid_fixtures_return_expected_fail_reason(self) -> None:
        for case_label, expected_reason in sorted(EXPECTED_INVALID_REASONS.items()):
            with self.subTest(case=case_label):
                result = self._run_case(case_label)

                self.assertEqual(result.generation_status, "fail")
                self.assertEqual(result.reason_codes, [expected_reason])
                self.assertNotEqual(result.failed_checks, [])
                self.assertEqual(
                    result.safe_summary,
                    "fail_closed_metadata_only_generator_scaffold_result",
                )

    def test_malformed_request_returns_safe_input_error(self) -> None:
        source = FIXTURE_ROOT / "valid" / "minimal_metadata_only_generation_plan"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "case"
            shutil.copytree(source, tmp_case)
            (tmp_case / "generation_request.json").write_text("{", encoding="utf-8")

            result = self._run_case_dir(tmp_case)

        self.assertEqual(result.generation_status, "input_error")
        self.assertEqual(result.reason_codes, ["malformed_request"])
        assert_safe_generator_scaffold_result(self, result)

    def test_missing_pointer_returns_safe_input_error(self) -> None:
        source = FIXTURE_ROOT / "valid" / "minimal_metadata_only_generation_plan"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "case"
            shutil.copytree(source, tmp_case)
            (tmp_case / "input_fixture_pointer.json").unlink()

            result = self._run_case_dir(tmp_case)

        self.assertEqual(result.generation_status, "input_error")
        self.assertEqual(result.reason_codes, ["missing_pointer_file"])
        assert_safe_generator_scaffold_result(self, result)

    def test_forbidden_raw_rows_payload_returns_fail_closed(self) -> None:
        result = self._run_temp_request_with_extra_payload(
            "raw_rows",
            [],
        )

        self.assertEqual(result.generation_status, "fail")
        self.assertEqual(result.reason_codes, ["raw_rows_carryover"])
        assert_safe_generator_scaffold_result(self, result)

    def test_generated_artifact_body_request_returns_fail_closed(self) -> None:
        result = self._run_case("invalid/generated_artifact_body_leakage")

        self.assertEqual(result.generation_status, "fail")
        self.assertEqual(result.reason_codes, ["generated_artifact_body_leakage"])
        self.assertFalse(result.artifact_flags["generated_artifact_body_available"])

    def test_artifact_file_writing_request_returns_fail_closed(self) -> None:
        result = self._run_case("invalid/artifact_file_writing_attempt")

        self.assertEqual(result.generation_status, "fail")
        self.assertEqual(result.reason_codes, ["artifact_file_writing_not_allowed"])
        self.assertFalse(result.artifact_flags["generated_artifact_written"])

    def test_no_body_in_summary(self) -> None:
        result = self._run_case("valid/minimal_metadata_only_generation_plan")
        rendered = json.dumps(
            summarize_frozen_policy_generation_generator_result(result),
            sort_keys=True,
        )

        assert_safe_generator_scaffold_text(self, rendered)

    def test_json_serializable_result(self) -> None:
        result = self._run_case("valid/validated_fixed_threshold_metadata_plan")
        rendered = json.dumps(result.to_safe_dict(), sort_keys=True)

        self.assertIsInstance(json.loads(rendered), dict)

    def test_deterministic_result(self) -> None:
        first = self._run_case("valid/validated_fixed_threshold_metadata_plan")
        second = self._run_case("valid/validated_fixed_threshold_metadata_plan")

        self.assertEqual(first.to_safe_dict(), second.to_safe_dict())

    def test_no_tmp_output_or_artifact_file_written(self) -> None:
        source = FIXTURE_ROOT / "valid" / "minimal_metadata_only_generation_plan"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "case"
            shutil.copytree(source, tmp_case)
            before = sorted(path.relative_to(tmp_case) for path in tmp_case.rglob("*"))

            result = self._run_case_dir(tmp_case)

            after = sorted(path.relative_to(tmp_case) for path in tmp_case.rglob("*"))

        self.assertEqual(result.generation_status, "pass")
        self.assertEqual(before, after)
        self.assertEqual(result.count_summary["written_file_count"], 0)
        self.assertEqual(result.count_summary["generated_artifact_count"], 0)

    def test_no_private_path_output(self) -> None:
        result = self._run_case("valid/minimal_metadata_only_generation_plan")
        rendered = json.dumps(result.to_safe_dict(), sort_keys=True)

        assert_no_forbidden_fragments(
            self,
            rendered,
            ["/Users/", "/home/", "/private/", "/var/folders/", "C:\\"],
        )

    def test_result_compatible_with_expected_generator_scaffold_result(self) -> None:
        for case_label in sorted(set(VALID_CASE_LABELS) | set(EXPECTED_INVALID_REASONS)):
            case_dir = FIXTURE_ROOT / case_label
            with self.subTest(case=case_label):
                result = self._run_case_dir(case_dir)
                expected = load_expected_generator_scaffold_result(case_dir)

                self.assertEqual(result.to_expected_result_dict(), expected)
                self.assertEqual(result.schema_version, RESULT_SCHEMA_VERSION)

    def _run_case(self, case_label: str) -> FrozenPolicyGenerationGeneratorResult:
        return self._run_case_dir(FIXTURE_ROOT / case_label)

    def _run_case_dir(self, case_dir: Path) -> FrozenPolicyGenerationGeneratorResult:
        result = run_frozen_policy_generation_generator_scaffold(
            case_dir / "generation_request.json",
            case_dir / "input_fixture_pointer.json",
        )
        assert_safe_generator_scaffold_result(self, result)
        return result

    def _run_temp_request_with_extra_payload(
        self,
        key: str,
        value: object,
    ) -> FrozenPolicyGenerationGeneratorResult:
        source = FIXTURE_ROOT / "valid" / "minimal_metadata_only_generation_plan"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "case"
            shutil.copytree(source, tmp_case)
            request_path = tmp_case / "generation_request.json"
            payload = json.loads(request_path.read_text(encoding="utf-8"))
            payload[key] = value
            request_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

            return self._run_case_dir(tmp_case)


def assert_safe_generator_scaffold_result(
    test_case: unittest.TestCase,
    result: FrozenPolicyGenerationGeneratorResult,
) -> None:
    assert_safe_generator_scaffold_text(
        test_case,
        json.dumps(result.to_safe_dict(), sort_keys=True),
    )


def assert_safe_generator_scaffold_text(
    test_case: unittest.TestCase,
    text: str,
) -> None:
    assert_no_forbidden_fragments(
        test_case,
        text,
        [
            '"generation_request":',
            '"input_fixture_pointer":',
            '"expected_generator_scaffold_result":',
            '"request_body":',
            '"pointer_body":',
            '"expected_result_body":',
            '"artifact_body":',
            '"generated_policy_body":',
            '"policy_json_body":',
            '"calibration_body":',
            '"label_body":',
            '"split_body":',
            '"raw_rows":',
            '"logits":',
            '"probabilities":',
            '"raw_learner_text":',
            '"observed_after_text":',
            '"final_text":',
            '"gold_label":',
            '"private_path":',
            '"performance_claim":',
        ],
    )
