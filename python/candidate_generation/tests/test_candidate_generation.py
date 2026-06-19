from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from candidate_generation.generate import run
from candidate_generation.generator import generate_candidate_set
from candidate_generation.loader import CandidateGenerationError, load_safe_episode_views

FIXTURE = Path("tests/fixtures/synthetic/safe_views/valid/deletion_safe_view.jsonl")
FORBIDDEN_FIXTURE = Path(
    "tests/fixtures/synthetic/safe_views/invalid/forbidden_field_safe_view.jsonl"
)
AFTER_OBSERVED_FIXTURE = Path(
    "tests/fixtures/synthetic/safe_views/invalid/local_context_after_observed_safe_view.jsonl"
)


class CandidateGenerationTests(unittest.TestCase):
    def test_loads_safe_view_jsonl(self) -> None:
        episodes = load_safe_episode_views(FIXTURE)

        self.assertEqual(len(episodes), 1)
        self.assertEqual(episodes[0]["episode_id"], "synthetic_session_001:micro:3")

    def test_rejects_forbidden_field(self) -> None:
        episode = safe_episode()
        episode["final_text"] = "synthetic forbidden field value"

        with self.assertRaises(CandidateGenerationError):
            generate_candidate_set(episode)

    def test_rejects_forbidden_field_fixture(self) -> None:
        with self.assertRaises(CandidateGenerationError):
            load_safe_episode_views(FORBIDDEN_FIXTURE)

    def test_rejects_local_context_after_observed(self) -> None:
        episode = safe_episode()
        episode["local_context_after_observed"] = {"text": "synthetic after context"}

        with self.assertRaises(CandidateGenerationError):
            generate_candidate_set(episode)

    def test_rejects_local_context_after_observed_fixture(self) -> None:
        with self.assertRaises(CandidateGenerationError):
            load_safe_episode_views(AFTER_OBSERVED_FIXTURE)

    def test_generates_candidate_set_with_hold_and_no_oracle_flags(self) -> None:
        candidate_set = generate_candidate_set(safe_episode())
        action_types = {candidate.action_type for candidate in candidate_set.candidates}

        self.assertIn("hold", action_types)
        self.assertTrue(candidate_set.no_oracle_safe)
        self.assertFalse(candidate_set.uses_observed_edit_text)
        self.assertTrue(
            all(candidate.no_oracle_safe for candidate in candidate_set.candidates)
        )
        self.assertTrue(
            all(
                not candidate.uses_observed_edit_text
                for candidate in candidate_set.candidates
            )
        )

    def test_observed_edit_text_present_is_ignored_by_default(self) -> None:
        episode = safe_episode()
        episode["observed_edit_text_included"] = True
        episode["inserted_text_observed"] = "synthetic observed insert"
        episode["deleted_text_observed"] = "synthetic observed delete"

        candidate_set = generate_candidate_set(episode)

        self.assertFalse(candidate_set.uses_observed_edit_text)
        self.assertTrue(candidate_set.policy_warnings)
        self.assertTrue(
            all(
                not candidate.uses_observed_edit_text
                for candidate in candidate_set.candidates
            )
        )

    def test_cli_writes_candidate_set_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "candidate_sets.jsonl"

            summary = run(FIXTURE, output)

            self.assertIn("candidate_generation: ok", summary)
            rows = [
                json.loads(line)
                for line in output.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(len(rows), 1)
            self.assertIn("candidates", rows[0])
            self.assertFalse(rows[0]["uses_observed_edit_text"])

    def test_source_does_not_use_eval_exec_or_pickle(self) -> None:
        source_dir = Path("python/candidate_generation")
        source_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in source_dir.glob("*.py")
        )

        self.assertNotIn("eval(", source_text)
        self.assertNotIn("exec(", source_text)
        self.assertNotIn("pickle", source_text)


def safe_episode() -> dict[str, object]:
    return {
        "episode_id": "synthetic_session_001:micro:3",
        "session_id": "synthetic_session_001",
        "task_id": "synthetic_task_001",
        "prompt_id": "synthetic_prompt_001",
        "source_revision_event_id": "synthetic_session_001:3",
        "source_seq": 3,
        "timestamp_ms": 1002,
        "revision_kind": "Deletion",
        "is_revision_like": True,
        "local_context_before": {
            "text": "Synthetic local context.",
            "anchor": 10,
            "window_start": 0,
            "window_end": 24,
            "window_size": 30,
        },
        "cursor_pos_before": 10,
        "span_start": 9,
        "span_end": 10,
        "doc_len_before": 24,
        "quality_flags": [],
        "no_oracle_safe_view": True,
        "post_edit_context_suppressed": True,
        "observed_edit_text_included": False,
    }


if __name__ == "__main__":
    unittest.main()
