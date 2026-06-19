# Config-Enabled E2E Design

This document records the safety design for the optional config-enabled
synthetic E2E path.

Status after Step 80: `scripts/run_synthetic_e2e_pipeline.sh` supports an
optional explicit `--weight-config <config.json>` argument, and
`scripts/check_config_enabled_e2e_smoke.sh` checks the explicit config-enabled
E2E wiring. The summary collector remains no-config. Default no-config E2E
behavior, default weights, the scoring formula, deterministic tie-break
behavior, F1, accuracy, calibration, and learner-state estimation are
unchanged.

This is not performance evaluation.

## 1. Purpose

The purpose of this design is to define a safe boundary before any future
config-enabled E2E implementation.

The design goals are:

- keep default synthetic E2E no-config
- allow config only when explicitly requested
- preserve existing E2E arguments and outputs when no config is supplied
- avoid implicit config discovery
- keep config-enabled outputs separate from no-config outputs
- avoid performance claims from synthetic config behavior

Config-enabled E2E, if implemented later, should be a wiring and regression
check. It must not be treated as model performance, accuracy, grammatical
correctness, calibration, or learner-state estimation.

## 2. Current State

Current state after Step 79:

- `python/ot_scorer/score.py` supports explicit `--weight-config <path>`.
- `scripts/run_synthetic_e2e_pipeline.sh` uses no-config scoring by default.
- `scripts/run_synthetic_e2e_pipeline.sh` can pass `--weight-config` only when
  the option is explicitly supplied.
- `scripts/check_config_enabled_e2e_smoke.sh` confirms no-config and
  config-enabled E2E outputs are written to separate case directories.
- `scripts/run_synthetic_e2e_summary.sh` still uses no-config scoring.
- `scripts/check_explicit_config_ranking_diff.sh` compares no-config and
  explicit-config score outputs outside the E2E pipeline.
- `scripts/check_no_config_scoring_fixture_lock.sh` locks no-config score
  behavior for selected synthetic cases.
- no-config synthetic E2E remains the default path.

No current E2E script auto-loads config, reads config from environment
variables, or writes config metadata into default `CandidateScoreSet` output.

## 3. E2E Config Option Proposal

Implemented option:

```text
scripts/run_synthetic_e2e_pipeline.sh <input_raw_events.jsonl> <case_name> [expected_actions.jsonl] [--weight-config <config.json>]
```

The E2E script uses a named `--weight-config` option rather than a bare fourth
positional argument.

Rationale:

- keeps existing positional meaning intact
- avoids ambiguity with optional `expected_actions.jsonl`
- matches the `score.py --weight-config` option name
- makes config use visually explicit in command history and CI logs
- allows future validation of option order without breaking old calls

Existing no-config calls must continue to work unchanged:

```bash
scripts/run_synthetic_e2e_pipeline.sh \
  tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl \
  deletion_case
```

Existing optional evaluation calls must also continue to work unchanged:

```bash
scripts/run_synthetic_e2e_pipeline.sh \
  tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl \
  deletion_case_with_eval \
  tests/fixtures/synthetic/expected_actions/valid/deletion_expected_actions.jsonl
```

Config-enabled calls require the explicit option:

```bash
scripts/run_synthetic_e2e_pipeline.sh \
  tests/fixtures/synthetic/raw_events/valid/deletion_case.jsonl \
  deletion_case_config_smoke \
  tests/fixtures/synthetic/expected_actions/valid/deletion_expected_actions.jsonl \
  --weight-config tests/fixtures/synthetic/hand_weight_configs/valid/current_default_like_config.json
```

The summary collector does not receive config. If summary support is needed
later, it should be designed as a separate step.

## 4. Default E2E Unchanged Policy

When no E2E weight config is supplied:

- pipeline behavior must remain exactly no-config
- `score.py` must be called without `--weight-config`
- output directory layout must remain unchanged
- `CandidateScoreSet` schema must remain unchanged
- no config metadata may appear in default E2E outputs
- default weights must remain unchanged
- default scoring formula must remain unchanged
- deterministic tie-break must remain unchanged
- no-config fixture lock must pass
- no implicit config discovery may happen
- no environment variable config loading may happen
- no hidden default config may be used

Default E2E is the public synthetic smoke path. Config-enabled E2E must not
silently replace it.

## 5. Config-Enabled E2E Output Policy

Config-enabled E2E output should be clearly separated from no-config output.

Recommended output strategy:

- require a distinct `case_name` for config-enabled runs
- write to `tmp/synthetic_e2e/<case_name>/` as usual
- do not overwrite the no-config case output directory
- document the config-enabled case name in the command or smoke script

Example:

```text
tmp/synthetic_e2e/deletion_case_config_smoke/
```

Config-enabled E2E keeps the existing `CandidateScoreSet` schema. It does not
add config metadata to score JSONL. If metadata is needed later, prefer a
separate safe metadata report or a separately designed schema version.

Do not output:

- config JSON body
- raw JSONL bodies
- raw text
- raw local context
- candidate description text
- proposed edit payload
- expected action details
- evaluation report body
- exact match result as a performance claim
- real participant identifiers

Stdout should remain stage-summary only.

## 6. Failure Policy

Config-enabled E2E must fail closed.

Failure cases:

- missing config path
- unreadable config path
- malformed config JSON
- invalid config schema
- unsafe config path
- private/manual/real path-like string in config
- expected-action tuning policy
- unknown active constraint
- duplicate constraint entry
- missing rationale for active weight
- non-finite weight

Failure behavior:

- fail before scoring when config validation fails
- do not silently fall back to no-config scoring
- do not emit config body
- do not print JSONL body
- print a safe error category only
- mark partial output clearly or clean it up in a separately documented policy

If partial outputs from earlier pipeline stages remain, they must stay under
`tmp/` and must not be committed.

## 7. Relationship To Summary Collector

The summary collector should remain no-config.

Current and near-future policy:

- do not pass config from `scripts/run_synthetic_e2e_summary.sh`
- do not auto-run config-enabled E2E in the collector
- do not add config-enabled summary columns yet
- do not mix no-config and config-enabled rows without a separate design

If config-enabled summary is added later, it should be a separate step and
decide whether to use:

- a separate CSV
- a separate summary directory
- explicit config columns
- separate case names

The default summary collector must remain a no-config synthetic wiring check.

## 8. Tests Required Before Further Implementation

Before extending config-enabled E2E further, tests should continue to cover:

- no-config E2E output unchanged
- no-config fixture lock passes
- existing optional evaluation third argument still works
- valid config E2E path produces output in a separate location
- invalid config prevents scoring
- unsafe config path is rejected
- config-enabled output does not overwrite no-config output
- `score.py --weight-config` is used only when explicitly requested
- no implicit config loading
- no environment variable config loading
- default `CandidateScoreSet` schema unchanged
- config body absent from stdout and outputs
- raw text absent
- safe stdout only
- summary collector unchanged
- explicit config ranking diff smoke still passes
- no F1, accuracy, calibration, or learner-state metrics are introduced

These tests should be treated as regression and wiring tests, not performance
evaluation.

## 9. What Not To Do Yet

Do not implement:

- E2E pipeline config connection
- summary collector config connection
- default E2E behavior changes
- config auto-loading
- environment-variable config loading
- hidden config
- default weight changes
- default tie-break changes
- expected-action fitting
- diagnostic-summary-count weight generation
- F1, accuracy, calibration, or learner-state estimation
- real-data tuning
- real gold label workflow

Do not paste JSONL contents, config bodies, diagnostic report bodies,
evaluation report bodies, or score rows into docs.

## 10. Future Roadmap

### Step 79: Implement Optional Explicit Config-Enabled E2E Path

Implemented as explicit `--weight-config <path>` support in the single-case
synthetic E2E script. No-config behavior remains the default.

### Step 80: Config-Enabled E2E Smoke Check

Implemented as `scripts/check_config_enabled_e2e_smoke.sh`. It runs no-config,
current-default-like config, and intentional synthetic config E2E cases with
separate case names, checks invalid and unsafe config failures, and confirms
the no-config output is not overwritten. It also calls the explicit config
ranking diff smoke for the intentional weighted-score diff check.

### Step 81: Config-Enabled Summary Collector Design

Design whether config-enabled summary should use a separate CSV, separate
directory, explicit columns, or remain outside the collector. See
[Config-enabled summary collector design](config_enabled_summary_collector_design.md).

### Step 82: Private Validation Design Later

Config-enabled summary and count-only observation notes are handled separately.
For the safe human-review template, see
[Config-enabled observation note template](templates/config_enabled_observation_note_template.md).
For storage and sharing policy, see
[Observation note storage and review workflow](observation_note_storage_and_review_workflow.md).

Private validation remains separate and must not be implemented inside the
public repository.

## 11. Related Documents

- [Synthetic E2E pipeline](synthetic_e2e_pipeline.md)
- [Explicit config CLI option design](explicit_config_cli_option_design.md)
- [Explicit config ranking diff plan](explicit_config_ranking_diff_plan.md)
- [Default-unchanged config support design](default_unchanged_config_support_design.md)
- [No-config scoring fixture lock plan](no_config_scoring_fixture_lock_plan.md)
- [Hand-weight config schema plan](hand_weight_config_schema_plan.md)
- [Config-enabled summary collector design](config_enabled_summary_collector_design.md)
- [Config-enabled observation note template](templates/config_enabled_observation_note_template.md)
- [Observation note storage and review workflow](observation_note_storage_and_review_workflow.md)
