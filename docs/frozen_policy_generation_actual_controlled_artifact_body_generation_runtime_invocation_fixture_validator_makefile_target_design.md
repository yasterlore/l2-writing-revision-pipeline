# Actual-Controlled Artifact Body Generation Runtime Invocation Fixture Validator Makefile Target Design

## 1. Title

Actual-Controlled Artifact Body Generation Runtime Invocation Fixture Validator Makefile Target Design

## 2. Scope

This document is a Step590 design-only / docs-only plan for running the Step589 standalone validator through a future Makefile target in Step591.

Step590 does not change Makefile, release-quality wrapper files, workflow files, Python code/tests, fixture JSON, runtime implementation, artifact body generation implementation, manifest writer integration, or file-writing behavior. It does not perform actual artifact body generation runtime invocation, does not invoke manifest writer code, and does not write files.

This design is not evidence of production readiness, real-data readiness, or model performance. It only defines a proposed standalone Makefile target around the existing Step589 validator.

## 3. Prior Chain Dependency

The proposed target depends on the following chain:

- Step569-Step574: planned-only runtime invocation fixture, validator, and standalone Makefile target chain.
- Step575-Step579: planned-only v0.3 runtime mode and standalone Makefile target chain.
- Step580-Step583: release-quality integration and remote status marker chain for the planned-only v0.3 boundary.
- Step584: final safety review for the planned-only v0.3 release-quality chain.
- Step585: actual controlled invocation design.
- Step586: actual-controlled fixture/schema contract design.
- Step587: actual-controlled fixture root creation.
- Step588: actual-controlled fixture validator design.
- Step589: actual-controlled fixture validator implementation.

Step589 created the standalone validator module and focused tests for the Step587 fixture root. Actual-controlled runtime invocation is still not implemented.

## 4. Target Validator

Module:

- `python/learner_state/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validation.py`

Existing direct CLI:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validation \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled
```

Fixture root:

- `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled/`

## 5. Proposed Makefile Target

Recommended target name:

- `check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation-fixtures`

Recommended help text:

- `Run actual-controlled artifact body generation runtime invocation fixture validation`

Recommended command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled
```

Step590 does not add the target. Step591 should implement it.

## 6. Expected Target Output

The future Makefile target should produce the same public-safe aggregate as the Step589 direct CLI. Expected count-only fields include:

- mode=artifact_body_generation_runtime_invocation_actual_controlled_fixture_validation
- validation_schema_version=learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled_fixture_validation_v0.1
- fixture_root=tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled
- total_cases=36
- valid_cases=6
- invalid_cases=30
- total_json_files=252
- json_files_per_case=7
- matched_cases=36
- mismatched_cases=0
- input_error_cases=0
- pass_cases=6
- usage_error_cases=3
- fail_closed_cases=26
- mismatch_cases=1
- expected_missing_required_metadata_file_cases=1
- expected_malformed_metadata_json_cases=1
- physical_missing_required_file_cases=0
- physical_malformed_json_cases=0
- content_suppressed=true
- body_suppressed=true
- metadata_only_checked=true
- synthetic_only_checked=true
- no_oracle_checked=true
- no_request_body=true
- no_pointer_body=true
- no_expected_body=true
- no_artifact_body_payload=true
- no_manifest_body=true
- no_generated_policy_body=true
- no_raw_stdout_body=true
- no_raw_stderr_body=true
- no_raw_rows=true
- no_logits_dump=true
- no_probabilities_dump=true
- no_private_paths=true
- no_absolute_paths=true
- no_raw_learner_text=true
- no_real_participant_data=true
- no_performance_metric_body=true
- file_writing_checked=true
- manifest_writer_integration_checked=true
- actual_controlled_runtime_invocation_checked=true
- production_readiness_claimed=false
- real_data_readiness_claimed=false
- performance_claims_present=false
- root_errors=[]

The target output must remain metadata-only and count-only where applicable.

## 7. Makefile Placement

Recommended placement:

- near the existing planned-only runtime invocation fixture validator target `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation-fixtures`
- before any future actual-controlled runtime implementation target
- outside the release-quality wrapper for Step591

Step591 should add only a standalone Makefile target. Release-quality wrapper integration should be deferred to a later design step after the standalone target is implemented and validated. The target should be added to `.PHONY` and included in `make help`.

## 8. Relationship To Existing Targets

Existing targets that must remain unchanged:

- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation-fixtures`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-runtime`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata`

The proposed new target validates the actual-controlled fixture root only. It does not invoke actual runtime, does not replace the planned-only fixture validator target, does not replace the planned-only v0.3 runtime target, does not replace safe-metadata runtime smoke, does not replace artifact body safe-metadata CLI smoke, does not invoke manifest writer, does not write files, and is not release-quality integrated yet.

## 9. Step591 Implementation Plan

Step591 should:

- update `Makefile`
- add a `.PHONY` entry
- add a `make help` entry
- add the target command
- not modify Python code/tests
- not modify fixture JSON
- not modify release-quality wrapper files
- not modify workflows
- not implement runtime invocation
- not invoke manifest writer
- not write files
- run the new target
- run the direct CLI
- run focused tests
- run the existing planned-only validator target
- run the existing planned-only v0.3 runtime target
- run the existing safe-metadata runtime target
- run artifact body safe-metadata CLI smoke
- run `make check-python`
- run compileall
- confirm fixture JSON diff is unchanged
- update root README and full technical specification related docs because Step591 is a Makefile target implementation step

## 10. Safety Boundary

The proposed target must:

- run only the standalone fixture validator
- read only synthetic metadata-only fixtures
- output only count-only / public-safe metadata
- not print fixture JSON body
- not print request body
- not print pointer body
- not print expected body
- not print artifact body payload
- not print manifest body
- not print generated policy body
- not print raw stdout/stderr body
- not print raw rows
- not print logits/probabilities
- not print private/absolute path values
- not print raw learner text
- not use real participant data
- not invoke actual artifact body generation runtime
- not invoke manifest writer
- not enable file writing

## 11. Failure Interpretation

A target failure means the fixture root or validator contract is inconsistent. It does not by itself indicate runtime invocation failure.

A target pass means the actual-controlled fixture root is structurally and metadata-safety validated by the standalone validator. It does not prove actual-controlled runtime correctness generally, does not prove artifact body payload correctness, does not imply release-quality integration, and does not imply production readiness or real-data readiness.

## 12. Non-Equivalence Cautions

- Makefile target design is not Makefile implementation.
- A future target pass will not prove runtime correctness generally.
- A future target pass will not prove artifact body payload correctness.
- The actual-controlled fixture root is not actual runtime invocation.
- Planned-only v0.3 pass remains not actual invocation.
- Artifact body generation safe-metadata CLI smoke is not equivalent to actual-controlled runtime invocation.
- Count-only metadata is not free-form body safety proof.
- Manifest writer validators are separate.
- Release-quality success is not production readiness.
- Synthetic-only pass is not real-data readiness.

## 13. Non-Claims

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

## 14. Public-Safe Checklist

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

## 15. Recommended Next Step

Recommended next step:

- Step591: actual-controlled fixture validator Makefile target implementation

Do not proceed directly to runtime implementation.

Step591 implementation status: the standalone Makefile target
`check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation-fixtures`
is now available with help text
`Run actual-controlled artifact body generation runtime invocation fixture validation`.
It remains outside the release-quality wrapper and does not invoke actual
artifact body generation runtime, manifest writer, or file writing.

Step592 follow-up status: the implementation refinement design is available at
`docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_implementation_refinement_design.md`.
It narrows the future v0.4 runtime behavior step without changing Makefile,
wrapper, workflow, Python code/tests, fixture JSON, manifest writer, or file
writing.

Step593 follow-up status: v0.4 `artifact-body-runtime-invocation-controlled`
runtime CLI behavior is implemented in
`python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py`.
The Step591 fixture-validator target remains standalone and outside
release-quality; Step593 does not change Makefile, wrapper, workflow, fixture
JSON, manifest writer integration, or file writing.

Step594 follow-up status: the design-only Makefile target plan for the Step593
v0.4 runtime CLI is available at
`docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_makefile_target_design.md`.
It does not implement the target or change wrapper, workflow, Python code/tests,
fixture JSON, manifest writer integration, or file writing.

Step595 follow-up status: the standalone Makefile target
`check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation`
is now available for the Step593 v0.4 runtime CLI. It remains outside
release-quality and does not invoke manifest writer or write files.

Step596 follow-up status: the release-quality integration design for this
fixture validator target and the Step595 v0.4 runtime smoke target is
available at
`docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_release_quality_integration_design.md`.
It is design-only / docs-only and does not change wrapper, Makefile,
workflow, Python code/tests, fixture JSON, manifest writer integration, or
file writing.

Step597 follow-up status: this fixture validator target is now connected to
the release-quality wrapper before the Step595 v0.4 runtime smoke target. The
target and fixture JSON remain unchanged, and Step597 does not invoke manifest
writer or write files.

Step598 follow-up status: a design-only remote/manual run record workflow for
the Step597 wrapper checks is available at
`docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_release_quality_remote_run_record_workflow.md`.
It does not create a status marker or change fixture JSON.

Step599 follow-up status: the public-safe status marker for the Step597
wrapper checks is available at
`docs/status/learner_state_frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_release_quality_remote_run_status.md`.
It records count-only summaries and does not change fixture JSON.

Step600 follow-up status: the final-safety-review / docs-only review for the
Step585-Step599 actual-controlled release-quality chain is available at
`docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_release_quality_chain_final_safety_review.md`.
This Makefile target design remains unchanged.

Step601 follow-up status: the planning-only / docs-only next-boundary plan is
available at
`docs/frozen_policy_generation_actual_controlled_post_final_safety_review_next_boundary_planning.md`.
This fixture validator Makefile target design remains unchanged.

Step602 follow-up status: the design-only / docs-only multi-case runtime smoke
plan is available at
`docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_design.md`.
This fixture validator Makefile target design remains unchanged.

Step603 follow-up status: the design-only / docs-only fixture/matrix contract
for the future all-valid multi-case runtime smoke is available at
`docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_fixture_matrix_contract_design.md`.
This fixture validator Makefile target design remains unchanged.
