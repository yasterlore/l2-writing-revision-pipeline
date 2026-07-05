# Post Invalid-Case Final Safety Review Next-Boundary Planning

## 1. Title

Post Invalid-Case Final Safety Review Next-Boundary Planning

## 2. Scope

This document is the planning-only / docs-only next-boundary planning record after the Step622 final safety review.

This step includes no implementation, no Makefile changes, no release-quality wrapper changes, no workflow changes, no Python code/tests changes, no fixture JSON changes, no runtime implementation changes, no validator implementation changes, no payload audit implementation, no manifest writer integration, and no file writing.

This planning document is not proof of production readiness, real-data readiness, or model performance.

## 3. Starting Point After Step622

Step622 accepted only this boundary:

```text
release-quality-integrated, remote-status-recorded, actual-controlled v0.4 invalid-case runtime fail-closed smoke for the fixed 26 selected invalid fail_closed cases
```

Accepted details:

- selected_case_count=26
- selected_invalid_case_count=26
- selected_valid_case_count=0
- deferred_case_count=4
- executed_case_count=26
- expected_fail_closed_case_count=26
- observed_fail_closed_case_count=26
- forbidden_body_emitted_case_count=0
- unsafe_signal_total_count=26
- residue_file_count=0
- artifact_body_payload_emitted_case_count=0
- manifest_writer_invoked_case_count=0
- file_writing_enabled_case_count=0
- final `release_quality_check: ok`

Deferred cases:

- `invalid/invalid_malformed_metadata_json`
- `invalid/invalid_missing_required_metadata_file`
- `invalid/invalid_unsupported_schema`
- `invalid/invalid_mismatched_expected_status`

Step622 did not accept production readiness, real-data readiness, model performance, F1 / accuracy / ECE / AURCC achievement, runtime correctness generally, all invalid-case runtime behavior, usage_error / mismatch invalid runtime behavior, artifact body payload correctness, manifest writer correctness, file-writing readiness, or safe-metadata free-form body safety.

## 4. Candidate Options

### Option A: Deferred Usage_Error / Mismatch Invalid Runtime Matrix Design

- description: Design a next runtime matrix for the 4 deferred invalid cases: 3 usage_error candidates and 1 mismatch candidate.
- expected value: Directly addresses the Step622 limitation that non-fail_closed invalid cases are not runtime-covered.
- safety risk: Low to moderate if kept design-only, metadata-only, body-free, and category-separated.
- implementation surface: None in Step623; future implementation would likely require a dedicated runner or runner extension, Makefile target, release-quality integration, remote marker, and final safety review.
- relation to Step622 limitations: Direct.
- whether it should be next: Yes.
- reason: It is the smallest boundary that directly follows from the accepted fail_closed matrix without expanding into payload, manifest writer, or file-writing surfaces.

### Option B: Payload Audit Design Without Payload Emission

- description: Design a payload audit boundary that keeps payload bodies suppressed and considers count-only / metadata-only audit signals.
- expected value: Moves toward later payload confidence without emitting bodies.
- safety risk: Moderate because payload-adjacent work can blur body inspection and body emission.
- implementation surface: None in a design-only step, but later steps would require careful audit-safe metadata policy.
- relation to Step622 limitations: Indirect; it addresses artifact body payload limitations, not the deferred invalid-case runtime limitation.
- whether it should be next: Not recommended next.
- reason: The 4 deferred usage_error / mismatch cases are a smaller and more direct continuation of the current runtime boundary.

### Option C: Manifest Writer Handoff Design

- description: Design a later handoff from runtime checks toward manifest writer / file-writing related boundaries.
- expected value: Could prepare integration planning across runtime and manifest writer chains.
- safety risk: Higher because manifest writer and file-writing surfaces are separate and broader.
- implementation surface: None in a design-only step, but future work risks pulling in output path, manifest body, and file-writing questions.
- relation to Step622 limitations: Indirect.
- whether it should be next: Not recommended next.
- reason: It does not directly address the deferred invalid-case limitation and would enlarge the boundary.

### Option D: Remote Metadata Consolidation

- description: Consolidate planned-only, single-case, all-valid multi-case, and invalid fail_closed remote status markers for easier cross-reference.
- expected value: Improves documentation navigation and comparison.
- safety risk: Low.
- implementation surface: Docs-only.
- relation to Step622 limitations: Indirect; it improves clarity but adds no runtime coverage.
- whether it should be next: Not recommended next unless navigation becomes the immediate blocker.
- reason: Useful, but it does not progress the next runtime boundary.

### Option E: Documentation Consolidation

- description: Consolidate README / status index / milestone recap / public checklist references after the Step613-Step622 chain.
- expected value: Improves readability and reduces navigation friction.
- safety risk: Low.
- implementation surface: Docs-only.
- relation to Step622 limitations: Indirect.
- whether it should be next: Not recommended next unless documentation maintenance is prioritized over boundary progress.
- reason: It adds no new safety boundary and does not address the deferred usage_error / mismatch cases.

## 5. Comparison Table

| Option | Directly addresses Step622 limitation | Keeps boundary small | Avoids payload/body emission | Avoids manifest writer / file writing | Release-quality staging clarity | Documentation value | Implementation risk | Recommended priority |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Option A: deferred usage_error / mismatch invalid runtime matrix design | High | High | High | High | High | Medium | Low in design; moderate later | First |
| Option B: payload audit design without payload emission | Medium | Medium | Medium if carefully designed | High | Medium | Medium | Moderate later | Later |
| Option C: manifest writer handoff design | Low | Low | Medium | Low | Medium | Medium | Higher later | Later |
| Option D: remote metadata consolidation | Low | High | High | High | Low | High | Low | Later / optional |
| Option E: documentation consolidation | Low | High | High | High | Low | High | Low | Later / optional |

## 6. Recommended Next Boundary

Recommended:

```text
Option A: deferred usage_error / mismatch invalid runtime matrix design
```

Reasons:

- Step622's largest remaining limitation is that the 4 deferred non-fail_closed invalid cases are not runtime-covered.
- The 26 fail_closed cases are an accepted boundary, but usage_error / mismatch behavior is not yet a final-safety-reviewed boundary.
- Payload audit, manifest writer, and file writing have larger surfaces than a usage_error / mismatch runtime matrix.
- A small deferred-case matrix design is more incremental and safer.
- Option A can begin as design-only, making it suitable for Step624.

## 7. Proposed Step624

Proposed Step624:

```text
Step624: actual-controlled v0.4 deferred invalid-case runtime usage_error / mismatch matrix design
```

Proposed doc path:

```text
docs/frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_matrix_design.md
```

Step624 scope:

- design-only / docs-only
- no runtime execution
- no Python code/tests changes
- no Makefile changes
- no release-quality wrapper changes
- no workflow changes
- no fixture JSON changes
- no manifest writer integration
- no file writing

Step624 should design:

- exact matrix for 3 usage_error cases and 1 mismatch case
- whether usage_error and mismatch should be one combined matrix or two separate matrices
- expected aggregate status semantics
- failure mapping
- output suppression policy
- relationship to the accepted fail_closed 26-case matrix
- future implementation chain

## 8. Proposed Future Chain After Step624

Tentative future chain:

- Step624: deferred invalid-case usage_error / mismatch matrix design
- Step625: fixture/matrix contract design
- Step626: runner implementation
- Step627: Makefile target design
- Step628: Makefile target implementation
- Step629: release-quality integration design
- Step630: wrapper integration
- Step631: remote status marker
- Step632: final safety review

This chain should be re-evaluated in Step624 if the usage_error and mismatch categories require separate chains.

## 9. Boundaries Explicitly Not Selected Now

Do not select now:

- payload audit implementation
- payload body emission
- manifest writer integration
- file writing
- production file-writing path
- real-data readiness check
- model performance check
- all-invalid broad runtime run without category separation
- usage_error / mismatch implementation before design

## 10. Relationship To Accepted Boundaries

Accepted boundaries remain complementary:

- planned-only v0.3 boundary: remains planned-only and not actual-controlled invocation.
- actual-controlled v0.4 single-case boundary: remains primary valid runtime smoke.
- actual-controlled v0.4 all-valid multi-case boundary: remains pass-matrix smoke.
- actual-controlled v0.4 invalid fail_closed 26-case boundary: remains fail_closed matrix smoke for the fixed 26 selected invalid cases.

The proposed next boundary would address deferred usage_error / mismatch cases without replacing any prior accepted boundary.

## 11. Non-Equivalence Cautions

- planning is not implementation.
- Step622 accepted the fail_closed matrix only, not usage_error / mismatch runtime behavior.
- deferred-case design would not prove payload correctness.
- metadata-only planning is not free-form body safety proof.
- release-quality success is not production readiness.
- synthetic-only pass is not real-data readiness.
- no model performance follows from this planning.

## 12. Non-Claims

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

## 13. Public-Safe Checklist

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

## Step624 Matrix Design Reference

Step624 adds `docs/frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_matrix_design.md` as the design-only / docs-only matrix design recommended by this planning document.

It recommends a combined deferred invalid status matrix for the 4 deferred non-fail_closed invalid cases and keeps runtime execution, implementation, Makefile changes, wrapper changes, workflow changes, fixture JSON changes, payload audit implementation, manifest writer integration, file writing, real-data readiness, and model performance claims out of Step624.

## Step625 Fixture Matrix Contract Reference

Step625 adds `docs/frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_fixture_matrix_contract_design.md` as a design-only / docs-only contract for the combined deferred invalid status matrix. It fixes selected case IDs, expected usage_error / mismatch categories, primary count policy, aggregate and per-case contracts, selection policy, failure mapping, and Step626 handoff while keeping runtime execution, Python code/tests changes, Makefile changes, wrapper changes, workflow changes, fixture JSON changes, payload audit implementation, manifest writer integration, file writing, real-data readiness, and model performance claims out of scope.

## Step626 Implementation Reference

Step626 adds a direct CLI-only runner and focused tests for the deferred usage_error / mismatch invalid matrix recommended by this planning chain. It remains outside Makefile target and release-quality integration, does not change fixture JSON, does not implement payload audit, does not invoke manifest writer, and does not enable file writing.

## Step627 Makefile Target Design Reference

Step627 adds `docs/frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_makefile_target_design.md` as a design-only / docs-only plan for a future standalone Makefile target around the Step626 runner. It does not change Makefile, wrapper, workflow, Python code/tests, fixture JSON, payload audit implementation, manifest writer integration, or file writing.

## Step628 Makefile Target Reference

Step628 adds the standalone Makefile target `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-deferred-invalid-case-runtime-usage-error-mismatch-smoke` for the Step626 runner. The target remains outside release-quality and does not change Python code/tests, fixture JSON, payload audit implementation, manifest writer integration, or file writing.

## Step629 Release-Quality Integration Design Reference

Step629 adds `docs/frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_release_quality_integration_design.md` as a design-only / docs-only plan for future wrapper integration of the Step628 target. It keeps implementation, Makefile changes, wrapper changes, workflow changes, Python code/tests changes, fixture JSON changes, payload audit implementation, manifest writer integration, and file writing out of Step629.

## Step630 Release-Quality Integration Reference

Step630 adds the Step628 deferred usage_error / mismatch target to `scripts/check_release_quality.sh` after the invalid fail_closed smoke and before artifact body fixture / CLI checks. It does not reopen the accepted fail_closed boundary and does not change Makefile, Python code/tests, fixture JSON, payload audit implementation, manifest writer integration, or file writing.
