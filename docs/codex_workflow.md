# Codex Workflow

Codex work in this repository must respect the project boundaries.

## Before Editing

- Confirm the task is inside this repository.
- Check whether the task touches real participant data. If yes, stop.
- Prefer synthetic examples and fixtures only.
- Avoid adding dependencies unless necessary.

## During Implementation

- TypeScript logger code must not perform downstream analysis.
- Rust owns deterministic validation and transformation.
- Python is exploratory and analytical.
- No-oracle components must not use forbidden future or gold fields.
- Treat all JSONL as untrusted.

## After Each Implementation Step

Run available:

- formatting
- linting
- tests
- dependency audit
- security audit

If a tool does not exist yet, document that it is unavailable rather than inventing a substitute.
