# Metadata Completeness Value Candidate Approval Checklist

This checklist is for reviewing the unapproved `0.01` metadata completeness
value candidate before any future approval.

It is checklist documentation only. It is not an actual approval, not an
approval record, not an actual config fixture, not a weight config file, not a
scorer change, and not performance evaluation.

Expected actions must not be used as scoring feedback.

## 1. Purpose

The purpose of this checklist is to make sure the `0.01` proposal is reviewed
before any future approval step.

This checklist preserves these boundaries:

- actual approval is not granted here
- actual fixture is not created here
- no-config default remains unchanged
- no weight is active in the default path
- this is not performance evaluation
- this is not expected-action tuning

If the checklist reveals uncertainty, keep the proposal design-only or revise
it before approval.

## 2. Proposal Being Reviewed

The proposal under review is:

```text
target_constraint: CANDIDATE-METADATA-COMPLETE
value_candidate: 0.01
direction: tiny positive
blocking: no
status: unapproved
scope: first metadata completeness proposal only
```

This checklist does not approve the value.

## 3. Checklist Sections

Use the following sections before any future value approval:

- proposal identity
- rationale quality
- no-oracle safety
- tiny weight safety
- non-target constraint exclusion
- output safety
- test readiness
- approval readiness
- rejection readiness

All sections should be reviewed before creating a fixture.

## 4. Proposal Identity Checklist

- [ ] target constraint is `CANDIDATE-METADATA-COMPLETE`
- [ ] value candidate is `0.01`
- [ ] direction is tiny positive
- [ ] blocking is `no`
- [ ] status remains unapproved
- [ ] scope is first metadata completeness proposal only
- [ ] no actual fixture has been created
- [ ] no scorer logic has been changed
- [ ] no default-path weight has been activated

## 5. Rationale Quality Checklist

- [ ] representation completeness rationale is clear
- [ ] traceability rationale is clear
- [ ] no grammar correctness claim
- [ ] no performance optimization claim
- [ ] no expected-action tuning claim
- [ ] why only one constraint first is clear
- [ ] why `0.01` is candidate-only is clear
- [ ] rollback rationale is clear

If the rationale cannot be explained without performance claims, revise the
proposal.

## 6. No-Oracle Safety Checklist

- [ ] no expected action used
- [ ] no gold label used
- [ ] no `final_text` used
- [ ] no `observed_after_text` used
- [ ] no teacher correction used
- [ ] no raw learner text used
- [ ] no private data used
- [ ] no real participant data used
- [ ] candidate metadata is available at ranking time
- [ ] no post-edit or gold information is needed

If any no-oracle item fails, stop before approval.

## 7. Tiny Weight Safety Checklist

- [ ] `0.01` is within the tiny illustrative range
- [ ] `0.01` is much smaller than blocking or safety weights
- [ ] no blocking behavior is introduced
- [ ] the value is not intended to dominate ranking
- [ ] rollback is possible
- [ ] no tie-break replacement claim is made
- [ ] no exact performance claim is made
- [ ] no grammar correctness claim is made

If `0.01` appears likely to dominate ranking, reject or revise the proposal.

## 8. Non-Target Constraint Exclusion Checklist

- [ ] `HAS-GENERATION-RULE` excluded
- [ ] `HAS-ACTION-FAMILY` excluded
- [ ] `CANDIDATE-FAMILY-BUCKET` excluded
- [ ] local pattern diagnostics excluded
- [ ] linguistic placeholder diagnostics excluded
- [ ] non-leaky linguistic diagnostics excluded
- [ ] diagnostic summary counts excluded
- [ ] expected actions excluded
- [ ] evaluation metrics excluded
- [ ] observation note labels excluded

The first proposal should remain narrow unless a later review changes scope.

## 9. Output Safety Checklist

- [ ] no config JSON body in docs
- [ ] no JSONL body in docs
- [ ] no summary CSV body in docs
- [ ] no diagnostic summary body in docs
- [ ] no candidate score rows in docs
- [ ] no raw text in docs
- [ ] no private paths in docs
- [ ] no manual output paths used as evidence
- [ ] filled approval records remain private/local by default
- [ ] public sharing would require separate review

The public repository should contain only safe process documentation at this
stage.

## 10. Test Readiness Checklist

- [ ] hand weight config validation plan ready
- [ ] no-config fixture lock plan ready
- [ ] explicit config ranking diff plan ready
- [ ] config-enabled E2E smoke plan ready
- [ ] config-enabled summary smoke plan ready
- [ ] synthetic diagnostic distribution check plan ready
- [ ] full Python checks plan ready
- [ ] full Rust checks plan ready
- [ ] full TypeScript checks plan ready
- [ ] synthetic policy check plan ready
- [ ] `git diff --check` planned
- [ ] Markdown link check planned

These are readiness checks. They do not convert the proposal into a performance
claim.

## 11. Approval Readiness Checklist

- [ ] approval record template is ready
- [ ] reviewer is identified
- [ ] repository owner approval is required
- [ ] rollback criteria reviewed
- [ ] public-sharing policy understood
- [ ] actual filled record will not be committed without separate review
- [ ] final value approval design has been read
- [ ] value candidate proposal has been read
- [ ] actual fixture implementation plan has been read

Do not create an actual approval record in this checklist.

For where a future filled approval record should be stored, use
[Metadata completeness private approval record workflow](metadata_completeness_private_approval_record_workflow.md).

## 12. Rejection / Revise Checklist

Reject or revise if:

- [ ] `0.01` seems too large
- [ ] `CANDIDATE-METADATA-COMPLETE` seems too broad
- [ ] grammar correctness claim appears
- [ ] expected-action matching appears
- [ ] performance metric appears
- [ ] output safety is unclear
- [ ] no-config default risk is unclear
- [ ] rationale is too weak
- [ ] rollback conditions are incomplete
- [ ] reviewer or owner approval path is unclear

The safest fallback is to keep the proposal design-only.

## 13. Decision Categories

After review, use one of these decision categories:

- ready for private approval record
- revise proposal
- keep design-only
- stop
- defer to later milestone

This checklist does not itself choose the decision.

## 14. Beginner Explanation

### What Is An Approval Checklist?

An approval checklist is a list of checks to complete before deciding whether a
proposal can move forward.

It is not the approval itself.

### Why Separate Proposal And Approval?

The proposal says what might be used. Approval decides whether it is safe and
well-justified enough to use later.

Keeping them separate prevents a candidate value from quietly becoming active.

### Why Treat `0.01` Carefully?

Even a small explicit-config weight can affect candidate ranking. It must be
reviewed before it enters a fixture.

### Why Protect The No-Config Default?

The no-config path is the baseline. If it changes, the explicit config
experiment has leaked into default behavior.

### Why Not Judge By Performance?

This stage is about safe metadata traceability and explicit-config wiring.
Accuracy, F1, calibration, and expected-action matching are not allowed as
approval reasons.

## 15. Related Documents

- [Metadata completeness value candidate proposal](metadata_completeness_value_candidate_proposal.md)
- [Metadata completeness final value approval design](metadata_completeness_final_value_approval_design.md)
- [Metadata completeness fixture approval record template](templates/metadata_completeness_fixture_approval_record_template.md)
- [Metadata completeness private approval record workflow](metadata_completeness_private_approval_record_workflow.md)
- [Metadata completeness actual fixture implementation plan](metadata_completeness_actual_fixture_implementation_plan.md)
- [Metadata completeness tiny weight selection design](metadata_completeness_tiny_weight_selection_design.md)
- [Metadata completeness config fixture design](metadata_completeness_config_fixture_design.md)
