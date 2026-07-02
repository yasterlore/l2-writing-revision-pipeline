# Frozen Policy Generation Artifact Body Generation Runtime Integration Safe-Metadata Fixture Update Design

## 1. Scope

This document is the fixture/update design for a future safe-metadata explicit
stage in artifact body generation runtime integration. It follows the Step544
safe-metadata explicit stage planning design and decides how to stage fixture,
schema, and validator work before any runtime implementation.

This is design-only / planning-only. It does not change fixture JSON, add a
fixture root, change validators, change runtime implementation, change Python
code/tests, change Makefile, change the release-quality wrapper, change
workflow files, invoke artifact body generation runtime, implement manifest
writer integration, or perform file writing. It does not prove production
readiness, real-data readiness, or model performance.

## 2. Prior Completed Chain Dependency

- Step532-Step534 planned the first artifact body generation runtime
  integration boundary and selected the existing Step523 fixture root for the
  initial `plan-only-bridge`.
- Step535-Step541 implemented, targeted, release-quality integrated, and
  recorded the selected-case `plan-only-bridge` runtime smoke.
- Step542 completed the `plan-only-bridge` final safety review.
- Step543 completed the broader final safety review through the manifest
  writer boundary.
- Step544 completed safe-metadata explicit stage planning and recommended a
  fixture/update design before implementation.

The `plan-only-bridge` chain is complete through remote marker and final
safety review. The broader final safety review through the manifest writer
boundary is complete. Safe-metadata explicit stage planning is complete. This
Step545 design keeps the next stage planning-only and does not implement the
safe-metadata runtime path.

## 3. Existing Fixture Root Assessment

Fixture root under review:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration/`

Body-free assessment:

- The existing root was created for artifact body generation integration
  fixture validation.
- The root has 28 cases, 196 JSON files, and a seven-file layout per case.
- The existing validator and release-quality wrapper already cover this root.
- The root is already used by the `plan-only-bridge` runtime integration.
- The root may be reused for the safe-metadata stage only if selected-case
  metadata is sufficient for a bounded runtime summary.
- Step545 does not change fixture JSON.

## 4. Candidate Safe-Metadata Case Assessment

Primary candidate:

`valid/valid_safe_metadata_summary_bridge`

Body-free assessment:

- The case name suggests an intended safe-metadata summary bridge.
- The case should remain synthetic-only.
- The case should remain public-safe.
- The case should not contain artifact body payload.
- The case should not contain manifest body.
- The case should not contain generated policy body.
- The case should not request file writing.
- The case should not request manifest writer invocation.
- The case should provide enough count-only / metadata-only information for a
  later safe-metadata runtime integration smoke.

This document does not quote fixture body. Exact field sufficiency is to be
verified in a later step before implementation.

## 5. Fixture Update Decision

| Option | Safety | Implementation risk | Existing root compatibility | Existing validator compatibility | Release-quality stability | Output surface clarity | New reason code need | Body/payload leakage risk | Future marker clarity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Option A: no fixture update required; use existing `valid/valid_safe_metadata_summary_bridge` | Medium until fields are verified | Low | High | High if fields already exist | High | Medium | Low if existing codes suffice | Medium if body availability is ambiguous | Medium |
| Option B: small fixture metadata extension required before runtime implementation | High | Medium | High | Medium, may need validator work | Medium until staged | High | Medium | Low if extension is body-free | High |
| Option C: add new valid/invalid cases to existing fixture root before runtime implementation | High | Medium to high | Medium | Medium, validator counts change | Medium | High | Medium to high | Low if cases stay body-free | High |
| Option D: create separate safe-metadata runtime fixture root | High but broader | High | Low | Low without new validator | Low initially | High | Medium | Low if isolated | Medium |
| Option E: defer runtime safe-metadata implementation and rely on existing artifact body generation safe-metadata CLI smoke for now | High short-term | Low | High | High | High | Low for runtime integration | Low | Low | Low for runtime marker clarity |

Recommended decision: Option B as a separate follow-up design path before
runtime implementation, unless a later body-free fixture/schema review shows
that all required safe-metadata runtime fields already exist.

This is a conservative choice. The existing case name is useful, but name alone
is not enough to decide runtime suitability. A small metadata extension path
keeps the existing root and release-quality chain stable while leaving room to
define count-only body metadata, safe-metadata body status, unsupported output
surface markers, and any new reason codes without exposing payloads.

Step545 performs no fixture update. The next step should remain design-only.

## 6. Proposed Initial Safe-Metadata Case

Primary candidate:

- `valid/valid_safe_metadata_summary_bridge`: candidate for an initial
  selected-case safe-metadata runtime smoke, intended to exercise a bounded
  metadata summary bridge without artifact body payload, manifest body,
  generated policy body, file writing, or manifest writer invocation.

Fallback candidates if needed:

- `valid/valid_no_file_writing_bridge`: candidate for verifying the no-file
  writing guard if safe-metadata fixture design needs a dedicated guard case.
- `valid/valid_no_manifest_writer_bridge`: candidate for verifying the no
  manifest writer invocation guard if safe-metadata fixture design needs a
  dedicated guard case.

The fallback cases should not replace the primary safe-metadata summary case
unless the next fixture/update design finds that a guard-first stage is safer.

## 7. Required Metadata Fields for Safe-Metadata Runtime

Future selected-case runtime checks should read body-free metadata fields such
as:

- case id / case kind / expected status / expected reason code
- runtime summary status and suppression flags
- request metadata summary-only / no-file-writing / no-manifest-writer /
  no-payload-output flags
- pointer metadata no-body / no-path / no-raw flags
- generation metadata safe-metadata mode or body status
- safe metadata body availability flag
- count-only body field count
- artifact body payload absence flag
- manifest body absence flag
- generated policy body absence flag
- artifact file written false
- manifest file written false
- expected integration summary status
- expected error none

The runtime should not require or describe raw body contents.

## 8. Expected Runtime Output Surface for Safe-Metadata Stage

Allowed public-safe output:

- mode
- runtime schema version
- status
- reason_code
- exit_code_category
- case_id
- integration_mode
- safe_metadata_runtime_invoked or artifact_body_runtime_invoked status
- safe_metadata_body_available flag
- safe_metadata_body_status
- body_field_count
- content_suppressed
- body_payload_suppressed
- request_body_detected false
- pointer_body_detected false
- expected_body_detected false
- artifact_body_payload_detected false
- manifest_body_detected false
- generated_policy_body_detected false
- raw_stdout_body_suppressed true
- raw_stderr_body_suppressed true
- raw_rows_detected false
- logits_detected false
- private_path_detected false
- absolute_path_detected false
- raw_learner_text_detected false
- real_data_marker_detected false
- performance_metric_body_detected false
- file_writing_enabled false
- file_writing_detected false
- manifest_writer_invoked false
- artifact_file_written false
- manifest_file_written false
- runtime_safety_scan_passed true
- runtime_fail_closed false
- production_readiness_claimed false
- real_data_readiness_claimed false
- performance_claims_present false
- unsafe_signal_count

Disallowed output:

- actual artifact body payload
- generated policy body
- manifest body
- request / pointer / expected body
- raw stdout/stderr body
- raw rows
- logits / probabilities
- private / absolute path values
- raw learner text
- real participant data
- performance metric body

## 9. Validator Update Implications

- The existing artifact body generation integration fixture validator validates
  root-level safety.
- If the existing safe-metadata case already contains the required metadata and
  expected summary, validator update may not be required.
- If new fields, cases, or reason codes are needed, validator update should be
  a separate implementation step.
- Step545 does not change validator implementation.
- Release-quality counts should not change in Step545.

## 10. Runtime Schema Implications

| Option | Compatibility | Output clarity | Payload exposure risk | Marker clarity | Docs burden |
| --- | --- | --- | --- | --- | --- |
| Keep `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.1` and add mode-specific fields only if already compatible | High | Medium | Medium unless fields are tightly bounded | Medium | Low |
| Introduce `v0.2` for safe-metadata explicit stage | Medium | High | Low if schema is explicit | High | Medium |
| Introduce a separate schema for safe-metadata runtime integration | Low to medium | High | Low | High | High |

Recommended schema path: prefer `v0.2` if the safe-metadata stage requires new
fields such as `safe_metadata_body_available`, `safe_metadata_body_status`, or
`body_field_count`. Keep `v0.1` only if the later runtime refinement design
confirms the existing schema can express the safe-metadata summary without
ambiguity or body/payload exposure.

## 11. Runtime Mode Naming

| Option | Compatibility | Naming clarity | Staging clarity | Risk |
| --- | --- | --- | --- | --- |
| `safe-metadata-smoke` | High, already reserved | Good | High | Low to medium |
| `safe-metadata-explicit` | Medium | Highest | Medium | Medium, new naming policy |
| `safe-metadata-bridge` | Medium | Good | Medium | Medium |
| Keep as reserved and do not implement yet | High | Clear short-term | High for design | Low |

Recommended mode path: keep `safe-metadata-smoke` reserved for now and use it
as the likely implementation mode after fixture/update and runtime refinement
designs. Do not implement it in Step545.

## 12. Safety Scan Requirements

Future selected-case safe-metadata scans should detect:

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
- unsupported safe-metadata output surface marker

## 13. Fail-Closed Behavior

Planned status mapping:

- unsupported mode: `usage_error`
- missing fixture: `usage_error`
- missing required metadata file: `usage_error`
- unsupported schema: `usage_error`
- unsafe body/payload marker: `fail_closed`
- raw stdout/stderr body marker: `fail_closed`
- private/absolute path marker: `fail_closed`
- raw learner text marker: `fail_closed`
- real data marker: `fail_closed`
- unexpected file writing: `fail_closed`
- unexpected manifest writer invocation: `fail_closed`
- unexpected artifact body payload availability: `fail_closed`
- unsafe output residue risk: `fail_closed`
- mismatched expected status: `fail_closed` or `mismatch`, to be decided in
  runtime refinement design

Output must not echo unsafe values.

## 14. Proposed Next-Step Staging

Because this design recommends Option B as the conservative path, the next
staging should keep fixture/schema definition ahead of runtime implementation:

- Step546: safe-metadata fixture root/update design
- Step547: safe-metadata fixture root/update implementation, only if Step546
  confirms changes are required
- Step548: safe-metadata validator update design, only if schemas, counts, or
  reason codes change
- Step549: safe-metadata validator update implementation, only if needed
- Later: safe-metadata runtime refinement design
- Later: safe-metadata runtime implementation
- Later: safe-metadata Makefile target design and implementation
- Later: safe-metadata release-quality integration design and wrapper
  integration
- Later: safe-metadata remote/manual run record workflow design and remote
  status marker
- Later: safe-metadata final safety review

If Step546 determines that no fixture update is required, the chain can move
to safe-metadata runtime refinement design before any implementation.

## 15. Relationship to Existing Artifact Body Generation Safe-Metadata CLI Smoke

- Existing artifact body generation safe-metadata CLI smoke remains separate.
- Runtime integration safe-metadata stage should not replace it.
- Existing CLI smoke is about artifact body generation behavior.
- Runtime integration safe-metadata stage is about the handoff boundary.
- Both must remain body-free in docs.
- Neither proves free-form body safety generally.

## 16. Relationship to Manifest Writer and File-Writing Chains

- Safe-metadata runtime integration must not invoke manifest writer.
- Manifest writer handoff must remain separate.
- Manifest body remains out of scope.
- Manifest file writing remains out of scope.
- Artifact body file-writing remains separate.
- No output path writing should occur in the safe-metadata runtime stage.

## 17. Non-Equivalence Cautions

- Existing safe-metadata fixture suitability is not established by name alone.
- Safe-metadata runtime smoke is not artifact body generation correctness
  generally.
- Safe-metadata output surface is not free-form body safety.
- Count-only body metadata is not payload correctness.
- Safe-metadata pass is not manifest writer readiness.
- Safe-metadata pass is not production readiness.
- Safe-metadata pass is not real-data readiness.
- Safe-metadata pass is not model performance evidence.

## 18. Recommended Next Step

Recommended next step: Step546 safe-metadata fixture root/update design.

This keeps the next stage design-only and avoids moving directly from fixture
uncertainty into runtime implementation. If Step546 can establish that the
existing `valid/valid_safe_metadata_summary_bridge` case is sufficient without
fixture or validator changes, the following step can move to safe-metadata
runtime refinement design.

## 19. Failure Interpretation

Future safe-metadata fixture/update chain or runtime stage failure should be
interpreted within the safe-metadata runtime integration boundary. It may
indicate unsafe metadata marker, fixture mismatch, unsupported mode, missing
fixture, schema mismatch, or fail-closed safety scan.

Failure does not prove artifact body generation correctness generally, does
not prove manifest writer failure, does not prove model performance issue, and
does not prove production readiness issue. Raw stdout/stderr and payloads must
not be copied into docs or reports. Use public-safe reason codes only.

## 20. Non-Claims

This fixture/update design does not claim:

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

## 22. Step546 Safe-Metadata Fixture Root Update Design Status

Step546 adds the docs-only / planning-only safe-metadata fixture root/update
design:

`docs/frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_root_update_design.md`

It follows this design's Option B path by recommending a future small
metadata-only extension to the existing fixture root. Step546 does not create
or change fixture JSON, change validators, change runtime implementation,
change workflow files, change the release-quality wrapper, change Makefile,
change Python code/tests, invoke artifact body generation runtime, connect
manifest writer integration, write files, use real data, compute metrics, or
claim production readiness.

## 23. Step547 Safe-Metadata Fixture Root Update Implementation Status

Step547 adds planned safe-metadata v0.2 fixture cases outside the active
validator root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration_planned_safe_metadata_v0_2/`

This placement preserves the existing static validator and release-quality
wrapper behavior until a later validator update step. Step547 does not change
validators, runtime implementation, Makefile, release-quality wrapper,
workflow files, artifact body generation runtime invocation, manifest writer
integration, file writing, real-data use, metric use, or production readiness
status.
