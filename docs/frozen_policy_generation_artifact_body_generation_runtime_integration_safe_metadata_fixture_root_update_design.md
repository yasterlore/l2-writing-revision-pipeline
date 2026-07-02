# Frozen Policy Generation Artifact Body Generation Runtime Integration Safe-Metadata Fixture Root Update Design

## 1. Scope

This document is the concrete fixture root/update design for a future
safe-metadata explicit stage in artifact body generation runtime integration.
It follows the Step545 safe-metadata fixture/update design and defines how a
future fixture update should be staged before validator or runtime
implementation.

This is design-only / planning-only. It does not create or change fixture
JSON, add a fixture root, change validators, change runtime implementation,
change Python code/tests, change Makefile, change the release-quality wrapper,
change workflow files, invoke artifact body generation runtime, implement
manifest writer integration, or perform file writing. It does not prove
production readiness, real-data readiness, or model performance.

## 2. Prior Completed Chain Dependency

- Step532-Step541 completed the `plan-only-bridge` runtime integration chain
  through implementation, Makefile target, release-quality integration, remote
  marker, and final safety review.
- Step543 completed the broader final safety review through the manifest
  writer boundary.
- Step544 completed safe-metadata explicit stage planning.
- Step545 completed safe-metadata fixture/update design and recommended that a
  small fixture metadata extension may be required before runtime
  implementation.

The `plan-only-bridge` chain is complete through remote marker and final
safety review. The broader final safety review through the manifest writer
boundary is complete. Safe-metadata explicit stage planning is complete.
Safe-metadata fixture/update design is complete. This Step546 document keeps
the next decision design-only.

## 3. Existing Fixture Root Reuse Decision

Existing fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration/`

| Option | Safety | Existing validator compatibility | Release-quality count stability | Schema clarity | Body/payload leakage risk | Test coverage | Future marker clarity | Docs burden |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Option A: extend the existing fixture root | High if fields stay metadata-only | Medium, validator update likely | Medium, counts may change | High with v0.2 fields | Low if body-free sentinels are enforced | High | High | Medium |
| Option B: create a new safe-metadata-specific fixture root | High but broader | Low initially | Low initially | High | Low if isolated | High | Medium | High |
| Option C: do not add fixtures; use `valid_safe_metadata_summary_bridge` as-is | Medium until field sufficiency is verified | High | High | Medium | Medium if output surface is ambiguous | Low to medium | Medium | Low |
| Option D: defer fixture update and only design runtime mode | High short-term | High | High | Low for fixture readiness | Low short-term | Low | Low | Low |

Recommended decision: Option A, extend the existing fixture root in a later
implementation step, with a small metadata-only v0.2 fixture extension.

Option A keeps continuity with the Step523 root and the existing validator
chain while allowing safe-metadata explicit runtime expectations to be stated
without relying on case name alone. It should be paired with validator update
design before implementation. Step546 does not perform the extension.

## 4. Proposed Fixture Update Strategy

Future fixture update strategy:

- Do not modify `valid/valid_safe_metadata_summary_bridge` unless the later
  implementation step explicitly decides that backward-compatible metadata-only
  field additions are safer than adding new cases.
- Prefer adding a new valid case:
  `valid/valid_safe_metadata_explicit_runtime_bridge`.
- Add targeted invalid cases for each unsafe safe-metadata output surface.
- Keep the existing seven-file layout.
- Add safe-metadata expected runtime fields to existing metadata files rather
  than adding body-bearing files.
- Introduce a safe-metadata fixture schema or expected runtime summary schema
  version only for the new safe-metadata cases.
- Expect aggregate counts to change if new cases are added.
- Treat validator update as required if new cases, schema fields, reason codes,
  or counts are introduced.

Step546 does not create or change fixture JSON.

## 5. Proposed Case Taxonomy

Minimum candidate valid cases:

- `valid/valid_safe_metadata_explicit_runtime_bridge`
- `valid/valid_safe_metadata_count_only_bridge`
- `valid/valid_safe_metadata_no_file_writing_bridge`
- `valid/valid_safe_metadata_no_manifest_writer_bridge`

Minimum candidate invalid cases:

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
- `invalid_safe_metadata_mismatched_expected_status`
- `invalid_safe_metadata_unsupported_schema`

All future cases must remain synthetic-only, metadata-only, body-free, and
no-oracle. Invalid cases should encode sentinel flags and public-safe reason
codes, not body content.

## 6. Proposed File Layout

Existing seven-file layout:

- `case_metadata.json`
- `actual_invocation_runtime_summary_metadata.json`
- `artifact_body_request_metadata.json`
- `artifact_body_pointer_metadata.json`
- `artifact_body_generation_metadata.json`
- `expected_integration_summary.json`
- `expected_error.json`

| Option | Safety | Validator compatibility | Schema clarity | File count stability | Docs burden |
| --- | --- | --- | --- | --- | --- |
| Keep seven-file layout and add safe-metadata fields to existing metadata files | High | Medium, validator update needed | High | High | Medium |
| Keep seven-file layout and add only new cases | Medium | Medium | Medium | High per case | Low |
| Introduce an eighth file, such as `safe_metadata_runtime_expectations.json` | Medium | Low until validator update | High | Low | Medium |
| Create a separate safe-metadata fixture root with a different layout | Medium | Low initially | High | Low | High |

Recommended layout: keep the seven-file layout and add safe-metadata fields to
existing metadata files for new safe-metadata cases. This preserves fixture
shape, keeps release-quality output count-only, and avoids a new body-like file
surface.

## 7. Proposed Schema/Version Plan

| Option | Backward compatibility | Validator clarity | Release-quality count stability | Runtime schema clarity | Public-safe marker clarity | Payload expansion risk |
| --- | --- | --- | --- | --- | --- | --- |
| Keep fixture schema v0.1 and add no new fields | High | Low for safe-metadata | High | Low | Low | Medium |
| Introduce fixture schema v0.2 for safe-metadata explicit cases | Medium | High | Medium | High | High | Low |
| Introduce runtime expected summary schema v0.2 only | Medium | Medium | Medium | High | High | Low |
| Separate safe-metadata fixture schema family | Low | High | Low | High | Medium | Low |

Recommended schema plan: introduce fixture schema v0.2 for the new
safe-metadata explicit cases, and align it with a future runtime expected
summary v0.2 if runtime output needs new fields. Keep existing v0.1 cases
unchanged.

This recommendation prioritizes schema clarity and public-safe marker clarity
while avoiding accidental body/payload expansion.

## 8. Required Metadata Fields

Future fixture update should cover these metadata categories:

- `safe_metadata_explicit_stage_requested`
- `safe_metadata_output_surface`
- `safe_metadata_body_available`
- `safe_metadata_body_status`
- `safe_metadata_body_field_count`
- `safe_metadata_body_payload_suppressed`
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
- `file_writing_detected`
- `manifest_writer_requested`
- `manifest_writer_invoked`
- `artifact_file_written`
- `manifest_file_written`
- `unsafe_signal_count`
- `expected_runtime_status`
- `expected_runtime_reason_code`

Field names can be refined later. The categories must remain body-free and
must not include actual body content fields.

## 9. Expected Aggregate Count Impact

Current aggregate:

- total cases: 28
- valid cases: 6
- invalid cases: 22
- total JSON files: 196
- JSON files per case: 7

Proposed future count impact if the taxonomy in this design is implemented:

- add 4 valid cases
- add 20 invalid cases
- new total cases: 52
- new valid cases: 10
- new invalid cases: 42
- if seven files per case are preserved, new total JSON files: 364

These are design proposal counts only. Step546 does not change fixture counts
or fixture JSON.

## 10. Validator Update Implications

- If new cases or schema v0.2 are added, validator update is required.
- The validator must enforce body-free / metadata-only / no-oracle fields.
- The validator must count safe-metadata cases separately.
- The validator must expose public-safe aggregate counts only.
- The validator must not print fixture JSON bodies.
- The validator must reject payload/body/raw/path/performance markers.
- Validator update should be separate design and implementation steps.
- The release-quality wrapper should remain unchanged until the validator
  target passes standalone.

## 11. Runtime Schema Implications

| Option | Safety | Backward compatibility | Public-safe marker clarity | Runtime output clarity | Docs burden |
| --- | --- | --- | --- | --- | --- |
| Keep runtime v0.1 and use mode-specific fields | Medium | High | Medium | Medium | Low |
| Introduce runtime v0.2 for safe-metadata explicit stage | High | Medium | High | High | Medium |
| Separate safe-metadata runtime integration schema | High | Low to medium | High | High | High |

Recommended runtime schema path: introduce runtime v0.2 for safe-metadata
explicit stage if the future runtime emits fields such as
`safe_metadata_body_available`, `safe_metadata_body_status`, or
`safe_metadata_body_field_count`. This follows the Step545 v0.2 direction and
keeps marker interpretation clearer.

## 12. Runtime Mode Naming

| Mode | Compatibility | Clarity | Recommendation |
| --- | --- | --- | --- |
| `safe-metadata-smoke` | High, already reserved | Good | Preferred future implementation mode |
| `safe-metadata-explicit` | Medium | Highest | Useful as prose, but new mode name adds policy surface |
| `safe-metadata-bridge` | Medium | Good | Secondary option if bridge naming becomes standard |

Recommended mode name: `safe-metadata-smoke`, preserving the existing reserved
mode. Use "safe-metadata explicit stage" as the planning/staging phrase.

## 13. Future Implementation Staging

Recommended path because fixture update is expected:

- Step547: safe-metadata fixture root/update implementation
- Step548: safe-metadata validator update design
- Step549: safe-metadata validator update implementation
- Step550: safe-metadata runtime refinement design
- Step551: safe-metadata runtime implementation
- Step552: safe-metadata Makefile target design
- Step553: safe-metadata Makefile target implementation
- Step554: safe-metadata release-quality integration design
- Step555: safe-metadata release-quality wrapper integration
- Step556: safe-metadata remote/manual run record workflow design
- Step557: safe-metadata remote status marker
- Step558: safe-metadata final safety review

If a later no-change review establishes that no fixture update is required,
the chain can move directly to safe-metadata runtime refinement design instead.

## 14. Relationship to Existing Safe-Metadata CLI Smoke

- Existing artifact body generation safe-metadata CLI smoke remains separate.
- Safe-metadata fixture root/update is for the runtime integration handoff
  boundary.
- Existing CLI smoke should not be treated as runtime integration proof.
- Safe-metadata runtime integration must not be confused with free-form body
  generation.
- Body payloads must remain absent from docs.

## 15. Relationship to Manifest Writer and File-Writing Chains

- Safe-metadata fixture update must not include manifest writer invocation.
- Manifest body remains out of scope.
- Generated manifest files remain out of scope.
- Artifact body file-writing remains separate.
- Output path safety remains separate.
- File-writing guards should be represented as metadata-only invalid or guard
  cases if needed.

## 16. Failure Interpretation

Future safe-metadata fixture update or validator update failure should be
interpreted within the fixture/validator boundary. It may indicate schema
mismatch, missing metadata, unsafe marker, count mismatch, or unsupported
output surface.

Failure does not prove artifact body generation correctness generally, does
not prove manifest writer failure, does not prove model performance issue, and
does not prove production readiness issue. Use public-safe reason codes only.
Raw stdout/stderr and payloads must not be copied into docs or reports.

## 17. Non-Equivalence Cautions

- Fixture name alone does not establish suitability.
- Fixture update pass does not prove runtime correctness generally.
- Validator pass does not prove artifact body generation correctness
  generally.
- Safe-metadata metadata surface is not artifact body payload correctness.
- Count-only body metadata is not free-form body safety.
- Safe-metadata fixture validity is not manifest writer readiness.
- Release-quality inclusion is not production readiness.
- Synthetic-only pass is not real-data readiness.

## 18. Recommended Next Step

Recommended next step: Step547 safe-metadata fixture root/update
implementation.

Before Step547 implementation, the implementer should confirm that the exact
case taxonomy, field categories, expected counts, and v0.2 schema boundary in
this design are still the intended target. If those details no longer fit the
implementation context, insert another design step instead of creating fixture
JSON.

## 19. Non-Claims

This fixture root/update design does not claim:

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

## 21. Step547 Safe-Metadata Fixture Root Update Implementation Status

Step547 adds the planned safe-metadata v0.2 fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration_planned_safe_metadata_v0_2/`

The planned root contains 4 valid and 20 invalid metadata-only / body-free
cases using the seven-file layout. It is outside the active validator root
because the existing validator enforces fixed active counts and rejects extra
root-level directories. Validator update, runtime implementation, Makefile
target, release-quality wrapper integration, workflow update, artifact body
generation runtime invocation, manifest writer integration, and file writing
remain future work.

## 22. Step548 Safe-Metadata v0.2 Fixture Validator Update Design Status

Step548 adds
`docs/frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_v0_2_fixture_validator_update_design.md`
as a design-only / planning-only validator update design for the planned root.
It recommends a separate future validator module and does not implement
validator changes, runtime changes, fixture JSON changes, Makefile targets,
release-quality wrapper integration, workflow changes, artifact body generation
runtime invocation, manifest writer integration, or file writing.

## 23. Step549 Safe-Metadata v0.2 Fixture Validator Implementation Status

Step549 implements the separate validator module and focused tests for the
planned root. The validator checks 24 cases / 168 JSON files with public-safe
aggregate output. Makefile target, release-quality wrapper integration,
workflow update, runtime implementation, artifact body generation runtime
invocation, manifest writer integration, and file writing remain future work.

## 24. Step550 Safe-Metadata v0.2 Fixture Validator Makefile Target Design Status

Step550 adds a design-only / planning-only standalone Makefile target design
for the Step549 validator CLI. It does not change Makefile, release-quality
wrapper, workflow files, Python code/tests, fixture JSON, validator
implementation, runtime implementation, artifact body generation runtime
invocation, manifest writer integration, or file writing.

## 25. Step551 Safe-Metadata v0.2 Fixture Validator Makefile Target Implementation Status

Step551 implements the standalone Makefile target
`check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-fixtures`
for the Step549 validator CLI. The planned fixture root remains separate from
the active root, and release-quality wrapper integration remains future work.

## 26. Step552 Release-Quality Integration Design Status

Step552 adds a design-only / planning-only release-quality integration design
for the Step551 standalone target. The planned fixture root remains separate
from the active root.

## 27. Step553 Release-Quality Wrapper Integration Status

Step553 adds the planned-root validator target to the release-quality wrapper.
The planned fixture root remains separate from the active root.

## 23. Step554 Remote Run Record Workflow Design Status

Step554 adds the docs-only public-safe remote/manual run record workflow design
for the Step553 wrapper check:

`docs/frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_v0_2_fixture_validator_release_quality_remote_run_record_workflow.md`

It proposes future metadata-only/body-free status marker fields and does not
create a marker, change workflow, wrapper, Makefile, Python code/tests,
fixture JSON, validator/runtime implementation, artifact body generation
runtime invocation, manifest writer integration, or file writing.

## 24. Step555 Remote Status Marker Status

Step555 adds the public-safe pass-only metadata-only body-free remote status
marker for the Step553 wrapper check:

`docs/status/learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_v0_2_fixture_validator_release_quality_remote_run_status.md`

It stores no raw logs, full job output, payload bodies, real data, metric
evidence, production readiness evidence, real-data readiness evidence, model
performance evidence, runtime correctness evidence generally, artifact body
generation correctness evidence generally, safe-metadata free-form body safety
evidence, or manifest writer readiness evidence.
