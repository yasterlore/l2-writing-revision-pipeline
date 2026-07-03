# Frozen Policy Generation Artifact Body Generation Runtime Invocation Fixture Contract Design

## 1. Scope

This document is the fixture contract design for a future artifact body
generation runtime invocation boundary.

This is design-only / planning-only / docs-only. It does not create fixture
JSON, implement a validator, change runtime implementation, implement actual
artifact body generation runtime invocation, change workflows, change the
release-quality wrapper, change Makefile, change Python code/tests, implement
manifest writer integration, or write files. It is not evidence of production
readiness, real-data readiness, or model performance.

## 2. Prior Chain Dependency

The prior chain dependency is:

- The safe-metadata runtime chain Step557-Step567 is complete.
- The Step568 broader final safety review is complete.
- `safe-metadata-smoke` remains metadata handoff only.
- Artifact body generation safe-metadata CLI smoke remains separate.
- Manifest writer boundary remains separate.
- Actual artifact body generation runtime invocation is not implemented.
- Future work should start with fixture contract design before implementation.

## 3. Design Goal

The fixture contract should:

- define a safe fixture root for future runtime invocation
- define case taxonomy before code implementation
- define expected public-safe runtime output
- define failure mapping
- define temporary mutation testing strategy for future validator/runtime tests
- preserve metadata-only / body-free / count-only where applicable
- keep artifact body payload suppressed
- keep manifest writer not invoked
- keep file writing disabled
- prevent no-oracle leakage
- avoid production readiness, real-data readiness, and model performance claims

## 4. Proposed Fixture Root

Proposed future fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation/`

Step569 does not create this root. The root should remain separate from the
active artifact body generation integration fixture root and the planned
safe-metadata v0.2 fixture root until a later fixture root creation step
explicitly creates and validates it.

## 5. Proposed Fixture Layout

Recommended layout: 7 metadata-only JSON files per case.

- `case_metadata.json`
- `safe_metadata_runtime_summary_metadata.json`
- `artifact_body_request_metadata.json`
- `artifact_body_pointer_metadata.json`
- `artifact_body_generation_invocation_metadata.json`
- `expected_runtime_invocation_summary.json`
- `expected_error.json`

Alternative layout: 8 files per case, adding
`artifact_body_runtime_safety_scan_metadata.json`.

Design decision: prefer the 7-file layout for the first fixture root because it
matches the existing compact fixture pattern and keeps the initial contract
easy to validate. If future runtime invocation needs a larger safety-scan
surface, the 8-file layout can be introduced in a later schema version.

The files must not contain raw request body, pointer body, expected body,
artifact body payload, manifest body, generated policy body, raw stdout/stderr
body, raw rows, logits/probabilities, private or absolute path values, raw
learner text, real participant data, or performance metric body.

## 6. Proposed Case Taxonomy

### Valid Cases

Proposed valid cases:

- `valid_minimal_safe_metadata_runtime_invocation`
- `valid_safe_metadata_count_only_runtime_invocation`
- `valid_invocation_no_manifest_writer`
- `valid_invocation_no_file_writing`
- `valid_invocation_body_payload_suppressed`
- `valid_invocation_artifact_body_available_count_only`

### Invalid Cases

Proposed invalid cases:

- `invalid_invocation_request_body_present`
- `invalid_invocation_pointer_body_present`
- `invalid_invocation_expected_body_present`
- `invalid_invocation_artifact_body_payload_present`
- `invalid_invocation_manifest_body_present`
- `invalid_invocation_generated_policy_body_present`
- `invalid_invocation_raw_stdout_body_present`
- `invalid_invocation_raw_stderr_body_present`
- `invalid_invocation_raw_rows_present`
- `invalid_invocation_logits_present`
- `invalid_invocation_probabilities_present`
- `invalid_invocation_private_path_present`
- `invalid_invocation_absolute_path_present`
- `invalid_invocation_raw_learner_text_present`
- `invalid_invocation_real_data_marker_present`
- `invalid_invocation_performance_metric_body_present`
- `invalid_invocation_file_writing_requested`
- `invalid_invocation_manifest_writer_requested`
- `invalid_invocation_unsafe_artifact_body_runtime_mode`
- `invalid_invocation_unsupported_schema`
- `invalid_invocation_mismatched_expected_status`
- `invalid_invocation_no_oracle_forbidden_field`
- `invalid_invocation_unsafe_output_residue_risk`
- `invalid_invocation_active_root_merge_attempted`

Proposed aggregate:

- valid cases: 6
- invalid cases: 24
- total cases: 30
- JSON files per case: 7
- total JSON files: 210

This count is a proposal only. Step569 does not create fixture JSON.

## 7. Proposed Schemas and Modes

Candidate schema and mode names:

- fixture schema:
  `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_v0.1`
- validation schema:
  `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation_v0.1`
- runtime schema:
  `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.3`
- integration mode:
  `artifact-body-runtime-invocation`

Mode/module options:

- Option A: reuse the existing runtime module with new mode
  `artifact-body-runtime-invocation`.
- Option B: create a new runtime module dedicated to artifact body generation
  runtime invocation.
- Option C: extend `safe-metadata-smoke` only with an explicit invocation flag.

Recommendation: prefer Option A if the runtime module can keep a clear
mode-specific branch and fail-closed output policy. Prefer Option B if adding
invocation behavior would make the existing module ambiguous. Do not use
Option C for the first invocation boundary because it blurs the distinction
between metadata handoff and future runtime invocation.

## 8. Expected Future Runtime Behavior

The future runtime invocation boundary should:

- read fixture metadata only
- invoke artifact body generation runtime only in a controlled future
  implementation
- keep artifact body payload suppressed in public output
- record safe metadata body availability as a boolean
- record safe metadata body field count as count-only
- keep manifest writer not invoked
- keep file writing disabled
- suppress raw stdout/stderr body
- fail closed on unsafe signals
- map missing / unsupported metadata to `usage_error`
- map expected mismatch to `mismatch`
- avoid production readiness, real-data readiness, and model performance
  claims

## 9. Expected Public-Safe Output

Future runtime invocation smoke output may include:

- mode
- runtime_schema_version
- status
- reason_code
- exit_code_category
- case_id
- integration_mode
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
- metadata_file_count
- unsafe_signal_count

It must not include artifact body payload body.

## 10. Failure Mapping

### Pass

- valid metadata-only runtime invocation case
- no unsafe marker
- no raw body output
- no manifest writer
- no file writing
- no no-oracle violation
- expected status `pass` / reason `none`

### Usage Error

- missing fixture root
- missing case
- missing required metadata file
- malformed JSON
- unsupported schema
- unsupported mode
- missing required metadata
- invalid fixture/runtime mode mismatch

### Fail Closed

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
- file writing requested
- manifest writer requested
- unsafe output residue risk
- no-oracle forbidden field

### Mismatch

- expected status mismatch
- expected reason mismatch
- expected field mismatch

## 11. Relationship to Existing Boundaries

- Relation to `safe-metadata-smoke`: future invocation is not a replacement;
  `safe-metadata-smoke` remains metadata handoff only.
- Relation to artifact body generation safe-metadata CLI smoke: CLI smoke
  remains separate and is not equivalent to runtime integration.
- Relation to artifact body fixture validation: fixture validation remains
  static contract validation.
- Relation to artifact body file-writing checks: file-writing remains a
  separate boundary.
- Relation to manifest writer runtime smoke: manifest writer remains separate
  and not invoked by this future fixture contract.
- Relation to manifest writer file-writing checks: those checks remain separate
  synthetic / metadata-only file-writing boundaries where applicable.
- Relation to active root and planned root: the proposed invocation root should
  start separate from both.
- Relation to release-quality wrapper: any wrapper integration should happen
  only after fixture root, validator, target, and runtime behavior are designed
  and verified in separate steps.

This future invocation fixture contract does not replace existing checks.

## 12. Future Staging

Suggested staging:

- Step570: artifact body generation runtime invocation fixture root creation
- Step571: fixture validator design
- Step572: fixture validator implementation
- Step573: Makefile target design
- Step574: standalone Makefile target implementation
- Step575: runtime invocation implementation design
- Step576: runtime invocation implementation
- Step577: release-quality integration design
- Step578: release-quality wrapper integration
- Step579: remote/manual run record workflow design
- Step580: remote status marker
- Step581: final safety review

Runtime invocation implementation should happen only after fixture root,
validator, and target contracts are established.

## 13. Recommended Next Step

Recommended next step: Step570 artifact body generation runtime invocation
fixture root creation.

Reason: the proposed 7-file layout is specific enough to create a
metadata-only root in a later step, while validator and runtime implementation
can remain separate follow-on work. If future reviewers find the 7-file layout
insufficient before creation, Step570 can be narrowed to fixture layout
refinement design instead.

Step570 follow-up status: the planned fixture root has been created at
`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation/`
with 6 valid cases, 24 invalid cases, and 210 metadata-only / body-free JSON
files. The root remains a planned fixture contract surface only; validator
implementation, runtime implementation, Makefile target integration,
release-quality wrapper integration, artifact body generation runtime
invocation, manifest writer integration, and file writing remain separate
future steps.

Step571 follow-up status: the fixture validator design is available at
`docs/frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validator_design.md`.
It designs the future validator module, CLI, validation schema, aggregate
output, checks, reason mapping, and test plan without implementing the
validator or changing fixture JSON.

Step572 follow-up status: the fixture validator is implemented at
`python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation.py`
with focused tests. It validates the Step570 root without changing fixture
JSON, invoking runtime code, invoking manifest writer code, or writing files.

Step573 follow-up status: the future Makefile target design is available at
`docs/frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validator_makefile_target_design.md`.
It does not add the target.

## 14. Non-Equivalence Cautions

- Fixture contract design is not runtime invocation implementation.
- Future runtime invocation fixture pass is not runtime correctness generally.
- Artifact body generation safe-metadata CLI smoke is not equivalent to runtime
  integration.
- Count-only metadata is not artifact body payload correctness.
- Manifest writer runtime smoke is not production manifest readiness.
- File-writing smoke is not production readiness.
- Release-quality success is not production readiness.
- Synthetic-only pass is not real-data readiness.
- Fixture contract design is not production approval.

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
