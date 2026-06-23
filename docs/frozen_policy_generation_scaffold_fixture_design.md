# Frozen Policy Generation Scaffold Fixture Design

This document designs future fixtures for the frozen policy generation
scaffold.

It is documentation only. It does not create fixture files, implement scaffold
code, implement generator code, add CLI behavior, change Makefile targets,
change release-quality, change workflows, change Python code, change tests, or
change existing fixtures. It is not performance evaluation and not a real-data
readiness claim.

Public docs must not include raw GitHub Actions logs, full job output, copied
log blocks, screenshots containing raw logs, generation request bodies, input
pointer bodies, generated frozen policy artifact bodies, frozen policy artifact
bodies, JSON bodies, raw rows, logits/probability dumps, label bodies, split
bodies, calibration policy bodies, generated feature/label/manifest bodies,
private paths, raw learner text, or real participant data.

## 1. Purpose

The purpose of this document is to define a future synthetic-only fixture
contract for the frozen policy generation scaffold before scaffold code is
implemented.

The fixture design should fix:

- valid and invalid scaffold cases
- per-case file set
- expected scaffold result metadata
- reason-code mapping
- safe output policy
- relation to existing generation validation fixtures

This is not fixture implementation, not scaffold implementation, not generator
implementation, not calibration, not selective prediction, not metric
computation, and not real-data readiness work.

## 2. Current State

Current state:

- frozen policy generation validation fixture root exists
- frozen policy generation validator exists
- validator CLI exists
- Makefile target exists
- release-quality integration exists
- remote/manual status marker exists
- Milestone 11 recap exists
- scaffold implementation design exists

Still absent:

- scaffold-specific fixture root
- scaffold-specific fixture files
- scaffold code
- generator code
- scaffold CLI
- generated policy artifact body publication
- real-data handling

The current validation fixture root checks the bridge-contract validator. It
does not yet exercise a scaffold API or scaffold CLI.

## 3. Proposed Fixture Root

Recommended future root:

- `tests/fixtures/learner_state_frozen_policy_generation_scaffold/`

Difference from the existing root:

- `tests/fixtures/learner_state_frozen_policy_generation/` is for generation
  fixture validation and validator expected-result matching.
- `tests/fixtures/learner_state_frozen_policy_generation_scaffold/` should be
  for future scaffold API and CLI behavior.

The new root should not copy existing fixture bodies into docs. It should use
synthetic-only metadata and safe relative pointers.

## 4. Proposed Fixture Directory Structure

Future structure:

- `tests/fixtures/learner_state_frozen_policy_generation_scaffold/README.md`
- `tests/fixtures/learner_state_frozen_policy_generation_scaffold/valid/<case_name>/`
- `tests/fixtures/learner_state_frozen_policy_generation_scaffold/invalid/<case_name>/`

Candidate files per case:

- `generation_request.json`
- `input_fixture_pointer.json`
- `expected_scaffold_result.json`
- optional `expected_generation_result.json`
- optional `expected_frozen_policy_validation_result.json`

Recommendation:

- require `generation_request.json`
- require `input_fixture_pointer.json`
- require `expected_scaffold_result.json`
- do not require `expected_generation_result.json` initially
- do not require `expected_frozen_policy_validation_result.json` initially

Reasoning:

- scaffold tests should first prove scaffold behavior and safe summaries
- generation validator compatibility can be added after scaffold result shape
  is stable
- frozen policy validation consistency can be represented as metadata in
  `expected_scaffold_result.json`
- adding too many expected-result files in the first scaffold fixture step
  increases coupling before scaffold API behavior exists

## 5. Recommended Case Files

Initial required file set:

- `generation_request.json`
- `input_fixture_pointer.json`
- `expected_scaffold_result.json`

`generation_request.json` should describe safe request metadata and intended
dry-run behavior.

`input_fixture_pointer.json` should point to safe synthetic input metadata
without copying row bodies or policy bodies.

`expected_scaffold_result.json` should contain safe metadata only and should
define the scaffold status, safety flags, reason codes, and write policy.

Optional future additions:

- `expected_generation_result.json`
  - add after scaffold output can be compared to generation validator expected
    results
- `expected_frozen_policy_validation_result.json`
  - add only if a later step needs direct frozen policy validator consistency
    fixture coverage

## 6. Valid Cases Design

Initial valid case candidates:

- `valid/minimal_fixed_threshold_dry_run`
  - Purpose: simplest dry-run plan with identity temperature and fixed
    confidence threshold metadata.
  - Expected status: pass.
  - Expected flags: `content_suppressed=true`, `no_raw_rows=true`,
    `no_logits_dump=true`, `no_request_body=true`,
    `no_generated_artifact_body=true`, `metadata_only=true`.

- `valid/minimal_fixed_abstention_rate_dry_run`
  - Purpose: dry-run plan with fixed abstention rate metadata.
  - Expected status: pass.
  - Expected flags: validation split available, test tuning checked, artifact
    body suppressed.

- `valid/validation_nll_temperature_metadata_only_dry_run`
  - Purpose: allow validation-NLL temperature provenance metadata without
    computing NLL or exposing logits.
  - Expected status: pass.
  - Expected flags: no logits dump, no performance claim, metadata only.

- `valid/no_artifact_body_dry_run`
  - Purpose: prove that a dry-run can indicate it would not write or expose a
    generated artifact body.
  - Expected status: pass.
  - Expected flags: `would_write_artifact=false`,
    `artifact_body_suppressed=true`.

- `valid/validator_consistency_metadata_only`
  - Purpose: record that frozen policy validation consistency metadata is
    present without requiring an artifact body.
  - Expected status: pass.
  - Expected flags: frozen policy validation status metadata present, no body
    copied.

Valid cases should not include request bodies in public docs, generated
artifact bodies, raw rows, logits, private paths, performance metrics, or
real-data references.

## 7. Invalid Cases Design

Initial invalid case candidates:

- `invalid/missing_request`
  - Purpose: request metadata is missing.
  - Expected reason code: `missing_request`.
- `invalid/malformed_request`
  - Purpose: request metadata cannot be parsed safely.
  - Expected reason code: `malformed_request`.
- `invalid/missing_pointer`
  - Purpose: pointer metadata is missing.
  - Expected reason code: `missing_pointer`.
- `invalid/malformed_pointer`
  - Purpose: pointer metadata cannot be parsed safely.
  - Expected reason code: `malformed_pointer`.
- `invalid/unvalidated_input`
  - Purpose: input validation was not recorded.
  - Expected reason code: `unvalidated_input`.
- `invalid/missing_validation_split`
  - Purpose: validation split availability is false or absent.
  - Expected reason code: `missing_validation_split`.
- `invalid/selective_prediction_validator_failure`
  - Purpose: selective prediction validation status is failure.
  - Expected reason code: `selective_prediction_validator_failure`.
- `invalid/frozen_policy_validator_failure`
  - Purpose: frozen policy validation consistency metadata indicates failure.
  - Expected reason code: `frozen_policy_validator_failure`.
- `invalid/test_temperature_tuning`
  - Purpose: temperature policy uses test split provenance.
  - Expected reason code: `test_temperature_tuning`.
- `invalid/test_threshold_tuning`
  - Purpose: threshold or abstention policy uses test split provenance.
  - Expected reason code: `test_threshold_tuning`.
- `invalid/raw_rows_carryover`
  - Purpose: request or scaffold plan attempts raw row carryover.
  - Expected reason code: `raw_rows_carryover`.
- `invalid/logits_dump_carryover`
  - Purpose: request or scaffold plan attempts logits/probability dump
    carryover.
  - Expected reason code: `logits_dump_carryover`.
- `invalid/generated_artifact_body_leakage`
  - Purpose: request or output policy asks to expose generated artifact body.
  - Expected reason code: `generated_artifact_body_leakage`.
- `invalid/private_path_output`
  - Purpose: output policy exposes an unsafe private path.
  - Expected reason code: `private_path_output`.
- `invalid/performance_claim_generation`
  - Purpose: request or expected summary claims performance evidence.
  - Expected reason code: `performance_claim_generation`.
- `invalid/body_dump_requested`
  - Purpose: request asks to print or store body content.
  - Expected reason code: `body_dump_requested`.
- `invalid/real_data_path`
  - Purpose: pointer or output path references real-data storage.
  - Expected reason code: `real_data_path`.
- `invalid/participant_data_path`
  - Purpose: pointer or output path references participant-data storage.
  - Expected reason code: `participant_data_path`.
- `invalid/manual_output_path`
  - Purpose: automated scaffold fixture points at `manual_outputs/`.
  - Expected reason code: `manual_output_path`.
- `invalid/no_oracle_violation`
  - Purpose: metadata attempts to use after-observed or oracle-only content.
  - Expected reason code: `no_oracle_violation`.
- `invalid/scoring_feedback_violation`
  - Purpose: expected action or label content is treated as scoring feedback.
  - Expected reason code: `scoring_feedback_violation`.

Invalid case output should still be safe: reason codes, failed checks, and
boolean flags only.

## 8. Expected Scaffold Result Contract

`expected_scaffold_result.json` should contain safe fields only:

- `scaffold_schema_version`
- `scaffold_status`
- `reason_codes`
- `failed_checks`
- `generation_request_schema_version`
- `pointer_schema_version`
- `input_validation_status`
- `selective_prediction_validation_status`
- `frozen_policy_validation_status`
- `validation_split_available`
- `temperature_policy_status`
- `threshold_policy_status`
- `abstention_policy_status`
- `output_policy_status`
- `safety_status`
- `content_suppressed`
- `no_raw_rows`
- `no_logits_dump`
- `no_request_body`
- `no_generated_artifact_body`
- `artifact_body_suppressed`
- `synthetic_only_checked`
- `no_oracle_checked`
- `test_tuning_checked`
- `private_path_scan_checked`
- `performance_claim_scan_checked`
- `would_write_artifact`
- `artifact_write_mode`
- `metadata_only`

Forbidden fields:

- request body
- pointer body
- generated artifact body
- raw rows
- logits
- probabilities
- labels body
- split body
- raw learner text
- private path
- performance metric body

Expected result files should be safe enough to print as summaries, although
docs should still avoid pasting full JSON bodies.

## 9. Request Fixture Contract

`generation_request.json` should contain safe metadata:

- request schema version
- generation mode
- `dry_run`
- temperature policy metadata
- threshold policy metadata
- abstention policy metadata
- output policy metadata
- validation split source metadata
- synthetic-only marker
- no-oracle marker
- no body dump marker

Forbidden content:

- raw rows
- logits
- probability dumps
- raw learner text
- labels
- final text
- observed-after text
- gold labels
- private paths
- performance claims

Valid request fixtures should prefer dry-run metadata and explicit body
suppression flags.

## 10. Input Pointer Fixture Contract

`input_fixture_pointer.json` should contain safe metadata:

- pointer schema version
- fixture family
- validation status
- validation split available
- selective prediction validation status
- frozen policy validation status
- fixture case label
- relative fixture references only

Forbidden content:

- absolute private paths
- real-data paths
- participant-data paths
- raw rows
- raw learner text
- generated artifact body
- logits

Pointer metadata should not duplicate existing selective prediction or frozen
policy fixture bodies.

## 11. Safe Output Policy

Fixture expected output must be metadata-only.

Required output expectations:

- stdout is safe summary only
- JSON output is safe metadata only
- `content_suppressed=true`
- `no_raw_rows=true`
- generated artifact body is suppressed
- request body is suppressed
- input pointer body is suppressed
- private path output is suppressed

Body leakage should appear only as an intentional invalid fixture marker and
safe reason code. It should not include the leaked body itself.

## 12. Reason Code Mapping

Initial mapping:

- `invalid/missing_request` -> `missing_request`
- `invalid/malformed_request` -> `malformed_request`
- `invalid/missing_pointer` -> `missing_pointer`
- `invalid/malformed_pointer` -> `malformed_pointer`
- `invalid/unvalidated_input` -> `unvalidated_input`
- `invalid/missing_validation_split` -> `missing_validation_split`
- `invalid/selective_prediction_validator_failure` ->
  `selective_prediction_validator_failure`
- `invalid/frozen_policy_validator_failure` ->
  `frozen_policy_validator_failure`
- `invalid/test_temperature_tuning` -> `test_temperature_tuning`
- `invalid/test_threshold_tuning` -> `test_threshold_tuning`
- `invalid/raw_rows_carryover` -> `raw_rows_carryover`
- `invalid/logits_dump_carryover` -> `logits_dump_carryover`
- `invalid/generated_artifact_body_leakage` ->
  `generated_artifact_body_leakage`
- `invalid/private_path_output` -> `private_path_output`
- `invalid/performance_claim_generation` -> `performance_claim_generation`
- `invalid/body_dump_requested` -> `body_dump_requested`
- `invalid/real_data_path` -> `real_data_path`
- `invalid/participant_data_path` -> `participant_data_path`
- `invalid/manual_output_path` -> `manual_output_path`
- `invalid/no_oracle_violation` -> `no_oracle_violation`
- `invalid/scoring_feedback_violation` -> `scoring_feedback_violation`

Valid cases should use `reason_codes=[]` or an equivalent safe empty value.

## 13. Relation To Existing Generation Validation Fixtures

Existing root:

- `tests/fixtures/learner_state_frozen_policy_generation/`

Future scaffold root:

- `tests/fixtures/learner_state_frozen_policy_generation_scaffold/`

Relationship:

- do not copy existing root into the new scaffold root blindly
- do not paste existing fixture bodies into docs
- generation validation fixtures are validator-focused
- scaffold fixtures are scaffold API and CLI behavior-focused
- later integration can compare scaffold result with generation validator
  expected result
- existing fixtures should remain stable while scaffold fixture behavior is
  designed and implemented separately

## 14. Relation To Future Scaffold Implementation

Recommended staging:

1. Implement the scaffold fixture files in a later step.
2. Add a scaffold fixture validator or loader design if needed.
3. Implement scaffold API against the fixture contract.
4. Add scaffold CLI only after API behavior is stable.
5. Compare scaffold safe summaries against expected scaffold results.
6. Later, allow the generation validator to consume scaffold summaries.

No artifact body should be created or published until a private/local future
stage explicitly designs that behavior.

## 15. Testing Plan

Future tests should cover:

- deterministic fixture discovery
- all expected scaffold result files parse
- valid cases pass
- invalid cases fail with expected reason code
- no body fields in expected outputs
- no absolute or private paths in valid outputs
- no raw rows in stdout
- no logits in stdout
- no private paths in stdout
- JSON output parseable and safe
- scaffold result comparable to expected scaffold result
- later validator compatibility

This document does not implement tests.

## 16. Release-Quality Future

Scaffold fixtures should not immediately enter release-quality.

Recommended order:

1. scaffold fixture design
2. scaffold fixture implementation
3. scaffold API implementation
4. scaffold CLI design and implementation
5. scaffold Makefile target design and implementation
6. standalone log-safety review
7. release-quality integration design
8. wrapper integration
9. remote/manual run record workflow and status marker

The current release-quality generation validation remains the safety net while
scaffold behavior is still being designed.

## 17. What This Does Not Do

This design does not:

- create fixtures
- change existing fixtures
- implement scaffold code
- implement generator code
- create policy artifact bodies
- compute metrics
- fit calibration
- run selective prediction
- train an estimator
- use real data
- prove performance
- change Makefile
- change release-quality wrapper
- change GitHub Actions workflow
- change Python code
- change tests

## 18. Beginner-Friendly Explanation

A scaffold fixture is a synthetic test case for the future scaffold. It says:
given this safe request and this safe input pointer, the scaffold should return
this safe result.

The fixture design comes before code so the expected behavior is clear before
implementation starts.

Valid fixtures describe safe requests that should pass. Invalid fixtures
describe unsafe requests that should fail closed.

The expected result file is the answer key for the scaffold. It should contain
only status, reason codes, and safety flags.

Bodies are excluded because bodies can accidentally contain rows, labels,
private paths, or future information. The public contract should stay
metadata-only.

Release-quality should not include scaffold fixtures immediately because new
scaffold behavior should first prove its standalone output is safe.

## 19. Next Recommended Steps

Candidate next steps:

- initial scaffold fixtures implementation
- scaffold fixture validator design
- scaffold API implementation
- scaffold CLI design

Comparison:

- initial scaffold fixtures implementation is safe if this fixture contract is
  stable and the next step remains metadata-only
- scaffold fixture validator design is safer if the team wants another
  fail-closed contract review before adding files

Recommended next step:

- initial scaffold fixtures implementation, as long as it creates only
  synthetic metadata fixture files and does not add scaffold code

If uncertainty remains about expected result matching, choose scaffold fixture
validator design first.

Step250 implements the initial scaffold fixture root at
`tests/fixtures/learner_state_frozen_policy_generation_scaffold/`.
It adds three valid metadata-only dry-run cases and eight representative
invalid metadata-only cases. Scaffold code, scaffold fixture validation code,
generator code, CLI, Makefile targets, release-quality wrapper changes,
workflow changes, Python tests, and existing fixtures remain unchanged.

Step251 designs a future scaffold fixture validator for this root. The design
keeps validator implementation out of scope while defining root-level checks,
case-level checks, forbidden field/value scans, expected reason-code matching,
and safe summary behavior.

Step252 implements that minimal fixture validator and unit tests without
changing scaffold fixtures, scaffold runtime code, generator code, CLI,
Makefile targets, release-quality wrapper, or workflow files.

Step253 designs the future CLI for the scaffold fixture validator. It keeps
the current fixture root unchanged and specifies only a future safe command
surface for fixture-root and single-case validation.

Step254 implements the minimal scaffold fixture validator CLI and tests
without changing the scaffold fixture root.

## 20. Update History

- Step249: initial frozen policy generation scaffold fixture design.
- Step250: initial scaffold fixture files created under
  `tests/fixtures/learner_state_frozen_policy_generation_scaffold/`.
- Step251: linked the scaffold fixture validator design.
- Step252: linked the minimal scaffold fixture validator implementation.
- Step253: linked the scaffold fixture validator CLI design.
- Step254: linked the scaffold fixture validator CLI implementation.

## Related Documents

- [Frozen policy generation scaffold fixtures](../tests/fixtures/learner_state_frozen_policy_generation_scaffold/README.md)
- [Frozen policy generation scaffold fixture validator design](frozen_policy_generation_scaffold_fixture_validator_design.md)
- [Frozen policy generation scaffold fixture validator CLI design](frozen_policy_generation_scaffold_fixture_validator_cli_design.md)
- [Frozen policy generation scaffold implementation design](frozen_policy_generation_scaffold_implementation_design.md)
- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Frozen policy generation fixture design](frozen_policy_generation_fixture_design.md)
- [Frozen policy generation validation design](frozen_policy_generation_validation_design.md)
- [Frozen policy generation validator CLI design](frozen_policy_generation_validator_cli_design.md)
- [Frozen policy generation validator Makefile target design](frozen_policy_generation_validator_makefile_target_design.md)
- [Frozen policy generation release-quality integration design](frozen_policy_generation_release_quality_integration_design.md)
- [Milestone 11 frozen policy generation validation infrastructure recap](milestone_11_frozen_policy_generation_validation_infrastructure_recap.md)
- [Public release checklist](public_release_checklist.md)
