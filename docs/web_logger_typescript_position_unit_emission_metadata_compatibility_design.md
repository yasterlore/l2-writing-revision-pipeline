# TypeScript Logger Explicit position_unit Emission and Metadata Compatibility Design

## 1. Title

TypeScript Logger Explicit position_unit Emission and Metadata Compatibility
Design

## 2. Scope

This is a TypeScript logger compatibility design / docs-only Step. It makes no
TypeScript code changes, no Rust code changes, no Python code changes, no test
changes, no fixture JSON / JSONL changes, no Makefile changes, no
release-quality wrapper changes, no CI workflow changes, no Cargo.toml /
Cargo.lock changes, and no package.json changes.

This Step changes no logger behavior, validator behavior, schema behavior,
replay behavior, extract / micro_episode behavior, SHA-256 helper behavior, or
event durability behavior. It provides no production readiness proof, no
real-data readiness proof, and no model performance proof.

## 3. Design Status

The Rust validator Phase 2 chain is release-quality-integrated,
remote-status-recorded, and final-reviewed as of Step-web-logger-064.

TypeScript logger compatibility is not accepted yet. Step-web-logger-065
designs TypeScript emission and metadata compatibility only. It does not
implement TypeScript changes, does not create TypeScript/Rust compatibility
fixtures, and does not integrate anything into release-quality.

## 4. Current TypeScript Logger Audit Summary

Audited files:

- `apps/logger-web/src/rawEvent.ts`
- `apps/logger-web/src/main.ts`
- `apps/logger-web/tests/rawEvent.test.ts`
- `apps/logger-web/package.json`
- `apps/logger-web/tsconfig.json`
- `apps/logger-web/tsconfig.test.json`
- `apps/logger-web/README.md`
- `apps/logger-web/EXPLAINED.md`
- `Makefile`
- `scripts/check_release_quality.sh`

Current event construction is centered in `buildRawEvent` in
`apps/logger-web/src/rawEvent.ts`. Browser listeners in
`apps/logger-web/src/main.ts` call `recordEvent`, which snapshots the textarea,
builds `RawEvent` objects, keeps them in memory, and serializes them with
`toJsonl` when the user downloads JSONL.

Metadata-only audit table:

| Area | Current audit result | Compatibility status |
| --- | --- | --- |
| `position_unit` | Not found in audited TypeScript source/tests. | Missing field for Web logger v0.2-style Phase 1 / Phase 2 compatibility. |
| `logger_schema_version` | Emitted as `web_logger_schema_v0_1`. | Naming mismatch with Rust `kslog.raw_event.v1` / `kslog.raw_event.v2` policy boundary. |
| `research_schema_target` | Not found in audited TypeScript source/tests. | Missing field for Rust position-unit target gating. |
| `prompt_id` | Emitted in synthetic metadata. | Already present. |
| `doc_len_before` / `doc_len_after` | Emitted by `charCount`. | Present, but current `charCount` uses code point count, not UTF-16 code unit length. |
| cursor fields | `cursor_pos_before` / `cursor_pos_after` are emitted from selection start. | Likely API-compatible names, semantic tests missing. |
| selection fields | before/after selection start/end are emitted. | Likely API-compatible names, semantic tests missing. |
| text hashes | placeholder before/after hashes are emitted. | Present but not cryptographic compatibility evidence. |
| text context | before/after full text is kept internally as snapshots but not emitted as full text fields. | Good for output minimization; Rust Phase 2 uses sequence state and inserted/deleted text where possible. |
| inserted/deleted text | Limited inference is emitted. | Useful for Rust state reconstruction, but current slicing uses code point arrays and can drift from UTF-16 offsets. |
| safety | forbidden-field helper covers final/after/gold-style oracle field names in code; app docs require synthetic-only use. | Public-safe intent exists, but future compatibility output still needs tests. |

Current event listeners cover `focus`, `blur`, `keydown`, `keyup`,
`beforeinput`, `input`, `compositionstart`, `compositionupdate`,
`compositionend`, `paste`, and `selectionchange`. The TypeScript `EventType`
union includes `cut`, but no audited listener records cut. No audited
`copy` event type was found. No snapshot event type was found.

## 5. Required Event Metadata for Rust Validator Compatibility

For future Web logger v0.2-style events intended to satisfy the Rust
position-unit validators, the target metadata should include:

- `logger_schema_version` aligned with the Rust v0.2 boundary, currently
  `kslog.raw_event.v2`
- `research_schema_target=web_logger_position_unit_schema_v0.1` when the event
  is meant to be checked by the position-unit validator policy
- `position_unit=utf16_code_unit`
- `event_type`
- `seq`
- `timestamp_ms`
- `session_id`
- `participant_local_id`
- `task_id`
- `prompt_id`
- `is_composing`
- `quality_flags`
- `doc_len_before` and `doc_len_after` for events with document state
- `cursor_pos_before` and `cursor_pos_after` for offset-bearing events
- `selection_start_before`, `selection_end_before`,
  `selection_start_after`, and `selection_end_after` for selection-bearing
  events
- `input_type` where browser input events provide it
- `inserted_text` / `deleted_text` only when needed for synthetic state
  reconstruction and only within no-oracle boundaries
- `text_hash_before` / `text_hash_after` if retained as metadata, with hash
  compatibility treated as a separate chain

Offset/document metadata should be present for events that carry cursor,
selection, doc_len, inserted/deleted text, or text-hash metadata. Pure
lifecycle events may still emit `position_unit` for schema consistency if they
also include document-state metadata.

## 6. position_unit Emission Policy

Future TypeScript logger v0.2-style events should emit
`position_unit=utf16_code_unit` for all browser-originated events that contain
cursor, selection, doc_len, or text offset metadata. Because the current
logger emits doc_len and selection/cursor metadata for nearly all recorded
events, the simpler future policy should be to emit `position_unit` on all
v0.2-style raw events produced by the logger.

Missing `position_unit` should not be silently accepted for v0.2-style events.
Legacy event behavior should remain explicitly gated on the Rust side. The
TypeScript logger should not emit `byte_index` or `code_point`, should not
infer UTF-8 byte offsets in the browser, and should not normalize text for
offset calculation.

## 7. doc_len Policy

Future `doc_len_before` and `doc_len_after` should be JavaScript string
`.length` values of the relevant stored text state, interpreted as UTF-16 code
unit lengths. The before value must correspond to the pre-event text state,
and the after value must correspond to the post-event text state.

The current `charCount` implementation uses code point counting through array
spread. That is not compatible with Rust Phase 2 for emoji / surrogate-pair
cases and should be changed in a later implementation Step. Composition,
paste, selection edit, deletion, and replacement cases need explicit handling.
Line endings, tabs, trailing newline, emoji, Japanese text, and combining
sequences should be preserved as stored and should not be normalized away.

If an event type cannot reliably identify before/after text state, it should
either avoid doc_len fields or mark a bounded quality flag; it should not guess
text context.

## 8. Cursor / Selection Policy

Cursor offsets should come from browser selection APIs and be treated as
UTF-16 code unit offsets. `selection_start` and `selection_end` fields should
be emitted consistently for before and after snapshots.

Normal textarea/input APIs should not produce selection start greater than
selection end or offsets beyond document length, but future tests should cover
invalid synthetic cases on the Rust side. Surrogate-pair internal offsets
should not be emitted as valid boundaries. If browser APIs expose unusual
offset behavior in IME or platform-specific paths, future synthetic/manual UI
tests should capture the expected behavior without raw learner text.

No implicit normalization should occur.

## 9. Text Context / Hash Metadata Policy

Rust validator Phase 2 can validate doc_len against reconstructed state when
it has sufficient synthetic text context. It uses sequence state plus
inserted/deleted text where available, and falls back to bounded metadata
checks where full context is unavailable.

The current TypeScript logger stores before/after textarea text internally for
event construction but does not emit full before/after text fields. This is a
good output-minimization boundary. Future implementation should avoid emitting
full raw text in production/research outputs unless a separately reviewed
synthetic fixture path requires controlled synthetic bodies.

Hash-only metadata is not enough for every Phase 2 doc_len or surrogate
boundary check, but it can remain useful as metadata. Any real SHA-256
compatibility work should be a separate hash chain. Future compatibility
fixtures may include controlled synthetic text bodies if explicitly marked
synthetic-only and public-safe; real participant text must not be used.

No real participant data, no raw learner text from real users, no oracle
answer fields, no after-snapshot oracle fields, no gold-style labels, no
after-the-fact annotation fields, and no test-set tuning should be introduced.

## 10. Event-Type Compatibility Matrix

Metadata-only audit matrix:

| Event type | Emits `position_unit` now | Emits doc_len before/after now | Emits cursor offset now | Emits selection before/after now | Emits text hash now | Before/after text state available internally | Rust Phase 1 compatible | Rust Phase 2 compatible | Gap / action needed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| keydown | no | yes | yes | yes | yes | yes | no for v0.2 target | no for v0.2 target | Add v0.2 schema fields and UTF-16 doc_len. |
| keyup | no | yes | yes | yes | yes | yes | no for v0.2 target | no for v0.2 target | Add v0.2 schema fields and UTF-16 doc_len. |
| beforeinput | no | yes | yes | yes | yes | yes | no for v0.2 target | no for v0.2 target | Add v0.2 schema fields; preserve beforeinput snapshot. |
| input | no | yes | yes | yes | yes | yes | no for v0.2 target | no for v0.2 target | Add v0.2 schema fields; align inserted/deleted slicing to UTF-16 offsets. |
| compositionstart | no | yes | yes | yes | yes | yes | no for v0.2 target | no for v0.2 target | Add v0.2 schema fields and IME-focused UTF-16 tests. |
| compositionupdate | no | yes | yes | yes | yes | yes | no for v0.2 target | no for v0.2 target | Add v0.2 schema fields and IME-focused UTF-16 tests. |
| compositionend | no | yes | yes | yes | yes | yes | no for v0.2 target | no for v0.2 target | Add v0.2 schema fields and IME-focused UTF-16 tests. |
| selectionchange | no | yes | yes | yes | yes | yes | no for v0.2 target | no for v0.2 target | Add v0.2 schema fields and selection UTF-16 tests. |
| paste | no | yes | yes | yes | yes | yes | no for v0.2 target | no for v0.2 target | Add v0.2 schema fields; input event should carry paste text metadata when safe. |
| copy | not found | not found | not found | not found | not found | maybe | not applicable | not applicable | Decide whether copy is in scope; no current event type found. |
| cut | event type exists, listener not found | no observed emitted event | no observed emitted event | no observed emitted event | no observed emitted event | maybe | not currently | not currently | Add or defer cut listener; ensure deleted metadata is UTF-16 aligned. |
| focus | no | yes | yes | yes | yes | yes | no for v0.2 target | no for v0.2 target | Add v0.2 schema fields or reduce document metadata if lifecycle-only. |
| blur | no | yes | yes | yes | yes | yes | no for v0.2 target | no for v0.2 target | Add v0.2 schema fields or reduce document metadata if lifecycle-only. |
| snapshot | not found | not found | not found | not found | not found | maybe | not applicable | not applicable | Decide if snapshot events are future scope. |

## 11. TypeScript Test Design for Future Implementation

Future tests should cover:

- event includes `position_unit=utf16_code_unit`
- all offset-bearing events include `position_unit`
- Japanese doc_len uses UTF-16 code unit length
- emoji doc_len uses UTF-16 code unit length
- mixed Japanese and emoji offsets are preserved
- combining sequence is not normalized
- line endings, tabs, and trailing newline are preserved
- selection start/end are emitted consistently
- paste event metadata is UTF-16 based
- composition event metadata is UTF-16 based
- snapshot metadata is UTF-16 based if snapshot events include offsets/doc_len
- no `byte_index` or `code_point` position unit
- no raw learner text in public-safe logs
- synthetic-only fixtures

Do not implement tests in this Step.

## 12. TypeScript/Rust Compatibility Fixture Design

Recommended future fixture root:

`tests/fixtures/web_logger_typescript_position_unit_compatibility/`

The future fixture chain should allow:

- TypeScript emitted synthetic events
- Rust schema deserialization checks
- Rust validator Phase 1 checks
- Rust validator Phase 2 checks
- reuse or cross-reference of Unicode/hash vectors where appropriate
- metadata-only summaries
- no real participant data
- no raw learner text from real users

Fixture bodies may include controlled synthetic text only when needed to
exercise Rust UTF-16 state reconstruction and TypeScript emission behavior.
Such bodies must be marked synthetic-only and public-safe. If that is deemed
too risky for a particular fixture class, use metadata-only summaries and
separate body-suppressed expected-result files instead.

## 13. Makefile / Release-Quality Staging Design

Recommended future staging:

- Step-web-logger-066: implement TypeScript logger explicit `position_unit`
  emission and metadata alignment
- Step-web-logger-067: TypeScript position_unit test target design
- Step-web-logger-068: add TypeScript position_unit tests / npm target if
  needed
- Step-web-logger-069: TypeScript/Rust compatibility fixture design
- Step-web-logger-070: implement TypeScript/Rust compatibility fixture
  validation
- Step-web-logger-071: Makefile target design for TypeScript/Rust
  compatibility
- Step-web-logger-072: add Makefile target
- Step-web-logger-073: release-quality integration design
- Step-web-logger-074: release-quality wrapper integration
- Step-web-logger-075: remote run record workflow design
- Step-web-logger-076: status marker
- Step-web-logger-077: final safety review

This sequence keeps TypeScript implementation, TypeScript tests, cross-language
fixtures, Makefile exposure, wrapper integration, and remote evidence separate.

## 14. Relationship to Rust Validator Phase 2 Final Review

Step-web-logger-064 accepted the Rust validator Phase 2 chain only. TypeScript
compatibility remains outside that boundary. Step-web-logger-065 starts
TypeScript compatibility design. TypeScript compatibility cannot be inferred
from Rust validator tests alone.

## 15. Relationship to Replay

TypeScript metadata compatibility is not replay correctness. Replay integration
remains separate. TypeScript emitted offsets may later affect replay, but this
Step does not prove replay behavior.

## 16. Relationship to Extract / Micro Episode

This Step does not integrate TypeScript `position_unit` with `kslog_extract`.
This Step does not integrate TypeScript `position_unit` with
`kslog_micro_episode`. Downstream compatibility remains separate future work.

## 17. Relationship to SHA-256 / Hash Compatibility

This Step does not implement SHA-256 helpers and does not prove TypeScript/Rust
hash equivalence. Hash vector checks remain separate future work. If
`text_hash_after` remains relevant to event metadata, it should be handled by a
separate hash compatibility chain.

## 18. Relationship to Event Durability

This Step does not implement event durability. Queue / IndexedDB / ack / retry
/ dedup remain future work. Server idempotency / event_id dedup and sequence
reconciliation remain future work.

## 19. No-Oracle / Synthetic-Only Boundary

This design uses synthetic examples only. It uses no real participant data and
no raw learner text from real users. It introduces no oracle answer fields, no
after-snapshot oracle fields, no gold-style labels, no after-the-fact
annotation fields, no test-set tuning, and no model performance validation.
No-oracle constraints are not relaxed.

## 20. Public-Safe Documentation Boundary

This design records no raw logs, no full job output, no raw Cargo output, no
raw npm output blocks, no raw test output blocks, no raw fixture body, no full
event payload body, no real learner text, no real participant data, no private
path values, no absolute local path values, no logits / probabilities, and no
performance metric body.

## 21. Non-Equivalence Cautions

- design is not implementation
- TypeScript audit is not TypeScript compatibility proof
- TypeScript `position_unit` emission, even if later implemented, is not replay
  correctness
- TypeScript metadata compatibility is not extract / micro_episode integration
- TypeScript metadata compatibility is not SHA-256 compatibility
- TypeScript metadata compatibility is not event durability
- synthetic-only fixture pass is not real-data readiness
- release-quality pass is not production readiness

## 22. Non-Claims

This design does not claim production readiness, real-data readiness, data
collection readiness, deployment readiness, model performance, F1 attainment,
accuracy attainment, ECE attainment, AURCC attainment, TypeScript
compatibility completion, TypeScript explicit `position_unit` emission
implementation, TypeScript/Rust compatibility completion, replay correctness
completion, extract integration completion, micro_episode integration
completion, hash compatibility implementation completion, or event durability
implementation.

## 23. Residual Risks / Remaining Work

Remaining work:

- TypeScript implementation of `position_unit` emission
- TypeScript UTF-16 doc_len / selection / cursor metadata alignment
- TypeScript tests
- TypeScript/Rust compatibility fixtures
- Rust validator compatibility target for TypeScript-generated fixtures
- release-quality integration
- status marker / final safety review for the future compatibility chain
- extract / micro_episode integration
- SHA-256 compatibility
- event durability
- browser manual / synthetic UI verification
- future real-data readiness review only after separate prerequisite chains

## 24. Recommended Next Step

Recommended:

`Step-web-logger-066: implement TypeScript logger explicit position_unit emission and metadata alignment`

This is recommended because the audit did not find `position_unit` or
`research_schema_target` emission in the current TypeScript logger, and found
that current doc_len / diff slicing helpers use code point counting rather
than UTF-16 code unit semantics. Step066 should implement the bounded
TypeScript emission and metadata alignment only, without claiming
TypeScript/Rust compatibility, without changing Rust validator behavior,
without changing release-quality wrapper behavior, and without claiming
production or real-data readiness.

## 25. Step-web-logger-066 Implementation Follow-Up

Step-web-logger-066 implements the bounded TypeScript logger alignment
recommended by this design. The logger now emits `logger_schema_version` as
`kslog.raw_event.v2`, emits
`research_schema_target=web_logger_position_unit_schema_v0.1`, and emits
`position_unit=utf16_code_unit` for the scoped raw logger events.

The implementation changes document length metadata to JavaScript string
`.length`, preserving UTF-16 code unit semantics, and aligns inserted/deleted
text inference with UTF-16 code unit slicing from browser selection offsets.
Focused tests cover metadata emission, UTF-16 lengths, cursor/selection
preservation, JSONL serialization, and no-oracle field absence using only
small synthetic strings.

This follow-up does not add TypeScript/Rust compatibility fixture validation,
does not change Rust validator behavior, does not change replay behavior, does
not change Makefile or release-quality wrapper behavior, does not implement
extract / micro_episode integration, does not add SHA-256 helpers or vector
checks, does not implement event durability, and does not claim production
readiness, real-data readiness, or model performance evidence.
