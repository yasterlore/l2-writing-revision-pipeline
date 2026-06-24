# Frozen Policy Generation Artifact Body Generation Makefile Target Design

This document designs a future Makefile target for running the frozen policy
generation artifact body generation CLI. It is synthetic-only,
metadata-only, and no-oracle by design.

This is a docs-only design. It does not implement the Makefile target, does
not integrate release-quality, does not connect artifact writer CLI, does not
write artifact files, does not generate manifest bodies, does not write
manifest files, does not compute metrics, does not use real data, and does
not claim production readiness.

## 1. Purpose

The purpose is to define how a short `make` command should later run the
artifact body generation CLI safely.

This document covers:

- target naming
- target command choice
- help text
- expected safe behavior
- exit-code interpretation
- output and logging safety
- future implementation and release-quality staging

This document does not implement the Makefile target, change workflow YAML,
change release-quality, change Python code or tests, change fixture JSON,
write files, generate manifest bodies, evaluate performance, or claim
real-data readiness.

## 2. Current State

- Artifact body generation API exists in
  `python/learner_state/frozen_policy_generation_artifact_body.py`.
- Artifact body generation CLI exists at
  `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body`.
- Artifact body generation CLI tests exist.
- Artifact body fixture validator exists.
- Artifact body fixture validator CLI exists.
- Artifact body fixture validator Makefile target exists.
- Artifact body fixture validation is included in release-quality.
- Artifact body generation Makefile target does not exist.
- Artifact body generation release-quality integration does not exist.
- Artifact body file writing does not exist.
- Manifest body generation does not exist.

## 3. Proposed Target Name

Candidates:

- `check-learner-state-frozen-policy-generation-artifact-body-generation`
- `check-frozen-policy-generation-artifact-body-generation`
- `check-learner-state-artifact-body-generation`
- `check-artifact-body-generation`

Recommended target:

`check-learner-state-frozen-policy-generation-artifact-body-generation`

Rationale:

- It matches the learner-state namespace.
- It matches the frozen policy generation pipeline naming.
- It can sit next to the artifact body fixture validator target.
- It is clear enough for future release-quality labels.
- It identifies that the target calls the artifact body generation CLI.

The shorter names are easier to type but lose useful pipeline context and are
less consistent with the existing target naming style.

## 4. Proposed Command

Initial default suppressed-mode smoke command:

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body --request tests/fixtures/learner_state_frozen_policy_generation_artifact_body/valid/minimal_suppressed_metadata_only_body/artifact_body_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_artifact_body/valid/minimal_suppressed_metadata_only_body/artifact_writer_result_pointer.json`

This command uses one valid synthetic request and one valid synthetic pointer.
It relies on the CLI default mode, `suppressed`, and should emit only a
body-free safe metadata summary.

## 5. Optional Safe-Metadata Smoke Command

A future safe-metadata smoke command could use:

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body --request tests/fixtures/learner_state_frozen_policy_generation_artifact_body/valid/safe_metadata_body_summary/artifact_body_request.json --pointer tests/fixtures/learner_state_frozen_policy_generation_artifact_body/valid/safe_metadata_body_summary/artifact_writer_result_pointer.json --mode safe-metadata`

Recommendation: the initial target should run only the default suppressed
smoke.

Reasons:

- It fixes the default safety boundary first.
- It keeps the first target small.
- Safe-metadata smoke can remain manually testable through the CLI.
- A second target or second smoke can be designed later after the initial
  target behavior is stable.
- Release-quality integration should start with the smallest clear signal.

## 6. Proposed Help Text

`check-learner-state-frozen-policy-generation-artifact-body-generation  Run artifact body generation CLI smoke`

## 7. Expected Behavior

The future target should:

- run the artifact body generation CLI on one valid synthetic request/pointer
- exit 0
- report artifact body generation mode
- report `body_status=suppressed_metadata_only`
- report `generation_status=pass`
- report no reason codes
- report no failed checks
- report `artifact_body_available=false`
- report `artifact_file_written=false`
- report `manifest_file_written=false`
- report `content_suppressed=true`
- report `no_raw_rows=true`
- report `no_logits_dump=true`
- report `no_private_paths=true`
- report `no_performance_claims=true`
- report `synthetic_only_checked=true`
- report `no_oracle_checked=true`
- report `artifact_policy_checked=true`
- report `body_suppression_checked=true`
- report `raw_row_count=0`
- report `logits_dump_count=0`
- report `private_path_count=0`
- report `performance_metric_count=0`
- report `request_body_count=0`
- report `pointer_body_count=0`
- report `expected_body_count=0`
- report `manifest_body_count=0`
- print no artifact body payload
- print no request body
- print no pointer body
- print no manifest body
- create no output file
- create no artifact file
- create no manifest file

## 8. Exit Code Interpretation

- CLI exit 0 means target pass.
- CLI exit 2 means target fail due to usage or input error.
- CLI exit 3 means target fail due to safety audit fail-closed.
- CLI exit 1 means target fail due to unexpected internal error.

The Makefile target should not transform exit codes. The CLI should own the
meaning of those exit codes.

## 9. Output And Logging Safety

Allowed output:

- mode
- artifact ID
- manifest ID
- body status
- generation status
- reason code names
- failed check names
- safety flags
- count summary
- `artifact_file_written=false`
- `manifest_file_written=false`
- safe summary label

Forbidden output:

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
- performance metric body
- GitHub raw logs
- local absolute paths
- output file path containing a private path

## 10. Relation To Artifact Body Fixture Validator Target

The artifact body fixture validator target validates 18 fixture contracts.
The artifact body generation target should run one CLI smoke.

The existing fixture validator target is already in release-quality. The new
generation target should stay standalone first.

Generation target success is not fixture contract validation. Fixture target
success is not a generation CLI smoke.

## 11. Relation To Artifact Writer Runtime Target

Artifact writer runtime remains separate. Artifact writer CLI remains
body-free.

The artifact body generation target should not change artifact writer CLI
behavior. Any future integration into artifact writer CLI should be designed
as a separate step.

## 12. Relation To Safe-Metadata Mode

The initial target should use default suppressed mode.

Safe-metadata mode remains manually testable by CLI. A future target may be
considered:

`check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata`

Do not add that second target until a later design explicitly defines its
purpose, expected output, and release-quality staging.

## 13. Future Makefile Implementation Notes

Future implementation should:

- add the target to `.PHONY`
- add the help text to `make help`
- place the target near the artifact body fixture target
- not add the target to release-quality in the same step
- not create output files
- not write temporary outputs
- not use `--json` by default
- use human safe summary by default
- keep workflow YAML unchanged

## 14. Future Tests For Target Implementation

Future implementation should verify:

- `make help` includes the target
- target exits 0
- output includes `body_status=suppressed_metadata_only`
- output includes `generation_status=pass`
- output includes no reason codes
- output includes file-written false flags
- output includes safety flags
- output includes zero counts
- output includes no artifact body payload
- output includes no request body
- output includes no pointer body
- output includes no manifest body
- output includes no raw rows
- output includes no logits
- output includes no private paths
- output includes no raw learner text
- no output files are created
- Makefile diff is limited to `.PHONY`, target, and help text
- wrapper and workflow remain unchanged
- all existing tests pass

## 15. Future Release-Quality Staging

Suggested staging:

- Step339 Makefile target implementation
- Step340 release-quality integration design
- Step341 wrapper integration
- Step342 remote/manual run record workflow design
- Step343 status marker

Artifact writer CLI integration and manifest writer remain separate.

## 16. Docs Safety Policy

Docs may include:

- target names
- command names
- CLI argument names
- safe field names
- exit codes
- high-level behavior
- safety flag names
- count field names

Docs must not include:

- command output examples
- JSON output examples
- artifact body payload examples
- request body examples
- pointer body examples
- expected result body examples
- raw log examples
- raw learner text
- raw rows
- logits or probability dumps
- private paths
- performance metric bodies

## 17. Beginner-Friendly Explanation

A Makefile target is a short project command that hides a longer command line.
It gives contributors a memorable way to run the same smoke check every time.

The Makefile target design comes after the CLI implementation because the CLI
already owns the safety behavior. The Makefile target should only call the CLI
with one safe synthetic case.

The initial target should run default suppressed mode because that checks the
safest behavior first: no artifact body payload is available or printed.

Safe-metadata mode is useful, but it is a slightly broader behavior. Keeping
it out of the initial target makes the target easier to interpret and easier
to integrate later.

Release-quality integration should not happen immediately because the
standalone target should be proven first. The artifact writer CLI remains
separate because artifact writing and artifact body generation have different
safety boundaries.

## 18. What This Does Not Do

This document does not:

- implement a Makefile target
- integrate release-quality
- change workflow YAML
- change Python code or tests
- change fixture JSON
- write artifact files
- print artifact body payload
- generate manifest bodies
- write manifest files
- change artifact writer CLI
- use real data
- compute metrics
- claim production readiness

## 19. Step339 Implementation Status

Step339 implements the standalone Makefile target:

`check-learner-state-frozen-policy-generation-artifact-body-generation`

The target calls the artifact body generation CLI with the default
suppressed-mode synthetic request/pointer pair described above. It emits only
the CLI's body-free safe summary, creates no output files, writes no artifact
files, writes no manifest files, and does not add a safe-metadata target.

Step339 adds the target to `.PHONY` and `make help`. It does not add the
target to release-quality, does not change workflow YAML, does not change
Python code or tests, does not change fixture JSON, does not connect artifact
writer CLI, does not generate manifest bodies, does not use real data, and
does not compute metrics.

## 20. Step340 Release-Quality Integration Design Status

Step340 designs the future release-quality wrapper integration for this
standalone target:

[Frozen policy generation artifact body generation release-quality integration design](frozen_policy_generation_artifact_body_generation_release_quality_integration_design.md).

The design recommends adding the target after artifact body fixture validation
and before config/scoring smoke checks in a later wrapper step. It does not
change the wrapper, workflow YAML, Makefile, Python code or tests, fixture
JSON, safe-metadata target coverage, artifact writer CLI behavior, file
writing, manifest generation, real-data use, or metrics.

## 21. Step341 Release-Quality Wrapper Integration Status

Step341 adds this standalone target to the release-quality wrapper after
artifact body fixture validation and before config/scoring smoke checks. The
target remains default suppressed-mode only and continues to emit a body-free
safe summary.

Step341 does not change workflow YAML, does not change Makefile, does not
change Python code or tests, does not change fixture JSON, does not add a
safe-metadata target, does not connect artifact writer CLI, does not write
artifact files, does not generate manifest bodies, does not use real data, and
does not compute metrics.

## 22. Step342 Remote Run Record Workflow Design Status

Step342 adds a docs-only workflow design for a future public-safe
remote/manual Release Quality status marker after the generation CLI smoke is
included in the wrapper:

[Frozen policy generation artifact body generation release-quality remote run record workflow](frozen_policy_generation_artifact_body_generation_release_quality_remote_run_record_workflow.md).

The standalone Makefile target remains unchanged. The workflow design does
not create a status marker, run GitHub Actions, change workflow YAML, change
the wrapper, change Python code or tests, change fixture JSON, add a
safe-metadata target, write artifact files, generate manifest bodies, use real
data, or compute metrics.

## 23. Step343 Remote Run Status Marker Status

Step343 creates the public-safe remote/manual Release Quality status marker
for the generation CLI smoke target:

[Learner-state frozen policy generation artifact body generation release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_body_generation_release_quality_remote_run_status.md).

The Makefile target remains unchanged. The marker records only safe run
identity, pass-only smoke status, count-only related summaries, and safety
review metadata.

## 24. Step344 Safe-Metadata Makefile Target Design Status

Step344 designs a future standalone Makefile target for the artifact body
generation CLI's safe-metadata mode:

[Frozen policy generation artifact body safe-metadata Makefile target design](frozen_policy_generation_artifact_body_safe_metadata_makefile_target_design.md).

The existing default suppressed-mode target remains unchanged and remains the
only artifact body generation target in release-quality. Step344 does not
implement the safe-metadata target, does not change the wrapper, does not
change workflow YAML, does not change Makefile, does not change Python code
or tests, does not change fixture JSON, does not write artifact files, does
not generate manifest bodies, does not use real data, and does not compute
metrics.

## 25. Step345 Safe-Metadata Makefile Target Implementation Status

Step345 implements the standalone safe-metadata Makefile target designed in
Step344:

`check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata`

The existing default suppressed-mode target remains unchanged and remains the
only artifact body generation target in release-quality. The safe-metadata
target is standalone only. Step345 does not change the release-quality
wrapper, workflow YAML, Python code or tests, fixture JSON, artifact writer
CLI behavior, file writing, manifest generation, real-data use, or metrics.

## 26. Step346 Safe-Metadata Release-Quality Integration Design Status

Step346 designs future release-quality wrapper integration for the standalone
safe-metadata target:

[Frozen policy generation artifact body safe-metadata release-quality integration design](frozen_policy_generation_artifact_body_safe_metadata_release_quality_integration_design.md).

The design keeps the target summary-only and body-free. It does not change
the wrapper, workflow YAML, Makefile, Python code or tests, fixture JSON,
artifact writer CLI behavior, file writing, manifest generation, real-data
use, or metrics.

## 27. Step347 Safe-Metadata Wrapper Integration Status

Step347 adds the standalone safe-metadata target to the release-quality
wrapper after the default suppressed generation smoke and before
config/scoring smoke checks.

The Makefile target remains unchanged. Step347 does not change workflow YAML,
Makefile, Python code or tests, fixture JSON, artifact writer CLI behavior,
file writing, manifest generation, real-data use, or metrics.

## 28. Step348 Safe-Metadata Remote Run Record Workflow Design Status

Step348 designs the future remote/manual Release Quality run record workflow
for the safe-metadata target:

[Frozen policy generation artifact body safe-metadata release-quality remote run record workflow](frozen_policy_generation_artifact_body_safe_metadata_release_quality_remote_run_record_workflow.md).

This Makefile target design remains unchanged. The Step348 workflow design
keeps the future marker public-safe, pass-only, and count-only, and does not
copy raw logs, request bodies, pointer bodies, artifact body payloads,
generated policy bodies, manifest bodies, raw rows, logits, private paths,
raw learner text, real participant data, or performance metric bodies.

## 29. Step349 Safe-Metadata Remote Run Status Marker Status

Step349 creates the public-safe remote/manual Release Quality status marker
for the safe-metadata target:

[Learner-state frozen policy generation artifact body safe-metadata release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_body_safe_metadata_release_quality_remote_run_status.md).

The marker records pass-only/count-only metadata only. It does not change
Makefile, workflow YAML, wrapper scripts, Python code or tests, fixture JSON,
artifact writer CLI behavior, file writing, manifest generation, real-data
use, or metrics.
