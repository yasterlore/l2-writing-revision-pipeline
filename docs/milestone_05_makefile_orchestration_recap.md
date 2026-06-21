# Milestone 05 Makefile Orchestration Recap

This document recaps the Step 145-151 response to an external review concern
that the repository's Rust, Python, TypeScript, and synthetic E2E checks relied
too heavily on hand-written shell script orchestration.

It is recap documentation only. It does not change the Makefile, shell scripts,
GitHub Actions workflows, tests, scorer logic, scoring formula, tie-break
behavior, manifest schema, fixtures, or weights. It is not a performance
evaluation.

## 1. Purpose

The purpose of this recap is to summarize how the project responded to the
shell-orchestration critique without overreacting or replacing working scripts
too early.

The milestone clarifies the current Makefile adoption state, why the existing
shell scripts remain in place, and how the Makefile now acts as a thin
top-level command menu rather than a new pipeline implementation.

This milestone is reliability and developer-experience infrastructure only. It
does not make any claim about model quality, scorer accuracy, research
validity, production readiness, or data-collection readiness.

## 2. Milestone Scope

The scope covers Step 145 through Step 151:

- orchestration modernization design
- shell script inventory and task categories
- Makefile versus justfile task-runner selection
- thin Makefile entrypoint implementation
- Makefile adoption and safety review
- parallel execution and shared `tmp/` output safety design
- sequential safety guidance through `.NOTPARALLEL` and `make help`

The scope does not include scorer, model, data, manifest schema, fixture,
workflow, or CI trigger changes.

## 3. Step-By-Step Recap

Step 145 translated the external critique into a staged modernization roadmap.
It acknowledged that shell orchestration can hide dependencies, retries,
structured logging, and cross-language boundaries, while also noting that
Airflow or Dagster would be premature for the current synthetic-only checks.

Step 146 inventoried the existing `scripts/*.sh` entrypoints and grouped them
by task category, dependency order, output-safety expectations, and future
task-runner target candidates.

Step 147 compared Makefile and justfile. The initial recommendation was
Makefile because it keeps dependencies low, works naturally in common local and
CI environments, and can call existing scripts without replacing them.

Step 148 added a thin Makefile. The Makefile introduced discoverable targets
such as `check-release-quality`, `check-summary-flow`, `check-python`,
`check-rust`, `check-logger`, and `check-fixtures` while keeping the underlying
script behavior unchanged.

Step 149 reviewed the Makefile adoption for safety. It documented that the
Makefile is a command menu, does not duplicate script bodies, and should not be
treated as a full orchestrator.

Step 150 documented the shared `tmp/` output risk around summary generation,
manifest sync, and diagnostic distribution checks. It identified parallel
execution and stale or partial generated outputs as orchestration risks rather
than scorer or model failures.

Step 151 added minimal Makefile-level sequential guidance. `.NOTPARALLEL` was
added, and `make help` now warns against using `make -j` with summary-flow
targets.

## 4. Current Makefile State

Current Makefile state:

- default target: `help`
- role: thin command menu for existing scripts and commands
- `check-release-quality`: calls `scripts/check_release_quality.sh`
- `check-summary-flow`: preserves the required order:
  `summary -> manifest sync -> diagnostic distribution`
- `check-all`: delegates to `check-release-quality`
- `.NOTPARALLEL`: present as a Make-level guard
- raw body behavior: the Makefile does not cat generated bodies
- compatibility layer: existing shell scripts remain the source of operational
  behavior

The Makefile improves command discoverability without moving shell script
bodies into Make recipes.

## 5. External Critique Response

Valid concerns acknowledged:

- shell scripts can make dependency visibility harder
- retry and failure classification are still lightweight
- structured logging and stage metadata are limited
- Rust, Python, and TypeScript boundaries are coordinated through shell glue
- production-like execution would need stronger orchestration guarantees

Overreaction avoided:

- no immediate Airflow or Dagster adoption
- no deletion of existing scripts
- no rewrite of working synthetic-only checks
- no production pipeline claim
- no claim that Makefile success proves research performance

Implemented improvement:

- Makefile top-level entrypoints
- explicit summary-flow ordering
- `.NOTPARALLEL` and help guidance
- shell script inventory and modernization roadmap docs
- public release checklist guidance for Makefile usage

## 6. Safety / No-Oracle Boundaries

This milestone preserves these boundaries:

- no real participant data
- no raw JSONL body in docs or command summaries
- no summary, marker, diagnostic, config, or candidate score body in docs
- no candidate score rows pasted into docs
- no expected action details used as scoring feedback
- no F1, accuracy, calibration, learner-state estimation, or performance
  metrics added
- no production, research, or data-collection readiness claim

Makefile and orchestration docs are infrastructure documentation, not evidence
of research correctness.

## 7. What Changed

Changed in this milestone:

- a thin Makefile was added
- Makefile targets were introduced for common checks
- `.NOTPARALLEL` and help guidance were added
- orchestration modernization, inventory, selection, adoption, and safety docs
  were added
- the public release checklist gained Makefile and summary-flow guidance

## 8. What Did Not Change

Not changed:

- existing shell script behavior
- GitHub Actions workflows
- CI triggers or job structure
- release-quality wrapper script behavior
- scorer logic
- scoring formula
- tie-break behavior
- manifest schema
- summary hash behavior
- fixtures and weights
- real-data handling
- candidate generation behavior
- E2E summary generator logic

## 9. Remaining Risks

Remaining risks:

- direct script execution outside Make can still race on shared `tmp/` output
- Makefile does not provide structured stage metadata
- failure classification still mostly lives in scripts
- Markdown link check remains a manual note inside the release-quality wrapper
- lock files and per-run temp directory isolation are not implemented
- a Python or Rust orchestrator remains a future option if complexity grows

These risks are not blockers for using the Makefile as a thin local entrypoint,
but they should guide future orchestration work.

## 10. Future Options

Future options:

- review and stabilize Makefile target naming conventions
- formalize a Markdown link checker command
- add structured stage summaries if shell output becomes hard to interpret
- move complex orchestration to a Python or Rust helper when needed
- add a lock file or per-run temp isolation if shared `tmp/` races recur
- keep Airflow or Dagster out of scope unless production-like scheduling,
  durable DAGs, and monitoring become real requirements

## 11. Beginner Notes

A recap is a short checkpoint document. It explains what changed, what did not
change, and what remains to watch.

Orchestration means deciding which commands run, in what order, and how failure
should be handled.

The Makefile is not a new pipeline body. It is a command menu that calls the
existing scripts.

The shell scripts remain because they already define working behavior and are a
useful compatibility layer. Removing them immediately would add migration risk
without solving the current problem.

The project started with Makefile rather than Airflow or Dagster because the
current work is local/CI-oriented and synthetic-only. Heavy schedulers are more
appropriate for production-like scheduled workflows with durable run history
and monitoring.

Passing CI or Makefile checks means the configured checks passed. It is not a
research performance result.

## Related Documents

- [Milestone 05 status marker](status/milestone_05_status.md)
- [Research pipeline next-phase plan](research_pipeline_next_phase_plan.md)
- [Milestone 05 final docs-only release review](milestone_05_final_docs_only_release_review.md)
- [Milestone 05 status marker design](milestone_05_status_marker_design.md)
- [Orchestration modernization design](orchestration_modernization_design.md)
- [Shell script inventory and task category design](shell_script_inventory_task_category_design.md)
- [Task runner selection design](task_runner_selection_design.md)
- [Makefile entrypoint safety review](makefile_entrypoint_safety_review.md)
- [Makefile parallel/tmp safety design](makefile_parallel_tmp_safety_design.md)
- [Public release checklist](public_release_checklist.md)
