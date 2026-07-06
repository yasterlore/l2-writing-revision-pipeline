# Actual-Controlled v0.4 Deferred Invalid-Case usage_error / mismatch Smoke Makefile Target Design

## 1. Title

Actual-Controlled v0.4 Deferred Invalid-Case usage_error / mismatch Smoke Makefile Target Design

## 2. Scope

This document is a design-only / docs-only plan for running the Step626 direct deferred invalid-case usage_error / mismatch CLI as a future standalone Makefile target.

This Step627 document does not change Makefile targets, release-quality wrapper entries, workflows, Python code/tests, fixture JSON, runtime implementation, validator implementation, payload audit implementation, manifest writer integration, or file writing. It is not evidence of production readiness, real-data readiness, or model performance.

## 3. Prior Chain Dependency

- Step622 accepted only the fixed 26 selected invalid fail_closed runtime smoke boundary.
- Step623 recommended deferred usage_error / mismatch invalid runtime matrix design.
- Step624 designed the combined deferred invalid status matrix.
- Step625 fixed exact 4 selected deferred invalid cases and aggregate contract.
- Step626 implemented direct CLI-only deferred invalid usage_error / mismatch runner and focused tests.
- Step626 direct CLI passes.
- Step626 has no Makefile target yet.
- Step626 is not release-quality integrated yet.

## 4. Target Runtime CLI

Runtime module:

- `python/learner_state/frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke.py`

Direct CLI:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled \
  --case-selection deferred-invalid-usage-error-mismatch \
  --summary-only \
  --no-file-writing \
  --no-manifest-writer \
  --fail-closed-on-unsafe-output
```

Fixture root:

- `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled/`

Case selection:

- `deferred-invalid-usage-error-mismatch`

Matrix:

- `actual_controlled_v0_4_deferred_invalid_usage_error_mismatch_runtime_smoke`

## 5. Proposed Makefile Target

Recommended target name:

```text
check-learner-state-frozen-policy-generation-actual-controlled-v0-4-deferred-invalid-case-runtime-usage-error-mismatch-smoke
```

Recommended help text:

```text
Run actual-controlled v0.4 deferred invalid-case usage_error/mismatch smoke
```

Recommended command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled --case-selection deferred-invalid-usage-error-mismatch --summary-only --no-file-writing --no-manifest-writer --fail-closed-on-unsafe-output
```

Do not add the target in Step627. Step628 should implement it.

## 6. Expected Target Output

The future Makefile target should produce the same public-safe summary as the Step626 direct CLI. Expected fields include:

- mode=actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke
- schema_version=learner_state_frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke_v0.1
- status=pass
- reason_code=none
- matrix_name=actual_controlled_v0_4_deferred_invalid_usage_error_mismatch_runtime_smoke
- case_selection=deferred-invalid-usage-error-mismatch
- selected_case_count=4
- selected_invalid_case_count=4
- selected_valid_case_count=0
- selected_usage_error_case_count=3
- selected_mismatch_case_count=1
- excluded_fail_closed_case_count=26
- excluded_valid_case_count=6
- processed_case_count=4
- preflight_usage_error_case_count=3
- runtime_or_contract_mismatch_case_count=1
- expected_usage_error_case_count=3
- observed_usage_error_case_count=3
- expected_mismatch_case_count=1
- observed_mismatch_case_count=1
- expected_fail_closed_case_count=0
- observed_fail_closed_case_count=0
- expected_pass_case_count=0
- observed_pass_case_count=0
- input_error_case_count=0
- runtime_schema_version=learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4
- integration_mode=artifact-body-runtime-invocation-controlled
- artifact_body_payload_emitted_case_count=0
- manifest_writer_invoked_case_count=0
- file_writing_enabled_case_count=0
- artifact_file_written_case_count=0
- manifest_file_written_case_count=0
- forbidden_body_emitted_case_count=0
- raw_stdout_body_suppressed_case_count=4
- raw_stderr_body_suppressed_case_count=4
- residue_file_count=0
- content_suppressed=True
- body_suppressed=True
- metadata_only_checked=True
- synthetic_only_checked=True
- no_oracle_checked=True
- production_readiness_claimed=False
- real_data_readiness_claimed=False
- performance_claims_present=False

Clarifications:

- `status=pass` means the runner observed the expected per-case usage_error / mismatch categories.
- It does not mean individual invalid cases passed.
- Per-case usage_error / mismatch are expected categories.
- Runner-level usage_error / mismatch remain separate failure modes.
- `processed_case_count=4` is the primary count.

## 7. Makefile Placement

Recommended placement:

- Near existing actual-controlled v0.4 runtime smoke targets.
- After the accepted invalid fail_closed Makefile target:
  - `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-invalid-case-runtime-fail-closed-smoke`
- Keep all-valid pass-matrix target before invalid fail_closed target.
- Keep invalid fail_closed target before deferred usage_error/mismatch target.

Recommended order:

1. actual-controlled v0.4 all-valid multi-case runtime smoke
2. actual-controlled v0.4 invalid-case runtime fail_closed smoke
3. actual-controlled v0.4 deferred invalid-case runtime usage_error / mismatch smoke

Step628 should add a standalone Makefile target only. Release-quality wrapper integration should be deferred to a later design Step after the standalone target passes. The target should be added to `.PHONY` and included in `make help`.

## 8. Relationship to Existing Targets

Existing targets that must remain unchanged:

- `check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation-fixtures`
- `check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation`
- `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-multi-case-runtime-smoke`
- `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-invalid-case-runtime-fail-closed-smoke`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation-fixtures`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-runtime`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata`

The new future target:

- runs the deferred invalid-case usage_error / mismatch smoke
- uses the actual-controlled fixture root
- selects exactly 4 deferred invalid cases
- excludes the 26 fail_closed invalid cases
- excludes all 6 valid cases
- uses `processed_case_count=4` as primary count
- does not replace all-valid multi-case target
- does not replace fail_closed invalid-case target
- does not replace v0.4 single-case target
- does not replace actual-controlled fixture validator target
- does not replace planned-only v0.3 target
- does not invoke manifest writer
- does not write files
- is not release-quality integrated yet

## 9. Step628 Implementation Plan

Step628 should:

- update `Makefile`
- add `.PHONY` entry
- add `make help` entry
- add the target command
- not modify Python code/tests
- not modify fixture JSON
- not modify release-quality wrapper
- not modify workflows
- not modify runtime implementation
- not invoke manifest writer
- not write files
- run the new target
- run direct deferred invalid-case CLI
- run focused deferred invalid-case tests
- run existing invalid fail_closed tests and target
- run all-valid multi-case tests and target
- run existing v0.4 single-case target
- run actual-controlled fixture validator target
- run planned-only v0.3 runtime target
- run safe-metadata runtime target
- run artifact body safe-metadata CLI smoke
- run runtime integration focused tests
- run make check-python
- run compileall
- confirm fixture JSON diff unchanged
- update root README and full technical specification related docs because Step628 is implementation

## 10. Safety Boundary

The proposed Makefile target must:

- run only the fixed 4 deferred invalid cases
- use synthetic metadata-only fixtures
- output only aggregate public-safe metadata
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

- Target failure may indicate deferred matrix mismatch, selected/excluded case confusion, missing safety flags, forbidden body emission, unexpected pass, unexpected fail_closed, runner-level usage_error, runner-level mismatch, manifest writer invocation, file writing, or residue.
- Target pass means all 4 selected deferred invalid cases matched expected per-case usage_error / mismatch categories with body-free output and no residue.
- Target pass does not mean individual invalid cases passed.
- Target pass does not prove runtime correctness generally.
- Target pass does not prove all invalid-case behavior.
- Target pass does not prove artifact body payload correctness.
- Target pass does not imply release-quality integration.
- Target pass does not imply production readiness or real-data readiness.

## 12. Non-Equivalence Cautions

- Makefile target design is not Makefile implementation.
- Future target pass will not prove runtime correctness generally.
- Future target pass will not prove all invalid-case behavior.
- Future target pass will not prove payload correctness.
- Future target pass will not prove manifest writer correctness.
- Metadata-only smoke will not prove free-form body safety.
- Fixture validator coverage is not equivalent to deferred runtime/preflight matrix coverage.
- Manifest writer validators remain separate.
- File-writing validators remain separate.
- Release-quality success is not production readiness.
- Synthetic-only pass is not real-data readiness.
- No model performance follows from this boundary.

## 13. Non-Claims

- production readiness is not claimed.
- real-data readiness is not claimed.
- model performance is not claimed.
- F1 / accuracy / ECE / AURCC achievement is not claimed.
- runtime correctness generally is not claimed.
- all invalid-case runtime behavior is not claimed.
- usage_error / mismatch runtime behavior is not generally claimed.
- payload correctness is not claimed.
- manifest writer correctness is not claimed.
- file-writing readiness is not claimed.
- generated policy quality is not claimed.
- learner-state estimator correctness is not claimed.

## 14. Public-Safe Checklist

- no raw logs
- no full job output
- no copied GitHub log blocks
- no fixture JSON body
- no request body
- no pointer body
- no expected body
- no artifact body payload
- no manifest body
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

## 15. Recommended Next Step

Recommended next step:

- Step628: deferred invalid-case usage_error / mismatch Makefile target implementation

Step628 should update Makefile and necessary README/docs only. Step628 should not change Python code/tests, fixture JSON, release-quality wrapper, workflows, manifest writer integration, or file writing.

## Step628 Implementation Reference

Step628 adds `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-deferred-invalid-case-runtime-usage-error-mismatch-smoke` as a standalone Makefile target for the Step626 direct CLI.

The target follows this design with help text `Run actual-controlled v0.4 deferred invalid-case usage_error/mismatch smoke`, placement after the accepted invalid fail_closed target, and the same public-safe aggregate-output boundary. Release-quality wrapper integration remains future work.

## Step629 Release-Quality Integration Design Reference

Step629 adds `docs/frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_release_quality_integration_design.md` as a design-only / docs-only plan for future release-quality wrapper integration of the Step628 standalone target.

The design proposes the wrapper label, command, insertion after the invalid fail_closed smoke, expected aggregate public-safe output, validation plan, and safety boundary without changing wrapper, Makefile, workflow, Python code/tests, fixture JSON, payload audit implementation, manifest writer integration, or file writing.

## Step630 Release-Quality Integration Reference

Step630 adds the Step628 standalone target to `scripts/check_release_quality.sh` after the invalid fail_closed smoke and before artifact body fixture / CLI checks. It does not change Makefile, Python code/tests, fixture JSON, payload audit implementation, manifest writer integration, or file writing.

## Step631 Remote Run Record Workflow Reference

Step631 adds `docs/frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_release_quality_remote_run_record_workflow.md` as a design-only / docs-only workflow for a future Step632 status marker. It does not create the marker and does not change Makefile, wrapper, Python code/tests, fixture JSON, payload audit implementation, manifest writer integration, or file writing.

## Step632 Remote Status Marker Reference

Step632 adds `docs/status/learner_state_frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_release_quality_remote_run_status.md` as a status-marker-only / docs-only record for the remote Release Quality run after Step630. It does not change Makefile, wrapper, Python code/tests, fixture JSON, payload audit implementation, manifest writer integration, or file writing.
