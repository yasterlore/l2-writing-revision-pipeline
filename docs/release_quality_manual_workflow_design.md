# Release-Quality Manual Workflow Design

This document is design documentation and implementation notes for the manual
release-quality GitHub Actions workflow. Step 128 adds the first
`workflow_dispatch` workflow, but this document does not change shell scripts,
test code, summary generation, scoring logic, scorer weights, formulas, or
tie-break policy.

It is not a performance evaluation. It does not approve real-data processing,
private validation, learner-state estimation, or expected-action tuning.

## 1. Purpose

The purpose of this design is to define a manual GitHub Actions workflow for
running `scripts/check_release_quality.sh` in a future step.

This is an intermediate option before adding the full wrapper to frequent PR
CI. The manual workflow should preserve safe logs, no-oracle boundaries, and
output-safety rules while making full release-quality checks reproducible in a
CI environment.

## 2. Current State

Current state:

- `scripts/check_release_quality.sh` exists
- the existing CI workflow is Rust-centered
- the wrapper runs Python, Rust, Node, synthetic summary, manifest sync,
  diagnostic distribution, config smoke, scoring smoke, and repository hygiene
  checks
- Markdown link check is a manual note inside the wrapper because no dedicated
  project command exists yet
- expected-failure regression checks are outside the wrapper unless already
  encapsulated in existing safe scripts
- `.github/workflows/release-quality.yml` exists as a manual
  `workflow_dispatch` workflow

The current wrapper is available locally and through a manual GitHub Actions
workflow. It is not part of automatic PR CI.

## 3. Why Use A Manual Workflow

A manual workflow is useful because it:

- avoids making every PR run the full heavy wrapper
- lets maintainers run full release-quality checks before release review
- keeps ordering-sensitive checks in one sequential job
- verifies the wrapper in a GitHub Actions environment
- reduces reliance on purely local machine state
- can be introduced before deciding whether any subset belongs in PR CI

This gives the project a middle path between local-only checks and always-on
full CI.

## 4. Workflow Trigger Design

Initial recommendation from Step 127:

- use `workflow_dispatch`
- do not add `pull_request` initially
- do not add `push` initially
- keep `schedule` or nightly runs as a future option

Step 128 implements the initial workflow with `workflow_dispatch` only. It does
not add `pull_request`, `push`, or `schedule` triggers.

Optional branch input is not required at first because GitHub Actions manual
runs can already choose a branch from the UI. If a future workflow needs an
explicit target branch, that should be reviewed separately.

Manual run responsibility:

- the maintainer intentionally starts the workflow
- the run should be treated as a release-quality signal, not a required PR
  gate unless branch protection is changed later
- failed runs should block release-quality approval until investigated

## 5. Workflow Setup Requirements

A future workflow should include:

- repository checkout
- Python setup
- Rust toolchain setup with rustfmt and clippy
- Node setup
- logger-web dependency install
- repository root as the working directory
- executable permission check for `scripts/check_release_quality.sh`
- optional cache setup only after the uncached workflow is understood

Step 128 uses:

- `actions/checkout@v4`
- `actions/setup-python@v5` with Python 3.11
- `dtolnay/rust-toolchain@stable` with rustfmt and clippy
- `actions/setup-node@v4` with Node 22 and npm cache for logger-web
- `npm ci` under `apps/logger-web`
- `scripts/check_release_quality.sh` from repository root

The workflow should not require private data, real participant data, secrets, or
network calls beyond normal dependency setup.

## 6. Command To Run

Implemented command:

```bash
scripts/check_release_quality.sh
```

Before that command, the workflow installs dependencies. It also includes:

```bash
chmod +x scripts/check_release_quality.sh
```

Markdown link check remains the wrapper's manual note until a dedicated project
command exists. Expected-failure tests are not added to the workflow.

## 7. Safe Logs Policy

Workflow logs must not contain:

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

Safe log output may contain:

- stage names
- command names
- safe repository-relative paths
- count-only metadata
- status labels
- reason codes

Do not upload `tmp/` outputs as artifacts initially. Generated outputs should
remain transient and ignored.

## 8. Failure Policy

Failure policy:

- wrapper failure fails the workflow
- missing summary is failure
- manifest sync failure is failure
- diagnostic distribution failure is failure
- conflict marker failure is failure
- no silent pass
- expected-failure regression tests are not part of the manual success workflow

The workflow should not reinterpret wrapper failures as warnings. If the wrapper
fails, the manual release-quality run should be considered failed.

## 9. Comparison With PR CI

Manual workflow:

- full release-quality wrapper
- manually triggered
- slower but more complete
- useful before release review or major merge checkpoints

PR CI:

- lighter and faster
- frequent
- should avoid unnecessary duplicate heavy checks
- may later run selected lightweight checks or a reduced subset

Future path:

- keep the full wrapper in a manual workflow first
- keep existing PR CI focused and fast
- later decide whether selected wrapper phases should move into PR CI
- avoid duplicating expensive Rust, Python, and Node checks without a reason

## 10. Future Implementation Checklist

Before implementation:

- create `.github/workflows/release-quality.yml`
- set `workflow_dispatch`
- confirm checkout step
- install Python
- install Rust with rustfmt and clippy
- install Node
- install logger-web dependencies
- run `scripts/check_release_quality.sh`
- verify logs remain safe
- confirm no `tmp/` artifacts are uploaded
- confirm whether branch protection should ignore or require this manual
  workflow
- update the public release checklist after implementation

Step 128 implementation status:

- `.github/workflows/release-quality.yml` added
- trigger is `workflow_dispatch` only
- dependency setup is included
- wrapper runs from repository root
- no artifact upload is configured
- public release checklist is updated

For the first remote GitHub Actions run after implementation, use the
[release-quality manual workflow remote-run checklist](release_quality_manual_workflow_remote_run_checklist.md).
After the run, record only a safe high-level summary using the
[release-quality manual workflow remote-run report template](templates/release_quality_manual_workflow_remote_run_report_template.md).

## 11. Beginner Notes

A manual workflow is a GitHub Actions workflow that a maintainer starts by
clicking a button in GitHub.

It is different from PR CI because it does not run automatically on every pull
request. That makes it a good first home for heavier release-quality checks.

Dependency setup is needed because the wrapper runs Python, Rust, and Node
commands. GitHub's runner needs those tools and packages before it can run the
wrapper.

Log safety matters because CI logs are often visible to collaborators and can be
shared in review. They should show only safe status and count-only information,
not generated data bodies.

## 12. Related Documents

- [Release-quality wrapper CI integration design](release_quality_wrapper_ci_integration_design.md)
- [Release-quality command bundle design](release_quality_command_bundle_design.md)
- [Release-quality manual workflow remote-run checklist](release_quality_manual_workflow_remote_run_checklist.md)
- [Release-quality manual workflow remote-run report template](templates/release_quality_manual_workflow_remote_run_report_template.md)
- [Summary manifest sync check release integration design](summary_manifest_sync_check_release_integration_design.md)
- [Public release checklist](public_release_checklist.md)
- [Milestone 03 final docs-only release review](milestone_03_final_docs_only_release_review.md)
