from __future__ import annotations

import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_scaffold_fixture_validation import (
    EXPECTED_INVALID_REASONS,
    FrozenPolicyGenerationScaffoldFixtureValidationResult,
    compare_scaffold_result_to_expected,
    discover_frozen_policy_generation_scaffold_fixture_cases,
    load_expected_scaffold_result,
    load_scaffold_fixture_case,
    summarize_scaffold_fixture_validation_result,
    validate_scaffold_fixture_case,
    validate_scaffold_fixture_root,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path("tests/fixtures/learner_state_frozen_policy_generation_scaffold")
VALID_CASES = {
    "minimal_fixed_abstention_rate_dry_run",
    "minimal_fixed_threshold_dry_run",
    "validation_nll_temperature_metadata_only_dry_run",
}


class FrozenPolicyGenerationScaffoldFixtureValidationTests(unittest.TestCase):
    def test_root_discovery_is_deterministic(self) -> None:
        cases = discover_frozen_policy_generation_scaffold_fixture_cases(FIXTURE_ROOT)

        self.assertEqual(cases, sorted(cases))
        self.assertEqual(len(cases), 11)
        self.assertEqual(
            VALID_CASES,
            {path.name for path in cases if path.parent.name == "valid"},
        )
        self.assertEqual(
            sorted(EXPECTED_INVALID_REASONS),
            sorted(path.name for path in cases if path.parent.name == "invalid"),
        )

    def test_all_json_files_parse(self) -> None:
        json_files = sorted(FIXTURE_ROOT.rglob("*.json"))

        self.assertEqual(len(json_files), 33)
        for path in json_files:
            with self.subTest(path=path.as_posix()):
                with path.open() as file:
                    self.assertIsInstance(json.load(file), dict)

    def test_all_required_files_exist(self) -> None:
        for case_dir in discover_frozen_policy_generation_scaffold_fixture_cases(
            FIXTURE_ROOT
        ):
            with self.subTest(case_name=f"{case_dir.parent.name}/{case_dir.name}"):
                self.assertTrue((case_dir / "generation_request.json").is_file())
                self.assertTrue((case_dir / "input_fixture_pointer.json").is_file())
                self.assertTrue((case_dir / "expected_scaffold_result.json").is_file())
                fixture = load_scaffold_fixture_case(case_dir)
                self.assertEqual(fixture.case_name, case_dir.name)

    def test_valid_cases_pass_and_match_expected(self) -> None:
        for case_dir in sorted((FIXTURE_ROOT / "valid").iterdir()):
            if not case_dir.is_dir():
                continue
            with self.subTest(case_name=case_dir.name):
                result = validate_scaffold_fixture_case(case_dir)
                expected = load_expected_scaffold_result(case_dir)

                self.assertEqual(result.scaffold_status, "pass")
                self.assertEqual(result.reason_codes, [])
                self.assertEqual(
                    [],
                    compare_scaffold_result_to_expected(result, expected),
                )
                assert_safe_scaffold_result(self, result)

    def test_invalid_cases_fail_with_expected_reason_and_match_expected(self) -> None:
        for case_dir in sorted((FIXTURE_ROOT / "invalid").iterdir()):
            if not case_dir.is_dir():
                continue
            with self.subTest(case_name=case_dir.name):
                result = validate_scaffold_fixture_case(case_dir)
                expected = load_expected_scaffold_result(case_dir)

                self.assertEqual(result.scaffold_status, "fail")
                self.assertEqual(
                    result.reason_codes,
                    [EXPECTED_INVALID_REASONS[case_dir.name]],
                )
                self.assertEqual(
                    [],
                    compare_scaffold_result_to_expected(result, expected),
                )
                assert_safe_scaffold_result(self, result)

    def test_root_validation_summary_counts_expected_matches(self) -> None:
        summary = validate_scaffold_fixture_root(FIXTURE_ROOT)
        payload = summary.to_safe_dict()

        self.assertEqual(payload["mode"], "fixture_root")
        self.assertEqual(payload["total_cases"], 11)
        self.assertEqual(payload["matched_cases"], 11)
        self.assertEqual(payload["mismatched_cases"], 0)
        self.assertEqual(payload["input_error_cases"], 0)
        self.assertEqual(
            set(payload["reason_code_counts"]),
            set(EXPECTED_INVALID_REASONS.values()),
        )
        assert_safe_scaffold_text(self, json.dumps(payload, sort_keys=True))

    def test_reason_code_mapping_is_complete_for_invalid_cases(self) -> None:
        invalid_case_names = {
            path.name for path in (FIXTURE_ROOT / "invalid").iterdir() if path.is_dir()
        }

        self.assertEqual(invalid_case_names, set(EXPECTED_INVALID_REASONS))

    def test_forbidden_payload_fragments_are_not_present(self) -> None:
        rendered = "\n".join(
            path.read_text()
            for path in sorted(FIXTURE_ROOT.rglob("*.json"))
        )

        assert_no_forbidden_fragments(
            self,
            rendered,
            [
                '"generated_artifact_body"',
                '"generated_frozen_policy_body"',
                '"frozen_policy_artifact_body"',
                '"policy_body"',
                '"raw_rows"',
                '"raw_prediction_rows"',
                '"raw_label_rows"',
                '"logits"',
                '"probabilities"',
                '"raw_learner_text"',
                '"final_text"',
                '"observed_after_text"',
                '"gold_label"',
                '"label_body"',
                '"split_body"',
                '"calibration_policy_body"',
                '"accuracy"',
                '"f1"',
                '"ece"',
                '"aurcc"',
            ],
        )

    def test_private_path_payload_is_not_present(self) -> None:
        rendered = "\n".join(
            path.read_text()
            for path in sorted(FIXTURE_ROOT.rglob("*.json"))
        )

        assert_no_forbidden_fragments(
            self,
            rendered,
            [
                "/Users/",
                "/home/",
                "/var/folders/",
                "C:\\",
                "real_data/",
                "participant_data/",
                "private_data/",
                "manual_outputs/",
            ],
        )

    def test_safe_summary_is_serializable_and_body_free(self) -> None:
        result = validate_scaffold_fixture_case(
            FIXTURE_ROOT / "invalid" / "generated_artifact_body_leakage"
        )
        payload = summarize_scaffold_fixture_validation_result(result)
        rendered = json.dumps(payload, sort_keys=True)

        json.loads(rendered)
        assert_safe_scaffold_text(self, rendered)

    def test_malformed_temp_fixture_returns_input_error_without_panic(self) -> None:
        source = FIXTURE_ROOT / "valid" / "minimal_fixed_threshold_dry_run"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_case = Path(tmp_dir) / "valid" / "malformed"
            shutil.copytree(source, tmp_case)
            (tmp_case / "generation_request.json").write_text("{", encoding="utf-8")

            result = validate_scaffold_fixture_case(tmp_case)

        self.assertEqual(result.scaffold_status, "input_error")
        self.assertIn("malformed_fixture_file", result.reason_codes)
        assert_safe_scaffold_result(self, result)

    def test_summary_helper_does_not_print(self) -> None:
        result = validate_scaffold_fixture_case(
            FIXTURE_ROOT / "valid" / "minimal_fixed_threshold_dry_run"
        )
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            payload = summarize_scaffold_fixture_validation_result(result)

        self.assertEqual(stdout.getvalue(), "")
        assert_safe_scaffold_text(self, json.dumps(payload, sort_keys=True))


def assert_safe_scaffold_result(
    test_case: unittest.TestCase,
    result: FrozenPolicyGenerationScaffoldFixtureValidationResult,
) -> None:
    assert_safe_scaffold_text(test_case, json.dumps(result.to_safe_dict()))


def assert_safe_scaffold_text(test_case: unittest.TestCase, text: str) -> None:
    assert_no_forbidden_fragments(
        test_case,
        text,
        [
            '"generation_request":',
            '"input_fixture_pointer":',
            '"expected_scaffold_result":',
            '"generated_artifact_body"',
            '"generated_frozen_policy_body"',
            '"frozen_policy_artifact_body"',
            '"policy_body"',
            '"raw_rows":',
            '"raw_prediction_rows"',
            '"raw_label_rows"',
            '"logits":',
            '"probabilities":',
            '"raw_learner_text"',
            '"final_text"',
            '"observed_after_text"',
            '"gold_label"',
            '"label_body"',
            '"split_body"',
            '"calibration_policy_body"',
            "/Users/",
            "/home/",
            "/var/folders/",
            "C:\\",
            "real_data/",
            "participant_data/",
            "private_data/",
            "manual_outputs/",
        ],
    )


if __name__ == "__main__":
    unittest.main()
