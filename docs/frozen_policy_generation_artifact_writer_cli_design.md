# Frozen Policy Generation Artifact Writer CLI Design

## 1. Purpose

This document designs a future CLI for the frozen policy generation artifact
writer metadata-only skeleton.

This is a CLI design, not a CLI implementation. It does not generate artifact
bodies, generate policy bodies, generate manifest bodies, write artifact
files, write manifest files, compute metrics, evaluate performance, use real
data, or claim real-data readiness.

The design keeps the first terminal-facing writer path synthetic-only,
metadata-only, deterministic, and fail-closed.

## 2. Current State

- The metadata-only artifact writer skeleton exists at
  `python/learner_state/frozen_policy_generation_artifact_writer.py`.
- Artifact writer tests exist and match all 17 artifact writer fixtures at
  expected-result metadata level.
- The artifact writer fixture validator exists.
- The artifact writer fixture validator CLI and Makefile target exist.
- Artifact writer fixture validation is included in release-quality.
- The artifact writer CLI does not exist.
- The artifact writer runtime smoke target does not exist.
- Artifact body generation does not exist.
- Manifest generation does not exist.
- File writing does not exist.

## 3. Proposed CLI Entrypoint

Recommended entrypoint:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer
```

Reasons:

- it matches the module name
- it follows the existing generator scaffold CLI pattern
- it is easy to reuse from a future Makefile runtime smoke target
- it keeps the writer CLI separate from fixture validation CLI behavior

## 4. Proposed CLI Arguments

Initial arguments:

- `--request`
- `--pointer`
- `--json`
- `--help`

Argument rules:

- `--request` and `--pointer` are both required for a writer run.
- Supplying only one of `--request` or `--pointer` is a usage error.
- Supplying neither is a usage error.
- `--json` is optional.
- The default output is a safe human summary.
- No output file option is added initially.
- No artifact body output option is added.
- No manifest body output option is added.
- No artifact file-writing option is added.
- No manifest file-writing option is added.

## 5. Example Commands

Valid case:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer --request tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/valid/minimal_metadata_only_artifact_plan/artifact_writer_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/valid/minimal_metadata_only_artifact_plan/generator_result_pointer.json
```

Valid case JSON:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer --request tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/valid/minimal_metadata_only_artifact_plan/artifact_writer_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/valid/minimal_metadata_only_artifact_plan/generator_result_pointer.json --json
```

Invalid expected fail-closed case:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer --request tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/invalid/generated_policy_body_leakage/artifact_writer_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_artifact_writer/invalid/generated_policy_body_leakage/generator_result_pointer.json
```

These examples identify fixture files only. They do not include request,
pointer, expected-result, artifact, policy, or manifest bodies.

## 6. Expected CLI Behavior

Valid case:

- `mode=artifact_writer`
- `writer_status=pass`
- `reason_codes=none`
- `failed_checks=none`
- artifact body unavailable and suppressed
- manifest body unavailable and suppressed
- artifact writing false
- manifest writing false
- exit code `0`

Invalid expected fail-closed case:

- `mode=artifact_writer`
- `writer_status=fail`
- expected reason code shown as a safe label
- safe metadata-only result
- no body output
- exit code `0`, because an expected fail-closed invalid fixture is a valid
  safe writer result

Usage error:

- missing request and pointer
- request only
- pointer only
- unknown option
- exit code `2`

Input loading error:

- missing request path
- missing pointer path
- malformed request JSON
- malformed pointer JSON
- non-object request or pointer payload
- exit code `2`

Missing required fields that are represented by loaded metadata should remain
a safe writer result when the writer skeleton can produce one. The CLI should
reserve input-error exit code `2` for failures to load or parse request or
pointer files.

Mismatch is not a CLI concern in the initial design. No expected-result
comparison option is added now.

Unexpected internal error:

- exit code `1`

## 7. Exit Code Design

Recommended exit codes:

- `0`: writer returned a safe metadata-only result, including expected
  fail-closed invalid fixtures
- `2`: usage error or request/pointer loading error
- `1`: unexpected internal error
- `3`: reserved for a future expected-result comparison mismatch, not used by
  the initial CLI

## 8. Safe Human Output

Allowed fields:

- mode
- writer status
- reason codes
- failed checks
- request ID safe label
- pointer ID safe label
- artifact ID safe label
- manifest ID safe label when available
- validation reference count
- artifact flags
- safety flags
- count summary
- safe summary
- validation schema version

Forbidden fields:

- artifact writer request body
- generator result pointer body
- expected artifact writer result body
- generated policy body
- generated artifact body
- artifact body
- manifest body
- policy body
- raw rows
- logits
- probabilities
- private paths
- raw learner text
- performance metric body

## 9. Safe JSON Output

The `--json` output should contain the same safe fields as the human output.
It must be parseable, deterministic, and body-free.

It must not include request bodies, pointer bodies, expected result bodies,
artifact bodies, policy bodies, manifest bodies, raw rows, logits, private
paths, raw learner text, or performance metric bodies.

## 10. No-Body-Leakage Policy

CLI stdout and stderr must not include:

- artifact writer request JSON body
- generator result pointer JSON body
- expected artifact writer result JSON body
- generated policy body
- artifact body
- manifest body
- policy body
- raw rows
- logits or probabilities
- private paths
- raw learner text
- performance metric body

Errors should report safe labels such as `missing_request_file`,
`malformed_request`, or `unknown_schema_version`, not raw payload excerpts.

## 11. Relation To Writer APIs

The CLI should:

- load request metadata via `load_artifact_writer_request`
- load pointer metadata via `load_generator_result_pointer`
- run the skeleton via `run_artifact_writer`
- summarize via `summarize_artifact_writer_result`
- safety-check via `audit_artifact_writer_safety`
- avoid duplicating writer logic
- avoid expected fixture result comparison
- avoid file writing
- avoid body generation
- avoid metrics

## 12. Relation To Fixture Validator

The fixture validator checks all 17 fixture contracts. The writer CLI runs one
request/pointer pair.

Future runtime smoke should use one valid synthetic request/pointer pair. The
fixture validator remains separate from runtime smoke. Fixture validation
success and writer runtime smoke success mean different things: fixture
validation proves expected metadata contract matching, while runtime smoke
proves that the writer CLI can execute one safe synthetic case.

## 13. Relation To Generator Scaffold

The generator scaffold produces a metadata-only generation plan scaffold. The
artifact writer consumes metadata-only artifact writer request/pointer
metadata. Both remain body-free and file-writing-free at this stage.

The artifact writer CLI should mirror the generator scaffold CLI's safety
style: safe labels, deterministic output, no body payloads, no file output,
and no performance claims.

## 14. Future CLI Tests

Future CLI tests should cover:

- `--help` exits `0`
- no args exits `2`
- request only exits `2`
- pointer only exits `2`
- valid case human output exits `0`
- valid case JSON exits `0` and is parseable
- invalid expected fail-closed case human output exits `0`
- invalid expected fail-closed case JSON exits `0` and is parseable
- malformed JSON temp request exits `2`
- missing request path exits `2`
- stdout/stderr contains no request body
- stdout/stderr contains no pointer body
- stdout/stderr contains no expected body
- stdout/stderr contains no artifact body
- stdout/stderr contains no manifest body
- stdout/stderr contains no raw rows
- stdout/stderr contains no logits
- stdout/stderr contains no private paths
- output is deterministic

## 15. Future Makefile Runtime Smoke Strategy

Not now. After CLI implementation and tests, add a standalone runtime smoke
target:

```text
check-learner-state-frozen-policy-generation-artifact-writer-runtime
```

The target should call one valid synthetic fixture:

```text
valid/minimal_metadata_only_artifact_plan
```

The target command should use `--request` and `--pointer`.

Success would mean the metadata-only artifact writer skeleton runtime returned
a safe pass summary. It would not mean artifact body generation, file writing,
artifact quality, manifest generation, performance evidence, or real-data
readiness.

## 16. Future Release-Quality Strategy

Not now. After CLI implementation, CLI tests, standalone Makefile runtime
target, and no-body-leakage review, add a runtime smoke to release-quality
after artifact writer fixture validation.

Success would mean the runtime smoke returned a safe pass summary. It would
not mean artifact writer quality, artifact generation evidence, manifest
generation evidence, performance evidence, or production readiness.

## 17. Status Marker Future

After release-quality integration and a successful remote/manual run, a future
status marker may record:

- artifact writer runtime smoke included yes/no
- writer status pass
- artifact writing false
- manifest writing false
- artifact body suppressed true
- manifest body suppressed true
- safety flags

The marker must not include raw logs, request/pointer/expected bodies,
artifact/policy/manifest bodies, raw rows, logits, private paths, raw learner
text, or performance metric bodies.

## 18. Docs Safety Policy

Docs should include schema/key-level descriptions and safe IDs only. They must
not include JSON fixture bodies, raw logs, request bodies, pointer bodies,
expected result bodies, artifact bodies, policy bodies, manifest bodies, raw
rows, logits, private paths, or raw learner text.

## 19. Proposed Next Steps

- Step317 artifact writer runtime Makefile target implementation
- Step318 artifact writer runtime release-quality integration design
- Step319 artifact writer runtime release-quality wrapper integration
- Step320 remote/manual run record workflow design
- Step321 remote/manual run status marker

## 20. Beginner-Friendly Explanation

A CLI is a terminal command for running the writer skeleton directly. It comes
after the skeleton because the code boundary should exist before a terminal
interface is exposed.

The fixture validator CLI and writer CLI are different. The fixture validator
checks all fixture contracts. The writer CLI runs one request/pointer pair and
returns the safe metadata-only writer result.

An invalid fixture can still exit `0` when it fails closed as expected. That
means the writer recognized unsafe metadata and returned a safe failure result.

Body and file-writing options are intentionally absent because the current
artifact policy suppresses bodies and disallows file writing. Adding those
options would require a separate design and review.

## 21. What This Does NOT Do

This design does not:

- implement the CLI
- write artifact files
- generate artifact bodies
- generate manifest bodies
- write manifest files
- compute metrics
- evaluate performance
- use real data
- prove production readiness

## 22. Step315 CLI Implementation Status

Step315 implements the metadata-only artifact writer CLI entrypoint:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_writer
```

The implemented CLI accepts `--request`, `--pointer`, optional `--json`, and
`--help`. It emits safe human or JSON metadata only. It does not add an output
file option, artifact body output option, manifest body output option,
artifact file-writing option, or manifest file-writing option.

Step315 also adds focused CLI tests in:

`python/learner_state/tests/test_frozen_policy_generation_artifact_writer_cli.py`

The CLI implementation does not add a Makefile target, change release-quality,
change workflow YAML, change fixture JSON, generate artifact bodies, generate
generated policy bodies, generate manifest bodies, write files, compute
metrics, use real data, or claim real-data readiness.

## 23. Step316 Runtime Makefile Target Design Status

Step316 designs the future standalone runtime smoke target for the artifact
writer CLI:

`check-learner-state-frozen-policy-generation-artifact-writer-runtime`

The design is documented in:

[Frozen policy generation artifact writer runtime Makefile target design](frozen_policy_generation_artifact_writer_runtime_makefile_target_design.md).

The target is not implemented in Step316. The design keeps the future target
limited to one valid synthetic request/pointer pair, safe human metadata
output, no artifact body generation, no manifest body generation, no artifact
or manifest file writing, no metrics, and no real-data readiness claim.

## 24. Step317 Runtime Makefile Target Implementation Status

Step317 implements the standalone runtime smoke target:

`check-learner-state-frozen-policy-generation-artifact-writer-runtime`

The target calls this writer CLI on one valid synthetic request/pointer pair
and emits the same safe human metadata summary. It is not added to
release-quality in Step317. It does not generate artifact bodies, generated
policy bodies, manifest bodies, write files, compute metrics, use real data,
or claim real-data readiness.

## 25. Step318 Runtime Release-Quality Integration Design Status

Step318 designs future release-quality wrapper integration for the standalone
runtime target:
[Frozen policy generation artifact writer runtime release-quality integration design](frozen_policy_generation_artifact_writer_runtime_release_quality_integration_design.md).

The wrapper is not changed in Step318. The design places the future runtime
smoke after artifact writer fixture validation and before config/scoring
smoke checks.

## 26. Step319 Runtime Release-Quality Wrapper Integration Status

Step319 integrates the standalone artifact writer runtime smoke target into
the release-quality wrapper:

`make check-learner-state-frozen-policy-generation-artifact-writer-runtime`

The wrapper section is placed after artifact writer fixture validation and
before config/scoring smoke checks. The CLI behavior remains metadata-only and
body-free. Step319 does not change the CLI implementation, Python tests,
workflow YAML, Makefile target, fixture JSON, artifact body generation,
generated policy body generation, manifest body generation, artifact or
manifest file writing, metrics, real-data use, or real-data readiness status.

## 27. Step320 Runtime Remote Run Record Workflow Design Status

Step320 designs the future public-safe remote/manual Release Quality run
recording workflow for the artifact writer runtime smoke:

[Frozen policy generation artifact writer runtime release-quality remote run record workflow](frozen_policy_generation_artifact_writer_runtime_release_quality_remote_run_record_workflow.md).

The workflow design keeps the future marker pass-only and count-only. It does
not create the marker, change the CLI, change workflow YAML, change wrapper
logic, change Makefile targets, change tests, change fixture JSON, generate
artifact bodies, generate manifest bodies, write files, compute metrics, use
real data, or claim real-data readiness.

## 28. Step321 Runtime Status Marker Creation Status

Step321 creates the public-safe remote/manual Release Quality status marker
for the artifact writer runtime smoke:

[Learner-state frozen policy generation artifact writer runtime release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_writer_runtime_release_quality_remote_run_status.md).

The marker records safe pass-only CLI runtime metadata. It does not change the
CLI implementation, change tests, change workflow YAML, change wrapper logic,
change Makefile targets, change fixture JSON, generate artifact bodies,
generate manifest bodies, write files, compute metrics, use real data, or
claim real-data readiness.

## 29. Step322 Artifact Body Generation Design Status

Step322 designs the future artifact body generation boundary:

[Frozen policy generation artifact body generation design](frozen_policy_generation_artifact_body_generation_design.md).

The CLI remains unchanged. The design keeps default CLI output body-free and
requires a later explicit safe design before any body mode can be added. No
artifact body generation, manifest body generation, file writing, Makefile
target, release-quality wrapper change, workflow change, Python test change,
fixture JSON change, metrics, real-data use, or production readiness claim is
introduced in Step322.

## 30. Step323 Artifact Body Fixture Design Status

Step323 designs future artifact body fixtures:

[Frozen policy generation artifact body fixture design](frozen_policy_generation_artifact_body_fixture_design.md).

The CLI remains unchanged and body-free by default. The future fixture design
does not create fixture JSON, implement a validator, implement body
generation, add CLI options, change Makefile targets, change release-quality,
change workflow YAML, change Python code or tests, write files, compute
metrics, use real data, or claim production readiness.
