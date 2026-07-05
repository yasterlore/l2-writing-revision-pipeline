# Actual-Controlled v0.4 Multi-Case Runtime Smoke Release Quality Integration Design

## 1. Title

Actual-Controlled v0.4 Multi-Case Runtime Smoke Release Quality Integration Design

## 2. Scope

This document is a design-only / docs-only plan for integrating the Step606 standalone multi-case Makefile target into the release-quality wrapper in a future Step608.

Step607 does not change the release-quality wrapper, Makefile, workflow files, Python code/tests, fixture JSON, runtime implementation, validator implementation, artifact body generation implementation, artifact body generation integration, manifest writer integration, manifest body generation, generated policy body generation, artifact body file writing, or manifest file writing.

This document does not implement release-quality integration, does not invoke manifest writer, does not enable file writing, and is not evidence for production readiness, real-data readiness, or model performance.

## 3. Prior Chain Dependency

- Step600: final safety review identified the single primary-case smoke limitation in the actual-controlled v0.4 chain.
- Step601: next-boundary planning recommended a multi-case runtime smoke.
- Step602: multi-case runtime smoke design defined the all-valid direction and public-safe boundary.
- Step603: fixture/matrix contract design fixed the all-valid 6-case matrix and aggregate expectations.
- Step604: multi-case runner implementation added a direct CLI-only all-valid runner and focused tests.
- Step605: Makefile target design planned a future standalone target for the Step604 runner.
- Step606: Makefile target implementation added the standalone target.
- Step606 standalone target passes with 6 selected cases, 6 executed cases, 6 pass cases, no unsafe signal, and no residue.
- Step606 target is not yet release-quality integrated.

## 4. Target To Integrate

Proposed label:

```text
release_quality_check: learner-state frozen policy generation actual-controlled v0.4 multi-case runtime smoke
```

Command:

```bash
make check-learner-state-frozen-policy-generation-actual-controlled-v0-4-multi-case-runtime-smoke
```

Expected public-safe summary:

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

The safe-metadata field count distribution is count-only. It does not expose safe-metadata body content.

## 5. Integration Options

### Option A: Integrate Multi-Case Target After Existing v0.4 Single-Case Runtime Smoke

Benefits:

- Keeps fixture validation, single-case smoke, then multi-case smoke ordering.
- Preserves the existing fast primary v0.4 smoke as a gate.
- Adds broader all-valid runtime smoke coverage without replacing existing checks.
- Keeps wrapper order readable and staged.

Risks and tradeoffs:

- Adds one more release-quality check.
- Requires explicit wrapper ordering verification in Step608.

Implementation complexity: low and localized to `scripts/check_release_quality.sh`.

Safety boundary clarity: high.

### Option B: Integrate Multi-Case Target Before Single-Case Smoke

Benefits:

- Runs broader coverage earlier.

Risks and tradeoffs:

- Runs the broader smoke before the fast primary smoke.
- Makes the staged progression harder to read.

Implementation complexity: low.

Safety boundary clarity: moderate. This option is not recommended.

### Option C: Replace Single-Case Smoke With Multi-Case Smoke

Benefits:

- Reduces duplicate release-quality checks.

Risks and tradeoffs:

- Removes the fast primary smoke from release-quality.
- Blurs the distinction between primary-case smoke and all-valid smoke.
- Makes Step597 remote status relationship less direct.

Implementation complexity: moderate because it changes existing wrapper semantics.

Safety boundary clarity: lower. This option is not recommended.

### Option D: Defer Release-Quality Integration

Benefits:

- Avoids wrapper changes if the standalone target becomes unstable.

Risks and tradeoffs:

- Leaves the Step606 target manual-only.
- Does not advance the release-quality chain for the multi-case smoke.

Implementation complexity: none in Step608.

Safety boundary clarity: acceptable as a pause, but it does not add wrapper coverage.

## 6. Recommended Option

Recommend Option A.

Required ordering:

1. actual-controlled fixture validation
2. actual-controlled v0.4 single-case runtime smoke
3. actual-controlled v0.4 multi-case runtime smoke
4. artifact body fixture validation / artifact body generation CLI checks

Rationale:

- the fixture root and schema contract should be validated before runtime smoke
- the single-case smoke remains a fast primary gate
- the multi-case smoke adds broader all-valid coverage
- invalid cases remain fixture-validator-covered
- manifest writer and file writing remain separate
- release-quality order remains readable and staged

## 7. Proposed Insertion Point In `scripts/check_release_quality.sh`

Recommended insertion:

- after existing actual-controlled v0.4 single-case runtime smoke
- before artifact body fixture validation and artifact body generation CLI checks

Expected local order around the insertion area:

1. planned-only runtime invocation fixture validation
2. planned-only v0.3 runtime invocation smoke
3. actual-controlled fixture validation
4. actual-controlled v0.4 single-case runtime smoke
5. actual-controlled v0.4 multi-case runtime smoke
6. artifact body fixture validation
7. artifact body generation CLI smoke
8. artifact body generation safe-metadata CLI smoke

If the current wrapper order differs, Step608 should place the new check adjacent to the actual-controlled single-case runtime smoke and before broader artifact body / manifest writer checks.

## 8. Expected Step608 Wrapper Changes

Step608 should:

- update `scripts/check_release_quality.sh`
- add one `run_check` entry or the equivalent wrapper pattern used locally
- add the label and command for the multi-case target
- not modify Makefile
- not modify Python code/tests
- not modify fixture JSON
- not modify workflows
- not implement runtime changes
- not invoke manifest writer
- not enable file writing
- run the standalone multi-case target
- run `make check-release-quality`
- update root README and full technical specification related docs because Step608 is an implementation step

## 9. Relationship To Existing Release-Quality Checks

Existing release-quality checks must remain unchanged:

- actual-controlled fixture validation
- actual-controlled v0.4 single-case runtime smoke
- planned-only runtime invocation fixture validation
- planned-only v0.3 runtime invocation smoke
- artifact body fixture validation
- artifact body generation CLI smoke
- artifact body generation safe-metadata CLI smoke
- manifest writer checks
- general Python checks

The multi-case release-quality check:

- adds all-valid v0.4 runtime smoke coverage
- does not replace single-case v0.4 runtime smoke
- does not replace actual-controlled fixture validator
- does not execute invalid cases through runtime
- does not replace artifact body safe-metadata CLI smoke
- does not replace manifest writer checks
- does not prove artifact body payload correctness
- does not prove runtime correctness generally
- does not imply production readiness

## 10. Safety Boundary

The release-quality check must:

- run only the standalone multi-case Makefile target
- use synthetic metadata-only fixtures
- select case IDs by directory names only
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

- multi-case target failure means all-valid runtime smoke or its safety scan failed
- failure may indicate case discovery mismatch, missing flags, fixture mismatch, unsafe output marker, unexpected residue, or compatibility break
- pass means all 6 selected valid v0.4 controlled metadata-only runtime smoke cases passed
- pass does not prove invalid runtime fail-closed behavior
- pass does not prove runtime correctness generally
- pass does not prove artifact body payload correctness
- pass does not imply production readiness or real-data readiness

## 12. Validation Plan For Step608

Step608 should run these checks in order:

1. `git status --short`
2. wrapper label / command / ordering check
3. `make help` check for the multi-case target
4. multi-case Makefile target
5. direct multi-case runtime smoke CLI
6. focused multi-case tests
7. existing v0.4 single-case runtime target
8. existing actual-controlled fixture validator target
9. existing planned-only v0.3 runtime target
10. existing safe-metadata runtime target
11. existing artifact body safe-metadata CLI smoke
12. existing runtime integration focused tests
13. `make check-python`
14. compileall
15. `make check-release-quality`
16. fixture JSON diff check
17. targeted diff for wrapper/docs
18. `git diff --check`
19. conflict marker scan
20. code/docs safety scan
21. forbidden target diff check
22. residue check

## 13. Non-Equivalence Cautions

- release-quality integration design is not wrapper implementation
- future release-quality pass will not prove runtime correctness generally
- future multi-case pass will not prove invalid runtime fail-closed behavior
- future release-quality pass will not prove artifact body payload correctness
- v0.4 multi-case smoke is still metadata-only / body-free smoke
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

- Step608: actual-controlled v0.4 multi-case runtime smoke release-quality wrapper integration

Step608 should update only the wrapper and necessary README/docs. Step608 should not change Makefile, Python code/tests, fixture JSON, workflows, runtime implementation, validator implementation, manifest writer integration, or file writing.

## Step608 Implementation Reference

Step608 adds `release_quality_check: learner-state frozen policy generation actual-controlled v0.4 multi-case runtime smoke` to `scripts/check_release_quality.sh` using the command proposed in this design. The check is inserted after the actual-controlled v0.4 single-case runtime smoke and before artifact body fixture / CLI checks. Step608 does not change Makefile, workflows, Python code/tests, fixture JSON, runtime implementation, validator implementation, manifest writer integration, or file writing.

## Step609 Remote Run Record Workflow Reference

Step609 adds `docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_release_quality_remote_run_record_workflow.md` as a design-only / docs-only plan for a future public-safe status marker after Step608 wrapper integration. This release-quality integration design remains unchanged; Step609 does not create the marker or change wrapper, Makefile, workflow, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step610 Remote Status Marker Reference

Step610 adds the future public-safe status marker designed in Step609. This release-quality integration design remains unchanged; Step610 does not change wrapper, Makefile, workflow, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step611 Final Safety Review Reference

Step611 adds `docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_release_quality_chain_final_safety_review.md` as a final-safety-review-only / docs-only review for the Step602-Step610 all-valid multi-case runtime smoke chain. This release-quality integration design remains unchanged; Step611 does not change wrapper, Makefile, workflow, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step612 Next Boundary Planning Reference

Step612 adds `docs/frozen_policy_generation_runtime_chain_post_multi_case_final_safety_review_next_boundary_planning.md` as a planning-only / docs-only comparison after the Step611 final safety review. This release-quality integration design remains unchanged; Step612 does not change wrapper, Makefile, workflow, Python code/tests, fixture JSON, manifest writer integration, or file writing.
