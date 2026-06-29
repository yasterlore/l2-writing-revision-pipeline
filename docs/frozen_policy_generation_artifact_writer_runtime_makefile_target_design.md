# Frozen Policy Generation Artifact Writer Runtime Makefile Target Design

## 1. Purpose

This document originally designed the Makefile runtime smoke target for the
frozen policy generation artifact writer CLI.

Step316 was docs-only design. Later steps implemented the standalone target
and release-quality wrapper integration. This document still does not define
artifact body generation, generated policy body generation, manifest body
generation, file writing, metric computation, performance evaluation, or
real-data readiness.

The goal is to make the Step315 artifact writer CLI easy to run with a short
`make` command while preserving the current synthetic-only, metadata-only,
body-suppressed, file-writing-free boundary.

## 2. Current State

- The artifact writer metadata-only skeleton exists.
- The artifact writer CLI exists.
- Artifact writer CLI tests exist.
- The artifact writer fixture validator target exists.
- The artifact writer fixture validator target is included in
  release-quality.
- The artifact writer runtime Makefile target exists.
- Artifact writer runtime release-quality integration exists.
- Artifact body generation does not exist.
- Manifest generation does not exist.
- Artifact file writing and manifest file writing do not exist.

Current CLI entrypoint:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer
```

## 3. Proposed Target Name

Candidate names:

| Candidate | Pros | Cons |
| --- | --- | --- |
| `check-learner-state-frozen-policy-generation-artifact-writer-runtime` | Aligns with the learner-state namespace; clearly names frozen policy generation artifact writer runtime smoke; mirrors generator scaffold runtime target naming. | Long. |
| `check-frozen-policy-generation-artifact-writer-runtime` | Shorter while still naming the artifact writer runtime. | Drops the learner-state target namespace used by nearby checks. |
| `check-learner-state-artifact-writer-runtime` | Shorter learner-state option. | Too broad; does not say frozen policy generation. |
| `check-learner-state-frozen-policy-generation-artifact-runtime` | Keeps learner-state and frozen policy generation. | Blurs the difference between artifact writer runtime and a future artifact-generation runtime. |

Recommended target:

```text
check-learner-state-frozen-policy-generation-artifact-writer-runtime
```

Reasons:

- It stays inside the learner-state target namespace.
- It clearly identifies the frozen policy generation pipeline.
- It says this is an artifact writer runtime smoke, not a fixture validator.
- It aligns with the existing generator scaffold runtime target style.
- It will be easy to reference from a future release-quality label.

## 4. Proposed Command

Recommended command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer --request tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/valid/minimal_metadata_only_artifact_plan/artifact_writer_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/valid/minimal_metadata_only_artifact_plan/generator_result_pointer.json
```

The target should use the valid minimal metadata-only artifact plan fixture.
The default safe human summary is preferred for the initial target because it
matches the nearby runtime smoke targets and avoids additional shell parsing.

The target should call the CLI directly and should not duplicate writer logic
in the Makefile.

## 5. Proposed Help Text

Recommended help text:

```text
check-learner-state-frozen-policy-generation-artifact-writer-runtime  Run frozen policy generation artifact writer runtime smoke
```

## 6. Expected Behavior

The future target should:

- run the artifact writer CLI on one valid synthetic fixture
- exit `0`
- print `mode=artifact_writer`
- print `writer_status=pass`
- print `reason_codes=none`
- print `failed_checks=none`
- show artifact body unavailable or suppressed metadata
- show manifest body unavailable or suppressed metadata
- show artifact writing as false
- show manifest writing as false
- avoid generated policy body output
- avoid raw rows
- avoid logits or probability dumps
- avoid private paths
- avoid performance metric bodies
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
- create no tmp output
- write no artifact file
- write no manifest file
- provide no performance evidence

## 7. Exit Code Interpretation

The Makefile target should not transform CLI exit codes.

Expected mapping:

- CLI exit `0`: target pass.
- CLI exit `2`: target fail because of usage or input loading error.
- CLI exit `1`: target fail because of unexpected internal error or safety
  audit failure.
- CLI exit `3`: reserved for future expected-result comparison; target fail
  if it ever appears.

The runtime smoke target should use one valid synthetic fixture only. Invalid
fail-closed fixture behavior remains covered by writer CLI tests and the
fixture validator contract.

## 8. Output And Logging Safety

Allowed output:

- `mode`
- `writer_status`
- `reason_codes`
- `failed_checks`
- safe request, pointer, artifact, and manifest IDs
- artifact flags
- safety flags
- count summary
- safe summary label
- validation schema version

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

The target should print only the CLI's safe metadata summary. It should not add
shell commands that print fixture contents, raw log blocks, copied workflow
output, or any body payload.

## 9. Tmp And Output Policy

The future target should:

- create no tmp outputs
- write no validation result file
- write no artifact file
- write no manifest file
- require no cleanup step
- not use `manual_outputs/`

The target is a read-only runtime smoke over one synthetic fixture pair.

## 10. Relation To Existing Targets

`check-learner-state-frozen-policy-generation-artifact-writer-fixtures`:

- validates the 17-case artifact writer fixture contract
- checks valid and invalid expected metadata outcomes
- is already included in release-quality

Proposed runtime target:

- runs one valid synthetic request/pointer pair through the writer CLI
- confirms terminal invocation and safe runtime summary behavior
- does not perform fixture-root expected matching

Related runtime targets:

- `check-learner-state-frozen-policy-generation-generator-scaffold-runtime`
  runs the generator scaffold CLI smoke.
- `check-learner-state-frozen-policy-generation-scaffold-runtime` runs the
  earlier runtime scaffold CLI smoke.

The artifact writer runtime target should mirror the generator scaffold
runtime target's safety style.

Success would not mean:

- artifact writer implementation quality
- artifact generation evidence
- manifest generation evidence
- generated policy quality
- model performance evidence
- production readiness

## 11. Future Tests For Target Implementation

When the target is implemented, future checks should verify:

- `make help` includes the target.
- the target exits `0`
- output includes `mode=artifact_writer`
- output includes `writer_status=pass`
- output includes `reason_codes=none`
- output includes `failed_checks=none`
- output includes artifact body suppression flags
- output includes manifest body suppression flags
- output includes `file_writing_checked=true`
- output includes `manifest_body_suppression_checked=true`
- stdout and stderr contain no request body
- stdout and stderr contain no pointer body
- stdout and stderr contain no expected result body
- stdout and stderr contain no artifact body
- stdout and stderr contain no manifest body
- stdout and stderr contain no raw rows
- stdout and stderr contain no logits
- stdout and stderr contain no private paths
- the target creates no tmp output
- the Makefile diff is limited
- release-quality wrapper remains unchanged until a later integration step
- workflow YAML remains unchanged

## 12. Release-Quality Strategy

Do not add this target to release-quality in the Makefile implementation step.

Recommended staging:

1. Implement the standalone runtime Makefile target.
2. Run the standalone target locally.
3. Review no-body-leakage behavior.
4. Confirm no tmp output, no artifact writing, and no manifest writing.
5. Design release-quality integration separately.
6. Integrate the wrapper only after the standalone target is stable.

Suggested future insertion point:

- after artifact writer fixture validation
- before config and scoring smoke checks

Release-quality success would mean the metadata-only artifact writer runtime
smoke passed. It would still not mean artifact body generation, manifest
generation, artifact writer quality, model performance, or real-data
readiness.

## 13. Status Marker Future

After future release-quality integration and a remote/manual Release Quality
success, a future status marker may record:

- artifact writer runtime target included yes/no
- `mode=artifact_writer`
- `writer_status=pass`
- artifact writing false
- manifest writing false
- artifact body suppressed true
- manifest body suppressed true
- safety flags

The marker must not include raw logs, request bodies, pointer bodies, expected
result bodies, artifact bodies, policy bodies, manifest bodies, raw rows,
logits, private paths, or raw learner text.

## 14. No-Oracle / Synthetic-Only Boundary

The future target should stay inside this boundary:

- synthetic fixture metadata only
- no real data
- no participant data
- no raw learner text
- no final, gold, or observed-after text
- no expected action scoring feedback
- no test-derived tuning payload
- no artifact body
- no generated policy body
- no manifest body
- no logits
- no raw rows
- no private paths

## 15. What This Does NOT Do

This design does not:

- implement a Makefile target
- integrate release-quality
- write artifacts
- write manifests
- generate artifact bodies
- generate generated policy bodies
- compute metrics
- evaluate performance
- use real data
- prove production readiness

## 16. Beginner-Friendly Explanation

A Makefile target is a named shortcut for a terminal command. Instead of
typing the full Python CLI command every time, a future target would let a
developer run one short `make` command.

The runtime target comes after the CLI because the CLI is the stable terminal
entrypoint. The Makefile should stay thin and call that CLI rather than
reimplementing writer behavior.

The fixture validator target and runtime smoke target are different. The
fixture validator checks all 17 fixture contracts. The runtime smoke target
should run one valid synthetic fixture through the actual writer CLI and
confirm that it returns a safe pass summary.

One valid fixture is enough for the initial runtime smoke because full valid
and invalid coverage is already handled by tests and the fixture validator.
Using only one valid fixture keeps the make target fast, readable, and easy to
interpret.

Release-quality integration was added later after standalone target output and
no-body-leakage behavior were reviewed.

Artifact body and file-writing behavior remain out of scope because the current
artifact policy is metadata-only and file-writing-free. Adding those behaviors
would require a separate design, implementation, and safety review.

## 17. Next Recommended Steps

- Step321 remote/manual run status marker

## 18. Step317 Runtime Makefile Target Implementation Status

Step317 implements the standalone target designed here:

```text
check-learner-state-frozen-policy-generation-artifact-writer-runtime
```

Implemented command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer --request tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/valid/minimal_metadata_only_artifact_plan/artifact_writer_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/valid/minimal_metadata_only_artifact_plan/generator_result_pointer.json
```

The target is added to `Makefile` and `make help`. It runs one valid synthetic
request/pointer pair and emits the existing safe artifact writer CLI human
summary.

Step317 does not add the target to release-quality, change workflow YAML,
change Python code or tests, change fixture JSON, generate artifact bodies,
generate generated policy bodies, generate manifest bodies, write artifact or
manifest files, compute metrics, use real data, or claim real-data readiness.

## 19. Step318 Runtime Release-Quality Integration Design Status

Step318 designs future release-quality wrapper integration for this standalone
runtime target:

[Frozen policy generation artifact writer runtime release-quality integration design](frozen_policy_generation_artifact_writer_runtime_release_quality_integration_design.md).

Step318 does not change the release-quality wrapper, workflow YAML, Makefile,
Python code or tests, fixture JSON, artifact body generation, generated policy
body generation, manifest body generation, artifact or manifest file writing,
metrics, real-data use, or real-data readiness status.

Next recommended steps:

- Step321 remote/manual run status marker

## 20. Step319 Runtime Release-Quality Wrapper Integration Status

Step319 integrates this standalone runtime target into the release-quality
wrapper. The wrapper now runs:

```text
check-learner-state-frozen-policy-generation-artifact-writer-runtime
```

The section is placed after artifact writer fixture validation and before
config/scoring smoke checks. Step319 does not change workflow YAML, change the
Makefile target, change Python code or tests, change fixture JSON, generate
artifact bodies, generate generated policy bodies, generate manifest bodies,
write artifact or manifest files, compute metrics, use real data, or claim
real-data readiness.

## 21. Step320 Remote Run Record Workflow Design Status

Step320 designs the future public-safe remote/manual Release Quality run
recording workflow for this runtime target:

[Frozen policy generation artifact writer runtime release-quality remote run record workflow](frozen_policy_generation_artifact_writer_runtime_release_quality_remote_run_record_workflow.md).

The future status marker should record only pass-only metadata for this
runtime smoke and count-only metadata for related fixture validators. It must
not copy raw logs, request bodies, pointer bodies, expected result bodies,
artifact bodies, manifest bodies, raw rows, logits, private paths, raw learner
text, or performance metric bodies.

## 22. Step321 Runtime Status Marker Creation Status

Step321 creates the public-safe remote/manual Release Quality status marker
for this runtime target:

[Learner-state frozen policy generation artifact writer runtime release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_writer_runtime_release_quality_remote_run_status.md).

The marker records pass-only runtime smoke metadata and count-only related
fixture validation metadata. It does not change the Makefile target, change
workflow YAML, change the release-quality wrapper, change Python code or
tests, change fixture JSON, generate artifact bodies, generate generated
policy bodies, generate manifest bodies, write files, compute metrics, use
real data, or claim real-data readiness.

## 23. Step322 Artifact Body Generation Design Status

Step322 designs future artifact body generation separately from this runtime
target:

[Frozen policy generation artifact body generation design](frozen_policy_generation_artifact_body_generation_design.md).

The runtime target remains body-free and file-writing-free. Step322 does not
change the Makefile target, release-quality wrapper, workflow YAML, Python
code or tests, fixture JSON, CLI behavior, artifact body generation, manifest
body generation, file writing, metrics, real-data use, or production
readiness status.

## 24. Step323 Artifact Body Fixture Design Status

Step323 designs future artifact body fixtures separately from this runtime
target:

[Frozen policy generation artifact body fixture design](frozen_policy_generation_artifact_body_fixture_design.md).

The runtime target remains body-free and file-writing-free. Step323 does not
create fixture JSON, implement a validator, change the Makefile target, change
the release-quality wrapper, change workflow YAML, change Python code or
tests, change existing fixtures, generate artifact bodies, write files,
compute metrics, use real data, or claim production readiness.

## 25. Step324 Artifact Body Fixture Creation Status

Step324 creates the artifact body fixture root:

[Frozen policy generation artifact body fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body/README.md).

The runtime target remains unchanged, body-free, and file-writing-free. The
new fixtures are for future artifact body validation only and are not added to
Makefile targets in Step324.

## 26. Step466 Artifact Writer CLI Integration Design Status

Step466 adds the docs-only design for a future artifact writer CLI integration
boundary:

[Frozen policy generation artifact writer CLI integration design](frozen_policy_generation_artifact_writer_cli_integration_design.md).

The standalone runtime target remains unchanged and should not be replaced by
the future integration target. Any future artifact writer CLI integration
target should use a separate label and should be staged only after fixture
contract and validator work. Step466 does not change Makefile, release-quality
wrapper, workflow YAML, Python code/tests, fixtures JSON, artifact body
generation CLI integration, manifest body generation, metrics, real-data use,
or production readiness.
