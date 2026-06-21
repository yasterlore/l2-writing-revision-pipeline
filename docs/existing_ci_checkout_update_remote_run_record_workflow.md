# Existing CI Checkout Update Remote-Run Record Workflow

This document defines how to safely record the remote CI result after the
existing CI checkout action update. It is record-workflow documentation only.
It is not an actual remote CI report, and it does not change GitHub Actions
workflows, shell scripts, tests, scorer behavior, manifest schema, or CI
triggers.

This workflow is maintenance documentation. It is not a performance evaluation,
accuracy claim, calibration check, or learner-state estimate.

## 1. Purpose

The purpose of this record workflow is to describe how to record remote CI
results after the `.github/workflows/ci.yml` checkout action update.

The record must:

- avoid raw CI logs
- record CI success, warning status, and artifact status only at a high level
- separate workflow maintenance from scorer or research behavior
- keep no-oracle and privacy boundaries unchanged

The record must not include JSONL body, summary body, marker body, config body,
candidate score rows, raw learner text, or real participant data.

## 2. Current State

Current state after Step 138:

- `.github/workflows/ci.yml` uses `actions/checkout@v7`
- `dtolnay/rust-toolchain@stable` is unchanged
- `.github/workflows/release-quality.yml` is unchanged
- CI triggers remain `push` and `pull_request`
- CI job structure is unchanged
- artifact upload is not configured
- no actual remote CI report is created by this document

The next confirmation should happen through a remote CI run or PR check. Public
documentation should receive only safe high-level status if a public note is
needed at all.

## 3. Remote CI Items To Check

During the remote CI run, check the following stages at a high level:

- checkout step success
- Rust toolchain step success
- `cargo fmt` success
- `cargo test` success
- `cargo clippy` success
- synthetic policy check success
- CLI valid fixture smoke success
- CLI invalid fixture smoke expected failure behavior
- synthetic E2E smoke success
- artifact upload remains absent
- Node runtime warning status
- overall workflow result: pass, fail, or cancelled

Do not copy step logs into docs. If a stage fails, record the stage name and a
safe reason only.

## 4. Safe Summary Fields

Allowed fields:

- workflow result: pass, fail, or cancelled
- branch
- short commit SHA
- trigger: `push` or `pull_request`
- approximate duration
- artifact uploaded: yes or no
- warning status: not shown, still shown, changed, or unknown
- failing stage, if any
- safe reason, if any
- decision

Forbidden fields:

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
- private, manual, or real paths
- real participant data

## 5. Public Documentation Criteria

Public documentation may include a remote CI summary only if all of these are
true:

- only safe fields are included
- raw logs are omitted
- run URLs that expose private context are omitted
- screenshots with sensitive content are omitted
- no performance interpretation is made
- CI success is not described as evidence of research accuracy
- no body dumps are included

If any log output looks unsafe, stop and fix output safety before adding any
public note.

## 6. Failure Recording Policy

If the remote CI run fails, record only:

- failing stage name
- safe reason
- warning status
- local reproduction command, if relevant
- whether unsafe output was noticed: yes, no, or unknown

Do not paste:

- raw logs
- JSONL rows
- summary rows
- marker JSON
- diagnostic summaries
- config body
- candidate score rows
- raw learner text

If unsafe logs are found, the next task should be output-safety hardening, not a
public release note.

## 7. Decision Policy

Use these high-level decision rules:

- CI success and warning not shown: checkout update is likely usable
- CI success and warning still shown: another action or runner warning may
  remain
- setup failure: inspect checkout version compatibility first
- Rust or toolchain failure: verify whether the issue is unrelated to checkout
- smoke failure: compare local and remote environments before changing logic
- unsafe logs: fix output safety before continuing release work

These decisions are workflow-maintenance decisions. They do not validate scorer
quality, learner-state estimation, or research performance.

## 8. Future Step Options

After the remote CI run:

- create a private or local filled CI report manually, if needed
- optionally add a public safe maintenance note
- inspect third-party actions only if warning remains
- decide whether `ci.yml` needs additional action updates
- leave `.github/workflows/release-quality.yml` unchanged unless a separate
  design calls for it

Any public note should remain a short maintenance summary and should not include
raw logs or body output.

## 9. Beginner Notes

A remote CI result is what GitHub Actions reports after running the workflow on a
GitHub-hosted runner. It can differ from local checks because the operating
system, installed tools, and action runtime are provided by GitHub.

Local pass is important, but it is not enough for workflow maintenance. The
checkout action update only fully proves itself after GitHub Actions can run the
workflow remotely.

Raw logs are not pasted because logs may contain paths, generated output, or
other details that do not belong in public documentation. A safe stage name and
short reason are usually enough.

A warning is not the same as a failure. A warning indicates maintenance risk; a
failure indicates the workflow did not complete successfully.

Workflow success is not evidence of research performance. It means CI commands
completed; it does not evaluate F1, accuracy, calibration, or learner-state
quality.

## Related Documents

- [Existing CI action versions audit design](existing_ci_action_versions_audit_design.md)
- [GitHub Actions Node deprecation warning handling design](actions_node_deprecation_warning_handling_design.md)
- [Release-quality action update remote-run record workflow](release_quality_action_update_remote_run_record_workflow.md)
- [Release-quality action version update plan](release_quality_action_version_update_plan.md)
- [Public release checklist](public_release_checklist.md)
