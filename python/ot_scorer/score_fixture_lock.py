"""No-config CandidateScoreSet fixture lock helper.

This module compares synthetic CandidateScoreSet JSONL files without printing
their JSONL bodies. It is a regression guard for default scoring behavior, not
performance evaluation.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from ot_scorer.models import FORBIDDEN_INPUT_FIELDS

DEFAULT_EXPECTED = Path(
    "tests/fixtures/synthetic/candidate_scores/valid/deletion_candidate_scores.jsonl"
)
DEFAULT_GENERATED = Path("tmp/synthetic_e2e/deletion_case/candidate_scores.jsonl")
DEFAULT_CASE_NAME = "deletion_case"

UNSAFE_PATH_PARTS: tuple[str, ...] = (
    "manual_outputs/",
    "private_data/",
    "real_data/",
    "participant_data/",
)

DEFAULT_OUTPUT_CONFIG_FIELDS: frozenset[str] = frozenset(
    {
        "config_schema_version",
        "config_name",
        "weight_config",
        "weight_config_path",
        "hand_weight_config",
        "constraint_weights",
    }
)

FORBIDDEN_SCORE_FIELDS: frozenset[str] = frozenset(
    set(FORBIDDEN_INPUT_FIELDS)
    | {
        "local_context_before",
        "raw_local_context_before",
        "raw_text",
        "candidate_description",
        "description",
        "proposed_edit",
        "expected_action",
        "expected_action_type",
        "evaluation_result",
        "exact_match",
        "participant_id",
        "participant_local_id",
    }
)


class ScoreFixtureLockError(Exception):
    """Raised when score fixture lock validation cannot proceed safely."""


@dataclass(frozen=True)
class ScoreFixtureLockReport:
    case_name: str
    lock_status: str
    expected_path: Path
    generated_path: Path
    score_sets_checked: int
    candidates_checked: int
    mismatch_counts: dict[str, int]
    first_mismatch_category: str
    first_mismatch_location: str

    def to_summary_lines(self) -> list[str]:
        mismatch_summary = (
            "none"
            if not self.mismatch_counts
            else ",".join(
                f"{category}:{count}"
                for category, count in sorted(self.mismatch_counts.items())
            )
        )
        return [
            f"case_name={self.case_name}",
            f"lock_status={self.lock_status}",
            f"expected_path={self.expected_path}",
            f"generated_path={self.generated_path}",
            f"score_sets_checked={self.score_sets_checked}",
            f"candidates_checked={self.candidates_checked}",
            f"mismatch_counts={mismatch_summary}",
            f"first_mismatch_category={self.first_mismatch_category}",
            f"first_mismatch_location={self.first_mismatch_location}",
            "content_suppressed=true",
            "performance_evaluation=false",
            "scorer_config_connected=false",
        ]


def run_lock_check(
    expected_path: str | Path = DEFAULT_EXPECTED,
    generated_path: str | Path = DEFAULT_GENERATED,
    *,
    case_name: str = DEFAULT_CASE_NAME,
) -> ScoreFixtureLockReport:
    expected = Path(expected_path)
    generated = Path(generated_path)
    validate_safe_path(expected)
    validate_safe_path(generated)

    expected_rows = load_score_jsonl(expected, label="expected")
    generated_rows = load_score_jsonl(generated, label="generated")

    expected_normalized = normalize_score_sets(expected_rows, label="expected")
    generated_normalized = normalize_score_sets(generated_rows, label="generated")
    return compare_normalized_scores(
        expected_normalized,
        generated_normalized,
        expected_path=expected,
        generated_path=generated,
        case_name=case_name,
    )


def validate_safe_path(path: Path) -> None:
    path_string = path.as_posix()
    if any(part in path_string for part in UNSAFE_PATH_PARTS):
        raise ScoreFixtureLockError("unsafe_path")


def load_score_jsonl(path: Path, *, label: str) -> list[dict[str, Any]]:
    if not path.exists():
        raise ScoreFixtureLockError(f"missing_{label}_file")
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ScoreFixtureLockError(f"malformed_{label}_jsonl") from error
            if not isinstance(row, dict):
                raise ScoreFixtureLockError(f"invalid_{label}_row_type")
            rows.append(row)
    return rows


def normalize_score_sets(
    rows: list[dict[str, Any]], *, label: str
) -> list[dict[str, Any]]:
    normalized = []
    for row_number, row in enumerate(rows, start=1):
        reject_forbidden_output_fields(row, label=label, row_number=row_number)
        normalized.append(normalize_score_set(row, label=label, row_number=row_number))
    return normalized


def reject_forbidden_output_fields(
    value: Any, *, label: str, row_number: int
) -> None:
    forbidden = find_forbidden_field_names(value, FORBIDDEN_SCORE_FIELDS)
    if forbidden:
        raise ScoreFixtureLockError(
            f"forbidden_field:{label}:row:{row_number}:{sorted(forbidden)[0]}"
        )
    config_fields = find_forbidden_field_names(value, DEFAULT_OUTPUT_CONFIG_FIELDS)
    if config_fields:
        raise ScoreFixtureLockError(
            f"default_output_config_field:{label}:row:{row_number}:"
            f"{sorted(config_fields)[0]}"
        )


def find_forbidden_field_names(
    value: Any, forbidden_names: frozenset[str]
) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in forbidden_names:
                found.add(key)
            found.update(find_forbidden_field_names(nested, forbidden_names))
    elif isinstance(value, list):
        for item in value:
            found.update(find_forbidden_field_names(item, forbidden_names))
    return found


def normalize_score_set(
    row: dict[str, Any], *, label: str, row_number: int
) -> dict[str, Any]:
    candidate_scores = require_list(row, "candidate_scores", label, row_number)
    return {
        "line": row_number,
        "candidate_score_set_id": require_field(
            row, "candidate_score_set_id", label, row_number
        ),
        "constraint_violation_set_id": require_field(
            row, "constraint_violation_set_id", label, row_number
        ),
        "candidate_score_schema_version": require_any_field(
            row,
            ("candidate_score_schema_version", "scoring_policy_version"),
            label,
            row_number,
        ),
        "micro_episode_id": require_any_field(
            row, ("micro_episode_id", "episode_id"), label, row_number
        ),
        "top_level_keys": sorted(row.keys()),
        "candidate_scores_count": len(candidate_scores),
        "candidate_scores": [
            normalize_candidate_score(
                candidate,
                label=label,
                row_number=row_number,
                candidate_index=index,
            )
            for index, candidate in enumerate(candidate_scores, start=1)
        ],
    }


def normalize_candidate_score(
    candidate: Any, *, label: str, row_number: int, candidate_index: int
) -> dict[str, Any]:
    if not isinstance(candidate, dict):
        raise ScoreFixtureLockError(
            f"invalid_candidate_score_type:{label}:row:{row_number}:"
            f"candidate:{candidate_index}"
        )
    location = f"{label}:row:{row_number}:candidate:{candidate_index}"
    return {
        "position": candidate_index,
        "candidate_id": require_field_at(candidate, "candidate_id", location),
        "micro_episode_id": require_any_field_at(
            candidate, ("micro_episode_id", "episode_id"), location
        ),
        "action_type": require_field_at(candidate, "action_type", location),
        "generation_rule": require_field_at(candidate, "generation_rule", location),
        "action_family": require_field_at(candidate, "action_family", location),
        "weighted_score": require_field_at(candidate, "weighted_score", location),
        "blocked": require_field_at(candidate, "blocked", location),
        "rank": require_field_at(candidate, "rank", location),
        "blocking_reasons": require_any_field_at(
            candidate, ("blocking_reasons", "block_reasons"), location
        ),
        "candidate_score_keys": sorted(candidate.keys()),
        "constraint_contributions_count": len(
            candidate.get("constraint_contributions", [])
        ),
    }


def require_list(
    row: dict[str, Any], field_name: str, label: str, row_number: int
) -> list[Any]:
    value = require_field(row, field_name, label, row_number)
    if not isinstance(value, list):
        raise ScoreFixtureLockError(
            f"invalid_field_type:{label}:row:{row_number}:{field_name}"
        )
    return value


def require_field(
    row: dict[str, Any], field_name: str, label: str, row_number: int
) -> Any:
    if field_name not in row:
        raise ScoreFixtureLockError(
            f"missing_field:{label}:row:{row_number}:{field_name}"
        )
    return row[field_name]


def require_any_field(
    row: dict[str, Any], field_names: tuple[str, ...], label: str, row_number: int
) -> Any:
    for field_name in field_names:
        if field_name in row:
            return row[field_name]
    joined = "|".join(field_names)
    raise ScoreFixtureLockError(f"missing_field:{label}:row:{row_number}:{joined}")


def require_field_at(row: dict[str, Any], field_name: str, location: str) -> Any:
    if field_name not in row:
        raise ScoreFixtureLockError(f"missing_field:{location}:{field_name}")
    return row[field_name]


def require_any_field_at(
    row: dict[str, Any], field_names: tuple[str, ...], location: str
) -> Any:
    for field_name in field_names:
        if field_name in row:
            return row[field_name]
    joined = "|".join(field_names)
    raise ScoreFixtureLockError(f"missing_field:{location}:{joined}")


def compare_normalized_scores(
    expected: list[dict[str, Any]],
    generated: list[dict[str, Any]],
    *,
    expected_path: Path,
    generated_path: Path,
    case_name: str,
) -> ScoreFixtureLockReport:
    mismatches: list[tuple[str, str]] = []

    if len(expected) != len(generated):
        mismatches.append(("score_set_count_mismatch", "score_sets"))

    for score_set_index, (expected_set, generated_set) in enumerate(
        zip(expected, generated), start=1
    ):
        compare_score_set(
            expected_set,
            generated_set,
            score_set_index=score_set_index,
            mismatches=mismatches,
        )

    mismatch_counts: dict[str, int] = {}
    for category, _location in mismatches:
        mismatch_counts[category] = mismatch_counts.get(category, 0) + 1

    candidates_checked = sum(
        len(score_set["candidate_scores"]) for score_set in generated
    )
    if mismatches:
        first_category, first_location = mismatches[0]
        status = "fail"
    else:
        first_category = "none"
        first_location = "none"
        status = "ok"

    return ScoreFixtureLockReport(
        case_name=case_name,
        lock_status=status,
        expected_path=expected_path,
        generated_path=generated_path,
        score_sets_checked=len(generated),
        candidates_checked=candidates_checked,
        mismatch_counts=mismatch_counts,
        first_mismatch_category=first_category,
        first_mismatch_location=first_location,
    )


def compare_score_set(
    expected: dict[str, Any],
    generated: dict[str, Any],
    *,
    score_set_index: int,
    mismatches: list[tuple[str, str]],
) -> None:
    location = f"score_set:{score_set_index}"
    for field_name in (
        "candidate_score_set_id",
        "constraint_violation_set_id",
        "candidate_score_schema_version",
        "micro_episode_id",
        "top_level_keys",
        "candidate_scores_count",
    ):
        if expected[field_name] != generated[field_name]:
            mismatches.append((category_for_field(field_name), f"{location}:{field_name}"))

    expected_candidates = expected["candidate_scores"]
    generated_candidates = generated["candidate_scores"]
    if len(expected_candidates) != len(generated_candidates):
        mismatches.append(("candidate_count_mismatch", location))

    for index, (expected_candidate, generated_candidate) in enumerate(
        zip(expected_candidates, generated_candidates), start=1
    ):
        compare_candidate_score(
            expected_candidate,
            generated_candidate,
            location=f"{location}:candidate:{index}",
            mismatches=mismatches,
        )


def compare_candidate_score(
    expected: dict[str, Any],
    generated: dict[str, Any],
    *,
    location: str,
    mismatches: list[tuple[str, str]],
) -> None:
    candidate_location = (
        f"{location}:candidate_id:{generated.get('candidate_id', 'unknown')}"
    )
    for field_name in (
        "position",
        "candidate_id",
        "micro_episode_id",
        "action_type",
        "generation_rule",
        "action_family",
        "weighted_score",
        "blocked",
        "rank",
        "blocking_reasons",
        "candidate_score_keys",
        "constraint_contributions_count",
    ):
        if expected[field_name] != generated[field_name]:
            mismatches.append(
                (category_for_field(field_name), f"{candidate_location}:{field_name}")
            )


def category_for_field(field_name: str) -> str:
    if field_name in {"top_level_keys", "candidate_score_keys"}:
        return "schema_mismatch"
    if field_name == "rank" or field_name == "position":
        return "rank_mismatch"
    if field_name == "weighted_score":
        return "weighted_score_mismatch"
    if field_name in {"blocked", "blocking_reasons"}:
        return "blocking_mismatch"
    if field_name == "candidate_scores_count":
        return "candidate_count_mismatch"
    if field_name == "candidate_score_schema_version":
        return "schema_mismatch"
    return "value_mismatch"


def run_summary(
    expected_path: str | Path = DEFAULT_EXPECTED,
    generated_path: str | Path = DEFAULT_GENERATED,
    *,
    case_name: str = DEFAULT_CASE_NAME,
) -> str:
    report = run_lock_check(expected_path, generated_path, case_name=case_name)
    return "\n".join(report.to_summary_lines())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compare no-config CandidateScoreSet JSONL against a synthetic lock "
            "fixture. This is not performance evaluation."
        )
    )
    parser.add_argument(
        "--expected",
        default=str(DEFAULT_EXPECTED),
        help="Expected synthetic CandidateScoreSet JSONL fixture",
    )
    parser.add_argument(
        "--generated",
        default=str(DEFAULT_GENERATED),
        help="Generated no-config CandidateScoreSet JSONL",
    )
    parser.add_argument(
        "--case-name",
        default=DEFAULT_CASE_NAME,
        help="Synthetic case name for safe summary output",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        report = run_lock_check(
            args.expected,
            args.generated,
            case_name=args.case_name,
        )
    except ScoreFixtureLockError as error:
        print(
            "\n".join(
                [
                    f"case_name={args.case_name}",
                    "lock_status=fail",
                    f"expected_path={Path(args.expected)}",
                    f"generated_path={Path(args.generated)}",
                    f"reason={safe_error_reason(str(error))}",
                    "mismatch_counts=not_available",
                    "content_suppressed=true",
                    "performance_evaluation=false",
                    "scorer_config_connected=false",
                ]
            )
        )
        return 2
    print("\n".join(report.to_summary_lines()))
    return 0 if report.lock_status == "ok" else 1


def safe_error_reason(message: str) -> str:
    if message.startswith("forbidden_field"):
        return "forbidden_field"
    if message.startswith("default_output_config_field"):
        return "config_field_in_default_output"
    if message.startswith("missing_field"):
        return "missing_field"
    if message.startswith("missing_expected_file"):
        return "missing_expected_file"
    if message.startswith("missing_generated_file"):
        return "missing_generated_file"
    if message.startswith("malformed_expected_jsonl"):
        return "malformed_expected_jsonl"
    if message.startswith("malformed_generated_jsonl"):
        return "malformed_generated_jsonl"
    if message.startswith("unsafe_path"):
        return "unsafe_path"
    return "score_fixture_lock_error"


if __name__ == "__main__":
    raise SystemExit(main())
