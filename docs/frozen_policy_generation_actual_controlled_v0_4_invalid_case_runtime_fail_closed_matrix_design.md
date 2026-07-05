# Actual-Controlled v0.4 Invalid-Case Runtime Fail-Closed Matrix Design

## 1. Title

Actual-Controlled v0.4 Invalid-Case Runtime Fail-Closed Matrix Design

## 2. Scope

This document is a design-only / docs-only matrix planning document for a future invalid-case runtime fail-closed smoke.

This step does not runtime-execute invalid cases, change Python code/tests, change Makefile targets, change the release-quality wrapper, change workflows, change fixture JSON, change runtime implementation, implement manifest writer integration, or perform file writing.

This design is not evidence of production readiness, real-data readiness, or model performance.

## 3. Prior Chain Dependency

- Step611 accepted the all-valid multi-case runtime smoke boundary only.
- Step611 did not accept invalid-case runtime fail-closed behavior.
- Step612 compared next boundaries.
- Step612 recommended invalid-case runtime fail-closed matrix design.
- Step613 now designs the matrix but does not execute invalid cases.

## 4. Starting Point

- fixture root path: `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled/`
- total cases: 36
- valid cases: 6
- invalid cases: 30
- total JSON files: 252
- JSON files per case: 7
- validator aggregate: pass 6 / usage_error 3 / fail_closed 26 / mismatch 1
- physical missing required file cases: 0
- physical malformed JSON cases: 0
- content_suppressed: true
- body_suppressed: true
- metadata_only_checked: true
- synthetic_only_checked: true
- no_oracle_checked: true

## 5. Invalid Case Inventory

This inventory records directory names / case IDs only. It does not copy fixture JSON body, request body, pointer body, expected body, artifact body payload, manifest body, generated policy body, raw stdout/stderr body, private / absolute path values, raw learner text, or real participant data.

| case_id | directory_name_only | inferred_reason_family | inferred_expected_status_category | selection_recommendation | rationale |
| --- | --- | --- | --- | --- | --- |
| `invalid/invalid_absolute_path_present` | true | absolute path exposure | fail_closed | selected | Directory name indicates unsafe path exposure surface; include in fail-closed matrix. |
| `invalid/invalid_artifact_body_cli_nonzero_exit` | true | artifact body CLI nonzero exit | fail_closed | selected | Directory name indicates runtime-side failure surface; include in fail-closed matrix. |
| `invalid/invalid_artifact_body_cli_output_not_body_free` | true | CLI output body-free violation | fail_closed | selected | Directory name indicates unsafe output surface; include in fail-closed matrix. |
| `invalid/invalid_artifact_body_payload_present` | true | artifact body payload present | fail_closed | selected | Directory name indicates forbidden payload surface; include in fail-closed matrix. |
| `invalid/invalid_expected_body_present` | true | expected body present | fail_closed | selected | Directory name indicates forbidden body surface; include in fail-closed matrix. |
| `invalid/invalid_file_writing_detected` | true | file writing detected | fail_closed | selected | Directory name indicates file-writing boundary violation; include in fail-closed matrix. |
| `invalid/invalid_file_writing_requested` | true | file writing requested | fail_closed | selected | Directory name indicates unsafe file-writing request surface; include in fail-closed matrix. |
| `invalid/invalid_generated_policy_body_present` | true | generated policy body present | fail_closed | selected | Directory name indicates forbidden generated policy body surface; include in fail-closed matrix. |
| `invalid/invalid_logits_present` | true | logits present | fail_closed | selected | Directory name indicates forbidden model-output surface; include in fail-closed matrix. |
| `invalid/invalid_malformed_metadata_json` | true | malformed metadata JSON | usage_error | deferred | Directory name indicates metadata parse / usage surface; defer to usage_error matrix. |
| `invalid/invalid_manifest_body_present` | true | manifest body present | fail_closed | selected | Directory name indicates forbidden manifest body surface; include in fail-closed matrix. |
| `invalid/invalid_manifest_writer_invoked` | true | manifest writer invoked | fail_closed | selected | Directory name indicates manifest writer boundary violation; include in fail-closed matrix. |
| `invalid/invalid_manifest_writer_requested` | true | manifest writer requested | fail_closed | selected | Directory name indicates unsafe manifest writer request surface; include in fail-closed matrix. |
| `invalid/invalid_mismatched_expected_status` | true | expected status mismatch | mismatch | deferred | Directory name indicates mismatch surface; defer to mismatch matrix. |
| `invalid/invalid_missing_required_metadata_file` | true | missing required metadata file | usage_error | deferred | Directory name indicates metadata presence / usage surface; defer to usage_error matrix. |
| `invalid/invalid_no_oracle_forbidden_field` | true | no-oracle forbidden field | fail_closed | selected | Directory name indicates no-oracle boundary violation; include in fail-closed matrix. |
| `invalid/invalid_performance_metric_body_present` | true | performance metric body present | fail_closed | selected | Directory name indicates forbidden metric body surface; include in fail-closed matrix. |
| `invalid/invalid_pointer_body_present` | true | pointer body present | fail_closed | selected | Directory name indicates forbidden pointer body surface; include in fail-closed matrix. |
| `invalid/invalid_private_path_present` | true | private path present | fail_closed | selected | Directory name indicates forbidden private path surface; include in fail-closed matrix. |
| `invalid/invalid_probabilities_present` | true | probabilities present | fail_closed | selected | Directory name indicates forbidden model-output surface; include in fail-closed matrix. |
| `invalid/invalid_raw_learner_text_present` | true | raw learner text present | fail_closed | selected | Directory name indicates forbidden learner text surface; include in fail-closed matrix. |
| `invalid/invalid_raw_rows_present` | true | raw rows present | fail_closed | selected | Directory name indicates forbidden raw rows surface; include in fail-closed matrix. |
| `invalid/invalid_raw_stderr_body_present` | true | raw stderr body present | fail_closed | selected | Directory name indicates forbidden stderr body surface; include in fail-closed matrix. |
| `invalid/invalid_raw_stdout_body_present` | true | raw stdout body present | fail_closed | selected | Directory name indicates forbidden stdout body surface; include in fail-closed matrix. |
| `invalid/invalid_real_data_marker_present` | true | real data marker present | fail_closed | selected | Directory name indicates forbidden real-data marker surface; include in fail-closed matrix. |
| `invalid/invalid_request_body_present` | true | request body present | fail_closed | selected | Directory name indicates forbidden request body surface; include in fail-closed matrix. |
| `invalid/invalid_unexpected_artifact_body_generation_request` | true | unexpected artifact body generation request | fail_closed | selected | Directory name indicates unexpected request surface; include in fail-closed matrix. |
| `invalid/invalid_unsafe_artifact_body_runtime_mode` | true | unsafe runtime mode | fail_closed | selected | Directory name indicates unsafe runtime mode surface; include in fail-closed matrix. |
| `invalid/invalid_unsafe_output_residue_risk` | true | unsafe output residue risk | fail_closed | selected | Directory name indicates residue risk surface; include in fail-closed matrix. |
| `invalid/invalid_unsupported_schema` | true | unsupported schema | usage_error | deferred | Directory name indicates schema / usage surface; defer to usage_error matrix. |

## 6. Runtime Matrix Selection Options

### Option A: All Invalid Cases In One Future Runtime Matrix

Summary:

- Include all 30 invalid cases in a future runtime matrix.

Pros:

- Widest invalid coverage.

Cons:

- Mixes usage_error / mismatch / fail_closed in one boundary.
- Broad unsafe output surface.
- Too broad for the first invalid runtime boundary.
- Failure interpretation becomes complex.

Recommendation:

- Not recommended for the first invalid runtime boundary.

### Option B: Fail-Closed-Only Invalid Cases First

Summary:

- Select invalid cases in the expected fail_closed family first.
- Defer usage_error / mismatch cases to separate boundaries.

Pros:

- Directly addresses the Step611 limitation.
- Focuses on runtime unsafe-surface detection.
- Keeps expected aggregate easier to interpret.
- Natural next boundary after the all-valid matrix.

Cons:

- usage_error / mismatch invalid categories are still not runtime-executed.
- Exact selected case count may need Step614 contract confirmation.

Recommendation:

- Recommended.

### Option C: Unsafe-Output-Surface Core Subset First

Summary:

- Select only the core unsafe output surface within fail_closed cases, such as request / pointer / expected / artifact payload / manifest body / raw stdout / raw stderr / private path / raw learner text / real data marker.

Pros:

- Smallest safer start.
- Easier to limit body leakage surface.

Cons:

- Less coverage gain than Option B.
- Leaves excluded fail_closed cases for a later boundary.

Recommendation:

- Acceptable fallback if Option B is too broad after Step614 contract work.

### Option D: Usage-Error-Only Runtime Matrix

Summary:

- Focus on missing metadata / malformed metadata / invalid selection usage_error surfaces.

Pros:

- Runtime execution surface is relatively small.

Cons:

- Does not directly answer the Step611 fail_closed limitation.
- Leaves fail_closed surface untested at runtime level.

Recommendation:

- Later boundary.

### Option E: Mismatch-Only Runtime Matrix

Summary:

- Handle expected status mismatch category separately.

Pros:

- Isolates mismatch interpretation.

Cons:

- Small case count.
- Does not directly answer the fail_closed limitation.

Recommendation:

- Later boundary.

## 7. Recommended Matrix

Recommended option:

- Option B: fail_closed-only invalid cases first

Matrix name:

`actual_controlled_v0_4_invalid_fail_closed_runtime_smoke`

Future schema name:

`learner_state_frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_matrix_v0.1`

Future runtime smoke schema name:

`learner_state_frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke_v0.1`

Future mode:

`actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke`

Future case selection:

`fail-closed-invalid`

Selection policy:

- select only invalid cases whose expected status category is fail_closed
- exclude valid cases
- defer usage_error cases
- defer mismatch cases
- defer cases requiring future public-safe contract verification
- sort selected case IDs lexicographically
- fail closed if an invalid selected case emits raw body content
- fail closed if a selected case emits artifact body payload
- fail closed if a selected case invokes manifest writer
- fail closed if a selected case enables file writing
- fail closed if residue appears

## 8. Proposed Selected Case Matrix

Proposed selected case matrix uses directory names only:

| case_id | expected_status | expected_runtime_schema_version | expected_integration_mode | expected_runtime_fail_closed | expected_runtime_safety_scan_passed | expected_artifact_body_payload_emitted | expected_manifest_writer_invoked | expected_file_writing_enabled | expected_raw_stdout_body_emitted | expected_raw_stderr_body_emitted | expected_residue_file_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `invalid/invalid_absolute_path_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_artifact_body_cli_nonzero_exit` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_artifact_body_cli_output_not_body_free` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_artifact_body_payload_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_expected_body_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_file_writing_detected` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_file_writing_requested` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_generated_policy_body_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_logits_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_manifest_body_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_manifest_writer_invoked` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_manifest_writer_requested` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_no_oracle_forbidden_field` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_performance_metric_body_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_pointer_body_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_private_path_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_probabilities_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_raw_learner_text_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_raw_rows_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_raw_stderr_body_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_raw_stdout_body_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_real_data_marker_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_request_body_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_unexpected_artifact_body_generation_request` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_unsafe_artifact_body_runtime_mode` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | False | 0 |
| `invalid/invalid_unsafe_output_residue_risk` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False or equivalent fail-closed semantics | False | False | False | False | 0 |

Expected selected fail_closed case count: 26, subject to Step614 confirmation from public-safe contract metadata.

## 9. Deferred Cases

Deferred cases:

- usage_error cases
- mismatch cases
- cases whose expected status cannot be safely inferred from directory names
- malformed / missing metadata cases until a separate usage_error runtime matrix or validator-only contract is designed

Deferred case IDs:

- `invalid/invalid_malformed_metadata_json`: usage_error
- `invalid/invalid_missing_required_metadata_file`: usage_error
- `invalid/invalid_unsupported_schema`: usage_error
- `invalid/invalid_mismatched_expected_status`: mismatch

## 10. Expected Aggregate Contract For Future Runtime Smoke

Future aggregate output should be public-safe and count-only:

- mode=actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke
- schema_version=learner_state_frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke_v0.1
- status=pass
- reason_code=none
- matrix_name=actual_controlled_v0_4_invalid_fail_closed_runtime_smoke
- case_selection=fail-closed-invalid
- selected_case_count=<to be fixed by Step614>
- selected_invalid_case_count=<to be fixed by Step614>
- selected_valid_case_count=0
- executed_case_count=<to be fixed by Step614>
- pass_case_count=0
- expected_fail_closed_case_count=<to be fixed by Step614>
- observed_fail_closed_case_count=<to be fixed by Step614>
- usage_error_case_count=0 for the recommended first fail-closed matrix
- mismatch_case_count=0 for the recommended first fail-closed matrix
- input_error_case_count=0
- runtime_schema_version=learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4
- integration_mode=artifact-body-runtime-invocation-controlled
- all_selected_cases_failed_closed=True
- artifact_body_payload_emitted_case_count=0
- manifest_writer_invoked_case_count=0
- file_writing_enabled_case_count=0
- artifact_file_written_case_count=0
- manifest_file_written_case_count=0
- raw_stdout_body_suppressed_case_count=<to be fixed by Step614>
- raw_stderr_body_suppressed_case_count=<to be fixed by Step614>
- unsafe_signal_total_count=>0 is expected for invalid fail-closed cases, but body emission must remain 0
- residue_file_count=0
- content_suppressed=True
- body_suppressed=True
- metadata_only_checked=True
- synthetic_only_checked=True
- no_oracle_checked=True
- production_readiness_claimed=False
- real_data_readiness_claimed=False
- performance_claims_present=False

For invalid cases, unsafe_signal_total_count may be positive unlike the all-valid matrix. A positive unsafe signal count is not payload/body emission.

## 11. Per-Case Summary Contract

Allowed per-case fields:

- case_id
- status
- reason_code
- expected_status
- runtime_schema_version
- integration_mode
- runtime_fail_closed
- artifact_body_runtime_invoked
- artifact_body_runtime_mode
- artifact_body_generation_cli_invoked
- artifact_body_generation_cli_output_body_free
- artifact_body_payload_emitted
- manifest_writer_invoked
- file_writing_enabled
- raw_stdout_body_suppressed
- raw_stderr_body_suppressed
- runtime_safety_scan_passed
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

## 12. Failure Interpretation

### pass

Future invalid-case runtime fail-closed matrix should pass only if:

- every selected case reaches expected fail_closed status
- no selected case emits raw body content
- no selected case emits artifact body payload
- no selected case emits manifest body
- no selected case emits generated policy body
- no selected case emits raw stdout/stderr body
- no selected case invokes manifest writer
- no selected case enables file writing
- no selected case leaves residue
- aggregate output is public-safe and count-only

### usage_error

Future runner should return usage_error if:

- fixture root missing
- invalid directory missing
- selected invalid case count does not match contract
- selected case cannot be classified safely
- usage_error case is accidentally included in fail-closed matrix
- valid case is accidentally included
- duplicate case ID appears
- unsupported case-selection value is used
- required CLI safety flags are missing

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
- residue appears
- unsafe output scan itself fails closed

### mismatch

Future runner should return mismatch if:

- expected fail_closed count differs from observed fail_closed count
- expected schema/mode differs
- expected body suppression flags differ
- expected selected case IDs differ from contract
- expected status category differs from contract

## 13. Output Suppression And Residue Policy

Future implementation must:

- emit only aggregate public-safe metadata
- optionally emit per-case public-safe metadata
- never emit raw stdout/stderr body
- never emit fixture JSON body
- never emit request / pointer / expected body
- never emit artifact body payload
- never emit manifest body
- never emit generated policy body
- never write files
- never invoke manifest writer
- use temp dirs only if needed
- clean temp dirs after each selected case
- aggregate residue_file_count
- fail closed on unexpected residue

## 14. Relationship To All-Valid Multi-Case Matrix

- all-valid matrix selected 6 valid cases and expected pass
- invalid fail-closed matrix will select invalid cases and expect fail_closed
- all-valid matrix unsafe_signal_total_count expected 0
- invalid fail-closed matrix unsafe_signal_total_count may be positive, but forbidden body emission must remain 0
- invalid fail-closed matrix does not replace all-valid matrix
- all-valid release-quality chain remains accepted by Step611

## 15. Relationship To Fixture Validator

- existing fixture validator already covers 36 cases at metadata/contract level
- proposed runtime fail-closed matrix would add runtime-level fail-closed smoke for selected invalid cases
- fixture validator remains the broader invalid coverage source
- runtime matrix should not replace fixture validator
- malformed/missing metadata cases may remain validator-only or become a separate usage_error runtime matrix later

## 16. Relationship To Payload / Manifest / File-Writing Boundaries

- this design does not emit payloads
- this design does not audit payload correctness
- this design does not invoke manifest writer
- this design does not enable file writing
- payload audit / manifest writer / file-writing boundaries remain separate
- no production readiness follows

## 17. Future Implementation Options

### Option A: Extend Existing Multi-Case Runner

Pros:

- reuses all-valid runner discovery / aggregation logic
- less new code

Cons:

- risk of mixing pass-matrix and fail-closed-matrix semantics

### Option B: Dedicated Invalid-Case Fail-Closed Runner

Pros:

- clearer semantics
- simpler safety review
- easier release-quality label naming

Cons:

- more code

Recommendation:

- Recommend dedicated future runner unless inspection in Step614 shows extension is cleaner without mixing semantics.

Future runner candidate:

`python/learner_state/frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke.py`

Future focused tests candidate:

`python/learner_state/tests/test_frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke.py`

Do not implement them in Step613.

## 18. Future CLI Design

Future CLI candidate:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled \
  --case-selection fail-closed-invalid \
  --summary-only \
  --no-file-writing \
  --no-manifest-writer \
  --fail-closed-on-unsafe-output
```

Do not implement it in Step613.

## 19. Future Makefile Target Design

Future target candidate:

`check-learner-state-frozen-policy-generation-actual-controlled-v0-4-invalid-case-runtime-fail-closed-smoke`

Future help text candidate:

`Run actual-controlled v0.4 invalid-case runtime fail-closed smoke`

Do not implement it in Step613.

## 20. Future Release-Quality Staging

Cautious future chain:

- Step614: invalid-case runtime fail-closed fixture/matrix contract design
- Step615: invalid-case runtime fail-closed runner implementation
- Step616: Makefile target design
- Step617: Makefile target implementation
- Step618: release-quality integration design
- Step619: release-quality wrapper integration
- Step620: remote status marker
- Step621: final safety review

Recommended next step is Step614 fixture/matrix contract design, because Step613 proposes a 26-case fail_closed matrix from directory names and validator aggregate, but Step614 should fix the contract before implementation. If Step614 confirms the exact matrix is already sufficiently fixed, a later implementation refinement design may replace an extra contract step.

## 21. Boundaries Explicitly Not Selected Now

Do not select now:

- invalid-case runtime execution implementation
- all invalid cases in one broad runtime run
- payload audit implementation
- payload emission
- manifest writer integration
- file writing
- production file-writing paths
- real-data readiness checks
- model performance checks

## 22. Non-Equivalence Cautions

- matrix design is not implementation
- matrix design does not prove invalid-case fail-closed behavior
- directory-name inventory is not equivalent to fixture JSON validation
- validator aggregate is not runtime execution
- future runtime fail-closed pass would not prove runtime correctness generally
- future fail-closed matrix would not prove payload correctness
- future fail-closed matrix would not prove manifest writer correctness
- future fail-closed matrix would not prove file-writing safety
- future release-quality pass would not prove production readiness
- synthetic-only pass would not prove real-data readiness
- no model performance follows from this boundary

## 23. Non-Claims

- production readiness is not claimed.
- real-data readiness is not claimed.
- model performance is not claimed.
- F1 / accuracy / ECE / AURCC achievement is not claimed.
- artifact body generation integration correctness is not claimed.
- artifact body generation runtime correctness generally is not claimed.
- invalid-case runtime fail-closed behavior is not claimed.
- manifest writer integration correctness is not claimed.
- manifest writer file-writing production readiness is not claimed.
- artifact body payload correctness is not claimed.
- safe-metadata free-form body safety is not claimed.
- manifest body generation correctness is not claimed.
- generated policy quality is not claimed.
- learner-state estimator correctness is not claimed.
- artifact writer CLI actual invocation correctness generally is not claimed.
- runtime actual invocation correctness generally is not claimed.

## 24. Public-Safe Checklist

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

## 25. Recommended Next Step

Recommended next step:

- Step614: actual-controlled v0.4 invalid-case runtime fail-closed fixture/matrix contract design

Step614 should remain design-only / docs-only unless Step613 clearly fixed the exact selected matrix. Step614 should not execute invalid cases, change Python code/tests, change fixture JSON, change Makefile, change the release-quality wrapper, change workflow, implement manifest writer integration, or enable file writing.

## Step614 Fixture Matrix Contract Reference

Step614 adds `docs/frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_fixture_matrix_contract_design.md` as the design-only / docs-only contract fixing the exact selected/deferred matrix for the future runner. This matrix design remains unchanged; Step614 does not execute invalid cases, change Python code/tests, change fixture JSON, change Makefile, change wrapper, change workflow, invoke manifest writer, or enable file writing.

## Step615 Implementation Status Reference

Step615 implements the direct CLI-only invalid-case fail-closed runner after the Step614 contract. The runner selects the fixed 26 invalid fail_closed cases, defers the 4 non-fail_closed invalid cases, emits aggregate public-safe metadata only, and keeps Makefile, release-quality wrapper, workflow, fixture JSON, manifest writer integration, and file writing unchanged. This reference does not expand the Step613 design claims or claim runtime correctness generally.
