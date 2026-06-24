# Learner-State Frozen Policy Generation Artifact Body File Writing Fixtures

## Purpose

This fixture root contains synthetic-only metadata contracts for future
artifact body file writing validator and implementation work. It does not
implement file writing, does not add a CLI option, does not write artifact
body files, does not generate or write manifests, and does not connect the
artifact writer CLI.

## Fixture Root

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing/`

## File List Per Case

Each case has four JSON files:

- `artifact_body_request.json`
- `artifact_writer_result_pointer.json`
- `file_write_request.json`
- `expected_file_write_result.json`

The files are metadata-only synthetic contracts. They do not contain artifact
body payloads, request bodies, pointer bodies, expected result bodies,
manifest bodies, raw rows, logits, private paths, raw learner text, real
participant data, or performance metric bodies.

## Schema Versions

- `learner_state_frozen_policy_generation_artifact_body_request_v0.1`
- `learner_state_frozen_policy_generation_artifact_body_writer_result_pointer_v0.1`
- `learner_state_frozen_policy_generation_artifact_body_file_write_request_v0.1`
- `learner_state_frozen_policy_generation_artifact_body_file_write_expected_result_v0.1`

## Valid Cases

- `valid_safe_metadata_relative_tmp_output`
- `valid_safe_metadata_nested_tmp_output`
- `valid_safe_metadata_no_output_path`
- `valid_safe_metadata_explicit_no_overwrite`
- `valid_safe_metadata_summary_only_stdout`

## Invalid Cases

- `invalid_suppressed_mode_with_output_path`
- `invalid_fail_closed_generation_with_output_path`
- `invalid_unsafe_body_audit_with_output_path`
- `invalid_absolute_output_path`
- `invalid_home_output_path`
- `invalid_parent_traversal_output_path`
- `invalid_private_path_marker_output_path`
- `invalid_dropbox_or_cloud_path_output_path`
- `invalid_manifest_file_output_attempt`
- `invalid_generated_policy_body_output_attempt`
- `invalid_request_body_leakage_in_file`
- `invalid_pointer_body_leakage_in_file`
- `invalid_expected_body_leakage_in_file`
- `invalid_raw_rows_in_file`
- `invalid_logits_dump_in_file`
- `invalid_private_path_in_file`
- `invalid_raw_learner_text_in_file`
- `invalid_performance_metric_body_in_file`
- `invalid_missing_synthetic_notice`
- `invalid_missing_no_oracle_notice`
- `invalid_missing_non_proof_notice`
- `invalid_overwrite_without_policy`
- `invalid_output_path_outside_allowed_root`
- `invalid_output_path_with_absolute_segment_after_normalization`

## Safety Rules

- No real data.
- No raw learner text.
- No raw rows.
- No logits or probability dumps.
- No actual private paths.
- No artifact body payload examples.
- No request, pointer, or expected-result bodies.
- No generated policy body.
- No manifest body.
- No performance metric body.

Private-path and unsafe-content invalid cases use synthetic marker names only.
They do not include actual local paths, learner text, rows, logits, or
metrics.

## Relation To Existing Artifact Body Fixtures

The existing artifact body fixtures validate body generation boundaries. This
fixture root is separate and targets future file writing, path-policy, and
file-output boundary validation.

## Relation To Future Validator

A future validator may read these fixtures to check expected outcomes,
path-policy decisions, body content policy decisions, and summary-only output.
The validator should avoid writing files by default or should write only in an
isolated temporary directory.

Step353 designs that future validator:

`docs/frozen_policy_generation_artifact_body_file_writing_fixture_validator_design.md`

The design keeps this fixture root unchanged. It does not implement the
validator, does not add a CLI option, does not write artifact body files,
does not write manifest files, does not connect artifact writer CLI, does not
use real data, and does not compute metrics.

## Relation To Future CLI Option

The future CLI option candidate is `--artifact-body-out`. These fixtures are
metadata contracts for that future option, but the option is not implemented
by this fixture root.

## Relation To Manifest Writer

Manifest writer work remains separate. These fixtures should expect
`manifest_file_written=false` and should fail closed on manifest file output
attempts.
