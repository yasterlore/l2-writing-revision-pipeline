# Frozen Policy Generation Manifest Writer Fixture Contract Design

## 1. Purpose

This document fixes the future fixture contract for frozen policy generation
manifest writer validation.

It is a docs-only fixture contract design. It is not fixture JSON creation,
manifest writer implementation, validator implementation, release-quality
integration, performance evaluation, real-data readiness, or production
readiness.

The fixture contract is synthetic-only, metadata-only, and no-oracle. It
defines the fixture root, case directory shape, schema names, field names,
case taxonomy, path policy, content policy, and future validator phases before
any manifest writer fixture JSON is created.

## 2. Current State

- manifest writer boundary design exists
- manifest writer module does not exist
- manifest writer CLI does not exist
- manifest writer fixtures do not exist
- manifest writer validator does not exist
- manifest body generation is not implemented
- manifest file writing is not implemented
- artifact writer CLI integration is not implemented
- artifact body generation remains separate
- artifact body isolated write validation remains separate

## 3. Proposed Fixture Root

Proposed future fixture root:

- `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer/`

Reasons:

- it aligns with the learner-state frozen policy generation namespace
- it sits alongside artifact writer and artifact body fixture roots
- it is manifest-writer-specific
- it is hard to confuse with artifact body isolated write fixtures

This step does not create the fixture root.

## 4. Proposed Case Directory Structure

Each future case directory should contain:

- `case_metadata.json`
- `manifest_writer_request.json`
- `artifact_writer_result_pointer.json`
- `artifact_body_generation_result_pointer.json`
- `expected_manifest_writer_result.json`

The fixture contract should keep the future manifest writer from receiving raw
bodies directly. The artifact writer pointer should reference existing
metadata-only artifact writer results. The artifact body generation pointer
should reference artifact body generation or file-writing result metadata.

Docs must describe only file names, field names, and policy. They must not
include fixture JSON body examples.

## 5. Proposed Schema Names

- `learner_state_frozen_policy_generation_manifest_writer_case_metadata_v0.1`
- `learner_state_frozen_policy_generation_manifest_writer_request_v0.1`
- `learner_state_frozen_policy_generation_manifest_writer_expected_result_v0.1`
- `learner_state_frozen_policy_generation_manifest_writer_result_v0.1`

## 6. Case Metadata Fields

Field names only:

- `schema_version`
- `case_id`
- `case_kind`
- `description`
- `source_artifact_writer_case`
- `source_artifact_body_case`
- `expected_category`
- `expected_status`
- `expected_exit_code`
- `safety_expectation`
- `should_write_manifest_file`
- `should_cleanup`
- `should_leave_residue`
- `allowed_failure_reason_codes`
- `forbidden_output_markers`
- `required_summary_fields`
- `forbidden_summary_fields`
- `notes`

## 7. Manifest Writer Request Fields

Field names only:

- `schema_version`
- `request_id`
- `manifest_id`
- `artifact_id`
- `artifact_body_id`
- `artifact_writer_result_pointer_id`
- `artifact_body_generation_result_pointer_id`
- `validation_reference_ids`
- `release_quality_reference_ids`
- `manifest_out`
- `manifest_output_root`
- `allow_overwrite`
- `cleanup_policy`
- `include_artifact_body_payload`
- `include_generated_policy_body`
- `include_manifest_body`
- `include_request_body`
- `include_pointer_body`
- `include_expected_body`
- `include_raw_rows`
- `include_logits`
- `include_private_paths`
- `synthetic_only`
- `no_oracle_required`
- `non_proof_notice_required`

## 8. Expected Manifest Writer Result Fields

Field names only:

- `schema_version`
- `case_id`
- `expected_category`
- `expected_status`
- `expected_exit_code`
- `expected_manifest_file_written`
- `expected_manifest_body_available`
- `expected_manifest_path_available`
- `expected_manifest_path_safe_relative_only`
- `expected_manifest_json_parse_ok`
- `expected_manifest_allowed_keys_only`
- `expected_manifest_cleanup_ok`
- `expected_residue_file_count`
- `expected_stdout_body_free`
- `expected_stderr_body_free`
- `expected_no_raw_rows`
- `expected_no_logits`
- `expected_no_private_paths`
- `expected_no_absolute_paths`
- `expected_no_raw_learner_text`
- `expected_no_artifact_body_payload`
- `expected_no_generated_policy_body`
- `expected_no_manifest_body_nesting`
- `expected_no_request_body`
- `expected_no_pointer_body`
- `expected_no_expected_body`
- `expected_no_performance_claim`
- `expected_reason_codes`
- `expected_failed_checks`
- `expected_summary_flags`
- `expected_forbidden_counts_zero`
- `expected_no_real_data`

## 9. Expected Categories

- `pass_metadata_only_no_file`
- `pass_manifest_file_written`
- `usage_error_no_write`
- `fail_closed_no_write`
- `input_error`
- `mismatch`

## 10. Valid Case Taxonomy

Proposed future valid cases:

- `valid/metadata_only_manifest_no_file`
- `valid/safe_relative_manifest_file`
- `valid/manifest_with_artifact_body_reference`
- `valid/manifest_with_release_quality_reference`
- `valid/manifest_existing_output_rejected_after_precreate`

The existing-output rejection case is a valid contract case because the
correct behavior is safe refusal. Its expected category may be
`usage_error_no_write`.

The no-file case validates the default no manifest file-writing behavior.

## 11. Invalid / Expected Failure Case Taxonomy

Proposed future invalid or expected-failure cases:

- `invalid/generated_policy_body_leakage`
- `invalid/artifact_body_payload_leakage`
- `invalid/request_body_leakage`
- `invalid/pointer_body_leakage`
- `invalid/expected_body_leakage`
- `invalid/raw_rows_leakage`
- `invalid/logits_dump_leakage`
- `invalid/private_path_leakage`
- `invalid/raw_learner_text_leakage`
- `invalid/manifest_body_nesting`
- `invalid/performance_claim_body`
- `invalid/missing_synthetic_notice`
- `invalid/missing_no_oracle_notice`
- `invalid/missing_non_proof_notice`
- `invalid/unknown_schema_version`
- `invalid/absolute_manifest_output_path`
- `invalid/home_manifest_output_path`
- `invalid/parent_traversal_manifest_output_path`
- `invalid/cloud_marker_manifest_output_path`
- `invalid/private_marker_manifest_output_path`
- `invalid/hidden_private_manifest_directory`
- `invalid/non_json_manifest_extension`
- `invalid/unsafe_manifest_filename`
- `invalid/too_long_manifest_path`
- `invalid/overwrite_without_policy`

## 12. Expected Fixture Counts

Future fixture count target:

- valid cases: 5
- invalid cases: 25
- total cases: 30
- JSON files per case: 5
- total JSON files: 150

This step does not create fixture JSON.

## 13. Path Policy

- default no manifest file writing
- explicit `manifest_out` required for file writing
- dedicated future root: `tmp/frozen_policy_generation_manifest/`
- safe relative path only
- reject absolute paths
- reject home paths
- reject parent traversal
- reject cloud/private markers
- reject hidden private directories
- reject unsafe filename characters
- reject non-`.json` extension
- reject too long path
- reject overwrite unless explicit safe policy exists
- summary must not print absolute resolved path
- cleanup and residue check required in future validator

## 14. Content Policy

Future manifest writer fixtures should validate:

- allowed keys only
- required notices
- safety flags
- count summary
- validation references
- artifact IDs only
- artifact body IDs only
- safe relative path only
- no body
- no payload
- no raw rows
- no logits
- no private path
- no absolute path
- no performance proof
- no nested manifest body
- no request body
- no pointer body
- no expected body
- no raw GitHub logs
- no real participant data

## 15. Validator Phases For Future

- Phase A: fixture structure validation
- Phase B: JSON parse and schema validation
- Phase C: static content-policy validation
- Phase D: path-policy validation
- Phase E: expected result contract matching
- Phase F: optional isolated write execution later
- Phase G: written manifest file parse and allowed-key scan later
- Phase H: cleanup/residue check later
- Phase I: summary-only reporting

## 16. Relation To Existing Artifact Writer / Artifact Body / Isolated Write Fixtures

- artifact writer fixtures validate metadata-only artifact writer behavior
- artifact body fixtures validate artifact body contract
- artifact body file-writing fixtures validate artifact body path/content
  policy
- isolated write fixtures validate artifact body actual temp write behavior
- manifest writer fixtures will validate manifest metadata index behavior

The manifest writer fixture root should not reuse the artifact body isolated
write fixture root. Manifest writer readiness should not be inferred from the
Step377 isolated write release-quality marker.

## 17. Future Implementation Staging

- Step380: manifest writer fixture JSON creation
- Step381: manifest writer fixture validator design
- Step382: manifest writer fixture validator implementation
- Step383: manifest writer fixture validator Makefile target design
- Step384: manifest writer fixture validator Makefile target implementation
- Step385: manifest writer fixture release-quality integration design
- Step386: wrapper integration
- Step387: remote/manual status marker workflow design
- Step388: remote/manual status marker
- later: metadata-only manifest writer API/CLI design
- later: manifest writer implementation

## 18. Safety Interpretation

Fixture contract success means only that the contract design is fixed.

Future fixture validation would mean synthetic fixture contracts matched the
expected metadata-only outcomes. Future writer success would mean
metadata-only manifest safety. None of these means production artifact
management, real-data readiness, model performance, calibration quality,
selective prediction correctness, or learner-state estimator correctness.

## 19. Beginner-Friendly Explanation

A fixture contract is the plan for what test fixture files will look like and
what each case is supposed to prove.

The contract comes before fixture JSON so the project can agree on names,
fields, safety rules, and expected outcomes before creating many files.

Manifest writer fixtures differ from artifact body isolated write fixtures.
Artifact body isolated write fixtures check artifact body file-writing
behavior. Manifest writer fixtures will check whether a metadata-only
manifest index stays safe.

The manifest is metadata-only because it should point to safe identifiers,
references, flags, and counts. It should not carry generated policy text,
artifact body payloads, request bodies, or raw data.

Path policy and content policy are separated because they catch different
risks. Path policy prevents unsafe file locations. Content policy prevents
unsafe data from entering summaries or manifest metadata.

## 20. Docs Safety Policy

Docs for this contract should include field names, file names, case IDs,
counts, and policy only.

Docs must not include JSON examples, manifest body examples, artifact body
payload examples, raw logs, private path examples, raw learner text, raw rows,
logits, real participant data, or performance metric bodies.

## 21. What This Does Not Do

- does not create fixture JSON
- does not implement manifest writer
- does not implement validator
- does not write manifest files
- does not change CLI
- does not change Makefile
- does not change wrapper
- does not change workflow
- does not change Python code/tests
- does not change existing fixture JSON
- does not use real data
- does not compute metrics
- does not prove production readiness

## 22. Next Recommended Steps

- create the synthetic metadata-only fixture JSON
- design the static fixture validator
- implement the static fixture validator
- design the metadata-only writer API/CLI
- implement the metadata-only manifest writer
- stage Makefile, release-quality, and remote marker work separately

## 23. Step380 Fixture JSON Creation Status

Step380 creates the synthetic-only, metadata-only manifest writer fixture
root:

[Frozen policy generation manifest writer fixtures](../tests/fixtures/learner_state_frozen_policy_generation_manifest_writer/README.md).

The fixture root contains 5 valid cases, 25 invalid / expected-failure cases,
30 total case directories, and 150 JSON files. Each case has the five-file
contract fixed by this document. The files use safe metadata, safe sentinel
reason codes, and expected result flags only.

This status does not implement a manifest writer, generate manifest bodies,
write manifest files, implement a validator, add a Makefile target, integrate
release-quality, connect artifact writer CLI, use real data, compute metrics,
or claim production readiness.

## 24. Step381 Fixture Validator Design Status

Step381 adds the docs-only static fixture validator design:

[Frozen policy generation manifest writer fixture validator design](frozen_policy_generation_manifest_writer_fixture_validator_design.md).

The design defines the future validator module, CLI, APIs, validation phases,
required files, schema checks, expected counts, path/content policy checks,
reason-code handling, safe selector rules, exit codes, tests, and staging. It
does not implement the validator, run a manifest writer, write manifest files,
change fixture JSON, add a Makefile target, integrate release-quality, connect
artifact writer CLI, use real data, compute metrics, or claim production
readiness.

## 25. Step382 Static Validator Implementation Status

Step382 implements the static fixture validator described by the Step381
design:

- `python/learner_state/frozen_policy_generation_manifest_writer_fixture_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_manifest_writer_fixture_validation.py`

The validator checks the existing synthetic metadata-only manifest writer
fixture root and produces body-free summaries. It does not run a manifest
writer, generate manifest bodies, write manifest files, add a Makefile target,
integrate release-quality, change workflow YAML, change fixture JSON, connect
artifact writer CLI, use real data, compute metrics, or claim production
readiness.

## 26. Step383 Makefile Target Design Status

Step383 adds the docs-only Makefile target design for the static fixture
validator:

[Frozen policy generation manifest writer fixture validator Makefile target design](frozen_policy_generation_manifest_writer_fixture_validator_makefile_target_design.md).

The design remains separate from this fixture contract and does not implement
a Makefile target, add release-quality integration, implement a manifest
writer, write manifest files, change fixture JSON, use real data, compute
metrics, or claim production readiness.

## 27. Step384 Makefile Target Implementation Status

Step384 implements the standalone target described by the Step383 design:

`check-learner-state-frozen-policy-generation-manifest-writer-fixtures`

The target validates this fixture contract through the static fixture
validator only. It does not add release-quality integration, run a manifest
writer, write manifest files, change fixture JSON, use real data, compute
metrics, or claim production readiness.

## 28. Step385 Release-Quality Integration Design Status

Step385 adds the docs-only release-quality integration design:

[Frozen policy generation manifest writer fixture release-quality integration design](frozen_policy_generation_manifest_writer_fixture_release_quality_integration_design.md).

The design does not add the target to the wrapper, run a manifest writer,
write manifest files, change fixture JSON, use real data, compute metrics, or
claim production readiness.

## 29. Step386 Wrapper Integration Status

Step386 adds the static manifest writer fixture validator target to the
release-quality wrapper. This does not change this fixture contract, run a
manifest writer, write manifest files, change fixture JSON, use real data,
compute metrics, or claim production readiness.

## 30. Related Documents

- [Frozen policy generation manifest writer boundary design](frozen_policy_generation_manifest_writer_boundary_design.md)
- [Frozen policy generation manifest writer fixtures](../tests/fixtures/learner_state_frozen_policy_generation_manifest_writer/README.md)
- [Frozen policy generation manifest writer fixture validator design](frozen_policy_generation_manifest_writer_fixture_validator_design.md)
- [Frozen policy generation manifest writer fixture validator Makefile target design](frozen_policy_generation_manifest_writer_fixture_validator_makefile_target_design.md)
- [Frozen policy generation manifest writer fixture release-quality integration design](frozen_policy_generation_manifest_writer_fixture_release_quality_integration_design.md)
- [Frozen policy generation artifact writer design](frozen_policy_generation_artifact_writer_design.md)
- [Frozen policy generation artifact body file writing design](frozen_policy_generation_artifact_body_file_writing_design.md)
- [Frozen policy generation artifact body isolated temp write validation design](frozen_policy_generation_artifact_body_isolated_temp_write_validation_design.md)
- [Learner-state frozen policy generation artifact body isolated write release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_body_isolated_write_release_quality_remote_run_status.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)
