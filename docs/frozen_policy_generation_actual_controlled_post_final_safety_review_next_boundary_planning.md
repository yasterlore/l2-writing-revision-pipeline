# Post-Final-Safety-Review Planning for the Next Actual-Controlled Boundary

## Scope

This document is the next-boundary planning doc after the Step600 final safety review for the actual-controlled artifact body generation runtime invocation chain.

This is a planning-only / docs-only step. It does not change the release-quality wrapper, Makefile, workflows, Python code/tests, fixture JSON, runtime implementation, validator implementation, artifact body generation implementation, manifest writer integration, manifest body generation, generated policy body generation, artifact body file writing, or manifest file writing.

This planning document does not provide production readiness, real-data readiness, or model performance evidence.

## Starting Point From Step600

Step600 records that the Step585-Step599 chain reached a release-quality-integrated actual-controlled v0.4 metadata-only runtime invocation smoke boundary. It also reached a remote-status-recorded boundary.

The v0.4 runtime smoke is actual-controlled, but it remains metadata-only / body-free. The v0.4 smoke uses one primary valid case. The fixture validator covers valid and invalid metadata-only cases. Manifest writer integration remains separate. File writing remains separate. Artifact body payload correctness remains separate. Model performance remains separate. No real participant data was used.

## Decision Question

Main question:

- What should be the next boundary after Step600?

Secondary questions:

- Should the next boundary expand runtime smoke coverage to multiple cases?
- Should the next boundary audit artifact body payload handling without emitting payload bodies?
- Should the next boundary prepare manifest writer handoff design?
- Should the next boundary refresh remote release-quality metadata instead?
- Should the next boundary pause implementation and consolidate documentation?

## Candidate Next Boundaries

### Option A: Actual-Controlled v0.4 Multi-Case Runtime Smoke Design

Purpose:

- Expand beyond one primary valid smoke case.
- Design a controlled multi-case runtime smoke over selected valid cases and selected invalid/fail-closed cases.
- Keep metadata-only / body-free / no manifest writer / no file writing.
- Do not emit payload body.
- Do not claim runtime correctness generally.

Potential future chain:

- Step602: multi-case runtime smoke design
- Step603: multi-case fixture/root or invocation matrix design
- Step604: implementation
- Step605: Makefile target design
- Step606: Makefile target implementation
- Step607: release-quality integration design
- Step608: release-quality wrapper integration
- Step609: remote status marker
- Step610: final safety review

Benefits:

- Directly addresses the Step600 limitation that runtime smoke uses one primary valid case.
- Still stays within the metadata-only runtime boundary.
- Lower risk than artifact payload or manifest writer handoff.
- Keeps the next chain close to the already reviewed v0.4 runtime.

Risks:

- More runtime cases may require careful fixture/case selection.
- Invalid-case runtime execution must avoid raw payloads and unsafe outputs.
- May require additional test infrastructure.

### Option B: Artifact Body Payload Audit Design Without Payload Emission

Purpose:

- Prepare an audit boundary around artifact body payload correctness without copying or emitting payload bodies.
- Use count-only / hash-only metadata if allowed later, but do not implement it now.
- Keep no raw body in docs.

Benefits:

- Moves toward payload confidence without exposing payloads.
- Addresses the artifact body payload correctness limitation.

Risks:

- Higher leakage risk.
- Requires careful policy for what counts as audit-safe metadata.
- Could accidentally blur payload body inspection and payload body emission.
- Should not be first step unless the multi-case metadata-only runtime boundary is stable.

### Option C: Manifest Writer Handoff Design

Purpose:

- Design how v0.4 actual-controlled runtime output may later hand off to manifest writer checks.

Benefits:

- Moves toward integration after artifact body generation runtime.
- Connects to existing manifest writer validators.

Risks:

- Step600 explicitly says manifest writer remains separate.
- Handoff may create pressure toward file writing.
- More complex safety boundary.
- Not recommended immediately after Step600.

### Option D: Remote Release-Quality Metadata Refresh Design

Purpose:

- Create a small workflow to refresh remote metadata if future GitHub Actions run metadata changes.

Benefits:

- Low risk.
- Keeps status docs current.

Risks:

- Does not address the primary technical limitation.
- Mainly administrative.

### Option E: Consolidation-Only Documentation Pass

Purpose:

- Pause implementation and consolidate docs indexes.

Benefits:

- Lowest risk.
- Useful if docs are hard to navigate.

Risks:

- Does not advance the runtime boundary.
- Could create documentation churn.

## Recommended Option

Recommend Option A unless there is a documented reason to pause.

Recommended next step:

- Step602: actual-controlled v0.4 multi-case runtime smoke design

Step602 should remain design-only. It should not implement the multi-case runner yet. It should not change fixture JSON yet unless Step602 explicitly decides a later fixture-root design is required. It should not involve manifest writer integration. It should not involve file writing. It should not emit artifact body payload. It should keep all outputs public-safe / metadata-only / body-free. It should not claim runtime correctness generally.

## Why Not Proceed Directly To Payload Audit Or Manifest Writer

Artifact body payload audit is higher risk than multi-case metadata-only runtime smoke. Manifest writer handoff is a broader integration boundary. File writing is explicitly outside the reviewed Step585-Step599 boundary. Real-data readiness is not supported by the current chain. Performance claims are unrelated to this boundary.

Multi-case metadata-only runtime smoke is the least risky way to address the most direct Step600 limitation.

## Proposed Step602 Scope

Step602 should:

- create a design doc for actual-controlled v0.4 multi-case runtime smoke
- decide whether to use the existing actual-controlled fixture root or a new runtime smoke matrix
- select candidate valid cases from the existing actual-controlled fixture root
- decide whether selected invalid cases should be executed through runtime or only validated through fixture validator
- define pass / usage_error / fail_closed / mismatch expectations for multi-case smoke
- define summary aggregation fields
- define public-safe output requirements
- define whether a new validator or runner is needed
- define future Makefile target and release-quality staging
- remain design-only / docs-only

Step602 should not:

- implement Python code
- modify Makefile
- modify release-quality wrapper
- modify workflow
- modify fixture JSON
- invoke manifest writer
- enable file writing
- emit artifact body payload
- use real data

## Proposed Step602 Design Doc Path

Recommended path:

- `docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_design.md`

## Possible Step602 Design Questions

- Should multi-case smoke run all 6 valid actual-controlled cases or a curated subset?
- Should fail-closed invalid cases be executed, or only fixture-validated?
- Should a new aggregation CLI mode be added later, or should Step604 loop over cases through existing CLI?
- Should the aggregated output be key-value text or JSON metadata summary?
- How should the runner suppress raw stdout/stderr for each case?
- How should residue checks be performed across multiple cases?
- How should safe-metadata field counts be compared across cases?
- How should v0.1/v0.2/v0.3 compatibility be rechecked?
- How should runtime nonzero or ambiguous case output map to fail_closed?
- How should release-quality target ordering change later?

## Future Chain Proposal

Recommended future chain:

- Step602: actual-controlled v0.4 multi-case runtime smoke design
- Step603: multi-case runtime smoke fixture/matrix contract design
- Step604: multi-case runtime smoke implementation
- Step605: multi-case runtime smoke Makefile target design
- Step606: multi-case runtime smoke Makefile target implementation
- Step607: multi-case runtime smoke release-quality integration design
- Step608: multi-case runtime smoke release-quality wrapper integration
- Step609: multi-case runtime smoke remote status marker
- Step610: multi-case runtime smoke final safety review

This chain is tentative and should be revised if Step602 finds unsafe assumptions.

## Safety Boundary For Next Chain

The next chain must:

- stay synthetic-only
- stay metadata-only
- stay body-free
- use public-safe summaries
- suppress raw stdout/stderr
- avoid fixture JSON body copies
- avoid request / pointer / expected body copies
- avoid artifact body payload
- avoid manifest body
- avoid generated policy body
- avoid raw rows
- avoid logits/probabilities
- avoid private / absolute path values
- avoid raw learner text
- avoid real participant data
- avoid manifest writer invocation
- avoid file writing
- avoid production readiness claims
- avoid real-data readiness claims
- avoid model performance claims

## Non-Equivalence Cautions

- Planning doc is not implementation.
- Multi-case smoke, even if later implemented, will not prove runtime correctness generally.
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

- Step602: actual-controlled v0.4 multi-case runtime smoke design

Step602 should be design-only. Step602 should not implement runtime code, modify Makefile, modify the release-quality wrapper, modify workflow, modify fixture JSON unless it explicitly chooses a later fixture contract step, invoke manifest writer, enable file writing, or use real data.

## Step602 Design Reference

Step602 adds
`docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_design.md`
as a design-only / docs-only plan for the recommended actual-controlled v0.4
multi-case runtime smoke boundary. It keeps the Step601 recommendation
planning-only and does not change Python code/tests, Makefile, wrapper,
workflow, fixture JSON, runtime implementation, manifest writer integration,
or file writing.

## Step603 Fixture Matrix Contract Reference

Step603 adds
`docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_fixture_matrix_contract_design.md`
as a design-only / docs-only contract for the future all-valid multi-case
runtime smoke matrix. This planning doc remains unchanged.

## Step604 Implementation Reference

Step604 implements the recommended direct CLI-only all-valid multi-case runner and focused tests. The implementation keeps Makefile target design, release-quality integration, manifest writer integration, file writing, payload audit, and real-data use outside this boundary.

## Step605 Makefile Target Design Reference

Step605 designs the future standalone Makefile target for the Step604 runner. This planning document remains unchanged; Step605 does not change Makefile, wrapper, workflow, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step606 Makefile Target Implementation Reference

Step606 implements the standalone Makefile target for the Step604 runner. This planning document remains unchanged; release-quality integration, manifest writer integration, and file writing remain out of scope.

## Step607 Release-Quality Integration Design Reference

Step607 designs future release-quality wrapper integration for the Step606 standalone multi-case target. This planning document remains unchanged; Step607 does not change wrapper, Makefile, workflow, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step608 Release-Quality Integration Reference

Step608 adds the Step606 standalone multi-case target to the release-quality wrapper. This planning document remains unchanged; Step608 does not change Makefile, workflow, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step609 Remote Run Record Workflow Reference

Step609 designs a future public-safe remote/manual run status marker for the Step608 wrapper-integrated multi-case check. This planning document remains unchanged; Step609 does not create the marker or change wrapper, Makefile, workflow, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step610 Remote Status Marker Reference

Step610 adds the public-safe status marker for the Step608 wrapper-integrated multi-case check. This planning document remains unchanged; Step610 does not change wrapper, Makefile, workflow, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step611 Final Safety Review Reference

Step611 adds `docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_release_quality_chain_final_safety_review.md` as a final-safety-review-only / docs-only review for the Step602-Step610 all-valid multi-case runtime smoke chain. This planning document remains unchanged; Step611 does not change wrapper, Makefile, workflow, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## Step612 Next Boundary Planning Reference

Step612 adds `docs/frozen_policy_generation_runtime_chain_post_multi_case_final_safety_review_next_boundary_planning.md` as a planning-only / docs-only comparison after the Step611 final safety review. This earlier planning document remains unchanged and is not replaced by Step612.

## Step613 Invalid-Case Matrix Design Reference

Step613 adds `docs/frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_matrix_design.md` as a design-only / docs-only plan for a future invalid-case runtime fail-closed smoke. This earlier planning document remains unchanged and is not replaced by Step613.

## Step614 Fixture Matrix Contract Reference

Step614 adds `docs/frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_fixture_matrix_contract_design.md` as a design-only / docs-only contract for the future invalid-case runtime fail-closed smoke. This earlier planning document remains unchanged and is not replaced by Step614.

## Step615 Implementation Status Reference

Step615 implements a direct CLI-only invalid-case fail-closed runner and focused tests after the Step613/Step614 design work. This earlier planning document remains unchanged and is not replaced by Step615. Step615 does not add Makefile integration, release-quality wrapper integration, workflow changes, fixture JSON changes, manifest writer integration, file writing, production readiness, real-data readiness, or model performance claims.

## Step616 Makefile Target Design Reference

Step616 adds a design-only / docs-only plan for the future standalone Makefile target around the Step615 runner. This earlier planning document remains unchanged and is not replaced by Step616.

## Step617 Makefile Target Status Reference

Step617 adds the standalone invalid-case fail-closed Makefile target for the Step615 runner. This earlier Step601 planning document remains unchanged and is not replaced by Step617; release-quality integration for the invalid-case target remains a later design boundary.
