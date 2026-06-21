# Milestone 04 CI Maintenance Recap

This document recaps the CI maintenance and release-quality workflow work from
Steps 132 through 140. It is recap documentation only. It does not change
GitHub Actions workflows, shell scripts, tests, scorer behavior, manifest
schema, or pipeline logic.

This milestone is workflow maintenance. It is not a performance evaluation,
accuracy claim, calibration check, or learner-state estimate.

## 1. Purpose

The purpose of this recap is to record a clear stopping point for CI maintenance
and release-quality workflow hardening.

It summarizes:

- how the GitHub Actions Node runtime warning was handled
- how the manual release-quality workflow was updated and checked
- how the existing push/pull-request CI workflow was audited and updated
- how safe remote-run recording policies were kept separate from raw logs

The recap keeps release-quality workflow maintenance separate from existing CI
maintenance, and both separate from scorer or model behavior.

## 2. Milestone Scope

This milestone covers Steps 132 through 140:

- GitHub Actions maintenance
- release-quality manual workflow action-version planning and update
- existing CI checkout action audit and update
- safe remote-run recording policy for both workflows
- remote success confirmations at a safe high level

Out of scope:

- scorer logic changes
- scoring formula changes
- tie-break policy changes
- metric implementation
- F1, accuracy, or calibration
- learner-state estimation
- production data handling
- real participant data

## 3. Step-By-Step Recap

Step 132: GitHub Actions Node runtime warning handling design.

- Documented the Node runtime deprecation warning seen after the first manual
  release-quality remote run.
- Separated workflow Success from warning status.
- Kept wrapper, scorer, manifest schema, and synthetic pipeline out of scope.

Step 133: release-quality workflow action version update plan.

- Planned how to update the manual workflow's GitHub-owned actions.
- Kept `.github/workflows/ci.yml` out of scope for that first update.
- Defined verification and rollback expectations.

Step 134: release-quality action update.

- Updated GitHub-owned actions in `.github/workflows/release-quality.yml`.
- Kept `workflow_dispatch` only.
- Kept artifact upload absent.
- Kept `scripts/check_release_quality.sh` as the wrapper command.

Step 135: post-update manual remote run success.

- Confirmed the updated manual release-quality workflow at a safe high level.
- Visible summary: Success.
- Visible artifact status: none.
- Visible Node runtime warning status: not shown.
- Raw logs and run URL were not added to public docs.

Step 136: action update remote-run record workflow.

- Defined how to safely record the release-quality action update remote run.
- Allowed only safe high-level summary fields.
- Prohibited raw logs, body dumps, and performance claims.

Step 137: existing CI action audit design.

- Audited `.github/workflows/ci.yml`.
- Identified `actions/checkout@v4` as the GitHub-owned action in existing CI
  relevant to Node runtime maintenance risk.
- Kept `dtolnay/rust-toolchain@stable` separate as a third-party action.

Step 138: existing CI checkout action update.

- Updated only `.github/workflows/ci.yml` checkout from `actions/checkout@v4`
  to `actions/checkout@v7`.
- Kept `dtolnay/rust-toolchain@stable` unchanged.
- Kept CI triggers, job structure, and artifact policy unchanged.

Step 139: existing CI remote-run record workflow.

- Defined how to safely record remote CI results after the checkout update.
- Separated CI success, warning status, and artifact status from raw logs.
- Reaffirmed that CI success is not a performance claim.

Step 140: remote CI success confirmation.

- Confirmed the existing CI checkout update at a safe high level.
- Visible summary: Success.
- Visible artifact status: none.
- Visible Node runtime warning status: not shown.
- Raw logs and run URL were not added to public docs.

## 4. Current Workflow State

### `release-quality.yml`

Current state:

- trigger: `workflow_dispatch` only
- artifact upload: absent
- wrapper command: `scripts/check_release_quality.sh`
- checkout action: `actions/checkout@v7`
- Python setup action: `actions/setup-python@v6`
- Node setup action: `actions/setup-node@v6`
- Rust toolchain action: `dtolnay/rust-toolchain@stable`

The manual release-quality workflow remains the full on-demand check path.

### `ci.yml`

Current state:

- triggers: `push` and `pull_request`
- checkout action: `actions/checkout@v7`
- Rust toolchain action: `dtolnay/rust-toolchain@stable`
- artifact upload: absent
- job structure: maintained
- Rust format, test, clippy, synthetic policy, CLI smoke, and synthetic E2E
  smoke checks: maintained

The existing CI workflow remains the narrower Rust-centered push/pull-request
check path.

## 5. Confirmed Remote Results

Safe high-level summary only:

| Workflow | Result | Artifact Status | Visible Warning Status | Notes |
| --- | --- | --- | --- | --- |
| Release-quality manual workflow | Success | none | not shown | Confirmed after GitHub-owned action updates |
| Existing CI workflow | Success | none | not shown | Confirmed after checkout action update |

Do not add raw workflow logs, run URLs, screenshots with sensitive content, or
body outputs to public docs.

These confirmations are workflow maintenance checks. They are not evidence of
research accuracy, F1, calibration, learner-state quality, or scorer quality.

## 6. Safety / Privacy / No-Oracle Boundaries

This milestone keeps these boundaries:

- no real participant data
- no JSONL body
- no summary body
- no marker body
- no diagnostic body
- no config body
- no candidate score rows
- no raw workflow logs
- no expected-action scoring feedback
- no performance metrics

Safe status fields such as workflow name, result, artifact status, warning
status, action version, and high-level maintenance decision are allowed.

## 7. What Changed

Workflow maintenance changes:

- release-quality workflow GitHub-owned actions were updated
- existing CI checkout action was updated
- safe record workflows were added for post-update remote-run summaries
- related checklists and release documentation were linked

Documentation and process changes:

- warning handling design was added
- action update plan was added
- existing CI action inventory was documented
- remote-run record policies were added for both manual release-quality and
  existing CI workflows

The release-quality wrapper already existed before this milestone and remains
unchanged during this recap step.

## 8. What Did Not Change

This milestone did not change:

- scorer logic
- scoring formula
- tie-break behavior
- manifest schema
- summary hash
- per-case diagnostic consistency checks
- actual config fixtures
- candidate generation
- learner-state estimation
- production data handling
- expected-action feedback policy
- JSONL or summary content policy
- workflow triggers beyond the already intended workflows

No actual filled remote-run report is added to public docs by this recap.

## 9. Remaining Risks

Remaining maintenance risks:

- future GitHub Actions deprecations
- third-party action maintenance
- remote/local environment differences
- Markdown link check remains a manual note inside the release-quality wrapper
- future PR CI integration choices
- future action-version drift between workflows

These are workflow maintenance risks, not scorer or model-performance risks.

## 10. Future Options

Possible future work:

- inspect third-party action release notes if warnings appear
- plan a project Markdown link checker separately
- decide whether selected release-quality checks should move into PR CI
- keep the manual release-quality workflow as the full check path
- schedule periodic action version audits
- continue recording remote-run results only as safe high-level summaries

Any future public record should avoid raw logs, run URLs with private context,
body dumps, and performance claims.
For the final docs-only release-readiness review of this milestone, see
[milestone 04 final docs-only release review](milestone_04_final_docs_only_release_review.md).
For a future short public-safe marker that summarizes this milestone status
without raw logs or performance claims, see
[milestone 04 status marker design](milestone_04_status_marker_design.md).

## 11. Beginner Notes

A milestone recap is a short checkpoint document. It explains what a sequence of
work accomplished and what remains outside the milestone.

CI maintenance is different from research performance. Updating GitHub Actions
helps workflows keep running, but it does not prove that scoring, candidate
generation, or learner-state estimates are better.

The warning handling was done in stages because workflow changes can affect
remote CI behavior. Smaller steps are easier to verify and roll back.

Raw logs are not pasted because logs can contain paths or generated output that
should not be preserved in public documentation. A safe high-level result is
enough for maintenance tracking.

The release-quality workflow and `ci.yml` serve different roles. The
release-quality workflow is a manual full check. The existing CI workflow runs
on push and pull request and focuses on Rust-centered checks.

## Related Documents

- [GitHub Actions Node deprecation warning handling design](actions_node_deprecation_warning_handling_design.md)
- [Release-quality action version update plan](release_quality_action_version_update_plan.md)
- [Release-quality action update remote-run record workflow](release_quality_action_update_remote_run_record_workflow.md)
- [Existing CI action versions audit design](existing_ci_action_versions_audit_design.md)
- [Existing CI checkout update remote-run record workflow](existing_ci_checkout_update_remote_run_record_workflow.md)
- [Milestone 04 final docs-only release review](milestone_04_final_docs_only_release_review.md)
- [Milestone 04 status marker design](milestone_04_status_marker_design.md)
- [Public release checklist](public_release_checklist.md)
