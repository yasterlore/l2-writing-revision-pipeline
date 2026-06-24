# Frozen Policy Generation Artifact Body Fixture Design

This document designs future fixtures for frozen policy generation artifact
body generation. It is docs-only. It does not create fixture JSON, implement a
validator, implement artifact body generation, write files, evaluate
performance, use real data, or claim real-data or production readiness.

## 1. Purpose

The purpose of this document is to define the fixture root, case layout,
valid and invalid cases, safe expected-result contract, safe marker policy,
forbidden marker scan, and future validator staging for artifact body
generation.

This is not:

- fixture creation
- artifact body generation implementation
- validator implementation
- artifact file writing
- manifest file writing
- performance evaluation
- real-data readiness
- production readiness

## 2. Current State

- The artifact body generation design exists.
- Artifact body fixtures do not exist.
- Artifact body validator does not exist.
- Artifact body generation implementation does not exist.
- Manifest body generation does not exist.
- Artifact file writing does not exist.
- Manifest file writing does not exist.

## 3. Proposed Fixture Root

Recommended fixture root:

```text
tests/fixtures/learner_state_frozen_policy_generation_artifact_body/
```

Reasons:

- It keeps artifact body fixtures separate from artifact writer fixtures.
- It gives artifact body generation its own fixture contract.
- It makes a future validator target easier to name and scope.
- It matches the learner-state / frozen policy generation namespace.

The root should be synthetic-only and should contain no real participant data.

## 4. Proposed Case File Layout

Each future case should contain:

- `artifact_body_request.json`
- `artifact_writer_result_pointer.json`
- `expected_artifact_body_result.json`

These files are described at key level only here. This document does not
include JSON body examples.

### artifact_body_request.json

Key-level purpose:

- identifies the requested body mode
- identifies safe artifact metadata inputs
- carries synthetic/no-oracle notices
- declares requested schema version
- declares whether body output should remain suppressed or safe metadata-only

### artifact_writer_result_pointer.json

Key-level purpose:

- points to a synthetic artifact writer result fixture or safe metadata result
- identifies safe artifact_id and manifest_id labels
- carries no request body, pointer body, expected result body, artifact body,
  manifest body, raw rows, logits, private paths, or raw learner text

### expected_artifact_body_result.json

Key-level purpose:

- records expected status and reason codes
- records expected body_status
- records expected safety flags and count summaries
- records expected safe marker booleans for invalid cases
- records no raw payload bodies

## 5. Schema Version Candidates

Proposed schema names:

- `learner_state_frozen_policy_generation_artifact_body_request_v0.1`
- `learner_state_frozen_policy_generation_artifact_body_writer_result_pointer_v0.1`
- `learner_state_frozen_policy_generation_artifact_body_expected_result_v0.1`
- `learner_state_frozen_policy_generation_artifact_body_result_v0.1`

Future validators should reject unknown schema versions with a safe
fail-closed result.

## 6. Valid Cases

Proposed valid cases:

### minimal_suppressed_metadata_only_body

Purpose:

- proves the default body-suppressed path remains valid
- keeps artifact body unavailable
- verifies safe metadata-only result fields

Expected key-level result:

- body_status: `suppressed_metadata_only`
- validation_status or writer_status: pass
- reason_codes: none
- failed_checks: none
- all safety flags true
- body/raw/logit/private/performance counts are zero

### safe_metadata_body_summary

Purpose:

- proves a future safe metadata body can be represented without raw payloads
- limits body sections to safe labels, flags, counts, and notices

Expected key-level result:

- body_status: `generated_safe_metadata_body`
- safe metadata body allowed
- synthetic-only and no-oracle notices present
- all forbidden payload counts are zero
- no artifact file or manifest file writing

### safe_reason_code_body_summary

Purpose:

- proves safe reason code summaries can be represented without payloads
- keeps invalid-reason vocabulary metadata-only

Expected key-level result:

- body_status: `generated_safe_metadata_body`
- reason code summary present at label/count level
- no failed check payload bodies
- all safety flags true

### safe_validation_reference_body_summary

Purpose:

- proves validation reference IDs can be represented safely
- confirms references are labels only, not embedded source bodies

Expected key-level result:

- body_status: `generated_safe_metadata_body`
- validation reference IDs present as safe labels
- validation_reference_count is explicit
- no referenced body content is emitted

## 7. Invalid Cases

Proposed invalid cases and expected reason codes:

- `raw_learner_text_in_artifact_body`
  - reason_code: `raw_learner_text_in_artifact_body`
  - failed_check: raw learner text marker scan
- `raw_rows_in_artifact_body`
  - reason_code: `raw_rows_in_artifact_body`
  - failed_check: raw rows marker scan
- `logits_dump_in_artifact_body`
  - reason_code: `logits_dump_in_artifact_body`
  - failed_check: logits marker scan
- `private_path_in_artifact_body`
  - reason_code: `private_path_in_artifact_body`
  - failed_check: private path marker scan
- `performance_claim_in_artifact_body`
  - reason_code: `performance_claim_in_artifact_body`
  - failed_check: performance claim marker scan
- `request_body_leakage`
  - reason_code: `request_body_leakage`
  - failed_check: request body marker scan
- `pointer_body_leakage`
  - reason_code: `pointer_body_leakage`
  - failed_check: pointer body marker scan
- `expected_result_body_leakage`
  - reason_code: `expected_result_body_leakage`
  - failed_check: expected result body marker scan
- `generated_policy_body_leakage`
  - reason_code: `generated_policy_body_leakage`
  - failed_check: generated policy body marker scan
- `manifest_body_leakage`
  - reason_code: `manifest_body_leakage`
  - failed_check: manifest body marker scan
- `unsafe_artifact_body_schema`
  - reason_code: `unsafe_artifact_body_schema`
  - failed_check: artifact body schema safety check
- `missing_synthetic_notice`
  - reason_code: `missing_synthetic_notice`
  - failed_check: synthetic notice required check
- `missing_no_oracle_notice`
  - reason_code: `missing_no_oracle_notice`
  - failed_check: no-oracle notice required check
- `unknown_artifact_body_schema_version`
  - reason_code: `unknown_artifact_body_schema_version`
  - failed_check: schema version check

Invalid cases should not contain the unsafe payload itself. They should use
safe marker booleans only.

## 8. Expected Valid Behavior

Expected valid aggregate behavior:

- body_status is `suppressed_metadata_only` or `generated_safe_metadata_body`
- content_suppressed=true
- no_raw_rows=true
- no_logits_dump=true
- no_private_paths=true
- no_performance_claims=true
- synthetic_only_checked=true
- no_oracle_checked=true
- artifact_policy_checked=true
- body_suppression_checked=true
- artifact_body_audit_checked=true
- request_body_count=0
- pointer_body_count=0
- expected_body_count=0
- raw_row_count=0
- logits_dump_count=0
- private_path_count=0
- performance_metric_count=0
- manifest_body_count=0

Valid fixture expected results should remain metadata-only.

## 9. Expected Invalid Behavior

Expected invalid behavior:

- body_status=`fail_closed`
- writer_status or validation_status is fail
- expected reason code is present
- failed check is present
- no raw payload is emitted in expected result
- safe marker boolean only
- body output suppressed
- no artifact file writing
- no manifest file writing
- no performance evidence

Invalid expected results should show only safe labels, booleans, reason codes,
and counts.

## 10. Safe Marker Policy

Invalid fixtures may use safe marker booleans only, such as:

- raw_learner_text_marker_present
- raw_rows_marker_present
- logits_dump_marker_present
- private_path_marker_present
- performance_claim_marker_present
- request_body_marker_present
- pointer_body_marker_present
- expected_result_body_marker_present
- generated_policy_body_marker_present
- manifest_body_marker_present
- unsafe_schema_marker_present
- missing_synthetic_notice_marker_present
- missing_no_oracle_notice_marker_present
- unknown_schema_version_marker_present

Forbidden in fixtures and docs:

- actual raw text
- actual rows
- actual logits
- actual private path
- actual request body
- actual pointer body
- actual expected body
- actual manifest body

The marker should indicate the simulated unsafe condition without embedding
the unsafe content.

## 11. Forbidden Marker Scan

A future validator should detect key names or marker labels for:

- raw_learner_text
- raw_rows
- logits
- probabilities
- private_path
- absolute_path
- request_body
- pointer_body
- expected_result_body
- generated_policy_body
- artifact_body_payload
- manifest_body
- final_text
- observed_after_text
- gold_label
- expected_action
- scoring_feedback_payload
- performance_metrics
- GitHub raw log markers

Detection should fail closed and should not echo the unsafe body back to
stdout, stderr, docs, or expected results.

## 12. Expected Aggregate Counts

Proposed future root counts:

- valid_cases=4
- invalid_cases=14
- total_cases=18
- matched_cases=18
- mismatched_cases=0
- input_error_cases=0

These counts are design targets for the future fixture creation and validator
steps.

## 13. Future Validator Design Outline

A future validator should:

- discover cases
- check required files
- parse JSON
- check schema versions
- check required fields
- run safe marker scan
- compare expected result metadata
- scan for forbidden body leakage
- emit aggregate summary
- emit no body output

Validator output should be metadata-only and deterministic.

## 14. Future CLI / Makefile / Release-Quality Staging

Recommended staging:

- fixture creation
- fixture validator design
- fixture validator implementation
- validator CLI design
- validator CLI implementation
- Makefile target design
- Makefile target implementation
- release-quality integration design
- wrapper integration
- remote status marker

Release-quality integration should wait until standalone validation and log
safety checks are complete.

## 15. Relation To Artifact Body Generation Implementation

Fixtures should be written before implementation. The first implementation
should pass the suppressed metadata-only body path. Safe metadata body
generation should be introduced only after the validator exists. Body
generation should remain optional and default-suppressed until safe mode is
complete.

## 16. Relation To Manifest Writer

Artifact body fixtures should not embed manifest body content. Manifest body
leakage is an invalid case. A future manifest may reference artifact body
metadata only. Manifest writer fixtures remain a separate future step.

## 17. Relation To Current Artifact Writer Fixtures

Current artifact writer fixtures validate writer result metadata. Artifact
body fixtures validate the artifact body generation boundary. These fixture
roots should not be merged.

The artifact writer runtime smoke remains body-free by default.

## 18. Docs Safety Policy

Docs should contain only:

- key names
- case names
- counts
- reason codes
- safe labels
- schema names

Docs must not contain:

- JSON examples
- request body examples
- artifact body examples
- manifest body examples
- raw log examples
- raw rows
- logits or probabilities
- private paths
- raw learner text

## 19. Beginner-Friendly Explanation

An artifact body fixture is a small synthetic contract case that says what the
future body generator should accept or reject. Valid cases describe safe
metadata-only body shapes. Invalid cases describe unsafe conditions using
safe marker booleans instead of the unsafe content itself.

Designing fixtures before generation code makes the safety boundary visible
first. JSON body examples are not pasted into docs because examples can
accidentally become payload templates; this document keeps the design at
schema, key, count, and reason-code level.

## 20. What This Does Not Do

This design does not:

- create fixtures
- implement validator
- implement artifact body generation
- generate artifact body
- write artifact file
- generate manifest body
- write manifest
- change writer CLI
- change Makefile
- change release-quality
- change workflow YAML
- change Python code or tests
- change existing fixture JSON
- compute metrics
- use real data

## 21. Step323 Status

Step323 creates this docs-only artifact body fixture design. It does not
create fixture JSON, implement a validator, implement artifact body
generation, generate bodies, write files, change the CLI, change Makefile
targets, change release-quality, change workflow YAML, change Python code or
tests, change existing fixture JSON, compute metrics, use real data, or
claim production readiness.

## 22. Step324 Fixture Creation Status

Step324 creates the synthetic-only artifact body fixture root:

[Frozen policy generation artifact body fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body/README.md).

The root contains 18 cases, 54 JSON files, and one README. The case layout is
`artifact_body_request.json`, `artifact_writer_result_pointer.json`, and
`expected_artifact_body_result.json` per case. The fixtures remain
metadata-only and no-oracle. Invalid cases use safe marker booleans only.

Step324 does not implement artifact body generation, implement a validator,
change the CLI, change Makefile targets, change release-quality, change
workflow YAML, change Python code or tests, change existing fixture JSON,
generate policy bodies, generate manifest bodies, write files, compute
metrics, use real data, or claim production readiness.

## 23. Step325 Validator Design Status

Step325 designs the future validator for this fixture root:

[Frozen policy generation artifact body fixture validator design](frozen_policy_generation_artifact_body_fixture_validator_design.md).

The design defines validator responsibilities, discovery behavior, safe marker
scan, forbidden payload scan, comparison rules, aggregate summary, error
handling, output safety, and future CLI/Makefile/release-quality staging. It
does not implement validator code, CLI code, Makefile targets, release-quality
integration, artifact body generation, file writing, Python tests, or fixture
JSON changes.

## 24. Step326 Validator Implementation Status

Step326 implements the artifact body fixture validator module and focused unit
tests. The implementation validates the existing 18-case fixture root with
metadata-only results, safe marker scans, forbidden payload scans, exact safe
metadata comparison, and aggregate count summaries.

It does not implement a validator CLI, add a Makefile target, integrate
release-quality, implement artifact body generation, generate bodies, write
files, change fixture JSON, compute metrics, use real data, or claim
production readiness.

## 25. Step327 Validator CLI Design Status

Step327 designs the future command-line interface for the implemented
artifact body fixture validator:

[Frozen policy generation artifact body fixture validator CLI design](frozen_policy_generation_artifact_body_fixture_validator_cli_design.md).

The design keeps terminal output body-free and metadata-only. It does not
implement CLI code, add a Makefile target, integrate release-quality,
implement artifact body generation, generate bodies, write files, change
fixture JSON, compute metrics, use real data, or claim production readiness.

## 26. Step328 Validator CLI Implementation Status

Step328 implements the artifact body fixture validator CLI and focused CLI
tests. The CLI validates this 18-case synthetic fixture root through the
existing validator API and outputs only safe metadata summaries.

It does not add a Makefile target, integrate release-quality, implement
artifact body generation, generate bodies, write files, change fixture JSON,
compute metrics, use real data, or claim production readiness.

## 27. Step329 Validator Makefile Target Design Status

Step329 designs the future Makefile target for the artifact body fixture
validator CLI:

[Frozen policy generation artifact body fixture validator Makefile target design](frozen_policy_generation_artifact_body_fixture_validator_makefile_target_design.md).

The target design keeps this fixture root synthetic-only, metadata-only, and
no-oracle. It does not implement the Makefile target, integrate
release-quality, change workflow YAML, change Python code or tests, change
fixture JSON, implement artifact body generation, write files, compute
metrics, use real data, or claim production readiness.

## 28. Step330 Validator Makefile Target Implementation Status

Step330 implements the standalone Makefile target for validating this fixture
root:

`check-learner-state-frozen-policy-generation-artifact-body-fixtures`

The target runs the existing validator CLI and keeps output metadata-only.
It does not integrate release-quality, change workflow YAML, change Python
code or tests, change fixture JSON, implement artifact body generation, write
files, compute metrics, use real data, or claim production readiness.

## 29. Step331 Release-Quality Integration Design Status

Step331 designs future release-quality integration for the standalone
artifact body fixture validator target:

[Frozen policy generation artifact body fixture release-quality integration design](frozen_policy_generation_artifact_body_fixture_release_quality_integration_design.md).

The design keeps this fixture root synthetic-only, metadata-only, and
no-oracle. It does not change the release-quality wrapper, workflow YAML,
Makefile, Python code or tests, fixture JSON, implement artifact body
generation, write files, compute metrics, use real data, or claim production
readiness.

## 30. Step332 Release-Quality Wrapper Integration Status

Step332 adds the artifact body fixture validator target to the release-quality
wrapper. The release-quality bundle now checks this 18-case synthetic
metadata-only fixture boundary through:

`make check-learner-state-frozen-policy-generation-artifact-body-fixtures`

This does not change fixture JSON, generate artifact bodies, write files,
compute metrics, use real data, or claim production readiness.

## 31. Step333 Remote Run Record Workflow Design Status

Step333 designs the future remote/manual Release Quality run record workflow
for the artifact body fixture validation wrapper integration:

[Frozen policy generation artifact body fixture release-quality remote run record workflow](frozen_policy_generation_artifact_body_fixture_release_quality_remote_run_record_workflow.md).

The workflow design does not create the actual status marker, change fixture
JSON, generate artifact bodies, write files, compute metrics, use real data,
or claim production readiness.

## Related Documents

- [Frozen policy generation artifact body fixture release-quality remote run record workflow](frozen_policy_generation_artifact_body_fixture_release_quality_remote_run_record_workflow.md)
- [Frozen policy generation artifact body fixture release-quality integration design](frozen_policy_generation_artifact_body_fixture_release_quality_integration_design.md)
- [Frozen policy generation artifact body fixture validator Makefile target design](frozen_policy_generation_artifact_body_fixture_validator_makefile_target_design.md)
- [Frozen policy generation artifact body fixture validator CLI design](frozen_policy_generation_artifact_body_fixture_validator_cli_design.md)
- [Frozen policy generation artifact body fixture validator design](frozen_policy_generation_artifact_body_fixture_validator_design.md)
- [Frozen policy generation artifact body fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body/README.md)
- [Frozen policy generation artifact body generation design](frozen_policy_generation_artifact_body_generation_design.md)
- [Frozen policy generation artifact writer design](frozen_policy_generation_artifact_writer_design.md)
- [Frozen policy generation artifact writer CLI design](frozen_policy_generation_artifact_writer_cli_design.md)
- [Frozen policy generation artifact writer runtime Makefile target design](frozen_policy_generation_artifact_writer_runtime_makefile_target_design.md)
- [Frozen policy generation artifact writer runtime release-quality integration design](frozen_policy_generation_artifact_writer_runtime_release_quality_integration_design.md)
- [Learner-state frozen policy generation artifact writer runtime release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_writer_runtime_release_quality_remote_run_status.md)
- [Frozen policy generation artifact writer fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/README.md)
- [Frozen policy generation artifact policy design](frozen_policy_generation_artifact_policy_design.md)
- [Public release checklist](public_release_checklist.md)
