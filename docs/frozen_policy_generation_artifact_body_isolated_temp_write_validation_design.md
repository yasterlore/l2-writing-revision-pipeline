# Frozen Policy Generation Artifact Body Isolated Temp Write Validation Design

## 1. Purpose

This document designs future isolated temp write validation for artifact body
file writing.

It is a docs-only design. It is not an implementation, not fixture JSON
creation, not release-quality integration, not a manifest writer, and not
artifact writer CLI integration.

The validation boundary remains synthetic-only, metadata-only, no-oracle, and
body-safe. It is not performance evaluation, real-data readiness, or
production readiness evidence.

## 2. Current State

- `--artifact-body-out` exists on the artifact body generation CLI.
- `--mode safe-metadata` can write a safe metadata artifact body file.
- The fixed safe root is `tmp/artifact_body_generation/`.
- The standalone smoke target exists:
  `check-learner-state-frozen-policy-generation-artifact-body-file-writing-smoke`.
- The smoke target checks one safe valid path with write, parse, safety scan,
  and cleanup.
- The no-write fixture validator target exists:
  `check-learner-state-frozen-policy-generation-artifact-body-file-writing-fixtures`.
- The no-write fixture validator target is in release-quality.
- Isolated temp write validation does not exist.
- Manifest writer does not exist.
- Artifact writer CLI integration does not exist.

## 3. Validation Goal

A future isolated validator should:

- create a temporary isolated safe root
- run multiple valid and invalid file-writing cases
- verify write success, no-write success, usage error, and fail-closed
  outcomes
- parse written files and check allowed keys only
- verify stdout and stderr remain body-free
- verify cleanup and residue count
- return a summary-only / count-only result
- avoid printing or documenting any artifact body payload

The validator should exercise the artifact body generation CLI, not the
artifact writer CLI.

## 4. Proposed Validator Module Name

Candidates:

- `learner_state.frozen_policy_generation_artifact_body_isolated_write_validation`
- `learner_state.frozen_policy_generation_artifact_body_file_write_validation`
- `learner_state.frozen_policy_generation_artifact_body_temp_write_validation`

Recommended:

`learner_state.frozen_policy_generation_artifact_body_isolated_write_validation`

Reasons:

- It clearly describes isolated temp-root file-writing validation.
- It is distinct from the static no-write fixture validator.
- It identifies the artifact body generation CLI file-writing boundary.
- It leaves room for a later Makefile target name that matches the module.

## 5. Proposed CLI Entrypoint

Future command shape:

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_isolated_write_validation`

The first implementation should default to summary-only human output. A later
`--json` option may emit a machine-readable summary, but it must remain
body-free and path-safe.

## 6. Proposed Validation Cases

Valid cases:

- `safe_metadata_nested_relative_output`
- `safe_metadata_flat_relative_output`
- `safe_metadata_output_parent_created`
- `safe_metadata_no_output_no_file`
- `safe_metadata_existing_output_rejected_after_precreate`

Invalid or expected-failure cases:

- `suppressed_default_with_output_usage_error`
- `suppressed_explicit_with_output_usage_error`
- `absolute_output_path_usage_error`
- `home_output_path_usage_error`
- `drive_root_output_path_usage_error`
- `parent_traversal_output_path_usage_error`
- `private_marker_output_path_usage_error`
- `cloud_marker_output_path_usage_error`
- `hidden_private_directory_usage_error`
- `non_json_extension_usage_error`
- `unsafe_filename_usage_error`
- `too_long_path_usage_error`
- `existing_output_without_overwrite_usage_error`
- `generation_fail_closed_no_file`
- `unsafe_body_audit_no_file`
- `manifest_write_attempt_not_supported`
- `generated_policy_body_write_attempt_not_supported`

These cases should be synthetic metadata cases. They should not embed real
learner text, raw rows, logits, private paths, request bodies, pointer bodies,
expected bodies, artifact body payloads, generated policy bodies, or manifest
bodies.

## 7. Expected Result Categories

Future validator case results should use a small category set:

- `pass_written`
- `pass_no_write`
- `usage_error_no_write`
- `fail_closed_no_write`
- `input_error`
- `mismatch`

Invalid cases that match their expected usage-error or fail-closed outcome
should count as matched cases, not validator failures.

## 8. Expected Summary Fields

Future summary fields:

- `mode=isolated_write_validation`
- `validation_schema_version=learner_state_frozen_policy_generation_artifact_body_isolated_write_validation_v0.1`
- `total_cases`
- `valid_cases`
- `invalid_cases`
- `pass_written_cases`
- `pass_no_write_cases`
- `usage_error_cases`
- `fail_closed_cases`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `residue_file_count`
- `body_payload_printed=false`
- `stdout_body_suppressed=true`
- `stderr_body_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_absolute_paths=true`
- `no_manifest_body=true`
- `no_generated_policy_body=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `path_policy_checked=true`
- `file_content_policy_checked=true`
- `cleanup_checked=true`
- `temp_root_isolated=true`
- `release_quality_ready=false`

The summary must not include absolute temp-root paths, full file contents, or
artifact body payloads.

## 9. Written File Content Checks

For cases that write a file, the future validator should check:

- JSON parse succeeds
- allowed keys only
- required notices present
- synthetic notice present
- no-oracle notice present
- non-proof notice present
- safety flags present
- count summary present
- no raw rows
- no logits
- no private paths
- no absolute paths
- no raw learner text
- no request body
- no pointer body
- no expected body
- no generated policy body
- no manifest body
- no performance metric body

The validator may read the written file internally, but it must not print the
file content.

## 10. Stdout/Stderr Checks

The future validator should inspect child process output and confirm:

- no artifact body payload
- no JSON body
- no request body
- no pointer body
- no expected body
- no generated policy body
- no manifest body
- no raw rows
- no logits
- no private path
- no absolute path

Errors should be category-only or safe-summary-only. Default output should
avoid traceback-heavy text unless a developer explicitly requests debug mode
in a later design.

## 11. Cleanup And Residue Checks

Cleanup policy:

- every case uses an isolated temp root
- cleanup runs after each case
- cleanup runs after the full validation run
- no files remain after pass cases
- no files remain after expected-failure cases
- no unrelated tmp files are removed
- cleanup failure becomes `input_error` or fail-closed according to phase
- validator never removes repository files
- validator does not print absolute temp paths in summary output

Residue should be reported as a count, not a path listing.

## 12. Relation To The Smoke Target

The standalone smoke target checks one happy path. It is deliberately small:
write one safe-metadata artifact body, parse it, scan for forbidden field
names, and clean it up.

The isolated validator should check many valid and invalid paths. It should
not replace the smoke target, and the smoke target should remain simple.

A future Makefile target may run the isolated validator after the design and
implementation are stable.

## 13. Relation To The No-Write Fixture Validator

The no-write fixture validator checks static fixture metadata and path/content
policy contracts. It does not write files.

The isolated validator should actually run CLI file writing under an isolated
temp root and verify file/no-file outcomes. The two validators check different
boundaries.

The no-write fixture validator remains in release-quality. The isolated
validator should not be added to release-quality until it is stable as a
standalone check.

## 14. Relation To Release-Quality

Recommended staging:

- implement the isolated validator as a standalone module/CLI first
- create a Makefile target design
- implement a standalone Makefile target
- create release-quality integration design
- integrate the wrapper later
- create a remote/manual status marker only after a successful remote run

This step does not add release-quality integration.

## 15. Relation To Manifest Writer

Manifest writer work remains separate.

The isolated validator should assert:

- `manifest_file_written=false`
- `manifest_body_generated=false`
- no manifest body in any written file

Future manifest validation should be a separate design and fixture family.

## 16. Relation To Artifact Writer CLI

Artifact writer CLI integration remains separate.

The isolated validator should exercise only the artifact body generation CLI.
It should not call the artifact writer CLI, and it should not change artifact
writer runtime targets.

## 17. Docs Safety Policy

Docs may include command shapes, field names, case names, reason categories,
and policy descriptions.

Docs must not include:

- written file body examples
- artifact body JSON examples
- artifact body payload examples
- raw logs
- private path examples
- output payloads
- request bodies
- pointer bodies
- expected bodies
- file write request bodies
- expected file write result bodies
- generated policy bodies
- manifest bodies
- raw rows
- logits
- raw learner text
- real data

## 18. Beginner-Friendly Explanation

Isolated temp validation means running file-writing tests inside a temporary
safe area that is created for the test and cleaned afterward. It gives stronger
coverage than a smoke target because it can check both successful writes and
expected failures.

The smoke target is useful because it is short and checks one known-good path.
It is not enough by itself because it does not cover unsafe paths, suppressed
mode usage errors, overwrite refusal, or content-policy failures.

Valid and invalid cases are separated so that expected failures can be treated
as success for the validator. For example, an unsafe output path should fail
without writing a file; that is the correct result.

stdout and stderr checks matter because the CLI must never print artifact body
payloads while reporting success or failure.

Cleanup and residue checks matter because file-writing validation should not
leave generated files behind or delete unrelated files.

The validator should not enter release-quality immediately. It should first be
implemented, run locally, and gain a standalone Makefile target.

## 19. What This Does Not Do

- does not implement the validator
- does not create fixture JSON
- does not add a Makefile target
- does not add release-quality integration
- does not change workflow YAML
- does not change Python code/tests
- does not change fixture JSON
- does not implement manifest writer
- does not connect artifact writer CLI
- does not use real data
- does not compute metrics
- does not prove production readiness

## 20. Next Recommended Steps

- Step368: isolated temp write validation fixture contract design.
- Step369: isolated temp write validation fixture JSON creation.
- Step370: isolated temp write validator implementation.
- Step371: standalone Makefile target design for the isolated validator.
- Later: Makefile target implementation, release-quality integration design,
  wrapper integration, and remote/manual status marker.

## 21. Step368 Fixture Contract Design Status

Step368 adds the docs-only fixture contract design for future isolated temp
write validation:

[Frozen policy generation artifact body isolated temp write fixture contract design](frozen_policy_generation_artifact_body_isolated_temp_write_fixture_contract_design.md).

The design fixes the proposed fixture root, case directory structure, schema
names, metadata fields, isolated write request fields, expected result fields,
case taxonomy, validation phases, temp-root rules, stdout/stderr rules, and
summary contract. It does not create fixture JSON, implement a validator, add
a Makefile target, add release-quality integration, write manifests, connect
artifact writer CLI, use real data, or compute metrics.

## 22. Step369 Fixture JSON Creation Status

Step369 creates the synthetic-only isolated write validation fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body_isolated_write_validation/`

The root contains 5 valid cases, 17 invalid / expected-failure cases, and 110
JSON files. These fixtures instantiate the Step368 contract only. Step369
does not implement this validator, does not add a Makefile target, does not
add release-quality integration, does not write manifests, and does not
connect the artifact writer CLI.

## 23. Related Documents

- [Frozen policy generation artifact body isolated write validator Makefile target design](frozen_policy_generation_artifact_body_isolated_write_validator_makefile_target_design.md)
- [Frozen policy generation artifact body isolated temp write fixture contract design](frozen_policy_generation_artifact_body_isolated_temp_write_fixture_contract_design.md)
- [Frozen policy generation artifact body isolated write validation fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body_isolated_write_validation/README.md)
- [Frozen policy generation artifact body file writing smoke target design](frozen_policy_generation_artifact_body_file_writing_smoke_target_design.md)
- [Frozen policy generation artifact body file writing implementation final design](frozen_policy_generation_artifact_body_file_writing_implementation_final_design.md)
- [Frozen policy generation artifact body file writing design](frozen_policy_generation_artifact_body_file_writing_design.md)
- [Frozen policy generation artifact body file writing fixture design](frozen_policy_generation_artifact_body_file_writing_fixture_design.md)
- [Frozen policy generation artifact body file writing fixture validator design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_design.md)
- [Frozen policy generation artifact body file writing fixture validator CLI design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_cli_design.md)
- [Frozen policy generation artifact body file writing fixture validator Makefile target design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_makefile_target_design.md)
- [Learner-state frozen policy generation artifact body file writing fixture release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_body_file_writing_fixture_release_quality_remote_run_status.md)
- [Frozen policy generation artifact body file writing fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing/README.md)
- [Public release checklist](public_release_checklist.md)

## 24. Step371 Makefile Target Design Status

Step371 adds the docs-only standalone Makefile target design for the isolated
write validator:

[Frozen policy generation artifact body isolated write validator Makefile target design](frozen_policy_generation_artifact_body_isolated_write_validator_makefile_target_design.md).

The design proposes a future target for running the isolated write validator
CLI against 22 cases and 110 JSON files after module availability is
confirmed. It does not implement the Makefile target, does not add
release-quality integration, does not change workflow YAML, does not change
Python code/tests, does not change fixture JSON, does not write manifests,
does not connect artifact writer CLI, does not use real data, and does not
compute metrics.

## 25. Step372 Availability Reconciliation Status

Step372 restores and confirms the isolated write validator module, CLI, and
tests:

`learner_state.frozen_policy_generation_artifact_body_isolated_write_validation`

The validator executes fixture cases in isolated temp roots and returns
summary-only metadata. The root validation now reports 22 total cases, 22
matched cases, 0 mismatches, 0 input errors, and 0 residue files. Step372
does not add a Makefile target, does not add release-quality integration,
does not change workflow YAML, does not change fixture JSON, does not write
manifests, and does not connect artifact writer CLI.

## 26. Step373 Standalone Makefile Target Status

Step373 adds the standalone Makefile target:

`check-learner-state-frozen-policy-generation-artifact-body-isolated-write-validation`

The target runs the isolated write validator CLI against the 22-case fixture
root and preserves summary-only output, isolated temp execution, cleanup
checking, and `residue_file_count=0`. Step373 does not add release-quality
integration, does not change workflow YAML, does not change Python code/tests,
does not change fixture JSON, does not write manifests, and does not connect
artifact writer CLI.

## 27. Step374 Release-Quality Integration Design Status

Step374 adds the docs-only release-quality integration design:

[Frozen policy generation artifact body isolated write release-quality integration design](frozen_policy_generation_artifact_body_isolated_write_release_quality_integration_design.md).

The design places the standalone isolated write validator target after the
no-write file writing fixture validation target and before config/scoring
smoke checks. It fixes the wrapper label, command, expected summary fields,
failure interpretation, cleanup/no-residue requirement, log safety, and future
status-marker policy. Step374 does not change the wrapper, workflow YAML,
Makefile, Python code/tests, fixture JSON, manifest writer, or artifact writer
CLI integration.

## 28. Step375 Release-Quality Wrapper Integration Status

Step375 adds the isolated write validator standalone target to the
release-quality wrapper after the no-write artifact body file writing fixture
validation target and before config/scoring smoke checks.

The wrapper command is:

`make check-learner-state-frozen-policy-generation-artifact-body-isolated-write-validation`

The integration keeps this validator summary-only and requires zero mismatches,
zero input errors, and `residue_file_count=0`. Step375 does not change workflow
YAML, Makefile targets, Python code/tests, fixture JSON, manifest writer
behavior, artifact writer CLI integration, or performance evaluation.

## 29. Step376 Remote Run Record Workflow Design Status

Step376 adds a docs-only workflow design for recording a future remote/manual
Release Quality run after the isolated write validator is included in the
wrapper:

[Frozen policy generation artifact body isolated write release-quality remote run record workflow](frozen_policy_generation_artifact_body_isolated_write_release_quality_remote_run_record_workflow.md).

The design keeps the future marker pass-only, count-only, metadata-only, and
public-safe. Step376 does not create a status marker, run a remote workflow,
change workflow YAML, change the release-quality wrapper, change Makefile,
change Python code/tests, change fixture JSON, implement manifest writer, or
connect artifact writer CLI.

## 30. Step377 Remote Status Marker Status

Step377 creates the public-safe remote/manual Release Quality status marker
for the isolated write validator wrapper integration:

[Learner-state frozen policy generation artifact body isolated write release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_body_isolated_write_release_quality_remote_run_status.md).

The marker records the 22-case isolated write validation result as
pass-only/count-only metadata with `matched_cases=22`,
`mismatched_cases=0`, `input_error_cases=0`, and `residue_file_count=0`.
It does not copy raw logs, fixture bodies, written file content, artifact
body payloads, generated policy bodies, manifest bodies, private paths,
absolute temp paths, raw learner text, or real participant data.
