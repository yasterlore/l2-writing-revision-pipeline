# Learner-State Sequence Audit Implementation Design

This document designs the future implementation of a learner-state sequence
no-oracle audit.

This is design documentation only. It does not implement audit code, schema
code, a sequence exporter, a learner-state estimator, a model, a metric, or a
production data pipeline. It does not change candidate generation, OT scoring,
scoring formula, tie-break behavior, existing manifest schemas, Makefile
targets, workflows, scripts, tests, or fixtures. It is not a performance
evaluation.

## 1. Purpose

The purpose of this document is to specify how the future learner-state sequence
audit should be implemented before code is added.

The implementation should:

- fail closed on malformed, unknown, suspicious, or unsafe input
- keep feature rows, label rows, and manifests separately audited
- compare fixture audit results with `expected_audit_result.json`
- emit safe count-only status
- avoid raw row dumps, label bodies, private paths, and stack traces with
  content

The audit will verify dataset safety boundaries. It will not validate
learner-state model quality, scorer quality, research validity, or production
readiness.

## 2. Current Assets

Current assets for the future implementation:

- [Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
- [Learner-state sequence audit fixture/schema design](learner_state_sequence_audit_fixture_schema_design.md)
- [Learner-state sequence audit fixture files design](learner_state_sequence_audit_fixture_files_design.md)
- [Initial synthetic audit fixture root](../tests/fixtures/learner_state_sequence_audit/README.md)

The fixture root currently contains:

- `valid/minimal`
- invalid forbidden-field fixture
- invalid label-feature separation fixture
- invalid future-leakage fixture
- invalid split-leakage fixture
- invalid unsafe-path fixture
- invalid manifest-leakage fixture
- invalid schema-version fixture
- invalid join-key-safety fixture

Each fixture case has `features.jsonl`, `labels.jsonl`, `manifest.json`, and
`expected_audit_result.json`. Public docs should continue to discuss fixture
case names and reason codes only, not row bodies.

## 3. Recommended Module Location

Candidate locations:

| Location | Pros | Cons | Fit |
| --- | --- | --- | --- |
| `python/learner_state/sequence_audit.py` | Close to future learner-state work; easy JSON/JSONL parsing; easy fixture tests | Python owns initial audit implementation even though future exporter may be cross-language | Recommended initial location |
| `python/learner_state/audit.py` | Shorter name | Less explicit if learner-state gains multiple audit types | Possible later wrapper |
| `python/test_support/learner_state_sequence_audit.py` | Good for tests only | Puts production-intended audit logic in test support | Not preferred |
| Rust CLI | Strong alignment with existing Rust no-oracle audit and safe views | More setup for JSON fixture iteration and Python learner-state pipeline integration | Future option |
| Shell wrapper | Easy to call from Makefile | Poor fit for structured JSON/JSONL validation and nested field checks | Not recommended for core logic |

Initial recommendation: implement the first audit in
`python/learner_state/sequence_audit.py`.

Reasoning:

- fixture-based JSON/JSONL validation is straightforward in Python
- future learner-state dataset/exporter work is likely to need Python-side
  orchestration
- tests can compare `AuditResult` objects without printing raw rows
- Rust can remain a future option if the audit boundary later moves closer to
  safe view generation

## 4. CLI / API Design

Future CLI candidates:

```bash
python -m learner_state.sequence_audit --features FEATURES --labels LABELS --manifest MANIFEST
python -m learner_state.sequence_audit --fixture-root tests/fixtures/learner_state_sequence_audit
```

Future library API candidates:

- `audit_sequence_dataset(features_path, labels_path, manifest_path) -> AuditResult`
- `audit_fixture_case(case_dir) -> AuditResult`
- `load_expected_audit_result(case_dir) -> ExpectedAuditResult`
- `compare_audit_result(actual, expected) -> MatchResult`

CLI mode should print only a safe summary or safe JSON result. Library mode
should return structured result objects that tests can inspect without needing
to parse stdout.

No CLI or API is implemented in this step.

## 5. Input Handling Design

Inputs:

- `features.jsonl`
- `labels.jsonl`
- `manifest.json`
- `expected_audit_result.json`, for fixture tests only

Input rules:

- JSON parse failures fail closed.
- JSONL line parse failures fail closed.
- Missing required files fail closed.
- Empty feature or label files should fail with `empty_input`.
- Empty fixture directories should fail with `no_cases`.
- Unknown file extensions should be ignored only if explicitly out of scope;
  otherwise they should fail closed in fixture mode.
- Errors should report file category and reason code, not raw row body.
- Paths should be sanitized before public output.

The audit should retain enough internal location metadata for debugging, but
public output should stay count-only and content-suppressed.

## 6. Audit Checks To Implement First

Initial checks should map directly to the Step 163 fixtures.

| Check | Representative fixture | Expected code |
| --- | --- | --- |
| valid minimal shape | `valid/minimal` | pass |
| forbidden field in feature row | `invalid/forbidden_field/final_text` | `forbidden_field` |
| expected action in feature row | `invalid/label_feature_separation/expected_action_in_feature` | `label_in_feature` |
| future action in current feature row | `invalid/future_leakage/next_episode_action` | `future_leakage` |
| same synthetic participant in train and test | `invalid/split_leakage/same_participant_train_test` | `split_leakage` |
| unsafe real-data-like source path | `invalid/unsafe_path/real_data_path` | `unsafe_path` |
| manifest embeds body-like content | `invalid/manifest_leakage/body_leakage` | `manifest_body_leakage` |
| missing feature schema version | `invalid/schema_version/missing_feature_schema_version` | `missing_schema_version` |
| real participant ID used as join key | `invalid/join_key_safety/real_participant_id` | `unsafe_join_key` |

The first implementation should be intentionally narrow. It should prove the
fail-closed surface before adding broader schema semantics.

## 7. Audit Result Schema

Safe result fields:

- `audit_schema_version`
- `audit_status`
- `violation_count`
- `violation_categories`
- `failed_checks`
- `checked_files_count`
- `content_suppressed`
- `no_raw_rows`
- `synthetic_only_checked`
- `no_oracle_checked`
- `reason_codes`

Forbidden in results:

- raw rows
- raw learner text
- JSONL body
- label body
- candidate score rows
- config body
- private absolute paths
- raw stack traces with content
- real participant data

`failed_checks` should contain category/reason-code pairs and sanitized file
categories. It should not include offending values.

## 8. Expected Result Matching

Fixture tests should compare:

- `audit_status`
- `expected_failure_code`
- `expected_violation_category`
- `expected_violation_count_min`
- `content_suppressed`
- `no_raw_rows`

Rules:

- valid fixtures expect pass
- invalid fixtures expect fail with the expected reason code
- actual violation count must be at least the expected minimum
- extra violations can be allowed initially only if the expected primary code
  is present
- missing expected-result files fail fixture mode
- mismatches are test failures
- mismatch output must not print row bodies

The expected result file is a test oracle for audit behavior, not a scoring
feedback signal and not a learner-state label.

## 9. Failure Policy

The audit should fail closed:

- malformed JSON -> `malformed_input`
- malformed JSONL -> `malformed_input`
- empty input -> `empty_input`
- no fixture cases -> `no_cases`
- missing required schema version -> `missing_schema_version`
- unknown schema version -> `unknown_schema_version`
- suspicious path -> `unsafe_path`
- forbidden field -> `forbidden_field`
- feature/label mixing -> label-feature reason code
- future leakage -> `future_leakage`
- split leakage -> `split_leakage`
- unsafe join key -> `unsafe_join_key`
- manifest body leakage -> `manifest_body_leakage`

Multiple violations should be aggregated count-only. There should be no silent
pass for unknown versions, suspicious paths, or ambiguous feature-label
boundaries.

## 10. Output Safety

Output rules:

- stdout safe status only
- optional safe JSON result
- no row dumps
- no raw labels
- no expected action body
- no private paths
- no raw stack traces with content
- no candidate score rows
- no config body
- no performance metrics

Tests should use safe output scan helpers where practical. Exception handling
should convert internal errors to safe failure summaries unless the process
crashes before structured handling is possible.

## 11. Fixture Test Design

Future fixture tests should:

- enumerate fixture case directories
- run `audit_fixture_case(case_dir)`
- load `expected_audit_result.json`
- compare actual and expected results
- assert valid fixtures pass
- assert invalid fixtures fail with expected reason codes
- assert stdout/stderr do not contain raw row bodies
- stay deterministic
- keep fixture bodies small and synthetic

The first tests should focus on safety behavior, not broad data coverage.

## 12. Makefile / Release-Quality Integration Plan

Initial implementation should not change Makefile or release-quality unless the
audit and fixture tests are already stable.

Future candidate target:

- `check-learner-state-audit-fixtures`

Integration sequence:

1. implement module
2. add fixture smoke tests
3. prove local tests are stable
4. consider a Makefile target
5. consider release-quality wrapper integration

Current Makefile and release-quality wrapper remain unchanged for this design
step.

## 13. Relation to Existing Pipeline

The learner-state sequence audit should align with:

- existing Rust no-oracle audit boundaries
- `SafeEpisodeView`
- `CandidateScoreSet` summaries, not raw score rows
- synthetic expected action registry as labels only
- synthetic policy checker
- safe output scan helper patterns
- Makefile and release-quality wrapper as support infrastructure
- future learner-state sequence exporter

The audit should run before any future learner-state estimator consumes a
sequence dataset.

## 14. Future Implementation Roadmap

Recommended order:

1. Step 165: implement minimal learner-state sequence audit module
2. Step 166: add fixture smoke tests
3. Step 167: optional CLI wrapper
4. Step 168: optional Makefile target integration
5. Later: release-quality integration after smoke tests are stable
6. Later: minimal sequence exporter
7. Later: selective prediction / calibration design
8. Later: estimator prototype

If fixture test output safety is not easy to guarantee, add a safe-output test
helper step before Makefile or release-quality integration.

## 15. Beginner Notes

An audit implementation is the code that checks whether a dataset is safe
enough for later tools to read.

Fixture expected results are useful because they tell the audit what each small
synthetic case should do: pass for safe input, fail for a known unsafe boundary.

Fail-closed means suspicious input is rejected instead of being treated as safe
by default.

Raw rows should not appear in errors because error output is often copied into
issues, docs, or CI logs. Keeping errors count-only makes the habit safe before
private-data readiness is ever considered.

Python is a practical first implementation because JSON, JSONL, directory
walking, and fixture result matching are simple to express there. Rust can be
revisited later if the audit needs to move closer to Rust-owned safe view
generation.

## Related Documents

- [Learner-state sequence no-oracle audit design](learner_state_sequence_no_oracle_audit_design.md)
- [Learner-state sequence audit fixture/schema design](learner_state_sequence_audit_fixture_schema_design.md)
- [Learner-state sequence audit fixture files design](learner_state_sequence_audit_fixture_files_design.md)
- [Learner-state sequence audit fixture files](../tests/fixtures/learner_state_sequence_audit/README.md)
- [Learner-state sequence schema design](learner_state_sequence_schema_design.md)
- [Synthetic learner-state sequence dataset design](synthetic_learner_state_sequence_dataset_design.md)
- [Learner-state input representation design](learner_state_input_representation_design.md)
- [No-oracle policy](03_no_oracle_policy.md)
- [Synthetic data policy](12_synthetic_data_policy.md)
- [Public release checklist](public_release_checklist.md)
