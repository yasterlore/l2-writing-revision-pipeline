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
- `NoOracleSafeEpisodeView`
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

To create a candidate-generation-oriented safe view:

```rust
use kslog_no_oracle_audit::NoOracleSafeEpisodeView;

let safe_view = NoOracleSafeEpisodeView::try_from_micro_episode(&episode);
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

## NoOracleSafeEpisodeView

`MicroEpisode` is a broad representation for observation, replay verification, and evaluation. It contains `local_context_after_observed`, which is no-oracle unsafe for candidate generation and ranking.

`NoOracleSafeEpisodeView` is a narrower view intended for candidate generation, ranking, and OT scoring inputs. It includes `local_context_before` and excludes `local_context_after_observed`.

The safe view also excludes `final_text`, `observed_after_text`, `gold_label`, and teacher correction fields.

`inserted_text_observed` and `deleted_text_observed` are retained by default because they describe the observed edit action. Depending on the prediction task, however, these can become target leakage. Use `NoOracleSafeEpisodeViewOptions { include_observed_edit_text: false }` when the model is supposed to predict the edit text itself.

The safe view is not universally safe. It must be audited together with the exact prediction-task definition.

## Safe-View JSONL Export

`kslog_cli export-safe-view` can export one `NoOracleSafeEpisodeView` per JSONL line for synthetic downstream Python candidate-generation prototypes.

The export contains the narrowed safe view only. It does not include `local_context_after_observed`, `final_text`, `observed_after_text`, `gold_label`, teacher correction fields, or full `MicroEpisode` artifacts.

Observed edit text is excluded by default in the CLI export. It can be included only with `--include-observed-edit-text`, and this may be target leakage if the prediction task is to predict the inserted or deleted text.

Do not commit safe-view exports derived from real participant data. Use synthetic data only in this repository.

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
- It does not implement candidate generation from the safe view.

## Data Policy

Audit reports may include artifact IDs and field names. Do not commit audit reports derived from real participant data unless they have passed institution-approved review.

Safe view output may still contain writing fragments in `local_context_before`, `inserted_text_observed`, or `deleted_text_observed`. Do not commit safe view outputs derived from real participant data.
