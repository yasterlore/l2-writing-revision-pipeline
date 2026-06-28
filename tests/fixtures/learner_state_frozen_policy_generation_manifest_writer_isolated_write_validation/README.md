# Learner State Frozen Policy Generation Manifest Writer Isolated Write Validation Fixtures

This fixture root contains synthetic-only, metadata-only fixtures for future
manifest writer isolated write validation.

These fixtures are isolated write validation fixtures only. They do not prove
runtime file writing, production readiness, real-data readiness, artifact writer
CLI integration, manifest body generation, or model performance.

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
- no performance metric body
- stdout and stderr should remain body-free
- cleanup should leave residue count 0
- no production-readiness claim

## Expected Counts

- valid_cases: 6
- invalid_cases: 19
- total_cases: 25
- json_files_per_case: 6
- total_json_files: 150
- pass_written_cases: 5
- pass_no_write_cases: 1
- usage_error_cases: 14
- fail_closed_cases: 5
- matched_cases: 25
- mismatched_cases: 0
- input_error_cases: 0
- residue_file_count: 0

## Required Files Per Case

Each case directory has exactly six JSON files:

- case_metadata.json
- isolated_write_request.json
- manifest_writer_request.json
- artifact_writer_result_pointer.json
- artifact_body_generation_result_pointer.json
- expected_isolated_write_result.json

## Case Categories

- pass_written
- pass_no_write
- usage_error
- fail_closed

## Safe Isolated Root Policy

Future validation must write only inside a test-controlled isolated temporary
root. Valid cases use safe relative requested output paths. Invalid path cases
use synthetic sentinel identifiers only. Fixtures do not store real user paths,
real private paths, real cloud paths, or absolute temp paths.

## Stdout and Stderr Policy

Future validator output should be body-free and count-only. It should not print
written file bodies, manifest bodies, request bodies, pointer bodies, expected
result bodies, artifact body payloads, private paths, absolute paths, raw learner
text, raw rows, logits, or performance metric bodies.

## Cleanup and Residue Expectation

Future isolated write validation should remove isolated output after each case
and report residue count 0 for this fixture set.

## Reason Code Categories

Usage-error cases cover unsafe output path contracts, overwrite policy, expected
write missing, unexpected write, and parse-or-cleanup grouped failures.
Fail-closed cases cover manifest body request and forbidden content/body write
sentinel cases.

## Future Staging

A future validator should parse this fixture root, check schema versions, case ID
consistency, category counts, safe isolated root policy, stdout/stderr body-free
expectations, cleanup/residue expectations, reason code matching, and body-free
summary output.

Later runtime file writing support should be exercised only inside an isolated
safe root. Release-quality integration should remain separate. This fixture root
does not implement isolated write validation, runtime file writing,
`--manifest-out`, or artifact writer CLI integration.
