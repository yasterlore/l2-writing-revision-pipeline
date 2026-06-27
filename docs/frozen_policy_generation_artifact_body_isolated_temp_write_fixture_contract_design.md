# Frozen Policy Generation Artifact Body Isolated Temp Write Fixture Contract Design

## 1. Purpose

This document defines the future fixture contract for isolated temp write
validation of frozen policy generation artifact body file writing.

It is a docs-only fixture contract design. It does not create fixture JSON,
does not implement the validator, does not add a Makefile target, does not add
release-quality integration, does not implement a manifest writer, and does
not connect the artifact writer CLI.

The contract remains synthetic-only, metadata-only, no-oracle, and body-safe.
It is not performance evaluation, real-data readiness, or production
readiness evidence.

## 2. Current State

- `--artifact-body-out` exists on the artifact body generation CLI.
- `--mode safe-metadata` can write a safe metadata artifact body file.
- The fixed safe root is `tmp/artifact_body_generation/`.
- The standalone smoke target exists:
  `check-learner-state-frozen-policy-generation-artifact-body-file-writing-smoke`.
- The smoke target checks one safe valid write path.
- The isolated temp write validation design exists:
  [Frozen policy generation artifact body isolated temp write validation design](frozen_policy_generation_artifact_body_isolated_temp_write_validation_design.md).
- The isolated temp write fixture contract does not exist yet.
- The isolated temp write validator does not exist.
- Isolated fixture JSON does not exist.
- Manifest writer does not exist.
- Artifact writer CLI integration does not exist.

## 3. Proposed Fixture Root

Candidates:

- `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_isolated_write_validation/`
- `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_temp_write_validation/`
- `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing_isolated/`

Recommended:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_isolated_write_validation/`

Reasons:

- It matches the proposed module name:
  `learner_state.frozen_policy_generation_artifact_body_isolated_write_validation`.
- It is distinct from the existing no-write file writing fixture root.
- It clearly indicates that the fixture root is for isolated write
  validation.
- It identifies the artifact body generation CLI file-writing boundary.

Step368 did not create that root. Step369 creates it as a fixture JSON root,
while still not implementing the validator.

## 4. Proposed Case Directory Structure

Future cases should be grouped by expected case kind:

- `valid/<case_name>/`
- `invalid/<case_name>/`

Each case directory should contain:

- `case_metadata.json`
- `artifact_body_request.json`
- `artifact_writer_result_pointer.json`
- `isolated_write_request.json`
- `expected_isolated_write_result.json`

Docs must not include the JSON bodies. The file names and meanings are enough
for this design.

## 5. Proposed Schemas

Schema names:

- `learner_state_frozen_policy_generation_artifact_body_isolated_write_case_metadata_v0.1`
- `learner_state_frozen_policy_generation_artifact_body_isolated_write_request_v0.1`
- `learner_state_frozen_policy_generation_artifact_body_isolated_write_expected_result_v0.1`

The future validator should fail closed on unknown schema versions.

## 6. Case Metadata Fields

Future `case_metadata.json` fields:

- `schema_version`
- `case_id`
- `case_kind`
- `description`
- `source_fixture_case`
- `expected_category`
- `expected_status`
- `expected_exit_code`
- `safety_expectation`
- `should_write_file`
- `should_cleanup`
- `should_leave_residue`
- `allowed_failure_reason_codes`
- `forbidden_output_markers`
- `required_summary_fields`
- `forbidden_summary_fields`
- `notes`

`case_kind` should be `valid` or `invalid`. A valid contract case may still
expect a usage error when the point of the case is verifying a safe refusal
such as overwrite rejection.

## 7. Isolated Write Request Fields

Future `isolated_write_request.json` fields:

- `schema_version`
- `case_id`
- `cli_mode`
- `artifact_body_out`
- `precreate_output_file`
- `expected_safe_root`
- `cleanup_policy`
- `parse_written_file`
- `scan_written_file`
- `scan_stdout_stderr`
- `allow_parent_creation`
- `allow_overwrite`
- `expect_manifest_file`
- `expect_manifest_body`
- `expect_artifact_file_written`
- `expect_body_payload_printed`
- `synthetic_only`
- `no_oracle_required`

The request should contain only metadata needed to run the CLI and validate
the outcome. It must not contain artifact body payloads, raw rows, logits,
private paths, or real data.

## 8. Expected Isolated Write Result Fields

Future `expected_isolated_write_result.json` fields:

- `schema_version`
- `case_id`
- `expected_category`
- `expected_status`
- `expected_exit_code`
- `expected_file_written`
- `expected_file_parse_ok`
- `expected_file_allowed_keys_only`
- `expected_file_cleanup_ok`
- `expected_residue_file_count`
- `expected_stdout_body_free`
- `expected_stderr_body_free`
- `expected_safe_relative_path_only`
- `expected_manifest_file_written`
- `expected_manifest_body_generated`
- `expected_reason_codes`
- `expected_failed_checks`
- `expected_summary_flags`
- `expected_forbidden_counts_zero`
- `expected_no_real_data`
- `expected_no_private_paths`
- `expected_no_absolute_paths`
- `expected_no_raw_rows`
- `expected_no_logits`
- `expected_no_raw_learner_text`

Expected results should be pass-only / count-only and should not include
written file contents.

## 9. Proposed Valid Cases

Minimum future valid cases:

- `valid/safe_metadata_flat_relative_output`
- `valid/safe_metadata_nested_relative_output`
- `valid/safe_metadata_output_parent_created`
- `valid/safe_metadata_no_output_no_file`
- `valid/safe_metadata_existing_output_rejected_after_precreate`

The `safe_metadata_existing_output_rejected_after_precreate` case is a valid
contract case because the validator expects safe refusal behavior. Its
expected category may be `usage_error_no_write`.

## 10. Proposed Invalid / Expected Failure Cases

Minimum future invalid or expected-failure cases:

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

Expected failures should count as matched cases when the CLI fails safely
without writing a file.

## 11. Expected Categories

Future expected categories:

- `pass_written`
- `pass_no_write`
- `usage_error_no_write`
- `fail_closed_no_write`
- `input_error`
- `mismatch`

The validator should distinguish an expected usage error from a validator
failure. A mismatch means the actual outcome did not match the fixture
contract.

## 12. Validation Phases For Future Validator

Recommended phases:

- Phase A: fixture contract static validation
- Phase B: isolated temp root creation
- Phase C: precondition setup, such as precreating output files
- Phase D: CLI execution
- Phase E: stdout/stderr safety scan
- Phase F: file existence and parse check
- Phase G: written file content safety scan
- Phase H: cleanup and residue check
- Phase I: result matching and summary generation

The validator should stop safely and return a body-free summary if any phase
cannot be completed.

## 13. Temp Root Rules

Future validator temp-root rules:

- use a test-created isolated temp root
- never use repository root for actual validator writes
- never write outside the temp root
- never record absolute temp path in summary
- expose safe relative paths only
- cleanup after each case
- cleanup after the full run
- remove no unrelated files
- turn cleanup failure into `input_error` or fail-closed according to phase
- never delete repository files

The summary may include residue counts, but not residue path listings.

## 14. Stdout/Stderr Rules

Future stdout/stderr rules:

- no body payload
- no request body
- no pointer body
- no expected body
- no manifest body
- no generated policy body
- no raw rows
- no logits
- no private paths
- no absolute paths
- category-only errors

The validator should scan both human and JSON summary modes if JSON output is
added later.

## 15. Written File Safety Rules

Future written file safety rules:

- JSON parseable
- allowed keys only
- required notices present
- safety flags present
- count summary present
- no raw rows
- no logits
- no private paths
- no absolute paths
- no raw learner text
- no request bodies
- no pointer bodies
- no expected bodies
- no generated policy body
- no manifest body
- no performance metric body

The validator may inspect file content internally. It must not print the
content.

## 16. Summary Contract For Future Validator

Future summary fields:

- `mode=isolated_write_validation`
- `validation_schema_version`
- `total_cases`
- `valid_cases`
- `invalid_cases`
- `pass_written_cases`
- `pass_no_write_cases`
- `usage_error_cases`
- `fail_closed_cases`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `residue_file_count`
- `body_payload_printed=false`
- `stdout_body_suppressed=true`
- `stderr_body_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_absolute_paths=true`
- `no_manifest_body=true`
- `no_generated_policy_body=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `path_policy_checked=true`
- `file_content_policy_checked=true`
- `cleanup_checked=true`
- `temp_root_isolated=true`
- `release_quality_ready=false`

The summary should be safe to store in docs as pass-only/count-only metadata.

## 17. Relationship To Existing Fixtures

- The no-write file writing fixture root remains unchanged.
- The isolated write fixture root should not replace the no-write fixture
  root.
- The artifact body fixture root remains unchanged.
- Isolated write cases may point to existing artifact body valid fixtures by
  ID.
- Docs should avoid copying request or pointer bodies.
- Fixture JSON creation should be a future step.

This contract should reduce duplication by referencing existing safe fixture
cases where possible.

## 18. Relationship To Implementation

Possible staging:

- Step369 can implement the validator against this contract, or refine the
  fixture contract before implementation.
- Step370 can create fixture JSON if fixtures are not created in Step369.
- Step371 can add Makefile target design.
- Release-quality integration should remain later.

The first validator implementation should remain standalone and should not be
added to release-quality in the same step.

## 19. Docs Safety Policy

Docs may include field names, schema names, case IDs, reason categories, and
policy descriptions.

Docs must not include:

- fixture JSON examples
- isolated write fixture JSON body examples
- written file body examples
- artifact body JSON examples
- artifact body payload examples
- raw logs
- private path examples
- output payloads
- request bodies
- pointer bodies
- expected bodies
- generated policy bodies
- manifest bodies
- raw rows
- logits
- raw learner text
- real data

## 20. Beginner-Friendly Explanation

A fixture contract is a written agreement about what future test files should
look like and what result each case should expect. It lets the validator be
implemented against a stable shape instead of guessing.

Creating the contract before the validator helps keep safety checks explicit:
which files exist, which fields are allowed, which failures are expected, and
which outputs must never appear.

A valid case can expect a usage error when the intended safe behavior is to
refuse a dangerous action. For example, precreating an output file should
prove that overwrite protection works.

An isolated temp root is a temporary area created for validation. It keeps
test writes away from repository fixtures and source files.

The static no-write fixture validator reads metadata contracts without
writing files. The future isolated temp validator will actually run file
writing in a controlled temporary area and then clean it up.

## 21. What This Does Not Do

- does not implement the validator
- does not create fixture JSON
- does not add a Makefile target
- does not add release-quality integration
- does not change workflow YAML
- does not change Python code/tests
- does not change fixture JSON
- does not implement manifest writer
- does not connect artifact writer CLI
- does not use real data
- does not compute metrics
- does not prove production readiness

## 22. Next Recommended Steps

- Step369: fixture JSON creation. Completed as a synthetic-only,
  metadata-only fixture root with 22 cases and 110 JSON files.
- Step370: isolated temp write validator implementation.
- Step371: Makefile target design for the isolated validator.
- Later: Makefile target implementation, release-quality integration design,
  wrapper integration, and remote/manual status marker.

## 23. Step369 Fixture JSON Creation Status

Step369 creates the fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_isolated_write_validation/`

The root contains 5 valid contract cases, 17 invalid / expected-failure
cases, and 110 JSON files. Each case contains the five contract files defined
by this document. The files are synthetic-only, metadata-only, and no-oracle.

Step369 does not implement the validator, does not add a Makefile target,
does not add release-quality integration, does not change workflow YAML, does
not change Python code/tests, does not write manifests, and does not connect
the artifact writer CLI.

Docs continue to avoid JSON body examples, artifact body payload examples,
raw logs, raw rows, logits, private paths, absolute local paths, raw learner
text, and real participant data.

## 24. Related Documents

- [Frozen policy generation artifact body isolated write validator Makefile target design](frozen_policy_generation_artifact_body_isolated_write_validator_makefile_target_design.md)
- [Frozen policy generation artifact body isolated temp write validation design](frozen_policy_generation_artifact_body_isolated_temp_write_validation_design.md)
- [Frozen policy generation artifact body file writing smoke target design](frozen_policy_generation_artifact_body_file_writing_smoke_target_design.md)
- [Frozen policy generation artifact body file writing implementation final design](frozen_policy_generation_artifact_body_file_writing_implementation_final_design.md)
- [Frozen policy generation artifact body file writing design](frozen_policy_generation_artifact_body_file_writing_design.md)
- [Frozen policy generation artifact body file writing fixture design](frozen_policy_generation_artifact_body_file_writing_fixture_design.md)
- [Frozen policy generation artifact body file writing fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing/README.md)
- [Frozen policy generation artifact body isolated write validation fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body_isolated_write_validation/README.md)
- [Learner-state frozen policy generation artifact body file writing fixture release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_body_file_writing_fixture_release_quality_remote_run_status.md)
- [Public release checklist](public_release_checklist.md)

## 25. Step371 Makefile Target Design Status

Step371 adds a docs-only design for a future standalone Makefile target that
runs the isolated write validator CLI. The proposed target validates the
Step369 fixture root through the isolated write validator CLI after module
availability is confirmed and expects `total_cases=22`, `matched_cases=22`,
and `residue_file_count=0`.

This does not implement a Makefile target, add release-quality integration,
change workflow YAML, change Python code/tests, change fixture JSON, write
manifests, connect artifact writer CLI, use real data, or compute metrics.

## 26. Step372 Validator Availability Reconciliation Status

Step372 restores and confirms the validator module and tests for this fixture
contract:

`learner_state.frozen_policy_generation_artifact_body_isolated_write_validation`

The validator runs this 22-case fixture root inside isolated temp roots,
checks write/no-write behavior, stdout/stderr safety, written-file safety,
cleanup, and residue count, and emits summary-only metadata. Step372 does
not change fixture JSON, does not add a Makefile target, does not add
release-quality integration, does not write manifests, and does not connect
artifact writer CLI.

## 27. Step373 Standalone Makefile Target Status

Step373 adds the standalone Makefile target that runs the isolated write
validator CLI against this fixture root:

`check-learner-state-frozen-policy-generation-artifact-body-isolated-write-validation`

The target validates the 22 synthetic metadata-only cases and expects 22
matched cases, 0 mismatches, 0 input errors, and 0 residue files. Step373
does not change fixture JSON, does not add release-quality integration, does
not write manifests, and does not connect artifact writer CLI.

## 28. Step374 Release-Quality Integration Design Status

Step374 adds a docs-only release-quality integration design for the standalone
isolated write validator target:

[Frozen policy generation artifact body isolated write release-quality integration design](frozen_policy_generation_artifact_body_isolated_write_release_quality_integration_design.md).

The design keeps this fixture root synthetic-only and metadata-only, requires
`residue_file_count=0`, and prohibits fixture JSON bodies, written file
content, artifact body payloads, private paths, absolute temp paths, raw rows,
logits, and raw learner text in release-quality logs or docs. Step374 does
not change fixture JSON and does not implement wrapper integration.

## 29. Step375 Release-Quality Wrapper Integration Status

Step375 integrates the standalone isolated write validator target into the
release-quality wrapper. The wrapper now runs the validator after the
no-write file-writing fixture validation target and before config/scoring
smoke checks.

The fixture contract remains unchanged: 5 valid cases, 17 invalid /
expected-failure cases, and 110 JSON files. Step375 does not change fixture
JSON, does not write manifests, does not connect artifact writer CLI, and does
not introduce real data or performance evaluation.
