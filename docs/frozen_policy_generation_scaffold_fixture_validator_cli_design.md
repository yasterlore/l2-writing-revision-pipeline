# Frozen Policy Generation Scaffold Fixture Validator CLI Design

## 1. Purpose

This document designs the command-line interface for the frozen policy
generation scaffold fixture validator and records the Step254 minimal
implementation status.

Step254 implements the minimal CLI entrypoint in
`python/learner_state/frozen_policy_generation_scaffold_fixture_validation.py`
and adds CLI tests in
`python/learner_state/tests/test_frozen_policy_generation_scaffold_fixture_validation_cli.py`.
It does not implement scaffold runtime code, generator code, Makefile targets,
release-quality integration, GitHub Actions workflow changes, metric
computation, performance evaluation, or real-data readiness.

The CLI should provide a safe way to run the existing scaffold fixture
validator against one synthetic fixture case or the full scaffold fixture
root. It should return only safe metadata summaries and must not print
generation request bodies, input pointer bodies, expected scaffold result
bodies, generated artifact bodies, raw rows, logits, private paths, raw
learner text, or metric bodies.

## 2. Current State

Current scaffold fixture validation assets:

- validator module:
  `python/learner_state/frozen_policy_generation_scaffold_fixture_validation.py`
- validator tests:
  `python/learner_state/tests/test_frozen_policy_generation_scaffold_fixture_validation.py`
- scaffold fixture root:
  `tests/fixtures/learner_state_frozen_policy_generation_scaffold/`
- valid cases: 3
- invalid cases: 8
- total cases: 11
- root README plus 33 JSON files
- public API for discovery, case loading, expected-result loading,
  case/root validation, comparison, and safe summary conversion

The CLI exists as of Step254. The following do not exist yet:

- scaffold fixture validator Makefile target
- release-quality integration for this scaffold fixture validator
- scaffold runtime
- generator runtime

## 3. Proposed CLI Entrypoint

Candidate entrypoints:

| Entrypoint | Assessment |
| --- | --- |
| `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_scaffold_fixture_validation` | Recommended initially. It keeps the CLI close to the existing API and follows the existing generation validator CLI pattern. |
| `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_scaffold_fixture_validation_cli` | Possible later if the CLI grows, but premature for the first fixture-root workflow. |

Recommended initial entrypoint:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_scaffold_fixture_validation
```

Rationale:

- the validation API and CLI wrapper remain in one small module
- the pattern matches the current frozen policy generation validator CLI
- there is no duplicate scanner or comparison logic
- the module remains separate from any future scaffold runtime module
- it is sufficient for the first fixture-root and single-case workflows

If the CLI later gains non-fixture modes or richer reporting, a separate CLI
module can be reconsidered.

## 4. CLI Modes

Future modes:

- fixture root mode:
  `--fixture-root tests/fixtures/learner_state_frozen_policy_generation_scaffold`
- single fixture case mode:
  `--fixture-case tests/fixtures/learner_state_frozen_policy_generation_scaffold/valid/minimal_fixed_threshold_dry_run`
- safe JSON summary output:
  `--json`
- help:
  `--help`

The initial implementation should stay fixture-focused. It should not run the
scaffold runtime, generate policy artifacts, compute metrics, or write output
files.

## 5. Argument Rules

Argument rules:

- exactly one of `--fixture-root` or `--fixture-case` is required
- passing both is a usage error
- passing neither is a usage error
- root mode validates the full initial root of 11 cases
- case mode validates exactly one case
- `--json` changes the presentation only; it must not expose file bodies

The CLI should reject unsafe input paths before validation when the path
contains real-data, participant-data, private-data, or manual-output markers.

## 6. Expected Behavior

Root mode should:

- discover all 11 cases deterministically
- validate 3 valid cases as expected pass
- validate 8 invalid cases as expected fail
- report `matched_cases=11`
- report `mismatched_cases=0`
- report `input_error_cases=0`
- aggregate safe reason-code counts
- print no fixture file bodies

Case mode should:

- validate one selected case
- return success for a valid case when it matches the expected pass result
- return success for an intentional invalid case when it fails with the
  expected reason code
- return an input error for missing, malformed, or unsafe fixture input
- return a mismatch error when the observed safe result differs from the
  expected scaffold result contract

Intentional invalid fixtures are successful fixture tests when they fail for
the expected reason.

## 7. Exit Code Design

Recommended exit codes:

- `0`: all expected fixture outcomes matched
- `2`: usage error, missing root or case, malformed fixture input, unsafe path,
  or other input error
- `3`: expected-result mismatch or fixture contract mismatch
- `1`: reserved for a future validation-only mode that does not perform
  expected-result matching

This mapping keeps future Makefile and CI behavior simple:

- `0` means the fixture contract matched expectations
- `2` means the command invocation or input was not valid enough to evaluate
- `3` means the fixture set was evaluated but did not match the expected
  contract

## 8. Safe Human Output

Human output may include:

- mode
- total case count
- matched case count
- mismatched case count
- input error case count
- reason-code counts
- content suppression flag
- no-raw-rows flag
- synthetic-only checked flag
- no-oracle checked flag
- private-path scan checked flag
- performance-claim scan checked flag
- safe fixture case label
- scaffold status
- reason codes

Human output must not include:

- `generation_request.json` body
- `input_fixture_pointer.json` body
- `expected_scaffold_result.json` body
- raw JSON body
- request body
- pointer body
- artifact body
- raw rows
- logits or probability dumps
- private paths
- raw learner text
- metric body

Case labels should be safe relative labels, not private absolute paths.

## 9. Safe JSON Output

JSON output should be machine-readable and safe. It should contain only the
same safe metadata that the API already exposes.

Root summary fields may include:

- mode
- total cases
- matched cases
- mismatched cases
- input error cases
- reason-code counts
- safety flags

Case summary fields may include:

- safe fixture case label
- case category
- scaffold status
- reason codes
- failed checks
- checked file count
- safety flags

Mismatch summaries may include:

- safe mismatch category
- safe case label
- expected status
- observed status
- expected reason code
- observed reason code

JSON output must not include file bodies, raw JSON bodies, request bodies,
pointer bodies, generated artifact bodies, raw rows, logits, probabilities,
labels, split bodies, private paths, raw learner text, or metric bodies.

## 10. Path Safety

The CLI should reject input paths containing:

- `real_data`
- `participant_data`
- `private_data`
- `manual_outputs`

Path safety rules:

- prefer relative fixture labels in output
- do not print absolute private paths
- report unsafe path failures by safe reason code only
- never echo raw path payloads
- keep fixture-root execution scoped to the synthetic fixture root

## 11. Expected Mismatch Reporting

Mismatch reporting should be metadata-only.

It may include:

- mismatch count
- safe mismatch category
- safe case label
- expected status
- observed status
- expected reason code
- observed reason code

It must not include:

- raw file contents
- raw JSON field body
- request body
- pointer body
- artifact body
- private path payload
- raw learner text

Mismatch summaries should be designed for debugging fixture contracts without
turning stdout or JSON into a fixture dump.

## 12. Relation To Python API

The CLI should wrap the existing Python API:

- root mode should call `validate_scaffold_fixture_root`
- case mode should call `validate_scaffold_fixture_case`
- expected-result matching should use `load_expected_scaffold_result` and
  `compare_scaffold_result_to_expected`
- display formatting should use safe summary metadata

The CLI should not duplicate scanner logic, reason-code mapping, or fixture
contract checks. The API remains the primary implementation surface.

## 13. Relation To Scaffold Runtime

This CLI validates fixtures only.

It does not:

- run scaffold runtime code
- build a generation plan
- write a policy artifact
- generate policy bodies
- fit calibration
- run selective prediction
- compute metrics
- train an estimator

The future scaffold runtime can use this fixture validator as a safety net,
but it should be implemented and tested separately.

## 14. Relation To Existing Generation Validator CLI

The existing frozen policy generation validator CLI checks:

- `tests/fixtures/learner_state_frozen_policy_generation/`

This future scaffold fixture validator CLI should check:

- `tests/fixtures/learner_state_frozen_policy_generation_scaffold/`

The output style, exit codes, and fixture-case/root modes should stay similar
so developer workflows remain predictable. The fixture roots should remain
separate because they validate different contracts:

- generation validation fixtures check generation request and frozen policy
  bridge-contract expectations
- scaffold fixtures check scaffold API/CLI behavior and metadata-only safety

## 15. Testing Plan For Future Implementation

Future CLI tests should cover:

- `--help` exits `0`
- root mode exits `0`
- root mode reports 11 matched cases
- valid single case exits `0`
- intentional invalid single case exits `0` when the expected failure matches
- missing root exits `2`
- no arguments exits `2`
- both `--fixture-root` and `--fixture-case` exit `2`
- temporary expected mismatch exits `3`
- `--json` output is parseable and safe
- stdout and stderr contain no request body, pointer body, artifact body, raw
  rows, logits, private paths, or raw learner text
- malformed temporary fixture returns input error without panic
- output ordering is deterministic

Tests should use temporary copied fixtures for mismatch or malformed scenarios
instead of modifying committed scaffold fixtures.

## 16. Makefile Future

After CLI implementation, a standalone Makefile target can be designed.

Candidate target names:

- `check-learner-state-frozen-policy-generation-scaffold-fixtures`
- `check-frozen-policy-generation-scaffold-fixtures`
- `check-learner-state-scaffold-fixtures`

Initial recommendation:

- `check-learner-state-frozen-policy-generation-scaffold-fixtures`

Rationale:

- it mirrors learner-state target naming
- it distinguishes scaffold fixtures from generation validation fixtures
- it is explicit enough for release-quality logs

Step254 verifies the standalone CLI behavior and log safety through CLI tests.
This step still does not implement a Makefile target. The target should be
designed and added in a later step.

## 17. Release-Quality Future

Release-quality integration should wait until:

1. CLI implementation exists
2. CLI tests pass
3. standalone Makefile target design is complete
4. standalone Makefile target implementation passes
5. log safety is reviewed
6. release-quality integration is designed
7. wrapper integration is implemented

The future wrapper should call the Makefile target, not duplicate the Python
CLI command.

## 18. What This Does NOT Do

This document and Step254 implementation do not:

- implement scaffold runtime
- implement a generator
- create or modify fixtures
- add a Makefile target
- integrate release-quality
- change GitHub Actions workflows
- compute metrics
- fit calibration
- run selective prediction
- train an estimator
- use real data
- prove model or generator performance

## 19. Beginner-Friendly Explanation

A CLI is a command someone can run from a terminal. Here, it would make the
scaffold fixture validator easier to use without writing Python test code by
hand.

The Python API is useful for tests and other code. A CLI is useful for humans,
Makefile targets, and CI wrappers.

The CLI should come before a Makefile target because the Makefile should call
a stable command rather than reimplement validation behavior itself.

Valid and invalid fixtures can both exit successfully because the question is
not "did every fixture pass?" The question is "did each fixture behave the way
we expected?" An invalid fixture is supposed to fail for a specific safe reason
code.

JSON output is for machines, but it still must be safe. It should include
counts, statuses, and reason codes, not fixture bodies or private data.

## 20. Next Recommended Steps

Step254 implements the scaffold fixture validator CLI.

Step255 designs the future standalone Makefile target that should call this
CLI. The target is not implemented in Step255; the design fixes the proposed
target name, command, help text, exit-code behavior, safe logging policy, and
release-quality staging boundary.

Recommended next step:

- design the standalone Makefile target for the scaffold fixture validator CLI

Reason:

- the CLI and CLI tests now exist
- a Makefile target should be introduced only after standalone log safety is
  confirmed
- release-quality integration should still wait for the standalone target

Other future steps:

- Makefile target design
- remaining invalid scaffold fixture expansion design
- scaffold runtime API design

## 21. Update History

- Step253: initial scaffold fixture validator CLI design.
- Step254: minimal scaffold fixture validator CLI implementation and CLI tests
  added.
- Step255: linked the docs-only scaffold fixture validator Makefile target
  design.

## Related Documents

- [Frozen policy generation scaffold fixture validator design](frozen_policy_generation_scaffold_fixture_validator_design.md)
- [Frozen policy generation scaffold fixture validator Makefile target design](frozen_policy_generation_scaffold_fixture_validator_makefile_target_design.md)
- [Frozen policy generation scaffold fixture design](frozen_policy_generation_scaffold_fixture_design.md)
- [Frozen policy generation scaffold implementation design](frozen_policy_generation_scaffold_implementation_design.md)
- [Milestone 11 frozen policy generation validation infrastructure recap](milestone_11_frozen_policy_generation_validation_infrastructure_recap.md)
- `python/learner_state/frozen_policy_generation_scaffold_fixture_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_scaffold_fixture_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_scaffold_fixture_validation_cli.py`
