# Frozen Policy Generation Artifact Writer CLI Integration Runtime Implementation Design

## 1. Scope

This document is the Step488 design-only / planning-only implementation design
for a future artifact writer CLI integration runtime.

Step489 implements the initial Python runtime module, CLI, and focused tests
described by this design. The implementation does not change the Makefile,
change the release-quality wrapper, change workflow YAML, change fixture JSON,
connect artifact body generation integration, connect manifest writer
integration, write files, or generate manifest bodies.

This document is not production readiness evidence, real-data readiness
evidence, model performance evidence, F1 evidence, accuracy evidence, ECE
evidence, AURCC evidence, artifact writer CLI integration runtime correctness
evidence, artifact body generation integration correctness evidence, manifest
writer integration correctness evidence, generated policy quality evidence, or
learner-state estimator correctness evidence.

## 2. Prior Completed Chain

- Step477 created the artifact writer CLI integration runtime boundary design.
- Step478 created the runtime fixture contract design.
- Step479 created the synthetic metadata-only runtime fixture root.
- Step480 created the runtime fixture validator design.
- Step481 implemented the static runtime fixture validator module, CLI, and
  focused tests.
- Step482 created the standalone Makefile target design.
- Step483 implemented the standalone Makefile target for static fixture
  validation.
- Step484 created the release-quality integration design.
- Step485 added the static runtime fixture validator target to the
  release-quality wrapper.
- Step486 created the public-safe remote/manual run record workflow design.
- Step487 created the public-safe pass-only/count-only remote/manual status
  marker for the Step485 wrapper check.

Step487 records wrapper inclusion and static fixture validation only. It is
not evidence that artifact writer CLI integration runtime behavior is correct.

## 3. Runtime Implementation Goal

The future runtime should provide a narrow metadata-only boundary between
generator scaffold CLI output or request metadata and the artifact writer CLI
boundary.

The goal is limited to:

- connecting generator scaffold CLI output or request metadata to the artifact
  writer CLI boundary through a safe runtime boundary
- calling or planning the artifact writer CLI only in metadata-only /
  summary-only mode
- avoiding body payload loading, storage, and display
- avoiding request, pointer, and expected body transfer
- avoiding generated policy body, artifact body payload, and manifest body
  transfer
- preserving no-oracle, synthetic-only, and metadata-only constraints
- returning a public-safe summary
- failing closed when prohibited fields, strings, paths, or body-bearing output
  are detected

## 4. Proposed Module and CLI

Future module candidate:

`python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_runtime.py`

Future CLI candidate:

`python -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime`

Step489 creates this module and CLI as an initial standalone metadata-only
runtime boundary.

## 5. Proposed Runtime Inputs

Allowed input categories:

- request metadata path
- pointer metadata path
- artifact writer CLI metadata path
- summary mode
- safe mode
- validation schema version
- relative fixture path
- file-writing disabled flag
- suppression policy
- no-oracle policy
- synthetic-only flag
- metadata-only flag

Forbidden input categories:

- request body
- pointer body
- expected body
- raw learner text
- raw rows
- logits or probabilities
- final text fields
- observed-after text fields
- gold labels
- post-hoc annotation
- generated policy body
- artifact body payload
- manifest body
- absolute path
- private path
- raw stdout or stderr body

The future runtime should accept metadata references only. It should not accept
inline body-bearing content.

## 6. Proposed Runtime Outputs

Allowed output fields:

- `mode`
- `runtime_schema_version`
- `status`
- `reason_code`
- `exit_code_category`
- `case_id`
- `command_label`
- `summary_mode`
- `content_suppressed`
- `body_suppressed`
- `no_raw_rows`
- `no_logits_dump`
- `no_private_paths`
- `no_absolute_paths`
- `no_generated_policy_body`
- `no_artifact_body_payload`
- `no_manifest_body`
- `no_request_body`
- `no_pointer_body`
- `no_expected_body`
- `no_oracle_checked`
- `synthetic_only_checked`
- `metadata_only_checked`
- `file_writing_enabled`
- `runtime_executed`
- `artifact_writer_cli_invoked`
- `artifact_body_generation_invoked`
- `manifest_writer_invoked`
- `production_readiness_claimed`
- `real_data_readiness_claimed`
- `performance_claims_present`

Outputs should be JSON serializable, body-free, deterministic, and public-safe.

## 7. Proposed Runtime Flow

The future implementation should follow this flow:

1. Parse CLI arguments.
2. Load metadata-only request, pointer, and artifact writer CLI metadata files.
3. Validate schema versions.
4. Validate safe fields and prohibited field absence.
5. Validate relative path policy.
6. Confirm file writing is disabled by default.
7. Build an artifact writer CLI invocation plan as a metadata-only summary.
8. Optionally call an existing artifact writer CLI only in safe
   metadata-only summary mode if a later step explicitly approves that
   behavior.
9. Suppress body content from all outputs.
10. Return a public-safe runtime summary.
11. Fail closed on prohibited fields, unsafe paths, unsafe strings, or unsafe
    command output.
12. Ensure no output residue remains after failure.

Step489 keeps the call in step 8 disabled and returns a metadata-only
invocation plan summary instead.

## 8. Artifact Writer CLI Invocation Boundary

If a later implementation invokes the artifact writer CLI, the boundary should
be:

- default implementation avoids artifact body generation
- artifact writer CLI call is metadata-only
- stdout and stderr summaries are body-free
- raw command output is not copied into docs or public summaries
- command result is summarized by status, reason code, counts, and safety flags
  only
- generated policy body, artifact body payload, and manifest body do not cross
  the boundary
- unsafe command output fails closed

This boundary does not replace existing artifact writer fixture validation,
artifact writer runtime smoke, or artifact writer CLI integration fixture
validation.

## 9. File-Writing Boundary

Initial future implementation should keep file writing disabled by default:

- no file writing by default
- no artifact body file writing
- no manifest file writing
- no generated policy body writing
- no output residue expected
- any future file-writing option requires a separate design, fixture,
  validator, implementation, Makefile, release-quality, and remote status
  chain

Step489 does not implement file writing.

## 10. Error and Fail-Closed Design

Future runtime should fail closed or return a safe usage error for:

- missing required metadata file
- malformed JSON metadata
- unsupported schema version
- case ID mismatch
- forbidden field detected
- forbidden string detected
- raw learner text marker with actual value
- raw rows, logits, or probabilities detected
- private or absolute path detected
- final text, observed-after text, or gold label detected
- generated policy body detected
- artifact body payload detected
- manifest body detected
- file writing requested unexpectedly
- runtime invocation would create residue
- unsafe artifact writer CLI output detected

Errors should be public-safe and should not include body-bearing values.

## 11. Relationship to Existing Validators and Fixtures

Step488 designs a future runtime implementation target. It does not replace:

- Step479 runtime fixture root
- Step481 runtime fixture validator
- Step483 standalone Makefile target
- Step485 release-quality wrapper integration
- Step487 remote status marker
- existing artifact writer fixture validator
- existing artifact writer runtime smoke
- artifact writer CLI integration fixture validator
- artifact body generation checks
- manifest writer checks

The existing runtime fixture validation chain remains a static contract
validation chain. Future runtime implementation work should use that chain as
guardrails, not as a substitute for focused runtime tests.

## 12. Proposed Focused Tests for Future Implementation

Future implementation tests should cover:

- valid minimal metadata runtime summary
- valid suppressed artifact writer summary
- valid relative fixture path
- file-writing disabled default
- no-oracle flags maintained
- forbidden request body fails closed
- forbidden pointer body fails closed
- forbidden artifact body payload fails closed
- forbidden manifest body fails closed
- forbidden generated policy body fails closed
- raw learner text fails closed
- raw rows or logits fail closed
- private or absolute path fails closed
- unsupported schema fails closed
- unsafe artifact writer CLI output fails closed
- CLI human output is body-free
- CLI JSON output is body-free
- deterministic summary
- no runtime output residue
- no artifact body generation invocation
- no manifest writer invocation

These tests should remain synthetic-only and metadata-only.

## 13. Proposed Implementation Staging

Suggested future staging after Step490:

- Step491: runtime CLI Makefile target implementation
- Step492: runtime release-quality integration design
- Step493: runtime release-quality wrapper integration
- Step494: remote/manual run record workflow design
- Step495: remote status marker

Step489 stops at the standalone runtime module, CLI, and focused tests.
Step490 adds only the docs-only Makefile target design.

## 14. Non-Claims

This document does not claim:

- production readiness
- real-data readiness
- model performance
- F1, accuracy, ECE, or AURCC achievement
- artifact writer CLI integration runtime correctness
- artifact body generation integration correctness
- manifest writer integration correctness
- generated policy quality
- learner-state estimator correctness
- Makefile runtime target
- release-quality runtime wrapper integration

## 16. Step489 Implementation Status

Step489 implements:

- `python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_runtime.py`
- `python/learner_state/tests/test_frozen_policy_generation_artifact_writer_cli_integration_runtime.py`
- CLI entrypoint:
  `python -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime`
- runtime schema version:
  `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_v0.1`
- mode: `artifact_writer_cli_integration_runtime`

The implementation is standalone and metadata-only. It returns public-safe
runtime summaries, keeps file writing disabled, does not invoke artifact body
generation, does not invoke manifest writer, does not generate manifest
bodies, does not generate policy bodies, and does not connect to Makefile or
release-quality runtime wrapper checks yet.

## 16.1 Step490 Makefile Target Design Status

Step490 adds the docs-only standalone Makefile target design for the Step489
runtime CLI:

[Frozen policy generation artifact writer CLI integration runtime Makefile target design](frozen_policy_generation_artifact_writer_cli_integration_runtime_makefile_target_design.md)

The design proposes the target name, command, help text, safe output
expectations, exit-code interpretation, no-file-writing policy, and
release-quality staging. It does not modify Makefile, change the wrapper,
change workflow YAML, change Python code/tests, change fixture JSON, invoke
artifact writer CLI actual downstream behavior, connect artifact body
generation integration, connect manifest writer integration, implement file
writing, or claim production readiness.

## 17. Public-Safe Checklist

- no raw logs
- no full job output
- no copied GitHub log blocks
- no screenshots containing raw logs
- no fixture JSON body
- no request body
- no pointer body
- no expected body
- no written file JSON body
- no manifest body
- no artifact body payload
- no generated policy body
- no raw rows
- no logits or probabilities
- no private paths
- no absolute paths
- no raw learner text
- no real participant data
- no performance claims
- no production readiness claims
- no real-data readiness claims
