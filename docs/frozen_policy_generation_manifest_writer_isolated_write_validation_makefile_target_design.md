# Frozen Policy Generation Manifest Writer Metadata-Only Isolated Write Validation Makefile Target Design

## 1. Purpose

This document designs a future standalone Makefile target for the manifest
writer metadata-only isolated write validation CLI.

It is a docs-only Makefile target design. It is not Makefile implementation,
not release-quality integration, not production-facing runtime file writing,
not public `--manifest-out`, not artifact writer CLI integration, and not a
production readiness claim.

The target boundary remains synthetic-only, metadata-only, no-oracle,
body-free, path-safe, and count-only.

## 2. Current State

- The isolated write validation module exists.
- The isolated write validation CLI exists.
- Focused isolated write validation tests exist.
- The isolated write validation fixture root exists.
- The Makefile target does not exist.
- Release-quality integration does not exist.
- Production-facing runtime file writing does not exist.
- Public `--manifest-out` is not implemented.
- Artifact writer CLI integration does not exist.

## 3. Target Name

Proposed target:

`check-learner-state-frozen-policy-generation-manifest-writer-isolated-write-validation`

## 4. Target Command

Proposed command:

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer_isolated_write_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_isolated_write_validation`

The command runs root validation through the existing isolated write
validation CLI.

## 5. Help Text

Proposed help text:

`check-learner-state-frozen-policy-generation-manifest-writer-isolated-write-validation  Validate manifest writer metadata-only isolated write behavior`

## 6. Expected Target Output

The default output should remain body-free and count-only. Expected summary
fields:

- mode=manifest_writer_isolated_write_validation
- validation_schema_version=learner_state_frozen_policy_generation_manifest_writer_isolated_write_validation_v0.1
- total_cases=25
- valid_cases=6
- invalid_cases=19
- total_json_files=150
- json_files_per_case=6
- pass_written_cases=5
- pass_no_write_cases=1
- usage_error_cases=14
- fail_closed_cases=5
- matched_cases=25
- mismatched_cases=0
- input_error_cases=0
- residue_file_count=0
- stdout_body_suppressed=true
- stderr_body_suppressed=true
- no_manifest_body=true
- no_generated_policy_body=true
- no_artifact_body_payload=true
- no_request_body=true
- no_pointer_body=true
- no_expected_body=true
- no_raw_rows=true
- no_logits_dump=true
- no_private_paths=true
- no_absolute_paths=true
- synthetic_only_checked=true
- no_oracle_checked=true
- path_policy_checked=true
- file_content_policy_checked=true
- cleanup_checked=true
- temp_root_isolated=true
- release_quality_ready=false

The output must not print fixture JSON bodies, written file bodies, manifest
bodies, request bodies, pointer bodies, expected-result bodies, artifact body
payloads, generated policy bodies, raw rows, logits, private paths, absolute
local paths, absolute temp paths, raw learner text, or performance evidence.

## 7. Expected Failure Behavior

The future target should fail when the underlying validator fails or detects a
contract violation, including:

- validator exits nonzero
- any case mismatches
- required file missing
- malformed JSON
- schema mismatch
- case_id mismatch
- category mismatch
- reason code mismatch
- unsafe selector or unsafe isolated path policy issue
- content policy issue
- stdout/stderr body suppression fails
- cleanup fails
- residue_file_count > 0
- body, payload, raw, logit, private-path, or absolute-path marker appears in
  public output
- temp_root_isolated=false
- normal manifest output residue is created under `tmp/frozen_policy_generation_manifest`

This failure interpretation is isolated validation harness failure only. It is
not production-facing runtime file writing evidence, public `--manifest-out`
evidence, artifact writer CLI integration evidence, model-performance
evidence, real-data readiness, or production readiness.

## 8. Relation To Current Isolated Write CLI

The Makefile target should be a thin wrapper around the CLI root validation.
It should not add new behavior and should not pass `--json` by default.

For `pass_written` cases, the validator writes only inside validator-owned
isolated temporary roots, parses and scans the metadata-only file, cleans up,
and reports residue count 0. The target must not write to normal project
output directories and must not print absolute temp paths.

## 9. Relation To Static File Writing Fixture Validator

The existing target:

`check-learner-state-frozen-policy-generation-manifest-writer-file-writing-fixtures`

performs static, non-write contract validation for manifest writer file
writing fixtures.

The proposed isolated write validation target exercises the isolated write
harness and writes metadata-only JSON only inside a validator-owned temporary
root for `pass_written` cases.

Both targets are separate. Neither target proves production readiness,
production file output correctness, artifact writer CLI integration, or
real-data readiness.

## 10. Relation To Existing Runtime Targets

Existing runtime-related targets stay distinct:

- `check-learner-state-frozen-policy-generation-manifest-writer-runtime`
  executes the existing metadata-only no-file runtime smoke.
- `check-learner-state-frozen-policy-generation-manifest-writer-runtime-fixtures`
  validates runtime fixture contracts statically.
- The proposed isolated write validation target validates isolated write
  harness behavior.

None of these targets proves production-facing `--manifest-out`.

## 11. Relation To Release-Quality

The target should be added as a standalone Makefile target first.
Release-quality integration should remain a later step.

The likely future wrapper insertion point is after manifest writer file
writing fixture validation and before config/scoring smoke checks, so the
manifest writer chain stays grouped while the isolated write boundary remains
explicit.

This Step423 design does not modify the wrapper.

## 12. Relation To Production-Facing Runtime File Writing

Public `--manifest-out` remains unimplemented. Production-facing runtime file
writing remains unimplemented.

Future target success would mean only that the isolated validation harness can
write and clean up metadata-only JSON inside its own temporary root. It would
not mean production file output readiness or normal output path readiness.

## 13. Docs Safety

Docs may list:

- target name
- command
- help text
- expected counts
- summary flags
- policy names
- reason-code categories

Docs must not include:

- fixture JSON bodies
- written file JSON body
- case metadata body
- isolated write request body
- manifest writer request body
- pointer body
- expected result body
- manifest body
- artifact body payload
- generated policy body
- raw logs
- full job output
- private path examples
- absolute local path examples
- absolute temp path examples
- raw learner text
- real participant data
- performance metric body

## 14. Future Implementation Tests

Future Step424 should verify:

- `make help` shows the target and help text
- target exits 0
- expected counts 25 / 150 and 5 / 1 / 14 / 5 are present
- residue_file_count=0
- stdout_body_suppressed=true
- stderr_body_suppressed=true
- temp_root_isolated=true
- no normal manifest output residue is created
- focused isolated write validation tests still pass
- full Python unittest discovery still passes
- Makefile diff is limited to target and help text
- release-quality wrapper diff remains none
- workflow YAML diff remains none

## 15. What This Does NOT Do

- does not implement the Makefile target
- does not integrate release-quality
- does not modify workflow YAML
- does not modify Python code/tests
- does not modify fixture JSON
- does not implement production-facing runtime file writing
- does not implement public `--manifest-out`
- does not connect artifact writer CLI
- does not use real data
- does not compute metrics
- does not prove production readiness

## 16. Next Recommended Steps

- Step424: Makefile target implementation
- Step425: release-quality integration design
- Step426: wrapper integration
- Step427: remote marker
- later production-facing runtime file writing design / implementation
- later artifact writer CLI integration

## 17. Related Documents

- [Frozen policy generation manifest writer metadata-only isolated write validation design](frozen_policy_generation_manifest_writer_isolated_write_validation_design.md)
- [Frozen policy generation manifest writer metadata-only isolated write validation release-quality integration design](frozen_policy_generation_manifest_writer_isolated_write_validation_release_quality_integration_design.md)
- [Frozen policy generation manifest writer metadata-only isolated write fixture contract design](frozen_policy_generation_manifest_writer_isolated_write_fixture_contract_design.md)
- [Frozen policy generation manifest writer metadata-only isolated write validation fixtures](../tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_isolated_write_validation/README.md)
- [Frozen policy generation manifest writer metadata-only file writing fixture validator Makefile target design](frozen_policy_generation_manifest_writer_file_writing_fixture_validator_makefile_target_design.md)
- [Frozen policy generation manifest writer metadata-only file writing boundary design](frozen_policy_generation_manifest_writer_file_writing_boundary_design.md)
- [Learner-state frozen policy generation manifest writer file writing fixture release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_file_writing_fixture_release_quality_remote_run_status.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)

## 18. Step424 Makefile Target Implementation Status

Step424 implements the standalone Makefile target:

`check-learner-state-frozen-policy-generation-manifest-writer-isolated-write-validation`

The target runs the isolated write validation CLI against:

`tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_isolated_write_validation`

The implementation is intentionally limited to Makefile target/help text
wiring. It does not add release-quality wrapper integration, change workflow
YAML, change Python code/tests, change fixture JSON, implement
production-facing runtime file writing, expose public `--manifest-out`,
connect artifact writer CLI, use real data, compute metrics, or claim
production readiness.

## 19. Step425 Release-Quality Integration Design Status

Step425 adds the docs-only release-quality integration design:

[Frozen policy generation manifest writer metadata-only isolated write validation release-quality integration design](frozen_policy_generation_manifest_writer_isolated_write_validation_release_quality_integration_design.md).

The design recommends adding the standalone target after manifest writer file
writing fixture validation and before config/scoring smoke checks in a future
wrapper step. It does not modify the release-quality wrapper, workflow YAML,
Makefile, Python code/tests, fixture JSON, production-facing runtime file
writing, public `--manifest-out`, artifact writer CLI integration, metrics,
real-data use, or production readiness.

## 20. Step426 Wrapper Integration Status

Step426 adds the standalone target to the release-quality wrapper with the
label:

`release_quality_check: learner-state frozen policy generation manifest writer isolated write validation`

The wrapper placement follows the Step425 design: after manifest writer file
writing fixture validation and before config/scoring smoke checks. This does
not change Makefile, workflow YAML, Python code/tests, fixture JSON,
production-facing runtime file writing, public `--manifest-out`, artifact
writer CLI integration, metrics, real-data use, or production readiness.

## 21. Step427 Remote Run Record Workflow Design Status

Step427 adds the docs-only remote/manual run record workflow design:

[Frozen policy generation manifest writer metadata-only isolated write validation release-quality remote run record workflow](frozen_policy_generation_manifest_writer_isolated_write_validation_release_quality_remote_run_record_workflow.md).

The target design remains unchanged. Step427 does not create a status marker,
run a workflow, change workflow YAML, change the release-quality wrapper,
change Makefile, change Python code/tests, change fixture JSON, implement
production-facing runtime file writing, expose public `--manifest-out`,
connect artifact writer CLI, use real data, compute metrics, or claim
production readiness.
