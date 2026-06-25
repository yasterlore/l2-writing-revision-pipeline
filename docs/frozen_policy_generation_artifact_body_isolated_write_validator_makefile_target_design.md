# Frozen Policy Generation Artifact Body Isolated Write Validator Makefile Target Design

## 1. Purpose

This document fixes the standalone Makefile target design for running the
isolated artifact body file-writing validator from a short, safe command.

This is a docs-only target design. It is not a Makefile target
implementation, not release-quality integration, not manifest writer work,
not artifact writer CLI integration, not metric computation, and not a
production-readiness claim.

## 2. Current State

- The target design assumes the Step370 isolated write validator module:
  `learner_state.frozen_policy_generation_artifact_body_isolated_write_validation`.
- The target design assumes the Step370 isolated write validator CLI:
  `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_isolated_write_validation`.
- The isolated write fixture root exists:
  `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_isolated_write_validation/`.
- The fixture root contains 22 cases and 110 JSON files.
- The expected root summary is count-only:
  - `total_cases=22`
  - `valid_cases=5`
  - `invalid_cases=17`
  - `pass_written_cases=3`
  - `pass_no_write_cases=1`
  - `usage_error_cases=14`
  - `fail_closed_cases=4`
  - `matched_cases=22`
  - `mismatched_cases=0`
  - `input_error_cases=0`
  - `residue_file_count=0`
- A standalone Makefile target for this validator does not exist yet.
- Release-quality integration for this validator does not exist yet.
- Manifest writer does not exist.
- Artifact writer CLI integration for file writing does not exist.
- Before implementing the target, local verification should confirm that the
  validator module and CLI are present in the active branch.

## 3. Proposed Target Name

Candidates:

- `check-learner-state-frozen-policy-generation-artifact-body-isolated-write-validation`
- `check-learner-state-frozen-policy-generation-artifact-body-isolated-write`
- `check-learner-state-artifact-body-isolated-write-validation`
- `check-artifact-body-isolated-write-validation`

Recommended:

`check-learner-state-frozen-policy-generation-artifact-body-isolated-write-validation`

Reasons:

- It matches the learner-state / frozen policy generation / artifact body
  namespace.
- It is distinct from the no-write fixture validator target and the
  single-path file-writing smoke target.
- It clearly names this as the multi-case isolated write validator.
- It remains understandable if added to release-quality later.

## 4. Proposed Command

The future target should run the validator CLI against the default isolated
write fixture root after the Step370 validator module is present:

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_isolated_write_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_artifact_body_isolated_write_validation`

The target should use the human summary by default, not `--json`.

## 5. Proposed Help Text

`check-learner-state-frozen-policy-generation-artifact-body-isolated-write-validation  Validate isolated artifact body file writing cases`

## 6. Expected Behavior

The future target should:

- exit 0 when all isolated write cases match expected outcomes
- emit `mode=isolated_write_validation`
- emit `total_cases=22`
- emit `valid_cases=5`
- emit `invalid_cases=17`
- emit `pass_written_cases=3`
- emit `pass_no_write_cases=1`
- emit `usage_error_cases=14`
- emit `fail_closed_cases=4`
- emit `matched_cases=22`
- emit `mismatched_cases=0`
- emit `input_error_cases=0`
- emit `residue_file_count=0`
- emit `body_payload_printed=false`
- emit `stdout_body_suppressed=true`
- emit `stderr_body_suppressed=true`
- emit `no_raw_rows=true`
- emit `no_logits_dump=true`
- emit `no_private_paths=true`
- emit `no_absolute_paths=true`
- emit `no_manifest_body=true`
- emit `no_generated_policy_body=true`
- emit `synthetic_only_checked=true`
- emit `no_oracle_checked=true`
- emit `path_policy_checked=true`
- emit `file_content_policy_checked=true`
- emit `cleanup_checked=true`
- emit `temp_root_isolated=true`
- emit `release_quality_ready=false`
- print no artifact body payload
- print no fixture JSON body
- print no written file content
- print no absolute temp path
- leave no artifact body generation residue after the target finishes

## 7. Output And Logging Safety

Allowed output:

- target label and help text
- command shape
- summary fields
- counts
- category names
- reason code names and counts
- safety flags
- safe case IDs if needed
- residue count

Forbidden output:

- written file content
- artifact body payload
- request body
- pointer body
- isolated write request body
- expected result body
- case metadata body
- generated policy body
- manifest body
- raw rows
- logits
- probabilities
- private paths
- absolute temp paths
- raw learner text
- raw logs

## 8. Relation To Existing Targets

The existing file-writing smoke target checks one happy-path write, parse,
safety scan, and cleanup path:

`check-learner-state-frozen-policy-generation-artifact-body-file-writing-smoke`

The existing no-write file-writing fixture validator checks static
file-output and path-policy metadata contracts without performing writes:

`check-learner-state-frozen-policy-generation-artifact-body-file-writing-fixtures`

The proposed isolated write validator target checks multiple actual CLI
write, no-write, usage-error, and fail-closed cases inside an isolated temp
root. It validates a different boundary and should not replace either
existing target.

## 9. Release-Quality Staging

Do not add this target to release-quality in the same step that implements
the standalone target.

Recommended staging:

- implement the standalone Makefile target
- run it locally and stabilize cleanup / no-residue behavior
- create a docs-only release-quality integration design
- integrate the wrapper in a separate step
- record a remote/manual status marker only after release-quality succeeds

Because this validator performs actual temporary writes, release-quality
integration should wait until the target output and cleanup behavior remain
stable.

## 10. Step370 Availability Note

This Makefile target should not be implemented until the isolated write
validator module is available in the active branch. If the module is absent,
the target would fail before validating fixture behavior.

The implementation step should first run the CLI help and root validation
commands, then add the Makefile target only if those commands succeed.

## 11. Step372 Availability Reconciliation Status

Step372 restores and confirms the isolated write validator module, CLI, and
unit tests in the active worktree:

`learner_state.frozen_policy_generation_artifact_body_isolated_write_validation`

The restored validator validates the 22-case / 110-JSON isolated write
fixture root with `matched_cases=22`, `mismatched_cases=0`,
`input_error_cases=0`, and `residue_file_count=0`. The CLI remains
summary-only and body-free. Step372 does not implement the Makefile target,
does not add release-quality integration, does not change workflow YAML, does
not change fixture JSON, does not write manifests, and does not connect the
artifact writer CLI.

## 12. Exit Code Strictness Note

The intended isolated write validator behavior is to match fail-closed cases
by category, status, and no-write behavior. Some fail-closed cases may
observe the artifact body generation CLI returning exit code `3` while the
historical fixture contract records expected exit code `1`.

The future Makefile target should document the current behavior and rely on
the validator result rather than reinterpreting case-level exit codes. Strict
exit-code normalization can be a separate future step if the contract is
tightened. This design does not change fixture JSON.

## 13. Future Tests And Checks For Implementation

The implementation step should verify:

- `make help` includes the new target
- the target exits 0
- output includes `total_cases=22`
- output includes `matched_cases=22`
- output includes `input_error_cases=0`
- output includes `residue_file_count=0`
- output includes `release_quality_ready=false`
- target output is body-free
- no absolute temp path is printed
- artifact body generation residue remains 0
- the existing file-writing smoke target still passes
- the existing no-write file-writing fixture target still passes
- `make check-release-quality` remains pass but does not include this target
  yet
- release-quality wrapper diff remains none
- workflow diff remains none

## 14. Docs Safety Policy

Documentation for this target must include only field names, target names,
command shapes, case IDs, counts, and safety policy.

It must not include fixture JSON examples, written file body examples,
artifact body payload examples, private path examples, raw logs, raw rows,
logits, raw learner text, real participant data, or performance metric
bodies.

## 15. Beginner-Friendly Explanation

A Makefile target is a short command name that runs a longer command in a
repeatable way.

The isolated write validator already has a CLI. A Makefile target would make
that CLI easy to run consistently without remembering the full module path
and fixture root.

The file-writing smoke target writes one safe case. The isolated validator
target runs many cases, including expected failures, and checks that unsafe
requests do not leave files behind.

The target should not enter release-quality immediately because it performs
temporary writes. The cleanup and no-residue behavior should first be stable
as a standalone command.

`residue_file_count=0` matters because it shows the validator cleaned up its
temporary outputs and did not leave generated artifact body files behind.

## 16. What This Does Not Do

- does not implement the Makefile target
- does not add release-quality integration
- does not change workflow YAML
- does not change Python code/tests
- does not change fixture JSON
- does not implement manifest writer
- does not connect artifact writer CLI
- does not use real data
- does not compute metrics
- does not prove production readiness

## 17. Next Recommended Steps

- Step373: implement the standalone Makefile target.
- Step374: design release-quality integration for the isolated write target.
- Step375: integrate the release-quality wrapper if the standalone target
  remains stable.
- Later: record a public-safe remote/manual status marker after release-quality
  succeeds.

## 18. Related Documents

- [Frozen policy generation artifact body isolated temp write validation design](frozen_policy_generation_artifact_body_isolated_temp_write_validation_design.md)
- [Frozen policy generation artifact body isolated temp write fixture contract design](frozen_policy_generation_artifact_body_isolated_temp_write_fixture_contract_design.md)
- [Frozen policy generation artifact body file writing smoke target design](frozen_policy_generation_artifact_body_file_writing_smoke_target_design.md)
- [Frozen policy generation artifact body file writing implementation final design](frozen_policy_generation_artifact_body_file_writing_implementation_final_design.md)
- [Frozen policy generation artifact body file writing design](frozen_policy_generation_artifact_body_file_writing_design.md)
- [Frozen policy generation artifact body isolated write validation fixtures](../tests/fixtures/learner_state_frozen_policy_generation_artifact_body_isolated_write_validation/README.md)
- [Learner-state frozen policy generation artifact body file writing fixture release-quality remote run status](status/learner_state_frozen_policy_generation_artifact_body_file_writing_fixture_release_quality_remote_run_status.md)
- [Public release checklist](public_release_checklist.md)
