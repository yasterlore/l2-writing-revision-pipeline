# Revision Event Spec

This file documents the first revision-event extraction layer.

The implementation lives in `crates/kslog_extract/`.

## Responsibility

Revision events describe observed editing actions derived from validated raw events.

They are not gold labels. They do not say whether an edit is correct. They do not use final corrected text, teacher corrections, or post-hoc annotations.

## Current RevisionEvent Kinds

The first extractor supports:

- `Insertion`
- `Deletion`
- `Replacement`
- `SelectionRangeEdit`
- `Paste`
- `CompositionCommit`
- `Unsupported`

Normal typing is extracted as `Insertion` with `is_revision_like = false`. This preserves observed input events while distinguishing ordinary text production from deletion, replacement, selection edit, paste, and composition commit.

When `inserted_text` and `deleted_text` are both present, the first extractor uses `Replacement` as the primary kind even if a selection range is present. The selection span is still preserved on the event.

## Current Fields

Initial `RevisionEvent` records include:

- `revision_event_id`
- `session_id`
- `task_id`
- `prompt_id`
- `source_seq`
- `timestamp_ms`
- `kind`
- `span`
- `inserted_text`
- `deleted_text`
- `cursor_pos_before`
- `cursor_pos_after`
- `doc_len_before`
- `doc_len_after`
- `is_revision_like`
- `quality_flags`

`revision_event_id` is deterministic and currently uses `{session_id}:{source_seq}`.

## No-Oracle Policy

Extraction must not use:

- `final_text`
- `observed_after_text`
- `gold_label`
- teacher corrections
- human corrections after writing
- post-hoc annotations

Replay success may be used as a consistency check. Replay output `final_text` must not be used as a reason for revision kind classification or candidate ranking.

## Data Policy

`RevisionEvent` may contain inserted or deleted text fragments. Revision-event outputs derived from real participant data must not be committed to this repository.

## Forbidden Location

Revision-event extraction must not be implemented in the TypeScript logger.

## Current Limitations

IME handling is minimal. Micro-episode grouping is not implemented here.
