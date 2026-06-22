# Learner-State Audit Release-Quality Remote Run Record Workflow

This document defines how to safely record a remote/manual release-quality
workflow run after the learner-state audit fixture check has been integrated
into the release-quality wrapper.

It is record workflow documentation only. It does not change GitHub Actions
workflows, the Makefile, the release-quality wrapper, shell scripts, audit code,
fixture files, scorer behavior, candidate generation, or manifest schemas. It
is not a performance evaluation.

## 1. Purpose

The purpose of this document is to describe how to record a GitHub Actions
manual release-quality run after the wrapper includes the learner-state audit
fixture check.

The record policy must:

- confirm that the remote/manual wrapper run included the learner-state audit
  fixture check
- record only safe high-level status
- avoid raw workflow logs in public docs
- avoid JSONL rows, fixture row contents, label bodies, manifest bodies, and
  private paths
- separate release-quality wrapper success from model, scorer, estimator, or
  research-performance claims

This document is not a remote run report. It is not a workflow change, and it
does not claim production, research, or data-collection readiness.

## 2. Current State

Current state after learner-state audit wrapper integration:

- the learner-state sequence audit module exists
- the safe CLI exists as `python -m learner_state.sequence_audit`
- the Makefile target `check-learner-state-audit-fixtures` exists
- `scripts/check_release_quality.sh` calls the Makefile target
- local `make check-release-quality` passes after wrapper integration
- the manual release-quality workflow exists as
  `.github/workflows/release-quality.yml`
- CI workflows have not been edited for this integration
- artifact upload is not configured for the manual release-quality workflow

The next remote/manual confirmation should use the existing workflow rather than
editing workflow files.

## 3. Remote/Manual Workflow To Run

Use the existing GitHub Actions manual release-quality workflow:

- workflow: release-quality manual workflow
- trigger: `workflow_dispatch`
- branch: `main` after the integration has been merged, unless a maintainer is
  intentionally validating a review branch
- command path: the workflow runs `scripts/check_release_quality.sh`, which now
  runs `make check-learner-state-audit-fixtures`
- artifacts: should remain absent

Do not paste raw GitHub Actions logs into docs, issues, PR descriptions, or
status markers. Record only safe high-level status and safety-review fields.

## 4. What To Record

Allowed public-safe record fields:

- workflow name
- branch
- short commit hash
- run status: success, failure, or cancelled
- approximate duration
- artifact presence: yes or no
- whether the learner-state audit fixture check was included
- whether log review found raw row/body/private path exposure
- date/time, if useful
- high-level decision or next action

Forbidden record content:

- raw logs
- full job output
- JSONL rows
- fixture row contents
- label body
- manifest body
- candidate score rows
- raw learner text
- private paths
- expected action body
- screenshots that expose logs or private context
- run URLs when they expose private context or encourage raw-log copying
- performance metrics or model-quality claims

## 5. Log Safety Review Checklist

Before adding any public note, review the remote run logs at a high level and
confirm:

- no raw JSONL lines are visible
- no manifest body is visible
- no label body is visible
- no private absolute path is visible
- no real data path is visible, except a synthetic unsafe-path fixture phrase if
  it is expected and not private
- no expected action body is visible
- no raw stack trace includes row content
- no candidate score rows are visible
- no model, scorer, estimator, calibration, accuracy, or performance claim is
  made
- no artifact uploads expose generated outputs

If any item is unclear, keep the run record private/local and do not create a
public summary yet.

## 6. Success Interpretation

A successful remote/manual workflow run means:

- the release-quality wrapper completed in the GitHub Actions environment
- the wrapper included the learner-state audit fixture check
- the fixture-root audit expected results matched under that remote environment
- no artifact upload was observed, if the run summary confirms it
- log safety review did not find unsafe public output, if reviewed

It does not mean:

- the model is valid
- learner-state estimation is correct
- scorer quality is proven
- candidate ranking is research-valid
- real data handling is ready
- production or data-collection readiness has been achieved

The result is an operational wrapper-integration confirmation only.

## 7. Failure Interpretation

If the remote/manual workflow fails, record only safe categories such as:

- environment failure
- dependency setup failure
- Python check failure
- learner-state audit fixture mismatch
- unsafe output exposure
- release-quality wrapper failure
- unrelated Rust, logger, policy, summary-flow, or fixture check failure
- unknown failure pending private review

Do not paste raw logs. Do not paste row bodies, label contents, manifest bodies,
expected action bodies, stack traces with raw content, or private paths.

If unsafe output exposure occurs, treat it as an output-safety issue. Do not
publish details; fix output safety in a separate step before using the remote
run as release evidence.

## 8. Recommended Record Location

Record-location options:

| Option | Description | Pros | Cons | Recommendation |
| --- | --- | --- | --- | --- |
| `docs/status/` | Public-safe status marker or update | Easy to find | Must be very short and safe | Use only for a concise public-safe summary |
| Private/local notes | Filled report outside public history | Can include operational context | Not visible in public repo | Preferred for detailed review |
| Public release checklist | Checklist confirmation only | Keeps process visible | Not a run report | Good for guidance, not detailed results |
| No persistent record | Use run result only for next decision | Lowest exposure | Less traceability | Acceptable if no public update is needed |

Initial recommendation:

- keep detailed run review private/local
- use a public-safe status marker only if maintainers need public traceability
- keep public docs limited to safe metadata and safety conclusions
- never paste raw logs or output bodies into public docs

## 9. Relation To Existing Status Markers

This record workflow is related to, but narrower than, previous status and
remote-run documents:

- Milestone 04 and Milestone 05 status markers record broad public-safe
  maintenance status.
- Release-quality action update records describe remote-run records after
  workflow action-version changes.
- Existing CI checkout update records describe remote CI follow-up after CI
  workflow maintenance.
- This document is specifically for confirming that the learner-state audit
  fixture check is included in the release-quality wrapper during a remote
  manual workflow run.

Any future status marker should clearly say that it is wrapper-integration
status, not performance evidence.

## 10. Future Roadmap

Recommended next steps:

1. Step 173: run the manual release-quality workflow and create either a
   private/local filled report or a short public-safe run record.
2. Step 174: optionally update a status marker if public traceability is needed.
3. Later: review whether CI should consume the wrapper or stay unchanged.
4. Later: continue learner-state sequence exporter work separately.

No workflow, Makefile, wrapper, audit-code, fixture, scorer, or model changes
are part of this record workflow document.

## 11. Beginner Notes

A remote/manual workflow is a GitHub Actions run started by a person through
`workflow_dispatch`. It runs on GitHub's environment rather than on a local
machine.

Local success is useful, but remote success checks whether the same wrapper also
works with GitHub runner tools, permissions, and setup steps.

Raw logs are not pasted because logs may contain paths, generated output, or
row-like content that should not become public repository history.

Success means the wrapper ran and the included checks passed in that
environment. It does not measure model quality, scoring accuracy, calibration,
or learner-state validity.

## 12. Related Documents

- [Learner-state sequence audit release-quality integration design](learner_state_sequence_audit_release_quality_integration_design.md)
- [Learner-state sequence audit CLI integration design](learner_state_sequence_audit_cli_integration_design.md)
- [Release-quality manual workflow remote-run checklist](release_quality_manual_workflow_remote_run_checklist.md)
- [Release-quality manual workflow remote-run report template](templates/release_quality_manual_workflow_remote_run_report_template.md)
- [Release-quality action update remote-run record workflow](release_quality_action_update_remote_run_record_workflow.md)
- [Existing CI checkout update remote-run record workflow](existing_ci_checkout_update_remote_run_record_workflow.md)
- [Public release checklist](public_release_checklist.md)
