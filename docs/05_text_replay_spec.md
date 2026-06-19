# Text Replay Spec

This file defines the documentation home for deterministic text replay.

No replay logic is implemented yet.

## Planned Responsibility

Text replay will reconstruct text states from validated raw events.

## Authoritative Layer

Rust is authoritative for replay. Python may inspect replay outputs for analysis but must not become the validation source of truth.

## Planned Tests

Replay tests should eventually include:

- valid insertion sequences
- deletion sequences
- cursor movement
- replacement behavior
- malformed events
- timestamp anomalies
- adversarial JSONL
- Unicode and IME edge cases
