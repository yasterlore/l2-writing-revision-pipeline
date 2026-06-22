# Frozen Policy Generation Validator CLI Design

This document designs the CLI for frozen policy generation fixture validation
and records the Step240 minimal implementation status.

Step240 implements the minimal CLI entrypoint in
`python/learner_state/frozen_policy_generation_validation.py` and adds CLI
tests in
`python/learner_state/tests/test_frozen_policy_generation_validation_cli.py`.
It does not implement a generator, frozen policy generation scaffold, Makefile
target, release-quality integration, GitHub Actions workflow change,
calibration, selective prediction, learner-state estimator, estimator
training, new model, or metric computation. It is not a performance
evaluation and is not a real-data readiness claim.

Public docs must not include raw GitHub Actions logs, full job output, copied
log blocks, screenshots containing raw logs, frozen policy artifact bodies,
JSON bodies, request bodies, policy bodies, raw rows, logits/probability
dumps, label bodies, split bodies, calibration policy bodies, generated
feature/label/manifest bodies, private paths, raw learner text, or real
participant data.

## 1. Purpose

The purpose of this document is to design a safe command-line interface for
the Step238 frozen policy generation fixture validator.

The CLI should let developers validate one fixture case or the full synthetic
fixture root, compare results against `expected_generation_result.json`, and
emit safe human or JSON summaries without printing request bodies, input
pointer bodies, generated artifact bodies, raw rows, logits dumps, private
paths, or metric bodies.

This is not a generator implementation. It does not compute temperature,
threshold, calibration quality, F1, accuracy, ECE, AURCC, or model
performance.

## 2. Current State

Current state:

- generation fixture root exists:
  `tests/fixtures/learner_state_frozen_policy_generation/`
- valid 3 fixtures exist
- invalid 10 fixtures exist
- Python validator API exists in
  `python/learner_state/frozen_policy_generation_validation.py`
- fixture-based unittest exists in
  `python/learner_state/tests/test_frozen_policy_generation_validation.py`
- CLI exists as of Step240
- Makefile target does not exist yet
- release-quality integration does not exist yet

Current Python API:

- `load_frozen_policy_generation_fixture(case_dir)`
- `validate_frozen_policy_generation_fixture(case_dir)`
- `load_expected_generation_result(case_dir)`
- `compare_frozen_policy_generation_result_to_expected(result, expected)`
- `discover_frozen_policy_generation_fixture_cases(root)`

## 3. Proposed CLI Entrypoint

Candidate entrypoints:

| Entrypoint | Assessment |
| --- | --- |
| `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_validation` | Recommended initially; keeps CLI close to the validator API, matches existing frozen policy validator pattern, and avoids an extra module |
| `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_validation_cli` | Useful later if CLI logic grows, but premature for the minimal fixture-root workflow |

Recommended initial entrypoint:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_validation
```

Rationale:

- mirrors `learner_state.frozen_policy_validation`
- keeps one implementation surface for loader, validator, and small CLI wrapper
- avoids duplicate validation logic
- keeps future tests simple

If the CLI later gains non-fixture raw validation modes, a separate module can
be reconsidered.

## 4. CLI Modes

Required initial modes:

- single fixture case mode:
  `--fixture-case tests/fixtures/learner_state_frozen_policy_generation/valid/identity_temperature_fixed_threshold`
- fixture root mode:
  `--fixture-root tests/fixtures/learner_state_frozen_policy_generation`
- JSON output:
  `--json`
- help:
  `--help`

Argument rule:

- exactly one of `--fixture-case` or `--fixture-root` is required
- passing both is a usage error
- passing neither is a usage error

Optional future modes:

- raw validation-only mode
- strict mode

The first implementation should stay simple and fixture-focused.

## 5. Command Examples

Validate one valid generation case:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_validation \
  --fixture-case tests/fixtures/learner_state_frozen_policy_generation/valid/identity_temperature_fixed_threshold
```

Validate one intentional invalid generation case:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_validation \
  --fixture-case tests/fixtures/learner_state_frozen_policy_generation/invalid/test_derived_temperature
```

Validate all generation fixture cases:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_validation \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation
```

Validate all generation fixture cases with JSON output:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_validation \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation --json
```

Expected-result matching should be on by default for fixture cases and fixture
roots. Intentional invalid fixtures should exit successfully when their
observed safe reason code matches `expected_generation_result.json`.

The examples must not print request bodies, input pointer bodies, generated
artifact bodies, logits bodies, private paths, or metric bodies.

## 6. Exit Code Design

Recommended exit codes:

- `0`: validation passed, or fixture expected results all matched
- `1`: validation failure for a future raw validation-only mode
- `2`: usage error, missing files, malformed input, unsafe path, or input error
- `3`: expected-result mismatch in fixture test mode

Single fixture case mode:

- valid fixture with expected pass -> exit `0`
- intentional invalid fixture with expected fail reason -> exit `0`
- expected-result mismatch -> exit `3`
- missing or malformed fixture input -> exit `2`

Fixture root mode:

- all 13 cases match expected results -> exit `0`
- any expected-result mismatch -> exit `3`
- any input error that prevents safe fixture processing -> exit `2`

Exit `1` should remain reserved for a future raw validation-only mode where
there may be no expected-result file.

## 7. Safe Human Output

Human summary fields:

- `mode`
- `validation_status`
- `reason_codes`
- `failed_checks`
- `generation_request_schema_version`
- `pointer_schema_version`
- `generation_status`
- `expected_output_status`
- `expected_frozen_policy_validation_status`
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only_checked`
- `no_oracle_checked`
- `test_tuning_checked`
- `forbidden_field_scan_checked`
- `private_path_scan_checked`
- `performance_claim_scan_checked`

Fixture-root mode should also report:

- `total_cases`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `reason_code_counts`

Forbidden from human output:

- request body
- input pointer body
- generated frozen policy body
- raw rows
- logits/probability dump
- label body
- split body
- calibration policy body
- private paths
- metric body
- raw learner text

## 8. Safe JSON Output

JSON output should be machine-readable but safe.

Allowed JSON content:

- validation result dictionaries
- case labels
- matched/mismatched counts
- safe reason-code counts
- safe mismatch field names
- safe boolean flags

Forbidden JSON content:

- full request body
- full input pointer body
- generated artifact body
- raw rows
- logits dump
- probability dump
- label body
- split body
- calibration policy body
- private absolute paths
- raw learner text
- performance metric bodies

The JSON summary should keep `content_suppressed: true` and `no_raw_rows:
true`.

## 9. Fixture-Root Behavior

Fixture-root mode should:

- discover fixture directories deterministically
- include valid and invalid cases
- load `expected_generation_result.json` for each case
- compare observed result to expected result
- report `total_cases`
- report `matched_cases`
- report `mismatched_cases`
- report `input_error_cases`
- output `reason_code_counts`
- avoid printing request bodies
- avoid printing generated artifact bodies
- exit `0` only when all expected results match

The expected current root count is 13 matched cases once CLI implementation is
added.

## 10. Single-Case Behavior

Single-case mode should:

- validate one fixture directory
- load `expected_generation_result.json` if present
- compare expected result by default
- exit `0` for intentional invalid fixtures when expected reason matches
- exit `3` for expected-result mismatch
- exit `2` for missing, malformed, or unsafe inputs

A future raw validation-only option may allow no expected result file, but that
should not be part of the initial CLI.

## 11. Path Safety

Path safety rules:

- reject input paths containing `real_data`
- reject input paths containing `participant_data`
- reject input paths containing `private_data`
- reject input paths containing `manual_outputs`
- allow fixture roots under `tests/fixtures`
- do not print absolute private paths
- display safe relative case labels such as
  `valid/identity_temperature_fixed_threshold`

The intentional invalid `private_path_output` fixture may contain an unsafe
path marker inside its metadata, but CLI output should report only
`unsafe_path` and the safe case label.

## 12. Relation To Python API

The CLI should wrap the existing Python API. It should not duplicate
validation logic.

Mapping:

- fixture loading -> `load_frozen_policy_generation_fixture`
- validation -> `validate_frozen_policy_generation_fixture`
- expected loading -> `load_expected_generation_result`
- expected matching -> `compare_frozen_policy_generation_result_to_expected`
- root discovery -> `discover_frozen_policy_generation_fixture_cases`

The API remains the primary implementation surface. CLI tests should cover
argument handling, exit codes, safe stdout/stderr, and safe JSON output.

## 13. Testing Plan For Future Implementation

Future CLI tests should cover:

- `--help` exits `0`
- valid single case exits `0`
- intentional invalid single case exits `0` when expected-result matching
  succeeds
- fixture root exits `0` with 13 matched cases
- missing fixture exits `2`
- both `--fixture-case` and `--fixture-root` exits `2`
- no args exits `2`
- expected mismatch exits `3`
- JSON output is parseable and safe
- stdout/stderr do not include request body
- stdout/stderr do not include generated artifact body
- stdout/stderr do not include logits dump
- stdout/stderr do not include private paths

Tests should use synthetic fixtures only and should not write `manual_outputs/`
or tracked `tmp/` files.

## 14. Makefile / Release-Quality Future

Not in this step:

- no Makefile target
- no release-quality wrapper change
- no GitHub Actions workflow change

Future sequence:

1. design and implement standalone Makefile target
2. review CLI/target log safety
3. integrate into release-quality only after standalone behavior is stable

Do not connect the CLI to release-quality in Step240.

## 15. No-Oracle / Synthetic-Only Boundary

Generation fixtures are synthetic-only metadata. Intentional invalid fixtures
may contain leakage markers, but the CLI should report only safe reason codes.

Boundaries:

- no real data
- no raw learner text
- no test-derived tuning in valid cases
- no expected action as scoring feedback
- no model performance evidence
- no generator implementation
- no calibration implementation
- no metric computation

## 16. What This Does Not Do

Step240 does not:

- implement generator
- implement frozen policy generation scaffold
- implement calibration
- implement selective prediction
- train an estimator
- compute metrics
- use real data
- add a Makefile target
- change release-quality
- change workflows
- change Makefile
- change fixtures

## 17. Beginner Notes

A CLI is a command-line interface. It lets a developer run the validator from
the terminal instead of importing Python functions manually.

The API is useful for tests and other Python code. The CLI is useful for local
checks, future Makefile targets, and CI wrappers.

An exit code is the number a command returns to the shell. `0` means success.
Nonzero values tell scripts what kind of failure happened.

Human output is short text meant for people. JSON output is structured data
meant for scripts. Both must stay safe and avoid body dumps.

Request bodies and generated artifact bodies are not printed because they can
accidentally expose raw rows, labels, logits, paths, or misleading metrics.

## 18. Update History

- Step239: initial frozen policy generation validator CLI design creation.
- Step240: minimal CLI implementation added to
  `python/learner_state/frozen_policy_generation_validation.py`, with CLI
  tests in
  `python/learner_state/tests/test_frozen_policy_generation_validation_cli.py`.

## Related Documents

- [Frozen policy generation validation design](frozen_policy_generation_validation_design.md)
- [Frozen policy generation fixture design](frozen_policy_generation_fixture_design.md)
- [Frozen policy generation fixtures](../tests/fixtures/learner_state_frozen_policy_generation/README.md)
- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Milestone 10 frozen policy validation infrastructure recap](milestone_10_frozen_policy_validation_infrastructure_recap.md)
- `python/learner_state/frozen_policy_generation_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_validation_cli.py`
- [Public release checklist](public_release_checklist.md)
