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

## CI Checks

GitHub Actions runs:

- `cargo fmt --all -- --check`
- `cargo test --workspace`
- `cargo clippy --workspace -- -D warnings`
- `scripts/check_synthetic_policy.sh`
- CLI smoke tests on synthetic valid and invalid fixtures

CI uses synthetic data only. It must not process production data, real participant data, `private_data/`, `real_data/`, or `participant_data/`.

The synthetic policy script checks public synthetic examples and valid fixtures for no-oracle forbidden fields. It intentionally excludes invalid fixtures because they include adversarial examples such as forbidden field names.

Before opening a PR, run the same commands locally when possible.
