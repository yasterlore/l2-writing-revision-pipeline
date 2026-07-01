# Frozen Policy Generation Artifact Writer CLI Actual Invocation Runtime Fixture Validator Update Design

## 1. Title

Frozen Policy Generation Artifact Writer CLI Actual Invocation Runtime Fixture
Validator Update Design

## 2. Scope

This document is a design-only / planning-only validator update design for
future validation of the Step509-expanded artifact writer CLI integration
runtime fixture root.

This step does not:

- change the validator
- change Python code/tests
- change the Makefile
- change the release-quality wrapper
- change workflow files
- change fixture JSON
- implement runtime actual invocation
- implement artifact writer CLI actual invocation
- implement artifact body generation integration
- implement manifest writer integration
- enable file writing
- prove production readiness, real-data readiness, or model performance

## 3. Prior Completed Chain

- Step489 implemented the initial artifact writer CLI integration runtime
  module / CLI / focused tests.
- Step507 created the runtime update design for a future metadata-only actual
  invocation boundary.
- Step508 created the runtime fixture update design for future
  `actual_invocation_metadata_only` fixture cases.
- Step509 expanded the existing runtime fixture root with v0.2 synthetic
  metadata-only actual invocation cases.

Step509 is a fixture root update. It does not update the validator and does
not prove runtime actual invocation correctness.

## 4. Current Validator Baseline

- module path: `python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation.py`
- CLI command: `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime`
- current validator schema version: `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation_v0.1`
- current expected counts before Step509: 30 cases, 6 valid cases, 24 invalid
  cases, 180 JSON files, 6 JSON files per case
- current v0.1 support: plan-only / no-invocation fixture cases
- current output fields: aggregate counts, status counts, safe reason codes,
  suppression flags, metadata-only flags, no-oracle flags, and public-safe
  safety booleans
- current Makefile target: `check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime-fixtures`
- current release-quality inclusion status: included through the existing
  standalone target and wrapper chain
- current limitation: v0.2 actual invocation metadata-only cases are not yet
  supported

## 5. Updated Target Fixture Root

Target fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime/`

Expected updated counts:

- total cases: 54
- valid cases: 12
- invalid cases: 42
- total JSON files: 324
- JSON files per case: 6
- existing v0.1 plan-only cases: 30
- new v0.2 actual invocation cases: 24
- new valid actual invocation cases: 6
- new invalid actual invocation cases: 18

## 6. Proposed Validator Schema Strategy

Two schema strategies are available:

- keep validator schema version as v0.1 and expand accepted fixture schemas
- introduce a validator schema version v0.2

Comparison:

- backward compatibility: both can preserve v0.1 fixture acceptance
- clarity of result output: v0.2 makes mixed v0.1 / v0.2 aggregate fields
  explicit
- release-quality stability: keeping the same Makefile target with a v0.2
  validator result minimizes orchestration change
- implementation risk: v0.2 requires result-schema updates but avoids hiding
  new semantics behind a v0.1 label
- docs clarity: v0.2 is clearer for reviewers and future status markers

Recommended future validator schema:

`learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation_v0.2`

Step510 does not implement this schema.

## 7. Fixture Schema Acceptance

Existing v0.1 fixture schemas should remain accepted:

- `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_case_v0.1`
- `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_request_v0.1`
- `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_pointer_v0.1`
- `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_artifact_writer_cli_metadata_v0.1`
- `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_expected_summary_v0.1`
- `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_expected_error_v0.1`

New v0.2 fixture schemas should be accepted:

- `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_case_v0.2`
- `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_request_v0.2`
- `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_pointer_v0.2`
- `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_artifact_writer_cli_metadata_v0.2`
- `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_expected_summary_v0.2`
- `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_expected_error_v0.2`

Unknown schemas should be rejected safely with public-safe reason codes.

## 8. Updated Validator Responsibilities

Future validator responsibilities should include the existing v0.1 checks plus:

- v0.1 and v0.2 schema family detection
- v0.1 plan-only case backward compatibility
- v0.2 actual invocation mode validation
- `runtime_mode` validation
- `invocation_mode` validation
- `actual_invocation_metadata_only` field consistency
- `runtime_actual_invocation_enabled` consistency
- `artifact_writer_cli_invoked` consistency
- `artifact_writer_cli_output_scanned` consistency
- `artifact_writer_cli_output_body_free` consistency
- `raw_stdout_body_suppressed` / `raw_stderr_body_suppressed` consistency
- unsafe output sentinel checks
- `file_writing_detected` checks
- downstream invocation sentinels
- nonzero exit safe summary handling
- timeout safe summary handling
- expected summary v0.2 field matching
- updated reason-code counts
- aggregate count matching for 54 cases / 324 JSON files

## 9. Updated Aggregate Counts

Expected future aggregate counts:

- `total_cases=54`
- `valid_cases=12`
- `invalid_cases=42`
- `total_json_files=324`
- `json_files_per_case=6`
- `matched_cases=54`
- `mismatched_cases=0`
- `input_error_cases=0`
- `pass_cases=12`

Recommended status counts:

- `usage_error_cases=6`
- `fail_closed_cases=35`
- `mismatch_cases=1`

Rationale:

- existing pass 6 + new pass 6 = 12
- existing usage error 5 + new unsupported schema 1 = 6
- existing fail-closed 19 + new fail-closed 16 = 35
- new mismatched expected status 1 = 1

These counts sum to 54.

## 10. Updated Reason Code Mapping

Existing v0.1 reason codes should remain supported.

New v0.2 reason-code families:

- `none`
- `actual_invocation_raw_stdout_body`
- `actual_invocation_raw_stderr_body`
- `actual_invocation_artifact_body_payload`
- `actual_invocation_manifest_body`
- `actual_invocation_generated_policy_body`
- `actual_invocation_request_body`
- `actual_invocation_pointer_body`
- `actual_invocation_expected_body`
- `actual_invocation_private_path`
- `actual_invocation_absolute_path`
- `actual_invocation_raw_learner_text`
- `actual_invocation_raw_rows`
- `actual_invocation_logits`
- `actual_invocation_file_writing_detected`
- `actual_invocation_artifact_body_generation_invoked`
- `actual_invocation_manifest_writer_invoked`
- `actual_invocation_unsupported_schema`
- `actual_invocation_mismatched_expected_status`
- `actual_invocation_timeout_safe_summary`
- `actual_invocation_nonzero_exit_safe_summary`

Reason codes should remain public-safe and body-free.

## 11. Sentinel Validation Policy Update

v0.2 actual invocation cases should follow this sentinel policy:

- invalid v0.2 cases must use metadata-only sentinels
- actual raw stdout/stderr body must not be stored
- actual request/pointer/expected body must not be stored
- actual artifact body payload, manifest body, and generated policy body must
  not be stored
- private / absolute path string values must not be stored
- raw learner text, raw rows, and logits must not be stored
- valid v0.2 cases must not contain forbidden sentinels
- sentinels must be allowed only in expected invalid cases
- sentinel values must be safe booleans, reason codes, or count-like metadata
  only

## 12. Path And Subprocess Boundary Checks

Future v0.2 validation should check:

- relative paths only
- no absolute/private path values
- no parent traversal
- no home/cloud markers
- `subprocess_shell_enabled=false`
- stdout/stderr capture flags remain safe
- stdout/stderr body printed flags remain false
- unsupported subprocess output schema fails safely
- timeout category remains body-free
- exit-code category remains body-free
- validator performs no actual subprocess execution

## 13. File-Writing / Residue Checks

Future v0.2 validation should check:

- valid cases have `file_writing_detected=false`
- valid cases have `file_writing_enabled=false`
- valid cases have `residue_expected=false`
- invalid file-writing detected case fails closed
- validator creates no tmp output
- validator does not invoke the runtime
- validator reports residue expectations only as metadata

## 14. CLI Output Boundary Update

Future validator CLI output may add:

- `validator_schema_version`
- `fixture_schema_versions_seen`
- `v0_1_case_count`
- `v0_2_case_count`
- `plan_only_case_count`
- `actual_invocation_case_count`
- `runtime_actual_invocation_enabled_cases`
- `actual_invocation_fail_closed_cases`
- `actual_invocation_usage_error_cases`
- `actual_invocation_mismatch_cases`
- `actual_invocation_safety_flags_checked`

Output must remain aggregate, public-safe, and body-free. It must not output
fixture bodies or raw content.

## 15. Focused Tests For Future Validator Update

Future focused tests should cover:

- updated root summary matches 54 cases / 324 JSON files
- v0.1 cases remain accepted
- v0.2 cases are accepted
- valid actual invocation cases pass
- invalid actual invocation cases match expected reason codes
- unknown v0.2 schema fails safely
- raw stdout/stderr sentinels fail closed
- artifact body payload sentinel fails closed
- manifest body sentinel fails closed
- generated policy body sentinel fails closed
- request/pointer/expected body sentinels fail closed
- private / absolute path sentinels fail closed
- raw learner text / raw rows / logits sentinels fail closed
- file-writing detected sentinel fails closed
- downstream invocation sentinels fail closed
- nonzero exit safe summary handled as designed
- timeout safe summary handled as designed
- mismatched expected status reported as mismatch
- CLI output contains no fixture bodies
- deterministic traversal
- malformed JSON returns `input_error` using a temp fixture
- root not found returns `input_error`

## 16. Backward Compatibility Plan

Backward compatibility plan:

- existing 30 v0.1 cases remain valid input
- validator supports v0.1 and v0.2 in one root
- old fields remain supported
- new fields are required only for v0.2 actual invocation cases
- existing Makefile target may keep the same name
- release-quality label may remain the same
- docs should clarify new counts after implementation
- implementation step should update full technical specification docs

## 17. Planned Implementation Step

Proposed next implementation step:

- Step511: runtime fixture validator v0.2 support implementation

Expected Step511 changes:

- validator module
- focused tests
- possibly docs / README / full technical specification docs

Expected Step511 non-changes:

- Makefile target name
- release-quality wrapper
- workflow files
- fixture JSON
- runtime actual invocation implementation

## 18. Failure Interpretation

Future validator failure means a fixture schema, metadata consistency, or
sentinel policy issue.

Failure does not mean:

- runtime actual invocation failed
- artifact writer CLI actual invocation failed
- artifact body generation failed
- manifest writer failed
- model performance issue

Failure must be interpreted through public-safe reason codes and aggregate
counts only.

## 19. Non-Claims

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
- validator update implemented

## 20. Public-Safe Checklist

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

## 21. Step511 Validator v0.2 Support Implementation Status

Step511 implements the static runtime fixture validator module / CLI / focused
test update described by this design. The validator result schema is now:

`learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation_v0.2`

The updated validator accepts the original v0.1 plan-only fixture schema
family and the Step509 v0.2 actual-invocation metadata-only fixture schema
family. Expected public-safe aggregate counts are:

- `total_cases=54`
- `valid_cases=12`
- `invalid_cases=42`
- `total_json_files=324`
- `matched_cases=54`
- `mismatched_cases=0`
- `input_error_cases=0`
- `pass_cases=12`
- `usage_error_cases=6`
- `fail_closed_cases=35`
- `mismatch_cases=1`
- `v0_1_case_count=30`
- `v0_2_case_count=24`
- `plan_only_case_count=30`
- `actual_invocation_case_count=24`
- `runtime_actual_invocation_enabled_cases=24`

Step511 does not change fixture JSON, rename the Makefile target, change the
release-quality wrapper, change workflows, implement runtime actual
invocation, perform artifact writer CLI actual invocation, connect artifact
body generation integration, connect manifest writer integration, enable file
writing, use real data, compute metrics, or claim production readiness.

## 22. Step512 Runtime Implementation Refinement Design Status

Step512 adds the docs-only / planning-only implementation refinement design
for a future Step489 runtime `actual_invocation_metadata_only` implementation
update:

[Frozen policy generation artifact writer CLI actual invocation runtime implementation refinement design](frozen_policy_generation_artifact_writer_cli_actual_invocation_runtime_implementation_refinement_design.md)

Step512 does not update the validator, change Python code/tests, change
Makefile, change the release-quality wrapper, change workflows, change fixture
JSON, implement runtime actual invocation, perform artifact writer CLI actual
invocation, connect artifact body generation integration, connect manifest
writer integration, enable file writing, use real data, compute metrics, or
claim production readiness.

## 23. Step513 Runtime Actual Invocation Implementation Status

Step513 updates the runtime module and focused tests so the existing plan-only
path remains the default while explicit `--actual-invocation` enables runtime
schema v0.2 `actual_invocation_metadata_only` public-safe summaries. This
does not change the fixture validator, fixture JSON, Makefile, release-quality
wrapper, workflows, artifact body generation integration, manifest writer
integration, file writing, real-data use, metric use, or production readiness
claims.

## 24. Step514 Makefile Target Design Status

Step514 adds a design-only / planning-only standalone Makefile target design
for the Step513 explicit `actual_invocation_metadata_only` runtime smoke. It
does not change the validator, Makefile, release-quality wrapper, workflows,
Python code/tests, fixture JSON, runtime implementation, artifact body
generation integration, manifest writer integration, file writing, real-data
use, metric use, or production readiness claims.

See
[Frozen policy generation artifact writer CLI actual invocation runtime Makefile target design](frozen_policy_generation_artifact_writer_cli_actual_invocation_runtime_makefile_target_design.md).

## 25. Step515 Makefile Target Implementation Status

Step515 implements the standalone Makefile target
`check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-runtime`
for one valid v0.2 actual invocation metadata-only runtime smoke case. It does
not change the fixture validator, fixture JSON, Python code/tests, runtime
implementation, release-quality wrapper, workflows, artifact body generation
integration, manifest writer integration, file writing, real-data use, metric
use, or production readiness claims.

## 26. Step516 Release-Quality Integration Design Status

Step516 adds the docs-only / planning-only release-quality integration design
for the Step515 standalone target:

[Frozen policy generation artifact writer CLI actual invocation runtime release-quality integration design](frozen_policy_generation_artifact_writer_cli_actual_invocation_runtime_release_quality_integration_design.md)

It proposes a future wrapper label / command and insertion point only. It
does not change the release-quality wrapper, workflow files, Makefile,
Python code/tests, fixture JSON, runtime implementation, artifact body
generation integration, manifest writer integration, file writing, real-data
use, metric use, or production readiness claims.
