# Candidate Generation Prototype

This Python module generates placeholder candidate sets from Rust-exported `NoOracleSafeEpisodeView` JSONL.

It is an exploratory prototype. It is not an authoritative validation layer, not a ranker, and not an OT scorer.

## Purpose

The module prepares a candidate set for each safe episode view before future OT scoring and ranking experiments.

It consumes only no-oracle-safe fields exported by Rust:

- `episode_id`
- `source_revision_event_id`
- `revision_kind`
- `is_revision_like`
- `local_context_before`
- cursor/span/doc length metadata before the edit
- `quality_flags`

It rejects forbidden no-oracle fields such as `final_text`, `observed_after_text`, `gold_label`, `teacher_correction`, and `local_context_after_observed`.

## Input

Input is JSONL with one `NoOracleSafeEpisodeView` per line.

Recommended source:

```bash
cargo run -q -p kslog_cli -- export-safe-view \
  tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl \
  tmp/safe_view.jsonl
```

Use synthetic data only. Do not store real participant exports in this repository.

## Output

Output is JSONL with one `CandidateSet` per episode. Each candidate includes:

- `candidate_id`
- `episode_id`
- `action_type`
- `description`
- `proposed_edit`
- `uses_observed_edit_text`
- `no_oracle_safe`
- `generation_rule`
- `feature_notes`

## Running

From the repository root:

```bash
PYTHONPATH=python python3 -m candidate_generation.generate \
  --input tests/fixtures/synthetic/safe_views/valid/deletion_safe_view.jsonl \
  --output tmp/candidate_sets.jsonl
```

Write generated outputs to `tmp/`, `manual_outputs/`, or another Git-ignored synthetic-output location.

## Candidate Action Taxonomy

- `hold`: keep a no-change placeholder.
- `local_insert_placeholder`: possible local insertion action.
- `local_delete_placeholder`: possible local deletion action.
- `local_replace_placeholder`: possible local replacement action.
- `article_fix_placeholder`: possible article-related edit.
- `number_fix_placeholder`: possible number-agreement edit.
- `sva_fix_placeholder`: possible subject-verb agreement edit.
- `tense_fix_placeholder`: possible tense-related edit.
- `preposition_fix_placeholder`: possible preposition edit.
- `punctuation_fix_placeholder`: possible punctuation edit.

These are placeholder candidates, not ranked hypotheses and not gold corrections.

## No-Oracle Policy

The generator does not use:

- `local_context_after_observed`
- `final_text`
- `observed_after_text`
- `gold_label`
- `teacher_correction`
- human corrections
- future edits

If `observed_edit_text_included=true` is present in input, the prototype still ignores `inserted_text_observed` and `deleted_text_observed` by default and emits a policy warning in the candidate set.

## Tests

```bash
PYTHONPATH=python python3 -m unittest discover -s python/candidate_generation/tests
PYTHONPATH=python python3 -m compileall python/candidate_generation
```

`ruff` and `pytest` are intentionally not required in this first version to keep dependencies minimal.

## What This Does Not Do Yet

- It does not perform OT scoring.
- It does not rank candidates.
- It does not evaluate candidate quality.
- It does not estimate learner state.
- It does not use real participant data.
- It does not produce final corrections.
