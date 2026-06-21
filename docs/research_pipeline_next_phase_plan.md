# Research Pipeline Next-Phase Plan

This document plans the next research-pipeline phase after the Makefile,
release-quality, and CI maintenance work.

It is planning documentation only. It does not implement a learner-state
estimator, add a model, add metrics, change candidate generation, change OT
scoring, change tie-break behavior, change the manifest schema, change the
Makefile, change workflows, change scripts, or process real data.

This is not a performance evaluation.

## 1. Purpose

The purpose of this document is to move attention back from infrastructure
maintenance to research-pipeline development while preserving the current
safety boundaries.

Recent work improved command discoverability, release-quality checks, CI
maintenance, and public-safe documentation. That work supports the research
pipeline, but it does not decide the next modeling step.

This plan separates infrastructure status from research development, keeps the
repository synthetic-only, and preserves the no-oracle boundary before any
learner-state estimation work begins.

## 2. Current State

Current pipeline state:

- Rust raw event validation checks JSONL shape, required fields, sequence
  consistency, and no-oracle forbidden fields.
- Rust replay reconstructs event streams and reports safe status without
  exposing raw writing text.
- Rust revision-event and micro-episode extraction identify revision-like
  events and create synthetic micro-episode records.
- Rust no-oracle audit and safe-view export define the boundary before Python
  prototype stages.
- Python candidate generation consumes safe episode views and emits placeholder
  candidate sets.
- Python OT-style scoring consumes constraint violations and produces ranked
  candidate score sets without using future, gold, or post-hoc inputs.
- Diagnostic constraints provide descriptive and blocking records, including
  local-pattern and linguistic placeholder diagnostics.
- Synthetic evaluation wiring uses synthetic expected actions only after
  scoring, never as scoring or ranking feedback.
- Config-aware scoring infrastructure supports explicit synthetic config smoke
  checks while keeping no-config defaults protected.
- Release-quality wrapper and Makefile entrypoints provide local command
  surfaces for normal success-path checks.
- CI and manual release-quality workflow provide support infrastructure for
  maintenance checks.
- Public-safe docs, recaps, reviews, and status markers describe the current
  state without raw output bodies or performance claims.

## 3. Large Unfinished Research Areas

Large unfinished research areas:

- Candidate generation enrichment: current candidates are still prototype-level
  and need richer no-oracle-safe generation strategies.
- OT constraints becoming score-active: descriptive constraints need a reviewed
  path before any additional family can influence scoring.
- Synthetic evaluation expansion: synthetic cases and sequence coverage remain
  limited and should grow before claiming broader behavior.
- Selective prediction and calibration preparation: uncertainty and abstention
  design should be planned before metric implementation.
- Learner-state input representation: the project needs a safe representation
  of what a learner-state estimator may consume.
- Learner-state model pre-design: model scope, labels, training boundaries, and
  synthetic supervision need design before implementation.
- Real-data readiness: real participant or institutional data remains a later
  phase gated by separate readiness review.
- Actual learner-state estimator: not implemented yet and should not be added
  before input and synthetic dataset design.

## 4. Next-Phase Options

| Option | Pros | Cons | Now? |
| --- | --- | --- | --- |
| A. Candidate generation enrichment | Improves the front of the pipeline and may make later scoring more meaningful | Can accidentally expand behavior before evaluation design catches up | Good candidate, but should follow a scoped design |
| B. OT scorer active-weight design | Clarifies which diagnostics may become score-active | Easy to overfit synthetic examples or blur descriptive diagnostics with scoring | Useful later, after learner-state input and dataset scope are clearer |
| C. Synthetic evaluation expansion | Broadens coverage and reduces single-case thinking | Can become metric work too early if not carefully scoped | High value, especially as sequence dataset design |
| D. Selective prediction / calibration design | Prepares abstention and confidence boundaries before implementation | Metric implementation is out of scope for now | Good as design-only follow-up |
| E. Learner-state input representation design | Defines safe inputs before any estimator exists | Does not produce a model immediately | Best next step |
| F. Learner-state estimator implementation | Moves toward the long-term research goal | Too early without input, dataset, and evaluation design | Not yet |
| G. Real data readiness | Necessary before any real data work | Premature for the current synthetic-only stage | Later |
| H. Documentation-only consolidation | Low risk and improves readability | Does not move research design forward much by itself | Useful only as support work |

## 5. Recommended Approach

Initial recommendation:

1. Learner-state input representation design
2. Synthetic sequence dataset design
3. Selective prediction / calibration design
4. Learner-state estimator minimal prototype
5. Real-data readiness review

The key recommendation is to design the learner-state input representation
before implementing an estimator. That representation should define which
safe-view fields, candidate-score summaries, action-family metadata, and
count-only diagnostic signals can be used.

The second step should design a synthetic sequence dataset because
learner-state estimation is inherently temporal. Single micro-episodes are not
enough to describe state transitions without a sequence design.

Selective prediction and calibration should remain design-only until the
prediction task, synthetic labels, and safe evaluation split are clear.

## 6. No-Oracle Boundary

If the project moves toward learner-state estimation, forbidden inputs remain
forbidden:

- `final_text`
- `observed_after_text`
- `gold_label`
- teacher correction
- post-hoc annotation
- future edit
- expected action as scoring or ranking feedback
- real participant data before readiness review

Allowed inputs, subject to task-specific review:

- no-oracle safe episode view
- candidate scores generated without oracle inputs
- action-family metadata
- diagnostic count-only summaries
- synthetic expected action only for evaluation after scoring, not for scoring
  or ranking

The learner-state estimator should document the exact input fields it consumes
before implementation.

## 7. Synthetic-Only Boundary

Development, tests, docs examples, and planning remain synthetic-only.

Real data is not introduced by this plan. Production or research data must not
be used until the relevant readiness checklist and privacy review are complete.

Docs must not include raw writing text, JSONL bodies, summary CSV bodies,
diagnostic bodies, config bodies, candidate score rows, or private/manual/real
paths.

## 8. Recommended Step 157 Candidates

Recommended Step 157 candidates:

| Candidate | Priority | Rationale |
| --- | --- | --- |
| Step 157: learner-state input representation design | High | Safest bridge from current pipeline to learner-state work |
| Step 157: synthetic sequence dataset design | High | Needed because learner state is sequence-oriented |
| Step 157: selective prediction design | Medium | Useful, but should follow task/input definitions |
| Step 157: candidate generation enrichment design | Medium | Important, but less directly tied to learner-state input boundary |
| Step 157: OT scorer active-weight design | Medium-low | Should wait until target task and representation are clearer |
| Step 157: documentation-only consolidation | Low | Helpful only if navigation becomes confusing |

Preferred next step: learner-state input representation design.

Step 157 follow-up: see
[Learner-state input representation design](learner_state_input_representation_design.md)
for the first detailed design step after this next-phase plan.

## 9. Migration / Dependency Considerations

The Makefile entrypoint does not change research implementation behavior.
Existing shell scripts remain a compatibility layer.

CI and release-quality checks remain support infrastructure. They should catch
regressions, but they should not drive research logic changes by themselves.

Research logic changes should be scoped separately from infrastructure changes.
For example, candidate generation enrichment, learner-state input design, and
synthetic dataset design should each have their own design step before any
implementation step.

The project should continue moving from docs-only planning to implementation
incrementally, with no raw output bodies added to docs.

## 10. Beginner Notes

Infrastructure work makes the project easier to run and safer to maintain, but
it does not answer the research question by itself. That is why the next phase
starts with representation and dataset design rather than immediately adding a
model.

Learner-state estimation means estimating something about the learner's current
writing or revision behavior from information available at that point in the
process. The input representation is the contract that says what the estimator
may see.

The no-oracle boundary prevents the system from using information from the
future, from answer keys, or from post-hoc correction sources when making a
prediction or ranking candidates.

Synthetic-only development keeps the project reviewable and privacy-safe while
the task definition is still being refined.

A next-phase plan is a map. It narrows the next useful design step without
pretending that implementation or performance evaluation has already happened.

## Related Documents

- [Learner-state input representation design](learner_state_input_representation_design.md)
- [Synthetic learner-state sequence dataset design](synthetic_learner_state_sequence_dataset_design.md)
- [Milestone 05 Makefile orchestration recap](milestone_05_makefile_orchestration_recap.md)
- [Milestone 05 status marker](status/milestone_05_status.md)
- [No-oracle policy](03_no_oracle_policy.md)
- [Synthetic data policy](12_synthetic_data_policy.md)
- [Synthetic E2E pipeline](synthetic_e2e_pipeline.md)
- [Milestone 03 config-aware diagnostic infrastructure recap](milestone_03_config_aware_diagnostic_infrastructure_recap.md)
- [Public release checklist](public_release_checklist.md)
