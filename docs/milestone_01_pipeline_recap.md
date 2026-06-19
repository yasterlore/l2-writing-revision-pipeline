# Milestone 01 Pipeline Recap

This document summarizes the current research-software foundation after Steps 1-27.

It is written as a beginner-friendly map of what exists, why each layer exists, and what is intentionally not implemented yet.

## 1. Project Purpose

This project studies keystroke-level writing process data from L2 English free-writing tasks.

The goal is to build a reproducible pipeline from browser-observed raw events to revision-process analysis units, no-oracle candidate generation, OT-inspired scoring prototypes, and eventually learner-state estimation.

This project is not:

- an automatic essay scoring system
- a grammar-correction product
- a teacher replacement
- a learner-state estimator yet
- a production data-processing system yet

At this milestone, the repository is a synthetic-only research pipeline foundation.

## 2. Language Architecture

### TypeScript

TypeScript is used only for the browser logger in `apps/logger-web/`.

It may:

- observe browser textarea events
- create RawEvent-like JSONL
- download synthetic manual test logs

It must not:

- validate JSONL authoritatively
- replay text
- extract revision events
- build micro-episodes
- generate candidates
- rank candidates
- estimate learner state

### Rust

Rust is the deterministic validation and transformation layer.

Rust owns:

- `kslog_schema`: RawEvent schema
- `kslog_validate`: JSONL/schema/order/range validation
- `kslog_replay`: deterministic text replay
- `kslog_extract`: RevisionEvent extraction
- `kslog_micro_episode`: MicroEpisode construction
- `kslog_no_oracle_audit`: no-oracle audit and safe view
- `kslog_cli`: command-line access to Rust stages

### Python

Python is for exploratory modeling and analysis prototypes.

Python currently owns:

- candidate generation placeholder prototype
- candidate feature extraction
- constraint violation schema
- weighted OT scoring prototype

Python does not perform authoritative raw-event validation.

## 3. Current Pipeline

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
```

Synthetic E2E scripts connect the current Rust and Python stages:

```bash
scripts/run_synthetic_e2e_pipeline.sh tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl deletion_case
scripts/run_synthetic_e2e_summary.sh
```

These scripts print summary-only status. They do not print JSONL rows.

## 4. Layer-by-Layer Beginner Map

### RawEvent JSONL

Input: browser event records, one JSON object per line.

Output: unprocessed event stream.

Why it exists: it preserves observed writing-process events before interpretation.

Where bugs are caught: Rust schema and validator reject malformed or unsafe records.

### Validation

Input: RawEvent JSONL.

Output: validation report or error.

Why it exists: it checks JSONL structure, sequence order, timestamps, cursor ranges, selection ranges, unknown fields, and no-oracle forbidden fields.

Where bugs are caught: malformed JSON, missing required fields, sequence gaps, timestamp inversions, invalid cursor/selection ranges.

### Replay

Input: validated RawEvent sequence.

Output: reconstructed document-state summary.

Why it exists: later revision extraction needs deterministic text-state reconstruction.

Where bugs are caught: document length mismatches, deleted-text mismatches, cursor/selection assumptions.

Privacy note: replay output can contain text, so repository docs and committed outputs must not store real-data replay text.

### RevisionEvent Extraction

Input: RawEvent sequence.

Output: observed edit-action records such as insertion, deletion, selection-range edit, paste, and composition commit.

Why it exists: RawEvent is too low-level for revision-process analysis.

Important limitation: RevisionEvent is an observed-action category, not a correctness label.

### MicroEpisode Construction

Input: RevisionEvent plus replayed local context.

Output: local analysis unit centered on one observed edit.

Why it exists: later candidate generation and scoring need a compact episode representation.

No-oracle warning: `local_context_after_observed` may exist for reconstruction/evaluation checks, but it is unsafe for candidate generation or ranking.

### No-Oracle Audit and Safe View

Input: RawEvent, RevisionEvent, or MicroEpisode structures.

Output: audit reports and `NoOracleSafeEpisodeView`.

Why it exists: candidate generation and ranking must not accidentally use future or gold information.

Safe view role: it removes post-edit context and forbidden fields before Python candidate generation.

### Candidate Generation

Input: `NoOracleSafeEpisodeView` JSONL.

Output: `CandidateSet` JSONL.

Why it exists: it proposes possible action candidates before scoring.

Current limitation: candidates are placeholders, not real grammar corrections and not ranked hypotheses.

### Candidate Features

Input: `CandidateSet` JSONL.

Output: `CandidateFeatureSet` JSONL.

Why it exists: it turns candidates into simple structural features for scoring.

Privacy note: it does not include writing text, local context text, proposed edit payloads, or observed edit text.

### Constraint Violations

Input: `CandidateFeatureSet` JSONL.

Output: `ConstraintViolationSet` JSONL.

Why it exists: it records penalty and descriptive constraints before scoring.

Current limitation: it does not apply learned weights or evaluate correctness.

### Weighted Scoring Prototype

Input: `ConstraintViolationSet` JSONL.

Output: `CandidateScoreSet` JSONL.

Why it exists: it gives a deterministic prototype score and rank for each candidate.

Important limitation: ranking is not a correctness claim. It is not evaluation.

## 5. No-Oracle Policy

Candidate generation, ranking, scoring, and learner-state estimation must not use:

- `final_text`
- `observed_after_text`
- `gold_label`
- teacher corrections
- human corrections after writing
- answer keys
- future edits
- post-hoc annotations

`local_context_after_observed` is unsafe for candidate generation, ranking, OT scoring, and learner-state estimation. It may exist for replay verification or later evaluation boundaries, but it must not enter safe candidate input.

`NoOracleSafeEpisodeView` is the boundary object for Python candidate generation.

## 6. Synthetic-Only Policy

During development, this repository uses synthetic data only.

Allowed:

- `examples/synthetic/`
- `tests/fixtures/synthetic/`
- synthetic manual tests kept outside Git

Forbidden:

- real participant data
- production writing logs
- actual student text
- private institutional data

`manual_outputs/` and `tmp/` are Git-ignored. They must not be committed.

Real data may be introduced only after the full pipeline is mature and only in a private local or institution-approved environment.

## 7. Security and Privacy

Current safeguards:

- JSONL is treated as untrusted input.
- Rust validator rejects malformed and adversarial raw events.
- Unknown RawEvent fields are denied.
- No-oracle forbidden field checks exist in Rust, Python loaders, and CI policy scripts.
- CLI and E2E scripts print summaries rather than JSONL rows.
- Documentation must not contain JSONL bodies or real writing text.
- `apps/logger-web/` does not send data to a backend.
- `apps/logger-web/` does not use `localStorage` for long-term real-data persistence.
- CI uses synthetic fixtures only.

GitHub Actions currently runs:

```bash
cargo fmt --all -- --check
cargo test --workspace
cargo clippy --workspace -- -D warnings
scripts/check_synthetic_policy.sh
scripts/run_synthetic_e2e_pipeline.sh tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl deletion_case_ci
```

## 8. What Currently Works

You can:

- run the TypeScript logger foundation locally
- download synthetic manual raw-event JSONL
- validate synthetic RawEvent JSONL with Rust
- replay synthetic text process events with Rust
- extract RevisionEvent records
- build MicroEpisode records
- audit no-oracle safety
- export `NoOracleSafeEpisodeView` JSONL
- generate placeholder candidate sets in Python
- extract structural candidate features
- build constraint-violation records
- create prototype weighted candidate scores
- run a synthetic E2E pipeline
- run a summary-only collector across valid synthetic fixtures
- run CI smoke checks

## 9. What Is Not Implemented Yet

Not implemented:

- production data handling
- real participant data processing
- evaluation schema
- F1, accuracy, calibration, or selective prediction
- learner-state estimation
- full grammar-aware candidate generation
- learned OT weights
- model calibration
- backend ingestion
- database storage
- deployment workflow

## 10. Suggested Next Steps

Possible next milestones:

- define evaluation schema without leaking oracle information
- add synthetic gold-like expected-action fixtures for testing evaluation mechanics
- refine scoring policy and blocking behavior
- add scorer output summary tools
- improve logger browser/event coverage
- decide whether to add the full summary collector to CI or keep it local
- document private-environment requirements before any real-data trial

## 11. Quick Commands

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

Run synthetic policy:

```bash
scripts/check_synthetic_policy.sh
```

Run one E2E case:

```bash
scripts/run_synthetic_e2e_pipeline.sh tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl deletion_case
```

Run all valid synthetic cases:

```bash
scripts/run_synthetic_e2e_summary.sh
```

Remember: these commands are synthetic-only connection checks, not evaluation.
