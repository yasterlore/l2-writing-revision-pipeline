# Synthetic Learner-State Sequence Dataset Design

This document designs a future synthetic-only sequence dataset for
learner-state input representation, sequence analysis, and later selective
prediction or estimator work.

It is design documentation only. It does not implement a sequence exporter,
learner-state estimator, model, metric, production data pipeline, candidate
generation change, OT scoring change, manifest schema change, Makefile change,
workflow change, script change, or test change.

This is not a performance evaluation.

## 1. Purpose

The purpose of this document is to define how the learner-state input
representation should be organized as a sequence dataset.

The dataset design remains synthetic-only. It must preserve the no-oracle
boundary and avoid future leakage.

This document stops before exporter, schema, model, or metric implementation.

## 2. Dataset Base Units

Candidate base units:

| Unit | Meaning | Pros | Cons | Initial role |
| --- | --- | --- | --- | --- |
| Episode row | One micro-episode with safe features and summaries | Simple, close to current artifacts, easy to audit | No sequence context by itself | Base row |
| Task sequence | Ordered episode rows within one task | Natural first sequence boundary | Shorter than a full learner trajectory | Recommended early unit |
| Session sequence | Ordered task sequences within one session | Captures short-term cross-task behavior | Requires synthetic session metadata | Recommended after task sequences |
| Participant sequence | Ordered session/task sequences for one synthetic learner identity | Supports learner-disjoint splits and longer horizons | Highest risk of overclaiming stable traits | Later, with strict boundaries |
| Split-level collection | Train/validation/test groups of synthetic participants/tasks | Supports future evaluation design | Can leak if split metadata uses labels or future outcomes | Design early, use carefully |

Initial recommendation: organize the future dataset as:

```text
synthetic participant
  -> synthetic session
  -> synthetic task
  -> ordered micro-episode sequence
```

The first exporter should likely emit episode rows with enough identifiers to
reconstruct that hierarchy, plus a separate manifest and separate label file
design.

## 3. Sequence Hierarchy

Sequence metadata candidates:

- synthetic `participant_id`
- synthetic `session_id`
- synthetic `task_id`
- `episode_order_index`
- `micro_episode_id`, if generated synthetically and safe
- boundary markers for first/last episode within a task
- task boundary metadata
- session boundary metadata
- participant boundary metadata
- split metadata prepared for learner-disjoint splits

Real participant IDs must not be used.

Synthetic identifiers should be stable enough for reproducible tests but must
not resemble private or institutional identifiers.

Boundary metadata should support safe grouping without requiring raw text or
future outcomes.

## 4. Episode-Level Payload

Each episode row may include:

- no-oracle-safe episode features
- candidate-family score summary
- top-ranked candidate family
- top-k candidate-family summary
- blocked candidate count
- diagnostic count-only features
- previous-window aggregate features, if computed from past episodes only
- sequence position or task progress bucket, if computed without future
  leakage
- evaluation-label placeholder stored separately from features

The payload should not include raw candidate rows, raw score rows, raw writing
text, or generated file bodies.

Task progress features need special care. If a progress feature requires
knowing the total number of future episodes in a task, it can leak future
structure. Early designs should prefer `episode_order_index` and past-count
features over percentage-of-task features.

## 5. Labels / Targets Separation

Synthetic expected action is evaluation-label information only.

It must not be included in the feature payload. It must not be used as scorer
feedback, ranking feedback, candidate generation input, or window aggregate
input.

Future labels should be stored separately from feature rows. Possible future
layout:

- feature rows file
- label rows file
- manifest file that describes their relationship without copying row bodies

The dataset should not create actual learner-state labels yet. Target design
for action-family prediction, next-action prediction, tendency estimation, or
selective prediction belongs in a later step.

Future observed action must not be added to the current episode feature row.

## 6. Split Design

Split rules to design before estimator implementation:

- learner-disjoint split by synthetic participant ID
- optional task-disjoint split for robustness checks
- train / validation / test boundaries
- split metadata based on synthetic grouping only
- no split assignment based on future outcomes or labels
- no group-level leakage across participants, sessions, or tasks
- no real participant identifiers

Learner-disjoint split is the safest default for future estimator work because
it prevents the same synthetic learner identity from appearing in both training
and evaluation partitions.

Task-disjoint split may be useful later, but it should not replace
learner-disjoint checks.

## 7. Ordering And Windowing

Ordering and windowing rules:

- current episode features may use only current and past information
- rolling window features must be past-only unless a current-episode inclusion
  rule is explicitly documented
- future episodes are not allowed in current features
- sequence sorting must be deterministic
- task, session, and participant boundaries must reset or explicitly mark
  window state
- elapsed/order indices are allowed only when they do not encode future
  outcomes
- idle or late-event features should not be introduced here unless already
  no-oracle-safe and separately designed

Avoid early task-progress features that require total task length. A safer
early alternative is a past-count bucket such as first episode, early past
count, middle past count, or later past count, computed without reading future
episodes.

## 8. No-Oracle Forbidden Fields

Forbidden fields and concepts:

- `final_text`
- `observed_after_text`
- `gold_label`
- teacher correction
- human correction
- post-hoc annotation
- future edit
- future episode
- final essay outcome
- expected action as feature
- expected action as scoring or ranking feedback
- real participant data before readiness review
- raw text body in public docs

The dataset must also exclude `local_context_after_observed` from feature
inputs.

## 9. Output Format Candidates

| Format | Pros | Cons | Initial recommendation |
| --- | --- | --- | --- |
| JSONL episode rows | Simple, streamable, close to current pipeline style | Easy to misuse by dumping rows into docs | Recommended for feature rows |
| Grouped JSON by participant/session/task | Preserves hierarchy directly | Harder to stream and diff | Later or manifest-level only |
| Parquet/Arrow | Efficient for larger datasets | Adds tooling and binary format complexity | Later |
| CSV summary only | Public-safe for counts | Not enough for sequence modeling | Use for public summaries, not main data |
| Manifest + data files | Separates metadata from rows | Requires schema discipline | Recommended |

Initial design recommendation:

- JSONL feature rows
- separate JSONL label rows or label file design
- separate manifest
- count-only public summary

No files are created by this step.

## 10. Public Summary Policy

Public docs may include only count-only summaries.

Public docs must not include:

- row dumps
- raw text
- label bodies
- candidate score rows
- candidate bodies
- config bodies
- JSONL bodies
- real data

Safe public summaries may include counts such as number of synthetic
participants, sessions, tasks, episodes, feature families, split partitions,
and audit status.

## 11. Validation / Audit Requirements

Future validation should include:

- forbidden field audit
- future leakage audit
- synthetic-only path checks
- split leakage audit
- label-feature separation audit
- sequence ordering audit
- schema versioning
- manifest safety checks
- count-only summary checks

Audits should fail closed if a row contains forbidden fields, if ordering is
ambiguous, or if a label appears in the feature payload.

## 12. Relation To Existing Pipeline

Relationship to current components:

- SafeEpisodeView provides the first no-oracle-safe source boundary.
- CandidateScoreSet can be summarized into candidate-family score features.
- Diagnostic summaries provide count-only descriptive features.
- Synthetic expected actions registry can provide evaluation labels only after
  scoring and only outside feature payloads.
- Synthetic evaluation summary remains a support signal, not a model metric for
  this design.
- Makefile and release-quality checks remain support infrastructure.
- A future exporter should compose existing safe artifacts without changing
  candidate generation, OT scoring, or diagnostic logic.

## 13. Future Implementation Roadmap

Recommended order:

1. Step 159: learner-state sequence schema design
2. Step 160: learner-state sequence no-oracle audit design
3. Step 161: learner-state sequence audit fixtures / result schema design
4. Step 162: minimal synthetic sequence exporter design or implementation
5. Step 163: sequence dataset smoke tests
6. Later: selective prediction / calibration design
7. Later: estimator prototype

Exporter implementation should wait until schema and audit design are complete.

Step 159 follow-up: see
[Learner-state sequence schema design](learner_state_sequence_schema_design.md)
for the planned feature row, label row, manifest, join-key, and versioning
schema boundaries.

Step 160 follow-up: see
[Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
for the future fail-closed audit of sequence features, labels, manifests,
splits, joins, paths, and public output.

Step 161 follow-up: see
[Learner-state sequence audit fixture/schema design](learner_state_sequence_audit_fixture_schema_design.md)
for the future audit fixture families and safe audit result schema.

## 14. Beginner Notes

A sequence dataset is a dataset where records are ordered. Here, the records
are synthetic micro-episodes arranged inside synthetic tasks, sessions, and
participants.

Episodes are ordered because learner-state questions are temporal. A later
revision may depend on patterns visible in earlier revisions, but not the other
way around.

Participant, session, and task boundaries matter because features and splits
must not accidentally mix information across learners or tasks.

Labels and features are separated so the model cannot accidentally see the
answer. The expected action is useful for evaluation, but it must not be part
of the input.

Synthetic-only design keeps the project safe while the representation,
sequence rules, and audits are still being defined.

## Related Documents

- [Learner-state input representation design](learner_state_input_representation_design.md)
- [Learner-state sequence schema design](learner_state_sequence_schema_design.md)
- [Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
- [Learner-state sequence audit fixture/schema design](learner_state_sequence_audit_fixture_schema_design.md)
- [Research pipeline next-phase plan](research_pipeline_next_phase_plan.md)
- [No-oracle policy](03_no_oracle_policy.md)
- [Synthetic data policy](12_synthetic_data_policy.md)
- [Synthetic E2E pipeline](synthetic_e2e_pipeline.md)
- [Evaluation spec](evaluation_spec.md)
- [Public release checklist](public_release_checklist.md)
