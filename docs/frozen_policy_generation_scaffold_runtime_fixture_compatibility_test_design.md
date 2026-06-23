# Frozen Policy Generation Scaffold Runtime Fixture Compatibility Test Design

## 1. Purpose

This document designs future compatibility tests between the minimal scaffold
runtime API skeleton and the existing scaffold fixture validator contract.

This is a docs-only test design. It does not implement tests, change fixtures,
design a CLI, implement generator behavior, evaluate performance, or claim
real-data readiness.

The goal is to make the future test boundary explicit before adding runtime
fixture compatibility tests.

## 2. Current State

Current scaffold validation and runtime state:

- scaffold fixture validator exists
- scaffold fixture validator CLI exists
- scaffold fixture Makefile target exists
- release-quality includes scaffold fixture validator
- minimal runtime API skeleton exists
- runtime CLI does not exist
- runtime Makefile target does not exist
- runtime compatibility tests do not yet exist
- generator does not exist
- artifact file writing does not exist
- artifact body generation does not exist

Current runtime module:

- `python/learner_state/frozen_policy_generation.py`

Current runtime APIs:

- `load_frozen_policy_generation_request(path)`
- `load_frozen_policy_generation_input_pointer(path)`
- `build_frozen_policy_generation_plan(request, pointer)`
- `validate_frozen_policy_generation_plan(plan)`
- `run_frozen_policy_generation_scaffold(request_path, pointer_path)`
- `summarize_frozen_policy_generation_scaffold_result(result)`

Current scaffold fixture root:

- `tests/fixtures/learner_state_frozen_policy_generation_scaffold`

Current fixture shape:

- valid cases: 3
- invalid cases: 8
- total cases: 11
- JSON files: 33
- per-case files: `generation_request.json`, `input_fixture_pointer.json`,
  `expected_scaffold_result.json`

## 3. Compatibility Test Purpose

Compatibility tests should confirm that runtime output stays compatible with
the fixture validator's expected-result contract.

They should check:

- runtime result can be compared with `expected_scaffold_result.json`
- valid 3 cases match expected pass outcomes
- invalid 8 cases match expected fail outcomes and reason codes
- summary output is body-free
- reason-code ordering is deterministic
- failed-check ordering is deterministic
- safety flags align with expected-result metadata
- generated artifact flags remain suppressed

This is contract and safety evidence only. It is not generator quality or model
performance evidence.

## 4. Proposed Test File

Recommended future test file:

- `python/learner_state/tests/test_frozen_policy_generation_scaffold_runtime_fixture_compatibility.py`

This file should stay separate from the basic runtime skeleton tests. The
runtime skeleton tests can cover direct runtime behavior, while compatibility
tests can focus on comparing runtime output to fixture validator expectations.

## 5. Proposed Helper Strategy

Two helper strategies are possible.

Strategy A:

- run the runtime API for a case
- convert the runtime result into a safe summary dict
- load `expected_scaffold_result.json` through the scaffold fixture validator
- compare runtime summary to expected metadata through the existing validator
  comparison helper

Strategy B:

- run the runtime API for a case
- read expected metadata directly in the runtime test
- compare fields with dedicated runtime-test comparison code

Recommended strategy: Strategy A.

Reasons:

- avoids duplicate comparison logic
- keeps the scaffold fixture validator as the test oracle
- keeps the contract centralized
- makes future field changes easier to review
- reduces the chance that runtime tests silently drift from fixture validator
  behavior

The future implementation may need a small adapter if the runtime summary is a
plain dict while the existing comparison helper expects a validator result
object. That adapter should expose only safe metadata fields.

## 6. Proposed Test Flow

Each fixture case should follow this flow:

1. Discover scaffold fixture cases deterministically.
2. Build the request path for the case.
3. Build the input pointer path for the case.
4. Run `run_frozen_policy_generation_scaffold(request_path, pointer_path)`.
5. Convert the result with
   `summarize_frozen_policy_generation_scaffold_result(result)`.
6. Load expected metadata with `load_expected_scaffold_result(case_dir)`.
7. Compare the safe runtime summary to expected metadata through the scaffold
   fixture validator comparison helper or a thin safe adapter.
8. Assert there are no mismatches.
9. Assert no body-leakage keys or values appear in the summary.
10. Assert reason codes and failed checks are deterministic.
11. Assert all safety flags are explicit booleans.

The test should print no request body, pointer body, expected result body, raw
rows, logits, artifact bodies, private paths, or raw learner text.

## 7. Valid Case Expectations

Valid fixtures should match expected pass outcomes:

- `valid/minimal_fixed_threshold_dry_run` -> `pass`
- `valid/minimal_fixed_abstention_rate_dry_run` -> `pass`
- `valid/validation_nll_temperature_metadata_only_dry_run` -> `pass`

Expected valid-case properties:

- no reason code
- no failed check
- body content suppressed
- artifact body suppressed
- no artifact written
- generated artifact body unavailable
- no raw rows
- no logits dump
- no private paths
- no performance claims
- synthetic-only boundary checked
- no-oracle boundary checked

## 8. Invalid Case Expectations

Invalid fixtures should match expected fail outcomes and expected reason codes:

- `invalid/missing_validation_split` -> `fail`, `missing_validation_split`
- `invalid/test_temperature_tuning` -> `fail`, `test_temperature_tuning`
- `invalid/test_threshold_tuning` -> `fail`, `test_threshold_tuning`
- `invalid/raw_rows_carryover` -> `fail`, `raw_rows_carryover`
- `invalid/logits_dump_carryover` -> `fail`, `logits_dump_carryover`
- `invalid/generated_artifact_body_leakage` -> `fail`,
  `generated_artifact_body_leakage`
- `invalid/private_path_output` -> `fail`, `private_path_output`
- `invalid/scoring_feedback_violation` -> `fail`,
  `scoring_feedback_violation`

Expected invalid-case properties:

- body content suppressed
- artifact body suppressed
- no artifact written
- generated artifact body unavailable
- no raw rows copied
- no logits dump copied
- no private path echo
- safe reason code only

## 9. Malformed / Missing Input Tests

Future tests should include temporary synthetic inputs for input-error
boundaries:

- malformed request fixture -> `input_error`, `malformed_request`
- malformed pointer fixture -> `input_error`, `malformed_pointer`
- missing request path -> `input_error`, `missing_request`
- missing pointer path -> `input_error`, `missing_pointer`
- unsafe path -> safe deterministic reason code according to the runtime API
  boundary

These tests should assert no panic and no path echo. Temporary fixtures should
be minimal and synthetic-only.

## 10. No Body Leakage Tests

Future tests should scan summary keys and safe string values for forbidden
payload surfaces:

- request body
- pointer body
- expected scaffold result body
- artifact body
- raw rows
- logits
- private paths
- raw learner text
- final text
- observed-after text
- gold label
- performance claims

Intentional invalid case labels and reason codes are allowed. Payload bodies
are not allowed.

## 11. Deterministic Behavior Tests

Future tests should verify deterministic behavior:

- same fixture run twice returns the same safe summary
- `reason_codes` ordering is stable
- `failed_checks` ordering is stable
- summary keys are stable
- JSON serialization is stable enough for tests
- fixture discovery order is deterministic

The tests should not compare raw JSON body text.

## 12. Safety Flag Tests

Future tests should assert explicit boolean values for:

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
- `generated_artifact_written`
- `generated_artifact_body_available`

Initial runtime compatibility expectations:

- `generated_artifact_written=false`
- `generated_artifact_body_available=false`
- `artifact_body_suppressed=true`
- `content_suppressed=true`

## 13. Release-Quality Implications

Compatibility tests should be standalone first.

They should not be added to release-quality immediately. A safer order is:

1. implement runtime compatibility tests
2. run them locally
3. add a standalone Makefile target in a later step
4. review stdout and JSON safety
5. consider release-quality integration only after standalone target stability

Even after future release-quality integration, success would mean runtime /
fixture compatibility and safe-output behavior. It would not mean generator
quality, calibration quality, model performance, or real-data readiness.

## 14. No-Oracle / Synthetic-Only Boundary

Compatibility tests must stay within the synthetic scaffold fixture root.

They must not use:

- real participant data
- raw learner text
- final text
- observed-after text
- gold labels
- expected action as scoring feedback
- test-derived tuning
- private data paths

Invalid fixtures are safety tests only. They are successful when they fail for
their expected reason code.

## 15. Implementation Constraints For Future

Future implementation should:

- not modify fixtures
- not duplicate validator comparison logic if a safe adapter can use it
- not expose private paths in assertion messages
- use safe case labels
- keep malformed temp fixtures synthetic and body-minimal
- avoid artifact writing
- avoid generator invocation
- avoid runtime CLI implementation in the compatibility-test step
- avoid Makefile changes in the compatibility-test implementation step unless
  a later step explicitly requests them
- avoid release-quality changes until a standalone target exists and is safe

## 16. What This Does NOT Do

This design does not:

- implement tests
- change runtime code
- change fixtures
- implement runtime CLI
- add Makefile targets
- change release-quality wrapper behavior
- change GitHub Actions workflows
- implement generator code
- write artifact files
- generate artifact bodies
- compute metrics
- use real data
- claim performance

## 17. Beginner-Friendly Explanation

A compatibility test checks whether two pieces of the system agree on the same
contract. Here, it checks whether the runtime result matches what the existing
scaffold fixture says should happen.

The expected scaffold result is the fixture's safe metadata answer key. The
runtime result is what the runtime skeleton returns. If they match, the runtime
is aligned with the fixture contract.

Using the validator as the test oracle means the future runtime tests reuse the
same comparison rules already used for fixture validation.

Both valid and invalid fixtures matter. Valid fixtures prove safe cases still
pass. Invalid fixtures prove unsafe cases still fail closed for the expected
reason.

Body-leakage tests matter because a result can be structurally correct while
still accidentally exposing request bodies, rows, logits, private paths, or
artifact bodies. That would violate the safety contract.

The tests should not enter release-quality immediately because a standalone
local compatibility check needs to settle first.

## 18. Next Recommended Steps

Recommended next step:

- runtime fixture compatibility tests implementation

Then proceed in this order:

- runtime CLI design
- runtime CLI implementation
- runtime Makefile target design
- runtime Makefile target implementation
- runtime release-quality integration design

Generator design and implementation should remain separate and later than the
runtime compatibility boundary.

## 19. Update History

- Step265: initial docs-only scaffold runtime fixture compatibility test
  design.

## Related Documents

- [Frozen policy generation scaffold runtime API design](frozen_policy_generation_scaffold_runtime_api_design.md)
- [Frozen policy generation scaffold runtime fixture alignment design](frozen_policy_generation_scaffold_runtime_fixture_alignment_design.md)
- [Milestone 12 frozen policy generation scaffold fixture validation recap](milestone_12_frozen_policy_generation_scaffold_fixture_validation_recap.md)
- [Frozen policy generation scaffold fixture validator design](frozen_policy_generation_scaffold_fixture_validator_design.md)
- [Frozen policy generation scaffold fixture design](frozen_policy_generation_scaffold_fixture_design.md)
- [Frozen policy generation scaffold fixtures](../tests/fixtures/learner_state_frozen_policy_generation_scaffold/README.md)
- `python/learner_state/frozen_policy_generation.py`
- `python/learner_state/tests/test_frozen_policy_generation_scaffold_runtime.py`
- `python/learner_state/frozen_policy_generation_scaffold_fixture_validation.py`
- [Public release checklist](public_release_checklist.md)
