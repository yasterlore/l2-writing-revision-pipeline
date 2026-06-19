from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ot_scorer.loader import CandidateFeatureError
from ot_scorer.score import run
from ot_scorer.scorer import build_candidate_score_set
from ot_scorer.violation_set_loader import load_constraint_violation_sets

FIXTURE = Path(
    "tests/fixtures/synthetic/constraint_violations/valid/deletion_constraint_violations.jsonl"
)
FORBIDDEN_FIXTURE = Path(
    "tests/fixtures/synthetic/constraint_violations/invalid/forbidden_field_constraint_violations.jsonl"
)


class ScorerTests(unittest.TestCase):
    def test_loads_constraint_violation_set_jsonl(self) -> None:
        violation_sets = load_constraint_violation_sets(FIXTURE)

        self.assertEqual(len(violation_sets), 1)
        self.assertEqual(
            violation_sets[0]["constraint_violation_set_id"],
            "synthetic_session_001:micro:3:candidate_set:features:constraints",
        )

    def test_builds_candidate_score_set(self) -> None:
        score_set = build_candidate_score_set(constraint_violation_set())

        self.assertEqual(
            score_set.candidate_score_set_id,
            "synthetic_session_001:micro:3:candidate_set:features:constraints:scores",
        )
        self.assertEqual(len(score_set.candidate_scores), 4)
        self.assertEqual(score_set.candidate_scores[0].action_type, "hold")
        self.assertEqual(
            score_set.candidate_scores[1].generation_rule,
            "revision_kind_delete_like",
        )
        self.assertEqual(score_set.candidate_scores[1].action_family, "local_edit")

    def test_leakage_violation_blocks_candidate(self) -> None:
        data = constraint_violation_set()
        set_violation_count(data, 0, "NO-LEAKAGE-FLAG", 1)

        score = build_candidate_score_set(data).candidate_scores[-1]

        self.assertTrue(score.blocked)
        self.assertIn("NO-LEAKAGE-FLAG", score.block_reasons)

    def test_observed_edit_text_violation_blocks_candidate(self) -> None:
        data = constraint_violation_set()
        set_violation_count(data, 0, "NO-OBSERVED-EDIT-TEXT", 1)

        score = build_candidate_score_set(data).candidate_scores[-1]

        self.assertTrue(score.blocked)
        self.assertIn("NO-OBSERVED-EDIT-TEXT", score.block_reasons)

    def test_unsafe_candidate_violation_blocks_candidate(self) -> None:
        data = constraint_violation_set()
        set_violation_count(data, 0, "NO-UNSAFE-CANDIDATE", 1)

        score = build_candidate_score_set(data).candidate_scores[-1]

        self.assertTrue(score.blocked)
        self.assertIn("NO-UNSAFE-CANDIDATE", score.block_reasons)

    def test_descriptive_constraints_do_not_add_to_score(self) -> None:
        score_set = build_candidate_score_set(constraint_violation_set())

        scores = [score.weighted_score for score in score_set.candidate_scores]

        self.assertEqual(scores, [0.0, 0.0, 0.0, 0.0])

    def test_tie_break_is_deterministic(self) -> None:
        first = build_candidate_score_set(constraint_violation_set()).to_json_dict()
        second = build_candidate_score_set(constraint_violation_set()).to_json_dict()

        self.assertEqual(first, second)

    def test_hold_local_grammar_tie_break_order(self) -> None:
        score_set = build_candidate_score_set(constraint_violation_set())
        ordered_ids = [score.candidate_id for score in score_set.candidate_scores]
        ordered_action_types = [
            score.action_type for score in score_set.candidate_scores
        ]

        self.assertEqual(
            ordered_ids,
            [
                "synthetic_session_001:micro:3:cand:01:hold",
                "synthetic_session_001:micro:3:cand:02:local_delete_placeholder",
                "synthetic_session_001:micro:3:cand:03:article_fix_placeholder",
                "synthetic_session_001:micro:3:cand:04:other_placeholder",
            ],
        )
        self.assertEqual(
            ordered_action_types,
            [
                "hold",
                "local_delete_placeholder",
                "article_fix_placeholder",
                "other_placeholder",
            ],
        )

    def test_generation_rule_and_action_family_do_not_change_order(self) -> None:
        score_set = build_candidate_score_set(constraint_violation_set())

        ordered_metadata = [
            (score.action_type, score.generation_rule, score.action_family)
            for score in score_set.candidate_scores
        ]

        self.assertEqual(
            ordered_metadata,
            [
                ("hold", "always_include_hold", "hold"),
                (
                    "local_delete_placeholder",
                    "revision_kind_delete_like",
                    "local_edit",
                ),
                (
                    "article_fix_placeholder",
                    "article_placeholder_rule",
                    "grammar_placeholder",
                ),
                ("other_placeholder", "synthetic_other_placeholder_rule", "other"),
            ],
        )

    def test_ranks_are_unique_within_episode(self) -> None:
        score_set = build_candidate_score_set(constraint_violation_set())
        ranks = [score.rank for score in score_set.candidate_scores]

        self.assertEqual(ranks, [1, 2, 3, 4])
        self.assertEqual(len(ranks), len(set(ranks)))

    def test_forbidden_field_input_is_rejected(self) -> None:
        with self.assertRaises(CandidateFeatureError):
            load_constraint_violation_sets(FORBIDDEN_FIXTURE)

    def test_cli_output_excludes_forbidden_fields_and_text_fragments(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "candidate_scores.jsonl"

            summary = run(FIXTURE, output)

            self.assertIn("candidate_scores: ok", summary)
            output_text = output.read_text(encoding="utf-8")
            self.assertNotIn("final_text", output_text)
            self.assertNotIn("observed_after_text", output_text)
            self.assertNotIn("gold_label", output_text)
            self.assertNotIn("teacher_correction", output_text)
            self.assertNotIn("Synthetic candidate description", output_text)
            rows = [json.loads(line) for line in output_text.splitlines()]
            self.assertIn("candidate_scores", rows[0])
            self.assertIn("action_type", rows[0]["candidate_scores"][0])
            self.assertIn("generation_rule", rows[0]["candidate_scores"][0])
            self.assertIn("action_family", rows[0]["candidate_scores"][0])

    def test_source_does_not_use_eval_exec_or_pickle(self) -> None:
        source_dir = Path("python/ot_scorer")
        source_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in source_dir.glob("*.py")
        )

        self.assertNotIn("eval(", source_text)
        self.assertNotIn("exec(", source_text)
        self.assertNotIn("pickle", source_text)


def set_violation_count(
    data: dict[str, object],
    candidate_index: int,
    constraint_id: str,
    violation_count: int,
) -> None:
    candidate = data["candidate_violations"][candidate_index]
    for violation in candidate["violations"]:
        if violation["constraint_id"] == constraint_id:
            violation["violation_count"] = violation_count
            violation["observed"] = violation_count > 0
            return
    raise AssertionError(f"missing constraint: {constraint_id}")


def constraint_violation_set() -> dict[str, object]:
    return {
        "constraint_violation_set_id": (
            "synthetic_session_001:micro:3:candidate_set:features:constraints"
        ),
        "candidate_feature_set_id": (
            "synthetic_session_001:micro:3:candidate_set:features"
        ),
        "episode_id": "synthetic_session_001:micro:3",
        "constraint_schema_version": "ot_constraint_schema_v0_1",
        "candidate_violations": [
            candidate_violations(
                "synthetic_session_001:micro:3:cand:01:hold",
                "hold",
                hold=True,
            ),
            candidate_violations(
                "synthetic_session_001:micro:3:cand:02:local_delete_placeholder",
                "local_delete_placeholder",
                local=True,
                placeholder=True,
            ),
            candidate_violations(
                "synthetic_session_001:micro:3:cand:03:article_fix_placeholder",
                "article_fix_placeholder",
                grammar=True,
                placeholder=True,
            ),
            candidate_violations(
                "synthetic_session_001:micro:3:cand:04:other_placeholder",
                "other_placeholder",
                placeholder=True,
            ),
        ],
    }


def candidate_violations(
    candidate_id: str,
    action_type: str,
    *,
    hold: bool = False,
    local: bool = False,
    grammar: bool = False,
    placeholder: bool = False,
) -> dict[str, object]:
    return {
        "candidate_id": candidate_id,
        "episode_id": "synthetic_session_001:micro:3",
        "action_type": action_type,
        "generation_rule": generation_rule_for_action(action_type),
        "action_family": action_family_for_flags(
            hold=hold, local=local, grammar=grammar, placeholder=placeholder
        ),
        "violations": [
            penalty("NO-LEAKAGE-FLAG"),
            penalty("NO-OBSERVED-EDIT-TEXT"),
            penalty("NO-UNSAFE-CANDIDATE"),
            descriptive("HOLD-CANDIDATE", hold),
            descriptive("LOCAL-EDIT-CANDIDATE", local),
            descriptive("GRAMMAR-PLACEHOLDER-CANDIDATE", grammar),
            descriptive("PLACEHOLDER-CANDIDATE", placeholder),
        ],
    }


def generation_rule_for_action(action_type: str) -> str:
    if action_type == "hold":
        return "always_include_hold"
    if action_type == "local_delete_placeholder":
        return "revision_kind_delete_like"
    if action_type == "article_fix_placeholder":
        return "article_placeholder_rule"
    return "synthetic_other_placeholder_rule"


def action_family_for_flags(
    *, hold: bool, local: bool, grammar: bool, placeholder: bool
) -> str:
    if hold:
        return "hold"
    if local:
        return "local_edit"
    if grammar:
        return "grammar_placeholder"
    if placeholder:
        return "other"
    return "other"


def penalty(constraint_id: str) -> dict[str, object]:
    return {
        "candidate_id": "synthetic_candidate",
        "episode_id": "synthetic_session_001:micro:3",
        "constraint_id": constraint_id,
        "constraint_type": "penalty",
        "violation_count": 0,
        "severity": "blocking",
        "explanation": "Synthetic penalty constraint.",
        "observed": False,
    }


def descriptive(constraint_id: str, observed: bool) -> dict[str, object]:
    return {
        "candidate_id": "synthetic_candidate",
        "episode_id": "synthetic_session_001:micro:3",
        "constraint_id": constraint_id,
        "constraint_type": "descriptive",
        "violation_count": 0,
        "severity": "info",
        "explanation": "Synthetic descriptive constraint.",
        "observed": observed,
    }


if __name__ == "__main__":
    unittest.main()
