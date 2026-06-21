# Release-Quality Wrapper CI Integration Design

This document is design documentation only. It does not change CI workflows,
shell scripts, test code, summary generation, scoring logic, scorer weights,
formulas, or tie-break policy.

It is not a performance evaluation. It does not approve real-data processing,
private validation, learner-state estimation, or expected-action tuning.

## 1. Purpose

The purpose of this design is to define how `scripts/check_release_quality.sh`
could be integrated into CI in a future step.

The design should:

- identify overlap with existing CI checks
- preserve the required summary generation ordering
- keep CI logs safe and body-suppressed
- clarify failure handling before changing workflow files

This is a release-quality reliability design, not a performance report.

## 2. Current State

Current state:

- `scripts/check_release_quality.sh` exists
- the wrapper runs normal success-path release-quality checks sequentially
- the wrapper enforces:
  `scripts/run_synthetic_e2e_summary.sh` →
  `scripts/check_summary_manifest_schema_sync.sh` →
  `scripts/check_synthetic_diagnostic_distribution.sh`
- Markdown link check is a manual note inside the wrapper because no dedicated
  project command exists yet
- expected-failure regression checks remain inside existing dedicated scripts
  or outside the wrapper
- CI workflow is not connected to the wrapper

The current `.github/workflows/ci.yml` is Rust-centered. It runs Rust format,
tests, clippy, synthetic policy checks, CLI fixture smoke tests, and one
synthetic E2E pipeline smoke test.

## 3. Why CI Integration Is Useful

CI integration is useful because manual checks can be missed.

The wrapper would help CI catch:

- summary generation ordering mistakes
- manifest schema sync drift
- diagnostic distribution precondition failures
- conflict markers
- no-config scoring fixture lock regressions
- config smoke failures
- Python, Rust, and logger-web regressions when included

The most important ordering requirement is that CI must not run summary
generation in parallel with manifest sync or diagnostic distribution checks.

## 4. CI Integration Options

### Option A: Add The Wrapper Directly To Existing CI

Add `scripts/check_release_quality.sh` as a step in the existing workflow.

This is simple, but it may duplicate Rust checks and synthetic policy checks
already present in the workflow.

### Option B: Distribute Individual Commands Across Existing Jobs

Keep the wrapper local/manual and add individual commands to relevant CI jobs.

This avoids some duplication, but it loses the wrapper's single sequential
ordering guarantee unless the summary-dependent commands stay in one job.

### Option C: Add A Dedicated Release-Quality Job

Add a separate job that installs all dependencies and runs
`scripts/check_release_quality.sh`.

This makes ownership clear and keeps summary-dependent checks together. It may
be heavier than the existing CI because the wrapper runs Python, Rust, Node, and
synthetic smoke checks.

### Option D: Add A Nightly Or Manual Workflow

Run the full wrapper on a scheduled or manually triggered workflow.

This reduces PR latency but catches failures later. It fits well if full release
checks are too heavy for every pull request.

### Option E: Lightweight PR CI, Full Manual Wrapper

Keep PR CI focused on existing lighter checks and require the full wrapper for
manual release-quality review.

This keeps CI fast, but manual discipline remains important.

## 5. Recommended Approach

Initial recommendation:

- do not modify CI yet
- add a future dedicated release-quality job or manual workflow first
- keep existing CI jobs until duplication is reviewed
- let the wrapper own summary generation, manifest sync, and diagnostic
  distribution ordering
- avoid splitting summary-dependent commands across parallel jobs
- consider a lighter PR subset only if the full wrapper is too slow

For the next implementation step, the smallest safe CI integration would be a
dedicated optional or manual job that runs the wrapper after Python, Rust, and
Node dependencies are available.

For the manual `workflow_dispatch` version of that option, see
[release-quality manual workflow design](release_quality_manual_workflow_design.md).
Step 128 implements that manual workflow without connecting the full wrapper to
automatic PR CI.

## 6. Order CI Must Preserve

A future CI job must preserve this order:

1. checkout
2. install or activate required Python, Rust, and Node dependencies
3. run shell syntax checks
4. run `scripts/run_synthetic_e2e_summary.sh`
5. run `scripts/check_summary_manifest_schema_sync.sh`
6. run `scripts/check_synthetic_diagnostic_distribution.sh`
7. run remaining checks

The summary-dependent commands must stay sequential and in the same workspace.
Do not run them in separate parallel jobs unless the generated summary and
manifest are explicitly passed between jobs and ordering is guaranteed.

## 7. Existing CI Overlap

The wrapper overlaps with existing or likely CI checks:

- Python unittest and compileall
- Rust fmt, tests, and clippy
- logger-web typecheck, test, and build
- synthetic policy check
- synthetic smoke scripts
- no-config scoring fixture lock
- hand-weight config validation
- explicit config ranking diff

The current workflow already runs Rust fmt, Rust tests, Rust clippy, synthetic
policy, CLI fixture smoke tests, and a synthetic E2E pipeline smoke test.

If the wrapper is added directly, Rust and synthetic policy checks will run
twice unless the existing job is reorganized. That may be acceptable for a
manual or release-only workflow, but it may be too slow for every PR.

## 8. Output Safety Policy

CI logs must not include:

- raw JSONL body
- summary CSV body
- marker JSON body
- diagnostic summary body
- config body
- candidate score rows
- raw learner text
- expected action details
- performance metrics
- real participant data

CI may print safe stage names, safe paths, status labels, counts, and reason
codes.

## 9. Failure Policy

CI should fail closed when the wrapper fails.

Failure should block PR or release-quality approval when:

- summary generation fails
- manifest sync fails
- diagnostic distribution check fails
- conflict marker grep finds markers
- no-config scoring fixture lock changes
- synthetic policy fails
- Python, Rust, or logger-web checks fail

Expected-failure tests should not be mixed into the success wrapper unless they
are already encapsulated in a dedicated safe script. Missing summary remains a
failure, not a silent pass.

## 10. Future CI Implementation Checklist

Before implementing CI integration:

- identify current CI workflow files
- decide whether the wrapper runs in PR CI, manual workflow, nightly workflow,
  or release-only workflow
- avoid duplicate heavy jobs where possible
- ensure the working directory is repository root
- ensure Python is available
- ensure Rust toolchain includes rustfmt and clippy
- ensure Node dependencies are installed for `apps/logger-web`
- ensure `scripts/check_release_quality.sh` is executable
- run the wrapper after dependency setup
- verify logs remain safe and body-suppressed
- keep `tmp/` outputs untracked

## 11. Beginner Notes

CI integration means making the repository run checks automatically on a remote
service when code is pushed or a pull request is opened.

A local wrapper is useful, but it only helps when someone remembers to run it.
CI can catch problems earlier and more consistently.

Duplicate checks matter because they can make CI slow. If Rust tests already
run in one job and the wrapper runs them again in another job, that may be fine
for release checks but annoying for every pull request.

The summary checks should not run in parallel because later checks read files
created by the summary generator. They need a clear order.

Expected-failure tests are separate because the wrapper represents the normal
success path. Mixing intentional failures into the same flow can make logs and
failure handling harder to understand.

## 12. Related Documents

- [Release-quality command bundle design](release_quality_command_bundle_design.md)
- [Release-quality manual workflow design](release_quality_manual_workflow_design.md)
- [Summary manifest sync check release integration design](summary_manifest_sync_check_release_integration_design.md)
- [Synthetic diagnostic distribution check ordering design](synthetic_diagnostic_distribution_check_ordering_design.md)
- [Public release checklist](public_release_checklist.md)
- [Milestone 03 final docs-only release review](milestone_03_final_docs_only_release_review.md)
