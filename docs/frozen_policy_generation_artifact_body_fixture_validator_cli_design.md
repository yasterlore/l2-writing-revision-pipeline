# Frozen Policy Generation Artifact Body Fixture Validator CLI Design

## 1. Purpose

This document designs a future command-line interface for the frozen policy
generation artifact body fixture validator.

This is a docs-only CLI design. It is not CLI implementation, Makefile target
implementation, release-quality integration, artifact body generation
implementation, file writing, performance evaluation, real-data readiness, or
production readiness.

The CLI should make the Step326 metadata-only validator safely callable from a
terminal while preserving the synthetic-only, metadata-only, no-oracle,
body-free fixture contract.

## 2. Current State

- Artifact body fixtures exist.
- The artifact body fixture validator API exists.
- The artifact body fixture validator tests exist.
- The validator CLI does not exist.
- The Makefile target does not exist.
- Release-quality integration does not exist.
- Artifact body generation does not exist.
- Generated policy body generation does not exist.
- Manifest body generation and file writing do not exist.

Current fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body`

Current validator module:

`python/learner_state/frozen_policy_generation_artifact_body_fixture_validation.py`

## 3. Proposed Entrypoint

Recommended future entrypoint:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_fixture_validation
```

Reasons:

- It matches the validator module name.
- It can call the existing validator APIs directly.
- It is easy to reuse from a future Makefile target.
- It follows the module-based fixture validator CLI style already used in the
  repository.

This step does not implement the entrypoint.

## 4. Proposed Arguments

Minimum future arguments:

- `--fixture-root`
- `--fixture-case`
- `--json`
- `--help`

Argument behavior:

- `--fixture-root` runs root validation.
- `--fixture-case` runs single-case validation.
- `--json` emits a safe parseable JSON summary.
- `--help` prints usage.
- `--fixture-root` and `--fixture-case` are mutually exclusive.
- If both are supplied, the CLI should return a usage error.
- If neither is supplied, the recommended default is the built-in fixture
  root.

Recommended default behavior:

- Use the default fixture root when neither `--fixture-root` nor
  `--fixture-case` is supplied.
- This keeps the command short for the common root-validation path.
- The behavior must be explicit in help text and docs.

Alternative considered:

- Treat missing `--fixture-root` and `--fixture-case` as a usage error.
- This is stricter, but it makes the common validator smoke path more verbose.

The initial CLI should not include:

- output file options
- artifact body output options
- artifact generation options
- manifest body output options
- artifact file writing options
- manifest file writing options

## 5. Default Fixture Root

Recommended default fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body`

This root contains 18 cases and 54 JSON files. The CLI should treat this path
as a synthetic fixture root only, not as real-data input.

## 6. Human Output Design

Root human output may include:

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
- `no_performance_claims`
- `synthetic_only_checked`
- `no_oracle_checked`
- `artifact_policy_checked`
- `body_suppression_checked`
- `artifact_body_audit_checked`
- `request_body_count`
- `pointer_body_count`
- `expected_body_count`
- `raw_row_count`
- `logits_dump_count`
- `private_path_count`
- `performance_metric_count`
- `manifest_body_count`

Single-case human output may include:

- safe `case_id`
- `category`
- `validation_status`
- `body_status`
- `matched`
- `reason_codes`
- `failed_checks`
- safe marker summary
- count summary
- safety flags
- schema versions

Human output should be compact and stable. It should not echo loaded JSON
objects or any payload-like body.

## 7. JSON Output Design

`--json` should emit deterministic safe metadata only.

Recommended JSON output rules:

- parseable JSON
- sorted keys
- sorted case order
- sorted reason codes
- sorted failed checks
- count-only `reason_code_counts`
- no request, pointer, expected-result, artifact, policy, or manifest body
- no raw rows
- no logits or probabilities
- no private paths
- no raw learner text
- no performance metric body
- no raw logs

The JSON output should contain the same kind of safe fields as human output,
but must remain body-free and payload-free.

## 8. Exit Code Design

Recommended exit codes:

- `0`: all matched, or selected case matched
- `2`: usage error or input error
- `3`: validation mismatch
- `1`: unexpected internal error

Concrete interpretation:

- All 18 cases matched: exit `0`.
- A single valid case matched: exit `0`.
- A single invalid expected fail-closed case matched: exit `0`.
- Missing fixture root: exit `2`.
- Missing case: exit `2`.
- Malformed JSON: exit `2`.
- Missing required file: exit `2`.
- Metadata mismatch: exit `3`.
- Unexpected internal exception: exit `1`.

An invalid fixture can exit `0` because the invalid condition is expected and
represented only by safe marker metadata.

## 9. Single Case Behavior

Recommended `--fixture-case` input:

- `valid/minimal_suppressed_metadata_only_body`
- `invalid/raw_rows_in_artifact_body`

The CLI should resolve category/path case labels under the default fixture
root unless an explicit root-path mode is later added. Missing case labels
should return input error exit `2`.

Matched invalid cases should exit `0` because the validator is confirming the
expected fail-closed contract, not accepting unsafe payload output.

Single-case output remains safe metadata only.

## 10. Error Handling

The CLI should handle:

- missing root as usage/input error
- missing case as input error
- malformed JSON as input error
- missing required file as input error
- unexpected fixture file as mismatch or fail-closed result
- internal exception as exit `1`

Error output must not echo file bodies, loaded objects, payload strings, or
private paths. It should report safe reason code names, failed check names,
and count-only summaries.

## 11. Output Safety

CLI stdout and stderr must never print:

- `artifact_body_request` body
- `artifact_writer_result_pointer` body
- `expected_artifact_body_result` body
- artifact body payload
- generated policy body
- manifest body
- raw rows
- logits
- probabilities
- private paths
- raw learner text
- performance metric body
- raw GitHub logs

The CLI may print:

- counts
- reason code names
- safe case IDs
- schema versions
- safe flags
- marker booleans summarized count-only

## 12. No-Body-Leakage Checks For Future Tests

Future CLI tests should verify:

- root human output is body-free
- root JSON output is body-free
- single valid case output is body-free
- single invalid case output is body-free
- missing root error output is body-free
- malformed JSON error output is body-free
- unknown option output is body-free
- JSON output is parseable
- JSON output is deterministic
- output does not include raw rows, logits, private paths, or raw learner text
- output does not include request, pointer, expected-result, artifact body
  payload, or manifest body fields except intentionally allowed safe field
  names such as count names

## 13. Future Makefile Target Candidate

Recommended future target:

`check-learner-state-frozen-policy-generation-artifact-body-fixtures`

Recommended command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body
```

Recommended help text:

`check-learner-state-frozen-policy-generation-artifact-body-fixtures  Validate frozen policy generation artifact body fixtures`

This step does not implement the Makefile target.

## 14. Future Release-Quality Staging

Recommended future staging:

- CLI implementation
- Makefile target design
- Makefile target implementation
- release-quality integration design
- wrapper integration
- remote status marker

Artifact body generation itself remains separate and later.

## 15. Relation To Validator API

The CLI should call the existing validator APIs. It should not duplicate
validation logic.

Root mode should call:

- `validate_artifact_body_fixture_root`
- `summarize_fixture_root`

Case mode should call:

- `validate_artifact_body_fixture_case`
- `compare_expected_result`
- `scan_safe_markers`
- `scan_forbidden_payload`
- `summarize_fixture_root`

The CLI should not compare raw payloads, create artifacts, write output files,
generate bodies, or compute metrics.

## 16. Relation To Artifact Body Generation

The CLI validates fixture contracts only. It does not generate an artifact
body and does not test generator quality.

Future artifact body generator work should happen after validator CLI and
Makefile target paths are stable, so the generator can be tested against an
already-visible safe fixture contract.

## 17. Docs Safety Policy

Docs may include:

- CLI argument names
- field names
- exit codes
- counts
- reason codes
- schema names
- safe status descriptions

Docs must not include:

- JSON output examples
- artifact body examples
- artifact body payloads
- request body examples
- pointer body examples
- expected result body examples
- manifest body examples
- raw log examples

## 18. Beginner-Friendly Explanation

A CLI is a terminal command. It lets someone run a validator without writing
Python code.

The validator API already exists, but a CLI needs its own design because
terminal output and exit codes become part of the developer workflow. Root
validation checks the whole fixture root. Single-case validation checks one
named valid or invalid case.

An invalid case can exit `0` when it matched the expected fail-closed result.
That means the validator correctly detected the simulated unsafe condition
using safe metadata. It does not mean unsafe content is accepted.

JSON output also stays body-free because JSON is easy to copy into logs or
docs. The CLI should make automation possible without exposing payloads.

## 19. What This Does Not Do

This design does not:

- implement CLI
- add Makefile target
- integrate release-quality
- implement artifact body generation
- generate artifact body
- change fixtures
- change Python code or tests
- change workflow YAML
- change release-quality wrapper
- write artifact files
- write manifest files
- use real data
- compute metrics

## 20. Step327 Status

Step327 creates this docs-only artifact body fixture validator CLI design. It
does not implement CLI code, Makefile targets, release-quality integration,
artifact body generation, generated policy body generation, manifest body
generation, file writing, Python code or tests, fixture JSON changes,
metrics, real-data use, or production readiness claims.

## 21. Step328 Implementation Status

Step328 implements the thin CLI entrypoint in:

`python/learner_state/frozen_policy_generation_artifact_body_fixture_validation.py`

It also adds focused CLI tests under `python/learner_state/tests/`. The CLI
supports default root validation, explicit `--fixture-root`, `--fixture-case`,
`--json`, and `--help`. It calls the existing validator APIs and emits safe
metadata-only summaries in human or JSON form.

Step328 does not add a Makefile target, integrate release-quality, change
workflow YAML, change fixture JSON, implement artifact body generation,
generate policy bodies, generate manifest bodies, write artifact or manifest
files, add output-file options, compute metrics, use real data, or claim
production readiness.

## 22. Step329 Makefile Target Design Status

Step329 designs the future standalone Makefile target for this CLI:

[Frozen policy generation artifact body fixture validator Makefile target design](frozen_policy_generation_artifact_body_fixture_validator_makefile_target_design.md).

The design recommends
`check-learner-state-frozen-policy-generation-artifact-body-fixtures` as a
future target around the existing CLI. Step329 does not change the Makefile,
release-quality wrapper, workflow YAML, Python code or tests, fixture JSON,
artifact body generation, file writing, metrics, real-data use, or production
readiness claims.

## 23. Step330 Makefile Target Implementation Status

Step330 implements the standalone Makefile target:

`check-learner-state-frozen-policy-generation-artifact-body-fixtures`

The target calls this CLI with the fixture root and uses the default safe
human summary. Release-quality integration remains separate and future.
Step330 does not change workflow YAML, Python code or tests, fixture JSON,
artifact body generation, generated policy body generation, manifest body
generation, file writing, metrics, real-data use, or production readiness
claims.

## 24. Step331 Release-Quality Integration Design Status

Step331 designs future release-quality integration for the standalone
artifact body fixture validator target:

[Frozen policy generation artifact body fixture release-quality integration design](frozen_policy_generation_artifact_body_fixture_release_quality_integration_design.md).

The CLI remains unchanged. Step331 does not change the release-quality
wrapper, workflow YAML, Makefile, Python code or tests, fixture JSON,
artifact body generation, file writing, metrics, real-data use, or production
readiness claims.

## 25. Step332 Release-Quality Wrapper Integration Status

Step332 integrates the standalone artifact body fixture validator target into
the release-quality wrapper. The CLI is now exercised by
`make check-release-quality` through:

`make check-learner-state-frozen-policy-generation-artifact-body-fixtures`

The CLI remains metadata-only and does not print fixture bodies, artifact body
payloads, raw rows, logits, private paths, raw learner text, or performance
metric bodies.

## 26. Step333 Remote Run Record Workflow Design Status

Step333 designs the future remote/manual Release Quality run record workflow
for the wrapper path that exercises this CLI:

[Frozen policy generation artifact body fixture release-quality remote run record workflow](frozen_policy_generation_artifact_body_fixture_release_quality_remote_run_record_workflow.md).

The workflow design keeps future records pass-only and count-only. It does
not create the actual status marker, change code, change fixtures, generate
artifact bodies, write files, compute metrics, use real data, or claim
production readiness.

## 27. Step334 Remote Run Status Marker Status

Step334 creates the public-safe remote/manual Release Quality status marker
for the wrapper path that exercises this CLI:

[Learner-state frozen policy generation artifact body fixture release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_body_fixture_release_quality_remote_run_status.md).

The marker records safe metadata only and does not copy raw logs, fixture
bodies, artifact body payloads, raw rows, logits, private paths, raw learner
text, real participant data, or performance metric bodies.

## 28. Step335 Artifact Body Generation Implementation Status

Step335 implements a safe metadata-only artifact body generation API. The
validator CLI remains unchanged and continues to emit body-free summaries for
fixture validation. No CLI option is added for artifact body generation in this
step, and no artifact body payload is printed by the validator CLI.

## 29. Step336 Artifact Body Generation CLI Design Status

Step336 designs a separate future CLI for artifact body generation:

[Frozen policy generation artifact body generation CLI design](frozen_policy_generation_artifact_body_generation_cli_design.md).

The validator CLI remains unchanged and remains the fixture-validation
interface. The generation CLI design does not implement CLI code, add Makefile
targets, change release-quality, or print artifact body payloads.

## 30. Step337 Artifact Body Generation CLI Implementation Status

Step337 implements the separate artifact body generation CLI. The validator
CLI remains unchanged and remains the fixture-validation interface. The new
generation CLI emits only body-free safe summaries, does not print artifact
body payloads, does not add Makefile targets, does not change release-quality,
does not write files, does not use real data, and does not compute metrics.

## 31. Step338 Artifact Body Generation Makefile Target Design Status

Step338 designs a future standalone Makefile target for the generation CLI:

[Frozen policy generation artifact body generation Makefile target design](frozen_policy_generation_artifact_body_generation_makefile_target_design.md).

The validator CLI remains unchanged. The generation Makefile target design
does not implement a target, does not change release-quality, does not write
files, does not print artifact body payloads, does not use real data, and
does not compute metrics.

## Related Documents

- [Frozen policy generation artifact body generation Makefile target design](frozen_policy_generation_artifact_body_generation_makefile_target_design.md)
- [Frozen policy generation artifact body generation CLI design](frozen_policy_generation_artifact_body_generation_cli_design.md)
- [Learner-state frozen policy generation artifact body fixture release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_body_fixture_release_quality_remote_run_status.md)
- [Frozen policy generation artifact body fixture release-quality remote run record workflow](frozen_policy_generation_artifact_body_fixture_release_quality_remote_run_record_workflow.md)
- [Frozen policy generation artifact body fixture release-quality integration design](frozen_policy_generation_artifact_body_fixture_release_quality_integration_design.md)
- [Frozen policy generation artifact body fixture validator Makefile target design](frozen_policy_generation_artifact_body_fixture_validator_makefile_target_design.md)
- [Frozen policy generation artifact body fixture validator design](frozen_policy_generation_artifact_body_fixture_validator_design.md)
- [Frozen policy generation artifact body fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body/README.md)
- [Frozen policy generation artifact body fixture design](frozen_policy_generation_artifact_body_fixture_design.md)
- [Frozen policy generation artifact body generation design](frozen_policy_generation_artifact_body_generation_design.md)
- [Learner-state frozen policy generation artifact writer runtime release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_writer_runtime_release_quality_remote_run_status.md)
- [Public release checklist](public_release_checklist.md)
