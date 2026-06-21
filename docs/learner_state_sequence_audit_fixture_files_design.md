# Learner-State Sequence Audit Fixture Files Design

This document designs the future placement, naming, and file organization for
synthetic learner-state sequence audit fixtures.

This is design documentation only. It does not create fixture files, fixture
directories, audit code, schema code, a sequence exporter, a learner-state
estimator, a model, a metric, or a production data pipeline. It does not change
candidate generation, OT scoring, scoring formula, tie-break behavior, existing
manifest schemas, Makefile targets, workflows, scripts, or tests. It is not a
performance evaluation.

## 1. Purpose

The purpose of this document is to decide how future synthetic learner-state
audit fixture files should be organized before any files are added.

The design should make future fixtures:

- synthetic-only
- small and reviewable
- no-oracle safe by construction, except for intentional invalid cases
- easy for tests to discover
- safe for public repository review without pasting row bodies into docs

Public docs should describe field-level shape, case names, reason codes, and
count-only expectations. They should not paste raw fixture bodies.

## 2. Fixture Root Candidate

Candidate roots:

| Candidate root | Pros | Cons | Fit |
| --- | --- | --- | --- |
| `fixtures/learner_state_sequence_audit/` | Short and visible | New top-level fixture convention that may not match existing project layout | Not preferred initially |
| `python/learner_state/tests/fixtures/` | Close to future Python audit tests | May hide cross-pipeline synthetic fixtures inside one package | Good for package-local helper fixtures later |
| `python/test_support/fixtures/learner_state_sequence_audit/` | Close to shared Python test support | Still Python-centered and less visible to Rust or shell checks | Possible later if helper libraries own fixture loading |
| `tests/fixtures/learner_state_sequence_audit/` | Matches existing synthetic fixture area and is language-neutral | Requires careful naming to avoid confusion with raw event fixtures | Recommended |
| `docs/examples/` | Easy to browse in docs | Encourages body snippets in docs and blurs examples with test fixtures | Avoid |

Recommended future root:

`tests/fixtures/learner_state_sequence_audit/`

Rationale:

- existing project fixtures already live under `tests/fixtures`
- the audit boundary is cross-pipeline, not Python-only
- future Rust, Python, shell, or Makefile checks can all reference it
- docs can link to the design without copying row bodies

`docs/examples/` should be avoided for audit fixture bodies because it invites
copying JSON or JSONL lines into public documentation. Documentation should
remain field-level and count-only.

## 3. Fixture Directory Structure

Future directory structure candidate:

```text
tests/fixtures/learner_state_sequence_audit/
  valid/
    minimal/
  invalid/
    forbidden_field/
    label_feature_separation/
    future_leakage/
    split_leakage/
    unsafe_path/
    manifest_leakage/
    schema_version/
    join_key_safety/
    public_output_safety/
```

This step does not create these directories.

The structure separates valid fixtures from invalid fixtures and keeps one
failure boundary per directory family. Future tests should be able to run all
valid fixtures as pass cases and all invalid fixtures as fail cases with
expected reason codes.

## 4. Fixture File Set

Each future fixture case may contain:

| File | Role | Public docs policy |
| --- | --- | --- |
| `features.jsonl` | Future synthetic feature rows for the case | Do not paste row body |
| `labels.jsonl` | Evaluation-only synthetic labels separated from features | Do not paste label body |
| `manifest.json` | Count-only metadata, schema versions, paths, and suppression flags | Field overview only |
| `expected_audit_result.json` | Expected pass/fail status and reason code summary | Field overview only |
| `README.md` | Optional per-family explanation with no row dumps | Allowed if short and safe |
| `summary.json` | Optional count-only fixture summary | Count-only only |

The initial implementation does not need every optional file. For the first
fixture pass, `features.jsonl`, `labels.jsonl`, `manifest.json`, and
`expected_audit_result.json` are enough.

## 5. Naming Convention

Future fixture names should be stable and test-friendly.

Rules:

- use snake_case
- use one fixture per failure boundary
- keep valid case names short
- keep invalid case names tied to the reason code or failing boundary
- avoid embedding raw text, labels, or outcomes in names
- avoid timestamps in case names
- add version suffixes only when a schema migration needs side-by-side fixtures
- keep names stable so tests can assert expected reason codes

Example case names, without row bodies:

- `minimal_valid`
- `forbidden_field_final_text`
- `label_in_feature_expected_action`
- `future_leakage_next_episode`
- `split_leakage_same_participant_train_test`
- `unsafe_path_real_data`
- `manifest_body_leakage`
- `missing_schema_version`
- `unsafe_join_key_real_participant_id`

Reason codes may appear in names when it improves clarity, but the authoritative
expected reason code should live in `expected_audit_result.json`.

## 6. Valid Fixture Design

Future valid fixture candidates:

| Fixture | Purpose | Initial priority |
| --- | --- | --- |
| `minimal_valid` | Smallest safe feature/label/manifest set | High |
| `multi_episode_valid` | Past-only sequence ordering across multiple episodes | Later |
| `multi_task_valid` | Task boundaries without leakage | Later |
| `split_valid` | Learner-disjoint split metadata without leakage | Later |

Initial recommendation: create only `minimal_valid` first.

The initial valid fixture should prove that the audit accepts the smallest safe
synthetic shape. It should not attempt to model realistic learner behavior or
demonstrate performance.

## 7. Invalid Fixture Design

Initial invalid fixture candidates:

| Fixture name | Expected reason code | Priority |
| --- | --- | --- |
| `forbidden_field_final_text` | `forbidden_field` | High |
| `label_in_feature_expected_action` | `label_in_feature` | High |
| `future_leakage_next_episode` | `future_leakage` | High |
| `split_leakage_same_participant_train_test` | `split_leakage` | High |
| `unsafe_path_real_data` | `unsafe_path` | High |
| `manifest_body_leakage` | `manifest_body_leakage` | High |
| `missing_schema_version` | `missing_schema_version` | High |
| `unsafe_join_key_real_participant_id` | `unsafe_join_key` | High |

These cover the main Step 161 audit families without requiring a large fixture
surface. Additional fixtures can be added later for unknown schema versions,
raw body output, malformed input, empty input, and public output safety.

## 8. Expected Audit Result File Design

Future `expected_audit_result.json` field candidates:

- `audit_status`
- `expected_failure_code`
- `expected_violation_category`
- `expected_violation_count_min`
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only_expected`

Forbidden fields:

- raw row body
- full error trace
- private path
- row-level raw content
- raw label content
- expected action body
- candidate score rows
- real data

The file should make tests precise without requiring unsafe output. For valid
fixtures, `audit_status` should be `pass` and failure-code fields can be absent
or explicitly empty. For invalid fixtures, `audit_status` should be `fail` and
the expected reason code should be explicit.

## 9. Public Docs Policy

Public docs may include:

- fixture family names
- case names
- failure codes
- violation categories
- count-only summaries
- field-level descriptions

Public docs must not include:

- fixture row bodies
- raw JSONL lines
- raw learner text
- label contents
- expected action body
- candidate score rows
- private paths
- full generated summaries
- performance metrics

The docs should explain the purpose of fixtures without turning docs into a
data dump.

## 10. Test Integration Future Plan

Future test integration should follow these rules:

- audit implementation reads the fixture root
- valid fixtures should pass
- invalid fixtures should fail with expected reason codes
- test failure messages should not print raw rows
- test failure messages should use safe count-only summaries
- safe output scan helpers should inspect audit stdout/stderr where practical
- a future Makefile target can be added only after audit code exists

The first audit tests should prioritize safety boundaries over broad coverage.

## 11. Git / Privacy Policy

Future fixture files must be:

- synthetic-only
- small and reviewable
- intentionally minimal
- free of real data
- free of private paths
- free of raw learner text
- free of generated `tmp/` outputs
- free of `manual_outputs/` contents
- appropriate for Git review

Private/manual outputs must not be committed. Generated outputs under `tmp/`
must not be added to Git.

## 12. Relation to Existing Pipeline

This fixture file design follows from:

- [Learner-state sequence audit fixture/schema design](learner_state_sequence_audit_fixture_schema_design.md)
- [Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
- [Learner-state sequence schema design](learner_state_sequence_schema_design.md)

It also relates to:

- safe output scan helper patterns
- the current no-oracle audit stance
- the synthetic policy checker
- future learner-state sequence audit implementation
- future learner-state sequence exporter implementation
- release-quality wrapper and Makefile support

No existing pipeline behavior changes in this step.

## 13. Future Implementation Roadmap

Recommended order:

1. Step 163: create initial synthetic audit fixture files
2. Step 164: implement learner-state sequence audit
3. Step 165: audit fixture smoke tests
4. Step 166: minimal sequence exporter design or implementation
5. Later: selective prediction / calibration design
6. Later: estimator prototype

If fixture creation exposes ambiguity in file names or expected result fields,
add one more docs-only preflight before implementation.

## 14. Beginner Notes

A fixture file is a small test input saved in the repository.

Docs should not paste fixture bodies because docs are for explanation, not data
storage. Keeping the bodies in fixture files makes review and tests cleaner.

A valid fixture proves the audit can accept a safe case. An invalid fixture is
intentionally broken so the audit can prove it catches a specific unsafe case.

An expected audit result says what the audit should report for a fixture:
usually pass for valid fixtures and fail with a specific reason code for
invalid fixtures.

Small synthetic-only fixtures keep the project reviewable and private-data safe
while the audit is still being designed.

## Related Documents

- [Learner-state sequence audit fixture/schema design](learner_state_sequence_audit_fixture_schema_design.md)
- [Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
- [Learner-state sequence schema design](learner_state_sequence_schema_design.md)
- [Synthetic learner-state sequence dataset design](synthetic_learner_state_sequence_dataset_design.md)
- [Learner-state input representation design](learner_state_input_representation_design.md)
- [No-oracle policy](03_no_oracle_policy.md)
- [Synthetic data policy](12_synthetic_data_policy.md)
- [Synthetic E2E pipeline](synthetic_e2e_pipeline.md)
- [Public release checklist](public_release_checklist.md)
