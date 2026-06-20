# Metadata Completeness Tiny Weight Selection Design

This document designs how a future tiny metadata completeness weight could be
selected.

It is design documentation only. It does not choose a final weight value, create
an actual config fixture, change scorer weights, change the scoring formula,
change deterministic tie-break behavior, or claim performance.

Expected actions must not be used as scoring feedback.

## 1. Purpose

The purpose of this document is to define how to think about a future tiny
metadata completeness weight before any implementation.

This document preserves these boundaries:

- actual weight is not chosen here
- actual fixture is not created here
- no-config default remains unchanged
- scoring formula remains unchanged
- tie-break policy remains unchanged
- this is not performance evaluation
- this is not expected-action tuning

Any future value selection must happen in a separate reviewed implementation
step.

## 2. Meaning Of A Tiny Weight

A tiny metadata completeness weight would be a very small auxiliary signal.

It would mean:

- candidate representation is slightly more auditable
- candidate provenance is slightly easier to trace
- candidate metadata is more complete

It would not mean:

- the candidate is grammatically correct
- the candidate is pedagogically best
- the candidate matches an expected action
- the candidate improves model performance
- the candidate should bypass safety policy

It is separate from safety and blocking constraints. Safety blockers remain
dominant and non-negotiable.

A tiny metadata completeness weight also does not make all diagnostic
constraints score-active. It only concerns a narrow metadata completeness
experiment, if later approved.

## 3. Thinking About Candidate Ranges

Exact values are not selected in this document.

A future design may consider a tiny positive candidate range such as:

```text
0.001 to 0.05
```

This range is illustrative only. It is not an approved config value.

The intended properties of any future value are:

- much smaller than blocking or safety weights
- too small to dominate ranking globally
- not a replacement for deterministic tie-break behavior
- not chosen to improve F1, accuracy, calibration, or exact match
- not chosen to match expected actions
- not chosen from real participant data

If the candidate value changes broad ranking behavior, it is probably too
large.

## 4. Constraint-Specific Direction Design

### `CANDIDATE-METADATA-COMPLETE`

Possible direction:

- tiny positive preference

Possible tiny range:

- illustrative range only: `0.001` to `0.05`

Why small:

- completeness supports auditability, not correctness

Why not blocking:

- incomplete metadata is not automatically unsafe

No-oracle-safe reason:

- uses candidate metadata available before evaluation

Risk if too large:

- complete representation could be mistaken for high-quality revision behavior

### `HAS-GENERATION-RULE`

Possible direction:

- tiny positive preference

Possible tiny range:

- illustrative range only: `0.001` to `0.05`

Why small:

- provenance helps explain candidates but does not determine quality

Why not blocking:

- missing a generation rule may indicate a candidate-generation issue, not a
  privacy or leakage issue

No-oracle-safe reason:

- uses candidate metadata, not final text or expected actions

Risk if too large:

- ranking may reward implementation bookkeeping over candidate behavior

### `HAS-ACTION-FAMILY`

Possible direction:

- tiny positive preference

Possible tiny range:

- illustrative range only: `0.001` to `0.05`

Why small:

- action-family metadata supports interpretation but is not a correctness label

Why not blocking:

- missing action-family metadata is not equivalent to unsafe output

No-oracle-safe reason:

- uses action-family metadata available at scoring time

Risk if too large:

- broad action-family metadata may become a hidden family preference

### `CANDIDATE-FAMILY-BUCKET`

Possible direction:

- tiny positive preference, if used at all

Possible tiny range:

- illustrative range only: `0.001` to `0.05`

Why small:

- family buckets are coarse and should not dominate candidate ordering

Why not blocking:

- bucket metadata is diagnostic, not a safety criterion

No-oracle-safe reason:

- uses abstract candidate-family metadata available before evaluation

Risk if too large:

- candidate family buckets may override more meaningful ranking behavior

## 5. Allowed Evidence For Selection

Future value selection may consider:

- written design rationale
- no-oracle safety review
- educational interpretability
- synthetic fixture behavior, count-only only
- config validation result
- ranking diff counts
- output safety checks
- no-config fixture lock status
- config-enabled E2E smoke status
- config-enabled summary smoke status

These sources support safety and wiring review. They do not prove performance.

## 6. Forbidden Evidence For Selection

Future value selection must not use:

- expected action match
- F1
- accuracy
- calibration
- exact-match improvement
- gold labels
- `final_text`
- `observed_after_text`
- teacher correction
- human correction
- raw learner text
- observation note impression alone
- real participant data
- private validation results, unless a later design explicitly permits and
  separates that workflow

If a proposed value is justified by metric improvement, it should be rejected at
this stage.

## 7. Review Protocol Before Choosing Actual Value

Before choosing any actual value, require:

- rationale written
- candidate range reviewed
- leakage risk reviewed
- no-oracle safety documented
- no performance tuning
- no expected-action tuning
- no-config fixture lock passes
- explicit config diff is count-only
- config-enabled summary remains separate from no-config summary
- rollback criteria written
- reviewer approval
- output safety confirmed
- docs updated

The review should focus on whether the proposed value is safe, interpretable,
and narrow.

## 8. Rejection Criteria

Reject the proposed value if:

- it dominates ranking
- it changes no-config output
- it was chosen because performance improved
- expected action match was used
- grammar correctness claim appears
- rationale is incomplete
- output safety fails
- config validation fails
- config-enabled output mixes with no-config output
- raw JSONL, config, summary, or score-row bodies appear in docs or stdout
- reviewers cannot explain the value without metric language

The safest fallback is to keep metadata completeness score-neutral.

## 9. Beginner Explanation

### What Is A Tiny Weight?

A tiny weight is a small number that nudges scoring without taking over the
ranking.

For metadata completeness, it would only say that better-described candidates
are slightly easier to audit.

### Why Keep It Small?

Metadata completeness is not a strong quality signal.

A large weight could make the system prefer well-described candidates even when
that preference is not educationally justified.

### Why Not Use Accuracy?

Accuracy is a performance metric. This stage is not performance evaluation.

Choosing a value because accuracy improves would turn a design experiment into
metric tuning.

### Why Not Fit Expected Actions?

Expected actions are evaluation references used after scoring.

Using them to choose weights would leak evaluation feedback into scoring.

### Why Protect No-Config Default?

The no-config path is the baseline. It lets future explicit-config experiments
be compared without silently changing existing behavior.

If no-config output changes, the experiment boundary is broken.

## 10. Related Documents

- [Metadata completeness config fixture design](metadata_completeness_config_fixture_design.md)
- [Metadata completeness explicit config experiment design](metadata_completeness_explicit_config_experiment_design.md)
- [Synthetic hand-weight rationale examples](synthetic_hand_weight_rationale_examples.md)
- [Hand-weight policy design](hand_weight_policy_design.md)
- [No-config scoring fixture lock plan](no_config_scoring_fixture_lock_plan.md)
- [Explicit config ranking diff plan](explicit_config_ranking_diff_plan.md)
