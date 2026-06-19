"""Synthetic expected-action evaluation prototype."""

from __future__ import annotations

from typing import Any

from evaluation.models import EpisodeEvaluation, EvaluationReport, ExpectedAction

REPORT_SCHEMA_VERSION = "evaluation_report_schema_v0_1"


def evaluate_score_sets(
    score_sets: list[dict[str, Any]],
    expected_actions: dict[str, ExpectedAction],
) -> EvaluationReport:
    per_episode = [
        evaluate_episode(score_set, expected_actions.get(str(score_set["episode_id"])))
        for score_set in score_sets
    ]
    episodes_total = len(score_sets)
    episodes_evaluated = sum(
        episode.expected_action_type is not None for episode in per_episode
    )
    episodes_missing_expected = episodes_total - episodes_evaluated
    exact_match_count = sum(episode.exact_match for episode in per_episode)
    expected_found_count = sum(
        episode.expected_found_in_candidates for episode in per_episode
    )
    blocked_expected_count = sum(
        episode.expected_candidate_blocked for episode in per_episode
    )

    return EvaluationReport(
        report_schema_version=REPORT_SCHEMA_VERSION,
        synthetic_only=True,
        episodes_total=episodes_total,
        episodes_evaluated=episodes_evaluated,
        episodes_missing_expected=episodes_missing_expected,
        exact_match_count=exact_match_count,
        exact_match_rate=safe_rate(exact_match_count, episodes_evaluated),
        expected_found_in_candidates_count=expected_found_count,
        expected_found_in_candidates_rate=safe_rate(
            expected_found_count, episodes_evaluated
        ),
        blocked_expected_count=blocked_expected_count,
        per_episode=per_episode,
    )


def evaluate_episode(
    score_set: dict[str, Any], expected: ExpectedAction | None
) -> EpisodeEvaluation:
    episode_id = str(score_set["episode_id"])
    candidates = score_set.get("candidate_scores", [])
    top1 = top_unblocked_candidate(candidates)
    top1_action_type = action_type_from_candidate(top1) if top1 else None
    if expected is None:
        return EpisodeEvaluation(
            episode_id=episode_id,
            expected_action_type=None,
            top1_action_type=top1_action_type,
            exact_match=False,
            expected_found_in_candidates=False,
            expected_rank=None,
            expected_candidate_blocked=False,
            evaluation_notes=["missing synthetic expected action"],
        )

    expected_candidates = [
        candidate
        for candidate in candidates
        if action_type_from_candidate(candidate) == expected.expected_action_type
    ]
    expected_found = bool(expected_candidates)
    expected_candidate_blocked = bool(expected_candidates) and all(
        candidate.get("blocked") is True for candidate in expected_candidates
    )
    expected_rank = min(
        (int(candidate["rank"]) for candidate in expected_candidates),
        default=None,
    )
    exact_match = (
        top1_action_type == expected.expected_action_type
        and not expected_candidate_blocked
    )
    notes = []
    if expected_candidate_blocked:
        notes.append("expected action is present only in blocked candidates")
    if not expected_found:
        notes.append("expected action not found in candidates")
    if not notes:
        notes.append("synthetic expected action compared after scoring")

    return EpisodeEvaluation(
        episode_id=episode_id,
        expected_action_type=expected.expected_action_type,
        top1_action_type=top1_action_type,
        exact_match=exact_match,
        expected_found_in_candidates=expected_found,
        expected_rank=expected_rank,
        expected_candidate_blocked=expected_candidate_blocked,
        evaluation_notes=notes,
    )


def top_unblocked_candidate(candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    unblocked = [
        candidate for candidate in candidates if candidate.get("blocked") is not True
    ]
    if not unblocked:
        return None
    return min(unblocked, key=lambda candidate: int(candidate["rank"]))


def action_type_from_candidate(candidate: dict[str, Any] | None) -> str | None:
    if not candidate:
        return None
    action_type = candidate.get("action_type")
    if action_type is None:
        return None
    return str(action_type)


def safe_rate(count: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return count / denominator
