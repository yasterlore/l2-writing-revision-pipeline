# Frozen Selective Prediction Policy Validation Design

## 1. Purpose

This document designs validation for future
`frozen_selective_prediction_policy.json` artifacts. It defines the
recommended check order, fail-closed policy, safe validation result schema,
failure reason mapping, expected-result matching, recursive forbidden field
scan, path safety checks, and test-derived tuning checks before implementing a
validator.

This is not an implementation. It does not run calibration, implement
selective prediction, train a learner-state estimator, compute performance
metrics, or claim real-data readiness.

## 2. Current Assets

The current frozen policy validation design builds on these public-safe
synthetic assets:

- [frozen selective prediction policy schema design](frozen_selective_prediction_policy_schema_design.md)
- [frozen selective prediction policy fixture design](frozen_selective_prediction_policy_fixture_design.md)
- fixture root:
  `tests/fixtures/learner_state_frozen_selective_prediction_policy/`
- one valid fixture:
  `valid/minimal_validation_only_policy/`
- eleven intentional invalid fixtures:
  `invalid/test_derived_temperature/`,
  `invalid/test_derived_threshold/`,
  `invalid/missing_schema_version/`,
  `invalid/unknown_schema_version/`,
  `invalid/raw_rows_in_policy/`,
  `invalid/logits_dump_in_policy/`,
  `invalid/private_path_in_policy/`,
  `invalid/non_numeric_threshold/`,
  `invalid/out_of_range_abstention_rate/`,
  `invalid/missing_required_field/`, and
  `invalid/performance_claim_in_policy/`
- each fixture case contains:
  `frozen_selective_prediction_policy.json` and
  `expected_frozen_policy_validation_result.json`

The expected result file is safe metadata only. It records expected status,
reason code, category, stage, schema version, policy status, and safety
booleans without including the frozen policy body.

## 3. Validation Scope

The future validator should check:

- `frozen_selective_prediction_policy.json`
- `expected_frozen_policy_validation_result.json` for fixture tests
- schema version
- required fields
- temperature and threshold source split
- numeric ranges
- `safety_review` booleans
- `split_policy_summary`
- `validation_input_summary`
- recursive forbidden fields
- path safety
- performance-claim absence

The future validator should not check:

- calibration computation
- selective prediction decision computation
- learner-state model training
- estimator correctness
- F1 computation
- accuracy computation
- ECE computation
- AURCC computation
- real-data readiness

Validation success means the frozen policy artifact shape and safety metadata
match the expected contract. It is not performance evidence.

## 4. Recommended Validation Order

Recommended order:

1. Path safety.
2. File presence.
3. JSON parse.
4. Schema version checks.
5. Required field checks.
6. Recursive forbidden field and path scan.
7. Synthetic-only and safety boolean checks.
8. Temperature field validation.
9. Threshold field validation.
10. Abstention rate validation.
11. Confidence definition validation.
12. Split policy summary validation.
13. Validation input summary validation.
14. Performance-claim absence checks.
15. Safe output construction.

Path and file checks should run first so unsafe or missing inputs fail before
the validator tries to inspect content. Parse and schema checks should happen
before semantic checks so malformed input cannot be treated as a partial
policy. Recursive forbidden scans should happen early because raw rows, logits
dumps, private paths, and metric claims are hard safety boundaries. Semantic
checks for temperature, threshold, abstention, confidence, split policy, and
summary counts can then run on a known schema. Safe output construction is
last so every failure path emits only metadata, reason codes, counts, and
booleans.

## 5. Validation Result Schema

The future validation result should contain safe metadata only:

- `validation_schema_version`
- `validation_status`
- `reason_codes`
- `failure_categories`
- `failed_checks`
- `checked_files_count`
- `policy_schema_version`
- `policy_status`
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only_checked`
- `no_oracle_checked`
- `test_tuning_checked`
- `forbidden_field_scan_checked`
- `private_path_scan_checked`
- `performance_claim_scan_checked`

The validation result must not contain:

- full policy body
- raw prediction rows
- raw label rows
- logits dump
- probability dump
- label body
- split metadata body
- calibration policy body
- private paths
- metric body
- stack traces that include policy content

For fixture-root tests, a wrapper summary may add total case counts, matched
case counts, mismatched case counts, and reason-code counts, as long as row
and policy bodies remain suppressed.

## 6. Failure Reason Code Mapping

Step222 fixture mappings:

| Fixture case | Reason code | Category | Stage |
| --- | --- | --- | --- |
| `invalid/test_derived_temperature` | `test_temperature_tuning` | `test_tuning_leakage` | `temperature_provenance` |
| `invalid/test_derived_threshold` | `test_threshold_tuning` | `test_tuning_leakage` | `threshold_provenance` |
| `invalid/missing_schema_version` | `missing_schema_version` | `schema_version` | `schema_version` |
| `invalid/unknown_schema_version` | `unknown_schema_version` | `schema_version` | `schema_version` |
| `invalid/raw_rows_in_policy` | `raw_rows_in_policy` | `forbidden_body` | `forbidden_field_scan` |
| `invalid/logits_dump_in_policy` | `logits_dump_in_policy` | `forbidden_body` | `forbidden_field_scan` |
| `invalid/private_path_in_policy` | `unsafe_path` | `path_safety` | `path_safety` |
| `invalid/non_numeric_threshold` | `invalid_threshold` | `numeric_range` | `threshold_validation` |
| `invalid/out_of_range_abstention_rate` | `invalid_abstention_rate` | `numeric_range` | `abstention_rate_validation` |
| `invalid/missing_required_field` | `missing_required_field` | `schema_required_field` | `required_fields` |
| `invalid/performance_claim_in_policy` | `performance_claim_in_policy` | `performance_claim` | `performance_claim_scan` |

General reason codes:

- `missing_input_file`
- `malformed_input`
- `empty_input`
- `forbidden_field`
- `invalid_temperature`
- `invalid_confidence_definition`
- `invalid_safety_review`
- `invalid_split_policy`
- `policy_count_mismatch`

If multiple failures are present, the validator may return multiple reason
codes, but fixture tests should still be able to assert the primary expected
failure reason without printing the policy body.

## 7. Expected Validation Result Matching

Fixture tests should load
`expected_frozen_policy_validation_result.json` and compare:

- `validation_status`
- `expected_failure_reason`
- `expected_failure_category`
- `expected_stage`
- `expected_policy_schema_version`
- `expected_policy_status`
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only`
- `no_oracle_checked`
- `test_tuning_checked`

Mismatch should fail tests safely. The mismatch output should include only
case id, expected field names, observed field names, safe reason codes, and
safe policy status. It must not include the full policy body, raw rows, logits
dumps, label body, private path strings, or metric body.

## 8. Recursive Forbidden Field Scan

The future validator should recursively scan keys and values for forbidden
content. It should detect:

- raw prediction rows
- raw label rows
- logits dump
- probability dump
- calibration policy body dump
- split metadata body dump
- expected action body
- raw learner text
- `final_text`
- `observed_after_text`
- `gold_label`
- teacher/human correction fields
- real participant identifiers
- private absolute paths
- performance metric claim fields

Suggested reason mapping:

- raw row containers -> `raw_rows_in_policy`
- logits/probability containers -> `logits_dump_in_policy`
- private or real-data path patterns -> `unsafe_path`
- final test metric claim fields -> `performance_claim_in_policy`
- other forbidden fields -> `forbidden_field`

The validator should report only the reason code, check name, and safe field
category. It should not echo the offending value.

## 9. Temperature Validation

Temperature validation should require:

- numeric, finite, positive `temperature`, or an explicit identity sentinel
  represented by `temperature = 1.0` with method `none_identity`
- `temperature_source_split` is `validation` or `none_identity`
- `temperature_selection_method` does not reference the test split
- selected temperature is recorded as frozen before test evaluation

Failures:

- test-derived temperature source or method -> `test_temperature_tuning`
- non-numeric, non-finite, or non-positive temperature -> `invalid_temperature`
- missing required temperature field -> `missing_required_field`

The validator should not fit a temperature value. It only checks provenance
and field safety.

## 10. Threshold Validation

Threshold validation should require:

- numeric, finite `threshold`
- threshold in the inclusive range `0.0` to `1.0`
- `threshold_source_split` is `validation`
- `threshold_selection_method` does not reference the test split
- selected threshold is recorded as frozen before test evaluation

Failures:

- test-derived threshold source or method -> `test_threshold_tuning`
- non-numeric or out-of-range threshold -> `invalid_threshold`
- missing required threshold field -> `missing_required_field`

The validator should not select a threshold. It only checks that the frozen
policy claims validation-only provenance.

## 11. Abstention Rate Validation

Abstention rate validation should require:

- numeric, finite `allowed_abstention_rate`
- value in the inclusive range `0.0` to `1.0`
- policy selection remains validation-only

Failures:

- non-numeric abstention rate -> `invalid_abstention_rate`
- out-of-range abstention rate -> `invalid_abstention_rate`
- missing required abstention rate -> `missing_required_field`

Abstention rate validation does not compute coverage or risk.

## 12. Safety Review Validation

The future validator should require these booleans to be present and true:

- `synthetic_only`
- `no_oracle_checked`
- `test_tuning_forbidden`
- `no_raw_rows`
- `content_suppressed`
- `no_private_paths`
- `prediction_label_separated`
- `expected_action_not_in_prediction_rows`
- `future_leakage_checked`

The top-level fields and nested `safety_review` should agree where the same
claim appears. Missing or false values should fail safely with
`invalid_safety_review` or `missing_required_field`, depending on whether the
field is present but unsafe or absent.

## 13. Split Policy Validation

The future validator should require `split_policy_summary` to indicate:

- `learner_disjoint` is true
- `validation_used_for_tuning` is true
- `test_used_for_tuning` is false
- `label_dependent_split` is false
- `test_evaluation_future_only` is true if present

Invalid or contradictory values should fail with `invalid_split_policy`. A
test-derived temperature or threshold source should use the more specific
`test_temperature_tuning` or `test_threshold_tuning` reason code.

## 14. Validation Input Summary Validation

The future validator should verify that `validation_input_summary` is
count-only and safe:

- `validation_prediction_count` is numeric
- `validation_label_count` is numeric
- `validation_participant_count` is numeric
- `split_counts` is count-only if present
- no raw rows
- no label body
- no logits dump
- no probability dump
- no private paths

The validator may check non-negative integer counts and obvious consistency
between summary fields. It should not require real-data-style participant
metadata, and it should not infer model performance from the counts.

## 15. Fixture Test Design

Future fixture tests should:

- discover fixture cases deterministically
- verify the valid fixture passes
- verify all eleven invalid fixtures fail with their expected primary reason
- exercise every `expected_frozen_policy_validation_result.json`
- ensure validation result dictionaries are JSON-serializable
- ensure mismatch summaries are safe
- ensure failure output does not include policy body
- ensure output does not include raw rows
- ensure output does not include logits/probability dumps
- ensure output does not include private paths

Temporary mismatch tests may copy a fixture into a temporary directory and
modify only expected metadata. They should still avoid printing the policy
body on failure.

## 16. Relation To Existing Validators

The selective prediction fixture validator checks prediction rows, label
rows, split metadata, calibration policy input, joins, and no-oracle
boundaries before any scaffold work.

The future frozen policy validator checks the frozen output artifact produced
after validation-only policy selection. It should not duplicate calibration
computation, prediction/label join validation, or estimator training. The
future scaffold should depend on both boundaries:

- input fixture validation before reading prediction/logit fixtures
- frozen policy validation before test evaluation consumes a policy artifact

The frozen policy artifact is not a metric report and must not be treated as
scoring feedback.

## 17. Implementation Roadmap

Recommended next steps:

1. Step224: minimal frozen policy validator implementation. Completed with
   `python/learner_state/frozen_policy_validation.py` and fixture-based
   tests in `python/learner_state/tests/test_frozen_policy_validation.py`.
2. Step225: frozen policy validator CLI design. Completed as docs-only in
   [frozen policy validator CLI design](frozen_policy_validator_cli_design.md).
3. Step226: minimal frozen policy validator CLI implementation. Completed in
   `python/learner_state/frozen_policy_validation.py` with tests in
   `python/learner_state/tests/test_frozen_policy_validation_cli.py`.
4. Step227: frozen policy validator Makefile target design. Completed as
   docs-only in
   [frozen policy validator Makefile target design](frozen_policy_validator_makefile_target_design.md).
5. Step228: Makefile target implementation. Completed with
   `make check-learner-state-frozen-policy`; release-quality is unchanged.
6. Step229: release-quality integration design. Completed as docs-only in
   [frozen policy release-quality integration design](frozen_policy_release_quality_integration_design.md).
7. Step230: release-quality integration implementation.
8. Step231: calibration scaffold fixture design.

Keep each step narrow. Do not combine frozen policy validation, calibration
implementation, selective prediction decisions, estimator training, metric
computation, release-quality wiring, and real-data readiness.

## 18. What This Does Not Do

This design and its Step224 implementation do not:

- implement calibration
- implement selective prediction
- create new fixtures
- create or generate a frozen policy artifact from model output
- train an estimator
- compute F1
- compute accuracy
- compute ECE
- compute AURCC
- use real data
- prove performance
- claim real-data readiness

## 19. Beginner Notes

Validation design is a plan for how a future checker should decide whether a
file is safe and well formed. It is the checklist before writing the checker.

A frozen policy also needs validation because it sits between tuning and test
evaluation. If it accidentally contains test-derived values, raw rows, logits
dumps, or performance claims, later reports could become leaky or misleading.

Test-derived tuning means choosing temperature or threshold using the test
split. That is unsafe because the test split should be saved for final
checking after the policy is already frozen.

A recursive forbidden field scan means looking through the whole nested JSON
object, not only top-level fields, for unsafe keys and values.

Fail-closed means the validator should reject unclear, missing, malformed, or
unsafe inputs instead of guessing that they are acceptable.

## 20. Related Documents

- [Frozen selective prediction policy schema design](frozen_selective_prediction_policy_schema_design.md)
- [Frozen selective prediction policy fixture design](frozen_selective_prediction_policy_fixture_design.md)
- [Frozen selective prediction policy fixtures](../tests/fixtures/learner_state_frozen_selective_prediction_policy/README.md)
- [Frozen policy validator CLI design](frozen_policy_validator_cli_design.md)
- [Frozen policy validator Makefile target design](frozen_policy_validator_makefile_target_design.md)
- [Frozen policy release-quality integration design](frozen_policy_release_quality_integration_design.md)
- `python/learner_state/frozen_policy_validation.py`
- `python/learner_state/tests/test_frozen_policy_validation.py`
- `python/learner_state/tests/test_frozen_policy_validation_cli.py`
- [Selective prediction and calibration scaffold design](selective_prediction_calibration_scaffold_design.md)
- [Selective prediction and calibration validation design](selective_prediction_calibration_validation_design.md)
- [Selective prediction and calibration design](selective_prediction_calibration_design.md)
- [No-oracle policy](03_no_oracle_policy.md)
- [Synthetic data policy](12_synthetic_data_policy.md)
- [Public release checklist](public_release_checklist.md)
