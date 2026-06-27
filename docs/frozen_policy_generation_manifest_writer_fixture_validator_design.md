# Frozen Policy Generation Manifest Writer Fixture Validator Design

## 1. Purpose

This document designs a future static fixture validator for frozen policy
generation manifest writer fixtures.

This is not a validator implementation. It is not a manifest writer
implementation, fixture JSON creation step, release-quality integration,
runtime writer validation, manifest body generation, manifest file writing,
artifact writer CLI integration, performance evaluation, real-data readiness
claim, or production readiness claim.

The validator boundary is synthetic-only, metadata-only, and no-oracle.

## 2. Current State

- manifest writer boundary design exists
- manifest writer fixture contract design exists
- manifest writer fixture JSON root exists
- fixture root: `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer/`
- fixture count: 30 cases / 150 JSON files
- valid cases: 5
- invalid / expected-failure cases: 25
- manifest writer module does not exist
- manifest writer CLI does not exist
- manifest writer validator does not exist
- manifest body generation is not implemented
- manifest file writing is not implemented
- artifact writer CLI integration is not implemented

## 3. Proposed Validator Module

`learner_state.frozen_policy_generation_manifest_writer_fixture_validation`

The module should validate static fixture contracts only. It should not run a
manifest writer, write manifest files, or inspect generated manifest content.

## 4. Proposed CLI

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer_fixture_validation`

Proposed arguments:

- `--fixture-root`
  - default: `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer`
- `--fixture-case`
  - optional
  - safe relative selector only
  - rejects absolute, parent traversal, and empty selectors
- `--json`
  - body-free JSON summary
- `--help`

## 5. Proposed APIs / Dataclasses

Proposed APIs:

- `validate_manifest_writer_fixture_root(fixture_root)`
- `validate_manifest_writer_fixture_case(case_dir, expected_kind=None)`
- `summarize_manifest_writer_fixture_validation(summary)`

Proposed dataclasses:

- `ManifestWriterFixtureValidationSummary`
- `ManifestWriterFixtureCaseResult`
- `ManifestWriterFixtureValidationError`

## 6. Validation Phases

- Phase A: fixture root discovery
- Phase B: case directory structure validation
- Phase C: JSON parse and schema version validation
- Phase D: case ID consistency validation
- Phase E: expected category / status validation
- Phase F: static path-policy sentinel validation
- Phase G: static content-policy sentinel validation
- Phase H: reason code and expected result contract validation
- Phase I: summary-only output generation

This validator should be static. Manifest writer CLI execution and actual
manifest file writing should remain separate future steps.

## 7. Required Files Per Case

Each case directory must contain exactly:

- `case_metadata.json`
- `manifest_writer_request.json`
- `artifact_writer_result_pointer.json`
- `artifact_body_generation_result_pointer.json`
- `expected_manifest_writer_result.json`

Missing or extra files should be treated as input errors.

## 8. Schema Versions To Check

- `learner_state_frozen_policy_generation_manifest_writer_case_metadata_v0.1`
- `learner_state_frozen_policy_generation_manifest_writer_request_v0.1`
- `learner_state_frozen_policy_generation_manifest_writer_expected_result_v0.1`

The future result schema
`learner_state_frozen_policy_generation_manifest_writer_result_v0.1` can be
referenced by fixtures, but the static validator should not require an actual
writer result file.

## 9. Expected Counts

The fixture root should summarize to:

- `total_cases=30`
- `valid_cases=5`
- `invalid_cases=25`
- `pass_metadata_only_no_file_cases=3`
- `pass_manifest_file_written_cases=1`
- `usage_error_cases=11`
- `fail_closed_cases=15`
- `matched_cases=30`
- `mismatched_cases=0`
- `input_error_cases=0`

## 10. Expected Categories

- `pass_metadata_only_no_file`
- `pass_manifest_file_written`
- `usage_error_no_write`
- `fail_closed_no_write`
- `input_error`
- `mismatch`

## 11. Summary Fields

The future summary should be body-free and include:

- `mode=manifest_writer_fixture_validation`
- `validation_schema_version=learner_state_frozen_policy_generation_manifest_writer_fixture_validation_v0.1`
- `total_cases`
- `valid_cases`
- `invalid_cases`
- `pass_metadata_only_no_file_cases`
- `pass_manifest_file_written_cases`
- `usage_error_cases`
- `fail_closed_cases`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `reason_code_counts`
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
- `release_quality_ready=false`

## 12. Path Policy Checks

The validator should check:

- `manifest_out` is absent for no-file cases unless the expected category is
  no-write
- `manifest_out` is present only for explicit file-writing or expected
  no-write path-policy cases
- `manifest_output_root` is the safe sentinel root
  `tmp/frozen_policy_generation_manifest/`
- valid write paths are safe relative JSON selectors
- absolute path sentinel cases match `usage_error_no_write`
- home path sentinel cases match `usage_error_no_write`
- parent traversal sentinel cases match `usage_error_no_write`
- cloud/private marker sentinel cases match `usage_error_no_write`
- hidden private directory sentinel cases match `usage_error_no_write`
- unsafe filename sentinel cases match `usage_error_no_write`
- non-JSON extension sentinel cases match `usage_error_no_write`
- too-long path sentinel cases match `usage_error_no_write`
- overwrite without policy sentinel cases match `usage_error_no_write`
- summaries do not expose absolute resolved paths

The static validator should inspect sentinel selectors and expected outcomes,
not create or resolve real output paths.

## 13. Content Policy Checks

The validator should check:

- required notices are represented
- `include_*` forbidden body flags are false for valid pass cases
- invalid cases use safe sentinel flags or reason codes, not actual payloads
- no raw rows payload
- no logits payload
- no artifact body payload
- no generated policy body
- no manifest body nesting
- no request body
- no pointer body
- no expected body
- no private path payload
- no raw learner text content
- no performance proof
- no real participant data

The validator should treat field names and reason code names as safe metadata
when they are used only as contract labels.

## 14. Reason Code Handling

Invalid cases should have `allowed_failure_reason_codes` matching the expected
reason codes in `expected_manifest_writer_result.json`.

Valid pass cases should use no reason codes. Valid no-write rejection cases
may use a safe reason code such as `overwrite_without_policy` when the expected
category is `usage_error_no_write`.

`reason_code_counts` should be count-only. No body payloads, raw data, or path
values should be attached to reason codes.

## 15. Safe Selector Rules

Allowed examples:

- `valid/metadata_only_manifest_no_file`
- `invalid/generated_policy_body_leakage`

Reject:

- absolute selectors
- parent traversal
- empty selectors
- selectors with backslashes
- selectors with control characters
- selectors outside the `valid/` or `invalid/` roots

Unsafe selector rejection should exit as a usage error and must not print
fixture bodies.

## 16. Exit Codes

- `0`: all checked cases matched
- `1`: internal error
- `2`: usage error
- `3`: mismatch
- `4`: input error / malformed fixture

## 17. Relation To Future Writer Implementation

This validator only validates fixture contracts. It does not execute the
manifest writer, generate manifest bodies, or write manifest files.

Actual manifest writer validation will need a separate runtime validator or
runtime smoke later. Makefile and release-quality staging should first include
static fixture validation, then add runtime writer validation only after the
writer boundary is implemented and stable.

## 18. Future Tests For Implementation Step

Future tests should cover:

- root validates 30 cases
- total JSON count is 150
- valid count is 5 and invalid count is 25
- category counts match the expected 3 / 1 / 11 / 15 split
- matched cases are 30
- mismatched cases are 0
- input error cases are 0
- single valid case passes
- single invalid case passes
- unsafe fixture selector is rejected
- missing required file becomes input error
- malformed JSON becomes input error
- case ID mismatch becomes input error or mismatch
- schema mismatch behavior matches the expected contract
- reason code counts match
- human output is body-free
- JSON output is parseable and body-free
- summary contains no raw rows, logits, private paths, raw learner text, or
  absolute paths
- docs safety scan remains clean

## 19. Makefile / Release-Quality Staging

Proposed staging:

- Step382: implement static validator
- Step383: Makefile target design
- Step384: Makefile target implementation
- Step385: release-quality integration design
- Step386: wrapper integration

Runtime manifest writer implementation and manifest file writing should remain
later separate work.

## 20. Safety Interpretation

Static validator success would mean fixture contract integrity only.

It would not mean manifest writer correctness, manifest file output readiness,
artifact writer CLI integration, production readiness, real-data readiness, or
model performance.

## 21. Beginner-Friendly Explanation

A validator is a checker that reads fixture files and confirms they follow the
rules the project expects.

A static fixture validator checks the test data contract. A runtime writer
validator would run the future manifest writer and check behavior. They are
separate because a clean fixture contract should exist before runtime behavior
is tested.

The first validator only looks at fixture structure, schema names, case IDs,
expected categories, safe path-policy labels, safe content-policy labels, and
summary counts.

Output stays body-free so that validation can be logged safely. Reason code
counts stay count-only because reason codes should describe categories, not
carry payloads or private details.

## 22. Docs Safety Policy

Docs for this area may include field names, counts, case IDs, module names,
command shapes, and policy.

Docs must not include JSON body examples, manifest body examples, artifact
body payload examples, raw logs, private path examples, raw learner text, raw
rows, logits, real participant data, or performance metric bodies.

## 23. What This Does Not Do

- does not implement validator
- does not implement manifest writer
- does not write manifest files
- does not generate manifest bodies
- does not change fixture JSON
- does not change Makefile
- does not change release-quality wrapper
- does not change workflow YAML
- does not change Python code/tests
- does not connect artifact writer CLI
- does not use real data
- does not compute metrics
- does not prove production readiness

## 24. Next Recommended Steps

- implement the static fixture validator
- design and implement a standalone Makefile target
- design and integrate release-quality wrapper coverage
- later design and implement runtime manifest writer validation separately

## 25. Step382 Implementation Status

Step382 implements the static manifest writer fixture validator module and
focused tests:

- `python/learner_state/frozen_policy_generation_manifest_writer_fixture_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_manifest_writer_fixture_validation.py`

The validator reads the 30-case / 150-JSON synthetic metadata-only fixture
root, checks fixture structure, schema versions, case IDs, expected category
counts, path-policy sentinels, content-policy sentinels, reason-code
contracts, selector safety, and body-free summaries. The root summary reports
30 matched cases, zero mismatches, zero input errors, and
`release_quality_ready=false`.

This implementation does not implement the manifest writer, generate manifest
bodies, write manifest files, add a Makefile target, integrate
release-quality, change workflow YAML, change fixture JSON, connect artifact
writer CLI, use real data, compute metrics, or claim production readiness.

## 26. Related Documents

- [Frozen policy generation manifest writer boundary design](frozen_policy_generation_manifest_writer_boundary_design.md)
- [Frozen policy generation manifest writer fixture contract design](frozen_policy_generation_manifest_writer_fixture_contract_design.md)
- [Frozen policy generation manifest writer fixtures](../tests/fixtures/learner_state_frozen_policy_generation_manifest_writer/README.md)
- [Frozen policy generation artifact writer design](frozen_policy_generation_artifact_writer_design.md)
- [Frozen policy generation artifact body isolated temp write validation design](frozen_policy_generation_artifact_body_isolated_temp_write_validation_design.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)
