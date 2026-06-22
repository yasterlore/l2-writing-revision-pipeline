# Frozen Policy Validator Makefile Target Design

## 1. Purpose

This document designs a future Makefile target for the frozen selective
prediction policy validator CLI. The target should make the safe fixture-root
validation command easy to run locally without exposing frozen policy bodies,
raw rows, logits dumps, private paths, or metric bodies.

Step228 implements the target described here as
`make check-learner-state-frozen-policy`.

This design and implementation do not change release-quality, change
workflows, implement calibration, implement selective prediction, compute
metrics, or claim real-data readiness.

## 2. Current State

Current assets:

- frozen policy validator Python API exists in
  `python/learner_state/frozen_policy_validation.py`
- frozen policy validator CLI exists at
  `PYTHONPATH=python python3 -m learner_state.frozen_policy_validation`
- frozen policy fixture root exists at
  `tests/fixtures/learner_state_frozen_selective_prediction_policy/`
- fixture-root validation currently gives 12 matched cases:
  `total_cases=12`, `matched_cases=12`, `mismatched_cases=0`, and
  `input_error_cases=0`
- Makefile target exists as `check-learner-state-frozen-policy`
- release-quality integration does not exist yet

The current CLI output is a safe summary only. It does not print policy
artifact bodies, raw rows, logits dumps, private path values, or performance
metrics.

## 3. Proposed Target Name

Candidate names:

- `check-learner-state-frozen-policy`
- `check-frozen-policy`
- `check-frozen-selective-prediction-policy`
- `check-learner-state-frozen-selective-prediction-policy`
- `check-selective-prediction-frozen-policy`

Recommended target:

```make
check-learner-state-frozen-policy
```

Rationale:

- it follows the existing learner-state target namespace
- it is shorter than `check-learner-state-frozen-selective-prediction-policy`
- it is clearer than the broad `check-frozen-policy`
- it sits naturally beside `check-learner-state-estimator-input`,
  `check-learner-state-exporter-cli`, and
  `check-learner-state-selective-prediction`
- the help text can carry the longer phrase "frozen selective prediction
  policy validation" without making the command unwieldy

`check-frozen-selective-prediction-policy` is descriptive, but it does not
show that this belongs to the learner-state validation family. The
learner-state prefix is useful for release-quality grouping and local
discoverability.

## 4. Proposed Command

Recommended command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_validation \
  --fixture-root tests/fixtures/learner_state_frozen_selective_prediction_policy
```

The initial target should use human summary output rather than `--json`.

Human summary output is preferred because:

- it is developer-readable in local terminal output
- it is already count/reason-code only
- it reports the expected 12 matched cases compactly
- it does not print policy bodies, raw rows, logits dumps, or private paths
- Makefile targets are usually read by humans first, while JSON remains
  available for future machine consumers

JSON output should remain available through the CLI, but the first Makefile
target does not need it.

## 5. Help Text

Suggested `make help` line:

```text
check-learner-state-frozen-policy  Smoke-test frozen selective prediction policy validation
```

This wording is short enough for the existing help table and explicit enough
to distinguish this target from the selective prediction calibration fixture
validator.

## 6. Expected Behavior

The future target should:

- discover 12 fixture cases deterministically
- include one valid fixture and eleven intentional invalid fixtures
- load each `expected_frozen_policy_validation_result.json`
- compare observed safe validation result metadata to expected metadata
- pass when all cases match expected results
- fail on expected-result mismatch
- fail on usage error, missing files, malformed JSON, or unsafe paths
- emit safe human summary only

Expected successful summary shape:

- `mode=fixture_root`
- `total_cases=12`
- `matched_cases=12`
- `mismatched_cases=0`
- `input_error_cases=0`
- `reason_code_counts=...`
- `content_suppressed=true`
- `no_raw_rows=true`

The target should not claim that calibration quality, selective prediction
quality, or model performance has been measured.

## 7. Exit Code Behavior

Makefile should rely on the CLI exit code directly:

- CLI exit `0` means the Make target passes
- CLI exit `2` means the Make target fails because of usage, missing input,
  malformed input, unsafe path, or other input error
- CLI exit `3` means the Make target fails because expected-result matching
  failed
- CLI exit `1` is reserved for a future raw validation-only mode and is not
  normally expected in this fixture-root target

The Makefile target should not translate or mask these exit codes. Fail-fast
behavior from Make is sufficient.

## 8. Output / Logging Policy

The target output must not include:

- full frozen policy body
- raw rows
- logits dump
- probability dump
- label body
- split body
- calibration policy body
- private paths
- metric body
- performance metrics
- raw learner text

Allowed output:

- safe human summary
- fixture-root case counts
- safe reason-code counts
- safety flags such as `content_suppressed=true` and `no_raw_rows=true`

No artifacts should be generated by this target.

## 9. Tmp / Output Policy

The future target should:

- read only the frozen policy fixture root
- not create `tmp/` output
- not write validation result files
- not use `manual_outputs/`
- not require cleanup
- not upload or persist artifacts

If a future machine-readable output file is needed, that should be a separate
design because it would change the target from smoke validation into artifact
generation.

## 10. Relation To Existing Makefile Targets

`check-learner-state-selective-prediction` validates the prediction, label,
split metadata, and calibration policy fixture contract before any future
calibration or selective prediction implementation consumes those inputs.

`check-learner-state-frozen-policy` would validate the frozen policy artifact
contract after validation-only policy selection. It is the output-side
counterpart to the selective prediction fixture validator.

`check-learner-state-estimator-input` validates exported feature/label/manifest
inputs for a future learner-state estimator.

`check-learner-state-exporter-cli` runs exporter smoke checks that create
temporary synthetic output under `tmp/`.

The frozen policy target should fit near the learner-state checks, likely
after `check-learner-state-selective-prediction`, because it checks a later
contract in the same validation-only calibration path. It is not part of
`check-release-quality` yet.

## 11. Release-Quality Future

This step does not connect release-quality. Step228 adds only the standalone
Makefile target and leaves `scripts/check_release_quality.sh` unchanged.

After Makefile target implementation and a log-safety review, a future
release-quality integration design should decide where to place the target.
The likely placement is near the learner-state checks:

1. learner-state audit fixtures
2. learner-state exporter CLI smoke
3. learner-state estimator input validation
4. learner-state selective prediction calibration validation
5. learner-state frozen policy validation
6. config/scoring smoke checks

Do not connect it in the Makefile target implementation step. The wrapper
should only be changed after the standalone target has proven safe output.

## 12. Testing Plan For Future Implementation

Future target implementation should verify:

- `make help` includes `check-learner-state-frozen-policy`
- `make check-learner-state-frozen-policy` exits `0`
- CLI fixture-root output reports `total_cases=12`
- CLI fixture-root output reports `matched_cases=12`
- stdout contains safe summary fields only
- no full policy body appears in output
- no raw rows appear in output
- no logits or probability dump appears in output
- no private path value appears in output
- no tmp output is created by the target
- Makefile diff is limited to `.PHONY`, help text, and target command
- release-quality wrapper and workflows are not modified in the target
  implementation step
- Python tests still pass

## 13. No-Oracle / Synthetic-Only Boundary

The fixture root is synthetic-only. Intentional invalid fixtures are safety
tests and may contain deliberate forbidden markers, but the target output
should only report safe reason codes.

The frozen policy is a metadata artifact contract only. The target must not:

- use real participant data
- print raw rows
- print logits dumps
- print private paths
- use expected action as scoring feedback
- fit calibration
- compute metrics
- evaluate model performance
- claim real-data readiness

## 14. What This Does NOT Do

This design does not:

- implement the Makefile target
- integrate release-quality
- change workflows
- implement calibration
- implement selective prediction
- generate frozen policy artifacts
- train an estimator
- evaluate a model
- compute F1, accuracy, ECE, or AURCC
- use real data
- prove performance

## 15. Beginner Notes

A Makefile target is a short command, such as `make check-python`, that wraps
a longer command in a memorable project-standard name.

The CLI already works, but a Makefile target makes it easier for contributors
to run the same safe check without remembering the full `PYTHONPATH=python`
module command.

This target should not create `tmp/` output because it only validates existing
synthetic fixture files. It reads the fixture root and prints a safe summary.

Release-quality should not include the target immediately because wrapper
integration should happen only after the standalone target's output is
reviewed for log safety.

Success means the synthetic fixture contract and expected-result matching are
working. It does not mean model performance is good, calibration quality is
validated, or real-data readiness has been established.

## 16. Related Documents

- [Frozen policy validator CLI design](frozen_policy_validator_cli_design.md)
- [Frozen selective prediction policy validation design](frozen_selective_prediction_policy_validation_design.md)
- [Frozen selective prediction policy fixture design](frozen_selective_prediction_policy_fixture_design.md)
- [Frozen selective prediction policy schema design](frozen_selective_prediction_policy_schema_design.md)
- [Frozen selective prediction policy fixtures](../tests/fixtures/learner_state_frozen_selective_prediction_policy/README.md)
- [Selective prediction and calibration validator Makefile target design](selective_prediction_calibration_validator_makefile_target_design.md)
- [Public release checklist](public_release_checklist.md)
