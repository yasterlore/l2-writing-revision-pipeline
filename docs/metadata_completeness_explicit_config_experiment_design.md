# Metadata Completeness Explicit Config Experiment Design

This document designs a possible future optional explicit-config experiment for
metadata completeness constraints.

It is design documentation only. It does not implement the experiment, change
scorer weights, change the scoring formula, change deterministic tie-break
behavior, create an actual config, add a config fixture, or claim performance.

Expected actions must not be used as scoring feedback.

## 1. Purpose

The purpose of this document is to describe how metadata completeness could be
treated in a future optional explicit config experiment.

The design preserves these boundaries:

- no-config default scoring remains unchanged
- no actual config is created here
- no weight is chosen here
- no new config fixture is added here
- any future experiment must be explicit `--weight-config` only
- any future experiment must avoid expected-action tuning
- any future experiment must avoid performance claims

This is a design step before implementation, not an implementation step.

If a future explicit config fixture is considered, read
[Metadata completeness config fixture design](metadata_completeness_config_fixture_design.md).
If a future tiny value is considered, read
[Metadata completeness tiny weight selection design](metadata_completeness_tiny_weight_selection_design.md).
Before creating an actual fixture, use
[Metadata completeness fixture readiness checklist](metadata_completeness_fixture_readiness_checklist.md).

## 2. What Metadata Completeness Means

Metadata completeness means that a candidate carries the abstract metadata
needed to explain where it came from and how it should be interpreted.

Examples include:

- candidate metadata completeness
- generation rule presence
- action family presence
- candidate family bucket presence

Related fields or concepts may include:

- `candidate_metadata_complete`
- `generation_rule`
- `action_family`
- `candidate_family_bucket`

Metadata completeness is not candidate quality.

It does not mean:

- the candidate is grammatically correct
- the candidate is the best revision
- the candidate matches an expected action
- the candidate is closer to final text
- the candidate improves model performance

It only means the candidate representation is more complete and easier to
audit.

## 3. Why Consider Score-Active Metadata Completeness

Metadata completeness may be worth considering later because it can support
interpretability.

Possible reasons to consider it:

- candidates with complete representation are easier to explain
- complete `generation_rule` metadata improves traceability
- complete `action_family` metadata clarifies candidate intent
- complete `candidate_family_bucket` metadata helps compare candidate families
- missing metadata may indicate a candidate should be handled cautiously

The possible scoring meaning would be narrow:

- prefer auditable candidate representations
- penalize missing interpretability metadata slightly
- surface candidate-generation gaps through controlled synthetic checks

This must not be framed as grammar correctness or model performance.

## 4. Risks Of Making It Score-Active

Metadata completeness has real risks if it becomes score-active too early.

Risks:

- metadata completeness may be mistaken for grammatical correctness
- candidates with polished representation may be over-preferred
- placeholder candidates may be affected in unintended ways
- ranking may start reflecting candidate-generator implementation details
- upstream metadata bugs may be hidden by scoring behavior
- the experiment may drift into performance tuning
- expected actions may tempt manual weight adjustment

The main risk is confusing "well-described candidate" with "good candidate."

Any future experiment must keep that distinction visible.

## 5. Optional Explicit Config Experiment Principles

A future metadata completeness experiment should follow these principles:

- no-config default unchanged
- explicit `--weight-config` only
- no implicit config discovery
- no hidden config
- no environment-variable config loading
- small weight only
- conservative magnitude
- rationale required
- no expected-action tuning
- no F1 or accuracy optimization
- no calibration optimization
- config validation fail closed
- config-enabled E2E output separated from no-config output
- config-enabled summary output separated from no-config summary
- count-only diff review
- safe stdout only
- no config body in docs or stdout
- no JSONL body in docs or stdout

If the experiment cannot be explained without performance language, it is not
ready.

## 6. Candidate Constraints

The following may be candidates for a future explicit config experiment.

### `CANDIDATE-METADATA-COMPLETE`

Possible meaning:

- candidate has the required metadata needed for interpretation and audit

Possible future status:

- cautious score-active candidate only in explicit config

Risk:

- may conflate completeness with correctness

### `HAS-GENERATION-RULE`

Possible meaning:

- candidate records the generation rule that produced it

Possible future status:

- cautious score-active candidate only in explicit config

Risk:

- may penalize candidates because of generator bookkeeping rather than
  candidate behavior

### `HAS-ACTION-FAMILY`

Possible meaning:

- candidate records an action family that helps interpret the candidate

Possible future status:

- cautious score-active candidate only in explicit config

Risk:

- may overvalue broad family metadata

### `CANDIDATE-FAMILY-BUCKET`

Possible meaning:

- candidate records a coarse family bucket for diagnostics and comparison

Possible future status:

- cautious score-active candidate only in explicit config, if ever

Risk:

- bucket-level scoring can become a broad family preference

### Relation To `candidate_metadata_complete`

If a `candidate_metadata_complete` feature exists or is added later, it should
be treated as a summary of representation completeness, not a correctness
signal.

It should not replace family-level rationale. If it becomes score-active, the
meaning must remain "auditable representation," not "better answer."

## 7. Constraints Not In Scope

The following should not be part of this metadata completeness experiment:

- local pattern diagnostics
- linguistic placeholder diagnostics
- non-leaky linguistic diagnostics
- observation note labels
- diagnostic summary counts
- expected actions
- evaluation metrics
- exact-match results
- final text
- observed-after text
- gold labels
- raw learner text

Those families either need separate review or must remain evaluation-only /
score-neutral.

## 8. Proposed Experimental Design

This section describes a possible future implementation shape. It does not
implement it.

If approved later:

1. Create one synthetic-only explicit config fixture.
2. Use a small metadata completeness weight.
3. Write a rationale before choosing the weight.
4. Validate the config fail-closed.
5. Run no-config fixture lock.
6. Run explicit config ranking diff.
7. Run config-enabled E2E smoke.
8. Run config-enabled summary smoke.
9. Compare count-only diff summaries.
10. Do not inspect raw score rows.
11. Do not inspect JSONL bodies.
12. Do not tune to expected actions.
13. Do not claim performance.

The expected output of the experiment should be a safe wiring and regression
summary, not a model-quality conclusion.

## 9. Required Review Checklist Before Implementation

Before any future implementation, confirm:

- rationale is written
- leakage risk is reviewed
- no-oracle safety is documented
- expected actions are not used for tuning
- no-config fixture lock passes
- config validation passes
- output safety passes
- docs are updated
- rollback plan exists
- config-enabled outputs remain separate from no-config outputs
- failure behavior is fail-closed
- no performance claim is made

Rollback plan should include removing or disabling the explicit config fixture
without changing the no-config default path.

## 10. Beginner Explanation

### Metadata Completeness Is Not Grammar Quality

Metadata completeness means the candidate is well described by the system.

It does not mean the candidate is grammatically correct or pedagogically best.

### Why Only Small Weights?

Completeness is a weak signal. It can support auditability, but it should not
dominate safety, candidate diversity, or linguistic interpretation.

A large weight would make representation polish look like candidate quality.

### Why Protect The No-Config Default?

The no-config path is the baseline. If an experiment changes it accidentally,
future ranking differences become hard to interpret.

Explicit config keeps experiments separate.

### Why Not Fit To Expected Actions?

Expected actions are evaluation references used after scoring.

Using them to choose weights would leak evaluation feedback into scoring policy.

### Why Count-Only Diff Review?

Count-only diff review checks whether an explicit config changed scores or
ranks in expected categories without exposing raw rows, JSONL bodies, candidate
text, or private data.

That is enough for a wiring smoke check. It is not performance evaluation.

## 11. Related Documents

- [Score-active family selection revisit](score_active_family_selection_revisit.md)
- [Synthetic hand-weight rationale examples](synthetic_hand_weight_rationale_examples.md)
- [Metadata completeness config fixture design](metadata_completeness_config_fixture_design.md)
- [Metadata completeness tiny weight selection design](metadata_completeness_tiny_weight_selection_design.md)
- [Metadata completeness fixture readiness checklist](metadata_completeness_fixture_readiness_checklist.md)
- [Hand-weight policy design](hand_weight_policy_design.md)
- [Hand-weight config schema plan](hand_weight_config_schema_plan.md)
- [Explicit config ranking diff plan](explicit_config_ranking_diff_plan.md)
- [Config-enabled E2E design](config_enabled_e2e_design.md)
