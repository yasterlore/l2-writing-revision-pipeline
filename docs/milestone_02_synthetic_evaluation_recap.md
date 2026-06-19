# Milestone 02 Synthetic Evaluation Recap

This document summarizes the synthetic evaluation foundation added in Steps 29-35.

It is a beginner-friendly map of what exists, what information is allowed, and why this milestone is still only a synthetic wiring check.

## 1. Purpose

Milestone 02 adds a synthetic-only evaluation schema around the existing Rust + Python pipeline.

The purpose is to check that these pieces connect:

```text
synthetic RawEvent JSONL
  -> Rust deterministic pipeline
  -> Python candidate generation
  -> Python feature extraction
  -> Python constraint generation
  -> Python weighted scoring prototype
  -> optional synthetic expected-action evaluation
  -> summary-only collector output
```

This milestone is not:

- production evaluation
- real participant evaluation
- a research performance claim
- a model-quality claim
- F1, accuracy, calibration, or learner-state estimation

It is a controlled synthetic connection check.

## 2. Step 29-35 Flow

### Step 29: Evaluation Schema

`python/evaluation/` defines synthetic expected actions and evaluation reports.

Input:

- `CandidateScoreSet` JSONL from the scorer
- synthetic expected action JSONL

Output:

- `EvaluationReport` JSON written under `tmp/`

The evaluation compares the unblocked rank-1 candidate action with the synthetic expected action for the same episode.

### Step 30: CandidateScore.action_type

`CandidateScore` now includes explicit `action_type`.

Why this matters:

- `candidate_id` is only an identifier.
- `action_type` is the candidate action category.
- evaluation compares `CandidateScore.action_type` with `expected_action_type`.
- evaluation no longer infers action type from candidate-id naming conventions.

`action_type` is candidate-generation-derived. It is not a gold label.

### Step 31: Optional Evaluation in the E2E Pipeline

`scripts/run_synthetic_e2e_pipeline.sh` accepts an optional expected action file:

```bash
scripts/run_synthetic_e2e_pipeline.sh \
  tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl \
  deletion_case_with_eval \
  tests/fixtures/synthetic/expected_actions/valid/deletion_expected_actions.jsonl
```

If the expected action file is omitted, the pipeline stops after scoring.

If it is provided, evaluation runs after scoring and writes:

```text
tmp/synthetic_e2e/<case_name>/evaluation_report.json
```

### Step 32: Synthetic Expected Action Registry

`tests/fixtures/synthetic/expected_actions/registry.json` maps case names to synthetic expected action fixtures.

Registry statuses:

- `active`: an expected action fixture exists and may be used for optional synthetic evaluation.
- `pending`: the case is known, but its expected action fixture is not defined yet.
- `missing`: returned by lookup when a case is not in the registry.

This registry is synthetic-only. It is not a real gold-label registry.

### Step 33: Summary Collector Registry Integration

`scripts/run_synthetic_e2e_summary.sh` now checks the registry for each synthetic fixture.

For `active` cases, it runs the E2E pipeline with optional evaluation.

For `pending` or `missing` cases, it runs the E2E pipeline without evaluation and records the skipped status.

### Step 34: Synthetic Expected Action Fixture Expansion

Active synthetic expected action coverage now includes:

- `deletion_case`
- `selection_edit_case`
- `cursor_movement_case`

These expected actions are conservative synthetic placeholders. They are not real gold labels.

### Step 35: Safe Evaluation Summary Aggregation

The summary collector can read top-level numeric fields from `evaluation_report.json` and write safe count fields into:

```text
tmp/synthetic_e2e_summary/summary.csv
```

It does not print report bodies, JSONL rows, or per-episode details.

## 3. Expected Actions

Expected actions in this repository are synthetic expected actions.

They are:

- created for synthetic fixtures only
- used only after scoring
- used only by the evaluation module or summary collector
- not used for candidate generation
- not used for feature extraction
- not used for constraint generation
- not used for weighted scoring
- not used to change ranks

They are not:

- real gold labels
- teacher corrections
- final corrected text
- human correction labels
- participant-derived annotations

## 4. Evaluation Reports

Evaluation reports are generated under `tmp/`.

Example location:

```text
tmp/synthetic_e2e/deletion_case/evaluation_report.json
```

Rules:

- `tmp/` is Git-ignored.
- Do not commit evaluation reports.
- Do not paste report bodies into docs.
- Do not paste per-episode details into docs.
- Do not use real participant data to produce reports in this repository.

## 5. Summary Collector

Run:

```bash
scripts/run_synthetic_e2e_summary.sh
```

The collector writes:

```text
tmp/synthetic_e2e_summary/summary.csv
```

It records connection-check fields such as:

- `pipeline_status`
- `evaluation_status`
- `expected_action_status`
- `evaluation_report_exists`
- `evaluation_summary_available`
- `evaluation_episodes_total`
- `evaluation_episodes_evaluated`
- `evaluation_exact_match_count`
- `evaluation_expected_found_count`
- `evaluation_blocked_expected_count`

The collector does not print JSONL rows, evaluation report bodies, or per-episode records.

### Active, Pending, Missing

`active` means the case has a synthetic expected action fixture and optional evaluation can run.

`pending` means the case is known but no expected action fixture exists yet, so evaluation is skipped.

`missing` means the case is not registered, so evaluation is skipped.

### Why exact_match_rate Is Not in summary.csv

`EvaluationReport` contains `exact_match_rate`, but the summary collector does not copy it into `summary.csv` in this milestone.

Reason:

- count fields are enough for a synthetic wiring check
- rates can look like performance claims
- this repository is not claiming research performance yet

The collector also does not report F1, accuracy, calibration, selective prediction, or learner-state estimates.

## 6. No-Oracle Boundary

Expected actions are evaluation-time information.

They must not flow backward into:

- candidate generation
- feature extraction
- constraint generation
- weighted scoring
- ranking
- learner-state estimation

The pipeline must not use:

- `final_text`
- `observed_after_text`
- `gold_label`
- teacher correction
- human correction
- answer key
- future context
- post-hoc annotation

This keeps prediction-time inputs separate from evaluation-time checks.

## 7. Synthetic-Only and Security Policy

Use synthetic data only in this repository.

Do not use:

- real participant data
- real learner writing
- real teacher corrections
- real gold labels
- private local datasets

Do not commit or document:

- `manual_outputs/`
- `tmp/`
- evaluation report bodies
- JSONL rows
- participant text
- private data

The collector and pipeline are summary-only by design.

## 8. What Works Now

The repository can now:

- run synthetic raw event fixtures through Rust validation, replay, extraction, micro-episodes, no-oracle audit, and safe-view export
- run Python candidate generation, feature extraction, constraint generation, and weighted scoring
- optionally run synthetic expected-action evaluation for active registry cases
- collect summary-only status across synthetic fixtures
- distinguish active, pending, and missing expected-action coverage
- record safe count fields without printing report bodies

## 9. What Still Does Not Exist

Not implemented yet:

- production evaluation
- real participant evaluation
- real gold label workflow
- F1
- accuracy claims
- calibration
- selective prediction
- learner-state estimation
- model-performance comparison
- private real-data readiness workflow

## 10. Where To Read Next

Read:

- `docs/evaluation_spec.md` for the evaluation schema.
- `docs/synthetic_e2e_pipeline.md` for the E2E pipeline and summary collector.
- `docs/03_no_oracle_policy.md` for no-oracle rules.
- `docs/milestone_01_pipeline_recap.md` for the earlier pipeline foundation.

## 11. Next Candidate Steps

Good next steps:

- add more pending synthetic expected action fixtures
- refine the scoring policy while keeping no-oracle boundaries explicit
- design future evaluation metrics cautiously
- defer calibration and selective prediction until the synthetic boundary is stable
- create a private real-data readiness checklist before any real-data work

Any future metric documentation should clearly separate synthetic connection checks from research performance claims.
