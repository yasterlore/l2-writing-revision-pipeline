# Frozen Policy Generation Artifact Body Generation Runtime Integration Safe-Metadata Runtime Fixture Expected Output Design

## 1. Scope

This document is the fixture/expected-output design for a future
`safe-metadata-smoke` runtime integration step for artifact body generation
runtime integration.

This is design-only / planning-only. It does not change runtime
implementation, Python code/tests, Makefile, release-quality wrapper, workflow
files, fixture JSON, validator implementation, artifact body generation
runtime invocation, manifest writer integration, or file writing. It is not
evidence of production readiness, real-data readiness, or model performance.

## 2. Prior Completed Chain Dependency

- The plan-only bridge chain is complete through remote marker and final
  safety review.
- The broader final safety review through the manifest writer boundary is
  complete.
- The safe-metadata v0.2 planned fixture validator chain is complete through
  remote marker and final safety review.
- Step557 recommends a metadata handoff only first runtime refinement.
- Step558 fixes the fixture / expected-output contract before implementation.

## 3. Existing Fixture Topology

Active fixture root:

- `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration/`
- aggregate: 28 cases / 196 JSON files
- validation family: active v0.1 fixture validation
- Step558 does not modify this root

Planned safe-metadata v0.2 fixture root:

- `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration_planned_safe_metadata_v0_2/`
- aggregate: 24 cases / 168 JSON files
- valid cases: 4
- invalid cases: 20
- layout: 7 metadata files per case
- separate validator status: available through the planned-root validator
- Step558 does not modify this root

## 4. Fixture Update Decision

Options:

- Option A: use the existing planned root as-is for the first
  `safe-metadata-smoke` implementation.
- Option B: add a new runtime-specific planned fixture root before
  implementation.
- Option C: add expected-runtime-output metadata files to existing planned
  cases.
- Option D: merge the planned root into the active root before implementation.

Comparison:

- Safety: Option A keeps fixture churn at zero and preserves the reviewed
  planned-root boundary. Options B and C increase fixture surface before the
  runtime has consumed it. Option D changes active validation scope and is not
  appropriate without a separate merge design.
- Release-quality stability: Option A keeps the current wrapper and validator
  behavior stable. Options B through D require additional validation staging.
- Implementation risk: Option A is the smallest metadata handoff path. Options
  B and C may be useful later if v0.2 summary fields need stronger fixtures.
  Option D has the highest blast radius.
- Validator compatibility: Option A uses the already validated 24-case planned
  root. Options B and C need validator updates. Option D needs active-root
  validator redesign.
- Schema clarity: Option A keeps runtime schema v0.2 as a runtime output
  contract rather than a fixture JSON expansion. Option C may later make sense
  if expected runtime summaries need fixture-side enumeration.
- Future active merge complexity: Option A defers merge complexity. Option D
  brings it forward too early.
- Docs burden: Option A has the smallest documentation update. Options B
  through D require more map updates.
- Fixture churn: Option A has none in Step558.

Recommendation: use Option A for the first metadata handoff only runtime
implementation. If implementation discovers missing fields, add a later
fixture update design instead of changing fixture JSON in Step558.

## 5. Primary Runtime Case

Recommended first case:

- `valid/valid_safe_metadata_explicit_runtime_bridge`

Rationale:

- It is a valid planned safe-metadata v0.2 case.
- It represents the explicit runtime bridge semantics most directly.
- It can support a first metadata handoff smoke with expected status `pass`
  and reason code `none`.
- It should not invoke artifact body generation runtime in the first
  implementation.
- It should not invoke manifest writer.
- It should not write files.

## 6. Guard / Later Cases

Guard valid cases for later expansion:

- `valid/valid_safe_metadata_count_only_bridge`
- `valid/valid_safe_metadata_no_file_writing_bridge`
- `valid/valid_safe_metadata_no_manifest_writer_bridge`

Invalid cases for later fail-closed and mismatch coverage:

- `invalid_safe_metadata_unsupported_schema`
- `invalid_safe_metadata_mismatched_expected_status`
- `invalid_safe_metadata_artifact_body_payload_present`
- `invalid_safe_metadata_manifest_body_present`
- `invalid_safe_metadata_generated_policy_body_present`
- `invalid_safe_metadata_request_body_present`
- `invalid_safe_metadata_pointer_body_present`
- `invalid_safe_metadata_expected_body_present`
- `invalid_safe_metadata_raw_stdout_body_present`
- `invalid_safe_metadata_raw_stderr_body_present`
- `invalid_safe_metadata_raw_rows_present`
- `invalid_safe_metadata_logits_present`
- `invalid_safe_metadata_private_path_present`
- `invalid_safe_metadata_absolute_path_present`
- `invalid_safe_metadata_raw_learner_text_present`
- `invalid_safe_metadata_real_data_marker_present`
- `invalid_safe_metadata_performance_metric_body_present`
- `invalid_safe_metadata_file_writing_requested`
- `invalid_safe_metadata_manifest_writer_requested`
- `invalid_safe_metadata_unsafe_output_surface`

Recommendation: Step559 should implement the primary valid case plus a small
set of fail-closed unit tests using temporary fixture mutations. A full
invalid-case sweep can follow after the first runtime boundary is stable.

## 7. Expected Runtime CLI

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

`--fixture-root` should be sufficient. A separate
`--planned-safe-metadata-root` option is not needed for the first
implementation because the runtime can record `planned_root: true` in the
summary.

## 8. Expected Runtime Schema

Recommended runtime schema:

- `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.2`

Minimum expected fields:

- `mode`
- `runtime_schema_version`
- `status`
- `reason_code`
- `exit_code_category`
- `case_id`
- `integration_mode`
- `planned_root`
- `safe_metadata_v0_2_planned_checked`
- `artifact_body_runtime_invoked`
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
- `runtime_summary_checked`
- `artifact_body_request_checked`
- `artifact_body_pointer_checked`
- `artifact_body_generation_metadata_checked`
- `metadata_file_count`
- `unsafe_signal_count`

The implementation step may choose a smaller subset if it keeps the output
surface tighter while preserving public-safe fail-closed behavior.

## 9. Expected Pass Output for Primary Case

For `valid/valid_safe_metadata_explicit_runtime_bridge`, expected public-safe
summary values are:

- `mode`: `artifact_body_generation_runtime_integration`
- `runtime_schema_version`:
  `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.2`
- `status`: `pass`
- `reason_code`: `none`
- `exit_code_category`: `zero`
- `case_id`: `valid/valid_safe_metadata_explicit_runtime_bridge`
- `integration_mode`: `safe-metadata-smoke`
- `planned_root`: `true`
- `safe_metadata_v0_2_planned_checked`: `true`
- `artifact_body_runtime_invoked`: `false`
- `artifact_body_runtime_mode`: `not_invoked`
- `artifact_body_payload_available`: `false`
- `artifact_body_payload_emitted`: `false`
- `safe_metadata_body_available`: `true`
- `safe_metadata_body_field_count`: count-only if present; otherwise
  `not_recorded_in_public_safe_summary`
- `content_suppressed`: `true`
- `body_suppressed`: `true`
- `summary_only`: `true`
- `request_body_detected`: `false`
- `pointer_body_detected`: `false`
- `expected_body_detected`: `false`
- `artifact_body_payload_detected`: `false`
- `manifest_body_detected`: `false`
- `generated_policy_body_detected`: `false`
- `raw_stdout_body_suppressed`: `true`
- `raw_stderr_body_suppressed`: `true`
- `raw_rows_detected`: `false`
- `logits_detected`: `false`
- `private_path_detected`: `false`
- `absolute_path_detected`: `false`
- `raw_learner_text_detected`: `false`
- `real_data_marker_detected`: `false`
- `performance_metric_body_detected`: `false`
- `file_writing_enabled`: `false`
- `file_writing_detected`: `false`
- `manifest_writer_invoked`: `false`
- `artifact_file_written`: `false`
- `manifest_file_written`: `false`
- `runtime_safety_scan_passed`: `true`
- `runtime_fail_closed`: `false`
- `production_readiness_claimed`: `false`
- `real_data_readiness_claimed`: `false`
- `performance_claims_present`: `false`
- `metadata_file_count`: `7`
- `unsafe_signal_count`: `0`

Boolean casing should match the future runtime emitter. This design records
the intended lowercase summary values.

## 10. Expected Usage Error Cases

Future runtime should return public-safe `usage_error` summaries for:

- missing fixture root
- missing fixture case
- missing required metadata file
- invalid JSON
- unsupported schema
- unsupported mode
- invalid mode / fixture mismatch
- missing required expected-runtime metadata field, if the implementation
  makes that field mandatory

Usage-error output must remain body-free and must not echo unsafe values.

## 11. Expected Fail-Closed Cases

Future runtime should return public-safe `fail_closed` summaries when any of
these markers are present:

- request body present
- pointer body present
- expected body present
- artifact body payload present
- manifest body present
- generated policy body present
- raw stdout/stderr body present
- raw rows present
- logits/probabilities present
- private/absolute path value present
- raw learner text present
- real data marker present
- performance metric body present
- file writing requested
- manifest writer requested
- unsafe output surface

Fail-closed output must report only public-safe reason codes and counts. It
must not echo unsafe values.

## 12. Expected Mismatch Cases

Future runtime should return `mismatch` when the fixture-side expected status
or reason code disagrees with the observed public-safe runtime summary.

Mismatch should stay distinct from `fail_closed`: a body/payload/path/raw/data
signal is a safety failure, while expected-vs-observed status disagreement is
a contract mismatch.

## 13. Temporary Mutation Testing Strategy

Future tests should use temporary copies or in-memory mutations only.

Test strategy:

- do not mutate real fixture JSON
- use temporary directories for missing-file, invalid-JSON, and unsafe-marker
  tests
- clean up temporary files
- assert no residue after runtime tests
- assert output suppression for unsafe values
- keep the planned fixture root unchanged
- keep the active fixture root unchanged

## 14. Runtime Implementation Boundary

Future first implementation should include:

- `safe-metadata-smoke` mode
- primary valid case pass
- metadata-only output
- body-free summary
- fail-closed scans
- usage-error handling
- no file writing
- no manifest writer invocation
- no artifact body generation runtime invocation in the first implementation

Future first implementation should not include:

- actual artifact body generation runtime invocation
- manifest writer integration
- artifact body payload emission
- file writing
- active root merge
- full invalid planned-case sweep unless simple and safe
- release-quality integration
- production readiness, real-data readiness, or model performance claims

## 15. Future Implementation Test Plan

Future tests should cover:

- primary valid case passes
- safe metadata body availability and count-only behavior
- unsafe body marker temporary mutation maps to `fail_closed`
- file writing requested temporary mutation maps to `fail_closed`
- manifest writer requested temporary mutation maps to `fail_closed`
- unsupported schema maps to `usage_error`
- missing fixture case maps to `usage_error`
- unsupported mode maps to `usage_error`
- mismatched expected status maps to `mismatch`
- output suppresses unsafe values
- no file writing / no residue
- existing `plan-only-bridge` tests still pass
- existing safe-metadata v0.2 validator tests still pass
- active root validator remains unchanged

## 16. Makefile / Release-Quality Staging

Recommended staging if no fixture gaps are found:

- Step559: safe-metadata runtime implementation
- Step560: safe-metadata runtime Makefile target design
- Step561: safe-metadata runtime Makefile target implementation
- Step562: safe-metadata runtime release-quality integration design
- Step563: safe-metadata runtime release-quality wrapper integration
- Step564: safe-metadata runtime remote/manual run record workflow design
- Step565: safe-metadata runtime remote status marker
- Step566: safe-metadata runtime final safety review

Fallback staging if fixture gaps are found:

- Step559: safe-metadata runtime fixture update design
- Step560: fixture update implementation
- Step561: runtime implementation

Recommendation: choose the first path only if the existing planned root is
enough for metadata handoff only. Otherwise, pause before implementation and
design the fixture update first.

## 17. Relationship to Completed Validator Chain

- The completed validator chain validates the planned fixture contract.
- Runtime expected-output design uses that contract.
- Validator pass does not prove runtime correctness.
- The remote marker does not prove runtime correctness.
- Runtime implementation should preserve the validator boundary.
- The active root remains separate until a separate active merge design exists.

## 18. Relationship to Artifact Body Generation Safe-Metadata CLI Smoke

- Existing artifact body generation safe-metadata CLI smoke remains separate.
- The first `safe-metadata-smoke` runtime should be metadata handoff only.
- It should not replace artifact body generation CLI smoke.
- It should not prove free-form body safety.
- Artifact body payload should remain suppressed.

## 19. Relationship to Manifest Writer and File-Writing Chains

- Manifest writer remains out of scope.
- File writing remains out of scope.
- Manifest writer invocation should remain `false`.
- `artifact_file_written` and `manifest_file_written` should remain `false`.
- Manifest body should not be emitted.
- Any future manifest integration requires separate design.

## 20. Residual Risks

- Expected-output design does not implement runtime.
- Metadata handoff does not prove actual artifact body generation runtime
  behavior.
- Count-only safe metadata does not prove artifact body payload correctness.
- Free-form body safety remains unproven.
- Active/planned root merge remains undesigned.
- Future schema v0.2 implementation may reveal fixture gaps.
- Release-quality integration for runtime smoke is future work.
- No production readiness or real-data readiness is provided.

## 21. Recommended Next Step

Options:

- Step559: safe-metadata runtime implementation
- Step559: safe-metadata runtime fixture update design
- Step559: safe-metadata runtime implementation design
- Step559: active/planned root merge design

Recommendation: Step559 should be safe-metadata runtime implementation only if
it is constrained to metadata handoff, no artifact body generation runtime
invocation, no manifest writer invocation, no file writing, and public-safe
summary output. If implementation review finds missing fixture-side metadata,
choose safe-metadata runtime fixture update design instead.

## 22. Non-Equivalence Cautions

- fixture/expected-output design is not runtime implementation
- runtime expected-output contract is not runtime correctness
- planned-root fixture validator status is not runtime correctness
- validator pass is not artifact body generation correctness generally
- safe-metadata runtime smoke, when later added, will not prove
  safe-metadata free-form body safety
- count-only body metadata is not artifact body payload correctness
- runtime integration is not manifest writer readiness
- release-quality success is not production readiness
- synthetic-only pass is not real-data readiness

## 23. Non-Claims

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

## 24. Public-Safe Checklist

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

## 25. Step558 Status

Step558 creates this fixture/expected-output design only. It does not change
runtime implementation, Python code/tests, Makefile, release-quality wrapper,
workflow files, fixture JSON, validator implementation, artifact body
generation runtime invocation, manifest writer integration, file writing,
real-data use, metric use, or production readiness status.

## 26. Step559 Runtime Implementation Status

Step559 implements the `safe-metadata-smoke` metadata handoff only runtime mode
designed here. It uses the planned primary case
`valid/valid_safe_metadata_explicit_runtime_bridge`, emits runtime schema
`learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.2`,
records public-safe count-only metadata, and fail-closes unsafe markers.

Step559 does not add a Makefile target, add release-quality wrapper
integration, change workflow files, change fixture JSON, invoke artifact body
generation runtime, invoke manifest writer, or write files.

## 27. Step560 Makefile Target Design Status

Step560 adds the design-only / planning-only Makefile target design for the
Step559 `safe-metadata-smoke` runtime CLI:

`docs/frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_runtime_makefile_target_design.md`

It does not implement the Makefile target, change release-quality wrapper,
change workflow files, change Python code/tests, change fixture JSON, change
runtime implementation, invoke artifact body generation runtime, invoke
manifest writer, or write files.
