from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import contextlib
import io
from pathlib import Path

from learner_state.frozen_policy_generation_manifest_writer import (
    ArtifactBodyGenerationResultPointer,
    ArtifactWriterResultPointer,
    ManifestWriterRequest,
    build_metadata_only_manifest_result,
    load_artifact_body_generation_result_pointer,
    load_artifact_writer_result_pointer,
    load_manifest_writer_request,
    main,
    run_manifest_writer,
    summarize_manifest_writer_result,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path(
    "tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime"
)
MANIFEST_OUTPUT_ROOT = Path("tmp/frozen_policy_generation_manifest")
VALID_CASES = (
    "metadata_only_minimal_no_file",
    "metadata_only_with_artifact_body_reference",
    "metadata_only_with_release_quality_reference",
    "metadata_only_safe_ids_and_counts",
    "metadata_only_no_artifact_body_available",
)
ZERO_COUNT_FIELDS = (
    "raw_row_count",
    "logits_dump_count",
    "private_path_count",
    "absolute_path_count",
    "artifact_body_payload_count",
    "generated_policy_body_count",
    "manifest_body_count",
    "request_body_count",
    "pointer_body_count",
    "expected_body_count",
    "performance_metric_count",
    "written_file_count",
)
FORBIDDEN_RESULT_KEYS = {
    "manifest_body",
    "manifest_json_body",
    "artifact_body_payload",
    "generated_policy_body",
    "request_body",
    "pointer_body",
    "expected_body",
    "expected_result_body",
    "raw_rows",
    "logits",
    "probabilities",
    "raw_learner_text",
    "final_text",
    "observed_after_text",
    "gold_label",
    "scoring_feedback_payload",
    "real_participant_data",
    "performance_metric_body",
    "performance_metrics",
}
FORBIDDEN_WRITTEN_MANIFEST_KEYS = {
    "manifest_body",
    "manifest_json_body",
    "artifact_body_payload",
    "generated_policy_body",
    "request_body",
    "pointer_body",
    "expected_body",
    "raw_rows",
    "logits",
    "probabilities",
    "private_path",
    "absolute_path",
    "raw_learner_text",
    "final_text",
    "observed_after_text",
    "gold_label",
    "scoring_feedback",
    "scoring_feedback_payload",
    "real_participant_data",
    "performance_metric_body",
}
UNSAFE_STRING_MARKERS = (
    "/Users/",
    "/home/",
    "/private/",
    "/var/folders/",
    "C:\\",
    "real_data/",
    "participant_data/",
    "private_data/",
    "manual_outputs/",
)


class FrozenPolicyGenerationManifestWriterRuntimeTests(unittest.TestCase):
    def tearDown(self) -> None:
        cleanup_manifest_output_root()

    def test_help_exits_zero(self) -> None:
        completed = run_cli("--help")

        self.assertEqual(completed.returncode, 0)
        self.assertIn("frozen policy generation manifest writer", completed.stdout)

    def test_missing_request_returns_usage_error(self) -> None:
        completed = run_cli(
            "--artifact-result",
            str(valid_case("metadata_only_minimal_no_file") / "artifact_writer_result_pointer.json"),
            "--artifact-body-result",
            str(
                valid_case("metadata_only_minimal_no_file")
                / "artifact_body_generation_result_pointer.json"
            ),
        )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("writer_status=usage_error", completed.stdout)
        self.assertIn("reason_codes=missing_request_path", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_missing_artifact_pointer_returns_usage_error(self) -> None:
        completed = run_cli(
            "--request",
            str(valid_case("metadata_only_minimal_no_file") / "manifest_writer_request.json"),
            "--artifact-body-result",
            str(
                valid_case("metadata_only_minimal_no_file")
                / "artifact_body_generation_result_pointer.json"
            ),
        )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("writer_status=usage_error", completed.stdout)
        self.assertIn("missing_artifact_pointer_path", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_missing_artifact_body_pointer_returns_usage_error(self) -> None:
        completed = run_cli(
            "--request",
            str(valid_case("metadata_only_minimal_no_file") / "manifest_writer_request.json"),
            "--artifact-result",
            str(valid_case("metadata_only_minimal_no_file") / "artifact_writer_result_pointer.json"),
        )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("writer_status=usage_error", completed.stdout)
        self.assertIn("missing_artifact_body_pointer_path", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_valid_metadata_only_minimal_no_file_returns_pass(self) -> None:
        result = run_case(valid_case("metadata_only_minimal_no_file"))

        self.assert_pass_result(result)
        self.assertFalse(result.manifest_body_available)
        self.assertFalse(result.manifest_file_written)
        self.assertFalse(result.manifest_output_path_available)
        self.assertTrue(result.runtime_writer_executed)
        self.assertFalse(result.release_quality_ready)

    def test_valid_artifact_body_reference_returns_pass(self) -> None:
        result = run_case(valid_case("metadata_only_with_artifact_body_reference"))

        self.assert_pass_result(result)
        self.assertIsNotNone(result.artifact_body_id)

    def test_valid_release_quality_reference_returns_pass(self) -> None:
        result = run_case(valid_case("metadata_only_with_release_quality_reference"))

        self.assert_pass_result(result)
        self.assertEqual(result.release_quality_reference_count, 1)

    def test_valid_safe_ids_and_counts_returns_pass(self) -> None:
        result = run_case(valid_case("metadata_only_safe_ids_and_counts"))

        self.assert_pass_result(result)
        self.assertIsNotNone(result.manifest_id)
        self.assertIsNotNone(result.artifact_id)
        self.assertEqual(result.release_quality_reference_count, 1)

    def test_artifact_body_unavailable_valid_case_returns_pass(self) -> None:
        result = run_case(valid_case("metadata_only_no_artifact_body_available"))

        self.assert_pass_result(result)
        self.assertFalse(result.manifest_body_available)

    def test_valid_cli_human_and_json_are_body_free(self) -> None:
        case_dir = valid_case("metadata_only_minimal_no_file")
        human = run_case_cli(case_dir)
        json_output = run_case_cli(case_dir, "--json")

        self.assertEqual(human.returncode, 0)
        self.assertIn("mode=manifest_writer", human.stdout)
        self.assertIn("writer_status=pass", human.stdout)
        self.assertEqual(json_output.returncode, 0)
        payload = json.loads(json_output.stdout)
        self.assertEqual(payload["mode"], "manifest_writer")
        self.assertEqual(payload["writer_status"], "pass")
        self.assertFalse(payload["manifest_body_available"])
        self.assertFalse(payload["manifest_file_written"])
        self.assertFalse(payload["manifest_output_path_available"])
        self.assertTrue(payload["runtime_writer_executed"])
        self.assertFalse(payload["release_quality_ready"])
        assert_safe_cli_output(self, human)
        assert_safe_cli_output(self, json_output)

    def test_all_valid_cli_cases_return_pass(self) -> None:
        for case_name in VALID_CASES:
            with self.subTest(case=case_name):
                completed = run_case_cli(valid_case(case_name))
                self.assertEqual(completed.returncode, 0)
                self.assertIn("writer_status=pass", completed.stdout)
                self.assertIn("manifest_file_written=false", completed.stdout)
                assert_safe_cli_output(self, completed)

    def test_summary_has_no_body_payload_or_private_keys(self) -> None:
        for case_name in VALID_CASES:
            with self.subTest(case=case_name):
                summary = summarize_manifest_writer_result(run_case(valid_case(case_name)))
                self.assertFalse(FORBIDDEN_RESULT_KEYS.intersection(collect_keys(summary)))
                self.assertFalse(contains_unsafe_string(summary))
                for field_name in ZERO_COUNT_FIELDS:
                    self.assertEqual(summary["count_summary"][field_name], 0)

    def test_include_manifest_body_true_fails_closed(self) -> None:
        completed = run_mutated_request_cli(
            {"include_manifest_body": True},
        )

        self.assert_fail_closed(completed, "manifest_body_requested")

    def test_allow_manifest_file_writing_true_fails_closed(self) -> None:
        completed = run_mutated_request_cli(
            {"allow_manifest_file_writing": True},
        )

        self.assert_fail_closed(completed, "manifest_file_writing_not_supported")

    def test_manifest_out_present_fails_closed_initially(self) -> None:
        completed = run_mutated_request_cli(
            {"manifest_out": "safe_sentinel_manifest.json"},
        )

        self.assert_fail_closed(completed, "unsafe_manifest_output_path")

    def test_manifest_out_cli_argument_writes_metadata_only_file(self) -> None:
        completed = run_case_cli(
            valid_case("metadata_only_minimal_no_file"),
            "--manifest-out",
            "manifest.json",
        )

        self.assertEqual(completed.returncode, 0)
        self.assertIn("writer_status=pass", completed.stdout)
        self.assertIn("manifest_writer_mode=metadata_only_file", completed.stdout)
        self.assertIn("manifest_file_written=true", completed.stdout)
        self.assertIn("manifest_output_path_available=true", completed.stdout)
        self.assertIn('"written_file_count":1', completed.stdout)
        payload = read_written_manifest("manifest.json")
        assert_metadata_only_written_manifest(self, payload)
        self.assertEqual(payload["manifest_writer_mode"], "metadata_only_file")
        assert_safe_cli_output(self, completed)

    def test_nested_manifest_out_writes_one_metadata_only_file(self) -> None:
        completed = run_case_cli(
            valid_case("metadata_only_minimal_no_file"),
            "--manifest-out",
            "nested/manifest.json",
        )

        self.assertEqual(completed.returncode, 0)
        payload = read_written_manifest("nested/manifest.json")
        assert_metadata_only_written_manifest(self, payload)
        self.assertEqual(count_manifest_output_files(), 1)
        assert_safe_cli_output(self, completed)

    def test_manifest_out_existing_file_without_overwrite_fails(self) -> None:
        write_existing_manifest("manifest.json")

        completed = run_case_cli(
            valid_case("metadata_only_minimal_no_file"),
            "--manifest-out",
            "manifest.json",
        )

        self.assertEqual(completed.returncode, 2)
        self.assertIn("writer_status=usage_error", completed.stdout)
        self.assertIn("output_exists_without_overwrite", completed.stdout)
        self.assertIn("manifest_file_written=false", completed.stdout)
        self.assertEqual(read_written_manifest("manifest.json")["safe_summary"], "existing")
        assert_safe_cli_output(self, completed)

    def test_manifest_out_existing_file_with_overwrite_succeeds(self) -> None:
        write_existing_manifest("manifest.json")

        completed = run_case_cli(
            valid_case("metadata_only_minimal_no_file"),
            "--manifest-out",
            "manifest.json",
            "--allow-overwrite",
        )

        self.assertEqual(completed.returncode, 0)
        payload = read_written_manifest("manifest.json")
        assert_metadata_only_written_manifest(self, payload)
        self.assertEqual(payload["safe_summary"], "metadata_only_manifest_writer_result")
        assert_safe_cli_output(self, completed)

    def test_unsafe_absolute_manifest_out_fails_body_free(self) -> None:
        completed = run_case_cli(
            valid_case("metadata_only_minimal_no_file"),
            "--manifest-out",
            "/ABSOLUTE_MANIFEST_OUTPUT_PATH_SENTINEL/manifest.json",
        )

        self.assert_usage_error(completed, "unsafe_absolute_manifest_output_path")
        self.assertEqual(count_manifest_output_files(), 0)

    def test_parent_traversal_manifest_out_fails_body_free(self) -> None:
        completed = run_case_cli(
            valid_case("metadata_only_minimal_no_file"),
            "--manifest-out",
            "../outside.json",
        )

        self.assert_usage_error(completed, "unsafe_parent_traversal_manifest_output_path")
        self.assertEqual(count_manifest_output_files(), 0)

    def test_outside_root_manifest_out_fails_body_free(self) -> None:
        completed = run_case_cli(
            valid_case("metadata_only_minimal_no_file"),
            "--manifest-out",
            "tmp/other/manifest.json",
        )

        self.assert_usage_error(
            completed,
            "unsafe_manifest_output_path_outside_allowed_root",
        )
        self.assertEqual(count_manifest_output_files(), 0)

    def test_non_json_manifest_out_fails_body_free(self) -> None:
        completed = run_case_cli(
            valid_case("metadata_only_minimal_no_file"),
            "--manifest-out",
            "manifest.txt",
        )

        self.assert_usage_error(completed, "unsafe_manifest_output_path_extension")
        self.assertEqual(count_manifest_output_files(), 0)

    def test_unsafe_filename_manifest_out_fails_body_free(self) -> None:
        completed = run_case_cli(
            valid_case("metadata_only_minimal_no_file"),
            "--manifest-out",
            "unsafe name.json",
        )

        self.assert_usage_error(completed, "unsafe_manifest_output_filename")
        self.assertEqual(count_manifest_output_files(), 0)

    def test_manifest_out_json_summary_is_body_free_and_has_no_absolute_path(self) -> None:
        completed = run_case_cli(
            valid_case("metadata_only_minimal_no_file"),
            "--manifest-out",
            "manifest.json",
            "--json",
        )

        self.assertEqual(completed.returncode, 0)
        summary = json.loads(completed.stdout)
        self.assertTrue(summary["manifest_file_written"])
        self.assertTrue(summary["manifest_output_path_available"])
        self.assertEqual(summary["count_summary"]["written_file_count"], 1)
        self.assertFalse(contains_unsafe_string(summary))
        self.assertNotIn('"writer_version"', completed.stdout)
        payload = read_written_manifest("manifest.json")
        assert_metadata_only_written_manifest(self, payload)
        assert_safe_cli_output(self, completed)

    def test_pointer_include_body_payload_true_fails_closed(self) -> None:
        completed = run_mutated_pointer_cli(
            "artifact_body_generation_result_pointer.json",
            {"include_body_payload": True},
        )

        self.assert_fail_closed(completed, "artifact_body_payload_leakage")

    def test_pointer_include_raw_rows_true_fails_closed(self) -> None:
        completed = run_mutated_pointer_cli(
            "artifact_writer_result_pointer.json",
            {"include_raw_rows": True},
        )

        self.assert_fail_closed(completed, "raw_rows_leakage")

    def test_pointer_include_private_paths_true_fails_closed(self) -> None:
        completed = run_mutated_pointer_cli(
            "artifact_body_generation_result_pointer.json",
            {"include_private_paths": True},
        )

        self.assert_fail_closed(completed, "private_path_leakage")

    def test_missing_synthetic_notice_fails_closed(self) -> None:
        completed = run_mutated_request_cli({"synthetic_notice": False})

        self.assert_fail_closed(completed, "missing_synthetic_notice")

    def test_missing_no_oracle_notice_fails_closed(self) -> None:
        completed = run_mutated_request_cli({"no_oracle_notice": False})

        self.assert_fail_closed(completed, "missing_no_oracle_notice")

    def test_missing_non_proof_notice_fails_closed(self) -> None:
        completed = run_mutated_request_cli({"non_proof_notice": False})

        self.assert_fail_closed(completed, "missing_non_proof_notice")

    def test_malformed_json_returns_input_error_body_free(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            case_dir = copy_case_to_tmp(tmp_dir)
            request_path = case_dir / "manifest_writer_request.json"
            request_path.write_text("{", encoding="utf-8")

            completed = run_case_cli(case_dir)

        self.assertEqual(completed.returncode, 4)
        self.assertIn("writer_status=input_error", completed.stdout)
        self.assertIn("malformed_request", completed.stdout)
        assert_safe_cli_output(self, completed)

    def test_unknown_request_schema_fails_closed(self) -> None:
        completed = run_mutated_request_cli({"schema_version": "unknown_schema_v0"})

        self.assert_fail_closed(completed, "unknown_request_schema_version")

    def test_unknown_pointer_schema_fails_closed(self) -> None:
        completed = run_mutated_pointer_cli(
            "artifact_writer_result_pointer.json",
            {"result_schema_version": "unknown_artifact_writer_result_schema_v0"},
        )

        self.assert_fail_closed(completed, "unknown_artifact_writer_result_schema")

    def test_forbidden_marker_fails_closed_without_echoing_payload(self) -> None:
        completed = run_mutated_request_cli(
            {"raw_learner_text": "synthetic unsafe body marker"},
        )

        self.assert_fail_closed(completed, "raw_learner_text_leakage")
        self.assertNotIn("synthetic unsafe body marker", completed.stdout)
        self.assertNotIn("synthetic unsafe body marker", completed.stderr)

    def test_no_files_written_and_manifest_tmp_residue_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            case_dir = copy_case_to_tmp(tmp_dir)
            before = sorted(path.name for path in case_dir.iterdir())
            completed = run_case_cli(case_dir)
            after = sorted(path.name for path in case_dir.iterdir())

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(before, after)
        manifest_tmp = Path("tmp/frozen_policy_generation_manifest")
        residue_count = (
            sum(1 for path in manifest_tmp.rglob("*") if path.is_file())
            if manifest_tmp.exists()
            else 0
        )
        self.assertEqual(residue_count, 0)
        assert_safe_cli_output(self, completed)

    def test_main_calls_runtime_builder(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            exit_code = main(
                [
                    "--request",
                    str(
                        valid_case("metadata_only_minimal_no_file")
                        / "manifest_writer_request.json"
                    ),
                    "--artifact-result",
                    str(
                        valid_case("metadata_only_minimal_no_file")
                        / "artifact_writer_result_pointer.json"
                    ),
                    "--artifact-body-result",
                    str(
                        valid_case("metadata_only_minimal_no_file")
                        / "artifact_body_generation_result_pointer.json"
                    ),
                ]
            )

        self.assertEqual(exit_code, 0)
        self.assertIn("mode=manifest_writer", buffer.getvalue())

    def assert_pass_result(self, result) -> None:
        self.assertEqual(result.mode, "manifest_writer")
        self.assertEqual(result.writer_status, "pass")
        self.assertEqual(result.manifest_writer_mode, "metadata_only_no_file")
        self.assertEqual(result.reason_codes, [])
        self.assertEqual(result.failed_checks, [])
        self.assertFalse(result.manifest_body_available)
        self.assertFalse(result.manifest_file_written)
        self.assertFalse(result.manifest_output_path_available)
        self.assertTrue(result.runtime_writer_executed)
        self.assertFalse(result.release_quality_ready)
        self.assertTrue(all(result.safety_flags.values()))
        for field_name in ZERO_COUNT_FIELDS:
            self.assertEqual(result.count_summary[field_name], 0)

    def assert_fail_closed(self, completed, reason_code: str) -> None:
        self.assertEqual(completed.returncode, 3)
        self.assertIn("writer_status=fail_closed", completed.stdout)
        self.assertIn(reason_code, completed.stdout)
        self.assertIn("manifest_file_written=false", completed.stdout)
        assert_safe_cli_output(self, completed)

    def assert_usage_error(self, completed, reason_code: str) -> None:
        self.assertEqual(completed.returncode, 2)
        self.assertIn("writer_status=usage_error", completed.stdout)
        self.assertIn(reason_code, completed.stdout)
        self.assertIn("manifest_file_written=false", completed.stdout)
        self.assertIn("manifest_output_path_available=false", completed.stdout)
        assert_safe_cli_output(self, completed)


def valid_case(case_name: str) -> Path:
    return FIXTURE_ROOT / "valid" / case_name


def run_case(case_dir: Path):
    request = load_manifest_writer_request(case_dir / "manifest_writer_request.json")
    artifact_pointer = load_artifact_writer_result_pointer(
        case_dir / "artifact_writer_result_pointer.json"
    )
    artifact_body_pointer = load_artifact_body_generation_result_pointer(
        case_dir / "artifact_body_generation_result_pointer.json"
    )
    assert isinstance(request, ManifestWriterRequest)
    assert isinstance(artifact_pointer, ArtifactWriterResultPointer)
    assert isinstance(artifact_body_pointer, ArtifactBodyGenerationResultPointer)
    return build_metadata_only_manifest_result(
        request,
        artifact_pointer,
        artifact_body_pointer,
    )


def run_case_cli(case_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run_cli(
        "--request",
        str(case_dir / "manifest_writer_request.json"),
        "--artifact-result",
        str(case_dir / "artifact_writer_result_pointer.json"),
        "--artifact-body-result",
        str(case_dir / "artifact_body_generation_result_pointer.json"),
        *args,
    )


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "learner_state.frozen_policy_generation_manifest_writer",
            *args,
        ],
        check=False,
        cwd=Path.cwd(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_mutated_request_cli(updates: dict[str, object]) -> subprocess.CompletedProcess[str]:
    return run_mutated_case_cli("manifest_writer_request.json", updates)


def run_mutated_pointer_cli(
    file_name: str,
    updates: dict[str, object],
) -> subprocess.CompletedProcess[str]:
    return run_mutated_case_cli(file_name, updates)


def run_mutated_case_cli(
    file_name: str,
    updates: dict[str, object],
) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        case_dir = copy_case_to_tmp(tmp_dir)
        path = case_dir / file_name
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload.update(updates)
        path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        return run_case_cli(case_dir)


def copy_case_to_tmp(tmp_dir: str) -> Path:
    case_dir = Path(tmp_dir) / "case"
    shutil.copytree(valid_case("metadata_only_minimal_no_file"), case_dir)
    return case_dir


def cleanup_manifest_output_root() -> None:
    shutil.rmtree(MANIFEST_OUTPUT_ROOT, ignore_errors=True)


def read_written_manifest(relative_path: str) -> dict[str, object]:
    return json.loads((MANIFEST_OUTPUT_ROOT / relative_path).read_text(encoding="utf-8"))


def write_existing_manifest(relative_path: str) -> None:
    path = MANIFEST_OUTPUT_ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "synthetic_existing_metadata_only_manifest_v0.1",
                "safe_summary": "existing",
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def count_manifest_output_files() -> int:
    if not MANIFEST_OUTPUT_ROOT.exists():
        return 0
    return sum(1 for path in MANIFEST_OUTPUT_ROOT.rglob("*") if path.is_file())


def assert_metadata_only_written_manifest(
    test_case: unittest.TestCase,
    payload: dict[str, object],
) -> None:
    test_case.assertEqual(
        payload["schema_version"],
        "learner_state_frozen_policy_generation_manifest_writer_metadata_only_manifest_v0.1",
    )
    test_case.assertEqual(
        payload["safe_summary"],
        "metadata_only_manifest_writer_result",
    )
    test_case.assertEqual(payload["count_summary"]["written_file_count"], 1)
    test_case.assertFalse(
        FORBIDDEN_WRITTEN_MANIFEST_KEYS.intersection(collect_keys(payload))
    )
    test_case.assertFalse(contains_unsafe_string(payload))


def collect_keys(value):
    keys = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            keys.add(str(key))
            keys.update(collect_keys(nested))
    elif isinstance(value, list):
        for nested in value:
            keys.update(collect_keys(nested))
    return keys


def contains_unsafe_string(value) -> bool:
    if isinstance(value, dict):
        return any(contains_unsafe_string(nested) for nested in value.values())
    if isinstance(value, list):
        return any(contains_unsafe_string(nested) for nested in value)
    if isinstance(value, str):
        return any(marker in value for marker in UNSAFE_STRING_MARKERS)
    return False


def assert_safe_cli_output(
    test_case: unittest.TestCase,
    completed: subprocess.CompletedProcess[str],
) -> None:
    assert_no_forbidden_fragments(
        test_case,
        completed.stdout + completed.stderr,
        [
            '"manifest_writer_request":',
            '"artifact_writer_result_pointer":',
            '"artifact_body_generation_result_pointer":',
            '"expected_manifest_writer_runtime_result":',
            '"manifest_body":',
            '"manifest_json_body":',
            '"artifact_body_payload":',
            '"generated_policy_body":',
            '"request_body":',
            '"pointer_body":',
            '"expected_body":',
            '"expected_result_body":',
            '"raw_rows":',
            '"logits":',
            '"probabilities":',
            '"raw_learner_text":',
            '"final_text":',
            '"observed_after_text":',
            '"gold_label":',
            '"scoring_feedback_payload":',
            '"real_participant_data":',
            '"performance_metrics":',
            "/Users/",
            "/home/",
            "/private/",
            "/var/folders/",
            "real_data/",
            "participant_data/",
            "manual_outputs/",
        ],
        normalize_paths=True,
    )


if __name__ == "__main__":
    unittest.main()
