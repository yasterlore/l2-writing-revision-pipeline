# Score-Active Family Selection Revisit

This document revisits score-active constraint family selection after
Milestone 03.

It is a design review only. It does not change scoring weights, scoring
formula, deterministic tie-break behavior, configs, feature extraction,
constraint generation, diagnostic summaries, evaluation metrics, calibration,
or learner-state estimation.

It is not performance evaluation. It does not use expected actions as scoring
feedback.

## 1. Purpose

Milestone 03 added config-aware diagnostic infrastructure, count-only summary
tools, explicit config validation, no-config regression locks, and
config-enabled smoke checks.

Before moving further toward scoring policy, this revisit checks the boundary
between:

- descriptive diagnostics
- score-neutral metadata
- safety blocking constraints
- possible future score-active families
- information that must never become score-active

The goals are to:

- preserve the no-oracle policy
- avoid expected-action tuning
- keep educational interpretability central
- keep no-config defaults unchanged
- avoid performance claims from synthetic-only checks
- avoid changing weights before a separate rationale and implementation step

This document is a checkpoint, not a weight proposal.

## 2. Current Constraint Family Map

### Safety / Blocking Constraints

Examples:

- `NO-LEAKAGE-FLAG`
- `NO-OBSERVED-EDIT-TEXT`
- `NO-UNSAFE-CANDIDATE`

Current status:

- score-active
- blocking
- safety-first

These constraints exist to prevent unsafe or leakage-bearing candidates from
being treated as acceptable candidates.

### Structural Metadata Constraints

Examples:

- metadata completeness records
- generation-rule records
- action-family records
- candidate-family bucket records

Current status:

- descriptive
- score-neutral

These records help inspect candidate metadata and future scoring-policy
readiness. They are not direct evidence of candidate quality.

### Linguistic Placeholder Constraints

Examples:

- article placeholder candidate records
- number placeholder candidate records
- SVA placeholder candidate records
- tense placeholder candidate records
- preposition placeholder candidate records
- punctuation placeholder candidate records

Current status:

- descriptive
- score-neutral

These constraints record candidate taxonomy. They do not judge grammatical
correctness.

### Local Pattern Diagnostic Constraints

Examples:

- `CONTEXT-BEFORE-*`
- `CURSOR-AT-*`
- `SELECTION-*`
- `LEFT-CONTEXT-ENDS-*`
- `LEFT-CHAR-CLASS-*`

Current status:

- descriptive
- score-neutral

These constraints summarize abstract no-oracle-safe local pattern features.
They do not expose raw local context text.

### Non-Leaky Linguistic Diagnostic Constraints

Examples:

- `ARTICLE-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `NUMBER-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `SVA-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `TENSE-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `PREPOSITION-CANDIDATE-LOCAL-CONTEXT-AVAILABLE`
- `PUNCTUATION-CANDIDATE-LEFT-PUNCTUATION-AWARE`
- `PUNCTUATION-CANDIDATE-LEFT-SPACE-AWARE`
- `GRAMMAR-CANDIDATE-LEFT-CHAR-CLASS-RECORDED`
- `GRAMMAR-CANDIDATE-SELECTION-CONTEXT-RECORDED`

Current status:

- descriptive
- score-neutral

These constraints record abstract local context availability or awareness for
grammar-placeholder candidates. They do not identify parts of speech, parse
sentences, compare against corrected text, or decide grammatical correctness.

### Candidate Family / Action Family Metadata Constraints

Examples:

- action type records
- generation rule records
- action family records
- candidate family bucket records

Current status:

- descriptive
- score-neutral

These records support interpretability and diagnostics. They should not become
generic family-level preferences without a separate rationale.

## 3. Current Recommended State

Recommended current state:

- safety / blocking constraints: keep active and blocking
- most diagnostic constraints: keep score-neutral
- metadata completeness: possible future candidate, cautiously
- local pattern diagnostics: descriptive only for now
- linguistic placeholder constraints: descriptive only for now
- non-leaky linguistic diagnostics: descriptive only for now
- candidate family / action family metadata: score-neutral for now

The current no-config default path should remain unchanged. Any future
experiment should be explicit config only.

## 4. Conditions For Score-Active Candidates

A family should only be considered for future score-active use if all of the
following are true:

- it is no-oracle safe
- it is available at candidate-generation or prediction time
- it does not depend on raw learner text in scoring output
- it does not depend on `observed_after_text`
- it does not depend on `final_text`
- it does not depend on `gold_label`
- it does not depend on expected actions
- it does not depend on teacher or human correction
- it is educationally interpretable
- a clear hand-weight rationale can be written
- the expected ranking effect can be described before implementation
- synthetic tests can isolate the config path from the no-config default path
- no-config fixture locks remain passing
- explicit `--weight-config` can be used for any experiment
- the design is not expected-action tuning
- the design is not optimization to F1, accuracy, calibration, or exact match

Passing these conditions does not make a family score-active automatically. It
only means the family is eligible for a later explicit design step.

## 5. Conditions That Should Prevent Score-Active Use

A family should not be made score-active if it:

- depends on expected actions
- depends on `observed_after_text`
- depends on `final_text`
- depends on `gold_label`
- depends on teacher or human correction
- requires storing or outputting raw learner text
- selects weights to match a performance metric
- uses diagnostic observation notes as direct tuning targets
- has unclear educational interpretation
- carries leakage risk
- would make hidden config behavior tempting
- would change the no-config default path
- would require real participant data in the public repository

Synthetic diagnostic counts and observation notes can guide human review of
wiring and documentation gaps. They must not be converted directly into
weights.

## 6. Family Decision Table

| Family | Current Status | Possible Future Status | No-Oracle Risk | Interpretability | Recommended Next Action |
| --- | --- | --- | --- | --- | --- |
| Safety / blocking | Active / blocking | Keep active / blocking | Low when based on existing safety flags | High | Keep current behavior; do not weaken without privacy review |
| Structural metadata | Neutral descriptive | Possible cautious score-active candidate | Medium if metadata becomes a proxy for quality | Medium | Consider only with strong rationale and explicit config tests |
| Metadata completeness | Neutral descriptive | Possible small explicit-config experiment | Medium; missing metadata may indicate upstream bugs | Medium | Prefer diagnostics first; revisit with synthetic-only rationale |
| Local pattern diagnostics | Neutral descriptive | Maybe later, but not now | Medium; local patterns are not correctness labels | Medium | Keep neutral; continue count-only observation |
| Linguistic placeholder | Neutral descriptive | Keep neutral for now | Medium; placeholders are taxonomy, not correctness | Medium | Keep neutral; avoid grammar-correctness claims |
| Non-leaky linguistic diagnostics | Neutral descriptive | Maybe later after stronger rationale | Medium; still not grammatical correctness | Medium to high if carefully explained | Keep neutral now; revisit with hand-weight rationale examples |
| Candidate family bucket | Neutral descriptive | Keep neutral for now | Medium; family preference can dominate ranking | Medium | Keep neutral; preserve deterministic tie-break tests |
| Action family metadata | Neutral descriptive | Keep neutral for now | Medium; action family is not quality | Medium | Keep neutral unless a narrow educational rationale exists |
| Diagnostic summary counts | Summary-only neutral | Should not be score-active | High if converted directly into weights | Low as scoring signal | Never use counts as direct weights |
| Observation note labels | Private/local review artifact | Should not be score-active | High | Low as scoring signal | Never use as direct tuning targets |
| Expected actions | Evaluation-only | Never score-active | High | Not valid for prediction-time scoring | Keep evaluation-only |

## 7. Recommended Roadmap

Recommended next steps:

1. Step 91: [synthetic-only hand-weight rationale examples](synthetic_hand_weight_rationale_examples.md)
2. Step 92: [candidate metadata completeness as an optional explicit config
   experiment](metadata_completeness_explicit_config_experiment_design.md)
3. Step 93: [metadata completeness explicit config fixture design](metadata_completeness_config_fixture_design.md)
4. Later step: private validation design, with no real data in the public
   repository

Each step should keep performance claims out of scope unless a separate
validation design explicitly supports them.

## 8. Boundaries To Preserve

Preserve these boundaries:

- no-config default unchanged
- explicit `--weight-config` only
- config validation fail closed
- no hidden config
- no implicit config discovery
- no environment-variable config loading
- no observation-note-based tuning
- no expected-action tuning
- no F1 or accuracy optimization at this stage
- no calibration optimization at this stage
- no learner-state estimation at this stage
- no real participant data in the public repository
- no raw JSONL, summary, diagnostic summary, config, or score-row bodies in docs

## 9. Beginner Explanation

### What Is A Score-Active Constraint?

A score-active constraint is a constraint whose violation count affects a
candidate's weighted score.

In this repository, safety blockers are score-active because unsafe candidates
must not rank as acceptable.

### What Is A Score-Neutral Diagnostic?

A score-neutral diagnostic records useful information without changing a
candidate's score.

For example, a local pattern diagnostic may record that a cursor was at the
document start or that the left character class was available. That is useful
for inspection, but it is not a correctness label.

### Why Not Add Weights Immediately?

Weights change ranking behavior. If a diagnostic is weighted too early, the
system may look more decisive than the evidence supports.

Before adding a weight, the team needs:

- a no-oracle review
- an educational rationale
- explicit config tests
- no-config fixture locks
- safe diff summaries

### Why Not Tune Against Expected Actions?

Expected actions are evaluation-time synthetic references. They are allowed
after scoring for synthetic wiring checks, but they must not teach the scorer
which weights to use.

Using expected actions to tune weights would leak evaluation feedback into
scoring policy.

### Why Are Safety Blockers Different?

Safety blockers protect privacy and no-oracle boundaries. They are not
ordinary linguistic preferences.

An unsafe candidate should remain blocked even if it otherwise looks attractive
by metadata or diagnostics.

## 10. Related Documents

- [Score-target constraint family selection plan](score_target_constraint_family_selection_plan.md)
- [Hand-weight policy design](hand_weight_policy_design.md)
- [Synthetic hand-weight rationale examples](synthetic_hand_weight_rationale_examples.md)
- [Metadata completeness explicit config experiment design](metadata_completeness_explicit_config_experiment_design.md)
- [Metadata completeness config fixture design](metadata_completeness_config_fixture_design.md)
- [Hand-weight config schema plan](hand_weight_config_schema_plan.md)
- [Diagnostic-to-scoring boundary review](diagnostic_to_scoring_boundary_review.md)
- [Milestone 03 config-aware diagnostic infrastructure recap](milestone_03_config_aware_diagnostic_infrastructure_recap.md)
