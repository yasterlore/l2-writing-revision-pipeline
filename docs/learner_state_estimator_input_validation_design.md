# Learner-State Estimator Input Validation Design

This document designs future validation for learner-state estimator inputs. It
describes the validation order, safe failure policy, result schema, fixture
expected-result matching, sequence grouping checks, split checks, and
no-oracle/leakage checks to apply before any estimator input loader or
learner-state estimator is implemented.

Step195 follow-up: the minimal synthetic-only estimator input validator/loader
is implemented in `python/learner_state/estimator_input.py`, with fixture-based
tests in `python/learner_state/tests/test_estimator_input.py`. The
implementation returns safe validation metadata, checks the Step193 fixtures,
and matches `expected_input_validation_result.json` without printing row
bodies.

Step196 follow-up: the command-line interface design for this validator is
recorded in
[learner-state estimator input validator CLI design](learner_state_estimator_input_validator_cli_design.md).
Step197 implements the minimal `python -m learner_state.estimator_input` CLI
and `python/learner_state/tests/test_estimator_input_cli.py`. No Makefile
target, release-quality integration, or workflow change is added by Step197.

This document remains the design reference for validation. The implementation
does not add a learner-state estimator, estimator training code, selective
prediction, calibration, a new model, or a new metric. It is not performance
evaluation and it is not a real-data readiness claim.

## 1. Purpose

The purpose of estimator input validation is to fail closed on unsafe,
malformed, or inconsistent exported-shape inputs before they can be treated as
estimator-ready.

The design defines:

- validation scope and non-scope
- recommended validation order
- safe validation result metadata
- failure reason code mapping
- fixture expected-result matching
- feature/label join checks
- sequence grouping checks
- split leakage checks
- no-oracle and future-leakage checks
- path safety checks
- future fixture test strategy

## 2. Current Assets

Current learner-state estimator input assets:

- [Learner-state estimator input contract design](learner_state_estimator_input_contract_design.md)
- [Learner-state estimator input fixture design](learner_state_estimator_input_fixture_design.md)
- fixture root: `tests/fixtures/learner_state_estimator_input/`
- root README: `tests/fixtures/learner_state_estimator_input/README.md`
- valid fixture: `valid/minimal_single_sequence/`
- invalid fixtures:
  - `invalid/label_in_features/`
  - `invalid/missing_label_row/`
  - `invalid/extra_label_row/`
  - `invalid/join_key_mismatch/`
  - `invalid/split_leakage_same_participant/`
  - `invalid/future_feature_leakage/`
  - `invalid/forbidden_feature_field/`
  - `invalid/unknown_schema_version/`
- expected validation contract file:
  - `expected_input_validation_result.json`
- implementation:
  - `python/learner_state/estimator_input.py`
- tests:
  - `python/learner_state/tests/test_estimator_input.py`

The fixture files are synthetic-only and exported-shape. Public docs should
refer to file names, counts, and reason codes, not row bodies.

## 3. Validation Scope

Validation should inspect:

- `features.jsonl`
- `labels.jsonl`
- `manifest.json`
- `expected_input_validation_result.json` for fixture tests
- schema versions
- join keys
- sequence order
- split metadata
- forbidden feature fields
- no-oracle and future-leakage fields
- safe output construction

Validation should not do:

- model training
- metric evaluation
- calibration
- estimator correctness assessment
- real-data readiness review
- production data collection validation
- F1, accuracy, ECE, AURCC, or other performance reporting

## 4. Recommended Validation Order

Recommended order:

1. Path safety
2. File presence
3. JSON / JSONL parse
4. Non-empty required inputs
5. Schema version checks
6. Manifest count consistency
7. Forbidden field checks
8. Label-feature separation checks
9. Join completeness
10. Sequence grouping and ordering
11. Split leakage checks
12. Future leakage checks
13. Safe output construction

Rationale:

- Path and file checks should run first because they are cheap and prevent
  accidental private or missing input access.
- Parse and non-empty checks should happen before semantic validation.
- Schema version checks should happen before interpreting fields.
- Manifest count checks should happen before trusting declared metadata.
- Forbidden field and label-feature separation checks should happen before
  join and sequence logic to prevent unsafe data from being normalized as if it
  were valid.
- Join, sequence, and split checks depend on parsed safe keys.
- Future leakage checks can use both field names and sequence metadata.
- Safe output construction should be last so every failure path reports only
  safe metadata.

## 5. Validation Result Schema

Future validator results should expose safe metadata only:

- `validation_schema_version`
- `validation_status`
- `reason_codes`
- `failure_categories`
- `failed_checks`
- `checked_files_count`
- `feature_row_count`
- `label_row_count`
- `sequence_count`
- `split_counts`
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only_checked`
- `no_oracle_checked`

`failed_checks` should contain only safe check names, categories, file roles,
and reason codes. It must not contain raw lines, row bodies, or private paths.

Validation result output must not include:

- feature row body
- label row body
- manifest body dump
- expected-action body
- raw learner text
- private paths
- performance metrics

## 6. Failure Reason Code Mapping

Fixture-mapped reason codes:

| Fixture | Reason code | Category | Stage |
| --- | --- | --- | --- |
| `invalid/label_in_features` | `label_in_features` | `feature_label_separation` | `input_validation` |
| `invalid/missing_label_row` | `missing_label_row` | `join_completeness` | `input_validation` |
| `invalid/extra_label_row` | `extra_label_row` | `join_completeness` | `input_validation` |
| `invalid/join_key_mismatch` | `join_key_mismatch` | `join_completeness` | `input_validation` |
| `invalid/split_leakage_same_participant` | `split_leakage` | `split_validation` | `input_validation` |
| `invalid/future_feature_leakage` | `future_feature_leakage` | `future_leakage` | `input_validation` |
| `invalid/forbidden_feature_field` | `forbidden_feature_field` | `forbidden_field` | `input_validation` |
| `invalid/unknown_schema_version` | `unknown_schema_version` | `schema_version` | `input_validation` |

General reason codes:

- `missing_input_file`
- `malformed_input`
- `empty_input`
- `manifest_count_mismatch`
- `sequence_order_error`
- `boundary_reset_error`
- `unsafe_path`

Reason codes should be stable, short, and safe for stdout, JSON summaries, and
unit test assertion messages.

## 7. Expected Validation Result Matching

Fixture tests should:

- load `expected_input_validation_result.json`
- compare `validation_status`
- compare `expected_failure_reason`
- compare `expected_failure_category`
- compare `expected_stage`
- compare row, sequence, and split counts when present
- compare `content_suppressed`
- compare `no_raw_rows`
- compare `synthetic_only`

Mismatch should fail tests safely. Failure messages should name the case label,
field name, expected safe value category, and actual safe value category. They
should not print JSONL row bodies, manifest bodies, label bodies, expected
action bodies, malformed line contents, raw text, or private paths.

## 8. Feature/Label Join Validation

Join keys:

- `synthetic_participant_id`
- `synthetic_session_id`
- `synthetic_task_id`
- `micro_episode_id`
- `episode_order_index`

Future validation should require:

- one feature row has exactly one matching label row for supervised fixtures
- missing label row fails with `missing_label_row`
- extra label row fails with `extra_label_row`
- mismatched key fails with `join_key_mismatch`
- duplicate feature join keys fail
- duplicate label join keys fail
- label values do not appear in feature rows

Unlabeled mode can be considered later, but it should be explicit and separate
from supervised fixture validation.

## 9. Sequence Grouping Validation

Future validation should:

- group by participant, session, and task
- order by `episode_order_index`
- require monotonic order within a sequence
- fail duplicate order indices
- verify boundary reset metadata if available
- confirm no future access is required to construct current-row features
- compare validated `sequence_count` with manifest `sequence_count`
- allow the train-only minimal fixture to pass

The validator should treat sequence order errors as structural failures. It
should not reorder rows silently and claim success if ordering metadata is
inconsistent.

## 10. Split Validation

Future validation should:

- default to learner-disjoint split checks
- fail if a participant crosses train/validation/test
- verify split counts against the manifest
- require split assignment to be independent of labels and outcomes
- report split leakage with safe counts only
- allow train-only fixtures as valid smoke cases

Validation/test label usage policy is related but out of scope for this
validator. Calibration and threshold tuning rules should be handled in a later
selective prediction / calibration design.

## 11. No-Oracle / Leakage Validation

Feature rows must not include:

- `expected_action`
- `expected_action_family`
- label aggregates
- future episode fields
- future action fields
- `final_text`
- `observed_after_text`
- `gold_label`
- raw learner text
- teacher/human correction
- real participant IDs

Expected action may appear in `labels.jsonl` as a separated synthetic
evaluation/training target. It must not be used as scoring feedback.

## 12. Path Safety Validation

Future validation should reject input paths containing:

- `real_data`
- `participant_data`
- `private_data`
- `manual_outputs`

Fixture paths under `tests/fixtures` are allowed for synthetic tests. Output
should not expose private absolute paths. If a path must be summarized, the
validator should use a safe path category, fixture case label, or sanitized
basename.

## 13. Fixture Test Design

Future fixture tests should:

- discover fixture directories deterministically
- require every fixture to have `expected_input_validation_result.json`
- assert the valid fixture passes
- assert each invalid fixture fails with its expected reason
- exercise all expected result contracts
- keep failure messages safe
- avoid printing raw rows
- avoid printing full manifest bodies
- avoid printing label bodies

The first test suite should focus on loader/validator safety, not model
training or estimator quality.

## 14. Relation to Existing Pipeline

This validation layer sits after exporter output and before any estimator:

- `sequence_exporter` generates exported-shape synthetic feature, label, and
  manifest files.
- `learner_state.sequence_audit` checks exported learner-state sequence safety.
- Estimator input fixtures provide exported-shape inputs for validator tests.
- Makefile and release-quality wrapper currently cover audit and exporter CLI
  smoke checks.
- A future loader should validate estimator input before constructing estimator
  batches.

This design does not modify exporter code, audit code, Makefile targets,
release-quality wrapper behavior, candidate generation, OT scoring, scoring
formula, tie-breaks, or manifest schema.

## 15. Implementation Roadmap

Recommended order:

1. Step195: minimal estimator input validator/loader implementation. Complete.
2. Step196: estimator input validator CLI design. Complete.
3. Step197: minimal estimator input validator CLI implementation. Complete.
4. Step198: estimator input validator Makefile target design. Complete.
5. Step199: standalone Makefile target implementation. Complete.
6. Step200: release-quality integration design after local target log-safety
   review.
7. Later: selective prediction / calibration design.
8. Later: estimator prototype design.

The first implementation should remain a synthetic-only validator/loader. It
should not introduce model training, metrics, calibration, or real-data
handling.

## 16. Beginner Notes

Validation means checking input files before trusting them. Here, validation
answers: "Can a future learner-state estimator safely read these files?"

Validation comes before the loader because a loader that silently accepts bad
inputs can make later model behavior misleading.

A join check makes sure every feature row and label row refer to the same
synthetic episode using safe keys.

A split leakage check makes sure the same synthetic participant does not appear
in both training and test-like splits.

Fail-closed means unsafe or unclear input becomes a failure, not a warning and
not a silent pass.

## 17. Related Documents

- [Learner-state estimator input contract design](learner_state_estimator_input_contract_design.md)
- [Learner-state estimator input fixture design](learner_state_estimator_input_fixture_design.md)
- [Learner-state estimator input fixtures](../tests/fixtures/learner_state_estimator_input/README.md)
- [Learner-state estimator input validator CLI design](learner_state_estimator_input_validator_cli_design.md)
- [Learner-state estimator input validator Makefile target design](learner_state_estimator_input_validator_makefile_target_design.md)
- `python/learner_state/estimator_input.py`
- `python/learner_state/tests/test_estimator_input.py`
- `python/learner_state/tests/test_estimator_input_cli.py`
- [Learner-state sequence exporter design](learner_state_sequence_exporter_design.md)
- [Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
- [Public release checklist](public_release_checklist.md)
