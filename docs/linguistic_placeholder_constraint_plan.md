# Linguistic Placeholder Constraint Plan

This document is a design plan for linguistic placeholder constraints.

The first descriptive constraints from this plan are now implemented in
`python/ot_scorer/constraint_builder.py`. They do not change scorer weights,
the scoring formula, tie-break policy, evaluation metrics, or learner-state
estimation.

## 1. Purpose

Linguistic placeholder constraints are a planned intermediate layer before deep linguistic validity checks.

Their first purpose is to record candidate type, action family, and generation rule in a more interpretable way.

They should answer questions like:

- Does this candidate belong to an article-related placeholder family?
- Does this candidate belong to a tense-related placeholder family?
- Does this candidate represent a punctuation placeholder?

They should not answer:

- Is the learner's sentence grammatically correct?
- Is this the best correction?
- Does this match a teacher correction?
- Does this improve final writing quality?

In the first implementation, these constraints should be descriptive records only. They must not affect `weighted_score` or rank.

## 2. Target Candidates

The planned constraints cover the current grammar-placeholder action taxonomy:

- `article_fix_placeholder`
- `number_fix_placeholder`
- `sva_fix_placeholder`
- `tense_fix_placeholder`
- `preposition_fix_placeholder`
- `punctuation_fix_placeholder`

These candidates are placeholders. They name a possible revision family, but they do not yet contain a fully validated correction.

## 3. Constraint Candidates

Implemented descriptive constraint ids:

- `ARTICLE-PLACEHOLDER-CANDIDATE`
- `NUMBER-PLACEHOLDER-CANDIDATE`
- `SVA-PLACEHOLDER-CANDIDATE`
- `TENSE-PLACEHOLDER-CANDIDATE`
- `PREPOSITION-PLACEHOLDER-CANDIDATE`
- `PUNCTUATION-PLACEHOLDER-CANDIDATE`

Each implemented constraint is:

- `constraint_type = "descriptive"`
- `severity = "info"`
- `violation_count = 0`
- `observed = true` only when the candidate matches that placeholder family

The word "constraint" here means an OT-style named record. It does not yet mean a penalty.

## 4. Information Allowed

These constraints may use only no-oracle-safe candidate metadata:

- `action_type`
- `generation_rule`
- `action_family`
- `candidate_family_bucket`
- `no_oracle_safe`
- `leakage_flags`
- `uses_observed_edit_text`
- candidate metadata completeness flags

They may use structural feature flags already present in `CandidateFeatureSet`, such as:

- `is_grammar_family_candidate`
- `is_placeholder_candidate`
- `has_generation_rule`
- `has_action_family`

## 5. Information Forbidden

These constraints must not use:

- `final_text`
- `observed_after_text`
- `gold_label`
- teacher correction
- human correction
- post-hoc annotation
- future edits
- future context
- `local_context_after_observed`
- synthetic expected action
- real participant data

They also must not inspect raw participant text, candidate descriptions, proposed edit payloads, or local context text unless a later design explicitly proves that the feature is no-oracle safe and privacy-safe.

## 6. Violation Count and Scoring

Initial linguistic placeholder constraints should be descriptive only.

Policy:

- `violation_count = 0`
- do not add to `weighted_score`
- do not change blocking behavior
- do not change tie-break policy
- do not mix with safety blocking constraints

The weighted scorer should continue to treat blocking constraints separately from descriptive records.

If future work introduces non-zero linguistic weights, that must be documented in a separate scoring-policy change with tests and no-oracle review.

## 7. Why Not Judge Linguistic Validity Yet

The current system should not deeply judge linguistic correctness yet because:

- many candidates are placeholders, not fully realized edits
- local context pattern features are still limited
- using post-edit context would create no-oracle leakage
- using final corrected text would turn evaluation data into scoring input
- hand-written grammar rules can become brittle and misleading
- synthetic expected actions are wiring fixtures, not real gold labels
- the project is not ready to make performance claims

For now, the safer goal is to record that a candidate belongs to a linguistic placeholder family.

## 8. Beginner Explanation

### Article

Article revisions involve words such as "a", "an", and "the".

These matter in L2 English writing because many learners' first languages do not mark articles in the same way English does.

### Number

Number revisions involve singular and plural forms.

Examples include choosing between a singular noun and a plural noun, but this plan does not implement that judgment yet.

### SVA

SVA means subject-verb agreement.

It concerns whether a verb form matches the subject. For example, third-person singular present tense is a common L2 English difficulty.

### Tense

Tense revisions involve time-related verb forms.

The first placeholder constraint should only record that a candidate is tense-related; it should not decide whether the tense is correct.

### Preposition

Preposition revisions involve words such as "in", "on", "at", "to", and "for".

Prepositions are frequent revision targets in L2 English because usage differs across languages and contexts.

### Punctuation

Punctuation revisions involve marks such as periods, commas, and question marks.

The placeholder constraint should record the candidate family, not judge the whole sentence's punctuation quality.

### Why Record Candidate Type Instead of Correctness

At this stage, candidate generation is still placeholder-based.

Recording candidate type is useful for debugging and later constraint design. Claiming correctness would require stronger linguistic modeling, careful evaluation design, and strict no-oracle safeguards.

## 9. Roadmap

### Step A: Implement Placeholder Descriptive Constraints

Add the six linguistic placeholder constraints as descriptive records with `violation_count=0`.

Status: completed for the six initial placeholder families. The constraints are
descriptive records only and do not affect score or rank.

### Step B: Review Non-Leaky Local Pattern Features

Consider structural features that can be derived from pre-edit context without exposing raw text or future information.

Examples may include length or punctuation-adjacent flags, but only after privacy and leakage review.

See [Local pattern feature plan](local_pattern_feature_plan.md) before
implementing any local context abstraction.

For the next design layer that combines linguistic placeholder categories with
no-oracle-safe local pattern features, see
[Non-leaky linguistic constraint design plan](non_leaky_linguistic_constraint_design_plan.md).

### Step C: Design Interpretable Linguistic Constraints

If richer linguistic constraints are added, each should have:

- a clear input boundary
- a beginner-readable explanation
- no-oracle review
- tests using synthetic data only
- no performance claim

### Step D: Document Hand-Designed Weights

If any non-safety weight is introduced later, document:

- formula
- variable meanings
- weight value
- rationale
- why it is hand-designed and not learned

### Step E: Synthetic Smoke Checks

Run synthetic E2E checks to verify wiring only.

Do not present F1, accuracy, calibration, or research performance.

### Step F: Private Validation Design Later

Only after synthetic behavior is stable, design a private validation protocol.

That later design must keep expected labels out of candidate generation, constraints, and scoring.

## 10. Non-Goals

This plan does not:

- change scoring
- add weights
- add ranking logic
- evaluate real data
- introduce real gold labels
- use teacher corrections
- implement F1, accuracy, calibration, or learner-state estimation
- permit public storage of real participant data
