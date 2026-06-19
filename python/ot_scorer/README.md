# Candidate Feature Schema and Leakage Audit

This module prepares simple no-oracle structural features from `CandidateSet` JSONL for future OT-inspired scoring experiments.

It does not implement OT scoring, weights, ranking, evaluation, or learner-state estimation.

## Purpose

The module defines `CandidateFeature` and `CandidateFeatureSet` as a stable boundary between candidate generation and future scoring.

It also performs a lightweight leakage audit before features are written.

## Input

Input is JSONL with one `CandidateSet` per line, produced by `python/candidate_generation/`.

The loader rejects forbidden no-oracle fields such as:

- `local_context_after_observed`
- `final_text`
- `observed_after_text`
- `gold_label`
- `teacher_correction`
- `inserted_text_observed`
- `deleted_text_observed`

## Output

Output is JSONL with one `CandidateFeatureSet` per episode.

Each candidate feature contains:

- `candidate_id`
- `episode_id`
- `action_type`
- `generation_rule`
- `no_oracle_safe`
- `uses_observed_edit_text`
- `action_family`
- `is_placeholder`
- `is_hold`
- `is_local_edit`
- `is_grammar_placeholder`
- `candidate_description_length`
- `feature_notes_count`
- `leakage_flags`

The feature output does not include candidate descriptions, proposed edit payloads, local context text, or observed edit text.

## Running

From the repository root:

```bash
PYTHONPATH=python python3 -m ot_scorer.features \
  --input tests/fixtures/synthetic/candidate_sets/valid/deletion_candidate_set.jsonl \
  --output tmp/candidate_features.jsonl
```

Write generated outputs to `tmp/`, `manual_outputs/`, or another Git-ignored synthetic-output location.

## Leakage Audit

The audit rejects forbidden field names recursively.

It also flags:

- `candidate_set_not_no_oracle_safe`
- `candidate_set_uses_observed_edit_text`
- `candidate_not_no_oracle_safe`
- `candidate_uses_observed_edit_text`

Flagged candidates can still be represented in feature output for synthetic testing, but downstream scoring should treat leakage flags as blocking until a task-specific policy says otherwise.

## No-Oracle Policy

The module does not use:

- post-edit context
- final text
- gold labels
- teacher corrections
- observed edit text
- future edits

It uses only structural properties of the candidate object, such as action type, rule name, description length, and note count.

## Tests

```bash
PYTHONPATH=python python3 -m unittest discover -s python
PYTHONPATH=python python3 -m compileall python
```

`ruff` and `pytest` are not required in this first version to keep dependencies minimal.

## Synthetic Data Only

All fixtures are synthetic. Do not commit feature outputs derived from real participant data.
