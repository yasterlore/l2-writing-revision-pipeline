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
