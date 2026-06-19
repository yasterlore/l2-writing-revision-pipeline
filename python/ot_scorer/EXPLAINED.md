# Candidate Feature Schema Explained

## 1. Beginner summary

This component turns generated candidates into simple structural features and then can turn those features into unweighted constraint-violation records.

It prepares data for future OT scoring, but it does not score, weight, or rank anything yet.

## 2. What this component does

It reads `CandidateSet` JSONL, checks for no-oracle leakage, and writes `CandidateFeatureSet` JSONL.

The features are intentionally simple: action family, placeholder flags, description length, and feature-note count.

It can also read `CandidateFeatureSet` JSONL and write `ConstraintViolationSet` JSONL.

## 3. What this component does not do

It does not implement OT scoring, weights, ranking, evaluation, learner-state estimation, or grammar correction.

It does not use raw browser events or full micro-episodes.

## 4. Input and output

Input for feature extraction: one `CandidateSet` per JSONL line.

Output from feature extraction: one `CandidateFeatureSet` per JSONL line.

Input for constraint generation: one `CandidateFeatureSet` per JSONL line.

Output from constraint generation: one `ConstraintViolationSet` per JSONL line.

The output is a feature schema for later experiments.

## 5. Step-by-step mechanism

1. Read CandidateSet JSONL line by line.
2. Parse each line as JSON.
3. Reject forbidden fields such as `final_text`, `observed_after_text`, `gold_label`, `teacher_correction`, and `local_context_after_observed`.
4. For each candidate, compute structural features.
5. Add leakage flags if a candidate claims to use observed edit text or is not marked no-oracle safe.
6. Write feature sets as JSONL.
7. Optionally read feature sets and create unweighted constraint-violation records.

## 6. Important data structures

`CandidateFeature` describes one candidate's structural features.

`CandidateFeatureSet` groups all candidate features for one episode.

`leakage_flags` records no-oracle concerns without using private text.

`Constraint` describes a named constraint.

`ConstraintViolation` records whether a candidate violates or matches a constraint.

`ConstraintViolationSet` groups constraint records for one episode.

## 7. Theory behind the implementation

The design separates feature extraction from scoring. This makes it possible to audit the input boundary before any model, ranker, or OT-style weighted constraint system is introduced.

Only non-content structural features are used in the first version.

The constraint schema separates penalty constraints from descriptive constraints. Penalty constraints count leakage and unsafe-candidate problems. Descriptive constraints record candidate categories for future scoring experiments.

## 8. Mathematical formulas, if any

No mathematical formulas are used in this version.

## 9. Meaning of each variable in the formula

There are no formulas or formula variables in this version.

## 10. Weighting rationale, if weights are used

No weights are used. Weighting belongs to a later OT scorer step.

## 11. Ranking rationale, if ranking is used

No ranking is used. This component only creates feature and unweighted constraint records.

## 12. Why this design was selected over alternatives

Starting with structural features avoids premature modeling and reduces leakage risk.

It also makes the future scoring input easier to review.

## 13. Security and privacy considerations

Use synthetic data only in this repository.

The loader rejects forbidden no-oracle fields recursively. It does not use `pickle`, `eval`, `exec`, unsafe deserialization, or network access.

Feature and constraint output exclude candidate descriptions, proposed edit payloads, local context text, and observed edit text.

## 14. Tests added

Tests cover loading CandidateSet JSONL, feature-set construction, forbidden field rejection, post-edit context rejection, leakage flag detection, hold/local/grammar feature classification, text-fragment exclusion, constraint generation, penalty/descriptive constraint behavior, and source scanning for `eval`, `exec`, and `pickle`.

## 15. Known limitations

The features and constraint records are simple structural descriptors. They are not enough to choose the best candidate.

Leakage flags are not a complete formal proof of no leakage. Future scorer-specific audits are still needed.

## 16. What to read next

Read `docs/09_ot_scoring_spec.md`, `docs/08_candidate_generation_spec.md`, and `docs/03_no_oracle_policy.md`.
