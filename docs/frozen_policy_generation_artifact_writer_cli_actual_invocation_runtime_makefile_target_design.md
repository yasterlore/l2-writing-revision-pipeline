# Frozen Policy Generation Artifact Writer CLI Actual Invocation Runtime Standalone Makefile Target Design

## 1. Scope

This document is the Step514 design-only / planning-only Makefile target
design for running the Step513 `actual_invocation_metadata_only` runtime path
from a future standalone Makefile target.

This document does not change the Makefile, change the release-quality
wrapper, change workflow files, change Python code/tests, change fixture JSON,
change the runtime implementation, connect artifact body generation
integration, connect manifest writer integration, or enable file writing.

This document is not evidence for production readiness, real-data readiness,
model performance, F1, accuracy, ECE, AURCC, artifact writer CLI actual
invocation correctness, runtime actual invocation correctness as a general
claim, artifact body generation integration correctness, manifest writer
integration correctness, generated policy quality, or learner-state estimator
correctness.

## 2. Prior Completed Chain

- Step489 implemented the initial artifact writer CLI integration runtime
  module, CLI, and focused tests with plan-only / no-invocation behavior.
- Step507 created the runtime update design for a future
  `actual_invocation_metadata_only` boundary.
- Step508 created the runtime fixture update design.
- Step509 extended the existing runtime fixture root to 54 synthetic
  metadata-only cases and 324 JSON files.
- Step510 created the runtime fixture validator update design.
- Step511 implemented runtime fixture validator v0.2 support for v0.1
  plan-only cases and v0.2 actual invocation metadata-only cases.
- Step512 created the final runtime implementation refinement design.
- Step513 updated the runtime module and focused tests so plan-only remains
  the default and explicit `--actual-invocation` enables runtime schema v0.2
  `actual_invocation_metadata_only` public-safe summaries.

Step513 did not add a standalone Makefile target for the explicit actual
invocation metadata-only runtime smoke. Step514 designs that future target
only.

## 3. Current Makefile Baseline

Existing related Makefile targets:

- `check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime`
  remains the plan-only runtime smoke target.
- `check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime-fixtures`
  remains the static runtime fixture validator target.

The existing plan-only runtime smoke target is included in the release-quality
wrapper through the earlier runtime integration chain. The static runtime
fixture validator target is also included through its earlier chain.

Current gap: there is no standalone Makefile target that runs the Step513
explicit `actual_invocation_metadata_only` runtime smoke.

## 4. Proposed New Makefile Target

Recommended target:

```text
check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-runtime
```

Recommended help text:

```text
Run artifact writer CLI actual invocation metadata-only runtime smoke
```

Recommended command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_cli_integration_runtime \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime \
  --fixture-case valid/valid_actual_invocation_minimal_metadata_only \
  --actual-invocation \
  --summary-only \
  --no-file-writing
```

Step514 does not implement this target.

## 5. Target Fixture Case Selection

Recommended fixture case:

```text
valid/valid_actual_invocation_minimal_metadata_only
```

Rationale:

- it is a valid v0.2 actual invocation metadata-only fixture case
- it is body-free and synthetic-only
- it keeps file writing disabled
- it does not invoke artifact body generation
- it does not invoke the manifest writer
- it expects a deterministic public-safe summary

A future separate target may add a fail-closed smoke over a controlled invalid
case if there is a distinct design need. Step514 does not add that target.

## 6. Expected Safe Output

The future target should emit only public-safe summary lines. Expected fields
include:

- `mode=artifact_writer_cli_integration_runtime`
- `runtime_schema_version=learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_v0.2`
- `status=pass`
- `reason_code=none`
- `exit_code_category=zero`
- `case_id=valid/valid_actual_invocation_minimal_metadata_only`
- `invocation_mode=actual_invocation_metadata_only`
- `summary_mode=public_safe_count_only`
- `content_suppressed=True`
- `body_suppressed=True`
- `runtime_actual_invocation_enabled=True`
- `artifact_writer_cli_invoked=True`
- `artifact_writer_cli_invocation_planned=False`
- `artifact_writer_cli_exit_code_category=zero`
- `artifact_writer_cli_output_scanned=True`
- `artifact_writer_cli_output_body_free=True`
- `raw_stdout_body_suppressed=True`
- `raw_stderr_body_suppressed=True`
- `runtime_actual_invocation_safety_scan_passed=True`
- `runtime_actual_invocation_fail_closed=False`
- `artifact_body_generation_invoked=False`
- `manifest_writer_invoked=False`
- `file_writing_enabled=False`
- `production_readiness_claimed=False`
- `real_data_readiness_claimed=False`
- `performance_claims_present=False`

Boolean spelling should follow the runtime output in the implementation step.
Step514 does not change output formatting.

## 7. Safety Boundary

The proposed target must not:

- print raw stdout/stderr body
- print fixture JSON body
- print request, pointer, or expected body
- print artifact body payload
- print manifest body
- print generated policy body
- print raw rows
- print logits or probabilities
- print private or absolute path values
- print raw learner text
- use real participant data
- write artifact files
- write manifest files
- invoke artifact body generation
- invoke manifest writer
- claim production readiness
- claim real-data readiness
- claim model performance

The target remains a metadata-only runtime smoke over a synthetic fixture case.
It is not a file-writing, artifact body generation, or manifest writer target.

## 8. Failure Interpretation

If the future target fails, the failure means the actual invocation
metadata-only runtime smoke failed.

Possible public-safe interpretations include:

- unsafe output was detected
- an unexpected nonzero summary was returned
- a timeout category was returned unexpectedly
- an unsupported schema was encountered
- the fixture case was missing
- CLI usage flags were inconsistent
- a safety scan failed

The failure does not prove an artifact writer CLI correctness issue in
general. It does not prove an artifact body generation issue, manifest writer
issue, or model performance issue. It must be interpreted through public-safe
reason codes only. Raw stdout/stderr must not be copied into docs or reports.

## 9. Relationship To Existing Targets

Existing target:

```text
check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime
```

This remains the plan-only runtime smoke.

Existing target:

```text
check-learner-state-frozen-policy-generation-artifact-writer-cli-integration-runtime-fixtures
```

This remains the static runtime fixture validator.

The proposed new target is only for explicit actual invocation metadata-only
runtime smoke. It does not replace the existing plan-only runtime smoke or the
static fixture validator. Release-quality integration should be a separate
design step, and wrapper integration should be a separate implementation step.

## 10. Proposed Implementation Checks For The Next Step

If Step515 implements the target, it should check:

- `make help` includes the target and help text
- the new target runs and returns the expected safe v0.2 summary
- the existing plan-only runtime target still passes
- the existing runtime fixture validator target still passes
- focused runtime tests still pass
- full Python tests pass
- compileall passes
- the release-quality wrapper still passes if it is not yet updated
- fixture JSON diff remains empty
- Makefile diff is limited to the new target
- wrapper and workflow diffs remain empty
- code/docs/output safety scan passes
- residue check passes

## 11. Future Release-Quality Staging

Possible follow-up:

- Step515: standalone Makefile target implementation
- Step516: release-quality integration design
- Step517: release-quality wrapper integration
- Step518: remote/manual run record workflow design
- Step519: remote status marker

Step514 does not proceed to those stages.

## 12. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1, accuracy, ECE, or AURCC achievement
- artifact writer CLI actual invocation correctness in general
- runtime actual invocation correctness in general
- artifact body generation integration correctness
- manifest writer integration correctness
- generated policy quality
- learner-state estimator correctness
- Makefile target implementation

## 13. Public-Safe Checklist

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
