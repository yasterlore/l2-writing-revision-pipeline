# Config-Enabled Summary Collector Design

This document designs and records the separate summary collector for explicit
config-enabled synthetic E2E outputs.

The implementation is intentionally separate from
`scripts/run_synthetic_e2e_summary.sh`. It does not change default summary
collector behavior, does not add config columns to the no-config summary CSV,
does not change default weights, does not change the scoring formula, does not
change deterministic tie-break behavior, and does not add F1, accuracy,
calibration, or learner-state estimation.

This is not performance evaluation.

## 1. Purpose

The purpose of this design is to define a safe boundary before any future
config-enabled summary collector is implemented.

The design goals are:

- summarize config-enabled synthetic E2E output only when explicitly requested
- keep no-config summary and config-enabled summary separate
- preserve default `run_synthetic_e2e_summary.sh` behavior
- prevent config-enabled rows from being mistaken for default E2E rows
- keep output count-only and free of raw JSONL bodies
- avoid performance claims from synthetic config-enabled summaries

Config-enabled summary output, if implemented later, should be a wiring and
regression diagnostic. It must not be treated as model performance, accuracy,
ranking quality, calibration, grammatical correctness, or learner-state
estimation.

## 2. Current State

Current state after Step 83:

- `scripts/run_synthetic_e2e_summary.sh` remains no-config.
- `scripts/run_synthetic_e2e_pipeline.sh` accepts `--weight-config` only when
  explicitly supplied.
- `scripts/check_config_enabled_e2e_smoke.sh` verifies explicit config-enabled
  E2E output separation and fail-closed behavior.
- `scripts/run_synthetic_e2e_config_summary.sh` writes a separate config-enabled
  count-only summary when `--weight-config` is explicitly supplied.
- `scripts/check_config_enabled_summary_smoke.sh` verifies the separate summary
  path, required safe columns, content suppression, expected failure cases, and
  no-config summary column separation.
- `scripts/check_explicit_config_ranking_diff.sh` compares no-config and
  explicit-config scoring outputs using safe diff summaries.
- `scripts/check_no_config_scoring_fixture_lock.sh` protects no-config scoring
  output for selected synthetic cases.
- no summary collector auto-discovers config, reads config from environment
  variables, or mixes config-enabled rows into the default summary CSV.

## 3. Summary Collector Design Options

### Option A: Separate CSV

Example output:

```text
tmp/synthetic_e2e_config_summary/summary.csv
```

Advantages:

- keeps default `tmp/synthetic_e2e_summary/summary.csv` unchanged
- makes config-enabled summary opt-in and visually separate
- reduces risk of comparing no-config and config-enabled counts as if they were
  the same run type

Risks:

- a single CSV may still mix different configs unless config metadata columns
  are required
- users must know which config produced the file

### Option B: Separate Directory Per Config

Example output:

```text
tmp/synthetic_e2e_config_summary/<config_name>/summary.csv
```

Advantages:

- keeps no-config summary unchanged
- separates config-enabled output from no-config output
- separates one config from another config
- makes repeated smoke runs easier to inspect without mixing config policies

Risks:

- requires a safe `config_name` normalization policy
- needs tests to prevent private/manual/real path leakage through directory
  names

### Option C: Add Config Columns To The Existing Summary CSV

Example:

```text
tmp/synthetic_e2e_summary/summary.csv
```

with extra config columns.

This is not recommended for the initial implementation.

Risks:

- changes default no-config summary columns
- makes config-enabled and no-config rows easier to mix accidentally
- increases the chance that downstream tooling treats config-enabled rows as
  default rows
- requires broader review of no-config summary compatibility

## 4. Recommended Policy

Initial config-enabled summary support should use Option B: a separate
directory per config.

Implemented output shape:

```text
tmp/synthetic_e2e_config_summary/<safe_config_name>/summary.csv
```

Policy:

- keep `tmp/synthetic_e2e_summary/summary.csv` unchanged
- require explicit config path input
- validate config before running config-enabled E2E
- derive `<safe_config_name>` from the config file basename
- normalize config summary directories to safe path components
- do not include config JSON body in the summary
- do not include raw JSONL bodies in the summary
- keep config-enabled summary count-only
- keep config-enabled summary separate from no-config summary
- run per-case pipeline output under config-suffixed case names in
  `tmp/synthetic_e2e/`, so no-config case directories are not overwritten

The initial config-enabled summary should not add performance metrics. It may
record safe config metadata and count-only E2E/diagnostic status fields.

Example:

```bash
scripts/run_synthetic_e2e_config_summary.sh \
  --weight-config tests/fixtures/synthetic/hand_weight_configs/valid/current_default_like_config.json
```

This writes:

```text
tmp/synthetic_e2e_config_summary/current_default_like_config/summary.csv
```

The script validates the config before running cases. Invalid, missing, or
unsafe config paths fail closed before per-case pipelines are started.

The smoke check for this collector is:

```bash
scripts/check_config_enabled_summary_smoke.sh
```

It runs the collector with a synthetic current-default-like config, checks that
`tmp/synthetic_e2e_config_summary/current_default_like_config/summary.csv`
exists, verifies required count-only columns, checks expected failures for
missing/invalid/unsafe config inputs, and confirms the no-config summary has no
config columns.

## 5. Information Allowed In Config-Enabled Summary

Allowed fields may include:

- `case_name`
- `config_summary_status`
- `config_name`
- `config_schema_version`
- `weight_config_path_basename` or another safe path summary
- `pipeline_status`
- `failed_stage`
- `output_dir`
- `score_sets_count`
- `candidates_count`
- `blocked_candidates_count`
- `unblocked_candidates_count`
- `rank1_available`
- `diagnostic_summary_status`
- safe count-only diagnostic fields
- `ranking_diff_status`, if generated separately
- ranking diff category counts, if generated separately
- `content_suppressed`

If `weight_config_path` is included, prefer a basename or other safe summary.
Do not include private/manual/real path values.

## 6. Information Not Allowed In Config-Enabled Summary

Do not include:

- config JSON body
- raw JSONL body
- raw text
- raw `local_context_before`
- `local_context_after_observed`
- `final_text`
- `observed_after_text`
- `gold_label`
- teacher or human correction
- expected action details
- evaluation report body
- candidate score rows
- proposed edit payload
- candidate description text
- real participant identifiers
- private/manual/real paths

Expected actions remain evaluation-only. They must not be used as config
selection, config tuning, or scoring feedback.

## 7. Default Summary Unchanged Policy

The default summary collector must remain unchanged.

Policy:

- `scripts/run_synthetic_e2e_summary.sh` remains no-config
- default summary columns remain unchanged unless separately reviewed
- config-enabled summary must not overwrite `tmp/synthetic_e2e_summary/summary.csv`
- config-enabled summary must not write into the default summary directory
- no implicit config discovery
- no environment variable config loading
- no hidden config
- no silent fallback from config-enabled summary to no-config summary

The default no-config summary remains the public synthetic wiring check.

## 8. Failure Policy

Config-enabled summary must fail closed.

Failure cases:

- missing config path
- unreadable config path
- malformed config JSON
- invalid config schema
- unsafe config path
- private/manual/real path-like string in config
- expected-action tuning policy
- unknown active constraint
- config-enabled E2E failure
- diagnostic summary failure
- ranking diff summary failure, if ranking diff is requested

Failure behavior:

- do not silently fall back to no-config summary
- do not overwrite no-config summary
- do not emit config body
- do not print JSONL bodies
- print safe error categories only
- write partial config-enabled output only under `tmp/` and mark failure clearly

## 9. Tests Required Before Implementation

Before implementing config-enabled summary support, tests should cover:

- no-config summary collector unchanged
- no-config summary columns unchanged
- config-enabled summary writes to a separate output directory
- config-enabled summary does not overwrite no-config summary
- invalid config fails closed
- unsafe config path fails
- config body absent from stdout and summary files
- JSONL body absent from stdout and summary files
- raw text absent
- safe stdout only
- `scripts/check_config_enabled_e2e_smoke.sh` still passes
- `scripts/check_no_config_scoring_fixture_lock.sh` still passes
- `scripts/check_explicit_config_ranking_diff.sh` still passes
- no F1, accuracy, calibration, or learner-state metrics are introduced

These tests are regression and wiring checks, not performance evaluation.

## 10. What Not To Do Yet

Do not implement in this collector:

- default summary changes
- config columns in no-config summary
- implicit config loading
- environment-variable config loading
- hidden config
- default weight changes
- scoring formula changes
- deterministic tie-break changes
- expected-action fitting
- F1, accuracy, calibration, or learner-state estimation
- real-data tuning
- real gold label workflow
- performance claims

Do not paste JSONL contents, config bodies, diagnostic report bodies,
evaluation report bodies, score rows, or private output into docs.

## 11. Future Roadmap

### Step 82: Implement Separate Config-Enabled Summary Collector

Completed: `scripts/run_synthetic_e2e_config_summary.sh` writes a separate
count-only summary under
`tmp/synthetic_e2e_config_summary/<safe_config_name>/summary.csv`.

### Step 83: Config-Enabled Summary Smoke Check

Completed: `scripts/check_config_enabled_summary_smoke.sh` proves
config-enabled summary output is separate, count-only, has required safe
columns, and does not add config columns to the no-config summary.

### Step 84: Config-Enabled Observation Note Template

Completed: `templates/config_enabled_observation_note_template.md` provides a
count-only observation note template for reviewing config-enabled synthetic
summaries without treating them as performance metrics.
For note storage and sharing policy, see
[Observation note storage and review workflow](observation_note_storage_and_review_workflow.md).

### Later: Private Validation Design

Private validation remains separate and must not be implemented inside the
public repository.

## 12. Related Documents

- [Synthetic E2E pipeline](synthetic_e2e_pipeline.md)
- [Config-enabled E2E design](config_enabled_e2e_design.md)
- [Explicit config ranking diff plan](explicit_config_ranking_diff_plan.md)
- [Diagnostic summary tooling plan](diagnostic_summary_tooling_plan.md)
- [Synthetic diagnostic distribution review plan](synthetic_diagnostic_distribution_review_plan.md)
- [Default-unchanged config support design](default_unchanged_config_support_design.md)
- [Config-enabled observation note template](templates/config_enabled_observation_note_template.md)
- [Observation note storage and review workflow](observation_note_storage_and_review_workflow.md)
