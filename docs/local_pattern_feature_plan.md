# Local Pattern Feature Plan

This document is a design plan for future no-oracle-safe local pattern features.

It does not implement features, constraints, scoring changes, weights, F1,
accuracy, calibration, or learner-state estimation.

## 1. Purpose

Local pattern features are planned abstract features derived from the local
pre-edit context around a candidate episode.

Their purpose is to capture the shape of the local writing context without
copying raw text into later scoring outputs.

They should help future interpretable constraints ask questions such as:

- Is the cursor at the beginning or end of the current document?
- Is there a token immediately before the cursor?
- Does the left context end with punctuation?
- Does the local window contain digits or sentence-boundary markers?
- Is the selection collapsed before the edit?

They should not decide whether the learner's text is grammatically correct.

They should not be added to `weighted_score` immediately. The first use should
be descriptive diagnostics and future constraint design.

## 2. Information Allowed

Future local pattern features may use prediction-time fields from
`NoOracleSafeEpisodeView`, including:

- `local_context_before`
- `cursor_pos_before`
- `doc_len_before`
- `selection_start_before`
- `selection_end_before`
- `action_type`
- `generation_rule`
- `action_family`
- `candidate_family_bucket`
- `quality_flags`
- no-oracle-safe flags

The key rule is that the information must be available at candidate-generation
or scoring time, before observing the learner's future edits or final text.

## 3. Information Forbidden

Local pattern features must not use:

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

Observed edit text should also remain out of this feature family unless a later
policy explicitly defines a safe prediction task boundary.

## 4. Candidate Feature Ideas

This section lists possible features only. They are not implemented yet.

### Position Features

- `context_before_length_bucket`
- `cursor_at_document_start`
- `cursor_at_document_end_before`
- `selection_is_collapsed_before`
- `selection_span_length_bucket`

### Left-Context Shape Features

- `has_left_token_before_cursor`
- `left_token_length_bucket`
- `left_char_class`
- `left_context_ends_with_space`
- `left_context_ends_with_punctuation`
- `left_context_ends_with_article_like_token`

### Local-Window Abstract Features

- `local_window_has_digit`
- `local_window_has_uppercase`
- `local_window_has_sentence_boundary_marker`

These features should use boolean values or coarse buckets instead of storing
raw local text.

## 5. Feature Design Rules

Local pattern features should be privacy-preserving and no-oracle-safe.

Design rules:

- do not add raw text to score output
- do not store long tokens
- avoid features that make re-identification easier
- prefer boolean values or coarse buckets
- document every bucket definition
- treat JSONL input as untrusted
- handle Unicode explicitly
- distinguish char count from byte count
- consider Japanese IME and composition boundaries
- use synthetic fixtures first

If a feature needs tokenization, the implementation must define what a token
means and how Unicode punctuation, whitespace, and composing text are handled.

## 6. No-Oracle Policy

`local_context_before` can be considered because it is prediction-time context.

`local_context_after_observed` is forbidden because it reflects observed
post-edit context and can leak the result of the learner's action.

Synthetic expected actions are evaluation-only. They must not be used to create
features, constraints, scores, or ranks.

Observed edit text is not part of this plan. If future work needs it, it should
go through a separate leakage review because it may become the prediction target
for some tasks.

## 7. Scoring Policy

This plan does not change scoring.

Even after local pattern features are implemented, they should not immediately
affect:

- `weighted_score`
- blocking constraints
- tie-break policy
- rank

The first integration should be descriptive constraints or diagnostics. Any
future non-zero weight must be documented in a separate scoring-policy change.

## 8. Beginner Explanation

### What Is a Local Pattern Feature?

A local pattern feature is a small abstract description of the text around the
cursor before an edit.

For example, instead of storing the actual previous word, a feature might store:

```text
has_left_token_before_cursor = true
left_token_length_bucket = short
```

This gives the system useful structure without copying the learner's writing
into public outputs.

### Why Not Store Raw Text?

Raw writing can contain personal information, sensitive topics, or distinctive
phrases.

Abstract features reduce privacy risk and make public synthetic tests easier to
audit.

### Why Is Post-Edit Context Leakage?

If a model sees text after an edit, it may indirectly see the learner's answer.

That would make ranking look better than it really is because the scorer would
have access to information that was unavailable at prediction time.

### Why No Performance Metrics Yet?

These features are still a design proposal.

The project should first verify no-oracle boundaries and synthetic wiring before
reporting any performance metric.

## 9. Roadmap

### Step A: Local Pattern Feature Schema Design

Define exact field names, bucket boundaries, Unicode handling, and no-oracle
input boundaries.

See [Local pattern feature schema v0.3 plan](local_pattern_feature_schema_v0_3_plan.md)
for the initial proposed field definitions.

### Step B: Synthetic Fixture Update

Add synthetic fixtures that cover document-start, document-end, punctuation,
selection, digits, uppercase letters, and sentence-boundary markers.

### Step C: Feature Extraction Implementation

Implement the features from `NoOracleSafeEpisodeView` or an explicitly safe
candidate input boundary.

### Step D: Descriptive Constraint Connection

Connect selected features to descriptive constraints only.

Do not add score weights yet.

### Step E: Synthetic Smoke Checks

Run synthetic E2E checks to verify that feature extraction, constraints, and
score output still suppress raw content.

### Step F: Private Validation Design Later

Only after synthetic behavior is stable, design private validation. Real data
must remain outside this repository and outside public CI.

## 10. Non-Goals

This plan does not:

- implement local pattern features
- implement constraints
- change scoring
- add weights
- change ranking
- evaluate real data
- introduce real gold labels
- use teacher corrections
- implement F1, accuracy, calibration, or learner-state estimation
