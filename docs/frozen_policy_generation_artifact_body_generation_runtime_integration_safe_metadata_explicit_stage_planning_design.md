# Frozen Policy Generation Artifact Body Generation Runtime Integration Safe-Metadata Explicit Stage Planning Design

## 1. Scope

This document is the planning design for a future safe-metadata explicit stage
in artifact body generation runtime integration. It follows the Step543
broader final safety review recommendation to plan the safe-metadata stage
before any implementation.

This is design-only / planning-only. It does not change implementation,
release-quality wrapper, Makefile, workflow files, Python code/tests, fixture
JSON, validators, runtime implementation, artifact body generation runtime
invocation, manifest writer integration, or file writing. It does not prove
production readiness, real-data readiness, or model performance.

## 2. Prior Completed Chain Dependency

- Step532-Step534 planned and refined the initial runtime integration boundary
  and selected the existing fixture root for the first `plan-only-bridge`.
- Step535 implemented the selected-case `plan-only-bridge` runtime module,
  CLI, and focused tests.
- Step536-Step537 designed and implemented the standalone Makefile target.
- Step538-Step539 designed and added the release-quality wrapper check.
- Step540-Step541 designed and recorded the public-safe remote status marker.
- Step542 completed the `plan-only-bridge` final safety review.
- Step543 completed the broader final safety review through the manifest
  writer boundary and recommended safe-metadata explicit stage planning next.

The `plan-only-bridge` chain is complete through remote marker and final
safety review. The broader final safety review through the manifest writer
boundary is complete. A safe-metadata stage must not be implemented without
explicit planning.

## 3. Motivation for Safe-Metadata Explicit Stage

The current `plan-only-bridge` checks a selected synthetic metadata-only
handoff without invoking artifact body generation runtime. A safe-metadata
explicit stage may check a broader metadata surface than `plan-only-bridge`,
but that surface must remain public-safe and bounded.

The safe-metadata explicit stage must:

- remain bounded to public-safe metadata
- avoid exposing artifact body payload
- avoid implying free-form body safety
- avoid invoking manifest writer
- avoid file writing
- remain synthetic-only
- remain no-oracle
- remain fail-closed on unsafe output

## 4. Existing Candidate Fixture Assessment

Candidate fixture case:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration/valid/valid_safe_metadata_summary_bridge`

The existing Step523 fixture root already contains a candidate case named for a
safe-metadata summary bridge. It may be enough for planning a future explicit
safe-metadata runtime integration stage, but that must be verified in a later
fixture/update design step.

The existing fixture root uses a seven-file layout for the integration fixture
cases, including case metadata, actual invocation runtime summary metadata,
artifact body request metadata, artifact body pointer metadata, artifact body
generation metadata, expected integration summary, and expected error. This
candidate appears to represent a safe-metadata summary bridge, but exact field
coverage and sufficiency must be verified later without copying fixture JSON
body into docs.

Fixture update status for Step544:

- fixture update requirement: to be verified in a later fixture/update design
  step
- validator update requirement: to be verified in a later fixture/update
  design step
- fixture JSON changes in Step544: none

## 5. Candidate Runtime Mode Options

| Option | Safety | Naming clarity | Compatibility with reserved modes | Output surface risk | Testability | Release-quality staging clarity | Future marker clarity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Option A: implement `safe-metadata-smoke` in existing runtime module | Medium if preceded by fixture/update design | Good, already reserved | High | Medium | High | Clear | Clear |
| Option B: introduce `safe-metadata-explicit` as a new mode name | Medium | Highest | Medium, needs new naming policy | Medium | High | Clear but broader change | Clear |
| Option C: keep runtime integration `plan-only` only and use existing artifact body generation safe-metadata CLI smoke separately | High | Clear separation | High | Low | Medium | Existing staging only | Lower for runtime integration |
| Option D: design a separate fixture/validator chain before runtime mode implementation | Highest | Good after design | High | Lowest before implementation | High later | Highest | Highest |

Recommended path: Option D first, then consider Option A with fixture/update
design completed.

Option D is safest because it verifies fixture sufficiency, expected summary
fields, reason codes, and validator compatibility before any runtime mode is
implemented. Option A may be a good implementation path later because
`safe-metadata-smoke` is already a reserved mode, but it should not proceed
before a dedicated fixture/update design.

## 6. Proposed Safe-Metadata Output Surface

Allowed public-safe output candidates:

- schema / mode / status / reason_code
- selected case id
- integration mode
- safe metadata body status
- count-only body field count
- content_suppressed flag
- body_suppressed or safe-metadata-body-bounded flag
- no request body
- no pointer body
- no expected body
- no artifact body payload
- no manifest body
- no generated policy body
- no raw stdout/stderr body
- no raw rows
- no logits
- no private / absolute paths
- no raw learner text
- no real data marker
- no performance metric body
- file writing disabled
- manifest writer not invoked
- artifact file written false
- manifest file written false
- unsafe signal count

Forbidden output:

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

## 7. Safety Scan Requirements

Future safe-metadata explicit stage scans must detect:

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

The output must use public-safe reason codes only and must not echo unsafe
values.

## 8. Fail-Closed Behavior Planning

Planned status mapping:

- unsupported mode: `usage_error`
- missing fixture: `usage_error`
- missing required metadata file: `usage_error`
- unsafe body / payload / path / raw marker: `fail_closed`
- unexpected file writing: `fail_closed`
- unexpected manifest writer invocation: `fail_closed`
- unexpected artifact body payload availability: `fail_closed`
- mismatched expected status: `fail_closed` or `mismatch`, to be decided in
  fixture/update design

All unsafe values must be suppressed from output.

## 9. Fixture/Update Design Needs

The next design step should decide:

- whether `valid_safe_metadata_summary_bridge` is enough
- whether new invalid cases are needed for safe-metadata stage
- whether existing validator schema needs extension
- whether runtime fixture root should remain the same
- whether expected runtime summary needs new fields
- whether new reason codes are needed
- whether release-quality counts would change
- whether fixture README needs updates

Step544 makes no fixture JSON changes.

## 10. Runtime Implementation Staging

Suggested staged chain:

- Step545: safe-metadata fixture/update design
- Step546: safe-metadata runtime refinement design
- Step547: safe-metadata runtime implementation
- Step548: safe-metadata Makefile target design
- Step549: safe-metadata Makefile target implementation
- Step550: safe-metadata release-quality integration design
- Step551: safe-metadata release-quality wrapper integration
- Step552: safe-metadata remote/manual run record workflow design
- Step553: safe-metadata remote status marker
- Step554: safe-metadata final safety review

The exact numbering can change, but the stages should stay separate.

## 11. Relationship to Existing Artifact Body Generation Safe-Metadata CLI Smoke

The existing artifact body generation safe-metadata CLI smoke is a separate
check. Runtime integration safe-metadata explicit stage must not be confused
with that existing check.

- Existing CLI smoke may expose safe metadata body availability or count-only
  surface.
- Runtime integration stage should test the handoff boundary, not free-form
  artifact body content.
- Release-quality ordering should preserve static validation before runtime
  checks.
- No body payload should be copied into docs.

## 12. Relationship to Manifest Writer Chain

- Safe-metadata explicit stage must not invoke manifest writer.
- Manifest writer handoff planning should be separate.
- Manifest body generation remains out of scope.
- Manifest file writing remains out of scope.
- Safe-metadata stage must not imply manifest writer integration correctness.

## 13. Relationship to File-Writing Chains

- Safe-metadata explicit stage should keep file writing disabled.
- Artifact body file-writing validation remains separate.
- Manifest writer file-writing validation remains separate.
- Output path safety remains separate.
- File residue check should be required in implementation stages.

## 14. Non-Equivalence Cautions

- Safe-metadata stage is not artifact body generation correctness generally.
- Safe-metadata stage is not free-form body safety.
- Count-only body metadata is not payload correctness.
- Safe-metadata pass is not manifest writer readiness.
- Safe-metadata pass is not production readiness.
- Safe-metadata pass is not real-data readiness.
- Safe-metadata pass is not model performance evidence.

## 15. Recommended Next Step

Recommended next step: Step545 safe-metadata fixture/update design.

This is the safest next handoff because it avoids assuming that the existing
candidate case is sufficient. It should verify fixture sufficiency, reason
codes, expected summary fields, schema impact, validator impact, and count
impact before any runtime implementation.

## 16. Failure Interpretation

Future safe-metadata explicit stage failure should be interpreted within the
safe-metadata runtime integration boundary. It may indicate unsafe metadata
marker, fixture mismatch, unsupported mode, missing fixture, or fail-closed
safety scan.

Failure does not prove artifact body generation correctness generally, does
not prove manifest writer failure, does not prove model performance issue, and
does not prove production readiness issue. Raw stdout/stderr and payloads must
not be copied into docs or reports. Use public-safe reason codes only.

## 17. Non-Claims

This planning design does not claim:

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

## 18. Public-Safe Checklist

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

## 19. Step545 Safe-Metadata Fixture Update Design Status

Step545 adds the docs-only / planning-only safe-metadata fixture/update design:

`docs/frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_update_design.md`

It assesses whether the existing fixture root and
`valid/valid_safe_metadata_summary_bridge` are enough for a later
safe-metadata runtime integration stage. Step545 does not change fixture JSON,
validators, runtime implementation, workflow files, the release-quality
wrapper, Makefile, Python code/tests, artifact body generation runtime
invocation, manifest writer integration, file writing, real-data use, metric
use, or production readiness status.

## 20. Step546 Safe-Metadata Fixture Root Update Design Status

Step546 adds the docs-only / planning-only safe-metadata fixture root/update
design:

`docs/frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_root_update_design.md`

It does not create or change fixture JSON, change validators, change runtime
implementation, change workflow files, change the release-quality wrapper,
change Makefile, change Python code/tests, invoke artifact body generation
runtime, connect manifest writer integration, write files, use real data,
compute metrics, or claim production readiness.

## 21. Step547 Safe-Metadata Fixture Root Update Implementation Status

Step547 adds planned metadata-only / body-free safe-metadata v0.2 fixture cases
outside the active validator root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration_planned_safe_metadata_v0_2/`

Validator update and runtime implementation are not yet implemented. Existing
release-quality wrapper behavior remains unchanged.

## 22. Step548 Safe-Metadata v0.2 Fixture Validator Update Design Status

Step548 adds
`docs/frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_v0_2_fixture_validator_update_design.md`
as the next planning document for validating the Step547 planned root. It
recommends a separate future validator module and keeps runtime implementation
and all integration targets out of scope.

## 23. Step549 Safe-Metadata v0.2 Fixture Validator Implementation Status

Step549 implements the separate planned-root validator module and focused
tests. Safe-metadata runtime implementation remains unimplemented, and the
validator is not yet connected to release-quality. Step551 later adds a
standalone Makefile target for the validator.

## 24. Step550 Safe-Metadata v0.2 Fixture Validator Makefile Target Design Status

Step550 adds a design-only / planning-only standalone Makefile target design
for the Step549 validator CLI. Runtime implementation remains unimplemented.

## 25. Step551 Safe-Metadata v0.2 Fixture Validator Makefile Target Implementation Status

Step551 implements the standalone Makefile target for the Step549 planned-root
validator CLI. It does not implement `safe-metadata-smoke` runtime behavior,
invoke artifact body generation runtime, invoke manifest writer, or write
files.
