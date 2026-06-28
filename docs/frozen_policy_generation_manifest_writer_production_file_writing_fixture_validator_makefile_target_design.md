# Frozen Policy Generation Manifest Writer Production File Writing Fixture Validator Makefile Target Design

## 1. Purpose

This document designs a future standalone Makefile target for running the
production-facing metadata-only manifest file writing fixture validator.

It is a design only. It does not implement a Makefile target, does not add
release-quality integration, does not implement production-facing runtime file
writing, does not expose public `--manifest-out`, does not change the runtime
writer, does not connect artifact writer CLI, and does not claim production
readiness.

The target is intended to be a thin wrapper around the Step433 static
validator CLI.

## 2. Current State

- The production file writing fixture root exists.
- The production file writing fixture validator module exists.
- The production file writing fixture validator CLI exists.
- Focused validator tests exist.
- The standalone Makefile target does not exist.
- Release-quality integration does not exist for this validator.
- Production-facing runtime file writing does not exist.
- Public `--manifest-out` is not implemented.
- Artifact writer CLI integration does not exist.

## 3. Target Name

`check-learner-state-frozen-policy-generation-manifest-writer-production-file-writing-fixtures`

## 4. Target Command

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer_production_file_writing_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_production_file_writing`

## 5. Help Text

`check-learner-state-frozen-policy-generation-manifest-writer-production-file-writing-fixtures  Validate manifest writer production metadata-only file writing fixture contracts`

## 6. Expected Target Output

The target should emit the validator's body-free, count-only human summary by
default. It should not pass `--json` by default.

Expected summary fields:

- `mode=manifest_writer_production_file_writing_fixture_validation`
- `validation_schema_version=learner_state_frozen_policy_generation_manifest_writer_production_file_writing_validation_v0.1`
- `total_cases=32`
- `valid_cases=8`
- `invalid_cases=24`
- `total_json_files=160`
- `json_files_per_case=5`
- `pass_written_cases=7`
- `pass_no_write_cases=1`
- `usage_error_cases=12`
- `fail_closed_cases=12`
- `matched_cases=32`
- `mismatched_cases=0`
- `input_error_cases=0`
- `content_suppressed=true`
- `manifest_body_suppressed=true`
- `no_written_file_body=true`
- `no_manifest_body=true`
- `no_manifest_json_body=true`
- `no_artifact_body_payload=true`
- `no_generated_policy_body=true`
- `no_request_body=true`
- `no_pointer_body=true`
- `no_expected_body=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_absolute_paths=true`
- `no_performance_claims=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `path_policy_checked=true`
- `overwrite_policy_checked=true`
- `stdout_stderr_policy_checked=true`
- `public_absolute_path_suppressed=true`
- `artifact_writer_cli_integration_checked=true`
- `release_quality_ready=false`

The output may include reason-code counts. It must not include fixture JSON
bodies, request bodies, pointer bodies, expected-result bodies, written file
bodies, manifest bodies, artifact body payloads, generated policy bodies, raw
rows, logits, private paths, absolute paths, raw learner text, or performance
metric bodies.

## 7. Expected Failure Behavior

The target should fail if:

- the validator exits nonzero
- any case mismatches
- a required file is missing
- JSON is malformed
- schema versions mismatch
- case IDs mismatch
- categories mismatch
- reason codes mismatch
- safe output root policy validation fails
- overwrite policy validation fails
- pointer policy validation fails
- content policy validation fails
- public absolute path suppression fails
- stdout/stderr body suppression fails
- artifact writer CLI integration disabled validation fails
- any body, payload, raw row, logit, private path, or absolute path marker
  appears in public output
- unexpected runtime file writing occurs
- `tmp/frozen_policy_generation_manifest` residue is created by the validator

Failure from this target is fixture-contract failure. It is not
production-facing runtime file writing failure, public `--manifest-out`
failure, artifact writer CLI integration failure, model performance failure,
or production readiness failure.

## 8. Relation To Current CLI

The Makefile target should be a wrapper around CLI root validation.

It should not add new behavior, should not pass `--json` by default, should
not execute the runtime writer, should not write manifest files, and should
not implement public `--manifest-out`.

## 9. Relation To Existing Static File Writing Fixture Validator

Existing target:

`check-learner-state-frozen-policy-generation-manifest-writer-file-writing-fixtures`

This existing target performs broad static file-writing contract validation
for manifest writer file-writing fixtures.

Proposed target:

`check-learner-state-frozen-policy-generation-manifest-writer-production-file-writing-fixtures`

The proposed target is more specific. It validates the future public
`--manifest-out` and project-controlled output root fixture contract.

Both are static validators. Neither proves production readiness.

## 10. Relation To Isolated Write Validation Target

The isolated write validation target writes minimal safe metadata inside a
validator-owned temporary root for pass-written cases, then parses, scans, and
cleans it up.

The proposed production file writing fixture validator target is static. It
does not write files. It checks future runtime contract metadata for
project-controlled output behavior.

Both targets should remain separate.

## 11. Relation To Existing Runtime Targets

The runtime fixture validation target validates no-file runtime fixture
contracts. The runtime smoke target executes the current no-file
metadata-only runtime.

The proposed production fixture validator target statically checks future file
writing contracts. None of these targets proves public `--manifest-out`
runtime implementation.

## 12. Relation To Release-Quality

This step does not add release-quality integration.

Two future insertion options:

- Option A: run the target after manifest writer isolated write validation and
  before config/scoring smoke checks.
- Option B: run the target before isolated write validation, immediately after
  manifest writer file writing fixture validation.

Recommended order is Option A:

- manifest writer file writing fixture validation
- manifest writer isolated write validation
- manifest writer production file writing fixture validation
- config and scoring smoke checks

Reasoning:

- broad static contract validation runs first
- isolated write validation confirms the temp-root harness behavior
- production-specific static contract validation then records the future
  project-controlled output root contract
- the manifest writer file-writing readiness chain remains grouped before
  config/scoring checks

This ordering still does not imply production-facing runtime file writing
readiness.

## 13. Relation To Production-Facing Runtime File Writing

Public `--manifest-out` remains unimplemented. Production-facing runtime file
writing remains unimplemented.

Target success would prove only that the production file writing fixture
contract is internally consistent. It would not prove production file output
readiness.

## 14. Docs Safety

Docs may list target name, command, help text, expected counts, summary field
names, safety flags, reason-code names, and policy names.

Docs must not include fixture JSON bodies, written file JSON bodies, manifest
bodies, artifact body payloads, request bodies, pointer bodies,
expected-result bodies, raw logs, full job output, private path examples,
absolute path examples, raw learner text, or performance metric bodies.

## 15. Future Implementation Tests

Future Step435 should verify:

- `make help` shows the target
- the target exits `0`
- expected counts are 32 / 160 and 7 / 1 / 12 / 12
- output is body-free
- `public_absolute_path_suppressed=true`
- `artifact_writer_cli_integration_checked=true`
- focused production fixture validator tests still pass
- full unittest still passes
- `tmp/frozen_policy_generation_manifest` residue is `0`
- Makefile diff is limited to help text and target
- wrapper and workflow diffs are empty
- Python code/tests diffs are empty
- fixture JSON diffs are empty

## 16. What This Does NOT Do

- does not implement the Makefile target
- does not integrate release-quality
- does not modify workflow
- does not implement runtime file writing
- does not implement public `--manifest-out`
- does not connect artifact writer CLI
- does not use real data
- does not compute metrics
- does not prove production readiness

## 17. Next Recommended Steps

- Step435 Makefile target implementation
- Step436 release-quality integration design
- Step437 wrapper integration
- Step438 remote marker
- keep runtime file writing implementation separate
- keep public `--manifest-out` implementation separate
- keep artifact writer CLI integration separate

## 18. Step434 Status

Step434 creates this docs-only Makefile target design for the production-facing
metadata-only manifest file writing fixture validator. It fixes the proposed
target name, command, help text, expected output, failure behavior,
relationship to current CLI and related targets, release-quality staging,
docs safety, and future implementation tests.

Step434 does not modify Makefile, release-quality wrapper, workflow YAML,
Python code/tests, fixture JSON, runtime writer behavior, public
`--manifest-out`, artifact writer CLI integration, real-data use, metrics, or
production readiness.

## 19. Step435 Implementation Status

Step435 implements the standalone Makefile target:

`check-learner-state-frozen-policy-generation-manifest-writer-production-file-writing-fixtures`

The target is a thin wrapper around production file writing fixture validator
CLI root validation:

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer_production_file_writing_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_production_file_writing`

The target emits the body-free, count-only human summary by default and does
not pass `--json`. It validates the 32-case / 160-JSON fixture root and
reports `matched_cases=32`, `input_error_cases=0`,
`public_absolute_path_suppressed=true`,
`artifact_writer_cli_integration_checked=true`, and
`release_quality_ready=false`.

Step435 does not add release-quality wrapper integration, change workflow
YAML, change Python code/tests, change fixture JSON, implement
production-facing runtime file writing, expose public `--manifest-out`, change
the runtime writer, connect artifact writer CLI, use real data, compute
metrics, or claim production readiness.

## 20. Step436 Release-Quality Integration Design Status

Step436 adds the docs-only release-quality integration design for this
standalone target:

[Frozen policy generation manifest writer production file writing fixture release-quality integration design](frozen_policy_generation_manifest_writer_production_file_writing_fixture_release_quality_integration_design.md).

The design recommends adding the target after manifest writer isolated write
validation and before config/scoring smoke checks in a later wrapper step. It
does not modify the release-quality wrapper, workflow YAML, Makefile, Python
code/tests, fixture JSON, runtime writer behavior, public `--manifest-out`,
artifact writer CLI integration, real-data use, metrics, or production
readiness.

## 21. Step437 Release-Quality Wrapper Integration Status

Step437 adds the standalone target to the release-quality wrapper after
manifest writer isolated write validation and before config/scoring smoke
checks.

The Makefile target itself remains unchanged. The wrapper integration does not
change workflow YAML, Python code/tests, fixture JSON, runtime writer behavior,
public `--manifest-out`, artifact writer CLI integration, real-data use,
metrics, or production readiness.

## 22. Step438 Remote Run Record Workflow Design Status

Step438 adds the docs-only remote/manual Release Quality run record workflow
for the production file writing fixture validator wrapper integration:

[Frozen policy generation manifest writer production file writing fixture release-quality remote run record workflow](frozen_policy_generation_manifest_writer_production_file_writing_fixture_release_quality_remote_run_record_workflow.md).

The Makefile target remains unchanged. Step438 does not create a status
marker, modify workflow YAML, modify the release-quality wrapper, modify
Makefile, modify Python code/tests, modify fixture JSON, execute runtime file
writing, write manifest files, expose public `--manifest-out`, connect
artifact writer CLI, use real data, compute metrics, or prove production
readiness.
