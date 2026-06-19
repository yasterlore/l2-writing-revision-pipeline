# Synthetic Evaluation Schema Prototype

This module compares `CandidateScoreSet` JSONL against synthetic expected action JSONL.

It is a schema and wiring prototype. It is not production evaluation, not real participant evaluation, and not a claim about model quality.

## Purpose

The module checks whether a synthetic expected action is ranked first by the current prototype scorer.

It also records whether the expected action appears anywhere among candidates and whether it appears only in blocked candidates.

## Input

1. `CandidateScoreSet` JSONL
   - one score set per episode
   - produced by `python/ot_scorer.score`
   - each candidate score must include explicit `action_type`

2. Synthetic expected action JSONL
   - one expected action per episode
   - fields:
     - `episode_id`
     - `expected_action_type`
     - `expected_source`
     - `synthetic_only`
     - `notes`

Synthetic expected actions are not real gold labels and not teacher corrections.

The evaluator compares `expected_action_type` with `CandidateScore.action_type`.
It does not parse `candidate_id` to infer action type. `candidate_id` remains a
stable identifier, while `action_type` is the candidate-generation-derived
category used for comparison.

## Synthetic Expected Action Registry

`tests/fixtures/synthetic/expected_actions/registry.json` maps synthetic case
names to synthetic expected action fixture paths.

The registry helper can:

- load the registry
- return an active expected action path for a case
- mark a known-but-not-ready case as `pending`
- mark an unknown case as `missing`
- reject duplicate case names
- reject missing fixture paths
- reject `manual_outputs/`, `private_data/`, `real_data/`, and `participant_data/` paths

The helper validates paths only. It does not read expected-action JSONL bodies.
The registry is not a real gold-label registry and must not be used for
production or participant-data evaluation.

## Output

Output is one `EvaluationReport` JSON file with summary fields and per-episode records.

Summary fields include:

- `episodes_total`
- `episodes_evaluated`
- `episodes_missing_expected`
- `exact_match_count`
- `exact_match_rate`
- `expected_found_in_candidates_count`
- `expected_found_in_candidates_rate`
- `blocked_expected_count`

Per-episode fields include:

- `episode_id`
- `expected_action_type`
- `top1_action_type`
- `exact_match`
- `expected_rank`
- `expected_candidate_blocked`
- `evaluation_notes`

## Running

From the repository root:

```bash
PYTHONPATH=python python3 -m evaluation.evaluate \
  --scores tests/fixtures/synthetic/candidate_scores/valid/deletion_candidate_scores.jsonl \
  --expected tests/fixtures/synthetic/expected_actions/valid/deletion_expected_actions.jsonl \
  --output tmp/evaluation_report.json
```

Write generated reports to `tmp/`, `manual_outputs/`, or another Git-ignored synthetic-output location.

## exact_match_rate

```text
exact_match_rate = exact_match_count / episodes_evaluated
```

If `episodes_evaluated` is zero, the rate is `0.0`.

This is a synthetic connection-check metric. It is not F1, not production accuracy, and not calibration.

## Blocked Candidates

`top1_action_type` is selected from unblocked candidates only.

If the expected action appears only in blocked candidates:

- `expected_candidate_blocked=true`
- it is not counted as an exact match
- `blocked_expected_count` increases

This keeps safety blocking from being treated as a successful ranking.

## No-Oracle Policy

Expected actions are used only after candidate generation, feature extraction, constraint generation, and scoring.

Expected actions must not be used to change ranking, candidate generation, feature extraction, constraints, or scores.

The loader rejects forbidden fields such as `final_text`, `observed_after_text`, `gold_label`, and `teacher_correction`.

## What This Does Not Do

- It does not evaluate real participant data.
- It does not use real gold labels.
- It does not use teacher corrections.
- It does not calculate F1.
- It does not calculate calibration.
- It does not implement selective prediction.
- It does not estimate learner state.

## Tests

```bash
PYTHONPATH=python python3 -m unittest discover -s python
PYTHONPATH=python python3 -m compileall python
```

`ruff` and `pytest` are not required in this first version to keep dependencies minimal.
