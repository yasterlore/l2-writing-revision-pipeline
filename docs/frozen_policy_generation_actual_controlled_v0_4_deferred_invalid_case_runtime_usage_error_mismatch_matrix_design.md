# Actual-Controlled v0.4 Deferred Invalid-Case Runtime usage_error / mismatch Matrix Design

## 1. Title

Actual-Controlled v0.4 Deferred Invalid-Case Runtime usage_error / mismatch Matrix Design

## 2. Scope

This document designs a future actual-controlled v0.4 deferred invalid-case runtime usage_error / mismatch matrix for the 4 invalid cases intentionally deferred from the Step614-Step622 fail_closed matrix.

This is design-only / docs-only. It includes no runtime execution, no Python code/tests changes, no Makefile changes, no release-quality wrapper changes, no workflow changes, no fixture JSON changes, no runtime implementation changes, no validator implementation changes, no payload audit implementation, no manifest writer integration, and no file writing.

This design is not proof of production readiness, real-data readiness, or model performance.

## 3. Prior Boundary Dependency

- Step622 accepted only the fixed 26 selected invalid fail_closed runtime smoke boundary.
- Step622 explicitly deferred usage_error / mismatch invalid runtime behavior.
- Step623 compared next-boundary options.
- Step623 recommended deferred usage_error / mismatch invalid runtime matrix design.
- Step624 designs that matrix but does not execute it.

## 4. Deferred Case Inventory

Directory-name / case-ID only inventory:

| case_id | expected_status_category | reason_family | selected_for_step624_design |
| --- | --- | --- | --- |
| invalid/invalid_malformed_metadata_json | usage_error | malformed metadata JSON | yes |
| invalid/invalid_missing_required_metadata_file | usage_error | missing required metadata file | yes |
| invalid/invalid_unsupported_schema | usage_error | unsupported schema | yes |
| invalid/invalid_mismatched_expected_status | mismatch | mismatched expected status | yes |

Important constraints:

- Do not copy fixture JSON body.
- Do not copy request / pointer / expected body.
- Do not copy payload body.
- Do not copy raw stdout/stderr body.
- Do not inspect JSON bodies.
- Use directory names and prior public-safe contract only.

## 5. Matrix Design Options

### Option A: Combined Deferred Invalid Status Matrix

Overview:

- Includes the 3 usage_error cases and 1 mismatch case in one deferred invalid status matrix.
- Future runner overall status is `pass` when expected per-category counts are observed.
- expected_usage_error_case_count=3
- observed_usage_error_case_count=3
- expected_mismatch_case_count=1
- observed_mismatch_case_count=1

Pros:

- The boundary is small because it covers only 4 cases.
- It directly addresses the Step622 deferred limitation.
- It can close in one runner / target / release-quality chain.
- It remains separable from the fail_closed 26-case matrix.

Cons:

- usage_error and mismatch have different semantics, so failure mapping must be explicit.
- Runner-level usage_error and expected per-case usage_error must be strictly distinguished.

### Option B: Separate usage_error-only And mismatch-only Matrices

Overview:

- Splits the 3 usage_error cases and the 1 mismatch case into separate runner / target / chain boundaries.

Pros:

- Semantic clarity is highest.
- Runner-level status and per-case expected status are less likely to be confused.

Cons:

- A 1-case mismatch chain is too small.
- Docs / target / release-quality staging becomes longer.
- The overhead is high for the first deferred-case boundary after Step622.

### Option C: Keep Deferred Cases Validator-Only

Overview:

- Leaves the 4 cases as fixture validator coverage only and does not design a runtime matrix.

Pros:

- Adds no implementation surface.
- Most conservative.

Cons:

- The largest Step622 remaining limitation remains.
- Deferred runtime behavior cannot progress.

### Option D: All-Invalid Broad Matrix

Overview:

- Re-runs the 26 fail_closed cases and 4 deferred cases together as a 30 invalid-case matrix.

Pros:

- All invalid cases are covered in one matrix.

Cons:

- It mixes the Step622 accepted fail_closed matrix with deferred usage_error / mismatch semantics.
- usage_error / mismatch meaning becomes less clear.
- The boundary is too broad.
- It is not appropriate as the first deferred-case boundary.

## 6. Recommended Matrix Option

Recommended option:

- Option A: combined deferred invalid status matrix

Reasons:

- It covers only 4 cases.
- It directly addresses the Step622 deferred limitation.
- It can stay separate from the fail_closed 26-case matrix.
- Explicit usage_error / mismatch subcounts reduce semantic mixing.
- It avoids payload, manifest, and file-writing boundaries.
- It creates a clear handoff to Step625 exact fixture/matrix contract design.

## 7. Proposed Matrix

Matrix name:

```text
actual_controlled_v0_4_deferred_invalid_usage_error_mismatch_runtime_smoke
```

Future mode:

```text
actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke
```

Future case selection:

```text
deferred-invalid-usage-error-mismatch
```

Future matrix schema name:

```text
learner_state_frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_matrix_v0.1
```

Future runtime smoke schema name:

```text
learner_state_frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke_v0.1
```

Selected cases:

- selected_case_count=4
- selected_invalid_case_count=4
- selected_valid_case_count=0
- selected_usage_error_case_count=3
- selected_mismatch_case_count=1
- excluded_fail_closed_case_count=26
- excluded_valid_case_count=6

Expected observed categories:

- expected_usage_error_case_count=3
- observed_usage_error_case_count=3
- expected_mismatch_case_count=1
- observed_mismatch_case_count=1
- expected_fail_closed_case_count=0
- observed_fail_closed_case_count=0
- expected_pass_case_count=0
- observed_pass_case_count=0
- input_error_case_count=0

## 8. Expected Future Aggregate Output Contract

Future aggregate output should include at least:

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
- Per-case usage_error is expected and distinct from runner-level usage_error.
- `processed_case_count=4` is preferred over `executed_case_count` if the future runner may stop malformed/missing metadata cases during safe preflight.
- Step625 may decide whether to use `processed_case_count`, `executed_case_count`, or both.

## 9. Per-Case Summary Contract

Allowed per-case fields:

- case_id
- expected_status
- observed_status
- reason_code
- runtime_schema_version
- integration_mode
- preflight_checked
- runtime_attempted
- artifact_body_runtime_invoked
- artifact_body_generation_cli_invoked
- artifact_body_payload_emitted
- manifest_writer_invoked
- file_writing_enabled
- artifact_file_written
- manifest_file_written
- raw_stdout_body_suppressed
- raw_stderr_body_suppressed
- forbidden_body_emitted
- unsafe_signal_count
- residue_file_count

Forbidden per-case fields:

- fixture JSON body
- request body
- pointer body
- expected body
- artifact body payload
- manifest body
- generated policy body
- raw stdout/stderr body
- raw rows
- logits/probabilities
- private / absolute path values
- raw learner text
- real participant data
- performance metric body

## 10. Runner-Level vs Per-Case Status Semantics

- runner-level `status=pass` means all selected deferred invalid cases matched their expected categories.
- per-case `usage_error` is expected for 3 cases.
- per-case `mismatch` is expected for 1 case.
- runner-level `usage_error` means runner misuse, contract violation, missing fixture root, unsafe CLI flags, or unsafe selection.
- runner-level `mismatch` means observed per-case categories did not match the contract.
- runner-level `fail_closed` means forbidden body emission, payload leak, manifest writer invocation, file writing, raw stdout/stderr body emission, private/absolute path emission, raw learner text, real data marker, or residue.

## 11. Failure Mapping

### pass

Future runner should pass only if:

- selected_case_count=4
- selected_invalid_case_count=4
- selected_valid_case_count=0
- selected_usage_error_case_count=3
- selected_mismatch_case_count=1
- observed_usage_error_case_count=3
- observed_mismatch_case_count=1
- observed_fail_closed_case_count=0
- observed_pass_case_count=0
- input_error_case_count=0
- no selected case emits forbidden body content
- no selected case emits artifact body payload
- no selected case emits manifest body
- no selected case emits generated policy body
- no selected case emits raw stdout/stderr body
- no selected case invokes manifest writer
- no selected case enables file writing
- no selected case writes artifact or manifest files
- no selected case leaves residue
- aggregate output is public-safe and count-only

### usage_error

Future runner should return runner-level usage_error if:

- fixture root missing
- invalid directory missing
- selected case count does not equal 4
- any selected case directory missing
- valid case is accidentally selected
- fail_closed case is accidentally selected
- duplicate case ID appears
- unsupported case-selection value is used
- required CLI safety flags are missing
- unknown fixture root layout is encountered
- selected case cannot be classified safely from contract

### mismatch

Future runner should return runner-level mismatch if:

- observed usage_error count differs from 3
- observed mismatch count differs from 1
- any selected case produces pass unexpectedly
- any selected case produces fail_closed unexpectedly
- any selected case produces the wrong expected category
- expected schema/mode differs
- expected selected case IDs differ from contract
- aggregate counts disagree with per-case counts

### fail_closed

Future runner should return fail_closed if:

- a selected case emits a forbidden body
- raw stdout/stderr body is emitted
- artifact body payload is emitted
- manifest body is emitted
- generated policy body is emitted
- request / pointer / expected body is emitted
- raw rows / logits / probabilities are emitted
- private / absolute path values are emitted
- raw learner text or real participant data markers are emitted
- manifest writer is invoked
- file writing is enabled or detected
- artifact or manifest file is written
- residue appears
- unsafe output scan itself fails closed

## 12. Selection Policy

Future `--case-selection deferred-invalid-usage-error-mismatch` should:

- select exactly the 4 deferred invalid cases.
- exclude the 26 fail_closed invalid cases.
- exclude all valid cases.
- sort selected case IDs lexicographically.
- include expected status category in the contract.
- fail with runner-level usage_error on duplicate or missing cases.
- fail with runner-level usage_error if a valid or fail_closed case is included.
- fail with runner-level mismatch if observed status categories differ from expected status categories.
- never emit fixture JSON body.

## 13. Relationship To Accepted fail_closed Matrix

- Step622 accepted the fixed 26 selected fail_closed invalid cases.
- Step624 does not reopen or replace the accepted fail_closed matrix.
- Step624 addresses the 4 deferred non-fail_closed invalid cases.
- The future deferred matrix should be complementary to the fail_closed matrix.
- A future deferred matrix pass would not prove fail_closed matrix behavior; that is already a separate boundary.
- A future deferred matrix pass would not prove all invalid-case behavior generally beyond the selected 4.

## 14. Relationship To Fixture Validator

- The existing actual-controlled fixture validator covers all 36 cases at metadata/contract level.
- The 4 deferred cases are already contract-classified as usage_error or mismatch.
- Step624 designs runtime/preflight-level handling for those deferred cases.
- The future runner must not replace the fixture validator.
- Fixture validator remains broader coverage.

## 15. Relationship To Payload / Manifest / File-Writing Boundaries

- This design does not emit payloads.
- This design does not audit payload correctness.
- This design does not invoke manifest writer.
- This design does not enable file writing.
- Payload audit / manifest writer / file-writing boundaries remain separate.
- No production readiness follows.

## 16. Future Implementation Options

### Option A: Dedicated Deferred Invalid Status Runner

Pros:

- clear separation from fail_closed runner
- easy to preserve per-category semantics
- avoids mixing expected fail_closed with expected usage_error/mismatch
- easier safety review

Cons:

- new module and focused tests required

### Option B: Extend Existing Invalid-Case fail_closed Runner

Pros:

- less new code
- can reuse selection and aggregation helpers

Cons:

- risk of mixing fail_closed semantics with usage_error / mismatch semantics
- harder to review
- may weaken clarity of Step622 accepted boundary

Recommendation:

- recommend dedicated future runner, or a shared helper plus separate CLI module, but not a simple extension that mixes fail_closed semantics.

Future runner candidate:

```text
python/learner_state/frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke.py
```

Future focused tests candidate:

```text
python/learner_state/tests/test_frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke.py
```

Do not implement in Step624.

## 17. Future CLI Design

Example:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled \
  --case-selection deferred-invalid-usage-error-mismatch \
  --summary-only \
  --no-file-writing \
  --no-manifest-writer \
  --fail-closed-on-unsafe-output
```

Required flags:

- `--fixture-root`
- `--case-selection deferred-invalid-usage-error-mismatch`
- `--summary-only`
- `--no-file-writing`
- `--no-manifest-writer`
- `--fail-closed-on-unsafe-output`

Do not implement in Step624.

## 18. Future Chain Proposal

Tentative future chain:

- Step625: deferred invalid-case usage_error / mismatch fixture/matrix contract design
- Step626: deferred invalid-case usage_error / mismatch runner implementation
- Step627: Makefile target design
- Step628: Makefile target implementation
- Step629: release-quality integration design
- Step630: wrapper integration
- Step631: remote status marker
- Step632: final safety review

## 19. Boundaries Explicitly Not Selected Now

Do not select now:

- runtime execution
- Python implementation
- Makefile target implementation
- release-quality wrapper integration
- workflow changes
- fixture JSON changes
- payload audit implementation
- payload body emission
- manifest writer integration
- file writing
- production file-writing path
- real-data readiness check
- model performance check
- all-invalid broad runtime run
- merging fail_closed 26 cases back into this matrix

## 20. Non-Equivalence Cautions

- design is not implementation.
- future deferred matrix pass would not prove runtime correctness generally.
- future deferred matrix pass would not prove all invalid-case behavior generally.
- future deferred matrix pass would not prove payload correctness.
- metadata-only planning is not free-form body safety proof.
- fixture validator coverage is not equivalent to runtime/preflight matrix coverage.
- release-quality success is not production readiness.
- synthetic-only pass is not real-data readiness.
- no model performance follows from this design.

## 21. Non-Claims

- production readiness is not claimed.
- real-data readiness is not claimed.
- model performance is not claimed.
- F1 / accuracy / ECE / AURCC achievement is not claimed.
- runtime correctness generally is not claimed.
- all invalid-case runtime behavior is not claimed.
- usage_error / mismatch runtime behavior is not claimed.
- payload correctness is not claimed.
- manifest writer correctness is not claimed.
- file-writing readiness is not claimed.
- generated policy quality is not claimed.
- learner-state estimator correctness is not claimed.

## 22. Public-Safe Checklist

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

## 23. Recommended Next Step

Recommended next step:

- Step625: deferred invalid-case usage_error / mismatch fixture/matrix contract design

Step625 should remain design-only / docs-only. It should fix the exact selected/deferred contract and decide whether to use `processed_case_count`, `executed_case_count`, or both. Step625 should not execute the cases, change Python code/tests, change Makefile, change release-quality wrapper, change workflow, change fixture JSON, implement payload audit, implement manifest writer integration, or enable file writing.

## Step625 Fixture Matrix Contract Reference

Step625 adds `docs/frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_fixture_matrix_contract_design.md` as the design-only / docs-only contract for the combined deferred invalid status matrix recommended here.

The contract fixes the 4 selected deferred invalid case IDs, expected usage_error / mismatch categories, primary count policy, aggregate and per-case contracts, allowed/forbidden per-case fields, runner-level versus per-case status semantics, selection policy, failure mapping, future CLI contract, and Step626 implementation handoff without runtime execution, Python code/tests changes, Makefile changes, wrapper changes, workflow changes, fixture JSON changes, payload audit implementation, manifest writer integration, or file writing.

## Step626 Implementation Reference

Step626 implements the direct CLI-only runner and focused tests for this deferred invalid status matrix. The runner processes the 4 selected non-fail_closed invalid cases with `--case-selection deferred-invalid-usage-error-mismatch`, emits aggregate public-safe metadata with `processed_case_count=4`, and keeps Makefile target design, release-quality integration, manifest writer integration, file writing, and fixture JSON changes out of scope.

## Step627 Makefile Target Design Reference

Step627 adds `docs/frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_makefile_target_design.md` as a design-only / docs-only plan for a future standalone Makefile target around the Step626 direct CLI. It keeps Makefile changes, release-quality wrapper changes, workflow changes, Python code/tests changes, fixture JSON changes, payload audit implementation, manifest writer integration, and file writing out of Step627.

## Step628 Makefile Target Reference

Step628 adds the standalone Makefile target `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-deferred-invalid-case-runtime-usage-error-mismatch-smoke` for the Step626 direct CLI. It remains outside release-quality and keeps Python code/tests, fixture JSON, payload audit implementation, manifest writer integration, and file writing unchanged.

## Step629 Release-Quality Integration Design Reference

Step629 adds `docs/frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_release_quality_integration_design.md` as a design-only / docs-only plan for future wrapper integration of the Step628 standalone target. It keeps wrapper, Makefile, workflow, Python code/tests, fixture JSON, payload audit implementation, manifest writer integration, and file writing unchanged.

## Step630 Release-Quality Integration Reference

Step630 adds the Step628 standalone target to `scripts/check_release_quality.sh` after the invalid fail_closed smoke and before artifact body fixture / CLI checks. It keeps Makefile, Python code/tests, fixture JSON, payload audit implementation, manifest writer integration, and file writing unchanged.

## Step631 Remote Run Record Workflow Reference

Step631 adds `docs/frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_release_quality_remote_run_record_workflow.md` as a design-only / docs-only plan for a future Step632 public-safe status marker. It keeps wrapper, Makefile, Python code/tests, fixture JSON, payload audit implementation, manifest writer integration, and file writing unchanged.
