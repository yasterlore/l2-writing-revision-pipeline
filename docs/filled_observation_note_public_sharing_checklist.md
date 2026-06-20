# Filled Observation Note Public-Sharing Checklist

This checklist is for the exceptional case where a filled observation note is
being considered for inclusion in the public repository.

Public sharing is not recommended by default. The default policy remains:
filled observation notes stay private or local. The public repository should
normally contain blank templates, workflow documents, and synthetic design
rationale only.

This is a safety checklist, not performance evaluation. It does not authorize
raw outputs, private data, no-oracle-unsafe content, weight changes, scoring
changes, ranking changes, F1, accuracy, calibration, or learner-state
estimation.

## 1. Purpose

The purpose of this checklist is to prevent unsafe public sharing of filled
observation notes.

Use it before placing any filled observation note in the public repository.
It checks for:

- raw text leakage
- JSONL body leakage
- summary body leakage
- config body leakage
- private/manual/real path leakage
- no-oracle-unsafe content
- performance claims
- weight or ranking decisions based only on observation notes

This checklist does not make public sharing desirable. It only defines extra
safety review steps for rare exceptions.

## 2. Principles

- Filled notes are private/local by default.
- Public repository content should usually be blank templates and workflow docs.
- Public sharing is exceptional.
- Public sharing requires reviewer checks.
- Repository owner approval is required before committing a filled note.
- A public filled note must remain count-only.
- A public filled note must not include raw generated outputs.
- A public filled note must not be used as direct scoring, ranking, or config
  feedback.

## 3. Required Checks Before Public Sharing

Before public sharing, confirm all items:

- [ ] No raw text is included.
- [ ] No JSONL body is included.
- [ ] No `summary.csv` body is included.
- [ ] No `diagnostic_summary.json` body is included.
- [ ] No config JSON body is included.
- [ ] No candidate score rows are included.
- [ ] No candidate descriptions are included.
- [ ] No proposed edit payload is included.
- [ ] No expected action details are included.
- [ ] No evaluation report body is included.
- [ ] No `final_text` is included.
- [ ] No `observed_after_text` is included.
- [ ] No `gold_label` is included.
- [ ] No teacher or human correction text is included.
- [ ] No real participant identifiers are included.
- [ ] No private/manual/real paths are included.
- [ ] No performance claim is made.
- [ ] No weight or ranking change decision is made based only on the note.

If any item is not confirmed, do not share the note publicly.

## 4. Content That May Be Allowed

The following may be allowed after review:

- high-level count-only observation
- manually summarized count-only statement
- safe decision label
- documentation issue label
- fixture coverage issue label
- no action decision
- proceed style decision
- a statement that no raw output was included
- a statement that no performance claim is made

Do not paste actual summary bodies, diagnostic summary bodies, config bodies,
JSONL bodies, score rows, or raw text.

## 5. Prohibited Content

Do not include:

- raw outputs
- generated file bodies
- pasted CSV tables
- pasted JSON reports
- text snippets
- participant data
- exact-match details
- ranking rows
- config body
- prompt or session content
- private paths
- manual output paths
- real data paths
- local machine-specific private paths
- expected action details
- evaluation report body
- candidate descriptions
- proposed edit payload

If the note needs one of these items to be understandable, it is not suitable
for public sharing.

## 6. Performance Claim Guardrails

A public filled note must explicitly avoid performance claims.

It is not:

- accuracy
- F1
- calibration
- ranking quality
- grammatical correctness
- learner-state quality
- real-data readiness
- publication-level evidence
- model performance evaluation

It must not be used alone to justify:

- changing scoring weights
- changing scoring formula
- changing tie-break policy
- changing candidate ranking
- changing config policy
- claiming real-data readiness

## 7. Review Workflow

Recommended workflow:

1. Fill the note privately or locally.
2. Run the forbidden-content checklist in this document.
3. Remove all generated body snippets.
4. Reduce observations to count-only statements if a public summary is needed.
5. Ask for a second review if public sharing is still desired.
6. Ask the repository owner for final approval.
7. Commit only after the safety review is complete.
8. Keep the private source note outside Git.

The public version, if approved, should be a reduced public-safe derivative,
not the reviewer working note.

## 8. Suggested Public-Safe Note Format

If public sharing is approved, use a minimal public-safe format:

```text
Date:
Reviewer:
Synthetic-only confirmation:
Observation type:
High-level count-only observation:
Follow-up classification:
Final decision:
No raw output included:
No config body included:
No JSONL body included:
No performance claim:
Repository owner approval:
```

Do not include generated output bodies, config bodies, raw rows, exact-match
details, or private paths in this format.

Filled metadata completeness approval records should follow the same or stricter
public-sharing review if public sharing is ever proposed. By default, use the
[metadata completeness private approval record workflow](metadata_completeness_private_approval_record_workflow.md)
and keep filled approval records private/local.

## 9. `.gitignore` And Directory Reminder

The default private/local note directories are ignored:

```text
private_notes/
local_notes/
```

Do not override these ignore rules without review. Do not add filled notes from
ignored directories. If a public-safe derivative is approved, create it as a
separate reviewed document rather than moving a private/local note into Git.

## 10. What Not To Do

Do not:

- create an actual filled observation note as part of this checklist
- add a public filled note without additional review
- add a real-data note
- add generated output bodies
- add a performance report
- add scripts, metrics, or visualizations
- change weights
- change scoring formula
- change tie-break policy
- add F1, accuracy, calibration, or learner-state estimation
- use expected actions as scoring feedback

## 11. Related Documents

- [Observation note storage and review workflow](observation_note_storage_and_review_workflow.md)
- [Metadata completeness private approval record workflow](metadata_completeness_private_approval_record_workflow.md)
- [Synthetic diagnostic observation note template](templates/synthetic_diagnostic_observation_note_template.md)
- [Config-enabled observation note template](templates/config_enabled_observation_note_template.md)
- [Synthetic diagnostic distribution review plan](synthetic_diagnostic_distribution_review_plan.md)
- [Config-enabled summary collector design](config_enabled_summary_collector_design.md)
