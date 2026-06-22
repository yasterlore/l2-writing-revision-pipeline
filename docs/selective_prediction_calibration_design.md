# Selective Prediction and Calibration Design

This document defines the future selective prediction and calibration policy
for a learner-state estimator before any estimator prototype, training loop,
metric computation, or calibration code is implemented.

It is design documentation only. It does not implement selective prediction,
calibration, a learner-state estimator, estimator training, a new model, a new
metric computation, F1, accuracy, ECE, AURCC, or real-data handling. It is not
a performance evaluation and is not a real-data readiness claim.

## 1. Purpose

The purpose of this document is to define:

- how a future learner-state estimator may express confidence
- when a prediction may abstain instead of forcing an answer
- how validation labels may be used for calibration and threshold selection
- how test labels must remain untouched until final evaluation
- how ECE, AURCC, and coverage-risk reporting should be positioned
- how no-oracle and leakage boundaries apply to confidence and calibration
- how public output should remain safe and count-only

This design assumes synthetic-only estimator input bundles that have already
passed estimator input validation.

## 2. One-Sentence Summary

A future learner-state estimator should not be forced to predict every
micro-episode; it should be allowed to abstain when confidence is low, and that
confidence should be calibrated and thresholded using the validation split
only, never the test split.

## 3. Terminology

| Term | Meaning |
| --- | --- |
| Prediction | The model's proposed next revision action or action family for one micro-episode |
| Confidence | A numeric estimate of how likely the prediction is to be correct |
| Abstention | The decision to withhold a prediction when confidence is too low |
| Coverage | The fraction of examples where the system does make a prediction |
| Risk | The error rate among the examples that remain covered |
| Calibration | The alignment between predicted confidence and observed correctness |
| ECE | Expected calibration error, a binned summary of calibration gap |
| AURCC | Area under the risk-coverage curve, summarizing selective prediction behavior |
| Validation split | Synthetic held-out split used for temperature and threshold selection |
| Test split | Synthetic held-out split used only for final evaluation after policies are frozen |

Beginner framing: confidence is not the same as accuracy. A model can be
confident and wrong, or uncertain and right. Calibration asks whether the
confidence values mean what they claim.

## 4. Prediction Target

The future prediction target is:

- next revision action or action family
- one target per micro-episode
- synthetic expected action as label-side target only

The feature side must not include:

- final text
- observed-after text
- teacher or human correction
- future edit information
- expected action aggregates
- gold labels

Expected action remains a supervised label or evaluation target. It must not
be used as scoring feedback, candidate generation input, ranking input, split
assignment input, or calibration feature input.

## 5. Confidence Design

Candidate confidence definitions:

| Candidate | Description | Pros | Cons |
| --- | --- | --- | --- |
| Max softmax probability | Confidence is the largest class probability after softmax | Simple, common, easy to calibrate | Often overconfident before calibration |
| Top1/top2 margin | Confidence is the probability gap between the top two classes | Captures ambiguity between close classes | Less directly interpretable as correctness probability |
| Entropy-based confidence | Confidence is high when the predictive distribution has low entropy | Uses the full distribution | Needs careful normalization for reporting |
| Temperature-scaled confidence | Confidence after applying a validation-chosen temperature | Better calibrated if assumptions hold | Requires validation labels and tuning discipline |

Initial recommendation:

- model produces logits `z_i`
- convert logits to probabilities with softmax
- set `confidence = max_i softmax(z)_i`
- later apply temperature scaling using validation split only

This document does not implement logits, softmax, confidence computation, or
temperature scaling.

## 6. Temperature Scaling Design

Temperature scaling should be a future calibration-only transformation.

Given logits `z_i` and temperature `T > 0`, calibrated probabilities are:

```text
p_i = exp(z_i / T) / sum_j exp(z_j / T)
```

Policy:

- choose `T` using the validation split only
- choose `T` by minimizing validation negative log likelihood
- do not use test labels when choosing `T`
- do not refit or adjust `T` after seeing test results
- report `T` as a chosen validation parameter in future safe summaries
- keep `T` selection separate from feature construction

The test split may only be used after `T` is frozen.

This document does not implement temperature search, NLL optimization, or any
calibration metric.

## 7. Selective Prediction Threshold Design

The future selective prediction rule should compare calibrated confidence to a
threshold:

```text
predict if confidence >= threshold
abstain otherwise
```

Threshold selection candidates:

| Candidate | Description | Pros | Cons |
| --- | --- | --- | --- |
| Fixed abstention rate | Choose a threshold so about `r%` of validation examples abstain | Simple and stable for early synthetic experiments | Does not guarantee a target error rate |
| Target risk | Choose a threshold to stay below a validation risk target | Directly tied to risk | Can overfit if validation is small |
| Fixed confidence threshold | Use a predeclared confidence threshold | Easy to explain | May be poorly matched before calibration |

Initial recommendation:

- use a fixed allowed abstention rate policy on the validation split
- freeze the threshold before test evaluation
- do not retune the threshold on test labels
- report validation-chosen threshold and coverage safely in future work

Train/validation/test roles:

- train: fit model parameters
- validation: choose temperature and threshold
- test: final evaluation only after model, temperature, and threshold are
  frozen

This document does not implement threshold selection or abstention.

## 8. Metrics and Reporting Design

Future metrics may include:

- F1 for next revision action prediction
- accuracy as a supporting metric
- macro-F1 as a supporting metric if class imbalance matters
- ECE for calibration
- AURCC for selective prediction
- coverage-risk curve
- optional future `Coverage@Risk` or `Risk@Coverage`

Important boundary:

- this document does not compute these metrics
- these metrics are for future synthetic estimator evaluation only
- metric code should be a separate implementation step
- public reports should avoid row-level or participant-level detail
- no metric should be described as real-data readiness evidence

## 9. ECE Design

Expected calibration error compares confidence with empirical correctness.

Future ECE procedure:

1. Split predictions into confidence bins.
2. For each bin, compute average confidence.
3. For each bin, compute empirical accuracy.
4. Compute the weighted average absolute gap.

Formula:

```text
ECE = sum_b (n_b / N) * abs(acc_b - conf_b)
```

Where:

- `b` is a confidence bin
- `n_b` is the number of examples in bin `b`
- `N` is the total number of evaluated examples
- `acc_b` is empirical accuracy in bin `b`
- `conf_b` is average confidence in bin `b`

Policy:

- validation labels may guide calibration choices
- test labels may only evaluate final frozen calibration
- do not tune binning, temperature, or thresholds on test performance
- public summaries should be count-only and aggregate-only

This document does not implement ECE.

## 10. AURCC / Risk-Coverage Design

A risk-coverage curve summarizes how errors change as low-confidence examples
are abstained.

Future procedure:

1. Sort predictions by confidence from high to low.
2. Cover the highest-confidence examples first.
3. Gradually include lower-confidence examples.
4. At each coverage level, compute risk among covered predictions.
5. Summarize the curve with AURCC.

Definitions:

- coverage = covered examples / total examples
- risk = errors among covered predictions / covered predictions
- lower AURCC is generally better when using error risk

Policy:

- confidence ordering must be frozen before test evaluation
- test labels must not be used to choose a threshold
- public reporting should avoid row-level examples

This document does not implement AURCC or risk-coverage curves.

## 11. Split Policy

Split policy:

- learner-disjoint split is the default
- the same synthetic participant must not appear across train, validation, and
  test
- split assignment must not use labels, expected actions, outcomes, final text,
  or future edits
- validation split is used for temperature and threshold selection
- test split is used only for final evaluation after policies are frozen
- optional task-disjoint split is a future candidate

The estimator input validator already checks learner-disjoint boundaries for
its current fixture scope. Future estimator/calibration code must not bypass
that validation.

## 12. No-Oracle / Leakage Policy

Forbidden leakage patterns:

- `final_text` in features
- `observed_after_text` in features
- `gold_label` in features
- future episode or action fields in current inputs
- expected action aggregates in features
- label aggregates in features
- threshold tuning on test labels
- temperature tuning on test labels
- looking at test performance before freezing model, temperature, and
  threshold policy
- real data at the current stage

Calibration must not become a back door for labels to influence features.
Validation labels may choose calibration parameters, but those parameters must
be frozen before test evaluation.

## 13. Output Safety

Public docs and future public summaries should use:

- aggregate counts
- split names
- coverage counts
- reason codes
- calibration parameter names
- safe metric names after implementation exists
- content suppression flags

They must not include:

- row bodies
- raw learner text
- generated `features.jsonl` body
- generated `labels.jsonl` body
- generated `manifest.json` body
- per-participant private details
- expected action bodies
- raw GitHub Actions logs
- overclaims about model performance or real-data readiness

## 14. Relation to Estimator Input Validation Infrastructure

Selective prediction and calibration depend on the Milestone 08 estimator input
validation boundary.

Relationship:

- estimator input validator checks safe input rows
- future estimator prototype should consume only validated input bundles
- calibration design assumes labels are separated from features
- expected action remains label-side target only
- calibration must not bypass feature/label separation
- threshold selection must not bypass split policy
- output must remain safe and aggregate-only

If input validation fails, calibration and selective prediction should not run.

## 15. Implementation Roadmap

Recommended future order:

1. Step206: calibration and selective prediction fixture design.
2. Step207: estimator prototype design.
3. Step208: minimal synthetic estimator prototype implementation.
4. Step209: validation-only calibration scaffold design.
5. Step210: selective prediction evaluation design.

Keep each step narrow. Do not combine estimator training, calibration metrics,
real-data readiness, and production data pipeline work in one step.

## 16. What This Does NOT Do

This design does not:

- implement a model
- implement estimator training
- implement selective prediction
- implement calibration
- compute F1
- compute accuracy
- compute ECE
- compute AURCC
- use real data
- prove performance
- claim real-data readiness
- change sequence exporter code
- change estimator input validator code
- change audit code
- change candidate generation, OT scoring, scoring formula, tie-break
  behavior, or manifest schemas

## 17. Beginner Notes

"I do not know" is useful for a prediction system. If a model is uncertain,
abstaining can be safer than forcing a low-quality prediction.

Confidence is the model's stated certainty. Accuracy is how often the model is
actually right. Calibration checks whether those two line up.

Validation data is for choosing settings like temperature and threshold. Test
data is for the final check after those settings are frozen. If the project
tunes thresholds on test labels, the test set stops being an honest final
evaluation.

Calibration is postponed until after input validation because confidence values
are only meaningful if the inputs themselves are safe, label-separated, and
leakage-checked.

## 18. Related Documents

- [Milestone 08 learner-state estimator input validation infrastructure recap](milestone_08_learner_state_estimator_input_validation_infrastructure_recap.md)
- [Learner-state estimator input contract design](learner_state_estimator_input_contract_design.md)
- [Learner-state estimator input validation design](learner_state_estimator_input_validation_design.md)
- [Learner-state estimator input fixtures](../tests/fixtures/learner_state_estimator_input/README.md)
- [No-oracle policy](03_no_oracle_policy.md)
- [Synthetic data policy](12_synthetic_data_policy.md)
- [Public release checklist](public_release_checklist.md)
