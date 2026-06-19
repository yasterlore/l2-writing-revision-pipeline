# Candidate Feature Schema Explained

## 1. Beginner summary

This component turns generated candidates into simple structural features, unweighted constraint-violation records, and prototype weighted scores.

It prepares the first weighted OT scoring prototype, but it still does not evaluate correctness.

## 2. What this component does

It reads `CandidateSet` JSONL, checks for no-oracle leakage, and writes `CandidateFeatureSet` JSONL.

The features are intentionally simple: action family, placeholder flags, description length, and feature-note count.

It can also read `CandidateFeatureSet` JSONL and write `ConstraintViolationSet` JSONL.

Finally, it can read `ConstraintViolationSet` JSONL and write `CandidateScoreSet` JSONL with prototype `weighted_score` and deterministic `rank`.

## 3. What this component does not do

It does not implement evaluation, F1, calibration, selective prediction, learner-state estimation, or grammar correction.

It does not use raw browser events or full micro-episodes.

## 4. Input and output

Input for feature extraction: one `CandidateSet` per JSONL line.

Output from feature extraction: one `CandidateFeatureSet` per JSONL line.

Input for constraint generation: one `CandidateFeatureSet` per JSONL line.

Output from constraint generation: one `ConstraintViolationSet` per JSONL line.

Input for scoring: one `ConstraintViolationSet` per JSONL line.

Output from scoring: one `CandidateScoreSet` per JSONL line.

The output is a feature schema for later experiments.

## 5. Step-by-step mechanism

1. Read CandidateSet JSONL line by line.
2. Parse each line as JSON.
3. Reject forbidden fields such as `final_text`, `observed_after_text`, `gold_label`, `teacher_correction`, and `local_context_after_observed`.
4. For each candidate, compute structural features.
5. Add leakage flags if a candidate claims to use observed edit text or is not marked no-oracle safe.
6. Write feature sets as JSONL.
7. Optionally read feature sets and create unweighted constraint-violation records.
8. Optionally read constraint records and compute prototype weighted scores.
9. Assign deterministic ranks within each episode.

## 6. Important data structures

`CandidateFeature` describes one candidate's structural features.

`CandidateFeatureSet` groups all candidate features for one episode.

`leakage_flags` records no-oracle concerns without using private text.

`Constraint` describes a named constraint.

`ConstraintViolation` records whether a candidate violates or matches a constraint.

`ConstraintViolationSet` groups constraint records for one episode.

`ConstraintWeight` defines a fixed prototype weight for a constraint.

`CandidateScore` stores candidate id, episode id, explicit `action_type`, `generation_rule`, `action_family`, weighted score, block status, block reasons, rank, and constraint contributions.

`candidate_id` identifies the candidate. `action_type` describes the candidate action category and is copied from candidate generation through constraint generation into score output.

`generation_rule` records which candidate-generation rule produced the candidate. `action_family` records the broad candidate family, such as hold, local edit, grammar placeholder, or other. These fields are carried for interpretation and debugging; they do not change the score formula or rank policy.

`CandidateScoreSet` groups candidate scores for one episode.

## 7. Theory behind the implementation

The design separates feature extraction from scoring. This makes it possible to audit the input boundary before any model, ranker, or OT-style weighted constraint system is introduced.

Only non-content structural features are used in the first version.

The constraint schema separates penalty constraints from descriptive constraints. Penalty constraints count leakage and unsafe-candidate problems. Descriptive constraints record candidate categories for future scoring experiments.

The scorer uses blocking constraints as safety gates. It does not learn from data and does not use gold labels.

The score output includes `action_type` explicitly so evaluation does not need to infer candidate class from the string shape of `candidate_id`. It also carries `generation_rule` and `action_family` so later analysis can inspect why a candidate exists without adding candidate descriptions, proposed edit payloads, local context text, or observed edit text to the score output.

## 8. Mathematical formulas, if any

The weighted score is:

```text
weighted_score(c) = sum_i w_i * v_i(c)
```

where `c` is a candidate, `i` indexes constraints, `w_i` is the fixed prototype weight for constraint `i`, and `v_i(c)` is that candidate's violation count for constraint `i`.

## 9. Meaning of each variable in the formula

`c`: the candidate being scored.

`i`: a constraint index.

`w_i`: the hand-designed prototype weight for constraint `i`.

`v_i(c)`: the violation count for candidate `c` under constraint `i`.

`weighted_score(c)`: the total penalty score. Lower is better in this prototype.

## 10. Weighting rationale, if weights are used

Blocking constraints use weight `1_000_000.0` because they represent no-oracle safety failures.

Descriptive constraints use weight `0.0` because they describe candidate type but should not influence score yet.

The weights are not learned. They are initial hand-designed safety policy values.

## 11. Ranking rationale, if ranking is used

Candidates are ranked deterministically within each episode.

Blocked candidates are placed after unblocked candidates. Among equal-score unblocked candidates, the tie-break order is hold, local edit, grammar placeholder, other placeholder, then other.

This ranking is not a gold correctness prediction.

## 12. Why this design was selected over alternatives

Starting with structural features and safety-first blocking avoids premature modeling and reduces leakage risk.

It also makes the future scoring input easier to review.

## 13. Security and privacy considerations

Use synthetic data only in this repository.

The loader rejects forbidden no-oracle fields recursively. It does not use `pickle`, `eval`, `exec`, unsafe deserialization, or network access.

Feature, constraint, and score output exclude candidate descriptions, proposed edit payloads, local context text, and observed edit text.

## 14. Tests added

Tests cover loading CandidateSet JSONL, feature-set construction, forbidden field rejection, post-edit context rejection, leakage flag detection, hold/local/grammar feature classification, text-fragment exclusion, constraint generation, penalty/descriptive constraint behavior, scorer blocking, deterministic tie-break, unique ranks, and source scanning for `eval`, `exec`, and `pickle`.

## 15. Known limitations

The features, constraints, and scores are prototype records. They are not enough to claim the best candidate is correct.

Leakage flags are not a complete formal proof of no leakage. Future scorer-specific audits are still needed.

## 16. What to read next

Read `docs/09_ot_scoring_spec.md`, `docs/08_candidate_generation_spec.md`, and `docs/03_no_oracle_policy.md`.

For the future scoring policy roadmap, read `../../docs/scoring_policy_refinement_plan.md`.
