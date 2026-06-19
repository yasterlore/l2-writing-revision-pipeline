# Raw Event Schema

This file documents the first Rust schema foundation for browser-side raw event rows.

The implementation lives in `crates/kslog_schema/`.

## Current Scope

`kslog_schema` defines a `RawEvent` Rust struct and related enums. It supports serde JSON serialization and deserialization for synthetic raw event objects.

This schema is a type boundary, not the full validator. Deterministic JSONL validation belongs in `crates/kslog_validate/`.

## RawEvent Fields

The initial `RawEvent` type includes:

- `logger_schema_version: String`
- `session_id: String`
- `participant_local_id: String`
- `task_id: String`
- `prompt_id: String`
- `seq: u64`
- `timestamp_ms: u64`
- `event_type: EventType`
- `input_type: Option<InputType>`
- `is_composing: bool`
- `composition_id: Option<String>`
- `selection_start_before: Option<u32>`
- `selection_end_before: Option<u32>`
- `selection_start_after: Option<u32>`
- `selection_end_after: Option<u32>`
- `cursor_pos_before: Option<u32>`
- `cursor_pos_after: Option<u32>`
- `doc_len_before: Option<u32>`
- `doc_len_after: Option<u32>`
- `inserted_text: Option<String>`
- `deleted_text: Option<String>`
- `text_hash_before: Option<String>`
- `text_hash_after: Option<String>`
- `diff_op: Option<DiffOp>`
- `quality_flags: Vec<String>`

## EventType

The initial `EventType` enum includes:

- `before_input`
- `input`
- `key_down`
- `key_up`
- `composition_start`
- `composition_update`
- `composition_end`
- `selection_change`
- `focus`
- `blur`
- `paste`
- `cut`

## InputType

The initial `InputType` enum uses browser-style camelCase names, including:

- `insertText`
- `insertLineBreak`
- `insertParagraph`
- `insertFromPaste`
- `deleteContentBackward`
- `deleteContentForward`
- `deleteByCut`
- `historyUndo`
- `historyRedo`

## DiffOp

The initial `DiffOp` enum is a coarse operation hint:

- `insert`
- `delete`
- `replace`
- `selection_only`
- `composition`
- `no_text_change`

`DiffOp` is not a replay algorithm and not a revision-event extractor.

## Forbidden No-Oracle Fields

`RawEvent` must not include:

- `final_text`
- `observed_after_text`
- `gold_label`
- teacher corrections
- human corrections after writing
- post-hoc annotations

These fields are forbidden because candidate generation, ranking, OT scoring, and learner-state estimation must not use future information or gold labels.

## Security Notes

Raw JSONL input must be treated as untrusted. Future validation must reject malformed, oversized, impossible, or adversarial events.

The schema crate uses serde `deny_unknown_fields` so unknown fields, including forbidden no-oracle fields, are not silently accepted as `RawEvent`.

## Data Notes

Examples and fixtures for this schema may contain synthetic data only. Real participant data must never be committed, read, inspected, transformed, summarized, or written by Codex.

Current synthetic raw event JSONL files live in:

- `examples/synthetic/raw_events/`
- `tests/fixtures/synthetic/raw_events/valid/`
- `tests/fixtures/synthetic/raw_events/invalid/`

The valid fixture lines are expected to deserialize as `RawEvent`. The invalid fixtures are reserved for future `kslog_validate` tests and include both schema-level invalid cases and cross-field invalid cases.

## Web Logger Notes

The initial TypeScript web logger lives in `apps/logger-web/`.

It emits RawEvent-like JSONL from browser textarea events using synthetic metadata:

- `synthetic_session_web_001`
- `synthetic_writer_web_001`
- `synthetic_task_web_freewrite_001`
- `synthetic_prompt_web_001`

The logger uses `Date.now()` for `timestamp_ms`, records selection/cursor/document length snapshots, and uses `synthetic_hash_*` placeholders for text hashes.

The logger is an observation layer only. It must not implement validation, replay, revision-event extraction, micro-episode construction, no-oracle audit, candidate generation, or ranking.

Downloaded JSONL can contain text fragments. Do not commit downloaded JSONL from real sessions to this repository.
