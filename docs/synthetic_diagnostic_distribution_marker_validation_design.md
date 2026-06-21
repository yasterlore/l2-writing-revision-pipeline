# Synthetic Diagnostic Distribution Marker Validation Design

This document designs future marker validation for
`scripts/check_synthetic_diagnostic_distribution.sh`.

It records the marker validation design and the initial required-validation
implementation. It does not change tests, E2E summary generator logic, scorer
logic, scorer weights, scoring formula, deterministic tie-break behavior, or
fixtures.

This is not performance evaluation.

## 1. Purpose

The purpose of this design is to define how the no-config synthetic diagnostic
distribution check should validate `summary.manifest.json` before relying on
`summary.csv`.

The design focuses on:

- keeping the check no-config summary only
- confirming that marker metadata is safe and count-only
- reducing stale-summary and mixed-run ambiguity
- separating precondition failures from diagnostic distribution logic failures
- preserving output safety and no-oracle boundaries

Marker validation is a reliability check. It is not a model-quality signal.

## 1.1 Implementation Status

Step 114 implemented required marker validation in
`scripts/check_synthetic_diagnostic_distribution.sh`:

- `summary.manifest.json` is now a required no-config precondition
- missing, malformed, invalid, or body-like marker fields fail closed
- marker `case_count` must match the summary data-row count
- marker `manifest_schema_version` must be `1.0`
- marker keys must be allowed for `manifest_schema_version="1.0"`
- config-enabled summary paths remain rejected
- marker JSON body and summary CSV body are not printed

This implementation remains no-config only.

For future stricter manifest schema options, see
[Summary manifest schema hardening design](summary_manifest_schema_hardening_design.md).
For the implemented design on rejecting unknown manifest keys, see
[Summary manifest allowed-key validation design](summary_manifest_allowed_key_validation_design.md).
For future work on sharing manifest schema constants across scripts and docs,
see [Summary manifest schema centralization design](summary_manifest_schema_centralization_design.md).

## 2. Current State

Current state:

- `tmp/synthetic_e2e_summary/summary.csv` is written through
  `summary.csv.tmp` and final rename.
- `tmp/synthetic_e2e_summary/summary.manifest.json` is generated after a
  successful no-config summary run.
- The marker contains safe count-only metadata only.
- `scripts/check_synthetic_diagnostic_distribution.sh` requires and validates
  the marker before running distribution checks.
- Config-enabled summaries remain separate under
  `tmp/synthetic_e2e_config_summary`.

The current distribution check fails closed for missing, empty, malformed, and
no-case no-config summaries. Marker validation is now an additional
precondition layer.

## 3. Why Add Marker Validation

Marker validation should be introduced to:

- reduce the risk of checking an old complete `summary.csv`
- confirm that summary generation completed and wrote a safe marker
- compare marker case counts with summary data-row counts
- distinguish precondition failures from distribution count failures
- keep CI and manual runs easier to interpret

The goal is not to change diagnostic counts or evaluate model performance.

## 4. Validation Items

Current validation checks:

- marker file exists
- marker is valid JSON
- `manifest_schema_version` is `1.0`
- all manifest keys are allowed for version `1.0`
- `content_suppressed` is `true`
- `no_config_summary` is `true`
- `case_count` is an integer greater than 0
- `diagnostic_summary_count` is an integer greater than or equal to 0
- `summary_path` points to the expected no-config summary path
- `generator_script` is `scripts/run_synthetic_e2e_summary.sh`
- marker does not contain forbidden body-like keys
- marker `case_count` equals summary data-row count

The validation should not print the marker JSON body.

## 5. Missing Or Malformed Marker Handling

Current behavior fails closed:

- marker missing: precondition failure
- marker malformed: precondition failure
- marker says not no-config: precondition failure
- marker path points outside the no-config summary path: precondition failure
- marker `case_count` mismatch: precondition failure or investigate-only
  failure, depending on the implementation step
- marker contains forbidden body-like fields: fail closed

None of these cases should be treated as a silent pass.

Safe output should include only status, reason, safe path, and count-level
details.

## 6. Forbidden Marker Keys

The marker must not include keys such as:

- `raw_summary_body`
- `diagnostic_summary_body`
- `jsonl_body`
- `candidate_score_rows`
- `raw_text`
- `expected_action_details`
- `config_body`
- `final_text`
- `observed_after_text`
- `gold_label`
- `performance_metrics`
- `f1`
- `accuracy`
- `calibration`

This list is intentionally conservative. A marker should remain a small
completion and count metadata file, not a report body.

## 7. Migration Strategy

Migration phases:

1. Marker generated, not required. This is the current state.
2. Marker validation optional warning, if a transition period is useful.
3. Marker required fail-closed.

Step 114 moved directly to phase 3 because the no-config summary script now
generates the marker. The implementation remains safe, count-only, and
no-config only.

## 8. Output Safety Policy

Marker validation must not print:

- marker JSON body
- raw summary CSV body
- diagnostic summary JSON body
- JSONL body
- candidate score rows
- raw text
- expected action details
- config body

Allowed output:

- status label
- safe path
- safe reason
- case count
- summary data-row count
- marker validation status
- `content_suppressed=true`

Marker validation is not a performance report.

## 9. Future Tests

Implemented and future smoke coverage includes:

- marker present pass
- marker missing fail
- malformed marker fail
- `content_suppressed=false` fail
- `no_config_summary=false` fail
- `case_count=0` fail
- marker `case_count` and summary row-count mismatch fail
- forbidden body-like key fail
- config-enabled path rejected
- safe stdout only

Tests should not print marker bodies, summary bodies, JSONL rows, or generated
score rows.

## 10. Beginner Explanation

### What Is Marker Validation?

Marker validation means checking the small completion file before trusting the
summary file.

It asks: is the marker present, readable, safe, and consistent with the
summary?

### Why Is Having A Marker Not Enough?

A marker file can be missing, malformed, stale, or accidentally contain unsafe
fields.

Validation makes sure the marker is actually useful and safe.

### Why Check That The Marker Is JSON?

The checker needs to read the marker reliably. If the file is not valid JSON,
the script cannot safely interpret its fields.

### Why Check `case_count`?

`case_count` lets the checker compare the marker's count-only metadata with the
summary row count.

That can reveal stale or mismatched outputs without reading raw bodies.

### Why Not Print The Marker Body?

Even a marker should be treated as generated output. Debugging should use safe
status and count fields instead of dumping file contents.

## 11. Related Documents

- [Synthetic E2E summary completion marker design](synthetic_e2e_summary_completion_marker_design.md)
- [Summary manifest schema hardening design](summary_manifest_schema_hardening_design.md)
- [Summary manifest allowed-key validation design](summary_manifest_allowed_key_validation_design.md)
- [Summary manifest schema centralization design](summary_manifest_schema_centralization_design.md)
- [Synthetic diagnostic distribution check ordering design](synthetic_diagnostic_distribution_check_ordering_design.md)
- [Synthetic E2E summary atomic write design](synthetic_e2e_summary_atomic_write_design.md)
- [Synthetic diagnostic distribution review plan](synthetic_diagnostic_distribution_review_plan.md)
- [Public release checklist](public_release_checklist.md)
