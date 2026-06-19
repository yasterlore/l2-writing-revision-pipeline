# Evaluation Spec

This document defines the first synthetic-only evaluation schema prototype.

It is not a production evaluation protocol and does not report real research performance.

## Purpose

The evaluation prototype compares `CandidateScoreSet` JSONL with synthetic expected action JSONL.

It checks whether the rank-1 unblocked candidate action matches the synthetic expected action for the same episode.

## Inputs

### CandidateScoreSet JSONL

One score set per line, produced by the weighted OT scorer prototype.

The evaluator reads:

- `episode_id`
- `candidate_scores`
- `candidate_id`
- `action_type`
- `rank`
- `blocked`

`candidate_id` is an identifier only. The evaluator compares synthetic expected
actions against the explicit `CandidateScore.action_type` field and does not
infer action type from candidate-id naming conventions.

### Synthetic Expected Action JSONL

One expected action per line:

- `episode_id`
- `expected_action_type`
- `expected_source`
- `synthetic_only: true`
- `notes`

Synthetic expected actions are not real gold labels, teacher corrections, or final corrected text.

### Synthetic Expected Action Registry

The registry file maps synthetic case names to synthetic expected action
fixtures:

```text
tests/fixtures/synthetic/expected_actions/registry.json
```

The registry is a fixture-management table, not a real gold-label registry.
It contains only synthetic case metadata and expected-action fixture paths.

The initial active synthetic expected action fixtures cover `deletion_case`,
`selection_edit_case`, and `cursor_movement_case`. The latter two are
conservative placeholders: `selection_edit_case` uses
`local_replace_placeholder` for its central range-edit episode, while
`cursor_movement_case` uses `local_insert_placeholder` for its non-terminal
cursor-edit episode. These are synthetic expectations for wiring checks, not
claims about learner correctness.

Registry entry statuses:

- `active`: the case has a synthetic expected action fixture and can be used for optional evaluation.
- `pending`: the case is known, but the expected action fixture has not been defined yet and must not be evaluated.
- `missing`: returned by the helper when a case name is not present in the registry.

The registry helper validates case names, duplicate entries, path existence, and
private/manual-looking paths. It does not read expected-action JSONL contents.
It rejects paths under `manual_outputs/`, `private_data/`, `real_data/`, and
`participant_data/`.

`scripts/run_synthetic_e2e_summary.sh` uses this registry to run optional
evaluation for `active` cases only. `pending` and `missing` cases are reported
as skipped and do not receive expected-action input.

The summary collector may read top-level numeric fields from
`evaluation_report.json` for active cases:

- `episodes_total`
- `episodes_evaluated`
- `exact_match_count`
- `expected_found_in_candidates_count`
- `blocked_expected_count`

It does not print the full report or per-episode details. It also does not copy
`exact_match_rate` into `summary.csv` in this version, to avoid presenting a
synthetic wiring check as a research-performance result.

## Output

The evaluator writes one `EvaluationReport` JSON file.

When connected through `scripts/run_synthetic_e2e_pipeline.sh`, the report is
written to `tmp/synthetic_e2e/<case_name>/evaluation_report.json` only when an
expected action JSONL path is provided. The expected action file is used after
scoring and is not passed to candidate generation, feature extraction,
constraint generation, or scoring.

Summary fields:

- `episodes_total`
- `episodes_evaluated`
- `episodes_missing_expected`
- `exact_match_count`
- `exact_match_rate`
- `expected_found_in_candidates_count`
- `expected_found_in_candidates_rate`
- `blocked_expected_count`

Per-episode fields:

- `episode_id`
- `expected_action_type`
- `top1_action_type`
- `exact_match`
- `expected_found_in_candidates`
- `expected_rank`
- `expected_candidate_blocked`
- `evaluation_notes`

## exact_match_rate

```text
exact_match_rate = exact_match_count / episodes_evaluated
```

If `episodes_evaluated` is zero, `exact_match_rate` is `0.0`.

The report intentionally does not include F1, production accuracy, calibration, or selective prediction.

## Blocked Candidate Policy

Top-1 is selected from unblocked candidates only.

If the expected action appears only in blocked candidates:

- `expected_candidate_blocked=true`
- exact match is false
- `blocked_expected_count` increases

This prevents a safety-blocked candidate from counting as a successful evaluation result.

## No-Oracle Boundary

Expected actions are used only after scoring.

They must not be used for:

- candidate generation
- feature extraction
- constraint generation
- weighted scoring
- rank adjustment

The evaluator must reject forbidden fields such as `final_text`, `observed_after_text`, `gold_label`, `teacher_correction`, and post-hoc correction fields.

## Synthetic-Only Policy

Use synthetic expected action fixtures only in this repository.

Do not use real participant data, real teacher corrections, real gold labels, or final corrected text.

Do not commit evaluation reports derived from real participant data.

## Current Non-Goals

- no real-data evaluation
- no F1
- no production accuracy claim
- no calibration
- no selective prediction
- no learner-state estimation
- no model comparison
