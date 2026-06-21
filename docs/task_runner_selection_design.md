# Task Runner Selection Design

This document compares Makefile and justfile as lightweight task-runner options
for this repository.

This began as design documentation. Step 148 implemented a thin Makefile
entrypoint that calls existing scripts and commands without moving script logic
into Make. It does not create a justfile, Airflow, Dagster, workflow change,
script change, test change, scorer change, manifest schema change, or
performance evaluation.

## 1. Purpose

The purpose of this design is to choose an initial direction for a top-level
task runner before implementing one.

The task runner should make common checks easier to discover while preserving
the existing shell scripts as stable compatibility entrypoints. The goal is not
to replace orchestration with Airflow or Dagster. The current repository is
synthetic-only research software with local and CI-oriented smoke, safety, and
release-quality checks.

## 2. Current Assumptions

Current assumptions:

- the existing shell script inventory is documented in
  [shell script inventory and task category design](shell_script_inventory_task_category_design.md)
- `scripts/check_release_quality.sh` is the current normal success-path wrapper
- the no-config summary flow has required ordering:
  `summary -> manifest sync -> diagnostic distribution`
- raw body output safety must be preserved
- local and CI users should have a simple entrypoint
- the repository includes Rust, Python, and TypeScript checks
- existing shell scripts should remain available as fallback commands

The task runner should initially call existing scripts rather than duplicate
their internal logic.

## 3. Comparison Axes

The comparison uses these axes:

- standardness and whether an extra install is required
- macOS, Linux, and GitHub Actions compatibility
- learning cost
- command readability
- argument, variable, and default target ergonomics
- compatibility with shell scripts
- compatibility with CI
- Windows portability
- public repository contributor experience
- effect on no-oracle and output-safety boundaries
- ease of later migration to a Python or Rust orchestrator

## 4. Makefile Option

Pros:

- widely known and commonly available on macOS and Linux
- usually available on GitHub Actions runners without extra setup
- no new project-specific tool dependency for many contributors
- fits simple top-level targets such as `check-release-quality` and
  `check-summary-flow`
- can call existing shell scripts directly
- easy to keep CI integration minimal later

Cons:

- Make syntax has quirks
- recipe lines require tabs
- `.PHONY` targets must be used carefully
- shell behavior can surprise contributors if commands span multiple lines
- argument passing is less ergonomic than justfile
- not ideal for complex structured orchestration

Fit for this repository:

Makefile is a strong initial fit because the next step is top-level command
discovery, not a full orchestration rewrite. It can preserve all existing shell
scripts and avoid adding another dependency to a public research repository.

Implementation cautions for a future step:

- use `.PHONY` for non-file targets
- keep targets thin
- call existing scripts rather than reimplementing their logic
- avoid adding generated-output printing
- keep the summary flow target sequential

## 5. Justfile Option

Pros:

- readable command syntax
- friendlier variables and arguments than Make
- good default target ergonomics
- designed specifically for command recipes
- works well as a developer-facing command surface
- can call existing shell scripts directly

Cons:

- requires installing `just`
- not guaranteed on all contributor machines or CI runners
- GitHub Actions setup would need an extra install step
- public repo contributors may be less familiar with it than Make
- a new dependency may distract from the minimal task-runner goal

Fit for this repository:

justfile is attractive for readability and developer ergonomics, especially on
macOS. It is less attractive as the first public repository task runner because
it adds a dependency before the command surface has proven that Make is
insufficient.

Implementation cautions for a future step:

- document installation clearly if selected
- avoid making CI depend on `just` until the workflow update is explicitly
  scoped
- keep existing scripts as fallback commands
- keep no-oracle and output-safety boundaries unchanged

## 6. Why Not Airflow Or Dagster Yet

Airflow and Dagster are not recommended for this stage because:

- this is not a production data pipeline
- development remains synthetic-only
- CI-oriented smoke and release-quality checks do not need a scheduler
- setup and operational costs would be disproportionate
- task discovery and ordering can be improved with a lightweight runner first
- DAG orchestration should be revisited only when long-term operational
  conditions are met

Those long-term conditions include scheduled runs, durable retry history,
multiple dependent DAGs, monitoring, and separately reviewed real-data handling.

## 7. Recommended Approach

Initial recommendation: choose Makefile as the first task-runner candidate.

Reasons:

- no additional dependency for typical macOS, Linux, and GitHub Actions usage
- familiar to many public repository contributors
- sufficient for thin targets that call existing scripts
- easy to keep scripts as fallbacks
- lower CI integration burden than justfile
- good fit for the current goal: top-level entrypoint discovery

Recommended initial shape:

- keep all existing shell scripts
- add only thin top-level targets in a future implementation step
- make `check-release-quality` call `scripts/check_release_quality.sh`
- make `check-summary-flow` preserve the required sequential summary flow
- do not add complex orchestration, retries, or structured result aggregation
- do not change scorer logic, manifest schema, fixtures, workflow triggers, or
  output-safety policy

justfile remains a good alternative if the project later prioritizes recipe
readability over dependency minimization.

Step 148 implementation status:

- `Makefile` now exists as a thin top-level command surface.
- `make help` lists the implemented targets.
- `make check-release-quality` calls `scripts/check_release_quality.sh`.
- `make check-summary-flow` preserves the required summary, manifest sync, and
  diagnostic distribution order.
- `make check-all` delegates to `check-release-quality` to avoid duplicating the
  release-quality command bundle.
- Existing shell scripts remain available and unchanged.

The post-adoption safety review is documented in
[Makefile entrypoint safety review](makefile_entrypoint_safety_review.md).
Parallel execution and shared `tmp/` output safety are documented in
[Makefile parallel/tmp safety design](makefile_parallel_tmp_safety_design.md).
Step 151 added `.NOTPARALLEL` and a short help warning without changing target
names or script behavior.

## 8. Initial Target Candidates

Initial target candidates implemented in the Step 148 Makefile:

- `check-release-quality`
- `check-summary-flow`
- `check-summary`
- `check-manifest-sync`
- `check-diagnostic-distribution`
- `check-config-smoke`
- `check-python`
- `check-rust`
- `check-logger`
- `check-policy`
- `check-fixtures`
- `check-all`

Suggested dependency shape:

- `check-summary-flow` should run:
  `check-summary -> check-manifest-sync -> check-diagnostic-distribution`
- `check-release-quality` should call the existing wrapper directly
- `check-all` should initially avoid duplicating too much wrapper behavior
  unless the target order is explicitly documented

The implemented targets remain thin wrappers. They do not print generated body
contents and do not replace the existing scripts.

## 9. Migration Safety Rules

Future task-runner implementation must:

- start by calling existing scripts
- preserve script behavior
- preserve the summary, manifest sync, diagnostic distribution order
- avoid printing raw logs, JSONL bodies, summary bodies, marker bodies, config
  bodies, diagnostic bodies, or candidate score rows
- keep CI workflow changes out of the first task-runner implementation unless
  separately scoped
- keep `scripts/*.sh` as fallback commands
- avoid performance claims in public docs or command output
- avoid changing scorer logic, scoring formula, tie-break behavior, manifest
  schema, fixtures, or weights

## 10. Decision Criteria

Choose Makefile when:

- minimizing dependencies is more important than recipe syntax elegance
- GitHub Actions compatibility should remain simple
- public repository contributor familiarity matters
- targets are thin wrappers around existing scripts

Choose justfile when:

- contributor ergonomics and readable recipes outweigh the extra dependency
- the team is willing to document and install `just`
- CI setup can explicitly include `just`
- target arguments become awkward in Make

Delay task-runner introduction when:

- command categories are still unstable
- script behavior is still changing rapidly
- a new top-level entrypoint would confuse rather than clarify usage

Move toward Python or Rust orchestration when:

- structured stage metadata becomes necessary
- shell failure classification becomes hard to maintain
- retry policy needs explicit modeling
- expected-failure phases need richer status reporting

## 11. Beginner Notes

A task runner is a small command menu for a repository. Instead of remembering a
long command, a contributor can run a named target.

Makefile is older and widely available. justfile is newer and often easier to
read, but it usually needs an extra install.

The shell scripts should not disappear right away. They already define working
behavior. A task runner can simply call them so the project gets easier
entrypoints without changing the pipeline.

Airflow and Dagster solve larger scheduling and data orchestration problems.
They are useful later if the project needs production-like scheduled workflows,
but they are too heavy for the current synthetic-only release-quality checks.

The first task-runner step should improve discoverability, not introduce a new
pipeline architecture.

## Related Documents

- [Orchestration modernization design](orchestration_modernization_design.md)
- [Shell script inventory and task category design](shell_script_inventory_task_category_design.md)
- [Release-quality command bundle design](release_quality_command_bundle_design.md)
- [Makefile entrypoint safety review](makefile_entrypoint_safety_review.md)
- [Makefile parallel/tmp safety design](makefile_parallel_tmp_safety_design.md)
- [Milestone 05 Makefile orchestration recap](milestone_05_makefile_orchestration_recap.md)
- [Milestone 05 final docs-only release review](milestone_05_final_docs_only_release_review.md)
- [Milestone 05 status marker design](milestone_05_status_marker_design.md)
- [Public release checklist](public_release_checklist.md)
