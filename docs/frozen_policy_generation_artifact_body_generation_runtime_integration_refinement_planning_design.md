# Frozen Policy Generation Artifact Body Generation Runtime Integration Refinement Planning Design

## 1. Title

Frozen Policy Generation Artifact Body Generation Runtime Integration
Refinement Planning Design

## 2. Scope

This document is a design-only / planning-only planning design for moving from
the completed static artifact body generation integration fixture validator
chain toward a future artifact body generation runtime integration refinement
chain.

This step does not:

- change runtime implementation
- implement artifact body generation integration
- change fixture JSON
- change validators
- change the Makefile
- change the release-quality wrapper
- change workflow files
- implement manifest writer integration
- enable file writing
- prove production readiness, real-data readiness, or model performance

The future runtime refinement must remain synthetic-only, metadata-only,
no-oracle, body-free, summary-only, public-safe, and fail-closed.

## 3. Completed Upstream Chain Summary

- Step520 created the final safety review design for the artifact writer CLI
  actual invocation runtime chain.
- Step521 created the next-chain planning design for artifact body generation
  integration.
- Step522 created the fixture contract design for the bridge from actual
  invocation runtime summary metadata to artifact body generation boundary
  metadata.
- Step523 created the synthetic metadata-only fixture root.
- Step524 created the fixture validator design.
- Step525 implemented the static fixture validator module, CLI, and focused
  tests.
- Step526 created the standalone Makefile target design.
- Step527 implemented the standalone Makefile target.
- Step528 created the release-quality integration design.
- Step529 added the fixture validator target to the release-quality wrapper.
- Step530 created the remote/manual run record workflow design.
- Step531 created the public-safe remote status marker.

This upstream chain is static fixture validation plus release-quality wrapper
and remote status marker coverage. It does not implement a runtime bridge.

## 4. Current Baseline

- fixture root:
  `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration`
- validator module:
  `python/learner_state/frozen_policy_generation_artifact_body_generation_integration_fixture_validation.py`
- Makefile target:
  `check-learner-state-frozen-policy-generation-artifact-body-generation-integration-fixtures`
- release-quality label:
  `release_quality_check: learner-state frozen policy generation artifact body generation integration fixture validation`
- remote marker:
  `docs/status/learner_state_frozen_policy_generation_artifact_body_generation_integration_fixture_validator_release_quality_remote_run_status.md`
- aggregate counts: total 28, valid 6, invalid 22, JSON files 196, files per
  case 7
- mapped status counts: pass 6, usage_error 1, fail_closed 20, mismatch 1
- reason code counts: `none: 6` plus one count for each public-safe invalid
  reason code in the fixture validator output

Safety boundaries:

- synthetic-only
- metadata-only
- no-oracle
- body-free output
- no request / pointer / expected body
- no artifact body payload
- no manifest body
- no generated policy body
- no raw stdout/stderr body
- no raw rows
- no logits/probabilities
- no private or absolute path values
- no raw learner text
- no real participant data
- no performance metric body
- no file writing
- no manifest writer invocation
- public-safe reason codes only

Non-claims:

- no artifact body generation integration correctness claim
- no manifest writer integration correctness claim
- no artifact writer CLI actual invocation correctness claim generally
- no runtime actual invocation correctness claim generally
- no production readiness claim
- no real-data readiness claim
- no model performance claim

## 5. Runtime Refinement Goal

The next runtime refinement goal should be limited to organizing the
runtime-level handoff between selected synthetic metadata-only actual
invocation runtime summary metadata and the artifact body generation metadata
boundary.

The future runtime should:

- keep suppressed mode as the default
- treat safe-metadata mode as explicit
- avoid request, pointer, and expected body output
- avoid artifact body payload output
- avoid manifest body output
- avoid generated policy body output
- avoid file writing
- avoid manifest writer invocation
- emit public-safe summary output only
- fail closed on unsafe output

## 6. Candidate Runtime Integration Modes

### Mode A: Plan-Only Bridge

This mode checks consistency between actual invocation runtime summary metadata
and artifact body generation request/pointer metadata. It does not invoke the
artifact body generation runtime.

- safety: highest
- implementation risk: lowest
- fixture clarity: high, because it follows the existing static fixture shape
- validator compatibility: high
- release-quality stability: high
- next-step staging: best first step

### Mode B: Suppressed Artifact Body Generation Smoke

This mode invokes artifact body generation in suppressed mode from
metadata-only request/pointer metadata. It emits no artifact body payload,
writes no files, and invokes no manifest writer.

- safety: high if suppression and scans are enforced
- implementation risk: medium
- fixture clarity: medium, because runtime behavior is introduced
- validator compatibility: high if fields remain count/boolean-only
- release-quality stability: medium until the smoke is isolated
- next-step staging: suitable after Mode A

### Mode C: Safe-Metadata Artifact Body Generation Smoke

This mode permits only explicit safe-metadata behavior. It may emit count-only
summaries such as body field count or metadata field count, but it must not
emit payloads, write files, or invoke the manifest writer.

- safety: medium-high with strict count-only output
- implementation risk: medium-high
- fixture clarity: medium
- validator compatibility: requires explicit safe-metadata expectations
- release-quality stability: later-stage only
- next-step staging: suitable after Mode A and Mode B are stable

Recommended starting mode: Mode A, plan-only bridge. Mode B should be a later
suppressed smoke step. Mode C should remain explicit and staged separately.
Step532 does not implement any mode.

## 7. Proposed Runtime Inputs

Future runtime CLI inputs may include:

- `--fixture-root`
- `--fixture-case`
- `--mode plan-only | suppressed-smoke | safe-metadata-smoke`
- `--summary-only`
- `--no-file-writing`
- `--no-manifest-writer`
- `--fail-closed-on-unsafe-output`

Inputs should only reference metadata-only fixture cases. Docs must not copy
fixture JSON bodies.

## 8. Proposed Runtime Output Schema

Candidate schema:

`learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.1`

Output mode:

`artifact_body_generation_runtime_integration`

Expected public-safe fields:

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

The output schema should contain public-safe booleans, controlled labels,
counts, and reason codes only.

## 9. Candidate Fixture Selection For Runtime Smoke

Candidate cases:

- `valid/valid_minimal_suppressed_metadata_only_bridge`
- `valid/valid_safe_metadata_summary_bridge`
- `valid/valid_no_file_writing_bridge`

Comparison:

- `valid_minimal_suppressed_metadata_only_bridge` is best for the first smoke
  because it keeps the smallest suppressed metadata-only boundary.
- `valid_safe_metadata_summary_bridge` is best for a later explicit
  safe-metadata smoke because it exercises count-only safe metadata behavior.
- `valid_no_file_writing_bridge` is useful as a focused guard for the
  no-file-writing boundary but should not be the first runtime bridge smoke.

Recommended first smoke:

- `valid/valid_minimal_suppressed_metadata_only_bridge`

Recommended later explicit safe-metadata smoke:

- `valid/valid_safe_metadata_summary_bridge`

## 10. Safety Scan Strategy

Future runtime refinement should scan for:

- raw stdout/stderr body
- request body
- pointer body
- expected body
- artifact body payload
- manifest body
- generated policy body
- raw rows
- logits / probabilities
- private path values
- absolute path values
- raw learner text
- real participant data
- performance metric body
- file writing
- manifest writer invocation
- production readiness claim
- real-data readiness claim
- model performance claim

Runtime output must not echo unsafe values. It should emit public-safe reason
codes and suppression flags only.

## 11. Fail-Closed Behavior

Future runtime refinement should use these mappings:

- unsafe output detected -> `fail_closed`
- missing fixture -> `usage_error`
- unsupported mode -> `usage_error`
- schema mismatch -> `usage_error` or `fail_closed` according to the case
- unexpected file writing -> `fail_closed`
- unexpected manifest writer invocation -> `fail_closed`
- unsafe stdout/stderr -> `fail_closed`

Reason codes must be public-safe only. Raw output must be suppressed.

## 12. Focused Test Plan For Future Implementation

Future focused tests should cover:

- plan-only valid case pass
- suppressed smoke valid case pass
- safe-metadata explicit case pass
- unsupported mode usage_error
- missing fixture usage_error
- unsafe request body fail_closed
- unsafe pointer body fail_closed
- unsafe expected body fail_closed
- artifact body payload fail_closed
- manifest body fail_closed
- generated policy body fail_closed
- raw stdout body fail_closed
- raw stderr body fail_closed
- raw rows fail_closed
- logits fail_closed
- private path fail_closed
- absolute path fail_closed
- raw learner text fail_closed
- real data marker fail_closed
- file writing fail_closed
- manifest writer invocation fail_closed
- output is public-safe
- no file residue
- deterministic output

## 13. Release-Quality Staging Proposal

Suggested future staging:

1. Step533: runtime integration refinement design
2. Step534: runtime fixture/update design, if needed
3. Step535: runtime implementation
4. Step536: Makefile target design
5. Step537: Makefile target implementation
6. Step538: release-quality integration design
7. Step539: release-quality wrapper integration
8. Step540: remote/manual run record workflow design
9. Step541: remote status marker

Step532 does not perform these steps.

## 14. Relationship To Manifest Writer Chain

Manifest writer integration is out of scope for this refinement planning.

Requirements:

- manifest writer invocation must remain false
- manifest body must remain absent
- manifest file writing is out of scope
- future manifest writer handoff should be a separate design / fixture /
  validator / marker chain
- this runtime refinement must not be interpreted as manifest writer
  correctness

## 15. Failure Interpretation

Future runtime failure means the public-safe artifact body generation runtime
boundary failed for the selected synthetic metadata-only case.

Failure does not prove:

- model performance issue
- manifest writer issue
- production readiness issue
- artifact body generation integration correctness generally

Failures should be interpreted through public-safe reason codes only. Raw
stdout/stderr and payloads must not be copied into docs or reports.

## 16. Non-Claims

This planning design does not claim:

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

## 17. Step533 Runtime Refinement Design Status

Step533 adds the docs-only / planning-only runtime integration refinement
design:

`docs/frozen_policy_generation_artifact_body_generation_runtime_integration_refinement_design.md`

It concretizes the future plan-only bridge, proposed runtime module/CLI,
schema, selected fixture case, safety scan, reason codes, focused tests, and
staging. It does not change runtime implementation, implement artifact body
generation integration, change fixture JSON, change validators, change Python
code/tests, change Makefile, change the wrapper, change workflow files,
connect manifest writer integration, enable file writing, use real data,
compute metrics, or claim production readiness.

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
