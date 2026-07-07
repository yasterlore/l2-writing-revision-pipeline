# Manifest Writer Handoff Fixture and Matrix Contract Design

## 1. Title

Manifest Writer Handoff Fixture and Matrix Contract Design

## 2. Scope

This document is design-only / docs-only. It defines only a future fixture / matrix contract.

This step does not create fixture JSON, implement Python code/tests, change Makefile, change release-quality wrapper, change workflows, change runtime implementation, or change validator implementation.

This step does not invoke manifest writer, generate manifest body, write manifest files, write artifact files, emit payload body, output artifact body payload, or output generated policy body.

This step does not prove production readiness, real-data readiness, or model performance.

## 3. Prior Contract Dependency

Step659 defined the future manifest writer handoff input contract.

Step660 defines a future synthetic fixture / matrix contract for that input contract. It does not create fixture JSON, implement a validator, implement a runner, invoke manifest writer, generate manifest body, write files, or add Makefile / release-quality checks.

## 4. Relationship to Step645 Payload Audit Limitation

Step660 does not revise Step645, remove the Step645 local/manual fallback limitation, or change the payload audit chain boundary.

Step660 focuses only on the next boundary after Step657 / Step659. The handoff chain is remote-status-recorded based on Step656 / Step657. The payload audit chain remains under its Step645 accepted boundary unless separately updated.

A separate supplemental status/review step would be required if the payload audit chain is to be updated from local/manual-status-recorded to remote-run-recorded.

## 5. Future Fixture Root

Recommended future fixture root:

```text
tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_handoff_input
```

Step660 must not create this directory. Step661 or later may use this root if a fixture implementation step is approved. The future root must remain synthetic-only and body-free.

## 6. Future Matrix Identity

Recommended future fixture / matrix identifiers:

```text
matrix_name=manifest_writer_handoff_input_contract_matrix
case_selection=manifest-writer-handoff-input-contract
schema_version=learner_state_frozen_policy_generation_manifest_writer_handoff_input_v0.1
contract_name=manifest_writer_handoff_input_contract
handoff_input_mode=manifest_writer_handoff_input_metadata_only_no_invocation
boundary_name=manifest_writer_handoff_input_metadata_only_no_writer_invocation
source_boundary=artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation
source_boundary_status=accepted_with_explicit_boundary
source_chain_step=Step647-Step657
```

These are future fixture / matrix identifiers only. Step660 does not create fixture JSON or schema files.

## 7. Future Selected Case Contract

Recommended fixed matrix:

```text
selected_case_count=23
selected_valid_case_count=3
selected_invalid_case_count=20
selected_fail_closed_case_count=11
selected_usage_error_case_count=5
selected_mismatch_case_count=4
expected_pass_case_count=3
expected_fail_closed_case_count=11
expected_usage_error_case_count=5
expected_mismatch_case_count=4
expected_manifest_writer_invocation_case_count=0
expected_manifest_body_generation_case_count=0
expected_file_writing_case_count=0
expected_payload_body_emission_case_count=0
expected_artifact_body_payload_output_case_count=0
expected_generated_policy_body_output_case_count=0
expected_residue_file_count=0
```

Invalid cases may represent unsafe categories as metadata labels. Canonical fixtures must not contain actual unsafe body values, trigger writer invocation, write files, or include body content.

## 8. Future Case IDs

### Valid Cases

1. `valid/minimal_handoff_input_metadata_only`
2. `valid/complete_handoff_input_count_summary`
3. `valid/non_claims_and_notices_present`

### Invalid Fail_Closed Cases

4. `invalid/fail_closed_manifest_writer_invocation_requested`
5. `invalid/fail_closed_manifest_body_generation_requested`
6. `invalid/fail_closed_file_writing_requested`
7. `invalid/fail_closed_payload_body_present`
8. `invalid/fail_closed_manifest_body_present`
9. `invalid/fail_closed_generated_policy_body_present`
10. `invalid/fail_closed_private_or_absolute_path_present`
11. `invalid/fail_closed_raw_learner_text_present`
12. `invalid/fail_closed_no_oracle_forbidden_field_present`
13. `invalid/fail_closed_raw_log_or_full_job_output_present`
14. `invalid/fail_closed_residue_detected`

### Invalid Usage_Error Cases

15. `invalid/usage_error_missing_schema_version`
16. `invalid/usage_error_unsupported_schema_version`
17. `invalid/usage_error_missing_required_identity_field`
18. `invalid/usage_error_malformed_metadata`
19. `invalid/usage_error_duplicate_handoff_input_id`

### Invalid Mismatch Cases

20. `invalid/mismatch_source_case_count_mismatch`
21. `invalid/mismatch_source_status_mismatch`
22. `invalid/mismatch_source_remote_status_mismatch`
23. `invalid/mismatch_count_summary_mismatch`

These are future case IDs only. Step660 does not create directories or JSON files. Step661 may refine runner design, but should not silently change this contract without documenting why.

## 9. Expected Status by Case

Valid cases:

```text
expected_status=pass
expected_category=valid_metadata_only
```

Fail_closed cases:

```text
expected_status=fail_closed
expected_category=invalid_fail_closed
```

For fail_closed cases, `unsafe_condition_category` should be metadata-only. Actual forbidden body values must not be present in canonical fixtures.

Usage_error cases:

```text
expected_status=usage_error
expected_category=invalid_usage_error
```

Mismatch cases:

```text
expected_status=mismatch
expected_category=invalid_mismatch
```

## 10. Future Fixture File Shape

Recommended future files per case:

- `handoff_input_metadata.json`
- `expected_summary_metadata.json`
- `safety_expectations.json`

Step660 must not create these files. Future files must be metadata-only and must not contain raw logs, body payloads, private or absolute path values, raw learner text, or real participant data.

## 11. Allowed Per-Case Metadata Fields

Allowed per-case metadata fields include:

- `case_id`
- `schema_version`
- `contract_name`
- `handoff_input_id`
- `handoff_input_mode`
- `boundary_name`
- `matrix_name`
- `case_selection`
- `expected_status`
- `expected_category`
- `unsafe_condition_category`
- `source_boundary`
- `source_boundary_status`
- `source_chain_step`
- `source_release_quality_status`
- `source_remote_status_recorded`
- `source_local_fallback_used`
- `source_target_command`
- `source_case_selection`
- `source_matrix_name`
- `source_selected_case_count`
- `source_selected_valid_metadata_only_case_count`
- `source_selected_invalid_fail_closed_case_count`
- `source_expected_pass_case_count`
- `source_observed_pass_case_count`
- `source_expected_fail_closed_case_count`
- `source_observed_fail_closed_case_count`
- `source_expected_usage_error_case_count`
- `source_observed_usage_error_case_count`
- `source_expected_mismatch_case_count`
- `source_observed_mismatch_case_count`
- `source_processed_case_count`
- `source_input_error_case_count`
- `manifest_writer_handoff_ready`
- `manifest_writer_invocation_requested`
- `manifest_writer_invoked`
- `manifest_body_generation_requested`
- `manifest_body_generated`
- `manifest_body_output`
- `manifest_file_writing_requested`
- `manifest_file_written`
- `artifact_file_writing_requested`
- `artifact_file_written`
- `file_writing_enabled`
- `payload_body_emission_requested`
- `payload_body_emitted`
- `artifact_body_payload_output`
- `generated_policy_body_emitted`
- `request_body_output`
- `pointer_body_output`
- `expected_body_output`
- `raw_stdout_body_suppressed`
- `raw_stderr_body_suppressed`
- `forbidden_body_detected`
- `private_path_detected`
- `absolute_path_detected`
- `raw_learner_text_detected`
- `real_data_marker_detected`
- `no_oracle_forbidden_field_detected`
- `residue_file_count`
- `content_suppressed`
- `body_suppressed`
- `metadata_only_checked`
- `synthetic_only_checked`
- `no_oracle_checked`
- `production_readiness_claimed`
- `real_data_readiness_claimed`
- `performance_claims_present`
- `non_claims_present`
- `required_notices_present`
- `reason_code`

These fields are metadata-only. Any future true value for unsafe actual-output flags should cause fail_closed. Canonical unsafe cases should prefer `unsafe_condition_category` over unsafe body values.

## 12. Allowed Aggregate Metadata Fields

Allowed future aggregate summary fields:

- `mode`
- `schema_version`
- `contract_name`
- `matrix_name`
- `case_selection`
- `status`
- `reason_code`
- `selected_case_count`
- `selected_valid_case_count`
- `selected_invalid_case_count`
- `selected_fail_closed_case_count`
- `selected_usage_error_case_count`
- `selected_mismatch_case_count`
- `expected_pass_case_count`
- `observed_pass_case_count`
- `expected_fail_closed_case_count`
- `observed_fail_closed_case_count`
- `expected_usage_error_case_count`
- `observed_usage_error_case_count`
- `expected_mismatch_case_count`
- `observed_mismatch_case_count`
- `processed_case_count`
- `input_error_case_count`
- `manifest_writer_invocation_requested_count`
- `manifest_writer_invoked_count`
- `manifest_body_generation_requested_count`
- `manifest_body_generated_count`
- `manifest_body_output_count`
- `manifest_file_writing_requested_count`
- `manifest_file_written_count`
- `artifact_file_writing_requested_count`
- `artifact_file_written_count`
- `file_writing_enabled_count`
- `payload_body_emission_requested_count`
- `payload_body_emitted_count`
- `artifact_body_payload_output_count`
- `generated_policy_body_emitted_count`
- `request_body_output_count`
- `pointer_body_output_count`
- `expected_body_output_count`
- `forbidden_body_detected_count`
- `private_path_detected_count`
- `absolute_path_detected_count`
- `raw_learner_text_detected_count`
- `real_data_marker_detected_count`
- `no_oracle_forbidden_field_detected_count`
- `raw_log_or_full_job_output_detected_count`
- `residue_file_count`
- `content_suppressed`
- `body_suppressed`
- `metadata_only_checked`
- `synthetic_only_checked`
- `no_oracle_checked`
- `production_readiness_claimed`
- `real_data_readiness_claimed`
- `performance_claims_present`

## 13. Expected Aggregate Pass Values

Expected aggregate pass values for the future validator:

```text
status=pass
reason_code=none
selected_case_count=23
selected_valid_case_count=3
selected_invalid_case_count=20
selected_fail_closed_case_count=11
selected_usage_error_case_count=5
selected_mismatch_case_count=4
expected_pass_case_count=3
observed_pass_case_count=3
expected_fail_closed_case_count=11
observed_fail_closed_case_count=11
expected_usage_error_case_count=5
observed_usage_error_case_count=5
expected_mismatch_case_count=4
observed_mismatch_case_count=4
processed_case_count=23
input_error_case_count=0
manifest_writer_invocation_requested_count=0
manifest_writer_invoked_count=0
manifest_body_generation_requested_count=0
manifest_body_generated_count=0
manifest_body_output_count=0
manifest_file_writing_requested_count=0
manifest_file_written_count=0
artifact_file_writing_requested_count=0
artifact_file_written_count=0
file_writing_enabled_count=0
payload_body_emission_requested_count=0
payload_body_emitted_count=0
artifact_body_payload_output_count=0
generated_policy_body_emitted_count=0
request_body_output_count=0
pointer_body_output_count=0
expected_body_output_count=0
forbidden_body_detected_count=0
private_path_detected_count=0
absolute_path_detected_count=0
raw_learner_text_detected_count=0
real_data_marker_detected_count=0
no_oracle_forbidden_field_detected_count=0
raw_log_or_full_job_output_detected_count=0
residue_file_count=0
content_suppressed=True
body_suppressed=True
metadata_only_checked=True
synthetic_only_checked=True
no_oracle_checked=True
production_readiness_claimed=False
real_data_readiness_claimed=False
performance_claims_present=False
```

Important distinction: `observed_fail_closed_case_count=11` means unsafe categories were classified as fail_closed. It does not mean forbidden bodies were emitted. Unsafe actual-output counts remain 0 in the canonical pass aggregate.

## 14. Forbidden Fixture Content

Future canonical fixtures must not contain:

- `payload_body`
- `artifact_body_payload`
- `generated_policy_body`
- `manifest_body`
- `manifest_json_body`
- `request_body`
- `pointer_body`
- `expected_body`
- `raw_stdout_body`
- `raw_stderr_body`
- `raw_rows`
- `logits`
- `probabilities`
- `private_path_value`
- `absolute_path_value`
- `raw_learner_text`
- `real_participant_data`
- `final_text`
- `observed_after_text`
- `gold_label`
- `post_hoc_annotation`
- `scoring_feedback_payload`
- `test_set_tuning_payload`
- `performance_metric_body`
- `raw_github_actions_logs`
- `full_job_output`
- `copied_log_block`

Forbidden path-like values:

- home directory paths
- cloud sync paths
- private absolute paths
- parent traversal paths
- hidden private directory paths
- symlink write paths
- production output paths

Use metadata categories, not unsafe values. Repository-relative fixture roots and command names may be allowed when they are public-safe and not private/absolute paths.

## 15. Future Validator Selection Policy

A future validator should:

- require `case_selection=manifest-writer-handoff-input-contract`.
- require the expected matrix name.
- require the expected schema version.
- require exactly 23 cases.
- require exact case IDs.
- reject duplicate case IDs.
- reject unknown case IDs.
- reject missing required case IDs.
- reject unsupported schema version.
- reject unsupported `contract_name`.
- reject unsupported `handoff_input_mode`.
- reject unsupported `source_boundary`.

## 16. Future Validator Status Semantics

### pass

A future validator may return pass only if:

- all 23 cases are selected.
- 3 valid cases pass.
- 11 fail_closed category cases are classified as fail_closed without emitting forbidden bodies.
- 5 usage_error cases are classified as usage_error.
- 4 mismatch cases are classified as mismatch.
- aggregate counts match expected values.
- safety fields are present and safe.
- no manifest writer invocation occurs.
- no manifest body is generated.
- no file writing occurs.
- no forbidden body / payload / path / raw text is emitted.
- `residue_file_count=0`.

### usage_error

Usage_error categories include:

- missing schema_version
- unsupported schema_version
- missing required identity field
- malformed metadata
- duplicate handoff_input_id
- missing required file
- invalid boolean or count type
- unsupported handoff_input_mode
- unsupported source_boundary

### mismatch

Mismatch categories include:

- source case count mismatch
- source status mismatch
- source remote status mismatch
- count summary mismatch
- source case selection mismatch
- matrix name mismatch
- selected case count mismatch

### fail_closed

Fail_closed categories include:

- manifest writer invocation requested
- manifest writer invoked
- manifest body generation requested
- manifest body present
- file writing requested
- file writing enabled
- artifact or manifest file written
- payload body present
- artifact body payload present
- generated policy body present
- private or absolute path present
- raw learner text present
- real data marker present
- no-oracle forbidden field present
- raw log or full job output present
- residue detected
- production readiness claim present
- real-data readiness claim present
- model performance claim present

## 17. Future Fixture Safety Rules

Future canonical fixtures must:

- be synthetic-only.
- be metadata-only.
- be body-free.
- use count-only summaries.
- avoid raw logs.
- avoid full job output.
- avoid manifest body.
- avoid artifact body payload.
- avoid generated policy body.
- avoid request / pointer / expected body.
- avoid raw stdout/stderr body.
- avoid raw rows.
- avoid logits/probabilities.
- avoid private / absolute path values.
- avoid raw learner text.
- avoid real participant data.
- avoid performance metric bodies.
- avoid production readiness claims.
- avoid real-data readiness claims.
- avoid model performance claims.

## 18. Future Implementation Staging

Suggested chain:

- Step661: manifest writer handoff runner design
- Step662: manifest writer handoff fixture / runner implementation
- Step663: Makefile target design
- Step664: Makefile target implementation
- Step665: release-quality integration design
- Step666: release-quality wrapper integration
- Step667: remote/manual status marker workflow design
- Step668: status marker
- Step669: final safety review

Step661 should still be design-only. Step662 may implement fixture JSON / runner only after Step661 design. No step should invoke manifest writer unless explicitly planned and reviewed in a later boundary. Manifest writer invocation remains out of scope for this fixture / matrix contract chain.

## 19. Relationship to Existing Manifest Writer Checks

This fixture / matrix contract does not replace existing manifest writer fixture validation, manifest writer runtime smoke, manifest writer file-writing fixture validation, or manifest writer isolated write validation.

This fixture / matrix contract does not prove manifest writer correctness. It defines a safer pre-invocation input boundary before any future integration step.

Existing manifest writer checks remain separate boundaries.

## 20. Relationship to Step657 / Step659

Step657 accepted the upstream handoff chain. Step659 defined the future handoff input contract. Step660 defines future cases for that contract.

Step660 does not expand the boundary into writer invocation, authorize manifest body generation, or authorize file writing.

## 21. Non-Equivalence Cautions

- Fixture / matrix contract design is not fixture implementation.
- Fixture / matrix contract design is not validator implementation.
- Fixture / matrix contract design is not runner implementation.
- Fixture / matrix contract design is not manifest writer invocation.
- Fixture / matrix contract design is not manifest body generation.
- Fixture / matrix contract design is not file writing.
- Handoff input contract is not manifest writer correctness.
- Metadata-only fixture matrix is not manifest writer correctness.
- No-writer-invocation is not writer correctness.
- No-file-writing is not file-writing readiness.
- Manifest writer validators remain separate.
- File-writing validators remain separate.
- Release-quality success is not production readiness.
- Synthetic-only pass is not real-data readiness.
- Payload audit Step645 limitation remains separate.

## 22. Non-Claims

- Does not claim production readiness.
- Does not claim real-data readiness.
- Does not claim model performance.
- Does not claim F1 / accuracy / ECE / AURCC achievement.
- Does not claim runtime correctness generally.
- Does not claim all invalid-case runtime behavior.
- Does not claim payload correctness.
- Does not claim artifact body payload quality.
- Does not claim manifest writer correctness.
- Does not claim file-writing readiness.
- Does not claim manifest body correctness.
- Does not claim generated policy quality.
- Does not claim learner-state estimator correctness.
- Does not claim educational validity.

## 23. Public-Safe Checklist

- no raw logs
- no full job output
- no copied GitHub log blocks
- no screenshots containing raw logs
- no fixture JSON body
- no request body
- no pointer body
- no expected body
- no written file JSON body
- no artifact body payload
- no generated policy body
- no manifest body
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

## 24. Recommended Next Step

Recommended:

`Step661: manifest writer handoff runner design`

Step661 should be design-only / docs-only. It should design how a future validator/runner reads the Step660 fixture matrix. It should not create fixture JSON, implement Python code/tests, change Makefile, change release-quality wrapper, change workflow, invoke manifest writer, generate manifest body, enable file writing, or emit payload bodies.

## 25. Step661 Runner Design

Step661 creates `docs/frozen_policy_generation_manifest_writer_handoff_runner_design.md` as design-only / docs-only runner / validator behavior design for this 23-case fixture / matrix contract.

It defines the future module, CLI, input model, fixture reading policy, selection algorithm, per-case classification, aggregate output, status semantics, failure mapping, safety scan, residue policy, and Step662 focused test plan without creating fixture JSON, implementing Python code/tests, invoking manifest writer, generating manifest body, writing files, or emitting payload bodies.

## 26. Step662 Fixture / Runner Implementation

Step662 creates the synthetic body-free fixture root `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_handoff_input/` and implements the direct CLI runner and focused tests for this 23-case contract.

The implementation keeps the canonical fixture metadata-only: invalid categories are represented by `unsafe_condition_category` and public-safe reason codes while actual writer/body/file/payload flags remain false / 0. Step662 does not add a Makefile target, release-quality wrapper entry, workflow change, manifest writer invocation, manifest body generation, artifact / manifest file writing, payload body emission, artifact body payload output, or generated policy body output.

## 27. Step663 Makefile Target Design

Step663 creates `docs/frozen_policy_generation_manifest_writer_handoff_input_validation_makefile_target_design.md` as design-only / docs-only standalone Makefile target design for the Step662 direct CLI runner.

The design keeps this fixture contract unchanged and does not modify Makefile, release-quality wrapper, workflow, Python code/tests, fixture JSON, manifest writer invocation, manifest body generation, artifact / manifest file writing, payload body emission, artifact body payload output, or generated policy body output.

## 28. Step664 Makefile Target Implementation

Step664 adds the standalone Makefile target `check-learner-state-frozen-policy-generation-manifest-writer-handoff-input-validation` for the Step662 direct CLI runner.

This fixture contract and fixture JSON remain unchanged. The target is not release-quality integrated and does not invoke manifest writer, generate manifest body, write files, emit payload body, output artifact body payload, or output generated policy body.

## 29. Step665 Release-Quality Integration Design

Step665 creates `docs/frozen_policy_generation_manifest_writer_handoff_input_validation_release_quality_integration_design.md` as design-only / docs-only planning for adding the Step664 standalone target to the release-quality wrapper in a future step.

This fixture contract and fixture JSON remain unchanged. Step665 does not change wrapper, Makefile, workflow, Python code/tests, manifest writer invocation, manifest body generation, file writing, payload body emission, artifact body payload output, or generated policy body output.
