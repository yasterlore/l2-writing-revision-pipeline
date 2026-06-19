"""Command line entry point for candidate generation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from candidate_generation.generator import generate_candidate_sets
from candidate_generation.loader import CandidateGenerationError, load_safe_episode_views


def run(input_path: str | Path, output_path: str | Path) -> str:
    episodes = load_safe_episode_views(input_path)
    candidate_sets = generate_candidate_sets(episodes)
    output = Path(output_path)
    if output.parent != Path("."):
        output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as handle:
        for candidate_set in candidate_sets:
            handle.write(json.dumps(candidate_set.to_json_dict(), ensure_ascii=False))
            handle.write("\n")

    return (
        "candidate_generation: ok\n"
        f"episodes: {len(episodes)}\n"
        f"candidate_sets: {len(candidate_sets)}\n"
        "uses_observed_edit_text: false\n"
        f"output_path: {output}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate no-oracle placeholder candidates from safe-view JSONL."
    )
    parser.add_argument("--input", required=True, help="Input NoOracleSafeEpisodeView JSONL")
    parser.add_argument("--output", required=True, help="Output CandidateSet JSONL")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        print(run(args.input, args.output))
    except CandidateGenerationError as error:
        parser.exit(status=2, message=f"candidate generation failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
