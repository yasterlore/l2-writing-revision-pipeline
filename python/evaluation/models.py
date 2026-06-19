"""Dataclasses for synthetic evaluation reports."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

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
        "inserted_text_observed",
        "deleted_text_observed",
    }
)


@dataclass(frozen=True)
class ExpectedAction:
    episode_id: str
    expected_action_type: str
    expected_source: str
    synthetic_only: bool
    notes: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EpisodeEvaluation:
    episode_id: str
    expected_action_type: str | None
    top1_action_type: str | None
    exact_match: bool
    expected_found_in_candidates: bool
    expected_rank: int | None
    expected_candidate_blocked: bool
    evaluation_notes: list[str]

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvaluationReport:
    report_schema_version: str
    synthetic_only: bool
    episodes_total: int
    episodes_evaluated: int
    episodes_missing_expected: int
    exact_match_count: int
    exact_match_rate: float
    expected_found_in_candidates_count: int
    expected_found_in_candidates_rate: float
    blocked_expected_count: int
    per_episode: list[EpisodeEvaluation]

    def to_json_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["per_episode"] = [episode.to_json_dict() for episode in self.per_episode]
        return data
