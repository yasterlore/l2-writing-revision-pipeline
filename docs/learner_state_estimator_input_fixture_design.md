# Learner-State Estimator Input Fixture Design

This document designs future synthetic fixtures for validating the
learner-state estimator input contract. The fixtures would use the same
exported-shape file set as audited learner-state sequence outputs:
`features.jsonl`, `labels.jsonl`, and `manifest.json`, plus a safe expected
validation result contract.

This is design documentation only. It does not create fixture files, implement
an estimator input loader, implement estimator training, add selective
prediction or calibration, add a model, add a metric, or claim real-data
readiness. It is not performance evaluation.

## 1. Purpose

The purpose of estimator input fixtures is to make the future input
loader/validator testable before any learner-state estimator is implemented.

The fixture plan should cover:

- feature/label join completeness
- sequence grouping and deterministic ordering
- split handling and learner-disjoint boundaries
- no-oracle and no-future-leakage checks
- schema compatibility
- safe failure summaries
- count-only expected validation results

The fixtures remain synthetic-only and should not include row bodies in public
documentation.

## 2. One-Sentence Summary

An estimator input fixture is a small synthetic-only test case in exported
learner-state sequence shape that provides feature, label, and manifest files
plus a safe expected validation result for checking joins, sequence grouping,
splits, forbidden fields, and leakage boundaries.

## 3. Fixture Root Candidate

Candidate roots:

| Candidate | Pros | Cons |
| --- | --- | --- |
| `tests/fixtures/learner_state_estimator_input/` | Clear scope, language-neutral, parallel to existing learner-state fixture roots | Adds one more fixture root |
| `tests/fixtures/learner_state_sequence_estimator/` | Emphasizes sequence context | Less direct about fixture purpose |
| `tests/fixtures/learner_state_sequence/estimator_input/` | Groups all sequence work together | Nested root may be less discoverable |
| `python/learner_state/tests/fixtures/` | Close to future Python loader tests | Less language-neutral and less consistent with existing top-level fixture roots |
| `docs/examples/` | Easy to browse | Not appropriate for validation fixtures and risks encouraging body examples in docs |

Recommended initial root:

`tests/fixtures/learner_state_estimator_input/`

This root keeps estimator input fixtures distinct from exporter input fixtures
and audit fixtures while staying under the normal synthetic fixture tree.
`docs/examples/` should be avoided because these files are validation fixtures,
not public examples.

## 4. Fixture Case Structure

Future case layout candidates:

```text
tests/fixtures/learner_state_estimator_input/
  valid/
    minimal_single_sequence/
    past_window_boundary_reset/
    learner_disjoint_split/
  invalid/
    label_in_features/
    missing_label_row/
    extra_label_row/
    join_key_mismatch/
    split_leakage_same_participant/
    future_feature_leakage/
    forbidden_feature_field/
    unknown_schema_version/
```

This step does not create these directories.

## 5. Fixture File Set

Each future fixture case should contain:

| File | Role |
| --- | --- |
| `features.jsonl` | Exported-shape feature rows visible to a future estimator input loader |
| `labels.jsonl` | Separated synthetic expected-action labels for supervised training/evaluation phases |
| `manifest.json` | Count-only metadata, schema versions, synthetic-only status, content suppression, row counts, and split counts |
| `expected_input_validation_result.json` | Safe contract describing expected pass/fail status, counts, split summaries, and reason codes |

Optional:

| File | Role |
| --- | --- |
| `README.md` | Short case-level note about purpose, synthetic-only status, and safety boundaries |

Docs should not paste JSONL rows, feature rows, label rows, manifest bodies, or
expected-action bodies.

## 6. Valid Fixture Design

Initial valid fixture candidate:

`valid/minimal_single_sequence`

Expected shape:

- one synthetic participant
- one session
- one task
- two or three ordered episodes
- complete feature/label joins
- deterministic sequence order by `episode_order_index`
- manifest row counts consistent with files
- labels separated from features
- no forbidden feature fields
- train-only split is allowed for smoke validation

Expected validation result:

- `validation_status: pass`
- expected feature row count
- expected label row count
- expected sequence count
- expected split counts
- `content_suppressed: true`
- `no_raw_rows: true`
- `synthetic_only: true`

This fixture checks the happy path for a future loader. It is not training data
quality evidence.

## 7. Invalid Fixture Design

Future invalid fixtures and expected failure meanings:

| Fixture | Intended violation | Expected failure reason |
| --- | --- | --- |
| `invalid/label_in_features` | Feature row contains `expected_action` or `expected_action_family` | `label_in_features` |
| `invalid/missing_label_row` | Feature row has no matching label row | `missing_label_row` |
| `invalid/extra_label_row` | Label row has no matching feature row | `extra_label_row` |
| `invalid/join_key_mismatch` | Safe join keys disagree between feature and label files | `join_key_mismatch` |
| `invalid/split_leakage_same_participant` | Same participant appears across train/test or train/validation | `split_leakage` |
| `invalid/future_feature_leakage` | Feature row includes future episode/action aggregate | `future_feature_leakage` |
| `invalid/forbidden_feature_field` | Feature row includes `final_text`, `observed_after_text`, or `gold_label` | `forbidden_feature_field` |
| `invalid/unknown_schema_version` | Feature, label, or manifest schema version is unknown | `unknown_schema_version` |

Invalid fixtures should fail closed with safe reason codes. They should not
print row bodies, malformed line contents, raw text, private paths, or
expected-action bodies.

## 8. Expected Validation Result Design

Future `expected_input_validation_result.json` should contain safe metadata
only:

- `validation_status`
- `expected_failure_reason`
- `expected_failure_category`
- `expected_stage`
- `expected_sequence_count`
- `expected_feature_row_count`
- `expected_label_row_count`
- `expected_split_counts`
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only`

It must not contain:

- full feature rows
- full label rows
- manifest body dumps
- raw learner text
- expected-action bodies
- private absolute paths
- performance metrics

For passing fixtures, failure fields can be absent or set to safe null-like
values. For failing fixtures, count fields should remain safe and optional if
the loader is expected to fail before counting all rows.

## 9. Failure Reason Code Design

Future estimator-input-specific reason code candidates:

- `label_in_features`
- `missing_label_row`
- `extra_label_row`
- `join_key_mismatch`
- `split_leakage`
- `future_feature_leakage`
- `forbidden_feature_field`
- `unknown_schema_version`
- `manifest_count_mismatch`
- `sequence_order_error`
- `boundary_reset_error`
- `unsafe_path`
- `malformed_input`
- `empty_input`

Relationship to existing reason codes:

- Existing learner-state audit codes detect no-oracle and exported-output
  safety issues.
- Exporter-specific reason codes detect upstream fixture/export failures.
- Estimator-input reason codes should describe loader contract failures after
  exported-shape files exist.
- If a violation is already covered by `learner_state.sequence_audit`, the
  future loader may either reuse the audit reason code or wrap it under an
  estimator-input stage such as `audit_failed_before_load`.

Reason codes should be stable, short, and safe to print.

## 10. Sequence Grouping Validation

Future validation should:

- group by `participant_id`, `session_id`, and `task_id`
- sort by `episode_order_index`
- require monotonic order within each sequence
- fail on duplicate `episode_order_index` within a sequence
- reset sequence state at task boundaries
- forbid future episode access in current-row features
- compare manifest sequence counts against validated sequence counts

The `past_window_boundary_reset` valid fixture can later verify that prior
episode summaries reset at a task boundary.

## 11. Split Validation

Future validation should:

- use learner-disjoint split as the default
- fail if the same participant appears in train and test
- fail if the same participant appears in train and validation
- require split assignment to be independent of labels and outcomes
- verify split counts against the manifest
- allow train-only fixtures as minimal smoke cases
- avoid using validation/test labels for tuning in this contract

This fixture layer validates split structure. It does not implement model
selection, threshold tuning, or calibration.

## 12. No-Oracle / Leakage Checks

Estimator input fixtures should support future checks for:

- no `expected_action` in features
- no `expected_action_family` in features
- no label aggregates in features
- no future episode/action fields
- no `final_text`
- no `observed_after_text`
- no `gold_label`
- no raw learner text
- no teacher/human correction
- no real participant IDs

Expected action remains label/evaluation side only. It is not scoring feedback.

## 13. Relation to Exporter Fixtures

Exporter fixtures and estimator input fixtures serve different boundaries.

- Exporter fixtures test generation from upstream synthetic inputs into
  `features.jsonl`, `labels.jsonl`, and `manifest.json`.
- Estimator input fixtures test loading and validating exported-shape outputs.
- Estimator input fixtures may be generated by the exporter in a future step,
  but initial fixture design can be explicit and minimal.
- Both fixture families must keep raw body content out of public docs.

This separation keeps exporter correctness and estimator input validation from
being conflated.

## 14. Future Implementation Roadmap

Recommended order:

1. Step193: create initial estimator input fixtures.
2. Step194: estimator input validation design.
3. Step195: minimal estimator input loader/validator implementation.
4. Step196: loader tests.
5. Step197: selective prediction / calibration design.
6. Step198: estimator prototype design.

The roadmap intentionally keeps fixture creation and validation design ahead of
estimator implementation.

## 15. Beginner Notes

An estimator input fixture is a small synthetic test folder that looks like the
files a future estimator loader will read. It helps prove the loader rejects
unsafe or inconsistent inputs before any model exists.

Exporter fixtures start from upstream synthetic inputs and test whether the
exporter can produce separated outputs. Estimator input fixtures start at the
exported-output boundary and test whether those outputs can be loaded safely.

Feature/label join means matching one feature row with its label row using safe
keys such as participant, session, task, micro-episode, and episode order.

Split leakage means information crosses train, validation, or test boundaries.
For this project, the same synthetic participant should not appear in multiple
splits.

Expected validation results should use counts and reason codes instead of full
row bodies because tests only need to know whether validation passed or failed,
not expose the underlying rows.

## 16. Related Documents

- [Learner-state estimator input contract design](learner_state_estimator_input_contract_design.md)
- [Milestone 07 learner-state sequence exporter infrastructure recap](milestone_07_learner_state_sequence_exporter_infrastructure_recap.md)
- [Learner-state sequence exporter design](learner_state_sequence_exporter_design.md)
- [Learner-state sequence schema design](learner_state_sequence_schema_design.md)
- [Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
- [Public release checklist](public_release_checklist.md)
