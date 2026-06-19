"""Safe ranking/score diff for explicit config scoring outputs.

This module compares no-config and explicit-config CandidateScoreSet JSONL
without printing JSONL bodies. It is a wiring smoke check, not performance
evaluation.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from ot_scorer.models import FORBIDDEN_INPUT_FIELDS

DEFAULT_NO_CONFIG = Path("tmp/score_cli_no_config/deletion_candidate_scores.jsonl")
DEFAULT_CONFIG = Path(
    "tmp/score_cli_with_default_like_config/deletion_candidate_scores.jsonl"
)
DEFAULT_CASE_NAME = "deletion_case"

UNSAFE_PATH_PARTS: tuple[str, ...] = (
    "manual_outputs/",
    "private_data/",
    "real_data/",
    "participant_data/",
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
        "constraint_weights",
    }
)


class ConfigRankingDiffError(Exception):
    """Raised when score diff validation cannot proceed safely."""


@dataclass(frozen=True)
class ConfigRankingDiffReport:
    case_name: str
    diff_status: str
    no_config_path: Path
    config_path: Path
    score_sets_checked: int
    total_candidates: int
    diff_counts: dict[str, int]
    first_mismatch_category: str
    first_mismatch_id: str

    def to_summary_lines(self) -> list[str]:
        diff_summary = (
            "none"
            if not self.diff_counts
            else ",".join(
                f"{category}:{count}"
                for category, count in sorted(self.diff_counts.items())
            )
        )
        return [
            f"case_name={self.case_name}",
            f"diff_status={self.diff_status}",
            f"no_config_path={self.no_config_path}",
            f"config_path={self.config_path}",
            f"score_sets_checked={self.score_sets_checked}",
            f"total_candidates={self.total_candidates}",
            f"diff_counts={diff_summary}",
            f"first_mismatch_category={self.first_mismatch_category}",
            f"first_mismatch_id={self.first_mismatch_id}",
            "content_suppressed=true",
            "performance_evaluation=false",
        ]


def run_diff(
    no_config_path: str | Path = DEFAULT_NO_CONFIG,
    config_path: str | Path = DEFAULT_CONFIG,
    *,
    case_name: str = DEFAULT_CASE_NAME,
) -> ConfigRankingDiffReport:
    no_config = Path(no_config_path)
    config = Path(config_path)
    validate_safe_path(no_config)
    validate_safe_path(config)

    no_config_rows = normalize_score_sets(
        load_score_jsonl(no_config, label="no_config"), label="no_config"
    )
    config_rows = normalize_score_sets(
        load_score_jsonl(config, label="config"), label="config"
    )
    return compare_score_outputs(
        no_config_rows,
        config_rows,
        no_config_path=no_config,
        config_path=config,
        case_name=case_name,
    )


def validate_safe_path(path: Path) -> None:
    path_string = path.as_posix()
    if any(part in path_string for part in UNSAFE_PATH_PARTS):
        raise ConfigRankingDiffError("unsafe_path")


def load_score_jsonl(path: Path, *, label: str) -> list[dict[str, Any]]:
    if not path.exists():
        raise ConfigRankingDiffError(f"missing_{label}_file")
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ConfigRankingDiffError(f"malformed_{label}_jsonl") from error
            if not isinstance(row, dict):
                raise ConfigRankingDiffError(f"invalid_{label}_row_type")
            rows.append(row)
    return rows


def normalize_score_sets(
    rows: list[dict[str, Any]], *, label: str
) -> list[dict[str, Any]]:
    normalized = []
    for row_number, row in enumerate(rows, start=1):
        reject_forbidden_fields(row, label=label, row_number=row_number)
        normalized.append(normalize_score_set(row, label=label, row_number=row_number))
    return normalized


def reject_forbidden_fields(value: Any, *, label: str, row_number: int) -> None:
    forbidden = find_forbidden_field_names(value, FORBIDDEN_SCORE_FIELDS)
    if forbidden:
        raise ConfigRankingDiffError(
            f"forbidden_field:{label}:row:{row_number}:{sorted(forbidden)[0]}"
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
        "schema_keys": sorted(row.keys()),
        "top_action_type": top_action_type(candidate_scores, label, row_number),
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
        raise ConfigRankingDiffError(
            f"invalid_candidate_score_type:{label}:row:{row_number}:"
            f"candidate:{candidate_index}"
        )
    location = f"{label}:row:{row_number}:candidate:{candidate_index}"
    return {
        "candidate_id": require_field_at(candidate, "candidate_id", location),
        "action_type": require_field_at(candidate, "action_type", location),
        "rank": require_field_at(candidate, "rank", location),
        "weighted_score": require_field_at(candidate, "weighted_score", location),
        "blocked": require_field_at(candidate, "blocked", location),
        "blocking_reasons": require_any_field_at(
            candidate, ("blocking_reasons", "block_reasons"), location
        ),
        "schema_keys": sorted(candidate.keys()),
    }


def top_action_type(candidates: list[Any], label: str, row_number: int) -> str:
    if not candidates:
        return "none"
    first = candidates[0]
    if not isinstance(first, dict):
        raise ConfigRankingDiffError(
            f"invalid_candidate_score_type:{label}:row:{row_number}:candidate:1"
        )
    return str(require_field_at(first, "action_type", f"{label}:row:{row_number}:top"))


def require_list(
    row: dict[str, Any], field_name: str, label: str, row_number: int
) -> list[Any]:
    value = require_field(row, field_name, label, row_number)
    if not isinstance(value, list):
        raise ConfigRankingDiffError(
            f"invalid_field_type:{label}:row:{row_number}:{field_name}"
        )
    return value


def require_field(
    row: dict[str, Any], field_name: str, label: str, row_number: int
) -> Any:
    if field_name not in row:
        raise ConfigRankingDiffError(
            f"missing_field:{label}:row:{row_number}:{field_name}"
        )
    return row[field_name]


def require_field_at(row: dict[str, Any], field_name: str, location: str) -> Any:
    if field_name not in row:
        raise ConfigRankingDiffError(f"missing_field:{location}:{field_name}")
    return row[field_name]


def require_any_field_at(
    row: dict[str, Any], field_names: tuple[str, ...], location: str
) -> Any:
    for field_name in field_names:
        if field_name in row:
            return row[field_name]
    joined = "|".join(field_names)
    raise ConfigRankingDiffError(f"missing_field:{location}:{joined}")


def compare_score_outputs(
    no_config: list[dict[str, Any]],
    config: list[dict[str, Any]],
    *,
    no_config_path: Path,
    config_path: Path,
    case_name: str,
) -> ConfigRankingDiffReport:
    mismatches: list[tuple[str, str]] = []

    if len(no_config) != len(config):
        mismatches.append(("unexpected_candidate_added_or_removed", "score_sets"))

    for score_set_index, (no_config_set, config_set) in enumerate(
        zip(no_config, config), start=1
    ):
        compare_score_set(
            no_config_set,
            config_set,
            score_set_index=score_set_index,
            mismatches=mismatches,
        )

    diff_counts: dict[str, int] = {}
    for category, _location in mismatches:
        diff_counts[category] = diff_counts.get(category, 0) + 1

    total_candidates = sum(len(score_set["candidate_scores"]) for score_set in config)
    if mismatches:
        first_category, first_id = mismatches[0]
    else:
        first_category = "none"
        first_id = "none"

    return ConfigRankingDiffReport(
        case_name=case_name,
        diff_status="ok",
        no_config_path=no_config_path,
        config_path=config_path,
        score_sets_checked=len(config),
        total_candidates=total_candidates,
        diff_counts=diff_counts,
        first_mismatch_category=first_category,
        first_mismatch_id=first_id,
    )


def compare_score_set(
    no_config: dict[str, Any],
    config: dict[str, Any],
    *,
    score_set_index: int,
    mismatches: list[tuple[str, str]],
) -> None:
    location = f"score_set:{score_set_index}"
    if no_config["schema_keys"] != config["schema_keys"]:
        mismatches.append(("schema_changed", location))
    if no_config["top_action_type"] != config["top_action_type"]:
        mismatches.append(("top_candidate_changed", location))
    if candidate_id_order(no_config["candidate_scores"]) != candidate_id_order(
        config["candidate_scores"]
    ):
        mismatches.append(("rank_changed", location))

    no_config_candidates = candidates_by_id(no_config["candidate_scores"])
    config_candidates = candidates_by_id(config["candidate_scores"])
    if set(no_config_candidates) != set(config_candidates):
        mismatches.append(("unexpected_candidate_added_or_removed", location))

    for candidate_id in sorted(set(no_config_candidates) & set(config_candidates)):
        compare_candidate(
            no_config_candidates[candidate_id],
            config_candidates[candidate_id],
            mismatches=mismatches,
        )


def candidates_by_id(candidates: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(candidate["candidate_id"]): candidate for candidate in candidates}


def candidate_id_order(candidates: list[dict[str, Any]]) -> list[str]:
    return [str(candidate["candidate_id"]) for candidate in candidates]


def compare_candidate(
    no_config: dict[str, Any],
    config: dict[str, Any],
    *,
    mismatches: list[tuple[str, str]],
) -> None:
    candidate_id = str(config["candidate_id"])
    if no_config["schema_keys"] != config["schema_keys"]:
        mismatches.append(("schema_changed", candidate_id))
    if no_config["rank"] != config["rank"]:
        mismatches.append(("rank_changed", candidate_id))
    if no_config["weighted_score"] != config["weighted_score"]:
        mismatches.append(("weighted_score_changed", candidate_id))
    if no_config["blocked"] != config["blocked"]:
        mismatches.append(("blocked_status_changed", candidate_id))
    if no_config["blocking_reasons"] != config["blocking_reasons"]:
        mismatches.append(("blocking_reasons_changed", candidate_id))


def run_summary(
    no_config_path: str | Path = DEFAULT_NO_CONFIG,
    config_path: str | Path = DEFAULT_CONFIG,
    *,
    case_name: str = DEFAULT_CASE_NAME,
) -> str:
    return "\n".join(
        run_diff(no_config_path, config_path, case_name=case_name).to_summary_lines()
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compare no-config and explicit-config CandidateScoreSet JSONL. "
            "This is not performance evaluation."
        )
    )
    parser.add_argument("--no-config", default=str(DEFAULT_NO_CONFIG))
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--case-name", default=DEFAULT_CASE_NAME)
    parser.add_argument("--expect-zero-diff", action="store_true")
    parser.add_argument("--expect-weighted-score-diff", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        report = run_diff(
            args.no_config,
            args.config,
            case_name=args.case_name,
        )
    except ConfigRankingDiffError as error:
        print(
            "\n".join(
                [
                    f"case_name={args.case_name}",
                    "diff_status=fail",
                    f"no_config_path={Path(args.no_config)}",
                    f"config_path={Path(args.config)}",
                    f"reason={safe_error_reason(str(error))}",
                    "diff_counts=not_available",
                    "content_suppressed=true",
                    "performance_evaluation=false",
                ]
            )
        )
        return 2

    print("\n".join(report.to_summary_lines()))
    if args.expect_zero_diff and report.diff_counts:
        return 1
    if args.expect_weighted_score_diff and (
        report.diff_counts.get("weighted_score_changed", 0) < 1
    ):
        return 1
    return 0


def safe_error_reason(message: str) -> str:
    if message.startswith("forbidden_field"):
        return "forbidden_field"
    if message.startswith("missing_no_config_file"):
        return "missing_no_config_file"
    if message.startswith("missing_config_file"):
        return "missing_config_file"
    if message.startswith("malformed_no_config_jsonl"):
        return "malformed_no_config_jsonl"
    if message.startswith("malformed_config_jsonl"):
        return "malformed_config_jsonl"
    if message.startswith("missing_field"):
        return "missing_field"
    if message.startswith("unsafe_path"):
        return "unsafe_path"
    return "config_ranking_diff_error"


if __name__ == "__main__":
    raise SystemExit(main())
