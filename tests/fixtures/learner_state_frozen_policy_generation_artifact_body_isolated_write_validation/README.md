# Learner-State Frozen Policy Generation Artifact Body Isolated Write Validation Fixtures

This fixture root contains synthetic-only, metadata-only, no-oracle fixtures for future isolated temp write validation of frozen policy generation artifact body file writing.

## Fixture Root

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_isolated_write_validation/`

## Purpose

These fixtures describe valid and expected-failure cases for a future validator that will run artifact body generation CLI file writing inside an isolated temp root. They are fixture contracts only. They do not implement the validator, do not add a Makefile target, do not add release-quality integration, do not write manifests, and do not connect the artifact writer CLI.

## Case Counts

- valid cases: 5
- invalid / expected-failure cases: 17
- total cases: 22
- JSON files per case: 5
- total JSON files: 110

## Files Per Case

Each case directory contains:

- `case_metadata.json`
- `artifact_body_request.json`
- `artifact_writer_result_pointer.json`
- `isolated_write_request.json`
- `expected_isolated_write_result.json`

## Schema Versions

- `learner_state_frozen_policy_generation_artifact_body_isolated_write_case_metadata_v0.1`
- `learner_state_frozen_policy_generation_artifact_body_isolated_write_request_v0.1`
- `learner_state_frozen_policy_generation_artifact_body_isolated_write_expected_result_v0.1`

The artifact body request and writer result pointer files use the existing artifact body generation fixture-compatible schema versions.

## Valid Cases

- `valid/safe_metadata_flat_relative_output`
- `valid/safe_metadata_nested_relative_output`
- `valid/safe_metadata_output_parent_created`
- `valid/safe_metadata_no_output_no_file`
- `valid/safe_metadata_existing_output_rejected_after_precreate`

The existing-output case is a valid contract case because the expected behavior is safe refusal without overwrite.

## Invalid / Expected-Failure Cases

- `invalid/suppressed_default_with_output_usage_error`
- `invalid/suppressed_explicit_with_output_usage_error`
- `invalid/absolute_output_path_usage_error`
- `invalid/home_output_path_usage_error`
- `invalid/drive_root_output_path_usage_error`
- `invalid/parent_traversal_output_path_usage_error`
- `invalid/private_marker_output_path_usage_error`
- `invalid/cloud_marker_output_path_usage_error`
- `invalid/hidden_private_directory_usage_error`
- `invalid/non_json_extension_usage_error`
- `invalid/unsafe_filename_usage_error`
- `invalid/too_long_path_usage_error`
- `invalid/existing_output_without_overwrite_usage_error`
- `invalid/generation_fail_closed_no_file`
- `invalid/unsafe_body_audit_no_file`
- `invalid/manifest_write_attempt_not_supported`
- `invalid/generated_policy_body_write_attempt_not_supported`

Expected failures should count as matched cases when the future validator observes the expected safe refusal category.

## Safety Rules

- No real participant data.
- No raw learner text.
- No raw rows.
- No logits or probability dumps.
- No artifact body payload examples.
- No request, pointer, isolated write request, or expected result body examples in docs.
- No generated policy body.
- No manifest body.
- No actual private paths or absolute local paths.
- No performance metric body.

Invalid cases use synthetic metadata, case IDs, and reason-code names rather than real unsafe content.

## Relationship To Existing Fixtures

This root is separate from the existing no-write file writing fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing/`

The no-write fixture root validates static file-writing/path-policy contracts. This isolated write fixture root is for a future validator that will execute write attempts inside a temporary isolated root.

## Future Validator

The proposed future validator module is:

`learner_state.frozen_policy_generation_artifact_body_isolated_write_validation`

It should produce summary-only, count-only output and must not print fixture JSON bodies or written artifact body payloads.

## Future CLI / Makefile / Release Quality

No CLI, Makefile target, or release-quality integration is added by this fixture root. Those are future steps after the isolated validator exists and is stable.

## Future Standalone Makefile Target

Step371 adds a docs-only design for a future standalone target:

`check-learner-state-frozen-policy-generation-artifact-body-isolated-write-validation`

The proposed target would run the isolated write validator CLI against this
fixture root and expect 22 matched cases with zero residue. The target is not
implemented by Step371, and release-quality integration remains a later
separate step.

## Validator Availability

Step372 restores and confirms the validator module and CLI:

`learner_state.frozen_policy_generation_artifact_body_isolated_write_validation`

The validator runs this fixture root in isolated temp roots and confirms the
22 expected outcomes without printing fixture JSON bodies or written artifact
body payloads. Step372 does not change the fixture JSON files and does not add
a Makefile target or release-quality integration.

## Standalone Makefile Target

Step373 adds the standalone target:

`check-learner-state-frozen-policy-generation-artifact-body-isolated-write-validation`

The target runs the isolated write validator CLI against this fixture root and
expects 22 matched cases, 0 mismatches, 0 input errors, and 0 residue files.
The target is not added to release-quality in Step373, and fixture JSON files
remain unchanged.

## Future Release-Quality Integration

Step374 adds a docs-only design for future release-quality integration of the
standalone isolated write validator target. The proposed wrapper placement is
after the no-write artifact body file-writing fixture validation target and
before config/scoring smoke checks.

Future release-quality integration should require `residue_file_count=0` and
must not print fixture JSON bodies, written file content, artifact body
payloads, private paths, absolute temp paths, raw rows, logits, or raw learner
text. Step374 does not change this fixture root and does not modify the
release-quality wrapper.

## Release-Quality Wrapper Integration

Step375 integrates the standalone isolated write validator target into the
release-quality wrapper:

`make check-learner-state-frozen-policy-generation-artifact-body-isolated-write-validation`

The wrapper placement is after the no-write artifact body file-writing fixture
validation target and before config/scoring smoke checks. The fixture JSON
files remain unchanged. The wrapper must keep output summary-only and require
22 matched cases, 0 mismatches, 0 input errors, and 0 residue files.

## Future Remote Status Marker

Step376 adds a docs-only workflow design for a future public-safe remote/manual
Release Quality status marker:

`docs/status/learner_state_frozen_policy_generation_artifact_body_isolated_write_release_quality_remote_run_status.md`

That future marker should record only pass-only/count-only metadata and safety
flags for this 22-case fixture root. It must not copy fixture JSON bodies,
written file content, artifact body payloads, private paths, absolute temp
paths, raw rows, logits, raw learner text, raw logs, or real participant data.
