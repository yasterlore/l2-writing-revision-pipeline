# Makefile Parallel Execution And Tmp-Output Safety Design

This document describes parallel execution and shared `tmp/` output safety for
the thin Makefile entrypoint introduced in Step 148.

This began as design documentation. Step 151 implemented minimal Makefile
sequential safety guidance by adding `.NOTPARALLEL` and a short `make help`
warning. It does not add or remove Makefile targets, add lock files, isolate
temp directories, change scripts, change workflows, change tests, change scorer
logic, change the manifest schema, or evaluate performance.

## 1. Purpose

The purpose of this design is to make the ordering and `tmp/` sharing risks
explicit after adding the Makefile entrypoint.

The summary flow depends on generated files under `tmp/synthetic_e2e_summary/`.
Some commands generate those files and other commands read them. Those commands
must not be treated as independent parallel steps unless a future implementation
adds stronger coordination.

This is not a performance evaluation and does not make claims about model
quality, scorer quality, research readiness, production readiness, or
data-collection readiness.

## 2. Current State

Current state:

- `Makefile` is a thin entrypoint that calls existing scripts and commands.
- `check-summary-flow` runs:
  `summary -> manifest sync -> diagnostic distribution`.
- `tmp/synthetic_e2e_summary/` is generated and then read by follow-up checks.
- `check-release-quality` calls the existing release-quality wrapper script.
- Makefile now uses `.NOTPARALLEL` as a Make-level guard against accidental
  parallel target execution.
- `make help` warns not to use `make -j` with summary-flow targets.
- shell scripts do not currently enforce global parallel safety outside Make.
- GitHub Actions workflows still call their existing commands and are not
  switched to Makefile targets.

## 3. Observed Issue

During Step 149 verification, a direct-script check was run while other commands
were also operating on `tmp/` outputs. The diagnostic distribution check saw an
inconsistent no-config summary precondition and failed closed with a
`malformed_header` precondition failure.

After regenerating the summary and rerunning the dependent checks in order, the
diagnostic distribution check passed.

This was an orchestration and shared-output dependency issue. It was not a
model failure, scorer failure, manifest schema change, or research-performance
finding.

No raw summary body, manifest body, JSONL body, diagnostic body, config body, or
candidate score rows are needed to diagnose this class of issue.

## 4. Risk Analysis

Key risks:

- `make -j` can run independent requested targets concurrently.
- `check-manifest-sync` or `check-diagnostic-distribution` can read
  `tmp/synthetic_e2e_summary/` while `check-summary` is regenerating it.
- stale `tmp/` outputs can look present but represent a previous run.
- partial or incomplete writes can be read before generator completion.
- direct script execution and Makefile execution can be mixed in the same
  workspace.
- local behavior can differ from CI if commands are run manually in a different
  order.

The current fail-closed behavior is useful: malformed or incomplete generated
state should fail as a safe precondition failure rather than silently pass.

## 5. Affected Targets / Scripts

Affected Makefile targets:

| Target | Role | Parallel/tmp-output concern |
| --- | --- | --- |
| `check-summary` | Generates `tmp/synthetic_e2e_summary/`. | Should not run concurrently with readers of the same output. |
| `check-manifest-sync` | Reads `summary.manifest.json`. | Requires completed summary generation. |
| `check-diagnostic-distribution` | Reads summary and manifest outputs. | Requires completed summary generation and valid manifest. |
| `check-summary-flow` | Runs the ordered summary flow. | Canonical safe target for this flow. |
| `check-release-quality` | Calls the success-path wrapper. | Uses wrapper-defined ordering. |
| `check-all` | Delegates to `check-release-quality`. | Avoids a second full-order implementation. |

Affected scripts:

- `scripts/run_synthetic_e2e_summary.sh`
- `scripts/check_summary_manifest_schema_sync.sh`
- `scripts/check_synthetic_diagnostic_distribution.sh`
- `scripts/check_release_quality.sh`

Other smoke scripts also write under `tmp/`. They should not be assumed to be
safe for arbitrary parallel execution unless their output paths and dependencies
are reviewed.

## 6. Safety Options

### Option A: Docs Warning Only

Pros:

- no implementation churn
- preserves current script behavior
- clarifies the safe manual workflow quickly

Cons:

- does not prevent accidental `make -j` usage
- relies on developer discipline

### Option B: Add `.NOTPARALLEL` To Makefile

Pros:

- simple Make-level guard
- reduces accidental parallel target execution
- fits the current thin Makefile model

Cons:

- requires a Makefile change in a later step
- does not prevent direct script concurrency outside Make

### Option C: Mark Specific Targets As Sequential-Only In Comments

Pros:

- low risk
- helps contributors understand `check-summary-flow`

Cons:

- does not enforce behavior
- comments can be missed

### Option D: Summary Flow Lock File

Pros:

- can prevent simultaneous generator/checker access to the same shared output
- can protect both Makefile and direct script execution if implemented in
  scripts

Cons:

- introduces lock lifecycle concerns
- stale lock handling must be safe
- higher complexity than the current need

### Option E: Stronger Atomic Output / Marker Validation

Pros:

- makes incomplete or stale output easier to detect
- complements existing fail-closed validation

Cons:

- requires script or generator changes
- does not by itself prevent concurrent writers

### Option F: Per-Run Temp Directory Isolation

Pros:

- avoids shared-output collisions
- improves reproducibility for concurrent runs

Cons:

- larger workflow and script change
- requires path plumbing across generator and checkers

### Option G: Python Or Rust Orchestrator

Pros:

- can model dependencies, stages, and failure classification explicitly
- can produce structured safe summaries

Cons:

- much larger migration
- premature for the current thin-entrypoint goal

## 7. Recommended Approach

Initial recommendation:

- treat `make check-summary-flow` as the canonical summary-flow target
- do not run `check-summary`, `check-manifest-sync`, and
  `check-diagnostic-distribution` as parallel targets
- do not use `make -j` for summary-flow targets
- keep `scripts/check_release_quality.sh` and `make check-release-quality` as
  the normal release-quality path
- use the Step 151 `.NOTPARALLEL` and help guidance as the initial Make-level
  protection
- keep current atomic write and marker validation behavior
- defer lock files and per-run temp directory isolation until the need is
  clearer
- do not change CI workflows in this design step

The short-term fix should be Makefile-level guidance or serialization, not a
full orchestrator rewrite.

## 8. Migration Safety Rules

Future changes must:

- preserve existing script behavior
- preserve the `summary -> manifest sync -> diagnostic distribution` order
- avoid printing raw JSONL, summary, manifest, diagnostic, config, or candidate
  score bodies
- keep failures safe and precondition-oriented when generated state is invalid
- keep `tmp/` and generated outputs out of Git
- avoid changing scorer logic, scoring formula, tie-break behavior, manifest
  schema, fixtures, or weights
- avoid performance, research-readiness, production-readiness, or
  data-collection-readiness claims

## 9. Developer Guidance

Recommended developer workflow:

- use `make check-summary-flow` for summary, manifest sync, and diagnostic
  distribution together
- avoid `make -j` with summary-related targets
- avoid running summary generation and summary readers concurrently in the same
  workspace
- if `malformed_header` or another safe precondition failure appears, regenerate
  the summary and rerun the dependent checks in order
- use `make check-release-quality` or `scripts/check_release_quality.sh` for the
  normal success-path release-quality check
- do not paste raw `tmp/` output, raw logs, JSONL bodies, summary bodies,
  manifest bodies, config bodies, or candidate score rows into docs or issues

## 10. Future Implementation Checklist

Future implementation options to evaluate:

- decide whether additional Makefile comments for sequential-only summary
  targets are needed
- add public release checklist guidance for `make check-summary-flow`
- decide whether a summary-flow lock file is worth the added complexity
- decide whether per-run temp directory isolation is needed
- consider structured stage summaries in a Python or Rust helper if failure
  classification grows more complex

## 11. Beginner Notes

Parallel execution means running more than one command at the same time. It can
be useful for independent tests, but it is risky when one command is writing a
file while another command is reading that same file.

The summary checks use generated files under `tmp/`. The generator must finish
before the manifest and diagnostic checks read those files.

A `malformed_header` precondition failure in this context means the checker saw
generated state that was not ready or not in the expected shape. It does not
mean the research model or scorer was wrong.

Starting with Makefile guidance or a simple Make-level sequential guard is
appropriate because the project is still using lightweight synthetic-only
checks. Heavier orchestration can wait until the need is real.

## Related Documents

- [Makefile entrypoint safety review](makefile_entrypoint_safety_review.md)
- [Task runner selection design](task_runner_selection_design.md)
- [Shell script inventory and task category design](shell_script_inventory_task_category_design.md)
- [Release-quality command bundle design](release_quality_command_bundle_design.md)
- [Milestone 05 Makefile orchestration recap](milestone_05_makefile_orchestration_recap.md)
- [Milestone 05 final docs-only release review](milestone_05_final_docs_only_release_review.md)
- [Public release checklist](public_release_checklist.md)
