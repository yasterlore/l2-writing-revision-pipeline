# Frozen Policy Generation Manifest Writer Production File Writing Fixture Contract Design

## 1. Purpose

This document fixes the docs-only fixture contract design for future
production-facing metadata-only manifest file writing fixtures.

This is not fixture JSON creation. It is not runtime implementation, public
`--manifest-out` implementation, artifact writer CLI integration, manifest
body generation, or a production readiness claim.

## 2. Current State

- production file writing design exists
- metadata-only no-file runtime exists
- static file writing fixture validator exists
- isolated write validation exists
- release-quality remote markers exist for static and isolated validation
- production file writing fixture root is created in Step431
- production file writing validator does not exist
- runtime file writing does not exist
- public `--manifest-out` is not implemented
- artifact writer CLI integration does not exist

## 3. Proposed Fixture Root

Future fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_production_file_writing/`

## 4. Proposed Fixture Directory Layout

Top-level layout:

- `valid/`
- `invalid/`
- `README.md`

Each case directory should contain:

- `case_metadata.json`
- `manifest_writer_request.json`
- `artifact_writer_result_pointer.json`
- `artifact_body_generation_result_pointer.json`
- `expected_production_file_writing_result.json`

## 5. Schema Versions

Proposed schema versions:

- `learner_state_frozen_policy_generation_manifest_writer_production_file_writing_case_metadata_v0.1`
- `learner_state_frozen_policy_generation_manifest_writer_production_file_writing_expected_result_v0.1`
- manifest writer request should use the future metadata-only file writing
  runtime schema
- result schema:
  `learner_state_frozen_policy_generation_manifest_writer_production_file_writing_validation_v0.1`

## 6. Case Categories

- `pass_written`
- `pass_no_write`
- `usage_error`
- `fail_closed`

## 7. Proposed Valid Cases

Design 8 valid cases:

- `valid/minimal_manifest_out_file_written`
- `valid/nested_manifest_out_file_written`
- `valid/manifest_out_with_release_quality_reference`
- `valid/manifest_out_with_artifact_body_reference`
- `valid/manifest_out_safe_ids_counts`
- `valid/no_manifest_out_default_no_file`
- `valid/overwrite_allowed_existing_file`
- `valid/safe_relative_subdirectory`

Expected category counts:

- 7 `pass_written` cases
- 1 `pass_no_write` case
- the overwrite-allowed case is one of the 7 `pass_written` cases

## 8. Proposed Invalid Cases

Design 24 invalid cases:

- `invalid/unsafe_absolute_manifest_output_path`
- `invalid/unsafe_parent_traversal_manifest_output_path`
- `invalid/unsafe_manifest_output_path_outside_allowed_root`
- `invalid/unsafe_home_manifest_output_path`
- `invalid/unsafe_private_path_marker_manifest_output_path`
- `invalid/unsafe_cloud_marker_manifest_output_path`
- `invalid/unsafe_hidden_private_manifest_directory`
- `invalid/unsafe_manifest_output_path_extension`
- `invalid/unsafe_manifest_output_filename`
- `invalid/unsafe_manifest_output_path_too_long`
- `invalid/output_exists_without_overwrite`
- `invalid/unsafe_symlink_manifest_output_path`
- `invalid/manifest_body_requested`
- `invalid/artifact_body_payload_leakage`
- `invalid/generated_policy_body_leakage`
- `invalid/request_pointer_expected_body_leakage`
- `invalid/raw_rows_logits_private_raw_text_leakage`
- `invalid/performance_metric_body_leakage`
- `invalid/manifest_write_failure`
- `invalid/manifest_write_parse_failure`
- `invalid/manifest_written_forbidden_content`
- `invalid/partial_write_cleanup_failure`
- `invalid/unsupported_artifact_writer_cli_integration`
- `invalid/unsupported_manifest_writer_mode`

## 9. Proposed Total Counts

Use these expected counts:

- `total_cases=32`
- `valid_cases=8`
- `invalid_cases=24`
- `json_files_per_case=5`
- `total_json_files=160`
- `pass_written_cases=7`
- `pass_no_write_cases=1`
- `usage_error_cases=12`
- `fail_closed_cases=12`
- `matched_cases=32`
- `mismatched_cases=0`
- `input_error_cases=0`

Count math:

- valid 8 = 7 written-capable valid cases plus 1 default no-file valid case
- invalid 24 = 12 usage-error cases plus 12 fail-closed cases
- total JSON files = 32 cases multiplied by 5 required JSON files per case

## 10. Proposed Case Category Mapping

`usage_error`:

- `unsafe_absolute_manifest_output_path`
- `unsafe_parent_traversal_manifest_output_path`
- `unsafe_manifest_output_path_outside_allowed_root`
- `unsafe_home_manifest_output_path`
- `unsafe_private_path_marker_manifest_output_path`
- `unsafe_cloud_marker_manifest_output_path`
- `unsafe_hidden_private_manifest_directory`
- `unsafe_manifest_output_path_extension`
- `unsafe_manifest_output_filename`
- `unsafe_manifest_output_path_too_long`
- `output_exists_without_overwrite`
- `unsafe_symlink_manifest_output_path`

`fail_closed`:

- `manifest_body_requested`
- `artifact_body_payload_leakage`
- `generated_policy_body_leakage`
- `request_pointer_expected_body_leakage`
- `raw_rows_logits_private_raw_text_leakage`
- `performance_metric_body_leakage`
- `manifest_write_failure`
- `manifest_write_parse_failure`
- `manifest_written_forbidden_content`
- `partial_write_cleanup_failure`
- `unsupported_artifact_writer_cli_integration`
- `unsupported_manifest_writer_mode`

## 11. Case Metadata Contract

Field names only:

- `schema_version`
- `case_id`
- `case_category`
- `expected_reason_codes`
- `synthetic_notice`
- `no_oracle_notice`
- `non_proof_notice`
- `production_readiness_notice`
- `fixture_kind`

## 12. Manifest Writer Request Contract

Field names only:

- `schema_version`
- `request_id`
- `manifest_writer_mode`
- `include_manifest_body`
- `allow_manifest_file_writing`
- `manifest_out`
- `allow_overwrite`
- `overwrite_policy`
- `safe_output_root_policy`
- `synthetic_notice`
- `no_oracle_notice`
- `non_proof_notice`
- `validation_reference_ids`
- `release_quality_reference_ids`

Rules:

- valid written cases use `metadata_only_file`
- no-file default case uses `metadata_only_no_file` and no `manifest_out`
- `manifest_out` must be a safe relative path under
  `tmp/frozen_policy_generation_manifest/`
- invalid path cases use sentinel values, not real unsafe local paths
- `include_manifest_body=false` for valid cases
- `allow_manifest_file_writing=true` only for written cases
- artifact writer CLI integration must remain disabled

## 13. Pointer Contracts

Artifact writer pointer field names:

- `schema_version`
- `pointer_id`
- `source_kind`
- `source_fixture_id`
- `safe_metadata_reference_id`
- `artifact_id`
- `manifest_id`
- `include_body_payload`
- `include_raw_rows`
- `include_private_paths`
- `artifact_writer_cli_integration_requested`

Artifact body generation pointer field names:

- `schema_version`
- `pointer_id`
- `source_kind`
- `source_fixture_id`
- `safe_metadata_reference_id`
- `artifact_body_id`
- `artifact_body_available`
- `include_body_payload`
- `include_raw_rows`
- `include_private_paths`

Rules:

- pointers are safe metadata only
- no payloads
- no private paths
- no raw rows
- no CLI execution

## 14. Expected Production File Writing Result Contract

Field names only:

- `schema_version`
- `case_id`
- `expected_category`
- `expected_writer_status`
- `expected_manifest_file_written`
- `expected_written_file_count`
- `expected_manifest_output_path_available`
- `expected_manifest_body_available`
- `expected_manifest_body_suppressed`
- `expected_output_path_safety_checked`
- `expected_content_policy_checked`
- `expected_stdout_body_printed`
- `expected_stderr_body_printed`
- `expected_public_absolute_path_printed`
- `expected_reason_codes`
- `expected_failed_checks`
- `expected_safety_flags`
- `expected_safe_summary`

Rules:

- `pass_written` expects `written_file_count=1`
- `pass_no_write` expects `written_file_count=0`
- `usage_error` and `fail_closed` expect no final write
- `expected_manifest_body_available=false` always
- `expected_manifest_body_suppressed=true` always
- `expected_stdout_body_printed=false`
- `expected_stderr_body_printed=false`
- `expected_public_absolute_path_printed=false`
- no expected written file body is included

## 15. Safe Output Root Policy

Allowed:

- `tmp/frozen_policy_generation_manifest/`
- safe relative paths under that root
- `.json` extension
- safe filename or safe subdirectory
- explicit overwrite only via `allow_overwrite`

Forbidden:

- absolute paths
- user home paths
- cloud or private marker paths
- parent traversal
- outside-root output
- hidden private directories
- non-json extension
- unsafe filename
- too long path
- symlink-sensitive path
- public docs recording absolute output paths

## 16. Valid Manifest Out Examples

Safe relative examples that may be fixture body values:

- `manifest.json`
- `nested/manifest.json`
- `release_quality_reference/manifest.json`
- `artifact_body_reference/manifest.json`
- `safe_ids_counts/manifest.json`
- `safe_relative_subdirectory/manifest.json`
- `overwrite_allowed/manifest.json`

## 17. Forbidden Path Sentinel Values

Use sentinel values for invalid path cases:

- `ABSOLUTE_MANIFEST_OUTPUT_PATH_SENTINEL`
- `PARENT_TRAVERSAL_MANIFEST_OUTPUT_PATH_SENTINEL`
- `OUTSIDE_ALLOWED_ROOT_MANIFEST_OUTPUT_PATH_SENTINEL`
- `HOME_MANIFEST_OUTPUT_PATH_SENTINEL`
- `PRIVATE_PATH_MARKER_MANIFEST_OUTPUT_PATH_SENTINEL`
- `CLOUD_MARKER_MANIFEST_OUTPUT_PATH_SENTINEL`
- `HIDDEN_PRIVATE_MANIFEST_DIRECTORY_SENTINEL`
- `NON_JSON_MANIFEST_EXTENSION_SENTINEL`
- `UNSAFE_MANIFEST_FILENAME_SENTINEL`
- `TOO_LONG_MANIFEST_OUTPUT_PATH_SENTINEL`
- `UNSAFE_SYMLINK_MANIFEST_OUTPUT_PATH_SENTINEL`

## 18. Written File Content Policy

Allowed future written fields:

- `schema_version`
- `result_schema_version`
- `manifest_id`
- `artifact_id`
- `artifact_body_id`
- `manifest_writer_mode`
- `validation_reference_count`
- `release_quality_reference_count`
- `safety_flags`
- `count_summary`
- `safe_summary`
- `writer_version`

Forbidden:

- `manifest_body`
- `manifest_json_body`
- `artifact_body_payload`
- `generated_policy_body`
- `request_body`
- `pointer_body`
- `expected_body`
- `raw_rows`
- `logits`
- `probabilities`
- `private_path`
- `absolute_path`
- `raw_learner_text`
- `final_text`
- `observed_after_text`
- `gold_label`
- `scoring_feedback`
- `real_participant_data`
- `performance_metric_body`

## 19. Stdout/Stderr Safety Policy

- body-free only
- no written file body printed
- no absolute resolved path printed
- no request, pointer, or expected body printed
- no payload printed
- no private path printed
- no raw learner text printed
- reason codes and safe labels only

## 20. Overwrite Policy

- default no overwrite
- output exists without `allow_overwrite` produces `usage_error`
- `allow_overwrite=true` may pass only inside the safe root
- symlink-sensitive path remains forbidden even with overwrite
- overwrite allowed case should be valid but still metadata-only

## 21. Reason Code Taxonomy

Use:

- `unsafe_absolute_manifest_output_path`
- `unsafe_parent_traversal_manifest_output_path`
- `unsafe_manifest_output_path_outside_allowed_root`
- `unsafe_home_manifest_output_path`
- `unsafe_private_path_marker_manifest_output_path`
- `unsafe_cloud_marker_manifest_output_path`
- `unsafe_hidden_private_manifest_directory`
- `unsafe_manifest_output_path_extension`
- `unsafe_manifest_output_filename`
- `unsafe_manifest_output_path_too_long`
- `output_exists_without_overwrite`
- `unsafe_symlink_manifest_output_path`
- `manifest_body_requested`
- `artifact_body_payload_leakage`
- `generated_policy_body_leakage`
- `request_body_leakage`
- `pointer_body_leakage`
- `expected_body_leakage`
- `raw_rows_leakage`
- `logits_dump_leakage`
- `private_path_leakage`
- `absolute_path_leakage`
- `raw_learner_text_leakage`
- `performance_metric_body_leakage`
- `manifest_write_failure`
- `manifest_write_parse_failure`
- `manifest_written_forbidden_content`
- `partial_write_cleanup_failure`
- `unsupported_artifact_writer_cli_integration`
- `unsupported_manifest_writer_mode`

Grouped cases:

- `request_pointer_expected_body_leakage` should include
  `request_body_leakage`, `pointer_body_leakage`, and
  `expected_body_leakage`
- `raw_rows_logits_private_raw_text_leakage` should include
  `raw_rows_leakage`, `logits_dump_leakage`, `private_path_leakage`,
  `absolute_path_leakage`, and `raw_learner_text_leakage`

## 22. Future Validator Expectations

Future validator should check:

- required files
- JSON parse
- schema versions
- case_id consistency
- category counts
- request/result contract
- safe output root policy
- pointer safe metadata policy
- expected result policy
- reason code matching
- stdout/stderr expected suppression fields
- public absolute path suppression fields
- no written file body in expected result
- body-free output

## 23. Future Runtime Expectations

Future runtime should:

- keep no-file default unchanged
- only write when `--manifest-out` is provided and safe
- write exactly one metadata-only manifest JSON for `pass_written` cases
- not print written file body
- not print absolute resolved output path
- fail closed for invalid paths and forbidden content
- leave isolated write validation behavior unchanged

## 24. Relation To Existing Static File Writing Fixtures

The existing file writing fixture root validates future file-writing contracts
statically. The new production file writing fixture root targets future
production-facing runtime behavior.

The separate root avoids confusing static contract validation with runtime
write behavior.

## 25. Relation To Isolated Write Validation

Isolated write validation writes only in validator-owned temp roots.
Production file writing fixtures target project-controlled output root
behavior.

Isolated write validation remains prerequisite evidence, but it is not
sufficient evidence for production-facing runtime file writing.

## 26. Relation To Release-Quality

Future standalone validator or target should come first. Release-quality
integration should happen later. This step does not modify release-quality.

## 27. Relation To Artifact Writer CLI Integration

- no artifact writer CLI execution
- no artifact body generation CLI execution
- pointers only safe metadata
- integration remains separate

## 28. Safety Interpretation

This fixture contract defines future expected behavior. It does not prove
runtime file writing works, public `--manifest-out` exists, production
readiness exists, or real-data readiness exists.

## 29. Beginner-Friendly Explanation

A production file writing fixture contract describes the synthetic cases that
future tests will use when the runtime is allowed to write a metadata-only
manifest file to a safe project-controlled output root.

It is separate from isolated write fixtures because isolated write validation
uses temporary validator-owned roots, while production-facing file writing
targets the normal project-controlled output root.

The valid cases make sure safe writing and default no-file behavior are both
covered. The invalid cases make sure unsafe paths, overwrite mistakes, body
leakage, and unsupported integrations fail closed.

## 30. Docs Safety Policy

Docs may include field names, count names, policy names, reason code names,
safe relative path examples, and sentinel names.

Docs must not include JSON body examples, written output examples, raw logs,
private path examples, or absolute path examples.

## 31. What This Does NOT Do

- does not create fixtures
- does not implement runtime file writing
- does not implement `--manifest-out`
- does not modify runtime
- does not modify Makefile, wrapper, or workflow
- does not modify Python code/tests
- does not connect artifact writer CLI
- does not use real data
- does not compute metrics
- does not prove production readiness

## 32. Next Recommended Steps

- Step431 production file writing fixtures
- Step432 production file writing validator design or runtime fixture
  validator design
- Step433 runtime implementation
- Step434 focused tests
- Step435 Makefile / Release Quality design
- Step436 wrapper integration
- Step437 remote marker

## 33. Step430 Status

Step430 creates this docs-only production-facing metadata-only manifest file
writing fixture contract design. It does not create fixture JSON, implement
production-facing runtime file writing, expose public `--manifest-out`, change
Makefile/wrapper/workflow, change Python code/tests, connect artifact writer
CLI, use real data, compute metrics, or claim production readiness.

## 34. Step431 Fixture Creation Status

Step431 creates the production-facing metadata-only manifest file writing
fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_production_file_writing/`

Final counts:

- `total_cases=32`
- `valid_cases=8`
- `invalid_cases=24`
- `json_files_per_case=5`
- `total_json_files=160`
- `pass_written_cases=7`
- `pass_no_write_cases=1`
- `usage_error_cases=12`
- `fail_closed_cases=12`
- `matched_cases=32`
- `mismatched_cases=0`
- `input_error_cases=0`

The fixture root is synthetic-only and metadata-only. Step431 does not
implement a validator, production-facing runtime file writing, public
`--manifest-out`, Makefile targets, release-quality integration, artifact
writer CLI integration, real-data use, metrics, or production readiness.
