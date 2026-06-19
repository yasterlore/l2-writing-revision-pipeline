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

After each successful pipeline run, the collector also looks for:

```text
tmp/synthetic_e2e/<case_name>/constraint_violations.jsonl
```

When that file exists, it runs the diagnostic summary CLI and writes:

```text
tmp/synthetic_e2e/<case_name>/diagnostic_summary.json
```

This diagnostic summary is count-only. It is for synthetic wiring and
diagnostic inspection, not model performance evaluation.

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
- `evaluation_summary_available`
- `evaluation_episodes_total`
- `evaluation_episodes_evaluated`
- `evaluation_exact_match_count`
- `evaluation_expected_found_count`
- `evaluation_blocked_expected_count`
- `diagnostic_summary_status`
- `diagnostic_summary_path`
- `diagnostic_total_constraints`
- `diagnostic_descriptive_constraint_count`
- `diagnostic_blocking_constraint_count`
- `diagnostic_safety_constraint_count`
- `diagnostic_local_pattern_constraint_count`
- `diagnostic_linguistic_placeholder_constraint_count`
- `diagnostic_non_leaky_linguistic_constraint_count`
- `content_suppressed`

The collector reads only top-level summary counts from `evaluation_report.json`
when an active case produced a report. It does not print report contents or
per-episode details.

The collector reads only top-level count fields from `diagnostic_summary.json`.
It does not print diagnostic report bodies, raw constraint JSONL rows,
candidate descriptions, proposed edits, local context, final text, or
per-episode details.

`diagnostic_non_leaky_linguistic_constraint_count` is the sum of top-level
`non_leaky_linguistic_constraint_counts` values from `diagnostic_summary.json`.
If that field is absent in an older diagnostic summary, the collector treats the
count as `0`. This count is diagnostic wiring information, not grammatical
correctness or model performance.

The collector is not production evaluation. It does not calculate F1, accuracy,
calibration, selective prediction, or learner-state estimates.

The collector intentionally does not add `exact_match_rate` to the CSV in this
version. Count fields are enough for synthetic wiring checks and are less likely
to be mistaken for research-performance claims.

Evaluation statuses:

- `ok`: active case evaluation ran and `evaluation_report.json` exists.
- `fail`: registry lookup or pipeline evaluation failed.
- `skipped_pending`: case is registered as pending, so evaluation was not run.
- `skipped_missing`: case is not in the registry, so evaluation was not run.
- `skipped_no_registry`: reserved for runs without registry support.

Diagnostic summary statuses:

- `ok`: `constraint_violations.jsonl` existed and count-only diagnostic summary generation succeeded.
- `fail`: diagnostic summary generation failed. This is reported separately from `pipeline_status`.
- `skipped_missing_constraints`: no constraint violation file was available for that case.

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
- `diagnostic_summary.json` when the summary collector runs diagnostic aggregation

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

7. Optional diagnostic summary aggregation in the collector
   - Runs from `scripts/run_synthetic_e2e_summary.sh`, not from the single-case pipeline script.
   - Reads `constraint_violations.jsonl` after the pipeline completes.
   - Writes `diagnostic_summary.json` under `tmp/`.
   - Records only count fields in `summary.csv`.
   - Does not change feature extraction, constraint generation, scoring, ranking, or evaluation.

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

For active evaluation cases, the summary collector may read top-level numeric
fields from `evaluation_report.json`, but it does not print the report body,
per-episode records, or any text fragments.

For diagnostic aggregation, the summary collector may read top-level count
fields from `diagnostic_summary.json`, but it does not print the report body,
raw constraint JSONL rows, candidate descriptions, proposed edits, local
context, or per-episode records.

For safe interpretation of these count-only outputs, see
[`synthetic_diagnostic_distribution_review_plan.md`](synthetic_diagnostic_distribution_review_plan.md).

## Diagnostic Distribution Smoke Check

After running the summary collector, a lightweight smoke check can verify that
the count-only diagnostic columns exist and contain parseable values:

```bash
scripts/check_synthetic_diagnostic_distribution.sh
```

You can also pass an explicit summary path:

```bash
scripts/check_synthetic_diagnostic_distribution.sh tmp/synthetic_e2e_summary/summary.csv
```

This script reads only the summary CSV. It checks column presence, at least one
case, at least one `diagnostic_summary_status=ok` row, and parseable diagnostic
count fields. It does not read raw JSONL, diagnostic summary bodies,
per-episode detail, expected actions, final text, or local context.

The smoke check also verifies that
`diagnostic_non_leaky_linguistic_constraint_count` is present and numeric.

The smoke check is not performance evaluation. It does not calculate F1,
accuracy, calibration, grammatical correctness, ranking quality, or
learner-state estimates.

## What This Is Not

This pipeline is not production evaluation. Its optional evaluation stage is only
a synthetic expected-action connection check. It does not calculate F1,
production accuracy, calibration, selective prediction, learner-state estimates,
or model performance.

The weighted score and rank are prototype outputs. They are deterministic analysis artifacts, not gold labels and not proof that a candidate is correct.
