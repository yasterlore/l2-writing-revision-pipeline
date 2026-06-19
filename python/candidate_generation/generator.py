"""Placeholder candidate generation from no-oracle-safe episode views."""

from __future__ import annotations

from typing import Any

from candidate_generation.loader import validate_safe_episode_view
from candidate_generation.models import ACTION_TYPES, Candidate, CandidateSet

GRAMMAR_PLACEHOLDERS: tuple[tuple[str, str, str], ...] = (
    (
        "article_fix_placeholder",
        "Consider whether an article-related edit is plausible.",
        "article_placeholder_rule",
    ),
    (
        "number_fix_placeholder",
        "Consider whether a number agreement edit is plausible.",
        "number_placeholder_rule",
    ),
    (
        "sva_fix_placeholder",
        "Consider whether a subject-verb agreement edit is plausible.",
        "sva_placeholder_rule",
    ),
    (
        "tense_fix_placeholder",
        "Consider whether a tense-related edit is plausible.",
        "tense_placeholder_rule",
    ),
    (
        "preposition_fix_placeholder",
        "Consider whether a preposition edit is plausible.",
        "preposition_placeholder_rule",
    ),
    (
        "punctuation_fix_placeholder",
        "Consider whether a punctuation edit is plausible.",
        "punctuation_placeholder_rule",
    ),
)


def generate_candidate_sets(
    episodes: list[dict[str, Any]],
) -> list[CandidateSet]:
    return [generate_candidate_set(episode) for episode in episodes]


def generate_candidate_set(episode: dict[str, Any]) -> CandidateSet:
    """Generate deterministic placeholder candidates for one safe episode."""

    validate_safe_episode_view(episode)
    episode_id = str(episode["episode_id"])
    observed_edit_text_included = episode.get("observed_edit_text_included") is True
    policy_warnings = []
    if observed_edit_text_included:
        policy_warnings.append(
            "observed edit text is present in the input but is ignored by default"
        )

    candidates: list[Candidate] = []
    add_candidate(
        candidates,
        episode_id=episode_id,
        action_type="hold",
        description="Keep a no-change placeholder available.",
        operation="hold",
        generation_rule="always_include_hold",
        feature_notes=["baseline candidate; not a ranking decision"],
    )

    revision_kind = str(episode.get("revision_kind", "Unsupported")).lower()
    if revision_kind in {"insertion", "paste", "compositioncommit"}:
        add_candidate(
            candidates,
            episode_id=episode_id,
            action_type="local_insert_placeholder",
            description="Consider a local insertion-like edit.",
            operation="insert_placeholder",
            generation_rule="revision_kind_insert_like",
            feature_notes=["uses revision_kind and pre-edit position metadata only"],
        )
    if revision_kind in {"deletion", "selectionrangeedit"}:
        add_candidate(
            candidates,
            episode_id=episode_id,
            action_type="local_delete_placeholder",
            description="Consider a local deletion-like edit.",
            operation="delete_placeholder",
            generation_rule="revision_kind_delete_like",
            feature_notes=["does not use deleted_text_observed"],
        )
    if revision_kind in {"replacement", "selectionrangeedit"}:
        add_candidate(
            candidates,
            episode_id=episode_id,
            action_type="local_replace_placeholder",
            description="Consider a local replacement-like edit.",
            operation="replace_placeholder",
            generation_rule="revision_kind_replace_like",
            feature_notes=["does not use inserted_text_observed or deleted_text_observed"],
        )

    if is_non_terminal_local_edit(episode):
        for action_type in (
            "local_insert_placeholder",
            "local_delete_placeholder",
            "local_replace_placeholder",
        ):
            if action_type not in {candidate.action_type for candidate in candidates}:
                add_candidate(
                    candidates,
                    episode_id=episode_id,
                    action_type=action_type,
                    description="Consider a local cursor-position edit.",
                    operation=action_type.replace("_placeholder", ""),
                    generation_rule="non_terminal_cursor_placeholder",
                    feature_notes=["cursor_pos_before < doc_len_before"],
                )

    if episode.get("is_revision_like") is True:
        for action_type, description, rule in GRAMMAR_PLACEHOLDERS:
            add_candidate(
                candidates,
                episode_id=episode_id,
                action_type=action_type,
                description=description,
                operation="grammar_placeholder",
                generation_rule=rule,
                feature_notes=["placeholder only; no correctness label or ranking"],
            )

    unknown_actions = [
        candidate.action_type
        for candidate in candidates
        if candidate.action_type not in ACTION_TYPES
    ]
    if unknown_actions:
        raise AssertionError(f"unknown candidate action type(s): {unknown_actions}")

    return CandidateSet(
        candidate_set_id=f"{episode_id}:candidate_set",
        episode_id=episode_id,
        source_revision_event_id=episode.get("source_revision_event_id"),
        no_oracle_safe=True,
        uses_observed_edit_text=False,
        observed_edit_text_policy="ignored_by_default",
        policy_warnings=policy_warnings,
        candidates=candidates,
    )


def add_candidate(
    candidates: list[Candidate],
    *,
    episode_id: str,
    action_type: str,
    description: str,
    operation: str,
    generation_rule: str,
    feature_notes: list[str],
) -> None:
    index = len(candidates) + 1
    candidates.append(
        Candidate(
            candidate_id=f"{episode_id}:cand:{index:02d}:{action_type}",
            episode_id=episode_id,
            action_type=action_type,
            description=description,
            proposed_edit={
                "operation": operation,
                "placeholder": True,
                "target": "local_context_before",
            },
            uses_observed_edit_text=False,
            no_oracle_safe=True,
            generation_rule=generation_rule,
            feature_notes=feature_notes,
        )
    )


def is_non_terminal_local_edit(episode: dict[str, Any]) -> bool:
    cursor_pos_before = episode.get("cursor_pos_before")
    doc_len_before = episode.get("doc_len_before")
    if not isinstance(cursor_pos_before, int) or not isinstance(doc_len_before, int):
        return False
    return cursor_pos_before < doc_len_before
