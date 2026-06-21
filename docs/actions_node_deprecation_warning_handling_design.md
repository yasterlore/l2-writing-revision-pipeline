# GitHub Actions Node Deprecation Warning Handling Design

This document designs how to handle the GitHub Actions Node.js runtime
deprecation warning observed after the first remote run of the manual
release-quality workflow.

It is design documentation only. It does not change GitHub Actions workflows,
the release-quality wrapper, shell scripts, tests, scorer behavior, manifest
schema, or CI triggers. It is not a performance evaluation.

## 1. Purpose

The purpose of this design is to track and handle the GitHub Actions Node.js
deprecation warning without ignoring it and without rushing unrelated workflow
changes.

The design separates:

- release-quality workflow result: Success
- annotation status: Node.js runtime deprecation warning
- release wrapper status: not implicated by the warning
- scorer, manifest schema, and synthetic pipeline status: unchanged

The goal is to plan a minimal action-version update path while preserving safe
logs, no-oracle boundaries, and the current manual workflow behavior.

## 2. Current State

Current state after Step 131:

- `.github/workflows/release-quality.yml` exists
- trigger is `workflow_dispatch` only
- the first GitHub UI remote run completed with Success
- artifact upload is not configured
- the warning is a GitHub Actions Node.js runtime deprecation warning
- the warning named these actions:
  - `actions/checkout@v4`
  - `actions/setup-node@v4`
  - `actions/setup-python@v5`
- `scripts/check_release_quality.sh` completed successfully during the remote
  run
- wrapper logic, scoring logic, manifest schema, and synthetic summary logic do
  not need changes for this warning

## 3. Meaning Of The Warning

The warning is not a workflow failure. It indicates that GitHub Actions is
transitioning actions that target an older internal Node.js runtime to a newer
runtime.

This is different from the Node version configured by `actions/setup-node` for
project commands. The workflow may set up Node for logger-web commands while the
GitHub-hosted action itself also has an internal Node runtime.

The warning should still be tracked because action runtime compatibility can
become a future maintenance risk. Treat it as workflow maintenance, not as a
release-quality wrapper failure.

## 4. Handling Options

Option A: update action versions immediately.

- Pros: may remove or reduce the warning quickly
- Cons: changes workflow behavior without a separate review step

Option B: track the warning in docs first, then perform a minimal workflow
update in the next step.

- Pros: keeps the current step docs-only and preserves review separation
- Cons: warning remains until the workflow update step

Option C: defer until the warning becomes a failure.

- Pros: no immediate work
- Cons: increases the risk of surprise workflow breakage later

Option D: update only the manual release-quality workflow first.

- Pros: narrow blast radius and easy remote-run verification
- Cons: existing CI may still have related warnings if it uses older actions

Option E: update existing CI and release-quality workflow at the same time.

- Pros: consolidates action maintenance
- Cons: larger change set and higher review risk

## 5. Recommended Approach

Use Option B first: docs-only tracking in this step.

For the next implementation step, consider a minimal update of
`.github/workflows/release-quality.yml` only, after inspecting the currently
recommended major versions of the affected actions.

Keep these boundaries:

- do not change the release-quality wrapper
- do not change scorer logic
- do not change manifest schema
- do not change synthetic summary or diagnostic logic
- inspect existing `ci.yml` separately before deciding whether to update it
- after any workflow update, rerun the manual workflow remotely

## 6. Update Planning

Before changing workflow files, perform this planning checklist:

- inspect `.github/workflows/release-quality.yml`
- inspect `.github/workflows/ci.yml`
- list all action versions used by each workflow
- confirm whether newer major versions exist for affected actions
- review action release notes or migration notes before bumping versions
- do not confuse project Node setup version with action internal Node runtime
- decide whether to update only release-quality workflow first
- after the update, run YAML parse locally
- after the update, run trigger grep checks locally
- after the update, run `scripts/check_release_quality.sh` locally
- after the update is pushed, rerun the manual workflow remotely
- confirm artifact upload is still absent
- record the result with the remote-run report template

## 7. Risk Assessment

Potential risks from action-version updates:

- checkout behavior may differ
- Python setup behavior may differ
- Node setup or npm cache behavior may differ
- `npm ci` behavior may surface environment differences
- Rust toolchain setup should be checked for indirect ordering effects
- warning deferral can become future workflow breakage
- CI logs must remain safe after any workflow update

The warning itself does not indicate a scoring, manifest, data, or no-oracle
problem.

## 8. Safe Output / Privacy Policy

It is acceptable to summarize the warning at a high level and name the affected
actions.

Do not paste:

- raw workflow logs
- raw JSONL body
- summary body
- marker body
- diagnostic body
- config body
- candidate score rows
- raw learner text
- real participant data

This warning does not alter no-oracle boundaries and must not be treated as
expected-action feedback or performance evidence.

## 9. Future Implementation Checklist

For a later implementation step:

- inspect `.github/workflows/release-quality.yml`
- inspect `.github/workflows/ci.yml`
- decide whether to update only the manual release-quality workflow first
- update action versions if safe
- parse workflow YAML
- run trigger grep checks
- verify no artifact upload is introduced
- run `scripts/check_release_quality.sh`
- push the branch
- run the manual workflow from GitHub Actions
- record safe result with the remote-run report template
- confirm the Node.js deprecation warning is removed or reduced

## 10. Beginner Notes

A GitHub Actions Node runtime warning is about the JavaScript runtime used by an
action such as checkout or setup. It is not the same thing as the Node version
installed for the project.

The workflow can still succeed while showing a warning. Success means the run
completed; the warning means there is maintenance work to track.

Changing every workflow at once can make review harder. A narrow manual workflow
update first is easier to verify and roll back.

Remote rerun matters because the warning appears in GitHub Actions, not only in
local shell checks.

## 11. Related Documents

- [Release-quality manual workflow design](release_quality_manual_workflow_design.md)
- [Release-quality manual workflow remote-run checklist](release_quality_manual_workflow_remote_run_checklist.md)
- [Release-quality manual workflow remote-run report template](templates/release_quality_manual_workflow_remote_run_report_template.md)
- [Public release checklist](public_release_checklist.md)
