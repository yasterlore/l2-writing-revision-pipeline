# Frozen Policy Generation Generator Scaffold Fixture Validator CLI Design

This document designs a future command-line interface for the frozen policy
generation generator scaffold fixture validator.

It is documentation only. It does not implement CLI code, generator code,
artifact writing, artifact body generation, Makefile targets, release-quality
wrapper changes, workflow changes, Python code, Python tests, fixture changes,
metric computation, performance evaluation, or real-data readiness.

Public docs must not include raw GitHub Actions logs, full job output, copied
log blocks, screenshots containing raw logs, generation request bodies, input
pointer bodies, expected generator scaffold result bodies, expected scaffold
result bodies, generated frozen policy artifact bodies, frozen policy artifact
bodies, JSON bodies, policy bodies, raw rows, logits/probability dumps, label
bodies, split bodies, calibration policy bodies, private paths, raw learner
text, manual output bodies, tmp output bodies, or real participant data.

## 1. Document Purpose

The purpose of this document is to design a future safe CLI over the
implemented metadata-only generator scaffold fixture validator.

The CLI should let developers run the validator from a terminal while
preserving the same safety boundary as the validator module: safe metadata-only
output, no fixture body echoing, no generator execution, no artifact writing,
and no performance interpretation.

This is not implementation. It is not generator implementation, not an
artifact writer, not artifact body generation, not performance evaluation, and
not a real-data readiness claim.

## 2. Current State

Current state:

- generator scaffold fixtures exist
- generator scaffold fixture validator module exists
- generator scaffold fixture validator unit tests exist
- CLI exists as of Step283
- standalone Makefile target exists as of Step285
- release-quality integration does not exist yet
- generator does not exist
- artifact writer does not exist

Current fixture root:

- `tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/`

Current root validation expectation:

- valid cases: 3
- invalid cases: 15
- total cases: 18
- matched cases: 18
- mismatched cases: 0
- input-error cases: 0

The validator summary is body-free metadata-only.

## 3. Proposed CLI Entrypoint

Recommended entrypoint:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_generator_scaffold_fixture_validation
```

Rationale:

- it matches the implemented validator module name
- it stays inside the existing `learner_state` namespace
- it mirrors existing fixture validator CLI usage patterns
- it is straightforward to wrap in a future Makefile target
- it keeps generator scaffold fixture validation distinct from runtime scaffold
  validation and frozen policy generation validation

The CLI should not add a separate executable script at first.

## 4. Proposed CLI Arguments

Minimum arguments:

- `--fixture-root tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold`
- `--fixture-case tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/valid/minimal_metadata_only_generation_plan`
- `--json`
- `--help`

Argument rules:

- exactly one of `--fixture-root` or `--fixture-case` is required
- specifying both `--fixture-root` and `--fixture-case` is a usage error
- specifying neither is a usage error
- `--json` is valid for root mode and case mode
- the default output is a safe human summary
- no output-file option is needed in the initial CLI
- no artifact-output option is allowed in the initial CLI

The CLI should treat every path argument as untrusted input and should not echo
private or absolute paths in public summaries.

## 5. Expected Behavior

Root mode:

- validates the full fixture root
- checks 3 valid cases and 15 invalid cases
- reports `total_cases=18`
- reports `matched_cases=18`
- reports `mismatched_cases=0`
- reports `input_error_cases=0`
- exits 0 when the fixture contract matches

Case mode:

- valid case with expected pass result exits 0
- invalid case with expected fail-closed reason exits 0
- malformed or missing temp case returns input error and exits 2
- expected mismatch exits 3
- usage error exits 2
- unexpected internal error exits 1

Invalid fixtures are expected fail-closed examples. They should not be treated
as command failure when their reason codes and safety metadata match the
fixture contract.

## 6. Exit Code Design

Recommended exit codes:

- `0`: validation completed and the expected contract matched
- `2`: usage error or input error
- `3`: validation mismatch
- `1`: unexpected internal error

Interpretation:

- an invalid fixture can exit 0 when it fails for the expected reason code
- malformed or missing fixture files are input errors and should exit 2
- a readable fixture whose actual validation summary differs from its expected
  result should exit 3
- unexpected exceptions should be caught, summarized safely, and exit 1

The CLI should not transform a validation mismatch into success.

## 7. Safe Human Output

Root mode fields:

- `mode=fixture_root`
- `total_cases`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `reason_code_counts`
- `content_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `artifact_policy_checked=true`
- `body_suppression_checked=true`
- `file_writing_checked=true`
- `validation_schema_version`

Case mode fields:

- `mode=fixture_case`
- `case_label`
- `category`
- `validation_status`
- `expected_status`
- `matched`
- `reason_codes`
- `failed_checks`
- `content_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- artifact flags summary
- safety flags summary

Human output must not include:

- request body
- pointer body
- expected result body
- artifact body
- generated policy body
- raw rows
- logits
- probabilities
- private paths
- raw learner text
- final, observed-after, or gold text
- performance metric body

## 8. Safe JSON Output

Safe JSON output should contain the same safe fields as the human output:

- parseable JSON object
- deterministic key set and ordering where practical
- safe scalar values, booleans, lists of reason codes, and count summaries
- no fixture bodies
- no request body
- no pointer body
- no expected result body
- no artifact body
- no generated policy body
- no raw rows
- no logits
- no private paths

JSON output is for machine readability of safe metadata. It is not permission
to print fixture contents or artifact bodies.

## 9. No-Body-Leakage Policy

CLI stdout and stderr must not include:

- `generation_request.json` body
- `input_fixture_pointer.json` body
- `expected_generator_scaffold_result.json` body
- artifact body
- generated policy body
- raw rows
- logits or probabilities
- private paths
- raw learner text
- final text
- observed-after text
- gold label
- performance metrics

Errors should report safe categories such as `usage_error`, `input_error`,
`validation_mismatch`, or `internal_error`, plus safe case labels and reason
codes only.

## 10. Relation To Validator APIs

Root mode should call:

- `validate_generator_scaffold_fixture_root`
- `summarize_generator_scaffold_fixture_validation_result`

Case mode should call:

- `load_generator_scaffold_fixture_case`
- `validate_generator_scaffold_fixture_case`
- `compare_generator_scaffold_fixture_to_expected`

The CLI should not duplicate validation logic. It should not execute the
generator, write artifacts, compute metrics, parse raw rows, or inspect logits.

## 11. Relation To Existing CLIs

Related existing CLIs:

- runtime scaffold fixture validator CLI validates runtime scaffold fixture
  contracts
- generator scaffold fixture validator CLI will validate generator scaffold
  metadata-only fixture contracts
- frozen policy generation validator CLI is separate
- frozen policy validator CLI is separate
- selective prediction validator CLI is separate
- estimator input CLI is separate

The future CLI should follow the same broad conventions as these existing
validators: root mode, optional JSON output, usage errors as exit 2, safe human
summary by default, and no body-bearing output.

## 12. Future Tests For CLI Implementation

Minimum future CLI tests:

- `--help` exits 0
- no args exits 2
- both root and case args exits 2
- root human mode exits 0
- root JSON mode exits 0 and is parseable
- root summary reports total 18, matched 18, mismatch 0, input error 0
- valid case human mode exits 0
- invalid case human mode exits 0 with expected reason
- case JSON mode exits 0 and is parseable
- missing root path exits 2
- malformed temp case exits 2
- forced mismatch temp case exits 3
- stdout and stderr do not include request body
- stdout and stderr do not include pointer body
- stdout and stderr do not include expected result body
- stdout and stderr do not include artifact body
- stdout and stderr do not include raw rows
- stdout and stderr do not include logits
- stdout and stderr do not include private paths
- output is deterministic

These tests should use synthetic temp fixtures only for malformed, missing, and
mismatch cases.

## 13. Makefile Strategy

Makefile integration is not part of this step.

After CLI implementation and tests, design a standalone Makefile target.

Likely target name:

- `check-learner-state-frozen-policy-generation-generator-scaffold-fixtures`

Likely command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_generator_scaffold_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold
```

Release-quality integration should wait until the standalone target passes and
no-body-leakage review is complete.

## 14. Release-Quality Strategy

Release-quality integration is not part of this step.

Future policy:

- do not add the generator scaffold fixture validator to release-quality until
  CLI and Makefile target pass
- keep generator execution out of release-quality at this stage
- keep artifact body generation out of release-quality
- keep artifact file writing out of release-quality
- treat success as fixture contract validation, not generator quality
- treat success as safety/smoke evidence, not performance evidence

Any future status marker should remain pass-only and count-only.

## 15. What This Does NOT Prove

This design does not prove:

- generator implementation exists
- artifact generation works
- artifact file writing works
- generated policy quality
- model performance
- calibration quality
- selective prediction correctness
- learner-state estimator correctness
- real-data readiness
- production readiness

It only designs a safe terminal entrypoint for a metadata-only fixture
validator.

## 16. Beginner-Friendly Explanation

A CLI is a terminal command. It lets a developer run the validator without
writing Python code.

The validator needs a CLI because the next stages will likely add a Makefile
target and then release-quality integration. A stable command makes those
later steps easier to review and safer to run.

An invalid fixture can exit 0 because it is intentionally invalid. The command
is successful when the validator confirms that the fixture failed for the
expected safe reason.

`input_error` means the fixture file itself is broken, missing, malformed, or
shaped incorrectly. A mismatch means the file is readable, but the actual
validation result does not match its expected result.

JSON output still must not include bodies because JSON is just another output
format. Machine-readable output can leak content just as easily as human text
if the boundary is not enforced.

## 17. Next Recommended Steps

Recommended next steps:

- Makefile target implementation
- release-quality integration design

Generator implementation and artifact writing should remain separate later
work.

## 18. Docs Update

This Step282 document links the implemented metadata-only fixture validator to
a future CLI boundary.

Step283 implements that CLI boundary in
`python/learner_state/frozen_policy_generation_generator_scaffold_fixture_validation.py`
and adds focused CLI tests at
`python/learner_state/tests/test_frozen_policy_generation_generator_scaffold_fixture_validation_cli.py`.
The implementation is still a thin validator wrapper only: it does not add a
Makefile target, release-quality wrapper change, workflow change, fixture
change, generator code, artifact body generation, artifact file writing,
metrics, or real-data readiness.

Step284 designs the future standalone Makefile target for this CLI at
[Frozen policy generation generator scaffold fixture validator Makefile target design](frozen_policy_generation_generator_scaffold_fixture_validator_makefile_target_design.md).
It remains docs-only and does not add the target, release-quality integration,
workflow changes, generator code, artifact writing, or artifact body
generation.

Step285 implements that standalone Makefile target without adding it to
release-quality and without changing workflows, Python code, tests, fixtures,
generator code, artifact writing, or artifact body generation.

Step286 designs the future release-quality integration for that target:
[Frozen policy generation generator scaffold fixture validator release-quality integration design](frozen_policy_generation_generator_scaffold_fixture_validator_release_quality_integration_design.md).
The design keeps wrapper implementation out of scope and preserves the
metadata-only CLI boundary.

Related docs:

- [Frozen policy generation generator scaffold fixture validator release-quality integration design](frozen_policy_generation_generator_scaffold_fixture_validator_release_quality_integration_design.md)
- [Frozen policy generation generator scaffold fixture validator Makefile target design](frozen_policy_generation_generator_scaffold_fixture_validator_makefile_target_design.md)
- [Frozen policy generation generator scaffold fixture validator design](frozen_policy_generation_generator_scaffold_fixture_validator_design.md)
- [Frozen policy generation generator scaffold fixture design](frozen_policy_generation_generator_scaffold_fixture_design.md)
- [Frozen policy generation generator scaffold fixtures](../tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/README.md)
- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Frozen policy generation artifact policy design](frozen_policy_generation_artifact_policy_design.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)

## 19. Update History

- Step282: initial docs-only CLI design for the metadata-only generator
  scaffold fixture validator.
- Step283: recorded CLI implementation status and focused CLI tests for safe
  root/case human and JSON summaries; Makefile, release-quality, workflow,
  generator, artifact body, and artifact writing remain out of scope.
- Step284: linked the docs-only Makefile target design; target
  implementation, release-quality integration, workflow changes, generator
  code, artifact body generation, and artifact writing remain future work.
- Step285: recorded standalone Makefile target implementation status;
  release-quality integration and workflow changes remain future work.
- Step286: linked the docs-only release-quality integration design.
