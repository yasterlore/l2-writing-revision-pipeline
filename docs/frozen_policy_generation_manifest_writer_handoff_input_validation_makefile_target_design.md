# Manifest Writer Handoff Input Validation Makefile Target Design

## 1. Title

Manifest Writer Handoff Input Validation Makefile Target Design

## 2. Scope

This document is design-only / docs-only. It defines the future standalone Makefile target for the Step662 direct CLI runner.

This step is Makefile target design only. It does not change Makefile, release-quality wrapper, workflows, Python code/tests, fixture JSON, runtime implementation, or validator implementation.

This step does not invoke manifest writer, generate manifest body, write manifest files, write artifact files, emit payload body, output artifact body payload, or output generated policy body.

This step does not prove production readiness, real-data readiness, or model performance.

## 3. Prior Implementation Dependency

Step659 defined the manifest writer handoff input contract.

Step660 fixed the 23-case fixture / matrix contract.

Step661 designed the future runner behavior.

Step662 implemented the direct CLI runner, focused tests, and synthetic body-free fixture root:

- `python/learner_state/frozen_policy_generation_manifest_writer_handoff_input_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_manifest_writer_handoff_input_validation.py`
- `tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_handoff_input/`

The Step662 runner is direct CLI-only. It is not Makefile-targeted yet and is not release-quality integrated yet.

Step663 designs the future standalone Makefile target. Step663 does not implement the target.

## 4. Target Runtime CLI

Runtime module:

```text
python/learner_state/frozen_policy_generation_manifest_writer_handoff_input_validation.py
```

Direct CLI:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer_handoff_input_validation \
  --fixture-root tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_handoff_input \
  --case-selection manifest-writer-handoff-input-contract \
  --summary-only \
  --no-manifest-writer \
  --no-file-writing \
  --fail-closed-on-forbidden-body
```

Required flags:

- `--summary-only`
- `--no-manifest-writer`
- `--no-file-writing`
- `--fail-closed-on-forbidden-body`

There is no flag that enables manifest writer invocation. There is no flag that enables file writing. The CLI remains metadata-only / body-free.

## 5. Proposed Makefile Target

Recommended target name:

```text
check-learner-state-frozen-policy-generation-manifest-writer-handoff-input-validation
```

Recommended help text:

```text
Run manifest writer handoff input metadata-only validation
```

Recommended command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer_handoff_input_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_handoff_input --case-selection manifest-writer-handoff-input-contract --summary-only --no-manifest-writer --no-file-writing --fail-closed-on-forbidden-body
```

Do not add the target in Step663. Step664 should implement it.

## 6. Expected Target Output

The future Makefile target should produce the same public-safe summary as the Step662 direct CLI.

Expected fields include:

- `mode=manifest_writer_handoff_input_validation`
- `schema_version=learner_state_frozen_policy_generation_manifest_writer_handoff_input_v0.1`
- `contract_name=manifest_writer_handoff_input_contract`
- `matrix_name=manifest_writer_handoff_input_contract_matrix`
- `case_selection=manifest-writer-handoff-input-contract`
- `status=pass`
- `reason_code=none`
- `selected_case_count=23`
- `selected_valid_case_count=3`
- `selected_invalid_case_count=20`
- `selected_fail_closed_case_count=11`
- `selected_usage_error_case_count=5`
- `selected_mismatch_case_count=4`
- `expected_pass_case_count=3`
- `observed_pass_case_count=3`
- `expected_fail_closed_case_count=11`
- `observed_fail_closed_case_count=11`
- `expected_usage_error_case_count=5`
- `observed_usage_error_case_count=5`
- `expected_mismatch_case_count=4`
- `observed_mismatch_case_count=4`
- `processed_case_count=23`
- `input_error_case_count=0`
- `manifest_writer_invocation_requested_count=0`
- `manifest_writer_invoked_count=0`
- `manifest_body_generation_requested_count=0`
- `manifest_body_generated_count=0`
- `manifest_body_output_count=0`
- `manifest_file_writing_requested_count=0`
- `manifest_file_written_count=0`
- `artifact_file_writing_requested_count=0`
- `artifact_file_written_count=0`
- `file_writing_enabled_count=0`
- `payload_body_emission_requested_count=0`
- `payload_body_emitted_count=0`
- `artifact_body_payload_output_count=0`
- `generated_policy_body_emitted_count=0`
- `request_body_output_count=0`
- `pointer_body_output_count=0`
- `expected_body_output_count=0`
- `forbidden_body_detected_count=0`
- `private_path_detected_count=0`
- `absolute_path_detected_count=0`
- `raw_learner_text_detected_count=0`
- `real_data_marker_detected_count=0`
- `no_oracle_forbidden_field_detected_count=0`
- `raw_log_or_full_job_output_detected_count=0`
- `residue_file_count=0`
- `raw_stdout_body_suppressed_count=23`
- `raw_stderr_body_suppressed_count=23`
- `content_suppressed=True`
- `body_suppressed=True`
- `metadata_only_checked=True`
- `synthetic_only_checked=True`
- `no_oracle_checked=True`
- `production_readiness_claimed=False`
- `real_data_readiness_claimed=False`
- `performance_claims_present=False`

`status=pass` means the Step660 fixture / matrix contract matched. It does not mean manifest writer correctness, file-writing readiness, manifest body correctness, or payload correctness. It does not authorize manifest writer invocation. It does not remove the Step645 payload audit limitation.

## 7. Makefile Placement

Recommended placement:

- near manifest writer / handoff / artifact body to manifest related checks.
- after existing artifact body to manifest handoff metadata-only no-writer-invocation target.
- before manifest writer invocation / manifest writer runtime checks if grouped nearby.
- before manifest writer file-writing checks if grouped nearby.
- before release-quality integration.

Recommended conceptual order:

1. artifact body generation safe-metadata checks
2. artifact body to manifest handoff metadata-only no-writer-invocation
3. manifest writer handoff input validation
4. manifest writer checks
5. file-writing checks

Step664 adds standalone Makefile target only. Release-quality wrapper integration should be deferred to a later design step after standalone target passes. The target should be added to `.PHONY` and included in `make help`.

## 8. Relationship to Existing Targets

Existing targets that must remain unchanged:

- `check-learner-state-frozen-policy-generation-artifact-body-to-manifest-handoff-metadata-only-no-writer-invocation`
- `check-learner-state-frozen-policy-generation-artifact-body-generation-safe-metadata`
- `check-learner-state-frozen-policy-generation-manifest-writer-fixtures`
- `check-learner-state-frozen-policy-generation-manifest-writer-runtime`
- `check-learner-state-frozen-policy-generation-manifest-writer-file-writing-fixtures`
- `check-learner-state-frozen-policy-generation-manifest-writer-isolated-write-validation`
- `check-learner-state-frozen-policy-generation-manifest-writer-runtime-file-writing`
- `check-learner-state-frozen-policy-generation-actual-controlled-v0-4-artifact-body-payload-audit-without-payload-emission`

The new future target:

- runs the manifest writer handoff input validation runner.
- uses the Step662 synthetic fixture root.
- checks the 23-case metadata-only handoff input contract.
- does not replace artifact body to manifest handoff no-writer-invocation.
- does not replace existing manifest writer checks.
- does not replace file-writing checks.
- does not replace payload audit without payload emission.
- does not invoke manifest writer.
- does not generate manifest body.
- does not write files.
- does not prove manifest writer correctness.
- does not prove file-writing readiness.
- is not release-quality integrated yet.

## 9. Step664 Implementation Plan

Step664 should:

- update `Makefile`
- add `.PHONY` entry
- add `make help` entry
- add the target command
- not modify Python code/tests
- not modify fixture JSON
- not modify release-quality wrapper
- not modify workflows
- not modify runtime implementation
- not invoke manifest writer
- not generate manifest body
- not write files
- run `make help`
- run the new Makefile target
- run the direct manifest writer handoff input validation CLI
- run focused manifest writer handoff input validation tests
- run existing artifact body to manifest handoff no-writer-invocation tests
- run existing artifact body to manifest handoff no-writer-invocation Makefile target
- run existing manifest writer fixture validation
- run existing manifest writer runtime smoke
- run existing manifest writer file-writing fixture validation
- run existing manifest writer isolated write validation
- run existing manifest writer runtime file-writing smoke
- run existing payload audit tests
- run existing payload audit Makefile target
- run `make check-python`
- run compileall
- confirm existing fixture JSON diff unchanged
- update root README and full technical specification related docs because Step664 is implementation

Step662 reported focused runner and core regression checks, but did not explicitly list every existing manifest writer Makefile check. Step664 should include the existing manifest writer fixture validation, runtime smoke, file-writing fixture validation, isolated write validation, and runtime file-writing smoke before accepting the target implementation.

## 10. Safety Boundary

The target must:

- run only the metadata-only manifest writer handoff input validation runner.
- use synthetic body-free fixtures.
- output only aggregate public-safe metadata.
- not print fixture JSON body.
- not print request body.
- not print pointer body.
- not print expected body.
- not print artifact body payload.
- not print generated policy body.
- not print manifest body.
- not print raw stdout/stderr body.
- not print raw rows.
- not print logits/probabilities.
- not print private/absolute path values.
- not print raw learner text.
- not use real participant data.
- not invoke manifest writer.
- not generate manifest body.
- not enable file writing.
- not write artifact files.
- not write manifest files.
- not produce residue.

## 11. Failure Interpretation

Target failure may indicate selected-count mismatch, valid/fail_closed/usage_error/mismatch count mismatch, missing flags, forbidden body emission, runner-level usage_error, runner-level mismatch, fail_closed, manifest writer invocation, manifest body generation, file writing, or residue.

Target pass means the 23-case metadata-only handoff input contract matched with body-free output and no residue.

Target pass does not prove manifest writer correctness, file-writing readiness, manifest body correctness, or payload correctness. It does not imply release-quality integration, production readiness, or real-data readiness.

## 12. Non-Equivalence Cautions

- Makefile target design is not Makefile implementation.
- future target pass will not prove manifest writer correctness.
- future target pass will not prove file-writing readiness.
- future target pass will not prove manifest body correctness.
- future target pass will not prove payload correctness.
- handoff input validation target is not manifest writer integration.
- no-writer-invocation target is not manifest writer correctness.
- no-file-writing target is not file-writing readiness.
- metadata-only handoff input validation is not manifest body correctness.
- payload audit pass is not payload correctness.
- Step645 payload audit limitation remains separate.
- release-quality success is not production readiness.
- synthetic-only pass is not real-data readiness.

## 13. Non-Claims

- Does not claim production readiness.
- Does not claim real-data readiness.
- Does not claim model performance.
- Does not claim F1 / accuracy / ECE / AURCC achievement.
- Does not claim runtime correctness generally.
- Does not claim all invalid-case runtime behavior.
- Does not claim payload correctness.
- Does not claim artifact body payload quality.
- Does not claim manifest writer correctness.
- Does not claim file-writing readiness.
- Does not claim manifest body correctness.
- Does not claim generated policy quality.
- Does not claim learner-state estimator correctness.
- Does not claim educational validity.

## 14. Public-Safe Checklist

- no raw logs
- no full job output
- no copied GitHub log blocks
- no screenshots containing raw logs
- no fixture JSON body
- no request body
- no pointer body
- no expected body
- no written file JSON body
- no artifact body payload
- no generated policy body
- no manifest body
- no raw stdout/stderr body
- no raw rows
- no logits/probabilities
- no private paths
- no absolute paths
- no raw learner text
- no real participant data
- no performance claims
- no production readiness claims
- no real-data readiness claims

## 15. Recommended Next Step

Recommended:

`Step664: manifest writer handoff input validation Makefile target implementation`

Step664 should update Makefile and necessary README/docs only. Step664 should not change Python code/tests, fixture JSON, release-quality wrapper, workflows, invoke manifest writer, generate manifest body, enable file writing, or emit payload bodies.

## 16. Step664 Makefile Target Implementation

Step664 implements the standalone Makefile target:

```text
check-learner-state-frozen-policy-generation-manifest-writer-handoff-input-validation
```

Help text:

```text
Run manifest writer handoff input metadata-only validation
```

Command:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer_handoff_input_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_handoff_input --case-selection manifest-writer-handoff-input-contract --summary-only --no-manifest-writer --no-file-writing --fail-closed-on-forbidden-body
```

The target is standalone only and is not release-quality integrated in Step664. Step664 does not change Python code/tests, fixture JSON, workflows, release-quality wrapper, invoke manifest writer, generate manifest body, enable file writing, or emit payload bodies. The next recommended step is Step665 release-quality integration design.

## 17. Step665 Release-Quality Integration Design

Step665 creates `docs/frozen_policy_generation_manifest_writer_handoff_input_validation_release_quality_integration_design.md` as design-only / docs-only release-quality wrapper integration planning for the Step664 standalone target.

The design proposes the future release-quality label, command, insertion after the artifact body to manifest handoff no-writer-invocation check and before manifest writer / file-writing checks, expected public-safe output, Step666 validation plan, safety boundary, non-equivalence cautions, and non-claims. Step665 does not change wrapper, Makefile, workflow, Python code/tests, fixture JSON, manifest writer invocation, manifest body generation, file writing, or payload body emission.

## 18. Step666 Release-Quality Wrapper Integration

Step666 adds the Step664 standalone target to `scripts/check_release_quality.sh` with label `release_quality_check: learner-state frozen policy generation manifest writer handoff input validation`.

The wrapper check runs `make check-learner-state-frozen-policy-generation-manifest-writer-handoff-input-validation` after the artifact body to manifest handoff no-writer-invocation check and before artifact / manifest file-writing and manifest writer checks. Step666 does not change Makefile, workflow, Python code/tests, fixture JSON, manifest writer invocation, manifest body generation, file writing, or payload body emission.

## 19. Step667 Remote/Manual Run Record Workflow Design

Step667 creates `docs/frozen_policy_generation_manifest_writer_handoff_input_validation_release_quality_remote_run_record_workflow.md` as design-only / docs-only planning for a future status marker. It records allowed public-safe metadata, forbidden raw log / body sources, target summary fields, missing metadata handling, and future Step668 staging without changing wrapper, Makefile, workflow, Python code/tests, fixture JSON, manifest writer invocation, manifest body generation, file writing, or payload body emission.
