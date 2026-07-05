# Actual-Controlled v0.4 Deferred Invalid-Case Runtime usage_error / mismatch Fixture Matrix Contract Design

## 1. Title

Actual-Controlled v0.4 Deferred Invalid-Case Runtime usage_error / mismatch Fixture Matrix Contract Design.

## 2. Scope

This document is a design-only / docs-only fixture and matrix contract for a future actual-controlled v0.4 deferred invalid-case runtime usage_error / mismatch smoke runner.

This Step625 scope is limited to contract design:

- no runtime execution
- no Python code/tests changes
- no Makefile changes
- no release-quality wrapper changes
- no workflow changes
- no fixture JSON changes
- no runtime implementation changes
- no validator implementation changes
- no payload audit implementation
- no manifest writer integration
- no file writing
- no production readiness proof
- no real-data readiness proof
- no model performance proof

## 3. Prior Design Dependency

Step622 accepted only the fixed 26 selected invalid fail_closed runtime smoke boundary. That accepted boundary was release-quality-integrated and remote-status-recorded, but it did not accept all invalid-case runtime behavior.

Step622 left 4 deferred non-fail_closed invalid cases outside the fail_closed matrix:

- `invalid/invalid_malformed_metadata_json`
- `invalid/invalid_missing_required_metadata_file`
- `invalid/invalid_unsupported_schema`
- `invalid/invalid_mismatched_expected_status`

Step623 recommended deferred usage_error / mismatch invalid runtime matrix design as the next small boundary. Step624 recommended the combined deferred invalid status matrix for those 4 cases.

Step625 fixes the fixture/matrix contract for that future runner. Step625 does not execute the deferred cases.

## 4. Fixture Root and Source of Contract

Fixture root:

```text
tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled/
```

Public-safe prior aggregate:

- total_cases=36
- valid_cases=6
- invalid_cases=30
- fail_closed_cases=26
- usage_error_cases=3
- mismatch_cases=1
- selected fail_closed cases accepted by Step622=26
- deferred non-fail_closed cases=4

This contract uses directory names and prior public-safe metadata only. It does not copy fixture JSON body. It does not copy request / pointer / expected body. It does not inspect JSON bodies.

## 5. Exact Selected Matrix

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

Future matrix schema:

```text
learner_state_frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_matrix_v0.1
```

Future runtime smoke schema:

```text
learner_state_frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke_v0.1
```

Exact selected cases:

| case_id | expected_status_category | reason_family | selected | runtime_execution_policy |
| --- | --- | --- | --- | --- |
| `invalid/invalid_malformed_metadata_json` | usage_error | malformed metadata JSON | yes | preflight / safe parse handling |
| `invalid/invalid_missing_required_metadata_file` | usage_error | missing required metadata file | yes | preflight / safe file presence handling |
| `invalid/invalid_unsupported_schema` | usage_error | unsupported schema | yes | preflight / safe schema handling |
| `invalid/invalid_mismatched_expected_status` | mismatch | mismatched expected status | yes | safe contract comparison / runtime summary if safe |

Counts:

- selected_case_count=4
- selected_invalid_case_count=4
- selected_valid_case_count=0
- selected_usage_error_case_count=3
- selected_mismatch_case_count=1
- excluded_fail_closed_case_count=26
- excluded_valid_case_count=6

## 6. Explicitly Excluded Cases

- all 26 fail_closed invalid cases are excluded from this matrix.
- all 6 valid cases are excluded from this matrix.
- the fail_closed 26-case boundary remains accepted separately by Step622.
- this matrix must not reopen or merge the fail_closed 26 cases.

## 7. Primary Count Policy

Recommended contract:

- Use `processed_case_count=4` as the primary count.
- Do not require all cases to be counted as `executed_case_count`, because malformed / missing metadata cases may stop at safe preflight.
- Include optional diagnostic counts:
  - `preflight_usage_error_case_count=3`
  - `runtime_or_contract_mismatch_case_count=1`
  - `runtime_attempted_case_count` may be recorded as an implementation-observed count in Step626, but should not be a pass condition unless Step626 safely fixes it.
- Future Step626 may include `executed_case_count` only if semantics are clearly defined and safe.

Rationale:

- malformed metadata JSON and missing required metadata file should not require full runtime invocation.
- usage_error may be an expected per-case category, not a runner failure.
- `processed_case_count` avoids overstating runtime execution.

## 8. Expected Aggregate Output Contract

The future runner should emit aggregate public-safe metadata only. Expected aggregate fields include:

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

`status=pass` means the future runner observed the expected per-case usage_error / mismatch categories. It does not mean individual invalid cases passed. Per-case usage_error is expected and distinct from runner-level usage_error. Per-case mismatch is expected and distinct from runner-level mismatch when the aggregate matches the contract. `processed_case_count=4` is the primary count for this matrix.

## 9. Per-Case Contract

### invalid/invalid_malformed_metadata_json

- expected_status=usage_error
- expected_reason_family=malformed metadata JSON
- preflight_checked=True
- runtime_full_invocation_required=False
- artifact_body_payload_emitted=False
- manifest_writer_invoked=False
- file_writing_enabled=False
- forbidden_body_emitted=False
- residue_file_count=0

### invalid/invalid_missing_required_metadata_file

- expected_status=usage_error
- expected_reason_family=missing required metadata file
- preflight_checked=True
- runtime_full_invocation_required=False
- artifact_body_payload_emitted=False
- manifest_writer_invoked=False
- file_writing_enabled=False
- forbidden_body_emitted=False
- residue_file_count=0

### invalid/invalid_unsupported_schema

- expected_status=usage_error
- expected_reason_family=unsupported schema
- preflight_checked=True
- runtime_full_invocation_required=False
- artifact_body_payload_emitted=False
- manifest_writer_invoked=False
- file_writing_enabled=False
- forbidden_body_emitted=False
- residue_file_count=0

### invalid/invalid_mismatched_expected_status

- expected_status=mismatch
- expected_reason_family=mismatched expected status
- preflight_checked=True
- runtime_full_invocation_required=implementation_defined_in_step626
- artifact_body_payload_emitted=False
- manifest_writer_invoked=False
- file_writing_enabled=False
- forbidden_body_emitted=False
- residue_file_count=0

## 10. Allowed Per-Case Summary Fields

Allowed per-case fields:

- case_id
- expected_status
- observed_status
- reason_code
- reason_family
- runtime_schema_version
- integration_mode
- preflight_checked
- runtime_attempted
- runtime_full_invocation_required
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

## 11. Runner-Level vs Per-Case Status Semantics

- runner-level `status=pass` means all selected deferred invalid cases matched their expected categories.
- per-case `usage_error` is expected for 3 cases.
- per-case `mismatch` is expected for 1 case.
- runner-level `usage_error` means runner misuse, contract violation, missing fixture root, unsafe CLI flags, or unsafe selection.
- runner-level `mismatch` means observed per-case categories did not match the contract.
- runner-level `fail_closed` means forbidden body emission, payload leak, manifest writer invocation, file writing, raw stdout/stderr body emission, private/absolute path emission, raw learner text, real data marker, or residue.
- The future runner must not collapse expected per-case usage_error into runner-level failure.

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

## 13. Failure Mapping

### pass

Future runner should pass only if:

- selected_case_count=4
- selected_invalid_case_count=4
- selected_valid_case_count=0
- selected_usage_error_case_count=3
- selected_mismatch_case_count=1
- processed_case_count=4
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

## 14. Future Runner Implementation Handoff

Preferred future implementation approach:

- dedicated future runner module
- optionally shared helper functions with existing fail_closed runner
- separate CLI mode and schema from the fail_closed 26-case runner
- no semantic mixing with fail_closed matrix

Future runner candidate:

```text
python/learner_state/frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke.py
```

Future tests candidate:

```text
python/learner_state/tests/test_frozen_policy_generation_actual_controlled_v0_4_deferred_invalid_case_runtime_usage_error_mismatch_smoke.py
```

Do not implement them in Step625. Step626 should implement them.

## 15. Future CLI Contract

Future CLI:

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

Unsupported / missing flags should map to runner-level usage_error.

Do not implement in Step625.

## 16. Relationship to Accepted fail_closed Matrix

- Step622 accepted the fixed 26 selected fail_closed invalid cases.
- Step625 does not reopen or replace the accepted fail_closed matrix.
- Step625 fixes the contract for the 4 deferred non-fail_closed invalid cases.
- The future deferred matrix should be complementary to the fail_closed matrix.
- A future deferred matrix pass would not prove fail_closed matrix behavior.
- A future deferred matrix pass would not prove all invalid-case behavior generally beyond the selected 4.

## 17. Relationship to Fixture Validator

- Existing actual-controlled fixture validator covers all 36 cases at metadata/contract level.
- The 4 deferred cases are already contract-classified as usage_error or mismatch.
- Step625 fixes runtime/preflight-level handling contract for those deferred cases.
- The future runner must not replace the fixture validator.
- Fixture validator remains broader coverage.

## 18. Relationship to Payload / Manifest / File-Writing Boundaries

- This contract does not emit payloads.
- This contract does not audit payload correctness.
- This contract does not invoke manifest writer.
- This contract does not enable file writing.
- Payload audit / manifest writer / file-writing boundaries remain separate.
- No production readiness follows.

## 19. Future Chain Proposal

- Step626: deferred invalid-case usage_error / mismatch runner implementation
- Step627: Makefile target design
- Step628: Makefile target implementation
- Step629: release-quality integration design
- Step630: wrapper integration
- Step631: remote status marker
- Step632: final safety review

## 20. Boundaries Explicitly Not Selected Now

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

## 21. Non-Equivalence Cautions

- contract design is not implementation.
- future deferred matrix pass would not prove runtime correctness generally.
- future deferred matrix pass would not prove all invalid-case behavior generally.
- future deferred matrix pass would not prove payload correctness.
- metadata-only planning is not free-form body safety proof.
- fixture validator coverage is not equivalent to runtime/preflight matrix coverage.
- release-quality success is not production readiness.
- synthetic-only pass is not real-data readiness.
- no model performance follows from this contract.

## 22. Non-Claims

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

## 23. Public-Safe Checklist

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

## 24. Recommended Next Step

Recommended next step:

- Step626: deferred invalid-case usage_error / mismatch runner implementation

Step626 should implement runner and focused tests only. Step626 should not change Makefile. Step626 should not change release-quality wrapper. Step626 should not change workflow. Step626 should not change fixture JSON. Step626 should not implement payload audit. Step626 should not invoke manifest writer. Step626 should not enable file writing. Step626 should update root README and full technical specification related docs because it is an implementation Step.
