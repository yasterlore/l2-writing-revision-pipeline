# Actual-Controlled v0.4 Multi-Case Runtime Smoke Fixture Matrix Contract Design

## Scope

This document is the fixture / matrix contract design for a future Step604 actual-controlled v0.4 multi-case runtime smoke implementation.

This is a design-only / docs-only step. It does not change Python code/tests, Makefile, release-quality wrapper, workflows, fixture JSON, runtime implementation, validator implementation, artifact body generation implementation, manifest writer integration, manifest body generation, generated policy body generation, artifact body file writing, or manifest file writing.

This contract does not provide production readiness, real-data readiness, or model performance evidence.

## Prior Design Dependency

This contract depends on:

- Step600 final safety review.
- Step601 next-boundary planning.
- Step602 multi-case runtime smoke design.

Step600 identified the primary-case limitation. Step601 recommended multi-case runtime smoke as the safest next boundary. Step602 recommended all-valid case selection and a dedicated future runner. Step603 now fixes the exact fixture/matrix contract for that future runner.

## Fixture Root Inventory

- fixture root path: `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled/`
- valid directory path: `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled/valid/`
- invalid directory path: `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled/invalid/`
- total case count: 36
- valid case count: 6
- invalid case count: 30
- total JSON file count: 252
- JSON files per case: 7

Valid case IDs found by directory name only:

- `valid/valid_actual_controlled_cli_output_body_free`
- `valid/valid_actual_controlled_no_file_writing`
- `valid/valid_actual_controlled_no_manifest_writer`
- `valid/valid_actual_controlled_no_residue`
- `valid/valid_actual_controlled_safe_metadata_invocation`
- `valid/valid_actual_controlled_stdout_stderr_suppressed`

Invalid cases are recorded count-only for this contract. They are not selected for the first multi-case runtime smoke.

No fixture JSON body, request body, pointer body, expected body, payload body, manifest body, generated policy body, raw stdout/stderr body, private / absolute path values, raw learner text, or real participant data is copied here.

## Matrix Purpose

The matrix defines which fixture cases future Step604 should execute through v0.4 runtime behavior. The first matrix is `all-valid`.

Invalid cases remain covered by the actual-controlled fixture validator target. Invalid runtime execution is deferred to a later separate boundary. The matrix is additive and does not replace the current single-case target.

## Matrix Selection

```text
matrix_name: actual_controlled_v0_4_all_valid_runtime_smoke
case_selection: all-valid
selected_valid_case_count: 6
selected_invalid_case_count: 0
expected_executed_case_count: 6
```

Selected valid case contract:

| case_id | expected_status | expected_reason_code | expected_runtime_schema_version | expected_integration_mode | expected_artifact_body_runtime_invoked | expected_artifact_body_runtime_mode | expected_manifest_writer_invoked | expected_file_writing_enabled | expected_artifact_body_payload_emitted | expected_runtime_safety_scan_passed | expected_unsafe_signal_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `valid/valid_actual_controlled_cli_output_body_free` | pass | none | `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4` | `artifact-body-runtime-invocation-controlled` | True | `controlled_metadata_only_invocation` | False | False | False | True | 0 |
| `valid/valid_actual_controlled_no_file_writing` | pass | none | `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4` | `artifact-body-runtime-invocation-controlled` | True | `controlled_metadata_only_invocation` | False | False | False | True | 0 |
| `valid/valid_actual_controlled_no_manifest_writer` | pass | none | `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4` | `artifact-body-runtime-invocation-controlled` | True | `controlled_metadata_only_invocation` | False | False | False | True | 0 |
| `valid/valid_actual_controlled_no_residue` | pass | none | `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4` | `artifact-body-runtime-invocation-controlled` | True | `controlled_metadata_only_invocation` | False | False | False | True | 0 |
| `valid/valid_actual_controlled_safe_metadata_invocation` | pass | none | `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4` | `artifact-body-runtime-invocation-controlled` | True | `controlled_metadata_only_invocation` | False | False | False | True | 0 |
| `valid/valid_actual_controlled_stdout_stderr_suppressed` | pass | none | `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4` | `artifact-body-runtime-invocation-controlled` | True | `controlled_metadata_only_invocation` | False | False | False | True | 0 |

No body fields are included in this matrix.

## Expected Aggregate Contract

Future runner aggregate output should include:

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
- `content_suppressed=True`
- `body_suppressed=True`
- `metadata_only_checked=True`
- `synthetic_only_checked=True`
- `no_oracle_checked=True`
- `production_readiness_claimed=False`
- `real_data_readiness_claimed=False`
- `performance_claims_present=False`

## Per-Case Summary Contract

Allowed per-case fields:

- case_id
- status
- reason_code
- runtime_schema_version
- integration_mode
- artifact_body_runtime_invoked
- artifact_body_runtime_mode
- artifact_body_generation_cli_invoked
- artifact_body_generation_cli_output_body_free
- safe_metadata_body_available
- safe_metadata_body_field_count
- manifest_writer_invoked
- file_writing_enabled
- artifact_body_payload_emitted
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

## Future Runner Contract

Future runner module:

- `python/learner_state/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke.py`

Future focused tests:

- `python/learner_state/tests/test_frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke.py`

Future CLI:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled \
  --case-selection all-valid \
  --summary-only \
  --no-file-writing \
  --no-manifest-writer \
  --fail-closed-on-unsafe-output
```

Future runner should:

- discover selected valid case IDs by directory names only
- execute each selected case through existing v0.4 controlled metadata-only runtime behavior
- capture raw stdout/stderr internally if subprocess is used
- emit only aggregate public-safe metadata
- optionally emit public-safe per-case lines
- not write files
- not invoke manifest writer
- not emit artifact body payload
- fail closed on unsafe output

## Discovery Rules

- `--case-selection all-valid` selects every directory under `valid/`.
- Case IDs are repository-relative under the fixture root, such as `valid/<case_dir_name>`.
- Selected cases must be sorted lexicographically for deterministic output.
- Duplicate case IDs map to usage_error.
- Zero valid cases maps to usage_error.
- Invalid cases are never selected by `all-valid`.

Recommended policy:

- Non-directory entries under `valid/` should map to usage_error if they would make discovery ambiguous.
- Hidden files should be ignored only if they are known tooling artifacts; otherwise usage_error is safer.

## Failure Mapping

### pass

- all selected valid cases pass
- all selected cases emit v0.4 schema
- all selected cases use controlled metadata-only invocation
- all selected cases suppress raw stdout/stderr bodies
- all selected cases have unsafe_signal_count=0
- no manifest writer invoked
- no file writing enabled
- no artifact body payload emitted
- no residue

### usage_error

- fixture root missing
- valid directory missing
- zero valid cases
- case count not equal to expected selected count when `all-valid` contract expects 6
- invalid case-selection value
- selected case missing required metadata
- duplicate case ID
- unexpected non-directory entry if chosen policy is usage_error
- unsupported schema / mode
- missing required CLI flags
- unexpected invalid case selected for all-valid mode

### fail_closed

- any selected case emits request body marker
- pointer body marker
- expected body marker
- artifact body payload marker
- manifest body marker
- generated policy body marker
- raw stdout/stderr body marker
- raw rows marker
- logits/probabilities marker
- private/absolute path marker
- raw learner text marker
- real data marker
- performance metric body marker
- file writing requested/detected
- manifest writer requested/invoked
- artifact body CLI nonzero or ambiguous
- unsafe output residue

### mismatch

- expected aggregate count mismatch
- expected per-case status mismatch
- expected schema/mode mismatch
- expected safety flag mismatch
- expected safe metadata count mismatch if the contract defines per-case expected counts

## Residue And Output Suppression Contract

Future implementation must:

- create no persistent output files
- use temporary directories only if needed
- clean temporary directories after each case
- aggregate residue_file_count
- fail closed if unexpected residue appears
- suppress raw stdout body
- suppress raw stderr body
- not write captured stdout/stderr into docs
- not write captured stdout/stderr into persistent files
- count only safe summary fields

## Compatibility Contract

Future implementation must preserve:

- v0.1 `plan-only-bridge`
- v0.2 `safe-metadata-smoke`
- v0.3 `artifact-body-runtime-invocation` planned-only mode
- v0.4 single-case `artifact-body-runtime-invocation-controlled`
- existing actual-controlled fixture validator target
- existing v0.4 single-case runtime target
- existing release-quality wrapper labels
- existing release-quality order

Multi-case smoke is additive.

## Expected Focused Tests For Step604

Future Step604 tests should include at least:

- discovers all 6 valid actual-controlled case IDs by directory name only
- discovered case IDs are sorted lexicographically
- invalid cases are not selected by all-valid
- no fixture JSON body is copied into output
- all-valid multi-case smoke passes
- selected_case_count=6
- selected_valid_case_count=6
- selected_invalid_case_count=0
- executed_case_count=6
- pass_case_count=6
- usage_error_case_count=0
- fail_closed_case_count=0
- mismatch_case_count=0
- artifact_body_generation_cli_invoked_case_count=6
- artifact_body_generation_cli_output_body_free_case_count=6
- artifact_body_payload_emitted_case_count=0
- manifest_writer_invoked_case_count=0
- file_writing_enabled_case_count=0
- raw_stdout_body_suppressed_case_count=6
- raw_stderr_body_suppressed_case_count=6
- unsafe_signal_total_count=0
- residue_file_count=0
- missing required flag maps to usage_error
- invalid case-selection maps to usage_error
- zero valid cases maps to usage_error
- duplicate case ID maps to usage_error
- unexpected invalid case selected maps to usage_error
- unsafe marker in one selected case maps aggregate to fail_closed
- artifact body CLI nonzero in one selected case maps aggregate to fail_closed
- residue in one selected case maps aggregate to fail_closed
- expected count mismatch maps to mismatch
- v0.4 single-case runtime target remains unchanged
- v0.3 planned-only target remains unchanged
- fixture JSON not mutated

Use temporary copies for mutation tests. Do not mutate canonical fixture JSON.

## Future Makefile Target Contract

Future target:

```text
check-learner-state-frozen-policy-generation-actual-controlled-v0-4-multi-case-runtime-smoke
```

Future help text:

```text
Run actual-controlled v0.4 multi-case runtime smoke
```

Future command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled --case-selection all-valid --summary-only --no-file-writing --no-manifest-writer --fail-closed-on-unsafe-output
```

Do not implement this target in Step603.

## Future Release-Quality Staging

Future staging should be:

- Step604: multi-case runtime smoke implementation
- Step605: multi-case runtime smoke Makefile target design
- Step606: multi-case runtime smoke Makefile target implementation
- Step607: multi-case runtime smoke release-quality integration design
- Step608: multi-case runtime smoke release-quality wrapper integration
- Step609: multi-case runtime smoke remote status marker
- Step610: multi-case runtime smoke final safety review

Do not integrate into release-quality before standalone target passes.

## Relationship To Invalid Cases

- Invalid cases remain covered by the actual-controlled fixture validator target.
- Invalid cases are not runtime-executed in the first multi-case smoke.
- Runtime execution of invalid cases should be a separate future fail-closed runtime matrix boundary.
- This avoids broadening unsafe output surfaces too early.

## Relationship To Current Single-Case Target

- Current single-case target remains unchanged.
- Multi-case target does not replace it.
- Single-case target remains fast primary smoke.
- Multi-case target adds broader valid-case coverage.
- Fixture validator remains responsible for invalid category coverage.

## Non-Equivalence Cautions

- Fixture/matrix contract design is not implementation.
- Future multi-case smoke will not prove runtime correctness generally.
- All-valid smoke will not prove invalid runtime fail-closed behavior.
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

- Step604: actual-controlled v0.4 multi-case runtime smoke implementation

Step604 should implement the dedicated runner and focused tests. Step604 should not modify Makefile, modify the release-quality wrapper, modify workflow, modify fixture JSON, invoke manifest writer, enable file writing, or use real data.

## Step604 Implementation Reference

Step604 adds `python/learner_state/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke.py` and focused tests for the all-valid 6-case runner described by this contract. The implementation remains direct CLI-only, emits aggregate public-safe metadata, and does not change Makefile, release-quality wrapper, workflow, fixture JSON, manifest writer integration, or file writing.

## Step605 Makefile Target Design Reference

Step605 adds `docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_makefile_target_design.md` as a design-only plan for a future standalone Makefile target around the Step604 runner. This matrix contract remains unchanged.

## Step606 Makefile Target Implementation Reference

Step606 adds the standalone Makefile target for the Step604 runner. This matrix contract remains unchanged; fixture JSON, Python code/tests, release-quality wrapper, manifest writer integration, and file writing remain unchanged.

## Step607 Release-Quality Integration Design Reference

Step607 designs future release-quality wrapper integration for the Step606 standalone multi-case target. This matrix contract remains unchanged; fixture JSON, Python code/tests, Makefile, wrapper, manifest writer integration, and file writing remain unchanged.

## Step608 Release-Quality Integration Reference

Step608 adds the Step606 standalone multi-case target to the release-quality wrapper. This matrix contract remains unchanged; fixture JSON, Python code/tests, Makefile, manifest writer integration, and file writing remain unchanged.

## Step609 Remote Run Record Workflow Reference

Step609 designs a future public-safe remote/manual run status marker for the Step608 wrapper-integrated multi-case check. This matrix contract remains unchanged; fixture JSON, Python code/tests, Makefile, wrapper, manifest writer integration, and file writing remain unchanged.

## Step610 Remote Status Marker Reference

Step610 adds the public-safe status marker for the Step608 wrapper-integrated multi-case check. This matrix contract remains unchanged; fixture JSON, Python code/tests, Makefile, wrapper, manifest writer integration, and file writing remain unchanged.

## Step611 Final Safety Review Reference

Step611 adds `docs/frozen_policy_generation_actual_controlled_v0_4_multi_case_runtime_smoke_release_quality_chain_final_safety_review.md` as a final-safety-review-only / docs-only review for the Step602-Step610 all-valid multi-case runtime smoke chain. This matrix contract remains unchanged; fixture JSON, Python code/tests, Makefile, wrapper, manifest writer integration, and file writing remain unchanged.

## Step612 Next Boundary Planning Reference

Step612 adds `docs/frozen_policy_generation_runtime_chain_post_multi_case_final_safety_review_next_boundary_planning.md` as a planning-only / docs-only comparison after the Step611 final safety review. This matrix contract remains unchanged; fixture JSON, Python code/tests, Makefile, wrapper, manifest writer integration, and file writing remain unchanged.

## Step613 Invalid-Case Matrix Design Reference

Step613 adds `docs/frozen_policy_generation_actual_controlled_v0_4_invalid_case_runtime_fail_closed_matrix_design.md` as a design-only / docs-only plan for a future invalid-case runtime fail-closed smoke. This all-valid matrix contract remains unchanged; Step613 does not execute invalid cases or change fixture JSON, Python code/tests, Makefile, wrapper, manifest writer integration, or file writing.
