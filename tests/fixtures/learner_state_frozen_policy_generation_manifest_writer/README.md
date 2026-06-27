# Frozen Policy Generation Manifest Writer Fixtures

This fixture root contains synthetic-only, metadata-only, no-oracle contract
fixtures for a future frozen policy generation manifest writer.

The manifest writer is not implemented yet. These fixtures do not generate a
manifest body, do not write manifest files, do not validate manifest files, and
do not connect artifact writer CLI output.

## Purpose

These fixtures fix the future manifest writer case taxonomy and expected
result contract before implementation. They describe safe metadata references,
path-policy outcomes, content-policy outcomes, and expected category names.

They intentionally do not include raw learner text, raw rows, logits,
probability dumps, artifact body payloads, generated policy bodies, manifest
bodies, request bodies, pointer bodies, expected result bodies, private paths,
absolute local paths, absolute temp paths, real participant data, or
performance evidence.

## Structure

Each case directory contains exactly five JSON files:

- `case_metadata.json`
- `manifest_writer_request.json`
- `artifact_writer_result_pointer.json`
- `artifact_body_generation_result_pointer.json`
- `expected_manifest_writer_result.json`

The fixture root has:

- `valid/`: 5 contract cases
- `invalid/`: 25 expected-failure contract cases
- total cases: 30
- total JSON files: 150

## Schema Versions

- case metadata: `learner_state_frozen_policy_generation_manifest_writer_case_metadata_v0.1`
- request: `learner_state_frozen_policy_generation_manifest_writer_request_v0.1`
- expected result: `learner_state_frozen_policy_generation_manifest_writer_expected_result_v0.1`
- future result: `learner_state_frozen_policy_generation_manifest_writer_result_v0.1`

## Valid Cases

- `valid/metadata_only_manifest_no_file`
- `valid/safe_relative_manifest_file`
- `valid/manifest_with_artifact_body_reference`
- `valid/manifest_with_release_quality_reference`
- `valid/manifest_existing_output_rejected_after_precreate`

The existing-output case is a valid contract case with an expected
`usage_error_no_write` result because safe overwrite refusal is the intended
behavior.

## Invalid / Expected-Failure Cases

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

## Expected Categories

- `pass_metadata_only_no_file`: 3 cases
- `pass_manifest_file_written`: 1 case
- `usage_error_no_write`: 11 cases
- `fail_closed_no_write`: 15 cases

## Path Policy

The future default is no manifest file writing. File writing requires an
explicit safe relative `manifest_out` under the dedicated
`tmp/frozen_policy_generation_manifest/` root.

The fixtures represent rejection cases for absolute, home, parent traversal,
cloud/private marker, hidden private directory, non-JSON extension, unsafe
filename, too-long path, and overwrite-without-policy selectors. Rejection
cases use safe sentinel selectors only; they do not include real private paths
or absolute local paths.

## Content Policy

Future manifest output must remain metadata-only. It may contain safe IDs,
safe reference IDs, safety flags, count summaries, and required notices. It
must not contain bodies, payloads, raw rows, logits, private paths, absolute
paths, raw learner text, performance proof, nested manifest body content, raw
logs, or real participant data.

## What These Fixtures Do Not Prove

These fixtures do not prove manifest writer correctness, manifest file output,
manifest validation, artifact writer CLI integration, model performance,
calibration quality, learner-state estimator correctness, real-data readiness,
or production readiness.

## Future Validator

Step381 adds a docs-only design for a future static fixture validator:

[Frozen policy generation manifest writer fixture validator design](../../../docs/frozen_policy_generation_manifest_writer_fixture_validator_design.md).

That future validator should check fixture structure, schema versions, case
IDs, expected category counts, path-policy sentinels, content-policy
sentinels, reason-code contracts, selector safety, and body-free summaries.
It should not run a manifest writer, generate manifest bodies, write manifest
files, connect artifact writer CLI, use real data, compute metrics, or claim
production readiness.

Step382 implements that static validator and focused tests. The implementation
checks this fixture root only as synthetic metadata contract data. It does not
implement a manifest writer, generate manifest bodies, write manifest files,
add a Makefile target, integrate release-quality, connect artifact writer CLI,
use real data, compute metrics, or claim production readiness.

## Future Makefile Target

Step383 adds a docs-only standalone Makefile target design for running the
static validator through a short project command:

[Frozen policy generation manifest writer fixture validator Makefile target design](../../../docs/frozen_policy_generation_manifest_writer_fixture_validator_makefile_target_design.md).

The design does not implement the target, add release-quality integration,
implement a manifest writer, write manifest files, connect artifact writer
CLI, use real data, compute metrics, or claim production readiness.

Step384 implements that standalone Makefile target:

`check-learner-state-frozen-policy-generation-manifest-writer-fixtures`

The target validates this synthetic metadata-only fixture root through the
static validator. It does not add release-quality integration, implement a
manifest writer, write manifest files, connect artifact writer CLI, use real
data, compute metrics, or claim production readiness.

## Future Release-Quality Integration

Step385 adds a docs-only release-quality integration design for this static
fixture validator target:

[Frozen policy generation manifest writer fixture release-quality integration design](../../../docs/frozen_policy_generation_manifest_writer_fixture_release_quality_integration_design.md).

The design does not add the target to the wrapper, implement a manifest
writer, write manifest files, connect artifact writer CLI, use real data,
compute metrics, or claim production readiness.

Step386 adds that static fixture validator target to the release-quality
wrapper. This does not implement a manifest writer, write manifest files,
connect artifact writer CLI, use real data, compute metrics, or claim
production readiness.
