# Frozen Policy Generation Artifact Writer Fixture Validator Makefile Target Design

## 1. Purpose

This document designs a future Makefile target for running the frozen policy
generation artifact writer fixture validator CLI.

This is a docs-only design. It does not implement a Makefile target, change the
release-quality wrapper, change GitHub Actions workflow YAML, change Python
code, change tests, change fixture JSON, execute an artifact writer, generate
artifact bodies, generate generated policy bodies, generate manifest bodies,
write files, compute metrics, evaluate performance, or claim real-data
readiness.

The target should make the Step306 safe CLI easy to run from `make` while
preserving the synthetic-only, metadata-only, no-body fixture validation
contract.

## 2. Current State

- The artifact writer fixture root exists.
- The artifact writer fixture validator module exists.
- The artifact writer fixture validator CLI exists.
- The validator CLI tests exist.
- The artifact writer fixture validator Makefile target does not exist.
- Release-quality integration for the artifact writer fixture validator does
  not exist.
- The artifact writer implementation does not exist.
- Artifact body generation, generated policy body generation, manifest body
  generation, artifact file writing, and manifest file writing do not exist.

Current CLI entrypoint:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_fixture_validation
```

Current fixture root:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/`

## 3. Proposed Target Name

Target candidates:

- `check-learner-state-frozen-policy-generation-artifact-writer-fixtures`
- `check-frozen-policy-generation-artifact-writer-fixtures`
- `check-learner-state-artifact-writer-fixtures`
- `check-learner-state-frozen-policy-generation-artifact-fixtures`

Recommended target:

`check-learner-state-frozen-policy-generation-artifact-writer-fixtures`

Reasons:

- It stays inside the learner-state target namespace.
- It clearly identifies the frozen policy generation pipeline.
- It names the artifact writer fixture validator boundary, not a runtime
  artifact writer smoke.
- It aligns with existing fixture validator target naming.
- It will be easy to reference from a future release-quality label.

The shorter alternatives are less precise. They either drop the learner-state
namespace, obscure that the target is for frozen policy generation, or blur the
difference between artifact fixtures and artifact writer fixtures.

## 4. Proposed Command

Recommended command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer
```

The target should use root mode and the default safe human summary. JSON mode
should remain available for ad hoc CLI use, but the initial Makefile target does
not need it.

The target should call the CLI instead of duplicating validator logic in the
Makefile.

## 5. Proposed Help Text

Recommended help text:

```text
check-learner-state-frozen-policy-generation-artifact-writer-fixtures  Validate frozen policy generation artifact writer fixtures
```

## 6. Expected Behavior

The future target should:

- run the artifact writer fixture validator CLI in root mode
- exit `0`
- print `mode=fixture_root`
- print `total_cases=17`
- print `valid_cases=3`
- print `invalid_cases=14`
- print `matched_cases=17`
- print `mismatched_cases=0`
- print `input_error_cases=0`
- print `content_suppressed=true`
- print `no_raw_rows=true`
- print `no_logits_dump=true`
- print `no_private_paths=true`
- print `no_performance_claims=true`
- print `synthetic_only_checked=true`
- print `no_oracle_checked=true`
- print `artifact_policy_checked=true`
- print `body_suppression_checked=true`
- print `file_writing_checked=true`
- print `manifest_body_suppression_checked=true`
- print `output_path_safety_checked=true`
- print a validation schema version
- avoid request body output
- avoid pointer body output
- avoid expected result body output
- avoid artifact body output
- avoid generated policy body output
- avoid manifest body output
- avoid raw rows, logits, private paths, and raw learner text
- avoid tmp output
- avoid artifact writing
- avoid manifest writing

Invalid fail-closed fixtures are part of the root validation. They count as
matched when their expected safe failure reason code matches.

## 7. Exit Code Interpretation

The Makefile target should not transform CLI exit codes.

- CLI exit `0` means the target passes.
- CLI exit `2` means the target fails because of usage or input error.
- CLI exit `3` means the target fails because of mismatch.
- CLI exit `1` means the target fails because of unexpected internal error.

Expected invalid fail-closed fixtures are included in root validation. They
should still lead to target success when they match their expected metadata.

## 8. Output And Logging Safety

Allowed output:

- `mode`
- `total_cases`
- `valid_cases`
- `invalid_cases`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `reason_code_counts`
- safety flags
- `validation_schema_version`

Forbidden output:

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
- gold text
- performance metric body

The target should print only the CLI's safe metadata summary. It should not
wrap the command in a way that dumps fixture JSON, shell traces, raw log blocks,
or copied workflow output into docs.

## 9. Tmp And Output Policy

The future target should not create tmp outputs.

The target should not:

- write a validation result file
- write an artifact file
- write a generated policy file
- write a manifest file
- require cleanup
- write under `manual_outputs/`

## 10. Relation To Existing Targets

Existing related targets:

- `check-learner-state-frozen-policy-generation-generator-scaffold-fixtures`
  validates the generator scaffold fixture contract.
- `check-learner-state-frozen-policy-generation-generator-scaffold-runtime`
  runs one metadata-only generator scaffold CLI smoke case.
- `check-learner-state-frozen-policy-generation-scaffold-fixtures` validates
  the earlier runtime scaffold fixture contract.
- `check-learner-state-frozen-policy-generation-scaffold-runtime` runs the
  earlier runtime scaffold CLI smoke.

The proposed artifact writer fixture validator target would validate only the
artifact writer fixture contract. It would not run an artifact writer. An
artifact writer runtime target does not exist yet.

Success would mean the fixture contract matched. Success would not mean:

- artifact writer implementation quality
- artifact generation evidence
- generated policy quality
- manifest generation evidence
- model performance evidence
- production readiness

## 11. Future Tests For Target Implementation

When the target is implemented, future checks should verify:

- `make help` includes the target.
- the target exits `0`
- output includes `mode=fixture_root`
- output includes `total_cases=17`
- output includes `valid_cases=3`
- output includes `invalid_cases=14`
- output includes `matched_cases=17`
- output includes `mismatched_cases=0`
- output includes `input_error_cases=0`
- output includes required safety flags
- stdout/stderr contain no request body
- stdout/stderr contain no pointer body
- stdout/stderr contain no expected result body
- stdout/stderr contain no artifact body
- stdout/stderr contain no generated policy body
- stdout/stderr contain no manifest body
- stdout/stderr contain no raw rows
- stdout/stderr contain no logits
- stdout/stderr contain no private paths
- the target creates no tmp output
- the Makefile diff is limited
- the release-quality wrapper remains unchanged until a later integration step
- workflow YAML remains unchanged unless a later design explicitly requires it

## 12. Release-Quality Strategy

Do not add this target to release-quality in the Makefile implementation step.

Recommended staging:

1. Implement the standalone Makefile target.
2. Run the standalone target.
3. Review no-body-leakage behavior.
4. Design release-quality integration separately.
5. Integrate the wrapper only after the standalone target is stable.

Suggested future insertion point:

- after generator scaffold runtime smoke
- before any future artifact writer runtime smoke

Release-quality success would mean the artifact writer fixture contract
matched. It would not mean artifact writer implementation quality, artifact
body generation, generated policy body generation, manifest body generation,
performance quality, or production readiness.

## 13. Status Marker Future

After future release-quality integration and remote/manual Release Quality
success, a public-safe status marker may record:

- target included: yes/no
- `total_cases=17`
- `matched_cases=17`
- `mismatched_cases=0`
- `input_error_cases=0`
- safety flags
- validation schema version

The marker must not include raw logs, full job output, request body, pointer
body, expected result body, artifact body, policy body, generated policy body,
manifest body, raw rows, logits, private paths, raw learner text, or
performance metrics.

## 14. No-Oracle And Synthetic-Only Boundary

The target should validate synthetic fixture metadata only.

The boundary excludes:

- real data
- participant data
- raw learner text
- final text
- gold text
- observed-after text
- expected-action scoring feedback payloads
- test-derived tuning payloads
- artifact bodies
- generated policy bodies
- manifest bodies
- logits
- raw rows
- private paths

## 15. What This Does NOT Do

This document does not:

- implement a Makefile target
- integrate release-quality
- execute an artifact writer
- write artifacts
- write manifests
- generate policy bodies
- generate artifact bodies
- compute metrics
- evaluate performance
- use real data
- prove production readiness

## 16. Beginner-Friendly Explanation

A Makefile target is a short project command, usually run with `make`, that
wraps a longer command. It makes repeated checks easier to run consistently.

The CLI already validates the artifact writer fixture root. A Makefile target
would give contributors a short, memorable command for that same validation.

A fixture validator target checks whether fixture files match the expected
contract. A runtime smoke target runs actual runtime code on a small safe case.
This target is a fixture validator target only; it does not run an artifact
writer.

Invalid fail-closed fixtures can still be matched because they are expected to
fail safely. A matched invalid fixture means the fixture describes the correct
safe failure reason without leaking bodies or raw data.

Release-quality should not receive the target immediately because the standalone
target should first be implemented and checked on its own. That keeps failures
easy to understand and keeps the wrapper change small later.

## 17. Next Recommended Steps

Recommended next steps:

1. Step308: artifact writer fixture validator Makefile target implementation.
   Complete.
2. Step309: release-quality integration design. Complete:
   [Frozen policy generation artifact writer fixture release-quality integration design](frozen_policy_generation_artifact_writer_fixture_release_quality_integration_design.md).
3. Step310: wrapper integration. Complete.
4. Step311: remote status marker workflow design.

## 18. Step308 Makefile Target Implementation Status

Step308 implements the standalone Makefile target:

`check-learner-state-frozen-policy-generation-artifact-writer-fixtures`

The target command is:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_writer
```

The help text is:

```text
check-learner-state-frozen-policy-generation-artifact-writer-fixtures  Validate frozen policy generation artifact writer fixtures
```

The target validates the 17 synthetic metadata-only artifact writer fixture
cases in root mode and prints only a body-free metadata summary. It does not
create tmp output, write validation result files, write artifact files, write
manifest files, execute an artifact writer, generate artifact bodies, generate
generated policy bodies, generate manifest bodies, compute metrics, evaluate
performance, use real data, or claim production readiness.

Release-quality integration is still intentionally separate. Step308 does not
change `scripts/check_release_quality.sh` or GitHub Actions workflow YAML.

## 19. Step309 Release-Quality Integration Design Status

Step309 designs future release-quality wrapper integration for the standalone
artifact writer fixture validator target:
[Frozen policy generation artifact writer fixture release-quality integration design](frozen_policy_generation_artifact_writer_fixture_release_quality_integration_design.md).

The recommended wrapper placement is after the generator scaffold runtime smoke
target and before config and scoring smoke checks. Step309 is docs-only and
does not change `scripts/check_release_quality.sh`, GitHub Actions workflow
YAML, Makefile target behavior, Python code, Python tests, fixture JSON,
artifact writer implementation, artifact body generation, generated policy
body generation, manifest body generation, file writing, metric computation,
performance evaluation, real-data use, or production readiness.

## 20. Step310 Wrapper Integration Status

Step310 adds the standalone artifact writer fixture validator target to
`scripts/check_release_quality.sh` with the release-quality label designed in
Step309. The section runs after generator scaffold runtime smoke and before
config and scoring smoke checks.

Step310 does not change GitHub Actions workflow YAML, Makefile target behavior,
Python code, Python tests, fixture JSON, artifact writer implementation,
artifact body generation, generated policy body generation, manifest body
generation, file writing, metric computation, performance evaluation,
real-data use, or production readiness.

## Related Documents

- [Frozen policy generation artifact writer fixture release-quality integration design](frozen_policy_generation_artifact_writer_fixture_release_quality_integration_design.md)
- [Frozen policy generation artifact writer fixture validator CLI design](frozen_policy_generation_artifact_writer_fixture_validator_cli_design.md)
- [Frozen policy generation artifact writer fixture validator design](frozen_policy_generation_artifact_writer_fixture_validator_design.md)
- [Frozen policy generation artifact writer fixture design](frozen_policy_generation_artifact_writer_fixture_design.md)
- [Frozen policy generation artifact writer design](frozen_policy_generation_artifact_writer_design.md)
- [Frozen policy generation artifact policy design](frozen_policy_generation_artifact_policy_design.md)
- [Frozen policy generation artifact writer fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/README.md)
- [Learner-state frozen policy generation generator scaffold runtime release-quality remote run status](status/learner_state_frozen_policy_generation_generator_scaffold_runtime_release_quality_remote_run_status.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)
