from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ot_scorer.constraint_builder import build_constraint_violation_set
from ot_scorer.constraints import run
from ot_scorer.feature_set_loader import load_candidate_feature_sets
from ot_scorer.loader import CandidateFeatureError

FIXTURE = Path(
    "tests/fixtures/synthetic/candidate_features/valid/deletion_candidate_features.jsonl"
)
FORBIDDEN_FIXTURE = Path(
    "tests/fixtures/synthetic/candidate_features/invalid/forbidden_field_candidate_features.jsonl"
)


class ConstraintTests(unittest.TestCase):
    def test_loads_candidate_feature_set_jsonl(self) -> None:
        feature_sets = load_candidate_feature_sets(FIXTURE)

        self.assertEqual(len(feature_sets), 1)
        self.assertEqual(
            feature_sets[0]["candidate_feature_set_id"],
            "synthetic_session_001:micro:3:candidate_set:features",
        )

    def test_builds_constraint_violation_set(self) -> None:
        violation_set = build_constraint_violation_set(candidate_feature_set())

        self.assertEqual(
            violation_set.constraint_violation_set_id,
            "synthetic_session_001:micro:3:candidate_set:features:constraints",
        )
        self.assertEqual(violation_set.constraint_schema_version, "ot_constraint_schema_v0_2")
        self.assertEqual(len(violation_set.candidate_violations), 3)
        self.assertEqual(
            violation_set.candidate_violations[1].generation_rule,
            "revision_kind_delete_like",
        )
        self.assertEqual(
            violation_set.candidate_violations[1].action_family,
            "local_edit",
        )

    def test_leakage_flags_get_no_leakage_flag_violation(self) -> None:
        data = candidate_feature_set()
        data["candidate_features"][0]["leakage_flags"] = ["synthetic_leakage_flag"]

        violation = find_violation(
            build_constraint_violation_set(data),
            candidate_index=0,
            constraint_id="NO-LEAKAGE-FLAG",
        )

        self.assertEqual(violation["violation_count"], 1)
        self.assertEqual(violation["constraint_type"], "penalty")

    def test_observed_edit_text_gets_violation(self) -> None:
        data = candidate_feature_set()
        data["candidate_features"][0]["uses_observed_edit_text"] = True

        violation = find_violation(
            build_constraint_violation_set(data),
            candidate_index=0,
            constraint_id="NO-OBSERVED-EDIT-TEXT",
        )

        self.assertEqual(violation["violation_count"], 1)

    def test_unsafe_candidate_gets_violation(self) -> None:
        data = candidate_feature_set()
        data["candidate_features"][0]["no_oracle_safe"] = False

        violation = find_violation(
            build_constraint_violation_set(data),
            candidate_index=0,
            constraint_id="NO-UNSAFE-CANDIDATE",
        )

        self.assertEqual(violation["violation_count"], 1)

    def test_identifies_hold_local_and_grammar_candidates(self) -> None:
        violation_set = build_constraint_violation_set(candidate_feature_set())

        self.assertTrue(
            find_violation(violation_set, 0, "HOLD-CANDIDATE")["observed"]
        )
        self.assertTrue(
            find_violation(violation_set, 1, "LOCAL-EDIT-CANDIDATE")["observed"]
        )
        self.assertTrue(
            find_violation(violation_set, 2, "GRAMMAR-PLACEHOLDER-CANDIDATE")[
                "observed"
            ]
        )
        self.assertTrue(
            find_violation(violation_set, 1, "PLACEHOLDER-CANDIDATE")["observed"]
        )

    def test_identifies_structural_descriptive_constraints(self) -> None:
        violation_set = build_constraint_violation_set(candidate_feature_set())

        self.assertTrue(
            find_violation(violation_set, 0, "HAS-GENERATION-RULE")["observed"]
        )
        self.assertTrue(
            find_violation(violation_set, 0, "HAS-ACTION-FAMILY")["observed"]
        )
        self.assertTrue(
            find_violation(violation_set, 0, "CANDIDATE-METADATA-COMPLETE")[
                "observed"
            ]
        )
        self.assertTrue(
            find_violation(violation_set, 0, "HOLD-FAMILY-CANDIDATE")["observed"]
        )
        self.assertTrue(
            find_violation(violation_set, 1, "LOCAL-EDIT-FAMILY-CANDIDATE")[
                "observed"
            ]
        )
        self.assertTrue(
            find_violation(violation_set, 2, "GRAMMAR-FAMILY-CANDIDATE")[
                "observed"
            ]
        )
        self.assertTrue(
            find_violation(violation_set, 1, "PLACEHOLDER-FAMILY-CANDIDATE")[
                "observed"
            ]
        )
        self.assertFalse(
            find_violation(violation_set, 0, "SAFETY-RELEVANT-CANDIDATE")[
                "observed"
            ]
        )
        self.assertTrue(
            find_violation(violation_set, 1, "CANDIDATE-FAMILY-BUCKET")[
                "observed"
            ]
        )

    def test_descriptive_constraints_have_zero_violation_count(self) -> None:
        violation_set = build_constraint_violation_set(candidate_feature_set())
        candidate = violation_set.to_json_dict()["candidate_violations"][1]

        for violation in candidate["violations"]:
            if violation["constraint_type"] == "descriptive":
                self.assertEqual(violation["violation_count"], 0)

    def test_identifies_linguistic_placeholder_constraints(self) -> None:
        data = candidate_feature_set()
        data["candidate_features"] = [
            grammar_placeholder_feature(
                "article_fix_placeholder",
                "article_placeholder_rule",
            ),
            grammar_placeholder_feature(
                "number_fix_placeholder",
                "number_placeholder_rule",
            ),
            grammar_placeholder_feature(
                "sva_fix_placeholder",
                "sva_placeholder_rule",
            ),
            grammar_placeholder_feature(
                "tense_fix_placeholder",
                "tense_placeholder_rule",
            ),
            grammar_placeholder_feature(
                "preposition_fix_placeholder",
                "preposition_placeholder_rule",
            ),
            grammar_placeholder_feature(
                "punctuation_fix_placeholder",
                "punctuation_placeholder_rule",
            ),
        ]

        violation_set = build_constraint_violation_set(data)

        expected_constraints = [
            "ARTICLE-PLACEHOLDER-CANDIDATE",
            "NUMBER-PLACEHOLDER-CANDIDATE",
            "SVA-PLACEHOLDER-CANDIDATE",
            "TENSE-PLACEHOLDER-CANDIDATE",
            "PREPOSITION-PLACEHOLDER-CANDIDATE",
            "PUNCTUATION-PLACEHOLDER-CANDIDATE",
        ]
        for index, constraint_id in enumerate(expected_constraints):
            with self.subTest(constraint_id=constraint_id):
                violation = find_violation(violation_set, index, constraint_id)
                self.assertTrue(violation["observed"])
                self.assertEqual(violation["constraint_type"], "descriptive")
                self.assertEqual(violation["violation_count"], 0)

    def test_rejects_forbidden_field(self) -> None:
        with self.assertRaises(CandidateFeatureError):
            load_candidate_feature_sets(FORBIDDEN_FIXTURE)

    def test_cli_output_excludes_text_and_scoring_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "constraint_violations.jsonl"

            summary = run(FIXTURE, output)

            self.assertIn("constraint_violations: ok", summary)
            output_text = output.read_text(encoding="utf-8")
            self.assertNotIn("Synthetic candidate description", output_text)
            self.assertNotIn("local_context", output_text)
            self.assertNotIn("weighted_score", output_text)
            self.assertNotIn("rank", output_text)
            rows = [json.loads(line) for line in output_text.splitlines()]
            self.assertIn("candidate_violations", rows[0])

    def test_source_does_not_use_eval_exec_or_pickle(self) -> None:
        source_dir = Path("python/ot_scorer")
        source_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in source_dir.glob("*.py")
        )

        self.assertNotIn("eval(", source_text)
        self.assertNotIn("exec(", source_text)
        self.assertNotIn("pickle", source_text)


def find_violation(
    violation_set: object, candidate_index: int, constraint_id: str
) -> dict[str, object]:
    candidate = violation_set.to_json_dict()["candidate_violations"][candidate_index]
    for violation in candidate["violations"]:
        if violation["constraint_id"] == constraint_id:
            return violation
    raise AssertionError(f"missing constraint: {constraint_id}")


def candidate_feature_set() -> dict[str, object]:
    return {
        "candidate_feature_set_id": "synthetic_session_001:micro:3:candidate_set:features",
        "candidate_set_id": "synthetic_session_001:micro:3:candidate_set",
        "episode_id": "synthetic_session_001:micro:3",
        "no_oracle_safe": True,
        "feature_schema_version": "candidate_feature_schema_v0_2",
        "leakage_flags": [],
        "candidate_features": [
            {
                "candidate_id": "synthetic_session_001:micro:3:cand:01:hold",
                "episode_id": "synthetic_session_001:micro:3",
                "action_type": "hold",
                "generation_rule": "always_include_hold",
                "no_oracle_safe": True,
                "uses_observed_edit_text": False,
                "action_family": "hold",
                "candidate_metadata_complete": True,
                "has_generation_rule": True,
                "has_action_family": True,
                "is_safety_relevant_candidate": False,
                "is_placeholder_candidate": False,
                "is_grammar_family_candidate": False,
                "is_local_edit_family_candidate": False,
                "is_hold_candidate": True,
                "candidate_family_bucket": "hold",
                "is_placeholder": False,
                "is_hold": True,
                "is_local_edit": False,
                "is_grammar_placeholder": False,
                "candidate_description_length": 41,
                "feature_notes_count": 1,
                "leakage_flags": [],
            },
            {
                "candidate_id": "synthetic_session_001:micro:3:cand:02:local_delete_placeholder",
                "episode_id": "synthetic_session_001:micro:3",
                "action_type": "local_delete_placeholder",
                "generation_rule": "revision_kind_delete_like",
                "no_oracle_safe": True,
                "uses_observed_edit_text": False,
                "action_family": "local_edit",
                "candidate_metadata_complete": True,
                "has_generation_rule": True,
                "has_action_family": True,
                "is_safety_relevant_candidate": False,
                "is_placeholder_candidate": True,
                "is_grammar_family_candidate": False,
                "is_local_edit_family_candidate": True,
                "is_hold_candidate": False,
                "candidate_family_bucket": "local_edit",
                "is_placeholder": True,
                "is_hold": False,
                "is_local_edit": True,
                "is_grammar_placeholder": False,
                "candidate_description_length": 51,
                "feature_notes_count": 1,
                "leakage_flags": [],
            },
            {
                "candidate_id": "synthetic_session_001:micro:3:cand:03:article_fix_placeholder",
                "episode_id": "synthetic_session_001:micro:3",
                "action_type": "article_fix_placeholder",
                "generation_rule": "article_placeholder_rule",
                "no_oracle_safe": True,
                "uses_observed_edit_text": False,
                "action_family": "grammar_placeholder",
                "candidate_metadata_complete": True,
                "has_generation_rule": True,
                "has_action_family": True,
                "is_safety_relevant_candidate": False,
                "is_placeholder_candidate": True,
                "is_grammar_family_candidate": True,
                "is_local_edit_family_candidate": False,
                "is_hold_candidate": False,
                "candidate_family_bucket": "grammar_placeholder",
                "is_placeholder": True,
                "is_hold": False,
                "is_local_edit": False,
                "is_grammar_placeholder": True,
                "candidate_description_length": 50,
                "feature_notes_count": 1,
                "leakage_flags": [],
            },
        ],
    }


def grammar_placeholder_feature(action_type: str, generation_rule: str) -> dict[str, object]:
    return {
        "candidate_id": f"synthetic_session_001:micro:3:cand:synthetic:{action_type}",
        "episode_id": "synthetic_session_001:micro:3",
        "action_type": action_type,
        "generation_rule": generation_rule,
        "no_oracle_safe": True,
        "uses_observed_edit_text": False,
        "action_family": "grammar_placeholder",
        "candidate_metadata_complete": True,
        "has_generation_rule": True,
        "has_action_family": True,
        "is_safety_relevant_candidate": False,
        "is_placeholder_candidate": True,
        "is_grammar_family_candidate": True,
        "is_local_edit_family_candidate": False,
        "is_hold_candidate": False,
        "candidate_family_bucket": "grammar_placeholder",
        "is_placeholder": True,
        "is_hold": False,
        "is_local_edit": False,
        "is_grammar_placeholder": True,
        "candidate_description_length": 0,
        "feature_notes_count": 0,
        "leakage_flags": [],
    }


if __name__ == "__main__":
    unittest.main()
