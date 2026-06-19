# L2 Writing Revision Pipeline

Research software for studying keystroke-level L2 English free-writing revision processes.

This repository builds a reproducible, synthetic-only pipeline from browser raw events to deterministic replay, revision events, micro-episodes, no-oracle candidate generation, OT-inspired scoring prototypes, synthetic evaluation wiring, and config-aware diagnostic infrastructure.

It is not:

- an automatic essay scorer
- a grammar-correction product
- a learner-state estimator yet
- a production data-processing system
- a repository for real participant data

## Current Pipeline

```text
RawEvent JSONL
  -> Rust validation
  -> Rust replay
  -> Rust revision_event extraction
  -> Rust micro_episode construction
  -> Rust no-oracle audit
  -> Rust NoOracleSafeEpisodeView export
  -> Python CandidateSet
  -> Python CandidateFeatureSet
  -> Python ConstraintViolationSet
  -> Python CandidateScoreSet
  -> optional synthetic expected-action evaluation
  -> summary-only synthetic E2E collector
```

The synthetic evaluation wiring is a connection check. It is not production evaluation and does not report F1, accuracy, calibration, or learner-state estimates.

Config-aware scoring support is explicit-only. It is diagnostic infrastructure,
not performance evaluation. The no-config default path remains the protected
baseline.

## Language Architecture

TypeScript is for the browser logger only:

- collect browser-side raw events
- download RawEvent-like JSONL for synthetic/manual testing
- do not validate authoritatively
- do not replay text
- do not extract revision events
- do not generate or rank candidates

Rust is the authoritative deterministic layer:

- `kslog_schema`
- `kslog_validate`
- `kslog_replay`
- `kslog_extract`
- `kslog_micro_episode`
- `kslog_no_oracle_audit`
- `kslog_cli`

Python is for exploratory modeling and analysis prototypes:

- candidate generation
- candidate feature extraction
- constraint violation records
- weighted scoring prototype
- synthetic evaluation schema
- future visualization and learner-state experiments

## Safety Policy

This repository is synthetic-only.

- Do not commit real participant data.
- Do not place real participant data in `examples/` or `tests/fixtures/`.
- Do not paste JSONL rows or participant text into docs.
- Do not commit outputs from `manual_outputs/` or `tmp/`.
- Do not ask Codex to read, inspect, transform, summarize, or write real participant data.
- Real-data trials, if they ever happen, must be private/local or institution-approved and must follow [the private real-data readiness checklist](docs/private_real_data_readiness_checklist.md).

## No-Oracle Policy

Candidate generation, scoring, ranking, and learner-state work must not use:

- `final_text`
- `observed_after_text`
- `gold_label`
- teacher correction
- human correction after writing
- answer key
- future edits
- post-hoc annotations
- `local_context_after_observed`

Synthetic expected actions are used only after scoring for synthetic evaluation checks. They must not flow into candidate generation, feature extraction, constraints, scoring, or ranking.

## Quick Start

Run Rust checks:

```bash
cargo fmt --all -- --check
cargo test --workspace
cargo clippy --workspace -- -D warnings
```

Run Python checks:

```bash
PYTHONPATH=python python3 -m unittest discover -s python
PYTHONPATH=python python3 -m compileall python
```

Run logger-web checks:

```bash
cd apps/logger-web
npm run typecheck
npm test
npm run build
```

Run synthetic policy checks:

```bash
scripts/check_synthetic_policy.sh
```

Run one synthetic E2E case:

```bash
scripts/run_synthetic_e2e_pipeline.sh tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl deletion_case
```

Run all valid synthetic raw-event fixtures with summary-only output:

```bash
scripts/run_synthetic_e2e_summary.sh
```

Outputs go under `tmp/`, which is Git-ignored.

Run optional diagnostic/config smoke checks:

```bash
scripts/check_no_config_scoring_fixture_lock.sh
scripts/check_hand_weight_config_validation.sh
scripts/check_explicit_config_ranking_diff.sh
scripts/check_config_enabled_e2e_smoke.sh
scripts/check_config_enabled_summary_smoke.sh
scripts/check_synthetic_diagnostic_distribution.sh
```

These checks are synthetic-only wiring and regression checks, not performance
metrics.

## What Is Implemented

- TypeScript logger-web foundation
- Rust RawEvent schema
- Rust JSONL validation
- Rust text replay
- Rust revision_event extraction
- Rust micro_episode construction
- Rust no-oracle audit
- Rust NoOracleSafeEpisodeView export
- Rust CLI tools
- Python candidate generation prototype
- Python CandidateFeatureSet extraction
- Python ConstraintViolationSet generation
- Python CandidateScoreSet weighted scoring prototype
- Python synthetic evaluation schema
- synthetic expected action registry
- synthetic E2E pipeline and summary collector
- diagnostic summary tooling
- hand-weight config validation
- explicit `score.py --weight-config` path
- config-enabled E2E and separate config-enabled summary collector
- observation note templates and storage/review workflow
- GitHub Actions CI for Rust checks, policy checks, CLI smoke tests, and one synthetic E2E smoke test

## What Is Not Implemented

- production data processing
- real participant data processing
- real gold label workflow
- public dataset release
- F1, accuracy, calibration, or selective prediction
- learner-state estimation
- automatic weight learning
- private validation
- backend ingestion
- database storage
- cloud deployment
- real-data CI

## Documentation Map

- [Documentation index](docs/README.md)
- [Milestone 01 pipeline recap](docs/milestone_01_pipeline_recap.md)
- [Milestone 02 synthetic evaluation recap](docs/milestone_02_synthetic_evaluation_recap.md)
- [Milestone 03 config-aware diagnostic infrastructure recap](docs/milestone_03_config_aware_diagnostic_infrastructure_recap.md)
- [Private real-data readiness checklist](docs/private_real_data_readiness_checklist.md)
- [No-oracle policy](docs/03_no_oracle_policy.md)
- [Synthetic data policy](docs/12_synthetic_data_policy.md)
- [Synthetic E2E pipeline](docs/synthetic_e2e_pipeline.md)
- [Evaluation spec](docs/evaluation_spec.md)
- [Scoring policy refinement plan](docs/scoring_policy_refinement_plan.md)
- [Public release checklist](docs/public_release_checklist.md)
- [Security policy](SECURITY.md)

## CI

GitHub Actions runs:

```bash
cargo fmt --all -- --check
cargo test --workspace
cargo clippy --workspace -- -D warnings
scripts/check_synthetic_policy.sh
cargo run -p kslog_cli -- validate tests/fixtures/synthetic/raw_events/valid/simple_typing.jsonl
scripts/run_synthetic_e2e_pipeline.sh tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl deletion_case_ci
```

CI uses synthetic fixtures only. It must not process real participant data.

## License

The license is not finalized yet.

This project is under active research-software development. `LICENSE` is a
placeholder, not a final open-source license. Until a final license is selected
and the placeholder is replaced, reuse terms are not finalized.

A final license must be chosen before formal public release. See
[the public release checklist](docs/public_release_checklist.md).

## Security and Privacy

See [SECURITY.md](SECURITY.md). Treat all JSONL input as untrusted, keep real data out of this repository, and do not publish logs, screenshots, derived outputs, or reports that may contain participant text.
