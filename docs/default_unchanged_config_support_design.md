# Default-Unchanged Config Support Design

This document defines a safe design boundary for any future connection between
hand-weight config files and the OT-style scorer.

It is a design document only. It does not connect config support to scoring,
add a `score.py` config option, change default weights, change the scoring
formula, change deterministic tie-break behavior, add evaluation metrics, or
implement learner-state estimation.

The main rule is simple: adding config support later must not change default
scoring behavior when no config is explicitly provided.

## 1. Purpose

The purpose of this design is to make future config support safe before it is
connected to the scorer.

The design priorities are:

- keep default behavior unchanged
- allow scoring changes only when an explicit config is supplied
- avoid hidden config discovery
- fail closed on invalid config
- keep no-oracle and privacy boundaries visible
- avoid any performance claim from synthetic-only checks

This is not weight tuning, scoring change, model evaluation, F1, accuracy,
calibration, ranking-quality analysis, or learner-state estimation.

## 2. Current State

Current config-related state:

- `python/ot_scorer/weight_config.py` defines schema models and strict
  validation helpers.
- `python/ot_scorer/validate_weight_config.py` validates config JSON files only.
- `scripts/check_hand_weight_config_validation.sh` smoke-checks valid and
  invalid synthetic config fixtures.
- `python/ot_scorer/scorer.py` has a separate config-aware function, but the
  default scorer path remains no-config.
- `python/ot_scorer/score.py` exposes an explicit `--weight-config` option, but
  no-config scoring remains the default path.
- `CandidateScoreSet` output does not include config fields.

Current default scoring behavior:

- safety blocking constraints remain active
- descriptive constraints remain score-neutral
- `weighted_score(c) = sum_i w_i * v_i(c)`
- blocking constraints use the current safety weight
- deterministic tie-break remains hold, local edit, grammar placeholder, other
  placeholder, then other

## 3. Definition of Default Unchanged

Default unchanged means that when no config is supplied, scoring produces the
same results as the current prototype.

The following must remain identical for no-config execution:

- `CandidateScoreSet` records
- candidate order within each episode
- `rank`
- `weighted_score`
- `blocked`
- `block_reasons`
- constraint contribution behavior
- tie-break behavior
- output schema
- synthetic E2E pipeline behavior
- synthetic E2E summary collector behavior

If config support is implemented later, tests must compare no-config output
against current expected behavior before any config-enabled path is accepted.
The planned fixture-lock approach is described in
[No-config scoring fixture lock plan](no_config_scoring_fixture_lock_plan.md).

## 4. Future Config Connection Design Principles

Future config support, if approved, should follow these rules.

### Explicit Config Only

Config should affect scoring only when an explicit CLI option is provided.

Disallowed:

- implicit config discovery
- environment-variable auto loading
- hidden default config files
- automatic use of files under private or real-data paths

### Validate Before Scoring

Config validation must run before scoring.

Invalid config must fail closed:

- do not score with a partially loaded config
- do not fall back silently to defaults after a validation error
- do not produce mixed default/config-enabled output

### Default Output Remains Stable

No-config output should keep the same schema.

If config-enabled output later needs metadata such as `config_name` or
`config_schema_version`, that metadata must be introduced only for the
explicit config-enabled path or in a separately documented optional metadata
container. It must not silently change default `CandidateScoreSet` output.

### Config-Aware Code Path Is Separate

A future implementation should make the boundary easy to test:

- default scoring function remains available
- config-aware scoring path is called only from the explicit config option
- tests cover both paths separately
- no shared mutable global weight state is introduced

## 5. Prohibited Behavior

Do not add:

- silent default weight changes
- automatic config file search
- expected-action-derived config
- evaluation-result-derived config
- real participant data derived config
- config depending on `final_text`
- config depending on `observed_after_text`
- config depending on `gold_label`
- config depending on teacher or human correction
- automatic weight generation from diagnostic summary counts
- hidden learned weights
- per-participant weights
- undocumented tie-break changes
- private/manual/real-data paths in public config

## 6. Tests Required Before Implementation

Before config is connected to scoring, the following tests are required:

- no-config scoring equals current expected fixture behavior
- no-config synthetic E2E `candidate_scores.jsonl` behavior remains unchanged
- no-config output schema remains unchanged
- no-config score fixture lock passes
- invalid config prevents scoring
- forbidden fields are rejected
- expected-action tuning config is rejected
- private, manual, real, and participant-data paths are rejected
- explicit config changes ranking only when intended
- blocked candidate behavior remains documented and tested
- tie-break changes, if any, are separately documented and tested
- config-enabled output metadata, if added, is tested separately
- synthetic E2E smoke still passes
- no F1, accuracy, calibration, or learner-state metrics are introduced

## 7. Suggested Implementation Order

### Phase 0: Current State

Validation, a separate config-aware scorer function, and explicit
`score.py --weight-config` exist. No-config remains the default scoring path,
and the synthetic E2E pipeline and summary collector remain no-config.

### Phase 1: Explicit CLI Option Design

Designed and implemented as explicit `--weight-config`.

Before implementing the option, add a no-config scoring fixture lock so the
current default path is protected.
After the no-config lock is protected, explicit-config ranking diff behavior
should be designed separately. See
[Explicit config ranking diff plan](explicit_config_ranking_diff_plan.md).
Optional config-enabled E2E should also be designed separately and remain
explicit-only. See
[Config-enabled E2E design](config_enabled_e2e_design.md).

### Phase 2: Config-Aware Scorer Function

If approved later, add a separate config-aware function that does not replace
the default scoring path.

The default path must stay unchanged.

For the function-level boundary, read
[Config-aware scorer function design](config_aware_scorer_function_design.md).

### Phase 3: Explicit CLI Option

Connect the config-aware path only through an explicit CLI option.

Do not auto-load config from environment variables or repository paths.

For the CLI boundary, read
[Explicit config CLI option design](explicit_config_cli_option_design.md).

### Phase 4: Ranking Diff Smoke Tests

Add synthetic-only tests that show config-enabled ranking changes only when
intended.

These tests are behavior checks, not performance metrics.

### Phase 5: Synthetic-Only Rationale Examples

Add synthetic-only rationale examples if useful.

Do not use expected action, exact match, or diagnostic observation notes as
weight-fitting targets.

### Later: Private Validation Design

Private validation design remains a separate step and must not be implemented
inside the public repository.

## 8. No-Oracle and Privacy Policy

Future config support must remain no-oracle-safe.

Allowed config content:

- public, synthetic-only design information
- explicit constraint IDs and families
- documented hand-designed weights
- rationale text that does not include raw participant text
- no-oracle review notes

Disallowed config content:

- raw local context text
- raw text patterns
- `local_context_after_observed`
- `observed_after_text`
- `final_text`
- `gold_label`
- teacher or human correction
- expected action as scoring feedback
- real participant data
- private/manual/real data paths

Expected actions remain evaluation-only. They must not be used to tune weights
or generate config files.

## 9. What Not To Do Yet

Do not implement:

- E2E config connection
- summary collector config connection
- implicit config discovery
- environment-variable config loading
- default weight changes
- scoring formula changes
- tie-break policy changes
- constraint generation changes
- diagnostic summary tool changes
- F1, accuracy, calibration, or learner-state estimation
- production or real-data processing
- real gold label workflow

Do not paste JSONL contents, config bodies, diagnostic report bodies, real
participant text, or private output into documentation.

## 10. What To Read Next

- [Hand-weight config schema plan](hand_weight_config_schema_plan.md)
- [No-config scoring fixture lock plan](no_config_scoring_fixture_lock_plan.md)
- [Explicit config ranking diff plan](explicit_config_ranking_diff_plan.md)
- [Config-enabled E2E design](config_enabled_e2e_design.md)
- [Hand-weight policy design](hand_weight_policy_design.md)
- [Score-target constraint family selection plan](score_target_constraint_family_selection_plan.md)
- [Diagnostic-to-scoring boundary review](diagnostic_to_scoring_boundary_review.md)
- [Scoring policy refinement plan](scoring_policy_refinement_plan.md)
