# Manual Synthetic E2E Case Results

This file records summary-only results for the seven manual synthetic `logger-web` E2E cases.

No JSONL lines, downloaded JSONL contents, final text, local contexts, real participant data, real prompts, names, email addresses, school names, addresses, or institution participant IDs may be recorded here.

Manual output files must remain outside Git under ignored paths such as `manual_outputs/` or files matching `manual_outputs:*`.

## Current Status

As of this document update, all seven manual synthetic cases have been checked with the Rust CLI pipeline. The results below are summary-only records.

The manual JSONL contents are not pasted here. Some CLI error messages can include tiny text snippets; those snippets are intentionally paraphrased below as non-content error categories.

Note: the seven-case table below preserves the first manual run, including the pre-Step 16 replay mismatches. Step 17 reran the three previously failing cases after the Step 16 `logger-web` deletion-diff fix; those rerun results are recorded in the Step 17 section below.

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

## Replay Diagnostic Summary

`diagnose-replay` was applied to the three replay mismatch cases. The command output is content-suppressed and records metadata and lengths only.

These diagnostic rows describe pre-Step 16 manual outputs. They remain useful as historical triage evidence, but they are not a result for the updated logger.

| case name | replay_status | failure_line | failure_kind | source_seq | event_type | input_type | doc_len_before | doc_len_after | cursor_pos_before | cursor_pos_after | selection_before | selection_after | inserted_text_present | inserted_text_len | deleted_text_present | deleted_text_len | diff_op | quality_flags | content_suppressed | probable_layer | suggested_next_check |
| --- | --- | ---: | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| deletion | failed | 179 | deleted_text_mismatch | 179 | Input | DeleteContentBackward | 26 | 25 | 10 | 9 | 10..10 | 9..9 | false | 0 | true | 1 | Delete | none | true | logger_diff_estimation | Check synthetic-only logger diff inference for inserted/deleted text lengths and edit range metadata. |
| selection_edit | failed | 36 | deleted_text_mismatch | 36 | Input | DeleteContentBackward | 6 | 5 | 6 | 5 | 6..6 | 5..5 | false | 0 | true | 1 | Delete | none | true | logger_diff_estimation | Check synthetic-only logger diff inference for inserted/deleted text lengths and edit range metadata. |
| cursor_movement | failed | 97 | deleted_text_mismatch | 97 | Input | DeleteContentBackward | 14 | 13 | 7 | 6 | 7..7 | 6..6 | false | 0 | true | 1 | Delete | none | true | logger_diff_estimation | Check synthetic-only logger diff inference for inserted/deleted text lengths and edit range metadata. |

The shared pattern is a schema-valid `DeleteContentBackward` event with one deleted character recorded, but replay cannot reconcile the deleted-text metadata with the reconstructed state. The most likely first investigation point is `logger-web` diff estimation for deletion-like events.

## Step 16 Fix Summary

Rust replay remains strict.

`logger-web` was minimally changed so `input` events prefer the snapshot captured at `beforeinput`, preventing later selection events from replacing the true pre-edit state. `deleteContentBackward` inference now uses:

- the selected range from the before snapshot for selection deletion
- the cursor range from after-to-before for collapsed-cursor backspace
- generic text diff only as fallback

The three previously failing manual synthetic cases must be regenerated and rerun:

- `deletion`
- `selection_edit`
- `cursor_movement`

Record only summary output from the rerun.

## Step 17 Post-Fix Rerun Summary

After the Step 16 `logger-web` deletion-diff fix, the three cases that previously failed replay were rerun from summary-only CLI output. All three now pass the full Rust CLI pipeline.

No JSONL lines, text fragments, final text, or local context are recorded here. `manual_outputs/` remains Git-ignored.

| case name | validate | events | replay | final_doc_len | final_text_suppressed | extract | extract summary | build-micro-episodes | micro summary | audit-no-oracle | audit summary | make-safe-view | safe-view summary | replay mismatch | schema mismatch | JSONL kept out of Git | notes |
| --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deletion | ok | n/a | ok | n/a | true | ok | summary-only result provided; exact counts not recorded in shared summary | ok | summary-only result provided | ok | summary-only result provided | ok | summary-only result provided | resolved | none | yes | full pipeline passed after Step 16 |
| selection_edit | ok | 119 | ok | 14 | true | ok | revision_events=119; insertion=20; deletion=1; replacement=0; selection_range_edit=0; paste=0; composition_commit=0; unsupported=98 | ok | episodes=119; revision_like_episodes=1 | ok | issues=119; unsafe_or_blocking_issues=119 | ok | safe_views=119; candidate_generation_audit_issues=0 | resolved | none | yes | replay passed; still not classified as `selection_range_edit`, so classification coverage remains an improvement candidate |
| cursor_movement | ok | 107 | ok | 20 | true | ok | revision_events=107; insertion=20; deletion=0; replacement=0; selection_range_edit=0; paste=0; composition_commit=0; unsupported=87 | ok | episodes=107; revision_like_episodes=0 | ok | issues=107; unsafe_or_blocking_issues=107 | ok | safe_views=107; candidate_generation_audit_issues=0 | resolved | none | yes | replay passed; local edit from cursor movement may still not be captured as revision-like, so classification coverage remains an improvement candidate |

Conclusion:

- The earlier replay mismatches for `deletion`, `selection_edit`, and `cursor_movement` are resolved after the Step 16 logger fix.
- No RawEvent schema mismatch was reported for the rerun cases.
- Rust replay remained strict; the fix was on the logger-side deletion diff inference path.
- Remaining work is classification coverage, not replay compatibility.

## Step 16 Deletion Rerun Notes

Three post-fix deletion manual artifacts were added under ignored `manual_outputs/logger_web/` paths. Their filenames include the command name, so they appear to be separate manual outputs rather than one shared JSONL passed through the full pipeline.

| artifact label | command checked | result | event count | replay diagnostic | notes | JSONL kept out of Git |
| --- | --- | --- | ---: | --- | --- | --- |
| `validate manual_outputs:logger_web:deletion.jsonl` | `validate` | ok | 113 | `diagnose-replay` also reports ok | summary only; no JSONL content copied | yes |
| `replay manual_outputs:logger_web:deletion.jsonl` | `replay` | ok | 108 | `diagnose-replay` also reports ok | summary only; final text suppressed | yes |
| `build-micro-episodes manual_outputs:logger_web:deletion.jsonl` | `build-micro-episodes` | failed before micro-episode construction | n/a | `deleted_text_mismatch` at failure line/source seq 82; probable layer `logger_diff_estimation`; content suppressed | still needs focused deletion triage | yes |

Because these are separate files, the next check should regenerate one deletion JSONL with the updated logger and run the full command sequence against that same file:

```bash
cargo run -p kslog_cli -- validate manual_outputs/logger_web/<deletion-file>.jsonl
cargo run -p kslog_cli -- replay manual_outputs/logger_web/<deletion-file>.jsonl
cargo run -p kslog_cli -- diagnose-replay manual_outputs/logger_web/<deletion-file>.jsonl
cargo run -p kslog_cli -- extract manual_outputs/logger_web/<deletion-file>.jsonl
cargo run -p kslog_cli -- build-micro-episodes manual_outputs/logger_web/<deletion-file>.jsonl
cargo run -p kslog_cli -- audit-no-oracle manual_outputs/logger_web/<deletion-file>.jsonl
cargo run -p kslog_cli -- make-safe-view manual_outputs/logger_web/<deletion-file>.jsonl
```

Do not paste JSONL lines or text snippets from any failing command. Use `diagnose-replay` for replay failures.

This intermediate note is superseded by the Step 17 post-fix rerun summary above for the final replay-compatibility conclusion.

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
