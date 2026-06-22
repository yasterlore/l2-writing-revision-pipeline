# Learner-State Sequence Schema Design

This document designs the schema family for a future synthetic learner-state
sequence dataset. It separates feature rows, label rows, and manifest metadata
so that future implementation can preserve no-oracle, synthetic-only, and
no-future-leakage boundaries.

This is design documentation only. It does not implement schema code, a
sequence exporter, a learner-state estimator, a new model, a new metric, or a
production data pipeline. It does not change candidate generation, OT scoring,
tie-break behavior, existing manifest schemas, Makefile targets, workflows,
scripts, or tests. It is not a performance evaluation.

## 1. Purpose

The purpose of this document is to define the intended schema boundaries before
any learner-state sequence exporter is implemented.

The design has four goals:

- keep feature inputs separate from evaluation labels
- keep dataset metadata separate from row bodies
- make no-oracle and synthetic-only checks explicit
- avoid public documentation that exposes raw text, row dumps, or generated
  output bodies

The schema design should support later synthetic sequence analysis and
learner-state estimation without allowing expected actions, future edits, or
post-hoc correction sources into the feature path.

## 2. Schema Family Overview

The future dataset should use three primary schema families.

| Schema family | Purpose | Safety boundary |
| --- | --- | --- |
| Feature row schema | Defines one no-oracle-safe input row per synthetic micro-episode | Must not contain labels, future outcomes, raw text, or correction sources |
| Label row schema | Defines evaluation-only labels derived from synthetic expected actions | Must be stored separately and never used for candidate generation, scoring, or ranking |
| Manifest schema | Defines dataset-level metadata, count-only summaries, paths, versions, and audit status | Must suppress row bodies, raw text, label bodies, and candidate score rows |

A count-only summary schema may be useful later for public reporting, but it
should remain a derived metadata artifact rather than a replacement for the
feature, label, and manifest schemas.

## 3. Feature Row Schema Design

Feature rows are the only rows a future learner-state estimator may consume as
inputs. Each row represents one synthetic micro-episode at a specific sequence
position.

Allowed field candidates:

- `schema_version`
- `synthetic_participant_id`
- `synthetic_session_id`
- `synthetic_task_id`
- `micro_episode_id`, if the identifier is synthetic and safe
- `episode_order_index`
- `task_order_index`, if derived without future leakage
- `session_order_index`, if derived without future leakage
- boundary markers for task, session, and participant starts or ends
- no-oracle-safe micro-episode derived features
- `candidate_family_score_summary`
- `top_ranked_candidate_family`
- `top_k_candidate_family_summary`
- `blocked_candidate_count`
- `diagnostic_count_features`
- `past_only_window_features`
- `split_id`, only if assigned from synthetic no-oracle-safe grouping metadata

The candidate-related fields should be summaries, not raw candidate bodies.
Diagnostic fields should be count-only or categorical summaries that do not
expose raw learner text.

Feature rows must not include:

- `final_text`
- `observed_after_text`
- `gold_label`
- teacher correction
- human correction
- post-hoc annotation
- future edit
- future episode
- final essay outcome
- expected action fields
- raw text body
- raw candidate body
- raw candidate score rows
- real participant identifiers
- private or manual real-data paths

If there is uncertainty about whether a field is no-oracle safe, the future
implementation should fail closed and exclude it until reviewed.

## 4. Label Row Schema Design

Label rows are evaluation-only rows. They should be stored separately from
feature rows and joined only during evaluation or test-time reporting.

Allowed field candidates:

- `label_schema_version`
- `synthetic_participant_id`
- `synthetic_session_id`
- `synthetic_task_id`
- `micro_episode_id`, if synthetic and safe
- `episode_order_index`
- `expected_action_family`
- `expected_action_type`
- optional `label_source`, such as `synthetic_expected_action_registry`

Labels are not model inputs. Labels are not scorer feedback. Labels are not
used in candidate generation, candidate ranking, OT scoring, tie-breaks, or
diagnostic construction.

Synthetic expected actions may be used only as evaluation labels. Real
correction labels, teacher corrections, human corrections, post-hoc annotations,
and production outcomes are not allowed in this schema family.

## 5. Manifest Schema Design

The manifest should describe the dataset without exposing row contents.

Allowed manifest candidates:

- `manifest_schema_version`
- `dataset_schema_version`
- `created_by`
- `synthetic_only: true`
- `no_oracle_checked`, with states such as `planned`, `true`, or `false`
- feature file paths
- label file paths
- count-only row counts
- participant, session, task, and episode counts
- split metadata summary
- forbidden-fields-absent summary
- `content_suppressed: true`
- explicit no-raw-data-body note
- explicit no-real-data note

Manifest contents must not include:

- raw row body
- raw text
- full JSONL body
- label body
- candidate score rows
- generated summary body
- real-data paths containing private context

This future learner-state sequence manifest is separate from existing summary
manifest schemas. This document does not modify the existing manifest schema.

## 6. Join Key Design

Feature rows and label rows may be joined only through safe synthetic keys.

Allowed join key candidates:

- `synthetic_participant_id`
- `synthetic_session_id`
- `synthetic_task_id`
- `micro_episode_id`, if synthetic and safe
- `episode_order_index`, when paired with stable synthetic hierarchy IDs

Join keys must not encode expected labels, future outcomes, correctness status,
final text state, or participant identity from real data.

Stable synthetic IDs are allowed because they support reproducible synthetic
tests and learner-disjoint splits. Real participant IDs are forbidden. A hash
strategy may be considered later for private-data readiness, but no hash
strategy is implemented or required here.

## 7. Versioning Policy

Each schema family should version independently:

- feature rows use `schema_version`
- label rows use `label_schema_version`
- manifests use `manifest_schema_version`

Future implementation should fail closed on unknown versions. Schema migration
should be explicit, reviewed, and documented before any exporter or estimator
depends on a new version.

For now, versioning is a design rule only. No schema code or generated files
are added in this step.

## 8. Split Metadata Design

Split metadata should support learner-disjoint evaluation and future
group-leakage checks.

Allowed split design:

- learner-disjoint split metadata based on synthetic participant groups
- optional task-disjoint split metadata for stricter generalization checks
- synthetic split identifiers only
- count-only split summaries in the manifest
- no expected-action-based split assignment
- no outcome-based split assignment

Split assignment should not use expected actions, final outcomes, label
distribution tuning, or post-hoc corrections. Group leakage prevention should
be explicit: the same synthetic participant should not appear across train,
validation, and test splits unless a future design intentionally creates a
different split family and labels it clearly.

## 9. No-Oracle Forbidden Fields

The following are forbidden in feature inputs, split assignment, candidate
generation feedback, scoring feedback, ranking feedback, and public row
documentation:

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

Expected actions may appear only in the separate label schema for synthetic
evaluation.

## 10. Output Format Recommendation

Initial future output recommendation:

- `features.jsonl`
- `labels.jsonl`
- `manifest.json`
- optional `summary.json` with count-only public-safe summaries

This step does not generate any of these files.

Public docs should not paste row dumps, full JSONL bodies, raw text, label
bodies, candidate bodies, score rows, or generated output bodies. Public
documentation should use count-only summaries and schema field names.

For the future exporter boundary that would generate these files, see
[Learner-state sequence exporter design](learner_state_sequence_exporter_design.md).
For the future synthetic input fixture contract that would feed that exporter,
see
[Learner-state sequence exporter input fixture design](learner_state_sequence_exporter_input_fixture_design.md).
For the downstream contract that would consume audited exporter outputs before
any estimator implementation, see
[Learner-state estimator input contract design](learner_state_estimator_input_contract_design.md).

## 11. Validation / Audit Design

Future implementation should include audits before any sequence exporter output
is treated as usable.

Required audit categories:

- forbidden field audit
- feature-label separation audit
- future leakage audit
- split leakage audit
- synthetic-only path audit
- schema version audit
- manifest content suppression audit
- count-only public summary audit

The audits should verify absence of forbidden fields, confirm that labels are
not present in feature rows, confirm that rolling features use only current or
past information, and confirm that public summaries do not expose row bodies.

## 12. Relation to Existing Pipeline

The future schema should compose existing safe pipeline outputs without
changing their behavior.

- Safe episode views define the no-oracle boundary for event-derived input.
- `CandidateScoreSet` can provide summarized candidate-family score features.
- Diagnostic summaries can provide count-only descriptive features.
- The synthetic expected action registry can provide evaluation-only labels.
- Existing synthetic evaluation summaries remain separate from learner-state
  feature rows.
- Makefile and release-quality checks remain support infrastructure; they do
  not define learner-state semantics.
- A future exporter should assemble these pieces without modifying candidate
  generation, OT scoring, tie-breaks, diagnostics, or existing manifest schemas.

## 13. Future Implementation Roadmap

Recommended order:

1. Step 160: learner-state sequence no-oracle audit design
2. Step 161: learner-state sequence audit fixtures / result schema design
3. Step 162: synthetic learner-state audit fixture files design
4. Step 163: create synthetic audit fixture files
5. Step 164: synthetic sequence exporter design or implementation
6. Step 165: schema fixtures / smoke tests
7. Step 191: learner-state estimator input contract design
8. Later: selective prediction / calibration design
9. Later: estimator prototype

If implementation risk is high, Step 162 may remain a separate exporter design
step before code is added.

Step 160 follow-up: see
[Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
for the fail-closed audit plan covering features, labels, manifests, split
metadata, join keys, paths, and public output.

Step 161 follow-up: see
[Learner-state sequence audit fixture/schema design](learner_state_sequence_audit_fixture_schema_design.md)
for future valid and invalid synthetic audit fixtures and safe audit result
fields.

Step 162 follow-up: see
[Learner-state sequence audit fixture files design](learner_state_sequence_audit_fixture_files_design.md)
for future fixture placement, naming, and file organization.

## 14. Beginner Notes

A schema is a contract for what fields a file may contain. It lets later tools
read the data without guessing.

Features and labels are separated so a future model cannot accidentally see
the answer while making a prediction.

A manifest is metadata about a dataset. It can say how many rows exist, what
versions were used, and which safety checks ran without printing the row
contents.

Expected action is useful as a synthetic evaluation answer, but it must not be
part of the input. Putting it into features would make the task circular.

Versioning matters because schemas change over time. A version field lets
future checks reject unknown or incompatible files instead of silently reading
the wrong shape.

## Related Documents

- [Synthetic learner-state sequence dataset design](synthetic_learner_state_sequence_dataset_design.md)
- [Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
- [Learner-state sequence audit fixture/schema design](learner_state_sequence_audit_fixture_schema_design.md)
- [Learner-state sequence audit fixture files design](learner_state_sequence_audit_fixture_files_design.md)
- [Learner-state input representation design](learner_state_input_representation_design.md)
- [Research pipeline next-phase plan](research_pipeline_next_phase_plan.md)
- [No-oracle policy](03_no_oracle_policy.md)
- [Synthetic data policy](12_synthetic_data_policy.md)
- [Synthetic E2E pipeline](synthetic_e2e_pipeline.md)
- [Evaluation spec](evaluation_spec.md)
- [Public release checklist](public_release_checklist.md)
