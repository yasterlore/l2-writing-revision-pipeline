# Micro-Episode Spec

This file documents the first micro-episode construction layer.

The implementation lives in `crates/kslog_micro_episode/`.

## Responsibility

A `MicroEpisode` is a local analysis unit centered on one observed `RevisionEvent`.

It is not a correctness label. It does not directly represent a learner's internal state. It prepares structured local evidence for later candidate generation, OT scoring, evaluation, and learner-state estimation.

## Current Fields

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

## Local Context Policy

The first version uses a char-window context around the edit anchor.

Default window size is 30 chars before and after the anchor. This is a fixed initial setting, not a learned weight.

The implementation uses Rust `char` count rather than byte length. Future versions may need grapheme cluster, token-based, or sentence-based context.

## No-Oracle Policy

`local_context_before` may be safe for no-oracle candidate generation because it is pre-edit context.

`local_context_after_observed` is observed post-edit context. It is no-oracle unsafe for candidate generation and ranking. It is retained only for reconstruction checks and later evaluation workflows.

MicroEpisode must not contain fields named:

- `final_text`
- `observed_after_text`
- `gold_label`
- teacher corrections
- human corrections

## Data Policy

`inserted_text`, `deleted_text`, and local contexts may contain writing fragments. Micro-episode outputs derived from real participant data must not be committed to this repository.

## Forbidden Location

Micro-episode construction must not be implemented in the TypeScript logger.

## Current Limitations

The first version creates one micro-episode per `RevisionEvent`. It does not yet group multiple nearby revision events by pauses or discourse boundaries.
