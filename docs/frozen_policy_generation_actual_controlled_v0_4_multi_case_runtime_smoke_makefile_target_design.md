# Actual-Controlled v0.4 Multi-Case Runtime Smoke Makefile Target Design

## Scope

This document designs a future standalone Makefile target for running the Step604 direct multi-case runtime smoke CLI.

This is a design-only / docs-only step. It does not change Makefile, release-quality wrapper, workflows, Python code/tests, fixture JSON, runtime implementation, validator implementation, manifest writer integration, manifest body generation, generated policy body generation, artifact body file writing, or manifest file writing.

This document does not provide production readiness, real-data readiness, or model performance evidence.

## Prior Chain Dependency

- Step600: final safety review identified the single primary-case smoke limitation in the actual-controlled v0.4 chain.
- Step601: next-boundary planning recommended a multi-case runtime smoke as the conservative next boundary.
- Step602: multi-case runtime smoke design recommended an all-valid matrix and a dedicated runner.
- Step603: fixture/matrix contract fixed all 6 valid case IDs and the expected aggregate contract.
- Step604: dedicated runner and focused tests were implemented.
- Step604 direct CLI passes with 6 selected cases, 6 executed cases, 6 pass cases, no unsafe signal, and no residue.
- Step604 has no Makefile target yet.
- Release-quality wrapper integration is still not implemented for the multi-case smoke.

## Target Runtime CLI

Runtime module:

- `python/learner_state/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke.py`

Direct CLI:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled \
  --case-selection all-valid \
  --summary-only \
  --no-file-writing \
  --no-manifest-writer \
  --fail-closed-on-unsafe-output
```

Fixture root:

- `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled/`

Case selection:

- `all-valid`

Selected matrix:

- `actual_controlled_v0_4_all_valid_runtime_smoke`

Selected valid case IDs:

- `valid/valid_actual_controlled_cli_output_body_free`
- `valid/valid_actual_controlled_no_file_writing`
- `valid/valid_actual_controlled_no_manifest_writer`
- `valid/valid_actual_controlled_no_residue`
- `valid/valid_actual_controlled_safe_metadata_invocation`
- `valid/valid_actual_controlled_stdout_stderr_suppressed`

## Proposed Makefile Target

Recommended target name:

```text
check-learner-state-frozen-policy-generation-actual-controlled-v0-4-multi-case-runtime-smoke
```

Recommended help text:

```text
Run actual-controlled v0.4 multi-case runtime smoke
```

Recommended command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled --case-selection all-valid --summary-only --no-file-writing --no-manifest-writer --fail-closed-on-unsafe-output
```

Do not add the target in Step605. Step606 should add it.

## Expected Target Output

The future Makefile target should produce the same public-safe summary as the Step604 direct CLI.

Expected fields include:

- `mode=actual_controlled_v0_4_multi_case_runtime_smoke`
- `schema_version=learner_state_frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_v0.1`
- `status=pass`
- `reason_code=none`
- `matrix_name=actual_controlled_v0_4_all_valid_runtime_smoke`
- `case_selection=all-valid`
- `selected_case_count=6`
- `selected_valid_case_count=6`
- `selected_invalid_case_count=0`
- `executed_case_count=6`
- `pass_case_count=6`
- `usage_error_case_count=0`
- `fail_closed_case_count=0`
- `mismatch_case_count=0`
- `input_error_case_count=0`
- `runtime_schema_version=learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4`
- `integration_mode=artifact-body-runtime-invocation-controlled`
- `all_cases_artifact_body_runtime_invoked=True`
- `all_cases_controlled_metadata_only_invocation=True`
- `artifact_body_generation_cli_invoked_case_count=6`
- `artifact_body_generation_cli_output_scanned_case_count=6`
- `artifact_body_generation_cli_output_body_free_case_count=6`
- `artifact_body_payload_emitted_case_count=0`
- `manifest_writer_invoked_case_count=0`
- `file_writing_enabled_case_count=0`
- `artifact_file_written_case_count=0`
- `manifest_file_written_case_count=0`
- `raw_stdout_body_suppressed_case_count=6`
- `raw_stderr_body_suppressed_case_count=6`
- `request_body_detected_case_count=0`
- `pointer_body_detected_case_count=0`
- `expected_body_detected_case_count=0`
- `artifact_body_payload_detected_case_count=0`
- `manifest_body_detected_case_count=0`
- `generated_policy_body_detected_case_count=0`
- `raw_rows_detected_case_count=0`
- `logits_detected_case_count=0`
- `probabilities_detected_case_count=0`
- `private_path_detected_case_count=0`
- `absolute_path_detected_case_count=0`
- `raw_learner_text_detected_case_count=0`
- `real_data_marker_detected_case_count=0`
- `performance_metric_body_detected_case_count=0`
- `runtime_safety_scan_passed_case_count=6`
- `unsafe_signal_total_count=0`
- `residue_file_count=0`
- `safe_metadata_body_field_count_min=5`
- `safe_metadata_body_field_count_max=5`
- `safe_metadata_body_field_count_unique_values=5`
- `content_suppressed=True`
- `body_suppressed=True`
- `metadata_only_checked=True`
- `synthetic_only_checked=True`
- `no_oracle_checked=True`
- `production_readiness_claimed=False`
- `real_data_readiness_claimed=False`
- `performance_claims_present=False`

## Makefile Placement

Recommended placement:

- near the existing actual-controlled v0.4 single-case runtime smoke target:
  - `check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation`
- after the single-case target.
- near the actual-controlled fixture validator target enough to keep the chain readable.

Step606 should add standalone Makefile target only. Release-quality wrapper integration should be deferred to a later design step after the standalone target passes.

The future target should be added to `.PHONY` and included in `make help`.

## Relationship To Existing Targets

Existing targets that must remain unchanged:

- `check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation-fixtures`
- `check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation-fixtures`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-runtime`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata`

The future target:

- runs the all-valid v0.4 multi-case runtime smoke.
- uses the actual-controlled fixture root.
- selects all 6 valid cases.
- does not replace the v0.4 single-case target.
- does not replace the actual-controlled fixture validator target.
- does not replace the planned-only v0.3 target.
- does not replace the artifact body safe-metadata CLI smoke.
- does not invoke manifest writer.
- does not write files.
- is not release-quality integrated yet.

## Step606 Implementation Plan

Step606 should:

- update `Makefile`.
- add `.PHONY` entry.
- add `make help` entry.
- add the target command.
- not modify Python code/tests.
- not modify fixture JSON.
- not modify release-quality wrapper.
- not modify workflows.
- not modify runtime implementation.
- not invoke manifest writer.
- not write files.
- run the new target.
- run direct multi-case CLI.
- run focused multi-case tests.
- run existing v0.4 single-case target.
- run actual-controlled fixture validator target.
- run planned-only v0.3 runtime target.
- run safe-metadata runtime target.
- run artifact body safe-metadata CLI smoke.
- run runtime integration focused tests.
- run `make check-python`.
- run compileall.
- confirm fixture JSON diff remains unchanged.
- update root README and full technical specification related docs because Step606 is an implementation step.

## Safety Boundary

The proposed target must:

- run only the all-valid v0.4 multi-case runtime smoke.
- read only synthetic metadata-only fixture metadata.
- select case IDs by directory name only.
- output only aggregate public-safe metadata.
- not print fixture JSON body.
- not print request body.
- not print pointer body.
- not print expected body.
- not print artifact body payload.
- not print manifest body.
- not print generated policy body.
- not print raw stdout/stderr body.
- not print raw rows.
- not print logits/probabilities.
- not print private/absolute path values.
- not print raw learner text.
- not use real participant data.
- not invoke manifest writer.
- not enable file writing.
- not produce residue.

## Failure Interpretation

- Target failure means the multi-case runtime smoke or its safety scan failed.
- Target failure may indicate case discovery mismatch, missing flags, fixture mismatch, unsafe output marker, unexpected residue, or compatibility break.
- Target pass means all selected valid v0.4 controlled metadata-only runtime smoke cases passed.
- Target pass does not prove runtime correctness generally.
- Target pass does not prove invalid runtime fail-closed behavior.
- Target pass does not prove artifact body payload correctness.
- Target pass does not imply release-quality integration.
- Target pass does not imply production readiness or real-data readiness.

## Non-Equivalence Cautions

- Makefile target design is not Makefile implementation.
- Future multi-case target pass will not prove runtime correctness generally.
- All-valid multi-case smoke will not prove invalid runtime fail-closed behavior.
- Metadata-only smoke will not prove artifact body payload correctness.
- Count-only summaries will not prove free-form body safety.
- Manifest writer validators remain separate.
- File-writing validators remain separate.
- Release-quality success is not production readiness.
- Synthetic-only pass is not real-data readiness.
- No model performance follows from this boundary.

## Non-Claims

- production readiness is not claimed.
- real-data readiness is not claimed.
- model performance is not claimed.
- F1 / accuracy / ECE / AURCC achievement is not claimed.
- artifact body generation integration correctness is not claimed.
- artifact body generation runtime correctness generally is not claimed.
- manifest writer integration correctness is not claimed.
- manifest writer file-writing production readiness is not claimed.
- artifact body payload correctness is not claimed.
- safe-metadata free-form body safety is not claimed.
- manifest body generation correctness is not claimed.
- generated policy quality is not claimed.
- learner-state estimator correctness is not claimed.
- artifact writer CLI actual invocation correctness generally is not claimed.
- runtime actual invocation correctness generally is not claimed.

## Public-Safe Checklist

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

## Recommended Next Step

Recommended next step:

- Step606: actual-controlled v0.4 multi-case runtime smoke Makefile target implementation

Step606 should update Makefile and necessary README/docs only. Step606 should not change Python code/tests, fixture JSON, release-quality wrapper, workflows, manifest writer integration, file writing, or real-data boundaries.

## Step606 Implementation Reference

Step606 adds the standalone Makefile target `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-multi-case-runtime-smoke` using the command proposed in this design. The target remains standalone and is not release-quality integrated in Step606.

## Step607 Release-Quality Integration Design Reference

Step607 adds `docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_release_quality_integration_design.md` as a design-only / docs-only plan for future wrapper integration of the Step606 standalone target. This Makefile target design remains unchanged; Step607 does not change Makefile, wrapper, workflow, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step608 Release-Quality Integration Reference

Step608 adds the Step606 standalone target to the release-quality wrapper after the actual-controlled v0.4 single-case smoke. This Makefile target design remains unchanged; Step608 does not change Makefile, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step609 Remote Run Record Workflow Reference

Step609 designs a future public-safe remote/manual run status marker for the Step608 wrapper-integrated multi-case check. This Makefile target design remains unchanged; Step609 does not change Makefile, wrapper, workflow, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step610 Remote Status Marker Reference

Step610 adds the public-safe status marker for the Step608 wrapper-integrated multi-case check. This Makefile target design remains unchanged; Step610 does not change Makefile, wrapper, workflow, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step611 Final Safety Review Reference

Step611 adds `docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_release_quality_chain_final_safety_review.md` as a final-safety-review-only / docs-only review for the Step602-Step610 all-valid multi-case runtime smoke chain. This Makefile target design remains unchanged; Step611 does not change Makefile, wrapper, workflow, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step612 Next Boundary Planning Reference

Step612 adds `docs/frozen_policy_generation_runtime_chain_post_multi_case_final_safety_review_next_boundary_planning.md` as a planning-only / docs-only comparison after the Step611 final safety review. This Makefile target design remains unchanged; Step612 does not change Makefile, wrapper, workflow, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step613 Invalid-Case Matrix Design Reference

Step613 adds `docs/frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_matrix_design.md` as a design-only / docs-only plan for a future invalid-case runtime fail-closed smoke. This Makefile target design remains unchanged; Step613 does not execute invalid cases or change Makefile, wrapper, workflow, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step614 Fixture Matrix Contract Reference

Step614 adds `docs/frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_fixture_matrix_contract_design.md` as a design-only / docs-only contract for the future invalid-case runtime fail-closed smoke. This Makefile target design remains unchanged; Step614 does not execute invalid cases or change Makefile, wrapper, workflow, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step615 Implementation Status Reference

Step615 implements a direct CLI-only invalid-case fail-closed runner and focused tests. This all-valid Makefile target design remains unchanged; Step615 does not add a Makefile target, change wrapper, change workflow, change fixture JSON, invoke manifest writer, or enable file writing.

## Step616 Makefile Target Design Reference

Step616 adds a separate design-only / docs-only plan for the future invalid-case fail-closed standalone target. This all-valid Makefile target design remains unchanged and is not replaced by Step616.
