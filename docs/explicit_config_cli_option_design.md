# Explicit Config CLI Option Design

This document designs the explicit config option for
`python/ot_scorer/score.py`.

Status after Step 76: `score.py` supports explicit `--weight-config <path>`.
No-config scoring remains the default. Config support is not connected to the
synthetic E2E pipeline or summary collector. This change does not alter default
weights, the default scoring formula, deterministic tie-break behavior,
evaluation metrics, or learner-state estimation.

This is not performance evaluation.

## 1. Purpose

The purpose of this design is to define a safe CLI boundary for explicit
`score.py` config use.

The design goals are:

- preserve the no-config default scoring path
- use the config-aware scorer function only when a config path is explicitly
  supplied
- validate config before scoring
- fail closed on invalid or unsafe config
- avoid performance claims from synthetic-only behavior checks

This design is not a weight change, ranking-quality claim, F1, accuracy,
calibration, grammatical-correctness check, or learner-state estimate.

## 2. Current State

Current state:

- `python/ot_scorer/score.py` has explicit `--weight-config`.
- `python/ot_scorer/scorer.py` has the existing default scorer path.
- `python/ot_scorer/scorer.py` also has
  `score_constraint_violation_set_with_config(violation_set, config)`.
- `python/ot_scorer/weight_config.py` can strictly validate hand-weight config
  JSON.
- `python/ot_scorer/validate_weight_config.py` validates configs without
  scoring.
- no-config scoring fixture lock checks exist.
- config-aware scorer unit tests exist.
- synthetic E2E pipeline and summary collector do not pass config to scoring.

## 3. CLI Option

Implemented option name:

```text
--weight-config <path>
```

Rationale:

- it is explicit about weight policy rather than general configuration
- it matches the `HandWeightConfig` terminology
- it reduces confusion with unrelated runtime or pipeline config

Behavior:

- without `--weight-config`, `score.py` behaves exactly as it does now
- with `--weight-config`, `score.py` loads and validates the config first
- valid config calls the explicit config-aware scorer function
- invalid config prevents scoring
- config is never discovered implicitly

Alias policy:

- do not add `--config` initially
- if an alias is needed later, document why and test it separately

## 4. No-Config Default Unchanged Policy

When `--weight-config` is not supplied:

- `score.py` output must be exactly the current no-config output
- default `CandidateScoreSet` schema remains unchanged
- no config metadata appears in default output
- default weights remain unchanged
- default scoring formula remains unchanged
- default deterministic tie-break remains unchanged
- no config file is loaded
- no implicit config discovery happens
- no environment variable config loading happens
- no hidden default config is used
- no-config fixture lock must pass

The default path must not import or load config as a side effect.

## 5. Config-Specified Output Policy

When `--weight-config` is supplied, output policy needs special care.

Initial implementation should prefer keeping the `CandidateScoreSet` JSONL
schema unchanged. This avoids accidentally breaking downstream tools that read
candidate scores.

Allowed safe output locations for config metadata, if needed later:

- stdout safe summary only
- a separate metadata report file
- a future explicit config-enabled schema version, if separately designed

Do not include in `CandidateScoreSet` JSONL:

- config JSON body
- raw text
- raw local context
- candidate description text
- proposed edit payload
- expected action
- evaluation result
- exact match result
- real participant identifiers

Stdout should remain safe summary only.

## 6. Failure Policy

`--weight-config` handling fails closed.

Failure cases:

- missing config path
- unreadable config path
- malformed config JSON
- invalid config schema
- unsafe config path
- private/manual/real path string in config
- expected-action tuning policy
- unknown active constraint
- duplicate constraint entry
- missing rationale for active weight
- non-finite weight

Failure output should include:

- `validation_status=fail` or equivalent safe status
- safe error category
- no config body
- no score rows
- no JSONL body
- no raw text

Scoring must not start after config validation fails.

## 7. Tests Required Before Implementation

Tests should continue to cover:

- no-config `score.py` output equals current fixture behavior
- no-config fixture lock passes
- valid `--weight-config` invokes the config-aware scorer path
- invalid config prevents scoring
- missing config path fails clearly
- unsafe config path is rejected
- expected-action tuning config is rejected
- unknown active constraint is rejected
- no implicit config loading
- no environment variable config loading
- default output schema unchanged
- config-enabled output excludes raw text and forbidden fields
- stdout is safe summary only
- synthetic E2E pipeline unchanged unless explicitly extended later

These are behavior-boundary tests, not performance metrics.

## 8. Relationship To Synthetic E2E Pipeline

This design does not connect config to E2E.

Current policy:

- synthetic E2E pipeline remains no-config by default
- summary collector remains no-config by default
- config-enabled E2E, if added later, must be a separate explicit design step
- E2E config use must require an explicit argument
- E2E must not auto-discover config files

Expected actions remain evaluation-only and must not be passed to scoring or
used for weight tuning.

## 9. What Not To Do Yet

Do not implement:

- `score.py --config`
- E2E config connection
- summary collector config connection
- implicit config loading
- environment-variable config loading
- hidden default config
- default weight changes
- scoring formula changes
- tie-break changes
- expected-action fitting
- diagnostic-summary-count weight generation
- F1, accuracy, calibration, or learner-state estimation
- real-data tuning
- real gold label workflow

Do not paste JSONL contents, config bodies, diagnostic report bodies, or score
rows into docs.

## 10. Future Roadmap

### Step 76: Implement Explicit `score.py --weight-config` Option

Implemented with no-config default behavior unchanged.

### Step 77: Explicit Config Ranking Diff Smoke Script

Implemented as `scripts/check_explicit_config_ranking_diff.sh`. It compares
no-config and explicit-config outputs using safe summary-only diff categories.
It is not connected to the E2E pipeline or summary collector.

### Step 78: Config-Enabled E2E Design

Design optional config-enabled E2E wiring separately. It must be explicit-only
and no-config by default.

### Later: Private Validation Design

Private validation remains separate and must not be implemented inside the
public repository.

## 11. Related Documents

- [Config-aware scorer function design](config_aware_scorer_function_design.md)
- [Explicit config ranking diff plan](explicit_config_ranking_diff_plan.md)
- [Default-unchanged config support design](default_unchanged_config_support_design.md)
- [Hand-weight config schema plan](hand_weight_config_schema_plan.md)
- [No-config scoring fixture lock plan](no_config_scoring_fixture_lock_plan.md)
