# Frozen Policy Generation Artifact Body Generation Runtime Integration Safe-Metadata Runtime Refinement Design

## 1. Scope

This document is the safe-metadata runtime refinement design for artifact body
generation runtime integration.

This is design-only / planning-only. The runtime refinement is designed here
only. This step does not change runtime implementation, change Python
code/tests, change Makefile, change the release-quality wrapper, change
workflow files, change fixture JSON, change validator implementation, invoke
artifact body generation runtime, implement manifest writer integration, or
enable file writing. It is not evidence of production readiness, real-data
readiness, or model performance.

## 2. Prior Completed Chain Dependency

- The plan-only bridge chain is complete through remote marker and final
  safety review.
- The broader final safety review through the manifest writer boundary is
  complete.
- Safe-metadata explicit stage planning is complete.
- The safe-metadata v0.2 planned fixture validator chain is complete through
  remote marker and final safety review.
- The current next action is design-only runtime refinement, not
  implementation.

## 3. Current Runtime State

- module:
  `python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py`
- implemented mode: `plan-only-bridge`
- reserved modes: `suppressed-smoke`, `safe-metadata-smoke`
- current schema:
  `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.1`
- future safe-metadata runtime schema candidate:
  `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.2`
- current `plan-only-bridge` does not invoke artifact body generation runtime
- current `plan-only-bridge` does not invoke manifest writer
- current `plan-only-bridge` does not write files
- current `plan-only-bridge` emits public-safe metadata-only summary output

## 4. Proposed Runtime Refinement Goal

The safe-metadata runtime refinement should:

- introduce or refine `safe-metadata-smoke` mode
- consume planned safe-metadata v0.2 fixture cases
- bridge from fixture metadata to runtime summary
- produce public-safe / metadata-only / body-free output
- record safe metadata body availability as count-only fields
- not emit artifact body payload
- not invoke manifest writer
- not write files
- fail closed if unsafe payload, body, path, raw-output, data, or metric
  markers appear
- remain synthetic-only / no-oracle

## 5. Proposed Runtime Mode

Recommended future mode:

- `--mode safe-metadata-smoke`

Relationship to existing modes:

- `plan-only-bridge`: current implemented metadata-only bridge with no artifact
  body runtime invocation.
- `suppressed-smoke`: reserved future mode for suppressed body runtime checks.
- `safe-metadata-smoke`: proposed next mode for count-only safe-metadata
  runtime integration checks.

Do not implement this mode in Step557.

## 6. Proposed CLI Shape

Proposed future CLI:

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

Recommendation: keep `--fixture-root` as the primary root selector instead of
adding `--planned-safe-metadata-root`. The existing runtime shape already uses
fixture-root semantics, and a single root argument keeps the CLI smaller while
the summary can still record `planned_root: true`.

## 7. Proposed Runtime Schema

Recommended future runtime schema:

- `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.2`

Minimal safe subset for the first v0.2 summary:

- mode
- runtime_schema_version
- status
- reason_code
- exit_code_category
- case_id
- integration_mode: `safe-metadata-smoke`
- planned_root: `true`
- safe_metadata_v0_2_planned_checked: `true`
- artifact_body_runtime_invoked
- artifact_body_runtime_mode
- artifact_body_payload_available
- artifact_body_payload_emitted
- safe_metadata_body_available
- safe_metadata_body_field_count
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
- runtime_summary_checked
- artifact_body_request_checked
- artifact_body_pointer_checked
- artifact_body_generation_metadata_checked
- metadata_file_count
- unsafe_signal_count

The implementation step may choose an even smaller v0.2 subset if that reduces
output surface while preserving fail-closed safety.

## 8. Proposed Fixture Case Usage

Primary candidate for the first runtime smoke:

- `valid/valid_safe_metadata_explicit_runtime_bridge`

Guard candidates for later expansion:

- `valid/valid_safe_metadata_count_only_bridge`
- `valid/valid_safe_metadata_no_file_writing_bridge`
- `valid/valid_safe_metadata_no_manifest_writer_bridge`

Invalid cases to check in later implementation and test steps:

- unsafe body, payload, path, raw-output, logits/probabilities, data marker,
  and performance marker cases from the planned root

Recommendation: first runtime implementation should use one primary valid case
only. The guard valid cases and invalid cases should be added after the first
metadata handoff smoke is stable and output suppression is verified.

## 9. Proposed Expected Output for First Runtime Smoke

Suggested first case:

- `valid/valid_safe_metadata_explicit_runtime_bridge`

Expected output categories:

- status: `pass`
- reason_code: `none`
- integration_mode: `safe-metadata-smoke`
- planned_root: `true`
- safe_metadata_body_available: `true`
- safe_metadata_body_field_count: count-only value from fixture metadata
- artifact_body_payload_emitted: `false`
- content_suppressed: `true`
- body_suppressed: `true`
- summary_only: `true`
- request, pointer, and expected bodies detected: `false`
- artifact body payload detected: `false`
- manifest body detected: `false`
- generated policy body detected: `false`
- raw stdout/stderr body emitted: `false`
- raw rows, logits/probabilities, private/absolute path values, raw learner
  text, real data marker, and performance body detected: `false`
- file_writing_enabled: `false`
- manifest_writer_invoked: `false`

Artifact body runtime invocation design question:

- Option A: metadata handoff only, no actual artifact body generation runtime
  invocation.
- Option B: invoke artifact body generation runtime in safe-metadata mode,
  capture, scan, and suppress output.

Recommendation: choose Option A for the first implementation. The current
planned root represents a metadata handoff boundary, and avoiding actual
artifact body generation runtime invocation keeps the first `safe-metadata`
runtime smoke small, body-free, and closer to the already reviewed validator
chain. Option B should require a later safety wrapper design with explicit
capture/suppression rules before any invocation path is added.

## 10. Fail-Closed Design

Future implementation should map failure categories to public-safe status and
reason codes:

- unsupported mode: `usage_error`
- missing fixture root: `usage_error`
- missing fixture case: `usage_error`
- missing required metadata file: `usage_error`
- invalid JSON: `usage_error`
- unsupported fixture schema: `usage_error`
- unsafe request body marker: `fail_closed`
- unsafe pointer body marker: `fail_closed`
- unsafe expected body marker: `fail_closed`
- artifact body payload marker: `fail_closed`
- manifest body marker: `fail_closed`
- generated policy body marker: `fail_closed`
- raw stdout/stderr body marker: `fail_closed`
- raw rows marker: `fail_closed`
- logits/probabilities marker: `fail_closed`
- private/absolute path marker: `fail_closed`
- raw learner text marker: `fail_closed`
- real data marker: `fail_closed`
- performance metric body marker: `fail_closed`
- file writing requested: `fail_closed`
- manifest writer requested: `fail_closed`
- unsafe output surface: `fail_closed`
- mismatched expected status: `mismatch`, if the mismatch is between expected
  public-safe summary and observed public-safe summary

Unsafe values must not be echoed in CLI or test output.

## 11. Output Suppression Policy

Output may include:

- mode
- schema
- status
- reason_code
- case id
- aggregate/count-only metadata
- boolean safety flags
- unsafe_signal_count
- root_errors summary

Output must not include:

- fixture JSON body
- request body
- pointer body
- expected body
- artifact body payload
- manifest body
- generated policy body
- raw stdout/stderr body
- raw rows
- logits / probabilities
- private / absolute path values
- raw learner text
- real participant data
- performance metric body

## 12. Test Plan for Future Implementation

Future implementation tests should cover:

- `safe-metadata-smoke` valid primary case passes
- missing fixture root maps to `usage_error`
- missing fixture case maps to `usage_error`
- unsupported mode maps to `usage_error`
- unsupported schema maps to `usage_error`
- artifact body payload marker maps to `fail_closed`
- manifest body marker maps to `fail_closed`
- generated policy body marker maps to `fail_closed`
- request/pointer/expected body marker maps to `fail_closed`
- raw stdout/stderr body marker maps to `fail_closed`
- raw rows, logits/probabilities, path-value, raw learner, real data, and
  performance marker cases map to `fail_closed`
- file writing requested maps to `fail_closed`
- manifest writer requested maps to `fail_closed`
- mismatched expected status maps to `mismatch`
- output suppresses unsafe values
- no file writing / no residue
- existing `plan-only-bridge` behavior remains unchanged
- existing safe-metadata v0.2 fixture validator remains unchanged
- active root validator remains unchanged

## 13. Makefile / Release-Quality Staging

Recommended safer next chain:

- Step558: safe-metadata runtime fixture/expected-output design
- Step559: safe-metadata runtime fixture contract update design, if Step558
  finds gaps
- Step560: safe-metadata runtime implementation design
- Step561: safe-metadata runtime implementation
- Step562: safe-metadata runtime Makefile target design
- Step563: safe-metadata runtime Makefile target implementation
- Step564: safe-metadata runtime release-quality integration design
- Step565: safe-metadata runtime release-quality wrapper integration
- Step566: safe-metadata runtime remote/manual run record workflow design
- Step567: safe-metadata runtime remote status marker
- Step568: safe-metadata runtime final safety review

This staging keeps fixture/expected-output design ahead of runtime
implementation and keeps Makefile / release-quality integration behind a
verified local runtime boundary.

## 14. Relationship to Completed Validator Chain

- The validator chain validates the planned fixture contract.
- Runtime refinement will use planned fixture metadata.
- Validator pass does not prove runtime correctness.
- The remote marker does not prove runtime correctness.
- Runtime refinement should preserve the validator boundary.
- The active root remains separate until a separate merge design exists.

## 15. Relationship to Artifact Body Generation Safe-Metadata CLI Smoke

- Existing artifact body generation safe-metadata CLI smoke remains separate.
- Safe-metadata runtime integration is a handoff boundary.
- CLI smoke does not prove runtime integration.
- Runtime integration smoke should not prove free-form body safety.
- Artifact body payload should remain suppressed.

## 16. Relationship to Manifest Writer and File-Writing Chains

- Manifest writer remains out of scope.
- File writing remains out of scope.
- Manifest writer invocation should remain `false`.
- `artifact_file_written` and `manifest_file_written` should remain `false`.
- Manifest body should not be emitted.
- Any future manifest integration requires separate design.

## 17. Residual Risks

- `safe-metadata-smoke` design may still be metadata handoff only.
- Actual artifact body runtime invocation may require a later safety wrapper.
- Fixture metadata may need schema refinement.
- Planned root may need future active merge design.
- Count-only body metadata does not prove payload correctness.
- No free-form body safety proof is provided.
- No production / real-data readiness is provided.
- No model performance evidence is provided.

## 18. Recommended Next Step

Options:

- Step558: safe-metadata runtime fixture/expected-output design
- Step558: safe-metadata runtime implementation design
- Step558: safe-metadata runtime fixture contract update design
- Step558: safe-metadata runtime implementation

Recommendation: Step558 should be safe-metadata runtime fixture/expected-output
design. That keeps the next move design-only, verifies whether the planned
fixture metadata is enough for v0.2 runtime summaries, and avoids moving
directly into runtime implementation.

## 19. Non-Equivalence Cautions

- runtime refinement design is not runtime implementation
- planned-root fixture validator status is not runtime correctness
- validator pass is not artifact body generation correctness generally
- safe-metadata runtime smoke, when later added, will not prove
  safe-metadata free-form body safety
- count-only body metadata is not artifact body payload correctness
- runtime integration is not manifest writer readiness
- release-quality success is not production readiness
- synthetic-only pass is not real-data readiness

## 20. Non-Claims

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

## 21. Public-Safe Checklist

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

## 22. Step557 Status

Step557 creates this runtime refinement design only. It does not change
runtime implementation, Python code/tests, Makefile, release-quality wrapper,
workflow files, fixture JSON, validator implementation, artifact body
generation runtime invocation, manifest writer integration, file writing,
real-data use, metric use, or production readiness status.

## 23. Step558 Fixture Expected Output Design Status

Step558 adds the design-only / planning-only fixture/expected-output design
recommended here:

`docs/frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_runtime_fixture_expected_output_design.md`

It fixes the primary planned fixture case, expected public-safe runtime summary
surface, failure categories, temporary mutation strategy, and implementation
staging without changing runtime implementation, Python code/tests, Makefile,
release-quality wrapper, workflow files, fixture JSON, validator
implementation, artifact body generation runtime invocation, manifest writer
integration, or file writing.

## 24. Step559 Runtime Implementation Status

Step559 implements `safe-metadata-smoke` as the metadata handoff only runtime
mode staged by this design. The implementation emits v0.2 public-safe summary
output over the planned primary case, preserves existing `plan-only-bridge`
behavior, and keeps artifact body generation runtime invocation, manifest
writer invocation, and file writing disabled.

Step559 does not add a Makefile target, add release-quality wrapper
integration, change workflow files, change fixture JSON, implement artifact
body generation runtime invocation, implement manifest writer integration, or
enable file writing.
