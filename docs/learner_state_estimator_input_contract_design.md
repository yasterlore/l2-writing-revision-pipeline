# Learner-State Estimator Input Contract Design

This document defines the future input contract for a learner-state estimator.
It connects audited learner-state sequence exporter outputs to a possible
estimator input bundle while preserving the feature/label separation and
no-oracle boundary established in Milestones 06 and 07.

This is design documentation only. It does not implement a learner-state
estimator, estimator training code, selective prediction, calibration, a new
model, a new metric, or real-data handling. It is not performance evaluation
and it is not a real-data readiness claim.

## 1. Purpose

The purpose of this contract is to define:

- which files a future learner-state estimator may read
- how feature rows, label rows, and manifest metadata remain separated
- how safe join keys and sequence grouping should work
- how split handling should avoid learner, task, label, and future leakage
- what validation should fail closed before any estimator training or
  evaluation code is allowed to run
- how public output remains count-only and body-free

The contract is intentionally narrow. It assumes synthetic-only exporter
outputs that have already passed `learner_state.sequence_audit`.

## 2. One-Sentence Summary

A learner-state estimator should read audited `features.jsonl`, separated
`labels.jsonl`, and count-only `manifest.json`, then construct
participant/session/task/episode sequence input bundles for future
training/evaluation without exposing labels to feature construction or using
future information.

## 3. Input Files

Future estimator input should be built from these files:

| File | Role | Public safety rule |
| --- | --- | --- |
| `features.jsonl` | Estimator-visible feature rows, already audited for forbidden fields and future leakage | Do not print row bodies |
| `labels.jsonl` | Separated synthetic expected-action labels used only as training/evaluation targets | Do not print label bodies or expected-action bodies |
| `manifest.json` | Count-only metadata about schema versions, row counts, synthetic-only status, content suppression, and split counts | Do not dump the full manifest body into public docs or logs |
| `summary.json` | Optional count-only exporter summary if generated | Treat as safe summary only after review |
| split metadata | Optional only if not already represented safely in the manifest | Must be count-only and label-independent |

The estimator input layer should not accept generated output files that have
not passed the existing learner-state sequence audit.

## 4. Feature Handling

Future estimator-visible features may include:

- synthetic `participant_id`, `session_id`, and `task_id`
- `micro_episode_id`
- `episode_order_index`
- safe bucket or class features derived from no-oracle micro-episode views
- candidate-family score summaries
- top-ranked candidate family
- blocked candidate count
- diagnostic count features
- past-only rolling window features

Feature rows must not include:

- `expected_action`
- `expected_action_family`
- `gold_label`
- `final_text`
- `observed_after_text`
- raw learner text
- future edit or future episode fields
- teacher or human correction fields
- final essay outcome fields

Feature handling must be deterministic and label-blind. If a future loader
finds a forbidden field in a feature row, it should fail closed with a safe
reason code rather than silently dropping the field.

## 5. Label Handling

Labels remain separated from features.

- The current-stage label source is synthetic only.
- Synthetic expected action is a training/evaluation target only.
- Labels may be joined to features by safe keys during supervised training or
  evaluation.
- Labels must not feed back into feature construction.
- Labels must not feed back into candidate generation, scoring, ranking,
  split assignment, or calibration feature construction.
- Expected action is not scoring feedback.

The label reader should preserve the distinction between "the label exists for
evaluation/training" and "the model may see this signal as input." Only the
former is allowed.

## 6. Join Key Contract

The safe join key set is:

- `participant_id`
- `session_id`
- `task_id`
- `micro_episode_id`
- `episode_order_index`

Join keys must not encode labels, outcomes, raw text, or real participant
identity. Raw text hashes should not be used unless they receive a separate
privacy and no-oracle review.

Future implementation should fail closed when:

- a feature row has no matching label row in a supervised dataset
- a label row has no matching feature row
- duplicate join keys appear in the same split
- join keys disagree on `episode_order_index`
- join keys imply a participant crossing train/validation/test boundaries

Failure output should include safe counts and reason codes only.

## 7. Sequence Grouping Contract

Estimator sequence construction should:

- group rows by `participant_id`, `session_id`, and `task_id`
- order rows by `episode_order_index`
- reset sequence state at participant, session, and task boundaries
- avoid any future episode access when constructing the current episode input
- preserve learner-disjoint split boundaries during batching
- make task-boundary behavior explicit

Past-window features may summarize only prior rows within the current allowed
sequence boundary. They must not use final task length if that value is
future-derived.

## 8. Split Handling

Learner-disjoint split is the default contract.

- The same participant must not appear across train, validation, and test.
- Split assignment must not use labels, expected actions, outcomes, or final
  task quality.
- Optional task-disjoint split is a future candidate, not part of the minimal
  contract.
- Manifest split counts should remain count-only.
- A split leakage check should pass before any training or evaluation run.

If split metadata is absent, a future loader should either fail closed or
require an explicit synthetic-only split policy. It should not infer a split
from labels or outcomes.

## 9. No-Oracle / Leakage Policy

The estimator input contract inherits the no-oracle boundary:

- no final text in features
- no observed-after text in features
- no gold labels in features
- no future edits or future episodes in current-row inputs
- no label aggregates in features
- no expected-action aggregates in features
- no calibration using test labels
- no threshold tuning on the test set
- no real participant data at this stage

Validation should treat leakage as a safety violation, not as a recoverable
warning.

## 10. Estimator Input Bundle Design

Future implementation may define the following bundle types. These names are
design placeholders, not implemented APIs.

| Bundle | Responsibility | Field-level contract |
| --- | --- | --- |
| `EstimatorFeatureRow` | One audited feature row visible to the estimator | safe join keys, episode order, safe feature fields, schema version |
| `EstimatorLabelRow` | One separated target row | safe join keys, synthetic expected-action target, label schema version, evaluation-only marker |
| `EstimatorSequence` | Ordered rows for one participant/session/task sequence | grouping keys, ordered feature rows, optional joined labels for supervised phases, boundary metadata |
| `EstimatorSplitBundle` | Split-specific sequence collections | split name, participant count, sequence count, row counts, learner-disjoint validation status |
| `EstimatorManifest` | Count-only metadata used for validation | schema versions, synthetic-only status, content suppression, row counts, split counts, audit status |

The bundle layer should keep raw rows out of public output. Debugging should use
safe row counts, schema names, and reason codes.

## 11. Minimal Estimator Dataset Candidate

The first synthetic-only estimator input smoke candidate can be generated from:

- `minimal_single_participant`
- `past_window_boundary_reset`

These generated outputs are useful for input contract smoke tests because they
exercise basic joins, row counts, audit status, and task-boundary reset
behavior. They are not sufficient for real training, model selection, or
performance claims.

The minimal candidate must not be described as evidence of estimator quality,
real-data readiness, or production data collection readiness.

## 12. Relation to Selective Prediction / Calibration

Selective prediction and calibration are later stages.

- Confidence scores, abstention thresholds, ECE, AURCC, and calibration metrics
  are not implemented by this contract.
- Validation labels may be used only in a validation phase.
- Test labels must remain untouched until final evaluation.
- Threshold tuning must not use test labels.
- Calibration feature construction must not consume labels as input features.

A separate calibration design should define how confidence, validation labels,
test labels, and public reporting are handled before any implementation.

## 13. Output Safety

Future estimator input validation should emit only:

- safe status
- row counts
- sequence counts
- split counts
- reason codes
- schema version names
- content suppression status
- synthetic-only status

It must not emit:

- feature row bodies
- label row bodies
- generated `features.jsonl` body
- generated `labels.jsonl` body
- generated `manifest.json` body
- raw learner text
- private absolute paths
- expected-action bodies
- performance metrics during contract validation

## 14. Future Validation Checks

Future input validation should cover:

- feature/label join completeness
- forbidden feature fields
- split leakage
- sequence ordering
- participant/session/task boundary reset
- label-feature separation
- schema version compatibility
- manifest count consistency
- synthetic-only and content-suppressed flags
- safe output checks for failure messages

These checks should fail closed. A validation failure should not leave a caller
with a dataset that appears training-ready.

## 15. Future Implementation Roadmap

Recommended order:

1. Step192: estimator input contract fixture design.
2. Step193: create initial estimator input fixtures.
3. Step194: estimator input validation design.
4. Step195: minimal estimator input loader implementation.
5. Step196: loader tests with exporter outputs.
6. Step197: selective prediction / calibration design.
7. Step198: estimator prototype design.

The roadmap intentionally keeps validation and loader work separate from model
training and metrics.

Step192 adds the
[learner-state estimator input fixture design](learner_state_estimator_input_fixture_design.md)
for future synthetic exported-shape fixtures and expected validation result
contracts. It does not create fixture files or implement a loader.

## 16. Relation to Existing Pipeline

This contract sits after the learner-state sequence exporter and audit:

- `sequence_exporter` produces separated feature, label, and manifest outputs.
- `learner_state.sequence_audit` checks exported outputs before use.
- Synthetic expected-action sources remain label/evaluation side only.
- Makefile and release-quality wrapper checks provide operational smoke
  coverage for synthetic exporter outputs.
- Milestone 06 established the audit boundary.
- Milestone 07 established the exporter boundary.

This contract does not modify candidate generation, OT scoring, tie-breaks,
diagnostics, manifest schema, workflow configuration, or release-quality
orchestration.

## 17. What This Does Not Do

This design does not:

- train a learner-state estimator
- implement estimator training code
- implement selective prediction or calibration
- evaluate F1, accuracy, calibration, ECE, or AURCC
- implement a new model or metric
- use real participant data
- prove model validity
- claim production readiness
- claim data-collection readiness

## 18. Beginner Notes

An estimator input contract is the rulebook for what a future learner-state
model is allowed to read. It exists before the model so the model cannot
accidentally learn from labels, future edits, raw text, or other forbidden
signals.

The exporter creates audited feature, label, and manifest files. The input
contract explains how a future estimator may consume those files safely.

Features are the signals the estimator may see as input. Labels are the target
answers used only for training or evaluation phases. Keeping them separate
prevents expected actions from becoming scoring feedback.

Split leakage happens when information crosses train, validation, or test
boundaries. A learner-disjoint split prevents the same synthetic participant
from appearing in multiple splits.

Calibration is later because confidence thresholds and validation/test label
use need their own safety rules. Adding calibration too early would mix input
loading, model behavior, and metric interpretation.

## 19. Related Documents

- [Milestone 06 learner-state audit infrastructure recap](milestone_06_learner_state_audit_infrastructure_recap.md)
- [Milestone 07 learner-state sequence exporter infrastructure recap](milestone_07_learner_state_sequence_exporter_infrastructure_recap.md)
- [Learner-state sequence exporter design](learner_state_sequence_exporter_design.md)
- [Learner-state sequence schema design](learner_state_sequence_schema_design.md)
- [Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
- [Learner-state estimator input fixture design](learner_state_estimator_input_fixture_design.md)
- [Learner-state input representation design](learner_state_input_representation_design.md)
- [Synthetic learner-state sequence dataset design](synthetic_learner_state_sequence_dataset_design.md)
- [Public release checklist](public_release_checklist.md)
