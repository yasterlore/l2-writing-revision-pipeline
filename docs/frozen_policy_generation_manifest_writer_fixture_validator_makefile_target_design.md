# Frozen Policy Generation Manifest Writer Fixture Validator Makefile Target Design

## 1. Purpose

This document fixes the docs-only design for a future standalone Makefile
target that runs the static manifest writer fixture validator.

This is not a Makefile target implementation, not release-quality integration,
not manifest writer implementation, not manifest file writing, and not a
production readiness claim.

## 2. Current State

- the manifest writer fixture validator module exists
- the manifest writer fixture validator CLI exists
- the manifest writer fixtures exist
- the CLI validates 30 cases and 150 JSON files
- the standalone Makefile target does not exist
- release-quality integration does not exist
- the manifest writer does not exist
- manifest file writing does not exist
- artifact writer CLI integration does not exist

The current validator is static fixture validation only. It checks synthetic
metadata-only fixture contracts and does not execute a manifest writer.

## 3. Proposed Target Name

Candidate target names:

- `check-learner-state-frozen-policy-generation-manifest-writer-fixtures`
- `check-learner-state-frozen-policy-generation-manifest-writer-fixture-validation`
- `check-learner-state-manifest-writer-fixtures`
- `check-manifest-writer-fixtures`

Recommended target:

`check-learner-state-frozen-policy-generation-manifest-writer-fixtures`

Reasons:

- it matches the existing artifact writer and artifact body fixture target
  naming style
- it makes fixture root validation easy to recognize
- it stays inside the learner-state / frozen policy generation namespace
- it remains clear when it is later added to release-quality

## 4. Proposed Command

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_manifest_writer`

The default target should use the human summary output, not `--json`.

## 5. Proposed Help Text

`check-learner-state-frozen-policy-generation-manifest-writer-fixtures  Validate manifest writer fixture contracts`

## 6. Expected Behavior

The future target should exit 0 when the current fixture root matches the
static validator contract.

Expected summary fields and values:

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

The target should not write manifest files, print manifest bodies, print
fixture JSON bodies, print request/pointer/expected bodies, print absolute
temp paths, or leave residue under `tmp/frozen_policy_generation_manifest/`.

## 7. Output and Logging Safety

Allowed output:

- target label and help text
- command shape
- summary fields
- counts
- category names
- reason code names and counts
- safety flags
- safe case IDs when needed

Forbidden output:

- manifest body
- manifest JSON body
- `manifest_writer_request` body
- `artifact_writer_result_pointer` body
- `artifact_body_generation_result_pointer` body
- `expected_manifest_writer_result` body
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

## 8. Relation to Existing Targets

The artifact writer fixture target checks artifact writer metadata-only
contracts. The artifact body fixture target checks artifact body body-safety
contracts. The artifact body file-writing fixture target checks artifact body
path and content policy contracts. The isolated write target checks artifact
body actual temp write behavior.

The proposed manifest writer fixture target checks manifest writer metadata
index fixture contracts. It does not replace existing targets and does not
prove manifest writer runtime behavior.

## 9. Release-Quality Staging

Do not add this target to release-quality in the same step as target
implementation.

Recommended staging:

- implement the standalone Makefile target
- run it locally and stabilize the output
- create a docs-only release-quality integration design
- add the wrapper integration in a separate step
- record a remote/manual status marker after release-quality succeeds

Runtime manifest writer smoke coverage should remain separate and later,
because the static fixture validator does not write manifest files.

## 10. Future Implementation Checks

The Makefile implementation step should verify:

- `make help` includes the target
- the target exits 0
- target output includes `total_cases=30`
- target output includes `matched_cases=30`
- target output includes `input_error_cases=0`
- target output includes `release_quality_ready=false`
- output remains body-free
- no absolute path is printed
- no manifest files are written
- `tmp/frozen_policy_generation_manifest/` residue remains 0
- existing release-quality still passes before wrapper integration
- wrapper diff remains none
- workflow diff remains none

## 11. Docs Safety Policy

Docs may include field names, target names, command shape, summary fields,
counts, category names, reason-code names, and policy.

Docs must not include fixture JSON examples, manifest body examples,
request/pointer/expected body examples, artifact body payload examples,
private path examples, raw logs, raw learner text, raw rows, logits, real
participant data, or performance metric bodies.

## 12. Beginner-Friendly Explanation

A Makefile target is a short command name that runs a longer command in a
repeatable way.

The CLI already knows how to validate the manifest writer fixture root. A
Makefile target gives developers a short, memorable command for the same
check.

The target should not enter release-quality immediately. First it should run
standalone, remain body-free, and show stable counts. Then release-quality can
include it in a separate wrapper step.

Static fixture validation is different from future runtime writer validation.
Static validation checks whether the fixture files follow the contract.
Runtime validation would run a future writer and check behavior. This target
only covers the static side.

Passing this target would not mean the manifest writer is ready, because the
manifest writer and manifest file writing still do not exist.

## 13. What This Does Not Do

- does not add release-quality integration
- does not implement the manifest writer
- does not write manifest files
- does not connect artifact writer CLI
- does not use real data
- does not compute metrics
- does not prove production readiness

## 14. Next Recommended Steps

- Step385: design release-quality integration
- Step386: integrate the wrapper
- Step387: design remote/manual run record workflow
- Step388: create the remote/manual run status marker
- later: design and implement runtime manifest writer behavior separately

## 15. Step384 Implementation Status

Step384 implements the standalone Makefile target:

`check-learner-state-frozen-policy-generation-manifest-writer-fixtures`

The target runs the static fixture validator over the 30-case / 150-JSON
synthetic metadata-only manifest writer fixture root. It uses the human
summary output, does not use `--json` by default, does not write manifest
files, and remains outside release-quality.

This implementation does not change the release-quality wrapper, workflow
YAML, Python code/tests, fixture JSON, manifest writer behavior, manifest
body generation, manifest file writing, artifact writer CLI integration,
metrics, real-data use, or production readiness claims.

## 16. Related Documents

- [Frozen policy generation manifest writer boundary design](frozen_policy_generation_manifest_writer_boundary_design.md)
- [Frozen policy generation manifest writer fixture contract design](frozen_policy_generation_manifest_writer_fixture_contract_design.md)
- [Frozen policy generation manifest writer fixture validator design](frozen_policy_generation_manifest_writer_fixture_validator_design.md)
- [Frozen policy generation manifest writer fixtures](../tests/fixtures/learner_state_frozen_policy_generation_manifest_writer/README.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)
