# Synthetic Raw Event Test Fixtures

All files in this directory are synthetic test fixtures.

They are not real participant data, not experimental production data, and not derived from any real writing session. Do not place real browser logs, institution-controlled data, participant exports, names, email addresses, school names, addresses, or real participant IDs here.

## Directory Layout

- `valid/`: JSONL files whose individual lines should deserialize as `RawEvent`.
- `invalid/`: JSONL files reserved for future `kslog_validate` tests.

## Valid Fixtures

Valid fixtures must not contain no-oracle forbidden fields:

- `final_text`
- `observed_after_text`
- `gold_label`
- teacher corrections
- human corrections after writing
- post-hoc annotations

## Invalid Fixtures

Invalid fixtures intentionally contain malformed JSON, missing required schema fields, forbidden unknown fields, or cross-field problems such as sequence gaps and cursor range errors.

The cross-field invalid cases are not fully checked by `kslog_schema`. They are stored here for future validator tests.

