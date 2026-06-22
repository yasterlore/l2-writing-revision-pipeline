# Learner-State Exporter Release-Quality Remote Run Record Workflow

This document defines how to record a remote/manual GitHub Actions
Release Quality run after the learner-state exporter CLI smoke check has been
added to the release-quality wrapper.

This is record-workflow design documentation. It does not change GitHub
Actions workflows, the Makefile, release-quality wrapper, shell scripts,
exporter code, exporter tests, audit code, or fixture files. It is not a
performance evaluation and is not a real-data readiness claim.

## 1. Purpose

The purpose of this document is to define a public-safe recording policy for a
remote/manual release-quality run after exporter CLI smoke wrapper integration.

The record should capture only public-safe metadata:

- whether the existing manual Release Quality workflow completed
- whether the learner-state audit fixture check was included
- whether the learner-state exporter CLI smoke check was included
- whether logs appeared safe after review
- whether artifacts were absent

The record must not include raw GitHub Actions logs, generated output bodies,
JSONL rows, fixture row contents, private paths, expected action bodies, or
performance metrics.

## 2. Current State

Current state:

- `python/learner_state/sequence_exporter.py` exists.
- The exporter CLI exists as `python -m learner_state.sequence_exporter`.
- `make check-learner-state-exporter-cli` exists.
- The release-quality wrapper calls `make check-learner-state-exporter-cli`.
- Local `make check-release-quality` has passed with the exporter CLI smoke
  section included.
- The existing manual Release Quality GitHub Actions workflow exists.
- No direct CI workflow edit was made for the exporter CLI smoke check.

The remote/manual run record is a verification record for wrapper behavior in a
GitHub Actions environment, not a new implementation step.

## 3. Remote / Manual Workflow To Run

Use the existing GitHub Actions manual Release Quality workflow:

- workflow name: `Release Quality`
- trigger: `workflow_dispatch`
- branch: `main` after the wrapper integration is merged
- expected artifacts: none

The workflow should run the release-quality wrapper through the existing
workflow definition. Do not add direct workflow steps for the exporter CLI smoke
check during this recording step.

The run reviewer should not paste raw logs into docs. Generated exporter output
files should not be uploaded as artifacts.

## 4. What To Record

A public-safe record may include:

- workflow name
- branch
- commit short hash
- run number, if useful
- status: success or failure
- duration
- job duration, if available
- artifact presence
- whether the learner-state audit fixture check was included
- whether the learner-state exporter CLI smoke check was included
- exporter CLI smoke result summary: pass or fail, count-only if available
- whether log review found raw row, body, or private path exposure
- warning summary, if any
- whether raw logs were excluded from docs

Do not record:

- raw logs
- full job output
- generated `features.jsonl` body
- generated `labels.jsonl` body
- generated `manifest.json` body
- JSONL rows
- fixture row contents
- label body
- expected action body
- private paths
- performance metrics

## 5. Log Safety Review Checklist

Before creating a public-safe status marker, review the remote logs for these
safety conditions:

- no raw JSONL lines
- no generated feature rows
- no generated label rows
- no manifest body
- no private absolute path
- no real data path
- no expected action body
- no raw stack trace with row content
- no performance claims
- exporter CLI section shows only safe summary fields

If any unsafe output appears, do not create a public record with details.
Create a private/local note instead and fix the output path before publishing a
status marker.

## 6. Success Interpretation

Remote workflow success means:

- the release-quality wrapper completed under GitHub Actions
- the wrapper included the learner-state exporter CLI smoke check if the log
  section confirms it
- the configured synthetic valid exporter fixtures passed the smoke path

Remote workflow success does not mean:

- model validity
- learner-state estimator correctness
- real-data readiness
- production data collection validation
- F1, accuracy, calibration, ECE, or AURCC evidence
- scoring model improvement

## 7. Failure Interpretation

Failures should be categorized using safe summaries only.

Allowed public-safe failure categories:

- `environment_failure`
- `dependency_failure`
- `exporter_cli_smoke_failure`
- `learner_state_audit_fixture_mismatch`
- `unsafe_output_exposure`
- `unrelated_check_failure`
- `unknown_safe_summary_only`

Do not paste raw logs or full failure output into docs. If the failure includes
raw output exposure, treat it as a safety issue and keep the detailed record
private/local.

## 8. Recommended Record Location

Candidate locations:

| Location | Pros | Cons |
| --- | --- | --- |
| `docs/status/` | Public-safe, easy to link from recaps | Requires careful redaction |
| Private/local notes | Safest for questionable logs | Not discoverable in repo |
| Public checklist only | Lightweight | Too little detail for traceability |
| No persistent public record | Avoids disclosure risk | Loses verification history |

Recommendation:

- Use this document for the recording workflow design.
- In the next step, choose between a public-safe `docs/status/` marker and a
  private/local note based on log safety review.
- If logs are clean, prefer a short `docs/status/` marker with metadata only.
- If logs contain unsafe bodies or private paths, do not publish the details.

## 9. Relation To Existing Status Markers

This record workflow complements:

- learner-state audit release-quality remote run status
- Milestone 06 status and recap documents
- release-quality action update records
- existing CI checkout update records

This workflow is specifically for remote verification of the exporter CLI smoke
check after it is included in the release-quality wrapper.

## 10. Future Roadmap

Recommended next steps:

1. Step 189: run the manual Release Quality workflow and create either a
   public-safe run record or a private/local note.
2. Step 190: optional status marker update if the remote run is public-safe.
3. Later: review whether direct CI integration is useful.
4. Later: broaden exporter fixtures.
5. Later: design learner-state estimator work.

Do not treat the remote run as performance evidence or real-data readiness.

Step189 follow-up: a public-safe status marker is available at
[Learner-state exporter release-quality remote run status](status/learner_state_exporter_release_quality_remote_run_status.md).
It records only metadata and count-only summaries; it does not include raw
GitHub Actions logs or generated output bodies.

## 11. Beginner Notes

A remote/manual workflow is a GitHub Actions job that is started manually from
GitHub rather than from the local machine.

Checking the remote run matters because GitHub Actions may have a different
environment from the developer machine. A local pass is necessary, but it does
not confirm the wrapper works on the remote runner.

Generated output bodies should not be pasted into docs because they are not
needed to verify the smoke check and can make public logs harder to review
safely.

Success means the release-quality wrapper ran in the remote environment and
included the exporter CLI smoke check. It does not prove model quality,
estimator correctness, real-data readiness, or production data collection
readiness.

## 12. Related Documents

- [Learner-state sequence exporter release-quality integration design](learner_state_sequence_exporter_release_quality_integration_design.md)
- [Learner-state sequence exporter Makefile target design](learner_state_sequence_exporter_makefile_target_design.md)
- [Learner-state sequence exporter CLI design](learner_state_sequence_exporter_cli_design.md)
- [Learner-state audit release-quality remote-run record workflow](learner_state_audit_release_quality_remote_run_record_workflow.md)
- [Public release checklist](public_release_checklist.md)
