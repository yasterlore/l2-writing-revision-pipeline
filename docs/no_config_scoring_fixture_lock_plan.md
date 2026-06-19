# No-Config Scoring Fixture Lock Plan

This document designs and documents the fixture-lock check for no-config
scoring output.

Status after Step 69: `python/ot_scorer/score_fixture_lock.py` and
`scripts/check_no_config_scoring_fixture_lock.sh` implement the synthetic
no-config score fixture lock. They do not connect config support to the scorer,
add a `score.py` config option, change default weights, change the scoring
formula, change deterministic tie-break behavior, add evaluation metrics, or
implement learner-state estimation.

The goal is to protect current default scoring behavior before any future
config support is connected to scoring.

## 1. Purpose

The fixture lock makes no-config scoring output stable.

If config support is added later, the lock should verify that running the
scorer without a config still produces the same `CandidateScoreSet` JSONL as
the locked synthetic fixture.

This lock is:

- a regression guard
- a default-behavior guard
- a schema stability guard
- synthetic-only

This lock is not:

- a performance metric
- a ranking correctness claim
- F1, accuracy, calibration, or learner-state estimation
- evidence that a candidate is grammatically correct

## 2. Lock Target

The lock target is no-config `CandidateScoreSet` JSONL produced from synthetic
inputs.

Fields and behavior to lock:

- `CandidateScoreSet` schema
- `candidate_id`
- `action_type`
- `generation_rule`
- `action_family`
- `weighted_score`
- `rank`
- `blocked`
- `block_reasons`
- constraint contribution behavior
- output schema fields

The lock must not add raw text to expected fixtures.

## 3. Information Allowed in Comparison

The lock check compares:

- `episode_id`
- `candidate_id`
- `action_type`
- `generation_rule`
- `action_family`
- `weighted_score`
- `blocked`
- `rank`
- `block_reasons`
- constraint contribution counts or summaries, if already present
- schema/version fields, if already part of score output
- candidate count per episode
- rank uniqueness per episode

These are no-oracle-safe scoring output fields and metadata.

## 4. Information Not Allowed in Comparison

The lock check must not compare, print, or introduce:

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
- candidate descriptions
- proposed edit payloads
- raw JSONL body in docs or stdout

Expected actions remain evaluation-only and must not be used as a lock target
for scoring behavior.

## 5. Initial Lock Fixture Candidates

Initial lock fixture candidates are synthetic only.

Recommended candidates:

- `deletion_case`
- `selection_edit_case`
- `cursor_movement_case`

The initial implemented lock starts with `deletion_case`, because it already
exercises the synthetic E2E scoring path and optional evaluation wiring.

More cases can be added after the lock script proves stable.

## 6. Lock Check Design

The script compares:

```text
expected CandidateScoreSet JSONL fixture
generated no-config CandidateScoreSet JSONL
```

Implemented design requirements:

- compare scorer output generated with no config
- normalize JSON objects before comparison
- preserve line and candidate order where rank/order is meaningful
- perform order-sensitive comparison for rank behavior
- perform schema-sensitive comparison for expected fields
- fail on missing expected fixture
- fail on generated output schema mismatch
- fail on `rank` mismatch
- fail on `weighted_score` mismatch
- fail on `blocked` or `block_reasons` mismatch
- print safe summary only
- never print raw JSONL bodies
- expect generated output under `tmp/` by default
- keep generated output Git ignored

Failure messages should name the failure category and safe counts only.

Failure summaries use safe count-only fields such as:

```text
lock_status=fail
reason=rank_mismatch
case_name=deletion_case
content_suppressed=true
```

Disallowed failure output:

- full expected JSONL line
- full generated JSONL line
- text snippets
- candidate description
- proposed edit content

## 7. Default Unchanged Judgment

Default unchanged means:

- no config is supplied
- no hidden config is loaded
- no environment variable config is loaded
- generated no-config score output matches the locked fixture
- output schema matches the locked fixture
- rank order matches the locked fixture
- `weighted_score` values match the locked fixture
- `blocked` state and reasons match the locked fixture

Explicit config behavior belongs in a separate test family. A config-enabled
ranking change must never be used to redefine the no-config lock.

## 8. Test Plan for Implementation

Tests cover or require coverage for:

- generated no-config scores equal the expected fixture
- missing expected fixture fails clearly
- malformed expected fixture fails clearly
- schema mismatch fails
- rank mismatch fails
- `weighted_score` mismatch fails
- blocked status mismatch fails
- raw text is absent from expected fixture and generated output
- config fields are absent in default output
- scorer does not auto-load config
- scorer does not expose config auto-loading through this lock path
- synthetic E2E smoke still passes
- synthetic E2E summary collector remains unchanged
- failure output is safe summary only
- no F1, accuracy, calibration, or learner-state metrics are introduced

## 9. What Not To Do Yet

Do not implement in this lock step:

- scorer config connection
- config-aware scorer function
- `score.py` config option
- default weight changes
- scoring formula changes
- tie-break policy changes
- constraint generation changes
- diagnostic summary tool changes
- expected-action fitting
- performance claims
- real-data lock fixtures
- real gold label workflow

Do not paste JSONL contents into docs.

## 10. Future Roadmap

### Step 69: Implement No-Config Scoring Fixture Lock Script

Status: completed. The script compares generated no-config scores against the
locked synthetic `deletion_case` score fixture and prints safe summary only.

### Step 70: Explicit Config Ranking Diff Plan

Design how explicit config-enabled ranking differences should be reviewed
without changing the no-config lock.

### Step 71: Config-Aware Scorer Function, Defaults Unchanged

If approved, add a separate config-aware scorer function while preserving the
default path.

### Step 72: Explicit Config CLI Option, If Approved

If approved, expose config support only through an explicit CLI option.

No implicit config discovery, hidden default config, or environment-variable
auto-loading should be added.

## 11. Related Documents

- [Default-unchanged config support design](default_unchanged_config_support_design.md)
- [Hand-weight config schema plan](hand_weight_config_schema_plan.md)
- [Scoring policy refinement plan](scoring_policy_refinement_plan.md)
- [Score-target constraint family selection plan](score_target_constraint_family_selection_plan.md)
