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
scripts/run_synthetic_e2e_pipeline.sh <input_raw_events.jsonl> <case_name> [expected_actions.jsonl]
```

If `expected_actions.jsonl` is provided, the script runs the synthetic-only
evaluation prototype after scoring:

```bash
scripts/run_synthetic_e2e_pipeline.sh \
  tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl \
  deletion_case_with_eval \
  tests/fixtures/synthetic/expected_actions/valid/deletion_expected_actions.jsonl
```

If no expected action file is provided, the script behaves as before and stops
after writing `candidate_scores.jsonl`.

## Summary Collector

To run every synthetic valid raw-event fixture and print a summary-only table:

```bash
scripts/run_synthetic_e2e_summary.sh
```

You can also pass an explicit synthetic fixture directory:

```bash
scripts/run_synthetic_e2e_summary.sh tests/fixtures/synthetic/raw_events/valid
```

You can pass an explicit synthetic expected action registry as the second argument:

```bash
scripts/run_synthetic_e2e_summary.sh \
  tests/fixtures/synthetic/raw_events/valid \
  tests/fixtures/synthetic/expected_actions/registry.json
```

The collector runs `scripts/run_synthetic_e2e_pipeline.sh` once per `.jsonl` file. The case name is the file stem.

The collector looks up each case name in the synthetic expected action registry.
If the case is `active`, it passes the expected action fixture as the third
pipeline argument and records whether `evaluation_report.json` exists. If the
case is `pending` or `missing`, it runs the pipeline without evaluation and
records the skipped status.

Synthetic expected action fixtures can be mapped by case name in:

```text
tests/fixtures/synthetic/expected_actions/registry.json
```

The registry is optional support for future multi-case synthetic evaluation.
`active` entries may be passed as the third pipeline argument. `pending` entries
are known cases without an expected action fixture and must be skipped for
evaluation. Unknown cases are treated as missing. The registry is synthetic only
and is not a real gold-label registry.

The collector reads registry metadata and checks paths through the Python
registry helper. It does not print expected action JSONL contents or
evaluation report contents.

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
- `evaluation_status`
- `expected_action_status`
- `expected_action_path`
- `evaluation_report_exists`
- `content_suppressed`

The collector is not evaluation. It does not calculate F1, accuracy, calibration, selective prediction, or learner-state estimates.

Evaluation statuses:

- `ok`: active case evaluation ran and `evaluation_report.json` exists.
- `fail`: registry lookup or pipeline evaluation failed.
- `skipped_pending`: case is registered as pending, so evaluation was not run.
- `skipped_missing`: case is not in the registry, so evaluation was not run.
- `skipped_no_registry`: reserved for runs without registry support.

Expected action statuses:

- `active`: expected action fixture exists and may be used for optional synthetic evaluation.
- `pending`: expected action fixture is not defined yet.
- `missing`: case is not present in the registry.

It must not be run on `manual_outputs/`, `private_data/`, `real_data/`, or `participant_data/`.

## CI Smoke Test

GitHub Actions runs one lightweight synthetic E2E smoke test:

```bash
scripts/run_synthetic_e2e_pipeline.sh tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl deletion_case_ci
```

This CI check verifies that the Rust safe-view export and Python prototype stages still connect. It is not evaluation and does not calculate F1, accuracy, calibration, or learner-state estimates.

The CI smoke uses only synthetic fixture data. Generated files are written under `tmp/synthetic_e2e/deletion_case_ci/`, which is Git-ignored.

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
- `evaluation_report.json` when optional synthetic evaluation is requested

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

6. Optional Python synthetic evaluation
   - Runs only when an expected action JSONL file is supplied as the third argument.
   - Creates `evaluation_report.json` in the same `tmp/synthetic_e2e/<case_name>/` directory.
   - Uses expected actions only after scoring.
   - Does not change candidate generation, features, constraints, scores, or ranks.
   - Does not calculate F1, production accuracy, calibration, selective prediction, or learner-state estimates.

## Privacy Rules

- Use synthetic data only.
- Do not use production data or real participant data.
- Do not paste JSONL contents into documentation.
- Do not commit generated outputs from `tmp/`.
- Do not process `private_data/`, `real_data/`, or `participant_data/`.

The script suppresses JSONL contents from stdout. It prints only stage summaries and output paths.

When optional evaluation is enabled, stdout reports only `evaluation: ok` or
`evaluation: fail` and the report path. The report is written under `tmp/` and
must not be committed. Do not paste report contents or JSONL contents into docs.

The summary collector also suppresses JSONL contents. It may count structural fields in `candidate_scores.jsonl`, but it does not print candidate descriptions, contexts, proposed edits, final text, or JSONL rows.

## What This Is Not

This pipeline is not production evaluation. Its optional evaluation stage is only
a synthetic expected-action connection check. It does not calculate F1,
production accuracy, calibration, selective prediction, learner-state estimates,
or model performance.

The weighted score and rank are prototype outputs. They are deterministic analysis artifacts, not gold labels and not proof that a candidate is correct.
