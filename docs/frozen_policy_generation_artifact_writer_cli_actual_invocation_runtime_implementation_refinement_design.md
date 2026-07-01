# Frozen Policy Generation Artifact Writer CLI Actual Invocation Runtime Implementation Refinement Design

## 1. Scope

This document is the Step512 design-only / planning-only refinement for a
future implementation update to the Step489 runtime module:

`python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_runtime.py`

It refines how a later step should add an
`actual_invocation_metadata_only` mode after the Step509 fixture expansion and
Step511 validator v0.2 support.

Step512 does not:

- implement runtime actual invocation
- implement artifact writer CLI actual invocation
- change Python code/tests
- change Makefile targets
- change the release-quality wrapper
- change workflows
- change fixture JSON
- connect artifact body generation integration
- connect manifest writer integration
- enable file writing
- prove production readiness, real-data readiness, or model performance

## 2. Prior Completed Chain

- Step489 implemented the initial artifact writer CLI integration runtime
  module / CLI / focused tests with plan-only, metadata-only, body-free,
  no-file-writing behavior.
- Step507 created the runtime update design for a future
  `actual_invocation_metadata_only` mode.
- Step508 created the runtime fixture update design.
- Step509 expanded the existing runtime fixture root to 54 cases / 324 JSON
  files by adding 24 v0.2 synthetic metadata-only actual invocation cases.
- Step510 created the validator update design for mixed v0.1/v0.2 fixture
  validation.
- Step511 implemented static runtime fixture validator v0.2 support.

Step511 validates fixture contracts only. It does not prove runtime actual
invocation correctness, artifact writer CLI actual invocation correctness, or
downstream generation/writer correctness.

## 3. Current Runtime Implementation Baseline

- module path:
  `python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_runtime.py`
- focused tests:
  `python/learner_state/tests/test_frozen_policy_generation_artifact_writer_cli_integration_runtime.py`
- current CLI arguments:
  - `--fixture-root`
  - `--fixture-case`
  - `--request-metadata`
  - `--pointer-metadata`
  - `--artifact-writer-cli-metadata`
  - `--json`
- current runtime schema:
  `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_v0.1`
- current default behavior: plan-only / no actual invocation
- current supported fixture behavior: v0.1 metadata-only runtime fixture
  summaries
- current supported fixture fields include metadata-only request, pointer,
  artifact writer CLI, expected summary, and expected error metadata from the
  existing runtime fixture layout
- current no-invocation summary boundary:
  - `artifact_writer_cli_invoked=false`
  - `artifact_writer_cli_invocation_planned=true`
  - `artifact_body_generation_invoked=false`
  - `manifest_writer_invoked=false`
  - `file_writing_enabled=false`
- current no-file-writing behavior: no artifact body, manifest, generated
  policy, or output file writing is enabled
- current Makefile / release-quality relationship: the existing runtime smoke
  and fixture validation chain remains separate from future actual invocation
  runtime work

## 4. Implementation Goal For The Next Step

The next implementation step should add an explicit
`actual_invocation_metadata_only` mode to the Step489 runtime module while
preserving plan-only as the default.

The implementation goal is limited to:

- enable actual invocation path only when an explicit flag requests it
- call the candidate artifact writer CLI module through a metadata-only,
  body-free subprocess boundary
- capture raw stdout/stderr without printing them directly
- parse and summarize approved safe fields only
- fail closed on unsafe output, unsupported output, ambiguous output, timeout,
  or unsafe fixture metadata
- emit public-safe summary-only runtime output
- keep file writing disabled
- avoid artifact body generation
- avoid manifest writer invocation

## 5. Proposed CLI Changes

Future CLI flags:

- `--actual-invocation`
- `--plan-only`
- `--summary-only`
- `--no-file-writing`
- `--fail-closed-on-unsafe-output`
- `--artifact-writer-cli-module`
- `--timeout-seconds`

Design policy:

- default mode remains `--plan-only`
- `--actual-invocation` is required for the metadata-only invocation path
- `--no-file-writing` remains required or default-true in actual invocation
  mode
- unsafe output fails closed
- default artifact writer CLI module is
  `learner_state.frozen_policy_generation_artifact_writer`

Step512 does not change the CLI.

## 6. Proposed Fixture Selection Behavior

- v0.1 plan-only cases keep the current behavior and v0.1 summary shape.
- v0.2 valid actual invocation cases map to
  `actual_invocation_metadata_only` behavior.
- v0.2 invalid cases map to public-safe `fail_closed`, `usage_error`, or
  `mismatch` summaries.
- runtime selection reads fixture `runtime_mode` and `invocation_mode`
  metadata.
- CLI flag / fixture mode contradictions should return `usage_error` or
  `fail_closed`.
- fixture bodies must never be printed.

## 7. Proposed Subprocess Implementation Boundary

Future actual invocation should use a narrow subprocess boundary:

- use `subprocess.run` or an equivalent controlled API
- use `shell=False`
- build an explicit argument list
- set a timeout
- use a controlled environment
- use a cwd policy that does not expose private path values in public output
- capture stdout/stderr
- never print raw stdout/stderr directly
- scan captured stdout/stderr for forbidden content before any parsing
- parse only approved safe key-value or JSON summary fields
- fail closed on unsupported output schema
- map nonzero exit code to a safe `exit_code_category`
- map timeout to a safe timeout category
- map subprocess exceptions to safe reason codes

## 8. Candidate Artifact Writer CLI Command Shape

Candidate module:

`python -m learner_state.frozen_policy_generation_artifact_writer`

Candidate safe argument categories:

- metadata-only request metadata path
- metadata-only pointer metadata path
- summary-only flag if supported
- no-file-writing flag if supported
- mode flag if supported

The implementation step must inspect the existing artifact writer CLI argument
contract before wiring the command. Step512 does not invoke or implement this
command.

## 9. Proposed Summary Schema v0.2

Proposed future runtime schema:

`learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_v0.2`

Add or update summary fields:

- `runtime_actual_invocation_enabled`
- `invocation_mode`
- `summary_mode`
- `artifact_writer_cli_invoked`
- `artifact_writer_cli_invocation_planned`
- `artifact_writer_cli_exit_code_category`
- `artifact_writer_cli_output_scanned`
- `artifact_writer_cli_output_body_free`
- `raw_stdout_body_suppressed`
- `raw_stderr_body_suppressed`
- `artifact_body_payload_detected`
- `manifest_body_detected`
- `generated_policy_body_detected`
- `request_body_detected`
- `pointer_body_detected`
- `expected_body_detected`
- `file_writing_detected`
- `runtime_actual_invocation_safety_scan_passed`
- `runtime_actual_invocation_fail_closed`
- `artifact_body_generation_invoked`
- `manifest_writer_invoked`
- `file_writing_enabled`
- `production_readiness_claimed`
- `real_data_readiness_claimed`
- `performance_claims_present`

Step512 does not change the schema.

## 10. Safety Scan Implementation Design

Future safety scanning must detect these forbidden categories without copying
offending values into output:

- fixture JSON body
- request body
- pointer body
- expected body
- written file JSON body
- manifest body
- artifact body payload
- generated policy body
- raw stdout body
- raw stderr body
- raw rows
- logits / probabilities
- private path values
- absolute path values
- raw learner text
- real participant data
- performance metric body
- `final_text`
- `observed_after_text`
- gold labels
- post-hoc annotation
- scoring feedback payload

Detection output must be limited to:

- safe reason code
- suppressed-content flags
- `fail_closed` or `usage_error` status

## 11. Valid Actual Invocation Expected Behavior

Future v0.2 valid case behavior:

- `valid_actual_invocation_minimal_metadata_only`: pass
- `valid_actual_invocation_body_free_output`: pass
- `valid_actual_invocation_nonzero_exit_safe_summary`: safe summary as
  designed, with nonzero exit category body-free
- `valid_actual_invocation_timeout_safe_summary`: safe summary as designed,
  with timeout category body-free
- `valid_actual_invocation_file_writing_disabled`: pass with
  `file_writing_enabled=false`
- `valid_actual_invocation_no_downstream_invocation`: pass with
  `artifact_body_generation_invoked=false` and `manifest_writer_invoked=false`

If nonzero or timeout behavior cannot be safely exercised through a real
subprocess in the implementation step, the implementation should use a
metadata-only simulated boundary or fail-closed plan rather than exposing raw
subprocess output.

## 12. Invalid Actual Invocation Expected Behavior

Future v0.2 invalid case behavior:

- raw stdout body sentinel -> `fail_closed`
- raw stderr body sentinel -> `fail_closed`
- artifact body payload sentinel -> `fail_closed`
- manifest body sentinel -> `fail_closed`
- generated policy body sentinel -> `fail_closed`
- request / pointer / expected body sentinel -> `fail_closed`
- private / absolute path sentinel -> `fail_closed`
- raw learner text / raw rows / logits sentinel -> `fail_closed`
- file writing detected sentinel -> `fail_closed`
- artifact body generation invoked sentinel -> `fail_closed`
- manifest writer invoked sentinel -> `fail_closed`
- unsupported schema -> `usage_error`
- mismatched expected status -> `mismatch`

## 13. Focused Tests For The Next Implementation Step

Future focused tests should cover:

- plan-only v0.1 behavior unchanged
- actual invocation flag required
- actual invocation mode returns schema v0.2
- valid actual invocation cases pass
- nonzero exit safe summary case handled
- timeout safe summary case handled
- raw stdout/stderr body fail-closed
- artifact body payload fail-closed
- manifest body fail-closed
- generated policy body fail-closed
- request / pointer / expected body fail-closed
- private / absolute path fail-closed
- raw learner text / raw rows / logits fail-closed
- file writing detected fail-closed
- downstream invocation sentinels fail-closed
- unsupported schema usage_error
- mismatched expected status mismatch
- CLI output body-free
- no residue
- deterministic summary

## 14. Makefile / Release-Quality Implications

The next implementation step should not change Makefile targets or the
release-quality wrapper.

Future separate steps may design:

- a mode-specific runtime smoke target for actual invocation metadata-only mode
- release-quality integration for that target
- wrapper integration
- remote/manual run record workflow
- remote status marker

## 15. Implementation Guardrails

The implementation step must preserve these guardrails:

- no fixture JSON mutation
- no committed generated outputs
- no tmp residue
- no raw subprocess output in test failure messages
- no private / absolute path values in public output
- no artifact body / manifest body / generated policy body printing
- no production readiness claims
- no performance claims
- fail closed on ambiguous output
- preserve current plan-only behavior

## 16. Proposed Next Implementation Step

Candidate next step:

Step513: runtime actual invocation implementation update

Expected files to change in Step513:

- `python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_runtime.py`
- `python/learner_state/tests/test_frozen_policy_generation_artifact_writer_cli_integration_runtime.py`
- related README / docs / full technical specification docs

Expected files not to change in Step513:

- fixture JSON
- Makefile
- release-quality wrapper
- workflows
- artifact body generation code
- manifest writer code

## 17. Failure Interpretation

Future runtime actual invocation implementation failure means the safe
metadata-only runtime boundary failed. Causes may include unsafe subprocess
output, nonzero exit, timeout, unsupported schema, or fixture mismatch.

Failure does not prove:

- model performance issue
- artifact body generation issue unless that scope is explicitly enabled
- manifest writer issue unless that scope is explicitly enabled

Raw stdout/stderr must not be copied into docs or reports.

## 18. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- artifact writer CLI actual invocation correctness
- runtime actual invocation correctness
- artifact body generation integration correctness
- manifest writer integration correctness
- generated policy quality
- learner-state estimator correctness
- runtime implementation updated

## 19. Public-Safe Checklist

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
- no raw stdout/stderr body
- no raw rows
- no logits/probabilities
- no private paths
- no absolute paths
- no raw learner text
- no real participant data
- no performance claims
- no production readiness claims
- no real-data readiness claims

## 20. Step513 Runtime Implementation Status

Step513 implements the next-step runtime update described by this refinement
design. The runtime module keeps plan-only as the default and adds explicit
`--actual-invocation` / `actual_invocation_metadata_only` support with runtime
schema `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_v0.2`.

The implementation adds public-safe CLI flags, stdout/stderr capture and
suppression, sentinel-driven fail-closed summaries, timeout/nonzero safe
summary categories, and no-file-writing metadata checks. It does not change
fixture JSON, Makefile targets, release-quality wrapper scripts, workflows,
artifact body generation integration, manifest writer integration, generated
policy body generation, artifact body file writing, manifest file writing,
real-data use, metric use, or production readiness claims.

## 21. Step514 Makefile Target Design Status

Step514 adds a design-only / planning-only standalone Makefile target design
for running the Step513 explicit `actual_invocation_metadata_only` runtime
smoke:

[Frozen policy generation artifact writer CLI actual invocation runtime Makefile target design](frozen_policy_generation_artifact_writer_cli_actual_invocation_runtime_makefile_target_design.md)

Step514 does not change Makefile, release-quality wrapper, workflows, Python
code/tests, fixture JSON, runtime implementation, artifact body generation
integration, manifest writer integration, file writing, real-data use, metric
use, or production readiness claims.

## 22. Step515 Makefile Target Implementation Status

Step515 implements the standalone Makefile target
`check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-runtime`
for the Step513 explicit `actual_invocation_metadata_only` runtime smoke over
`valid/valid_actual_invocation_minimal_metadata_only`. The target remains
standalone and is not added to the release-quality wrapper in Step515.

Step515 does not change workflow files, Python code/tests, fixture JSON,
runtime implementation, artifact body generation integration, manifest writer
integration, file writing, real-data use, metric use, or production readiness
claims.

## 23. Step516 Release-Quality Integration Design Status

Step516 adds a design-only / planning-only release-quality integration design
for adding the Step515 standalone target to a future wrapper:

[Frozen policy generation artifact writer CLI actual invocation runtime release-quality integration design](frozen_policy_generation_artifact_writer_cli_actual_invocation_runtime_release_quality_integration_design.md)

The design proposes a future wrapper label, command, and insertion point only.
It does not change the release-quality wrapper, workflow files, Makefile,
Python code/tests, fixture JSON, runtime implementation, artifact body
generation integration, manifest writer integration, file writing, real-data
use, metric use, or production readiness claims.

## 24. Step517 Release-Quality Wrapper Integration Status

Step517 adds the Step515 standalone target to `scripts/check_release_quality.sh`
with label
`release_quality_check: learner-state frozen policy generation artifact writer CLI actual invocation runtime smoke`
and command
`make check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-runtime`.
The block is placed after static actual invocation fixture validation and
before artifact body fixture validation. Step517 does not change workflow
files, Makefile, Python code/tests, fixture JSON, runtime implementation,
artifact body generation integration, manifest writer integration, file
writing, real-data use, metric use, or production readiness claims.

## 25. Step518 Remote Run Record Workflow Design Status

Step518 adds the docs-only / public-safe remote/manual run record workflow
design for the Step517 wrapper check:

[Frozen policy generation artifact writer CLI actual invocation runtime release-quality remote run record workflow](frozen_policy_generation_artifact_writer_cli_actual_invocation_runtime_release_quality_remote_run_record_workflow.md)

It defines future status marker fields and interpretation rules for a later
remote/manual Release Quality record. It does not create a remote status
marker, change workflow files, change the wrapper, change Makefile, change
Python code/tests, change fixture JSON, change runtime implementation,
connect artifact body generation integration, connect manifest writer
integration, enable file writing, use real data, compute metrics, or claim
production readiness.

## 26. Step519 Remote Status Marker Status

Step519 creates the public-safe pass-only metadata-only body-free remote run
status marker for the Step517 wrapper check:

[Learner-state frozen policy generation artifact writer CLI actual invocation runtime release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation_runtime_release_quality_remote_run_status.md)

It records the selected synthetic fixture case runtime summary and public-safe
remote run metadata only. It does not change runtime implementation, Python
code/tests, workflow files, the wrapper, Makefile, fixture JSON, artifact body
generation integration, manifest writer integration, file writing, real-data
use, metric use, or production readiness claims.
