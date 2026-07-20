# Rust Validator Position Unit Policy Test and Fixture Mapping Design

## 1. Title

Rust Validator Position Unit Policy Test and Fixture Mapping Design

## 2. Scope

This is a design-only / docs-only step. It makes no Rust code changes, no
TypeScript code changes, no Python code changes, no test changes, no fixture
JSON changes, no Makefile changes, no release-quality wrapper changes, no CI
workflow changes, no `Cargo.toml` / `Cargo.lock` changes, and no
`package.json` changes.

This step makes no validator behavior changes, no schema behavior changes, no
replay behavior changes, no extract / micro_episode behavior changes, and no
event durability implementation. It provides no production readiness proof, no
real-data readiness proof, and no model performance proof.

## 3. Design Status

Step-web-logger-043 accepted the bounded fixture contract validation boundary
for the fixed 17-case synthetic Web logger position_unit fixture matrix.

Step-web-logger-044 designed the staged Rust schema / validator implementation
strategy. Step-web-logger-045 implemented the Rust `kslog_schema` field and
parser boundary for position_unit metadata, but did not implement Rust
validator policy enforcement.

Step-web-logger-046 designs Rust validator tests and fixture mapping only.
`kslog_validate` position_unit enforcement remains future work.

## 4. Step045 Schema Boundary Review

Step-web-logger-045 adds two optional raw metadata fields to
`kslog_schema::RawEvent`:

- `position_unit: Option<String>`
- `research_schema_target: Option<String>`

`RawEvent` still uses `serde(deny_unknown_fields)`, so no-oracle forbidden
fields and unrelated unknown fields are not silently accepted. Unsupported
position_unit values deserialize as raw strings instead of failing before
validator policy can classify them.

The typed boundary currently includes:

- `PositionUnit::Utf16CodeUnit`
- `PositionUnitPolicyError::MissingPositionUnit`
- `PositionUnitPolicyError::UnsupportedPositionUnit`
- `PositionUnitPolicyError::PositionUnitSchemaMismatch`
- `PositionUnitPolicyError::UnknownSchemaVersion`
- `RawEvent::parse_position_unit()`
- `RawEvent::position_unit_policy()`

Stable reason-code strings are:

- `none`
- `missing_position_unit`
- `unsupported_position_unit`
- `position_unit_schema_mismatch`
- `unknown_schema_version`

Focused `kslog_schema` tests cover supported `utf16_code_unit`, missing values,
unsupported `byte_index` / `code_point`, schema mismatch, unknown schema
version, unknown-field rejection, body-free parser diagnostics, and schema
deserialization of the Step034 fixture records.

Step045 also required compatibility-only edits in `kslog_replay` and
`kslog_extract` test helper initializers because `RawEvent` is a public struct
constructed with field literals. Those edits added `None` metadata fields and
did not change replay or extraction behavior.

Step045 does not implement `kslog_validate` position_unit policy enforcement,
UTF-16 numeric metadata validation, validate / extract / micro_episode
integration, TypeScript logger behavior, SHA-256 helper work, TypeScript/Rust
vector checks, event durability, production readiness, real-data readiness, or
model performance evidence.

## 5. Current kslog_validate Audit

Current `kslog_validate` reads JSONL input, applies line-size and empty-line
policy, parses each non-empty line as JSON, requires each line to be a JSON
object, pre-scans no-oracle forbidden fields, deserializes to
`kslog_schema::RawEvent`, then validates sequence, timestamp ordering, cursor
bounds, and selection bounds.

Current `ValidationErrorKind` values are descriptive Rust enum variants rather
than a complete public reason-code system. Existing display text is mostly
metadata-only: line number, field names, numeric values, and schema parse
messages. The no-oracle pre-scan rejects fields such as future text and labels
before `RawEvent` deserialization.

Current checks include:

- malformed JSON
- non-object JSONL records
- no-oracle forbidden fields
- `RawEvent` serde schema errors
- `seq` gaps and overflow
- timestamp inversion
- cursor positions greater than available document lengths
- selection start greater than end
- selection positions greater than available document lengths

Current limitations for position_unit:

- `kslog_validate` does not call the Step045 parser/accessor.
- Missing and unsupported position_unit values are not validator policy
  failures yet.
- Unknown schema versions are not position_unit policy failures yet.
- UTF-16 document length and surrogate-boundary semantics are not validator
  checks.

The lowest-risk insertion point for Phase 1 is after `RawEvent` deserialization
and before sequence / timestamp / range validation. This lets the validator use
typed schema data, preserve the no-oracle pre-scan, and fail fast for
position_unit policy cases before unrelated numeric checks obscure the intended
reason code.

## 6. Target Validator Phase 1 Policy

Recommended Phase 1 enforces only presence / value / schema-version gating:

- Audited Web logger v0.2+ fixture-targeted events must declare
  `position_unit=utf16_code_unit`.
- Missing position_unit fails for audited Web logger v0.2+ events with
  `missing_position_unit`.
- Unsupported `byte_index` fails with `unsupported_position_unit`.
- Unsupported `code_point` fails with `unsupported_position_unit`.
- Schema mismatch fails with `position_unit_schema_mismatch`.
- Unknown schema version fails closed with `unknown_schema_version` when the
  event is in the Web logger position_unit target boundary.
- Explicit legacy missing-position-unit fixtures remain allowed or categorized
  through a separate legacy gate.
- Existing legacy synthetic raw event fixtures remain compatible.

Phase 1 must not validate UTF-16 numeric metadata. It should not validate
`doc_len_before` / `doc_len_after` against text content, cursor offsets beyond
UTF-16 length, surrogate-pair internal offsets, or byte-index-as-UTF-16 misuse.
It should not call replay, move the UTF-16 helper, or implement extract /
micro_episode integration.

## 7. Phase 2 Deferred Policy

Phase 2 should cover numeric UTF-16 metadata checks:

- `doc_len_before_utf16_mismatch`
- `doc_len_after_utf16_mismatch`
- `start_greater_than_end`
- `offset_beyond_utf16_length`
- `offset_inside_surrogate_pair`
- `invalid_utf16_boundary`

Some generic range checks already exist in `kslog_validate`, but Phase 2 should
decide whether those existing errors should be mapped to Web logger
position_unit reason codes or kept separate. Phase 2 likely needs a shared
UTF-16 helper strategy. Avoid adding a direct `kslog_validate -> kslog_replay`
dependency if it creates architectural coupling or a dependency cycle. Do not
implement Phase 2 in the next step unless a separate design explicitly expands
the boundary.

## 8. Fixture Mapping Table

This table maps the Step034 fixture contract to future Rust validator testing
without copying fixture bodies.

| case_id | kind | Python status | Python reason | Phase 1 expected behavior | Phase 1 reason | Phase 2 / deferred note | text context | read by Phase 1 test |
|---|---|---:|---|---|---|---|---:|---:|
| `valid_ascii_utf16_position_unit` | valid | pass | none | pass | none | none | yes | yes |
| `valid_japanese_cursor_utf16_position_unit` | valid | pass | none | pass | none | numeric semantics remain Phase 2 evidence | yes | yes |
| `valid_japanese_selection_utf16_position_unit` | valid | pass | none | pass | none | numeric semantics remain Phase 2 evidence | yes | yes |
| `valid_emoji_boundary_utf16_position_unit` | valid | pass | none | pass | none | surrogate boundary acceptance remains Phase 2 evidence | yes | yes |
| `valid_mixed_japanese_emoji_utf16_position_unit` | valid | pass | none | pass | none | numeric semantics remain Phase 2 evidence | yes | yes |
| `invalid_v0_2_missing_position_unit` | invalid | fail | missing_position_unit | fail | missing_position_unit | none | no | yes |
| `invalid_unsupported_position_unit_byte_index` | invalid | fail | unsupported_position_unit | fail | unsupported_position_unit | none | no | yes |
| `invalid_unsupported_position_unit_code_point` | invalid | fail | unsupported_position_unit | fail | unsupported_position_unit | none | no | yes |
| `invalid_position_unit_schema_mismatch` | invalid | fail | position_unit_schema_mismatch | fail | position_unit_schema_mismatch | none | no | yes |
| `invalid_doc_len_before_utf16_mismatch` | invalid | fail | doc_len_before_utf16_mismatch | position_unit policy passes; do not assert Phase 1 failure | none | defer UTF-16 length check | yes | no |
| `invalid_doc_len_after_utf16_mismatch` | invalid | fail | doc_len_after_utf16_mismatch | position_unit policy passes; do not assert Phase 1 failure | none | defer UTF-16 length check | yes | no |
| `invalid_selection_start_greater_than_end` | invalid | fail | start_greater_than_end | not a position_unit Phase 1 failure | none | existing generic selection check may fail before Phase 2 mapping | no | no |
| `invalid_offset_beyond_utf16_length` | invalid | fail | offset_beyond_utf16_length | not a position_unit Phase 1 failure | none | defer UTF-16 offset boundary mapping | yes | no |
| `invalid_surrogate_pair_internal_offset` | invalid | fail | offset_inside_surrogate_pair | position_unit policy passes; do not assert Phase 1 failure | none | defer surrogate-boundary check | yes | no |
| `invalid_byte_index_supplied_as_utf16_when_detectable` | invalid | fail | offset_beyond_utf16_length | position_unit policy passes; do not assert Phase 1 failure | none | defer detectable byte-index misuse check | yes | no |
| `invalid_unknown_schema_version` | invalid | fail | unknown_schema_version | fail | unknown_schema_version | none | no | yes |
| `legacy_missing_position_unit_explicitly_gated` | legacy | legacy_allowed | legacy_position_unit_missing_allowed | pass through explicit legacy gate | legacy_position_unit_missing_allowed or none | should not imply v0.2 missing allowance | no | yes |

Phase 1 tests should also include a schema-deserialization smoke over all
Step034 records to confirm `RawEvent` compatibility, but the Phase 1 validator
pass/fail assertions should focus on the rows marked `read by Phase 1 test=yes`.

## 9. Gating Design for Rust Validator Tests

Future tests should use the actual Step045 fields and helpers:

- `RawEvent::is_known_raw_event_schema_version()`
- `RawEvent::is_web_logger_v0_2_or_later()`
- `RawEvent::is_web_logger_position_unit_target()`
- `RawEvent::is_legacy_position_unit_missing_allowed()`
- `RawEvent::position_unit_policy()`

For Phase 1, audited Web logger v0.2+ should mean the exact fixture boundary:

- `logger_schema_version == "kslog.raw_event.v2"`
- `research_schema_target == "web_logger_position_unit_schema_v0.1"`

Legacy allowance should mean the exact audited legacy fixture boundary:

- `logger_schema_version == "kslog.raw_event.v1"`
- `position_unit` is missing
- the test is explicitly selected as a legacy case

Unknown schema version behavior should be tested with the audited
`kslog.raw_event.v9` fixture-targeted event. Missing `research_schema_target`
should not trigger the new position_unit requirement in existing synthetic
fixtures. Future implementation should encode only audited strings and avoid
guessing broader version semantics.

## 10. Rust Validator Error / Reason Code Design

Future `kslog_validate` should add a position_unit-specific error kind or
reason-code accessor without exposing event bodies.

Required Phase 1 reason codes:

- `missing_position_unit`
- `unsupported_position_unit`
- `position_unit_schema_mismatch`
- `unknown_schema_version`
- `legacy_position_unit_missing_allowed`, if legacy allowance is surfaced in a
  report rather than only tested as pass-through

The existing validator may keep Rust enum names such as
`ValidationErrorKind::PositionUnitPolicy`, or use separate variants for each
case. Regardless of enum shape, reason-code strings should be stable and
public-safe. Error display should not include raw event JSON, source text,
selected text, inserted text, deleted text, machine-specific filesystem
locations, participant-origin records, model score dumps, or metric payloads.

## 11. Test Design for Future Implementation Step

Recommended focused tests for `kslog_validate`:

- one valid Web logger v0.2+ position_unit fixture passes
- all 5 valid position_unit fixtures pass Phase 1
- missing position_unit v0.2+ fixture fails with `missing_position_unit`
- unsupported `byte_index` fixture fails with `unsupported_position_unit`
- unsupported `code_point` fixture fails with `unsupported_position_unit`
- schema mismatch fixture fails with `position_unit_schema_mismatch`
- unknown schema version fixture fails with `unknown_schema_version`
- legacy missing position_unit fixture is explicitly allowed or categorized
- existing legacy synthetic valid fixtures continue to pass
- existing invalid synthetic fixtures continue to fail as before
- validator diagnostics do not print raw body or raw text
- numeric invalid fixtures are documented as deferred unless the next
  implementation explicitly expands beyond Phase 1

Safest placement is unit tests in `crates/kslog_validate/src/lib.rs` if the
new policy remains a small private helper near the existing validation flow.
Use integration tests under `crates/kslog_validate/tests` only if the public API
needs black-box coverage. Fixture-driven tests should read the Step034 JSONL
files, but should not copy fixture bodies into test source or failure messages.

## 12. Test Fixture Access Strategy

Recommendation: Option C, a small Rust-side mapping table in tests, paired
with direct fixture file reads.

Rationale:

- avoids depending on the Python validator
- avoids adding case_index parsing complexity to initial Rust tests
- keeps expected Phase 1 behavior explicit
- keeps failure output public-safe
- does not duplicate fixture bodies
- does not mutate fixture root or regenerate expected values

Option B, reading `case_index.json`, is useful for a later broader fixture
contract parity test, but it may add unnecessary serde parsing complexity to
the first Phase 1 validator implementation. Option A, hard-coding direct paths
without an explicit mapping table, is simple but makes Phase 1 / Phase 2
deferred status less visible.

## 13. Existing Fixture Compatibility Strategy

Future validator implementation must not require position_unit globally.

Existing synthetic raw event fixtures use `kslog.raw_event.v1` and omit
position_unit. Those valid fixtures should continue to pass. Existing invalid
fixtures should continue to fail for their current reasons where practical.
Unknown fields and no-oracle forbidden fields should remain rejected.

Unsupported position_unit values should be classified only when an event
otherwise reaches the position_unit policy check. Do not migrate all existing
fixtures in the first validator step.

## 14. UTF-16 Helper Dependency Strategy

Phase 1 should not call `kslog_replay::utf16_offsets`. Do not add a dependency
from `kslog_validate` to `kslog_replay` for Phase 1.

Phase 2 should separately decide whether the UTF-16 offset helper belongs in a
shared crate, stays in replay with a wrapper boundary, or is duplicated with an
explicit acceptance of maintenance cost. Avoid dependency cycles and avoid
moving helper code without a dedicated design.

## 15. Public-Safe Diagnostics Design

Allowed diagnostics:

- reason_code
- relative fixture path
- line number
- `seq`
- field names
- numeric counts and offsets

Forbidden diagnostics:

- raw event JSON
- full JSONL line
- source text
- selected text
- inserted text by default
- deleted text by default
- machine-specific filesystem locations
- participant-origin records
- learner-authored raw content
- model score dumps
- metric payloads

## 16. Step045 Compatibility Exception Handling

Step045 required minimal test-helper updates in `kslog_replay` and
`kslog_extract` because `RawEvent` is a public struct and downstream tests
construct it with field literals. The change added `None` for the new optional
metadata fields and was compile compatibility only.

Future implementation prompts should explicitly allow minimal downstream
test-helper compile compatibility edits when public struct fields are added.
They should still prohibit behavior changes in unrelated crates. Final reports
must distinguish compile compatibility from behavior changes and must list any
such exception explicitly.

## 17. Proposed Step-web-logger-047 Implementation Scope

Recommended next implementation scope:

- implement Rust `kslog_validate` Phase 1 position_unit policy enforcement
- use the Step045 parser/accessor boundary where feasible
- add focused Rust tests for Phase 1 fixture mapping
- modify only `crates/kslog_validate` and, only if strictly necessary,
  `crates/kslog_schema`
- do not modify `kslog_replay`, `kslog_extract`, or `kslog_micro_episode`
  unless compile compatibility absolutely requires it
- do not modify TypeScript / Python
- do not modify fixture JSON
- do not modify Makefile / wrapper / CI
- update README and full technical specification related docs because
  validator behavior changes
- run Rust tests and existing fixture validator checks
- do not claim Phase 2 UTF-16 numeric validation
- do not claim extract / micro_episode integration
- do not claim production / real-data readiness

## 18. Future Release-Quality Staging

After Rust validator implementation and focused checks:

- Step-web-logger-048: Makefile target design for Rust validator position_unit
  policy checks
- Step-web-logger-049: add Makefile target
- Step-web-logger-050: release-quality integration design
- Step-web-logger-051: release-quality wrapper integration
- Step-web-logger-052: remote/manual run record workflow design
- Step-web-logger-053: status marker
- Step-web-logger-054: final safety review

Do not add Makefile or wrapper integration in Step046.

## 19. Relationship to Step043 Accepted Boundary

Step043 accepted fixture contract validation only. Step046 designs Rust
validator enforcement strategy only and does not expand the accepted boundary.
Rust validator implementation remains future work.

## 20. Relationship to Step045 Schema Boundary

Step045 implemented the schema parser/accessor boundary that future
`kslog_validate` should call where feasible. Step046 does not modify schema
code and does not reimplement raw string parsing independently.

## 21. Relationship to Step031 Replay Integration

Step031 replay integration remains separate. Phase 1 validator policy does not
prove replay correctness, and replay correctness does not prove validator
policy. Phase 2 numeric UTF-16 validation may later need a shared helper
strategy.

## 22. Relationship to TypeScript Logger

Rust validator policy assumes future Web logger v0.2+ events emit explicit
`position_unit=utf16_code_unit`. TypeScript logger changes remain future work
if not already implemented. Step046 does not modify TypeScript, and
TypeScript/Rust compatibility remains separate.

## 23. Relationship to SHA-256 Hash Compatibility

Step046 does not implement a Rust SHA-256 helper, a TypeScript SHA-256 helper,
or TypeScript/Rust hash vector checks. It does not prove current TypeScript
and Rust hashes match. Hash compatibility remains a separate chain.

## 24. Relationship to Event Durability

Step046 does not implement event durability. Queue / IndexedDB /
acknowledgement / retry / dedup remain unimplemented. Server-side idempotency /
event_id dedup remains unimplemented. Ordering and delivery durability remain
open.

## 25. No-Oracle / Synthetic-Only Boundary

Future tests should use synthetic fixtures only. They must not introduce
participant-origin records, learner-authored raw content, future final-text
snapshots, observed-after snapshots, gold labels, post-hoc annotation,
test-set tuning, or model performance validation. No-oracle constraints remain
unchanged.

## 26. Non-Equivalence Cautions

- Test design is not implementation.
- Fixture mapping is not validator behavior.
- Rust schema parser boundary is not validator enforcement.
- Phase 1 validator enforcement will not prove Phase 2 UTF-16 numeric
  correctness.
- Rust validator enforcement will not prove replay correctness.
- Rust validator enforcement will not prove TypeScript compatibility.
- Rust validator enforcement will not prove hash compatibility.
- Rust validator enforcement will not prove event durability.
- Synthetic-only validation is not real-data readiness.
- Release-quality pass is not production readiness.

## 27. Non-Claims

This document does not claim production readiness, real-data readiness, model
performance, F1 attainment, accuracy attainment, ECE attainment, AURCC
attainment, broader Unicode correctness completion, validate integration
completion, extract integration completion, micro_episode integration
completion, Rust validator position_unit implementation, Phase 2 UTF-16
numeric validation implementation, hash compatibility implementation
completion, TypeScript/Rust vector check implementation, current
TypeScript/Rust hash equality, event durability implementation, data
collection readiness, or deployment readiness.

## 28. Recommended Next Step

Recommended next step:

Step-web-logger-047: implement Rust validator Phase 1 position_unit policy
enforcement

Step047 should be an implementation step. It should implement presence / value
/ schema-version gating in `kslog_validate`, use the Step045 parser/accessor
boundary where feasible, add focused Rust tests, map only Phase 1 cases, and
leave UTF-16 numeric metadata validation for Phase 2. It should not modify
TypeScript / Python / fixture JSON / Makefile / wrapper / CI. It should update
README and full technical specification related docs because validator
behavior changes, and it should not claim production or real-data readiness.

## 29. Step-web-logger-047 Implementation Status

Step-web-logger-047 adds the Phase 1 validator enforcement planned by this
mapping design. `kslog_validate` now checks fixture-targeted Web logger
v0.2-style records after `RawEvent` deserialization and requires explicit
`position_unit=utf16_code_unit` for that bounded target. Missing,
unsupported, schema-mismatch, and unknown-version cases fail with stable
body-free reason codes.

The Step034 mapping remains split: the five Phase 1 valid fixtures pass, the
five Phase 1 policy invalid fixtures fail with their Phase 1 reason codes, the
legacy missing-position-unit fixture remains explicitly allowed, and UTF-16
numeric metadata cases remain deferred. Step047 does not depend on
`kslog_replay::utf16_offsets`, does not modify fixtures, Makefile, wrapper,
TypeScript, Python, or release-quality wiring, and does not claim production
or real-data readiness.

## 30. Step-web-logger-048 Makefile Target Design

Step-web-logger-048 adds
[Rust Validator Position Unit Phase 1 Makefile Target Design](web_logger_rust_validator_position_unit_phase1_makefile_target_design.md).

The design recommends exposing the Step047 focused validator tests through
future Makefile target `check-web-logger-rust-validator-position-unit-phase1`
with command `cargo test -p kslog_validate position_unit`. Step059 later
corrects the implemented target command to
`cargo test -p kslog_validate position_unit_phase1`. The design remains
docs-only and does not change Makefile, wrapper, Rust code, tests, fixtures,
TypeScript, Python, release-quality wiring, Phase 2 UTF-16 numeric validation,
production readiness, real-data readiness, or model performance evidence.

## 31. Step-web-logger-049 Makefile Target Implementation

Step-web-logger-049 adds the Makefile target
`check-web-logger-rust-validator-position-unit-phase1` for this mapping's
focused Rust validator tests. The target runs
`cargo test -p kslog_validate position_unit_phase1` after the Step059 filter
correction and is placed before the Phase 2 / Rust UTF-16 replay target group.

The target does not change validator behavior, Rust tests, fixtures,
TypeScript, Python, wrapper behavior, Phase 2 UTF-16 numeric validation,
production readiness, real-data readiness, or model performance evidence.

## 32. Step-web-logger-050 Release-Quality Integration Design

Step-web-logger-050 adds the release-quality integration design for the
Step049 Makefile target. The planned wrapper check remains focused on this
mapping's Phase 1 presence / value / schema-version tests through
`make check-web-logger-rust-validator-position-unit-phase1`.

The design does not expand the mapping to Phase 2 UTF-16 numeric metadata
validation, does not modify Rust code or tests, does not modify fixtures, and
does not add wrapper implementation, production readiness, real-data
readiness, or model performance evidence.

## 33. Step-web-logger-051 Release-Quality Integration

Step-web-logger-051 adds release-quality wrapper coverage for this mapping's
Rust validator Phase 1 focused tests. The wrapper runs
`make check-web-logger-rust-validator-position-unit-phase1`.

This does not expand the mapping to Phase 2 UTF-16 numeric metadata
validation, does not modify Rust code or tests, does not modify fixtures, and
does not add status marker evidence, final safety review acceptance,
production readiness, real-data readiness, or model performance evidence.

## 34. Step-web-logger-052 Run Record Workflow Design

Step-web-logger-052 designs how future status marker evidence should record
the focused Rust validator Phase 1 test mapping. The required public-safe
summary includes focused test count, expected reason-code categories, legacy
missing position_unit gating, and explicit `phase2_utf16_numeric_validation_checked=false`.

This workflow design does not change the mapping, Rust code, tests, fixtures,
status marker files, production readiness, real-data readiness, or model
performance evidence.

## 35. Step-web-logger-053 Remote Status Marker

Step-web-logger-053 created
[Rust validator position_unit Phase 1 release-quality remote run status](status/web_logger_rust_validator_position_unit_phase1_release_quality_remote_run_status.md).
The marker records the focused Phase 1 mapping evidence as public-safe names
and counts only: 9 focused tests passed, missing / unsupported /
schema-mismatch / unknown-version reason-code paths were checked, and legacy
missing `position_unit` gating remained explicit.

The marker does not add Phase 2 UTF-16 numeric metadata validation and does
not reinterpret deferred fixture cases as implemented validator behavior. It
does not change Rust code, tests, fixtures, Makefile, wrapper, release-quality
ordering, production readiness, real-data readiness, or model performance
evidence.

## 36. Step-web-logger-054 Final Safety Review

Step-web-logger-054 created
[Rust validator position_unit Phase 1 release-quality chain final safety review](web_logger_rust_validator_position_unit_phase1_release_quality_chain_final_safety_review.md).
The review accepts the Phase 1 fixture mapping only for presence / value /
schema-version gating and stable reason-code coverage.

Deferred UTF-16 numeric fixture cases remain outside the accepted boundary.
The review does not add validator numeric checks, fixture changes, replay
correctness, extract / micro_episode integration, TypeScript compatibility,
event durability, production readiness, real-data readiness, or model
performance evidence.

## 37. Step-web-logger-055 Phase 2 Fixture Mapping Design

Step-web-logger-055 created
[Rust validator Phase 2 UTF-16 numeric metadata validation design](web_logger_rust_validator_phase2_utf16_numeric_metadata_validation_design.md).
It maps deferred Phase 2 fixture cases for doc_len mismatch, start greater
than end, offset beyond UTF-16 length, surrogate-pair internal offset, and
detectable byte-index misuse.

The design is metadata-only and does not paste fixture bodies, change
fixtures, implement validator numeric checks, or claim Phase 2 release-quality
evidence.

## 38. Step-web-logger-056 Shared Helper Follow-Up

Step-web-logger-056 moves reusable UTF-16 code unit length and offset/range
conversion into `kslog_schema::utf16_offsets` and preserves
`kslog_replay::utf16_offsets` as a compatibility re-export. This supports later
Phase 2 validator fixture mapping without changing the Phase 1 validator
mapping described here.

The Phase 2 doc_len / offset / surrogate-pair checks remain unimplemented, and
this follow-up does not change fixtures, Makefile, release-quality wrapper,
TypeScript/Python code, SHA-256 helper work, TypeScript/Rust vector checks,
event durability, production readiness, real-data readiness, or model
performance evidence.

## 39. Step-web-logger-057 Phase 2 Fixture Mapping Follow-Up

Step-web-logger-057 implements the Phase 2 validator mapping for the fixed
Step034 fixture matrix. The five valid position-unit fixtures continue to pass.
The Phase 2 invalid fixtures are covered with body-free reason codes for
UTF-16 doc length mismatch, `start > end`, beyond-length offsets,
surrogate-pair internal offsets, invalid UTF-16 boundaries where applicable,
and detectable byte-index misuse when the metadata contradicts UTF-16 length or
scalar boundaries.

The Phase 1 fixture mapping remains intact: missing, unsupported,
schema-mismatch, and unknown-version cases keep their Phase 1 reason codes, and
the legacy missing case remains outside the global requirement. This follow-up
does not change fixture JSON and does not add Makefile or release-quality
coverage for Phase 2.

## 40. Step-web-logger-058 Makefile Filter Mapping Follow-Up

Step-web-logger-058 maps the focused test filters to future Makefile targets.
The Phase 1-only mapping uses `position_unit_phase1` and currently covers 9
tests. The Phase 2-only mapping uses `position_unit_phase2` and currently
covers 8 tests.

The existing `position_unit` filter remains a broader manual regression filter
and should not be used as the Phase 1-only Makefile command after Step057.

## 41. Step-web-logger-059 Makefile Filter Mapping Implementation

Step-web-logger-059 implements the filter mapping. The Phase 1 Makefile target
now uses `position_unit_phase1` and the Phase 2 Makefile target uses
`position_unit_phase2`.

The broader `position_unit` filter remains available manually but is no longer
the Phase 1 target command. This keeps the 9-test Phase 1 mapping and 8-test
Phase 2 mapping distinct.

## 42. Step-web-logger-060 Release-Quality Design Follow-Up

Step-web-logger-060 designs wrapper integration for the 8-test Phase 2 mapping
through `make check-web-logger-rust-validator-position-unit-phase2-utf16-numeric`.
It keeps the 9-test Phase 1 mapping separate and does not change fixtures,
Rust tests, or validator behavior.

## 43. Step-web-logger-061 Release-Quality Integration Follow-Up

Step-web-logger-061 exposes the 8-test Phase 2 mapping through release-quality
by calling the existing Makefile target. The 9-test Phase 1 mapping remains
separate and continues to run through the existing Phase 1 release-quality
label.
