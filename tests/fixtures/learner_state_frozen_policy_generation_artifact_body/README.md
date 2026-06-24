# Frozen Policy Generation Artifact Body Fixtures

This fixture root contains synthetic-only, metadata-only, no-oracle contract
fixtures for future frozen policy generation artifact body generation.

These fixtures do not implement artifact body generation, do not implement a
validator, do not write artifact files, do not write manifest files, do not
generate manifest bodies, do not compute metrics, and do not prove real-data
or production readiness.

## Fixture Purpose

The fixtures define the future artifact body generation boundary before any
body generator is implemented. They describe safe valid metadata-only body
states and fail-closed invalid states using safe labels, booleans, counts,
reason codes, and schema names.

## Synthetic-Only / Metadata-Only / No-Oracle Boundary

The fixtures use only synthetic safe labels. They must not contain real
participant data, raw learner text, raw rows, logits, probabilities, private
paths, request bodies, pointer bodies, expected result bodies, generated
policy bodies, artifact body payloads, manifest bodies, or performance metric
bodies.

## File Layout

Each case contains:

- `artifact_body_request.json`
- `artifact_writer_result_pointer.json`
- `expected_artifact_body_result.json`

The files are fixture contract metadata only. This README intentionally does
not include JSON body examples.

## Valid Cases

- `valid/minimal_suppressed_metadata_only_body`
- `valid/safe_metadata_body_summary`
- `valid/safe_reason_code_body_summary`
- `valid/safe_validation_reference_body_summary`

Valid cases expect `validation_status=pass`, no reason codes, no failed
checks, safe metadata-only output, no raw rows, no logits, no private paths,
no performance claims, no request/pointer/expected bodies, no manifest body,
and no artifact or manifest file writing.

## Invalid Cases

- `invalid/raw_learner_text_in_artifact_body`
- `invalid/raw_rows_in_artifact_body`
- `invalid/logits_dump_in_artifact_body`
- `invalid/private_path_in_artifact_body`
- `invalid/performance_claim_in_artifact_body`
- `invalid/request_body_leakage`
- `invalid/pointer_body_leakage`
- `invalid/expected_result_body_leakage`
- `invalid/generated_policy_body_leakage`
- `invalid/manifest_body_leakage`
- `invalid/unsafe_artifact_body_schema`
- `invalid/missing_synthetic_notice`
- `invalid/missing_no_oracle_notice`
- `invalid/unknown_artifact_body_schema_version`

Invalid cases expect `validation_status=fail`, `body_status=fail_closed`, one
safe reason code, one failed check, body output suppressed, and no artifact or
manifest file writing.

## Safe Marker Policy

Invalid fixtures use safe marker booleans to indicate simulated unsafe
conditions. The unsafe payload itself must not appear in the fixture.

Allowed marker examples include:

- `raw_learner_text_marker_present`
- `raw_rows_marker_present`
- `logits_dump_marker_present`
- `private_path_marker_present`
- `performance_claim_marker_present`
- `request_body_marker_present`
- `pointer_body_marker_present`
- `expected_result_body_marker_present`
- `generated_policy_body_marker_present`
- `manifest_body_marker_present`
- `unsafe_schema_marker_present`
- `missing_synthetic_notice_marker_present`
- `missing_no_oracle_notice_marker_present`
- `unknown_schema_version_marker_present`

## Forbidden Payload Policy

The fixture root must not contain actual raw learner text, actual rows, actual
logits, actual probabilities, actual private paths, actual request bodies,
actual pointer bodies, actual expected result bodies, actual generated policy
bodies, actual artifact body payloads, actual manifest bodies, GitHub raw
logs, full job output, or performance metric bodies.

## Expected Aggregate Counts

- valid_cases: 4
- invalid_cases: 14
- total_cases: 18
- expected matched_cases: 18
- expected mismatched_cases: 0
- expected input_error_cases: 0
- expected JSON files: 54

## What This Does Not Test

These fixtures do not test artifact body generation correctness, artifact
writer implementation quality, manifest writer behavior, file writing,
generated policy quality, calibration quality, model performance, real-data
readiness, or production readiness.

## Future Validator Plan

A future validator should discover the 18 cases, check the three required
files per case, parse JSON, validate schema versions, check required fields,
scan safe marker flags, compare expected metadata results, scan for forbidden
body leakage, and emit a deterministic metadata-only aggregate summary.

The validator should not output request bodies, pointer bodies, expected
result bodies, artifact bodies, manifest bodies, raw rows, logits, private
paths, raw learner text, or performance metric bodies.

The future validator design is documented in:

`docs/frozen_policy_generation_artifact_body_fixture_validator_design.md`

That design is docs-only. It does not implement validator code, validator
CLI, Makefile targets, release-quality integration, artifact body generation,
file writing, metrics, real-data use, or production readiness claims.
