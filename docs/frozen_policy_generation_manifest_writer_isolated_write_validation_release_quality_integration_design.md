# Frozen Policy Generation Manifest Writer Metadata-Only Isolated Write Validation Release-Quality Integration Design

## 1. Purpose

This document designs future release-quality wrapper integration for the
manifest writer metadata-only isolated write validation target.

It is docs-only. It is not wrapper implementation, not workflow change, not
production-facing runtime file writing, not public `--manifest-out`, not
artifact writer CLI integration, and not a production readiness claim.

The design remains synthetic-only, metadata-only, no-oracle, body-free,
path-safe, and count-only.

## 2. Current State

- The isolated write fixture root exists.
- The isolated write validation module exists.
- Focused isolated write validation tests exist.
- The standalone Makefile target exists.
- Release-quality integration does not exist.
- Production-facing runtime file writing does not exist.
- Public `--manifest-out` is not implemented.
- Artifact writer CLI integration does not exist.

## 3. Proposed Wrapper Insertion Point

Candidate A:

Place the isolated write validation target immediately after manifest writer
file writing fixture validation and before config/scoring smoke checks.

Candidate B:

Place it after manifest writer runtime smoke and before file writing fixture
validation.

Candidate C:

Place it after config/scoring smoke checks.

Recommended: Candidate A.

Reasons:

- Static file writing fixture validation should run before isolated write
  validation, so the order reads contract integrity then isolated write
  harness behavior.
- The manifest writer chain stays grouped as static fixture validation,
  runtime fixture validation, runtime smoke, file writing fixture validation,
  then isolated write validation.
- Candidate B places isolated write validation before the static file writing
  fixture contract check that frames it.
- Candidate C separates the manifest writer chain from the downstream
  config/scoring checks.

Intended order:

- artifact writer fixture validation
- artifact writer runtime smoke
- artifact body fixture validation
- artifact body generation CLI smoke
- artifact body generation safe-metadata CLI smoke
- artifact body file writing fixture validation
- artifact body isolated write validation
- static manifest writer fixture validation
- runtime manifest writer fixture validation
- runtime manifest writer smoke
- manifest writer file writing fixture validation
- manifest writer isolated write validation
- config and scoring smoke checks

## 4. Proposed Wrapper Command

`make check-learner-state-frozen-policy-generation-manifest-writer-isolated-write-validation`

## 5. Proposed Wrapper Label

`release_quality_check: learner-state frozen policy generation manifest writer isolated write validation`

## 6. Expected Wrapper Behavior

- target pass -> release-quality continues
- target fail -> release-quality fails
- target writes only inside validator-owned isolated temporary roots during
  `pass_written` cases
- target cleans up and reports residue count 0
- target does not write to normal project output directories
- target does not imply production-facing runtime file writing readiness
- target does not imply public `--manifest-out`

Expected body-free / count-only output:

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

## 7. Failure Interpretation

Release-quality should fail if any of these occur:

- target exits nonzero
- mismatched_cases > 0
- input_error_cases > 0
- total_cases != 25
- total_json_files != 150
- category counts mismatch
- required file missing
- malformed JSON
- schema mismatch
- case_id mismatch
- category mismatch
- reason code mismatch
- unsafe selector
- unsafe isolated root policy
- output path outside isolated root
- stdout/stderr body leakage
- forbidden body, payload, raw, logit, private-path, or absolute-path marker
  in public output
- written file forbidden content
- parseable JSON check failure
- cleanup failure
- residue_file_count > 0
- temp_root_isolated=false
- normal manifest tmp residue > 0

This failure is not production-facing runtime file writing failure, not public
`--manifest-out` failure, not artifact writer CLI integration failure, not
model performance failure, not real-data readiness, and not production
readiness.

## 8. Log Safety Review

Allowed in wrapper output:

- label
- command
- mode
- validation schema version
- total counts
- category counts
- safety flags
- residue_file_count=0
- stdout_body_suppressed=true
- stderr_body_suppressed=true
- temp_root_isolated=true
- release_quality_ready=false

Forbidden in wrapper output and docs:

- written file JSON body
- fixture JSON bodies
- isolated write request body
- manifest writer request body
- pointer body
- expected result body
- manifest body
- manifest JSON body
- artifact body payload
- generated policy body
- raw rows
- logits/probabilities
- private paths
- absolute temp paths
- raw learner text
- final text
- observed_after_text
- gold labels
- scoring feedback payload
- real participant data
- performance metric body
- raw GitHub logs
- full job output copied into docs

## 9. Relation To Current Isolated Write CLI

The wrapper should call the Makefile target. The Makefile target wraps CLI root
validation, does not pass `--json` by default, writes only inside
validator-owned isolated temporary roots, performs cleanup inside the
validator, and emits body-free / count-only output.

## 10. Relation To Static File Writing Fixture Validator

The static file writing fixture validator checks future file writing contract
fixtures without writing files. Isolated write validation writes minimal
metadata-only JSON in an isolated temporary root.

The static validator should run before isolated write validation. Both should
remain separate release-quality labels.

## 11. Relation To Existing Runtime Targets

- Runtime fixture validation validates runtime fixtures statically.
- Runtime smoke executes the no-file metadata-only runtime.
- File writing fixture validation checks static file writing contracts.
- Isolated write validation checks isolated temporary-root write harness
  behavior.
- Public `--manifest-out` remains separate.

## 12. Relation To Artifact Body Isolated Write Validation

Artifact body isolated write validation already exists and remains separate.
Manifest writer isolated write validation should have its own label and should
not call artifact body generation CLI or artifact writer CLI.

## 13. Relation To Production-Facing Runtime File Writing

Target success proves only the isolated validation harness behavior. It does
not prove normal project output writing, public `--manifest-out`, production
file output readiness, real-data readiness, or production readiness.

## 14. Relation To Release-Quality Staging

- Step425: design only
- Step426: wrapper integration
- Step427: remote/manual status marker design or marker
- later production-facing runtime file writing design / implementation
- later artifact writer CLI integration

## 15. Testing Plan For Future Wrapper Implementation

Future Step426 should verify:

- standalone target passes
- `make check-release-quality` includes the new label
- `make check-release-quality` passes
- output includes 25 / 150 / 5 / 1 / 14 / 5
- residue_file_count=0
- stdout_body_suppressed=true
- stderr_body_suppressed=true
- temp_root_isolated=true
- normal manifest tmp residue is 0
- Makefile diff remains none
- workflow diff remains none
- wrapper diff is limited to the new label and command

## 16. Safety Interpretation

Release-quality success after future integration will mean isolated write
validation harness passed in the wrapper. It will not mean production-facing
manifest file writing works, public `--manifest-out` exists, artifact writer
CLI integration exists, production readiness, real-data readiness, or model
performance.

## 17. Beginner-Friendly Explanation

Release-quality is the routine check bundle. Adding isolated write validation
there later will make the temporary-root write harness run on every release
quality pass.

It belongs after static file writing fixture validation because first we check
the contract files without writing, then we check that the isolated write
harness can write and clean up safe metadata-only JSON.

That success still is not production file writing success. The write happens
inside a validator-owned temporary root, not a normal user or project output
path.

CI should check stdout/stderr body suppression and cleanup because file
writing bugs often leak content through output streams or leave files behind.

## 18. What This Does NOT Do

- does not modify the wrapper
- does not modify workflow YAML
- does not modify Makefile
- does not modify Python code/tests
- does not modify fixtures
- does not implement production-facing runtime file writing
- does not implement public `--manifest-out`
- does not connect artifact writer CLI
- does not use real data
- does not compute metrics
- does not prove production readiness

## 19. Next Recommended Steps

- Step426: wrapper integration
- Step427: remote/manual run record workflow design
- later remote/manual status marker
- later production-facing runtime file writing design / implementation
- later artifact writer CLI integration

## 20. Related Documents

- [Frozen policy generation manifest writer metadata-only isolated write validation Makefile target design](frozen_policy_generation_manifest_writer_isolated_write_validation_makefile_target_design.md)
- [Frozen policy generation manifest writer metadata-only isolated write validation design](frozen_policy_generation_manifest_writer_isolated_write_validation_design.md)
- [Frozen policy generation manifest writer metadata-only isolated write fixture contract design](frozen_policy_generation_manifest_writer_isolated_write_fixture_contract_design.md)
- [Frozen policy generation manifest writer metadata-only isolated write validation fixtures](../tests/fixtures/learner_state_frozen_policy_generation_manifest_writer_isolated_write_validation/README.md)
- [Frozen policy generation manifest writer metadata-only isolated write validation release-quality remote run record workflow](frozen_policy_generation_manifest_writer_isolated_write_validation_release_quality_remote_run_record_workflow.md)
- [Learner-state frozen policy generation manifest writer isolated write validation release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_isolated_write_validation_release_quality_remote_run_status.md)
- [Frozen policy generation manifest writer metadata-only file writing fixture release-quality integration design](frozen_policy_generation_manifest_writer_file_writing_fixture_release_quality_integration_design.md)
- [Frozen policy generation manifest writer metadata-only file writing boundary design](frozen_policy_generation_manifest_writer_file_writing_boundary_design.md)
- [Learner-state frozen policy generation manifest writer file writing fixture release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_file_writing_fixture_release_quality_remote_run_status.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)

## 21. Step426 Wrapper Integration Status

Step426 implements the release-quality wrapper integration for:

`check-learner-state-frozen-policy-generation-manifest-writer-isolated-write-validation`

The wrapper now runs this target after manifest writer file writing fixture
validation and before config/scoring smoke checks, using the label:

`release_quality_check: learner-state frozen policy generation manifest writer isolated write validation`

The integration is intentionally limited to wrapper wiring. It does not
change workflow YAML, Makefile, Python code/tests, fixture JSON,
production-facing runtime file writing, public `--manifest-out`, artifact
writer CLI integration, metrics, real-data use, or production readiness.

The target output remains body-free and count-only. It may report the
25-case / 150-JSON isolated write validation summary, residue count 0,
stdout/stderr body suppression, temp-root isolation, and safety flags, but it
must not copy written file bodies, fixture JSON bodies, request/pointer/result
bodies, manifest bodies, artifact body payloads, generated policy bodies,
raw rows, logits, private paths, absolute temp paths, raw learner text, real
participant data, raw logs, or full job output into docs.

## 22. Step427 Remote Run Record Workflow Design Status

Step427 adds the docs-only remote/manual run record workflow design:

[Frozen policy generation manifest writer metadata-only isolated write validation release-quality remote run record workflow](frozen_policy_generation_manifest_writer_isolated_write_validation_release_quality_remote_run_record_workflow.md).

The workflow design specifies the future status marker path, allowed
public-safe metadata, forbidden raw logs and body content, status marker
sections, pass-only/count-only isolated write validation summary, related
check summaries, safety review, failure handling, and next recording steps.
It does not create the status marker, run a workflow, change workflow YAML,
change the wrapper, change Makefile, change Python code/tests, change fixture
JSON, implement production-facing runtime file writing, expose public
`--manifest-out`, connect artifact writer CLI, compute metrics, use real
data, or claim production readiness.

## 23. Step428 Remote Run Status Marker Status

Step428 creates the public-safe remote/manual Release Quality status marker:

[Learner-state frozen policy generation manifest writer isolated write validation release-quality remote run status](status/learner_state_frozen_policy_generation_manifest_writer_isolated_write_validation_release_quality_remote_run_status.md).

The marker records only safe run identity metadata, wrapper inclusion
metadata, pass-only/count-only isolated write validation summary fields,
related check inclusion summaries, safety review, interpretation, and
non-goals. It does not copy raw logs, full job output, written file JSON
bodies, fixture JSON bodies, request/pointer/expected-result bodies, manifest
bodies, artifact body payloads, generated policy bodies, private paths,
absolute temp paths, raw learner text, real participant data, or performance
evidence.

Step428 does not change workflow YAML, release-quality wrapper, Makefile,
Python code/tests, fixture JSON, production-facing runtime file writing,
public `--manifest-out`, artifact writer CLI integration, metrics,
real-data use, or production readiness.
