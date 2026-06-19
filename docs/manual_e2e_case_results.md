# Manual Synthetic E2E Case Results

This file records summary-only results for the seven manual synthetic `logger-web` E2E cases.

No JSONL lines, downloaded JSONL contents, final text, local contexts, real participant data, real prompts, names, email addresses, school names, addresses, or institution participant IDs may be recorded here.

Manual output files must remain outside Git under ignored paths such as `manual_outputs/` or files matching `manual_outputs:*`.

## Current Status

As of this document update, the seven case summaries have not been provided in a summary-only form for recording here. The table below is therefore a prepared results ledger, not evidence that the cases passed.

Do not fill this table by reading manual JSONL contents. Update it only from user-shared synthetic manual E2E summaries or from CLI summaries that avoid text fragments.

| case name | validate result | event count | replay result | final_doc_len | extract summary | micro_episode count | audit-no-oracle result | safe-view result | schema mismatch | notes | JSONL kept out of Git |
| --- | --- | ---: | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| simple_typing | pending summary | n/a | pending summary | n/a | pending summary | n/a | pending summary | pending summary | unknown until summary is provided | summary not yet recorded | pending confirmation |
| deletion | pending summary | n/a | pending summary | n/a | pending summary | n/a | pending summary | pending summary | unknown until summary is provided | summary not yet recorded | pending confirmation |
| replacement | pending summary | n/a | pending summary | n/a | pending summary | n/a | pending summary | pending summary | unknown until summary is provided | summary not yet recorded | pending confirmation |
| selection_edit | pending summary | n/a | pending summary | n/a | pending summary | n/a | pending summary | pending summary | unknown until summary is provided | summary not yet recorded | pending confirmation |
| paste | pending summary | n/a | pending summary | n/a | pending summary | n/a | pending summary | pending summary | unknown until summary is provided | summary not yet recorded | pending confirmation |
| cursor_movement | pending summary | n/a | pending summary | n/a | pending summary | n/a | pending summary | pending summary | unknown until summary is provided | summary not yet recorded | pending confirmation |
| ime_composition_minimal | pending summary | n/a | pending summary | n/a | pending summary | n/a | pending summary | pending summary | unknown until summary is provided | summary not yet recorded | pending confirmation |

## Schema Mismatch Summary

No schema mismatch can be confirmed from this document yet because the seven summary records have not been provided.

When a summary reports a mismatch, record only:

- the failed pipeline layer
- the non-content error category
- the likely cause
- the smallest proposed fix
- whether the fix belongs in `apps/logger-web`, a Rust crate, or documentation

Do not paste the offending JSONL line.

## Failure Record Format

Use this format if a case fails. Keep it summary-only.

```text
case name:
failed command:
failed layer:
non-content error category:
reproduction condition:
likely cause:
minimal next fix:
schema mismatch:
JSONL kept out of Git:
notes:
```

## Privacy Checklist

Before marking a case as recorded:

- The result was derived from synthetic manual data only.
- The manual JSONL file was not added to Git.
- No JSONL line was pasted here.
- No final text or local context was pasted here.
- No real participant data or real prompt content was used.
- CLI output was summarized without text fragments.
- Any no-oracle issue was described as a policy category, not with content.
