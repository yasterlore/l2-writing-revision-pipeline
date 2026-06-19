# OT Scoring Spec

This file defines the documentation home for OT-inspired ranking and scoring experiments.

Prototype scoring logic is implemented for synthetic-only connection testing.
It is not a production scorer and does not claim research performance.

The initial Python feature schema and leakage audit lives in `python/ot_scorer/`.

The initial Python constraint schema prototype also lives in `python/ot_scorer/`.

The initial weighted scorer prototype lives in `python/ot_scorer/score.py`.

## Planned Responsibility

OT-inspired scorers will rank candidates using explicit constraints and documented weights.

Before any scorer is implemented, `python/ot_scorer/features.py` converts `CandidateSet` JSONL into `CandidateFeatureSet` JSONL.

This feature step is not scoring. It creates structural features and leakage flags only.

## CandidateFeature Schema

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

The first version does not include candidate descriptions, proposed edit payloads, local context text, final text, observed edit text, or post-edit context.

## Action Families

- `hold`: no-change baseline candidate.
- `local_edit`: local insert/delete/replace placeholder.
- `grammar_placeholder`: article, number, SVA, tense, preposition, or punctuation placeholder.
- `other_placeholder`: placeholder action outside the initial taxonomy.
- `other`: non-placeholder action.

## Leakage Audit

The feature step rejects input containing forbidden field names, including:

- `local_context_after_observed`
- `final_text`
- `observed_after_text`
- `gold_label`
- `teacher_correction`
- `inserted_text_observed`
- `deleted_text_observed`

It flags candidates or candidate sets that claim `uses_observed_edit_text=true` or `no_oracle_safe=false`.

Future scorers should treat leakage flags as blocking unless a task-specific policy explicitly documents why they are safe.

## Required Documentation

Any scorer must document:

- constraints
- formulas
- variable meanings
- weighting rationale
- ranking rationale
- no-oracle input boundary
- leakage tests

## No-Oracle Requirement

Scoring and ranking must not use final corrected text, future edits, gold labels, post-hoc annotations, `observed_after_text`, `final_text`, teacher corrections, or human corrections after writing.

The feature step follows the same boundary. It uses only structural metadata from candidate generation and does not read observed edit text.

## Constraint Schema Prototype

`python/ot_scorer/constraints.py` converts `CandidateFeatureSet` JSONL into `ConstraintViolationSet` JSONL.

This is still not an OT scorer. It does not assign weights, calculate weighted scores, rank candidates, or evaluate correctness.

Each `ConstraintViolationSet` contains candidate-level constraint records with:

- `constraint_id`
- `constraint_type`
- `violation_count`
- `severity`
- `explanation`
- `observed`

## Constraint Taxonomy

Penalty constraints:

- `NO-LEAKAGE-FLAG`: violation count is 1 when candidate `leakage_flags` is not empty.
- `NO-OBSERVED-EDIT-TEXT`: violation count is 1 when `uses_observed_edit_text=true`.
- `NO-UNSAFE-CANDIDATE`: violation count is 1 when `no_oracle_safe=false`.

Descriptive constraints:

- `HOLD-CANDIDATE`: records whether the candidate is a hold baseline.
- `LOCAL-EDIT-CANDIDATE`: records whether the candidate is a local edit placeholder.
- `GRAMMAR-PLACEHOLDER-CANDIDATE`: records whether the candidate is a grammar placeholder.
- `PLACEHOLDER-CANDIDATE`: records whether the candidate is any placeholder candidate.

Descriptive constraints have `violation_count=0` in this prototype. They are present so a future weighted scorer can decide how to use candidate type information.

Constraint generation uses only `CandidateFeatureSet` structural fields. It must reject forbidden no-oracle field names and must not read context text, observed edit text, final text, gold labels, or teacher corrections.

## Weighted OT Scorer Prototype

`python/ot_scorer/score.py` converts `ConstraintViolationSet` JSONL into `CandidateScoreSet` JSONL.

Each `CandidateScore` includes:

- `candidate_id`
- `episode_id`
- `action_type`
- `weighted_score`
- `blocked`
- `block_reasons`
- `rank`
- `constraint_contributions`
- `scoring_policy_version`
- `no_oracle_safe`

`candidate_id` is an identifier. `action_type` is the explicit candidate action
category copied from candidate generation via constraint generation. Downstream
synthetic evaluation must use `action_type`, not candidate-id naming conventions.
This field is candidate-derived and is not an expected action, gold label, or
teacher correction.

The score formula is:

```text
weighted_score(c) = sum_i w_i * v_i(c)
```

where:

- `c` is a candidate.
- `i` is a constraint index.
- `w_i` is the prototype weight for constraint `i`.
- `v_i(c)` is the candidate's violation count for constraint `i`.
- `weighted_score(c)` is the total penalty score. Lower is better.

Initial blocking constraints:

- `NO-LEAKAGE-FLAG`
- `NO-OBSERVED-EDIT-TEXT`
- `NO-UNSAFE-CANDIDATE`

These use weight `1_000_000.0` and mark a candidate as `blocked=true` when `violation_count > 0`.

Descriptive constraints use weight `0.0` and are not added to the score.

The weights are not learned. They are hand-designed safety defaults for the prototype.

Blocked candidates are placed after unblocked candidates. Among equal-score unblocked candidates, tie-break is deterministic:

1. hold
2. local edit
3. grammar placeholder
4. other placeholder
5. other

The rank is a deterministic prototype order, not a correctness label or evaluation result.

## Current Non-Goals

- No evaluation, F1, calibration, or selective prediction is implemented.
- No evaluation or learner-state estimation is performed.
