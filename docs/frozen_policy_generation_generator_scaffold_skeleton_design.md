# Frozen Policy Generation Generator Scaffold Skeleton Design

This document defines the Step290 docs-only design for a future frozen policy
generation generator scaffold skeleton.

The proposed skeleton is a metadata-only boundary. It would read only safe
request and input pointer metadata, produce a deterministic safe plan/result,
and keep artifact body generation and file writing out of scope.

This is not an implementation. It does not add Python code, tests, fixtures,
Makefile targets, release-quality wrapper changes, GitHub Actions workflow
changes, generated policy bodies, artifact bodies, artifact writers, metrics,
or real-data readiness.

## 1. Purpose

The purpose of this document is to design the first generator scaffold skeleton
before implementation.

The design covers:

- module boundary
- metadata-only dataclasses
- public API candidates
- input and output contracts
- fixed artifact and safety flags
- count-only summaries
- fail-closed behavior
- relationship to the existing generator scaffold fixture validator
- future test, CLI, Makefile, release-quality, and status-marker staging

This document is not:

- a generator scaffold implementation
- an artifact writer
- artifact body generation
- generated policy body generation
- performance evaluation
- calibration implementation
- selective prediction implementation
- learner-state estimator implementation
- metric computation
- real-data readiness claim
- production readiness claim

## 2. Current State

The following pieces already exist:

- generator scaffold fixture root:
  `tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/`
- generator scaffold fixture validator module:
  `python/learner_state/frozen_policy_generation_generator_scaffold_fixture_validation.py`
- generator scaffold fixture validator CLI:
  `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_generator_scaffold_fixture_validation`
- Makefile target:
  `make check-learner-state-frozen-policy-generation-generator-scaffold-fixtures`
- release-quality wrapper integration:
  `release_quality_check: learner-state frozen policy generation generator scaffold fixture validation`
- remote status marker:
  `docs/status/learner_state_frozen_policy_generation_generator_scaffold_fixture_release_quality_remote_run_status.md`

The following pieces do not exist yet:

- generator scaffold implementation
- generator scaffold CLI
- generated policy body
- artifact writer
- artifact file writing
- artifact manifest writer
- generator quality evaluation
- performance evaluation

## 3. Skeleton Basic Policy

The first skeleton should be deliberately small and conservative.

Required behavior:

- metadata-only
- read request metadata only
- read pointer metadata only
- do not read raw rows
- do not read logits or probability dumps
- do not read request body payloads beyond required metadata
- do not emit policy bodies
- do not emit artifact bodies
- do not write files
- return a safe metadata-only plan/result
- fail closed on unsafe input
- deterministic output
- JSON serializable output
- no performance claims
- no real-data behavior

The skeleton is allowed to inspect schema labels, IDs, safe labels, flags,
reason-code expectations, and count-only validation references. It is not
allowed to inspect or create any body content.

## 4. Proposed Module

Candidate module names:

- `python/learner_state/frozen_policy_generation_generator_scaffold.py`
- `python/learner_state/frozen_policy_generation_generator.py`
- `python/learner_state/frozen_policy_generation_generator_scaffold_runtime.py`

Recommended module:

`python/learner_state/frozen_policy_generation_generator_scaffold.py`

Reasons:

- it clearly names the generator scaffold boundary
- it stays separate from the existing runtime scaffold module
- it avoids implying a complete generator or artifact writer
- it stays separate from the fixture validator module
- it can later host a thin CLI without changing fixture validation code

## 5. Proposed Dataclasses

All dataclasses should be metadata-only and serializable to safe plain
dictionaries.

### FrozenPolicyGenerationGeneratorRequest

Suggested fields:

- `schema_version`
- `request_id`
- `generator_mode`
- `validation_reference_ids`
- `split_policy_label`
- `calibration_policy_label`
- `threshold_policy_label`
- `abstention_policy_label`
- `artifact_policy_label`
- `synthetic_only`
- `no_oracle_required`
- `requested_artifact_body`
- `requested_file_writing`
- `expected_generation_status`
- `expected_reason_codes`
- `notes`

This structure represents safe request metadata. It must not contain request
body payloads, raw data, policy bodies, or artifact bodies.

### FrozenPolicyGenerationGeneratorInputPointer

Suggested fields:

- `schema_version`
- `pointer_id`
- `fixture_label`
- `validation_fixture_label`
- `frozen_policy_validation_label`
- `selective_prediction_validation_label`
- `source_kind`
- `synthetic_only`
- `no_raw_rows`
- `no_logits_dump`
- `no_private_paths`
- `notes`

This structure represents safe pointer metadata. It must not contain pointed-to
payload bodies, raw rows, logits, private paths, or raw learner text.

### FrozenPolicyGenerationGeneratorMetadataPlan

Suggested fields:

- `schema_version`
- `request_id`
- `pointer_id`
- `generator_mode`
- `policy_id`
- `artifact_id`
- `generator_version`
- `validation_reference_ids`
- `planned_artifact_metadata_fields`
- `planned_checks`
- `artifact_flags`
- `safety_flags`
- `count_summary`
- `safe_summary`

This plan is the skeleton's body-free description of what would be generated
later. It is not a policy body and not an artifact body.

### FrozenPolicyGenerationGeneratorArtifactMetadata

Suggested fields:

- `policy_id`
- `artifact_id`
- `generator_version`
- `artifact_policy_label`
- `split_policy_label`
- `calibration_policy_label`
- `threshold_policy_label`
- `abstention_policy_label`
- `validation_reference_count`
- `artifact_metadata_field_count`

This metadata can identify a future artifact shell without containing the
artifact body.

### FrozenPolicyGenerationGeneratorSafetySummary

Suggested fields:

- `content_suppressed`
- `no_raw_rows`
- `no_logits_dump`
- `no_private_paths`
- `no_performance_claims`
- `synthetic_only_checked`
- `no_oracle_checked`
- `test_tuning_checked`
- `scoring_feedback_checked`
- `artifact_policy_checked`
- `body_suppression_checked`
- `file_writing_checked`

All fields should be booleans. In the initial skeleton, all required safety
fields should be true for both pass and fail-closed results.

### FrozenPolicyGenerationGeneratorResult

Suggested fields:

- `schema_version`
- `generation_status`
- `reason_codes`
- `failed_checks`
- `request_id`
- `pointer_id`
- `policy_id`
- `artifact_id`
- `generator_version`
- `validation_reference_ids`
- `artifact_flags`
- `safety_flags`
- `count_summary`
- `safe_summary`
- `metadata_plan_summary`

This is the public safe result. It must never include policy body, artifact
body, raw rows, logits, private paths, raw learner text, or performance metric
body content.

### FrozenPolicyGenerationGeneratorError

Suggested fields:

- `error_status`
- `reason_codes`
- `failed_checks`
- `request_id`
- `pointer_id`
- `safe_summary`
- `content_suppressed`

This structure represents safe input errors or fail-closed errors without
including raw input bodies or private paths.

## 6. Proposed Public APIs

The first implementation should keep validation and generation logic small.

### load_frozen_policy_generation_generator_request(path)

Responsibility:

- read a request file
- parse only safe metadata
- reject malformed input safely
- avoid returning raw body payloads

Return type:

- `FrozenPolicyGenerationGeneratorRequest`
- or `FrozenPolicyGenerationGeneratorError`

### load_frozen_policy_generation_generator_input_pointer(path)

Responsibility:

- read an input pointer file
- parse only safe pointer metadata
- reject malformed input safely
- avoid dereferencing raw data payloads

Return type:

- `FrozenPolicyGenerationGeneratorInputPointer`
- or `FrozenPolicyGenerationGeneratorError`

### build_frozen_policy_generation_generator_metadata_plan(request, pointer)

Responsibility:

- combine safe request and pointer metadata
- construct a metadata-only plan
- set fixed artifact and safety flags
- compute count-only summary fields
- fail closed when unsafe metadata requests body generation or file writing

Return type:

- `FrozenPolicyGenerationGeneratorMetadataPlan`
- or `FrozenPolicyGenerationGeneratorResult` with `generation_status=fail`

### validate_frozen_policy_generation_generator_metadata_plan(plan)

Responsibility:

- check that the plan is body-free
- check artifact flags
- check safety flags
- check count-only zero constraints
- check no forbidden payload markers appear as actual payload fields

Return type:

- `FrozenPolicyGenerationGeneratorResult`

### run_frozen_policy_generation_generator_scaffold(request_path, pointer_path)

Responsibility:

- load request metadata
- load pointer metadata
- build a metadata plan
- validate the plan
- return a safe metadata-only result
- never write artifacts
- never emit policy bodies

Return type:

- `FrozenPolicyGenerationGeneratorResult`

### summarize_frozen_policy_generation_generator_result(result)

Responsibility:

- produce a safe human or dictionary summary
- include only status, reason codes, flags, counts, IDs, and safe summary labels
- exclude request/pointer/result bodies and artifact bodies

Return type:

- safe string summary
- or safe dictionary summary

### audit_frozen_policy_generation_generator_safety(result)

Responsibility:

- scan the result summary for body leakage
- confirm artifact flags and safety flags
- confirm zero body/raw/logits/private-path/performance counts
- fail closed if an unsafe field is present

Return type:

- `FrozenPolicyGenerationGeneratorSafetySummary`
- or safe fail-closed result

## 7. Input Contract

Allowed request and pointer metadata:

- `schema_version`
- `request_id`
- `pointer_id`
- `fixture_label`
- `generator_mode`
- `validation_reference_ids`
- `split_policy_label`
- `calibration_policy_label`
- `threshold_policy_label`
- `abstention_policy_label`
- `artifact_policy_label`
- `synthetic_only`
- `no_oracle_required`
- `expected_generation_status`
- `expected_reason_codes`
- safe notes
- count-only validation references

Forbidden input payload:

- raw rows
- logits
- probabilities
- raw learner text
- observed-after text
- final text
- gold labels
- expected action scoring feedback payload
- request body payload
- pointer body payload
- expected result body payload
- policy body
- generated artifact body
- private paths
- real participant data
- calibration body
- label body
- split body
- performance metric body

Marker words may appear as case labels, reason codes, failed checks, safe
notes, safety flag names, or count field names only when they do not introduce
payload content.

## 8. Output Contract

Allowed output:

- `schema_version`
- `generation_status`
- `reason_codes`
- `failed_checks`
- `request_id`
- `pointer_id`
- `policy_id`
- `artifact_id`
- `generator_version`
- `validation_reference_ids`
- `artifact_flags`
- `safety_flags`
- `count_summary`
- `safe_summary`
- metadata-only plan summary

Forbidden output:

- policy body
- artifact body
- generated JSON body
- raw rows
- logits
- probabilities
- raw learner text
- final text
- observed-after text
- gold text
- private paths
- performance metric body

The initial success summary should use a stable safe label such as:

- `metadata_only_generator_scaffold_result`

The initial fail-closed summary should use a stable safe label such as:

- `fail_closed_metadata_only_generator_scaffold_result`

## 9. Artifact Flags

Initial fixed values:

- `generated_artifact_written=false`
- `generated_artifact_body_available=false`
- `artifact_body_suppressed=true`
- `artifact_file_path_available=false`
- `artifact_manifest_available=false`
- `artifact_validation_summary_available=true`

These values should remain fixed for both pass and fail-closed results in the
initial skeleton. Invalid input must not cause artifact writing or artifact body
generation.

## 10. Safety Flags

Required true values:

- `content_suppressed`
- `no_raw_rows`
- `no_logits_dump`
- `no_private_paths`
- `no_performance_claims`
- `synthetic_only_checked`
- `no_oracle_checked`
- `test_tuning_checked`
- `scoring_feedback_checked`
- `artifact_policy_checked`
- `body_suppression_checked`
- `file_writing_checked`

The skeleton should treat any false required safety flag as a validation
failure.

## 11. count_summary

Allowed count-only fields:

- `validation_reference_count`
- `artifact_metadata_field_count`
- `body_field_count=0`
- `raw_row_count=0`
- `logits_dump_count=0`
- `private_path_count=0`
- `performance_metric_count=0`
- `generated_artifact_count=0`
- `written_file_count=0`

Counts must be integers and must not be negative. Body, raw row, logits,
private path, performance metric, generated artifact, and written file counts
must stay zero in the initial skeleton.

## 12. Fail-Closed Behavior

The skeleton should fail closed instead of panicking or producing partial body
content.

Recommended reason codes:

- `missing_required_field`
- `unknown_schema_version`
- `missing_validation_reference`
- `unvalidated_input`
- `raw_rows_carryover`
- `logits_dump_carryover`
- `request_body_leakage`
- `pointer_body_leakage`
- `expected_result_body_leakage`
- `generated_artifact_body_leakage`
- `artifact_file_writing_not_allowed`
- `private_path_output`
- `test_temperature_tuning`
- `test_threshold_tuning`
- `scoring_feedback_violation`
- `performance_claim_in_generated_policy`
- `non_synthetic_input`
- `no_oracle_violation`

Fail-closed result requirements:

- `generation_status=fail`
- at least one reason code
- at least one failed check
- no artifact body
- no artifact file writing
- no raw rows
- no logits
- no private paths
- no performance claims
- safe summary only

## 13. Relation To Existing Validator

The generator scaffold fixture validator validates the fixture contract. It
does not run a generator.

The future generator scaffold skeleton would consume a request and pointer,
then return a safe metadata-only result. It should not replace the validator.

Future compatibility tests should compare skeleton results with the
`expected_generator_scaffold_result.json` metadata in the fixture root without
printing or embedding that expected-result body in docs.

The validator CLI remains separate until a generator scaffold CLI is designed.

## 14. Proposed Tests For Future Implementation

Future implementation tests should include:

- load valid request and pointer metadata
- minimal valid case returns pass
- fixed threshold valid case returns pass
- fixed abstention-rate valid case returns pass
- all 15 invalid fixtures return expected fail reason
- malformed request returns safe input error
- missing pointer returns safe input error
- forbidden raw rows marker in payload returns fail closed
- generated artifact body request returns fail closed
- artifact file writing request returns fail closed
- no body in summary
- result is JSON serializable
- result is deterministic
- no tmp output
- no artifact file written
- no private path output
- result is compatible with `expected_generator_scaffold_result.json`

Tests should use synthetic-only fixtures and should not print fixture bodies.

## 15. Proposed CLI Future

Do not implement a CLI in the skeleton implementation step unless a separate
CLI step explicitly asks for it.

Likely future entrypoint:

`PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_generator_scaffold`

Likely future arguments:

- `--request`
- `--pointer`
- `--json`

Initial CLI constraints:

- no file writing option
- no artifact body output
- no generated policy body output
- no raw rows
- no logits
- no private paths
- safe human summary by default
- parseable safe JSON summary with `--json`

## 16. Proposed Makefile Future

Do not add a Makefile target in the skeleton implementation step.

After skeleton implementation, tests, and CLI exist, a future standalone smoke
target can be designed. It should run one or more synthetic metadata-only cases
and must not write artifacts.

The target should not enter release-quality until:

- standalone target passes
- no-body-leakage review passes
- no tmp output or artifact writing is confirmed
- CLI output remains metadata-only

## 17. Release-Quality Future

Generator scaffold fixture validation is already included in release-quality.
That validates fixture contract only.

The future generator scaffold skeleton runtime should not be added to
release-quality until implementation, tests, CLI, and Makefile target exist.

Even then, success would mean only that the skeleton returns a safe
metadata-only result. It would not prove generator quality, artifact generation,
policy quality, model performance, or production readiness.

## 18. Status Marker Future

A future remote status marker may be created after skeleton runtime is
integrated and passes remotely.

Any such marker should be:

- count-only
- pass-only
- raw-log-free
- body-free
- artifact-body-free
- policy-body-free
- private-path-free

It should not copy request bodies, pointer bodies, expected-result bodies,
artifact bodies, raw rows, logits, or raw learner text.

## 19. No-Oracle / Synthetic-Only Boundary

The skeleton must keep this boundary:

- no real data
- no participant data
- no raw learner text
- no final text
- no gold labels
- no observed-after text
- no expected action scoring feedback
- no test-derived tuning payload
- no artifact body
- no logits
- no raw rows
- no private paths

The only allowed inputs and outputs are synthetic-only, metadata-only,
count-only, and safe marker labels.

## 20. What This Does NOT Do

This design does not:

- implement a generator beyond the metadata-only skeleton boundary
- add a CLI
- change fixtures
- change the Makefile
- change the release-quality wrapper
- change GitHub Actions workflows
- generate policy bodies
- write artifacts
- write manifests
- compute metrics
- evaluate performance
- use real data
- prove production readiness

## 21. Beginner-Friendly Explanation

A skeleton is the smallest safe shape of a future component. It lets the
project agree on inputs, outputs, flags, and failure behavior before the real
implementation grows.

This skeleton should not create an artifact body yet because artifact bodies
carry much higher leakage risk. The first useful milestone is proving that the
system can read safe metadata and return safe metadata without touching raw
data.

It should not write files yet because file writing expands the safety surface.
The first version should be easy to inspect: no output file, no generated
policy, no artifact path, no cleanup.

The fixture validator checks that fixture files follow the contract. The
generator scaffold skeleton will be a separate component that consumes safe
request/pointer metadata and returns a safe result.

If the skeleton succeeds, that means the metadata-only boundary works. It does
not mean the final generator is good, useful, calibrated, performant, or ready
for real data.

## 22. Next Recommended Steps

Recommended sequence after Step291:

- Step292: skeleton CLI design
- Step293: skeleton CLI implementation
- Step294: CLI test expansion if needed
- Step295: Makefile target design
- later: Makefile target implementation
- later: release-quality integration design
- later: remote status marker after remote success

Each step should remain synthetic-only and metadata-only until a future
artifact-body or artifact-writing design explicitly changes that boundary.

## 23. Step291 Implementation Status

Step291 implements the metadata-only skeleton at
`python/learner_state/frozen_policy_generation_generator_scaffold.py` and adds
focused tests at
`python/learner_state/tests/test_frozen_policy_generation_generator_scaffold.py`.

The implementation:

- loads safe request metadata
- loads safe input pointer metadata
- builds a metadata-only plan
- returns a safe result compatible with
  `expected_generator_scaffold_result.json`
- passes the three valid fixture cases
- returns fail-closed results for the fifteen invalid fixture cases
- returns safe input errors for malformed or missing input files
- keeps artifact writing disabled
- keeps artifact body generation disabled
- keeps generated policy body generation disabled
- does not add a CLI in Step291
- does not add a Makefile target
- does not change release-quality
- does not change workflows
- does not change fixtures

The implementation remains synthetic-only and metadata-only. It still does not
prove generator quality, policy quality, model performance, calibration
quality, real-data readiness, or production readiness.

## 24. Step292 CLI Design Status

Step292 designs the future safe CLI boundary for running the implemented
metadata-only skeleton:
[Frozen policy generation generator scaffold CLI design](frozen_policy_generation_generator_scaffold_cli_design.md).

The design keeps CLI implementation, Makefile target changes, release-quality
integration, workflow changes, fixture changes, artifact body generation,
generated policy body generation, artifact writing, metric computation, and
real-data readiness out of scope.

## 25. Step293 CLI Implementation Status

Step293 implements the safe CLI entrypoint in
`python/learner_state/frozen_policy_generation_generator_scaffold.py` and adds
focused CLI tests at
`python/learner_state/tests/test_frozen_policy_generation_generator_scaffold_cli.py`.

The CLI remains a thin wrapper over the skeleton APIs. It emits safe
metadata-only human or JSON summaries, does not write files, does not generate
artifact bodies, does not generate policy bodies, and does not add Makefile,
release-quality, workflow, or fixture changes.

## 26. Step294 CLI Makefile Target Design Status

Step294 designs a future valid-only Makefile runtime smoke target for the safe
generator scaffold CLI:
[Frozen policy generation generator scaffold CLI Makefile target design](frozen_policy_generation_generator_scaffold_cli_makefile_target_design.md).

The skeleton remains unchanged by that design. It still produces metadata-only
results, writes no files, emits no artifact bodies, emits no generated policy
bodies, and makes no performance or real-data readiness claim.

## 27. Step295 CLI Makefile Target Implementation Status

Step295 implements the standalone valid-only Makefile runtime smoke target for
the safe generator scaffold CLI. The skeleton remains unchanged: it still
returns metadata-only results, writes no files, emits no artifact bodies, emits
no generated policy bodies, and makes no performance or real-data readiness
claim.

## 28. Step296 Release-Quality Integration Design Status

Step296 designs future release-quality integration for the generator scaffold
runtime smoke target:
[Frozen policy generation generator scaffold runtime release-quality integration design](frozen_policy_generation_generator_scaffold_runtime_release_quality_integration_design.md).

The skeleton remains unchanged. The design does not add wrapper integration,
workflow changes, artifact writing, artifact bodies, generated policy bodies,
metrics, or real-data readiness claims.

## 29. Step297 Release-Quality Wrapper Integration Status

Step297 adds the standalone generator scaffold runtime smoke target to the
release-quality wrapper. The skeleton implementation remains unchanged: it
still returns metadata-only results, writes no files, emits no artifact bodies,
emits no generated policy bodies, and makes no performance or real-data
readiness claim.

## 30. Step298 Remote Run Record Workflow Design Status

Step298 designs the future public-safe remote/manual Release Quality run record
workflow for generator scaffold runtime smoke:
[Frozen policy generation generator scaffold runtime release-quality remote run record workflow](frozen_policy_generation_generator_scaffold_runtime_release_quality_remote_run_record_workflow.md).

The skeleton remains unchanged. The workflow design does not create a status
marker, run a remote workflow, write artifacts, emit artifact bodies, emit
generated policy bodies, compute metrics, or claim real-data readiness.

## 31. Step299 Remote Run Status Marker

Step299 creates the public-safe remote/manual Release Quality status marker for
generator scaffold runtime smoke:
[Learner-state frozen policy generation generator scaffold runtime release-quality remote run status](status/learner_state_frozen_policy_generation_generator_scaffold_runtime_release_quality_remote_run_status.md).

The skeleton remains unchanged: it still returns metadata-only results, writes
no files, emits no artifact bodies, emits no generated policy bodies, and
makes no performance or real-data readiness claim.

## 32. Step300 Artifact Writer Design Status

Step300 designs the future frozen policy generation artifact writer boundary:
[Frozen policy generation artifact writer design](frozen_policy_generation_artifact_writer_design.md).

The skeleton remains unchanged. The writer design consumes only safe generator
scaffold metadata summaries, does not ask for a policy body or artifact body,
does not write files, and keeps manifest output limited to metadata summaries.

## 33. Step301 Artifact Writer Fixture Design Status

Step301 designs future artifact writer fixtures:
[Frozen policy generation artifact writer fixture design](frozen_policy_generation_artifact_writer_fixture_design.md).

The skeleton remains unchanged. The fixture design references generator
scaffold outputs only by safe metadata IDs and does not copy generator scaffold
request bodies, pointer bodies, expected result bodies, generated policy
bodies, artifact bodies, raw rows, logits, or private paths.

## Related Documents

- [Frozen policy generation artifact writer fixture design](frozen_policy_generation_artifact_writer_fixture_design.md)
- [Frozen policy generation artifact writer design](frozen_policy_generation_artifact_writer_design.md)
- [Frozen policy generation generator scaffold runtime release-quality remote run record workflow](frozen_policy_generation_generator_scaffold_runtime_release_quality_remote_run_record_workflow.md)
- [Learner-state frozen policy generation generator scaffold runtime release-quality remote run status](status/learner_state_frozen_policy_generation_generator_scaffold_runtime_release_quality_remote_run_status.md)
- [Frozen policy generation generator scaffold runtime release-quality integration design](frozen_policy_generation_generator_scaffold_runtime_release_quality_integration_design.md)
- [Frozen policy generation generator scaffold CLI Makefile target design](frozen_policy_generation_generator_scaffold_cli_makefile_target_design.md)
- [Frozen policy generation generator scaffold CLI design](frozen_policy_generation_generator_scaffold_cli_design.md)
- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Frozen policy generation artifact policy design](frozen_policy_generation_artifact_policy_design.md)
- [Frozen policy generation generator scaffold fixture design](frozen_policy_generation_generator_scaffold_fixture_design.md)
- [Frozen policy generation generator scaffold fixtures](../tests/fixtures/learner_state_frozen_policy_generation_generator_scaffold/README.md)
- [Frozen policy generation generator scaffold fixture validator design](frozen_policy_generation_generator_scaffold_fixture_validator_design.md)
- [Frozen policy generation generator scaffold fixture validator CLI design](frozen_policy_generation_generator_scaffold_fixture_validator_cli_design.md)
- [Frozen policy generation generator scaffold fixture validator Makefile target design](frozen_policy_generation_generator_scaffold_fixture_validator_makefile_target_design.md)
- [Frozen policy generation generator scaffold fixture validator release-quality integration design](frozen_policy_generation_generator_scaffold_fixture_validator_release_quality_integration_design.md)
- [Frozen policy generation generator scaffold fixture release-quality remote run record workflow](frozen_policy_generation_generator_scaffold_fixture_release_quality_remote_run_record_workflow.md)
- [Learner-state frozen policy generation generator scaffold fixture release-quality remote run status](status/learner_state_frozen_policy_generation_generator_scaffold_fixture_release_quality_remote_run_status.md)
- [Milestone 13 frozen policy generation scaffold runtime recap](milestone_13_frozen_policy_generation_scaffold_runtime_recap.md)
- [Public release checklist](public_release_checklist.md)
