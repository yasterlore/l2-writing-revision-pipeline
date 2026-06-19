from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ot_scorer.feature_builder import build_feature_set
from ot_scorer.features import run
from ot_scorer.loader import CandidateFeatureError, load_candidate_sets

FIXTURE = Path("tests/fixtures/synthetic/candidate_sets/valid/deletion_candidate_set.jsonl")
FORBIDDEN_FIXTURE = Path(
    "tests/fixtures/synthetic/candidate_sets/invalid/forbidden_field_candidate_set.jsonl"
)
AFTER_OBSERVED_FIXTURE = Path(
    "tests/fixtures/synthetic/candidate_sets/invalid/local_context_after_observed_candidate_set.jsonl"
)


class CandidateFeatureTests(unittest.TestCase):
    def test_loads_candidate_set_jsonl(self) -> None:
        candidate_sets = load_candidate_sets(FIXTURE)

        self.assertEqual(len(candidate_sets), 1)
        self.assertEqual(
            candidate_sets[0]["candidate_set_id"],
            "synthetic_session_001:micro:3:candidate_set",
        )

    def test_builds_candidate_feature_set(self) -> None:
        feature_set = build_feature_set(candidate_set())

        self.assertEqual(
            feature_set.candidate_feature_set_id,
            "synthetic_session_001:micro:3:candidate_set:features",
        )
        self.assertTrue(feature_set.no_oracle_safe)
        self.assertEqual(
            feature_set.feature_schema_version,
            "candidate_feature_schema_v0_3",
        )
        self.assertEqual(len(feature_set.candidate_features), 3)

    def test_rejects_forbidden_field(self) -> None:
        with self.assertRaises(CandidateFeatureError):
            load_candidate_sets(FORBIDDEN_FIXTURE)

    def test_rejects_local_context_after_observed(self) -> None:
        with self.assertRaises(CandidateFeatureError):
            load_candidate_sets(AFTER_OBSERVED_FIXTURE)

    def test_detects_candidate_using_observed_edit_text(self) -> None:
        data = candidate_set()
        data["candidates"][0]["uses_observed_edit_text"] = True

        feature_set = build_feature_set(data)

        self.assertIn("candidate_uses_observed_edit_text", feature_set.leakage_flags)

    def test_detects_candidate_not_no_oracle_safe(self) -> None:
        data = candidate_set()
        data["candidates"][0]["no_oracle_safe"] = False

        feature_set = build_feature_set(data)

        self.assertIn("candidate_not_no_oracle_safe", feature_set.leakage_flags)

    def test_hold_candidate_feature(self) -> None:
        feature_set = build_feature_set(candidate_set())
        hold = feature_set.candidate_features[0]

        self.assertTrue(hold.is_hold)
        self.assertTrue(hold.is_hold_candidate)
        self.assertEqual(hold.action_family, "hold")
        self.assertEqual(hold.candidate_family_bucket, "hold")
        self.assertFalse(hold.is_placeholder)
        self.assertFalse(hold.is_placeholder_candidate)

    def test_placeholder_action_family(self) -> None:
        feature_set = build_feature_set(candidate_set())
        local_delete = feature_set.candidate_features[1]
        grammar = feature_set.candidate_features[2]

        self.assertEqual(local_delete.action_family, "local_edit")
        self.assertTrue(local_delete.is_local_edit)
        self.assertTrue(local_delete.is_local_edit_family_candidate)
        self.assertEqual(local_delete.candidate_family_bucket, "local_edit")
        self.assertEqual(grammar.action_family, "grammar_placeholder")
        self.assertTrue(grammar.is_grammar_placeholder)
        self.assertTrue(grammar.is_grammar_family_candidate)
        self.assertTrue(grammar.is_placeholder_candidate)

    def test_structural_metadata_features_are_present(self) -> None:
        feature_set = build_feature_set(candidate_set())
        hold = feature_set.candidate_features[0]

        self.assertTrue(hold.candidate_metadata_complete)
        self.assertTrue(hold.has_generation_rule)
        self.assertTrue(hold.has_action_family)
        self.assertFalse(hold.is_safety_relevant_candidate)

    def test_local_pattern_features_are_present(self) -> None:
        feature_set = build_feature_set(candidate_set())
        hold = feature_set.candidate_features[0]

        self.assertEqual(hold.context_before_length_bucket, "medium")
        self.assertFalse(hold.cursor_at_document_start)
        self.assertFalse(hold.cursor_at_document_end_before)
        self.assertFalse(hold.selection_is_collapsed_before)
        self.assertEqual(hold.selection_span_length_bucket, "short")
        self.assertFalse(hold.left_context_ends_with_space)
        self.assertTrue(hold.left_context_ends_with_punctuation)
        self.assertEqual(hold.left_char_class, "punctuation")

    def test_empty_context_has_none_left_char_class(self) -> None:
        feature_set = build_feature_set(candidate_set_with_left_context(""))
        hold = feature_set.candidate_features[0]

        self.assertEqual(hold.context_before_length_bucket, "empty")
        self.assertEqual(hold.left_char_class, "none")

    def test_whitespace_ending_context(self) -> None:
        feature_set = build_feature_set(candidate_set_with_left_context("Synthetic "))
        hold = feature_set.candidate_features[0]

        self.assertTrue(hold.left_context_ends_with_space)
        self.assertEqual(hold.left_char_class, "whitespace")

    def test_punctuation_ending_context(self) -> None:
        feature_set = build_feature_set(candidate_set_with_left_context("Synthetic."))
        hold = feature_set.candidate_features[0]

        self.assertTrue(hold.left_context_ends_with_punctuation)
        self.assertEqual(hold.left_char_class, "punctuation")

    def test_digit_ending_context(self) -> None:
        feature_set = build_feature_set(candidate_set_with_left_context("Synthetic1"))
        hold = feature_set.candidate_features[0]

        self.assertEqual(hold.left_char_class, "digit")

    def test_uppercase_and_lowercase_ending_context(self) -> None:
        uppercase = build_feature_set(candidate_set_with_left_context("Synthetic A"))
        lowercase = build_feature_set(candidate_set_with_left_context("Synthetic a"))

        self.assertEqual(
            uppercase.candidate_features[0].left_char_class,
            "uppercase_letter",
        )
        self.assertEqual(
            lowercase.candidate_features[0].left_char_class,
            "lowercase_letter",
        )

    def test_unicode_ime_smoke_context(self) -> None:
        feature_set = build_feature_set(candidate_set_with_left_context("Synthetic あ"))
        hold = feature_set.candidate_features[0]

        self.assertEqual(hold.left_char_class, "other_letter")

    def test_selection_collapsed_and_cursor_boundaries(self) -> None:
        data = candidate_set()
        data["selection_start_before"] = 0
        data["selection_end_before"] = 0
        data["cursor_pos_before"] = 0

        feature_set = build_feature_set(data)
        hold = feature_set.candidate_features[0]

        self.assertTrue(hold.selection_is_collapsed_before)
        self.assertEqual(hold.selection_span_length_bucket, "collapsed")
        self.assertTrue(hold.cursor_at_document_start)

        data["cursor_pos_before"] = data["doc_len_before"]
        feature_set = build_feature_set(data)

        self.assertTrue(feature_set.candidate_features[0].cursor_at_document_end_before)

    def test_safety_relevant_candidate_feature_is_structural(self) -> None:
        data = candidate_set()
        data["candidates"][0]["uses_observed_edit_text"] = True

        feature_set = build_feature_set(data)
        hold = feature_set.candidate_features[0]

        self.assertTrue(hold.is_safety_relevant_candidate)

    def test_cli_output_excludes_text_fragments(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "candidate_features.jsonl"

            summary = run(FIXTURE, output)

            self.assertIn("candidate_features: ok", summary)
            output_text = output.read_text(encoding="utf-8")
            self.assertNotIn("Synthetic candidate description", output_text)
            self.assertNotIn("proposed_edit", output_text)
            rows = [json.loads(line) for line in output_text.splitlines()]
            self.assertIn("candidate_features", rows[0])
            first_feature = rows[0]["candidate_features"][0]
            self.assertIn("candidate_metadata_complete", first_feature)
            self.assertIn("candidate_family_bucket", first_feature)
            self.assertIn("context_before_length_bucket", first_feature)
            self.assertIn("left_char_class", first_feature)
            self.assertNotIn("local_context_before", first_feature)
            self.assertNotIn("Synthetic local context.", output_text)

    def test_source_does_not_use_eval_exec_or_pickle(self) -> None:
        source_dir = Path("python/ot_scorer")
        source_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in source_dir.glob("*.py")
        )

        self.assertNotIn("eval(", source_text)
        self.assertNotIn("exec(", source_text)
        self.assertNotIn("pickle", source_text)


def candidate_set() -> dict[str, object]:
    return {
        "candidate_set_id": "synthetic_session_001:micro:3:candidate_set",
        "episode_id": "synthetic_session_001:micro:3",
        "source_revision_event_id": "synthetic_session_001:3",
        "local_context_before": {
            "text": "Synthetic local context.",
            "anchor": 10,
            "window_start": 0,
            "window_end": 24,
            "window_size": 30,
        },
        "cursor_pos_before": 10,
        "doc_len_before": 24,
        "selection_start_before": 9,
        "selection_end_before": 10,
        "no_oracle_safe": True,
        "uses_observed_edit_text": False,
        "observed_edit_text_policy": "ignored_by_default",
        "policy_warnings": [],
        "candidates": [
            {
                "candidate_id": "synthetic_session_001:micro:3:cand:01:hold",
                "episode_id": "synthetic_session_001:micro:3",
                "action_type": "hold",
                "description": "Synthetic candidate description for hold.",
                "proposed_edit": {
                    "operation": "hold",
                    "placeholder": True,
                    "target": "local_context_before",
                },
                "uses_observed_edit_text": False,
                "no_oracle_safe": True,
                "generation_rule": "always_include_hold",
                "feature_notes": ["baseline candidate"],
            },
            {
                "candidate_id": "synthetic_session_001:micro:3:cand:02:local_delete_placeholder",
                "episode_id": "synthetic_session_001:micro:3",
                "action_type": "local_delete_placeholder",
                "description": "Synthetic candidate description for local deletion.",
                "proposed_edit": {
                    "operation": "delete_placeholder",
                    "placeholder": True,
                    "target": "local_context_before",
                },
                "uses_observed_edit_text": False,
                "no_oracle_safe": True,
                "generation_rule": "revision_kind_delete_like",
                "feature_notes": ["does not use deleted text"],
            },
            {
                "candidate_id": "synthetic_session_001:micro:3:cand:03:article_fix_placeholder",
                "episode_id": "synthetic_session_001:micro:3",
                "action_type": "article_fix_placeholder",
                "description": "Synthetic candidate description for article check.",
                "proposed_edit": {
                    "operation": "grammar_placeholder",
                    "placeholder": True,
                    "target": "local_context_before",
                },
                "uses_observed_edit_text": False,
                "no_oracle_safe": True,
                "generation_rule": "article_placeholder_rule",
                "feature_notes": ["placeholder only"],
            },
        ],
    }


def candidate_set_with_left_context(text: str) -> dict[str, object]:
    data = candidate_set()
    local_context_before = data["local_context_before"]
    assert isinstance(local_context_before, dict)
    local_context_before["text"] = text
    return data


if __name__ == "__main__":
    unittest.main()
