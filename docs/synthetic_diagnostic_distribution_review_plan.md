# Synthetic Diagnostic Distribution Review Plan

This document describes how to review synthetic diagnostic distribution outputs
from the summary collector safely.

It is a review plan only. It does not add visualization, additional tooling,
scoring changes, calibration, F1, accuracy, or learner-state estimation.

## 1. Purpose

The purpose of this review is to inspect count-only diagnostic distributions
from synthetic E2E runs.

The review should answer wiring and diagnostic questions:

- Did each synthetic case produce a diagnostic summary?
- Are local pattern diagnostic constraints appearing as expected?
- Are linguistic placeholder diagnostic constraints appearing when candidate
  generation emits those placeholder families?
- Are safety or blocking constraints unexpectedly increasing?

This review is not model performance evaluation. It is not evidence of
grammatical correctness, ranking quality, learner-state quality, F1, accuracy,
or calibration.

## 2. Review Inputs

Allowed inputs:

- `tmp/synthetic_e2e_summary/summary.csv`
- `tmp/synthetic_e2e/<case_name>/diagnostic_summary.json`
- count-only fields created from synthetic cases

Allowed data source:

- synthetic fixture runs only

Forbidden data source:

- real participant data
- private production output
- `manual_outputs/`
- `private_data/`
- `real_data/`
- `participant_data/`

The `tmp/` outputs are Git-ignored. Do not commit them.

## 3. Items That May Be Observed

The review may inspect count-only fields:

- `diagnostic_summary_status`
- `diagnostic_total_constraints`
- `diagnostic_descriptive_constraint_count`
- `diagnostic_blocking_constraint_count`
- `diagnostic_safety_constraint_count`
- `diagnostic_local_pattern_constraint_count`
- `diagnostic_linguistic_placeholder_constraint_count`
- `diagnostic_non_leaky_linguistic_constraint_count`
- per-case presence or absence of expected diagnostic categories
- top constraint ID counts from `diagnostic_summary.json`, if needed

These fields describe diagnostic wiring. They do not describe correctness.

## 4. Items That Must Not Be Observed

The review must not inspect, copy, summarize, or paste:

- raw JSONL bodies
- raw `local_context_before`
- candidate descriptions
- `proposed_edit`
- per-episode text detail
- expected action as model feedback
- `final_text`
- `observed_after_text`
- `gold_label`
- teacher or human correction
- real participant identifiers
- real participant data

Expected actions are evaluation-only and must not be used as feedback for
diagnostic design, candidate generation, scoring, or ranking in this review.

## 5. Initial Review Questions

Start with these questions:

- Did every synthetic case finish with `diagnostic_summary_status=ok`?
- Did every case with `constraint_violations.jsonl` produce
  `diagnostic_summary.json`?
- Are local pattern constraints present across all synthetic cases?
- Are linguistic placeholder constraints present when placeholder candidates are
  generated?
- Did blocking or safety constraint counts increase unexpectedly?
- Are diagnostic counts unexpectedly zero?
- Are diagnostic counts unexpectedly large for the case size?
- Are pending evaluation cases being kept separate from diagnostic summary
  status?
- Is the review avoiding any interpretation of diagnostic counts as accuracy or
  correctness?

## 6. Judgments That Must Not Be Made

Do not use this review to claim:

- model accuracy
- grammatical correctness
- learner-state quality
- candidate ranking performance
- real-data readiness
- publication-level results
- score calibration
- selective prediction quality

Diagnostic distribution review can suggest implementation follow-up questions,
but it does not justify changing weights, tie-breaks, or scoring formulas by
itself.

## 7. Output and Recording Policy

Do not paste `diagnostic_summary.json` bodies into documentation.

Do not paste `summary.csv` bodies into documentation.

If notes are needed, record high-level, count-only observations. For example,
it is acceptable to write that a synthetic case had diagnostic summary
generation available, but do not paste generated report rows or JSON objects.

Public documentation should remain design-oriented. Generated reports should
stay under `tmp/` or another Git-ignored location.

## 8. No-Oracle and Privacy Policy

The review uses only count-only summaries derived from abstract
`ConstraintViolationSet` records.

The review must not go back to raw text. It must not use post-edit context,
final text, gold labels, teacher corrections, or expected actions as feedback
signals.

Do not adjust scorer weights, ranking, candidate generation, or constraint
behavior based only on this review. Any future change needs a separate
no-oracle review and design step.

## 9. Suggested Manual Review Procedure

From the repository root, run the collector:

```bash
scripts/run_synthetic_e2e_summary.sh
```

Then run or inspect only safe counts:

- confirm that `summary.csv` exists under `tmp/synthetic_e2e_summary/`
- confirm that each case has `diagnostic_summary_status`
- check count columns, not JSONL contents
- optionally inspect top-level count keys in
  `tmp/synthetic_e2e/<case_name>/diagnostic_summary.json`

If using `scripts/check_synthetic_diagnostic_distribution.sh`, run it only
after `scripts/run_synthetic_e2e_summary.sh` has completed. See
[Synthetic diagnostic distribution check ordering design](synthetic_diagnostic_distribution_check_ordering_design.md).

Do not open or paste raw JSONL files. Do not copy generated report bodies into
docs.

## 10. Future Roadmap

### Step 55: Optional Diagnostic Distribution Smoke Check Script

Implemented as `scripts/check_synthetic_diagnostic_distribution.sh`.

The script verifies that `summary.csv` exists, diagnostic columns are present,
at least one case has `diagnostic_summary_status=ok`, and diagnostic count
fields are parseable. It prints count-only summary information and does not
print raw CSV bodies, diagnostic summary bodies, raw JSONL, per-episode detail,
or performance metrics.

For ordering preconditions and `no_cases` interpretation, see
[Synthetic diagnostic distribution check ordering design](synthetic_diagnostic_distribution_check_ordering_design.md).

### Step 56: Synthetic Diagnostic Observation Note Template

Completed in
[`templates/synthetic_diagnostic_observation_note_template.md`](templates/synthetic_diagnostic_observation_note_template.md).
Use it for local, count-only observations. It avoids JSONL bodies, report
bodies, per-episode text, expected-action feedback, and performance claims.
For note storage and sharing policy, see
[Observation note storage and review workflow](observation_note_storage_and_review_workflow.md).

### Step 57: Non-Leaky Linguistic Constraint Design

Status: initial non-leaky linguistic diagnostic constraints have been designed
and implemented as descriptive records. The summary collector records their
aggregate count in `diagnostic_non_leaky_linguistic_constraint_count`.

### Later: Scoring Reflection

Only after separate no-oracle, validation, and scoring-policy reviews should
diagnostic summaries influence scoring design. They should not directly tune
weights or ranking.

## 11. Non-Goals

This plan does not:

- implement a visualization
- implement a new aggregation tool
- change feature extraction
- change constraint generation
- change scoring
- add F1
- add accuracy
- add calibration
- implement learner-state estimation
- process real participant data
- introduce real gold labels
- use expected actions as scoring feedback
