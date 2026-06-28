# Frozen Policy Generation Manifest Writer Runtime Implementation Design

## 1. Purpose

This document fixes the docs-only implementation design for a future frozen
policy generation manifest writer runtime.

It is not an implementation, not fixture JSON creation, not release-quality
integration, not manifest file writing, not artifact writer CLI integration,
not performance evaluation, and not a production readiness claim.

The initial runtime should be synthetic-only, metadata-only, no-oracle, and
no-file. It should construct a safe manifest writer result summary from a
manifest writer request and safe artifact result pointers without producing
or writing a manifest body.

## 2. Current State

- the runtime API design exists
- runtime fixtures exist
- the runtime fixture validator exists
- the runtime fixture validator target is in release-quality
- the runtime fixture validator remote/manual status marker exists
- the manifest writer runtime does not exist
- the manifest writer CLI does not exist
- manifest file writing does not exist
- artifact writer CLI integration does not exist

## 3. Proposed Runtime Module

Future module:

- `learner_state.frozen_policy_generation_manifest_writer`

## 4. Proposed Initial CLI

Future CLI:

- `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer`

## 5. Proposed Initial CLI Arguments

Initial arguments:

- `--request`
- `--artifact-result`
- `--artifact-body-result`
- `--json`
- `--help`

The initial CLI should not accept `--manifest-out`. File writing is a separate
future phase. The first implementation should support only
`metadata_only_no_file` mode.

The runtime fixture validator remains separate. It validates static fixture
contracts and must not be treated as the writer runtime.

## 6. Proposed APIs / Dataclasses

Proposed APIs:

- `load_manifest_writer_request(path)`
- `load_artifact_writer_result_pointer(path)`
- `load_artifact_body_generation_result_pointer(path)`
- `build_metadata_only_manifest_result(request, artifact_pointer, artifact_body_pointer)`
- `audit_manifest_result_safety(result)`
- `summarize_manifest_writer_result(result)`
- `main(argv=None)`

Proposed dataclasses:

- `ManifestWriterRequest`
- `ArtifactWriterResultPointer`
- `ArtifactBodyGenerationResultPointer`
- `ManifestWriterResult`
- `ManifestWriterSafetyFlags`
- `ManifestWriterCountSummary`
- `ManifestWriterError`

## 7. Initial Supported Mode

Supported mode:

- `metadata_only_no_file`

Expected behavior:

- `writer_status=pass`
- `manifest_writer_mode=metadata_only_no_file`
- `manifest_body_available=false`
- `manifest_file_written=false`
- `manifest_output_path_available=false`
- `runtime_writer_executed=true`
- `release_quality_ready=false`
- `content_suppressed=true`
- `manifest_body_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_absolute_paths=true`
- `no_artifact_body_payload=true`
- `no_generated_policy_body=true`
- `no_manifest_body_nesting=true`
- `no_request_body=true`
- `no_pointer_body=true`
- `no_expected_body=true`
- `no_performance_claims=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `non_proof_notice_checked=true`
- `path_policy_checked=true`
- `content_policy_checked=true`
- `file_writing_checked=true`

## 8. Runtime Input Policy

Allowed input:

- manifest writer request metadata fields
- artifact writer result safe metadata pointer
- artifact body generation result safe metadata pointer
- safe validation reference IDs
- safe release-quality reference IDs
- safe synthetic `artifact_id`
- safe synthetic `artifact_body_id`
- safe synthetic `manifest_id`-like IDs
- boolean no-body flags
- synthetic-only notices
- no-oracle notices
- non-proof notices

Forbidden input:

- manifest body
- manifest JSON body
- artifact body payload
- generated policy body
- request body nesting
- pointer body nesting
- expected body nesting
- raw rows
- logits/probabilities
- private paths
- absolute paths
- raw learner text
- `final_text`
- `observed_after_text`
- gold labels
- scoring feedback payload
- real participant data
- performance metric body

## 9. Runtime Output Policy

Allowed output:

- `mode=manifest_writer`
- result schema version
- `writer_status`
- `manifest_writer_mode`
- `manifest_id`
- `artifact_id`
- `artifact_body_id`
- `validation_reference_count`
- `release_quality_reference_count`
- `manifest_body_available=false`
- `manifest_file_written=false`
- `manifest_output_path_available=false`
- reason codes
- failed checks
- safety flags
- count summary
- safe summary

Forbidden output:

- manifest body
- manifest JSON body
- artifact body payload
- generated policy body
- request body
- pointer body
- expected body
- raw rows
- logits/probabilities
- private paths
- absolute paths
- raw learner text
- final/gold/observed-after text
- performance evidence

## 10. Fail-Closed Behavior

The runtime should fail closed if:

- request path is missing
- artifact pointer path is missing
- artifact body pointer path is missing
- JSON is malformed
- schema version is unknown
- `manifest_writer_mode` is unsupported
- `include_manifest_body=true`
- `allow_manifest_file_writing=true`
- `manifest_out` is present
- pointer `include_body_payload=true`
- pointer `include_raw_rows=true`
- pointer `include_private_paths=true`
- synthetic notice is missing
- no-oracle notice is missing
- non-proof notice is missing
- forbidden body/payload/raw/logit/private/absolute marker is found
- artifact writer CLI integration is requested
- real-data marker is found

Fail-closed output should remain body-free and should report only safe reason
codes and failed check names.

## 11. Result Schema Fields

Proposed result fields:

- `mode`
- `result_schema_version`
- `writer_status`
- `manifest_writer_mode`
- `manifest_id`
- `artifact_id`
- `artifact_body_id`
- `validation_reference_count`
- `release_quality_reference_count`
- `manifest_body_available`
- `manifest_file_written`
- `manifest_output_path_available`
- `reason_codes`
- `failed_checks`
- `safety_flags`
- `count_summary`
- `safe_summary`
- `runtime_writer_executed`
- `release_quality_ready`

## 12. Count Summary Fields

Proposed count summary fields:

- `manifest_metadata_field_count`
- `validation_reference_count`
- `release_quality_reference_count`
- `raw_row_count`
- `logits_dump_count`
- `private_path_count`
- `absolute_path_count`
- `artifact_body_payload_count`
- `generated_policy_body_count`
- `manifest_body_count`
- `request_body_count`
- `pointer_body_count`
- `expected_body_count`
- `performance_metric_count`
- `written_file_count`

## 13. Safety Flags

Proposed safety flags:

- `content_suppressed`
- `manifest_body_suppressed`
- `no_raw_rows`
- `no_logits_dump`
- `no_private_paths`
- `no_absolute_paths`
- `no_artifact_body_payload`
- `no_generated_policy_body`
- `no_manifest_body_nesting`
- `no_request_body`
- `no_pointer_body`
- `no_expected_body`
- `no_performance_claims`
- `synthetic_only_checked`
- `no_oracle_checked`
- `non_proof_notice_checked`
- `path_policy_checked`
- `content_policy_checked`
- `file_writing_checked`

## 14. Relation To Runtime Fixture Validator

The runtime fixture validator validates static fixture contracts. It does not
execute a runtime writer and does not write manifest files.

The future runtime writer should execute metadata-only no-file result
construction. Focused runtime writer tests can use selected valid runtime
fixtures as inputs, but validator success does not imply writer
implementation correctness.

Invalid runtime fixture behavior can be tested through future CLI fail-closed
cases. Those tests should remain body-free and should not require manifest
file writing.

## 15. Relation To Existing Artifact Writer / Artifact Body

The artifact writer runtime already produces safe metadata-only result
summaries. Artifact body generation can produce suppressed or safe-metadata
summaries.

The manifest writer should initially consume pointers and safe metadata
references only. It must not reopen, reconstruct, copy, or embed artifact body
payloads.

Artifact writer CLI integration remains separate. The initial runtime should
not call the artifact writer CLI or artifact body generation CLI.

## 16. Proposed Tests For Future Implementation

Future tests should cover:

- `--help` exits 0
- missing request returns usage error
- valid `metadata_only_minimal_no_file` returns pass
- valid artifact body reference returns pass
- valid release-quality reference returns pass
- `manifest_body_available=false`
- `manifest_file_written=false`
- `manifest_output_path_available=false`
- `runtime_writer_executed=true`
- `release_quality_ready=false`
- no body fields in output
- no raw rows/logits/private/absolute paths in output
- `include_manifest_body=true` fails closed
- `allow_manifest_file_writing=true` fails closed
- `manifest_out` present fails closed in the initial implementation
- pointer `include_body_payload=true` fails closed
- missing notices fail closed
- malformed JSON fails closed
- unknown schema fails closed
- JSON output is parseable
- human output is body-free
- no files are written
- `tmp/frozen_policy_generation_manifest` residue remains 0

## 17. Future Implementation Staging

Proposed staging:

- Step401: runtime writer fixture-backed implementation
- Step402: focused runtime writer tests
- Step403: standalone Makefile target design
- Step404: standalone Makefile target implementation
- Step405: release-quality integration design
- Step406: wrapper integration
- Step407: remote/manual run record workflow design
- Step408: remote/manual run status marker
- later: manifest file writing design and implementation

## 18. Path/File Writing Policy

Initial runtime policy:

- no file writing
- no `--manifest-out` in the initial CLI
- any `manifest_out` in the request fails closed
- no absolute path in output summary
- no manifest output residue

Future manifest file writing needs separate design, fixtures, validation,
isolated write checks, Makefile target, release-quality staging, and remote
status marker.

## 19. Safety Interpretation

Future runtime writer success means metadata-only no-file manifest writer
result construction works.

It does not mean manifest file writing is ready, artifact writer CLI
integration exists, production readiness is established, model performance is
proven, or real-data readiness is established.

## 20. Beginner-Friendly Explanation

A runtime writer is the code that will take safe request and pointer metadata
and produce a safe result summary at execution time.

The runtime fixture validator is different: it checks that fixture files have
the expected structure and safety policy. It does not run the writer.

The design starts with no-file mode because it is the smallest safe runtime
step. It proves metadata-only result construction before any manifest output
path or file writing is introduced.

The runtime does not create a manifest body because body generation raises
content and leakage risks that are out of scope for the first implementation.

It also does not read artifact body payloads. It references only safe metadata
pointers so that generated policy bodies, raw rows, raw learner text, and
private paths remain out of logs and summaries.

## 21. Docs Safety Policy

Docs must include only field names, counts, command shapes, and policy
statements.

Docs must not include:

- JSON body examples
- manifest body examples
- request/pointer body examples
- artifact body payload examples
- raw logs
- private path examples

## 22. What This Does Not Do

- does not implement the runtime writer
- does not implement the CLI
- does not write manifest files
- does not create or change fixtures
- does not change Makefile
- does not change the release-quality wrapper
- does not change workflow YAML
- does not connect artifact writer CLI
- does not use real data
- does not compute metrics
- does not prove production readiness

## 23. Next Recommended Steps

- metadata-only runtime writer implementation
- focused runtime writer tests
- Makefile target design and implementation
- release-quality integration
- remote marker
- later manifest file writing design

## 24. Step401 Implementation Status

Step401 implements the initial metadata-only no-file manifest writer runtime:

- `python/learner_state/frozen_policy_generation_manifest_writer.py`
- `python/learner_state/tests/test_frozen_policy_generation_manifest_writer.py`

Implemented scope:

- module `learner_state.frozen_policy_generation_manifest_writer`
- CLI `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer`
- initial arguments `--request`, `--artifact-result`, `--artifact-body-result`,
  `--json`, and `--help`
- mode `metadata_only_no_file`
- body-free result summary
- fail-closed handling for unsupported body/file/payload/path inputs
- focused tests over the five valid runtime fixture cases

This implementation does not add a Makefile target, does not add
release-quality integration, does not accept `--manifest-out`, does not write
manifest files, does not generate manifest bodies, does not connect artifact
writer CLI output, does not use real data, does not compute metrics, and does
not claim production readiness.

## 25. Related Documents

- [Frozen policy generation manifest writer runtime API design](frozen_policy_generation_manifest_writer_runtime_api_design.md)
- [Frozen policy generation manifest writer runtime fixture contract design](frozen_policy_generation_manifest_writer_runtime_fixture_contract_design.md)
- [Frozen policy generation manifest writer runtime fixture validator design](frozen_policy_generation_manifest_writer_runtime_fixture_validator_design.md)
- [Frozen policy generation manifest writer runtime fixture release-quality integration design](frozen_policy_generation_manifest_writer_runtime_fixture_release_quality_integration_design.md)
- [Learner-state frozen policy generation manifest writer runtime fixture release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_runtime_fixture_release_quality_remote_run_status.md)
- [Frozen policy generation manifest writer boundary design](frozen_policy_generation_manifest_writer_boundary_design.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)
