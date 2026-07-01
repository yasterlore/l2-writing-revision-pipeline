# Frozen Policy Generation Artifact Writer CLI Actual Invocation Fixture Validator Makefile Target Design

## 1. Title

Frozen Policy Generation Artifact Writer CLI Actual Invocation Fixture
Validator Makefile Target Design.

## 2. Scope

This document is the Step501 design-only / planning-only document for running
the Step500 artifact writer CLI actual invocation fixture validator CLI from a
future standalone Makefile target.

This document does not change the Makefile, implement the target, change the
release-quality wrapper, change workflow files, change Python code/tests,
change fixture JSON, implement runtime actual invocation, implement artifact
writer CLI actual invocation, connect artifact body generation integration,
connect manifest writer integration, or enable file writing.

This document is not evidence for production readiness, real-data readiness,
model performance, F1, accuracy, ECE, AURCC, artifact writer CLI actual
invocation correctness, artifact body generation integration correctness,
manifest writer integration correctness, generated policy quality, or
learner-state estimator correctness.

## 3. Prior Completed Chain

- Step496 created the design-only artifact writer CLI actual invocation
  boundary.
- Step497 created the design-only fixture contract for future actual invocation
  fixture validation.
- Step498 created the synthetic metadata-only fixture root with 32 cases and
  192 JSON files.
- Step499 created the design-only fixture validator plan for that fixture root.
- Step500 implemented the static validator module, CLI, and focused tests.

Step500 provides a runnable validator CLI. There is still no standalone
Makefile target, release-quality wrapper integration, workflow change, runtime
actual invocation implementation, artifact writer CLI actual invocation
implementation, artifact body generation integration, manifest writer
integration, or file-writing behavior for this boundary.

Step500 validator module:

`python/learner_state/frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation.py`

Step500 focused tests:

`python/learner_state/tests/test_frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation.py`

Target fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation/`

## 4. Target Validator CLI

The proposed Makefile target should call the Step500 validator CLI directly:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation
```

The target should not duplicate validator logic in the Makefile and should not
invoke any runtime actual invocation behavior.

## 5. Proposed Makefile Target

Recommended target:

`check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-fixtures`

Recommended command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation
```

Recommended help text:

`Run artifact writer CLI actual invocation fixture validation`

Step501 does not add this target to the Makefile.

Step502 implements this standalone Makefile target in the Makefile:

`check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-fixtures`

The implementation calls the Step500 validator CLI with the command above. It
does not add release-quality wrapper integration, change workflow files, change
Python code/tests, change fixture JSON, update runtime actual invocation,
perform artifact writer CLI actual invocation, connect artifact body generation
integration, connect manifest writer integration, or enable file writing.

## 6. Expected Safe Output

The future Makefile target should preserve the Step500 validator's body-free
summary output. Expected public-safe fields include:

- `mode=artifact_writer_cli_actual_invocation_fixture_validation`
- `validation_schema_version=learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation_v0.1`
- `fixture_root=tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation`
- `total_cases=32`
- `valid_cases=6`
- `invalid_cases=26`
- `total_json_files=192`
- `json_files_per_case=6`
- `matched_cases=32`
- `mismatched_cases=0`
- `input_error_cases=0`
- `pass_cases=6`
- `usage_error_cases=3`
- `fail_closed_cases=22`
- `mismatch_cases=1`
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
- `no_raw_stdout_body=true`
- `no_raw_stderr_body=true`
- `no_oracle_checked=true`
- `synthetic_only_checked=true`
- `metadata_only_checked=true`
- `file_writing_checked=true`
- `artifact_writer_cli_actual_invocation_fixture_checked=true`
- `artifact_body_generation_integration_checked=true`
- `manifest_writer_integration_checked=true`
- `production_readiness_claimed=false`
- `real_data_readiness_claimed=false`
- `performance_claims_present=false`

The output may also include controlled reason-code counts and safe root error
codes. Those values must remain metadata-only and must not include fixture
bodies, request bodies, pointer bodies, expected bodies, raw command output
bodies, private path values, or absolute path values.

## 7. Safety Boundary

The proposed target is limited to static fixture validation:

- it does not call the artifact writer CLI
- it does not execute runtime actual invocation
- it does not call artifact body generation
- it does not call the manifest writer
- it does not write files
- it does not display fixture JSON bodies
- it does not display request, pointer, or expected bodies
- it does not display raw stdout/stderr bodies
- it does not display artifact body payloads, manifest bodies, or generated
  policy bodies
- it does not display raw rows, logits, or raw learner text
- it does not display private or absolute path values
- it does not create output artifacts or tmp residue

Expected invalid fixtures are part of the contract. The target should pass when
their expected status, exit-code category, sentinel policy, and reason code
match the Step500 validator rules.

## 8. Relationship To Existing Makefile Targets

Existing related targets remain separate:

- artifact writer fixture validation target
- artifact writer runtime smoke target
- artifact writer CLI integration fixture validation target
- artifact writer CLI integration runtime fixture validation target
- artifact writer CLI integration runtime smoke target
- artifact body fixture validation target
- manifest writer fixture validation target

The proposed target is a standalone target only for artifact writer CLI actual
invocation fixture validation. It does not replace existing artifact writer,
CLI integration, runtime smoke, artifact body, or manifest writer targets.

Success for this proposed target would mean the Step498 actual invocation
fixture root is internally consistent under the Step500 validator. It would
not prove artifact writer CLI actual invocation correctness, artifact body
generation integration correctness, manifest writer integration correctness,
model performance, real-data readiness, or production readiness.

## 9. Release-Quality Staging

Recommended staging:

- Step501: docs-only Makefile target design
- Step502: standalone Makefile target implementation
- Step503: release-quality integration design
- later separate step: release-quality wrapper integration
- later separate step: remote/manual run record workflow design
- later separate step: remote status marker

Step502 does not add the target to release-quality. Release-quality
wrapper integration should remain separate from standalone target
implementation.

Step503 adds the release-quality integration design:
[Frozen policy generation artifact writer CLI actual invocation fixture validator release-quality integration design](frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validator_release_quality_integration_design.md).
It does not change the release-quality wrapper, workflow files, Makefile,
Python code/tests, fixture JSON, runtime actual invocation, artifact writer CLI
actual invocation, artifact body generation integration, manifest writer
integration, or file writing.

Step504 adds the standalone target to the release-quality wrapper. The wrapper
check remains static fixture validation only and does not perform artifact
writer CLI actual invocation, artifact body generation integration, manifest
writer integration, or file writing.

Step505 adds the docs-only remote/manual run record workflow design for the
Step504 wrapper check:
[Frozen policy generation artifact writer CLI actual invocation fixture validator release-quality remote run record workflow](frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validator_release_quality_remote_run_record_workflow.md).

Step506 adds the public-safe remote status marker:
[Learner-state frozen policy generation artifact writer CLI actual invocation fixture validator release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validator_release_quality_remote_run_status.md).

Step507 adds the docs-only runtime update design:
[Frozen policy generation artifact writer CLI actual invocation runtime update design](frozen_policy_generation_artifact_writer_cli_actual_invocation_runtime_update_design.md).

## 10. Proposed Checks For Step502

If Step502 implements the standalone Makefile target, it should run checks such
as:

- `git status --short`
- `make help` includes the proposed target and help text
- proposed Makefile target execution
- focused tests for the Step500 validator
- validator CLI smoke
- `make check-python`
- compileall
- targeted diff review
- `git diff --check`
- conflict marker scan
- code/docs/output safety scan
- fixture JSON diff check
- Makefile-only implementation diff check
- release-quality wrapper and workflow diff check
- residue check

Step501 does not run these future implementation checks.

## 11. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1, accuracy, ECE, or AURCC achievement
- artifact writer CLI actual invocation correctness
- artifact body generation integration correctness
- manifest writer integration correctness
- generated policy quality
- learner-state estimator correctness
- Makefile target implementation
- release-quality integration implementation
- actual invocation implementation

## 12. Public-Safe Checklist

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

## 13. Step508 Runtime Fixture Update Design Status

Step508 adds the docs-only / planning-only fixture update design for adapting
the existing artifact writer CLI integration runtime fixture root to a future
`actual_invocation_metadata_only` mode:

[Frozen policy generation artifact writer CLI actual invocation runtime fixture update design](frozen_policy_generation_artifact_writer_cli_actual_invocation_runtime_fixture_update_design.md)

Step508 does not change fixture JSON, change fixture roots, update validators,
change Python code/tests, change Makefile, change the release-quality wrapper,
change workflow files, implement runtime actual invocation, perform artifact
writer CLI actual invocation, connect artifact body generation integration,
connect manifest writer integration, enable file writing, use real data,
compute metrics, or claim production readiness.
