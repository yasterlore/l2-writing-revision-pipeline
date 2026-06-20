# Synthetic E2E Summary Completion Marker Design

This document designs a future completion marker or run-id manifest for the
no-config synthetic E2E summary.

It records the marker design and the initial no-config marker implementation.
It does not change tests, scorer logic, scorer weights, scoring formula,
deterministic tie-break behavior, or fixtures.

This is not performance evaluation.

## 1. Purpose

The purpose of this design is to describe how a future completion marker or
run-id manifest could help downstream checks confirm that a no-config synthetic
E2E summary belongs to a completed run.

The design aims to:

- reduce the risk of reading a stale old complete `summary.csv`
- make completion state visible through safe count-only metadata
- keep output safety and no-oracle boundaries unchanged
- keep no-config and config-enabled summary outputs separate
- avoid turning diagnostic checks into performance evaluation

The marker is a reliability and ordering aid. It is not a model-quality signal.

## 1.1 Implementation Status

Step 112 implemented the initial no-config summary manifest:

- `scripts/run_synthetic_e2e_summary.sh` writes
  `tmp/synthetic_e2e_summary/summary.manifest.json.tmp`
- after a successful no-config summary run, the temp marker is renamed to
  `tmp/synthetic_e2e_summary/summary.manifest.json`
- the marker contains safe count-only metadata only
- if the summary run fails, the marker is not created
- stale marker files are removed at the start of a new summary run
- `scripts/check_synthetic_diagnostic_distribution.sh` does not yet require or
  validate the marker

The marker remains no-config only and is not written under
`tmp/synthetic_e2e_config_summary`.

For the future checker-side validation design, see
[Synthetic diagnostic distribution marker validation design](synthetic_diagnostic_distribution_marker_validation_design.md).

## 2. Current State

Current state:

- `scripts/run_synthetic_e2e_summary.sh` writes to `summary.csv.tmp` and then
  renames the completed file to `summary.csv`.
- `scripts/run_synthetic_e2e_summary.sh` also writes a safe
  `summary.manifest.json` after successful summary generation.
- `scripts/check_synthetic_diagnostic_distribution.sh` reads the final
  no-config `summary.csv`.
- The diagnostic distribution check does not require the marker yet.
- The diagnostic distribution check is no-config only.
- Config-enabled summaries are generated separately under
  `tmp/synthetic_e2e_config_summary`.

The atomic rename reduces partial-write risk. The marker records safe
completion metadata for future checks, but marker-required validation is still
future work.

## 3. Remaining Risks

Remaining risks are ordering and stale-output risks:

- a check may read an old complete `summary.csv` while a new run is in progress
- `summary.csv` and per-case diagnostic summaries may come from different runs
- `summary.csv` may be complete but not from the current intended run
- CI or manual commands may run in the wrong order
- no-config and config-enabled summary paths may be confused

These risks should be reduced without printing generated bodies or weakening
privacy checks.

## 4. Marker Design Options

### Option A: `summary.completed.json`

Write a small JSON marker after summary generation finishes.

Benefits:

- easy to understand
- clearly communicates completion
- can contain safe count-only metadata

Limits:

- name focuses on completion but less on run identity
- needs atomic writing too

### Option B: `summary.manifest.json`

Write a small JSON manifest with run identity, completion status, output path,
and count-only totals.

Benefits:

- can support run-id consistency checks
- can support case-count and diagnostic-count comparisons
- leaves room for a schema version
- still safe if fields are count-only

Limits:

- slightly broader than a simple completion marker
- requires careful field review

### Option C: `summary.run_id`

Write a small text file containing only the run id.

Benefits:

- very small
- low risk of accidentally becoming a report

Limits:

- cannot carry case counts or completion metadata by itself
- downstream checks need other sources for validation

### Option D: Status Row Inside `summary.csv`

Add a status row to the CSV itself.

Benefits:

- one file to read
- no separate marker path

Limits:

- changes summary CSV semantics
- may confuse row-count logic
- risks mixing metadata with case rows
- not recommended for the initial design

### Option E: Wrapper-Only Approach

Use a wrapper script that runs summary generation and distribution checking in
sequence.

Benefits:

- simple manual and CI entry point
- reduces ordering mistakes

Limits:

- does not prove that files are fresh outside the wrapper
- does not record run identity
- still benefits from a marker or manifest

## 5. Recommended Direction

Recommended initial direction:

- use `summary.manifest.json` as the primary future design, or
  `summary.completed.json` if a smaller marker is preferred
- write the marker at the end of summary generation, after `summary.csv` has
  been renamed into place
- write the marker through a temporary file and rename it atomically
- keep marker fields limited to safe count-only metadata
- keep marker support no-config only
- let the diagnostic distribution check optionally verify the marker at first,
  then consider making it required in a later hardening step

The recommended first marker shape is a manifest rather than an in-CSV status
row because it preserves the existing `summary.csv` case-row schema.

The initial marker file is now created by the no-config summary script on a
successful run. Distribution-check marker validation is still future work.

## 6. Marker: Allowed Information

Allowed marker fields:

- `run_id`
- `completed_at`
- `summary_path`
- `case_count`
- `diagnostic_summary_count`
- `content_suppressed=true`
- `no_config_summary=true`
- `generator_script`
- `summary_schema_version`, if useful

The marker should remain small, safe, and count-only.

## 7. Marker: Forbidden Information

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

The marker must not become a generated report body in disguise.

## 8. Future Distribution Check Integration

Future integration should follow these boundaries:

- the check reads only the final no-config `summary.csv`
- the check may require a marker after a transition period
- the check may compare marker `case_count` with the summary row count
- the check may reject a stale marker when staleness is detectable
- the check must not treat marker fields as performance evidence
- the check continues to reject config-enabled summary paths
- `no_cases` remains a failure
- output remains count-only

If marker verification fails, the result should be a precondition failure, not
a silent pass.

## 9. Failure And Rollback Policy

Future marker implementation should fail closed for:

- marker missing, if marker is required
- marker malformed
- marker status incomplete
- marker case count and summary row count mismatch
- marker containing forbidden body-like content
- marker pointing at a config-enabled summary path

Rollback expectations:

- marker implementation must not break the existing `summary.csv` schema
- marker implementation must not change no-config scoring output
- marker implementation must not require config-enabled summary output
- if marker checks are too strict, the project can temporarily return to
  precondition-only checking while keeping atomic summary writes

## 10. Future Hardening Tests

Future implementation should add safe smoke checks for:

- marker present pass
- marker missing fail
- marker malformed fail
- marker incomplete fail
- case-count mismatch fail
- stale marker fail if detectable
- final summary exists but marker is missing
- marker contains only safe metadata
- config-enabled path rejected
- safe stdout only

These tests should not print marker bodies, summary bodies, or generated rows.

## 11. Output Safety, Privacy, And No-Oracle Policy

The marker and related checks must preserve:

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

The marker is not training data, not evaluation evidence, and not a scoring
feedback mechanism.

## 12. Beginner Explanation

### What Is A Completion Marker?

A completion marker is a small file that says a summary run finished.

It helps another script avoid guessing whether `summary.csv` is current and
complete.

### What Is A Run ID?

A run id is a small identifier for one execution of the summary generator.

It can help connect a summary file and its safe metadata without exposing
generated content.

### Why Is `summary.csv` Alone Sometimes Not Enough?

Atomic rename keeps `summary.csv` from being half-written, but an old complete
summary can still remain while a new run is being generated.

A marker or manifest can help future checks distinguish completed run metadata
from stale output.

### Why Not Put Bodies In The Marker?

The marker should only prove completion and count-level consistency.

Raw bodies can contain content that should not appear in docs, stdout, or
public-safe summaries.

### Why Is This Not Performance Evaluation?

The marker does not measure model quality. It only helps scripts check whether
summary generation completed in a safe and orderly way.

## 13. Related Documents

- [Synthetic E2E summary atomic write design](synthetic_e2e_summary_atomic_write_design.md)
- [Synthetic diagnostic distribution marker validation design](synthetic_diagnostic_distribution_marker_validation_design.md)
- [Synthetic diagnostic distribution check ordering design](synthetic_diagnostic_distribution_check_ordering_design.md)
- [Synthetic diagnostic distribution review plan](synthetic_diagnostic_distribution_review_plan.md)
- [Synthetic E2E pipeline](synthetic_e2e_pipeline.md)
- [Public release checklist](public_release_checklist.md)
