# Actual-Controlled v0.4 Deferred Invalid-Case usage_error / mismatch Smoke Release Quality Integration Design

## 1. Title

Actual-Controlled v0.4 Deferred Invalid-Case usage_error / mismatch Smoke Release Quality Integration Design

## 2. Scope

This document is a design-only / docs-only plan for integrating the Step628 standalone deferred invalid-case usage_error / mismatch Makefile target into the future release-quality wrapper.

This Step629 document does not change the release-quality wrapper, Makefile, workflows, Python code/tests, fixture JSON, runtime implementation, validator implementation, payload audit implementation, manifest writer integration, or file writing. It is not evidence of production readiness, real-data readiness, or model performance.

## 3. Prior Chain Dependency

- Step622 accepted only the fixed 26 selected invalid fail_closed runtime smoke boundary.
- Step623 recommended deferred usage_error / mismatch invalid runtime matrix design.
- Step624 designed the combined deferred invalid status matrix.
- Step625 fixed exact 4 selected deferred invalid cases and aggregate contract.
- Step626 implemented direct CLI-only deferred invalid usage_error / mismatch runner and focused tests.
- Step627 designed standalone Makefile target.
- Step628 implemented standalone Makefile target.
- Step628 standalone target passes.
- Step628 target is not yet release-quality integrated.

## 4. Target to Integrate

Proposed release-quality label:

```text
release_quality_check: learner-state frozen policy generation actual-controlled v0.4 deferred invalid-case usage_error/mismatch smoke
```

Proposed command:

```bash
make check-learner-state-frozen-policy-generation-actual-controlled-v0-4-deferred-invalid-case-runtime-usage-error-mismatch-smoke
```

Expected public-safe summary:

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

## 5. Integration Options

### Option A: Integrate deferred target after invalid fail_closed target

- Runs actual-controlled fixture validation first.
- Runs single-case smoke next.
- Runs all-valid multi-case smoke next.
- Runs invalid fail_closed 26-case smoke next.
- Runs deferred usage_error / mismatch 4-case smoke after fail_closed smoke.
- Keeps positive path, fail_closed path, and deferred category path in staged order.

Benefits: clear staged order and direct coverage of the remaining deferred category boundary.

Risks: adds one more release-quality check, but the target is standalone and already scoped to body-free aggregate metadata.

Implementation complexity: low; add one wrapper entry using the existing wrapper pattern.

Safety boundary clarity: high; the check runs the existing standalone target only.

### Option B: Integrate deferred target before invalid fail_closed target

- Runs deferred usage_error / mismatch matrix before fail_closed matrix.
- Not recommended because the accepted fail_closed boundary should remain the primary invalid smoke before the smaller deferred matrix.

Benefits: surfaces deferred category issues earlier.

Risks: makes the invalid-case sequence less readable and separates the accepted fail_closed boundary from its current staging role.

Implementation complexity: low.

Safety boundary clarity: medium; ordering may imply the smaller deferred matrix is the primary invalid check.

### Option C: Replace invalid fail_closed target with deferred target

- Not recommended.
- These checks cover different semantics.
- fail_closed 26-case target and deferred usage_error/mismatch 4-case target are complementary.

Benefits: fewer wrapper checks.

Risks: removes the accepted 26-case fail_closed wrapper coverage and conflates separate invalid-case categories.

Implementation complexity: medium because it changes existing wrapper behavior.

Safety boundary clarity: low; replacement would blur the accepted fail_closed boundary.

### Option D: Defer release-quality integration

- Safest if standalone target is unstable.
- Not necessary if Step628 target and focused tests passed.

Benefits: avoids any wrapper change in the immediate next step.

Risks: leaves the deferred usage_error / mismatch target outside release-quality after standalone validation has passed.

Implementation complexity: none now.

Safety boundary clarity: high, but coverage staging remains incomplete.

## 6. Recommended Option

Recommend Option A.

Required ordering around actual-controlled runtime smoke checks:

1. actual-controlled fixture validation
2. actual-controlled v0.4 single-case runtime smoke
3. actual-controlled v0.4 all-valid multi-case runtime smoke
4. actual-controlled v0.4 invalid-case fail_closed smoke
5. actual-controlled v0.4 deferred invalid-case usage_error / mismatch smoke
6. artifact body fixture validation / artifact body generation CLI checks

Rationale:

- fixture root and schema contract should be validated before runtime smoke.
- single-case smoke remains a fast primary gate.
- all-valid multi-case smoke verifies positive pass-matrix behavior first.
- invalid fail_closed smoke verifies the accepted 26-case fail_closed boundary.
- deferred usage_error / mismatch smoke verifies the remaining 4-case category boundary.
- artifact body / manifest writer / file writing remain separate.
- release-quality order remains readable and staged.

## 7. Proposed Insertion Point in `scripts/check_release_quality.sh`

Recommended insertion:

- after existing actual-controlled v0.4 invalid-case runtime fail_closed smoke
- before artifact body fixture validation / artifact body generation CLI checks

Expected local order around the insertion area:

1. planned-only runtime invocation fixture validation
2. planned-only v0.3 runtime invocation smoke
3. actual-controlled fixture validation
4. actual-controlled v0.4 single-case runtime smoke
5. actual-controlled v0.4 all-valid multi-case runtime smoke
6. actual-controlled v0.4 invalid-case fail_closed smoke
7. actual-controlled v0.4 deferred invalid-case usage_error / mismatch smoke
8. artifact body fixture validation
9. artifact body generation CLI smoke
10. artifact body generation safe-metadata CLI smoke

If the current wrapper order differs, place the new check adjacent to the invalid fail_closed target and before broader artifact body / manifest writer checks.

## 8. Expected Step630 Wrapper Changes

Step630 should:

- update `scripts/check_release_quality.sh`
- add one `run_check` entry or equivalent project wrapper pattern
- add the label and command for the deferred usage_error / mismatch target
- not modify Makefile
- not modify Python code/tests
- not modify fixture JSON
- not modify workflows
- not implement runtime changes
- not invoke manifest writer
- not enable file writing
- run the standalone deferred target
- run `make check-release-quality`
- update root README and full technical specification related docs because Step630 is implementation

## 9. Relationship to Existing Release-Quality Checks

Existing release-quality checks must remain unchanged:

- actual-controlled fixture validation
- actual-controlled v0.4 single-case runtime smoke
- actual-controlled v0.4 all-valid multi-case runtime smoke
- actual-controlled v0.4 invalid-case fail_closed smoke
- planned-only runtime invocation fixture validation
- planned-only v0.3 runtime invocation smoke
- artifact body fixture validation
- artifact body generation CLI smoke
- artifact body generation safe-metadata CLI smoke
- manifest writer checks
- general Python checks

The deferred release-quality check:

- adds selected deferred usage_error / mismatch runtime/preflight coverage
- uses exact 4 selected deferred invalid cases
- excludes 26 fail_closed invalid cases
- excludes all valid cases
- does not replace all-valid multi-case target
- does not replace invalid fail_closed target
- does not replace single-case target
- does not replace actual-controlled fixture validator
- does not replace planned-only v0.3 target
- does not replace artifact body safe-metadata CLI smoke
- does not replace manifest writer checks
- does not prove runtime correctness generally
- does not imply production readiness

## 10. Safety Boundary

The release-quality check must:

- run only the standalone deferred usage_error / mismatch Makefile target
- use synthetic metadata-only fixtures
- select the fixed 4 deferred invalid cases
- exclude the 26 fail_closed invalid cases
- exclude all 6 valid cases
- use `processed_case_count=4` as primary count
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

- Deferred target failure may indicate category mismatch, selected/excluded case confusion, missing flags, forbidden body emission, unexpected pass, unexpected fail_closed, runner-level usage_error, runner-level mismatch, manifest writer invocation, file writing, or residue.
- Pass means all 4 selected deferred invalid cases matched expected per-case usage_error / mismatch categories with body-free output and no residue.
- Pass does not mean individual invalid cases passed.
- Pass does not prove runtime correctness generally.
- Pass does not prove all invalid-case behavior generally.
- Pass does not prove artifact body payload correctness.
- Pass does not imply production readiness or real-data readiness.

## 12. Validation Plan for Step630

Step630 should run:

- `git status --short`
- wrapper label / command / ordering check
- `make help` check for deferred target
- deferred Makefile target
- direct deferred CLI
- focused deferred tests
- existing invalid fail_closed tests
- existing invalid fail_closed Makefile target
- existing all-valid multi-case tests
- existing all-valid multi-case Makefile target
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

## 13. Non-Equivalence Cautions

- release-quality integration design is not wrapper implementation.
- future release-quality pass will not prove runtime correctness generally.
- future deferred target pass will not prove all invalid-case behavior generally.
- future deferred target pass will not prove payload correctness.
- deferred usage_error / mismatch smoke is metadata-only / body-free.
- fail_closed smoke is not equivalent to deferred usage_error / mismatch smoke.
- count-only metadata is not free-form body safety proof.
- manifest writer validators remain separate.
- release-quality success is not production readiness.
- synthetic-only pass is not real-data readiness.

## 14. Non-Claims

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

## 15. Public-Safe Checklist

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

## 16. Recommended Next Step

Recommended next step:

- Step630: deferred invalid-case usage_error / mismatch release-quality wrapper integration

Step630 should update only wrapper and necessary README/docs. Step630 should not change Makefile, Python code/tests, fixture JSON, workflows, payload audit implementation, manifest writer integration, or file writing.

## Step630 Implementation Reference

Step630 adds `release_quality_check: learner-state frozen policy generation actual-controlled v0.4 deferred invalid-case usage_error/mismatch smoke` to `scripts/check_release_quality.sh`.

The wrapper check follows this design with command `make check-learner-state-frozen-policy-generation-actual-controlled-v0-4-deferred-invalid-case-runtime-usage-error-mismatch-smoke`, insertion after the invalid fail_closed smoke and before artifact body fixture / CLI checks, and the same aggregate public-safe output boundary. Remote/manual run record workflow design remains future work.

## Step631 Remote Run Record Workflow Reference

Step631 adds `docs/frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_release_quality_remote_run_record_workflow.md` as a design-only / docs-only plan for a future public-safe status marker after Step630 wrapper integration. It keeps wrapper, Makefile, workflow, Python code/tests, fixture JSON, payload audit implementation, manifest writer integration, and file writing unchanged.
