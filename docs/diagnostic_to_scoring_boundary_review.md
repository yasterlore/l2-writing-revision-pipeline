# Diagnostic-to-Scoring Boundary Review

This document defines the boundary between diagnostic information and future
scoring policy changes.

It is a design review only. It does not change scoring weights, scoring
formula, deterministic tie-break behavior, feature extraction, constraint
generation, diagnostic summary tooling, evaluation, calibration, or
learner-state estimation.

The current diagnostic outputs are useful for checking wiring and future
constraint design. They are not model performance metrics.

## 1. Purpose

The purpose of this review is to clarify:

- which diagnostic information may be considered later for scoring
- which information must never enter scoring
- which checks are required before any hand-weight policy is introduced
- why diagnostic counts must not be treated as accuracy, F1, calibration, or
  learner-state quality

Diagnostic observation alone must not change weights or ranking. Any future
connection from diagnostics to scoring requires a separate design step,
no-oracle review, documentation update, and tests showing that any scoring
behavior change is intentional.

## 2. Current Diagnostic Information

The project currently has these diagnostic layers.

### Structural Candidate Features

Structural features are candidate metadata and safety flags prepared in
`CandidateFeatureSet`.

Examples:

- `action_type`
- `generation_rule`
- `action_family`
- `candidate_family_bucket`
- `candidate_metadata_complete`
- `has_generation_rule`
- `has_action_family`
- `no_oracle_safe`
- `leakage_flags`

These fields are metadata. They are not gold labels, teacher corrections, or
performance evidence.

### Local Pattern Features v0.3

`CandidateFeatureSet v0_3` adds no-oracle-safe local pattern features as
abstract bucket, boolean, or enum fields.

Examples:

- `context_before_length_bucket`
- `cursor_at_document_start`
- `cursor_at_document_end_before`
- `selection_is_collapsed_before`
- `selection_span_length_bucket`
- `left_context_ends_with_space`
- `left_context_ends_with_punctuation`
- `left_char_class`

These fields are derived from prediction-time information. The feature output
does not store raw `local_context_before` text.

### Linguistic Placeholder Descriptive Constraints

These constraints record candidate families such as article, number, SVA,
tense, preposition, and punctuation placeholders.

They are descriptive only:

- `constraint_type = "descriptive"`
- `severity = "info"`
- `violation_count = 0`
- not included in `weighted_score`

They do not judge grammatical correctness.

### Local Pattern Diagnostic Constraints

These constraints record the v0.3 local pattern buckets, booleans, and enums in
constraint form.

Examples:

- `CONTEXT-BEFORE-*`
- `CURSOR-AT-*`
- `SELECTION-*`
- `LEFT-CONTEXT-ENDS-*`
- `LEFT-CHAR-CLASS-*`

They are diagnostic records only. They do not change score, blocking, or rank.

### Non-Leaky Linguistic Diagnostic Constraints

These constraints combine grammar-placeholder candidate metadata with abstract
local pattern features.

Examples:

- `ARTICLE-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `NUMBER-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `SVA-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `TENSE-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `PREPOSITION-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `PUNCTUATION-CANDIDATE-LEFT-PUNCTUATION-AWARE`
- `PUNCTUATION-CANDIDATE-LEFT-SPACE-AWARE`
- `GRAMMAR-CANDIDATE-LEFT-CHAR-CLASS-RECORDED`
- `GRAMMAR-CANDIDATE-SELECTION-CONTEXT-RECORDED`

They are descriptive diagnostics only. They do not decide whether a candidate
is linguistically correct.

### Diagnostic Summary Counts

The diagnostic summary tool aggregates count-only fields such as:

- total constraint sets
- total candidates
- constraint ID counts
- constraint type counts
- severity counts
- local pattern diagnostic counts
- linguistic placeholder diagnostic counts
- non-leaky linguistic diagnostic counts
- safety blocking counts

These counts are useful for wiring and distribution checks. They are not model
performance metrics.

### Synthetic E2E Summary Columns

The synthetic E2E summary collector records safe top-level columns such as:

- `diagnostic_summary_status`
- `diagnostic_total_constraints`
- `diagnostic_descriptive_constraint_count`
- `diagnostic_blocking_constraint_count`
- `diagnostic_safety_constraint_count`
- `diagnostic_local_pattern_constraint_count`
- `diagnostic_linguistic_placeholder_constraint_count`
- `diagnostic_non_leaky_linguistic_constraint_count`

These columns are count-only synthetic diagnostics. They must not be read as
accuracy, ranking quality, grammatical correctness, or real-data readiness.

## 3. Information That May Be Considered for Future Scoring

The following information may be considered in a future scoring design, but it
is not score-active now:

- `no_oracle_safe` flags
- `leakage_flags`
- `action_type`
- `generation_rule`
- `action_family`
- `candidate_family_bucket`
- local pattern bucket, boolean, and enum features
- descriptive diagnostic constraints that are no-oracle-safe
- safety blocking constraints

Using any of these for scoring later requires a separate hand-weight policy
document and tests. The future design must say whether a field is:

- a safety blocker
- a score penalty
- a score-neutral descriptive diagnostic
- excluded from scoring

## 4. Information That Must Not Be Used for Scoring

The following information must not be used in candidate generation, feature
extraction, constraint generation, scoring, tie-breaks, or weight tuning:

- raw `local_context_before` text
- `local_context_after_observed`
- `observed_after_text`
- `final_text`
- `gold_label`
- teacher correction
- human correction
- post-hoc annotation
- future edit
- future context
- expected action
- evaluation result
- exact match result
- participant identity
- real participant data
- diagnostic observation notes as direct optimization targets

Expected actions are evaluation-only synthetic fixtures. They must not flow
back into scoring or weight design.

Diagnostic notes are human review aids. They must not become direct objective
functions.

## 5. Conditions Before Any Diagnostic Information Enters Scoring

Before any diagnostic family is connected to scoring, confirm:

- no-oracle audit passes
- synthetic-only smoke checks pass
- raw text is absent from feature, constraint, score, and summary outputs
- forbidden fields are absent
- documentation explains the scoring boundary
- tests show scoring order changes are intentional
- tests show blocking behavior remains intentional
- the hand-weight rationale is written before implementation
- synthetic-only outputs are not used for performance claims
- expected actions are not used to choose or tune weights
- private validation design remains a separate later step

If any of these conditions is not met, diagnostics should remain score-neutral.

## 6. Diagnostic Constraint Classification

### Safety / Blocking

Current safety constraints:

- `NO-LEAKAGE-FLAG`
- `NO-OBSERVED-EDIT-TEXT`
- `NO-UNSAFE-CANDIDATE`

These are already score-active as safety blockers.

### Structural Descriptive

These describe candidate metadata, completeness, and family membership.

They remain score-neutral unless a future hand-weight policy explicitly says
otherwise.

### Linguistic Placeholder Descriptive

These describe grammar-placeholder candidate families.

They are score-neutral and do not judge correctness.

### Local Pattern Diagnostic Descriptive

These describe v0.3 local pattern bucket, boolean, and enum features in
constraint form.

They are score-neutral and do not reintroduce raw text.

### Non-Leaky Linguistic Diagnostic Descriptive

These describe grammar-placeholder candidates using no-oracle-safe local
pattern features.

They are score-neutral and do not judge grammatical correctness.

## 7. Checklist Before Hand-Weight Policy

Before designing or implementing any non-safety hand weights:

- [ ] The reason for changing weights is written down.
- [ ] The target constraint family is identified.
- [ ] Constraints that remain score-neutral are identified.
- [ ] Constraints that remain excluded from scoring are identified.
- [ ] Expected actions are not used for weight tuning.
- [ ] Evaluation results are not used for weight tuning.
- [ ] Synthetic smoke checks are described as wiring checks only.
- [ ] No F1, accuracy, calibration, or learner-state claim is added.
- [ ] Raw text and forbidden fields remain absent.
- [ ] Tests are planned for intentional scoring-order changes.
- [ ] Private validation design is kept as a separate later step.

## 8. Still Not Allowed

Do not:

- use diagnostic counts as a substitute for accuracy
- tune weights to synthetic expected actions
- tune weights to exact-match results
- make performance claims without a separate validation design
- use `final_text` in ranking
- use `observed_after_text` in ranking
- use teacher correction in ranking
- use post-hoc annotation in ranking
- add F1
- add accuracy
- add calibration
- implement selective prediction
- implement learner-state estimation
- process real participant data in this repository

## 9. Future Roadmap

### Step 62: Hand-Weight Policy Design Document

Define which constraint families may become score-active, which remain
descriptive, and why any hand-designed weight is interpretable and
no-oracle-safe.

See [Hand-weight policy design](hand_weight_policy_design.md) for the
follow-up design principles. That document remains design-only and does not
change current weights or ranking behavior.

### Step 63: Score-Target Constraint Family Selection Plan

Select a small set of candidate constraint families for possible scoring while
explicitly listing excluded families.

### Step 64: Implement Hand-Weight Config, If Approved

Implement only after the design, no-oracle review, and tests are ready.

### Step 65: Synthetic-Only Scoring Behavior Smoke Checks

Check deterministic score behavior on synthetic fixtures only. Do not report
performance metrics.

### Later: Private Validation Design

Design private validation separately, with institution-approved storage,
learner-disjoint splits, and no public real participant data.

## 10. Non-Goals

This document does not:

- implement scoring changes
- change feature extraction
- change constraint generation
- change diagnostic summary tooling
- change weights
- change tie-breaks
- introduce evaluation metrics
- implement learner-state estimation
- authorize real participant data processing
