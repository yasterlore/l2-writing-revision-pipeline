# Frozen Policy Generation Artifact Writer Fixture Validator Design

This document designs a future validator for the frozen policy generation
artifact writer fixtures. It is docs-only. It does not implement the validator,
does not implement the artifact writer, does not generate artifact bodies, does
not generate generated policy bodies, does not generate manifest bodies, does
not write files, does not compute metrics, and does not claim real-data
readiness.

The validator boundary is synthetic-only and metadata-only. Documentation must
stay at schema/key level and must not copy fixture JSON bodies, request bodies,
pointer bodies, expected result bodies, policy bodies, artifact bodies,
manifest bodies, raw rows, logits, private paths, or raw learner text.

## 1. Purpose

The purpose of this document is to define the future artifact writer fixture
validator boundary:

- fixture discovery
- case loading
- metadata-only dataclasses
- public validation APIs
- root and case validation flow
- forbidden key and safe marker scans
- expected result metadata matching
- safe root summaries
- future CLI, Makefile, release-quality, and status-marker staging

This is not:

- validator implementation
- artifact writer implementation
- artifact body generation
- generated policy body generation
- manifest body generation
- file writing
- performance evaluation
- real-data readiness evidence

## 2. Current State

Currently:

- artifact writer design exists:
  [Frozen policy generation artifact writer design](frozen_policy_generation_artifact_writer_design.md)
- artifact writer fixture design exists:
  [Frozen policy generation artifact writer fixture design](frozen_policy_generation_artifact_writer_fixture_design.md)
- artifact writer fixture root exists:
  [Frozen policy generation artifact writer fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/README.md)
- artifact writer fixture validator does not exist
- artifact writer implementation does not exist
- artifact writer CLI does not exist
- artifact writer validator Makefile target does not exist
- artifact writer release-quality integration does not exist

The current fixture root contains:

- valid cases: 3
- invalid cases: 14
- total cases: 17
- case JSON files: 51
- root README: yes

## 3. Proposed Module

Recommended module:

`python/learner_state/frozen_policy_generation_artifact_writer_fixture_validation.py`

Rationale:

- clearly validates artifact writer fixtures rather than implementing the
  writer
- matches the naming style of existing frozen policy generation fixture
  validators
- fits a future `python -m learner_state...` CLI entrypoint
- keeps artifact writer runtime logic separate from fixture contract checking

## 4. Proposed Dataclasses

### `ArtifactWriterFixtureCase`

Metadata-only representation of one fixture case.

Proposed fields:

- `case_id`
- `case_category`
- `case_dir`
- `request_metadata`
- `generator_result_pointer_metadata`
- `expected_result_metadata`
- `request_schema_version`
- `pointer_schema_version`
- `expected_schema_version`
- `result_schema_version`

The dataclass should keep parsed metadata only. It should not store raw body
payloads in summaries.

### `ArtifactWriterFixtureValidationResult`

Safe result for one case validation.

Proposed fields:

- `case_id`
- `case_category`
- `matched`
- `writer_status`
- `reason_codes`
- `failed_checks`
- `input_error`
- `mismatch_reasons`
- `safety_summary`
- `comparison_result`

### `ArtifactWriterFixtureRootValidationResult`

Safe root-level summary.

Proposed fields:

- `mode`
- `total_cases`
- `valid_cases`
- `invalid_cases`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `reason_code_counts`
- `case_results`
- `safety_summary`
- `validation_schema_version`

### `ArtifactWriterFixtureSafetySummary`

Metadata-only safety flags for a case or root summary.

Proposed fields:

- `content_suppressed`
- `no_raw_rows`
- `no_logits_dump`
- `no_private_paths`
- `no_performance_claims`
- `synthetic_only_checked`
- `no_oracle_checked`
- `artifact_policy_checked`
- `body_suppression_checked`
- `file_writing_checked`
- `manifest_body_suppression_checked`
- `output_path_safety_checked`

### `ArtifactWriterFixtureInputError`

Safe input error for unreadable or malformed fixtures.

Proposed fields:

- `case_id`
- `error_code`
- `safe_message`
- `file_role`
- `content_suppressed`

The safe message should not include file bodies, private paths, or raw content.

### `ArtifactWriterFixtureComparisonResult`

Expected-result comparison metadata.

Proposed fields:

- `matched`
- `compared_fields`
- `mismatched_fields`
- `missing_fields`
- `extra_forbidden_fields`
- `reason_code_match`
- `failed_check_match`
- `artifact_flags_match`
- `safety_flags_match`
- `count_summary_match`

## 5. Proposed Public APIs

### `discover_artifact_writer_fixture_cases(fixture_root)`

Responsibility:

- discover `valid/*` and `invalid/*` case directories
- return stable sorted case references
- avoid reading file bodies in the summary

Input:

- fixture root path

Output:

- list of case directories or safe case descriptors

Failure behavior:

- return an input error for missing root or malformed layout

### `load_artifact_writer_fixture_case(case_dir)`

Responsibility:

- require the three case files
- parse request metadata
- parse generator result pointer metadata
- parse expected result metadata
- attach safe case category and case ID

Input:

- case directory

Output:

- `ArtifactWriterFixtureCase`

Failure behavior:

- produce `ArtifactWriterFixtureInputError` for missing files or malformed JSON
- do not print file contents

### `load_expected_artifact_writer_result(case_dir)`

Responsibility:

- load expected result metadata for focused comparisons
- validate expected result schema labels

Input:

- case directory

Output:

- metadata dictionary or expected-result dataclass

Failure behavior:

- safe input error for malformed or missing expected result file

### `validate_artifact_writer_fixture_case(case)`

Responsibility:

- validate schema versions
- validate required fields
- validate valid/invalid category expectations
- validate artifact flags
- validate safety flags
- validate count-only zero constraints
- validate safe marker policy

Input:

- `ArtifactWriterFixtureCase`

Output:

- `ArtifactWriterFixtureValidationResult`

Failure behavior:

- fail closed as mismatch or input error
- no artifact writer execution
- no file writing

### `compare_artifact_writer_fixture_to_expected(case)`

Responsibility:

- compare request and pointer metadata to expected result metadata
- check expected status, reason codes, failed checks, IDs, flags, and counts
- confirm invalid cases map to the exact expected reason code

Input:

- `ArtifactWriterFixtureCase`

Output:

- `ArtifactWriterFixtureComparisonResult`

Failure behavior:

- record mismatch metadata only

### `validate_artifact_writer_fixture_root(fixture_root)`

Responsibility:

- discover cases
- validate all cases
- aggregate root counts
- aggregate reason code counts
- return a safe root summary

Input:

- fixture root path

Output:

- `ArtifactWriterFixtureRootValidationResult`

Failure behavior:

- root-level input error when discovery fails
- case-level input errors for malformed cases

### `summarize_artifact_writer_fixture_validation_result(result)`

Responsibility:

- convert case or root results to safe human/JSON serializable summaries
- suppress fixture contents and body payloads

Input:

- case or root validation result

Output:

- metadata-only summary dictionary

Failure behavior:

- never include raw body payloads in fallback messages

### `scan_artifact_writer_fixture_for_forbidden_markers(case)`

Responsibility:

- recursively scan request, pointer, and expected result metadata
- detect forbidden keys, unsafe path patterns, raw log markers, and body marker
  misuse
- allow only explicitly designed safe marker booleans for invalid cases

Input:

- `ArtifactWriterFixtureCase`

Output:

- safe scan summary with reason codes and failed checks

Failure behavior:

- fail closed as mismatch when a forbidden payload or unsafe marker appears

## 6. Validation Flow

### Root Flow

The root validator should:

1. Discover `valid/*` and `invalid/*` case directories.
2. Require exactly three files per case.
3. Parse all JSON files.
4. Validate schema version values.
5. Validate required fields.
6. Validate expected status and reason codes.
7. Scan forbidden keys and body markers.
8. Compare request and pointer metadata to expected result metadata.
9. Summarize total, matched, mismatched, and input error counts.
10. Return a safe root summary.

### Case Flow

The case validator should:

1. Load request metadata.
2. Load generator result pointer metadata.
3. Load expected result metadata.
4. Check category: valid or invalid.
5. Validate allowed metadata.
6. Scan forbidden payload markers.
7. Validate expected artifact flags.
8. Validate expected safety flags.
9. Validate count summary body, raw row, logits, private path, and written file
   counts are zero.
10. Validate invalid cases fail with the exact expected reason code.
11. Avoid artifact writer execution.
12. Avoid file writing.

## 7. Expected Valid Behavior

Valid cases should match when:

- `writer_status=pass`
- reason codes are empty
- failed checks are empty
- `safe_summary=metadata_only_artifact_writer_result`
- artifact flags are safe
- safety flags are true
- body, raw row, logits, private path, generated artifact, written file, and
  manifest body counts are zero
- no forbidden markers appear
- no raw rows, logits, private paths, raw learner text, artifact bodies,
  generated policy bodies, or manifest bodies appear

## 8. Expected Invalid Behavior

Invalid cases should match when:

- `writer_status=fail`
- reason codes contain the exact expected reason code
- failed checks contain the expected failed check
- `safe_summary=fail_closed_metadata_only_artifact_writer_result`
- artifact flags remain safe
- safety flags remain true
- output body, raw row, logits, private path, generated artifact, written file,
  and manifest body counts remain zero
- no forbidden body output appears
- the trigger is represented only by a safe marker field or safe label

An invalid fixture can be a matched fixture. Matched means the expected
fail-closed contract is represented correctly. It does not mean the writer
would pass that unsafe input.

## 9. Forbidden Marker Scan

The validator should detect or prohibit these keys and payload families:

- `generated_policy_body`
- `generated_artifact_body`
- `artifact_body`
- `manifest_body`
- `policy_body`
- `raw_rows`
- `logits`
- `probabilities`
- `raw_learner_text`
- `observed_after_text`
- `final_text`
- `gold_label`
- `expected_action`
- `scoring_feedback_payload`
- `request_body`
- `pointer_body`
- `expected_result_body`
- `private_path`
- `absolute_path`
- `real_participant_data`
- `calibration_body`
- `label_body`
- `split_body`
- `performance_metrics`
- unsafe path patterns
- raw log markers
- GitHub Actions log group markers
- copied workflow log timestamps

The scan should be recursive across request, pointer, and expected result
metadata.

## 10. Safe Marker Policy

Invalid fixtures may use safe marker booleans to express the intended unsafe
condition without including the unsafe payload.

Allowed safe marker examples:

- `generated_policy_body_present=true`
- `generated_artifact_body_present=true`
- `manifest_body_present=true`
- `raw_rows_present=true`
- `logits_dump_present=true`
- `private_path_marker_present=true`
- `non_synthetic_marker_present=true`
- `no_oracle_violation_marker_present=true`
- `performance_claim_marker_present=true`

Policy:

- safe marker booleans must not include real body payloads
- safe marker booleans must map to expected reason codes
- expected results must not include the forbidden body itself
- private path cases must not include actual absolute or private paths
- logits and raw row cases must not include arrays or numeric dumps
- marker labels must be synthetic-only and body-free

## 11. Expected Reason Code Matching

The validator should check exact mapping for the current invalid cases:

- `generated_policy_body_leakage`
- `generated_artifact_body_leakage`
- `manifest_body_leakage`
- `raw_rows_carryover`
- `logits_dump_carryover`
- `private_path_output`
- `artifact_file_writing_not_allowed`
- `manifest_file_writing_not_allowed`
- `non_synthetic_input`
- `no_oracle_violation`
- `scoring_feedback_violation`
- `performance_claim_in_artifact`
- `missing_required_field`
- `unknown_schema_version`

Each invalid case should have the same value in the expected reason code and
expected failed check unless a later design explicitly changes that mapping.

## 12. Root Summary Output

Allowed root summary fields:

- `mode=fixture_root`
- `total_cases`
- `valid_cases`
- `invalid_cases`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `reason_code_counts`
- `content_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_performance_claims=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `artifact_policy_checked=true`
- `body_suppression_checked=true`
- `file_writing_checked=true`
- `manifest_body_suppression_checked=true`
- `output_path_safety_checked=true`
- `validation_schema_version`

Forbidden root summary content:

- request body
- pointer body
- expected result body
- artifact body
- policy body
- generated policy body
- manifest body
- raw rows
- logits
- private paths
- raw learner text
- performance metric body

Recommended validation schema version:

`learner_state_frozen_policy_generation_artifact_writer_fixture_validation_v0.1`

## 13. Expected Aggregate Counts

Given the Step302 fixtures, the future root validator should expect:

- `total_cases=17`
- `valid_cases=3`
- `invalid_cases=14`
- `matched_cases=17`
- `mismatched_cases=0`
- `input_error_cases=0`

These are contract counts, not writer runtime counts.

## 14. Relation To Artifact Writer Implementation

The fixture validator should not run the artifact writer initially.

The validator checks only fixture contract correctness:

- expected status metadata
- reason-code alignment
- flag safety
- count-only zero constraints
- forbidden marker policy
- required files and schema versions

The future artifact writer implementation can later use the same expected
result contract for compatibility tests. Future end-to-end writer tests should
be designed separately after a writer skeleton exists.

The fixture validator is not artifact quality evaluation.

## 15. Relation To Generator Scaffold Validators

The artifact writer fixture validator should mirror the generator scaffold
fixture validator style:

- body-free summaries
- deterministic case discovery
- root and single-case validation
- exact reason-code matching
- safe invalid marker allowance
- no raw rows
- no logits
- no private paths
- no body payloads in output

It should reference generator scaffold outputs only through safe generator
result IDs and pointer metadata. It should not depend on generator scaffold raw
bodies, request bodies, pointer bodies, or expected result bodies.

## 16. Future CLI Design

Do not implement now.

Likely entrypoint:

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_fixture_validation`

Likely arguments:

- `--fixture-root`
- `--fixture-case`
- `--json`
- `--help`

Recommended exit codes:

- `0`: all selected cases matched
- `2`: usage error or input error
- `3`: mismatch
- `1`: unexpected internal error

The CLI should output safe human summaries by default and deterministic safe
JSON summaries with `--json`.

## 17. Future Makefile Target

Do not add now.

Proposed target:

`check-learner-state-frozen-policy-generation-artifact-writer-fixtures`

Proposed command:

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer`

Proposed help text:

`check-learner-state-frozen-policy-generation-artifact-writer-fixtures  Validate frozen policy generation artifact writer fixtures`

## 18. Future Release-Quality Integration

Do not integrate now.

Future release-quality integration should happen only after:

- validator implementation
- validator tests
- validator CLI
- Makefile target
- no-body-leakage review

Suggested placement:

- after generator scaffold runtime smoke
- before future artifact writer runtime smoke, if that later exists

Success would mean the artifact writer fixture contract matched. It would not
mean artifact writer implementation quality, artifact generation quality,
policy quality, model performance, or real-data readiness.

## 19. Status Marker Future

A future remote/manual Release Quality marker may record:

- `total_cases=17`
- `matched_cases=17`
- `mismatched_cases=0`
- `input_error_cases=0`
- reason-code counts
- safety flags
- validation schema version

It must not record:

- raw logs
- request bodies
- pointer bodies
- expected result bodies
- artifact bodies
- policy bodies
- generated policy bodies
- manifest bodies
- raw rows
- logits
- private paths
- raw learner text
- performance metrics

## 20. Docs Safety Policy

Documentation should include only schema/key-level descriptions and safe IDs.

Documentation must not include:

- JSON fixture bodies
- raw logs
- request body
- pointer body
- expected result body
- artifact body
- policy body
- manifest body
- raw rows
- logits
- private paths
- raw learner text

## 21. Proposed Next Steps

Recommended next steps:

1. Step307: Makefile target design.
2. Later: Makefile target implementation, release-quality integration design,
   wrapper integration, and public-safe remote status marker.

## 22. Beginner-Friendly Explanation

A validator is a small checker. It reads fixture metadata and decides whether
the fixture files match the contract.

Fixture contract matching means the validator checks that the fixture says the
same safe thing in all expected places: status, reason codes, failed checks,
IDs, flags, and count-only summaries.

A forbidden marker scan checks for dangerous or out-of-scope payloads, such as
raw rows, logits, private paths, raw learner text, or artifact bodies. Invalid
fixtures may use safe marker booleans to say "this unsafe thing is being
tested" without including the unsafe thing itself.

The validator should not run the writer yet because this step checks fixture
quality, not artifact writer behavior.

Invalid fixtures can be matched because they are expected to fail closed. A
matched invalid fixture means the fixture correctly describes the safe failure.

Matched and pass are different. Matched means the fixture contract is correct.
Pass means a valid artifact writer scenario is expected to succeed.

## 23. What This Does NOT Do

This document does not:

- implement the validator
- execute the writer
- generate artifact bodies
- generate generated policy bodies
- generate manifest bodies
- write artifact files
- write manifest files
- compute metrics
- evaluate performance
- use real data
- claim production readiness

## 24. Step304 Validator Implementation Status

Step304 implements the metadata-only artifact writer fixture validator module:

`python/learner_state/frozen_policy_generation_artifact_writer_fixture_validation.py`

It also adds focused validator tests:

`python/learner_state/tests/test_frozen_policy_generation_artifact_writer_fixture_validation.py`

The implementation validates the Step302 fixture contract only. It discovers
the 17 synthetic fixture cases, checks required files and schema metadata,
allows safe marker booleans for expected invalid cases, scans for forbidden
body/payload keys, compares expected metadata summaries, and returns a
body-free root summary.

Step304 does not implement an artifact writer, artifact writer CLI, Makefile
target, release-quality wrapper integration, workflow change, artifact body
generation, generated policy body generation, manifest body generation,
artifact file writing, manifest file writing, metric computation, performance
evaluation, real-data use, or production readiness.

## 25. Step305 Fixture Validator CLI Design Status

Step305 designs the future CLI for this validator:
[Frozen policy generation artifact writer fixture validator CLI design](frozen_policy_generation_artifact_writer_fixture_validator_cli_design.md).

The validator implementation remains unchanged. Step305 does not implement CLI
code, execute an artifact writer, add a Makefile target, integrate
release-quality, change workflow YAML, generate artifact bodies, generate
generated policy bodies, generate manifest bodies, or write files.

## 26. Step306 Fixture Validator CLI Implementation Status

Step306 implements the CLI described by the Step305 design in the validator
module itself. It provides root and case modes, safe human/JSON summaries, and
exit codes for matched, usage/input-error, mismatch, and unexpected internal
error outcomes.

The validator remains metadata-only. Step306 does not execute an artifact
writer, add a Makefile target, integrate release-quality, change workflow
YAML, generate artifact bodies, generate generated policy bodies, generate
manifest bodies, or write files.

## 27. Step307 Makefile Target Design Status

Step307 designs the future standalone Makefile target for the implemented CLI:
[Frozen policy generation artifact writer fixture validator Makefile target design](frozen_policy_generation_artifact_writer_fixture_validator_makefile_target_design.md).

This keeps the validator and CLI unchanged. It does not implement a Makefile
target, integrate release-quality, change workflow YAML, change fixture JSON,
execute an artifact writer, generate artifact bodies, generate generated policy
bodies, generate manifest bodies, or write files.

## 28. Step308 Makefile Target Implementation Status

Step308 implements the standalone Makefile target:

`check-learner-state-frozen-policy-generation-artifact-writer-fixtures`

The target invokes the metadata-only validator CLI over the Step302 fixture
root. The validator remains fixture-contract-only. Step308 does not integrate
release-quality, change workflow YAML, change Python code, change tests, change
fixture JSON, execute an artifact writer, generate artifact bodies, generate
generated policy bodies, generate manifest bodies, or write files.

## 29. Step309 Release-Quality Integration Design Status

Step309 designs future release-quality wrapper integration for the standalone
artifact writer fixture validator target:
[Frozen policy generation artifact writer fixture release-quality integration design](frozen_policy_generation_artifact_writer_fixture_release_quality_integration_design.md).

The validator remains unchanged and still validates fixture contracts only.
Step309 does not modify wrapper scripts, workflow YAML, Makefile target
behavior, Python code, tests, fixture JSON, artifact writer implementation,
artifact body generation, generated policy body generation, manifest body
generation, file writing, metrics, real-data use, or production readiness.

## 30. Step310 Wrapper Integration Status

Step310 adds the artifact writer fixture validator Makefile target to
`scripts/check_release_quality.sh`. The validator remains unchanged and still
checks fixture contracts only. The wrapper now runs the target after generator
scaffold runtime smoke and before config and scoring smoke checks.

Step310 does not change workflow YAML, Makefile target behavior, Python code,
tests, fixture JSON, artifact writer implementation, artifact body generation,
generated policy body generation, manifest body generation, file writing,
metrics, real-data use, or production readiness.

## 31. Step311 Remote Run Record Workflow Design Status

Step311 designs the future public-safe remote/manual Release Quality recording
workflow:
[Frozen policy generation artifact writer fixture release-quality remote run record workflow](frozen_policy_generation_artifact_writer_fixture_release_quality_remote_run_record_workflow.md).

The validator remains unchanged. Step311 does not create a status marker,
change workflow YAML, change wrapper scripts, change Makefile behavior, change
Python code or tests, change fixture JSON, execute an artifact writer,
generate artifact bodies, generate generated policy bodies, generate manifest
bodies, write files, compute metrics, evaluate performance, use real data, or
claim production readiness.

## 32. Step312 Remote Run Status Marker

Step312 creates the public-safe remote/manual Release Quality status marker:
[Learner-state frozen policy generation artifact writer fixture release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_writer_fixture_release_quality_remote_run_status.md).

The marker records that the artifact writer fixture validator target matched
17 metadata-only cases in the remote/manual Release Quality run. It does not
record fixture JSON bodies, request/pointer/expected bodies, artifact bodies,
manifest bodies, raw rows, logits, private paths, raw learner text, or
performance metric bodies.

## Related Documents

- [Learner-state frozen policy generation artifact writer fixture release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_writer_fixture_release_quality_remote_run_status.md)
- [Frozen policy generation artifact writer fixture release-quality remote run record workflow](frozen_policy_generation_artifact_writer_fixture_release_quality_remote_run_record_workflow.md)
- [Frozen policy generation artifact writer fixture release-quality integration design](frozen_policy_generation_artifact_writer_fixture_release_quality_integration_design.md)
- [Frozen policy generation artifact writer fixture validator Makefile target design](frozen_policy_generation_artifact_writer_fixture_validator_makefile_target_design.md)
- [Frozen policy generation artifact writer fixture validator CLI design](frozen_policy_generation_artifact_writer_fixture_validator_cli_design.md)
- [Frozen policy generation artifact writer fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/README.md)
- [Frozen policy generation artifact writer fixture design](frozen_policy_generation_artifact_writer_fixture_design.md)
- [Frozen policy generation artifact writer design](frozen_policy_generation_artifact_writer_design.md)
- [Frozen policy generation artifact policy design](frozen_policy_generation_artifact_policy_design.md)
- [Frozen policy generation generator scaffold skeleton design](frozen_policy_generation_generator_scaffold_skeleton_design.md)
- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Learner-state frozen policy generation generator scaffold runtime release-quality remote run status](status/learner_state_frozen_policy_generation_generator_scaffold_runtime_release_quality_remote_run_status.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)
