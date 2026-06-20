# Metadata Completeness Final Value Approval Design

This document designs how a future final metadata completeness tiny weight
value should be approved.

It is approval design documentation only. It does not choose an actual value,
create an actual config fixture, add a weight config file, create an approval
record, change scorer weights, change the scoring formula, change deterministic
tie-break behavior, or claim performance.

Expected actions must not be used as scoring feedback.

## 1. Purpose

The purpose of this document is to define the approval process that should
happen before a future metadata completeness config fixture uses an actual
weight value.

This design preserves these boundaries:

- actual final value is not chosen here
- actual fixture is not created here
- actual approval record is not created here
- no-config default remains unchanged
- scorer logic remains unchanged
- this is not performance evaluation
- this is not expected-action tuning

The document describes how a value should be approved later. It is not the
approval itself.

For an unapproved example candidate that may be reviewed later, see
[Metadata completeness value candidate proposal](metadata_completeness_value_candidate_proposal.md).

## 2. Role Of Final Value Approval

Final value approval sits between:

1. [Metadata completeness tiny weight selection design](metadata_completeness_tiny_weight_selection_design.md)
2. [Metadata completeness actual fixture implementation plan](metadata_completeness_actual_fixture_implementation_plan.md)

The tiny weight selection design defines the safe range and selection rules.
The actual fixture implementation plan defines the later implementation steps.
Final value approval is the policy/rationale decision that says whether a
specific future value candidate is acceptable before it enters a fixture.

Choosing a value is not treated as a code implementation detail. It is a
reviewed policy decision because even a tiny score-active weight can affect
candidate ordering in the explicit config path.

Final value approval is not:

- performance metric optimization
- expected action matching
- grammar correctness certification
- learner-state estimation
- real-data readiness approval

The approval must require reviewer and repository owner approval before fixture
implementation begins.

## 3. Inputs Required Before Approval

Before a final value candidate can be approved, the reviewer should have:

- target constraints
- non-target constraints
- proposed tiny range
- proposed value candidate, defined outside this document
- rationale per target constraint
- no-oracle-safe reason per target constraint
- risk note if the value is too large
- rollback criteria
- test plan
- output safety plan
- confirmation that no-config default remains protected
- confirmation that explicit `--weight-config` is the only activation path

If any required input is missing, the approval should stop before a fixture is
created.

## 4. Allowed Grounds For Choosing A Value Candidate

A future value candidate may be justified by:

- design rationale
- no-oracle safety
- educational interpretability
- conservative magnitude
- count-only synthetic ranking diff expectation
- no-config default protection
- config validation readiness
- output safety
- rollback readiness
- reviewer ability to explain the value without raw outputs

These grounds support safe design review. They do not prove that ranking is
better.

## 5. Forbidden Grounds For Choosing A Value Candidate

A future value candidate must not be justified by:

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
- private participant data
- real participant data
- observation note impression alone
- performance improvement
- publication-style claim

If a value candidate depends on these grounds, it should be rejected for this
stage.

## 6. Recommended Approval Format

Use a blank approval format like this in a future private/local approval record
or separately reviewed public-safe record.

Do not fill this template in this document.

```text
proposed_value_candidate:
target_constraint_ids:
reason_this_value_is_tiny:
why_not_smaller:
why_not_larger:
why_not_blocking:
why_not_performance_tuned:
why_not_expected_action_tuned:
no_oracle_confirmation:
expected_count_only_diff:
rollback_conditions:
reviewer_decision:
repository_owner_approval:
date:
```

The filled record should not include raw JSONL bodies, config bodies, summary
bodies, score rows, expected action details, or private paths.

## 7. Approval Decision Categories

The reviewer should choose one of these decision categories:

- approve value for fixture implementation
- revise value candidate
- keep design-only
- stop experiment
- defer to later milestone

Approval should only allow the next implementation step to create a synthetic
fixture. It should not authorize default scoring changes.

## 8. Rejection Criteria

Reject the value candidate if:

- value is chosen from a performance metric
- expected action matching is used
- grammar correctness claim appears
- value is too large for an auxiliary metadata signal
- value dominates ranking
- rationale is incomplete
- no-oracle safety is unclear
- no-config default risk is unclear
- output safety is unclear
- rollback criteria are missing
- reviewer approval is missing
- repository owner approval is missing

The safest fallback is to keep metadata completeness score-neutral.

## 9. Documentation And Privacy Policy

Public docs may describe:

- approval process
- synthetic-only scope
- target constraint categories
- no-oracle rationale shape
- test plan shape
- rollback criteria shape

Public docs must not include:

- actual config JSON body
- raw output body
- raw JSONL body
- summary CSV body
- diagnostic summary JSON body
- candidate score rows
- expected action details
- raw learner text
- private/manual/real paths
- performance claims

Filled approval records are private/local by default.

If a filled approval record needs to be shared publicly, it requires the
separate public-sharing review workflow before commit.

## 10. Beginner Explanation

### What Is Final Value Approval?

Final value approval is the review step where humans decide whether a specific
tiny weight value is safe and understandable enough to put into a future
synthetic config fixture.

This document does not make that decision.

### Why Approve Before Choosing A Value?

Even tiny values can change ranking in the explicit config path. Approval makes
the reason for the value visible before it becomes a fixture.

### Why Not Choose By Performance?

This stage is about safe, interpretable infrastructure. F1, accuracy,
calibration, and exact-match improvements are not allowed as reasons for the
value.

### Why Not Match Expected Actions?

Expected actions belong to synthetic evaluation checks. Using them to choose a
weight would turn the config into expected-action tuning.

### Why Are Rollback Conditions Needed?

Rollback conditions define when to stop if the value leaks into no-config
behavior, dominates ranking, weakens output safety, or creates unclear
rationale.

## 11. Related Documents

- [Metadata completeness tiny weight selection design](metadata_completeness_tiny_weight_selection_design.md)
- [Metadata completeness actual fixture implementation plan](metadata_completeness_actual_fixture_implementation_plan.md)
- [Metadata completeness value candidate proposal](metadata_completeness_value_candidate_proposal.md)
- [Metadata completeness fixture readiness checklist](metadata_completeness_fixture_readiness_checklist.md)
- [Metadata completeness fixture approval record template](templates/metadata_completeness_fixture_approval_record_template.md)
- [Metadata completeness config fixture design](metadata_completeness_config_fixture_design.md)
- [Metadata completeness explicit config experiment design](metadata_completeness_explicit_config_experiment_design.md)
- [Synthetic hand-weight rationale examples](synthetic_hand_weight_rationale_examples.md)
