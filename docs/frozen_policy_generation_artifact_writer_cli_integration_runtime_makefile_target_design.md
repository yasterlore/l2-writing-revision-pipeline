# Frozen Policy Generation Artifact Writer CLI Integration Runtime Makefile Target Design

## 1. Scope

This document is the Step490 design-only Makefile target design for running
the Step489 artifact writer CLI integration runtime module from a future
standalone Makefile target.

Step491 implements the standalone Makefile target described here. This
document still does not change the release-quality wrapper, change workflow
YAML, change Python code or tests, change fixture JSON, invoke the artifact
writer CLI for actual downstream work, connect artifact body generation
integration, connect manifest writer integration, generate manifest bodies,
generate policy bodies, or implement file writing.

This document is not production readiness evidence, real-data readiness
evidence, model performance evidence, F1 evidence, accuracy evidence, ECE
evidence, AURCC evidence, artifact writer CLI actual invocation correctness
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
- Step482 created the standalone Makefile target design for the static
  runtime fixture validator.
- Step483 implemented the static runtime fixture validator Makefile target.
- Step484 created the release-quality integration design for that static
  validator target.
- Step485 added the static runtime fixture validator target to the
  release-quality wrapper.
- Step486 created the public-safe remote/manual run record workflow design.
- Step487 created the public-safe remote/manual status marker for the static
  runtime fixture validator wrapper check.
- Step488 created the runtime implementation design.
- Step489 implemented the initial standalone metadata-only runtime module,
  CLI, and focused tests.
- Step490 created this Makefile target design.
- Step491 implemented the standalone Makefile target.

Step491 adds a standalone Makefile target only. It does not add
release-quality runtime wrapper integration, workflow changes, artifact writer
CLI actual invocation, artifact body generation, manifest writer integration,
generated policy body generation, or file writing.

## 3. Current Runtime CLI

Step489 runtime module:

`python/learner_state/frozen_policy_generation_artifact_writer_cli_integration_runtime.py`

Step489 CLI:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime
```

The runtime emits a body-free public-safe summary with:

- `mode=artifact_writer_cli_integration_runtime`
- `runtime_schema_version=learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_v0.1`
- `artifact_writer_cli_invoked=false`
- `artifact_body_generation_invoked=false`
- `manifest_writer_invoked=false`
- `file_writing_enabled=false`

The runtime can consume the Step479 runtime fixture root or explicit metadata
paths. It returns an invocation plan summary instead of invoking artifact body
generation or manifest writer behavior.

## 4. Target Name

Implemented target name:

```text
check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime
```

Rationale:

- It stays in the learner-state target namespace.
- It names frozen policy generation explicitly.
- It distinguishes runtime execution from static runtime fixture validation.
- It keeps the existing artifact writer CLI integration wording.
- It is suitable for future release-quality labels without implying artifact
  body generation, manifest writer integration, file writing, or production
  readiness.

## 5. Target Command

Implemented Makefile command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime \
  --fixture-case valid/valid_minimal_metadata_runtime_pass
```

The target uses one valid synthetic metadata-only fixture case as a runtime
smoke. It should not read or print fixture JSON bodies. It should not
use invalid fixture cases for the standalone smoke; invalid fail-closed
coverage remains in focused tests and the Step481 static runtime fixture
validator.

The target uses the runtime's default human summary for the initial Makefile
target. A later target may choose `--json` only if a separate design
requires machine-readable summary checks without copying payload bodies.

## 6. Help Text

Implemented help text:

```text
check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime  Run artifact writer CLI integration runtime smoke
```

## 7. Expected Safe Output

The target should allow only body-free public-safe summary output.

Expected safe fields or lines include:

- mode
- runtime schema version
- status
- reason code
- exit code category
- case ID
- command label
- summary mode
- suppression flags
- no-oracle flags
- synthetic-only and metadata-only flags
- file-writing disabled flag
- downstream invocation flags
- production, real-data, and performance claim flags

Expected success summary for the recommended valid fixture:

- status: `pass`
- exit code category: `zero`
- content suppressed: `true`
- body suppressed: `true`
- file writing enabled: `false`
- artifact writer CLI invoked: `false`
- artifact writer CLI invocation planned: `true`
- artifact body generation invoked: `false`
- manifest writer invoked: `false`
- production readiness claimed: `false`
- real-data readiness claimed: `false`
- performance claims present: `false`

## 8. Exit-Code Behavior

The target should not transform the runtime CLI exit code.

Expected interpretation:

- runtime exit `0`: Makefile target passes.
- runtime exit `1`: Makefile target fails because the runtime failed closed.
- runtime exit `2`: Makefile target fails because of usage or input error.
- any other exit code: Makefile target fails.

The standalone runtime smoke should use a valid fixture case. It should not
turn expected invalid cases into successful Makefile target runs.

## 9. File-Writing And Residue Policy

The Makefile target should:

- write no files
- create no artifact body output
- create no manifest output
- create no generated policy body output
- create no temp result file
- require no cleanup step in the normal path
- leave no residue after failure

Any future file-writing option requires a separate design, fixture, validator,
implementation, Makefile, release-quality, and remote status chain.

## 10. Forbidden Output And Input Policy

The target must not print or pass through:

- raw GitHub Actions logs
- full job output
- copied GitHub log blocks
- screenshots containing raw logs
- fixture JSON body
- request body
- pointer body
- expected body
- written file JSON body
- manifest body
- artifact body payload
- generated policy body
- raw rows
- logits or probabilities
- private paths
- absolute paths
- raw learner text
- real participant data
- performance metric body

Field names and reason-code names may appear as controlled safety terms. They
must not be accompanied by body payloads or actual private values.

## 11. Relation To Existing Targets

Existing static runtime fixture validator target:

`check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime-fixtures`

That target validates the 30-case / 180-JSON synthetic metadata-only fixture
root and is already in the release-quality wrapper.

Implemented runtime smoke target:

`check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime`

The target runs the Step489 runtime CLI over one valid metadata-only fixture
case. It verifies terminal invocation and safe runtime summary behavior, but
it does not replace the static fixture validator, focused tests, or future
release-quality integration.

## 12. Future Release-Quality Staging

A later release-quality integration design may add the proposed target to the
wrapper after the static artifact writer CLI integration runtime fixture
validation check and before artifact body fixture validation.

That future design should define:

- wrapper label
- command
- insertion point
- expected safe output
- failure interpretation
- remote/manual run record workflow
- remote status marker staging

Step490 does not change the wrapper.
Step491 also does not change the wrapper.

## 13. Verification Plan For Future Implementation

For the Step491 implementation and future maintenance, focused verification
should run:

- `git status --short`
- the new Makefile target
- the Step489 focused runtime tests
- the Step481 static runtime fixture validator target
- `git diff -- Makefile`
- `git diff -- scripts/check_release_quality.sh`
- `git diff -- .github/workflows/ci.yml`
- `git diff -- .github/workflows/release-quality.yml`
- `git diff -- tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime`
- `git diff --check`
- conflict marker scan
- docs/code safety scan
- residue checks for artifact body and manifest tmp roots

The Step491 implementation keeps release-quality wrapper and workflow YAML
unchanged. Future steps should do the same unless explicitly scoped.

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
- release-quality runtime wrapper integration implemented

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

## 16. Planned Follow-Up Steps

Suggested future staging:

1. Step492: artifact writer CLI integration runtime release-quality
   integration design.
2. Step493: artifact writer CLI integration runtime release-quality wrapper
   integration.
3. Step494: remote/manual run record workflow design.
4. Step495: remote/manual status marker.

Artifact writer CLI actual invocation, artifact body generation integration,
manifest writer integration, manifest body generation, and file-writing
behavior remain separate future work.
