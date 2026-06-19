# Manual Logger E2E Check Guide

This guide describes how to check synthetic `logger-web` output with the Rust CLI pipeline.

## Data Rule

Use synthetic manual test text only.

Do not use production data, real participant data, real prompts, real names, email addresses, school names, addresses, or institution participant IDs.

Real-data testing is allowed only after the full pipeline is complete and only in a private local or institution-approved environment.

## Output Location

Downloaded logger output should be placed under:

```text
manual_outputs/logger_web/
```

`manual_outputs/` is ignored by Git. Do not commit manual output JSONL.

Some systems or browsers may create filenames with separators changed into colons. Files matching `manual_outputs:*` are also ignored.

## Rust CLI Pipeline

Run these commands from the repository root, replacing `<file>.jsonl` with the synthetic manual logger output:

```bash
cargo run -p kslog_cli -- validate manual_outputs/logger_web/<file>.jsonl
cargo run -p kslog_cli -- replay manual_outputs/logger_web/<file>.jsonl
cargo run -p kslog_cli -- extract manual_outputs/logger_web/<file>.jsonl
cargo run -p kslog_cli -- build-micro-episodes manual_outputs/logger_web/<file>.jsonl
cargo run -p kslog_cli -- audit-no-oracle manual_outputs/logger_web/<file>.jsonl
cargo run -p kslog_cli -- make-safe-view manual_outputs/logger_web/<file>.jsonl
```

## How To Read Errors

Validation errors usually point to schema, sequence, timestamp, cursor, selection, unknown-field, or forbidden-field problems.

Replay errors usually indicate document length, cursor, selection, inserted/deleted text, or hash consistency problems.

Extraction and micro-episode errors usually mean the event sequence passed schema validation but cannot yet be interpreted by the current deterministic Rust layers.

No-oracle audit output may report unsafe post-edit context for full `MicroEpisode` values. `make-safe-view` should not expose `local_context_after_observed`.

## Privacy Notes

Do not paste JSONL contents into docs, README files, issues, or chat.

CLI summaries are designed to avoid printing final text and local contexts. If future commands add detailed output, do not use those modes with real participant data in this repository.
