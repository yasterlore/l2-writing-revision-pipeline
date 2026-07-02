# Frozen Policy Generation Artifact Body Generation Runtime Integration Safe-Metadata v0.2 Fixture Validator Makefile Target Design

## 1. Scope

This document is a design-only / planning-only Makefile target design for
running the Step549 safe-metadata v0.2 planned fixture root validator CLI as a
future standalone Makefile target.

Step550 does not change Makefile, change the release-quality wrapper, change
workflow files, change Python code/tests, change fixture JSON, change validator
implementation, change runtime implementation, invoke artifact body generation
runtime, implement manifest writer integration, or write files.

This document is not evidence of production readiness, real-data readiness, or
model performance.

## 2. Prior Completed Chain Dependency

The plan-only bridge chain is complete through remote marker and final safety
review. The safe-metadata planned fixture root exists. The safe-metadata v0.2
fixture validator update design is complete, and the separate validator
implementation is complete.

The Step549 validator CLI exists, but it is not yet Makefile-connected and is
not yet release-quality integrated. Runtime implementation remains unchanged.

## 3. Proposed Makefile Target

Future target:

- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-fixtures`

Future help text:

- `Run artifact body generation runtime integration safe-metadata v0.2 fixture validation`

Future command:

```text
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration_planned_safe_metadata_v0_2
```

Do not implement this target in Step550.

Step551 later implements this proposed standalone target with the same name,
help text, and command. Release-quality wrapper integration remains a later
separate step.

Step552 later adds
`docs/frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_v0_2_fixture_validator_release_quality_integration_design.md`
as the design-only / planning-only release-quality integration design for this
standalone target.

## 4. Expected Public-Safe Output

The future standalone target should expose the validator's public-safe
aggregate output, including:

- mode: `safe_metadata_fixture_validation`
- validation_schema_version: `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation_v0.1`
- planned_root: true
- total_cases: 24
- valid_cases: 4
- invalid_cases: 20
- total_json_files: 168
- json_files_per_case: 7
- matched_cases: 24
- mismatched_cases: 0
- input_error_cases: 0
- pass_cases: 4
- usage_error_cases: 1
- fail_closed_cases: 18
- mismatch_cases: 1
- reason_code_counts
- content_suppressed: true
- body_suppressed: true
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
- no_private_paths: true
- no_absolute_paths: true
- no_raw_learner_text: true
- synthetic_only_checked: true
- no_oracle_checked: true
- file_writing_checked: true
- manifest_writer_integration_checked: true
- production_readiness_claimed: false
- real_data_readiness_claimed: false
- performance_claims_present: false

When implemented, use the actual boolean casing emitted by the validator.

## 5. Safety Boundary

The proposed Makefile target must not:

- print raw stdout/stderr body
- print fixture JSON body
- print request / pointer / expected body
- print artifact body payload
- print manifest body
- print generated policy body
- print raw rows
- print logits / probabilities
- print private / absolute path values
- print raw learner text
- use real participant data
- write artifact files
- write manifest files
- invoke artifact body generation runtime
- invoke manifest writer
- claim production readiness
- claim real-data readiness
- claim model performance

## 6. Relationship to Existing Targets

This is a new standalone planned-root validator target. It does not replace the
active root artifact body generation integration fixture validation target.

The active root target remains:

- `check-learner-state-frozen-policy-generation-artifact-body-generation-integration-fixtures`

The active root remains 28 cases / 196 JSON. The planned safe-metadata root
remains separate. The runtime plan-only bridge target remains separate. The
existing artifact body generation safe-metadata CLI smoke remains separate.
Release-quality integration should be a later separate step.

## 7. Proposed Implementation Checks for Next Step

If Step551 implements the Makefile target, it should verify:

- `make help` shows the new target and help text
- new target passes
- direct planned-root validator CLI still passes
- focused validator tests still pass
- active root validator still passes
- active root Makefile target still passes
- full Python tests pass
- compileall passes
- fixture JSON diff remains none
- Makefile diff is limited to target + help entry
- wrapper/workflow diff remains none
- code/docs/output safety scan passes
- no artifact body generation runtime invocation
- no manifest writer invocation
- no file writing
- no residue

## 8. Future Staging

Suggested next chain:

- Step551: safe-metadata v0.2 fixture validator Makefile target implementation
- Step552: safe-metadata v0.2 fixture validator release-quality integration design
- Step553: safe-metadata v0.2 fixture validator release-quality wrapper integration
- Step554: safe-metadata v0.2 fixture validator remote/manual run record workflow design
- Step555: safe-metadata v0.2 fixture validator remote status marker
- Step556: safe-metadata runtime refinement design

Do not perform these in Step550.

## 9. Failure Interpretation

Future Makefile target failure means the planned-root safe-metadata v0.2
fixture validator failed. Possible reasons include missing fixture root,
missing metadata file, invalid JSON, schema mismatch, unsafe marker mismatch,
reason-code mismatch, or aggregate mismatch.

Failure does not prove artifact body generation correctness generally, runtime
correctness generally, manifest writer issue, model performance issue, or
production readiness issue. Failure must be interpreted through public-safe
reason codes only. Raw stdout/stderr and payloads must not be copied into docs
or reports.

## 10. Non-Equivalence Cautions

- planned-root fixture validator target is not runtime correctness
- validator pass is not artifact body generation correctness generally
- validator pass is not safe-metadata free-form body safety
- count-only body metadata is not artifact body payload correctness
- planned-root validation is not manifest writer readiness
- standalone Makefile target pass is not release-quality integration
- later release-quality integration is not production readiness
- synthetic-only pass is not real-data readiness

## 11. Non-Claims

This document does not claim:

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
- Makefile target implemented
- release-quality integrated

## 12. Public-Safe Checklist

- no raw logs
- no full job output
- no copied GitHub log blocks
- no screenshots containing raw logs
- no fixture JSON body
- no request body
- no pointer body
- no expected body
- no written file JSON body
- no manifest body
- no artifact body payload
- no generated policy body
- no raw stdout/stderr body
- no raw rows
- no logits/probabilities
- no private paths
- no absolute paths
- no raw learner text
- no real participant data
- no performance claims
- no production readiness claims
- no real-data readiness claims
