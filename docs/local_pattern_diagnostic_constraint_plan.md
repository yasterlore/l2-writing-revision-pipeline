# Local Pattern Diagnostic Constraint Plan

This document plans descriptive diagnostic constraints derived from
`CandidateFeatureSet v0_3` local pattern features.

It is a design document only. It does not implement constraints, change
feature extraction, change scoring, add weights, add F1, add accuracy, add
calibration, or implement learner-state estimation.

## 1. Purpose

Local pattern diagnostic constraints will observe the local pattern features
that were added in `candidate_feature_schema_v0_3`.

The goal is to make the feature state easier to inspect in the existing
`ConstraintViolationSet` format.

These constraints are not grammar-correctness judgments. They do not decide
whether a revision is right or wrong. They do not change ranking behavior, and
they are not added to `weighted_score`.

Initial use cases:

- record whether a candidate was generated near the document start or end
- record whether the pre-edit selection was collapsed
- record coarse pre-edit context length
- record the abstract class of the final pre-edit left-context character
- support future debugging and no-oracle review without exposing raw text

## 2. Features Used

The diagnostic constraints should use only `CandidateFeatureSet v0_3` fields:

- `context_before_length_bucket`
- `cursor_at_document_start`
- `cursor_at_document_end_before`
- `selection_is_collapsed_before`
- `selection_span_length_bucket`
- `left_context_ends_with_space`
- `left_context_ends_with_punctuation`
- `left_char_class`

Constraint generation should not re-read or reintroduce raw
`local_context_before`.

## 3. Initial Constraint Candidates

### Context Length Diagnostics

- `CONTEXT-BEFORE-EMPTY`
- `CONTEXT-BEFORE-SHORT`
- `CONTEXT-BEFORE-MEDIUM`
- `CONTEXT-BEFORE-LONG`

These constraints record the coarse `context_before_length_bucket` value.

### Cursor Position Diagnostics

- `CURSOR-AT-DOCUMENT-START`
- `CURSOR-AT-DOCUMENT-END-BEFORE`

These constraints record whether the cursor was at a boundary before the
candidate action.

### Selection Diagnostics

- `SELECTION-COLLAPSED-BEFORE`
- `SELECTION-NONCOLLAPSED-BEFORE`
- `SELECTION-SPAN-SHORT`
- `SELECTION-SPAN-MEDIUM`
- `SELECTION-SPAN-LONG`

These constraints record whether the selection was collapsed and, when not
collapsed, the coarse selection span bucket. `SELECTION-SPAN-SHORT`,
`SELECTION-SPAN-MEDIUM`, and `SELECTION-SPAN-LONG` should be observed only
when the corresponding bucket is present.

### Left-Context Ending Diagnostics

- `LEFT-CONTEXT-ENDS-WITH-SPACE`
- `LEFT-CONTEXT-ENDS-WITH-PUNCTUATION`

These constraints record the boolean ending-shape features without storing the
character itself.

### Left-Character Class Diagnostics

- `LEFT-CHAR-CLASS-NONE`
- `LEFT-CHAR-CLASS-WHITESPACE`
- `LEFT-CHAR-CLASS-PUNCTUATION`
- `LEFT-CHAR-CLASS-DIGIT`
- `LEFT-CHAR-CLASS-UPPERCASE-LETTER`
- `LEFT-CHAR-CLASS-LOWERCASE-LETTER`
- `LEFT-CHAR-CLASS-OTHER-LETTER`
- `LEFT-CHAR-CLASS-OTHER`

These constraints mirror the `left_char_class` enum. They are diagnostic
records only; they do not imply a correction category or correctness label.

## 4. Violation Count and Scoring

Initial local pattern diagnostic constraints should be descriptive constraints.

Policy:

- `constraint_type = descriptive`
- `violation_count = 0`
- `severity = info`
- no contribution to `weighted_score`
- no blocking behavior
- no tie-break change

They must not be mixed with safety blocking constraints such as
`NO-LEAKAGE-FLAG`, `NO-OBSERVED-EDIT-TEXT`, or `NO-UNSAFE-CANDIDATE`.

The existing scorer may carry the records in `constraint_contributions`, but
because their weight is `0.0` and their `violation_count` is `0`, ranking
behavior should remain unchanged.

## 5. No-Oracle Policy

The v0.3 local pattern features are derived from prediction-time fields such
as `local_context_before`, cursor position, document length before edit, and
selection offsets before edit.

Diagnostic constraint generation must use only those already-extracted
features.

Forbidden inputs:

- `local_context_after_observed`
- `observed_after_text`
- `final_text`
- `gold_label`
- teacher correction
- human correction
- post-hoc annotation
- future edit
- future context
- synthetic expected action
- real participant data

Synthetic expected actions remain evaluation-only and must not be used by
feature extraction, constraint generation, scoring, or ranking.

## 6. Privacy Policy

Local pattern diagnostic constraints must not contain enough information to
reconstruct raw text.

Allowed output:

- short enum buckets
- booleans
- constraint IDs
- `observed` flags
- `violation_count = 0`

Forbidden output:

- raw `local_context_before`
- raw tokens
- selected text
- candidate description text
- proposed edit payloads
- observed edit text
- post-edit context
- final text
- expected actions

The constraints should record shape, not content.

## 7. Deferred Items

The following constraint families should not be added in the first diagnostic
implementation:

- article-like token constraints
- token length constraints
- local window scan constraints
- sentence boundary marker constraints
- fine-grained Unicode punctuation constraints

Reasons for deferral:

- token features move closer to raw text processing
- token-like constraints can increase privacy and re-identification risk
- local-window scans may expose more content shape than necessary
- Unicode punctuation requires a separately reviewed classification policy
- the first diagnostic constraint set should stay small and auditable

## 8. Implementation Test Plan

When these constraints are implemented, tests should cover:

- every context length bucket produces the corresponding diagnostic constraint
- cursor start and cursor end booleans produce the corresponding constraints
- collapsed and non-collapsed selection states are represented
- short / medium / long selection span buckets are represented
- whitespace and punctuation ending booleans are represented
- every `left_char_class` enum value has a corresponding constraint
- every new constraint is descriptive
- every new constraint has `violation_count = 0`
- scoring order is unchanged
- blocking behavior is unchanged
- forbidden fields are absent
- raw local context text is absent
- synthetic E2E smoke still passes

All tests should use synthetic fixtures only.

## 9. Future Roadmap

### Step 50: Implement Local Pattern Diagnostic Descriptive Constraints

Add the diagnostic constraints listed in this plan to constraint generation.

### Step 51: Diagnostic Summary Tooling

Consider summary-only tooling that counts diagnostic constraint observations
without printing JSONL content.

### Step 52: Consider Non-Leaky Linguistic Constraints

Use diagnostic evidence to decide whether more interpretable linguistic
constraints can be designed without raw text leakage.

### Later: Scoring Review

Do not add local pattern diagnostics to `weighted_score` until there is a
separate scoring-policy design, no-oracle review, and synthetic smoke coverage.

## 10. Non-Goals

This plan does not:

- implement constraints
- change feature extraction
- change scoring
- add weights
- change tie-break policy
- implement grammar correctness checks
- implement F1, accuracy, calibration, or learner-state estimation
- introduce real participant data
- introduce real gold labels
- use teacher corrections
