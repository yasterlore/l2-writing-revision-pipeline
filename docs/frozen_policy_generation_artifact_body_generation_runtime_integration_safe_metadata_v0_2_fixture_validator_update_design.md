# Frozen Policy Generation Artifact Body Generation Runtime Integration Safe-Metadata v0.2 Fixture Validator Update Design

## 1. Scope

This document is a design-only / planning-only validator update design for
public-safe validation of the Step547 planned safe-metadata v0.2 fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration_planned_safe_metadata_v0_2/`

Step548 does not implement a validator, change runtime implementation, change
Python code/tests, change Makefile, change the release-quality wrapper, change
workflow files, change fixture JSON, invoke artifact body generation runtime,
implement manifest writer integration, or write files.

This document is not evidence of production readiness, real-data readiness, or
model performance.

## 2. Prior Completed Chain Dependency

The plan-only bridge chain is complete through remote marker and final safety
review. The broader final safety review through the manifest writer boundary
is complete. Safe-metadata explicit stage planning, safe-metadata fixture/update
design, and safe-metadata fixture root/update design are complete.

Step547 added the planned v0.2 fixture root without changing the active root.
The existing active validator and release-quality wrapper still pass against
the active root.

## 3. Current Fixture Topology

Active root:

- path: `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration/`
- total cases: 28
- total JSON files: 196
- existing validator target: active root only
- release-quality integrated: yes

Planned root:

- path: `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration_planned_safe_metadata_v0_2/`
- planned cases: 24
- planned JSON files: 168
- per-case layout: 7 files
- validator-integrated: no
- release-quality integrated: no

## 4. Validator Integration Options

Option A extends the existing active validator with an optional planned-root
argument. It preserves the current active root by default, but increases the
chance that active and planned validation concerns become coupled.

Option B creates a separate validator module for the planned safe-metadata v0.2
root. This keeps active validation stable, makes aggregate counts clear, and
keeps future Makefile and release-quality staging explicit.

Option C merges the planned root into the active root before validator update.
This has the highest release-quality stability risk because the active validator
currently enforces fixed active counts and root layout.

Option D keeps the planned root unvalidated and proceeds to runtime refinement.
This avoids immediate implementation risk but leaves the safe-metadata contract
unchecked before runtime work.

Recommended option: Option B. A separate validator module is the safest next
step because it does not replace or disturb the active validator and gives the
planned v0.2 root its own public-safe aggregate summary.

## 5. Proposed Validator Module / CLI

Future module:

- `python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation.py`

Future tests:

- `python/learner_state/tests/test_frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation.py`

Future CLI:

```text
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration_planned_safe_metadata_v0_2
```

Do not implement this CLI in Step548.

## 6. Proposed Validation Schema

Recommended schema:

- `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation_v0.1`

This is preferable to extending the existing active validator schema because
the planned root is separate, has distinct v0.2 runtime expectations, and is
not part of the active root validator. Step553 later adds release-quality
wrapper integration for the separate planned-root validator target.

## 7. Expected Aggregate Summary

The future planned root validator should emit a public-safe aggregate summary:

- mode: `safe_metadata_fixture_validation`
- validation schema version: `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation_v0.1`
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

The unsupported schema case should map to `usage_error`. The mismatched
expected status case should map to `mismatch` because it is intended to check
expected-result agreement rather than a body/payload safety marker. The
remaining unsafe marker cases should map to `fail_closed`.

## 8. Required Validation Checks

The future validator should check:

- root exists
- expected directory layout
- each case has exactly 7 required metadata files
- JSON parseability
- case id / directory consistency
- case kind is valid or invalid
- schema version is recognized
- safe-metadata v0.2 planned marker is present
- runtime mode is expected to be `safe-metadata-smoke`
- expected runtime schema is `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.2`
- valid cases expect pass / reason `none`
- invalid cases expect `usage_error`, `fail_closed`, or `mismatch`
- all cases remain metadata-only
- no request body
- no pointer body
- no expected body
- no artifact body payload
- no manifest body
- no generated policy body
- no raw stdout/stderr body
- no raw rows
- no logits / probabilities
- no private / absolute path values
- no raw learner text
- no real participant data
- no performance metric body
- no file writing
- no manifest writer invocation
- no production/readiness/performance claims
- unsafe marker cases map to expected reason codes
- valid cases have unsafe signal count 0
- invalid cases have unsafe signal count greater than 0 where applicable
- output is public-safe and does not echo unsafe values

## 9. Reason Code Mapping

Candidate reason codes:

- `none`
- `unsupported_schema`
- `mismatched_expected_status`
- `artifact_body_payload_present`
- `manifest_body_present`
- `generated_policy_body_present`
- `request_body_present`
- `pointer_body_present`
- `expected_body_present`
- `raw_stdout_body_present`
- `raw_stderr_body_present`
- `raw_rows_present`
- `logits_present`
- `private_path_present`
- `absolute_path_present`
- `raw_learner_text_present`
- `real_data_marker_present`
- `performance_metric_body_present`
- `file_writing_requested`
- `manifest_writer_requested`
- `unsafe_output_surface`

Status mapping:

- `none`: pass
- `unsupported_schema`: usage_error
- `mismatched_expected_status`: mismatch
- all unsafe marker reason codes: fail_closed

## 10. Public-Safe Output Policy

Validator output may include:

- mode
- validation schema version
- fixture root label
- planned root flag
- aggregate counts
- reason code counts
- safety flags
- production readiness claimed false
- real-data readiness claimed false
- performance claims present false
- root errors count or empty marker

Validator output must not include fixture JSON bodies, request bodies, pointer
bodies, expected bodies, artifact body payloads, manifest bodies, generated
policy bodies, raw stdout/stderr bodies, raw rows, logits / probabilities,
private / absolute path values, raw learner text, real participant data, or
performance metric bodies.

## 11. Focused Test Plan

Future focused tests should cover:

- planned root aggregate pass
- every case has 7 files
- valid cases map to pass
- unsupported schema maps to usage_error
- mismatched expected status maps to mismatch
- each unsafe marker case maps to fail_closed
- missing required file maps to usage_error
- extra unexpected file maps to usage_error
- invalid JSON maps to usage_error
- output suppresses unsafe values
- reason code counts are deterministic
- traversal order is deterministic
- active root remains unaffected
- existing active validator still passes
- no file writing / no residue

Extra unexpected files should map to usage_error because they indicate fixture
layout misuse rather than an artifact body safety result.

## 12. Makefile / Release-Quality Staging

Suggested future chain:

- Step549: safe-metadata v0.2 fixture validator implementation
- Step550: safe-metadata v0.2 fixture validator Makefile target design
- Step551: safe-metadata v0.2 fixture validator Makefile target implementation
- Step552: safe-metadata v0.2 fixture validator release-quality integration design
- Step553: safe-metadata v0.2 fixture validator release-quality wrapper integration
- Step554: safe-metadata v0.2 fixture validator remote/manual run record workflow design
- Step555: safe-metadata v0.2 fixture validator remote status marker
- later: runtime refinement design

## 13. Relationship to Active Root Validator

The existing active root validator remains unchanged in Step548. It currently
validates 28 cases / 196 JSON files and remains release-quality integrated.

The planned v0.2 validator should not replace the active root validator and
should not break release-quality. Any eventual merger into the active root
should require a separate design. Planned root validation is not runtime
correctness generally.

## 14. Relationship to Runtime Implementation

Safe-metadata runtime implementation is not done. The runtime mode remains
reserved. The planned fixture validator only validates a metadata contract.
Runtime schema v0.2 remains future. No artifact body generation runtime
invocation occurs. No manifest writer invocation occurs. No file writing
occurs.

## 15. Relationship to Existing Safe-Metadata CLI Smoke

The existing artifact body generation safe-metadata CLI smoke remains separate.
The planned v0.2 fixture validator is for the runtime integration
safe-metadata handoff contract. Existing CLI smoke should not be treated as
runtime integration proof, and neither check proves free-form body safety
generally.

## 16. Failure Interpretation

Future validator failure should be interpreted within the planned
safe-metadata v0.2 fixture validation boundary. It may indicate missing
metadata, schema mismatch, unsafe marker mismatch, count mismatch, invalid
JSON, or output policy issue.

Failure does not prove artifact body generation correctness generally,
manifest writer failure, runtime correctness generally, or production
readiness issue. Raw stdout/stderr and payloads must not be copied into docs
or reports. Public-safe reason codes only.

## 17. Non-Equivalence Cautions

- planned fixture validation is not runtime correctness
- validator pass is not artifact body generation correctness generally
- validator pass is not safe-metadata free-form body safety
- count-only body metadata is not payload correctness
- planned root validation is not manifest writer readiness
- release-quality inclusion is not production readiness
- synthetic-only pass is not real-data readiness

## 18. Recommended Next Step

Recommended next step: Step549 safe-metadata v0.2 fixture validator
implementation.

This is safer than runtime refinement because it validates the planned
metadata-only fixture contract before any runtime mode implementation.

## 19. Non-Claims

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

## 20. Public-Safe Checklist

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

## 21. Step549 Validator Implementation Status

Step549 implements the separate planned-root validator module:

`python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation.py`

It also adds focused tests:

`python/learner_state/tests/test_frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation.py`

The CLI validates the planned root as 24 cases / 168 JSON files with output
mode `safe_metadata_fixture_validation` and schema
`learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation_v0.1`.

Makefile target, release-quality wrapper integration, workflow update, runtime
implementation, artifact body generation runtime invocation, manifest writer
integration, and file writing remain future work.

## 22. Step550 Makefile Target Design Status

Step550 adds
`docs/frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_v0_2_fixture_validator_makefile_target_design.md`
as a design-only / planning-only standalone Makefile target design for the
Step549 validator CLI. It does not implement a Makefile target or connect the
validator to release-quality.

## 23. Step551 Makefile Target Implementation Status

Step551 implements the standalone Makefile target
`check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-fixtures`
for the Step549 validator CLI. The target preserves the 24-case / 168-JSON
public-safe aggregate boundary. Step553 later adds release-quality wrapper
integration for this target.

## 24. Step552 Release-Quality Integration Design Status

Step552 adds a design-only / planning-only release-quality integration design
for the Step551 standalone target. It does not change the wrapper, workflow,
Makefile, Python code/tests, fixture JSON, validator implementation, runtime
implementation, artifact body generation runtime invocation, manifest writer
integration, or file writing.

## 25. Step553 Release-Quality Wrapper Integration Status

Step553 adds the Step551 standalone target to the release-quality wrapper
after plan-only bridge smoke and before artifact body fixture validation. It
does not change workflow, Makefile, Python code/tests, fixture JSON, validator
implementation, runtime implementation, artifact body generation runtime
invocation, manifest writer integration, or file writing.

## 26. Step554 Remote Run Record Workflow Design Status

Step554 adds the docs-only public-safe remote/manual run record workflow design
for the Step553 wrapper check:

`docs/frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_v0_2_fixture_validator_release_quality_remote_run_record_workflow.md`

It proposes future metadata-only/body-free status marker fields and does not
create a marker, change workflow, wrapper, Makefile, Python code/tests,
fixture JSON, validator/runtime implementation, artifact body generation
runtime invocation, manifest writer integration, or file writing.
