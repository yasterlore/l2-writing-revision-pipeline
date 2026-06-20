# Public-Safe Approval Existence Marker Design

This document designs how a future implementation step may refer to approval
existence without publishing the approval body.

It is design documentation only. It does not create an approval record, approve
an actual value, create an approval marker file, create an actual config
fixture, add a weight config file, change scorer weights, change the scoring
formula, change deterministic tie-break behavior, or claim performance.

Expected actions must not be used as scoring feedback.

## 1. Purpose

The purpose of this document is to define how approval existence may be handled
in a public-safe way.

This design preserves these boundaries:

- approval body is not published
- actual approval record is not created here
- actual approval is not granted here
- actual fixture is not created here
- no-config default remains unchanged
- this is not performance evaluation
- this is not expected-action tuning

The design is about safe status handling, not about approving the value.

## 2. Why Approval Existence Marker Is Needed

A future implementation step may need to confirm that approval exists before
creating a metadata completeness fixture.

However:

- the approval body belongs in private or local storage
- reviewer notes should not be public by default
- detailed rationale copied from private records may expose process details
- public docs should not contain raw approval text
- public docs should only carry minimal high-level status, if any

An approval existence marker is a way to say that approval status was checked
without exposing the approval body.

## 3. Public-Safe Status Labels

Possible public-safe status labels:

- `approval_required`
- `approval_present_private_local`
- `approval_not_present`
- `approval_deferred`
- `approval_revoked`
- `approval_recheck_required`

These labels are examples. This document does not create an actual marker file
and does not assign a real status.

Status labels should not imply permanent approval.

## 4. Information Allowed In A Public Marker

A public-safe marker may include:

- status label
- approval type
- proposal document name
- target constraint id
- value candidate, if already public in proposal docs
- date, optional
- reviewer role, not necessarily reviewer name
- owner approval status label
- statement that no raw approval body is included
- statement that no performance claim is included

Keep the marker short and process-focused.

## 5. Information Forbidden In A Public Marker

A public marker must not include:

- filled approval record body
- reviewer private notes
- detailed rationale copied from a private record
- config JSON body
- JSONL body
- summary body
- diagnostic summary body
- candidate score rows
- expected action details
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

If a status marker needs one of these items to be understandable, it is too
detailed for public use.

## 6. Recommended Marker Formats

### Option A: High-Level Status Line In Docs

Example shape:

```text
approval_status: approval_present_private_local
approval_body_included: false
```

Pros:

- easy to read
- no new file type
- can stay near the implementation note

Cons:

- may invite adding too much context
- requires careful review before commit

### Option B: YAML Or JSON Marker File

Example shape:

```text
status: approval_present_private_local
approval_body_included: false
```

Pros:

- machine-readable
- explicit fields

Cons:

- may look like an implementation artifact
- may invite scripts to read approval status
- easy to expand into unsafe detail

### Option C: Commit Message Or PR Description Only

Pros:

- avoids adding a repository file
- can be brief

Cons:

- harder to discover later
- may be inconsistently phrased

### Option D: Private-Only, No Public Marker

Pros:

- safest for privacy
- no chance of leaking private rationale
- keeps public repo limited to process docs

Cons:

- future readers may not see public evidence that approval was checked

### Initial Recommendation

Use Option D by default.

If public status is needed, use Option A with a minimal high-level line only.
Do not create a YAML or JSON marker file initially.

## 7. Use In An Implementation Step

In a future implementation step:

- preflight checks approval status
- human reviewer confirms private/local approval record exists
- approval body is not read by scripts
- approval body is not copied into docs
- implementation commit may mention only safe high-level status
- if approval is missing, stop before fixture implementation

Scripts should not depend on private approval record contents. Human review is
the boundary.

If scripts or tests inspect status output, they should avoid treating
environment-dependent temporary paths as approval content. See
[forbidden-term path-safety test hardening design](forbidden_term_path_safety_test_hardening_design.md).

## 8. Revocation And Recheck Policy

Approval may need recheck or revocation if assumptions change.

Require recheck if:

- target constraints change
- value candidate changes
- config schema changes
- output safety policy changes
- no-config default behavior changes
- explicit config path changes
- private approval record becomes stale
- public docs accidentally include unsafe approval detail

Approval may be revoked if:

- expected-action tuning appears
- performance claim appears
- output safety fails
- no-oracle assumptions fail
- reviewer or owner withdraws approval

Public status should not imply permanent approval.

## 9. Privacy And No-Oracle Policy

Approval existence is:

- not training data
- not a tuning signal
- not scoring feedback
- not performance evidence
- not real-data evidence
- not learner-state evidence

Approval existence must not expose:

- expected action details
- private note body
- raw learner text
- final, observed-after, or gold text
- private/manual/real paths
- real participant identifiers

The status marker is only a process signal.

## 10. Beginner Explanation

### What Is Approval Existence?

Approval existence means that a reviewer can confirm an approval record exists
somewhere private or local.

It does not mean the approval text is public.

### Why Not Publish The Approval Body?

The approval body may contain reviewer-specific notes, local process details, or
private context. The public repository only needs safe status, if any.

### Why Is A Status Label Enough?

A status label can tell future readers whether approval was required, present,
missing, deferred, revoked, or needing recheck without exposing private content.

### Why Should Scripts Not Read Approval Bodies?

Approval is a human governance boundary. Scripts should validate configs and
outputs, but they should not parse private approval records or depend on private
notes.

### Why Is Approval Not Permanent?

Approval depends on assumptions. If the value, target constraint, schema, or
output safety policy changes, the approval should be rechecked.

## 11. Related Documents

- [Metadata completeness fixture preflight check](metadata_completeness_fixture_preflight_check.md)
- [Metadata completeness private approval record workflow](metadata_completeness_private_approval_record_workflow.md)
- [Metadata completeness actual fixture implementation plan](metadata_completeness_actual_fixture_implementation_plan.md)
- [Metadata completeness fixture approval record template](templates/metadata_completeness_fixture_approval_record_template.md)
- [Metadata completeness value candidate approval checklist](metadata_completeness_value_candidate_approval_checklist.md)
- [Forbidden-term path-safety test hardening design](forbidden_term_path_safety_test_hardening_design.md)
- [Observation note storage and review workflow](observation_note_storage_and_review_workflow.md)
