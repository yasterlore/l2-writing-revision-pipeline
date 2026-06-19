# Candidate Feature Schema and Leakage Audit

This module prepares simple no-oracle structural features, constraint violations, and prototype weighted scores for future OT-inspired scoring experiments.

It does not implement evaluation, F1, calibration, selective prediction, or learner-state estimation.

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
- `candidate_metadata_complete`
- `has_generation_rule`
- `has_action_family`
- `is_safety_relevant_candidate`
- `is_placeholder_candidate`
- `is_grammar_family_candidate`
- `is_local_edit_family_candidate`
- `is_hold_candidate`
- `candidate_family_bucket`
- `is_placeholder`
- `is_hold`
- `is_local_edit`
- `is_grammar_placeholder`
- `candidate_description_length`
- `feature_notes_count`
- `leakage_flags`

The newer structural fields are derived only from candidate metadata and safety
flags. They are intended for later constraint refinement and debugging, not for
performance claims.

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

## Constraint Schema

The constraint prototype reads `CandidateFeatureSet` JSONL and writes `ConstraintViolationSet` JSONL.

Run it from the repository root:

```bash
PYTHONPATH=python python3 -m ot_scorer.constraints \
  --input tests/fixtures/synthetic/candidate_features/valid/deletion_candidate_features.jsonl \
  --output tmp/constraint_violations.jsonl
```

### Constraint Taxonomy

Penalty constraints record violations that future scoring should treat as blocking until a task-specific policy says otherwise:

- `NO-LEAKAGE-FLAG`: violation when candidate `leakage_flags` is not empty.
- `NO-OBSERVED-EDIT-TEXT`: violation when `uses_observed_edit_text=true`.
- `NO-UNSAFE-CANDIDATE`: violation when `no_oracle_safe=false`.

Descriptive constraints record candidate type without adding a penalty in this version:

- `HOLD-CANDIDATE`
- `LOCAL-EDIT-CANDIDATE`
- `GRAMMAR-PLACEHOLDER-CANDIDATE`
- `PLACEHOLDER-CANDIDATE`
- `HAS-GENERATION-RULE`
- `HAS-ACTION-FAMILY`
- `CANDIDATE-METADATA-COMPLETE`
- `HOLD-FAMILY-CANDIDATE`
- `LOCAL-EDIT-FAMILY-CANDIDATE`
- `GRAMMAR-FAMILY-CANDIDATE`
- `PLACEHOLDER-FAMILY-CANDIDATE`
- `SAFETY-RELEVANT-CANDIDATE`
- `CANDIDATE-FAMILY-BUCKET`
- `ARTICLE-PLACEHOLDER-CANDIDATE`
- `NUMBER-PLACEHOLDER-CANDIDATE`
- `SVA-PLACEHOLDER-CANDIDATE`
- `TENSE-PLACEHOLDER-CANDIDATE`
- `PREPOSITION-PLACEHOLDER-CANDIDATE`
- `PUNCTUATION-PLACEHOLDER-CANDIDATE`

These structural descriptive constraints are derived from
`CandidateFeatureSet` metadata. Their `violation_count` is always `0`, and the
weighted scorer does not add them to `weighted_score`.

The linguistic placeholder constraints record candidate families only. They do
not judge grammatical correctness.

The output includes `violation_count`, `severity`, and `explanation`, but it does not include weights, weighted scores, ranks, candidate text, local context text, or observed edit text.

## Synthetic Data Only

All fixtures are synthetic. Do not commit feature outputs derived from real participant data.

## Weighted OT Scorer Prototype

The scorer prototype reads `ConstraintViolationSet` JSONL and writes `CandidateScoreSet` JSONL.

Run it from the repository root:

```bash
PYTHONPATH=python python3 -m ot_scorer.score \
  --input tests/fixtures/synthetic/constraint_violations/valid/deletion_constraint_violations.jsonl \
  --output tmp/candidate_scores.jsonl
```

Each candidate score contains:

- `candidate_id`
- `episode_id`
- `action_type`
- `generation_rule`
- `action_family`
- `weighted_score`
- `blocked`
- `block_reasons`
- `rank`
- `constraint_contributions`
- `scoring_policy_version`
- `no_oracle_safe`

`candidate_id` is only an identifier. `action_type` is the explicit candidate
classification copied from the constraint-violation input and is used by the
synthetic evaluation prototype. It is not a gold label, expected answer, or
teacher correction.

`generation_rule` and `action_family` are copied through from candidate
generation and feature extraction for interpretability and debugging. They are
no-oracle-safe metadata in this prototype and do not change the weighted score,
blocking constraints, or deterministic tie-break policy.

### Weighted Score

The prototype uses:

```text
weighted_score(candidate) = sum(weight(constraint_id) * violation_count)
```

Blocking constraints have weight `1_000_000.0` and are treated as safety blockers:

- `NO-LEAKAGE-FLAG`
- `NO-OBSERVED-EDIT-TEXT`
- `NO-UNSAFE-CANDIDATE`

Descriptive constraints have weight `0.0`:

- `HOLD-CANDIDATE`
- `LOCAL-EDIT-CANDIDATE`
- `GRAMMAR-PLACEHOLDER-CANDIDATE`
- `PLACEHOLDER-CANDIDATE`

These weights are hand-designed safety defaults, not learned values.

### Blocking and Ranking Policy

If a blocking constraint has `violation_count > 0`, the candidate is marked `blocked=true` and placed after unblocked candidates.

Among unblocked candidates with the same score, tie-break is deterministic:

1. hold
2. local edit
3. grammar placeholder
4. other placeholder
5. other

This rank is not a correctness prediction. It is a deterministic prototype order for later experiments.

Candidate score outputs derived from real participant data must not be committed to this repository.

For planned refinements and non-goals, read `../../docs/scoring_policy_refinement_plan.md`.
For the future linguistic placeholder constraint boundary, read
`../../docs/linguistic_placeholder_constraint_plan.md`.
For future no-oracle-safe local pattern features, read
`../../docs/local_pattern_feature_plan.md`.
