# Web Logger Position Unit and Text Hash Schema Clarification

## 1. Title

Web Logger Position Unit and Text Hash Schema Clarification

## 2. Scope

This is a schema-clarification / docs-only step.

Out of scope:

- no TypeScript implementation changes
- no Rust implementation changes
- no Python implementation changes
- no tests changes
- no fixture JSON changes
- no CI workflow changes
- no Makefile changes
- no release-quality wrapper changes
- no data collection authorization
- no production readiness proof
- no real-data readiness proof
- no model performance proof

Event durability work such as queue, IndexedDB, acknowledgement, retry, and deduplication remains out of scope for this step.

## 3. Clarification Status

This document clarifies intended schema policy. It does not implement the policy.

Current implementation may still be partially aligned or non-aligned with the clarified policy. Future implementation steps are required before any real collection boundary can be considered.

Any existing schema version should not be claimed compatible with this clarification unless implementation is updated, tested, and explicitly reviewed. Validators should treat unsupported or ambiguous schema versions as fail-closed once the versioned policy is implemented.

## 4. Position Unit Policy

Browser-originated `selection_start`, `selection_end`, `cursor_pos`, and edit span offsets must be interpreted as UTF-16 code unit offsets.

The schema should expose or document:

```text
position_unit=utf16_code_unit
```

Policy:

- JavaScript `selectionStart` and `selectionEnd` values must not be treated as Unicode scalar indices.
- JavaScript `selectionStart` and `selectionEnd` values must not be treated as UTF-8 byte offsets.
- Rust must not use these offsets directly as byte indices.
- Rust must convert UTF-16 code unit offsets to UTF-8 byte indices using a validated helper in a future implementation step.
- Invalid offsets must fail closed.
- Silent repair, rounding, or best-effort correction is not allowed for replay-critical offsets.

## 5. Position-Related Fields

| field | intended unit | source of value | authored or derived | may Rust trust directly? | validation expectation | fail-closed condition |
| --- | --- | --- | --- | --- | --- | --- |
| `selection_start` | UTF-16 code unit offset | Browser selection state | client-authored | No. Convert through validated helper. | Present value must be within UTF-16 length and at a valid boundary. | Missing required value for replay-critical edit, out of range, or inside a surrogate pair. |
| `selection_end` | UTF-16 code unit offset | Browser selection state | client-authored | No. Convert through validated helper. | Must be within UTF-16 length, at a valid boundary, and not before `selection_start`. | End before start, out of range, or inside a surrogate pair. |
| `cursor_pos` | UTF-16 code unit offset | Browser selection start for collapsed cursor, or explicit cursor capture | client-authored | No. Convert through validated helper. | Must be within UTF-16 length and at a valid boundary. | Out of range or inside a surrogate pair. |
| `doc_len_before` | UTF-16 code unit length under clarified policy | Stored before-text state | client-authored or derived from captured text | No. Compare against validated UTF-16 length of stored context. | Must match the UTF-16 code unit length of the stored before string when present. | Length mismatch for replay-critical event. |
| `doc_len_after` | UTF-16 code unit length under clarified policy | Stored after-text state | client-authored or derived from captured text | No. Compare against validated UTF-16 length of stored context. | Must match the UTF-16 code unit length of the stored after string when present. | Length mismatch for replay-critical event. |
| edit span start/end fields | UTF-16 code unit offsets | Planned or downstream schema clarification target | planned / derived | No. Convert through validated helper. | Must be ordered, in range, and boundary-safe. | Missing required span, inverted span, out of range, or boundary error. |
| inserted / deleted text span metadata | UTF-16 code unit length or offset fields, if represented numerically | Planned or derived from event context | planned / derived | No. Validate against stored string and converted offsets. | Must align with stored context and event operation semantics. | Span/text mismatch, unsupported unit, or ambiguous schema version. |

Current field names in code include before/after variants such as `selection_start_before`, `selection_end_before`, `selection_start_after`, `selection_end_after`, `cursor_pos_before`, and `cursor_pos_after`. This document clarifies the intended policy for the position family and does not claim all field names already implement it.

## 6. UTF-16 to UTF-8 Conversion Policy

Future conversion helper contract:

- input: stored string and UTF-16 code unit offset
- output: UTF-8 byte index
- valid only at a UTF-16 code unit boundary that maps to a Rust `char` boundary
- offsets inside surrogate pairs must be rejected
- offsets beyond UTF-16 length must be rejected
- offsets must not be rounded
- offsets must not be normalized
- helper should be shared by replay, validation, extraction, and later downstream paths that consume replay-critical offsets
- conversion should happen after verifying the stored string used for the event context
- conversion errors should produce validation errors or replay errors, not panics

The helper should never silently reinterpret a UTF-16 offset as a Rust character index or byte index.

## 7. Unicode Normalization Policy

Default policy:

- no Unicode normalization by default
- preserve stored string exactly as captured
- combining sequences and precomposed characters are distinct unless a future schema version explicitly normalizes them
- normalization policy is shared by offset interpretation and hash canonicalization
- any future normalization change requires an explicit schema version bump and migration note

This means offset conversion and hash generation must use the same stored string.

## 8. Newline and Tab Policy

Default policy:

- preserve newline sequences exactly as captured
- do not normalize CRLF / LF / CR by default
- tab is a single Unicode scalar value and one UTF-16 code unit, but display width is irrelevant to stored offsets
- stored string is authoritative for replay and hashing
- line ending normalization must not happen silently
- any future newline normalization requires a schema version bump

## 9. Grapheme Cluster Policy

Human-perceived grapheme clusters are not the stored offset unit.

Schema policy:

- use UTF-16 code unit offsets, not grapheme cluster counts
- combining mark boundaries may be valid code unit offsets while splitting a user-perceived character
- initial validation should check code unit / byte boundary safety, not semantic grapheme editing correctness
- future grapheme-aware diagnostics may be added separately
- future grapheme-aware diagnostics must not change the base offset unit without schema versioning

## 10. Text Hash Canonicalization Policy

Intended canonical policy:

- fields: `text_hash_before`, `text_hash_after`
- algorithm: SHA-256
- input encoding: UTF-8
- input text: stored string exactly as captured
- Unicode normalization: none
- newline normalization: none
- trailing newline: preserved as-is
- empty string: SHA-256 of zero-length UTF-8 byte sequence
- output format: lowercase hex
- no salt
- no JSON escaping layer before hashing
- hash is over text bytes, not event JSON
- TypeScript and Rust implementations must produce identical output

Current placeholder or incompatible hash behavior should be migrated explicitly in a future implementation step.

## 11. Hash-Related Fields

| field | required or optional | generation side | validation side | canonicalization policy | mismatch behavior | raw text in errors |
| --- | --- | --- | --- | --- | --- | --- |
| `text_hash_before` | Optional in current schema; should become required or conditionally required in a future versioned replay-critical schema. | TypeScript logger or trusted synthetic fixture generator. | Rust validation/replay. | SHA-256 over exact UTF-8 bytes of stored before string, lowercase hex. | Validation or replay failure. | Must not emit raw before text. |
| `text_hash_after` | Optional in current schema; should become required or conditionally required in a future versioned replay-critical schema. | TypeScript logger or trusted synthetic fixture generator. | Rust validation/replay. | SHA-256 over exact UTF-8 bytes of stored after string, lowercase hex. | Validation or replay failure. | Must not emit raw after text. |
| `text_hash` | Not clearly present in current audited schema; planned clarification target only if introduced. | Future schema-specific producer. | Future schema-specific validator. | Must use the same SHA-256 UTF-8 lowercase-hex policy unless versioned otherwise. | Validation failure on mismatch. | Must not emit raw text. |
| replay validation hash checks | Partially present today; canonical policy not implemented in this step. | N/A | Rust replay/validation. | Future checks should use canonical SHA-256 policy. | Fail closed on mismatch. | Metadata-only diagnostics. |
| safe summary hash reporting | Planned only if needed. | Rust or reporting layer. | Public-safe report consumer. | May report field names and mismatch counts, not text bodies. | N/A | Must not emit raw text or raw event payload body. |

## 12. Hash Mismatch Policy

Hash mismatch must be a validation failure or replay failure.

Policy:

- do not silently accept mismatch
- do not output raw learner text in error reports
- diagnostic output should be metadata-only
- mismatch report may include `event_id`, `seq`, hash field names, and `reason_code`
- mismatch report must not include raw before/after text
- mismatch report must not include raw event payload body

If `event_id` is unavailable in current schema, future diagnostics may use `seq` and session metadata until the event-id schema step is implemented.

## 13. Schema Versioning Recommendation

This clarification likely requires a future schema version bump.

Recommendation:

- do not claim current schema fully implements the clarified policy
- future implementation should introduce explicit schema version / target version note
- migration from placeholder or previous hash behavior must be explicit
- backward compatibility must be handled through explicit version checks or migration tooling
- validators should fail closed for unsupported schema versions
- current placeholder hash labels should not be treated as canonical SHA-256 values

## 14. Required Future Test Vectors

Shared TypeScript / Rust vectors should be designed before implementation.

Required synthetic cases:

- empty string
- ASCII
- Japanese
- full-width alphanumerics
- emoji / surrogate pair
- combining character such as e + combining acute
- precomposed accented character
- mixed Japanese + emoji
- CRLF multi-line
- LF multi-line
- trailing newline
- tab
- selection around emoji
- offset inside surrogate pair, expected validation error
- offset beyond UTF-16 length, expected validation error
- combining mark boundary behavior
- long mixed Unicode text

Each vector should include:

- `vector_id`
- `source_text_description`, not raw long text if unnecessary
- synthetic source text, if minimal and safe
- UTF-16 code unit length
- UTF-8 byte length
- selected UTF-16 offsets
- expected UTF-8 byte offsets or expected validation error
- expected SHA-256 lowercase hex
- no raw learner text
- no real participant data

This step does not hardcode final hash values. Final hash values should be generated and reviewed by a future implementation step.

## 15. Required Future Implementation Tasks

Future tasks, not implemented here:

- add or document `position_unit=utf16_code_unit`
- implement Rust UTF-16 to UTF-8 conversion helper
- add Rust tests for valid and invalid offsets
- implement TypeScript SHA-256 UTF-8 lowercase hex helper
- implement Rust SHA-256 UTF-8 lowercase hex helper
- replace placeholder or incompatible hash behavior
- add shared test vectors
- add replay hash verification tests
- add schema version checks
- add public-safe mismatch diagnostics
- update CI to run TypeScript / Rust cross-language vector checks

## 16. P0 / P1 Classification

P0 pre-collection blockers:

- explicit position unit policy
- Rust UTF-16 to UTF-8 safe conversion
- invalid offset fail-closed behavior
- SHA-256 hash canonicalization
- TypeScript / Rust shared test vectors
- hash mismatch fail-closed behavior
- public-safe diagnostics

P1 before pilot:

- broader Unicode vector expansion
- grapheme-aware diagnostics
- richer schema migration report
- extended CRLF / LF mixed tests

## 17. Relationship to Event Durability

This step does not implement event queue, IndexedDB, acknowledgement, retry, or deduplication.

Durability remains P0 but is staged after schema clarification. Event id, seq, ack, and retry should be handled in later steps. Schema clarification reduces ambiguity before durability implementation by fixing offset and hash interpretation.

Event ordering still depends on the client-seq authoritative policy from `docs/web_logger_durability_unicode_hash_safety_design.md` and the audit findings in `docs/web_logger_durability_unicode_hash_current_implementation_audit.md`.

## 18. Relationship to No-Oracle and Synthetic-Only Boundaries

This clarification does not relax no-oracle constraints, introduce real data, authorize real participant collection, or validate model performance.

It protects replay integrity before no-oracle audit by making replay-critical offsets and hash checks explicit. Public-safe summaries must remain metadata-only / count-only where possible.

## 19. Non-Claims

This clarification does not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- Unicode correctness implementation completion
- hash compatibility implementation completion
- event durability implementation completion
- all invalid offsets are currently rejected
- current TypeScript and Rust hash outputs are already aligned
- data collection readiness
- deployment readiness

## 20. Public-Safe Documentation Policy

Documentation and future reports must preserve:

- no raw learner text in docs
- no real participant data in docs
- no raw event payload bodies in docs
- no fixture JSON bodies copied into docs
- no private paths
- no absolute local paths
- no logits / probabilities
- no performance metric bodies
- examples must be synthetic and minimal
- hash examples must not reveal real text

## 21. Recommended Next Codex Step

Recommended next step:

Step-web-logger-003: shared synthetic Unicode and hash test vector design

Reason:

- after schema clarification, test vectors should be designed before implementation
- vectors will guide both Rust UTF-16 conversion helper and TypeScript/Rust SHA-256 helpers
- this still avoids large durability implementation until offset and hash semantics are testable

## 22. Step-web-logger-003 Test Vector Design Handoff

Step-web-logger-003 is recorded in `docs/web_logger_shared_unicode_hash_test_vector_design.md`.

The design defines future shared synthetic vector structure, required vector categories, initial vector set, offset expectation policy, hash expectation policy, invalid vector policy, cross-language validation design, future CI integration design, and review/generation procedure. It remains docs-only and does not create fixture JSON, tests, helper code, Makefile targets, release-quality labels, workflow changes, or event durability implementation.

## 23. Step-web-logger-004 Shared Vector Fixture Root

Step-web-logger-004 creates `tests/fixtures/web_logger_unicode_hash_vectors/README.md` and `tests/fixtures/web_logger_unicode_hash_vectors/vectors.json`.

The fixture root records the Step-web-logger-002 schema clarification as synthetic fixture data: UTF-16 code unit offsets, expected UTF-8 byte offsets, SHA-256 UTF-8 lowercase-hex hashes over decoded stored text, no Unicode normalization, no newline normalization, and invalid offset metadata. It does not implement the future Rust UTF-16 conversion helper, TypeScript hash helper, Rust hash helper, tests, CI, Makefile targets, or event durability implementation.

## 24. Step-web-logger-005 Validator Design Handoff

Step-web-logger-005 is recorded in `docs/web_logger_unicode_hash_vector_fixture_validator_design.md`.

The design translates the schema clarification and Step-web-logger-004 fixture root into a future validator contract. It remains docs-only and does not implement validation code, modify vectors, add tests, add Makefile targets, add release-quality checks, or implement TypeScript / Rust helpers.

## 25. Step-web-logger-006 Validator Implementation Handoff

Step-web-logger-006 adds a Python fixture validator for the shared Unicode/hash vector fixture root.

The validator checks the clarified UTF-16 code unit position policy, decoded-text SHA-256 hash policy, no-normalization policy, and invalid offset expectations at the fixture-data level. It does not implement the future Rust replay-critical conversion helper or TypeScript / Rust hash helpers.

## 26. Step-web-logger-007 Makefile Target Design Handoff

Step-web-logger-007 is recorded in `docs/web_logger_unicode_hash_vector_validator_makefile_target_design.md`.

It designs a future Makefile target for running the Step-web-logger-006 Python validator against `tests/fixtures/web_logger_unicode_hash_vectors/vectors.json`. The target remains future work; this docs-only handoff does not change Makefile, code, tests, fixture JSON, release-quality wrapper, CI workflow, or the clarified schema policy.

## 27. Step-web-logger-008 Makefile Target Implementation Handoff

Step-web-logger-008 adds `check-web-logger-unicode-hash-vector-fixtures` to Makefile.

The target runs the Python validator for the shared Unicode/hash vector fixture and checks the clarified fixture-level position/hash metadata, decoded-text SHA-256 values, UTF-16 lengths, UTF-8 lengths, offset mappings, and expected invalid offset records. It does not implement the future Rust replay-critical conversion helper, TypeScript hash helper, Rust hash helper, release-quality integration, CI integration, or event durability.

## 28. Step-web-logger-009 Release-Quality Integration Design Handoff

Step-web-logger-009 is recorded in `docs/web_logger_unicode_hash_vector_validator_release_quality_integration_design.md`.

It plans future wrapper integration for the Makefile-targeted vector validator. This handoff does not change the clarified schema policy, wrapper, Makefile, code, tests, fixture JSON, CI workflow, TypeScript/Rust helper work, or event durability.

## 29. Step-web-logger-010 Release-Quality Wrapper Integration

Step-web-logger-010 adds the Makefile-targeted vector validator to the release-quality wrapper.

The wrapper integration validates the shared fixture-level position/hash metadata through the Python validator. It does not implement the future Rust replay-critical conversion helper, TypeScript hash helper, Rust hash helper, CI workflow integration, or event durability.

## 30. Step-web-logger-011 Remote/Manual Run Record Workflow Design

Step-web-logger-011 adds [Web Logger Unicode and Hash Vector Validator Release Quality Remote/Manual Run Record Workflow](web_logger_unicode_hash_vector_validator_release_quality_remote_run_record_workflow.md). It defines future status-marker evidence and metadata handling for the release-quality-integrated vector validator without changing the clarified position/hash policy or implementing TypeScript/Rust helpers.

## 31. Step-web-logger-012 Remote Status Marker

Step-web-logger-012 adds [Web Logger Unicode and Hash Vector Validator Release Quality Remote Run Status](status/web_logger_unicode_hash_vector_validator_release_quality_remote_run_status.md). It records public-safe remote release-quality evidence for the Python fixture validator and does not change the clarified UTF-16 position unit or hash canonicalization policy.

## 32. Step-web-logger-013 Final Safety Review

Step-web-logger-013 adds [Web Logger Unicode and Hash Vector Validator Release Quality Chain Final Safety Review](web_logger_unicode_hash_vector_validator_release_quality_chain_final_safety_review.md). It accepts the Python fixture validator chain while keeping Rust UTF-16 conversion helper design and implementation as future work.

## 33. Step-web-logger-014 Rust UTF-16 Offset Conversion Helper Design

Step-web-logger-014 adds [Rust UTF-16 Offset Conversion Helper Design for Web Logger Events](web_logger_rust_utf16_offset_conversion_helper_design.md). It designs the future Rust helper for converting browser-originated UTF-16 code unit offsets into UTF-8 byte offsets without changing the clarified schema policy or implementing Rust code.

## 34. Step-web-logger-015 Rust UTF-16 Offset Conversion Helper

Step-web-logger-015 adds the focused Rust helper described by Step-web-logger-014 in `crates/kslog_replay/src/utf16_offsets.rs`, with tests in `crates/kslog_replay/tests/utf16_offsets.rs`.

The helper supports the clarified `position_unit=utf16_code_unit` policy at a focused utility level by converting browser-originated UTF-16 code unit offsets into UTF-8 byte offsets at valid Rust char boundaries. It fails closed for surrogate-pair internal offsets, offsets beyond UTF-16 length, and `start > end`, and it keeps diagnostics public-safe.

This does not change schema behavior, does not integrate the helper into broader replay/runtime paths, and does not implement Rust or TypeScript SHA-256 helpers, TypeScript/Rust cross-language vector checks, or event durability.

## 35. Step-web-logger-016 Rust Helper Makefile Target Design

Step-web-logger-016 adds [Rust UTF-16 Offset Conversion Helper Makefile Target Design](web_logger_rust_utf16_offset_conversion_helper_makefile_target_design.md).

It proposes a future focused Makefile target for running the Step-web-logger-015 Rust helper tests. It does not change Makefile, schema behavior, Rust code, tests, fixture JSON, release-quality wrapper, or event durability.

## 36. Step-web-logger-017 Rust Helper Makefile Target

Step-web-logger-017 adds `check-web-logger-rust-utf16-offset-conversion` to Makefile.

The target runs the focused Rust helper tests for the clarified UTF-16 code unit offset policy with `cargo test -p kslog_replay utf16`. It does not change schema behavior, Rust helper code, tests, fixture JSON, release-quality wrapper, TypeScript/Rust hash work, or event durability.

## 37. Step-web-logger-018 Rust Helper Release-Quality Integration Design

Step-web-logger-018 adds [Rust UTF-16 Offset Conversion Helper Release Quality Integration Design](web_logger_rust_utf16_offset_conversion_helper_release_quality_integration_design.md).

The design proposes future wrapper execution of the existing focused Rust helper target. It does not change schema behavior, Makefile, wrapper, Rust code, tests, fixture JSON, TypeScript/Rust hash work, broader runtime integration, or event durability.

## 38. Step-web-logger-019 Rust Helper Release-Quality Integration

Step-web-logger-019 adds `release_quality_check: web logger Rust UTF-16 offset conversion helper` to the release-quality wrapper.

The wrapper calls the existing Makefile target for focused Rust UTF-16 offset conversion tests. It does not change schema behavior, Makefile, Rust helper code, tests, fixture JSON, TypeScript/Rust hash work, broader runtime integration, or event durability.

## 39. Step-web-logger-020 Rust Helper Remote/Manual Run Record Workflow Design

Step-web-logger-020 adds [Rust UTF-16 Offset Conversion Helper Release Quality Remote/Manual Run Record Workflow](web_logger_rust_utf16_offset_conversion_helper_release_quality_remote_run_record_workflow.md).

The workflow design plans future public-safe status evidence for the wrapper check. It does not change schema behavior, Makefile, wrapper, Rust helper code, tests, fixture JSON, TypeScript/Rust hash work, broader runtime integration, or event durability.

## 40. Step-web-logger-021 Rust Helper Remote Status Marker

Step-web-logger-021 adds [Rust UTF-16 Offset Conversion Helper Release Quality Remote Run Status](status/web_logger_rust_utf16_offset_conversion_helper_release_quality_remote_run_status.md).

The marker records public-safe remote metadata for the focused Rust UTF-16 helper wrapper check. It does not change schema behavior, Makefile, wrapper, Rust helper code, tests, fixture JSON, TypeScript/Rust hash work, broader runtime integration, or event durability.

## 41. Step-web-logger-022 Rust Helper Final Safety Review

Step-web-logger-022 adds [Rust UTF-16 Offset Conversion Helper Release Quality Chain Final Safety Review](web_logger_rust_utf16_offset_conversion_helper_release_quality_chain_final_safety_review.md).

The review accepts the focused Rust helper chain within an explicit boundary. It does not change schema behavior, Makefile, wrapper, Rust helper code, tests, fixture JSON, TypeScript/Rust hash work, broader runtime integration, or event durability.

## 42. Step-web-logger-023 Broader Replay Integration Design

Step-web-logger-023 adds [Rust UTF-16 Offset Conversion Helper Broader Replay Integration Design](web_logger_rust_utf16_offset_conversion_helper_broader_replay_integration_design.md).

The design applies the clarified UTF-16 code unit policy to future replay-first integration planning. It does not change schema behavior, Makefile, wrapper, Rust helper code, tests, fixture JSON, TypeScript/Rust hash work, broader runtime implementation, or event durability.

## 43. Step-web-logger-024 Replay-Focused Integration

Step-web-logger-024 applies the UTF-16 code unit position policy inside `kslog_replay` only.

Replay now converts browser-originated cursor and selection offsets to UTF-8 byte ranges before string indexing / replacement and validates replay document lengths as UTF-16 code unit counts. Invalid surrogate-pair internal offsets, offsets beyond length, and `start > end` fail closed with public-safe reason_code behavior.

The schema still has no new explicit position_unit implementation in this step. Validate / extract / micro_episode integration, Rust SHA-256 helper work, TypeScript SHA-256 helper work, TypeScript/Rust checks, event durability, fixture JSON changes, Makefile changes, wrapper changes, and CI workflow changes remain future work.

## 44. Step-web-logger-025 Makefile Target Semantics Design

Step-web-logger-025 adds [Rust UTF-16 Replay Integration Makefile Target Design](web_logger_rust_utf16_replay_integration_makefile_target_design.md).

The design covers future Makefile-visible naming/help text for replay-focused UTF-16 coverage and does not change schema-level position_unit behavior. Validate / extract / micro_episode integration, Rust SHA-256 helper work, TypeScript SHA-256 helper work, TypeScript/Rust checks, event durability, fixture JSON changes, Makefile changes, wrapper changes, and CI workflow changes remain future work.

## 45. Step-web-logger-026 Makefile Help Text Alignment

Step-web-logger-026 updates the existing `check-web-logger-rust-utf16-offset-conversion` help text to `Run Rust UTF-16 offset conversion and replay integration tests`.

The target command remains `cargo test -p kslog_replay utf16`, and no new target is added. This aligns Makefile-visible wording with the existing `utf16` test filter after replay-focused integration. It does not change schema-level position_unit behavior, validate / extract / micro_episode integration, Rust SHA-256 helper work, TypeScript SHA-256 helper work, TypeScript/Rust checks, event durability, fixture JSON, wrapper behavior, or CI workflow.

## 46. Step-web-logger-027 Release-Quality Label Update Design

Step-web-logger-027 adds [Rust UTF-16 Replay Integration Release Quality Label Update Design](web_logger_rust_utf16_replay_integration_release_quality_label_update_design.md).

The design proposes future release-quality label wording for the existing Rust UTF-16 target. It does not change schema-level position_unit behavior, command behavior, validate / extract / micro_episode integration, TypeScript/Rust hash work, event durability, or replay-focused remote status.

## 47. Step-web-logger-028 Release-Quality Label Update

Step-web-logger-028 updates the Rust UTF-16 release-quality label wording while keeping the command and insertion point unchanged.

This label update reflects existing `kslog_replay` helper + replay-focused test coverage. It does not implement schema-level position_unit policy, validate / extract / micro_episode integration, TypeScript/Rust hash work, event durability, or replay-focused remote status.

## 48. Step-web-logger-029 Run Record Workflow Design

Step-web-logger-029 adds [Rust UTF-16 Replay Integration Release Quality Remote/Manual Run Record Workflow](web_logger_rust_utf16_replay_integration_release_quality_remote_run_record_workflow.md).

The workflow design plans public-safe status evidence for the updated Rust UTF-16 replay label. It does not change schema-level position_unit behavior, validate / extract / micro_episode integration, TypeScript/Rust hash work, event durability, wrapper behavior, Makefile, code, tests, fixture JSON, or CI workflow.

## 49. Step-web-logger-032 Schema-Level Position Unit Policy Design

Step-web-logger-032 adds [Schema-Level Position Unit Policy Design for Web Logger Events](web_logger_schema_position_unit_policy_design.md).

The design recommends a future explicit `position_unit=utf16_code_unit` field policy for Web logger schema / validation boundaries. It does not change current schema behavior, validation behavior, replay behavior, fixtures, Makefile targets, wrapper checks, TypeScript/Rust hash work, event durability, production readiness, real-data readiness, or model performance evidence.

## 50. Step-web-logger-033 Schema-Level Position Unit Fixture Design

Step-web-logger-033 adds [Schema-Level Position Unit Fixture Design for Web Logger Events](web_logger_schema_position_unit_fixture_design.md).

The design recommends a future dedicated fixture root and valid / invalid / legacy case matrix for explicit `position_unit=utf16_code_unit` schema / validation policy. It does not create fixtures, modify existing fixture JSON, change current schema behavior, change validation behavior, change replay behavior, alter TypeScript/Rust hash work, or alter event durability.

## 51. Step-web-logger-034 Schema-Level Position Unit Fixtures

Step-web-logger-034 adds `tests/fixtures/web_logger_position_unit_schema/`
with README guidance, `case_index.json`, and 17 synthetic JSONL cases for
future Web logger `position_unit=utf16_code_unit` schema / validator policy.

The fixture root separates valid, invalid, and legacy cases and records
public-safe expected reason codes. It does not change current schema behavior,
validation behavior, replay behavior, Makefile targets, release-quality
wrapper checks, TypeScript/Rust hash work, event durability, production
readiness, real-data readiness, or model performance evidence.

## 52. Step-web-logger-035 Schema-Level Position Unit Fixture Validator Design

Step-web-logger-035 adds
[Schema-Level Position Unit Fixture Validator Design](web_logger_schema_position_unit_fixture_validator_design.md).

The design recommends a future Python-first validator for the Step-web-logger-034
fixture root. It fixes planned CLI behavior, public-safe summary output,
reason-code coverage, UTF-16 metadata checks, and failure semantics. It does
not change schema behavior, validation behavior, replay behavior, fixture
content, Makefile targets, release-quality checks, TypeScript/Rust hash work,
event durability, production readiness, real-data readiness, or model
performance evidence.

## 53. Step-web-logger-036 Schema-Level Position Unit Fixture Validator

Step-web-logger-036 adds `python/web_logger_position_unit_fixture_validation.py`
and focused tests for the Step-web-logger-034 fixture root.

The validator verifies fixture contract metadata, JSONL structure, expected
reason-code counts, and bounded UTF-16 position metadata with public-safe
summary output. It does not change schema behavior, validation behavior,
replay behavior, Makefile targets, release-quality checks, TypeScript/Rust hash
work, event durability, production readiness, real-data readiness, or model
performance evidence.

## 54. Step-web-logger-037 Schema-Level Position Unit Fixture Validator Makefile Target Design

Step-web-logger-037 adds
[Schema-Level Position Unit Fixture Validator Makefile Target Design](web_logger_schema_position_unit_fixture_validator_makefile_target_design.md).

The design recommends future target `check-web-logger-position-unit-fixtures`
to run the summary-only Python fixture contract validator. It does not change
schema behavior, validation behavior, replay behavior, Makefile targets in this
step, release-quality checks, TypeScript/Rust hash work, event durability,
production readiness, real-data readiness, or model performance evidence.

## 55. Step-web-logger-038 Schema-Level Position Unit Fixture Validator Makefile Target

Step-web-logger-038 adds Makefile target
`check-web-logger-position-unit-fixtures`.

The target runs the summary-only Python fixture contract validator for
`tests/fixtures/web_logger_position_unit_schema/`. It does not change
`scripts/check_release_quality.sh`, schema behavior, validation behavior,
replay behavior, TypeScript/Rust hash work, event durability, production
readiness, real-data readiness, or model performance evidence.

## 56. Step-web-logger-039 Schema-Level Position Unit Fixture Validator Release-Quality Integration Design

Step-web-logger-039 adds
[Schema-Level Position Unit Fixture Validator Release Quality Integration Design](web_logger_schema_position_unit_fixture_validator_release_quality_integration_design.md).

The design recommends future release-quality label
`release_quality_check: web logger position_unit fixture contract validation`
and command `make check-web-logger-position-unit-fixtures`. It does not change
`scripts/check_release_quality.sh`, Makefile, schema behavior, validation
behavior, replay behavior, TypeScript/Rust hash work, event durability,
production readiness, real-data readiness, or model performance evidence.

## 57. Step-web-logger-040 Schema-Level Position Unit Fixture Validator Release-Quality Integration

Step-web-logger-040 adds release-quality wrapper check
`release_quality_check: web logger position_unit fixture contract validation`.

The wrapper command is `make check-web-logger-position-unit-fixtures`, inserted
after Unicode/hash fixture validation and before Rust UTF-16 replay
integration. It does not change Makefile, schema behavior, validation
behavior, replay behavior, TypeScript/Rust hash work, status markers, final
safety review, event durability, production readiness, real-data readiness, or
model performance evidence.

## 58. Step-web-logger-041 Schema-Level Position Unit Fixture Validator Release-Quality Run Record Workflow Design

Step-web-logger-041 adds
[Schema-Level Position Unit Fixture Validator Release Quality Remote/Manual Run Record Workflow](web_logger_schema_position_unit_fixture_validator_release_quality_remote_run_record_workflow.md).

The workflow design defines future public-safe status-marker metadata for the
Step-web-logger-040 wrapper integration. It does not change Makefile,
`scripts/check_release_quality.sh`, schema behavior, validation behavior,
replay behavior, TypeScript/Rust hash work, status markers, final safety
review, event durability, production readiness, real-data readiness, or model
performance evidence.

## 59. Step-web-logger-042 Schema-Level Position Unit Fixture Validator Release-Quality Remote Status Marker

Step-web-logger-042 adds
[Schema-Level Position Unit Fixture Validator Release Quality Remote Run Status](status/web_logger_schema_position_unit_fixture_validator_release_quality_remote_run_status.md).

The marker records public-safe remote metadata for the Step-web-logger-040
fixture contract validation wrapper integration. It does not change Makefile,
`scripts/check_release_quality.sh`, schema behavior, validation behavior,
replay behavior, TypeScript/Rust hash work, final safety review, event
durability, production readiness, real-data readiness, or model performance
evidence.

## 60. Step-web-logger-043 Schema-Level Position Unit Fixture Validator Release-Quality Final Safety Review

Step-web-logger-043 adds
[Schema-Level Position Unit Fixture Validator Release Quality Chain Final Safety Review](web_logger_schema_position_unit_fixture_validator_release_quality_chain_final_safety_review.md).

The review accepts only bounded fixture-contract validation for the fixed
17-case synthetic matrix. It does not change Makefile,
`scripts/check_release_quality.sh`, schema behavior, validation behavior,
replay behavior, TypeScript/Rust hash work, event durability, production
readiness, real-data readiness, or model performance evidence.

## 61. Step-web-logger-044 Rust Schema-Level Position Unit Policy Implementation Design

Step-web-logger-044 adds
[Rust Schema-Level Position Unit Policy Implementation Design](web_logger_rust_schema_position_unit_policy_implementation_design.md).

The design plans future `kslog_schema` / `kslog_validate` handling for
explicit `position_unit=utf16_code_unit`, version gating, unsupported and
missing values, and validator reason-code staging. It does not change current
schema behavior, validation behavior, replay behavior, TypeScript/Rust hash
work, event durability, production readiness, real-data readiness, or model
performance evidence.

## 62. Step-web-logger-045 Rust Schema Position Unit Boundary

Step-web-logger-045 adds the bounded `kslog_schema` parser/accessor layer for
`position_unit`. `RawEvent` now accepts optional raw `position_unit` and
optional `research_schema_target`, and the schema crate classifies supported
`utf16_code_unit`, missing values, unsupported values, schema mismatch, and
unknown schema version without printing event bodies or raw text fields.

This does not implement Rust validator policy enforcement, UTF-16 numeric
metadata checks, validate / extract / micro_episode integration, TypeScript
logger behavior, Rust or TypeScript SHA-256 helpers, TypeScript/Rust vector
checks, event durability, production readiness, real-data readiness, or model
performance evidence.

## 63. Step-web-logger-046 Rust Validator Mapping Design

Step-web-logger-046 adds
[Rust Validator Position Unit Policy Test and Fixture Mapping Design](web_logger_rust_validator_position_unit_policy_test_fixture_mapping_design.md).

The design separates future validator Phase 1 position_unit presence / value /
schema-version enforcement from Phase 2 UTF-16 numeric metadata validation.
It does not implement validator behavior, TypeScript logger changes, Rust or
TypeScript SHA-256 helpers, TypeScript/Rust vector checks, event durability,
production readiness, real-data readiness, or model performance evidence.

## 64. Step-web-logger-047 Rust Validator Phase 1 Position Unit Enforcement

Step-web-logger-047 adds bounded `kslog_validate` enforcement for the
schema-level position-unit Phase 1 boundary. The validator now checks
fixture-targeted Web logger v0.2-style records for explicit
`position_unit=utf16_code_unit`, fails missing / unsupported /
schema-mismatch / unknown-version cases with stable body-free reason codes,
and preserves legacy synthetic fixture compatibility outside that target.

This does not implement Phase 2 UTF-16 numeric metadata validation, extract /
micro_episode integration, TypeScript logger changes, Rust or TypeScript
SHA-256 helpers, TypeScript/Rust vector checks, fixture JSON changes, Makefile
or wrapper changes, event durability, production readiness, real-data
readiness, or model performance evidence.

## 65. Step-web-logger-048 Rust Validator Phase 1 Makefile Target Design

Step-web-logger-048 adds
[Rust Validator Position Unit Phase 1 Makefile Target Design](web_logger_rust_validator_position_unit_phase1_makefile_target_design.md).

The design recommends future target
`check-web-logger-rust-validator-position-unit-phase1` for running
`cargo test -p kslog_validate position_unit`. Step059 later corrects the
implemented target command to `cargo test -p kslog_validate position_unit_phase1`.
The Step048 design remains docs-only and does not change Makefile, wrapper,
Rust code, tests, fixtures, TypeScript, Python, Phase 2 UTF-16 numeric
validation, hash compatibility, event durability, production readiness,
real-data readiness, or model performance evidence.

## 66. Step-web-logger-049 Rust Validator Phase 1 Makefile Target

Step-web-logger-049 adds Makefile target
`check-web-logger-rust-validator-position-unit-phase1` with help text
`Run Rust validator position_unit Phase 1 policy tests`. The command is
`cargo test -p kslog_validate position_unit_phase1` after the Step059 filter
correction.

This exposes focused Rust validator Phase 1 coverage only. It does not add
release-quality integration, Phase 2 UTF-16 numeric validation, hash
compatibility implementation, TypeScript/Rust vector checks, event durability,
production readiness, real-data readiness, or model performance evidence.

## 67. Step-web-logger-050 Rust Validator Phase 1 Release-Quality Integration Design

Step-web-logger-050 adds design-only release-quality integration planning for
the Step049 target. The future wrapper check should call
`make check-web-logger-rust-validator-position-unit-phase1` and keep hash /
position-unit boundaries distinct.

This design does not implement SHA-256 helpers, TypeScript/Rust hash vector
checks, Phase 2 UTF-16 numeric validation, TypeScript logger compatibility,
event durability, production readiness, real-data readiness, or model
performance evidence.

## 68. Step-web-logger-051 Rust Validator Phase 1 Release-Quality Integration

Step-web-logger-051 adds release-quality wrapper integration for the Rust
validator Phase 1 target. The wrapper calls
`make check-web-logger-rust-validator-position-unit-phase1`.

This keeps position-unit policy and hash compatibility boundaries distinct.
It does not implement SHA-256 helpers, TypeScript/Rust hash vector checks,
Phase 2 UTF-16 numeric validation, TypeScript logger compatibility, event
durability, production readiness, real-data readiness, or model performance
evidence.

## 69. Step-web-logger-052 Rust Validator Phase 1 Run Record Workflow Design

Step-web-logger-052 designs future status marker evidence for the Rust
validator Phase 1 release-quality check. The status marker should keep
position-unit policy evidence and hash compatibility evidence distinct.

This design does not implement SHA-256 helpers, TypeScript/Rust hash vector
checks, Phase 2 UTF-16 numeric validation, TypeScript logger compatibility,
event durability, production readiness, real-data readiness, or model
performance evidence.

## 70. Step-web-logger-053 Rust Validator Phase 1 Remote Status Marker

Step-web-logger-053 created
[Rust validator position_unit Phase 1 release-quality remote run status](status/web_logger_rust_validator_position_unit_phase1_release_quality_remote_run_status.md).
The marker records position-unit validator Phase 1 evidence only and keeps it
separate from hash compatibility work.

It does not implement SHA-256 helpers, TypeScript/Rust hash vector checks,
Phase 2 UTF-16 numeric validation, TypeScript logger compatibility, event
durability, production readiness, real-data readiness, or model performance
evidence.

## 71. Step-web-logger-054 Rust Validator Phase 1 Final Safety Review

Step-web-logger-054 created
[Rust validator position_unit Phase 1 release-quality chain final safety review](web_logger_rust_validator_position_unit_phase1_release_quality_chain_final_safety_review.md).
The accepted boundary remains position-unit Phase 1 validation only and stays
separate from hash compatibility.

It does not implement SHA-256 helpers, TypeScript/Rust hash vector checks,
Phase 2 UTF-16 numeric validation, TypeScript logger compatibility, event
durability, production readiness, real-data readiness, or model performance
evidence.

## 72. Step-web-logger-055 Phase 2 UTF-16 Numeric Metadata Design

Step-web-logger-055 created
[Rust validator Phase 2 UTF-16 numeric metadata validation design](web_logger_rust_validator_phase2_utf16_numeric_metadata_validation_design.md).
The design keeps position-unit numeric validation separate from hash
compatibility and recommends shared UTF-16 helper extraction before Phase 2
validator implementation.

It does not implement SHA-256 helpers, TypeScript/Rust hash vector checks,
Phase 2 validation, TypeScript logger compatibility, event durability,
production readiness, real-data readiness, or model performance evidence.

## 73. Step-web-logger-056 Shared UTF-16 Helper Update

Step-web-logger-056 extracts reusable UTF-16 code unit length and offset/range
conversion into `kslog_schema::utf16_offsets`. `kslog_replay::utf16_offsets`
remains as a compatibility re-export of the shared helper so replay behavior
and existing helper paths remain stable.

This update is helper infrastructure only: `kslog_validate` Phase 2 numeric
metadata enforcement, TypeScript logger changes, SHA-256 helpers,
TypeScript/Rust vector checks, event durability, production readiness,
real-data readiness, and model performance evidence remain unimplemented.

## 74. Step-web-logger-057 Validator Phase 2 Follow-Up

Step-web-logger-057 adds bounded `kslog_validate` enforcement for UTF-16
numeric metadata after Phase 1 accepts `position_unit=utf16_code_unit` Web
logger v0.2-style events. The validator uses `kslog_schema::utf16_offsets` for
doc length and offset/range boundaries and keeps hash canonicalization as a
separate future chain.

Detectable byte-index misuse is handled only when the supplied metadata
contradicts UTF-16 length or scalar boundaries. This follow-up does not add
TypeScript logger changes, Rust or TypeScript SHA-256 helpers, TypeScript/Rust
vector checks, event durability, production readiness, real-data readiness, or
model performance evidence.

## 75. Step-web-logger-058 Makefile Target Design Follow-Up

Step-web-logger-058 designs future Makefile exposure for the Rust validator
Phase 2 UTF-16 numeric metadata checks. It recommends a separate Phase 2 target
and a Phase 1 target filter correction so Phase 1 and Phase 2 checks remain
distinct.

This remains separate from SHA-256 hash compatibility, TypeScript logger
emission, TypeScript/Rust vector checks, event durability, production
readiness, real-data readiness, and model performance evidence.

## 76. Step-web-logger-059 Makefile Target Follow-Up

Step-web-logger-059 adds Makefile exposure for Phase 2 UTF-16 numeric metadata
focused tests and corrects the Phase 1 target to use the Phase 1-only filter.
This keeps position-unit validation evidence separate from SHA-256 hash
compatibility and TypeScript/Rust vector checks.

The Phase 2 target is not yet release-quality-integrated and does not prove
TypeScript logger compatibility, event durability, production readiness,
real-data readiness, or model performance.
