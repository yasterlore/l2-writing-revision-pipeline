"""CLI for weighted OT scorer prototype."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from ot_scorer.loader import CandidateFeatureError
from ot_scorer.scorer import build_candidate_score_sets
from ot_scorer.violation_set_loader import load_constraint_violation_sets


def run(input_path: str | Path, output_path: str | Path) -> str:
    violation_sets = load_constraint_violation_sets(input_path)
    score_sets = build_candidate_score_sets(violation_sets)
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
    return (
        "candidate_scores: ok\n"
        f"violation_sets: {len(violation_sets)}\n"
        f"score_sets: {len(score_sets)}\n"
        f"blocked_candidates: {blocked_count}\n"
        "evaluation: not_implemented\n"
        "calibration: not_implemented\n"
        f"output_path: {output}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Score candidates with the weighted OT prototype policy."
    )
    parser.add_argument("--input", required=True, help="Input ConstraintViolationSet JSONL")
    parser.add_argument("--output", required=True, help="Output CandidateScoreSet JSONL")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        print(run(args.input, args.output))
    except CandidateFeatureError as error:
        parser.exit(status=2, message=f"candidate scoring failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
