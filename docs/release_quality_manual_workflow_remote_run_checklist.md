# Release-Quality Manual Workflow Remote-Run Checklist

This checklist is for the first remote run of the manual release-quality GitHub
Actions workflow after the workflow file has been added.

It is an operations checklist only. It does not change the workflow, release
wrapper, shell scripts, tests, scorer behavior, manifest schema, or CI triggers.
It is not a performance evaluation and must not use expected actions as scoring
feedback.

## 1. Purpose

Use this checklist to confirm that the manual workflow can run safely on GitHub
Actions and that its logs remain public-safe.

The checklist verifies:

- the workflow is visible and manually runnable
- setup steps work in the remote runner
- the release-quality wrapper starts from the repository root
- summary generation, manifest sync, and diagnostic distribution checks run in
  the expected order
- logs do not expose raw bodies or private data
- failures can be recorded with safe high-level summaries only

## 2. Current State

Current repository state:

- `.github/workflows/release-quality.yml` exists
- the trigger is `workflow_dispatch` only
- the workflow runs `scripts/check_release_quality.sh`
- artifact upload is not configured
- existing CI workflows are not changed by the manual workflow

The workflow is intended for an on-demand release-quality run. It is not a
replacement for local review, and it is not currently an automatic pull request
gate.

## 3. First Run Before Starting Checklist

Before starting the first remote run, confirm:

- [ ] The workflow appears in the GitHub Actions tab.
- [ ] The workflow can be started manually.
- [ ] The target branch can be selected.
- [ ] The run will use `main` or the intended review branch.
- [ ] No secrets are required.
- [ ] `contents: read` permissions are sufficient.
- [ ] No trigger other than `workflow_dispatch` is configured.
- [ ] No artifact upload step is configured.

If any item is unclear, stop before the remote run and revise the workflow
design or implementation in a separate step.

## 4. What To Watch During The First Run

During the first GitHub Actions run, check the high-level stages:

- checkout succeeds
- Python setup succeeds
- Rust toolchain setup succeeds
- Node setup succeeds
- `npm ci` succeeds for `apps/logger-web`
- the wrapper starts from the repository root
- `scripts/run_synthetic_e2e_summary.sh` runs before manifest sync
- `scripts/check_summary_manifest_schema_sync.sh` runs after summary generation
- `scripts/check_synthetic_diagnostic_distribution.sh` runs after manifest sync
- Python checks complete
- Rust checks complete
- logger-web checks complete
- the workflow result is clearly pass or fail

Do not copy raw command logs into public docs. Record only safe high-level stage
status.

## 5. Safe Logs Checklist

The first remote run logs are acceptable only if they do not contain:

- raw JSONL body
- summary body
- marker body
- diagnostic body
- config body
- candidate score rows
- raw learner text or generated raw text
- real participant data
- artifact uploads containing `tmp/` outputs

Logs should be limited to safe status, paths, counts, stage names, and failure
reasons. If unsafe output appears, stop relying on the workflow and revise output
safety before using it for release review.

## 6. Failure Triage

If the workflow fails, classify the failure by safe stage name:

- dependency setup failure
- `npm ci` failure
- Rust toolchain failure
- wrapper failure
- manifest sync failure
- diagnostic distribution failure
- conflict marker failure
- synthetic policy failure
- logger-web failure

For each failure, record only the safe stage and safe reason. Do not paste raw
JSONL, summary, marker, diagnostic, config, candidate score, or text bodies into
docs, issues, pull requests, or approval notes.

Prefer a local reproduction command when possible, such as the corresponding
script or package command, rather than copying remote logs.

## 7. Success Record Policy

For a successful first remote run, record only:

- run date
- branch
- workflow result
- safe high-level status
- confirmation that no raw logs were copied
- confirmation that no artifacts were uploaded

Do not paste raw GitHub Actions logs into public docs. A concise public note may
say that the manual release-quality workflow ran successfully if separately
reviewed.

For a blank safe reporting format, use the
[release-quality manual workflow remote-run report template](templates/release_quality_manual_workflow_remote_run_report_template.md).

## 8. Failure Record Policy

For a failed first remote run, record only:

- failing stage name
- safe reason
- whether local reproduction is available
- whether workflow setup, environment differences, or wrapper behavior need
  review

Do not paste raw output bodies, JSONL bodies, summary bodies, marker bodies,
config bodies, candidate score rows, or raw text into public docs or comments.

## 9. Next Decision

Use the first remote run result to choose the next action:

- remote run passes: the manual workflow is usable for on-demand
  release-quality review
- setup failure: revise workflow setup in a separate implementation step
- wrapper failure only in Actions: investigate environment differences
- unsafe logs: stop and revise output safety before further remote runs
- too slow: consider a lighter pull-request CI subset and keep the full wrapper
  as manual

The result is not a performance claim and must not be interpreted as model,
scoring, or learner-state quality evidence.

## 10. Beginner Notes

A remote run is a workflow run executed on GitHub Actions, not on the local
machine.

Local success is still not enough because the GitHub runner has its own operating
system image, dependency cache, permissions, and installed tool versions.

Log safety matters because remote CI logs are often visible to collaborators and
may be copied into reviews. They should show safe status and reasons, not data
bodies.

Raw logs should not be pasted into docs because they may include environment
details or generated output that is not appropriate for public repository
history.

## 11. Related Documents

- [Release-quality manual workflow design](release_quality_manual_workflow_design.md)
- [Release-quality wrapper CI integration design](release_quality_wrapper_ci_integration_design.md)
- [Release-quality command bundle design](release_quality_command_bundle_design.md)
- [Release-quality manual workflow remote-run report template](templates/release_quality_manual_workflow_remote_run_report_template.md)
- [Public release checklist](public_release_checklist.md)
