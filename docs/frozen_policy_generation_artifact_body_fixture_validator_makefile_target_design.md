# Frozen Policy Generation Artifact Body Fixture Validator Makefile Target Design

## 1. Purpose

This document designs a future Makefile target for running the frozen policy
generation artifact body fixture validator CLI.

This is a docs-only design. It is not a Makefile implementation, not
release-quality integration, not artifact body generation implementation, not
file writing, not performance evaluation, and not a real-data readiness claim.

The design keeps the boundary synthetic-only, metadata-only, and no-oracle.
It names the target, command, help text, expected safe output, exit-code
interpretation, log-safety policy, and future release-quality staging.

## 2. Current State

- Artifact body fixtures exist.
- The artifact body fixture validator API exists.
- The artifact body fixture validator CLI exists.
- CLI tests exist.
- The artifact body fixture Makefile target does not exist.
- Release-quality integration for the artifact body fixture validator does
  not exist.
- Artifact body generation does not exist.
- Manifest body generation does not exist.
- Artifact file writing does not exist.
- Manifest file writing does not exist.

The current fixture root is:

`tests/fixtures/learner_state_frozen_policy_generation_artifact_body`

It contains 18 synthetic metadata cases: 4 valid cases and 14 invalid
expected fail-closed cases.

## 3. Proposed Target Name

Candidate target names:

- `check-learner-state-frozen-policy-generation-artifact-body-fixtures`
- `check-frozen-policy-generation-artifact-body-fixtures`
- `check-learner-state-artifact-body-fixtures`
- `check-artifact-body-fixtures`

Recommended target:

`check-learner-state-frozen-policy-generation-artifact-body-fixtures`

Reasons:

- It follows the learner-state namespace used by related targets.
- It stays aligned with the frozen policy generation pipeline.
- It is clear that the target validates artifact body fixtures.
- It is easy to place beside the existing artifact writer fixture target.
- It is suitable for a future release-quality label.

The shorter names are easier to type but lose useful namespace and pipeline
context. The recommended name is longer, but it is explicit and consistent
with the surrounding validation targets.

## 4. Proposed Command

Future target command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body
```

The command should run the existing CLI on the fixture root. It should not
create output files, write artifacts, write manifests, or generate artifact
bodies.

## 5. Proposed Help Text

Future `make help` text:

```text
check-learner-state-frozen-policy-generation-artifact-body-fixtures  Validate frozen policy generation artifact body fixtures
```

## 6. Expected Behavior

The future target should:

- run the artifact body fixture validator CLI on the fixture root
- exit `0` when all expected fixture outcomes match
- report `mode=fixture_root`
- report
  `validation_schema_version=learner_state_frozen_policy_generation_artifact_body_fixture_validation_v0.1`
- report `total_cases=18`
- report `valid_cases=4`
- report `invalid_cases=14`
- report `matched_cases=18`
- report `mismatched_cases=0`
- report `input_error_cases=0`
- report `reason_code_counts` as count-only metadata
- report `content_suppressed=true`
- report `no_raw_rows=true`
- report `no_logits_dump=true`
- report `no_private_paths=true`
- report `no_performance_claims=true`
- report `synthetic_only_checked=true`
- report `no_oracle_checked=true`
- report `artifact_policy_checked=true`
- report `body_suppression_checked=true`
- report `artifact_body_audit_checked=true`
- report `request_body_count=0`
- report `pointer_body_count=0`
- report `expected_body_count=0`
- report `raw_row_count=0`
- report `logits_dump_count=0`
- report `private_path_count=0`
- report `performance_metric_count=0`
- report `manifest_body_count=0`
- avoid artifact body payload output
- avoid generated policy body output
- avoid manifest body output
- avoid file writing
- avoid performance evidence

Success means the fixture validator contract matched the safe expected
metadata for the 18 synthetic cases. It does not mean artifact body generation
exists or that generated artifact quality has been evaluated.

## 7. Exit Code Interpretation

The Makefile target should pass through the CLI exit code without
transformation.

- CLI exit `0`: target passes.
- CLI exit `2`: target fails due to usage or input error.
- CLI exit `3`: target fails due to validation mismatch.
- CLI exit `1`: target fails due to unexpected internal error.

Expected fail-closed invalid fixtures are included in root validation. They
still contribute to a target pass when the validator matches their expected
safe fail-closed metadata.

## 8. Output And Logging Safety

The future target may output:

- mode
- validation schema version
- total, valid, invalid, matched, mismatched, and input-error counts
- count-only reason code counts
- safety flags
- body, raw-row, logits, private-path, performance, and manifest counts
- schema names
- case IDs only if future mismatch details need safe identifiers

The future target must not output:

- artifact body request body
- artifact writer result pointer body
- expected artifact body result body
- artifact body payload
- generated policy body
- manifest body
- raw rows
- logits
- probabilities
- private paths
- local absolute paths
- raw learner text
- performance metric body
- GitHub raw logs
- full job output

The target should use the CLI human summary by default. JSON output should
remain available through the CLI but should not be required for this target
unless a later project style decision explicitly needs it.

## 9. Relation To Existing Targets

- The artifact writer fixture target validates writer result metadata.
- The artifact writer runtime target validates one safe writer CLI runtime
  smoke path.
- The future artifact body fixture target will validate the artifact body
  generation boundary fixtures.
- The artifact body fixture target does not generate artifact bodies.
- The artifact body fixture target does not validate artifact writer quality.
- The generator scaffold targets remain separate.
- Release-quality integration remains a future step.

This target is a fixture-contract check, not a generator-quality or
performance check.

## 10. Makefile Implementation Notes For Future

Future implementation should:

- add the target to `.PHONY`
- add the help text to `make help`
- follow the existing Makefile style
- avoid adding the target to release-quality in the same step
- avoid creating output files
- avoid writing temporary validation results
- avoid writing artifact files
- avoid writing manifest files
- use the safe human summary by default
- avoid workflow changes

The target should be standalone first. Release-quality should be designed and
integrated only after the standalone target is implemented and verified.

## 11. Future Tests For Target Implementation

Future target implementation should verify:

- `make help` includes the target
- the target exits `0`
- output includes `total_cases=18`
- output includes `matched_cases=18`
- output includes `mismatched_cases=0`
- output includes `input_error_cases=0`
- output includes the expected safety flags
- output includes the expected zero counts
- output does not include request, pointer, expected, artifact, or manifest
  bodies
- output does not include raw rows
- output does not include logits
- output does not include private paths
- output does not include raw learner text
- the Makefile diff is limited to target and help updates
- the release-quality wrapper remains unchanged
- workflow YAML remains unchanged
- existing tests and checks continue to pass

## 12. Future Release-Quality Staging

Recommended future staging:

- Step330: artifact body fixture validator Makefile target implementation
- Step331: artifact body fixture validator release-quality integration design
- Step332: artifact body fixture validator wrapper integration
- Step333: artifact body fixture validator remote/manual run record workflow
  design
- Step334: artifact body fixture validator remote/manual run status marker

Artifact body generation remains separate and later. The fixture target should
exist before any artifact body generator implementation depends on this
contract.

## 13. Relation To Artifact Body Generation

The future target validates fixtures only. It does not generate artifact
bodies, validate generator quality, or prove production readiness.

Artifact body generation should remain a later step and should use this
fixture validator target only after the target is implemented and integrated
safely. The default artifact writer runtime should remain body-free until a
separate safe artifact body generation mode is designed and implemented.

## 14. Docs Safety Policy

Docs should include only:

- target name
- command
- help text
- expected safe fields
- exit codes
- counts
- reason code names
- safety flags
- non-goals

Docs should not include command output examples, JSON output examples, request
body examples, pointer body examples, expected result body examples, artifact
body examples, artifact body payloads, manifest body examples, raw rows,
logits, private paths, raw learner text, or raw log examples.

## 15. Beginner-Friendly Explanation

A Makefile target is a short command name that runs a longer command in a
consistent way. It lets a developer type one stable `make` command instead of
remembering the full Python module invocation.

The CLI already makes validation possible from a terminal. A Makefile target
is useful next because it gives the project a standard, discoverable command
for the same safe validation.

Release-quality is not added immediately because the standalone target should
be implemented and checked first. That keeps the change easier to review and
reduces the chance of mixing target wiring with release-quality policy.

Invalid fixtures can still be part of a passing target because they are
expected fail-closed cases. A pass means the validator recognized the unsafe
synthetic marker and returned the expected safe metadata, not that unsafe
content is allowed.

This is separate from body generation. These fixtures describe and validate
the safety boundary before any future code creates a safe artifact body.

## 16. What This Does Not Do

This design does not:

- implement a Makefile target
- integrate release-quality
- change workflow YAML
- change Python code or tests
- change fixture JSON
- implement artifact body generation
- generate artifact bodies
- generate policy bodies
- generate manifest bodies
- write artifact files
- write manifest files
- use real data
- compute metrics
- evaluate performance
- prove production readiness

## 17. Step329 Status

Step329 creates this docs-only artifact body fixture validator Makefile target
design. It does not add the Makefile target, integrate release-quality, change
workflow YAML, change Python code or tests, change fixture JSON, implement
artifact body generation, generate policy bodies, generate manifest bodies,
write files, compute metrics, use real data, or claim production readiness.

## 18. Step330 Implementation Status

Step330 implements the standalone Makefile target:

`check-learner-state-frozen-policy-generation-artifact-body-fixtures`

The target runs the existing artifact body fixture validator CLI against the
synthetic fixture root and emits the default safe human metadata summary. It
is added to `.PHONY` and `make help`.

Step330 does not integrate release-quality, change workflow YAML, change
Python code or tests, change fixture JSON, implement artifact body generation,
generate policy bodies, generate manifest bodies, write artifact or manifest
files, add output-file options, compute metrics, use real data, or claim
production readiness.

## Related Documents

- [Frozen policy generation artifact body fixture validator CLI design](frozen_policy_generation_artifact_body_fixture_validator_cli_design.md)
- [Frozen policy generation artifact body fixture validator design](frozen_policy_generation_artifact_body_fixture_validator_design.md)
- [Frozen policy generation artifact body fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body/README.md)
- [Frozen policy generation artifact body fixture design](frozen_policy_generation_artifact_body_fixture_design.md)
- [Frozen policy generation artifact body generation design](frozen_policy_generation_artifact_body_generation_design.md)
- [Learner-state frozen policy generation artifact writer runtime release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_writer_runtime_release_quality_remote_run_status.md)
- [Public release checklist](public_release_checklist.md)
