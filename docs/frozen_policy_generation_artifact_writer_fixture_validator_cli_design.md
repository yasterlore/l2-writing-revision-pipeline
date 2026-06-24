# Frozen Policy Generation Artifact Writer Fixture Validator CLI Design

## 1. Purpose

This document designs a future command-line interface for the frozen policy
generation artifact writer fixture validator.

This is a docs-only CLI design. It is not CLI implementation, artifact writer
implementation, artifact body generation, generated policy body generation,
manifest body generation, file writing, performance evaluation, or a real-data
readiness claim.

The CLI should make the Step304 metadata-only validator safely callable from a
terminal while preserving the same no-body, synthetic-only, fail-closed fixture
contract.

## 2. Current State

- The artifact writer fixture root exists.
- The artifact writer fixture validator module exists.
- The artifact writer fixture validator tests exist.
- The validator CLI does not exist.
- The Makefile target does not exist.
- Release-quality integration does not exist.
- The artifact writer implementation does not exist.
- Artifact body generation, generated policy body generation, manifest body
  generation, and file writing do not exist.

Current fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/`

Current validator module:

`python/learner_state/frozen_policy_generation_artifact_writer_fixture_validation.py`

## 3. Proposed CLI Entrypoint

Recommended entrypoint:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_fixture_validation
```

Reasons:

- It matches the module name.
- It can call the validator APIs directly.
- It is easy to reuse from a future Makefile target.
- It follows the existing fixture validator CLI pattern in this repository.

## 4. Proposed CLI Arguments

Minimum arguments:

- `--fixture-root`
- `--fixture-case`
- `--json`
- `--help`

Argument rules:

- `--fixture-root` and `--fixture-case` are mutually exclusive.
- Supplying both should be a usage error.
- Supplying neither should be a usage error.
- `--json` is optional.
- The default output should be a safe human summary.
- The initial CLI should not include an output-file option.
- The initial CLI should not include an artifact writer execution option.
- The initial CLI should not include artifact body, manifest body, or file
  writing options.

## 5. Example Commands

Root validation:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer
```

Root validation with safe JSON summary:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer --json
```

Single valid case:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_fixture_validation --fixture-case tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/valid/minimal_metadata_only_artifact_plan
```

Single invalid expected fail-closed case:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_fixture_validation --fixture-case tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/invalid/generated_policy_body_leakage
```

These commands should print summaries only. They must not print fixture JSON
bodies, artifact writer request bodies, pointer bodies, expected result bodies,
artifact bodies, generated policy bodies, manifest bodies, raw rows, logits,
private paths, raw learner text, or performance metric bodies.

## 6. Expected CLI Behavior

Root validation should return:

- `mode=fixture_root`
- `total_cases=17`
- `matched_cases=17`
- `mismatched_cases=0`
- `input_error_cases=0`
- exit `0`

Single valid case validation should return:

- `mode=fixture_case`
- safe `case_id`
- `writer_status=pass`
- `matched=true`
- `reason_codes=none`
- `failed_checks=none`
- exit `0`

Single invalid expected fail-closed validation should return:

- `mode=fixture_case`
- safe `case_id`
- `writer_status=fail`
- `matched=true`
- the expected reason code
- exit `0`

Missing files or malformed JSON should return a safe input-error summary and
exit `2`.

Fixture mismatches should exit `3`.

Unexpected internal errors should exit `1`.

## 7. Exit Code Design

Recommended exit codes:

- `0`: matched / safe expected result
- `2`: usage error or input error
- `3`: mismatch
- `1`: unexpected internal error

Important interpretation:

- An invalid fixture can exit `0` when the expected fail-closed reason code
  matches.
- A body-leakage trigger can exit `0` when it is represented only by a safe
  marker and the expected reason code matches.
- Unsafe body output should be a mismatch and exit `3`.
- Missing files or malformed JSON should be input errors and exit `2`.

## 8. Safe Human Output

Allowed human-output fields:

- `mode`
- `case_id`
- `category`
- fixture root safe label
- `total_cases`
- `valid_cases`
- `invalid_cases`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `writer_status`
- `reason_codes`
- `failed_checks`
- `reason_code_counts`
- artifact flags
- safety flags
- `count_summary`
- `safe_summary`
- `validation_schema_version`

Forbidden human-output content:

- artifact writer request body
- generator result pointer body
- expected artifact writer result body
- generated policy body
- generated artifact body
- artifact body
- manifest body
- policy body
- raw rows
- logits
- probabilities
- private paths
- raw learner text
- performance metric body

## 9. Safe JSON Output

Safe JSON output should contain the same safe fields as the human output. It
should be parseable, deterministic, and metadata-only.

Safe JSON output must not contain request bodies, pointer bodies, expected
result bodies, artifact bodies, policy bodies, manifest bodies, raw rows,
logits, private paths, raw learner text, or performance metric bodies.

## 10. No-Body-Leakage Policy

CLI stdout and stderr must not include:

- artifact writer request JSON body
- generator result pointer JSON body
- expected artifact writer result JSON body
- generated policy body
- artifact body
- manifest body
- policy body
- raw rows
- logits or probabilities
- private paths
- raw learner text
- performance metric body

The CLI should print compact metadata summaries and should avoid echoing input
objects.

## 11. Relation To Validator APIs

Root CLI mode should call:

- `validate_artifact_writer_fixture_root`
- `summarize_artifact_writer_fixture_validation_result`

Case CLI mode should call:

- `load_artifact_writer_fixture_case`
- `compare_artifact_writer_fixture_to_expected`
- `scan_artifact_writer_fixture_for_forbidden_markers`

The CLI should not duplicate core validation logic. It should not execute an
artifact writer, write files, generate bodies, or compute metrics.

## 12. Relation To Artifact Writer Implementation

This CLI validates fixture contracts only.

It does not run an artifact writer, generate an artifact body, write an
artifact file, write a manifest file, compute metrics, or evaluate artifact
quality.

Writer implementation tests should come later and should use a separate
contract.

## 13. Future CLI Tests

Future CLI implementation should include tests for:

- `--help` exit `0`
- no args exit `2`
- both root and case exit `2`
- missing root exit `2`
- missing case exit `2`
- root human exit `0`
- root JSON exit `0` and parseable
- valid case human exit `0`
- valid case JSON exit `0` and parseable
- invalid expected fail-closed case human exit `0`
- invalid expected fail-closed case JSON exit `0` and parseable
- malformed JSON temporary case exit `2`
- mismatch temporary case exit `3`
- stdout/stderr no request body
- stdout/stderr no pointer body
- stdout/stderr no expected body
- stdout/stderr no artifact body
- stdout/stderr no manifest body
- stdout/stderr no raw rows
- stdout/stderr no logits
- stdout/stderr no private paths
- deterministic output

## 14. Future Makefile Strategy

Do not add a Makefile target in the CLI design step.

After CLI implementation and tests, add a standalone target:

`check-learner-state-frozen-policy-generation-artifact-writer-fixtures`

Proposed command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer
```

Proposed help text:

`check-learner-state-frozen-policy-generation-artifact-writer-fixtures  Validate frozen policy generation artifact writer fixtures`

## 15. Future Release-Quality Strategy

Do not integrate release-quality in the CLI design step.

Future integration should wait until:

- CLI implementation is complete.
- CLI tests pass.
- the standalone Makefile target exists.
- no-body-leakage review passes.

The release-quality target should be placed after generator scaffold runtime
smoke and before any future artifact writer runtime smoke.

Release-quality success would mean the fixture contract matched. It would not
mean artifact writer quality, artifact body generation, manifest generation,
or production readiness.

## 16. Status Marker Future

A future remote status marker may record:

- `total_cases=17`
- `matched_cases=17`
- `mismatched_cases=0`
- `input_error_cases=0`
- reason-code counts
- safety flags

It must not include raw logs, request bodies, pointer bodies, expected result
bodies, artifact bodies, policy bodies, manifest bodies, raw rows, logits,
private paths, raw learner text, or performance metrics.

## 17. Docs Safety Policy

Documentation should include only schema/key-level descriptions, safe command
shapes, safe IDs, and count-only summaries.

Documentation must not include:

- JSON fixture bodies
- raw logs
- request body
- pointer body
- expected result body
- artifact body
- policy body
- manifest body
- raw rows
- logits
- private paths
- raw learner text

## 18. Proposed Next Steps

Recommended next steps:

1. Step307: Makefile target design. Complete:
   [Frozen policy generation artifact writer fixture validator Makefile target design](frozen_policy_generation_artifact_writer_fixture_validator_makefile_target_design.md).
2. Step308: Makefile target implementation.
3. Step309: release-quality integration design.

## 19. Beginner-Friendly Explanation

A CLI is a terminal command. It lets a human or Makefile run an existing module
without writing a small Python script each time.

The validator API already knows how to check fixture contracts. A CLI is useful
because it gives the project one consistent terminal entrypoint for root
validation and single-case validation.

Root validation checks every fixture case in the root. Case validation checks
one case directory, which is useful for debugging a specific valid or invalid
case.

An invalid fixture can exit `0` because the fixture is supposed to fail closed.
If it fails for the expected reason and prints only safe metadata, that is a
successful validator result.

An input error means the CLI could not safely read the requested fixture, such
as a missing file or malformed JSON. A mismatch means the files were readable,
but the fixture contract did not match the expected metadata.

The first CLI should not accept output-file options because writing files adds
path-safety and cleanup concerns. That should be designed separately.

## 20. What This Does NOT Do

This document does not:

- execute an artifact writer
- generate artifact bodies
- generate generated policy bodies
- generate manifest bodies
- write artifact files
- write manifest files
- compute metrics
- evaluate performance
- use real data
- claim production readiness

## 21. Step306 CLI Implementation Status

Step306 implements the minimal safe CLI in:

`python/learner_state/frozen_policy_generation_artifact_writer_fixture_validation.py`

It also adds focused CLI tests:

`python/learner_state/tests/test_frozen_policy_generation_artifact_writer_fixture_validation_cli.py`

The CLI supports root mode, case mode, safe human output, safe JSON output,
usage/input-error/mismatch exit codes, deterministic summaries, and
no-body-leakage checks. It remains a thin wrapper over the validator APIs.

Step306 does not implement an artifact writer, Makefile target,
release-quality wrapper integration, workflow change, artifact body
generation, generated policy body generation, manifest body generation,
artifact file writing, manifest file writing, metric computation, performance
evaluation, real-data use, or production readiness.

## 22. Step307 Makefile Target Design Status

Step307 designs a future standalone Makefile target for this CLI:
[Frozen policy generation artifact writer fixture validator Makefile target design](frozen_policy_generation_artifact_writer_fixture_validator_makefile_target_design.md).

The CLI implementation remains unchanged. Step307 is docs-only and does not
add a Makefile target, release-quality wrapper integration, workflow change,
Python code, Python tests, fixture JSON, artifact writer implementation,
artifact body generation, generated policy body generation, manifest body
generation, artifact file writing, manifest file writing, metric computation,
performance evaluation, real-data use, or production readiness.

## 23. Step308 Makefile Target Implementation Status

Step308 implements the standalone Makefile target designed in Step307:

`check-learner-state-frozen-policy-generation-artifact-writer-fixtures`

The target calls this CLI in fixture-root mode and keeps the output
metadata-only. Step308 does not change the CLI implementation, release-quality
wrapper, workflow YAML, fixture JSON, artifact writer implementation, artifact
body generation, generated policy body generation, manifest body generation,
file writing, metric computation, performance evaluation, real-data use, or
production readiness.

## 24. Step309 Release-Quality Integration Design Status

Step309 designs future release-quality wrapper integration for the standalone
Makefile target:
[Frozen policy generation artifact writer fixture release-quality integration design](frozen_policy_generation_artifact_writer_fixture_release_quality_integration_design.md).

The CLI remains unchanged. Step309 does not modify release-quality wrapper
scripts, workflow YAML, Makefile target behavior, Python code, Python tests,
fixture JSON, artifact writer implementation, artifact body generation,
generated policy body generation, manifest body generation, file writing,
metric computation, performance evaluation, real-data use, or production
readiness.

## Related Documents

- [Frozen policy generation artifact writer fixture release-quality integration design](frozen_policy_generation_artifact_writer_fixture_release_quality_integration_design.md)
- [Frozen policy generation artifact writer fixture validator Makefile target design](frozen_policy_generation_artifact_writer_fixture_validator_makefile_target_design.md)
- [Frozen policy generation artifact writer fixture validator design](frozen_policy_generation_artifact_writer_fixture_validator_design.md)
- [Frozen policy generation artifact writer fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/README.md)
- [Frozen policy generation artifact writer fixture design](frozen_policy_generation_artifact_writer_fixture_design.md)
- [Frozen policy generation artifact writer design](frozen_policy_generation_artifact_writer_design.md)
- [Frozen policy generation artifact policy design](frozen_policy_generation_artifact_policy_design.md)
- [Learner-state frozen policy generation generator scaffold runtime release-quality remote run status](status/learner_state_frozen_policy_generation_generator_scaffold_runtime_release_quality_remote_run_status.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)
