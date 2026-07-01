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
- validator design: yes, Step499 docs-only / planning-only
- validator implemented: yes, Step500 static module / CLI / focused tests
- runtime actual invocation update implemented: no
- artifact writer CLI actual invocation implemented: no
- Makefile target added: yes, Step502 standalone validator target
- release-quality integration design: yes, Step503 docs-only design
- release-quality wrapper changed: yes, Step504 static fixture validation check
- workflow changed: no
- artifact body generation integration implemented: no
- manifest writer integration implemented: no
- file writing implemented: no

Step500 validator implementation:

- module: `python/learner_state/frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation.py`
- focused tests: `python/learner_state/tests/test_frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation.py`
- validation schema: `learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation_v0.1`
- expected aggregate: 32 cases / 192 JSON files / 6 valid / 26 invalid
- output boundary: public-safe summary-only; no fixture body, request body,
  pointer body, expected body, raw stdout/stderr body, artifact body payload,
  manifest body, generated policy body, raw rows, logits/probabilities,
  private paths, absolute paths, raw learner text, or real participant data

Step501 Makefile target design:

- design doc: `docs/frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validator_makefile_target_design.md`
- proposed target: `check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-fixtures`
- implementation status: implemented as standalone target in Step502
- release-quality status: not integrated

Step503 release-quality integration design:

- design doc: `docs/frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validator_release_quality_integration_design.md`
- proposed label: `release_quality_check: learner-state frozen policy generation artifact writer CLI actual invocation fixture validation`
- implementation status: implemented in Step504

Step504 release-quality wrapper integration:

- label: `release_quality_check: learner-state frozen policy generation artifact writer CLI actual invocation fixture validation`
- command: `make check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-fixtures`
- insertion point: after artifact writer CLI integration runtime smoke and before artifact body fixture validation
- safety boundary: static fixture validation only; no runtime actual invocation, artifact writer CLI actual invocation, artifact body generation integration, manifest writer integration, or file writing
