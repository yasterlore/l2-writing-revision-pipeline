# Raw Event Schema

This file defines the intended documentation home for browser-side raw event schemas.

No schema is implemented yet.

## Planned Requirements

Raw events must eventually document:

- event type
- timestamp source and precision
- session identifier
- task identifier
- browser context metadata allowed for research
- text-input event details
- composition and IME behavior
- focus and blur events
- clipboard-related policy
- validation rules

## Security Notes

Raw JSONL input must be treated as untrusted. Validation must reject malformed, oversized, impossible, or adversarial events.

## Data Notes

Examples and fixtures for this schema may contain synthetic data only.
