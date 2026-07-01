# Frozen Policy Generation Artifact Body Generation Runtime Integration Refinement Design

## 1. Title

Frozen Policy Generation Artifact Body Generation Runtime Integration
Refinement Design

## 2. Scope

This document is a design-only / planning-only runtime integration refinement
design. It makes the Step532 planning concrete for a future implementation
step.

This step does not:

- change runtime implementation
- implement artifact body generation integration
- change fixture JSON
- change validators
- change Python code/tests
- change the Makefile
- change the release-quality wrapper
- change workflow files
- implement manifest writer integration
- enable file writing
- prove production readiness, real-data readiness, or model performance

The design keeps the future runtime boundary synthetic-only, metadata-only,
no-oracle, body-free, summary-only, public-safe, and fail-closed.

## 3. Prior Chain Dependency

- Step520 completed the final safety review design for the artifact writer CLI
  actual invocation runtime chain.
- Step521 planned the artifact body generation integration next chain.
- Step522 designed the fixture contract.
- Step523 created the synthetic metadata-only fixture root.
- Step524 designed the fixture validator.
- Step525 added the static fixture validator module, CLI, and focused tests.
- Step526 designed the standalone Makefile target.
- Step527 added the standalone Makefile target.
- Step528 designed release-quality wrapper inclusion.
- Step529 added the fixture validator check to the release-quality wrapper.
- Step530 designed future public-safe remote/manual run recording.
- Step531 added the public-safe remote status marker.
- Step532 planned runtime integration refinement and recommended Mode A
  plan-only bridge as the first mode.

The static fixture validator chain is complete through remote marker coverage.
Runtime refinement has not been built yet. Step533 refines the runtime design
before any future implementation step.

## 4. Runtime Design Goal

The runtime design goal is limited to a selected synthetic metadata-only
fixture case.

The initial runtime should:

- use the selected fixture case
- check the handoff between actual invocation runtime summary metadata and the
  artifact body generation metadata boundary in plan-only form
- avoid invoking artifact body generation runtime in the initial mode
- keep suppressed mode as the default boundary
- reserve safe-metadata mode for a later explicit stage
- avoid request, pointer, and expected body output
- avoid artifact body payload output
- avoid manifest body output
- avoid generated policy body output
- avoid raw stdout/stderr body output
- avoid raw rows, logits, private path values, absolute path values, and raw
  learner text
- avoid file writing
- avoid manifest writer invocation
- emit public-safe summary output only
- fail closed on unsafe output

## 5. Initial Runtime Mode

Mode name:

`plan-only-bridge`

Behavior:

- read fixture metadata files for the selected case
- validate enough selected-case metadata to build a runtime plan summary
- do not invoke artifact body generation runtime
- do not invoke manifest writer
- do not write files
- emit public-safe summary output
- fail closed on unsafe metadata
- return `usage_error` for missing fixture, unsupported mode, or unsupported
  schema

This initial mode is intentionally narrower than the static aggregate
validator. It verifies one selected runtime boundary plan and leaves full
fixture-root validation to the existing validator.

## 6. Later Runtime Modes

### suppressed-smoke

Purpose: run a suppressed artifact body generation smoke from metadata-only
request/pointer metadata.

Safety boundary:

- no artifact body payload output
- no file writing
- no manifest writer invocation
- public-safe summary only
- fail-closed safety scan

Expected fixture case:

- `valid/valid_minimal_suppressed_metadata_only_bridge`

This mode should be separate from the initial plan-only bridge because it
introduces runtime invocation. It should have separate tests, Makefile target
planning, and release-quality staging if added later.

### safe-metadata-smoke

Purpose: allow explicit safe-metadata behavior with count-only metadata such
as body field count or metadata field count.

Safety boundary:

- no payload output
- no file writing
- no manifest writer invocation
- count-only safe metadata
- public-safe summary only

Expected fixture case:

- `valid/valid_safe_metadata_summary_bridge`

This mode should be separate from the initial plan-only bridge because it
expands the output surface, even if only count-only metadata is emitted. It
should have separate tests, Makefile target planning, and release-quality
staging if added later.

## 7. Proposed Runtime Module / CLI

Proposed module:

`python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py`

Proposed tests:

`python/learner_state/tests/test_frozen_policy_generation_artifact_body_generation_runtime_integration.py`

Proposed CLI:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_generation_runtime_integration \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration \
  --fixture-case valid/valid_minimal_suppressed_metadata_only_bridge \
  --mode plan-only-bridge \
  --summary-only \
  --no-file-writing \
  --no-manifest-writer \
  --fail-closed-on-unsafe-output
```

Step533 does not implement this module, CLI, or tests.

## 8. Proposed Runtime Inputs

Required:

- `--fixture-root`
- `--fixture-case`
- `--mode`

Optional flags:

- `--summary-only`
- `--no-file-writing`
- `--no-manifest-writer`
- `--fail-closed-on-unsafe-output`

Mode values:

- initial supported: `plan-only-bridge`
- future reserved: `suppressed-smoke`, `safe-metadata-smoke`

Safer recommendation:

- require explicit `--mode`
- require `--summary-only` for the first runtime CLI
- default file writing to false
- default manifest writer invocation to false
- return `usage_error` for unsupported mode
- return `usage_error` for missing fixture
- return `fail_closed` for unsafe metadata

Explicit mode and summary-only flags reduce accidental expansion of the
runtime surface.

## 9. Proposed Runtime Output Schema

Schema:

`learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.1`

Output mode:

`artifact_body_generation_runtime_integration`

Required fields:

- mode
- runtime_schema_version
- status
- reason_code
- exit_code_category
- case_id
- integration_mode
- artifact_body_runtime_invoked
- artifact_body_runtime_mode
- content_suppressed
- body_suppressed
- summary_only
- request_body_detected
- pointer_body_detected
- expected_body_detected
- artifact_body_payload_detected
- manifest_body_detected
- generated_policy_body_detected
- raw_stdout_body_suppressed
- raw_stderr_body_suppressed
- raw_rows_detected
- logits_detected
- private_path_detected
- absolute_path_detected
- raw_learner_text_detected
- real_data_marker_detected
- performance_metric_body_detected
- file_writing_enabled
- file_writing_detected
- manifest_writer_invoked
- artifact_file_written
- manifest_file_written
- runtime_safety_scan_passed
- runtime_fail_closed
- production_readiness_claimed
- real_data_readiness_claimed
- performance_claims_present

Optional count-only fields:

- runtime_summary_checked
- artifact_body_request_checked
- artifact_body_pointer_checked
- artifact_body_generation_metadata_checked
- metadata_file_count
- unsafe_signal_count

## 10. Expected Plan-Only Pass Summary

For `valid/valid_minimal_suppressed_metadata_only_bridge`, expected
public-safe output:

- mode: `artifact_body_generation_runtime_integration`
- runtime_schema_version:
  `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.1`
- status: pass
- reason_code: none
- exit_code_category: zero
- case_id: `valid/valid_minimal_suppressed_metadata_only_bridge`
- integration_mode: `plan-only-bridge`
- artifact_body_runtime_invoked: false
- artifact_body_runtime_mode: `not_invoked`
- content_suppressed: true
- body_suppressed: true
- summary_only: true
- request_body_detected: false
- pointer_body_detected: false
- expected_body_detected: false
- artifact_body_payload_detected: false
- manifest_body_detected: false
- generated_policy_body_detected: false
- raw_stdout_body_suppressed: true
- raw_stderr_body_suppressed: true
- raw_rows_detected: false
- logits_detected: false
- private_path_detected: false
- absolute_path_detected: false
- raw_learner_text_detected: false
- real_data_marker_detected: false
- performance_metric_body_detected: false
- file_writing_enabled: false
- file_writing_detected: false
- manifest_writer_invoked: false
- artifact_file_written: false
- manifest_file_written: false
- runtime_safety_scan_passed: true
- runtime_fail_closed: false
- production_readiness_claimed: false
- real_data_readiness_claimed: false
- performance_claims_present: false

## 11. Candidate Fixture Case Selection

Candidate cases:

- `valid/valid_minimal_suppressed_metadata_only_bridge`
- `valid/valid_safe_metadata_summary_bridge`
- `valid/valid_no_file_writing_bridge`

Recommendation:

- initial plan-only bridge:
  `valid/valid_minimal_suppressed_metadata_only_bridge`
- later safe-metadata explicit stage:
  `valid/valid_safe_metadata_summary_bridge`
- later no-file-writing guard smoke:
  `valid/valid_no_file_writing_bridge`

The minimal suppressed case is the narrowest first boundary. The
safe-metadata case should wait for an explicit count-only stage. The
no-file-writing case is useful as a later guard but is not the smallest
runtime handoff case.

## 12. Validation Depth In Plan-Only Bridge

Plan-only bridge should validate enough selected-case metadata to be useful
without duplicating the aggregate fixture validator.

Required checks:

- selected case exists
- required metadata files exist
- case kind is valid
- expected status is pass
- runtime summary metadata is pass and `actual_invocation_metadata_only`
- request metadata is summary-only, no-file-writing, no-manifest-writer, and
  no-payload-output
- pointer metadata has no body/path/raw markers
- generation metadata has suppressed or safe metadata status
- expected summary is pass
- expected error is none
- no unsafe sentinel appears in the valid case
- no file writing is requested
- no manifest writer is requested

The static validator remains responsible for aggregate fixture-root behavior.

## 13. Safety Scan Strategy

Scan selected case metadata for:

- request body marker
- pointer body marker
- expected body marker
- artifact body payload marker
- manifest body marker
- generated policy body marker
- raw stdout/stderr body marker
- raw rows marker
- logits / probabilities marker
- private path marker
- absolute path marker
- raw learner text marker
- real data marker
- performance metric body marker
- file writing marker
- manifest writer invocation marker
- production readiness claim
- real-data readiness claim
- model performance claim

Output must not echo unsafe values. Use public-safe reason codes only.

## 14. Reason Code Plan

Potential public-safe reason codes:

- none
- missing_fixture
- missing_required_metadata_file
- unsupported_mode
- unsupported_schema
- unexpected_case_kind
- unexpected_expected_status
- runtime_summary_status
- runtime_summary_body_detected
- request_body_present
- pointer_body_present
- expected_body_present
- artifact_body_payload_detected
- manifest_body_detected
- generated_policy_body_detected
- raw_stdout_body_detected
- raw_stderr_body_detected
- raw_rows_detected
- logits_detected
- private_path_detected
- absolute_path_detected
- raw_learner_text_detected
- real_data_marker_detected
- performance_metric_body_detected
- file_writing_detected
- manifest_writer_invoked
- unsafe_output_residue_risk

Status mapping:

- `none`: pass
- missing fixture / missing file / unsupported mode / unsupported schema:
  `usage_error`
- unsafe signal reason codes: `fail_closed`
- unexpected expected status / case mismatch: `fail_closed`

Use `fail_closed` for unexpected expected status or case mismatch because the
selected-case runtime boundary should not proceed when the fixture expectation
does not match the safe plan.

## 15. Focused Test Plan

Future focused tests should cover:

- plan-only bridge valid case pass
- CLI default or explicit mode behavior
- unsupported mode usage_error
- missing fixture usage_error
- missing required metadata file usage_error
- runtime summary status fail_closed
- request body sentinel fail_closed
- pointer body sentinel fail_closed
- expected body sentinel fail_closed
- artifact body payload sentinel fail_closed
- manifest body sentinel fail_closed
- generated policy body sentinel fail_closed
- raw stdout body sentinel fail_closed
- raw stderr body sentinel fail_closed
- raw rows sentinel fail_closed
- logits sentinel fail_closed
- private path sentinel fail_closed
- absolute path sentinel fail_closed
- raw learner text sentinel fail_closed
- real data marker fail_closed
- performance metric body fail_closed
- file writing detected fail_closed
- manifest writer invocation fail_closed
- output suppresses unsafe values
- no runtime invocation in plan-only mode
- no file residue
- deterministic output

## 16. Makefile / Release-Quality Staging

Suggested future chain:

1. Step534: runtime fixture/update design, if needed
2. Step535: runtime implementation
3. Step536: Makefile target design
4. Step537: Makefile target implementation
5. Step538: release-quality integration design
6. Step539: release-quality wrapper integration
7. Step540: remote/manual run record workflow design
8. Step541: remote status marker

Step533 does not perform these steps.

## 17. Relationship To Existing Validator Chain

- the static validator remains the aggregate fixture-root validator
- runtime refinement is a selected-case runtime boundary check
- runtime refinement must not replace the static validator
- the static validator remains included in release-quality
- runtime refinement should be staged separately
- runtime refinement does not prove artifact body generation integration
  correctness generally

## 18. Relationship To Artifact Body Generation Implementation

- initial plan-only bridge does not invoke artifact body generation
  implementation
- later suppressed-smoke may invoke artifact body generation but still must
  emit no payload and write no files
- later safe-metadata-smoke may expose count-only metadata but no payload
- existing artifact body generation CLI smoke remains separate
- this design does not change artifact body generation implementation

## 19. Relationship To Manifest Writer Chain

- manifest writer integration is out of scope
- manifest writer invocation must remain false
- manifest body must remain absent
- manifest file writing is out of scope
- future manifest writer handoff should be a separate design / fixture /
  validator / marker chain
- current runtime refinement must not be interpreted as manifest writer
  correctness

## 20. Failure Interpretation

Future runtime failure means the selected synthetic metadata-only runtime
boundary failed.

Failure does not prove:

- model performance issue
- manifest writer issue
- production readiness issue
- artifact body generation integration correctness generally

Failures should be interpreted through public-safe reason codes only. Raw
stdout/stderr and payloads must not be copied into docs or reports.

## 21. Non-Claims

This runtime integration refinement design does not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- artifact body generation integration correctness
- manifest writer integration correctness
- generated policy quality
- learner-state estimator correctness
- artifact writer CLI actual invocation correctness generally
- runtime actual invocation correctness generally
- runtime refinement implementation

## 22. Step534 Fixture Update Design Status

Step534 adds the docs-only / planning-only fixture update design:

`docs/frozen_policy_generation_artifact_body_generation_runtime_integration_fixture_update_design.md`

It recommends no fixture update for the initial `plan-only-bridge`. It does
not change fixture JSON, add fixture roots, change validators, change runtime
implementation, change Python code/tests, change Makefile, change the wrapper,
change workflow files, implement artifact body generation integration, connect
manifest writer integration, enable file writing, use real data, compute
metrics, or claim production readiness.

## 23. Public-Safe Checklist

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

## 24. Step535 Implementation Status

Step535 implements the initial selected-case `plan-only-bridge` described in
this design:

- module:
  `python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py`
- focused tests:
  `python/learner_state/tests/test_frozen_policy_generation_artifact_body_generation_runtime_integration.py`
- selected case:
  `valid/valid_minimal_suppressed_metadata_only_bridge`
- runtime schema:
  `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.1`

Only `plan-only-bridge` is supported. `suppressed-smoke` and
`safe-metadata-smoke` remain reserved usage-error modes. The implementation
does not invoke artifact body generation runtime, call the manifest writer,
write files, modify fixture JSON, change validators, add a Makefile target,
change the release-quality wrapper, change workflow files, use real data,
compute metrics, or claim production readiness.

## 25. Step536 Makefile Target Design Status

Step536 adds the docs-only / planning-only standalone Makefile target design:

`docs/frozen_policy_generation_artifact_body_generation_runtime_integration_plan_only_bridge_makefile_target_design.md`

It proposes
`check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration`
for the Step535 `plan-only-bridge` CLI. It does not change Makefile,
release-quality wrapper, workflow files, Python code/tests, fixture JSON,
validators, runtime implementation, artifact body generation runtime
invocation, manifest writer integration, file writing, real-data use, metric
use, or production readiness status.
