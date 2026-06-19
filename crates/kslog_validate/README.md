# kslog_validate

`kslog_validate` performs the first deterministic JSONL validation pass for raw keystroke-level event logs.

It uses `kslog_schema::RawEvent` as the typed schema boundary and validates synthetic JSONL files one line at a time.

## Purpose

The crate exists to reject malformed or structurally unsafe raw event JSONL before later deterministic stages attempt text replay, revision-event extraction, micro-episode construction, or no-oracle auditing.

## Input and Output

Input:

- UTF-8 JSONL
- one JSON object per line
- each valid line must deserialize as `kslog_schema::RawEvent`

Output:

- `ValidationReport` on success
- `ValidationError` on failure

Errors include a line number when the error is tied to a specific JSONL line.

## Usage

```rust
use std::io::Cursor;

use kslog_validate::{validate_jsonl_reader, ValidationOptions};

let input = Cursor::new(synthetic_jsonl);
let report = validate_jsonl_reader(input, &ValidationOptions::default())?;
```

## Test Method

From the repository root:

```bash
cargo test -p kslog_validate
```

The tests use only synthetic fixtures from `tests/fixtures/synthetic/raw_events/`.

## What This Crate Checks

- JSONL is read as one JSON object per line.
- Malformed JSON is rejected.
- Empty lines are rejected by default.
- Lines over `max_line_bytes` are rejected.
- Lines must deserialize as `kslog_schema::RawEvent`.
- Unknown fields are rejected through `RawEvent` serde policy.
- No-oracle forbidden fields such as `final_text`, `observed_after_text`, and `gold_label` are rejected.
- `seq` must be consecutive, starting from the first line's `seq`.
- `timestamp_ms` must be monotonically non-decreasing.
- Cursor positions must not exceed corresponding document lengths when both are present.
- Selection starts must not exceed selection ends.
- Selection positions must not exceed corresponding document lengths when both are present.

## What This Crate Does Not Check Yet

- It does not implement a web logger.
- It does not replay text.
- It does not check whether inserted or deleted text reconstructs the document.
- It does not extract revision events.
- It does not construct micro-episodes.
- It does not run the full no-oracle audit.
- It does not generate candidates, rank candidates, or estimate learner state.
- It does not process real participant data.

