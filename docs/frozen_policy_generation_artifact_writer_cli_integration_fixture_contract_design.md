# Frozen Policy Generation Artifact Writer CLI Integration Fixture Contract Design

## 1. Purpose

This document fixes the docs-only fixture contract design for future frozen
policy generation artifact writer CLI integration fixtures.

It is not fixture root creation, validator implementation, artifact writer CLI
integration implementation, artifact body generation integration, manifest
writer integration, manifest body generation, release-quality integration,
real-data readiness, or production readiness.

The contract is synthetic-only, metadata-only, no-oracle, body-suppressed, and
public-safe. It may name files, fields, counts, case ids, reason codes, and
policy flags, but it must not include fixture JSON bodies, request bodies,
pointer bodies, expected-result bodies, written file JSON bodies, manifest
bodies, artifact body payloads, generated policy bodies, raw rows,
logits/probabilities, private paths, absolute paths, raw learner text, raw
logs, or full job output.

## 2. Current State

- Step466 artifact writer CLI integration design exists
- artifact writer fixture validation exists
- artifact writer runtime smoke exists
- generator scaffold fixture validation exists
- generator scaffold runtime smoke exists
- artifact body fixture validation exists
- artifact body generation suppressed CLI smoke exists
- artifact body generation safe-metadata CLI smoke exists
- artifact body file writing fixture validation exists
- artifact body isolated write validation exists
- manifest writer fixture/runtime/file-writing/isolated/production checks
  exist
- manifest writer runtime metadata-only file writing smoke exists
- release-quality wrapper includes the current artifact and manifest writer
  checks
- artifact writer CLI integration fixture contract does not exist yet
- artifact writer CLI integration fixture root does not exist yet
- artifact writer CLI integration validator does not exist yet
- artifact writer CLI integration Makefile target does not exist yet
- artifact writer CLI integration release-quality integration does not exist
  yet
- artifact body generation CLI integration is not implemented
- manifest writer integration is not implemented
- manifest body generation is not implemented
- production readiness is not claimed

## 3. Recommended Scope

The first artifact writer CLI integration fixture contract should cover only:

- generator scaffold CLI -> artifact writer CLI
- no artifact body generation CLI
- no manifest writer CLI/runtime chaining
- no manifest body generation
- no file writing
- metadata-only artifact writer result
- body-free public output
- `release_quality_ready=false`

This keeps the integration boundary narrow and keeps later artifact body and
manifest writer chaining as separate fixture and validation work.

## 4. Fixture Root Proposal

Proposed future fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_writer_cli_integration/`

Step467 does not create this root.

Proposed layout:

- `README.md`
- `valid/`
- `invalid/`

Each case directory should contain exactly 6 JSON files:

- `case_metadata.json`
- `generator_request.json`
- `generator_input_fixture_pointer.json`
- `artifact_writer_request.json`
- `generator_result_pointer.json`
- `expected_artifact_writer_cli_integration_result.json`

Naming convention:

- valid cases use `valid/<case_id>`
- invalid cases use `invalid/<case_id>`
- case ids should be lowercase, snake-case-compatible path segments
- selectors should never be absolute, parent-traversing, or outside the
  `valid/` and `invalid/` roots

Fixture files must not include raw bodies, public absolute paths, raw learner
text, real participant data, or performance metric bodies.

## 5. Case Count Summary

Expected future counts:

- total cases: 28
- valid cases: 6
- invalid cases: 22
- JSON files per case: 6
- total JSON files: 168

Case categories:

- valid pass cases: 6
- invalid usage-error or fail-closed cases: 22
- artifact body generation integration cases: unsupported only
- manifest writer integration cases: out of scope
- file-writing cases: unsupported only

## 6. Proposed Case Taxonomy

Valid cases:

1. `valid/minimal_generator_to_artifact_writer_metadata_only`
2. `valid/generator_with_validation_references_metadata_only`
3. `valid/generator_with_release_quality_reference_metadata_only`
4. `valid/artifact_writer_preserves_safe_ids_metadata_only`
5. `valid/no_file_writing_default_metadata_only`
6. `valid/body_suppressed_metadata_only`

Invalid cases:

1. `invalid/missing_generator_request`
2. `invalid/missing_generator_input_pointer`
3. `invalid/missing_artifact_writer_request`
4. `invalid/missing_generator_result_pointer`
5. `invalid/malformed_generator_result_pointer`
6. `invalid/unknown_generator_result_schema`
7. `invalid/unvalidated_generator_result`
8. `invalid/generated_policy_body_leakage`
9. `invalid/artifact_body_payload_leakage`
10. `invalid/manifest_body_leakage`
11. `invalid/request_body_leakage`
12. `invalid/pointer_body_leakage`
13. `invalid/raw_rows_leakage`
14. `invalid/logits_dump_leakage`
15. `invalid/private_path_leakage`
16. `invalid/absolute_path_leakage`
17. `invalid/raw_learner_text_leakage`
18. `invalid/performance_claim_in_artifact`
19. `invalid/non_synthetic_input`
20. `invalid/no_oracle_violation`
21. `invalid/unsupported_file_writing_mode`
22. `invalid/unsupported_artifact_body_generation_integration`

## 7. Per-Case File Contract

### `case_metadata.json`

Purpose:

- declares case id, category, expected status, and expected reason codes
- records synthetic-only, metadata-only, no-oracle, and body-suppression
  flags
- records whether the case is valid or invalid

Forbidden:

- raw learner text
- request/pointer/expected bodies
- raw rows
- logits/probabilities
- private or absolute path values
- performance metric bodies
- real participant data

### `generator_request.json`

Purpose:

- describes the synthetic generator scaffold request metadata needed for the
  integration boundary
- references validation-safe ids and metadata-only options

Forbidden:

- generated policy body
- raw rows
- logits/probabilities
- request body payload copied for display
- observed-after text, final corrected text, gold labels, or scoring feedback

### `generator_input_fixture_pointer.json`

Purpose:

- points to synthetic input fixture metadata for the generator scaffold side
- provides safe reference ids only

Forbidden:

- pointer body payload
- raw rows
- private or absolute path values
- raw learner text
- future/oracle information

### `artifact_writer_request.json`

Purpose:

- describes the metadata-only artifact writer request for this integration
  boundary
- requests body suppression and no file writing by default

Forbidden:

- artifact body payload request
- generated policy body request
- manifest body request
- file-writing request
- private or absolute path values
- performance claims

### `generator_result_pointer.json`

Purpose:

- represents a safe metadata pointer to the generator scaffold result
- exposes only safe ids, schema/version metadata, and validation references

Forbidden:

- generated policy body
- raw rows
- logits/probabilities
- scoring feedback payload
- private or absolute path values
- raw learner text

### `expected_artifact_writer_cli_integration_result.json`

Purpose:

- declares the expected body-free integration result
- records expected status, reason codes, counters, and safety flags
- records that artifact body generation and manifest writer execution are
  false

Forbidden:

- expected result body payload
- written file JSON body
- artifact body payload
- manifest body
- generated policy body
- raw rows
- logits/probabilities
- private or absolute path values
- raw learner text
- real participant data
- performance metric body

## 8. Expected Result Schema Proposal

Proposed expected-result schema version:

`learner_state_frozen_policy_generation_artifact_writer_cli_integration_result_v0.1`

Expected public summary fields:

- `mode=artifact_writer_cli_integration_fixture_validation`
- `integration_status`
- `integration_step=generator_scaffold_to_artifact_writer`
- `generator_scaffold_executed`
- `artifact_writer_executed`
- `artifact_body_generation_executed=false`
- `manifest_writer_executed=false`
- `generated_artifact_written=false`
- `artifact_file_written=false`
- `manifest_file_written=false`
- `artifact_body_available=false`
- `generated_artifact_body_available=false`
- `manifest_body_available=false`
- `body_suppressed=true`
- `artifact_body_suppressed=true`
- `manifest_body_suppressed=true`
- `content_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_absolute_paths=true`
- `no_generated_policy_body=true`
- `no_artifact_body_payload=true`
- `no_manifest_body=true`
- `no_request_body=true`
- `no_pointer_body=true`
- `no_expected_body=true`
- `no_performance_claims=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `file_writing_checked=true`
- `artifact_writer_cli_integration_checked=true`
- `release_quality_ready=false`

Expected count fields:

- `written_file_count`
- `body_field_count`
- `raw_row_count`
- `logits_dump_count`
- `private_path_count`
- `absolute_path_count`
- `performance_metric_count`
- `validation_reference_count`
- `release_quality_reference_count`

## 9. Valid Case Expectations

For every valid case:

- `integration_status=pass`
- `generator_scaffold_executed=true`
- `artifact_writer_executed=true`
- `artifact_body_generation_executed=false`
- `manifest_writer_executed=false`
- `generated_artifact_written=false`
- `artifact_file_written=false`
- `manifest_file_written=false`
- `written_file_count=0`
- `body_field_count=0`
- `raw_row_count=0`
- `logits_dump_count=0`
- `private_path_count=0`
- `absolute_path_count=0`
- `performance_metric_count=0`
- `release_quality_ready=false`
- reason codes are empty or `none`

## 10. Invalid Case Expectations

For every invalid case:

- `integration_status=usage_error` or `integration_status=fail_closed`
- `artifact_writer_executed=false` if input contract validation fails before
  the artifact writer boundary
- `artifact_body_generation_executed=false`
- `manifest_writer_executed=false`
- `generated_artifact_written=false`
- `artifact_file_written=false`
- `manifest_file_written=false`
- `written_file_count=0`
- `body_field_count=0`
- forbidden content counters remain 0 in public output
- reason codes include the expected reason code
- no raw body is printed
- no fixture/request/pointer/expected body is copied
- no private or absolute path value is exposed

Invalid leakage cases should use sentinel labels, booleans, and expected
reason codes only, not actual payloads.

## 11. Reason Code Taxonomy

The future validator should recognize:

- `missing_generator_request`
- `missing_generator_input_pointer`
- `missing_artifact_writer_request`
- `missing_generator_result_pointer`
- `malformed_generator_result_pointer`
- `unknown_generator_result_schema`
- `unvalidated_generator_result`
- `generated_policy_body_leakage`
- `artifact_body_payload_leakage`
- `manifest_body_leakage`
- `request_body_leakage`
- `pointer_body_leakage`
- `raw_rows_leakage`
- `logits_dump_leakage`
- `private_path_leakage`
- `absolute_path_leakage`
- `raw_learner_text_leakage`
- `performance_claim_in_artifact`
- `non_synthetic_input`
- `no_oracle_violation`
- `unsupported_file_writing_mode`
- `unsupported_artifact_body_generation_integration`

## 12. Forbidden Content Policy

Fixture files and expected outputs must not include:

- raw learner text
- raw rows
- logits/probabilities
- generated policy body
- artifact body payload
- manifest body
- request body
- pointer body
- expected body
- private paths
- absolute local/temp paths
- performance metric body
- real participant data
- final text
- observed-after text
- gold label
- scoring feedback payload

## 13. No-Oracle Policy

The fixture contract must enforce:

- no future information
- no observed-after text
- no final corrected text
- no gold labels
- no post-hoc annotations
- no test-set tuning
- no generated body leakage
- no scoring feedback leakage

## 14. File-Writing Policy

The integration fixtures should represent no file writing:

- `generated_artifact_written=false`
- `artifact_file_written=false`
- `manifest_file_written=false`
- `written_file_count=0`

Any future file-writing behavior must be a separate opt-in design and should
not be introduced through this fixture contract.

## 15. Relation To Artifact Body Generation

Artifact body generation is not included in the Step467 fixture contract.

The invalid case
`invalid/unsupported_artifact_body_generation_integration` documents this
boundary. Future artifact body generation integration should receive its own
fixture contract, fixture root, validator, Makefile target, release-quality
staging, and remote marker sequence.

## 16. Relation To Manifest Writer

Manifest writer execution is not included in the Step467 fixture contract.

All expected results should keep:

- `manifest_writer_executed=false`
- `manifest_body_available=false`
- `manifest_file_written=false`

Manifest writer integration should remain a later design sequence.

## 17. Relation To Release-Quality

Release-quality staging should remain ordered:

- fixture contract first
- fixture root next
- validator design later
- validator implementation later
- Makefile target later
- release-quality wrapper integration later
- remote/manual run record workflow later
- remote status marker later

This contract should not be added to release-quality until a static validator
and standalone Makefile target exist.

## 18. Docs Safety Policy

Docs may include:

- field names
- reason code names
- target names
- schema version names
- case names
- counts
- policy names

Docs must not include:

- JSON body examples
- raw logs
- full job output
- private or absolute path examples
- raw learner text examples
- written body examples
- artifact body payload examples
- generated policy body examples
- manifest body examples

## 19. What This Does Not Do

This design does not:

- create fixtures
- create fixture directories
- create or modify fixture JSON
- implement a validator
- implement integration runtime
- add a Makefile target
- integrate release-quality
- modify workflow YAML
- modify runtime code
- modify Python tests
- use real data
- compute metrics
- prove production readiness
- prove real-data readiness

## 20. Next Recommended Steps

- Step468 fixture root creation
- Step469 validator design
- Step470 validator implementation
- Step471 Makefile target design
- Step472 Makefile target implementation
- Step473 release-quality integration design
- Step474 wrapper integration
- Step475 remote workflow design
- Step476 remote marker
