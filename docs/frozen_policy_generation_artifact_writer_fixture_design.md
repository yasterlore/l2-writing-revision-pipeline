# Frozen Policy Generation Artifact Writer Fixture Design

This document designs future fixtures for the frozen policy generation artifact
writer. It is docs-only. It does not create fixture files, does not implement a
validator, does not implement the writer, does not generate artifact bodies,
does not generate generated policy bodies, does not generate manifest bodies,
does not write files, does not compute metrics, and does not claim real-data
readiness.

The fixture design is synthetic-only and metadata-only. It intentionally avoids
copying JSON fixture bodies, request bodies, pointer bodies, expected result
bodies, policy bodies, artifact bodies, raw rows, logits, private paths, or raw
learner text into documentation.

## 1. Purpose

The purpose of this document is to define the fixture contract for a future
artifact writer implementation:

- fixture root layout
- case directory file names
- valid case intent
- invalid fail-closed case intent
- allowed metadata keys
- forbidden payload keys
- expected safe result metadata
- expected artifact flags
- expected safety flags
- count-only summary requirements
- reason-code mapping
- future validator implications

This is not:

- fixture implementation
- validator implementation
- artifact writer implementation
- artifact body generation
- generated policy body generation
- manifest body generation
- file writing
- performance evaluation
- real-data readiness evidence

## 2. Current State

Currently:

- artifact writer design exists:
  [Frozen policy generation artifact writer design](frozen_policy_generation_artifact_writer_design.md)
- artifact writer fixture design exists in this document
- artifact writer fixture files now exist as the Step302 synthetic-only
  metadata-only fixture root
- artifact writer validator does not exist
- artifact writer implementation does not exist
- artifact body generation does not exist
- generated policy body generation does not exist
- manifest body generation does not exist
- artifact file writing does not exist

## 3. Proposed Fixture Root

Recommended fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/`

Rationale:

- aligns with the `learner_state` namespace
- clearly belongs to the frozen policy generation pipeline
- clearly targets the artifact writer boundary
- stays separate from generator scaffold fixtures
- supports future validator and Makefile target names

## 4. Proposed Fixture File Layout

Each case directory should contain:

- `artifact_writer_request.json`
- `generator_result_pointer.json`
- `expected_artifact_writer_result.json`

Documentation should describe only schema/key-level contracts. It must not
paste JSON bodies from these files.

Recommended case directory shape:

- `valid/<case_name>/artifact_writer_request.json`
- `valid/<case_name>/generator_result_pointer.json`
- `valid/<case_name>/expected_artifact_writer_result.json`
- `invalid/<case_name>/artifact_writer_request.json`
- `invalid/<case_name>/generator_result_pointer.json`
- `invalid/<case_name>/expected_artifact_writer_result.json`

## 5. Valid Fixture Cases

### `valid/minimal_metadata_only_artifact_plan`

Purpose:

- proves the minimal metadata-only artifact writer request can pass
- requests no artifact body
- requests no file writing
- requests a manifest summary only

Allowed inputs:

- safe request IDs
- safe generator result reference IDs
- safe policy and artifact IDs
- `requested_artifact_body=false`
- `requested_file_writing=false`
- `requested_manifest=true`
- synthetic-only and no-oracle flags
- count-only generator result summary

Expected artifact flags:

- `generated_artifact_written=false`
- `generated_artifact_body_available=false`
- `artifact_body_suppressed=true`
- `artifact_file_path_available=false`
- `artifact_manifest_available=true`
- `artifact_manifest_body_available=false`
- `artifact_validation_summary_available=true`
- `file_writing_allowed=false`
- `manifest_body_suppressed=true`

Expected safety flags:

- all required safety flags are true

Expected count summary:

- validation reference count is at least 1
- artifact metadata field count is greater than 0
- manifest metadata field count is greater than 0
- all body, raw row, logits, private path, performance, generated artifact,
  written file, and manifest body counts are 0

Expected status and reason codes:

- `writer_status=pass`
- `reason_codes=none`
- `failed_checks=none`

Forbidden leakage checks:

- no request body
- no pointer body
- no expected result body
- no policy body
- no artifact body
- no manifest body
- no raw rows
- no logits
- no private paths
- no raw learner text

### `valid/metadata_manifest_summary_only`

Purpose:

- proves that a manifest metadata summary can be represented safely
- confirms manifest body remains unavailable and suppressed

Allowed inputs:

- safe manifest ID
- safe artifact metadata fields
- count-only manifest metadata summary
- synthetic-only and no-oracle flags

Expected artifact flags:

- `artifact_manifest_available=true`
- `artifact_manifest_body_available=false`
- `manifest_body_suppressed=true`
- no generated artifact body
- no file writing

Expected safety flags:

- all required safety flags are true
- manifest body suppression is checked
- output path safety is checked

Expected count summary:

- manifest metadata field count is greater than 0
- manifest body count is 0
- written file count is 0

Expected status and reason codes:

- `writer_status=pass`
- `reason_codes=none`
- `failed_checks=none`

Forbidden leakage checks:

- no manifest body
- no generated policy body
- no artifact body
- no private paths
- no performance metrics

### `valid/synthetic_generator_result_reference`

Purpose:

- proves the writer can consume a safe generator scaffold result reference
- avoids copying generator scaffold request or expected result bodies
- confirms the writer uses metadata references only

Allowed inputs:

- safe generator result ID
- safe generator result pointer ID
- safe validation reference IDs
- safe policy and artifact IDs
- count-only generator result summary

Expected artifact flags:

- no artifact body available
- no generated artifact written
- manifest summary metadata available
- manifest body unavailable
- file writing disabled

Expected safety flags:

- all required safety flags are true
- generator result reference is treated as metadata-only

Expected count summary:

- validation reference count is at least 1
- body field count is 0
- generated artifact count is 0
- written file count is 0

Expected status and reason codes:

- `writer_status=pass`
- `reason_codes=none`
- `failed_checks=none`

Forbidden leakage checks:

- no generator scaffold request body
- no generator scaffold pointer body
- no expected generator scaffold result body
- no generated policy body
- no artifact body
- no raw rows
- no logits
- no private paths

## 6. Invalid Fixture Cases

Each invalid case should return:

- `writer_status=fail`
- one exact expected reason code
- one expected failed check
- safe fail-closed summary
- no artifact writing
- no manifest writing
- no body output
- no private path output

### `invalid/generated_policy_body_leakage`

- purpose: detects generated policy body carryover
- forbidden trigger: generated policy body field or marker
- expected reason code: `generated_policy_body_leakage`
- expected failed check: `generated_policy_body_leakage`
- expected safe summary: fail-closed metadata-only writer result

### `invalid/generated_artifact_body_leakage`

- purpose: detects generated artifact body carryover
- forbidden trigger: generated artifact body field or marker
- expected reason code: `generated_artifact_body_leakage`
- expected failed check: `generated_artifact_body_leakage`
- expected safe summary: fail-closed metadata-only writer result

### `invalid/manifest_body_leakage`

- purpose: detects manifest body output or carryover
- forbidden trigger: manifest body field or marker
- expected reason code: `manifest_body_leakage`
- expected failed check: `manifest_body_leakage`
- expected safe summary: fail-closed metadata-only writer result

### `invalid/raw_rows_carryover`

- purpose: detects raw row carryover
- forbidden trigger: raw rows field or marker
- expected reason code: `raw_rows_carryover`
- expected failed check: `raw_rows_carryover`
- expected safe summary: fail-closed metadata-only writer result

### `invalid/logits_dump_carryover`

- purpose: detects logits or probability dump carryover
- forbidden trigger: logits or probabilities field or marker
- expected reason code: `logits_dump_carryover`
- expected failed check: `logits_dump_carryover`
- expected safe summary: fail-closed metadata-only writer result

### `invalid/private_path_output`

- purpose: detects private or unsafe path output
- forbidden trigger: private or absolute path field or marker
- expected reason code: `private_path_output`
- expected failed check: `private_path_output`
- expected safe summary: fail-closed metadata-only writer result

### `invalid/artifact_file_writing_not_allowed`

- purpose: rejects artifact file writing in the initial writer boundary
- forbidden trigger: requested artifact file writing
- expected reason code: `artifact_file_writing_not_allowed`
- expected failed check: `artifact_file_writing_not_allowed`
- expected safe summary: fail-closed metadata-only writer result

### `invalid/manifest_file_writing_not_allowed`

- purpose: rejects manifest file writing in the initial writer boundary
- forbidden trigger: requested manifest file writing
- expected reason code: `manifest_file_writing_not_allowed`
- expected failed check: `manifest_file_writing_not_allowed`
- expected safe summary: fail-closed metadata-only writer result

### `invalid/non_synthetic_input`

- purpose: rejects non-synthetic or real-data-marked input
- forbidden trigger: synthetic-only flag is false or real-data marker appears
- expected reason code: `non_synthetic_input`
- expected failed check: `non_synthetic_input`
- expected safe summary: fail-closed metadata-only writer result

### `invalid/no_oracle_violation`

- purpose: rejects no-oracle boundary violations
- forbidden trigger: oracle-like label, final text, observed-after text, or
  future information marker
- expected reason code: `no_oracle_violation`
- expected failed check: `no_oracle_violation`
- expected safe summary: fail-closed metadata-only writer result

### `invalid/scoring_feedback_violation`

- purpose: rejects expected-action or scoring-feedback payloads
- forbidden trigger: scoring feedback payload or expected action field
- expected reason code: `scoring_feedback_violation`
- expected failed check: `scoring_feedback_violation`
- expected safe summary: fail-closed metadata-only writer result

### `invalid/performance_claim_in_artifact`

- purpose: rejects artifact metadata that claims performance evidence
- forbidden trigger: performance metric body or performance claim marker
- expected reason code: `performance_claim_in_artifact`
- expected failed check: `performance_claim_in_artifact`
- expected safe summary: fail-closed metadata-only writer result

### `invalid/missing_required_field`

- purpose: rejects incomplete required metadata
- forbidden trigger: required field omitted
- expected reason code: `missing_required_field`
- expected failed check: `missing_required_field`
- expected safe summary: safe input error or fail-closed metadata-only writer
  result

### `invalid/unknown_schema_version`

- purpose: rejects unknown schema versions
- forbidden trigger: unsupported schema version marker
- expected reason code: `unknown_schema_version`
- expected failed check: `unknown_schema_version`
- expected safe summary: safe input error or fail-closed metadata-only writer
  result

## 7. Allowed Request Metadata

Allowed keys:

- `schema_version`
- `request_id`
- `generator_result_id`
- `generator_result_pointer_id`
- `policy_id`
- `artifact_id`
- `manifest_id`
- `generator_version`
- `artifact_writer_version`
- `validation_reference_ids`
- `artifact_policy_label`
- `requested_artifact_body`
- `requested_file_writing`
- `requested_manifest`
- `synthetic_only`
- `no_oracle_required`
- `safe_output_mode`
- `safe_notes`
- `expected_status`
- `expected_reason_codes`
- `expected_failed_checks`
- `count_summary_hint`

## 8. Forbidden Request / Pointer Payload

Forbidden keys and payloads:

- `generated_policy_body`
- `generated_artifact_body`
- `artifact_body`
- `manifest_body`
- `policy_body`
- `raw_rows`
- `logits`
- `probabilities`
- `raw_learner_text`
- `observed_after_text`
- `final_text`
- `gold_label`
- `expected_action`
- `scoring_feedback_payload`
- `request_body`
- `pointer_body`
- `expected_result_body`
- `private_path`
- `absolute_path`
- `real_participant_data`
- `calibration_body`
- `label_body`
- `split_body`
- `performance_metrics`

## 9. Expected Result Contract

Allowed result metadata:

- `schema_version`
- `writer_status`
- `reason_codes`
- `failed_checks`
- `request_id`
- `generator_result_id`
- `policy_id`
- `artifact_id`
- `manifest_id`
- `artifact_writer_version`
- `artifact_policy_label`
- `artifact_flags`
- `safety_flags`
- `count_summary`
- `safe_summary`

Forbidden result:

- `generated_policy_body`
- `generated_artifact_body`
- `artifact_body`
- `manifest_body`
- `raw_rows`
- `logits`
- `probabilities`
- `raw_learner_text`
- `final_text`
- `observed_after_text`
- `gold_label`
- `private_path`
- `performance_metrics`

## 10. Artifact Flags Expected

Valid cases:

- `generated_artifact_written=false`
- `generated_artifact_body_available=false`
- `artifact_body_suppressed=true`
- `artifact_file_path_available=false`
- `artifact_manifest_available=true`
- `artifact_manifest_body_available=false`
- `artifact_validation_summary_available=true`
- `file_writing_allowed=false`
- `manifest_body_suppressed=true`

Invalid cases:

- preserve safe failure flags
- `generated_artifact_written=false`
- `generated_artifact_body_available=false`
- `artifact_body_suppressed=true`
- `artifact_manifest_body_available=false`
- `file_writing_allowed=false`
- `manifest_body_suppressed=true`

## 11. Safety Flags Expected

Required true in valid and safe fail-closed invalid cases:

- `content_suppressed`
- `no_raw_rows`
- `no_logits_dump`
- `no_private_paths`
- `no_performance_claims`
- `synthetic_only_checked`
- `no_oracle_checked`
- `test_tuning_checked`
- `scoring_feedback_checked`
- `artifact_policy_checked`
- `body_suppression_checked`
- `file_writing_checked`
- `manifest_body_suppression_checked`
- `output_path_safety_checked`

## 12. Count Summary Expected

Valid cases:

- `validation_reference_count >= 1`
- `artifact_metadata_field_count > 0`
- `manifest_metadata_field_count > 0`
- `body_field_count=0`
- `raw_row_count=0`
- `logits_dump_count=0`
- `private_path_count=0`
- `performance_metric_count=0`
- `generated_artifact_count=0`
- `written_file_count=0`
- `manifest_body_count=0`

Invalid cases:

- all body, leakage, and file-writing counts in output remain 0
- reason codes identify the trigger
- no body appears in expected result

## 13. Expected Reason Code Mapping

- `generated_policy_body_leakage` -> `generated_policy_body_leakage`
- `generated_artifact_body_leakage` -> `generated_artifact_body_leakage`
- `manifest_body_leakage` -> `manifest_body_leakage`
- `raw_rows_carryover` -> `raw_rows_carryover`
- `logits_dump_carryover` -> `logits_dump_carryover`
- `private_path_output` -> `private_path_output`
- `artifact_file_writing_not_allowed` -> `artifact_file_writing_not_allowed`
- `manifest_file_writing_not_allowed` -> `manifest_file_writing_not_allowed`
- `non_synthetic_input` -> `non_synthetic_input`
- `no_oracle_violation` -> `no_oracle_violation`
- `scoring_feedback_violation` -> `scoring_feedback_violation`
- `performance_claim_in_artifact` -> `performance_claim_in_artifact`
- `missing_required_field` -> `missing_required_field`
- `unknown_schema_version` -> `unknown_schema_version`

## 14. Relation To Generator Scaffold Fixtures

Artifact writer fixtures should:

- not copy generator scaffold request bodies
- not copy generator scaffold pointer bodies
- not copy expected generator scaffold result bodies
- reference safe generator scaffold results by ID or pointer metadata only
- not depend on raw generated policy bodies
- not depend on artifact bodies
- reuse safe IDs from generator scaffold output metadata where helpful
- avoid importing full generated policy or artifact payloads

## 15. Relation To Artifact Writer Design

This fixture design implements the contract from Step300:

- valid cases show metadata-only success
- invalid cases show fail-closed safety
- body and file-writing paths remain disabled
- fixture design prepares Step302 fixture creation
- no implementation is added yet

## 16. Relation To Future Validator

The future validator should:

- compare fixture expected result metadata
- scan forbidden keys and body markers
- summarize total cases, matched cases, mismatched cases, and input errors
- emit body-free output
- avoid executing the artifact writer unless explicitly designed later
- avoid copying fixture bodies into logs or docs

## 17. Docs Safety Policy

Documentation must include:

- schema-level descriptions
- key-level descriptions
- safe IDs
- reason-code names
- count-only expectations

Documentation must not include:

- JSON fixture bodies
- raw logs
- request bodies
- pointer bodies
- expected result bodies
- artifact bodies
- policy bodies
- manifest bodies
- raw rows
- logits
- private paths
- raw learner text

## 18. Proposed Next Steps

Recommended next steps:

1. Step307: artifact writer fixture validator Makefile target design.
2. Step308: artifact writer fixture validator Makefile target implementation.
3. Step309: artifact writer fixture validator release-quality integration
   design.

## 19. Beginner-Friendly Explanation

A fixture is a small synthetic example that says, "when the future code sees
this kind of metadata, it should return this safe result."

Valid fixtures describe safe inputs that should pass. Invalid fixtures describe
unsafe or unsupported inputs that should fail closed. Both are useful because
they turn the safety boundary into something a validator can check.

Body leakage cases are needed because the artifact writer must never expose
generated policy bodies, artifact bodies, manifest bodies, raw rows, logits, or
raw learner text. File-writing request cases are needed because the first
writer boundary must reject output-file behavior until a separate path-safety
design exists.

The expected result must also stay metadata-only. Otherwise the test fixture
itself would become a place where unsafe body content could leak.

## 20. What This Does Not Do

This document does not:

- create fixture files
- implement a validator
- implement the writer
- generate artifact bodies
- generate generated policy bodies
- generate manifest bodies
- write artifact files
- write manifest files
- compute metrics
- evaluate performance
- use real data

## 21. Step302 Fixture Creation Status

Step302 creates the fixture root described by this design:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/`

The created root contains:

- 17 total cases
- 3 valid cases
- 14 invalid fail-closed cases
- 51 JSON files
- one root README

The fixture files remain synthetic-only and metadata-only. They do not include
artifact writer request bodies, artifact writer expected result bodies,
generator scaffold request bodies, pointer bodies, expected result bodies,
generated policy bodies, artifact bodies, manifest bodies, raw rows, logits,
private paths, raw learner text, real participant data, or performance metric
bodies.

Step302 does not implement an artifact writer, validator, CLI, Makefile
target, release-quality integration, artifact body generation, generated
policy body generation, manifest body generation, artifact file writing, or
manifest file writing.

## 22. Step303 Fixture Validator Design Status

Step303 designs the future validator for this fixture root:
[Frozen policy generation artifact writer fixture validator design](frozen_policy_generation_artifact_writer_fixture_validator_design.md).

The fixture files remain unchanged. The validator design covers discovery,
required-file checks, schema checks, safe marker scans, expected result
metadata matching, root summaries, and future CLI/Makefile/release-quality
staging. It does not implement validator code, execute an artifact writer,
generate artifact bodies, generate generated policy bodies, generate manifest
bodies, write artifact or manifest files, compute metrics, or claim real-data
readiness.

## 23. Step304 Fixture Validator Implementation Status

Step304 implements the metadata-only validator for this fixture root:

`python/learner_state/frozen_policy_generation_artifact_writer_fixture_validation.py`

The implementation validates the fixture contract without running an artifact
writer. It checks 17 synthetic cases, preserves the 3 valid / 14 invalid case
split, permits only safe marker booleans for invalid triggers, and keeps the
root summary body-free and count-only.

The fixture JSON files remain unchanged. Step304 does not add an artifact
writer, CLI, Makefile target, release-quality wrapper integration, workflow
change, artifact body generation, generated policy body generation, manifest
body generation, artifact file writing, or manifest file writing.

## 24. Step305 Fixture Validator CLI Design Status

Step305 designs the future terminal entrypoint for the fixture validator:
[Frozen policy generation artifact writer fixture validator CLI design](frozen_policy_generation_artifact_writer_fixture_validator_cli_design.md).

The fixture JSON files remain unchanged. Step305 does not implement CLI code,
artifact writer code, Makefile targets, release-quality integration, workflow
changes, artifact body generation, generated policy body generation, manifest
body generation, artifact file writing, or manifest file writing.

## 25. Step306 Fixture Validator CLI Implementation Status

Step306 implements the metadata-only validator CLI. It can validate this root
or one case directory from the terminal and prints only safe metadata
summaries.

The fixture JSON files remain unchanged. Step306 does not implement an
artifact writer, Makefile target, release-quality integration, workflow
change, artifact body generation, generated policy body generation, manifest
body generation, artifact file writing, or manifest file writing.

## Related Documents

- [Frozen policy generation artifact writer fixture validator CLI design](frozen_policy_generation_artifact_writer_fixture_validator_cli_design.md)
- [Frozen policy generation artifact writer fixture validator design](frozen_policy_generation_artifact_writer_fixture_validator_design.md)
- [Frozen policy generation artifact writer fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/README.md)
- [Frozen policy generation artifact writer design](frozen_policy_generation_artifact_writer_design.md)
- [Frozen policy generation artifact policy design](frozen_policy_generation_artifact_policy_design.md)
- [Frozen policy generation generator scaffold skeleton design](frozen_policy_generation_generator_scaffold_skeleton_design.md)
- [Frozen policy generation generator scaffold CLI design](frozen_policy_generation_generator_scaffold_cli_design.md)
- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Learner-state frozen policy generation generator scaffold runtime release-quality remote run status](status/learner_state_frozen_policy_generation_generator_scaffold_runtime_release_quality_remote_run_status.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)
