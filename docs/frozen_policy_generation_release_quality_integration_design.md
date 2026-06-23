# Frozen Policy Generation Release-Quality Integration Design

This document designs and records the Step244 implementation status for the
release-quality wrapper integration of the frozen policy generation validator
target.

It is primarily a design record. Step244 changes only the release-quality
wrapper by adding the standalone Makefile target. It does not change GitHub
Actions workflows, Makefile, Python code, tests, fixtures, generated
artifacts, generator code, frozen policy generation scaffold, calibration,
selective prediction, learner-state estimator, new model, or metric
computation. It is not a performance evaluation and is not a real-data
readiness claim.

Public docs must not include raw GitHub Actions logs, full job output, copied
log blocks, screenshots containing raw logs, frozen policy artifact bodies,
JSON bodies, generation request bodies, input pointer bodies, generated
artifact bodies, raw rows, logits/probability dumps, label bodies, split
bodies, calibration policy bodies, generated feature/label/manifest bodies,
private paths, raw learner text, or real participant data.

## 1. Purpose

The purpose of this document is to design and record how
`make check-learner-state-frozen-policy-generation` is integrated into the
release-quality wrapper.

The integration should make release-quality cover the frozen policy generation
bridge contract after the standalone target has already demonstrated safe
local behavior. It should not run a generator, compute calibration, compute
metrics, or claim model performance.

## 2. Current State

Current state:

- generation fixture root exists:
  `tests/fixtures/learner_state_frozen_policy_generation/`
- generation validator Python API exists in
  `python/learner_state/frozen_policy_generation_validation.py`
- generation validator CLI exists as
  `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_validation`
- Makefile target exists:
  `make check-learner-state-frozen-policy-generation`
- standalone target passes with `total_cases=13`, `matched_cases=13`,
  `mismatched_cases=0`, and `input_error_cases=0`
- standalone output is safe human summary only
- no request body, input pointer body, generated artifact body, raw rows,
  logits dump, private path, or performance metric body is printed
- release-quality wrapper integration exists
- workflow YAML change does not exist yet

## 3. Proposed Wrapper Insertion Point

Implemented wrapper order:

1. learner-state audit fixtures
2. learner-state exporter CLI smoke
3. learner-state estimator input validation
4. learner-state selective prediction calibration validation
5. learner-state frozen policy validation
6. learner-state frozen policy generation validation
7. config and scoring smoke checks

Implemented insertion point:

- immediately after `release_quality_check: learner-state frozen policy validation`
- immediately before `release_quality_check: config and scoring smoke checks`

Rationale:

- selective prediction validation checks the safe input contract
- frozen policy validation checks the frozen artifact output contract
- frozen policy generation validation checks the bridge contract between those
  two surfaces
- config/scoring smoke checks are broader pipeline checks, so the learner-state
  validator family should remain grouped before them

## 4. Proposed Wrapper Command

Implemented wrapper command:

```bash
make check-learner-state-frozen-policy-generation
```

The wrapper should not call the Python module directly.

Reasons:

- the Makefile target already gives the standalone entrypoint
- standalone log safety has been reviewed around the Makefile output
- local developer runs and CI use the same command
- the wrapper remains readable
- long CLI arguments are not duplicated in the wrapper

## 5. Proposed Wrapper Label

Implemented section label:

```text
release_quality_check: learner-state frozen policy generation validation
```

This label names the learner-state family and the generation validation bridge
contract without implying generator execution or performance evaluation.

## 6. Expected Wrapper Behavior

Expected behavior:

- if the target passes, release-quality continues
- if the target fails, release-quality fails
- the wrapper does not remap target exit codes
- expected root summary reports:
  - `total_cases=13`
  - `matched_cases=13`
  - `mismatched_cases=0`
  - `input_error_cases=0`
- output remains safe human summary only
- no request body is printed
- no input fixture pointer body is printed
- no generated artifact body is printed
- no raw rows are printed
- no logits/probability dump is printed
- no private paths are printed
- no performance metric body is printed
- no `tmp/` output is created by this target

## 7. Log Safety Review

Allowed output:

- target name
- command name
- mode
- total cases
- matched cases
- mismatched cases
- input error cases
- reason-code counts
- safety flags
- `content_suppressed`
- `no_raw_rows`

Forbidden output:

- generation request body
- input fixture pointer body
- generated frozen policy artifact body
- frozen policy artifact body
- raw rows
- logits/probability dump
- label body
- split body
- calibration policy body
- private paths
- raw learner text
- performance metric body
- raw GitHub Actions logs copied into docs
- full job output copied into docs

Intentional invalid fixture reason codes may appear in logs. Intentional
invalid fixture bodies must not appear.

## 8. Failure Interpretation

The following should fail release-quality, but they are not model performance
failures:

- expected-result mismatch
- unsafe path
- raw rows, logits, or performance marker leak
- invalid fixture no longer fails as expected
- valid fixture no longer passes
- input pointer mismatch
- generation request schema mismatch
- frozen policy validation consistency mismatch
- input error

These failures mean the fixture contract, bridge validation, or log-safety
boundary changed. They do not mean a model is inaccurate, calibrated, useful,
or production-ready.

## 9. Remote / Manual Run Record Future

After wrapper integration, a future remote/manual run status marker may record
only public-safe metadata:

- workflow name
- branch
- commit short hash
- run status
- job status
- target included yes/no
- wrapper label
- total cases
- matched cases
- mismatched cases
- input error cases
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only_checked`
- `no_oracle_checked`
- `test_tuning_checked`
- `private_path_scan_checked`
- `performance_claim_scan_checked`

Do not record:

- raw logs
- full job output
- generation request body
- input pointer body
- generated artifact body
- frozen policy artifact body
- JSON body
- private paths
- raw rows
- logits/probability dumps
- raw learner text
- performance metric body

The future record workflow is specified in
[Frozen policy generation release-quality remote run record workflow](frozen_policy_generation_release_quality_remote_run_record_workflow.md).
It should be used before creating any actual status marker.

## 10. Relation To Existing Release-Quality Checks

Related release-quality checks:

- learner-state audit checks no-oracle and future-leakage boundaries for
  learner-state sequence fixtures
- learner-state exporter CLI smoke checks synthetic export behavior and safe
  count summaries
- estimator input validation checks feature/label input contracts
- selective prediction calibration validation checks prediction/label/split
  fixture contracts and tuning safety
- frozen policy validation checks frozen selective prediction policy artifact
  contracts
- frozen policy generation validation checks the bridge contract between
  validated selective prediction inputs and future frozen policy artifacts
- config/scoring smoke checks broader synthetic pipeline and config behavior

Frozen policy generation validation is not generation quality, calibration
quality, selective prediction correctness, or model performance evidence. It
only checks that safe synthetic generation request and pointer metadata match
the expected bridge contract.

## 11. Makefile / Workflow Status

Status:

- Makefile target already exists
- release-quality wrapper now calls the Makefile target
- GitHub Actions workflows are not changed
- only `scripts/check_release_quality.sh` changed for wrapper integration
- workflow YAML did not need changes because the workflow already calls the
  release-quality wrapper

## 12. Testing Plan For Implementation

Implementation checks:

- `make check-learner-state-frozen-policy-generation` passes
- `make check-release-quality` includes the generation validation label
- `make check-release-quality` passes
- stdout includes `total_cases=13` and `matched_cases=13`
- stdout does not include request bodies, input pointer bodies, generated
  artifact bodies, raw rows, logits dumps, private paths, or performance
  metric bodies
- `git diff -- .github/workflows/release-quality.yml` shows no diff unless a
  workflow change is explicitly required
- wrapper diff is limited to the new section and command
- Python tests still pass
- all existing checks still pass
- conflict marker grep remains clean

## 13. No-Oracle / Synthetic-Only Boundary

Boundary:

- fixture root is synthetic-only
- intentional invalid fixtures are allowed only as safety tests
- generation validation is bridge contract validation
- not generator implementation
- not calibration fitting
- not selective prediction decision making
- not metric computation
- not model performance evidence
- no real data
- no raw learner text
- no expected action as scoring feedback

## 14. What This Does NOT Do

This step does not:

- change GitHub Actions workflows
- modify the Makefile
- modify Python code
- modify tests
- modify fixtures
- implement generator code
- implement calibration
- implement selective prediction
- train an estimator
- compute metrics
- use real data
- prove model performance

## 15. Beginner Notes

Release-quality is the project's larger local check bundle. It runs several
safe smoke and validation checks together before changes are treated as ready
for release-style review.

The standalone target comes first because a small command is easier to inspect
and stabilize. Once the standalone target is safe, release-quality can call it
as one more step.

The wrapper should call the Makefile target instead of the long Python command
because developers and CI should use the same stable entrypoint.

Log safety review matters because release-quality output may appear in local
terminals or CI logs. It must not expose request bodies, generated artifact
bodies, rows, labels, logits, private paths, or misleading performance
signals.

Success is not performance evidence. It means only that synthetic fixture
expected-result matching and bridge-contract validation passed.

## 16. Update History

- Step243: initial frozen policy generation validator release-quality
  integration design creation.
- Step244: integrated `make check-learner-state-frozen-policy-generation`
  into `scripts/check_release_quality.sh` after frozen policy validation and
  before config/scoring smoke checks. Workflow, Makefile, Python code, tests,
  and fixtures remain unchanged.
- Step245: added a docs-only remote/manual Release Quality run record workflow
  design for future count-only status marker creation.

## Related Documents

- [Frozen policy generation release-quality remote run record workflow](frozen_policy_generation_release_quality_remote_run_record_workflow.md)
- [Frozen policy generation validator Makefile target design](frozen_policy_generation_validator_makefile_target_design.md)
- [Frozen policy generation validator CLI design](frozen_policy_generation_validator_cli_design.md)
- [Frozen policy generation validation design](frozen_policy_generation_validation_design.md)
- [Frozen policy generation fixture design](frozen_policy_generation_fixture_design.md)
- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Frozen policy generation fixtures](../tests/fixtures/learner_state_frozen_policy_generation/README.md)
- [Frozen policy release-quality integration design](frozen_policy_release_quality_integration_design.md)
- `python/learner_state/frozen_policy_generation_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_validation_cli.py`
- [Public release checklist](public_release_checklist.md)
