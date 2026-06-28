# Frozen Policy Generation Manifest Writer Production File Writing Fixture Validator Design

## 1. Purpose

This document designs a future static validator for the production-facing
metadata-only manifest file writing fixture root.

It is a design only. It does not implement the validator, does not implement
production-facing runtime file writing, does not expose public
`--manifest-out`, does not add Makefile or release-quality integration, does
not connect artifact writer CLI, does not generate manifest bodies, and does
not claim production readiness.

The validator is intended to check the Step431 fixture root as synthetic-only,
metadata-only, no-oracle fixture metadata. It should not execute the runtime
writer and should not write manifest files.

## 2. Current State

- The production-facing metadata-only manifest file writing design exists.
- The production file writing fixture contract exists.
- The production file writing fixture root exists.
- The fixture root has 32 cases and 160 JSON files.
- The production file writing fixture validator does not exist.
- Production-facing runtime file writing does not exist.
- Public `--manifest-out` is not implemented.
- No Makefile target exists for this validator.
- Release-quality integration does not exist for this validator.
- Artifact writer CLI integration does not exist.

## 3. Proposed Validator Module

Proposed module:

`learner_state.frozen_policy_generation_manifest_writer_production_file_writing_fixture_validation`

The module should statically validate the production file writing fixture
contract. It should not call the manifest writer runtime, should not write a
manifest file, and should not inspect or produce file body examples.

## 4. Proposed CLI

Proposed command:

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer_production_file_writing_fixture_validation`

Proposed arguments:

- `--fixture-root`
- `--fixture-case`
- `--json`
- `--help`

The default fixture root should be:

`tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_production_file_writing`

## 5. Proposed APIs

- `validate_manifest_writer_production_file_writing_fixture_root(fixture_root)`
- `validate_manifest_writer_production_file_writing_fixture_case(case_dir)`
- `summarize_manifest_writer_production_file_writing_fixture_validation(summary, as_json=False)`

Names are provisional and should be refined during implementation only if the
existing validator patterns require it.

## 6. Proposed Dataclasses

- `ManifestWriterProductionFileWritingFixtureValidationSummary`
- `ManifestWriterProductionFileWritingFixtureCaseResult`
- `ManifestWriterProductionFileWritingFixtureValidationError`

The dataclasses should carry only safe metadata, counts, booleans, reason-code
names, and relative fixture identifiers. They should not carry fixture bodies,
request bodies, pointer bodies, expected-result bodies, written file bodies,
private paths, absolute paths, or raw learner text.

## 7. Required Files Per Case

Each case directory must contain exactly the required fixture files:

- `case_metadata.json`
- `manifest_writer_request.json`
- `artifact_writer_result_pointer.json`
- `artifact_body_generation_result_pointer.json`
- `expected_production_file_writing_result.json`

The validator should fail with an input error if a required file is missing,
if an extra body-bearing fixture file is introduced, or if JSON parsing fails.

## 8. Expected Root Summary

The root summary should be body-free and count-only:

- `mode=manifest_writer_production_file_writing_fixture_validation`
- `validation_schema_version=learner_state_frozen_policy_generation_manifest_writer_production_file_writing_validation_v0.1`
- `total_cases=32`
- `valid_cases=8`
- `invalid_cases=24`
- `total_json_files=160`
- `json_files_per_case=5`
- `pass_written_cases=7`
- `pass_no_write_cases=1`
- `usage_error_cases=12`
- `fail_closed_cases=12`
- `matched_cases=32`
- `mismatched_cases=0`
- `input_error_cases=0`
- `content_suppressed=true`
- `manifest_body_suppressed=true`
- `no_written_file_body=true`
- `no_manifest_body=true`
- `no_manifest_json_body=true`
- `no_artifact_body_payload=true`
- `no_generated_policy_body=true`
- `no_request_body=true`
- `no_pointer_body=true`
- `no_expected_body=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_absolute_paths=true`
- `no_performance_claims=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `path_policy_checked=true`
- `overwrite_policy_checked=true`
- `stdout_stderr_policy_checked=true`
- `public_absolute_path_suppressed=true`
- `artifact_writer_cli_integration_checked=true`
- `release_quality_ready=false`

`release_quality_ready=false` means the validator target has not yet been
staged through Makefile and release-quality wrapper integration.

## 9. Validation Phases

Recommended phases:

- Phase A root discovery
- Phase B valid/invalid directory layout
- Phase C required file set
- Phase D JSON parse
- Phase E schema version checks
- Phase F case_id consistency
- Phase G category/status consistency
- Phase H case count aggregation
- Phase I manifest_writer_request contract validation
- Phase J pointer contract validation
- Phase K expected result contract validation
- Phase L safe output root policy validation
- Phase M overwrite policy validation
- Phase N content/body leakage sentinel validation
- Phase O grouped reason code validation
- Phase P stdout/stderr suppression field validation
- Phase Q public absolute path suppression validation
- Phase R artifact writer CLI integration disabled validation
- Phase S summary aggregation

The validator should keep phase failures body-free. It may report the case id,
phase name, safe reason codes, and safe relative fixture path.

## 10. Case Handling

Valid `pass_written` cases must have:

- safe relative `manifest_out`
- `allow_manifest_file_writing=true`
- `include_manifest_body=false`
- `expected_written_file_count=1`
- `expected_manifest_file_written=true`
- `expected_manifest_output_path_available=true`
- body suppression fields set to the safe values

The valid `pass_no_write` case must have:

- no `manifest_out`
- `allow_manifest_file_writing=false`
- `expected_written_file_count=0`
- `expected_manifest_file_written=false`
- `expected_manifest_output_path_available=false`
- body suppression fields set to the safe values

`usage_error` cases must map to unsafe path, overwrite, or symlink reason
codes.

`fail_closed` cases must map to body leakage, write failure, parse failure,
cleanup failure, unsupported artifact writer CLI integration, or unsupported
manifest writer mode reason codes.

Grouped cases must include every required grouped reason code. No case should
include actual raw payloads, real private paths, absolute local paths, absolute
temp paths, raw learner text, or performance metric bodies.

## 11. Safe Output Root Policy Checks

The validator should statically check:

- valid `manifest_out` values are safe relative paths
- valid `manifest_out` values end in `.json`
- valid `manifest_out` values do not contain parent traversal
- valid `manifest_out` values do not contain absolute path markers
- valid `manifest_out` values do not contain home, cloud, or private markers
- valid `manifest_out` values do not contain unsafe filenames
- invalid path cases use sentinel values only
- no actual absolute path or private path appears in fixtures
- no public absolute path is expected in CLI or runtime output

The validator should treat safe relative paths as fixture metadata only. It
should not resolve them into absolute paths in public output.

## 12. Overwrite Policy Checks

The validator should check:

- default behavior is no overwrite
- `output_exists_without_overwrite` maps to `usage_error`
- `overwrite_allowed_existing_file` is valid only with `allow_overwrite=true`
- unsafe symlink path remains invalid even if overwrite flags are present
- overwrite policy is represented as metadata only

The validator should not create existing files to test overwrite behavior.
Runtime behavior belongs to a later implementation stage.

## 13. Pointer Policy Checks

The validator should check:

- `include_body_payload=false`
- `include_raw_rows=false`
- `include_private_paths=false`
- `artifact_writer_cli_integration_requested=false`
- `safe_metadata_reference_id` is present
- no payload or raw row fields are included

The pointer files are safe metadata pointers only. The validator must not run
the artifact writer CLI or artifact body generation CLI.

## 14. Content Policy Checks

The validator should reject malformed fixtures or expected-fail cases that
contain actual forbidden content instead of safe sentinel metadata. Forbidden
content includes:

- manifest body
- manifest JSON body
- written file JSON body
- artifact body payload
- generated policy body
- request body
- pointer body
- expected result body
- raw rows
- logits or probabilities
- private paths
- absolute paths
- raw learner text
- final text
- observed-after text
- gold labels
- scoring feedback payload
- real participant data
- performance metric body

Invalid leakage cases should use sentinel booleans, labels, and reason codes
only. They should not embed the forbidden payload they represent.

## 15. Reason Code Taxonomy

The validator should recognize:

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

Grouped cases:

- `request_pointer_expected_body_leakage` expects `request_body_leakage`,
  `pointer_body_leakage`, and `expected_body_leakage`
- `raw_rows_logits_private_raw_text_leakage` expects `raw_rows_leakage`,
  `logits_dump_leakage`, `private_path_leakage`, `absolute_path_leakage`, and
  `raw_learner_text_leakage`

Reason-code mismatches should produce `mismatched_cases > 0`.

## 16. Safe Selector Rules

Allowed selector examples:

- `valid/minimal_manifest_out_file_written`
- `invalid/unsafe_absolute_manifest_output_path`

Reject:

- empty selector
- absolute selector
- parent traversal
- backslash
- control characters
- selector outside the `valid/` or `invalid/` root

Invalid selector handling should be a usage error, not a fixture mismatch.

## 17. Expected CLI Behavior

- Root validation prints a body-free count-only summary.
- `--json` prints a parseable JSON summary without fixture bodies.
- Single-case validation prints a body-free summary for that case.
- Invalid selector exits with usage error.
- Malformed fixture exits with input error.
- Expected/result mismatch exits with mismatch code.
- Public output must not include written file JSON body or absolute resolved
  output path.

Human output should be concise and should mirror the safe summary fields.
JSON output should contain only safe scalar, list, and count metadata.

## 18. Exit Codes

Proposed exit codes:

- `0` all matched
- `1` internal error
- `2` usage error
- `3` mismatch
- `4` input error / malformed fixture

Exit-code normalization can be revisited during implementation if the existing
validator modules have a more specific local convention.

## 19. Focused Test Plan For Future Implementation

Future tests should cover:

- root validates 32 cases
- total JSON 160
- valid=8 and invalid=24
- category counts 7 / 1 / 12 / 12
- matched=32
- input_error=0
- single valid `pass_written`
- single valid `pass_no_write`
- single invalid usage-error path case
- single invalid fail-closed body case
- overwrite allowed valid case
- output exists without overwrite invalid case
- grouped request/pointer/expected reason case
- grouped raw/logit/private/text reason case
- missing required file
- malformed JSON
- schema mismatch
- case_id mismatch
- category mismatch
- unsafe selector
- body-free human output
- parseable and body-free JSON output
- `public_absolute_path_suppressed=true`
- `release_quality_ready=false`

These tests should not execute production-facing runtime file writing and
should not create manifest files.

## 20. Relation To Runtime Implementation

This validator is static fixture validation. It does not execute the runtime
writer and does not implement public `--manifest-out`.

Future runtime implementation should satisfy these contracts and should have
separate focused runtime tests. Passing this validator will mean the fixture
contract is internally consistent; it will not mean production-facing runtime
file writing works.

## 21. Relation To Isolated Write Validation

Isolated write validation executes a validator-owned temp-root write harness.
The production file writing fixture validator is a static contract validator
for project-controlled output behavior.

Both are separate. Isolated validation success is prerequisite evidence for
write-path safety concepts, but it is not production-facing writing success.

## 22. Relation To Existing Static File Writing Validator

The existing static file writing fixture validator covers broader future
manifest writer file-writing contract metadata. This production file writing
fixture validator is more specific: it focuses on future public
`--manifest-out`, project-controlled output root behavior, overwrite policy,
and production-facing stdout/stderr safety.

The validators should remain separate to avoid ambiguity.

## 23. Relation To Release-Quality

Release-quality integration is not part of this step.

Future staging should be:

1. standalone validator implementation
2. standalone Makefile target design
3. standalone Makefile target implementation
4. release-quality integration design
5. wrapper integration
6. remote/manual status marker

## 24. Relation To Artifact Writer CLI Integration

The validator must confirm `artifact_writer_cli_integration_requested=false`
in the fixture metadata.

It must not execute the artifact writer CLI and must not execute the artifact
body generation CLI. Artifact writer CLI integration remains a separate future
workstream.

## 25. Docs Safety Policy

Docs may include field names, counts, reason-code names, policy names, module
names, command shapes, and safe relative fixture selectors.

Docs must not include JSON bodies, written file contents, raw logs, full job
output, private path examples, absolute path examples, raw learner text,
artifact payload examples, generated policy bodies, or performance metric
bodies.

## 26. What This Does NOT Do

- does not implement the validator
- does not implement runtime file writing
- does not implement public `--manifest-out`
- does not create or change fixtures
- does not modify Python code/tests
- does not modify Makefile, wrapper, or workflow
- does not connect artifact writer CLI
- does not use real data
- does not compute metrics
- does not prove production readiness

## 27. Next Recommended Steps

- Step433 production file writing fixture validator implementation
- Step434 Makefile target design
- Step435 Makefile target implementation
- Step436 release-quality integration design
- Step437 wrapper integration
- Step438 remote marker
- Runtime implementation may be separate after validator/target staging,
  depending on desired project sequencing.

## 28. Step432 Status

Step432 creates this docs-only production-facing metadata-only manifest file
writing fixture validator design. It fixes the proposed module, CLI, APIs,
dataclasses, required files, summary fields, validation phases, case handling,
safe output root checks, overwrite checks, pointer checks, content checks,
reason-code matching, selector rules, exit codes, and future test plan.

Step432 does not implement a validator, production-facing runtime file
writing, public `--manifest-out`, Makefile target, release-quality
integration, artifact writer CLI integration, real-data use, metrics, or
production readiness.

## 29. Step433 Implementation Status

Step433 implements the static production-facing metadata-only manifest file
writing fixture validator module and focused tests:

- [Production file writing fixture validator module](../python/learner_state/frozen_policy_generation_manifest_writer_production_file_writing_fixture_validation.py)
- [Production file writing fixture validator tests](../python/learner_state/tests/test_frozen_policy_generation_manifest_writer_production_file_writing_fixture_validation.py)

The implementation validates the Step431 fixture root as 32 cases and
160 JSON files. It checks required files, JSON parse, schema versions, case ID
consistency, category counts, manifest writer request policy, pointer safe
metadata policy, expected result policy, safe output root policy, overwrite
policy, grouped reason codes, stdout/stderr body-free expectations, public
absolute path suppression, and artifact writer CLI integration disabled
metadata.

The implementation is static fixture validation only. It does not execute the
runtime writer, write manifest files, expose public `--manifest-out`, add a
Makefile target, integrate release-quality, change workflow YAML, change
fixture JSON, connect artifact writer CLI, use real data, compute metrics, or
claim production readiness.

## 30. Step434 Makefile Target Design Status

Step434 adds the docs-only standalone Makefile target design for this
validator:

[Frozen policy generation manifest writer production file writing fixture validator Makefile target design](frozen_policy_generation_manifest_writer_production_file_writing_fixture_validator_makefile_target_design.md).

The design proposes
`check-learner-state-frozen-policy-generation-manifest-writer-production-file-writing-fixtures`
as a thin wrapper around the validator CLI root validation. It fixes target
name, command, help text, expected body-free/count-only output, failure
behavior, release-quality staging, and future implementation tests.

Step434 does not modify Makefile, release-quality wrapper, workflow YAML,
Python code/tests, fixture JSON, runtime writer behavior, public
`--manifest-out`, artifact writer CLI integration, real-data use, metrics, or
production readiness.

## 31. Step435 Makefile Target Implementation Status

Step435 implements the standalone Makefile target proposed in Step434:

`check-learner-state-frozen-policy-generation-manifest-writer-production-file-writing-fixtures`

The target runs the production file writing fixture validator CLI against the
Step431 fixture root and emits only the body-free, count-only human summary by
default. It does not execute the runtime writer, write manifest files, expose
public `--manifest-out`, or call artifact writer CLI.

Release-quality wrapper integration remains a later step. Step435 does not
change workflow YAML, Python code/tests, fixture JSON, runtime writer behavior,
real-data use, metrics, or production readiness.

## 32. Step436 Release-Quality Integration Design Status

Step436 adds the docs-only release-quality integration design for the
standalone production file writing fixture validator target:

[Frozen policy generation manifest writer production file writing fixture release-quality integration design](frozen_policy_generation_manifest_writer_production_file_writing_fixture_release_quality_integration_design.md).

The design fixes the future wrapper label, command, insertion point after
manifest writer isolated write validation, expected body-free output, failure
interpretation, log safety, staging, and non-goals. It does not modify the
release-quality wrapper, workflow YAML, Makefile, Python code/tests, fixture
JSON, runtime writer behavior, public `--manifest-out`, artifact writer CLI
integration, real-data use, metrics, or production readiness.

## 33. Step437 Release-Quality Wrapper Integration Status

Step437 adds the production file writing fixture validator target to the
release-quality wrapper under its own label. The target runs after manifest
writer isolated write validation and before config/scoring smoke checks.

The validator remains static fixture validation only. Step437 does not change
workflow YAML, Makefile, Python code/tests, fixture JSON, runtime writer
behavior, public `--manifest-out`, artifact writer CLI integration, real-data
use, metrics, or production readiness.

## 34. Step438 Remote Run Record Workflow Design Status

Step438 adds the docs-only remote/manual Release Quality run record workflow
for the wrapper integration that now includes this validator:

[Frozen policy generation manifest writer production file writing fixture release-quality remote run record workflow](frozen_policy_generation_manifest_writer_production_file_writing_fixture_release_quality_remote_run_record_workflow.md).

The validator remains static and body-free. Step438 does not create a status
marker, run GitHub Actions, modify workflow YAML, modify the wrapper, modify
Makefile, modify Python code/tests, modify fixture JSON, execute runtime file
writing, write manifest files, expose public `--manifest-out`, connect
artifact writer CLI, use real data, compute metrics, or prove production
readiness.

## 35. Step439 Remote Run Status Marker Status

Step439 creates the public-safe pass-only/count-only remote/manual Release
Quality status marker for the wrapper integration that includes this static
validator:

[Learner-state frozen policy generation manifest writer production file writing fixture release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_production_file_writing_fixture_release_quality_remote_run_status.md).

The validator remains static fixture validation only. Step439 does not modify
workflow YAML, the release-quality wrapper, Makefile, Python code/tests,
fixture JSON, runtime writer behavior, public `--manifest-out`, artifact
writer CLI integration, real-data use, metrics, or production readiness.

## 36. Step441 Runtime File Writing Separation Note

Step441 implements opt-in metadata-only runtime file writing in the manifest
writer runtime. This validator remains static fixture-contract validation for
the production file writing fixture root.

The validator still does not execute the runtime writer, write manifest files,
invoke artifact writer CLI, invoke artifact body generation CLI, use real
data, compute metrics, or prove production readiness. Runtime file writing
evidence and static fixture validation evidence remain separate.

## 37. Step442 Runtime Smoke Target Separation Note

Step442 adds the docs-only design for a future runtime file writing smoke
Makefile target:

[Frozen policy generation manifest writer runtime file writing smoke Makefile target design](frozen_policy_generation_manifest_writer_runtime_file_writing_smoke_makefile_target_design.md).

The future smoke target will execute the runtime and write one target-owned
metadata-only smoke file. This validator remains static fixture validation and
continues not to write files or execute runtime file writing.

## 38. Step443 Runtime Smoke Target Implementation Separation Note

Step443 implements the standalone runtime file writing smoke Makefile target.
That target executes the runtime and writes one target-owned metadata-only
smoke file, then cleans it up.

This static validator remains unchanged and still does not execute runtime
file writing. Static fixture validation evidence and runtime smoke evidence
remain separate.
