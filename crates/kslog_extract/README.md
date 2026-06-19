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

When `inserted_text` and `deleted_text` are both present, the event is classified as `Replacement` even if a selection span is available. The span is still preserved. `SelectionRangeEdit` is reserved for selection-based edits that are not already represented as replacement in this first version.

## What This Crate Does Not Do Yet

- It does not implement a web logger.
- It does not validate JSONL directly.
- It does not construct micro-episodes.
- It does not run no-oracle audits.
- It does not generate candidates.
- It does not run OT scoring.
- It does not estimate learner state.
- It does not use final corrected text, gold labels, teacher corrections, or post-hoc annotations.

## Data Policy

`RevisionEvent` can contain text fragments copied from `inserted_text` and `deleted_text`. Do not commit revision-event outputs derived from real participant data.
