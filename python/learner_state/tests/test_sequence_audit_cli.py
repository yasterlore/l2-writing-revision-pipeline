from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path("tests/fixtures/learner_state_sequence_audit")
VALID_CASE = FIXTURE_ROOT / "valid" / "minimal"
INVALID_CASE = FIXTURE_ROOT / "invalid" / "forbidden_field" / "final_text"


class LearnerStateSequenceAuditCliTests(unittest.TestCase):
    def test_dataset_mode_valid_fixture_exits_zero(self) -> None:
        result = run_cli(
            "--features",
            str(VALID_CASE / "features.jsonl"),
            "--labels",
            str(VALID_CASE / "labels.jsonl"),
            "--manifest",
            str(VALID_CASE / "manifest.json"),
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("audit_status=pass", result.stdout)
        assert_cli_output_is_safe(self, result)

    def test_dataset_mode_invalid_fixture_exits_one(self) -> None:
        result = run_cli(
            "--features",
            str(INVALID_CASE / "features.jsonl"),
            "--labels",
            str(INVALID_CASE / "labels.jsonl"),
            "--manifest",
            str(INVALID_CASE / "manifest.json"),
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("audit_status=fail", result.stdout)
        self.assertIn("forbidden_field", result.stdout)
        assert_cli_output_is_safe(self, result)

    def test_fixture_case_valid_exits_zero(self) -> None:
        result = run_cli("--fixture-case", str(VALID_CASE))

        self.assertEqual(result.returncode, 0)
        self.assertIn("match_status=matched", result.stdout)
        assert_cli_output_is_safe(self, result)

    def test_fixture_case_invalid_expected_fail_exits_zero(self) -> None:
        result = run_cli("--fixture-case", str(INVALID_CASE))

        self.assertEqual(result.returncode, 0)
        self.assertIn("match_status=matched", result.stdout)
        self.assertIn("forbidden_field", result.stdout)
        assert_cli_output_is_safe(self, result)

    def test_fixture_root_exits_zero_and_covers_fixture_cases(self) -> None:
        result = run_cli("--fixture-root", str(FIXTURE_ROOT))

        self.assertEqual(result.returncode, 0)
        self.assertIn("audit_status=pass", result.stdout)
        self.assertIn("mismatched_cases=0", result.stdout)
        total_line = next(
            line for line in result.stdout.splitlines() if line.startswith("total_cases=")
        )
        self.assertGreaterEqual(int(total_line.split("=", 1)[1]), 9)
        assert_cli_output_is_safe(self, result)

    def test_fixture_root_json_output_is_parseable_and_safe(self) -> None:
        result = run_cli("--fixture-root", str(FIXTURE_ROOT), "--json")

        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["audit_status"], "pass")
        self.assertGreaterEqual(data["total_cases"], 9)
        self.assertTrue(data["content_suppressed"])
        self.assertTrue(data["no_raw_rows"])
        assert_cli_output_is_safe(self, result)

    def test_dataset_mode_json_output_is_parseable_and_safe(self) -> None:
        result = run_cli(
            "--features",
            str(VALID_CASE / "features.jsonl"),
            "--labels",
            str(VALID_CASE / "labels.jsonl"),
            "--manifest",
            str(VALID_CASE / "manifest.json"),
            "--json",
        )

        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["audit_status"], "pass")
        self.assertEqual(data["violation_count"], 0)
        self.assertTrue(data["content_suppressed"])
        self.assertTrue(data["no_raw_rows"])
        assert_cli_output_is_safe(self, result)

    def test_missing_required_args_exit_nonzero(self) -> None:
        result = run_cli("--features", str(VALID_CASE / "features.jsonl"))

        self.assertNotEqual(result.returncode, 0)
        assert_cli_output_is_safe(self, result)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        "python" if not existing_pythonpath else f"python{os.pathsep}{existing_pythonpath}"
    )
    return subprocess.run(
        [sys.executable, "-m", "learner_state.sequence_audit", *args],
        check=False,
        text=True,
        capture_output=True,
        env=env,
    )


def assert_cli_output_is_safe(
    test_case: unittest.TestCase,
    result: subprocess.CompletedProcess[str],
) -> None:
    output = result.stdout + result.stderr
    forbidden_fragments = [
        "synthetic forbidden fixture value",
        "real_data/example/features.jsonl",
        "expected_action\":\"",
        "final_text\":\"",
        "next_episode_action\":\"",
        "/Users/",
        "/home/",
    ]
    assert_no_forbidden_fragments(test_case, output, forbidden_fragments)


if __name__ == "__main__":
    unittest.main()
