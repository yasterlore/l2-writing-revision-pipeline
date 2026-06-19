# Manual Synthetic E2E Case Results

This file records summary-only results for the seven manual synthetic `logger-web` E2E cases.

No JSONL lines, downloaded JSONL contents, final text, local contexts, real participant data, real prompts, names, email addresses, school names, addresses, or institution participant IDs may be recorded here.

Manual output files must remain outside Git under ignored paths such as `manual_outputs/` or files matching `manual_outputs:*`.

## Current Status

As of this document update, all seven manual synthetic cases have been checked with the Rust CLI pipeline. The results below are summary-only records.

The manual JSONL contents are not pasted here. Some CLI error messages can include tiny text snippets; those snippets are intentionally paraphrased below as non-content error categories.

| case name | manual file path | validate result | event count | replay result | final_doc_len | extract summary | micro_episode count | audit-no-oracle result | safe-view result | schema mismatch | notes | JSONL kept out of Git |
| --- | --- | --- | ---: | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| simple_typing | `manual_outputs/logger_web/manual_outputs:logger_web:simple_typing.jsonl` | ok | 114 | ok | 21 | revision_events=114; insertion=21; unsupported=93 | 114 | ok; full `MicroEpisode` candidate-generation audit reports 114 unsafe issues due to observed-after context | ok; safe_views=114; `local_context_after_observed` absent; candidate audit issues=0 | none | final text suppressed; summary only | yes |
| deletion | `manual_outputs/logger_web/manual_outputs:logger_web:deletion.jsonl` | ok | 182 | failed: deleted-text consistency mismatch at seq 179 | n/a | blocked by replay failure | n/a | blocked by replay failure | blocked by replay failure | none at RawEvent schema level; replay consistency mismatch | likely logger deletion inference mismatch; no JSONL line copied | yes |
| replacement | `manual_outputs/logger_web/manual_outputs:logger_web:replacement.jsonl` | ok | 118 | ok | 14 | revision_events=118; insertion=20; deletion=1; replacement=0; unsupported=97 | 118 | ok; full `MicroEpisode` candidate-generation audit reports 118 unsafe issues due to observed-after context | ok; safe_views=118; `local_context_after_observed` absent; candidate audit issues=0 | none | manual replacement was represented as insertion/deletion events rather than `Replacement`; not a schema mismatch | yes |
| selection_edit | `manual_outputs/logger_web/manual_outputs:logger_web:selection_edit.jsonl` | ok | 168 | failed: deleted-text consistency mismatch at seq 36 | n/a | blocked by replay failure | n/a | blocked by replay failure | blocked by replay failure | none at RawEvent schema level; replay consistency mismatch | likely logger selected-range/deletion inference mismatch; no JSONL line copied | yes |
| paste | `manual_outputs/logger_web/manual_outputs:logger_web:paste.jsonl` | ok | 100 | ok | 15 | revision_events=100; insertion=15; paste=0; unsupported=85 | 100 | ok; full `MicroEpisode` candidate-generation audit reports 100 unsafe issues due to observed-after context | ok; safe_views=100; `local_context_after_observed` absent; candidate audit issues=0 | none | paste passed pipeline but was summarized as insertion/unsupported rather than `Paste`; extraction coverage gap | yes |
| cursor_movement | `manual_outputs/logger_web/manual_outputs:logger_web:cursor_movement.jsonl` | ok | 100 | failed: deleted-text consistency mismatch at seq 97 | n/a | blocked by replay failure | n/a | blocked by replay failure | blocked by replay failure | none at RawEvent schema level; replay consistency mismatch | likely logger deletion/edit inference around moved cursor mismatch; no JSONL line copied | yes |
| ime_composition_minimal | `manual_outputs/logger_web/manual_outputs:logger_web:ime_composition_minimal.jsonl` | ok | 72 | ok | 13 | revision_events=72; insertion=13; composition_commit=0; unsupported=59 | 72 | ok; full `MicroEpisode` candidate-generation audit reports 72 unsafe issues due to observed-after context | ok; safe_views=72; `local_context_after_observed` absent; candidate audit issues=0 | none | IME case passed pipeline but was not summarized as `CompositionCommit`; minimal IME interpretation remains limited | yes |

## Schema Mismatch Summary

No RawEvent schema mismatch was observed in the seven manual synthetic cases. All seven cases passed `validate`.

Three cases failed later in `replay` with deleted-text consistency mismatches:

- `deletion`
- `selection_edit`
- `cursor_movement`

These failures are not schema mismatches. They indicate that the browser/logger event stream was schema-valid but not yet replay-compatible for some deletion or cursor/selection edit patterns.

Minimal next fixes:

- Inspect `apps/logger-web` deletion and selection inference using synthetic-only manual cases.
- Keep Rust replay strict for now, because it is correctly surfacing deterministic consistency mismatches.
- If logger output is found to be internally coherent but replay is too narrow, make the smallest Rust replay adjustment and add a synthetic fixture test.
- Do not copy JSONL lines or text fragments into docs or issues.

## Failure Cases

### deletion

Failed layer: `replay`.

Reproduction condition: synthetic manual deletion case passes validation, then replay fails at a late sequence number with a deleted-text consistency mismatch.

Likely cause: logger inference for deletion text does not match the text state reconstructed by Rust replay.

Next fix: improve synthetic-only logger deletion inference or add a narrowly scoped replay rule if the emitted event sequence is valid by design.

### selection_edit

Failed layer: `replay`.

Reproduction condition: synthetic manual selection edit case passes validation, then replay fails early with a deleted-text consistency mismatch.

Likely cause: selected-range edit or deletion inference is not aligned with Rust replay expectations.

Next fix: inspect synthetic-only range edit metadata emitted by `logger-web`; adjust the logger first if it emits incomplete `deleted_text`.

### cursor_movement

Failed layer: `replay`.

Reproduction condition: synthetic manual cursor movement edit passes validation, then replay fails near the end with a deleted-text consistency mismatch.

Likely cause: moved-cursor edit inference may be recording deletion metadata that is not replay-compatible.

Next fix: add a focused synthetic manual reproduction and decide whether the logger should emit richer before/after edit metadata or replay should support the pattern.

## Non-Failing Coverage Gaps

The `paste` case passed the full pipeline but did not produce a `Paste` kind summary. The event sequence was treated as insertion/unsupported activity. This is a classification coverage gap, not a validation or replay failure.

The `ime_composition_minimal` case passed the full pipeline but did not produce a `CompositionCommit` kind summary. This matches the current minimal IME interpretation limit.

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
