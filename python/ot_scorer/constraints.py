"""CLI for building OT-style constraint violation JSONL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from ot_scorer.constraint_builder import build_constraint_violation_sets
from ot_scorer.feature_set_loader import load_candidate_feature_sets
from ot_scorer.loader import CandidateFeatureError


def run(input_path: str | Path, output_path: str | Path) -> str:
    feature_sets = load_candidate_feature_sets(input_path)
    violation_sets = build_constraint_violation_sets(feature_sets)
    output = Path(output_path)
    if output.parent != Path("."):
        output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as handle:
        for violation_set in violation_sets:
            handle.write(json.dumps(violation_set.to_json_dict(), ensure_ascii=False))
            handle.write("\n")

    penalty_violation_count = sum(
        violation.violation_count
        for violation_set in violation_sets
        for candidate_violations in violation_set.candidate_violations
        for violation in candidate_violations.violations
        if violation.constraint_type == "penalty"
    )
    return (
        "constraint_violations: ok\n"
        f"feature_sets: {len(feature_sets)}\n"
        f"violation_sets: {len(violation_sets)}\n"
        f"penalty_violation_count: {penalty_violation_count}\n"
        "weighted_scoring: not_implemented\n"
        "ranking: not_implemented\n"
        f"output_path: {output}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build unweighted OT-style constraint violation records."
    )
    parser.add_argument("--input", required=True, help="Input CandidateFeatureSet JSONL")
    parser.add_argument("--output", required=True, help="Output ConstraintViolationSet JSONL")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        print(run(args.input, args.output))
    except CandidateFeatureError as error:
        parser.exit(status=2, message=f"constraint generation failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
