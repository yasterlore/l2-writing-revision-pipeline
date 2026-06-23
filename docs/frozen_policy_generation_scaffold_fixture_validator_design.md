# Frozen Policy Generation Scaffold Fixture Validator Design

## 1. Purpose

This document designs a future validator for the frozen policy generation
scaffold fixture root.

It is a docs-only design. It does not implement validator code, scaffold
runtime code, generator code, CLI behavior, Makefile targets, release-quality
integration, metric computation, performance evaluation, or real-data
readiness.

The validator's job will be to confirm that scaffold fixtures are
metadata-only, synthetic-only, no-oracle safe, and aligned with the expected
pass/fail reason-code contract.

## 2. Current State

Current scaffold fixture assets:

- fixture root:
  `tests/fixtures/learner_state_frozen_policy_generation_scaffold/`
- valid cases: 3
- invalid cases: 8
- total cases: 11
- root README: present
- JSON files: 33
- required files per case:
  - `generation_request.json`
  - `input_fixture_pointer.json`
  - `expected_scaffold_result.json`

The current JSON files parse, and the current fixture root is metadata-only.

The following do not exist yet:

- scaffold fixture validator code
- scaffold runtime code
- generator code
- scaffold fixture CLI
- scaffold fixture Makefile target
- scaffold fixture release-quality integration

## 3. Proposed Validator Module

Candidate modules:

- `python/learner_state/frozen_policy_generation_scaffold_fixture_validation.py`
- `python/learner_state/frozen_policy_generation_scaffold_validation.py`
- `python/learner_state/frozen_policy_generation_scaffold.py`

Recommended initial module:

- `python/learner_state/frozen_policy_generation_scaffold_fixture_validation.py`

Rationale:

- it scopes the code to fixture contract validation
- it avoids mixing fixture validation with future scaffold runtime behavior
- it makes the validator intent explicit
- it leaves room for a later runtime module such as
  `python/learner_state/frozen_policy_generation.py`

`frozen_policy_generation_scaffold_validation.py` is shorter, but it could be
mistaken for runtime validation of scaffold outputs. `frozen_policy_generation_scaffold.py`
should be reserved for the future scaffold runtime or facade.

## 4. Proposed Public API

Future public API candidates:

- `discover_frozen_policy_generation_scaffold_fixture_cases(root)`
  - deterministically finds valid and invalid fixture case directories
- `load_scaffold_fixture_case(case_dir)`
  - loads the three expected metadata files for one case
- `validate_scaffold_fixture_case(case_dir)`
  - validates one case and returns a safe validation result
- `load_expected_scaffold_result(case_dir)`
  - loads the expected metadata-only result for expected-result matching
- `compare_scaffold_result_to_expected(result, expected)`
  - compares status, reason codes, failed checks, and safety flags
- `validate_scaffold_fixture_root(root)`
  - validates every discovered case and returns a root summary
- `summarize_scaffold_fixture_validation_result(result)`
  - converts a result into safe human or JSON metadata

The API should never return request body, pointer body, generated artifact
body, raw rows, logits, labels, split bodies, private paths, or metric bodies.

## 5. Proposed Dataclasses

Future dataclass candidates:

- `FrozenPolicyGenerationScaffoldFixtureCase`
  - safe case path label, case category, case name, schema versions, and loaded
    metadata status flags
- `FrozenPolicyGenerationScaffoldFixtureValidationResult`
  - validation status, reason codes, failure categories, failed checks, safety
    flags, and checked file count
- `ExpectedScaffoldResult`
  - expected scaffold status, reason codes, failed checks, safety flags, and
    dry-run artifact metadata
- `ScaffoldFixtureValidationMismatch`
  - safe mismatch field names and expected/actual scalar summaries only
- `ScaffoldFixtureSafetyScanResult`
  - booleans for forbidden field scan, private path scan, raw row scan, logits
    scan, artifact body scan, and performance claim scan
- `ScaffoldFixtureRootValidationSummary`
  - mode, total cases, matched cases, mismatched cases, input error cases, and
    reason-code counts

All dataclasses should contain safe metadata only. Body fields should be
excluded by design.

## 6. Root-Level Checks

Recommended root-level checks:

- root exists
- root README exists
- `valid/` and `invalid/` directories exist
- fixture discovery is deterministic
- expected case count is 11 for the initial root
- expected JSON file count is 33 for the initial root
- no unexpected file extensions are present
- every JSON file parses
- every case has exactly the three required files
- no absolute or private paths are present
- no raw rows, logits, probabilities, generated artifact bodies, or policy
  bodies are present
- future invalid cases may be absent if the README documents them as future
  cases

The root validator should fail closed for missing or malformed required files
without printing file bodies.

## 7. Case-Level Checks

Recommended case-level checks:

- required files exist
- schema version fields exist
- valid/invalid path category matches expected scaffold status
- `generation_request.json` contains safe metadata only
- `input_fixture_pointer.json` contains safe metadata only
- `expected_scaffold_result.json` contains safe metadata only
- valid cases expect `scaffold_status=pass`
- invalid cases expect `scaffold_status=fail`
- valid cases have empty reason codes
- invalid case reason code aligns with the case name
- `failed_checks` align with `reason_codes`
- safety flags are true:
  - `content_suppressed`
  - `no_raw_rows`
  - `no_logits_dump`
  - `no_request_body`
  - `no_generated_artifact_body`
  - `artifact_body_suppressed`
  - `synthetic_only_checked`
  - `no_oracle_checked`
  - `test_tuning_checked`
  - `private_path_scan_checked`
  - `performance_claim_scan_checked`
  - `metadata_only`

The validator should report safe reason codes and field names only.

## 8. Forbidden Field / Value Scans

The recursive scan should inspect:

- key names
- string values
- nested objects
- lists

Forbidden payloads and values:

- raw rows
- logits dumps
- probabilities
- raw learner text
- final text
- observed-after text
- gold labels
- label bodies
- split bodies
- generated artifact bodies
- policy bodies
- private absolute paths
- `real_data` paths
- `participant_data` paths
- `manual_outputs` paths
- performance metric bodies
- GitHub raw log markers

Intentional invalid fixture labels and reason codes are allowed when they are
only markers. The validator should distinguish markers from payloads:

- allowed: an invalid case named for a safety failure
- allowed: a reason code naming a safety failure
- forbidden: embedded row, logit, private path, artifact body, policy body, or
  metric payload

The validation result should expose only the safe reason code, not the matched
payload text.

## 9. Expected Reason-Code Mapping

Current invalid case mapping:

- `missing_validation_split` -> `missing_validation_split`
- `test_temperature_tuning` -> `test_temperature_tuning`
- `test_threshold_tuning` -> `test_threshold_tuning`
- `raw_rows_carryover` -> `raw_rows_carryover`
- `logits_dump_carryover` -> `logits_dump_carryover`
- `generated_artifact_body_leakage` -> `generated_artifact_body_leakage`
- `private_path_output` -> `private_path_output`
- `scoring_feedback_violation` -> `scoring_feedback_violation`

Future invalid cases should be added to a mapping table before fixture files
are added. Unknown invalid case names should fail safely as
`unknown_invalid_fixture_case` or `expected_result_mismatch`.

## 10. Expected Pass/Fail Behavior

Expected behavior:

- valid cases validate as pass
- invalid cases validate as fail with the expected reason code
- intentional invalid cases are successful fixture tests when the failure
  matches the expected reason
- fixture root validation passes only when all expected results match the
  fixture design
- malformed fixture files return `input_error` or a safe parse failure reason
  without panicking

This is fixture contract validation, not scaffold runtime quality validation.

## 11. Safe Output / Summary Policy

Human summary fields:

- mode
- total cases
- matched cases
- mismatched cases
- input error cases
- reason-code counts
- content suppressed flag
- no raw rows flag
- synthetic-only checked flag
- no-oracle checked flag
- private path scan checked flag
- performance claim scan checked flag

JSON summary should be parseable and metadata-only. It must not include:

- file bodies
- raw JSON body dumps
- request bodies
- input pointer bodies
- generated artifact bodies
- raw rows
- logits or probabilities
- private paths
- metric bodies

## 12. Relation To Scaffold Implementation

The scaffold fixture validator should be implemented before scaffold runtime
code. It gives the runtime a stable fixture contract and makes unsafe fixture
shape changes visible before the runtime depends on them.

The future scaffold runtime can later be tested against these fixtures by
comparing a safe scaffold result to `expected_scaffold_result.json`.

The validator does not generate policies, compute thresholds, fit calibration,
or compute metrics.

## 13. Relation To Existing Generation Validator

The existing frozen policy generation validator checks:

- `tests/fixtures/learner_state_frozen_policy_generation/`

The future scaffold fixture validator should check:

- `tests/fixtures/learner_state_frozen_policy_generation_scaffold/`

These roots should remain separate:

- generation validation fixtures test the generation bridge contract
- scaffold fixtures test scaffold API and CLI behavior

Later compatibility checks can compare scaffold summaries with generation
validator expected-result metadata, but the roots should not be merged.

## 14. CLI Future

Future CLI entrypoint:

```bash
PYTHONPATH=python python3 -m learner_state.frozen_policy_generation_scaffold_fixture_validation --fixture-root tests/fixtures/learner_state_frozen_policy_generation_scaffold
```

Future CLI modes:

- `--fixture-root`
- `--fixture-case`
- `--json`
- `--help`

CLI output should remain safe metadata only. This step does not implement the
CLI.

## 15. Makefile / Release-Quality Future

Recommended sequence:

1. implement standalone fixture validator API
2. add fixture validator tests
3. design CLI
4. implement CLI
5. design Makefile target
6. implement Makefile target
7. run standalone log-safety review
8. design release-quality integration
9. integrate release-quality wrapper only after standalone safety is stable

It is acceptable to keep the scaffold fixture validator out of release-quality
initially. It should enter release-quality only after its standalone output is
reviewed for body and path safety.

## 16. Testing Plan

Future tests:

- root discovery is deterministic
- all 11 cases are discovered
- all 33 JSON files parse
- all required files exist
- valid 3 cases pass
- invalid 8 cases fail with expected reason codes
- reason-code mapping is correct
- forbidden fields are absent
- private path payloads are absent
- safe summary contains no file bodies
- malformed temporary fixture returns input error
- JSON output is parseable
- stdout and stderr do not leak bodies

The tests should use temporary malformed fixtures for input-error behavior
instead of changing the committed fixture root.

## 17. What This Does NOT Do

This design does not:

- implement scaffold runtime
- implement a generator
- create more fixtures
- compute metrics
- fit calibration
- run selective prediction
- train an estimator
- use real data
- prove performance
- change Makefile
- change release-quality wrapper
- change GitHub Actions workflow

Step252 implements the minimal scaffold fixture validator module and
fixture-based unit tests:

- `python/learner_state/frozen_policy_generation_scaffold_fixture_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_scaffold_fixture_validation.py`

The implementation validates the initial 11 scaffold fixture cases and 33 JSON
files as safe metadata-only fixtures. It does not add scaffold runtime code,
generator code, CLI behavior, Makefile targets, release-quality wrapper
integration, workflow changes, metric computation, calibration, selective
prediction logic, estimator training, real-data handling, or performance
claims.

Step253 designs the future CLI wrapper for this validator. The design keeps
CLI implementation out of scope while specifying fixture-root and single-case
modes, exit codes, safe human output, safe JSON output, path safety, mismatch
reporting, and later Makefile/release-quality staging.

Step254 implements that minimal CLI in the existing validator module and adds
fixture-based CLI tests. The implementation remains fixture-only and does not
add scaffold runtime code, generator code, Makefile targets, release-quality
wrapper changes, workflow changes, fixture changes, metric computation, or
real-data readiness claims.

## 18. Beginner-Friendly Explanation

A fixture validator is a checker for test-case files. It asks whether the
fixtures themselves are shaped correctly and safe to use.

JSON parsing is not enough because a file can be valid JSON while still
containing unsafe bodies, private paths, raw learner text, or future labels.

Invalid fixtures are supposed to fail. If an invalid fixture fails for the
expected reason, that is a successful fixture test.

Markers and payloads are different. A marker safely says "this case represents
raw row carryover." A payload would include the row body, which is forbidden.

The fixture validator should come before scaffold runtime code so the scaffold
has a stable and safe contract to target.

## 19. Next Recommended Steps

Candidate next steps:

- scaffold fixture validator implementation
- add remaining scaffold invalid fixtures
- scaffold runtime API design
- scaffold runtime API implementation

Recommended next step:

- scaffold fixture validator implementation

Reason:

- the initial fixture root already exists
- validating it before adding scaffold runtime code reduces ambiguity
- it keeps unsafe fixture changes fail-closed

## 20. Update History

- Step251: initial frozen policy generation scaffold fixture validator design.
- Step252: minimal scaffold fixture validator implementation and fixture-based
  tests added.
- Step253: linked the docs-only scaffold fixture validator CLI design.
- Step254: linked the minimal scaffold fixture validator CLI implementation.

## Related Documents

- [Frozen policy generation scaffold fixtures](../tests/fixtures/learner_state_frozen_policy_generation_scaffold/README.md)
- [Frozen policy generation scaffold fixture design](frozen_policy_generation_scaffold_fixture_design.md)
- [Frozen policy generation scaffold fixture validator CLI design](frozen_policy_generation_scaffold_fixture_validator_cli_design.md)
- [Frozen policy generation scaffold implementation design](frozen_policy_generation_scaffold_implementation_design.md)
- `python/learner_state/frozen_policy_generation_scaffold_fixture_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_scaffold_fixture_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_scaffold_fixture_validation_cli.py`
- [Milestone 11 frozen policy generation validation infrastructure recap](milestone_11_frozen_policy_generation_validation_infrastructure_recap.md)
- [Frozen policy generation validation design](frozen_policy_generation_validation_design.md)
- [Frozen policy generation validator CLI design](frozen_policy_generation_validator_cli_design.md)
- [Public release checklist](public_release_checklist.md)
