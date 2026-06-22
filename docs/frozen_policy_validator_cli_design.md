# Frozen Policy Validator CLI Design

## 1. Purpose

This document records the CLI design for the frozen selective prediction policy
validator. The goal is to make the synthetic frozen policy fixture validation
safe to run with `python -m`, while preserving fixture-root expected-result
matching, safe human output, safe JSON output, and clear exit codes.

Step226 implements the minimal CLI described here in
`python/learner_state/frozen_policy_validation.py` and adds CLI tests in
`python/learner_state/tests/test_frozen_policy_validation_cli.py`.

This design and implementation do not add a Makefile target, release-quality
integration, calibration, selective prediction, estimator training, metric
computation, or real-data readiness.

## 2. Current State

Current assets:

- frozen policy validator Python API exists in
  `python/learner_state/frozen_policy_validation.py`
- frozen policy fixture root exists at
  `tests/fixtures/learner_state_frozen_selective_prediction_policy/`
- one valid fixture exists:
  `valid/minimal_validation_only_policy/`
- eleven intentional invalid fixtures exist under `invalid/`
- fixture-based unittest exists in
  `python/learner_state/tests/test_frozen_policy_validation.py`
- CLI exists at `python -m learner_state.frozen_policy_validation`
- Makefile target exists as `check-learner-state-frozen-policy`
- release-quality integration does not exist yet

The validator API is already the implementation surface. The CLI should wrap
that API rather than duplicating validation logic.

## 3. Proposed CLI Entrypoint

Recommended entrypoint:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_validation
```

Alternative:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_validation_cli
```

Step226 follows the recommendation and adds `main()` to
`python/learner_state/frozen_policy_validation.py`, matching the existing
module-style pattern used by nearby learner-state validators. This keeps the
public CLI close to the public API and avoids another small forwarding module.

A separate `frozen_policy_validation_cli.py` can be introduced later if CLI
formatting, subcommands, or release-quality output policy become large enough
to make the validator module hard to read.

## 4. CLI Modes

Required initial modes:

- single fixture case mode:
  `--fixture-case tests/fixtures/learner_state_frozen_selective_prediction_policy/valid/minimal_validation_only_policy`
- fixture root mode:
  `--fixture-root tests/fixtures/learner_state_frozen_selective_prediction_policy`
- JSON output:
  `--json`
- help:
  `--help`

Argument rule:

- exactly one of `--fixture-case` or `--fixture-root` is required
- specifying both is a usage error
- specifying neither is a usage error

Possible future options:

- raw validation-only mode for non-fixture policy files
- strict mode for future schema checks

The first implementation should stay simple and fixture-focused.

## 5. Command Examples

Validate one valid frozen policy case:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_validation \
  --fixture-case tests/fixtures/learner_state_frozen_selective_prediction_policy/valid/minimal_validation_only_policy
```

Validate one intentional invalid case:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_validation \
  --fixture-case tests/fixtures/learner_state_frozen_selective_prediction_policy/invalid/test_derived_threshold
```

Validate all fixture cases:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_validation \
  --fixture-root tests/fixtures/learner_state_frozen_selective_prediction_policy
```

Validate all fixture cases with safe JSON output:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_validation \
  --fixture-root tests/fixtures/learner_state_frozen_selective_prediction_policy \
  --json
```

Expected-result matching should be the default in fixture-case and
fixture-root modes. Intentional invalid fixtures should return success when
the observed failure matches the expected safe metadata.

The CLI must not print frozen policy bodies, logits bodies, private path
values, raw rows, label bodies, split bodies, calibration policy bodies, or
metric bodies.

## 6. Exit Code Design

Recommended exit codes:

- `0`: validation passed, or fixture expected results all matched
- `1`: validation failure in a future raw validation-only mode
- `2`: usage error, missing files, malformed input, unsafe input path, or
  other input error
- `3`: expected-result mismatch in fixture test mode

Single fixture case mode:

- valid fixture exits `0` if validation passes and expected result matches
- intentional invalid fixture exits `0` if validation fails with the expected
  reason
- expected-result mismatch exits `3`
- missing fixture or unsafe path exits `2`

Fixture root mode:

- exits `0` only when all discovered fixture cases match their expected
  results
- exits `2` if fixture discovery or expected-result loading has input errors
- exits `3` if one or more fixture cases mismatch expected metadata

Because expected-result matching is the default, known invalid fixtures are
not CLI failures when their fail-closed reason matches.

## 7. Safe Human Output

Human output should be compact and line-oriented. Suggested fields:

- `mode`
- `case` for single-case mode
- `validation_status`
- `reason_codes`
- `failed_checks`
- `policy_schema_version`
- `policy_status`
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only_checked`
- `no_oracle_checked`
- `test_tuning_checked`
- `forbidden_field_scan_checked`
- `private_path_scan_checked`
- `performance_claim_scan_checked`
- `total_cases` for fixture-root mode
- `matched_cases` for fixture-root mode
- `mismatched_cases` for fixture-root mode
- `input_error_cases` for fixture-root mode
- `reason_code_counts` for fixture-root mode

Human output must not include:

- full policy body
- raw rows
- logits or probability dump
- label body
- split body
- calibration policy body
- private path values
- metric body
- raw learner text

## 8. Safe JSON Output

JSON output should be machine-readable but safe:

- result dictionary only
- no full policy body
- no raw rows
- no logits dump
- no probability dump
- no label body
- no split body
- no calibration policy body
- no private absolute paths
- no metric body
- `content_suppressed` true
- `no_raw_rows` true

Fixture-root JSON may include per-case safe summaries with case labels,
status, reason codes, policy status, expected-result match flag, and mismatch
field names. It must not include policy content or unsafe values.

## 9. Fixture-Root Behavior

Fixture-root mode should:

- discover fixture directories deterministically
- include the valid fixture and all intentional invalid fixtures
- load each `expected_frozen_policy_validation_result.json`
- compare each observed validation result to expected metadata
- report `total_cases`, `matched_cases`, `mismatched_cases`, and
  `input_error_cases`
- report `reason_code_counts`
- avoid printing policy body or unsafe values
- exit `0` only if all expected results match

For the current fixture root, the expected success summary is 12 matched
cases: one valid fixture and eleven intentional invalid fixtures.

## 10. Single-Case Behavior

Single-case mode should:

- validate one fixture case
- compare to `expected_frozen_policy_validation_result.json` by default when
  it exists
- exit `0` for an intentional invalid fixture if the expected failure reason
  matches
- emit safe human or JSON summary
- avoid printing policy body, private path values, logits, or metric fields

A future raw validation-only mode may skip expected-result matching and use
exit `1` for validation failure. That mode is intentionally out of scope for
the first CLI implementation.

## 11. Path Safety

The CLI should reject input paths containing:

- `real_data`
- `participant_data`
- `private_data`
- `manual_outputs`

Fixture roots under `tests/fixtures` are allowed. Output should display safe
relative case labels such as `invalid/test_derived_threshold`, not private
absolute paths. Input errors should return reason codes and safe file roles
only.

## 12. Relation To Python API

The CLI should wrap the existing Python API:

- `validate_frozen_policy_fixture`
- `load_expected_frozen_policy_validation_result`
- `compare_frozen_policy_validation_result_to_expected`
- `discover_frozen_policy_fixture_cases`

Validation logic should remain in the API. CLI helpers should only handle
argument parsing, fixture-case/root orchestration, expected-result matching,
safe summary formatting, JSON serialization, and exit code translation.

CLI tests should stay separate from the API fixture tests. The API remains the
primary implementation surface for unit tests and future scaffold integration.

## 13. Testing Plan

Step226 adds fixture-based CLI tests that cover:

- `--help` exits `0`
- valid single case exits `0`
- intentional invalid single case exits `0` when expected-result matching
  succeeds
- fixture root exits `0` with 12 matched cases
- missing fixture exits `2`
- both `--fixture-case` and `--fixture-root` exits `2`
- no args exits `2`
- expected mismatch exits `3`
- JSON output is parseable and safe
- stdout/stderr are safe
- no policy body appears in output
- no logits dump appears in output
- no private path value appears in output
- no metric body appears in output

Expected mismatch tests may use a temporary copied fixture with modified
expected metadata. The mismatch summary should remain safe and should not
print policy content.

## 14. Makefile / Release-Quality Future

Step228 adds the standalone Makefile target and does not modify
release-quality.

Recommended future sequence:

1. minimal CLI and CLI tests. Completed in Step226.
2. design a Makefile target. Completed in Step227.
3. implement the Makefile target. Completed in Step228.
4. review log safety.
5. design and implement release-quality integration. Completed in Step230 via
   [frozen policy release-quality integration design](frozen_policy_release_quality_integration_design.md).

Release-quality is connected only after the CLI and standalone Makefile target
have safe human and JSON outputs.

Step227 adds the
[frozen policy validator Makefile target design](frozen_policy_validator_makefile_target_design.md)
as a docs-only plan for wrapping the safe fixture-root CLI in a future
`make check-learner-state-frozen-policy` target. Step228 implements that
standalone target.

Step230 integrates the standalone target into the release-quality wrapper.

## 15. No-Oracle / Synthetic-Only Boundary

The frozen policy is a synthetic-only metadata artifact. Intentional invalid
fixtures may contain leakage markers, raw row markers, logits markers,
private path markers, or performance claim markers as test targets, but the
CLI should report only safe reason codes and safe metadata.

The CLI must not:

- use real data
- print raw learner text
- expose policy bodies
- expose private paths
- tune on test split
- use expected action as scoring feedback
- claim model performance
- compute F1, accuracy, ECE, or AURCC

## 16. What This Does Not Do

This document and Step226 implementation do not:

- implement calibration
- implement selective prediction
- generate frozen policy artifacts
- train an estimator
- compute metrics
- use real data
- prove performance

## 17. Beginner Notes

A CLI is a command-line interface: a small command that lets someone run the
validator from a terminal instead of writing Python code.

An API is useful for tests and other Python modules. A CLI is useful for
humans, Makefile targets, and CI wrappers. The CLI should call the API rather
than reimplementing the checker.

An exit code is the number a command returns to the shell. `0` means success;
nonzero values tell automation that something needs attention.

Human output is for quick reading in the terminal. JSON output is for tools
that want to parse the result. Both forms must suppress policy bodies,
logits, raw rows, private paths, and metric bodies.

Policy bodies and logits dumps are not printed because the frozen policy
validator is a safety boundary. It should tell us what failed, not expose the
unsafe content that caused the failure.

## 18. Related Documents

- [Frozen selective prediction policy validation design](frozen_selective_prediction_policy_validation_design.md)
- [Frozen selective prediction policy fixture design](frozen_selective_prediction_policy_fixture_design.md)
- [Frozen selective prediction policy schema design](frozen_selective_prediction_policy_schema_design.md)
- [Frozen selective prediction policy fixtures](../tests/fixtures/learner_state_frozen_selective_prediction_policy/README.md)
- [Frozen policy validator Makefile target design](frozen_policy_validator_makefile_target_design.md)
- [Frozen policy release-quality integration design](frozen_policy_release_quality_integration_design.md)
- [Selective prediction and calibration scaffold design](selective_prediction_calibration_scaffold_design.md)
- [No-oracle policy](03_no_oracle_policy.md)
- [Synthetic data policy](12_synthetic_data_policy.md)
- [Public release checklist](public_release_checklist.md)
