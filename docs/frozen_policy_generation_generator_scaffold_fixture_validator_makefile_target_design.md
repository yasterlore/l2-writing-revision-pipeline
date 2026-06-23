# Frozen Policy Generation Generator Scaffold Fixture Validator Makefile Target Design

## 1. Purpose

This document designs a future Makefile target for running the frozen policy
generation generator scaffold fixture validator CLI.

This is a docs-only design. It does not implement a Makefile target, change the
Makefile, integrate release-quality, change a workflow, change Python code,
change tests, change fixtures, implement a generator, add an artifact writer,
generate artifact bodies, compute metrics, evaluate performance, or claim
real-data readiness.

The goal is to make the existing safe generator scaffold fixture validator CLI
easy to run from `make` while preserving the current synthetic-only,
no-oracle, metadata-only output boundary.

## 2. Current State

- Metadata-only generator scaffold fixtures exist at
  `tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/`.
- The fixture validator module exists at
  `python/learner_state/frozen_policy_generation_generator_scaffold_fixture_validation.py`.
- Validator unit tests exist at
  `python/learner_state/tests/test_frozen_policy_generation_generator_scaffold_fixture_validation.py`.
- The validator CLI exists at:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_generator_scaffold_fixture_validation
```

- CLI tests exist at
  `python/learner_state/tests/test_frozen_policy_generation_generator_scaffold_fixture_validation_cli.py`.
- The CLI root mode validates 18 fixture cases:
  - valid cases: 3
  - invalid cases: 15
  - matched cases: 18
  - mismatched cases: 0
  - input error cases: 0
- The Makefile target does not exist yet.
- Release-quality integration does not exist yet.
- Generator implementation does not exist.
- Artifact writer implementation does not exist.

## 3. Proposed Target Name

Candidate names:

| Candidate | Pros | Cons |
| --- | --- | --- |
| `check-learner-state-frozen-policy-generation-generator-scaffold-fixtures` | Aligns with learner-state targets; explicitly names frozen policy generation generator scaffold fixtures; clear that this is fixture validation. | Long. |
| `check-learner-state-frozen-policy-generation-generator-scaffold` | Shorter while still naming generator scaffold. | Less explicit that the target validates fixtures rather than executing a generator scaffold. |
| `check-frozen-policy-generation-generator-scaffold-fixtures` | Clear and shorter than the learner-state-prefixed option. | Drops the learner-state target family marker used by nearby checks. |
| `check-learner-state-generator-scaffold-fixtures` | Shortest learner-state option. | Too broad; does not say frozen policy generation and could be confused with future learner-state generator fixtures. |

Recommended target:

```text
check-learner-state-frozen-policy-generation-generator-scaffold-fixtures
```

Rationale:

- It matches the learner-state target family.
- It is explicit that these are frozen policy generation generator scaffold
  fixtures.
- It is distinct from
  `check-learner-state-frozen-policy-generation-scaffold-fixtures`, which
  validates the runtime scaffold fixture contract.
- It is distinct from
  `check-learner-state-frozen-policy-generation-scaffold-runtime`, which
  smoke-tests the runtime CLI on one valid fixture pair.
- It is clear that this is a fixture validator target, not generator-quality
  evidence.

## 4. Proposed Command

Recommended command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_generator_scaffold_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold
```

Rationale:

- It uses the CLI root mode.
- It validates all 18 metadata-only generator scaffold fixture cases.
- It prints the safe human summary by default.
- It creates no output file.
- It invokes no generator.
- It writes no artifact.
- It does not expose fixture bodies, request bodies, pointer bodies, expected
  result bodies, artifact bodies, raw rows, logits, private paths, raw learner
  text, or performance metric bodies.

The initial Makefile target should not use `--json`; JSON mode remains useful
for direct CLI checks and future machine consumers, but the first Makefile
target only needs a safe human summary.

## 5. Proposed Help Text

Recommended Makefile help text:

```text
check-learner-state-frozen-policy-generation-generator-scaffold-fixtures  Validate frozen policy generation generator scaffold fixtures
```

The help text should stay short and should not imply generator implementation,
artifact generation, model performance, or real-data readiness.

## 6. Expected Behavior

The future target should:

- run the CLI in fixture-root mode
- exit `0` when the CLI exits `0`
- validate 3 valid cases and 15 fail-closed invalid cases
- report `total_cases=18`
- report `matched_cases=18`
- report `mismatched_cases=0`
- report `input_error_cases=0`
- report `content_suppressed=true`
- report `no_raw_rows=true`
- report `no_logits_dump=true`
- report `no_private_paths=true`
- report `artifact_policy_checked=true`
- report `body_suppression_checked=true`
- report `file_writing_checked=true`
- emit no fixture body output
- emit no request body output
- emit no pointer body output
- emit no expected result body output
- emit no artifact body output
- emit no raw rows
- emit no logits or probability dumps
- emit no private paths
- create no tmp output
- write no artifact
- invoke no generator

Intentional invalid fixtures are successful fixture tests when they fail for
their expected reason code. They contribute to `matched_cases`, not target
failure.

## 7. Exit Code Interpretation

The Makefile target should not transform CLI exit codes.

Expected mapping:

- CLI exit `0`: target pass.
- CLI exit `2`: target fail.
- CLI exit `3`: target fail.
- CLI exit `1`: target fail.

The CLI semantics should remain visible:

- An invalid fixture that matches its expected fail-closed reason exits `0`.
- A usage error or input error exits `2`.
- A readable fixture whose actual validation summary does not match its
  expected result exits `3`.
- An unexpected internal error exits `1`.

## 8. Output / Logging Safety

Allowed output:

- target command echo if consistent with existing Makefile style
- `mode`
- `total_cases`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `reason_code_counts`
- safety flags
- artifact policy flags
- `validation_schema_version`

Forbidden output:

- request body
- pointer body
- expected result body
- artifact body
- generated policy body
- raw rows
- logits
- probabilities
- private paths
- raw learner text
- final text
- observed-after text
- gold label
- performance metric body

The target should rely on the CLI's safe-output behavior and should not add
shell commands that print fixture file contents.

## 9. Tmp / Output Policy

The future target should:

- create no `tmp/` outputs
- write no validation result file
- write no artifact file
- write no generated policy file
- require no cleanup step
- not use `manual_outputs/`

The target should be read-only over the metadata-only synthetic fixture root.

## 10. Relation To Existing Targets

`check-learner-state-frozen-policy-generation-scaffold-fixtures`:

- validates the runtime scaffold fixture contract
- checks 11 scaffold fixture cases
- is already integrated into release-quality

`check-learner-state-frozen-policy-generation-scaffold-runtime`:

- smoke-tests the runtime CLI on one valid fixture pair
- checks metadata-only runtime summary behavior
- is already integrated into release-quality

Proposed target:

- validates the generator scaffold fixture contract
- checks 18 metadata-only generator scaffold fixture cases
- does not execute a generator
- does not write artifacts
- is not yet integrated into release-quality

`check-learner-state-frozen-policy-generation`:

- validates the frozen policy generation validation fixture root
- is separate from generator scaffold fixture contract validation

`check-learner-state-frozen-policy`:

- validates frozen selective prediction policy fixtures
- is separate from generator scaffold fixture contract validation

## 11. Release-Quality Strategy

Do not add this target to release-quality in the same step as target design.

Recommended staging:

1. Implement the standalone Makefile target.
2. Run the standalone target locally.
3. Review stdout/stderr for no-body-leakage.
4. Confirm no tmp output and no artifact writing.
5. Create a separate release-quality integration design.
6. Integrate into the wrapper only after the standalone target is stable.

Success would mean the generator scaffold fixture contract is valid. It would
not mean generator quality, artifact generation, model performance, calibration
quality, selective prediction correctness, learner-state estimator correctness,
real-data readiness, or production readiness.

## 12. Future Tests For Target Implementation

When the target is implemented, check:

- `make help` includes the target
- target exits `0`
- output includes `total_cases=18`
- output includes `matched_cases=18`
- output includes `mismatched_cases=0`
- output includes `input_error_cases=0`
- output includes `content_suppressed=true`
- output includes `no_raw_rows=true`
- output includes `no_logits_dump=true`
- output includes `no_private_paths=true`
- output includes `artifact_policy_checked=true`
- output includes `body_suppression_checked=true`
- output includes `file_writing_checked=true`
- stdout/stderr contain no request body
- stdout/stderr contain no pointer body
- stdout/stderr contain no expected result body
- stdout/stderr contain no artifact body
- stdout/stderr contain no raw rows
- stdout/stderr contain no logits
- stdout/stderr contain no private paths
- no tmp output is created
- Makefile diff is limited to the target and help text
- release-quality wrapper remains unchanged
- GitHub Actions workflows remain unchanged

## 13. No-Oracle / Synthetic-Only Boundary

The future target should use metadata-only synthetic fixtures only.

It must not use:

- real data
- participant data
- raw learner text
- final text
- observed-after text
- gold label
- expected action as scoring feedback
- test-derived tuning payloads
- artifact bodies
- logits
- raw rows
- private paths

The target should preserve:

- `content_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `artifact_policy_checked=true`
- `body_suppression_checked=true`
- `file_writing_checked=true`

## 14. What This Does Not Do

This design does not:

- implement the Makefile target
- change the Makefile
- integrate release-quality
- change GitHub Actions workflows
- change Python code
- change Python tests
- change fixtures
- execute a generator
- write artifacts
- generate artifact bodies
- compute metrics
- evaluate performance
- use real data
- prove production readiness

## 15. Beginner-Friendly Explanation

A Makefile target is a short project command, usually run with `make`, that
wraps a longer command in a memorable name.

The validator CLI already knows how to check the generator scaffold fixture
root. A Makefile target would make that same check easier to run consistently,
especially before later release-quality integration.

This target is different from the runtime scaffold fixture target. The runtime
scaffold target checks the outer runtime fixture contract or one runtime CLI
smoke case. The proposed target checks the generator scaffold fixture contract:
metadata-only plans/results for future generator work.

Invalid fixtures are not target failures when they fail for the expected safe
reason. They exist to prove that the validator recognizes unsafe patterns and
keeps the result fail-closed.

The target should not be added to release-quality immediately because
standalone target behavior and log safety should be reviewed first.

## 16. Next Recommended Steps

Recommended next steps:

- Makefile target implementation
- release-quality integration design
- release-quality wrapper integration
- remote/manual status marker if needed

Generator implementation and artifact writing should remain separate later
work.

## 17. Docs Update

This Step284 document links the implemented metadata-only generator scaffold
fixture validator CLI to a future standalone Makefile target boundary. It does
not add the target, change release-quality, change workflows, change Python
code, change tests, change fixtures, run a generator, write artifacts, expose
artifact bodies, compute metrics, or claim real-data readiness.

Step285 implements the standalone Makefile target:

```text
check-learner-state-frozen-policy-generation-generator-scaffold-fixtures
```

The target runs the safe CLI root mode over
`tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/`.
It is not added to release-quality, does not change workflows, does not change
Python code or tests, does not change fixtures, does not run a generator, does
not write artifacts, and does not expose artifact bodies.

Step286 designs the future release-quality integration for this standalone
target:
[Frozen policy generation generator scaffold fixture validator release-quality integration design](frozen_policy_generation_generator_scaffold_fixture_validator_release_quality_integration_design.md).
The design keeps wrapper implementation, workflow changes, generator execution,
artifact writing, artifact body generation, and performance evaluation out of
scope.

Step288 designs the future remote/manual Release Quality run record workflow:
[Frozen policy generation generator scaffold fixture release-quality remote run record workflow](frozen_policy_generation_generator_scaffold_fixture_release_quality_remote_run_record_workflow.md).
It keeps the actual status marker as future work and records only
pass-only/count-only metadata.

Step290 designs the generator scaffold skeleton:
[Frozen policy generation generator scaffold skeleton design](frozen_policy_generation_generator_scaffold_skeleton_design.md).
The existing Makefile target remains a fixture validator target only and should
not be confused with future generator scaffold runtime smoke targets.

Related docs:

- [Frozen policy generation generator scaffold skeleton design](frozen_policy_generation_generator_scaffold_skeleton_design.md)
- [Frozen policy generation generator scaffold fixture release-quality remote run record workflow](frozen_policy_generation_generator_scaffold_fixture_release_quality_remote_run_record_workflow.md)
- [Frozen policy generation generator scaffold fixture validator release-quality integration design](frozen_policy_generation_generator_scaffold_fixture_validator_release_quality_integration_design.md)
- [Frozen policy generation generator scaffold fixture validator CLI design](frozen_policy_generation_generator_scaffold_fixture_validator_cli_design.md)
- [Frozen policy generation generator scaffold fixture validator design](frozen_policy_generation_generator_scaffold_fixture_validator_design.md)
- [Frozen policy generation generator scaffold fixture design](frozen_policy_generation_generator_scaffold_fixture_design.md)
- [Frozen policy generation generator scaffold fixtures](../tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/README.md)
- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Frozen policy generation artifact policy design](frozen_policy_generation_artifact_policy_design.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)

## 18. Update History

- Step284: initial docs-only Makefile target design for the metadata-only
  generator scaffold fixture validator CLI.
- Step285: recorded standalone Makefile target implementation status; release
  quality integration, workflow changes, generator code, artifact body
  generation, and artifact writing remain out of scope.
- Step286: added docs-only release-quality integration design handoff.
- Step288: added docs-only remote/manual run record workflow handoff.
- Step290: linked the future generator scaffold skeleton design while keeping
  this target scoped to fixture validation.
