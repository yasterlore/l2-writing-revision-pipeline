"""CLI for weighted OT scorer prototype."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from ot_scorer.loader import CandidateFeatureError
from ot_scorer.scorer import (
    build_candidate_score_sets,
    score_constraint_violation_set_with_config,
)
from ot_scorer.validate_weight_config import safe_error_message
from ot_scorer.violation_set_loader import load_constraint_violation_sets
from ot_scorer.weight_config import (
    WeightConfigError,
    load_hand_weight_config,
    string_contains_forbidden_path,
)


def run(
    input_path: str | Path,
    output_path: str | Path,
    weight_config_path: str | Path | None = None,
) -> str:
    violation_sets = load_constraint_violation_sets(input_path)
    summary_lines: list[str] = []
    if weight_config_path is None:
        score_sets = build_candidate_score_sets(violation_sets)
    else:
        weight_config = load_explicit_weight_config(weight_config_path)
        score_sets = [
            score_constraint_violation_set_with_config(violation_set, weight_config)
            for violation_set in violation_sets
        ]
        summary_lines.extend(
            [
                "weight_config: used",
                f"weight_config_schema_version: {weight_config.config_schema_version}",
                f"weight_config_name: {weight_config.config_name}",
            ]
        )
    output = Path(output_path)
    if output.parent != Path("."):
        output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as handle:
        for score_set in score_sets:
            handle.write(json.dumps(score_set.to_json_dict(), ensure_ascii=False))
            handle.write("\n")

    blocked_count = sum(
        1
        for score_set in score_sets
        for candidate_score in score_set.candidate_scores
        if candidate_score.blocked
    )
    return "\n".join(
        [
            "candidate_scores: ok",
            f"violation_sets: {len(violation_sets)}",
            f"score_sets: {len(score_sets)}",
            f"blocked_candidates: {blocked_count}",
            *summary_lines,
            "evaluation: not_implemented",
            "calibration: not_implemented",
            f"output_path: {output}",
        ]
    )


def load_explicit_weight_config(path: str | Path):
    if string_contains_forbidden_path(str(path)):
        raise WeightConfigError("unsafe weight config path")
    return load_hand_weight_config(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Score candidates with the weighted OT prototype policy."
    )
    parser.add_argument(
        "--input",
        "--constraints",
        dest="input",
        required=True,
        help="Input ConstraintViolationSet JSONL",
    )
    parser.add_argument("--output", required=True, help="Output CandidateScoreSet JSONL")
    parser.add_argument(
        "--weight-config",
        help="Explicit hand-weight config JSON. Omit to use default scoring.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        print(run(args.input, args.output, args.weight_config))
    except WeightConfigError as error:
        parser.exit(
            status=2,
            message=f"candidate scoring failed: {safe_error_message(error)}\n",
        )
    except CandidateFeatureError as error:
        parser.exit(status=2, message=f"candidate scoring failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
