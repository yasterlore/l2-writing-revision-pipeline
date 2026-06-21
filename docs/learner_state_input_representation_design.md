# Learner-State Input Representation Design

This document designs the input representation for a future learner-state
estimator.

It is design documentation only. It does not implement a learner-state
estimator, add a model, add metrics, change candidate generation, change OT
scoring, change tie-break behavior, change the manifest schema, change the
Makefile, change workflows, change scripts, change tests, or process real
data.

This is not a performance evaluation.

## 1. Purpose

The purpose of this document is to define what a future learner-state estimator
may receive as input before any estimator or model is implemented.

The input representation must preserve the no-oracle boundary. It must also
remain synthetic-only at this stage.

This design is intentionally one step before schema implementation. It
describes allowed source families, forbidden fields, sequence construction
rules, and future validation needs.

## 2. Operational Definition Of Learner-State

In this project, learner-state is not a direct estimate of a learner's inner
mental state, emotion, motivation, or ability.

The initial operational definition is:

```text
learner-state = local tendency in revision strategy inferred from observable
process data available at the revision point
```

Possible state dimensions include:

- article-related tendency
- noun-number-related tendency
- subject-verb-agreement-related tendency
- tense-related tendency
- preposition-related tendency
- punctuation-related tendency
- hold/no-change tendency

These are local behavioral tendencies over safe process traces. They are not
psychological readings and should not be presented as stable learner traits.

## 3. Input Units

Possible input units:

| Unit | Meaning | Pros | Cons | Initial role |
| --- | --- | --- | --- | --- |
| Participant-level sequence | All synthetic tasks for one synthetic learner identity | Supports longer trajectory questions | Highest risk of overclaiming persistent state | Later, after split rules |
| Session-level sequence | Synthetic tasks within one session | Natural boundary for temporal state | Requires synthetic session design | Useful early |
| Task-level sequence | Micro-episodes within one writing task | Easy to construct from current pipeline shape | Shorter horizon | Recommended initial boundary |
| Micro-episode-level record | One revision-like event and its candidate/scoring context | Closest to current pipeline outputs | No temporal state by itself | Base record |

Initial recommendation: build synthetic participant/session/task sequences from
micro-episode-level records. The first implementation should likely start with
task-level or session-level synthetic sequences, then add participant-level
grouping only after split and leakage rules are documented.

## 4. Available No-Oracle-Safe Sources

Allowed source families, subject to task-specific review:

- `NoOracleSafeEpisodeView` / SafeEpisodeView fields
- revision-event metadata fields that do not expose post-edit context
- micro-episode features derived from local before-context only
- generated candidate metadata
- `CandidateScoreSet`
- `action_type`, `action_family`, and `generation_rule`
- rank, weighted score, blocked flag, and block reasons
- diagnostic count-only summaries
- synthetic `participant_id`, `session_id`, and `task_id` when generated as
  safe synthetic identifiers
- timestamp, order, or sequence index when computed without future leakage
- synthetic expected action only as an evaluation label, not as input features,
  scoring feedback, ranking feedback, or representation fields

The future representation should prefer compact summaries over raw records.
For example, a candidate-family score summary is safer for public docs than
candidate score rows.

## 5. Forbidden Information

Forbidden information:

- `final_text`
- `observed_after_text`
- `gold_label`
- teacher correction
- human correction
- post-hoc annotation
- future edit
- future micro-episode
- final essay outcome
- expected action as a feature
- expected action as scorer or ranking feedback
- real participant data before readiness review
- raw text bodies in public docs

`local_context_after_observed` remains unsafe for candidate generation,
ranking, OT scoring, and learner-state estimation.

## 6. Representation Levels

| Level | Description | Pros | Cons | No-oracle risk | Timing |
| --- | --- | --- | --- | --- | --- |
| A. Micro-episode feature row | One row per episode with safe structural features | Simple and auditable | Weak temporal signal alone | Low if fields are audited | Early |
| B. Candidate-score distribution per episode | Score summaries grouped by candidate family | Uses existing scorer output | Can leak detail if raw rows are copied | Medium; summarize only | Early-medium |
| C. Top-k candidate summary | Top candidate families and safe score aggregates | Compact and useful for prediction tasks | Top-k can overemphasize current scorer behavior | Medium; avoid expected-action feedback | Medium |
| D. Action-family distribution over recent window | Counts or proportions from past/current episodes | Captures trajectory | Window can leak future if built incorrectly | Medium-high; past-only windows required | Medium |
| E. Task-level aggregated trajectory | Task-level sequence summaries | Useful for session modeling | Can hide episode order details | Medium; keep boundaries explicit | Medium-later |
| F. Participant-level sequence embedding input | Long-horizon input across tasks/sessions | Supports richer learner-state modeling | Highest overclaim and leakage risk | High; needs split design first | Later |

The first representation should combine A with carefully summarized B and
past-only D.

## 7. Initial Recommended Representation

Initial lightweight representation:

- `episode_order_index`
- synthetic participant/session/task identifiers
- no-oracle-safe micro-episode features
- candidate-family score summary
- top-ranked candidate family
- blocked candidate count
- descriptive diagnostic counts
- recent-window aggregate features computed only from past/current episodes
- evaluation-only expected action stored separately from feature inputs

The concrete schema should be designed in a later step before implementation.
At that point, every field should be classified as one of:

- identifier
- order metadata
- safe episode feature
- candidate-score summary
- diagnostic count summary
- past-window aggregate
- evaluation-only label

No raw text or generated body should be part of the public schema docs.

## 8. Sequence Construction

Sequence construction rules:

- sort micro-episodes by safe temporal order within a task/session
- do not mix future episodes into the current episode's features
- compute window aggregates from past episodes and, if explicitly designed,
  the current episode only
- make task, session, and participant boundaries explicit
- do not carry state across participant boundaries
- design learner-disjoint splits before estimator training
- keep synthetic expected actions outside the feature table
- keep raw text out of public docs and public summaries

If a future exporter writes a sequence dataset, it should write deterministic
metadata that lets audits confirm ordering and boundary behavior.

## 9. Labels / Targets

Synthetic expected action may be used only as an evaluation label after
candidate generation, scoring, and representation construction.

The project should not create a learner-state label casually. A future target
definition must explain whether the estimator is predicting:

- next action family
- current action family
- action-family tendency over a past window
- selective prediction / abstention status
- another explicitly designed synthetic-only target

Post-hoc correction labels must not be used.

In the initial phase, this document stops at representation design. Future
label and target definitions should be separate design steps.

## 10. Relation To Existing Pipeline

Relation to existing components:

- Rust safe view defines the first no-oracle preprocessing boundary.
- Python candidate generation provides candidate metadata but should not be
  changed by this design.
- OT scorer outputs candidate score sets that can be summarized into safe
  candidate-family features.
- Diagnostic summaries provide count-only descriptive signals.
- Synthetic evaluation can provide expected-action labels only after scoring
  and only outside feature inputs.
- Makefile and release-quality checks remain support infrastructure and do not
  define research semantics.

The future learner-state input representation should consume existing safe
artifacts through a separate, explicit exporter or schema step.

## 11. Validation / Audit Requirements

Future validation should check:

- no forbidden fields are present
- no future micro-episode leakage is present
- inputs remain synthetic-only
- public summaries are count-only
- no raw text appears in docs or safe summaries
- synthetic participant/session/task identifiers are safe and non-real
- learner/session/task split metadata does not allow leakage
- schema versioning exists before implementation
- evaluation-only labels are separated from features

Audits should fail closed when forbidden fields or ordering ambiguity appear.

## 12. Future Implementation Roadmap

Recommended next steps:

1. Step 158: synthetic learner-state sequence dataset design
2. Step 159: learner-state input schema design
3. Step 160: no-oracle audit for learner-state inputs
4. Later: minimal synthetic sequence exporter
5. Later: selective prediction / calibration design
6. Later: estimator prototype

The order may be adjusted, but estimator implementation should wait until the
sequence dataset design, input schema, and no-oracle audit plan are complete.

Step 158 follow-up: see
[Synthetic learner-state sequence dataset design](synthetic_learner_state_sequence_dataset_design.md)
for the next sequence-level planning document.

Step 159 follow-up: see
[Learner-state sequence schema design](learner_state_sequence_schema_design.md)
for the feature row, label row, and manifest separation plan.

Step 160 follow-up: see
[Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
for the planned fail-closed audit before any future sequence exporter output is
trusted.

## 13. Beginner Notes

An input representation is the shape of the data a future model is allowed to
see. It is a contract, not a model.

Learner-state is not treated here as direct mind-reading. It is a cautious
summary of local revision-strategy tendencies from observable process data.

No-oracle means a component cannot use future information, answer keys,
post-hoc annotations, or correction sources when making a prediction or ranking
candidates.

Future leakage happens when information from later in the writing process gets
included in the current prediction input. Even a harmless-looking aggregate can
leak if it counts future episodes.

Expected actions must not be features because they are evaluation-time answers
in synthetic fixtures. Feeding them into features or scoring would make the
task circular.

Synthetic-only development keeps the project private-data safe while the task
definition and representation are still being designed.

## Related Documents

- [Synthetic learner-state sequence dataset design](synthetic_learner_state_sequence_dataset_design.md)
- [Learner-state sequence schema design](learner_state_sequence_schema_design.md)
- [Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
- [Research pipeline next-phase plan](research_pipeline_next_phase_plan.md)
- [No-oracle policy](03_no_oracle_policy.md)
- [Synthetic data policy](12_synthetic_data_policy.md)
- [Synthetic E2E pipeline](synthetic_e2e_pipeline.md)
- [Evaluation spec](evaluation_spec.md)
- [Milestone 03 config-aware diagnostic infrastructure recap](milestone_03_config_aware_diagnostic_infrastructure_recap.md)
- [Public release checklist](public_release_checklist.md)
