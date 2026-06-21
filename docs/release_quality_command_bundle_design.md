# Release-Quality Command Bundle Design

This document is design documentation and implementation notes for the
release-quality command bundle. Step 125 adds the first minimal wrapper script,
but this document does not change CI workflows, test code, summary generation,
scoring logic, scorer weights, formulas, or tie-break policy.

It is not a performance evaluation. It does not approve real-data processing,
private validation, learner-state estimation, or expected-action tuning.

## 1. Purpose

The purpose of this design is to define a safe release-quality command bundle
before implementing any wrapper script or CI job.

The bundle should reduce manual ordering mistakes, especially around:

- no-config synthetic E2E summary generation
- summary manifest schema sync
- diagnostic distribution checks

The bundle should preserve output safety and no-oracle boundaries. It should
not print generated bodies or introduce performance metrics.

## 2. Current Major Check Groups

Current release-quality checks fall into these groups:

- shell syntax checks:
  `sh -n` for release-relevant shell scripts
- synthetic E2E summary generation:
  `scripts/run_synthetic_e2e_summary.sh`
- summary manifest schema sync:
  `scripts/check_summary_manifest_schema_sync.sh`
- diagnostic distribution check:
  `scripts/check_synthetic_diagnostic_distribution.sh`
- config-enabled summary smoke:
  `scripts/check_config_enabled_summary_smoke.sh`
- config-enabled E2E smoke:
  `scripts/check_config_enabled_e2e_smoke.sh`
- no-config scoring fixture lock:
  `scripts/check_no_config_scoring_fixture_lock.sh`
- hand-weight config validation:
  `scripts/check_hand_weight_config_validation.sh`
- explicit config ranking diff:
  `scripts/check_explicit_config_ranking_diff.sh`
- Python checks:
  `PYTHONPATH=python python3 -m unittest discover -s python` and
  `PYTHONPATH=python python3 -m compileall python`
- Rust checks:
  `cargo fmt --all -- --check`, `cargo test --workspace`, and
  `cargo clippy --workspace -- -D warnings`
- synthetic policy check:
  `scripts/check_synthetic_policy.sh`
- logger-web checks:
  typecheck, test, and build under `apps/logger-web`
- Markdown link check
- `git diff --check`
- conflict marker grep

These checks are repository safety, wiring, schema, and regression checks. They
are not accuracy, F1, calibration, ranking-quality, grammar-correctness, or
learner-state checks.

## 3. Recommended Execution Order

Initial recommended order:

1. Repository state and shell syntax checks
2. Markdown link check
3. Python unit tests and compile check
4. Rust fmt, tests, and clippy
5. logger-web typecheck, test, and build
6. synthetic policy check
7. no-config synthetic summary generation
8. summary manifest schema sync check
9. diagnostic distribution check
10. config-enabled summary smoke
11. config-enabled E2E smoke
12. no-config scoring fixture lock
13. hand-weight config validation
14. explicit config ranking diff
15. `git diff --check`
16. conflict marker grep

The summary-dependent checks must keep this local order:

```bash
scripts/run_synthetic_e2e_summary.sh
scripts/check_summary_manifest_schema_sync.sh
scripts/check_synthetic_diagnostic_distribution.sh
```

The sync check should run after summary generation and before the diagnostic
distribution check so schema drift fails early. If the diagnostic distribution
check is run first, it must still be sequential and after summary generation;
parallel execution with the summary generator is unsafe.

Config-enabled summary checks should remain separate from the no-config summary
manifest checks.

## 4. Command Bundle Options

### Option A: Docs-Only Checklist

Keep the release-quality bundle as a documented command order.

This is the safest current option because it does not change scripts, CI, or
test runners. It is more manual, so reviewers must follow the order carefully.

### Option B: Shell Wrapper Script

Create a shell wrapper such as `scripts/check_release_quality.sh`.

This would reduce manual ordering errors and can fit the current shell-first
workflow. It should be introduced only after the command order is stable.

### Option C: Makefile Target

Add a `make` target for the command bundle.

This can be convenient, but the repository does not currently rely on Make as
the main command surface.

### Option D: CI Workflow Job

Add the command bundle to CI.

This improves repeatability, but CI integration should come after the manual
bundle is stable and after output safety is reviewed.

### Option E: Python Orchestrator

Create a Python orchestration script.

This can provide richer reporting, but it is more machinery than needed while
the checks are shell-first and mostly independent.

## 5. Recommended Approach

Initial recommendation from Step 124:

- keep a docs-only checklist until the order is reviewed
- consider a shell wrapper script next
- defer CI workflow integration to a later step
- introduce Makefile or Python orchestration only if the bundle becomes hard to
  maintain as shell
- keep no-config summary checks and config-enabled summary checks separate
- keep logs safe and body-suppressed

Step 125 implements the first shell wrapper:

```bash
scripts/check_release_quality.sh
```

The wrapper preserves the existing command surfaces, runs normal success-path
checks sequentially, and enforces the critical no-config summary ordering. It
does not add CI integration or expected-failure regression phases.

## 6. Fail-Fast Policy

The future bundle should fail fast.

Recommended fail-fast rules:

- run syntax checks before generated-output checks
- run no-config summary generation before manifest sync and distribution
  checks
- stop if summary generation fails
- stop if manifest sync fails
- treat missing summary as failure
- keep `no_cases` as failure, not a silent pass
- keep malformed marker or schema mismatch as failure
- run `git diff --check` before final conflict marker grep

Expected-failure regression checks can be either:

- kept inside their existing dedicated scripts, or
- run as separate wrapper phases only if they can stay safe and body-suppressed

The bundle should not duplicate complex expected-failure tests unless the output
stays safe and maintenance remains clear.

## 7. Output Safety Policy

The bundle may print only:

- safe command names
- safe status labels
- safe repository-relative paths
- safe counts
- safe reason codes

The bundle must not print:

- raw summary body
- marker JSON body
- JSONL body
- diagnostic summary body
- candidate score rows
- config body
- raw learner text
- expected action details
- performance metrics
- real participant data

Logs should remain safe for public review.

## 8. CI And Manual Guidance

Manual release-quality review should follow the documented command order until
a wrapper or CI job exists.

Future CI guidance:

- run dependency setup before the bundle
- avoid parallel execution for summary generation, manifest sync, and
  diagnostic distribution checks
- keep `tmp/` outputs ignored
- keep failure logs safe and count-only
- run conflict marker grep after docs merges and conflict resolution
- keep config-enabled checks separate from no-config summary manifest checks

Any CI integration should be reviewed separately.

For a dedicated design of future CI integration for
`scripts/check_release_quality.sh`, see
[release-quality wrapper CI integration design](release_quality_wrapper_ci_integration_design.md).

## 9. Wrapper Script Design

The initial wrapper is named:

```bash
scripts/check_release_quality.sh
```

It should:

- call commands sequentially
- stop on first failure
- print safe status only
- avoid printing file bodies
- enforce the summary generation, manifest sync, and distribution order
- keep config-enabled and no-config checks separated
- leave expected-failure tests inside existing scripts unless a safe wrapper
  phase is clearly needed
- avoid changing scorer, pipeline, or config behavior

The wrapper should not become a performance report.

Markdown link checking remains a manual step in the wrapper because there is no
existing project command dedicated to it. The wrapper prints a safe note rather
than introducing a new checker.

Conflict marker grep is included as a normal success-path hygiene check. It
excludes `.git`, `target`, `node_modules`, `tmp`, and generated web build
directories, and reports only file and line locations when markers are found.

## 10. Beginner Notes

A command bundle is a planned list of checks to run together.

Order matters because some checks depend on files generated by earlier commands.
Here, the no-config summary must exist before the manifest sync check and
diagnostic distribution check can make sense.

The manifest sync check runs after summary generation because it compares the
generated manifest with shared schema constants. Running it before generation
would only test a missing precondition.

The wrapper script is not created immediately because the command order should
be reviewed first. A wrapper makes mistakes harder to make, but it also becomes
another maintained tool.

This is not performance evaluation. It only checks synthetic wiring, safe
metadata, repository health, and regression boundaries.

## 11. Related Documents

- [Summary manifest sync check release integration design](summary_manifest_sync_check_release_integration_design.md)
- [Summary manifest schema sync check design](summary_manifest_schema_sync_check_design.md)
- [Synthetic diagnostic distribution check ordering design](synthetic_diagnostic_distribution_check_ordering_design.md)
- [Release-quality wrapper CI integration design](release_quality_wrapper_ci_integration_design.md)
- [Public release checklist](public_release_checklist.md)
- [Milestone 03 final docs-only release review](milestone_03_final_docs_only_release_review.md)
