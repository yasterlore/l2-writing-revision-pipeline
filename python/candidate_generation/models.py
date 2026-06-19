"""Data models for no-oracle candidate generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

ACTION_TYPES: tuple[str, ...] = (
    "hold",
    "local_insert_placeholder",
    "local_delete_placeholder",
    "local_replace_placeholder",
    "article_fix_placeholder",
    "number_fix_placeholder",
    "sva_fix_placeholder",
    "tense_fix_placeholder",
    "preposition_fix_placeholder",
    "punctuation_fix_placeholder",
)

FORBIDDEN_INPUT_FIELDS: frozenset[str] = frozenset(
    {
        "final_text",
        "final_corrected_text",
        "observed_after_text",
        "local_context_after_observed",
        "gold_label",
        "teacher_correction",
        "human_correction",
        "post_hoc_annotation",
        "target_label",
        "answer_key",
        "corrected_sentence",
        "future_edit",
        "future_context",
    }
)


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    episode_id: str
    action_type: str
    description: str
    proposed_edit: dict[str, Any]
    uses_observed_edit_text: bool
    no_oracle_safe: bool
    generation_rule: str
    feature_notes: list[str] = field(default_factory=list)

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CandidateSet:
    candidate_set_id: str
    episode_id: str
    source_revision_event_id: str | None
    no_oracle_safe: bool
    uses_observed_edit_text: bool
    observed_edit_text_policy: str
    policy_warnings: list[str]
    candidates: list[Candidate]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["candidates"] = [candidate.to_json_dict() for candidate in self.candidates]
        return data
