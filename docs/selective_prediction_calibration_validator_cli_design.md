# Selective Prediction Calibration Validator CLI Design

This document designs a future command-line interface for the synthetic
selective prediction / calibration fixture validator.

It is docs-only. It does not implement a CLI, calibration, selective
prediction, a learner-state estimator, estimator training, a new model, F1,
accuracy, ECE, AURCC, metric computation, or real-data handling. It is not a
performance evaluation and is not a real-data readiness claim.

## 1. Purpose

The purpose of this document is to define a safe CLI shape for running the
minimal calibration / selective prediction fixture validator added in Step209.

The CLI should make local and future release-quality checks easy to run while
preserving the same safety boundary as the Python API:

- synthetic-only fixture inputs
- expected-result matching by default
- safe count/reason-code output only
- no prediction row body
- no label row body
- no split metadata body dump
- no calibration policy body dump
- no logits or probability body dump
- no expected action body
- no raw learner text
- no private paths

The CLI should not compute calibration parameters, tune thresholds, train a
model, evaluate model performance, or report metrics.

## 2. Current State

Current assets:

- validator Python API exists in
  `python/learner_state/selective_prediction_validation.py`
- fixture-based unittest exists in
  `python/learner_state/tests/test_selective_prediction_validation.py`
- fixture root exists at
  `tests/fixtures/learner_state_selective_prediction/`
- valid fixture:
  - `valid/minimal_validation_test_split/`
- invalid fixtures:
  - `invalid/test_threshold_tuning/`
  - `invalid/test_temperature_tuning/`
  - `invalid/label_in_confidence_feature/`
  - `invalid/missing_validation_split/`
  - `invalid/same_participant_across_splits/`
  - `invalid/future_label_aggregate/`
  - `invalid/raw_text_in_prediction_row/`

Current API surface:

- `load_selective_prediction_fixture(case_dir)`
- `validate_selective_prediction_fixture(case_dir)`
- `load_expected_calibration_validation_result(case_dir)`
- `compare_calibration_validation_result_to_expected(result, expected)`
- `discover_selective_prediction_fixture_cases(root)`

Not present yet:

- CLI entrypoint
- CLI tests
- Makefile target
- release-quality wrapper integration
- workflow integration

## 3. Proposed CLI Entrypoint

Recommended entrypoint:

```bash
PYTHONPATH=python python3 -m learner_state.selective_prediction_validation
```

Alternative:

```bash
PYTHONPATH=python python3 -m learner_state.selective_prediction_validation_cli
```

Recommendation: put the initial `main()` in
`learner_state.selective_prediction_validation`.

Reasons:

- The module is already the primary implementation surface.
- The first CLI is thin and should only wrap existing API functions.
- The command mirrors the estimator input validator pattern.
- It avoids a second module until the CLI grows enough to justify separation.

When to reconsider a separate CLI module:

- argument parsing becomes large
- subcommands are added
- fixture-root reporting needs richer formatting
- future public package boundaries need a smaller API module

## 4. CLI Modes

Required initial modes:

- single fixture case mode
  - `--fixture-case tests/fixtures/learner_state_selective_prediction/valid/minimal_validation_test_split`
- fixture root mode
  - `--fixture-root tests/fixtures/learner_state_selective_prediction`
- JSON output
  - `--json`
- help
  - `--help`

Argument rule:

- exactly one of `--fixture-case` or `--fixture-root` is required
- specifying both is a usage error
- specifying neither is a usage error

Optional future flags:

- `--strict`
- `--expect`
- `--validation-only`

Initial recommendation: do not add optional flags yet. Expected-result
matching should be the default for fixture cases when the expected file is
present.

## 5. Command Examples

Validate one valid fixture case:

```bash
PYTHONPATH=python python3 -m learner_state.selective_prediction_validation --fixture-case tests/fixtures/learner_state_selective_prediction/valid/minimal_validation_test_split
```

Validate one intentional invalid fixture case:

```bash
PYTHONPATH=python python3 -m learner_state.selective_prediction_validation --fixture-case tests/fixtures/learner_state_selective_prediction/invalid/test_threshold_tuning
```

Validate all fixture cases:

```bash
PYTHONPATH=python python3 -m learner_state.selective_prediction_validation --fixture-root tests/fixtures/learner_state_selective_prediction
```

Validate all fixture cases with safe JSON output:

```bash
PYTHONPATH=python python3 -m learner_state.selective_prediction_validation --fixture-root tests/fixtures/learner_state_selective_prediction --json
```

These commands must not print row bodies, logits/probability bodies, split
metadata bodies, calibration policy bodies, label bodies, expected action
bodies, raw learner text, or private paths.

## 6. Exit Code Design

Recommended exit codes:

- `0`: validation passed, or all fixture expected results matched
- `1`: validation failure for a future raw validation-only mode
- `2`: usage error, missing files, malformed input, unsafe path, or input error
- `3`: expected-result mismatch in fixture test mode

Single fixture case mode:

- if `expected_calibration_validation_result.json` exists, compare by default
- a valid fixture exits `0` when validation passes and expected result matches
- an intentional invalid fixture exits `0` when the expected failure reason
  matches
- expected-result mismatch exits `3`
- usage/input errors exit `2`

Fixture root mode:

- discover all fixture dirs deterministically
- compare every case to its expected result
- exit `0` only when all cases match expected results
- exit `3` if any case has expected-result mismatch
- exit `2` if fixture discovery or input loading has a usage/input error

## 7. Safe Human Output

Human summary output should include only safe metadata.

Single-case fields:

- `mode`
- `case`
- `validation_status`
- `reason_codes`
- `failed_checks`
- `prediction_row_count`
- `label_row_count`
- `split_counts`
- `policy_status`
- `expected_result_matched`
- `mismatch_fields`
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only_checked`
- `no_oracle_checked`
- `test_tuning_checked`

Fixture-root fields:

- `mode`
- `total_cases`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `reason_code_counts`
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only_checked`
- `no_oracle_checked`
- `test_tuning_checked`

Forbidden in human output:

- prediction row body
- label row body
- split metadata body
- calibration policy body
- logits body
- probability body
- expected action body
- raw learner text
- private absolute paths
- performance metrics

## 8. Safe JSON Output

JSON output should be machine-readable but safe.

Allowed:

- validation result safe dict
- safe fixture-root summary
- safe case labels
- reason-code counts
- row counts
- split counts
- mismatch field names
- `content_suppressed: true`
- `no_raw_rows: true`

Forbidden:

- raw prediction rows
- raw label rows
- full split metadata body
- full calibration policy body
- logits/probability body dump
- expected action body
- raw learner text
- private absolute paths
- model performance claims

JSON output should be parseable with `json.loads` and should preserve stable
field names for future Makefile and release-quality checks.

## 9. Fixture-Root Behavior

Fixture-root mode should:

- discover fixture dirs through `expected_calibration_validation_result.json`
- sort cases deterministically
- include both valid and invalid cases
- load expected results for every case
- validate every case using the Python API
- compare result to expected result
- report `total_cases`
- report `matched_cases`
- report `mismatched_cases`
- report `input_error_cases`
- report `reason_code_counts`
- avoid printing row bodies
- avoid printing policy or split body dumps
- exit `0` only if all expected results match

Current expected root summary after implementation should be:

- `total_cases`: `8`
- `matched_cases`: `8`
- `mismatched_cases`: `0`
- `input_error_cases`: `0`

These counts are fixture-contract smoke results, not model performance
metrics.

## 10. Single-Case Behavior

Single-case mode should:

- validate one case directory
- compare to `expected_calibration_validation_result.json` by default when it
  exists
- return exit `0` for an intentional invalid fixture if the expected result
  matches
- return exit `3` for expected-result mismatch
- return exit `2` for missing files, malformed input, unsafe path, or usage
  errors
- display a safe case label such as `valid/minimal_validation_test_split` or
  `invalid/test_threshold_tuning`

A future validation-only mode may return exit `1` for invalid data without
expected-result matching. That mode should be designed separately.

## 11. Path Safety

The CLI should reject input paths containing:

- `real_data`
- `participant_data`
- `private_data`
- `manual_outputs`

Fixture paths under `tests/fixtures` are allowed.

Output should display safe relative case labels or basenames only. It should
not print private absolute paths in stdout or stderr.

## 12. Relation to Python API

The CLI should wrap the existing Python API:

- `validate_selective_prediction_fixture`
- `load_expected_calibration_validation_result`
- `compare_calibration_validation_result_to_expected`
- `discover_selective_prediction_fixture_cases`

The CLI should not duplicate validation logic. API functions remain the
primary implementation surface, and CLI tests should focus on argument
handling, exit codes, safe stdout/stderr, JSON parseability, and expected
result matching.

## 13. Testing Plan for Future Implementation

Future CLI tests should cover:

- `--help` exits `0`
- valid single fixture exits `0`
- intentional invalid single fixture exits `0` when expected result matches
- fixture root exits `0` with 8 matched cases
- missing fixture exits `2`
- both `--fixture-case` and `--fixture-root` exits `2`
- no args exits `2`
- expected mismatch exits `3`
- JSON output is parseable
- stdout/stderr are safe
- no prediction row bodies
- no label row bodies
- no logits/probability bodies
- no split metadata body dump
- no calibration policy body dump
- no private absolute paths

Expected mismatch tests may use a temporary copied fixture with only the
expected result safely modified. The mismatch summary should name fields only,
not row contents.

## 14. Makefile / Release-Quality Future

Step211 implementation status:

- CLI implementation added in
  `python/learner_state/selective_prediction_validation.py`
- CLI tests added in
  `python/learner_state/tests/test_selective_prediction_validation_cli.py`
- fixture-case mode implemented
- fixture-root mode implemented
- safe JSON output implemented
- expected-result matching is default when expected files are present
- intentional invalid fixtures exit `0` when expected results match

Still not in this step:

- no Makefile target
- no release-quality wrapper change
- no workflow change

Future staged work:

1. Design a Makefile target.
2. Implement the Makefile target.
3. Review CLI log safety.
4. Design release-quality integration.
5. Integrate through the Makefile target if safe.

Initial release-quality integration should not call the long CLI command
directly. A Makefile target should own the command shape once it exists.

Step212 adds the
[selective prediction calibration validator Makefile target design](selective_prediction_calibration_validator_makefile_target_design.md)
as a docs-only plan for a future standalone Makefile smoke target. It
recommends `check-learner-state-selective-prediction`, the fixture-root CLI
command, safe human summary output, no tmp output, and no release-quality
connection in the design step.

## 15. No-Oracle / Synthetic-Only Boundary

The CLI must preserve these boundaries:

- fixtures are synthetic-only
- expected action remains label-side only
- intentional invalid fixtures may include leakage markers only as test
  targets
- validation reports safe reason codes only
- no real participant data
- no raw learner text
- no test tuning leakage
- no scoring feedback
- no model performance
- no production data readiness claim

Success means fixture validation and expected-result matching passed. It does
not mean calibration quality, model correctness, or estimator performance.

## 16. What This Does NOT Do

This document and Step211 implementation do not:

- add a Makefile target
- change release-quality
- change workflows
- implement calibration
- implement selective prediction
- train an estimator
- compute metrics
- compute F1
- compute accuracy
- compute ECE
- compute AURCC
- use real data
- prove performance
- claim real-data readiness

## 17. Beginner Notes

A CLI is a command-line interface: a way to run the validator from a terminal
instead of importing Python functions.

The API is useful for tests and future Python code. The CLI is useful for
humans, Makefile targets, and release-quality wrappers because it gives a
stable command with clear output and exit codes.

An exit code is the number a command returns to the shell. `0` usually means
success. Non-zero values mean different kinds of failure.

Human output is for quick reading in a terminal. JSON output is for scripts.
Both must stay safe: counts, reason codes, and flags are okay; row bodies,
logits/probability dumps, policy bodies, and raw text are not.

Row bodies and logits/probability bodies are hidden because they can become
too detailed for public logs and can accidentally carry label leakage or raw
content. The validator only needs counts and reason codes to prove the fixture
contract behaved as expected.

## 18. Related Documents

- [Selective prediction and calibration design](selective_prediction_calibration_design.md)
- [Selective prediction and calibration fixture design](selective_prediction_calibration_fixture_design.md)
- [Selective prediction and calibration validation design](selective_prediction_calibration_validation_design.md)
- [Selective prediction calibration validator Makefile target design](selective_prediction_calibration_validator_makefile_target_design.md)
- [Initial selective prediction fixtures](../tests/fixtures/learner_state_selective_prediction/README.md)
- [Learner-state estimator input validation design](learner_state_estimator_input_validation_design.md)
- [Public release checklist](public_release_checklist.md)
