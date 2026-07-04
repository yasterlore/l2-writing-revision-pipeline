# Actual-Controlled Artifact Body Generation Runtime Invocation Fixture Validator Design

## 1. Title

Actual-Controlled Artifact Body Generation Runtime Invocation Fixture Validator Design

## 2. Scope

This document designs a future validator for the Step587 actual-controlled fixture root. It is a design-only / docs-only step.

This step does not:

- implement a validator
- change Python code/tests
- change Makefile targets
- change the release-quality wrapper
- change workflow files
- change fixture JSON
- change runtime implementation
- perform actual artifact body generation runtime invocation
- implement manifest writer integration
- perform file writing
- prove production readiness
- prove real-data readiness
- prove model performance

## 3. Prior Chain Dependency

Prior chain dependency:

- Step569-Step574: planned-only runtime invocation fixture / validator / target chain established the Step570 planned-only root and the validator/target boundary for that root.
- Step575-Step579: planned-only v0.3 runtime mode / target chain added the planned-only `artifact-body-runtime-invocation` mode and target while keeping actual invocation not performed.
- Step580-Step583: release-quality integration / remote status marker chain added adjacent wrapper checks and recorded public-safe status evidence for the planned-only chain.
- Step584: planned-only v0.3 release-quality chain final safety review concluded that chain is acceptable only as a planned-only boundary.
- Step585: actual controlled invocation design proposed a separate future v0.4 actual-controlled boundary.
- Step586: actual-controlled fixture/schema contract design defined the future root, schemas, case taxonomy, layout, and expected aggregate.
- Step587: actual-controlled fixture root creation created the new root and parseable metadata-only JSON files.

Step587 created the new root, but no actual-controlled validator exists yet.

Actual-controlled runtime invocation is not implemented yet.

## 4. Target Fixture Root

Target fixture root:

- `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled/`

Expected root summary:

- valid cases: 6
- invalid cases: 30
- total cases: 36
- JSON files per case: 7
- total JSON files: 252
- root README: 1
- all JSON parseable
- exact layout complete
- missing-file / malformed-json cases are metadata marker cases in root, not physical missing/malformed files

## 5. Proposed Validator Module And CLI

Recommended future module:

- `python/learner_state/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validation.py`

Recommended future test file:

- `python/learner_state/tests/test_frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validation.py`

Recommended future CLI, not implemented in Step588:

- `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled`

Do not implement these in Step588.

## 6. Proposed Validation Schema And Mode

Recommended validator names:

- validation schema: `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled_fixture_validation_v0.1`
- validator mode: `artifact_body_generation_runtime_invocation_actual_controlled_fixture_validation`
- accepted fixture schema: `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled_fixture_v0.1`
- accepted future runtime schema: `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4`
- accepted integration mode: `artifact-body-runtime-invocation-controlled`

The v0.3 planned-only schema and root remain separate.

## 7. Required 7-File Layout Checks

The validator should require exactly these files in every case:

- `case_metadata.json`
- `artifact_body_runtime_request_metadata.json`
- `artifact_body_runtime_pointer_metadata.json`
- `artifact_body_generation_cli_metadata.json`
- `expected_runtime_invocation_summary.json`
- `residue_policy_metadata.json`
- `expected_error.json`

The validator should check:

- no missing required files
- no unexpected JSON files
- each case has exactly 7 JSON files
- all JSON parse
- case id matches directory name
- case group matches parent directory
- valid / invalid directory structure is correct
- root README exists
- no unexpected top-level JSON files

## 8. Expected Aggregate Output

Expected public-safe aggregate output:

- mode: `artifact_body_generation_runtime_invocation_actual_controlled_fixture_validation`
- validation_schema_version: `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled_fixture_validation_v0.1`
- fixture_root: `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled`
- total_cases: 36
- valid_cases: 6
- invalid_cases: 30
- total_json_files: 252
- json_files_per_case: 7
- matched_cases: 36
- mismatched_cases: 0
- input_error_cases: 0
- pass_cases: 6
- usage_error_cases: 3
- fail_closed_cases: 26
- mismatch_cases: 1
- expected_missing_required_metadata_file_cases: 1
- expected_malformed_metadata_json_cases: 1
- physical_missing_required_file_cases: 0
- physical_malformed_json_cases: 0
- content_suppressed: true
- body_suppressed: true
- metadata_only_checked: true
- synthetic_only_checked: true
- no_oracle_checked: true
- no_request_body: true
- no_pointer_body: true
- no_expected_body: true
- no_artifact_body_payload: true
- no_manifest_body: true
- no_generated_policy_body: true
- no_raw_stdout_body: true
- no_raw_stderr_body: true
- no_raw_rows: true
- no_logits_dump: true
- no_probabilities_dump: true
- no_private_paths: true
- no_absolute_paths: true
- no_raw_learner_text: true
- no_real_participant_data: true
- no_performance_metric_body: true
- file_writing_checked: true
- manifest_writer_integration_checked: true
- actual_controlled_runtime_invocation_checked: true
- production_readiness_claimed: false
- real_data_readiness_claimed: false
- performance_claims_present: false
- root_errors: []

Reason-code counts must be count-only and body-free.

## 9. Expected Case Taxonomy

The validator should verify all required IDs exist.

Valid cases:

- `valid_actual_controlled_safe_metadata_invocation`
- `valid_actual_controlled_cli_output_body_free`
- `valid_actual_controlled_no_file_writing`
- `valid_actual_controlled_no_manifest_writer`
- `valid_actual_controlled_stdout_stderr_suppressed`
- `valid_actual_controlled_no_residue`

Invalid cases:

- `invalid_unsupported_schema`
- `invalid_missing_required_metadata_file`
- `invalid_malformed_metadata_json`
- `invalid_mismatched_expected_status`
- `invalid_request_body_present`
- `invalid_pointer_body_present`
- `invalid_expected_body_present`
- `invalid_artifact_body_payload_present`
- `invalid_manifest_body_present`
- `invalid_generated_policy_body_present`
- `invalid_raw_stdout_body_present`
- `invalid_raw_stderr_body_present`
- `invalid_raw_rows_present`
- `invalid_logits_present`
- `invalid_probabilities_present`
- `invalid_private_path_present`
- `invalid_absolute_path_present`
- `invalid_raw_learner_text_present`
- `invalid_real_data_marker_present`
- `invalid_performance_metric_body_present`
- `invalid_file_writing_requested`
- `invalid_file_writing_detected`
- `invalid_manifest_writer_requested`
- `invalid_manifest_writer_invoked`
- `invalid_unsafe_artifact_body_runtime_mode`
- `invalid_no_oracle_forbidden_field`
- `invalid_unsafe_output_residue_risk`
- `invalid_artifact_body_cli_nonzero_exit`
- `invalid_artifact_body_cli_output_not_body_free`
- `invalid_unexpected_artifact_body_generation_request`

## 10. Expected Status / Reason Mapping

### pass

Valid cases:

- status: `pass`
- reason_code: `none`

### usage_error

Usage-error cases:

- `invalid_unsupported_schema`
- `invalid_missing_required_metadata_file`
- `invalid_malformed_metadata_json`

### mismatch

Mismatch case:

- `invalid_mismatched_expected_status`

### fail_closed

Fail-closed cases:

- all other invalid cases

## 11. Safety Checks

The validator must check only public-safe markers and must not print raw values.

It should verify:

- no request body values
- no pointer body values
- no expected body values
- no artifact body payload values
- no manifest body values
- no generated policy body values
- no raw stdout/stderr body values
- no raw rows
- no logits/probabilities
- no private/absolute path values
- no raw learner text
- no real participant data
- no performance metric body
- no file writing
- no manifest writer invocation
- no unexpected residue

Important nuance:

- invalid cases may contain boolean/count-only markers such as unsafe-signal booleans or marker counts
- those markers are allowed when metadata-only and body-free
- validator should fail only if raw body/value fields are present, not merely because an invalid case has an unsafe marker

## 12. Public-Safe Output Policy

Validator output may include:

- mode
- validation schema
- fixture root as repository-relative path
- case counts
- JSON counts
- status class counts
- reason-code counts
- boolean safety checks
- root errors as empty list or count-only summary

Validator output must not include:

- fixture JSON body
- request body
- pointer body
- expected body
- artifact body payload
- manifest body
- generated policy body
- raw stdout/stderr body
- raw rows
- logits/probabilities
- private/absolute path values
- raw learner text
- real participant data
- performance metric body

## 13. Proposed Focused Tests For Step589

Future focused tests should include:

- aggregate counts match 36 / 6 / 30 / 252
- exact 7-file layout enforced
- all JSON parse
- required case taxonomy exists
- valid cases map to pass
- unsupported schema maps to usage_error
- missing required metadata marker maps to usage_error
- malformed metadata marker maps to usage_error
- mismatched expected status maps to mismatch
- unsafe invalid markers map to fail_closed
- reason-code counts are count-only
- output includes required public-safe flags
- output does not include raw body fields
- output does not include private / absolute path values
- physical missing file in temp copy maps to input_error
- physical malformed JSON in temp copy maps to input_error
- unexpected JSON file in temp copy maps to input_error
- duplicate case id in temp copy maps to input_error if easy to simulate safely
- existing planned-only runtime invocation fixture validator target still passes
- existing planned-only v0.3 runtime target still passes
- existing artifact body generation safe-metadata CLI smoke still passes
- no fixture JSON mutation

Use temporary copies for mutation tests.

## 14. Relationship To Existing Validators And Roots

This future validator:

- does not replace Step570 planned-only fixture root
- does not replace planned-only runtime invocation fixture validator
- does not replace planned-only v0.3 runtime target
- does not replace safe-metadata fixture validator
- does not replace artifact body generation fixture validator
- does not replace artifact body safe-metadata CLI smoke
- does not replace manifest writer validators
- does not invoke actual runtime
- does not invoke manifest writer
- does not write files
- is not release-quality integrated

## 15. Future Staging

Recommended next chain:

- Step589: actual-controlled fixture validator implementation
- Step590: actual-controlled fixture validator Makefile target design
- Step591: actual-controlled fixture validator Makefile target implementation
- Step592: actual-controlled runtime implementation refinement design
- Step593: actual-controlled runtime implementation
- Step594: actual-controlled runtime Makefile target design
- Step595: actual-controlled runtime Makefile target implementation
- Step596: release-quality integration design
- Step597: release-quality wrapper integration
- Step598: remote/manual run record workflow design
- Step599: remote status marker
- Step600: final safety review

Do not perform these in Step588.

## 16. Recommended Next Step

Recommended next step:

- Step589: actual-controlled fixture validator implementation

Do not recommend direct runtime implementation.

## 17. Non-Equivalence Cautions

Non-equivalence cautions:

- fixture validator design is not validator implementation
- fixture validator pass will not prove runtime correctness generally
- fixture validator pass will not prove artifact body payload correctness
- actual-controlled fixture root is not actual runtime invocation
- planned-only v0.3 pass remains not actual invocation
- artifact body generation safe-metadata CLI smoke is not equivalent to actual-controlled runtime invocation
- count-only metadata is not free-form body safety proof
- manifest writer validators are separate
- release-quality success is not production readiness
- synthetic-only pass is not real-data readiness

## 18. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- artifact body generation integration correctness
- artifact body generation runtime correctness generally
- manifest writer integration correctness
- manifest writer file-writing production readiness
- artifact body payload correctness
- safe-metadata free-form body safety
- manifest body generation correctness
- generated policy quality
- learner-state estimator correctness
- artifact writer CLI actual invocation correctness generally
- runtime actual invocation correctness generally

## 19. Public-Safe Checklist

- [x] no raw logs
- [x] no full job output
- [x] no copied GitHub log blocks
- [x] no screenshots containing raw logs
- [x] no fixture JSON body
- [x] no request body
- [x] no pointer body
- [x] no expected body
- [x] no written file JSON body
- [x] no manifest body
- [x] no artifact body payload
- [x] no generated policy body
- [x] no raw stdout/stderr body
- [x] no raw rows
- [x] no logits/probabilities
- [x] no private paths
- [x] no absolute paths
- [x] no raw learner text
- [x] no real participant data
- [x] no performance claims
- [x] no production readiness claims
- [x] no real-data readiness claims


## Step589 Implementation Status

Step589 implements this design as the standalone module `python/learner_state/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validation.py` with focused tests at `python/learner_state/tests/test_frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validation.py`. The direct CLI validates the Step587 root and emits public-safe key-value metadata only. Makefile target design remains the next step: Step590. Runtime invocation, manifest writer integration, file writing, release-quality wrapper integration, workflow changes, and fixture JSON changes remain out of scope.


## Step590 Makefile Target Design Reference

Step590 adds `docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validator_makefile_target_design.md` as the design-only handoff for a future standalone Makefile target around the Step589 validator. Step590 does not implement the target or change Makefile, wrapper, workflow, Python code/tests, fixture JSON, runtime implementation, manifest writer integration, or file writing.


## Step591 Makefile Target Implementation Reference

Step591 adds the standalone Makefile target `check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation-fixtures` for the Step589 validator. It remains outside release-quality and does not invoke actual artifact body generation runtime, manifest writer, or file writing.
