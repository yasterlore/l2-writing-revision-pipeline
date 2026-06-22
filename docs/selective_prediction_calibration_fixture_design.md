# Selective Prediction and Calibration Fixture Design

This document designs future synthetic fixtures for calibration and selective
prediction validation. It is docs-only. It does not create fixture files,
implement calibration, implement selective prediction, train a learner-state
estimator, add a model, compute F1, accuracy, ECE, AURCC, or use real data.

It is not a performance evaluation and is not a real-data readiness claim.

## 1. Purpose

The purpose of this document is to define:

- where future calibration / selective prediction fixtures should live
- which fixture cases should exist first
- which files each case should contain
- what safe prediction, label, split, and policy rows should represent
- how expected validation results should be recorded with safe metadata only
- which fail-closed reason codes future validators should use
- how these fixtures relate to estimator input validation

The fixtures are intended to test policy safety around confidence,
validation-only temperature selection, validation-only threshold selection,
and test leakage prevention. They are not meant to prove model performance.

## 2. One-Sentence Summary

A calibration / selective prediction fixture is a small synthetic test case
containing prediction logits or probabilities, labels, and split metadata so a
future validator can check validation-only temperature and threshold selection,
test leakage prevention, and no-oracle boundaries without exposing row bodies.

## 3. Fixture Root Candidate

Candidate roots:

| Candidate | Pros | Cons |
| --- | --- | --- |
| `tests/fixtures/learner_state_calibration/` | Short and focused on calibration | Does not name selective prediction or abstention |
| `tests/fixtures/selective_prediction/` | General and easy to read | Less clearly tied to learner-state work |
| `tests/fixtures/learner_state_selective_prediction/` | Ties learner-state, confidence, abstention, and calibration policy together | Slightly longer path |
| `tests/fixtures/learner_state_estimator_calibration/` | Clearly estimator-adjacent | Understates selective prediction / abstention |
| `docs/examples/` | Easy to browse | Avoid: examples risk being copied into docs and can encourage row-body publication |

Recommendation:

Use `tests/fixtures/learner_state_selective_prediction/`.

Rationale:

- keeps fixtures under the existing test fixture tree
- makes the learner-state scope explicit
- covers both selective prediction and calibration
- avoids placing JSONL examples in docs
- leaves estimator input fixtures as a separate upstream boundary

Step206 did not create the directory. Step207 creates this directory as the
initial synthetic-only fixture root.

## 4. Fixture Case Structure

Future case layout:

```text
tests/fixtures/learner_state_selective_prediction/
  valid/
    minimal_validation_test_split/
    fixed_abstention_rate_policy/
    temperature_scaling_candidate/
  invalid/
    test_threshold_tuning/
    test_temperature_tuning/
    label_in_confidence_feature/
    missing_validation_split/
    same_participant_across_splits/
    future_label_aggregate/
    raw_text_in_prediction_row/
```

Initial fixture creation should start with one valid case and a small set of
representative invalid cases.

Step207 implements this initial fixture set with one valid fixture and seven
representative invalid fixtures. The files are fixture data only; no
calibration validator, selective prediction code, learner-state estimator, or
metric computation is added.

Step208 adds the
[selective prediction and calibration validation design](selective_prediction_calibration_validation_design.md)
for future fixture validation order, safe result schema, expected-result
matching, join checks, split checks, calibration policy checks, test tuning
leakage checks, and no-oracle checks. It does not implement the validator.

## 5. Fixture File Set

Each fixture case should eventually contain:

- `predictions.jsonl`
- `labels.jsonl`
- `split_metadata.json`
- `calibration_policy.json`
- `expected_calibration_validation_result.json`

Optional:

- `README.md`

Roles:

| File | Role |
| --- | --- |
| `predictions.jsonl` | Synthetic prediction-side rows with logits or probabilities, predicted action family, confidence, and safe join keys |
| `labels.jsonl` | Synthetic label-side targets joined by safe keys |
| `split_metadata.json` | Count-only split metadata and learner-disjoint split declarations |
| `calibration_policy.json` | Policy configuration for confidence definition, temperature selection, threshold selection, and no-test-tuning flags |
| `expected_calibration_validation_result.json` | Safe expected pass/fail metadata for fixture tests |
| `README.md` | Optional short fixture-root explanation and synthetic-only safety notes |

Docs should not paste JSONL row bodies, logits/probability full dumps, label
bodies, expected action bodies, or generated manifests.

## 6. Prediction Row Design

Prediction rows may include:

- synthetic participant ID
- synthetic session ID
- synthetic task ID
- `micro_episode_id`
- `episode_order_index`
- split name
- candidate action family list or label-space version
- logits or probabilities
- `predicted_action_family`
- confidence
- optional `calibrated_confidence` in later output fixtures

Prediction rows must not include:

- raw learner text
- `final_text`
- `observed_after_text`
- future edit fields
- `expected_action`
- `expected_action_family`
- label aggregates
- future label aggregates
- teacher or human correction
- real participant IDs
- private paths

The prediction row represents model-side output. It is allowed to be wrong.
Correctness is determined only by joining to label rows during validation or
future evaluation.

## 7. Label Row Design

Label rows may include:

- synthetic participant ID
- synthetic session ID
- synthetic task ID
- `micro_episode_id`
- `episode_order_index`
- expected action family
- expected action type if needed
- label schema version
- synthetic label source

Label policy:

- labels are label-side only
- labels join to predictions using safe keys
- labels must be synthetic in this stage
- labels must not be fed back into prediction row construction
- labels must not influence split assignment
- labels must not be used for test threshold or test temperature tuning
- label row bodies should not be pasted into docs

## 8. Split Metadata Design

Split metadata should describe:

- train / validation / test split names
- count-only rows by split
- count-only participants by split
- learner-disjoint guarantee
- validation split availability
- test split availability
- whether split assignment is label-independent

Policy:

- learner-disjoint split is the default
- validation split is used for temperature and threshold selection
- test split is final evaluation only after policy freeze
- the same synthetic participant cannot appear across train, validation, and
  test
- split counts are count-only
- split assignment must not use labels, outcomes, confidence, or future edits

## 9. Calibration Policy Design

`calibration_policy.json` may eventually include:

- `policy_schema_version`
- `confidence_definition`
- `temperature_selection_method`
- `threshold_selection_method`
- `allowed_abstention_rate`
- `validation_only_tuning`
- `test_tuning_forbidden`
- `frozen_policy_required`
- `synthetic_only`
- optional policy status fields for future validators

Initial policy should be configuration only. It should not contain computed
metric results, fitted model parameters, full logits dumps, row bodies, or
test-derived thresholds.

Recommended initial policy values:

- confidence definition: max softmax probability
- temperature selection: validation-only candidate or not yet selected
- threshold selection: validation-only fixed abstention rate candidate
- test tuning forbidden: true
- frozen policy required before test evaluation: true

## 10. Expected Validation Result Design

`expected_calibration_validation_result.json` should contain safe metadata
only:

- `validation_status`
- `expected_failure_reason`
- `expected_failure_category`
- `expected_stage`
- `expected_prediction_row_count`
- `expected_label_row_count`
- `expected_split_counts`
- `expected_policy_status`
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only`

Forbidden in expected-result files and docs:

- raw prediction rows
- raw label rows
- logits/probability full dumps in docs
- expected action body
- raw learner text
- private paths
- performance metric values used as claims

Valid fixtures may omit failure fields or set them to null. Invalid fixtures
should name the expected failure reason and category.

## 11. Valid Fixture Design

Initial valid fixture:

`valid/minimal_validation_test_split/`

Planned properties:

- small synthetic participants
- learner-disjoint validation/test split
- optional train split if useful for policy shape
- predictions and labels join completely
- confidence values present
- policy declares validation-only tuning
- policy declares test tuning forbidden
- no threshold chosen on test
- no temperature chosen on test
- no raw learner text
- no expected action in prediction rows
- no future label aggregates
- expected validation status: pass

This fixture would validate that the future scaffold can safely read
prediction-side confidence rows and label-side targets without crossing the
validation/test boundary.

## 12. Invalid Fixture Design

Representative invalid fixtures:

| Fixture | Trigger | Expected reason |
| --- | --- | --- |
| `invalid/test_threshold_tuning/` | Policy or metadata indicates threshold was chosen using test labels | `test_threshold_tuning` |
| `invalid/test_temperature_tuning/` | Policy or metadata indicates temperature was chosen using test labels | `test_temperature_tuning` |
| `invalid/label_in_confidence_feature/` | Prediction row contains expected action or a label-derived confidence feature | `label_in_prediction_row` |
| `invalid/missing_validation_split/` | Calibration policy requires validation tuning but no validation split exists | `missing_validation_split` |
| `invalid/same_participant_across_splits/` | Same synthetic participant appears in validation/test or train/test | `split_leakage` |
| `invalid/future_label_aggregate/` | Prediction row contains future label aggregate or future action summary | `future_label_leakage` |
| `invalid/raw_text_in_prediction_row/` | Prediction row contains raw learner text or text-like content fields | `raw_text_in_prediction_row` |

Additional future invalid cases may cover missing labels, extra labels, join
key mismatch, unknown schema versions, malformed input, unsafe paths, and
empty inputs.

## 13. Failure Reason Code Design

Reason code candidates:

- `test_threshold_tuning`
- `test_temperature_tuning`
- `label_in_prediction_row`
- `missing_validation_split`
- `split_leakage`
- `future_label_leakage`
- `raw_text_in_prediction_row`
- `missing_label_row`
- `extra_label_row`
- `join_key_mismatch`
- `unknown_schema_version`
- `malformed_input`
- `unsafe_path`
- `empty_input`
- `manifest_count_mismatch`
- `policy_schema_mismatch`

Failure categories should remain broad and safe, for example:

- `path_safety`
- `input_format`
- `schema`
- `join`
- `split`
- `policy`
- `no_oracle`
- `content_safety`

Validators should report reason codes and counts, not row bodies.

## 14. Future Validation Checks

A future calibration fixture validator should check:

- path safety
- required file presence
- JSON / JSONL parseability
- known schema versions
- non-empty required inputs
- prediction / label join completeness
- duplicate join keys
- split presence
- learner-disjoint split boundaries
- validation-only tuning flags
- no test tuning for temperature
- no test tuning for threshold
- no labels or label aggregates in prediction rows
- no raw text in prediction rows
- no future leakage fields
- count consistency across files
- safe output construction

Validation output should be safe metadata only:

- case name
- validation status
- reason codes
- failure categories
- prediction row count
- label row count
- split counts
- content suppression flags

## 15. Relation to Estimator Input Validation Infrastructure

Estimator input validation and calibration fixture validation are adjacent but
different boundaries.

Estimator input validation checks:

- exported-shape feature rows
- separated label rows
- manifest counts
- feature/label joins
- sequence grouping
- split leakage
- no-oracle feature boundaries

Calibration fixture validation should check:

- prediction-side confidence rows
- prediction/label joins
- validation/test split policy
- temperature and threshold tuning boundaries
- no label-derived confidence features
- no raw text or future label leakage in prediction rows

Future calibration code should assume estimator inputs have already been
validated. It should not bypass input validation, no-oracle checks, or
feature/label separation.

## 16. Implementation Roadmap

Recommended future order:

1. Step207: create initial calibration / selective prediction fixtures.
2. Step208: calibration / selective prediction validation design.
3. Step209: minimal calibration fixture validator implementation.
4. Step210: optional CLI design.
5. Step211: Makefile target design.
6. Step212: release-quality integration design.
7. Step213: selective prediction / calibration scaffold design.
8. Step214: minimal learner-state estimator prototype design.

Keep implementation steps narrow. Do not combine fixture creation, validation
logic, estimator modeling, metric computation, and release-quality integration
in one step.

Step209 adds a minimal synthetic-only fixture validator at
`python/learner_state/selective_prediction_validation.py` with fixture-based
tests in `python/learner_state/tests/test_selective_prediction_validation.py`.
The validator exercises this fixture root through safe count/reason-code
metadata and expected-result matching. It does not compute calibration
metrics, train a model, or expose row bodies.

## 17. What This Does NOT Do

This design does not:

- create fixture files
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
- change sequence exporter code
- change estimator input validator code
- change audit code
- change workflow, Makefile, release-quality wrapper, or shell scripts

## 18. Beginner Notes

A calibration fixture is a small synthetic example that lets the project test
whether confidence and abstention rules are wired safely before any real model
evaluation exists.

A prediction row is what the model side says: predicted action family,
confidence, and optional logits or probabilities. A label row is the answer
side used to check that prediction. Keeping them separate prevents the answer
from leaking into the model's input.

The validation split is needed because settings such as temperature and
threshold must be chosen somewhere. The test split is held back for the final
check after those settings are frozen.

Test tuning is dangerous because it makes the final test set part of the
design process. Once test labels influence thresholds or temperature, the test
result is no longer an honest final evaluation.

Confidence fixtures are useful because confidence has its own leakage risks:
it can accidentally include labels, future outcomes, or raw text even when the
original estimator input rows are safe.

## 19. Related Documents

- [Selective prediction and calibration design](selective_prediction_calibration_design.md)
- [Selective prediction and calibration validation design](selective_prediction_calibration_validation_design.md)
- [Initial selective prediction fixtures](../tests/fixtures/learner_state_selective_prediction/README.md)
- [Milestone 08 learner-state estimator input validation infrastructure recap](milestone_08_learner_state_estimator_input_validation_infrastructure_recap.md)
- [Learner-state estimator input contract design](learner_state_estimator_input_contract_design.md)
- [Learner-state estimator input validation design](learner_state_estimator_input_validation_design.md)
- [No-oracle policy](03_no_oracle_policy.md)
- [Synthetic data policy](12_synthetic_data_policy.md)
- [Public release checklist](public_release_checklist.md)
