# Milestone 04 Status Marker Design

This document designs the public-safe status marker for Milestone 04 CI
maintenance documentation.

It is design documentation and implementation notes. The implemented marker is
[Milestone 04 status](status/milestone_04_status.md). This document does not
change workflows and does not make any research-performance claim.

## 1. Purpose

The purpose of a Milestone 04 status marker is to show, in a short and
public-safe form, that the Milestone 04 docs-only release review has been
completed.

The marker must separate CI maintenance status from research performance. It
must not include raw workflow logs, remote-run bodies, generated summary bodies,
or any participant data. It is not a performance evaluation.

## 2. Current State

Current Milestone 04 documentation state:

- the Milestone 04 CI maintenance recap has been created
- the Milestone 04 final docs-only release review has been created
- the short public-safe status marker has been created at
  `docs/status/milestone_04_status.md`
- the release-quality manual workflow remote run has been confirmed at a safe
  high level as Success
- the existing CI remote run has been confirmed at a safe high level as Success
- public docs do not include raw workflow logs or run URLs
- public docs do not include actual filled remote-run reports

The current public-safe remote-run summaries are limited to workflow result,
artifact status, visible warning status, and maintenance scope. They do not
claim scorer quality, model validity, or production readiness.

## 3. Status Marker Candidates

Candidate A: `docs/status/milestone_04_status.md`

- Pros: clearly reads as a reusable status marker location; can scale if later
  milestones need short status files.
- Cons: introduces a new `docs/status/` directory.

Candidate B: `docs/milestone_04_release_quality_status.md`

- Pros: simple flat docs path; easy to link from the README and checklist.
- Cons: less clearly separated from longer milestone narrative documents.

Candidate C: a status section inside `docs/public_release_checklist.md`

- Pros: keeps release-facing status near the release checklist.
- Cons: mixes a marker with a checklist and can make the checklist harder to
  scan.

Candidate D: a short status note in `docs/README.md`

- Pros: very visible.
- Cons: README should stay as navigation, not as the source of status truth.

Candidate E: no marker; rely only on the final review document

- Pros: avoids another file.
- Cons: makes it harder to find the current status without reading the longer
  review.

## 4. Recommended Approach

The implemented approach is a short dedicated status marker at
`docs/status/milestone_04_status.md`.

The README links to the marker. The public release checklist, recap, final
docs-only release review, and this design document also link to it.

The marker should:

- stay short
- avoid raw logs and run URLs
- limit success wording to workflow maintenance
- explicitly state that it is not a performance evaluation
- avoid any claim about research quality, scorer quality, model validity,
  production readiness, or data-collection readiness

The marker is intentionally short. Longer context remains in the recap, final
review, and checklist.

## 5. Items Allowed In The Marker

The marker may include only safe high-level fields:

- milestone name
- status: docs-only release review completed
- scope: CI maintenance / release-quality workflow
- remote checks: release-quality manual workflow success and existing CI success
- artifacts uploaded: no
- visible warning status: not shown in visible summary screens
- implementation scope: workflow maintenance only
- note that raw logs are not included
- note that there is no performance claim
- links to the recap, final review, and public release checklist

## 6. Items Not Allowed In The Marker

The marker must not include:

- raw workflow logs
- raw CI logs
- run URLs if they expose private context
- screenshots containing sensitive content
- JSONL body
- summary body
- marker body
- diagnostic body
- config body
- candidate score rows
- raw learner text
- expected action details
- real participant data
- F1, accuracy, calibration, or model-performance claims
- any claim that CI success proves research validity

## 7. Wording Guidance

Preferred wording:

- "docs-only release review completed"
- "workflow maintenance status"
- "no performance claim"
- "safe high-level remote-run summary"

Avoid wording such as:

- "validated model"
- "research ready"
- "production ready"
- "data collection ready"
- "performance validated"
- "accuracy confirmed"

If the marker mentions success, the sentence should make the scope clear.
For example, it may say that the release-quality workflow maintenance checks
completed, but it must not imply that scoring behavior or research conclusions
were validated.

## 8. Verification Before Creating The Marker

Before updating the status marker, verify:

- the README link path is correct
- the Milestone 04 final docs-only release review exists
- the Milestone 04 CI maintenance recap exists
- the public release checklist links to the right marker or design
- workflow YAML still parses
- no conflict markers remain in docs
- the marker contains no raw logs
- the marker contains no private paths
- the marker contains no performance claim

## 9. Future Implementation Checklist

Future marker maintenance should:

- update the README link
- update the public release checklist link
- link from the final docs-only release review
- run a Markdown link check
- run the full release-quality wrapper
- run the conflict-marker safety grep
- keep the marker short and public-safe

## 10. Beginner Notes

A status marker is a small document that says where a milestone stands. It is
not the full history of the milestone.

A short marker is useful because readers can quickly see that the docs-only
review is complete, then follow links to the recap and final review for details.

The meaning of success must be limited because CI success only says that
configured workflow checks completed. It does not prove that the research model
is valid or that scorer quality improved.

Raw logs are not included because they can contain paths or generated outputs
that should not be preserved in public documentation. A safe high-level summary
is enough for release-maintenance status.

## Related Documents

- [Milestone 04 CI maintenance recap](milestone_04_ci_maintenance_recap.md)
- [Milestone 04 final docs-only release review](milestone_04_final_docs_only_release_review.md)
- [Milestone 04 status](status/milestone_04_status.md)
- [Public release checklist](public_release_checklist.md)
