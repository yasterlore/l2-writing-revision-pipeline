# Frozen Policy Generation Validator Makefile Target Design

This document designs and records the Step242 implementation status for the
Makefile target that runs the frozen policy generation validator CLI.

It is primarily a design record. Step242 implements only the standalone
Makefile target. It does not implement a generator, frozen policy generation
scaffold, release-quality integration, GitHub Actions workflow change, Python
code change, test change, fixture change, calibration, selective prediction,
learner-state estimator, estimator training, new model, or metric computation.
It is not a performance evaluation and is not a real-data readiness claim.

Public docs must not include raw GitHub Actions logs, full job output, copied
log blocks, screenshots containing raw logs, frozen policy artifact bodies,
JSON bodies, request bodies, generated artifact bodies, raw rows,
logits/probability dumps, label bodies, split bodies, calibration policy
bodies, generated feature/label/manifest bodies, private paths, raw learner
text, or real participant data.

## 1. Purpose

The purpose of this document is to design and record the safe standalone
Makefile target for the Step240 frozen policy generation validator CLI.

The target should let developers run fixture-root validation with a short
command, while preserving the same safe output policy as the CLI. It should
not create artifacts, write validation result files, run a generator, compute
calibration, compute metrics, or claim model performance.

## 2. Current State

Current state:

- generation fixture root exists:
  `tests/fixtures/learner_state_frozen_policy_generation/`
- generation validator Python API exists in
  `python/learner_state/frozen_policy_generation_validation.py`
- generation validator CLI exists as:
  `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_validation`
- fixture-root validation reports `total_cases=13`, `matched_cases=13`,
  `mismatched_cases=0`, and `input_error_cases=0`
- output is safe summary only
- no request body, generated artifact body, raw rows, logits dump, or private
  path is printed
- Makefile target exists as `make check-learner-state-frozen-policy-generation`
- release-quality integration does not exist yet

## 3. Proposed Target Name

Candidate target names:

| Target | Assessment |
| --- | --- |
| `check-learner-state-frozen-policy-generation` | Recommended. It pairs with `check-learner-state-frozen-policy`, stays in the learner-state target family, and names the generation fixture validation boundary clearly. |
| `check-frozen-policy-generation` | Shorter, but loses the learner-state grouping used by nearby targets. |
| `check-learner-state-frozen-policy-generation-fixtures` | Precise, but long enough to be awkward for routine use. |
| `check-frozen-policy-generation-fixtures` | Clear that fixtures are involved, but less aligned with existing learner-state target names. |
| `check-learner-state-generation-policy` | Ambiguous; it could be read as generation policy rather than frozen policy generation validation. |

Implemented target:

```text
check-learner-state-frozen-policy-generation
```

Rationale:

- pairs with `check-learner-state-frozen-policy`
- matches the `check-learner-state-*` target family
- makes the generation fixture validation scope visible
- avoids implying model generation or production generation

## 4. Proposed Command

Implemented command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_validation \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation
```

Human summary output is recommended for the initial Makefile target rather
than `--json`.

Human summary rationale:

- developer-readable in local runs
- already safe and count-only
- includes reason-code counts without request or artifact bodies
- matches the style of nearby learner-state smoke targets

JSON output should remain available for direct CLI use and future automation,
but the first Makefile target does not need it.

## 5. Help Text

Implemented `make help` text:

```text
check-learner-state-frozen-policy-generation  Smoke-test frozen policy generation fixture validation
```

The wording intentionally says fixture validation, not generator validation,
to avoid implying that a generator exists.

## 6. Expected Behavior

Expected target behavior:

- discover the fixture-root cases deterministically
- include all valid and intentional invalid generation fixture cases
- load each `expected_generation_result.json`
- compare validation results to expected results
- pass when all thirteen cases match
- fail on usage errors, missing files, malformed input, unsafe paths, input
  errors, or expected-result mismatches
- emit safe human summary only
- avoid request body, input pointer body, generated artifact body, raw rows,
  logits/probability dumps, private paths, and performance metrics
- create no artifacts

Expected successful summary:

- `mode=fixture_root`
- `total_cases=13`
- `matched_cases=13`
- `mismatched_cases=0`
- `input_error_cases=0`
- safe reason-code counts
- safety flags such as `content_suppressed=true` and `no_raw_rows=true`

## 7. Exit Code Behavior

The Makefile target should not remap CLI exit codes.

Expected behavior:

- CLI exit `0` means the Makefile target passes.
- CLI exit `2` means usage, missing input, malformed input, unsafe path, or
  input error; the Makefile target fails.
- CLI exit `3` means expected-result mismatch; the Makefile target fails.
- CLI exit `1` is reserved for a future raw validation-only mode and is not
  normally expected in the current fixture expected-result mode.

Keeping the CLI exit code unchanged makes failures easier to diagnose and
keeps the Makefile target thin.

## 8. Output / Logging Policy

Allowed output:

- target name
- CLI command line
- mode
- total cases
- matched cases
- mismatched cases
- input error cases
- reason-code counts
- safety flags

Forbidden output:

- request body
- input pointer body
- generated frozen policy body
- frozen policy artifact body
- raw rows
- logits/probability dump
- label body
- split body
- calibration policy body
- private paths
- raw learner text
- performance metrics
- full job output pasted into docs
- raw GitHub Actions logs pasted into docs

The target should be safe for local terminal output and future CI logs, but
release-quality integration still needs its own review before connection.

## 9. tmp / Output Policy

The target should:

- read the synthetic fixture root only
- create no `tmp/` output
- create no `manual_outputs/` output
- write no validation result files
- require no cleanup
- avoid artifact generation

If a future implementation needs saved validation summaries, that should be a
separate design step with explicit log and artifact safety review.

## 10. Relation To Existing Makefile Targets

Related targets:

- `check-learner-state-frozen-policy` validates frozen selective prediction
  policy artifacts as output contracts.
- `check-learner-state-selective-prediction` validates selective prediction
  calibration fixture inputs and split/tuning safety.
- `check-learner-state-estimator-input` validates estimator input feature and
  label contracts.
- `check-learner-state-frozen-policy-generation` would validate the bridge
  fixtures that connect selective prediction input validation to frozen policy
  output validation.

The proposed target fits near the learner-state checks, but it should not be
added to `check-release-quality` in this step.

## 11. Release-Quality Future

Release-quality integration is not part of this step.

Recommended future sequence:

1. Confirm the standalone target stays stable.
2. Review stdout/stderr for body and path safety.
3. Design release-quality integration.
4. Add the wrapper call only after the standalone target is stable.

Likely future placement is near the learner-state checks, after frozen policy
validation and before config/scoring smoke checks. Do not connect it now.

## 12. Testing Plan For Standalone Implementation

Standalone implementation checks:

- `make help` includes `check-learner-state-frozen-policy-generation`
- `make check-learner-state-frozen-policy-generation` exits `0`
- CLI fixture-root output reports `total_cases=13`
- CLI fixture-root output reports `matched_cases=13`
- stdout and stderr are safe
- no `tmp/` output is created
- no `manual_outputs/` output is created
- Makefile diff is limited to `.PHONY`, help, and target body
- release-quality wrapper is not modified
- workflow YAML is not modified
- Python tests still pass

## 13. No-Oracle / Synthetic-Only Boundary

Boundary:

- generation fixture root is synthetic-only
- intentional invalid fixtures are safety tests
- no request body output
- no input pointer body output
- no generated artifact body
- no raw rows
- no logits dump
- no private paths
- no expected action as scoring feedback
- no calibration fitting
- no metric computation
- no model performance evidence
- no real data

Passing the target means only that fixture expected-result matching passed.

## 14. What This Does NOT Do

This step does not:

- integrate release-quality
- modify GitHub Actions workflows
- implement generator code
- implement frozen policy generation scaffold code
- implement calibration
- implement selective prediction
- train an estimator
- evaluate a model
- compute metrics
- use real data
- prove performance

## 15. Beginner Notes

A Makefile target is a short command name that runs a longer command. It lets
developers type one stable command instead of remembering the full Python CLI.

The CLI remains useful because it is the real validation entrypoint. The
Makefile target is a convenient wrapper around that CLI.

This target should not create `tmp/` output because it only checks metadata
fixtures. It reads fixture files and prints a safe summary.

It should not be added to release-quality immediately because CI logs need a
separate safety review. Local standalone behavior should be stable first.

Success is not performance evidence. It means only that the synthetic fixture
contract and expected-result matching behaved as designed.

## 16. Update History

- Step241: initial frozen policy generation validator Makefile target design
  creation.
- Step242: implemented `make check-learner-state-frozen-policy-generation`
  as a standalone smoke target. Release-quality wrapper and workflows remain
  unchanged.

## Related Documents

- [Frozen policy generation validator CLI design](frozen_policy_generation_validator_cli_design.md)
- [Frozen policy generation validation design](frozen_policy_generation_validation_design.md)
- [Frozen policy generation fixture design](frozen_policy_generation_fixture_design.md)
- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Frozen policy generation fixtures](../tests/fixtures/learner_state_frozen_policy_generation/README.md)
- `python/learner_state/frozen_policy_generation_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_validation_cli.py`
- [Public release checklist](public_release_checklist.md)
