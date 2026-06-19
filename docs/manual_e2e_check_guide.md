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

## Manual Synthetic Case Set

Run each case with synthetic text only. Save downloaded JSONL under `manual_outputs/logger_web/` or another ignored `manual_outputs/` path. Record only command summaries, not JSONL lines or text fragments.

### 1. simple_typing

Goal: check ordinary left-to-right typing.

Suggested synthetic text:

```text
I like music.
```

Steps:

1. Open `apps/logger-web`.
2. Focus the textarea.
3. Type the synthetic sentence from left to right.
4. Download JSONL as a manual output file.
5. Run the full Rust CLI pipeline listed above.

Expected focus:

- `validate` should pass.
- `replay` should pass and suppress final text.
- `extract` may classify ordinary insertions as non-revision-like insertions or unsupported browser events.

### 2. deletion

Goal: check deletion after ordinary typing.

Suggested synthetic text and edit:

```text
I likes music.
```

Steps:

1. Type the full synthetic sentence.
2. Move the cursor to the extra `s`.
3. Delete only the extra `s` so the intended synthetic result is `I like music.`.
4. Download JSONL.
5. Run the full Rust CLI pipeline.

Expected focus:

- `validate` should pass if `seq`, cursor positions, and document lengths are coherent.
- `replay` should confirm that delete events can be applied.
- `extract` should include deletion-like activity if the browser emitted enough information for the logger to infer it.

### 3. replacement

Goal: check replacing one phrase with another without using final corrected text as an oracle.

Suggested synthetic text and edit:

```text
I go school.
```

Steps:

1. Type the sentence.
2. Select or position around `go`.
3. Replace it with `go to`.
4. Download JSONL.
5. Run the full Rust CLI pipeline.

Expected focus:

- Replacement may appear as one replacement event or as delete plus insert depending on browser behavior.
- The current Rust layers should not require a gold final sentence.

### 4. selection_edit

Goal: check range selection edits.

Suggested synthetic text and edit:

```text
I enjoy musics.
```

Steps:

1. Type the sentence.
2. Select `musics`.
3. Replace it with `music`.
4. Download JSONL.
5. Run the full Rust CLI pipeline.

Expected focus:

- Selection ranges should be within document length.
- `extract` may classify the edit as `SelectionRangeEdit` or `Replacement`.

### 5. paste

Goal: check paste event capture without network or persistent browser storage.

Suggested synthetic phrase:

```text
synthetic phrase
```

Steps:

1. Copy the synthetic phrase from a local scratch area.
2. Focus the textarea.
3. Paste it.
4. Optionally type one short synthetic word before or after the pasted phrase.
5. Download JSONL.
6. Run the full Rust CLI pipeline.

Expected focus:

- `paste` should not send data anywhere.
- CLI output should remain summary-oriented.

### 6. cursor_movement

Goal: check edits away from the document end.

Suggested synthetic text and edit:

```text
I music.
```

Steps:

1. Type the sentence to the end.
2. Move the cursor between `I` and `music`.
3. Insert ` like`.
4. Download JSONL.
5. Run the full Rust CLI pipeline.

Expected focus:

- Cursor-before and cursor-after positions should remain in range.
- Replay should not assume every edit occurs at the end.

### 7. ime_composition_minimal

Goal: check IME composition boundaries with non-personal synthetic tokens.

Suggested synthetic token:

```text
synthetic-ime-token
```

Steps:

1. Enable an IME locally if needed.
2. Enter a short synthetic token only.
3. Avoid real names, places, personal phrases, or real participant-like content.
4. Complete composition so `compositionstart`, `compositionupdate`, and `compositionend` can be observed if the browser emits them.
5. Download JSONL.
6. Run the full Rust CLI pipeline.

Expected focus:

- IME handling is minimal in the first version.
- Passing validation/replay is more important than deep IME interpretation at this stage.

## Result Recording Format

Use `docs/manual_e2e_case_template.md` for a copyable record format. Keep records as summaries only. Do not paste JSONL lines, downloaded file contents, final text, local contexts, or text fragments from real data.

Use `docs/manual_e2e_case_results.md` to maintain the seven-case summary ledger after synthetic manual runs are complete.

Each case record should include:

- `case name`
- `manual file path`
- `validate result`
- `event count`
- `replay result`
- `final_doc_len`
- `extract summary`
- `micro_episode count`
- `audit-no-oracle result`
- `safe-view result`
- `schema mismatch`
- `notes`
- `whether JSONL was kept out of Git`

## Mismatch Triage

If a manual case fails, first identify the layer that failed:

- `validate` failure: inspect schema compatibility, unknown fields, forbidden fields, `seq`, timestamp order, cursor range, and selection range.
- `replay` failure: inspect `doc_len_before`, `doc_len_after`, cursor position, selected range, inserted text inference, and deleted text inference.
- `extract` failure: inspect whether the event passed replay but is unsupported by the first extraction rules.
- `build-micro-episodes` failure: inspect replay state availability and revision event spans.
- `audit-no-oracle` issue: distinguish expected full `MicroEpisode` warnings from forbidden field leakage.
- `make-safe-view` failure: inspect whether unsafe observed-after context accidentally entered the safe view.

Use the smallest reasonable fix. Prefer documenting a known browser/logger limitation when Rust behavior is correct. Change TypeScript logger logic only when the emitted RawEvent is malformed or inconsistent. Change Rust logic only when the deterministic pipeline rejects a valid schema-compatible event pattern that the current specs intend to support.

## How To Read Errors

Validation errors usually point to schema, sequence, timestamp, cursor, selection, unknown-field, or forbidden-field problems.

Replay errors usually indicate document length, cursor, selection, inserted/deleted text, or hash consistency problems.

Extraction and micro-episode errors usually mean the event sequence passed schema validation but cannot yet be interpreted by the current deterministic Rust layers.

No-oracle audit output may report unsafe post-edit context for full `MicroEpisode` values. `make-safe-view` should not expose `local_context_after_observed`.

## Privacy Notes

Do not paste JSONL contents into docs, README files, issues, or chat.

CLI summaries are designed to avoid printing final text and local contexts. If future commands add detailed output, do not use those modes with real participant data in this repository.
