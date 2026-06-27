# Frozen Policy Generation Manifest Writer Runtime Fixture Release-Quality Integration Design

## 1. Purpose

This document fixes the docs-only design for adding the standalone manifest
writer runtime fixture validator target to the release-quality wrapper.

This is not wrapper implementation, not a workflow change, not manifest writer
runtime implementation, not manifest file writing, not artifact writer CLI
integration, and not a production readiness claim.

## 2. Current State

- the runtime fixture validator module exists
- the runtime fixture validator CLI exists
- the runtime fixture Makefile target exists
- the target validates 31 cases and 155 JSON files
- the target is static runtime fixture validation only
- the target does not execute a runtime writer
- the target does not write manifest files
- the target is not in release-quality
- static manifest writer fixture validation is already in release-quality
- the manifest writer runtime does not exist
- manifest file writing does not exist
- artifact writer CLI integration does not exist

## 3. Proposed Wrapper Insertion Point

Candidate A:

Immediately after static manifest writer fixture validation and before
config/scoring smoke checks.

Candidate B:

Immediately after artifact body isolated write validation and before static
manifest writer fixture validation.

Candidate C:

After config/scoring smoke checks.

Recommended: Candidate A, immediately after static manifest writer fixture
validation and before config/scoring smoke checks.

Reasons:

- runtime fixture validation is a natural downstream check after static
  manifest writer fixture validation
- the sequence reads as artifact writer, artifact body, isolated write,
  static manifest fixture, then runtime manifest fixture
- config/scoring smoke checks are a separate family, so the manifest writer
  fixture chain should stay together before them
- this is not runtime writer smoke, so it stays separate from any future
  runtime writer implementation position
- Candidate B reverses the static and runtime fixture order
- Candidate C splits the manifest writer fixture chain from the rest of the
  frozen policy generation artifact checks

Expected future order:

- artifact writer fixture validation
- artifact writer runtime smoke
- artifact body fixture validation
- artifact body generation CLI smoke
- artifact body generation safe-metadata CLI smoke
- artifact body file writing fixture validation
- artifact body isolated write validation
- static manifest writer fixture validation
- runtime manifest writer fixture validation
- config and scoring smoke checks

## 4. Proposed Wrapper Command

`make check-learner-state-frozen-policy-generation-manifest-writer-runtime-fixtures`

## 5. Proposed Wrapper Label

`release_quality_check: learner-state frozen policy generation manifest writer runtime fixture validation`

## 6. Expected Wrapper Behavior

If the target passes, release-quality should continue. If the target fails,
release-quality should fail.

Expected output includes:

- `mode=manifest_writer_runtime_fixture_validation`
- `validation_schema_version=learner_state_frozen_policy_generation_manifest_writer_runtime_fixture_validation_v0.1`
- `total_cases=31`
- `valid_cases=5`
- `invalid_cases=26`
- `pass_metadata_only_no_file_cases=5`
- `usage_error_cases=8`
- `fail_closed_cases=18`
- `matched_cases=31`
- `mismatched_cases=0`
- `input_error_cases=0`
- `total_json_files=155`
- `json_files_per_case=5`
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
- `runtime_writer_executed=false`
- `manifest_file_written=false`
- `release_quality_ready=false`

Expected output does not include a runtime writer execution, manifest bodies,
manifest files, fixture JSON bodies, request/pointer/expected bodies, artifact
body payloads, generated policy bodies, private paths, absolute paths, or
performance evidence.

## 7. Failure Interpretation

Treat these as release-quality failures:

- required fixture file missing
- malformed JSON
- schema version mismatch
- case ID mismatch
- expected category mismatch
- expected status mismatch
- request policy mismatch
- pointer policy mismatch
- expected result contract mismatch
- valid case has `manifest_out` unexpectedly
- valid case has `include_manifest_body=true`
- valid case has `allow_manifest_file_writing=true`
- valid pointer includes body payload, raw rows, or private path markers
- invalid case missing expected reason code
- reason code mismatch
- raw rows marker detected
- logits marker detected
- private path marker detected
- absolute path marker detected
- artifact body payload marker detected
- generated policy body marker detected
- manifest body marker detected
- request/pointer/expected body marker detected
- performance claim marker detected
- real data marker detected
- `mismatched_cases > 0`
- `input_error_cases > 0`
- validator internal error

These failures are not manifest writer runtime failures, not manifest file
writing failures, not artifact writer CLI integration failures, and not model
performance failures.

## 8. Log Safety Review

Allowed log content:

- label
- command
- mode
- validation schema version
- counts
- category names
- reason code names and counts
- safety flags
- `runtime_writer_executed=false`
- `manifest_file_written=false`
- `release_quality_ready=false`

Forbidden log content:

- manifest body
- manifest JSON body
- `manifest_writer_request` body
- `artifact_writer_result_pointer` body
- `artifact_body_generation_result_pointer` body
- `expected_manifest_writer_runtime_result` body
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
- GitHub raw logs
- full job output copied into docs

## 9. Relation to Existing Release-Quality Checks

Artifact writer fixture validation checks artifact writer metadata-only
contracts. Artifact writer runtime smoke checks metadata-only artifact writer
runtime behavior.

Artifact body fixture validation checks the artifact body contract. Artifact
body generation suppressed and safe-metadata checks validate body generation
summaries. Artifact body file writing fixture validation checks path/content
policy for artifact body files. Artifact body isolated write validation checks
actual artifact body write/no-write behavior in isolated temp roots.

Static manifest writer fixture validation checks metadata index fixture
contracts. Runtime manifest writer fixture validation checks runtime
request/pointer/expected-result fixture contracts.

Runtime manifest writer smoke remains separate and later. Manifest file
writing remains separate and later.

## 10. Release-Quality Staging

Recommended staging:

- first add static runtime fixture validation to the wrapper
- then record a remote/manual marker for this runtime fixture validation
- only later design and implement the runtime manifest writer
- later runtime manifest writer smoke should get its own target and
  release-quality integration

Runtime writer readiness must not be inferred from runtime fixture validation.

## 11. Makefile / Workflow Status

The Makefile target exists:

`check-learner-state-frozen-policy-generation-manifest-writer-runtime-fixtures`

The release-quality wrapper is not yet changed for this runtime fixture
target.

The workflow should not need to change if it already invokes the wrapper. The
future implementation step should modify only the wrapper unless a specific
workflow need appears.

Workflow YAML diff should remain none unless necessary.

## 12. Testing Plan for Future Wrapper Implementation

Future checks:

- standalone runtime fixture target passes
- `make check-release-quality` includes the new label
- `make check-release-quality` passes
- target output includes `total_cases=31`
- target output includes `matched_cases=31`
- target output includes `input_error_cases=0`
- target output includes `runtime_writer_executed=false`
- target output includes `manifest_file_written=false`
- target output includes `release_quality_ready=false`
- target output remains body-free
- no manifest body is printed
- no manifest files are written
- `tmp/frozen_policy_generation_manifest/` residue remains 0
- wrapper diff is limited
- workflow diff remains none
- all existing checks pass

## 13. Future Status Marker

After wrapper integration and a successful remote/manual Release Quality run,
a future status marker may be added.

Recommended future marker path:

`docs/status/learner_state_frozen_policy_generation_manifest_writer_runtime_fixture_release_quality_remote_run_status.md`

The marker should record pass-only/count-only metadata. Raw logs must not be
copied.

Allowed marker fields include:

- target included: yes
- label
- command
- `total_cases=31`
- `matched_cases=31`
- `input_error_cases=0`
- `runtime_writer_executed=false`
- `manifest_file_written=false`
- safety flags
- no manifest body copied
- no fixture JSON body copied
- no artifact body payload copied
- no generated policy body copied
- no private or absolute paths copied
- no performance evidence

## 14. No-Oracle / Synthetic-Only Boundary

The target uses synthetic-only manifest writer runtime fixtures. It uses no
real data, no participant data, no raw learner text, no final/gold/observed-
after text, no expected action payload, no scoring feedback payload, no
artifact body payload in logs, no generated policy body, no manifest body, no
logits, no raw rows, and no private paths.

## 15. Safety Interpretation

Release-quality success with this target would mean the static runtime
fixture contracts matched expected outcomes.

It would not mean the manifest writer runtime is implemented, manifest files
can be written, artifact writer CLI integration exists, production file output
is ready, model performance is proven, or real-data readiness is established.

## 16. Beginner-Friendly Explanation

Release-quality is the project-level check bundle that protects the normal
safe path before release work continues.

Adding runtime fixture validation to release-quality means the future runtime
request, pointer, and expected-result fixture contracts are checked every time
the wrapper runs.

Runtime manifest writer smoke is separate because it would execute future
writer behavior. This target only validates fixture contracts, so
`runtime_writer_executed=false` remains the expected state.

Passing this target would not prove that the manifest writer runtime exists.
It only proves that the synthetic metadata-only fixture contracts remain
internally consistent.

## 17. What This Does Not Do

- does not change workflow YAML
- does not implement manifest writer runtime
- does not write manifest files
- does not connect artifact writer CLI
- does not compute metrics
- does not use real data
- does not prove production readiness

## 18. Next Recommended Steps

- Step399: remote/manual run status marker
- later: runtime manifest writer design / implementation
- later: manifest file writing design / implementation
- later: artifact writer CLI integration design / implementation

## 19. Related Documents

- [Frozen policy generation manifest writer runtime fixture validator Makefile target design](frozen_policy_generation_manifest_writer_runtime_fixture_validator_makefile_target_design.md)
- [Frozen policy generation manifest writer runtime fixture validator design](frozen_policy_generation_manifest_writer_runtime_fixture_validator_design.md)
- [Frozen policy generation manifest writer runtime fixture contract design](frozen_policy_generation_manifest_writer_runtime_fixture_contract_design.md)
- [Frozen policy generation manifest writer runtime fixtures](../tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime/README.md)
- [Frozen policy generation manifest writer runtime API design](frozen_policy_generation_manifest_writer_runtime_api_design.md)
- [Frozen policy generation manifest writer boundary design](frozen_policy_generation_manifest_writer_boundary_design.md)
- [Frozen policy generation manifest writer fixture release-quality integration design](frozen_policy_generation_manifest_writer_fixture_release_quality_integration_design.md)
- [Frozen policy generation manifest writer runtime fixture release-quality remote run record workflow](frozen_policy_generation_manifest_writer_runtime_fixture_release_quality_remote_run_record_workflow.md)
- [Learner-state frozen policy generation manifest writer fixture release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_fixture_release_quality_remote_run_status.md)
- [Learner-state frozen policy generation manifest writer runtime fixture release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_runtime_fixture_release_quality_remote_run_status.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)

## 20. Step397 Wrapper Integration Status

Step397 adds the runtime fixture validator target to the release-quality
wrapper immediately after static manifest writer fixture validation and before
config/scoring smoke checks.

Wrapper label:

`release_quality_check: learner-state frozen policy generation manifest writer runtime fixture validation`

Wrapper command:

`make check-learner-state-frozen-policy-generation-manifest-writer-runtime-fixtures`

This integration runs static runtime fixture validation only. It does not
change workflow YAML, Makefile, Python code/tests, fixture JSON, implement or
execute a manifest writer runtime, implement a manifest writer CLI, generate
manifest bodies, write manifest files, connect artifact writer CLI, use real
data, compute metrics, or claim production readiness.

## 21. Step398 Remote Run Record Workflow Design Status

Step398 adds the docs-only remote/manual Release Quality run record workflow
for this runtime fixture validator wrapper integration:

[Frozen policy generation manifest writer runtime fixture release-quality remote run record workflow](frozen_policy_generation_manifest_writer_runtime_fixture_release_quality_remote_run_record_workflow.md).

The workflow design defines the future status marker path and safe
pass-only/count-only metadata to record after a remote/manual run. It does not
create the status marker, run GitHub Actions, change workflow YAML, change the
wrapper, change Makefile, change Python code/tests, change fixture JSON,
execute a manifest writer runtime, write manifest files, connect artifact
writer CLI, use real data, compute metrics, or claim production readiness.

## 22. Step399 Remote Run Status Marker Status

Step399 creates the public-safe remote/manual Release Quality status marker:

[Learner-state frozen policy generation manifest writer runtime fixture release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_runtime_fixture_release_quality_remote_run_status.md).

The marker records the runtime fixture validator wrapper evidence using
pass-only/count-only metadata. It does not change workflow YAML, the wrapper,
Makefile, Python code/tests, fixture JSON, execute a manifest writer runtime,
write manifest files, connect artifact writer CLI, use real data, compute
metrics, or claim production readiness.
