# Artifact Body Generation Runtime Invocation Fixtures

Step570 creates this planned fixture root for a future artifact body generation
runtime invocation boundary. The root is separate from the active artifact body
generation integration fixture root and separate from the planned safe-metadata
v0.2 runtime integration fixture root.

This root is synthetic-only, metadata-only, body-free, count-only where
applicable, and no-oracle. It contains no request body, pointer body, expected
body, artifact body payload, manifest body, generated policy body, raw
stdout/stderr body, raw rows, logits/probabilities values, private or absolute
path values, raw learner text, real participant data, or performance metric
body.

Step570 creates fixture JSON and this README only. It does not implement a
validator, change runtime implementation, invoke artifact body generation
runtime, invoke manifest writer, change Makefile, change release-quality
wrapper, change workflows, or write artifact/manifest files.

## Layout

Each case uses seven metadata-only JSON files:

- `case_metadata.json`
- `safe_metadata_runtime_summary_metadata.json`
- `artifact_body_request_metadata.json`
- `artifact_body_pointer_metadata.json`
- `artifact_body_generation_invocation_metadata.json`
- `expected_runtime_invocation_summary.json`
- `expected_error.json`

## Case Taxonomy

Valid cases:

- `valid_minimal_safe_metadata_runtime_invocation`
- `valid_safe_metadata_count_only_runtime_invocation`
- `valid_invocation_no_manifest_writer`
- `valid_invocation_no_file_writing`
- `valid_invocation_body_payload_suppressed`
- `valid_invocation_artifact_body_available_count_only`

Invalid cases:

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
- `invalid_manifest_writer_requested`
- `invalid_unsafe_artifact_body_runtime_mode`
- `invalid_unsupported_schema`
- `invalid_mismatched_expected_status`
- `invalid_no_oracle_forbidden_field`
- `invalid_unsafe_output_residue_risk`
- `invalid_active_root_merge_attempted`

Aggregate:

- valid cases: 6
- invalid cases: 24
- total cases: 30
- JSON files per case: 7
- total JSON files: 210

## Schema and Mode Names

- fixture schema: `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_v0.1`
- validation schema: `learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation_v0.1`
- future runtime schema: `learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.3`
- proposed integration mode: `artifact-body-runtime-invocation`

## Validator Design Status

Step571 adds
`docs/frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validator_design.md`
as a design-only / docs-only future validator design for this planned root.
The validator is not implemented here, and this root is not yet connected to a
Makefile target, release-quality wrapper, workflow, runtime invocation,
manifest writer integration, or file-writing path.

Step572 implements the standalone validator module
`python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validation.py`
and focused tests. The validator checks this root as 30 cases / 210 JSON files
with public-safe metadata-only / body-free / count-only output. Step574 adds a
standalone Makefile target for the validator, while release-quality wrapper
integration, workflow changes, runtime invocation, manifest writer
integration, and file writing remain future work.

Step573 adds
`docs/frozen_policy_generation_artifact_body_generation_runtime_invocation_fixture_validator_makefile_target_design.md`
as a design-only / docs-only future standalone target design for the Step572
validator. The Makefile target was not added in Step573; Step574 adds it as a
separate implementation step.

Step574 adds the standalone Makefile target
`check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation-fixtures`.
It runs the Step572 validator over this planned root and keeps the aggregate at
30 cases / 210 JSON files with 6 pass, 1 usage-error, 22 fail-closed, and 1
mismatch case. The target is not yet release-quality integrated and does not
invoke artifact body generation runtime, invoke manifest writer, or write
files.

Step575 adds
`docs/frozen_policy_generation_artifact_body_generation_runtime_invocation_implementation_design.md`
as a design-only / docs-only implementation design for a future
`artifact-body-runtime-invocation` boundary. It recommends a refinement design
before runtime code changes and does not change this fixture root or fixture
JSON.

## Non-Claims

This planned root does not claim production readiness, real-data readiness,
model performance, F1 / accuracy / ECE / AURCC achievement, artifact body
generation correctness generally, runtime correctness generally, artifact body
payload correctness, manifest writer integration correctness, generated policy
quality, learner-state estimator correctness, or safe-metadata free-form body
safety.
