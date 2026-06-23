# Frozen Policy Generation Scaffold Runtime API Design

This document designs the future frozen policy generation scaffold runtime API.

It is documentation only. It does not implement runtime code, generator code,
CLI behavior, Makefile targets, release-quality wrapper changes, workflow
changes, tests, fixtures, calibration, selective prediction, learner-state
estimation, estimator training, metric computation, or model code. It is not a
performance evaluation and not a real-data readiness claim.

Public docs must not include raw GitHub Actions logs, full job output, copied
log blocks, screenshots containing raw logs, generation request bodies, input
pointer bodies, expected scaffold result bodies, generated frozen policy
artifact bodies, frozen policy artifact bodies, JSON bodies, policy bodies, raw
rows, logits/probability dumps, label bodies, split bodies, calibration policy
bodies, private paths, raw learner text, manual output bodies, tmp output
bodies, or real participant data.

## 1. Purpose

The purpose of this document is to design the scaffold runtime API boundary
before implementing any runtime code.

The runtime API should define how a future scaffold loads safe metadata,
builds a metadata-only generation plan, validates that plan, and returns a safe
scaffold result. It is not the actual generator and does not produce or expose
policy artifact bodies.

This design fixes the API contract before the implementation begins.

## 2. Current State

Current infrastructure exists:

- scaffold fixture validation infrastructure
- scaffold fixture root
- scaffold fixture validator API
- scaffold fixture validator CLI
- scaffold fixture validator Makefile target
- release-quality wrapper inclusion for scaffold fixture validation
- remote/manual Release Quality status marker
- Milestone 12 recap

Current scaffold fixture coverage:

- valid cases: 3
- intentional invalid cases: 8
- total cases: 11
- JSON files: 33

Current recorded safe status:

- `total_cases=11`
- `matched_cases=11`
- `mismatched_cases=0`
- `input_error_cases=0`

Still not implemented:

- actual scaffold runtime
- actual generator
- runtime CLI
- runtime Makefile target
- runtime release-quality integration
- model performance evaluation
- real-data readiness

## 3. Runtime Role

The future runtime should:

- load `generation_request.json`
- load `input_fixture_pointer.json`
- validate request metadata
- validate pointer metadata
- confirm validation metadata is present and safe
- reject unsafe requests, unsafe pointers, and unsafe output plans
- avoid calling the generator body at first
- build a metadata-only scaffold plan
- return a metadata-only scaffold result
- keep artifact bodies suppressed
- avoid generating public policy artifact bodies
- guarantee no-oracle, synthetic-only, no raw rows, no logits dump, and no
  private path boundaries around the scaffold API

The runtime is a safety wrapper and planning layer. It is not the policy
generator.

## 4. Proposed Module

Candidate modules:

- `python/learner_state/frozen_policy_generation.py`
- `python/learner_state/frozen_policy_generation_scaffold.py`

Recommended future module:

- `python/learner_state/frozen_policy_generation.py`

Rationale:

- It aligns with the Step248 scaffold implementation design.
- It can hold the generation-facing scaffold API before the generator exists.
- It pairs clearly with
  `python/learner_state/frozen_policy_generation_validation.py`.
- It leaves room for future generator implementation without prematurely
  naming the module as a complete generator.

Alternative:

- `python/learner_state/frozen_policy_generation_scaffold.py` is precise for
  the first runtime scaffold, but it may become narrow once the module grows
  to include future generation-facing helpers.

The recommended initial module remains
`python/learner_state/frozen_policy_generation.py`.

## 5. Proposed Public APIs

Future public API candidates:

- `load_frozen_policy_generation_request(path)`
  - Load safe request metadata from a path.
  - Reject unsafe paths and malformed metadata.
  - Do not return raw request body text.
- `load_frozen_policy_generation_input_pointer(path)`
  - Load safe input pointer metadata from a path.
  - Reject private, real-data, participant-data, or manual-output paths.
  - Do not return raw pointer body text.
- `build_frozen_policy_generation_plan(request, pointer)`
  - Build a metadata-only plan.
  - Record request ID, pointer ID, validation references, policy family,
    output policy, planned checks, and safety summary.
  - Do not create or include a policy artifact body.
- `validate_frozen_policy_generation_plan(plan)`
  - Check the plan against no-oracle, synthetic-only, path, tuning, scoring
    feedback, and body-suppression rules.
  - Return safe reason codes and failed checks.
- `run_frozen_policy_generation_scaffold(request_path, pointer_path)`
  - Load request and pointer metadata, build a plan, validate it, and return a
    safe scaffold result.
  - At first, this should be dry-run metadata-only behavior.
- `summarize_frozen_policy_generation_scaffold_result(result)`
  - Convert the result to safe summary metadata for future CLI or tests.
  - Suppress bodies, raw rows, logits, private paths, and performance claims.

Additional future helpers:

- `scan_generation_request_safety(request)`
- `scan_input_pointer_safety(pointer)`
- `scan_generation_plan_safety(plan)`
- `format_scaffold_result_for_cli(result)`

These APIs are design candidates only. They are not implemented in this step.

## 6. Proposed Dataclasses

Future dataclass candidates:

- `FrozenPolicyGenerationRequest`
  - Safe request metadata only.
  - No raw request body field.
- `FrozenPolicyGenerationInputPointer`
  - Safe input pointer metadata only.
  - No prediction rows, label rows, feature rows, learner text, or artifact
    body.
- `FrozenPolicyGenerationPlan`
  - Metadata-only scaffold plan.
  - No generated policy body.
- `FrozenPolicyGenerationScaffoldResult`
  - Safe result metadata, reason codes, failed checks, and summary flags.
  - No body dumps.
- `FrozenPolicyGenerationScaffoldSafetySummary`
  - Boolean scan and suppression flags.
  - No private path payloads.
- `FrozenPolicyGenerationScaffoldError`
  - Safe reason code and failed-check metadata.
  - No raw exception body if it could include paths or content.

Optional future dataclasses:

- `FrozenPolicyGenerationScaffoldArtifactPolicy`
- `FrozenPolicyGenerationScaffoldValidationReference`
- `FrozenPolicyGenerationScaffoldInputSummary`
- `FrozenPolicyGenerationScaffoldOutputSummary`

All dataclasses should hold safe metadata fields only.

## 7. Request Contract

Allowed safe request metadata:

- `request_id`
- `schema_version`
- `generation_mode`
- `policy_family`
- `calibration_policy_reference`
- `selective_prediction_policy_reference`
- `frozen_policy_validator_reference`
- `output_policy`
- `artifact_policy`
- `synthetic_only`
- `no_oracle_required`
- `allow_artifact_body`
- `allow_logits_dump`
- `allow_raw_rows`
- `allow_private_paths`
- `allow_performance_claims`
- `created_by`
- `notes_safe_summary`

Forbidden request content:

- raw rows
- logits
- learner text
- final text
- `observed_after_text`
- gold labels
- private paths
- generated artifact body
- expected action as scoring feedback

Recommended safety defaults:

- `synthetic_only=true`
- `no_oracle_required=true`
- `allow_artifact_body=false`
- `allow_logits_dump=false`
- `allow_raw_rows=false`
- `allow_private_paths=false`
- `allow_performance_claims=false`

## 8. Input Pointer Contract

Allowed safe pointer metadata:

- `pointer_id`
- `schema_version`
- `input_kind`
- `validation_status`
- `validation_reference`
- `split_policy`
- `train_split_present`
- `validation_split_present`
- `test_split_present`
- `validation_split_used_for_temperature`
- `test_split_used_for_temperature`
- `validation_split_used_for_threshold`
- `test_split_used_for_threshold`
- `source_fixture_label`
- `synthetic_only`
- `no_oracle_checked`
- `content_suppressed`
- `no_raw_rows`

Forbidden pointer content:

- raw prediction rows
- raw labels
- raw features
- raw learner text
- private absolute paths
- logits dump
- artifact body

The pointer should identify safe validation references and split metadata. It
should not carry raw input data.

## 9. Plan Contract

`build_frozen_policy_generation_plan` should create a metadata-only plan. It
should not create an artifact body.

Allowed plan metadata:

- `request_id`
- `pointer_id`
- scaffold status candidate
- generation mode
- policy family
- validation references
- output policy
- planned checks
- planned reason code mapping
- safety summary
- `artifact_body_suppressed`
- `content_suppressed`
- `no_raw_rows`
- `no_logits_dump`
- `no_private_paths`
- `no_performance_claims`
- `no_test_tuning`
- `no_scoring_feedback`

Forbidden plan content:

- generated policy body
- raw input rows
- logits
- private paths
- final text
- gold label
- `observed_after_text`

The plan is a record of what the scaffold would validate and report, not a
policy artifact.

## 10. Scaffold Result Contract

Allowed scaffold result metadata:

- `scaffold_status`
- `reason_codes`
- `failed_checks`
- `request_id`
- `pointer_id`
- `validation_reference_ids`
- `content_suppressed`
- `artifact_body_suppressed`
- `no_raw_rows`
- `no_logits_dump`
- `no_private_paths`
- `no_performance_claims`
- `synthetic_only_checked`
- `no_oracle_checked`
- `test_tuning_checked`
- `scoring_feedback_checked`
- `generated_artifact_written`: false
- `generated_artifact_body_available`: false
- `safe_summary`

Forbidden scaffold result content:

- generated policy body
- raw rows
- logits
- private paths
- learner text
- final text
- gold label
- `observed_after_text`
- performance metrics as claims

The result should be compatible with the `expected_scaffold_result.json`
contract used by the scaffold fixture validator.

## 11. Error Categories

Future error categories should align with Step248 and scaffold fixture
validator reason codes:

- `missing_request`
- `malformed_request`
- `missing_pointer`
- `malformed_pointer`
- `unvalidated_input`
- `missing_validation_split`
- `test_temperature_tuning`
- `test_threshold_tuning`
- `raw_rows_carryover`
- `logits_dump_carryover`
- `generated_artifact_body_leakage`
- `private_path_output`
- `performance_claim_generation`
- `unsafe_path`
- `no_oracle_violation`
- `scoring_feedback_violation`
- `unsupported_generation_mode`
- `artifact_body_not_allowed`
- `output_policy_not_safe`
- `unknown_schema_version`
- `missing_required_field`
- `scaffold_runtime_internal_error`

The runtime should fail closed with safe reason codes. It should not print raw
file contents, raw exceptions, or private paths.

## 12. Relation To Scaffold Fixture Validator

The scaffold fixture validator checks expected scaffold outputs.

The runtime API should produce outputs compatible with
`expected_scaffold_result.json`. The validator remains the test oracle for
scaffold behavior because it already checks expected pass/fail behavior,
reason-code alignment, metadata-only output, forbidden field/value scans,
private path payload absence, and safe summaries.

Future runtime implementation should:

- use the same reason-code vocabulary
- keep valid fixtures passing
- keep invalid fixtures failing with expected reason codes
- avoid duplicating scanner logic where shared helpers can be used safely
- return safe metadata that can be compared with expected scaffold results

The validator does not generate policy. The runtime should not bypass the
validator boundary.

## 13. Relation To Release-Quality

Release-quality currently validates the scaffold fixture contract.

Runtime API implementation should first pass standalone unit tests and fixture
compatibility tests. Runtime CLI, Makefile target, and release-quality
integration are future steps.

Do not add runtime execution to release-quality until:

- standalone runtime tests pass
- fixture compatibility is confirmed
- safe human output is reviewed
- safe JSON output is reviewed
- no body leakage is confirmed
- no private path output is confirmed

Release-quality success for fixture validation is not runtime quality evidence.

## 14. Path Safety

Runtime path safety should:

- reject `real_data` paths
- reject `participant_data` paths
- reject `private_data` paths
- reject `manual_outputs` paths
- reject private absolute paths
- avoid echoing rejected paths
- output only safe labels and reason codes
- avoid writing artifacts by default
- keep any later output writing under controlled synthetic or temporary output
  paths
- suppress artifact bodies even if writing is introduced later

If a path is unsafe, the runtime should report only a safe reason code such as
`unsafe_path` or a more specific category.

## 15. No-Oracle Boundary

Runtime no-oracle rules:

- do not use `observed_after_text`
- do not use final text
- do not use gold label
- do not use expected action as scoring feedback
- do not tune on test split
- use validation split only when explicitly safe and recorded
- allow test split only for later evaluation boundaries, not tuning
- do not select policy behavior from future-derived fields

Any violation should fail closed with safe reason codes.

## 16. Synthetic-Only Boundary

The initial runtime should be valid for synthetic fixtures only.

Rules:

- real-data paths are rejected
- participant-data paths are rejected
- production readiness is not claimed
- no raw learner text is accepted
- no real participant logs are read
- no production data pipeline is created

Any future real-data integration must go through private/institution-approved
review outside this public synthetic-only path.

## 17. Logging / Output Policy

Runtime logging and output should be safe metadata only.

Required output flags:

- `content_suppressed=true`
- `artifact_body_suppressed=true`
- `no_raw_rows=true`
- `no_logits_dump=true`
- `no_private_paths=true`
- `no_performance_claims=true`

Human summaries and JSON summaries must both avoid:

- request body
- pointer body
- expected scaffold result body
- generated artifact body
- frozen policy artifact body
- raw rows
- logits/probability dump
- private paths
- raw learner text
- performance claims

The runtime should summarize counts, statuses, reason codes, and safety flags
only.

## 18. Future Tests

Future implementation tests should cover:

- valid minimal fixed threshold request
- valid fixed abstention rate request
- validation NLL temperature metadata-only request
- missing validation split
- test temperature tuning
- test threshold tuning
- raw rows carryover
- logits dump carryover
- generated artifact body leakage
- private path output
- scoring feedback violation
- malformed request
- malformed pointer
- unsafe path
- summary output no body leak
- JSON output safe
- deterministic result

The tests should compare runtime result metadata with scaffold fixture expected
results without printing fixture bodies.

## 19. Future Implementation Plan

Suggested staged plan:

- Step263: scaffold runtime API implementation
- Step264: scaffold runtime API tests
- Step265: scaffold runtime CLI design
- Step266: scaffold runtime CLI implementation
- Step267: scaffold runtime fixture compatibility tests
- Step268: scaffold runtime Makefile target design
- Step269: scaffold runtime Makefile target implementation
- Step270: scaffold runtime release-quality integration design

The exact numbering can change, but the order should keep standalone runtime
safety ahead of CLI, Makefile, and release-quality integration.

## 20. What This Does NOT Do

This design does not:

- implement runtime code
- implement generator code
- create artifact bodies
- compute metrics
- evaluate performance
- use real data
- change fixtures
- change Python code
- change tests
- change Makefile targets
- change release-quality wrapper behavior
- change GitHub Actions workflows
- claim production readiness

## 21. Beginner-Friendly Explanation

The scaffold runtime API is the future code boundary that will read safe
generation request metadata and safe input pointer metadata, then return a safe
result saying whether a policy generation plan would be allowed.

It differs from the validator because the validator checks fixture expectations
and safety rules. The runtime will be the code path that creates a safe plan
from request and pointer metadata.

It differs from the generator because the runtime API will not create a real
policy artifact body. The generator would be a later component.

The API design comes first so the code has a clear safety contract before it
exists. That reduces the chance that implementation accidentally prints raw
rows, private paths, logits, or policy bodies.

Artifact bodies stay suppressed because this stage is about safe metadata and
contract validation, not publishing policies.

The runtime should align with invalid fixtures and reason codes so unsafe cases
continue to fail for the expected reasons.

Step263 follow-up:

[Frozen policy generation scaffold runtime fixture alignment design](frozen_policy_generation_scaffold_runtime_fixture_alignment_design.md)
checks how the future `FrozenPolicyGenerationScaffoldResult` contract should
align with the existing `expected_scaffold_result.json` fields and scaffold
fixture validator comparison rules before runtime code is implemented.

Step264 implementation status:

The minimal scaffold runtime API skeleton now exists at
`python/learner_state/frozen_policy_generation.py`, with focused tests in
`python/learner_state/tests/test_frozen_policy_generation_scaffold_runtime.py`.
It loads only safe request and pointer metadata, builds a metadata-only plan,
returns a metadata-only scaffold result, keeps artifact body output suppressed,
and maps the current synthetic valid and invalid scaffold fixtures to
deterministic pass/fail reason-code outcomes.

This implementation still does not include generator code, artifact file
writing, runtime CLI behavior, runtime Makefile targets, release-quality
runtime integration, metric computation, real-data handling, or production
readiness claims.

Step265 follow-up:

[Frozen policy generation scaffold runtime fixture compatibility test design](frozen_policy_generation_scaffold_runtime_fixture_compatibility_test_design.md)
defines how future tests should compare runtime skeleton results against the
existing scaffold fixture validator expected-result contract. It remains
docs-only and does not add runtime compatibility tests, CLI behavior, Makefile
targets, generator code, artifact writing, or release-quality runtime
integration.

Step266 implementation status:

The runtime fixture compatibility tests now exist at
`python/learner_state/tests/test_frozen_policy_generation_scaffold_runtime_fixture_compatibility.py`.
They verify that the runtime skeleton's safe summary remains compatible with
the current scaffold fixture expected-result contract for valid 3 and invalid
8 synthetic cases. They do not add runtime CLI behavior, runtime Makefile
targets, generator behavior, artifact writing, release-quality runtime
integration, metric computation, real-data use, or performance claims.

Step267 follow-up:

[Frozen policy generation scaffold runtime CLI design](frozen_policy_generation_scaffold_runtime_cli_design.md)
defines the future terminal boundary for running the runtime scaffold over one
request/pointer pair. It recommends `python -m
learner_state.frozen_policy_generation` as a thin wrapper around the runtime
API, with safe metadata-only human and JSON summaries. It remains docs-only and
does not implement CLI behavior, artifact writing, generator code, Makefile
targets, or release-quality runtime integration.

Step268 implementation status:

The minimal runtime CLI is now implemented in
`python/learner_state/frozen_policy_generation.py`, with tests in
`python/learner_state/tests/test_frozen_policy_generation_scaffold_runtime_cli.py`.
It remains a thin wrapper around the runtime API, returns safe metadata-only
human or JSON summaries, and does not add generator behavior, artifact writing,
runtime Makefile targets, release-quality runtime integration, metric
computation, real-data use, or performance claims.

## 22. Update History

- Step262: initial docs-only scaffold runtime API design.
- Step263: linked the runtime API / scaffold fixture validator alignment
  design.
- Step264: recorded the minimal scaffold runtime API skeleton implementation
  status.
- Step265: linked the docs-only runtime fixture compatibility test design.
- Step266: recorded the runtime fixture compatibility tests implementation
  status.
- Step267: linked the docs-only runtime CLI design.
- Step268: recorded the minimal runtime CLI implementation status.

## Related Documents

- [Milestone 12 frozen policy generation scaffold fixture validation recap](milestone_12_frozen_policy_generation_scaffold_fixture_validation_recap.md)
- [Frozen policy generation scaffold runtime fixture alignment design](frozen_policy_generation_scaffold_runtime_fixture_alignment_design.md)
- [Frozen policy generation scaffold runtime fixture compatibility test design](frozen_policy_generation_scaffold_runtime_fixture_compatibility_test_design.md)
- [Frozen policy generation scaffold runtime CLI design](frozen_policy_generation_scaffold_runtime_cli_design.md)
- [Frozen policy generation scaffold implementation design](frozen_policy_generation_scaffold_implementation_design.md)
- [Frozen policy generation scaffold fixture design](frozen_policy_generation_scaffold_fixture_design.md)
- [Frozen policy generation scaffold fixture validator design](frozen_policy_generation_scaffold_fixture_validator_design.md)
- [Frozen policy generation scaffold fixture validator CLI design](frozen_policy_generation_scaffold_fixture_validator_cli_design.md)
- [Frozen policy generation scaffold fixture validator release-quality integration design](frozen_policy_generation_scaffold_fixture_validator_release_quality_integration_design.md)
- [Frozen policy generation scaffold fixture validator release-quality remote run record workflow](frozen_policy_generation_scaffold_fixture_validator_release_quality_remote_run_record_workflow.md)
- [Learner-state frozen policy generation scaffold fixture release-quality remote run status](status/learner_state_frozen_policy_generation_scaffold_fixture_release_quality_remote_run_status.md)
- [Public release checklist](public_release_checklist.md)
