# Frozen Policy Release-Quality Integration Design

This document records the release-quality wrapper integration design and
Step230 implementation status for the synthetic frozen policy validator
Makefile target.

Step230 adds `make check-learner-state-frozen-policy` to
`scripts/check_release_quality.sh` only. It does not change GitHub Actions
workflows, Makefile, Python code, tests, fixtures, calibration code,
selective prediction code, frozen policy generation scaffold, learner-state
estimator code, training code, metric computation, candidate generation, OT
scoring, scoring formula, tie-break logic, or manifest schemas. It is not a
performance evaluation and is not a real-data readiness claim.

## 1. Purpose

The purpose of this document is to define and record how
`make check-learner-state-frozen-policy` is integrated into the release-quality
wrapper.

The integration keeps the frozen policy validator inside the existing
synthetic-only learner-state check sequence and preserves safe count-only
logging. It does not expose frozen policy bodies, raw rows, logits dumps,
private paths, raw learner text, or performance metric bodies.

## 2. Current State

Current assets:

- Python API exists in
  `python/learner_state/frozen_policy_validation.py`
- CLI exists through
  `PYTHONPATH=python python3 -m learner_state.frozen_policy_validation`
- Makefile target exists:
  `make check-learner-state-frozen-policy`
- fixture root exists:
  `tests/fixtures/learner_state_frozen_selective_prediction_policy/`
- standalone target passes with:
  - `total_cases=12`
  - `matched_cases=12`
  - `mismatched_cases=0`
  - `input_error_cases=0`
- target output is safe human summary only
- target creates no tmp output
- Step230 release-quality wrapper integration is present
- workflow change is not present

The target is an artifact-contract smoke check. It does not fit calibration,
make selective prediction decisions, train a learner-state estimator, compute
metrics, or handle real data.

## 3. Wrapper Insertion Point

Step230 places the frozen policy check immediately after selective prediction
calibration validation and before config/scoring smoke checks.

The learner-state sequence in the wrapper is:

1. learner-state audit fixtures
2. learner-state exporter CLI smoke
3. learner-state estimator input validation
4. learner-state selective prediction calibration validation
5. learner-state frozen policy validation
6. config and scoring smoke checks

Rationale:

- audit fixtures check the learner-state sequence audit boundary
- exporter CLI smoke checks generated synthetic feature/label output shape
- estimator input validation checks exported-shape feature/label contracts
- selective prediction calibration validation checks prediction/label/split
  and no-test-tuning fixture contracts
- frozen policy validation checks the downstream frozen policy artifact
  contract that would be consumed after validation-only tuning
- config/scoring smoke checks are a separate downstream command family

## 4. Wrapper Command

Step230 wrapper command:

```bash
make check-learner-state-frozen-policy
```

The wrapper calls the Makefile target rather than the Python module directly.
This keeps the developer command and release-quality command aligned, avoids
duplicating the long Python invocation, and keeps future fixture-root or flag
changes localized to the Makefile.

The wrapper does not use `--json`. The human summary is short,
developer-readable, and already suppresses policy bodies, rows, logits dumps,
and private paths.

## 5. Wrapper Label

Step230 wrapper section label:

```text
release_quality_check: learner-state frozen policy validation
```

The label intentionally does not mention performance, calibration quality,
model quality, or real-data readiness.

## 6. Expected Wrapper Behavior

Expected behavior:

- target pass: release-quality continues
- target fail: release-quality fails through existing fail-fast behavior
- no retry
- no special exit-code conversion
- no tmp output
- no cleanup required
- no artifacts
- safe human summary only

Expected fixture-root summary:

- `total_cases=12`
- `matched_cases=12`
- `mismatched_cases=0`
- `input_error_cases=0`
- `content_suppressed=true`
- `no_raw_rows=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `test_tuning_checked=true`

These fields are fixture-contract smoke results, not model performance
metrics.

## 7. Log Safety Review

Allowed in release-quality logs:

- wrapper section label
- command line
- mode
- total cases
- matched cases
- mismatched cases
- input error cases
- reason-code counts
- safety flags
- `content_suppressed`
- `no_raw_rows`
- intentional invalid fixture reason codes

Forbidden in release-quality logs:

- full frozen policy artifact body
- raw prediction rows
- raw label rows
- logits dump
- probability dump
- label body
- split metadata body
- calibration policy body
- expected action body
- private absolute paths
- real data paths
- raw learner text
- performance metric body
- raw GitHub Actions logs copied into docs
- full job output copied into docs

Intentional invalid fixture reason codes may appear because they are part of
the safe summary. Intentional invalid fixture bodies must not appear. The
private-path fixture must report only a safe reason code and must not expose
the private path value.

## 8. Failure Interpretation

Release-quality failure can mean:

- schema mismatch
- expected-result mismatch
- unsafe path detected
- raw rows, logits dump, or performance marker detected
- intentional invalid fixture no longer fails as expected
- valid fixture no longer passes
- missing input file
- malformed JSON
- usage error
- input error

Release-quality failure does not mean:

- model performance failure
- calibration quality failure
- selective prediction quality failure
- learner-state estimator quality failure
- real-data readiness failure
- production data collection failure
- F1 / accuracy / ECE / AURCC failure

The target validates frozen policy artifact safety and expected fixture
contracts only.

## 9. Remote / Manual Run Record Future

After this wrapper integration, a future remote/manual run record should
capture high-level metadata only.

Safe metadata to record:

- workflow name
- repository
- branch
- commit short hash
- run status
- job status
- target included: yes/no
- `release_quality_check: learner-state frozen policy validation`
- `total_cases`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only_checked`
- `no_oracle_checked`
- `test_tuning_checked`
- log safety review result
- warning summary if any

Do not record:

- raw GitHub Actions logs
- full job output
- frozen policy artifact body
- JSON body from fixture files
- raw rows
- logits or probability dump
- private paths
- raw learner text
- performance metrics as claims
- F1 / accuracy / ECE / AURCC values

The remote/manual run record should follow the existing public-safe pattern
used by estimator input and selective prediction release-quality status
markers.

Step231 follow-up: the remote/manual run recording workflow is documented in
[Frozen policy release-quality remote run record workflow](frozen_policy_release_quality_remote_run_record_workflow.md).
It defines the future status marker path, allowed metadata, forbidden log/body
content, safety review, failure handling, and public checklist relationship.
It does not create the status marker or run the remote workflow.

## 10. Relation To Existing Release-Quality Checks

The learner-state release-quality progression is:

- learner-state audit: checks synthetic sequence audit fixture contracts and
  no-oracle boundaries
- learner-state exporter: checks the synthetic exporter CLI smoke path and
  audited generated output shape
- learner-state estimator input validation: checks exported-shape
  feature/label input contracts
- selective prediction calibration validation: checks prediction, label,
  split, confidence, and no-test-tuning fixture contracts
- frozen policy validation: checks frozen policy artifact metadata,
  validation-only provenance, forbidden fields, and safe output contract
- config/scoring smoke: checks broader synthetic scoring/config infrastructure

Frozen policy validation is downstream of selective prediction calibration
validation but still upstream of any future calibration scaffold, test
evaluation, or model performance reporting.

## 11. Makefile / Workflow Status

Current status:

- Makefile target already exists
- release-quality wrapper integration is present
- workflow is not changed

Step230 modifies only `scripts/check_release_quality.sh` plus documentation.
The GitHub Actions release-quality workflow does not need a direct YAML change
because it already calls the wrapper.

## 12. Testing Plan

Implementation checks:

- `make check-learner-state-frozen-policy` passes
- `make check-release-quality` includes
  `release_quality_check: learner-state frozen policy validation`
- `make check-release-quality` passes
- wrapper output contains the safe 12-case matched summary
- wrapper output does not contain policy body, raw rows, logits dump, private
  paths, raw learner text, or performance metric bodies
- `git diff -- .github/workflows/release-quality.yml` has no diff
- wrapper diff is limited to the new check stanza
- Python tests pass
- all existing release-quality checks pass
- `make check-summary-flow` and `make check-release-quality` are run
  separately, not in parallel

## 13. No-Oracle / Synthetic-Only Boundary

Boundary:

- fixture root is synthetic-only
- intentional invalid fixtures are safety tests only
- frozen policy validation is artifact contract validation
- invalid fixture reason codes are safe metadata
- full fixture bodies remain suppressed
- no real participant data is used
- no raw learner text is used
- no expected action is used as scoring feedback
- no test-derived tuning is accepted

This integration is not:

- calibration fitting
- selective prediction decision making
- learner-state estimator training
- metric computation
- model performance evidence
- real-data readiness evidence

## 14. What This Does NOT Do

This design and implementation do not:

- change workflows
- change Makefile
- change Python code
- change tests
- change fixtures
- implement calibration
- implement selective prediction
- generate frozen policy artifacts
- train a learner-state estimator
- compute metrics
- use real data
- prove model performance

## 15. Beginner Explanation

Release-quality is the project's local bundle of checks that should pass
before treating a change as release-ready for this synthetic-only pipeline.

The standalone target came first because it let developers review the exact
command and log output in isolation. After that output was known to be safe,
Step230 added the same target to release-quality.

The wrapper calls the Makefile target instead of the Python command directly
because Makefile is the shared entrypoint for developers and automation.
That avoids duplicating long command arguments in multiple places.

Log safety review matters because frozen policy fixtures intentionally include
invalid cases. The logs should show only reason codes and counts, never the
policy artifact body, raw rows, logits dumps, private paths, or raw learner
text.

Success means the synthetic fixture contract check ran and matched expected
safe results. It does not mean the model is good, calibration is good,
selective prediction works on real data, or any performance metric has been
measured.

## Related Documents

- [Frozen policy validator Makefile target design](frozen_policy_validator_makefile_target_design.md)
- [Frozen policy validator CLI design](frozen_policy_validator_cli_design.md)
- [Frozen selective prediction policy validation design](frozen_selective_prediction_policy_validation_design.md)
- [Frozen selective prediction policy fixtures](../tests/fixtures/learner_state_frozen_selective_prediction_policy/README.md)
- [Selective prediction calibration release-quality integration design](selective_prediction_calibration_release_quality_integration_design.md)
- [Frozen policy release-quality remote run record workflow](frozen_policy_release_quality_remote_run_record_workflow.md)
