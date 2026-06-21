# Learner-State Sequence Audit Fixture Schema Design

This document designs the future synthetic fixtures and audit result schema for
the learner-state sequence no-oracle audit.

This is design documentation only. It does not create fixture files, implement
audit code, implement schema code, implement a sequence exporter, implement a
learner-state estimator, add a model, add a metric, or change production data
handling. It does not change candidate generation, OT scoring, scoring formula,
tie-break behavior, existing manifest schemas, Makefile targets, workflows,
scripts, or tests. It is not a performance evaluation.

## 1. Purpose

The purpose of this document is to define what future valid and invalid
synthetic audit fixtures should cover, and what safe audit result schema should
look like.

The fixture plan should let a future audit implementation verify fail-closed
behavior for forbidden fields, label-feature separation, future leakage, split
leakage, synthetic-only paths, manifest leakage, schema versions, join keys,
and public output safety.

The fixtures are synthetic design cases only. This step does not create fixture
files or row bodies.

## 2. Fixture Family Overview

Future audit fixtures should be organized by failure boundary.

| Fixture family | Intended status | Purpose |
| --- | --- | --- |
| Valid minimal fixture | pass | Confirms the smallest safe feature/label/manifest set is accepted |
| Forbidden field fixtures | fail | Confirms oracle, correction, raw text, and real-data fields are rejected |
| Label-feature separation fixtures | fail | Confirms labels cannot appear in feature rows or scorer metadata |
| Future leakage fixtures | fail | Confirms current rows cannot use future episodes or final outcomes |
| Split leakage fixtures | fail | Confirms group splits do not leak synthetic learners or outcome-derived groups |
| Synthetic-only path fixtures | fail or private-only reject | Confirms real/private/manual paths are rejected for public dataset use |
| Manifest leakage fixtures | fail | Confirms manifests suppress row bodies, labels, candidate rows, and private paths |
| Schema version fixtures | fail | Confirms missing, unknown, or mismatched versions fail closed |
| Join key safety fixtures | fail | Confirms join keys do not encode labels, outcomes, raw text, or real IDs |
| Public output safety fixtures | fail | Confirms audit output does not dump unsafe content even on failure |

Each fixture should be tiny, synthetic, and designed to test one primary
boundary at a time.

## 3. Valid Minimal Fixture Design

A future valid minimal fixture should contain only field-level safe structures.
The docs should not paste row bodies.

Minimal components:

- `features.jsonl` with one or more safe feature rows
- `labels.jsonl` with separated synthetic expected action labels
- `manifest.json` with `content_suppressed: true`
- synthetic participant, session, task, and micro-episode identifiers only
- schema versions present
- count-only manifest metadata
- no raw text
- no real data
- no expected action in features
- no private paths
- no candidate score row bodies

Expected audit result: pass.

The valid fixture should prove only that the minimum safe shape is accepted. It
should not imply estimator validity, scoring quality, model quality, or
performance.

## 4. Forbidden Field Fixtures

Invalid fixture examples:

| Fixture idea | Expected result | Reason code |
| --- | --- | --- |
| Feature row includes `final_text` | fail | `forbidden_field` |
| Feature row includes `observed_after_text` | fail | `forbidden_field` |
| Feature row includes `gold_label` | fail | `forbidden_field` |
| Feature row includes `raw_text` | fail | `forbidden_field` |
| Feature row includes `teacher_correction` | fail | `forbidden_field` |
| Feature row includes `human_correction` | fail | `forbidden_field` |
| Manifest includes a raw row body | fail | `manifest_body_leakage` |
| Label row uses a real correction source | fail | `forbidden_field` |

The audit should report category and reason code only. It should not print the
offending row body.

## 5. Label-Feature Separation Fixtures

Invalid fixture examples:

| Fixture idea | Expected result | Reason code |
| --- | --- | --- |
| Feature row includes `expected_action` | fail | `label_in_feature` |
| Feature row includes `expected_action_family` | fail | `label_in_feature` |
| Feature row includes `label_source` | fail | `label_in_feature` |
| Label row includes feature vectors | fail | `feature_in_label` |
| Same file path is used for features and labels | fail | `label_in_feature` |
| Evaluation label is referenced by scoring metadata | fail | `label_in_feature` |

Expected action belongs only in separated label rows for synthetic evaluation.
It must not flow into scorer, candidate, ranking, or feature metadata.

## 6. Future Leakage Fixtures

Invalid fixture examples:

| Fixture idea | Expected result | Reason code |
| --- | --- | --- |
| Current feature includes next episode action | fail | `future_leakage` |
| Current feature includes future edit count | fail | `future_leakage` |
| Rolling window includes future episodes | fail | `future_leakage` |
| Task progress uses final total episode count when future-derived | fail | `future_leakage` |
| Final essay outcome is included | fail | `future_leakage` |

The audit should treat future-derived progress metadata as suspicious unless a
future design proves it can be computed from current or past information only.

## 7. Split Leakage Fixtures

Invalid fixture examples:

| Fixture idea | Expected result | Reason code |
| --- | --- | --- |
| Same synthetic participant appears in train and test | fail | `split_leakage` |
| Same synthetic participant appears in train and validation | fail | `split_leakage` |
| Split assignment uses expected action distribution | fail | `split_leakage` |
| Declared task-disjoint split contains the same task in multiple splits | fail | `split_leakage` |
| Split metadata includes label-derived grouping | fail | `split_leakage` |
| Split metadata includes outcome-derived grouping | fail | `split_leakage` |

Split fixtures should use synthetic IDs only. They should not include real
participant identifiers or private grouping information.

## 8. Synthetic-Only Path Fixtures

Invalid fixture examples:

| Fixture idea | Expected result | Reason code |
| --- | --- | --- |
| Input path includes `real_data` | fail | `unsafe_path` |
| Input path includes `participant_data` | fail | `unsafe_path` |
| Input path includes `private_data` | fail | `unsafe_path` |
| Public manifest includes an absolute user path | fail | `unsafe_path` |
| `manual_outputs` is used as a dataset source | private-only reject or fail | `unsafe_path` |

`manual_outputs` may exist for private/local notes in other workflows, but it
should not be accepted as a public sequence dataset source.

## 9. Manifest Leakage Fixtures

Invalid fixture examples:

| Fixture idea | Expected result | Reason code |
| --- | --- | --- |
| `content_suppressed` is false | fail | `manifest_body_leakage` |
| `synthetic_only` is false | fail | `unsafe_path` |
| Manifest contains row dumps | fail | `manifest_body_leakage` |
| Manifest contains label body | fail | `manifest_body_leakage` |
| Manifest contains candidate score rows | fail | `manifest_body_leakage` |
| Manifest contains private path details | fail | `unsafe_path` |

The manifest should contain count-only metadata and safe paths only. It should
never embed feature, label, or candidate row bodies.

## 10. Schema Version Fixtures

Invalid fixture examples:

| Fixture idea | Expected result | Reason code |
| --- | --- | --- |
| Missing feature schema version | fail | `missing_schema_version` |
| Missing label schema version | fail | `missing_schema_version` |
| Missing manifest schema version | fail | `missing_schema_version` |
| Unknown feature schema version | fail | `unknown_schema_version` |
| Unknown label schema version | fail | `unknown_schema_version` |
| Mismatched versions without migration policy | fail | `unknown_schema_version` |

The future audit should reject unknown or mismatched versions instead of trying
to infer compatibility.

## 11. Join Key Safety Fixtures

Invalid fixture examples:

| Fixture idea | Expected result | Reason code |
| --- | --- | --- |
| Real participant ID is used as a join key | fail | `unsafe_join_key` |
| Join key encodes expected label | fail | `unsafe_join_key` |
| Join key encodes outcome or correctness | fail | `unsafe_join_key` |
| Hash of raw text is used without review | fail | `unsafe_join_key` |

Safe join keys should be stable synthetic IDs. They should not carry semantic
answers, future outcomes, raw text fingerprints, or real identity.

## 12. Audit Result Schema Design

The future audit result should be safe to publish by default.

Allowed fields:

- `audit_schema_version`
- `audit_status`, with values such as `pass` or `fail`
- optional `checked_at`, or omitted if timestamp stability is undesirable
- checked file counts and sanitized file categories
- `violation_count`
- count-only `violation_categories`
- `failed_checks` as category and reason code pairs
- `content_suppressed: true`
- `no_raw_rows: true`
- `synthetic_only_checked`
- `no_oracle_checked`

Forbidden in audit results:

- raw row body
- raw text
- JSONL body
- label body
- candidate score rows
- private absolute paths
- real data

The audit result should remain safe even for failing fixtures.

## 13. Failure Reason Code Design

Recommended reason codes:

| Reason code | Meaning |
| --- | --- |
| `forbidden_field` | A forbidden or suspicious field name was found |
| `label_in_feature` | Label or expected-action information appeared in feature rows |
| `feature_in_label` | Feature values appeared in label rows |
| `future_leakage` | A current row used future or final-outcome information |
| `split_leakage` | Split metadata leaked groups, labels, or outcomes |
| `unsafe_path` | A real, private, manual, or absolute unsafe path was found |
| `manifest_body_leakage` | Manifest embedded row, label, candidate, or raw body content |
| `missing_schema_version` | Required schema version was absent |
| `unknown_schema_version` | Schema version was unknown or incompatible |
| `unsafe_join_key` | Join key encoded identity, label, outcome, or raw text |
| `raw_body_output` | Audit output attempted to print raw body content |
| `malformed_input` | Input shape could not be parsed safely |
| `empty_input` | Required input was empty |
| `no_cases` | No auditable cases were present |

`no_cases` should not become an unconditional pass. A future audit should
decide explicitly whether it is a failure, skip, or not-applicable status for
the specific command.

## 14. Public Summary Policy

Public audit summaries should be count-only.

Allowed:

- audit pass/fail status
- violation counts
- failure categories
- reason codes
- schema version names
- content-suppressed status

Forbidden:

- fixture row dumps
- raw paths
- private paths
- label contents
- expected action bodies
- candidate score rows
- raw text
- performance metrics

The public summary should describe what failed without exposing the data that
failed.

## 15. Relation to Existing Pipeline

This design should reuse existing safety ideas without changing current
behavior.

- Safe output scan helpers can inspire public-safe failure output.
- Current no-oracle audit defines the broader forbidden-field stance.
- Summary manifest validation shows the value of explicit schema versions and
  suppressed content.
- The synthetic policy checker already enforces synthetic-only expectations for
  existing fixtures.
- Makefile and the release-quality wrapper remain support infrastructure.
- A future exporter should emit artifacts that this future audit can check.

No existing scripts, tests, Makefile targets, or manifest schemas are changed
by this design.

## 16. Future Implementation Roadmap

Recommended order:

1. Step 162: create synthetic audit fixture files
2. Step 163: implement learner-state sequence audit
3. Step 164: audit fixture smoke tests
4. Step 165: minimal synthetic sequence exporter design or implementation
5. Later: selective prediction / calibration design
6. Later: estimator prototype

If fixture creation needs another preflight, Step 162 may remain docs-only and
fixture files can be added in a later implementation step.

## 17. Beginner Notes

A fixture is a small example file used to test behavior.

A valid fixture is supposed to pass. An invalid fixture is intentionally broken
so the audit can prove it catches the problem.

Broken synthetic fixtures are useful because they test safety without using
real participant data.

An audit result schema is the shape of the audit report. It defines what the
audit may print when it passes or fails.

Raw rows should not be printed because even synthetic row dumps can normalize a
bad habit that would be unsafe when private data readiness is reviewed later.

## Related Documents

- [Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
- [Learner-state sequence schema design](learner_state_sequence_schema_design.md)
- [Synthetic learner-state sequence dataset design](synthetic_learner_state_sequence_dataset_design.md)
- [Learner-state input representation design](learner_state_input_representation_design.md)
- [No-oracle policy](03_no_oracle_policy.md)
- [Synthetic data policy](12_synthetic_data_policy.md)
- [Synthetic E2E pipeline](synthetic_e2e_pipeline.md)
- [Public release checklist](public_release_checklist.md)
