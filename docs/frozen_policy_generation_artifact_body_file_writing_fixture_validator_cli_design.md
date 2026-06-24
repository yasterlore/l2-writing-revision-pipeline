# Frozen Policy Generation Artifact Body File Writing Fixture Validator CLI Design

## 1. Purpose

This document designs a future CLI for the static no-write artifact body file
writing fixture validator.

It is a docs-only CLI design. It does not implement the CLI, does not add a
Makefile target, does not implement artifact body file writing, does not add
an output file option, does not implement `--artifact-body-out`, does not run
isolated temp write validation, does not implement a manifest writer, does not
connect artifact writer CLI, and does not add release-quality integration.

The design remains synthetic-only, metadata-only, and no-oracle. It uses safe
field names, case IDs, counts, statuses, and reason-code names only.

## 2. Current State

- The static validator module exists.
- Validator APIs exist:
  - `validate_fixture_root(fixture_root)`
  - `validate_fixture_case(case_dir, expected_kind=None)`
  - `summarize_file_writing_fixture_validation(summary)`
- The fixture root exists with 29 cases and 116 JSON files.
- CLI does not exist.
- Makefile target does not exist.
- Release-quality integration does not exist.
- Artifact body file writing does not exist.
- `--artifact-body-out` does not exist.
- Isolated temp write validation does not exist.

## 3. Proposed CLI Entrypoint

Recommended future entrypoint:

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_file_writing_fixture_validation`

The module already owns the static validation API, so the CLI should be a
thin wrapper around that API. It should not add file writing behavior.

## 4. Proposed CLI Arguments

### `--fixture-root`

- Optional.
- Default:
  `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing`
- Validates the full fixture root.
- Should accept a repository-relative fixture root only.
- Should not print the root as an absolute local path.

### `--fixture-case`

- Optional.
- Selects one case by safe relative case ID.
- Example shape in prose: a `valid/` or `invalid/` case selector under the
  file writing fixture root.
- Should not accept absolute paths.
- Should not allow parent traversal.
- Should not follow a selector outside the fixture root.

### `--json`

- Optional.
- Emits a machine-readable safe summary.
- Must not include fixture JSON bodies, request bodies, pointer bodies,
  expected result bodies, file write request bodies, artifact body payloads,
  raw rows, logits, private paths, raw learner text, manifest bodies, or
  absolute local paths.

### `--help`

- Prints usage and argument descriptions.
- Must not include fixture JSON bodies or payload examples.

## 5. Proposed Default Behavior

With no arguments, the future CLI should validate the default fixture root
and print a human safe summary.

Default behavior:

- Validate the default fixture root.
- Emit summary-only human output.
- Do not write files.
- Do not create temp directories.
- Do not print artifact body payloads.
- Do not print raw fixture body contents.
- Do not print absolute local paths.
- Exit 0 when all cases match expected outcomes.
- Exit nonzero when mismatches, input errors, usage errors, or internal
  errors occur.

## 6. Proposed `--fixture-case` Behavior

`--fixture-case` should validate one case only.

The selector should be a safe relative case selector under the fixture root.
The output should be a safe case result summary and should not print file
contents.

Exit behavior:

- Exit 0 if the case result matches the expected outcome.
- Exit nonzero if the case mismatches or has an input error.
- An invalid fixture case that correctly matches its expected fail-closed or
  usage-error outcome should exit 0, because the validator behavior matched
  the fixture expectation.

## 7. Proposed JSON Behavior

Safe JSON output may include:

- `mode`
- `validation_schema_version`
- `total_cases`
- `valid_cases`
- `invalid_cases`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `reason_code_counts`
- `content_suppressed`
- `no_raw_rows`
- `no_logits_dump`
- `no_private_paths`
- `synthetic_only_checked`
- `no_oracle_checked`
- `path_policy_checked`
- `body_content_policy_checked`
- `stdout_body_suppression_checked`
- `manifest_absence_checked`
- `file_writing_isolated=false`
- safe relative `case_ids` only if needed

JSON output must not include:

- fixture JSON bodies
- request bodies
- pointer bodies
- expected result bodies
- file write request bodies
- artifact body payloads
- raw rows
- logits
- private paths
- absolute paths
- raw learner text
- manifest bodies

## 8. Proposed Exit Codes

Recommended exit codes:

- `0`: validation completed and all checked cases matched expected outcome
- `1`: validator internal error or unexpected failure
- `2`: usage error, such as unsafe `--fixture-case`, missing path, or invalid
  arguments
- `3`: validation mismatch
- `4`: input error or malformed fixture root/file

The future implementation should align with existing learner-state CLI
patterns where practical, while preserving the distinction between usage
errors, mismatches, and malformed fixture input.

## 9. Proposed Human Summary

Human output should be field-list style only, for example these fields:

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
- `file_writing_isolated=false`

The summary should not include raw fixture file contents or JSON body
examples.

## 10. CLI Safety Constraints

The future CLI must:

- not print fixture bodies
- not print raw JSON bodies
- not print artifact body payloads
- not print request, pointer, expected result, or file write request bodies
- not print absolute local paths
- report safe relative case IDs only
- not create temp directories
- not write files
- fail closed on malformed arguments
- reject unsafe fixture-case selectors
- avoid traceback-heavy output by default
- keep stdout/stderr summary-only

## 11. Test Plan For Future CLI Implementation

Future CLI tests should verify:

- `--help` exits 0
- default root validation exits 0
- JSON output is parseable
- JSON output is body-free
- human output is body-free
- single valid case exits 0
- single invalid expected fail-closed case exits 0 when matched
- unsafe absolute fixture-case selector is rejected
- parent traversal fixture-case selector is rejected
- missing fixture-case returns usage or input error
- malformed temporary fixture root returns input error
- summary counts match 29 / 5 / 24
- no files are created
- no temp directories are created
- no private paths are printed
- no raw rows, logits, or raw learner text are printed

## 12. Relation To Future Makefile Target

Future target:

`check-learner-state-frozen-policy-generation-artifact-body-file-writing-fixtures`

That target should run the CLI against the default fixture root. This step
does not implement the target.

## 13. Relation To Release-Quality

- Do not add the CLI target to release-quality yet.
- Implement the CLI first.
- Add a standalone Makefile target later.
- Design release-quality integration later.
- Add wrapper integration and a remote/manual status marker only after the
  standalone target is stable.

## 14. Relation To Future File Writing

The validator CLI should remain no-write until artifact body file writing
exists.

Isolated temp write validation should be a later optional mode. The initial
CLI should not add a write-validation flag. The static validator API and
summary contract should remain stable as later phases are added.

## 15. Docs Safety Policy

Docs for the CLI should include field names, command shapes, statuses,
reason-code names, and count-only summaries only.

Docs must not include JSON body examples, raw file examples, artifact body
payload examples, private path examples, raw logs, full job output, copied
log blocks, raw rows, logits, real data, raw learner text, generated policy
bodies, manifest bodies, or performance metric bodies.

## 16. Beginner-Friendly Explanation

A CLI is a command-line interface. It lets someone run the validator from a
terminal instead of importing Python functions.

Designing the CLI after the module API keeps the command thin. The command
should call the already-tested validator and format the result safely.

The default should validate the whole fixture root because the most common
question is whether the complete contract still matches.

An invalid fixture can still lead to exit 0 when the validator confirms the
expected failure. In that case, the fixture is doing its job: it proves the
validator recognizes the unsafe condition and fails closed as expected.

JSON output is useful for automation, but it still must not include bodies.
It should carry only safe metadata, counts, flags, and reason-code names.

## 17. What This Does NOT Do

- Does not implement the CLI.
- Does not add a Makefile target.
- Does not add a release-quality target.
- Does not implement file writing.
- Does not create output files.
- Does not implement `--artifact-body-out`.
- Does not run isolated temp write validation.
- Does not write manifests.
- Does not connect artifact writer CLI.
- Does not use real data.
- Does not compute metrics.

## 18. Next Recommended Steps

- Step356: CLI implementation.
- Step357: Makefile target design.
- Step360: release-quality wrapper integration.
- Later: remote/manual status marker.
- Later: isolated temp write validation after artifact body file writing
  exists.

## 19. Related Documents

- [Frozen policy generation artifact body file writing fixture validator design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_design.md)
- [Frozen policy generation artifact body file writing fixture validator Makefile target design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_makefile_target_design.md)
- [Frozen policy generation artifact body file writing fixture release-quality integration design](frozen_policy_generation_artifact_body_file_writing_fixture_release_quality_integration_design.md)
- [Frozen policy generation artifact body file writing fixture design](frozen_policy_generation_artifact_body_file_writing_fixture_design.md)
- [Frozen policy generation artifact body file writing design](frozen_policy_generation_artifact_body_file_writing_design.md)
- [Frozen policy generation artifact body file writing fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body_file_writing/README.md)
- [Public release checklist](public_release_checklist.md)

## 20. Step356 CLI Implementation Status

Step356 implements the safe no-write CLI entrypoint:

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_file_writing_fixture_validation`

The CLI supports `--fixture-root`, `--fixture-case`, `--json`, and `--help`.
With no arguments, it validates the default file writing fixture root and
emits a body-free human summary. Single-case mode accepts safe relative case
selectors only. JSON output is summary-only and does not include fixture
bodies, request bodies, pointer bodies, file write request bodies, expected
result bodies, artifact body payloads, raw rows, logits, private paths, raw
learner text, generated policy bodies, manifest bodies, or absolute local
paths.

Step356 also adds focused CLI tests for help, default root, JSON output,
single valid case, single expected invalid case, unsafe selectors, missing
cases, malformed temp roots, and no-write behavior.

This implementation does not add a Makefile target, does not add
release-quality integration, does not implement file writing, does not add
`--artifact-body-out`, does not run isolated temp write validation, does not
write manifests, does not connect artifact writer CLI, does not use real
data, and does not compute metrics.

## 21. Step357 Makefile Target Design Status

Step357 designs a future standalone Makefile target for this CLI:

[Frozen policy generation artifact body file writing fixture validator Makefile target design](frozen_policy_generation_artifact_body_file_writing_fixture_validator_makefile_target_design.md).

The target design proposes a long explicit learner-state/frozen-policy
generation target name, a default-root CLI command, safe help text, expected
counts, output safety, Makefile placement notes, relation to existing
targets, release-quality staging, and future tests. It does not implement a
Makefile target, does not add release-quality integration, does not write
files, does not create temp output directories, does not implement
`--artifact-body-out`, does not use real data, and does not compute metrics.

## 22. Step358 Makefile Target Implementation Status

Step358 implements the standalone Makefile target:

`check-learner-state-frozen-policy-generation-artifact-body-file-writing-fixtures`

The target calls this CLI against the default file writing fixture root and
keeps the run static/no-write. The target does not use `--json` by default,
does not write files, does not create temp output directories, does not run
isolated temp write validation, does not implement `--artifact-body-out`,
does not add release-quality integration, does not change workflow YAML,
does not change Python code/tests, does not change fixture JSON, does not
connect artifact writer CLI, does not use real data, and does not compute
metrics.

## 23. Step359 Release-Quality Integration Design Status

Step359 designs future release-quality wrapper integration for the
standalone no-write fixture validator target:

[Frozen policy generation artifact body file writing fixture release-quality integration design](frozen_policy_generation_artifact_body_file_writing_fixture_release_quality_integration_design.md).

The design does not change the wrapper, workflow YAML, Makefile, Python
code/tests, fixture JSON, file writing implementation, `--artifact-body-out`,
isolated temp write validation, manifest writer, artifact writer CLI, real
data, metrics, or production readiness claims.

## 24. Step360 Release-Quality Wrapper Integration Status

Step360 integrates the standalone no-write target into
`scripts/check_release_quality.sh` after safe-metadata artifact body
generation smoke and before config/scoring smoke checks. The CLI remains
static/no-write, body-free, and summary-only. Step360 does not change this
CLI, does not change Python tests, does not change fixture JSON, does not
implement file writing, does not implement `--artifact-body-out`, does not
run isolated temp write validation, does not write manifests, does not use
real data, and does not compute metrics.
