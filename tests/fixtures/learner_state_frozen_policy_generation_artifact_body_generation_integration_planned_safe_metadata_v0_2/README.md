# Planned Safe-Metadata v0.2 Artifact Body Generation Runtime Integration Fixtures

Step547 adds these planned safe-metadata v0.2 fixture cases outside the active
artifact body generation integration fixture root so the existing static
validator and release-quality wrapper remain unchanged until a later validator
update step.

Placement:

- planned root: `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration_planned_safe_metadata_v0_2/`
- active validator root remains: `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_integration/`

The planned root preserves the seven-file case layout:

- `case_metadata.json`
- `actual_invocation_runtime_summary_metadata.json`
- `artifact_body_request_metadata.json`
- `artifact_body_pointer_metadata.json`
- `artifact_body_generation_metadata.json`
- `expected_integration_summary.json`
- `expected_error.json`

Planned valid cases:

- `valid_safe_metadata_explicit_runtime_bridge`
- `valid_safe_metadata_count_only_bridge`
- `valid_safe_metadata_no_file_writing_bridge`
- `valid_safe_metadata_no_manifest_writer_bridge`

Planned invalid cases:

- `invalid_safe_metadata_artifact_body_payload_present`
- `invalid_safe_metadata_manifest_body_present`
- `invalid_safe_metadata_generated_policy_body_present`
- `invalid_safe_metadata_request_body_present`
- `invalid_safe_metadata_pointer_body_present`
- `invalid_safe_metadata_expected_body_present`
- `invalid_safe_metadata_raw_stdout_body_present`
- `invalid_safe_metadata_raw_stderr_body_present`
- `invalid_safe_metadata_raw_rows_present`
- `invalid_safe_metadata_logits_present`
- `invalid_safe_metadata_private_path_present`
- `invalid_safe_metadata_absolute_path_present`
- `invalid_safe_metadata_raw_learner_text_present`
- `invalid_safe_metadata_real_data_marker_present`
- `invalid_safe_metadata_performance_metric_body_present`
- `invalid_safe_metadata_file_writing_requested`
- `invalid_safe_metadata_manifest_writer_requested`
- `invalid_safe_metadata_unsafe_output_surface`
- `invalid_safe_metadata_mismatched_expected_status`
- `invalid_safe_metadata_unsupported_schema`

Safety boundary:

- synthetic-only
- metadata-only
- body-free
- no-oracle
- no artifact body payload
- no manifest body
- no generated policy body
- no raw stdout/stderr body
- no raw rows
- no logits/probabilities dump
- no private or absolute path values
- no raw learner text
- no real participant data
- no performance metric body
- no file writing
- no manifest writer integration

Validator update is not yet implemented. Runtime implementation is not yet
implemented. Release-quality wrapper integration is unchanged. These planned
fixtures do not claim production readiness, real-data readiness, model
performance, artifact body generation correctness generally, runtime
correctness generally, manifest writer integration correctness, generated
policy quality, learner-state estimator correctness, or safe-metadata
free-form body safety.

Step548 adds the design-only / planning-only validator update design for this
planned root:

`docs/frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_v0_2_fixture_validator_update_design.md`

The design recommends a separate future validator module. It does not change
these fixture JSON files, implement validation, implement runtime behavior,
add Makefile or release-quality wrapper integration, invoke artifact body
generation runtime, invoke manifest writer integration, or write files.

Step549 implements that separate validator module and focused tests:

`python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation.py`

`python/learner_state/tests/test_frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_fixture_validation.py`

The validator checks this planned root as 24 cases / 168 JSON files with
public-safe aggregate output. Makefile and release-quality integration remain
future work, and runtime implementation remains unimplemented.

Step550 adds the design-only / planning-only Makefile target design for the
validator CLI:

`docs/frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_v0_2_fixture_validator_makefile_target_design.md`

No Makefile target or release-quality integration is implemented in Step550.

Step551 adds the standalone Makefile target:

`check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-fixtures`

The target runs the planned-root validator CLI and keeps the expected
public-safe aggregate at 24 cases / 168 JSON files, with 4 pass, 1 usage-error,
18 fail-closed, and 1 mismatch case. Release-quality integration remains
future work, and runtime implementation remains unimplemented.

Step552 adds the design-only / planning-only release-quality integration
design for this target:

`docs/frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_v0_2_fixture_validator_release_quality_integration_design.md`

No release-quality wrapper change is implemented in Step552.

Step553 adds the planned-root validator target to the release-quality wrapper
after plan-only bridge smoke and before artifact body fixture validation.
Runtime implementation remains unimplemented.

## Step554 Remote Run Record Workflow Design Status

Step554 adds the docs-only public-safe remote/manual run record workflow design
for the Step553 wrapper check:

`docs/frozen_policy_generation_artifact_body_generation_runtime_integration_safe_metadata_v0_2_fixture_validator_release_quality_remote_run_record_workflow.md`

It proposes future metadata-only/body-free status marker fields for this
planned root but does not create the marker, change fixture JSON, change
validators, change runtime implementation, invoke artifact body generation
runtime, invoke manifest writer, or write files.
