# Frozen Policy Generation Manifest Writer Runtime Fixture Validator Design

## 1. Purpose

This document fixes the docs-only design for a future static validator for
frozen policy generation manifest writer runtime fixtures.

It is not validator implementation, not runtime writer implementation, not
fixture JSON creation, not release-quality integration, not performance
evaluation, and not a production readiness claim.

The validator design is synthetic-only, metadata-only, and no-oracle. It
defines the future validator responsibility, validation phases, CLI/API
shape, summary fields, path/content/no-oracle checks, reason-code handling,
safe selector rules, exit codes, implementation tests, and Makefile /
release-quality staging.

## 2. Current State

- runtime fixture root exists
- 31 case directories / 155 JSON files exist
- static manifest writer fixture validator exists
- static manifest writer fixture target is in release-quality
- runtime fixture validator does not exist
- manifest writer runtime does not exist
- manifest writer CLI does not exist
- manifest file writing does not exist
- artifact writer CLI integration does not exist

## 3. Proposed Validator Module

Proposed future module:

- `learner_state.frozen_policy_generation_manifest_writer_runtime_fixture_validation`

## 4. Proposed CLI

Proposed future CLI:

- `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer_runtime_fixture_validation`

## 5. Proposed CLI Arguments

- `--fixture-root`
  - default: `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime`
- `--fixture-case`
  - optional
  - safe relative selector only
  - example: `valid/metadata_only_minimal_no_file`
  - example: `invalid/manifest_body_requested`
- `--json`
  - body-free JSON summary
- `--help`

## 6. Proposed APIs / Dataclasses

Proposed future APIs:

- `validate_manifest_writer_runtime_fixture_root(fixture_root)`
- `validate_manifest_writer_runtime_fixture_case(case_dir, expected_kind=None)`
- `summarize_manifest_writer_runtime_fixture_validation(summary)`

Proposed future dataclasses:

- `ManifestWriterRuntimeFixtureValidationSummary`
- `ManifestWriterRuntimeFixtureCaseResult`
- `ManifestWriterRuntimeFixtureValidationError`

## 7. Validation Phases

- Phase A: fixture root discovery
- Phase B: case directory structure validation
- Phase C: required file set validation
- Phase D: JSON parse and schema version validation
- Phase E: case ID consistency validation
- Phase F: expected category / status validation
- Phase G: request policy validation
- Phase H: pointer policy validation
- Phase I: expected result contract validation
- Phase J: path policy sentinel validation
- Phase K: content policy sentinel validation
- Phase L: no-oracle / synthetic-only notice validation
- Phase M: reason code contract validation
- Phase N: summary-only output generation

The validator should not execute the manifest writer runtime. It should not
write manifest files.

## 8. Required Files Per Case

Each case must contain exactly:

- `case_metadata.json`
- `manifest_writer_request.json`
- `artifact_writer_result_pointer.json`
- `artifact_body_generation_result_pointer.json`
- `expected_manifest_writer_runtime_result.json`

## 9. Schema Versions To Check

- `learner_state_frozen_policy_generation_manifest_writer_runtime_case_metadata_v0.1`
- `learner_state_frozen_policy_generation_manifest_writer_runtime_request_v0.1`
- `learner_state_frozen_policy_generation_manifest_writer_runtime_expected_result_v0.1`

Pointer schemas should also be checked as fixture-internal contracts:

- `learner_state_frozen_policy_generation_manifest_writer_runtime_artifact_writer_result_pointer_v0.1`
- `learner_state_frozen_policy_generation_manifest_writer_runtime_artifact_body_generation_result_pointer_v0.1`

## 10. Expected Root Summary

Expected body-free root summary fields:

- `mode=manifest_writer_runtime_fixture_validation`
- `validation_schema_version=learner_state_frozen_policy_generation_manifest_writer_runtime_fixture_validation_v0.1`
- `total_cases=31`
- `valid_cases=5`
- `invalid_cases=26`
- `pass_metadata_only_no_file_cases=5`
- `usage_error_cases=8`
- `fail_closed_cases=18`
- `matched_cases=31`
- `mismatched_cases=0`
- `input_error_cases=0`
- `total_json_files=155`
- `json_files_per_case=5`
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
- `runtime_writer_executed=false`
- `manifest_file_written=false`
- `release_quality_ready=false`

## 11. Expected Categories

- `pass_metadata_only_no_file`
- `usage_error_no_write`
- `fail_closed_no_write`
- `input_error`
- `mismatch`

## 12. Request Policy Checks

Check field presence and value policy only. Do not print request bodies.

Fields to check:

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

- valid cases use `metadata_only_no_file`
- valid cases have `include_manifest_body=false`
- valid cases have `allow_manifest_file_writing=false`
- valid cases have no `manifest_out`
- valid cases include required notices
- invalid cases use safe sentinel flags / reason codes
- actual runtime writer execution is not required

## 13. Pointer Policy Checks

Check field presence and value policy only. Do not print pointer bodies.

Fields to check:

- `schema_version`
- `pointer_id`
- `source_kind`
- `source_fixture_id`
- `safe_metadata_reference_id`
- `include_body_payload=false`
- `include_raw_rows=false`
- `include_private_paths=false`

Rules:

- valid pointers never include body payloads
- valid pointers never include raw rows
- valid pointers never include private paths
- invalid pointers use safe sentinels, missing references, or malformed schema
  markers as expected
- artifact writer CLI is not executed

## 14. Expected Result Policy Checks

Check field presence and expected value policy only. Do not print expected
result bodies.

Fields to check:

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
- `expected_release_quality_ready`
- `expected_safety_flags`
- `expected_count_summary`
- `expected_safe_summary`

Rules:

- valid pass cases have no reason codes
- usage-error and fail-closed cases have the expected reason code
- body, payload, private path, and performance counts remain zero
- expected failures are represented by safe sentinel flags and reason codes
- `release_quality_ready=false`

## 15. Path Policy Checks

- default no manifest file writing
- valid cases do not write manifest files
- `manifest_out` absent for valid cases
- if `manifest_out` is present while file writing is disabled, expected
  category should be `usage_error_no_write`
- unsafe output path uses a safe sentinel only
- overwrite case uses a safe sentinel only
- no absolute resolved path in summaries
- no files written under `tmp/frozen_policy_generation_manifest`

## 16. Content Policy Checks

- no manifest body
- no manifest JSON body
- no artifact body payload
- no generated policy body
- no request body nesting
- no pointer body nesting
- no expected body nesting
- no raw rows
- no logits or probabilities
- no private paths
- no absolute paths
- no raw learner text
- no performance proof
- no real participant data

## 17. No-Oracle / Synthetic-Only Checks

- synthetic notice required except the expected `missing_synthetic_notice`
  case
- no-oracle notice required except the expected `missing_no_oracle_notice`
  case
- non-proof notice required except the expected `missing_non_proof_notice`
  case
- forbid `final_text`
- forbid `observed_after_text`
- forbid gold labels
- forbid expected action payload
- forbid scoring feedback payload
- forbid real participant IDs

## 18. Reason Code Handling

Expected reason codes:

- `missing_artifact_result_pointer`
- `missing_artifact_body_result_pointer`
- `malformed_artifact_result_pointer`
- `malformed_artifact_body_result_pointer`
- `unknown_artifact_writer_result_schema`
- `unknown_artifact_body_generation_result_schema`
- `generated_policy_body_leakage`
- `artifact_body_payload_leakage`
- `manifest_body_requested`
- `manifest_json_body_requested`
- `request_body_leakage`
- `pointer_body_leakage`
- `expected_body_leakage`
- `raw_rows_leakage`
- `logits_dump_leakage`
- `private_path_leakage`
- `absolute_path_leakage`
- `raw_learner_text_leakage`
- `performance_claim`
- `missing_synthetic_notice`
- `missing_no_oracle_notice`
- `missing_non_proof_notice`
- `unsafe_manifest_output_path`
- `overwrite_without_policy`
- `unsupported_artifact_writer_cli_integration`
- `real_data_marker`

Reason-code counts should be count-only and body-free.

## 19. Safe Selector Rules

Allow:

- `valid/metadata_only_minimal_no_file`
- `invalid/manifest_body_requested`

Reject:

- empty selector
- absolute selector
- parent traversal
- selector with backslash
- selector with control characters
- selector outside `valid/` or `invalid/`

## 20. Exit Codes

- `0`: all matched
- `1`: internal error
- `2`: usage error
- `3`: mismatch
- `4`: input error / malformed fixture

## 21. Future Tests For Implementation Step

Future implementation tests should cover:

- root validates 31 cases
- total JSON count 155
- valid cases = 5 and invalid cases = 26
- category counts are 5 / 8 / 18
- matched = 31, mismatch = 0, input error = 0
- single valid case passes
- single invalid usage-error case passes
- single invalid fail-closed case passes
- unsafe selector rejected
- missing required file returns input error
- malformed JSON returns input error
- schema mismatch behavior
- case ID mismatch behavior
- reason-code counts match
- JSON output is parseable and body-free
- human output is body-free
- no manifest files written
- `tmp/frozen_policy_generation_manifest` remains absent or residue-free
- no raw rows, logits, private paths, or absolute paths in summary
- release-quality still passes, while this runtime validator remains
  unintegrated until a later step

## 22. Relation To Manifest Writer Runtime

The runtime fixture validator validates fixture contracts only. It does not
execute the runtime writer, write manifest files, or call artifact writer CLI.

Runtime writer tests, runtime writer Makefile targets, and runtime writer
release-quality integration should remain separate.

## 23. Relation To Existing Static Manifest Writer Fixture Validator

The existing static manifest writer fixture validator checks the metadata
index fixture root. This future runtime fixture validator checks the runtime
request / pointer / expected-result fixture root.

Roots and target names must stay distinct. The runtime validator should not
replace the static validator.

## 24. Future Makefile / Release-Quality Staging

- Step393: runtime fixture validator implementation
- Step394: standalone Makefile target design
- Step395: standalone Makefile target implementation
- Step396: release-quality integration design
- Step397: wrapper integration
- Step398: remote/manual run record workflow design
- Step399: remote/manual run status marker

Runtime writer implementation remains separate unless explicitly scheduled.

## 25. Safety Interpretation

Future validator success would mean runtime fixture contract integrity only.
It would not mean runtime writer correctness, manifest file writing readiness,
artifact writer CLI integration, production readiness, model performance, or
real-data readiness.

## 26. Beginner-Friendly Explanation

A runtime fixture validator is a checker for the fixture files that will later
describe runtime behavior. It is different from a runtime writer: the
validator reads synthetic fixture contracts, while the writer would build a
metadata-only manifest result.

The validator looks at request, pointer, and expected-result files statically
because this is the lowest-risk way to confirm the contract before any runtime
code exists.

The summary stays body-free so logs and docs can show counts, categories, and
safety flags without exposing fixture bodies or payloads.

Manifest file writing stays out of scope because the initial runtime path is
metadata-only no-file mode.

## 27. Docs Safety Policy

- no JSON body examples
- no manifest body examples
- no request/pointer body examples
- no artifact body payload examples
- no raw logs
- no private path examples
- field names, counts, and policy only

## 28. What This Does Not Do

- does not implement validator
- does not execute runtime writer
- does not write manifest files
- does not change Makefile, wrapper, or workflow
- does not use real data
- does not compute metrics
- does not prove production readiness

## 29. Next Recommended Steps

- runtime fixture validator implementation
- Makefile target design / implementation
- release-quality integration
- later runtime writer design / implementation

## 30. Step393 Runtime Fixture Validator Implementation Status

Step393 implements the static runtime fixture validator module and focused
tests:

- `python/learner_state/frozen_policy_generation_manifest_writer_runtime_fixture_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_manifest_writer_runtime_fixture_validation.py`

The validator checks the 31-case / 155-JSON runtime fixture root with
body-free summaries. It validates fixture structure, schema versions, case
identity, expected categories, request policy, pointer policy, expected-result
policy, path/content/no-oracle sentinels, reason-code contracts, and safe
selectors.

The validator does not execute a manifest writer runtime, implement a
manifest writer CLI, generate manifest bodies, write manifest files, change
Makefile, change the release-quality wrapper, change workflow YAML, change
fixture JSON, connect artifact writer CLI, use real data, compute metrics, or
claim production readiness.

## 31. Step394 Makefile Target Design Status

Step394 adds the docs-only standalone Makefile target design:

[Frozen policy generation manifest writer runtime fixture validator Makefile target design](frozen_policy_generation_manifest_writer_runtime_fixture_validator_makefile_target_design.md).

The design proposes a future target for running this validator through
`make`, but it does not implement the Makefile target, add release-quality
integration, change workflow YAML, change Python code/tests, change fixture
JSON, execute a runtime writer, write manifest files, connect artifact writer
CLI, use real data, compute metrics, or claim production readiness.

## 32. Related Documents

- [Frozen policy generation manifest writer runtime fixture contract design](frozen_policy_generation_manifest_writer_runtime_fixture_contract_design.md)
- [Frozen policy generation manifest writer runtime fixtures](../tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime/README.md)
- [Frozen policy generation manifest writer runtime API design](frozen_policy_generation_manifest_writer_runtime_api_design.md)
- [Frozen policy generation manifest writer boundary design](frozen_policy_generation_manifest_writer_boundary_design.md)
- [Frozen policy generation manifest writer fixture validator design](frozen_policy_generation_manifest_writer_fixture_validator_design.md)
- [Frozen policy generation manifest writer runtime fixture validator Makefile target design](frozen_policy_generation_manifest_writer_runtime_fixture_validator_makefile_target_design.md)
- [Learner-state frozen policy generation manifest writer fixture release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_fixture_release_quality_remote_run_status.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)
