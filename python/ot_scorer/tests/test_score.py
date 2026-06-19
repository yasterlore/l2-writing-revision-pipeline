from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ot_scorer.loader import CandidateFeatureError
from ot_scorer.score import run
from ot_scorer.scorer import (
    build_candidate_score_set,
    score_constraint_violation_set_with_config,
)
from ot_scorer.violation_set_loader import load_constraint_violation_sets
from ot_scorer.weight_config import WeightConfigError, parse_hand_weight_config

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

    def test_config_aware_function_with_default_like_config_matches_default(self) -> None:
        data = constraint_violation_set()
        config = parse_hand_weight_config(default_like_config_dict())

        default_score_set = build_candidate_score_set(data).to_json_dict()
        config_score_set = score_constraint_violation_set_with_config(
            data, config
        ).to_json_dict()

        self.assertEqual(config_score_set, default_score_set)
        self.assertNotIn("config_schema_version", config_score_set)
        self.assertNotIn("config_name", config_score_set)
        self.assertNotIn("constraint_weights", config_score_set)
        assert_no_config_fields(self, config_score_set)

    def test_default_function_output_snapshot_is_unchanged(self) -> None:
        score_set = build_candidate_score_set(constraint_violation_set()).to_json_dict()

        self.assertEqual(score_set["scoring_policy_version"], "weighted_ot_scorer_policy_v0_1")
        self.assertEqual(
            [
                (
                    score["candidate_id"],
                    score["rank"],
                    score["weighted_score"],
                    score["blocked"],
                    score["block_reasons"],
                )
                for score in score_set["candidate_scores"]
            ],
            [
                (
                    "synthetic_session_001:micro:3:cand:01:hold",
                    1,
                    0.0,
                    False,
                    [],
                ),
                (
                    "synthetic_session_001:micro:3:cand:02:local_delete_placeholder",
                    2,
                    0.0,
                    False,
                    [],
                ),
                (
                    "synthetic_session_001:micro:3:cand:03:article_fix_placeholder",
                    3,
                    0.0,
                    False,
                    [],
                ),
                (
                    "synthetic_session_001:micro:3:cand:04:other_placeholder",
                    4,
                    0.0,
                    False,
                    [],
                ),
            ],
        )
        assert_no_config_fields(self, score_set)

    def test_config_aware_function_can_change_explicit_weight_only(self) -> None:
        data = constraint_violation_set()
        set_violation_count(data, 0, "NO-LEAKAGE-FLAG", 1)
        config_data = default_like_config_dict()
        config_data["config_name"] = "synthetic_unit_test_leakage_weight"
        config_data["constraint_weights"][0]["weight"] = 5.0
        config_data["constraint_weights"][0]["rationale"] = (
            "Synthetic unit test config changes only the leakage weight."
        )
        config = parse_hand_weight_config(config_data)

        default_score_set = build_candidate_score_set(data)
        config_score_set = score_constraint_violation_set_with_config(data, config)
        default_score = find_score(
            default_score_set,
            "synthetic_session_001:micro:3:cand:01:hold",
        )
        config_score = find_score(
            config_score_set,
            "synthetic_session_001:micro:3:cand:01:hold",
        )

        self.assertEqual(default_score.weighted_score, 1_000_000.0)
        self.assertEqual(config_score.weighted_score, 5.0)
        self.assertTrue(config_score.blocked)
        self.assertEqual(config_score.block_reasons, ["NO-LEAKAGE-FLAG"])
        self.assertEqual(
            [score.candidate_id for score in config_score_set.candidate_scores],
            [score.candidate_id for score in default_score_set.candidate_scores],
        )
        unchanged_default_score = find_score(
            build_candidate_score_set(data),
            "synthetic_session_001:micro:3:cand:01:hold",
        )
        self.assertEqual(unchanged_default_score.weighted_score, 1_000_000.0)

    def test_config_aware_tie_break_matches_default_for_equal_scores(self) -> None:
        data = constraint_violation_set()
        config = parse_hand_weight_config(default_like_config_dict())

        config_score_set = score_constraint_violation_set_with_config(data, config)

        self.assertEqual(
            [score.candidate_id for score in config_score_set.candidate_scores],
            [
                "synthetic_session_001:micro:3:cand:01:hold",
                "synthetic_session_001:micro:3:cand:02:local_delete_placeholder",
                "synthetic_session_001:micro:3:cand:03:article_fix_placeholder",
                "synthetic_session_001:micro:3:cand:04:other_placeholder",
            ],
        )

    def test_config_aware_blocking_keeps_unsafe_candidate_out_of_top_rank(self) -> None:
        data = constraint_violation_set()
        set_violation_count(data, 0, "NO-UNSAFE-CANDIDATE", 1)
        config = parse_hand_weight_config(default_like_config_dict())

        score_set = score_constraint_violation_set_with_config(data, config)
        blocked_score = find_score(
            score_set,
            "synthetic_session_001:micro:3:cand:01:hold",
        )

        self.assertTrue(blocked_score.blocked)
        self.assertIn("NO-UNSAFE-CANDIDATE", blocked_score.block_reasons)
        self.assertGreater(blocked_score.rank, 1)
        self.assertFalse(score_set.candidate_scores[0].blocked)

    def test_config_aware_inactive_weight_is_ignored(self) -> None:
        data = constraint_violation_set()
        set_violation_count(data, 0, "HOLD-CANDIDATE", 1)
        config_data = default_like_config_dict()
        config_data["constraint_weights"].append(
            config_weight("HOLD-CANDIDATE", 999.0, active=False)
        )
        config = parse_hand_weight_config(config_data)

        score_set = score_constraint_violation_set_with_config(data, config)
        hold_score = find_score(
            score_set,
            "synthetic_session_001:micro:3:cand:01:hold",
        )

        self.assertEqual(hold_score.weighted_score, 0.0)
        self.assertEqual(
            find_contribution_weight(hold_score, "HOLD-CANDIDATE"),
            0.0,
        )

    def test_config_aware_function_does_not_mutate_default_path(self) -> None:
        data = constraint_violation_set()
        config = parse_hand_weight_config(default_like_config_dict())
        before = build_candidate_score_set(data).to_json_dict()

        score_constraint_violation_set_with_config(data, config)
        after = build_candidate_score_set(data).to_json_dict()

        self.assertEqual(after, before)

    def test_invalid_config_is_rejected_before_config_aware_scoring(self) -> None:
        config_data = default_like_config_dict()
        config_data["constraint_weights"][0]["rationale"] = ""

        with self.assertRaises(WeightConfigError):
            parse_hand_weight_config(config_data)

    def test_unknown_active_constraint_is_rejected_before_config_aware_scoring(self) -> None:
        config_data = default_like_config_dict()
        config_data["constraint_weights"].append(
            config_weight("SYNTHETIC-UNKNOWN-CONSTRAINT", 1.0)
        )

        with self.assertRaises(WeightConfigError):
            parse_hand_weight_config(config_data)

    def test_config_aware_output_schema_excludes_config_and_forbidden_fields(self) -> None:
        data = constraint_violation_set()
        config = parse_hand_weight_config(default_like_config_dict())

        score_set = score_constraint_violation_set_with_config(
            data, config
        ).to_json_dict()

        assert_no_config_fields(self, score_set)
        assert_forbidden_output_fields_absent(self, score_set)

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

    def test_score_cli_has_no_config_option(self) -> None:
        source = Path("python/ot_scorer/score.py").read_text(encoding="utf-8")

        self.assertNotIn("--config", source)
        self.assertNotIn("--weight-config", source)
        self.assertNotIn("load_hand_weight_config", source)

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


def find_score(score_set: object, candidate_id: str) -> object:
    for score in score_set.candidate_scores:
        if score.candidate_id == candidate_id:
            return score
    raise AssertionError(f"missing score: {candidate_id}")


def find_contribution_weight(score: object, constraint_id: str) -> float:
    for contribution in score.constraint_contributions:
        if contribution.constraint_id == constraint_id:
            return contribution.weight
    raise AssertionError(f"missing contribution: {constraint_id}")


def assert_no_config_fields(
    test_case: unittest.TestCase,
    score_set: dict[str, object],
) -> None:
    forbidden_config_fields = [
        "config_schema_version",
        "config_name",
        "config",
        "weight_config",
        "constraint_weights",
        "score_active_constraint_families",
    ]
    serialized = json.dumps(score_set, ensure_ascii=False)
    for field in forbidden_config_fields:
        test_case.assertNotIn(field, score_set)
        test_case.assertNotIn(f'"{field}"', serialized)


def assert_forbidden_output_fields_absent(
    test_case: unittest.TestCase,
    score_set: dict[str, object],
) -> None:
    serialized = json.dumps(score_set, ensure_ascii=False)
    forbidden_fragments = [
        "final_text",
        "observed_after_text",
        "gold_label",
        "teacher_correction",
        "expected_action",
        "raw_text",
        "raw_local_context_before",
        "local_context_before",
        "local_context_after_observed",
        "candidate_description",
        "proposed_edit",
    ]
    for fragment in forbidden_fragments:
        test_case.assertNotIn(fragment, serialized)


def default_like_config_dict() -> dict[str, object]:
    return {
        "config_schema_version": "hand_weight_config_schema_v0_1",
        "config_name": "synthetic_unit_test_default_like",
        "created_for": "synthetic scorer unit test only",
        "default_behavior": "Default scorer path remains unchanged.",
        "score_active_constraint_families": ["safety_blocking"],
        "constraint_weights": [
            config_weight("NO-LEAKAGE-FLAG", 1_000_000.0),
            config_weight("NO-OBSERVED-EDIT-TEXT", 1_000_000.0),
            config_weight("NO-UNSAFE-CANDIDATE", 1_000_000.0),
        ],
        "blocking_constraints": [
            "NO-LEAKAGE-FLAG",
            "NO-OBSERVED-EDIT-TEXT",
            "NO-UNSAFE-CANDIDATE",
        ],
        "score_neutral_constraints": [
            "HOLD-CANDIDATE",
            "LOCAL-EDIT-CANDIDATE",
            "GRAMMAR-PLACEHOLDER-CANDIDATE",
            "PLACEHOLDER-CANDIDATE",
        ],
        "rationale": "Synthetic unit test config; not connected to default scoring.",
        "no_oracle_review": {
            "review_status": "synthetic unit test only",
            "allowed_information": ["constraint_id", "violation_count"],
            "forbidden_information": [
                "final_text",
                "observed_after_text",
                "gold_label",
                "expected action",
                "real participant data",
            ],
        },
        "synthetic_only_notice": (
            "Synthetic unit test config only; no real participant data is used."
        ),
        "expected_action_usage_policy": (
            "Expected actions are not used for scoring or weight tuning."
        ),
        "forbidden_information_policy": {
            "forbidden_fields": [
                "final_text",
                "observed_after_text",
                "gold_label",
                "teacher_correction",
            ],
            "forbidden_path_parts": [
                "manual_outputs",
                "private_data",
                "real_data",
                "participant_data",
            ],
            "raw_text_policy": "Raw text patterns are not allowed in config.",
        },
    }


def config_weight(
    constraint_id: str,
    weight: float,
    *,
    active: bool = True,
) -> dict[str, object]:
    return {
        "constraint_id": constraint_id,
        "constraint_family": "safety_blocking",
        "weight": weight,
        "active": active,
        "rationale": "Synthetic unit test active safety weight.",
        "no_oracle_safe_reason": "Uses no-oracle safety flags only.",
        "expected_effect": "Candidate is blocked when violation_count is positive.",
        "risk_note": "Synthetic unit test only; not a performance claim.",
        "tests_required": ["default path unchanged"],
        "last_reviewed": "2026-06-19",
    }


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
