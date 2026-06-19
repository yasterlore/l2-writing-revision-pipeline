from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ot_scorer.score_fixture_lock import (
    DEFAULT_EXPECTED,
    ScoreFixtureLockError,
    run_lock_check,
)

SELECTION_EXPECTED = Path(
    "tests/fixtures/synthetic/candidate_scores/valid/selection_edit_candidate_scores.jsonl"
)
CURSOR_EXPECTED = Path(
    "tests/fixtures/synthetic/candidate_scores/valid/cursor_movement_candidate_scores.jsonl"
)


class ScoreFixtureLockTests(unittest.TestCase):
    def test_matching_fixture_passes(self) -> None:
        report = run_lock_check(DEFAULT_EXPECTED, DEFAULT_EXPECTED)

        self.assertEqual(report.lock_status, "ok")
        self.assertEqual(report.case_name, "deletion_case")
        self.assertEqual(report.mismatch_counts, {})
        self.assertGreater(report.candidates_checked, 0)

    def test_added_lock_fixtures_pass_against_themselves(self) -> None:
        cases = [
            ("selection_edit_case", SELECTION_EXPECTED),
            ("cursor_movement_case", CURSOR_EXPECTED),
        ]
        for case_name, fixture in cases:
            with self.subTest(case_name=case_name):
                report = run_lock_check(fixture, fixture, case_name=case_name)

                self.assertEqual(report.lock_status, "ok")
                self.assertEqual(report.case_name, case_name)
                self.assertGreater(report.candidates_checked, 0)

    def test_rank_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            generated = Path(directory) / "rank_mismatch.jsonl"
            rows = load_fixture_rows()
            rows[0]["candidate_scores"][0]["rank"] = 99
            write_rows(generated, rows)

            report = run_lock_check(DEFAULT_EXPECTED, generated)

            self.assertEqual(report.lock_status, "fail")
            self.assertIn("rank_mismatch", report.mismatch_counts)

    def test_weighted_score_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            generated = Path(directory) / "weighted_score_mismatch.jsonl"
            rows = load_fixture_rows()
            rows[0]["candidate_scores"][0]["weighted_score"] = 1.0
            write_rows(generated, rows)

            report = run_lock_check(DEFAULT_EXPECTED, generated)

            self.assertEqual(report.lock_status, "fail")
            self.assertIn("weighted_score_mismatch", report.mismatch_counts)

    def test_schema_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            generated = Path(directory) / "schema_mismatch.jsonl"
            rows = load_fixture_rows()
            rows[0]["candidate_scores"][0].pop("action_family")
            write_rows(generated, rows)

            with self.assertRaises(ScoreFixtureLockError) as context:
                run_lock_check(DEFAULT_EXPECTED, generated)

            self.assertIn("missing_field", str(context.exception))

    def test_missing_generated_file_fails(self) -> None:
        with self.assertRaises(ScoreFixtureLockError) as context:
            run_lock_check(DEFAULT_EXPECTED, "tmp/synthetic_e2e/missing/scores.jsonl")

        self.assertIn("missing_generated_file", str(context.exception))

    def test_unsafe_path_fails(self) -> None:
        with self.assertRaises(ScoreFixtureLockError) as context:
            run_lock_check(DEFAULT_EXPECTED, "private_data/scores.jsonl")

        self.assertIn("unsafe_path", str(context.exception))

    def test_config_field_in_default_output_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            generated = Path(directory) / "config_field.jsonl"
            rows = load_fixture_rows()
            rows[0]["config_name"] = "synthetic_config_should_not_be_in_default_output"
            write_rows(generated, rows)

            with self.assertRaises(ScoreFixtureLockError) as context:
                run_lock_check(DEFAULT_EXPECTED, generated)

            self.assertIn("default_output_config_field", str(context.exception))

    def test_forbidden_field_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            generated = Path(directory) / "forbidden_field.jsonl"
            rows = load_fixture_rows()
            rows[0]["candidate_scores"][0]["final_text"] = "synthetic forbidden value"
            write_rows(generated, rows)

            with self.assertRaises(ScoreFixtureLockError) as context:
                run_lock_check(DEFAULT_EXPECTED, generated)

            self.assertIn("forbidden_field", str(context.exception))

    def test_cli_stdout_is_safe_on_match(self) -> None:
        result = run_cli(DEFAULT_EXPECTED, DEFAULT_EXPECTED)

        self.assertEqual(result.returncode, 0)
        self.assertIn("case_name=deletion_case", result.stdout)
        self.assertIn("lock_status=ok", result.stdout)
        assert_safe_cli_output(self, result.stdout + result.stderr)

    def test_cli_stdout_is_safe_on_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            generated = Path(directory) / "rank_mismatch.jsonl"
            rows = load_fixture_rows()
            rows[0]["candidate_scores"][0]["rank"] = 99
            write_rows(generated, rows)

            result = run_cli(DEFAULT_EXPECTED, generated)

        self.assertEqual(result.returncode, 1)
        self.assertIn("lock_status=fail", result.stdout)
        self.assertIn("rank_mismatch", result.stdout)
        assert_safe_cli_output(self, result.stdout + result.stderr)


def load_fixture_rows() -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in DEFAULT_EXPECTED.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def run_cli(expected: Path, generated: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "ot_scorer.score_fixture_lock",
            "--expected",
            str(expected),
            "--generated",
            str(generated),
        ],
        check=False,
        cwd=Path.cwd(),
        text=True,
        capture_output=True,
    )


def assert_safe_cli_output(
    test_case: unittest.TestCase, combined_output: str
) -> None:
    forbidden_fragments = [
        '"candidate_scores"',
        '"constraint_contributions"',
        "final_text",
        "observed_after_text",
        "local_context_before",
        "local_context_after_observed",
        "gold_label",
        "teacher_correction",
        "synthetic forbidden value",
        "proposed_edit",
        "expected_action_type",
        "exact_match",
    ]
    for fragment in forbidden_fragments:
        test_case.assertNotIn(fragment, combined_output)


if __name__ == "__main__":
    unittest.main()
