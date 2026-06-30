# Frozen Policy Generation Artifact Writer CLI Integration Runtime Fixture Validator Makefile Target Design

## 1. Scope

This document is the Step482 design for a future standalone Makefile target
that runs the Step481 artifact writer CLI integration runtime fixture validator
CLI.

This is design-only. It does not change the Makefile, change the
release-quality wrapper, change workflow YAML, change Python code/tests, change
fixture JSON, or implement runtime integration.

This is not artifact body generation integration, manifest writer integration,
production readiness evidence, real-data readiness evidence, or model
performance evidence.

## 2. Prior Completed Chain

- Step477 created the artifact writer CLI integration runtime design.
- Step478 created the runtime fixture contract design.
- Step479 created the synthetic metadata-only runtime fixture root.
- Step480 created the runtime fixture validator design.
- Step481 implemented the static validator module, CLI, and focused tests.

Step481 provides a runnable validator CLI, but there is still no standalone
Makefile target, release-quality wrapper integration, workflow change, or
runtime implementation for this boundary.

Current validator module:

`python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation.py`

Current focused tests:

`python/learner_state/tests/test_frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation.py`

Target fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime/`

## 3. Proposed Target Name

Recommended target:

`check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime-fixtures`

Reasons:

- It stays inside the learner-state / frozen policy generation target namespace.
- It distinguishes runtime fixture validation from the earlier CLI integration
  fixture validator.
- It names artifact writer CLI integration without implying artifact body
  generation or manifest writer chaining.
- It can later receive a separate release-quality wrapper label.

## 4. Proposed Help Text

Recommended help text:

`check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime-fixtures  Validate artifact writer CLI integration runtime fixture contracts`

## 5. Proposed Command

Recommended command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime
```

The target should call the validator CLI directly. It should not duplicate
validator logic in the Makefile, execute artifact writer CLI integration
runtime, call artifact writer CLI runtime, run artifact body generation, run
manifest writer integration, or write files.

The default human summary is sufficient for the first standalone target. JSON
mode remains available from the CLI for ad hoc inspection.

## 6. Expected Target Output

The target output should remain body-free and count-only:

- `mode=artifact_writer_cli_integration_runtime_fixture_validation`
- `validation_schema_version=learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_validation_v0.1`
- `fixture_root=tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime`
- `total_cases=30`
- `valid_cases=6`
- `invalid_cases=24`
- `total_json_files=180`
- `json_files_per_case=6`
- `matched_cases=30`
- `mismatched_cases=0`
- `input_error_cases=0`
- `pass_cases=6`
- `usage_error_cases=5`
- `fail_closed_cases=19`
- `duplicate_case_id_cases=0`
- `missing_required_file_cases=0`
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
- `no_oracle_checked=true`
- `synthetic_only_checked=true`
- `metadata_only_checked=true`
- `file_writing_checked=true`
- `artifact_writer_cli_integration_runtime_checked=true`
- `artifact_body_generation_integration_checked=true`
- `manifest_writer_integration_checked=true`
- `production_readiness_claimed=false`
- `real_data_readiness_claimed=false`
- `performance_claims_present=false`
- `root_errors=[]`

The target may also print controlled reason-code counts. Those counts must
remain field-name / reason-code metadata only and must not include fixture
bodies, request bodies, pointer bodies, expected bodies, raw content, private
paths, or absolute local paths.

## 7. Expected Target Behavior

The future target should:

- exit `0` when the fixture root matches the validator contract
- return nonzero when validation fails
- print no fixture JSON body
- print no request, pointer, or expected body
- print no raw rows
- print no logits or probability dump
- print no private or absolute path values
- perform no file writing
- execute no artifact writer CLI integration runtime
- execute no artifact body generation
- execute no manifest writer integration
- leave no output residue

Expected invalid fixtures are part of the contract. They should pass when their
expected status, exit-code category, sentinel policy, and reason code match.

## 8. Failure Interpretation

The target should fail if any of the following occurs:

- fixture root is missing
- valid or invalid directory is missing
- required file is missing
- extra JSON file exists in a case directory
- JSON is malformed
- case count does not match 30
- JSON file count does not match 180
- schema version does not match
- case_id does not match the case path
- case_kind does not match the directory group
- expected status does not match the case contract
- expected reason code does not match the case taxonomy
- expected exit-code category does not match the case contract
- duplicate case id is detected
- forbidden actual key or unsafe string is detected
- no-oracle violation is detected
- synthetic-only or metadata-only flag is missing
- file-writing flag is unexpectedly enabled
- artifact body generation flag is unexpectedly enabled outside the expected
  invalid boundary case
- manifest writer flag is unexpectedly enabled outside the expected invalid
  boundary case
- suppression flags are inconsistent
- public output contains body, private-path, absolute-path, raw-content, or raw
  log leakage

The Makefile target should not mask validator failures or normalize a failing
exit code into success.

## 9. Relation To Existing Targets

Existing related targets remain separate:

- `check-learner-state-frozen-policy-generation-artifact-writer-fixtures`
  validates the artifact writer fixture contract.
- `check-learner-state-frozen-policy-generation-artifact-writer-runtime`
  smoke-tests the metadata-only artifact writer runtime.
- `check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-fixtures`
  validates the earlier generator scaffold CLI -> artifact writer CLI
  integration fixture contract.

The proposed target validates only the Step479 runtime fixture contracts for a
future artifact writer CLI integration runtime boundary. It does not replace
existing artifact writer fixture, runtime, or CLI integration fixture targets.

Success for this target would mean the runtime fixture root is internally
consistent. It would not prove runtime integration, artifact body generation
integration, manifest writer integration, generated policy quality, model
performance, real-data readiness, or production readiness.

## 10. Relation To Release-Quality

Recommended staging:

- Step482: docs-only Makefile target design
- Step483: standalone Makefile target implementation
- Step484: release-quality integration design
- Step485: release-quality wrapper integration
- Step486: remote/manual run record workflow design
- Step487: remote status marker
- Step488: artifact writer CLI integration runtime implementation design

The target should remain standalone at first. Release-quality wrapper
integration should happen in a later step after the standalone target is
implemented and locally verified.

## 11. Docs Safety Policy

Docs may include:

- target names
- command names
- fixture root names
- field names
- reason-code names
- counts and boolean safety flags

Docs must not include:

- JSON body examples
- raw logs
- full job output
- fixture JSON bodies
- request, pointer, or expected bodies
- written file JSON bodies
- manifest bodies
- artifact body payloads
- generated policy bodies
- raw rows
- logits or probability dumps
- private path examples
- absolute local or temp path examples
- raw learner text examples
- real participant data
- performance metric bodies

## 12. Future Implementation Tests

Step483 should verify:

- `make help` includes the target and help text.
- The target exits `0`.
- Target output includes `total_cases=30`.
- Target output includes `total_json_files=180`.
- Target output includes `matched_cases=30`.
- Target output includes `input_error_cases=0`.
- Target output includes `pass_cases=6`.
- Target output includes `usage_error_cases=5`.
- Target output includes `fail_closed_cases=19`.
- Target output includes `artifact_writer_cli_integration_runtime_checked=true`.
- Target output includes `production_readiness_claimed=false`.
- Output remains body-free and public-safe.
- No fixture JSON body, request body, pointer body, expected body, artifact
  body payload, manifest body, generated policy body, raw rows, logits,
  private paths, absolute paths, raw learner text, or raw logs are printed.
- No files are written by the target.
- Release-quality wrapper diff remains none in the standalone target step.
- Workflow diff remains none.
- Python code/tests diff remains none in the standalone target step.
- Fixture JSON diff remains none.

## 13. What This Does Not Do

This design does not:

- implement the Makefile target
- integrate release-quality
- modify workflow YAML
- modify Python code/tests
- modify fixture JSON
- implement artifact writer CLI integration runtime
- execute artifact writer CLI integration runtime
- connect artifact body generation integration
- connect manifest writer integration
- generate manifest bodies
- use real data
- compute metrics
- prove production readiness
- prove real-data readiness
- prove model performance

## 14. Step483 Standalone Target Implementation Status

Step483 implements the standalone Makefile target proposed by this design:

`check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime-fixtures`

The target runs the Step481 validator CLI over the Step479 fixture root and
emits body-free public-safe counts. Step483 does not add the target to
release-quality, change workflow YAML, change Python code/tests, change
fixture JSON, execute runtime integration, connect artifact body generation,
connect manifest writer integration, use real data, compute metrics, or claim
production readiness.

## 15. Step484 Release-Quality Integration Design Status

Step484 adds the docs-only release-quality integration design for the
standalone target:

[Frozen policy generation artifact writer CLI integration runtime fixture release-quality integration design](frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_release_quality_integration_design.md)

The design proposes the future wrapper label, command, insertion point,
expected body-free output, failure interpretation, and remote marker staging.
It does not change the release-quality wrapper, workflow files, Makefile,
Python code/tests, fixture JSON, execute runtime integration, connect artifact
body generation, connect manifest writer integration, use real data, compute
metrics, or claim production readiness.

## 16. Next Recommended Steps

- Step485: release-quality wrapper integration.
- Step486: remote/manual run record workflow design.
- Step487: remote status marker.
- Step488: artifact writer CLI integration runtime implementation design.

## 17. Public-Safe Checklist

- no raw logs
- no full job output
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
