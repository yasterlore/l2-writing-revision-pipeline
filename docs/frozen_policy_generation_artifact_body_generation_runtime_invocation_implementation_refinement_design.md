# Frozen Policy Generation Artifact Body Generation Runtime Invocation Implementation Refinement Design

## 1. Scope

This document refines the Step575 implementation design before any runtime
implementation work. It narrows the first implementation boundary for the
future `artifact-body-runtime-invocation` mode.

This is design-only / docs-only. It does not change runtime implementation,
Python code/tests, Makefile, release-quality wrapper, workflow, fixture JSON,
validator implementation, artifact body generation implementation, manifest
writer integration, manifest body generation, generated policy body
generation, artifact body file writing, or manifest file writing. It does not
implement actual artifact body generation runtime invocation.

This document is not evidence of production readiness, real-data readiness, or
model performance.

## 2. Prior Completed Chain Dependency

- Step569 fixture contract design is complete.
- Step570 fixture root creation is complete.
- Step571 fixture validator design is complete.
- Step572 fixture validator implementation is complete.
- Step573 Makefile target design is complete.
- Step574 standalone Makefile target implementation is complete.
- Step575 implementation design is complete.
- The fixture validator target is standalone Makefile-connected.
- The fixture validator target is not yet release-quality integrated.
- Runtime invocation implementation is not implemented.
- Actual artifact body generation runtime invocation is not implemented.

## 3. Refinement Question

Main question:

- Should Step577 implement actual controlled artifact body generation runtime
  invocation, or should it first implement a v0.3
  `artifact-body-runtime-invocation` mode as a planned-only / explicit
  invocation-boundary marker?

Secondary questions:

- Should implementation extend the existing runtime module or create a
  dedicated module?
- What exact primary case should Step577 support first?
- What output fields are mandatory in Step577?
- Which failure modes must Step577 implement immediately?
- Which behavior must remain out of scope?

## 4. Option Comparison

### Option A: Existing Module + Planned-Only v0.3 Boundary Marker

Benefits:

- Reuses the existing runtime integration CLI shape.
- Adds an explicit mode without invoking artifact body generation runtime.
- Keeps the first implementation metadata-only, body-free, count-only, and
  small.
- Preserves `plan-only-bridge` and `safe-metadata-smoke` as separate modes.

Risks:

- The name may suggest invocation unless output fields clearly mark
  `artifact_body_runtime_invoked=False`.
- v0.3 schema must clearly separate planned boundary markers from actual
  runtime invocation.

Implementation complexity: low to medium.

Safety: strongest first implementation option.

### Option B: Existing Module + Controlled Metadata-Only Runtime Invocation

Benefits:

- Moves directly toward the intended runtime invocation boundary.
- Exercises more runtime path than a planned-only marker.

Risks:

- Captured stdout/stderr and invocation residue create a larger output surface.
- Fail-closed scanning becomes more complex.
- It may blur fixture-contract validation with actual runtime behavior too
  early.

Implementation complexity: medium to high.

Safety: lower than Option A for the first implementation.

### Option C: Dedicated Runtime Invocation Module

Benefits:

- Stronger module separation.
- Reduces risk of affecting existing `plan-only-bridge` and
  `safe-metadata-smoke` behavior.

Risks:

- Adds a new module surface before the planned-only behavior is proven useful.
- Requires more docs/tests/CLI staging.

Implementation complexity: medium.

Safety: good separation, but more code surface than Option A.

### Option D: Additional Fixture/Schema Refinement Before Implementation

Benefits:

- Allows more schema review before runtime changes.
- Useful if Step570 fixture metadata is found insufficient.

Risks:

- Delays runtime boundary progress despite existing fixture root and validator.
- May add fixture churn without changing implementation risk.

Implementation complexity: low.

Safety: conservative, but likely not necessary before a planned-only marker.

## 5. Recommended Initial Implementation Boundary

Recommendation: Step577 should implement Option A first.

Step577 should:

- add explicit v0.3 `artifact-body-runtime-invocation` mode to the existing
  runtime module
- not call artifact body generation runtime
- emit planned-only invocation boundary markers
- use the Step570 fixture root
- support primary case `valid/valid_minimal_safe_metadata_runtime_invocation`
- preserve `plan-only-bridge` and `safe-metadata-smoke` behavior unchanged
- include fail-closed scanning based on fixture metadata
- include `usage_error` and `mismatch` mapping based on fixture metadata
- not invoke manifest writer
- not write files

This keeps the first runtime code change public-safe, metadata-only,
body-free, and count-only while making the future invocation boundary explicit.

## 6. Step577 Proposed CLI

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_generation_runtime_integration \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation \
  --fixture-case valid/valid_minimal_safe_metadata_runtime_invocation \
  --mode artifact-body-runtime-invocation \
  --summary-only \
  --no-file-writing \
  --no-manifest-writer \
  --fail-closed-on-unsafe-output
```

This CLI is not implemented in Step576.

## 7. Step577 Expected Pass Output

Expected fields for the primary case:

- `mode=artifact_body_generation_runtime_integration`
- `runtime_schema_version=learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.3`
- `status=pass`
- `reason_code=none`
- `exit_code_category=zero`
- `case_id=valid/valid_minimal_safe_metadata_runtime_invocation`
- `integration_mode=artifact-body-runtime-invocation`
- `artifact_body_runtime_invoked=False`
- `artifact_body_runtime_invocation_planned=True`
- `artifact_body_runtime_mode=planned_only_not_invoked`
- `artifact_body_payload_available=False`
- `artifact_body_payload_emitted=False`
- `safe_metadata_body_available=True`
- `safe_metadata_body_field_count=<count-only fixture value>`
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
- `probabilities_detected=False`
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

## 8. Step577 Failure Mapping

`pass`:

- primary valid case
- expected status `pass` / reason `none`
- no unsafe markers
- no raw bodies
- no manifest writer
- no file writing
- no no-oracle violation

`usage_error`:

- missing fixture root
- missing fixture case
- missing required metadata file
- malformed JSON
- unsupported fixture schema
- unsupported runtime schema
- unsupported mode
- invalid mode / fixture mismatch
- missing required metadata

`fail_closed`:

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
- file writing requested or detected
- manifest writer requested or invoked
- unsafe artifact body runtime mode
- no-oracle forbidden field
- unsafe output residue risk
- active root merge attempted unexpectedly

`mismatch`:

- expected status mismatch
- expected reason mismatch
- expected field mismatch

## 9. Step577 Minimal Test Scope

Required focused tests:

- primary valid case passes
- v0.3 schema emitted
- integration mode is `artifact-body-runtime-invocation`
- `artifact_body_runtime_invoked=False`
- `artifact_body_runtime_invocation_planned=True`
- `artifact_body_runtime_mode=planned_only_not_invoked`
- no artifact body payload emitted
- safe metadata body field count is count-only
- `manifest_writer_invoked` is false
- `file_writing_enabled` is false
- `unsafe_signal_count` is 0
- unsupported schema maps to `usage_error`
- missing fixture root maps to `usage_error`
- missing fixture case maps to `usage_error`
- request body marker maps to `fail_closed`
- artifact body payload marker maps to `fail_closed`
- manifest body marker maps to `fail_closed`
- generated policy body marker maps to `fail_closed`
- raw stdout/stderr body marker maps to `fail_closed`
- logits/probabilities marker maps to `fail_closed`
- private/absolute path marker maps to `fail_closed`
- raw learner text marker maps to `fail_closed`
- real data marker maps to `fail_closed`
- file writing requested maps to `fail_closed`
- manifest writer requested maps to `fail_closed`
- mismatched expected status maps to `mismatch`
- output suppression does not leak raw values
- no residue files are created
- existing `plan-only-bridge` behavior remains unchanged
- existing `safe-metadata-smoke` behavior remains unchanged
- runtime invocation fixture validator target still passes
- artifact body generation safe-metadata CLI smoke still passes

Mutation tests should use temporary copies.

## 10. Out Of Scope For Step577

Step577 should not:

- invoke actual artifact body generation runtime
- invoke manifest writer
- write files
- emit artifact body payload
- emit manifest body
- emit generated policy body
- implement Makefile target for the new runtime mode
- integrate release-quality wrapper
- modify workflow
- merge active / planned roots
- claim runtime correctness generally
- claim artifact body generation correctness generally
- claim production readiness, real-data readiness, or model performance

## 11. Relationship To Existing Boundaries

- `plan-only-bridge` remains a selected-case bridge smoke and is not replaced.
- `safe-metadata-smoke` remains metadata handoff only and is not replaced.
- The runtime invocation fixture validator target remains a static
  fixture-contract validator and is not runtime behavior.
- Artifact body generation safe-metadata CLI smoke remains a separate CLI
  boundary and is not equivalent to runtime invocation.
- Artifact body fixture validator remains separate.
- Manifest writer runtime smoke remains separate.
- Manifest writer file-writing smoke remains separate.
- Release-quality wrapper integration for the runtime invocation fixture
  validator target remains future work.

Step577 planned-only invocation mode should not replace existing checks.

## 12. Future Staging After Step577

Suggested chain:

- Step577: planned-only v0.3 runtime invocation mode implementation
- Step578: runtime invocation Makefile target design
- Step579: runtime invocation standalone Makefile target implementation
- Step580: release-quality integration design
- Step581: release-quality wrapper integration
- Step582: remote/manual run record workflow design
- Step583: remote status marker
- Step584: final safety review
- Later chain: actual controlled artifact body generation runtime invocation
  implementation design

Do not proceed to actual controlled invocation until after the planned-only
v0.3 boundary has its own safety review.

## 13. Recommended Next Step

Recommended next step: Step577 planned-only v0.3
`artifact-body-runtime-invocation` mode implementation.

Do not proceed directly to actual artifact body generation runtime invocation.

## 14. Non-Equivalence Cautions

- Refinement design is not runtime implementation.
- Planned-only v0.3 invocation mode is not actual artifact body generation
  runtime invocation.
- Future planned-only pass is not runtime correctness generally.
- Artifact body generation safe-metadata CLI smoke is not equivalent to
  runtime invocation.
- Count-only metadata is not artifact body payload correctness.
- Manifest writer runtime smoke is not production manifest readiness.
- File-writing smoke is not production readiness.
- Release-quality success is not production readiness.
- Synthetic-only pass is not real-data readiness.
- Refinement design is not production approval.

## 15. Non-Claims

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

## 16. Public-Safe Checklist

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

## 17. Step577 Implementation Status

Step577 implements the recommended planned-only v0.3 boundary in
`python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py`.
The mode name is `artifact-body-runtime-invocation`, the runtime schema is
`learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.3`,
and the primary selected fixture case remains
`valid/valid_minimal_safe_metadata_runtime_invocation`.

The implementation emits public-safe metadata-only / body-free summary output,
including `artifact_body_runtime_invocation_planned=True`,
`artifact_body_runtime_invoked=False`, `manifest_writer_invoked=False`, and
`file_writing_enabled=False`. It also adds focused tests for pass,
usage-error, fail-closed, mismatch, public-safe output, no residue, and
existing mode compatibility. Actual artifact body generation runtime
invocation remains future work.

## 18. Step578 Makefile Target Design Status

Step578 adds
`docs/frozen_policy_generation_artifact_body_generation_runtime_invocation_makefile_target_design.md`
as a design-only / docs-only future standalone target design for the Step577
direct CLI. It does not change Makefile, release-quality wrapper, workflow
files, Python code/tests, fixture JSON, runtime implementation, validator
implementation, actual artifact body generation runtime invocation, manifest
writer integration, or file writing.

## 19. Step579 Makefile Target Implementation Status

Step579 adds the standalone Makefile target
`check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation`
for the Step577 planned-only v0.3 direct CLI. The target remains public-safe,
metadata-only, body-free, and separate from release-quality wrapper
connection, workflow changes, actual artifact body generation runtime
invocation, manifest writer integration, and file writing.
