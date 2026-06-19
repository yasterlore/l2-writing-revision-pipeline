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

Normal terminal typing is extracted as `Insertion` with `is_revision_like = false`. This preserves observed input events while distinguishing ordinary text production from deletion, replacement, selection edit, paste, and composition commit.

Revision kinds are heuristic observations, not correctness labels.

Current priority:

1. `CompositionCommit`: `event_type = composition_end` and observed `inserted_text`
2. `Paste`: `event_type = paste` or `input_type = insertFromPaste`
3. `SelectionRangeEdit`: non-collapsed `selection_start_before < selection_end_before` with inserted and/or deleted text
4. `Replacement`: both inserted and deleted text, without a non-collapsed selection
5. `Deletion`
6. `Insertion`
7. `Unsupported`

`SelectionRangeEdit` is prioritized over `Replacement` when a non-collapsed selection is present. The inserted and deleted text fields are still preserved.

Cursor-local insertion is marked `is_revision_like = true` when `cursor_pos_before < doc_len_before`. This is a heuristic for edits away from the document end. Terminal ordinary typing remains `is_revision_like = false`.

Paste and IME classification are minimal and browser-dependent. Paste can be detected from `event_type = paste` or `input_type = insertFromPaste`. Composition commit is detected only for `composition_end` with observed inserted text.

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

IME handling is minimal. Paste and cursor-local classification are heuristic. Micro-episode grouping is not implemented here.
