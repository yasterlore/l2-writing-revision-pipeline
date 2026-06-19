# Data Quality Policy

Data quality checks must begin with synthetic data.

## Raw Input Quality

Raw JSONL input must be treated as untrusted. Future validators should check:

- parse failures
- missing required fields
- unknown fields where disallowed
- timestamp monotonicity where required
- impossible cursor or text states
- oversized payloads
- invalid encodings
- adversarial structures

The first Rust validator lives in `crates/kslog_validate/`. It currently checks:

- one JSON object per JSONL line
- malformed JSON
- empty-line rejection by default
- maximum line size
- `kslog_schema::RawEvent` deserialization
- no-oracle forbidden fields
- consecutive `seq`
- monotonic non-decreasing `timestamp_ms`
- cursor positions against corresponding document lengths
- selection range ordering and bounds

It intentionally does not replay text or validate the semantic consistency of `inserted_text`, `deleted_text`, and `diff_op`.

The first Rust replay layer lives in `crates/kslog_replay/`. It checks replay-specific consistency after JSONL validation:

- `doc_len_before` against current replayed character count
- `doc_len_after` against updated replayed character count
- cursor and selection bounds used by replay
- selected text against `deleted_text` when present
- non-placeholder replay hash labels when present

Replay output may contain reconstructed writing. Do not commit replay output derived from real participant data.

## Derived Data Quality

Derived artifacts should document:

- source input hash or identifier
- validation status
- transformation version
- no-oracle audit status where applicable

## Testing

Malformed, adversarial, and invalid inputs should be covered when each implementation component is added.
