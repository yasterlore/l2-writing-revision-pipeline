# Synthetic Data Policy

All development and testing must use synthetic data only.

## Allowed Locations

Synthetic examples may live in:

- `examples/synthetic/`
- `tests/fixtures/synthetic/`

Synthetic raw event JSONL examples and fixtures are organized as:

- `examples/synthetic/raw_events/`
- `tests/fixtures/synthetic/raw_events/valid/`
- `tests/fixtures/synthetic/raw_events/invalid/`

The `valid/` directory contains JSONL lines that should deserialize as `RawEvent`.

The `invalid/` directory contains malformed, forbidden-field, or cross-field-invalid cases for future validator tests. Some invalid files may still deserialize as `RawEvent` because cross-field validation belongs in `kslog_validate`, not `kslog_schema`.

## Disallowed Data

Do not commit:

- real participant data
- private participant data
- institution-controlled data
- exported browser logs from actual participants
- derived artifacts created from real participant data

## Naming Rules

The following filename patterns are treated as private or real-data indicators and are ignored by Git:

- `*.real.jsonl`
- `*.private.jsonl`
- `*.real.json`
- `*.private.json`
- `*.participant.jsonl`
- `*.participant.json`

## Codex Rule

Codex must not read, inspect, transform, summarize, or write real participant data.

Codex may work with the synthetic fixtures in this repository when the task explicitly concerns synthetic data or schema tests.
