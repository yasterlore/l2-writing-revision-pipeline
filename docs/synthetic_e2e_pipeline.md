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

## Summary Collector

To run every synthetic valid raw-event fixture and print a summary-only table:

```bash
scripts/run_synthetic_e2e_summary.sh
```

You can also pass an explicit synthetic fixture directory:

```bash
scripts/run_synthetic_e2e_summary.sh tests/fixtures/synthetic/raw_events/valid
```

The collector runs `scripts/run_synthetic_e2e_pipeline.sh` once per `.jsonl` file. The case name is the file stem.

It writes a CSV summary to:

```text
tmp/synthetic_e2e_summary/summary.csv
```

The collector records:

- `case_name`
- `pipeline_status`
- `failed_stage`
- `output_dir`
- `score_sets_count`
- `candidates_count`
- `blocked_candidates_count`
- `unblocked_candidates_count`
- `rank1_available`
- `content_suppressed`

The collector is not evaluation. It does not calculate F1, accuracy, calibration, selective prediction, or learner-state estimates.

It must not be run on `manual_outputs/`, `private_data/`, `real_data/`, or `participant_data/`.

## Output Location

Outputs are written under:

```text
tmp/synthetic_e2e/<case_name>/
```

`tmp/` is Git-ignored. Do not add generated JSONL outputs to Git.

The summary collector also writes under:

```text
tmp/synthetic_e2e_summary/
```

This directory is Git-ignored as part of `tmp/`.

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

The summary collector also suppresses JSONL contents. It may count structural fields in `candidate_scores.jsonl`, but it does not print candidate descriptions, contexts, proposed edits, final text, or JSONL rows.

## What This Is Not

This pipeline is not evaluation. It does not calculate F1, calibration, selective prediction, learner-state estimates, or model performance.

The weighted score and rank are prototype outputs. They are deterministic analysis artifacts, not gold labels and not proof that a candidate is correct.
