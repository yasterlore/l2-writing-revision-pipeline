# Frozen Policy Generation Manifest Writer Metadata-Only File Writing Fixture Contract Design

## 1. Purpose

This document defines the future fixture contract for metadata-only manifest
file writing.

It is a docs-only contract design. It does not create fixture JSON, implement
runtime file writing, implement `--manifest-out`, add isolated write
validation, integrate release-quality, connect artifact writer CLI, or claim
production readiness.

The contract is synthetic-only, metadata-only, and no-oracle. It defines field
names, case categories, counts, path policy, content policy, expected result
shape, reason codes, and future validator expectations without embedding any
fixture body examples.

## 2. Current State

- The manifest writer runtime exists in no-file mode.
- The runtime CLI exists.
- The runtime smoke Makefile target exists.
- The runtime smoke target is included in release-quality.
- The runtime remote/manual status marker exists.
- The metadata-only file writing boundary design exists.
- File writing fixtures do not exist.
- The file writing fixture validator does not exist.
- Isolated write validation does not exist.
- `--manifest-out` is not implemented.
- Manifest file writing does not exist.
- Manifest body generation does not exist.
- Artifact writer CLI integration does not exist.

## 3. Proposed Future Fixture Root

Future file writing fixtures should live under:

`tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_file_writing/`

This root is reserved for synthetic metadata-only contract fixtures. It is not
a production output root and should not contain real participant data, manifest
bodies, artifact body payloads, generated policy bodies, raw rows, logits,
private paths, absolute local paths, absolute temp paths, or raw learner text.

## 4. Proposed Fixture Directory Layout

Top-level layout:

- `valid/`
- `invalid/`
- `README.md`

Each case directory should contain exactly these required files:

- `case_metadata.json`
- `manifest_writer_request.json`
- `artifact_writer_result_pointer.json`
- `artifact_body_generation_result_pointer.json`
- `expected_manifest_writer_file_writing_result.json`

The fixture contract uses file names and field names only in docs. Fixture JSON
bodies are intentionally not shown here.

## 5. Schema Versions

Proposed fixture schema versions:

- `learner_state_frozen_policy_generation_manifest_writer_file_writing_case_metadata_v0.1`
- `learner_state_frozen_policy_generation_manifest_writer_file_writing_request_v0.1`
- `learner_state_frozen_policy_generation_manifest_writer_file_writing_expected_result_v0.1`

The runtime result schema remains:

- `learner_state_frozen_policy_generation_manifest_writer_result_v0.1`

The validator should fail closed on unknown schema versions and report only
safe reason code names and counts.

## 6. Case Categories

The fixture root should use these case categories:

- `pass_metadata_file_written`
- `pass_metadata_no_file`
- `usage_error_no_write`
- `fail_closed_no_write`
- `input_error`
- `mismatch`

`input_error` and `mismatch` are validator result categories, not desired
fixture outcomes for the proposed root. The intended fixture set should keep
both counts at zero.

## 7. Proposed Valid Cases

Design six valid cases:

- `valid/metadata_file_minimal_safe_relative_json`
- `valid/metadata_file_nested_safe_relative_json`
- `valid/metadata_file_with_artifact_body_reference`
- `valid/metadata_file_with_release_quality_reference`
- `valid/metadata_file_safe_ids_and_counts`
- `valid/metadata_no_file_existing_runtime_mode`

Expected distribution:

- 5 file-written pass cases
- 1 no-file pass case

The five file-written cases exercise safe relative JSON output paths under the
future safe root. The one no-file case preserves compatibility with the
existing `metadata_only_no_file` runtime behavior.

## 8. Proposed Invalid Cases

Design invalid cases covering:

- absolute manifest output path
- parent traversal manifest output path
- output path outside the safe root after normalization
- home output path
- hidden private directory
- cloud/private marker output path
- non-JSON extension
- unsafe filename
- too long manifest path
- overwrite without policy
- manifest body requested
- manifest JSON body requested
- artifact body payload leakage
- generated policy body leakage
- request body leakage
- pointer body leakage
- expected body leakage
- raw rows leakage
- logits dump leakage
- private path leakage
- absolute path leakage
- raw learner text leakage
- performance claim body
- missing synthetic notice
- missing no-oracle notice
- missing non-proof notice
- real data marker
- unsupported artifact writer CLI integration
- unknown schema version
- malformed artifact pointer
- malformed artifact body pointer
- missing artifact pointer
- missing artifact body pointer

Invalid fixtures should use safe sentinel reason codes and metadata-only
markers. They must not include actual payloads, raw rows, logits, private
paths, absolute local paths, absolute temp paths, or raw learner text.

## 9. Proposed Total Counts

The proposed root has 38 cases:

- `valid_cases=6`
- `invalid_cases=32`
- `total_cases=38`
- `json_files_per_case=5`
- `total_json_files=190`
- `pass_metadata_file_written_cases=5`
- `pass_metadata_no_file_cases=1`
- `usage_error_cases=13`
- `fail_closed_cases=19`
- `input_error_cases=0`
- `mismatched_cases=0`

Count math:

- 6 valid cases plus 32 invalid cases equals 38 total cases.
- 38 cases times 5 JSON files per case equals 190 JSON files.
- The 32 invalid cases are split into 13 usage-error no-write cases and 19
  fail-closed no-write cases.

The usage-error group should cover malformed/missing inputs and unsupported
invocation shape. The fail-closed group should cover policy violations and
forbidden content markers.

## 10. Request Contract

`manifest_writer_request.json` should use these field names:

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

Rules:

- File-written valid cases use `metadata_only_file`.
- The no-file valid case uses `metadata_only_no_file`.
- File-written valid cases set `allow_manifest_file_writing=true`.
- File-written valid cases use safe `manifest_out` values.
- Valid cases always set `include_manifest_body=false`.
- Valid cases always include synthetic, no-oracle, and non-proof notices.
- Invalid cases use safe sentinel reason codes, not real unsafe payloads.
- `manifest_out` is a future contract field and is not implemented today.

## 11. Artifact Writer Pointer Contract

`artifact_writer_result_pointer.json` should use these field names:

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

Rules:

- Valid pointers set `include_body_payload=false`.
- Valid pointers set `include_raw_rows=false`.
- Valid pointers set `include_private_paths=false`.
- Invalid leakage cases are represented by sentinel markers, not actual
  payloads.
- The pointer is a safe metadata pointer only; it is not a request to run the
  artifact writer CLI.

## 12. Artifact Body Generation Pointer Contract

`artifact_body_generation_result_pointer.json` should use these field names:

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

- Valid pointers do not include body payload.
- `artifact_body_available` may be true or false as safe metadata.
- Fixture docs must not include artifact body payload examples.
- The pointer is a safe metadata pointer only; it is not a request to run the
  artifact body generation CLI.

## 13. Expected Result Contract

`expected_manifest_writer_file_writing_result.json` should use these field
names:

- `schema_version`
- `case_id`
- `expected_category`
- `expected_writer_status`
- `expected_manifest_writer_mode`
- `expected_reason_codes`
- `expected_failed_checks`
- `expected_manifest_body_available`
- `expected_manifest_file_written`
- `expected_manifest_output_path_available`
- `expected_written_file_count`
- `expected_release_quality_ready`
- `expected_safety_flags`
- `expected_count_summary`
- `expected_safe_summary`
- `expected_output_residue_count`

Rules:

- File-written valid cases expect `manifest_file_written=true`.
- The no-file valid case expects `manifest_file_written=false`.
- All valid cases expect `manifest_body_available=false`.
- All valid cases expect `release_quality_ready=false` initially.
- Invalid cases expect no write.
- Output content bodies are never included.
- Expected result bodies are not pasted into docs.

## 14. Safe Path Policy

Allowed:

- safe root `tmp/frozen_policy_generation_manifest/`
- relative safe path under the safe root
- `.json` extension
- normalized path remains inside the safe root
- optional safe subdirectories

Forbidden:

- absolute path
- parent traversal
- home path
- cloud/private marker path
- hidden private directory
- local user path
- temp absolute path
- non-JSON extension
- too long path
- unsafe filename
- symlink-sensitive path
- overwrite without policy
- normalized path outside the safe root

Validators and future runtime checks should report only reason code names and
safe counts, not raw path examples.

## 15. File Content Policy

Allowed:

- safe metadata
- safe IDs
- reference counts
- safety flags
- count summary
- safe summary
- schema/version

Forbidden:

- manifest body
- manifest JSON body nesting
- artifact body payload
- generated policy body
- request body
- pointer body
- expected body
- raw rows
- logits/probabilities
- private paths
- absolute paths
- raw learner text
- `final_text`
- `observed_after_text`
- gold labels
- scoring feedback payload
- real participant data
- performance metric body

## 16. Reason Code Taxonomy

Invalid cases should use this reason code taxonomy:

- `absolute_manifest_output_path`
- `parent_traversal_manifest_output_path`
- `manifest_output_path_outside_safe_root`
- `home_manifest_output_path`
- `hidden_private_manifest_directory`
- `cloud_marker_manifest_output_path`
- `non_json_manifest_extension`
- `unsafe_manifest_filename`
- `too_long_manifest_path`
- `overwrite_without_policy`
- `manifest_body_requested`
- `manifest_json_body_requested`
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
- `performance_claim_body`
- `missing_synthetic_notice`
- `missing_no_oracle_notice`
- `missing_non_proof_notice`
- `real_data_marker`
- `unsupported_artifact_writer_cli_integration`
- `unknown_schema_version`
- `malformed_artifact_result_pointer`
- `malformed_artifact_body_result_pointer`
- `missing_artifact_result_pointer`
- `missing_artifact_body_result_pointer`

These codes are metadata-only labels. They must not be backed by real unsafe
content in docs or fixtures.

## 17. Fixture README Policy

The future fixture README should state:

- synthetic-only
- metadata-only
- no real data
- no raw learner text
- no manifest body
- no artifact body payload
- no generated policy body
- no private paths
- no absolute paths
- no raw rows/logits
- fixtures are contract fixtures only
- not production readiness

It should also link to the boundary design, this contract design, the future
validator design, and the future isolated write validation design once those
exist.

## 18. Validator Expectations

The future validator should check:

- required file set
- JSON parse
- schema versions
- case ID consistency
- category counts
- request policy
- pointer policy
- expected result policy
- safe path policy
- content policy
- no-oracle notices
- reason code matching
- summary count matching
- body-free output

The validator should be static and count-only. It should not write manifest
files and should not execute the runtime writer.

## 19. Relation To Isolated Write Validation

The fixture validator is static and does not write files.

Isolated write validation should come later. It should write only to an
isolated temp safe root, verify parseable JSON, verify forbidden field count
zero, verify cleanup, and report residue count zero.

Do not combine fixture validation and isolated write validation in one step.
They answer different questions: the fixture validator checks contract shape;
isolated write validation checks actual write behavior.

## 20. Relation To Runtime Implementation

The runtime is currently no-file only.

Future file writing runtime implementation should use these fixtures only
after the fixture contract and validator are in place. Runtime file writing
should not be implemented before the validator and isolated write staging are
ready.

The current runtime smoke remains no-file evidence only.

## 21. Relation To Artifact Writer / Artifact Body

The future manifest writer file writing path should consume safe metadata
pointers only.

It should not:

- run artifact writer CLI
- run artifact body generation CLI
- include artifact body payload
- include generated policy body
- infer artifact writer CLI integration readiness

Artifact writer CLI integration remains a later separate phase.

## 22. Future Staging

Recommended staging:

- Step410: file-writing fixture JSON creation
- Step411: fixture validator design
- Step412: fixture validator implementation
- Step413: Makefile target design
- Step414: Makefile target implementation
- Step415: release-quality integration design
- Step416: wrapper integration
- Step417: remote marker
- later: isolated write validation
- later: runtime file writing implementation

The staging intentionally validates fixture shape before implementing writes.

## 23. Safety Interpretation

This fixture contract defines what future tests should check. It does not
prove file writing works. It does not prove output file correctness. It does
not prove production readiness. It does not imply artifact writer CLI
integration. It does not imply real-data readiness.

## 24. Beginner-Friendly Explanation

A fixture contract is a rulebook for future test cases. It says which files a
case must have, what categories exist, which fields are allowed, and which
failures should be expected.

The contract comes before file writing because writing files has more safety
risk than returning a no-file summary. The project needs clear path and
content rules before any code is allowed to write manifest files.

The fixture set includes both file-written valid cases and a no-file valid case
because the future writer must support the new metadata-only file path without
breaking the existing no-file runtime mode.

There are many invalid path cases because most file-writing bugs are boundary
bugs: unsafe paths, traversal, overwrites, hidden private paths, or normalized
paths escaping the safe root.

## 25. Docs Safety Policy

Docs may include field names, case names, counts, category names, reason code
names, target names, command shapes, and policy language.

Docs must not include:

- `case_metadata` body
- `manifest_writer_request` body
- pointer body
- expected result body
- fixture JSON body examples
- file writing fixture JSON body examples
- manifest body examples
- artifact body payload examples
- generated policy bodies
- raw logs
- private path examples
- raw learner text
- real participant data
- performance metric bodies

## 26. What This Does Not Do

- does not create fixture JSON
- does not implement a validator
- does not write files
- does not implement `--manifest-out`
- does not modify runtime code
- does not modify Makefile
- does not modify the release-quality wrapper
- does not modify workflow YAML
- does not connect artifact writer CLI
- does not use real data
- does not compute metrics
- does not prove production readiness

## 27. Step410 Fixture JSON Creation Status

Step410 creates the synthetic metadata-only fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_file_writing/`

Final fixture counts use the revised Option A split so that missing artifact
writer result pointer and missing artifact body generation result pointer are
separate cases:

- `valid_cases=6`
- `invalid_cases=33`
- `total_cases=39`
- `json_files_per_case=5`
- `total_json_files=195`
- `pass_metadata_file_written_cases=5`
- `pass_metadata_no_file_cases=1`
- `usage_error_cases=15`
- `fail_closed_cases=18`
- `input_error_cases=0`
- `mismatched_cases=0`

This creates fixture JSON only. It does not implement a validator, write
manifest files, add `--manifest-out`, change runtime code, change Makefile,
change the release-quality wrapper, change workflow YAML, connect artifact
writer CLI, use real data, compute metrics, or claim production readiness.

## 28. Step411 Fixture Validator Design Status

Step411 adds the docs-only static validator design for this fixture root:

[Frozen policy generation manifest writer metadata-only file writing fixture validator design](frozen_policy_generation_manifest_writer_file_writing_fixture_validator_design.md).

The fixture contract remains unchanged. Step411 does not implement the
validator, change fixture JSON, write manifest files, add `--manifest-out`,
add isolated write validation, change Makefile, change the release-quality
wrapper, change workflow YAML, connect artifact writer CLI, use real data,
compute metrics, or claim production readiness.

## 29. Step412 Fixture Validator Implementation Status

Step412 implements the static validator and focused tests for this fixture
contract:

- `python/learner_state/frozen_policy_generation_manifest_writer_file_writing_fixture_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_manifest_writer_file_writing_fixture_validation.py`

The implemented validator checks the 39-case / 195-JSON fixture root without
writing files, running the runtime writer, running isolated write validation,
or changing fixture JSON. It reports body-free, count-only metadata and keeps
`release_quality_ready=false` until a separate Makefile/release-quality
staging step.

## 30. Step413 Makefile Target Design Status

Step413 adds the docs-only standalone Makefile target design for running the
static validator CLI:

[Frozen policy generation manifest writer metadata-only file writing fixture validator Makefile target design](frozen_policy_generation_manifest_writer_file_writing_fixture_validator_makefile_target_design.md).

The fixture contract remains unchanged. Step413 does not modify Makefile,
add release-quality integration, change workflow YAML, change Python
code/tests, change fixture JSON, write manifest files, implement
`--manifest-out`, run isolated writes, connect artifact writer CLI, use real
data, compute metrics, or claim production readiness.

## 31. Step414 Makefile Target Implementation Status

Step414 implements the standalone Makefile target
`check-learner-state-frozen-policy-generation-manifest-writer-file-writing-fixtures`
for the static validator CLI. The fixture contract remains unchanged.

Step414 does not add release-quality integration, change workflow YAML,
change Python code/tests, change fixture JSON, write manifest files,
implement `--manifest-out`, run isolated writes, connect artifact writer CLI,
use real data, compute metrics, or claim production readiness.

## 32. Related Documents

- [Frozen policy generation manifest writer metadata-only file writing fixture release-quality integration design](frozen_policy_generation_manifest_writer_file_writing_fixture_release_quality_integration_design.md)
- [Frozen policy generation manifest writer metadata-only file writing fixture validator Makefile target design](frozen_policy_generation_manifest_writer_file_writing_fixture_validator_makefile_target_design.md)
- [Frozen policy generation manifest writer metadata-only file writing fixture validator design](frozen_policy_generation_manifest_writer_file_writing_fixture_validator_design.md)
- [Frozen policy generation manifest writer metadata-only file writing fixture validator implementation](../python/learner_state/frozen_policy_generation_manifest_writer_file_writing_fixture_validation.py)
- [Frozen policy generation manifest writer metadata-only file writing fixture validator tests](../python/learner_state/tests/test_frozen_policy_generation_manifest_writer_file_writing_fixture_validation.py)
- [Frozen policy generation manifest writer metadata-only file writing boundary design](frozen_policy_generation_manifest_writer_file_writing_boundary_design.md)
- [Frozen policy generation manifest writer runtime implementation design](frozen_policy_generation_manifest_writer_runtime_implementation_design.md)
- [Frozen policy generation manifest writer runtime API design](frozen_policy_generation_manifest_writer_runtime_api_design.md)
- [Frozen policy generation manifest writer runtime Makefile target design](frozen_policy_generation_manifest_writer_runtime_makefile_target_design.md)
- [Frozen policy generation manifest writer runtime release-quality integration design](frozen_policy_generation_manifest_writer_runtime_release_quality_integration_design.md)
- [Learner-state frozen policy generation manifest writer runtime release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_runtime_release_quality_remote_run_status.md)
- [Frozen policy generation manifest writer boundary design](frozen_policy_generation_manifest_writer_boundary_design.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)

## 33. Step415 Release-Quality Integration Design Status

Step415 adds the docs-only release-quality integration design for the
standalone file writing fixture validator target:

[Frozen policy generation manifest writer metadata-only file writing fixture release-quality integration design](frozen_policy_generation_manifest_writer_file_writing_fixture_release_quality_integration_design.md).

The fixture contract remains unchanged. Step415 does not modify the wrapper,
workflow YAML, Makefile, Python code/tests, or fixture JSON. It does not
write manifest files, implement `--manifest-out`, run isolated writes, connect
artifact writer CLI, use real data, compute metrics, or claim production
readiness.

## 34. Step416 Wrapper Integration Status

Step416 adds the standalone file writing fixture validator target to the
release-quality wrapper. The fixture contract remains unchanged.

The wrapper now runs the static contract validator through:

`make check-learner-state-frozen-policy-generation-manifest-writer-file-writing-fixtures`

Step416 does not change workflow YAML, Makefile, Python code/tests, fixture
JSON, runtime implementation, manifest file writing, `--manifest-out`,
isolated write validation, artifact writer CLI integration, metrics, real
data use, or production readiness claims.

## 35. Step417 Remote Run Record Workflow Design Status

Step417 adds the docs-only remote/manual run record workflow for future
public-safe status marker creation:

[Frozen policy generation manifest writer metadata-only file writing fixture release-quality remote run record workflow](frozen_policy_generation_manifest_writer_file_writing_fixture_release_quality_remote_run_record_workflow.md).

The fixture contract remains unchanged. Step417 does not create a status
marker, run remote workflows, change workflow YAML, change the wrapper, change
Makefile, change Python code/tests, change fixture JSON, write manifest files,
implement `--manifest-out`, run isolated writes, connect artifact writer CLI,
use real data, compute metrics, or claim production readiness.

## 36. Step418 Remote Status Marker Status

Step418 creates the public-safe remote/manual Release Quality status marker:

[Learner-state frozen policy generation manifest writer file writing fixture release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_file_writing_fixture_release_quality_remote_run_status.md).

The fixture contract remains unchanged. The marker records that the
release-quality wrapper included and passed the static file writing fixture
validator target with 39 cases and 195 JSON files. It does not copy fixture
JSON bodies, request/pointer/expected-result bodies, manifest bodies, raw
logs, private paths, raw learner text, real participant data, or performance
evidence. It does not prove runtime file writing, isolated write validation,
artifact writer CLI integration, real-data readiness, or production
readiness.

## 37. Step419 Isolated Write Validation Design Status

Step419 adds the docs-only isolated write validation design:

[Frozen policy generation manifest writer metadata-only isolated write validation design](frozen_policy_generation_manifest_writer_isolated_write_validation_design.md).

The existing file writing fixture contract remains static and unchanged.
Step419 recommends a separate future isolated write fixture root so actual
write/no-write behavior, parseable JSON checks, stdout/stderr suppression,
cleanup, and residue checks do not blur with static contract validation.
Step419 does not create fixtures, write files, implement runtime file writing,
add `--manifest-out`, change code/tests, change Makefile/wrapper/workflow, or
claim production readiness.

## 38. Step420 Isolated Write Fixture Contract Design Status

Step420 adds the docs-only isolated write fixture contract design:

[Frozen policy generation manifest writer metadata-only isolated write fixture contract design](frozen_policy_generation_manifest_writer_isolated_write_fixture_contract_design.md).

The static file writing fixture contract remains unchanged. The new contract
design is for a separate future isolated write validation root and does not
create fixtures, modify existing fixture JSON, implement isolated writes,
implement runtime file writing, add `--manifest-out`, change Makefile,
wrapper, workflow, or Python code/tests, use real data, compute metrics, or
claim production readiness.
