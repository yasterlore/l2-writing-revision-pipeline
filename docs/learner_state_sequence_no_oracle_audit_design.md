# Learner-State Sequence No-Oracle Audit Design

This document designs the no-oracle audit for a future synthetic learner-state
sequence dataset. It focuses on feature rows, label rows, manifests, split
metadata, join keys, file paths, and public output safety.

This is design documentation only. It does not implement audit code, schema
code, a sequence exporter, a learner-state estimator, a new model, a new
metric, or a production data pipeline. It does not change candidate generation,
OT scoring, scoring formula, tie-break behavior, existing manifest schemas,
Makefile targets, workflows, scripts, or tests. It is not a performance
evaluation.

## 1. Purpose

The purpose of this document is to define how a future learner-state sequence
dataset should be audited before any exporter output is trusted.

The audit should check features, labels, and manifests separately. It should
fail closed when forbidden fields, feature-label mixing, future leakage, split
leakage, unsafe paths, unknown schema versions, or public body leakage are
detected.

The audit is not intended to validate learner-state model quality, scorer
quality, research validity, or production readiness.

## 2. Audit Scope

In scope:

- feature rows
- label rows
- manifest
- optional count-only summary
- split metadata
- join keys
- file paths
- public docs output

Out of scope:

- model performance
- learner-state validity
- real data readiness
- estimator correctness
- candidate generation quality
- OT scoring quality
- calibration, accuracy, F1, ECE, or AURCC

The audit should answer a narrow question: whether the future sequence dataset
shape stays within the no-oracle, synthetic-only, and no-future-leakage
boundaries.

## 3. Audit Categories

The future audit should include these categories:

- forbidden field audit
- label-feature separation audit
- future leakage audit
- split leakage audit
- synthetic-only path audit
- manifest content suppression audit
- schema version audit
- join key safety audit
- count-only public summary audit
- raw body leakage audit

Each category should produce safe pass/fail status and count-only violation
summaries. It should not print row dumps or raw learner text.

## 4. Forbidden Field Audit

The forbidden field audit should scan top-level fields, nested keys, metadata
keys, path-like fields, and suspicious name variants.

Forbidden or suspicious names include:

- `final_text`
- `observed_after_text`
- `gold_label`
- `teacher_correction`
- `human_correction`
- `post_hoc_annotation`
- `future_edit`
- `future_episode`
- `final_essay_outcome`
- `expected_action` in feature rows
- `expected_action_feedback`
- `raw_text`
- `real_participant_id`
- private paths
- manual real-data paths
- real-data paths

The implementation should treat obvious spelling variants and nested key names
as suspicious. A suspicious field should fail closed unless an explicit design
review allows it for a non-feature, non-public purpose.

## 5. Label-Feature Separation Audit

This audit should verify that feature rows and label rows remain separate.

Required checks:

- feature rows contain no label fields
- feature rows contain no expected action fields
- label rows do not carry feature values
- expected action appears only in labels
- join keys are safe synthetic keys
- label file paths and feature file paths are separate
- evaluation labels do not flow back into scorer, candidate, or ranking inputs

The audit should fail if a label-like field appears in a feature row, even if
the value looks harmless in a synthetic fixture.

## 6. Future Leakage Audit

This audit should verify that each current feature row uses only current or
past information.

Required checks:

- current feature rows use only current and past episodes
- rolling windows are past-only
- future episode statistics are absent
- total task length is absent when it would require future knowledge
- final essay outcome is absent
- future edit count is absent
- episode order index is allowed only as a sequence position
- progress features are treated as risky unless they are computed without
  future knowledge

The audit should distinguish safe ordering metadata from future-derived
progress metadata. `episode_order_index` can be safe; a feature that depends on
the eventual number of episodes is not safe unless separately reviewed.

## 7. Split Leakage Audit

This audit should verify group-safe synthetic splits.

Required checks:

- learner-disjoint split metadata is enforced when that split family is used
- optional task-disjoint split metadata is checked when present
- the same synthetic participant does not appear in train, validation, and test
  partitions for learner-disjoint splits
- split assignment does not use expected action
- split assignment does not use outcome or correctness signals
- split metadata in manifests is count-only
- group leakage is reported as a failure

Split leakage is a dataset construction problem, not a model performance
finding. It should fail the dataset audit before any estimator is trained.

## 8. Synthetic-Only Path Audit

This audit should verify that future generated outputs and input references
stay within synthetic-only boundaries.

Required checks:

- generated sequence outputs use safe synthetic output paths
- real-data source paths are rejected
- `real_data`, `participant_data`, and `private_data` path segments are rejected
  for dataset sources
- `manual_outputs` is rejected as a public dataset source
- private notes may remain private/local, but they are not dataset inputs
- absolute private paths are not written into public manifests
- `tmp/` outputs remain ignored by Git
- no real participant data is used

If a path appears private, manual, or real-data derived, the audit should fail
or reject it as private-only, not silently pass.

## 9. Manifest Audit

The manifest audit should verify that the manifest records dataset metadata
without exposing content.

Required checks:

- `content_suppressed` is true
- `synthetic_only` is true
- raw row bodies are absent
- label bodies are absent
- candidate score rows are absent
- row counts are count-only
- participant, session, task, and episode counts are count-only
- schema versions are present
- private paths are absent
- audit status fields are present or explicitly planned

The manifest may point to future generated files, but it should not embed their
contents.

## 10. Schema Version Audit

The schema version audit should verify that each schema family is explicit and
compatible.

Required checks:

- feature schema version is present
- label schema version is present
- manifest schema version is present
- unknown versions fail closed in future implementation
- version mismatches are handled safely
- no implicit upgrade is performed

If a future exporter emits a version the audit does not recognize, the audit
should reject the dataset until the version is reviewed.

## 11. Join Key Safety Audit

The join key audit should verify that feature rows and label rows can be joined
without leaking labels, outcomes, or raw text.

Required checks:

- join keys use safe synthetic IDs only
- `micro_episode_id` does not encode expected label or outcome information
- real participant IDs are absent
- join keys are stable but non-semantic
- hashes of raw text are absent unless a separate privacy review approves them
- join keys do not reveal final outcome, correctness, or label family

Stable synthetic IDs are allowed. Semantic IDs that encode the answer are not.

## 12. Audit Output Policy

Audit output should be public-safe by default.

Allowed output:

- safe pass/fail status
- count-only violation summary
- checked file category names
- schema version names
- audit category names
- suppressed-content status

Forbidden output:

- row dumps
- raw text
- JSONL body
- label body
- config body
- candidate rows
- raw candidate score rows
- real data
- private path details

Public output should be safe even when the audit fails.

## 13. Failure Policy

The audit should fail closed.

Failure conditions:

- forbidden field detected -> fail
- label in feature row -> fail
- feature value in label row -> fail
- future leakage detected -> fail
- split leakage detected -> fail
- manifest body leakage detected -> fail
- unknown schema version -> fail
- version mismatch -> fail
- suspicious path -> fail or private-only reject
- raw body printed or embedded -> fail

There should be no silent pass for unknown fields, unknown versions, suspicious
paths, or ambiguous feature-label boundaries.

## 14. Relation to Existing Pipeline

The future learner-state sequence audit should build on existing safety ideas
without changing current behavior.

- Existing no-oracle audit defines the broader forbidden-field boundary.
- Safe episode views define the no-oracle-safe event-derived input surface.
- `CandidateScoreSet` may contribute summarized candidate-family features, not
  raw candidate row bodies.
- The expected action registry provides evaluation labels only.
- Synthetic evaluation remains separate from feature construction.
- Safe output scan helpers may inform future implementation, but this design
  does not change tests.
- The release-quality wrapper and Makefile remain support infrastructure and
  are not changed by this audit design.
- A future exporter should run this audit before any learner-state estimator
  consumes generated sequence data.

## 15. Future Implementation Roadmap

Recommended order:

1. Step 161: minimal audit schema / fixtures design
2. Step 162: synthetic learner-state audit fixture files design
3. Step 163: create synthetic audit fixture files
4. Step 164: learner-state sequence no-oracle audit implementation
5. Step 165: smoke tests
6. Later: selective prediction / calibration design
7. Later: estimator prototype

If exporter implementation depends on audit behavior, Step 162 may remain a
design step and audit implementation can move earlier.

Step 161 follow-up: see
[Learner-state sequence audit fixture/schema design](learner_state_sequence_audit_fixture_schema_design.md)
for the future valid and invalid synthetic fixture families, expected
fail-closed results, and safe audit result schema.

Step 162 follow-up: see
[Learner-state sequence audit fixture files design](learner_state_sequence_audit_fixture_files_design.md)
for the future fixture root, directory structure, naming, and file set.

Step 163 follow-up: the initial synthetic audit fixture files are available at
[`tests/fixtures/learner_state_sequence_audit/`](../tests/fixtures/learner_state_sequence_audit/README.md).
They define future pass/fail expectations only; audit code and exporter logic
are still intentionally unimplemented.

## 16. Beginner Notes

An audit is a check that looks for unsafe or invalid data before later tools
trust it.

A no-oracle audit is needed because a future learner-state dataset is useful
only if it does not contain answers, future edits, correction labels, or
post-hoc information in its inputs.

Feature and label mixing is dangerous because it can let a model see the answer
while pretending to predict it.

Future leakage means using information from later in the sequence when building
the current row. That makes temporal prediction circular.

Fail-closed means the audit rejects unknown or suspicious cases instead of
assuming they are safe.

## Related Documents

- [Learner-state sequence schema design](learner_state_sequence_schema_design.md)
- [Learner-state sequence audit fixture/schema design](learner_state_sequence_audit_fixture_schema_design.md)
- [Learner-state sequence audit fixture files design](learner_state_sequence_audit_fixture_files_design.md)
- [Synthetic learner-state sequence dataset design](synthetic_learner_state_sequence_dataset_design.md)
- [Learner-state input representation design](learner_state_input_representation_design.md)
- [Research pipeline next-phase plan](research_pipeline_next_phase_plan.md)
- [No-oracle policy](03_no_oracle_policy.md)
- [Synthetic data policy](12_synthetic_data_policy.md)
- [Synthetic E2E pipeline](synthetic_e2e_pipeline.md)
- [Evaluation spec](evaluation_spec.md)
- [Public release checklist](public_release_checklist.md)
