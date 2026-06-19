# L2 Writing Revision Pipeline

This repository is for collecting and analyzing keystroke-level writing process data from L2 English free-writing tasks.

The intended research pipeline runs from raw browser events to deterministic validation, text replay, revision events, micro-episodes, no-oracle candidate generation, OT-inspired ranking, evaluation, and learner-state estimation.

This repository currently contains structure, policies, documentation templates, and project foundations only. It intentionally does not implement the logger, replay engine, revision extraction, micro-episode construction, candidate generation, ranking, evaluation, or learner-state estimation logic yet.

## Language Boundaries

TypeScript is reserved for the browser logger only. It may collect raw browser-side events, but it must not extract revision events, construct micro-episodes, generate candidates, rank candidates, or estimate learner state.

Rust is the authoritative deterministic layer. Validation, text replay, revision-event extraction, micro-episode construction, no-oracle audit, and CLI tools belong in Rust.

Python is for exploratory modeling and analysis. Candidate generation prototypes, OT scorer experiments, evaluation, learner-state estimation, and visualization belong in Python. Python must not become the authoritative raw-event validation layer.

## Data Policy

All development and testing in this repository must use synthetic data only.

Real participant data must never be committed, read, inspected, transformed, summarized, or written by Codex in this repository. Real-data testing may happen only after the full pipeline passes synthetic-data validation, and only in a private local or institution-approved environment.

## Repository Map

```text
apps/logger-web/                  TypeScript browser logger foundation
crates/                           Rust deterministic pipeline crates
python/                           Python exploratory modeling and analysis
docs/                             Architecture, policy, and component specs
examples/synthetic/               Synthetic examples only
tests/fixtures/synthetic/         Synthetic test fixtures only
```

## Current Status

Foundation-only repository. See `docs/00_project_overview.md` and `docs/codex_workflow.md` before adding implementation.

## CI

GitHub Actions runs the Rust workspace checks on push and pull request:

```bash
cargo fmt --all -- --check
cargo test --workspace
cargo clippy --workspace -- -D warnings
scripts/check_synthetic_policy.sh
```

CI uses synthetic fixtures only. It does not process production data or real participant data.

The synthetic policy check rejects private/real-data-looking paths and checks public synthetic examples plus valid fixtures for no-oracle forbidden fields such as `final_text`, `observed_after_text`, `gold_label`, `teacher_correction`, `answer_key`, and `future_context`. Invalid fixtures are excluded because some intentionally contain forbidden examples for validator tests.
