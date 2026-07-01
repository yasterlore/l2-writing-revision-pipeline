# Frozen Policy Generation Artifact Body Generation Runtime Integration Fixture Update Design

## 1. Title

Frozen Policy Generation Artifact Body Generation Runtime Integration Fixture
Update Design

## 2. Scope

This document is a design-only / planning-only fixture/update decision for the
future artifact body generation runtime integration refinement described in
Step533.

This step does not:

- change fixture JSON
- add a fixture root
- change validators
- change runtime implementation
- change Python code/tests
- change the Makefile
- change the release-quality wrapper
- change workflow files
- implement artifact body generation integration
- implement manifest writer integration
- enable file writing
- prove production readiness, real-data readiness, or model performance

The decision remains synthetic-only, metadata-only, no-oracle, body-free,
summary-only, public-safe, and fail-closed.

## 3. Prior Chain Dependency

- Step520 completed the artifact writer CLI actual invocation runtime chain
  final safety review design.
- Step521 planned the artifact body generation integration next chain.
- Step522 designed the fixture contract.
- Step523 created the artifact body generation integration fixture root.
- Step524 designed the fixture validator.
- Step525 implemented the static fixture validator.
- Step526 designed the standalone Makefile target.
- Step527 implemented the standalone Makefile target.
- Step528 designed release-quality inclusion.
- Step529 added the fixture validator check to the release-quality wrapper.
- Step530 designed public-safe remote/manual run recording.
- Step531 added the public-safe remote status marker.
- Step532 planned runtime integration refinement.
- Step533 refined the future runtime design and selected `plan-only-bridge` as
  the initial mode.

The static fixture validator chain is complete, the fixture root exists and is
release-quality checked, the runtime refinement design exists, and runtime
implementation has not been done.

## 4. Existing Fixture Root Assessment

Existing fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration/`

The Step523 fixture root contains:

- total cases: 28
- valid cases: 6
- invalid cases: 22
- JSON files per case: 7
- total JSON files: 196
- selected candidate:
  `valid/valid_minimal_suppressed_metadata_only_bridge`

The 7-file layout already includes:

- `case_metadata.json`
- `actual_invocation_runtime_summary_metadata.json`
- `artifact_body_request_metadata.json`
- `artifact_body_pointer_metadata.json`
- `artifact_body_generation_metadata.json`
- `expected_integration_summary.json`
- `expected_error.json`

For the Step533 initial plan-only bridge, the existing root provides runtime
summary metadata, request metadata, pointer metadata, generation metadata,
expected integration summary, and expected error metadata. The Step525 static
validator covers the aggregate fixture root, and Step529 includes that
validator in release-quality.

## 5. Fixture Update Decision

Decision: Option A, no fixture update required for the initial
`plan-only-bridge`.

Comparison:

- safety: Option A is safest because it adds no new fixture JSON and no new
  fixture root surface.
- implementation risk: Option A keeps Step535 focused on selected-case loading
  and public-safe summary generation.
- compatibility with Step523 fixture root: Option A reuses the existing
  7-file metadata-only layout.
- compatibility with Step525 validator: Option A leaves validator schemas,
  counts, and reason-code expectations unchanged.
- release-quality stability: Option A preserves the existing release-quality
  fixture validator check.
- future suppressed-smoke / safe-metadata-smoke expansion: Option A does not
  block future fixture expansion, but defers it to a separate chain.

Recommended path:

- Step535 can implement runtime using the existing fixture root.
- No fixture JSON changes are needed.
- No validator changes are needed.
- Runtime should use the selected case only.
- Broader runtime cases can be a future separate chain.

Options B and C are not recommended before the initial plan-only bridge. If a
future mode requires new metadata, a separate fixture design or fixture root
update should happen before implementation of that later mode.

## 6. Selected Fixture Case For Initial Runtime

Selected case:

`valid/valid_minimal_suppressed_metadata_only_bridge`

Reasons:

- it represents a suppressed metadata-only boundary
- it has no file-writing boundary expansion
- it has no manifest writer boundary expansion
- it has no payload output boundary expansion
- it is the safest initial plan-only bridge
- it is consistent with validator expectations
- it keeps the runtime surface minimal

## 7. Cases Reserved For Later Runtime Stages

Reserved cases:

- `valid/valid_safe_metadata_summary_bridge` for a later explicit
  safe-metadata stage
- `valid/valid_no_file_writing_bridge` for a later file-writing guard smoke
- `valid/valid_no_manifest_writer_bridge` for a later manifest-writer guard
  smoke

Step534 does not proceed to those stages.

## 8. Runtime Metadata Fields Needed From Existing Fixture

Step535 can read these existing metadata fields:

- case metadata: expected status and expected reason code
- actual invocation runtime summary: status, invocation mode, suppression
  flags, and body-free flags
- artifact body request metadata: summary-only, no-file-writing,
  no-manifest-writer, and no-payload-output flags
- artifact body pointer metadata: no body, no path, and no raw marker flags
- generation metadata: generation mode, body status, artifact file written,
  manifest file written, and payload flags
- expected integration summary: status and reason code
- expected error: expected status, expected reason code, and no-payload-in-error
  flag

Docs and runtime output must not copy fixture JSON bodies.

## 9. Runtime Should Not Duplicate Full Static Validator

The static validator remains the aggregate fixture-root validator. The future
runtime should:

- check the selected case boundary only
- reuse strict selected-case safety checks
- avoid re-counting all 28 cases
- avoid replacing the fixture validator
- avoid modifying fixtures

This keeps the runtime refinement focused on the selected metadata-only
runtime boundary.

## 10. Safety Implications Of No Fixture Update

Option A safety implications:

- fewer moving parts
- no new JSON body risk
- existing validator and release-quality coverage remain stable
- runtime implementation can focus on selected-case loading and public-safe
  summary output
- later mode expansion can add fixtures separately if needed

The no-update decision reduces the chance of introducing fixture body,
payload, path, or raw text leakage.

## 11. Future Fixture Expansion Policy

Future expansion for suppressed-smoke, safe-metadata-smoke, file-writing
guard, or manifest-writer guard should use a separate chain if new metadata is
needed.

Future expansion should include:

- separate fixture update design
- separate fixture root update or extension
- validator update if schemas or counts change
- Makefile, wrapper, and remote marker staging if new targets are added
- no raw payloads
- no manifest body
- no file writing unless a separate file-writing chain explicitly scopes it

## 12. Candidate Step535 Implementation Boundary

If Step535 proceeds, the implementation boundary should be:

- create runtime module
- create focused tests
- implement `plan-only-bridge` only
- use the existing fixture root
- use selected case:
  `valid/valid_minimal_suppressed_metadata_only_bridge`
- do not invoke artifact body generation runtime
- do not invoke manifest writer
- do not write files
- emit public-safe CLI output only
- update full technical specification docs because Step535 would be an
  implementation step
- do not add a Makefile target until a separate later step

## 13. Failure Interpretation

If the future runtime proceeds without fixture updates:

- missing selected case means `usage_error`
- missing required metadata file means `usage_error`
- unsafe metadata means `fail_closed`
- unsupported mode means `usage_error`
- unexpected expected status means `fail_closed` according to the Step533
  selected-case design
- failure does not prove artifact body generation integration correctness
  generally
- failure does not prove a manifest writer issue
- failure does not prove a production readiness issue
- raw stdout/stderr and payloads must not be copied into docs or reports

## 14. Non-Claims

This fixture/update design does not claim:

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
- fixture update performed
- runtime implementation performed

## 15. Public-Safe Checklist

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
