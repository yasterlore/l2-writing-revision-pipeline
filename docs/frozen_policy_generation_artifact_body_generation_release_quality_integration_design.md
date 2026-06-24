# Frozen Policy Generation Artifact Body Generation Release-Quality Integration Design

This document designs a future release-quality wrapper integration for the
frozen policy generation artifact body generation Makefile target. It is
synthetic-only, metadata-only, and no-oracle by design.

This is a docs-only design. It does not implement wrapper integration, does
not change workflow YAML, does not change Makefile, does not change Python
code or tests, does not change fixture JSON, does not connect artifact writer
CLI, does not add a safe-metadata target, does not write artifact files, does
not generate manifest bodies, does not write manifests, does not compute
metrics, does not use real data, and does not claim production readiness.

## 1. Purpose

The purpose is to define how the standalone artifact body generation Makefile
target should later be included in `make check-release-quality` safely.

This document covers:

- wrapper insertion point
- wrapper command
- wrapper label
- expected safe behavior
- failure interpretation
- log safety
- testing plan
- future remote status marker staging

This document does not implement the wrapper change, alter workflow YAML,
connect artifact writer CLI, write files, generate manifest bodies, evaluate
performance, or claim real-data readiness.

## 2. Current State

- Artifact body generation API exists.
- Artifact body generation CLI exists.
- Artifact body generation CLI tests exist.
- Artifact body generation Makefile target exists.
- Artifact body generation target passes standalone.
- Artifact body fixture validator target exists.
- Artifact body fixture validator target is already in release-quality.
- Artifact body generation target is not in release-quality yet.
- Safe-metadata target does not exist.
- Artifact file writing does not exist.
- Manifest body generation does not exist.
- Artifact writer CLI integration does not exist.

## 3. Proposed Wrapper Insertion Point

Candidate A: after artifact body fixture validation and before config and
scoring smoke checks.

Candidate B: after artifact writer runtime smoke and before artifact body
fixture validation.

Candidate C: after config and scoring smoke checks.

Recommended insertion point: Candidate A.

The recommended order is:

- artifact writer fixture validation
- artifact writer runtime smoke
- artifact body fixture validation
- artifact body generation CLI smoke
- config and scoring smoke checks

Rationale:

- Artifact body fixture validation checks the 18 body-boundary fixture
  contracts before running the generation CLI smoke.
- The fixture contract and generation smoke form a natural sequence.
- The release-quality flow can read as writer fixture/runtime first, then
  artifact body fixture/generation.
- Config and scoring smoke checks are a separate track and should remain
  after the frozen policy generation artifact body checks.
- The generation target is a body-free suppressed smoke, so it belongs with
  the safety-oriented release-quality checks.

## 4. Proposed Wrapper Command

`make check-learner-state-frozen-policy-generation-artifact-body-generation`

## 5. Proposed Wrapper Label

`release_quality_check: learner-state frozen policy generation artifact body generation CLI smoke`

## 6. Expected Wrapper Behavior

When the target passes, release-quality should continue. When the target
fails, release-quality should fail.

Expected safe metadata from the target:

- `body_status=suppressed_metadata_only`
- `generation_status=pass`
- `reason_codes=none`
- `failed_checks=none`
- `artifact_body_available=false`
- `artifact_file_written=false`
- `manifest_file_written=false`
- `content_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_performance_claims=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `artifact_policy_checked=true`
- `body_suppression_checked=true`
- `raw_row_count=0`
- `logits_dump_count=0`
- `private_path_count=0`
- `performance_metric_count=0`
- `request_body_count=0`
- `pointer_body_count=0`
- `expected_body_count=0`
- `manifest_body_count=0`

The target should produce safe metadata only. It should create no temporary
output, no artifact file, and no manifest file. It should print no artifact
body payload, request body, pointer body, generated policy body, manifest
body, or performance evidence.

## 7. Failure Interpretation

The following should be release-quality failures:

- missing request fixture
- missing pointer fixture
- malformed JSON
- unknown request or pointer schema
- CLI usage error
- safety audit fail-closed
- internal error
- `body_status` is not `suppressed_metadata_only`
- `generation_status` is not `pass`
- `reason_codes` is not `none`
- `failed_checks` is not `none`
- `artifact_body_available=true`
- `artifact_file_written=true`
- `manifest_file_written=true`
- safety flag false
- `raw_row_count > 0`
- `logits_dump_count > 0`
- `private_path_count > 0`
- `performance_metric_count > 0`
- `request_body_count > 0`
- `pointer_body_count > 0`
- `expected_body_count > 0`
- `manifest_body_count > 0`
- artifact body payload leakage
- request body leakage
- pointer body leakage
- generated policy body leakage
- manifest body leakage
- raw learner text leakage
- private path leakage

These failures are release-quality safety or integration failures. They are
not artifact body generation correctness failures, artifact writer correctness
failures, or model performance failures.

## 8. Log Safety Review

Allowed in logs:

- label
- command
- mode
- artifact ID
- manifest ID
- body status
- generation status
- reason code names
- failed check names
- safety flags
- count summary
- file-written false flags
- safe summary label

Forbidden in logs:

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
- raw learner text
- final text
- observed-after text
- gold label
- expected action payload
- scoring feedback payload
- performance metric body
- GitHub raw logs
- full job output copied into docs

## 9. Relation To Existing Release-Quality Checks

- Artifact writer fixture validation validates the writer metadata contract.
- Artifact writer runtime smoke validates writer CLI runtime behavior.
- Artifact body fixture validation validates 18 body-boundary fixture
  contracts.
- Artifact body generation CLI smoke validates one suppressed-mode generation
  CLI path.
- Artifact body generation CLI smoke does not print body payload.
- Artifact body generation CLI smoke does not write files.
- Artifact body generation CLI smoke does not validate a safe-metadata mode
  target.
- Artifact body generation CLI smoke does not prove artifact body generation
  correctness.
- Generator scaffold checks remain separate.
- Config and scoring smoke checks remain separate.

## 10. Makefile And Workflow Status

- Makefile target already exists.
- Release-quality wrapper is not yet changed.
- Workflow YAML should not need to change if the workflow already calls the
  wrapper.
- Future implementation should modify only the wrapper if possible.
- Workflow YAML diff should remain empty unless a later step finds a concrete
  need.

## 11. Testing Plan For Future Implementation

Future implementation should verify:

- standalone generation target passes
- `make check-release-quality` includes the new generation label
- `make check-release-quality` passes
- output includes `body_status=suppressed_metadata_only`
- output includes `generation_status=pass`
- output includes `reason_codes=none`
- output includes `failed_checks=none`
- output includes `artifact_body_available=false`
- output includes `artifact_file_written=false`
- output includes `manifest_file_written=false`
- output includes safety flags
- output includes zero counts
- no request, pointer, artifact, or manifest body leakage
- no raw rows, logits, private path, or raw learner text leakage
- no temporary output
- no artifact writing
- no manifest writing
- wrapper diff is limited
- workflow diff is empty
- all Python tests pass
- all existing checks pass

## 12. Release-Quality Status Marker Future

After wrapper integration and a successful remote or manual Release Quality
run, a future status marker may be added.

The marker should record pass-only and count-only metadata. Raw logs must not
be copied.

Artifact body generation CLI smoke status may record:

- target included yes or no
- label
- command
- `body_status=suppressed_metadata_only`
- `generation_status=pass`
- `reason_codes=none`
- `failed_checks=none`
- `artifact_body_available=false`
- `artifact_file_written=false`
- `manifest_file_written=false`
- safety flags
- zero counts

The marker must not record request, pointer, artifact, or manifest bodies.

## 13. Safe-Metadata Mode Staging

- Safe-metadata CLI mode remains manually testable.
- Safe-metadata mode should not be added to release-quality yet.
- A future dedicated target can be designed if needed.
- Default suppressed smoke is sufficient for the initial release-quality
  generation CLI smoke.

## 14. No-Oracle And Synthetic-Only Boundary

The future wrapper target should use one synthetic metadata request/pointer
pair only.

The boundary excludes:

- real data
- participant data
- raw learner text
- final, gold, or observed-after text
- expected action payload
- scoring feedback payload
- artifact body payload
- generated policy body
- manifest body
- logits
- raw rows
- private paths

## 15. What This Does Not Do

This document does not:

- integrate the wrapper
- change workflow YAML
- generate printable artifact body payload
- write artifacts
- generate manifest bodies
- write manifests
- compute metrics
- evaluate performance
- use real data
- prove production readiness

## 16. Beginner-Friendly Explanation

Release-quality is the project's combined safety and regression check. Adding
a target to it means the check will run as part of the normal release-quality
bundle instead of only when someone remembers to run it manually.

The standalone target comes first because it proves the command is stable on
its own. The release-quality design then decides where that target belongs in
the larger wrapper.

Artifact body fixture validation and artifact body generation CLI smoke are
different checks. Fixture validation checks many expected contract outcomes.
Generation smoke checks one CLI path in default suppressed mode.

Suppressed mode is the right first release-quality signal because it confirms
the CLI can run without making an artifact body payload available in logs.
Safe-metadata mode stays out for now because it is a broader behavior and can
receive its own target and integration design later.

A successful smoke check means the safe CLI path ran. It does not prove
artifact body generation correctness, writer correctness, model performance,
real-data readiness, or production readiness.

## 17. Next Recommended Steps

- Step341: release-quality wrapper integration
- Step342: remote/manual run record workflow design
- Step343: remote/manual run status marker

Artifact writer CLI integration, safe-metadata target design, manifest writer,
artifact file writing, and real-data readiness remain separate future work.

## 18. Step341 Wrapper Integration Status

Step341 implements the release-quality wrapper integration described here.
The wrapper now runs:

`make check-learner-state-frozen-policy-generation-artifact-body-generation`

with the label:

`release_quality_check: learner-state frozen policy generation artifact body generation CLI smoke`

The command is placed after artifact body fixture validation and before
config/scoring smoke checks. It remains default suppressed-mode only. Step341
does not change workflow YAML, does not change Makefile, does not change
Python code or tests, does not change fixture JSON, does not add a
safe-metadata target, does not connect artifact writer CLI, does not write
artifact files, does not generate manifest bodies, does not use real data, and
does not compute metrics.

## 19. Step342 Remote Run Record Workflow Design Status

Step342 designs how a future remote/manual Release Quality run should be
recorded after this wrapper integration:

[Frozen policy generation artifact body generation release-quality remote run record workflow](frozen_policy_generation_artifact_body_generation_release_quality_remote_run_record_workflow.md).

The workflow design keeps the future status marker pass-only and count-only.
It does not create the status marker, run GitHub Actions, change workflow
YAML, change the wrapper, change Makefile, change Python code or tests, change
fixture JSON, add a safe-metadata target, write artifact files, generate
manifest bodies, use real data, or compute metrics.

## 20. Step343 Remote Run Status Marker Status

Step343 creates the public-safe remote/manual Release Quality status marker
for this wrapper integration:

[Learner-state frozen policy generation artifact body generation release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_body_generation_release_quality_remote_run_status.md).

The marker records the generation CLI smoke as default suppressed-mode,
body-free, pass-only metadata. It does not copy raw logs, request/pointer
bodies, artifact body payloads, generated policy bodies, manifest bodies, raw
rows, logits, private paths, raw learner text, real participant data, or
performance metric bodies.

## 21. Step344 Safe-Metadata Makefile Target Design Status

Step344 designs a future standalone safe-metadata Makefile target:

[Frozen policy generation artifact body safe-metadata Makefile target design](frozen_policy_generation_artifact_body_safe_metadata_makefile_target_design.md).

This release-quality integration remains scoped to the default
suppressed-mode target. The safe-metadata target is not implemented here and
is not added to release-quality. Step344 does not change the wrapper,
workflow YAML, Makefile, Python code or tests, fixture JSON, artifact writer
CLI behavior, artifact file writing, manifest generation, real-data use, or
metrics.

## 22. Step345 Safe-Metadata Makefile Target Implementation Status

Step345 implements the standalone safe-metadata Makefile target:

`check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata`

This release-quality integration remains scoped to the default
suppressed-mode target. The new safe-metadata target is not added to
release-quality in Step345. Step345 does not change the wrapper, workflow
YAML, Python code or tests, fixture JSON, artifact writer CLI behavior,
artifact file writing, manifest generation, real-data use, or metrics.

## 23. Step346 Safe-Metadata Release-Quality Integration Design Status

Step346 designs future release-quality wrapper integration for the
standalone safe-metadata target:

[Frozen policy generation artifact body safe-metadata release-quality integration design](frozen_policy_generation_artifact_body_safe_metadata_release_quality_integration_design.md).

This document remains the default suppressed-mode integration record.
Step346's design keeps safe-metadata integration separate and future. It does
not change the wrapper, workflow YAML, Makefile, Python code or tests,
fixture JSON, artifact writer CLI behavior, artifact file writing, manifest
generation, real-data use, or metrics.

## 24. Step347 Safe-Metadata Wrapper Integration Status

Step347 adds the standalone safe-metadata target to the release-quality
wrapper after the default suppressed artifact body generation CLI smoke and
before config/scoring smoke checks.

This document remains the default suppressed-mode integration record, while
the safe-metadata wrapper status is tracked in:

[Frozen policy generation artifact body safe-metadata release-quality integration design](frozen_policy_generation_artifact_body_safe_metadata_release_quality_integration_design.md).

Step347 does not change workflow YAML, Makefile, Python code or tests,
fixture JSON, artifact writer CLI behavior, artifact file writing, manifest
generation, real-data use, or metrics.

## 25. Step348 Safe-Metadata Remote Run Record Workflow Design Status

Step348 designs the future remote/manual Release Quality run record workflow
for the safe-metadata artifact body generation CLI smoke:

[Frozen policy generation artifact body safe-metadata release-quality remote run record workflow](frozen_policy_generation_artifact_body_safe_metadata_release_quality_remote_run_record_workflow.md).

This document remains the release-quality integration design for the default
suppressed generation smoke. Step348 does not create a status marker, does
not run a remote workflow, does not change workflow YAML, does not change the
wrapper, does not change Makefile, does not change Python code or tests, does
not change fixture JSON, does not write artifact files, does not generate
manifest bodies, does not use real data, and does not compute metrics.
