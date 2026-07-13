# Web Logger Unicode and Hash Vectors

This fixture root contains shared synthetic Unicode / UTF-16 position / text hash vectors for future TypeScript Web logger and Rust replay / validation checks.

## Purpose

The vectors fix public-safe input data for future checks of:

- browser-originated UTF-16 code unit offsets
- expected UTF-8 byte offset mappings
- SHA-256 text hash canonicalization over decoded stored text
- invalid offset fail-closed metadata
- TypeScript / Rust cross-language consistency checks

This root provides fixture data only. It does not implement TypeScript helpers, Rust helpers, tests, CI, Makefile targets, or release-quality checks.

## Synthetic-Only Policy

All `source_text` and `expected_selected_text` values are short synthetic examples.

This fixture root contains:

- no real participant data
- no private text
- no private paths
- no absolute local paths
- no raw event payload bodies
- no logits or probabilities
- no performance metric bodies

## Position Unit Policy

The vector set declares:

- `position_unit=utf16_code_unit`

Future TypeScript checks should treat offsets as JavaScript-style UTF-16 code unit offsets. Future Rust checks must not treat these offsets as UTF-8 byte indices directly.

For each valid `offset_cases` entry:

- `utf16_start` and `utf16_end` are UTF-16 code unit offsets.
- `expected_utf8_start_byte` and `expected_utf8_end_byte` are UTF-8 byte offsets after decoding `source_text`.
- offsets must map to valid Rust `char` boundaries.
- offsets must not be rounded or repaired.

## Hash Canonicalization Policy

The vector set declares:

- `hash_algorithm=SHA-256`
- `hash_encoding=UTF-8`
- `unicode_normalization=none`
- `newline_normalization=none`
- `trailing_newline_policy=preserve_as_is`
- `hash_output_format=lowercase_hex`

`hash_sha256_utf8_lowercase_hex` is computed over the decoded `source_text` bytes, not over JSON escaping and not over the event JSON object.

## Newline, Tab, and Unicode Policy

The vectors preserve stored text exactly as represented after JSON decoding:

- no Unicode normalization
- no CRLF / LF / CR normalization
- trailing newline preserved
- tab treated as one UTF-16 code unit
- grapheme cluster display length is not the stored offset unit

Combining sequence cases may include code-unit-valid offsets that split a user-perceived grapheme. Those cases are marked with grapheme-sensitive notes but are not invalid under the base UTF-16 / UTF-8 boundary policy.

## Vector Schema Fields

Top-level metadata includes:

- `vector_schema_version`
- `position_unit`
- `hash_algorithm`
- `hash_encoding`
- `unicode_normalization`
- `newline_normalization`
- `trailing_newline_policy`
- `hash_output_format`
- `source_text_policy`
- `real_data_allowed`
- `non_real_data_notice`
- `no_oracle_notice`
- `generated_by`
- `reviewed_by`
- `vectors`

Each vector includes:

- `vector_id`
- `category`
- `priority`
- `source_text`
- `source_text_description`
- `utf16_code_unit_length`
- `utf8_byte_length`
- `code_point_count`
- `grapheme_cluster_note`
- `hash_sha256_utf8_lowercase_hex`
- `offset_cases`
- `expected_failures`
- `notes`

Each valid offset case includes UTF-16 input offsets, expected UTF-8 byte offsets, expected selected synthetic text, expected status, reason code, and a public-safe note.

Each expected failure includes offset metadata, expected validation status, reason code, `raw_text_emission_allowed=false`, and a public-safe note.

## Future TypeScript / Rust Consumption

Future TypeScript checks should:

- parse `vectors.json`
- verify JavaScript-style UTF-16 code unit lengths
- compute SHA-256 UTF-8 lowercase hex over decoded `source_text`
- verify selected spans under JavaScript string offset semantics
- emit metadata-only summaries

Future Rust checks should:

- parse `vectors.json`
- validate vector schema metadata
- convert UTF-16 code unit offsets to UTF-8 byte offsets with a shared helper
- verify expected byte offsets for valid cases
- reject invalid cases fail-closed
- compute SHA-256 UTF-8 lowercase hex over decoded `source_text`
- emit metadata-only diagnostics without raw event payload bodies

## Invalid Vector Behavior

Invalid offsets are represented in `expected_failures`.

Future validators should fail closed for:

- offsets inside UTF-16 surrogate pairs
- offsets beyond UTF-16 length
- ranges where start is greater than end

Failure diagnostics should include vector id, case/failure id, field names, and reason codes only. They should not emit raw event payload bodies or private data.

## Non-Claims

This fixture root does not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- Unicode correctness implementation completion
- hash compatibility implementation completion
- TypeScript / Rust helper implementation completion
- event durability implementation completion
- data collection readiness
- deployment readiness

## Recommended Future Implementation Steps

Recommended next steps:

1. Add a small validator for this fixture root.
2. Implement a Rust UTF-16 code unit to UTF-8 byte offset helper.
3. Implement TypeScript and Rust SHA-256 UTF-8 lowercase-hex helpers.
4. Add shared vector tests in TypeScript and Rust.
5. Add standalone Makefile targets only after helper tests are stable.
6. Consider release-quality integration only after standalone checks are reviewed.
7. Keep event durability queue / IndexedDB / acknowledgement / retry / deduplication as a separate implementation track.
