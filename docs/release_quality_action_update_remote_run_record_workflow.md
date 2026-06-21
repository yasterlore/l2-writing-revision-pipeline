# Release-Quality Action Update Remote-Run Record Workflow

This document defines how to record the remote-run result after the
release-quality workflow action-version update.

It is record workflow documentation only. It is not an actual remote-run report,
does not change workflow files, and is not a performance evaluation.

## 1. Purpose

The purpose of this workflow is to define where and how to record the result of
the manual remote run after the release-quality action-version update.

The record must:

- avoid raw workflow logs
- record workflow success separately from warning status
- record artifact upload status at a high level
- make public documentation criteria explicit
- preserve no-oracle, privacy, and output-safety boundaries
- avoid any performance claim

## 2. Current State

Current state after the action-version update and Step 135 remote check:

- `.github/workflows/release-quality.yml` has updated action versions
- the workflow trigger remains `workflow_dispatch` only
- artifact upload is not configured
- `scripts/check_release_quality.sh` remains the wrapper command
- the visible Step 135 summary was Success
- artifacts were not shown in the visible Step 135 summary
- the Node.js runtime warning was not shown in the visible Step 135 summary
- no actual filled remote-run report is created by this document

The visible summary is useful for operational follow-up, but raw logs and output
bodies must not be copied into public docs.

## 3. Record Location Options

Option A: store an actual filled report in `local_notes/` or `private_notes/`.

- Pros: keeps detailed review local/private
- Cons: not visible in public repository history

Option B: add only a safe high-level summary to public docs.

- Pros: public maintenance status is visible
- Cons: must be carefully limited to safe fields

Option C: write only a safe PR comment.

- Pros: tied to the review context
- Cons: comments may be copied or quoted later

Option D: create an issue maintenance note.

- Pros: useful if follow-up is needed
- Cons: unnecessary for a simple pass with no visible warning

Option E: do not record the result, and use it only for the next decision.

- Pros: lowest public exposure
- Cons: loses maintenance traceability

## 4. Recommended Approach

Initial recommendation:

- keep any actual filled report in `local_notes/` or `private_notes/`
- keep `local_notes/` and `private_notes/` Git ignored
- do not paste raw logs into public docs
- do not paste run URLs into public docs if they expose private context
- if public documentation is needed, use safe high-level summary only
- record warning status as `not shown`, `still shown`, `changed`, or `unknown`
- record artifact upload as `yes` or `no`
- do not make performance claims

For Step 135, this document does not create the filled report. A maintainer may
fill the blank template privately or locally in a separate manual step.

## 5. Safe Summary Fields

Allowed safe summary fields:

- run result: pass / fail / cancelled
- branch
- short commit SHA
- approximate duration
- artifact uploaded: yes / no
- trigger: `workflow_dispatch`
- warning status: not shown / still shown / changed / unknown
- unsafe output noticed: yes / no / unknown
- decision

Do not include:

- raw logs
- raw workflow output
- JSONL body
- summary body
- marker body
- diagnostic body
- config body
- candidate score rows
- raw learner text
- expected action details
- private/manual/real paths
- real participant data

## 6. Public Documentation Criteria

Public documentation may include a safe summary only when all of these are true:

- only safe fields are included
- no raw logs are copied
- no run URL is included if it exposes private context
- no private paths are included
- no screenshot contains sensitive content
- no performance interpretation is made
- no claim implies that release-quality success validates research accuracy
- no JSONL, summary, marker, diagnostic, config, or candidate score body appears

If any criterion is unclear, keep the record private/local and do not add a
public summary yet.

## 7. Failure Recording Policy

For a failed action-update remote run, record only:

- failing stage name
- safe reason
- warning status
- local reproduction command
- whether unsafe logs were noticed

Do not paste raw logs or body dumps.

If unsafe logs are found, stop and fix output safety before continuing the
release process.

## 8. Decision Policy

Use this decision policy:

- success + no warning shown: workflow update is likely usable
- success + warning still shown: action update may be incomplete or another
  action may be affected
- failure in setup: inspect action-version compatibility
- failure in wrapper: compare local and remote environments
- unsafe logs: fix output safety before further release work

The decision is operational. It is not evidence of scorer quality, research
accuracy, calibration, or learner-state estimation.

## 9. Future Step Options

Possible next steps:

- create a private/local filled report manually
- optionally add a public safe maintenance note
- inspect existing `.github/workflows/ci.yml` action versions separately
- plan `ci.yml` Node warning handling separately
- decide whether PR CI should remain unchanged
- rerun the manual workflow after any future workflow action update

## 10. Beginner Notes

A successful workflow still needs a record policy because remote logs may
contain details that should not become public repository history.

Raw logs should not be pasted because they can contain environment details,
paths, or generated output. A safe summary is usually enough.

Public docs and private/local notes serve different purposes. Public docs should
be minimal and safe; private/local notes may hold more operational context when
needed.

Workflow success only means the release-quality checks ran successfully in that
environment. It is not proof of research performance, scoring accuracy, or model
quality.

## 11. Related Documents

- [Release-quality action version update plan](release_quality_action_version_update_plan.md)
- [GitHub Actions Node deprecation warning handling design](actions_node_deprecation_warning_handling_design.md)
- [Release-quality manual workflow remote-run checklist](release_quality_manual_workflow_remote_run_checklist.md)
- [Release-quality manual workflow remote-run report template](templates/release_quality_manual_workflow_remote_run_report_template.md)
- [Public release checklist](public_release_checklist.md)
