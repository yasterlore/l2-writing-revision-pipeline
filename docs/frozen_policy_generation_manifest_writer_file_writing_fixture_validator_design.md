# Frozen Policy Generation Manifest Writer Metadata-Only File Writing Fixture Validator Design

## 1. Purpose

This document defines the future validator design for the metadata-only
manifest writer file writing fixture root.

It is a docs-only design. It does not implement the validator, implement
runtime file writing, implement `--manifest-out`, add isolated write
validation, integrate release-quality, connect artifact writer CLI, or claim
production readiness.

The validator is intended to statically validate the existing synthetic-only,
metadata-only, no-oracle fixture root with body-free, count-only output.

## 2. Current State

- The file writing fixture root exists.
- The fixture root contains 39 cases and 195 JSON files.
- The fixture root contains 6 valid cases and 33 invalid / expected-failure
  cases.
- The fixture validator does not exist.
- Isolated write validation does not exist.
- Runtime file writing does not exist.
- `--manifest-out` is not implemented.
- The no-file manifest writer runtime still exists and is release-quality
  tracked.
- Manifest body generation does not exist.
- Artifact writer CLI integration does not exist.

## 3. Proposed Validator Module

`learner_state.frozen_policy_generation_manifest_writer_file_writing_fixture_validation`

The module should validate fixture contracts only. It must not write manifest
files, execute the runtime writer, perform isolated writes, run artifact writer
CLI, or inspect real data.

## 4. Proposed CLI

Future CLI entrypoint:

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer_file_writing_fixture_validation`

CLI arguments:

- `--fixture-root`
- `--fixture-case`
- `--json`
- `--help`

Default fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_file_writing`

The default output should be human-readable and body-free. The `--json` output
should be parseable and body-free.

## 5. Proposed APIs / Dataclasses

APIs:

- `validate_manifest_writer_file_writing_fixture_root(fixture_root)`
- `validate_manifest_writer_file_writing_fixture_case(case_dir, expected_kind=None)`
- `summarize_manifest_writer_file_writing_fixture_validation(summary)`

Dataclasses:

- `ManifestWriterFileWritingFixtureValidationSummary`
- `ManifestWriterFileWritingFixtureCaseResult`
- `ManifestWriterFileWritingFixtureValidationError`

The dataclasses should carry safe IDs, categories, reason code names, counts,
and boolean safety flags only.

## 6. Validation Phases

Future validation phases:

- Phase A: root discovery
- Phase B: directory layout
- Phase C: required file set
- Phase D: JSON parse
- Phase E: schema version
- Phase F: case ID consistency
- Phase G: category/status consistency
- Phase H: request contract policy
- Phase I: artifact writer pointer policy
- Phase J: artifact body generation pointer policy
- Phase K: expected result contract policy
- Phase L: safe path policy
- Phase M: file content policy
- Phase N: no-oracle / synthetic-only notices
- Phase O: reason code matching
- Phase P: summary/count aggregation
- Phase Q: body-free output audit

Each phase should fail closed for malformed fixtures and report only safe
reason code names and counts.

## 7. Required Files

Each case requires exactly:

- `case_metadata.json`
- `manifest_writer_request.json`
- `artifact_writer_result_pointer.json`
- `artifact_body_generation_result_pointer.json`
- `expected_manifest_writer_file_writing_result.json`

Missing or extra required files should be reported as input errors or
mismatches without printing file bodies.

## 8. Expected Root Summary

Expected root summary:

- `mode=manifest_writer_file_writing_fixture_validation`
- `validation_schema_version=learner_state_frozen_policy_generation_manifest_writer_file_writing_fixture_validation_v0.1`
- `total_cases=39`
- `valid_cases=6`
- `invalid_cases=33`
- `total_json_files=195`
- `json_files_per_case=5`
- `pass_metadata_file_written_cases=5`
- `pass_metadata_no_file_cases=1`
- `usage_error_cases=15`
- `fail_closed_cases=18`
- `matched_cases=39`
- `mismatched_cases=0`
- `input_error_cases=0`
- `content_suppressed=true`
- `manifest_body_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_absolute_paths=true`
- `no_artifact_body_payload=true`
- `no_generated_policy_body=true`
- `no_manifest_body_nesting=true`
- `no_request_body=true`
- `no_pointer_body=true`
- `no_expected_body=true`
- `no_performance_claims=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `non_proof_notice_checked=true`
- `path_policy_checked=true`
- `content_policy_checked=true`
- `file_writing_checked=true`
- `validator_wrote_files=false`
- `runtime_writer_executed=false`
- `isolated_write_executed=false`
- `release_quality_ready=false`

## 9. Category Policy

Expected fixture categories:

- `pass_metadata_file_written`
- `pass_metadata_no_file`
- `usage_error_no_write`
- `fail_closed_no_write`

`input_error` and `mismatch` are output summary categories only. They are not
expected fixture categories in the Step410 fixture root.

## 10. Request Policy Checks

Check these request field names:

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

- File-written valid cases use `metadata_only_file`.
- The no-file valid case uses `metadata_only_no_file`.
- File-written valid cases set `include_manifest_body=false`.
- File-written valid cases set `allow_manifest_file_writing=true`.
- File-written valid cases use safe `manifest_out`.
- The no-file valid case has no manifest output path.
- Invalid cases use sentinel values and expected reason codes.
- Fixtures must not include actual private paths or body payloads.

## 11. Pointer Policy Checks

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

- Valid pointers include no body payload.
- Valid pointers set `include_raw_rows=false`.
- Valid pointers set `include_private_paths=false`.
- Invalid leakage cases use sentinel fields, not real payloads.
- Pointers are safe metadata references only and do not imply CLI execution.

## 12. Expected Result Policy Checks

Check:

- `schema_version`
- `case_id`
- `expected_category`
- `expected_writer_status`
- `expected_manifest_writer_mode`
- `expected_reason_codes`
- `expected_failed_checks`
- `expected_manifest_body_available`
- `expected_manifest_file_written`
- `expected_manifest_output_path_available`
- `expected_written_file_count`
- `expected_release_quality_ready`
- `expected_safety_flags`
- `expected_count_summary`
- `expected_safe_summary`
- `expected_output_residue_count`

Rules:

- File-written valid cases expect `expected_manifest_file_written=true`.
- The no-file valid case expects `expected_manifest_file_written=false`.
- Invalid cases expect `expected_manifest_file_written=false`.
- Valid cases expect `expected_manifest_body_available=false`.
- Valid cases expect `expected_release_quality_ready=false`.
- All cases expect `expected_output_residue_count=0`.
- Expected result fixtures must not contain body content.

## 13. Safe Path Policy Checks

Allowed:

- safe root `tmp/frozen_policy_generation_manifest/`
- relative safe path
- `.json` extension
- safe nested directory
- normalized path remains under the safe root
- no overwrite unless explicitly allowed

Forbidden:

- absolute output path
- parent traversal
- home path
- cloud/private marker path
- hidden private directory
- local user path
- temp absolute path
- non-JSON extension
- too long path
- unsafe filename
- symlink-sensitive path
- overwrite without policy
- normalized path outside the safe root

The validator should never print raw unsafe path examples. It should report
only reason code names and counts.

## 14. File Content Policy Checks

Forbidden in fixtures:

- manifest body
- manifest JSON body nesting
- artifact body payload
- generated policy body
- request body
- pointer body
- expected body
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

The validator should count forbidden markers and fail closed without printing
fixture bodies.

## 15. Reason Code Taxonomy

The validator must recognize:

- `absolute_manifest_output_path`
- `parent_traversal_manifest_output_path`
- `manifest_output_path_outside_safe_root`
- `home_manifest_output_path`
- `hidden_private_manifest_directory`
- `cloud_marker_manifest_output_path`
- `non_json_manifest_extension`
- `unsafe_manifest_filename`
- `too_long_manifest_path`
- `overwrite_without_policy`
- `manifest_body_requested`
- `manifest_json_body_requested`
- `artifact_body_payload_leakage`
- `generated_policy_body_leakage`
- `request_body_leakage`
- `pointer_body_leakage`
- `expected_body_leakage`
- `raw_rows_leakage`
- `logits_dump_leakage`
- `private_path_leakage`
- `absolute_path_leakage`
- `raw_learner_text_leakage`
- `performance_claim_body`
- `missing_synthetic_notice`
- `missing_no_oracle_notice`
- `missing_non_proof_notice`
- `real_data_marker`
- `unsupported_artifact_writer_cli_integration`
- `unknown_schema_version`
- `malformed_artifact_result_pointer`
- `malformed_artifact_body_result_pointer`
- `missing_artifact_result_pointer`
- `missing_artifact_body_result_pointer`

Unknown reason codes should be mismatches.

## 16. Safe Selector Rules

Allowed selector shapes:

- `valid/metadata_file_minimal_safe_relative_json`
- `invalid/absolute_manifest_output_path`

Reject:

- empty selector
- absolute selector
- parent traversal
- backslash
- control characters
- selector outside the `valid/` or `invalid/` roots

Selector failures should return usage errors and body-free output.

## 17. Exit Codes

- `0`: all matched
- `1`: internal error
- `2`: usage error
- `3`: mismatch
- `4`: input error / malformed fixture

Exit codes should distinguish user invocation errors from malformed fixture
input and contract mismatches.

## 18. Future Implementation Tests

Design focused tests for:

- root validates 39 cases
- total JSON files is 195
- valid cases are 6 and invalid cases are 33
- category counts are 5 / 1 / 15 / 18
- matched cases are 39
- input error cases are 0
- single valid file-written case
- single valid no-file case
- single invalid usage-error path case
- single invalid fail-closed payload case
- missing required file
- malformed JSON
- schema mismatch
- case ID mismatch
- category mismatch
- unsafe selector
- reason code count matching
- body-free human output
- JSON output parseable and body-free
- `validator_wrote_files=false`
- `runtime_writer_executed=false`
- `isolated_write_executed=false`
- `tmp/frozen_policy_generation_manifest` residue count remains zero

## 19. Relation To Fixture JSON

The validator checks the existing Step410 fixtures.

It must not mutate fixture files. It must not write manifest files. It must not
run the runtime writer. It must not add or infer fixture body content.

## 20. Relation To Isolated Write Validation

The validator is static only.

Isolated write validation should come later and should perform actual writes
only in an isolated safe root. Do not combine static fixture validation and
isolated write validation in one step.

## 21. Relation To Runtime Implementation

The runtime is currently no-file only.

File writing runtime implementation remains later. `--manifest-out` remains
unimplemented. Validator success is not runtime file writing success.

## 22. Relation To Release-Quality

Future staging should add a standalone Makefile target for the validator, then
a release-quality integration for that validator.

This step does not change Makefile, the release-quality wrapper, or workflow
YAML.

## 23. Safety Interpretation

Validator success will mean fixture contract integrity only.

It will not prove file writing works. It will not prove output correctness. It
will not prove production readiness. It will not prove real-data readiness.

## 24. Beginner-Friendly Explanation

A validator is a checker for the fixture rulebook. It confirms that every case
has the right files, safe fields, expected category, reason codes, and summary
counts.

The validator design comes after fixture creation because the project now has
a concrete root to check. The design fixes what a future checker must verify
before code is written.

Static validation and isolated write validation are separate because they test
different risks. Static validation checks fixture integrity. Isolated write
validation later checks actual file writing behavior.

The validator does not write files because it should be a low-risk contract
checker. File writes need a separate isolated safe-root workflow.

## 25. What This Does Not Do

- does not implement the validator
- does not write files
- does not run the runtime writer
- does not implement `--manifest-out`
- does not change fixtures
- does not modify Makefile
- does not modify the release-quality wrapper
- does not modify workflow YAML
- does not connect artifact writer CLI
- does not use real data
- does not compute metrics

## 26. Step412 Implementation Status

Step412 implements the static validator module and focused tests:

- `python/learner_state/frozen_policy_generation_manifest_writer_file_writing_fixture_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_manifest_writer_file_writing_fixture_validation.py`

The validator checks the existing 39-case / 195-JSON fixture root with
body-free, count-only summaries. Its root summary records
`validator_wrote_files=false`, `runtime_writer_executed=false`,
`isolated_write_executed=false`, and `release_quality_ready=false`.

This implementation does not write manifest files, implement
`--manifest-out`, run isolated writes, execute the manifest writer runtime,
change fixture JSON, add a Makefile target, change the release-quality
wrapper, change workflow YAML, connect artifact writer CLI, use real data,
compute metrics, or claim production readiness.

## 27. Next Recommended Steps

- Step414: Makefile target implementation
- Step415: release-quality integration design
- Step416: wrapper integration
- Step417: remote marker
- later: isolated write validation
- later: runtime file writing implementation

## 28. Step413 Makefile Target Design Status

Step413 adds the docs-only standalone Makefile target design for running this
validator CLI:

[Frozen policy generation manifest writer metadata-only file writing fixture validator Makefile target design](frozen_policy_generation_manifest_writer_file_writing_fixture_validator_makefile_target_design.md).

The proposed future target is
`check-learner-state-frozen-policy-generation-manifest-writer-file-writing-fixtures`.
Step413 does not modify Makefile, add release-quality integration, change
workflow YAML, change Python code/tests, change fixture JSON, write manifest
files, implement `--manifest-out`, run isolated writes, connect artifact
writer CLI, use real data, compute metrics, or claim production readiness.

## 29. Step414 Makefile Target Implementation Status

Step414 implements the standalone Makefile target:

`check-learner-state-frozen-policy-generation-manifest-writer-file-writing-fixtures`

The target wraps the existing validator CLI root validation only. It is not
added to the release-quality wrapper in Step414. It does not change workflow
YAML, change Python code/tests, change fixture JSON, write manifest files,
implement `--manifest-out`, run isolated writes, connect artifact writer CLI,
use real data, compute metrics, or claim production readiness.

## 30. Related Documents

- [Frozen policy generation manifest writer metadata-only file writing fixture release-quality integration design](frozen_policy_generation_manifest_writer_file_writing_fixture_release_quality_integration_design.md)
- [Frozen policy generation manifest writer metadata-only file writing fixture validator Makefile target design](frozen_policy_generation_manifest_writer_file_writing_fixture_validator_makefile_target_design.md)
- [Frozen policy generation manifest writer metadata-only file writing fixtures](../tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_file_writing/README.md)
- [Frozen policy generation manifest writer metadata-only file writing fixture contract design](frozen_policy_generation_manifest_writer_file_writing_fixture_contract_design.md)
- [Frozen policy generation manifest writer metadata-only file writing boundary design](frozen_policy_generation_manifest_writer_file_writing_boundary_design.md)
- [Frozen policy generation manifest writer metadata-only file writing fixture validator implementation](../python/learner_state/frozen_policy_generation_manifest_writer_file_writing_fixture_validation.py)
- [Frozen policy generation manifest writer metadata-only file writing fixture validator tests](../python/learner_state/tests/test_frozen_policy_generation_manifest_writer_file_writing_fixture_validation.py)
- [Frozen policy generation manifest writer runtime implementation design](frozen_policy_generation_manifest_writer_runtime_implementation_design.md)
- [Learner-state frozen policy generation manifest writer runtime release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_runtime_release_quality_remote_run_status.md)
- [Frozen policy generation manifest writer boundary design](frozen_policy_generation_manifest_writer_boundary_design.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)

## 31. Step415 Release-Quality Integration Design Status

Step415 adds the docs-only release-quality integration design for the
standalone file writing fixture validator target:

[Frozen policy generation manifest writer metadata-only file writing fixture release-quality integration design](frozen_policy_generation_manifest_writer_file_writing_fixture_release_quality_integration_design.md).

The validator implementation remains unchanged. Step415 does not modify the
release-quality wrapper, change workflow YAML, change Makefile, change Python
code/tests, change fixture JSON, write manifest files, implement
`--manifest-out`, run isolated writes, connect artifact writer CLI, use real
data, compute metrics, or claim production readiness.

## 32. Step416 Wrapper Integration Status

Step416 adds the standalone file writing fixture validator target to the
release-quality wrapper:

`make check-learner-state-frozen-policy-generation-manifest-writer-file-writing-fixtures`

The validator implementation remains unchanged and static-only. Step416 does
not change workflow YAML, change Makefile, change Python code/tests, change
fixture JSON, write manifest files, implement `--manifest-out`, run isolated
writes, connect artifact writer CLI, use real data, compute metrics, or claim
production readiness.

## 33. Step417 Remote Run Record Workflow Design Status

Step417 adds the docs-only remote/manual run record workflow for a future
public-safe status marker:

[Frozen policy generation manifest writer metadata-only file writing fixture release-quality remote run record workflow](frozen_policy_generation_manifest_writer_file_writing_fixture_release_quality_remote_run_record_workflow.md).

The validator remains unchanged. Step417 does not create a status marker, run
remote workflows, change workflow YAML, change the wrapper, change Makefile,
change Python code/tests, change fixture JSON, write manifest files,
implement `--manifest-out`, run isolated writes, connect artifact writer CLI,
use real data, compute metrics, or claim production readiness.
