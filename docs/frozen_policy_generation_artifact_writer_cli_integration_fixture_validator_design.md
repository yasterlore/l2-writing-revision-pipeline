# Frozen Policy Generation Artifact Writer CLI Integration Fixture Validator Design

## 1. Purpose

This document fixes the docs-only validator design for the frozen policy
generation artifact writer CLI integration fixture root.

It is not validator implementation, Python test implementation, Makefile
target implementation, release-quality integration, workflow implementation,
artifact writer CLI integration runtime implementation, artifact body
generation CLI integration, manifest writer integration, manifest body
generation, real-data readiness, or production readiness.

The validator should be synthetic-only, metadata-only, no-oracle, body-free,
and public-safe. It may report names, counts, reason codes, schema names, and
boolean safety flags. It must not print fixture JSON bodies, request bodies,
pointer bodies, expected-result bodies, written file JSON bodies, manifest
bodies, artifact body payloads, generated policy bodies, raw rows,
logits/probabilities, private paths, absolute paths, raw learner text, raw
logs, or full job output.

## 2. Current State

- Step466 artifact writer CLI integration design exists.
- Step467 fixture contract design exists.
- Step468 fixture root exists:
  `tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration/`
- The fixture root contains 28 cases and 168 JSON files.
- The current fixture split is 6 pass cases, 9 usage-error cases, and 13
  fail-closed cases.
- The scope is generator scaffold CLI -> artifact writer CLI only.
- Artifact body generation CLI integration is not implemented.
- Manifest writer integration is not implemented.
- Manifest body generation is not implemented.
- Artifact writer CLI integration runtime is not implemented.
- Validator module does not exist yet.
- Focused validator tests do not exist yet.
- Makefile target does not exist yet.
- Release-quality integration does not exist yet.

## 3. Future Module / CLI

Future module:

- `python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_fixture_validation.py`

Future focused tests:

- `python/learner_state/tests/test_frozen_policy_generation_artifact_writer_cli_integration_fixture_validation.py`

Future CLI command:

- `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_fixture_validation`

Future CLI args:

- `--fixture-root`
- `--fixture-case`
- `--json`
- `--help`

Default root mode should validate the full fixture root. Case mode should
validate exactly one `valid/<case>` or `invalid/<case>` selector beneath the
fixture root. Human output should be body-free summary lines. JSON output
should be a parseable body-free summary object.

## 4. Validation Summary Schema

Future mode:

- `artifact_writer_cli_integration_fixture_validation`

Future validation schema:

- `learner_state_frozen_policy_generation_artifact_writer_cli_integration_fixture_validation_v0.1`

Expected root summary fields:

- `mode=artifact_writer_cli_integration_fixture_validation`
- `validation_schema_version=learner_state_frozen_policy_generation_artifact_writer_cli_integration_fixture_validation_v0.1`
- `total_cases=28`
- `valid_cases=6`
- `invalid_cases=22`
- `total_json_files=168`
- `json_files_per_case=6`
- `matched_cases=28`
- `mismatched_cases=0`
- `input_error_cases=0`
- `pass_cases=6`
- `usage_error_cases=9`
- `fail_closed_cases=13`
- `content_suppressed=true`
- `body_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_absolute_paths=true`
- `no_generated_policy_body=true`
- `no_artifact_body_payload=true`
- `no_manifest_body=true`
- `no_request_body=true`
- `no_pointer_body=true`
- `no_expected_body=true`
- `no_performance_claims=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `file_writing_checked=true`
- `artifact_body_generation_integration_checked=true`
- `manifest_writer_integration_checked=true`
- `artifact_writer_cli_integration_checked=true`
- `release_quality_ready=false`

The summary should also include safe reason-code counts for invalid cases, but
must not include fixture bodies or raw content.

## 5. Case Discovery Rules

The validator should:

- discover case directories only under `valid/` and `invalid/`
- require exactly 6 JSON files per case
- ignore the root `README.md`
- reject extra JSON files inside case directories
- reject missing required files
- reject unexpected case directories outside `valid/` and `invalid/`
- require total directory and JSON counts to match 28 and 168
- require `case_id` to match the relative selector, such as `valid/<case>`
- keep selectors relative and reject absolute or parent-traversing selectors

## 6. Required File Validation

Each case must contain exactly:

- `case_metadata.json`
- `generator_request.json`
- `generator_input_fixture_pointer.json`
- `artifact_writer_request.json`
- `generator_result_pointer.json`
- `expected_artifact_writer_cli_integration_result.json`

The validator should parse each file as JSON and fail closed on malformed JSON,
missing files, duplicate or extra files, and schema mismatch.

## 7. Schema And Identity Validation

The validator should check:

- known schema versions
- case metadata schema:
  `learner_state_frozen_policy_generation_artifact_writer_cli_integration_case_metadata_v0.1`
- expected result schema:
  `learner_state_frozen_policy_generation_artifact_writer_cli_integration_result_v0.1`
- `case_id` alignment with the relative path
- `case_group` alignment with `valid` or `invalid`
- `integration_step=generator_scaffold_to_artifact_writer`
- `mode=artifact_writer_cli_integration_fixture_validation`
- `expected_status` alignment with `integration_status`
- `expected_reason_codes` alignment between case metadata and expected result
- `release_quality_ready=false`

## 8. Valid Case Rules

Valid cases must have:

- `integration_status=pass`
- `expected_reason_codes=[]`
- `generator_scaffold_executed=true`
- `artifact_writer_executed=true`
- `artifact_body_generation_executed=false`
- `manifest_writer_executed=false`
- `generated_artifact_written=false`
- `artifact_file_written=false`
- `manifest_file_written=false`
- `written_file_count=0`
- `body_field_count=0` when present
- `raw_row_count=0`
- `logits_dump_count=0`
- `private_path_count=0`
- `performance_metric_count=0`
- `release_quality_ready=false`

## 9. Invalid Case Rules

Invalid cases must have:

- `integration_status=usage_error` or `integration_status=fail_closed`
- non-empty `expected_reason_codes`
- one expected reason code matching the case-name taxonomy
- `artifact_body_generation_executed=false`
- `manifest_writer_executed=false`
- `generated_artifact_written=false`
- `artifact_file_written=false`
- `manifest_file_written=false`
- `written_file_count=0`
- public counters at 0 for raw/body/path/performance content
- no raw body printed or exposed in summaries

The validator should count matched invalid expectations without executing the
integration runtime.

## 10. Reason Code Validation

Allowed reason codes:

- `missing_generator_request`
- `missing_generator_input_pointer`
- `missing_artifact_writer_request`
- `missing_generator_result_pointer`
- `malformed_generator_result_pointer`
- `unknown_generator_result_schema`
- `unvalidated_generator_result`
- `generated_policy_body_leakage`
- `artifact_body_payload_leakage`
- `manifest_body_leakage`
- `request_body_leakage`
- `pointer_body_leakage`
- `raw_rows_leakage`
- `logits_dump_leakage`
- `private_path_leakage`
- `absolute_path_leakage`
- `raw_learner_text_leakage`
- `performance_claim_in_artifact`
- `non_synthetic_input`
- `no_oracle_violation`
- `unsupported_file_writing_mode`
- `unsupported_artifact_body_generation_integration`

The validator should reject unknown reason codes, missing expected reason
codes for invalid cases, and reason-code/case-name mismatches.

## 11. Forbidden Content Scan

The validator should recursively scan JSON keys and values for forbidden
actual content while allowing controlled reason-code strings and controlled
safe marker booleans.

Forbidden actual content:

- raw learner text payload
- raw rows payload
- logits/probability dumps
- generated policy body payload
- artifact body payload
- manifest body payload
- request body payload
- pointer body payload
- expected body payload
- private path strings
- absolute local or temporary path strings
- performance metric body
- real participant markers
- final-text payload
- observed-after payload
- gold-label payload
- scoring feedback payload

The scan should be conservative, but it should distinguish safe reason-code
names from actual body or path payloads.

## 12. Safe Marker Policy

Allowed:

- controlled reason-code strings
- controlled marker booleans for invalid cases
- safe synthetic ids
- safe relative fixture references
- count-only fields
- boolean safety flags

Forbidden:

- actual body payloads
- actual absolute or private paths
- raw learner text examples
- copied request, pointer, expected, artifact, manifest, or generated policy
  bodies
- real participant data

## 13. No-Oracle Validation

The validator should require:

- `synthetic_only=true` or equivalent checked flag
- `no_oracle=true` or equivalent checked flag
- no observed-after fields or payloads
- no final corrected text payloads
- no gold labels
- no post-hoc annotation payloads
- no test tuning payloads
- no scoring feedback payloads

No-oracle validation is a metadata and forbidden-content check only. It is not
model evaluation and does not prove estimator correctness.

## 14. File-Writing Validation

The validator should require:

- `file_writing_expected=false` in case metadata
- `file_writing_allowed=false` in request metadata
- `generated_artifact_written=false`
- `artifact_file_written=false`
- `manifest_file_written=false`
- `written_file_count=0`

The `unsupported_file_writing_mode` invalid case should remain usage-error or
fail-closed metadata. The validator itself must write no files.

## 15. Artifact Body / Manifest Writer Separation Validation

The validator should require:

- `artifact_body_generation_expected=false`
- `artifact_body_generation_requested=false`
- `artifact_body_generation_executed=false`
- `manifest_writer_expected=false`
- `manifest_writer_requested=false`
- `manifest_writer_executed=false`

The `unsupported_artifact_body_generation_integration` invalid case documents
the boundary only. Manifest writer integration remains future work.

## 16. CLI Behavior

Human output:

- body-free summary lines only
- counts and flags only
- no fixture body
- no JSON body payload
- no raw path body
- no absolute or private paths

JSON output:

- parseable summary object
- no fixture body
- no raw content
- no private or absolute paths

Exit behavior:

- exit 0 when all selected cases match expected metadata
- exit nonzero for malformed root, missing files, extra files, count mismatch,
  unexpected pass/fail, forbidden content, schema mismatch, identity mismatch,
  reason-code mismatch, unsafe selector, or input error
- `--fixture-case` validates one case
- `--json` emits JSON summary
- `--help` explains args without fixture bodies

## 17. Test Plan For Future Implementation

Focused tests should cover:

- full root validation success
- single valid case validation
- single invalid case validation
- count summary matches 28 cases and 168 JSON files
- required file missing in a temp copy fails
- extra JSON file in a temp copy fails
- schema mismatch in a temp copy fails
- case-id mismatch in a temp copy fails
- reason-code mismatch in a temp copy fails
- forbidden body marker in a temp copy fails
- actual absolute path sentinel in a temp copy fails
- file-writing true in a temp copy fails
- artifact body generation true in a temp copy fails
- manifest writer true in a temp copy fails
- JSON output parseable
- help output
- no body printed

## 18. Relation To Release-Quality

Staging should remain:

- validator implementation first
- focused tests with temp-copy mutation cases
- standalone Makefile target design
- standalone Makefile target implementation
- release-quality integration design
- release-quality wrapper integration
- remote/manual run record workflow
- remote status marker

This validator should eventually be separate from existing artifact writer
fixture and runtime targets.

## 19. Docs Safety Policy

Docs may include:

- field names
- reason code names
- target names
- module names
- schema names
- counts
- safety flags

Docs must not include:

- JSON body examples
- raw logs
- full job output
- private or absolute path examples
- raw learner text examples
- written body examples
- artifact body payload examples
- generated policy body examples
- manifest body examples

## 20. What This Does Not Do

This design does not:

- implement the validator
- add Python tests
- modify fixture JSON
- add a Makefile target
- integrate release-quality
- modify workflow YAML
- implement artifact writer CLI integration runtime
- implement artifact body generation CLI integration
- implement manifest writer integration
- implement manifest body generation
- use real data
- compute metrics
- prove production readiness
- prove real-data readiness

## 21. Next Recommended Steps

- Step470 validator implementation
- Step471 Makefile target design
- Step472 Makefile target implementation
- Step473 release-quality integration design
- Step474 wrapper integration
- Step475 remote workflow design
- Step476 remote marker

## 22. Step470 Fixture Validator Implementation Status

Step470 implements the static validator module and focused tests:

- `python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_fixture_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_artifact_writer_cli_integration_fixture_validation.py`

The validator checks the Step468 fixture root only. It validates case
discovery, 6 required files per case, JSON parsing, schema and identity
alignment, expected status and reason-code alignment, valid and invalid case
rules, forbidden-content scans, no-oracle metadata, file-writing suppression,
and artifact body / manifest writer separation. It emits body-free summaries
for human and JSON output.

Step470 does not add a Makefile target, integrate release-quality, change
workflow YAML, change fixture JSON, implement artifact writer CLI integration
runtime, connect artifact body generation CLI, connect manifest writer
runtime, generate manifest bodies, use real data, compute metrics, or claim
production readiness.

## 23. Step471 Makefile Target Design Status

Step471 adds the docs-only standalone Makefile target design for running the
Step470 validator CLI from `make`:

[Frozen policy generation artifact writer CLI integration fixture validator Makefile target design](frozen_policy_generation_artifact_writer_cli_integration_fixture_validator_makefile_target_design.md)

The proposed target is
`check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-fixtures`.
It would validate the 28-case / 168-JSON fixture root through the existing
body-free validator CLI. Step471 does not modify the Makefile, integrate
release-quality, change workflow YAML, change Python code or tests, change
fixture JSON, implement runtime integration, use real data, compute metrics, or
claim production readiness.

## 24. Step472 Makefile Target Implementation Status

Step472 implements the standalone Makefile target:

`check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-fixtures`

The target invokes the Step470 validator CLI over the Step468 fixture root and
prints only the existing body-free validation summary. Step472 does not add the
target to release-quality, change workflow YAML, change Python code or tests,
change fixture JSON, implement runtime integration, use real data, compute
metrics, or claim production readiness.

## 25. Step473 Release-Quality Integration Design Status

Step473 adds the docs-only release-quality integration design for the
standalone target:

[Frozen policy generation artifact writer CLI integration fixture release-quality integration design](frozen_policy_generation_artifact_writer_cli_integration_fixture_release_quality_integration_design.md)

The design fixes the proposed label, command, insertion point, expected
body-free output, failure interpretation, relation to existing artifact writer
checks, artifact body / manifest writer separation, wrapper implementation
plan, and remote marker staging. Step473 does not change the wrapper, change
workflow YAML, change the Makefile, change Python code or tests, change fixture
JSON, implement runtime integration, use real data, compute metrics, or claim
production readiness.

## 26. Step474 Release-Quality Wrapper Integration Status

Step474 integrates the standalone Makefile target into the release-quality
wrapper after artifact writer fixture validation and artifact writer runtime
smoke, and before artifact body fixture validation.

The added wrapper label is
`release_quality_check: learner-state frozen policy generation artifact writer CLI integration fixture validation`.
The added command is
`make check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-fixtures`.

This keeps the validator as a static fixture-contract check. Step474 does not
change workflow YAML, change the Makefile, change Python code or tests, change
fixture JSON, implement runtime integration, connect artifact body generation
CLI, connect manifest writer runtime, use real data, compute metrics, or claim
production readiness.

## 27. Step475 Remote/Manual Run Record Workflow Design Status

Step475 adds the docs-only future remote/manual Release Quality recording
workflow for this static validator check:

[Frozen policy generation artifact writer CLI integration fixture release-quality remote run record workflow](frozen_policy_generation_artifact_writer_cli_integration_fixture_release_quality_remote_run_record_workflow.md)

The future status marker remains planned only. Step475 does not create the
marker, run remote workflows, change wrapper/workflow/Makefile/Python/test
code, change fixture JSON, implement runtime integration, use real data,
compute metrics, or claim production readiness.

## 28. Step476 Remote Status Marker Status

Step476 creates the public-safe pass-only / count-only marker for the remote
Release Quality run that included this validator check:

[Learner-state frozen policy generation artifact writer CLI integration fixture release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_writer_cli_integration_fixture_release_quality_remote_run_status.md)

The marker is status evidence for wrapper inclusion and static fixture
validation only. It is not evidence of artifact writer CLI integration runtime,
artifact body generation integration, manifest writer integration, model
performance, real-data readiness, or production readiness.
