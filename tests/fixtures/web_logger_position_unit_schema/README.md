# Web Logger Position Unit Schema Fixtures

This fixture root contains synthetic fixture cases for future schema-level
`position_unit=utf16_code_unit` validation of Web logger events.

## Purpose

These fixtures fix a valid / invalid / legacy matrix for future
`kslog_schema` and `kslog_validate` work. They are not consumed by the current
schema or validator implementation yet.

## Synthetic-Only And No-Oracle Boundary

All event text fragments are short synthetic examples created only to exercise
UTF-16 code unit behavior. This root contains no real participant data, no raw
learner text, no private paths, no absolute local paths, no raw logs, no full
job output, no logits or probabilities, and no performance metric bodies.

Forbidden no-oracle fields are not used:

- `final_text`
- `observed_after_text`
- `gold_label`
- `gold_labels`
- `post_hoc_annotation`

## Position Unit Policy

Future Web logger v0.2+ events in this root use:

- `position_unit=utf16_code_unit`
- `logger_schema_version=kslog.raw_event.v2`
- `research_schema_target=web_logger_position_unit_schema_v0.1`

Cursor, selection, and document length metadata are intended to be interpreted
as browser-originated UTF-16 code unit offsets. Unsupported position units,
missing position units in future schema versions, invalid UTF-16 boundaries,
and incompatible schema/version combinations should fail closed in future
schema / validator implementation.

Legacy cases live under `legacy/` and must not be treated as Web logger v0.2
valid cases.

## Layout

- `case_index.json`: metadata-only case index and expected reason-code matrix.
- `valid/`: JSONL cases expected to pass future position-unit validation.
- `invalid/`: JSONL cases expected to fail future position-unit validation.
- `legacy/`: explicitly gated legacy cases without `position_unit`.

Each case is one JSONL file. The JSONL bodies are intentionally not copied into
project docs.

## Case Counts

- valid cases: 5
- invalid cases: 11
- legacy cases: 1
- total cases: 17

## Valid Case Summary

- `valid_ascii_utf16_position_unit`
- `valid_japanese_cursor_utf16_position_unit`
- `valid_japanese_selection_utf16_position_unit`
- `valid_emoji_boundary_utf16_position_unit`
- `valid_mixed_japanese_emoji_utf16_position_unit`

All valid cases use explicit `position_unit=utf16_code_unit` and
`expected_reason_code=none`.

## Invalid Case Summary

- `invalid_v0_2_missing_position_unit`
- `invalid_unsupported_position_unit_byte_index`
- `invalid_unsupported_position_unit_code_point`
- `invalid_position_unit_schema_mismatch`
- `invalid_doc_len_before_utf16_mismatch`
- `invalid_doc_len_after_utf16_mismatch`
- `invalid_selection_start_greater_than_end`
- `invalid_offset_beyond_utf16_length`
- `invalid_surrogate_pair_internal_offset`
- `invalid_byte_index_supplied_as_utf16_when_detectable`
- `invalid_unknown_schema_version`

The byte-index misuse fixture uses a Japanese single-character state and a
cursor value that corresponds to UTF-8 byte length rather than UTF-16 code unit
length. The expected reason code is `offset_beyond_utf16_length`.

## Legacy Case Summary

- `legacy_missing_position_unit_explicitly_gated`

The legacy case intentionally omits `position_unit` and is expected to be
handled as `legacy_allowed` with reason code
`legacy_position_unit_missing_allowed` only when an explicit legacy gate is
active.

## Future Validator Usage

Future validators should read `case_index.json`, verify fixture paths exist,
parse each JSONL line, run schema / validator policy checks, compare
`expected_status` and `expected_reason_code`, and emit metadata-only summaries.

Expected public-safe output may include counts, case IDs, reason-code counts,
schema version, position-unit policy status, and content-suppression flags.
It must not include raw event bodies, full fixture bodies, selected text,
inserted/deleted text by default, private paths, raw learner text, real
participant data, logits, probabilities, or performance metric bodies.

## Relationships

Step-web-logger-032 defines the schema-level policy. This root implements the
fixture matrix from Step-web-logger-033.

Step-web-logger-031 accepted only the focused `kslog_replay` boundary. These
fixtures are for future schema / validator boundaries and do not prove replay,
extract, or micro_episode integration.

The focused Rust helper chain remains separate. These fixtures may use the same
Unicode categories conceptually, but helper evidence is not schema validation
evidence.

## Non-Claims

These fixtures do not claim production readiness, real-data readiness, model
performance, F1 / accuracy / ECE / AURCC achievement, broader Unicode
correctness completion, validate integration completion, extract integration
completion, micro_episode integration completion, schema-level position_unit
policy implementation, hash compatibility implementation completion,
TypeScript / Rust vector check implementation, current TypeScript/Rust hash
equality, event durability implementation, data collection readiness, or
deployment readiness.

## Future Staging

Recommended next step:

Step-web-logger-035: design schema-level position_unit fixture validator

Future implementation should add a validator design and then a validator or
schema implementation in separate steps. Do not move directly to TypeScript/Rust
hash checks, validate / extract / micro_episode integration, or event
durability.
