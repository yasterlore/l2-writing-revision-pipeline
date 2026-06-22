# Frozen Policy Generation Validation Design

## 1. Purpose

This document defines the validation design for frozen policy generation
fixtures. It describes how future tooling should inspect synthetic generation
requests, input pointers, expected generation results, and expected frozen
policy validation results before any generator implementation is trusted.

This is not generator implementation. It is not calibration implementation,
selective prediction implementation, metric computation, performance
evaluation, real-data readiness review, or production readiness evidence.

## 2. Current Assets

Current assets for this stage are:

- Step234 frozen policy generation scaffold design.
- Step235 frozen policy generation fixture design.
- Step236 initial synthetic fixture root at
  `tests/fixtures/learner_state_frozen_policy_generation/`.
- Step237 validation design captured by this document.
- Step238 minimal Python fixture validator implementation.
- Step239 frozen policy generation validator CLI design.

The fixture root contains three valid cases and ten intentional invalid cases.
Each case contains four safe metadata files:

- `generation_request.json`
- `input_fixture_pointer.json`
- `expected_generation_result.json`
- `expected_frozen_policy_validation_result.json`

That gives thirteen fixture cases and fifty-two JSON files, plus the fixture
root README. The fixture files are synthetic-only and do not store raw
prediction rows, label bodies, logits dumps, generated frozen policy artifact
bodies, private paths in valid cases, or raw learner text.

## 3. Validation Scope

The validator scope is limited to safe metadata checks over the generation
fixture files:

- generation request schema and required fields.
- input pointer schema and required fields.
- source selective prediction fixture pointer metadata.
- expected selective prediction validator status.
- validation split availability.
- learner-disjoint and no-label-in-prediction-row metadata.
- temperature and threshold policy provenance.
- output policy safety.
- safety policy booleans.
- recursive forbidden field and unsafe path scans.
- expected frozen policy validation result consistency.
- expected generation result matching.

Out of scope:

- actual frozen policy artifact generation.
- actual calibration or threshold computation.
- model training, estimator training, or selective prediction execution.
- F1, accuracy, ECE, AURCC, or other metric calculation.
- real-data handling, production data collection, or deployment readiness.

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

The order is fail-closed: cheap structural and path checks run before semantic
checks, and all reporting remains safe even when JSON is malformed or the
fixture intentionally contains leakage markers.

## 5. Validation Result Schema

Future validation results should expose only safe metadata:

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

The result must not include request bodies, input pointer bodies, generated
frozen policy bodies, raw rows, logits/probability dumps, label bodies, split
bodies, calibration policy bodies, private paths, performance metric bodies,
or raw learner text.

## 6. Failure Reason Code Mapping

Fixture-specific reason codes:

- `unvalidated_input` for an input pointer that does not require or record
  selective prediction validation.
- `selective_prediction_validator_failure` when the input contract is expected
  to fail before generation.
- `test_temperature_tuning` when temperature metadata is test-derived.
- `test_threshold_tuning` when threshold metadata is test-derived.
- `raw_rows_in_generated_policy` when raw row-like content is carried forward.
- `logits_dump_in_generated_policy` when logits or probability dumps appear.
- `missing_validation_split` when the validation split is unavailable.
- `unsafe_path` when private, real-data, or manual-output paths are referenced.
- `performance_claim_in_generated_policy` when performance claims appear.
- `frozen_policy_validator_failure` when a generated output would fail the
  frozen policy validator.

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

## 7. Expected Generation Result Matching

The validator should load `expected_generation_result.json` and compare safe
fields only:

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

Mismatch output should include only a compact safe mismatch summary. It must
not include request body content, generated artifact bodies, private paths,
raw rows, logits dumps, or raw learner text.

## 8. Expected Frozen Policy Validation Result Consistency

Valid generation cases should expect frozen policy validation to pass. Invalid
generation cases where no artifact should be written may mark the frozen
policy validation result as `not_applicable` or `skipped`. The
`frozen_policy_validator_failure` case represents a bridge failure path where
generation reaches the output contract but the frozen policy validator rejects
the resulting metadata.

This consistency check should not require a generated policy artifact body in
the fixture. Future generator implementation should run the frozen policy
validator after construction and before writing or accepting the artifact.

## 9. Recursive Forbidden Field Scan

The validator should recursively scan all fixture metadata for unsafe keys and
values. It should detect:

- raw prediction rows or raw label rows.
- raw row carryover markers.
- logits or probability dumps.
- generated frozen policy artifact body dumps.
- expected action bodies.
- raw learner text.
- `final_text`, `observed_after_text`, and `gold_label`.
- teacher or human correction bodies.
- private absolute paths.
- `manual_outputs` paths in valid cases.
- performance metric claim fields.

Reason mapping should be safe:

- raw rows map to `raw_rows_in_generated_policy`.
- logits or probabilities map to `logits_dump_in_generated_policy`.
- private paths map to `unsafe_path`.
- performance claims map to `performance_claim_in_generated_policy`.
- other forbidden content maps to `forbidden_field`.

The validator should not echo the matched unsafe value.

## 10. Input Pointer Validation

Input pointers should use safe relative paths and must not copy prediction,
label, split, or calibration policy bodies. Valid generation cases require:

- `expected_selective_prediction_validation_status` is `pass`.
- `validation_split_available` is true.
- `learner_disjoint_expected` is true.
- `label_in_prediction_row_expected` is false.
- `test_tuning_expected` is false.
- `content_suppressed` is true.
- `no_raw_rows` is true.

Unvalidated input should fail with `unvalidated_input`. A known failed
selective prediction validator result should fail with
`selective_prediction_validator_failure`. Missing validation split metadata
should fail with `missing_validation_split`.

## 11. Temperature Policy Validation

Valid temperature policy methods:

- `none_identity`
- `validation_nll_minimization`

Valid source splits:

- `validation`
- `none_identity`

The test split is forbidden as a temperature source and should map to
`test_temperature_tuning`. Raw logits dumps are forbidden and should map to
`logits_dump_in_generated_policy`. Unknown methods or sources should map to
`invalid_temperature_policy`.

This validation design does not compute NLL or choose a temperature.

## 12. Threshold Policy Validation

Valid threshold policy methods:

- `fixed_confidence_threshold`
- `fixed_abstention_rate`

The threshold source split must be `validation`. If present, `threshold` and
`allowed_abstention_rate` must be finite numeric values in the inclusive range
0.0 to 1.0. Test-derived threshold metadata should fail with
`test_threshold_tuning`. Unknown methods, invalid sources, or invalid numeric
ranges should fail with `invalid_threshold_policy`.

This validation design does not compute a threshold.

## 13. Output Policy Validation

Valid output policy metadata should avoid private paths, `manual_outputs`,
generated artifact body dumps, and performance claims. Future implementation
may write only under an explicitly synthetic-safe or temporary-safe location,
and this validation design performs no writes.

Unsafe output paths should map to `unsafe_path`. Performance claims should map
to `performance_claim_in_generated_policy`. Other invalid output policy shapes
should map to `invalid_output_policy`.

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

Missing or false values should fail safely with `invalid_safety_policy` or a
more specific reason code when available.

## 15. Fixture Test Design

Future tests should cover:

- deterministic fixture discovery.
- three valid cases passing.
- ten invalid cases failing with expected reason codes.
- all expected files exercised.
- validation result serialization to a safe dict and JSON.
- safe mismatch summaries.
- no request body in output.
- no input pointer body in output.
- no generated artifact body in output.
- no private paths in output.

Step238 implements this minimal fixture validator and fixture-based unittest
coverage. It does not implement a generator, CLI, Makefile target,
release-quality integration, calibration, selective prediction, or metrics.

## 16. Relation To Existing Validators

The selective prediction validator checks the input contract. The frozen
policy validator checks the output artifact contract. The generation validator
checks the bridge contract between them: whether a generation request is safe,
synthetic-only, validation-split-only, and expected to produce an artifact
that can later pass the frozen policy validator.

Future generator code should call existing validators instead of duplicating
their responsibilities, and should never bypass the frozen policy validator.

## 17. Implementation Roadmap

Recommended staged roadmap:

1. Step238: minimal frozen policy generation fixture validator implementation.
2. Step239: frozen policy generation validator CLI design.
3. Step240: CLI implementation.
4. Step241: Makefile target design and implementation.
5. Step242: release-quality integration design and implementation.
6. Step243: frozen policy generation scaffold implementation design.

Each stage should preserve synthetic-only fixtures, safe output, and no metric
or performance claims.

## 18. What This Does NOT Do

This document does not:

- implement a generator.
- create or write a frozen policy artifact.
- compute temperature.
- compute threshold.
- calibrate a model.
- run selective prediction.
- train a learner-state estimator.
- compute F1, accuracy, ECE, AURCC, or any other metric.
- use real participant data.
- prove model performance, calibration quality, or production readiness.

## 19. Beginner Notes

A generation validator is a guardrail around a future generator. It checks
whether the request and metadata are safe before any frozen policy artifact is
accepted. The input pointer is checked because the generator must only build
from already-validated synthetic inputs. The generated artifact body is not
printed because bodies may accidentally contain rows, labels, or other
content-bearing data.

Fail-closed means suspicious or incomplete metadata fails by default. Passing
this validator means only that the fixture contract matched expectations. It
is not evidence that a model is accurate, calibrated, or ready for real data.

## 20. Update History

- Step237: initial frozen policy generation validation design creation.
- Step238: minimal frozen policy generation fixture validator implemented in
  `python/learner_state/frozen_policy_generation_validation.py`, with
  fixture-based tests in
  `python/learner_state/tests/test_frozen_policy_generation_validation.py`.
- Step239: linked the frozen policy generation validator CLI design as the
  next docs-only interface plan.

## Related Documents

- [Frozen policy generation scaffold design](frozen_policy_generation_scaffold_design.md)
- [Frozen policy generation fixture design](frozen_policy_generation_fixture_design.md)
- [Frozen policy generation validator CLI design](frozen_policy_generation_validator_cli_design.md)
- [Frozen policy generation fixtures](../tests/fixtures/learner_state_frozen_policy_generation/README.md)
- [Frozen selective prediction policy validation design](frozen_selective_prediction_policy_validation_design.md)
- [Selective prediction and calibration scaffold design](selective_prediction_calibration_scaffold_design.md)
- [Milestone 10 frozen policy validation infrastructure recap](milestone_10_frozen_policy_validation_infrastructure_recap.md)
- `python/learner_state/frozen_policy_generation_validation.py`
- `python/learner_state/tests/test_frozen_policy_generation_validation.py`
