# Web Logger Durability, Unicode Position, and Text Hash Safety Design

## 1. Title

Web Logger Durability, Unicode Position, and Text Hash Safety Design

## 2. Scope

This document is design-only / docs-only. It fixes a pre-implementation safety design and audit plan for three Web logger risks:

- event durability under network and browser lifecycle failures
- TypeScript / Rust character position unit consistency
- TypeScript / Rust text hash canonicalization consistency

This document does not implement the design. It makes no TypeScript code changes, Rust code changes, Python code changes, fixture JSON changes, CI workflow changes, schema implementation changes, runtime implementation changes, or validator implementation changes.

This document is not production readiness proof, real-data readiness proof, model performance proof, or data collection authorization.

## 3. Why This Is A Pre-Collection Blocker

The Web logger is upstream of the whole keystroke-level processing chain. Event integrity affects text replay. Text replay affects revision_event extraction. Revision_event extraction affects micro_episode generation. Micro_episode quality affects candidate generation, OT-inspired scoring, and no-oracle audit.

If the logger loses events, duplicates events, reorders events, stores partial JSONL, misinterprets Unicode offsets, or produces text hashes differently from Rust replay, later stages can appear to fail when the data are wrong, or appear to pass when validation is too weak.

Therefore event durability, position units, and hash rules must be fixed before real data collection is considered.

## 4. Current Risk Model

Risks to address before collection:

- event loss during transient network failure
- event duplication caused by retry
- event reordering caused by request arrival order
- partial JSONL write on the server
- unflushed events on tab close or browser shutdown
- replay mismatch from missing or reordered events
- UTF-16 / UTF-8 index mismatch between browser and Rust
- invalid Unicode boundary in selection or edit span offsets
- inconsistent hash generation across TypeScript and Rust
- silent correction of invalid offsets
- downstream no-oracle audit contamination
- false reconstruction failure from harmless transport artifacts
- false reconstruction success due to weak validation

The high-level safe failure rule is fail closed: do not silently repair, reorder by arrival, or normalize text in a way that changes the stored evidence without an explicit schema version and validation path.

## 5. Event Durability Design

The Web logger should use a client-side event queue. Each event should be written to durable temporary browser storage, preferably IndexedDB, before network transmission is attempted. In-memory state can speed up the UI, but it must not be the only pending-event store.

Each event should include:

- `event_id`: unique id for deduplication
- `session_id`: stable id for a writing session
- `seq`: monotonic client sequence number within the session
- client-created timestamp as diagnostic metadata

The client should send events in batches. The server should acknowledge accepted events, including a last accepted sequence summary and any rejected or duplicate event identifiers. The client should retain unacknowledged events in IndexedDB and retry with backoff.

Durability design requirements:

- client event queue
- durable temporary storage using IndexedDB
- event_id for deduplication
- session_id for session grouping
- seq for authoritative session order
- monotonic client sequence
- batch send
- ack protocol
- retry with backoff
- deduplication by event_id
- server-side last accepted seq summary
- client/server seq reconciliation
- flush on `pagehide`, `visibilitychange`, and `beforeunload` where possible
- explicit acknowledgement that `navigator.sendBeacon` is best effort and size/lifecycle constrained
- idempotent server writes
- server reconstruction by client seq, not arrival order
- detection of seq_gap
- detection of duplicate event_id
- detection of duplicate seq
- detection of out-of-order arrival
- detection of partial JSONL writes
- safe failure behavior

Server append safety should avoid treating a partially written JSONL line as a valid event. The server should use atomic append or a write-ahead/staging strategy where possible, validate line completeness, and mark truncated or malformed lines as ingestion errors rather than replayable events.

## 6. Event Ordering Policy

Authoritative order is the client-assigned `seq` within a `session_id`.

Arrival order is never authoritative. `event_id` is for deduplication. `seq` is for order. Timestamp is diagnostic only and must not be the primary ordering key.

The server should reject or mark suspicious events with inconsistent `session_id`, `seq`, or `event_id`. Replay should operate only on seq-sorted, validated events after duplicate and gap checks.

Inconsistency handling:

- duplicate `event_id` with identical payload: idempotent duplicate
- duplicate `event_id` with conflicting payload: fail closed / suspicious
- duplicate `seq` with same event: idempotent duplicate if event_id and payload align
- duplicate `seq` with different event_id: fail closed / suspicious
- seq gap: fail closed or mark session incomplete before replay
- out-of-order arrival: allowed as transport artifact, but replay order remains seq order

## 7. UTF-16 Code Unit Position Policy

Browser-originated `selection_start`, `selection_end`, `cursor_pos`, and edit span offsets are UTF-16 code unit offsets.

The event schema should explicitly declare:

```text
position_unit=utf16_code_unit
```

Rust must not treat these values as UTF-8 byte offsets. Rust must convert UTF-16 code unit offsets to UTF-8 byte indices using a shared validated helper.

Position policy:

- invalid offsets are validation errors
- do not silently repair offsets
- do not normalize Unicode before applying offsets unless a future schema version explicitly specifies that behavior
- newline handling must be fixed
- tab handling must be fixed
- surrogate pairs and combining marks must be covered by tests
- grapheme cluster display length is not the stored index unit

The helper should accept a stored string and a UTF-16 code unit offset, then return a valid UTF-8 byte index only when the offset lands on a valid scalar boundary in the stored string. Out-of-range positions, surrogate inconsistencies, and offsets that cannot map safely must fail validation.

## 8. Unicode Normalization And Newline Policy

Recommended policy:

- preserve text exactly as captured
- no Unicode normalization by default
- no newline normalization by default
- CRLF / LF / CR are preserved unless a future schema version explicitly changes this
- hash and offset interpretation use the same stored string
- tab is preserved as U+0009 and is one UTF-16 code unit
- combining marks are preserved as captured
- grapheme cluster display length is not used as the storage index unit
- any future normalization requires an explicit schema version bump

This policy avoids hidden transformations between TypeScript capture, server storage, Rust validation, Rust replay, and hash verification.

## 9. Hash Canonicalization Policy

Recommended policy for `text_hash_before` and `text_hash_after`:

- algorithm=SHA-256
- input encoding=UTF-8
- text source=stored string exactly as captured
- Unicode normalization=none
- newline normalization=none
- trailing newline=preserve as-is
- empty string=SHA-256 of zero-length UTF-8 byte sequence
- output=lowercase hex
- no salt
- no JSON escaping layer before hashing
- hash is over text bytes, not event JSON
- TypeScript and Rust must share test vectors

Hash verification must use the exact stored string that offset interpretation and replay use. If TypeScript and Rust disagree on the hash for a shared vector, collection must not proceed.

## 10. Required Schema Changes Or Schema Clarification

Schema-level fields and metadata should be clarified before implementation.

Event fields:

- `event_id`
- `session_id`
- `seq`
- `client_created_at`
- `position_unit`
- `selection_start`
- `selection_end`
- `cursor_pos`
- edit span offsets, where applicable
- `text_hash_before`
- `text_hash_after`
- `hash_algorithm`
- `hash_encoding`
- `hash_normalization`
- `hash_output_format`

Optional client/batch fields:

- `client_flush_attempt_id`
- `batch_id`
- `retry_count`

Optional server response metadata:

- `acked_seq`
- accepted event_id list or compact equivalent
- rejected event_id list or compact equivalent
- duplicate event_id diagnostics

Optional server diagnostic fields:

- `duplicate_of_event_id`
- `server_received_at`
- `arrival_index`

Diagnostics are not authoritative ordering keys. `server_received_at` and `arrival_index` can help audit transport behavior, but replay must use validated client `seq`.

## 11. TypeScript / Rust Shared Test Vectors

Future shared test vectors should cover these groups:

- empty string
- ASCII
- Japanese
- full-width alphanumerics
- emoji / surrogate pair
- combining character such as a base letter plus combining acute
- precomposed accented character
- mixed Japanese + emoji
- CRLF multi-line
- LF multi-line
- trailing newline
- tab
- selection around emoji
- selection inside invalid surrogate boundary, if representable in a fixture, should fail
- combining mark boundary behavior
- long text with mixed Unicode

Each vector should define:

- source text
- UTF-16 length
- UTF-8 byte length
- selected UTF-16 offsets
- expected UTF-8 byte offsets or expected validation error
- expected SHA-256 lowercase hex

Do not hardcode hash values in this design document. Hash values should be generated by a reviewed script in a later implementation step and then reviewed as part of the shared test vector artifact.

All vector source text must be synthetic and minimal. No real participant text should be used.

## 12. Failure Injection Tests To Design

Future failure injection tests should cover:

- offline then reconnect
- dropped batch
- duplicated batch
- out-of-order batch arrival
- retry after ack timeout
- tab close with pending queue
- partial server write simulation
- duplicate event_id
- duplicate seq
- seq gap
- conflicting same seq with different event_id
- conflicting same event_id with different payload
- malformed JSONL line
- truncated JSONL line
- server restart between batch writes

Expected safe outcomes should include no silent loss, no arrival-order replay, duplicate detection, gap detection, idempotent accepted duplicate handling, suspicious conflict reporting, and no raw learner text in public-safe output.

## 13. Integration Tests To Design

Future TypeScript / Rust integration tests should verify:

- TypeScript emits synthetic events with UTF-16 offsets and canonical hashes
- Rust validates schema
- Rust converts UTF-16 offsets safely
- Rust replays text using validated seq order
- Rust verifies `text_hash_before` and `text_hash_after`
- Rust rejects invalid offsets
- Rust rejects hash mismatch
- Rust detects seq gaps and duplicates
- no-oracle forbidden fields remain absent
- public-safe reports suppress content

The integration path should use synthetic fixtures only and should not expose raw event payload bodies in public docs or summaries.

## 14. Acceptance Criteria Before Real Collection

Go only if:

- event queue design is implemented and tested
- IndexedDB persistence is tested
- batch ack / retry is tested
- event_id deduplication is tested
- seq reconciliation is tested
- unload / pagehide flush is tested as best effort
- server-side seq ordering is tested
- UTF-16 offset schema is fixed
- Rust UTF-16 to UTF-8 conversion is tested
- invalid Unicode offsets fail closed
- hash canonicalization is fixed
- TypeScript / Rust hash vectors match
- fault injection tests pass
- no raw learner text appears in public-safe summaries
- production readiness is not claimed solely from synthetic tests

No-Go if:

- event loss occurs under common retry scenarios
- hash mismatch occurs across TypeScript / Rust
- Unicode offset mismatch occurs
- replay silently repairs invalid offsets
- server relies on arrival order
- duplicate events are not deduplicated
- partial writes cannot be detected
- reports expose raw learner text

These gates are pre-collection gates. Passing synthetic gates is still not real-data readiness proof.

## 15. Implementation Staging Proposal

Do not implement in this step. Recommended future stages:

- Stage A: schema clarification docs and test vector design
- Stage B: hash canonicalization helper and shared test vectors
- Stage C: Rust UTF-16 offset conversion helper and tests
- Stage D: TypeScript logger event_id / queue / IndexedDB design
- Stage E: server ack / dedup / seq reconciliation design
- Stage F: failure injection test implementation
- Stage G: end-to-end synthetic logger-to-replay validation
- Stage H: final pre-collection safety review

Each stage should keep public-safe reporting and no-oracle constraints explicit.

## 16. Relationship To Existing No-Oracle And Synthetic-Only Boundaries

This design protects input integrity before no-oracle audit. It does not relax no-oracle constraints. It does not authorize real participant collection. It does not add real data. It does not claim model performance.

The design complements existing synthetic-only pipeline validation by adding a pre-collection integrity layer for logger durability, offset interpretation, and hash compatibility.

## 17. Non-Claims

- production readiness is not claimed.
- real-data readiness is not claimed.
- model performance is not claimed.
- F1 / accuracy / ECE / AURCC achievement is not claimed.
- perfect event delivery is not claimed.
- recoverability for all browser shutdown cases is not claimed.
- Unicode correctness implementation completion is not claimed.
- hash compatibility implementation completion is not claimed.
- no data loss in all environments is not claimed.
- deployment readiness is not claimed.

## 18. Public-Safe Documentation Policy

Documentation and future reports should follow these rules:

- no raw learner text in docs
- no real participant data in docs
- no raw event payload bodies in docs
- no fixture JSON bodies copied into docs
- no private paths
- no absolute local paths
- test vectors should be synthetic and minimal
- summaries should be metadata-only / count-only when possible

## 19. Recommended Next Codex Step

Recommended next step:

Step-web-logger-001: Web logger durability / Unicode / hash current implementation audit

Purpose:

- inspect current TypeScript logger, Rust replay/validation, schemas, docs, and tests
- identify exact files requiring future changes
- produce an implementation checklist
- make no code changes yet

## 20. Step-web-logger-001 Audit Handoff

Step-web-logger-001 is recorded in `docs/web_logger_durability_unicode_hash_current_implementation_audit.md`.

The audit remains audit-only / docs-only. It inventories current TypeScript logger, Rust schema/validation/replay, docs, and tests against this design without changing TypeScript, Rust, Python, tests, fixture JSON, Makefile, release-quality wrapper, workflow, package files, Cargo files, schema implementation, runtime implementation, or validator implementation.

## 21. Step-web-logger-002 Position Unit and Hash Schema Clarification

Step-web-logger-002 is recorded in `docs/web_logger_position_unit_and_hash_schema_clarification.md`.

The clarification fixes intended schema policy for `position_unit=utf16_code_unit`, replay-critical offset conversion expectations, Unicode/newline preservation, and `text_hash_before` / `text_hash_after` SHA-256 UTF-8 lowercase-hex canonicalization. It remains schema-clarification / docs-only and does not implement TypeScript, Rust, Python, tests, fixture JSON, CI, Makefile, release-quality wrapper, schema implementation, runtime implementation, or validator implementation changes.

## 22. Step-web-logger-003 Shared Unicode and Hash Test Vector Design

Step-web-logger-003 is recorded in `docs/web_logger_shared_unicode_hash_test_vector_design.md`.

The design plans a future shared synthetic vector fixture root for Unicode, UTF-16 offset, UTF-8 byte index, and SHA-256 hash checks. It does not create fixture files, compute final hash values, implement helpers, add tests, add CI, change Makefile, change release-quality wrapper, or implement event durability.

## 23. Step-web-logger-004 Shared Unicode and Hash Vector Fixtures

Step-web-logger-004 creates `tests/fixtures/web_logger_unicode_hash_vectors/README.md` and `tests/fixtures/web_logger_unicode_hash_vectors/vectors.json`.

The fixture root provides synthetic-only vector data for future TypeScript / Rust validation of UTF-16 code unit offsets, UTF-8 byte offset expectations, SHA-256 UTF-8 lowercase-hex hash expectations, invalid surrogate-boundary failures, and out-of-range offset failures. It remains fixture-data only and does not implement helper code, tests, CI, Makefile targets, release-quality checks, schema changes, runtime changes, validator changes, or event durability.

## 24. Step-web-logger-005 Shared Vector Fixture Validator Design

Step-web-logger-005 is recorded in `docs/web_logger_unicode_hash_vector_fixture_validator_design.md`.

The design specifies a future validator for the Step-web-logger-004 fixture root. It covers structure checks, metadata policy checks, hash validation, UTF-16 / UTF-8 length validation, offset mapping validation, expected failure handling, public-safe diagnostics, future tests, and later Makefile / release-quality staging. It does not implement event durability or any validator/runtime/helper code.

## 25. Step-web-logger-006 Shared Vector Fixture Validator Implementation

Step-web-logger-006 adds a Python validator and focused tests for `tests/fixtures/web_logger_unicode_hash_vectors/vectors.json`.

The validator is limited to fixture-data validation and public-safe summary output. It does not implement Web logger durability, TypeScript helper code, Rust helper code, replay/runtime changes, Makefile targets, release-quality checks, or CI workflow changes.

## 26. Step-web-logger-007 Shared Vector Validator Makefile Target Design

Step-web-logger-007 is recorded in `docs/web_logger_unicode_hash_vector_validator_makefile_target_design.md`.

It designs the future standalone target `check-web-logger-unicode-hash-vector-fixtures` for the Step-web-logger-006 validator. The design covers help text, command, Makefile placement, expected metadata/count-only output, failure semantics, public-safe diagnostics, and later release-quality staging. It remains docs-only and does not change Makefile, release-quality wrapper, CI workflow, code, tests, fixture JSON, TypeScript/Rust helpers, or event durability.

## 27. Step-web-logger-008 Shared Vector Validator Makefile Target

Step-web-logger-008 adds `check-web-logger-unicode-hash-vector-fixtures` to Makefile.

The target invokes the Step-web-logger-006 Python validator for the shared synthetic Unicode/hash vector fixture and emits public-safe summary-only output. It validates fixture metadata, SHA-256 hashes, UTF-16 lengths, UTF-8 lengths, offset mappings, and expected invalid offset records. It does not add release-quality integration, CI workflow integration, TypeScript/Rust helpers, fixture JSON changes, schema/runtime changes, or event durability.

## 28. Step-web-logger-009 Shared Vector Validator Release-Quality Integration Design

Step-web-logger-009 is recorded in `docs/web_logger_unicode_hash_vector_validator_release_quality_integration_design.md`.

It designs future release-quality integration for the Step-web-logger-008 Makefile target. It records the proposed wrapper label, command, insertion point, output expectations, failure semantics, Step-web-logger-010 preconditions, and public-safe boundaries. It does not change the wrapper, Makefile, code, tests, fixture JSON, CI workflow, TypeScript/Rust helpers, or event durability.

## 29. Step-web-logger-010 Shared Vector Validator Release-Quality Integration

Step-web-logger-010 adds `release_quality_check: web logger unicode hash vector fixture validation` to `scripts/check_release_quality.sh`.

The wrapper calls `make check-web-logger-unicode-hash-vector-fixtures` and records the shared Unicode/hash vector fixture validation as part of local release-quality checks. It remains public-safe summary-only and does not add CI workflow integration, TypeScript/Rust helpers, fixture JSON changes, schema/runtime changes, or event durability.

## 30. Step-web-logger-011 Shared Vector Validator Remote/Manual Run Record Workflow Design

Step-web-logger-011 is recorded in `docs/web_logger_unicode_hash_vector_validator_release_quality_remote_run_record_workflow.md`.

It designs future public-safe status marker evidence handling for the release-quality-integrated vector validator. It defines remote/manual evidence hierarchy, future metadata fields, target summary fields, missing metadata handling, failure interpretation, non-equivalence cautions, and future staging. It does not create a status marker, change wrapper/Makefile/code/tests/fixture JSON/workflow files, implement TypeScript/Rust helpers, or implement event durability.

## 31. Step-web-logger-012 Shared Vector Validator Remote Status Marker

Step-web-logger-012 is recorded in `docs/status/web_logger_unicode_hash_vector_validator_release_quality_remote_run_status.md`.

It records public-safe remote release-quality metadata for the Step-web-logger-010 wrapper check, including the observed label, Makefile target command, final ok label, and 15-vector count-only summary. It does not alter the pre-collection blocker status for TypeScript/Rust helper implementation or event durability.

## 32. Step-web-logger-013 Shared Vector Validator Final Safety Review

Step-web-logger-013 is recorded in `docs/web_logger_unicode_hash_vector_validator_release_quality_chain_final_safety_review.md`.

It accepts the Web logger Unicode/hash vector validator release-quality chain with explicit boundary for the fixed 15-vector synthetic metadata/count-only fixture contract. It leaves TypeScript/Rust helpers, Rust replay Unicode correctness, TypeScript logger hash correctness, and event durability as future work.

## 33. Step-web-logger-014 Rust UTF-16 Offset Conversion Helper Design

Step-web-logger-014 is recorded in `docs/web_logger_rust_utf16_offset_conversion_helper_design.md`.

It designs a future Rust helper for converting browser-originated UTF-16 code unit offsets into UTF-8 byte offsets at valid Rust char boundaries. It does not implement the helper, change replay behavior, change fixture JSON, or alter the event durability gap.

## 34. Step-web-logger-015 Rust UTF-16 Offset Conversion Helper

Step-web-logger-015 adds the focused Rust helper and tests for UTF-16 code unit offset to UTF-8 byte offset conversion in `kslog_replay`.

The helper follows the safety design for offset semantics: no Unicode normalization, no newline normalization, no rounding or repair, valid Rust char boundaries only, fail-closed behavior for out-of-range / surrogate-pair internal / `start > end` cases, and public-safe diagnostics. This is a utility implementation boundary only. It does not add broader runtime integration, Rust or TypeScript SHA-256 helper work, TypeScript/Rust cross-language checks, queueing, IndexedDB buffering, acknowledgement, retry, deduplication, or collection readiness.

## 35. Step-web-logger-016 Rust Helper Makefile Target Design

Step-web-logger-016 adds [Rust UTF-16 Offset Conversion Helper Makefile Target Design](web_logger_rust_utf16_offset_conversion_helper_makefile_target_design.md).

The design proposes a future focused Makefile target for the Step-web-logger-015 Rust helper tests. It keeps event durability, broader runtime integration, TypeScript/Rust hash work, release-quality integration, CI workflow changes, and collection readiness outside this step.

## 36. Step-web-logger-017 Rust Helper Makefile Target

Step-web-logger-017 adds the focused Makefile target `check-web-logger-rust-utf16-offset-conversion`.

The target runs `cargo test -p kslog_replay utf16` for the Rust helper tests. It keeps release-quality integration, CI workflow changes, broader runtime integration, TypeScript/Rust hash work, queueing, IndexedDB buffering, acknowledgement, retry, deduplication, and collection readiness outside this step.

## 37. Step-web-logger-018 Rust Helper Release-Quality Integration Design

Step-web-logger-018 adds [Rust UTF-16 Offset Conversion Helper Release Quality Integration Design](web_logger_rust_utf16_offset_conversion_helper_release_quality_integration_design.md).

The design proposes future wrapper execution of `make check-web-logger-rust-utf16-offset-conversion` after the existing Web logger Unicode/hash vector fixture validation check. It does not change wrapper code, Makefile, Rust code, tests, fixture JSON, CI workflow, broader runtime integration, TypeScript/Rust hash work, queueing, IndexedDB buffering, acknowledgement, retry, deduplication, or collection readiness.

## 38. Step-web-logger-019 Rust Helper Release-Quality Integration

Step-web-logger-019 adds `release_quality_check: web logger Rust UTF-16 offset conversion helper` to the release-quality wrapper.

The wrapper calls `make check-web-logger-rust-utf16-offset-conversion` after the Web logger Unicode/hash vector fixture validation check. This remains focused on Rust helper tests and does not add CI workflow changes, broader runtime integration, TypeScript/Rust hash work, queueing, IndexedDB buffering, acknowledgement, retry, deduplication, or collection readiness.

## 39. Step-web-logger-020 Rust Helper Remote/Manual Run Record Workflow Design

Step-web-logger-020 adds [Rust UTF-16 Offset Conversion Helper Release Quality Remote/Manual Run Record Workflow](web_logger_rust_utf16_offset_conversion_helper_release_quality_remote_run_record_workflow.md).

The design plans future public-safe status evidence for the Step-web-logger-019 wrapper check. It does not create the status marker, change wrapper code, change Makefile, change Rust code or tests, change fixture JSON, add CI workflow changes, add broader runtime integration, add TypeScript/Rust hash work, add queueing, add IndexedDB buffering, add acknowledgement, add retry, add deduplication, or add collection readiness.

## 40. Step-web-logger-021 Rust Helper Remote Status Marker

Step-web-logger-021 adds [Rust UTF-16 Offset Conversion Helper Release Quality Remote Run Status](status/web_logger_rust_utf16_offset_conversion_helper_release_quality_remote_run_status.md).

The marker records public-safe remote metadata/count-only evidence for the Step-web-logger-019 wrapper check. It does not change wrapper code, change Makefile, change Rust code or tests, change fixture JSON, add CI workflow changes, add broader runtime integration, add TypeScript/Rust hash work, add queueing, add IndexedDB buffering, add acknowledgement, add retry, add deduplication, or add collection readiness.

## 41. Step-web-logger-022 Rust Helper Final Safety Review

Step-web-logger-022 adds [Rust UTF-16 Offset Conversion Helper Release Quality Chain Final Safety Review](web_logger_rust_utf16_offset_conversion_helper_release_quality_chain_final_safety_review.md).

The review accepts the focused Rust helper release-quality chain with an explicit boundary. It does not change wrapper code, change Makefile, change Rust code or tests, change fixture JSON, add CI workflow changes, add broader runtime integration, add TypeScript/Rust hash work, add queueing, add IndexedDB buffering, add acknowledgement, add retry, add deduplication, or add collection readiness.

## 42. Step-web-logger-023 Broader Replay Integration Design

Step-web-logger-023 adds [Rust UTF-16 Offset Conversion Helper Broader Replay Integration Design](web_logger_rust_utf16_offset_conversion_helper_broader_replay_integration_design.md).

The design plans replay-first integration of the helper before broader validate / extract / micro_episode chains. It does not change wrapper code, change Makefile, change Rust code or tests, change fixture JSON, add CI workflow changes, add runtime implementation, add TypeScript/Rust hash work, add queueing, add IndexedDB buffering, add acknowledgement, add retry, add deduplication, or add collection readiness.

## 43. Step-web-logger-024 Replay-Focused Integration

Step-web-logger-024 adds replay-focused UTF-16 offset integration in `kslog_replay`.

Replay now uses the existing helper to convert browser-originated cursor and selection offsets before string indexing / replacement, checks replay document length as UTF-16 code unit length, and fail-closes invalid UTF-16 offsets. Focused `utf16` replay tests cover successful and invalid synthetic cases with content-suppressed diagnostics.

This does not change validate / extract / micro_episode behavior, schema-level position_unit behavior, Makefile, wrapper, CI workflow, fixture JSON, Rust SHA-256 helper work, TypeScript SHA-256 helper work, TypeScript/Rust checks, queueing, IndexedDB buffering, acknowledgement, retry, deduplication, or collection readiness.

## 44. Step-web-logger-025 Makefile Target Semantics Design

Step-web-logger-025 adds [Rust UTF-16 Replay Integration Makefile Target Design](web_logger_rust_utf16_replay_integration_makefile_target_design.md).

The design recommends future help text/docs alignment for the existing Rust UTF-16 target now that it covers helper-focused and replay-focused tests. It does not change Makefile, wrapper, Rust code, tests, fixture JSON, validate / extract / micro_episode behavior, schema-level position_unit behavior, CI workflow, Rust SHA-256 helper work, TypeScript SHA-256 helper work, TypeScript/Rust checks, queueing, IndexedDB buffering, acknowledgement, retry, deduplication, or collection readiness.

## 45. Step-web-logger-026 Makefile Help Text Alignment

Step-web-logger-026 updates the existing Rust UTF-16 target help text to `Run Rust UTF-16 offset conversion and replay integration tests`.

The command remains `cargo test -p kslog_replay utf16`, and no new target or wrapper label change is introduced. This preserves the durability safety boundary: queueing, IndexedDB buffering, acknowledgement, retry, deduplication, ordering, delivery durability, validate / extract / micro_episode integration, schema-level position_unit policy, TypeScript/Rust hash work, and collection readiness remain future work.

## 46. Step-web-logger-027 Release-Quality Label Update Design

Step-web-logger-027 adds [Rust UTF-16 Replay Integration Release Quality Label Update Design](web_logger_rust_utf16_replay_integration_release_quality_label_update_design.md).

The design recommends future wrapper label wording alignment for helper-focused plus replay-focused UTF-16 coverage. It does not change the command, add a new target, update the wrapper in this step, or alter the durability safety boundary.

## 47. Step-web-logger-028 Release-Quality Label Update

Step-web-logger-028 updates the wrapper label to `release_quality_check: web logger Rust UTF-16 offset conversion and replay integration`.

The command and target remain unchanged. This update does not alter the durability safety boundary or implement queueing, IndexedDB buffering, acknowledgement, retry, deduplication, ordering, delivery durability, TypeScript/Rust hash work, validate / extract / micro_episode integration, or schema-level position_unit policy.

## 48. Step-web-logger-029 Run Record Workflow Design

Step-web-logger-029 adds [Rust UTF-16 Replay Integration Release Quality Remote/Manual Run Record Workflow](web_logger_rust_utf16_replay_integration_release_quality_remote_run_record_workflow.md).

The workflow design preserves the durability safety boundary. It does not create a status marker, change wrapper or target behavior, alter code or tests, change fixture JSON, or implement queueing, IndexedDB buffering, acknowledgement, retry, deduplication, ordering, delivery durability, TypeScript/Rust hash work, validate / extract / micro_episode integration, or schema-level position_unit policy.

## 49. Step-web-logger-032 Schema-Level Position Unit Policy Design

Step-web-logger-032 adds [Schema-Level Position Unit Policy Design for Web Logger Events](web_logger_schema_position_unit_policy_design.md).

The design preserves the durability safety boundary. It plans future explicit `position_unit=utf16_code_unit` schema / validation policy but does not implement queueing, IndexedDB buffering, acknowledgement, retry, deduplication, ordering, delivery durability, TypeScript/Rust hash work, validate / extract / micro_episode integration, code changes, tests, fixture JSON changes, Makefile changes, wrapper changes, or CI workflow changes.

## 50. Step-web-logger-033 Schema-Level Position Unit Fixture Design

Step-web-logger-033 adds [Schema-Level Position Unit Fixture Design for Web Logger Events](web_logger_schema_position_unit_fixture_design.md).

The design preserves the durability safety boundary. It plans future synthetic fixture cases for explicit `position_unit=utf16_code_unit` schema / validation policy but does not implement queueing, IndexedDB buffering, acknowledgement, retry, deduplication, ordering, delivery durability, TypeScript/Rust hash work, validate / extract / micro_episode integration, code changes, tests, fixture JSON changes, Makefile changes, wrapper changes, or CI workflow changes.

## 51. Step-web-logger-034 Schema-Level Position Unit Fixtures

Step-web-logger-034 adds `tests/fixtures/web_logger_position_unit_schema/`
with synthetic valid / invalid / legacy cases for future schema-level
`position_unit=utf16_code_unit` checks.

The new fixture root preserves the durability safety boundary. It does not
implement queueing, IndexedDB buffering, acknowledgement, retry, deduplication,
ordering, delivery durability, TypeScript/Rust hash work, validate / extract /
micro_episode integration, schema / validator behavior, Makefile changes,
wrapper changes, or CI workflow changes.

## 52. Step-web-logger-035 Schema-Level Position Unit Fixture Validator Design

Step-web-logger-035 adds
[Schema-Level Position Unit Fixture Validator Design](web_logger_schema_position_unit_fixture_validator_design.md).

The design preserves the durability safety boundary. It plans a future
public-safe fixture validator and does not implement queueing, IndexedDB
buffering, acknowledgement, retry, deduplication, ordering, delivery
durability, TypeScript/Rust hash work, validate / extract / micro_episode
integration, schema / validator behavior, code changes, tests, fixture changes,
Makefile changes, wrapper changes, or CI workflow changes.

## 53. Step-web-logger-036 Schema-Level Position Unit Fixture Validator

Step-web-logger-036 adds a Python-first fixture contract validator with
summary-only public-safe output for
`tests/fixtures/web_logger_position_unit_schema/`.

The validator preserves the durability safety boundary. It does not implement
queueing, IndexedDB buffering, acknowledgement, retry, deduplication, ordering,
delivery durability, TypeScript/Rust hash work, validate / extract /
micro_episode integration, Rust schema / validator behavior, Makefile changes,
wrapper changes, or CI workflow changes.

## 54. Step-web-logger-037 Schema-Level Position Unit Fixture Validator Makefile Target Design

Step-web-logger-037 adds
[Schema-Level Position Unit Fixture Validator Makefile Target Design](web_logger_schema_position_unit_fixture_validator_makefile_target_design.md).

The design preserves the durability safety boundary. It plans only a future
Makefile target for the summary-only fixture contract validator and does not
implement queueing, IndexedDB buffering, acknowledgement, retry,
deduplication, ordering, delivery durability, TypeScript/Rust hash work,
validate / extract / micro_episode integration, Rust schema / validator
behavior, Makefile changes, wrapper changes, or CI workflow changes.

## 55. Step-web-logger-038 Schema-Level Position Unit Fixture Validator Makefile Target

Step-web-logger-038 adds Makefile target
`check-web-logger-position-unit-fixtures`.

The target preserves the durability safety boundary. It runs summary-only
fixture contract validation and does not implement queueing, IndexedDB
buffering, acknowledgement, retry, deduplication, ordering, delivery
durability, TypeScript/Rust hash work, validate / extract / micro_episode
integration, Rust schema / validator behavior, wrapper changes, or CI workflow
changes.

## 56. Step-web-logger-039 Schema-Level Position Unit Fixture Validator Release-Quality Integration Design

Step-web-logger-039 adds
[Schema-Level Position Unit Fixture Validator Release Quality Integration Design](web_logger_schema_position_unit_fixture_validator_release_quality_integration_design.md).

The design preserves the durability safety boundary. It plans only future
wrapper integration for the fixture contract target and does not implement
queueing, IndexedDB buffering, acknowledgement, retry, deduplication,
ordering, delivery durability, TypeScript/Rust hash work, validate / extract /
micro_episode integration, Rust schema / validator behavior, wrapper changes
in this step, or CI workflow changes.

## 57. Step-web-logger-040 Schema-Level Position Unit Fixture Validator Release-Quality Integration

Step-web-logger-040 adds release-quality wrapper integration for
`check-web-logger-position-unit-fixtures`.

The integration preserves the durability safety boundary. It adds fixture
contract validation to the wrapper only and does not implement queueing,
IndexedDB buffering, acknowledgement, retry, deduplication, ordering, delivery
durability, TypeScript/Rust hash work, validate / extract / micro_episode
integration, Rust schema / validator behavior, status markers, final safety
review, or CI workflow changes.

## 58. Step-web-logger-041 Schema-Level Position Unit Fixture Validator Release-Quality Run Record Workflow Design

Step-web-logger-041 adds
[Schema-Level Position Unit Fixture Validator Release Quality Remote/Manual Run Record Workflow](web_logger_schema_position_unit_fixture_validator_release_quality_remote_run_record_workflow.md).

The workflow design preserves the durability safety boundary. It designs future
status evidence for the fixture contract target only and does not implement
queueing, IndexedDB buffering, acknowledgement, retry, deduplication,
ordering, delivery durability, TypeScript/Rust hash work, validate / extract /
micro_episode integration, Rust schema / validator behavior, status markers,
final safety review, wrapper changes, or CI workflow changes.

## 59. Step-web-logger-042 Schema-Level Position Unit Fixture Validator Release-Quality Remote Status Marker

Step-web-logger-042 adds
[Schema-Level Position Unit Fixture Validator Release Quality Remote Run Status](status/web_logger_schema_position_unit_fixture_validator_release_quality_remote_run_status.md).

The marker preserves the durability safety boundary. It records public-safe
remote status evidence for the fixture contract target only and does not
implement queueing, IndexedDB buffering, acknowledgement, retry,
deduplication, ordering, delivery durability, TypeScript/Rust hash work,
validate / extract / micro_episode integration, Rust schema / validator
behavior, final safety review, wrapper changes, or CI workflow changes.

## 60. Step-web-logger-043 Schema-Level Position Unit Fixture Validator Release-Quality Final Safety Review

Step-web-logger-043 adds
[Schema-Level Position Unit Fixture Validator Release Quality Chain Final Safety Review](web_logger_schema_position_unit_fixture_validator_release_quality_chain_final_safety_review.md).

The review preserves the durability safety boundary. It accepts only bounded
fixture-contract validation and does not implement queueing, IndexedDB
buffering, acknowledgement, retry, deduplication, ordering, delivery
durability, TypeScript/Rust hash work, validate / extract / micro_episode
integration, Rust schema / validator behavior, wrapper changes, or CI workflow
changes.

## 61. Step-web-logger-044 Rust Schema-Level Position Unit Policy Implementation Design

Step-web-logger-044 adds
[Rust Schema-Level Position Unit Policy Implementation Design](web_logger_rust_schema_position_unit_policy_implementation_design.md).

The design preserves the durability safety boundary. It plans future schema /
validator position_unit policy work only and does not implement queueing,
IndexedDB buffering, acknowledgement, retry, deduplication, ordering, delivery
durability, TypeScript/Rust hash work, code changes, wrapper changes, or CI
workflow changes.

## 62. Step-web-logger-045 Rust Schema Boundary Follow-Up

Step-web-logger-045 adds the bounded Rust schema parser/accessor boundary for
`position_unit` metadata in `kslog_schema`. This does not affect the durability
safety design.

Event queueing, IndexedDB persistence, acknowledgement, retry, deduplication,
server-side idempotency, ordering guarantees, TypeScript/Rust hash work, Rust
validator policy enforcement, validate / extract / micro_episode integration,
production readiness, real-data readiness, and model performance evidence
remain future work.

## 63. Step-web-logger-046 Rust Validator Mapping Design

Step-web-logger-046 adds
[Rust Validator Position Unit Policy Test and Fixture Mapping Design](web_logger_rust_validator_position_unit_policy_test_fixture_mapping_design.md).

This design does not change event durability boundaries. Queueing, IndexedDB
persistence, acknowledgement, retry, deduplication, server-side idempotency,
ordering guarantees, TypeScript/Rust hash work, production readiness,
real-data readiness, and model performance evidence remain future work.

## 64. Step-web-logger-047 Rust Validator Phase 1 Follow-Up

Step-web-logger-047 adds bounded `kslog_validate` Phase 1 position-unit
presence / value / schema-version enforcement. The safety boundary remains
metadata-gating only and does not add delivery durability.

Event queueing, IndexedDB persistence, acknowledgement, retry, deduplication,
server-side idempotency, ordering guarantees, TypeScript/Rust hash work, Phase
2 UTF-16 numeric metadata validation, extract / micro_episode integration,
production readiness, real-data readiness, and model performance evidence
remain future work.

## 65. Step-web-logger-048 Rust Validator Phase 1 Makefile Target Design

Step-web-logger-048 adds
[Rust Validator Position Unit Phase 1 Makefile Target Design](web_logger_rust_validator_position_unit_phase1_makefile_target_design.md).

This design does not change event durability boundaries. It plans future
Makefile exposure for focused validator tests only; queueing, IndexedDB
persistence, acknowledgement, retry, deduplication, server-side idempotency,
ordering guarantees, TypeScript/Rust hash work, production readiness,
real-data readiness, and model performance evidence remain future work.

## 66. Step-web-logger-049 Rust Validator Phase 1 Makefile Target

Step-web-logger-049 adds Makefile target
`check-web-logger-rust-validator-position-unit-phase1`.

This target runs focused Rust validator Phase 1 tests only. It does not change
event durability boundaries: queueing, IndexedDB persistence, acknowledgement,
retry, deduplication, server-side idempotency, ordering guarantees,
TypeScript/Rust hash work, production readiness, real-data readiness, and
model performance evidence remain future work.

## 67. Step-web-logger-050 Rust Validator Phase 1 Release-Quality Integration Design

Step-web-logger-050 designs future release-quality integration for the
Step049 target. It remains a release-quality planning step and does not change
event durability boundaries: queueing, IndexedDB persistence, acknowledgement,
retry, deduplication, server-side idempotency, ordering guarantees,
TypeScript/Rust hash work, production readiness, real-data readiness, and
model performance evidence remain future work.

## 68. Step-web-logger-051 Rust Validator Phase 1 Release-Quality Integration

Step-web-logger-051 adds release-quality wrapper integration for the Rust
validator Phase 1 target. It does not change event durability boundaries:
queueing, IndexedDB persistence, acknowledgement, retry, deduplication,
server-side idempotency, ordering guarantees, TypeScript/Rust hash work,
production readiness, real-data readiness, and model performance evidence
remain future work.

## 69. Step-web-logger-052 Rust Validator Phase 1 Run Record Workflow Design

Step-web-logger-052 designs future run-record workflow for the Rust validator
Phase 1 release-quality check. It does not change event durability boundaries:
queueing, IndexedDB persistence, acknowledgement, retry, deduplication,
server-side idempotency, ordering guarantees, TypeScript/Rust hash work,
production readiness, real-data readiness, and model performance evidence
remain future work.
