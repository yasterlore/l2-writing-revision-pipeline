"""CLI for building CandidateFeatureSet JSONL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from ot_scorer.feature_builder import build_feature_sets
from ot_scorer.loader import CandidateFeatureError, load_candidate_sets


def run(input_path: str | Path, output_path: str | Path) -> str:
    candidate_sets = load_candidate_sets(input_path)
    feature_sets = build_feature_sets(candidate_sets)
    output = Path(output_path)
    if output.parent != Path("."):
        output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as handle:
        for feature_set in feature_sets:
            handle.write(json.dumps(feature_set.to_json_dict(), ensure_ascii=False))
            handle.write("\n")

    leakage_issue_count = sum(len(feature_set.leakage_flags) for feature_set in feature_sets)
    return (
        "candidate_features: ok\n"
        f"candidate_sets: {len(candidate_sets)}\n"
        f"feature_sets: {len(feature_sets)}\n"
        f"leakage_issue_count: {leakage_issue_count}\n"
        f"output_path: {output}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build no-oracle structural candidate features."
    )
    parser.add_argument("--input", required=True, help="Input CandidateSet JSONL")
    parser.add_argument("--output", required=True, help="Output CandidateFeatureSet JSONL")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        print(run(args.input, args.output))
    except CandidateFeatureError as error:
        parser.exit(status=2, message=f"candidate feature extraction failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
