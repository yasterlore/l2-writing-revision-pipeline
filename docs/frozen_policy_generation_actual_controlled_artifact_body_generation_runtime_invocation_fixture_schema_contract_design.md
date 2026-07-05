# Actual-Controlled Artifact Body Generation Runtime Invocation Fixture Schema Contract Design

## 1. Title

Actual-Controlled Artifact Body Generation Runtime Invocation Fixture Schema Contract Design

## 2. Scope

This document designs the fixture/schema contract for a future actual-controlled artifact body generation runtime invocation boundary. It is a docs-only / design-only contract document.

This step does not:

- perform fixture root creation
- create fixture JSON
- implement a fixture validator
- implement runtime behavior
- perform actual artifact body generation runtime invocation
- change Makefile targets
- change the release-quality wrapper
- change workflow files
- implement manifest writer integration
- perform file writing
- prove production readiness
- prove real-data readiness
- prove model performance

## 3. Prior Chain Dependency

Prior chain dependency:

- Step569-Step574: planned-only runtime invocation fixture / validator / target chain established the first metadata-only / body-free synthetic fixture boundary and validator target for planned-only runtime invocation.
- Step575-Step579: planned-only v0.3 runtime mode / target chain added the planned-only `artifact-body-runtime-invocation` marker and target while keeping runtime invocation not performed.
- Step580-Step583: release-quality integration / remote status marker chain added adjacent wrapper checks and a public-safe remote status marker.
- Step584: planned-only v0.3 release-quality chain final safety review concluded the chain is acceptable only as a planned-only release-quality boundary.
- Step585: actual controlled invocation design recommended a separate fixture/schema contract before implementation.

Actual-controlled invocation code is not part of the current boundary.

## 4. Contract Design Question

Main question:

- What fixture root, schemas, layout, case taxonomy, expected output contract, and safety mapping are required before implementing actual-controlled artifact body generation runtime invocation?

Secondary questions:

- Should the new root be separate from Step570 planned-only root?
- What files should each case contain?
- How many valid and invalid cases should be included in the initial fixture root?
- What schema versions should be recorded?
- What expected output fields must future runtime emit?
- Which unsafe signals must be represented as metadata-only markers?
- How should future validator map pass / usage_error / fail_closed / mismatch?
- What future implementation should remain out of scope?

## 5. Proposed Fixture Root

Recommended future root:

- `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled/`

Contract points:

- this is a new future root
- it should not replace the Step570 planned-only root
- it should not be merged into the Step570 root
- it should be created in Step587, not Step586
- it should contain synthetic metadata-only cases only

## 6. Proposed Schemas and Modes

Recommended names:

- fixture schema: `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled_fixture_v0.1`
- fixture validation schema: `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled_fixture_validation_v0.1`
- future runtime schema: `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4`
- integration mode: `artifact-body-runtime-invocation-controlled`
- optional command flag: `--actual-invocation`

Distinction:

- v0.3 / `artifact-body-runtime-invocation`: planned-only marker, not actual invocation
- v0.4 / `artifact-body-runtime-invocation-controlled`: future actual controlled metadata-only invocation behavior

## 7. Proposed Case Layout

Each case should use a 7-file layout:

- `case_metadata.json`
- `artifact_body_runtime_request_metadata.json`
- `artifact_body_runtime_pointer_metadata.json`
- `artifact_body_generation_cli_metadata.json`
- `expected_runtime_invocation_summary.json`
- `residue_policy_metadata.json`
- `expected_error.json`

File roles:

- `case_metadata.json`: case id, case group, fixture schema, expected status, expected reason, synthetic-only/no-oracle notices
- `artifact_body_runtime_request_metadata.json`: request metadata only, no request body
- `artifact_body_runtime_pointer_metadata.json`: pointer metadata only, no pointer body
- `artifact_body_generation_cli_metadata.json`: future CLI invocation metadata, exit-code category, stdout/stderr scan flags, no raw stdout/stderr body
- `expected_runtime_invocation_summary.json`: expected public-safe summary fields, no expected body
- `residue_policy_metadata.json`: temp root / residue count policy, no private or absolute path values
- `expected_error.json`: expected error class / reason code only, no body payload

No JSON body examples are included in this design.

## 8. Proposed Initial Case Taxonomy

Recommended initial fixture root size:

- valid cases: 6
- invalid cases: 30
- total cases: 36
- JSON files per case: 7
- total JSON files: 252

Proposed valid cases:

- `valid_actual_controlled_safe_metadata_invocation`
- `valid_actual_controlled_cli_output_body_free`
- `valid_actual_controlled_no_file_writing`
- `valid_actual_controlled_no_manifest_writer`
- `valid_actual_controlled_stdout_stderr_suppressed`
- `valid_actual_controlled_no_residue`

Proposed invalid cases:

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

This taxonomy keeps the initial contract broad enough to cover usage errors, fail-closed body/payload risks, invocation-mode risks, writer risks, and one mismatch case without embedding payload values.

## 9. Expected Aggregate for Future Fixture Validator

Expected future aggregate output:

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
- missing_required_file_cases: 1
- malformed_json_cases: 1
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

Reason-code counts must remain count-only and body-free.

## 10. Expected Future Runtime Pass Output Contract

Expected future v0.4 runtime pass output for `valid/valid_actual_controlled_safe_metadata_invocation` should include public-safe summary fields such as:

- mode=artifact_body_generation_runtime_integration
- runtime_schema_version=learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4
- status=pass
- reason_code=none
- exit_code_category=zero
- case_id=valid/valid_actual_controlled_safe_metadata_invocation
- integration_mode=artifact-body-runtime-invocation-controlled
- artifact_body_runtime_invoked=True
- artifact_body_runtime_invocation_planned=False
- artifact_body_runtime_mode=controlled_metadata_only_invocation
- artifact_body_generation_cli_invoked=True
- artifact_body_generation_cli_exit_code_category=zero
- artifact_body_generation_cli_output_scanned=True
- artifact_body_generation_cli_output_body_free=True
- artifact_body_payload_available=False
- artifact_body_payload_emitted=False
- artifact_body_payload_detected=False
- safe_metadata_body_available=True
- safe_metadata_body_field_count=count-only value
- content_suppressed=True
- body_suppressed=True
- summary_only=True
- request_body_detected=False
- pointer_body_detected=False
- expected_body_detected=False
- manifest_body_detected=False
- generated_policy_body_detected=False
- raw_stdout_body_suppressed=True
- raw_stderr_body_suppressed=True
- raw_rows_detected=False
- logits_detected=False
- probabilities_detected=False
- private_path_detected=False
- absolute_path_detected=False
- raw_learner_text_detected=False
- real_data_marker_detected=False
- performance_metric_body_detected=False
- file_writing_enabled=False
- file_writing_detected=False
- manifest_writer_invoked=False
- artifact_file_written=False
- manifest_file_written=False
- runtime_safety_scan_passed=True
- runtime_fail_closed=False
- residue_file_count=0
- production_readiness_claimed=False
- real_data_readiness_claimed=False
- performance_claims_present=False
- metadata_file_count=7
- unsafe_signal_count=0

## 11. Expected Status / Reason Mapping

### pass

Valid cases:

- expected status pass
- expected reason none
- body-free output
- CLI exit-code category zero
- no unsafe markers
- no manifest writer
- no file writing
- no residue

### usage_error

Usage-error cases:

- unsupported schema
- missing required metadata file
- malformed metadata JSON

### mismatch

Mismatch case:

- mismatched expected status

### fail_closed

Unsafe cases:

- request body present
- pointer body present
- expected body present
- artifact body payload present
- manifest body present
- generated policy body present
- raw stdout/stderr body present
- raw rows present
- logits/probabilities present
- private/absolute path present
- raw learner text present
- real data marker present
- performance metric body present
- file writing requested/detected
- manifest writer requested/invoked
- unsafe artifact body runtime mode
- no-oracle forbidden field
- unsafe output residue risk
- artifact body CLI nonzero exit
- artifact body CLI output not body-free
- unexpected artifact body generation request

## 12. Actual-Controlled Safety Scan Contract

The future implementation and validator must scan:

- fixture metadata
- runtime request metadata
- pointer metadata
- artifact body generation CLI metadata
- stdout/stderr summary flags
- expected runtime invocation summary
- residue policy metadata
- runtime output summary

The scan must detect only public-safe markers and suppress raw values.

The scan must verify:

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

## 13. Relationship to Existing Fixture Roots

Relationship to existing fixture roots:

- Step570 root remains planned-only
- new actual-controlled root should be separate
- existing runtime invocation fixture validator target remains unchanged
- existing planned-only v0.3 target remains unchanged
- existing release-quality checks remain unchanged
- actual-controlled root should not replace artifact body generation safe-metadata fixtures
- actual-controlled root should not replace manifest writer fixtures
- actual-controlled root should not introduce file writing

## 14. Future Validator Requirements

The future validator must check:

- root exists
- valid / invalid directories exist
- README exists
- total case counts
- exact 7-file layout
- no unexpected JSON files
- JSON parse for all files except intentionally malformed case handling
- case id / directory consistency
- schema consistency
- expected status / reason mapping
- safety marker mapping
- public-safe output policy
- count-only reason-code summary
- no fixture JSON body printed
- no payload/body printed
- root errors count-only

## 15. Future Implementation Test Plan

Future tests should include:

- fixture root count tests
- file layout tests
- schema tests
- valid case pass mapping
- usage_error mapping
- fail_closed mapping
- mismatch mapping
- no raw body output
- no private/absolute path output
- no residue
- v0.3 planned-only compatibility
- v0.2 safe-metadata compatibility
- v0.1 plan-only compatibility
- artifact body generation safe-metadata CLI smoke compatibility
- manifest writer not invoked
- file writing not enabled

## 16. Future Staging

Recommended next chain:

- Step587: actual-controlled fixture root creation
- Step588: actual-controlled fixture validator design
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

Do not perform these in Step586.

## 17. Recommended Next Step

Step587 actual-controlled fixture root is recorded in
`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled/README.md`.

Step588 fixture validator design is recorded in
`docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validator_design.md`.

Recommended next step after Step588:

- Step589: actual-controlled fixture validator implementation

Do not recommend direct runtime implementation.

## 18. Non-Equivalence Cautions

Non-equivalence cautions:

- fixture/schema contract design is not fixture root creation
- fixture/schema contract design is not actual invocation implementation
- future fixture validator pass is not runtime correctness generally
- future actual-controlled runtime pass is not artifact body payload correctness
- planned-only v0.3 pass remains not actual invocation
- artifact body generation safe-metadata CLI smoke is not equivalent to actual-controlled runtime invocation
- count-only metadata is not free-form body safety proof
- manifest writer validators are separate
- release-quality success is not production readiness
- synthetic-only pass is not real-data readiness

## 19. Non-Claims

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

## 20. Public-Safe Checklist

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


## Step589 Validator Implementation Reference

Step589 adds the standalone actual-controlled fixture validator module and focused tests for the Step587 root. The validator consumes the schema and 7-file layout designed here and reports the expected public-safe aggregate without changing fixture JSON, invoking runtime code, invoking manifest writer code, or writing files. Step590 is expected to design a Makefile target for this validator.


## Step590 Makefile Target Design Reference

Step590 designs a future standalone Makefile target for the Step589 validator that consumes this fixture/schema contract. The target is not implemented in Step590, and release-quality wrapper integration remains deferred.


## Step591 Makefile Target Implementation Reference

Step591 implements the standalone Makefile target for the Step589 validator against this fixture/schema contract. The fixture JSON remains unchanged, and release-quality wrapper integration, actual runtime invocation, manifest writer integration, and file writing remain deferred.


## Step592 Implementation Refinement Design Reference

Step592 adds the implementation refinement design for the future v0.4 runtime behavior that consumes this fixture/schema contract. The fixture JSON remains unchanged, and Makefile, wrapper, workflow, manifest writer, and file-writing changes remain out of scope in Step592.

## Step593 Runtime Implementation Reference

Step593 consumes this contract for the selected actual-controlled primary case through v0.4 `artifact-body-runtime-invocation-controlled` runtime CLI behavior. The fixture JSON remains unchanged, and Step593 does not change Makefile, wrapper, workflow, manifest writer integration, or file writing.

## Step594 Makefile Target Design Reference

Step594 adds a design-only / docs-only plan for a future standalone Makefile target around the Step593 v0.4 runtime CLI. This fixture/schema contract remains unchanged, and Step594 does not change Makefile, wrapper, workflow, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step595 Makefile Target Implementation Reference

Step595 adds the standalone Makefile target for the Step593 v0.4 runtime CLI that consumes this fixture/schema contract's selected primary case. Fixture JSON remains unchanged, and Step595 does not change wrapper, workflow, Python code/tests, runtime implementation, manifest writer integration, or file writing.

## Step596 Release-Quality Integration Design Reference

Step596 adds a design-only / docs-only plan for future release-quality wrapper
integration of the actual-controlled fixture validator target and v0.4 runtime
smoke target. This fixture/schema contract and fixture JSON remain unchanged.

## Step597 Release-Quality Integration Status

Step597 adds release-quality wrapper checks for the actual-controlled fixture
validator target and v0.4 runtime smoke target. This fixture/schema contract
and fixture JSON remain unchanged, and manifest writer integration and file
writing remain out of scope.

## Step598 Remote Run Record Workflow Reference

Step598 adds a design-only / docs-only workflow for a future status marker for
the Step597 wrapper checks. This fixture/schema contract and fixture JSON
remain unchanged.

## Step599 Remote Run Status Reference

Step599 adds the public-safe remote run status marker for the Step597 wrapper
checks. This fixture/schema contract and fixture JSON remain unchanged.

## Step600 Final Safety Review Reference

Step600 adds
`docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_release_quality_chain_final_safety_review.md`
as the final-safety-review / docs-only review for the Step585-Step599
actual-controlled release-quality chain. This fixture/schema contract remains
unchanged, and Step600 does not change fixture JSON, validator implementation,
runtime implementation, manifest writer integration, or file writing.

## Step601 Planning Reference

Step601 adds
`docs/frozen_policy_generation_actual_controlled_post_final_safety_review_next_boundary_planning.md`
as a planning-only / docs-only next-boundary plan after Step600. This
fixture/schema contract remains unchanged.

## Step602 Design Reference

Step602 adds
`docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_design.md`
as a design-only / docs-only plan for a future all-valid multi-case runtime
smoke. This fixture/schema contract remains unchanged.
