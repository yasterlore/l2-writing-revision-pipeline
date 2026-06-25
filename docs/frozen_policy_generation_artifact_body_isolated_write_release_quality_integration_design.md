# Frozen Policy Generation Artifact Body Isolated Write Release-Quality Integration Design

## 1. Purpose

This document fixes the release-quality integration design for the isolated
artifact body file-writing validator target:

`check-learner-state-frozen-policy-generation-artifact-body-isolated-write-validation`

This is a docs-only integration design. It is not wrapper implementation, not
a workflow change, not manifest writer work, not artifact writer CLI
integration, not metric computation, not performance evaluation, and not a
production-readiness claim.

## 2. Current State

- The isolated write validator module exists:
  `learner_state.frozen_policy_generation_artifact_body_isolated_write_validation`.
- The isolated write validator CLI exists:
  `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_artifact_body_isolated_write_validation`.
- The isolated write fixture root exists:
  `tests/fixtures/learner_state_frozen_policy_generation_artifact_body_isolated_write_validation/`.
- The standalone Makefile target exists:
  `check-learner-state-frozen-policy-generation-artifact-body-isolated-write-validation`.
- The target validates 22 cases / 110 JSON files.
- The target performs isolated temp writes and cleanup.
- The target reports `residue_file_count=0`.
- The target is not in release-quality yet.
- Manifest writer does not exist.
- Artifact writer CLI integration for file writing does not exist.

Expected standalone target summary:

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
- `release_quality_ready=false`

## 3. Proposed Wrapper Insertion Point

Candidates:

- Candidate A: immediately after the artifact body file writing fixture
  validation target and before config/scoring smoke checks.
- Candidate B: immediately after the safe-metadata artifact body generation
  CLI smoke and before file writing fixture validation.
- Candidate C: after config/scoring smoke checks.

Recommended: Candidate A.

Proposed order:

- artifact writer fixture validation
- artifact writer runtime smoke
- artifact body fixture validation
- artifact body generation CLI smoke
- artifact body generation safe-metadata CLI smoke
- artifact body file writing fixture validation
- artifact body isolated write validation
- config and scoring smoke checks

Reasons:

- The no-write file writing fixture validation checks the static contract.
  The isolated write target then checks actual temp-root write/no-write
  behavior.
- The artifact body sequence reads as generation smoke, safe-metadata smoke,
  no-write file writing contract validation, then isolated write validation.
- Config/scoring smoke checks are a separate subsystem and should remain after
  the artifact body file-writing boundary.
- The isolated write target reports cleanup and `residue_file_count=0`, so it
  should finish before config/scoring checks create their own temp outputs.
- The one-path file-writing smoke target can remain standalone; the isolated
  write validator gives broader multi-case coverage for release-quality.

## 4. Proposed Wrapper Command

`make check-learner-state-frozen-policy-generation-artifact-body-isolated-write-validation`

## 5. Proposed Wrapper Label

`release_quality_check: learner-state frozen policy generation artifact body isolated write validation`

## 6. Expected Wrapper Behavior

- target pass -> release-quality continues
- target fail -> release-quality fails
- output remains summary-only and body-free
- no written file content is printed
- no fixture JSON body is printed
- no artifact body payload is printed
- no absolute temp path is printed
- no private path is printed
- no residue remains after the target
- no manifest writer evidence is created
- no artifact writer CLI integration evidence is created
- no performance evidence is created

Expected output fields:

- `mode=isolated_write_validation`
- `validation_schema_version=learner_state_frozen_policy_generation_artifact_body_isolated_write_validation_v0.1`
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
- `body_payload_printed=false`
- `stdout_body_suppressed=true`
- `stderr_body_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_absolute_paths=true`
- `no_manifest_body=true`
- `no_generated_policy_body=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `path_policy_checked=true`
- `file_content_policy_checked=true`
- `cleanup_checked=true`
- `temp_root_isolated=true`
- `release_quality_ready=false`

## 7. Failure Interpretation

Treat the following as release-quality failures:

- required fixture file missing
- malformed JSON
- schema version mismatch
- case ID mismatch
- expected category mismatch
- expected status mismatch
- write expected but file missing
- no-write expected but file written
- written file JSON parse failure
- written file forbidden key or forbidden marker detected
- stdout body payload detected
- stderr body payload detected
- absolute temp path leaked in summary
- private path leaked in summary
- cleanup failure
- `residue_file_count > 0`
- `mismatched_cases > 0`
- `input_error_cases > 0`
- validator internal error

These failures indicate isolated write validator or fixture-contract problems.
They are not manifest writer failures, not artifact writer CLI integration
failures, and not model performance failures.

## 8. Log Safety Review

Allowed output:

- release-quality label
- command
- mode
- validation schema version
- counts
- category names
- reason code names and counts
- safety flags
- residue count
- safe summary fields

Forbidden output:

- written file content
- artifact body payload
- artifact body request body
- artifact writer result pointer body
- isolated write request body
- expected isolated write result body
- case metadata body
- generated policy body
- manifest body
- raw rows
- logits
- probabilities
- private paths
- absolute temp paths
- raw learner text
- final text
- observed-after text
- gold label
- expected action payload
- scoring feedback payload
- performance metric body
- GitHub raw logs
- full job output copied into docs

## 9. Relation To Existing Release-Quality Checks

- Artifact body fixture validation checks artifact body contract fixtures.
- Artifact body generation suppressed smoke checks the body-free suppressed
  path.
- Artifact body generation safe-metadata smoke checks the safe-metadata
  generation path.
- File writing fixture validation checks no-write static file-writing and
  path-policy contracts.
- Isolated write validation checks actual multi-case write/no-write behavior
  in isolated temp roots.
- The file-writing smoke target remains standalone initially and does not need
  release-quality inclusion while the isolated validator provides multi-case
  coverage.
- Artifact writer runtime remains separate.
- Manifest writer remains separate.
- Config/scoring smoke checks remain separate.

## 10. Cleanup And No-Residue Release-Quality Condition

- `residue_file_count` must be `0`.
- The target must not leave files in `tmp/artifact_body_generation`.
- The target must not remove unrelated files.
- The target must not expose absolute temp paths.
- Cleanup failure should fail release-quality.
- Release-quality should not continue if residue remains.

## 11. Exit Code Strictness Note

The current validator matches fail-closed cases by category, status, and
no-write behavior. Some historical expected exit codes may differ from the
actual artifact body generation CLI exit code for fail-closed cases.

Release-quality integration should initially use the current validator
behavior. Strict exit-code normalization can be a separate future contract
cleanup step. This design does not change fixture JSON.

## 12. Makefile And Workflow Status

- Makefile target exists.
- Release-quality wrapper is not yet changed.
- Workflow YAML should not need a change if it already invokes the wrapper.
- Future implementation should modify only the wrapper if possible.
- Workflow YAML diff should remain none unless a concrete blocker appears.

## 13. Testing Plan For Future Wrapper Implementation

Future wrapper implementation should verify:

- standalone isolated write target passes
- `make check-release-quality` includes the new label
- `make check-release-quality` passes
- target output includes `total_cases=22`
- target output includes `matched_cases=22`
- target output includes `residue_file_count=0`
- target output includes `release_quality_ready=false`
- target output remains body-free
- no absolute temp path is printed
- no written file content is printed
- `tmp/artifact_body_generation` residue remains `0`
- wrapper diff is limited
- workflow diff remains none
- all existing checks pass

## 14. Release-Quality Status Marker Future

After wrapper integration and a successful remote/manual Release Quality run,
a future status marker may be added.

The marker should record only pass-only and count-only metadata. Raw logs must
not be copied.

Allowed marker fields include:

- target included: yes
- label
- command
- `total_cases=22`
- `matched_cases=22`
- `residue_file_count=0`
- safety flags
- no written file content copied
- no artifact body payload copied
- no manifest body copied
- no absolute temp path copied
- no private path copied

## 15. No-Oracle And Synthetic-Only Boundary

- target uses synthetic-only isolated write fixtures
- no real data
- no participant data
- no raw learner text
- no final, gold, or observed-after text
- no expected action payload
- no scoring feedback payload
- no artifact body payload in logs
- no generated policy body
- no manifest body
- no logits
- no raw rows
- no private paths

## 16. What This Does Not Do

- does not integrate the wrapper
- does not change workflow YAML
- does not change Makefile
- does not change Python code/tests
- does not change fixture JSON
- does not implement manifest writer
- does not connect artifact writer CLI
- does not compute metrics
- does not evaluate performance
- does not use real data
- does not prove production readiness

## 17. Beginner-Friendly Explanation

Release-quality is the project’s broad local check bundle. It runs a curated
set of safety, fixture, CLI, Python, Rust, and frontend checks before a change
is considered ready for release-quality review.

The isolated write validator should be designed before wrapper integration
because it performs temporary writes. The wrapper placement must preserve
cleanup, no-residue behavior, and body-free logs.

The file-writing smoke target checks one happy path. The isolated validator
checks many valid and expected-failure paths, including safe refusal cases.

`residue_file_count=0` matters because release-quality should not leave
generated artifact body files behind.

A successful isolated write target does not prove manifest writer behavior or
artifact writer CLI integration. Those systems are intentionally separate and
remain future work.

## 18. Next Recommended Steps

- Step375: integrate the release-quality wrapper.
- Step376: design the remote/manual run record workflow.
- Step377: add a public-safe remote/manual status marker after a successful
  Release Quality run.
