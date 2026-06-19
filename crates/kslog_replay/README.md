# kslog_replay

`kslog_replay` reconstructs document text from a sequence of validated `kslog_schema::RawEvent` values.

It is the first text replay layer for synthetic keystroke-level writing process data. It does not extract revision events or construct micro-episodes.

## Purpose

The purpose of this crate is to replay raw event sequences into document state so later Rust crates can extract revision events and construct micro-episodes from deterministic text states.

## Input and Output

Input:

- `&[RawEvent]`
- events should already pass `kslog_validate`
- initial document state is the empty string

Output:

- `ReplayReport` on success
- `ReplayError` on failure

`ReplayReport.final_text` is replay output. It must not be treated as a no-oracle input for candidate generation, ranking, OT scoring, or learner-state estimation.

## Usage

```rust
use kslog_replay::replay_events;

let report = replay_events(&events)?;
println!("{}", report.final_text);
```

## Test Method

From the repository root:

```bash
cargo test -p kslog_replay
```

The tests use only synthetic fixtures from `tests/fixtures/synthetic/raw_events/valid/`.

## What This Crate Checks

- `doc_len_before` matches the current replayed character count when present.
- `doc_len_after` matches the updated replayed character count when present.
- cursor positions used for editing are in bounds.
- selection ranges used for editing are ordered and in bounds.
- `deleted_text` matches the selected or inferred range before deletion or replacement.
- non-placeholder text hashes can be checked with the built-in deterministic hash label.

## What This Crate Does Not Check Yet

- It does not validate JSONL format.
- It does not enforce `seq` continuity.
- It does not perform full browser-event semantic validation.
- It does not deeply interpret IME composition updates.
- It does not extract revision events.
- It does not construct micro-episodes.
- It does not run no-oracle audits.
- It does not generate or rank revision candidates.

## Hash Policy

Synthetic fixtures currently use placeholder hash labels such as `synthetic_hash_*`. Replay skips those placeholders.

For non-placeholder hash strings, this crate expects `kslog_fnv1a64:<hex>`, computed by a small deterministic FNV-1a implementation without adding a dependency.

## Data Policy

Replay output may contain reconstructed text. Do not commit replay outputs derived from real participant data. This repository must use synthetic data only.

