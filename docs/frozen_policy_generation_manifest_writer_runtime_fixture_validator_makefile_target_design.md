# Frozen Policy Generation Manifest Writer Runtime Fixture Validator Makefile Target Design

## 1. Purpose

This document fixes the docs-only design for a future standalone Makefile
target that runs the manifest writer runtime fixture validator.

This is not a Makefile target implementation, not release-quality
integration, not manifest writer runtime implementation, not manifest file
writing, and not a production readiness claim.

## 2. Current State

- the runtime fixture validator module exists
- the runtime fixture validator CLI exists
- the runtime fixtures exist
- the CLI validates 31 cases and 155 JSON files
- the standalone Makefile target does not exist
- release-quality integration does not exist
- the manifest writer runtime does not exist
- the manifest writer CLI does not exist
- manifest file writing does not exist
- artifact writer CLI integration does not exist

The current validator is static runtime fixture validation only. It checks
synthetic metadata-only request / pointer / expected-result fixture contracts
and does not execute a manifest writer runtime.

## 3. Proposed Target Name

Candidate target names:

- `check-learner-state-frozen-policy-generation-manifest-writer-runtime-fixtures`
- `check-learner-state-frozen-policy-generation-manifest-writer-runtime-fixture-validation`
- `check-learner-state-manifest-writer-runtime-fixtures`
- `check-manifest-writer-runtime-fixtures`

Recommended target:

`check-learner-state-frozen-policy-generation-manifest-writer-runtime-fixtures`

Reasons:

- it is distinct from the existing static manifest writer fixture target
- it makes runtime request / pointer / expected-result fixture contract
  validation recognizable
- it stays inside the learner-state / frozen policy generation namespace
- it remains clear when it is later added to release-quality
- it is long, but matches the existing target naming style

## 4. Proposed Command

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_manifest_writer_runtime_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime`

The default target should use the human summary output, not `--json`.

## 5. Proposed Help Text

`check-learner-state-frozen-policy-generation-manifest-writer-runtime-fixtures  Validate manifest writer runtime fixture contracts`

## 6. Expected Behavior

The future target should exit 0 when the runtime fixture root matches the
static validator contract.

Expected summary fields and values:

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
- `expected_manifest_writer_runtime_result` body
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

`check-learner-state-frozen-policy-generation-manifest-writer-fixtures`
checks the existing static manifest writer fixture contract for the metadata
index fixture root.

The proposed runtime target checks the runtime request / pointer /
expected-result fixture contract root.

The proposed target must not replace the existing static target. It must not
execute the runtime writer, write manifest files, or imply runtime writer
readiness. Runtime writer smoke coverage and manifest file writing checks
remain future and separate.

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
because this runtime fixture validator does not execute a writer.

## 10. Future Implementation Checks

The Makefile implementation step should verify:

- `make help` includes the target
- the target exits 0
- target output includes `total_cases=31`
- target output includes `matched_cases=31`
- target output includes `input_error_cases=0`
- target output includes `runtime_writer_executed=false`
- target output includes `manifest_file_written=false`
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

The CLI already knows how to validate the runtime fixture root. A Makefile
target gives developers a short, memorable command for the same check.

The existing static manifest writer fixture target checks the metadata index
fixture root. The proposed runtime fixture target checks the future runtime
request, pointer, and expected-result fixture root.

The target should not enter release-quality immediately. First it should run
standalone, remain body-free, and show stable counts. Then release-quality can
include it in a separate wrapper step.

Passing this target would not mean runtime writer readiness, because the
manifest writer runtime, manifest writer CLI, and manifest file writing still
do not exist.

## 13. What This Does Not Do

- does not implement a Makefile target
- does not add release-quality integration
- does not implement runtime writer
- does not write manifest files
- does not connect artifact writer CLI
- does not use real data
- does not compute metrics
- does not prove production readiness

## 14. Next Recommended Steps

- Step395: Makefile target implementation
- Step396: release-quality integration design
- Step397: wrapper integration
- Step398: remote/manual run record workflow design
- Step399: remote/manual run status marker
- later: runtime manifest writer design / implementation

## 15. Step395 Implementation Status

Step395 implements the standalone Makefile target:

`check-learner-state-frozen-policy-generation-manifest-writer-runtime-fixtures`

The target runs the static runtime fixture validator over the 31-case /
155-JSON synthetic metadata-only runtime fixture root. It uses the human
summary output, does not use `--json` by default, does not execute a runtime
writer, does not write manifest files, and remains outside release-quality.

This implementation does not change the release-quality wrapper, workflow
YAML, Python code/tests, fixture JSON, manifest writer runtime behavior,
manifest writer CLI behavior, manifest body generation, manifest file
writing, artifact writer CLI integration, metrics, real-data use, or
production readiness claims.

## 16. Related Documents

- [Frozen policy generation manifest writer runtime fixture validator design](frozen_policy_generation_manifest_writer_runtime_fixture_validator_design.md)
- [Frozen policy generation manifest writer runtime fixture contract design](frozen_policy_generation_manifest_writer_runtime_fixture_contract_design.md)
- [Frozen policy generation manifest writer runtime fixtures](../tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_runtime/README.md)
- [Frozen policy generation manifest writer runtime API design](frozen_policy_generation_manifest_writer_runtime_api_design.md)
- [Frozen policy generation manifest writer boundary design](frozen_policy_generation_manifest_writer_boundary_design.md)
- [Frozen policy generation manifest writer fixture validator Makefile target design](frozen_policy_generation_manifest_writer_fixture_validator_makefile_target_design.md)
- [Learner-state frozen policy generation manifest writer fixture release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_fixture_release_quality_remote_run_status.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)
