# Frozen Policy Generation Artifact Writer CLI Integration Runtime Fixtures

This fixture root contains synthetic-only, metadata-only, no-oracle fixture
contracts for a future artifact writer CLI integration runtime.

The root was created in Step479 from the Step478 fixture contract design:

`docs/frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_contract_design.md`

## Fixture Root

`tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime/`

## Case Counts

- total_cases: 30
- valid_cases: 6
- invalid_cases: 24
- json_files_per_case: 6
- total_json_files: 180

## Case Files

Each case directory contains exactly these metadata-only files:

- `case_metadata.json`: case id, group, expected status, reason code, and public-safe policy flags.
- `request_metadata.json`: future runtime request metadata without request body payloads.
- `pointer_metadata.json`: safe pointer metadata using relative fixture references only.
- `artifact_writer_cli_metadata.json`: future artifact writer CLI boundary metadata without command output bodies.
- `expected_runtime_summary.json`: expected public-safe runtime summary fields and safety flags.
- `expected_error.json`: expected public-safe error category, reason code, and exit-code category.

## Valid Case Taxonomy

- `valid/valid_minimal_metadata_runtime_pass`
- `valid/valid_suppressed_artifact_writer_summary_pass`
- `valid/valid_safe_relative_repo_path_pass`
- `valid/valid_file_writing_disabled_pass`
- `valid/valid_no_oracle_flags_pass`
- `valid/valid_fail_safe_suppression_flags_pass`

Valid cases model future metadata-only runtime summaries. They do not include
artifact body payloads, manifest bodies, generated policy bodies, raw text, raw
rows, logits, private paths, absolute paths, or performance evidence.

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
- `invalid/invalid_unsupported_schema_version`
- `invalid/invalid_ambiguous_file_writing_target`
- `invalid/invalid_unexpected_manifest_writer_request`
- `invalid/invalid_unexpected_artifact_body_generation_request`
- `invalid/invalid_unsafe_output_residue_risk`
- `invalid/invalid_missing_required_metadata_file`
- `invalid/invalid_mismatched_expected_status`
- `invalid/invalid_duplicate_case_id`

Invalid cases use safe marker fields and boolean presence flags only. They do
not include the prohibited content itself.

## Public-Safe Policy

These fixtures are:

- synthetic-only
- metadata-only
- no-oracle
- body-suppressed
- public-safe
- count-only where summaries are expected

They must not include raw GitHub Actions logs, full job output, request body
payloads, pointer body payloads, expected body payloads, written file JSON
bodies, manifest bodies, artifact body payloads, generated policy bodies, raw
rows, logits or probabilities, private paths, absolute paths, raw learner text,
real participant data, or screenshots containing raw logs.

## Non-Claims

This fixture root does not prove runtime correctness, artifact body generation
integration correctness, manifest writer integration correctness, generated
policy quality, model performance, learner-state estimator correctness,
real-data readiness, or production readiness.

## Future Validator Design

Step480 adds the docs-only validator design for this fixture root:

[Frozen policy generation artifact writer CLI integration runtime fixture validator design](../../../docs/frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validator_design.md)

The design describes future static validation only. It does not implement the
validator, execute runtime integration, add a Makefile target, change
release-quality wrapper or workflow files, change Python code/tests, or change
fixture JSON.

## Validator Implementation

Step481 implements the static validator module, CLI, and focused tests for this
fixture root:

`python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation.py`

The validator checks fixture contracts only. It does not execute runtime
integration, call artifact writer CLI integration runtime, connect artifact
body generation, connect manifest writer integration, write files, change
fixture JSON, or prove production readiness.

## Implementation Status

- fixture root created: yes
- fixture JSON created: yes
- validator implemented: yes
- runtime implemented: no
- Makefile target added: no
- release-quality wrapper changed: no
- workflow changed: no
- artifact body generation integration implemented: no
- manifest writer integration implemented: no
