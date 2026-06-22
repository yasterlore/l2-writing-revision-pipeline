# Frozen Selective Prediction Policy Schema Design

This document designs a future schema for
`frozen_selective_prediction_policy.json`, the metadata artifact that a future
selective prediction / calibration scaffold may create after validation-only
temperature and threshold selection.

It is design documentation only. It does not implement calibration, selective
prediction, a learner-state estimator, estimator training, a model, metric
computation, release-quality changes, workflow changes, Makefile changes,
fixture changes, or production data handling. It does not create a frozen
policy artifact file. It is not a performance evaluation and is not a
real-data readiness claim.

The artifact described here is synthetic-only and metadata-only. Public docs
must not include raw JSONL rows, prediction row bodies, label row bodies,
calibration policy bodies, split metadata bodies, logits/probability dumps,
generated feature/label/manifest bodies, raw GitHub Actions logs, raw learner
text, private paths, or real participant data.

## 1. Purpose

The purpose of this document is to define the future schema expectations for a
frozen selective prediction policy artifact before scaffold implementation
begins.

This design covers:

- artifact role and recommended filename
- schema versioning
- required fields
- optional fields
- forbidden fields
- temperature, threshold, and confidence metadata
- validation-only tuning provenance
- safe validation input summaries
- split policy and safety review fields
- future artifact validation checks

This document does not create `frozen_selective_prediction_policy.json` and
does not compute calibration, F1, accuracy, ECE, AURCC, coverage-risk curves,
or model performance.

## 2. One-Sentence Summary

A frozen selective prediction policy artifact is a synthetic-only metadata
artifact that records temperature and threshold policy chosen from the
validation split only, freezes that policy before test evaluation, and keeps
the provenance needed for future safe reporting without storing raw rows,
labels, logits dumps, or test-derived tuning traces.

## 3. Artifact Role

The future artifact should serve these roles:

- output of the future calibration / selective prediction scaffold
- frozen policy input for a later test evaluation step
- provenance record for validation-only temperature selection
- provenance record for validation-only threshold / abstention selection
- stable description of confidence and abstention behavior
- safe trace of what a future report used
- metadata-only bridge between scaffold and future evaluation

The artifact is not:

- a storage location for prediction rows
- a storage location for label rows
- a logits/probability archive
- a calibration policy body dump
- a split metadata body dump
- a metric report
- a performance certificate
- real-data readiness evidence

## 4. Proposed Filename

Filename candidates:

| Candidate | Assessment |
| --- | --- |
| `frozen_selective_prediction_policy.json` | Recommended; explicit that the policy is frozen and belongs to selective prediction |
| `selective_prediction_frozen_policy.json` | Clear but less consistent with the scaffold wording |
| `calibration_frozen_policy.json` | Too narrow; threshold / abstention policy is also included |
| `frozen_calibration_policy.json` | Could be confused with the input `calibration_policy.json` fixture |

Recommended filename:

- `frozen_selective_prediction_policy.json`

Reason:

- names the frozen status first
- names the selective prediction policy scope
- avoids confusion with source `calibration_policy.json`
- leaves room for both temperature and threshold metadata

## 5. Schema Versioning

Required schema version field:

- `policy_schema_version`

Initial version candidate:

- `frozen_selective_prediction_policy_schema_v0_1`

Schema version policy:

- every artifact must include an explicit `policy_schema_version`
- future validators should fail closed on unknown schema versions
- backward compatibility should be explicit, not inferred
- schema changes that alter required fields should create a new version
- schema changes that only add optional safe metadata may remain compatible if
  a future validator explicitly allows them

Unknown or missing schema version should be treated as an artifact validation
failure, not as a warning.

## 6. Required Fields

Recommended required top-level fields:

| Field | Required | Purpose |
| --- | --- | --- |
| `policy_schema_version` | yes | Identifies the artifact schema |
| `policy_id` | yes | Stable synthetic-safe identifier for this frozen policy |
| `source_fixture_id` | yes | Safe fixture/case identifier, not a private path |
| `created_by_step` | yes | Step or scaffold stage that created the artifact |
| `synthetic_only` | yes | Must be true for the current project stage |
| `content_suppressed` | yes | Must be true for safe reporting |
| `no_raw_rows` | yes | Must be true; raw rows are not stored |
| `no_oracle_checked` | yes | Records no-oracle validation status |
| `test_tuning_forbidden` | yes | Must be true |
| `confidence_definition` | yes | Declares how confidence is interpreted |
| `confidence_is_calibrated` | yes | States whether confidence has temperature applied |
| `temperature` | yes | Numeric value or identity value |
| `temperature_source_split` | yes | Must be `validation` or an explicit identity sentinel |
| `temperature_selection_method` | yes | Describes how temperature was selected |
| `threshold` | yes | Numeric abstention threshold |
| `threshold_source_split` | yes | Must be `validation` |
| `threshold_selection_method` | yes | Describes how threshold was selected |
| `allowed_abstention_rate` | yes | Safe numeric policy parameter |
| `label_space_version` | yes | Declares the action-family label space |
| `split_policy_summary` | yes | Safe metadata about split policy |
| `validation_input_summary` | yes | Count-only validation input metadata |
| `safety_review` | yes | Safe booleans for artifact boundary checks |

The required fields are intentionally metadata-heavy and row-light. They
should make tuning provenance auditable without exposing prediction or label
bodies.

## 7. Optional Fields

Optional safe fields:

| Field | Use With Care |
| --- | --- |
| `calibration_objective` | May state a method such as validation NLL minimization, but should not include row-level losses |
| `validation_loss_summary` | If used, must be aggregate-only and clearly not a final performance claim |
| `candidate_thresholds_count` | Count-only; no threshold candidate dump |
| `covered_validation_count` | Count-only validation coverage metadata |
| `abstained_validation_count` | Count-only validation abstention metadata |
| `policy_notes` | Short public-safe notes, no row content or private paths |
| `artifact_manifest` | Safe manifest metadata, no generated body dumps |

Optional fields should be excluded until they have a clear use. Adding a field
because it is convenient is not enough; it should support reproducibility,
validation, or safe reporting.

Optional aggregate fields must not be described as final model performance.

## 8. Forbidden Fields

The artifact must not contain:

- raw prediction rows
- raw label rows
- logits dumps
- probability dumps
- calibration policy body dumps
- split metadata body dumps
- expected action body
- raw learner text
- `final_text`
- `observed_after_text`
- `gold_label`
- teacher or human correction content
- real participant IDs
- test label tuning trace
- test-derived threshold
- test-derived temperature
- F1 as a final performance claim
- accuracy as a final performance claim
- ECE as a final performance claim
- AURCC as a final performance claim
- private absolute paths
- generated `features.jsonl` body
- generated `labels.jsonl` body
- generated `manifest.json` body

Future validation should scan recursively for forbidden field names and unsafe
path-like values.

## 9. Temperature Field Design

Temperature fields:

- `temperature`
- `temperature_source_split`
- `temperature_selection_method`

Design rules:

- `temperature` should be numeric
- `temperature` should be finite and positive
- `temperature_source_split` must be `validation` when temperature scaling is
  selected from data
- test split cannot be the temperature source
- temperature must be chosen before test evaluation
- `temperature_selection_method` may be `validation_nll_minimization` in a
  future implementation
- if no temperature scaling is used, represent that explicitly with
  `temperature: 1.0` and `temperature_selection_method: none_identity`
- identity temperature should not imply calibration quality

This document does not implement temperature scaling and does not compute
validation NLL.

## 10. Threshold Field Design

Threshold fields:

- `threshold`
- `threshold_source_split`
- `threshold_selection_method`
- `allowed_abstention_rate`

Design rules:

- `threshold` should be numeric
- `threshold` should be within the confidence range, initially `0.0` to `1.0`
- `threshold_source_split` must be `validation`
- test split cannot be the threshold source
- threshold must be chosen before test evaluation
- initial threshold selection method candidate:
  `fixed_abstention_rate`
- `allowed_abstention_rate` should be numeric and within `0.0` to `1.0`
- a threshold derived from test labels is forbidden

This document does not implement threshold selection, abstention, coverage,
risk, or evaluation metrics.

## 11. Confidence Definition Design

Initial confidence definition candidate:

- `max_softmax_probability`

Future candidates:

- top-1 / top-2 margin
- entropy-derived confidence
- calibrated confidence after temperature scaling

Design rules:

- `confidence_definition` must match the prediction fixture and scaffold
  interpretation
- whether confidence is calibrated must be explicit
- confidence source must not include labels, expected actions, future actions,
  or test outcomes
- confidence fields should not include raw logits/probability dumps in the
  frozen artifact

The artifact may name the confidence definition, but should not store row-level
confidence traces.

## 12. Validation Input Summary Design

`validation_input_summary` should be safe and count-only.

Candidate fields:

- `fixture_case_id`
- `validation_prediction_count`
- `validation_label_count`
- `validation_participant_count`
- `split_counts`
- `prediction_label_join_complete`
- `content_suppressed`
- `no_raw_rows`

Forbidden content:

- prediction row bodies
- label row bodies
- expected action body
- logits/probability dumps
- private paths
- raw learner text

This summary should help future readers understand what validation split data
was used without exposing the data itself.

## 13. Split Policy Summary

`split_policy_summary` should state:

- learner-disjoint split: yes/no
- validation split used for tuning: yes
- test split used for tuning: no
- test evaluation: future only
- label-dependent split: no
- outcome-dependent split: no

The summary should be metadata-only. It should not copy `split_metadata.json`
or list participant-level private details.

## 14. Safety Review Fields

`safety_review` should include safe booleans such as:

- `synthetic_only`
- `no_oracle_checked`
- `test_tuning_forbidden`
- `no_raw_rows`
- `content_suppressed`
- `no_private_paths`
- `prediction_label_separated`
- `expected_action_not_in_prediction_rows`
- `future_leakage_checked`
- `raw_learner_text_absent`
- `performance_claims_absent`

These fields should summarize checks, not embed raw evidence. If a future
check fails, the artifact should not be considered valid.

## 15. Future Artifact Validation Checks

A future frozen policy validator should check:

- known `policy_schema_version`
- required fields are present
- no unknown required-field substitutions
- `synthetic_only` is true
- `content_suppressed` is true
- `no_raw_rows` is true
- `test_tuning_forbidden` is true
- `no_oracle_checked` is true
- `temperature` is finite and positive
- `temperature_source_split` is `validation` or identity-only sentinel
- `threshold` is numeric and within the allowed confidence range
- `threshold_source_split` is `validation`
- `allowed_abstention_rate` is within `0.0` to `1.0`
- confidence definition is allowed
- split policy summary is safe
- safety review fields are safe booleans
- no forbidden fields appear recursively
- no private absolute paths appear
- no test-derived temperature or threshold is recorded
- no performance claims are embedded as final evaluation results

Validation should fail closed and report safe reason codes only.

## 16. Relation To Selective Prediction Validator And Scaffold

Relationship:

- selective prediction validator validates prediction / label / split / policy
  fixture inputs
- scaffold may create a frozen policy only after validator pass
- frozen policy records the scaffold's validation-only choices
- future test evaluation consumes the frozen policy
- frozen policy should not bypass the validator
- frozen policy is not a metric report
- frozen policy is not an estimator artifact

The artifact should preserve the same safety posture as the validator and CLI:
safe metadata only, no row bodies, no logits dumps, no label bodies, no
private paths, and no real data.

## 17. Output Safety

Public docs should use field tables and bullet lists instead of full artifact
body examples.

If a future example is needed, it should be minimal, synthetic-safe, and
contain only schema/field-shape illustration. It should not contain:

- full JSON body from an actual run
- raw rows
- logits/probability dumps
- label bodies
- policy or split body dumps
- expected action body
- raw learner text
- private paths
- performance claims

For this design step, no example artifact body is included.

## 18. Implementation Roadmap

Recommended future order:

1. Step221: frozen policy fixture design.
2. Step222: frozen policy validator design.
3. Step223: minimal frozen policy validator implementation.
4. Step224: calibration scaffold fixture design.
5. Step225: minimal validation-only calibration scaffold implementation.
6. Step226: threshold policy scaffold implementation.

Keep each step narrow. Do not combine artifact schema, validator
implementation, calibration scaffold, estimator training, metric computation,
release-quality integration, and real-data readiness in one step.

## 19. What This Does Not Prove

This schema design does not prove:

- model performance
- calibration quality
- selective prediction correctness
- learner-state estimator correctness
- real-data readiness
- production data collection validity
- F1 evidence
- accuracy evidence
- ECE evidence
- AURCC evidence
- scoring model improvement

It only defines how a future frozen policy artifact should safely record
validation-only policy choices.

## 20. Beginner Notes

A frozen policy is a saved decision about how confidence should be adjusted
and when the system should abstain.

Temperature changes probability confidence. Threshold decides when confidence
is too low and the system should not make a prediction. Both decisions must be
chosen from validation data only, because validation is the split used for
choosing settings.

The test split is different. It should be held back until after the policy is
frozen. If the project chooses temperature or threshold from test labels, the
test result stops being an honest final check.

Raw rows do not belong in the frozen policy because the policy only needs to
record the decision and its safe provenance. Keeping raw prediction and label
rows out of the artifact reduces leakage risk and keeps public records safe.

Artifact success is not performance evidence. It only means the future policy
metadata follows the schema and preserves validation-only, no-oracle, and
safe-output boundaries.

## 21. Related Documents

- [Selective prediction and calibration design](selective_prediction_calibration_design.md)
- [Selective prediction and calibration scaffold design](selective_prediction_calibration_scaffold_design.md)
- [Selective prediction and calibration validation design](selective_prediction_calibration_validation_design.md)
- [Selective prediction and calibration fixture design](selective_prediction_calibration_fixture_design.md)
- [Milestone 09 selective prediction validation infrastructure recap](milestone_09_selective_prediction_validation_infrastructure_recap.md)
- [Selective prediction fixtures](../tests/fixtures/learner_state_selective_prediction/README.md)
- [No-oracle policy](03_no_oracle_policy.md)
- [Synthetic data policy](12_synthetic_data_policy.md)
- [Public release checklist](public_release_checklist.md)
