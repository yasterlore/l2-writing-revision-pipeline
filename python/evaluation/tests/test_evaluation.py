from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from evaluation.evaluate import run
from evaluation.evaluator import evaluate_score_sets
from evaluation.loader import EvaluationInputError, load_expected_actions, load_score_sets
from evaluation.models import ExpectedAction

SCORES_FIXTURE = Path(
    "tests/fixtures/synthetic/candidate_scores/valid/deletion_candidate_scores.jsonl"
)
EXPECTED_FIXTURE = Path(
    "tests/fixtures/synthetic/expected_actions/valid/deletion_expected_actions.jsonl"
)
FORBIDDEN_SCORE_FIXTURE = Path(
    "tests/fixtures/synthetic/candidate_scores/invalid/forbidden_field_candidate_scores.jsonl"
)
FORBIDDEN_EXPECTED_FIXTURE = Path(
    "tests/fixtures/synthetic/expected_actions/invalid/forbidden_field_expected_actions.jsonl"
)


class EvaluationTests(unittest.TestCase):
    def test_loads_candidate_score_set_jsonl(self) -> None:
        score_sets = load_score_sets(SCORES_FIXTURE)

        self.assertEqual(len(score_sets), 1)
        self.assertEqual(
            score_sets[0]["candidate_score_set_id"],
            "synthetic_session_001:micro:3:candidate_set:features:constraints:scores",
        )

    def test_loads_synthetic_expected_action_jsonl(self) -> None:
        expected = load_expected_actions(EXPECTED_FIXTURE)

        self.assertIn("synthetic_session_001:micro:3", expected)
        self.assertTrue(expected["synthetic_session_001:micro:3"].synthetic_only)

    def test_exact_match_is_computed(self) -> None:
        report = evaluate_score_sets(score_sets(), expected_actions("hold"))

        self.assertEqual(report.exact_match_count, 1)
        self.assertEqual(report.exact_match_rate, 1.0)

    def test_expected_action_found_and_rank_detected(self) -> None:
        report = evaluate_score_sets(score_sets(), expected_actions("local_delete_placeholder"))
        episode = report.per_episode[0]

        self.assertTrue(episode.expected_found_in_candidates)
        self.assertEqual(episode.expected_rank, 2)
        self.assertFalse(episode.exact_match)

    def test_missing_expected_action_is_reported(self) -> None:
        report = evaluate_score_sets(score_sets(), {})
        episode = report.per_episode[0]

        self.assertEqual(report.episodes_missing_expected, 1)
        self.assertIsNone(episode.expected_action_type)
        self.assertFalse(episode.exact_match)

    def test_blocked_expected_candidate_is_detected(self) -> None:
        data = score_sets()
        data[0]["candidate_scores"][1]["blocked"] = True
        data[0]["candidate_scores"][1]["block_reasons"] = ["NO-LEAKAGE-FLAG"]
        report = evaluate_score_sets(data, expected_actions("local_delete_placeholder"))
        episode = report.per_episode[0]

        self.assertTrue(episode.expected_candidate_blocked)
        self.assertFalse(episode.exact_match)
        self.assertEqual(report.blocked_expected_count, 1)

    def test_expected_action_does_not_change_ranking(self) -> None:
        before = [candidate["candidate_id"] for candidate in score_sets()[0]["candidate_scores"]]
        data = score_sets()

        _ = evaluate_score_sets(data, expected_actions("local_delete_placeholder"))

        after = [candidate["candidate_id"] for candidate in data[0]["candidate_scores"]]
        self.assertEqual(before, after)

    def test_forbidden_fields_are_rejected(self) -> None:
        with self.assertRaises(EvaluationInputError):
            load_score_sets(FORBIDDEN_SCORE_FIXTURE)
        with self.assertRaises(EvaluationInputError):
            load_expected_actions(FORBIDDEN_EXPECTED_FIXTURE)

    def test_cli_writes_report_without_forbidden_metrics_or_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "evaluation_report.json"

            summary = run(SCORES_FIXTURE, EXPECTED_FIXTURE, output)

            self.assertIn("evaluation: ok", summary)
            self.assertNotIn("f1", summary.lower())
            self.assertNotIn("accuracy", summary.lower())
            self.assertNotIn("calibration", summary.lower())
            report_text = output.read_text(encoding="utf-8")
            self.assertNotIn("final_text", report_text)
            self.assertNotIn("observed_after_text", report_text)
            self.assertNotIn("gold_label", report_text)
            self.assertNotIn("teacher_correction", report_text)
            self.assertNotIn("f1", report_text.lower())
            self.assertNotIn("accuracy", report_text.lower())
            self.assertNotIn("calibration", report_text.lower())
            report = json.loads(report_text)
            self.assertEqual(report["exact_match_rate"], 1.0)

    def test_source_does_not_use_eval_exec_or_pickle(self) -> None:
        source_dir = Path("python/evaluation")
        source_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in source_dir.glob("*.py")
        )

        self.assertNotIn("eval(", source_text)
        self.assertNotIn("exec(", source_text)
        self.assertNotIn("pickle", source_text)


def expected_actions(action_type: str) -> dict[str, ExpectedAction]:
    return {
        "synthetic_session_001:micro:3": ExpectedAction(
            episode_id="synthetic_session_001:micro:3",
            expected_action_type=action_type,
            expected_source="synthetic_expected_action_fixture",
            synthetic_only=True,
            notes="Synthetic expected action for evaluation schema tests.",
        )
    }


def score_sets() -> list[dict[str, object]]:
    return [
        {
            "candidate_score_set_id": (
                "synthetic_session_001:micro:3:candidate_set:features:constraints:scores"
            ),
            "constraint_violation_set_id": (
                "synthetic_session_001:micro:3:candidate_set:features:constraints"
            ),
            "episode_id": "synthetic_session_001:micro:3",
            "scoring_policy_version": "weighted_ot_scorer_policy_v0_1",
            "candidate_scores": [
                candidate_score("hold", 1, blocked=False),
                candidate_score("local_delete_placeholder", 2, blocked=False),
                candidate_score("article_fix_placeholder", 3, blocked=False),
            ],
        }
    ]


def candidate_score(action_type: str, rank: int, *, blocked: bool) -> dict[str, object]:
    return {
        "candidate_id": f"synthetic_session_001:micro:3:cand:{rank:02d}:{action_type}",
        "episode_id": "synthetic_session_001:micro:3",
        "weighted_score": 0.0,
        "blocked": blocked,
        "block_reasons": [],
        "rank": rank,
        "constraint_contributions": [],
        "scoring_policy_version": "weighted_ot_scorer_policy_v0_1",
        "no_oracle_safe": not blocked,
    }


if __name__ == "__main__":
    unittest.main()
