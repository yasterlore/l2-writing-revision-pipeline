# OT Scoring Spec

This file defines the documentation home for OT-inspired ranking and scoring experiments.

No scoring logic is implemented yet.

The initial Python feature schema and leakage audit lives in `python/ot_scorer/`.

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

## Current Non-Goals

- No OT constraints are implemented.
- No weights are introduced.
- No ranking is performed.
- No evaluation or learner-state estimation is performed.
