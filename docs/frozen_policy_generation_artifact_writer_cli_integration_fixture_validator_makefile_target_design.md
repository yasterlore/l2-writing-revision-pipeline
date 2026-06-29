# Frozen Policy Generation Artifact Writer CLI Integration Fixture Validator Makefile Target Design

## 1. Purpose

This document designs a future standalone Makefile target for running the
artifact writer CLI integration fixture validator.

This is a docs-only design. It does not implement a Makefile target, change the
release-quality wrapper, change GitHub Actions workflow YAML, change Python
code or tests, change fixture JSON, implement artifact writer CLI integration
runtime, connect artifact body generation CLI, connect manifest writer runtime,
generate manifest bodies, use real data, compute metrics, or claim production
readiness.

The target should make the Step470 validator CLI easy to run from `make` while
preserving the synthetic-only, metadata-only, no-oracle, body-free fixture
validation contract.

## 2. Current State

- The artifact writer CLI integration fixture root exists.
- The fixture root has 28 cases and 168 JSON files.
- The validator module exists.
- The validator CLI exists.
- Focused validator tests exist.
- The standalone Makefile target does not exist.
- Release-quality integration for this validator does not exist.
- Artifact writer CLI integration runtime does not exist.
- Artifact body generation CLI integration does not exist.
- Manifest writer integration does not exist.
- Manifest body generation does not exist.

Current validator module:

`python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_fixture_validation.py`

Current CLI entrypoint:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_fixture_validation
```

Current fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration/`

## 3. Target Name

Recommended target:

`check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-fixtures`

Reasons:

- It stays inside the learner-state target namespace.
- It names the frozen policy generation artifact writer boundary.
- It clearly identifies CLI integration fixtures rather than the existing
  artifact writer fixture contract.
- It leaves artifact body generation and manifest writer integration out of the
  target name.
- It can be referenced later from a separate release-quality label.

## 4. Help Text

Recommended help text:

```text
check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-fixtures  Validate artifact writer CLI integration fixture contracts
```

## 5. Target Command

Recommended command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration
```

The target should call the validator CLI directly. It should not duplicate
validator logic in the Makefile, invoke runtime integration, execute artifact
body generation, execute manifest writer code, or write files.

The default human summary is sufficient for the first Makefile target. JSON
mode remains available for ad hoc CLI use but is not required for the
standalone target.

## 6. Expected Target Output

The target output should be body-free and count-only:

- `mode=artifact_writer_cli_integration_fixture_validation`
- `validation_schema_version=learner_state_frozen_policy_generation_artifact_writer_cli_integration_fixture_validation_v0.1`
- `total_cases=28`
- `valid_cases=6`
- `invalid_cases=22`
- `total_json_files=168`
- `json_files_per_case=6`
- `matched_cases=28`
- `mismatched_cases=0`
- `input_error_cases=0`
- `pass_cases=6`
- `usage_error_cases=9`
- `fail_closed_cases=13`
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
- `no_performance_claims=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `file_writing_checked=true`
- `artifact_body_generation_integration_checked=true`
- `manifest_writer_integration_checked=true`
- `artifact_writer_cli_integration_checked=true`
- `release_quality_ready=false`

The target may also print reason-code counts, provided they remain controlled
metadata and do not include fixture bodies, raw content, private paths, or
absolute local paths.

## 7. Expected Target Behavior

The future target should:

- exit `0` when all expected cases match
- return nonzero when validation fails
- print no fixture body
- print no request, pointer, or expected-result body
- print no raw rows
- print no logits or probability dump
- print no private or absolute path values
- perform no file writing
- execute no artifact body generation
- execute no manifest writer
- execute no artifact writer CLI integration runtime

Expected invalid fixtures are part of the fixture contract. They should pass
the target when their expected status and reason code match.

## 8. Failure Interpretation

The target should fail if any of the following occurs:

- fixture root is missing
- required file is missing
- extra JSON file exists in a case directory
- JSON is malformed
- case count does not match 28
- JSON file count does not match 168
- schema version does not match
- case_id does not match the case path
- case_group does not match the directory group
- expected status does not match the case contract
- expected reason code does not match the case taxonomy
- forbidden content is detected
- no-oracle violation is detected
- file-writing flag is true
- artifact body generation flag is true
- manifest writer flag is true
- public output contains body, private-path, or absolute-path leakage

The Makefile target should not mask validator failures or normalize a failing
exit code into success.

## 9. Relation To Existing Artifact Writer Targets

Existing artifact writer targets remain separate:

- `check-learner-state-frozen-policy-generation-artifact-writer-fixtures`
  validates the artifact writer fixture contract.
- `check-learner-state-frozen-policy-generation-artifact-writer-runtime`
  smoke-tests the metadata-only artifact writer runtime.

The proposed target validates only the artifact writer CLI integration fixture
contracts for the generator scaffold CLI -> artifact writer CLI boundary. It
does not replace the existing fixture validator or runtime smoke target.

Success for this target would mean the integration fixture root is internally
consistent. It would not prove runtime integration, artifact body generation,
manifest writer integration, model performance, real-data readiness, or
production readiness.

## 10. Relation To Release-Quality

Recommended staging:

- Step471: docs-only Makefile target design
- Step472: standalone Makefile target implementation
- Step473: release-quality integration design
- Step474: release-quality wrapper integration
- Step475: remote/manual run record workflow design
- Step476: remote status marker

This target should eventually receive its own release-quality label. It should
not replace existing artifact writer fixture or runtime checks.

## 11. Docs Safety Policy

Docs may include:

- target names
- command names
- fixture root names
- field names
- reason code names
- counts and boolean safety flags

Docs must not include:

- JSON body examples
- raw logs
- full job output
- fixture JSON bodies
- request, pointer, or expected-result bodies
- written file JSON bodies
- manifest bodies
- artifact body payloads
- generated policy bodies
- raw rows
- logits or probability dumps
- private path examples
- absolute local or temp path examples
- raw learner text examples
- performance metric bodies

## 12. Future Implementation Tests

Step472 should verify:

- `make help` includes the target and help text
- the target exits `0`
- output includes the expected counts
- output is body-free
- output contains no private or absolute path leakage
- wrapper diff remains empty
- workflow diff remains empty
- Python diff remains empty
- fixture JSON diff remains empty
- `make check-release-quality` still passes but does not include this target
  until a separate wrapper integration step

## 13. What This Does Not Do

This design does not:

- implement the Makefile target
- integrate release-quality
- modify workflow YAML
- modify Python code or tests
- modify fixture JSON
- implement artifact writer CLI integration runtime
- connect artifact body generation CLI
- connect manifest writer runtime
- generate manifest bodies
- use real data
- compute metrics
- prove production readiness

## 14. Next Recommended Steps

- Step472 Makefile target implementation
- Step473 release-quality integration design
- Step474 wrapper integration
- Step475 remote/manual run record workflow design
- Step476 remote status marker

## 15. Step472 Makefile Target Implementation Status

Step472 implements the standalone Makefile target:

`check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-fixtures`

The target runs the Step470 validator CLI against the Step468 fixture root:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration
```

The target emits the validator's body-free count-only summary and remains
standalone. Step472 does not add the target to the release-quality wrapper,
change workflow YAML, change Python code or tests, change fixture JSON,
implement runtime integration, connect artifact body generation CLI, connect
manifest writer runtime, use real data, compute metrics, or claim production
readiness.

## 16. Step473 Release-Quality Integration Design Status

Step473 adds the docs-only release-quality wrapper integration design for this
standalone target:

[Frozen policy generation artifact writer CLI integration fixture release-quality integration design](frozen_policy_generation_artifact_writer_cli_integration_fixture_release_quality_integration_design.md)

The design recommends adding the target after artifact writer fixture
validation and artifact writer runtime smoke, and before artifact body fixture
validation. Step473 does not change the wrapper, change workflow YAML, change
the Makefile, change Python code or tests, change fixture JSON, implement
runtime integration, use real data, compute metrics, or claim production
readiness.

## 17. Step474 Release-Quality Wrapper Integration Status

Step474 adds the standalone target to `scripts/check_release_quality.sh` using
the Step473 label:

`release_quality_check: learner-state frozen policy generation artifact writer CLI integration fixture validation`

The wrapper invokes:

`make check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-fixtures`

The target remains the same body-free, count-only static fixture validator. The
Step474 wrapper integration does not change the Makefile, workflow YAML,
Python code or tests, fixture JSON, runtime integration, artifact body
generation CLI integration, manifest writer integration, real-data use,
metrics, or production readiness status.

## 18. Step475 Remote/Manual Run Record Workflow Design Status

Step475 adds the docs-only future recording workflow for a remote/manual
Release Quality run that includes this target:

[Frozen policy generation artifact writer CLI integration fixture release-quality remote run record workflow](frozen_policy_generation_artifact_writer_cli_integration_fixture_release_quality_remote_run_record_workflow.md)

The design keeps the future marker public-safe, pass-only / count-only, and
explicitly excludes raw logs, fixture bodies, request/pointer/expected bodies,
artifact body payloads, manifest bodies, generated policy bodies, raw rows,
logits, private paths, absolute paths, raw learner text, real data, metrics,
and production readiness claims.
