# Frozen Policy Generation Artifact Writer CLI Actual Invocation Design

## 1. Scope

This document is the Step496 design-only / planning-only document for a future
artifact writer CLI actual invocation boundary from the artifact writer CLI
integration runtime.

This document does not implement actual invocation, change Python code/tests,
change Makefile, change the release-quality wrapper, change workflow YAML,
change fixture JSON, connect artifact body generation integration, connect
manifest writer integration, implement file writing, generate manifest bodies,
generate policy bodies, or write output files.

This document is not production readiness evidence, real-data readiness
evidence, model performance evidence, F1 evidence, accuracy evidence, ECE
evidence, AURCC evidence, artifact writer CLI actual invocation correctness
evidence, artifact body generation integration correctness evidence, manifest
writer integration correctness evidence, generated policy quality evidence, or
learner-state estimator correctness evidence.

## 2. Prior Completed Chain

- Step489 implemented the initial metadata-only artifact writer CLI
  integration runtime module, CLI, and focused tests.
- Step490 created the docs-only runtime Makefile target design.
- Step491 implemented the standalone runtime Makefile target.
- Step492 created the runtime release-quality integration design.
- Step493 added the runtime smoke target to the release-quality wrapper.
- Step494 created the docs-only remote/manual run record workflow design.
- Step495 created the public-safe pass-only metadata-only body-free remote
  status marker for the runtime smoke wrapper check.

Step495 records remote wrapper inclusion and pass status for the current
metadata-only runtime smoke. It is not evidence that artifact writer CLI
actual invocation is correct.

Current runtime summary keeps:

- `artifact_writer_cli_invoked: false`
- `artifact_writer_cli_invocation_planned: true`
- `artifact_body_generation_invoked: false`
- `manifest_writer_invoked: false`
- `file_writing_enabled: false`

## 3. Actual Invocation Goal

The future actual invocation goal is limited to:

- calling the existing artifact writer CLI from the Step489 runtime only in
  metadata-only / body-free mode
- limiting artifact writer CLI output to a public-safe summary
- not passing, storing, or displaying artifact body payloads
- not passing, storing, or displaying manifest bodies
- not passing, storing, or displaying generated policy bodies
- not passing, storing, or displaying request, pointer, or expected bodies
- preserving no-oracle, synthetic-only, and metadata-only constraints
- failing closed if unsafe output is detected
- keeping file writing disabled

The future invocation should remain a narrow boundary check. It should not
expand into artifact body generation, manifest writer integration, production
file writing, or generated policy body generation.

## 4. Candidate Invocation Target

Candidate existing artifact writer CLI:

```bash
python -m learner_state.frozen_policy_generation_artifact_writer
```

Step496 does not run this command.

Current position of that CLI:

- metadata-only artifact writer runtime
- artifact body suppressed
- manifest body suppressed
- no file writing
- included in the release-quality wrapper as artifact writer runtime smoke

The future Step489 runtime update may call this CLI only if the invocation can
be constrained to body-free summary output and fail-closed safety scans.

## 5. Allowed Invocation Inputs

Future actual invocation may pass only metadata references and safe flags:

- metadata-only artifact writer request path
- metadata-only artifact writer pointer path
- fixture-derived relative paths
- safe mode flag
- summary mode flag
- synthetic-only flag
- metadata-only flag
- no-oracle flag
- file-writing disabled flag

The design permits field names and relative fixture references only. It does
not permit inline JSON body examples or raw payload examples in docs, tests, or
runtime output.

## 6. Forbidden Invocation Inputs

Future actual invocation must not pass:

- request body
- pointer body
- expected body
- raw learner text
- raw rows
- logits or probabilities
- `final_text`
- `observed_after_text`
- gold labels
- post-hoc annotation
- generated policy body
- artifact body payload
- manifest body
- written file JSON body
- private path
- absolute path
- full stdout or stderr body
- raw GitHub Actions logs
- full job output

Any detected body-bearing input, unsafe path, oracle-bearing field, or raw
content marker with an actual value should fail closed before invocation.

## 7. Invocation Output Boundary

Future actual invocation output should be limited to body-free summary fields:

- `status`
- `reason_code`
- `exit_code_category`
- `command_label`
- `summary_mode`
- `artifact_writer_cli_invoked`
- `artifact_writer_cli_exit_code_category`
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
- `file_writing_enabled`
- `artifact_body_generation_invoked`
- `manifest_writer_invoked`
- `production_readiness_claimed`
- `real_data_readiness_claimed`
- `performance_claims_present`

Future actual invocation output must not include:

- raw stdout
- raw stderr
- fixture body
- request body
- pointer body
- expected body
- artifact body payload
- manifest body
- generated policy body
- raw rows
- logits or probabilities
- raw learner text
- private or absolute path values

## 8. Safety Scan And Fail-Closed Design

After a future actual invocation, the runtime should safety-scan the command
result before emitting its own summary.

Fail-closed conditions include:

- CLI output contains a body-bearing field
- CLI output contains raw stdout or stderr body
- CLI output contains artifact body payload
- CLI output contains manifest body
- CLI output contains generated policy body
- CLI output contains raw learner text
- CLI output contains raw rows
- CLI output contains logits or probabilities
- CLI output contains private or absolute path values
- CLI unexpectedly writes files
- CLI invokes artifact body generation
- CLI invokes manifest writer
- CLI returns unsupported schema version
- CLI returns status or reason inconsistent with expected metadata-only pass

Failures should be represented by safe reason-code labels and body-free
summaries. The failing payload must not be copied into stdout, stderr, docs,
or test expectations.

## 9. File-Writing Boundary

Initial actual invocation should keep no-file behavior:

- no artifact body file writing
- no manifest file writing
- no generated policy body writing
- no output residue expected
- no tmp output expected
- any future file-writing option requires a separate design, fixture,
  validator, implementation, Makefile, release-quality, and remote status
  chain

Step496 does not design or implement file writing.

## 10. Runtime Summary Changes

Future actual invocation implementation may change or add runtime summary
fields:

- `artifact_writer_cli_invoked` may change from `false` to `true` only when
  safe actual invocation is explicitly enabled.
- `artifact_writer_cli_invocation_planned` may remain as a planning flag or be
  refined into an invocation state field.
- `artifact_writer_cli_exit_code_category` may be added to summarize the
  invoked CLI exit category without raw stdout or stderr.
- actual invocation safety-scan flags may be added for body-free output,
  path-safety, no-oracle, no-file-writing, and residue checks.

Step496 does not change the current runtime summary.

## 11. Relationship To Existing Checks

This design does not replace existing checks:

- artifact writer fixture validation
- artifact writer runtime smoke
- artifact writer CLI integration fixture validation
- artifact writer CLI integration runtime fixture validation
- artifact writer CLI integration runtime smoke
- artifact body fixture validation
- artifact body generation checks
- manifest writer checks
- release-quality wrapper
- Step495 remote status marker

The future actual invocation boundary would be an additional runtime boundary.
It should remain separate from artifact body generation integration and
manifest writer integration.

## 12. Proposed Future Fixture / Validator / Test Staging

Recommended future staging:

1. actual invocation fixture contract design
2. actual invocation fixture root creation
3. actual invocation fixture validator design
4. actual invocation fixture validator implementation
5. runtime implementation update design
6. runtime implementation update
7. Makefile target update design
8. Makefile target update
9. release-quality integration design
10. release-quality wrapper integration
11. remote/manual run record workflow design
12. remote status marker

Step496 does not start any of these implementation steps.

## 13. Proposed Focused Tests For Future Implementation

Future actual invocation implementation should add focused tests for:

- valid metadata-only actual invocation summary
- artifact writer CLI invoked flag true only when safe
- artifact writer CLI output body-free
- raw stdout and stderr not copied
- artifact body payload fail-closed
- manifest body fail-closed
- generated policy body fail-closed
- private or absolute path fail-closed
- no file writing
- no residue
- no artifact body generation invocation
- no manifest writer invocation
- CLI JSON output body-free
- CLI human output body-free
- deterministic summary

Tests should use synthetic-only metadata fixtures and controlled safety
sentinels. They should not include raw learner text, raw rows, body payloads,
private paths, absolute paths, or performance metric bodies.

## 14. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1, accuracy, ECE, or AURCC achievement
- artifact writer CLI actual invocation correctness
- artifact body generation integration correctness
- manifest writer integration correctness
- manifest body generation correctness
- generated policy quality
- learner-state estimator correctness
- completion of actual invocation implementation

## 15. Public-Safe Checklist

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
- no logits/probabilities
- no private paths
- no absolute paths
- no raw learner text
- no real participant data
- no performance claims
- no production readiness claims
- no real-data readiness claims

## 16. Step497 Fixture Contract Design Status

Step497 adds the docs-only / planning-only fixture contract design for a future
metadata-only body-free artifact writer CLI actual invocation fixture root:

[Frozen policy generation artifact writer CLI actual invocation fixture contract design](frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_contract_design.md)

The fixture contract design does not create a fixture root, create fixture
JSON, implement a validator, update the runtime, implement actual invocation,
change Python code/tests, change Makefile, change the release-quality wrapper,
change workflow files, connect artifact body generation integration, connect
manifest writer integration, write files, use real data, compute metrics, or
claim production readiness.

## 17. Step498 Fixture Root Creation Status

Step498 creates the synthetic metadata-only fixture root for the future actual
invocation fixture contract:

[Artifact writer CLI actual invocation fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation/README.md)

The root contains 32 case directories and 192 metadata-only JSON files. This
does not implement actual invocation, update the runtime, implement a
validator, change Python code/tests, change Makefile, change the
release-quality wrapper, change workflow files, connect artifact body
generation integration, connect manifest writer integration, enable file
writing, use real data, compute metrics, or claim production readiness.

## 18. Step499 Fixture Validator Design Status

Step499 adds the docs-only / planning-only validator design for the Step498
fixture root:

[Frozen policy generation artifact writer CLI actual invocation fixture validator design](frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validator_design.md)

The validator design does not implement a validator, change Python code/tests,
change Makefile, change the release-quality wrapper, change workflow files,
change fixture JSON, update runtime actual invocation, implement artifact
writer CLI actual invocation, connect artifact body generation integration,
connect manifest writer integration, enable file writing, use real data,
compute metrics, or claim production readiness.

## 19. Step500 Fixture Validator Implementation Status

Step500 implements the static validator module / CLI / focused tests for the
Step498 actual invocation fixture root:

- `python/learner_state/frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation.py`

The validator checks 32 cases / 192 JSON files and emits public-safe
summary-only output. It does not update runtime actual invocation, perform
artifact writer CLI actual invocation, change fixture JSON, change Makefile,
change the release-quality wrapper, change workflow files, connect artifact
body generation integration, connect manifest writer integration, enable file
writing, use real data, compute metrics, or claim production readiness.
