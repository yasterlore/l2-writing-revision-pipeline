# Frozen Policy Generation Manifest Writer Runtime Makefile Target Design

## 1. Purpose

This document fixes the docs-only design for a future standalone Makefile
target that runs the frozen policy generation manifest writer runtime smoke.

It is not a Makefile implementation, not release-quality integration, not
manifest file writing, not artifact writer CLI integration, not performance
evaluation, and not a production readiness claim.

The target should run the existing metadata-only no-file manifest writer
runtime against one valid synthetic runtime fixture case and emit only a
body-free safe summary.

## 2. Current State

- the manifest writer runtime module exists
- the manifest writer runtime CLI exists
- focused runtime tests exist
- the runtime fixture validator target is in release-quality
- the runtime writer Makefile target does not exist
- the runtime writer is not in release-quality
- manifest file writing does not exist
- artifact writer CLI integration does not exist

The runtime module is:

- `learner_state.frozen_policy_generation_manifest_writer`

The runtime CLI is:

- `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer`

The runtime supports only:

- `metadata_only_no_file`

## 3. Proposed Target Name

Candidate names:

- `check-learner-state-frozen-policy-generation-manifest-writer-runtime`
- `check-learner-state-frozen-policy-generation-manifest-writer-runtime-smoke`
- `check-learner-state-manifest-writer-runtime`
- `check-manifest-writer-runtime`

Recommended target:

- `check-learner-state-frozen-policy-generation-manifest-writer-runtime`

Reasons:

- it matches existing learner-state / frozen policy generation target naming
- it stays distinct from the runtime fixture validation target
- it is clear enough when documented as a metadata-only no-file runtime smoke
- it will read well in a future release-quality label

## 4. Proposed Command

Use the valid minimal runtime fixture case:

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer --request tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime/valid/metadata_only_minimal_no_file/manifest_writer_request.json --artifact-result tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime/valid/metadata_only_minimal_no_file/artifact_writer_result_pointer.json --artifact-body-result tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime/valid/metadata_only_minimal_no_file/artifact_body_generation_result_pointer.json`

The command should not pass `--json` by default. Human output is already a
safe field/value summary.

The command should not pass `--manifest-out`. `--manifest-out` is not a
supported output feature for this phase.

## 5. Proposed Help Text

`check-learner-state-frozen-policy-generation-manifest-writer-runtime  Smoke test manifest writer metadata-only runtime`

## 6. Expected Behavior

Expected target behavior:

- target exits `0`
- `mode=manifest_writer`
- `result_schema_version=learner_state_frozen_policy_generation_manifest_writer_result_v0.1`
- `writer_status=pass`
- `manifest_writer_mode=metadata_only_no_file`
- `runtime_writer_executed=true`
- `manifest_body_available=false`
- `manifest_file_written=false`
- `manifest_output_path_available=false`
- `release_quality_ready=false`
- `reason_codes=none`
- `failed_checks=none`
- `content_suppressed=true`
- `manifest_body_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_absolute_paths=true`
- `no_artifact_body_payload=true`
- `no_generated_policy_body=true`
- `no_manifest_body_nesting=true`
- `no_request_body=true`
- `no_pointer_body=true`
- `no_expected_body=true`
- `no_performance_claims=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `non_proof_notice_checked=true`
- `path_policy_checked=true`
- `content_policy_checked=true`
- `file_writing_checked=true`
- `written_file_count=0`
- `tmp/frozen_policy_generation_manifest` residue remains `0`

## 7. Output / Logging Safety

Allowed output:

- target label/help
- command shape
- result schema version
- writer status
- safe synthetic IDs
- reference counts
- reason code names
- failed check names
- safety flags
- count summary
- safe summary

Forbidden output:

- manifest body
- manifest JSON body
- `manifest_writer_request` body
- `artifact_writer_result_pointer` body
- `artifact_body_generation_result_pointer` body
- `expected_manifest_writer_runtime_result` body
- fixture JSON body
- artifact body payload
- generated policy body
- request body
- pointer body
- expected body
- raw rows
- logits
- probabilities
- private paths
- absolute paths
- raw learner text
- raw logs

## 8. Relation To Runtime Fixture Validation Target

Existing target:

- `check-learner-state-frozen-policy-generation-manifest-writer-runtime-fixtures`

That target validates 31 runtime fixture contracts statically. It does not
execute the runtime writer.

Proposed target:

- `check-learner-state-frozen-policy-generation-manifest-writer-runtime`

This target executes one metadata-only no-file runtime smoke using the valid
minimal fixture case.

The proposed target must not replace the fixture validation target. Both
targets should remain separate. Runtime smoke success does not imply manifest
file writing readiness.

## 9. Relation To Artifact Writer / Artifact Body

The runtime smoke consumes existing pointer fixture files.

It does not:

- run the artifact writer CLI
- run the artifact body generation CLI
- reopen artifact body payloads
- create a manifest body
- write a manifest file

Artifact writer CLI integration remains a separate future phase.

## 10. Release-Quality Staging

Do not add the target to release-quality in this step.

Recommended staging:

- design the standalone target
- implement the standalone target
- design release-quality integration
- integrate the wrapper
- record remote/manual status after a successful remote run
- keep manifest file writing for a later separate phase

## 11. Future Implementation Checks

Future Step403 checks should include:

- `make help` includes the target
- target exits `0`
- output includes `mode=manifest_writer`
- output includes `writer_status=pass`
- output includes `runtime_writer_executed=true`
- output includes `manifest_body_available=false`
- output includes `manifest_file_written=false`
- output includes `release_quality_ready=false`
- no manifest body printed
- no fixture JSON body printed
- no artifact body payload printed
- no private path printed
- no absolute path printed
- `tmp/frozen_policy_generation_manifest` residue remains `0`
- runtime fixture validation target still passes
- release-quality still passes but does not include runtime smoke yet
- wrapper diff remains none
- workflow diff remains none

## 12. Docs Safety Policy

Docs must include only field names, command shape, count-only summary fields,
and policy statements.

Docs must not include:

- JSON body examples
- manifest body examples
- request/pointer body examples
- artifact body payload examples
- private path examples
- raw logs

## 13. Beginner-Friendly Explanation

A Makefile target is a short command name that runs a longer command
consistently.

The runtime fixture validation target and runtime smoke target are different.
The fixture validation target checks many fixture files without running the
writer. The runtime smoke target runs the writer once against a valid minimal
metadata-only fixture.

The valid minimal fixture is enough for the first smoke because the goal is
only to confirm that the runtime CLI can build a safe no-file summary. It is
not meant to exhaust every fixture case.

The target should not be added to release-quality in the same step so the
standalone command can be stabilized first.

Success does not mean manifest file writing is ready. The runtime still does
not accept `--manifest-out` as an output feature, does not create manifest
bodies, and does not write files.

## 14. Step403 Implementation Status

Step403 implements the standalone Makefile target:

`check-learner-state-frozen-policy-generation-manifest-writer-runtime`

The target runs the metadata-only no-file manifest writer runtime against the
valid minimal runtime fixture. It does not use `--json` by default and it does
not write manifest files.

The implementation adds only the standalone Makefile entry and help text. It
does not add the target to release-quality, change workflow YAML, change
Python code/tests, change fixture JSON, add `--manifest-out`, generate
manifest bodies, connect artifact writer CLI, use real data, compute metrics,
or claim production readiness.

## 15. What This Does Not Do

- does not add release-quality
- does not write manifest files
- does not add `--manifest-out`
- does not create a manifest body
- does not connect artifact writer CLI
- does not use real data
- does not compute metrics
- does not prove production readiness

After Step403, this design record is historical for the target shape. The
target is now implemented as a standalone local smoke target, but
release-quality integration remains a later step.

## 16. Step404 Release-Quality Integration Design Status

Step404 adds the docs-only release-quality integration design for the runtime
smoke target:

[Frozen policy generation manifest writer runtime release-quality integration design](frozen_policy_generation_manifest_writer_runtime_release_quality_integration_design.md).

The design proposes adding this target after runtime fixture validation and
before config/scoring smoke checks. It does not change the wrapper, workflow
YAML, Makefile, Python code/tests, fixture JSON, manifest file writing,
`--manifest-out`, manifest body generation, artifact writer CLI integration,
real-data use, metrics, or production readiness.

## 17. Step405 Wrapper Integration Status

Step405 adds the standalone runtime smoke target to the release-quality
wrapper. The target remains the same:

`check-learner-state-frozen-policy-generation-manifest-writer-runtime`

The wrapper entry runs after runtime fixture validation and before
config/scoring smoke checks. It does not change the target command, does not
change workflow YAML, does not write manifest files, does not add
`--manifest-out`, does not generate manifest bodies, does not connect
artifact writer CLI, and does not claim production readiness.

## 18. Step406 Remote Run Record Workflow Design Status

Step406 adds the docs-only remote/manual Release Quality run record workflow
for the runtime smoke target:

[Frozen policy generation manifest writer runtime release-quality remote run record workflow](frozen_policy_generation_manifest_writer_runtime_release_quality_remote_run_record_workflow.md).

The future status marker is separate from this Makefile target design and
from the runtime fixture validation marker. It should record only public-safe
metadata and pass-only/count-only runtime smoke summary fields. It should not
copy raw logs, fixture JSON bodies, request/pointer bodies, artifact body
payloads, generated policy bodies, manifest bodies, private paths, raw
learner text, or performance evidence.

## 19. Next Recommended Steps

- later: manifest file writing design / implementation

## 20. Step407 Remote Run Status Marker Status

Step407 creates the public-safe remote/manual Release Quality status marker
for the runtime smoke target:

[Learner-state frozen policy generation manifest writer runtime release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_runtime_release_quality_remote_run_status.md).

The marker records the Makefile target only as safe command metadata and does
not copy fixture JSON bodies, request/pointer bodies, artifact body payloads,
generated policy bodies, manifest bodies, raw logs, private paths, raw
learner text, or performance evidence.

## 21. Step408 File Writing Boundary Design Status

Step408 adds the docs-only boundary design for future metadata-only manifest
file writing:

[Frozen policy generation manifest writer metadata-only file writing boundary design](frozen_policy_generation_manifest_writer_file_writing_boundary_design.md).

The existing runtime Makefile target remains no-file only. A future
file-writing target should be separate, should use a safe root, should have
isolated write validation, and should not replace the current runtime smoke
target.

## 22. Step409 File Writing Fixture Contract Design Status

Step409 adds the docs-only fixture contract design for future metadata-only
manifest file writing fixtures:

[Frozen policy generation manifest writer metadata-only file writing fixture contract design](frozen_policy_generation_manifest_writer_file_writing_fixture_contract_design.md).

The existing runtime Makefile target remains a no-file smoke target. The file
writing fixture contract is a future fixture/validator track and does not add
fixture JSON, change Makefile, add `--manifest-out`, write manifest files, or
join release-quality here.

## 23. Related Documents

- [Frozen policy generation manifest writer metadata-only file writing fixture contract design](frozen_policy_generation_manifest_writer_file_writing_fixture_contract_design.md)
- [Frozen policy generation manifest writer metadata-only file writing boundary design](frozen_policy_generation_manifest_writer_file_writing_boundary_design.md)
- [Frozen policy generation manifest writer runtime implementation design](frozen_policy_generation_manifest_writer_runtime_implementation_design.md)
- [Frozen policy generation manifest writer runtime API design](frozen_policy_generation_manifest_writer_runtime_api_design.md)
- [Frozen policy generation manifest writer runtime fixture contract design](frozen_policy_generation_manifest_writer_runtime_fixture_contract_design.md)
- [Frozen policy generation manifest writer runtime fixture validator design](frozen_policy_generation_manifest_writer_runtime_fixture_validator_design.md)
- [Frozen policy generation manifest writer runtime fixture release-quality integration design](frozen_policy_generation_manifest_writer_runtime_fixture_release_quality_integration_design.md)
- [Frozen policy generation manifest writer runtime release-quality integration design](frozen_policy_generation_manifest_writer_runtime_release_quality_integration_design.md)
- [Frozen policy generation manifest writer runtime release-quality remote run record workflow](frozen_policy_generation_manifest_writer_runtime_release_quality_remote_run_record_workflow.md)
- [Learner-state frozen policy generation manifest writer runtime fixture release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_runtime_fixture_release_quality_remote_run_status.md)
- [Learner-state frozen policy generation manifest writer runtime release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_runtime_release_quality_remote_run_status.md)
- [Frozen policy generation manifest writer boundary design](frozen_policy_generation_manifest_writer_boundary_design.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)
