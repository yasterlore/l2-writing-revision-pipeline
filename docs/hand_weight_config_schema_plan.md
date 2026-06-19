# Hand-Weight Config Schema Plan

This document designs a possible future configuration schema for
hand-designed scoring weights.

It is primarily a design plan. The repository now includes schema models,
strict validation helpers, and a validation-only CLI, but those pieces do not
change scoring weights, change the scoring formula, change deterministic
tie-break behavior, change constraint generation, add evaluation metrics, or
implement learner-state estimation.

Status after Step 66: Python schema models and a strict validation helper have
been added in `python/ot_scorer/weight_config.py`, and a validation-only CLI has
been added in `python/ot_scorer/validate_weight_config.py`. They are not
connected to the scorer, and default scoring behavior remains unchanged.

The schema described here is intended to make future hand-designed weights
explicit, interpretable, and auditable before any scoring behavior changes.

Before any config is connected to scoring, read
[Default-unchanged config support design](default_unchanged_config_support_design.md).
For the planned no-config regression guard, read
[No-config scoring fixture lock plan](no_config_scoring_fixture_lock_plan.md).
For the future explicit-config ranking diff boundary, read
[Explicit config ranking diff plan](explicit_config_ranking_diff_plan.md).
For the future explicit function boundary, read
[Config-aware scorer function design](config_aware_scorer_function_design.md).
For the Milestone 03 follow-up review of score-active family boundaries, read
[Score-active family selection revisit](score_active_family_selection_revisit.md).
For synthetic-only examples of rationale entries before actual config changes,
read [Synthetic hand-weight rationale examples](synthetic_hand_weight_rationale_examples.md).
For a possible future metadata completeness explicit-config experiment, read
[Metadata completeness explicit config experiment design](metadata_completeness_explicit_config_experiment_design.md).
For the possible fixture shape for that experiment, read
[Metadata completeness config fixture design](metadata_completeness_config_fixture_design.md).

## 1. Purpose

The purpose of a hand-weight config schema is to represent hand-designed
weights in a way that is:

- explicit
- interpretable
- reviewable
- testable
- no-oracle-safe
- privacy-conscious

The schema should avoid hidden weights and require a rationale for any active
non-default weight.

This document is a design step before default behavior changes. It is not a
performance evaluation and does not claim F1, accuracy, calibration,
grammatical correctness, ranking quality, or learner-state quality.

## 2. Information the Config Should Represent

A future config should represent top-level policy metadata and per-constraint
weight entries.

Recommended top-level fields:

- `config_schema_version`
- `config_name`
- `created_for`
- `default_behavior`
- `score_active_constraint_families`
- `constraint_weights`
- `blocking_constraints`
- `score_neutral_constraints`
- `rationale`
- `no_oracle_review`
- `synthetic_only_notice`
- `expected_action_usage_policy`
- `forbidden_information_policy`

### `config_schema_version`

Required string that identifies the config schema version.

Example:

```text
hand_weight_config_schema_v0_1
```

### `config_name`

Human-readable name for the config.

It should not imply production readiness or model performance.

### `created_for`

Short description of the intended design use.

Allowed examples:

- synthetic ranking behavior smoke check
- hand-weight design review
- no-oracle scoring policy prototype

Disallowed examples:

- real participant performance tuning
- final evaluation
- accuracy optimization

### `default_behavior`

Description of expected default behavior when no explicit config is provided.

The current default behavior is:

- safety blocking constraints remain active
- descriptive diagnostics remain score-neutral
- deterministic tie-break remains unchanged

### `score_active_constraint_families`

Explicit list of constraint families that the config intends to make
score-active.

This list should be short. Any active family needs a rationale.

### `constraint_weights`

List of per-constraint weight entries.

Each active weight must be explicit and reviewable.

### `blocking_constraints`

List of constraints that are blocking safety constraints.

Safety blocking must remain separate from ordinary linguistic preferences.

### `score_neutral_constraints`

List or family-level declaration of constraints that should remain
score-neutral.

This helps prevent accidental scoring of diagnostics.

### `rationale`

Top-level explanation for why the config exists.

It must state that weights are hand-designed, not learned.

### `no_oracle_review`

Structured statement of the no-oracle review status.

It should say which information is allowed and which information is forbidden.

### `synthetic_only_notice`

Required notice that public repository configs use synthetic design information
only.

### `expected_action_usage_policy`

Required policy statement that expected actions are evaluation-only and must
not be used for weight design or tuning.

### `forbidden_information_policy`

Required policy statement listing forbidden information such as final text,
post-edit text, gold labels, teacher corrections, raw text patterns, and real
participant data.

## 3. Constraint Weight Entry Schema Candidate

A future `constraint_weights` entry may include:

- `constraint_id`
- `constraint_family`
- `weight`
- `active`
- `rationale`
- `no_oracle_safe_reason`
- `expected_effect`
- `risk_note`
- `tests_required`
- `last_reviewed`

Example shape:

```text
constraint_id: NO-LEAKAGE-FLAG
constraint_family: safety_blocking
weight: 1000000.0
active: true
rationale: Blocks leakage-bearing candidates.
no_oracle_safe_reason: Uses leakage flags from no-oracle audit only.
expected_effect: Candidate is blocked when violation_count > 0.
risk_note: Must not be weakened without privacy review.
tests_required: blocking behavior unchanged
last_reviewed: YYYY-MM-DD
```

This is an illustrative shape, not an implementation format.

### Required Fields for Active Entries

If `active = true`, require:

- `constraint_id`
- `constraint_family`
- finite numeric `weight`
- `rationale`
- `no_oracle_safe_reason`
- `expected_effect`
- `risk_note`
- `tests_required`

### Optional Fields

Optional fields may include:

- `last_reviewed`
- `reviewer`
- `related_design_doc`

These optional fields must not contain private data or participant identifiers.

## 4. Default Behavior Policy

Creating a config schema must not change current default scoring.

Current default:

- safety blocking constraints are active
- descriptive constraints are score-neutral
- deterministic tie-break applies among equal unblocked candidates
- no config file is required

Future implementation policy:

- default scoring should remain unchanged when no config is provided
- initial config support should preserve current behavior by default
- only an explicitly supplied config should be allowed to change behavior
- any behavior-changing config needs tests showing intentional rank changes

## 5. Allowed Weight Policy

Future hand-designed weights should follow these rules.

### Safety Blocking

Safety blocking weights should remain very large compared with ordinary
preferences.

They are not linguistic preferences. They protect no-oracle and privacy
boundaries.

### Descriptive Diagnostics

Initial descriptive diagnostic weights should be `0.0`.

If a diagnostic family becomes score-active later, it should start with small
weights and a written rationale.

### Negative Weights / Rewards

Negative weights or rewards require extra caution.

They can make candidates look better because a diagnostic fired. That behavior
can be hard to audit and may encourage overfitting.

Initial recommendation:

- do not allow negative weights in the first implementation
- revisit only after a separate design review

### Disallowed Numeric Values

Disallow:

- `NaN`
- positive infinity
- negative infinity
- hidden dynamic weights
- weights computed from evaluation results
- weights computed from expected actions

All active weights should be finite numeric values.

## 6. Config Content That Must Be Forbidden

Future configs must not contain:

- weights fitted to expected actions
- weights fitted to exact-match results
- weights depending on `final_text`
- weights depending on `observed_after_text`
- weights depending on `gold_label`
- weights derived from real participant data
- undocumented weights
- dynamic learned weights
- per-participant weights
- private data paths
- raw text patterns
- teacher corrections
- human corrections
- post-hoc annotations
- future context

Forbidden information must be rejected during validation when feasible.

## 7. No-Oracle and Privacy Policy

The config should contain design metadata only.

It must not contain:

- raw text
- raw local context
- participant identifiers
- private data paths
- final text
- post-edit text
- gold labels
- teacher corrections
- expected-action-derived tuning results

Public repository configs should be based only on synthetic design policy, not
real participant data.

Expected actions remain evaluation-only. They must not influence weight design.

Diagnostic summary counts may motivate human review, but they must not be
converted directly into weights.

## 8. Validation Policy

A future config validator should enforce:

- `config_schema_version` is required
- `config_name` is required
- `default_behavior` is explicit
- active constraint families are listed explicitly
- active weights have required rationales
- active weights have no-oracle-safe reasons
- weights are finite numeric values
- duplicate constraint entries are rejected
- forbidden field names are rejected
- unknown constraints are handled by a documented policy
- default config reproduces current behavior

### Unknown Constraint Handling

Initial recommendation:

- reject unknown active constraint IDs
- allow unknown score-neutral IDs only if explicitly marked as ignored
- prefer fail-closed behavior for active weights

### Duplicate Constraint Handling

Reject duplicate `constraint_id` entries in `constraint_weights`.

Duplicate entries can hide conflicting weight policy.

### Default Config Validation

A default config, if introduced, must reproduce current behavior:

- same blocked candidates
- same `weighted_score` values
- same ranks
- same tie-break behavior

## 9. Tests Required Before Implementation

Before implementing config support, plan tests for:

- config parser behavior
- invalid config rejection
- forbidden field rejection
- duplicate constraint rejection
- finite weight validation
- missing rationale rejection for active weights
- unknown active constraint rejection
- defaults unchanged
- explicit config changes ranking only when intended
- synthetic E2E smoke
- no F1, accuracy, calibration, or learner-state fields

Tests should use synthetic fixtures only.

## 10. Future Roadmap

### Step 65: Implement Hand-Weight Config Schema Models Without Changing Defaults

Add schema model types only if approved. Do not change scoring behavior.

Status: completed for schema models and strict validation helper. No scorer
connection, CLI option, default weight change, formula change, or tie-break
change was added.

### Step 66: Implement Config Loader With Strict Validation

Status: completed as a validation-only CLI and repository smoke script. The
CLI validates synthetic config fixtures and prints safe summary fields only.
It does not print config bodies, score output, ranking output, evaluation
results, expected action details, JSONL content, or raw text.

Default behavior remains unchanged. The scorer still has no config option.

### Step 67: Synthetic Ranking Behavior Diff Smoke Tests

Add synthetic-only tests that demonstrate intentional scoring differences when
an explicit config is supplied.

Do not report performance metrics.

Before this step, the default-unchanged config support boundary should be
reviewed so that no-config scoring remains identical to current behavior.

### Step 68: Hand-Weight Rationale Examples, Synthetic-Only

Add example rationale documents or configs using synthetic-only design
information.

### Later: Private Validation Design

Private validation design remains separate and must not be implemented inside
the public repository.

## 11. Non-Goals

This document does not:

- implement a config loader
- change current weights
- change the scoring formula
- change tie-break behavior
- change constraint generation
- change diagnostic summary tooling
- implement evaluation metrics
- implement calibration
- implement learner-state estimation
- authorize real participant data processing
