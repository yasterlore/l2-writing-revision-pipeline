from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from test_support.safe_output_scan import (
    assert_no_forbidden_fragments,
    normalize_environment_paths_for_scan,
)


class SafeOutputScanTests(unittest.TestCase):
    def test_temp_path_with_forbidden_looking_substring_is_normalized(self) -> None:
        temp_path = Path(tempfile.gettempdir()) / "contains_f1_segment" / "scores.jsonl"
        output = f"status=fail\noutput_path={temp_path}\ncontent_suppressed=true"

        normalized = normalize_environment_paths_for_scan(output)

        self.assertIn("<TMP_PATH>", normalized)
        self.assertNotIn("contains_f1_segment", normalized)
        assert_no_forbidden_fragments(
            self,
            output,
            ["f1"],
            normalize_paths=True,
        )

    def test_forbidden_body_term_still_fails_after_path_normalization(self) -> None:
        output = "status=fail\nsafe_error=f1 metric appeared in body"

        with self.assertRaises(AssertionError):
            assert_no_forbidden_fragments(
                self,
                output.lower(),
                ["f1"],
                normalize_paths=True,
            )

    def test_project_controlled_relative_output_name_is_not_ignored(self) -> None:
        output = "output_path=tmp/synthetic_e2e/f1_report.jsonl"

        with self.assertRaises(AssertionError):
            assert_no_forbidden_fragments(
                self,
                output.lower(),
                ["f1_report"],
                normalize_paths=True,
            )

    def test_project_root_prefix_keeps_project_controlled_basename_visible(self) -> None:
        project_path = Path.cwd() / "tmp" / "synthetic_e2e" / "f1_report.jsonl"

        normalized = normalize_environment_paths_for_scan(str(project_path))

        self.assertIn("<PROJECT_ROOT>", normalized)
        self.assertIn("f1_report.jsonl", normalized)


if __name__ == "__main__":
    unittest.main()
