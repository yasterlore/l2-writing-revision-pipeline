# Frozen Policy Generation Validation Design

This document designs validation for frozen policy generation fixtures.

It is documentation only for the design portion, with Step238 implementation
status noted below. It does not implement a generator, frozen policy generation
scaffold, CLI, Makefile target, release-quality integration, workflow change,
calibration, selective prediction, learner-state estimator, estimator
training, new model, or metric computation. It is not a performance evaluation
and is not a real-data readiness claim.

Public docs must not include raw GitHub Actions logs, full job output, copied
log blocks, screenshots containing raw logs, frozen policy artifact bodies,
JSON bodies, request bodies, policy bodies, raw rows, logits/probability
dumps, label bodies, split bodies, calibration policy bodies, generated
feature/label/manifest bodies, private paths, raw learner text, or real
participant data.

Step238 implements the minimal fixture validator in
`python/learner_state/frozen_policy_generation_validation.py` with tests in
`python/learner_state/tests/test_frozen_policy_generation_validation.py`. That
implementation validates only synthetic fixture metadata and returns only safe
metadata summaries.

## 1. Purpose

The purpose of this document is to define how frozen policy generation
fixtures should be checked before a future generator is trusted.

The validator should inspect generation requests, input fixture pointers,
expected generation results, and expected frozen policy validation results. It
should fail closed on unsafe paths, missing files, malformed JSON, unknown
schema versions, unvalidated inputs, test-derived temperature or threshold
policy, forbidden body carryover, unsafe output policy, invalid safety policy,
and expected-result mismatch.

This is not generator implementation. It does not create frozen policy
artifacts, compute temperature, compute threshold, calibrate a model, run
selective prediction, train an estimator, compute F1, compute accuracy, compute
ECE, or compute AURCC.

## 2. Current Assets

Current assets:

- Step234 frozen policy generation scaffold design
- Step235 frozen policy generation fixture design
- Step236 fixture root
- Step237 validation design
- Step238 minimal Python fixture validator implementation

Fixture root:

```text
tests/fixtures/learner_state_frozen_policy_generation/
```

Current fixture inventory:

- 3 valid cases
- 10 invalid cases
- 13 total cases
- 52 JSON files
- root README

Each case has:

- `generation_request.json`
- `input_fixture_pointer.json`
- `expected_generation_result.json`
- `expected_frozen_policy_validation_result.json`

## 3. Validation Scope

In scope:

- request schema version
- pointer schema version
- required fields
- input pointer safety
- expected selective prediction validator status
- validation split availability
- learner-disjoint expectation
- label-in-prediction expectation
- test-tuning expectation
- temperature policy source and method
- threshold policy source, method, and numeric ranges
- output policy safety
- safety policy booleans
- recursive forbidden field and path scan
- expected frozen policy validation result consistency
- expected generation result matching
- safe result serialization

Out of scope:

- actual generator implementation
- actual frozen policy artifact generation
- calibration computation
- threshold computation
- model training
- F1 / accuracy / ECE / AURCC calculation
- real-data readiness

## 4. Recommended Validation Order

Recommended order:

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

This order rejects unsafe or malformed inputs before interpreting policy
metadata, then constructs only safe count/status/reason-code output.

## 5. Validation Result Schema

Validation result fields are safe metadata only:

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
- label body
- split body
- calibration policy body
- private paths
- metric body
- raw learner text

## 6. Failure Reason Code Mapping

Step236 fixture mapping:

| Fixture case | Reason code |
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

General reason codes include `missing_generation_file`,
`malformed_generation_request`,
`unknown_generation_request_schema_version`, `unknown_pointer_schema_version`,
`missing_required_field`, `invalid_temperature_policy`,
`invalid_threshold_policy`, `invalid_output_policy`, `invalid_safety_policy`,
`forbidden_field`, and `expected_result_mismatch`.

## 7. Expected Generation Result Matching

The validator should compare safe fields from `expected_generation_result.json`:

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

Mismatch output must not include request bodies or artifact bodies.

## 8. Expected Frozen Policy Validation Result Consistency

Valid generation cases should expect frozen policy validation `pass`.

Invalid generation cases that should not write an artifact should expect
`not_applicable` or skipped frozen policy validation. The
`frozen_policy_validator_failure` case is the explicit failure path for a
would-be generated artifact rejected by the frozen policy validator.

No generated artifact body is required for this consistency check.

## 9. Recursive Forbidden Field Scan

The validator should detect:

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
- teacher/human correction
- private absolute paths
- `manual_outputs` path in valid cases
- performance metric claim fields

Reason mapping:

- raw rows -> `raw_rows_in_generated_policy`
- logits/probability dump -> `logits_dump_in_generated_policy`
- private path -> `unsafe_path`
- performance claim -> `performance_claim_in_generated_policy`
- other forbidden body field -> `forbidden_field`

## 10. Input Pointer Validation

Input pointer rules:

- safe relative paths only
- no prediction body
- no label body
- no split body
- no calibration policy body
- valid generation requires selective prediction validator status `pass`
- unvalidated input fails with `unvalidated_input`
- selective prediction validator failure fails with
  `selective_prediction_validator_failure`
- missing validation split fails with `missing_validation_split`
- learner-disjoint expectation must be true for valid generation
- label-in-prediction expectation must be false for valid generation
- test-tuning expectation must be false for valid generation

## 11. Temperature Policy Validation

Valid methods:

- `none_identity`
- `validation_nll_minimization`

Valid source split:

- `validation`
- `none_identity`

Test source is forbidden and fails with `test_temperature_tuning`. Invalid
method or source fails with `invalid_temperature_policy`. No NLL computation is
performed by this validator.

## 12. Threshold Policy Validation

Valid methods:

- `fixed_confidence_threshold`
- `fixed_abstention_rate`

Source split must be `validation`. `threshold_value` and
`allowed_abstention_rate` must be numeric and in the range `0.0` to `1.0` when
present. Test source is forbidden and fails with `test_threshold_tuning`.

## 13. Output Policy Validation

Valid output policy must not contain private paths, `manual_outputs`, generated
artifact bodies, or performance claims. Validation should not write files.
Unsafe output paths fail with `unsafe_path`.

## 14. Safety Policy Validation

Required safety commitments should be true:

- `synthetic_only`
- `content_suppressed`
- `no_raw_rows`
- `no_oracle_checked`
- `test_tuning_forbidden`
- no private paths
- no logits dump
- no label body
- no policy body dump
- future leakage checked

The Step238 implementation validates the Step236 fixture field names that
encode these commitments, such as `forbid_content_rows`,
`forbid_model_score_vector_dump`, `forbid_probability_vectors`,
`forbid_label_body`, `forbid_policy_body_dump`, `forbid_private_paths`,
`forbid_metric_claims`, `forbid_test_tuning`, and required validation/split
preconditions.

## 15. Fixture Test Design

Step238 tests cover:

- deterministic fixture discovery
- valid 3 cases pass
- invalid 10 cases fail with expected reason
- all expected generation result files are exercised
- safe result serialization
- safe mismatch summary
- no request body in output
- no generated artifact body in output
- no private path in output

## 16. Relation To Existing Validators

The selective prediction validator checks input contract examples. The frozen
policy validator checks output artifact contract examples. This generation
validator checks the bridge request and expected-result contract between them.

The future generator should call both boundary validators. The generation
validator does not duplicate calibration computation or metric computation.

## 17. Implementation Roadmap

Recommended next steps:

1. Step239: frozen policy generation validator CLI design.
2. Step240: CLI implementation.
3. Step241: Makefile target design and implementation.
4. Step242: release-quality integration design and implementation.
5. Step243: frozen policy generation scaffold implementation design.

Keep implementation staged and synthetic-only.

## 18. What This Does Not Do

This design and Step238 implementation do not:

- implement a generator
- implement frozen policy generation scaffold
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
- change fixture files

## 19. Beginner Notes

A generation validator checks whether a future generator request is safe before
any generator writes an artifact.

The input pointer is checked because a generator should not run on unvalidated
prediction/label/split inputs. The pointer gives traceability without copying
prediction or label bodies.

Generated artifact bodies are not returned because they could accidentally
include unsafe rows, logits, labels, paths, or metric details.

Fail-closed means unclear, malformed, missing, or unsafe fixture metadata is
rejected instead of guessed to be safe.

Success is not performance evidence. It means only that synthetic fixture
metadata follows the bridge contract.

## 20. Update History

- Step237: initial frozen policy generation validation design.
- Step238: minimal Python fixture validator and fixture-based tests added.

## Related Documents

- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Frozen policy generation fixture design](frozen_policy_generation_fixture_design.md)
- [Frozen policy generation fixtures](../tests/fixtures/learner_state_frozen_policy_generation/README.md)
- [Frozen selective prediction policy validation design](frozen_selective_prediction_policy_validation_design.md)
- [Selective prediction and calibration scaffold design](selective_prediction_calibration_scaffold_design.md)
- `python/learner_state/frozen_policy_generation_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_validation.py`
- [Public release checklist](public_release_checklist.md)
