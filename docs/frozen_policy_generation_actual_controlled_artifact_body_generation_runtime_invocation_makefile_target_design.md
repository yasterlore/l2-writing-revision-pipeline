# Actual-Controlled Artifact Body Generation Runtime Invocation Makefile Target Design

## 1. Title

Actual-Controlled Artifact Body Generation Runtime Invocation Makefile Target Design

## 2. Scope

This document is a design-only / docs-only plan for running the Step593 v0.4
actual-controlled direct runtime CLI through a future standalone Makefile
target.

This Step594 document does not:

- change `Makefile`
- change the release-quality wrapper
- change workflows
- change Python code or tests
- change fixture JSON
- change runtime implementation
- implement manifest writer integration
- perform file writing
- prove production readiness, real-data readiness, or model performance

The purpose is to design the future Step595 target name, help text, command,
expected output, placement, relationship to existing targets, validation
commands, and safety boundary.

## 3. Prior Chain Dependency

The target design depends on the completed Step569-Step593 chain:

- Step569-Step574: planned-only runtime invocation fixture, validator, and
  standalone target chain.
- Step575-Step579: planned-only v0.3 runtime mode and standalone target chain.
- Step580-Step583: release-quality integration, remote/manual run record
  workflow, and remote status marker chain.
- Step584: planned-only v0.3 release-quality chain final safety review.
- Step585: actual controlled invocation design.
- Step586: actual-controlled fixture/schema contract design.
- Step587: actual-controlled fixture root creation.
- Step588: actual-controlled fixture validator design.
- Step589: actual-controlled fixture validator implementation.
- Step590: actual-controlled fixture validator Makefile target design.
- Step591: actual-controlled fixture validator Makefile target implementation.
- Step592: actual-controlled runtime implementation refinement design.
- Step593: actual-controlled runtime implementation.

Step593 provides the direct v0.4 runtime CLI behavior. It does not add a
Makefile target. Release-quality wrapper integration is still not implemented
for the v0.4 actual-controlled runtime smoke.

## 4. Target Runtime CLI

Runtime module:

- `python/learner_state/frozen_policy_generation_artifact_body_generation_runtime_integration.py`

Direct CLI:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_generation_runtime_integration \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled \
  --fixture-case valid/valid_actual_controlled_safe_metadata_invocation \
  --mode artifact-body-runtime-invocation-controlled \
  --actual-invocation \
  --summary-only \
  --no-file-writing \
  --no-manifest-writer \
  --fail-closed-on-unsafe-output
```

Primary fixture root:

- `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled/`

Primary fixture case:

- `valid/valid_actual_controlled_safe_metadata_invocation`

## 5. Proposed Makefile Target

Recommended target name:

- `check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation`

Recommended help text:

- `Run actual-controlled artifact body generation runtime invocation smoke`

Recommended command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_generation_runtime_integration --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_generation_runtime_invocation_actual_controlled --fixture-case valid/valid_actual_controlled_safe_metadata_invocation --mode artifact-body-runtime-invocation-controlled --actual-invocation --summary-only --no-file-writing --no-manifest-writer --fail-closed-on-unsafe-output
```

Do not add this target in Step594. Step595 should implement it.

## 6. Expected Target Output

The future Makefile target should produce the same public-safe summary as the
Step593 direct v0.4 CLI. Expected fields include:

- `mode=artifact_body_generation_runtime_integration`
- `runtime_schema_version=learner_state_frozen_policy_generation_artifact_body_generation_runtime_integration_v0.4`
- `status=pass`
- `reason_code=none`
- `exit_code_category=zero`
- `case_id=valid/valid_actual_controlled_safe_metadata_invocation`
- `integration_mode=artifact-body-runtime-invocation-controlled`
- `artifact_body_runtime_invoked=True`
- `artifact_body_runtime_invocation_planned=False`
- `artifact_body_runtime_mode=controlled_metadata_only_invocation`
- `artifact_body_generation_cli_invoked=True`
- `artifact_body_generation_cli_exit_code_category=zero`
- `artifact_body_generation_cli_output_scanned=True`
- `artifact_body_generation_cli_output_body_free=True`
- `artifact_body_payload_available=False`
- `artifact_body_payload_emitted=False`
- `artifact_body_payload_detected=False`
- `safe_metadata_body_available=True`
- `safe_metadata_body_field_count=5`
- `content_suppressed=True`
- `body_suppressed=True`
- `summary_only=True`
- `request_body_detected=False`
- `pointer_body_detected=False`
- `expected_body_detected=False`
- `manifest_body_detected=False`
- `generated_policy_body_detected=False`
- `raw_stdout_body_suppressed=True`
- `raw_stderr_body_suppressed=True`
- `raw_rows_detected=False`
- `logits_detected=False`
- `probabilities_detected=False`
- `private_path_detected=False`
- `absolute_path_detected=False`
- `raw_learner_text_detected=False`
- `real_data_marker_detected=False`
- `performance_metric_body_detected=False`
- `file_writing_enabled=False`
- `file_writing_detected=False`
- `manifest_writer_invoked=False`
- `artifact_file_written=False`
- `manifest_file_written=False`
- `runtime_safety_scan_passed=True`
- `runtime_fail_closed=False`
- `residue_file_count=0`
- `production_readiness_claimed=False`
- `real_data_readiness_claimed=False`
- `performance_claims_present=False`
- `metadata_file_count=7`
- `unsafe_signal_count=0`

## 7. Makefile Placement

Recommended placement:

- near the existing planned-only v0.3 runtime target:
  `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation`
- near the actual-controlled fixture validator target:
  `check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation-fixtures`
- after the actual-controlled fixture validator target and before any future
  release-quality integration discussion

Step595 should add a standalone Makefile target only. Release-quality wrapper
integration should be deferred to a later design step after the standalone
target passes. The target should be added to `.PHONY` and included in
`make help`.

## 8. Relationship to Existing Targets

Existing targets that must remain unchanged:

- `check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation-fixtures`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation-fixtures`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-invocation`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-runtime-integration-safe-metadata-runtime`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata`

The future target:

- runs the v0.4 actual-controlled direct runtime smoke
- uses the actual-controlled fixture root
- uses only the primary valid case
- requires `--actual-invocation`
- requires `--summary-only`
- requires `--no-file-writing`
- requires `--no-manifest-writer`
- requires `--fail-closed-on-unsafe-output`
- does not replace the actual-controlled fixture validator target
- does not replace the planned-only v0.3 target
- does not replace the safe-metadata runtime smoke
- does not replace the artifact body safe-metadata CLI smoke
- does not invoke manifest writer
- does not write files
- is not release-quality integrated yet

## 9. Step595 Implementation Plan

Step595 should:

- update `Makefile`
- add a `.PHONY` entry
- add a `make help` entry
- add the target command
- not modify Python code or tests
- not modify fixture JSON
- not modify the release-quality wrapper
- not modify workflows
- not modify runtime implementation
- not invoke manifest writer
- not write files
- run the new target
- run the direct v0.4 CLI
- run focused runtime tests
- run the actual-controlled fixture validator target
- run the actual-controlled direct fixture validator CLI
- run the existing planned-only validator target
- run the existing planned-only v0.3 runtime target
- run the existing safe-metadata runtime target
- run the artifact body safe-metadata CLI smoke
- run `make check-python`
- run compileall
- confirm fixture JSON diff remains unchanged
- update root README and full technical specification related docs because
  Makefile target implementation is an implementation step

## 10. Safety Boundary

The proposed Makefile target must:

- run only the v0.4 actual-controlled direct runtime smoke
- read only synthetic metadata-only fixtures
- call artifact body generation only in controlled metadata-only mode
- output only count-only / public-safe metadata
- not print fixture JSON body
- not print request body
- not print pointer body
- not print expected body
- not print artifact body payload
- not print manifest body
- not print generated policy body
- not print raw stdout/stderr body
- not print raw rows
- not print logits/probabilities
- not print private/absolute path values
- not print raw learner text
- not use real participant data
- not invoke manifest writer
- not enable file writing
- not produce residue

## 11. Failure Interpretation

- Target failure means the v0.4 actual-controlled runtime smoke or its safety
  scan failed.
- Target failure may indicate fixture mismatch, CLI flag error, unsafe output
  marker, subprocess failure, or compatibility break.
- Target pass means the primary v0.4 controlled metadata-only runtime smoke
  passed.
- Target pass does not prove runtime correctness generally.
- Target pass does not prove artifact body payload correctness.
- Target pass does not imply release-quality integration.
- Target pass does not imply production readiness or real-data readiness.

## 12. Non-Equivalence Cautions

- Makefile target design is not Makefile implementation.
- Future target pass will not prove runtime correctness generally.
- Future target pass will not prove artifact body payload correctness.
- v0.4 actual-controlled target is still metadata-only / body-free smoke.
- Planned-only v0.3 pass remains not actual invocation.
- Artifact body generation safe-metadata CLI smoke is not equivalent to
  actual-controlled runtime invocation.
- Count-only metadata is not free-form body safety proof.
- Manifest writer validators are separate.
- Release-quality success is not production readiness.
- Synthetic-only pass is not real-data readiness.

## 13. Non-Claims

- production readiness is not claimed
- real-data readiness is not claimed
- model performance is not claimed
- F1 / accuracy / ECE / AURCC achievement is not claimed
- artifact body generation integration correctness is not claimed
- artifact body generation runtime correctness generally is not claimed
- manifest writer integration correctness is not claimed
- manifest writer file-writing production readiness is not claimed
- artifact body payload correctness is not claimed
- safe-metadata free-form body safety is not claimed
- manifest body generation correctness is not claimed
- generated policy quality is not claimed
- learner-state estimator correctness is not claimed
- artifact writer CLI actual invocation correctness generally is not claimed
- runtime actual invocation correctness generally is not claimed

## 14. Public-Safe Checklist

- [x] no raw logs
- [x] no full job output
- [x] no copied GitHub log blocks
- [x] no screenshots containing raw logs
- [x] no fixture JSON body
- [x] no request body
- [x] no pointer body
- [x] no expected body
- [x] no written file JSON body
- [x] no manifest body
- [x] no artifact body payload
- [x] no generated policy body
- [x] no raw stdout/stderr body
- [x] no raw rows
- [x] no logits/probabilities
- [x] no private paths
- [x] no absolute paths
- [x] no raw learner text
- [x] no real participant data
- [x] no performance claims
- [x] no production readiness claims
- [x] no real-data readiness claims

## 15. Recommended Next Step

Recommended next step:

- Step595: actual-controlled runtime invocation Makefile target implementation

Do not proceed to release-quality wrapper integration before the standalone
target is implemented and checked.

## Step595 Implementation Status

Step595 implements the standalone Makefile target
`check-learner-state-frozen-policy-generation-actual-controlled-artifact-body-generation-runtime-invocation`
with help text `Run actual-controlled artifact body generation runtime
invocation smoke`. The target runs the Step593 v0.4 runtime CLI against
`valid/valid_actual_controlled_safe_metadata_invocation`, remains outside
release-quality, does not invoke manifest writer, and does not write files.

## Step596 Release-Quality Integration Design Reference

Step596 adds
`docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_release_quality_integration_design.md`
as a design-only / docs-only plan for future wrapper integration of this
target together with the Step591 actual-controlled fixture validator target.
It does not change the wrapper, Makefile, workflows, Python code/tests,
fixture JSON, manifest writer integration, or file writing.

## Step597 Release-Quality Integration Status

Step597 adds this target to `scripts/check_release_quality.sh` after the
actual-controlled fixture validator target and before artifact body fixture /
CLI checks. The Makefile target remains unchanged, and Step597 does not change
workflow files, Python code/tests, fixture JSON, manifest writer integration,
or file writing.

## Step598 Remote Run Record Workflow Reference

Step598 adds a design-only / docs-only workflow for a future status marker for
the Step597 wrapper checks. This Makefile target design remains unchanged.

## Step599 Remote Run Status Reference

Step599 adds a public-safe status marker for the remote Release Quality run
after Step597 wrapper integration. This Makefile target design remains
unchanged.

## Step600 Final Safety Review Reference

Step600 adds
`docs/frozen_policy_generation_actual_controlled_artifact_body_generation_runtime_invocation_release_quality_chain_final_safety_review.md`
as a final-safety-review / docs-only review for the Step585-Step599
actual-controlled release-quality chain. This Makefile target design remains
unchanged, and Step600 does not change Makefile, wrapper, workflow, Python,
fixture JSON, runtime implementation, manifest writer integration, or file
writing.

## Step601 Planning Reference

Step601 adds
`docs/frozen_policy_generation_actual_controlled_post_final_safety_review_next_boundary_planning.md`
as a planning-only / docs-only next-boundary plan after Step600. This Makefile
target design remains unchanged.
