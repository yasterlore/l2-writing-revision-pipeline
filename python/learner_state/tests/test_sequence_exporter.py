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
    compare_export_result_to_contract,
    export_sequence_from_fixture,
    load_expected_output_contract,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path("tests/fixtures/learner_state_sequence_exporter")
MINIMAL_CASE = FIXTURE_ROOT / "valid" / "minimal_single_participant"


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


if __name__ == "__main__":
    unittest.main()
