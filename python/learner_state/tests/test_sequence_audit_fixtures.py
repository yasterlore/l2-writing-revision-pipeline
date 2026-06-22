from __future__ import annotations

import json
import unittest
from pathlib import Path

from learner_state.sequence_audit import (
    audit_fixture_case,
    compare_audit_result_to_expected,
    load_expected_audit_result,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path("tests/fixtures/learner_state_sequence_audit")


class LearnerStateSequenceAuditFixtureTests(unittest.TestCase):
    def test_all_fixture_expected_results_match(self) -> None:
        case_dirs = fixture_case_dirs()

        self.assertGreaterEqual(len(case_dirs), 9)
        for case_dir in case_dirs:
            with self.subTest(case=str(case_dir.relative_to(FIXTURE_ROOT))):
                actual = audit_fixture_case(case_dir)
                expected = load_expected_audit_result(case_dir)

                compare_audit_result_to_expected(actual, expected)
                assert_audit_result_is_safe(self, actual.to_dict())

    def test_valid_minimal_fixture_passes(self) -> None:
        case_dir = FIXTURE_ROOT / "valid" / "minimal"

        actual = audit_fixture_case(case_dir)

        self.assertEqual(actual.audit_status, "pass")
        self.assertEqual(actual.violation_count, 0)
        self.assertEqual(actual.reason_codes, [])
        assert_audit_result_is_safe(self, actual.to_dict())

    def test_invalid_fixtures_fail_with_expected_codes(self) -> None:
        invalid_dirs = [
            case_dir
            for case_dir in fixture_case_dirs()
            if "invalid" in case_dir.relative_to(FIXTURE_ROOT).parts
        ]

        self.assertGreaterEqual(len(invalid_dirs), 8)
        for case_dir in invalid_dirs:
            with self.subTest(case=str(case_dir.relative_to(FIXTURE_ROOT))):
                expected = load_expected_audit_result(case_dir)
                actual = audit_fixture_case(case_dir)

                self.assertEqual(actual.audit_status, "fail")
                self.assertIn(expected["expected_failure_code"], actual.reason_codes)
                assert_audit_result_is_safe(self, actual.to_dict())


def fixture_case_dirs() -> list[Path]:
    return sorted(path.parent for path in FIXTURE_ROOT.rglob("expected_audit_result.json"))


def assert_audit_result_is_safe(
    test_case: unittest.TestCase,
    audit_result: dict[str, object],
) -> None:
    result_text = json.dumps(audit_result, sort_keys=True)
    forbidden_fragments = [
        "synthetic forbidden fixture value",
        "real_data/example/features.jsonl",
        "expected_action\":\"",
        "final_text\":\"",
        "next_episode_action\":\"",
        "/Users/",
        "/home/",
    ]
    assert_no_forbidden_fragments(test_case, result_text, forbidden_fragments)


if __name__ == "__main__":
    unittest.main()
