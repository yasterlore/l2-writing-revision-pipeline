# Frozen Policy Generation Scaffold Fixture Validator Makefile Target Design

## 1. Purpose

This document designs a future Makefile target for running the frozen policy
generation scaffold fixture validator CLI.

This is a docs-only target design. It does not implement a Makefile target,
change the Makefile, integrate release-quality, change a workflow, implement
scaffold runtime code, implement a generator, compute metrics, evaluate
performance, or claim real-data readiness.

The target is intended to give developers a short, safe command for validating
the synthetic scaffold fixture contract before any scaffold runtime or
generator work is added.

## 2. Current State

The scaffold fixture root exists at:

- `tests/fixtures/learner_state_frozen_policy_generation_scaffold`

The validator API exists at:

- `python/learner_state/frozen_policy_generation_scaffold_fixture_validation.py`

The validator CLI exists and is run as:

- `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_scaffold_fixture_validation`

The CLI tests exist at:

- `python/learner_state/tests/test_frozen_policy_generation_scaffold_fixture_validation_cli.py`

The current scaffold fixture root contains:

- valid cases: 3
- invalid cases: 8
- total cases: 11
- required JSON files: 33

The current CLI root mode reports safe count-only matching:

- `total_cases=11`
- `matched_cases=11`
- `mismatched_cases=0`
- `input_error_cases=0`

At Step255 design time, the Makefile target did not exist yet.

As of Step258, release-quality wrapper integration exists.

Scaffold runtime code and generator code do not exist.

As of Step256, the standalone Makefile target exists:

- `make check-learner-state-frozen-policy-generation-scaffold-fixtures`

The target calls the scaffold fixture validator CLI in fixture-root mode and
Step258 adds release-quality wrapper integration through this standalone
target.

Step257 designs the future release-quality wrapper integration for this
standalone target. The design keeps wrapper implementation and workflow changes
out of scope while defining the proposed insertion point, command, label, log
safety review, failure interpretation, and status-marker staging.

Step258 implements that wrapper integration without changing GitHub Actions
workflows, Python code, tests, fixtures, scaffold runtime code, or generator
code.

## 3. Proposed Target Name

Candidate target names:

- `check-learner-state-frozen-policy-generation-scaffold-fixtures`
- `check-frozen-policy-generation-scaffold-fixtures`
- `check-learner-state-scaffold-fixtures`
- `check-learner-state-frozen-policy-scaffold-fixtures`

Recommended target:

- `check-learner-state-frozen-policy-generation-scaffold-fixtures`

Rationale:

- It follows the learner-state target naming style.
- It makes clear that this validates frozen policy generation scaffold fixtures.
- It stays distinct from `check-learner-state-frozen-policy-generation`, which
  validates the generation validator fixture root.
- It is long, but the meaning is precise and hard to confuse with frozen policy
  validation or scaffold runtime execution.

Rejected alternatives:

- `check-frozen-policy-generation-scaffold-fixtures` is shorter but drops the
  learner-state family marker.
- `check-learner-state-scaffold-fixtures` is too broad; future scaffold
  fixtures could exist for other learner-state stages.
- `check-learner-state-frozen-policy-scaffold-fixtures` is ambiguous because it
  can be read as frozen policy validation scaffold fixtures rather than frozen
  policy generation scaffold fixtures.

## 4. Proposed Command

Recommended command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_scaffold_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_scaffold
```

Initial output mode recommendation:

- use the human summary, not `--json`

Human summary rationale:

- It is developer-readable in Makefile output.
- It exposes only safe counts, reason-code counts, and safety flags.
- It avoids raw request, pointer, artifact, fixture, or JSON bodies.
- It is enough for a smoke target whose job is pass/fail contract validation.

The `--json` mode remains useful for future machine consumers, but it is not
needed for the first Makefile target.

## 5. Help Text

Recommended Makefile help text:

```text
check-learner-state-frozen-policy-generation-scaffold-fixtures  Smoke-test frozen policy generation scaffold fixture validation
```

The description should stay short and avoid implying scaffold runtime,
generator quality, model performance, or real-data readiness.

## 6. Expected Behavior

The future target should:

- discover the 11 scaffold fixture cases deterministically
- validate 3 valid cases as expected pass cases
- validate 8 invalid cases as expected fail cases
- report `matched_cases=11`
- report `mismatched_cases=0`
- report `input_error_cases=0`
- pass when all expected fixture outcomes match
- fail on usage errors, input errors, unsafe paths, or expected-result
  mismatches
- print safe human summary only

Intentional invalid fixtures are successful fixture tests when they fail for
their expected reason code.

## 7. Exit Code Behavior

The Makefile target should rely on the CLI exit code directly:

- CLI exit `0`: target passes
- CLI exit `2`: target fails
- CLI exit `3`: target fails
- CLI exit `1`: reserved for a future validation-only mode and not expected in
  the initial target

The Makefile should not translate or reinterpret these exit codes. A simple
command line keeps CI and local behavior aligned.

## 8. Output / Logging Safety

Allowed output:

- target name
- mode
- `total_cases`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `reason_code_counts`
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only_checked`
- `no_oracle_checked`
- `private_path_scan_checked`
- `performance_claim_scan_checked`

Forbidden output:

- `generation_request.json` body
- `input_fixture_pointer.json` body
- `expected_scaffold_result.json` body
- generation request body
- input pointer body
- generated artifact body
- frozen policy artifact body
- raw JSON body
- raw rows
- logits or probability dumps
- private paths
- raw learner text
- label body
- split body
- calibration policy body
- performance metric body

The target should preserve the CLI's safe-output behavior and should not add
extra shell output that reveals fixture contents.

## 9. Tmp / Output Policy

The future target should:

- read the scaffold fixture root only
- not create temporary outputs
- not write validation result files
- not use `manual_outputs`
- not require cleanup
- not create generated artifacts

The target is a smoke validation entrypoint, not an artifact generation step.

## 10. Relation To Existing Makefile Targets

`check-learner-state-frozen-policy-generation` validates the existing frozen
policy generation validation fixture root:

- `tests/fixtures/learner_state_frozen_policy_generation`

The proposed target validates the scaffold fixture root:

- `tests/fixtures/learner_state_frozen_policy_generation_scaffold`

`check-learner-state-frozen-policy` validates frozen selective prediction
policy artifacts, not scaffold fixture contracts.

`check-learner-state-selective-prediction` validates selective prediction and
calibration fixtures, not frozen policy generation scaffold fixtures.

The proposed target fits after the CLI implementation and before any
release-quality wrapper integration. It is not part of release-quality yet.

## 11. Release-Quality Future

Release-quality integration is not part of this step.

Recommended future order:

1. implement the standalone Makefile target
2. run standalone log-safety review
3. design release-quality integration
4. add wrapper integration only after the target is stable

Success of this future target would mean fixture contract validation passed. It
would not mean generator quality, policy quality, model performance, or
real-data readiness.

## 12. Testing Plan For Future Implementation

Future implementation checks should include:

- `make help` includes the target
- the target exits `0`
- the target reports 11 matched cases
- stdout remains safe
- stderr remains safe
- no temporary output is created
- Makefile diff is limited
- release-quality wrapper is not changed unless a later step explicitly asks
  for it
- GitHub Actions workflows are not changed unless a later step explicitly asks
  for it
- Python validator tests still pass
- CLI tests still pass
- existing learner-state checks still pass

## 13. No-Oracle / Synthetic-Only Boundary

The scaffold fixture root is synthetic-only.

The future target must not use:

- real participant data
- raw learner text
- observed-after text
- final text
- gold labels
- expected action as scoring feedback
- test-derived temperature tuning
- test-derived threshold tuning
- real-data paths
- participant-data paths
- private-data paths
- `manual_outputs`

The target should only validate safe metadata summaries and expected reason-code
alignment.

## 14. What This Does NOT Do

This document does not:

- implement a Makefile target
- change the Makefile
- integrate release-quality
- change GitHub Actions workflows
- change Python code
- change Python tests
- create or modify fixtures
- implement scaffold runtime code
- implement generator code
- compute metrics
- fit calibration
- run selective prediction
- train an estimator
- use real data
- prove performance
- claim production or data-collection readiness

## 15. Beginner-Friendly Explanation

A Makefile target is a short command name that runs a longer command in a
repeatable way.

The CLI already exists, but a Makefile target gives developers one memorable
entrypoint and lets future CI wrappers call the same command humans use.

The target should not go into release-quality immediately because it first needs
a standalone implementation and log-safety review.

Target success would mean the scaffold fixture files match their expected safe
contract. It would not mean a generator exists, and it would not evaluate
generation quality.

The target should not create temporary outputs because this validation is
read-only. A read-only target has less cleanup risk and fewer chances to
accidentally publish generated bodies.

## 16. Next Recommended Steps

Candidate next steps:

- Makefile target implementation
- release-quality integration design
- remaining scaffold fixture expansion design
- scaffold runtime API design

Recommended next step:

- release-quality integration design

Reason:

- the fixture root exists
- the validator API exists
- the CLI exists
- CLI tests exist
- Step256 adds the standalone Makefile target
- release-quality staging should still wait for a separate design and wrapper
  integration step

## 17. Update History

- Step255: initial docs-only scaffold fixture validator Makefile target design.
- Step256: standalone Makefile target implemented as
  `check-learner-state-frozen-policy-generation-scaffold-fixtures`.
- Step257: linked the docs-only release-quality integration design for this
  target.
- Step258: release-quality wrapper now calls the standalone target after frozen
  policy generation validation and before config/scoring smoke checks.

## Related Documents

- [Frozen policy generation scaffold fixture validator CLI design](frozen_policy_generation_scaffold_fixture_validator_cli_design.md)
- [Frozen policy generation scaffold fixture validator release-quality integration design](frozen_policy_generation_scaffold_fixture_validator_release_quality_integration_design.md)
- [Frozen policy generation scaffold fixture validator design](frozen_policy_generation_scaffold_fixture_validator_design.md)
- [Frozen policy generation scaffold fixture design](frozen_policy_generation_scaffold_fixture_design.md)
- [Frozen policy generation scaffold implementation design](frozen_policy_generation_scaffold_implementation_design.md)
- [Milestone 11 frozen policy generation validation infrastructure recap](milestone_11_frozen_policy_generation_validation_infrastructure_recap.md)
- `python/learner_state/frozen_policy_generation_scaffold_fixture_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_scaffold_fixture_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_scaffold_fixture_validation_cli.py`
- [Public release checklist](public_release_checklist.md)
