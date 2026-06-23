# Frozen Policy Generation Scaffold Fixture Validator Release-Quality Integration Design

## 1. Purpose

This document designs a future release-quality wrapper integration for the
frozen policy generation scaffold fixture validator Makefile target.

This is a docs-only integration design. It does not change the release-quality
wrapper, change GitHub Actions workflows, change the Makefile, change Python
code, change tests, change fixtures, implement scaffold runtime code, implement
a generator, compute metrics, evaluate performance, or claim real-data
readiness.

The goal is to define where and how
`check-learner-state-frozen-policy-generation-scaffold-fixtures` should later
be added to `make check-release-quality` safely.

## 2. Current State

The scaffold fixture root exists:

- `tests/fixtures/learner_state_frozen_policy_generation_scaffold`

The validator API exists:

- `python/learner_state/frozen_policy_generation_scaffold_fixture_validation.py`

The validator CLI exists:

- `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_scaffold_fixture_validation`

The standalone Makefile target exists:

- `make check-learner-state-frozen-policy-generation-scaffold-fixtures`

The standalone target passes with safe metadata-only output:

- `total_cases=11`
- `matched_cases=11`
- `mismatched_cases=0`
- `input_error_cases=0`

Step258 implements the release-quality wrapper integration.

No GitHub Actions workflow change exists for this target.

Scaffold runtime code and generator code do not exist.

## Step258 Implementation Status

Step258 adds the standalone target to `scripts/check_release_quality.sh` after
learner-state frozen policy generation validation and before config/scoring
smoke checks.

Implemented wrapper label:

```text
release_quality_check: learner-state frozen policy generation scaffold fixture validation
```

Implemented wrapper command:

```bash
make check-learner-state-frozen-policy-generation-scaffold-fixtures
```

The integration keeps the standalone target's safe human summary behavior:

- `total_cases=11`
- `matched_cases=11`
- `mismatched_cases=0`
- `input_error_cases=0`
- no request body
- no pointer body
- no artifact body
- no raw rows
- no logits dump
- no private paths
- no tmp output

## 3. Proposed Wrapper Insertion Point

Recommended insertion point:

- immediately after learner-state frozen policy generation validation
- before config and scoring smoke checks

Recommended learner-state sequence inside the release-quality wrapper:

1. learner-state selective prediction calibration validation
2. learner-state frozen policy validation
3. learner-state frozen policy generation validation
4. learner-state frozen policy generation scaffold fixture validation
5. config/scoring smoke checks

Rationale:

- scaffold fixture validation depends conceptually on the generation validation
  infrastructure being present
- it is still a learner-state contract check, so it belongs before broader
  config/scoring smoke checks
- it validates scaffold fixture contract safety, not runtime scaffold behavior
  or generator quality

## 4. Proposed Wrapper Command

Recommended command:

```bash
make check-learner-state-frozen-policy-generation-scaffold-fixtures
```

The wrapper should call the Makefile target instead of invoking the Python CLI
directly.

Rationale:

- the standalone Makefile target has already been verified
- developers and CI use the same entrypoint
- wrapper readability stays high
- long CLI arguments are not duplicated in the wrapper
- future target changes remain localized to the Makefile

## 5. Proposed Wrapper Label

Recommended label:

```text
release_quality_check: learner-state frozen policy generation scaffold fixture validation
```

The label should describe fixture contract validation and should not imply
scaffold runtime execution, generator quality, model performance, or real-data
readiness.

## 6. Expected Wrapper Behavior

Expected behavior after future integration:

- if the target passes, release-quality continues
- if the target fails, release-quality fails
- the expected root summary remains count-only:
  - `total_cases=11`
  - `matched_cases=11`
  - `mismatched_cases=0`
  - `input_error_cases=0`
- output remains safe human summary only
- no request body is printed
- no pointer body is printed
- no artifact body is printed
- no raw rows are printed
- no logits dump is printed
- no private paths are printed
- no temporary output is created by this target

## 7. Log Safety Review

Allowed log fields:

- target name
- mode
- `total_cases`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `reason_code_counts`
- safety flags
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only_checked`
- `no_oracle_checked`
- `private_path_scan_checked`
- `performance_claim_scan_checked`

Forbidden log content:

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
- performance metric body
- raw GitHub Actions logs
- full job output copied into docs

The wrapper should add only a label and the Makefile command. It should not add
extra inspection, printing, or artifact capture around the target.

## 8. Failure Interpretation

The following should be treated as release-quality failures:

- fixture contract mismatch
- expected-result mismatch
- unsafe path
- raw rows, logits, or artifact body leak
- invalid fixture no longer fails as expected
- valid fixture no longer passes
- reason-code mismatch
- malformed fixture input
- input error

These failures are not model performance failures. They indicate scaffold
fixture contract or safety regressions. They do not measure generator quality,
policy quality, calibration quality, selective prediction correctness, or
learner-state estimator performance.

## 9. Relation To Existing Release-Quality Checks

Existing learner-state checks cover different contract layers:

- learner-state audit fixtures: sequence audit fixture safety
- learner-state exporter CLI smoke: synthetic exporter behavior and safe counts
- learner-state estimator input validation: exported feature/label contract
- learner-state selective prediction calibration validation: calibration fixture
  contract and no-oracle boundaries
- learner-state frozen policy validation: frozen selective prediction policy
  artifact contract
- learner-state frozen policy generation validation: bridge contract for
  generation request, input pointer, and expected generation result metadata
- learner-state frozen policy generation scaffold fixture validation: scaffold
  fixture contract safety and expected reason-code alignment
- config/scoring smoke checks: synthetic config and scoring wiring

Scaffold fixture validation is not scaffold runtime execution and is not
generator quality validation. It checks that the scaffold fixture root remains
safe, synthetic-only, metadata-only, and expected-result aligned.

## 10. Makefile / Workflow Status

Current status:

- Makefile target already exists
- release-quality wrapper now includes the scaffold fixture validator target
- GitHub Actions workflow is not changed
- scaffold runtime is not implemented
- generator is not implemented

Future implementation should modify only the release-quality wrapper if
possible. The workflow YAML may not need any change if it already calls the
wrapper.

## 11. Testing Plan For Future Implementation

Future implementation checks should include:

- `make check-learner-state-frozen-policy-generation-scaffold-fixtures` passes
- `make check-release-quality` includes the scaffold fixture validation label
- `make check-release-quality` passes
- stdout contains 11 matched cases for the scaffold fixture target
- stdout does not contain request body, pointer body, artifact body, raw rows,
  logits dump, private paths, or raw learner text
- `git diff -- .github/workflows/release-quality.yml` has no diff unless a
  workflow change is explicitly required
- wrapper diff is limited to the new label and target command
- Python tests pass
- all existing checks pass

## 12. No-Oracle / Synthetic-Only Boundary

The scaffold fixture root is synthetic-only.

Invalid fixtures are safety tests.

The future wrapper integration must not expose:

- request body
- pointer body
- generated artifact body
- frozen policy artifact body
- raw rows
- logits dumps
- scoring feedback
- calibration fitting
- metric computation
- model performance evidence
- real data
- raw learner text
- private paths

Success means the scaffold fixture contract validation matched expected
metadata-only outcomes.

## 13. Release-Quality Future Status Marker

After wrapper integration, a later remote/manual Release Quality run record can
be created.

That future status marker should record count-only metadata, such as:

- target included: yes/no
- `total_cases=11`
- `matched_cases=11`
- `mismatched_cases=0`
- `input_error_cases=0`
- `content_suppressed=true`
- `no_raw_rows=true`

It must not record raw logs, full job output, request bodies, pointer bodies,
artifact bodies, JSON bodies, raw rows, logits dumps, private paths, raw
learner text, or performance metric bodies.

## 14. What This Does NOT Do

This design and the Step258 integration do not:

- change GitHub Actions workflows
- change the Makefile
- change Python code
- change Python tests
- create or modify fixtures
- implement scaffold runtime code
- implement generator code
- compute metrics
- use real data
- prove performance
- claim production or data-collection readiness

## 15. Beginner-Friendly Explanation

Release-quality is the repository's larger safety check bundle. It runs many
smoke checks together before work is considered ready for release-style review.

The standalone target came first so its output and behavior could be checked in
isolation. Only after that does it make sense to design wrapper integration.

The wrapper should call the Makefile target rather than the Python command
directly because the Makefile target is the shared stable entrypoint for humans
and CI.

Log safety matters because release-quality output can be viewed or copied more
widely. It must show counts and reason codes, not fixture bodies or raw data.

Success would mean the scaffold fixtures match their safe expected contract. It
would not mean scaffold runtime code exists, a generator works, or a model has
good performance.

## 16. Next Recommended Steps

Candidate next steps:

- release-quality wrapper integration implementation
- remote/manual run record workflow design
- scaffold runtime API design

Recommended next step:

- release-quality wrapper integration implementation

Reason:

- the fixture root exists
- the validator API exists
- the CLI exists
- CLI tests exist
- the standalone Makefile target exists and passes
- this design fixes the intended wrapper placement, command, label, and log
  safety boundaries

## 17. Update History

- Step257: initial docs-only scaffold fixture validator release-quality
  integration design.
- Step258: release-quality wrapper integration implemented with the standalone
  scaffold fixture validator Makefile target.

## Related Documents

- [Frozen policy generation scaffold fixture validator Makefile target design](frozen_policy_generation_scaffold_fixture_validator_makefile_target_design.md)
- [Frozen policy generation scaffold fixture validator CLI design](frozen_policy_generation_scaffold_fixture_validator_cli_design.md)
- [Frozen policy generation scaffold fixture validator design](frozen_policy_generation_scaffold_fixture_validator_design.md)
- [Frozen policy generation scaffold fixture design](frozen_policy_generation_scaffold_fixture_design.md)
- [Frozen policy generation scaffold implementation design](frozen_policy_generation_scaffold_implementation_design.md)
- [Milestone 11 frozen policy generation validation infrastructure recap](milestone_11_frozen_policy_generation_validation_infrastructure_recap.md)
- [Frozen policy generation release-quality integration design](frozen_policy_generation_release_quality_integration_design.md)
- [Public release checklist](public_release_checklist.md)
