# Frozen Policy Generation Artifact Writer CLI Integration Runtime Fixture Contract Design

## 1. Scope

This document is the contract design for a future artifact writer CLI
integration runtime fixture root.

This is design-only. It does not:

- create the fixture root
- create fixture JSON
- implement a validator
- implement runtime integration
- add a Makefile target
- change the release-quality wrapper
- change workflow YAML
- change Python code or tests
- implement artifact body generation integration
- implement manifest writer integration
- generate manifest bodies
- generate policy bodies
- prove production readiness
- prove real-data readiness
- prove model performance

The future fixture contract must remain synthetic-only, metadata-only,
no-oracle, public-safe, body-suppressed, and fail-closed.

## 2. Prior Completed Chain

- Step466 created the artifact writer CLI integration design.
- Step467 created the artifact writer CLI integration fixture contract design.
- Step468 created the fixture root for static CLI integration contract cases.
- Step469 created the fixture validator design.
- Step470 implemented the validator module, CLI, and focused tests.
- Step471 created the standalone Makefile target design.
- Step472 implemented the standalone Makefile target.
- Step473 created the release-quality integration design.
- Step474 integrated the target into the release-quality wrapper.
- Step475 created the remote/manual run record workflow design.
- Step476 created the public-safe remote status marker for Release Quality.
- Step477 created the artifact writer CLI integration runtime design.

Step476 records that fixture validation was included in Release Quality and
passed as public-safe pass-only / count-only metadata. It is not runtime
correctness evidence.

Step477 defines the future runtime boundary and contract. It does not implement
runtime behavior and does not prove runtime correctness.

## 3. Proposed Fixture Root

Future fixture root proposal:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime/`

Step478 does not create this directory.

The future root should use `valid/` and `invalid/` groups with deterministic
case ids based on relative case paths.

## 4. Proposed Case Layout

Each future case directory should contain six metadata-only JSON files:

- `case_metadata.json`
- `request_metadata.json`
- `pointer_metadata.json`
- `artifact_writer_cli_metadata.json`
- `expected_runtime_summary.json`
- `expected_error.json`

File roles:

- `case_metadata.json`: case id, group, status category, expected reason code,
  synthetic-only flag, no-oracle flag, metadata-only flag, and release-quality
  non-readiness flags.
- `request_metadata.json`: safe request metadata for the future runtime entry
  point.
- `pointer_metadata.json`: safe pointer identifiers and relative fixture
  references only.
- `artifact_writer_cli_metadata.json`: metadata describing the future artifact
  writer CLI boundary without command output bodies.
- `expected_runtime_summary.json`: expected public-safe runtime summary field
  names and expected status categories.
- `expected_error.json`: expected public-safe error category and reason code
  metadata for invalid cases.

The fixture contract should not include JSON body examples in docs.

## 5. Proposed Case Counts

Proposed future counts:

- total_cases: 30
- valid_cases: 6
- invalid_cases: 24
- json_files_per_case: 6
- total_json_files: 180

These counts are a proposal only. Step478 does not create files.

## 6. Valid Case Taxonomy

Proposed valid cases:

- `valid/minimal_metadata_only_runtime_pass`
- `valid/suppressed_artifact_writer_summary_pass`
- `valid/safe_relative_repo_path_pass`
- `valid/file_writing_disabled_pass`
- `valid/no_oracle_flags_pass`
- `valid/fail_safe_suppression_flags_pass`

Valid cases should confirm that the future runtime returns a metadata-only
summary, preserves suppression flags, keeps file writing disabled by default,
and does not cross into artifact body generation or manifest writer
integration.

Valid cases must not include artifact body payloads, manifest bodies, generated
policy bodies, raw rows, logits, private paths, absolute paths, raw learner
text, final text fields, observed-after fields, gold labels, or performance
metric bodies.

## 7. Invalid / Expected-Failure Case Taxonomy

Proposed invalid cases and failure boundary:

- `invalid/request_body_present`: fail_closed
- `invalid/pointer_body_present`: fail_closed
- `invalid/expected_body_present`: fail_closed
- `invalid/artifact_body_payload_present`: fail_closed
- `invalid/manifest_body_present`: fail_closed
- `invalid/generated_policy_body_present`: fail_closed
- `invalid/raw_learner_text_present`: fail_closed
- `invalid/raw_rows_present`: fail_closed
- `invalid/logits_probabilities_present`: fail_closed
- `invalid/private_path_present`: fail_closed
- `invalid/absolute_path_present`: fail_closed
- `invalid/final_text_present`: fail_closed
- `invalid/observed_after_text_present`: fail_closed
- `invalid/gold_label_present`: fail_closed
- `invalid/post_hoc_annotation_present`: fail_closed
- `invalid/unsupported_schema_version`: usage_error
- `invalid/ambiguous_file_writing_target`: usage_error
- `invalid/unexpected_manifest_writer_request`: fail_closed
- `invalid/unexpected_artifact_body_generation_request`: fail_closed
- `invalid/unsafe_output_residue_risk`: fail_closed
- `invalid/missing_required_metadata_file`: input_error
- `invalid/mismatched_expected_status`: mismatch
- `invalid/mismatched_expected_reason_code`: mismatch
- `invalid/invalid_case_id`: input_error
- `invalid/duplicate_case_id`: input_error

The validator should distinguish malformed fixture input from runtime-style
safety failures. Public output should report only category, reason code, and
counts.

## 8. Expected Result Schema

Future `expected_runtime_summary.json` should define these field names:

- `schema_version`
- `case_id`
- `expected_status`
- `expected_reason_code`
- `expected_exit_code_category`
- `expected_summary_mode`
- `content_suppressed`
- `body_suppressed`
- `no_raw_rows`
- `no_logits_dump`
- `no_private_paths`
- `no_absolute_paths`
- `no_generated_policy_body`
- `no_artifact_body_payload`
- `no_manifest_body`
- `no_request_body`
- `no_pointer_body`
- `no_expected_body`
- `no_oracle_checked`
- `synthetic_only_checked`
- `metadata_only_checked`
- `file_writing_enabled`
- `residue_expected`
- `production_readiness_claimed`
- `real_data_readiness_claimed`
- `performance_claims_present`

Suggested schema version name:

`learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_result_v0.1`

Docs should list field names only and should not include fixture JSON bodies.

## 9. Runtime Request Metadata Contract

Allowed request metadata field names:

- `schema_version`
- `case_id`
- `mode`
- `validation_schema_version`
- `artifact_writer_cli_summary_mode`
- `fixture_source`
- `relative_fixture_path`
- `suppression_policy`
- `no_oracle_policy`
- `synthetic_only`
- `metadata_only`
- `file_writing_requested`

Forbidden request metadata field names:

- `request_body`
- `pointer_body`
- `expected_body`
- `final_text`
- `observed_after_text`
- `raw_learner_text`
- `raw_rows`
- `logits`
- `probabilities`
- `gold_labels`
- `post_hoc_annotations`
- `generated_policy_body`
- `artifact_body_payload`
- `manifest_body`
- `absolute_path`
- `private_path`

The future validator should reject forbidden field names and forbidden content
markers fail-closed or as fixture input errors, depending on where the issue is
detected.

## 10. Runtime Pointer Metadata Contract

Allowed pointer metadata field names:

- `schema_version`
- `case_id`
- `pointer_id`
- `relative_fixture_path`
- `fixture_reference_id`
- `validation_status`
- `synthetic_only`
- `metadata_only`
- `no_oracle_checked`
- `content_suppressed`
- `body_suppressed`

Forbidden pointer metadata field names:

- `pointer_body`
- `request_body`
- `expected_body`
- `absolute_path`
- `private_path`
- `raw_learner_text`
- `raw_rows`
- `logits`
- `probabilities`
- `artifact_body_payload`
- `manifest_body`
- `generated_policy_body`
- `final_text`
- `observed_after_text`
- `gold_labels`
- `post_hoc_annotations`

Relative repo paths may be used as fixture references. Absolute paths and
private path markers must be forbidden.

## 11. Artifact Writer CLI Metadata Contract

Allowed artifact writer CLI metadata field names:

- `schema_version`
- `case_id`
- `command_label`
- `safe_mode`
- `summary_mode`
- `expected_exit_code_category`
- `relative_fixture_pointers`
- `content_suppressed`
- `body_suppressed`
- `artifact_body_suppressed`
- `manifest_body_suppressed`
- `synthetic_only_checked`
- `no_oracle_checked`

Forbidden artifact writer CLI metadata field names:

- `command_output_raw_body`
- `full_stdout`
- `full_stderr`
- `artifact_body_payload`
- `manifest_body`
- `generated_policy_body`
- `file_contents`
- `raw_rows`
- `logits`
- `probabilities`
- `private_path`
- `absolute_path`
- `raw_learner_text`

The future fixture contract should describe the CLI boundary without invoking
the CLI or storing command output bodies.

## 12. Validator Implications

A future validator should check:

- root discovery under `valid/` and `invalid/`
- required file presence
- no extra JSON files per case
- case id consistency across files
- schema version consistency
- expected status and reason-code matching
- forbidden key scan
- forbidden string scan
- absolute/private path scan
- no-oracle field scan
- synthetic-only flag consistency
- metadata-only flag consistency
- suppression flag consistency
- file-writing disabled/default policy
- artifact body generation separation
- manifest writer separation
- residue expectation checks
- safe summary field matching
- deterministic ordering
- selector safety for single-case validation

The validator should print only public-safe counts, statuses, flags, and reason
codes.

## 13. Exit-Code And Status Mapping

Proposed status values:

- `pass`: expected metadata-only runtime summary matches the contract.
- `usage_error`: unsupported schema, unsupported mode, ambiguous file-writing
  target, or invalid CLI argument.
- `fail_closed`: prohibited content or unsafe boundary crossing detected.
- `input_error`: malformed fixture root, missing required file, invalid case
  id, or duplicate case id.
- `mismatch`: fixture expected summary does not match validator-observed
  status, reason code, or safety flags.

Proposed exit-code categories:

- `success`
- `usage_error`
- `fail_closed`
- `input_error`
- `mismatch`

The mapping is design-only and does not implement runtime or validator code.

## 14. Relationship To Step477 Runtime Design

Step477 defines the future artifact writer CLI integration runtime boundary,
runtime contract, CLI flow, fail-closed behavior, and public-safe checklist.

Step478 defines the future fixture contract used to test that runtime boundary
in later steps. It specifies the proposed fixture root, case layout, case
counts, schemas, metadata contracts, and validator implications.

Step478 does not create runtime fixtures and does not prove runtime
correctness.

## 15. Planned Follow-Up Steps

Suggested future sequence:

- Step479: artifact writer CLI integration runtime fixture root creation
- Step480: runtime fixture validator design
- Step481: runtime fixture validator module / CLI / focused tests
- Step482: standalone Makefile target design
- Step483: standalone Makefile target implementation
- Step484: release-quality integration design
- Step485: release-quality wrapper integration
- Step486: remote/manual run record workflow design
- Step487: remote status marker
- Step488: artifact writer CLI integration runtime implementation design

The numbering is a proposal. Step478 does not advance into these steps.

## 15.1 Step479 Fixture Root Creation Status

Step479 creates the fixture root proposed in this design:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime/`

The root contains 30 case directories, 6 valid cases, 24 invalid cases, 6 JSON
files per case, and 180 JSON case files. Step479 does not implement a
validator, implement runtime integration, add a Makefile target, change the
release-quality wrapper, change workflow YAML, change Python code/tests, use
real data, compute metrics, or claim production readiness.

## 16. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1, accuracy, ECE, or AURCC achievement
- artifact writer CLI integration runtime correctness
- artifact body generation integration correctness
- manifest writer integration correctness
- generated policy quality
- learner-state estimator correctness
- fixture root creation
- validator implementation
- runtime implementation

## 17. Public-Safe Checklist

- no raw logs
- no full job output
- no fixture JSON body
- no request body
- no pointer body
- no expected body
- no written file JSON body
- no manifest body
- no artifact body payload
- no generated policy body
- no raw rows
- no logits or probabilities
- no private paths
- no absolute paths
- no raw learner text
- no real participant data
- no performance claims
- no production readiness claims
- no real-data readiness claims
