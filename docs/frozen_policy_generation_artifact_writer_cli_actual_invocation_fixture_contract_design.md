# Frozen Policy Generation Artifact Writer CLI Actual Invocation Fixture Contract Design

## 1. Title

Frozen Policy Generation Artifact Writer CLI Actual Invocation Fixture Contract
Design.

## 2. Scope

This document is the Step497 design-only / planning-only contract design for a
future artifact writer CLI actual invocation fixture root.

This document does not create a fixture root, create fixture JSON, implement a
validator, update the runtime implementation, implement actual invocation,
change Python code/tests, change Makefile targets, change the release-quality
wrapper, change workflows, connect artifact body generation, connect manifest
writer integration, or enable file writing.

This document is not evidence for production readiness, real-data readiness,
model performance, F1, accuracy, ECE, AURCC, artifact writer CLI actual
invocation correctness, artifact body generation integration correctness,
manifest writer integration correctness, generated policy quality, or
learner-state estimator correctness.

## 3. Prior Completed Chain

- Step489 implemented the initial artifact writer CLI integration runtime module
  / CLI / focused tests as a metadata-only, body-free, no-file-writing runtime
  smoke path.
- Step490 designed the standalone Makefile target for the Step489 runtime CLI.
- Step491 implemented the standalone Makefile target for the Step489 runtime
  smoke.
- Step492 designed release-quality integration for that standalone target.
- Step493 added the runtime smoke target to the release-quality wrapper.
- Step494 designed the public-safe remote/manual run record workflow for the
  runtime smoke check.
- Step495 recorded a public-safe remote status marker for the runtime smoke
  check.
- Step496 designed the future artifact writer CLI actual invocation boundary.

Step496 is an actual invocation boundary design. It does not prove artifact
writer CLI actual invocation correctness and does not implement actual
invocation.

## 4. Proposed Fixture Root

Future fixture root candidate:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation/`

Step497 does not create this fixture root.

## 5. Proposed Case Layout

Each future case directory should contain metadata-only JSON files. The proposed
file layout is:

- `case_metadata.json`: case identity, expected category, and synthetic-only /
  metadata-only flags.
- `runtime_request_metadata.json`: runtime request metadata for the proposed
  actual invocation boundary.
- `runtime_pointer_metadata.json`: relative pointers to metadata-only fixture
  resources.
- `artifact_writer_cli_invocation_metadata.json`: metadata-only command
  boundary information for the candidate artifact writer CLI invocation.
- `expected_invocation_summary.json`: expected public-safe summary fields and
  status mapping.
- `expected_error.json`: expected error category, reason code, and fail-closed
  handling for invalid cases.

The fixture contract should describe field names and roles only. It should not
store or document JSON body examples, request bodies, pointer bodies, expected
bodies, artifact body payloads, manifest bodies, generated policy bodies, raw
stdout/stderr bodies, raw rows, logits, probabilities, private path values,
absolute path values, or raw learner text.

## 6. Proposed Case Counts

Proposed future fixture counts:

- `total_cases`: 32
- `valid_cases`: 6
- `invalid_cases`: 26
- `json_files_per_case`: 6
- `total_json_files`: 192

These are proposed counts for a future fixture root. Step497 does not create
files and does not validate these counts against any fixture root.

## 7. Valid Case Taxonomy

Proposed valid case categories:

- `valid_minimal_metadata_only_actual_invocation_plan`
- `valid_artifact_writer_cli_summary_body_free`
- `valid_relative_fixture_paths_only`
- `valid_file_writing_disabled_actual_invocation`
- `valid_no_oracle_flags_preserved`
- `valid_invocation_output_safety_flags`

Valid cases must remain synthetic-only, metadata-only, body-free, and
no-oracle. Valid cases must not include artifact body payloads, manifest bodies,
generated policy bodies, request/pointer/expected bodies, raw learner text, raw
rows, logits, probabilities, private path values, absolute path values, raw
stdout/stderr bodies, final text fields, observed-after text fields, gold
labels, post-hoc annotations, test-set tuning signals, or scoring feedback
payloads.

## 8. Invalid / Expected-Failure Case Taxonomy

Proposed invalid case categories:

- `invalid_request_body_present`
- `invalid_pointer_body_present`
- `invalid_expected_body_present`
- `invalid_artifact_body_payload_present`
- `invalid_manifest_body_present`
- `invalid_generated_policy_body_present`
- `invalid_raw_learner_text_present`
- `invalid_raw_rows_present`
- `invalid_logits_present`
- `invalid_probabilities_present`
- `invalid_private_path_present`
- `invalid_absolute_path_present`
- `invalid_final_text_present`
- `invalid_observed_after_text_present`
- `invalid_gold_label_present`
- `invalid_post_hoc_annotation_present`
- `invalid_raw_stdout_body_present`
- `invalid_raw_stderr_body_present`
- `invalid_file_writing_requested`
- `invalid_artifact_body_generation_invoked`
- `invalid_manifest_writer_invoked`
- `invalid_unsupported_artifact_writer_schema`
- `invalid_unsafe_actual_invocation_output`
- `invalid_mismatched_expected_status`
- `invalid_missing_required_metadata_file`
- `invalid_duplicate_case_id`

Expected category boundary:

- `usage_error`: missing required metadata files, duplicate case IDs,
  unsupported metadata layout, or selector misuse.
- `fail_closed`: forbidden fields, forbidden strings, body-bearing output,
  unsafe paths, unexpected file writing, artifact body generation invocation, or
  manifest writer invocation.
- `input_error`: malformed JSON or unreadable metadata-only files.
- `mismatch`: expected status, reason code, or exit-code category mismatch.

Invalid cases should use controlled sentinel metadata. They should not store
actual prohibited payloads.

## 9. Expected Invocation Summary Schema

Future `expected_invocation_summary.json` or equivalent metadata should include
these field names:

- `schema_version`
- `case_id`
- `expected_status`
- `expected_reason_code`
- `expected_exit_code_category`
- `expected_summary_mode`
- `artifact_writer_cli_invoked`
- `artifact_writer_cli_exit_code_category`
- `artifact_writer_cli_invocation_planned`
- `artifact_body_generation_invoked`
- `manifest_writer_invoked`
- `file_writing_enabled`
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
- `synthetic_only_checked`
- `metadata_only_checked`
- `no_oracle_checked`
- `production_readiness_claimed`
- `real_data_readiness_claimed`
- `performance_claims_present`
- `residue_expected`

This section defines field names only. It does not include JSON body examples.

## 10. Runtime Request Metadata Contract

Allowed runtime request metadata fields:

- `schema_version`
- `case_id`
- `mode`
- `invocation_mode`
- `artifact_writer_cli_module`
- `runtime_schema_version`
- `fixture_source`
- `relative_fixture_path`
- `suppression_policy`
- `no_oracle_policy`
- `synthetic_only`
- `metadata_only`
- `file_writing_requested`
- `artifact_writer_cli_actual_invocation_requested`

Forbidden runtime request metadata fields:

- `request_body`
- `pointer_body`
- `expected_body`
- `final_text`
- `observed_after_text`
- `raw_learner_text`
- `raw_rows`
- `logits`
- `probabilities`
- `gold_labels`
- `post_hoc_annotations`
- `generated_policy_body`
- `artifact_body_payload`
- `manifest_body`
- `raw_stdout_body`
- `raw_stderr_body`
- `absolute_path`
- `private_path`

The request metadata must stay body-free and must use relative fixture paths
only.

## 11. Runtime Pointer Metadata Contract

Allowed runtime pointer metadata fields:

- `schema_version`
- `case_id`
- `pointer_mode`
- `relative_request_metadata_path`
- `relative_invocation_metadata_path`
- `relative_expected_summary_path`
- `relative_expected_error_path`
- `relative_fixture_root`
- `path_policy`
- `synthetic_only`
- `metadata_only`
- `no_oracle_checked`

Forbidden runtime pointer metadata fields:

- `absolute_request_path`
- `absolute_pointer_path`
- `absolute_expected_path`
- `private_request_path`
- `private_pointer_path`
- `private_expected_path`
- `request_body`
- `pointer_body`
- `expected_body`
- `artifact_body_payload`
- `manifest_body`
- `generated_policy_body`
- `raw_stdout_body`
- `raw_stderr_body`

Relative repo paths may be represented as metadata. Absolute or private path
values must not be stored.

## 12. Artifact Writer CLI Invocation Metadata Contract

Allowed invocation metadata:

- command label
- module name
- safe mode
- summary mode
- expected exit-code category
- relative request pointer
- relative artifact writer pointer
- suppression flags
- no-oracle flags
- expected invocation flags

Forbidden invocation metadata:

- command output raw body
- full stdout
- full stderr
- artifact body payload
- manifest body
- generated policy body
- file contents
- absolute path values
- private path values

The invocation metadata should support future actual invocation planning without
allowing payload transfer across the runtime boundary.

## 13. Sentinel Policy

Invalid cases must represent unsafe conditions through controlled metadata-only
sentinels:

- prohibited field presence is represented by controlled sentinel fields
- actual prohibited body values must not appear
- sentinel field names may be allowed only in expected invalid cases
- sentinel values must remain body-free
- private / absolute path cases must not store actual private or absolute path
  strings
- artifact body / manifest body / generated policy body cases must not store
  actual body payloads
- raw stdout / stderr body cases must not store actual raw output
- raw learner text / raw rows / logits cases must not store actual raw content

The future validator should fail-closed if an invalid sentinel is represented by
an actual payload rather than a body-free sentinel.

## 14. Validator Implications

A future validator should check at least:

- root discovery
- required file presence
- case ID consistency
- schema version consistency
- expected status / reason-code matching
- forbidden key scan
- forbidden string scan
- absolute/private path scan
- no-oracle field scan
- suppression flag consistency
- file-writing disabled/default policy
- artifact body / manifest writer separation
- raw stdout/stderr body absence
- actual invocation output safety fields
- residue expectation checks
- safe summary field matching
- deterministic ordering
- selector safety

Validator output should be public-safe, summary-only, body-free, and JSON
serializable.

## 15. Exit-Code and Status Mapping

Future validator and fixture metadata should use a small status vocabulary:

- `pass`: expected safe metadata-only invocation boundary behavior.
- `usage_error`: invalid root structure, missing metadata, duplicate case IDs,
  or invalid selector usage.
- `fail_closed`: unsafe payload, unsafe path, unexpected file writing,
  unexpected artifact body generation, unexpected manifest writer invocation, or
  unsafe actual invocation output.
- `input_error`: malformed JSON or unreadable metadata-only files.
- `mismatch`: actual summary fields do not match expected metadata.

Exit-code categories should be metadata-only labels such as `zero`,
`usage_error`, `fail_closed`, `input_error`, and `mismatch`. Step497 does not
implement this mapping.

## 16. Relationship to Step496 Actual Invocation Design

- Step496 defines the future actual invocation boundary: allowed inputs,
  forbidden inputs, output boundary, safety scan, fail-closed behavior, and
  no-file-writing boundary.
- Step497 defines a proposed fixture contract for testing that future boundary.

Step497 is a future fixture root contract design. It is not actual invocation
implementation, fixture root creation, fixture JSON creation, or validator
implementation.

## 17. Planned Follow-Up Steps

Possible future steps:

1. Step498: actual invocation fixture root creation
2. Step499: actual invocation fixture validator design
3. Step500: actual invocation fixture validator module / CLI / focused tests
4. Step501: actual invocation runtime update design
5. Step502: actual invocation runtime implementation update
6. Step503: Makefile target update design
7. Step504: Makefile target update
8. Step505: release-quality integration design
9. Step506: release-quality wrapper integration
10. Step507: remote/manual run record workflow design
11. Step508: remote status marker

Step497 does not start any of these follow-up steps.

## 18. Non-Claims

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
- fixture root creation
- validator implementation
- actual invocation implementation

## 19. Public-Safe Checklist

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

## 20. Step498 Fixture Root Creation Status

Step498 creates the synthetic metadata-only fixture root proposed by this
contract:

[Artifact writer CLI actual invocation fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation/README.md)

Confirmed Step498 counts:

- `total_cases`: 32
- `valid_cases`: 6
- `invalid_cases`: 26
- `json_files_per_case`: 6
- `total_json_files`: 192
- `root_readme`: 1

The fixture root uses metadata-only sentinel flags. It does not implement a
validator, update runtime actual invocation, implement artifact writer CLI
actual invocation, change Python code/tests, change Makefile, change the
release-quality wrapper, change workflow files, connect artifact body
generation integration, connect manifest writer integration, enable file
writing, use real data, compute metrics, or claim production readiness.

## 21. Step499 Fixture Validator Design Status

Step499 adds the docs-only / planning-only validator design for the Step498
fixture root:

[Frozen policy generation artifact writer CLI actual invocation fixture validator design](frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validator_design.md)

The validator design does not implement a validator, change Python code/tests,
change Makefile, change the release-quality wrapper, change workflow files,
change fixture JSON, update runtime actual invocation, implement artifact
writer CLI actual invocation, connect artifact body generation integration,
connect manifest writer integration, enable file writing, use real data,
compute metrics, or claim production readiness.

## 22. Step500 Fixture Validator Implementation Status

Step500 implements the static validator module / CLI / focused tests for the
Step498 fixture root:

- `python/learner_state/frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation.py`

The validator checks 32 cases / 192 JSON files with public-safe summary-only
output and validation schema
`learner_state_frozen_policy_generation_artifact_writer_cli_actual_invocation_fixture_validation_v0.1`.
This does not change fixture JSON, update runtime actual invocation, implement
artifact writer CLI actual invocation, change Makefile, change the
release-quality wrapper, change workflow files, connect artifact body
generation integration, connect manifest writer integration, enable file
writing, use real data, compute metrics, or claim production readiness.
