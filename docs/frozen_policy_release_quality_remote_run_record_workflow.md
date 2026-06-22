# Frozen Policy Release-Quality Remote Run Record Workflow

This document defines how to record a remote/manual GitHub Actions Release
Quality run after frozen policy validation has been added to the
release-quality wrapper.

This is record-workflow design documentation. It is not an implementation, not
an actual run status marker, not a workflow change, not a wrapper change, and
not a performance evaluation. It does not change Makefile targets, Python code,
tests, fixtures, calibration code, selective prediction code, frozen policy
generation scaffold, learner-state estimator code, training code, metric
computation, candidate generation, OT scoring, scoring formula, tie-break
logic, or manifest schemas. It is not a real-data readiness claim.

## 1. Purpose

The purpose of this document is to define a public-safe workflow for recording
a remote/manual Release Quality run that includes frozen policy validation.

The future record should capture only high-level metadata:

- whether the existing GitHub Actions Release Quality workflow completed
- whether the release-quality wrapper included frozen policy validation
- whether the frozen policy target matched its expected fixture results
- whether the related learner-state checks were included
- whether logs remained public-safe after review
- whether artifacts were absent or not recorded

The future record must not include raw GitHub Actions logs, full job output,
frozen policy artifact bodies, JSON bodies, raw rows, logits/probability
dumps, label bodies, split bodies, calibration policy bodies, private paths,
raw learner text, real participant data, or performance metric bodies.

## 2. Current State

Current state:

- `make check-learner-state-frozen-policy` exists.
- `scripts/check_release_quality.sh` includes frozen policy validation.
- The existing GitHub Actions Release Quality workflow calls the
  release-quality wrapper.
- The wrapper learner-state sequence includes:
  1. learner-state audit fixtures
  2. learner-state exporter CLI smoke
  3. learner-state estimator input validation
  4. learner-state selective prediction calibration validation
  5. learner-state frozen policy validation
  6. config/scoring smoke checks
- A remote/manual frozen policy Release Quality status marker does not exist
  yet.

The remote/manual run record is a traceability record for wrapper behavior in
GitHub Actions. It is not a new validator, not a model evaluation, and not a
real-data readiness record.

## 3. Remote / Manual Run Purpose

The remote/manual run should confirm that:

- the wrapper passes locally and in GitHub Actions
- frozen policy validation is included in the release-quality wrapper
- the frozen policy fixture-root expected-result matching remains stable
- only public-safe metadata is recorded afterward

The run is not performance evidence. It does not validate calibration quality,
selective prediction quality, learner-state estimator quality, production
readiness, or real-data handling.

## 4. Future Status Marker Path

Candidate future status marker paths:

| Candidate | Pros | Cons |
| --- | --- | --- |
| `docs/status/learner_state_frozen_policy_release_quality_remote_run_status.md` | Consistent with existing learner-state audit, exporter, estimator input, and selective prediction status marker names | Longer filename |
| `docs/status/frozen_policy_release_quality_remote_run_status.md` | Shorter and readable | Less explicit that this belongs to learner-state infrastructure |

Recommendation:

Use
`docs/status/learner_state_frozen_policy_release_quality_remote_run_status.md`
for the future status marker if the remote run logs pass safety review.

This follows the existing learner-state status marker family and keeps the
artifact-contract validation record near the other learner-state release-quality
records.

This Step231 document does not create the status marker.

Step232 follow-up: the public-safe status marker is available at
[Learner-state frozen policy release-quality remote run status](status/learner_state_frozen_policy_release_quality_remote_run_status.md).
It records only metadata and count-only summaries for the successful remote
Release Quality run; it does not include raw GitHub Actions logs, full job
output, copied log blocks, frozen policy artifact bodies, JSON bodies, raw
rows, logits/probability dumps, private paths, raw learner text, or
performance metric bodies.

## 5. Metadata To Record

A future public-safe status marker may record:

- workflow name
- job name
- repository
- branch
- commit full hash
- commit short hash
- run status
- job status
- run trigger type
- run date/time, if available
- `release_quality_check` included: yes/no
- frozen policy target included: yes/no
- target label
- `total_cases`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only_checked`
- `no_oracle_checked`
- `test_tuning_checked`
- `private_path_scan_checked`
- `performance_claim_scan_checked`
- workflow YAML changed: yes/no
- artifacts recorded: yes/no
- raw logs stored: yes/no
- safety review summary

The frozen policy target label should be recorded as:

```text
release_quality_check: learner-state frozen policy validation
```

The target command should be recorded as metadata only:

```text
make check-learner-state-frozen-policy
```

## 6. Metadata Not To Record

Do not record:

- raw GitHub Actions logs
- full job output
- frozen policy artifact body
- JSON body
- policy body
- raw rows
- logits dump
- probability dump
- label body
- split body
- calibration policy body
- private paths
- raw learner text
- real participant data
- performance metric body
- screenshots containing raw logs
- copied GitHub log blocks

If a remote log includes unsafe details, do not paste those details into docs.
Record only a safe failure category or keep the detailed note private/local.

## 7. Status Marker Structure

The future status marker should use this structure:

1. Title
2. Purpose
3. Run identity
4. Wrapper inclusion summary
5. Frozen policy validation summary
6. Related learner-state checks summary
7. Safety review
8. Interpretation
9. What this does not prove
10. Next actions
11. Update history

Run identity should include workflow/job/repository/branch/commit/status
metadata only.

Wrapper inclusion summary should state whether the release-quality wrapper
included the frozen policy check and whether workflow YAML changed.

Frozen policy validation summary should be count-only. It should not copy any
policy artifact body, expected-result JSON body, or fixture JSON body.

Related learner-state checks summary should be pass-only or count-only when a
safe count summary is visible.

Update history should be brief and should not include raw log excerpts.

## 8. Frozen Policy Validation Summary

The frozen policy section of the future status marker should be count-only:

- included: true/false
- target: `make check-learner-state-frozen-policy`
- label: `release_quality_check: learner-state frozen policy validation`
- `total_cases`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- no policy body
- no raw rows
- no logits dump
- no private paths
- no tmp output
- no performance evidence

Expected success-path count values are:

- `total_cases=12`
- `matched_cases=12`
- `mismatched_cases=0`
- `input_error_cases=0`

The future status marker should treat those values as fixture contract
matching, not as model performance.

## 9. Related Checks Summary

The future status marker may summarize these learner-state release-quality
checks:

- learner-state audit fixtures
- learner-state exporter CLI smoke
- learner-state estimator input validation
- learner-state selective prediction calibration validation
- learner-state frozen policy validation

Use pass-only or count-only summaries. Do not copy raw exporter output, JSONL
rows, generated feature/label/manifest bodies, prediction rows, label rows,
policy bodies, split bodies, logits/probability dumps, or raw learner text.

## 10. Safety Review

Before creating the future status marker, verify:

- `content_suppressed=true` when visible
- `no_raw_rows=true` when visible
- `synthetic_only_checked=true` when visible
- `no_oracle_checked=true` when visible
- `test_tuning_checked=true` when visible
- no private paths are included in docs
- no raw logs are included in docs
- no frozen policy artifact body is included in docs
- no JSONL body is included in docs
- no logits/probability dump is included in docs
- no performance metric body or performance claim is included in docs
- artifacts are absent or not recorded

Intentional invalid fixture reason codes may be mentioned only as safe reason
codes. Their fixture bodies must not be copied.

## 11. Interpretation

Remote Release Quality success means:

- the release-quality wrapper completed in GitHub Actions
- frozen policy validation was included if the label is visible
- frozen policy fixture expected-result matching passed if the count summary is
  visible
- the recorded metadata passed public-safety review

Remote Release Quality success does not mean:

- model performance is good
- calibration quality is validated
- selective prediction is correct
- learner-state estimator behavior is validated
- ECE, AURCC, F1, or accuracy was measured
- real-data readiness is established
- production readiness is established

## 12. Failure Handling

If the remote/manual run fails:

- record failure status only if it can be done public-safely
- do not paste raw logs
- do not paste full job output
- summarize only the safe failure category
- do not include private paths
- do not include stack traces with row or artifact bodies
- fix the issue in a separate branch
- rerun the workflow after the fix
- update or replace the status marker only with safe metadata

Safe failure categories may include:

- `environment_failure`
- `dependency_failure`
- `release_quality_wrapper_failure`
- `frozen_policy_validation_failure`
- `frozen_policy_expected_result_mismatch`
- `unsafe_output_exposure`
- `unrelated_check_failure`
- `unknown_safe_summary_only`

A frozen policy validation failure is an artifact-contract or safety-boundary
failure. It is not a model performance failure.

## 13. Workflow For Actually Recording Later

Future recording steps:

1. Merge the Step230 wrapper integration to `main`.
2. Trigger the existing Release Quality workflow manually or through the
   existing workflow trigger.
3. Inspect the GitHub Actions log in the GitHub UI.
4. Extract only safe metadata and count-only summaries.
5. Create the future status marker under `docs/status/`.
6. Link it from `docs/status/README.md` and `docs/README.md`.
7. Run local documentation and release-quality checks.
8. Commit only the status marker and safe docs links.

Do not store raw logs, screenshots containing raw logs, generated output
bodies, fixture bodies, or policy artifact bodies in the repository.

## 14. Relation To Public Release Checklist

The future status marker improves traceability for the release-quality wrapper
after frozen policy validation is included.

It is not a formal public release. It is one safety signal among others:

- wrapper inclusion is visible
- expected fixture matching is visible
- public log safety review is documented

License/reuse policy, real-data readiness, and production readiness remain
separate review areas.

## 15. What This Does Not Do

This document does not:

- run the remote workflow
- create a status marker
- change GitHub Actions workflows
- change the release-quality wrapper
- change the Makefile
- change Python code, tests, or fixtures
- implement calibration
- implement selective prediction
- generate frozen policy artifacts
- train a learner-state estimator
- compute F1, accuracy, calibration, ECE, or AURCC
- use real data
- prove performance

## 16. Beginner Notes

A remote/manual run is a GitHub Actions run started outside the local machine,
usually from the GitHub UI. It checks that the same release-quality wrapper can
run in the repository automation environment.

A status marker is a short public-safe record that says what was checked and
what high-level result was observed. It should be easy to link from recaps and
checklists.

Raw logs are not pasted because logs can accidentally contain file paths,
generated bodies, stack traces, or other details that should not become public
documentation.

Count-only summaries are safer because they record whether fixture contracts
matched without exposing fixture bodies or generated data.

Success is not a performance evaluation. It means the wrapper and fixture
contract checks passed, not that a model is accurate or production-ready.
