# Frozen Policy Generation Generator Scaffold CLI Makefile Target Design

## 1. Purpose

This document designs a future Makefile target for the frozen policy generation
generator scaffold CLI.

This is a docs-only design. It does not implement a Makefile target, change the
Makefile, integrate release-quality, change a workflow, change Python code,
change tests, change fixtures, add an artifact writer, generate artifact
bodies, generate policy bodies, write files, compute metrics, evaluate
performance, or claim real-data readiness.

The goal is to make the implemented metadata-only generator scaffold CLI easy
to run from `make` while preserving the current synthetic-only, no-oracle,
body-free output boundary.

## 2. Current State

- The metadata-only generator scaffold skeleton exists at
  `python/learner_state/frozen_policy_generation_generator_scaffold.py`.
- The generator scaffold CLI exists at:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_generator_scaffold
```

- Skeleton tests and CLI tests exist.
- The generator scaffold fixture validator Makefile target exists:
  `check-learner-state-frozen-policy-generation-generator-scaffold-fixtures`.
- The generator scaffold fixture validator target is integrated into
  release-quality.
- The generator scaffold CLI runtime Makefile target does not exist yet.
- Generator scaffold CLI runtime release-quality integration does not exist
  yet.
- Artifact writer implementation does not exist.
- Artifact body generation, generated policy body generation, artifact
  manifest writing, metric computation, and performance evaluation do not
  exist in this path.

## 3. Proposed Target Name

Candidate names:

| Candidate | Pros | Cons |
| --- | --- | --- |
| `check-learner-state-frozen-policy-generation-generator-scaffold-runtime` | Aligns with the existing runtime scaffold target; clearly reads as a generator scaffold CLI smoke; stays in the learner-state frozen policy generation target family. | Long. |
| `check-learner-state-frozen-policy-generation-generator-scaffold` | Shorter while still naming the generator scaffold. | Less explicit that this is a runtime smoke target rather than fixture validation or broader generator validation. |
| `check-learner-state-frozen-policy-generation-generator-scaffold-cli` | Explicit that it calls the CLI. | Less aligned with the existing `*-runtime` naming used for runtime smoke checks. |
| `check-frozen-policy-generation-generator-scaffold-runtime` | Shorter and still clear about runtime smoke. | Drops the learner-state target family prefix used by nearby checks. |

Recommended target:

```text
check-learner-state-frozen-policy-generation-generator-scaffold-runtime
```

Rationale:

- It matches the learner-state target family.
- It mirrors `check-learner-state-frozen-policy-generation-scaffold-runtime`.
- It is distinct from
  `check-learner-state-frozen-policy-generation-generator-scaffold-fixtures`,
  which validates the generator scaffold fixture contract.
- It reads as a runtime CLI smoke check, not generator-quality evidence.

## 4. Proposed Command

Minimal valid-only smoke:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_generator_scaffold --request tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/valid/minimal_metadata_only_generation_plan/generation_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/valid/minimal_metadata_only_generation_plan/input_fixture_pointer.json
```

Alternative considered: add one expected fail-closed invalid smoke:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_generator_scaffold --request tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/invalid/test_temperature_tuning/generation_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/invalid/test_temperature_tuning/input_fixture_pointer.json
```

Recommended initial target shape:

- run only the valid synthetic case
- keep invalid expected fail-closed behavior covered by CLI tests and the
  generator scaffold fixture validator target
- keep the Makefile target short and easy to interpret
- keep future release-quality logs shorter if the target is later integrated

The target should use default safe human output. It should not pass `--json`
and should not add parsing, output-file, artifact-body, artifact-writing, or
manifest-writing options.

## 5. Proposed Help Text

Recommended Makefile help text:

```text
check-learner-state-frozen-policy-generation-generator-scaffold-runtime  Run frozen policy generation generator scaffold runtime smoke
```

The help text should not imply artifact generation, policy body generation,
model performance, or real-data readiness.

## 6. Expected Behavior

The future valid-only smoke target should:

- run the generator scaffold CLI over one valid synthetic request/pointer pair
- exit `0` when the CLI exits `0`
- include `mode=generator_scaffold`
- include `generation_status=pass`
- include `reason_codes=none`
- include `failed_checks=none`
- include `content_suppressed=true`
- include `no_raw_rows=true`
- include `no_logits_dump=true`
- include `no_private_paths=true`
- include `artifact_policy_checked=true`
- include `body_suppression_checked=true`
- include `file_writing_checked=true`
- include `generated_artifact_written=false`
- include `generated_artifact_body_available=false`
- include `artifact_body_suppressed=true`
- emit no request body output
- emit no pointer body output
- emit no expected result body output
- emit no artifact body output
- emit no generated policy body output
- emit no raw rows
- emit no logits or probability dumps
- emit no private paths
- create no tmp output
- write no artifact
- invoke no artifact writer

This target is a runtime smoke check. It should not attempt whole-root expected
matching, because that belongs to the existing fixture validator target.

## 7. Exit Code Interpretation

The Makefile target should not transform CLI exit codes.

Expected mapping:

- CLI exit `0`: target pass.
- CLI exit `2`: target fail.
- CLI exit `3`: target fail.
- CLI exit `1`: target fail.

The initial target should not include an invalid expected fail-closed fixture.
Expected invalid fail-closed behavior remains covered by CLI tests and fixture
validator checks.

## 8. Output / Logging Safety

Allowed output:

- target command echo if consistent with existing Makefile style
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
- gold label
- performance metric body

The target should rely on the CLI safe summary and should not add shell
commands that print fixture file contents.

## 9. Tmp / Output Policy

The future target should:

- create no `tmp/` outputs
- write no validation result file
- write no artifact file
- write no generated policy file
- require no cleanup step
- not use `manual_outputs/`

The target should be read-only over the synthetic metadata-only fixture pair.

## 10. Relation To Existing Targets

`check-learner-state-frozen-policy-generation-generator-scaffold-fixtures`:

- validates the generator scaffold fixture contract
- checks all 18 metadata-only fixture cases
- includes valid cases and expected fail-closed invalid cases
- is already integrated into release-quality

Proposed target:

- runs the generator scaffold CLI on one valid synthetic request/pointer pair
- confirms terminal invocation and safe runtime summary behavior
- does not perform fixture-root expected matching
- is not yet integrated into release-quality

`check-learner-state-frozen-policy-generation-scaffold-runtime`:

- runs the earlier frozen policy generation scaffold runtime CLI smoke
- is separate from the generator scaffold CLI smoke

`check-learner-state-frozen-policy-generation-scaffold-fixtures`:

- validates the earlier scaffold fixture contract
- is separate from the generator scaffold fixture validator target

## 11. Future Tests For Target Implementation

When the target is implemented, future checks should confirm:

- `make help` includes the target and help text
- the target exits `0`
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
- stdout/stderr include no request body
- stdout/stderr include no pointer body
- stdout/stderr include no expected result body
- stdout/stderr include no generated policy body
- stdout/stderr include no artifact body
- stdout/stderr include no raw rows
- stdout/stderr include no logits
- stdout/stderr include no private paths
- no tmp output is created
- Makefile diff is limited to the standalone target and help text
- release-quality wrapper and workflow diffs remain unchanged

## 12. Release-Quality Strategy

Do not add this target to release-quality in the same step that implements the
Makefile target.

Recommended staging:

1. Implement the standalone Makefile target.
2. Run the standalone target.
3. Review no-body-leakage and no-output-writing behavior.
4. Design release-quality integration separately.
5. Integrate only after the standalone target is stable.

Future release-quality success would mean the metadata-only generator scaffold
runtime smoke is safe. It would still not mean generator quality, artifact
generation correctness, policy quality, model performance, calibration quality,
real-data readiness, or production readiness.

## 13. Status Marker Future

After a future release-quality integration and remote/manual success, a status
marker may record pass-only or count-only metadata such as:

- target included: yes/no
- target name
- wrapper label
- `mode=generator_scaffold`
- `generation_status=pass`
- artifact/body/file-writing flags
- content suppressed
- no raw rows
- no logits
- no private paths

The marker must not copy raw logs, request bodies, pointer bodies, expected
result bodies, artifact bodies, generated policy bodies, raw rows, logits,
private paths, raw learner text, or performance metric bodies.

## 14. No-Oracle / Synthetic-Only Boundary

The target should remain inside the existing boundary:

- synthetic fixtures only
- no real data
- no participant data
- no raw learner text
- no final text
- no gold labels
- no observed-after text
- no expected-action scoring feedback payloads
- no test-derived tuning payloads
- no artifact body
- no logits
- no raw rows
- no private paths

## 15. What This Does NOT Do

This document does not:

- implement a Makefile target
- integrate release-quality
- change workflows
- write artifacts
- generate policy bodies
- generate artifact bodies
- write an artifact manifest
- compute metrics
- evaluate performance
- use real data
- prove production readiness

## 16. Beginner-Friendly Explanation

A Makefile target is a short command name that runs a longer command. It gives
developers a consistent way to run the same smoke check locally.

The generator scaffold CLI already runs the metadata-only skeleton on one
request and pointer. A Makefile target would make that command easier to run
and easier to include in a later quality wrapper.

The fixture validator target and runtime smoke target are different. The
fixture validator checks whether all fixture cases have the expected metadata
contract. The runtime smoke target checks that the CLI can run one safe
synthetic request/pointer pair and print a safe summary.

The first target should be valid-only because fail-closed invalid behavior is
already covered by focused CLI tests and the fixture validator target. Keeping
the smoke short reduces log surface and review burden.

Release-quality should come later because adding a new standalone target and
adding it to the release wrapper are separate safety reviews.

## 17. Next Recommended Steps

Recommended next steps:

- Step295: generator scaffold CLI Makefile target implementation
- Step296: generator scaffold runtime release-quality integration design
- Step297: generator scaffold runtime wrapper integration
- Step298: generator scaffold runtime remote run record workflow design

Keep artifact writing, generated policy bodies, calibration work, performance
evaluation, and real-data readiness separate.

## 18. Step295 Implementation Status

Step295 implements the standalone Makefile target:

```text
check-learner-state-frozen-policy-generation-generator-scaffold-runtime
```

The target command is:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_generator_scaffold --request tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/valid/minimal_metadata_only_generation_plan/generation_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/valid/minimal_metadata_only_generation_plan/input_fixture_pointer.json
```

The Makefile help text is:

```text
check-learner-state-frozen-policy-generation-generator-scaffold-runtime  Run frozen policy generation generator scaffold runtime smoke
```

The implementation:

- runs one valid synthetic request/pointer pair
- returns `mode=generator_scaffold`
- returns `generation_status=pass`
- returns `reason_codes=none`
- returns `failed_checks=none`
- keeps content suppressed
- keeps raw rows, logits, and private paths out of output
- keeps artifact body and generated policy body unavailable
- keeps artifact file writing disabled
- creates no target-specific tmp output
- does not add release-quality integration
- does not change workflows
- does not change Python code, tests, or fixtures

Release-quality integration for this runtime smoke remains a future staged
step.

## 19. Step296 Release-Quality Integration Design Status

Step296 designs future release-quality integration for the standalone runtime
smoke target:
[Frozen policy generation generator scaffold runtime release-quality integration design](frozen_policy_generation_generator_scaffold_runtime_release_quality_integration_design.md).

The design recommends placing the runtime smoke immediately after generator
scaffold fixture validation and before config/scoring smoke checks. Step296 is
docs-only: it does not change the wrapper, workflows, Makefile, Python code,
tests, fixtures, artifact writing, artifact bodies, generated policy bodies,
metrics, or real-data readiness status.

## 20. Step297 Release-Quality Wrapper Integration Status

Step297 implements that wrapper integration by adding
`make check-learner-state-frozen-policy-generation-generator-scaffold-runtime`
to `scripts/check_release_quality.sh` immediately after generator scaffold
fixture validation and before config/scoring smoke checks.

The Makefile target itself remains unchanged. The integration does not change
GitHub Actions workflows, Python code, tests, fixtures, artifact writing,
artifact bodies, generated policy bodies, metrics, or real-data readiness
status.

## 21. Step298 Remote Run Record Workflow Design Status

Step298 designs the future public-safe remote/manual Release Quality run record
workflow for this runtime smoke:
[Frozen policy generation generator scaffold runtime release-quality remote run record workflow](frozen_policy_generation_generator_scaffold_runtime_release_quality_remote_run_record_workflow.md).

The workflow design is docs-only and does not create the future status marker.

## 22. Step299 Remote Run Status Marker

Step299 creates the public-safe remote/manual Release Quality status marker for
the generator scaffold runtime smoke:
[Learner-state frozen policy generation generator scaffold runtime release-quality remote run status](status/learner_state_frozen_policy_generation_generator_scaffold_runtime_release_quality_remote_run_status.md).

The status marker records only metadata, pass-only runtime smoke fields, and
count-only fixture validation summaries. It does not copy raw logs or
content-bearing request, pointer, policy, generated policy, or artifact bodies.

## Related Documents

- [Frozen policy generation generator scaffold runtime release-quality remote run record workflow](frozen_policy_generation_generator_scaffold_runtime_release_quality_remote_run_record_workflow.md)
- [Learner-state frozen policy generation generator scaffold runtime release-quality remote run status](status/learner_state_frozen_policy_generation_generator_scaffold_runtime_release_quality_remote_run_status.md)
- [Frozen policy generation generator scaffold runtime release-quality integration design](frozen_policy_generation_generator_scaffold_runtime_release_quality_integration_design.md)
- [Frozen policy generation generator scaffold CLI design](frozen_policy_generation_generator_scaffold_cli_design.md)
- [Frozen policy generation generator scaffold skeleton design](frozen_policy_generation_generator_scaffold_skeleton_design.md)
- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Frozen policy generation artifact policy design](frozen_policy_generation_artifact_policy_design.md)
- [Frozen policy generation generator scaffold fixture design](frozen_policy_generation_generator_scaffold_fixture_design.md)
- [Frozen policy generation generator scaffold fixture validator Makefile target design](frozen_policy_generation_generator_scaffold_fixture_validator_makefile_target_design.md)
- [Frozen policy generation generator scaffold fixture validator release-quality integration design](frozen_policy_generation_generator_scaffold_fixture_validator_release_quality_integration_design.md)
- [Learner-state frozen policy generation generator scaffold fixture release-quality remote run status](status/learner_state_frozen_policy_generation_generator_scaffold_fixture_release_quality_remote_run_status.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)
