# Actual-Controlled Artifact Body Generation Runtime Invocation Release Quality Integration Design

## 1. Title

Actual-Controlled Artifact Body Generation Runtime Invocation Release Quality Integration Design

## 2. Scope

This document is a design-only / docs-only plan for integrating the Step591 and Step595 standalone Makefile targets into the release-quality wrapper in a future Step597.

Step596 does not change the release-quality wrapper, Makefile, workflow files, Python code/tests, fixture JSON, runtime implementation, validator implementation, artifact body generation implementation, artifact body generation integration, manifest writer integration, manifest body generation, generated policy body generation, artifact body file writing, or manifest file writing.

This document does not implement release-quality integration, does not invoke manifest writer, does not enable file writing, and is not evidence for production readiness, real-data readiness, or model performance.

## 3. Prior Chain Dependency

- Step569-Step574: planned-only runtime invocation fixture contract, fixture root, validator, and standalone Makefile target chain completed.
- Step575-Step579: planned-only v0.3 runtime mode and standalone Makefile target chain completed.
- Step580-Step583: planned-only release-quality integration, remote/manual run record workflow, and remote status marker chain completed.
- Step584: planned-only v0.3 release-quality chain final safety review completed.
- Step585-Step587: actual-controlled design, fixture/schema contract, and fixture root chain completed.
- Step588-Step591: actual-controlled fixture validator design, implementation, and standalone Makefile target chain completed.
- Step592-Step595: actual-controlled runtime refinement, v0.4 implementation, target design, and standalone Makefile target chain completed.

Step595 provides the standalone v0.4 runtime smoke target. The actual-controlled targets are not yet release-quality integrated.

## 4. Targets To Integrate

### Target 1: Actual-Controlled Fixture Validation

Proposed label:

```text
release_quality_check: learner-state frozen policy generation actual-controlled artifact body generation runtime invocation fixture validation
```

Command:

```bash
make check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation-fixtures
```

Expected public-safe summary:

- `total_cases=36`
- `valid_cases=6`
- `invalid_cases=30`
- `total_json_files=252`
- `pass_cases=6`
- `usage_error_cases=3`
- `fail_closed_cases=26`
- `mismatch_cases=1`
- `content_suppressed=true`
- `body_suppressed=true`
- `metadata_only_checked=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`

### Target 2: Actual-Controlled v0.4 Runtime Smoke

Proposed label:

```text
release_quality_check: learner-state frozen policy generation actual-controlled artifact body generation runtime invocation smoke
```

Command:

```bash
make check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation
```

Expected public-safe summary:

- `runtime_schema_version=learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4`
- `status=pass`
- `reason_code=none`
- `integration_mode=artifact-body-runtime-invocation-controlled`
- `artifact_body_runtime_invoked=True`
- `artifact_body_runtime_invocation_planned=False`
- `artifact_body_runtime_mode=controlled_metadata_only_invocation`
- `artifact_body_generation_cli_invoked=True`
- `artifact_body_generation_cli_output_scanned=True`
- `artifact_body_generation_cli_output_body_free=True`
- `safe_metadata_body_field_count=5`
- `artifact_body_payload_emitted=False`
- `raw_stdout_body_suppressed=True`
- `raw_stderr_body_suppressed=True`
- `manifest_writer_invoked=False`
- `file_writing_enabled=False`
- `runtime_safety_scan_passed=True`
- `unsafe_signal_count=0`

## 5. Integration Options

### Option A: Integrate Fixture Validator First, Runtime Smoke Later

Benefits:

- Smallest wrapper change.
- Lowest runtime smoke staging risk.
- Keeps the fixture contract gate first.

Risks and tradeoffs:

- Leaves v0.4 runtime smoke outside release-quality temporarily.
- Slower completion of the actual-controlled release-quality chain.

Implementation complexity: low.

Safety boundary clarity: high, but incomplete for the v0.4 smoke until a later step.

### Option B: Integrate Both Actual-Controlled Targets Together

Benefits:

- Adds fixture validation first, then runtime smoke.
- Mirrors the Step580/Step581 planned-only pattern.
- Keeps the v0.4 smoke gated by fixture root validation.
- Keeps the actual-controlled checks adjacent and understandable.

Risks and tradeoffs:

- Slightly larger wrapper diff than Option A.
- Requires explicit ordering verification in Step597.

Implementation complexity: moderate and localized to the wrapper.

Safety boundary clarity: high.

### Option C: Integrate Runtime Smoke Only

Benefits:

- Small wrapper change.

Risks and tradeoffs:

- Runtime smoke would run without release-quality fixture validation first.
- Weakens staged fixture-contract gating.

Implementation complexity: low.

Safety boundary clarity: low. This option is not recommended.

### Option D: Defer Release-Quality Integration

Benefits:

- Avoids wrapper churn if standalone targets are unstable.

Risks and tradeoffs:

- Leaves checks manual-only.
- Slows the actual-controlled release-quality chain.

Implementation complexity: none in the current step.

Safety boundary clarity: acceptable as a pause, but it does not advance wrapper coverage.

## 6. Recommended Option

Recommend Option B unless Step597 discovers a concrete blocker.

Required order:

1. actual-controlled fixture validation
2. actual-controlled v0.4 runtime smoke

Rationale:

- the fixture root and schema contract should be validated before runtime smoke
- the ordering mirrors the planned-only release-quality pattern
- actual-controlled checks remain adjacent and readable
- standalone targets remain available
- existing planned-only checks remain unchanged
- workflow files remain unchanged
- no manifest writer invocation or file writing is added

## 7. Proposed Insertion Point In `scripts/check_release_quality.sh`

Recommended insertion:

- after existing planned-only v0.3 runtime invocation smoke
- before artifact body fixture validation and artifact body generation CLI checks

Expected local order around the insertion area:

1. safe-metadata runtime smoke
2. planned-only runtime invocation fixture validation
3. planned-only v0.3 runtime invocation smoke
4. actual-controlled fixture validation
5. actual-controlled v0.4 runtime smoke
6. artifact body fixture validation
7. artifact body generation CLI smoke
8. artifact body generation safe-metadata CLI smoke

If the current wrapper order differs, Step597 should place the new checks adjacent to the planned-only runtime invocation checks and before broader artifact body / manifest writer checks.

## 8. Expected Step597 Wrapper Changes

Step597 should:

- update `scripts/check_release_quality.sh`
- add two `run_check` entries or the equivalent wrapper pattern used locally
- add the fixture validation label and command first
- add the v0.4 runtime smoke label and command second
- not modify Makefile
- not modify Python code/tests
- not modify fixture JSON
- not modify workflows
- not implement runtime changes
- not invoke manifest writer
- not enable file writing
- run both standalone targets
- run `make check-release-quality`
- update root README and full technical specification related docs because Step597 is an implementation step

## 9. Relationship To Existing Release-Quality Checks

Existing release-quality checks should remain unchanged:

- planned-only runtime invocation fixture validation
- planned-only v0.3 runtime invocation smoke
- artifact body fixture validation
- artifact body generation CLI smoke
- artifact body generation safe-metadata CLI smoke
- manifest writer checks
- general Python checks

The actual-controlled release-quality checks:

- add additional coverage for the v0.4 fixture root and v0.4 runtime smoke
- do not replace planned-only checks
- do not replace artifact body safe-metadata CLI smoke
- do not replace manifest writer checks
- do not prove artifact body payload correctness
- do not prove runtime correctness generally
- do not imply production readiness

## 10. Safety Boundary

The proposed release-quality checks must:

- run only standalone Makefile targets
- use synthetic metadata-only fixtures
- output only count-only / public-safe metadata
- not print fixture JSON body
- not print request body
- not print pointer body
- not print expected body
- not print artifact body payload
- not print manifest body
- not print generated policy body
- not print raw stdout/stderr body
- not print raw rows
- not print logits/probabilities
- not print private/absolute path values
- not print raw learner text
- not use real participant data
- not invoke manifest writer
- not enable file writing
- not produce residue

## 11. Failure Interpretation

- actual-controlled fixture validation failure means fixture root, schema, or validator contract inconsistency.
- actual-controlled runtime smoke failure means the primary v0.4 controlled metadata-only smoke or safety scan failed.
- failure does not imply real-data failure.
- failure does not imply model performance failure.
- pass does not prove runtime correctness generally.
- pass does not prove artifact body payload correctness.
- pass does not imply production readiness or real-data readiness.

## 12. Validation Plan For Step597

Step597 should run these checks in order:

- `git status --short`
- `make help` check for both standalone actual-controlled targets
- `make check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation-fixtures`
- `make check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation`
- direct actual-controlled fixture validator CLI
- direct v0.4 runtime CLI
- focused runtime tests
- focused actual-controlled fixture validator tests
- existing planned-only fixture validator target
- existing planned-only v0.3 runtime target
- existing safe-metadata runtime target
- existing artifact body safe-metadata CLI smoke
- `make check-python`
- `PYTHONPATH=python python3 -m compileall python`
- `make check-release-quality`
- fixture JSON diff check
- targeted diff for wrapper/docs
- `git diff --check`
- conflict marker scan
- code/docs safety scan
- forbidden target diff check
- residue check

## 13. Non-Equivalence Cautions

- release-quality integration design is not wrapper implementation
- future release-quality pass will not prove runtime correctness generally
- future release-quality pass will not prove artifact body payload correctness
- v0.4 actual-controlled smoke is still metadata-only / body-free smoke
- planned-only v0.3 pass remains not actual-controlled invocation
- artifact body generation safe-metadata CLI smoke is not equivalent to v0.4 runtime smoke
- count-only metadata is not free-form body safety proof
- manifest writer validators are separate
- release-quality success is not production readiness
- synthetic-only pass is not real-data readiness

## 14. Non-Claims

- production readiness is not claimed
- real-data readiness is not claimed
- model performance is not claimed
- F1 / accuracy / ECE / AURCC achievement is not claimed
- artifact body generation integration correctness is not claimed
- artifact body generation runtime correctness generally is not claimed
- manifest writer integration correctness is not claimed
- manifest writer file-writing production readiness is not claimed
- artifact body payload correctness is not claimed
- safe-metadata free-form body safety is not claimed
- manifest body generation correctness is not claimed
- generated policy quality is not claimed
- learner-state estimator correctness is not claimed
- artifact writer CLI actual invocation correctness generally is not claimed
- runtime actual invocation correctness generally is not claimed

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

## 16. Recommended Next Step

Recommended next step:

- Step597: actual-controlled runtime invocation release-quality wrapper integration

Step597 should update only the wrapper and necessary README/docs. It should not change Makefile, Python code/tests, fixture JSON, workflow files, runtime implementation, validator implementation, manifest writer integration, or file writing.

## Step597 Implementation Status

Step597 adds both proposed checks to `scripts/check_release_quality.sh` in the
recommended order:

1. `release_quality_check: learner-state frozen policy generation actual-controlled artifact body generation runtime invocation fixture validation`
2. `release_quality_check: learner-state frozen policy generation actual-controlled artifact body generation runtime invocation smoke`

The checks run after the planned-only v0.3 runtime invocation smoke and before
artifact body fixture / CLI checks. Step597 does not change Makefile,
workflow files, Python code/tests, fixture JSON, runtime implementation,
manifest writer integration, or file writing.

## Step598 Remote Run Record Workflow Reference

Step598 adds
`docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_release_quality_remote_run_record_workflow.md`
as a design-only / docs-only workflow for a future public-safe status marker
covering the Step597 wrapper checks. It does not create the marker or change
wrapper, Makefile, workflow files, Python code/tests, fixture JSON, manifest
writer integration, or file writing.

## Step599 Remote Run Status Reference

Step599 adds the public-safe status marker
`docs/status/learner_state_frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_release_quality_remote_run_status.md`
for the remote Release Quality run after Step597 wrapper integration. It does
not change wrapper, Makefile, workflow files, Python code/tests, fixture JSON,
manifest writer integration, or file writing.

## Step600 Final Safety Review Reference

Step600 adds
`docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_release_quality_chain_final_safety_review.md`
as a final-safety-review / docs-only review for the Step585-Step599
actual-controlled release-quality chain. This integration design remains
unchanged, and no wrapper, Makefile, workflow, Python, fixture JSON, runtime,
manifest writer, or file-writing change is made by Step600.

## Step601 Planning Reference

Step601 adds
`docs/frozen_policy_generation_actual_controlled_post_final_safety_review_next_boundary_planning.md`
as a planning-only / docs-only next-boundary plan after Step600. This
release-quality integration design remains unchanged.

## Step602 Design Reference

Step602 adds
`docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_design.md`
as a design-only / docs-only plan for a future all-valid multi-case runtime
smoke. This release-quality integration design remains unchanged.

## Step603 Fixture Matrix Contract Reference

Step603 adds
`docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_fixture_matrix_contract_design.md`
as a design-only / docs-only fixture/matrix contract for a future all-valid
multi-case runtime smoke. This release-quality integration design remains
unchanged.

## Step604 Implementation Reference

Step604 implements the all-valid multi-case runner as a direct CLI-only Python module with focused tests. This release-quality integration design remains for the prior actual-controlled checks; the new Step604 runner is not yet Makefile-targeted or release-quality integrated.

## Step605 Makefile Target Design Reference

Step605 designs the future standalone Makefile target for the Step604 runner. This release-quality integration design remains unchanged; release-quality integration for the multi-case runner is still deferred.

## Step606 Makefile Target Implementation Reference

Step606 adds the standalone Makefile target for the Step604 runner. This release-quality integration design remains unchanged; the new target is not added to release-quality in Step606.

## Step607 Multi-Case Release-Quality Integration Design Reference

Step607 adds `docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_release_quality_integration_design.md` as the future wrapper integration design for the Step606 standalone multi-case target. This earlier release-quality integration design remains unchanged and continues to cover the Step591 fixture validator plus Step595 single-case smoke checks.

## Step608 Multi-Case Release-Quality Integration Reference

Step608 adds the Step606 standalone multi-case target to `scripts/check_release_quality.sh` after the Step595 single-case smoke. This earlier release-quality integration design remains unchanged and continues to cover the Step591 fixture validator plus Step595 single-case smoke checks.
