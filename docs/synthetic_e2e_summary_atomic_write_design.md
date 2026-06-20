# Synthetic E2E Summary Atomic Write Design

This document designs future atomic-write and completion-marker hardening for
the no-config synthetic E2E summary.

It records the atomic-write design and the initial temp-file rename
implementation. It does not change test code, scorer logic, scorer weights,
scoring formula, deterministic tie-break behavior, or fixtures.

This is not performance evaluation.

## 1. Purpose

The purpose of this design is to describe a future hardening path for
`scripts/run_synthetic_e2e_summary.sh`.

The design focuses on:

- atomic writing of the no-config synthetic E2E summary
- optional completion metadata for downstream checks
- reducing ambiguity when distribution checks run while summary generation is
  in progress
- keeping no-config and config-enabled summaries separate
- preserving output safety and no-oracle boundaries

This is the next design layer after the ordering and precondition hardening for
`scripts/check_synthetic_diagnostic_distribution.sh`.

It is not a performance evaluation and does not add metrics.

## 1.1 Implementation Status

Step 110 implemented the initial no-config summary atomic write behavior:

- `scripts/run_synthetic_e2e_summary.sh` writes rows to
  `tmp/synthetic_e2e_summary/summary.csv.tmp`
- after summary generation completes, the script renames that temp file to
  `tmp/synthetic_e2e_summary/summary.csv`
- if the script exits before the rename, the temp file is removed when possible
- existing `summary.csv` is not overwritten by an incomplete temp file
- completion marker and wrapper script are still not implemented
- Step 112 adds a no-config `summary.manifest.json` marker after successful
  summary generation; wrapper script support is still not implemented

This implementation remains no-config only and does not touch
`tmp/synthetic_e2e_config_summary`.

## 2. Current State

Current no-config summary flow:

1. `scripts/run_synthetic_e2e_summary.sh` generates
   `tmp/synthetic_e2e_summary/summary.csv` through a temporary
   `summary.csv.tmp` file and final rename.
2. `scripts/check_synthetic_diagnostic_distribution.sh` reads that no-config
   summary.
3. Step 108 added fail-closed handling for missing, empty, malformed, and
   `no_cases` summaries.
4. Step 110 added the initial temp-file atomic rename for the no-config summary.
5. Step 112 added a safe no-config `summary.manifest.json` completion marker.

The distribution check now rejects config-enabled summary paths and continues
to use safe count-only output.

Still open:

- a downstream check can still read an older complete summary if one exists
- the relationship between `summary.csv` and per-case diagnostic summaries is
  recorded as safe count metadata and checked at the summary row-count level;
  deeper per-case run identity checks are still future work

For the dedicated completion-marker design, see
[Synthetic E2E summary completion marker design](synthetic_e2e_summary_completion_marker_design.md).
For the future diagnostic distribution checker validation design, see
[Synthetic diagnostic distribution marker validation design](synthetic_diagnostic_distribution_marker_validation_design.md).

## 3. Remaining Risks

The remaining risks are ordering and consistency risks, not diagnostic
performance risks.

Risks:

- the distribution check runs while summary generation is in progress
- an old complete `summary.csv` remains and is read by a downstream check
- a partial file is read before all case rows are written
- `summary.csv` and per-case diagnostic summaries come from different runs
- config-enabled summary output is accidentally used for the no-config check
- CI or manual runs parallelize commands that should be sequential
- a failed summary run leaves confusing stale output

These risks should be addressed without printing raw summary bodies or generated
report bodies.

## 4. Atomic Write Design Options

### Option A: `summary.csv.tmp` Then Rename

Write all summary rows to a temporary file in the same directory, then rename it
to `summary.csv` only after generation succeeds.

Benefits:

- simple
- portable enough for the current shell-script workflow
- downstream readers see either the old complete file or the new complete file
- avoids most partial-write reads

Limits:

- downstream checks may still read an old complete file while a new run is in
  progress
- no run metadata is recorded by itself

### Option B: Timestamped Temp Directory

Write a complete run into a timestamped temp directory, then atomically update a
stable pointer, symlink, or copied output.

Benefits:

- keeps complete run artifacts grouped
- can reduce mixed-run confusion

Limits:

- more moving parts
- symlink behavior may vary by environment
- not necessary for the first hardening step

### Option C: Completion Marker

Write a small marker after all summary rows and per-case diagnostic summaries
are complete.

Benefits:

- downstream checks can verify that the run completed
- marker can include safe count-only metadata
- helps distinguish incomplete current run from stale output

Limits:

- marker must be kept in sync with the summary
- marker should not include raw generated content

### Option D: Sequential Wrapper Script

Create a wrapper that runs summary generation and then the diagnostic
distribution check in order.

Benefits:

- simple user experience
- reduces CI ordering mistakes

Limits:

- does not directly prevent stale summary reads outside the wrapper
- still benefits from atomic write and marker support

### Option E: Status Manifest

Write a safe manifest with `run_id`, completion status, expected output paths,
and count-only totals.

Benefits:

- strongest audit trail
- can support future consistency checks

Limits:

- larger design surface
- requires careful privacy review
- not needed for the first implementation

## 5. Recommended Initial Direction

Recommended initial hardening step:

1. Write no-config summary rows to `summary.csv.tmp`.
2. Rename `summary.csv.tmp` to `summary.csv` only after the summary file is
   fully written.
3. Optionally write a small completion marker after the final summary is in
   place.
4. Keep the distribution check reading only the final `summary.csv`.
5. Keep config-enabled summary output separate.
6. Keep stdout count-only and suppress all generated bodies.

This should remain no-config only for the existing summary collector.

The temp-file rename portion is now implemented. The completion marker remains
optional future work. If added, it should contain only safe metadata and should
not become a performance report.

## 6. Completion Marker: Allowed Information

Allowed marker fields:

- `run_id`
- `completed_at`
- `summary_path`
- `case_count`
- `diagnostic_summary_count`
- `content_suppressed=true`
- `no_config_summary=true`
- `summary_schema_status`
- `pipeline_status_summary`, if count-only

The marker should be small, safe, and count-only.

## 7. Completion Marker: Forbidden Information

The marker must not include:

- raw summary body
- diagnostic summary JSON body
- JSONL body
- candidate score rows
- raw text
- local context
- expected action details
- config body
- real participant data
- private/manual/real paths
- performance metrics
- tuning conclusions

The marker should not duplicate generated report contents.

## 8. Distribution Check Integration

Future integration should follow these boundaries:

- the distribution check reads only the final no-config `summary.csv`
- the distribution check does not read `summary.csv.tmp`
- the distribution check may verify a completion marker if implemented later
- the distribution check continues to reject config-enabled summary paths
- `no_cases` remains a failure
- precondition failures remain nonzero
- output remains count-only
- raw summary and diagnostic bodies remain suppressed

If marker verification is added, marker failure should be a precondition
failure, not a silent pass.

## 9. Future Hardening Tests

Future implementation should include smoke or shell-level checks for:

- missing summary
- empty summary
- malformed summary
- header-only summary
- temp file exists but final summary is missing
- temp file exists while final summary remains old
- marker missing
- marker says incomplete
- marker case count does not match final summary row count
- final summary appears to be from a previous run
- config-enabled path rejected
- safe stdout only
- no raw body printed

These tests should be count-only and synthetic-only.

## 10. Output Safety, Privacy, And No-Oracle Policy

This design must preserve:

- no raw summary body
- no JSONL body
- no diagnostic body
- no candidate score rows
- no raw text
- no expected action feedback
- no config body
- no real participant data
- no private/manual/real data
- no performance metric
- no tuning signal

Atomic write and markers are reliability tools, not evaluation tools.

## 11. Beginner Explanation

### What Is Atomic Write?

Atomic write means readers should see either the previous complete file or the
new complete file, not a half-written file.

### Why Write To A Temp File And Rename?

Writing to a temp file lets the script finish building the full summary before
replacing the public `summary.csv`.

The rename step makes the final file appear all at once.

### What Is A Completion Marker?

A completion marker is a small safe file that says a run finished. It can record
count-only metadata such as case count and completion time.

It must not include raw output bodies.

### Why Is Reading An Old Summary A Risk?

If an old `summary.csv` remains while a new summary is being generated, a check
may pass using stale output. That can make a current run look healthier than it
is.

### Why Not Print Raw Bodies For Debugging?

Raw bodies can contain data that docs and stdout should not expose. Debug output
should stay count-only and safe.

## 12. Related Documents

- [Synthetic diagnostic distribution check ordering design](synthetic_diagnostic_distribution_check_ordering_design.md)
- [Synthetic E2E summary completion marker design](synthetic_e2e_summary_completion_marker_design.md)
- [Synthetic diagnostic distribution marker validation design](synthetic_diagnostic_distribution_marker_validation_design.md)
- [Synthetic diagnostic distribution review plan](synthetic_diagnostic_distribution_review_plan.md)
- [Synthetic E2E pipeline](synthetic_e2e_pipeline.md)
- [Public release checklist](public_release_checklist.md)
- [Milestone 03 final docs-only release review](milestone_03_final_docs_only_release_review.md)
