# Frozen Policy Generation Generator Scaffold Fixture Validator Design

This document designs a future validator for the frozen policy generation
generator scaffold fixture root.

It is documentation only. It does not implement validator code, generator code,
artifact writing, artifact body generation, fixture creation, workflow changes,
release-quality wrapper changes, Makefile targets, Python code, Python tests,
metric computation, performance evaluation, or real-data readiness.

Public docs must not include raw GitHub Actions logs, full job output, copied
log blocks, screenshots containing raw logs, generation request bodies, input
pointer bodies, expected generator scaffold result bodies, generated frozen
policy artifact bodies, frozen policy artifact bodies, JSON bodies, policy
bodies, raw rows, logits/probability dumps, label bodies, split bodies,
calibration policy bodies, private paths, raw learner text, manual output
bodies, tmp output bodies, or real participant data.

## 1. Document Purpose

The purpose of this document is to define a future validator for the
metadata-only generator scaffold fixtures created under
`tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/`.

The validator will check fixture shape, required files, schema labels, required
fields, valid/invalid category alignment, reason-code expectations, artifact
flags, safety flags, count-only summaries, and forbidden marker scans.

This is not implementation. It is not generator implementation, not fixture
creation, not an artifact writer, not artifact body generation, not
performance evaluation, and not a real-data readiness claim.

## 2. Current State

Current state:

- artifact policy design exists
- generator scaffold design exists
- generator scaffold fixture design exists
- generator scaffold fixtures exist
- validator does not exist yet
- generator scaffold implementation does not exist yet
- fixture root has 3 valid cases, 15 invalid cases, and 54 JSON files
- artifact body generation is not allowed
- artifact file writing is not allowed
- Python code, tests, Makefile targets, wrapper, and workflows are unchanged

The fixture root is metadata-only and synthetic-only. It provides a contract for
future validator and generator scaffold work, not an executable generator.

## 3. Proposed Validator Module

Recommended module:

- `python/learner_state/frozen_policy_generation_generator_scaffold_fixture_validation.py`

Rationale:

- it stays inside the existing `learner_state` namespace
- it names frozen policy generation explicitly
- it names the generator scaffold layer explicitly
- it names fixture validation rather than generator execution
- it stays distinct from the runtime scaffold fixture validator

The module name is intentionally long because the boundary is safety-sensitive:
it should be clear that this checks generator scaffold fixtures and does not run
the future generator.

## 4. Proposed Public APIs

Future public API candidates:

- `discover_frozen_policy_generation_generator_scaffold_fixture_cases(fixture_root)`
  - deterministically discovers valid and invalid case directories
- `load_generator_scaffold_fixture_case(case_dir)`
  - loads the three required metadata files for one case
- `validate_generator_scaffold_fixture_case(case)`
  - validates one loaded case and returns safe metadata only
- `load_expected_generator_scaffold_result(path)`
  - loads the expected metadata-only generator scaffold result
- `compare_generator_scaffold_fixture_to_expected(case_result, expected)`
  - compares status, reason codes, failed checks, flags, and count constraints
- `validate_generator_scaffold_fixture_root(fixture_root)`
  - validates every discovered case and returns a root-level summary
- `summarize_generator_scaffold_fixture_validation_result(result)`
  - converts the root result into safe human or JSON metadata
- `scan_generator_scaffold_fixture_for_forbidden_markers(case)`
  - recursively scans keys and string values for unsafe payload indicators

The API should not expose request bodies, pointer bodies, expected result
bodies, artifact bodies, raw rows, logits, private paths, raw learner text, or
performance metric bodies.

## 5. Proposed Dataclasses / Structures

Future structure candidates:

- `GeneratorScaffoldFixtureCase`
  - safe case label, category, file paths, schema labels, and parsed metadata
    shape status
- `GeneratorScaffoldFixtureValidationResult`
  - per-case status, matched status, reason codes, failed checks, mismatch
    field names, and safety scan flags
- `GeneratorScaffoldFixtureRootValidationResult`
  - mode, total counts, matched counts, mismatched counts, input-error counts,
    reason-code counts, and aggregate safety flags
- `GeneratorScaffoldFixtureSafetySummary`
  - content suppression, no raw rows, no logits, no private paths, no
    performance claims, artifact policy, body suppression, and file-writing
    checks
- `GeneratorScaffoldFixtureInputError`
  - safe error category, safe case label, and missing/malformed file label
- `GeneratorScaffoldFixtureComparisonResult`
  - expected/actual scalar comparison result with safe field names only

All structures should contain metadata, booleans, counts, reason codes, and
safe labels only.

## 6. Discovery Contract

The future validator should enforce:

- fixture root exists
- root `README.md` exists
- `valid/` directory exists
- `invalid/` directory exists
- valid cases are discovered deterministically
- invalid cases are discovered deterministically
- expected valid count is 3
- expected invalid count is 15
- expected total count is 18
- each case contains exactly the three required JSON files
- no unexpected extra files are present
- unsupported extensions produce `input_error`
- invalid directory shape produces `input_error`

Optional category README files or case notes should remain disallowed until a
later explicit design allows them.

## 7. Required File Contract

Each case must contain exactly:

- `generation_request.json`
- `input_fixture_pointer.json`
- `expected_generator_scaffold_result.json`

Failure handling:

- missing file -> `input_error`
- malformed JSON -> `input_error`
- unexpected duplicate -> `input_error`
- unexpected non-JSON file -> `input_error`
- unreadable file -> `input_error`

The validator should report safe file labels only. It should not print file
bodies.

## 8. Schema Version Checks

Required schema labels:

- request schema:
  `frozen_policy_generation_generator_scaffold_request_v0.1`
- pointer schema:
  `frozen_policy_generation_generator_scaffold_pointer_v0.1`
- expected result schema:
  `frozen_policy_generation_generator_scaffold_result_v0.1`

Boundary between `fail` and `input_error`:

- the intentional `invalid/unknown_schema_version` fixture is a fail-closed
  case, not an input error, when the JSON is readable and the expected result
  declares the matching fail reason
- malformed JSON, missing `schema_version`, or structurally unreadable schema
  metadata is `input_error`
- category and expected result must agree with the schema failure expectation

This keeps intentional invalid marker cases distinct from broken fixture files.

## 9. Required Fields

`generation_request.json` required fields:

- `schema_version`
- `request_id`
- `generator_mode`
- `validation_reference_ids`
- `split_policy_label`
- `calibration_policy_label`
- `threshold_policy_label`
- `abstention_policy_label`
- `synthetic_only`
- `no_oracle_required`
- `artifact_policy_label`
- `requested_artifact_body`
- `requested_file_writing`
- `expected_generation_status`
- `expected_reason_codes`
- `notes`

`input_fixture_pointer.json` required fields:

- `schema_version`
- `pointer_id`
- `fixture_label`
- `validation_fixture_label`
- `frozen_policy_validation_label`
- `selective_prediction_validation_label`
- `source_kind`
- `synthetic_only`
- `no_raw_rows`
- `no_logits_dump`
- `no_private_paths`
- `notes`

`expected_generator_scaffold_result.json` required fields:

- `schema_version`
- `generation_status`
- `reason_codes`
- `failed_checks`
- `request_id`
- `pointer_id`
- `policy_id`
- `artifact_id`
- `generator_version`
- `validation_reference_ids`
- `artifact_flags`
- `safety_flags`
- `count_summary`
- `safe_summary`

Required fields should be checked for type and safe metadata shape, not for
body content.

## 10. Valid / Invalid Category Checks

Valid category expectations:

- `generation_status` is `pass`
- `reason_codes` is empty
- `failed_checks` is empty
- request `expected_generation_status` is `pass`
- request `expected_reason_codes` is empty

Invalid category expectations:

- `generation_status` is `fail`
- `reason_codes` is non-empty
- `failed_checks` is non-empty
- request `expected_generation_status` is `fail`
- request `expected_reason_codes` is non-empty
- at least one expected reason code aligns with the safe case label

The validator should treat invalid fixtures as expected fail-closed cases, not
as validator failures, when their expected metadata matches the contract.

## 11. Valid Cases Expected

Expected valid cases:

- `valid/minimal_metadata_only_generation_plan`
- `valid/validated_fixed_threshold_metadata_plan`
- `valid/validated_fixed_abstention_rate_metadata_plan`

All valid cases should remain body-free, artifact-file-free, synthetic-only,
and no-oracle safe.

## 12. Invalid Cases Expected

Expected invalid cases:

- `invalid/missing_validation_reference`
- `invalid/unvalidated_input`
- `invalid/raw_rows_carryover`
- `invalid/logits_dump_carryover`
- `invalid/generated_artifact_body_leakage`
- `invalid/artifact_file_writing_attempt`
- `invalid/private_path_output`
- `invalid/test_temperature_tuning`
- `invalid/test_threshold_tuning`
- `invalid/scoring_feedback_violation`
- `invalid/performance_claim_in_generated_policy`
- `invalid/request_body_leakage`
- `invalid/pointer_body_leakage`
- `invalid/unknown_schema_version`
- `invalid/missing_required_field`

These are safe marker cases. They should not include actual unsafe payloads.

## 13. Artifact Flags Validation

Required boolean fields:

- `generated_artifact_written`
- `generated_artifact_body_available`
- `artifact_body_suppressed`
- `artifact_file_path_available`
- `artifact_manifest_available`
- `artifact_validation_summary_available`

Initial required values:

- `generated_artifact_written=false`
- `generated_artifact_body_available=false`
- `artifact_body_suppressed=true`
- `artifact_file_path_available=false`
- `artifact_manifest_available=false`
- `artifact_validation_summary_available=true`

Invalid cases still must keep these values. They model fail-closed metadata,
not actual artifact body creation or file writing.

## 14. Safety Flags Validation

Required boolean fields:

- `content_suppressed`
- `no_raw_rows`
- `no_logits_dump`
- `no_private_paths`
- `no_performance_claims`
- `synthetic_only_checked`
- `no_oracle_checked`
- `test_tuning_checked`
- `scoring_feedback_checked`
- `artifact_policy_checked`
- `body_suppression_checked`
- `file_writing_checked`

Expected values:

- every required field is a boolean
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
- `test_tuning_checked=true`
- `scoring_feedback_checked=true`

The test-tuning and scoring-feedback checks should be true even for
fail-closed invalid cases because the fixture demonstrates detection metadata
without carrying forbidden payloads.

## 15. Count Summary Validation

Required integer fields:

- `validation_reference_count`
- `artifact_metadata_field_count`
- `body_field_count`
- `raw_row_count`
- `logits_dump_count`
- `private_path_count`
- `performance_metric_count`

Expected constraints:

- `body_field_count=0`
- `raw_row_count=0`
- `logits_dump_count=0`
- `private_path_count=0`
- `performance_metric_count=0`
- all counts are integers
- no counts are negative

Count summaries should remain count-only. They must not include row bodies,
metric bodies, or private paths.

## 16. Forbidden Marker Scan Policy

The validator should recursively scan keys and string values for actual unsafe
payload indicators:

- `raw_rows`
- `logits`
- `probabilities`
- `raw_learner_text`
- `observed_after_text`
- `final_text`
- `gold_label`
- `expected_action_feedback`
- `request_body`
- `pointer_body`
- `artifact_body`
- `generated_policy_body`
- `policy_json_body`
- `calibration_body`
- `label_body`
- `split_body`
- `private_path`
- `real_data`
- `participant_data`
- `manual_outputs`
- `performance_claim`

Allowed safe markers:

- case directory names
- `reason_codes`
- `failed_checks`
- README explanations
- `notes` fields when they describe marker labels without payloads
- safety flag names such as `no_raw_rows`, `no_logits_dump`,
  `no_private_paths`, and `no_performance_claims`
- count field names such as `raw_row_count`, `logits_dump_count`,
  `private_path_count`, and `performance_metric_count`

The validator should report the safe marker category and case label, not the
matched payload text. Actual payload fields should fail closed.

## 17. No-Oracle Checks

The validator should confirm:

- no observed-after text payload
- no final text payload
- no gold label payload
- no expected action scoring feedback payload
- no test-derived tuning payload
- no validation/test leakage payload
- marker labels appear only as case names, reason codes, failed checks, or
  safe notes

No-oracle checks should apply to all three files in every case.

## 18. Synthetic-Only Checks

The validator should confirm:

- request `synthetic_only=true`
- pointer `synthetic_only=true`
- no real-data payload
- no participant-data payload
- no private paths
- no `manual_outputs`
- no raw learner text
- no artifact output path
- fixture references are safe labels only

The generator scaffold fixture root is public-safe metadata. It is not a real
data pipeline.

## 19. Comparison Strategy

The validator should:

- produce an actual metadata-only validation result from the fixture files
- compare valid/invalid category against expected result
- compare request expected status against expected result status
- compare expected reason codes against result reason codes
- compare failed checks against the reason-code contract
- compare artifact flags against required values
- compare safety flags against required values
- enforce count-summary zero constraints
- mark mismatches as validation mismatches
- mark malformed or missing inputs as `input_error`
- never panic on malformed fixtures

Comparison output should include safe field names and scalar status only.

## 20. Summary Output Design

Safe human summary fields:

- `mode=fixture_root`
- `total_cases`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `reason_code_counts`
- `content_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `artifact_policy_checked=true`
- `body_suppression_checked=true`
- `file_writing_checked=true`
- `validation_schema_version`

Safe JSON summary:

- same safe fields as human output
- parseable
- deterministic enough for tests
- no request body
- no pointer body
- no expected result body
- no artifact body
- no raw rows
- no logits
- no private paths
- no raw learner text
- no performance metric body

## 21. CLI Design Implications

Future CLI entrypoint candidate:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_generator_scaffold_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold
```

Future optional arguments:

- `--json`
- `--fixture-case`

This step does not implement the CLI. The first CLI should remain a thin
wrapper over the validator API and should output safe metadata only.

## 22. Test Strategy For Implementation

Future tests should cover:

- deterministic discovery counts: 3 valid, 15 invalid, 18 total
- required files present
- JSON parse behavior
- schema version checks
- valid cases pass
- invalid cases fail with expected reason codes
- artifact flags are required and fixed
- safety flags are required and true
- count summary zero constraints
- forbidden marker scans
- malformed request temp fixture returns `input_error`
- malformed pointer temp fixture returns `input_error`
- malformed expected result temp fixture returns `input_error`
- missing files return `input_error`
- unexpected files return `input_error`
- JSON summary is parseable
- no body leakage in stdout or stderr

Tests should use synthetic temp fixtures only for malformed/missing cases and
must not write artifacts.

## 23. Relation To Existing Validators

This future validator is separate from:

- runtime scaffold fixture validator
- frozen policy generation validator
- frozen policy validator
- selective prediction validator
- learner-state estimator input validator

Its scope is the generator scaffold metadata-only fixture contract. It should
not run the generator, write artifacts, compute metrics, load raw rows, or
inspect real data.

## 24. Release-Quality Strategy

Release-quality strategy:

- do not add this validator to release-quality now
- implement validator first
- add focused tests for fixture root and malformed/missing temp cases
- add a standalone Makefile target only after validator tests pass
- integrate release-quality only after standalone target success and
  no-body-leakage review

Future release-quality success would mean fixture contract validation passed.
It would not mean generator quality or performance evidence.

## 25. What This Does Not Prove

This design does not prove:

- generator implementation exists
- artifact generation works
- artifact file writing works
- generated policy quality
- model performance
- calibration quality
- selective prediction correctness
- learner-state estimator correctness
- real-data readiness
- production readiness

## 26. Beginner-Friendly Explanation

A validator is a small checker that reads fixture files and confirms that they
follow the expected contract. Here, it will confirm that the generator scaffold
fixtures are safe metadata-only examples.

Invalid fixtures are not "bad files." They are intentional safe marker cases.
They should pass the validator when they fail for the expected reason code.

`input_error` is different from `fail`: `fail` means the fixture intentionally
describes a rejected generator scenario, while `input_error` means the fixture
file itself is broken, missing, malformed, or shaped incorrectly.

Body scans are needed because this fixture root is public-facing. The validator
must preserve the boundary that no request body, pointer body, artifact body,
raw rows, logits, private paths, raw learner text, or performance metric body
is stored or reported.

## 27. Next Recommended Steps

Recommended next steps:

- generator scaffold fixture validator CLI design and implementation
- generator scaffold validator Makefile target design and implementation
- release-quality integration design after standalone safety evidence

Generator implementation and artifact writing should remain separate later
work.

## 28. Docs Update

This Step280 document links the Step279 fixture root to a future validator
boundary. It does not add code, tests, fixtures, Makefile targets, wrapper
changes, workflow changes, artifact bodies, or generated policy bodies.

Step281 implements the metadata-only fixture validator at
`python/learner_state/frozen_policy_generation_generator_scaffold_fixture_validation.py`
and focused tests at
`python/learner_state/tests/test_frozen_policy_generation_generator_scaffold_fixture_validation.py`.
The implementation validates the fixture contract only. It does not add a CLI,
Makefile target, release-quality integration, workflow change, generator,
artifact body generation, artifact file writing, metrics, or real-data
readiness.

Step282 designs the future safe CLI for this implemented validator at
[Frozen policy generation generator scaffold fixture validator CLI design](frozen_policy_generation_generator_scaffold_fixture_validator_cli_design.md).
That design covers entrypoint, arguments, exit codes, safe human/JSON output,
no-body-leakage policy, future CLI tests, and staged Makefile/release-quality
integration. It does not implement CLI code or change the validator module.

Step283 implements the CLI entrypoint in the validator module and adds focused
CLI tests. The CLI remains metadata-only and does not execute a generator,
write artifacts, expose request/pointer/expected-result bodies, add a Makefile
target, change release-quality, or change workflows.

Step284 designs the future standalone Makefile target for that CLI at
[Frozen policy generation generator scaffold fixture validator Makefile target design](frozen_policy_generation_generator_scaffold_fixture_validator_makefile_target_design.md).
The design keeps Makefile implementation, release-quality integration,
workflow changes, generator code, artifact body generation, and artifact
writing out of scope.

Step285 implements the standalone Makefile target for the CLI. The validator
contract remains unchanged, and release-quality integration, workflows,
generator code, artifact body generation, artifact writing, Python tests, and
fixtures remain out of scope.

Step286 designs future release-quality wrapper integration for that target:
[Frozen policy generation generator scaffold fixture validator release-quality integration design](frozen_policy_generation_generator_scaffold_fixture_validator_release_quality_integration_design.md).
The design does not change the wrapper, workflows, validator, fixtures,
generator, or artifact policy.

Step288 adds the future remote/manual Release Quality run record workflow:
[Frozen policy generation generator scaffold fixture release-quality remote run record workflow](frozen_policy_generation_generator_scaffold_fixture_release_quality_remote_run_record_workflow.md).
The validator remains a metadata-only fixture contract checker; the future
status marker should record only pass-only/count-only results.

Step290 adds the generator scaffold skeleton design:
[Frozen policy generation generator scaffold skeleton design](frozen_policy_generation_generator_scaffold_skeleton_design.md).
The validator remains separate; future compatibility tests may compare skeleton
metadata-only results with expected fixture metadata without printing bodies.

Related docs:

- [Frozen policy generation generator scaffold skeleton design](frozen_policy_generation_generator_scaffold_skeleton_design.md)
- [Frozen policy generation generator scaffold fixture release-quality remote run record workflow](frozen_policy_generation_generator_scaffold_fixture_release_quality_remote_run_record_workflow.md)
- [Frozen policy generation generator scaffold fixture validator release-quality integration design](frozen_policy_generation_generator_scaffold_fixture_validator_release_quality_integration_design.md)
- [Frozen policy generation generator scaffold fixture validator Makefile target design](frozen_policy_generation_generator_scaffold_fixture_validator_makefile_target_design.md)
- [Frozen policy generation generator scaffold fixture design](frozen_policy_generation_generator_scaffold_fixture_design.md)
- [Frozen policy generation generator scaffold fixture validator CLI design](frozen_policy_generation_generator_scaffold_fixture_validator_cli_design.md)
- [Frozen policy generation generator scaffold fixtures](../tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/README.md)
- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Frozen policy generation artifact policy design](frozen_policy_generation_artifact_policy_design.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)

## 29. Update History

- Step280: initial docs-only validator design for metadata-only generator
  scaffold fixtures.
- Step281: recorded implementation status for the metadata-only fixture
  validator and focused tests; CLI, Makefile target, release-quality
  integration, generator code, and artifact writing remain out of scope.
- Step282: linked the docs-only CLI design for safe terminal execution of the
  implemented validator; CLI implementation remains future work.
- Step283: recorded CLI implementation status; Makefile target,
  release-quality integration, workflow changes, generator code, artifact body
  generation, and artifact writing remain future work.
- Step284: linked the docs-only standalone Makefile target design for the
  validator CLI; implementation and release-quality integration remain future
  work.
- Step285: recorded standalone Makefile target implementation status; wrapper,
  workflow, generator, artifact body, artifact writing, test, and fixture
  changes remain out of scope.
- Step286: linked the release-quality integration design for the standalone
  target.
- Step288: linked the remote/manual run record workflow design for a future
  public-safe status marker.
- Step290: linked the generator scaffold skeleton design; validator and
  skeleton responsibilities remain separate and metadata-only.
