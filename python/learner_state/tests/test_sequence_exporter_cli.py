from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from learner_state.sequence_exporter import (
    FEATURES_OUTPUT_FILE,
    LABELS_OUTPUT_FILE,
    MANIFEST_OUTPUT_FILE,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path("tests/fixtures/learner_state_sequence_exporter")
MINIMAL_CASE = FIXTURE_ROOT / "valid" / "minimal_single_participant"
PAST_WINDOW_CASE = FIXTURE_ROOT / "valid" / "past_window_boundary_reset"
INVALID_CASES = {
    "missing_safe_episodes": 2,
    "malformed_jsonl": 2,
    "empty_input": 1,
    "unknown_schema_version": 1,
    "label_in_feature_input": 1,
}


class LearnerStateSequenceExporterCliTests(unittest.TestCase):
    def test_help_exits_zero(self) -> None:
        completed = run_cli("--help")

        self.assertEqual(completed.returncode, 0)
        assert_safe_cli_output(self, completed)

    def test_minimal_fixture_export_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            completed = run_cli(
                "--input-fixture",
                str(MINIMAL_CASE),
                "--output-dir",
                tmpdir,
            )
            output_dir = Path(tmpdir)

            self.assertEqual(completed.returncode, 0)
            self.assertTrue((output_dir / FEATURES_OUTPUT_FILE).exists())
            self.assertTrue((output_dir / LABELS_OUTPUT_FILE).exists())
            self.assertTrue((output_dir / MANIFEST_OUTPUT_FILE).exists())
            self.assertIn("export_status=pass", completed.stdout)
            assert_safe_cli_output(self, completed)

    def test_past_window_boundary_fixture_export_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            completed = run_cli(
                "--input-fixture",
                str(PAST_WINDOW_CASE),
                "--output-dir",
                tmpdir,
            )

            self.assertEqual(completed.returncode, 0)
            self.assertIn("export_status=pass", completed.stdout)
            assert_safe_cli_output(self, completed)

    def test_json_output_is_parseable_and_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            completed = run_cli(
                "--input-fixture",
                str(MINIMAL_CASE),
                "--output-dir",
                tmpdir,
                "--json",
            )

            self.assertEqual(completed.returncode, 0)
            summary = json.loads(completed.stdout)
            self.assertEqual(summary["mode"], "export")
            self.assertEqual(summary["export_status"], "pass")
            self.assertEqual(summary["audit_status"], "pass")
            self.assertEqual(summary["feature_row_count"], 3)
            self.assertEqual(summary["label_row_count"], 3)
            self.assertTrue(summary["content_suppressed"])
            self.assertTrue(summary["no_raw_rows"])
            self.assertNotIn("features_path", summary)
            self.assertNotIn("labels_path", summary)
            self.assertNotIn("manifest_path", summary)
            assert_safe_cli_output(self, completed)

    def test_invalid_fixtures_exit_nonzero_with_safe_summary(self) -> None:
        for case_name, expected_exit in sorted(INVALID_CASES.items()):
            with self.subTest(case_name=case_name):
                with tempfile.TemporaryDirectory() as tmpdir:
                    completed = run_cli(
                        "--input-fixture",
                        str(FIXTURE_ROOT / "invalid" / case_name),
                        "--output-dir",
                        tmpdir,
                    )

                    self.assertEqual(completed.returncode, expected_exit)
                    self.assertIn("export_status=fail", completed.stdout)
                    assert_safe_cli_output(self, completed)

    def test_missing_required_args_exits_nonzero(self) -> None:
        completed = run_cli("--input-fixture", str(MINIMAL_CASE))

        self.assertNotEqual(completed.returncode, 0)
        assert_safe_cli_output(self, completed)

    def test_existing_output_files_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            (output_dir / FEATURES_OUTPUT_FILE).write_text("", encoding="utf-8")
            completed = run_cli(
                "--input-fixture",
                str(MINIMAL_CASE),
                "--output-dir",
                tmpdir,
            )

            self.assertEqual(completed.returncode, 1)
            self.assertIn("existing_output_files", completed.stdout)
            assert_safe_cli_output(self, completed)

    def test_unsafe_output_path_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            unsafe_output = Path(tmpdir) / "manual_outputs" / "exporter_case"
            completed = run_cli(
                "--input-fixture",
                str(MINIMAL_CASE),
                "--output-dir",
                str(unsafe_output),
            )

            self.assertEqual(completed.returncode, 1)
            self.assertIn("unsafe_output_path", completed.stdout)
            assert_safe_cli_output(self, completed)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "python"
    return subprocess.run(
        [sys.executable, "-m", "learner_state.sequence_exporter", *args],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def assert_safe_cli_output(
    test_case: unittest.TestCase,
    completed: subprocess.CompletedProcess[str],
) -> None:
    output = completed.stdout + completed.stderr
    forbidden_fragments = [
        "{synthetic_malformed_jsonl_marker",
        "final_text",
        "observed_after_text",
        "gold_label",
        "teacher_correction",
        "human_correction",
        "raw_text",
        "expected_action_family",
        "expected_action_type",
        "candidate_family_score_summary",
        "safe_episode_features",
        "features_path",
        "labels_path",
        "manifest_path",
        "/Users/",
        "/home/",
        "real_data",
        "private_data",
        "participant_data",
    ]
    assert_no_forbidden_fragments(test_case, output, forbidden_fragments)


if __name__ == "__main__":
    unittest.main()
