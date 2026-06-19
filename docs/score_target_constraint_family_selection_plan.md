# Score-Target Constraint Family Selection Plan

This document narrows which constraint families may be considered for future
score-active hand-weight policy.

It is a design plan only. It does not change scoring weights, scoring formula,
deterministic tie-break behavior, feature extraction, constraint generation,
diagnostic summary tooling, evaluation, calibration, or learner-state
estimation.

This is not performance evaluation. It does not claim F1, accuracy,
calibration, grammatical correctness, ranking quality, or learner-state
quality.

## 1. Purpose

The purpose of this selection plan is to choose a narrow starting point before
any hand-weight config is designed or implemented.

This document answers:

- which constraint families are already score-active
- which families may be future score-active candidates
- which families should remain score-neutral for now
- which information must never become score-active
- what tests are required before ranking behavior changes

It does not assign weights. It does not change current behavior.

Before any future hand-weight config is connected to scoring, read
[Default-unchanged config support design](default_unchanged_config_support_design.md).
For the Milestone 03 follow-up review, read
[Score-active family selection revisit](score_active_family_selection_revisit.md).

## 2. Current Constraint Families

### Safety Blocking Constraints

Current examples:

- `NO-LEAKAGE-FLAG`
- `NO-OBSERVED-EDIT-TEXT`
- `NO-UNSAFE-CANDIDATE`

Current status:

- score-active
- blocking
- very high prototype weight

Purpose:

- prevent unsafe or leakage-bearing candidates from ranking as acceptable

### Structural Descriptive Constraints

Current examples:

- metadata completeness records
- generation-rule presence
- action-family presence
- candidate-family bucket records
- hold/local/grammar/placeholder family records

Current status:

- descriptive
- score-neutral

Purpose:

- make candidate metadata visible for diagnostics and future design

### Linguistic Placeholder Descriptive Constraints

Current examples:

- article placeholder candidate records
- number placeholder candidate records
- SVA placeholder candidate records
- tense placeholder candidate records
- preposition placeholder candidate records
- punctuation placeholder candidate records

Current status:

- descriptive
- score-neutral

Purpose:

- record candidate taxonomy, not grammatical correctness

### Local Pattern Diagnostic Descriptive Constraints

Current examples:

- `CONTEXT-BEFORE-*`
- `CURSOR-AT-*`
- `SELECTION-*`
- `LEFT-CONTEXT-ENDS-*`
- `LEFT-CHAR-CLASS-*`

Current status:

- descriptive
- score-neutral

Purpose:

- record abstract v0.3 local pattern features without raw text

### Non-Leaky Linguistic Diagnostic Descriptive Constraints

Current examples:

- `ARTICLE-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `NUMBER-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `SVA-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `TENSE-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `PREPOSITION-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `PUNCTUATION-CANDIDATE-LEFT-PUNCTUATION-AWARE`
- `PUNCTUATION-CANDIDATE-LEFT-SPACE-AWARE`
- `GRAMMAR-CANDIDATE-LEFT-CHAR-CLASS-RECORDED`
- `GRAMMAR-CANDIDATE-SELECTION-CONTEXT-RECORDED`

Current status:

- descriptive
- score-neutral

Purpose:

- record no-oracle-safe diagnostic context for grammar-placeholder candidates

### Diagnostic Summary Counts

Current status:

- summary-only
- score-neutral

Purpose:

- inspect synthetic diagnostic wiring and count distributions

### Evaluation-Related Expected Actions

Current status:

- evaluation-only
- never score-active

Purpose:

- synthetic wiring checks after scoring, not candidate generation or scoring
  feedback

## 3. First Score-Active Candidates

The initial selection should be conservative.

### Keep Safety Blocking Constraints Score-Active

Recommendation:

- keep current safety blocking constraints score-active and blocking

Meaning:

- safety and leakage policy stays ahead of linguistic preference
- unsafe candidates remain blocked

No change is proposed here.

### Metadata Completeness: Candidate With Caution

Recommendation:

- possible future candidate, but not yet score-active

Meaning if score-active later:

- incomplete or missing candidate metadata could receive a small penalty
- scoring could prefer candidates whose interpretation metadata is complete

Risks:

- metadata completeness is not linguistic quality
- metadata penalties can hide upstream candidate-generation problems
- missing metadata should often trigger diagnostics, not ranking changes

Required before use:

- separate rationale
- explicit score-target family list
- tests showing intentional ranking changes

### Non-Leaky Linguistic Diagnostics: Keep Neutral For Now

Recommendation:

- remain score-neutral for now

Meaning if score-active later:

- no-oracle-safe grammar diagnostics could become small preferences or
  penalties

Risks:

- current constraints do not judge grammatical correctness
- premature weights could imply unsupported linguistic validity

Required before use:

- stronger review
- clear rationale
- no performance claims

### Local Pattern Diagnostics: Keep Neutral For Now

Recommendation:

- remain score-neutral for now

Meaning if score-active later:

- abstract local context patterns could affect candidate ranking

Risks:

- local patterns are not correctness labels
- fixture-specific distributions could overfit ranking behavior

Required before use:

- score-target family selection update
- ranking behavior diff tests

### Placeholder Family Constraints: Keep Neutral For Now

Recommendation:

- remain score-neutral for now

Meaning if score-active later:

- broad candidate families could receive default preferences

Risks:

- broad family preferences may dominate candidate diversity
- placeholder candidates are not full corrections

Required before use:

- explicit family-level rationale
- tests showing deterministic and intentional behavior

## 4. Families To Keep Score-Neutral For Now

Keep these score-neutral in the initial hand-weight design:

- structural descriptive constraints
- linguistic placeholder descriptive constraints
- local pattern diagnostic constraints
- non-leaky linguistic diagnostic constraints
- diagnostic summary counts
- observation note labels
- synthetic expected action
- evaluation result
- exact match result

Score-neutral means:

- `weighted_score` should not include these families
- ranking should not change because of these families
- diagnostics may still be summarized count-only

## 5. Families Requiring Additional Review Before Score Use

### Metadata Completeness

Possible meaning:

- prefer candidates whose metadata is complete and interpretable

Danger:

- turns schema completeness into a quality signal
- may mask upstream bugs

Additional review needed:

- decide whether incompleteness should block, warn, or mildly penalize

### No-Oracle Safe Flags

Possible meaning:

- keep unsafe candidates blocked or penalized

Danger:

- weakening safety policy could allow leakage-bearing candidates to compete

Additional review needed:

- safety and privacy review before any change

### Leakage Flags

Possible meaning:

- continue treating leakage as blocking

Danger:

- treating leakage as a small ordinary penalty would be unsafe

Additional review needed:

- keep as blocking unless a separate privacy review says otherwise

### Local Pattern Diagnostics

Possible meaning:

- use abstract context buckets and booleans as small preferences

Danger:

- can overfit to synthetic fixture shapes
- can be mistaken for correctness

Additional review needed:

- prove raw text remains absent
- define expected ranking changes before implementation

### Non-Leaky Linguistic Diagnostics

Possible meaning:

- use grammar-placeholder diagnostics as small hand-designed preferences

Danger:

- current diagnostics do not know whether grammar is correct
- premature use can imply unsupported linguistic claims

Additional review needed:

- separate linguistic rationale
- no-oracle review
- synthetic smoke only, no performance claim

## 6. Information That Must Never Be Score-Active

Do not make these score-active:

- raw text
- raw `local_context_before`
- `local_context_after_observed`
- `final_text`
- `observed_after_text`
- `gold_label`
- expected action
- evaluation result
- exact match result
- real participant metadata
- diagnostic summary counts as direct weights
- observation note labels
- teacher correction
- human correction
- post-hoc annotation
- future edit
- future context

These are either leakage risks, evaluation-only signals, privacy-sensitive
fields, or human notes that must not become optimization targets.

## 7. Initial Selection Proposal

### Phase 0: Current Behavior

Keep current behavior:

- safety blocking constraints remain score-active
- descriptive constraints remain score-neutral
- diagnostic summaries remain count-only
- deterministic tie-break remains unchanged

This is the current recommended baseline.

### Phase 1 Candidate: Metadata Completeness Only After Rationale

Possible later addition:

- maintain safety blocking
- optionally add a very small metadata completeness penalty or preference

Only proceed if:

- a separate rationale exists
- tests show intentional ranking changes
- no-oracle and privacy checks pass

### Phase 2 Later: Non-Leaky Linguistic Diagnostics

Possible later addition:

- consider non-leaky linguistic diagnostics only after stronger review

Do not proceed until:

- the constraint family has a clear interpretation
- raw text remains absent
- expected actions are not used as feedback
- synthetic smoke checks remain non-performance checks

### Phase 3 Later: Private Validation Design

Private validation design is a separate later step.

It must not happen inside the public repository and must not use public CI.

## 8. Selection Criteria

A future score-active family must be:

- no-oracle safe
- interpretable
- testable
- not derived from expected action
- not directly optimized from diagnostic counts
- not dependent on raw text
- not dependent on post-edit, final, or gold information
- able to produce explainable ranking changes
- limited to a small number of active families

If a family fails any criterion, keep it score-neutral.

## 9. Tests Required Before Implementation

Before implementing any new score-active family, add or update tests for:

- ranking behavior diff
- blocked candidate behavior unchanged
- explicit score-active family list
- no forbidden fields in feature, constraint, score, or summary output
- synthetic E2E smoke
- diagnostic summary remains count-only
- no F1, accuracy, calibration, or learner-state fields
- expected actions do not flow into scoring

Tests must demonstrate intentional behavior, not performance.

## 10. Still Not Allowed

Do not implement:

- actual weight changes
- hidden tuning
- expected-action fitting
- real-data tuning
- F1
- accuracy
- calibration
- learner-state estimation
- private validation inside the public repository
- real gold label workflow

Do not use synthetic expected actions as scoring feedback.

## 11. Future Roadmap

### Step 64: Hand-Weight Config Schema Plan

Design a config representation for future hand weights without changing
defaults.

See [Hand-weight config schema plan](hand_weight_config_schema_plan.md) for the
proposed schema fields, validation policy, and default-behavior constraints.

### Step 65: Implement Config File Support Without Changing Defaults

Add configuration plumbing only if approved and keep current scoring behavior
unchanged by default.

### Step 66: Synthetic Ranking Behavior Diff Smoke Tests

Add synthetic-only tests that show score/rank differences when an explicit
future config changes behavior.

Do not report performance metrics.

### Step 67: Private Validation Design Later

Design private validation separately after scoring semantics are stable.

## 12. Non-Goals

This document does not:

- change weights
- change scoring formula
- change tie-break policy
- change constraint generation
- change diagnostic summary tooling
- implement hand-weight config
- implement performance evaluation
- implement learner-state estimation
- authorize real participant data processing
