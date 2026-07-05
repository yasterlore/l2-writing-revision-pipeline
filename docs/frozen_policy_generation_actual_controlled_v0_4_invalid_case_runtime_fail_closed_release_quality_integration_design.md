# Actual-Controlled v0.4 Invalid-Case Runtime Fail-Closed Smoke Release Quality Integration Design

## 1. Scope

This document is the Step618 design-only / docs-only plan for integrating the Step617 standalone invalid-case fail-closed Makefile target into the future release-quality wrapper.

This step does not change the release-quality wrapper, change Makefile, change workflow files, change Python code/tests, change fixture JSON, change runtime implementation, implement manifest writer integration, or perform file writing.

This document is not evidence of production readiness, real-data readiness, or model performance.

## 2. Prior Chain Dependency

- Step611 accepted only the all-valid multi-case runtime smoke boundary.
- Step612 recommended invalid-case runtime fail-closed matrix design.
- Step613 designed a fail_closed-only invalid matrix.
- Step614 fixed the exact 26 selected invalid fail_closed cases and 4 deferred cases.
- Step615 implemented the direct CLI-only invalid-case fail-closed runner and focused tests.
- Step616 designed the standalone Makefile target.
- Step617 implemented the standalone Makefile target.
- Step617 standalone target passes.
- Step617 target is not yet release-quality integrated.

## 3. Target To Integrate

Proposed release-quality label:

```text
release_quality_check: learner-state frozen policy generation actual-controlled v0.4 invalid-case runtime fail-closed smoke
```

Proposed command:

```bash
make check-learner-state-frozen-policy-generation-actual-controlled-v0-4-invalid-case-runtime-fail-closed-smoke
```

Expected public-safe summary:

- mode=actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke
- schema_version=learner_state_frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke_v0.1
- status=pass
- reason_code=none
- matrix_name=actual_controlled_v0_4_invalid_fail_closed_runtime_smoke
- case_selection=fail-closed-invalid
- selected_case_count=26
- selected_invalid_case_count=26
- selected_valid_case_count=0
- deferred_case_count=4
- executed_case_count=26
- pass_case_count=0
- expected_fail_closed_case_count=26
- observed_fail_closed_case_count=26
- usage_error_case_count=0
- mismatch_case_count=0
- input_error_case_count=0
- runtime_schema_version=learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4
- integration_mode=artifact-body-runtime-invocation-controlled
- all_selected_cases_failed_closed=True
- artifact_body_payload_emitted_case_count=0
- manifest_writer_invoked_case_count=0
- file_writing_enabled_case_count=0
- artifact_file_written_case_count=0
- manifest_file_written_case_count=0
- raw_stdout_body_suppressed_case_count=26
- raw_stderr_body_suppressed_case_count=26
- forbidden_body_emitted_case_count=0
- unsafe_signal_total_count=26
- residue_file_count=0
- content_suppressed=True
- body_suppressed=True
- metadata_only_checked=True
- synthetic_only_checked=True
- no_oracle_checked=True
- production_readiness_claimed=False
- real_data_readiness_claimed=False
- performance_claims_present=False

`unsafe_signal_total_count=26` is expected for this invalid fail-closed smoke. It is not raw body emission. `forbidden_body_emitted_case_count=0` remains required.

## 4. Integration Options

### Option A: Integrate Invalid-Case Fail-Closed Target After All-Valid Multi-Case Runtime Smoke

- Runs actual-controlled fixture validation first.
- Runs single-case smoke next.
- Runs all-valid multi-case smoke next.
- Runs invalid-case fail-closed smoke after pass-matrix smoke.
- Keeps pass boundary before fail-closed boundary.

Benefits: staged ordering is readable, the positive pass matrix gates the invalid fail-closed matrix, and the new check stays adjacent to the actual-controlled v0.4 runtime checks.

Risks: release-quality runtime duration increases slightly, and failures must be interpreted as fail-closed smoke or safety-scan failures rather than broad runtime correctness evidence.

Implementation complexity: low, because Step617 already provides the standalone target.

Safety boundary clarity: high, because the target is aggregate-only, metadata-only, body-free, no-manifest-writer, and no-file-writing.

### Option B: Integrate Invalid-Case Fail-Closed Target Before All-Valid Multi-Case Runtime Smoke

- Runs invalid fail-closed matrix before all-valid pass matrix.
- Not recommended because pass-matrix smoke should remain the broader positive-path gate before fail-closed invalid matrix.

Benefits: surfaces selected fail_closed invalid failures earlier.

Risks: less readable staging and less useful gating order.

Implementation complexity: low.

Safety boundary clarity: medium, because the ordering may obscure the pass-matrix / fail-closed-matrix distinction.

### Option C: Replace All-Valid Multi-Case Smoke With Invalid-Case Fail-Closed Smoke

- Not recommended.
- These checks cover different semantics.
- All-valid expects pass; invalid-case expects fail_closed.

Benefits: fewer checks.

Risks: loses all-valid multi-case positive-path coverage and blurs distinct runtime boundaries.

Implementation complexity: medium because it would alter existing wrapper semantics.

Safety boundary clarity: low.

### Option D: Defer Release-Quality Integration

- Safest if standalone target is unstable.
- Not necessary if Step617 target and focused tests passed.

Benefits: no wrapper change in the next implementation step.

Risks: leaves the Step617 standalone target outside release-quality despite passing focused checks.

Implementation complexity: none now.

Safety boundary clarity: high but coverage gain is deferred.

## 5. Recommended Option

Recommend Option A.

Required ordering:

1. actual-controlled fixture validation
2. actual-controlled v0.4 single-case runtime smoke
3. actual-controlled v0.4 all-valid multi-case runtime smoke
4. actual-controlled v0.4 invalid-case runtime fail-closed smoke
5. artifact body fixture validation / artifact body generation CLI checks

Rationale:

- fixture root and schema contract should be validated before runtime smoke
- single-case smoke remains a fast primary gate
- all-valid multi-case smoke verifies positive pass-matrix behavior first
- invalid-case fail-closed smoke verifies selected invalid fail-closed behavior second
- artifact body / manifest writer / file writing remain separate
- release-quality order remains readable and staged

## 6. Proposed Insertion Point In `scripts/check_release_quality.sh`

Recommended insertion:

- after existing actual-controlled v0.4 all-valid multi-case runtime smoke
- before artifact body fixture validation / artifact body generation CLI checks

Expected local order around the insertion area:

1. planned-only runtime invocation fixture validation
2. planned-only v0.3 runtime invocation smoke
3. actual-controlled fixture validation
4. actual-controlled v0.4 single-case runtime smoke
5. actual-controlled v0.4 all-valid multi-case runtime smoke
6. actual-controlled v0.4 invalid-case runtime fail-closed smoke
7. artifact body fixture validation
8. artifact body generation CLI smoke
9. artifact body generation safe-metadata CLI smoke

If the current wrapper order differs, place the new check adjacent to the actual-controlled all-valid multi-case runtime smoke and before broader artifact body / manifest writer checks.

## 7. Expected Step619 Wrapper Changes

Step619 should:

- update `scripts/check_release_quality.sh`
- add one `run_check` entry or equivalent project wrapper pattern
- add the label and command for the invalid-case fail-closed target
- not modify Makefile
- not modify Python code/tests
- not modify fixture JSON
- not modify workflows
- not implement runtime changes
- not invoke manifest writer
- not enable file writing
- run the standalone invalid-case target
- run `make check-release-quality`
- update root README and full technical specification related docs because Step619 is implementation

## 8. Relationship To Existing Release-Quality Checks

Existing release-quality checks must remain unchanged:

- actual-controlled fixture validation
- actual-controlled v0.4 single-case runtime smoke
- actual-controlled v0.4 all-valid multi-case runtime smoke
- planned-only runtime invocation fixture validation
- planned-only v0.3 runtime invocation smoke
- artifact body fixture validation
- artifact body generation CLI smoke
- artifact body generation safe-metadata CLI smoke
- manifest writer checks
- general Python checks

The invalid-case release-quality check:

- adds selected invalid fail_closed runtime coverage
- uses exact 26 selected invalid fail_closed cases
- defers usage_error / mismatch cases
- does not replace all-valid multi-case target
- does not replace single-case target
- does not replace actual-controlled fixture validator
- does not replace planned-only v0.3 target
- does not replace artifact body safe-metadata CLI smoke
- does not replace manifest writer checks
- does not prove runtime correctness generally
- does not imply production readiness

## 9. Safety Boundary

The release-quality check must:

- run only the standalone invalid-case fail-closed Makefile target
- use synthetic metadata-only fixtures
- select the fixed 26 invalid fail_closed cases
- defer the 4 non-fail_closed invalid cases
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

- invalid-case target failure means fail-closed smoke or its safety scan failed
- failure may indicate selected matrix mismatch, selected/deferred case confusion, missing flags, forbidden body emission, unexpected pass, unexpected usage_error, manifest writer invocation, file writing, or residue
- pass means all 26 selected invalid cases reached expected fail_closed status with body-free output and no residue
- pass does not prove runtime correctness generally
- pass does not prove all invalid-case behavior generally
- pass does not prove usage_error / mismatch invalid runtime behavior
- pass does not prove artifact body payload correctness
- pass does not imply production readiness or real-data readiness

## 11. Validation Plan For Step619

Step619 should run:

- `git status --short`
- wrapper label / command / ordering check
- `make help` check for invalid-case target
- invalid-case Makefile target
- direct invalid-case CLI
- focused invalid-case tests
- all-valid multi-case tests
- all-valid multi-case Makefile target
- existing v0.4 single-case runtime target
- existing actual-controlled fixture validator target
- existing planned-only v0.3 runtime target
- existing safe-metadata runtime target
- existing artifact body safe-metadata CLI smoke
- existing runtime integration focused tests
- make check-python
- compileall
- make check-release-quality
- fixture JSON diff check
- targeted diff for wrapper/docs
- `git diff --check`
- conflict marker scan
- code/docs safety scan
- forbidden target diff check
- residue check

## 12. Non-Equivalence Cautions

- release-quality integration design is not wrapper implementation
- future release-quality pass will not prove runtime correctness generally
- future invalid-case pass will not prove all invalid-case behavior generally
- future invalid-case pass will not prove usage_error / mismatch invalid runtime behavior
- future release-quality pass will not prove artifact body payload correctness
- invalid-case smoke is metadata-only / body-free fail-closed smoke
- all-valid multi-case smoke is not equivalent to invalid-case fail-closed smoke
- planned-only v0.3 pass remains not actual-controlled invocation
- artifact body generation safe-metadata CLI smoke is not equivalent to v0.4 runtime smoke
- count-only metadata is not free-form body safety proof
- manifest writer validators are separate
- release-quality success is not production readiness
- synthetic-only pass is not real-data readiness

## 13. Non-Claims

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

- Step619: actual-controlled v0.4 invalid-case runtime fail-closed smoke release-quality wrapper integration

Step619 should update only wrapper and necessary README/docs. Step619 should not change Makefile, change Python code/tests, change fixture JSON, change workflow, implement manifest writer integration, or enable file writing.

## 16. Step619 Implementation Status

Step619 adds `release_quality_check: learner-state frozen policy generation actual-controlled v0.4 invalid-case runtime fail-closed smoke` to `scripts/check_release_quality.sh`.

The check runs `make check-learner-state-frozen-policy-generation-actual-controlled-v0-4-invalid-case-runtime-fail-closed-smoke` after the actual-controlled v0.4 all-valid multi-case runtime smoke and before artifact body fixture / CLI checks. It is release-quality wrapper integration only; Step619 does not change Makefile, workflow, Python code/tests, fixture JSON, runtime implementation, validator implementation, manifest writer integration, or file writing.

Expected aggregate output remains public-safe and metadata-only: 26 selected invalid cases, 4 deferred cases, 26 executed cases, 26 observed fail_closed cases, `unsafe_signal_total_count=26`, `forbidden_body_emitted_case_count=0`, and `residue_file_count=0`. `unsafe_signal_total_count=26` is expected for this invalid fail-closed smoke and is not raw body emission.

Recommended next step:

- Step620: actual-controlled v0.4 invalid-case runtime fail-closed smoke release-quality remote/manual run record workflow design

## 17. Step620 Remote Run Record Workflow Design Reference

Step620 adds `docs/frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_release_quality_remote_run_record_workflow.md` as a design-only / docs-only workflow for a future Step621 public-safe status marker after Step619 wrapper integration.

The workflow design keeps this release-quality integration unchanged. It defines allowed evidence sources, forbidden raw log / payload sources, metadata fields, invalid-case count-only summary fields, missing metadata handling, and Step621 / Step622 staging without creating a marker, changing wrapper, changing Makefile, changing workflow, changing Python code/tests, changing fixture JSON, invoking manifest writer, or enabling file writing.
