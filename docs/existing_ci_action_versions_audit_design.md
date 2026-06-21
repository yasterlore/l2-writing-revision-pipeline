# Existing CI Action Versions Audit Design

This document designs a docs-only audit for action versions in the existing
`.github/workflows/ci.yml` workflow. It does not change GitHub Actions
workflows, shell scripts, tests, scorer behavior, manifest schema, or CI
triggers.

This audit is workflow-maintenance documentation. It is not a performance
evaluation, tuning signal, or learner-state estimate.

## 1. Purpose

The purpose of this audit design is to inspect the action versions used by the
existing CI workflow before changing that workflow.

The audit keeps these concerns separate:

- the release-quality manual workflow, which has already had GitHub-owned
  action versions updated
- the existing CI workflow, which remains unchanged
- GitHub Actions Node runtime warnings and other maintenance risks
- workflow update verification and rollback planning

The audit must not weaken output safety, no-oracle boundaries, or synthetic-only
fixture policy.

## 2. Current State

- `.github/workflows/release-quality.yml` has updated GitHub-owned action
  versions.
- `.github/workflows/ci.yml` has not been changed for the action-version update
  sequence.
- The existing CI workflow is Rust-centered.
- The release-quality workflow remains manual-only with `workflow_dispatch`.
- Existing CI action versions had not yet been organized in a dedicated audit
  document before this step.

## 3. `ci.yml` Action Inventory

Current actions used by `.github/workflows/ci.yml`:

| Workflow | Job | Action | Owner Type | Purpose | Warning Relevance |
| --- | --- | --- | --- | --- | --- |
| `CI` | `Rust workspace` | `actions/checkout@v4` | GitHub-owned | Checks out the repository before Rust and policy checks | Potentially relevant to GitHub Actions Node runtime deprecation warnings because it is a JavaScript action |
| `CI` | `Rust workspace` | `dtolnay/rust-toolchain@stable` | third-party | Installs stable Rust with `rustfmt` and `clippy` components | Not one of the GitHub-owned actions noted in the release-quality warning; review separately before changing |

The workflow also runs shell commands for formatting, tests, clippy, synthetic
policy, CLI fixture smoke checks, and a synthetic E2E pipeline smoke check.
Those commands are not reusable GitHub Actions and are outside the action-version
inventory.

Do not paste raw CI logs into this audit. If a remote CI run produces warnings,
record only a short safe summary.

## 4. Warning Risk Assessment

`actions/checkout@v4` is the main action in existing CI that may be relevant to
GitHub Actions Node runtime warnings. If GitHub-hosted runners force older
internal action runtimes onto a newer Node runtime, CI can still succeed while
showing a maintenance warning.

`dtolnay/rust-toolchain@stable` should be treated separately:

- it is third-party, not GitHub-owned
- it was not part of the visible release-quality Node warning target list
- it affects Rust setup behavior, so updates should be based on that action's
  own release notes and compatibility expectations

Warnings are not the same as workflow failures. A warning can indicate future
maintenance risk while the current workflow still passes. Conversely, a workflow
failure after an action update is an actual CI behavior issue and should be
triaged separately.

The release-quality workflow warning follow-up should not be mixed with existing
CI. The manual workflow can be clean while `ci.yml` still needs its own audit.

## 5. Update Options

Option A: update GitHub-owned actions in `ci.yml` similarly to
`release-quality.yml`.

- Pros: reduces Node runtime warning risk in the existing CI workflow
- Cons: changes a PR/push workflow and should be verified through remote CI

Option B: keep `ci.yml` unchanged until a warning is observed.

- Pros: avoids touching a working workflow
- Cons: defers maintenance and can leave a warning for contributors

Option C: keep `ci.yml` as lightweight PR CI and keep only the manual workflow
fully updated for now.

- Pros: minimizes PR CI churn
- Cons: two workflows may use different action major versions for longer

Option D: align action majors between `ci.yml` and `release-quality.yml`.

- Pros: easier to reason about shared workflow maintenance
- Cons: still needs careful verification because triggers and job scopes differ

Option E: update GitHub-owned and third-party actions together.

- Pros: one maintenance pass
- Cons: higher review and rollback risk; third-party behavior changes can be
  unrelated to the Node runtime warning

## 6. Recommended Approach

Initial recommendation:

- keep this step docs-only
- in a later step, consider a minimal update for GitHub-owned actions in
  `.github/workflows/ci.yml`
- treat third-party actions separately after checking their release notes and
  compatibility expectations
- do not change `.github/workflows/release-quality.yml` as part of the existing
  CI audit
- keep current PR/push trigger behavior and job structure unchanged unless a
  separate design calls for it
- after any `ci.yml` update, verify via remote CI or PR checks and record only a
  safe warning-status summary

For the currently observed inventory, that means `actions/checkout@v4` is the
first candidate for a future GitHub-owned action update. The Rust toolchain
action should not be updated merely because a GitHub-owned Node runtime warning
was seen elsewhere.

## 7. Verification Plan

Before and after any future `ci.yml` action-version update, verify:

- `.github/workflows/ci.yml` parses as YAML
- `.github/workflows/release-quality.yml` still parses as YAML
- CI triggers remain intentional
- action versions can be listed clearly
- no artifact upload is introduced unless separately designed
- local relevant checks still pass
- remote CI or PR checks run after the workflow update
- warning status is recorded only as a safe summary
- raw logs are not copied into docs or public comments

Local checks may include:

- `sh -n scripts/check_release_quality.sh`
- `scripts/check_release_quality.sh`
- Python unit tests and compile checks
- Rust format, test, and clippy checks
- synthetic policy and smoke checks
- logger-web typecheck, test, and build if the release-quality wrapper remains a
  reference point for broader release safety

## 8. Rollback Plan

If a future `ci.yml` action-version update causes setup failure, remote-only
failure, or unsafe logs:

- revert only the `ci.yml` action-version changes
- do not change the release-quality workflow as part of that rollback
- do not change wrapper scripts, scorer logic, manifest schema, scoring formula,
  or tie-break behavior
- keep the rollback record as a safe summary only
- avoid pasting raw CI logs or body outputs into docs

## 9. Safe Documentation Policy

Do not include:

- raw CI logs
- raw workflow output
- JSONL body
- summary body
- marker body
- diagnostic body
- config body
- candidate score rows
- raw learner text
- expected action details
- performance metrics
- real participant data
- private paths

Allowed documentation is limited to safe metadata such as action name, action
version, workflow name, job name, warning status, pass/fail status, and safe
reason.

## 10. Beginner Notes

A CI action audit is a checklist for the reusable GitHub Actions a workflow
depends on. It answers: what actions are used, who owns them, what versions are
pinned, and which ones may need maintenance.

The release-quality workflow and `ci.yml` are different workflows. The manual
release-quality workflow runs on demand and exercises a broad command bundle.
The existing CI workflow runs on push and pull request and is narrower.

Updating every workflow at once can make failures harder to understand. A narrow
update lets reviewers see whether a failure came from checkout, Rust setup, or a
project command.

A warning is not a failure. A warning says "this may need maintenance"; a failure
says "the workflow did not complete successfully." Both matter, but they are
handled differently.

Remote CI confirmation matters because GitHub Actions warnings and setup
behavior can appear only on GitHub-hosted runners.

## Related Documents

- [GitHub Actions Node deprecation warning handling design](actions_node_deprecation_warning_handling_design.md)
- [Release-quality action version update plan](release_quality_action_version_update_plan.md)
- [Release-quality action update remote-run record workflow](release_quality_action_update_remote_run_record_workflow.md)
- [Release-quality wrapper CI integration design](release_quality_wrapper_ci_integration_design.md)
- [Public release checklist](public_release_checklist.md)
