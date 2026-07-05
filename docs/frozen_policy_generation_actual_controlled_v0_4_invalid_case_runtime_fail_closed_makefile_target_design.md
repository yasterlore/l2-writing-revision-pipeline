# Actual-Controlled v0.4 Invalid-Case Runtime Fail-Closed Smoke Makefile Target Design

## 1. Scope

This document is the Step616 design-only / docs-only plan for running the Step615 direct invalid-case runtime fail-closed CLI as a future standalone Makefile target.

This step does not change Makefile, change the release-quality wrapper, change workflows, change Python code/tests, change fixture JSON, change runtime implementation, implement manifest writer integration, or perform file writing. It is not evidence of production readiness, real-data readiness, or model performance.

## 2. Prior Chain Dependency

- Step611 accepted only the release-quality-integrated, remote-status-recorded, all-valid multi-case runtime smoke boundary.
- Step612 recommended invalid-case runtime fail-closed matrix design as the next boundary.
- Step613 designed a fail_closed-only invalid matrix.
- Step614 fixed the exact 26 selected invalid fail_closed cases and 4 deferred cases.
- Step615 implemented the direct CLI-only invalid-case fail-closed runner and focused tests.
- Step615 direct CLI passes with 26 selected / executed / observed fail_closed cases.
- Step615 has no Makefile target yet.
- Step615 is not release-quality integrated yet.

## 3. Target Runtime CLI

Runtime module:

- `python/learner_state/frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke.py`

Direct CLI:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled \
  --case-selection fail-closed-invalid \
  --summary-only \
  --no-file-writing \
  --no-manifest-writer \
  --fail-closed-on-unsafe-output
```

Fixture root:

- `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled/`

Case selection:

- `fail-closed-invalid`

Matrix:

- `actual_controlled_v0_4_invalid_fail_closed_runtime_smoke`

## 4. Proposed Makefile Target

Recommended target name:

```text
check-learner-state-frozen-policy-generation-actual-controlled-v0-4-invalid-case-runtime-fail-closed-smoke
```

Recommended help text:

```text
Run actual-controlled v0.4 invalid-case runtime fail-closed smoke
```

Recommended command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled --case-selection fail-closed-invalid --summary-only --no-file-writing --no-manifest-writer --fail-closed-on-unsafe-output
```

Do not add the target in Step616. Step617 should implement it.

## 5. Expected Target Output

The future Makefile target should produce the same public-safe summary as the Step615 direct CLI.

Expected fields include:

- `mode=actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke`
- `schema_version=learner_state_frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke_v0.1`
- `status=pass`
- `reason_code=none`
- `matrix_name=actual_controlled_v0_4_invalid_fail_closed_runtime_smoke`
- `case_selection=fail-closed-invalid`
- `selected_case_count=26`
- `selected_invalid_case_count=26`
- `selected_valid_case_count=0`
- `deferred_case_count=4`
- `executed_case_count=26`
- `pass_case_count=0`
- `expected_fail_closed_case_count=26`
- `observed_fail_closed_case_count=26`
- `usage_error_case_count=0`
- `mismatch_case_count=0`
- `input_error_case_count=0`
- `runtime_schema_version=learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4`
- `integration_mode=artifact-body-runtime-invocation-controlled`
- `all_selected_cases_failed_closed=True`
- `artifact_body_payload_emitted_case_count=0`
- `manifest_writer_invoked_case_count=0`
- `file_writing_enabled_case_count=0`
- `artifact_file_written_case_count=0`
- `manifest_file_written_case_count=0`
- `raw_stdout_body_suppressed_case_count=26`
- `raw_stderr_body_suppressed_case_count=26`
- `forbidden_body_emitted_case_count=0`
- `unsafe_signal_total_count=26`
- `residue_file_count=0`
- `content_suppressed=True`
- `body_suppressed=True`
- `metadata_only_checked=True`
- `synthetic_only_checked=True`
- `no_oracle_checked=True`
- `production_readiness_claimed=False`
- `real_data_readiness_claimed=False`
- `performance_claims_present=False`

`unsafe_signal_total_count=26` reflects expected invalid fail-closed signals in Step615 output. It is not raw body emission. `forbidden_body_emitted_case_count=0` remains required.

## 6. Makefile Placement

Recommended placement:

- near existing actual-controlled v0.4 runtime smoke targets
- after `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-multi-case-runtime-smoke`
- before unrelated artifact body / manifest writer targets if nearby
- keep the all-valid pass-matrix target before the invalid fail-closed matrix target

Step617 should add a standalone Makefile target only. Release-quality wrapper integration should be deferred to a later design step after the standalone target passes.

The future target should be added to `.PHONY` and included in `make help`.

## 7. Relationship To Existing Targets

Existing targets that must remain unchanged:

- `check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation-fixtures`
- `check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation`
- `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-multi-case-runtime-smoke`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation-fixtures`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-runtime`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata`

The new future target:

- runs the invalid-case v0.4 runtime fail-closed smoke
- uses the actual-controlled fixture root
- selects exactly 26 invalid fail_closed cases
- defers 4 non-fail_closed invalid cases
- does not replace the all-valid multi-case target
- does not replace the v0.4 single-case target
- does not replace the actual-controlled fixture validator target
- does not replace the planned-only v0.3 target
- does not invoke manifest writer
- does not write files
- is not release-quality integrated yet

## 8. Step617 Implementation Plan

Step617 should:

- update `Makefile`
- add a `.PHONY` entry
- add a `make help` entry
- add the target command
- not modify Python code/tests
- not modify fixture JSON
- not modify release-quality wrapper
- not modify workflows
- not modify runtime implementation
- not invoke manifest writer
- not write files
- run the new target
- run direct invalid-case CLI
- run focused invalid-case tests
- run all-valid multi-case tests
- run all-valid multi-case target
- run existing v0.4 single-case target
- run actual-controlled fixture validator target
- run planned-only v0.3 runtime target
- run safe-metadata runtime target
- run artifact body safe-metadata CLI smoke
- run runtime integration focused tests
- run `make check-python`
- run compileall
- confirm fixture JSON diff unchanged
- update root README and full technical specification related docs because Step617 is implementation

## 9. Safety Boundary

The proposed target must:

- run only the fixed 26 invalid fail_closed case matrix
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

## 10. Failure Interpretation

- Target failure means the invalid-case runtime fail-closed smoke or its safety scan failed.
- Target failure may indicate selected matrix mismatch, missing safety flags, selected/deferred case confusion, forbidden body emission, unexpected pass, unexpected usage_error, manifest writer invocation, file writing, or residue.
- Target pass means all 26 selected invalid cases reached expected fail_closed status with body-free output and no residue.
- Target pass does not prove runtime correctness generally.
- Target pass does not prove all invalid cases generally.
- Target pass does not prove usage_error / mismatch runtime matrix behavior.
- Target pass does not prove artifact body payload correctness.
- Target pass does not imply release-quality integration.
- Target pass does not imply production readiness or real-data readiness.

## 11. Non-Equivalence Cautions

- Makefile target design is not Makefile implementation.
- Future target pass will not prove runtime correctness generally.
- Future target pass will not prove all invalid-case behavior.
- Future target pass will not prove usage_error / mismatch invalid runtime behavior.
- Future target pass will not prove artifact body payload correctness.
- Metadata-only smoke will not prove free-form body safety.
- Manifest writer validators remain separate.
- File-writing validators remain separate.
- Release-quality success is not production readiness.
- Synthetic-only pass is not real-data readiness.
- No model performance follows from this boundary.

## 12. Non-Claims

- Production readiness is not claimed.
- Real-data readiness is not claimed.
- Model performance is not claimed.
- F1 / accuracy / ECE / AURCC achievement is not claimed.
- Artifact body generation integration correctness is not claimed.
- Artifact body generation runtime correctness generally is not claimed.
- Invalid-case runtime fail-closed behavior is not generally claimed.
- Manifest writer integration correctness is not claimed.
- Manifest writer file-writing production readiness is not claimed.
- Artifact body payload correctness is not claimed.
- Safe-metadata free-form body safety is not claimed.
- Manifest body generation correctness is not claimed.
- Generated policy quality is not claimed.
- Learner-state estimator correctness is not claimed.
- Artifact writer CLI actual invocation correctness generally is not claimed.
- Runtime actual invocation correctness generally is not claimed.

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

## 14. Recommended Next Step

Recommended next step:

- Step617: actual-controlled v0.4 invalid-case runtime fail-closed smoke Makefile target implementation

Step617 should update Makefile and necessary README/docs only. Step617 should not change Python code/tests, change fixture JSON, change the release-quality wrapper, change workflows, invoke manifest writer, or enable file writing.

## 15. Step617 Implementation Status

Step617 adds the standalone Makefile target `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-invalid-case-runtime-fail-closed-smoke` with help text `Run actual-controlled v0.4 invalid-case runtime fail-closed smoke`.

The target runs the Step615 direct CLI with `--case-selection fail-closed-invalid`, `--summary-only`, `--no-file-writing`, `--no-manifest-writer`, and `--fail-closed-on-unsafe-output`. It is placed after `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-multi-case-runtime-smoke`, remains a standalone target only, is not release-quality integrated, does not change Python code/tests or fixture JSON, does not invoke manifest writer, and does not enable file writing.

Expected aggregate output remains public-safe and metadata-only: 26 selected invalid cases, 4 deferred invalid cases, 26 executed cases, 26 observed fail_closed cases, `unsafe_signal_total_count=26`, `forbidden_body_emitted_case_count=0`, and `residue_file_count=0`.

Recommended next step:

- Step618: actual-controlled v0.4 invalid-case runtime fail-closed smoke release-quality integration design

## 16. Step618 Release-Quality Integration Design Reference

Step618 adds `docs/frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_release_quality_integration_design.md` as a design-only / docs-only plan for future wrapper integration of the Step617 standalone target. Step618 does not change wrapper, Makefile, workflow, Python code/tests, fixture JSON, manifest writer integration, or file writing.
