# Release-Quality Workflow Action Version Update Plan

This document plans a future action-version update for the manual
release-quality workflow. It is documentation only. It does not change GitHub
Actions workflows, CI workflows, wrapper scripts, shell scripts, tests, scorer
logic, scoring formula, tie-break policy, manifest schema, or synthetic pipeline
logic.

The plan addresses the GitHub Actions Node.js runtime deprecation warning seen
after the first remote run. It is not a performance evaluation.

## 1. Purpose

The purpose of this plan is to define a safe update path for action versions in
the release-quality workflow before changing the workflow file.

The plan aims to:

- reduce or remove the GitHub Actions Node.js runtime warning
- keep workflow Success separate from warning status
- identify the exact workflow and actions in scope
- preserve the current trigger, wrapper command, and artifact policy
- define local and remote verification before considering the warning resolved

## 2. Target Workflow

Initial target:

- `.github/workflows/release-quality.yml`
- trigger: `workflow_dispatch` only
- artifact upload: none
- command: `scripts/check_release_quality.sh`
- existing `.github/workflows/ci.yml`: out of scope for this first update

This is a narrow workflow-maintenance change. It should not touch wrapper logic,
scoring logic, manifest schema, or release-quality command ordering.

## 3. Current Action Versions

The current release-quality workflow uses:

- `actions/checkout@v4`
- `actions/setup-python@v5`
- `dtolnay/rust-toolchain@stable`
- `actions/setup-node@v4`

The workflow also runs local shell commands, including `npm ci` in
`apps/logger-web` and `scripts/check_release_quality.sh` from the repository
root.

## 4. Warning Targets

The Step 131 remote run warning named these GitHub-owned actions:

- `actions/checkout@v4`
- `actions/setup-node@v4`
- `actions/setup-python@v5`

`dtolnay/rust-toolchain@stable` was not listed in the warning summary recorded
for Step 131. Treat it separately and do not update it as part of the Node.js
runtime warning response unless a later review identifies a specific need.

## 5. Update Candidates

Before implementing, review the official release notes and repository pages
again. Do not rely on this plan as a permanent version lock.

Initial candidates, based on official release pages checked for this plan:

| Current action | Candidate direction | Evidence to confirm before implementation |
| --- | --- | --- |
| `actions/checkout@v4` | update to a Node 24-compatible newer major, likely `actions/checkout@v6` or latest stable major after release-note review | official `actions/checkout` releases show newer majors, including `v6` and latest `v7` |
| `actions/setup-node@v4` | update to a Node 24-compatible newer major, likely latest stable `actions/setup-node@v6` line after release-note review | official `actions/setup-node` releases show the `v6` line and recent releases |
| `actions/setup-python@v5` | update to a Node 24-compatible newer major, likely latest stable `actions/setup-python@v6` line after release-note review | official `actions/setup-python` releases show `v6` releases with Node 24-compatible dependency updates |

Reference pages to review again before implementation:

- [actions/checkout releases](https://github.com/actions/checkout/releases)
- [actions/setup-node releases](https://github.com/actions/setup-node/releases)
- [actions/setup-python releases](https://github.com/actions/setup-python/releases)

Do not update `dtolnay/rust-toolchain@stable` for this warning unless a separate
Rust toolchain review calls for it.

## 6. Recommended Update Scope

Initial recommended scope:

- update only `.github/workflows/release-quality.yml`
- keep existing `.github/workflows/ci.yml` for a separate review step
- keep `workflow_dispatch` only
- keep artifact upload absent
- keep `scripts/check_release_quality.sh` unchanged
- keep `python-version`, `node-version`, npm cache settings, and `npm ci`
  behavior under explicit review
- do not alter wrapper, scorer, manifest schema, or synthetic summary logic

This keeps the blast radius small and makes the remote rerun easier to
interpret.

## 7. Verification Plan

After the workflow action update, verify:

- YAML parses successfully
- `workflow_dispatch` remains present
- `pull_request`, `push`, and `schedule` triggers remain absent
- artifact upload remains absent
- `scripts/check_release_quality.sh` is still called
- local `scripts/check_release_quality.sh` passes
- local full checks pass
- branch is pushed
- manual GitHub Actions remote run is executed
- warning status is recorded as removed, reduced, unchanged, or changed
- no raw workflow logs are copied into docs
- no `tmp/` outputs are uploaded as artifacts

Use the remote-run report template for the remote result.

## 8. Risk Assessment

Potential risks:

- checkout behavior may differ after a major action update
- setup-python behavior may differ after a major action update
- setup-node cache behavior may differ after a major action update
- `npm ci` may expose remote environment differences
- runner compatibility may differ from local checks
- a remote-only failure may occur even if local checks pass
- the warning may remain after the update if another action is involved
- logs must remain safe after any update

These risks are workflow maintenance risks, not scoring or learner-state
evidence.

## 9. Rollback Plan

If the remote run fails after the action-version update:

- revert only the workflow action-version changes on the update branch
- keep safe documentation summaries only
- do not alter wrapper scripts during rollback
- do not alter scorer logic
- do not alter manifest schema
- rerun local YAML and wrapper checks after rollback
- rerun the manual workflow remotely if needed

Rollback should not introduce actual config fixtures, scorer weight changes, or
new metrics.

## 10. Safe Documentation Policy

When documenting the update and remote rerun:

- do not paste raw workflow logs
- summarize warnings briefly
- do not paste JSONL body
- do not paste summary body
- do not paste marker body
- do not paste config body
- do not paste candidate score rows
- do not paste performance metrics
- do not paste real data or private paths

Safe status, action names, version labels, paths, counts, and short reasons are
acceptable.

## 11. Beginner Notes

An action version update changes the version of reusable GitHub Actions such as
checkout or setup-node.

Workflow Success means the previous run completed. A deprecation warning can
still matter because it points to future compatibility work.

Major updates can change behavior, so they need a small plan and a rerun.

Updating only `release-quality.yml` first keeps the change narrow. Existing CI
can be reviewed later.

Remote rerun is needed because the warning is produced by GitHub Actions, not by
local shell checks alone.

## 12. Related Documents

- [GitHub Actions Node deprecation warning handling design](actions_node_deprecation_warning_handling_design.md)
- [Release-quality manual workflow design](release_quality_manual_workflow_design.md)
- [Release-quality manual workflow remote-run checklist](release_quality_manual_workflow_remote_run_checklist.md)
- [Release-quality manual workflow remote-run report template](templates/release_quality_manual_workflow_remote_run_report_template.md)
- [Public release checklist](public_release_checklist.md)
