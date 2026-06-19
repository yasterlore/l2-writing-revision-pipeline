# Text Replay Spec

This file documents the first deterministic text replay layer.

The implementation lives in `crates/kslog_replay/`.

## Responsibility

Text replay reconstructs document state from a validated sequence of `RawEvent` values.

The initial document state is the empty string. Events are processed in slice order, which should already be `seq` order after `kslog_validate`.

## Current State Updates

The first replay version supports:

- insertion from `inserted_text`
- deletion from `deleted_text`
- replacement when both `inserted_text` and `deleted_text` are present
- range replacement using `selection_start_before` and `selection_end_before`
- cursor-based insertion and deletion
- paste as an insertion event
- minimal IME composition handling

For IME, `composition_start` and `composition_update` are treated as non-committed text updates. `composition_end` can commit `inserted_text`.

## Current Checks

Replay checks:

- `doc_len_before` against current character count when present
- `doc_len_after` against updated character count when present
- edit cursor bounds
- edit selection bounds
- selected/deleted text consistency when `deleted_text` is present
- non-placeholder hash labels when present

## Character Count Policy

The first version uses Rust `char` count, meaning Unicode scalar value count. It does not use byte length.

Future versions may need grapheme cluster support for emoji, combining marks, and complex scripts.

## Hash Policy

Synthetic fixtures currently use placeholder labels such as `synthetic_hash_*`; replay skips those.

For non-placeholder hash labels, replay expects the deterministic format `kslog_fnv1a64:<hex>`.

## No-Oracle Note

`ReplayReport.final_text` is replay output. It must not be used as no-oracle input for candidate generation, ranking, OT scoring, or learner-state estimation.

Replay outputs derived from real participant data must not be committed to this repository.

## Authoritative Layer

Rust is authoritative for replay. Python may inspect replay outputs for analysis but must not become the validation or replay source of truth.
