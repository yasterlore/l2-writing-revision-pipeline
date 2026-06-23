# Frozen Policy Generation Generator Scaffold Fixture Design

This document designs future metadata-only fixtures for the frozen policy
generation generator scaffold.

It is documentation only. It does not create fixtures, implement a generator,
implement an artifact writer, generate artifact bodies, write artifact files,
compute metrics, evaluate performance, change workflows, change the
release-quality wrapper, change the Makefile, change Python code, or change
tests. It is not a real-data readiness claim.

Public docs must not include raw GitHub Actions logs, full job output, copied
log blocks, screenshots containing raw logs, generation request bodies, input
pointer bodies, expected scaffold result bodies, generated frozen policy
artifact bodies, frozen policy artifact bodies, JSON bodies, policy bodies, raw
rows, logits/probability dumps, label bodies, split bodies, calibration policy
bodies, private paths, raw learner text, manual output bodies, tmp output
bodies, or real participant data.

## 1. Document Purpose

The purpose of this document is to define the fixture structure and case plan
for a future metadata-only generator scaffold validator and implementation.

This is not implementation. It is not fixture creation, not generator code,
not artifact writing, not artifact body generation, not performance
evaluation, and not a real-data readiness claim.

The fixture design keeps the Step276 artifact policy and Step277 generator
scaffold boundary intact: the first generator scaffold returns metadata-only
plans/results, never generated policy bodies, and never written artifact files.

## 2. Current State

Current state:

- artifact policy design exists
- generator scaffold design exists
- generator scaffold fixtures do not exist yet
- generator scaffold validator does not exist yet
- generator scaffold implementation does not exist yet
- artifact body generation is not allowed
- artifact file writing is not allowed
- runtime fixtures and runtime validation infrastructure exist
- release-quality currently covers the runtime smoke, not generator fixtures

The future fixture set should therefore test only safe metadata contracts and
fail-closed behavior.

## 3. Proposed Fixture Root

Recommended fixture root:

- `tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/`

Rationale:

- it follows the learner-state fixture-root naming pattern
- it names frozen policy generation explicitly
- it names the future generator scaffold layer explicitly
- it is distinct from the runtime scaffold fixture root
- it leaves room for separate validator, runtime, and artifact fixture roots

This step does not create that directory.

## 4. Proposed Fixture Case Layout

Each future case should contain:

- `generation_request.json`
- `input_fixture_pointer.json`
- `expected_generator_scaffold_result.json`

Optional future metadata-only files:

- category-level `README.md`
- case-level `case_notes.md`

Optional notes must stay metadata-only. They must not include request bodies,
pointer bodies, expected result bodies, artifact bodies, raw rows, logits,
private paths, raw learner text, or performance claims.

## 5. Required Common Fields

Future `generation_request.json` metadata should include:

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

Future `input_fixture_pointer.json` metadata should include:

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

Future `expected_generator_scaffold_result.json` metadata should include:

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
- artifact flags
- safety flags
- count-only summary
- `safe_summary`

These fields are labels, booleans, IDs, reason codes, and counts only. They are
not bodies.

## 6. Valid Fixture Cases

Minimum valid case candidates:

- `valid/minimal_metadata_only_generation_plan`
- `valid/validated_fixed_threshold_metadata_plan`
- `valid/validated_fixed_abstention_rate_metadata_plan`

Expected valid behavior:

- `generation_status=pass`
- `reason_codes=[]`
- `failed_checks=[]`
- `generated_artifact_written=false`
- `generated_artifact_body_available=false`
- `artifact_body_suppressed=true`
- `artifact_file_path_available=false`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_performance_claims=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `test_tuning_checked=true`
- `scoring_feedback_checked=true`
- `safe_summary=metadata_only_generator_scaffold_result`

The three valid cases should cover a minimal metadata-only plan, a validated
fixed-threshold metadata plan, and a validated fixed-abstention-rate metadata
plan without producing a policy body.

## 7. Invalid Fixture Cases

Minimum invalid case candidates:

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

Expected invalid behavior:

- `generation_status=fail`
- expected reason code is present
- expected failed check is present
- validator and future runtime do not panic
- `generated_artifact_written=false`
- `generated_artifact_body_available=false`
- `artifact_body_suppressed=true`
- output contains no raw rows
- output contains no logits
- output contains no private paths
- `safe_summary=metadata_only_generator_scaffold_result` or
  `safe_summary=fail_closed_metadata_only_generator_scaffold_result`

Invalid cases may use safe marker labels and reason codes. They must not carry
actual body payloads.

## 8. Malformed / Missing Input Cases

Future validator tests should create temporary synthetic cases for:

- malformed request
- malformed pointer
- malformed expected result
- missing request
- missing pointer
- missing expected result
- unexpected extra file
- unsupported extension
- invalid directory shape

These cases should return input-error summaries without panic and without
echoing unsafe paths or malformed bodies.

## 9. Expected Result Contract

The expected result contract should require:

- output fields are safe metadata only
- no body content
- no raw data
- no logits
- no private paths
- no generated policy body
- deterministic keys
- JSON serializable summary
- expected status matches valid/invalid category
- reason code is required for invalid cases
- reason code is empty for valid cases
- artifact flags are present
- safety flags are present

The contract should be strict enough that adding a body-producing field fails
closed before release-quality integration is considered.

## 10. Artifact Flags Contract

Required artifact boolean fields:

- `generated_artifact_written`
- `generated_artifact_body_available`
- `artifact_body_suppressed`
- `artifact_file_path_available`
- `artifact_manifest_available`
- `artifact_validation_summary_available`

Initial valid expectations:

- `generated_artifact_written=false`
- `generated_artifact_body_available=false`
- `artifact_body_suppressed=true`
- `artifact_file_path_available=false`
- `artifact_manifest_available=false`
- `artifact_validation_summary_available=true` only when the summary is
  metadata-only

Any future `true` value for body availability or file path availability
requires a separate design and tests.

## 11. Safety Flags Contract

Required safety boolean fields:

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

Future validators should treat missing safety flags as `missing_required_field`
or an equivalent fail-closed reason code.

## 12. Forbidden Field / Marker Scan Policy

Future fixture validators should recursively scan keys and values for:

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

Safe appearances should be allowed only when they are reason codes, case
labels, safe marker labels, checklist text, or README explanations. Actual
payload fields should fail closed.

## 13. No-Oracle Fixture Rules

Fixture rules:

- no `observed_after_text`
- no `final_text`
- no `gold_label`
- no expected action scoring feedback
- no validation/test leakage
- no test-derived tuning
- invalid cases may use marker labels only
- invalid cases must not include actual forbidden payloads

The fixture set should prove that the generator scaffold contract can reject
oracle leakage without needing any real learner content.

## 14. Synthetic-Only Fixture Rules

Fixture rules:

- all cases use synthetic labels only
- no real participant data
- no private paths
- no `manual_outputs`
- no raw text
- no actual generated artifact body
- no artifact output path

Synthetic-only does not make body output safe. The fixture set remains
metadata-only even when every case is synthetic.

## 15. Validator Design Implications

Future validator behavior should:

- discover cases deterministically
- verify expected case counts
- verify required files
- parse JSON without printing bodies
- validate required fields
- compare category with expected `generation_status`
- compare expected reason codes
- verify artifact flags
- verify safety flags
- scan forbidden body/raw/logit/private/performance markers
- return `input_error` for malformed/missing cases
- avoid panic
- produce a safe summary

The validator should be strict about field presence and conservative about any
new field that looks body-like.

## 16. Relationship To Existing Fixtures

Existing fixture relationships:

- runtime scaffold fixtures validate runtime API, CLI, and compatibility
- generator scaffold fixtures will validate metadata-only generation planning
- frozen policy generation validation fixtures are separate
- frozen policy validation fixtures are separate
- selective prediction fixtures are separate
- runtime fixture expected result bodies should not be reused directly
- future generator fixtures may reference validation labels only

The generator scaffold fixture root should not replace the runtime scaffold
fixture root. It adds a later layer focused on generation planning metadata.

## 17. Release-Quality Strategy

Release-quality strategy:

- do not add generator scaffold fixtures to release-quality now
- create fixture design first
- create fixtures second
- design and implement the fixture validator third
- implement generator scaffold skeleton after the validator exists
- add CLI, Makefile, and release-quality only after no-body-leakage tests pass

Release-quality success should remain safety and smoke evidence, not generator
quality or performance evidence.

## 18. What This Does NOT Prove

This fixture design does not prove:

- generator implementation
- artifact generation
- artifact file writing
- generated policy quality
- calibration quality
- model performance
- real-data readiness
- production readiness

It only plans the future metadata-only fixture contract.

## 19. Beginner-Friendly Explanation

A fixture is a tiny, controlled test example. Here, each future fixture case
will describe a synthetic generator request, a safe pointer to synthetic
metadata, and the safe result that should come back.

Valid fixtures describe cases that should pass. Invalid fixtures describe
cases that should fail safely with a reason code.

The expected result contract is the checklist that says what the result must
look like. It keeps future code honest by requiring the same safety flags,
artifact flags, and fail-closed reason codes every time.

Bodies are not included because body content is the risky part. A future
generator should first prove it can plan safely before it can create policy
content.

Invalid cases use marker labels because the tests only need to prove that the
validator catches the unsafe condition. They do not need actual raw text,
logits, private paths, or policy bodies.

## 20. Next Recommended Steps

Recommended sequence:

- generator scaffold fixture creation
- generator scaffold fixture validator design
- generator scaffold fixture validator implementation
- generator scaffold skeleton implementation

The next safest step is fixture creation, still using synthetic-only,
metadata-only content and no artifact body or file writing.

Step279 creates that fixture root at
`tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/`.
The created fixtures stay metadata-only and synthetic-only. They include three
valid cases and fifteen fail-closed invalid marker cases. They do not include
artifact bodies, generated policy bodies, raw rows, logits, private paths, raw
learner text, real participant data, generator code, artifact file writing, or
validator code.

Step280 designs the future validator for that fixture root at
[Frozen policy generation generator scaffold fixture validator design](frozen_policy_generation_generator_scaffold_fixture_validator_design.md).
It keeps validator implementation, generator implementation, artifact body
generation, artifact writing, Makefile targets, release-quality integration,
metrics, and real-data readiness out of scope.

Step281 implements that metadata-only fixture validator and focused tests. It
still does not add a CLI, Makefile target, release-quality integration,
generator implementation, artifact body generation, artifact writing, metrics,
or real-data readiness.

Step282 designs the future CLI for running that validator safely from a
terminal:
[Frozen policy generation generator scaffold fixture validator CLI design](frozen_policy_generation_generator_scaffold_fixture_validator_cli_design.md).
The CLI design keeps output metadata-only and does not implement CLI code,
Makefile targets, release-quality integration, generator code, artifact body
generation, or artifact writing.

Step283 implements that safe validator CLI and focused tests. The fixture root
itself remains unchanged, and the CLI still does not run a generator, write
artifacts, expose fixture bodies, add a Makefile target, or change
release-quality.

Step284 designs the future Makefile target for running that CLI over this
fixture root:
[Frozen policy generation generator scaffold fixture validator Makefile target design](frozen_policy_generation_generator_scaffold_fixture_validator_makefile_target_design.md).
The design does not change fixtures, add the target, integrate
release-quality, run a generator, or write artifacts.

Step285 implements the standalone Makefile target for validating this fixture
root through the safe CLI. The fixture files remain unchanged, and the target
does not run a generator, write artifacts, expose fixture bodies, or integrate
release-quality.

Step286 designs future release-quality integration for that standalone target:
[Frozen policy generation generator scaffold fixture validator release-quality integration design](frozen_policy_generation_generator_scaffold_fixture_validator_release_quality_integration_design.md).
The fixture root remains unchanged and no generator or artifact writer is
introduced.

Step288 designs the future remote/manual Release Quality run record workflow:
[Frozen policy generation generator scaffold fixture release-quality remote run record workflow](frozen_policy_generation_generator_scaffold_fixture_release_quality_remote_run_record_workflow.md).
The future record should summarize these fixtures only through safe counts and
safety flags.

Step290 designs the future generator scaffold skeleton:
[Frozen policy generation generator scaffold skeleton design](frozen_policy_generation_generator_scaffold_skeleton_design.md).
The skeleton should consume this fixture root only as metadata-only
request/pointer input and compare future safe results with expected metadata,
without producing artifact bodies or writing files.

Step291 implements that metadata-only skeleton and focused tests. The fixture
root remains unchanged, and expected-result compatibility is checked without
printing fixture bodies in docs.

Step292 designs the future CLI for running the implemented skeleton:
[Frozen policy generation generator scaffold CLI design](frozen_policy_generation_generator_scaffold_cli_design.md).
The fixture root remains unchanged. The future CLI should consume one
request/pointer pair as metadata-only input and should not expose fixture
bodies, artifact bodies, generated policy bodies, or write files.

## Related Documents

- [Frozen policy generation generator scaffold CLI design](frozen_policy_generation_generator_scaffold_cli_design.md)
- [Frozen policy generation generator scaffold skeleton design](frozen_policy_generation_generator_scaffold_skeleton_design.md)
- [Frozen policy generation generator scaffold fixture release-quality remote run record workflow](frozen_policy_generation_generator_scaffold_fixture_release_quality_remote_run_record_workflow.md)
- [Frozen policy generation generator scaffold fixtures](../tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/README.md)
- [Frozen policy generation generator scaffold fixture validator design](frozen_policy_generation_generator_scaffold_fixture_validator_design.md)
- [Frozen policy generation generator scaffold fixture validator CLI design](frozen_policy_generation_generator_scaffold_fixture_validator_cli_design.md)
- [Frozen policy generation generator scaffold fixture validator Makefile target design](frozen_policy_generation_generator_scaffold_fixture_validator_makefile_target_design.md)
- [Frozen policy generation generator scaffold fixture validator release-quality integration design](frozen_policy_generation_generator_scaffold_fixture_validator_release_quality_integration_design.md)
- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Frozen policy generation artifact policy design](frozen_policy_generation_artifact_policy_design.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Frozen policy generation scaffold runtime fixture compatibility test design](frozen_policy_generation_scaffold_runtime_fixture_compatibility_test_design.md)
- [Frozen policy generation scaffold fixture design](frozen_policy_generation_scaffold_fixture_design.md)
- [Frozen policy generation fixture design](frozen_policy_generation_fixture_design.md)
- [Public release checklist](public_release_checklist.md)
