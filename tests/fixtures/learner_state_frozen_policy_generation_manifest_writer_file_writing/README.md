# Learner State Frozen Policy Generation Manifest Writer File Writing Fixtures

This fixture root contains synthetic-only, metadata-only contract fixtures for
future manifest writer metadata-only file writing.

These fixtures are contract fixtures only. They do not prove runtime file
writing, production readiness, real-data readiness, artifact writer CLI
integration, manifest body generation, or model performance.

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
- no production-readiness claim

## Expected Counts

- valid_cases: 6
- invalid_cases: 33
- total_cases: 39
- json_files_per_case: 5
- total_json_files: 195
- pass_metadata_file_written_cases: 5
- pass_metadata_no_file_cases: 1
- usage_error_cases: 15
- fail_closed_cases: 18
- input_error_cases: 0
- mismatched_cases: 0

Step410 uses the revised Option A count from the contract design: missing
artifact writer result pointer and missing artifact body generation result
pointer are separate cases. This makes future validator behavior clearer.

## Required Files Per Case

Each case directory has exactly five JSON files:

- case_metadata.json
- manifest_writer_request.json
- artifact_writer_result_pointer.json
- artifact_body_generation_result_pointer.json
- expected_manifest_writer_file_writing_result.json

## Safe Root Policy

Future file writing is limited to metadata-only JSON under:

`tmp/frozen_policy_generation_manifest/`

Valid cases use safe relative JSON paths under that root. Invalid path cases
use synthetic sentinel metadata only. They do not contain real private paths,
absolute local paths, absolute temp paths, or user paths.

## Case Categories

- pass_metadata_file_written
- pass_metadata_no_file
- usage_error_no_write
- fail_closed_no_write

## Future Staging

The future validator should statically check required files, schema versions,
case ID consistency, category counts, safe path policy, content policy,
no-oracle notices, reason codes, summary counts, and body-free output.

Step411 adds the docs-only validator design for that future static checker.

Step412 implements the static fixture validator at:

`python/learner_state/frozen_policy_generation_manifest_writer_file_writing_fixture_validation.py`

The validator checks this 39-case / 195-JSON fixture root without writing
manifest files, running the runtime writer, running isolated write validation,
changing fixture JSON, adding a Makefile target, or adding release-quality
integration. Its summaries are body-free and count-only.

Step413 adds the docs-only Makefile target design for a future short command:

`check-learner-state-frozen-policy-generation-manifest-writer-file-writing-fixtures`

That target is not implemented in Step413. The fixture root remains unchanged
and the future target should only wrap the static validator CLI.

This fixture root does not execute runtime file writing, isolated writes,
`--manifest-out`, or artifact writer CLI integration.

A later isolated write validation step should perform actual writes only in an
isolated safe root, verify parseable JSON, verify forbidden field counts are
zero, and clean up residue.

The runtime currently remains metadata_only_no_file. This fixture root does
not implement --manifest-out or manifest file writing.
