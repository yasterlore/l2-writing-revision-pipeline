# Frozen Policy Generation Manifest Writer Runtime Fixture Contract Design

## 1. Purpose

This document fixes the docs-only fixture contract for future frozen policy
generation manifest writer runtime fixtures.

It is not fixture JSON creation, not runtime implementation, not runtime
validator implementation, not release-quality integration, not performance
evaluation, and not a production readiness claim.

The contract is synthetic-only, metadata-only, and no-oracle. It defines the
future runtime fixture root, case taxonomy, required files, schema versions,
expected result contract, valid/invalid case set, expected counts, path
policy, content policy, and future validation staging.

## 2. Current State

- the static manifest writer fixture validator exists
- the static manifest writer fixture target is in release-quality
- the static fixture validation remote status marker exists
- the manifest writer runtime API design exists
- runtime fixtures do not exist
- manifest writer runtime does not exist
- manifest writer CLI does not exist
- manifest file writing does not exist
- artifact writer CLI integration does not exist
- manifest body remains suppressed

## 3. Proposed Fixture Root

Proposed future runtime fixture root:

- `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime/`

This root should remain separate from the existing static manifest writer
fixture root so that contract-only fixture validation and runtime result
contract validation do not get confused.

## 4. Proposed Case Structure

Each future case directory should contain exactly these five JSON files:

- `case_metadata.json`
- `manifest_writer_request.json`
- `artifact_writer_result_pointer.json`
- `artifact_body_generation_result_pointer.json`
- `expected_manifest_writer_runtime_result.json`

The docs intentionally list file names and field names only. They do not
include JSON body examples.

## 5. Proposed Schema Versions

Proposed schema version names:

- `learner_state_frozen_policy_generation_manifest_writer_runtime_case_metadata_v0.1`
- `learner_state_frozen_policy_generation_manifest_writer_runtime_request_v0.1`
- `learner_state_frozen_policy_generation_manifest_writer_runtime_expected_result_v0.1`
- future result: `learner_state_frozen_policy_generation_manifest_writer_result_v0.1`

## 6. Valid Cases

Recommended valid cases:

- `valid/metadata_only_minimal_no_file`
- `valid/metadata_only_with_artifact_body_reference`
- `valid/metadata_only_with_release_quality_reference`
- `valid/metadata_only_safe_ids_and_counts`
- `valid/metadata_only_no_artifact_body_available`

All valid cases should use the initial runtime mode:

- `metadata_only_no_file`

They should not request manifest body generation, manifest JSON body output,
manifest file writing, artifact body payload embedding, generated policy body
embedding, raw rows, logits, private paths, absolute paths, or performance
proof.

## 7. Invalid / Expected Failure Cases

Recommended invalid / expected-failure cases:

- `invalid/missing_artifact_result_pointer`
- `invalid/missing_artifact_body_result_pointer`
- `invalid/malformed_artifact_result_pointer`
- `invalid/malformed_artifact_body_result_pointer`
- `invalid/unknown_artifact_writer_result_schema`
- `invalid/unknown_artifact_body_generation_result_schema`
- `invalid/generated_policy_body_leakage`
- `invalid/artifact_body_payload_leakage`
- `invalid/manifest_body_requested`
- `invalid/manifest_json_body_requested`
- `invalid/request_body_leakage`
- `invalid/pointer_body_leakage`
- `invalid/expected_body_leakage`
- `invalid/raw_rows_leakage`
- `invalid/logits_dump_leakage`
- `invalid/private_path_leakage`
- `invalid/absolute_path_leakage`
- `invalid/raw_learner_text_leakage`
- `invalid/performance_claim`
- `invalid/missing_synthetic_notice`
- `invalid/missing_no_oracle_notice`
- `invalid/missing_non_proof_notice`
- `invalid/unsafe_manifest_output_path`
- `invalid/overwrite_without_policy`
- `invalid/unsupported_artifact_writer_cli_integration`
- `invalid/real_data_marker`

This proposes 26 invalid cases rather than exactly 25 because the runtime
contract has two distinct unsupported-output risks: manifest body request and
manifest JSON body request. Keeping them separate makes the future validator
and reason-code reporting clearer while still staying near the requested
target.

## 8. Expected Counts

Recommended fixture counts:

- valid cases: 5
- invalid / expected-failure cases: 26
- total cases: 31
- JSON files per case: 5
- total JSON files: 155

The count uses 26 invalid cases to keep `manifest_body_requested` and
`manifest_json_body_requested` separate. A future implementation may collapse
one of those cases to return to 30 cases / 150 JSON files, but it should
record that simplification explicitly.

## 9. Expected Categories

Recommended expected categories:

- `pass_metadata_only_no_file`
- `usage_error_no_write`
- `fail_closed_no_write`
- `input_error`
- `mismatch`

## 10. Expected Category Counts

Recommended expected category counts:

- `pass_metadata_only_no_file`: 5
- `usage_error_no_write`: 8
- `fail_closed_no_write`: 18
- `input_error`: 0
- `mismatch`: 0

This distribution is slightly stricter than the 25-invalid baseline because
one additional fail-closed case is retained for manifest JSON body request.
No malformed fixture input should be expected in the normal root; malformed
runtime input should be represented as expected runtime failure rather than
fixture parse failure.

## 11. Expected Runtime Result Contract

The expected runtime result should be body-free and metadata-only. Expected
result files should use field names such as:

- `expected_category`
- `expected_writer_status`
- `expected_manifest_writer_mode`
- `expected_reason_codes`
- `expected_failed_checks`
- `expected_manifest_body_available`
- `expected_manifest_file_written`
- `expected_manifest_output_path_available`
- `expected_release_quality_ready`
- `expected_safety_flags`
- `expected_count_summary`
- `expected_safe_summary`

Expected result files must not include manifest bodies, manifest JSON bodies,
artifact body payloads, generated policy bodies, request bodies, pointer
bodies, expected result bodies, raw rows, logits, private paths, absolute
paths, raw learner text, or performance proof.

## 12. Request Policy

Future `manifest_writer_request.json` files should use field names such as:

- `schema_version`
- `request_id`
- `manifest_writer_mode`
- `include_manifest_body`
- `allow_manifest_file_writing`
- `manifest_out`
- `overwrite_policy`
- `synthetic_notice`
- `no_oracle_notice`
- `non_proof_notice`
- `validation_reference_ids`
- `release_quality_reference_ids`

The docs do not include a JSON body example. Valid initial cases should set
the contract so that manifest body generation and manifest file writing remain
disabled.

## 13. Pointer Policy

Future artifact writer result pointer and artifact body generation result
pointer files should use field names such as:

- `schema_version`
- `pointer_id`
- `source_kind`
- `source_fixture_id`
- `safe_metadata_reference_id`
- `include_body_payload=false`
- `include_raw_rows=false`
- `include_private_paths=false`

Pointers should refer to safe metadata summaries only. They must not embed
request, pointer, expected result, artifact body, generated policy, manifest,
raw row, logits, private path, absolute path, or learner text bodies.

## 14. Path Policy

- default no manifest file writing
- `allow_manifest_file_writing=false` by default
- `manifest_out` absent for initial valid cases
- future file-writing cases should be separate
- if `manifest_out` is present while file writing is disabled, use
  `usage_error_no_write`
- reject absolute paths
- reject home paths
- reject parent traversal
- reject cloud/private markers
- reject hidden path segments
- reject non-JSON extensions
- reject unsafe filenames
- reject too-long paths
- reject overwrite without policy
- summary must not print absolute resolved paths

The initial runtime fixture contract should not require writing manifest
files.

## 15. Content Policy

- no manifest body
- no manifest JSON body
- no artifact body payload
- no generated policy body
- no request body nesting
- no pointer body nesting
- no expected body nesting
- no raw rows
- no logits or probabilities
- no private paths
- no absolute paths
- no raw learner text
- no performance proof
- no real participant data

## 16. No-Oracle / Synthetic-Only Policy

- synthetic notice required
- no-oracle notice required
- non-proof notice required
- no `final_text`
- no `observed_after_text`
- no gold labels
- no expected action payload
- no scoring feedback payload
- no real participant IDs

The fixture contract should remain synthetic-only and metadata-only even for
expected failure cases.

## 17. Reason Code Taxonomy

Recommended reason codes:

- `missing_artifact_result_pointer`
- `missing_artifact_body_result_pointer`
- `malformed_artifact_result_pointer`
- `malformed_artifact_body_result_pointer`
- `unknown_artifact_writer_result_schema`
- `unknown_artifact_body_generation_result_schema`
- `generated_policy_body_leakage`
- `artifact_body_payload_leakage`
- `manifest_body_requested`
- `manifest_json_body_requested`
- `request_body_leakage`
- `pointer_body_leakage`
- `expected_body_leakage`
- `raw_rows_leakage`
- `logits_dump_leakage`
- `private_path_leakage`
- `absolute_path_leakage`
- `raw_learner_text_leakage`
- `performance_claim`
- `missing_synthetic_notice`
- `missing_no_oracle_notice`
- `missing_non_proof_notice`
- `unsafe_manifest_output_path`
- `overwrite_without_policy`
- `unsupported_artifact_writer_cli_integration`
- `real_data_marker`

Reason codes should be safe labels only. They should not carry body payloads
or private path values.

## 18. Future Validator Design

A future static runtime fixture validator should be a separate step. It
should:

- validate the runtime fixture root structure and file set
- validate schema versions and case IDs
- validate expected category/status contracts
- validate reason code consistency
- validate path-policy sentinels
- validate content-policy sentinels
- validate synthetic/no-oracle/non-proof notices
- report body-free summaries only
- avoid executing the runtime writer
- avoid writing manifest files

Runtime writer execution tests should be later and separate. Makefile,
release-quality, and remote marker steps should also remain later.

## 19. Relation To Existing Static Manifest Writer Fixtures

The existing root checks the static manifest writer fixture contract for
metadata index policy. The proposed runtime root will check runtime
request/pointer/result contracts.

Do not merge the roots. Do not reuse old fixture JSON. Keep names distinct so
static fixture validation is not mistaken for runtime result validation.

## 20. Relation To Artifact Writer / Artifact Body

Runtime fixtures should reference artifact writer summaries and artifact body
generation summaries only. They must not copy or embed body payloads.

Artifact writer CLI integration remains future work. The manifest writer
runtime should aggregate safe metadata only.

## 21. Safety Interpretation

Fixture contract success later would mean the fixture set is internally
consistent. Runtime writer success later would mean metadata-only manifest
result construction works.

Neither outcome means manifest file writing is ready. Neither outcome means
production readiness, model performance, or real-data readiness.

## 22. Beginner-Friendly Explanation

A runtime fixture is a small synthetic case used to test how a future runtime
writer should behave.

The static manifest writer fixtures describe broad contract rules. Runtime
fixtures are closer to the future CLI/API behavior: they hold a request, safe
pointers to upstream summaries, and an expected body-free result.

The request says what the future writer is allowed to do. The pointers tell it
which safe metadata summaries it may reference. The expected result describes
the safe summary the runtime should return.

The fixtures avoid body payloads because the manifest is intended to be a
metadata index, not a place to store generated policies, artifact bodies, raw
rows, or learner text. The first runtime mode stays no-file so file-writing
policy can be added only after summary safety is stable.

## 23. Docs Safety Policy

- no JSON body examples
- no manifest body examples
- no request/pointer body examples
- no artifact body payload examples
- no raw logs
- no private path examples
- field names, counts, and policy only

## 24. What This Does Not Do

- does not create fixture JSON
- does not implement runtime writer
- does not implement runtime validator
- does not write manifest files
- does not change Makefile, wrapper, or workflow
- does not use real data
- does not compute metrics
- does not prove production readiness

## 25. Next Recommended Steps

- Step391: runtime fixture JSON creation
- Step392: runtime fixture validator design
- Step393: runtime fixture validator implementation
- Step394: runtime writer implementation design
- Step395: metadata-only runtime writer implementation
- later Makefile / release-quality / remote marker steps

## 26. Related Documents

- [Frozen policy generation manifest writer runtime API design](frozen_policy_generation_manifest_writer_runtime_api_design.md)
- [Frozen policy generation manifest writer boundary design](frozen_policy_generation_manifest_writer_boundary_design.md)
- [Frozen policy generation manifest writer fixture contract design](frozen_policy_generation_manifest_writer_fixture_contract_design.md)
- [Frozen policy generation manifest writer fixture validator design](frozen_policy_generation_manifest_writer_fixture_validator_design.md)
- [Learner-state frozen policy generation manifest writer fixture release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_fixture_release_quality_remote_run_status.md)
- [Frozen policy generation artifact writer design](frozen_policy_generation_artifact_writer_design.md)
- [Frozen policy generation artifact body generation design](frozen_policy_generation_artifact_body_generation_design.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)
