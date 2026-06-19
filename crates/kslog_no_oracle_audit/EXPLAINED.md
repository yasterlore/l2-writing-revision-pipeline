# kslog_no_oracle_audit Explained

## 1. Beginner Summary

`kslog_no_oracle_audit` checks whether a data object might accidentally reveal information that a model should not know at prediction time.

For example, a candidate generator should not see the final corrected text or a teacher's correction. If it did, the experiment would be unfair because the model would be looking at the answer.

## 2. What This Component Does

This component:

- defines no-oracle use contexts
- defines risk levels
- reports forbidden field names
- checks `RawEvent`, `RevisionEvent`, and `MicroEpisode` field policies
- flags `local_context_after_observed` as unsafe for candidate generation and ranking
- creates `NoOracleSafeEpisodeView`, a narrower input view for candidate generation and ranking

## 3. What This Component Does Not Do

This component does not:

- generate candidates
- rank candidates
- run OT scoring
- estimate learner state
- implement Python analysis
- read real participant data
- decide whether a learner's edit is correct

## 4. Input and Output

Input can be a `RawEvent`, `RevisionEvent`, `MicroEpisode`, `NoOracleSafeEpisodeView`, or a synthetic list of metadata field names.

Output is a `NoOracleAuditReport` containing zero or more `NoOracleAuditIssue` records.

## 5. Step-by-Step Mechanism

1. Choose a use context, such as `ForCandidateGeneration` or `ForEvaluation`.
2. Inspect known field names for forbidden no-oracle terms.
3. For micro-episodes, check whether post-edit observed context is being used in a no-oracle modeling context.
4. When needed, create a `NoOracleSafeEpisodeView` that excludes post-edit observed context.
5. Emit issues with a risk level.
6. Return a report instead of panicking.

## 6. Important Data Structures

`NoOracleUseContext` describes how the artifact will be used.

`NoOracleRiskLevel` describes how serious an issue is.

`NoOracleAuditIssue` describes one audit finding.

`NoOracleAuditReport` summarizes a whole audit.

`NoOracleSafeEpisodeView` contains only the fields intended to be passed toward candidate generation, ranking, or OT scoring. It excludes `local_context_after_observed`.

## 7. Theory Behind the Implementation

No-oracle policy protects research validity. A model or scoring method must not use information from the future or from an answer key when making a prediction.

Without this boundary, candidate generation or ranking could look artificially strong because it would be allowed to see the result it is supposed to predict.

## 8. Mathematical Formulas, If Any

No mathematical formulas are used in this component.

## 9. Weighting Rationale, If Weights Are Used

No weights are used in this component.

## 10. Ranking Rationale, If Ranking Is Used

No ranking is used in this component.

## 11. Why This Design Was Selected Over Alternatives

The first version uses explicit field-name policies because the current Rust types are strongly typed and do not include forbidden fields.

The audit also checks use context because the same field can be acceptable for evaluation but unsafe for candidate generation.

The safe view exists because field-name auditing alone is not enough. It is safer to create a smaller type that simply cannot carry `local_context_after_observed`.

## 12. Security and Privacy Considerations

Tests use synthetic fixtures only.

The crate does not read `private_data/`, `real_data/`, or `participant_data/`.

It rejects or flags concepts such as `final_text`, `observed_after_text`, `gold_label`, teacher corrections, human corrections, answer keys, and future context.

Audit reports derived from real participant data must not be committed to this repository.

Safe view output may still contain writing fragments in `local_context_before`, `inserted_text_observed`, or `deleted_text_observed`. Do not commit safe view outputs derived from real participant data.

The crate uses no `unsafe` Rust.

## 13. Tests Added

The tests cover:

- valid synthetic micro-episode audit for evaluation
- candidate-generation audit flagging `local_context_after_observed`
- ranking audit flagging `local_context_after_observed`
- forbidden metadata fields `final_text`, `observed_after_text`, and `gold_label`
- core type field names not colliding with forbidden names
- RawEvent and RevisionEvent audit paths
- empty metadata audit without panic
- creating a safe view from a synthetic micro-episode
- preserving `local_context_before`
- excluding `local_context_after_observed`
- confirming forbidden field names are not part of the safe view
- candidate-generation audit of the safe view
- optional exclusion of observed edit text

## 14. Known Limitations

The first version audits known Rust field names and synthetic metadata field names. It does not scan arbitrary JSON documents or nested user-defined structures.

It cannot prove that downstream code never uses unsafe fields. Later steps should enforce this at API boundaries.

`NoOracleSafeEpisodeView` is safer than `MicroEpisode`, but it is not universally safe. If a task asks the model to predict inserted or deleted text, then `inserted_text_observed` or `deleted_text_observed` may be target leakage and should be excluded.

## 15. What To Read Next

- `docs/03_no_oracle_policy.md`
- `docs/08_candidate_generation_spec.md`
- `docs/09_ot_scoring_spec.md`
- `crates/kslog_micro_episode/README.md`
