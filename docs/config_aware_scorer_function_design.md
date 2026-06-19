# Config-Aware Scorer Function Design

This document designs how a config-aware scorer function can be kept separate
without changing the current no-config default scoring path.

Status after Step 73: `python/ot_scorer/scorer.py` includes
`score_constraint_violation_set_with_config(violation_set, config)`. This
function is explicit-only and is not connected to `score.py`, the synthetic E2E
pipeline, or the summary collector. It does not change default weights, the
default scoring formula, deterministic tie-break behavior, evaluation metrics,
or learner-state estimation.

Status after Step 74: config-aware scorer unit tests cover default snapshot
stability, default-like config equivalence, explicit active weight behavior,
unchanged tie-break behavior, unchanged blocking behavior, inactive weight
handling, validator rejection before scoring, unchanged output schema, and
forbidden-field absence. No CLI or E2E config connection was added.

Status after Step 76: `score.py` has an explicit `--weight-config <path>`
option that calls the config-aware scorer only after strict validation. No-config
scoring remains the default, and the synthetic E2E pipeline and summary
collector remain no-config.

This is not performance evaluation.

## 1. Purpose

The purpose of this design is to separate two scoring paths:

- the existing default scorer path
- a future explicit config-aware scorer path

The config-aware function should be used only when it is called explicitly with
a validated hand-weight config. No-config default behavior must remain
unchanged.

This separation is intended to protect the current prototype behavior while
allowing future synthetic-only experiments with hand-designed weights. A ranking
change from a config-aware path would be an intentional behavior check, not a
performance claim.

## 2. Current Scorer State

Current state:

- `python/ot_scorer/scorer.py` holds current default scoring behavior
  internally.
- `python/ot_scorer/score.py` has explicit `--weight-config`; no-config remains
  the default.
- `python/ot_scorer/weight_config.py` is validation-only.
- `python/ot_scorer/validate_weight_config.py` is validation-only.
- no-config scoring fixture lock checks exist for synthetic cases.
- hand-weight config validation smoke checks exist.
- current default scoring is safety blocking plus deterministic tie-break.
- current default `CandidateScoreSet` output does not contain config metadata.

This document assumes those facts stay true until a separate approved
implementation step changes them.

## 3. Function Design

Do not replace the existing scorer function.

The implemented minimal function is separate from the default path:

```text
score_constraint_violation_set_with_config(violation_set, config)
```

Alternative design:

```text
score_constraint_violation_set(violation_set, weight_policy=None)
```

If the second shape is chosen, `weight_policy=None` must be exactly identical to
current behavior. However, the separate-function design is preferred because it
makes the default path harder to change accidentally.

Boundary:

- keep the existing default scorer function unchanged
- use the config-aware function only when it is called directly
- require a validated config object as an argument in tests or future explicit
  callers
- avoid any implicit file loading inside scorer logic

## 4. Config-Aware Function Inputs

The config-aware function accepts:

- a `ConstraintViolationSet`
- a validated `HandWeightConfig` object
- optional config metadata that has already passed validation

It must not accept or use:

- synthetic expected action
- evaluation result
- exact match result
- `final_text`
- `observed_after_text`
- `gold_label`
- teacher or human correction
- post-hoc annotation
- future edit or future context
- real participant data

Expected actions remain evaluation-only. They must not flow into scoring or
weight selection.

## 5. Config-Aware Function Outputs

The config-aware function outputs a `CandidateScoreSet`.

If config-enabled output needs metadata, such as `config_name` or
`config_schema_version`, that should be handled carefully as one of:

- a separate config-enabled schema version
- optional metadata only on the explicit config-aware output path
- an external sidecar summary that does not alter default output

The default no-config output schema must not change.

No score output should include:

- raw text
- raw `local_context_before`
- `local_context_after_observed`
- candidate description text
- proposed edit payload
- expected action details
- evaluation report details
- real participant identifiers

## 6. Default Unchanged Strategy

Default unchanged means:

- no-config scoring still calls the existing default path
- the default path does not import, read, or load config automatically
- there is no implicit config discovery
- there is no environment-variable config auto-loading
- there is no hidden default config file
- there is no config metadata in default output
- rank order remains the same
- `weighted_score` values remain the same
- `blocked` status remains the same
- blocking reasons remain the same
- deterministic tie-break remains the same
- default `CandidateScoreSet` schema remains the same
- no-config fixture lock passes before and after the new function is added

If a future caller cannot prove those conditions, config-aware scoring
should not be connected.

## 7. Validation And Failure Policy

Config validation must happen before config-aware scoring.

Failure policy:

- invalid config fails closed
- unknown active constraints fail closed
- missing rationale for active weights fails closed
- missing no-oracle-safe reason for active weights fails closed
- duplicate constraint entries fail closed
- non-finite weights fail closed
- forbidden fields fail closed
- private/manual/real data paths fail closed
- expected-action tuning language fails closed

The scorer should receive only a validated config object, not a raw config file
path or raw config JSON body.

## 8. Tests Required Before Implementation

Before connecting the config-aware function to any CLI or pipeline path, tests
should continue to cover:

- default scorer output unchanged
- no-config fixture lock passes
- config-aware function requires a validated config object
- invalid config cannot reach scoring
- explicit config changes only intended weights
- inactive config weights are ignored
- config-aware tie-break matches the default tie-break policy
- config-aware blocking behavior keeps blocked candidates behind unblocked ones
- ranking diff summary is safe and count-only
- default output schema unchanged
- config metadata absent from default output
- raw text absent from all scoring outputs
- forbidden fields absent from all scoring outputs
- expected action not used
- evaluation result not used
- synthetic E2E smoke still passes
- hand-weight config validation smoke still passes

These tests would be regression and behavior-boundary tests, not performance
metrics.

## 9. What Not To Do Yet

Do not implement:

- scorer config connection
- `score.py` config option
- config-aware CLI behavior
- default weight changes
- scoring formula changes
- tie-break policy changes
- hidden config loading
- config auto-loading
- environment-variable config loading
- expected-action tuning
- diagnostic-summary-count weight generation
- F1, accuracy, calibration, or learner-state estimation
- real-data tuning
- real gold label workflow
- publication-level performance claims

Do not paste JSONL contents, config bodies, diagnostic report bodies, or score
rows into docs.

## 10. Future Roadmap

### Step 73: Implement Config-Aware Scorer Function Without Default Path Change

Implemented as a separate function. It is not connected to the default scorer
path, CLI, synthetic E2E pipeline, or summary collector.

### Step 74: Config-Aware Scorer Unit Tests

Implemented additional tests for default unchanged behavior, validated-config
requirements, inactive weight handling, output schema stability, and intentional
synthetic-only config effects.

### Step 75: Explicit CLI Option Design

Design a `score.py` explicit config option separately. Do not add implicit
config loading. See
[Explicit config CLI option design](explicit_config_cli_option_design.md).

### Step 76: Implement Explicit `score.py --weight-config` Option

Implemented with no-config default behavior unchanged.

### Step 77: Explicit Config Ranking Diff Smoke Script

If approved, add a synthetic-only ranking diff smoke script that reports safe
summary categories only.

### Later: Private Validation Design

Private validation remains a separate later design step and must not be
implemented inside the public repository.

## 11. Related Documents

- [Explicit config ranking diff plan](explicit_config_ranking_diff_plan.md)
- [Explicit config CLI option design](explicit_config_cli_option_design.md)
- [Default-unchanged config support design](default_unchanged_config_support_design.md)
- [No-config scoring fixture lock plan](no_config_scoring_fixture_lock_plan.md)
- [Hand-weight config schema plan](hand_weight_config_schema_plan.md)
- [Hand-weight policy design](hand_weight_policy_design.md)
