# Observation Note Storage and Review Workflow

This document defines where observation notes should live, how they should be
reviewed, and what may be placed in the public repository.

It is an operations design document only. It does not add analysis, does not
add filled notes, does not change implementation logic, does not change default
weights, does not change the scoring formula, does not change deterministic
tie-break behavior, and does not add F1, accuracy, calibration, or
learner-state estimation.

This is not performance evaluation.

## 1. Purpose

The workflow exists to:

- record observation notes safely
- prevent raw text, JSONL bodies, summary bodies, and config bodies from being
  pasted into notes
- keep notes from being mistaken for performance claims
- separate public repository design artifacts from private or local review
  notes
- keep synthetic diagnostic review and config-enabled review count-only
- preserve the no-oracle boundary before any future scoring-policy work

Observation notes are human review aids. They are not training data, tuning
signals, scoring feedback, or publication-level evidence.

## 2. Target Notes

This workflow applies to:

- synthetic diagnostic observation notes created from
  `templates/synthetic_diagnostic_observation_note_template.md`
- config-enabled observation notes created from
  `templates/config_enabled_observation_note_template.md`

Future private validation notes are separate. They require their own storage,
privacy, access-control, and review design before any private validation work.

## 3. Recommended Storage Policy

### Public Repository

The public repository should contain:

- blank templates
- workflow documents
- synthetic design rationale
- count-only schema descriptions
- safe process checklists

The public repository should not contain filled observation notes by default.
If a filled note is proposed for the public repository, it needs an additional
review focused on privacy, no-oracle safety, content suppression, and
performance-claim risk.

### Private Or Local Storage

Private or local storage may contain:

- actual filled observation notes
- count-only observation notes
- reviewer-specific notes
- temporary notes used during local synthetic review

Recommended local directories, if needed:

```text
private_notes/
local_notes/
```

These directories should stay Git ignored. Do not create these directories
unless there is an actual local review need.

### Generated Outputs Under `tmp/`

Generated summary outputs should remain under `tmp/`, for example:

```text
tmp/synthetic_e2e_summary/
tmp/synthetic_e2e_config_summary/
tmp/synthetic_e2e/
```

Generated outputs are Git ignored and should not be copied into docs.

## 4. What May Be Placed In The Public Repository

Allowed public artifacts:

- blank observation note templates
- storage and review workflow docs
- synthetic design rationale
- count-only schema descriptions
- safe command references
- no-oracle and privacy guardrails

Allowed public docs may mention paths and field names, but they must not paste
actual summary bodies, config bodies, JSONL bodies, candidate rows, or raw text.

## 5. What Should Not Be Placed In The Public Repository

Do not place the following in the public repository by default:

- filled observation notes
- raw `summary.csv` body
- `diagnostic_summary.json` body
- config-enabled `summary.csv` body
- config JSON body
- JSONL body
- raw text
- candidate score rows
- candidate descriptions
- proposed edit payload
- expected action details
- evaluation report body
- final text
- observed-after text
- gold label
- teacher or human correction
- real participant identifiers
- private/manual/real paths
- private validation notes

Do not use public docs to store local diagnostic outputs or reviewer-specific
notes.

## 6. Review Procedure

Recommended review procedure:

1. Run the relevant synthetic checks.
2. Open the count-only summary locally.
3. Copy the appropriate blank template into private or local storage.
4. Fill only count-only fields and safe status fields.
5. Verify that no forbidden content was recorded.
6. Record only a safe high-level decision in public docs if a public record is
   needed.
7. Do not use the note alone to change weights, ranking, scoring formula,
   tie-break policy, candidate generation, or config policy.

For synthetic diagnostic review, start from:

```text
docs/templates/synthetic_diagnostic_observation_note_template.md
```

For config-enabled summary review, start from:

```text
docs/templates/config_enabled_observation_note_template.md
```

## 7. Checklist Before Sharing Any Note

Before sharing a note outside private or local storage, confirm:

- [ ] No raw text is included.
- [ ] No JSONL body is included.
- [ ] No summary CSV body is included.
- [ ] No diagnostic summary JSON body is included.
- [ ] No config JSON body is included.
- [ ] No candidate score rows are included.
- [ ] No candidate descriptions are included.
- [ ] No proposed edit payload is included.
- [ ] No expected action details are included.
- [ ] No evaluation report body is included.
- [ ] No real participant data is included.
- [ ] No private/manual/real paths are included.
- [ ] No performance claim is made.
- [ ] No weight or ranking change decision is based only on the note.

If any item cannot be confirmed, do not share the note publicly.

## 8. No-Oracle And Privacy Policy

Observation notes must preserve the no-oracle boundary:

- an observation note is not training data
- an observation note is not a tuning signal
- an observation note is not scoring feedback
- expected action details remain evaluation-only
- post-edit, final, gold, teacher, or human correction text must not be used
- raw local context must not be copied into notes
- private or real participant data must not be used

Count-only observations may support later design discussions, but they cannot
justify weight changes, ranking changes, or performance claims by themselves.

## 9. `.gitignore` And Directory Guidance

Recommended private or local note directories:

```text
private_notes/
local_notes/
```

These directories should be Git ignored before use. The repository ignore file
may include both root-level and nested variants:

```text
private_notes/
local_notes/
**/private_notes/
**/local_notes/
```

Do not create actual private note directories unless a local review needs them.
Do not add actual filled notes to Git. Generated summaries should remain under
`tmp/`, which is already ignored.

## 10. What Not To Do Yet

Do not add:

- actual filled observation notes
- real-data notes
- private validation notes
- performance reports
- visualization scripts
- additional metric scripts
- weight changes
- scoring formula changes
- tie-break changes
- F1, accuracy, calibration, or learner-state estimation

Do not use expected actions as scoring feedback or config feedback.

## 11. Related Documents

- [Synthetic diagnostic observation note template](templates/synthetic_diagnostic_observation_note_template.md)
- [Config-enabled observation note template](templates/config_enabled_observation_note_template.md)
- [Synthetic diagnostic distribution review plan](synthetic_diagnostic_distribution_review_plan.md)
- [Config-enabled summary collector design](config_enabled_summary_collector_design.md)
- [Synthetic E2E pipeline](synthetic_e2e_pipeline.md)
- [No-oracle policy](03_no_oracle_policy.md)
