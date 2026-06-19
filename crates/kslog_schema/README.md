# kslog_schema

`kslog_schema` defines shared Rust data types for one row of keystroke-level writing-process data.

This first version focuses on `RawEvent`, the schema type for a single browser-side raw event. The crate is intentionally small: it provides serde serialization and deserialization, but it does not implement the logger, JSONL validation, text replay, revision-event extraction, micro-episode construction, no-oracle audits, or modeling logic.

## Purpose

The purpose of this crate is to give later Rust crates a common, typed representation of raw keystroke log events.

Downstream crates can eventually use this type for:

- validation
- text replay
- revision-event extraction
- micro-episode construction
- no-oracle audit tooling
- CLI input and output boundaries

## Usage

Add `kslog_schema` as a workspace dependency from another Rust crate, then deserialize synthetic JSON into `RawEvent`:

```rust
use kslog_schema::RawEvent;

let event: RawEvent = serde_json::from_str(synthetic_json)?;
```

This crate is not yet published and is currently intended for workspace-local use.

## RawEvent Overview

`RawEvent` represents one raw browser event row. It includes:

- session and task identifiers
- local synthetic participant identifier
- sequence number
- timestamp in milliseconds
- event type
- optional browser input type
- composition state
- optional cursor and selection positions
- optional document lengths
- optional inserted and deleted text
- optional text-state hashes
- optional coarse diff operation
- quality flags

Optional fields use `Option<T>` because many event types do not naturally have text, cursor, selection, or diff information.

## No-Oracle Fields

`RawEvent` does not include `final_text`, `observed_after_text`, `gold_label`, teacher corrections, human corrections after writing, or other post-hoc labels.

Those fields are forbidden by project policy for no-oracle candidate generation, ranking, OT scoring, and learner-state estimation. This crate uses serde `deny_unknown_fields` so those fields are not silently accepted as part of `RawEvent`.

## Test Method

From the repository root:

```bash
cargo test -p kslog_schema
```

The tests use synthetic JSON only.

## What This Crate Does Not Do Yet

- It does not implement a web logger.
- It does not validate JSONL files.
- It does not replay text.
- It does not extract revision events.
- It does not construct micro-episodes.
- It does not run no-oracle audits.
- It does not generate or rank candidates.
- It does not process real participant data.

