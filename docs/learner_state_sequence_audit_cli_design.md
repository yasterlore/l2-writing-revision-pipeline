# Learner-State Sequence Audit CLI Design

This document designs a future safe command-line interface for the
learner-state sequence no-oracle audit.

This is design documentation only. It does not implement a CLI, change audit
code, change fixtures, add a sequence exporter, add a learner-state estimator,
add a model, add a metric, or change production data handling. It does not
change candidate generation, OT scoring, scoring formula, tie-break behavior,
existing manifest schemas, Makefile targets, workflows, wrappers, or scripts.
It is not a performance evaluation.

## 1. Purpose

The purpose of this document is to define how a future
`python -m learner_state.sequence_audit ...` CLI should behave before the CLI is
implemented.

The CLI should be a thin interface over the existing audit module. It should
not duplicate audit logic. It should provide safe stdout, optional safe JSON
output, clear exit codes, and fixture expected-result checking without printing
raw fixture rows.

## 2. Current State

Current state:

- `python/learner_state/sequence_audit.py` exists.
- `AuditResult` is safe and count-only.
- Fixture unittest coverage exists under `python/learner_state/tests/`.
- Synthetic fixture cases live under
  [`tests/fixtures/learner_state_sequence_audit/`](../tests/fixtures/learner_state_sequence_audit/README.md).
- CLI entrypoints are not implemented.
- Makefile and release-quality integration are not implemented.

The current module can already audit a dataset trio or a fixture case from
Python API calls. The future CLI should expose that behavior safely for local
developer use.

## 3. CLI Use Cases

Candidate use cases:

| Use case | Description | Initial fit |
| --- | --- | --- |
| Single dataset audit | Audit one feature/label/manifest trio | High |
| One fixture case audit | Audit a single fixture directory and compare expected result | High |
| Fixture root audit | Enumerate all fixture cases and compare expected results | High |
| JSON result output | Emit safe machine-readable `AuditResult` fields | Medium |
| Human-readable safe summary | Emit compact status and count-only details | High |
| Future CI / Makefile use | Use CLI from top-level targets or wrappers | Later |

Initial CLI scope should include single dataset mode and fixture-root mode.
One-fixture mode is useful for targeted debugging. JSON output can be included
only if it reuses safe `AuditResult` fields.

## 4. CLI Commands / Arguments Design

Candidate commands:

```bash
python -m learner_state.sequence_audit --features <path> --labels <path> --manifest <path>
python -m learner_state.sequence_audit --fixture-case <dir>
python -m learner_state.sequence_audit --fixture-root <dir>
```

Candidate flags:

- `--json`: print safe JSON result or aggregate safe JSON result
- `--summary-only`: print human-readable count-only summary
- `--strict`: treat warning-like conditions as failures if future warnings are added
- `--no-color`: keep output stable for logs and tests

Initial recommendation:

- implement exactly one mode per invocation
- require one of dataset mode, fixture-case mode, or fixture-root mode
- default to human-readable safe summary
- support `--json` only if tests prove output stays safe
- avoid color by default; `--no-color` may be unnecessary if no color is used
- do not add Makefile target in the first CLI step

## 5. Output Format Design

Human summary should include:

- `audit_status`
- `violation_count`
- `reason_codes`
- `checked_files_count`
- `content_suppressed`
- `no_raw_rows`

Fixture-root summary should include:

- total fixture cases checked
- pass cases count
- expected-fail cases count
- mismatch count
- aggregate reason codes
- `content_suppressed`
- `no_raw_rows`

JSON output may include only `AuditResult` safe fields, plus fixture aggregate
counts in fixture-root mode.

Forbidden output:

- raw rows
- raw JSONL body
- label body
- manifest body
- candidate score rows
- raw learner text
- expected action body
- private paths
- full stack trace with row content
- performance metrics

## 6. Exit Code Design

Recommended exit codes:

| Exit code | Meaning |
| --- | --- |
| 0 | Audit passed, or fixture cases matched expected pass/fail results |
| 1 | Audit completed and found safety violations |
| 2 | Usage error, malformed input, missing files, or unreadable input |
| 3 | Fixture expected-result mismatch |

This keeps dataset safety failures separate from usage/input failures and
fixture-test mismatches. If this feels too complex during implementation, a
simpler scheme may use `0` for pass and nonzero for all failures, but the CLI
should still print safe reason codes.

## 7. Path Safety

Path policy:

- reject `real_data`, `participant_data`, and `private_data` as dataset source
  path segments
- reject private absolute paths in public output
- reject `manual_outputs` as a public dataset source
- allow the synthetic unsafe-path fixture only in fixture-testing context so
  the audit can prove it catches the unsafe pattern
- sanitize paths in stdout and JSON
- report file roles such as `features`, `labels`, `manifest`, or fixture case
  labels rather than private absolute paths

Public docs should not include raw paths beyond repository-relative design
paths and fixture case names.

## 8. Fixture Mode Design

Fixture-root mode should:

- enumerate fixture case directories deterministically
- require `expected_audit_result.json` for each case
- audit each fixture case through `audit_fixture_case`
- compare results through `compare_audit_result_to_expected`
- treat valid fixture pass and invalid expected failure as overall success
- report aggregate counts only
- report mismatches with safe case labels and reason codes
- never print feature rows, label rows, manifest bodies, or raw expected action
  values

One-fixture mode should follow the same matching policy for a single case.

## 9. Integration Plan

Recommended order:

1. Step later: implement CLI with dataset mode and fixture-root mode.
2. Step later: add CLI smoke tests for safe stdout and exit codes.
3. Step later: optionally add Makefile target
   `check-learner-state-audit-fixtures`.
4. Step later: consider release-quality wrapper integration after CLI smoke
   tests are stable.
5. Step later: consider CI use only after local and release-quality behavior is
   predictable.

Makefile and release-quality integration should not happen before CLI output
safety is tested.

Step 167 implementation note: the minimal CLI is implemented on
`python -m learner_state.sequence_audit` with dataset, fixture-case, and
fixture-root modes. It supports default safe human summaries and `--json` safe
metadata output. It does not add a Makefile target, release-quality wrapper
integration, CI workflow changes, sequence exporter, learner-state estimator,
model, metric, or scorer change.

Step 168 follow-up: see
[Learner-state sequence audit CLI integration design](learner_state_sequence_audit_cli_integration_design.md)
for the staged plan to connect the CLI to a future Makefile target,
release-quality wrapper, and CI consideration while preserving safe output.

Step 169 follow-up: the first integration step adds
`make check-learner-state-audit-fixtures` as a manual Makefile target. It is
not part of the release-quality wrapper or CI.

## 10. Failure Policy

The CLI should fail safely on:

- missing files
- malformed JSON
- malformed JSONL
- empty feature or label input
- unknown schema version
- forbidden field
- label-feature leakage
- future leakage
- split leakage
- unsafe paths
- manifest body leakage
- expected-result mismatch in fixture mode

There should be no silent pass. Errors should identify category and reason code
without printing row body, label body, or raw text.

## 11. Relation to Existing Module/API

The CLI should call existing module APIs:

- `audit_sequence_dataset` for dataset mode
- `audit_fixture_case` for single fixture mode
- `load_expected_audit_result` for fixture expected-result loading
- `compare_audit_result_to_expected` for fixture matching

The CLI should not reimplement forbidden-field scans, path checks, split checks,
or expected-result comparison. New audit behavior should live in the module and
be covered by module tests first.

## 12. Public Docs / Logging Policy

Public docs may show example command shapes and field names.

Public docs and logs must not include:

- JSONL lines
- fixture row bodies
- manifest bodies
- label contents
- expected action body
- candidate score rows
- raw learner text
- private paths
- raw CI logs
- performance metrics

CLI examples should be command-only or show short synthetic status summaries
without generated body content.

## 13. Beginner Notes

A CLI is a command you can run from a terminal. In this case, it would let a
developer run the learner-state sequence audit without writing Python code.

The module is the actual logic. The CLI is only the front door to that logic.
Keeping them separate prevents command-line formatting from becoming mixed with
audit rules.

Exit codes let scripts tell the difference between success, safety failure,
usage error, and fixture mismatch.

Safe output is important because terminal output is often copied into issues,
docs, and CI summaries. The CLI should never normalize a habit of printing raw
dataset rows.

Makefile integration should wait until the CLI is stable because top-level
targets are easy to run repeatedly and should be boringly predictable.

## Related Documents

- [Learner-state sequence audit CLI integration design](learner_state_sequence_audit_cli_integration_design.md)
- [Learner-state sequence audit implementation design](learner_state_sequence_audit_implementation_design.md)
- [Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
- [Learner-state sequence audit fixture/schema design](learner_state_sequence_audit_fixture_schema_design.md)
- [Learner-state sequence audit fixture files design](learner_state_sequence_audit_fixture_files_design.md)
- [Learner-state sequence audit fixture files](../tests/fixtures/learner_state_sequence_audit/README.md)
- [Learner-state sequence schema design](learner_state_sequence_schema_design.md)
- [No-oracle policy](03_no_oracle_policy.md)
- [Synthetic data policy](12_synthetic_data_policy.md)
- [Public release checklist](public_release_checklist.md)
