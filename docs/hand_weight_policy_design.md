# Hand-Weight Policy Design

This document defines design principles for possible future hand-designed
weights in the OT-style scorer.

It is a design document only. It does not change scoring weights, scoring
formula, deterministic tie-break behavior, feature extraction, constraint
generation, diagnostic summary tooling, evaluation, calibration, or
learner-state estimation.

Hand-designed weights, if added later, must be interpretable safety and
diagnostic policy choices. They must not be learned weights, performance
claims, or tuning results from synthetic expected actions.

## 1. Purpose

The purpose of a hand-weight policy is to define how future initial weights
could be chosen before any implementation.

The policy should:

- keep safety and no-oracle rules ahead of linguistic preference
- make every nonzero weight explainable
- keep the number of score-active families small
- prevent hidden tuning against expected actions or evaluation results
- document expected ranking behavior before code changes

This is not production evaluation. It does not claim F1, accuracy,
calibration, grammatical correctness, or learner-state quality.

## 2. Current Scorer State

The current scorer uses:

```text
weighted_score(c) = sum_i w_i * v_i(c)
```

Variables:

- `c`: candidate being scored
- `i`: constraint index
- `w_i`: current fixed prototype weight for constraint `i`
- `v_i(c)`: violation count for candidate `c`

Current safety blocking constraints use a very large prototype weight:

```text
1_000_000.0
```

Current safety blockers:

- `NO-LEAKAGE-FLAG`
- `NO-OBSERVED-EDIT-TEXT`
- `NO-UNSAFE-CANDIDATE`

Most descriptive constraints are score-neutral:

```text
weight = 0.0
violation_count = 0
```

The current tie-break is deterministic and prototype-only:

1. hold
2. local edit
3. grammar placeholder
4. other placeholder
5. other

This document does not change any of that behavior.

## 3. Possible Score-Active Constraint Families

The following families may be considered in a later score-target selection
step. They are not score-active now unless already noted.

### Safety Blocking Constraints

Current status: score-active as safety blockers.

Meaning if score-active:

- leakage or unsafe candidate state should dominate ordinary ranking
- blocked candidates should be placed after unblocked candidates
- safety violations should not be traded off against linguistic preferences

Policy:

- keep safety weights much larger than any future linguistic preference
- do not weaken safety blocking without a separate privacy and no-oracle review

### Metadata Completeness Constraints

Current status: descriptive and score-neutral.

Meaning if score-active:

- candidates with incomplete required metadata could be mildly penalized
- missing rule or family metadata could reduce interpretability

Risks:

- metadata completeness is not linguistic quality
- overly penalizing missing metadata can hide candidate-generation bugs

Policy:

- prefer diagnostics first
- if score-active later, use small penalties and explicit tests

### Local Pattern Diagnostic Constraints

Current status: descriptive and score-neutral.

Meaning if score-active:

- abstract pre-edit context patterns could influence candidate preference
- examples include cursor position, selection state, context length bucket, or
  left-character class

Risks:

- local patterns are diagnostic abstractions, not correctness labels
- direct use can overfit to synthetic fixture shapes

Policy:

- keep as diagnostics until a separate score-target family selection plan
- never reintroduce raw `local_context_before` text into scoring output

### Non-Leaky Linguistic Diagnostic Constraints

Current status: descriptive and score-neutral.

Meaning if score-active:

- grammar-placeholder candidates could receive small preferences or penalties
  based on no-oracle-safe abstract context availability
- this would still not judge full grammatical correctness

Risks:

- these constraints are not POS tags, parse results, or teacher corrections
- using them too early may create unsupported linguistic claims

Policy:

- keep score-neutral until diagnostic behavior is stable
- document every future weight as a hand-designed preference, not learned truth

### Placeholder Family Constraints

Current status: descriptive and score-neutral.

Meaning if score-active:

- some candidate families could be preferred or discouraged by default
- for example, a future policy might distinguish hold, local edit, and grammar
  placeholder candidates beyond tie-break order

Risks:

- family-level preferences may dominate candidate diversity
- placeholder candidates are not fully realized corrections

Policy:

- avoid broad family penalties unless the rationale is clear
- preserve deterministic tests for ranking behavior

## 4. Families That Should Remain Score-Neutral

The following should not become score-active:

- raw diagnostic distribution counts
- observation note labels
- synthetic expected action
- evaluation result
- exact match result
- real participant metadata
- anything requiring post-edit information
- anything requiring final text
- anything requiring gold labels
- anything requiring teacher or human correction

Diagnostic summary counts may guide human inspection of wiring. They should not
be converted directly into weights.

## 5. Weight Design Principles

Future hand-designed weights should follow these principles.

### Safety First

Safety and leakage constraints should dominate ordinary candidate preference.

No linguistic preference should make an unsafe candidate look acceptable.

### No-Oracle First

Only prediction-time and no-oracle-safe information may influence scoring.

Expected actions, exact-match results, post-edit text, final text, and teacher
corrections must not be used to choose weights.

### Interpretability

Every nonzero weight needs a written rationale:

- what the weight means
- why the constraint family is score-active
- why the magnitude is appropriate
- what ranking behavior should change

### Monotonicity Where Possible

When a constraint is a penalty, more violations should not improve score.

Avoid rules where a violation sometimes helps and sometimes hurts unless the
behavior is explicitly documented.

### Small Number of Active Weights

Start with very few score-active non-safety weights.

A small policy is easier to inspect, test, and reverse.

### Avoid Overfitting to Synthetic Fixtures

Synthetic fixtures are wiring checks. They are not training data.

Do not tune weights to make synthetic expected actions rank first.

### No Hidden Learned Weights

All weights must be visible in source or config and documented.

Do not introduce implicit learned coefficients or data-derived constants under
the label of hand weights.

### Tests for Intentional Ranking Changes

Any weight change must include tests that show:

- scoring order changes are intentional
- blocking behavior remains intentional
- tie-break behavior changes only if explicitly approved

## 6. Prohibited Weight-Design Inputs and Actions

Do not:

- tune weights to F1
- tune weights to accuracy
- tune weights to calibration
- tune weights to synthetic expected actions
- tune weights to exact-match results
- use `final_text`
- use `observed_after_text`
- use `gold_label`
- use teacher correction
- use human correction
- pre-tune on real participant data
- convert diagnostic summary counts directly into weights
- add hidden learned weights
- change tie-break behavior without documentation and tests

## 7. Checklist Before Candidate Ranking Is Affected

Before any new weight can affect ranking:

- [ ] No-oracle audit passes.
- [ ] Raw text is absent from feature, constraint, score, and summary outputs.
- [ ] Forbidden fields are absent.
- [ ] Score-active family selection is documented.
- [ ] Hand-weight rationale is documented.
- [ ] Synthetic E2E smoke passes.
- [ ] Ranking behavior diff tests are added.
- [ ] Blocking behavior tests still pass.
- [ ] Performance claims remain prohibited.
- [ ] Expected actions are not used as scoring feedback.
- [ ] Private validation design remains a separate later step.

## 8. Initial Weight Design Direction

This section is directional only. It does not implement weights.

Initial direction:

- keep blocking constraints very large
- keep descriptive diagnostics at `0.0` first
- if a diagnostic family becomes score-active later, start with small weights
- keep safety constraints separate from linguistic preferences
- avoid mixing safety and linguistic signals into one opaque score
- treat diagnostic constraints as observation tools before scoring tools
- document each score-active family before implementation

Non-safety weights should be introduced only after the relevant constraint
family has been reviewed as no-oracle-safe and score-appropriate.

## 9. Relationship to Evaluation

Synthetic expected actions and exact-match reports are evaluation-stage wiring
checks.

They must not be used to:

- choose weights
- adjust weights
- choose score-active families
- change tie-break behavior
- filter candidates before scoring

Evaluation can reveal that a pipeline is connected. It cannot, by itself,
justify a scoring policy.

## 10. Future Roadmap

### Step 63: Score-Target Constraint Family Selection Plan

Select which constraint families may become score-active and which must remain
descriptive or excluded.

See
[Score-target constraint family selection plan](score_target_constraint_family_selection_plan.md)
for the narrower family-selection proposal. It does not change weights or
ranking behavior.

### Step 64: Hand-Weight Config Schema Plan

Design how weights would be represented in config without changing current
defaults.

### Step 65: Implement Hand-Weight Config Without Changing Defaults

Add configuration plumbing only if approved, while preserving current scoring
behavior by default.

### Step 66: Synthetic Ranking Behavior Smoke Tests

Add tests that inspect deterministic ranking behavior on synthetic fixtures
without reporting performance metrics.

### Step 67: Private Validation Design Later

Design private validation separately, after synthetic-only policies and
hand-weight documentation are stable.

## 11. Non-Goals

This document does not:

- change current weights
- change the scoring formula
- change tie-break behavior
- select score-active non-safety families
- implement weight configuration
- implement evaluation metrics
- implement calibration
- implement learner-state estimation
- authorize real participant data processing
