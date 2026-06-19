"""CLI for count-only diagnostic summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from ot_scorer.diagnostic_summary import summarize_constraint_violation_file
from ot_scorer.loader import CandidateFeatureError


def run(constraints_path: str | Path, output_path: str | Path) -> str:
    summary = summarize_constraint_violation_file(str(constraints_path))
    output = Path(output_path)
    if output.parent != Path("."):
        output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return (
        "diagnostic_summary: ok\n"
        f"constraint_sets: {summary['total_constraint_sets']}\n"
        f"candidates: {summary['total_candidates']}\n"
        f"constraints: {summary['total_constraints']}\n"
        f"diagnostic_constraints: {summary['diagnostic_constraint_count']}\n"
        f"safety_constraints: {summary['safety_constraint_count']}\n"
        "performance_metrics_included: false\n"
        "content_suppressed: true\n"
        f"output_path: {output}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build count-only diagnostic summaries from ConstraintViolationSet JSONL."
    )
    parser.add_argument(
        "--constraints",
        required=True,
        help="Input ConstraintViolationSet JSONL",
    )
    parser.add_argument("--output", required=True, help="Output diagnostic summary JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        print(run(args.constraints, args.output))
    except CandidateFeatureError as error:
        parser.exit(status=2, message=f"diagnostic summary failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
