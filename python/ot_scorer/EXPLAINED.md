# Candidate Feature Schema Explained

## 1. Beginner summary

This component turns generated candidates into simple structural features, unweighted constraint-violation records, and prototype weighted scores.

It prepares the first weighted OT scoring prototype, but it still does not evaluate correctness.

## 2. What this component does

It reads `CandidateSet` JSONL, checks for no-oracle leakage, and writes `CandidateFeatureSet` JSONL.

The features are intentionally simple: action family, placeholder flags, description length, and feature-note count.

It can also read `CandidateFeatureSet` JSONL and write `ConstraintViolationSet` JSONL.

Finally, it can read `ConstraintViolationSet` JSONL and write `CandidateScoreSet` JSONL with prototype `weighted_score` and deterministic `rank`.

It can also summarize `ConstraintViolationSet` JSONL into count-only
diagnostic summaries for synthetic wiring checks.

It also defines hand-weight config schema models, a strict validation helper,
and a separate explicit config-aware scorer function for unit-tested synthetic
config experiments. That function is not connected to the scorer CLI, E2E
pipeline, or summary collector, so default scoring behavior is unchanged.
The config-aware scorer tests are boundary tests only; they do not make
performance, F1, accuracy, calibration, grammar-correctness, or learner-state
claims.

It also provides a validation CLI for those config files. The CLI prints only a
safe count summary and does not print config bodies, score output, ranking
output, evaluation results, expected action details, JSONL content, or raw text.

It also provides a no-config scoring fixture lock helper. That helper compares
synthetic `CandidateScoreSet` output against a locked synthetic fixture and
prints safe summary only. The default lock covers `deletion_case`,
`selection_edit_case`, and `cursor_movement_case`. It does not connect config
to scoring.

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

Input for diagnostic summary: `ConstraintViolationSet` JSONL.

Output from diagnostic summary: one JSON file with aggregate counts only.

Input for hand-weight config validation: one synthetic config JSON file.

Output from hand-weight config validation: typed dataclass models in memory, or
a CLI safe summary containing validation status, schema/config names, and count
fields. No `CandidateScoreSet` output is changed by this validation.

Input for no-config score fixture lock: expected and generated synthetic
`CandidateScoreSet` JSONL files.

Output from no-config score fixture lock: safe match/mismatch summary only.
The JSONL body is not printed.

The output is a feature schema for later experiments.

## 5. Step-by-step mechanism

1. Read CandidateSet JSONL line by line.
2. Parse each line as JSON.
3. Reject forbidden fields such as `final_text`, `observed_after_text`, `gold_label`, `teacher_correction`, and `local_context_after_observed`.
4. For each candidate, compute structural features from candidate metadata.
5. Add leakage flags if a candidate claims to use observed edit text or is not marked no-oracle safe.
6. Write feature sets as JSONL.
7. Optionally read feature sets and create unweighted constraint-violation records.
8. Optionally read constraint records and compute prototype weighted scores.
9. Assign deterministic ranks within each episode.
10. Optionally summarize constraint records into count-only diagnostic JSON.
11. Optionally validate a synthetic hand-weight config and print only a safe
    count summary. This does not run scoring and does not connect the config to
    the scorer.
12. Optionally compare generated no-config score output with a locked synthetic
    score fixture. This checks regression behavior only and does not evaluate
    ranking correctness.

## 6. Important data structures

`CandidateFeature` describes one candidate's structural features.

Important structural features include `candidate_metadata_complete`, `has_generation_rule`, `has_action_family`, `is_safety_relevant_candidate`, `is_placeholder_candidate`, `is_grammar_family_candidate`, `is_local_edit_family_candidate`, `is_hold_candidate`, and `candidate_family_bucket`.

`candidate_feature_schema_v0_3` also adds no-oracle-safe local pattern
features: `context_before_length_bucket`, cursor boundary booleans, selection
span buckets, whitespace/punctuation ending booleans, and `left_char_class`.
These are abstract booleans or buckets. The raw `local_context_before` text is
not stored in `CandidateFeatureSet`.

These fields are derived from candidate metadata, action taxonomy, and leakage flags. They do not add candidate descriptions, proposed edit payloads, local context text, observed edit text, final text, or expected actions.

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

`diagnostic_summary_schema_v0_1` records aggregate counts, such as total
constraints, observed constraint IDs, local pattern diagnostic counts, and
linguistic placeholder counts. It does not contain per-episode text detail or
raw JSONL content.

`HandWeightConfig` describes a future hand-weight config. It contains policy
metadata, score-active family declarations, blocking constraints,
score-neutral constraints, no-oracle review metadata, expected-action usage
policy, and `ConstraintWeightEntry` records. The model is validation-only at
this stage and is not used by `build_candidate_score_set`.

## 7. Theory behind the implementation

The design separates feature extraction from scoring. This makes it possible to audit the input boundary before any model, ranker, or OT-style weighted constraint system is introduced.

Only non-content structural features and coarse pre-edit local pattern features
are used in this prototype. Local pattern features summarize shape, such as
length bucket or final-character class, without storing text.

The constraint schema separates penalty constraints from descriptive constraints. Penalty constraints count leakage and unsafe-candidate problems. Descriptive constraints record candidate categories for future scoring experiments.

The structural descriptive constraints include rule presence, action-family
presence, metadata completeness, family membership, placeholder-family
membership, safety relevance, and family-bucket presence. They are
interpretation records only: their violation count is `0`, and they do not
change `weighted_score` or rank.

The linguistic placeholder descriptive constraints record whether a candidate
belongs to article, number, subject-verb-agreement, tense, preposition, or
punctuation placeholder families. They do not decide whether the grammar is
correct.

The local pattern diagnostic descriptive constraints record v0.3 local pattern
feature states such as context-length bucket, cursor boundary, selection span
bucket, whitespace/punctuation ending flags, and left-character class. They use
only already-extracted no-oracle-safe buckets, booleans, and enums. They do not
store or reconstruct raw local context text.

The non-leaky linguistic diagnostic descriptive constraints combine
grammar-placeholder candidate metadata with those v0.3 abstract features. They
record whether a grammar candidate has relevant pre-edit diagnostic context,
but they do not decide whether a sentence is grammatically correct.

The scorer uses blocking constraints as safety gates. It does not learn from data and does not use gold labels.

The score output includes `action_type` explicitly so evaluation does not need to infer candidate class from the string shape of `candidate_id`. It also carries `generation_rule` and `action_family` so later analysis can inspect why a candidate exists without adding candidate descriptions, proposed edit payloads, local context text, or observed edit text to the score output.

The hand-weight config validator is separate from scoring. It rejects unsafe
or ambiguous config files before any future loader is connected, but it does
not change weights, formula, blocking, or tie-break behavior.

The config validation CLI is also separate from scoring. It is a smoke-check
entry point for schema validation only.

The no-config score fixture lock is separate from config support. It checks
that default score output stays stable when no config is supplied.

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

Feature, constraint, and score output exclude candidate descriptions, proposed
edit payloads, raw local context text, post-edit context, and observed edit
text.

Diagnostic summary output is count-only and also excludes those fields.

## 14. Tests added

Tests cover loading CandidateSet JSONL, feature-set construction, forbidden
field rejection, post-edit context rejection, leakage flag detection,
hold/local/grammar feature classification, v0.3 local pattern feature buckets
and character classes, local pattern diagnostic constraints, text-fragment
exclusion, constraint generation, diagnostic summary counts,
penalty/descriptive constraint behavior, scorer blocking, deterministic
tie-break, unique ranks, and source scanning for `eval`, `exec`, and `pickle`.

They also cover hand-weight config validation, including valid synthetic
config loading, forbidden field rejection, duplicate constraint rejection,
non-finite weight rejection, active-weight rationale requirements,
no-oracle-safe reason requirements, unknown constraint rejection, unsafe path
string rejection, synthetic-only notice requirements, expected-action tuning
policy rejection, validation CLI success/failure behavior, safe CLI stdout, and
default scoring behavior remaining unchanged.

They also cover no-config score fixture lock matching, rank mismatch,
weighted-score mismatch, schema mismatch, missing generated file, unsafe path,
config field leakage in default output, forbidden field leakage, and safe CLI
stdout.

## 15. Known limitations

The features, constraints, and scores are prototype records. They are not enough to claim the best candidate is correct.

Leakage flags are not a complete formal proof of no leakage. Future scorer-specific audits are still needed.

## 16. What to read next

Read `docs/09_ot_scoring_spec.md`, `docs/08_candidate_generation_spec.md`, and `docs/03_no_oracle_policy.md`.

For the future scoring policy roadmap, read `../../docs/scoring_policy_refinement_plan.md`.
For the beginner-friendly plan for linguistic placeholder constraints, read
`../../docs/linguistic_placeholder_constraint_plan.md`.
For the no-oracle plan for local pattern features, read
`../../docs/local_pattern_feature_plan.md`.
For the implemented v0.3 local pattern feature schema, read
`../../docs/local_pattern_feature_schema_v0_3_plan.md`.
For the descriptive diagnostic constraints based on those fields, read
`../../docs/local_pattern_diagnostic_constraint_plan.md`.
For future non-leaky linguistic diagnostic design, read
`../../docs/non_leaky_linguistic_constraint_design_plan.md`.
For the safe summary tooling for diagnostics, read
`../../docs/diagnostic_summary_tooling_plan.md`.
For future hand-weight config schema design, read
`../../docs/hand_weight_config_schema_plan.md`.
For future explicit scorer config CLI design, read
`../../docs/explicit_config_cli_option_design.md`.
