# Selective Prediction Release-Quality Remote Run Record Workflow

This document defines how to record a remote/manual GitHub Actions Release
Quality run after selective prediction calibration validation has been added
to the release-quality wrapper.

This is record-workflow design documentation. It is not an implementation, not
a remote run status marker, not a workflow change, and not a performance
evaluation. It does not change the release-quality wrapper, workflows,
Makefile, code, scripts, tests, or fixtures. It does not implement
calibration, selective prediction, estimator training, metric computation, or
real-data handling. It is not a real-data readiness claim.

## 1. Purpose

The purpose of this document is to define a public-safe recording workflow for
a remote/manual Release Quality run after selective prediction calibration
validation wrapper integration.

The record workflow should capture only high-level metadata:

- whether the existing manual Release Quality workflow completed
- whether the learner-state audit fixture check was included
- whether the learner-state exporter CLI smoke check was included
- whether the learner-state estimator input validation check was included
- whether the learner-state selective prediction calibration validation check
  was included
- whether selective prediction fixture-root expected results matched
- whether logs appeared safe after review
- whether artifacts were absent or not recorded

The record must not include raw GitHub Actions logs, full job output, JSONL
rows, prediction rows, label rows, split metadata bodies, calibration policy
bodies, logits/probability dumps, expected action bodies, generated output
bodies, raw learner text, private paths, or performance metrics.

## 2. Current State

Current state:

- local release-quality wrapper includes selective prediction calibration
  validation
- wrapper order is:
  1. learner-state audit fixtures
  2. learner-state exporter CLI smoke
  3. learner-state estimator input validation
  4. learner-state selective prediction calibration validation
  5. config/scoring smoke checks
- standalone target exists:
  `make check-learner-state-selective-prediction`
- standalone target passes with:
  - `total_cases=8`
  - `matched_cases=8`
  - `mismatched_cases=0`
  - `input_error_cases=0`
- local `make check-release-quality` has passed with the selective prediction
  calibration validation section included
- remote/manual run is not yet recorded
- workflow itself is unchanged
- no code, calibration, selective prediction, model, or metric implementation
  is added by this step

The remote/manual run record is a verification record for wrapper behavior in
a GitHub Actions environment, not a new implementation step.

## 3. Remote / Manual Run Trigger

Use the existing GitHub Actions manual Release Quality workflow:

- workflow name: `Release Quality`
- trigger: `workflow_dispatch`
- branch: `main` after the Step215 wrapper integration is merged
- expected artifacts: none, unless the workflow already creates them

The run should be started through the GitHub UI. Do not add direct workflow
steps for selective prediction calibration validation during this recording
step. Do not upload raw logs or generated output files to the repository.

## 4. Metadata To Record

A public-safe record may include only high-level metadata:

- workflow name
- job name
- repository
- branch
- commit short hash
- run status
- job status
- duration, if the GitHub UI confirms it
- artifacts: none or not recorded
- `release_quality_check` result: ok or fail
- `content_suppressed=true` if visible
- learner-state audit fixture check included: yes/no
- learner-state exporter CLI smoke included: yes/no
- learner-state estimator input validation included: yes/no
- learner-state selective prediction calibration validation included: yes/no
- selective prediction validation count-only result:
  - `total_cases`
  - `matched_cases`
  - `mismatched_cases`
  - `input_error_cases`
- log safety review result
- warning summary, if any

Count-only summaries are acceptable. Row bodies, policy bodies, split bodies,
and logits/probability dumps are not acceptable.

## 5. Metadata Not To Record

Do not record:

- raw GitHub Actions logs
- full job output
- prediction row body
- label row body
- split metadata body
- calibration policy body
- logits dump
- probability dump
- expected action body
- generated `features.jsonl` body
- generated `labels.jsonl` body
- generated `manifest.json` body
- JSONL rows
- raw learner text
- private paths
- raw stack traces with row content
- performance metrics as claims
- F1 claims
- accuracy claims
- ECE claims
- AURCC claims

If the remote run output contains unsafe material, do not create a public
status marker with those details.

## 6. Selective Prediction Section Extraction

From the run log, safely extract only the selective prediction calibration
section metadata needed for the record:

- `release_quality_check: learner-state selective prediction calibration
  validation`
- command used: `make check-learner-state-selective-prediction`
- `total_cases`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `content_suppressed`
- `no_raw_rows`

Do not copy the full section body if it contains more detail than the public
record needs. Do not copy row bodies, policy bodies, split bodies,
logits/probability dumps, expected action bodies, or stack traces with row
content.

## 7. Status Marker Design For Future Step217

Candidate future status marker locations:

| Candidate | Pros | Cons |
| --- | --- | --- |
| `docs/status/selective_prediction_release_quality_remote_run_status.md` | Short and easy to read | Less explicit that this belongs to learner-state infrastructure |
| `docs/status/learner_state_selective_prediction_release_quality_remote_run_status.md` | Consistent with existing learner-state status marker names | Longer filename |

Recommendation:

Use
`docs/status/learner_state_selective_prediction_release_quality_remote_run_status.md`
for Step217 if the remote run logs pass safety review. The learner-state prefix
matches the existing audit, exporter, and estimator input status marker family.

Planned future status marker fields:

- title
- purpose
- run metadata
- included checks
- selective prediction validation result
- log safety review
- scope limitations
- non-goals
- next steps

Step216 does not create this status marker.

## 8. Log Safety Review Checklist

Before creating a public-safe status marker, review the remote logs for these
safety conditions:

- no raw rows
- no prediction rows
- no label rows
- no calibration policy body
- no split metadata body
- no logits/probability dump
- no raw learner text
- no private paths
- no generated feature/label/manifest body
- no expected action body
- no performance claims
- no unexpected artifacts
- selective prediction section shows safe summary only
- `content_suppressed=true` if visible
- `no_raw_rows=true` if visible

If any unsafe output appears, do not publish a detailed public record. Keep the
details private/local and fix the unsafe output path before making another
public-safe status marker.

## 9. Failure Case Record Policy

If the remote/manual run fails, record only high-level metadata:

- workflow name
- job name
- branch
- commit short hash
- run status
- failed check label, if safely visible
- safe reason category, if safely visible
- artifact presence: none or not recorded
- log safety review result

Allowed safe failure categories include:

- `environment_failure`
- `dependency_failure`
- `learner_state_audit_fixture_mismatch`
- `exporter_cli_smoke_failure`
- `estimator_input_validation_failure`
- `selective_prediction_validation_failure`
- `selective_prediction_expected_result_mismatch`
- `test_tuning_leakage_detected`
- `label_leakage_detected`
- `split_leakage_detected`
- `unsafe_output_exposure`
- `unrelated_check_failure`
- `unknown_safe_summary_only`

Do not paste raw logs, full failure output, row bodies, or stack traces with
row content. A failure does not imply model performance failure. It may
indicate a fixture contract, leakage, path-safety, dependency, or unrelated
wrapper issue.

## 10. Success Interpretation

Remote workflow success means:

- the remote Release Quality wrapper completed under GitHub Actions
- selective prediction calibration validation was included if the log section
  confirms it
- fixture-root expected results matched if the safe summary confirms it
- logs remained safe after review

Remote workflow success does not mean:

- model performance is good
- calibration quality is validated
- selective prediction works on real data
- learner-state estimator correctness
- real-data readiness
- production data collection readiness
- F1 is measured
- accuracy is measured
- ECE is measured
- AURCC is measured

## 11. Relation To Previous Remote Run Records

This workflow should follow the same public-safe pattern as:

- learner-state audit release-quality remote run status
- learner-state exporter release-quality remote run status
- learner-state estimator input release-quality remote run status

The common pattern is:

- count-only summaries
- high-level metadata
- no raw logs
- no generated output bodies
- no row bodies
- no private paths
- no performance claims

This document is specifically for the selective prediction calibration
validation section after it has been added to the release-quality wrapper.

## 12. Future Implementation Plan

Recommended next steps:

1. Step217: run the manual Release Quality workflow and create a public-safe
   status marker if the logs pass safety review.
2. Step218: milestone recap for selective prediction validation
   infrastructure.
3. Step219: selective prediction / calibration scaffold design.
4. Step220: minimal learner-state estimator prototype design.

If the remote run output is not public-safe, create a private/local note
instead of a public status marker and fix the unsafe output path first.

## 13. Beginner Notes

A remote/manual run record is a short note about a GitHub Actions run that was
started manually from GitHub.

Checking GitHub Actions matters because the remote runner can differ from the
local machine. A local pass is important, but it does not prove the wrapper
works in the remote environment.

Raw logs should not be saved in docs because they can contain much more detail
than a public record needs. A safe record only needs metadata, counts, and a
log-safety review result.

Success is not performance evaluation. It only confirms that the remote
release-quality wrapper ran, included the selective prediction calibration
validation section, and matched the expected synthetic fixture results.

## 14. Related Documents

- [Selective prediction calibration release-quality integration design](selective_prediction_calibration_release_quality_integration_design.md)
- [Selective prediction calibration validator Makefile target design](selective_prediction_calibration_validator_makefile_target_design.md)
- [Selective prediction calibration validator CLI design](selective_prediction_calibration_validator_cli_design.md)
- [Selective prediction calibration validation design](selective_prediction_calibration_validation_design.md)
- [Selective prediction calibration fixture design](selective_prediction_calibration_fixture_design.md)
- [Selective prediction fixtures](../tests/fixtures/learner_state_selective_prediction/README.md)
- [Learner-state estimator input release-quality remote run record workflow](learner_state_estimator_input_release_quality_remote_run_record_workflow.md)
- [Public release checklist](public_release_checklist.md)
