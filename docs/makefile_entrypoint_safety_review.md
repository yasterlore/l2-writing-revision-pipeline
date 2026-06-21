# Makefile Entrypoint Safety Review

This document reviews the thin Makefile entrypoint introduced in Step 148 and
describes how it should be adopted safely.

It is review documentation only. It does not change the Makefile, add targets,
change workflows, change scripts, change tests, change scorer logic, change the
manifest schema, or evaluate performance.

## 1. Purpose

The purpose of this review is to confirm that the Makefile remains a thin
entrypoint over existing safe scripts and commands.

The Makefile is not a replacement for the shell scripts. It is a command menu
that makes common checks easier to discover while preserving the established
script behavior and output-safety boundaries.

This review is not a performance evaluation and does not make claims about
model quality, scoring accuracy, production readiness, research readiness, or
data-collection readiness.

## 2. Current State

Current state:

- `Makefile` exists at the repository root.
- The default target is `help`.
- `check-release-quality` calls `scripts/check_release_quality.sh`.
- `check-summary-flow` preserves the required
  `summary -> manifest sync -> diagnostic distribution` order.
- `check-all` delegates to `check-release-quality`.
- GitHub Actions workflows are unchanged by the Makefile introduction.
- Existing shell scripts are unchanged and remain directly runnable.
- Scorer logic, scoring formula, tie-break behavior, manifest schema, fixtures,
  and weights are unchanged.

## 3. Implemented Targets Review

Implemented targets:

| Target | Role | Notes |
| --- | --- | --- |
| `help` | Lists available Makefile targets. | Default target. |
| `check-release-quality` | Runs the normal success-path release-quality bundle. | Calls `scripts/check_release_quality.sh`. |
| `check-summary` | Generates the no-config synthetic E2E summary. | Calls `scripts/run_synthetic_e2e_summary.sh`. |
| `check-manifest-sync` | Checks generated manifest values against shared schema constants. | Calls `scripts/check_summary_manifest_schema_sync.sh`. |
| `check-diagnostic-distribution` | Checks the synthetic diagnostic distribution after summary generation. | Calls `scripts/check_synthetic_diagnostic_distribution.sh`. |
| `check-summary-flow` | Runs the ordered no-config summary flow. | Runs summary, manifest sync, then diagnostic distribution. |
| `check-config-smoke` | Runs config-enabled summary and E2E smoke checks. | Calls existing config smoke scripts. |
| `check-python` | Runs Python unit tests and compileall. | Uses the existing Python test commands. |
| `check-rust` | Runs Rust fmt, tests, and clippy. | Uses the existing Cargo commands. |
| `check-logger` | Runs logger-web typecheck, test, and build. | Uses existing npm commands in `apps/logger-web`. |
| `check-policy` | Runs synthetic policy checks. | Calls `scripts/check_synthetic_policy.sh`. |
| `check-fixtures` | Runs no-config lock and explicit config validation checks. | Calls existing fixture/config scripts. |
| `check-all` | Runs the normal release-quality path. | Delegates to `check-release-quality`. |

## 4. Thin Wrapper Review

The Makefile remains a thin wrapper because:

- it does not copy shell script bodies into Make recipes
- it does not implement complex shell control logic
- it does not parse generated JSON, CSV, JSONL, marker, or config bodies
- it does not `cat` generated files
- it does not print raw JSONL, summary bodies, marker bodies, diagnostic
  bodies, config bodies, candidate score rows, or raw learner text
- it calls existing scripts and commands instead of changing their behavior

This preserves the existing compatibility layer while improving command
discovery.

## 5. Order Dependency Review

The most important ordering dependency is the no-config summary flow:

1. `scripts/run_synthetic_e2e_summary.sh`
2. `scripts/check_summary_manifest_schema_sync.sh`
3. `scripts/check_synthetic_diagnostic_distribution.sh`

`check-summary-flow` keeps that order explicitly.

`check-release-quality` still uses the order defined by
`scripts/check_release_quality.sh`. The Makefile does not duplicate that
wrapper's internal ordering.

`check-all` avoids a second implementation of the full command bundle by
delegating to `check-release-quality`.

The Makefile should not be treated as parallel-safe orchestration. Dependent
checks should be run through the explicit ordered targets.

## 6. Adoption Guidance

Recommended local usage:

- run `make help` to discover available targets
- run `make check-release-quality` for the normal release-quality success path
- run `make check-summary-flow` when reviewing only the no-config summary,
  manifest sync, and diagnostic distribution path
- run individual targets for focused local reruns after a failure
- keep direct script commands available for debugging and compatibility

CI should not be switched to Makefile targets automatically in this step.
Future CI adoption should be designed separately so trigger behavior, job
structure, logs, and failure handling remain clear.

## 7. Future Target Policy

Add a future target only when:

- it improves discoverability for an existing safe command or script
- it preserves existing behavior
- it keeps output safe and count/status-oriented
- the target name is stable and clear
- the target does not duplicate script internals

Do not add a future target when:

- the command is still experimental or unclear
- it would require copying complex shell logic into Make
- it would mix expected-failure tests into the normal success wrapper
- it would print generated bodies or raw logs
- it would imply performance, production, research, or data-collection
  readiness

If Makefile recipes begin to need structured stage metadata, retries, or rich
failure classification, the project should reconsider a Python or Rust helper
rather than growing complex Make logic.

## 8. Safety / No-Oracle Policy

The Makefile adoption must preserve these boundaries:

- no real participant data
- no raw JSONL body output
- no summary, marker, diagnostic, config, or candidate score body output
- no expected action details used as scoring feedback
- no F1, accuracy, calibration, learner-state estimation, or performance
  metric implementation
- no production or data-collection readiness claim
- no changes to scorer logic, scoring formula, tie-break behavior, manifest
  schema, fixtures, or weights

The Makefile is reliability and developer-experience infrastructure only.

## 9. Remaining Risks

Remaining risks:

- Makefile tab syntax can be easy to break in future edits
- future targets could duplicate existing wrapper behavior if not reviewed
- `check-all` and `check-release-quality` may be confused unless documented
- Markdown link check remains a manual note inside the release-quality wrapper
- stage metadata and failure classification remain lightweight
- future CI adoption of Makefile targets is not yet decided

These are not current blockers for using the Makefile as a local thin
entrypoint.

## 10. Future Options

Future options:

- decide whether CI should call Makefile targets or continue calling scripts
- document a stable Makefile target naming convention
- add a small README quickstart for common Make targets
- move structured stage metadata to a Python or Rust helper if needed
- re-evaluate justfile only if readability becomes more important than avoiding
  a new dependency
- keep Airflow and Dagster out of scope unless production-like orchestration
  requirements appear later

## 11. Beginner Notes

The Makefile is a command menu. It is not the new pipeline implementation.

The shell scripts are still important because they contain the existing working
behavior. Keeping them means contributors can use either the familiar script
commands or the shorter Make targets.

`check-release-quality` runs the existing release-quality wrapper.
`check-all` currently points to the same wrapper so the project does not have
two separate definitions of the full success-path check.

CI is not immediately switched to Makefile targets because remote workflow
changes need their own review. Local developer convenience and CI job structure
are related, but they should move in separate, controlled steps.

## Related Documents

- [Task runner selection design](task_runner_selection_design.md)
- [Shell script inventory and task category design](shell_script_inventory_task_category_design.md)
- [Orchestration modernization design](orchestration_modernization_design.md)
- [Release-quality command bundle design](release_quality_command_bundle_design.md)
- [Public release checklist](public_release_checklist.md)
