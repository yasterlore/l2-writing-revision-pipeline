# Diagnostic Summary Tooling Plan

This document describes summary-only tooling for descriptive diagnostics in
`ConstraintViolationSet` JSONL.

Step 52 implemented the first diagnostic summary CLI. It does not change
feature extraction, change constraint generation, change scoring, add weights,
add F1, add accuracy, add calibration, or implement learner-state estimation.

## 1. Purpose

Diagnostic summary tooling should aggregate descriptive constraints so that
the project can inspect feature and constraint wiring without exposing raw
text.

The tooling is for diagnosis and future constraint design. It is not a model
performance report.

It must not report:

- F1
- accuracy
- calibration
- learner-state estimates
- correctness claims

It should answer limited structural questions such as:

- Which descriptive constraints were observed?
- How many candidates carried each action family?
- How often did local pattern diagnostics appear in synthetic fixtures?
- Did any safety blocking constraints appear?

## 2. Target Input

Primary input:

- `ConstraintViolationSet` JSONL

Optional input:

- `CandidateScoreSet` JSONL, only when blocked-candidate counts or rank-related
  structural summaries are useful

Allowed data source:

- synthetic E2E output only

Forbidden data source:

- real participant data
- private production output
- `manual_outputs/`
- public CI input derived from real writing

## 3. Information That May Be Aggregated

The tooling may aggregate counts over already-abstract fields:

- `constraint_id` counts
- `constraint_type` counts
- `severity` counts
- candidate `action_type` counts
- `generation_rule` counts
- `action_family` counts
- `candidate_family_bucket` counts, if available from upstream summary input
- blocked candidate counts, if `CandidateScoreSet` is provided
- diagnostic constraint counts
- safety blocking constraint counts

These are structural counts only. They should not include per-episode text,
candidate descriptions, or proposed edits.

## 4. Information That Must Not Be Aggregated

The tooling must not aggregate or display:

- raw `local_context_before`
- candidate description text
- `proposed_edit` payload
- `observed_after_text`
- `final_text`
- `gold_label`
- expected action
- teacher correction
- human correction
- post-hoc annotation
- future context
- per-episode text detail
- real participant identifiers

If any forbidden field appears in input, the tool should fail closed or report
a safe error without printing the offending value.

## 5. Output Policy

Initial output can be JSON summary or CSV summary.

The Step 52 implementation writes JSON summary output.

Output location:

- `tmp/diagnostic_summary/`
- `tmp/synthetic_e2e_summary/`
- another Git-ignored synthetic-output directory

Standard output should contain only count summaries and paths. It should not
print raw JSONL lines, per-episode details, local context, candidate text, or
evaluation report bodies.

Documentation must not paste generated report bodies. If a summary needs to be
described in docs, record the schema and high-level outcome only.

## 6. Initial Summary Fields

Initial summary candidates:

- `total_constraint_sets`
- `total_candidates`
- `total_constraints`
- `descriptive_constraint_count`
- `blocking_constraint_count`
- `safety_constraint_count`
- `diagnostic_constraint_count`
- `top_constraint_ids`
- `action_family_counts`
- `generation_rule_counts`
- `candidate_family_bucket_counts`
- `local_pattern_constraint_counts`
- `linguistic_placeholder_constraint_counts`

`top_constraint_ids` should be a bounded list, such as the top 20 by count,
not a dump of every record.

## 7. Local Pattern Diagnostic Summary

The local pattern diagnostic summary should count these groups:

- `CONTEXT-BEFORE-*`
- `CURSOR-AT-*`
- `SELECTION-*`
- `LEFT-CONTEXT-ENDS-*`
- `LEFT-CHAR-CLASS-*`

These counts are not performance metrics. They only describe how synthetic
candidate diagnostics are distributed.

Examples of valid questions:

- How many candidates had `LEFT-CHAR-CLASS-PUNCTUATION` observed?
- How many candidates had a collapsed selection diagnostic?
- How often did context-before buckets appear in synthetic smoke fixtures?

Invalid interpretation:

- treating a diagnostic count as evidence of correctness
- comparing learners by diagnostic count
- claiming model performance from diagnostic summaries

## 8. Safety Blocking Summary

The summary may separately count safety constraints:

- `NO-LEAKAGE-FLAG`
- `NO-OBSERVED-EDIT-TEXT`
- `NO-UNSAFE-CANDIDATE`

This is a wiring and safety check, not an evaluation metric.

If safety blocking counts are nonzero in synthetic smoke output, the next step
should be investigation, not ranking or performance interpretation.

## 9. No-Oracle and Privacy Policy

The summary tool should read abstract constraint records only.

It must not reintroduce:

- raw `local_context_before`
- post-edit context
- final text
- gold labels
- expected actions
- teacher corrections
- real participant identifiers

Expected actions remain evaluation-only. They should not be used in diagnostic
summary tooling.

The summary should be safe even if someone later runs it on private data, but
this repository should only use synthetic fixtures and synthetic E2E outputs.

## 10. Implementation Test Plan

When implemented, tests should cover:

- summary generation from synthetic `ConstraintViolationSet` fixture
- optional safe use of synthetic `CandidateScoreSet` fixture
- raw text absent from output
- forbidden fields rejected or safely reported without values
- count consistency
- empty input handling
- malformed JSONL handling
- unknown constraint ID handling
- tmp output is Git ignored
- stdout includes summary counts only
- no F1, accuracy, calibration, or learner-state fields

All tests should use synthetic fixtures only.

## 11. Future Roadmap

### Step 52: Implement Diagnostic Summary Tool

Completed: `python -m ot_scorer.summarize_diagnostics` reads
`ConstraintViolationSet` JSONL and writes a summary JSON file under `tmp/` or
another caller-provided path. Empty input produces a valid zero-count summary.

### Step 53: Connect Diagnostic Summary to Synthetic E2E Summary

Completed: `scripts/run_synthetic_e2e_summary.sh` optionally runs the diagnostic
summary tool for each case after the synthetic E2E pipeline creates
`constraint_violations.jsonl`.

The collector writes `diagnostic_summary.json` under
`tmp/synthetic_e2e/<case_name>/` and records only safe top-level count fields in
`tmp/synthetic_e2e_summary/summary.csv`.

It does not print diagnostic report bodies, raw JSONL rows, per-episode detail,
candidate descriptions, proposed edits, local context, expected actions, or
performance metrics.

### Step 54: Inspect Synthetic Diagnostic Distribution

Planned in
[`synthetic_diagnostic_distribution_review_plan.md`](synthetic_diagnostic_distribution_review_plan.md):
inspect count-only synthetic diagnostic distributions without reading raw JSONL,
report bodies, per-episode text, expected actions, or performance metrics.

### Later: Scoring Review

Do not use diagnostic summaries to tune weights or claim performance until
there is a separate scoring-policy design, no-oracle review, and validation
plan.

## 12. Non-Goals

This plan and implementation do not:

- change constraint generation
- change scoring
- add weights
- add F1
- add accuracy
- add calibration
- implement learner-state estimation
- introduce real participant data
- introduce real gold labels
- use expected actions
