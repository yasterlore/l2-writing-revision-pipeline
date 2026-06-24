# Frozen Policy Generation Generator Scaffold Runtime Release-Quality Integration Design

## 1. Purpose

This document designs a future release-quality wrapper integration for the
frozen policy generation generator scaffold runtime Makefile target.

This is a docs-only design. It does not change the release-quality wrapper,
change GitHub Actions workflows, change the Makefile, change Python code,
change tests, change fixtures, add an artifact writer, generate artifact
bodies, generate policy bodies, write files, compute metrics, evaluate
performance, or claim real-data readiness.

The goal is to define where and how
`check-learner-state-frozen-policy-generation-generator-scaffold-runtime`
should later enter `make check-release-quality` safely.

## 2. Current State

- The generator scaffold skeleton module exists at
  `python/learner_state/frozen_policy_generation_generator_scaffold.py`.
- The generator scaffold CLI exists at:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_generator_scaffold
```

- Generator scaffold skeleton tests and CLI tests exist.
- The generator scaffold runtime Makefile target exists:
  `make check-learner-state-frozen-policy-generation-generator-scaffold-runtime`.
- The generator scaffold fixture validator target is already in
  release-quality:
  `make check-learner-state-frozen-policy-generation-generator-scaffold-fixtures`.
- At Step296 design time, the generator scaffold runtime target was not in
  release-quality yet.
- Step297 adds the generator scaffold runtime smoke target to the
  release-quality wrapper.
- Artifact writer implementation does not exist.
- Artifact body generation and generated policy body generation do not exist.

Current standalone runtime target behavior is metadata-only:

- runs one valid synthetic request/pointer pair
- `mode=generator_scaffold`
- `generation_status=pass`
- `reason_codes=none`
- `failed_checks=none`
- `content_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `artifact_policy_checked=true`
- `body_suppression_checked=true`
- `file_writing_checked=true`
- `generated_artifact_written=false`
- `generated_artifact_body_available=false`
- `artifact_body_suppressed=true`
- no request body output
- no pointer body output
- no expected result body output
- no generated policy body output
- no artifact body output
- no raw rows
- no logits
- no private paths
- no target-specific tmp output
- no artifact writing
- no performance evidence

## 2.1 Step297 Wrapper Integration Status

Step297 implements this design by adding the standalone runtime smoke target
to `scripts/check_release_quality.sh` immediately after generator scaffold
fixture validation and before config/scoring smoke checks.

The added wrapper section is:

```text
release_quality_check: learner-state frozen policy generation generator scaffold runtime smoke
```

It calls:

```bash
make check-learner-state-frozen-policy-generation-generator-scaffold-runtime
```

The implementation is intentionally minimal. It does not change GitHub Actions
workflows, the Makefile, Python code, Python tests, fixtures, artifact file
writing, artifact bodies, generated policy bodies, artifact manifest writing,
metrics, performance evaluation, or real-data readiness status.

The wrapper now checks both generator scaffold layers:

- generator scaffold fixture validation checks the 18-case fixture contract
- generator scaffold runtime smoke runs one valid synthetic request/pointer
  pair through the metadata-only CLI

This remains a safety and contract check. It is not generator quality evidence,
artifact generation evidence, performance evidence, or production readiness
evidence.

## 3. Proposed Wrapper Insertion Point

The current relevant release-quality order is:

- learner-state frozen policy generation scaffold fixture validation
- learner-state frozen policy generation scaffold runtime smoke
- learner-state frozen policy generation generator scaffold fixture validation
- config and scoring smoke checks

Recommended insertion point:

- immediately after learner-state frozen policy generation generator scaffold
  fixture validation
- before config and scoring smoke checks

Recommended ordering after future integration:

1. learner-state frozen policy generation scaffold fixture validation
2. learner-state frozen policy generation scaffold runtime smoke
3. learner-state frozen policy generation generator scaffold fixture validation
4. learner-state frozen policy generation generator scaffold runtime smoke
5. config and scoring smoke checks

Rationale:

- generator scaffold fixture contract validation should run before generator
  scaffold runtime smoke
- contract -> runtime is the same staging pattern used by the earlier runtime
  scaffold path
- runtime scaffold checks and generator scaffold checks remain grouped before
  broader config/scoring smoke checks
- generator scaffold runtime smoke is metadata-only skeleton execution, not
  scoring/config work
- success is not generator quality, artifact generation, or performance
  evidence

## 4. Proposed Wrapper Command

Recommended wrapper command:

```bash
make check-learner-state-frozen-policy-generation-generator-scaffold-runtime
```

The wrapper should call the Makefile target instead of invoking the Python CLI
directly.

Rationale:

- the standalone target has already been verified as the local entrypoint
- developers and CI use the same command
- wrapper readability stays high
- long CLI arguments are not duplicated in the wrapper
- future target-local command changes remain localized to the Makefile

## 5. Proposed Wrapper Label

Recommended label:

```text
release_quality_check: learner-state frozen policy generation generator scaffold runtime smoke
```

The label should say `runtime smoke`, not generator quality, artifact
generation, model evaluation, calibration, or real-data readiness.

## 6. Expected Wrapper Behavior

Expected behavior after future integration:

- target pass -> release-quality continues
- target fail -> release-quality fails
- output remains safe metadata only
- no target-specific tmp output
- no artifact writing
- no generated policy body
- no performance evidence

Expected output metadata:

- `mode=generator_scaffold`
- `generation_status=pass`
- `reason_codes=none`
- `failed_checks=none`
- `content_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `artifact_policy_checked=true`
- `body_suppression_checked=true`
- `file_writing_checked=true`
- `generated_artifact_written=false`
- `generated_artifact_body_available=false`
- `artifact_body_suppressed=true`

The wrapper should add only a release-quality section label and the Makefile
target command. It should not add extra file inspection, body printing, or
artifact capture.

## 7. Failure Interpretation

The following should fail release-quality:

- CLI usage failure
- missing request/pointer fixture
- malformed request/pointer fixture
- `generation_status` is not `pass` for the selected valid smoke fixture
- `reason_codes` is not empty
- `failed_checks` is not empty
- request, pointer, expected-result, policy, generated-policy, or artifact
  body leakage
- raw rows leakage
- logits leakage
- private path leakage
- `artifact_policy_checked=false`
- `body_suppression_checked=false`
- `file_writing_checked=false`
- `generated_artifact_written=true`
- `generated_artifact_body_available=true`
- `artifact_body_suppressed=false`
- unexpected target-specific tmp output
- artifact writing
- generated policy body output
- internal error

These are release-quality safety or command-boundary failures. They are not
generator performance failures. They do not measure generator quality, policy
quality, calibration quality, selective prediction correctness, learner-state
estimator correctness, or real-data readiness.

## 8. Log Safety Review

Allowed log fields:

- target label
- command label
- `mode`
- `generation_status`
- `reason_codes`
- `failed_checks`
- `request_id`
- `pointer_id`
- `policy_id`
- `artifact_id`
- `generator_version`
- `validation_reference_ids`
- artifact flags
- safety flags
- `count_summary`
- `safe_summary`
- `schema_version`

Forbidden log content:

- request body
- pointer body
- expected result body
- policy body
- generated policy body
- artifact body
- manifest body
- raw rows
- logits
- probabilities
- private paths
- raw learner text
- final text
- observed-after text
- gold label
- performance metric body
- raw GitHub Actions logs
- full job output copied into docs

The future wrapper integration should rely on the generator scaffold CLI's
existing safe summary. It should not use shell commands that print fixture file
contents.

## 9. Relation To Existing Release-Quality Checks

- The generator scaffold fixture validator target validates the 18-case
  generator scaffold fixture contract.
- The generator scaffold runtime target validates one valid synthetic
  request/pointer runtime smoke.
- The runtime scaffold fixture validator target validates the earlier
  11-case runtime scaffold fixture contract.
- The runtime scaffold runtime target validates the earlier runtime scaffold
  CLI smoke.
- Frozen policy generation validation remains a separate fixture-root check.
- Config and scoring smoke checks remain separate from learner-state generator
  scaffold runtime smoke.

Generator scaffold runtime target success means the metadata-only skeleton CLI
command boundary and safe summary worked for one valid synthetic fixture pair.
It is not generator quality evidence, artifact generation evidence,
performance evidence, calibration evidence, or production readiness evidence.

## 10. Makefile / Workflow Status

- The Makefile target already exists.
- The release-quality wrapper is not changed by this design.
- GitHub Actions workflows are not changed by this design.
- Future implementation should modify only the wrapper if possible.
- Workflow YAML diff should remain none unless a future implementation finds a
  concrete wrapper invocation limitation.

## 11. Testing Plan For Future Implementation

Future wrapper implementation checks:

- standalone target passes
- `make check-release-quality` includes the new runtime smoke label
- `make check-release-quality` passes
- output includes `mode=generator_scaffold`
- output includes `generation_status=pass`
- output includes `reason_codes=none`
- output includes `failed_checks=none`
- output includes `content_suppressed=true`
- output includes `no_raw_rows=true`
- output includes `no_logits_dump=true`
- output includes `no_private_paths=true`
- output includes `artifact_policy_checked=true`
- output includes `body_suppression_checked=true`
- output includes `file_writing_checked=true`
- output includes `generated_artifact_written=false`
- output includes `generated_artifact_body_available=false`
- output includes `artifact_body_suppressed=true`
- no request, pointer, expected-result, policy, generated-policy, or artifact
  body leakage
- no raw rows, logits, or private path leakage
- wrapper diff is limited
- workflow diff is none
- all Python tests pass
- all existing checks pass

The checks should remain metadata-only and should not paste raw logs into docs.

## 12. Release-Quality Status Marker Future

After wrapper integration and a successful remote/manual Release Quality run,
a later status marker may record only public-safe metadata.

Allowed future generator scaffold runtime marker fields:

- target included: yes/no
- target name
- wrapper label
- `mode=generator_scaffold`
- `generation_status=pass`
- `reason_codes=none`
- `failed_checks=none`
- `content_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `artifact_policy_checked=true`
- `body_suppression_checked=true`
- `file_writing_checked=true`
- `generated_artifact_written=false`
- `generated_artifact_body_available=false`
- `artifact_body_suppressed=true`

The marker must not copy raw logs, request bodies, pointer bodies, expected
result bodies, policy bodies, generated policy bodies, artifact bodies, raw
rows, logits, private paths, raw learner text, or performance metric bodies.

## 13. No-Oracle / Synthetic-Only Boundary

The future wrapper integration should stay inside the current boundary:

- one valid synthetic request/pointer fixture
- no real data
- no participant data
- no raw learner text
- no final text
- no gold label
- no observed-after text
- no expected-action scoring feedback payload
- no test-derived tuning payload
- no artifact body
- no generated policy body
- no logits
- no raw rows
- no private paths

## 14. What This Does NOT Do

This document does not:

- integrate the release-quality wrapper
- change workflows
- change the Makefile
- change Python code
- change tests
- change fixtures
- execute an artifact writer
- write artifacts
- generate policy bodies
- generate artifact bodies
- write an artifact manifest
- compute metrics
- evaluate performance
- use real data
- prove production readiness

## 15. Beginner-Friendly Explanation

Release-quality is the project's broader local quality wrapper. It runs a
bundle of checks that should pass before treating the repository as healthy.

The standalone Makefile target came first so the command could be checked on
its own. Adding it to release-quality later makes the broader wrapper exercise
the same safe entrypoint developers can run manually.

The fixture validator target and runtime smoke target are different. The
fixture validator checks all generator scaffold fixture cases and expected
safe outcomes. The runtime smoke runs the generator scaffold CLI on one valid
synthetic request/pointer pair and checks that a safe metadata summary is
returned.

Runtime smoke success does not mean generator quality. It only means the
metadata-only skeleton CLI command boundary worked for one synthetic valid
fixture. It still does not generate artifacts, generate policy bodies, compute
metrics, evaluate performance, or prove real-data readiness.

A status marker should be a separate step because remote/manual run recording
needs its own public-safe review and must avoid copying raw logs.

## 16. Next Recommended Steps

Recommended next steps:

- future artifact writer design
- future generator scaffold expansion design
- future calibration scaffold work

Keep artifact writing, generated policy bodies, calibration work, performance
evaluation, and real-data readiness separate.

## 17. Step298 Remote Run Record Workflow Design Status

Step298 designs the future public-safe remote/manual Release Quality run
record workflow for generator scaffold runtime smoke:
[Frozen policy generation generator scaffold runtime release-quality remote run record workflow](frozen_policy_generation_generator_scaffold_runtime_release_quality_remote_run_record_workflow.md).

The design stages a future status marker at
`docs/status/learner_state_frozen_policy_generation_generator_scaffold_runtime_release_quality_remote_run_status.md`.
It does not create that status marker, run a remote workflow, change workflows,
change the release-quality wrapper, change the Makefile, change Python code,
change tests, change fixtures, write artifacts, emit artifact bodies, emit
generated policy bodies, compute metrics, evaluate performance, or claim
real-data readiness.

## 18. Step299 Remote Run Status Marker

Step299 creates the public-safe runtime smoke status marker:
[Learner-state frozen policy generation generator scaffold runtime release-quality remote run status](status/learner_state_frozen_policy_generation_generator_scaffold_runtime_release_quality_remote_run_status.md).

The marker records only run identity metadata, wrapper inclusion metadata,
pass-only runtime smoke fields, count-only fixture validation summaries, and a
public-safe safety review. It does not copy raw logs, request bodies, pointer
bodies, expected result bodies, policy bodies, generated policy bodies,
artifact bodies, raw rows, logits, private paths, raw learner text, or
performance metric bodies.

## Related Documents

- [Frozen policy generation generator scaffold runtime release-quality remote run record workflow](frozen_policy_generation_generator_scaffold_runtime_release_quality_remote_run_record_workflow.md)
- [Learner-state frozen policy generation generator scaffold runtime release-quality remote run status](status/learner_state_frozen_policy_generation_generator_scaffold_runtime_release_quality_remote_run_status.md)
- [Frozen policy generation generator scaffold CLI Makefile target design](frozen_policy_generation_generator_scaffold_cli_makefile_target_design.md)
- [Frozen policy generation generator scaffold CLI design](frozen_policy_generation_generator_scaffold_cli_design.md)
- [Frozen policy generation generator scaffold skeleton design](frozen_policy_generation_generator_scaffold_skeleton_design.md)
- [Frozen policy generation generator scaffold fixture validator release-quality integration design](frozen_policy_generation_generator_scaffold_fixture_validator_release_quality_integration_design.md)
- [Frozen policy generation generator scaffold fixture validator Makefile target design](frozen_policy_generation_generator_scaffold_fixture_validator_makefile_target_design.md)
- [Frozen policy generation generator scaffold fixture release-quality remote run record workflow](frozen_policy_generation_generator_scaffold_fixture_release_quality_remote_run_record_workflow.md)
- [Learner-state frozen policy generation generator scaffold fixture release-quality remote run status](status/learner_state_frozen_policy_generation_generator_scaffold_fixture_release_quality_remote_run_status.md)
- [Frozen policy generation scaffold runtime release-quality integration design](frozen_policy_generation_scaffold_runtime_release_quality_integration_design.md)
- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Frozen policy generation artifact policy design](frozen_policy_generation_artifact_policy_design.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)
