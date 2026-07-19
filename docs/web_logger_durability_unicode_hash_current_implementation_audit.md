# Web Logger Durability, Unicode Position, and Text Hash Current Implementation Audit

## 1. Title

Web Logger Durability, Unicode Position, and Text Hash Current Implementation Audit

## 2. Scope

This is an audit-only / docs-only review of the current implementation against `docs/web_logger_durability_unicode_hash_safety_design.md`.

This audit makes no TypeScript code changes, no Rust code changes, no Python code changes, no tests changes, no fixture JSON changes, no schema implementation changes, no Makefile changes, no CI workflow changes, and no release-quality wrapper changes.

This audit uses no real data, makes no production readiness claim, and makes no real-data readiness claim.

## 3. Audit Method

Audited directories and files:

- `apps/logger-web/`
- `apps/logger-web/src/rawEvent.ts`
- `apps/logger-web/src/main.ts`
- `apps/logger-web/tests/rawEvent.test.ts`
- `apps/logger-web/README.md`
- `apps/logger-web/EXPLAINED.md`
- `crates/kslog_schema/`
- `crates/kslog_validate/`
- `crates/kslog_replay/`
- `crates/kslog_extract/`
- `crates/kslog_micro_episode/`
- `crates/kslog_no_oracle_audit/`
- `crates/kslog_cli/`
- `docs/04_raw_event_schema.md`
- `docs/05_text_replay_spec.md`
- `tests/fixtures/synthetic/raw_events/README.md`

Representative `rg` keyword groups used:

- durability: `IndexedDB`, `indexedDB`, `localStorage`, `sendBeacon`, `fetch`, `beforeunload`, `pagehide`, `visibilitychange`, `queue`, `retry`, `ack`, `batch`, `event_id`, `duplicate seq`, `seq_gap`
- position units: `selectionStart`, `selectionEnd`, `selection_start`, `selection_end`, `cursor_pos`, `position_unit`, `utf16`, `UTF-16`, `char_indices`, `char_count`, `grapheme`
- hash: `text_hash`, `sha`, `sha256`, `crypto`, `digest`, `hash`
- tests: `emoji`, `surrogate`, `combining`, `CRLF`, `LF`, `tab`, `unicode`, `malformed`, `seq gap`

Status policy:

- `implemented and tested`: current code and tests show the requirement exists and is exercised.
- `partially implemented`: current code supports part of the requirement, but important pieces from the design are missing.
- `design documented but not implemented`: the safety design records the requirement, but current implementation does not provide it.
- `not found in current implementation`: no current implementation evidence was found in audited files.
- `unclear from current files`: current files do not provide enough evidence; this audit does not infer missing behavior.

## 4. Executive Summary

| area | current status | summary |
| --- | --- | --- |
| event durability | partially implemented | The Web logger records `session_id`, in-memory `seq`, timestamps, and downloadable JSONL. It does not send to a server and does not implement durable queue, IndexedDB, ack, retry, batch send, deduplication, or server-side idempotency. Rust validation checks consecutive `seq` in input order, but no network durability layer was found. |
| Unicode position unit | partially implemented | Browser `selectionStart` / `selectionEnd` are captured, and Rust avoids byte slicing by using Rust `char` counts and `char_indices` conversion. However, schema does not declare `position_unit=utf16_code_unit`, TypeScript document length uses code point counting, Rust interprets positions as Rust character counts, and no shared UTF-16 code unit to UTF-8 byte conversion helper was found. |
| text hash canonicalization | partially implemented | Schema fields and replay hash mismatch checks exist, but Web logger emits placeholder hash labels. Rust replay uses an internal FNV-1a-style label for non-placeholder hashes, while the safety design requires SHA-256 over exact UTF-8 stored text with lowercase hex. Shared TypeScript / Rust hash vectors were not found. |

## 5. Current Event Durability Audit

| item | status | evidence files | current behavior | missing pieces | risk if left unresolved | recommended future implementation step |
| --- | --- | --- | --- | --- | --- | --- |
| client-side event queue | partially implemented | `apps/logger-web/src/main.ts`, `apps/logger-web/EXPLAINED.md` | Events are kept in an in-memory array until manual download. | Durable queue with retry state. | Browser/tab loss can discard pending events. | Stage 5 TypeScript queue and persistence implementation. |
| durable temporary storage using IndexedDB | not found in current implementation | `apps/logger-web/README.md`, `apps/logger-web/EXPLAINED.md` | Docs explicitly describe in-memory storage and no long-term browser storage. | IndexedDB-backed event store. | Pending events can be lost during page lifecycle or crash. | Stage 5 IndexedDB-backed queue. |
| localStorage fallback, if any | not found in current implementation | `apps/logger-web/README.md`, `apps/logger-web/EXPLAINED.md` | Docs state no `localStorage` use. | Explicit fallback decision and tests if introduced later. | No durable fallback exists. | Decide whether fallback is forbidden or staged separately. |
| batch sending | not found in current implementation | `apps/logger-web/src/main.ts`, `apps/logger-web/README.md` | The app downloads a Blob; no server send path was found. | Batch API, batch ids, request limits. | No network durability path exists. | Stage 6 ack / retry / dedup / seq reconciliation. |
| server acknowledgement | not found in current implementation | `apps/logger-web/src/main.ts` | No server request/response code was found. | Ack protocol and `acked_seq` metadata. | Client cannot know what server durably accepted. | Stage 6 server acknowledgement design and implementation. |
| retry with backoff | not found in current implementation | `apps/logger-web/src/main.ts` | No retry loop was found. | Retry state, backoff, retry count, terminal failure status. | Temporary outage can cause event loss. | Stage 6 retry implementation with fault tests. |
| event_id | not found in current implementation | `apps/logger-web/src/rawEvent.ts`, `crates/kslog_schema/src/lib.rs` | `RawEvent` includes `session_id` and `seq`, but not `event_id`. | Stable per-event id. | Cannot deduplicate retry collisions by event id. | Stage 1 schema clarification, then Stage 5 event id generation. |
| session_id | implemented and tested | `apps/logger-web/src/rawEvent.ts`, `apps/logger-web/tests/rawEvent.test.ts`, `crates/kslog_schema/src/lib.rs` | TypeScript and Rust schemas include `session_id`; TS tests check a synthetic session id. | Session boundary reconciliation across batches. | Session mixing can still occur without server validation. | Add server-side session/seq validation in Stage 6. |
| seq | implemented and tested | `apps/logger-web/src/main.ts`, `apps/logger-web/tests/rawEvent.test.ts`, `crates/kslog_validate/src/lib.rs` | TypeScript increments `seq`; Rust validator checks consecutive sequence in input order. | Server reconciliation and ordering after out-of-order transport. | Out-of-order arrival may be rejected or misinterpreted unless sorted after dedup. | Stage 6 server seq reconciliation. |
| monotonic client sequence | partially implemented | `apps/logger-web/src/main.ts` | A local counter increments per event and resets on clear. | Durability across reloads, persisted last seq, conflict checks. | Reload or crash can lose sequence continuity. | Stage 5 persisted queue and seq state. |
| deduplication by event_id | not found in current implementation | audited TS/Rust files | No `event_id` field or dedup path was found. | Idempotency key and duplicate handling. | Retries can create duplicate event rows. | Stage 6 dedup logic. |
| duplicate seq detection | partially implemented | `crates/kslog_validate/src/lib.rs` | Non-consecutive `seq` causes `SequenceGap`; duplicate seq in input order also fails as an unexpected sequence. | Explicit duplicate category, duplicate same/different event handling. | Duplicate diagnosis is not specific and cannot compare event identity. | Stage 4/6 explicit duplicate seq detection. |
| seq gap detection | implemented and tested | `crates/kslog_validate/src/lib.rs`, `tests/fixtures/synthetic/raw_events/README.md` | Validator has a `SequenceGap` error and tests for a seq gap fixture. | Cross-batch reconciliation and server summaries. | Current protection applies only to validation input, not transport storage. | Keep validator check; add server/client reconciliation. |
| out-of-order arrival handling | not found in current implementation | `apps/logger-web/src/main.ts`, `crates/kslog_validate/src/lib.rs` | No network arrival layer exists. Validator expects input order to be consecutive. | Server should sort or reconstruct by client seq after dedup. | Arrival order could become de facto order in a future server if not specified. | Stage 6 server ordering policy implementation. |
| server-side last accepted seq summary | not found in current implementation | audited TS/Rust files | No server acknowledgement layer found. | Accepted seq summary. | Client cannot reconcile accepted vs pending events. | Stage 6 ack response metadata. |
| client/server seq reconciliation | not found in current implementation | audited TS/Rust files | No client/server protocol found. | Reconciliation after reconnect and retries. | Gaps can persist unnoticed until replay/validation. | Stage 6 reconciliation tests. |
| flush on pagehide / visibilitychange / beforeunload | not found in current implementation | `apps/logger-web/src/main.ts` | No lifecycle flush listener was found. | Best-effort flush from durable queue. | Pending events can remain unsent on tab close. | Stage 5/6 lifecycle flush design and tests. |
| sendBeacon usage and limitations | not found in current implementation | `apps/logger-web/src/main.ts` | No `sendBeacon` use was found. | Decide whether it is allowed as best-effort only. | A future implementation may overtrust lifecycle send behavior. | Stage 5 design explicitly documents limitations. |
| server-side idempotent write behavior | not found in current implementation | audited files | No server write path found. | Idempotent append/write transaction. | Duplicate retries and partial writes can corrupt logs. | Stage 6 server write design. |
| JSONL partial write detection | partially implemented | `crates/kslog_validate/src/lib.rs` | Malformed JSON lines are rejected during validation; line length is capped. | Server append atomicity, truncated write repair/quarantine policy. | Partial server writes may only be caught later. | Stage 6/7 server partial write simulation. |
| arrival order vs client seq ordering | partially implemented | `docs/05_text_replay_spec.md`, `crates/kslog_validate/src/lib.rs` | Replay docs say events should already be `seq` order; validator enforces consecutive seq in current input order. | Explicit server sorting by client seq after dedup. | Future server may preserve arrival order and fail/replay incorrectly. | Stage 1 schema/order clarification and Stage 6 server implementation. |

## 6. Current Event Ordering Audit

- Client seq is present and monotonic in the current Web logger session, but not persisted across browser lifecycle failures.
- Arrival order is not represented in the current Web logger because there is no server send path. Rust validation operates on the order of JSONL lines it receives.
- Timestamp is checked for monotonic non-decrease in `crates/kslog_validate/src/lib.rs`. It is not the sole ordering key, but it is currently a validation constraint rather than diagnostic-only metadata.
- Replay processes events in slice order. `docs/05_text_replay_spec.md` states this should already be `seq` order after validation.
- Validation checks sequence gaps and inversions as non-consecutive `seq`; explicit duplicate event id handling is not available because no `event_id` exists.
- Session boundary handling exists as a `session_id` field, but validator evidence for rejecting mixed `session_id` values within one file was not found in the audited implementation.

## 7. Current UTF-16 Position Unit Audit

| item | status | evidence files | current behavior | missing pieces | risk if left unresolved | recommended future implementation step |
| --- | --- | --- | --- | --- | --- | --- |
| selection_start field | partially implemented | `apps/logger-web/src/rawEvent.ts`, `crates/kslog_schema/src/lib.rs` | TS emits before/after selection starts; Rust schema accepts them. | Unit declaration. | TS/Rust may interpret the same value differently. | Stage 1 schema clarification. |
| selection_end field | partially implemented | `apps/logger-web/src/rawEvent.ts`, `crates/kslog_schema/src/lib.rs` | TS emits before/after selection ends; Rust schema accepts them. | Unit declaration. | Selection ranges can drift for non-ASCII text. | Stage 1 schema clarification. |
| cursor_pos field | partially implemented | `apps/logger-web/src/rawEvent.ts`, `crates/kslog_schema/src/lib.rs` | TS maps cursor to selection start; Rust schema accepts before/after cursor positions. | Unit declaration and conversion helper. | Replay/edit span can be wrong for surrogate pairs or combining marks. | Stage 3 Rust UTF-16 conversion helper. |
| edit span fields | partially implemented | `crates/kslog_extract/src/lib.rs`, `crates/kslog_micro_episode/src/lib.rs` | Extract and micro-episode layers use cursor/selection-derived spans. | UTF-16-aware span policy. | Downstream revision spans may inherit wrong offsets. | Stage 4 fail-closed replay/extract behavior. |
| current schema-declared unit | not found in current implementation | `docs/04_raw_event_schema.md`, `crates/kslog_schema/src/lib.rs` | No `position_unit` field found in schema. | `position_unit=utf16_code_unit`. | Unit ambiguity remains. | Stage 1 schema clarification. |
| browser source unit | partially implemented | `apps/logger-web/src/rawEvent.ts` | Browser `selectionStart` / `selectionEnd` are captured. | Docs/schema declaration of browser unit. | Browser values may be assumed to be Rust chars. | Stage 1 docs/schema alignment. |
| Rust interpretation | partially implemented | `crates/kslog_replay/src/lib.rs`, `docs/05_text_replay_spec.md` | Rust uses `char_count`, `slice_chars`, and `char_to_byte_index`; this is Unicode scalar value count, not UTF-16 code unit count. | UTF-16 code unit offset conversion. | Positions after surrogate pairs can be incorrect. | Stage 3 helper and tests. |
| byte-index usage risk | partially implemented | `crates/kslog_replay/src/lib.rs`, `crates/kslog_micro_episode/src/lib.rs` | Rust converts char index to byte index before `replace_range`; it does not directly treat positions as byte offsets. | The source position unit is still mismatched. | Safer than byte indexing, but still not the browser unit. | Stage 3 conversion helper. |
| existing UTF-16 to UTF-8 conversion helper | not found in current implementation | audited Rust files | No helper using UTF-16 code unit offsets was found. | Shared validated conversion helper. | Non-BMP character positions can be misapplied. | Stage 3 helper. |
| invalid offset handling | partially implemented | `crates/kslog_validate/src/lib.rs`, `crates/kslog_replay/src/lib.rs` | Out-of-range and inverted ranges can fail. | Invalid UTF-16 boundary handling. | Offset validation cannot catch code-unit boundary errors. | Stage 4 fail-closed invalid offset behavior. |
| out-of-range offset handling | implemented and tested | `crates/kslog_validate/src/lib.rs`, `crates/kslog_replay/src/lib.rs` | Cursor/selection out-of-bounds checks exist and are tested. | Unit-specific out-of-range tests. | Existing checks are only as good as the chosen length unit. | Stage 3/4 shared vectors. |
| surrogate pair handling | not found in current implementation | audited tests | No targeted surrogate-pair test found. | Shared vectors for emoji / non-BMP text. | Browser/Rust mismatch can silently alter replay. | Stage 2/3 shared test vectors. |
| combining mark handling | not found in current implementation | audited tests | No targeted combining-mark test found. | Combining boundary policy and vectors. | Grapheme display can diverge from stored offsets. | Stage 2/3 shared test vectors. |
| CRLF / LF handling | partially implemented | `docs/web_logger_durability_unicode_hash_safety_design.md`, `crates/kslog_validate/src/lib.rs` | Validator trims JSONL line endings; text normalization policy is design-only. | Raw text newline preservation tests. | Text offsets/hash can diverge if newline normalization appears later. | Stage 2 shared vectors and Stage 4 replay tests. |
| tab handling | not found in current implementation | audited tests | No targeted tab offset test found. | Tab vector and policy tests. | Offset assumptions may drift in display vs stored string. | Stage 2 shared vectors. |
| Unicode normalization policy | design documented but not implemented | `docs/web_logger_durability_unicode_hash_safety_design.md` | Safety design says no normalization by default. | Schema field/policy enforcement and tests. | Hash and offsets can diverge silently. | Stage 1 schema clarification and Stage 2 vectors. |
| grapheme cluster policy | design documented but not implemented | `docs/05_text_replay_spec.md`, `docs/web_logger_durability_unicode_hash_safety_design.md` | Current docs note Rust char count and future grapheme concerns; safety design says grapheme display length is not the stored index unit. | Explicit schema wording and tests. | UI display positions can be conflated with stored offsets. | Stage 1 docs/schema alignment. |

## 8. Current Text Hash Audit

| item | status | evidence files | current behavior | missing pieces | risk if left unresolved | recommended future implementation step |
| --- | --- | --- | --- | --- | --- | --- |
| text_hash_before field | partially implemented | `apps/logger-web/src/rawEvent.ts`, `crates/kslog_schema/src/lib.rs` | Field exists in TypeScript and Rust schemas. | Canonical algorithm metadata and real helper. | Field can carry incompatible values. | Stage 1 schema clarification and Stage 2 helper. |
| text_hash_after field | partially implemented | `apps/logger-web/src/rawEvent.ts`, `crates/kslog_schema/src/lib.rs` | Field exists in TypeScript and Rust schemas. | Canonical algorithm metadata and real helper. | Replay mismatch may be false or missed. | Stage 1/2. |
| hash algorithm | partially implemented | `apps/logger-web/src/rawEvent.ts`, `crates/kslog_replay/src/lib.rs`, `docs/05_text_replay_spec.md` | TS emits placeholders; Rust non-placeholder hash uses a `kslog_fnv1a64` label. | SHA-256 canonical policy implementation. | TypeScript and Rust hashes will not match the safety design. | Stage 2 SHA-256 helpers. |
| input encoding | partially implemented | `crates/kslog_replay/src/lib.rs` | Rust hash uses `text.as_bytes()`, i.e. UTF-8 bytes. | TypeScript helper and explicit schema metadata. | Cross-language mismatch remains possible. | Stage 2 shared vectors. |
| newline handling | design documented but not implemented | `docs/web_logger_durability_unicode_hash_safety_design.md` | Safety design says no newline normalization. | Helper tests for CRLF / LF / trailing newline. | Hash mismatch across platforms. | Stage 2 vectors. |
| Unicode normalization handling | design documented but not implemented | `docs/web_logger_durability_unicode_hash_safety_design.md` | Safety design says no Unicode normalization. | Helper tests for combining vs precomposed forms. | Semantically similar text can hash differently without explicit policy. | Stage 2 vectors and docs. |
| trailing newline handling | design documented but not implemented | `docs/web_logger_durability_unicode_hash_safety_design.md` | Safety design says preserve as-is. | Test vector. | Hash drift for text ending in newline. | Stage 2 vectors. |
| empty string handling | design documented but not implemented | `docs/web_logger_durability_unicode_hash_safety_design.md` | Safety design says SHA-256 of empty UTF-8 byte sequence. | Test vector. | Initial state checks can diverge. | Stage 2 vectors. |
| output format | partially implemented | `crates/kslog_replay/src/lib.rs`, `docs/05_text_replay_spec.md` | Rust expects `kslog_fnv1a64:<hex>` for non-placeholder values. | Lowercase SHA-256 hex without prefix, or explicit final schema choice. | Format mismatch across TS/Rust. | Stage 1/2. |
| TypeScript hash helper | not found in current implementation | `apps/logger-web/src/rawEvent.ts` | Only `placeholderHash` found. | Web Crypto or equivalent SHA-256 helper. | Logger cannot emit canonical hashes. | Stage 2 TypeScript helper. |
| Rust hash helper | partially implemented | `crates/kslog_replay/src/lib.rs` | Existing deterministic helper is FNV-1a-style, not SHA-256. | SHA-256 helper matching TypeScript. | Replay cannot validate safety-design hashes. | Stage 2 Rust helper. |
| replay hash verification | partially implemented | `crates/kslog_replay/src/lib.rs` | Replay verifies non-placeholder hash labels and reports before/after mismatch. | Canonical SHA-256 policy and tests. | Verification may reject future canonical values or accept incompatible legacy labels. | Stage 4 replay validation update. |
| shared test vectors | not found in current implementation | audited tests | No shared TypeScript / Rust hash vector set was found. | Synthetic vector file and cross-language checks. | Compatibility can regress silently. | Stage 2 shared test vector implementation. |
| CI cross-language hash check | not found in current implementation | audited docs/files | No cross-language hash CI check found in current audited surfaces. | CI target after helpers exist. | Mismatch may reach later stages. | Stage 8 end-to-end synthetic validation. |

## 9. Current Test Coverage Audit

| test area | current status | evidence |
| --- | --- | --- |
| TypeScript logger tests | partially implemented | `apps/logger-web/tests/rawEvent.test.ts` covers RawEvent builder shape, sequence, simple insertion/deletion inference, forbidden field absence, and JSONL serialization. |
| Rust schema tests | implemented and tested | `crates/kslog_schema/src/lib.rs` tests schema serialization/deserialization and rejection of forbidden unknown fields. |
| Rust replay tests | partially implemented | `crates/kslog_replay/src/lib.rs` tests valid synthetic replay, doc length mismatch, cursor/range errors, and content-suppressed diagnostics. |
| Rust validation tests | implemented and tested | `crates/kslog_validate/src/lib.rs` tests malformed JSON, missing required field, forbidden field, seq gap, timestamp inversion, cursor/selection range errors, empty line, and line length. |
| Unicode offset tests | not found in current implementation | No targeted UTF-16 / UTF-8 offset vector tests found. |
| emoji / surrogate pair tests | not found in current implementation | No targeted non-BMP position test found. |
| combining mark tests | not found in current implementation | No targeted combining mark vector test found. |
| CRLF / LF tests | not found in current implementation | JSONL line trimming exists, but stored-text newline vector tests were not found. |
| tab tests | not found in current implementation | No targeted tab vector test found. |
| hash canonicalization tests | not found in current implementation | No SHA-256 canonical hash tests found. |
| TypeScript / Rust shared test vectors | not found in current implementation | No shared cross-language vector set found. |
| retry / dedup / ack tests | not found in current implementation | No network durability layer found. |
| seq gap / duplicate seq tests | partially implemented | Seq gap tests exist; explicit duplicate seq category tests were not found. |
| malformed JSONL / partial write tests | partially implemented | Malformed JSON and line length tests exist; server partial write simulation was not found. |
| no-oracle forbidden field tests | implemented and tested | TypeScript, schema, validator, and no-oracle-related Rust tests include forbidden-field checks. |
| public-safe summary tests | partially implemented | Existing CLI and diagnostic tests suppress replay content in selected outputs; this audit did not find Web logger public-safe summary tests beyond RawEvent shape tests. |

## 10. Gap Matrix

| area | requirement | current status | evidence | gap | risk | proposed future step | priority |
| --- | --- | --- | --- | --- | --- | --- | --- |
| event durability | event queue / retry / ack / dedup | not found in current implementation | `apps/logger-web/src/main.ts`, `apps/logger-web/README.md` | No durable network path. | Event loss or duplication under outage. | Stage 5 and Stage 6 | P0 pre-collection blocker |
| event ordering | client seq authoritative ordering | partially implemented | `apps/logger-web/src/main.ts`, `crates/kslog_validate/src/lib.rs` | Seq exists, but server sorting/reconciliation absent. | Arrival order can be mistaken for canonical order in future server path. | Stage 1 and Stage 6 | P0 pre-collection blocker |
| event ordering | explicit duplicate seq detection | partially implemented | `crates/kslog_validate/src/lib.rs` | Duplicate seq collapses into general sequence mismatch. | Ambiguous failure category. | Stage 4/6 | P0 pre-collection blocker |
| event durability | event_id deduplication | not found in current implementation | `crates/kslog_schema/src/lib.rs` | No `event_id`. | Retry dedup cannot be robust. | Stage 1/5/6 | P0 pre-collection blocker |
| Unicode position | UTF-16 code unit schema clarification | not found in current implementation | `docs/04_raw_event_schema.md`, `crates/kslog_schema/src/lib.rs` | No `position_unit` field or policy. | Browser and Rust units diverge. | Stage 1 | P0 pre-collection blocker |
| Unicode position | Rust UTF-16 to UTF-8 safe conversion | not found in current implementation | `crates/kslog_replay/src/lib.rs` | Existing conversion is Rust char index to byte index. | Non-BMP positions can replay incorrectly. | Stage 3 | P0 pre-collection blocker |
| Unicode position | invalid offset fail-closed behavior | partially implemented | `crates/kslog_validate/src/lib.rs`, `crates/kslog_replay/src/lib.rs` | Range checks exist, but UTF-16 invalid boundary checks absent. | Invalid offsets can pass as a different unit. | Stage 4 | P0 pre-collection blocker |
| hash | text hash canonicalization | partially implemented | `apps/logger-web/src/rawEvent.ts`, `crates/kslog_replay/src/lib.rs` | Placeholder TS hashes and Rust FNV-1a-style helper do not match SHA-256 policy. | Replay hash checks can be incompatible. | Stage 2 | P0 pre-collection blocker |
| hash | TypeScript / Rust shared test vectors | not found in current implementation | audited tests | No shared vector set. | Cross-language regressions can go unnoticed. | Stage 2 | P0 pre-collection blocker |
| hash | hash verification in replay | partially implemented | `crates/kslog_replay/src/lib.rs` | Verification exists but not with SHA-256 canonical policy. | False mismatch or false acceptance. | Stage 4 | P0 pre-collection blocker |
| tests | failure injection for transport | not found in current implementation | audited tests | No offline/retry/partial write tests. | Data loss path untested. | Stage 7 | P1 before pilot |
| tests | Unicode vectors for emoji/combining/newline/tab | not found in current implementation | audited tests | No targeted vectors. | Offset/hash mismatch untested. | Stage 2/3 | P0 pre-collection blocker |
| docs | public-safe reporting policy for logger audit outputs | partially implemented | `apps/logger-web/README.md`, `docs/web_logger_durability_unicode_hash_safety_design.md` | Needs future implementation audit/report template after code changes. | Reports could expose unsafe bodies if not controlled. | Stage 8/9 | P1 before pilot |

## 11. File-Level Change Inventory for Future Implementation

No files are changed in this audit. Likely future change inventory:

| category | file or placeholder | likely future change | reason | related requirement | priority | implementation risk |
| --- | --- | --- | --- | --- | --- | --- |
| TypeScript logger files | `apps/logger-web/src/rawEvent.ts` | Add `event_id`, `position_unit`, hash metadata, canonical hash values, and unit-consistent length policy. | Current schema omits position unit and uses placeholder hashes. | schema clarification, hash canonicalization | P0 | Medium |
| TypeScript logger files | `apps/logger-web/src/main.ts` | Add durable queue, IndexedDB persistence, batch send, ack handling, retry, lifecycle flush. | Current events are in-memory and download-only. | event durability | P0 | High |
| TypeScript test files | `apps/logger-web/tests/` | Add synthetic Unicode/hash vectors and durability behavior tests. | Current tests are shape/basic inference focused. | shared vectors, queue/retry | P0/P1 | Medium |
| TypeScript support file | new file likely needed | Hash helper and possibly durable queue helper modules. | Avoid overloading RawEvent builder. | hash, durability | P0 | Medium |
| Rust schema files | `crates/kslog_schema/src/lib.rs` | Add schema fields or versioned clarification for `position_unit`, hash metadata, event ids, batch diagnostics. | Current schema lacks required explicit metadata. | schema clarification | P0 | Medium |
| Rust validation files | `crates/kslog_validate/src/lib.rs` | Validate position unit, hash metadata, event id shape, duplicate seq/event id categories, UTF-16 offset boundary rules. | Existing checks are range/consecutive only. | validation fail-closed | P0 | High |
| Rust replay files | `crates/kslog_replay/src/lib.rs` | Replace or stage hash helper, add UTF-16 conversion before edit operations, enforce hash mismatch policy. | Current replay uses char count and FNV-1a-style helper. | position and hash consistency | P0 | High |
| Rust extraction files | `crates/kslog_extract/src/lib.rs` | Ensure revision spans consume the same normalized validated offset unit. | Downstream spans inherit replay offsets. | UTF-16 unit consistency | P1 | Medium |
| Rust micro-episode files | `crates/kslog_micro_episode/src/lib.rs` | Align context slicing with validated offset policy. | Current context operations use Rust char count. | downstream offset integrity | P1 | Medium |
| Rust tests | crate-local tests or new shared vector tests | Add emoji, combining, CRLF/LF, tab, invalid boundary, hash vectors. | Current vectors are ASCII/simple synthetic. | shared vectors | P0 | Medium |
| docs | `docs/04_raw_event_schema.md` | Clarify position/hash schema policy. | Current raw schema docs list fields but not units/canonical hash. | Stage 1 | P0 | Low |
| docs | `docs/05_text_replay_spec.md` | Align replay spec with UTF-16 conversion and SHA-256 once implemented. | Current spec documents Rust char count and FNV-1a-style hash. | Stage 3/4 | P0 | Low |
| fixtures | new shared synthetic vector file likely needed | Store public-safe minimal Unicode/hash vectors. | Shared TS/Rust tests need one source of truth. | Stage 2 | P0 | Medium |
| CI workflow | future workflow update likely needed | Add cross-language vector checks after helpers exist. | Current audit found no cross-language hash CI check. | Stage 8 | P1 | Medium |
| Makefile / scripts | future target likely needed | Add targeted check for logger-to-replay vectors after tests exist. | Keep validation repeatable. | Stage 8 | P1 | Low |

## 12. Proposed Staged Implementation Plan

### Stage 1: schema clarification and docs alignment

Goal: Add or clarify `position_unit`, hash policy fields, `event_id`, `seq`, and diagnostic ordering metadata before changing behavior.

Files likely affected: `docs/04_raw_event_schema.md`, `crates/kslog_schema/src/lib.rs`, related schema tests.

Tests needed: schema serialization/deserialization, required/optional field behavior, version compatibility.

Non-claims: no durability implementation, no Unicode implementation completion claim, no hash compatibility implementation completion claim.

Safety gates: no raw event payload bodies in public docs; synthetic minimal examples only.

### Stage 2: hash canonicalization helper and shared test vectors

Goal: Implement SHA-256 UTF-8 lowercase-hex helpers and shared synthetic vectors.

Files likely affected: TypeScript helper, Rust helper, new shared vector fixtures/tests.

Tests needed: empty string, ASCII, Japanese, full-width, emoji, combining mark, precomposed accent, CRLF/LF, trailing newline, tab.

Non-claims: no event durability implementation and no data collection authorization.

Safety gates: vectors synthetic/minimal; no raw learner text.

### Stage 3: Rust UTF-16 code unit offset conversion helper

Goal: Add a validated helper converting UTF-16 code unit offsets to UTF-8 byte indices without silent repair.

Files likely affected: Rust replay/validation helper modules and tests.

Tests needed: valid boundaries, invalid surrogate/boundary cases where representable, emoji, combining marks, CRLF/LF, tab.

Non-claims: no broad runtime correctness claim.

Safety gates: invalid offsets fail closed.

### Stage 4: Rust replay / validation fail-closed behavior

Goal: Wire schema metadata, UTF-16 conversion, canonical hash verification, duplicate/seq diagnostics, and replay failure behavior.

Files likely affected: `crates/kslog_validate/src/lib.rs`, `crates/kslog_replay/src/lib.rs`, `crates/kslog_cli/src/lib.rs`.

Tests needed: hash mismatch, invalid offset, duplicate seq, seq gap, content-suppressed diagnostics.

Non-claims: no model performance or data collection claim.

Safety gates: diagnostics stay metadata-only/count-only where possible.

### Stage 5: TypeScript logger event_id / queue / IndexedDB design implementation

Goal: Add durable client event queue and persisted pending event state.

Files likely affected: `apps/logger-web/src/main.ts`, new queue/storage helper files, TypeScript tests.

Tests needed: queue append, reload recovery, event id uniqueness, persisted seq state.

Non-claims: no perfect event delivery claim.

Safety gates: no console logging of event bodies.

### Stage 6: ack / retry / dedup / seq reconciliation

Goal: Add batch send protocol, ack handling, retry, event id dedup, and seq reconciliation.

Files likely affected: TypeScript client, future server endpoint files, Rust or server-side validator helpers if introduced.

Tests needed: dropped batch, duplicate batch, out-of-order arrival, ack timeout, conflicting event id/seq.

Non-claims: no guarantee that all browser shutdown cases are recoverable.

Safety gates: server uses client seq, not arrival order, for replay order.

### Stage 7: failure injection tests

Goal: Exercise network and write failure paths.

Files likely affected: TypeScript tests, server tests, Rust validation tests, fixtures.

Tests needed: offline/reconnect, server restart between batch writes, malformed/truncated JSONL, duplicate/conflict cases.

Non-claims: no production readiness claim.

Safety gates: no raw logs copied into docs.

### Stage 8: end-to-end synthetic logger-to-replay validation

Goal: Validate a synthetic browser-to-Rust path with durability, UTF-16 positions, and hashes.

Files likely affected: test harness, Makefile/scripts only after focused tests exist.

Tests needed: TypeScript emits synthetic events; Rust validates, converts, replays, and verifies hash.

Non-claims: no real-data readiness claim.

Safety gates: synthetic-only, public-safe summaries.

### Stage 9: pre-collection final safety review

Goal: Review all staged evidence before any collection is considered.

Files likely affected: docs only.

Tests needed: all relevant staged tests already passing.

Non-claims: no deployment readiness claim.

Safety gates: no raw learner text, no real participant data, no raw event payload bodies in docs.

## 13. Recommended Next Codex Step

Recommended next step:

Step-web-logger-002: schema clarification for position units and hash canonicalization

Reason:

- Event durability implementation is large and should not start before schema semantics are fixed.
- The current code already has position and hash fields, but the units and canonical hash rules are not aligned with the design.
- Fixing schema-level `position_unit` and hash policy first makes later Rust helpers, TypeScript helpers, and shared tests more reviewable.
- Step-web-logger-002 should remain docs + schema clarification focused and should not implement queue / IndexedDB.

Step-web-logger-002 has been added as `docs/web_logger_position_unit_and_hash_schema_clarification.md`. It clarifies the intended schema policy only; it does not implement Rust UTF-16 conversion, TypeScript/Rust SHA-256 helpers, shared vectors, queue, IndexedDB, acknowledgement, retry, or deduplication.

Step-web-logger-003 has been added as `docs/web_logger_shared_unicode_hash_test_vector_design.md`. It designs the future shared synthetic vector structure and review path only; it does not create vector fixture JSON, implement hash helpers, implement UTF-16 conversion, add tests, or add CI.

Step-web-logger-004 has been added as `tests/fixtures/web_logger_unicode_hash_vectors/`. It creates synthetic vector fixture data and README documentation for future Unicode/hash checks; it does not implement TypeScript/Rust helpers, tests, CI, Makefile targets, release-quality checks, queue, IndexedDB, acknowledgement, retry, or deduplication.

Step-web-logger-005 has been added as `docs/web_logger_unicode_hash_vector_fixture_validator_design.md`. It designs the future shared vector fixture validator contract only; it does not implement validator code, change fixture JSON, add tests, add Makefile targets, add CI, or add release-quality integration.

Step-web-logger-006 has been added as `python/web_logger_unicode_hash_vector_validation.py` with focused tests under `python/test_support/tests/`. It validates the shared synthetic Unicode/hash fixture metadata, hashes, lengths, offset mappings, and expected failures. It does not implement TypeScript/Rust helper compatibility, event durability, Makefile integration, release-quality integration, or CI integration.

Step-web-logger-007 has been added as `docs/web_logger_unicode_hash_vector_validator_makefile_target_design.md`. It designs the future standalone Makefile target for the Step-web-logger-006 validator, including target name, help text, command, placement, output expectations, failure semantics, and future Step-web-logger-008 checks. It does not modify Makefile, Python code, tests, fixture JSON, release-quality wrapper, CI workflow, TypeScript, Rust, or event durability.

Step-web-logger-008 adds the standalone Makefile target `check-web-logger-unicode-hash-vector-fixtures` for the Step-web-logger-006 validator. It makes the shared Unicode/hash vector fixture validation available via Makefile and keeps release-quality integration, CI integration, TypeScript/Rust helper work, fixture JSON changes, and event durability out of scope.

Step-web-logger-009 adds `docs/web_logger_unicode_hash_vector_validator_release_quality_integration_design.md` as release-quality-integration-design / docs-only planning for the Step-web-logger-008 target. It designs the future wrapper label, command, insertion point, expected output, failure semantics, and Step-web-logger-010 scope without changing wrapper code, Makefile, Python code, tests, fixture JSON, TypeScript, Rust, CI, or event durability.

Step-web-logger-010 adds `release_quality_check: web logger unicode hash vector fixture validation` to `scripts/check_release_quality.sh`. The wrapper calls `make check-web-logger-unicode-hash-vector-fixtures` after Python checks and before learner-state target groups. This integrates the Python vector fixture validator into release-quality while leaving CI workflow integration, TypeScript/Rust helper work, fixture JSON, and event durability unchanged.

Step-web-logger-011 adds `docs/web_logger_unicode_hash_vector_validator_release_quality_remote_run_record_workflow.md` as remote/manual-run-record-workflow-design / docs-only planning for a future public-safe status marker. It defines evidence hierarchy, future metadata fields, target summary fields, missing metadata handling, and future Step-web-logger-012 / Step-web-logger-013 staging while keeping the audit gaps for TypeScript/Rust helpers and event durability open.

Step-web-logger-012 adds `docs/status/web_logger_unicode_hash_vector_validator_release_quality_remote_run_status.md` as a status-marker-only / docs-only remote public-safe record for the Step-web-logger-010 wrapper check. It records the observed label, target command, final release-quality ok label, and count-only validator summary while keeping TypeScript/Rust helper and event durability gaps open.

Step-web-logger-013 adds `docs/web_logger_unicode_hash_vector_validator_release_quality_chain_final_safety_review.md` as final-safety-review / docs-only. It accepts the Step-web-logger-004 through Step-web-logger-012 chain only within the fixed 15-vector Python validator fixture boundary and leaves remaining P0 gaps open.

Step-web-logger-014 adds `docs/web_logger_rust_utf16_offset_conversion_helper_design.md` as design-only / docs-only planning for the Rust UTF-16 code unit offset to UTF-8 byte offset helper. It addresses one remaining P0 gap at the design level only; Rust implementation, Rust tests, broad replay integration, and event durability remain future work.

Step-web-logger-015 adds `crates/kslog_replay/src/utf16_offsets.rs` and `crates/kslog_replay/tests/utf16_offsets.rs` as a focused Rust utility and test boundary for UTF-16 code unit offset to UTF-8 byte offset conversion. This closes the narrow helper/test gap for `kslog_replay` utility behavior, while broad replay / validate / extract / micro_episode runtime integration, Rust SHA-256 helper work, TypeScript SHA-256 helper work, TypeScript/Rust cross-language vector checks, schema/runtime policy integration, and event durability remain open.

Step-web-logger-016 adds `docs/web_logger_rust_utf16_offset_conversion_helper_makefile_target_design.md` as makefile-target-design / docs-only planning for a future focused Rust helper test target. It does not add the target, change Makefile, alter Rust helper code, change tests, or close the broader runtime / hash / durability gaps.

Step-web-logger-017 adds `check-web-logger-rust-utf16-offset-conversion` to Makefile. It provides a focused Makefile path for `cargo test -p kslog_replay utf16`, while leaving Rust helper code, focused tests, fixture JSON, release-quality integration, broader runtime integration, TypeScript/Rust hash work, and event durability unchanged.

Step-web-logger-018 adds `docs/web_logger_rust_utf16_offset_conversion_helper_release_quality_integration_design.md` as docs-only planning for future wrapper integration of the Rust helper Makefile target. It leaves the wrapper, Makefile, Rust code, focused tests, fixture JSON, broader runtime integration, TypeScript/Rust hash work, and event durability unchanged.

Step-web-logger-019 adds `release_quality_check: web logger Rust UTF-16 offset conversion helper` to `scripts/check_release_quality.sh` and calls `make check-web-logger-rust-utf16-offset-conversion`. It leaves Makefile, Rust helper code, focused tests, fixture JSON, CI workflow, broader runtime integration, TypeScript/Rust hash work, and event durability unchanged.

Step-web-logger-020 adds `docs/web_logger_rust_utf16_offset_conversion_helper_release_quality_remote_run_record_workflow.md` as docs-only planning for future remote/manual status evidence for the Rust helper wrapper check. It does not create a status marker, alter the wrapper, change Makefile, change Rust code or tests, change fixture JSON, add broader runtime integration, add TypeScript/Rust hash work, or add event durability.

Step-web-logger-021 adds `docs/status/web_logger_rust_utf16_offset_conversion_helper_release_quality_remote_run_status.md` as public-safe remote metadata/count-only evidence for the Rust helper wrapper check. It does not alter the wrapper, change Makefile, change Rust code or tests, change fixture JSON, add broader runtime integration, add TypeScript/Rust hash work, or add event durability.

Step-web-logger-022 adds `docs/web_logger_rust_utf16_offset_conversion_helper_release_quality_chain_final_safety_review.md` as a docs-only final safety review for the Rust helper release-quality chain. It accepts only the focused helper/test boundary and does not add broader runtime integration, TypeScript/Rust hash work, event durability, production readiness, or real-data readiness.

Step-web-logger-023 adds `docs/web_logger_rust_utf16_offset_conversion_helper_broader_replay_integration_design.md` as docs-only planning for replay-first integration of the existing helper. It does not change Rust code, tests, fixture JSON, Makefile, wrapper, CI workflow, validate / extract / micro_episode behavior, TypeScript/Rust hash work, or event durability.

Step-web-logger-024 adds replay-focused UTF-16 offset integration inside `kslog_replay`. Replay cursor and selection offsets are converted through the existing helper before string indexing / replacement, and replay document length checks use UTF-16 code unit counts. This does not change `kslog_validate`, `kslog_extract`, `kslog_micro_episode`, `kslog_schema`, fixture JSON, Makefile, wrapper, CI workflow, TypeScript/Rust hash work, or event durability.

Step-web-logger-025 adds `docs/web_logger_rust_utf16_replay_integration_makefile_target_design.md` as docs-only planning for future Makefile target semantics after replay-focused integration. It recommends updating the existing Rust UTF-16 target help text/docs rather than adding a duplicate target immediately. It does not change Makefile, wrapper, Rust code, tests, fixture JSON, validate / extract / micro_episode behavior, schema-level position_unit behavior, TypeScript/Rust hash work, or event durability.

## 14. Relationship to Existing No-Oracle and Synthetic-Only Boundaries

This audit does not relax no-oracle constraints, does not authorize real participant data collection, does not introduce real data, and does not validate model performance.

The audit protects input integrity before no-oracle audit by identifying where event ordering, position units, and hash checks can affect text replay, revision-event extraction, micro-episode construction, and later synthetic-only pipeline checks.

## 15. Non-Claims

This audit does not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- event durability implementation completion
- Unicode correctness implementation completion
- hash compatibility implementation completion
- no data loss in all environments
- all browser shutdown cases are recoverable
- deployment readiness

## 16. Public-Safe Documentation Policy

This audit keeps evidence to file paths, metadata, and implementation summaries. It does not include raw learner text, real participant data, raw event payload bodies, fixture JSON bodies, private paths, absolute local paths, logits / probabilities, or performance metric bodies.

Future examples should remain synthetic and minimal. Future summaries should be metadata-only / count-only where possible.

## 17. Step-web-logger-026 Makefile Help Text Alignment

Step-web-logger-026 updates the existing Rust UTF-16 Makefile target help text to reflect that `cargo test -p kslog_replay utf16` now covers helper-focused and replay-focused UTF-16 tests.

This does not change the event durability audit conclusion. Queueing, IndexedDB buffering, acknowledgement, retry, deduplication, ordering, delivery durability, TypeScript/Rust hash work, validate / extract / micro_episode integration, schema-level position_unit policy, and fixture JSON remain outside this update.

## 18. Step-web-logger-027 Release-Quality Label Update Design

Step-web-logger-027 adds [Rust UTF-16 Replay Integration Release Quality Label Update Design](web_logger_rust_utf16_replay_integration_release_quality_label_update_design.md).

The design does not change the event durability audit conclusion. It plans only future wrapper label wording alignment and does not add queueing, IndexedDB buffering, acknowledgement, retry, deduplication, ordering, delivery durability, TypeScript/Rust hash work, validate / extract / micro_episode integration, or schema-level position_unit policy.

## 19. Step-web-logger-028 Release-Quality Label Update

Step-web-logger-028 updates only the Rust UTF-16 release-quality label wording.

This does not change the event durability audit conclusion. Queueing, IndexedDB buffering, acknowledgement, retry, deduplication, ordering, delivery durability, TypeScript/Rust hash work, validate / extract / micro_episode integration, and schema-level position_unit policy remain outside this update.

## 20. Step-web-logger-029 Run Record Workflow Design

Step-web-logger-029 adds [Rust UTF-16 Replay Integration Release Quality Remote/Manual Run Record Workflow](web_logger_rust_utf16_replay_integration_release_quality_remote_run_record_workflow.md).

This does not change the event durability audit conclusion. It designs only future public-safe status recording for the updated Rust UTF-16 replay release-quality label and does not add queueing, IndexedDB buffering, acknowledgement, retry, deduplication, ordering, delivery durability, TypeScript/Rust hash work, validate / extract / micro_episode integration, or schema-level position_unit policy.

## 21. Step-web-logger-032 Schema-Level Position Unit Policy Design

Step-web-logger-032 adds [Schema-Level Position Unit Policy Design for Web Logger Events](web_logger_schema_position_unit_policy_design.md).

This does not change the event durability audit conclusion. It designs future schema / validation position-unit policy only and does not add queueing, IndexedDB buffering, acknowledgement, retry, deduplication, ordering, delivery durability, TypeScript/Rust hash work, validate / extract / micro_episode integration, code changes, tests, fixture JSON changes, Makefile changes, wrapper changes, or CI workflow changes.

## 22. Step-web-logger-033 Schema-Level Position Unit Fixture Design

Step-web-logger-033 adds [Schema-Level Position Unit Fixture Design for Web Logger Events](web_logger_schema_position_unit_fixture_design.md).

This does not change the event durability audit conclusion. It designs future synthetic schema / validator fixtures only and does not add queueing, IndexedDB buffering, acknowledgement, retry, deduplication, ordering, delivery durability, TypeScript/Rust hash work, validate / extract / micro_episode integration, code changes, tests, fixture JSON changes, Makefile changes, wrapper changes, or CI workflow changes.

## 23. Step-web-logger-034 Schema-Level Position Unit Fixtures

Step-web-logger-034 adds `tests/fixtures/web_logger_position_unit_schema/`
as a synthetic fixture root for future Web logger position-unit schema /
validator checks.

This does not change the event durability audit conclusion. It adds fixture
files only and does not add queueing, IndexedDB buffering, acknowledgement,
retry, deduplication, ordering, delivery durability, TypeScript/Rust hash work,
validate / extract / micro_episode integration, Rust / TypeScript / Python
code changes, tests outside the new fixture root, Makefile changes, wrapper
changes, or CI workflow changes.

## 24. Step-web-logger-035 Schema-Level Position Unit Fixture Validator Design

Step-web-logger-035 adds
[Schema-Level Position Unit Fixture Validator Design](web_logger_schema_position_unit_fixture_validator_design.md).

This does not change the event durability audit conclusion. It designs only a
future fixture contract validator and does not add queueing, IndexedDB
buffering, acknowledgement, retry, deduplication, ordering, delivery
durability, TypeScript/Rust hash work, validate / extract / micro_episode
integration, schema / validator behavior, code changes, tests, fixture changes,
Makefile changes, wrapper changes, or CI workflow changes.

## 25. Step-web-logger-036 Schema-Level Position Unit Fixture Validator

Step-web-logger-036 adds the Python-first fixture contract validator for
`tests/fixtures/web_logger_position_unit_schema/`.

This does not change the event durability audit conclusion. It adds fixture
contract validation only and does not add queueing, IndexedDB buffering,
acknowledgement, retry, deduplication, ordering, delivery durability,
TypeScript/Rust hash work, validate / extract / micro_episode integration,
Rust schema / validator behavior, Makefile changes, wrapper changes, or CI
workflow changes.

## 26. Step-web-logger-037 Schema-Level Position Unit Fixture Validator Makefile Target Design

Step-web-logger-037 adds
[Schema-Level Position Unit Fixture Validator Makefile Target Design](web_logger_schema_position_unit_fixture_validator_makefile_target_design.md).

This does not change the event durability audit conclusion. It designs only a
future Makefile target for the summary-only fixture contract validator and does
not add queueing, IndexedDB buffering, acknowledgement, retry, deduplication,
ordering, delivery durability, TypeScript/Rust hash work, validate / extract /
micro_episode integration, Rust schema / validator behavior, Makefile changes,
wrapper changes, or CI workflow changes.
