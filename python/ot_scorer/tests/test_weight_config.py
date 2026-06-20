from __future__ import annotations

import copy
import json
import math
import subprocess
import sys
import unittest
from pathlib import Path

from ot_scorer.scorer import build_candidate_score_set
from ot_scorer.violation_set_loader import load_constraint_violation_sets
from ot_scorer.weight_config import (
    CONFIG_SCHEMA_VERSION,
    HandWeightConfig,
    WeightConfigError,
    load_hand_weight_config,
    parse_hand_weight_config,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

VALID_CONFIG = Path(
    "tests/fixtures/synthetic/hand_weight_configs/valid/current_default_like_config.json"
)
VALID_CONFIG_DIR = Path("tests/fixtures/synthetic/hand_weight_configs/valid")
INVALID_DIR = Path("tests/fixtures/synthetic/hand_weight_configs/invalid")
CONSTRAINT_FIXTURE = Path(
    "tests/fixtures/synthetic/constraint_violations/valid/deletion_constraint_violations.jsonl"
)


class HandWeightConfigTests(unittest.TestCase):
    def test_valid_config_loads(self) -> None:
        config = load_hand_weight_config(VALID_CONFIG)

        self.assertIsInstance(config, HandWeightConfig)
        self.assertEqual(config.config_schema_version, CONFIG_SCHEMA_VERSION)
        self.assertEqual(config.config_name, "synthetic_current_default_like")
        self.assertEqual(len(config.constraint_weights), 3)
        self.assertEqual(
            [entry.constraint_id for entry in config.constraint_weights],
            [
                "NO-LEAKAGE-FLAG",
                "NO-OBSERVED-EDIT-TEXT",
                "NO-UNSAFE-CANDIDATE",
            ],
        )
        self.assertTrue(all(entry.active for entry in config.constraint_weights))

    def test_all_valid_config_fixtures_load(self) -> None:
        for config_path in sorted(VALID_CONFIG_DIR.glob("*.json")):
            with self.subTest(config_path=config_path.name):
                config = load_hand_weight_config(config_path)
                self.assertEqual(config.config_schema_version, CONFIG_SCHEMA_VERSION)

    def test_forbidden_field_is_rejected(self) -> None:
        self.assert_invalid_fixture("forbidden_field_config.json", "forbidden")

    def test_duplicate_constraint_id_is_rejected(self) -> None:
        self.assert_invalid_fixture("duplicate_constraint_config.json", "duplicate")

    def test_non_finite_weight_fixture_is_rejected(self) -> None:
        self.assert_invalid_fixture("non_finite_weight_config.json", "non-finite")

    def test_nan_and_infinity_weight_are_rejected_from_parsed_config(self) -> None:
        for value in [math.nan, math.inf, -math.inf]:
            with self.subTest(value=value):
                data = valid_config_dict()
                data["constraint_weights"][0]["weight"] = value
                with self.assertRaises(WeightConfigError):
                    parse_hand_weight_config(data)

    def test_active_weight_without_rationale_is_rejected(self) -> None:
        self.assert_invalid_fixture("missing_rationale_config.json", "rationale")

    def test_active_weight_without_no_oracle_reason_is_rejected(self) -> None:
        self.assert_invalid_fixture(
            "missing_no_oracle_safe_reason_config.json",
            "no_oracle_safe_reason",
        )

    def test_unknown_active_constraint_is_rejected(self) -> None:
        self.assert_invalid_fixture(
            "unknown_active_constraint_config.json",
            "unknown",
        )

    def test_private_manual_real_path_string_is_rejected(self) -> None:
        for path_value in [
            "manual_outputs/synthetic_config.json",
            "private_data/synthetic_config.json",
            "real_data/synthetic_config.json",
            "participant_data/synthetic_config.json",
            "synthetic_placeholder.real.jsonl",
            "synthetic_placeholder.private.jsonl",
        ]:
            with self.subTest(path_value=path_value):
                data = valid_config_dict()
                data["rationale"] = f"Synthetic invalid path reference: {path_value}"
                with self.assertRaises(WeightConfigError):
                    parse_hand_weight_config(data)

    def test_missing_synthetic_only_notice_is_rejected(self) -> None:
        self.assert_invalid_fixture(
            "missing_synthetic_notice_config.json",
            "synthetic_only_notice",
        )

    def test_expected_action_usage_policy_that_implies_tuning_is_rejected(self) -> None:
        self.assert_invalid_fixture(
            "expected_action_tuning_policy_config.json",
            "expected_action_usage_policy",
        )

    def test_default_scoring_behavior_is_not_connected_to_config(self) -> None:
        load_hand_weight_config(VALID_CONFIG)
        violation_set = load_constraint_violation_sets(CONSTRAINT_FIXTURE)[0]

        score_set = build_candidate_score_set(violation_set)
        scores = score_set.to_json_dict()["candidate_scores"]

        self.assertEqual([score["rank"] for score in scores], list(range(1, len(scores) + 1)))
        self.assertTrue(all(score["weighted_score"] == 0.0 for score in scores))
        self.assertTrue(all(score["blocked"] is False for score in scores))
        self.assertNotIn("config_schema_version", score_set.to_json_dict())
        self.assertNotIn("constraint_weights", score_set.to_json_dict())

    def test_validate_cli_valid_config_success(self) -> None:
        result = run_validate_cli(VALID_CONFIG)

        self.assertEqual(result.returncode, 0)
        self.assertIn("validation_status=ok", result.stdout)
        self.assertIn("config_schema_version=hand_weight_config_schema_v0_1", result.stdout)
        self.assertIn("config_name=synthetic_current_default_like", result.stdout)
        self.assertIn("constraint_weights_count=3", result.stdout)
        self.assertIn("active_weights_count=3", result.stdout)
        assert_cli_output_is_safe(self, result.stdout + result.stderr)

    def test_validate_cli_invalid_config_failure(self) -> None:
        result = run_validate_cli(INVALID_DIR / "duplicate_constraint_config.json")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("validation_status=fail", result.stdout)
        self.assertIn("safe_error=duplicate constraint_id", result.stdout)
        assert_cli_output_is_safe(self, result.stdout + result.stderr)

    def test_validate_cli_rejects_required_invalid_fixtures(self) -> None:
        expected_errors = {
            "forbidden_field_config.json": "forbidden config field",
            "duplicate_constraint_config.json": "duplicate constraint_id",
            "non_finite_weight_config.json": "non-finite weight",
            "missing_rationale_config.json": "missing rationale",
            "expected_action_tuning_policy_config.json": (
                "unsafe expected_action_usage_policy"
            ),
        }
        for filename, safe_error in expected_errors.items():
            with self.subTest(filename=filename):
                result = run_validate_cli(INVALID_DIR / filename)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("validation_status=fail", result.stdout)
                self.assertIn(f"safe_error={safe_error}", result.stdout)
                assert_cli_output_is_safe(self, result.stdout + result.stderr)

    def assert_invalid_fixture(self, filename: str, expected_fragment: str) -> None:
        with self.assertRaises(WeightConfigError) as context:
            load_hand_weight_config(INVALID_DIR / filename)
        self.assertIn(expected_fragment, str(context.exception))


def valid_config_dict() -> dict[str, object]:
    return copy.deepcopy(json.loads(VALID_CONFIG.read_text(encoding="utf-8")))


def run_validate_cli(config_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "ot_scorer.validate_weight_config",
            "--config",
            str(config_path),
        ],
        check=False,
        cwd=Path.cwd(),
        text=True,
        capture_output=True,
    )


def assert_cli_output_is_safe(
    test_case: unittest.TestCase, combined_output: str
) -> None:
    forbidden_fragments = [
        '"constraint_weights"',
        '"rationale"',
        "final_text",
        "observed_after_text",
        "gold_label",
        "teacher_correction",
        "Synthetic invalid fixture",
        "expected actions may be used",
        "manual_outputs/",
        "private_data/",
        "real_data/",
        "participant_data/",
    ]
    assert_no_forbidden_fragments(
        test_case,
        combined_output,
        forbidden_fragments,
        normalize_paths=True,
    )


if __name__ == "__main__":
    unittest.main()
