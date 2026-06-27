# Frozen Policy Generation Manifest Writer Runtime Fixtures

This fixture root contains synthetic-only, metadata-only, no-oracle runtime
fixture contracts for a future frozen policy generation manifest writer.

The manifest writer runtime and CLI are not implemented yet. These fixtures do
not execute a runtime writer, do not generate manifest bodies, do not write
manifest files, do not validate written manifest files, and do not connect
artifact writer CLI output.

## Purpose

These fixtures fix the future runtime request, safe pointer, and expected
runtime result contract before implementation. They describe the initial
`metadata_only_no_file` mode, safe upstream metadata references, no-file path
policy, content-policy outcomes, and expected category names.

They intentionally do not include raw learner text, raw rows, logits,
probability dumps, artifact body payloads, generated policy bodies, manifest
bodies, manifest JSON bodies, request bodies, pointer bodies, expected result
bodies, private paths, absolute local paths, absolute temp paths, real
participant data, raw logs, full job output, or performance evidence.

## Structure

Each case directory contains exactly five JSON files:

- `case_metadata.json`
- `manifest_writer_request.json`
- `artifact_writer_result_pointer.json`
- `artifact_body_generation_result_pointer.json`
- `expected_manifest_writer_runtime_result.json`

The fixture root has:

- `valid/`: 5 runtime contract cases
- `invalid/`: 26 expected-failure runtime contract cases
- total cases: 31
- total JSON files: 155

## Schema Versions

- case metadata: `learner_state_frozen_policy_generation_manifest_writer_runtime_case_metadata_v0.1`
- request: `learner_state_frozen_policy_generation_manifest_writer_runtime_request_v0.1`
- expected result: `learner_state_frozen_policy_generation_manifest_writer_runtime_expected_result_v0.1`
- future result: `learner_state_frozen_policy_generation_manifest_writer_result_v0.1`

## Valid Cases

- `valid/metadata_only_minimal_no_file`
- `valid/metadata_only_with_artifact_body_reference`
- `valid/metadata_only_with_release_quality_reference`
- `valid/metadata_only_safe_ids_and_counts`
- `valid/metadata_only_no_artifact_body_available`

## Invalid / Expected-Failure Cases

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

## Expected Category Counts

- `pass_metadata_only_no_file`: 5 cases
- `usage_error_no_write`: 8 cases
- `fail_closed_no_write`: 18 cases
- `input_error`: 0 cases
- `mismatch`: 0 cases

## Path Policy

The initial runtime mode is no manifest file writing. Valid cases use
`allow_manifest_file_writing=false`, do not expect manifest files, and do not
expect manifest output paths.

Unsafe path and overwrite cases use safe sentinel labels only. They do not
include private paths, absolute local paths, absolute temp paths, or resolved
output paths.

## Content Policy

The runtime result contract is metadata-only. Fixtures may use safe IDs, safe
reference IDs, safety flags, count summaries, and reason-code labels. They
must not include bodies, payloads, raw rows, logits, private paths, absolute
paths, raw learner text, performance proof, raw logs, or real participant
data.

Invalid cases use boolean sentinel flags and safe reason codes rather than
content values.

## No-Oracle / Synthetic-Only Policy

Synthetic, no-oracle, and non-proof notices are required except in their
specific expected-failure cases. Fixtures must not include final text,
observed-after text, gold labels, expected action payloads, scoring feedback
payloads, or real participant IDs.

## Relation To Static Manifest Writer Fixtures

The existing static manifest writer fixture root validates metadata index
fixture contracts. This runtime fixture root is separate and focuses on future
runtime request, pointer, and expected result contracts.

Do not merge the roots and do not infer runtime writer behavior from static
fixture validation.

## What These Fixtures Do Not Prove

These fixtures do not prove manifest writer correctness, manifest file output,
manifest validation, artifact writer CLI integration, model performance,
calibration quality, learner-state estimator correctness, real-data readiness,
or production readiness.

## Future Validator / Runtime Staging

A future runtime fixture validator should validate this root structure, schema
versions, case IDs, expected category counts, path-policy sentinels,
content-policy sentinels, reason-code contracts, and body-free summaries. It
should not execute a runtime writer or write manifest files.

Runtime writer implementation, Makefile targets, release-quality integration,
and remote markers remain separate future steps.

## Docs Safety

This README contains no JSON body examples, manifest body examples,
request/pointer body examples, artifact body payload examples, raw logs, or
private path examples.
