# Rust UTF-16 Offset Conversion Helper Broader Replay Integration Design

## 1. Title

Rust UTF-16 Offset Conversion Helper Broader Replay Integration Design

## 2. Scope

This is a broader-replay-integration-design / docs-only step.

This step makes no Rust code changes, no TypeScript code changes, no Python code changes, no tests changes, no fixture JSON changes, no Makefile changes, no release-quality wrapper changes, no CI workflow changes, and no package.json / Cargo.toml / Cargo.lock changes.

This step makes no schema behavior changes, no replay runtime behavior changes, and no validate / extract / micro_episode behavior changes.

This step does not implement event durability, production readiness proof, real-data readiness proof, or model performance proof.

## 3. Design Status

The Rust UTF-16 helper exists and is release-quality-integrated / remote-status-recorded for focused tests.

This doc designs future broader integration. It does not implement broader integration. The current accepted boundary remains the focused helper/test chain only.

Broader replay / validate / extract / micro_episode integration remains future work. TypeScript/Rust compatibility is not claimed.

## 4. Current Helper Boundary Recap

The helper is located in `crates/kslog_replay` and implemented in `crates/kslog_replay/src/utf16_offsets.rs`.

The current helper APIs are:

- `utf16_code_unit_offset_to_utf8_byte_index`
- `utf16_code_unit_range_to_utf8_byte_range`

The helper converts UTF-16 code unit offsets to UTF-8 byte offsets, supports range conversion, and fail-closes offset beyond UTF-16 length, offset inside surrogate pair / invalid UTF-16 boundary, and `start > end`.

The error type exposes public-safe `reason_code` values:

- `offset_beyond_utf16_length`
- `offset_inside_surrogate_pair`
- `start_greater_than_end`
- `invalid_utf16_boundary`
- `unsupported_position_unit`
- `internal_invariant_violation`

The helper does not normalize Unicode, does not normalize newlines, does not implement grapheme-cluster semantics, does not compute SHA-256 hash, and does not include raw text in diagnostics.

Focused Rust tests reuse the shared Unicode/hash vectors. The focused helper/test chain is release-quality-integrated and remote-status-recorded.

## 5. Current Rust Call-Site Audit

Audited crates:

- `crates/kslog_replay`
- `crates/kslog_validate`
- `crates/kslog_extract`
- `crates/kslog_micro_episode`
- `crates/kslog_schema`

`kslog_schema` defines `RawEvent` with optional `selection_start_before`, `selection_end_before`, `selection_start_after`, `selection_end_after`, `cursor_pos_before`, `cursor_pos_after`, `doc_len_before`, `doc_len_after`, `inserted_text`, `deleted_text`, and text hash fields. The current schema does not expose an explicit `position_unit` field in `RawEvent`.

`kslog_validate` checks cursor and selection numeric bounds against `doc_len_before` / `doc_len_after`, and checks inverted selection ranges. It does not reconstruct text state and does not validate UTF-16 surrogate boundaries because it does not have the current document string for conversion.

`kslog_replay` reconstructs text state and is the first crate that has the current string needed to convert browser-originated positions. It currently uses Rust `char` counts, `slice_chars`, and `char_to_byte_index`. Cursor and selection values are cast to `usize` and treated as character positions before string slicing or replacement. This is the highest-risk first boundary for UTF-16 integration.

`kslog_extract` builds revision spans from cursor and selection fields and uses `char_count` for deleted-text length inference. It does not generally slice source document state itself in the extraction span construction path. Its spans can inherit unit ambiguity from raw events, so it should wait until replay behavior and a crate-boundary plan are stable.

`kslog_micro_episode` applies revision spans to text state, slices local context using character windows, and converts character indexes to byte indexes before `replace_range`. It may contain text fragments in micro-episode outputs and has explicit no-oracle cautions. It should receive already validated/converted spans where possible, or use conversion in a later dedicated integration step if raw browser offsets still reach it.

Current error/reporting paths are mixed. Replay diagnostic reports suppress content through metadata fields and length summaries, but direct `ReplayErrorKind::DeletedTextMismatch` still carries expected/actual strings internally. Future integration diagnostics should keep status summaries metadata-only and avoid adding raw text to new UTF-16 offset failures.

First integration should target `kslog_replay` string-index boundaries. Validation, extraction, and micro_episode integration should wait unless compile-time boundaries require a small shared abstraction.

## 6. Position Unit Policy for Integration

Browser-originated positions should be treated as UTF-16 code unit offsets when `position_unit=utf16_code_unit`.

Rust slicing must use UTF-8 byte offsets produced by the helper conversion. New Web logger schema paths should not silently assume a missing `position_unit`.

Legacy / older fixture behavior should be handled explicitly and conservatively. Unsupported `position_unit` should fail closed. Offsets must not be rounded, repaired, or silently reinterpreted as byte indices or Rust character indices.

Raw source text must not be included in diagnostics.

## 7. Recommended First Integration Boundary

Recommended first implementation target:

- integrate the helper into `crates/kslog_replay` replay validation/string-index boundary first
- convert browser-originated cursor / selection offsets before any Rust string slicing or bounds-sensitive operation
- preserve existing replay output behavior except invalid UTF-16 offsets become explicit fail-closed errors
- do not integrate `kslog_validate`, `kslog_extract`, or `kslog_micro_episode` in the first implementation step unless required by compile-time boundaries
- keep the first implementation small and focused

This is the safest first boundary because replay owns the evolving text state required by the UTF-16 to UTF-8 conversion helper.

## 8. Proposed Replay Integration Behavior

Replay should use the current `ReplayState.text` as the input text state for before-edit cursor and selection conversion.

Future behavior should:

- convert `cursor_pos_before` with the helper before cursor-sensitive replay operations
- convert `selection_start_before` / `selection_end_before` with the range helper before selection operations
- convert or validate `cursor_pos_after` against the post-edit text state before storing final cursor position
- validate `doc_len_before` / `doc_len_after` as UTF-16 code unit lengths rather than Rust character counts for `position_unit=utf16_code_unit`
- avoid interpreting UTF-16 offsets as byte offsets or Rust character indexes
- preserve no raw content diagnostics
- return a public-safe error reason_code on invalid UTF-16 offset
- avoid panic on malformed offsets
- avoid offset repair, rounding, or fallback conversion
- keep successful ASCII behavior unchanged where UTF-16 and UTF-8 byte offsets coincide
- add explicit tests for non-ASCII browser positions

Because the current replay internals return character-index ranges before converting to bytes, a future implementation may either introduce byte-range-specific edit helpers or carry both UTF-16 metadata and UTF-8 byte ranges through the edit path. The first implementation should choose the smaller change that avoids invalid slicing.

## 9. Proposed Validation Integration Behavior

Validation should eventually check `position_unit` and offset bounds consistently with schema policy.

Validation may use the helper or a shared helper only after crate boundary is decided. If the helper stays in `kslog_replay`, `kslog_validate` should not depend on replay unless dependency direction is intentionally approved.

If validation needs UTF-16 boundary conversion, consider moving the helper to `kslog_schema` or a small shared utility crate/module in a later design step. Unsupported `position_unit` should fail closed. Missing `position_unit` for Web logger v0.2+ should be treated according to schema policy, not guessed.

Validation integration should remain a separate future chain if cross-crate refactor is needed.

## 10. Proposed Extraction Integration Behavior

Extraction should not treat UTF-16 offsets as byte indices.

Selection-range edit extraction should use converted byte ranges when slicing is needed. If extraction only carries spans forward, it should record which unit a span uses or consume spans already normalized by replay/validation.

Extraction should preserve observed edit classification semantics. Invalid UTF-16 offsets should fail closed or produce public-safe extraction errors according to the existing error model.

Raw selected text should not be printed in diagnostics. Extraction integration should happen after the replay boundary is stable.

## 11. Proposed Micro-Episode Integration Behavior

Local context slicing must not use browser UTF-16 offsets directly as byte indices.

Integration should use byte offsets or unit-explicit spans already validated/converted upstream where possible. If `kslog_micro_episode` receives raw browser offsets, it must convert or reject them.

Context windows should preserve existing no-oracle boundaries. No `observed_after_text`, `final_text`, gold labels, or post-hoc annotation should be introduced.

Micro_episode integration should be a later step after replay/extract behavior is clarified.

## 12. Crate Boundary and Dependency Strategy

Option A: keep the helper in `kslog_replay` for first runtime integration, then move or re-export only if `kslog_validate`, `kslog_extract`, or `kslog_micro_episode` need it.

Option B: move the helper immediately to `kslog_schema` or a shared crate/module before broader integration.

Recommendation: choose Option A for the next implementation step.

Tradeoff: Option A minimizes first-step blast radius and uses the crate that already owns text state and replacement behavior. It avoids broad cross-crate refactor before a concrete second call site requires it. Option B may become cleaner later if validation/extraction need shared conversion, but it introduces dependency and ownership changes before the first replay integration proves its shape.

If validate/extract/micro_episode need the helper later, create a dedicated design step for moving or re-exporting it.

## 13. Error Semantics and Reason Code Propagation

Future integration should map conversion errors as fail-closed replay/validation outcomes:

- `offset_beyond_utf16_length` -> fail_closed
- `offset_inside_surrogate_pair` / `invalid_utf16_boundary` -> fail_closed
- `start_greater_than_end` -> fail_closed
- `unsupported_position_unit` -> fail_closed
- `internal_invariant_violation` -> fail_closed
- missing required field -> existing schema usage_error or validation error

Diagnostics must be metadata-only. They may include reason_code, event index, synthetic/public-safe event id, field name, numeric offsets, and numeric lengths.

Diagnostics must not include raw text, private paths, absolute local paths, or raw payload bodies. Malformed input must not cause panic.

## 14. Proposed Future Tests for Replay Integration

Future replay-focused tests should include:

- ASCII fixture behavior unchanged
- Japanese cursor position converts correctly
- Japanese selection range converts correctly
- emoji boundary before and after character converts correctly
- surrogate pair internal offset fails closed
- offset beyond UTF-16 length fails closed
- `start > end` selection fails closed
- missing / unsupported `position_unit` behavior according to policy
- range conversion prevents invalid slicing panic
- replay diagnostics suppress raw text
- existing `kslog_replay` tests still pass
- shared Unicode/hash vector cases reused where practical
- fixture JSON remains unchanged unless a separate fixture design step authorizes additions

If new synthetic fixtures are needed, create a later fixture-design step first, or include safe Rust test literals only if they remain synthetic and do not change shared fixture JSON.

Do not introduce real participant data.

## 15. Proposed Future Makefile / Release-Quality Staging

Recommended staging:

- Step-web-logger-024: implement replay-focused UTF-16 integration with focused tests
- Step-web-logger-025: Makefile target design or update existing target design for replay integration tests
- Step-web-logger-026: add/update Makefile target
- Step-web-logger-027: release-quality integration design
- Step-web-logger-028: release-quality wrapper integration
- Step-web-logger-029: remote/manual status marker workflow design
- Step-web-logger-030: status marker
- Step-web-logger-031: final safety review

Do not jump directly to broad multi-crate integration.

## 16. Relationship to Existing Focused Helper Chain

Step-web-logger-014 through Step-web-logger-022 created and reviewed the focused helper/test/release-quality chain.

Broader integration should reuse that helper and should not weaken focused helper tests. The focused helper target remains useful after replay integration.

Future replay integration target should be separate or clearly layered. Focused helper pass does not prove broader replay correctness.

## 17. Relationship to Python Validator Chain

The Python validator chain validates the fixed 15-vector fixture contract.

The Rust helper chain validates focused Rust offset conversion behavior. Broader replay integration is a separate evidence boundary.

Python validator pass does not prove replay integration. Replay integration pass does not prove Python validator correctness. Do not merge evidence boundaries.

## 18. Relationship to TypeScript / Rust Hash/Helper Work

Broader replay integration does not implement the Rust SHA-256 helper.

It does not implement the TypeScript SHA-256 helper. It does not implement TypeScript/Rust vector checks. It does not prove current TypeScript and Rust hashes match.

Hash compatibility remains a separate future chain.

## 19. Relationship to Event Durability

Broader replay integration does not implement event durability.

It does not implement queue / IndexedDB / ack / retry / dedup. It does not implement server-side idempotency / event_id dedup. It does not solve ordering or delivery durability.

Event durability remains a separate P0 chain.

## 20. Relationship to No-Oracle and Synthetic-Only Boundaries

No real participant data is introduced. No raw learner text is introduced.

No `final_text`, `observed_after_text`, gold labels, post-hoc annotation, or test-set tuning is introduced.

No model performance validation is performed. No-oracle constraints are not relaxed. Future tests must remain synthetic-only.

## 21. Public-Safe Diagnostics

Allowed future diagnostics:

- reason_code
- event_id if synthetic/public-safe
- vector_id / case_id when synthetic/public-safe
- numeric UTF-16 offset
- numeric UTF-8 byte offset
- document length numeric metadata
- status
- count summary
- crate/module/test name

Forbidden diagnostics:

- raw source text
- raw selected text
- raw inserted/deleted text unless already explicitly safe synthetic fixture text and not printed by default
- raw event payload body
- full fixture JSON body
- private paths
- absolute local paths
- raw learner text
- real participant data
- logits / probabilities
- performance metric body

## 22. Failure Interpretation

Conversion failure should mean fail-closed for the affected replay operation.

Fail-closed does not imply data corruption and does not imply production readiness.

Passing future replay-focused tests would not prove validate/extract/micro_episode integration, TypeScript compatibility, or event durability. Synthetic-only pass would not be real-data readiness.

## 23. Non-Equivalence Cautions

- Broader replay integration design is not implementation.
- Future replay integration pass is not schema validation integration.
- Future replay integration pass is not revision extraction integration.
- Future replay integration pass is not micro_episode context slicing integration.
- Helper integration is not TypeScript compatibility.
- Helper integration is not hash compatibility.
- Helper integration is not event durability.
- Helper integration is not production readiness.
- Synthetic-only validation is not real-data readiness.
- Call-site audit is not proof of all hidden Unicode issues.

## 24. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- broader Unicode correctness completion
- broader replay integration completion
- schema validation integration completion
- revision extraction integration completion
- micro_episode context slicing integration completion
- hash compatibility implementation completion
- TypeScript / Rust vector check implementation
- TypeScript / Rust helper compatibility
- event durability implementation completion
- current TypeScript and Rust hashes match
- data collection readiness
- deployment readiness

## 25. Recommended Next Codex Step

Recommended next step:

Step-web-logger-024: implement replay-focused UTF-16 offset integration with focused tests

Clarification:

- Step-web-logger-024 should be an implementation step.
- It should modify only minimal `kslog_replay` files and focused tests if possible.
- It should reuse the existing helper.
- It should not move the helper across crates unless unavoidable.
- It should not modify TypeScript, Python, or fixture JSON unless explicitly required and justified.
- It should not implement validate / extract / micro_episode integration.
- It should not implement Rust SHA-256 helper, TypeScript SHA-256 helper, or TypeScript/Rust vector checks.
- It should not implement event durability.
- Because Step-web-logger-024 is implementation, it should update README and full technical specification related docs minimally.
