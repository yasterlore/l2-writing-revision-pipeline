# Frozen Policy Generation Manifest Writer Production File Writing Fixture Release Quality Integration Design

## 1. Purpose

This document designs how the production-facing metadata-only manifest file
writing fixture validator target should be added to the future
`check-release-quality` wrapper.

It is a design only. It does not modify the release-quality wrapper, does not
change workflow YAML, does not change Makefile, does not change Python
code/tests, does not change fixture JSON, does not implement runtime file
writing, does not expose public `--manifest-out`, does not change the runtime
writer, does not connect artifact writer CLI, and does not claim production
readiness.

## 2. Current State

- The production file writing fixture root exists.
- The production file writing fixture validator module exists.
- Focused validator tests exist.
- The standalone Makefile target exists.
- Release-quality wrapper integration does not exist.
- Production-facing runtime file writing does not exist.
- Public `--manifest-out` is not implemented.
- Artifact writer CLI integration does not exist.

## 3. Wrapper Label

`release_quality_check: learner-state frozen policy generation manifest writer production file writing fixture validation`

## 4. Wrapper Command

`make check-learner-state-frozen-policy-generation-manifest-writer-production-file-writing-fixtures`

## 5. Recommended Insertion Point

Recommended insertion point:

- after `release_quality_check: learner-state frozen policy generation manifest writer isolated write validation`
- before `release_quality_check: config and scoring smoke checks`

Recommended manifest writer chain:

- manifest writer fixture validation
- manifest writer runtime fixture validation
- manifest writer runtime smoke
- manifest writer file writing fixture validation
- manifest writer isolated write validation
- manifest writer production file writing fixture validation
- config and scoring smoke checks

Reasoning:

- no-file runtime contract is checked before runtime smoke
- no-file runtime smoke confirms the current metadata-only runtime path
- broad static file-writing contract is checked before write-specific layers
- isolated temp-root write harness confirms validator-owned write behavior
- production/public-output-root static contract is checked after the isolated
  write harness, while still remaining separate from runtime implementation

This ordering makes the manifest writer safety boundary readable without
claiming production-facing runtime file writing readiness.

## 6. Expected Wrapper Output

The wrapper should expose only the target's body-free, count-only summary.
Expected fields:

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

Reason-code counts may be printed if they remain body-free and contain only
safe reason-code names and counts.

## 7. Expected Wrapper Behavior

- target pass lets release-quality continue
- target failure fails release-quality
- target does not execute the runtime writer
- target does not write manifest files
- target does not create `tmp/frozen_policy_generation_manifest` residue
- target does not implement or invoke public `--manifest-out`
- target does not execute artifact writer CLI
- target does not execute artifact body generation CLI

## 8. Failure Interpretation

Treat the following as release-quality failures:

- target exits nonzero
- `mismatched_cases > 0`
- `input_error_cases > 0`
- `total_cases != 32`
- `total_json_files != 160`
- pass-written, pass-no-write, usage-error, or fail-closed count mismatch
- required file missing
- malformed JSON
- schema mismatch
- case ID mismatch
- category mismatch
- reason code mismatch
- safe output root policy failure
- overwrite policy failure
- pointer policy failure
- content/body leakage check failure
- stdout/stderr body suppression failure
- public absolute path suppression failure
- artifact writer CLI integration disabled check failure
- runtime writer executed unexpectedly
- manifest file written unexpectedly
- `tmp/frozen_policy_generation_manifest` residue greater than zero
- raw, logit, private, absolute, body, or payload marker appears in public output

These failures are fixture-contract failures. They are not production-facing
runtime file writing failures, public `--manifest-out` failures, artifact
writer CLI integration failures, model performance failures, or production
readiness failures.

## 9. Log Safety

Allowed in release-quality output:

- label
- command
- mode
- validation schema version
- counts
- safety flags
- `release_quality_ready=false`
- body suppression flags
- `public_absolute_path_suppressed=true`
- `artifact_writer_cli_integration_checked=true`

Forbidden in release-quality output and docs:

- fixture JSON body
- case metadata body
- manifest writer request body
- artifact writer result pointer body
- artifact body generation result pointer body
- expected result body
- written file JSON body
- manifest body
- manifest JSON body
- artifact body payload
- generated policy body
- raw rows
- logits or probabilities
- private paths
- absolute local paths
- absolute temp paths
- raw learner text
- `final_text`
- `observed_after_text`
- gold labels
- scoring feedback payload
- real participant data
- performance metric body
- raw GitHub logs
- full job output

## 10. Relation To Existing Manifest Writer Release-Quality Chain

This target should fit after the existing manifest writer checks:

- static manifest writer fixture validation
- runtime manifest writer fixture validation
- runtime manifest writer smoke
- broad static file writing fixture validation
- isolated write validation

It adds a production/public-output-root-specific static fixture contract check
without changing the runtime behavior or public CLI surface.

## 11. Relation To Production-Facing Runtime File Writing

The target is static contract validation only.

Target success does not prove that runtime file writing works, does not prove
that public `--manifest-out` exists, does not prove production output root
safety at runtime, and does not prove production readiness.

## 12. Relation To Isolated Write Validation

Isolated write validation writes only to a validator-owned temporary root.

The production file writing fixture validator is static and writes nothing.
Both are separate safety layers. The production fixture validator can follow
isolated write validation in the wrapper because it extends the safety story
from temporary-root harness behavior to future project-controlled output root
contract integrity.

## 13. Relation To Existing Static File Writing Fixture Validator

The existing file writing fixture validator is a broad static contract check.
The production file writing fixture validator is specific to future
production/public-output-root behavior.

Both should remain separate release-quality labels. Neither is production
readiness evidence by itself.

## 14. Relation To Artifact Writer CLI Integration

The target should confirm fixture metadata indicates
`artifact_writer_cli_integration_requested=false`.

The target should not execute artifact writer CLI, should not execute artifact
body generation CLI, and should not embed payloads. Artifact writer CLI
integration remains separate.

## 15. Relation To Release-Quality Staging

Recommended future sequence:

- Step436 design only
- Step437 wrapper integration
- Step438 remote/manual run record workflow design
- Step439 remote/manual status marker
- runtime file writing implementation remains separate
- public `--manifest-out` implementation remains separate
- artifact writer CLI integration remains separate

## 16. Docs Safety Policy

Docs may include field names, count names, flags, reason-code names, target
names, labels, command names, and policy names.

Docs must not include JSON body examples, written file examples, raw logs,
private path examples, absolute local path examples, absolute temp path
examples, raw learner text, real participant data, or performance metric
bodies.

## 17. What This Does NOT Do

- does not modify the release-quality wrapper
- does not modify workflow YAML
- does not modify Makefile
- does not modify Python code/tests
- does not modify fixtures JSON
- does not implement runtime file writing
- does not implement public `--manifest-out`
- does not connect artifact writer CLI
- does not use real data
- does not compute metrics
- does not prove production readiness

## 18. Next Recommended Steps

- Step437 wrapper integration
- Step438 remote/manual run record workflow design
- Step439 status marker
- keep production runtime implementation separate
- keep public `--manifest-out` separate
- keep artifact writer CLI integration separate

## 19. Step436 Status

Step436 creates this docs-only release-quality integration design for the
production-facing metadata-only manifest file writing fixture validator
target. It fixes the future wrapper label, command, insertion point, expected
body-free output, failure interpretation, log safety, relationship to related
checks, staging, non-goals, and next steps.

Step436 does not modify the release-quality wrapper, workflow YAML, Makefile,
Python code/tests, fixture JSON, runtime writer behavior, public
`--manifest-out`, artifact writer CLI integration, real-data use, metrics, or
production readiness.

## 20. Step437 Wrapper Integration Status

Step437 implements the release-quality wrapper integration designed here. The
wrapper now runs:

`make check-learner-state-frozen-policy-generation-manifest-writer-production-file-writing-fixtures`

under the label:

`release_quality_check: learner-state frozen policy generation manifest writer production file writing fixture validation`

The section is placed after manifest writer isolated write validation and
before config/scoring smoke checks. It remains static fixture validation only:
it does not execute the runtime writer, write manifest files, expose public
`--manifest-out`, execute artifact writer CLI, execute artifact body
generation CLI, use real data, compute metrics, or claim production
readiness.

Step437 does not modify workflow YAML, Makefile, Python code/tests, fixture
JSON, runtime writer behavior, public `--manifest-out`, artifact writer CLI
integration, real-data use, metrics, or production readiness.

## 21. Step438 Remote Run Record Workflow Design

Step438 adds the docs-only remote/manual Release Quality run record workflow
for this wrapper integration:

[Frozen policy generation manifest writer production file writing fixture release-quality remote run record workflow](frozen_policy_generation_manifest_writer_production_file_writing_fixture_release_quality_remote_run_record_workflow.md).

The workflow design fixes the future status marker path, public-safe metadata
fields, metadata that must not be recorded, marker structure, pass-only /
count-only summaries, safety review, interpretation, and failure handling.

Step438 does not create a status marker, run GitHub Actions, modify workflow
YAML, modify the wrapper, modify Makefile, modify Python code/tests, modify
fixture JSON, implement runtime file writing, expose public `--manifest-out`,
connect artifact writer CLI, use real data, compute metrics, or claim
production readiness.

## 22. Step439 Remote Run Status Marker

Step439 creates the public-safe pass-only/count-only remote/manual Release
Quality status marker for this wrapper integration:

[Learner-state frozen policy generation manifest writer production file writing fixture release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_production_file_writing_fixture_release_quality_remote_run_status.md).

The marker records the successful remote run using only safe metadata and
count summaries. It does not copy raw logs, full job output, fixture JSON
bodies, request/pointer/expected-result bodies, written file bodies, manifest
bodies, artifact payloads, generated policy bodies, raw rows, logits, private
paths, absolute paths, raw learner text, real participant data, or performance
evidence. Runtime file writing, public `--manifest-out`, artifact writer CLI
integration, real-data readiness, and production readiness remain separate.
