# Web Logger Shared Unicode and Text Hash Test Vector Design

## 1. Title

Web Logger Shared Unicode and Text Hash Test Vector Design

## 2. Scope

This is a test-vector-design / docs-only step.

Out of scope:

- no TypeScript implementation changes
- no Rust implementation changes
- no Python implementation changes
- no tests changes
- no fixture JSON changes
- no schema implementation changes
- no runtime / validator implementation changes
- no CI workflow changes
- no Makefile changes
- no release-quality wrapper changes
- no real data
- no raw learner text
- no production readiness proof
- no real-data readiness proof
- no model performance proof

This step does not create the vector fixture root, compute hash values, implement helper code, or add CI checks.

## 3. Design Status

This document designs future shared synthetic test vectors.

This document does not:

- create the actual vector fixture files
- compute or hardcode final SHA-256 values
- implement UTF-16 to UTF-8 conversion
- implement TypeScript / Rust hash helpers
- implement TypeScript / Rust vector checks
- implement event durability queueing, IndexedDB, acknowledgement, retry, or deduplication

Future implementation and review steps are required.

## 4. Goals of Shared Test Vectors

The future shared vectors should make these properties reviewable:

- TypeScript and Rust agree on text hash canonicalization.
- Rust correctly converts browser UTF-16 code unit offsets to UTF-8 byte indices.
- Invalid offsets fail closed.
- Replay / validation diagnostics remain public-safe.
- Unicode boundary mistakes are not silently accepted.
- Vectors are synthetic and minimal.
- Vectors contain no real participant text.
- Vectors can support future CI cross-language checks.

The vectors should become a single shared contract for TypeScript logger tests, Rust validation/replay tests, and later cross-language checks.

## 5. Vector File Design

Proposed future fixture paths, not created in this step:

- `tests/fixtures/web_logger_unicode_hash_vectors/README.md`
- `tests/fixtures/web_logger_unicode_hash_vectors/vectors.json`

Intended top-level fields:

- `vector_schema_version`
- `position_unit`
- `hash_algorithm`
- `hash_encoding`
- `unicode_normalization`
- `newline_normalization`
- `trailing_newline_policy`
- `hash_output_format`
- `vectors`
- `generated_by`
- `reviewed_by`
- `non_real_data_notice`
- `no_oracle_notice`

Intended per-vector fields:

- `vector_id`
- `category`
- `source_text`
- `source_text_description`
- `utf16_code_unit_length`
- `utf8_byte_length`
- `code_point_count`, optional diagnostic
- `grapheme_cluster_note`, optional diagnostic
- `hash_sha256_utf8_lowercase_hex`
- `offset_cases`
- `expected_failures`
- `notes`

Intended per-offset-case fields:

- `case_id`
- `description`
- `utf16_start`
- `utf16_end`
- `expected_utf8_start_byte`
- `expected_utf8_end_byte`
- `expected_selected_text_description`
- `expected_status`
- `reason_code`
- `public_safe_note`

Clarifications:

- `source_text` may be synthetic and minimal in future fixture files.
- Docs may describe planned text, but should avoid long raw strings.
- No real participant text is allowed.
- No private text is allowed.
- No raw event payload body is included in docs.
- Final hash values should be generated and reviewed in a future implementation step.

## 6. Canonical Vector Metadata Policy

Every future vector set must declare:

- `position_unit=utf16_code_unit`
- `hash_algorithm=SHA-256`
- `hash_encoding=UTF-8`
- `unicode_normalization=none`
- `newline_normalization=none`
- `trailing_newline_policy=preserve_as_is`
- `hash_output_format=lowercase_hex`
- `source_text_policy=synthetic_minimal_text_only`
- `real_data_allowed=false`

These metadata fields should be checked before any vector body is processed by TypeScript or Rust tests.

## 7. Required Vector Categories

| category | purpose | minimal synthetic example description | expected offset behavior | expected hash behavior | risk covered | priority |
| --- | --- | --- | --- | --- | --- | --- |
| empty string | Initial state and zero-length hash baseline. | Empty string. | Offset 0 valid; nonzero offsets invalid. | SHA-256 over zero-length UTF-8 bytes. | Initial replay/hash mismatch. | P0 required before implementation confidence |
| ASCII | Baseline one-byte-per-code-unit case. | Short synthetic ASCII token. | UTF-16 offsets equal UTF-8 byte offsets. | Canonical SHA-256 over exact bytes. | Regression in simple case. | P0 required before implementation confidence |
| Japanese | BMP non-ASCII characters. | Short synthetic Japanese token. | UTF-16 offsets count code units; UTF-8 byte offsets differ. | Canonical SHA-256 over UTF-8. | Mistaking UTF-16 offset for byte offset. | P0 required before implementation confidence |
| full-width alphanumerics | BMP full-width characters. | Synthetic full-width letters/numbers. | UTF-16 offsets differ from UTF-8 byte offsets. | Canonical SHA-256 over exact text. | Width/display confusion. | P0 required before implementation confidence |
| emoji / surrogate pair | Non-BMP character requiring two UTF-16 code units. | Single synthetic emoji. | Offset before and after emoji valid; inside surrogate pair invalid. | Canonical SHA-256 over UTF-8 bytes. | Surrogate boundary bug. | P0 required before implementation confidence |
| combining sequence | Combining mark boundary behavior. | Minimal letter plus combining mark. | Boundary may be code-unit-valid even if grapheme-sensitive. | No normalization; distinct from precomposed form. | Silent normalization or grapheme assumption. | P0 required before implementation confidence |
| precomposed accented character | Compare with combining form. | Minimal precomposed accented character. | Single scalar offset behavior. | Distinct hash from decomposed form. | Unicode normalization drift. | P0 required before implementation confidence |
| mixed Japanese + emoji | Mixed BMP and non-BMP text. | Short Japanese token plus emoji. | Offsets around emoji and BMP characters checked. | Canonical exact-text hash. | Mixed offset accounting. | P0 required before implementation confidence |
| CRLF multi-line | Preserve CRLF. | Two-line synthetic text with CRLF. | Offsets count both CR and LF code units. | Hash preserves CRLF. | Silent newline normalization. | P0 required before implementation confidence |
| LF multi-line | Preserve LF. | Two-line synthetic text with LF. | LF counts as one UTF-16 code unit. | Hash differs from CRLF form. | Platform newline drift. | P0 required before implementation confidence |
| CR-only line break | Preserve CR if intentionally supported. | Two-line synthetic text with CR only. | CR counts as one UTF-16 code unit. | Hash preserves CR. | Legacy newline ambiguity. | P1 before pilot |
| trailing newline | Preserve terminal newline. | Minimal token with trailing newline. | Final offset includes trailing newline. | Hash includes trailing newline. | Trim bug. | P0 required before implementation confidence |
| tab | Tab is stored text, not display width. | Two short synthetic fields separated by tab. | Tab is one UTF-16 code unit. | Hash preserves tab. | Display-width confusion. | P0 required before implementation confidence |
| selection around emoji | Validate spans adjacent to surrogate pair. | Synthetic token with emoji in middle. | Surrounding offsets valid; inside surrogate invalid. | Hash exact. | Span conversion bug. | P0 required before implementation confidence |
| offset inside surrogate pair | Invalid offset case. | Same minimal emoji vector. | Expected validation error. | Hash may still be computed for whole text, but offset case fails. | Boundary fail-closed behavior. | P0 required before implementation confidence |
| offset beyond UTF-16 length | Invalid out-of-range case. | Any short synthetic text. | Expected validation error. | Hash independent of invalid offset. | Out-of-range acceptance. | P0 required before implementation confidence |
| combining mark boundary behavior | Grapheme-sensitive but code-unit-valid boundary. | Letter plus combining mark. | Boundary may be valid; note grapheme sensitivity. | No normalization. | Over-rejection or silent repair. | P1 before pilot |
| mixed BMP and non-BMP | Broader mixed accounting. | Short synthetic mix of ASCII, Japanese, full-width, emoji. | Multiple offset cases across character classes. | Exact SHA-256. | Cross-class drift. | P1 before pilot |
| long mixed Unicode synthetic text | Larger deterministic vector. | Longer synthetic-only mixture. | Several validated spans. | Exact SHA-256. | Accumulated offset error. | P2 before scale-up |

## 8. Recommended Initial Vector Set

Do not compute hash values in this step.

| vector | category | intended synthetic text pattern | intended offset cases | expected validation behavior | hash expected later? | priority |
| --- | --- | --- | --- | --- | --- | --- |
| V001 | empty string | Empty stored text. | Offset 0, and invalid offset 1. | Offset 0 pass; offset 1 fail. | Yes. | P0 |
| V002 | ASCII simple text | Short synthetic ASCII token. | Select first character, middle span, whole text. | Valid offsets pass. | Yes. | P0 |
| V003 | Japanese simple text | Short synthetic Japanese token. | Select first character and whole text. | Valid UTF-16 offsets convert to multi-byte UTF-8 byte indices. | Yes. | P0 |
| V004 | full-width alphanumerics | Minimal full-width letters/numbers. | Select one full-width character and full text. | Valid offsets pass; byte indices differ from offsets. | Yes. | P0 |
| V005 | single emoji requiring surrogate pair | One non-BMP emoji. | Before emoji, after emoji, inside surrogate pair. | Boundary offsets pass; inside offset fails. | Yes. | P0 |
| V006 | Japanese plus emoji | Short Japanese token with one emoji. | Select around emoji and adjacent Japanese character. | Valid offsets pass; inside surrogate fails if included. | Yes. | P0 |
| V007 | combining sequence e + combining acute | Minimal decomposed accented form. | Select base only, combining mark boundary, whole sequence. | Code-unit-valid offsets pass but note grapheme sensitivity. | Yes. | P0 |
| V008 | precomposed accented character | Minimal precomposed accented form. | Select character and whole text. | Valid offsets pass; hash differs from V007. | Yes. | P0 |
| V009 | LF multi-line | Two short synthetic lines with LF. | Select across line break and whole text. | LF preserved. | Yes. | P0 |
| V010 | CRLF multi-line | Two short synthetic lines with CRLF. | Select across CRLF and whole text. | CRLF preserved as two code units. | Yes. | P0 |
| V011 | trailing newline | Short synthetic token ending with newline. | Select trailing newline and whole text. | Trailing newline preserved. | Yes. | P0 |
| V012 | tab-separated text | Two synthetic tokens separated by tab. | Select tab and adjacent spans. | Tab is one code unit. | Yes. | P0 |
| V013 | invalid offset inside surrogate pair | Same pattern as V005 or V006. | Start or end inside surrogate pair. | Expected validation failure. | Whole-text hash may be present; offset case fails. | P0 |
| V014 | invalid offset beyond UTF-16 length | Short synthetic string. | End beyond UTF-16 length. | Expected validation failure. | Whole-text hash may be present; offset case fails. | P0 |
| V015 | mixed long synthetic Unicode text | Mixed ASCII, Japanese, full-width, emoji, newline, tab. | Multiple spans across categories. | Valid spans pass; invalid spans fail by category. | Yes. | P1 |

## 9. UTF-16 / UTF-8 Offset Expectation Policy

Offset expectations must be derived from the exact stored string.

Policy:

- UTF-16 code unit offsets are the input.
- UTF-8 byte indices are the expected output for the Rust helper.
- Offsets must map to Rust `char` boundaries.
- Offsets inside surrogate pairs must fail.
- Offsets beyond UTF-16 length must fail.
- Offsets should not be rounded.
- Offsets should not be normalized.
- Offsets that split combining sequences may be code-unit-valid but should be documented as grapheme-sensitive.
- Grapheme-sensitive does not mean invalid unless the policy later changes.

## 10. Hash Expectation Policy

Hash expectations follow Step-web-logger-002:

- hash is computed over exact UTF-8 bytes of stored string
- no JSON escaping layer
- no Unicode normalization
- no newline normalization
- trailing newline preserved
- empty string hashes zero-length UTF-8 byte sequence
- TypeScript and Rust expected value must be identical
- mismatch must fail closed in future replay / validation
- public reports must not include raw before/after text on mismatch

## 11. Invalid Vector Policy

Required invalid vector types:

| invalid type | expected_status | reason_code | public-safe diagnostic expectation | raw text emission allowed |
| --- | --- | --- | --- | --- |
| offset inside surrogate pair | fail_closed | `offset_inside_surrogate_pair` | Include vector id, offset case id, field name, and reason code. | false |
| offset beyond UTF-16 length | fail_closed | `offset_out_of_range` | Include vector id, expected length metadata, and reason code. | false |
| negative offset, if schema/parser can represent it | usage_error | `negative_offset` | Include vector id and field name. | false |
| start > end | fail_closed | `offset_range_inverted` | Include vector id, offset case id, and reason code. | false |
| hash mismatch | fail_closed | `hash_mismatch` | Include vector id, hash field name, and reason code. | false |
| unsupported vector schema version | usage_error | `unsupported_vector_schema_version` | Include declared version only. | false |
| missing position_unit | usage_error | `missing_position_unit` | Include missing field name. | false |
| unsupported hash_algorithm | usage_error | `unsupported_hash_algorithm` | Include declared algorithm metadata. | false |
| unsupported hash_encoding | usage_error | `unsupported_hash_encoding` | Include declared encoding metadata. | false |
| unsupported Unicode normalization policy | usage_error | `unsupported_unicode_normalization` | Include declared policy metadata. | false |
| newline normalization mismatch | fail_closed | `newline_normalization_mismatch` | Include vector id and policy fields. | false |
| raw learner text marker, if marker policy exists | fail_closed | `raw_learner_text_marker_detected` | Include marker category only. | false |
| real data marker, if marker policy exists | fail_closed | `real_data_marker_detected` | Include marker category only. | false |

Invalid vectors should be synthetic and metadata-safe. They should not rely on real text, private text, or raw event payload bodies.

## 12. Cross-Language Validation Design

Future TypeScript checks:

- compute SHA-256 UTF-8 lowercase hex for every valid vector
- verify UTF-16 code unit length
- verify selected offset slices under JavaScript semantics
- export vector results in public-safe summary
- avoid raw event payload body in test output

Future Rust checks:

- parse shared vectors
- verify schema metadata
- convert UTF-16 offsets to UTF-8 byte indices
- verify selected byte spans are valid `char` boundaries
- compute SHA-256 UTF-8 lowercase hex
- compare expected hashes
- reject invalid vectors fail-closed
- emit metadata-only diagnostics

Future cross-language check:

- TypeScript generated hashes equal Rust generated hashes.
- TypeScript length / offset metadata align with Rust conversion.
- Invalid vectors fail in expected categories.
- Public-safe reports contain no raw text.

## 13. Future CI Integration Design

Future standalone target proposals, not implemented here:

- `check-web-logger-unicode-hash-vectors`
- `check-web-logger-ts-rust-hash-consistency`
- `check-web-logger-utf16-offset-conversion`

Future release-quality label proposals, not added here:

- `release_quality_check: web logger unicode hash shared vectors`
- `release_quality_check: web logger utf16 offset conversion`

Future CI / release-quality behavior:

- test should be deterministic
- no network access required
- no real data required
- output should be metadata-only
- failure output should not expose raw vector text if avoidable
- `content_suppressed=true` style summary is recommended
- release-quality integration should wait until standalone checks are stable and reviewed

## 14. Review and Generation Procedure

Future hash value generation procedure:

- generate expected hash values using a reviewed script
- compare TypeScript and Rust independently
- do not manually type hash values without review
- record script name and version
- review vector source text as synthetic and minimal
- record no-real-data notice
- record reviewer checklist
- regenerate only with explicit schema version change
- explain every hash value change

The first generated vector fixture should include a README explaining how values were generated and reviewed.

## 15. Relationship to Schema Clarification

This vector design implements the testing strategy for the Step-web-logger-002 policy. It does not change that policy and does not implement code.

It prepares future implementation of:

- Rust UTF-16 code unit to UTF-8 byte conversion helper
- TypeScript SHA-256 helper
- Rust SHA-256 helper
- shared validation tests
- public-safe mismatch diagnostics

## 16. Relationship to Event Durability

This step does not implement queue, IndexedDB, acknowledgement, retry, or deduplication.

Durability remains P0. Shared Unicode/hash vectors should be completed before or alongside replay-critical durability work because durable event delivery still needs unambiguous event semantics.

Event durability tests will need separate failure injection vectors later. This vector design focuses only on offset and hash semantics.

## 17. Relationship to No-Oracle and Synthetic-Only Boundaries

Vectors must be synthetic only.

They must not include real participant data or raw learner text. They do not relax no-oracle constraints, authorize real collection, or validate model performance.

The vectors protect replay integrity before no-oracle audit by reducing ambiguity in offset conversion and hash verification.

## 18. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- Unicode correctness implementation completion
- hash compatibility implementation completion
- event durability implementation completion
- TypeScript / Rust vector check implementation completion
- current TypeScript and Rust hash outputs are already aligned
- data collection readiness
- deployment readiness

## 19. Public-Safe Documentation Policy

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
- long raw strings should be avoided in docs
- future fixture files may contain minimal synthetic text only

## 20. Recommended Next Codex Step

Recommended next step:

Step-web-logger-004: implement shared synthetic Unicode/hash vector fixtures and docs

Clarification:

- Step-web-logger-004 should create the vector fixture root and README.
- Step-web-logger-004 may generate reviewed expected hash values.
- Step-web-logger-004 should not yet implement full TypeScript/Rust helpers unless explicitly scoped.
- Step-web-logger-004 should still avoid event durability implementation.
- Step-web-logger-004 should keep all examples synthetic and minimal.

## 21. Step-web-logger-004 Fixture Root Implementation

Step-web-logger-004 creates the shared synthetic vector fixture root at `tests/fixtures/web_logger_unicode_hash_vectors/`.

The root contains:

- `README.md`
- `vectors.json`

`vectors.json` fixes `vector_schema_version=web_logger_unicode_hash_vectors_v0.1`, `position_unit=utf16_code_unit`, SHA-256 / UTF-8 / lowercase-hex hash metadata, no Unicode normalization, no newline normalization, trailing-newline preservation, and 15 synthetic vectors covering empty, ASCII, Japanese, full-width, emoji surrogate pair, mixed Japanese/emoji, combining sequence, precomposed accent, LF, CRLF, trailing newline, tab, invalid surrogate boundary, invalid beyond-length, and compact mixed Unicode cases.

This step creates fixture data only. It does not implement TypeScript helpers, Rust helpers, test code, CI, Makefile targets, release-quality checks, schema implementation, runtime implementation, validator implementation, or event durability queue / IndexedDB / acknowledgement / retry / deduplication.

## 22. Step-web-logger-005 Vector Fixture Validator Design

Step-web-logger-005 is recorded in `docs/web_logger_unicode_hash_vector_fixture_validator_design.md`.

It designs a future public-safe validator for `tests/fixtures/web_logger_unicode_hash_vectors/vectors.json`, including top-level metadata checks, vector-level checks, UTF-16 length checks, UTF-8 byte length checks, SHA-256 hash checks, offset mapping checks, expected failure checks, forbidden marker scans, diagnostics, failure semantics, future focused tests, and future Makefile / release-quality staging. It remains validator-design / docs-only and does not implement a validator, change fixture JSON, add tests, add CI, add Makefile targets, or add release-quality checks.

## 23. Step-web-logger-006 Vector Fixture Validator Implementation

Step-web-logger-006 adds `python/web_logger_unicode_hash_vector_validation.py` and `python/test_support/tests/test_web_logger_unicode_hash_vector_validation.py`.

The validator makes the Step-web-logger-004 fixture checks repeatable for metadata, hashes, lengths, offset mappings, expected failures, and public-safe summary behavior. It does not implement TypeScript or Rust helpers, change fixture JSON, add Makefile / release-quality integration, add CI, or implement event durability.

## 24. Step-web-logger-007 Vector Validator Makefile Target Design

Step-web-logger-007 is recorded in `docs/web_logger_unicode_hash_vector_validator_makefile_target_design.md`.

It designs a future standalone Makefile target for the Step-web-logger-006 validator:

```text
check-web-logger-unicode-hash-vector-fixtures
```

The design fixes the proposed command, help text, placement, expected metadata/count-only output, failure semantics, preconditions, future Step-web-logger-008 checks, and later release-quality staging. It does not add the Makefile target, release-quality integration, CI workflow changes, TypeScript/Rust helpers, fixture JSON changes, or event durability.

## 25. Step-web-logger-008 Vector Validator Makefile Target

Step-web-logger-008 adds the standalone Makefile target `check-web-logger-unicode-hash-vector-fixtures`.

The target runs the Step-web-logger-006 Python validator against `tests/fixtures/web_logger_unicode_hash_vectors/vectors.json` with `--summary-only`. It makes the shared vector fixture validation available through Makefile while keeping release-quality integration, CI workflow integration, TypeScript/Rust helper implementation, fixture JSON changes, and event durability out of scope.

## 26. Step-web-logger-009 Vector Validator Release-Quality Integration Design

Step-web-logger-009 is recorded in `docs/web_logger_unicode_hash_vector_validator_release_quality_integration_design.md`.

It designs future release-quality integration for the Makefile-targeted vector validator while keeping wrapper changes for Step-web-logger-010. It does not add release-quality integration, CI workflow changes, TypeScript/Rust helper implementation, fixture JSON changes, or event durability.

## 27. Step-web-logger-010 Vector Validator Release-Quality Integration

Step-web-logger-010 adds `release_quality_check: web logger unicode hash vector fixture validation` to `scripts/check_release_quality.sh`.

The wrapper calls `make check-web-logger-unicode-hash-vector-fixtures`, so shared vector validation is now part of local release-quality checks. This does not implement TypeScript/Rust helpers, cross-language vector checks, CI workflow changes, fixture JSON changes, or event durability.

## 28. Step-web-logger-011 Remote/Manual Run Record Workflow Design

Step-web-logger-011 adds [Web Logger Unicode and Hash Vector Validator Release Quality Remote/Manual Run Record Workflow](web_logger_unicode_hash_vector_validator_release_quality_remote_run_record_workflow.md). It designs future public-safe status recording for the release-quality-integrated vector validator while keeping the shared vector fixture, TypeScript/Rust helper work, and event durability implementation unchanged.

## 29. Step-web-logger-012 Remote Status Marker

Step-web-logger-012 adds [Web Logger Unicode and Hash Vector Validator Release Quality Remote Run Status](status/web_logger_unicode_hash_vector_validator_release_quality_remote_run_status.md). It records remote release-quality status for the shared vector validator using metadata-only and count-only evidence. The marker does not change vectors, compute new hashes, implement TypeScript/Rust helper checks, or implement event durability.

## 30. Step-web-logger-013 Final Safety Review

Step-web-logger-013 adds [Web Logger Unicode and Hash Vector Validator Release Quality Chain Final Safety Review](web_logger_unicode_hash_vector_validator_release_quality_chain_final_safety_review.md). It accepts the fixed 15-vector fixture only as part of the release-quality-integrated, remote-status-recorded Python validator boundary.

## 31. Step-web-logger-014 Rust UTF-16 Offset Conversion Helper Design

Step-web-logger-014 adds [Rust UTF-16 Offset Conversion Helper Design for Web Logger Events](web_logger_rust_utf16_offset_conversion_helper_design.md). It plans how future Rust tests should reuse the shared Unicode/hash vectors for UTF-16 offset to UTF-8 byte boundary conversion without modifying `vectors.json`.

## 32. Step-web-logger-015 Rust UTF-16 Offset Conversion Helper

Step-web-logger-015 adds a focused Rust helper and tests for UTF-16 code unit offset to UTF-8 byte offset conversion in `kslog_replay`.

The focused tests reuse `tests/fixtures/web_logger_unicode_hash_vectors/vectors.json` directly where practical, checking valid offset mappings and expected invalid offset cases without changing the fixture. This is Rust helper utility coverage only; it is not TypeScript/Rust cross-language vector check coverage, Rust SHA-256 helper work, TypeScript SHA-256 helper work, broader replay/runtime integration, or event durability.

## 33. Step-web-logger-016 Rust Helper Makefile Target Design

Step-web-logger-016 adds [Rust UTF-16 Offset Conversion Helper Makefile Target Design](web_logger_rust_utf16_offset_conversion_helper_makefile_target_design.md).

The design keeps shared vector reuse in the focused Rust tests and proposes `cargo test -p kslog_replay utf16` as the future standalone Makefile target command. It does not change vector fixture data, Rust tests, Makefile, release-quality wrapper, or TypeScript/Rust cross-language checks.
