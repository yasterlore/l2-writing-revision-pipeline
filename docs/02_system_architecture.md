# System Architecture

## TypeScript

TypeScript is used only in `apps/logger-web/`.

Allowed responsibilities:

- Browser-side raw event collection.
- Event serialization.
- Local logger UI needed for collection.
- In-memory JSONL download for synthetic manual testing.

Forbidden responsibilities:

- Revision-event extraction.
- Micro-episode construction.
- Candidate generation.
- Candidate ranking.
- Learner-state estimation.

The initial `apps/logger-web/` implementation is a Vite + plain TypeScript app. It observes textarea events and emits RawEvent-like JSONL with synthetic metadata only. Rust remains authoritative for validation, replay, extraction, micro-episodes, no-oracle audit, and CLI processing.

## Rust

Rust is used in `crates/` and is authoritative for deterministic validation and transformation.

Planned crates:

- `kslog_schema`: shared schema definitions.
- `kslog_validate`: raw-event validation.
- `kslog_replay`: text replay.
- `kslog_extract`: revision-event extraction.
- `kslog_micro_episode`: micro-episode construction.
- `kslog_no_oracle_audit`: no-oracle compliance checks.
- `kslog_cli`: command-line tools.

`kslog_cli` is the initial command-line entry point for running validation, replay, revision-event extraction, micro-episode construction, no-oracle audit, and safe-view summary generation on synthetic JSONL fixtures.

Rust also exports `NoOracleSafeEpisodeView` JSONL as the boundary between deterministic replay-derived structures and Python exploratory candidate-generation prototypes.

## Python

Python is used in `python/` for exploratory research workflows.

Allowed responsibilities:

- Candidate generation prototypes.
- OT scorer experiments.
- Evaluation.
- Learner-state estimation.
- Visualization.

Forbidden responsibility:

- Authoritative raw-event validation.

Current Python prototypes include:

- `python/candidate_generation/`: placeholder `CandidateSet` generation from safe views.
- `python/ot_scorer/`: candidate feature extraction, constraint violation records, and weighted scoring prototype.

Python scoring outputs are prototype rankings, not correctness labels and not evaluation metrics.

## Synthetic E2E Script

`scripts/run_synthetic_e2e_pipeline.sh` connects the current Rust and Python prototype stages for synthetic fixtures:

1. Rust safe-view export.
2. Python candidate generation.
3. Python candidate feature extraction.
4. Python constraint violation generation.
5. Python weighted scoring prototype.

The script writes generated JSONL under `tmp/synthetic_e2e/<case_name>/`, which is Git-ignored. It prints summaries only and must not be used for production or real participant data in this repository.

For a detailed milestone recap, see `docs/milestone_01_pipeline_recap.md`.
