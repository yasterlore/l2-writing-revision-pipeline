# Rust Validator Phase 2 UTF-16 Numeric Metadata Validation Design

## 1. Title

Rust Validator Phase 2 UTF-16 Numeric Metadata Validation Design

## 2. Scope

This is a design-only / docs-only Step. It makes no Rust code changes, no
TypeScript code changes, no Python code changes, no tests changes, no fixture
JSON / JSONL changes, no Makefile changes, no release-quality wrapper
changes, no CI workflow changes, no Cargo.toml / Cargo.lock changes, and no
package.json changes.

This Step changes no validator behavior, schema behavior, replay behavior,
extract / micro_episode behavior, event durability behavior, production
readiness proof, real-data readiness proof, or model performance proof.

## 3. Design Status

Step-web-logger-054 accepted the Rust validator Phase 1 chain for
`position_unit` presence / value / schema-version gating. Step-web-logger-055
designs Phase 2 numeric validation only. Phase 2 is not implemented in this
Step.

Phase 2 must remain separate from replay correctness, extract /
micro_episode integration, TypeScript logger compatibility, SHA-256
compatibility, and event durability.

## 4. Phase 1 Accepted Boundary Recap

Accepted Step054 boundary:

`release-quality-integrated, remote-status-recorded, Rust validator Phase 1 position_unit policy enforcement for Web logger v0.2-style presence/value/schema-version gating`

Phase 1 covers stable reason codes for `missing_position_unit`,
`unsupported_position_unit`, `position_unit_schema_mismatch`, and
`unknown_schema_version`, plus explicit legacy missing-position gating. The
focused Makefile target is `check-web-logger-rust-validator-position-unit-phase1`,
and the release-quality wrapper calls that target. Step053 recorded remote
status evidence, and Step054 final-reviewed the chain.

Phase 1 does not cover UTF-16 numeric metadata, doc_len/text length
agreement, surrogate-pair boundaries, invalid UTF-16 boundaries, replay
correctness, extract / micro_episode integration, TypeScript compatibility,
hash compatibility, event durability, production readiness, real-data
readiness, or model performance.

## 5. Target Phase 2 Policy

For Web logger v0.2-style events that pass Phase 1 with
`position_unit=utf16_code_unit`, Phase 2 should validate numeric metadata
against UTF-16 code unit semantics when sufficient text context is available.

Target checks:

- `doc_len_before` equals the UTF-16 code unit length of the relevant
  before-text context.
- `doc_len_after` equals the UTF-16 code unit length of the relevant
  after-text context.
- cursor offsets are not beyond the UTF-16 length of the relevant text
  context.
- selection start / end offsets are not beyond the UTF-16 length of the
  relevant text context.
- selection start is not greater than selection end.
- cursor / selection offsets do not split surrogate pairs.
- invalid UTF-16 boundaries fail closed.
- diagnostics remain body-free and public-safe.

Current `RawEvent` does not carry full before-text or after-text fields. It
does carry edit text fields and numeric metadata. Therefore Phase 2 must not
guess missing context. The lowest-risk implementation should either maintain a
minimal synthetic document context while validating a JSONL sequence or return
a public-safe unavailable classification for checks that lack enough context.
That context tracker must remain a validator-side consistency check and must
not be presented as full replay correctness.

## 6. Required Phase 2 Reason Codes

Required stable Phase 2 reason codes:

- `doc_len_before_utf16_mismatch`
- `doc_len_after_utf16_mismatch`
- `start_greater_than_end`
- `offset_beyond_utf16_length`
- `offset_inside_surrogate_pair`
- `invalid_utf16_boundary`

Optional or derived reason codes:

- `byte_index_supplied_as_utf16_when_detectable`
- `utf16_numeric_metadata_validation_unavailable`
- `insufficient_text_context_for_utf16_validation`

Recommendation: implement the required reason codes first. For the
byte-index misuse fixture, prefer an existing required reason code when the
misuse is detectable as an offset beyond UTF-16 length or invalid UTF-16
boundary. Use `insufficient_text_context_for_utf16_validation` only if future
implementation chooses to expose an explicit non-failing or failing
unavailable state; otherwise keep insufficient context as an internal
skip-without-claim boundary.

## 7. Fixture Mapping Table

Metadata-only Phase 2 mapping:

| case_id | current expected_reason_code | Phase 1 behavior | future Phase 2 expected behavior | future Phase 2 reason_code | required text context | helper needed | direct validator check feasible | deferred if context unavailable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `valid_ascii_utf16_position_unit` | `none` | pass | pass | `none` | before/after context or sequence state | UTF-16 length and boundary helper | yes | no |
| `valid_japanese_cursor_utf16_position_unit` | `none` | pass | pass | `none` | sequence state with Japanese edit context | UTF-16 length and boundary helper | yes | no |
| `valid_japanese_selection_utf16_position_unit` | `none` | pass | pass | `none` | sequence state with selection context | UTF-16 range helper | yes | no |
| `valid_emoji_boundary_utf16_position_unit` | `none` | pass | pass | `none` | sequence state around emoji boundary | UTF-16 offset helper | yes | no |
| `valid_mixed_japanese_emoji_utf16_position_unit` | `none` | pass | pass | `none` | sequence state with mixed text | UTF-16 length and range helper | yes | no |
| `invalid_doc_len_before_utf16_mismatch` | `doc_len_before_utf16_mismatch` | pass or non-Phase1 result | fail | `doc_len_before_utf16_mismatch` | before-text context from sequence state | UTF-16 length helper | yes | yes, if no context |
| `invalid_doc_len_after_utf16_mismatch` | `doc_len_after_utf16_mismatch` | pass or non-Phase1 result | fail | `doc_len_after_utf16_mismatch` | after-text context from sequence state | UTF-16 length helper | yes | yes, if no context |
| `invalid_selection_start_greater_than_end` | `start_greater_than_end` | may fail existing selection check with legacy reason | fail | `start_greater_than_end` | none beyond numeric pair | range ordering helper or direct check | yes | no |
| `invalid_offset_beyond_utf16_length` | `offset_beyond_utf16_length` | may fail existing bounds check with legacy reason | fail | `offset_beyond_utf16_length` | relevant text context or trusted doc_len | UTF-16 offset helper | yes | yes, if no context |
| `invalid_surrogate_pair_internal_offset` | `offset_inside_surrogate_pair` | pass or non-Phase1 result | fail | `offset_inside_surrogate_pair` | text containing surrogate-pair boundary | UTF-16 offset helper | yes | yes, if no context |
| `invalid_byte_index_supplied_as_utf16_when_detectable` | `offset_beyond_utf16_length` | pass or non-Phase1 result | fail only when detectable | `offset_beyond_utf16_length` or `invalid_utf16_boundary` | text context where byte-like value is inconsistent | UTF-16 offset helper | yes for this fixture | yes for ambiguous cases |

No fixture bodies are pasted here.

## 8. Byte-Index Misuse Detectability Boundary

Byte-index misuse is not always detectable from a single numeric offset. A
byte-like offset is detectable only when the supplied number is inconsistent
with UTF-16 length or scalar boundary semantics. If the byte-like value also
falls on a valid UTF-16 code unit boundary, the validator cannot reliably
infer misuse without additional evidence.

Future tests should assert only detectable cases. Docs and status markers must
not claim general byte-index misuse detection.

## 9. Shared UTF-16 Helper Strategy

Audited options:

- Option A: move or expose reusable UTF-16 helper functionality from
  `kslog_replay` to `kslog_schema`. Then `kslog_validate` and `kslog_replay`
  both use `kslog_schema`. This avoids a `kslog_validate -> kslog_replay`
  dependency and keeps UTF-16 semantics near shared event schema concepts.
- Option B: duplicate a minimal helper in `kslog_validate`. This avoids a
  cross-crate move but risks drift from replay behavior.
- Option C: create a new shared crate. This is clean but requires Cargo
  metadata changes and is too large for the next narrowly scoped Step.
- Option D: add a direct `kslog_validate -> kslog_replay` dependency. This is
  not recommended because validator would depend on replay implementation.

Recommendation: Option A. Extract or expose shared UTF-16 offset/length helper
APIs from `kslog_schema`, then update `kslog_replay` and later
`kslog_validate` to use the shared helper.

Recommended split:

- Step-web-logger-056: extract shared UTF-16 helper into `kslog_schema` and
  update replay imports/tests.
- Step-web-logger-057: implement `kslog_validate` Phase 2 numeric metadata
  validation using the shared helper.

This split keeps helper movement and validator behavior change separate.

## 10. Crate Dependency Design

Desired dependency shape:

- `kslog_validate -> kslog_schema`
- `kslog_replay -> kslog_schema`
- no `kslog_validate -> kslog_replay`
- no dependency cycle
- no new crate unless separately justified

`kslog_validate` and `kslog_replay` already depend on `kslog_schema`. Moving
helper APIs into `kslog_schema` should not require adding a new dependency
edge, though implementation may update imports and public exports. No Cargo
metadata changes should be needed for Option A unless the helper extraction
requires a new module feature or dependency.

## 11. Validator Insertion Point

Audited current order:

1. line length / empty-line policy
2. JSON parse into `serde_json::Value`
3. no-oracle forbidden-field pre-scan
4. `RawEvent` deserialize
5. Phase 1 `position_unit` policy
6. sequence checks
7. timestamp checks
8. cursor-vs-doc_len bounds
9. selection ordering and bounds

Recommended Phase 2 insertion point:

1. no-oracle / forbidden-field pre-scan
2. JSONL parse / `RawEvent` deserialize
3. Phase 1 `position_unit` policy
4. Phase 2 UTF-16 numeric metadata validation
5. existing sequence / timestamp / cursor / selection / doc_len checks, or a
   carefully migrated integration with existing numeric checks

Phase 2 should run only after `position_unit=utf16_code_unit` is accepted by
Phase 1. Unsupported, missing, mismatch, and unknown schema version cases
should fail in Phase 1 before Phase 2. Legacy missing cases should not be
forced into Phase 2 unless explicitly designed. Diagnostics must remain
body-free.

## 12. Test Design For Future Implementation

Recommended focused test filter:

`cargo test -p kslog_validate position_unit_phase2`

Future tests should cover:

- all 5 valid position_unit fixtures continue to pass
- `invalid_doc_len_before_utf16_mismatch` fails with
  `doc_len_before_utf16_mismatch`
- `invalid_doc_len_after_utf16_mismatch` fails with
  `doc_len_after_utf16_mismatch`
- `invalid_selection_start_greater_than_end` fails with
  `start_greater_than_end`
- `invalid_offset_beyond_utf16_length` fails with
  `offset_beyond_utf16_length`
- `invalid_surrogate_pair_internal_offset` fails with
  `offset_inside_surrogate_pair`
- detectable byte-index misuse fails with `offset_beyond_utf16_length` or
  `invalid_utf16_boundary`, depending on the fixture's observable mismatch
- Phase 1 failures still produce Phase 1 reason codes, not Phase 2 reason
  codes
- legacy missing position_unit remains explicitly allowed or categorized as
  designed
- diagnostics do not print raw event body or raw text
- existing synthetic valid fixtures remain compatible
- existing invalid synthetic fixtures remain compatible

## 13. Existing Phase 1 Regression Strategy

`cargo test -p kslog_validate position_unit` should remain pass. Phase 1
reason codes should not be changed by Phase 2. The Step049 Makefile target
should remain focused on Phase 1 unless a new target is created. The
release-quality Phase 1 label should not be relabeled as full `position_unit`
policy.

Future Phase 2 should get its own Makefile and release-quality chain after
implementation.

## 14. Makefile / Release-Quality Staging For Phase 2

Recommended later chain:

- Step-web-logger-056: extract shared UTF-16 helper into `kslog_schema`
- Step-web-logger-057: implement Rust validator Phase 2 UTF-16 numeric
  metadata validation
- Step-web-logger-058: Phase 2 Makefile target design
- Step-web-logger-059: add Phase 2 Makefile target
- Step-web-logger-060: Phase 2 release-quality integration design
- Step-web-logger-061: Phase 2 release-quality wrapper integration
- Step-web-logger-062: Phase 2 run record workflow design
- Step-web-logger-063: Phase 2 status marker
- Step-web-logger-064: Phase 2 final safety review

Step055 does not add Makefile or wrapper integration.

## 15. Public-Safe Diagnostics Design

Diagnostics should include only public-safe metadata:

- reason code
- line number / seq if needed
- relative fixture case id if needed
- lengths / counts if needed

Diagnostics must not include raw event JSON, full JSONL line, raw source text,
selected text, inserted / deleted text, private path, absolute local path,
real participant data, raw learner text, logits / probabilities, or
performance metric body.

## 16. Interaction With Existing doc_len / Cursor / Selection Checks

Current `kslog_validate` already checks cursor positions against
`doc_len_before` / `doc_len_after`, selection start/end ordering, and
selection bounds against doc_len metadata. These checks are numeric metadata
checks against reported doc_len values; they are not UTF-16-aware checks
against actual text context and use existing reason codes such as
`cursor_out_of_bounds`, `selection_range_inverted`, and
`selection_out_of_bounds`.

Phase 2 should either precede these checks for Web logger v0.2-style
`utf16_code_unit` events or wrap/migrate them carefully so Phase 2 fixtures
receive the required reason codes. Existing non-Web-logger synthetic fixture
behavior should remain compatible. Diagnostics must remain body-free.

## 17. Interaction With Replay Helper And Step031

The replay helper proves replay-side conversion behavior, not validator
policy. Validator Phase 2 should not call `kslog_replay`. If helper logic is
moved to `kslog_schema`, replay tests must remain pass.

Phase 2 validator pass would not prove replay correctness, and replay
correctness remains a separate accepted boundary.

## 18. Interaction With TypeScript Logger

Phase 2 validator design assumes events declare
`position_unit=utf16_code_unit`. It does not prove that TypeScript currently
emits all required fields. TypeScript emission and compatibility review remain
separate. TypeScript/Rust compatibility should later check real emitted event
shape using synthetic browser-side fixtures.

## 19. Interaction With SHA-256 Hash Compatibility

Phase 2 UTF-16 numeric validation is not hash compatibility. Step055
implements no SHA-256 helper, no TypeScript/Rust hash vector check, and no
current TypeScript/Rust hash equivalence claim.

## 20. Interaction With Event Durability

Phase 2 numeric validation is not event durability. Queue / IndexedDB / ack /
retry / dedup remain future work. Server-side idempotency / event_id dedup
remains future work. Ordering and delivery durability remain open.

## 21. No-Oracle / Synthetic-Only Boundary

Future Phase 2 tests should use synthetic fixtures only. No real participant
data, raw learner text, final_text, observed_after_text, gold labels,
post-hoc annotation, test-set tuning, or model performance validation should
be introduced. No-oracle constraints remain unchanged.

## 22. Non-Equivalence Cautions

- Design is not implementation.
- Phase 2 design is not Phase 2 validation.
- Phase 2 validation would not prove replay correctness.
- Phase 2 validation would not prove extract integration.
- Phase 2 validation would not prove micro_episode integration.
- Phase 2 validation would not prove TypeScript compatibility.
- Phase 2 validation would not prove hash compatibility.
- Phase 2 validation would not prove event durability.
- Synthetic-only validation is not real-data readiness.
- Release-quality pass is not production readiness.

## 23. Non-Claims

This design does not claim production readiness, real-data readiness, model
performance, F1 attainment, accuracy attainment, ECE attainment, AURCC
attainment, broader Unicode correctness completion, extract integration
completion, micro_episode integration completion, Phase 2 UTF-16 numeric
validation implementation, hash compatibility implementation completion,
TypeScript/Rust vector check implementation, current TypeScript/Rust hash
equality, event durability implementation, data collection readiness, or
deployment readiness.

## 24. Recommended Next Step

Recommended next step:

`Step-web-logger-056: extract shared UTF-16 helper into kslog_schema`

Step056 should be an implementation Step because the audit shows the shared
dependency direction is already available: both `kslog_validate` and
`kslog_replay` depend on `kslog_schema`, while a direct
`kslog_validate -> kslog_replay` dependency would be undesirable. Step056
should move or expose reusable UTF-16 helper APIs from replay into schema,
update replay imports/tests, and keep validator Phase 2 behavior for a later
Step unless explicitly scoped otherwise.

Step056 should update README and full technical specification docs because
shared helper behavior changes. It should not modify TypeScript / Python /
fixture JSON / Makefile / wrapper and should not claim Phase 2 validation.

## Step-web-logger-056 Implementation Note

Step-web-logger-056 extracts reusable UTF-16 code unit length and offset/range
conversion into `kslog_schema::utf16_offsets`. `kslog_replay::utf16_offsets`
remains as a compatibility re-export, preserving the existing replay helper
path while using the shared schema helper.

This satisfies the shared-helper prerequisite for future Phase 2 validator work
without adding a `kslog_validate -> kslog_replay` dependency. It does not
implement validator Phase 2 doc_len, cursor, selection, surrogate-pair,
invalid-boundary, or detectable byte-index-misuse enforcement.

## Step-web-logger-057 Implementation Note

Step-web-logger-057 implements the bounded Rust validator Phase 2 UTF-16
numeric metadata checks in `kslog_validate`. The implementation applies only
after Phase 1 accepts a Web logger v0.2-style event with
`position_unit=utf16_code_unit`, uses `kslog_schema::utf16_offsets`, and adds no
`kslog_validate -> kslog_replay` dependency.

The implemented reason-code boundary covers
`doc_len_before_utf16_mismatch`, `doc_len_after_utf16_mismatch`,
`start_greater_than_end`, `offset_beyond_utf16_length`,
`offset_inside_surrogate_pair`, and `invalid_utf16_boundary`. Focused tests
cover the five valid position-unit fixtures and the Phase 2 invalid fixture
cases. Detectable byte-index misuse remains limited to cases that contradict
UTF-16 length or scalar boundaries.

Step057 does not add a Makefile target, does not add release-quality
integration for Phase 2, does not change fixture JSON, does not change replay
behavior, does not implement extract / micro_episode integration, does not
change TypeScript logger behavior, does not add SHA-256 helpers or
TypeScript/Rust vector checks, and does not provide production readiness,
real-data readiness, or model performance evidence.

## Step-web-logger-058 Makefile Target Design Follow-Up

Step-web-logger-058 adds
[Rust validator Phase 2 UTF-16 numeric metadata Makefile target design](web_logger_rust_validator_phase2_utf16_numeric_metadata_makefile_target_design.md).
It recommends future target
`check-web-logger-rust-validator-position-unit-phase2-utf16-numeric` with
command `cargo test -p kslog_validate position_unit_phase2`.

The design also records that the existing Phase 1 target currently uses the
broader substring filter `position_unit`, which now matches Phase 2 tests. It
recommends correcting that target command to
`cargo test -p kslog_validate position_unit_phase1` in the same future
Makefile implementation Step. Step058 does not change Makefile or wrapper
behavior.
