# Actual Controlled Artifact Body Generation Runtime Invocation Design

## 1. Title

Actual Controlled Artifact Body Generation Runtime Invocation Design

## 2. Scope

This design doc describes how the project should move from the planned-only v0.3 `artifact-body-runtime-invocation` boundary toward a future actual controlled artifact body generation runtime invocation while preserving synthetic-only / metadata-only / body-free / no-oracle safety.

This is a design-only / docs-only step.

This step does not:

- implement actual invocation
- change Python code/tests
- change Makefile targets
- change the release-quality wrapper
- change workflow files
- change fixture JSON
- change validator implementation
- implement manifest writer integration
- perform file writing
- prove production readiness
- prove real-data readiness
- prove model performance

## 3. Prior Chain Reviewed

The prior Step569-Step584 chain is reviewed as follows:

- Step569-Step574: runtime invocation fixture contract / root / validator / target chain. These steps designed and added a metadata-only / body-free synthetic fixture root, validator, and standalone fixture validator target for the planned boundary.
- Step575-Step579: planned-only v0.3 runtime mode and target chain. These steps designed and added planned-only runtime markers and a standalone target while keeping actual invocation disabled.
- Step580-Step583: release-quality integration and remote status marker chain. These steps designed and integrated adjacent wrapper checks and recorded a public-safe remote status marker.
- Step584: final safety review completed. It concluded that the Step569-Step583 chain is acceptable only as a planned-only v0.3 runtime invocation release-quality boundary.

Actual controlled invocation has not been implemented.

## 4. Design Question

Main question:

- How should the project move from planned-only v0.3 `artifact-body-runtime-invocation` to actual controlled artifact body generation runtime invocation while preserving metadata-only / body-free / synthetic-only / no-oracle safety?

Secondary questions:

- Should actual invocation reuse the existing runtime integration module or use a dedicated module?
- Should actual invocation reuse v0.3 schema or introduce v0.4 schema?
- Should actual invocation use the existing Step570 fixture root or require a new actual-invocation fixture root?
- Should actual invocation invoke the artifact body generation module directly in-process or via controlled subprocess CLI?
- What must be captured and scanned?
- What must remain out of scope?
- What Step should come before implementation?

## 5. Option Comparison

### Option A: Existing Runtime Module + New v0.4 Actual-Controlled Mode

Description:

- extend `python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py`
- keep existing v0.3 planned-only behavior unchanged
- add a new actual-controlled behavior under an explicit mode or flag
- emit a new schema such as `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4`
- run artifact body generation only in controlled metadata-only mode
- capture and scan public-safe stdout/stderr summaries
- suppress all body payloads
- do not invoke manifest writer
- do not write files

Benefits:

- reuses existing runtime integration entrypoint and safety idioms
- keeps one integration surface for plan-only bridge, safe-metadata smoke, planned-only invocation, and future actual-controlled invocation
- can preserve backwards compatibility if mode and schema separation are explicit

Risks:

- module responsibilities may become ambiguous if v0.4 behavior is not clearly separated
- implementation must prevent v0.3 planned-only behavior from drifting into actual invocation semantics

Implementation complexity:

- moderate

Safety boundary clarity:

- acceptable only with explicit v0.4 schema, explicit actual-controlled mode, and fail-closed checks

### Option B: Dedicated Actual-Controlled Runtime Invocation Module

Description:

- create a new module for actual controlled artifact body generation runtime invocation
- keep existing runtime integration module unchanged
- use a separate CLI, schema, fixture root, and validator chain

Benefits:

- strongest separation between planned-only and actual-controlled surfaces
- lowers the risk of accidentally changing v0.3 semantics
- makes release-quality staging easier to reason about as a new chain

Risks:

- increases code surface and docs/target surface
- may duplicate safety scan logic unless shared helpers are carefully factored later

Implementation complexity:

- moderate to high

Safety boundary clarity:

- strong

### Option C: Reuse v0.3 Planned-Only Schema for Actual Invocation

Description:

- extend v0.3 behavior with actual invocation semantics

Benefits:

- lower schema churn
- fewer new labels and docs references

Risks:

- blurs planned-only and actual invocation boundaries
- makes Step584 conclusions ambiguous
- increases risk that planned-only pass is later misread as actual invocation evidence

Implementation complexity:

- low to moderate

Safety boundary clarity:

- weak

Recommendation for this option:

- not recommended

### Option D: Additional Fixture/Schema Design Before Actual Implementation

Description:

- do not implement actual invocation immediately
- first design a new fixture root, schema, expected-output contract, and validator for actual-controlled invocation

Benefits:

- safest path if the current Step570 fixture root is insufficient
- makes expected public-safe output and failure mapping explicit before code changes
- preserves the Step570 root as a planned-only boundary

Risks:

- adds another design step before implementation

Implementation complexity:

- low for the next step, moderate for the later chain

Safety boundary clarity:

- strongest

## 6. Recommended Design Direction

Recommended direction:

- prefer a new actual-controlled schema version, likely v0.4, rather than changing v0.3 semantics
- keep v0.3 planned-only behavior unchanged
- prefer extending the existing runtime integration module only if mode/schema separation remains explicit
- prefer a dedicated module if existing module boundaries become ambiguous during detailed fixture/schema design
- do not reuse v0.3 planned-only output as actual invocation evidence
- do not implement actual invocation until a fixture/schema/expected-output contract for actual-controlled invocation is designed
- do not invoke manifest writer
- do not write files
- do not generate or emit artifact body payload bodies

The safest next step is Option D: create an actual-controlled fixture/schema contract design before implementation. After that contract exists, Option A and Option B can be re-evaluated with more concrete schema and fixture requirements.

## 7. Proposed Future Schema and Mode

Proposed future runtime schema:

- `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4`

Proposed future integration mode:

- `artifact-body-runtime-invocation-controlled`

Alternative only if the existing mode is retained:

- use existing `artifact-body-runtime-invocation` plus explicit `--actual-invocation`, but only with v0.4 schema and unambiguous fields

Difference between v0.3 and proposed v0.4:

- v0.3: planned-only marker, no actual invocation
- v0.4: actual controlled metadata-only invocation, stdout/stderr scanned, no body emitted, no file writing, no manifest writer

## 8. Proposed Future CLI

If extending the existing runtime module, the future CLI should be shaped as a summary-only, fail-closed invocation. Proposed command form, not implemented in this step:

- `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_generation_runtime_integration --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled --fixture-case valid/valid_actual_controlled_safe_metadata_invocation --mode artifact-body-runtime-invocation-controlled --actual-invocation --summary-only --no-file-writing --no-manifest-writer --fail-closed-on-unsafe-output`

If a dedicated module is selected later, the alternative proposed form is:

- `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_generation_actual_controlled_runtime_invocation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled --fixture-case valid/valid_actual_controlled_safe_metadata_invocation --summary-only --no-file-writing --no-manifest-writer --fail-closed-on-unsafe-output`

The second form is an alternative only if a dedicated module is selected in a later design/implementation chain.

The fixture root in these commands is proposed only. It is not created in this step.

## 9. Proposed Fixture Strategy

Recommended fixture strategy:

- create a new planned fixture root for actual-controlled invocation before implementation
- do not mutate the existing Step570 fixture root unless a future contract proves it is sufficient
- keep the Step570 root as the planned-only runtime invocation fixture root

Proposed new root:

- `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled/`

Possible future layout:

- `case_metadata.json`
- `artifact_body_runtime_request_metadata.json`
- `artifact_body_runtime_pointer_metadata.json`
- `artifact_body_generation_cli_metadata.json`
- `expected_runtime_invocation_summary.json`
- `expected_error.json`
- optional `residue_policy_metadata.json`

This root is not created in Step585.

## 10. Expected Future Pass Output

A future valid actual-controlled invocation case should emit only public-safe summary metadata. Suggested fields:

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
- metadata_file_count=count-only value
- unsafe_signal_count=0

## 11. Actual Invocation Safety Scan Design

The future implementation should scan:

- input fixture metadata
- artifact body generation CLI stdout summary
- artifact body generation CLI stderr summary
- runtime summary fields
- output fields
- temporary directory and residue indicators

The scan must detect and suppress:

- request body values
- pointer body values
- expected body values
- artifact body payload values
- manifest body values
- generated policy body values
- raw stdout/stderr body values
- raw rows
- logits/probabilities
- private / absolute path values
- raw learner text
- real participant data
- performance metric body
- file writing
- manifest writer invocation
- unexpected residue

The scan may record only boolean or count-only metadata.

## 12. Failure Mapping

### pass

Use pass only when all of the following are true:

- valid actual-controlled invocation case
- artifact body generation CLI exits zero
- output is body-free
- no unsafe markers
- no manifest writer
- no file writing
- no residue
- expected status pass / reason none

### usage_error

Use usage_error for:

- missing fixture root
- missing fixture case
- missing required metadata file
- malformed JSON
- unsupported fixture schema
- unsupported runtime schema
- unsupported mode
- missing request/pointer metadata
- invalid mode / fixture mismatch
- unsupported actual invocation fixture layout

### fail_closed

Use fail_closed for:

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
- unexpected artifact body generation request
- artifact body CLI output not body-free
- artifact body CLI non-zero exit if unsafe or ambiguous

### mismatch

Use mismatch for:

- expected status mismatch
- expected reason mismatch
- expected field mismatch
- expected invocation flag mismatch
- expected count mismatch

## 13. Test Plan for Future Implementation

Future focused tests should include:

- actual-controlled primary valid case passes
- v0.4 schema emitted
- v0.3 planned-only behavior remains unchanged
- v0.2 safe-metadata-smoke behavior remains unchanged
- v0.1 plan-only bridge behavior remains unchanged
- integration mode is actual-controlled
- artifact_body_runtime_invoked=True
- artifact_body_runtime_invocation_planned=False
- artifact_body_runtime_mode=controlled_metadata_only_invocation
- artifact body generation CLI is invoked only in controlled metadata-only mode
- artifact body payload is not emitted
- safe metadata body field count is count-only
- stdout/stderr body is suppressed
- manifest_writer_invoked=False
- file_writing_enabled=False
- residue_file_count=0
- unsupported schema maps to usage_error
- missing fixture root maps to usage_error
- malformed JSON maps to usage_error
- request body marker maps to fail_closed
- artifact body payload marker maps to fail_closed
- manifest body marker maps to fail_closed
- generated policy body marker maps to fail_closed
- raw stdout/stderr body marker maps to fail_closed
- logits/probabilities marker maps to fail_closed
- private/absolute path marker maps to fail_closed
- raw learner text marker maps to fail_closed
- real data marker maps to fail_closed
- file writing requested maps to fail_closed
- manifest writer requested maps to fail_closed
- unsafe residue maps to fail_closed
- mismatched expected status maps to mismatch
- output suppression does not leak raw values
- no residue files are created
- runtime invocation fixture validator target still passes
- planned-only v0.3 runtime target still passes
- artifact body generation safe-metadata CLI smoke still passes

Mutation tests should use temporary copies.

## 14. Relationship to Existing Boundaries

Relationship to existing boundaries:

- relation to Step570 planned-only fixture root: keep it as the planned-only fixture root and do not mutate it for actual-controlled semantics without a separate contract
- relation to Step574 fixture validator target: keep it as the planned-only fixture validator target and do not treat it as actual-controlled validation
- relation to Step577/579 planned-only v0.3 runtime target: keep v0.3 planned-only behavior unchanged
- relation to Step581 release-quality integration: do not replace existing adjacent checks; future actual-controlled checks should be added only after separate design and implementation steps
- relation to Step583 remote status marker: treat it as public-safe planned-only evidence, not actual invocation evidence
- relation to artifact body generation safe-metadata CLI smoke: use it as an upstream compatibility check, but do not treat it as runtime invocation
- relation to artifact body fixture validation: keep it separate from runtime invocation validation
- relation to manifest writer runtime smoke: keep it separate and do not invoke manifest writer in actual-controlled runtime invocation
- relation to manifest writer file-writing smoke: keep it separate and do not write files in actual-controlled runtime invocation

Actual-controlled invocation design must not replace existing planned-only checks.

## 15. Future Staging

Recommended safe staging:

- Step586: actual-controlled runtime invocation fixture/schema contract design
- Step587: actual-controlled fixture root creation
- Step588: actual-controlled fixture validator design
- Step589: actual-controlled fixture validator implementation
- Step590: actual-controlled runtime implementation refinement design
- Step591: actual-controlled runtime implementation
- Step592: actual-controlled runtime Makefile target design
- Step593: actual-controlled runtime Makefile target implementation
- Step594: release-quality integration design
- Step595: release-quality wrapper integration
- Step596: remote/manual run record workflow design
- Step597: remote status marker
- Step598: final safety review

Do not perform any of these in Step585.

## 16. Recommended Next Step

Step586 fixture/schema contract design is recorded in
`docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_schema_contract_design.md`.

Step587 actual-controlled fixture root is recorded in
`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled/README.md`.

Step588 fixture validator design is recorded in
`docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validator_design.md`.

Recommended next step after Step588:

- Step589: actual-controlled fixture validator implementation

Do not proceed to direct runtime implementation as the next step.

## 17. Non-Equivalence Cautions

Non-equivalence cautions:

- actual controlled invocation design is not implementation
- planned-only v0.3 pass is not actual invocation
- actual-controlled future pass will not prove runtime correctness generally
- fixture validator pass is not runtime correctness generally
- artifact body generation safe-metadata CLI smoke is not equivalent to actual runtime invocation
- count-only metadata is not artifact body payload correctness
- safe metadata body field count is not free-form body safety proof
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


## Step589 Fixture Validator Implementation Reference

Step589 implements a standalone validator for the Step587 actual-controlled fixture root. This is still fixture validation only; it does not implement actual controlled runtime invocation, manifest writer integration, file writing, wrapper integration, or workflow integration. The next expected step is Step590 Makefile target design.


## Step590 Makefile Target Design Reference

Step590 designs a future standalone Makefile target for the actual-controlled fixture validator. This remains fixture validation only and does not implement actual controlled runtime invocation, manifest writer integration, file writing, wrapper integration, or workflow integration.


## Step591 Makefile Target Implementation Reference

Step591 implements the standalone Makefile target for the actual-controlled fixture validator. This remains fixture validation only and does not implement actual controlled runtime invocation, manifest writer integration, file writing, wrapper integration, or workflow integration.


## Step592 Implementation Refinement Design Reference

Step592 adds `docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_implementation_refinement_design.md` as the design-only refinement before future v0.4 direct runtime behavior. It keeps this chain out of Makefile, wrapper, workflow, fixture JSON, manifest writer, and file-writing changes in Step592.

## Step593 Runtime Implementation Reference

Step593 adds v0.4 direct runtime behavior for `artifact-body-runtime-invocation-controlled` with `--actual-invocation`, using public-safe summary-only output. It does not add release-quality wrapper integration, workflow changes, fixture JSON changes, manifest writer integration, or file writing.

## Step594 Makefile Target Design Reference

Step594 adds `docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_makefile_target_design.md` as a design-only plan for a future standalone target around the Step593 v0.4 runtime CLI. It does not change Makefile, release-quality wrapper, workflow files, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step595 Makefile Target Implementation Reference

Step595 adds the standalone Makefile target `check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation` for the Step593 v0.4 runtime CLI. It remains outside release-quality and does not change workflow files, Python code/tests, fixture JSON, runtime implementation, manifest writer integration, or file writing.

## Step596 Release-Quality Integration Design Reference

Step596 adds
`docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_release_quality_integration_design.md`
as the design-only plan for adding the Step591 fixture validator target and
Step595 v0.4 runtime smoke target to release-quality in a later step. It does
not change wrapper, Makefile, workflow files, Python code/tests, fixture JSON,
runtime implementation, manifest writer integration, or file writing.

## Step597 Release-Quality Integration Status

Step597 adds the Step591 actual-controlled fixture validator target and
Step595 v0.4 runtime smoke target to `scripts/check_release_quality.sh` in
adjacent order. It does not change Makefile, workflow files, Python
code/tests, fixture JSON, runtime implementation, manifest writer integration,
or file writing.

## Step598 Remote Run Record Workflow Reference

Step598 adds
`docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_release_quality_remote_run_record_workflow.md`
as a design-only workflow for a future public-safe status marker after
Step597. It does not create the marker or change wrapper, Makefile, workflow
files, Python code/tests, fixture JSON, runtime implementation, manifest
writer integration, or file writing.

## Step599 Remote Run Status Reference

Step599 adds
`docs/status/learner_state_frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_release_quality_remote_run_status.md`
as the public-safe status marker for the remote Release Quality run after
Step597 wrapper integration. It does not change wrapper, Makefile, workflow
files, Python code/tests, fixture JSON, runtime implementation, manifest
writer integration, or file writing.

## Step600 Final Safety Review Reference

Step600 adds
`docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_release_quality_chain_final_safety_review.md`
as a final-safety-review / docs-only review for the Step585-Step599
actual-controlled release-quality chain. This design remains unchanged, and
Step600 does not change wrapper, Makefile, workflow, Python code/tests,
fixture JSON, runtime implementation, manifest writer integration, or file
writing.

## Step601 Planning Reference

Step601 adds
`docs/frozen_policy_generation_actual_controlled_post_final_safety_review_next_boundary_planning.md`
as a planning-only / docs-only next-boundary plan after Step600. This design
remains unchanged.

## Step602 Design Reference

Step602 adds
`docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_design.md`
as a design-only / docs-only plan for a future all-valid multi-case runtime
smoke. This design remains unchanged.

## Step603 Fixture Matrix Contract Reference

Step603 adds
`docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_fixture_matrix_contract_design.md`
as a design-only / docs-only fixture/matrix contract for the future all-valid
multi-case runtime smoke. This design remains unchanged.

## Step604 Implementation Reference

Step604 adds the direct CLI-only all-valid multi-case runner and focused tests. This original actual-controlled design remains unchanged; Step604 does not add Makefile target integration, release-quality integration, manifest writer integration, file writing, or payload emission.
