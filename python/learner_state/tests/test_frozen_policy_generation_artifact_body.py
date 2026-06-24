from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from learner_state.frozen_policy_generation_artifact_body import (
    ARTIFACT_BODY_SCHEMA_VERSION,
    BODY_STATUS_FAIL_CLOSED,
    BODY_STATUS_GENERATED_SAFE,
    BODY_STATUS_SUPPRESSED,
    audit_artifact_body_safety,
    build_safe_metadata_body,
    build_suppressed_metadata_only_body,
    generate_artifact_body,
    summarize_artifact_body_result,
)
from learner_state.frozen_policy_generation_artifact_body_fixture_validation import (
    validate_artifact_body_fixture_root,
)
from learner_state.frozen_policy_generation_artifact_writer import (
    load_artifact_writer_request,
    load_generator_result_pointer,
    run_artifact_writer,
    summarize_artifact_writer_result,
)
from test_support.safe_output_scan import assert_no_forbidden_fragments

FIXTURE_ROOT = Path(
    "tests/fixtures/learner_state_frozen_policy_generation_artifact_body"
)
ARTIFACT_WRITER_FIXTURE_ROOT = Path(
    "tests/fixtures/learner_state_frozen_policy_generation_artifact_writer"
)

FORBIDDEN_BODY_FRAGMENTS = (
    '"raw_learner_text":',
    '"raw_rows":',
    '"logits":',
    '"probabilities":',
    '"private_path":',
    '"request_body":',
    '"pointer_body":',
    '"expected_result_body":',
    '"generated_policy_body":',
    '"manifest_body":',
    '"performance_metrics":',
    "synthetic unsafe body marker",
)


class FrozenPolicyGenerationArtifactBodyTests(unittest.TestCase):
    def test_suppressed_metadata_only_body_is_generated_safely(self) -> None:
        request, pointer = _load_case("valid/minimal_suppressed_metadata_only_body")

        body = build_suppressed_metadata_only_body(request, pointer)
        audit = audit_artifact_body_safety(body)

        self.assertEqual(body["artifact_body_schema_version"], ARTIFACT_BODY_SCHEMA_VERSION)
        self.assertEqual(body["body_status"], BODY_STATUS_SUPPRESSED)
        self.assertTrue(body["content_suppressed"])
        self.assertEqual(body["allowed_sections"], [])
        self.assertEqual(audit.reason_codes, [])
        self.assertEqual(audit.count_summary.raw_row_count, 0)
        self.assertEqual(audit.count_summary.logits_dump_count, 0)

    def test_safe_metadata_body_is_generated_safely(self) -> None:
        request, pointer = _load_case("valid/safe_metadata_body_summary")

        body = build_safe_metadata_body(request, pointer)
        audit = audit_artifact_body_safety(body)

        self.assertEqual(body["body_status"], BODY_STATUS_GENERATED_SAFE)
        self.assertTrue(body["synthetic_only_notice"])
        self.assertTrue(body["no_oracle_notice"])
        self.assertEqual(audit.reason_codes, [])
        self.assertGreater(body["count_summary"]["body_field_count"], 0)
        self.assertEqual(body["count_summary"]["raw_row_count"], 0)

    def test_generated_body_is_json_serializable_and_deterministic(self) -> None:
        request, pointer = _load_case("valid/safe_metadata_body_summary")

        first = build_safe_metadata_body(request, pointer)
        second = build_safe_metadata_body(request, pointer)

        self.assertEqual(
            json.dumps(first, sort_keys=True),
            json.dumps(second, sort_keys=True),
        )
        json.loads(json.dumps(first, sort_keys=True))

    def test_generated_body_excludes_forbidden_payload_fields(self) -> None:
        request, pointer = _load_case("valid/safe_validation_reference_body_summary")

        body = build_safe_metadata_body(request, pointer)
        rendered = json.dumps(body, sort_keys=True)

        assert_no_forbidden_fragments(self, rendered, FORBIDDEN_BODY_FRAGMENTS)

    def test_generate_artifact_body_defaults_to_suppressed_metadata_only(self) -> None:
        request, pointer = _load_case("valid/minimal_suppressed_metadata_only_body")

        result = generate_artifact_body(request, pointer)
        summary = summarize_artifact_body_result(result)

        self.assertEqual(result.body_status, BODY_STATUS_SUPPRESSED)
        self.assertEqual(result.validation_status, "pass")
        self.assertFalse(result.artifact_body_available)
        self.assertIsNone(result.artifact_body)
        self.assertEqual(summary["artifact_body_available"], False)
        self.assertEqual(summary["artifact_file_written"], False)
        self.assertEqual(summary["manifest_file_written"], False)

    def test_generate_artifact_body_can_return_safe_metadata_body(self) -> None:
        request, pointer = _load_case("valid/safe_metadata_body_summary")

        result = generate_artifact_body(request, pointer)

        self.assertEqual(result.body_status, BODY_STATUS_GENERATED_SAFE)
        self.assertEqual(result.validation_status, "pass")
        self.assertTrue(result.artifact_body_available)
        self.assertIsInstance(result.artifact_body, dict)
        self.assertEqual(result.reason_codes, [])

    def test_result_summary_is_body_free_by_default(self) -> None:
        request, pointer = _load_case("valid/safe_reason_code_body_summary")

        result = generate_artifact_body(request, pointer)
        summary = summarize_artifact_body_result(result)
        rendered = json.dumps(summary, sort_keys=True)

        self.assertNotIn("artifact_body", summary)
        assert_no_forbidden_fragments(self, rendered, FORBIDDEN_BODY_FRAGMENTS)

    def test_safety_audit_fail_closes_for_synthetic_forbidden_payload(self) -> None:
        request, pointer = _load_case("valid/safe_metadata_body_summary")
        body = build_safe_metadata_body(request, pointer)
        unsafe_body = dict(body)
        unsafe_body["raw_learner_text"] = "synthetic unsafe body marker"

        audit = audit_artifact_body_safety(unsafe_body)
        rendered = json.dumps(audit.to_safe_dict(), sort_keys=True)

        self.assertIn("raw_learner_text_in_artifact_body", audit.reason_codes)
        self.assertNotIn("synthetic unsafe body marker", rendered)

    def test_generate_fail_closed_does_not_echo_forbidden_payload_text(self) -> None:
        request, pointer = _load_case("valid/safe_metadata_body_summary")
        unsafe_request = dict(request)
        unsafe_request["raw_learner_text"] = "synthetic unsafe body marker"

        result = generate_artifact_body(unsafe_request, pointer)
        summary = summarize_artifact_body_result(result)
        rendered = json.dumps(summary, sort_keys=True)

        self.assertEqual(result.body_status, BODY_STATUS_FAIL_CLOSED)
        self.assertEqual(result.validation_status, "fail")
        self.assertIn("raw_learner_text_in_artifact_body", result.reason_codes)
        self.assertFalse(result.artifact_body_available)
        self.assertNotIn("synthetic unsafe body marker", rendered)

    def test_missing_notices_fail_closed(self) -> None:
        request, pointer = _load_case("valid/safe_metadata_body_summary")
        missing_notice_request = dict(request)
        missing_notice_request["synthetic_only_notice_present"] = False
        missing_notice_request["no_oracle_notice_present"] = False

        result = generate_artifact_body(missing_notice_request, pointer)

        self.assertEqual(result.body_status, BODY_STATUS_FAIL_CLOSED)
        self.assertIn("missing_synthetic_notice", result.reason_codes)
        self.assertIn("missing_no_oracle_notice", result.reason_codes)

    def test_unknown_body_schema_fails_audit(self) -> None:
        request, pointer = _load_case("valid/safe_metadata_body_summary")
        body = build_safe_metadata_body(request, pointer)
        unsafe_body = dict(body)
        unsafe_body["artifact_body_schema_version"] = "unknown_schema_v0"

        audit = audit_artifact_body_safety(unsafe_body)

        self.assertIn("unknown_artifact_body_schema_version", audit.reason_codes)

    def test_no_artifact_or_manifest_files_are_written(self) -> None:
        request, pointer = _load_case("valid/safe_metadata_body_summary")
        with tempfile.TemporaryDirectory() as tmp_dir:
            before = set(Path(tmp_dir).iterdir())
            result = generate_artifact_body(request, pointer)
            after = set(Path(tmp_dir).iterdir())

        self.assertEqual(before, after)
        self.assertFalse(result.artifact_file_written)
        self.assertFalse(result.manifest_file_written)

    def test_artifact_body_fixture_validator_still_passes_all_cases(self) -> None:
        result = validate_artifact_body_fixture_root(FIXTURE_ROOT)

        self.assertEqual(result.total_cases, 18)
        self.assertEqual(result.matched_cases, 18)
        self.assertEqual(result.mismatched_cases, 0)
        self.assertEqual(result.input_error_cases, 0)

    def test_existing_artifact_writer_runtime_remains_body_suppressed(self) -> None:
        case = ARTIFACT_WRITER_FIXTURE_ROOT / "valid" / "minimal_metadata_only_artifact_plan"
        request = load_artifact_writer_request(case / "artifact_writer_request.json")
        pointer = load_generator_result_pointer(case / "generator_result_pointer.json")

        result = run_artifact_writer(request, pointer)
        summary = summarize_artifact_writer_result(result)

        self.assertEqual(summary["writer_status"], "pass")
        self.assertTrue(summary["artifact_flags"]["artifact_body_suppressed"])
        self.assertFalse(summary["artifact_flags"]["generated_artifact_body_available"])
        self.assertEqual(summary["count_summary"]["body_field_count"], 0)


def _load_case(case_label: str) -> tuple[dict[str, object], dict[str, object]]:
    case_dir = FIXTURE_ROOT / case_label
    request = json.loads((case_dir / "artifact_body_request.json").read_text())
    pointer = json.loads((case_dir / "artifact_writer_result_pointer.json").read_text())
    return request, pointer


if __name__ == "__main__":
    unittest.main()
