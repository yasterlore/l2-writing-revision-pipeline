# System Architecture

## TypeScript

TypeScript is used only in `apps/logger-web/`.

Allowed responsibilities:

- Browser-side raw event collection.
- Event serialization.
- Local logger UI needed for collection.

Forbidden responsibilities:

- Revision-event extraction.
- Micro-episode construction.
- Candidate generation.
- Candidate ranking.
- Learner-state estimation.

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
