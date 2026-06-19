# kslog_replay Explained

## 1. Beginner Summary

`kslog_replay` rebuilds the text of a writing session by applying raw editing events one by one.

It starts with an empty document. Each event may insert text, delete text, replace selected text, move the cursor, or mark an IME composition boundary.

## 2. What This Component Does

This component:

- takes `RawEvent` values
- starts from an empty string
- applies insertions, deletions, replacements, selections, paste events, and minimal IME commit events
- checks document length before and after each event
- checks edit cursor and selection ranges
- returns a `ReplayReport`

## 3. What This Component Does Not Do

This component does not:

- implement a web logger
- validate raw JSONL format
- extract revision events
- construct micro-episodes
- run a no-oracle audit
- generate correction candidates
- rank candidates
- estimate learner state
- process real participant data

## 4. Input and Output

Input is a slice of `RawEvent` values. These events should already have passed `kslog_validate`.

Output is either:

- `ReplayReport`, including replayed `final_text`
- `ReplayError`, if replay cannot proceed safely

The `final_text` in `ReplayReport` is a replay artifact. It must not be used as no-oracle input for candidate generation, ranking, OT scoring, or learner-state estimation.

## 5. Step-by-Step Mechanism

1. Start with an empty document.
2. Read the next `RawEvent`.
3. Check `doc_len_before` against the current document character count when present.
4. Check `text_hash_before` if it is present and not a placeholder.
5. Choose the edit range.
6. Apply insertion, deletion, replacement, or no text change.
7. Check `doc_len_after` against the updated document character count when present.
8. Check `text_hash_after` if it is present and not a placeholder.
9. Update cursor position when `cursor_pos_after` is present.
10. Continue until all events are replayed.

## 6. Important Data Structures

`ReplayState` stores the current text and cursor position.

`ReplayReport` stores the final replayed text, event count, final cursor position, and final document length.

`ReplayError` reports deterministic replay failures.

`ReplayErrorKind` describes the reason for failure, such as document length mismatch or out-of-bounds selection.

## 7. Theory Behind the Implementation

Text replay treats writing as a sequence of state transitions. Each raw event transforms the document from one state into another.

This layer is intentionally separate from revision-event extraction. Replay reconstructs text states; later crates decide which changes count as revision events or micro-episodes.

## 8. Mathematical Formulas, If Any

No mathematical formulas are used in this component.

## 9. Weighting Rationale, If Weights Are Used

No weights are used in this component.

## 10. Ranking Rationale, If Ranking Is Used

No ranking is used in this component.

## 11. Why This Design Was Selected Over Alternatives

Rust is used because replay is part of the deterministic authoritative layer.

The implementation uses `Result` rather than panics so inconsistent events can be reported safely.

The implementation uses character counts rather than byte lengths because browser cursor positions are text positions, not Rust byte offsets. This is still an approximation: future work may need grapheme cluster support for emoji, combining marks, and some complex scripts.

## 12. Security and Privacy Considerations

Only synthetic fixtures are used in tests.

Replay output can contain reconstructed writing. Do not commit replay outputs derived from real participant data.

This crate does not read `private_data/`, `real_data/`, or `participant_data/`.

Malformed or inconsistent events return `ReplayError` instead of panicking.

The crate uses no `unsafe` Rust.

## 13. Tests Added

The tests cover:

- simple typing
- deletion
- replacement
- selection edit
- paste
- cursor movement
- minimal IME composition
- `doc_len_before` mismatch
- `doc_len_after` mismatch
- out-of-bounds cursor
- out-of-bounds selection
- malformed JSON parse failure without panic

## 14. Known Limitations

IME composition is handled minimally. `composition_update` is not treated as committed document text; `composition_end` may commit text when `inserted_text` is present.

The initial implementation uses Unicode scalar value counts via Rust `char` count. It does not yet use grapheme cluster segmentation.

Placeholder hashes such as `synthetic_hash_*` are skipped.

The replay engine does not collect all possible errors; it stops at the first replay error.

## 15. What To Read Next

- `crates/kslog_schema/README.md`
- `crates/kslog_validate/README.md`
- `docs/05_text_replay_spec.md`
- `docs/06_revision_event_spec.md`
- `docs/07_micro_episode_spec.md`

