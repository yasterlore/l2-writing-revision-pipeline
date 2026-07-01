# Frozen Policy Generation Artifact Writer CLI Actual Invocation Runtime Update Design

## 1. Title

Frozen Policy Generation Artifact Writer CLI Actual Invocation Runtime Update
Design

## 2. Scope

This document is a design-only / planning-only runtime update design for a
future update to the Step489 artifact writer CLI integration runtime.

This step does not:

- implement runtime actual invocation
- implement artifact writer CLI actual invocation
- change Python code/tests
- change the Makefile
- change the release-quality wrapper
- change workflow files
- change fixture JSON
- implement artifact body generation integration
- implement manifest writer integration
- enable file writing
- prove production readiness, real-data readiness, or model performance

## 3. Prior Completed Chain

- Step489 implemented the initial metadata-only artifact writer CLI integration
  runtime module / CLI / focused tests.
- Step496 created the artifact writer CLI actual invocation boundary design.
- Step497 created the actual invocation fixture contract design.
- Step498 created the synthetic metadata-only actual invocation fixture root.
- Step499 created the fixture validator design.
- Step500 implemented the static fixture validator module / CLI / focused
  tests.
- Step501 created the Makefile target design.
- Step502 implemented the standalone fixture validator target.
- Step503 created the release-quality integration design.
- Step504 added the static fixture validator target to the release-quality
  wrapper.
- Step505 created the public-safe remote/manual run record workflow design.
- Step506 created the public-safe remote status marker.

Step506 records that the static fixture validator was included in a remote
Release Quality run and passed. It is not runtime actual invocation correctness
evidence.

## 4. Current Runtime Baseline

- module path: `python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_runtime.py`
- CLI path: `python -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime`
- current fixture root: `tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime`
- current target fixture case: `valid/valid_minimal_metadata_runtime_pass`
- runtime mode: `artifact_writer_cli_integration_runtime`
- runtime schema version: `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_v0.1`
- current release-quality status: included as metadata-only runtime smoke in
  the release-quality wrapper

Current summary baseline:

- `artifact_writer_cli_invoked: false`
- `artifact_writer_cli_invocation_planned: true`
- `artifact_body_generation_invoked: false`
- `manifest_writer_invoked: false`
- `file_writing_enabled: false`

The current runtime is metadata-only, body-free, and no-file-writing. It
returns a public-safe invocation plan summary and does not call the artifact
writer CLI.

## 5. Proposed Runtime Update Goal

The future runtime update should be limited to a safe metadata-only /
body-free actual invocation boundary.

Goals:

- call the existing artifact writer CLI only through a safe metadata-only /
  body-free boundary
- avoid outputting request / pointer / expected body content
- avoid outputting raw stdout/stderr body content
- avoid outputting artifact body payload, manifest body, or generated policy
  body
- avoid file writing
- avoid artifact body generation
- avoid manifest writer invocation
- preserve no-oracle, synthetic-only, and metadata-only constraints
- fail closed when unsafe output is detected
- keep output summary-only and public-safe

## 6. Candidate Invocation Target

Candidate module:

`python -m learner_state.frozen_policy_generation_artifact_writer`

Step507 does not call this module. The candidate already exists as a
metadata-only / body-free artifact writer runtime smoke target, but future
runtime integration correctness for actual invocation remains unproven.

## 7. Proposed Runtime Input Contract

Allowed future inputs:

- fixture root
- fixture case
- metadata-only request metadata path
- metadata-only pointer metadata path
- artifact writer CLI metadata path
- explicit actual invocation flag
- explicit dry-run / plan-only flag
- explicit summary-only flag
- explicit no-file-writing flag
- explicit synthetic-only flag
- explicit metadata-only flag
- explicit no-oracle flag

Forbidden future inputs:

- request body
- pointer body
- expected body
- raw learner text
- raw rows
- logits / probabilities
- private path
- absolute path
- final_text
- observed_after_text
- gold labels
- post-hoc annotation
- generated policy body
- artifact body payload
- manifest body
- raw stdout body
- raw stderr body
- file content payload
- scoring feedback payload

## 8. Proposed Runtime Modes

Future runtime modes:

- `plan_only`
  - preserves current behavior
  - `artifact_writer_cli_invoked=false`
  - `artifact_writer_cli_invocation_planned=true`
- `actual_invocation_metadata_only`
  - future behavior
  - `artifact_writer_cli_invoked=true`
  - `artifact_writer_cli_exit_code_category=zero` or `nonzero`
  - raw stdout/stderr body is suppressed
  - body-bearing output is scanned
  - `file_writing_enabled=false`

Step507 does not implement these mode changes.

## 9. Proposed Summary Schema Changes

Possible future summary fields:

- `runtime_actual_invocation_enabled`
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
- `invocation_mode`
- `summary_mode`

Schema version planning:

- current: `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_v0.1`
- proposed future: `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_v0.2`

Step507 does not change the schema.

## 10. Safety Scan Design

Future safety scan should detect:

- fixture JSON body in output
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
- final_text
- observed_after_text
- gold labels
- post-hoc annotation
- scoring feedback payload

Detection should fail closed. Output should include only safe reason codes and
public-safe aggregate fields.

## 11. Subprocess / Invocation Boundary

Future subprocess boundary:

- invoke a Python module only
- pass an explicit argument list
- use `shell=False`
- set a bounded timeout policy
- use a controlled working directory and relative path policy
- use a minimal environment policy
- capture stdout/stderr
- never print raw stdout/stderr
- scan captured stdout/stderr, then suppress raw bodies
- map exit code to `exit_code_category`
- parse JSON or key-value output only for approved safe fields
- fail closed on unsupported output format
- avoid inherited private path exposure
- avoid absolute path printing

Step507 does not implement subprocess behavior.

## 12. File-Writing / Residue Boundary

Future initial actual invocation runtime should preserve no-file-writing:

- no artifact body file writing
- no manifest file writing
- no generated policy body writing
- no output residue expected
- no tmp output expected from the actual invocation runtime
- any future file-writing option requires a separate design, fixture,
  validator, implementation, Makefile, release-quality, and remote status
  chain

## 13. Relationship To Existing Fixture Validator

- The Step500 fixture validator checks the static fixture contract.
- The fixture validator does not execute runtime actual invocation.
- A future runtime update should use the fixture contract as a safety boundary.
- Passing the fixture validator is prerequisite-like evidence for fixture
  quality, not proof of runtime actual invocation correctness.
- Runtime implementation must have its own focused tests and smoke checks.

## 14. Proposed Focused Tests For Future Runtime Update

Future tests should cover:

- plan-only mode preserves current summary
- actual invocation mode sets `artifact_writer_cli_invoked=true` only with an
  explicit flag
- actual invocation mode keeps `file_writing_enabled=false`
- actual invocation mode does not invoke artifact body generation
- actual invocation mode does not invoke manifest writer
- raw stdout body suppressed
- raw stderr body suppressed
- artifact body payload in subprocess output fail-closed
- manifest body in subprocess output fail-closed
- generated policy body in subprocess output fail-closed
- private / absolute path in subprocess output fail-closed
- request / pointer / expected body in subprocess output fail-closed
- unsupported output schema fail-closed
- nonzero exit code mapped safely
- timeout mapped safely
- root not found / fixture case not found usage_error
- deterministic summary
- no residue

## 15. Proposed CLI Changes For Future Runtime Update

Possible future flags:

- `--actual-invocation`
- `--plan-only`
- `--summary-only`
- `--no-file-writing`
- `--fail-closed-on-unsafe-output`
- `--artifact-writer-cli-module`
- `--timeout-seconds`

Step507 does not change the CLI.

## 16. Proposed Implementation Staging

Possible future staging:

1. Step508: runtime actual invocation fixture update design, if needed
2. Step509: runtime actual invocation implementation update
3. Step510: Makefile target update design
4. Step511: Makefile target update
5. Step512: release-quality integration design
6. Step513: release-quality wrapper integration
7. Step514: remote/manual run record workflow design
8. Step515: remote status marker

Step507 does not start these follow-up steps.

## 17. Failure Interpretation

Future runtime actual invocation failures should be interpreted narrowly:

- failure means the safe metadata-only subprocess boundary failed or returned a
  nonzero / unsafe output condition
- failure does not prove model performance issue
- failure does not prove artifact body generation issue unless artifact body
  generation is explicitly in scope
- failure does not prove manifest writer issue unless manifest writer is
  explicitly in scope
- failure must be interpreted through public-safe reason codes only
- raw stdout/stderr must not be copied into docs

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
- runtime update implemented

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

## 20. Step508 Runtime Fixture Update Design Status

Step508 adds the docs-only / planning-only fixture update design for adapting
the existing runtime fixture root to a future `actual_invocation_metadata_only`
mode:

[Frozen policy generation artifact writer CLI actual invocation runtime fixture update design](frozen_policy_generation_artifact_writer_cli_actual_invocation_runtime_fixture_update_design.md)

Step508 does not change fixture JSON, change fixture roots, update validators,
change Python code/tests, change Makefile, change the release-quality wrapper,
change workflow files, implement runtime actual invocation, perform artifact
writer CLI actual invocation, connect artifact body generation integration,
connect manifest writer integration, enable file writing, use real data,
compute metrics, or claim production readiness.

## 21. Step509 Runtime Fixture Root Update Status

Step509 expands the existing artifact writer CLI integration runtime fixture
root with 24 v0.2 synthetic metadata-only `actual_invocation_metadata_only`
cases. The root now contains 54 cases and 324 JSON files while preserving the
original 30 v0.1 plan-only cases.

Step509 does not update the fixture validator, implement runtime actual
invocation, perform artifact writer CLI actual invocation, change Python
code/tests, change Makefile, change the release-quality wrapper, change
workflow files, connect artifact body generation integration, connect manifest
writer integration, enable file writing, use real data, compute metrics, or
claim production readiness.

## 22. Step510 Validator Update Design Status

Step510 adds the docs-only / planning-only validator update design for future
v0.1/v0.2 validation of the Step509-expanded runtime fixture root:

[Frozen policy generation artifact writer CLI actual invocation runtime fixture validator update design](frozen_policy_generation_artifact_writer_cli_actual_invocation_runtime_fixture_validator_update_design.md)

Step510 does not update the validator, change Python code/tests, change
Makefile, change the release-quality wrapper, change workflow files, change
fixture JSON, implement runtime actual invocation, perform artifact writer CLI
actual invocation, connect artifact body generation integration, connect
manifest writer integration, enable file writing, use real data, compute
metrics, or claim production readiness.

## 23. Step511 Runtime Fixture Validator v0.2 Support Status

Step511 implements static validator v0.2 support for the Step509-expanded
runtime fixture root. The validator module / CLI / focused tests now validate
54 synthetic metadata-only cases / 324 JSON files across the v0.1 plan-only
and v0.2 actual-invocation metadata-only fixture schema families.

This remains static fixture validation only. Step511 does not implement
runtime actual invocation, perform artifact writer CLI actual invocation,
change fixture JSON, change Makefile target names, change the release-quality
wrapper, change workflows, connect artifact body generation integration,
connect manifest writer integration, enable file writing, use real data,
compute metrics, or claim production readiness.

## 24. Step512 Runtime Implementation Refinement Design Status

Step512 adds the docs-only / planning-only implementation refinement design
that narrows the future Step489 runtime implementation boundary for
`actual_invocation_metadata_only` mode:

[Frozen policy generation artifact writer CLI actual invocation runtime implementation refinement design](frozen_policy_generation_artifact_writer_cli_actual_invocation_runtime_implementation_refinement_design.md)

Step512 does not change Python code/tests, change Makefile, change the
release-quality wrapper, change workflows, change fixture JSON, implement
runtime actual invocation, perform artifact writer CLI actual invocation,
connect artifact body generation integration, connect manifest writer
integration, enable file writing, use real data, compute metrics, or claim
production readiness.

## 25. Step513 Runtime Actual Invocation Implementation Status

Step513 implements the explicit `actual_invocation_metadata_only` runtime
summary path in the Step489 runtime module. Plan-only remains the default.
Runtime schema v0.2 summaries are emitted only when `--actual-invocation` is
used, with stdout/stderr suppression, fail-closed sentinel handling, and
file-writing disabled. This does not connect artifact body generation
integration, connect manifest writer integration, change fixture JSON, change
Makefile, change the release-quality wrapper, change workflows, use real
data, compute metrics, or claim production readiness.

## 26. Step514 Makefile Target Design Status

Step514 adds a design-only / planning-only standalone Makefile target design
for a future `make` smoke over the Step513 explicit
`actual_invocation_metadata_only` runtime path. It does not change Makefile,
release-quality wrapper, workflows, Python code/tests, fixture JSON, runtime
implementation, artifact body generation integration, manifest writer
integration, file writing, real-data use, metric use, or production readiness
claims.

See
[Frozen policy generation artifact writer CLI actual invocation runtime Makefile target design](frozen_policy_generation_artifact_writer_cli_actual_invocation_runtime_makefile_target_design.md).

## 27. Step515 Makefile Target Implementation Status

Step515 implements the standalone Makefile target for the Step513 explicit
`actual_invocation_metadata_only` runtime smoke. The target runs
`valid/valid_actual_invocation_minimal_metadata_only` with
`--actual-invocation --summary-only --no-file-writing`. It is not added to the
release-quality wrapper in Step515 and does not change workflow files, Python
code/tests, fixture JSON, runtime implementation, artifact body generation
integration, manifest writer integration, file writing, real-data use, metric
use, or production readiness claims.

## 28. Step516 Release-Quality Integration Design Status

Step516 adds a design-only / planning-only release-quality integration design
for the Step515 standalone target:

[Frozen policy generation artifact writer CLI actual invocation runtime release-quality integration design](frozen_policy_generation_artifact_writer_cli_actual_invocation_runtime_release_quality_integration_design.md)

The design proposes future wrapper placement after the plan-only runtime smoke
and actual invocation fixture validation, and before the artifact body fixture
validation. Step516 does not change the release-quality wrapper, workflow
files, Makefile, Python code/tests, fixture JSON, runtime implementation,
artifact body generation integration, manifest writer integration, file
writing, real-data use, metric use, or production readiness claims.
