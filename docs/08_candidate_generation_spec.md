# Candidate Generation Spec

This file defines the documentation home for no-oracle candidate generation.

The initial Python prototype lives in `python/candidate_generation/`.

## Responsibility

Candidate generation proposes possible action candidates from a Rust-exported `NoOracleSafeEpisodeView` JSONL file.

It is a broad proposal stage, not a scorer and not a ranker.

## Input

Input is one `NoOracleSafeEpisodeView` per JSONL line.

Allowed input fields include:

- `episode_id`
- `source_revision_event_id`
- `revision_kind`
- `is_revision_like`
- `local_context_before`
- `cursor_pos_before`
- `span_start`
- `span_end`
- `doc_len_before`
- `quality_flags`
- `no_oracle_safe_view`
- `post_edit_context_suppressed`
- `observed_edit_text_included`

`inserted_text_observed` and `deleted_text_observed` may exist in an explicitly exported safe view, but the initial generator ignores them by default.

## Output

Output is one `CandidateSet` per JSONL line.

Each candidate contains:

- `candidate_id`
- `episode_id`
- `action_type`
- `description`
- `proposed_edit`
- `uses_observed_edit_text`
- `no_oracle_safe`
- `generation_rule`
- `feature_notes`

## Action Type Taxonomy

- `hold`: no-change placeholder.
- `local_insert_placeholder`: local insertion-like placeholder.
- `local_delete_placeholder`: local deletion-like placeholder.
- `local_replace_placeholder`: local replacement-like placeholder.
- `article_fix_placeholder`: article-related placeholder.
- `number_fix_placeholder`: number-agreement placeholder.
- `sva_fix_placeholder`: subject-verb agreement placeholder.
- `tense_fix_placeholder`: tense-related placeholder.
- `preposition_fix_placeholder`: preposition placeholder.
- `punctuation_fix_placeholder`: punctuation placeholder.

The taxonomy is intentionally provisional. These candidates are not correctness labels.

## Generation Rules

The prototype always emits `hold`.

It emits local edit placeholders from observed event shape, such as `revision_kind` and cursor/span metadata.

For revision-like episodes, it emits broad grammar placeholders. These are unranked options for later scoring experiments.

## No-Oracle Requirement

Candidate generation must not use final corrected text, future edits, gold labels, post-hoc annotations, `observed_after_text`, `final_text`, teacher corrections, or human corrections after writing.

The initial Python loader rejects forbidden fields recursively, including `local_context_after_observed`.

`uses_observed_edit_text` is always `false` in this prototype. If observed edit text is present in the input, it is ignored and a policy warning is attached.

## Security and Privacy

Use synthetic data only in this repository.

Do not write candidate outputs derived from real participant data into the repository. Use `tmp/`, `manual_outputs/`, or an institution-approved private location for local outputs.

The prototype uses standard JSON parsing only. It does not use `pickle`, `eval`, `exec`, unsafe deserialization, or network access.

## Current Limitations

The first version only creates placeholder candidates. It does not perform OT scoring, ranking, evaluation, learner-state estimation, or actual grammar correction.
