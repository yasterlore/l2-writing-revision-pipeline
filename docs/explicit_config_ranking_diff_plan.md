# Explicit Config Ranking Diff Plan

This document designs how future explicit-config scoring behavior should be
reviewed without changing no-config default scoring.

It is a design document only. It does not connect config support to the scorer
CLI, add a `score.py` config option, change default weights, change the scoring
formula, change deterministic tie-break behavior, add evaluation metrics, or
implement learner-state estimation.

The goal is to check intentional ranking differences only when an explicit
config path is supplied.

## 1. Purpose

The purpose of this plan is to define a safe future ranking-diff check for
explicit config use.

The check should verify that:

- no-config default scoring still matches locked fixtures
- explicit config is validated before scoring
- ranking differences happen only on the explicit config-enabled path
- diff output is safe summary only
- ranking differences are treated as intentional behavior checks, not
  performance improvements

This is not weight tuning, F1, accuracy, calibration, grammatical correctness,
ranking-quality evaluation, or learner-state estimation.

## 2. Current Assumptions

Current state:

- `python/ot_scorer/weight_config.py` is validation-only.
- `python/ot_scorer/validate_weight_config.py` is validation-only.
- `python/ot_scorer/scorer.py` includes a separate explicit config-aware
  function, but the default scorer path is not connected to config.
- `python/ot_scorer/score.py` has no config option.
- no-config fixture lock covers:
  - `deletion_case`
  - `selection_edit_case`
  - `cursor_movement_case`
- current default scoring is safety blocking plus deterministic tie-break.
- current default `CandidateScoreSet` output does not contain config metadata.

This plan assumes those facts stay true until a separate approved
implementation step changes them.

## 3. Diff Targets

A future explicit-config ranking diff may compare no-config output with
config-enabled output for synthetic cases.

Allowed diff targets:

- `CandidateScoreSet` JSONL structure
- candidate ordering
- `rank`
- `weighted_score`
- `blocked`
- top candidate `action_type`
- `block_reasons`
- `candidate_id`
- `action_type`
- `generation_rule`
- `action_family`
- config metadata, if a future config-enabled output path adds it explicitly

The diff should be order-sensitive where rank and candidate order matter.

## 4. Information Not Allowed as Diff Targets

The diff must not compare, print, or depend on:

- raw text
- raw `local_context_before`
- `local_context_after_observed`
- `observed_after_text`
- `final_text`
- `gold_label`
- teacher or human correction
- expected action
- evaluation result
- exact match result
- real participant data
- candidate description text
- proposed edit payload
- diagnostic observation notes as optimization targets

Expected action remains evaluation-only. It must not be used as scoring
feedback or as the reason a config is accepted.

## 5. Explicit Config Diff Design Principles

Future explicit config diff tooling should follow these rules.

### Explicit Config Path Only

Config must be supplied by an explicit path.

Disallowed:

- implicit config discovery
- environment-variable auto loading
- hidden default config
- private/manual/real-data path config

### Validate Before Scoring

Config validation must run before config-enabled scoring.

Invalid config must fail closed:

- do not score
- do not silently fall back to default scoring
- do not emit partial config-enabled score output

### No-Config Lock First

Before any explicit config diff is considered, the no-config fixture lock must
pass.

The default no-config path must continue to match:

- `deletion_case`
- `selection_edit_case`
- `cursor_movement_case`

### Separate Config-Enabled Output

Config-enabled output should be treated separately from no-config output.

If future config-enabled score output includes `config_name`,
`config_schema_version`, or similar metadata, those fields should be documented
and tested only on the config-enabled path. They must not silently appear in
default no-config output.

### Safe Summary Only

Diff tooling should print count-only summary fields.

Allowed stdout examples:

```text
diff_status=ok
case_name=deletion_case
rank_changed_count=1
weighted_score_changed_count=2
top_candidate_changed=false
content_suppressed=true
performance_evaluation=false
```

Disallowed stdout:

- raw JSONL rows
- full score rows
- candidate descriptions
- proposed edit payloads
- raw local context
- expected action details
- evaluation report body

## 6. Diff Categories

Initial diff categories should be explicit and countable:

- `rank_changed`
- `weighted_score_changed`
- `top_candidate_changed`
- `blocked_status_changed`
- `blocking_reasons_changed`
- `schema_changed`
- `unexpected_candidate_added_or_removed`
- `config_metadata_changed`

Each category should be counted per case and summarized without printing the
full JSON rows.

## 7. Tests Required Before Implementation

Before explicit config ranking diff tooling is implemented, tests should cover:

- no-config lock still passes
- explicit config validates
- invalid config prevents scoring
- explicit config produces the intended synthetic score/rank diff
- no implicit config loading
- no environment-variable auto loading
- raw text absent from output
- forbidden fields absent from output
- config metadata absent from no-config output
- config metadata present only if intentionally added to config-enabled output
- safe stdout only
- synthetic E2E smoke still passes
- no F1, accuracy, calibration, or learner-state metrics are introduced
- no performance claim is made from synthetic diff behavior

## 8. Allowed Synthetic Test Config

A future synthetic test config may be allowed if it is:

- synthetic-only
- intentionally tiny
- designed only for ranking-diff smoke checks
- validated by the strict hand-weight config validator
- accompanied by a rationale
- free of expected-action tuning
- free of exact-match or evaluation-result tuning
- free of real participant data
- free of private/manual/real-data paths
- free of raw text patterns

The purpose of such a config is to prove the wiring can produce an intentional
diff when explicitly requested. It is not evidence of performance improvement.

## 9. What Not To Do Yet

Do not implement:

- scorer config connection
- config-aware scorer function
- `score.py` config option
- default weight changes
- default scoring formula changes
- default tie-break changes
- hidden config loading
- config auto-loading
- expected-action fitting
- diagnostic-summary-count weight generation
- F1, accuracy, calibration, or learner-state estimation
- real-data tuning
- real gold label workflow
- publication-level performance claims

Do not paste JSONL contents, config bodies, diagnostic report bodies, or score
rows into docs.

## 10. Future Roadmap

### Step 72: Config-Aware Scorer Function Design

Design a separate config-aware scorer path while keeping the default no-config
path unchanged. See
[Config-aware scorer function design](config_aware_scorer_function_design.md).

### Step 73: Implement Config-Aware Scorer Function Without Default Path Change

Implemented as a separate function that accepts a validated config but does not
alter default scoring.

### Step 74: Explicit CLI Option Design

Design an explicit CLI option such as `--weight-config`. Do not allow implicit
config discovery.

### Step 75: Explicit Config Ranking Diff Smoke Script

If approved, implement a synthetic-only script that compares no-config and
explicit-config outputs using safe summary-only diff categories.

### Later: Private Validation Design

Private validation design remains separate and must not be implemented inside
the public repository.

## 11. Related Documents

- [Default-unchanged config support design](default_unchanged_config_support_design.md)
- [No-config scoring fixture lock plan](no_config_scoring_fixture_lock_plan.md)
- [Config-aware scorer function design](config_aware_scorer_function_design.md)
- [Hand-weight config schema plan](hand_weight_config_schema_plan.md)
- [Hand-weight policy design](hand_weight_policy_design.md)
- [Score-target constraint family selection plan](score_target_constraint_family_selection_plan.md)
