# No-Oracle Policy

No-oracle components must operate only on information that would be available at the relevant moment in the writing process.

## Forbidden Inputs

Candidate generation, ranking, OT scoring, and learner-state estimation must not use:

- final corrected text
- observed future edits
- gold labels
- post-hoc annotations
- `observed_after_text`
- `final_text`
- teacher corrections
- human corrections after writing

## Required Design Pattern

Any no-oracle component must document:

- the exact input fields it consumes
- the timestamp or process boundary for those inputs
- fields explicitly excluded for no-oracle safety
- tests or audits used to catch leakage

## Audit Layer

The Rust `kslog_no_oracle_audit` crate will eventually provide deterministic checks for no-oracle field use and dataset splits.

The initial audit crate lives in `crates/kslog_no_oracle_audit/`.

## Use Contexts

No-oracle safety depends on how an artifact is used.

- `ForCandidateGeneration`: must not use future, gold, post-hoc, or observed post-edit context.
- `ForRanking`: must not use future, gold, post-hoc, or observed post-edit context.
- `ForOtScoring`: must not use future, gold, post-hoc, or observed post-edit context.
- `ForLearnerStateEstimation`: must not use future, gold, post-hoc, or observed post-edit context.
- `ForEvaluation`: may use observed outcomes after prediction, but not as candidate-generation input.
- `ForReplayVerification`: may use observed replay artifacts to check deterministic reconstruction.
- `ForArchival`: may store artifacts, but archival storage does not make them safe model inputs.

`MicroEpisode.local_context_after_observed` is allowed to exist for reconstruction checks and evaluation. It is no-oracle unsafe for candidate generation, ranking, OT scoring, and learner-state estimation.

## Forbidden Field Names

The audit policy treats the following as forbidden concepts:

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
