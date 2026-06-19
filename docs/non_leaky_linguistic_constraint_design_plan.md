# Non-Leaky Linguistic Constraint Design Plan

This document is a design plan for future non-leaky linguistic diagnostic
constraints.

Step 59 implemented the first descriptive-only diagnostic constraints from this
plan. They do not change feature extraction, scoring weights, scoring formula,
tie-break policy, F1, accuracy, calibration, or learner-state estimation.

## 1. Purpose

Non-leaky linguistic constraints are intended to evolve the current linguistic
placeholder records into more interpretable diagnostic records.

The goal is to prepare candidate-fit diagnostics for linguistic categories
using no-oracle-safe local pattern features. The first version should still be
descriptive and diagnostic only.

The goal is not to decide whether a sentence is grammatically correct. The goal
is not to claim model performance. The goal is not to score candidates yet.

Initial policy:

- use prediction-time metadata and abstract local pattern features only
- do not use post-edit, final, gold, teacher, or expected-action information
- keep `violation_count = 0`
- keep `severity = "info"`
- do not add these constraints to `weighted_score`
- do not change tie-break behavior

## 2. Target Categories

Future non-leaky linguistic diagnostic constraints may cover:

- article
- number
- SVA
- tense
- preposition
- punctuation

These categories correspond to the current grammar-placeholder action taxonomy.
They are useful for L2 English writing analysis, but this plan does not turn
them into correctness judgments.

## 3. Information That May Be Used

Allowed candidate metadata:

- `action_type`
- `generation_rule`
- `action_family`
- `candidate_family_bucket`
- `no_oracle_safe` flags
- `leakage_flags`

Allowed `CandidateFeatureSet v0_3` local pattern features:

- `context_before_length_bucket`
- `cursor_at_document_start`
- `cursor_at_document_end_before`
- `selection_is_collapsed_before`
- `selection_span_length_bucket`
- `left_context_ends_with_space`
- `left_context_ends_with_punctuation`
- `left_char_class`

These fields are allowed because they are either candidate metadata or abstract
prediction-time features. They do not require post-edit text or final essay
text.

## 4. Information That Must Not Be Used

Future constraints must not use:

- raw `local_context_before` in constraint output
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
- real participant data
- real participant identifiers

The raw pre-edit context may be used only inside a tightly reviewed feature
extraction boundary that outputs abstract features. It must not be copied into
constraint output, score output, diagnostic summary, documentation, or public
fixtures.

## 5. Initial Constraint Design Candidates

These candidate IDs are future design candidates only. Do not implement them
until a separate implementation step.

### Local Context Availability

- `ARTICLE-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `NUMBER-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `SVA-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `TENSE-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `PREPOSITION-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`

Possible condition:

- candidate belongs to the matching grammar placeholder category
- `context_before_length_bucket` is not `empty`

Interpretation:

- the candidate has some pre-edit local context available for later diagnostic
  design
- it does not mean the candidate is correct

### Punctuation Awareness

- `PUNCTUATION-CANDIDATE-LEFT-PUNCTUATION-AWARE`
- `PUNCTUATION-CANDIDATE-LEFT-SPACE-AWARE`

Possible condition:

- candidate is punctuation-related
- `left_context_ends_with_punctuation` or `left_context_ends_with_space` is
  recorded

Interpretation:

- punctuation candidates can be described with adjacent abstract context
- it does not judge punctuation correctness

### Grammar Candidate Context Records

- `GRAMMAR-CANDIDATE-LEFT-CHAR-CLASS-RECORDED`
- `GRAMMAR-CANDIDATE-SELECTION-CONTEXT-RECORDED`

Possible condition:

- candidate is in a grammar-placeholder family
- `left_char_class` is present
- `selection_is_collapsed_before` and `selection_span_length_bucket` are present

Interpretation:

- the diagnostic record confirms relevant abstract context was captured
- it is not a penalty and not a correctness label

## 6. Constraints To Avoid For Now

Avoid constraints that require deeper linguistic analysis or content recovery:

- article-like token detection constraints
- noun identity constraints
- verb identity constraints
- POS tagging constraints
- dependency parsing constraints
- corrected sentence constraints
- final essay text constraints
- observed edit content as a correct answer
- expected-action-matching constraints

Reasons to defer:

- they can move too close to raw text or token identity
- they may create re-identification risk
- they may introduce no-oracle leakage
- they may accidentally use future or post-edit information
- they may invite unsupported performance claims
- the current candidates are still placeholders

## 7. Violation Count and Scoring

Initial non-leaky linguistic constraints should be descriptive diagnostics:

- `constraint_type = "descriptive"`
- `severity = "info"`
- `violation_count = 0`
- do not add to `weighted_score`
- do not change blocking behavior
- do not change deterministic tie-break behavior
- do not mix with safety blocking constraints

They may be counted by diagnostic summary tooling. Their counts are wiring and
diagnostic signals, not model performance metrics.

## 8. Privacy Policy

The constraint output should not add raw text.

Avoid storing:

- raw local context
- token text
- candidate descriptions
- proposed edit payloads
- observed edit text
- final or corrected text

Preferred output shapes:

- count
- bucket
- boolean
- enum
- named diagnostic constraint ID

Diagnostic summaries must also remain count-only and must not display text.

## 9. No-Oracle Policy

Use only prediction-time fields and no-oracle-safe abstract features.

Do not use:

- post-edit context
- future context
- final text
- gold labels
- teacher corrections
- human corrections
- expected actions

Synthetic expected actions are evaluation-only. They must not influence
candidate generation, feature extraction, constraint generation, scoring, or
ranking.

Diagnostic observation alone must not change weights or ranking. Any future
scoring use requires a separate no-oracle review, scoring policy update, and
synthetic-only tests.

## 10. Implementation-Readiness Checklist

Before implementing any future non-leaky linguistic diagnostic constraint,
confirm:

- [ ] No raw text is added to constraint output.
- [ ] No token text is added to constraint output.
- [ ] No candidate description is added to constraint output.
- [ ] No proposed edit payload is added to constraint output.
- [ ] No forbidden field is used or emitted.
- [ ] Only prediction-time fields are used.
- [ ] Expected actions are not used.
- [ ] Constraints are descriptive only.
- [ ] `violation_count = 0`.
- [ ] `severity = "info"`.
- [ ] `weighted_score` remains unchanged.
- [ ] Blocking behavior remains unchanged.
- [ ] Tie-break behavior remains unchanged.
- [ ] Synthetic E2E still passes.
- [ ] Diagnostic summary remains count-only.
- [ ] No F1, accuracy, calibration, or learner-state estimate is added.

## 11. Future Roadmap

### Step 59: Implement Non-Leaky Linguistic Diagnostic Constraints

Completed for the initial nine constraints listed in this document. They are
descriptive records only with `violation_count = 0` and `severity = "info"`.
They do not change score or rank.

### Step 60: Update Diagnostic Summary Categories If Needed

If new constraint IDs need a new summary bucket, update diagnostic summary
categories without exposing raw text.

### Step 61: Synthetic Smoke Checks

Run synthetic-only E2E and diagnostic distribution smoke checks. Do not claim
performance.

### Step 62: Design Hand-Weight Policy

Only after descriptive diagnostics are stable, design a hand-weight policy.
This should still use synthetic data only and should not use real participant
data or expected actions as scoring feedback.

### Later: Scoring Integration

Scoring integration is further downstream and requires a separate design,
tests, no-oracle review, and privacy review.

## 12. Non-Goals

This plan does not:

- implement constraints
- change feature extraction
- change diagnostic summary tooling
- change scoring
- add weights
- change tie-break policy
- add F1
- add accuracy
- add calibration
- implement learner-state estimation
- process production data
- process real participant data
- introduce real gold labels
- use expected actions as scoring feedback
