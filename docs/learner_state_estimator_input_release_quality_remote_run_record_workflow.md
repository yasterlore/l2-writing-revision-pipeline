# Learner-State Estimator Input Release-Quality Remote Run Record Workflow

This document defines how to record a remote/manual GitHub Actions
Release Quality run after the learner-state estimator input validator has been
added to the release-quality wrapper.

This is record-workflow design documentation. It does not change GitHub
Actions workflows, the Makefile, the release-quality wrapper, shell scripts,
estimator input validator code, sequence exporter code, audit code, tests, or
fixture files. It is not a performance evaluation and is not a real-data
readiness claim.

## 1. Purpose

The purpose of this document is to define a public-safe recording policy for a
remote/manual Release Quality run after estimator input validator wrapper
integration.

The record should capture only public-safe metadata:

- whether the existing manual Release Quality workflow completed
- whether the learner-state audit fixture check was included
- whether the learner-state exporter CLI smoke check was included
- whether the learner-state estimator input validation check was included
- whether logs appeared safe after review
- whether artifacts were absent

The record must not include raw GitHub Actions logs, generated output bodies,
JSONL rows, fixture row contents, private paths, expected action bodies, or
performance metrics.

## 2. Current State

Current state:

- The estimator input validator Python API exists in
  `python/learner_state/estimator_input.py`.
- The estimator input validator CLI exists as
  `python -m learner_state.estimator_input`.
- `make check-learner-state-estimator-input` exists.
- The release-quality wrapper calls
  `make check-learner-state-estimator-input`.
- Local `make check-release-quality` has passed with the estimator input
  validation section included.
- The existing manual Release Quality GitHub Actions workflow exists.
- No direct CI workflow edit was made for estimator input validation.

The remote/manual run record is a verification record for wrapper behavior in a
GitHub Actions environment, not a new implementation step.

## 3. Remote / Manual Workflow To Run

Use the existing GitHub Actions manual Release Quality workflow:

- workflow name: `Release Quality`
- trigger: `workflow_dispatch`
- branch: `main` after the wrapper integration is merged
- expected artifacts: none

The workflow should run the release-quality wrapper through the existing
workflow definition. Do not add direct workflow steps for estimator input
validation during this recording step.

The run reviewer should not paste raw logs into docs. Generated exporter output
files, estimator fixture rows, and validator result dumps should not be
uploaded as artifacts.

## 4. What To Record

A public-safe record may include:

- workflow name
- job name
- branch
- commit short hash
- run number, if useful
- status: success or failure
- duration
- job duration, if available
- artifact presence
- whether the learner-state audit fixture check was included
- whether the learner-state exporter CLI smoke check was included
- whether the learner-state estimator input validation check was included
- estimator input validation result summary: pass or fail
- fixture-root `total_cases`, `matched_cases`, and `mismatched_cases` if
  visible in safe summary output
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
- feature rows
- label rows
- manifest body
- expected action body
- private paths
- performance metrics

## 5. Log Safety Review Checklist

Before creating a public-safe status marker, review the remote logs for these
safety conditions:

- no raw JSONL lines
- no feature rows
- no label rows
- no manifest body
- no private absolute path
- no real data path
- no expected action body
- no raw stack trace with row content
- no performance claims
- estimator input validation section shows only safe summary fields
- `content_suppressed=true` if visible
- `no_raw_rows=true` if visible

If any unsafe output appears, do not create a public record with details.
Create a private/local note instead and fix the output path before publishing a
status marker.

## 6. Success Interpretation

Remote workflow success means:

- the release-quality wrapper completed under GitHub Actions
- the wrapper included estimator input validation if the log section confirms
  it
- the configured synthetic estimator input fixtures matched their expected
  validation results if the safe summary confirms it

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
- `learner_state_audit_fixture_mismatch`
- `exporter_cli_smoke_failure`
- `estimator_input_validation_failure`
- `estimator_input_expected_result_mismatch`
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
- learner-state exporter release-quality remote run status
- Milestone 06 learner-state audit infrastructure recap
- Milestone 07 learner-state sequence exporter infrastructure recap
- release-quality action update records

This workflow is specifically for remote verification of estimator input
validation after it is included in the release-quality wrapper.

## 10. Future Roadmap

Recommended next steps:

1. Step203: run the manual Release Quality workflow and create either a
   public-safe run record or a private/local note.
2. Step204: optional status marker update or Milestone 08 recap.
3. Later: selective prediction and calibration design.
4. Later: estimator prototype design.
5. Later: review whether direct CI integration is useful.

Do not treat the remote run as performance evidence, estimator correctness
evidence, or real-data readiness.

Step203 follow-up: a public-safe status marker is available at
[Learner-state estimator input release-quality remote run status](status/learner_state_estimator_input_release_quality_remote_run_status.md).
It records only metadata and count-only summaries; it does not include raw
GitHub Actions logs, generated output bodies, JSONL rows, or fixture row
contents.

## 11. Beginner Notes

A remote/manual workflow is a GitHub Actions job that is started manually from
GitHub rather than from the local machine.

Checking the remote run matters because GitHub Actions may have a different
environment from the developer machine. A local pass is necessary, but it does
not confirm the wrapper works on the remote runner.

Raw logs should not be pasted into docs because they can contain more detail
than the public record needs. A safe record only needs metadata, counts, and
status.

Success means the release-quality wrapper ran in the remote environment and
included estimator input validation. It does not prove model quality,
estimator correctness, real-data readiness, or production data collection
readiness.

## 12. Related Documents

- [Learner-state estimator input release-quality integration design](learner_state_estimator_input_release_quality_integration_design.md)
- [Learner-state estimator input validator Makefile target design](learner_state_estimator_input_validator_makefile_target_design.md)
- [Learner-state estimator input validator CLI design](learner_state_estimator_input_validator_cli_design.md)
- [Learner-state estimator input validation design](learner_state_estimator_input_validation_design.md)
- [Learner-state estimator input fixtures](../tests/fixtures/learner_state_estimator_input/README.md)
- [Learner-state exporter release-quality remote run record workflow](learner_state_exporter_release_quality_remote_run_record_workflow.md)
- [Public release checklist](public_release_checklist.md)
