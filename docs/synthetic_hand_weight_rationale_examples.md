# Synthetic Hand-Weight Rationale Examples

This document gives synthetic-only examples of how future hand-weight
rationales should be written.

It is example documentation only. It is not an actual config, not a config
fixture, not a weight change, not performance evaluation, and not expected-action
tuning.

## 1. Purpose

Future hand-designed weights need written rationales before they affect
candidate ranking.

This document shows the shape of a good rationale using synthetic-only examples.
It does not:

- change scorer weights
- change the scoring formula
- change deterministic tie-break behavior
- create or modify weight config fixtures
- claim accuracy, F1, calibration, or ranking quality
- use expected actions as scoring feedback
- use real participant data

The examples here are design examples. They are not approved weights.

## 2. Basic Principles

A future hand-weight rationale should satisfy these principles:

- no-oracle safe
- available at candidate generation or ranking time
- independent of expected actions
- independent of gold labels
- independent of final text
- independent of observed-after text
- independent of teacher or human correction
- does not store or output raw learner text
- educationally interpretable
- keeps the default no-config path unchanged
- uses explicit config only
- relies on fail-closed config validation
- keeps the number of active weights small
- requires a written rationale for every active weight
- requires tests before implementation

The rationale must explain what the weight means. It must not say that a weight
exists because it improved a synthetic metric.

## 3. Rationale Entry Template

Use a template like this before any future implementation:

```text
constraint_id:
family:
proposed_status:
proposed_weight_direction:
proposed_weight_magnitude_range:
educational_rationale:
no_oracle_safe_reason:
leakage_risk_review:
why_not_expected_action_tuning:
why_not_performance_optimization:
expected_effect_on_ranking:
possible_failure_modes:
tests_required:
review_status:
```

Field guidance:

- `constraint_id`: concrete constraint ID or clearly named family
- `family`: safety, metadata, local pattern, linguistic diagnostic, or other
  documented family
- `proposed_status`: active, keep-neutral, or defer
- `proposed_weight_direction`: penalty, preference, blocking, or none
- `proposed_weight_magnitude_range`: qualitative range only until a later
  config design step
- `educational_rationale`: why this policy is interpretable for revision
  behavior
- `no_oracle_safe_reason`: why the information is available without future,
  final, gold, or observed-after content
- `leakage_risk_review`: what could leak and how the design avoids it
- `why_not_expected_action_tuning`: explicit statement that expected actions are
  not used to choose the weight
- `why_not_performance_optimization`: explicit statement that metrics are not
  used to choose the weight
- `expected_effect_on_ranking`: intended behavior change in plain language
- `possible_failure_modes`: ways the weight could mislead ranking or
  interpretation
- `tests_required`: regression, config validation, diff, E2E, and safe-output
  checks
- `review_status`: draft, needs review, approved for experiment, or rejected

## 4. Synthetic Examples

These examples are not config entries. They are prose examples of how rationale
records could be written later.

### Safety / Blocking Constraint Example

Example family:

- safety / blocking

Example constraint:

- `NO-LEAKAGE-FLAG`

Proposed status:

- remain score-active and blocking

Rationale:

- A leakage-bearing candidate should be blocked because the system must not rank
  unsafe candidates as acceptable. This is a privacy and no-oracle policy, not a
  linguistic preference.

No-oracle risk:

- low when the flag comes from existing no-oracle safety metadata

Interpretability:

- high, because the policy is simple: unsafe candidates are blocked

Expected-action tuning:

- prohibited; expected actions are not used to decide the blocking policy

Performance metric tuning:

- prohibited; the blocking weight is a safety policy, not a metric result

Next review needed:

- privacy review before weakening or changing blocking behavior

### Metadata Completeness Cautious Example

Example family:

- metadata completeness

Example proposed status:

- possible future explicit-config candidate

Rationale:

- If a candidate is missing required interpretability metadata, a small future
  penalty might make the ranking prefer candidates whose provenance and family
  are easier to audit.

No-oracle risk:

- medium; metadata is prediction-time information, but missing metadata may
  indicate upstream generation issues rather than candidate quality

Interpretability:

- medium; completeness is easy to explain, but it is not linguistic correctness

Expected-action tuning:

- prohibited; the penalty must not be chosen because it matches expected actions

Performance metric tuning:

- prohibited; the rationale must not be "this improved exact match"

Next review needed:

- separate rationale, explicit config experiment, default-path fixture lock, and
  ranking diff smoke

### Local Pattern Diagnostic Keep-Neutral Example

Example family:

- local pattern diagnostic

Example constraints:

- `CONTEXT-BEFORE-*`
- `CURSOR-AT-*`
- `LEFT-CHAR-CLASS-*`

Proposed status:

- keep score-neutral

Rationale:

- Local pattern diagnostics describe abstract context. They are useful for
  checking whether diagnostic records are emitted, but they are not correctness
  labels.

No-oracle risk:

- medium if converted into weights too early, because local patterns can become
  fixture-specific proxies

Interpretability:

- medium; the fields are explainable, but the link to better ranking is not yet
  established

Expected-action tuning:

- prohibited; do not weight a local pattern because it appears near an expected
  action in synthetic fixtures

Performance metric tuning:

- prohibited; diagnostic distribution is not a performance metric

Next review needed:

- keep count-only observation; revisit only after a stronger educational
  rationale exists

### Linguistic Placeholder Keep-Neutral Example

Example family:

- linguistic placeholder

Example constraints:

- article placeholder
- number placeholder
- SVA placeholder
- tense placeholder
- preposition placeholder
- punctuation placeholder

Proposed status:

- keep score-neutral

Rationale:

- Placeholder family records identify candidate taxonomy. They do not decide
  whether an article, number, SVA, tense, preposition, or punctuation correction
  is grammatically right.

No-oracle risk:

- medium if placeholder family becomes a broad proxy for correctness

Interpretability:

- medium; taxonomy is easy to explain, but it is not enough for a preference

Expected-action tuning:

- prohibited; do not prefer a placeholder family because it matches expected
  actions in synthetic cases

Performance metric tuning:

- prohibited; do not tune family weights to optimize synthetic accuracy

Next review needed:

- keep neutral until non-leaky linguistic rationale is stronger

### Non-Leaky Linguistic Diagnostic Future-Candidate Example

Example family:

- non-leaky linguistic diagnostic

Example constraints:

- `PUNCTUATION-CANDIDATE-LEFT-PUNCTUATION-AWARE`
- `GRAMMAR-CANDIDATE-LEFT-CHAR-CLASS-RECORDED`

Proposed status:

- possible future candidate, but defer

Rationale:

- Some non-leaky diagnostics may eventually support small, interpretable
  preferences for candidates whose abstract context is available and recorded.
  The rationale would still be about context awareness, not grammatical
  correctness.

No-oracle risk:

- medium; the fields are abstract and no-oracle-safe, but the interpretation can
  be overstated

Interpretability:

- medium to high if carefully framed as context availability

Expected-action tuning:

- prohibited; expected actions must not be used to select or tune these weights

Performance metric tuning:

- prohibited; do not choose the weight because a synthetic metric improved

Next review needed:

- write a separate active-family rationale, add explicit config tests, and
  require safe ranking diff summaries

### Candidate Family Bucket Keep-Neutral Example

Example family:

- candidate family bucket

Proposed status:

- keep score-neutral

Rationale:

- Candidate family buckets help explain candidate provenance. A broad preference
  for one family can dominate ranking and hide candidate-generation weaknesses.

No-oracle risk:

- medium; family labels are no-oracle-safe, but a family preference may become a
  shortcut

Interpretability:

- medium; easy to name, but too coarse to justify ranking changes alone

Expected-action tuning:

- prohibited; do not prefer a family because it happens to match expected
  actions

Performance metric tuning:

- prohibited; do not choose family weights from exact-match results

Next review needed:

- keep neutral; rely on deterministic tie-break tests unless a narrow
  educational rationale is written

## 5. Good And Bad Rationale Examples

### Good Rationale Patterns

Good rationales are:

- no-oracle safe
- educationally explainable
- conservative
- explicit-config only
- testable with synthetic fixtures
- written before implementation
- clear about possible failure modes
- clear that expected actions are not used for tuning
- clear that performance metrics are not used for tuning

Example wording:

```text
This weight is proposed as a small explicit-config penalty for missing
interpretability metadata. The policy is not grammatical correctness. It is
intended to prefer candidates whose provenance can be audited. It uses only
prediction-time metadata and does not use expected actions, final text, observed
after text, gold labels, or raw learner text.
```

### Bad Rationale Patterns

Bad rationales include:

- "accuracy went up"
- "F1 improved"
- "it matches the expected action"
- "it is closer to the gold label"
- "it is closer to the final text"
- "the observation note looked concerning, so change the weight"
- "the raw learner text pattern suggests this weight"
- "this should improve real data readiness"
- "this makes the system grammatically correct"

These are not acceptable reasons for public-repository hand weights at this
stage.

## 6. Tests Required Before Any Future Implementation

Before any future implementation of a rationale as an actual config or scorer
change, require:

- no-config fixture lock unchanged
- config validation
- explicit config ranking diff
- config-enabled E2E smoke
- config-enabled summary smoke
- safe stdout only
- no config body in stdout or docs
- no JSONL body in stdout or docs
- no summary body in docs
- no candidate score rows in docs
- no expected-action tuning
- no performance claim
- default output schema review
- forbidden-field absence checks

If a change affects ranking, the expected ranking behavior must be documented
before implementation and verified with synthetic-only diff summaries.

## 7. Beginner Explanation

### What Is A Hand-Weight?

A hand-weight is a human-designed number that says how much a constraint should
affect candidate scoring.

It is not learned from data and should not be tuned to match expected actions.

### What Is A Rationale?

A rationale is the explanation for why a weight should exist.

It should explain:

- what the weight means
- why it is no-oracle safe
- why it is educationally interpretable
- what ranking effect is expected
- what tests are needed

### Why Not Change Weights Immediately?

Weights affect ranking. Changing them without a written rationale can turn a
diagnostic observation into an unsupported scoring policy.

The safe path is:

1. write the rationale
2. review no-oracle and privacy boundaries
3. validate config behavior explicitly
4. keep no-config defaults unchanged
5. check synthetic diff summaries without performance claims

### Why Start With Synthetic Examples?

Synthetic examples can exercise wiring and documentation boundaries without
using real participant data.

They are good for checking whether a rationale is coherent. They are not proof
that the system performs well.

### Why Not Use Expected Actions To Fit Weights?

Expected actions are references used after scoring for synthetic evaluation
wiring.

If expected actions are used to choose weights, evaluation feedback leaks into
scoring policy. That would break the boundary between evaluation and ranking.

## 8. Related Documents

- [Hand-weight policy design](hand_weight_policy_design.md)
- [Hand-weight config schema plan](hand_weight_config_schema_plan.md)
- [Score-active family selection revisit](score_active_family_selection_revisit.md)
- [Diagnostic-to-scoring boundary review](diagnostic_to_scoring_boundary_review.md)
- [Default-unchanged config support design](default_unchanged_config_support_design.md)
