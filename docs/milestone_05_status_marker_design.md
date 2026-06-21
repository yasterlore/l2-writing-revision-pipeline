# Milestone 05 Status Marker Design

This document designs a future public-safe status marker for Milestone 05
Makefile orchestration documentation.

It is design documentation only. It does not change the Makefile, add or
remove Makefile targets, add a justfile, add Airflow or Dagster, change
workflows, change scripts, change tests, change implementation logic, change
scorer logic, change the manifest schema, or evaluate performance.

Step 155 implementation note: the short marker has been created at
[docs/status/milestone_05_status.md](status/milestone_05_status.md). The
boundaries in this design remain the maintenance rules for future updates.

## 1. Purpose

The purpose of this document is to define how a short public-safe status marker
should represent that the Milestone 05 docs-only release review is complete.

The marker must separate Makefile orchestration maintenance status from
research performance. It must not include raw logs, generated file bodies,
workflow output bodies, or performance claims.

The marker should help readers find the recap and final review without implying
that the model, scorer, or pipeline has been validated for research,
production, or data collection.

## 2. Current State

Current state:

- [Milestone 05 Makefile orchestration recap](milestone_05_makefile_orchestration_recap.md)
  exists.
- [Milestone 05 final docs-only release review](milestone_05_final_docs_only_release_review.md)
  exists.
- The Makefile thin entrypoint exists.
- `.NOTPARALLEL` and `make help` summary-flow guidance are implemented.
- Public docs do not include raw logs or actual filled run reports.
- The short status marker now exists at
  [docs/status/milestone_05_status.md](status/milestone_05_status.md).

This document records the marker design and the rules for future marker
updates.

## 3. Status Marker Options

### Option A: `docs/status/milestone_05_status.md`

Pros:

- matches the existing short status-marker pattern
- keeps status markers grouped under `docs/status/`
- easy to link from README, checklist, recap, and final review
- keeps the marker short and separate from long design docs

Cons:

- adds another document to maintain
- requires a small link update in multiple docs

### Option B: `docs/milestone_05_makefile_orchestration_status.md`

Pros:

- colocates the marker with other milestone docs
- filename is explicit about Makefile orchestration

Cons:

- less consistent with the existing `docs/status/` marker location
- longer filename for a short status note

### Option C: Public Release Checklist Status Section

Pros:

- keeps status near release procedure
- no new marker file

Cons:

- checklist can become crowded
- status is less reusable as a short standalone reference

### Option D: README Short Status Note

Pros:

- highest visibility
- no new marker file required

Cons:

- README should remain an index, not the detailed status record
- risks overemphasizing a maintenance status as a release claim

### Option E: No Marker

Pros:

- no additional file
- final review remains the authoritative readiness statement

Cons:

- readers need to open a longer review to understand current status
- no short public-safe marker exists for quick navigation

## 4. Recommended Approach

Initial recommendation: create a short dedicated status marker at
`docs/status/milestone_05_status.md`. Step 155 implemented this marker.

Recommended boundaries:

- README should link to the marker only.
- Public release checklist and final review should link to the marker.
- The marker should not include raw logs, run URLs, screenshots, or body dumps.
- The status should be limited to orchestration and Makefile adoption
  documentation.
- The marker must not claim research performance, scorer quality, model
  validity, production readiness, or data-collection readiness.

## 5. Allowed Marker Content

The future status marker may include:

- milestone name
- status: docs-only release review completed
- scope: Makefile orchestration and shell orchestration modernization
  documentation
- Makefile state:
  - thin entrypoint
  - default `help` target
  - `check-summary-flow` sequential guidance
- configured checks passed as a local release-quality / Makefile verification
  summary
- implementation scope: orchestration maintenance only
- explicit no raw logs / no performance claim note
- links to:
  - [Milestone 05 Makefile orchestration recap](milestone_05_makefile_orchestration_recap.md)
  - [Milestone 05 final docs-only release review](milestone_05_final_docs_only_release_review.md)
  - [Milestone 05 status marker design](milestone_05_status_marker_design.md)
  - [Public release checklist](public_release_checklist.md)

## 6. Disallowed Marker Content

The future marker must not include:

- raw workflow logs
- raw CI logs
- raw Makefile output bodies
- run URLs
- screenshots
- JSONL, summary, marker, diagnostic, or config bodies
- candidate score rows
- raw learner text
- expected action details
- real participant data
- F1, accuracy, calibration, or model performance claims
- claims that Makefile success proves research validity
- production ready, research ready, or data collection ready claims
- claims that Airflow or Dagster is unnecessary forever

## 7. Wording Guidance

Preferred wording:

- "docs-only release review completed"
- "orchestration maintenance status"
- "Makefile thin entrypoint"
- "no performance claim"
- "configured checks passed"

Avoid wording such as:

- "validated model"
- "research ready"
- "production ready"
- "data collection ready"
- "model quality confirmed"
- "pipeline accuracy validated"
- "orchestration fully modernized"

The marker should say what was checked, not imply broader readiness.

## 8. Verification Before Creating Marker

Before creating the marker file, verify:

- README link path is correct
- final review exists
- recap exists
- public release checklist alignment is present
- `make help` works
- no conflict markers are present
- the marker includes no raw logs
- the marker includes no private paths
- the marker includes no performance claims
- the marker includes no production or data-collection readiness claims

## 9. Future Implementation Checklist

Implementation checklist:

- create `docs/status/milestone_05_status.md`
- update README link
- update public release checklist link
- update final review link
- run Markdown link check
- run `make check-release-quality`
- run conflict-marker and forbidden-wording safety grep
- keep the marker short

## 10. Beginner Notes

A status marker is a short public-safe note that tells readers the current
state of a milestone without making them read the full recap or review first.

It is useful because recap and review docs can be long. A marker gives a quick
pointer to the important status and the authoritative docs.

Makefile success must be scoped carefully. It means configured checks passed;
it does not prove model quality, research validity, production readiness, or
data-collection readiness.

Raw logs are omitted because they can include too much operational detail or
accidentally expose generated content. Safe high-level status is enough.

Airflow and Dagster are not described as unnecessary forever. They are deferred
until production-like scheduling, durable run history, monitoring, or other
heavier orchestration needs actually appear.

## Related Documents

- [Milestone 05 status marker](status/milestone_05_status.md)
- [Milestone 05 Makefile orchestration recap](milestone_05_makefile_orchestration_recap.md)
- [Milestone 05 final docs-only release review](milestone_05_final_docs_only_release_review.md)
- [Orchestration modernization design](orchestration_modernization_design.md)
- [Task runner selection design](task_runner_selection_design.md)
- [Public release checklist](public_release_checklist.md)
