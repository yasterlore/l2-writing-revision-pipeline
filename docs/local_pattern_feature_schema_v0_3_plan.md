# Local Pattern Feature Schema v0.3 Plan

This document specifies the `CandidateFeatureSet` v0.3 local pattern feature
schema.

Step 48 implemented the feature extraction portion of this schema. It still
does not implement new constraints, scoring changes, weights, F1, accuracy,
calibration, or learner-state estimation.

## 1. Purpose

`CandidateFeatureSet v0_2` contains structural candidate metadata such as
`generation_rule`, `action_family`, and candidate-family flags.

`CandidateFeatureSet v0_3` adds a small first set of no-oracle-safe local
pattern features.

The goal is to represent local pre-edit context shape without storing raw text.

Design principles:

- add only boolean or bucket features
- do not store `local_context_before` text in `CandidateFeatureSet`
- do not store raw tokens
- do not add proposed edit payloads
- do not add score weights
- do not change rank

## 2. Initial v0.3 Feature Candidates

Implemented initial fields:

- `context_before_length_bucket`
- `cursor_at_document_start`
- `cursor_at_document_end_before`
- `selection_is_collapsed_before`
- `selection_span_length_bucket`
- `left_context_ends_with_space`
- `left_context_ends_with_punctuation`
- `left_char_class`

These features are intentionally small. They avoid token extraction and avoid
copying raw learner text into feature, constraint, or score outputs.

## 3. Feature Definitions

### `context_before_length_bucket`

Type: string enum.

Input:

- `local_context_before`

Provisional output values:

- `empty`
- `short`
- `medium`
- `long`

Provisional thresholds:

- `empty`: char count is `0`
- `short`: char count is `1..=10`
- `medium`: char count is `11..=30`
- `long`: char count is greater than `30`

No-oracle reason:

`local_context_before` is prediction-time context.

Privacy note:

Only a coarse length bucket is stored, not the text itself.

Implementation notes:

Use char count, not byte length. Revisit grapheme-cluster handling later.

### `cursor_at_document_start`

Type: boolean.

Input:

- `cursor_pos_before`

Output examples:

- `true`
- `false`

No-oracle reason:

Cursor position before the candidate action is prediction-time metadata.

Privacy note:

The feature reveals only a position condition, not text content.

Implementation notes:

Treat missing cursor position as `false` or an explicit unknown policy. The
implementation should document that choice.

### `cursor_at_document_end_before`

Type: boolean.

Input:

- `cursor_pos_before`
- `doc_len_before`

Output examples:

- `true`
- `false`

No-oracle reason:

Both fields describe the pre-edit document state.

Privacy note:

The feature does not store document text.

Implementation notes:

Use character counts consistently. If either input is missing, use an explicit
unknown policy rather than guessing.

### `selection_is_collapsed_before`

Type: boolean.

Input:

- `selection_start_before`
- `selection_end_before`

Output examples:

- `true`
- `false`

No-oracle reason:

The selection before the candidate action is prediction-time metadata.

Privacy note:

The feature stores only whether the selection had span length zero.

Implementation notes:

If selection offsets are missing, define a conservative unknown/default policy.

### `selection_span_length_bucket`

Type: string enum.

Input:

- `selection_start_before`
- `selection_end_before`

Provisional output values:

- `collapsed`
- `short`
- `medium`
- `long`
- `unknown`

Provisional thresholds:

- `collapsed`: span length is `0`
- `short`: span length is `1..=5`
- `medium`: span length is `6..=20`
- `long`: span length is greater than `20`
- `unknown`: one or both selection offsets are missing or invalid

No-oracle reason:

Only pre-edit selection metadata is used.

Privacy note:

The selected text itself is not stored.

Implementation notes:

Use saturating or validated arithmetic. Invalid ranges should not panic.

### `left_context_ends_with_space`

Type: boolean.

Input:

- `local_context_before`

Output examples:

- `true`
- `false`

No-oracle reason:

The feature only checks the final pre-edit character.

Privacy note:

The character itself is not stored; only a whitespace boolean is stored.

Implementation notes:

Use Unicode-aware whitespace checks where practical.

### `left_context_ends_with_punctuation`

Type: boolean.

Input:

- `local_context_before`

Output examples:

- `true`
- `false`

No-oracle reason:

The feature only checks the class of the final pre-edit character.

Privacy note:

The punctuation character itself is not stored.

Implementation notes:

Start with a documented ASCII punctuation set or a carefully reviewed Unicode
category policy. Keep the first implementation conservative.

### `left_char_class`

Type: string enum.

Input:

- `local_context_before`

Provisional output values:

- `none`
- `whitespace`
- `punctuation`
- `digit`
- `uppercase_letter`
- `lowercase_letter`
- `other_letter`
- `other`

No-oracle reason:

The feature abstracts only the final pre-edit character.

Privacy note:

It does not store the character itself.

Implementation notes:

Use char-level classification. Be explicit about Unicode casing behavior and
the difference between char count and byte length.

## 4. Deferred Features

The following features should not be included in the initial v0.3
implementation:

- `left_context_ends_with_article_like_token`
- `has_left_token_before_cursor`
- `left_token_length_bucket`
- `local_window_has_digit`
- `local_window_has_uppercase`
- `local_window_has_sentence_boundary_marker`

Reasons for deferral:

- token handling moves closer to raw text processing
- token-derived features can increase re-identification risk
- Unicode and IME handling need more careful specification
- local-window scans can reveal more about content shape than a single-character abstraction
- the initial schema should remain small and auditable

These features may be reconsidered after v0.3 has synthetic tests and privacy
review.

## 5. Information Allowed

The v0.3 schema may use:

- `local_context_before`
- `cursor_pos_before`
- `doc_len_before`
- `selection_start_before`
- `selection_end_before`
- candidate metadata
- no-oracle-safe flags

The feature extractor may inspect `local_context_before` transiently to compute
abstract features, but it must not write that text into `CandidateFeatureSet`.

## 6. Information Forbidden

The v0.3 schema must not use:

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

Expected actions remain evaluation-only.

## 7. Output Policy

`CandidateFeatureSet v0_3` output must not contain:

- `local_context_before` text
- `local_context_after_observed`
- raw tokens
- candidate description text
- proposed edit payloads
- observed edit text
- final text
- expected actions

Allowed output shape:

- booleans
- short enum buckets
- numeric counts only if coarse and justified

Score output should also remain text-free.

## 8. Test Plan

Initial tests should cover:

- empty context
- whitespace ending
- punctuation ending
- digit ending
- uppercase ending
- lowercase ending
- other-letter ending
- selection collapsed
- selection non-collapsed
- selection missing or invalid
- cursor at start
- cursor at end
- cursor in middle
- Unicode / IME smoke case
- forbidden fields not present
- no raw text in feature output
- no raw text in score output

All tests should use synthetic data only.

## 9. Implementation Status

Step 48 implemented these fields in `python/ot_scorer`:

- `context_before_length_bucket`
- `cursor_at_document_start`
- `cursor_at_document_end_before`
- `selection_is_collapsed_before`
- `selection_span_length_bucket`
- `left_context_ends_with_space`
- `left_context_ends_with_punctuation`
- `left_char_class`

The implementation stores only booleans and enum buckets in
`CandidateFeatureSet`. It does not store raw `local_context_before`, selected
text, candidate descriptions, proposed edit payloads, post-edit context,
observed edit text, final text, expected actions, or teacher corrections.

The current provisional thresholds are:

- `context_before_length_bucket`: `empty` for `0`, `short` for `1..=10`,
  `medium` for `11..=30`, and `long` for more than `30` characters.
- `selection_span_length_bucket`: `collapsed` for `0`, `short` for `1..=5`,
  `medium` for `6..=20`, and `long` for more than `20` characters.

`left_char_class` uses Python string methods for whitespace, digit, and letter
checks, and begins punctuation handling with ASCII punctuation. Unicode
punctuation and grapheme-cluster boundaries remain known limitations.

Constraint generation, scoring formula, weights, tie-break policy, and
evaluation metrics are unchanged.

## 10. Roadmap

### Step 48: Implement CandidateFeatureSet v0.3 Local Pattern Features

Completed: the initial v0.3 fields are now emitted by feature extraction.

### Step 49: Update Synthetic Fixtures and Tests

Update synthetic fixtures and add targeted tests for each bucket and boolean.

### Step 50: Descriptive Diagnostic Constraints

Connect selected local pattern fields to descriptive constraints only.

### Later: Scoring Review

Do not add these features to `weighted_score` until there is a separate
scoring-policy design, no-oracle review, and synthetic smoke coverage.

## 11. Non-Goals

This plan does not:

- implement constraints
- change scoring
- add weights
- change tie-break policy
- implement F1, accuracy, calibration, or learner-state estimation
- introduce real participant data
- introduce real gold labels
