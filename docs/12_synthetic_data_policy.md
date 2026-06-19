# Synthetic Data Policy

All development and testing must use synthetic data only.

## Allowed Locations

Synthetic examples may live in:

- `examples/synthetic/`
- `tests/fixtures/synthetic/`

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
