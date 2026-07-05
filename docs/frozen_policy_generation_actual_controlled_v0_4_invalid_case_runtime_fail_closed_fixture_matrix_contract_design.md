# Actual-Controlled v0.4 Invalid-Case Runtime Fail-Closed Fixture Matrix Contract Design

## 1. Title

Actual-Controlled v0.4 Invalid-Case Runtime Fail-Closed Fixture Matrix Contract Design

## 2. Scope

This document fixes the exact fixture/matrix contract for a future invalid-case runtime fail-closed smoke implementation.

This is design-only / docs-only. It does not runtime-execute invalid cases, change Python code/tests, change Makefile targets, change the release-quality wrapper, change workflows, change fixture JSON, change runtime implementation, implement manifest writer integration, or perform file writing.

This contract is not evidence of production readiness, real-data readiness, or model performance.

## 3. Prior Design Dependency

- Step611 accepted only the all-valid multi-case runtime smoke boundary.
- Step611 did not accept invalid-case runtime fail-closed behavior.
- Step612 recommended invalid-case runtime fail-closed matrix design.
- Step613 designed fail_closed-only invalid cases first.
- Step614 now fixes the exact fixture/matrix contract for the future runner.
- Step614 does not execute invalid cases.

## 4. Fixture Root And Aggregate Contract Source

- fixture root path: `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled/`
- total cases: 36
- valid cases: 6
- invalid cases: 30
- total JSON files: 252
- JSON files per case: 7
- validator aggregate: pass 6 / usage_error 3 / fail_closed 26 / mismatch 1
- content_suppressed: true
- body_suppressed: true
- metadata_only_checked: true
- synthetic_only_checked: true
- no_oracle_checked: true

This is public-safe aggregate metadata, not fixture JSON body.

## 5. Exact Selected Matrix

Matrix:

- matrix_name=actual_controlled_v0_4_invalid_fail_closed_runtime_smoke
- case_selection=fail-closed-invalid
- selected_case_count=26
- selected_invalid_case_count=26
- selected_valid_case_count=0
- expected_fail_closed_case_count=26
- deferred_case_count=4

Exact selected case matrix uses directory names / case IDs only:

| case_id | expected_status | expected_runtime_schema_version | expected_integration_mode | expected_runtime_fail_closed | expected_artifact_body_payload_emitted | expected_manifest_writer_invoked | expected_file_writing_enabled | expected_artifact_file_written | expected_manifest_file_written | expected_raw_stdout_body_suppressed | expected_raw_stderr_body_suppressed | expected_residue_file_count | body_content_allowed | runtime_execution_in_step614 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `invalid/invalid_absolute_path_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_artifact_body_cli_nonzero_exit` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_artifact_body_cli_output_not_body_free` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_artifact_body_payload_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_expected_body_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_file_writing_detected` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_file_writing_requested` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_generated_policy_body_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_logits_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_manifest_body_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_manifest_writer_invoked` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_manifest_writer_requested` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_no_oracle_forbidden_field` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_performance_metric_body_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_pointer_body_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_private_path_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_probabilities_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_raw_learner_text_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_raw_rows_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_raw_stderr_body_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_raw_stdout_body_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_real_data_marker_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_request_body_present` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_unexpected_artifact_body_generation_request` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_unsafe_artifact_body_runtime_mode` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |
| `invalid/invalid_unsafe_output_residue_risk` | fail_closed | learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4 | artifact-body-runtime-invocation-controlled | True | False | False | False | False | False | True | True | 0 | False | False |

## 6. Deferred Matrix

Deferred matrix:

- deferred_case_count=4
- deferred_usage_error_case_count=3
- deferred_mismatch_case_count=1

| case_id | expected_status_category | reason_for_deferral | future_boundary_candidate | runtime_execution_in_step614 |
| --- | --- | --- | --- | --- |
| `invalid/invalid_malformed_metadata_json` | usage_error | Metadata parsing / usage surface should be handled separately from fail_closed runtime behavior. | usage_error runtime matrix or validator-only contract | False |
| `invalid/invalid_missing_required_metadata_file` | usage_error | Missing metadata surface should be handled separately from fail_closed runtime behavior. | usage_error runtime matrix or validator-only contract | False |
| `invalid/invalid_unsupported_schema` | usage_error | Unsupported schema surface should be handled separately from fail_closed runtime behavior. | usage_error runtime matrix or validator-only contract | False |
| `invalid/invalid_mismatched_expected_status` | mismatch | Expected-status mismatch should be isolated from fail_closed matrix semantics. | mismatch runtime matrix or validator-only contract | False |

## 7. Selection Rules

- `--case-selection fail-closed-invalid` selects only the 26 selected invalid case IDs fixed in this contract.
- It does not dynamically select every invalid case.
- It excludes valid cases.
- It excludes deferred usage_error cases.
- It excludes deferred mismatch cases.
- It sorts selected case IDs lexicographically.
- It treats missing selected case ID as usage_error.
- It treats unexpected selected valid case as usage_error.
- It treats duplicate selected case ID as usage_error.
- It treats any selected case expected status other than fail_closed as mismatch or usage_error, depending on contract violation.
- It does not read fixture JSON body for output.
- It does not emit fixture JSON body.

## 8. Expected Future Runner Contract

Future runner candidate:

`python/learner_state/frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke.py`

Future focused tests candidate:

`python/learner_state/tests/test_frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke.py`

Future CLI:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled \
  --case-selection fail-closed-invalid \
  --summary-only \
  --no-file-writing \
  --no-manifest-writer \
  --fail-closed-on-unsafe-output
```

Required flags:

- `--fixture-root`
- `--case-selection fail-closed-invalid`
- `--summary-only`
- `--no-file-writing`
- `--no-manifest-writer`
- `--fail-closed-on-unsafe-output`

Unsupported / missing flags should map to usage_error.

## 9. Expected Aggregate Output Contract

Future aggregate output contract:

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
- unsafe_signal_total_count=<positive integer expected, exact value to be observed by Step615>
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

- `unsafe_signal_total_count` is expected to be positive for invalid fail-closed cases, unlike the all-valid matrix.
- Positive unsafe signals do not mean raw body emission.
- The pass condition is expected fail_closed behavior with body-free output and no residue.

## 10. Per-Case Summary Contract

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
- artifact_file_written
- manifest_file_written
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

## 11. Failure Mapping

### pass

Future invalid-case runtime fail-closed smoke should pass only if:

- selected_case_count=26
- executed_case_count=26
- observed_fail_closed_case_count=26
- pass_case_count=0
- usage_error_case_count=0
- mismatch_case_count=0
- input_error_case_count=0
- every selected case reaches expected fail_closed status
- no selected case emits raw body content
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

Future runner should return usage_error if:

- fixture root missing
- invalid directory missing
- selected case count does not equal 26
- any selected case directory missing
- valid case is accidentally selected
- deferred usage_error case is included
- duplicate case ID appears
- unsupported case-selection value is used
- required CLI safety flags are missing
- unknown fixture root layout is encountered
- selected case cannot be classified safely from contract

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

### mismatch

Future runner should return mismatch if:

- observed fail_closed count differs from 26
- any selected case does not fail_closed as expected
- expected schema/mode differs
- expected body suppression flags differ
- expected selected case IDs differ from contract
- deferred mismatch case is included in the fail_closed matrix
- aggregate counts disagree with per-case counts

## 12. Output Suppression And Residue Policy

Future implementation must:

- emit only aggregate public-safe metadata
- optionally emit per-case public-safe metadata
- never emit raw stdout/stderr body
- never emit fixture JSON body
- never emit request / pointer / expected body
- never emit artifact body payload
- never emit manifest body
- never emit generated policy body
- never emit raw rows / logits / probabilities
- never emit private / absolute path values
- never emit raw learner text
- never use real participant data
- never write files
- never invoke manifest writer
- use temp dirs only if needed
- clean temp dirs after each selected case
- aggregate residue_file_count
- fail closed on unexpected residue

## 13. Relationship To Step613 Design

- Step613 selected Option B at the design level.
- Step614 fixes the exact selected/deferred matrix contract.
- Step614 still does not implement runtime execution.
- Step614 does not prove invalid-case runtime fail-closed behavior.
- Step614 prepares Step615 implementation.

## 14. Relationship To All-Valid Multi-Case Smoke

- all-valid matrix selected 6 valid cases and expected pass
- invalid fail-closed matrix selects 26 invalid cases and expects fail_closed
- all-valid matrix expected unsafe_signal_total_count=0
- invalid matrix may observe positive unsafe_signal_total_count, but forbidden body emission must remain 0
- invalid fail-closed matrix does not replace all-valid matrix
- Step611 accepted all-valid release-quality chain remains valid as a separate boundary

## 15. Relationship To Fixture Validator

- existing actual-controlled fixture validator covers 36 cases at metadata/contract level
- fail_closed 26, usage_error 3, mismatch 1 are validator aggregate categories
- proposed future runner covers only selected fail_closed invalid cases at runtime level
- fixture validator remains broader and should not be replaced
- deferred usage_error / mismatch cases remain validator-covered until a separate runtime matrix is designed

## 16. Relationship To Payload / Manifest / File-Writing Boundaries

- this contract does not emit payloads
- this contract does not audit payload correctness
- this contract does not invoke manifest writer
- this contract does not enable file writing
- payload audit / manifest writer / file-writing boundaries remain separate
- no production readiness follows

## 17. Future Implementation Plan

Step615 should:

- implement dedicated invalid-case fail-closed runner
- implement focused tests
- not modify fixture JSON
- not modify Makefile
- not modify wrapper
- not modify workflow
- not invoke manifest writer
- not enable file writing
- use the exact 26 selected case IDs from Step614
- enforce deferred cases exclusion
- enforce body-free output
- enforce no residue
- preserve all-valid runner behavior
- preserve v0.4 single-case behavior

Do not implement Step615 in Step614.

## 18. Future Makefile Target Candidate

Future target:

`check-learner-state-frozen-policy-generation-actual-controlled-v0-4-invalid-case-runtime-fail-closed-smoke`

Future help text:

`Run actual-controlled v0.4 invalid-case runtime fail-closed smoke`

Do not implement it in Step614.

## 19. Future Release-Quality Staging

Recommended staging:

- Step615: invalid-case runtime fail-closed runner implementation
- Step616: Makefile target design
- Step617: Makefile target implementation
- Step618: release-quality integration design
- Step619: release-quality wrapper integration
- Step620: remote status marker
- Step621: final safety review

## 20. Boundaries Explicitly Not Selected Now

Do not select now:

- runtime execution in Step614
- all invalid cases in one broad runtime run
- usage_error runtime matrix
- mismatch runtime matrix
- payload audit implementation
- payload emission
- manifest writer integration
- file writing
- production file-writing paths
- real-data readiness checks
- model performance checks

## 21. Non-Equivalence Cautions

- contract design is not implementation
- contract design does not prove invalid-case fail-closed behavior
- directory-name inventory is not equivalent to fixture JSON validation
- validator aggregate is not runtime execution
- future runtime fail-closed pass would not prove runtime correctness generally
- future fail-closed matrix would not prove payload correctness
- future fail-closed matrix would not prove manifest writer correctness
- future fail-closed matrix would not prove file-writing safety
- future release-quality pass would not prove production readiness
- synthetic-only pass would not prove real-data readiness
- no model performance follows from this boundary

## 22. Non-Claims

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

## 23. Public-Safe Checklist

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

## 24. Recommended Next Step

Recommended next step:

- Step615: actual-controlled v0.4 invalid-case runtime fail-closed runner implementation

Step615 should implement runner and focused tests only. Step615 should not change fixture JSON, change Makefile, change the release-quality wrapper, change workflow, implement manifest writer integration, enable file writing, or claim invalid-case runtime fail-closed behavior beyond the focused smoke implementation result.

## 25. Step615 Implementation Status

Step615 implements `python/learner_state/frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke.py` and focused tests at `python/learner_state/tests/test_frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_smoke.py`.

The implemented direct CLI uses `--case-selection fail-closed-invalid`, selects the fixed 26 invalid fail_closed cases from this contract, defers the 4 non-fail_closed invalid cases, and emits aggregate public-safe metadata only. The canonical summary records 26 selected / executed / observed fail_closed cases, unsafe signal total 26, residue count 0, artifact body payload emitted count 0, manifest writer invocation count 0, and file-writing enabled count 0. Step615 does not add a Makefile target, release-quality wrapper integration, workflow changes, fixture JSON changes, manifest writer integration, or file writing. Step616 is expected to design the standalone Makefile target.

## 26. Step616 Makefile Target Design Status

Step616 adds `docs/frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_makefile_target_design.md` as a design-only / docs-only plan for the future standalone Makefile target. This contract remains unchanged; Step616 does not change Makefile, wrapper, workflow, Python code/tests, fixture JSON, manifest writer integration, or file writing.

## 27. Step617 Makefile Target Status

Step617 adds `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-invalid-case-runtime-fail-closed-smoke` as a standalone Makefile target for the Step615 runner. The target uses the fixed 26 selected invalid fail_closed cases and 4 deferred invalid cases from this contract, emits aggregate public-safe metadata only, and remains outside release-quality. This contract and fixture JSON remain unchanged; Step617 does not change Python code/tests, wrapper, workflow, manifest writer integration, or file writing.

## 28. Step618 Release-Quality Integration Design Reference

Step618 adds a design-only / docs-only release-quality integration plan for the Step617 standalone target. This contract and fixture JSON remain unchanged; Step618 does not change wrapper, Makefile, workflow, Python code/tests, manifest writer integration, or file writing.
