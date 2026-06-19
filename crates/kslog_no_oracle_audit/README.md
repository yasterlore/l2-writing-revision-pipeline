# kslog_no_oracle_audit

`kslog_no_oracle_audit` checks whether pipeline artifacts contain fields or concepts that would leak future, gold, or post-hoc information into no-oracle modeling contexts.

It does not generate candidates, rank candidates, score candidates, or estimate learner state.

## Purpose

The purpose of this crate is to create an explicit audit boundary before candidate generation, ranking, OT scoring, and learner-state estimation.

No-oracle means those stages must not use future edits, final corrected text, gold labels, teacher corrections, human corrections, answer keys, or post-hoc annotations.

## Input and Output

Input:

- `RawEvent`
- `RevisionEvent`
- `MicroEpisode`
- metadata field-name lists for synthetic tests or future adapters

Output:

- `NoOracleAuditReport`
- zero or more `NoOracleAuditIssue` values

## Usage

```rust
use kslog_no_oracle_audit::{
    audit_micro_episode,
    NoOracleUseContext,
};

let report = audit_micro_episode(&episode, NoOracleUseContext::ForCandidateGeneration);
```

## Test Method

From the repository root:

```bash
cargo test -p kslog_no_oracle_audit
```

Tests use only synthetic fixtures.

## What This Crate Checks

The first version checks forbidden field names and use-context risks for:

- `final_text`
- `final_corrected_text`
- `observed_after_text`
- `gold_label`
- `teacher_correction`
- `human_correction`
- `post_hoc_annotation`
- `target_label`
- `answer_key`
- `corrected_sentence`
- `future_edit`
- `future_context`

It also flags `MicroEpisode.local_context_after_observed` as unsafe for candidate generation, ranking, OT scoring, and learner-state estimation.

## Use Contexts

`ForCandidateGeneration` and `ForRanking` are no-oracle modeling contexts. They must not use observed post-edit context or forbidden gold/future fields.

`ForEvaluation` may use observed post-edit context because evaluation may compare predictions to observed outcomes after the fact. It still must not treat gold labels or teacher corrections as candidate-generation inputs.

`ForReplayVerification` may use observed replay artifacts to check reconstruction.

`ForArchival` stores artifacts but should not be confused with no-oracle modeling input.

## What This Crate Does Not Do Yet

- It does not implement candidate generation.
- It does not implement ranking.
- It does not implement OT scoring.
- It does not estimate learner state.
- It does not scan arbitrary serialized JSON files.
- It does not replace human review of release artifacts.

## Data Policy

Audit reports may include artifact IDs and field names. Do not commit audit reports derived from real participant data unless they have passed institution-approved review.

