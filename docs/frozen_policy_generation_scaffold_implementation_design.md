# Frozen Policy Generation Scaffold Implementation Design

This document designs a future frozen policy generation scaffold
implementation.

It is documentation only. It does not implement scaffold code, generator code,
calibration, selective prediction, learner-state estimation, estimator
training, metric computation, CLI behavior, Makefile targets, release-quality
wrapper changes, workflow changes, tests, or fixtures. It is not policy
quality evaluation, not a performance evaluation, and not a real-data
readiness claim.

Public docs must not include raw GitHub Actions logs, full job output, copied
log blocks, screenshots containing raw logs, generation request bodies, input
pointer bodies, generated frozen policy artifact bodies, frozen policy artifact
bodies, JSON bodies, raw rows, logits/probability dumps, label bodies, split
bodies, calibration policy bodies, generated feature/label/manifest bodies,
private paths, raw learner text, or real participant data.

## 1. Purpose

The purpose of this document is to design the safe implementation boundary for
a future frozen policy generation scaffold.

The scaffold is not the actual generator. It is the safety wrapper around
future policy generation. It should accept safe metadata inputs, check that the
inputs are compatible with validation-only tuning rules, and return a safe
metadata summary without exposing policy bodies or row bodies.

This design fixes the safety boundary before any implementation begins.

## 2. Current State

Current infrastructure exists:

- frozen policy generation scaffold design
- frozen policy generation fixture design
- frozen policy generation fixture root
- frozen policy generation validator
- validator CLI
- Makefile target
- release-quality integration
- remote/manual Release Quality status marker
- Milestone 11 recap

Current fixture root:

- `tests/fixtures/learner_state_frozen_policy_generation/`

Current validator command:

- `PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation`

Current Makefile target:

- `make check-learner-state-frozen-policy-generation`

Current release-quality label:

- `release_quality_check: learner-state frozen policy generation validation`

Still not implemented:

- scaffold code
- generator code
- generated policy artifact body publication
- calibration computation
- selective prediction implementation
- learner-state estimator
- metric computation
- real-data handling

## 3. Scaffold Role

The future scaffold should:

- safely accept a generation request
- safely load or receive an input fixture pointer
- check validation split availability
- check selective prediction validation status metadata
- check frozen policy validation status metadata
- inspect temperature policy metadata
- inspect threshold policy metadata
- inspect abstention policy metadata
- inspect output policy metadata
- align with the frozen policy generation validator result contract
- align with the frozen policy validator consistency boundary
- return only safe summary metadata
- avoid returning generated policy bodies
- avoid returning request bodies or input pointer bodies
- avoid returning raw rows
- avoid returning logits/probability dumps
- avoid returning private paths
- avoid returning performance metric bodies

The scaffold should be a safe planning and summary layer. It should not become
a hidden generator that writes public artifacts before the validator boundary
is ready.

## 4. Proposed Module / File Structure

Candidate module names:

- `python/learner_state/frozen_policy_generation.py`
- `python/learner_state/frozen_policy_generator.py`
- `python/learner_state/frozen_policy_generation_scaffold.py`

Recommended future module:

- `python/learner_state/frozen_policy_generation.py`

Rationale:

- It is generation-facing without promising a complete generator too early.
- It pairs cleanly with
  `python/learner_state/frozen_policy_generation_validation.py`.
- It can hold scaffold API first and later expand toward generator behavior in
  controlled steps.
- It leaves room for CLI and API helpers without creating multiple small
  modules before the behavior is stable.

Rejected alternatives:

- `frozen_policy_generator.py` sounds like the actual generator exists.
- `frozen_policy_generation_scaffold.py` is precise but may become awkward if
  the module later owns both scaffold and generator-facing API.

## 5. Proposed Public API

Future public API candidates:

- `load_frozen_policy_generation_request(path)`
  - Load request metadata from a safe path.
  - Return only structured metadata, not raw request body text.
- `load_frozen_policy_generation_input_pointer(path)`
  - Load input pointer metadata from a safe path.
  - Preserve only safe pointer fields and case identifiers.
- `build_frozen_policy_generation_plan(request, pointer)`
  - Build a metadata-only plan describing what the scaffold would do.
  - Do not write artifacts.
  - Do not include policy bodies or row bodies.
- `validate_frozen_policy_generation_plan(plan)`
  - Check the plan against no-oracle, synthetic-only, path, tuning, and body
    suppression rules.
- `run_frozen_policy_generation_scaffold(request_path, pointer_path)`
  - Load metadata, build a plan, validate the plan, and return a safe scaffold
    result.
  - This should be dry-run style at first.
- `summarize_frozen_policy_generation_scaffold_result(result)`
  - Convert the result to safe human or JSON-compatible metadata.
  - Suppress request bodies, generated artifact bodies, raw rows, logits, and
    private paths.

These functions are design candidates only. They are not implemented in this
step.

## 6. Proposed Dataclasses

Future dataclass candidates:

- `FrozenPolicyGenerationRequest`
  - Safe request metadata only.
  - No raw request body field.
- `FrozenPolicyGenerationInputPointer`
  - Safe relative pointer metadata only.
  - No copied prediction, label, split, or calibration policy body.
- `FrozenPolicyGenerationPlan`
  - Metadata-only plan describing validation source, temperature policy,
    threshold policy, abstention policy, and output policy status.
  - No generated artifact body.
- `FrozenPolicyGenerationScaffoldResult`
  - Safe result metadata, reason codes, failed checks, and safety flags.
  - No body dumps.
- `FrozenPolicyGenerationScaffoldSafetySummary`
  - Boolean safety flags and scan status.
  - No private paths.
- `FrozenPolicyGenerationScaffoldError`
  - Safe failure category and reason code.
  - No raw exception text if it could contain paths or body content.

Dataclasses should hold safe metadata fields only. They should not carry row
bodies, label bodies, split bodies, calibration policy bodies, generated
policy bodies, private absolute paths, or raw learner text.

## 7. Input Contract

Future scaffold inputs should include safe metadata for:

- request schema version
- pointer schema version
- input validation status
- validation split availability
- selective prediction validation status
- frozen policy validation status
- temperature policy metadata
- threshold policy metadata
- abstention policy metadata
- output policy metadata
- synthetic-only marker
- no-oracle marker
- no body dump marker
- no raw rows marker
- no logits dump marker

Required safety expectations:

- input paths are synthetic fixture paths or explicit safe temporary paths
- validation split is available before tuning metadata is accepted
- test split is not used for temperature or threshold tuning
- expected action is not used as scoring feedback
- request and pointer bodies are not returned by public output
- generated artifact bodies are not returned by public output

## 8. Output Contract

Future scaffold output should be safe metadata only:

- `scaffold_schema_version`
- `scaffold_status`
- `generation_request_schema_version`
- `pointer_schema_version`
- `input_validation_status`
- `selective_prediction_validation_status`
- `frozen_policy_validation_status`
- `validation_split_available`
- `temperature_policy_status`
- `threshold_policy_status`
- `abstention_policy_status`
- `output_policy_status`
- `safety_status`
- `reason_codes`
- `failed_checks`
- `content_suppressed`
- `no_raw_rows`
- `no_logits_dump`
- `no_request_body`
- `no_generated_artifact_body`
- `synthetic_only_checked`
- `no_oracle_checked`
- `test_tuning_checked`
- `private_path_scan_checked`
- `performance_claim_scan_checked`
- `would_write_artifact`
- `artifact_body_suppressed`

Output must not include:

- generation request body
- input pointer body
- generated frozen policy artifact body
- frozen policy artifact body
- raw rows
- logits or probability dumps
- label body
- split body
- calibration policy body
- private paths
- raw learner text
- performance metric body

## 9. Error / Failure Categories

Future reason codes:

- `missing_request`
  - Request file or request metadata is absent.
- `malformed_request`
  - Request metadata cannot be parsed safely.
- `missing_pointer`
  - Input pointer file or metadata is absent.
- `malformed_pointer`
  - Input pointer metadata cannot be parsed safely.
- `unvalidated_input`
  - Input validation has not run or is not recorded.
- `missing_validation_split`
  - Validation split metadata is absent.
- `selective_prediction_validator_failure`
  - Input contract validation failed.
- `frozen_policy_validator_failure`
  - Frozen policy validation consistency is expected to fail.
- `test_temperature_tuning`
  - Temperature policy uses test data.
- `test_threshold_tuning`
  - Threshold or abstention policy uses test data.
- `raw_rows_carryover`
  - Raw rows appear in request, plan, output policy, or generated metadata.
- `logits_dump_carryover`
  - Logits or probability dumps appear in public metadata.
- `generated_artifact_body_leakage`
  - Generated policy body is requested or included in public output.
- `private_path_output`
  - Output metadata exposes a private path.
- `performance_claim_generation`
  - Request or output claims performance evidence.
- `unsafe_path`
  - Path policy rejects the input or output location.
- `unknown_schema_version`
  - Request or pointer schema version is unsupported.
- `body_dump_requested`
  - Caller requests request body, pointer body, raw rows, or artifact body.
- `real_data_path`
  - Path appears to reference real-data storage.
- `participant_data_path`
  - Path appears to reference participant-data storage.
- `manual_output_path`
  - Automated scaffold path points to `manual_outputs/`.
- `no_oracle_violation`
  - Metadata uses after-observed or oracle-only content.
- `scoring_feedback_violation`
  - Expected action or label content is used as scoring feedback.

Failure output should include only safe reason codes and check names.

## 10. No-Oracle Boundary

The scaffold must not use:

- `observed_after_text`
- `final_text`
- `gold_label`
- future annotations
- expected action as scoring feedback
- test split for temperature tuning
- test split for threshold tuning

The validation split may be referenced only as safe provenance metadata. The
scaffold must not print validation rows, labels, logits, request bodies, or
generated policy bodies.

## 11. Synthetic-Only Boundary

The scaffold should default to synthetic fixture inputs only.

It must reject or fail closed on:

- `real_data`
- `participant_data`
- `private_data`
- `manual_outputs`
- private absolute paths
- raw learner text
- production data paths
- real participant logs

Public summaries should use safe case ids, counts, booleans, and reason codes
instead of private path strings.

## 12. Relation To Validator

The scaffold result should correspond to the expected generation result shape
validated by the frozen policy generation validator.

Relationship:

- scaffold builds a safe metadata plan or summary
- generation validator checks request, pointer, expected result, and safety
  metadata
- scaffold does not replace the validator
- validator remains the independent fail-closed safety check

Future flow:

1. request + pointer
2. scaffold
3. safe generation summary
4. generation validator
5. Makefile / release-quality target

Actual artifact bodies remain a private/local future stage unless a later
synthetic fixture step explicitly designs safe expected artifacts.

## 13. Relation To Frozen Policy Validator

The scaffold must not publicly expose generated policy bodies.

The frozen policy validator relationship should be metadata-consistency first:

- generated policy body is not printed in public output
- frozen policy validation status is recorded as safe metadata
- frozen policy validation consistency failure is a scaffold failure
- no raw frozen policy body is pasted into docs

Later implementation may pass a private/local generated artifact to the frozen
policy validator, but public docs and summaries should remain metadata-only.

## 14. CLI Future

Future CLI candidate:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation --request <generation_request.json> --input-pointer <input_fixture_pointer.json>
```

Future options:

- `--json`
- `--dry-run`
- `--fixture-case`
- `--fixture-root`

Initial CLI behavior should be dry-run oriented:

- default to safe summary only
- do not write generated artifacts
- do not print request bodies
- do not print input pointer bodies
- do not print generated artifact bodies
- reject unsafe paths
- return parseable safe JSON in JSON mode

This step does not implement the CLI.

## 15. Fixture Future

Future fixture options:

- reuse existing generation fixtures
- add scaffold-specific valid/invalid fixtures
- add expected scaffold result files
- keep existing generation fixtures unchanged and create a separate scaffold
  fixture design step

Recommended next fixture policy:

- keep existing generation fixtures unchanged
- design scaffold-specific fixtures in a separate step before implementation
- avoid adding generated artifact bodies to fixtures unless a later synthetic
  fixture design explicitly approves a safe body format

This keeps Step236 generation validator fixtures stable while the scaffold
contract is refined.

## 16. Testing Plan

Future tests should cover:

- valid request and pointer produce a passing safe summary
- missing validation split fails
- test-derived temperature fails
- test-derived threshold fails
- raw row carryover fails
- logits dump carryover fails
- generated artifact body leakage fails
- private path output fails
- performance claim fails
- no request body appears in output
- no input pointer body appears in output
- no generated artifact body appears in output
- no raw rows, logits, or private paths appear in stdout
- JSON output is parseable and safe
- result is deterministic
- validator can consume the scaffold summary

No tests are implemented in this step.

## 17. Release-Quality Future

The scaffold implementation should not be added directly to release-quality at
first.

Recommended staging:

1. scaffold fixture design
2. scaffold API implementation or API implementation design
3. scaffold CLI design
4. scaffold CLI implementation
5. scaffold Makefile target design
6. standalone log-safety review
7. release-quality integration design
8. release-quality wrapper integration
9. remote/manual run record workflow and status marker

The current generation validation infrastructure should act as the safety net
around future scaffold work.

## 18. What This Does Not Do

This design does not:

- implement scaffold code
- implement generator code
- create policy artifact bodies
- compute metrics
- fit calibration
- run selective prediction
- train an estimator
- use real data
- prove performance
- change Makefile
- change release-quality wrapper
- change GitHub Actions workflow
- change Python code
- change tests
- change fixtures

## 19. Beginner-Friendly Explanation

A scaffold is a safe outer frame around a future feature. Here, it would check
whether a frozen policy generation request is safe before any real generator
logic is trusted.

The generator would eventually construct a candidate frozen policy. The
scaffold decides whether the request, pointer, provenance, and output policy
are safe enough to proceed.

Policy bodies are not printed because bodies can accidentally carry rows,
labels, private paths, or tuning evidence. Public outputs should show only
counts, booleans, statuses, and reason codes.

The validator came first because a future scaffold needs a stable contract to
target. Invalid fixtures are useful because they prove unsafe requests fail
closed.

Release-quality should not run new scaffold code immediately. First the
scaffold should pass standalone tests and log-safety review.

## 20. Next Recommended Steps

Next candidate steps:

- scaffold fixture design
- scaffold API implementation design
- scaffold API implementation
- scaffold CLI design
- scaffold CLI implementation
- scaffold Makefile target design
- scaffold release-quality design
- actual generator implementation design
- actual generator implementation

Recommended next step:

- scaffold fixture design if the team wants another docs-only safety pass
- scaffold API implementation design if the current fixture contract is stable
  enough to start coding

The safer next step is scaffold fixture design, because it fixes expected
input and output metadata before any scaffold code is added.

Step249 defines that next fixture contract in the
[frozen policy generation scaffold fixture design](frozen_policy_generation_scaffold_fixture_design.md).

Step250 creates the initial synthetic-only scaffold fixture files under
`tests/fixtures/learner_state_frozen_policy_generation_scaffold/` without
adding scaffold code, generator code, CLI, Makefile targets, release-quality
integration, workflow changes, or Python tests.

Step251 defines the future scaffold fixture validator design. It keeps
validator implementation separate from scaffold runtime code and focuses on
fixture safety, metadata-only contracts, and expected reason-code alignment.

Step252 implements the minimal scaffold fixture validator module and tests.
The scaffold runtime and generator remain unimplemented.

Step253 designs the future CLI for running that validator. The CLI design is
still fixture-only and does not add scaffold runtime or generator behavior.

Step254 implements the minimal scaffold fixture validator CLI. The CLI remains
fixture-only and does not introduce scaffold runtime or generator behavior.

Step255 designs the future Makefile target for running the scaffold fixture
validator CLI. It keeps Makefile implementation and release-quality integration
out of scope while defining the proposed target name, command, help text, safe
logging policy, and staging plan.

Step256 implements that standalone Makefile target. It remains fixture-only and
does not add release-quality integration, workflow changes, scaffold runtime
code, or generator code.

Step257 designs the future release-quality wrapper integration for that target.
It remains fixture-only and does not implement wrapper changes, workflow
changes, scaffold runtime code, or generator code.

Step258 implements the release-quality wrapper integration for the standalone
scaffold fixture validator target. It remains fixture-only and does not add
workflow changes, scaffold runtime code, or generator code.

Step262 adds
[Frozen policy generation scaffold runtime API design](frozen_policy_generation_scaffold_runtime_api_design.md).
It refines this implementation-boundary design into a proposed runtime module,
public API, dataclass, request/pointer/plan/result contract, error category,
and safety policy before any runtime or generator code is implemented.

## 21. Update History

- Step248: initial frozen policy generation scaffold implementation design.
- Step249: linked the frozen policy generation scaffold fixture design as the
  next docs-only fixture contract before scaffold code.
- Step250: linked the initial scaffold fixture root implementation; scaffold
  code remains unimplemented.
- Step251: linked the scaffold fixture validator design as the next safety
  layer before scaffold runtime code.
- Step252: linked the minimal scaffold fixture validator implementation.
- Step253: linked the scaffold fixture validator CLI design.
- Step254: linked the scaffold fixture validator CLI implementation.
- Step255: linked the scaffold fixture validator Makefile target design.
- Step256: linked the scaffold fixture validator Makefile target
  implementation status.
- Step257: linked the scaffold fixture validator release-quality integration
  design.
- Step258: linked the scaffold fixture validator release-quality wrapper
  integration implementation status.
- Step262: linked the scaffold runtime API design as the next docs-only API
  boundary before runtime implementation.

## Related Documents

- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Frozen policy generation scaffold runtime API design](frozen_policy_generation_scaffold_runtime_api_design.md)
- [Frozen policy generation scaffold fixture design](frozen_policy_generation_scaffold_fixture_design.md)
- [Frozen policy generation scaffold fixtures](../tests/fixtures/learner_state_frozen_policy_generation_scaffold/README.md)
- [Frozen policy generation scaffold fixture validator design](frozen_policy_generation_scaffold_fixture_validator_design.md)
- [Frozen policy generation scaffold fixture validator CLI design](frozen_policy_generation_scaffold_fixture_validator_cli_design.md)
- [Frozen policy generation scaffold fixture validator Makefile target design](frozen_policy_generation_scaffold_fixture_validator_makefile_target_design.md)
- [Frozen policy generation scaffold fixture validator release-quality integration design](frozen_policy_generation_scaffold_fixture_validator_release_quality_integration_design.md)
- [Frozen policy generation fixture design](frozen_policy_generation_fixture_design.md)
- [Frozen policy generation validation design](frozen_policy_generation_validation_design.md)
- [Frozen policy generation validator CLI design](frozen_policy_generation_validator_cli_design.md)
- [Frozen policy generation validator Makefile target design](frozen_policy_generation_validator_makefile_target_design.md)
- [Frozen policy generation release-quality integration design](frozen_policy_generation_release_quality_integration_design.md)
- [Frozen policy generation release-quality remote run record workflow](frozen_policy_generation_release_quality_remote_run_record_workflow.md)
- [Learner-state frozen policy generation release-quality remote run status](status/learner_state_frozen_policy_generation_release_quality_remote_run_status.md)
- [Milestone 11 frozen policy generation validation infrastructure recap](milestone_11_frozen_policy_generation_validation_infrastructure_recap.md)
- [Frozen selective prediction policy validation design](frozen_selective_prediction_policy_validation_design.md)
- [Frozen policy validator CLI design](frozen_policy_validator_cli_design.md)
- [Public release checklist](public_release_checklist.md)
