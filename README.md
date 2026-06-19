# L2 Writing Revision Pipeline

This repository is for collecting and analyzing keystroke-level writing process data from L2 English free-writing tasks.

The intended research pipeline runs from raw browser events to deterministic validation, text replay, revision events, micro-episodes, no-oracle candidate generation, OT-inspired ranking prototypes, evaluation, and learner-state estimation.

This is research software for studying revision processes in L2 English free writing. It is not an automatic scoring system and it does not make learner-state claims by itself.

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

Milestone 1 is a synthetic-only, no-oracle pipeline foundation:

- TypeScript browser logger foundation.
- Rust deterministic schema, validation, replay, extraction, micro-episode, no-oracle audit, safe-view export, and CLI tools.
- Python candidate generation, feature extraction, constraint violation, and weighted scoring prototypes.
- Synthetic E2E scripts and CI smoke checks.

Start with `docs/milestone_01_pipeline_recap.md` for a beginner-friendly recap.

Milestone 2 adds synthetic-only evaluation wiring:

- synthetic expected action schema
- explicit `CandidateScore.action_type`
- optional evaluation at the end of the synthetic E2E pipeline
- expected action registry for active, pending, and missing cases
- summary-only evaluation connection checks

See `docs/milestone_02_synthetic_evaluation_recap.md`. This is not production evaluation and does not report F1, accuracy, calibration, or learner-state estimates.

## Synthetic E2E Pipeline

The current synthetic-only Rust + Python prototype can be run end to end:

```bash
scripts/run_synthetic_e2e_pipeline.sh tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl deletion_case
```

Outputs are written under `tmp/synthetic_e2e/<case_name>/`, which is Git-ignored. The script is not for production data or real participant data. See `docs/synthetic_e2e_pipeline.md`.

To run all valid synthetic raw-event fixtures and print a summary-only connection check:

```bash
scripts/run_synthetic_e2e_summary.sh
```

The summary collector is not evaluation and does not report F1, accuracy, or calibration.

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

CI also runs one synthetic E2E smoke test:

```bash
scripts/run_synthetic_e2e_pipeline.sh tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl deletion_case_ci
```

This is a connection check, not evaluation. It does not report F1, accuracy, calibration, or learner-state estimates.
