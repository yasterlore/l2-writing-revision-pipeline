# Frozen Policy Generation Manifest Writer Runtime API Design

## 1. Purpose

This document fixes the docs-only boundary for a future frozen policy
generation manifest writer runtime API and CLI.

It is not an implementation, not fixture JSON creation, not runtime validator
implementation, not release-quality integration, not performance evaluation,
and not a production readiness claim.

The design is synthetic-only, metadata-only, and no-oracle. It defines future
runtime inputs, outputs, summary fields, body suppression, path policy, file
writing policy, fail-closed behavior, relation to the static fixture
validator, and future staging.

## 2. Current State

- the static manifest writer fixture validator exists
- the manifest writer fixture target is in release-quality
- the manifest writer fixture remote status marker exists
- the manifest writer runtime does not exist
- the manifest writer CLI does not exist
- manifest file writing does not exist
- artifact writer CLI integration does not exist
- manifest body remains suppressed

## 3. Proposed Runtime Module

Proposed future module:

- `learner_state.frozen_policy_generation_manifest_writer`

## 4. Proposed CLI

Proposed future CLI:

- `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer`

## 5. Proposed CLI Arguments

Potential future arguments:

- `--artifact-result`
- `--artifact-body-result`
- `--manifest-out`
- `--json`
- `--help`

`--manifest-out` is a future explicit file-writing option. The default should
be no manifest file writing. The initial runtime implementation should support
metadata-only no-file mode first. Manifest file writing can remain a separate
later phase if needed.

## 6. Proposed APIs / Dataclasses

Proposed future APIs:

- `build_metadata_only_manifest_result(...)`
- `audit_manifest_result_safety(...)`
- `summarize_manifest_writer_result(...)`
- optional later: `write_manifest_file(...)`

Proposed future dataclasses:

- `ManifestWriterRequest`
- `ManifestWriterArtifactPointer`
- `ManifestWriterArtifactBodyPointer`
- `ManifestWriterResult`
- `ManifestWriterSafetySummary`
- `ManifestWriterCountSummary`
- `ManifestWriterError`

## 7. Runtime Input Boundary

Allowed input:

- artifact writer result pointer / metadata summary
- artifact body generation result pointer / metadata summary
- validation reference IDs
- release-quality reference IDs
- safe `artifact_id`
- safe `artifact_body_id`
- safe `manifest_id`
- safe relative output intent if explicit
- synthetic-only notices
- no-oracle notices
- non-proof notices

Forbidden input:

- generated policy body
- artifact body payload
- manifest body
- request body
- pointer body as nested payload
- expected result body
- raw rows
- logits
- probabilities
- model scores
- raw learner text
- `final_text`
- `observed_after_text`
- gold labels
- scoring feedback payload
- private paths
- absolute paths
- raw logs
- real participant data

## 8. Runtime Output Boundary

Allowed output:

- metadata-only summary
- schema version
- `manifest_id`
- `artifact_id`
- `artifact_body_id`
- validation reference count / IDs if safe
- artifact flags
- safety flags
- count summary
- body-suppressed flags
- file-writing status
- safe relative output path if available
- reason codes
- failed checks
- safe summary label

Forbidden output:

- manifest body
- manifest JSON body
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
- final/gold/observed-after text
- performance proof

## 9. Initial Runtime Mode

Proposed initial mode:

- `metadata_only_no_file`

Expected behavior:

- no manifest file written
- `manifest_body_available=false`
- `manifest_file_written=false`
- `content_suppressed=true`
- `manifest_body_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_absolute_paths=true`
- `no_artifact_body_payload=true`
- `no_generated_policy_body=true`
- `no_request_body=true`
- `no_pointer_body=true`
- `no_expected_body=true`
- `no_performance_claims=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `non_proof_notice_checked=true`
- `path_policy_checked=true`
- `content_policy_checked=true`
- `release_quality_ready=false`

## 10. Future File Writing Mode

Design only:

- explicit `--manifest-out` required
- dedicated root: `tmp/frozen_policy_generation_manifest/`
- safe relative path only
- `.json` only
- reject absolute paths
- reject home paths
- reject parent traversal
- reject cloud/private markers
- reject hidden directories
- reject unsafe filenames
- reject too-long paths
- reject overwrite without safe policy
- summary must not print absolute resolved paths

Writing should be separate from the initial runtime implementation if needed.

## 11. Fail-Closed Behavior

Fail closed if:

- input pointer missing
- input JSON malformed
- unknown schema version
- request tries to include manifest body
- request tries to include artifact body payload
- request tries to include generated policy body
- request includes raw rows
- request includes logits
- request includes private paths
- manifest output path is unsafe
- overwrite is attempted without policy
- manifest body generation is requested before support exists
- artifact writer CLI integration is requested before support exists
- real-data path is requested or detected

## 12. Summary Fields

Proposed fields:

- `mode=manifest_writer`
- `result_schema_version=learner_state_frozen_policy_generation_manifest_writer_result_v0.1`
- `writer_status`
- `manifest_writer_mode`
- `manifest_id`
- `artifact_id`
- `artifact_body_id`
- `validation_reference_count`
- `release_quality_reference_count`
- `manifest_body_available`
- `manifest_file_written`
- `manifest_output_path_available`
- `manifest_output_path_safe_relative`
- `reason_codes`
- `failed_checks`
- `safety_flags`
- `count_summary`
- `safe_summary`
- `release_quality_ready=false`

## 13. Count Summary Fields

Proposed count summary fields:

- `manifest_metadata_field_count`
- `validation_reference_count`
- `release_quality_reference_count`
- `raw_row_count`
- `logits_dump_count`
- `private_path_count`
- `absolute_path_count`
- `artifact_body_payload_count`
- `generated_policy_body_count`
- `manifest_body_count`
- `request_body_count`
- `pointer_body_count`
- `expected_body_count`
- `performance_metric_count`
- `written_file_count`

## 14. Safety Flags

Proposed safety flags:

- `content_suppressed`
- `manifest_body_suppressed`
- `no_raw_rows`
- `no_logits_dump`
- `no_private_paths`
- `no_absolute_paths`
- `no_artifact_body_payload`
- `no_generated_policy_body`
- `no_manifest_body_nesting`
- `no_request_body`
- `no_pointer_body`
- `no_expected_body`
- `no_performance_claims`
- `synthetic_only_checked`
- `no_oracle_checked`
- `non_proof_notice_checked`
- `path_policy_checked`
- `content_policy_checked`
- `file_writing_checked`

## 15. Relation To Static Manifest Writer Fixture Validation

Static fixture validation checks contract fixtures. Runtime writer validation
would check actual metadata-only result construction.

Static fixture validation success does not imply runtime writer success. The
runtime writer should have separate tests, a separate Makefile target,
separate release-quality entry, and a separate remote marker later.

## 16. Relation To Artifact Writer / Artifact Body

Artifact writer runtime produces metadata-only artifact writer summaries.
Artifact body generation produces suppressed or safe-metadata body summaries.

The future manifest writer should aggregate references to those safe
summaries. It must not reopen, copy, or embed their body payloads.

Artifact writer CLI integration remains separate.

## 17. Future Fixture / Runtime Staging

Proposed next steps:

- Step390: runtime fixture contract design
- Step391: runtime fixture JSON creation
- Step392: runtime API/CLI implementation
- Step393: runtime tests
- Step394: Makefile target design
- Step395: Makefile target implementation
- Step396: release-quality integration design
- Step397: wrapper integration
- Step398: remote/manual run record workflow design
- Step399: remote/manual run status marker

## 18. Safety Interpretation

Runtime writer success later would mean metadata-only manifest summary
construction works. It would not mean manifest file writing is ready unless
file writing is separately implemented and validated.

It would not mean artifact writer CLI integration, production readiness, model
performance, or real-data readiness.

## 19. Beginner-Friendly Explanation

A runtime writer is code that would build a manifest writer result from safe
metadata inputs. It is different from the static fixture validator, which only
checks fixture contracts.

The initial design avoids manifest bodies because a manifest should be a safe
metadata index, not a payload container.

Default no-file mode keeps the first implementation narrow: it can prove safe
summary construction before adding file-writing behavior.

The manifest writer should reference artifact writer and artifact body
summaries because those summaries are already safety-reviewed. It should not
copy their bodies.

## 20. Docs Safety Policy

- no JSON body examples
- no manifest body examples
- no request/pointer body examples
- no artifact body payload examples
- no raw logs
- no private path examples
- field names, command shape, and metadata-only policy only

## 21. What This Does Not Do

- does not implement manifest writer
- does not write manifest files
- does not create runtime fixtures
- does not implement runtime validator
- does not change Makefile, wrapper, or workflow
- does not use real data
- does not compute metrics
- does not prove production readiness

## 22. Next Recommended Steps

- runtime fixture contract design
- runtime fixtures
- metadata-only runtime writer implementation
- Makefile / release-quality / remote marker steps

## 23. Step390 Runtime Fixture Contract Design Status

Step390 adds the docs-only runtime fixture contract design:

[Frozen policy generation manifest writer runtime fixture contract design](frozen_policy_generation_manifest_writer_runtime_fixture_contract_design.md).

The fixture contract fixes the future runtime fixture root, case structure,
schema names, valid/invalid taxonomy, expected counts, request and pointer
policy, expected result contract, path/content policy, and validator staging.
It does not create runtime fixture JSON, implement a runtime writer, write
manifest files, implement a runtime validator, change Makefile, change the
wrapper, change workflow YAML, change Python code/tests, change fixture JSON,
connect artifact writer CLI, use real data, compute metrics, or claim
production readiness.

## 24. Step391 Runtime Fixture Root Creation Status

Step391 creates the runtime fixture root described by the Step390 contract:

[Frozen policy generation manifest writer runtime fixtures](../tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime/README.md).

The fixture root is synthetic-only, metadata-only, and no-oracle. It contains
31 case directories and 155 JSON files. It does not implement the manifest
writer runtime, implement a CLI, implement a runtime validator, generate
manifest bodies, write manifest files, connect artifact writer CLI, use real
data, compute metrics, or claim production readiness.

## 25. Step392 Runtime Fixture Validator Design Status

Step392 adds the docs-only runtime fixture validator design:

[Frozen policy generation manifest writer runtime fixture validator design](frozen_policy_generation_manifest_writer_runtime_fixture_validator_design.md).

The validator remains separate from the runtime API. It will validate fixture
contracts only and will not execute the runtime writer, write manifest files,
or connect artifact writer CLI.

## 26. Step393 Runtime Fixture Validator Implementation Status

Step393 implements the static runtime fixture validator for the 31-case /
155-JSON runtime fixture root. The validator is separate from the future
runtime writer API and does not execute runtime writer logic, implement the
manifest writer CLI, generate manifest bodies, write manifest files, connect
artifact writer CLI, use real data, compute metrics, or claim production
readiness.

## 27. Step394 Makefile Target Design Status

Step394 adds the docs-only standalone Makefile target design for running the
runtime fixture validator from `make`:

[Frozen policy generation manifest writer runtime fixture validator Makefile target design](frozen_policy_generation_manifest_writer_runtime_fixture_validator_makefile_target_design.md).

The target remains unimplemented in this step. Runtime writer implementation,
manifest writer CLI implementation, manifest file writing, release-quality
integration, and artifact writer CLI integration remain separate.

## 28. Step395 Makefile Target Implementation Status

Step395 implements the standalone Makefile target for the static runtime
fixture validator. The target remains separate from the runtime API and does
not implement or execute manifest writer runtime behavior, manifest writer
CLI behavior, manifest file writing, release-quality integration, or artifact
writer CLI integration.

## 29. Step396 Runtime Fixture Release-Quality Integration Design Status

Step396 adds the docs-only release-quality integration design:

[Frozen policy generation manifest writer runtime fixture release-quality integration design](frozen_policy_generation_manifest_writer_runtime_fixture_release_quality_integration_design.md).

The runtime writer remains unimplemented and separate. The design concerns
only future wrapper placement for static runtime fixture validation.

## 30. Step397 Runtime Fixture Wrapper Integration Status

Step397 adds the runtime fixture validator target to the release-quality
wrapper. This does not implement or execute the manifest writer runtime,
manifest writer CLI, manifest body generation, manifest file writing, or
artifact writer CLI integration.

## 31. Step398 Runtime Fixture Remote Run Record Workflow Design Status

Step398 adds a docs-only remote/manual run record workflow for the runtime
fixture validator wrapper integration:

[Frozen policy generation manifest writer runtime fixture release-quality remote run record workflow](frozen_policy_generation_manifest_writer_runtime_fixture_release_quality_remote_run_record_workflow.md).

The runtime writer remains unimplemented and separate. The workflow design
does not create a status marker, run a workflow, write manifest files, connect
artifact writer CLI, use real data, compute metrics, or claim production
readiness.

## 32. Step399 Runtime Fixture Remote Run Status Marker Status

Step399 creates the public-safe remote/manual Release Quality status marker
for runtime fixture validation:

[Learner-state frozen policy generation manifest writer runtime fixture release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_runtime_fixture_release_quality_remote_run_status.md).

The marker records safe pass-only/count-only wrapper evidence only. It does
not implement or execute the manifest writer runtime, write manifest files,
connect artifact writer CLI, use real data, compute metrics, or claim
production readiness.

## 33. Step400 Runtime Implementation Design Status

Step400 adds the docs-only runtime implementation design:

[Frozen policy generation manifest writer runtime implementation design](frozen_policy_generation_manifest_writer_runtime_implementation_design.md).

The design fixes the future metadata-only no-file runtime scope, proposed
module/API/CLI, input parsing, safe pointer handling, result construction,
safety audit, fail-closed behavior, tests, and staging. It does not implement
the runtime writer, implement the CLI, write manifest files, connect artifact
writer CLI, use real data, compute metrics, or claim production readiness.

## 34. Step401 Runtime Implementation Status

Step401 implements the initial metadata-only no-file runtime module and CLI:

- `learner_state.frozen_policy_generation_manifest_writer`
- `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer`

The implementation reads synthetic request/pointer metadata and emits a
body-free manifest writer result summary. It keeps `--manifest-out`,
manifest file writing, manifest body generation, artifact writer CLI
integration, Makefile target wiring, release-quality integration, real-data
use, metric computation, and production readiness out of scope.

## 35. Step402 Makefile Target Design Status

Step402 adds the docs-only Makefile target design for a future runtime smoke:

[Frozen policy generation manifest writer runtime Makefile target design](frozen_policy_generation_manifest_writer_runtime_makefile_target_design.md).

The design keeps runtime API behavior unchanged. It does not add a Makefile
target, release-quality integration, `--manifest-out`, manifest file writing,
manifest body generation, artifact writer CLI integration, real-data use,
metrics, or production readiness claims.

## 36. Step403 Makefile Target Implementation Status

Step403 implements the standalone Makefile runtime smoke target:

`check-learner-state-frozen-policy-generation-manifest-writer-runtime`

The target invokes the existing metadata-only no-file CLI with the valid
minimal runtime fixture. The API boundary remains unchanged: no
`--manifest-out`, no manifest file writing, no manifest body generation, no
artifact writer CLI integration, no real data, no metrics, and no production
readiness claim. The target is not added to release-quality in this step.

## 37. Step404 Release-Quality Integration Design Status

Step404 adds the docs-only release-quality integration design for the runtime
smoke target:

[Frozen policy generation manifest writer runtime release-quality integration design](frozen_policy_generation_manifest_writer_runtime_release_quality_integration_design.md).

The API boundary remains unchanged. The design does not add wrapper
integration, change workflow YAML, change Makefile, change Python code/tests,
change fixture JSON, write manifest files, add `--manifest-out`, generate
manifest bodies, connect artifact writer CLI, use real data, compute metrics,
or claim production readiness.

## 38. Related Documents

- [Frozen policy generation manifest writer boundary design](frozen_policy_generation_manifest_writer_boundary_design.md)
- [Frozen policy generation manifest writer fixture contract design](frozen_policy_generation_manifest_writer_fixture_contract_design.md)
- [Frozen policy generation manifest writer fixture validator design](frozen_policy_generation_manifest_writer_fixture_validator_design.md)
- [Frozen policy generation manifest writer fixture release-quality integration design](frozen_policy_generation_manifest_writer_fixture_release_quality_integration_design.md)
- [Learner-state frozen policy generation manifest writer fixture release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_fixture_release_quality_remote_run_status.md)
- [Learner-state frozen policy generation manifest writer runtime fixture release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_runtime_fixture_release_quality_remote_run_status.md)
- [Frozen policy generation manifest writer runtime fixture contract design](frozen_policy_generation_manifest_writer_runtime_fixture_contract_design.md)
- [Frozen policy generation manifest writer runtime fixtures](../tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime/README.md)
- [Frozen policy generation manifest writer runtime fixture validator design](frozen_policy_generation_manifest_writer_runtime_fixture_validator_design.md)
- [Frozen policy generation manifest writer runtime fixture release-quality integration design](frozen_policy_generation_manifest_writer_runtime_fixture_release_quality_integration_design.md)
- [Frozen policy generation manifest writer runtime fixture release-quality remote run record workflow](frozen_policy_generation_manifest_writer_runtime_fixture_release_quality_remote_run_record_workflow.md)
- [Frozen policy generation manifest writer runtime implementation design](frozen_policy_generation_manifest_writer_runtime_implementation_design.md)
- [Frozen policy generation manifest writer runtime Makefile target design](frozen_policy_generation_manifest_writer_runtime_makefile_target_design.md)
- [Frozen policy generation manifest writer runtime release-quality integration design](frozen_policy_generation_manifest_writer_runtime_release_quality_integration_design.md)
- [Frozen policy generation artifact writer design](frozen_policy_generation_artifact_writer_design.md)
- [Frozen policy generation artifact body generation design](frozen_policy_generation_artifact_body_generation_design.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)
