from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
import tempfile
import unittest
from pathlib import Path

from ot_scorer.config_ranking_diff import (
    ConfigRankingDiffError,
    main as diff_main,
    run_diff,
)
from ot_scorer.score import run as score_run

CONSTRAINTS = Path(
    "tests/fixtures/synthetic/constraint_violations/valid/deletion_constraint_violations.jsonl"
)
DEFAULT_LIKE_CONFIG = Path(
    "tests/fixtures/synthetic/hand_weight_configs/valid/current_default_like_config.json"
)
INTENTIONAL_CONFIG = Path(
    "tests/fixtures/synthetic/hand_weight_configs/valid/"
    "intentional_leakage_tiny_weight_config.json"
)


class ConfigRankingDiffTests(unittest.TestCase):
    def test_default_like_config_produces_zero_diff(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            no_config, config = score_default_and_config(Path(directory))

            report = run_diff(
                no_config,
                config,
                case_name="synthetic_default_like_unit",
            )

            self.assertEqual(report.diff_counts, {})
            self.assertEqual(report.first_mismatch_category, "none")
            self.assertEqual(report.total_candidates, 10)

    def test_intentional_config_produces_weighted_score_diff(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            constraints = root / "constraint_violations_with_leakage.jsonl"
            no_config = root / "no_config.jsonl"
            config = root / "config.jsonl"
            write_constraints_with_leakage_violation(constraints)
            score_run(constraints, no_config)
            score_run(constraints, config, INTENTIONAL_CONFIG)

            report = run_diff(
                no_config,
                config,
                case_name="synthetic_intentional_unit",
            )

            self.assertGreater(report.diff_counts.get("weighted_score_changed", 0), 0)
            self.assertNotIn("top_candidate_changed", report.diff_counts)
            self.assertNotIn("blocked_status_changed", report.diff_counts)

    def test_malformed_score_jsonl_fails_safely(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            malformed = root / "malformed.jsonl"
            valid = root / "valid.jsonl"
            malformed.write_text('{"candidate_scores": [', encoding="utf-8")
            score_run(CONSTRAINTS, valid)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = diff_main(
                    [
                        "--no-config",
                        str(malformed),
                        "--config",
                        str(valid),
                        "--case-name",
                        "malformed_unit",
                    ]
                )

            self.assertEqual(exit_code, 2)
            output = stdout.getvalue()
            self.assertIn("diff_status=fail", output)
            self.assertIn("reason=malformed_no_config_jsonl", output)
            assert_safe_diff_output(self, output)

    def test_missing_file_fails_safely(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            missing = root / "missing.jsonl"
            valid = root / "valid.jsonl"
            score_run(CONSTRAINTS, valid)

            with self.assertRaises(ConfigRankingDiffError) as context:
                run_diff(missing, valid)

            self.assertIn("missing_no_config_file", str(context.exception))

    def test_unsafe_path_fails_before_reading(self) -> None:
        with self.assertRaises(ConfigRankingDiffError) as context:
            run_diff("private_data/no_config_scores.jsonl", "tmp/config_scores.jsonl")

        self.assertEqual(str(context.exception), "unsafe_path")

    def test_cli_stdout_is_safe_summary_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            no_config, config = score_default_and_config(Path(directory))

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = diff_main(
                    [
                        "--no-config",
                        str(no_config),
                        "--config",
                        str(config),
                        "--case-name",
                        "safe_stdout_unit",
                        "--expect-zero-diff",
                    ]
                )

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("diff_status=ok", output)
            self.assertIn("diff_counts=none", output)
            assert_safe_diff_output(self, output)


def score_default_and_config(directory: Path) -> tuple[Path, Path]:
    no_config = directory / "no_config.jsonl"
    config = directory / "default_like_config.jsonl"
    score_run(CONSTRAINTS, no_config)
    score_run(CONSTRAINTS, config, DEFAULT_LIKE_CONFIG)
    return no_config, config


def write_constraints_with_leakage_violation(path: Path) -> None:
    rows = [
        json.loads(line)
        for line in CONSTRAINTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    changed = False
    for row in rows:
        for candidate in row["candidate_violations"]:
            for violation in candidate["violations"]:
                if not changed and violation["constraint_id"] == "NO-LEAKAGE-FLAG":
                    violation["violation_count"] = 1
                    violation["observed"] = True
                    changed = True
    if not changed:
        raise AssertionError("missing NO-LEAKAGE-FLAG fixture violation")
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def assert_safe_diff_output(
    test_case: unittest.TestCase,
    output: str,
) -> None:
    forbidden_fragments = [
        '"candidate_scores"',
        '"constraint_contributions"',
        "final_text",
        "observed_after_text",
        "gold_label",
        "expected_action",
        "raw_text",
        "raw_local_context_before",
        "local_context_before",
        "local_context_after_observed",
        "candidate_description",
        "proposed_edit",
    ]
    for fragment in forbidden_fragments:
        test_case.assertNotIn(fragment, output)


if __name__ == "__main__":
    unittest.main()
