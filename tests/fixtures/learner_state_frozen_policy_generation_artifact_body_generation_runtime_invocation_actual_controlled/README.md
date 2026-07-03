# Actual-Controlled Artifact Body Generation Runtime Invocation Fixtures

Step587 creates this future actual-controlled artifact body generation runtime
invocation fixture root from the Step586 fixture/schema contract design.

This root is separate from the Step570 planned-only runtime invocation fixture
root. It is also separate from artifact body generation safe-metadata fixtures
and manifest writer fixtures.

This root is synthetic-only, metadata-only, body-free, count-only where
applicable, and no-oracle. It contains no request body, pointer body, expected
body, written file JSON body, manifest body, artifact body payload, generated
policy body, raw stdout/stderr body, raw rows, logits/probabilities values,
private or absolute path values, raw learner text, real participant data, or
performance metric body.

Step587 creates fixture JSON and this README only. It does not implement a
validator, change runtime implementation, invoke artifact body generation
runtime, invoke manifest writer, change Makefile, change release-quality
wrapper, change workflows, or write artifact/manifest files.

## Layout

Each case uses seven metadata-only JSON files:

- `case_metadata.json`
- `artifact_body_runtime_request_metadata.json`
- `artifact_body_runtime_pointer_metadata.json`
- `artifact_body_generation_cli_metadata.json`
- `expected_runtime_invocation_summary.json`
- `residue_policy_metadata.json`
- `expected_error.json`

All JSON files are parseable in this root. The cases
`invalid_missing_required_metadata_file` and `invalid_malformed_metadata_json`
use metadata-only markers and expected reason codes instead of physical missing
files or malformed JSON. Mutation tests can exercise physical missing/malformed
conditions later using temporary copies.

## Schemas And Modes

- fixture schema: `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled_fixture_v0.1`
- validation schema: `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled_fixture_validation_v0.1`
- future runtime schema: `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4`
- integration mode: `artifact-body-runtime-invocation-controlled`
- optional future command flag: `--actual-invocation`

The v0.3 `artifact-body-runtime-invocation` boundary remains planned-only. This
root is for a future v0.4 actual-controlled metadata-only invocation chain.

## Case Counts

- valid cases: 6
- invalid cases: 30
- total cases: 36
- JSON files per case: 7
- total JSON files: 252
- README files in root: 1

## Valid Cases

- `valid_actual_controlled_safe_metadata_invocation`
- `valid_actual_controlled_cli_output_body_free`
- `valid_actual_controlled_no_file_writing`
- `valid_actual_controlled_no_manifest_writer`
- `valid_actual_controlled_stdout_stderr_suppressed`
- `valid_actual_controlled_no_residue`

All valid cases expect status `pass`, reason `none`, runtime invoked true,
invocation planned false, controlled metadata-only runtime mode, CLI invoked
true, no manifest writer, no file writing, no residue, and unsafe signal count
0.

## Invalid Cases

- `invalid_unsupported_schema`
- `invalid_missing_required_metadata_file`
- `invalid_malformed_metadata_json`
- `invalid_mismatched_expected_status`
- `invalid_request_body_present`
- `invalid_pointer_body_present`
- `invalid_expected_body_present`
- `invalid_artifact_body_payload_present`
- `invalid_manifest_body_present`
- `invalid_generated_policy_body_present`
- `invalid_raw_stdout_body_present`
- `invalid_raw_stderr_body_present`
- `invalid_raw_rows_present`
- `invalid_logits_present`
- `invalid_probabilities_present`
- `invalid_private_path_present`
- `invalid_absolute_path_present`
- `invalid_raw_learner_text_present`
- `invalid_real_data_marker_present`
- `invalid_performance_metric_body_present`
- `invalid_file_writing_requested`
- `invalid_file_writing_detected`
- `invalid_manifest_writer_requested`
- `invalid_manifest_writer_invoked`
- `invalid_unsafe_artifact_body_runtime_mode`
- `invalid_no_oracle_forbidden_field`
- `invalid_unsafe_output_residue_risk`
- `invalid_artifact_body_cli_nonzero_exit`
- `invalid_artifact_body_cli_output_not_body_free`
- `invalid_unexpected_artifact_body_generation_request`

Expected status / reason mapping:

- usage_error: `invalid_unsupported_schema`, `invalid_missing_required_metadata_file`, `invalid_malformed_metadata_json`
- mismatch: `invalid_mismatched_expected_status`
- fail_closed: all other invalid cases

## Expected Aggregate For Future Validator

- mode: `artifact_body_generation_runtime_invocation_actual_controlled_fixture_validation`
- validation_schema_version: `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled_fixture_validation_v0.1`
- fixture_root: `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled`
- total_cases: 36
- valid_cases: 6
- invalid_cases: 30
- total_json_files: 252
- json_files_per_case: 7
- matched_cases: 36
- mismatched_cases: 0
- input_error_cases: 0
- pass_cases: 6
- usage_error_cases: 3
- fail_closed_cases: 26
- mismatch_cases: 1
- expected_missing_required_metadata_file_cases: 1
- expected_malformed_metadata_json_cases: 1
- content_suppressed: true
- body_suppressed: true
- metadata_only_checked: true
- synthetic_only_checked: true
- no_oracle_checked: true
- no_request_body: true
- no_pointer_body: true
- no_expected_body: true
- no_artifact_body_payload: true
- no_manifest_body: true
- no_generated_policy_body: true
- no_raw_stdout_body: true
- no_raw_stderr_body: true
- no_raw_rows: true
- no_logits_dump: true
- no_probabilities_dump: true
- no_private_paths: true
- no_absolute_paths: true
- no_raw_learner_text: true
- no_real_participant_data: true
- no_performance_metric_body: true
- file_writing_checked: true
- manifest_writer_integration_checked: true
- actual_controlled_runtime_invocation_checked: true
- production_readiness_claimed: false
- real_data_readiness_claimed: false
- performance_claims_present: false

Reason-code counts must remain count-only and body-free.

## Safety Boundary

This root is public-safe fixture metadata only. It uses marker booleans and
count-only fields for unsafe cases. It does not include raw payload values,
stdout/stderr bodies, row bodies, paths, learner text, participant data, or
performance metric bodies.

## Not Implemented Or Claimed

This root is not a validator implementation, not a runtime implementation, not
actual runtime correctness evidence, not artifact body payload correctness
evidence, not production readiness, not real-data readiness, and not model
performance evidence.

## Next Expected Step

Step588 fixture validator design is recorded in
`docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validator_design.md`.

Recommended next step after Step588:

- Step589: actual-controlled fixture validator implementation

Do not proceed directly to runtime implementation from this fixture root.


## Step589 Validator Implementation

Step589 adds the standalone validator module `python/learner_state/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validation.py` and focused tests at `python/learner_state/tests/test_frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validation.py`.

Direct CLI:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled
```

Expected direct aggregate remains 36 cases, 6 valid cases, 30 invalid cases, 252 JSON files, 6 pass cases, 3 usage-error cases, 26 fail-closed cases, and 1 mismatch case. The validator is standalone only; Makefile target design is expected in Step590. Runtime invocation, manifest writer integration, file writing, release-quality wrapper integration, workflow changes, and fixture JSON changes remain out of scope.


## Step590 Makefile Target Design

Step590 adds `docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_fixture_validator_makefile_target_design.md` as a design-only plan for a future standalone Makefile target around the Step589 validator. The proposed target is `check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation-fixtures`. Step590 does not implement the target, change fixture JSON, invoke runtime code, invoke manifest writer code, or write files.
