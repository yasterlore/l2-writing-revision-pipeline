# Frozen Policy Generation Manifest Writer Runtime Release-Quality Integration Design

## 1. Purpose

This document fixes the future release-quality integration design for the
frozen policy generation manifest writer runtime smoke target.

It is a design document only. It is not wrapper implementation, not a
workflow change, not manifest file writing, not `--manifest-out` support, not
manifest body generation, not artifact writer CLI integration, not a
performance evaluation, and not a production-readiness claim.

The target covered here is:

`check-learner-state-frozen-policy-generation-manifest-writer-runtime`

## 2. Current State

- manifest writer runtime module exists
- manifest writer runtime CLI exists
- focused runtime tests exist
- standalone runtime Makefile target exists
- runtime fixture validator target is already in release-quality
- runtime smoke target is not yet in release-quality
- manifest file writing does not exist
- `--manifest-out` is not a supported output feature
- artifact writer CLI integration does not exist

The runtime smoke uses the existing metadata-only no-file implementation. It
does not generate a manifest body and does not write a manifest file.

## 3. Proposed Wrapper Insertion Point

Candidate A: after runtime fixture validation target, before config/scoring
smoke checks.

Candidate B: after static manifest writer fixture validation, before runtime
fixture validation target.

Candidate C: after config/scoring smoke checks.

Recommended insertion point: Candidate A.

Recommended order:

- artifact writer fixture validation
- artifact writer runtime smoke
- artifact body fixture validation
- artifact body generation CLI smoke
- artifact body generation safe-metadata CLI smoke
- artifact body file writing fixture validation
- artifact body isolated write validation
- static manifest writer fixture validation
- runtime manifest writer fixture validation
- runtime manifest writer smoke
- config and scoring smoke checks

Rationale:

- static manifest writer fixture validation
- runtime manifest writer fixture validation
- runtime manifest writer smoke

This order naturally moves from contract validation to runtime smoke. It also
keeps the manifest writer chain together before the separate config/scoring
smoke checks. Candidate B runs the runtime smoke before runtime fixture
validation, which reverses the intended order. Candidate C splits the manifest
writer chain across unrelated config/scoring checks.

## 4. Proposed Wrapper Command

`make check-learner-state-frozen-policy-generation-manifest-writer-runtime`

## 5. Proposed Wrapper Label

`release_quality_check: learner-state frozen policy generation manifest writer runtime smoke`

## 6. Expected Wrapper Behavior

If the runtime smoke target passes, release-quality should continue. If the
target fails, release-quality should fail.

Expected safe output fields include:

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

The wrapper entry must not print manifest bodies, fixture JSON bodies,
request/pointer/expected bodies, artifact body payloads, generated policy
bodies, private paths, absolute paths, raw learner text, or performance
evidence.

## 7. Failure Interpretation

Release-quality should treat the following as failures:

- runtime target exits nonzero
- `writer_status` is not `pass`
- unsupported mode
- malformed request or pointer
- body, payload, raw row, logits, private path, or absolute path marker
  detected
- `include_manifest_body=true` accepted unexpectedly
- `allow_manifest_file_writing=true` accepted unexpectedly
- `manifest_out` accepted unexpectedly
- `manifest_body_available=true` unexpectedly
- `manifest_file_written=true` unexpectedly
- `manifest_output_path_available=true` unexpectedly
- `runtime_writer_executed=false` unexpectedly
- `reason_codes` not `none` for the valid minimal fixture
- `failed_checks` not `none` for the valid minimal fixture
- `written_file_count > 0`
- `tmp/frozen_policy_generation_manifest` residue count is greater than `0`

These failures are runtime smoke failures for metadata-only no-file result
construction. They are not manifest file writing failures, not artifact writer
CLI integration failures, and not model performance failures.

## 8. Log Safety Review

Allowed in logs:

- wrapper label
- wrapper command
- mode
- result schema version
- writer status
- manifest writer mode
- safe synthetic IDs
- reference counts
- `reason_codes=none`
- `failed_checks=none`
- safety flags
- count summary
- safe summary
- `runtime_writer_executed=true`
- `manifest_body_available=false`
- `manifest_file_written=false`
- `release_quality_ready=false`

Forbidden in logs:

- manifest body
- manifest JSON body
- manifest writer request body
- artifact writer result pointer body
- artifact body generation result pointer body
- expected manifest writer runtime result body
- fixture JSON body
- artifact body payload
- generated policy body
- raw rows
- logits
- probabilities
- private paths
- absolute paths
- raw learner text
- final text
- observed-after text
- gold label
- scoring feedback payload
- performance metric body
- GitHub raw logs copied into docs
- full job output copied into docs

## 9. Relation To Existing Release-Quality Checks

The runtime fixture validation target checks 31 fixture contracts statically.
The runtime smoke target executes one valid metadata-only no-file fixture
through the runtime writer.

The runtime smoke does not replace runtime fixture validation. Both should
remain in the release-quality chain once integration happens.

The artifact writer runtime smoke remains separate. The artifact body
generation smoke remains separate. Manifest file writing remains future and
separate. Artifact writer CLI integration remains future and separate.

## 10. Release-Quality Staging

Recommended staging:

- add runtime smoke target to wrapper
- run local release-quality
- add remote/manual run record workflow design
- record remote/manual status marker after a successful run
- design manifest file writing later
- design artifact writer CLI integration later

Do not infer manifest file writing readiness from runtime smoke success.

## 11. Makefile / Workflow Status

- Makefile target exists
- wrapper is not yet changed for runtime smoke target
- workflow YAML should not need changes if it already invokes the wrapper
- future implementation should modify only the wrapper unless a workflow issue
  is discovered
- workflow YAML diff should remain none unless necessary

## 12. Testing Plan For Future Wrapper Implementation

Future checks should include:

- standalone runtime target passes
- `make check-release-quality` includes the new runtime smoke label
- `make check-release-quality` passes
- output includes `mode=manifest_writer`
- output includes `writer_status=pass`
- output includes `runtime_writer_executed=true`
- output includes `manifest_body_available=false`
- output includes `manifest_file_written=false`
- output includes `release_quality_ready=false`
- output remains body-free
- no manifest body printed
- no manifest files written
- `tmp/frozen_policy_generation_manifest` residue remains `0`
- runtime fixture validation target remains included
- wrapper diff is limited to the new label and command
- workflow diff remains none
- all existing checks pass

## 13. Future Status Marker

After wrapper integration and a successful remote/manual Release Quality run,
a future status marker may be added.

Recommended future marker path:

`docs/status/learner_state_frozen_policy_generation_manifest_writer_runtime_release_quality_remote_run_status.md`

The marker should record pass-only/count-only metadata. Raw logs must not be
copied.

Safe marker fields can include:

- target included yes
- label
- command
- `writer_status=pass`
- `runtime_writer_executed=true`
- `manifest_body_available=false`
- `manifest_file_written=false`
- `release_quality_ready=false`
- `written_file_count=0`
- no manifest body copied
- no fixture JSON body copied
- no artifact body payload copied
- no generated policy body copied
- no private paths copied
- no absolute paths copied
- no performance evidence

## 14. No-Oracle / Synthetic-Only Boundary

The target uses a synthetic metadata-only valid fixture. It uses no real data
and no participant data.

It must not include:

- raw learner text
- final text
- gold label
- observed-after text
- expected action payload
- scoring feedback payload
- artifact body payload in logs
- generated policy body
- manifest body
- logits
- raw rows
- private paths

## 15. Safety Interpretation

Release-quality success with the runtime smoke means the metadata-only
no-file runtime writer can construct a safe summary from one valid fixture.

It does not mean manifest file writing is implemented. It does not mean
manifest files can be written. It does not mean artifact writer CLI
integration exists. It does not mean production file output is ready. It does
not mean model performance. It does not mean real-data readiness.

## 16. Beginner-Friendly Explanation

A runtime smoke is a small command that runs the actual runtime once with a
known safe synthetic input. It checks that the command can execute and return
a safe summary.

Runtime fixture validation is different. Fixture validation checks the
fixture set statically and does not run the runtime writer.

Putting the runtime smoke in release-quality later is useful because it
confirms that the runtime command still works in the normal release-quality
bundle. It still does not prove file writing readiness or production
readiness.

Manifest file writing remains separate because writing files has additional
path, overwrite, cleanup, and privacy risks. The current runtime smoke is
metadata-only and no-file by design.

## 17. What This Does Not Do

- does not change workflow YAML
- does not change Makefile
- does not change Python code/tests
- does not change fixture JSON
- does not write manifest files
- does not implement `--manifest-out`
- does not generate manifest bodies
- does not connect artifact writer CLI
- does not compute metrics
- does not use real data
- does not prove production readiness

## 18. Step405 Wrapper Integration Status

Step405 adds the standalone runtime smoke target to the release-quality
wrapper:

`make check-learner-state-frozen-policy-generation-manifest-writer-runtime`

Wrapper label:

`release_quality_check: learner-state frozen policy generation manifest writer runtime smoke`

The wrapper entry is placed after runtime manifest writer fixture validation
and before config/scoring smoke checks. It runs the existing metadata-only
no-file runtime smoke and keeps output body-free. It does not change workflow
YAML, Makefile, Python code/tests, fixture JSON, manifest file writing,
`--manifest-out`, manifest body generation, artifact writer CLI integration,
real-data use, metrics, or production readiness.

After Step405, this document is historical for the integration design and
records that the wrapper integration has been implemented. Remote/manual run
recording and a runtime smoke status marker remain later steps.

## 19. Step406 Remote Run Record Workflow Design Status

Step406 adds the docs-only remote/manual Release Quality run record workflow
for the runtime smoke target:

[Frozen policy generation manifest writer runtime release-quality remote run record workflow](frozen_policy_generation_manifest_writer_runtime_release_quality_remote_run_record_workflow.md).

The workflow design defines the future public-safe status marker path,
allowed metadata, forbidden metadata, marker structure, failure handling,
interpretation, and next actions. It does not create the actual status
marker, run GitHub Actions, change workflow YAML, change the wrapper, change
Makefile, change Python code/tests, change fixture JSON, write manifest
files, add `--manifest-out`, connect artifact writer CLI, use real data,
compute metrics, or claim production readiness.

## 20. Next Recommended Steps

- later: manifest file writing design / implementation
- later: artifact writer CLI integration design / implementation

## 21. Step407 Remote Run Status Marker Status

Step407 creates the public-safe remote/manual Release Quality status marker
for the runtime smoke target:

[Learner-state frozen policy generation manifest writer runtime release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_runtime_release_quality_remote_run_status.md).

The marker is pass-only/count-only and records safe run identity metadata,
wrapper inclusion metadata, runtime smoke summary fields, related check
summaries, safety review, interpretation, and non-goals. It does not copy raw
logs, full job output, request/pointer bodies, fixture JSON bodies, artifact
body payloads, generated policy bodies, manifest bodies, private paths, raw
learner text, real participant data, or performance evidence.

## 22. Related Documents

- [Frozen policy generation manifest writer runtime Makefile target design](frozen_policy_generation_manifest_writer_runtime_makefile_target_design.md)
- [Frozen policy generation manifest writer runtime implementation design](frozen_policy_generation_manifest_writer_runtime_implementation_design.md)
- [Frozen policy generation manifest writer runtime API design](frozen_policy_generation_manifest_writer_runtime_api_design.md)
- [Frozen policy generation manifest writer runtime fixture contract design](frozen_policy_generation_manifest_writer_runtime_fixture_contract_design.md)
- [Frozen policy generation manifest writer runtime fixture validator design](frozen_policy_generation_manifest_writer_runtime_fixture_validator_design.md)
- [Frozen policy generation manifest writer runtime fixture release-quality integration design](frozen_policy_generation_manifest_writer_runtime_fixture_release_quality_integration_design.md)
- [Frozen policy generation manifest writer runtime release-quality remote run record workflow](frozen_policy_generation_manifest_writer_runtime_release_quality_remote_run_record_workflow.md)
- [Learner-state frozen policy generation manifest writer runtime fixture release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_runtime_fixture_release_quality_remote_run_status.md)
- [Learner-state frozen policy generation manifest writer runtime release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_runtime_release_quality_remote_run_status.md)
- [Frozen policy generation manifest writer boundary design](frozen_policy_generation_manifest_writer_boundary_design.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)
