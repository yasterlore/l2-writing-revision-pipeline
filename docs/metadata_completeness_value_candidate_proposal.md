# Metadata Completeness Value Candidate Proposal

This document proposes a possible future metadata completeness tiny weight
candidate.

It is proposal documentation only. It does not approve an actual final value,
create an actual config fixture, add a weight config file, create an approval
record, change scorer weights, change the scoring formula, change deterministic
tie-break behavior, or claim performance.

Expected actions must not be used as scoring feedback.

## 1. Purpose

The purpose of this document is to record one possible final value candidate
for a future metadata completeness explicit config fixture.

This document preserves these boundaries:

- candidate value is only a proposal
- actual approval is not granted here
- actual config fixture is not created here
- no-config default remains unchanged
- no weight is active in the default path
- this is not performance evaluation
- this is not expected-action tuning

Any future implementation must still pass final value approval before the value
is placed into a fixture.

## 2. Proposal Status

Status:

- unapproved proposal
- design-only
- no fixture created
- no scorer logic changed
- no weight active in the default path
- no approval record created
- reviewer approval required before implementation
- repository owner approval required before implementation

This proposal may be revised, rejected, deferred, or kept as design-only.

## 3. Proposed Minimal Candidate

The minimal candidate proposal is:

```text
target_constraint: CANDIDATE-METADATA-COMPLETE
proposed_value_candidate: 0.01
direction: tiny positive
blocking: no
status: unapproved proposal
```

Rationale:

- candidate representation completeness can support traceability
- complete metadata can make later review easier to interpret
- the signal is about representation completeness, not candidate correctness
- the proposed direction is weak and auxiliary
- the candidate is not selected from performance metrics
- the candidate is not selected from expected-action matching

This proposal does not mean:

- the candidate is grammatically correct
- the candidate is pedagogically best
- the candidate should outrank safety concerns
- the candidate matches an expected action
- the value is approved

## 4. Constraints Intentionally Not Weighted In The First Proposal

The first proposal intentionally does not weight:

- `HAS-GENERATION-RULE`
- `HAS-ACTION-FAMILY`
- `CANDIDATE-FAMILY-BUCKET`

Reasons:

- multiple metadata weights may interact
- the first experiment should be minimal
- metadata signals should not dominate ranking
- fewer active constraints reduce interpretability risk
- a single target constraint is easier to review and roll back

These constraints may remain future candidates, but they should not be part of
the first proposed fixture unless a later review changes the scope.

## 5. Why `0.01` Is A Candidate, Not An Approved Value

`0.01` is a candidate because:

- it is inside the previously discussed tiny illustrative range
- it is much smaller than blocking or safety weights
- it is intended as a weak auxiliary signal
- it should be easy to roll back
- it is simple to explain in a count-only review

`0.01` is not approved because:

- no final value approval has been completed
- no approval record has been created
- no actual fixture has been created
- no reviewer decision has been recorded
- no repository owner approval has been recorded

The value must not be treated as active until a later approved fixture
implementation step.

## 6. Why Not Smaller / Why Not Larger

Why not smaller:

- a smaller value may be indistinguishable from deterministic tie-break behavior
- a smaller value may be too weak for count-only diff inspection
- a smaller value may make the explicit-config smoke less informative

Why not larger:

- a larger value may over-emphasize representation completeness
- a larger value may make metadata look like candidate quality
- a larger value may risk ranking domination
- a larger value may make rollback review more urgent

The exact value is not finalized in this proposal.

## 7. Allowed Rationale

Allowed rationale for this proposal:

- no-oracle-safe feature
- candidate metadata available at ranking time
- educational traceability
- count-only diff expectation
- conservative magnitude
- rollback readiness
- no-config default protection
- explicit `--weight-config` activation only

These rationales support safe design review. They do not establish ranking
quality.

## 8. Prohibited Rationale

Prohibited rationale:

- expected action match
- accuracy improvement
- F1 improvement
- calibration improvement
- exact-match improvement
- gold label proximity
- `final_text` proximity
- `observed_after_text` proximity
- teacher correction
- human correction
- raw learner text
- observation note impression alone
- real participant data
- private participant data
- publication claim

If any prohibited rationale appears, this proposal should be rejected or
rewritten.

## 9. Approval Requirements Before Fixture Implementation

Before any fixture implementation uses this candidate, require:

- approval record filled privately or through a separately reviewed process
- no-config fixture lock confirmed
- config validation plan confirmed
- output safety confirmed
- count-only diff review confirmed
- no performance claim confirmed
- no expected-action tuning confirmed
- reviewer decision recorded
- repository owner approval recorded
- rollback conditions recorded

Approval should happen before the fixture is created.

## 10. Rejection / Revise Triggers

Reject or revise this proposal if:

- reviewer thinks `0.01` is too large
- reviewer thinks `CANDIDATE-METADATA-COMPLETE` is too broad
- rationale is not strong enough
- metadata signal is likely to dominate ranking
- no-config default risk is unclear
- expected-action tuning appears
- performance claim appears
- output safety is unclear
- rollback conditions are incomplete

The safest fallback is to keep metadata completeness score-neutral.

## 11. Beginner Explanation

### What Is A Value Candidate?

A value candidate is a possible number that might be used later if it passes
review.

It is not active yet.

### Why Is `0.01` Not Approved?

Because this document only proposes the number. It does not create a fixture,
fill an approval record, or change scoring behavior.

### Why Start With One Constraint?

Using one constraint makes the first experiment easier to understand, test, and
roll back.

### Why Not Choose By Performance?

This proposal is about safe metadata traceability, not proving accuracy,
calibration, F1, or ranking quality.

### Why Not Create The Fixture Yet?

The value still needs approval. Creating the fixture before approval would skip
the safety boundary established by the previous design documents.

## 12. Related Documents

- [Metadata completeness final value approval design](metadata_completeness_final_value_approval_design.md)
- [Metadata completeness actual fixture implementation plan](metadata_completeness_actual_fixture_implementation_plan.md)
- [Metadata completeness tiny weight selection design](metadata_completeness_tiny_weight_selection_design.md)
- [Metadata completeness config fixture design](metadata_completeness_config_fixture_design.md)
- [Metadata completeness fixture readiness checklist](metadata_completeness_fixture_readiness_checklist.md)
- [Metadata completeness fixture approval record template](templates/metadata_completeness_fixture_approval_record_template.md)
