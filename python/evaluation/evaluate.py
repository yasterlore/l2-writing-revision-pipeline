"""CLI for synthetic expected-action evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from evaluation.evaluator import evaluate_score_sets
from evaluation.loader import EvaluationInputError, load_expected_actions, load_score_sets


def run(scores_path: str | Path, expected_path: str | Path, output_path: str | Path) -> str:
    score_sets = load_score_sets(scores_path)
    expected_actions = load_expected_actions(expected_path)
    report = evaluate_score_sets(score_sets, expected_actions)
    output = Path(output_path)
    if output.parent != Path("."):
        output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report.to_json_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return (
        "evaluation: ok\n"
        f"episodes_total: {report.episodes_total}\n"
        f"episodes_evaluated: {report.episodes_evaluated}\n"
        f"episodes_missing_expected: {report.episodes_missing_expected}\n"
        f"exact_match_count: {report.exact_match_count}\n"
        f"exact_match_rate: {report.exact_match_rate:.6f}\n"
        f"output_path: {output}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate synthetic CandidateScoreSet output against synthetic expected actions."
    )
    parser.add_argument("--scores", required=True, help="Input CandidateScoreSet JSONL")
    parser.add_argument("--expected", required=True, help="Synthetic expected action JSONL")
    parser.add_argument("--output", required=True, help="Output EvaluationReport JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        print(run(args.scores, args.expected, args.output))
    except EvaluationInputError as error:
        parser.exit(status=2, message=f"evaluation failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
