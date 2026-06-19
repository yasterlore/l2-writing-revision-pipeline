# kslog_extract Explained

## 1. Beginner Summary

`kslog_extract` turns raw browser events into observed editing actions called `RevisionEvent`.

For example, if a learner deletes one letter, this crate can describe that as a `Deletion`. If a learner replaces selected text, it can describe that as a `SelectionRangeEdit`.

## 2. What This Component Does

This component:

- reads `RawEvent` values
- checks that replay succeeds before extraction
- classifies each event into a small set of observed edit kinds
- creates deterministic `revision_event_id` values
- marks terminal normal typing as `is_revision_like = false`
- marks deletion, replacement, selection edit, paste, composition commit, and cursor-local insertion as `is_revision_like = true`

## 3. What This Component Does Not Do

This component does not:

- implement a browser logger
- validate JSONL files
- construct micro-episodes
- run no-oracle audits
- generate correction candidates
- rank candidates
- run OT scoring
- estimate learner state
- use gold labels or final corrected text
- decide whether an edit is correct

## 4. Input and Output

Input is a slice of `RawEvent` values.

Output is a `RevisionExtractionReport`, which contains extracted `RevisionEvent` records and a count of unsupported events.

Each `RevisionEvent` includes identifiers, source `seq`, timestamp, kind, span, inserted text, deleted text, cursor positions, document lengths, `is_revision_like`, and quality flags.

## 5. Step-by-Step Mechanism

1. Replay the full event sequence with `kslog_replay`.
2. If replay fails, return `RevisionExtractionError`.
3. For each `RawEvent`, inspect only observed event fields.
4. Classify composition commit and paste first.
5. Classify selection range edits when a non-collapsed selection and text edit are present.
6. Classify replacement, deletion, insertion, or unsupported.
7. Compute a span from selection or cursor positions.
8. Create a deterministic ID in the form `{session_id}:{source_seq}`.

## 6. Important Data Structures

`RevisionEventKind` is the category of observed edit.

`RevisionSpan` stores a start and end offset in the pre-event document coordinate system.

`RevisionEvent` stores one extracted observed edit.

`RevisionExtractionReport` stores all extracted events and summary counts.

`RevisionExtractionError` reports replay or span extraction failures.

## 7. Theory Behind the Implementation

The design separates observation from interpretation. A deletion is an observed action; whether it improves the text is a later research question.

This avoids using teacher corrections, final corrected text, or gold labels during extraction.

## 8. Mathematical Formulas, If Any

No mathematical formulas are used in this component.

## 9. Weighting Rationale, If Weights Are Used

No weights are used in this component.

## 10. Ranking Rationale, If Ranking Is Used

No ranking is used in this component.

## 11. Why This Design Was Selected Over Alternatives

The extractor is deliberately conservative. It uses only fields available in `RawEvent`, plus replay success as a consistency check.

Normal terminal typing is preserved as `Insertion` but marked `is_revision_like = false` so later components can include or exclude it without losing information.

When a non-collapsed selection is present, the extractor uses `SelectionRangeEdit` before `Replacement`. This makes selection-driven edits easy to find. If inserted and deleted text are both present without a non-collapsed selection, the event can still be classified as `Replacement`.

Cursor-local insertion is treated as revision-like when `cursor_pos_before < doc_len_before`. This is a heuristic: it catches edits made away from the document end, but it is not a claim about correctness or learner intention.

Micro-episode grouping is left for a later crate to keep this layer focused.

## 12. Security and Privacy Considerations

Tests use only synthetic fixtures.

The extractor does not read `private_data/`, `real_data/`, or `participant_data/`.

It does not use `final_text`, `observed_after_text`, `gold_label`, teacher corrections, human corrections, or post-hoc annotations.

It does not use replay output final text to decide revision kind.

`RevisionEvent` may include inserted or deleted text. Do not commit revision-event output derived from real participant data.

The crate uses no `unsafe` Rust.

## 13. Tests Added

The tests cover:

- deletion extraction
- replacement extraction
- selection range edit extraction
- paste extraction
- composition commit extraction
- selection range priority over replacement
- cursor-local insertion marked revision-like
- paste detection from `input_type = insertFromPaste`
- simple typing as non-revision-like insertion
- unsupported event handling without panic

## 14. Known Limitations

IME handling is minimal. The extractor identifies `composition_end` with `inserted_text` as `CompositionCommit` but does not model all IME internals.

The extractor does not determine whether an edit is linguistically meaningful or correct.

The extractor currently emits an `Unsupported` event for observed events that are not text edits.

Classification coverage is heuristic and can be improved as more synthetic manual cases are checked.

## 15. What To Read Next

- `crates/kslog_schema/README.md`
- `crates/kslog_validate/README.md`
- `crates/kslog_replay/README.md`
- `docs/06_revision_event_spec.md`
- `docs/07_micro_episode_spec.md`
