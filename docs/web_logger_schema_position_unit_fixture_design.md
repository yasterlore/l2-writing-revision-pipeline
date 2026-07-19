# Schema-Level Position Unit Fixture Design for Web Logger Events

## 1. Title

Schema-Level Position Unit Fixture Design for Web Logger Events

## 2. Scope

This is a fixture-design / docs-only step.

It does not change Rust, TypeScript, or Python code. It does not change tests,
fixture JSON, Makefile targets, release-quality wrapper behavior, CI workflow
files, package metadata, Cargo metadata, schema behavior, validator behavior,
replay behavior, extract behavior, micro_episode behavior, or event durability.

It does not prove production readiness, real-data readiness, or model
performance.

## 3. Design Status

Step-web-logger-032 designed the schema-level `position_unit` policy. This
document translates that policy into a future synthetic fixture matrix for
schema / validator implementation.

This document does not create or modify fixture JSON. It does not implement
schema or validator behavior. The current `kslog_replay` focused boundary
remains accepted, and schema-level validation remains future work.

## 4. Existing Fixture Structure Audit

Relevant existing fixture roots:

- `tests/fixtures/synthetic/raw_events/`
- `tests/fixtures/web_logger_unicode_hash_vectors/`
- multiple learner-state fixture roots that use dedicated `valid/` and
  `invalid/` directories plus metadata and expected-result files

Current raw event fixtures live under `tests/fixtures/synthetic/raw_events/`.
They use JSONL files split into `valid/` and `invalid/`.

Current valid raw event fixture names include simple typing, deletion,
replacement, selection edit, paste, IME composition, and cursor movement cases.
Current invalid raw event fixture names include malformed JSON, missing required
field, unknown forbidden field, sequence gap, timestamp inversion, invalid
cursor range, and invalid selection range.

`kslog_schema` tests deserialize all current valid raw event JSONL fixtures and
check the no-oracle forbidden-field invalid fixture. `kslog_validate` tests run
all valid raw event fixtures and targeted invalid raw event fixtures.

Current missing required field cases are represented as invalid JSONL fixtures.
Unknown / forbidden fields are represented by the `unknown_forbidden_field`
fixture and by inline synthetic tests. Cursor and selection invalid cases are
represented as numeric range failures against document length fields.

The current raw event fixture layout can technically host `position_unit` cases,
but mixing future Web logger v0.2 position-unit policy cases into legacy
`kslog.raw_event.v1` fixtures risks blurring the schema boundary. A dedicated
fixture root is safer.

## 5. Proposed Fixture Root Strategy

Recommended future fixture root:

`tests/fixtures/web_logger_position_unit_schema/`

Recommended layout:

- `README.md`
- `valid/`
- `invalid/`
- `legacy/`
- optional `case_index.json` if the future validator needs a metadata-only case
  manifest

Alternative:

- extend `tests/fixtures/synthetic/raw_events/valid`
- extend `tests/fixtures/synthetic/raw_events/invalid`

Recommendation:

Use the dedicated `tests/fixtures/web_logger_position_unit_schema/` root. It
keeps future Web logger position-unit policy separate from legacy raw event
fixtures, supports explicit valid / invalid / legacy grouping, and follows the
project pattern of dedicated roots for specialized safety contracts.

All cases should be synthetic and minimal. Do not reuse real data. Do not paste
full fixture bodies into docs.

## 6. Fixture Schema Metadata Design

Future fixture metadata should be public-safe and explicit.

Recommended metadata fields:

- `fixture_schema_version`
- `case_id`
- `case_kind`
- `expected_status`
- `expected_reason_code`
- `logger_schema_version`
- `research_schema_target`
- `position_unit`
- `expected_position_unit_policy`
- `synthetic_only`
- `no_oracle_safe`
- `content_suppressed_expected`
- `notes`

Metadata must not include raw learner text, full event payload bodies, private
paths, absolute local paths, expected body fields, request body fields, or
pointer body fields unless a later design justifies them. Schema version must be
explicit.

## 7. Required Valid Fixture Cases

### valid_ascii_utf16_position_unit

Purpose:

- ASCII case where UTF-16 code unit offsets and UTF-8 byte offsets coincide
- confirms explicit `position_unit=utf16_code_unit` is accepted

Expected:

- `expected_status=pass`
- `expected_reason_code=none`

### valid_japanese_cursor_utf16_position_unit

Purpose:

- Japanese text where UTF-16 offsets differ from UTF-8 byte offsets
- confirms validator checks UTF-16 unit semantics rather than byte-offset
  assumptions

Expected:

- `expected_status=pass`
- `expected_reason_code=none`

### valid_japanese_selection_utf16_position_unit

Purpose:

- selection range over Japanese text
- confirms `selection_start` / `selection_end` are UTF-16 code unit offsets

Expected:

- `expected_status=pass`
- `expected_reason_code=none`

### valid_emoji_boundary_utf16_position_unit

Purpose:

- emoji surrogate-pair boundary case
- valid offsets before and after emoji are accepted

Expected:

- `expected_status=pass`
- `expected_reason_code=none`

### valid_mixed_japanese_emoji_utf16_position_unit

Purpose:

- mixed Japanese + emoji + ASCII case
- confirms multi-kind UTF-16 offset behavior

Expected:

- `expected_status=pass`
- `expected_reason_code=none`

### valid_legacy_missing_position_unit_explicitly_gated

Purpose:

- legacy fixture without `position_unit`
- confirms legacy behavior is explicit, not guessed

Expected:

- `expected_status=pass` or `expected_status=legacy_allowed`, depending on the
  final policy
- `expected_reason_code=legacy_position_unit_missing_allowed`, if treated as a
  metadata note

The legacy case must not silently become Web logger v0.2 behavior. If the final
policy rejects legacy missing `position_unit`, this case should move to
`invalid/`.

## 8. Required Invalid Fixture Cases

### invalid_v0_2_missing_position_unit

Purpose:

- Web logger v0.2+ event missing `position_unit`

Expected:

- `expected_status=fail`
- `expected_reason_code=missing_position_unit`

### invalid_unsupported_position_unit_byte_index

Purpose:

- event declares unsupported value such as `byte_index`

Expected:

- `expected_status=fail`
- `expected_reason_code=unsupported_position_unit`

### invalid_unsupported_position_unit_code_point

Purpose:

- event declares unsupported value such as `code_point`

Expected:

- `expected_status=fail`
- `expected_reason_code=unsupported_position_unit`

### invalid_position_unit_schema_mismatch

Purpose:

- schema version / logger version combination conflicts with position-unit
  policy

Expected:

- `expected_status=fail`
- `expected_reason_code=position_unit_schema_mismatch`

### invalid_doc_len_before_utf16_mismatch

Purpose:

- `doc_len_before` does not match UTF-16 code unit length

Expected:

- `expected_status=fail`
- `expected_reason_code=doc_len_before_utf16_mismatch`

### invalid_doc_len_after_utf16_mismatch

Purpose:

- `doc_len_after` does not match UTF-16 code unit length

Expected:

- `expected_status=fail`
- `expected_reason_code=doc_len_after_utf16_mismatch`

### invalid_selection_start_greater_than_end

Purpose:

- `selection_start > selection_end`

Expected:

- `expected_status=fail`
- `expected_reason_code=start_greater_than_end`

### invalid_offset_beyond_utf16_length

Purpose:

- cursor / selection offset beyond UTF-16 length

Expected:

- `expected_status=fail`
- `expected_reason_code=offset_beyond_utf16_length`

### invalid_surrogate_pair_internal_offset

Purpose:

- cursor / selection offset points inside emoji surrogate pair

Expected:

- `expected_status=fail`
- `expected_reason_code=offset_inside_surrogate_pair`

### invalid_byte_index_supplied_as_utf16_when_detectable

Purpose:

- value resembles UTF-8 byte offset rather than UTF-16 code unit offset and
  should fail when validator has enough text context

Expected:

- `expected_status=fail`
- `expected_reason_code=invalid_utf16_boundary` or
  `expected_reason_code=offset_beyond_utf16_length`, depending on detectability

### invalid_unknown_schema_version

Purpose:

- unknown schema version with `position_unit` field

Expected:

- `expected_status=fail`
- `expected_reason_code=unknown_schema_version`, if existing project policy
  supports it

Metadata-only checks can cover missing field, unsupported value, schema mismatch,
unknown schema version, and `start > end`. Text-context checks are needed for
UTF-16 document-length mismatch, surrogate-pair internal offset, and byte-index
misuse detection.

## 9. Event Field Design for Fixtures

Future event fixtures should include only fields required by the current or
planned schema.

Candidate fields:

- `seq`
- `event_type`
- `input_type`
- `logger_schema_version`
- `research_schema_target`
- `position_unit`
- `cursor_pos`
- `cursor_pos_before`
- `cursor_pos_after`
- `selection_start`
- `selection_end`
- `selection_start_before`
- `selection_end_before`
- `doc_len_before`
- `doc_len_after`
- `inserted_text`
- `deleted_text`
- `text_hash_before`
- `text_hash_after`
- `prompt_id`
- `timestamp_ms`
- `quality_flags`

Use short synthetic strings only. Avoid unnecessary fields. Do not include full
event payload examples in docs.

## 10. Expected Reason Code Matrix

| case_id | category | expected_status | expected_reason_code | requires_text_context | schema check | validator check | replay check | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| valid_ascii_utf16_position_unit | valid | pass | none | yes | yes | yes | no | explicit UTF-16 unit |
| valid_japanese_cursor_utf16_position_unit | valid | pass | none | yes | yes | yes | no | non-byte-equivalent offset |
| valid_japanese_selection_utf16_position_unit | valid | pass | none | yes | yes | yes | no | selection range |
| valid_emoji_boundary_utf16_position_unit | valid | pass | none | yes | yes | yes | no | scalar boundaries only |
| valid_mixed_japanese_emoji_utf16_position_unit | valid | pass | none | yes | yes | yes | no | mixed Unicode categories |
| valid_legacy_missing_position_unit_explicitly_gated | legacy | pass or legacy_allowed | legacy_position_unit_missing_allowed | no | yes | yes | no | gated legacy only |
| invalid_v0_2_missing_position_unit | invalid | fail | missing_position_unit | no | yes | yes | no | future schema requires field |
| invalid_unsupported_position_unit_byte_index | invalid | fail | unsupported_position_unit | no | yes | yes | no | unsupported value |
| invalid_unsupported_position_unit_code_point | invalid | fail | unsupported_position_unit | no | yes | yes | no | unsupported value |
| invalid_position_unit_schema_mismatch | invalid | fail | position_unit_schema_mismatch | no | yes | yes | no | version / unit conflict |
| invalid_doc_len_before_utf16_mismatch | invalid | fail | doc_len_before_utf16_mismatch | yes | no | yes | no | needs safe text context |
| invalid_doc_len_after_utf16_mismatch | invalid | fail | doc_len_after_utf16_mismatch | yes | no | yes | no | needs safe text context |
| invalid_selection_start_greater_than_end | invalid | fail | start_greater_than_end | no | no | yes | no | metadata range check |
| invalid_offset_beyond_utf16_length | invalid | fail | offset_beyond_utf16_length | yes | no | yes | no | needs length context |
| invalid_surrogate_pair_internal_offset | invalid | fail | offset_inside_surrogate_pair | yes | no | yes | no | needs boundary mapping |
| invalid_byte_index_supplied_as_utf16_when_detectable | invalid | fail | invalid_utf16_boundary or offset_beyond_utf16_length | yes | no | yes | no | depends on text context |
| invalid_unknown_schema_version | invalid | fail | unknown_schema_version | no | yes | yes | no | if policy supports it |

Replay already covers some offset behavior in `kslog_replay`, but these fixtures
are intended for schema / validator boundary checks.

## 11. Legacy Fixture Policy

Missing `position_unit` must not be silently assumed as UTF-16 for Web logger
v0.2+ events and must not be silently assumed as byte index.

Legacy fixtures should be gated by schema version and fixture family. Any
legacy allowance should be explicit, documented, and temporary unless the
project decides to preserve it as a stable legacy contract.

Legacy allowance must not weaken the new Web logger v0.2 policy. If existing
fixtures need migration, migration should be a separate step. If existing
fixtures remain unchanged, document that they do not exercise the new
position-unit policy.

## 12. Fixture Body Safety Policy

Future fixtures must include:

- no real participant data
- no raw learner text
- no private path
- no absolute local path
- no full raw logs
- no copied GitHub logs
- no full job output
- no logits / probabilities
- no performance metric body
- no `final_text`
- no `observed_after_text`
- no gold labels
- no post-hoc annotation
- no test-set tuning markers
- no raw fixture body pasted into docs

Short synthetic strings may exist in fixture files in a future implementation
step, but docs should not paste full fixture bodies. Diagnostics should report
metadata, counts, and reason codes only.

## 13. Public-Safe Expected Output Design

Allowed future CLI / validator output:

- `mode`
- `schema_version`
- `validation_status`
- `total_cases`
- `pass_cases`
- `fail_closed_cases`
- `usage_error_cases`
- `expected_reason_code_counts`
- `observed_reason_code_counts`
- `content_suppressed=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `position_unit_policy_checked=true`
- `raw_text_suppressed=true`
- `fixture_body_suppressed=true`

Forbidden future output:

- raw event JSON body
- full fixture JSON body
- source text
- selected text
- inserted/deleted text by default
- private paths
- absolute paths
- raw learner text
- real participant data
- logits / probabilities
- performance metric body

## 14. Proposed Future Validator Behavior Covered by Fixtures

Future fixtures are intended to test:

- presence of `position_unit`
- supported value check
- schema version gating
- UTF-16 `doc_len_before` / `doc_len_after` checks
- UTF-16 cursor offset bounds
- UTF-16 selection offset bounds
- surrogate internal offset fail-closed behavior when text context is available
- selection `start > end`
- public-safe diagnostics
- legacy gating

They do not test TypeScript/Rust hash compatibility, event durability, network
retry / acknowledgement / deduplication, extract integration, micro_episode
integration, production readiness, or real-data readiness.

## 15. Proposed Future Implementation Staging

Recommended future staging:

- Step-web-logger-034: create schema-level position_unit fixtures for Web logger
  events
- Step-web-logger-035: implement schema/validator position_unit policy with
  focused tests
- Step-web-logger-036: Makefile target design for schema position_unit
  validation
- Step-web-logger-037: add Makefile target
- Step-web-logger-038: release-quality integration design
- Step-web-logger-039: release-quality wrapper integration
- Step-web-logger-040: remote/manual run record workflow design
- Step-web-logger-041: status marker
- Step-web-logger-042: final safety review

Prefer staging fixture creation separately from validator implementation for
safer review.

## 16. Relationship to Step-web-logger-032 Policy Design

Step-web-logger-032 defined the policy. Step-web-logger-033 translates that
policy into a fixture matrix. Step-web-logger-033 does not implement policy,
does not create fixtures, and should remain consistent with Step-web-logger-032.

## 17. Relationship to Step-web-logger-031 Replay Integration

Step-web-logger-031 accepted the `kslog_replay` focused replay boundary.
Position-unit fixtures are for the schema / validator boundary. Replay pass does
not prove schema validation. Schema fixtures should not weaken replay-focused
tests, and replay-focused status evidence remains distinct.

## 18. Relationship to Focused Helper Chain

The focused helper chain remains accepted. Fixture design may reuse the same
Unicode categories conceptually, but fixture design is not helper
implementation, and helper evidence is not schema validation evidence.

## 19. Relationship to TypeScript / Rust Hash/Helper Work

This fixture design does not implement Rust SHA-256 helper work, TypeScript
SHA-256 helper work, or TypeScript/Rust vector checks. It does not prove current
TypeScript/Rust hash equality. Hash compatibility remains separate.

## 20. Relationship to Event Durability

This fixture design does not implement event durability. Queueing, IndexedDB
buffering, acknowledgement, retry, deduplication, server-side idempotency, and
ordering / delivery durability remain unimplemented.

## 21. Relationship to No-Oracle and Synthetic-Only Boundaries

Future fixtures must be synthetic-only. They must not introduce real participant
data, raw learner text, final text, observed-after text, gold labels, post-hoc
annotations, test-set tuning, or model performance validation. No-oracle
constraints are not relaxed.

## 22. Failure Interpretation

Fixture design is not fixture implementation. Fixture creation pass will not
prove validator implementation. Validator fixture pass will not prove replay
correctness. Replay pass will not prove schema validation. Synthetic-only
fixture pass will not prove real-data readiness.

Status for missing `position_unit` should be determined by schema version
policy. Legacy allowance should not be treated as new Web logger v0.2 behavior.

## 23. Non-Equivalence Cautions

- Fixture design is not fixture creation.
- Fixture design is not schema implementation.
- Fixture design is not validator implementation.
- Fixture design is not replay integration.
- Fixture design is not extract integration.
- Fixture design is not micro_episode integration.
- Fixture design is not TypeScript/Rust compatibility.
- Fixture design is not hash compatibility.
- Fixture design is not event durability.
- Fixture design is not production readiness.
- Synthetic-only fixture design is not real-data readiness.

## 24. Non-Claims

This fixture design does not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- broader Unicode correctness completion
- validate integration completion
- extract integration completion
- micro_episode integration completion
- schema-level position_unit policy implementation
- schema-level position_unit fixture creation
- hash compatibility implementation completion
- TypeScript / Rust vector check implementation
- current TypeScript/Rust hash equality
- event durability implementation
- data collection readiness
- deployment readiness

## 25. Recommended Next Codex Step

Recommended next step:

Step-web-logger-034: create schema-level position_unit fixtures for Web logger
events

Clarification:

- Step-web-logger-034 should be a fixture implementation step.
- It should create the dedicated fixture root if this recommendation is
  accepted.
- It should add README and fixture metadata/cases.
- It should not implement validator behavior yet unless explicitly scoped.
- It should not modify Rust code except possibly tests only if required by
  fixture validation, and preferably not yet.
- It should not modify TypeScript code.
- It should not modify Makefile.
- It should not modify release-quality wrapper.
- It should update README and full technical specification related docs because
  fixture files are implementation artifacts.
- It should preserve synthetic-only, no-oracle, and public-safe boundaries.

## 26. Step-web-logger-034 Fixture Root Implementation Note

Step-web-logger-034 implements the dedicated fixture root recommended by this
design:

- `tests/fixtures/web_logger_position_unit_schema/README.md`
- `tests/fixtures/web_logger_position_unit_schema/case_index.json`
- `tests/fixtures/web_logger_position_unit_schema/valid/*.jsonl`
- `tests/fixtures/web_logger_position_unit_schema/invalid/*.jsonl`
- `tests/fixtures/web_logger_position_unit_schema/legacy/*.jsonl`

The implemented matrix contains 5 valid, 11 invalid, and 1 legacy synthetic
case. It fixes future schema / validator expectations for explicit
`position_unit=utf16_code_unit`, missing units, unsupported units, schema /
logger mismatch, UTF-16 document length mismatch, invalid UTF-16 boundaries,
and explicit legacy missing-unit gating.

This implementation note does not change the design boundary: schema /
validator behavior, fixture validator CLI, Makefile target, release-quality
wrapper integration, Rust / TypeScript / Python code changes, existing fixture
JSON changes, validate / extract / micro_episode integration, TypeScript/Rust
hash work, event durability, production readiness, real-data readiness, and
model performance remain future work.

## 27. Step-web-logger-035 Fixture Validator Design

Step-web-logger-035 adds
[Schema-Level Position Unit Fixture Validator Design](web_logger_schema_position_unit_fixture_validator_design.md).

The validator design plans a future Python-first contract validator for the
Step-web-logger-034 fixture root. It does not modify the fixture root, implement
Python / Rust / TypeScript code, add tests, add a Makefile target, add
release-quality integration, or change schema / validator behavior.

## 28. Step-web-logger-036 Fixture Validator Implementation

Step-web-logger-036 adds `python/web_logger_position_unit_fixture_validation.py`
and focused tests at
`python/test_support/tests/test_web_logger_position_unit_fixture_validation.py`.

The validator now checks this fixture design's 17-case / 24-record contract
with public-safe summary output. It does not change fixture JSON, add a
Makefile target, add release-quality integration, implement Rust schema /
validator behavior, or alter validate / extract / micro_episode boundaries.
