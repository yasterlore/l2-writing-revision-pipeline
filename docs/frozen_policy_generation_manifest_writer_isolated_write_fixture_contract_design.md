# Frozen Policy Generation Manifest Writer Metadata-Only Isolated Write Fixture Contract Design

## 1. Purpose

This document designs the future fixture contract for manifest writer
metadata-only isolated write validation.

It is a docs-only fixture contract design. It is not fixture JSON creation,
not isolated write validation implementation, not runtime file writing
implementation, not `--manifest-out` implementation, not release-quality
integration, not artifact writer CLI integration, and not a production
readiness claim.

The contract remains synthetic-only, metadata-only, no-oracle, body-free, and
count-safe.

## 2. Current State

- The static file writing fixture validator exists.
- The static file writing fixture validator is in release-quality.
- The file writing fixture validator remote status marker exists.
- The isolated write validation design exists.
- The isolated write fixture root does not exist.
- The isolated write validator does not exist.
- Runtime file writing does not exist.
- `--manifest-out` is not implemented.
- Manifest body generation does not exist.
- Artifact writer CLI integration does not exist.

## 3. Proposed Fixture Root

Future fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_isolated_write_validation/`

This Step420 design does not create that root.

## 4. Proposed Fixture Directory Layout

Top-level layout:

- `valid/`
- `invalid/`
- `README.md`

Each case directory should contain:

- `case_metadata.json`
- `isolated_write_request.json`
- `manifest_writer_request.json`
- `artifact_writer_result_pointer.json`
- `artifact_body_generation_result_pointer.json`
- `expected_isolated_write_result.json`

Docs may list required file names. Docs must not include fixture JSON bodies.

## 5. Schema Versions

Proposed future schema versions:

- `learner_state_frozen_policy_generation_manifest_writer_isolated_write_case_metadata_v0.1`
- `learner_state_frozen_policy_generation_manifest_writer_isolated_write_request_v0.1`
- `learner_state_frozen_policy_generation_manifest_writer_isolated_write_expected_result_v0.1`

The manifest writer request should remain aligned with the future
metadata-only file writing request schema. The validation result schema should
be:

`learner_state_frozen_policy_generation_manifest_writer_isolated_write_validation_v0.1`

## 6. Case Categories

Expected fixture categories:

- `pass_written`
- `pass_no_write`
- `usage_error`
- `fail_closed`

`input_error` and `mismatch` should remain validator output summary
categories, not expected fixture categories.

## 7. Proposed Valid Cases

Future valid cases:

- `valid/minimal_metadata_file_written`
- `valid/nested_metadata_file_written`
- `valid/metadata_file_with_artifact_body_reference`
- `valid/metadata_file_with_release_quality_reference`
- `valid/metadata_file_safe_ids_counts`
- `valid/metadata_no_file_existing_runtime_mode`

Expected valid split:

- 5 `pass_written` cases
- 1 `pass_no_write` case

The no-file case preserves the existing metadata-only no-file runtime mode as
a control case.

## 8. Proposed Invalid Cases

Future invalid or expected-failure cases:

- `invalid/unsafe_absolute_output_path`
- `invalid/unsafe_parent_traversal_output_path`
- `invalid/unsafe_output_path_outside_isolated_root`
- `invalid/unsafe_home_output_path`
- `invalid/unsafe_private_path_marker`
- `invalid/unsafe_cloud_marker`
- `invalid/unsafe_hidden_private_directory`
- `invalid/unsafe_output_path_extension`
- `invalid/unsafe_output_path_filename`
- `invalid/unsafe_output_path_too_long`
- `invalid/overwrite_without_policy`
- `invalid/manifest_body_requested`
- `invalid/artifact_body_payload_written`
- `invalid/generated_policy_body_written`
- `invalid/request_pointer_expected_body_written`
- `invalid/raw_rows_logits_private_or_raw_text_written`
- `invalid/expected_write_missing`
- `invalid/unexpected_write_occurred`
- `invalid/output_json_parse_failure_or_cleanup_failed`

Grouped cases are acceptable at this contract stage for related body leakage
or cleanup failures. Later implementation may split them if sharper coverage
is useful, but count math should be updated explicitly if that happens.

## 9. Proposed Total Counts

Initial contract counts:

- total_cases=25
- valid_cases=6
- invalid_cases=19
- json_files_per_case=6
- total_json_files=150
- pass_written_cases=5
- pass_no_write_cases=1
- usage_error_cases=14
- fail_closed_cases=5
- matched_cases=25
- mismatched_cases=0
- input_error_cases=0
- residue_file_count=0

## 10. Case Category Mapping

Usage-error cases:

- `unsafe_absolute_output_path`
- `unsafe_parent_traversal_output_path`
- `unsafe_output_path_outside_isolated_root`
- `unsafe_home_output_path`
- `unsafe_private_path_marker`
- `unsafe_cloud_marker`
- `unsafe_hidden_private_directory`
- `unsafe_output_path_extension`
- `unsafe_output_path_filename`
- `unsafe_output_path_too_long`
- `overwrite_without_policy`
- `expected_write_missing`
- `unexpected_write_occurred`
- `output_json_parse_failure_or_cleanup_failed`

Fail-closed cases:

- `manifest_body_requested`
- `artifact_body_payload_written`
- `generated_policy_body_written`
- `request_pointer_expected_body_written`
- `raw_rows_logits_private_or_raw_text_written`

Tradeoff: expected-write-missing, unexpected-write-occurred, and
output-json-parse-or-cleanup failures could be modeled as fail-closed because
they indicate unsafe runtime behavior. This contract keeps them as
usage-error-style expected failures to preserve the Step419 count shape and
to treat them as harness/output-contract violations. A future implementation
may split them into fail-closed cases if the validator can distinguish
runtime security failure from test setup failure without leaking paths or
file contents.

## 11. Isolated Write Request Contract

Field names only:

- `schema_version`
- `case_id`
- `isolated_root_policy`
- `allowed_output_root`
- `requested_manifest_out`
- `cleanup_policy`
- `allow_overwrite`
- `expect_write`
- `synthetic_notice`
- `no_oracle_notice`
- `non_proof_notice`

Rules:

- `pass_written` cases expect a write inside the isolated root.
- `pass_no_write` cases expect no write.
- Invalid path cases use synthetic sentinel reason markers, not real unsafe
  local paths.
- No real private path or absolute temp path is stored as fixture content.
- Required notices are present for non-notice-failure cases.

## 12. Manifest Writer Request Contract

Field names only:

- `schema_version`
- `request_id`
- `manifest_writer_mode`
- `include_manifest_body`
- `allow_manifest_file_writing`
- `manifest_out`
- `overwrite_policy`
- `synthetic_notice`
- `no_oracle_notice`
- `non_proof_notice`
- `validation_reference_ids`
- `release_quality_reference_ids`

Rules:

- `pass_written` cases use `metadata_only_file`.
- The `pass_no_write` case uses `metadata_only_no_file`.
- `include_manifest_body=false` for valid cases.
- `manifest_out` is a safe relative path for valid written cases.
- Invalid cases use sentinel values and reason codes, not real payloads.

## 13. Pointer Contracts

Artifact writer pointer field names:

- `schema_version`
- `pointer_id`
- `source_kind`
- `source_fixture_id`
- `safe_metadata_reference_id`
- `artifact_id`
- `manifest_id`
- `include_body_payload`
- `include_raw_rows`
- `include_private_paths`

Artifact body generation pointer field names:

- `schema_version`
- `pointer_id`
- `source_kind`
- `source_fixture_id`
- `safe_metadata_reference_id`
- `artifact_body_id`
- `artifact_body_available`
- `include_body_payload`
- `include_raw_rows`
- `include_private_paths`

Rules:

- Pointers are safe metadata only.
- No payloads are included.
- No private paths are included.
- No raw rows are included.

## 14. Expected Isolated Write Result Contract

Field names only:

- `schema_version`
- `case_id`
- `expected_category`
- `expected_writer_status`
- `expected_manifest_file_written`
- `expected_written_file_count`
- `expected_parseable_json_file_count`
- `expected_forbidden_field_count`
- `expected_stdout_body_printed`
- `expected_stderr_body_printed`
- `expected_residue_file_count`
- `expected_cleanup_status`
- `expected_reason_codes`
- `expected_failed_checks`
- `expected_safety_flags`
- `expected_safe_summary`

Rules:

- `pass_written` expects `written_file_count=1`.
- `pass_no_write` expects `written_file_count=0`.
- `usage_error` and `fail_closed` expect no final write.
- `expected_forbidden_field_count=0` for pass cases.
- `expected_stdout_body_printed=false`.
- `expected_stderr_body_printed=false`.
- `expected_residue_file_count=0`.
- No expected output file body is included.

## 15. Safe Isolated Root Policy

Allowed:

- test-controlled isolated temp root only
- normalized output path under isolated root
- `.json` extension
- safe filename or safe subdirectory
- cleanup after validation

Forbidden:

- repository root direct output
- normal project tmp output unless nested inside isolated root
- absolute user or home paths
- cloud/private marker paths
- parent traversal
- non-json extension
- unsafe filename
- too long path
- symlink-sensitive path
- public docs recording absolute temp paths

## 16. Output File Content Policy

Allowed in future written metadata-only file:

- schema/version
- `manifest_id`
- `artifact_id`
- `artifact_body_id` or safe reference
- `manifest_writer_mode`
- reference counts
- safety flags
- count summary
- safe summary

Forbidden:

- manifest body
- manifest JSON body nesting
- artifact body payload
- generated policy body
- request body
- pointer body
- expected result body
- raw rows
- logits/probabilities
- private paths
- absolute paths
- raw learner text
- `final_text`
- `observed_after_text`
- gold labels
- scoring feedback payload
- real participant data
- performance metric body

## 17. Stdout/Stderr Safety Policy

- stdout must be body-free summary only.
- stderr must be body-free errors only.
- file bodies must not be printed.
- manifest bodies must not be printed.
- raw JSON bodies must not be printed.
- request, pointer, and expected-result bodies must not be printed.
- payloads must not be printed.
- private paths and absolute temp paths must not be printed.
- raw learner text must not be printed.

## 18. Reason Code Taxonomy

Future validator should recognize:

- `unsafe_absolute_output_path`
- `unsafe_parent_traversal_output_path`
- `unsafe_output_path_outside_isolated_root`
- `unsafe_home_output_path`
- `unsafe_private_path_marker`
- `unsafe_cloud_marker`
- `unsafe_hidden_private_directory`
- `unsafe_output_path_extension`
- `unsafe_output_path_filename`
- `unsafe_output_path_too_long`
- `overwrite_without_policy`
- `manifest_body_requested`
- `manifest_body_written`
- `artifact_body_payload_written`
- `generated_policy_body_written`
- `request_body_written`
- `pointer_body_written`
- `expected_body_written`
- `raw_rows_written`
- `logits_dump_written`
- `private_path_written`
- `absolute_path_written`
- `raw_learner_text_written`
- `performance_metric_body_written`
- `expected_write_missing`
- `unexpected_write_occurred`
- `output_json_parse_failure`
- `cleanup_failed`
- `residue_file_count_mismatch`
- `runtime_writer_failure`
- `unsupported_manifest_writer_mode`
- `unknown_schema_version`

Reason codes should be emitted as names/counts only.

## 19. Future Validator Expectations

Future validator should check:

- required file set
- JSON parse
- schema versions
- case_id consistency
- category counts
- request/result contract
- safe isolated root policy
- pointer safe metadata policy
- expected result policy
- reason code matching
- stdout/stderr expected suppression fields
- cleanup/residue expected fields
- body-free output

## 20. Relation To Static File Writing Fixture Validator

The static file writing fixture validator validates non-write fixture
contracts. The isolated write fixture validator validates actual isolated
write scenarios.

Both are separate. Neither by itself is production readiness.

## 21. Relation To Runtime Implementation

Isolated write validation will need minimal runtime file writing support.
Runtime file writing remains separate. `--manifest-out` remains separate.

Future implementation should ensure writes happen only inside the isolated
root during validation.

## 22. Relation To Release-Quality

Future isolated write fixture validator target should be standalone first.
Release-quality integration should come later, followed by a remote marker.

This Step420 design does not change release-quality.

## 23. Relation To Artifact Writer / Artifact Body

Future fixtures should consume safe metadata pointers only.

They should not:

- run artifact writer CLI
- run artifact body generation CLI
- embed payloads
- imply artifact writer CLI integration

Artifact writer CLI integration remains separate.

## 24. Safety Interpretation

This fixture contract defines what future isolated write validation should
check. It does not prove isolated write works, runtime file writing works,
production readiness, or real-data readiness.

## 25. Beginner-Friendly Explanation

An isolated write fixture contract is the checklist for future tests that
write files only inside a temporary safe folder. It says which files each test
case will have, what kinds of pass and expected-failure cases exist, and what
the validator must check.

It uses a separate root from the static fixtures because static fixtures do
not write files, while isolated write fixtures are meant to exercise actual
write/no-write behavior. Keeping the roots separate makes future failures
easier to understand.

Both written and no-write valid cases are useful. Written cases check that a
safe metadata-only file can be produced. The no-write case checks that the
existing no-file mode remains valid.

Invalid path and body cases are needed because file writing is risky: unsafe
paths, body leakage, payload leakage, and cleanup failures must fail closed.
Output bodies stay out of fixtures and docs so the public record remains
metadata-only and safe.

## 26. What This Does NOT Do

- does not create isolated write fixtures
- does not implement isolated write validation
- does not implement runtime file writing
- does not implement `--manifest-out`
- does not modify runtime
- does not modify Makefile
- does not modify release-quality wrapper
- does not modify workflow YAML
- does not modify Python code/tests
- does not modify fixture JSON
- does not connect artifact writer CLI
- does not use real data
- does not compute metrics
- does not prove production readiness

## 27. Next Recommended Steps

- Step421: isolated write fixture JSON creation
- Step422: isolated write validation implementation
- Step423: Makefile target design
- Step424: Makefile target implementation
- Step425: release-quality integration design
- Step426: wrapper integration
- Step427: remote marker

## 28. Related Documents

- [Frozen policy generation manifest writer metadata-only isolated write validation design](frozen_policy_generation_manifest_writer_isolated_write_validation_design.md)
- [Frozen policy generation manifest writer metadata-only isolated write validation fixtures](../tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_isolated_write_validation/README.md)
- [Frozen policy generation manifest writer metadata-only file writing boundary design](frozen_policy_generation_manifest_writer_file_writing_boundary_design.md)
- [Frozen policy generation manifest writer metadata-only file writing fixture contract design](frozen_policy_generation_manifest_writer_file_writing_fixture_contract_design.md)
- [Frozen policy generation manifest writer metadata-only file writing fixture validator design](frozen_policy_generation_manifest_writer_file_writing_fixture_validator_design.md)
- [Learner-state frozen policy generation manifest writer file writing fixture release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_file_writing_fixture_release_quality_remote_run_status.md)
- [Frozen policy generation manifest writer boundary design](frozen_policy_generation_manifest_writer_boundary_design.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)

## 29. Step421 Fixture Creation Status

Step421 creates the synthetic-only, metadata-only isolated write validation
fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_isolated_write_validation/`

The root contains `README.md`, `valid/`, `invalid/`, 6 valid cases, 19
invalid / expected-failure cases, 25 total cases, 6 JSON files per case, 150
total JSON files, 5 `pass_written` cases, 1 `pass_no_write` case, 14
`usage_error` cases, 5 `fail_closed` cases, and expected residue count 0.

Step421 does not implement isolated write validation, runtime file writing,
`--manifest-out`, runtime writer changes, Makefile targets, release-quality
integration, workflow changes, Python code/tests, artifact writer CLI
integration, metrics, real-data use, or production readiness.

The fixture JSON bodies remain fixtures only and must not be copied into
public docs.

## 30. Step422 Validator Implementation Status

Step422 implements the isolated write validation module and focused tests:

- `python/learner_state/frozen_policy_generation_manifest_writer_isolated_write_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_manifest_writer_isolated_write_validation.py`

The validator checks this fixture root, performs actual writes only inside
validator-owned temporary isolated roots for `pass_written` cases, parses and
scans the written metadata-only JSON, cleans up residue, and emits body-free
count summaries.

It does not change fixture JSON, implement production-facing runtime file
writing, expose public `--manifest-out`, add Makefile targets, add
release-quality integration, change workflow YAML, connect artifact writer
CLI, use real data, compute metrics, or claim production readiness.
