from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ot_scorer.diagnostic_summary import summarize_constraint_violation_sets
from ot_scorer.loader import CandidateFeatureError
from ot_scorer.summarize_diagnostics import run
from ot_scorer.violation_set_loader import load_constraint_violation_sets

FIXTURE = Path(
    "tests/fixtures/synthetic/constraint_violations/valid/deletion_constraint_violations.jsonl"
)


class DiagnosticSummaryTests(unittest.TestCase):
    def test_builds_summary_from_synthetic_fixture(self) -> None:
        summary = summarize_constraint_violation_sets(
            load_constraint_violation_sets(FIXTURE)
        )

        self.assertEqual(summary["total_constraint_sets"], 1)
        self.assertEqual(summary["total_candidates"], 10)
        self.assertEqual(summary["total_constraints"], 430)
        self.assertEqual(summary["safety_constraint_count"], 30)
        self.assertEqual(summary["diagnostic_constraint_count"], 210)
        self.assertFalse(summary["performance_metrics_included"])
        self.assertTrue(summary["content_suppressed"])

    def test_constraint_id_counts_are_observed_counts(self) -> None:
        summary = summarize_constraint_violation_sets(
            load_constraint_violation_sets(FIXTURE)
        )

        self.assertEqual(summary["constraint_id_counts"]["HOLD-CANDIDATE"], 1)
        self.assertEqual(summary["constraint_id_counts"]["LOCAL-EDIT-CANDIDATE"], 3)
        self.assertEqual(
            summary["constraint_id_counts"]["GRAMMAR-PLACEHOLDER-CANDIDATE"],
            6,
        )

    def test_local_pattern_counts_are_observed_counts(self) -> None:
        summary = summarize_constraint_violation_sets(
            load_constraint_violation_sets(FIXTURE)
        )
        counts = summary["local_pattern_constraint_counts"]

        self.assertEqual(counts["CONTEXT-BEFORE-MEDIUM"], 10)
        self.assertEqual(counts["SELECTION-NONCOLLAPSED-BEFORE"], 10)
        self.assertEqual(counts["SELECTION-SPAN-SHORT"], 10)
        self.assertEqual(counts["LEFT-CONTEXT-ENDS-WITH-PUNCTUATION"], 10)
        self.assertEqual(counts["LEFT-CHAR-CLASS-PUNCTUATION"], 10)

    def test_linguistic_placeholder_counts_are_observed_counts(self) -> None:
        summary = summarize_constraint_violation_sets(
            load_constraint_violation_sets(FIXTURE)
        )
        counts = summary["linguistic_placeholder_constraint_counts"]

        self.assertEqual(counts["ARTICLE-PLACEHOLDER-CANDIDATE"], 1)
        self.assertEqual(counts["NUMBER-PLACEHOLDER-CANDIDATE"], 1)
        self.assertEqual(counts["SVA-PLACEHOLDER-CANDIDATE"], 1)
        self.assertEqual(counts["TENSE-PLACEHOLDER-CANDIDATE"], 1)
        self.assertEqual(counts["PREPOSITION-PLACEHOLDER-CANDIDATE"], 1)
        self.assertEqual(counts["PUNCTUATION-PLACEHOLDER-CANDIDATE"], 1)

    def test_summary_excludes_raw_text_and_forbidden_fields(self) -> None:
        summary = summarize_constraint_violation_sets(
            load_constraint_violation_sets(FIXTURE)
        )
        text = json.dumps(summary, ensure_ascii=False)

        self.assertNotIn("local_context_before", text)
        self.assertNotIn("Synthetic candidate description", text)
        self.assertNotIn("proposed_edit", text)
        self.assertNotIn("observed_after_text", text)
        self.assertNotIn("final_text", text)
        self.assertNotIn("gold_label", text)
        self.assertNotIn("expected_action", text)

    def test_empty_input_returns_zero_summary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "empty.jsonl"
            output_path = Path(directory) / "summary.json"
            input_path.write_text("", encoding="utf-8")

            stdout_summary = run(input_path, output_path)
            summary = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertIn("diagnostic_summary: ok", stdout_summary)
        self.assertEqual(summary["total_constraint_sets"], 0)
        self.assertEqual(summary["total_candidates"], 0)
        self.assertEqual(summary["total_constraints"], 0)

    def test_malformed_jsonl_fails_without_printing_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "malformed.jsonl"
            input_path.write_text("{not valid json", encoding="utf-8")

            with self.assertRaises(CandidateFeatureError) as error:
                run(input_path, Path(directory) / "summary.json")

        self.assertIn("malformed JSON", str(error.exception))
        self.assertNotIn("{not valid json", str(error.exception))

    def test_run_writes_output_file_and_safe_stdout_summary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "diagnostic_summary.json"

            stdout_summary = run(FIXTURE, output_path)
            summary = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertIn("diagnostic_summary: ok", stdout_summary)
        self.assertIn("content_suppressed: true", stdout_summary)
        self.assertIn("performance_metrics_included: false", stdout_summary)
        self.assertNotIn("{", stdout_summary)
        self.assertNotIn("candidate_violations", stdout_summary)
        self.assertEqual(summary["summary_kind"], "constraint_diagnostic_counts")


if __name__ == "__main__":
    unittest.main()
