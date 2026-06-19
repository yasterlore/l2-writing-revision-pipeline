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

## Safe Episode View

Before candidate generation, ranking, or OT scoring, code should prefer `NoOracleSafeEpisodeView` from `crates/kslog_no_oracle_audit/` rather than passing full `MicroEpisode` values.

`NoOracleSafeEpisodeView` includes pre-edit context such as `local_context_before` and excludes `local_context_after_observed`.

The safe view also excludes forbidden fields such as `final_text`, `observed_after_text`, `gold_label`, and teacher corrections.

However, the safe view is not universally safe. If the prediction task is to predict inserted or deleted text, then `inserted_text_observed` and `deleted_text_observed` can be target leakage and should be excluded with safe-view options or a narrower task-specific view.

Safe view outputs may still contain writing fragments and must not be committed when derived from real participant data.

## Safe View Export

Rust CLI safe-view export is the approved pre-processing boundary before future Python candidate generation prototypes.

Export must use `NoOracleSafeEpisodeView`, not full `MicroEpisode`.

Safe-view export must not include:

- `local_context_after_observed`
- `final_text`
- `observed_after_text`
- `gold_label`
- teacher corrections
- human corrections
- answer keys
- post-hoc annotations

Observed edit text is excluded by default. It may be included only by an explicit option and only when the prediction task definition permits it. If the model is supposed to predict inserted or deleted text, observed edit text is target leakage.

Safe-view export files derived from real participant data must not be stored in this repository.

## Python Candidate Generation Prototype

The Python candidate generation prototype reads only Rust-exported `NoOracleSafeEpisodeView` JSONL.

It must reject input containing forbidden field names, including `local_context_after_observed`, `final_text`, `observed_after_text`, `gold_label`, and `teacher_correction`.

The prototype may use `local_context_before`, event-shape metadata, and quality flags. It must not use observed post-edit context.

Observed edit text is ignored by default even if present in a safe-view export. Candidate outputs must mark `uses_observed_edit_text=false` unless a future task-specific design explicitly permits otherwise and documents the leakage risk.

Candidate generation produces unranked placeholder candidates. It is not an evaluation step and does not create gold labels.

## Candidate Feature Extraction

The Python candidate feature step reads `CandidateSet` JSONL and prepares structural features for future OT scoring.

It must not use candidate descriptions as text features, proposed edit payloads, observed edit text, final text, post-edit context, gold labels, or teacher corrections.

Allowed first-version features are structural fields such as `action_type`, `generation_rule`, action-family flags, description length, and feature-note count.

If a candidate or candidate set has `uses_observed_edit_text=true` or `no_oracle_safe=false`, the feature step must flag it as a leakage concern before any scorer can use it.

## Constraint Violation Generation

The Python constraint prototype reads only `CandidateFeatureSet` JSONL and produces unweighted constraint-violation records.

Penalty constraints may record no-oracle problems such as leakage flags, observed edit text use, or unsafe candidates.

Descriptive constraints may record candidate categories such as hold, local edit, grammar placeholder, or placeholder. These descriptive records are not correctness labels and are not rankings.

The constraint step must not read local context text, observed edit text, final text, gold labels, teacher corrections, or post-edit context.

## Weighted Scoring Prototype

The weighted OT scorer prototype reads only `ConstraintViolationSet` JSONL.

It may use constraint IDs, violation counts, constraint types, and descriptive candidate-type records. It must not use writing text, observed edit text, final text, gold labels, teacher corrections, or post-edit context.

Leakage-related constraints are blocking. If a candidate violates `NO-LEAKAGE-FLAG`, `NO-OBSERVED-EDIT-TEXT`, or `NO-UNSAFE-CANDIDATE`, it must be marked blocked before ranking.

Prototype ranking is not a correctness label and must not be evaluated as gold accuracy until a separate evaluation design exists.

## Synthetic Evaluation Prototype

The evaluation prototype may use synthetic expected actions only after scoring is complete.

Expected actions must not feed back into candidate generation, feature extraction, constraint generation, weighted scoring, or rank adjustment.

Synthetic expected actions are not real gold labels, teacher corrections, final corrected text, or participant outcomes.

The evaluator must reject forbidden fields such as `final_text`, `observed_after_text`, `gold_label`, and `teacher_correction`.

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
