# Metadata Completeness Fixture Preflight Check

This document defines the final preflight check before a future metadata
completeness config fixture implementation step.

It is preflight check documentation only. It does not create an actual config
fixture, create an approval record, approve an actual value, add a weight config
file, change scorer weights, change the scoring formula, change deterministic
tie-break behavior, or claim performance.

Expected actions must not be used as scoring feedback.

## 1. Purpose

The purpose of this document is to provide a final check immediately before a
future actual metadata completeness config fixture implementation.

This preflight preserves these boundaries:

- actual fixture is not created here
- actual approval record is not created here
- actual value approval is not granted here
- no scorer logic is changed
- no-config default remains unchanged
- this is not performance evaluation
- this is not expected-action tuning

If this preflight fails, stop before fixture implementation.

## 2. Role Of The Preflight

The preflight sits after the design documents and approval workflow, and before
the implementation step.

It is the last public-safe checklist for deciding whether the implementation
step may begin.

The preflight may confirm that a private/local approval record exists and has an
acceptable status, but it must not copy the approval body into public docs.
For public-safe status handling, use
[public-safe approval existence marker design](public_safe_approval_existence_marker_design.md).

The highest priority is protecting the no-config default path.

## 3. Required Documents Checklist

Before implementation, confirm these documents exist and are linked:

- [ ] [Metadata completeness explicit config experiment design](metadata_completeness_explicit_config_experiment_design.md)
- [ ] [Metadata completeness config fixture design](metadata_completeness_config_fixture_design.md)
- [ ] [Metadata completeness tiny weight selection design](metadata_completeness_tiny_weight_selection_design.md)
- [ ] [Metadata completeness fixture readiness checklist](metadata_completeness_fixture_readiness_checklist.md)
- [ ] [Metadata completeness fixture approval record template](templates/metadata_completeness_fixture_approval_record_template.md)
- [ ] [Metadata completeness actual fixture implementation plan](metadata_completeness_actual_fixture_implementation_plan.md)
- [ ] [Metadata completeness final value approval design](metadata_completeness_final_value_approval_design.md)
- [ ] [Metadata completeness value candidate proposal](metadata_completeness_value_candidate_proposal.md)
- [ ] [Metadata completeness value candidate approval checklist](metadata_completeness_value_candidate_approval_checklist.md)
- [ ] [Metadata completeness private approval record workflow](metadata_completeness_private_approval_record_workflow.md)

If any required document is missing or inconsistent, stop before implementation.

## 4. Approval Status Checklist

Before implementation, confirm:

- [ ] private/local approval record exists, if implementation is to proceed
- [ ] reviewer decision exists
- [ ] repository owner approval exists
- [ ] proposed value candidate is confirmed
- [ ] target constraint is confirmed
- [ ] rollback criteria are confirmed
- [ ] approval body has not been copied into public docs
- [ ] approval status is safe to mention publicly, if mentioned at all

If approval is missing, stop before fixture implementation.

## 5. Implementation Scope Checklist

The future implementation step may only add a synthetic config fixture, if
approved.

Before implementation, confirm:

- [ ] only synthetic config fixture may be added
- [ ] no scorer logic change
- [ ] no scoring formula change
- [ ] no deterministic tie-break change
- [ ] no no-config expected output change
- [ ] no no-config summary behavior change
- [ ] no real data
- [ ] no private data
- [ ] no manual output data
- [ ] no participant data
- [ ] no filled approval record in public repo
- [ ] no raw output copied into docs

If the fixture requires scorer logic changes, it is no longer this experiment.

## 6. Output Safety Preflight

Before implementation, confirm:

- [ ] no config body in docs
- [ ] no JSONL body in docs
- [ ] no summary body in docs
- [ ] no diagnostic summary body in docs
- [ ] no candidate score rows in docs
- [ ] no expected action details in docs
- [ ] no raw learner text in docs
- [ ] no private/manual/real paths in docs
- [ ] `tmp/` outputs remain ignored
- [ ] `private_notes/` remains ignored
- [ ] `local_notes/` remains ignored

Public docs should describe process and rationale, not generated or private
bodies.

## 7. Test Preflight Order

In the future actual fixture implementation step, run checks in this order:

1. Config validation first.
2. No-config fixture lock.
3. Explicit config ranking diff.
4. Config-enabled E2E smoke.
5. Config-enabled summary smoke.
6. Synthetic diagnostic distribution check.
7. Python checks.
8. Rust checks.
9. TypeScript checks.
10. Synthetic policy check.
11. `git diff --check`.
12. Markdown link check.

If config validation fails, stop before running ranking or E2E checks.

If no-config fixture lock changes, stop and roll back before continuing.

## 8. Stop Conditions Before Implementation

Stop before implementation if:

- approval is missing
- repository owner approval is missing
- value candidate is unclear
- target constraint is unclear
- no-config default risk is unclear
- output safety risk is unclear
- rollback criteria are missing
- performance claim appears
- expected-action tuning appears
- real data appears
- private data appears
- manual output data appears
- approval body has been copied into public docs
- config body has been copied into public docs

The safest fallback is to keep the proposal design-only.

## 9. Go / No-Go Template

Use this blank template in a future private/local preflight note or reviewed
public-safe status.

Do not fill this template in this document.

```text
preflight_date:
reviewer:
branch:
commit:
approval_status: present / missing / not reviewed
value_candidate:
target_constraint:
no_go_blockers:
decision: go to fixture implementation / revise / stop / defer
```

Do not include the approval body, config body, JSONL body, summary body, score
rows, private paths, or performance claims.

## 10. Beginner Explanation

### What Is A Preflight Check?

A preflight check is the final checklist before starting an implementation
step.

It helps confirm that the project is ready to make the next change.

### Why Is It Needed Right Before Fixture Creation?

The fixture can affect explicit-config scoring behavior. The preflight catches
missing approval, unclear scope, output-safety risk, and no-config default risk
before a file is added.

### Why Not Paste The Approval Body Into Public Docs?

Approval bodies are private/local by default. Public docs only need to describe
the process and safe high-level status.

### Why Is No-Config Default Protection Most Important?

The no-config path is the protected baseline. If it changes, the explicit config
experiment has leaked into default behavior.

### Why Not Judge By Performance?

This stage is about safe explicit-config infrastructure and no-oracle metadata
traceability. Accuracy, F1, calibration, expected-action matching, and
real-data claims are not allowed as reasons to proceed.

## 11. Related Documents

- [Metadata completeness private approval record workflow](metadata_completeness_private_approval_record_workflow.md)
- [Public-safe approval existence marker design](public_safe_approval_existence_marker_design.md)
- [Metadata completeness value candidate approval checklist](metadata_completeness_value_candidate_approval_checklist.md)
- [Metadata completeness actual fixture implementation plan](metadata_completeness_actual_fixture_implementation_plan.md)
- [Metadata completeness fixture readiness checklist](metadata_completeness_fixture_readiness_checklist.md)
- [Metadata completeness value candidate proposal](metadata_completeness_value_candidate_proposal.md)
- [Metadata completeness final value approval design](metadata_completeness_final_value_approval_design.md)
- [No-config scoring fixture lock plan](no_config_scoring_fixture_lock_plan.md)
