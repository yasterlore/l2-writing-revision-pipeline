# Selective Prediction and Calibration Validation Design

This document designs validation for the synthetic selective prediction and
calibration fixtures. Step209 adds the first minimal validator implementation
for this design while keeping calibration, selective prediction, estimator
training, and metric computation out of scope.

The design itself is not selective prediction, calibration, a learner-state
estimator, estimator training, a new model, F1, accuracy, ECE, AURCC, or
real-data handling. It is not a performance evaluation and is not a real-data
readiness claim.

## 1. Purpose

The purpose of this document is to define:

- validation order for future calibration / selective prediction fixtures
- fail-closed failure policy
- safe validation result schema
- expected-result matching behavior
- prediction / label join checks
- split validation
- test tuning leakage checks
- no-oracle and output-safety checks

The validator should help prove fixture safety and contract consistency. It
should not train a model, fit calibration parameters, optimize thresholds, or
compute performance metrics.

## 2. Current Assets

Current design assets:

- [Selective prediction and calibration design](selective_prediction_calibration_design.md)
- [Selective prediction and calibration fixture design](selective_prediction_calibration_fixture_design.md)
- fixture root: `tests/fixtures/learner_state_selective_prediction/`
- valid fixture: `valid/minimal_validation_test_split/`
- invalid fixtures:
  - `invalid/test_threshold_tuning/`
  - `invalid/test_temperature_tuning/`
  - `invalid/label_in_confidence_feature/`
  - `invalid/missing_validation_split/`
  - `invalid/same_participant_across_splits/`
  - `invalid/future_label_aggregate/`
  - `invalid/raw_text_in_prediction_row/`
- per-case `expected_calibration_validation_result.json`

Each fixture case contains:

- `predictions.jsonl`
- `labels.jsonl`
- `split_metadata.json`
- `calibration_policy.json`
- `expected_calibration_validation_result.json`

The expected-result files are safe count/reason-code contracts, not full row
snapshots and not metric reports.

## 3. Validation Scope

Validation targets:

- `predictions.jsonl`
- `labels.jsonl`
- `split_metadata.json`
- `calibration_policy.json`
- `expected_calibration_validation_result.json` for fixture tests
- schema versions
- join keys
- split metadata
- confidence fields
- policy flags
- forbidden and leakage fields

Out of scope:

- model training
- metric computation
- ECE calculation
- AURCC calculation
- calibration parameter fitting
- threshold optimization
- estimator correctness
- real-data readiness
- production data collection

## 4. Recommended Validation Order

Recommended order:

1. Path safety.
2. Required file presence.
3. JSON / JSONL parse.
4. Non-empty required inputs.
5. Schema version checks.
6. Split metadata consistency.
7. Calibration policy checks.
8. Forbidden field / leakage checks in prediction rows.
9. Prediction-label join completeness.
10. Split leakage checks.
11. Validation split presence.
12. Test tuning leakage checks.
13. Safe output construction.

Rationale:

- Path and file checks should happen before any content-dependent checks.
- Parse and schema checks make later validation deterministic.
- Split and policy metadata provide context for tuning/leakage checks.
- Forbidden prediction-row fields should fail before any metric-like work.
- Join and split checks then verify that labels remain separate but reachable.
- Safe output should be constructed last from counts and reason codes only.

The validator should fail closed: malformed or ambiguous input should fail with
a safe reason code instead of being accepted by default.

## 5. Validation Result Schema

Future validation results should contain safe metadata only:

- `validation_schema_version`
- `validation_status`
- `reason_codes`
- `failure_categories`
- `failed_checks`
- `checked_files_count`
- `prediction_row_count`
- `label_row_count`
- `split_counts`
- `policy_status`
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only_checked`
- `no_oracle_checked`
- `test_tuning_checked`

Forbidden in validation output:

- prediction row body
- label row body
- split metadata body dump
- calibration policy body dump
- expected action body
- raw learner text
- private paths
- metric values as performance claims

`failed_checks` should identify the check, stage, file role, reason code, and
category without including raw input content.

## 6. Failure Reason Code Mapping

Fixture-specific reason codes:

| Fixture | Expected reason code | Category |
| --- | --- | --- |
| `invalid/test_threshold_tuning/` | `test_threshold_tuning` | `policy` |
| `invalid/test_temperature_tuning/` | `test_temperature_tuning` | `policy` |
| `invalid/label_in_confidence_feature/` | `label_in_prediction_row` | `no_oracle` |
| `invalid/missing_validation_split/` | `missing_validation_split` | `split` |
| `invalid/same_participant_across_splits/` | `split_leakage` | `split` |
| `invalid/future_label_aggregate/` | `future_label_leakage` | `no_oracle` |
| `invalid/raw_text_in_prediction_row/` | `raw_text_in_prediction_row` | `content_safety` |

General reason codes:

- `missing_input_file`
- `malformed_input`
- `empty_input`
- `missing_label_row`
- `extra_label_row`
- `join_key_mismatch`
- `unknown_schema_version`
- `policy_count_mismatch`
- `unsafe_path`
- `duplicate_join_key`
- `invalid_confidence_value`
- `missing_confidence`

The first implementation may support a narrower subset, but reason-code names
should stay stable once tests depend on them.

## 7. Expected Validation Result Matching

Fixture tests should:

- load `expected_calibration_validation_result.json`
- compare `validation_status`
- compare `expected_failure_reason`
- compare `expected_failure_category`
- compare `expected_stage`
- compare expected prediction and label row counts
- compare expected split counts
- compare expected policy status
- compare `content_suppressed`
- compare `no_raw_rows`
- compare `synthetic_only`

Mismatch policy:

- mismatch should fail tests safely
- test failure should name the case and mismatch fields
- test failure should not print prediction rows
- test failure should not print label rows
- test failure should not dump full split metadata or calibration policy

## 8. Prediction / Label Join Validation

Join keys:

- `synthetic_participant_id`
- `synthetic_session_id`
- `synthetic_task_id`
- `micro_episode_id`
- `episode_order_index`

Requirements:

- one prediction row should have one matching label row
- missing label row should fail with `missing_label_row`
- extra label row should fail with `extra_label_row`
- mismatched key should fail with `join_key_mismatch`
- duplicate join keys should fail with `duplicate_join_key` or
  `join_key_mismatch`
- prediction rows must not contain label values

Labels are allowed to contain expected action fields because they are
label-side targets. Those values must not appear in prediction rows except in
intentional invalid fixtures.

## 9. Split Validation

Split validation should check:

- validation split is present for calibration
- test split is present for final-evaluation fixtures when policy includes
  test
- learner-disjoint split is the default
- the same participant cannot cross train / validation / test
- split counts are consistent with `split_metadata.json`
- split assignment must not use labels, outcomes, confidence, or future edits
- split leakage failure should be safe and count-only

If `split_metadata.json` says `learner_disjoint: true` but the rows show a
participant crossing splits, the validator should fail closed with
`split_leakage`.

## 10. Calibration Policy Validation

Calibration policy checks:

- `validation_only_tuning` must be true
- `test_tuning_forbidden` must be true
- `frozen_policy_required` should be true
- `temperature_selection_method` must not indicate test tuning
- `threshold_selection_method` must not indicate test tuning
- `temperature_tuning_split` must not be `test`
- `threshold_tuning_split` must not be `test`
- `selected_temperature_source` must not be `test` if present
- `selected_threshold_source` must not be `test` if present
- `allowed_abstention_rate` should be numeric and in a safe range if present
- metric result fields should not appear as performance claims
- raw output fields or real-data paths should not appear

Initial safe range for `allowed_abstention_rate` should be `0.0 <= r <= 1.0`.
Future policy may narrow this range, but invalid numeric values should fail
closed.

## 11. No-Oracle / Leakage Validation

Prediction rows must not contain:

- `expected_action`
- `expected_action_family`
- label aggregates
- future label fields
- future action fields
- future episode fields
- `final_text`
- `observed_after_text`
- `gold_label`
- raw learner text
- teacher or human correction fields
- real participant IDs

Reason-code mapping:

- expected action or expected action family in prediction rows:
  `label_in_prediction_row`
- label aggregate or future label fields: `future_label_leakage`
- future action / future episode fields: `future_label_leakage` or a future
  narrower leakage reason
- raw learner text-like fields: `raw_text_in_prediction_row`
- final or observed-after text fields: `raw_text_in_prediction_row` or future
  `forbidden_prediction_field`

The validator should report reason codes only, not offending row contents.

## 12. Path Safety Validation

Path safety should:

- reject input paths containing `real_data`
- reject input paths containing `participant_data`
- reject input paths containing `private_data`
- reject input paths containing `manual_outputs`
- allow fixture paths under `tests/fixtures`
- avoid printing private absolute paths
- report safe case names or relative fixture names only

Path failures should use `unsafe_path` and should not include the full private
path in public output.

## 13. Fixture Test Design

Future tests should:

- discover fixture directories deterministically
- require every fixture case to contain all expected files
- pass `valid/minimal_validation_test_split/`
- fail each invalid fixture with its expected reason code
- exercise every `expected_calibration_validation_result.json`
- verify validation result serialization is safe
- verify stdout/stderr do not contain raw rows
- avoid full calibration policy or split metadata dumps

Fixture-root mode may later report:

- total cases
- matched cases
- mismatched cases
- input error cases
- reason-code counts
- `content_suppressed: true`
- `no_raw_rows: true`
- `synthetic_only_checked: true`
- `no_oracle_checked: true`
- `test_tuning_checked: true`

## 14. Relation to Estimator Input Validation Infrastructure

Estimator input validator checks:

- feature / label / manifest safety
- feature-label separation
- joins
- sequence grouping
- split leakage
- no-oracle input fields

Calibration validator checks:

- prediction / confidence rows
- prediction-label joins
- split metadata
- calibration policy flags
- validation-only tuning
- no test tuning
- no label leakage into prediction rows

The calibration validator should assume estimator inputs were already
validated upstream. It should not bypass estimator input validation, and
expected action remains a label-side target only. It must not feed expected
actions into candidate generation, scoring, ranking, or confidence feature
construction.

## 15. Implementation Roadmap

Recommended future order:

1. Step209: minimal calibration / selective prediction fixture validator
   implementation.
2. Step210: optional CLI design.
3. Step211: minimal CLI implementation.
4. Step212: Makefile target design.
5. Step213: release-quality integration design.
6. Step214: selective prediction / calibration scaffold design.
7. Step215: minimal learner-state estimator prototype design.

Keep these steps separate. Do not combine validator implementation, estimator
training, metric computation, and release-quality integration in one step.

Step209 adds
`python/learner_state/selective_prediction_validation.py` and
`python/learner_state/tests/test_selective_prediction_validation.py`. The
implementation loads synthetic fixture files, validates schema versions,
policy flags, prediction/label joins, split boundaries, no-oracle leakage
fields, and expected validation results, and returns safe count/reason-code
metadata only. It does not implement calibration, selective prediction,
metric computation, an estimator, or real-data handling.

Step210 adds the
[selective prediction calibration validator CLI design](selective_prediction_calibration_validator_cli_design.md)
as a docs-only plan for a future safe
`python -m learner_state.selective_prediction_validation` command. It defines
fixture-case/root modes, exit codes, safe human/JSON output, expected-result
matching, and path-safety behavior. It does not implement the CLI or connect a
Makefile target or release-quality wrapper.

Step211 implements the minimal safe CLI entrypoint in
`python/learner_state/selective_prediction_validation.py` and adds CLI tests
in `python/learner_state/tests/test_selective_prediction_validation_cli.py`.
The CLI supports fixture-case mode, fixture-root mode, safe JSON output, and
expected-result matching. It does not add a Makefile target or release-quality
integration.

## 16. What This Does NOT Do

This design and the Step209 minimal validator do not:

- implement calibration
- implement selective prediction
- train a model
- implement a learner-state estimator
- compute ECE
- compute AURCC
- compute F1 or accuracy
- use real data
- prove performance
- claim real-data readiness
- change fixtures, workflow, Makefile, release-quality wrapper, scripts, or
  tests

## 17. Beginner Notes

Validation means checking that an input has the shape and safety properties
the next program expects before that program trusts it.

Calibration fixtures need validation because confidence is easy to contaminate
with answers. A prediction row should say what the model thinks; a label row
should say the answer. The validator checks that the answer did not leak into
the model-side row.

Test tuning leakage means using test labels to choose temperature or
threshold. That is dangerous because test data is supposed to be the final
check after decisions are frozen.

Prediction-label join means matching each prediction to exactly one label
using safe synthetic keys. It lets future evaluation compare predictions to
labels without putting labels inside prediction rows.

Fail-closed means ambiguous, malformed, unsafe, or incomplete data is rejected
instead of being treated as valid.

## 18. Related Documents

- [Selective prediction and calibration design](selective_prediction_calibration_design.md)
- [Selective prediction and calibration fixture design](selective_prediction_calibration_fixture_design.md)
- [Selective prediction calibration validator CLI design](selective_prediction_calibration_validator_cli_design.md)
- [Initial selective prediction fixtures](../tests/fixtures/learner_state_selective_prediction/README.md)
- [Learner-state estimator input validation design](learner_state_estimator_input_validation_design.md)
- [No-oracle policy](03_no_oracle_policy.md)
- [Synthetic data policy](12_synthetic_data_policy.md)
- [Public release checklist](public_release_checklist.md)
