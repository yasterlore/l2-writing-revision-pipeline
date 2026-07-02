# Frozen Policy Generation Artifact Body Generation Runtime Integration Safe-Metadata Runtime Makefile Target Design

## 1. Scope

This document is the Makefile target design for running the Step559
`safe-metadata-smoke` runtime CLI as a future standalone Makefile target.

This is design-only / planning-only. Step560 does not change Makefile,
release-quality wrapper, workflow files, Python code/tests, fixture JSON,
runtime implementation, validator implementation, artifact body generation
runtime invocation, manifest writer integration, or file writing. It is not
evidence of production readiness, real-data readiness, or model performance.

## 2. Prior Completed Chain Dependency

- The plan-only bridge chain is complete through remote marker and final
  safety review.
- The safe-metadata v0.2 planned fixture validator chain is complete through
  remote marker and final safety review.
- The safe-metadata runtime refinement design is complete.
- The safe-metadata runtime fixture/expected-output design is complete.
- The `safe-metadata-smoke` runtime implementation is complete.
- The runtime remains metadata handoff only.
- The runtime is not yet Makefile-connected.
- The runtime is not yet release-quality integrated.

## 3. Proposed Makefile Target

Future target:

- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-runtime`

Future help text:

- `Run artifact body generation runtime integration safe-metadata smoke`

Future command:

```sh
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_generation_runtime_integration \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration_planned_safe_metadata_v0_2 \
  --fixture-case valid/valid_safe_metadata_explicit_runtime_bridge \
  --mode safe-metadata-smoke \
  --summary-only \
  --no-file-writing \
  --no-manifest-writer \
  --fail-closed-on-unsafe-output
```

Do not implement this target in Step560.

## 4. Expected Public-Safe Output

The future standalone target is expected to emit the Step559 runtime summary
with implementation casing:

- `mode=artifact_body_generation_runtime_integration`
- `runtime_schema_version=learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.2`
- `status=pass`
- `reason_code=none`
- `exit_code_category=zero`
- `case_id=valid/valid_safe_metadata_explicit_runtime_bridge`
- `integration_mode=safe-metadata-smoke`
- `planned_root=True`
- `safe_metadata_v0_2_planned_checked=True`
- `artifact_body_runtime_invoked=False`
- `artifact_body_runtime_mode=not_invoked`
- `artifact_body_payload_available=False`
- `artifact_body_payload_emitted=False`
- `safe_metadata_body_available=True`
- `safe_metadata_body_field_count=count-only value`
- `content_suppressed=True`
- `body_suppressed=True`
- `summary_only=True`
- `request_body_detected=False`
- `pointer_body_detected=False`
- `expected_body_detected=False`
- `artifact_body_payload_detected=False`
- `manifest_body_detected=False`
- `generated_policy_body_detected=False`
- `raw_stdout_body_suppressed=True`
- `raw_stderr_body_suppressed=True`
- `raw_rows_detected=False`
- `logits_detected=False`
- `private_path_detected=False`
- `absolute_path_detected=False`
- `raw_learner_text_detected=False`
- `real_data_marker_detected=False`
- `performance_metric_body_detected=False`
- `file_writing_enabled=False`
- `file_writing_detected=False`
- `manifest_writer_invoked=False`
- `artifact_file_written=False`
- `manifest_file_written=False`
- `runtime_safety_scan_passed=True`
- `runtime_fail_closed=False`
- `production_readiness_claimed=False`
- `real_data_readiness_claimed=False`
- `performance_claims_present=False`
- `metadata_file_count=7`
- `unsafe_signal_count=0`

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

- The new target should be a standalone runtime smoke target.
- It should not replace the plan-only bridge target:
  `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration`.
- It should not replace the safe-metadata v0.2 fixture validator target:
  `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-fixtures`.
- It should not replace artifact body generation safe-metadata CLI smoke:
  `check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata`.
- It should not replace artifact body fixture validation:
  `check-learner-state-frozen-policy-generation-artifact-body-fixtures`.
- It should not invoke manifest writer.
- It should not write files.
- Release-quality integration should be a later separate step.

## 7. Proposed Implementation Checks for Next Step

If Step561 implements the target, verify:

- `make help` shows the new target and help text
- new target passes
- direct `safe-metadata-smoke` CLI still passes
- focused runtime tests still pass
- existing plan-only target still passes
- existing safe-metadata fixture validator target still passes
- existing artifact body generation safe-metadata CLI smoke still passes
- active root validator still passes
- planned safe-metadata validator CLI still passes
- full Python tests pass
- compileall passes
- fixture JSON diff remains none
- Makefile diff is limited to target and help entry
- wrapper/workflow diff remains none
- code/docs/output safety scan passes
- no artifact body generation runtime invocation
- no manifest writer invocation
- no file writing
- no residue

## 8. Future Staging

Suggested next chain:

- Step561: safe-metadata runtime Makefile target implementation
- Step562: safe-metadata runtime release-quality integration design
- Step563: safe-metadata runtime release-quality wrapper integration
- Step564: safe-metadata runtime remote/manual run record workflow design
- Step565: safe-metadata runtime remote status marker
- Step566: safe-metadata runtime final safety review

Do not perform these in Step560.

## 9. Failure Interpretation

Future target failure means the `safe-metadata-smoke` runtime CLI failed
inside the standalone Makefile target. Possible reasons include missing
planned fixture root, missing case, unsupported schema, unsafe marker,
expected status mismatch, output policy issue, or unexpected residue.

Failure does not prove artifact body generation correctness generally, does
not prove artifact body payload correctness, does not prove manifest writer
issue, does not prove model performance issue, and does not prove production
readiness issue. Failure must be interpreted through public-safe status and
reason codes only. Raw stdout/stderr and payloads must not be copied into docs
or reports.

## 10. Non-Equivalence Cautions

- standalone target pass is not runtime correctness generally
- `safe-metadata-smoke` remains metadata handoff only
- it does not prove artifact body generation correctness generally
- it does not prove safe-metadata free-form body safety
- count-only body metadata is not artifact body payload correctness
- it is not manifest writer readiness
- standalone Makefile target pass is not release-quality integration
- release-quality integration, when later added, is not production readiness
- synthetic-only pass is not real-data readiness

## 11. Non-Claims

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
- standalone Makefile target availability
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

## 13. Step560 Status

Step560 creates this Makefile target design only. It does not change Makefile,
release-quality wrapper, workflow files, Python code/tests, fixture JSON,
runtime implementation, validator implementation, artifact body generation
runtime invocation, manifest writer integration, file writing, real-data use,
metric use, or production readiness status.

## 14. Step561 Standalone Target Implementation Status

Step561 implements the standalone Makefile target designed here:

`check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-runtime`

The target runs the Step559 `safe-metadata-smoke` runtime CLI over
`valid/valid_safe_metadata_explicit_runtime_bridge` and remains metadata
handoff only. Step561 does not add release-quality wrapper integration, change
workflow files, change Python code/tests, change fixture JSON, change runtime
implementation, invoke artifact body generation runtime, invoke manifest
writer, or write files.
