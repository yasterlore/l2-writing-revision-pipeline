# Selective Prediction Calibration Release-Quality Integration Design

This document designs release-quality wrapper integration for the synthetic
selective prediction calibration validator Makefile target and records the
Step215 implementation status.

The Step214 version was docs-only. Step215 adds the wrapper call only through
the existing Makefile target. It does not change workflows, Makefile, code,
tests, fixtures, or scripts other than `scripts/check_release_quality.sh`. It
does not implement calibration, selective prediction, estimator training,
metric computation, or real-data handling. It is not a performance evaluation
and is not a real-data readiness claim.

## 1. Purpose

The purpose of this document is to define how the standalone target
`make check-learner-state-selective-prediction` should be integrated into
`scripts/check_release_quality.sh`.

The design covers:

- wrapper insertion point
- wrapper command
- release-quality label
- success and failure meaning
- output/logging safety
- runtime and CI impact
- remote/manual run record policy

The design must preserve the current safety boundary:

- synthetic-only fixtures
- safe count/reason-code output only
- no raw rows
- no prediction rows
- no label rows
- no split metadata body
- no calibration policy body
- no logits or probability dump
- no expected action body
- no private paths
- no model performance claims

## 2. Current State

Current assets:

- Python API exists in
  `python/learner_state/selective_prediction_validation.py`
- CLI exists through
  `PYTHONPATH=python python3 -m learner_state.selective_prediction_validation`
- Makefile target exists:
  `make check-learner-state-selective-prediction`
- fixture root exists:
  `tests/fixtures/learner_state_selective_prediction/`
- standalone target passes with:
  - `total_cases=8`
  - `matched_cases=8`
  - `mismatched_cases=0`
  - `input_error_cases=0`
- target output is safe human summary only
- target creates no tmp output

Step215 implementation status:

- release-quality wrapper integration is present
- wrapper calls `make check-learner-state-selective-prediction`
- placement is after learner-state estimator input validation and before
  config/scoring smoke checks
- output remains the target's safe human summary
- workflow integration is not present
- remote/manual run record for this target inside release-quality is not
  present yet

Not present yet:

- workflow integration
- remote/manual run record for this target inside release-quality

## 3. Proposed Wrapper Insertion Point

Recommended insertion order:

1. learner-state audit fixtures
2. learner-state exporter CLI smoke
3. learner-state estimator input validation
4. learner-state selective prediction calibration validation
5. config and scoring smoke checks

Recommended placement in `scripts/check_release_quality.sh`:

- after `make check-learner-state-estimator-input`
- before `section "config and scoring smoke checks"`

Rationale:

- audit fixtures check the learner-state sequence audit boundary
- exporter CLI smoke checks synthetic exporter behavior and audited outputs
- estimator input validation checks exported-shape feature/label/manifest
  safety
- selective prediction calibration validation checks prediction/confidence,
  label separation, split metadata, and no-test-tuning fixture contracts
- config/scoring smoke checks are a separate downstream command family

This preserves a natural learner-state progression before returning to the
general config/scoring checks.

Alternative placements:

- after exporter CLI smoke: acceptable, but estimator input validation is a
  closer prerequisite for later prediction/confidence fixtures
- near config/scoring smoke checks: less clear, because the target is a
  learner-state validation boundary rather than a scoring smoke
- before audit fixtures: not recommended because it would run later-stage
  fixture checks before upstream learner-state boundaries

## 4. Proposed Wrapper Command

Recommended command:

```bash
make check-learner-state-selective-prediction
```

The wrapper should call the Makefile target rather than the Python module
directly.

Reasons:

- local command and wrapper command stay consistent
- CLI command shape remains centralized in Makefile
- future path or flag changes can be made in one place
- wrapper stays readable
- safe output policy is documented at the target boundary
- long Python invocation is not duplicated

## 5. Release-Quality Check Label

Recommended wrapper section label:

```text
release_quality_check: learner-state selective prediction calibration validation
```

Recommended wrapper stanza:

```sh
section "learner-state selective prediction calibration validation"
run make check-learner-state-selective-prediction
```

The label should not imply metric computation, calibration quality, model
training, or performance evaluation.

Step215 implements this stanza in `scripts/check_release_quality.sh` without
changing the Makefile, workflows, code, tests, or fixtures.

## 6. Expected Wrapper Behavior

Expected behavior:

- target exit `0`: wrapper continues
- target nonzero: wrapper fails through normal `set -e` behavior
- no retry
- no special exit-code conversion
- no tmp output
- no cleanup required
- no artifacts
- safe human summary only
- no performance metrics

Successful output should include the target safe summary:

- `total_cases=8`
- `matched_cases=8`
- `mismatched_cases=0`
- `input_error_cases=0`
- `content_suppressed=true`
- `no_raw_rows=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `test_tuning_checked=true`

These fields are fixture-contract smoke results, not model evaluation
metrics.

## 7. Output / Logging Safety

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

Forbidden in release-quality logs:

- raw rows
- prediction rows
- label rows
- split metadata body
- calibration policy body
- logits dump
- probability dump
- expected action body
- raw learner text
- private absolute paths
- real data paths
- performance claims
- F1 / accuracy / ECE / AURCC values

The wrapper should not use `--json` initially. Human summary is easier to
review and already suppresses row, policy, split, and logits bodies.

## 8. Runtime / CI Impact

Runtime expectations:

- fixture root has 8 cases
- validator is Python-only
- no Node dependency
- no Rust dependency
- no network access
- no tmp output
- no artifact generation
- expected runtime impact is small because fixture count is small

The exact local or remote runtime should be recorded after a future run rather
than guessed in this design document.

The target should run after Python is already available in release-quality.
The current wrapper already runs Python checks before learner-state fixture
checks, so this target fits naturally in the existing environment.

## 9. Failure Interpretation

Target failure can mean:

- fixture contract mismatch
- expected-result mismatch
- test tuning leakage detected
- label leakage detected
- future label/action leakage detected
- split leakage detected
- missing fixture file
- malformed JSON / JSONL
- unsafe input path

Target failure does not mean:

- model performance failure
- calibration quality failure
- learner-state estimator quality failure
- real-data readiness failure
- production data collection failure
- F1 failure
- accuracy failure
- ECE failure
- AURCC failure

Failure output should remain safe and count/reason-code oriented. Raw rows,
policy bodies, split bodies, logits/probability bodies, and expected action
bodies should not be printed.

## 10. Relation to Existing Release-Quality Checks

Existing learner-state release-quality checks:

- learner-state audit fixture check
- learner-state exporter CLI smoke
- learner-state estimator input validation

The proposed target extends that learner-state chain by checking a future
calibration/selective-prediction fixture boundary after estimator inputs are
validated.

Relation to other release-quality checks:

- config/scoring smoke checks remain separate and later in the wrapper
- no-config fixture lock checks scoring fixture stability
- hand-weight config validation checks explicit config safety
- explicit config ranking diff checks expected config/no-config behavior

The selective prediction calibration target does not modify or evaluate
candidate generation, OT scoring, scoring formulas, tie-breaks, or hand-weight
config behavior.

## 11. Future Implementation Plan

Recommended next steps:

1. Step215: release-quality wrapper integration implementation.
2. Step216: remote/manual Release Quality run record workflow design.
3. Step217: remote/manual run status marker.
4. Step218: milestone recap or selective prediction / calibration scaffold
   design.

Keep wrapper integration separate from any calibration, selective prediction,
estimator, or metric implementation.

## 12. Remote / Manual Run Record Policy

After wrapper integration, a manual or remote Release Quality run may be
recorded with public-safe metadata only.

Step216 follow-up: the remote/manual Release Quality run recording workflow
for the selective prediction calibration validation section is defined in
[Selective prediction release-quality remote run record workflow](selective_prediction_release_quality_remote_run_record_workflow.md).

Step217 follow-up: the successful public-safe remote/manual run status marker
is available at
[Learner-state selective prediction release-quality remote run status](status/learner_state_selective_prediction_release_quality_remote_run_status.md).

Allowed record fields:

- workflow name
- job name
- branch
- commit short hash
- status
- target included: yes/no
- selective prediction calibration validation summary:
  - pass/fail
  - `total_cases`
  - `matched_cases`
  - `mismatched_cases`
  - `input_error_cases`
- log safety review result
- duration only if GitHub UI confirms it
- artifact presence only if GitHub UI confirms it

Forbidden in public records:

- raw GitHub Actions logs
- full job output
- raw rows
- prediction row bodies
- label row bodies
- split metadata body
- calibration policy body
- logits/probability bodies
- expected action body
- private paths
- performance metrics
- real participant data

If unsafe output appears in a remote run, do not create a public status marker
with that output. Record only a private/local remediation note if needed.

## 13. What This Does NOT Do

This document and Step215 implementation do not:

- change workflows
- change Makefile
- change scripts other than the minimal release-quality wrapper stanza
- implement calibration
- implement selective prediction
- train an estimator
- compute metrics
- compute F1
- compute accuracy
- compute ECE
- compute AURCC
- use real data
- prove performance
- claim real-data readiness

## 14. Beginner Notes

The release-quality wrapper is the script that runs the normal bundle of
checks before treating the repository as healthy for release-quality review.

The standalone Makefile target proves that the validator command works by
itself. Wrapper integration makes that same check part of the larger
release-quality bundle.

Designing the wrapper step first helps decide where the command belongs, what
it should print, how failures should be interpreted, and how to avoid unsafe
logs.

Success is not performance evaluation. It only means the synthetic fixture
validation target ran inside the release-quality command path and matched its
expected fixture results.

## 15. Related Documents

- [Selective prediction and calibration design](selective_prediction_calibration_design.md)
- [Selective prediction and calibration fixture design](selective_prediction_calibration_fixture_design.md)
- [Selective prediction and calibration validation design](selective_prediction_calibration_validation_design.md)
- [Selective prediction calibration validator CLI design](selective_prediction_calibration_validator_cli_design.md)
- [Selective prediction calibration validator Makefile target design](selective_prediction_calibration_validator_makefile_target_design.md)
- [Selective prediction release-quality remote run record workflow](selective_prediction_release_quality_remote_run_record_workflow.md)
- [Learner-state selective prediction release-quality remote run status](status/learner_state_selective_prediction_release_quality_remote_run_status.md)
- [Learner-state estimator input release-quality integration design](learner_state_estimator_input_release_quality_integration_design.md)
- [Public release checklist](public_release_checklist.md)
