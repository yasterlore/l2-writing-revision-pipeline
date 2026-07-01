# Frozen Policy Generation Artifact Writer CLI Actual Invocation Runtime Release Quality Integration Design

## 1. Title

Frozen Policy Generation Artifact Writer CLI Actual Invocation Runtime Release
Quality Integration Design

## 2. Scope

This document is a design-only / planning-only release-quality integration
design for adding the Step515 standalone Makefile target to a future
release-quality wrapper.

This step does not:

- change the release-quality wrapper
- change workflow files
- change the Makefile
- change Python code/tests
- change fixture JSON
- change runtime implementation
- implement artifact body generation integration
- implement manifest writer integration
- enable file writing
- prove production readiness, real-data readiness, or model performance

The proposed check is a metadata-only runtime smoke over one synthetic fixture
case. It remains body-free, public-safe, summary-only, synthetic-only,
no-oracle, and fail-closed.

## 3. Prior Completed Chain

- Step489 implemented the initial artifact writer CLI integration runtime
  module, CLI, and focused tests with plan-only behavior.
- Step507 created the runtime update design for a future metadata-only
  actual invocation boundary.
- Step508 created the runtime fixture update design.
- Step509 expanded the runtime fixture root to include v0.2
  `actual_invocation_metadata_only` cases.
- Step510 created the runtime fixture validator update design.
- Step511 implemented static validator v0.2 support for the 54-case /
  324-JSON runtime fixture root.
- Step512 created the runtime implementation refinement design.
- Step513 implemented explicit `actual_invocation_metadata_only` runtime
  support while preserving plan-only as the default.
- Step514 created the standalone Makefile target design.
- Step515 implemented the standalone Makefile target.

Step515 adds the standalone target only. It is not connected to the
release-quality wrapper yet.

## 4. Target Standalone Makefile Check

- target: `check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-runtime`
- help text: `Run artifact writer CLI actual invocation metadata-only runtime smoke`
- command: `make check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-runtime`
- fixture case: `valid/valid_actual_invocation_minimal_metadata_only`
- runtime schema: `learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_v0.2`
- invocation mode: `actual_invocation_metadata_only`

The standalone target exercises one public-safe v0.2 runtime case. It does not
write artifact files, write manifest files, invoke artifact body generation,
or invoke manifest writer.

## 5. Proposed Release-Quality Label / Command

Proposed release-quality wrapper label:

```text
release_quality_check: learner-state frozen policy generation artifact writer CLI actual invocation runtime smoke
```

Proposed release-quality wrapper command:

```bash
make check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-runtime
```

Step516 does not add this label or command to
`scripts/check_release_quality.sh`.

Step517 adds this label and command to `scripts/check_release_quality.sh`.
Step517 does not change workflow files, Makefile, Python code/tests, fixture
JSON, runtime implementation, artifact body generation integration, manifest
writer integration, file writing, real-data use, metric use, or production
readiness claims.

## 6. Proposed Insertion Point

Recommended insertion point:

- after learner-state frozen policy generation artifact writer CLI integration
  runtime smoke
- after learner-state frozen policy generation artifact writer CLI actual
  invocation fixture validation
- before learner-state frozen policy generation artifact body fixture
  validation

If the current wrapper order has actual invocation fixture validation after
integration runtime smoke and before artifact body fixture validation, the new
runtime smoke should be placed immediately after the actual invocation fixture
validation and before artifact body fixture validation.

Rationale:

- the plan-only runtime smoke remains first
- the static actual invocation fixture validation remains adjacent to the
  actual invocation boundary
- the actual invocation metadata-only runtime smoke runs before the artifact
  body chain
- artifact body generation, manifest writer, and file-writing checks remain
  separate boundaries

## 7. Expected Safe Output

Future wrapper output should preserve the Step515 public-safe runtime summary
fields, including:

- `mode=artifact_writer_cli_integration_runtime`
- `runtime_schema_version=learner_state_frozen_policy_generation_artifact_writer_cli_integration_runtime_v0.2`
- `status=pass`
- `reason_code=none`
- `exit_code_category=zero`
- `case_id=valid/valid_actual_invocation_minimal_metadata_only`
- `invocation_mode=actual_invocation_metadata_only`
- `summary_mode=summary_only_public_safe`
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

Boolean casing should remain consistent with the current runtime output.
Step516 does not change runtime implementation.

## 8. Safety Boundary

The proposed release-quality check must not:

- print raw stdout/stderr body
- print fixture JSON body
- print request / pointer / expected body
- print artifact body payload
- print manifest body
- print generated policy body
- print raw rows
- print logits / probabilities
- print private / absolute path values
- print raw learner text
- use real participant data
- write artifact files
- write manifest files
- invoke artifact body generation
- invoke manifest writer
- claim production readiness
- claim real-data readiness
- claim model performance

The wrapper should preserve the standalone target's summary-only output and
should not add parsing that reveals suppressed content.

## 9. Failure Interpretation

If the future wrapper check fails, the failure means the actual invocation
metadata-only runtime smoke failed inside the release-quality wrapper.

Possible public-safe causes include:

- unsafe output
- unexpected nonzero summary
- timeout
- unsupported schema
- missing fixture
- CLI usage mismatch
- safety scan failure

A failure does not prove:

- artifact writer CLI correctness issue in general
- artifact body generation issue
- manifest writer issue
- model performance issue

Failure review must use public-safe reason codes only. Raw stdout/stderr must
not be copied into docs or reports.

## 10. Relationship To Existing Release-Quality Checks

The proposed new check:

- leaves the existing plan-only runtime smoke unchanged
- leaves the existing runtime fixture validator check unchanged
- leaves the existing actual invocation static fixture validation check
  unchanged
- adds an explicit actual invocation metadata-only runtime smoke
- keeps artifact body fixture validation separate and later
- keeps artifact body generation smoke checks separate and later
- keeps manifest writer checks separate and later
- leaves the final `release_quality_check` behavior unchanged

It is not a replacement for static fixture validation, plan-only runtime
smoke, artifact body checks, manifest writer checks, Python checks, Rust
checks, or logger-web checks.

## 11. Proposed Wrapper Implementation Checks For The Next Step

If Step517 adds the wrapper block, it should check:

- wrapper label / command present
- wrapper insertion point correct
- new standalone target still passes
- existing plan-only runtime target still passes
- runtime fixture validator target still passes
- direct runtime CLI actual invocation smoke still passes
- focused runtime tests still pass
- focused validator tests still pass
- full Python tests pass
- compileall passes
- release-quality wrapper passes
- fixture JSON diff remains empty
- Makefile diff remains empty
- wrapper diff is limited to the new label / command block
- workflow diff remains empty
- code/docs/output safety scan passes
- residue check passes

## 12. Future Staging

Possible follow-up:

- Step517: release-quality wrapper integration
- Step518: remote/manual run record workflow design
- Step519: remote status marker

Step516 does not proceed to those stages.

Step517 implements the wrapper integration stage by adding only the label /
command block described above.

## 13. Step517 Wrapper Integration Status

Step517 adds the release-quality wrapper check:

```text
release_quality_check: learner-state frozen policy generation artifact writer CLI actual invocation runtime smoke
```

Wrapper command:

```bash
make check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-runtime
```

Insertion point:

- after `release_quality_check: learner-state frozen policy generation artifact writer CLI actual invocation fixture validation`
- before `release_quality_check: learner-state frozen policy generation artifact body fixture validation`

The wrapper integration preserves the expected safe output and safety boundary
defined in this document. It does not change workflow files, Makefile, Python
code/tests, fixture JSON, runtime implementation, artifact body generation
integration, manifest writer integration, file writing, real-data use, metric
use, or production readiness claims.

## 14. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- artifact writer CLI actual invocation correctness in general
- runtime actual invocation correctness in general
- artifact body generation integration correctness
- manifest writer integration correctness
- generated policy quality
- learner-state estimator correctness
- production readiness evidence from wrapper inclusion

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
