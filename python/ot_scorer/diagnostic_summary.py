"""Count-only diagnostic summaries for ConstraintViolationSet JSONL."""

from __future__ import annotations

from collections import Counter
from typing import Any

from ot_scorer.violation_set_loader import load_constraint_violation_sets

SAFETY_CONSTRAINT_IDS: frozenset[str] = frozenset(
    {
        "NO-LEAKAGE-FLAG",
        "NO-OBSERVED-EDIT-TEXT",
        "NO-UNSAFE-CANDIDATE",
    }
)

LOCAL_PATTERN_PREFIXES: tuple[str, ...] = (
    "CONTEXT-BEFORE-",
    "CURSOR-AT-",
    "SELECTION-",
    "LEFT-CONTEXT-ENDS-",
    "LEFT-CHAR-CLASS-",
)

LINGUISTIC_PLACEHOLDER_CONSTRAINT_IDS: frozenset[str] = frozenset(
    {
        "ARTICLE-PLACEHOLDER-CANDIDATE",
        "NUMBER-PLACEHOLDER-CANDIDATE",
        "SVA-PLACEHOLDER-CANDIDATE",
        "TENSE-PLACEHOLDER-CANDIDATE",
        "PREPOSITION-PLACEHOLDER-CANDIDATE",
        "PUNCTUATION-PLACEHOLDER-CANDIDATE",
    }
)

NON_LEAKY_LINGUISTIC_CONSTRAINT_IDS: frozenset[str] = frozenset(
    {
        "ARTICLE-CANDIDATE-LOCAL-CONTEXT-AVAILABLE",
        "NUMBER-CANDIDATE-LOCAL-CONTEXT-AVAILABLE",
        "SVA-CANDIDATE-LOCAL-CONTEXT-AVAILABLE",
        "TENSE-CANDIDATE-LOCAL-CONTEXT-AVAILABLE",
        "PREPOSITION-CANDIDATE-LOCAL-CONTEXT-AVAILABLE",
        "PUNCTUATION-CANDIDATE-LEFT-PUNCTUATION-AWARE",
        "PUNCTUATION-CANDIDATE-LEFT-SPACE-AWARE",
        "GRAMMAR-CANDIDATE-LEFT-CHAR-CLASS-RECORDED",
        "GRAMMAR-CANDIDATE-SELECTION-CONTEXT-RECORDED",
    }
)


def summarize_constraint_violation_file(path: str) -> dict[str, Any]:
    return summarize_constraint_violation_sets(load_constraint_violation_sets(path))


def summarize_constraint_violation_sets(
    violation_sets: list[dict[str, Any]],
) -> dict[str, Any]:
    constraint_id_counts: Counter[str] = Counter()
    constraint_type_counts: Counter[str] = Counter()
    severity_counts: Counter[str] = Counter()
    action_type_counts: Counter[str] = Counter()
    generation_rule_counts: Counter[str] = Counter()
    action_family_counts: Counter[str] = Counter()
    candidate_family_bucket_counts: Counter[str] = Counter()
    local_pattern_constraint_counts: Counter[str] = Counter()
    linguistic_placeholder_constraint_counts: Counter[str] = Counter()
    non_leaky_linguistic_constraint_counts: Counter[str] = Counter()

    total_candidates = 0
    total_constraints = 0
    descriptive_constraint_count = 0
    blocking_constraint_count = 0
    safety_constraint_count = 0
    diagnostic_constraint_count = 0

    for violation_set in violation_sets:
        for candidate in violation_set["candidate_violations"]:
            total_candidates += 1
            action_type_counts.update([str(candidate["action_type"])])
            generation_rule_counts.update([str(candidate["generation_rule"])])
            action_family_counts.update([str(candidate["action_family"])])
            if "candidate_family_bucket" in candidate:
                candidate_family_bucket_counts.update(
                    [str(candidate["candidate_family_bucket"])]
                )

            for violation in candidate["violations"]:
                total_constraints += 1
                constraint_id = str(violation["constraint_id"])
                constraint_type = str(violation["constraint_type"])
                severity = str(violation["severity"])
                observed = violation.get("observed") is True
                constraint_type_counts.update([constraint_type])
                severity_counts.update([severity])
                if constraint_type == "descriptive":
                    descriptive_constraint_count += 1
                if severity == "blocking":
                    blocking_constraint_count += 1
                if constraint_id in SAFETY_CONSTRAINT_IDS:
                    safety_constraint_count += 1
                if is_local_pattern_constraint(constraint_id):
                    diagnostic_constraint_count += 1
                if observed:
                    constraint_id_counts.update([constraint_id])
                    if is_local_pattern_constraint(constraint_id):
                        local_pattern_constraint_counts.update([constraint_id])
                    if constraint_id in LINGUISTIC_PLACEHOLDER_CONSTRAINT_IDS:
                        linguistic_placeholder_constraint_counts.update(
                            [constraint_id]
                        )
                    if constraint_id in NON_LEAKY_LINGUISTIC_CONSTRAINT_IDS:
                        non_leaky_linguistic_constraint_counts.update(
                            [constraint_id]
                        )

    return {
        "diagnostic_summary_schema_version": "diagnostic_summary_schema_v0_1",
        "summary_kind": "constraint_diagnostic_counts",
        "content_suppressed": True,
        "performance_metrics_included": False,
        "total_constraint_sets": len(violation_sets),
        "total_candidates": total_candidates,
        "total_constraints": total_constraints,
        "descriptive_constraint_count": descriptive_constraint_count,
        "blocking_constraint_count": blocking_constraint_count,
        "safety_constraint_count": safety_constraint_count,
        "diagnostic_constraint_count": diagnostic_constraint_count,
        "constraint_id_counts": sorted_dict(constraint_id_counts),
        "constraint_type_counts": sorted_dict(constraint_type_counts),
        "severity_counts": sorted_dict(severity_counts),
        "action_type_counts": sorted_dict(action_type_counts),
        "generation_rule_counts": sorted_dict(generation_rule_counts),
        "action_family_counts": sorted_dict(action_family_counts),
        "candidate_family_bucket_counts": sorted_dict(candidate_family_bucket_counts),
        "local_pattern_constraint_counts": sorted_dict(
            local_pattern_constraint_counts
        ),
        "linguistic_placeholder_constraint_counts": sorted_dict(
            linguistic_placeholder_constraint_counts
        ),
        "non_leaky_linguistic_constraint_counts": sorted_dict(
            non_leaky_linguistic_constraint_counts
        ),
        "top_constraint_ids": top_counts(constraint_id_counts),
    }


def is_local_pattern_constraint(constraint_id: str) -> bool:
    return constraint_id.startswith(LOCAL_PATTERN_PREFIXES)


def sorted_dict(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted(counter.items()))


def top_counts(counter: Counter[str], limit: int = 20) -> list[dict[str, int | str]]:
    return [
        {"constraint_id": constraint_id, "count": count}
        for constraint_id, count in counter.most_common(limit)
    ]
