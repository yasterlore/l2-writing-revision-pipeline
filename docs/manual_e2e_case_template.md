# Manual E2E Case Record Template

Use this template for synthetic manual logger checks only.

Do not paste JSONL lines, downloaded JSONL contents, final text, local contexts, real participant data, real prompts, names, email addresses, school names, addresses, or institution participant IDs.

`manual_outputs/` and `manual_outputs:*` are ignored by Git. Confirm manual JSONL stays out of Git before sharing a summary.

## Case Record

```text
case name:
manual file path:
validate result:
event count:
replay result:
final_doc_len:
extract summary:
micro_episode count:
audit-no-oracle result:
safe-view result:
schema mismatch:
notes:
JSONL kept out of Git:
```

## Command Checklist

Run these commands from the repository root. Replace `<file>.jsonl` with the ignored synthetic manual output path.

```bash
cargo run -p kslog_cli -- validate manual_outputs/logger_web/<file>.jsonl
cargo run -p kslog_cli -- replay manual_outputs/logger_web/<file>.jsonl
cargo run -p kslog_cli -- diagnose-replay manual_outputs/logger_web/<file>.jsonl
cargo run -p kslog_cli -- extract manual_outputs/logger_web/<file>.jsonl
cargo run -p kslog_cli -- build-micro-episodes manual_outputs/logger_web/<file>.jsonl
cargo run -p kslog_cli -- audit-no-oracle manual_outputs/logger_web/<file>.jsonl
cargo run -p kslog_cli -- make-safe-view manual_outputs/logger_web/<file>.jsonl
```

## Allowed Summary Example

This example shows the shape of a summary. It is not JSONL data.

```text
case name: simple_typing
manual file path: manual_outputs/logger_web/simple_typing_manual.jsonl
validate result: ok
event count: 77
replay result: ok
final_doc_len: 14
extract summary: insertion=14, unsupported=63
micro_episode count: 77
audit-no-oracle result: expected unsafe issues for full MicroEpisode candidate-generation audit
safe-view result: ok, local_context_after_observed not present
schema mismatch: none
notes: synthetic manual text only
JSONL kept out of Git: yes
```

## Forbidden Record Content

Do not include:

- JSONL lines
- Full downloaded files
- Real participant text
- Real participant metadata
- Final corrected text as an oracle
- `final_text`, `observed_after_text`, `gold_label`, or teacher correction content
- Local contexts from real data
