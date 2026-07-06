# Actual-Controlled v0.4 Artifact Body Payload Audit Without Payload Emission Fixture Contract Design

## 1. Title

Actual-Controlled v0.4 Artifact Body Payload Audit Without Payload Emission Fixture Contract Design

## 2. Scope

This document fixes a future fixture / matrix / metadata contract for an actual-controlled v0.4 artifact body payload audit that remains body-free, metadata-only, and count-only.

This is design-only / docs-only. Step636 does not implement payload audit, emit payload bodies, output artifact body payloads, output generated policy bodies, output manifest bodies, implement manifest writer integration, perform file writing, change Python code/tests, change Makefile, change the release-quality wrapper, change workflow files, change fixture JSON, change runtime implementation, or change validator implementation.

This contract design is not proof of production readiness, real-data readiness, model performance, runtime correctness generally, payload correctness, artifact body quality, free-form body safety, manifest writer correctness, file-writing readiness, generated policy quality, or learner-state estimator correctness.

## 3. Prior Chain Dependency

This contract depends on:

- Step622 accepted the release-quality-integrated, remote-status-recorded fixed 26 invalid fail_closed boundary.
- Step633 accepted the release-quality-integrated, remote-status-recorded fixed 4 deferred invalid usage_error / mismatch boundary.
- Step634 recommended payload audit without payload emission as the next boundary.
- Step635 designed the body-free / metadata-only / count-only payload audit boundary.

Step635 recommended:

```text
Surface A + Surface C:
metadata-only payload audit summary + fixture-contract expected counts
```

Step636 fixes that recommendation as a future contract only. It does not execute the audit and does not require any current runner to emit the fields below.

## 4. Contract Goal

The goal is to define exact future aggregate counts for a payload audit that can confirm only metadata and suppression invariants.

The contract should allow a future runner or checker to determine whether:

- selected fixture categories match the accepted actual-controlled v0.4 matrices
- payload-capable valid cases are counted without emitting payload bodies
- invalid cases are counted as no-payload-expected categories
- payload emission remains suppressed
- forbidden body emission remains zero
- manifest writer invocation remains zero
- file writing remains zero
- residue remains zero

The contract must not determine:

- artifact body payload correctness
- artifact body quality
- generated policy quality
- free-form body safety
- manifest writer correctness
- file-writing readiness
- runtime correctness generally
- all invalid-case behavior generally

## 5. Matrix Name And Case Selection

Future matrix name:

```text
actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission
```

Future case selection:

```text
payload-audit-without-payload-emission
```

Future mode:

```text
actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission
```

Future schema version:

```text
learner_state_frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission_v0.1
```

The future audit should use these identifiers only for metadata and aggregate summaries. It must not print fixture bodies or payload bodies.

## 6. Selected Fixture Scope

The future audit should select the accepted actual-controlled v0.4 fixture categories by metadata contract, not by body inspection.

Selected scope:

- 6 valid all-valid multi-case runtime smoke cases
- 26 invalid fail_closed cases from the accepted fail_closed matrix
- 4 deferred invalid usage_error / mismatch cases from the accepted deferred matrix

Aggregate selected count:

```text
selected_case_count=36
selected_valid_case_count=6
selected_invalid_case_count=30
selected_fail_closed_invalid_case_count=26
selected_deferred_invalid_case_count=4
selected_usage_error_case_count=3
selected_mismatch_case_count=1
```

This is a count-only selection contract. Step636 does not list fixture JSON bodies and does not require runtime execution.

## 7. Expected Payload Category Counts

The future audit should distinguish payload-capable valid cases from invalid cases where payload emission should remain absent.

Expected payload category counts:

```text
expected_payload_capable_case_count=6
expected_payload_not_applicable_case_count=30
expected_payload_availability_checked_case_count=6
expected_payload_suppressed_case_count=36
expected_payload_body_free_case_count=36
```

Interpretation:

- `expected_payload_capable_case_count=6` means only the 6 valid cases are expected to represent payload-capable successful-path metadata.
- `expected_payload_not_applicable_case_count=30` means invalid cases are not expected to emit or require payload bodies.
- `expected_payload_availability_checked_case_count=6` is count-only and must not inspect payload content.
- `expected_payload_suppressed_case_count=36` means all selected cases must keep public output body-free.
- `expected_payload_body_free_case_count=36` means all selected cases must remain body-free on public surfaces.

These counts do not prove payload correctness or artifact body quality.

## 8. Expected Status Category Counts

The future audit should preserve the accepted status category separation from earlier chains.

Expected category counts:

```text
expected_pass_case_count=6
expected_fail_closed_case_count=26
expected_usage_error_case_count=3
expected_mismatch_case_count=1
```

Observed category counts should match the expected counts if a future implementation executes category checks:

```text
observed_pass_case_count=6
observed_fail_closed_case_count=26
observed_usage_error_case_count=3
observed_mismatch_case_count=1
```

Runner-level status must remain separate from per-case expected categories. A future runner-level `status=pass` would mean the metadata contract was satisfied, not that invalid cases individually passed.

## 9. Expected Body Suppression Counts

The future audit must require zero body emission on public surfaces.

Expected suppression counts:

```text
artifact_body_payload_emitted_case_count=0
generated_policy_body_emitted_case_count=0
manifest_body_emitted_case_count=0
forbidden_body_emitted_case_count=0
raw_stdout_body_suppressed_case_count=36
raw_stderr_body_suppressed_case_count=36
```

The future audit may count body-field metadata only when those counts cannot reconstruct body content:

```text
safe_metadata_body_field_count_min=not fixed in Step636
safe_metadata_body_field_count_max=not fixed in Step636
safe_metadata_body_field_count_unique_values=not fixed in Step636
```

Step636 intentionally does not fix exact body field count distribution because doing so should be based on future runner output that is confirmed body-free.

## 10. Expected Writer And Residue Counts

The future audit must keep manifest writer and file-writing boundaries closed.

Expected writer and residue counts:

```text
manifest_writer_invoked_case_count=0
file_writing_enabled_case_count=0
artifact_file_written_case_count=0
manifest_file_written_case_count=0
residue_file_count=0
```

If any of these values is non-zero, a future audit should fail closed.

## 11. Expected Safety Flags

Expected aggregate safety flags:

```text
content_suppressed=True
body_suppressed=True
metadata_only_checked=True
synthetic_only_checked=True
no_oracle_checked=True
payload_body_emitted=False
production_readiness_claimed=False
real_data_readiness_claimed=False
performance_claims_present=False
```

The future audit should treat missing or false safety flags as contract failures unless a later design explicitly defines a narrower staged check.

## 12. Proposed Future Aggregate Summary

A future runner or checker should emit only an aggregate summary like:

```text
mode=actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission
schema_version=learner_state_frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission_v0.1
status=pass
reason_code=none
matrix_name=actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission
case_selection=payload-audit-without-payload-emission
selected_case_count=36
selected_valid_case_count=6
selected_invalid_case_count=30
selected_fail_closed_invalid_case_count=26
selected_deferred_invalid_case_count=4
selected_usage_error_case_count=3
selected_mismatch_case_count=1
expected_payload_capable_case_count=6
expected_payload_not_applicable_case_count=30
expected_payload_availability_checked_case_count=6
expected_payload_suppressed_case_count=36
expected_payload_body_free_case_count=36
observed_payload_capable_case_count=6
observed_payload_not_applicable_case_count=30
observed_payload_availability_checked_case_count=6
observed_payload_suppressed_case_count=36
observed_payload_body_free_case_count=36
expected_pass_case_count=6
observed_pass_case_count=6
expected_fail_closed_case_count=26
observed_fail_closed_case_count=26
expected_usage_error_case_count=3
observed_usage_error_case_count=3
expected_mismatch_case_count=1
observed_mismatch_case_count=1
artifact_body_payload_emitted_case_count=0
generated_policy_body_emitted_case_count=0
manifest_body_emitted_case_count=0
forbidden_body_emitted_case_count=0
raw_stdout_body_suppressed_case_count=36
raw_stderr_body_suppressed_case_count=36
manifest_writer_invoked_case_count=0
file_writing_enabled_case_count=0
artifact_file_written_case_count=0
manifest_file_written_case_count=0
residue_file_count=0
content_suppressed=True
body_suppressed=True
metadata_only_checked=True
synthetic_only_checked=True
no_oracle_checked=True
payload_body_emitted=False
production_readiness_claimed=False
real_data_readiness_claimed=False
performance_claims_present=False
```

This summary is a future contract sketch. Step636 does not implement it and does not claim that current commands emit it.

## 13. Allowed Per-Case Metadata

If a future implementation needs per-case records, each record must be metadata-only and body-free.

Allowed per-case fields:

- case identifier by directory name
- expected category
- observed category
- payload-capable boolean
- payload-availability-checked boolean
- payload-suppressed boolean
- forbidden-body-emitted boolean
- manifest-writer-invoked boolean
- file-writing-enabled boolean
- residue-detected boolean

Forbidden per-case fields:

- fixture JSON body
- request body
- pointer body
- expected body
- artifact body payload
- generated policy body
- manifest body
- raw stdout body
- raw stderr body
- raw learner text
- raw rows
- logits/probabilities
- private paths
- absolute paths
- performance metric body

## 14. Selection Policy

The future audit should select by accepted metadata contracts:

- valid 6 cases from the all-valid multi-case matrix
- invalid 26 cases from the accepted fail_closed matrix
- deferred invalid 4 cases from the accepted usage_error / mismatch matrix

The future audit should not:

- discover new fixture categories dynamically without a contract update
- broaden into all-invalid behavior generally
- merge usage_error / mismatch semantics into fail_closed semantics
- inspect fixture JSON body to decide selection
- use payload body content for selection

## 15. Failure Mapping

Future runner-level failure mapping:

- `usage_error`: invalid CLI options, unsupported case selection, missing required fixture root argument, or incompatible audit configuration.
- `input_error`: fixture root cannot be read as metadata, accepted matrix contract is unavailable, or selected case count cannot be resolved without body inspection.
- `mismatch`: observed aggregate counts differ from the contract, or expected category counts do not match accepted matrices.
- `fail_closed`: forbidden body emission, manifest writer invocation, file-writing enablement, residue, or missing safety flags.

Per-case expected categories remain distinct from runner-level failure modes.

## 16. Relationship To Existing Boundaries

- Planned-only v0.3 remains not actual-controlled invocation.
- Actual-controlled v0.4 single-case smoke remains the primary controlled metadata-only invocation smoke.
- Actual-controlled v0.4 all-valid multi-case smoke remains the 6-case pass matrix.
- Actual-controlled v0.4 invalid fail_closed smoke remains the fixed 26-case fail_closed matrix.
- Actual-controlled v0.4 deferred usage_error / mismatch smoke remains the fixed 4-case expected-category matrix.
- Step636 combines their accepted counts only for a future payload audit contract.
- Step636 does not reopen or broaden any accepted boundary.
- Step636 does not replace any release-quality chain or remote status marker.

## 17. Relationship To Step635 Surface A And Surface C

Surface A maps to the future aggregate metadata summary:

- selected counts
- expected and observed category counts
- payload-capable counts
- payload suppression counts
- forbidden body emission counts
- writer / residue counts
- safety flags

Surface C maps to fixture-contract expected counts:

- 6 valid cases
- 26 fail_closed invalid cases
- 4 deferred invalid cases
- 36 selected cases total
- 6 payload-capable cases
- 30 no-payload-expected invalid cases

Step636 intentionally excludes any surface that would require payload body content, generated policy body content, manifest body content, or file-writing output.

## 18. Future Implementation Handoff

Recommended next design step:

```text
Step637: actual-controlled v0.4 artifact body payload audit without payload emission runner design
```

Step637 should design the future runner before implementation. It should:

- define how the future runner reads the count-only metadata contract
- define how it classifies selected cases
- define how it emits aggregate summary fields
- define usage_error / input_error / mismatch / fail_closed semantics
- avoid payload body emission
- avoid fixture JSON body copying
- avoid request / pointer / expected body copying
- avoid generated policy body output
- avoid manifest body output
- avoid manifest writer integration
- avoid file writing

If Step637 cannot preserve those constraints, the next step should be another design refinement instead of implementation.

## 19. Boundaries Explicitly Not Selected Now

Do not select now:

- payload audit implementation
- payload body emission
- artifact body payload output
- generated policy body output
- manifest body output
- payload correctness evaluation
- artifact body quality evaluation
- free-form body safety proof
- manifest writer integration
- manifest body generation
- file writing
- production file-writing path
- real-data readiness check
- model performance check

## 20. Non-Equivalence Cautions

- Contract design is not implementation.
- Aggregate metadata is not payload correctness evidence.
- Count-only body field metadata is not free-form body safety proof.
- Payload-capable counts are not artifact body quality evidence.
- Body suppression checks are not generated policy quality evidence.
- Combining accepted matrix counts does not prove runtime correctness generally.
- Release-quality success is not production readiness.
- Synthetic-only pass is not real-data readiness.
- No model performance follows from this boundary.
- Manifest writer validators remain separate.
- File-writing validators remain separate.

## 21. Non-Claims

- Production readiness is not claimed.
- Real-data readiness is not claimed.
- Model performance is not claimed.
- F1 / accuracy / ECE / AURCC achievement is not claimed.
- Runtime correctness generally is not claimed.
- All invalid-case runtime behavior is not claimed.
- Payload correctness is not claimed.
- Artifact body quality is not claimed.
- Free-form body safety is not claimed.
- Manifest writer correctness is not claimed.
- File-writing readiness is not claimed.
- Manifest body generation correctness is not claimed.
- Generated policy quality is not claimed.
- Learner-state estimator correctness is not claimed.

## 22. Public-Safe Checklist

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

## 23. Recommended Next Step

Recommended next step:

```text
Step637: actual-controlled v0.4 artifact body payload audit without payload emission runner design
```

Step637 should remain design-only / docs-only. It should not implement the runner, emit payload bodies, change fixture JSON, invoke manifest writer integration, or enable file writing.

## 24. Step637 Runner Design Reference

Step637 adds `docs/frozen_policy_generation_actual_controlled_v0_4_artifact_body_payload_audit_without_payload_emission_runner_design.md` as the design-only / docs-only runner design for the Step636 contract.

The Step637 design keeps payload audit runner implementation, payload body emission, artifact body payload output, generated policy body output, manifest body output, manifest writer integration, file writing, Python code/tests changes, Makefile changes, wrapper changes, workflow changes, fixture JSON changes, runtime implementation changes, and validator implementation changes out of scope.
