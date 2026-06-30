# Frozen Policy Generation Artifact Writer CLI Integration Runtime Release-Quality Integration Design

## 1. Scope

This document is the Step492 design-only release-quality integration design
for the Step491 standalone artifact writer CLI integration runtime Makefile
target.

This document does not implement the release-quality wrapper change, change
workflow YAML, change Makefile, change Python code or tests, change fixture
JSON, perform artifact writer CLI actual invocation, connect artifact body
generation integration, connect manifest writer integration, generate manifest
bodies, generate policy bodies, or implement file writing.

This document is not production readiness evidence, real-data readiness
evidence, model performance evidence, F1 evidence, accuracy evidence, ECE
evidence, AURCC evidence, artifact writer CLI actual invocation correctness
evidence, artifact body generation integration correctness evidence, manifest
writer integration correctness evidence, generated policy quality evidence, or
learner-state estimator correctness evidence.

## 2. Prior Completed Chain

- Step489 implemented the initial standalone metadata-only artifact writer CLI
  integration runtime module, CLI, and focused tests.
- Step490 created the docs-only standalone Makefile target design for that
  runtime CLI.
- Step491 implemented the standalone Makefile target:
  `check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime`.

Step491 adds a standalone target only. It does not add release-quality runtime
wrapper integration, workflow changes, artifact writer CLI actual invocation,
artifact body generation integration, manifest writer integration, generated
policy body generation, or file writing.

## 3. Target Makefile Target

Target:

```text
check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime
```

Target command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime \
  --fixture-case valid/valid_minimal_metadata_runtime_pass
```

The target runs one valid synthetic metadata-only fixture case and emits a
body-free public-safe runtime summary. It does not write files, invoke
artifact body generation, invoke manifest writer, generate manifest bodies,
generate policy bodies, or perform artifact writer CLI actual downstream
behavior.

## 4. Proposed Release-Quality Label

Recommended label:

```text
release_quality_check: learner-state frozen policy generation artifact writer CLI integration runtime smoke
```

The label should say `runtime smoke`. It must not imply production readiness,
real-data readiness, model performance, artifact writer CLI actual invocation
correctness, artifact body generation integration correctness, manifest writer
integration correctness, generated policy quality, or learner-state estimator
correctness.

## 5. Proposed Release-Quality Command

Recommended wrapper command:

```bash
make check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime
```

The wrapper should call the standalone Makefile target rather than duplicating
the Python CLI command. This keeps the release-quality wrapper aligned with
the local developer entrypoint.

## 6. Proposed Insertion Point

Recommended insertion point:

- after artifact writer fixture validation
- after artifact writer runtime smoke
- after artifact writer CLI integration fixture validation
- after artifact writer CLI integration runtime fixture validation
- before artifact body fixture validation
- before artifact body generation checks
- before manifest writer checks
- before config/scoring smoke checks

Recommended local order:

1. `release_quality_check: learner-state frozen policy generation artifact writer fixture validation`
2. `release_quality_check: learner-state frozen policy generation artifact writer runtime smoke`
3. `release_quality_check: learner-state frozen policy generation artifact writer CLI integration fixture validation`
4. `release_quality_check: learner-state frozen policy generation artifact writer CLI integration runtime fixture validation`
5. `release_quality_check: learner-state frozen policy generation artifact writer CLI integration runtime smoke`
6. `release_quality_check: learner-state frozen policy generation artifact body fixture validation`

Reasons:

- The artifact writer CLI integration fixture contract should be validated
  before runtime smoke.
- The runtime fixture contract should be statically validated before running
  the Step489 runtime boundary.
- The runtime smoke should stay with artifact writer / CLI integration checks.
- Artifact body generation and manifest writer chains remain separate and
  later.

## 7. Expected Release-Quality Output

Expected body-free public-safe output includes:

- `mode=artifact_writer_cli_integration_runtime`
- `runtime_schema_version=learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_v0.1`
- `status=pass`
- `reason_code=none`
- `exit_code_category=zero`
- `case_id=valid/valid_minimal_metadata_runtime_pass`
- `command_label=artifact_writer_cli_integration_runtime_future_boundary`
- `summary_mode=public_safe_count_only`
- `content_suppressed=True`
- `body_suppressed=True`
- `file_writing_enabled=False`
- `runtime_executed=True`
- `artifact_writer_cli_invoked=False`
- `artifact_writer_cli_invocation_planned=True`
- `artifact_body_generation_invoked=False`
- `manifest_writer_invoked=False`
- `production_readiness_claimed=False`
- `real_data_readiness_claimed=False`
- `performance_claims_present=False`

The output must remain metadata-only and body-free. It must not print fixture
JSON bodies, request bodies, pointer bodies, expected bodies, generated policy
bodies, artifact body payloads, manifest bodies, raw rows, logits,
probabilities, private paths, absolute paths, raw learner text, real
participant data, or performance metric bodies.

## 8. Expected Wrapper Behavior

The wrapper should:

- print the release-quality label
- print the Makefile command
- continue when the target exits `0`
- fail when the target exits nonzero
- preserve the target's public-safe output
- perform no extra parsing that prints fixture contents
- create no target-specific output files
- leave no target-specific residue
- keep artifact body generation and manifest writer checks separate

## 9. Failure Interpretation

Release-quality should fail if the target fails because of:

- missing runtime fixture root
- missing valid fixture case
- malformed metadata JSON
- unsupported runtime schema version
- case ID mismatch
- forbidden field detected
- forbidden string detected
- unsafe path detected
- file writing enabled unexpectedly
- artifact writer CLI actual invocation attempted unexpectedly
- artifact body generation invoked unexpectedly
- manifest writer invoked unexpectedly
- generated policy body, artifact body payload, or manifest body detected
- raw rows, logits, probabilities, private path, absolute path, raw learner
  text, or real participant data detected
- unsafe runtime output detected
- runtime internal error

These failures mean the runtime smoke or its safety boundary failed. They do
not prove model performance failure, production readiness failure, real-data
readiness failure, artifact body generation integration correctness, manifest
writer integration correctness, generated policy quality, or learner-state
estimator correctness.

## 10. Relation To Existing Release-Quality Chain

This proposed check:

- does not replace artifact writer fixture validation
- does not replace artifact writer runtime smoke
- does not replace artifact writer CLI integration fixture validation
- does not replace artifact writer CLI integration runtime fixture validation
- does not perform artifact writer CLI actual downstream invocation
- does not run artifact body generation integration
- does not run manifest writer integration
- does not write files
- checks only the Step489 runtime boundary over one valid synthetic
  metadata-only fixture case

The static runtime fixture validator remains the count-oriented contract check.
The proposed runtime smoke is a terminal invocation and safe-summary check.

## 11. Wrapper Implementation Guidance

A future Step493 wrapper implementation should add only a label and command
block to `scripts/check_release_quality.sh`.

The future wrapper block should look conceptually like:

```text
release_quality_check: learner-state frozen policy generation artifact writer CLI integration runtime smoke
command: make check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime
```

The implementation step should not change workflow YAML, Makefile, Python
code/tests, fixture JSON, artifact writer CLI actual invocation behavior,
artifact body generation integration, manifest writer integration, or
file-writing behavior.

## 12. Remote Status Marker Staging

After a future wrapper integration and actual remote/manual Release Quality
run, a separate remote/manual run record workflow design should define what
metadata can be recorded publicly.

Future status marker records should be pass-only, count-only or summary-only,
metadata-only, and raw-log-free. They must not copy full job output, GitHub log
blocks, screenshots containing raw logs, fixture bodies, request/pointer/
expected bodies, generated policy bodies, artifact body payloads, manifest
bodies, raw rows, logits/probabilities, private paths, absolute paths, raw
learner text, real participant data, or performance metric bodies.

## 13. Non-Claims

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
- release-quality wrapper implementation completed
- remote status marker created

## 14. Public-Safe Checklist

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

## 15. Planned Follow-Up Steps

Suggested future staging:

1. Step493: artifact writer CLI integration runtime release-quality wrapper
   integration.
2. Step494: remote/manual run record workflow design.
3. Step495: remote/manual status marker.

Artifact writer CLI actual invocation, artifact body generation integration,
manifest writer integration, manifest body generation, and file-writing
behavior remain separate future work.
