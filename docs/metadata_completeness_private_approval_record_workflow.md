# Metadata Completeness Private Approval Record Workflow

This document defines how a future metadata completeness approval record should
be created and stored privately or locally.

It is workflow design documentation only. It does not create an actual approval
record, approve an actual value, create an actual config fixture, add a weight
config file, change scorer weights, change the scoring formula, change
deterministic tie-break behavior, or claim performance.

Expected actions must not be used as scoring feedback.

## 1. Purpose

The purpose of this workflow is to keep any future actual approval record for
the metadata completeness value candidate private or local by default.

This workflow exists to:

- prevent filled approval records from being committed to the public repository
- keep public docs limited to blank templates, workflows, and checklists
- preserve no-oracle and privacy boundaries
- separate approval from implementation
- prevent approval records from becoming performance claims
- prevent expected-action tuning

This document does not approve the value and does not create the fixture.

## 2. Target Approval

The workflow applies to a future approval for:

```text
proposal: metadata completeness 0.01 proposal
target_constraint: CANDIDATE-METADATA-COMPLETE
value_candidate: 0.01
direction: tiny positive
blocking: no
status: unapproved until separately approved
```

The approval would be needed before a future actual metadata completeness
fixture implementation step.

This document does not grant that approval.

## 3. Recommended Storage Location

Recommended private or local locations:

```text
private_notes/
local_notes/
```

These directories should be Git ignored before use.

The public repository should contain:

- blank approval record template
- workflow documents
- checklist documents
- design documents

The public repository should not contain the filled approval record by default.

Do not create `private_notes/` or `local_notes/` as part of this workflow
document. Create them only if an actual local review needs them.

## 4. Private Approval Record Creation Procedure

For a future approval, use this procedure:

1. Copy the blank approval record template into private or local storage.
2. Record the branch, commit hash, and related proposal document.
3. Review the value candidate approval checklist.
4. Confirm no-oracle safety.
5. Confirm output safety.
6. Confirm rollback criteria.
7. Record reviewer decision.
8. Record repository owner approval, if approval is granted.
9. Keep the filled record private or local.
10. Do not paste the filled record into public docs.

Use this template as the source:

```text
docs/templates/metadata_completeness_fixture_approval_record_template.md
```

The filled private/local record should remain count-only and process-focused.

## 5. What May Remain In The Public Repository

The public repository may contain:

- blank template
- workflow docs
- checklist docs
- design docs
- high-level status only, if separately reviewed
- statement that approval is required
- statement that approval was checked, if safe and separately reviewed

Any public status should avoid raw bodies, private paths, score rows, and
performance claims.

## 6. What Must Not Remain In The Public Repository

Do not commit:

- filled approval record
- actual config JSON body copied into docs
- raw JSONL body
- summary CSV body
- diagnostic summary body
- candidate score rows
- candidate descriptions
- proposed edit payload
- expected action details
- evaluation report body
- `final_text`
- `observed_after_text`
- `gold_label`
- teacher correction
- human correction
- real participant identifiers
- private/manual/real paths
- local machine-specific private paths
- performance claims
- F1
- accuracy
- calibration
- learner-state estimates

If a public document needs one of these items to be understandable, it is not
safe for the public repository.

## 7. Public Sharing Exception

The default rule is:

- filled approval records stay private or local

Public sharing is exceptional.

If a filled approval record is proposed for public sharing:

- run a review at least as strict as the filled observation note public-sharing
  checklist
- reduce the content to high-level count-only status
- remove generated bodies and score rows
- remove config bodies
- remove private paths
- remove performance claims
- obtain repository owner approval
- commit only a reviewed public-safe derivative, not the private working record

The safest public artifact is usually a short status statement, not the filled
record.

## 8. Approval Outcome Handling

Possible private approval outcomes:

- approve: next implementation step may create the fixture
- revise: update the proposal doc or checklist before approval
- stop: end the experiment
- defer: move the decision to a later milestone

The private approval record itself remains private or local for all outcomes.

If approval is granted, the implementation step should still verify:

- no-config fixture lock
- config validation
- explicit config ranking diff
- config-enabled E2E smoke
- config-enabled summary smoke
- output safety
- no performance claim

Before the implementation step begins, run the
[metadata completeness fixture preflight check](metadata_completeness_fixture_preflight_check.md).

## 9. Bridge To Actual Fixture Implementation

The future implementation step may check that approval exists, but it should
not copy the approval body into public docs.

Public docs or commit messages may say:

- approval required
- approval checked
- approval completed, if that status is safe and separately reviewed

For designing safe high-level status labels, use
[public-safe approval existence marker design](public_safe_approval_existence_marker_design.md).

Public docs or commit messages must not include:

- filled approval body
- private/local note path
- config body copied from the fixture
- score rows
- summary body
- expected action details
- performance claims

If the actual fixture is later added, the fixture file may exist under
synthetic fixtures after approval, but docs should not duplicate the config JSON
body.

## 10. Beginner Explanation

### What Is An Approval Record?

An approval record is a written note that records whether a reviewer and
repository owner approved a value candidate for a later implementation step.

### Why Not Put It In The Public Repository?

Filled approval records may contain reviewer-specific notes, local paths, or
process details that should not become public project artifacts.

The public repository only needs the blank template, workflow, and checklist.

### Why Is Private Or Local Storage Enough?

The record is used to support a controlled implementation decision. It does not
need to be public to protect the public code path.

### Why Separate Approval And Implementation?

Approval decides whether the value is acceptable. Implementation creates the
fixture later.

Keeping them separate prevents a proposed value from quietly becoming active.

### Why Not Decide By Performance?

This workflow is about no-oracle-safe, interpretable metadata completeness
review. Accuracy, F1, calibration, expected-action matching, and real-data
claims are not allowed as approval reasons.

## 11. Related Documents

- [Metadata completeness value candidate approval checklist](metadata_completeness_value_candidate_approval_checklist.md)
- [Metadata completeness value candidate proposal](metadata_completeness_value_candidate_proposal.md)
- [Metadata completeness final value approval design](metadata_completeness_final_value_approval_design.md)
- [Metadata completeness fixture approval record template](templates/metadata_completeness_fixture_approval_record_template.md)
- [Metadata completeness fixture preflight check](metadata_completeness_fixture_preflight_check.md)
- [Public-safe approval existence marker design](public_safe_approval_existence_marker_design.md)
- [Metadata completeness actual fixture implementation plan](metadata_completeness_actual_fixture_implementation_plan.md)
- [Observation note storage and review workflow](observation_note_storage_and_review_workflow.md)
- [Filled observation note public-sharing checklist](filled_observation_note_public_sharing_checklist.md)
