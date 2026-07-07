# Manifest Writer Handoff Input Contract Design

## 1. Title

Manifest Writer Handoff Input Contract Design

## 2. Scope

This document is design-only / docs-only. It defines only a future manifest writer handoff input contract.

This step does not create fixture JSON, implement Python code/tests, change Makefile, change release-quality wrapper, change workflows, change runtime implementation, or change validator implementation.

This step does not invoke manifest writer, generate manifest body, write manifest files, write artifact files, emit payload body, output artifact body payload, or output generated policy body.

This step does not prove production readiness, real-data readiness, or model performance.

## 3. Prior Accepted Boundary Dependency

Step657 accepted the handoff chain with explicit boundary. Step657 accepted only the metadata-only no-writer-invocation handoff boundary.

Step658 recommended a contract-design step before any manifest writer integration. Step659 defines the future input metadata contract for manifest writer handoff.

Step659 does not invoke manifest writer, generate manifest body, write files, implement a runner, create fixtures, or add release-quality checks.

## 4. Relationship to Step645 Payload Audit Limitation

Step659 does not revise Step645, remove the Step645 local/manual fallback limitation, or change the payload audit chain boundary.

Step659 focuses only on the next boundary after the Step657 handoff chain. The handoff chain is remote-status-recorded based on Step656 / Step657. The payload audit chain remains under its Step645 accepted boundary unless separately updated.

A separate supplemental status/review step would be required if the payload audit chain is to be updated from local/manual-status-recorded to remote-run-recorded.

## 5. Proposed Contract Identity

Proposed design-time identifiers:

```text
contract_name=manifest_writer_handoff_input_contract
schema_version=learner_state_frozen_policy_generation_manifest_writer_handoff_input_v0.1
handoff_input_mode=manifest_writer_handoff_input_metadata_only_no_invocation
boundary_name=manifest_writer_handoff_input_metadata_only_no_writer_invocation
source_boundary=artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation
source_boundary_status=accepted_with_explicit_boundary
source_chain_step=Step647-Step657
```

These are design-time proposed identifiers. Step659 does not create fixture JSON using these identifiers. Step660 or later may use them in a fixture / matrix contract.

## 6. Purpose of the Handoff Input Contract

The contract defines the metadata-only input that a future manifest writer integration may accept after the handoff chain.

The contract answers:

- Which metadata may cross from artifact body handoff to manifest writer staging?
- Which identity fields are required?
- Which safety flags are required?
- Which count-only fields are required?
- Which body / payload / path / raw text fields are forbidden?
- How should future validators classify pass / usage_error / mismatch / fail_closed?
- What must remain out of scope until later steps?

This contract is not manifest writer invocation. It is not manifest body generation. It is not manifest writer correctness. It is not file-writing readiness.

## 7. Allowed Top-Level Metadata Fields

Allowed top-level metadata fields:

- `schema_version`
- `contract_name`
- `handoff_input_id`
- `handoff_input_mode`
- `source_boundary`
- `source_boundary_status`
- `source_chain_step`
- `source_release_quality_status`
- `source_remote_status_recorded`
- `source_local_fallback_used`
- `source_commit_short_hash`
- `source_target_command`
- `source_case_selection`
- `source_matrix_name`
- `source_selected_case_count`
- `source_observed_pass_case_count`
- `source_observed_fail_closed_case_count`
- `source_observed_usage_error_case_count`
- `source_observed_mismatch_case_count`
- `source_processed_case_count`
- `source_input_error_case_count`
- `manifest_writer_handoff_ready`
- `manifest_writer_invocation_requested`
- `manifest_body_generation_requested`
- `manifest_file_writing_requested`
- `artifact_file_writing_requested`
- `payload_body_emission_requested`
- `safety_summary`
- `count_summary`
- `non_claims`
- `next_boundary_notice`

Allowed fields are metadata-only. They must not contain body payloads, raw paths, raw learner text, or real participant data.

## 8. Required Identity Fields

Required identity fields:

- `schema_version`
- `contract_name`
- `handoff_input_id`
- `handoff_input_mode`
- `source_boundary`
- `source_boundary_status`
- `source_chain_step`
- `source_target_command`
- `source_case_selection`
- `source_matrix_name`

Expected values:

```text
schema_version=learner_state_frozen_policy_generation_manifest_writer_handoff_input_v0.1
contract_name=manifest_writer_handoff_input_contract
handoff_input_mode=manifest_writer_handoff_input_metadata_only_no_invocation
source_boundary=artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation
source_boundary_status=accepted_with_explicit_boundary
source_case_selection=artifact-body-to-manifest-handoff-metadata-only-no-writer
source_matrix_name=artifact_body_to_manifest_handoff_metadata_only_no_writer_invocation_matrix
```

## 9. Required Source Summary Fields

Required count-only source fields:

```text
source_selected_case_count=8
source_selected_valid_metadata_only_case_count=3
source_selected_invalid_fail_closed_case_count=5
source_expected_pass_case_count=3
source_observed_pass_case_count=3
source_expected_fail_closed_case_count=5
source_observed_fail_closed_case_count=5
source_expected_usage_error_case_count=0
source_observed_usage_error_case_count=0
source_expected_mismatch_case_count=0
source_observed_mismatch_case_count=0
source_processed_case_count=8
source_input_error_case_count=0
```

Required source release-quality fields:

```text
source_release_quality_status=pass
source_remote_status_recorded=true
source_local_fallback_used=false
source_target_output_seen=true
source_final_release_quality_ok_observed=true
```

These fields are count-only and metadata-only. They do not contain fixture bodies, raw logs, or full job output.

## 10. Required Safety Fields

Recommended required safety fields:

```text
content_suppressed=true
body_suppressed=true
metadata_only_checked=true
synthetic_only_checked=true
no_oracle_checked=true
raw_body_emitted=false
raw_logs_stored_in_docs=false
full_job_output_stored_in_docs=false
manifest_writer_invoked=false
manifest_body_generated=false
manifest_body_output=false
manifest_file_written=false
artifact_file_written=false
file_writing_enabled=false
payload_body_emitted=false
generated_policy_body_emitted=false
artifact_body_payload_output=false
request_body_output=false
pointer_body_output=false
expected_body_output=false
forbidden_body_detected=false
private_path_detected=false
absolute_path_detected=false
raw_learner_text_detected=false
real_data_marker_detected=false
no_oracle_forbidden_field_detected=false
residue_file_count=0
production_readiness_claimed=false
real_data_readiness_claimed=false
performance_claims_present=false
```

Any future manifest writer invocation request must be false in this contract. Any future file-writing request must be false in this contract. This contract remains pre-invocation and pre-file-writing.

## 11. Allowed Nested Metadata Objects

### safety_summary

Allowed keys:

- `content_suppressed`
- `body_suppressed`
- `metadata_only_checked`
- `synthetic_only_checked`
- `no_oracle_checked`
- `raw_body_emitted`
- `raw_logs_stored_in_docs`
- `full_job_output_stored_in_docs`
- `production_readiness_claimed`
- `real_data_readiness_claimed`
- `performance_claims_present`

### count_summary

Allowed keys:

- `selected_case_count`
- `valid_metadata_only_case_count`
- `invalid_fail_closed_case_count`
- `pass_case_count`
- `fail_closed_case_count`
- `usage_error_case_count`
- `mismatch_case_count`
- `manifest_writer_invoked_count`
- `manifest_body_generated_count`
- `manifest_body_output_count`
- `manifest_file_written_count`
- `artifact_file_written_count`
- `file_writing_enabled_count`
- `payload_body_emitted_count`
- `generated_policy_body_emitted_count`
- `artifact_body_payload_output_count`
- `request_body_output_count`
- `pointer_body_output_count`
- `expected_body_output_count`
- `forbidden_body_detected_count`
- `private_path_detected_count`
- `absolute_path_detected_count`
- `raw_learner_text_detected_count`
- `real_data_marker_detected_count`
- `no_oracle_forbidden_field_detected_count`
- `residue_file_count`

### non_claims

Allowed keys:

- `production_readiness`
- `real_data_readiness`
- `model_performance`
- `manifest_writer_correctness`
- `file_writing_readiness`
- `manifest_body_correctness`
- `payload_correctness`
- `educational_validity`

All values should be false or explicit non-claim markers.

## 12. Forbidden Fields

The future contract must reject or fail_closed if any of these appear:

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

Forbidden path-like outputs:

- home directory paths
- cloud sync paths
- private absolute paths
- parent traversal paths
- hidden private directory paths
- symlink write paths
- production output paths

Repository-relative command names and fixture root names may be allowed if they do not reveal private or absolute paths. Private absolute path values are not allowed.

## 13. Required Notice Fields

Recommended notice fields:

- `synthetic_only_notice`
- `metadata_only_notice`
- `no_oracle_notice`
- `no_writer_invocation_notice`
- `no_manifest_body_generation_notice`
- `no_file_writing_notice`
- `non_proof_notice`

Each notice should be metadata-only text, not raw evidence.

The non-proof notice should state:

- This contract does not prove manifest writer correctness.
- This contract does not prove file-writing readiness.
- This contract does not prove manifest body correctness.
- This contract does not prove payload correctness.
- This contract does not prove production readiness.
- This contract does not prove real-data readiness.

## 14. Future Validator Status Semantics

### pass

A future validator may return pass only if:

- `schema_version` is supported.
- required identity fields are present.
- required source summary fields match the Step657 accepted boundary.
- required safety fields are present and safe.
- `manifest_writer_invocation_requested=false`.
- `manifest_body_generation_requested=false`.
- `manifest_file_writing_requested=false`.
- `artifact_file_writing_requested=false`.
- `file_writing_enabled=false`.
- `payload_body_emission_requested=false`.
- no forbidden fields are present.
- no raw logs or body payloads are present.
- no private / absolute path values are present.
- `residue_file_count=0`.
- non-claim notices are present.

### usage_error

A future validator may return usage_error for:

- missing required file
- malformed metadata
- missing `schema_version`
- unsupported `schema_version`
- missing required identity field
- missing required source summary field
- missing required safety field
- invalid boolean / count type
- duplicate `handoff_input_id`
- unsupported `handoff_input_mode`
- unsupported `source_boundary`

### mismatch

A future validator may return mismatch for:

- `source_selected_case_count` not 8
- `source_observed_pass_case_count` not 3
- `source_observed_fail_closed_case_count` not 5
- `source_observed_usage_error_case_count` not 0
- `source_observed_mismatch_case_count` not 0
- `source_release_quality_status` not pass
- `source_remote_status_recorded` not true
- `source_local_fallback_used` not false
- `source_case_selection` mismatch
- `source_matrix_name` mismatch
- accepted boundary fields inconsistent with Step657
- `count_summary` inconsistent with top-level fields

### fail_closed

A future validator must return fail_closed for:

- `manifest_writer_invocation_requested=true`
- `manifest_writer_invoked=true`
- `manifest_body_generation_requested=true`
- `manifest_body_generated=true`
- `manifest_body_output=true`
- `manifest_file_writing_requested=true`
- `manifest_file_written=true`
- `artifact_file_writing_requested=true`
- `artifact_file_written=true`
- `file_writing_enabled=true`
- `payload_body_emission_requested=true`
- `payload_body_emitted=true`
- `artifact_body_payload_output=true`
- `generated_policy_body_emitted=true`
- `request_body_output=true`
- `pointer_body_output=true`
- `expected_body_output=true`
- raw stdout body output
- raw stderr body output
- raw rows present
- logits/probabilities present
- private/absolute path value present
- raw learner text present
- real participant marker present
- final_text / observed_after_text / gold_label / post_hoc_annotation present
- scoring feedback payload present
- performance metric body present
- raw GitHub logs or full job output copied
- residue file detected

## 15. Future Fixture Categories, Design Only

Do not create fixture JSON in Step659.

Suggested valid categories:

- `valid/minimal_handoff_input_metadata_only`
- `valid/complete_handoff_input_count_summary`
- `valid/non_claims_and_notices_present`

Suggested invalid fail_closed categories:

- `invalid/manifest_writer_invocation_requested`
- `invalid/manifest_body_generation_requested`
- `invalid/file_writing_requested`
- `invalid/payload_body_present`
- `invalid/manifest_body_present`
- `invalid/generated_policy_body_present`
- `invalid/private_or_absolute_path_present`
- `invalid/raw_learner_text_present`
- `invalid/no_oracle_forbidden_field_present`
- `invalid/raw_log_or_full_job_output_present`
- `invalid/residue_detected`

Suggested usage_error categories:

- `invalid/missing_schema_version`
- `invalid/unsupported_schema_version`
- `invalid/missing_required_identity_field`
- `invalid/malformed_metadata`
- `invalid/duplicate_handoff_input_id`

Suggested mismatch categories:

- `invalid/source_case_count_mismatch`
- `invalid/source_status_mismatch`
- `invalid/source_remote_status_mismatch`
- `invalid/count_summary_mismatch`

This is only future fixture category planning. Step660 may refine the exact matrix. Step659 must not create fixture JSON.

## 16. Future Matrix Design Principles

Future matrix should:

- remain synthetic-only.
- remain metadata-only.
- remain body-free.
- use metadata categories rather than unsafe body values.
- include valid / usage_error / mismatch / fail_closed classes.
- keep canonical fixtures safe.
- use temp copies or monkeypatching for unsafe actual flag tests if needed in later implementation.
- avoid private / absolute path values.
- avoid raw learner text.
- avoid raw logs.
- avoid manifest body.
- avoid artifact body payload.
- avoid generated policy body.

## 17. Relationship to Existing Manifest Writer Checks

This contract does not replace existing manifest writer fixture validation, manifest writer runtime smoke, manifest writer file-writing fixture validation, or manifest writer isolated write validation.

This contract does not prove manifest writer correctness. It defines a safer input boundary before any future integration step.

Existing manifest writer checks remain separate boundaries.

## 18. Relationship to Step657 Handoff Chain

Step657 accepted the upstream handoff chain. Step659 uses that boundary as source metadata.

Step659 does not expand Step657 into writer invocation, authorize manifest body generation, or authorize file writing. Step659 is a contract design for a future next boundary.

## 19. Safety Scan Requirements

A future validator should scan:

- top-level fields
- nested metadata objects
- notices
- count summaries
- any future optional debug summaries

Scan must check for:

- forbidden field names
- forbidden body-like values
- raw logs
- full job output
- request / pointer / expected bodies
- artifact body payload
- generated policy body
- manifest body
- raw stdout/stderr body
- raw rows
- logits/probabilities
- private / absolute path values
- raw learner text
- real participant data
- final_text / observed_after_text / gold labels / post-hoc annotation
- scoring feedback payload
- performance metric body
- production readiness claims
- real-data readiness claims
- model performance claims

Scan failure must not print offending content. It should be represented as public-safe reason codes and count-only metadata.

## 20. Public-Safe Reason Codes

Example future reason codes:

- `none`
- `missing_schema_version`
- `unsupported_schema_version`
- `missing_required_identity_field`
- `missing_required_source_summary_field`
- `missing_required_safety_field`
- `malformed_metadata`
- `duplicate_handoff_input_id`
- `unsupported_handoff_input_mode`
- `source_boundary_mismatch`
- `source_case_count_mismatch`
- `source_status_mismatch`
- `source_remote_status_mismatch`
- `count_summary_mismatch`
- `manifest_writer_invocation_requested`
- `manifest_writer_invoked`
- `manifest_body_generation_requested`
- `manifest_body_present`
- `manifest_file_writing_requested`
- `manifest_file_written`
- `artifact_file_writing_requested`
- `artifact_file_written`
- `file_writing_enabled`
- `payload_body_present`
- `artifact_body_payload_present`
- `generated_policy_body_present`
- `request_body_present`
- `pointer_body_present`
- `expected_body_present`
- `raw_stdout_body_present`
- `raw_stderr_body_present`
- `raw_rows_present`
- `logits_present`
- `probabilities_present`
- `private_path_present`
- `absolute_path_present`
- `raw_learner_text_present`
- `real_data_marker_present`
- `no_oracle_forbidden_field_present`
- `scoring_feedback_payload_present`
- `performance_metric_body_present`
- `raw_log_or_full_job_output_present`
- `residue_detected`
- `production_readiness_claim_present`
- `real_data_readiness_claim_present`
- `model_performance_claim_present`

## 21. Non-Equivalence Cautions

- Handoff input contract design is not implementation.
- Handoff input contract design is not fixture validation.
- Handoff input contract design is not manifest writer invocation.
- Handoff input contract design is not manifest body generation.
- Handoff input contract design is not file writing.
- Handoff final safety review is not manifest writer correctness.
- Metadata-only input contract is not manifest writer correctness.
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

`Step660: manifest writer handoff fixture / matrix contract design`

Step660 should be design-only / docs-only. It should define future synthetic fixture cases. It should not create fixture JSON, implement Python code/tests, change Makefile, change release-quality wrapper, change workflow, invoke manifest writer, generate manifest body, enable file writing, or emit payload bodies.

## 25. Step660 Fixture / Matrix Contract Design

Step660 creates `docs/frozen_policy_generation_manifest_writer_handoff_fixture_matrix_contract_design.md` as design-only / docs-only fixture / matrix contract design for this input contract.

It defines the future fixture root, matrix identity, fixed 23-case selection, case IDs, expected statuses, fixture file shape, allowed metadata, aggregate pass values, forbidden fixture content, and future validator expectations without creating fixture JSON, implementing Python code/tests, invoking manifest writer, generating manifest body, writing files, or emitting payload bodies.

## 26. Step661 Runner Design

Step661 creates `docs/frozen_policy_generation_manifest_writer_handoff_runner_design.md` as design-only / docs-only future runner / validator behavior design for the Step660 matrix. It does not create fixture JSON, implement Python code/tests, invoke manifest writer, generate manifest body, write files, or emit payload bodies.

## 27. Step662 Fixture / Runner Implementation

Step662 implements the manifest writer handoff input validator / runner as a direct CLI-only check with focused tests and a synthetic body-free fixture root:

- `python/learner_state/frozen_policy_generation_manifest_writer_handoff_input_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_manifest_writer_handoff_input_validation.py`
- `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_handoff_input/`

The implementation validates the 23-case metadata-only contract from Step660. It does not add a Makefile target, release-quality wrapper entry, workflow change, manifest writer invocation, manifest body generation, artifact / manifest file writing, payload body emission, artifact body payload output, or generated policy body output.

## 28. Step663 Makefile Target Design

Step663 creates `docs/frozen_policy_generation_manifest_writer_handoff_input_validation_makefile_target_design.md` as design-only / docs-only Makefile target design for the Step662 direct CLI runner.

The design proposes `check-learner-state-frozen-policy-generation-manifest-writer-handoff-input-validation` as a future standalone target and keeps this input contract unchanged. Step663 does not change Makefile, release-quality wrapper, workflow, Python code/tests, fixture JSON, manifest writer invocation, manifest body generation, file writing, or payload body emission.
