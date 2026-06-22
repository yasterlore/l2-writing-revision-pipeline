# Selective Prediction Calibration Validator Makefile Target Design

This document designs the Makefile target for running the synthetic selective
prediction calibration validator CLI and records the Step213 implementation
status.

The Step212 version was docs-only. Step213 adds only the Makefile target and
help text. It does not change release-quality, change workflows, implement
calibration, implement selective prediction, train an estimator, compute
metrics, use real data, or claim real-data readiness. It is not a performance
evaluation.

## 1. Purpose

The purpose of this document is to define a safe Makefile entrypoint for the
Step211 CLI:

```bash
PYTHONPATH=python python3 -m learner_state.selective_prediction_validation
```

The target should let developers run the fixture-root validation with a short
command while preserving CLI safety guarantees:

- synthetic-only fixture root
- expected-result matching by default
- safe human summary only
- no prediction row body
- no label body
- no split metadata body
- no calibration policy body
- no logits or probability dump
- no expected action body
- no private paths
- no performance metrics

## 2. Current State

Current assets:

- validator Python API exists in
  `python/learner_state/selective_prediction_validation.py`
- CLI exists through
  `PYTHONPATH=python python3 -m learner_state.selective_prediction_validation`
- fixture root exists at
  `tests/fixtures/learner_state_selective_prediction/`
- fixture-root validation currently reports 8 matched cases:
  - `total_cases=8`
  - `matched_cases=8`
  - `mismatched_cases=0`
  - `input_error_cases=0`
- output is safe summary only
- no raw rows, logits body, probability body, split body, or policy body are
  printed

Step213 implementation status:

- Makefile target exists.
- `make help` includes the target.
- standalone target passes with 8 matched fixture cases.
- target creates no tmp output.
- release-quality wrapper integration is not present yet.
- workflow integration is not present.

Not present yet:

- release-quality wrapper integration
- workflow integration

## 3. Proposed Target Name

Candidate names:

| Candidate | Pros | Cons |
| --- | --- | --- |
| `check-learner-state-selective-prediction` | Matches learner-state target family; concise enough for daily use | Does not spell out calibration in the target name |
| `check-selective-prediction` | Short | Too broad and less clearly tied to learner-state fixtures |
| `check-learner-state-calibration` | Shorter than the full phrase | Hides selective prediction and may sound like parameter fitting |
| `check-selective-prediction-calibration` | Names both concepts | Less aligned with existing learner-state target names |
| `check-learner-state-selective-prediction-calibration` | Fully explicit | Too long for a Makefile target and help output |

Recommended initial target:

```make
check-learner-state-selective-prediction
```

Rationale:

- It follows the learner-state target naming pattern.
- It is shorter than the fully explicit calibration variant.
- The help text can mention calibration validation.
- It leaves room for a future target that handles actual calibration
  computation, if such a target is ever designed separately.

## 4. Proposed Command

Recommended command:

```bash
PYTHONPATH=python python3 -m learner_state.selective_prediction_validation --fixture-root tests/fixtures/learner_state_selective_prediction
```

Human summary is recommended for the initial Makefile target instead of
`--json`.

Reasons:

- developer-readable in local terminals
- already safe count/reason-code output
- no row body
- no logits or probability body
- no split metadata body
- no calibration policy body
- no artifact parsing is needed for pass/fail

Safe JSON output remains useful for future scripts, but the first target
should keep logs readable and minimal.

## 5. Help Text

Suggested Makefile help text:

```text
check-learner-state-selective-prediction  Smoke-test selective prediction calibration validation
```

The text should avoid implying calibration fitting, metric computation, model
training, or performance evaluation.

## 6. Expected Behavior

The target should:

- read `tests/fixtures/learner_state_selective_prediction/`
- deterministically discover 8 fixture cases
- include the valid case and seven intentional invalid cases
- load each `expected_calibration_validation_result.json`
- compare actual validation result to expected result
- pass when all cases match
- fail on expected-result mismatch
- fail on usage or input errors
- print safe human summary only

Expected successful summary:

- `total_cases=8`
- `matched_cases=8`
- `mismatched_cases=0`
- `input_error_cases=0`

These counts are fixture-contract smoke results, not model performance
metrics.

## 7. Exit Code Behavior

Makefile should not transform CLI exit codes.

Recommended mapping:

- CLI exit `0`: Make target passes
- CLI exit `2`: Make target fails for usage, missing files, malformed input,
  unsafe path, or input error
- CLI exit `3`: Make target fails for expected-result mismatch
- CLI exit `1`: reserved for a future raw validation-only mode and not
  expected in the initial target

The Makefile target should rely on normal shell failure behavior.

## 8. Output / Logging Policy

Allowed output:

- mode
- total cases
- matched cases
- mismatched cases
- input error cases
- reason-code counts
- prediction row count
- label row count
- split counts
- policy status
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only_checked`
- `no_oracle_checked`
- `test_tuning_checked`

Forbidden output:

- raw rows
- prediction row body
- label body
- split metadata body
- calibration policy body
- logits dump
- probability dump
- expected action body
- raw learner text
- private absolute paths
- performance metrics
- generated output body

The target should not use `cat` on fixture files or generated outputs.

## 9. Tmp / Output Policy

The target should not create tmp outputs.

Policy:

- read fixture root only
- no artifact generation
- no cleanup needed
- do not use `manual_outputs`
- do not write validation result files unless a future design explicitly
  requires it
- do not upload or persist CLI output as an artifact

This differs from exporter CLI smoke checks, which intentionally write to
`tmp/` to exercise exporter behavior.

## 10. Relation to Existing Makefile Targets

Existing learner-state checks:

- `check-learner-state-audit-fixtures`: validates learner-state sequence
  audit fixture contracts
- `check-learner-state-exporter-cli`: smoke-tests synthetic sequence exporter
  CLI behavior and audited outputs
- `check-learner-state-estimator-input`: smoke-tests estimator input
  validation over exported-shape fixtures

Proposed position:

- after estimator input validation in the learner-state validation family
- before any future calibration/scaffold or estimator-prototype targets
- not part of `check-release-quality` yet

Conceptual order:

1. audit boundary
2. exporter boundary
3. estimator input boundary
4. selective prediction calibration fixture boundary

This target checks prediction/confidence fixture safety, not estimator
training or calibration quality.

## 11. Release-Quality Future

Release-quality integration is not part of this step.

Recommended future staging:

1. Implement the Makefile target.
2. Run it standalone and confirm safe logs.
3. Design release-quality integration.
4. If accepted, connect release-quality through the Makefile target, not by
   duplicating the long CLI command.

Likely future wrapper placement:

- after `make check-learner-state-estimator-input`
- before config/scoring smoke checks

The release-quality wrapper should not be changed during the target design
step.

Step213 implementation:

- adds `.PHONY: check-learner-state-selective-prediction`
- adds the Makefile help line
- adds the standalone target command
- does not add the target to `check-release-quality`
- does not change `check-all`
- does not change workflows or wrapper scripts

## 12. Testing Plan for Future Implementation

Implementation checks:

- `make help` includes the new target
- target exits `0`
- CLI fixture-root reports 8 matched cases
- stdout is safe
- stderr is safe
- no tmp output is created
- Makefile diff is limited to the new target and help text
- release-quality wrapper is not modified in the target implementation step
- workflows are not modified
- Python tests still pass

The implementation step should also verify that the target does not print row,
policy, split, logits, probability, or label bodies.

## 13. No-Oracle / Synthetic-Only Boundary

Boundaries:

- fixture root is synthetic-only
- intentional invalid fixtures are allowed only as safety tests
- expected action remains label-side only
- expected action leakage in prediction rows is allowed only in intentional
  invalid fixtures
- no scoring feedback
- no calibration fitting
- no threshold fitting
- no metric computation
- no model performance
- no real participant data
- no production data readiness claim

The target passing means the fixture validator command path matched expected
safe results. It does not mean calibration quality or model correctness.

## 14. What This Does NOT Do

This document and Step213 implementation do not:

- integrate release-quality
- change workflows
- implement calibration
- implement selective prediction
- train an estimator
- evaluate a model
- compute metrics
- compute F1
- compute accuracy
- compute ECE
- compute AURCC
- use real data
- claim real-data readiness

## 15. Beginner Notes

A Makefile target is a short named command. Instead of remembering a long
Python invocation, a developer can run a shorter `make ...` command.

The CLI is still the real validator interface. The Makefile target is a thin
shortcut that makes the correct safe command easier to remember and easier to
reuse later.

This target should not create `tmp/` output because validation only reads
fixture files and reports safe counts. It is not exporting data or producing
model artifacts.

It should not be added to release-quality immediately because wrapper logs
deserve a separate safety review. First the target should pass standalone.

Success is not performance evidence. It only confirms that synthetic fixture
validation and expected-result matching worked.

Step213 makes this shortcut available as
`make check-learner-state-selective-prediction`. It remains standalone until a
separate release-quality integration step is designed and implemented.

## 16. Related Documents

- [Selective prediction and calibration design](selective_prediction_calibration_design.md)
- [Selective prediction and calibration fixture design](selective_prediction_calibration_fixture_design.md)
- [Selective prediction and calibration validation design](selective_prediction_calibration_validation_design.md)
- [Selective prediction calibration validator CLI design](selective_prediction_calibration_validator_cli_design.md)
- [Initial selective prediction fixtures](../tests/fixtures/learner_state_selective_prediction/README.md)
- [Learner-state estimator input validator Makefile target design](learner_state_estimator_input_validator_makefile_target_design.md)
- [Public release checklist](public_release_checklist.md)
