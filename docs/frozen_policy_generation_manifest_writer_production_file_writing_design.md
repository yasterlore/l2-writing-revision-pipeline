# Frozen Policy Generation Manifest Writer Production File Writing Design

## 1. Purpose

This document fixes the docs-only design for future production-facing
metadata-only manifest file writing in the frozen policy generation manifest
writer.

This is not an implementation. It does not implement public `--manifest-out`,
artifact writer CLI integration, manifest body generation, or production
readiness. It only defines the responsibilities, safety boundary, CLI/API
shape, output policy, failure behavior, tests, and staging for a later
implementation.

## 2. Current State

- metadata-only no-file runtime exists
- static file writing fixture validator exists and is in release-quality
- isolated write validation exists and is in release-quality
- remote status markers exist for fixture validation and isolated write
  validation
- production-facing runtime file writing does not exist
- public `--manifest-out` is not implemented
- artifact writer CLI integration does not exist
- manifest body generation does not exist

## 3. Design Goal

The future runtime writer should be able to write a metadata-only manifest JSON
document to a safe project-controlled output root when an explicit output
option is provided.

The design goal is to keep all body-bearing and private material suppressed:

- manifest body suppressed
- artifact body payload suppressed
- generated policy body suppressed
- request, pointer, and expected bodies suppressed
- raw rows, logits, private paths, raw learner text, and performance bodies
  excluded from the written file
- stdout and stderr remain body-free
- no-oracle and synthetic-only development boundaries remain visible
- unsafe paths and content leakage fail closed

## 4. Non-Goals

- no real participant data
- no manifest body
- no artifact body payload
- no generated policy body
- no request, pointer, or expected body embedding
- no raw rows
- no logits or probability dumps
- no performance metrics
- no production readiness claim
- no artifact writer CLI integration yet
- no public release claim

## 5. Proposed CLI Surface

Three future CLI shapes are possible:

- Option A: `--manifest-out <path>`
- Option B: `--output-dir <dir>` plus generated filename
- Option C: `--manifest-out <path>` plus `--allow-overwrite`

Recommendation: Option C, but only under strict safe path and metadata-only
constraints.

Proposed future arguments:

- `--manifest-out`
- `--allow-overwrite`
- `--json`
- existing `--request`
- existing `--artifact-result`
- existing `--artifact-body-result`

Important constraints:

- `--manifest-out` must be absent by default
- no-file runtime remains the default
- file writing is opt-in
- file writing must fail closed unless the path is safe
- manifest body mode is not allowed

## 6. Proposed API Surface

Potential future function names are provisional:

- `write_metadata_only_manifest_file(result, output_path, allow_overwrite=False, safe_root=None)`
- `validate_manifest_output_path(path, safe_root=None)`
- `build_metadata_only_manifest_document(...)`

The implementation should happen in a later step. This design only fixes the
expected boundaries and responsibilities.

## 7. Safe Output Root Policy

Allowed production-facing output should be limited to a project-controlled
relative path under `tmp/frozen_policy_generation_manifest/`, or an explicit
relative path that normalizes under that root.

Allowed path properties:

- `.json` extension only
- safe filename
- safe subdirectory
- no parent traversal
- no absolute path
- no user home path
- no cloud or private marker path
- no hidden private directory
- no symlink-sensitive path
- no too-long path
- no overwrite unless `--allow-overwrite` is set

This is more permissive than validator-owned isolated temp roots, but it is
still not arbitrary file writing. A normal project output root is not proof of
production readiness. Public docs must not record real absolute path examples.

## 8. Relation To Isolated Write Validation

Isolated write validation writes only inside validator-owned temporary roots.
Production-facing runtime file writing would write to a project-controlled
output root.

Isolated validation success is prerequisite evidence for path normalization,
metadata-only content checks, stdout/stderr suppression, parse checks, and
cleanup behavior, but it is not sufficient evidence that production-facing
runtime file writing is ready.

Future implementation should reuse the policy concepts without blindly reusing
temp-root-only assumptions.

## 9. Written File Content Policy

Allowed fields:

- `schema_version`
- `result_schema_version`
- `manifest_id`
- `artifact_id`
- `artifact_body_id` or safe reference
- `manifest_writer_mode`
- `validation_reference_count`
- `release_quality_reference_count`
- `safety_flags`
- `count_summary`
- `safe_summary`
- timestamp, only if deterministic or clearly non-private
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

## 10. Stdout/Stderr Policy

- stdout can print body-free metadata summary only
- stdout may include `manifest_file_written=true` and `written_file_count=1`
- stdout must not print the written file body
- stdout must not print an absolute resolved path
- stderr must not print body, payload, private path, absolute path, or raw
  learner text
- errors should use reason codes and safe labels only

## 11. Output Result Summary Policy

Future runtime result summaries should include:

- `manifest_file_written`
- `manifest_output_path_available`
- `written_file_count`
- `manifest_body_available=false`
- `manifest_body_suppressed=true`
- `file_writing_checked=true`
- `output_path_safety_checked=true`
- `content_policy_checked=true`
- `release_quality_ready=false`
- `safe_summary=metadata_only_manifest_writer_result`

Public output must not include an absolute output path. If a path is recorded,
it should be a safe relative path only.

## 12. Overwrite Policy

- default behavior: fail if output exists
- explicit allow behavior: require `--allow-overwrite`
- overwrite must still be inside the safe output root
- overwrite must not follow unsafe symlinks
- result summaries may say an overwrite policy was applied, but must not print
  file content

## 13. Fail-Closed Behavior

The future writer should fail closed for:

- unsafe absolute path
- parent traversal
- outside allowed root
- home path
- cloud or private marker path
- hidden private directory
- non-json extension
- unsafe filename
- path too long
- output exists without allow-overwrite
- symlink-sensitive target
- manifest body requested
- artifact body payload detected
- generated policy body detected
- request, pointer, or expected body leakage
- raw rows, logits, private path, or raw learner text detected
- performance metric body detected
- write failure
- parse failure after write
- forbidden content after write
- cleanup or rollback failure when partial write occurs

## 14. Reason Code Taxonomy

Recognized future reason codes:

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
- `unknown_schema_version`

## 15. Test Plan

Future tests should cover:

- no-file default behavior unchanged
- valid metadata-only file write to safe relative path
- nested safe relative path
- output exists without overwrite fails
- output exists with allow-overwrite succeeds
- unsafe absolute path fails
- parent traversal fails
- outside root fails
- non-json extension fails
- unsafe filename fails
- manifest body request fails
- artifact body payload leakage fails
- request, pointer, or expected body leakage fails
- written file parseable JSON
- written file forbidden field scan
- stdout body-free
- stderr body-free
- no absolute path in public output
- normal output root residue explicitly expected only when file writing
  succeeds
- no effect on isolated write validation harness

## 16. Release-Quality Staging

Do not add this design to release-quality yet.

Proposed future staging:

- Step430 production file writing fixture contract design
- Step431 production file writing fixtures
- Step432 runtime implementation
- Step433 focused tests
- Step434 Makefile / target design if needed
- Step435 wrapper integration design
- Step436 wrapper integration
- Step437 remote marker

Step numbers can be adjusted if smaller implementation slices are needed.

## 17. Relation To Artifact Writer CLI Integration

Artifact writer CLI integration remains separate. A future production manifest
writer may consume safe pointer files only. It should not execute the artifact
writer CLI implicitly, should not execute artifact body generation CLI
implicitly, and should not embed payloads.

## 18. Relation To Public Release Checklist

This design prepares a future implementation. It is not a public release, not
production readiness, not real-data readiness, and not institution-approved
data use.

## 19. Beginner-Friendly Explanation

Isolated write validation proves that the validator can write a tiny safe
metadata document inside a temporary sandbox and clean it up. Production-facing
file writing is different: it would let the runtime write an opt-in file under
a normal project-controlled output root.

That difference is why `--manifest-out` needs careful path rules. Even a
metadata-only file writer should not write to arbitrary locations, overwrite
unexpected files, or print private path information.

The writer should not write bodies because the manifest is meant to be a safe
index of metadata, not a container for learner text, generated policy text,
artifact payloads, request objects, or scoring internals.

Success in this future mode would mean the project-controlled metadata-only
write path behaved as designed. It would still not prove production readiness
or real-data readiness.

## 20. Docs Safety Policy

Docs may include only field names, policy names, count names, and reason code
names.

Docs must not include JSON body examples, written output examples, raw logs,
private path examples, or absolute temp path examples.

## 21. What This Does NOT Do

- does not implement production-facing file writing
- does not implement public `--manifest-out`
- does not modify runtime
- does not modify Makefile, wrapper, or workflow
- does not modify Python code/tests
- does not modify fixtures JSON
- does not connect artifact writer CLI
- does not use real data
- does not compute metrics
- does not prove production readiness

## 22. Next Recommended Steps

- production file writing fixture contract design
- production file writing fixtures
- production file writing fixture validator design
- runtime implementation
- focused tests
- Makefile / Release Quality integration design
- wrapper integration
- remote marker
- keep artifact writer CLI integration separate

## 23. Step429 Status

Step429 creates this docs-only production-facing metadata-only manifest file
writing design. It does not implement production-facing runtime file writing,
public `--manifest-out`, manifest body generation, artifact writer CLI
integration, real-data use, metrics, or production readiness.

## 24. Step430 Fixture Contract Design Status

Step430 adds the docs-only production-facing metadata-only manifest file
writing fixture contract design:

[Frozen policy generation manifest writer production file writing fixture contract design](frozen_policy_generation_manifest_writer_production_file_writing_fixture_contract_design.md).

The production file writing design remains unimplemented. Step430 fixes the
future fixture root, required files, schema versions, case categories, counts,
request/result field names, safe output root policy, overwrite policy,
written file content policy, stdout/stderr safety policy, reason codes,
validator expectations, and runtime expectations. It does not create fixture
JSON, implement production-facing runtime file writing, expose public
`--manifest-out`, change Makefile/wrapper/workflow, change Python code/tests,
connect artifact writer CLI, use real data, compute metrics, or claim
production readiness.

## 25. Step431 Fixture Root Status

Step431 creates the production-facing metadata-only manifest file writing
fixture root:

[Frozen policy generation manifest writer production file writing fixtures](../tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_production_file_writing/README.md).

The root contains 32 synthetic-only, metadata-only cases and 160 JSON files:
8 valid cases, 24 invalid / expected-failure cases, 7 `pass_written` cases,
1 `pass_no_write` case, 12 `usage_error` cases, and 12 `fail_closed` cases.

This does not implement production-facing runtime file writing, public
`--manifest-out`, a validator, Makefile target, release-quality integration,
artifact writer CLI integration, real-data use, metrics, or production
readiness.

## 26. Step432 Fixture Validator Design Status

Step432 adds the docs-only production-facing metadata-only manifest file
writing fixture validator design:

[Frozen policy generation manifest writer production file writing fixture validator design](frozen_policy_generation_manifest_writer_production_file_writing_fixture_validator_design.md).

The validator design is static fixture validation for the Step431 32-case /
160-JSON root. It does not execute runtime file writing, expose public
`--manifest-out`, change Makefile/wrapper/workflow, change Python code/tests,
change fixture JSON, connect artifact writer CLI, use real data, compute
metrics, or claim production readiness.

## 27. Step433 Fixture Validator Implementation Status

Step433 implements the static production-facing metadata-only manifest file
writing fixture validator:

[Production file writing fixture validator module](../python/learner_state/frozen_policy_generation_manifest_writer_production_file_writing_fixture_validation.py).

The validator checks the Step431 production file writing fixture root without
writing files or executing the runtime writer. Production-facing runtime file
writing and public `--manifest-out` remain unimplemented and separate.
