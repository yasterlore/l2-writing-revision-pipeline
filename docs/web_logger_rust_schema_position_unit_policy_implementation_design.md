# Rust Schema-Level Position Unit Policy Implementation Design

## 1. Title

Rust Schema-Level Position Unit Policy Implementation Design

## 2. Scope

This is a design-only / docs-only step.

This step makes no Rust code changes, no TypeScript code changes, no Python
code changes, no test changes, no fixture JSON changes, no Makefile changes,
no release-quality wrapper changes, no CI workflow changes, and no
`package.json` / `Cargo.toml` / `Cargo.lock` changes.

This step makes no schema behavior changes, no validator behavior changes, no
replay behavior changes, no extract / micro_episode behavior changes, and no
event durability implementation. It provides no production readiness proof, no
real-data readiness proof, and no model performance proof.

## 3. Design Status

Step-web-logger-034 through Step-web-logger-043 completed the fixture
contract / validator / Makefile / release-quality / remote-status chain for
schema-level position_unit fixture validation.

Step-web-logger-043 accepted this explicit boundary:

`release-quality-integrated, remote-status-recorded, schema-level position_unit fixture contract validation for the fixed 17-case synthetic Web logger fixture matrix`

This document designs future Rust schema / validator implementation strategy.
It does not implement Rust schema / validator behavior. `kslog_schema` /
`kslog_validate` position_unit policy remains future work.

## 4. Current Rust Schema Audit

Current `kslog_schema::RawEvent` is defined in `crates/kslog_schema/src/lib.rs`.
It includes `logger_schema_version` as a required `String`, but does not
currently include `position_unit` or `research_schema_target`.

Relevant current fields:

- `logger_schema_version`
- identity / ordering / timestamp fields
- cursor and selection fields
- document length fields
- inserted / deleted text fields
- text hash fields
- `diff_op`
- `quality_flags`

Current serde behavior:

- `RawEvent` uses `serde(deny_unknown_fields)`.
- Optional fields deserialize as absent when omitted.
- `quality_flags` defaults to an empty vector.
- Unknown fields are rejected during deserialization.
- Project no-oracle forbidden fields are also rejected by validator pre-scan.

Current limitation for position_unit policy:

- Records containing `position_unit` currently fail as unknown `RawEvent`
  fields.
- Records containing `research_schema_target` also currently fail as unknown
  `RawEvent` fields.
- Unsupported position_unit values cannot yet be classified by a stable
  validator reason code because deserialization rejects the field before the
  validator can inspect the value.
- Making position_unit mandatory globally would break existing legacy /
  synthetic fixtures that intentionally omit it.

## 5. Current Rust Validator Audit

Current `kslog_validate` reads JSONL lines, rejects malformed JSON, requires a
JSON object, pre-scans no-oracle forbidden fields, deserializes to `RawEvent`,
then validates sequence, timestamp ordering, cursor bounds, selection range
ordering, and selection bounds.

Current validation stages:

- max line size
- empty-line policy
- JSON syntax
- JSON object shape
- no-oracle forbidden field pre-scan
- `RawEvent` schema deserialization
- consecutive `seq`
- non-decreasing `timestamp_ms`
- cursor positions within available document lengths
- selection start/end ordering
- selection positions within available document lengths

Current error reporting uses `ValidationErrorKind` plus display text. It does
not currently expose stable reason-code strings for every validator error.

Current limitations:

- Validation does not distinguish UTF-16 code unit offsets from byte offsets.
- `doc_len_before` / `doc_len_after` are treated as numeric bounds, not as
  UTF-16 code unit lengths.
- Missing or unsupported position_unit cannot be classified because the field
  is not in `RawEvent`.
- Existing legacy/synthetic fixtures would be at risk if position_unit were
  required without version / target gating.

## 6. Current Fixture Contract Audit

Step-web-logger-034 created:

- fixture root: `tests/fixtures/web_logger_position_unit_schema/`
- case index: `tests/fixtures/web_logger_position_unit_schema/case_index.json`
- valid cases: 5
- invalid cases: 11
- legacy cases: 1
- total cases: 17
- JSONL records: 24

Metadata-only fixture coverage includes:

- valid ASCII UTF-16 position_unit case
- valid Japanese cursor case
- valid Japanese selection case
- valid emoji boundary case
- valid mixed Japanese / emoji case
- missing position_unit invalid case
- unsupported `byte_index` invalid case
- unsupported `code_point` invalid case
- schema mismatch invalid case
- UTF-16 document length mismatch invalid cases
- selection start greater than end invalid case
- offset beyond UTF-16 length invalid cases
- surrogate-pair internal offset invalid case
- byte-index-as-UTF-16 misuse fixture
- unknown schema version fixture
- explicitly gated legacy missing position_unit case

The fixture contract is synthetic-only and no-oracle safe. Fixture bodies are
not pasted into docs.

Step-web-logger-042 records Python fixture validator pass status through
remote release-quality evidence.

## 7. Target Policy

Target Rust policy:

- Browser-originated Web logger events targeting Web logger schema v0.2+ must
  explicitly declare `position_unit=utf16_code_unit`.
- Missing `position_unit` should fail for Web logger v0.2+ events.
- Unsupported values such as `byte_index` and `code_point` should fail.
- Legacy events may omit `position_unit` only under explicit legacy gating.
- Missing `position_unit` must not be silently treated as UTF-16 for Web
  logger v0.2+.
- Validator output must be public-safe and body-free.
- Errors must not emit raw source / selected / inserted / deleted text.

Policy boundaries:

- Schema presence/value policy decides whether `position_unit` is present,
  recognized, and compatible with schema gating.
- UTF-16 numeric offset boundary policy decides whether numeric offsets and
  document lengths match UTF-16 code unit semantics when text context is
  available.
- Replay string slicing policy converts accepted UTF-16 offsets to Rust UTF-8
  byte indices before slicing. That replay boundary is already separate.

## 8. RawEvent Field Representation Design

Option A: `position_unit: Option<String>`

- Pros: preserves unsupported values for validator classification; missing vs
  unsupported remains distinguishable; legacy records can still deserialize.
- Cons: schema type stays less precise without a parser/accessor.

Option B: `position_unit: Option<PositionUnit>` enum

- Pros: typed value is convenient after successful deserialization.
- Cons: unsupported values fail during serde deserialization and are harder to
  classify as `unsupported_position_unit`; schema layer may erase useful error
  context before validator policy runs.

Option C: raw string plus helper accessor / parser returning a typed enum

- Pros: preserves unsupported values, keeps missing vs unsupported vs mismatch
  distinguishable, avoids panic, lets validator emit stable reason codes, and
  keeps legacy fixtures deserializable.
- Cons: requires small parser API and focused tests.

Recommendation: Option C.

Future `RawEvent` should add:

- `position_unit: Option<String>`
- `research_schema_target: Option<String>`, if Web logger target gating relies
  on the fixture contract's target field

Future parser/accessor shape:

- `PositionUnitPolicy::Utf16CodeUnit`
- `PositionUnitPolicyError::MissingPositionUnit`
- `PositionUnitPolicyError::UnsupportedPositionUnit`
- `PositionUnitPolicyError::PositionUnitSchemaMismatch`
- `PositionUnitPolicyError::UnknownSchemaVersion`
- `PositionUnitPolicyError::LegacyPositionUnitMissingAllowed`, if represented
  as metadata rather than an error

The parser should not panic. It should not include raw event body or raw text
in error display. It should leave unsupported string values available for
classification without printing those values by default.

## 9. Version / Schema Gating Design

Current audit shows the relevant metadata values in the fixture contract are:

- `logger_schema_version=kslog.raw_event.v1`
- `logger_schema_version=kslog.raw_event.v2`
- `logger_schema_version=kslog.raw_event.v9`
- `research_schema_target=web_logger_position_unit_schema_v0.1`

Recommended predicates:

- `is_web_logger_position_unit_target(event) -> bool`
- `is_known_raw_event_schema_version(event) -> bool`
- `is_web_logger_v0_2_or_later(event) -> bool`
- `is_legacy_position_unit_allowed(event) -> bool`
- `position_unit_required(event) -> bool`

Recommended gating:

- `kslog.raw_event.v2` plus the Web logger position_unit target requires
  `position_unit=utf16_code_unit`.
- `kslog.raw_event.v1` plus the Web logger position_unit target may omit
  position_unit only when explicitly treated as legacy.
- `kslog.raw_event.v1` with `position_unit=utf16_code_unit` should fail as
  `position_unit_schema_mismatch` for the current fixture contract.
- Unknown schema versions such as `kslog.raw_event.v9` should fail closed as
  `unknown_schema_version` where the Web logger position_unit target is in
  scope.
- Existing non-position-unit legacy synthetic fixtures should not become
  invalid by accident; do not require position_unit globally.

If current version strings remain inconsistent outside this fixture root, the
implementation should keep target gating explicit rather than guessing.

## 10. Validator Reason_Code Design

Stable reason codes needed by the full fixture contract:

- `none`
- `missing_position_unit`
- `unsupported_position_unit`
- `position_unit_schema_mismatch`
- `unknown_schema_version`
- `doc_len_before_utf16_mismatch`
- `doc_len_after_utf16_mismatch`
- `start_greater_than_end`
- `offset_beyond_utf16_length`
- `offset_inside_surrogate_pair`
- `invalid_utf16_boundary`
- `legacy_position_unit_missing_allowed`

Recommended phased split:

Phase 1:

- `missing_position_unit`
- `unsupported_position_unit`
- `position_unit_schema_mismatch`
- `unknown_schema_version`
- legacy missing-position handling

Phase 2:

- `doc_len_before_utf16_mismatch`
- `doc_len_after_utf16_mismatch`
- `start_greater_than_end`
- `offset_beyond_utf16_length`
- `offset_inside_surrogate_pair`
- `invalid_utf16_boundary`

Phase 1 should add stable validator reason-code mapping without claiming UTF-16
numeric metadata validation. Phase 2 should add UTF-16 length / boundary
checks only after dependency strategy is resolved.

## 11. UTF-16 Helper / Dependency Strategy

Current helper location:

- `crates/kslog_replay/src/utf16_offsets.rs`

Current crate dependency shape:

- `kslog_validate` depends on `kslog_schema`.
- `kslog_replay` depends on `kslog_schema`.
- `kslog_replay` uses `kslog_validate` only as a dev-dependency.
- `kslog_validate` does not depend on `kslog_replay`.

Option A: Phase 1 only implements field presence/value/version policy in
`kslog_schema` / `kslog_validate`; UTF-16 numeric validation remains future
work.

- Pros: avoids dependency cycle risk; avoids moving helper too early; protects
  existing tests; keeps the first implementation small.
- Cons: does not satisfy numeric UTF-16 mismatch fixtures in Rust yet.

Option B: move UTF-16 helper to a shared crate/module, then use it from replay
and validate.

- Pros: avoids duplicated conversion logic; can support Phase 2 numeric checks.
- Cons: requires crate/module design and broader Cargo changes.

Option C: duplicate a minimal helper in validate temporarily.

- Pros: fastest path to numeric checks.
- Cons: risks divergence from replay behavior and increases maintenance cost.

Recommendation: Option A for the next implementation step, followed by a
separate shared-helper design before Phase 2. Do not make `kslog_validate`
depend on `kslog_replay`.

## 12. Test Design

Future `kslog_schema` tests should cover:

- deserializing valid `position_unit=utf16_code_unit`
- preserving missing position_unit for legacy fixtures
- preserving unsupported values for validator classification
- preserving `research_schema_target` if used for gating
- rejecting project no-oracle forbidden fields
- ensuring parser/display output stays body-free

Future `kslog_validate` tests should cover:

- valid Web logger v0.2+ position_unit cases pass
- missing position_unit fails for Web logger v0.2+
- unsupported `byte_index` fails
- unsupported `code_point` fails
- schema mismatch fails
- unknown schema version fails
- legacy missing position_unit is explicitly allowed or categorized
- existing legacy synthetic raw event fixtures still pass where intended
- invalid UTF-16 metadata cases are either validated in the current phase or
  explicitly deferred

No tests are created in this step.

## 13. Fixture Integration Design

Future Rust tests should reuse
`tests/fixtures/web_logger_position_unit_schema/`.

Requirements:

- do not duplicate fixture bodies
- do not modify fixture JSON in the first Rust design step
- use `case_index.json` metadata where useful
- do not paste fixture bodies into docs
- keep the Python fixture validator as the fixture contract check
- do not bypass the fixture contract in Rust implementation

Recommended approach:

- Phase 1 Rust tests may read `case_index.json` and focused fixture files for
  presence/value/version cases only.
- Phase 2 Rust tests may expand fixture mapping to numeric UTF-16 metadata
  cases after shared-helper strategy is resolved.

## 14. Error Output and Public-Safe Diagnostics Design

Diagnostics should be stable, machine-checkable, and public-safe.

Requirements:

- include reason_code where feasible
- include line number where useful
- include case ID or repository-relative fixture path only if needed
- do not include raw event body
- do not include raw source text
- do not include selected text
- do not include inserted/deleted text by default
- do not include private paths or absolute local paths
- stay safe for release-quality logs

Recommended implementation detail:

- add `reason_code()` to position-unit policy error type
- optionally map position-unit errors into `ValidationErrorKind`
- keep `Display` messages limited to field names, reason codes, and numeric
  metadata

## 15. Backward Compatibility Design

Backward compatibility requirements:

- current legacy fixtures may not have position_unit
- do not require position_unit globally
- gate requirement to Web logger v0.2+ or explicit Web logger target
- maintain existing behavior for older fixtures unless explicitly migrated
- record legacy allowance clearly
- avoid silent fallback for new Web logger v0.2+ cases

Adding `position_unit: Option<String>` and `research_schema_target:
Option<String>` should be staged with focused tests so existing legacy fixtures
continue to deserialize.

## 16. Proposed Implementation Staging

Recommended staging:

- Step-web-logger-045: implement Rust schema position_unit field and parser
  boundary
- Step-web-logger-046: design Rust validator position_unit policy tests and
  fixture mapping, if not included in Step045
- Step-web-logger-047: implement Rust validator position_unit
  presence/value/version gating
- Step-web-logger-048: Makefile target design for Rust schema/validator
  position_unit checks
- Step-web-logger-049: add Makefile target
- Step-web-logger-050: release-quality integration design
- Step-web-logger-051: release-quality wrapper integration
- Step-web-logger-052: remote/manual run record workflow design
- Step-web-logger-053: status marker
- Step-web-logger-054: final safety review

Rationale: this keeps schema representation, validator policy, Makefile
surface, release-quality evidence, and final safety acceptance as separate
auditable boundaries.

## 17. Relationship to Step043 Accepted Boundary

Step-web-logger-043 accepted fixture contract validation boundary only.

Step-web-logger-044 designs Rust implementation strategy only and does not
expand the accepted boundary. Rust implementation must be separately accepted
later.

## 18. Relationship to Step031 Replay Integration

Step-web-logger-031 accepted the replay-focused UTF-16 offset conversion and
replay integration boundary.

Rust schema/validator position_unit policy is separate. The replay helper may
inform validator design, but replay pass does not prove schema validation, and
schema validation pass will not prove replay correctness.

## 19. Relationship to TypeScript Logger

Rust schema/validator policy assumes browser-originated position values are
UTF-16 code units.

The TypeScript logger must eventually emit explicit
`position_unit=utf16_code_unit`. This step does not implement TypeScript
changes. TypeScript/Rust compatibility remains separately staged.

## 20. Relationship to SHA-256 Hash Compatibility

This step does not implement Rust SHA-256 helper work, TypeScript SHA-256
helper work, or TypeScript/Rust vector checks.

It does not prove current TypeScript and Rust hashes match. SHA-256 UTF-8
lowercase hex compatibility remains separate.

## 21. Relationship to Event Durability

This step does not implement event durability.

Queue / IndexedDB / acknowledgement / retry / dedup remain unimplemented.
Server-side idempotency / event_id dedup remains unimplemented. Ordering and
delivery durability remains open.

## 22. No-Oracle / Synthetic-Only Boundary

Future work should use synthetic fixtures only. It must not introduce real
participant data, learner-originated raw text, final/observed-after text
fields, gold labels, or post-hoc annotation fields.

No test-set tuning is introduced. No model performance validation is
performed. No-oracle constraints remain unchanged.

## 23. Non-Equivalence Cautions

- Implementation design is not implementation.
- Rust schema design is not Rust schema behavior.
- Rust validator design is not Rust validator behavior.
- Fixture contract pass is not Rust implementation.
- Rust schema/validator implementation will not by itself prove replay
  correctness.
- Rust schema/validator implementation will not by itself prove TypeScript
  compatibility.
- Rust schema/validator implementation will not by itself prove hash
  compatibility.
- Rust schema/validator implementation will not prove event durability.
- Synthetic-only validation is not real-data readiness.
- Release-quality pass is not production readiness.

## 24. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- broader Unicode correctness completion
- validate integration completion
- extract integration completion
- micro_episode integration completion
- implemented schema-level position-unit policy behavior
- Rust schema position-unit behavior
- Rust validator position-unit behavior
- completed hash compatibility implementation
- TypeScript / Rust vector check implementation
- current TypeScript/Rust hash equality
- event durability implementation
- data collection readiness
- deployment readiness

## 25. Recommended Next Step

Recommended next step:

Step-web-logger-045: implement Rust schema position_unit field and parser
boundary

Clarification:

- Step-web-logger-045 should be an implementation step.
- Step-web-logger-045 should modify Rust schema code only as needed.
- Step-web-logger-045 may add focused Rust tests for `RawEvent`
  deserialization and parser behavior.
- Step-web-logger-045 should not yet implement full `kslog_validate` policy
  unless a revised design explicitly combines those boundaries.
- Step-web-logger-045 should not modify TypeScript code.
- Step-web-logger-045 should not modify fixture JSON unless a clear fixture
  metadata bug is found.
- Step-web-logger-045 should not modify Makefile / wrapper / CI.
- Step-web-logger-045 should update README and full technical specification
  related docs because implementation behavior changes.
- Step-web-logger-045 should not claim production readiness or real-data
  readiness.

## 26. Step-web-logger-045 Implementation Note

Step-web-logger-045 implements the first bounded Rust schema phase described
by this design. `kslog_schema::RawEvent` now accepts optional raw
`position_unit` and optional `research_schema_target` fields while preserving
unknown-field rejection. The schema crate also exposes body-free
`parse_position_unit()` / `position_unit_policy()` accessors that classify
supported `utf16_code_unit`, missing values, unsupported values, schema
mismatch, and unknown schema version with stable reason codes.

This implementation note does not convert the Step034 fixture contract into
Rust validator enforcement. UTF-16 numeric metadata checks, `kslog_validate`
policy enforcement, validate / extract / micro_episode integration,
TypeScript logger changes, SHA-256 helper work, TypeScript/Rust vector checks,
event durability, production readiness, real-data readiness, and model
performance evidence remain future work.

## 27. Step-web-logger-046 Validator Test / Fixture Mapping Design

Step-web-logger-046 adds
[Rust Validator Position Unit Policy Test and Fixture Mapping Design](web_logger_rust_validator_position_unit_policy_test_fixture_mapping_design.md).

The design uses the Step045 schema parser/accessor as input and maps the
Step034 fixed fixture matrix into Phase 1 validator enforcement cases and
Phase 2 deferred UTF-16 numeric metadata cases. It does not implement
`kslog_validate` behavior, change schema code, change tests, change fixtures,
change Makefile / wrapper / CI, or provide production readiness, real-data
readiness, or model performance evidence.

## 28. Step-web-logger-047 Validator Phase 1 Implementation Note

Step-web-logger-047 adds the bounded `kslog_validate` Phase 1 enforcement that
uses the Step045 parser/accessor boundary. The validator checks
fixture-targeted Web logger v0.2-style events after `RawEvent`
deserialization, requires explicit `position_unit=utf16_code_unit`, and fails
missing / unsupported / schema-mismatch / unknown-version cases with stable
body-free reason codes.

This note is limited to presence / value / schema-version gating. UTF-16
numeric metadata validation, `kslog_replay::utf16_offsets` dependency,
extract / micro_episode integration, TypeScript logger changes, fixture JSON
changes, Makefile changes, wrapper changes, event durability, production
readiness, real-data readiness, and model performance evidence remain outside
Step047.

## 29. Step-web-logger-048 Makefile Target Design

Step-web-logger-048 adds
[Rust Validator Position Unit Phase 1 Makefile Target Design](web_logger_rust_validator_position_unit_phase1_makefile_target_design.md).

The design plans future Makefile exposure for the Step047 focused validator
tests only. It does not modify schema behavior, validator behavior, Makefile,
wrapper, tests, fixtures, TypeScript, Python, Phase 2 UTF-16 numeric
validation, event durability, production readiness, real-data readiness, or
model performance evidence.

## 30. Step-web-logger-049 Makefile Target Implementation

Step-web-logger-049 adds Makefile target
`check-web-logger-rust-validator-position-unit-phase1` for the Step047
focused validator Phase 1 tests. The target command is
`cargo test -p kslog_validate position_unit_phase1` after the Step059 filter
correction.

This does not change schema behavior, validator behavior, Rust code, tests,
fixtures, wrapper behavior, Phase 2 UTF-16 numeric validation, event
durability, production readiness, real-data readiness, or model performance
evidence.

## 31. Step-web-logger-050 Release-Quality Integration Design

Step-web-logger-050 designs future release-quality integration for the Step049
target. The design keeps the schema parser/accessor boundary as prerequisite
context, but the planned wrapper check targets Rust validator Phase 1 behavior
rather than schema parsing alone.

This remains docs-only and does not change schema behavior, validator
behavior, wrapper behavior, Makefile behavior, fixtures, Phase 2 UTF-16
numeric validation, event durability, production readiness, real-data
readiness, or model performance evidence.

## 32. Step-web-logger-051 Release-Quality Integration

Step-web-logger-051 adds release-quality wrapper integration for the Rust
validator Phase 1 target. The schema parser/accessor boundary remains
prerequisite context, but the release-quality check runs validator focused
tests through Makefile rather than schema tests alone.

This does not change schema behavior, validator behavior, Makefile behavior,
fixtures, Phase 2 UTF-16 numeric validation, event durability, production
readiness, real-data readiness, or model performance evidence.

## 33. Step-web-logger-052 Run Record Workflow Design

Step-web-logger-052 designs future status marker evidence for the Rust
validator Phase 1 release-quality check. The schema parser/accessor boundary
remains prerequisite context, but the future status marker should record
validator focused-test evidence rather than schema-only evidence.

This does not change schema behavior, validator behavior, fixtures, status
marker files, Phase 2 UTF-16 numeric validation, event durability, production
readiness, real-data readiness, or model performance evidence.

## 34. Step-web-logger-053 Remote Status Marker

Step-web-logger-053 created
[Rust validator position_unit Phase 1 release-quality remote run status](status/web_logger_rust_validator_position_unit_phase1_release_quality_remote_run_status.md).
The marker records remote release-quality evidence for validator Phase 1 tests
that depend on the Step045 schema parser/accessor boundary.

This status marker does not change the schema boundary and does not claim that
the full schema-level `position_unit` policy is complete. Phase 2 UTF-16
numeric metadata validation, extract / micro_episode integration, TypeScript
logger compatibility, SHA-256 hash compatibility, event durability,
production readiness, real-data readiness, and model performance evidence
remain future work.

## 35. Step-web-logger-054 Final Safety Review

Step-web-logger-054 created
[Rust validator position_unit Phase 1 release-quality chain final safety review](web_logger_rust_validator_position_unit_phase1_release_quality_chain_final_safety_review.md).
The review accepts the validator Phase 1 chain that uses the Step045 schema
parser/accessor boundary.

This does not make schema parsing equivalent to full validator behavior and
does not complete Phase 2 UTF-16 numeric metadata validation, extract /
micro_episode integration, TypeScript logger compatibility, SHA-256
compatibility, event durability, production readiness, real-data readiness, or
model performance evidence.

## 36. Step-web-logger-055 Shared Helper Design

Step-web-logger-055 created
[Rust validator Phase 2 UTF-16 numeric metadata validation design](web_logger_rust_validator_phase2_utf16_numeric_metadata_validation_design.md).
The design recommends extracting reusable UTF-16 helper APIs into
`kslog_schema` before implementing validator Phase 2 numeric checks.

This keeps schema helper extraction separate from validator behavior and does
not claim Phase 2 validation, replay correctness, TypeScript compatibility,
event durability, production readiness, real-data readiness, or model
performance evidence.

## 37. Step-web-logger-056 Shared UTF-16 Helper Follow-Up

Step-web-logger-056 adds `kslog_schema::utf16_offsets` as the shared UTF-16
code unit length and offset/range conversion helper. `kslog_replay` keeps its
existing helper module path as a compatibility re-export of the schema helper.

This extends the schema crate with shared helper infrastructure only; it does
not change the Step045 `position_unit` parser/accessor boundary, does not
implement validator Phase 2 numeric metadata checks, and does not change
fixtures, Makefile, release-quality wrapper, TypeScript/Python code, SHA-256
helper work, TypeScript/Rust vector checks, event durability, production
readiness, real-data readiness, or model performance evidence.

## 38. Step-web-logger-057 Validator Phase 2 Follow-Up

Step-web-logger-057 uses the Step045 schema parser boundary and the Step056
shared UTF-16 helper to add bounded Phase 2 numeric metadata checks in
`kslog_validate`. `kslog_schema` remains the source for `position_unit`
classification and UTF-16 offset conversion helpers; no `kslog_validate ->
kslog_replay` dependency is introduced.

This does not change the schema parser boundary itself and does not add
extract / micro_episode integration, TypeScript logger changes, SHA-256 helper
work, TypeScript/Rust vector checks, event durability, production readiness,
real-data readiness, or model performance evidence.

## 39. Step-web-logger-058 Makefile Target Design Follow-Up

Step-web-logger-058 designs Makefile exposure for the validator behavior that
uses the schema parser boundary and shared UTF-16 helper. It recommends keeping
Phase 1 and Phase 2 focused targets separate with `position_unit_phase1` and
`position_unit_phase2` filters.

This follow-up does not change schema behavior and does not add wrapper
integration, extract / micro_episode integration, TypeScript logger changes,
SHA-256 helper work, TypeScript/Rust vector checks, event durability,
production readiness, real-data readiness, or model performance evidence.

## 40. Step-web-logger-059 Makefile Target Follow-Up

Step-web-logger-059 exposes the validator-side Phase 2 behavior through a
Makefile target and corrects the Phase 1 target filter. This does not change
the `kslog_schema` parser boundary or shared UTF-16 helper API.

The Phase 2 target is Makefile-only at this point and is not release-quality
integrated yet.

## 41. Step-web-logger-060 Release-Quality Design Follow-Up

Step-web-logger-060 designs future release-quality wrapper integration for the
validator Phase 2 Makefile target. It does not change the `kslog_schema`
parser/accessor boundary or shared UTF-16 helper API.

## 42. Step-web-logger-061 Release-Quality Integration Follow-Up

Step-web-logger-061 integrates the validator Phase 2 Makefile target into the
release-quality wrapper. This does not change the `kslog_schema`
parser/accessor boundary, `RawEvent` fields, or shared UTF-16 helper API.

## 43. Step-web-logger-062 Run Record Workflow Design Follow-Up

Step-web-logger-062 designs future status metadata for the Phase 2 wrapper
check. It does not change the `kslog_schema` parser/accessor boundary,
`RawEvent` fields, or shared UTF-16 helper API.

## 44. Step-web-logger-063 Status Marker Follow-Up

Step-web-logger-063 records public-safe remote metadata for the Phase 2
release-quality check. It does not change the `kslog_schema` parser/accessor
boundary, `RawEvent` fields, shared UTF-16 helper API, Rust code/tests,
fixtures, or wrapper behavior.

## 45. Step-web-logger-064 Final Safety Review Follow-Up

Step-web-logger-064 final-reviews the Phase 2 release-quality chain without
changing the `kslog_schema` parser/accessor boundary, `RawEvent` fields,
shared UTF-16 helper API, Rust code/tests, fixtures, or wrapper behavior.

## 46. Step-web-logger-065 TypeScript Compatibility Design Follow-Up

Step-web-logger-065 designs future TypeScript logger metadata alignment with
the existing Rust schema parser/accessor and validator boundaries. It does not
change `kslog_schema`, `RawEvent`, the shared UTF-16 helper API, Rust code,
TypeScript code, tests, fixtures, Makefile, wrapper, production readiness,
real-data readiness, or model performance evidence.

## 47. Step-web-logger-066 TypeScript Implementation Follow-Up

Step-web-logger-066 aligns the TypeScript logger with the existing Rust schema
boundary by emitting `logger_schema_version=kslog.raw_event.v2`,
`research_schema_target=web_logger_position_unit_schema_v0.1`, and
`position_unit=utf16_code_unit`. This does not change `kslog_schema`,
`RawEvent`, the shared UTF-16 helper API, Rust code/tests, fixtures, Makefile,
wrapper, production readiness, real-data readiness, or model performance
evidence.
