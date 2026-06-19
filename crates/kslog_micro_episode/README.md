# kslog_micro_episode

`kslog_micro_episode` builds local analysis units from extracted `RevisionEvent` records.

A `MicroEpisode` is centered on one observed edit and includes local context, edit span, inserted/deleted text fragments, cursor metadata, document lengths, and quality flags.

## Purpose

The purpose of this crate is to prepare deterministic Rust-side analysis units for later candidate generation, OT scoring, evaluation, and learner-state estimation.

`MicroEpisode` is not a correctness label and does not directly represent a learner's internal state.

## Input and Output

Input:

- `&[RawEvent]`
- events should be synthetic in this repository
- events should validate, replay, and extract successfully

Output:

- `MicroEpisodeConstructionReport`
- a list of `MicroEpisode` values
- skipped event counts

## Usage

```rust
use kslog_micro_episode::build_micro_episodes;

let report = build_micro_episodes(&events)?;
```

## Test Method

From the repository root:

```bash
cargo test -p kslog_micro_episode
```

Tests use only synthetic fixtures from `tests/fixtures/synthetic/raw_events/valid/`.

## MicroEpisode Fields

The first version includes:

- `micro_episode_id`
- `session_id`
- `task_id`
- `prompt_id`
- `source_revision_event_id`
- `source_seq`
- `timestamp_ms`
- `revision_kind`
- `is_revision_like`
- `local_context_before`
- `local_context_after_observed`
- `cursor_pos_before`
- `cursor_pos_after`
- `span_start`
- `span_end`
- `inserted_text`
- `deleted_text`
- `doc_len_before`
- `doc_len_after`
- `quality_flags`

`micro_episode_id` is deterministic and currently uses `{session_id}:micro:{source_seq}`.

## Context Window

The first version uses a fixed character window of 30 chars before and after the edit anchor.

This is a fixed initial setting, not a learned weight. It should be evaluated later against synthetic and institution-approved research workflows.

## No-Oracle Notes

`local_context_before` may be appropriate for no-oracle candidate generation because it is pre-edit context.

`local_context_after_observed` is observed post-edit context. It is no-oracle unsafe for candidate generation and ranking. It is retained for reconstruction checks and later evaluation workflows.

The crate does not include fields named `final_text`, `observed_after_text`, or `gold_label`.

## What This Crate Does Not Do Yet

- It does not implement a web logger.
- It does not run no-oracle audits.
- It does not generate candidates.
- It does not run OT scoring.
- It does not estimate learner state.
- It does not implement Python analysis.
- It does not assign correctness labels.

## Data Policy

`inserted_text`, `deleted_text`, and local contexts may contain writing fragments. Do not commit micro-episode outputs derived from real participant data.

