# Frozen Policy Generation Artifact Body Generation Integration Fixtures

This fixture root contains synthetic-only, metadata-only, no-oracle fixtures
for the future artifact body generation integration boundary.

The fixtures connect public-safe actual invocation runtime summary metadata to
artifact body generation boundary metadata. They do not implement artifact
body generation integration, do not implement a validator, do not invoke a
runtime, do not invoke a manifest writer, do not write artifact files, do not
write manifest files, do not compute metrics, and do not prove production or
real-data readiness.

## Purpose

The purpose is to define a future contract for static fixture validation of
the bridge between:

- actual invocation runtime summary metadata
- artifact body request metadata
- artifact body pointer metadata
- artifact body generation metadata
- expected public-safe integration summary metadata
- expected public-safe error metadata

All cases are body-free and use safe booleans, reason codes, count-like
metadata, schema names, mode labels, and relative fixture identifiers only.

## Synthetic-Only / Metadata-Only / No-Oracle Boundary

These fixtures must not contain real participant data, raw learner text, raw
rows, logits, probabilities, private path values, absolute path values,
request bodies, pointer bodies, expected bodies, generated policy bodies,
artifact body payloads, manifest bodies, raw stdout bodies, raw stderr
bodies, copied GitHub log blocks, full job output, or performance metric
bodies.

## Counts

- total_cases: 28
- valid_cases: 6
- invalid_cases: 22
- json_files_per_case: 7
- total_json_files: 196
- README: 1

## File Layout

Each case directory contains:

- `case_metadata.json`
- `actual_invocation_runtime_summary_metadata.json`
- `artifact_body_request_metadata.json`
- `artifact_body_pointer_metadata.json`
- `artifact_body_generation_metadata.json`
- `expected_integration_summary.json`
- `expected_error.json`

This README intentionally does not include fixture JSON bodies.

## Valid Taxonomy

- `valid/valid_minimal_suppressed_metadata_only_bridge`
- `valid/valid_safe_metadata_summary_bridge`
- `valid/valid_runtime_summary_to_suppressed_body_generation`
- `valid/valid_no_file_writing_bridge`
- `valid/valid_no_manifest_writer_bridge`
- `valid/valid_no_downstream_payload_bridge`

Valid cases expect `status=pass`, `reason_code=none`,
`exit_code_category=zero`, `invocation_mode=actual_invocation_metadata_only`,
suppressed content/body flags, suppressed raw stdout/stderr body flags, no
request / pointer / expected body detection, no artifact body payload
detection, no manifest body detection, no generated policy body detection, no
file writing detection, no manifest writer invocation, no production
readiness claim, no real-data readiness claim, and no performance claim.

## Invalid Taxonomy

- `invalid/invalid_runtime_summary_schema`
- `invalid/invalid_runtime_summary_status`
- `invalid/invalid_runtime_summary_body_detected`
- `invalid/invalid_runtime_summary_raw_stdout_body`
- `invalid/invalid_runtime_summary_raw_stderr_body`
- `invalid/invalid_artifact_body_payload_requested`
- `invalid/invalid_manifest_body_requested`
- `invalid/invalid_generated_policy_body_requested`
- `invalid/invalid_request_body_present`
- `invalid/invalid_pointer_body_present`
- `invalid/invalid_expected_body_present`
- `invalid/invalid_raw_rows_present`
- `invalid/invalid_logits_present`
- `invalid/invalid_private_path_present`
- `invalid/invalid_absolute_path_present`
- `invalid/invalid_raw_learner_text_present`
- `invalid/invalid_file_writing_requested`
- `invalid/invalid_manifest_writer_requested`
- `invalid/invalid_artifact_body_generation_unsafe_mode`
- `invalid/invalid_mismatched_expected_status`
- `invalid/invalid_real_data_marker_present`
- `invalid/invalid_performance_metric_body_present`

Invalid cases use metadata-only sentinels. The expected status split is:

- `invalid_runtime_summary_schema`: usage_error
- `invalid_mismatched_expected_status`: mismatch
- all other invalid cases: fail_closed

Reason codes are public-safe labels only.

## Schema Family

- `learner_state_frozen_policy_generation_artifact_body_generation_integration_case_v0.1`
- `learner_state_frozen_policy_generation_artifact_body_generation_integration_runtime_summary_metadata_v0.1`
- `learner_state_frozen_policy_generation_artifact_body_generation_integration_request_metadata_v0.1`
- `learner_state_frozen_policy_generation_artifact_body_generation_integration_pointer_metadata_v0.1`
- `learner_state_frozen_policy_generation_artifact_body_generation_integration_generation_metadata_v0.1`
- `learner_state_frozen_policy_generation_artifact_body_generation_integration_expected_summary_v0.1`
- `learner_state_frozen_policy_generation_artifact_body_generation_integration_expected_error_v0.1`

## Sentinel Policy

Invalid fixtures use safe sentinel booleans, reason codes, schema names, mode
labels, and count-like metadata. Actual unsafe payloads are never stored.

Valid cases must not contain forbidden sentinels. Invalid cases may contain
controlled metadata-only sentinel fields that indicate the simulated failure
class.

## Forbidden Payload Policy

This fixture root must not store:

- request bodies
- pointer bodies
- expected bodies
- written file JSON bodies
- manifest bodies
- artifact body payloads
- generated policy bodies
- raw stdout bodies
- raw stderr bodies
- raw rows
- logits or probabilities
- private path values
- absolute path values
- raw learner text
- real participant data
- performance metric bodies
- raw logs or full job output

## What Is Not Implemented

This fixture root does not implement fixture validation, runtime invocation,
artifact body generation integration, manifest writer integration, artifact
file writing, manifest file writing, release-quality integration, workflow
changes, or model evaluation.

## Future Validator Design

Step524 adds the future public-safe fixture validator design:

`docs/frozen_policy_generation_artifact_body_generation_integration_fixture_validator_design.md`

The design proposes a future validator module/CLI, validation schema,
aggregate counts, reason-code mapping, required-file validation, schema
validation, cross-file consistency checks, safety scan rules, CLI output
policy, focused tests, and release-quality staging. It does not implement a
validator, change Python code/tests, change Makefile, change the wrapper,
change workflow files, change fixture JSON, change runtime implementation,
implement artifact body generation integration, connect manifest writer
integration, enable file writing, use real data, compute metrics, or claim
production readiness.

## Validator Implementation

Step525 implements the static public-safe fixture validator module / CLI /
focused tests:

`python/learner_state/frozen_policy_generation_artifact_body_generation_integration_fixture_validation.py`

The validator checks this fixture root without invoking runtime code,
generating artifact bodies, invoking manifest writer code, writing files,
computing metrics, using real data, or claiming production readiness. It emits
aggregate metadata-only output and public-safe reason code counts only.

## Validator Makefile Target Design

Step526 adds the docs-only / planning-only standalone Makefile target design:

`docs/frozen_policy_generation_artifact_body_generation_integration_fixture_validator_makefile_target_design.md`

The design proposes a future target for running the Step525 validator CLI
against this fixture root. It does not change Makefile, the wrapper, workflow
files, Python code/tests, fixture JSON, runtime implementation, artifact body
generation integration, manifest writer integration, file writing, real-data
use, metric use, or production readiness claims.

## Validator Makefile Target

Step527 adds the standalone Makefile target:

`check-learner-state-frozen-policy-generation-artifact-body-generation-integration-fixtures`

The target runs the Step525 validator CLI against this fixture root and emits
public-safe aggregate counts and reason-code counts only. It does not add
release-quality wrapper integration, change workflow files, change Python
code/tests, change fixture JSON, change runtime implementation, implement
artifact body generation integration, connect manifest writer integration,
enable file writing, use real data, compute metrics, or claim production
readiness.

## Validator Release-Quality Integration Design

Step528 adds the docs-only / planning-only release-quality integration design:

`docs/frozen_policy_generation_artifact_body_generation_integration_fixture_validator_release_quality_integration_design.md`

The design proposes future wrapper inclusion for the Step527 standalone target
after actual invocation runtime smoke and before artifact body fixture
validation. It does not change the wrapper, workflow files, Makefile, Python
code/tests, fixture JSON, runtime implementation, artifact body generation
integration, manifest writer integration, file writing, real-data use, metric
use, or production readiness claims.

## Validator Release-Quality Wrapper Integration

Step529 adds the Step527 standalone target to the release-quality wrapper with
the artifact body generation integration fixture validation label. The check
still validates this synthetic metadata-only fixture root only. It does not
change workflow files, Makefile, Python code/tests, fixture JSON, runtime
implementation, artifact body generation integration, manifest writer
integration, file writing, real-data use, metric use, or production readiness
claims.

## Non-Claims

These fixtures do not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- artifact body generation integration correctness
- manifest writer integration correctness
- artifact writer CLI actual invocation correctness generally
- runtime actual invocation correctness generally
- generated policy quality
- learner-state estimator correctness
