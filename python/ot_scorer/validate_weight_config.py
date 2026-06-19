"""CLI for validating hand-weight config JSON without connecting it to scoring."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from ot_scorer.weight_config import (
    HandWeightConfig,
    WeightConfigError,
    load_hand_weight_config,
)


def run(config_path: str | Path) -> str:
    config = load_hand_weight_config(config_path)
    return validation_summary(config, config_path)


def validation_summary(config: HandWeightConfig, config_path: str | Path) -> str:
    active_weights_count = sum(1 for entry in config.constraint_weights if entry.active)
    return "\n".join(
        [
            "validation_status=ok",
            f"config_file={Path(config_path)}",
            f"config_schema_version={config.config_schema_version}",
            f"config_name={config.config_name}",
            f"constraint_weights_count={len(config.constraint_weights)}",
            f"active_weights_count={active_weights_count}",
            f"blocking_constraints_count={len(config.blocking_constraints)}",
            f"score_neutral_constraints_count={len(config.score_neutral_constraints)}",
            "scorer_connected=false",
            "default_scoring_changed=false",
            "content_suppressed=true",
        ]
    )


def safe_error_message(error: WeightConfigError) -> str:
    message = str(error)
    if "forbidden path-like" in message:
        return "forbidden path-like string"
    if "forbidden config field" in message:
        return "forbidden config field"
    if "duplicate constraint_id" in message:
        return "duplicate constraint_id"
    if "non-finite" in message or "finite" in message:
        return "non-finite weight"
    if "rationale" in message:
        return "missing rationale"
    if "no_oracle_safe_reason" in message:
        return "missing no_oracle_safe_reason"
    if "unknown constraint" in message or "unknown constraint_id" in message:
        return "unknown constraint"
    if "synthetic_only_notice" in message:
        return "missing synthetic_only_notice"
    if "expected_action_usage_policy" in message:
        return "unsafe expected_action_usage_policy"
    if "malformed config JSON" in message:
        return "malformed config JSON"
    if "missing required config field" in message:
        return "missing required config field"
    return "config validation failed"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a hand-weight config JSON file without scoring."
    )
    parser.add_argument("--config", required=True, help="Input hand-weight config JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        print(run(args.config))
    except WeightConfigError as error:
        print(
            "\n".join(
                [
                    "validation_status=fail",
                    f"config_file={Path(args.config)}",
                    f"safe_error={safe_error_message(error)}",
                    "scorer_connected=false",
                    "default_scoring_changed=false",
                    "content_suppressed=true",
                ]
            )
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
