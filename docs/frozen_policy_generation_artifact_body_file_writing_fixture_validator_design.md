# Frozen Policy Generation Artifact Body File Writing Fixture Validator Design

## 1. Purpose

This document designs a future validator for the artifact body file writing
fixture root.

It is a docs-only validator design. It does not implement the validator, does
not implement artifact body file writing, does not add a CLI output option,
does not implement a manifest writer, does not connect artifact writer CLI,
and does not add release-quality integration.

The validator design stays synthetic-only, metadata-only, and no-oracle. It
uses safe case IDs, field names, reason-code names, and count-only summaries.
It must not print fixture JSON bodies, artifact body payloads, request
bodies, pointer bodies, expected bodies, manifest bodies, raw rows, logits,
private paths, learner text, real participant data, or metrics.

## 2. Current State

- The file writing fixture root exists.
- 29 cases exist.
- 116 JSON files exist.
- Each case has 4 JSON files.
- JSON parse checks pass.
- Validator implementation does not exist.
- Path-policy validator does not exist.
- Isolated temp write validator does not exist.
- `--artifact-body-out` does not exist.
- Artifact body file writing does not exist.
- Manifest writer does not exist.

## 3. Proposed Validator Module Name

Candidate module names:

| Candidate | Notes |
| --- | --- |
| `learner_state.frozen_policy_generation_artifact_body_file_writing_fixture_validation` | Long, but mirrors existing learner-state fixture validator naming and states the full boundary. |
| `learner_state.artifact_body_file_writing_fixture_validation` | Shorter, but loses the frozen policy generation namespace. |
| `learner_state.frozen_policy_artifact_body_file_writing_validation` | Shorter than the first option, but less aligned with existing artifact body fixture validator names. |

Recommended:

`learner_state.frozen_policy_generation_artifact_body_file_writing_fixture_validation`

Reasoning:

- It aligns with existing artifact body fixture validator naming.
- It explicitly states frozen policy generation, artifact body, file writing,
  and fixture validation.
- It will be easy to map to a future Makefile target name.

## 4. Proposed CLI Entrypoint

Future command:

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_file_writing_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing`

The initial CLI should validate the fixture root and print only a safe
summary. It should not print JSON body contents.

## 5. Proposed Output Mode

Initial output should be a human safe summary:

- `mode=fixture_root`
- `validation_schema_version=learner_state_frozen_policy_generation_artifact_body_file_writing_fixture_validation_v0.1`
- `total_cases=29`
- `valid_cases=5`
- `invalid_cases=24`
- `matched_cases=29`
- `mismatched_cases=0`
- `input_error_cases=0`
- `reason_code_counts=count-only`
- `content_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `path_policy_checked=true`
- `body_content_policy_checked=true`
- `stdout_body_suppression_checked=true`
- `manifest_absence_checked=true`
- `file_writing_isolated=false` for a static/no-write implementation phase

Later isolated temp write validation may set `file_writing_isolated=true`.

## 6. Validation Phases

### Phase A: Static Fixture Contract Validation

- Count case directories.
- Check required file existence.
- Parse JSON.
- Validate schema versions.
- Validate `case_id` consistency.
- Validate expected result fields.
- Check that forbidden sentinels appear only in intended invalid cases.
- Check no actual private paths.
- Check no raw learner text.
- Check no raw rows.
- Check no logits.
- Check no manifest body.
- Check no artifact body payload.

### Phase B: Path-Policy Validation Without Writing

- Normalize output path.
- Reject absolute path.
- Reject home path.
- Reject drive root.
- Reject parent traversal.
- Reject private cloud marker.
- Reject hidden private dirs.
- Enforce `.json` extension.
- Enforce safe character set.
- Enforce path length.
- Enforce allowed root.
- Verify overwrite policy.

### Phase C: Isolated Temp Write Simulation Or Execution

- Use an isolated temporary directory only.
- Never write into repository fixture directories.
- Do not use a production output path.
- If a future generator supports file writing, run only safe temp paths.
- Validate files exist only for expected valid write cases.
- Validate no files exist for invalid cases.
- Validate no manifest file exists.
- Validate no extra outputs exist.

### Phase D: File Content Policy Validation

- Parse the written body file.
- Allow only approved top-level keys.
- Require notices.
- Require schema and body status.
- Require zero forbidden counts.
- Reject request body content.
- Reject pointer body content.
- Reject expected body content.
- Reject generated policy body content.
- Reject manifest body content.
- Reject raw rows.
- Reject logits.
- Reject private paths.
- Reject raw learner text.
- Reject performance metric body content.

### Phase E: Stdout/Stderr Safety Validation

- Require summary-only stdout.
- Reject printed body payload.
- Reject printed request or pointer bodies.
- Reject printed private paths.
- Reject printed raw text.
- Reject printed manifest body.

## 7. Expected Status Mapping

- Valid cases should have `expected_status=pass`.
- Invalid cases should have `expected_status=fail_closed` or `usage_error`
  depending on case type.
- Malformed fixtures should produce `input_error`.
- Actual/expected disagreement should increment `mismatched_cases`.
- Validator internal exceptions should produce a fail-safe summary rather
  than traceback-heavy output.

## 8. Reason Code Taxonomy

Recommended reason codes:

- `unsafe_absolute_output_path`
- `unsafe_home_output_path`
- `unsafe_parent_traversal_output_path`
- `unsafe_private_path_marker`
- `unsafe_private_cloud_marker`
- `output_path_outside_allowed_root`
- `unsafe_path_after_normalization`
- `suppressed_mode_output_not_allowed`
- `fail_closed_generation_output_not_allowed`
- `unsafe_body_audit_output_not_allowed`
- `manifest_output_not_allowed`
- `generated_policy_body_output_not_allowed`
- `request_body_leakage`
- `pointer_body_leakage`
- `expected_body_leakage`
- `raw_rows_leakage`
- `logits_dump_leakage`
- `private_path_leakage`
- `raw_learner_text_leakage`
- `performance_metric_body_leakage`
- `missing_synthetic_notice`
- `missing_no_oracle_notice`
- `missing_non_proof_notice`
- `overwrite_policy_missing`
- `malformed_fixture`
- `schema_version_unknown`
- `required_file_missing`
- `case_id_mismatch`

Reason codes should be safe names only. They should not include payloads,
paths, rows, or learner text.

## 9. Validator Safety Constraints

The validator must:

- not use real data
- not read outside the fixture root except an isolated temp directory when
  enabled
- not write outside an isolated temp directory
- not print JSON body contents
- not print artifact body payloads
- not print raw fixture file contents
- not print absolute local paths
- report safe relative case IDs only
- not follow symlinks outside a safe root
- clean isolated temp directories where appropriate
- fail closed on malformed input

## 10. Proposed Future Makefile Target

Future target:

`check-learner-state-frozen-policy-generation-artifact-body-file-writing-fixtures`

Recommended initial target behavior: static fixture contract validation plus
path-policy no-write validation. Isolated temp write validation should be
added later after CLI file writing exists.

## 11. Relation To Future CLI File Writing Implementation

The validator can start with static validation before `--artifact-body-out`
exists. Later phases can be enabled after file writing implementation exists.

Fixture contracts should remain stable, and no implementation dependency
should force raw body printing.

## 12. Relation To Existing Artifact Body Fixture Validator

The existing artifact body fixture validator checks the body generation
boundary. This new validator checks the file writing and path-output
boundary.

It should use a similar summary style while keeping fixture roots separate.
The existing validator should not be modified in this step.

## 13. Relation To Release-Quality

Do not add this validator to release-quality yet.

Recommended staging:

- Implement validator.
- Add standalone Makefile target.
- Write docs-only release-quality integration design.
- Integrate wrapper.
- Record a remote/manual status marker after success.

## 14. Docs Safety Policy

Docs should include reason-code names and field names only.

Docs must not include fixture JSON bodies, artifact body payload examples,
private path examples, raw logs, raw rows, logits, real data, raw learner
text, manifest bodies, generated policy bodies, or metric bodies.

## 15. Beginner-Friendly Explanation

A validator is a checker. It reads fixture contracts and decides whether the
actual behavior matches the expected safe result.

A fixture validator is useful before file writing exists because it locks down
what the future implementation must prove: safe paths, safe content,
summary-only output, no manifest writing, and no extra files.

Path-policy validation asks whether the destination is safe. Content-policy
validation asks whether the body content is safe. Both must pass.

An isolated temp directory is a short-lived, controlled folder used during a
test so the validator never writes into project fixtures or private
locations.

Designing the validator before implementation keeps the first code pass small
and makes fail-closed behavior explicit.

## 16. What This Does NOT Do

- Does not implement the validator.
- Does not write artifact body files.
- Does not add a CLI option.
- Does not change Makefile.
- Does not change release-quality.
- Does not change workflow YAML.
- Does not change Python code or tests.
- Does not change fixture JSON.
- Does not use real data.
- Does not compute metrics.

## 17. Next Recommended Steps

- Step354: static validator implementation.
- Step355: CLI design.
- Step356: CLI implementation.
- Step357: Makefile target design.
- Step358: Makefile target implementation.
- Step359: release-quality integration design.
- Later: isolated temp write validation after CLI file writing exists.
- Later: wrapper integration and remote/manual status marker.

## 18. Step354 Static Validator Implementation Status

Step354 implements the static no-write validator module:

`python/learner_state/frozen_policy_generation_artifact_body_file_writing_fixture_validation.py`

It also adds unit tests:

`python/learner_state/tests/test_frozen_policy_generation_artifact_body_file_writing_fixture_validation.py`

The implementation validates fixture shape, JSON parsing, schema versions,
case ID consistency, expected result fields, expected valid/invalid status,
path-policy metadata, content-policy metadata, expected reason codes, and
safe summary output. It does not write files, does not create temp output
directories, does not implement `--artifact-body-out`, does not generate or
write manifest bodies, does not connect artifact writer CLI, does not change
Makefile, does not change release-quality, does not change workflow YAML,
does not use real data, and does not compute metrics.

## 19. Step355 Fixture Validator CLI Design Status

Step355 designs a future CLI for safely running the static no-write validator:

[Frozen policy generation artifact body file writing fixture validator CLI design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_cli_design.md).

The CLI design defines the module entrypoint, `--fixture-root`,
`--fixture-case`, `--json`, safe default behavior, exit-code interpretation,
human summary fields, JSON summary boundaries, test plan, Makefile staging,
release-quality staging, and future file-writing separation. It does not
implement a CLI, does not add a Makefile target, does not write files, does
not create temp outputs, does not implement `--artifact-body-out`, does not
change release-quality, does not use real data, and does not compute metrics.

## 20. Step356 Fixture Validator CLI Implementation Status

Step356 implements the safe no-write CLI entrypoint in the existing validator
module:

`python/learner_state/frozen_policy_generation_artifact_body_file_writing_fixture_validation.py`

The CLI validates the default fixture root, a custom fixture root, or one
safe relative fixture case selector. It emits body-free human or JSON
summaries only. It rejects unsafe `--fixture-case` selectors, does not print
fixture bodies, does not print artifact body payloads, does not write files,
does not create temp output directories, does not implement
`--artifact-body-out`, does not change Makefile, does not change
release-quality, does not change workflow YAML, does not use real data, and
does not compute metrics.

Step356 also adds CLI tests:

`python/learner_state/tests/test_frozen_policy_generation_artifact_body_file_writing_fixture_validation_cli.py`

## 21. Step357 Makefile Target Design Status

Step357 designs a future standalone Makefile target for running the safe
no-write CLI:

[Frozen policy generation artifact body file writing fixture validator Makefile target design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_makefile_target_design.md).

The design proposes target naming, command shape, help text, expected
behavior, output safety, Makefile implementation notes, relation to existing
targets, release-quality staging, and future tests. It does not implement a
Makefile target, does not change release-quality, does not change workflow
YAML, does not write files, does not implement `--artifact-body-out`, does
not use real data, and does not compute metrics.

## 22. Related Documents

- [Frozen policy generation artifact body file writing fixture validator CLI design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_cli_design.md)
- [Frozen policy generation artifact body file writing fixture validator Makefile target design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_makefile_target_design.md)
- [Frozen policy generation artifact body file writing fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing/README.md)
- [Frozen policy generation artifact body file writing fixture design](frozen_policy_generation_artifact_body_file_writing_fixture_design.md)
- [Frozen policy generation artifact body file writing design](frozen_policy_generation_artifact_body_file_writing_design.md)
- [Frozen policy generation artifact body generation design](frozen_policy_generation_artifact_body_generation_design.md)
- [Frozen policy generation artifact body generation CLI design](frozen_policy_generation_artifact_body_generation_cli_design.md)
- [Public release checklist](public_release_checklist.md)
