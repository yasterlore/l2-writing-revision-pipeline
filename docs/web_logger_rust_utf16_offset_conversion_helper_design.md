# Rust UTF-16 Offset Conversion Helper Design for Web Logger Events

## 1. Title

Rust UTF-16 Offset Conversion Helper Design for Web Logger Events

## 2. Scope

This is a design-only / docs-only step.

This step does not implement Rust code, TypeScript code, Python code, tests, fixture JSON, Makefile targets, release-quality wrapper entries, CI workflow changes, package metadata changes, Cargo metadata changes, schema behavior changes, runtime behavior changes, replay behavior changes, or event durability.

This step does not provide production readiness proof, real-data readiness proof, or model performance proof.

## 3. Design Status

This document designs a future Rust helper for converting browser-originated UTF-16 code unit offsets into Rust UTF-8 byte offsets.

Shared Unicode/hash vectors are already available at `tests/fixtures/web_logger_unicode_hash_vectors/vectors.json`. The Python validator already validates the fixed 15-vector fixture contract. Rust helper implementation and tests remain future work.

TypeScript / Rust compatibility is not claimed by this design.

## 4. Problem Statement

Browser-originated selection, cursor, and edit span offsets are UTF-16 code unit offsets. Rust string slicing requires UTF-8 byte offsets at valid `char` boundaries.

Directly using UTF-16 offsets as Rust byte indices is unsafe. It can point inside multi-byte UTF-8 sequences, mis-slice non-ASCII text, or treat the middle of a UTF-16 surrogate pair as a valid boundary.

Required failure behavior:

- offsets inside surrogate pairs must fail closed
- offsets beyond UTF-16 length must fail closed
- `start > end` must fail closed
- no rounding or repair should be performed
- conversion diagnostics must be public-safe
- diagnostics must not print raw source text

## 5. Proposed Rust Helper Location

Conservative future locations:

- `crates/kslog_replay`: replay-local helper for reconstructing text and checking event-derived ranges
- `crates/kslog_validate`: validation helper if invalid offsets should be rejected before replay
- `crates/kslog_schema`: schema-adjacent shared utility if the helper becomes a broadly shared contract
- a small shared module reused by replay / validate / extract only if existing crate boundaries allow it cleanly

Recommended first implementation location:

`crates/kslog_replay`

Reasoning:

- `kslog_replay` already owns reconstruction from validated raw events.
- The helper is immediately replay-critical because Rust slicing must use byte offsets.
- `kslog_replay` currently depends on `kslog_schema`, while `kslog_validate` is a dev-dependency for replay tests. Keeping the first helper local avoids broad cross-crate refactors.
- The first API should be small and pure.
- If `kslog_validate`, `kslog_extract`, or `kslog_micro_episode` later need the same helper, a later step can move or re-export it deliberately.

This step does not create or modify any Rust files.

## 6. Proposed Helper API

Future single-offset helper:

```rust
pub fn utf16_code_unit_offset_to_utf8_byte_index(
    text: &str,
    utf16_offset: usize,
) -> Result<usize, Utf16OffsetError>
```

Future range helper:

```rust
pub fn utf16_code_unit_range_to_utf8_byte_range(
    text: &str,
    utf16_start: usize,
    utf16_end: usize,
) -> Result<std::ops::Range<usize>, Utf16OffsetError>
```

API expectations:

- input text is a Rust `&str` that is already valid UTF-8
- `utf16_start` and `utf16_end` come from browser-originated event metadata
- returned byte offsets are valid Rust `char` boundaries
- end offset may equal `text.len()`
- empty ranges are allowed when `start == end` at a valid boundary
- errors and display output must not contain raw text

## 7. Error Type Design

Future error enum:

```rust
pub enum Utf16OffsetError {
    OffsetBeyondUtf16Length {
        offset: usize,
        utf16_len: usize,
    },
    OffsetInsideSurrogatePair {
        offset: usize,
        utf16_len: usize,
    },
    StartAfterEnd {
        start: usize,
        end: usize,
    },
    InvalidBoundary {
        offset: usize,
        utf16_len: usize,
    },
    UnsupportedPositionUnit {
        position_unit: String,
    },
    InternalInvariantViolation,
}
```

Error semantics:

| Variant | Occurs when | reason_code | Higher-level status | Safe metadata |
| --- | --- | --- | --- | --- |
| `OffsetBeyondUtf16Length` | requested offset is greater than UTF-16 code unit length | `offset_beyond_utf16_length` | fail_closed | offset, UTF-16 length |
| `OffsetInsideSurrogatePair` | requested offset is inside a non-BMP scalar's UTF-16 surrogate pair | `offset_inside_surrogate_pair` | fail_closed | offset, UTF-16 length |
| `StartAfterEnd` | range start is greater than range end | `start_greater_than_end` | fail_closed | start, end |
| `InvalidBoundary` | offset is within UTF-16 length but not a valid boundary for another reason | `invalid_utf16_boundary` | fail_closed | offset, UTF-16 length |
| `UnsupportedPositionUnit` | event metadata declares an unsupported position unit | `unsupported_position_unit` | fail_closed | position unit name only |
| `InternalInvariantViolation` | helper detects an impossible mapping state | `internal_invariant_violation` | fail_closed | reason code only |

Higher-level callers may map missing required fields to `usage_error` or an existing schema validation error. Malformed offsets that are present should fail closed rather than be repaired.

## 8. Boundary Mapping Algorithm

Future algorithm:

1. Build a mapping from valid UTF-16 code unit boundaries to UTF-8 byte offsets.
2. Start with mapping `0 -> 0`.
3. Iterate over `text.char_indices()`.
4. For each `char`:
   - current UTF-8 byte index is known from `char_indices`
   - char UTF-8 byte length is `ch.len_utf8()`
   - char UTF-16 code unit length is `ch.len_utf16()`
   - advance cumulative UTF-16 position by `ch.len_utf16()`
   - advance cumulative UTF-8 byte position by `ch.len_utf8()`
   - insert only the boundary after the full char
5. For non-BMP characters, `len_utf16()` is 2, so the intermediate UTF-16 code unit inside the surrogate pair is not inserted.
6. Insert final UTF-16 length -> `text.len()`.
7. Lookup requested UTF-16 offset in the mapping.
8. If absent but `offset <= utf16_len`, return `offset_inside_surrogate_pair` or `invalid_utf16_boundary`.
9. If `offset > utf16_len`, return `offset_beyond_utf16_length`.

The helper must not normalize Unicode, normalize newline sequences, trim trailing newline, round to nearest boundary, or repair invalid offsets.

Implementation note for a future Rust step: because Rust `char` values are Unicode scalar values, a non-BMP character appears as one `char` with `len_utf16() == 2`. The helper can therefore intentionally omit the intermediate UTF-16 code unit from the valid boundary map.

## 9. Range Conversion Policy

Range conversion should:

- validate `start <= end` before slicing
- validate start and end independently
- allow `start == end` if both offsets are valid boundaries
- return `start_byte..end_byte`
- avoid raw selected text in diagnostics
- avoid unnecessary allocation beyond the boundary mapping

Selected text validation should occur only in tests or in callers that already have safe synthetic text. Normal diagnostics should report metadata only.

## 10. Unicode Policy

The helper follows the existing schema clarification policy:

- no Unicode normalization
- no newline normalization
- no grapheme-cluster semantics
- code point count is not the same as UTF-16 code unit count
- combining marks are separate scalar values
- precomposed and decomposed forms remain distinct
- CRLF is two code points and two UTF-16 code units
- trailing newline is preserved

The stored string is the source of truth for both offset conversion and later hash checking.

## 11. Relationship to Shared Unicode/Hash Vectors

Future Rust tests should reuse:

```text
tests/fixtures/web_logger_unicode_hash_vectors/vectors.json
```

Future Rust tests should verify:

- `utf16_code_unit_length`
- `utf8_byte_length`
- valid offset mapping
- invalid surrogate boundary expected failures
- beyond-length expected failures
- `start > end` expected failures

This step does not modify `vectors.json` and does not regenerate hashes.

Rust helper tests should not print raw source text in normal output. If tests read `source_text`, it remains synthetic fixture text.

## 12. Proposed Future Rust Tests

Future Step-web-logger-015 tests should include at least:

- ASCII offset maps 1:1 to byte offsets
- Japanese text maps UTF-16 code units to UTF-8 byte offsets correctly
- full-width text maps correctly
- emoji surrogate pair maps boundaries before and after emoji
- surrogate pair internal offset fails closed
- Japanese + emoji mixed offsets map correctly
- combining sequence remains unnormalized
- precomposed accent remains distinct
- LF and CRLF are preserved
- trailing newline is preserved
- tab is preserved
- beyond UTF-16 length fails
- `start > end` fails
- empty string offset `0` maps to byte `0`
- end offset maps to `text.len()`
- range conversion returns expected byte range
- diagnostics do not include raw source text

Focused tests may include direct unit tests plus fixture-driven tests over the shared vector JSON. Fixture-driven tests should keep output metadata-only.

## 13. Proposed Future Integration Points

Potential future integration points:

- `kslog_replay` cursor / selection validation
- `kslog_validate` event schema validation
- `kslog_extract` selection range edit extraction
- `kslog_micro_episode` context slicing

Recommended staging:

1. First implementation step adds the helper and focused tests only.
2. Later integration step wires the helper into replay / validation / extraction paths.
3. Runtime behavior should not change until helper tests pass.
4. Integration must preserve no-oracle and content suppression boundaries.

## 14. Public-Safe Diagnostics

Allowed diagnostic fields:

- reason_code
- vector_id
- case_id
- `utf16_start` / `utf16_end` numeric values
- `utf16_length`
- `utf8_byte_length`
- `byte_start` / `byte_end` numeric values
- status
- count summary

Forbidden diagnostic content:

- raw source text
- raw selected text
- raw event payload body
- full fixture JSON body
- private paths
- absolute local paths
- raw learner text
- real participant data
- logits / probabilities
- performance metric body

## 15. Failure Semantics for Callers

Future callers should treat failures as follows:

- invalid UTF-16 offset in event validation -> fail_closed
- missing required offset field -> usage_error or existing schema validation error
- unsupported `position_unit` -> fail_closed
- offset beyond document length -> fail_closed
- surrogate-pair internal offset -> fail_closed
- `start > end` -> fail_closed
- unexpected internal invariant -> fail_closed

Callers must not panic on malformed input, silently coerce invalid offsets, continue with repaired offsets, or emit raw text in diagnostics. Higher-level summaries must remain metadata-only.

## 16. Relationship to Hash Policy

The UTF-16 offset conversion helper does not compute SHA-256 hashes.

It should be consistent with the same source text used for SHA-256 UTF-8 hashing. Rust SHA-256 helper remains a separate future step. TypeScript SHA-256 helper remains a separate future step.

TypeScript / Rust hash compatibility is not proven by this helper design.

## 17. Relationship to Event Durability

This helper design does not implement event queueing, IndexedDB buffering, acknowledgement, retry, deduplication, or event ID idempotency.

It does not solve ordering or delivery durability. Event durability remains a separate P0 chain.

## 18. Relationship to No-Oracle and Synthetic-Only Boundaries

Shared vectors are synthetic-only. No real participant data is introduced. No raw learner text is introduced.

No `final_text`, `observed_after_text`, gold labels, or post-hoc annotation are used.

No model performance validation is performed. No-oracle constraints are not relaxed.

## 19. Non-Equivalence Cautions

- Rust helper design is not Rust helper implementation.
- Rust helper implementation will not by itself prove TypeScript compatibility.
- Rust helper implementation will not by itself prove full replay correctness.
- Fixture tests will not prove all Unicode cases.
- Python validator pass is not Rust implementation pass.
- Release-quality status for Python validator is not Rust helper status.
- UTF-16 conversion is not event durability.
- UTF-16 conversion is not data collection readiness.

## 20. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- Unicode correctness の実装完了
- hash compatibility の実装完了
- TypeScript / Rust vector check の実装完了
- TypeScript / Rust helper compatibility
- event durability の実装完了
- TypeScript と Rust の hash 出力が現時点で一致済みであること
- data collection readiness
- deployment readiness

## 21. Recommended Next Step

Recommended next step:

Step-web-logger-015: implement Rust UTF-16 offset conversion helper with focused tests

Clarification:

- Step-web-logger-015 should implement the helper and focused Rust tests only.
- It should reuse the shared Unicode/hash vectors where practical.
- It should not modify TypeScript.
- It should not modify fixture JSON.
- It should not implement hash helper.
- It should not integrate broadly into replay / validate / extract yet unless explicitly scoped.
- It should not implement event durability.
- It should update README and full technical specification docs only because it will be an implementation step.

## 22. Step-web-logger-015 Implementation Status

Step-web-logger-015 adds the first focused Rust helper in `crates/kslog_replay/src/utf16_offsets.rs` and focused tests in `crates/kslog_replay/tests/utf16_offsets.rs`.

The helper follows this design's narrow boundary:

- converts a single UTF-16 code unit offset to a UTF-8 byte offset at a valid Rust char boundary
- converts a UTF-16 code unit range to a UTF-8 byte range
- rejects offsets beyond the UTF-16 length
- rejects surrogate-pair internal offsets
- rejects `start > end`
- preserves Unicode and newline content without normalization
- exposes stable public-safe reason codes
- avoids raw text in error display output

The focused tests include direct shared-vector reuse through the existing `kslog_replay` dev dependency surface, so `Cargo.toml` and `vectors.json` are unchanged.

This implementation step does not integrate the helper into replay / validate / extract / micro_episode runtime behavior, does not implement Rust or TypeScript SHA-256 helpers, does not add TypeScript/Rust cross-language vector checks, does not change Makefile or release-quality wrapper wiring, and does not implement event durability.

## 23. Step-web-logger-016 Makefile Target Design Handoff

Step-web-logger-016 adds [Rust UTF-16 Offset Conversion Helper Makefile Target Design](web_logger_rust_utf16_offset_conversion_helper_makefile_target_design.md).

The design proposes a future standalone target, `check-web-logger-rust-utf16-offset-conversion`, that runs `cargo test -p kslog_replay utf16` for the focused Rust helper tests. It does not change Makefile, Rust code, tests, fixture JSON, release-quality wrapper, CI workflow, or broader replay/runtime behavior.

## 24. Step-web-logger-017 Makefile Target

Step-web-logger-017 adds `check-web-logger-rust-utf16-offset-conversion` to Makefile.

The target runs `cargo test -p kslog_replay utf16` for the Step-web-logger-015 focused helper tests. It is a Makefile execution path only; it does not change helper code, tests, fixture JSON, release-quality wrapper, CI workflow, or broader replay/runtime behavior.

## 25. Step-web-logger-018 Release-Quality Integration Design

Step-web-logger-018 adds [Rust UTF-16 Offset Conversion Helper Release Quality Integration Design](web_logger_rust_utf16_offset_conversion_helper_release_quality_integration_design.md).

The design plans a future wrapper check for the existing Makefile target. It does not change helper behavior, focused tests, fixture JSON, Makefile, wrapper, CI workflow, broader replay / validate / extract / micro_episode runtime integration, Rust SHA-256 helper work, TypeScript SHA-256 helper work, TypeScript/Rust cross-language checks, or event durability.
