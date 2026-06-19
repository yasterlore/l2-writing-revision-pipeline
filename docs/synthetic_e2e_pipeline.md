# Synthetic E2E Pipeline

This document describes the synthetic-only Rust + Python E2E pipeline script.

The script is for synthetic fixtures only. Do not use it for production data or real participant data in this repository.

## Command

From the repository root:

```bash
scripts/run_synthetic_e2e_pipeline.sh tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl deletion_case
```

Usage:

```bash
scripts/run_synthetic_e2e_pipeline.sh <input_raw_events.jsonl> <case_name>
```

## Output Location

Outputs are written under:

```text
tmp/synthetic_e2e/<case_name>/
```

`tmp/` is Git-ignored. Do not add generated JSONL outputs to Git.

If the directory already exists, this first version may overwrite files with the same names:

- `safe_views.jsonl`
- `candidate_sets.jsonl`
- `candidate_features.jsonl`
- `constraint_violations.jsonl`
- `candidate_scores.jsonl`

## Pipeline Stages

1. Rust `kslog_cli export-safe-view`
   - Converts synthetic raw event JSONL into no-oracle-safe episode views.
   - Excludes observed edit text by default.

2. Python candidate generation
   - Creates placeholder `CandidateSet` JSONL.
   - Does not rank candidates.

3. Python feature extraction
   - Creates structural `CandidateFeatureSet` JSONL.
   - Does not include writing text, context text, or proposed edit payloads.

4. Python constraint generation
   - Creates unweighted `ConstraintViolationSet` JSONL.
   - Separates penalty constraints from descriptive constraints.

5. Python weighted scoring prototype
   - Creates `CandidateScoreSet` JSONL with prototype score and deterministic rank.
   - This is not evaluation and not a correctness claim.

## Privacy Rules

- Use synthetic data only.
- Do not use production data or real participant data.
- Do not paste JSONL contents into documentation.
- Do not commit generated outputs from `tmp/`.
- Do not process `private_data/`, `real_data/`, or `participant_data/`.

The script suppresses JSONL contents from stdout. It prints only stage summaries and output paths.

## What This Is Not

This pipeline is not evaluation. It does not calculate F1, calibration, selective prediction, learner-state estimates, or model performance.

The weighted score and rank are prototype outputs. They are deterministic analysis artifacts, not gold labels and not proof that a candidate is correct.
