# logger-web

`logger-web` is a minimal Vite + TypeScript browser logger for synthetic keystroke-level writing-process experiments.

It provides one `textarea`, records browser-side raw events in memory, and lets the user download synthetic raw event JSONL.

## Start

```bash
npm install
npm run dev
```

For build and checks:

```bash
npm run typecheck
npm test
npm run build
```

## Usage

1. Open the local Vite URL.
2. Type synthetic text into the textarea.
3. Review the event count summary.
4. Click `Download JSONL`.
5. Validate the downloaded file with Rust:

```bash
cargo run -p kslog_cli -- validate path/to/synthetic_session_web_001.raw_events.jsonl
```

For manual end-to-end checks, place downloaded synthetic JSONL under `manual_outputs/logger_web/` and follow `docs/manual_e2e_check_guide.md`. Use `docs/manual_e2e_case_template.md` to record summaries only.

## JSONL Output

Each JSONL line is intended to match the first `RawEvent` shape used by the Rust schema layer.

The logger records synthetic metadata:

- `logger_schema_version`
- `session_id`
- `participant_local_id`
- `task_id`
- `prompt_id`

It also records event type, sequence number, timestamp, input type when available, selection positions, cursor positions, document lengths, limited inserted/deleted text inference, placeholder hashes, diff operation hints, and quality flags.

## Timestamp Policy

The first version uses `Date.now()` for `timestamp_ms`. Rust validation remains authoritative for deterministic validation. Future versions may add a monotonic browser timestamp field if needed.

## What This App Does Not Do

- It does not send data to a server.
- It does not implement validation.
- It does not implement text replay.
- It does not extract revision events.
- It does not construct micro-episodes.
- It does not run no-oracle audit.
- It does not generate candidates or rank anything.
- It does not use React.

## Security and Privacy Notes

Use synthetic data only.

Do not use real participant data, real prompts, real names, email addresses, school names, addresses, or institution participant IDs.

The app does not use `localStorage`, does not send network requests, and does not log text content or JSONL to the console.

Downloaded JSONL can contain text fragments. Do not commit downloaded JSONL from real sessions to this repository.

Downloaded synthetic manual outputs should stay under `manual_outputs/`, which is ignored by Git.

Manual case summaries must not include JSONL lines or real text fragments. Keep only command results such as event counts, replay status, and safe-view status.
