# Frozen Policy Generation Manifest Writer Runtime File Writing Implementation Plan

## 1. Purpose

This document fixes the docs-only implementation plan for adding
production-facing metadata-only runtime file writing to the frozen policy
generation manifest writer in a later step.

It is not implementation. It is not public `--manifest-out` implementation in
this step. It is not artifact writer CLI integration, not manifest body
generation, not performance evaluation, not real-data readiness, and not a
production readiness claim.

The plan exists to make the next implementation step narrow, testable, and
consistent with the synthetic-only, metadata-only, no-oracle boundary already
established by the broad file writing fixture validator, isolated write
validation, production file writing fixture validator, and their Release
Quality status markers.

## 2. Current State

- The metadata-only no-file manifest writer runtime exists.
- The broad manifest writer file writing fixture validator exists and is in
  release-quality.
- The isolated write validation harness exists and is in release-quality.
- The production file writing fixture validator exists and is in
  release-quality.
- Remote/manual Release Quality status markers exist for the broad fixture
  validation, isolated write validation, and production file writing fixture
  validation layers.
- Production-facing runtime file writing does not exist.
- Public `--manifest-out` is not implemented.
- Artifact writer CLI integration does not exist.
- Manifest body generation does not exist.

## 3. Implementation Goal For Next Step

The next implementation step should add opt-in metadata-only manifest file
writing to the manifest writer runtime.

Goals:

- keep no-file runtime behavior unchanged by default
- add future public CLI arguments:
  - `--manifest-out`
  - `--allow-overwrite`
- write exactly one metadata-only manifest JSON when the output path is safe
- never write manifest body
- never write artifact body payload
- never write generated policy body
- never write request, pointer, or expected-result body
- never write raw rows, logits, private paths, raw learner text, or
  performance bodies
- emit body-free stdout and stderr only
- fail closed for unsafe paths, unsafe overwrite, write failure, parse
  failure, and forbidden content leakage

## 4. Proposed Files To Change In The Next Implementation Step

Expected:

- `python/learner_state/frozen_policy_generation_manifest_writer.py`
- `python/learner_state/tests/test_frozen_policy_generation_manifest_writer.py`
- docs as needed for implementation status

Not expected:

- `Makefile`
- `scripts/check_release_quality.sh`
- `.github/workflows/ci.yml`
- `.github/workflows/release-quality.yml`
- fixture JSON files
- artifact writer CLI
- artifact body generation CLI

## 5. Proposed CLI Behavior

Default behavior:

- no `--manifest-out`
- mode remains metadata-only no-file
- `manifest_file_written=false`
- `written_file_count=0`
- `manifest_output_path_available=false`
- `manifest_body_available=false`
- `manifest_body_suppressed=true`

With safe `--manifest-out`:

- mode becomes metadata-only file-writing mode or equivalent safe runtime
  state
- `manifest_file_written=true`
- `written_file_count=1`
- `manifest_output_path_available=true`
- only a safe relative output path may be reported
- no absolute resolved output path appears in public output
- `manifest_body_available=false`
- `manifest_body_suppressed=true`

With `--allow-overwrite`:

- overwrite is allowed only under the safe project-controlled root
- output exists without `--allow-overwrite` fails closed as a usage error
- symlink-sensitive output remains forbidden even with overwrite enabled

## 6. Safe Output Root Policy

Allowed:

- project-controlled root: `tmp/frozen_policy_generation_manifest/`
- safe relative `.json` paths under that root
- safe filenames
- safe subdirectories
- explicit overwrite only with `--allow-overwrite`

Forbidden:

- absolute path
- parent traversal
- outside allowed root
- user home path
- cloud/private marker path
- hidden private directory
- non-JSON extension
- unsafe filename
- too-long path
- symlink-sensitive output
- public absolute resolved path in stdout, stderr, or result summaries

This policy is more permissive than validator-owned isolated temp-root writes,
but it is still not arbitrary file writing.

## 7. Write Flow For The Next Implementation

Proposed sequence:

- parse manifest writer request, artifact writer result pointer, and artifact
  body generation result pointer
- build the existing metadata-only runtime result
- if `--manifest-out` is absent, return the unchanged no-file result
- if `--manifest-out` is present:
  - validate the output path as a safe relative path
  - normalize under the project-controlled safe output root
  - check overwrite policy
  - build a metadata-only manifest document
  - pre-scan the document for forbidden keys and values
  - write to a temporary sibling file or otherwise safe temporary path
  - parse the written JSON back
  - post-scan the parsed written JSON
  - atomically replace or safely finalize the target
  - produce a body-free runtime summary
- if any failure occurs:
  - fail closed
  - avoid leaving partial files where possible
  - clean up partial output when safe
  - avoid body, payload, private path, absolute path, or raw learner text in
    error output

## 8. Metadata-Only Written Document Policy

Allowed fields:

- `schema_version`
- `result_schema_version`
- `manifest_id`
- `artifact_id`
- `artifact_body_id`
- `manifest_writer_mode`
- `validation_reference_count`
- `release_quality_reference_count`
- `safety_flags`
- `count_summary`
- `safe_summary`
- `writer_version`

Forbidden fields or content:

- `manifest_body`
- `manifest_json_body`
- `artifact_body_payload`
- `generated_policy_body`
- `request_body`
- `pointer_body`
- `expected_body`
- `raw_rows`
- `logits`
- `probabilities`
- `private_path`
- `absolute_path`
- `raw_learner_text`
- `final_text`
- `observed_after_text`
- `gold_label`
- `scoring_feedback`
- `real_participant_data`
- `performance_metric_body`

## 9. Stdout, Stderr, And Result Policy

- stdout is body-free
- stderr is body-free
- written file JSON body is not printed
- absolute resolved output path is not printed
- fixture body is not printed
- result can include:
  - `manifest_file_written=true/false`
  - `written_file_count`
  - `manifest_output_path_available=true/false`
  - `manifest_body_available=false`
  - `manifest_body_suppressed=true`
  - `file_writing_checked=true`
  - `output_path_safety_checked=true`
  - `content_policy_checked=true`
  - `release_quality_ready=false`
  - `safe_summary=metadata_only_manifest_writer_result`
- result must not include absolute output path
- if a path is exposed, it must be a safe relative path only

## 10. Failure / Reason Code Plan

Use these reason codes:

- `unsafe_absolute_manifest_output_path`
- `unsafe_parent_traversal_manifest_output_path`
- `unsafe_manifest_output_path_outside_allowed_root`
- `unsafe_home_manifest_output_path`
- `unsafe_private_path_marker_manifest_output_path`
- `unsafe_cloud_marker_manifest_output_path`
- `unsafe_hidden_private_manifest_directory`
- `unsafe_manifest_output_path_extension`
- `unsafe_manifest_output_filename`
- `unsafe_manifest_output_path_too_long`
- `output_exists_without_overwrite`
- `unsafe_symlink_manifest_output_path`
- `manifest_body_requested`
- `artifact_body_payload_leakage`
- `generated_policy_body_leakage`
- `request_body_leakage`
- `pointer_body_leakage`
- `expected_body_leakage`
- `raw_rows_leakage`
- `logits_dump_leakage`
- `private_path_leakage`
- `absolute_path_leakage`
- `raw_learner_text_leakage`
- `performance_metric_body_leakage`
- `manifest_write_failure`
- `manifest_write_parse_failure`
- `manifest_written_forbidden_content`
- `partial_write_cleanup_failure`
- `unsupported_artifact_writer_cli_integration`
- `unsupported_manifest_writer_mode`

Usage errors should be used for unsafe paths and overwrite violations. Runtime
fail-closed errors should be used for forbidden content, write failure, parse
failure, cleanup failure, unsupported integration, and unsupported modes.

## 11. Focused Tests For The Next Implementation

Future tests should cover:

- default no-file behavior unchanged
- `--manifest-out manifest.json` writes one metadata-only file
- nested safe path writes one metadata-only file
- output exists without `--allow-overwrite` fails
- output exists with `--allow-overwrite` succeeds
- unsafe absolute sentinel/path fails
- parent traversal fails
- outside allowed root fails
- non-JSON extension fails
- unsafe filename fails
- stdout does not include written file body
- stderr does not include written file body
- public output does not include absolute resolved path
- written JSON parses
- written JSON has no forbidden fields
- written JSON has no body, payload, raw row, logit, private path, path, or
  performance fields
- failure does not leave partial residue
- no effect on isolated write validation
- production fixture validator still passes
- full unittest passes

## 12. Relation To Existing Fixture Validators

- The broad file writing fixture validator remains static.
- The isolated write validation remains a validator-owned temporary root
  harness.
- The production file writing fixture validator remains a static contract
  check for future project-controlled output behavior.
- The runtime implementation should satisfy the production fixture contract
  without mutating fixtures.
- The runtime implementation should not reinterpret isolated temp-root success
  as production file writing readiness.

## 13. Relation To Release-Quality

Do not add runtime file writing to release-quality in the implementation step
unless separately designed.

Existing release-quality static checks should remain:

- broad file writing fixture validation
- isolated write validation
- production file writing fixture validation

A future runtime file writing smoke target should be introduced through a
separate design, standalone target, wrapper integration, and remote marker
sequence.

## 14. Relation To Artifact Writer CLI Integration

The next runtime implementation must not call artifact writer CLI and must not
call artifact body generation CLI.

It should consume only existing safe pointer inputs. It should not embed
artifact body payloads, generated policy bodies, request bodies, pointer
bodies, expected-result bodies, raw rows, logits, private paths, or raw
learner text.

Artifact writer CLI integration remains a separate future line of work.

## 15. Docs Safety Policy

Docs may mention:

- field names
- reason code names
- safe relative examples
- count names
- policy names

Docs must not include:

- JSON body examples
- written output examples
- raw logs
- full job output
- private path examples
- absolute path examples
- fixture body examples
- request/pointer/expected-result body examples
- manifest body examples
- artifact body payload examples
- generated policy body examples
- raw learner text

## 16. What This Does Not Do

This Step440 plan does not:

- implement runtime file writing
- implement public `--manifest-out`
- modify Python code/tests
- modify Makefile
- modify the release-quality wrapper
- modify workflow YAML
- modify fixtures JSON
- connect artifact writer CLI
- use real data
- compute metrics
- prove production readiness

## 17. Next Recommended Steps

- Step441 runtime file writing implementation
- Step442 focused runtime file writing tests if not included in Step441
- Step443 Makefile/runtime smoke target design
- Step444 Makefile/runtime smoke target implementation
- Step445 release-quality runtime integration design
- Step446 wrapper integration
- Step447 remote marker
- artifact writer CLI integration remains separate

## 18. Related Documents

- [Frozen policy generation manifest writer production file writing design](frozen_policy_generation_manifest_writer_production_file_writing_design.md)
- [Frozen policy generation manifest writer production file writing fixture contract design](frozen_policy_generation_manifest_writer_production_file_writing_fixture_contract_design.md)
- [Frozen policy generation manifest writer production file writing fixture validator design](frozen_policy_generation_manifest_writer_production_file_writing_fixture_validator_design.md)
- [Frozen policy generation manifest writer production file writing fixture release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_production_file_writing_fixture_release_quality_remote_run_status.md)
- [Frozen policy generation manifest writer runtime implementation design](frozen_policy_generation_manifest_writer_runtime_implementation_design.md)
- [Frozen policy generation manifest writer runtime API design](frozen_policy_generation_manifest_writer_runtime_api_design.md)
- [Frozen policy generation manifest writer boundary design](frozen_policy_generation_manifest_writer_boundary_design.md)
- [Frozen policy generation manifest writer file writing boundary design](frozen_policy_generation_manifest_writer_file_writing_boundary_design.md)
