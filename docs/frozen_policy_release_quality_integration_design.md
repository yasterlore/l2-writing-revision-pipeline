# Frozen Policy Release-Quality Integration Design

This document designs future release-quality wrapper integration for the
synthetic frozen policy validator Makefile target.

It is documentation only. It does not change the release-quality wrapper,
GitHub Actions workflows, Makefile, shell scripts, validator code, fixtures,
calibration code, selective prediction code, learner-state estimator code,
training code, model code, metric computation, candidate generation, OT
scoring, scoring formula, tie-break logic, or manifest schemas. It is not a
performance evaluation and is not a real-data readiness claim.

## 1. Purpose

The purpose of this document is to define how
`make check-learner-state-frozen-policy` should be integrated into
`make check-release-quality` in a future implementation step.

The design covers:

- wrapper insertion point
- wrapper command
- release-quality label
- expected wrapper behavior
- log safety review
- failure interpretation
- remote/manual run record policy
- relation to existing release-quality checks
- testing plan for future implementation

The integration must preserve the current safety boundary:

- synthetic-only fixtures
- safe count/reason-code output only
- no frozen policy body
- no raw rows
- no logits or probability dump
- no private paths
- no raw learner text
- no performance metrics or claims

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
- release-quality integration does not exist yet
- GitHub Actions workflow change does not exist yet

The target is an artifact-contract smoke check. It does not fit calibration,
make selective prediction decisions, train a learner-state estimator, compute
metrics, or handle real data.

## 3. Proposed Wrapper Insertion Point

Recommended insertion order inside the learner-state release-quality checks:

1. learner-state audit fixtures
2. learner-state exporter CLI smoke
3. learner-state estimator input validation
4. learner-state selective prediction calibration validation
5. learner-state frozen policy validation
6. config and scoring smoke checks

Recommended placement in `scripts/check_release_quality.sh`:

- after `make check-learner-state-selective-prediction`
- before `section "config and scoring smoke checks"`

Rationale:

- audit fixtures check the learner-state sequence audit boundary
- exporter CLI smoke checks generated synthetic feature/label output shape
- estimator input validation checks exported-shape feature/label contracts
- selective prediction calibration validation checks prediction/label/split
  and no-test-tuning fixture contracts
- frozen policy validation checks the downstream frozen policy artifact
  contract that would be consumed after validation-only tuning
- config/scoring smoke checks are a separate downstream command family

This order keeps the learner-state checks in a readable progression from
upstream sequence safety toward downstream frozen policy artifact safety.

Alternative placements:

- after estimator input validation: acceptable, but frozen policy validation
  is more naturally downstream of selective prediction calibration validation
- after config/scoring smoke checks: not recommended, because frozen policy is
  a learner-state validation boundary rather than a scoring smoke check
- before selective prediction calibration validation: not recommended, because
  the frozen policy artifact is meant to depend on validated prediction,
  label, split, and policy inputs

## 4. Proposed Wrapper Command

Recommended command:

```bash
make check-learner-state-frozen-policy
```

The wrapper should call the Makefile target rather than the Python module
directly.

Reasons:

- the standalone Makefile target has already been reviewed for safe output
- developers and CI use the same command entrypoint
- the wrapper remains readable
- the long Python module invocation is not duplicated
- future fixture-root or flag changes can stay localized to the Makefile
- output policy is documented at the target boundary

The wrapper should not pass `--json` initially. Human summary is short,
developer-readable, and already suppresses policy bodies, rows, logits dumps,
and private paths.

## 5. Proposed Wrapper Label

Recommended wrapper section label:

```text
release_quality_check: learner-state frozen policy validation
```

Recommended wrapper stanza:

```sh
section "learner-state frozen policy validation"
run make check-learner-state-frozen-policy
```

The label should not mention performance, calibration quality, model quality,
or real-data readiness.

## 6. Expected Wrapper Behavior

Expected behavior after future integration:

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
- fixture-root safe summary
- total cases
- matched cases
- mismatched cases
- input error cases
- reason-code counts
- safety flags
- intentional invalid fixture reason codes

Forbidden in release-quality logs:

- full frozen policy body
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
- F1 / accuracy / ECE / AURCC claims
- full job output copied into docs
- raw GitHub Actions logs copied into docs

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

After future release-quality integration, a remote/manual run record should
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

## 10. Relation To Existing Release-Quality Checks

The learner-state release-quality progression should be:

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
- release-quality wrapper is not changed yet
- workflow is not changed

Future implementation should modify only `scripts/check_release_quality.sh` if
possible. The GitHub Actions release-quality workflow likely does not need a
direct YAML change because it already calls the wrapper. That assumption should
be verified during the implementation step.

## 12. Testing Plan For Future Implementation

Future implementation checks:

- `make check-learner-state-frozen-policy` passes
- `make check-release-quality` includes
  `release_quality_check: learner-state frozen policy validation`
- `make check-release-quality` passes
- wrapper output contains the safe 12-case matched summary
- wrapper output does not contain policy body, raw rows, logits dump, private
  paths, raw learner text, or performance metric bodies
- `git diff -- .github/workflows/release-quality.yml` has no diff unless a
  workflow change is explicitly required
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

This design does not:

- integrate the release-quality wrapper
- change workflows
- change Makefile
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

The standalone target comes first because it lets developers review the exact
command and log output in isolation. After that output is known to be safe, a
later step can add the same target to release-quality.

The wrapper should call the Makefile target instead of the Python command
directly because Makefile becomes the shared entrypoint for developers and CI.
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
