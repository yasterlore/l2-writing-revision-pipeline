# Frozen Policy Generation Artifact Body File Writing Fixture Design

## 1. Purpose

This document designs future fixtures and path-policy checks for artifact
body file writing.

It is a docs-only fixture and path-policy design. It does not create fixture
files, does not implement file writing, does not add a CLI output option,
does not implement a manifest writer, does not connect artifact writer CLI,
and does not add release-quality integration.

The design stays synthetic-only, metadata-only, and no-oracle. It describes
fixture case names, expected result fields, path-policy dimensions, and
content-policy dimensions without including request bodies, pointer bodies,
expected bodies, artifact body payload examples, manifest bodies, raw rows,
logits, private paths, learner text, real participant data, or metrics.

## 2. Current State

- The artifact body generation API exists.
- The artifact body generation CLI exists.
- Suppressed and safe-metadata CLI modes exist.
- Suppressed and safe-metadata Makefile targets exist.
- Both targets are included in release-quality.
- Remote/manual status markers exist for suppressed and safe-metadata smoke.
- The artifact body file writing design exists.
- Artifact body file writing fixtures do not exist.
- A path-policy validator does not exist.
- `--artifact-body-out` does not exist.
- Manifest writer does not exist.
- Artifact writer CLI integration does not exist.

## 3. Proposed Future Fixture Root

Recommended future fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing/`

This root should be separate from the existing artifact body fixture root so
body generation boundary tests and file-output boundary tests remain easy to
reason about.

## 4. Proposed Fixture Structure

Each future case should have files with these meanings:

- `artifact_body_request.json`: synthetic metadata request used to generate
  the candidate body.
- `artifact_writer_result_pointer.json`: synthetic metadata pointer used by
  the generation API.
- `file_write_request.json` or `artifact_body_output_pointer.json`: metadata
  describing the intended output path policy and write request.
- `expected_file_write_result.json`: expected safe result metadata.

This document intentionally does not provide JSON bodies. It only defines the
file names and their roles.

## 5. Valid Fixture Cases

Recommended valid cases:

- `valid_safe_metadata_relative_tmp_output`: safe-metadata body with a safe
  relative temporary output path; expected file writing success.
- `valid_safe_metadata_nested_tmp_output`: safe nested relative path; expected
  parent creation only if the future policy permits it.
- `valid_safe_metadata_no_output_path`: no output path; expected no file
  writing.
- `valid_safe_metadata_explicit_no_overwrite`: safe path with overwrite
  disabled; expected writing only when the target does not already exist.
- `valid_safe_metadata_summary_only_stdout`: write succeeds but stdout and
  stderr remain body-free.

These cases should use only synthetic metadata and controlled temporary output
roots.

## 6. Invalid Fixture Cases

Recommended invalid cases:

- `invalid_suppressed_mode_with_output_path`
- `invalid_fail_closed_generation_with_output_path`
- `invalid_unsafe_body_audit_with_output_path`
- `invalid_absolute_output_path`
- `invalid_home_output_path`
- `invalid_parent_traversal_output_path`
- `invalid_private_path_marker_output_path`
- `invalid_dropbox_or_cloud_path_output_path`
- `invalid_manifest_file_output_attempt`
- `invalid_generated_policy_body_output_attempt`
- `invalid_request_body_leakage_in_file`
- `invalid_pointer_body_leakage_in_file`
- `invalid_expected_body_leakage_in_file`
- `invalid_raw_rows_in_file`
- `invalid_logits_dump_in_file`
- `invalid_private_path_in_file`
- `invalid_raw_learner_text_in_file`
- `invalid_performance_metric_body_in_file`
- `invalid_missing_synthetic_notice`
- `invalid_missing_no_oracle_notice`
- `invalid_missing_non_proof_notice`
- `invalid_overwrite_without_policy`
- `invalid_output_path_outside_allowed_root`
- `invalid_output_path_with_absolute_segment_after_normalization`

Invalid cases should assert fail-closed behavior and should never require
real data or private paths.

## 7. Path-Policy Dimensions

Future path-policy checks should cover:

- relative path required
- allowed root required
- no absolute path
- no home path
- no drive root
- no parent traversal
- no symlink escape if the future implementation handles symlinks
- no private cloud marker
- no hidden private directories
- no overwrite unless explicit policy
- extension policy, likely `.json`
- filename safe character set
- path length limit
- created parent directory policy
- temporary-output-only initial test policy

The validator should normalize paths before final checks and should reject
paths that become unsafe after normalization.

## 8. Artifact Body Content Policy Dimensions

Future content-policy checks should cover:

- allowed top-level keys
- required notices
- required schema version
- required body status
- required synthetic-only notice
- required no-oracle notice
- required non-proof notice
- no request body
- no pointer body
- no expected body
- no generated policy body
- no manifest body
- no raw rows
- no logits
- no private paths
- no performance metric body
- no raw learner text
- count fields match zero leakage

Path safety and content safety should both be required for a successful write.

## 9. Expected Result Schema

Future expected results should include fields such as:

- `case_id`
- `expected_status`
- `expected_reason_codes`
- `expected_failed_checks`
- `expected_file_written`
- `expected_file_exists`
- `expected_summary_only_stdout`
- `expected_body_payload_not_printed`
- `expected_manifest_file_written`
- `expected_output_path_safety_checked`
- `expected_artifact_body_audit_checked`
- `expected_allowed_key_check`
- `expected_forbidden_key_check`
- `expected_zero_forbidden_counts`

Expected results should remain metadata-only and should not include the body
payload, request body, pointer body, manifest body, raw rows, logits, private
paths, or learner text.

## 10. Future Validator Design

A future validator should:

- avoid writing files by default, or write only inside an isolated temporary
  directory during controlled validation
- validate expected outcomes
- fail closed on malformed fixtures
- validate path normalization
- validate file content if writing is enabled in an isolated temporary
  directory
- validate stdout and stderr remain body-free
- validate no manifest file is written
- validate no extra output files are created
- validate summaries contain no private paths

The validator should report safe reason-code names and counts only.

## 11. Future Makefile Target Design

Future target candidate:

`check-learner-state-frozen-policy-generation-artifact-body-file-writing-fixtures`

This target is not implemented in this step. It should be designed only after
fixture JSON and a validator boundary are ready.

## 12. Relation To Existing Artifact Body Fixtures

Existing artifact body fixtures validate the body generation boundary. The
new file writing fixtures should validate the path and file-output boundary.

The two fixture groups should not be mixed initially. The existing
safe-metadata synthetic request and pointer may be reused by reference, but
file-writing expected results should live in the separate file-writing root.
Docs should not duplicate request or pointer bodies.

## 13. Relation To Artifact Writer Fixtures

Artifact writer fixtures remain metadata-only and body-free.

File writing fixtures should not change the artifact writer fixture contract.
Artifact writer CLI integration remains separate future work.

## 14. Relation To Manifest Writer

File writing fixtures should assert `manifest_file_written=false`.

Manifest body output attempts should fail closed. Manifest writer fixtures
are a future separate group and should have their own suppression, path, and
content policies.

## 15. Relation To Release-Quality

File writing fixtures should not be added to release-quality initially.

Recommended staging:

- local validator first
- standalone Makefile target after validator stabilization
- release-quality design after standalone target success
- wrapper integration after design approval
- remote/manual status marker after remote success

## 16. Docs Safety Policy

Docs should use descriptive fixture case names and policy field names only.

Docs must not include fixture JSON examples, artifact body payload examples,
private path examples, raw logs, raw rows, logits, raw learner text, real
data, or metric bodies.

## 17. Beginner-Friendly Explanation

Fixture design comes before implementation because file writing has two
different safety surfaces: the content being written and the place it is
written to. Designing fixtures first makes those expectations explicit before
code exists.

Path policy is the rule set for deciding whether an output path is safe. A
path can be risky if it escapes the intended output root, overwrites an
unexpected file, reveals private filesystem structure, or points into a
private sync location.

Body content policy is separate from path policy because a safe path does not
make unsafe content safe, and safe content does not make an unsafe path safe.
Both checks need to pass.

Manifest writer is separate because manifests describe files and references.
That contract needs its own fixture root and audit rules.

## 18. What This Does NOT Do

- Does not create fixtures.
- Does not implement a validator.
- Does not implement file writing.
- Does not add a CLI option.
- Does not write artifact bodies.
- Does not write manifests.
- Does not change release-quality.
- Does not change workflow YAML.
- Does not change Makefile.
- Does not change Python code or tests.
- Does not change fixture JSON.
- Does not use real data.
- Does not compute metrics.

## 19. Next Recommended Steps

- Step352: file writing fixture JSON creation.
- Step353: file writing fixture validator design or implementation.
- Step354: CLI file writing implementation.
- Later: standalone Makefile target design and implementation.
- Later: release-quality wrapper integration.
- Later: remote/manual status marker.

Manifest writer and artifact writer CLI integration should remain separate
tracks.

## 20. Step352 Fixture Creation Status

Step352 creates the future artifact body file writing fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing/`

The root contains 29 synthetic-only metadata cases: 5 valid cases and 24
invalid cases. Each case has `artifact_body_request.json`,
`artifact_writer_result_pointer.json`, `file_write_request.json`, and
`expected_file_write_result.json`.

Step352 does not implement a validator, does not implement file writing,
does not add a CLI option, does not write artifact bodies or manifests, does
not connect artifact writer CLI, does not change release-quality, does not
use real data, and does not compute metrics.

## 21. Step353 Validator Design Status

Step353 designs a future validator for this fixture root:

[Frozen policy generation artifact body file writing fixture validator design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_design.md).

The validator design defines static fixture validation, path-policy no-write
validation, later isolated temp write validation, content-policy validation,
stdout/stderr safety validation, reason-code taxonomy, and fail-closed safety
constraints. It does not implement the validator, does not change fixture
JSON, does not add a CLI option, does not write artifacts or manifests, does
not change release-quality, does not use real data, and does not compute
metrics.

## 22. Step354 Static Validator Implementation Status

Step354 implements the static no-write validator module:

`python/learner_state/frozen_policy_generation_artifact_body_file_writing_fixture_validation.py`

The validator reads this fixture root, validates required files, JSON parse,
schema versions, case IDs, expected result fields, valid/invalid expected
status, path-policy metadata, content-policy metadata, expected reason codes,
and safe summaries. It does not implement file writing, does not add a CLI
option, does not write artifacts or manifests, does not change Makefile,
does not change release-quality, does not use real data, and does not
compute metrics.

## 23. Step358 Makefile Target Implementation Status

Step358 adds a standalone Makefile target for the safe no-write fixture
validator CLI:

`check-learner-state-frozen-policy-generation-artifact-body-file-writing-fixtures`

The target validates this fixture root through the existing CLI and emits
summary-only metadata. It does not add release-quality integration, does not
write artifact body files, does not create temp output directories, does not
implement `--artifact-body-out`, does not write manifests, does not change
fixture JSON, does not use real data, and does not compute metrics.

## 24. Step359 Release-Quality Integration Design Status

Step359 designs future release-quality wrapper integration for the
standalone no-write fixture validator target:

[Frozen policy generation artifact body file writing fixture release-quality integration design](frozen_policy_generation_artifact_body_file_writing_fixture_release_quality_integration_design.md).

The fixture root remains unchanged. The design does not add the target to
release-quality, does not write files, does not create temp outputs, does
not implement `--artifact-body-out`, does not write manifests, does not use
real data, and does not compute metrics.

## 25. Step360 Release-Quality Wrapper Integration Status

Step360 adds the no-write fixture validator target to the release-quality
wrapper. The fixture root remains unchanged and the target still validates
metadata-only fixture contracts without writing files. Step360 does not
change fixture JSON, does not implement file writing, does not implement
`--artifact-body-out`, does not run isolated temp write validation, does not
write manifests, does not use real data, and does not compute metrics.

## 26. Step361 Remote Run Record Workflow Design Status

Step361 adds a docs-only remote/manual Release Quality run record workflow:

[Frozen policy generation artifact body file writing fixture release-quality remote run record workflow](frozen_policy_generation_artifact_body_file_writing_fixture_release_quality_remote_run_record_workflow.md).

It defines a future status marker path and a pass-only/count-only recording
policy for the file writing fixture validation target. It does not create
the status marker and does not change this fixture root.

## 27. Related Documents

- [Frozen policy generation artifact body isolated temp write validation design](frozen_policy_generation_artifact_body_isolated_temp_write_validation_design.md)
- [Frozen policy generation artifact body file writing fixture validator CLI design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_cli_design.md)
- [Frozen policy generation artifact body file writing fixture validator Makefile target design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_makefile_target_design.md)
- [Frozen policy generation artifact body file writing fixture release-quality integration design](frozen_policy_generation_artifact_body_file_writing_fixture_release_quality_integration_design.md)
- [Frozen policy generation artifact body file writing fixture release-quality remote run record workflow](frozen_policy_generation_artifact_body_file_writing_fixture_release_quality_remote_run_record_workflow.md)
- [Frozen policy generation artifact body file writing fixture validator design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_design.md)
- [Frozen policy generation artifact body file writing smoke target design](frozen_policy_generation_artifact_body_file_writing_smoke_target_design.md)
- [Frozen policy generation artifact body file writing fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing/README.md)
- [Frozen policy generation artifact body file writing design](frozen_policy_generation_artifact_body_file_writing_design.md)
- [Frozen policy generation artifact body generation design](frozen_policy_generation_artifact_body_generation_design.md)
- [Frozen policy generation artifact body generation CLI design](frozen_policy_generation_artifact_body_generation_cli_design.md)
- [Frozen policy generation artifact body fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body/README.md)
- [Learner-state frozen policy generation artifact body safe-metadata release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_body_safe_metadata_release_quality_remote_run_status.md)
- [Public release checklist](public_release_checklist.md)

## 28. Step362 Remote Run Status Marker Status

Step362 creates the public-safe remote/manual Release Quality status marker:

[Learner-state frozen policy generation artifact body file writing fixture release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_body_file_writing_fixture_release_quality_remote_run_status.md).

The marker records that the fixture root's no-write validator target passed
through Release Quality. It records only metadata and counts; it does not
copy fixture bodies, implement file writing, write artifact files, write
manifest files, use real data, compute metrics, or claim production
readiness.

## 29. Step363 Final Implementation Design Status

Step363 adds the docs-only final implementation design:

[Frozen policy generation artifact body file writing implementation final design](frozen_policy_generation_artifact_body_file_writing_implementation_final_design.md).

The final design uses this fixture root as the policy background for a
future safe-metadata-only `--artifact-body-out` implementation. It does not
change fixture JSON, implement file writing, run isolated temp write
validation, write manifests, use real data, compute metrics, or claim
production readiness.

## 30. Step365 Smoke Target Design Status

Step365 adds a docs-only standalone smoke target design:

[Frozen policy generation artifact body file writing smoke target design](frozen_policy_generation_artifact_body_file_writing_smoke_target_design.md).

The design does not change this fixture root. It keeps fixture validation
separate from the future write smoke: fixture validation remains no-write,
while the future smoke target should write one safe-metadata file, parse it,
and clean it up under the fixed safe root.

## 31. Step367 Isolated Temp Write Validation Design Status

Step367 adds the docs-only isolated temp write validation design:

[Frozen policy generation artifact body isolated temp write validation design](frozen_policy_generation_artifact_body_isolated_temp_write_validation_design.md).

The future isolated validator should exercise multiple valid and invalid
write cases under a temp root. This fixture root remains unchanged and remains
the static no-write contract fixture root.

## 32. Step368 Isolated Temp Write Fixture Contract Design Status

Step368 adds the docs-only fixture contract design:

[Frozen policy generation artifact body isolated temp write fixture contract design](frozen_policy_generation_artifact_body_isolated_temp_write_fixture_contract_design.md).

That future fixture root should be separate from this no-write fixture root.
This document's fixture root remains unchanged, and no fixture JSON is created
or modified in Step368.

## 33. Step369 Isolated Temp Write Fixture JSON Creation Status

Step369 creates that separate future isolated write validation fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_isolated_write_validation/`

It contains 5 valid cases, 17 invalid / expected-failure cases, and 110 JSON
files. This no-write fixture root remains unchanged and continues to validate
static file-writing/path-policy contracts separately.
