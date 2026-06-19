# Scoring Policy Refinement Plan

This document describes how the current OT-style scoring prototype works and how it should be refined later.

It is a design plan only. It does not implement new scoring logic, learned weights, F1, accuracy, calibration, or learner-state estimation.

## 1. Current Scorer Role

The current scorer lives in `python/ot_scorer/`.

It reads:

```text
ConstraintViolationSet JSONL
```

and writes:

```text
CandidateScoreSet JSONL
```

The scorer does not decide whether a learner's revision is correct.

It does:

- apply no-oracle safety blocking constraints
- compute a prototype weighted score
- assign deterministic ranks inside one episode
- preserve candidate identity and `action_type`

It does not:

- validate learner correctness
- use gold labels
- use final corrected text
- estimate learner state
- claim model performance

The current rank is a deterministic prototype order, not a research result.

## 2. Current Scoring Formula

The current formula is:

```text
weighted_score(c) = sum_i w_i * v_i(c)
```

Variables:

- `c`: candidate being scored
- `i`: constraint index
- `w_i`: fixed prototype weight for constraint `i`
- `v_i(c)`: violation count for candidate `c` under constraint `i`
- `weighted_score(c)`: total penalty score; lower is better in this prototype

### Blocking Constraints

Current blocking constraints:

- `NO-LEAKAGE-FLAG`
- `NO-OBSERVED-EDIT-TEXT`
- `NO-UNSAFE-CANDIDATE`

If any blocking constraint has `violation_count > 0`, the candidate is marked:

```text
blocked = true
```

Blocked candidates are placed after unblocked candidates.

### Current Tie-Break Policy

Among unblocked candidates with the same score, the current deterministic tie-break is:

1. hold
2. local edit
3. grammar placeholder
4. other placeholder
5. other

This is not a correctness claim. It is only a stable ordering policy for prototype output.

## 3. Current Constraint Categories

### Safety / Blocking Constraints

Safety constraints protect the no-oracle boundary.

They are blocking because leakage is more serious than a bad rank.

### Descriptive Constraints

Descriptive constraints record candidate type:

- `HOLD-CANDIDATE`
- `LOCAL-EDIT-CANDIDATE`
- `GRAMMAR-PLACEHOLDER-CANDIDATE`
- `PLACEHOLDER-CANDIDATE`

They currently have weight `0.0`.

### Placeholder Constraints

Many candidates are placeholders. They represent possible edit families, not fully realized corrections.

Current placeholder behavior is useful for wiring tests, but it is not enough to evaluate linguistic validity.

### Linguistic Validity

The current scorer does not deeply evaluate:

- grammar correctness
- semantic appropriateness
- discourse fit
- learner-intended meaning
- whether a candidate matches a teacher correction

Those would require later modeling and stricter no-oracle review.

## 4. Current Temporary Choices

These are deliberate prototype choices:

- blocking weight is `1_000_000.0`
- descriptive constraints do not affect score
- tie-break is deterministic and hand-designed
- many candidates are placeholders
- action taxonomy is an initial version
- linguistic constraints are not implemented
- score output includes `action_type`
- score output preserves `generation_rule` and `action_family` for interpretation
- CandidateFeatureSet v0_3 includes no-oracle-safe local pattern buckets and
  booleans, but scoring does not use them yet

## 5. No-Oracle Policy

Scoring policy refinement must not use:

- `final_text`
- `observed_after_text`
- `gold_label`
- teacher correction
- human correction
- answer key
- future edits
- future context
- post-hoc annotations
- `local_context_after_observed`

Synthetic expected actions are evaluation-time fixtures only.

They must not be used to:

- tune weights
- choose constraints
- change ranks
- filter candidates before scoring
- train candidate generation

Any future validation or tuning must be explicitly separated from scoring-time information and must use learner-disjoint validation design.

## 6. Beginner Explanation

### What OT-Style Scoring Means Here

OT-style scoring means candidates are compared by named constraints.

Each constraint can record whether a candidate violates a policy or has a property.

The current system is inspired by this idea, but it is not a complete linguistic Optimality Theory model.

### What a Constraint Violation Is

A constraint violation is a structured record such as:

```text
candidate X violates NO-LEAKAGE-FLAG once
```

The scorer converts violations into scores using weights.

### Why Safety Blocking Comes First

If a candidate uses future information or unsafe observed text, it might look artificially good.

Blocking these candidates first prevents leakage from contaminating later experiments.

### Why There Are No Performance Metrics Yet

The current scorer is a prototype. The candidate set is placeholder-heavy, and expected actions are synthetic wiring fixtures.

Reporting F1, accuracy, or calibration now would make the project look more mature than it is.

## 7. Refinement Candidates

Future refinements should proceed cautiously.

Completed schema refinement:

- preserve `generation_rule` through scorer output
- preserve stable `action_family` through scorer output
- add CandidateFeatureSet v0_3 local pattern features without storing raw text

Possible future improvements:

- connect local pattern features to descriptive diagnostics
- separate safety constraints from linguistic constraints
- define interpretable linguistic placeholder constraints
- document any hand-designed non-safety weights
- add synthetic-only smoke checks for new constraints
- design validation-only tuning later, with learner-disjoint splits
- defer calibration and selective prediction until scoring semantics are stable

## 8. Stepwise Roadmap

### Step A: Preserve Rule Metadata

Carry `generation_rule` and possibly `action_family` through:

```text
CandidateSet
  -> CandidateFeatureSet
  -> ConstraintViolationSet
  -> CandidateScoreSet
```

Status: completed for `generation_rule` and `action_family`. They are metadata
only and do not change weights, blocking behavior, or tie-break order.

### Step B: Add Interpretable Non-Leaky Features

Status: initial structural metadata features have been added to
`CandidateFeatureSet`.

Current examples:

- action family
- candidate placeholder class
- candidate metadata completeness
- generation-rule presence
- action-family presence
- safety-relevant candidate flag
- candidate family bucket

Future examples:

- cursor-local edit flag
- safe structural context length
- punctuation-adjacent flag, if derived without post-edit context

Do not include raw context text in feature or score output.

See [Local pattern feature plan](local_pattern_feature_plan.md) for the
no-oracle and privacy boundary before implementing local context abstractions.
The initial schema proposal is in
[Local pattern feature schema v0.3 plan](local_pattern_feature_schema_v0_3_plan.md).

The descriptive diagnostic constraint design is in
[Local pattern diagnostic constraint plan](local_pattern_diagnostic_constraint_plan.md).
These planned constraints should keep `violation_count=0` and should not affect
`weighted_score`, blocking, or tie-break behavior.

### Step C: Add Linguistic Placeholder Constraints

Status: structural descriptive constraints have been added for metadata
completeness, rule presence, action-family presence, family membership,
placeholder-family membership, safety relevance, and family-bucket presence.
They remain descriptive and are not added to `weighted_score`.

Possible future linguistic placeholder constraints:

- article placeholder candidate present
- number agreement placeholder candidate present
- tense placeholder candidate present
- preposition placeholder candidate present
- punctuation placeholder candidate present

These should remain descriptive until a clear scoring rationale exists.

See [Linguistic placeholder constraint plan](linguistic_placeholder_constraint_plan.md)
for the no-oracle design boundary before implementing these constraints.

Status: the initial article, number, SVA, tense, preposition, and punctuation
placeholder constraints have been implemented as descriptive records with
`violation_count=0`. They do not affect `weighted_score` or rank.

### Step D: Document Initial Hand Weights

If non-safety weights are introduced:

- document each weight
- explain why it is hand-designed
- state that it is not learned
- include tests showing deterministic behavior
- avoid performance claims

### Step E: Synthetic-Only Smoke Evaluation

Run synthetic expected-action checks only to verify wiring.

Do not report F1, accuracy, or calibration.

### Step F: Private Validation Design Later

Only after synthetic policies are stable, design a private validation protocol.

Requirements:

- institution-approved environment
- no public real data
- learner-disjoint validation
- no leakage from future edits or final corrections
- clear separation between tuning, validation, and reporting

## 9. Still Not Allowed

Do not implement or claim:

- real-data tuning
- gold-label-based weight optimization
- final-text-based ranking
- `observed_after_text` ranking
- teacher-correction-based scoring
- F1
- accuracy
- calibration
- selective prediction
- learner-state estimation
- production performance

## 10. Documentation Checklist for Future Scoring Changes

Any future scoring change should document:

- formula
- variables
- constraint taxonomy
- no-oracle boundary
- whether a constraint is blocking, penalty, or descriptive
- why each weight exists
- whether weights are hand-designed or learned
- tests added
- known leakage risks
- what metrics are still not claimed

## 11. Related Docs

Read:

- `docs/09_ot_scoring_spec.md`
- `docs/08_candidate_generation_spec.md`
- `docs/03_no_oracle_policy.md`
- `docs/evaluation_spec.md`
- `docs/milestone_02_synthetic_evaluation_recap.md`
