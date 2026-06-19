from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from evaluation.evaluate import run
from evaluation.evaluator import evaluate_score_sets
from evaluation.expected_action_registry import (
    ExpectedActionRegistryError,
    load_expected_action_registry,
    lookup_expected_action_path,
)
from evaluation.loader import EvaluationInputError, load_expected_actions, load_score_sets
from evaluation.models import ExpectedAction

SCORES_FIXTURE = Path(
    "tests/fixtures/synthetic/candidate_scores/valid/deletion_candidate_scores.jsonl"
)
EXPECTED_FIXTURE = Path(
    "tests/fixtures/synthetic/expected_actions/valid/deletion_expected_actions.jsonl"
)
SELECTION_EDIT_EXPECTED_FIXTURE = Path(
    "tests/fixtures/synthetic/expected_actions/valid/selection_edit_expected_actions.jsonl"
)
CURSOR_MOVEMENT_EXPECTED_FIXTURE = Path(
    "tests/fixtures/synthetic/expected_actions/valid/cursor_movement_expected_actions.jsonl"
)
REGISTRY_FIXTURE = Path("tests/fixtures/synthetic/expected_actions/registry.json")
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

    def test_loads_added_synthetic_expected_action_jsonl(self) -> None:
        selection_expected = load_expected_actions(SELECTION_EDIT_EXPECTED_FIXTURE)
        cursor_expected = load_expected_actions(CURSOR_MOVEMENT_EXPECTED_FIXTURE)

        self.assertIn("synthetic_session_005:micro:2", selection_expected)
        self.assertEqual(
            selection_expected[
                "synthetic_session_005:micro:2"
            ].expected_action_type,
            "local_replace_placeholder",
        )
        self.assertIn("synthetic_session_004:micro:3", cursor_expected)
        self.assertEqual(
            cursor_expected["synthetic_session_004:micro:3"].expected_action_type,
            "local_insert_placeholder",
        )

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

    def test_evaluation_uses_action_type_not_candidate_id_convention(self) -> None:
        data = score_sets()
        data[0]["candidate_scores"][0]["candidate_id"] = "synthetic_arbitrary_id_001"

        report = evaluate_score_sets(data, expected_actions("hold"))

        self.assertEqual(report.exact_match_count, 1)
        self.assertEqual(report.per_episode[0].top1_action_type, "hold")

    def test_forbidden_fields_are_rejected(self) -> None:
        with self.assertRaises(EvaluationInputError):
            load_score_sets(FORBIDDEN_SCORE_FIXTURE)
        with self.assertRaises(EvaluationInputError):
            load_expected_actions(FORBIDDEN_EXPECTED_FIXTURE)

    def test_loads_expected_action_registry(self) -> None:
        registry = load_expected_action_registry(REGISTRY_FIXTURE)

        self.assertIn("deletion_case", registry)
        self.assertEqual(registry["deletion_case"].status, "active")
        self.assertTrue(registry["deletion_case"].expected_action_path is not None)

    def test_registry_returns_deletion_expected_action_path(self) -> None:
        registry = load_expected_action_registry(REGISTRY_FIXTURE)

        lookup = lookup_expected_action_path(registry, "deletion_case")

        self.assertEqual(lookup.status, "active")
        self.assertIsNotNone(lookup.expected_action_path)
        self.assertEqual(lookup.expected_action_path.name, "deletion_expected_actions.jsonl")

    def test_registry_marks_added_expected_action_cases_active(self) -> None:
        registry = load_expected_action_registry(REGISTRY_FIXTURE)

        selection_lookup = lookup_expected_action_path(registry, "selection_edit_case")
        cursor_lookup = lookup_expected_action_path(registry, "cursor_movement_case")

        self.assertEqual(selection_lookup.status, "active")
        self.assertEqual(
            selection_lookup.expected_action_path.name,
            "selection_edit_expected_actions.jsonl",
        )
        self.assertEqual(cursor_lookup.status, "active")
        self.assertEqual(
            cursor_lookup.expected_action_path.name,
            "cursor_movement_expected_actions.jsonl",
        )

    def test_registry_marks_pending_case(self) -> None:
        registry = load_expected_action_registry(REGISTRY_FIXTURE)

        lookup = lookup_expected_action_path(registry, "simple_typing")

        self.assertEqual(lookup.status, "pending")
        self.assertIsNone(lookup.expected_action_path)

    def test_registry_marks_unknown_case_as_missing(self) -> None:
        registry = load_expected_action_registry(REGISTRY_FIXTURE)

        lookup = lookup_expected_action_path(registry, "unknown_case")

        self.assertEqual(lookup.status, "missing")
        self.assertIsNone(lookup.expected_action_path)

    def test_registry_rejects_duplicate_case_names(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            registry_path = write_registry(
                Path(directory),
                [
                    {"case_name": "duplicate_case", "status": "pending"},
                    {"case_name": "duplicate_case", "status": "pending"},
                ],
            )

            with self.assertRaises(ExpectedActionRegistryError):
                load_expected_action_registry(registry_path)

    def test_registry_rejects_missing_expected_action_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            registry_path = write_registry(
                Path(directory),
                [
                    {
                        "case_name": "missing_path_case",
                        "status": "active",
                        "expected_action_path": "tests/fixtures/synthetic/expected_actions/valid/missing.jsonl",
                    }
                ],
            )

            with self.assertRaises(ExpectedActionRegistryError):
                load_expected_action_registry(registry_path)

    def test_registry_rejects_private_or_manual_paths(self) -> None:
        forbidden_paths = [
            "manual_outputs/expected.jsonl",
            "private_data/expected.jsonl",
            "real_data/expected.jsonl",
            "participant_data/expected.jsonl",
        ]
        for forbidden_path in forbidden_paths:
            with self.subTest(forbidden_path=forbidden_path):
                with tempfile.TemporaryDirectory() as directory:
                    registry_path = write_registry(
                        Path(directory),
                        [
                            {
                                "case_name": "forbidden_path_case",
                                "status": "active",
                                "expected_action_path": forbidden_path,
                            }
                        ],
                    )

                    with self.assertRaises(ExpectedActionRegistryError):
                        load_expected_action_registry(registry_path)

    def test_registry_cli_lookup_outputs_status_and_path_only(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "evaluation.expected_action_registry",
                "lookup",
                "--registry",
                str(REGISTRY_FIXTURE),
                "--case-name",
                "deletion_case",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertTrue(result.stdout.startswith("active\t"))
        self.assertIn("deletion_expected_actions.jsonl", result.stdout)
        self.assertNotIn("expected_action_type", result.stdout)

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
        "action_type": action_type,
        "weighted_score": 0.0,
        "blocked": blocked,
        "block_reasons": [],
        "rank": rank,
        "constraint_contributions": [],
        "scoring_policy_version": "weighted_ot_scorer_policy_v0_1",
        "no_oracle_safe": not blocked,
    }


def write_registry(directory: Path, entries: list[dict[str, object]]) -> Path:
    registry_path = directory / "registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "registry_schema_version": "synthetic_expected_action_registry_v0_1",
                "synthetic_only": True,
                "entries": entries,
            }
        ),
        encoding="utf-8",
    )
    return registry_path


if __name__ == "__main__":
    unittest.main()
