# Frozen Policy Generation Manifest Writer Fixture Release-Quality Integration Design

## 1. Purpose

This document fixes the docs-only design for adding the standalone manifest
writer fixture validator target to the release-quality wrapper, and records
the later Step386 wrapper integration status.

This is not wrapper implementation, not a workflow change, not manifest writer
implementation, not manifest file writing, not artifact writer CLI
integration, and not a production readiness claim.

## 2. Current State

- the manifest writer fixture validator module exists
- the manifest writer fixture validator CLI exists
- the manifest writer fixture Makefile target exists
- the target validates 30 cases and 150 JSON files
- the target is static fixture validation only
- the target does not write manifest files
- the target is in the release-quality wrapper after Step386
- the manifest writer does not exist
- manifest file writing does not exist
- artifact writer CLI integration does not exist

## 3. Proposed Wrapper Insertion Point

Candidate A:

artifact body isolated write validation immediately after artifact body
isolated write validation and before config/scoring smoke checks.

Candidate B:

artifact writer fixture validation immediately after artifact writer fixture
validation and before artifact writer runtime smoke.

Candidate C:

artifact body fixture validation immediately after artifact body fixture
validation and before artifact body generation smoke.

Recommended: Candidate A, immediately after artifact body isolated write
validation and before config/scoring smoke checks.

Reasons:

- manifest writer fixture validation is a later frozen policy generation
  artifact metadata-chain check
- the sequence can read as artifact writer, artifact body, file-writing
  contract, isolated write behavior, then manifest metadata index contract
- config/scoring smoke checks are a separate family, so this check should stay
  before them
- this is not runtime manifest writer smoke, so it should not sit before
  artifact writer runtime smoke
- placing it near artifact body fixture validation is too early in the chain

Expected future order:

- artifact writer fixture validation
- artifact writer runtime smoke
- artifact body fixture validation
- artifact body generation CLI smoke
- artifact body generation safe-metadata CLI smoke
- artifact body file writing fixture validation
- artifact body isolated write validation
- manifest writer fixture validation
- config and scoring smoke checks

## 4. Proposed Wrapper Command

`make check-learner-state-frozen-policy-generation-manifest-writer-fixtures`

## 5. Proposed Wrapper Label

`release_quality_check: learner-state frozen policy generation manifest writer fixture validation`

## 6. Expected Wrapper Behavior

If the target passes, release-quality should continue. If the target fails,
release-quality should fail.

Expected output includes:

- `mode=manifest_writer_fixture_validation`
- `validation_schema_version=learner_state_frozen_policy_generation_manifest_writer_fixture_validation_v0.1`
- `total_cases=30`
- `valid_cases=5`
- `invalid_cases=25`
- `pass_metadata_only_no_file_cases=3`
- `pass_manifest_file_written_cases=1`
- `usage_error_cases=11`
- `fail_closed_cases=15`
- `matched_cases=30`
- `mismatched_cases=0`
- `input_error_cases=0`
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
- `release_quality_ready=false`

Expected output does not include manifest bodies, manifest files, fixture JSON
bodies, request/pointer/expected bodies, artifact body payloads, generated
policy bodies, private paths, absolute paths, or performance evidence.

## 7. Failure Interpretation

Treat these as release-quality failures:

- required fixture file missing
- malformed JSON
- schema version mismatch
- case ID mismatch
- expected category mismatch
- expected status mismatch
- valid case has unsafe path sentinel
- valid case has forbidden include flag true
- invalid case missing expected reason code
- reason code mismatch
- expected result contract mismatch
- raw rows marker detected
- logits marker detected
- private path marker detected
- absolute path marker detected
- artifact body payload marker detected
- generated policy body marker detected
- manifest body nesting marker detected
- request/pointer/expected body marker detected
- performance claim marker detected
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
- `release_quality_ready=false`

Forbidden log content:

- manifest body
- manifest JSON body
- `manifest_writer_request` body
- `artifact_writer_result_pointer` body
- `artifact_body_generation_result_pointer` body
- `expected_manifest_writer_result` body
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

Manifest writer fixture validation checks manifest writer metadata index
fixture contracts only. Runtime manifest writer smoke remains separate and
later. Manifest file writing remains separate and later.

## 10. Release-Quality Staging

Recommended staging:

- first add static manifest writer fixture validation to the wrapper
- then record a remote/manual marker for this static fixture validation
- only later design and implement the runtime manifest writer
- later runtime manifest writer smoke should get its own target and
  release-quality integration

Runtime readiness must not be inferred from static fixture validation.

## 11. Makefile / Workflow Status

The Makefile target exists. The release-quality wrapper is not yet changed.

The workflow should not need to change if it already invokes the wrapper. The
future implementation step should modify only the wrapper unless a specific
workflow need appears.

Workflow YAML diff should remain none unless necessary.

## 12. Testing Plan for Future Wrapper Implementation

Future checks:

- standalone manifest writer fixture target passes
- `make check-release-quality` includes the new label
- `make check-release-quality` passes
- target output includes `total_cases=30`
- target output includes `matched_cases=30`
- target output includes `input_error_cases=0`
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

`docs/status/learner_state_frozen_policy_generation_manifest_writer_fixture_release_quality_remote_run_status.md`

The marker should record pass-only/count-only metadata. Raw logs must not be
copied.

Allowed marker fields include:

- target included: yes
- label
- command
- `total_cases=30`
- `matched_cases=30`
- `input_error_cases=0`
- safety flags
- no manifest body copied
- no fixture JSON body copied
- no artifact body payload copied
- no generated policy body copied
- no private or absolute paths copied
- no performance evidence

## 14. No-Oracle / Synthetic-Only Boundary

The target uses synthetic-only manifest writer fixtures. It uses no real data,
no participant data, no raw learner text, no final/gold/observed-after text,
no expected action payload, no scoring feedback payload, no artifact body
payload in logs, no generated policy body, no manifest body, no logits, no raw
rows, and no private paths.

## 15. Safety Interpretation

Release-quality success with this target would mean the static manifest writer
fixture contracts matched expected outcomes.

It would not mean the manifest writer is implemented, manifest files can be
written, artifact writer CLI integration exists, production artifact
management is ready, model performance is proven, or real-data readiness is
established.

## 16. Beginner-Friendly Explanation

Release-quality is the project-level check bundle that protects the normal
safe path before release work continues.

Adding static fixture validation to release-quality means the fixture contract
is checked every time the wrapper runs. It does not run a future manifest
writer; it only checks that the synthetic metadata-only cases remain valid.

Runtime manifest writer smoke is separate because it would execute future
writer behavior. This design is only about static contract coverage.

`release_quality_ready=false` stays false because this target is a contract
check, not proof that manifest writing or production file management is ready.

## 17. What This Does Not Do

- does not change workflow YAML
- does not implement manifest writer
- does not write manifest files
- does not connect artifact writer CLI
- does not compute metrics
- does not use real data
- does not prove production readiness

## 18. Next Recommended Steps

- Step388: remote/manual run status marker
- later: runtime manifest writer design and implementation
- later: runtime manifest writer Makefile and release-quality integration

## 19. Step386 Wrapper Integration Status

Step386 adds the manifest writer fixture validator target to the
release-quality wrapper immediately after artifact body isolated write
validation and before config/scoring smoke checks.

Wrapper label:

`release_quality_check: learner-state frozen policy generation manifest writer fixture validation`

Wrapper command:

`make check-learner-state-frozen-policy-generation-manifest-writer-fixtures`

This integration runs static fixture validation only. It does not change
workflow YAML, Makefile, Python code/tests, fixture JSON, implement a manifest
writer, generate manifest bodies, write manifest files, connect artifact
writer CLI, use real data, compute metrics, or claim production readiness.

## 20. Step387 Remote Run Record Workflow Design Status

Step387 adds the docs-only remote/manual run record workflow for a future
public-safe status marker:

[Frozen policy generation manifest writer fixture release-quality remote run record workflow](frozen_policy_generation_manifest_writer_fixture_release_quality_remote_run_record_workflow.md).

The workflow design records only pass-only/count-only metadata after a future
remote/manual Release Quality run. It does not create the actual status
marker, run a remote workflow, change workflow YAML, change the wrapper,
change Makefile, change Python code/tests, change fixture JSON, implement a
manifest writer, write manifest files, connect artifact writer CLI, use real
data, compute metrics, or claim production readiness.

## 21. Related Documents

- [Frozen policy generation manifest writer boundary design](frozen_policy_generation_manifest_writer_boundary_design.md)
- [Frozen policy generation manifest writer fixture contract design](frozen_policy_generation_manifest_writer_fixture_contract_design.md)
- [Frozen policy generation manifest writer fixture validator design](frozen_policy_generation_manifest_writer_fixture_validator_design.md)
- [Frozen policy generation manifest writer fixture validator Makefile target design](frozen_policy_generation_manifest_writer_fixture_validator_makefile_target_design.md)
- [Frozen policy generation manifest writer fixture release-quality remote run record workflow](frozen_policy_generation_manifest_writer_fixture_release_quality_remote_run_record_workflow.md)
- [Frozen policy generation manifest writer fixtures](../tests/fixtures/learner_state_frozen_policy_generation_manifest_writer/README.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)
