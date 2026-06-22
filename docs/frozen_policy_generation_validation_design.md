# Frozen Policy Generation Validation Design

This document designs future validation for frozen policy generation fixtures.

It is documentation only. It does not implement a generation validator, a
generator, a CLI, a Makefile target, calibration, selective prediction, a
learner-state estimator, estimator training, model logic, metric computation,
GitHub Actions workflow changes, release-quality wrapper changes, Python code,
tests, or fixture changes. It is not a performance evaluation and is not a
real-data readiness claim.

The design assumes synthetic-only fixtures and metadata-only outputs. Public
docs must not include raw GitHub Actions logs, full job output, copied log
blocks, screenshots containing raw logs, frozen policy artifact bodies, JSON
bodies, policy bodies, raw rows, logits/probability dumps, prediction row
bodies, label bodies, split bodies, calibration policy bodies, generated
feature/label/manifest bodies, private paths, raw learner text, or real
participant data.

## 1. Purpose

The purpose of this document is to define how a future frozen policy
generation validator should inspect the Step236 generation fixtures.

The validator design should answer:

- whether a generation request is safe and well formed
- whether an input fixture pointer is safe and expects validated input
- whether temperature and threshold policies are validation-only
- whether output and safety policies forbid unsafe content
- whether expected generation results match observed validation outcomes
- whether expected frozen policy validation results are consistent with the
  generation scenario

This is not generator implementation. It does not create or validate an actual
generated frozen policy artifact body, and it does not compute temperature,
threshold, calibration quality, F1, accuracy, ECE, AURCC, or model
performance.

## 2. Current Assets

Current assets feeding this design:

- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Frozen policy generation fixture design](frozen_policy_generation_fixture_design.md)
- [Frozen policy generation fixtures](../tests/fixtures/learner_state_frozen_policy_generation/README.md)

The Step236 fixture root is:

```text
tests/fixtures/learner_state_frozen_policy_generation/
```

It contains three valid cases:

- `valid/identity_temperature_fixed_threshold/`
- `valid/identity_temperature_fixed_abstention_rate/`
- `valid/validation_nll_temperature_metadata_only/`

It contains ten intentional invalid cases:

- `invalid/unvalidated_input/`
- `invalid/selective_prediction_validator_failure/`
- `invalid/test_derived_temperature/`
- `invalid/test_derived_threshold/`
- `invalid/raw_rows_carryover/`
- `invalid/logits_dump_carryover/`
- `invalid/missing_validation_split/`
- `invalid/private_path_output/`
- `invalid/performance_claim_generation/`
- `invalid/frozen_policy_validator_failure/`

Each fixture case has four safe metadata files:

- `generation_request.json`
- `input_fixture_pointer.json`
- `expected_generation_result.json`
- `expected_frozen_policy_validation_result.json`

The current root has 13 cases, 52 JSON files, and a root README. The fixture
files are metadata-only and do not store generated frozen policy artifact
bodies.

## 3. Validation Scope

The future generation validator should inspect:

- `generation_request.json`
- `input_fixture_pointer.json`
- `expected_generation_result.json`
- `expected_frozen_policy_validation_result.json`
- request schema version
- pointer schema version
- source selective prediction fixture pointer
- expected selective prediction validator status
- validation split availability
- temperature policy source and method
- threshold policy source and method
- output policy safety
- safety policy booleans
- recursive forbidden field and path scan results
- expected-result matching

The validator should not do:

- actual generator implementation
- actual frozen policy artifact generation
- calibration computation
- threshold computation
- model training
- F1 calculation
- accuracy calculation
- ECE calculation
- AURCC calculation
- real-data readiness review

The validator checks fixture contracts and safety boundaries only.

## 4. Recommended Validation Order

Recommended future validation order:

1. Path safety.
2. File presence.
3. JSON parse.
4. Schema version checks.
5. Required field checks.
6. Input pointer safety.
7. Source selective prediction fixture status check.
8. Validation split availability check.
9. Learner-disjoint and label-in-prediction metadata check.
10. Temperature policy validation.
11. Threshold policy validation.
12. Output policy validation.
13. Safety policy validation.
14. Recursive forbidden field and path scan.
15. Expected frozen policy validation result consistency.
16. Expected generation result matching.
17. Safe output construction.

Rationale:

- path and file checks happen early so unsafe or missing inputs fail before any
  deeper interpretation
- JSON and schema checks happen before field semantics are trusted
- input pointer checks happen before generation policy checks because the
  generator should require validated selective prediction input
- validation split and no-oracle metadata checks happen before tuning policy
  checks because tuning policy is unsafe without the split boundary
- temperature and threshold checks happen before output checks because
  test-derived tuning must fail closed
- recursive forbidden scans happen after parse and schema checks but before
  safe output construction
- expected-result matching happens last so mismatch summaries can be safe,
  metadata-only, and informed by all checks

## 5. Validation Result Schema

The future validation result should be safe metadata only.

Candidate fields:

- `validation_schema_version`
- `validation_status`
- `reason_codes`
- `failure_categories`
- `failed_checks`
- `checked_files_count`
- `generation_request_schema_version`
- `pointer_schema_version`
- `generation_status`
- `expected_output_status`
- `expected_frozen_policy_validation_status`
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only_checked`
- `no_oracle_checked`
- `test_tuning_checked`
- `forbidden_field_scan_checked`
- `private_path_scan_checked`
- `performance_claim_scan_checked`

Forbidden from validation output:

- request body
- input fixture body
- generated frozen policy body
- raw rows
- logits dump
- probability dump
- label body
- split body
- calibration policy body
- private paths
- performance metric body
- raw learner text

## 6. Failure Reason Code Mapping

Step236 fixture case mapping:

| Fixture case | Expected reason code |
| --- | --- |
| `invalid/unvalidated_input/` | `unvalidated_input` |
| `invalid/selective_prediction_validator_failure/` | `selective_prediction_validator_failure` |
| `invalid/test_derived_temperature/` | `test_temperature_tuning` |
| `invalid/test_derived_threshold/` | `test_threshold_tuning` |
| `invalid/raw_rows_carryover/` | `raw_rows_in_generated_policy` |
| `invalid/logits_dump_carryover/` | `logits_dump_in_generated_policy` |
| `invalid/missing_validation_split/` | `missing_validation_split` |
| `invalid/private_path_output/` | `unsafe_path` |
| `invalid/performance_claim_generation/` | `performance_claim_in_generated_policy` |
| `invalid/frozen_policy_validator_failure/` | `frozen_policy_validator_failure` |

General reason codes:

- `missing_generation_file`
- `malformed_generation_request`
- `unknown_generation_request_schema_version`
- `unknown_pointer_schema_version`
- `missing_required_field`
- `invalid_temperature_policy`
- `invalid_threshold_policy`
- `invalid_output_policy`
- `invalid_safety_policy`
- `forbidden_field`
- `expected_result_mismatch`

Reason codes should be stable, lowercase, and safe to print in human or JSON
summaries.

## 7. Expected Generation Result Matching

The future validator should load `expected_generation_result.json` and compare
safe fields only:

- `generation_status`
- `expected_failure_reason`
- `expected_failure_category`
- `expected_stage`
- `expected_output_status`
- `expected_frozen_policy_validation_status`
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only`
- `no_oracle_checked`
- `test_tuning_checked`

A mismatch should fail tests safely with an `expected_result_mismatch` reason
or a dedicated mismatch summary. The mismatch summary should include only case
id, expected status, observed status, reason codes, and stage names. It must
not include request bodies, input fixture bodies, generated artifact bodies,
raw rows, logits dumps, private paths, or metric bodies.

## 8. Expected Frozen Policy Validation Result Consistency

The future validator should also check that
`expected_frozen_policy_validation_result.json` is consistent with the
generation scenario.

Consistency rules:

- valid generation cases should expect frozen policy validation `pass`
- invalid generation cases with no generated policy write should expect
  `not_applicable` or an equivalent skipped status
- `invalid/frozen_policy_validator_failure/` should expect a frozen policy
  validation failure path
- consistency checks should not require a generated artifact body
- future generator implementation should run the frozen policy validator after
  generation and before accepting any generated artifact

This consistency check keeps the bridge contract aligned: input validation
guards the source, generation validation guards the request, and frozen policy
validation guards the output artifact.

## 9. Recursive Forbidden Field Scan

The future validator should recursively inspect keys and safe string values
for forbidden content markers.

Forbidden key or value families:

- raw prediction rows
- raw label rows
- raw row carryover
- logits dump
- probability dump
- generated frozen policy body
- expected action body
- raw learner text
- `final_text`
- `observed_after_text`
- `gold_label`
- teacher correction
- human correction
- private absolute paths
- `manual_outputs` path in valid cases
- performance metric claim fields

Suggested reason mapping:

- raw row carryover -> `raw_rows_in_generated_policy`
- logits or probability dump -> `logits_dump_in_generated_policy`
- private or manual-output path -> `unsafe_path`
- performance claim -> `performance_claim_in_generated_policy`
- other forbidden content -> `forbidden_field`

The validator should not print the offending body. It should print only the
safe reason code and check name.

## 10. Input Pointer Validation

`input_fixture_pointer.json` should be validated as a safe pointer, not as a
content copy.

Rules:

- use safe relative paths only
- do not include prediction body
- do not include label body
- do not include split body
- do not include calibration policy body
- source selective prediction fixture exists or is expected to exist
- expected selective prediction validator status must be `pass` for valid
  generation
- unvalidated input fails with `unvalidated_input`
- selective prediction validator failure fails with
  `selective_prediction_validator_failure`
- validation split must be available for valid generation
- learner-disjoint expectation should be true for valid generation
- `label_in_prediction_row_expected` should be false for valid generation
- `test_tuning_expected` should be false for valid generation

The pointer protects traceability without duplicating content-bearing rows.

## 11. Temperature Policy Validation

Valid temperature policy examples:

- method `none_identity`
- method `validation_nll_minimization`

Allowed source split:

- `validation`
- `none_identity`

Rules:

- test source is forbidden
- raw logits dump is forbidden
- invalid method or invalid source fails safely
- test-derived temperature fails with `test_temperature_tuning`
- malformed numeric metadata can fail with `invalid_temperature_policy`
- this validator design does not compute NLL

The validator checks provenance and shape, not calibration quality.

## 12. Threshold Policy Validation

Valid threshold policy examples:

- method `fixed_confidence_threshold`
- method `fixed_abstention_rate`

Allowed source split:

- `validation`

Rules:

- `threshold` should be numeric and in the range `0.0` to `1.0` if present
- `allowed_abstention_rate` should be numeric and in the range `0.0` to `1.0`
  if present
- test source is forbidden
- test-derived threshold fails with `test_threshold_tuning`
- invalid method, source, or numeric range fails with
  `invalid_threshold_policy`

The validator checks policy metadata only. It does not compute a threshold.

## 13. Output Policy Validation

`output_policy` should describe where a future generated artifact may be
written without writing it during validation-only checks.

Rules:

- no private path in valid cases
- no `manual_outputs` path in automated valid fixtures
- no generated artifact body in fixture metadata
- output target must be synthetic-safe or tmp-safe for future implementation
- validation-only checks should not write files
- performance claims are forbidden

Unsafe paths should fail with `unsafe_path`. Performance claims should fail
with `performance_claim_in_generated_policy`.

## 14. Safety Policy Validation

Required safety booleans should be true:

- `synthetic_only`
- `content_suppressed`
- `no_raw_rows`
- `no_oracle_checked`
- `test_tuning_forbidden`
- `no_private_paths`
- `no_logits_dump`
- `no_label_body`
- `no_policy_body_dump`
- `future_leakage_checked`

Missing or false safety booleans should fail safely with
`invalid_safety_policy` or a more specific reason code when available.

Safety policy validation is separate from forbidden scans. The former checks
declared commitments; the latter checks the actual metadata structure for
unsafe content.

## 15. Fixture Test Design

Future tests should cover:

- deterministic fixture discovery
- valid three cases pass
- invalid ten cases fail with expected reason
- all expected files are exercised
- missing files fail safely
- malformed JSON fails safely
- safe result serialization
- safe mismatch summary
- no request body in output
- no generated artifact body in output
- no private path in output
- no raw rows or logits dumps in output
- no performance metric bodies in output

Tests should use synthetic-only fixture metadata and should not write
`manual_outputs/` or tracked `tmp/` artifacts.

## 16. Relation To Existing Validators

Existing validator boundaries:

- selective prediction validator checks the input contract
- frozen policy validator checks the output artifact contract
- generation validator checks the bridge contract

The future generator should call the selective prediction validator before
generation and the frozen policy validator after constructing the artifact.
The generation validator should not duplicate calibration computation, model
training, or metric computation.

The bridge validator exists to ensure the generator request and expected
results remain safe before implementation work starts.

## 17. Implementation Roadmap

Recommended next steps:

1. Step238: minimal frozen policy generation fixture validator implementation.
2. Step239: frozen policy generation validator CLI design.
3. Step240: CLI implementation.
4. Step241: Makefile target design and implementation.
5. Step242: release-quality integration design and implementation.
6. Step243: frozen policy generation scaffold implementation design.

Each step should remain narrow. Do not combine generator implementation,
validator implementation, CLI, Makefile, release-quality wiring, calibration,
metric computation, estimator training, and real-data readiness in one step.

## 18. What This Does Not Do

This design does not:

- implement a validator
- implement a generator
- create new fixtures
- create a frozen policy artifact
- compute temperature
- compute threshold
- calibrate a model
- run selective prediction
- train an estimator
- compute metrics
- use real data
- prove performance
- change release-quality
- change GitHub Actions workflows
- change Makefile
- change Python code
- change tests
- change fixtures

## 19. Beginner Notes

A generation validation design is a plan for how a future checker will inspect
generation requests before trusting them.

Generation requests need validation because they describe how a future frozen
policy would be created. If a request uses test data, carries raw rows, writes
to unsafe paths, or claims performance, the generated policy would be unsafe
before it even exists.

The input pointer is checked because the generator should only run after
selective prediction inputs have already passed validation. A pointer keeps
traceability without copying prediction or label row bodies.

Generated artifact bodies are not printed because they can accidentally
include content-bearing fields, logits dumps, labels, paths, or other unsafe
details. Safe summaries should use counts, flags, statuses, and reason codes.

Fail-closed means the future validator rejects unclear, missing, malformed, or
unsafe requests instead of guessing that they are acceptable.

Success is not performance evidence. It means only that synthetic fixture
metadata obeyed the generation safety contract.

## 20. Update History

- Step237: initial frozen policy generation validation design creation.

## Related Documents

- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Frozen policy generation fixture design](frozen_policy_generation_fixture_design.md)
- [Frozen policy generation fixtures](../tests/fixtures/learner_state_frozen_policy_generation/README.md)
- [Milestone 10 frozen policy validation infrastructure recap](milestone_10_frozen_policy_validation_infrastructure_recap.md)
- [Frozen selective prediction policy validation design](frozen_selective_prediction_policy_validation_design.md)
- [Frozen selective prediction policy schema design](frozen_selective_prediction_policy_schema_design.md)
- [Selective prediction and calibration scaffold design](selective_prediction_calibration_scaffold_design.md)
- [Selective prediction and calibration validation design](selective_prediction_calibration_validation_design.md)
- [No-oracle policy](03_no_oracle_policy.md)
- [Synthetic data policy](12_synthetic_data_policy.md)
- [Public release checklist](public_release_checklist.md)
