# Learner-State Sequence Exporter Edge Fixture Design

This document designs future exporter-specific edge-case fixtures and test
expansion for the learner-state sequence exporter.

This is design documentation only. It does not create edge-case fixture files,
change exporter code, change tests, train a learner-state estimator, add a
model, add a metric, use real data, or evaluate performance.

## 1. Purpose

The purpose of this document is to define how future edge-case fixtures should
broaden coverage around the minimal learner-state sequence exporter.

The design focuses on:

- exporter-specific valid and invalid fixture families
- safe expected-output contracts for edge cases
- fail-closed test expansion
- no-oracle and no future leakage boundaries
- synthetic-only fixture handling
- safe, count-only output and failure reporting

This document is not a real-data readiness claim and does not provide model
performance evidence.

## 2. Current Exporter State

Current state:

- `python/learner_state/sequence_exporter.py` exists.
- The initial exporter input fixture root exists at
  `tests/fixtures/learner_state_sequence_exporter/`.
- The current valid fixture is
  `valid/minimal_single_participant/`.
- The minimal exporter writes separated `features.jsonl`, `labels.jsonl`, and
  `manifest.json` files to a caller-provided output directory.
- Generated outputs pass the existing `learner_state.sequence_audit` check.
- Exporter tests exist under `python/learner_state/tests/`.
- The exporter currently has no CLI, Makefile target, or release-quality wrapper
  integration.
- Exporter-specific edge-case fixtures do not exist yet.

The current fixture coverage is intentionally small and centered on one valid
synthetic path.

## 3. Fixture Root / Placement

Future edge-case fixtures should live under the existing exporter fixture root:

`tests/fixtures/learner_state_sequence_exporter/`

Suggested future placement:

```text
tests/fixtures/learner_state_sequence_exporter/
  valid/
    multi_episode_single_task/
    multi_task_split_ready/
    multi_task_same_participant/
    two_participants_learner_disjoint/
    past_window_boundary_reset/
  invalid/
    missing_safe_episodes/
    malformed_jsonl/
    empty_input/
    unknown_schema_version/
    label_in_feature_input/
    future_window_input/
    split_leakage_input/
    mismatched_join_keys/
    missing_expected_output_contract/
    unsafe_path/
    raw_text_field/
    real_participant_id/
```

This step does not create these directories or files.

The exporter input fixture root should remain separate from
`tests/fixtures/learner_state_sequence_audit/`. Audit fixtures are already in
exported feature/label/manifest shape; exporter fixtures are upstream inputs
that the exporter turns into those outputs.

## 4. Valid Edge Fixtures

Future valid edge fixtures should broaden coverage without introducing real
data or raw text.

| Fixture | Purpose | Expected behavior |
| --- | --- | --- |
| `valid/multi_episode_single_task/` | Exercises longer ordered episode sequences within one task | Exports all episodes in order, computes past-only features, and passes audit |
| `valid/multi_task_same_participant/` | Checks task boundaries for one synthetic participant | Resets task-scoped fields at task boundaries without participant leakage |
| `valid/two_participants_learner_disjoint/` | Exercises learner-disjoint split metadata | Keeps synthetic participants in disjoint groups and passes split safety checks |
| `valid/split_ready_train_val_test/` | Exercises train/validation/test metadata | Uses synthetic split metadata that does not depend on labels or outcomes |
| `valid/past_window_boundary_reset/` | Tests rolling-window reset behavior | Uses only past/current information and resets windows at participant/session/task boundaries |

The initial priority among valid edge fixtures should be
`valid/past_window_boundary_reset/`, because future learner-state features are
especially sensitive to accidental future leakage.

## 5. Invalid Edge Fixtures

Future invalid fixtures should be small, synthetic-only, and focused on one
failure boundary per case.

| Fixture | Intended failure | Expected reason code |
| --- | --- | --- |
| `invalid/missing_safe_episodes/` | Required input file is absent | `missing_input_file` |
| `invalid/malformed_jsonl/` | A JSONL input cannot be parsed | `malformed_input` |
| `invalid/empty_input/` | Required JSONL input has no usable rows | `empty_input` |
| `invalid/unknown_schema_version/` | Input declares an unsupported version | `unknown_input_schema_version` |
| `invalid/missing_expected_output_contract/` | Fixture lacks a safe expected-output contract | `missing_contract` |
| `invalid/label_in_feature_input/` | Feature-side input includes expected-action information | `exporter_forbidden_field` |
| `invalid/future_window_input/` | Input includes future episode/action fields | `exporter_future_leakage` |
| `invalid/split_leakage_input/` | Same synthetic participant appears across incompatible splits | `exporter_split_leakage` |
| `invalid/mismatched_join_keys/` | Safe episodes, scores, and labels cannot be joined safely | `join_key_mismatch` |
| `invalid/unsafe_path/` | Fixture metadata references unsafe source categories | `unsafe_path` |
| `invalid/raw_text_field/` | Input includes raw learner text or raw context text | `exporter_forbidden_field` |
| `invalid/real_participant_id/` | Input includes real participant identifier fields | `exporter_forbidden_field` |

Invalid fixtures should not include real participant data, private paths, raw
learner text, or full generated output bodies. Unsafe-path cases should use
synthetic path strings only.

## 6. Failure Reason Code Design

Exporter-specific failures should be distinguishable from audit failures.

Existing audit reason codes include:

- `forbidden_field`
- `label_in_feature`
- `future_leakage`
- `split_leakage`
- `unsafe_path`
- `manifest_body_leakage`
- `missing_schema_version`
- `unsafe_join_key`

Exporter-specific reason code candidates:

- `missing_input_file`
- `malformed_input`
- `empty_input`
- `unknown_input_schema_version`
- `join_key_mismatch`
- `missing_contract`
- `contract_mismatch`
- `exporter_forbidden_field`
- `exporter_future_leakage`
- `exporter_split_leakage`
- `audit_failed_after_export`

Policy:

- Use exporter-specific codes for failures detected before output generation.
- Use existing audit codes for generated-output audit violations.
- If generated outputs fail audit, the exporter may report
  `audit_failed_after_export` plus safe audit reason codes.
- Do not report raw rows, raw labels, raw manifests, candidate score rows, or
  private paths in failure messages.
- Unknown or ambiguous failures should fail closed with a safe category.

## 7. Expected Output Contract Expansion

Future `expected_output_contract.json` files may include:

- expected output file presence
- expected feature row count
- expected label row count
- expected participant count
- expected session count
- expected task count
- expected split counts
- expected past-window feature availability
- expected audit status
- expected failure reason code for invalid exporter fixtures
- expected content suppression flag
- expected no-raw-rows flag
- expected schema version names

Forbidden in expected output contracts:

- full `features.jsonl` body
- full `labels.jsonl` body
- full `manifest.json` body dump
- raw learner text
- raw candidate text
- private paths
- expected-action bodies beyond safe label-category metadata needed for tests
- performance metrics

Contracts should compare safe counts, versions, flags, and reason codes rather
than complete row bodies.

## 8. Test Expansion Design

Future exporter tests should cover:

- valid fixtures export successfully and pass the sequence audit
- invalid fixtures fail before writing outputs when required inputs are missing,
  malformed, empty, or unsupported
- invalid fixtures fail after generated-output audit when the exporter produces
  unsafe output
- output directories are temporary or explicit caller-provided directories
- fixture discovery is deterministic
- contract mismatches fail safely
- failure messages include safe case names and reason codes only
- no raw JSONL rows, labels, manifest bodies, or private paths are printed
- past-only rolling-window features reset at participant, session, and task
  boundaries
- generated outputs are never committed from `tmp/`, `manual_outputs/`, or
  private local paths

At least one future test should directly exercise the past-only boundary reset
because this is the most likely place for accidental future leakage.

## 9. Output Safety

Exporter edge-case testing should preserve these output rules:

- no raw rows in stdout
- no JSONL body in public docs
- no label body
- no manifest body
- no candidate score rows
- no raw learner text
- no private absolute paths
- no full stack trace with row content
- safe summaries only
- count-only public results
- temporary output directories only for generated files

Docs may name fixture categories, file names, field families, counts, and reason
codes. Docs must not paste fixture row bodies or generated output bodies.

## 10. No-Oracle / Leakage Policy

Future exporter fixtures and tests must maintain:

- synthetic-only inputs
- no real participant data
- no raw learner text
- no `final_text`
- no `observed_after_text`
- no `gold_label`
- no teacher or human correction fields
- no post-hoc annotation fields
- no future edit or future episode fields
- no final outcome features
- expected action remains labels-only
- no expected-action aggregates in features
- split assignment is not label-derived or outcome-derived
- safe join keys only
- generated outputs pass no-oracle audit before use

Expected action may be used as an evaluation-only label source in
`labels_source.jsonl`-style inputs. It must not become a feature, candidate
generation input, scorer input, ranking feedback, or split assignment signal.

## 11. Prioritization

Recommended high-priority fixtures:

1. `invalid/missing_safe_episodes/`
2. `invalid/malformed_jsonl/`
3. `invalid/empty_input/`
4. `invalid/unknown_schema_version/`
5. `invalid/label_in_feature_input/`
6. `valid/past_window_boundary_reset/`

These should come first because they protect the exporter from common
fail-closed and no-oracle mistakes before broader dataset shapes are added.

Recommended medium-priority fixtures:

1. `invalid/split_leakage_input/`
2. `invalid/mismatched_join_keys/`
3. `valid/multi_task_same_participant/`
4. `valid/two_participants_learner_disjoint/`

These broaden grouping and join-key coverage after basic input robustness is in
place.

Recommended later fixtures:

1. `valid/split_ready_train_val_test/`
2. `invalid/unsafe_path/`
3. `invalid/raw_text_field/`
4. `invalid/real_participant_id/`

These remain important but can wait until the exporter failure-reporting path is
stable enough to keep all errors public-safe.

## 12. Relation To Existing Pipeline

This design relates to:

- exporter input fixtures in
  `tests/fixtures/learner_state_sequence_exporter/`
- `python/learner_state/sequence_exporter.py`
- `learner_state.sequence_audit`
- audit fixtures in `tests/fixtures/learner_state_sequence_audit/`
- existing Python exporter tests
- Makefile and release-quality infrastructure
- future exporter CLI work

The edge fixtures should not change candidate generation, scorer formulas,
tie-breaks, diagnostic logic, audit fixtures, Makefile targets, wrapper scripts,
workflow files, or manifest schemas.

## 13. Future Roadmap

Recommended next steps:

1. Step 180: create exporter edge-case fixtures.
2. Step 181: implement exporter edge-case tests.
3. Step 182: learner-state sequence exporter CLI design.
4. Step 183: learner-state sequence exporter CLI implementation.
5. Step 184: Makefile target design or integration review.
6. Later: release-quality integration review after CLI and tests stabilize.

Possible adjustment: implement the highest-priority invalid fixtures first and
delay CLI work until fail-closed exporter behavior is stable.

Step 180 implementation note: the initial exporter edge-case fixture files now
exist under
[`tests/fixtures/learner_state_sequence_exporter/`](../tests/fixtures/learner_state_sequence_exporter/README.md).
The added cases are `valid/past_window_boundary_reset/` plus invalid
`missing_safe_episodes/`, `malformed_jsonl/`, `empty_input/`,
`unknown_schema_version/`, and `label_in_feature_input/`. They are synthetic
fixture files for future tests only; exporter code, exporter tests, audit code,
Makefile, workflow, and release-quality wrapper behavior are unchanged.

Step 181 implementation note: exporter edge-case tests now exercise the Step
180 fixtures. The tests export `valid/past_window_boundary_reset/`, verify
safe/count-only generated outputs, confirm learner-state sequence audit success,
and check task-boundary past-window reset behavior. The invalid fixtures are
loaded through fail-closed exporter failure handling and compared with their
safe `expected_failure_contract.json` reason codes. Test failure summaries do
not include JSONL row bodies, malformed-line bodies, label bodies, manifest
bodies, or private paths.

## 14. Beginner Notes

An edge-case fixture is a small synthetic test case designed to exercise an
unusual or failure-prone situation.

Valid fixtures show that the exporter can handle more realistic safe structures,
such as multiple episodes or boundary resets.

Invalid fixtures are intentionally broken. They are useful because they prove
the exporter fails safely when inputs are missing, malformed, leaky, or
unsupported.

Malformed, missing, and unknown-version cases should be tested early because
they verify that the exporter does not silently accept bad inputs.

Raw output is restricted because tests and docs can become public surfaces. The
safe pattern is to report counts, categories, and reason codes rather than row
contents.

## 15. Related Documents

- [Learner-state sequence exporter design](learner_state_sequence_exporter_design.md)
- [Learner-state sequence exporter input fixture design](learner_state_sequence_exporter_input_fixture_design.md)
- [Learner-state sequence schema design](learner_state_sequence_schema_design.md)
- [Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
- [Learner-state sequence audit implementation design](learner_state_sequence_audit_implementation_design.md)
- [Milestone 06 learner-state audit infrastructure recap](milestone_06_learner_state_audit_infrastructure_recap.md)
- [Public release checklist](public_release_checklist.md)
