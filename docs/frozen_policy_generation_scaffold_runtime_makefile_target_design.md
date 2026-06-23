# Frozen Policy Generation Scaffold Runtime Makefile Target Design

## 1. Purpose

This document designs a future Makefile target for the frozen policy generation
scaffold runtime CLI.

This is a docs-only design. It does not implement a Makefile target, integrate
release-quality, implement generator behavior, add an artifact writer, compute
metrics, evaluate performance, or claim real-data readiness.

The goal is to make the existing safe runtime CLI easy to run from `make` while
preserving the current synthetic-only, no-oracle, metadata-only output boundary.

## 2. Current State

- Runtime API skeleton exists at `python/learner_state/frozen_policy_generation.py`.
- Runtime fixture compatibility tests exist at
  `python/learner_state/tests/test_frozen_policy_generation_scaffold_runtime_fixture_compatibility.py`.
- Runtime CLI exists at:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation
```

- Runtime CLI tests exist at
  `python/learner_state/tests/test_frozen_policy_generation_scaffold_runtime_cli.py`.
- Runtime Makefile target does not exist.
- Runtime release-quality integration does not exist.
- Generator implementation does not exist.
- Artifact writer implementation does not exist.

## 3. Proposed Target Name

Candidate names:

| Candidate | Pros | Cons |
| --- | --- | --- |
| `check-learner-state-frozen-policy-generation-scaffold-runtime` | Aligns with learner-state targets; explicitly names frozen policy generation scaffold runtime; distinct from scaffold fixture validation. | Long. |
| `check-learner-state-frozen-policy-generation-runtime` | Shorter while staying in learner-state naming. | Less explicit that this is scaffold runtime, not future full generator runtime. |
| `check-frozen-policy-generation-scaffold-runtime` | Shorter and clear about scaffold runtime. | Less aligned with existing learner-state target prefix. |
| `check-learner-state-scaffold-runtime` | Shortest learner-state option. | Too broad; does not say frozen policy generation. |

Recommended target:

```text
check-learner-state-frozen-policy-generation-scaffold-runtime
```

Rationale:

- It matches the learner-state target family.
- It is explicit that the target is for frozen policy generation scaffold
  runtime.
- It is clearly distinct from
  `check-learner-state-frozen-policy-generation-scaffold-fixtures`, which
  validates the scaffold fixture contract.
- It reads as a standalone runtime CLI smoke check, not a generator-quality
  check.

## 4. Proposed Command

Recommended initial command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation --request tests/fixtures/learner_state_frozen_policy_generation_scaffold/valid/minimal_fixed_threshold_dry_run/generation_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_scaffold/valid/minimal_fixed_threshold_dry_run/input_fixture_pointer.json
```

This uses the valid minimal fixed-threshold synthetic fixture as a smoke case.

Rationale:

- It verifies that the runtime CLI can be invoked through a short `make`
  command.
- The selected request and pointer are a safe valid fixture pair, so target
  success naturally maps to CLI exit `0` and `scaffold_status=pass`.
- The default human summary is developer-readable and body-free.
- It does not write artifacts.
- It does not call a generator.
- Whole-root expected matching remains covered by the scaffold fixture
  validator and runtime fixture compatibility tests.

Alternatives:

| Option | Benefit | Tradeoff |
| --- | --- | --- |
| Single valid smoke | Minimal, fast, and easy to interpret. | Does not exercise fail-closed invalid output in the target itself. |
| Valid plus one invalid smoke | Confirms both pass and safe fail result behavior through `make`. | Slightly more output; invalid runtime result exits `0`, so target semantics need extra explanation. |
| JSON mode with parse check | Machine-checkable summary. | Requires extra shell parsing or a second command and makes the Makefile target less thin. |
| Multiple fixtures | Broader runtime CLI exercise. | Duplicates fixture validator and compatibility-test coverage. |

Recommended initial target shape:

- Use a single valid smoke case.

The invalid fixture behavior should remain covered by runtime CLI tests and
runtime fixture compatibility tests. If a future target wants broader smoke
coverage, add a second target or a clearly named expanded runtime smoke target
after separate log-safety review.

## 5. Proposed Help Text

Suggested Makefile help entry:

```text
check-learner-state-frozen-policy-generation-scaffold-runtime  Smoke-test frozen policy generation scaffold runtime CLI
```

## 6. Expected Behavior

The future target should:

- run the runtime CLI over the selected synthetic valid request and pointer
- exit `0` when the CLI exits `0`
- print a safe human summary only
- include `mode=scaffold_runtime`
- include `scaffold_status=pass`
- include `content_suppressed=true`
- include `no_raw_rows=true`
- include `generated_artifact_written=false`
- include `generated_artifact_body_available=false`
- include `artifact_body_suppressed=true`
- avoid request body output
- avoid pointer body output
- avoid expected result body output
- avoid artifact body output
- avoid raw rows
- avoid logits or probability dumps
- avoid private paths
- avoid raw learner text
- avoid performance claims
- create no tmp output
- write no artifact file

## 7. Exit Code Interpretation

The Makefile target should not transform CLI exit codes.

Expected mapping:

- Runtime CLI exit `0`: target pass.
- Runtime CLI exit `2`: target fail.
- Runtime CLI exit `1`: target fail.
- Runtime CLI exit `3`: reserved for a future expected-output comparison mode;
  target fail if it ever appears.

Runtime CLI invalid fail-closed results can still exit `0`, but the proposed
initial target uses a valid fixture. Therefore the target output should include
`scaffold_status=pass`.

## 8. Output / Logging Safety

Allowed output:

- target command echo if consistent with existing Makefile style
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
- safe summary label

Forbidden output:

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
- performance claims

The target should rely on the CLI's existing safe summary behavior and should
not add shell commands that print file contents.

## 9. Tmp / Output Policy

The future target should:

- create no `tmp/` outputs
- write no artifact file
- write no validation result file
- require no cleanup step
- not use `manual_outputs/`
- not create a generated policy body

This target is a read-only smoke check over a synthetic fixture pair.

## 10. Relation To Existing Targets

`check-learner-state-frozen-policy-generation-scaffold-fixtures`:

- validates the scaffold fixture root contract using the scaffold fixture
  validator
- checks valid 3 and invalid 8 expected outcomes
- is already included in release-quality

Proposed runtime target:

- smoke-tests the runtime CLI on one safe fixture pair
- confirms terminal invocation and safe summary behavior
- does not perform fixture-root expected matching

`check-learner-state-frozen-policy-generation`:

- validates the separate frozen policy generation validation fixture root
- is not the scaffold runtime CLI smoke target

Release-quality currently includes the scaffold fixture validator target only.
The runtime target should not be added to release-quality yet.

## 11. Release-Quality Future

Release-quality integration is not part of this step.

Recommended staging:

1. Implement the standalone Makefile target.
2. Run the target locally and verify safe output.
3. Confirm no tmp output and no artifact writing.
4. Confirm Makefile diff is limited.
5. Create a release-quality integration design.
6. Integrate the wrapper only after standalone log safety is stable.

Success of the future target is runtime CLI smoke and safety evidence. It is
not generator quality, policy quality, model performance, calibration quality,
or real-data readiness evidence.

## 12. Future Tests For Target Implementation

Future implementation checks:

- `make help` includes the target.
- The target exits `0`.
- Target output includes `scaffold_status=pass`.
- Target output includes `content_suppressed=true`.
- Target output includes `no_raw_rows=true`.
- Target output includes `generated_artifact_written=false`.
- Target output includes `generated_artifact_body_available=false`.
- Target stdout and stderr contain no body leakage.
- No tmp output is created by this target.
- Makefile diff is limited.
- release-quality wrapper remains unchanged.
- GitHub Actions workflows remain unchanged.
- Existing Python tests pass.
- Existing scaffold fixture validator target still passes.

## 13. No-Oracle / Synthetic-Only Boundary

The target should use only the synthetic scaffold fixture pair.

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

The target is a synthetic-only runtime CLI smoke check.

## 14. What This Does NOT Do

This design does not:

- implement the Makefile target
- change the Makefile
- integrate release-quality
- change GitHub Actions workflows
- implement generator behavior
- write artifacts
- create artifact bodies
- compute metrics
- evaluate performance
- use real data
- prove production readiness

## 15. Beginner-Friendly Explanation

A Makefile target is a short named command. Instead of typing a long Python
command, a developer can type one `make` command.

The runtime CLI target is different from the scaffold fixture validator target.
The fixture validator target checks the whole fixture contract and expected
pass/fail outcomes. The runtime CLI target only proves that the runtime CLI can
run safely on one synthetic request and pointer pair.

The first target should be a smoke target because the runtime is still a
scaffold. A small smoke check is enough to verify the command boundary without
pretending the generator exists.

The target should not enter release-quality immediately because standalone
logging behavior and Makefile output need to be reviewed first.

Passing the target does not mean generator quality. No generator runs, no
policy artifact is written, and no performance metric is computed.

## 16. Next Recommended Steps

Recommended next step:

- remote/manual status marker design if needed

Then proceed with:

- remote/manual status marker after a safe run if needed

Generator implementation should remain separate.

## 17. Step270 Implementation Status

The standalone Makefile target now exists:

```bash
make check-learner-state-frozen-policy-generation-scaffold-runtime
```

It runs the runtime CLI over the synthetic
`valid/minimal_fixed_threshold_dry_run` request and pointer pair and emits the
runtime CLI's safe human summary.

The implemented command is:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation --request tests/fixtures/learner_state_frozen_policy_generation_scaffold/valid/minimal_fixed_threshold_dry_run/generation_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_scaffold/valid/minimal_fixed_threshold_dry_run/input_fixture_pointer.json
```

The implementation does not add release-quality runtime integration, GitHub
Actions workflow changes, Python code changes, Python test changes, fixture
changes, generator behavior, artifact writing, artifact body generation,
metric computation, real-data use, or performance claims.

## 18. Step271 Follow-Up

[Frozen policy generation scaffold runtime release-quality integration design](frozen_policy_generation_scaffold_runtime_release_quality_integration_design.md)
defines the future wrapper placement, command, label, expected behavior,
failure interpretation, log-safety review, and testing plan for adding the
standalone runtime target to release-quality. It remains docs-only and does
not change the wrapper, workflows, Makefile, Python code, tests, fixtures,
generator behavior, artifact writing, metrics, real-data use, or performance
claims.

## 19. Step272 Implementation Status

The release-quality wrapper now calls
`make check-learner-state-frozen-policy-generation-scaffold-runtime` after
scaffold fixture validation and before config/scoring smoke checks. The wrapper
label is:

```text
release_quality_check: learner-state frozen policy generation scaffold runtime smoke
```

The integration does not change GitHub Actions workflows, the Makefile, Python
code, tests, fixtures, generator behavior, artifact writing, metric
computation, real-data use, or performance claims.

## 20. Update History

- Step269: initial docs-only runtime CLI Makefile target design.
- Step270: recorded the standalone runtime CLI Makefile target implementation
  status.
- Step271: linked the docs-only runtime release-quality integration design.
- Step272: recorded release-quality wrapper integration status for the runtime
  smoke target.

## Related Documents

- [Frozen policy generation scaffold runtime release-quality integration design](frozen_policy_generation_scaffold_runtime_release_quality_integration_design.md)
- [Frozen policy generation scaffold runtime release-quality remote run record workflow](frozen_policy_generation_scaffold_runtime_release_quality_remote_run_record_workflow.md)
- [Frozen policy generation scaffold runtime CLI design](frozen_policy_generation_scaffold_runtime_cli_design.md)
- [Frozen policy generation scaffold runtime API design](frozen_policy_generation_scaffold_runtime_api_design.md)
- [Frozen policy generation scaffold runtime fixture compatibility test design](frozen_policy_generation_scaffold_runtime_fixture_compatibility_test_design.md)
- [Frozen policy generation scaffold runtime fixture alignment design](frozen_policy_generation_scaffold_runtime_fixture_alignment_design.md)
- [Milestone 12 frozen policy generation scaffold fixture validation recap](milestone_12_frozen_policy_generation_scaffold_fixture_validation_recap.md)
- [Frozen policy generation scaffold fixture validator Makefile target design](frozen_policy_generation_scaffold_fixture_validator_makefile_target_design.md)
- [Frozen policy generation scaffold fixture validator release-quality integration design](frozen_policy_generation_scaffold_fixture_validator_release_quality_integration_design.md)
- `python/learner_state/frozen_policy_generation.py`
- `python/learner_state/tests/test_frozen_policy_generation_scaffold_runtime_cli.py`
- [Public release checklist](public_release_checklist.md)
