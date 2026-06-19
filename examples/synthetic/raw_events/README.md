# Synthetic Raw Event Examples

All JSONL files in this directory are synthetic public examples.

They are not real participant data, not experimental production data, and not derived from any real writing session. Do not place real browser logs, institution-controlled data, participant exports, names, email addresses, school names, addresses, or real participant IDs in this directory.

Each `.jsonl` line is intended to represent one `RawEvent` object from `crates/kslog_schema`.

Valid examples do not include no-oracle forbidden fields such as `final_text`, `observed_after_text`, or `gold_label`.

These examples are for documentation and future manual inspection. Test fixtures live under `tests/fixtures/synthetic/raw_events/`.

