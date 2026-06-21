# Orchestration Modernization Design

This document responds to an external review note that the current pipeline
relies heavily on hand-written shell script orchestration.

It is design documentation only. It does not add a Makefile, justfile, task
runner, Airflow, Dagster, workflow change, test change, or implementation
change. It is not a performance evaluation.

## 1. Purpose

The purpose of this document is to describe the current shell-script
orchestration model, acknowledge the legitimate risks, and define a staged
modernization roadmap.

The goal is not to reject the current scripts outright. The current repository
is still synthetic-only research software, and lightweight shell entrypoints are
reasonable at this stage. The goal is to make future orchestration choices more
intentional before the pipeline grows into more production-like operation.

Airflow and Dagster are not recommended immediately because the current work is
not a production data pipeline, does not process real participant data, and does
not yet need scheduled multi-DAG operations, persistent run history, or
institutional monitoring.

## 2. Current State

The repository currently spans three main implementation surfaces:

- Rust: command-line tooling, raw event validation, replay, safe-view export,
  micro-episode extraction, and no-oracle safety checks
- Python: candidate generation, feature and constraint handling, scoring,
  evaluation wiring, summary generation support, and unit tests
- TypeScript: logger-web typecheck, tests, and browser build surface

Shell scripts under `scripts/*.sh` are the main orchestration entrypoints for:

- synthetic E2E summary generation
- summary manifest sync checks
- diagnostic distribution checks
- config-enabled summary and E2E smoke checks
- no-config scoring fixture locks
- hand-weight config validation
- explicit config ranking diff checks
- synthetic policy checks
- release-quality command bundling

`scripts/check_release_quality.sh` is the normal success-path wrapper for the
release-quality command bundle. It preserves the critical order:

```bash
scripts/run_synthetic_e2e_summary.sh
scripts/check_summary_manifest_schema_sync.sh
scripts/check_synthetic_diagnostic_distribution.sh
```

GitHub Actions either runs existing CI checks or invokes the release-quality
wrapper. The current development and verification surface remains synthetic-only
and does not authorize real-data processing.

## 3. Valid Points In The External Review

The external concern is directionally valid:

- as shell scripts grow, dependency order becomes harder to see
- retry and rerun behavior is mostly manual
- structured logging and machine-readable stage summaries are limited
- Rust / Python / TypeScript boundaries are coordinated across several scripts
- failure classification can become inconsistent across scripts
- future production-like pipelines may need stronger orchestration guarantees

These issues are especially relevant if the project later adds real operational
runs, scheduled execution, multiple dependent DAGs, or long-running remote jobs.

## 4. Points Not To Over-Interpret

The current shell-script usage should not be over-read as a design failure by
itself:

- shell usage ratio alone does not determine architecture quality
- the current system is not a production data pipeline
- current checks are synthetic-only release, smoke, and safety checks
- Airflow or Dagster would be heavy machinery for the present scope
- lightweight orchestration is acceptable for a research prototype with clear
  output-safety boundaries
- no-oracle and synthetic-only constraints are more important than adopting a
  heavyweight scheduler early

The modernization path should preserve the working behavior first, then improve
entrypoint clarity and structured reporting in stages.

## 5. Orchestration Options

### Option A: Keep Current Scripts As-Is

Pros:

- no migration risk
- no new tool dependency
- current local and CI behavior stays stable

Cons:

- command order remains distributed across scripts and docs
- stage metadata stays informal
- future contributors may find the entrypoints hard to discover

Good timing: acceptable while the pipeline remains small and scripts are easy to
audit.

### Option B: Organize Shell Wrappers And Continue

Pros:

- preserves existing behavior
- improves naming, grouping, and documentation
- low migration cost

Cons:

- still limited for structured outputs and retries
- shell complexity can continue growing

Good timing: useful as a short-term cleanup before adding a top-level task
runner.

### Option C: Makefile

Pros:

- common, lightweight, and available in many environments
- good for top-level targets such as `release-quality`, `summary`, and `smoke`
- can call existing scripts without replacing them

Cons:

- shell semantics remain underneath
- portability quirks can appear across systems
- richer structured reporting still needs another layer

Good timing: reasonable near-term candidate for top-level command discovery.

### Option D: justfile

Pros:

- clearer task syntax than Make for command recipes
- good developer ergonomics
- can keep existing scripts as lower-level commands

Cons:

- adds a tool dependency
- may not be installed in all CI or contributor environments
- still not a full structured orchestrator

Good timing: reasonable near-term candidate if the team accepts the dependency.

### Option E: Python Task Runner Or CLI Orchestrator

Pros:

- can produce structured stage summaries
- can classify failures consistently
- can share validation helpers with existing Python tests
- better suited for expected-failure phases than shell alone

Cons:

- adds more code surface
- may duplicate existing script behavior during migration
- must be careful not to print generated bodies

Good timing: medium-term candidate once command targets and stage metadata are
well understood.

### Option F: Rust CLI Orchestrator

Pros:

- strong typing and good error handling
- can integrate with existing Rust CLI surfaces
- useful for safety-critical orchestration if it grows

Cons:

- higher implementation cost than a task file
- less convenient for invoking Python / Node checks unless carefully designed

Good timing: medium-to-long-term candidate if orchestration becomes core
product functionality.

### Option G: Dagster

Pros:

- modern data orchestration model
- rich observability and asset-aware pipelines
- good for complex DAGs and reruns

Cons:

- substantial dependency and operational overhead
- unnecessary for current synthetic-only smoke/release checks
- could distract from no-oracle and privacy hardening

Good timing: only when real operational pipelines, scheduled jobs, persistent
run records, or multi-stage DAG observability are truly needed.

### Option H: Airflow

Pros:

- mature scheduler ecosystem
- strong fit for scheduled production data workflows
- established retry and dependency modeling

Cons:

- heavy operational footprint
- poor fit for the current local release-quality command bundle
- unnecessary before production or institutional data handling exists

Good timing: only after a separate production/data-governance review concludes
that scheduled pipeline orchestration is required.

## 6. Recommended Approach

Initial recommendation:

- do not introduce Airflow or Dagster now
- do not remove existing shell scripts immediately
- keep shell scripts as low-level smoke and compatibility entrypoints
- evaluate a Makefile or justfile as the next design step
- move top-level command discovery toward a task runner
- keep `scripts/check_release_quality.sh` as the current stable wrapper until a
  replacement proves equivalent
- consider Python or Rust orchestration later for structured stage metadata,
  failure classification, and richer expected-failure handling

This keeps the current safe behavior intact while creating a path toward better
developer ergonomics and future maintainability.

## 7. Short-Term Roadmap

Short-term work should remain docs-only or low-risk:

- create a script inventory
- group commands into categories:
  - release-quality
  - no-config summary and manifest checks
  - diagnostic distribution checks
  - config-enabled smoke checks
  - scoring lock and config validation checks
  - Python / Rust / TypeScript checks
- compare Makefile and justfile as top-level command surfaces
- model the summary order as a task target:
  `summary -> manifest-sync -> diagnostic-distribution`
- keep raw body output suppressed
- keep `tmp/` and generated outputs out of Git

The current script inventory and task category design is documented in
[shell script inventory and task category design](shell_script_inventory_task_category_design.md).
The Makefile vs justfile selection is documented in
[task runner selection design](task_runner_selection_design.md).
Step 148 added a thin `Makefile` entrypoint for common checks. The Makefile
calls existing scripts and commands; it does not replace script internals or
change workflow behavior.
The Makefile adoption and safety review is documented in
[Makefile entrypoint safety review](makefile_entrypoint_safety_review.md).

## 8. Medium-Term Roadmap

Medium-term work can reduce duplicated shell logic:

- identify repeated shell patterns suitable for Python or Rust helpers
- introduce safe structured stage summaries
- classify stages as deterministic, generated-output, validation, smoke, or
  remote-environment checks
- separate success-path wrappers from expected-failure regression checks
- decide which stages should never retry and which stages might safely retry
- stabilize one local/CI command entrypoint before broader CI migration

Structured summaries must remain safe status, path, count, and reason metadata.
They must not include raw JSONL, summary bodies, marker bodies, config bodies,
candidate score rows, or raw learner text.

## 9. Long-Term Roadmap

Airflow or Dagster should be reconsidered only if the project later needs:

- real operational data handling after a separate privacy review
- scheduled recurring runs
- multiple dependent DAGs
- persistent run history
- remote monitoring
- retry policies with durable state
- team or institutional operations

Any such move must preserve no-oracle, privacy, synthetic-only, and output
safety boundaries until real-data readiness has been reviewed separately.

## 10. Migration Safety Rules

Any orchestration migration must:

- preserve existing script behavior until replacement is verified
- preserve the summary generation, manifest sync, and diagnostic distribution
  order
- avoid printing raw logs, JSONL bodies, summary bodies, marker bodies, config
  bodies, diagnostic bodies, or candidate score rows
- avoid performance claims in public docs
- keep workflow and CI changes separate and incremental
- keep config-enabled summary behavior separate from no-config manifest checks
- keep scorer logic, scoring formula, tie-break behavior, and scorer weights
  unchanged unless explicitly scoped in a future task

## 11. Decision Criteria

Move toward Makefile or justfile when:

- contributors need a smaller set of memorable top-level commands
- the command inventory is stable
- existing scripts can remain as implementation details
- CI can install or already has the chosen tool

Move toward a Python or Rust orchestrator when:

- stage metadata needs to become structured
- shell error handling becomes hard to maintain
- expected-failure checks need clearer classification
- repeated shell parsing or validation logic becomes risky

Reconsider Airflow or Dagster when:

- scheduled production-like workflows are needed
- multiple durable DAGs exist
- retry history and observability become requirements
- real data handling has passed a separate readiness review

Stay with current scripts when:

- changes would add more complexity than they remove
- the command surface is still understandable
- safety checks and release-quality wrapper remain stable
- the project is still synthetic-only and local/CI oriented

## 12. Beginner Notes

Orchestration means deciding which commands run, in what order, and what should
happen when one of them fails.

Shell scripts are not bad. They are simple, visible, and useful for small
pipelines. They become risky when too many dependencies, generated files, and
language boundaries are hidden inside ad hoc scripts.

Makefile and justfile are lightweight task runners. They help people remember
and run common commands. Airflow and Dagster are heavier orchestration systems
for scheduled, observable, multi-stage workflows.

The safest path is gradual: keep the working scripts, add clearer top-level
entrypoints, then move complex orchestration into Python, Rust, or a data
orchestrator only when the project has a real need.

## Related Documents

- [Release-quality command bundle design](release_quality_command_bundle_design.md)
- [Shell script inventory and task category design](shell_script_inventory_task_category_design.md)
- [Task runner selection design](task_runner_selection_design.md)
- [Milestone 05 Makefile orchestration recap](milestone_05_makefile_orchestration_recap.md)
- [Milestone 05 final docs-only release review](milestone_05_final_docs_only_release_review.md)
- [Milestone 05 status marker design](milestone_05_status_marker_design.md)
- [Release-quality wrapper CI integration design](release_quality_wrapper_ci_integration_design.md)
- [Release-quality manual workflow design](release_quality_manual_workflow_design.md)
- [Milestone 04 CI maintenance recap](milestone_04_ci_maintenance_recap.md)
- [Public release checklist](public_release_checklist.md)
