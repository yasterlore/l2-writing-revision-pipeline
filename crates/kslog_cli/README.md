# kslog_cli

`kslog_cli` provides command-line entry points for the deterministic Rust side of the keystroke-log pipeline.

The CLI is intended for synthetic JSONL validation and pipeline checks before later Python candidate generation, OT scoring, or learner-state estimation.

## Install and Run

From the repository root:

```bash
cargo run -p kslog_cli -- validate tests/fixtures/synthetic/raw_events/valid/simple_typing.jsonl
```

The binary name is `kslog`.

## Commands

### validate

```bash
cargo run -p kslog_cli -- validate <input.jsonl>
```

Runs `kslog_validate` and prints a validation summary.

### replay

```bash
cargo run -p kslog_cli -- replay <input.jsonl>
```

Validates and replays the raw events. It prints only a summary, not the final replayed text.

### extract

```bash
cargo run -p kslog_cli -- extract <input.jsonl>
```

Runs revision-event extraction and prints kind counts.

### build-micro-episodes

```bash
cargo run -p kslog_cli -- build-micro-episodes <input.jsonl>
```

Builds micro-episodes and prints episode counts.

### audit-no-oracle

```bash
cargo run -p kslog_cli -- audit-no-oracle <input.jsonl>
```

Builds micro-episodes and audits them for `ForCandidateGeneration`.

### make-safe-view

```bash
cargo run -p kslog_cli -- make-safe-view <input.jsonl>
cargo run -p kslog_cli -- make-safe-view <input.jsonl> --exclude-observed-edit-text
```

Builds `NoOracleSafeEpisodeView` summaries. The first version does not export JSON.

## Synthetic Fixture Example

```bash
cargo run -p kslog_cli -- validate tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl
cargo run -p kslog_cli -- replay tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl
cargo run -p kslog_cli -- extract tests/fixtures/synthetic/raw_events/valid/replacement_case.jsonl
```

## Manual Logger E2E Check

Downloaded synthetic output from `apps/logger-web/` should be placed under:

```text
manual_outputs/logger_web/
```

Then run:

```bash
cargo run -p kslog_cli -- validate manual_outputs/logger_web/<file>.jsonl
cargo run -p kslog_cli -- replay manual_outputs/logger_web/<file>.jsonl
cargo run -p kslog_cli -- extract manual_outputs/logger_web/<file>.jsonl
cargo run -p kslog_cli -- build-micro-episodes manual_outputs/logger_web/<file>.jsonl
cargo run -p kslog_cli -- audit-no-oracle manual_outputs/logger_web/<file>.jsonl
cargo run -p kslog_cli -- make-safe-view manual_outputs/logger_web/<file>.jsonl
```

See `docs/manual_e2e_check_guide.md`.

For the recommended manual synthetic case set and summary-only record format, see `docs/manual_e2e_check_guide.md` and `docs/manual_e2e_case_template.md`.

## Privacy Notes

This CLI must be used with synthetic data in this repository.

Do not run this repository workflow on real participant data. Do not save CLI output derived from real participant data into the repository.

Replay, revision-event extraction, micro-episode construction, and safe views can involve writing fragments. The CLI intentionally prints summaries rather than final text or local contexts.

## What This CLI Does Not Do

- It does not implement the web logger.
- It does not implement Python candidate generation.
- It does not implement OT scoring.
- It does not estimate learner state.
- It does not process production or real participant data.
- It does not export safe-view JSON yet.
