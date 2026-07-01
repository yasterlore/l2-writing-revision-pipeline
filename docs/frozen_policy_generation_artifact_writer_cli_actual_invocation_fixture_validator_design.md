# Frozen Policy Generation Artifact Writer CLI Actual Invocation Fixture Validator Design

## 1. Title

Frozen Policy Generation Artifact Writer CLI Actual Invocation Fixture Validator
Design.

## 2. Scope

This document is the Step499 design-only / planning-only document for a future
validator that statically validates the Step498 artifact writer CLI actual
invocation fixture root.

This document does not implement a validator, change Python code/tests, change
Makefile targets, change the release-quality wrapper, change workflows, change
fixture JSON, implement runtime actual invocation, implement artifact writer CLI
actual invocation, connect artifact body generation integration, connect
manifest writer integration, or enable file writing.

This document is not evidence for production readiness, real-data readiness,
model performance, F1, accuracy, ECE, AURCC, artifact writer CLI actual
invocation correctness, artifact body generation integration correctness,
manifest writer integration correctness, generated policy quality, or
learner-state estimator correctness.

## 3. Prior Completed Chain

- Step496 created the design-only artifact writer CLI actual invocation
  boundary.
- Step497 created the design-only fixture contract for future actual invocation
  fixture validation.
- Step498 created the synthetic metadata-only fixture root with 32 cases and
  192 JSON files.

Step498 is fixture root creation only. It does not implement a validator, does
not implement actual invocation, and does not prove artifact writer CLI actual
invocation correctness.

## 4. Target Fixture Root

Target fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation/`

Expected counts:

- `total_cases`: 32
- `valid_cases`: 6
- `invalid_cases`: 26
- `json_files_per_case`: 6
- `total_json_files`: 192
- `README`: 1

Required files per case:

- `case_metadata.json`
- `runtime_request_metadata.json`
- `runtime_pointer_metadata.json`
- `artifact_writer_cli_invocation_metadata.json`
- `expected_invocation_summary.json`
- `expected_error.json`

## 5. Proposed Validator Module / CLI

Future module candidate:

`python/learner_state/frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation.py`

Future CLI candidate:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation
```

Step499 does not create this module or CLI.

## 6. Validator Responsibilities

The future validator should perform static fixture validation only:

- fixture root discovery
- README presence check
- case directory discovery
- expected case count check
- valid / invalid count check
- JSON files per case check
- total JSON file count check
- required file presence check
- JSON parse check
- schema version consistency check
- case ID consistency across files
- duplicate case ID detection
- expected status / reason-code consistency
- expected exit-code category consistency
- valid / invalid taxonomy check
- required field presence check
- unknown or unsupported schema version check
- body-bearing forbidden key scan
- body-bearing forbidden value scan
- no-oracle forbidden field scan
- synthetic-only / metadata-only flag consistency
- suppression flag consistency
- path safety check
- private / absolute path sentinel check
- raw stdout / stderr sentinel check
- artifact body / manifest body / generated policy body sentinel check
- downstream invocation boundary check
- file-writing disabled/default check
- residue expectation check
- expected summary field matching
- deterministic traversal / sorted output
- root error handling
- input error handling

The validator must not invoke the artifact writer CLI and must not create output
artifacts.

## 7. Validation Schema / Result Schema

Future validation schema version candidate:

`learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation_v0.1`

Future result fields should include:

- `mode`
- `validation_schema_version`
- `fixture_root`
- `total_cases`
- `valid_cases`
- `invalid_cases`
- `total_json_files`
- `json_files_per_case`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `pass_cases`
- `usage_error_cases`
- `fail_closed_cases`
- `duplicate_case_id_cases`
- `missing_required_file_cases`
- `content_suppressed`
- `body_suppressed`
- `no_raw_rows`
- `no_logits_dump`
- `no_private_paths`
- `no_absolute_paths`
- `no_generated_policy_body`
- `no_artifact_body_payload`
- `no_manifest_body`
- `no_request_body`
- `no_pointer_body`
- `no_expected_body`
- `no_raw_stdout_body`
- `no_raw_stderr_body`
- `no_oracle_checked`
- `synthetic_only_checked`
- `metadata_only_checked`
- `file_writing_checked`
- `artifact_writer_cli_actual_invocation_fixture_checked`
- `artifact_body_generation_integration_checked`
- `manifest_writer_integration_checked`
- `production_readiness_claimed`
- `real_data_readiness_claimed`
- `performance_claims_present`
- `reason_code_counts`
- `root_errors`

The result must be JSON serializable, public-safe, body-free, and summary-only.
Step499 does not implement this schema.

## 8. Expected Aggregate Counts

For the Step498 fixture root, the future validator should expect:

- `total_cases=32`
- `valid_cases=6`
- `invalid_cases=26`
- `total_json_files=192`
- `json_files_per_case=6`
- `matched_cases=32`
- `mismatched_cases=0`
- `input_error_cases=0`
- `pass_cases=6`

Expected non-pass category counts:

- `usage_error_cases=3`
- `fail_closed_cases=22`
- `mismatch_cases=1`

The usage-error cases are:

- `invalid_missing_required_metadata_file`
- `invalid_duplicate_case_id`
- `invalid_unsupported_artifact_writer_schema`

The mismatch case is:

- `invalid_mismatched_expected_status`

The fail-closed cases cover forbidden payload sentinels, no-oracle sentinels,
path-safety sentinels, unsafe invocation output sentinels, downstream
invocation boundary violations, and file-writing requested.

## 9. Status / Reason Code Mapping

Status categories:

- `pass`
- `usage_error`
- `fail_closed`
- `input_error`
- `mismatch`

Reason code families:

- `none`
- `request_body_present`
- `pointer_body_present`
- `expected_body_present`
- `artifact_body_payload_present`
- `manifest_body_present`
- `generated_policy_body_present`
- `raw_learner_text_present`
- `raw_rows_present`
- `logits_present`
- `probabilities_present`
- `private_path_present`
- `absolute_path_present`
- `final_text_present`
- `observed_after_text_present`
- `gold_label_present`
- `post_hoc_annotation_present`
- `raw_stdout_body_present`
- `raw_stderr_body_present`
- `file_writing_requested`
- `artifact_body_generation_invoked`
- `manifest_writer_invoked`
- `unsupported_artifact_writer_schema`
- `unsafe_actual_invocation_output`
- `mismatched_expected_status`
- `missing_required_metadata_file`
- `duplicate_case_id`
- `unsupported_schema_version`
- `malformed_json`
- `root_error`

The future validator should compare expected status, expected reason code, and
expected exit-code category across case metadata, expected summary metadata, and
expected error metadata.

## 10. Forbidden Key / String Scan Design

The future validator should scan metadata keys and string values for forbidden
body-bearing terms:

- `request_body`
- `pointer_body`
- `expected_body`
- `written_file_json_body`
- `manifest_body`
- `artifact_body_payload`
- `generated_policy_body`
- `raw_stdout_body`
- `raw_stderr_body`
- `raw_learner_text`
- `raw_rows`
- `logits`
- `probabilities`
- `final_text`
- `observed_after_text`
- `gold_label`
- `gold_labels`
- `post_hoc_annotation`
- `post_hoc_annotations`
- `scoring_feedback_payload`
- `private_path`
- `absolute_path`
- `real_participant_data`
- `real_data_marker`

Controlled sentinel names may appear only in expected invalid cases. Actual
body values must never appear.

## 11. Sentinel Validation Policy

Invalid cases may use controlled sentinels. The future validator should enforce:

- sentinel field names may appear only in expected invalid cases
- sentinel field values must be body-free
- actual prohibited body values must not appear
- private / absolute path cases must not include actual path strings
- raw stdout / stderr cases must not include raw output bodies
- raw learner text / raw rows / logits cases must not include raw content
- artifact body / manifest body / generated policy body cases must not include
  actual body payloads
- valid cases must not contain forbidden sentinel fields

Sentinels are metadata-only indicators, not payload examples.

## 12. Path Safety Validation Design

The future validator should enforce path safety:

- only relative repo / fixture paths are allowed
- no absolute path values
- no home path markers
- no cloud/private path markers
- no parent traversal
- no hidden private directory markers
- no platform-specific private prefixes
- pointer metadata must not contain path body content
- path sentinels are allowed only in expected invalid cases and without actual
  path values

The validator should report path failures through public-safe reason codes only.

## 13. File-Writing And Residue Validation Design

The future validator should enforce a no-writing validation boundary:

- validator itself must not write output artifacts
- fixture validation must not perform actual invocation
- `file_writing_enabled` / `file_writing_requested` flags must be false in valid
  cases
- file-writing requested invalid case must be fail-closed
- `residue_expected` must be false in valid cases
- validator result must report residue expectation only as metadata
- no temp output root should be created by fixture validation
- any future runtime file-writing behavior must be a separate chain

## 14. Downstream Invocation Boundary Validation

The future validator should confirm:

- artifact writer CLI actual invocation fixture validation does not invoke the
  artifact writer CLI
- artifact body generation must not be invoked
- manifest writer must not be invoked
- file writing must not be invoked
- artifact body generation invoked sentinel is invalid
- manifest writer invoked sentinel is invalid
- actual invocation output unsafe sentinel is invalid

This is a fixture validator boundary, not runtime integration.

## 15. CLI Output Boundary

Future CLI output may include:

- aggregate counts
- matched / mismatched counts
- status category counts
- `reason_code_counts`
- suppression flags
- safety flags
- `root_errors` as safe reason codes

Future CLI output must not include:

- fixture JSON body
- request body
- pointer body
- expected body
- raw stdout/stderr body
- artifact body payload
- manifest body
- generated policy body
- raw rows
- logits / probabilities
- raw learner text
- private / absolute path values

## 16. Proposed Focused Tests For Future Implementation

Future Step500 tests should cover:

- valid root summary matches 32 cases / 192 JSON files
- all valid cases pass
- all invalid cases match expected status / reason code
- duplicate case ID detected
- missing required metadata file detected
- mismatched expected status detected
- unsupported schema detected
- forbidden body sentinel fail-closed
- no-oracle sentinel fail-closed
- private / absolute path sentinel fail-closed
- raw stdout / stderr sentinel fail-closed
- downstream invocation boundary sentinel fail-closed
- valid cases contain no forbidden sentinels
- validator output contains no fixture bodies
- validator output contains no private / absolute path values
- deterministic sorted traversal
- malformed JSON returns input_error safely
- root not found returns input_error safely

## 17. Relationship To Step497 / Step498

- Step497: fixture contract design
- Step498: fixture root creation
- Step499: fixture validator design

Step499 is not validator implementation. It is the design for a future
validator that will check the Step498 fixture root.

Step500 implements the static validator module / CLI / focused tests described
by this design:

- `python/learner_state/frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation.py`

The implementation validates the Step498 fixture root at summary level with
the validation schema
`learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation_v0.1`.
It does not update runtime actual invocation, perform artifact writer CLI
actual invocation, add a Makefile target, change the release-quality wrapper,
change workflows, change fixture JSON, connect artifact body generation
integration, connect manifest writer integration, enable file writing, use
real data, compute metrics, or claim production readiness.

Step501 adds the design-only / planning-only Makefile target design for running
this validator CLI from a future standalone target:

[Frozen policy generation artifact writer CLI actual invocation fixture validator Makefile target design](frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validator_makefile_target_design.md)

Step501 does not change Makefile, implement the target, change release-quality,
change workflow files, change Python code/tests, change fixture JSON, update
runtime actual invocation, perform artifact writer CLI actual invocation, or
enable file writing.

Step502 implements the standalone Makefile target for this validator:

`check-learner-state-frozen-policy-generation-artifact-writer-cli-actual-invocation-fixtures`

Step502 does not change release-quality, change workflow files, change Python
code/tests, change fixture JSON, update runtime actual invocation, perform
artifact writer CLI actual invocation, or enable file writing.

Step503 adds the docs-only release-quality integration design for that
standalone target:
[Frozen policy generation artifact writer CLI actual invocation fixture validator release-quality integration design](frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validator_release_quality_integration_design.md).
Step503 does not change the release-quality wrapper, workflow files, Makefile,
Python code/tests, fixture JSON, runtime actual invocation, artifact writer CLI
actual invocation, or file writing.

Step504 adds the standalone target to the release-quality wrapper as:

`release_quality_check: learner-state frozen policy generation artifact writer CLI actual invocation fixture validation`

Step504 does not change workflow files, Makefile, Python code/tests, fixture
JSON, runtime actual invocation, artifact writer CLI actual invocation, or file
writing.

Step505 adds the docs-only remote/manual run record workflow design:
[Frozen policy generation artifact writer CLI actual invocation fixture validator release-quality remote run record workflow](frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validator_release_quality_remote_run_record_workflow.md).
Step505 does not create a status marker or change workflow files, wrapper,
Makefile, Python code/tests, fixture JSON, runtime actual invocation, artifact
writer CLI actual invocation, or file writing.

Step506 adds the public-safe remote status marker:
[Learner-state frozen policy generation artifact writer CLI actual invocation fixture validator release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validator_release_quality_remote_run_status.md).
Step506 does not change workflow files, wrapper, Makefile, Python code/tests,
fixture JSON, runtime actual invocation, artifact writer CLI actual invocation,
or file writing.

Step507 adds the docs-only runtime update design:
[Frozen policy generation artifact writer CLI actual invocation runtime update design](frozen_policy_generation_artifact_writer_cli_actual_invocation_runtime_update_design.md).
Step507 does not change workflow files, wrapper, Makefile, Python code/tests,
fixture JSON, runtime actual invocation, artifact writer CLI actual invocation,
or file writing.

## 18. Planned Follow-Up Steps

Possible follow-up steps:

1. Step508: runtime actual invocation fixture update design, if needed
2. Step509: runtime actual invocation implementation update

Step507 does not start these follow-up steps.

## 19. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1, accuracy, ECE, or AURCC achievement
- artifact writer CLI actual invocation correctness
- artifact body generation integration correctness
- manifest writer integration correctness
- generated policy quality
- learner-state estimator correctness
- validator implementation
- actual invocation implementation

## 20. Public-Safe Checklist

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

## 21. Step508 Runtime Fixture Update Design Status

Step508 adds the docs-only / planning-only fixture update design for adapting
the existing artifact writer CLI integration runtime fixture root to a future
`actual_invocation_metadata_only` mode:

[Frozen policy generation artifact writer CLI actual invocation runtime fixture update design](frozen_policy_generation_artifact_writer_cli_actual_invocation_runtime_fixture_update_design.md)

Step508 does not change the Step498 actual invocation fixture JSON, change the
existing runtime fixture JSON, update validators, change Python code/tests,
change Makefile, change the release-quality wrapper, change workflow files,
implement runtime actual invocation, perform artifact writer CLI actual
invocation, connect artifact body generation integration, connect manifest
writer integration, enable file writing, use real data, compute metrics, or
claim production readiness.
