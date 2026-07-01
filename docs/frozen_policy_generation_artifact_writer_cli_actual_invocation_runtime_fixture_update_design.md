# Frozen Policy Generation Artifact Writer CLI Actual Invocation Runtime Fixture Update Design

## 1. Title

Frozen Policy Generation Artifact Writer CLI Actual Invocation Runtime Fixture
Update Design

## 2. Scope

This document is a design-only / planning-only fixture update design for
adapting the existing artifact writer CLI integration runtime fixture root to a
future `actual_invocation_metadata_only` mode.

This step does not:

- change fixture JSON
- change the fixture root
- change the fixture validator
- implement runtime actual invocation
- implement artifact writer CLI actual invocation
- change Python code/tests
- change the Makefile
- change the release-quality wrapper
- change workflow files
- implement artifact body generation integration
- implement manifest writer integration
- enable file writing
- prove production readiness, real-data readiness, or model performance

## 3. Prior Completed Chain

- Step489 implemented the initial artifact writer CLI integration runtime
  module / CLI / focused tests.
- Step496 created the artifact writer CLI actual invocation boundary design.
- Step497 created the actual invocation fixture contract design.
- Step498 created the synthetic metadata-only actual invocation fixture root.
- Step499 created the actual invocation fixture validator design.
- Step500 implemented the static actual invocation fixture validator module /
  CLI / focused tests.
- Step502 implemented the standalone Makefile target for the static validator.
- Step504 added the static validator target to the release-quality wrapper.
- Step506 created the public-safe remote status marker for that static
  validator wrapper check.
- Step507 created the runtime update design for a future metadata-only actual
  invocation boundary.

Step507 is a runtime update design. It does not prove runtime actual
invocation correctness.

## 4. Current Runtime Fixture Baseline

Current fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime/`

Current aggregate counts:

- total cases: 30
- valid cases: 6
- invalid cases: 24
- JSON files per case: 6
- total JSON files: 180

Current case files:

- `case_metadata.json`
- `request_metadata.json`
- `pointer_metadata.json`
- `artifact_writer_cli_metadata.json`
- `expected_runtime_summary.json`
- `expected_error.json`

Current runtime schema version:

- `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_v0.1`

Current expected runtime summary baseline:

- `artifact_writer_cli_invoked=false`
- `artifact_writer_cli_invocation_planned=true`
- `artifact_body_generation_invoked=false`
- `manifest_writer_invoked=false`
- `file_writing_enabled=false`

Current fixture coverage is plan-only / no-invocation. The existing validator
checks static fixture metadata, required files, expected status / reason-code
alignment, body-suppression flags, path safety markers, no-oracle flags, and
deterministic aggregate counts. The existing release-quality chain includes
the static runtime fixture validator and the current runtime smoke, but neither
performs artifact writer CLI actual invocation.

## 5. Proposed Update Strategy

The proposed fixture update strategy is:

- extend the existing runtime fixture root in a backward-compatible way
- preserve v0.1 plan-only cases without changing their expected behavior
- add new actual-invocation-mode cases under a future schema version candidate
- consider `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_v0.2`
  for new fields
- update the fixture validator later so it can validate both v0.1 and v0.2
  cases
- keep existing Makefile and release-quality checks stable through staged
  updates

Step508 does not change fixture JSON.

## 6. Proposed Fixture Root Option

Option A extends the existing root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime/`

Option B creates a new root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_actual_invocation/`

Comparison:

- backward compatibility: Option A keeps plan-only and future actual
  invocation cases in one runtime contract; Option B separates them but adds a
  second root lifecycle.
- validator complexity: Option A requires mixed v0.1 / v0.2 schema support;
  Option B requires an additional validator root or selector path.
- release-quality stability: Option A can evolve the existing validator target
  carefully; Option B likely needs a new target and wrapper staging.
- fixture count clarity: Option A shows the full runtime contract in one root;
  Option B makes actual invocation counts easier to read independently.
- implementation risk: Option A has more schema-compatibility risk; Option B
  has more orchestration and documentation drift risk.
- future runtime CLI clarity: Option A aligns with a single runtime fixture
  root; Option B can make mode-specific CLI smoke selection clearer.

Recommended option: Option A. The existing root should be extended
backward-compatibly so the runtime fixture contract remains unified, while v0.1
plan-only cases stay unchanged and v0.2 actual invocation cases are added in a
separate future step.

## 7. Proposed Case Taxonomy

Proposed valid actual invocation cases:

- `valid_actual_invocation_minimal_metadata_only`
- `valid_actual_invocation_body_free_output`
- `valid_actual_invocation_nonzero_exit_safe_summary`
- `valid_actual_invocation_timeout_safe_summary`
- `valid_actual_invocation_file_writing_disabled`
- `valid_actual_invocation_no_downstream_invocation`

Proposed invalid / fail-closed actual invocation cases:

- `invalid_actual_invocation_raw_stdout_body`
- `invalid_actual_invocation_raw_stderr_body`
- `invalid_actual_invocation_artifact_body_payload`
- `invalid_actual_invocation_manifest_body`
- `invalid_actual_invocation_generated_policy_body`
- `invalid_actual_invocation_request_body`
- `invalid_actual_invocation_pointer_body`
- `invalid_actual_invocation_expected_body`
- `invalid_actual_invocation_private_path`
- `invalid_actual_invocation_absolute_path`
- `invalid_actual_invocation_raw_learner_text`
- `invalid_actual_invocation_raw_rows`
- `invalid_actual_invocation_logits`
- `invalid_actual_invocation_file_writing_detected`
- `invalid_actual_invocation_artifact_body_generation_invoked`
- `invalid_actual_invocation_manifest_writer_invoked`
- `invalid_actual_invocation_unsupported_schema`
- `invalid_actual_invocation_mismatched_expected_status`

Invalid cases must use metadata-only sentinels. They must not store actual
body payloads, raw content, private path values, absolute path values, or
performance metric bodies.

## 8. Proposed Aggregate Count Strategy

Option A count strategy:

- keep the existing 30 v0.1 cases
- add 24 v0.2 actual invocation cases
- proposed additional valid cases: 6
- proposed additional invalid cases: 18
- proposed future total: 54 cases
- proposed future JSON files per case: 6, if the current layout is preserved
- proposed future total JSON files: 324, if the current layout is preserved

Option B count strategy:

- keep the existing 30-case root unchanged
- create a separate actual invocation runtime-specific root
- proposed separate-root cases: 24 or 30
- proposed separate-root JSON count depends on the chosen file layout

Recommendation: use Option A with 24 additional cases as the first future
fixture update. These numbers are design values only. Step508 creates no files
and changes no fixture JSON.

## 9. Proposed Case Files

Current six-file layout:

- `case_metadata.json`
- `request_metadata.json`
- `pointer_metadata.json`
- `artifact_writer_cli_metadata.json`
- `expected_runtime_summary.json`
- `expected_error.json`

Possible additional files:

- `actual_invocation_metadata.json`
- `subprocess_boundary_metadata.json`
- `expected_actual_invocation_summary.json`

Six-file layout option:

- extend `request_metadata.json` with runtime mode and invocation request
  metadata
- extend `artifact_writer_cli_metadata.json` with subprocess and output
  suppression metadata
- extend `expected_runtime_summary.json` with actual invocation summary fields
- preserve existing file-count expectations

Additional-file option:

- separate actual invocation and subprocess metadata into dedicated files
- improve local readability for future actual invocation cases
- require validator, fixture count, Makefile, and release-quality updates to
  account for a changed per-case file count

Recommended option: preserve the existing six-file layout for the first future
fixture update. Add dedicated files only if v0.2 fields become too dense for
the existing metadata files.

## 10. Proposed Runtime Request Fields

Possible future request metadata fields:

- `runtime_mode`
- `actual_invocation_requested`
- `plan_only`
- `summary_only`
- `no_file_writing`
- `fail_closed_on_unsafe_output`
- `artifact_writer_cli_module`
- `timeout_seconds`
- `subprocess_shell_enabled`
- `stdout_capture_enabled`
- `stderr_capture_enabled`
- `stdout_body_printed`
- `stderr_body_printed`

Forbidden request metadata fields:

- request body
- pointer body
- expected body
- raw stdout body
- raw stderr body
- artifact body payload
- manifest body
- generated policy body
- raw rows
- logits
- private path
- absolute path
- raw learner text

## 11. Proposed Expected Summary Fields

Possible future `expected_runtime_summary.json` fields:

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

## 12. Sentinel Policy

Future invalid cases must use metadata-only sentinels.

Sentinel policy:

- actual raw stdout/stderr body must not be stored
- actual request/pointer/expected body must not be stored
- actual artifact body payload, manifest body, or generated policy body must
  not be stored
- private / absolute path string values must not be stored
- raw learner text, raw rows, and logits must not be stored
- valid cases must not contain forbidden sentinels
- sentinels must be allowed only in expected invalid cases

## 13. Fixture Validator Update Implications

A future fixture validator update should include:

- v0.2 schema support
- backward compatibility for v0.1 cases
- aggregate count updates
- new actual invocation mode checks
- subprocess boundary metadata checks
- output body suppression checks
- stdout/stderr suppression checks
- no-file-writing checks
- downstream boundary checks
- reason-code count updates
- deterministic traversal
- root error handling

Step508 does not change the validator.

## 14. Runtime Implementation Implications

A future runtime actual invocation implementation should require:

- explicit actual invocation flag
- default plan-only behavior
- `shell=False` subprocess boundary
- timeout handling
- stdout/stderr capture and suppression
- safe field parsing
- fail-closed handling for unsafe output
- exit-code category mapping
- no file writing
- no downstream artifact body generation or manifest writer invocation
- summary schema v0.2 consideration

## 15. Makefile / Release-Quality Implications

Future Makefile / release-quality implications:

- the existing static fixture validator target remains unchanged unless the
  fixture root or per-case file layout changes
- the runtime smoke target may need a new mode-specific target for actual
  invocation metadata-only behavior
- release-quality integration should be a separate design step
- wrapper integration should be a separate implementation step
- remote/manual run record workflow and status marker should be separate steps

## 16. Proposed Follow-Up Steps

Possible follow-up staging:

1. Step509: runtime actual invocation fixture root update
2. Step510: runtime actual invocation fixture validator update design
3. Step511: runtime actual invocation fixture validator update implementation
4. Step512: runtime actual invocation implementation design refinement, if
   needed
5. Step513: runtime actual invocation implementation update
6. Step514: Makefile target design
7. Step515: Makefile target implementation
8. Step516: release-quality integration design
9. Step517: release-quality wrapper integration
10. Step518: remote/manual run record workflow design
11. Step519: remote status marker

Step508 does not start these follow-up steps.

## 17. Failure Interpretation

Future fixture update failure means a fixture contract or metadata consistency
problem.

Future runtime actual invocation failure means the safe metadata-only
subprocess boundary failed or returned an unsafe / nonzero / timeout summary.
It does not prove a model performance issue. It does not prove an artifact
body generation issue unless artifact body generation is explicitly in scope.
It does not prove a manifest writer issue unless manifest writer integration is
explicitly in scope.

Raw stdout/stderr must not be copied into docs.

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
- fixture update implementation

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

## 20. Step509 Fixture Root Update Status

Step509 applies the recommended Option A fixture-root update by adding 24 v0.2
synthetic metadata-only `actual_invocation_metadata_only` cases to the existing
runtime fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime/`

Updated fixture counts:

- total cases: 54
- existing v0.1 plan-only cases: 30
- additional v0.2 actual invocation metadata-only cases: 24
- valid cases: 12
- invalid cases: 42
- JSON files per case: 6
- total JSON files: 324

Step509 does not update the fixture validator, implement runtime actual
invocation, perform artifact writer CLI actual invocation, change Python
code/tests, change Makefile, change the release-quality wrapper, change
workflow files, connect artifact body generation integration, connect manifest
writer integration, enable file writing, use real data, compute metrics, or
claim production readiness.

## 21. Step510 Validator Update Design Status

Step510 adds the docs-only / planning-only validator update design for future
v0.1/v0.2 validation of the 54-case / 324-JSON runtime fixture root:

[Frozen policy generation artifact writer CLI actual invocation runtime fixture validator update design](frozen_policy_generation_artifact_writer_cli_actual_invocation_runtime_fixture_validator_update_design.md)

Step510 does not update the validator, change Python code/tests, change
Makefile, change the release-quality wrapper, change workflow files, change
fixture JSON, implement runtime actual invocation, perform artifact writer CLI
actual invocation, connect artifact body generation integration, connect
manifest writer integration, enable file writing, use real data, compute
metrics, or claim production readiness.
