# Frozen Policy Generation Artifact Body Generation Runtime Invocation Implementation Design

## 1. Scope

This document is the implementation design for a future
`artifact-body-runtime-invocation` runtime boundary.

This is design-only / docs-only. It does not change runtime implementation,
Python code/tests, Makefile, release-quality wrapper, workflow, fixture JSON,
validator implementation, artifact body generation implementation, manifest
writer integration, manifest body generation, generated policy body
generation, artifact body file writing, or manifest file writing. It does not
perform actual artifact body generation runtime invocation.

This document is not evidence of production readiness, real-data readiness, or
model performance.

## 2. Prior Completed Chain Dependency

- Step569 fixture contract design is complete.
- Step570 fixture root creation is complete.
- Step571 validator design is complete.
- Step572 validator implementation is complete.
- Step573 Makefile target design is complete.
- Step574 standalone Makefile target implementation is complete.
- The runtime invocation fixture validator target is standalone
  Makefile-connected.
- Step581 connects the runtime invocation fixture validator target and
  planned-only v0.3 runtime smoke target to the release-quality wrapper in
  adjacent order.
- Runtime invocation implementation is not implemented.
- The artifact body safe-metadata CLI smoke remains separate.
- Manifest writer and file-writing boundaries remain separate.

## 3. Design Decision: Implementation Surface

Option A extends the existing runtime integration module
`python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py`,
adds mode `artifact-body-runtime-invocation`, and emits runtime schema
`learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.3`.

Option B creates a new module dedicated to runtime invocation and keeps the
existing runtime integration module unchanged.

Option C extends `safe-metadata-smoke` with an invocation flag.

Recommendation: prefer Option A if the implementation preserves explicit mode
separation and schema v0.3. Prefer Option B if Option A would blur the
metadata handoff boundary. Do not use Option C for the first invocation
boundary because it may blur `safe-metadata-smoke` metadata handoff behavior
with controlled invocation behavior.

## 4. Proposed Runtime Mode And Schema

- proposed integration mode: `artifact-body-runtime-invocation`
- proposed runtime schema:
  `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.3`
- fixture root:
  `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation`
- primary candidate case: `valid/valid_minimal_safe_metadata_runtime_invocation`
- validator schema prerequisite:
  `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation_v0.1`

## 5. Proposed CLI

Preferred CLI if extending the existing runtime integration module:

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

Secondary CLI if a dedicated module is needed:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_generation_runtime_invocation \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation \
  --fixture-case valid/valid_minimal_safe_metadata_runtime_invocation \
  --summary-only \
  --no-file-writing \
  --no-manifest-writer \
  --fail-closed-on-unsafe-output
```

Neither CLI is implemented in Step575.

## 6. Implementation Boundary

The future implementation should:

- read fixture metadata only
- use the runtime invocation fixture root
- use one valid primary case first
- perform controlled runtime invocation only after fixture validation is in place
- suppress artifact body payload in public output
- emit safe metadata body availability as a boolean
- emit safe metadata body field count as count-only
- suppress raw stdout/stderr body
- not invoke manifest writer
- not write files
- fail closed on unsafe markers
- return `usage_error` on missing, malformed, or unsupported metadata
- return `mismatch` on expected status / reason mismatch
- avoid production readiness, real-data readiness, and model performance claims

The future implementation should not:

- emit artifact body payload body
- emit manifest body
- emit generated policy body
- print request, pointer, or expected body
- invoke manifest writer
- write artifact files
- write manifest files
- use real participant data
- use raw learner text
- use `final_text`, `observed_after_text`, or gold labels
- perform test-set tuning
- emit performance metrics

## 7. Expected Future Runtime Behavior

For the primary case:

- mode: `artifact_body_generation_runtime_integration`
- runtime schema version:
  `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.3`
- status: `pass`
- reason code: `none`
- exit code category: `zero`
- case id: `valid/valid_minimal_safe_metadata_runtime_invocation`
- integration mode: `artifact-body-runtime-invocation`
- artifact body runtime invoked: initially recommended as `false`
- artifact body runtime invocation planned: `true`
- artifact body runtime mode: `planned_controlled_metadata_only_invocation`
- artifact body payload available: `false`
- artifact body payload emitted: `false`
- safe metadata body available: fixture-defined boolean
- safe metadata body field count: count-only
- manifest writer invoked: `false`
- file writing enabled: `false`
- file writing detected: `false`
- artifact file written: `false`
- manifest file written: `false`
- runtime safety scan passed: `true`
- unsafe signal count: `0`

Recommendation: first implement this boundary as explicit planned invocation
with `artifact_body_runtime_invoked=false` and
`artifact_body_runtime_invocation_planned=true`, then add a later controlled
actual invocation step if the public-safe output surface and fail-closed scans
remain clear. This keeps the first runtime change small and avoids mixing
fixture-boundary validation with actual runtime invocation behavior too early.

## 8. Expected Public-Safe Output Fields

The future output surface may include:

- `mode`
- `runtime_schema_version`
- `status`
- `reason_code`
- `exit_code_category`
- `case_id`
- `integration_mode`
- `artifact_body_runtime_invoked`
- `artifact_body_runtime_invocation_planned`
- `artifact_body_runtime_mode`
- `artifact_body_payload_available`
- `artifact_body_payload_emitted`
- `safe_metadata_body_available`
- `safe_metadata_body_field_count`
- `content_suppressed`
- `body_suppressed`
- `summary_only`
- `request_body_detected`
- `pointer_body_detected`
- `expected_body_detected`
- `artifact_body_payload_detected`
- `manifest_body_detected`
- `generated_policy_body_detected`
- `raw_stdout_body_suppressed`
- `raw_stderr_body_suppressed`
- `raw_rows_detected`
- `logits_detected`
- `probabilities_detected`
- `private_path_detected`
- `absolute_path_detected`
- `raw_learner_text_detected`
- `real_data_marker_detected`
- `performance_metric_body_detected`
- `file_writing_enabled`
- `file_writing_detected`
- `manifest_writer_invoked`
- `artifact_file_written`
- `manifest_file_written`
- `runtime_safety_scan_passed`
- `runtime_fail_closed`
- `production_readiness_claimed`
- `real_data_readiness_claimed`
- `performance_claims_present`
- `metadata_file_count`
- `unsafe_signal_count`

The output must not include artifact body payload body.

## 9. Failure Mapping

`pass`:

- valid primary case
- metadata-only and body-free
- no unsafe markers
- no manifest writer
- no file writing
- no no-oracle violation
- expected status `pass` / reason `none`

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

## 10. Safety Scan Design

The future implementation should scan:

- input fixture metadata
- runtime summary fields
- captured artifact body generation runtime stdout/stderr, if any
- output fields
- residue / generated file indicators

The scan should detect only public-safe markers and must suppress raw values.

The scan should verify:

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

## 11. Test Plan For Future Implementation

Future focused tests should cover:

- primary valid case passes
- v0.3 schema emitted
- integration mode is `artifact-body-runtime-invocation`
- artifact body payload is not emitted
- safe metadata body field count is count-only
- manifest writer invoked is false
- file writing enabled is false
- unsafe signal count is 0 for valid case
- unsupported schema maps to `usage_error`
- missing fixture root maps to `usage_error`
- missing fixture case maps to `usage_error`
- malformed JSON maps to `usage_error`
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
- existing runtime invocation fixture validator target still passes
- existing artifact body generation safe-metadata CLI smoke still passes

Mutation tests should use temporary fixture copies.

## 12. Relationship To Existing Boundaries

- `plan-only-bridge`: remains an earlier selected-case handoff smoke and is
  not replaced.
- `safe-metadata-smoke`: remains metadata handoff only and is not converted
  into invocation behavior.
- runtime invocation fixture validator: remains a static fixture-contract
  validator and is a prerequisite for any runtime implementation.
- artifact body generation safe-metadata CLI smoke: remains a separate CLI
  boundary and is not equivalent to runtime invocation.
- artifact body fixture validator: remains separate and later in the broader
  validation chain.
- manifest writer runtime smoke: remains separate and must not be inferred
  from runtime invocation work.
- manifest writer file-writing smoke: remains separate and out of scope.
- release-quality wrapper: Step581 adds the runtime invocation fixture
  validator target immediately before the planned-only v0.3 runtime smoke.

This future implementation does not replace any existing boundary.

## 13. Future Staging

Suggested chain:

- Step576: runtime invocation implementation
- Step577: runtime invocation Makefile target design
- Step578: runtime invocation standalone Makefile target implementation
- Step579: release-quality integration design
- Step580: release-quality wrapper integration
- Step581: remote/manual run record workflow design
- Step582: remote status marker
- Step583: final safety review

Safer chain:

- Step576: runtime invocation implementation refinement design
- Step577: runtime invocation implementation
- then Makefile / release-quality chain

Recommendation: use the safer chain because actual invocation behavior remains
ambiguous and should be narrowed in one more design step before runtime code
changes.

## 14. Recommended Next Step

Recommended next step: Step576 runtime invocation implementation refinement
design.

Do not proceed directly to manifest writer integration or file writing. If the
next design determines that the first implementation can remain planned-only
with explicit invocation boundary markers, implementation can follow as a
small metadata-only / body-free runtime change.

## 15. Non-Equivalence Cautions

- Implementation design is not runtime implementation.
- Future runtime invocation pass is not runtime correctness generally.
- Artifact body generation safe-metadata CLI smoke is not equivalent to
  runtime invocation.
- Count-only metadata is not artifact body payload correctness.
- Manifest writer runtime smoke is not production manifest readiness.
- File-writing smoke is not production readiness.
- Release-quality success is not production readiness.
- Synthetic-only pass is not real-data readiness.
- Implementation design is not production approval.

## 16. Non-Claims

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

## 17. Public-Safe Checklist

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

## 18. Step576 Refinement Status

Step576 adds
`docs/frozen_policy_generation_artifact_body_generation_runtime_invocation_implementation_refinement_design.md`
as a design-only / docs-only narrowing step before runtime implementation. It
recommends Step577 implement planned-only v0.3
`artifact-body-runtime-invocation` mode markers first, without actual artifact
body generation runtime invocation, manifest writer integration, or file
writing.

## 19. Step577 Planned-Only Runtime Mode Status

Step577 implements the planned-only v0.3 `artifact-body-runtime-invocation`
mode in the existing runtime integration module. It uses the Step570 fixture
root and selected case `valid/valid_minimal_safe_metadata_runtime_invocation`
to emit public-safe metadata-only / body-free summary output with runtime
invocation planned but not invoked.

The implementation keeps actual artifact body generation runtime invocation,
manifest writer integration, file writing, Makefile changes, release-quality
wrapper changes, workflow changes, fixture JSON changes, validator changes,
real-data use, metric use, production readiness, real-data readiness, and
model performance claims out of scope.

## 20. Step578 Makefile Target Design Status

Step578 adds
`docs/frozen_policy_generation_artifact_body_generation_runtime_invocation_makefile_target_design.md`
as a design-only / docs-only future target design for the planned-only v0.3
direct CLI. Makefile target implementation and release-quality wrapper staging
remain later work.

## 21. Step579 Makefile Target Implementation Status

Step579 adds
`check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation`
as a standalone Makefile target for the planned-only v0.3 direct CLI. The
target does not perform actual artifact body generation runtime invocation,
invoke manifest writer, or write files.

## 22. Step581 Release-Quality Wrapper Integration Status

Step581 adds the runtime invocation fixture validator target and the
planned-only v0.3 runtime smoke target to `scripts/check_release_quality.sh`
in adjacent order. The fixture validator runs first, after safe-metadata
runtime smoke and before the planned-only v0.3 runtime smoke. Actual artifact
body generation runtime invocation, manifest writer integration, and file
writing remain out of scope.


## Step590 Later-Chain Note

Step590 is a later actual-controlled fixture validator Makefile target design. It does not implement actual runtime invocation or change the planned-only runtime invocation implementation design recorded here.

## Step596 Later-Chain Note

Step596 adds a separate design-only release-quality integration plan for
future wrapper integration of the actual-controlled fixture validator and
v0.4 runtime smoke targets. It remains separate from this planned-only v0.3
implementation design.

## Step598 Later-Chain Note

Step598 adds a separate design-only remote/manual run record workflow for a
future actual-controlled status marker. It remains separate from this
planned-only v0.3 implementation design.
