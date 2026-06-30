# Learner State Frozen Policy Generation Artifact Writer CLI Actual Invocation Fixtures

This fixture root was created in Step498 from the Step497 fixture contract
design for future artifact writer CLI actual invocation validation. The files
are synthetic-only, metadata-only, body-free, and no-oracle.

## Purpose

The root provides a future fixture set for validating a proposed metadata-only
artifact writer CLI actual invocation boundary. It is designed for future
validator work and future runtime update work. It does not implement actual
invocation and does not prove artifact writer CLI actual invocation correctness.

## Counts

- total_cases: 32
- valid_cases: 6
- invalid_cases: 26
- json_files_per_case: 6
- total_json_files: 192
- root_readme: 1

## Case Files

Each case directory contains six metadata-only JSON files:

- `case_metadata.json`: case identity, expected category, and synthetic-only / metadata-only flags.
- `runtime_request_metadata.json`: runtime request metadata for the proposed actual invocation boundary.
- `runtime_pointer_metadata.json`: relative metadata pointers and path safety flags.
- `artifact_writer_cli_invocation_metadata.json`: metadata-only command boundary information.
- `expected_invocation_summary.json`: expected public-safe summary fields and status mapping.
- `expected_error.json`: expected error category, reason code, and fail-closed / usage-error handling.

## Valid Case Taxonomy

- `valid/valid_minimal_metadata_only_actual_invocation_plan`
- `valid/valid_artifact_writer_cli_summary_body_free`
- `valid/valid_relative_fixture_paths_only`
- `valid/valid_file_writing_disabled_actual_invocation`
- `valid/valid_no_oracle_flags_preserved`
- `valid/valid_invocation_output_safety_flags`

## Invalid / Expected-Failure Case Taxonomy

- `invalid/invalid_request_body_present`
- `invalid/invalid_pointer_body_present`
- `invalid/invalid_expected_body_present`
- `invalid/invalid_artifact_body_payload_present`
- `invalid/invalid_manifest_body_present`
- `invalid/invalid_generated_policy_body_present`
- `invalid/invalid_raw_learner_text_present`
- `invalid/invalid_raw_rows_present`
- `invalid/invalid_logits_present`
- `invalid/invalid_probabilities_present`
- `invalid/invalid_private_path_present`
- `invalid/invalid_absolute_path_present`
- `invalid/invalid_final_text_present`
- `invalid/invalid_observed_after_text_present`
- `invalid/invalid_gold_label_present`
- `invalid/invalid_post_hoc_annotation_present`
- `invalid/invalid_raw_stdout_body_present`
- `invalid/invalid_raw_stderr_body_present`
- `invalid/invalid_file_writing_requested`
- `invalid/invalid_artifact_body_generation_invoked`
- `invalid/invalid_manifest_writer_invoked`
- `invalid/invalid_unsupported_artifact_writer_schema`
- `invalid/invalid_unsafe_actual_invocation_output`
- `invalid/invalid_mismatched_expected_status`
- `invalid/invalid_missing_required_metadata_file`
- `invalid/invalid_duplicate_case_id`

## Safety Policy

These fixtures use metadata-only sentinel flags for expected invalid cases. They
must not contain raw logs, copied job output, request/pointer/expected bodies,
written file bodies, manifest bodies, artifact body payloads, generated policy
bodies, raw stdout/stderr bodies, raw rows, logits/probabilities, private path
values, absolute path values, raw learner text, real participant data, or
performance metric bodies.

Relative fixture paths are allowed as metadata. Private or absolute path values
are not stored.

## Non-Claims

This fixture root does not claim production readiness, real-data readiness,
model performance, F1, accuracy, ECE, AURCC, artifact writer CLI actual
invocation correctness, artifact body generation integration correctness,
manifest writer integration correctness, generated policy quality, or
learner-state estimator correctness.

## Implementation Status

- fixture root created: yes, Step498
- fixture JSON created: yes, 192 metadata-only JSON files
- validator implemented: no
- runtime actual invocation update implemented: no
- artifact writer CLI actual invocation implemented: no
- Makefile target added: no
- release-quality wrapper changed: no
- workflow changed: no
- artifact body generation integration implemented: no
- manifest writer integration implemented: no
- file writing implemented: no
