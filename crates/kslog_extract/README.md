# kslog_extract

`kslog_extract` extracts initial `RevisionEvent` records from validated raw keystroke event sequences.

The crate describes observed editing actions. It does not decide whether an edit is correct, does not use gold labels, and does not construct micro-episodes.

## Purpose

The purpose of this crate is to convert low-level `RawEvent` rows into a more useful event layer for later revision-event analysis and micro-episode construction.

## Input and Output

Input:

- `&[RawEvent]`
- events should already pass `kslog_validate`
- events should replay successfully with `kslog_replay`

Output:

- `RevisionExtractionReport`
- a list of `RevisionEvent` values
- unsupported event count

## Usage

```rust
use kslog_extract::extract_revision_events;

let report = extract_revision_events(&events)?;
```

## Test Method

From the repository root:

```bash
cargo test -p kslog_extract
```

Tests use only synthetic fixtures from `tests/fixtures/synthetic/raw_events/valid/`.

## Extracted RevisionEvent Kinds

The first version can extract:

- `Insertion`
- `Deletion`
- `Replacement`
- `SelectionRangeEdit`
- `Paste`
- `CompositionCommit`
- `Unsupported`

Normal typing is extracted as `Insertion` with `is_revision_like = false`. This preserves the observed event while distinguishing it from deletion, replacement, paste, and other revision-like behaviors.

Classification is heuristic and based only on observed event shape.

Current priority:

1. `CompositionCommit` for `composition_end` with observed `inserted_text`
2. `Paste` for `event_type = paste` or `input_type = insertFromPaste`
3. `SelectionRangeEdit` for non-collapsed `selection_start_before..selection_end_before` with text change
4. `Replacement` for observed inserted and deleted text without a non-collapsed selection
5. `Deletion`
6. `Insertion`
7. `Unsupported`

`SelectionRangeEdit` is intentionally prioritized over `Replacement` when a non-collapsed selection is present. This makes selection-driven edits easy to find; inserted/deleted text is still preserved on the event.

`Insertion` is marked `is_revision_like = true` only when it is selection-based or cursor-local. Cursor-local means `cursor_pos_before < doc_len_before`. Terminal ordinary typing remains `is_revision_like = false`.

Paste and composition handling are minimal. Browser differences may still cause paste or IME behavior to appear as ordinary insertion or unsupported events.

## What This Crate Does Not Do Yet

- It does not implement a web logger.
- It does not validate JSONL directly.
- It does not construct micro-episodes.
- It does not run no-oracle audits.
- It does not generate candidates.
- It does not run OT scoring.
- It does not estimate learner state.
- It does not use final corrected text, gold labels, teacher corrections, or post-hoc annotations.
- It does not use replay output final text as a classification reason.

## Data Policy

`RevisionEvent` can contain text fragments copied from `inserted_text` and `deleted_text`. Do not commit revision-event outputs derived from real participant data.
