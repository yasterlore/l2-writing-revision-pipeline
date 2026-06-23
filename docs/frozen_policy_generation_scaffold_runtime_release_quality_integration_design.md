# Frozen Policy Generation Scaffold Runtime Release-Quality Integration Design

## 1. Purpose

This document designs a future release-quality wrapper integration for the
frozen policy generation scaffold runtime Makefile target.

This is a docs-only design. It does not change the release-quality wrapper,
change GitHub Actions workflows, change the Makefile, change Python code,
change tests, change fixtures, implement generator behavior, add an artifact
writer, compute metrics, evaluate performance, or claim real-data readiness.

The goal is to define where and how
`check-learner-state-frozen-policy-generation-scaffold-runtime` should later
enter `make check-release-quality` safely.

## 2. Current State

- Runtime API skeleton exists at
  `python/learner_state/frozen_policy_generation.py`.
- Runtime fixture compatibility tests exist at
  `python/learner_state/tests/test_frozen_policy_generation_scaffold_runtime_fixture_compatibility.py`.
- Runtime CLI exists at
  `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation`.
- Runtime Makefile target exists:
  `make check-learner-state-frozen-policy-generation-scaffold-runtime`.
- The release-quality wrapper does not include the runtime target yet.
- The release-quality wrapper already includes the scaffold fixture validator
  target.
- Generator implementation does not exist.
- Artifact writer implementation does not exist.

The standalone runtime target currently uses one valid synthetic scaffold
fixture pair. It exits `0`, returns `scaffold_status=pass`, suppresses content
and artifact bodies, writes no artifact, creates no tmp output, and does not
invoke a generator.

## 3. Proposed Wrapper Insertion Point

Recommended insertion point:

- immediately after learner-state frozen policy generation scaffold fixture
  validation
- before config and scoring smoke checks

Recommended release-quality learner-state ordering:

1. learner-state audit fixtures
2. learner-state exporter CLI smoke
3. learner-state estimator input validation
4. learner-state selective prediction calibration validation
5. learner-state frozen policy validation
6. learner-state frozen policy generation validation
7. learner-state frozen policy generation scaffold fixture validation
8. learner-state frozen policy generation scaffold runtime smoke
9. config/scoring smoke checks

Rationale:

- fixture contract validation should run before runtime smoke
- runtime smoke should be staged after the validator target has confirmed the
  scaffold fixture contract
- learner-state scaffold checks stay grouped before broader config/scoring
  smoke checks
- runtime smoke is not generator quality, policy quality, or performance
  evidence

## 4. Proposed Wrapper Command

Recommended wrapper command:

```bash
make check-learner-state-frozen-policy-generation-scaffold-runtime
```

The wrapper should call the Makefile target instead of invoking the Python CLI
directly.

Rationale:

- the standalone target has already been verified
- developers and CI use the same entrypoint
- wrapper readability stays high
- long CLI arguments are not duplicated in the wrapper
- future target command changes remain localized to the Makefile

## 5. Proposed Wrapper Label

Recommended label:

```text
release_quality_check: learner-state frozen policy generation scaffold runtime smoke
```

The label should say `runtime smoke`, not generator, artifact generation,
model evaluation, calibration, or real-data readiness.

## 6. Expected Wrapper Behavior

Expected behavior after future integration:

- if the runtime target passes, release-quality continues
- if the runtime target fails, release-quality fails
- output includes `scaffold_status=pass`
- output includes `content_suppressed=true`
- output includes `no_raw_rows=true`
- output includes `artifact_body_suppressed=true`
- output includes `generated_artifact_written=false`
- output includes `generated_artifact_body_available=false`
- output remains safe metadata only
- no tmp output is created by this target
- no artifact file is written
- no generator is invoked

The wrapper should add only a release-quality section label and the Makefile
target command. It should not add extra file inspection, body printing, or
artifact capture.

## 7. Failure Interpretation

The following should be treated as release-quality failures:

- runtime CLI usage failure
- missing fixture path
- malformed fixture input
- path-before-load unsafe condition
- runtime internal error
- `scaffold_status` is not `pass` for the selected valid smoke fixture
- request body leakage
- pointer body leakage
- artifact body leakage
- raw rows leakage
- logits or probability dump leakage
- private path leakage
- `generated_artifact_written` unexpectedly true
- `generated_artifact_body_available` unexpectedly true
- `artifact_body_suppressed` unexpectedly false

These are release-quality safety or command-boundary failures. They are not
model performance failures. They do not measure generator quality, policy
quality, calibration quality, selective prediction correctness, learner-state
estimator correctness, or real-data readiness.

## 8. Log Safety Review

Allowed log fields:

- target label
- command label
- `mode`
- `scaffold_status`
- `reason_codes`
- `failed_checks`
- `request_id`
- `pointer_id`
- validation references
- safety flags
- artifact flags
- schema version

Forbidden log content:

- request body
- pointer body
- expected scaffold result body
- artifact body
- raw JSON body
- raw rows
- logits or probability dumps
- private paths
- raw learner text
- final text
- observed-after text
- gold label
- performance metric body
- raw GitHub Actions logs
- full job output copied into docs

The future wrapper integration should rely on the runtime CLI's existing safe
summary. It should not use shell commands that print fixture file contents.

## 9. Relation To Existing Release-Quality Checks

Relevant existing checks:

- scaffold fixture validator target validates all 11 scaffold fixture
  contracts
- runtime target smoke-tests one valid runtime CLI path
- runtime fixture compatibility tests verify runtime summaries against the
  scaffold fixture expected-result contract
- frozen policy generation validator remains a separate generation validation
  fixture check
- config/scoring smoke checks remain separate from learner-state scaffold
  runtime smoke

Runtime target success means the runtime CLI command boundary and safe summary
worked for one synthetic valid fixture pair. It is not generator quality,
artifact quality, model performance, or production readiness evidence.

## 10. Makefile / Workflow Status

- The Makefile target already exists.
- Step272 updates the release-quality wrapper to include the runtime smoke.
- GitHub Actions workflow changes should not be needed if the workflow already
  calls the release-quality wrapper.
- The wrapper change is limited to `scripts/check_release_quality.sh`.
- Workflow YAML diff should remain none unless a separate reason appears.

## 11. Testing Plan For Future Implementation

Future wrapper implementation checks:

- `make check-learner-state-frozen-policy-generation-scaffold-runtime` passes
- `make check-release-quality` includes the new runtime smoke label
- `make check-release-quality` passes
- output includes `scaffold_status=pass`
- output includes `content_suppressed=true`
- output includes `no_raw_rows=true`
- output includes `generated_artifact_written=false`
- output includes `generated_artifact_body_available=false`
- output includes `artifact_body_suppressed=true`
- stdout and stderr contain no request body
- stdout and stderr contain no pointer body
- stdout and stderr contain no artifact body
- stdout and stderr contain no raw rows
- stdout and stderr contain no logits dump
- stdout and stderr contain no private paths
- wrapper diff is limited
- workflow diff is none
- all Python tests pass
- all existing checks pass

## 12. Release-Quality Status Marker Future

After wrapper integration and a successful remote/manual Release Quality run,
a later status marker may record only public-safe metadata.

Allowed future runtime smoke marker fields:

- target included yes/no
- target command label
- wrapper label
- `scaffold_status=pass`
- `content_suppressed=true`
- `no_raw_rows=true`
- `generated_artifact_written=false`
- `generated_artifact_body_available=false`
- `artifact_body_suppressed=true`

The marker must not copy raw logs, full job output, request bodies, pointer
bodies, artifact bodies, raw rows, logits, private paths, raw learner text, or
performance metric bodies.

## 13. No-Oracle / Synthetic-Only Boundary

The runtime smoke target uses only the synthetic scaffold fixture pair.

It must not use or expose:

- real data
- raw learner text
- final text
- observed-after text
- gold labels
- expected action as scoring feedback
- test-derived tuning
- artifact body
- logits or probability dumps
- raw rows
- performance metrics

This remains a synthetic-only runtime CLI smoke check.

## 14. What This Does NOT Do

This design does not:

- integrate the release-quality wrapper
- change GitHub Actions workflows
- change the Makefile
- change Python code
- change tests
- change fixtures
- implement generator behavior
- write artifacts
- create artifact bodies
- compute metrics
- evaluate performance
- use real data
- prove production readiness

## 15. Beginner-Friendly Explanation

Release-quality is the project's bigger local command bundle for checking that
important safety and smoke checks still pass before release-like work.

The standalone runtime target came first so the command could be tested on its
own. Once a standalone command is stable and safe, release-quality can call the
same target instead of duplicating a long Python command.

The runtime smoke should run after the scaffold fixture validator target
because the fixture validator checks the whole expected contract first. The
runtime smoke then checks that the runtime CLI can safely execute one valid
synthetic request/pointer pair.

Success is not generator quality because no generator runs. No policy artifact
is written, no artifact body is produced, and no performance metric is
computed.

A status marker should be a separate later step because remote/manual
Release Quality results need careful public-safe recording without raw logs or
body content.

The remote/manual recording workflow is designed in
[Frozen policy generation scaffold runtime release-quality remote run record workflow](frozen_policy_generation_scaffold_runtime_release_quality_remote_run_record_workflow.md).

## 16. Step272 Implementation Status

Step272 adds the standalone runtime target to `scripts/check_release_quality.sh`
immediately after scaffold fixture validation and before config/scoring smoke
checks.

Implemented wrapper label:

```text
release_quality_check: learner-state frozen policy generation scaffold runtime smoke
```

Implemented wrapper command:

```bash
make check-learner-state-frozen-policy-generation-scaffold-runtime
```

The integration keeps the runtime target's safe metadata-only output:

- `scaffold_status=pass`
- `content_suppressed=true`
- `no_raw_rows=true`
- `artifact_body_suppressed=true`
- `generated_artifact_written=false`
- `generated_artifact_body_available=false`
- no request body
- no pointer body
- no artifact body
- no raw rows
- no logits dump
- no private paths
- no tmp output from the runtime target
- no generator invocation
- no artifact writing

The implementation does not change GitHub Actions workflows, Makefile targets,
Python code, tests, fixtures, generator behavior, artifact writing, artifact
body generation, metric computation, real-data use, or performance claims.

## 17. Next Recommended Steps

Recommended next step:

- remote/manual run record workflow design

Then proceed with:

- remote/manual status marker after a safe successful run if needed

Generator implementation should remain separate.

## 18. Update History

- Step271: initial docs-only runtime release-quality integration design.
- Step272: recorded the release-quality wrapper integration implementation
  status.
- Step273: linked the docs-only runtime Release Quality remote/manual run
  record workflow design.

## Related Documents

- [Frozen policy generation scaffold runtime Makefile target design](frozen_policy_generation_scaffold_runtime_makefile_target_design.md)
- [Frozen policy generation scaffold runtime CLI design](frozen_policy_generation_scaffold_runtime_cli_design.md)
- [Frozen policy generation scaffold runtime API design](frozen_policy_generation_scaffold_runtime_api_design.md)
- [Frozen policy generation scaffold runtime fixture compatibility test design](frozen_policy_generation_scaffold_runtime_fixture_compatibility_test_design.md)
- [Frozen policy generation scaffold runtime fixture alignment design](frozen_policy_generation_scaffold_runtime_fixture_alignment_design.md)
- [Frozen policy generation scaffold runtime release-quality remote run record workflow](frozen_policy_generation_scaffold_runtime_release_quality_remote_run_record_workflow.md)
- [Frozen policy generation scaffold fixture validator release-quality integration design](frozen_policy_generation_scaffold_fixture_validator_release_quality_integration_design.md)
- [Milestone 12 frozen policy generation scaffold fixture validation recap](milestone_12_frozen_policy_generation_scaffold_fixture_validation_recap.md)
- [Public release checklist](public_release_checklist.md)
