# Learner State Frozen Policy Generation Manifest Writer Production File Writing Fixtures

This fixture root contains synthetic-only, metadata-only fixtures for future
production-facing manifest writer file writing contract validation.

These fixtures are production-facing file writing contract fixtures only. They
do not implement runtime file writing, public `--manifest-out`, production
readiness, real-data readiness, artifact writer CLI integration, manifest body
generation, or model performance evaluation.

## Safety Policy

- synthetic-only
- metadata-only
- no real data
- no raw learner text
- no manifest body
- no artifact body payload
- no generated policy body
- no private paths
- no absolute paths
- no raw rows or logits
- stdout and stderr should remain body-free
- no production-readiness claim

## Expected Counts

- valid_cases: 8
- invalid_cases: 24
- total_cases: 32
- json_files_per_case: 5
- total_json_files: 160
- pass_written_cases: 7
- pass_no_write_cases: 1
- usage_error_cases: 12
- fail_closed_cases: 12
- matched_cases: 32
- mismatched_cases: 0
- input_error_cases: 0

## Required Files Per Case

Each case directory has exactly five JSON files:

- case_metadata.json
- manifest_writer_request.json
- artifact_writer_result_pointer.json
- artifact_body_generation_result_pointer.json
- expected_production_file_writing_result.json

## Case Categories

- pass_written
- pass_no_write
- usage_error
- fail_closed

## Safe Output Root Policy

Future validation should allow only safe relative manifest output paths under
`tmp/frozen_policy_generation_manifest/`. Invalid path cases use synthetic
sentinel identifiers only. Fixtures do not store real user paths, cloud paths,
private paths, or absolute temp paths.

## Stdout and Stderr Policy

Future runtime and validator output should be body-free and count-only. It
should not print written file bodies, manifest bodies, request bodies, pointer
bodies, expected result bodies, artifact body payloads, private paths, absolute
paths, raw learner text, raw rows, logits, or performance metric bodies.

## Overwrite Policy

Default behavior is no overwrite. Output exists without overwrite is a usage
error. The overwrite-allowed valid case remains metadata-only and must still be
inside the safe output root.

## Reason Code Categories

Usage-error cases cover unsafe manifest output paths, overwrite policy, and
symlink-sensitive path handling. Fail-closed cases cover manifest body request,
forbidden content leakage, write/parse/cleanup failure sentinels, unsupported
artifact writer CLI integration, and unsupported manifest writer mode.

## Future Staging

A future validator should parse this fixture root, check schema versions, case
ID consistency, category counts, safe output root policy, stdout/stderr
body-free expectations, public absolute path suppression, reason code matching,
and body-free summary output.

A later runtime implementation may use these fixtures to test opt-in
metadata-only manifest file writing. Release-quality integration should remain
separate. This fixture root does not implement validator logic, runtime file
writing, public `--manifest-out`, Makefile targets, or artifact writer CLI
integration.

## Step431 Fixture Creation

Step431 creates this 32-case / 160-JSON fixture root from the Step430 contract.
It does not implement production-facing runtime file writing, public
`--manifest-out`, a validator, Makefile target, release-quality integration,
artifact writer CLI integration, real-data use, metrics, or production
readiness.

## Step432 Future Validator Design

Step432 adds the docs-only production file writing fixture validator design:

[Frozen policy generation manifest writer production file writing fixture validator design](../../../docs/frozen_policy_generation_manifest_writer_production_file_writing_fixture_validator_design.md).

The future validator should statically check this fixture root for required
files, JSON parsing, schema versions, case ID consistency, category counts,
safe output root policy, overwrite policy, pointer safety, reason-code
matching, stdout/stderr body-free expectations, and public absolute path
suppression.

The design does not implement the validator, production-facing runtime file
writing, public `--manifest-out`, Makefile target, release-quality
integration, artifact writer CLI integration, real-data use, metrics, or
production readiness.
