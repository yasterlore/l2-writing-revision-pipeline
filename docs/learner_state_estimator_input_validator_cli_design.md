# Learner-State Estimator Input Validator CLI Design

This document designs a future safe command-line interface for the
learner-state estimator input validator.

Step197 follow-up: the minimal CLI is implemented as
`PYTHONPATH=python python3 -m learner_state.estimator_input`, with CLI tests in
`python/learner_state/tests/test_estimator_input_cli.py`. The implementation
supports fixture-case mode, fixture-root mode, safe JSON output, help, default
expected-result matching, and safe count/reason-code summaries.

This document remains the CLI design reference. Step197 does not add a
Makefile target, release-quality integration, workflow change, learner-state
estimator, estimator training code, selective prediction, calibration, a new
model, or a new metric. It is not performance evaluation and it is not a
real-data readiness claim.

## 1. Purpose

The purpose of the estimator input validator CLI is to let developers run the
existing synthetic-only estimator input validation API from a terminal while
preserving the same safe-output boundary as the Python module.

The design defines:

- CLI entrypoint options
- single fixture case mode
- fixture root mode
- expected-result matching
- exit codes
- safe human output
- safe JSON output
- path safety
- future tests
- future Makefile and release-quality integration boundaries

The CLI should remain a thin wrapper over the existing Python API. It should
not duplicate validation logic and should not introduce model training,
metrics, calibration, scoring feedback, or real-data handling.

## 2. Current State

Current assets:

- `python/learner_state/estimator_input.py` exists.
- The Python API includes:
  - `load_estimator_input_fixture(case_dir)`
  - `validate_estimator_input_fixture(case_dir)`
  - `load_expected_input_validation_result(case_dir)`
  - `compare_validation_result_to_expected(result, expected)`
  - `discover_estimator_input_fixture_cases(root)`
- Fixture root exists:
  - `tests/fixtures/learner_state_estimator_input/`
- Valid fixture exists:
  - `valid/minimal_single_sequence/`
- Invalid fixtures exist:
  - `invalid/label_in_features/`
  - `invalid/missing_label_row/`
  - `invalid/extra_label_row/`
  - `invalid/join_key_mismatch/`
  - `invalid/split_leakage_same_participant/`
  - `invalid/future_feature_leakage/`
  - `invalid/forbidden_feature_field/`
  - `invalid/unknown_schema_version/`
- Fixture-based unittest coverage exists:
  - `python/learner_state/tests/test_estimator_input.py`
- CLI exists as `python -m learner_state.estimator_input`.
- CLI tests exist:
  - `python/learner_state/tests/test_estimator_input_cli.py`
- Makefile target does not exist yet.
- Release-quality integration does not exist yet.

The existing module is a validator/loader only. It does not implement a
learner-state estimator, training loop, selective prediction, calibration, or
performance metrics.

## 3. Proposed CLI Entrypoint

Candidate entrypoints:

| Entrypoint | Benefits | Costs |
| --- | --- | --- |
| `PYTHONPATH=python python3 -m learner_state.estimator_input` | Keeps CLI beside the existing validator API; mirrors the exporter CLI pattern; easy to discover | Adds argument parsing to the module |
| `PYTHONPATH=python python3 -m learner_state.estimator_input_cli` | Keeps the validator module smaller; separates CLI wiring from API logic | Adds another module and import surface |

Implemented initial entrypoint:

Use `PYTHONPATH=python python3 -m learner_state.estimator_input`.

Rationale:

- The current module is still small.
- The exporter already uses module-local `main()` successfully.
- A thin `main()` can call existing APIs without duplicating validation logic.
- If CLI behavior grows, a later step can split the CLI into
  `learner_state.estimator_input_cli` without changing the validation API.

## 4. CLI Modes

Implemented initial modes:

- single fixture case mode:
  - `--fixture-case <case_dir>`
- fixture root mode:
  - `--fixture-root <root_dir>`
- safe JSON output:
  - `--json`
- help:
  - `--help`

Optional future arguments:

- `--strict`
- `--expect`
- `--validation-only`
- `--no-color`

Implemented initial behavior:

- Support exactly one of `--fixture-case` or `--fixture-root`.
- In fixture case mode, compare `expected_input_validation_result.json` by
  default when the file exists.
- In fixture root mode, discover all cases with
  `expected_input_validation_result.json` and compare every expected result.
- Keep validation-only mode as a future option. The first CLI should optimize
  for fixture safety smoke, not arbitrary dataset validation.
- Keep color disabled by default and avoid adding a color option initially.

## 5. Command Examples

Validate one fixture case:

```bash
PYTHONPATH=python python3 -m learner_state.estimator_input --fixture-case tests/fixtures/learner_state_estimator_input/valid/minimal_single_sequence
```

Validate all estimator input fixture cases:

```bash
PYTHONPATH=python python3 -m learner_state.estimator_input --fixture-root tests/fixtures/learner_state_estimator_input
```

Validate all fixture cases with safe JSON summary:

```bash
PYTHONPATH=python python3 -m learner_state.estimator_input --fixture-root tests/fixtures/learner_state_estimator_input --json
```

Expected-result matching mode:

- single-case mode should compare the case's
  `expected_input_validation_result.json` by default if present
- fixture-root mode should always compare expected validation results

Docs may show command shapes, but should not show `features.jsonl`,
`labels.jsonl`, `manifest.json`, expected-action, or fixture row bodies.

## 6. Exit Code Design

Recommended exit codes:

- `0`: validation passed, or fixture-root expected results all matched
- `1`: raw validation failed for a dataset/case when no expected-result
  comparison mode is active
- `2`: usage error, missing files, malformed input, or unsafe path
- `3`: expected-result mismatch in fixture test mode

Single fixture case mode:

- If `expected_input_validation_result.json` exists and the result matches,
  exit `0` even when the fixture is intentionally invalid.
- If expected-result matching finds a mismatch, exit `3`.
- If the case cannot be loaded because of usage-like problems, exit `2`.
- If a future validation-only mode is added, an invalid dataset should exit
  `1` because the caller is asking whether the dataset itself is valid.

Fixture root mode:

- Exit `0` only when every discovered fixture matches its expected result.
- Exit `3` when one or more expected results mismatch.
- Exit `2` for root path, discovery, missing-file, malformed-input, or unsafe
  path errors that prevent expected-result matching from running safely.

The command must never silently pass unknown failures.

## 7. Safe Human Output

Single-case human summary should include safe fields such as:

- `mode`
- `case`
- `validation_status`
- `reason_codes`
- `failed_checks`
- `feature_row_count`
- `label_row_count`
- `sequence_count`
- `split_counts`
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only_checked`
- `no_oracle_checked`
- `expected_result_matched`

Fixture-root human summary should include:

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

Forbidden output:

- feature row body
- label row body
- manifest body
- expected-action body
- raw learner text
- private absolute paths
- malformed line body
- raw stack trace with row content
- performance metrics

For paths, prefer a safe case name or relative fixture path. Do not print
private absolute paths.

## 8. Safe JSON Output

Safe JSON output should be machine-readable and limited to validation metadata.

Single-case JSON should contain:

- `mode`
- safe `EstimatorInputValidationResult.to_safe_dict()` fields
- `expected_result_matched`
- mismatch field names when relevant
- safe case label

Fixture-root JSON should contain:

- `mode`
- `total_cases`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `reason_code_counts`
- case-level safe summaries if needed
- `content_suppressed: true`
- `no_raw_rows: true`

JSON output must not include:

- raw feature rows
- raw label rows
- full manifest body
- expected-action body
- raw learner text
- private absolute paths
- generated output bodies
- performance metrics

## 9. Fixture-Root Behavior

Fixture-root mode should:

- discover fixture case directories deterministically
- include valid and invalid cases
- require `expected_input_validation_result.json` for every discovered case
- call `validate_estimator_input_fixture(case_dir)`
- load expected results with `load_expected_input_validation_result(case_dir)`
- compare with `compare_validation_result_to_expected(result, expected)`
- count:
  - `total_cases`
  - `matched_cases`
  - `mismatched_cases`
  - `input_error_cases`
- aggregate safe `reason_code_counts`
- exit `0` only when all expected results match

Fixture-root mode should not:

- print row bodies
- print manifest bodies
- print label bodies
- print expected-action bodies
- expose private absolute paths
- treat intentional invalid fixture failures as CLI failures when expected
  results match

## 10. Single-Case Behavior

Single-case mode should:

- validate exactly one fixture case
- use safe case labeling
- return safe validation metadata
- compare `expected_input_validation_result.json` by default when present
- report `expected_result_matched=true` or `false`
- exit `0` when an intentional invalid fixture matches its expected result
- exit `3` when validation result and expected result disagree

Future option:

- a later `--validation-only` mode may ignore expected-result files and answer
  only whether the case is valid as a dataset. That mode should exit `1` for
  invalid inputs.

The initial CLI should favor expected-result matching because the current
fixture root intentionally contains invalid cases.

## 11. Path Safety

The CLI should reject input paths containing:

- `real_data`
- `participant_data`
- `private_data`
- `manual_outputs`

Allowed:

- fixture paths under `tests/fixtures/learner_state_estimator_input/`
- other explicitly reviewed synthetic paths in future steps

Output policy:

- the validator CLI should not write generated dataset outputs
- it should only print safe summaries
- it should not create `tmp/` outputs in the initial implementation

Path display:

- prefer safe relative fixture paths or case names
- do not print private absolute paths
- do not include full local workspace paths in JSON summaries

## 12. Relation to Python API

The CLI should wrap the existing Python API:

- use `validate_estimator_input_fixture`
- use `load_expected_input_validation_result`
- use `compare_validation_result_to_expected`
- use `discover_estimator_input_fixture_cases`

The Python API remains the primary implementation surface. CLI tests should
exercise argument parsing, output safety, JSON safety, exit codes, and
fixture-root orchestration without duplicating validation logic.

## 13. Testing Plan And Implementation Status

Step197 CLI tests cover:

- `--help`
- valid single case exits `0`
- invalid single case exits `0` when expected-result matching succeeds
- fixture-root mode exits `0` with all 9 cases matched
- `--json` output is parseable and safe
- missing fixture path exits `2`
- expected-result mismatch exits `3`
- no raw rows in stdout/stderr
- no full manifest body in stdout/stderr
- no label body in stdout/stderr
- no private absolute paths in stdout/stderr
- deterministic fixture discovery order

Future additions may cover malformed fixture inputs and validation-only mode if
those modes are added later.

Tests should remain synthetic-only and should not add model training, metrics,
calibration, Makefile targets, or release-quality integration.

## 14. Makefile / Release-Quality Future

This step should not add a Makefile target or release-quality integration.

Recommended future order:

1. Step197: implement minimal estimator input validator CLI. Complete.
2. Step198: design a standalone Makefile target for fixture-root validation.
3. Step199: implement the standalone Makefile target after CLI log safety
   review.
4. Later: design release-quality wrapper integration.
5. Later: run remote/manual release-quality and record public-safe status if
   integrated.

Do not connect the CLI to release-quality before local CLI log safety and
fixture-root output safety have been reviewed.

## 15. No-Oracle / Synthetic-Only Boundary

CLI safety boundary:

- current fixtures are synthetic-only
- expected action remains label-side only
- invalid fixtures may intentionally contain leakage fields, but CLI output
  should report only safe reason codes
- no real participant data
- no raw learner text
- no generated feature, label, or manifest body in output
- no expected action as scoring feedback
- no model performance claims

The CLI validates input safety. It does not make inputs useful for production
or prove estimator correctness.

## 16. What This Does NOT Do

This design does not:

- implement the CLI
- add a Makefile target
- change release-quality wrapper behavior
- change GitHub Actions workflows
- implement a learner-state estimator
- implement estimator training
- implement selective prediction
- implement calibration
- implement F1, accuracy, ECE, AURCC, or other metrics
- use real data
- change exporter code
- change audit code
- change fixture files
- change candidate generation, OT scoring, scoring formula, or tie-break logic
- change manifest schema
- claim production readiness

## 17. Beginner Notes

A CLI is a terminal command. It lets a developer run validation without writing
a Python script.

The API already does the real work. The CLI is useful because Makefile targets,
release checks, and local smoke checks can call a stable command.

An exit code is the number a command returns when it finishes. `0` usually
means success. Nonzero values tell shell scripts and CI that something failed.

Human output is for people reading the terminal. JSON output is for scripts.
Both should contain only safe counts, statuses, and reason codes here.

Row bodies are hidden because they can contain labels, expected actions, raw
text, or private details in future datasets. The validator only needs to say
what passed or failed, not show the underlying data.

## 18. Related Documents

- [Learner-state estimator input contract design](learner_state_estimator_input_contract_design.md)
- [Learner-state estimator input fixture design](learner_state_estimator_input_fixture_design.md)
- [Learner-state estimator input validation design](learner_state_estimator_input_validation_design.md)
- [Learner-state estimator input fixtures](../tests/fixtures/learner_state_estimator_input/README.md)
- `python/learner_state/estimator_input.py`
- `python/learner_state/tests/test_estimator_input_cli.py`
- [Learner-state sequence exporter design](learner_state_sequence_exporter_design.md)
- [Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
- [Public release checklist](public_release_checklist.md)
