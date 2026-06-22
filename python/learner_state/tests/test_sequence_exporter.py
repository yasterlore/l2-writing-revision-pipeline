from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from learner_state.sequence_audit import audit_sequence_dataset
from learner_state.sequence_exporter import (
    FEATURES_OUTPUT_FILE,
    LABELS_OUTPUT_FILE,
    MANIFEST_OUTPUT_FILE,
    ExporterFailure,
    compare_export_result_to_contract,
    export_sequence_from_fixture,
    load_expected_failure_contract,
    load_expected_output_contract,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path("tests/fixtures/learner_state_sequence_exporter")
MINIMAL_CASE = FIXTURE_ROOT / "valid" / "minimal_single_participant"
PAST_WINDOW_CASE = FIXTURE_ROOT / "valid" / "past_window_boundary_reset"
INVALID_CASES = {
    "missing_safe_episodes": "missing_input_file",
    "malformed_jsonl": "malformed_input",
    "empty_input": "empty_input",
    "unknown_schema_version": "unknown_input_schema_version",
    "label_in_feature_input": "exporter_forbidden_field",
}


class LearnerStateSequenceExporterTests(unittest.TestCase):
    def test_exports_minimal_fixture_and_matches_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = export_sequence_from_fixture(MINIMAL_CASE, tmpdir)
            contract = load_expected_output_contract(MINIMAL_CASE)

            compare_export_result_to_contract(result, contract)

            self.assertEqual(result.export_status, "pass")
            self.assertEqual(result.audit_status, "pass")
            self.assertEqual(result.feature_row_count, 3)
            self.assertEqual(result.label_row_count, 3)
            self.assertTrue(result.content_suppressed)
            self.assertTrue(result.no_raw_rows)
            self.assertTrue(result.synthetic_only)
            assert_safe_export_result(self, result.to_safe_dict())

    def test_generated_files_exist_and_parse(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            export_sequence_from_fixture(MINIMAL_CASE, tmpdir)
            output_dir = Path(tmpdir)

            features = load_jsonl(output_dir / FEATURES_OUTPUT_FILE)
            labels = load_jsonl(output_dir / LABELS_OUTPUT_FILE)
            manifest = load_json(output_dir / MANIFEST_OUTPUT_FILE)

            self.assertEqual(len(features), 3)
            self.assertEqual(len(labels), 3)
            self.assertEqual(manifest["feature_row_count"], 3)
            self.assertEqual(manifest["label_row_count"], 3)
            self.assertTrue(manifest["content_suppressed"])
            self.assertTrue(manifest["synthetic_only"])

    def test_generated_output_audit_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            export_sequence_from_fixture(MINIMAL_CASE, tmpdir)
            output_dir = Path(tmpdir)

            audit_result = audit_sequence_dataset(
                output_dir / FEATURES_OUTPUT_FILE,
                output_dir / LABELS_OUTPUT_FILE,
                output_dir / MANIFEST_OUTPUT_FILE,
            )

            self.assertEqual(audit_result.audit_status, "pass")
            self.assertEqual(audit_result.violation_count, 0)
            assert_safe_export_result(self, audit_result.to_dict())

    def test_feature_rows_exclude_labels_and_forbidden_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            export_sequence_from_fixture(MINIMAL_CASE, tmpdir)
            features = load_jsonl(Path(tmpdir) / FEATURES_OUTPUT_FILE)

            forbidden = {
                "expected_action",
                "expected_action_family",
                "expected_action_type",
                "label_source",
                "final_text",
                "observed_after_text",
                "gold_label",
                "teacher_correction",
                "human_correction",
                "raw_text",
                "future_episode",
            }
            for row in features:
                keys = nested_keys(row)
                self.assertTrue(row["feature_schema_version"])
                self.assertFalse(keys & forbidden)
                self.assertIn("past_only_window_features", row)

    def test_label_rows_keep_expected_actions_separate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            export_sequence_from_fixture(MINIMAL_CASE, tmpdir)
            labels = load_jsonl(Path(tmpdir) / LABELS_OUTPUT_FILE)

            for row in labels:
                self.assertTrue(row["label_schema_version"])
                self.assertIn("expected_action_family", row)
                self.assertIn("expected_action_type", row)
                self.assertTrue(row["evaluation_only"])
                self.assertNotIn("candidate_family_score_summary", row)
                self.assertNotIn("safe_episode_features", row)

    def test_manifest_is_count_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            export_sequence_from_fixture(MINIMAL_CASE, tmpdir)
            manifest = load_json(Path(tmpdir) / MANIFEST_OUTPUT_FILE)

            self.assertTrue(manifest["content_suppressed"])
            self.assertTrue(manifest["no_raw_rows"])
            forbidden_manifest_keys = {
                "feature_rows",
                "label_rows",
                "candidate_score_rows",
                "row_dump",
                "raw_rows",
                "raw_text",
            }
            self.assertFalse(nested_keys(manifest) & forbidden_manifest_keys)
            assert_safe_export_result(self, manifest)

    def test_exports_past_window_boundary_reset_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = export_sequence_from_fixture(PAST_WINDOW_CASE, tmpdir)
            contract = load_expected_output_contract(PAST_WINDOW_CASE)
            output_dir = Path(tmpdir)

            compare_export_result_to_contract(result, contract)
            features = load_jsonl(output_dir / FEATURES_OUTPUT_FILE)
            labels = load_jsonl(output_dir / LABELS_OUTPUT_FILE)
            manifest = load_json(output_dir / MANIFEST_OUTPUT_FILE)
            audit_result = audit_sequence_dataset(
                output_dir / FEATURES_OUTPUT_FILE,
                output_dir / LABELS_OUTPUT_FILE,
                output_dir / MANIFEST_OUTPUT_FILE,
            )

            self.assertEqual(result.export_status, "pass")
            self.assertEqual(audit_result.audit_status, "pass")
            self.assertEqual(len(features), 4)
            self.assertEqual(len(labels), 4)
            self.assertEqual(manifest["synthetic_task_count"], 2)
            self.assertTrue(manifest["content_suppressed"])

            first_by_task = {}
            for row in features:
                task_id = row["synthetic_task_id"]
                first_by_task.setdefault(task_id, row)
                keys = nested_keys(row)
                self.assertFalse(keys & forbidden_feature_keys())
                self.assertIn("past_only_window_features", row)

            self.assertEqual(set(first_by_task), {"syn-t010a", "syn-t010b"})
            for first_row in first_by_task.values():
                window = first_row["past_only_window_features"]
                self.assertEqual(window["previous_episode_count"], 0)
                self.assertEqual(window["previous_same_top_family_count"], 0)

            task_b_rows = [
                row for row in features if row["synthetic_task_id"] == "syn-t010b"
            ]
            self.assertEqual(
                [row["past_only_window_features"]["previous_episode_count"]
                 for row in task_b_rows],
                [0, 1],
            )
            assert_safe_export_result(self, result.to_safe_dict())

    def test_invalid_edge_fixtures_fail_closed_with_expected_reason(self) -> None:
        self.assertEqual(
            sorted(INVALID_CASES),
            sorted(
                path.name
                for path in (FIXTURE_ROOT / "invalid").iterdir()
                if (path / "expected_failure_contract.json").exists()
            ),
        )

        for case_name, expected_reason in sorted(INVALID_CASES.items()):
            with self.subTest(case_name=case_name):
                case_dir = FIXTURE_ROOT / "invalid" / case_name
                contract = load_expected_failure_contract(case_dir)
                self.assertEqual(contract["expected_failure_reason"], expected_reason)

                with tempfile.TemporaryDirectory() as tmpdir:
                    output_dir = Path(tmpdir)
                    with self.assertRaises(ExporterFailure) as caught:
                        export_sequence_from_fixture(case_dir, output_dir)

                    failure = caught.exception.summary
                    compare_failure_to_contract(self, failure.to_safe_dict(), contract)
                    self.assertFalse((output_dir / FEATURES_OUTPUT_FILE).exists())
                    self.assertFalse((output_dir / LABELS_OUTPUT_FILE).exists())
                    self.assertFalse((output_dir / MANIFEST_OUTPUT_FILE).exists())
                    assert_safe_failure_summary(self, caught.exception)

    def test_valid_edge_fixture_is_discovered(self) -> None:
        valid_cases = sorted(
            path.name for path in (FIXTURE_ROOT / "valid").iterdir() if path.is_dir()
        )
        self.assertIn("minimal_single_participant", valid_cases)
        self.assertIn("past_window_boundary_reset", valid_cases)


def load_jsonl(path: Path) -> list[dict[str, object]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise AssertionError("jsonl_row_not_object")
                rows.append(row)
    return rows


def load_json(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise AssertionError("json_not_object")
    return data


def nested_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(key, str):
                keys.add(key)
            keys.update(nested_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(nested_keys(child))
    return keys


def assert_safe_export_result(
    test_case: unittest.TestCase,
    value: dict[str, object],
) -> None:
    output = json.dumps(value, sort_keys=True)
    forbidden_fragments = [
        "final_text",
        "observed_after_text",
        "gold_label",
        "teacher_correction",
        "human_correction",
        "raw_text",
        "/Users/",
        "/home/",
        "real_data",
        "private_data",
    ]
    assert_no_forbidden_fragments(test_case, output, forbidden_fragments)


def compare_failure_to_contract(
    test_case: unittest.TestCase,
    actual: dict[str, object],
    expected: dict[str, object],
) -> None:
    checks = {
        "expected_status": actual.get("export_status"),
        "expected_failure_reason": first_string(actual.get("reason_codes")),
        "expected_failure_category": first_string(actual.get("failure_categories")),
        "expected_stage": actual.get("stage"),
        "content_suppressed": actual.get("content_suppressed"),
        "no_raw_rows": actual.get("no_raw_rows"),
        "synthetic_only": actual.get("synthetic_only_checked"),
    }
    mismatches = [
        key
        for key, actual_value in checks.items()
        if expected.get(key) != actual_value
    ]
    test_case.assertEqual(
        [],
        mismatches,
        msg=f"safe_failure_contract_mismatch:{sorted(mismatches)}",
    )


def first_string(value: object) -> str | None:
    if isinstance(value, list) and value and isinstance(value[0], str):
        return value[0]
    return None


def forbidden_feature_keys() -> set[str]:
    return {
        "expected_action",
        "expected_action_family",
        "expected_action_type",
        "label_source",
        "final_text",
        "observed_after_text",
        "gold_label",
        "teacher_correction",
        "human_correction",
        "raw_text",
        "future_episode",
    }


def assert_safe_failure_summary(
    test_case: unittest.TestCase,
    failure: ExporterFailure,
) -> None:
    output = json.dumps(failure.summary.to_safe_dict(), sort_keys=True)
    output += str(failure)
    forbidden_fragments = [
        "{synthetic_malformed_jsonl_marker",
        "final_text",
        "observed_after_text",
        "gold_label",
        "teacher_correction",
        "human_correction",
        "raw_text",
        "/Users/",
        "/home/",
        "real_data",
        "private_data",
    ]
    assert_no_forbidden_fragments(test_case, output, forbidden_fragments)


if __name__ == "__main__":
    unittest.main()
