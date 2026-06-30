# Frozen Policy Generation Artifact Writer CLI Integration Runtime Fixture Release-Quality Integration Design

## 1. Purpose

This document fixes the docs-only release-quality integration design for the
standalone artifact writer CLI integration runtime fixture validator target.

This is not release-quality wrapper implementation, not a workflow change, not
a Makefile change, not Python code/test change, not fixture JSON change, not
artifact writer CLI integration runtime implementation, not artifact body
generation integration, not manifest writer integration, and not manifest body
generation.

The goal is to define how
`check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime-fixtures`
should later enter the release-quality wrapper safely while preserving the
synthetic-only / metadata-only / no-oracle boundary.

This design does not prove production readiness, real-data readiness, model
performance, F1, accuracy, ECE, AURCC, runtime integration correctness,
artifact body generation integration correctness, manifest writer integration
correctness, generated policy quality, or learner-state estimator correctness.

## 2. Current State

- The artifact writer CLI integration runtime design exists.
- The runtime fixture contract design exists.
- The runtime fixture root exists with 30 synthetic metadata-only cases.
- The runtime fixture root contains 180 JSON files, 6 per case.
- The static runtime fixture validator module exists.
- The validator CLI exists.
- Focused validator tests exist.
- The standalone Makefile target exists.
- The standalone target validates the fixture root statically only.
- Step485 adds the standalone target to the release-quality wrapper.
- GitHub Actions workflow YAML is unchanged for this target.
- Artifact writer CLI integration runtime is not implemented.
- Artifact body generation CLI integration is not implemented.
- Manifest writer integration is not implemented.
- Manifest body generation is not implemented.

Standalone target:

`check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime-fixtures`

Standalone target command:

```bash
make check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime-fixtures
```

## 3. Proposed Release-Quality Label

Recommended label:

```text
release_quality_check: learner-state frozen policy generation artifact writer CLI integration runtime fixture validation
```

The label says `runtime fixture validation` because this check validates the
future runtime fixture contract. It must not imply that the artifact writer CLI
integration runtime exists or has been executed.

## 4. Proposed Command

Recommended wrapper command:

```bash
make check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime-fixtures
```

The wrapper should call the standalone Makefile target rather than duplicating
the validator CLI command. This keeps the developer entrypoint and wrapper
entrypoint aligned.

## 5. Proposed Insertion Point

Recommended insertion point:

- after artifact writer fixture validation
- after artifact writer runtime smoke
- after artifact writer CLI integration fixture validation
- before artifact body fixture validation
- before artifact body generation checks
- before artifact body file-writing checks
- before manifest writer checks
- before config/scoring smoke checks

Recommended local order:

1. `release_quality_check: learner-state frozen policy generation artifact writer fixture validation`
2. `release_quality_check: learner-state frozen policy generation artifact writer runtime smoke`
3. `release_quality_check: learner-state frozen policy generation artifact writer CLI integration fixture validation`
4. `release_quality_check: learner-state frozen policy generation artifact writer CLI integration runtime fixture validation`
5. `release_quality_check: learner-state frozen policy generation artifact body fixture validation`

Reasons:

- Artifact writer standalone fixture validation runs first.
- Artifact writer standalone runtime smoke runs next.
- The earlier generator scaffold CLI -> artifact writer CLI integration fixture
  validation runs before the runtime fixture layer.
- The new check validates future runtime fixture contracts statically, still
  without executing the runtime.
- Artifact body generation and manifest writer chains remain separate and
  later.
- Existing targets are not replaced.

## 6. Expected Release-Quality Output

The expected output is body-free and count-only:

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

Controlled reason-code counts may be printed as metadata. They must not include
fixture bodies, request bodies, pointer bodies, expected bodies, raw rows,
logits, probabilities, private paths, absolute local paths, raw learner text,
or performance metric bodies.

## 7. Expected Wrapper Behavior

The wrapper should:

- continue when the standalone target exits `0`
- fail when the standalone target exits nonzero
- print the release-quality label and command
- allow only body-free public-safe target output
- perform no file writing beyond the validator's read-only fixture scan
- execute no artifact writer CLI integration runtime
- execute no artifact body generation integration
- execute no manifest writer integration
- copy no raw logs into docs
- preserve existing artifact writer, artifact body, and manifest writer checks

Expected invalid fixtures remain part of the contract. They should count as
matched when the expected status, exit-code category, sentinel policy, and
reason code align.

## 8. Failure Interpretation

Release-quality should fail if the target fails because of:

- fixture root missing
- required file missing
- extra JSON file in a case directory
- malformed JSON
- case count mismatch
- JSON file count mismatch
- schema version mismatch
- case_id mismatch
- case_kind mismatch
- expected status mismatch
- expected reason-code mismatch
- expected exit-code category mismatch
- duplicate case id
- forbidden actual key or unsafe string
- no-oracle violation
- missing synthetic-only or metadata-only flag
- unexpected file-writing flag
- unexpected artifact body generation flag
- unexpected manifest writer flag
- inconsistent suppression flags
- residue expectation mismatch
- public output leakage
- validator internal error

These failures mean the static runtime fixture contract is unsafe or
inconsistent. They are not model performance failures, production readiness
failures, or proof that a runtime integration executed.

## 9. Relation To Existing Release-Quality Chain

This proposed check:

- does not replace artifact writer fixture validation
- does not replace artifact writer runtime smoke
- does not replace artifact writer CLI integration fixture validation
- does not run artifact writer CLI integration runtime
- does not run artifact body generation integration
- does not run manifest writer integration
- validates only the Step479 runtime fixture root contract

The existing artifact writer fixture/runtime and CLI integration fixture checks
remain upstream. The proposed runtime fixture validator adds a separate static
fixture-contract layer before artifact body checks begin.

## 10. Relation To Artifact Body And Manifest Writer

Artifact body generation remains later and separate. Manifest writer
integration remains later and separate. Manifest body generation remains later
and separate.

The check may report:

- `artifact_body_generation_integration_checked=true`
- `manifest_writer_integration_checked=true`
- `artifact_writer_cli_integration_runtime_checked=true`

Those fields mean the fixture contract checked the disabled or separated
boundaries. They do not mean artifact body generation integration, manifest
writer integration, or runtime integration correctness has been proven.

## 11. Release-Quality Safety Policy

Allowed in wrapper output:

- label
- command
- mode
- validation schema version
- fixture root as a relative repo path
- case counts
- pass / usage-error / fail-closed counts
- duplicate/missing-file counts
- safety flags
- controlled reason-code counts
- `production_readiness_claimed=false`
- `real_data_readiness_claimed=false`
- `performance_claims_present=false`

Forbidden in wrapper output and docs:

- raw logs
- full job output copied into docs
- fixture JSON bodies
- request bodies
- pointer bodies
- expected-result bodies
- written file JSON bodies
- manifest bodies
- artifact body payloads
- generated policy bodies
- raw rows
- logits or probability dumps
- private paths
- absolute local or temp paths
- raw learner text
- final text
- observed-after text
- gold labels
- post-hoc annotations
- test-set tuning payloads
- scoring feedback payloads
- real participant data
- performance metric bodies

## 12. Wrapper Implementation Plan

Step485 follows this implementation plan:

- update `scripts/check_release_quality.sh`
- add the proposed label and command at the proposed insertion point
- not change GitHub Actions workflow YAML
- not change the Makefile
- not change Python code or tests
- not change fixture JSON
- not execute artifact writer CLI integration runtime
- not connect artifact body generation integration
- not connect manifest writer integration
- run the standalone target
- run `make check-release-quality`
- confirm the new label appears
- confirm output remains body-free
- confirm wrapper diff contains only the new label and command block

## 13. Remote Marker Staging

After wrapper integration:

- run Release Quality remotely after the wrapper change is present on the
  target branch
- collect safe metadata only
- do not copy raw logs
- do not copy full job output
- create a remote/manual run record workflow design
- then create a remote status marker

The future marker should remain pass-only / count-only. It should not claim
runtime integration correctness, artifact body generation integration
correctness, manifest writer integration correctness, production readiness,
real-data readiness, or model performance.

## 14. Docs Safety Policy

Docs may include:

- target names
- command names
- release-quality labels
- fixture root names
- schema/version names
- field names
- reason-code names
- counts
- boolean safety flags

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

## 15. Step485 Wrapper Integration Status

Step485 implements the wrapper integration proposed by this design by adding
the release-quality label and command block to `scripts/check_release_quality.sh`.

Added label:

```text
release_quality_check: learner-state frozen policy generation artifact writer CLI integration runtime fixture validation
```

Added command:

```bash
make check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime-fixtures
```

The check is inserted after artifact writer CLI integration fixture validation
and before artifact body fixture validation. Step485 does not change workflow
YAML, Makefile targets, Python code/tests, fixture JSON, runtime
implementation, artifact body generation integration, manifest writer
integration, real-data use, metrics, or production readiness.

## 16. Step486 Remote Run Record Workflow Design Status

Step486 adds the docs-only remote/manual run record workflow design for the
Step485 wrapper check:

[Frozen policy generation artifact writer CLI integration runtime fixture release-quality remote run record workflow](frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_release_quality_remote_run_record_workflow.md)

The design defines public-safe remote run metadata, count-only target summary
fields, related release-quality chain summary policy, safety review workflow,
interpretation rules, and the proposed future status marker path. It does not
create the marker, change workflow YAML, change the wrapper, change Makefile,
change Python code/tests, change fixture JSON, execute runtime integration,
use real data, compute metrics, or claim production readiness.

## 17. Step487 Remote Status Marker Status

Step487 creates the public-safe pass-only/count-only remote/manual status
marker for the Step485 wrapper check:

[Learner-state frozen policy generation artifact writer CLI integration runtime fixture release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_fixture_release_quality_remote_run_status.md)

The marker records wrapper inclusion and the 30-case / 180-JSON static fixture
validation summary without raw logs, full job output, copied GitHub log blocks,
fixture JSON bodies, request/pointer/expected bodies, runtime integration
evidence, real-data readiness evidence, model-performance evidence, or
production readiness evidence.

## 18. What This Does Not Do

This design does not:

- modify workflow YAML
- modify the Makefile
- modify Python code or tests
- modify fixture JSON
- implement artifact writer CLI integration runtime
- execute artifact writer CLI integration runtime
- implement artifact body generation CLI integration
- implement manifest writer integration
- generate manifest bodies
- use real data
- compute metrics
- prove production readiness
- prove real-data readiness
- prove model performance

## 19. Next Recommended Steps

- Step489: artifact writer CLI integration runtime implementation.

## 20. Step488 Runtime Implementation Design Status

Step488 adds the design-only / planning-only implementation design for a
future metadata-only artifact writer CLI integration runtime:

[Frozen policy generation artifact writer CLI integration runtime implementation design](frozen_policy_generation_artifact_writer_cli_integration_runtime_implementation_design.md)

The design does not change the release-quality wrapper, workflow files,
Makefile, Python code/tests, fixture JSON, artifact body generation
integration, manifest writer integration, real-data use, metrics, or
production readiness.

## 21. Step489 Runtime Implementation Status

Step489 implements the initial standalone metadata-only artifact writer CLI
integration runtime module, CLI, and focused tests:

- `python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_runtime.py`
- `python/learner_state/tests/test_frozen_policy_generation_artifact_writer_cli_integration_runtime.py`

This fixture validator release-quality integration remains unchanged. The
Step489 runtime is added to a standalone Makefile target in Step491, but is
added to release-quality as a runtime smoke check in Step493.

## 22. Step490 Runtime Makefile Target Design Status

Step490 adds the docs-only standalone Makefile target design for the Step489
runtime CLI:

[Frozen policy generation artifact writer CLI integration runtime Makefile target design](frozen_policy_generation_artifact_writer_cli_integration_runtime_makefile_target_design.md)

This release-quality integration remains limited to the static runtime fixture
validator target. Step490 does not change the wrapper, change workflow files,
modify Makefile, change Python code/tests, change fixture JSON, perform
artifact writer CLI actual invocation, connect artifact body generation
integration, connect manifest writer integration, write files, or claim
production readiness.

## 23. Step494 Runtime Smoke Remote Run Record Workflow Design Status

Step494 adds the docs-only public-safe remote/manual run record workflow
design for the separate Step493 runtime smoke wrapper check:

[Frozen policy generation artifact writer CLI integration runtime release-quality remote run record workflow](frozen_policy_generation_artifact_writer_cli_integration_runtime_release_quality_remote_run_record_workflow.md)

The static runtime fixture validator release-quality integration remains
unchanged. Step494 does not create a remote status marker, change workflow
files, change the wrapper, change Makefile, change Python code/tests, change
fixture JSON, perform artifact writer CLI actual invocation, connect artifact
body generation integration, connect manifest writer integration, write files,
or claim production readiness.
