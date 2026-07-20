# Schema-Level Position Unit Policy Design for Web Logger Events

## 1. Title

Schema-Level Position Unit Policy Design for Web Logger Events

## 2. Scope

This is a design-only / docs-only step.

It does not change Rust, TypeScript, or Python code. It does not change tests,
fixture JSON, Makefile targets, release-quality wrapper behavior, CI workflow
files, package metadata, Cargo metadata, runtime behavior, replay behavior,
validation behavior, extraction behavior, micro_episode behavior, event
durability, or schema serialization behavior.

It does not prove production readiness, real-data readiness, model performance,
TypeScript/Rust compatibility, or event durability.

## 3. Design Status

The `kslog_replay` replay-focused UTF-16 boundary was accepted in
Step-web-logger-031 for the focused replay scope only.

Schema-level `position_unit` policy is not yet implemented. This document
designs a future schema and validation policy for browser-originated Web logger
events. It does not modify fixtures and does not claim TypeScript/Rust
compatibility.

## 4. Current Accepted Replay Boundary Recap

Step-web-logger-024 integrated the existing Rust UTF-16 offset helper inside
`kslog_replay`. Replay now treats cursor and selection offsets as UTF-16 code
unit offsets, converts them to UTF-8 byte ranges before Rust string indexing,
checks replay document length as UTF-16 code unit length, and fail-closes
surrogate-pair internal offsets, offsets beyond the UTF-16 document length, and
`start > end`.

Step-web-logger-030 recorded public-safe remote release-quality metadata for the
updated wrapper label, and Step-web-logger-031 accepted that chain only for the
focused `kslog_replay` boundary.

## 5. Current Schema and Validator Audit

`crates/kslog_schema/src/lib.rs` currently defines `RawEvent` with
`logger_schema_version`, cursor fields, selection fields, document length fields,
text hash fields, edit hints, and quality flags. It uses `deny_unknown_fields`.
There is currently no `position_unit` field in `RawEvent`.

`crates/kslog_validate/src/lib.rs` currently validates JSONL structure,
no-oracle-forbidden fields, schema parsing, sequence order, timestamp order,
cursor bounds against document length, selection order, and selection bounds
against document length. It does not currently distinguish whether those
positions are UTF-16 code units, Unicode scalar values, grapheme clusters, or
UTF-8 bytes.

The current validator can reject numeric ranges that exceed provided document
length fields, but it cannot enforce browser-originated UTF-16 semantics without
a schema field and policy.

## 6. Current Replay / Extract / Micro-Episode Relationship Audit

`kslog_replay` now resolves replay-local cursor and selection offsets with the
UTF-16 helper before string replacement and slicing.

`kslog_extract` calls `replay_events` before classification, then constructs
revision spans from the raw cursor and selection metadata. It does not yet carry
an explicit position-unit field into revision spans.

`kslog_micro_episode` consumes revision events and uses character-indexed local
context and replacement helpers. It is not yet integrated with a schema-level
`position_unit` policy or the UTF-16 conversion helper.

Therefore, schema-level policy should be designed before extending the UTF-16
position contract into `kslog_validate`, `kslog_extract`, or
`kslog_micro_episode`.

## 7. Position Unit Field Policy

Future Web logger events should use an explicit field named `position_unit`.

Recommended initial supported value:

- `utf16_code_unit`

For browser-originated Web logger events, cursor, selection, and document length
positions should be interpreted as JavaScript string UTF-16 code unit offsets
when `position_unit=utf16_code_unit`.

Policy:

- Use an explicit finite allowed-value set.
- Reject unsupported values fail-closed.
- Do not infer missing `position_unit` for new Web logger schema versions.
- Do not fallback to byte indices.
- Do not round, repair, or coerce invalid offsets.
- Keep diagnostics metadata-only and content-suppressed.

Future values such as grapheme-cluster or UTF-8 byte indexing require separate
schema design, validation design, implementation, tests, and safety review.

## 8. Schema Version Policy

Recommended future schema policy:

- Keep legacy `kslog.raw_event.v1` behavior explicitly gated.
- Introduce a future Web logger schema version that requires
  `position_unit=utf16_code_unit` for browser-originated events.
- Treat missing `position_unit` in that future schema version as a schema or
  usage error.
- Treat unknown schema versions according to the existing schema-version policy
  or, if no sufficient policy exists, add a focused schema clarification step
  before implementation.
- Never silently interpret missing `position_unit` as UTF-16, UTF-8 bytes, or
  character counts.

If the current schema fields are insufficient to distinguish legacy and future
Web logger events, the next implementation chain should begin with fixture and
schema-version design rather than changing validation behavior immediately.

## 9. Recommended Validation Policy

Future validation should:

- Require `position_unit=utf16_code_unit` for the future Web logger event schema.
- Validate cursor and selection presence according to existing event-type rules.
- Validate `start <= end` for selection ranges.
- Validate cursor and selection offsets against UTF-16 document length fields.
- Validate `doc_len_before` and `doc_len_after` as UTF-16 code unit counts when
  source text is available to a safe synthetic test or replay context.
- Preserve existing no-oracle field rejection.
- Emit only metadata/count-safe diagnostics.

If validation needs full UTF-16 boundary conversion, the helper should either be
moved to a small shared crate or duplicated behind a deliberately tiny
schema-adjacent utility after a separate crate-boundary design. `kslog_validate`
should not acquire an awkward dependency on `kslog_replay` solely to reuse this
helper.

## 10. Recommended Error Semantics

Recommended public-safe reason codes:

- `missing_position_unit`: required field absent for the future Web logger
  schema.
- `unsupported_position_unit`: field has a value outside the allowed set.
- `position_unit_schema_mismatch`: field value is incompatible with the event
  schema version.
- `offset_beyond_utf16_length`: cursor or selection offset exceeds UTF-16
  document length.
- `offset_inside_surrogate_pair`: offset lands inside a non-BMP scalar value.
- `start_greater_than_end`: range start exceeds range end.
- `doc_len_before_utf16_mismatch`: before-length does not match UTF-16 length in
  a context that can safely verify it.
- `doc_len_after_utf16_mismatch`: after-length does not match UTF-16 length in a
  context that can safely verify it.
- `invalid_utf16_boundary`: offset is within length but not a valid UTF-16 scalar
  boundary.
- `legacy_position_unit_missing_allowed`: metadata note only, if a legacy path is
  explicitly allowed.
- `unknown_schema_version`: schema version cannot be safely classified.
- `malformed_event`: event cannot be parsed or violates basic shape.

Higher-level callers should classify these as schema validation errors,
usage errors, or fail-closed replay/validation errors according to existing
crate terminology. Errors must not include raw source text, selected text,
inserted/deleted text, or full event payloads.

## 11. Crate Boundary and Dependency Strategy

Recommended strategy:

- Do not move the existing `kslog_replay` helper in this design step.
- First design the schema field and validator behavior in `kslog_schema` /
  `kslog_validate`.
- If validation implementation needs full UTF-16 boundary mapping, create a
  separate helper relocation or shared-utility design.
- Avoid broad cross-crate refactors during the first schema policy
  implementation.
- Keep dependency direction simple: schema types should remain data-shape
  oriented, validation should remain deterministic, and replay should remain the
  owner of reconstruction behavior.

## 12. Fixture Policy

Do not modify `tests/fixtures/web_logger_unicode_hash_vectors/vectors.json` for
this policy design.

Future fixture work should be a separate step. Recommended next fixture design:

- Use synthetic-only events.
- Include explicit `position_unit=utf16_code_unit`.
- Include legacy missing-field cases only when the legacy path is intentionally
  gated.
- Include unsupported-position-unit cases.
- Include surrogate-pair internal offset failures.
- Include beyond-length failures.
- Include `start > end` failures.
- Exclude real participant data, raw learner text, final text labels, observed
  after text, gold labels, post-hoc annotations, logits, probabilities, and
  performance metric bodies.

## 13. Proposed Future Tests

Future focused tests should cover:

- future Web logger schema event accepts `position_unit=utf16_code_unit`
- future Web logger schema event rejects missing `position_unit`
- unsupported `position_unit` fail-closes
- legacy schema missing `position_unit` is handled only through an explicit gate
- cursor offset equal to UTF-16 length is accepted
- cursor offset beyond UTF-16 length fails
- selection `start > end` fails
- surrogate-pair internal offset fails when safe source text is available
- Japanese and emoji offsets are interpreted as UTF-16 code units
- diagnostics include reason codes and numeric metadata only
- no raw source text, selected text, or event payload body appears in failures
- existing no-oracle field rejection remains active

## 14. Proposed Future Implementation Staging

Recommended staged chain:

- Step-web-logger-033: schema-level position_unit fixture design for Web logger
  events.
- Step-web-logger-034: implement schema / validator position_unit policy with
  focused tests.
- Step-web-logger-035: Makefile target design for schema-level policy checks.
- Step-web-logger-036: add the Makefile target.
- Step-web-logger-037: release-quality integration design.
- Step-web-logger-038: integrate the wrapper check.
- Step-web-logger-039: remote/manual run record workflow design.
- Step-web-logger-040: status marker.
- Step-web-logger-041: final safety review.

Do not move directly to validate / extract / micro_episode runtime integration
without separate design.

## 15. Relationship to Step-web-logger-031

Step-web-logger-031 accepted the `kslog_replay` focused replay boundary with
release-quality and remote-status evidence. It left schema-level
`position_unit` policy as a remaining P0 gap.

This design addresses that remaining gap at the planning level only. It does
not expand the Step-web-logger-031 accepted boundary.

## 16. Relationship to Focused Helper Chain

The Step-web-logger-014 through Step-web-logger-022 helper chain remains valid
for focused UTF-16 offset conversion helper tests. The helper chain does not by
itself establish schema policy.

The schema-level policy should reuse the same UTF-16 semantics but must have its
own fixtures, tests, release-quality evidence, status marker, and safety review.

## 17. Relationship to Validate / Extract / Micro-Episode Integration

This design does not integrate `kslog_validate`, `kslog_extract`, or
`kslog_micro_episode`.

Future validation should come first because it establishes the schema-level
contract. Future extraction and micro_episode integration should then decide how
to represent spans and context windows without silently changing units.

## 18. Relationship to TypeScript / Rust Hash/Helper Work

This design does not implement Rust SHA-256 hashing, TypeScript SHA-256 hashing,
or TypeScript/Rust vector checks.

Schema-level `position_unit` policy is related to cursor and selection offsets,
not hash compatibility. Hash work remains a separate chain.

## 19. Relationship to Event Durability

This design does not implement queueing, IndexedDB buffering, acknowledgement,
retry, deduplication, server-side idempotency, or event ordering guarantees.

Position-unit policy may make events more interpretable once received, but it
does not solve delivery durability.

## 20. Relationship to No-Oracle and Synthetic-Only Boundaries

The policy does not relax no-oracle constraints.

Future fixtures should remain synthetic-only and must not introduce real
participant data, raw learner text, final text, observed-after text, gold
labels, post-hoc annotations, test-set tuning, logits, probabilities, or model
performance validation.

## 21. Public-Safe Diagnostics Policy

Allowed diagnostics:

- reason code
- schema version
- `position_unit` value when not sensitive
- event type
- field name
- line number
- sequence number
- numeric UTF-16 offset metadata
- numeric document length metadata
- count summaries

Forbidden diagnostics:

- raw source text
- selected raw text
- inserted/deleted raw text in normal summaries
- raw event payload body
- full fixture JSON body
- private paths
- absolute local paths
- raw learner text
- real participant data
- logits / probabilities
- performance metric body

## 22. Failure Interpretation

Missing or unsupported `position_unit` in a future schema should indicate that
the event cannot be safely interpreted under the Web logger position policy.

Passing schema-level position-unit checks would mean only that the future schema
and validation boundary accepted the event metadata under the scoped policy. It
would not prove replay correctness, extraction correctness, micro_episode
correctness, TypeScript/Rust compatibility, hash compatibility, event
durability, production readiness, or real-data readiness.

## 23. Non-Equivalence Cautions

- Schema policy design is not schema implementation.
- Schema policy implementation would not by itself prove replay correctness.
- Replay-focused pass is not validation integration.
- Validation integration is not extraction integration.
- Extraction integration is not micro_episode integration.
- `position_unit=utf16_code_unit` is not hash compatibility.
- Synthetic-only fixtures are not real-data readiness.
- Release-quality pass is not production readiness.
- Status markers are not raw evidence.
- This design does not authorize real data collection.

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
- schema-level position_unit policy completion
- hash compatibility implementation completion
- TypeScript / Rust vector check implementation
- current TypeScript/Rust hash equality
- event durability implementation
- data collection readiness
- deployment readiness

## 25. Recommended Next Codex Step

Recommended next step:

Step-web-logger-033: schema-level position_unit fixture design for Web logger events

Clarification:

- Step-web-logger-033 should be design-only / docs-only.
- It should design synthetic schema / validator fixtures for explicit
  `position_unit=utf16_code_unit`.
- It should not modify schema code.
- It should not modify validation code.
- It should not modify replay code.
- It should not modify existing fixture JSON unless a later fixture
  implementation step explicitly allows it.
- It should not implement validate / extract / micro_episode integration.
- It should not implement TypeScript/Rust hash checks.
- It should not implement event durability.

## 26. Step-web-logger-033 Schema-Level Position Unit Fixture Design

Step-web-logger-033 adds [Schema-Level Position Unit Fixture Design for Web Logger Events](web_logger_schema_position_unit_fixture_design.md).

The fixture design translates this policy into a future synthetic valid / invalid / legacy fixture matrix for schema and validator work. It does not create fixtures, modify fixture JSON, implement schema behavior, implement validator behavior, change replay, or alter release-quality checks.

## 27. Step-web-logger-034 Fixture Root

Step-web-logger-034 adds the dedicated synthetic fixture root
`tests/fixtures/web_logger_position_unit_schema/` for this policy.

The root contains README guidance, `case_index.json`, and a 17-case valid /
invalid / legacy JSONL matrix for future Web logger
`position_unit=utf16_code_unit` schema and validator checks. It does not
implement schema behavior, validation behavior, fixture validator CLI,
Makefile target, release-quality wrapper changes, validate / extract /
micro_episode integration, TypeScript/Rust hash work, event durability,
production readiness, real-data readiness, or model performance evidence.

## 28. Step-web-logger-035 Fixture Validator Design

Step-web-logger-035 adds
[Schema-Level Position Unit Fixture Validator Design](web_logger_schema_position_unit_fixture_validator_design.md).

The design translates the Step-web-logger-032 policy and Step-web-logger-034
fixture root into a future validator plan. It does not implement schema
behavior, validation behavior, fixture validator CLI, code changes, tests,
Makefile target, release-quality wrapper changes, event durability,
production readiness, real-data readiness, or model performance evidence.

## 29. Step-web-logger-036 Fixture Validator Implementation

Step-web-logger-036 adds a Python-first fixture contract validator for
`tests/fixtures/web_logger_position_unit_schema/`.

The validator checks the fixture-level `position_unit=utf16_code_unit` contract
and bounded UTF-16 metadata expectations. It does not implement Rust schema
behavior, Rust validation behavior, Makefile target, release-quality wrapper
changes, validate / extract / micro_episode integration, event durability,
production readiness, real-data readiness, or model performance evidence.

## 30. Step-web-logger-037 Makefile Target Design

Step-web-logger-037 adds
[Schema-Level Position Unit Fixture Validator Makefile Target Design](web_logger_schema_position_unit_fixture_validator_makefile_target_design.md).

The design plans a future Makefile target for the Python-first fixture contract
validator. The recommended target is
`check-web-logger-position-unit-fixtures`, with help text
`Run Web logger position_unit fixture contract validation`, calling the
summary-only validator CLI over `tests/fixtures/web_logger_position_unit_schema/`.
This remains a fixture contract boundary and does not implement Rust schema
behavior, Rust validation behavior, release-quality wrapper changes, validate /
extract / micro_episode integration, event durability, production readiness,
real-data readiness, or model performance evidence.

## 31. Step-web-logger-038 Makefile Target Implementation

Step-web-logger-038 adds Makefile target
`check-web-logger-position-unit-fixtures`.

The target exposes the Python-first fixture contract validator for
`tests/fixtures/web_logger_position_unit_schema/` through summary-only CLI
output. It does not add release-quality wrapper integration, implement Rust
schema behavior, implement Rust validation behavior, change validate / extract
/ micro_episode behavior, implement event durability, or provide production
readiness, real-data readiness, or model performance evidence.

## 32. Step-web-logger-039 Release-Quality Integration Design

Step-web-logger-039 adds
[Schema-Level Position Unit Fixture Validator Release Quality Integration Design](web_logger_schema_position_unit_fixture_validator_release_quality_integration_design.md).

The design plans future wrapper integration for the fixture contract validator
target only. It does not implement Rust schema behavior, implement Rust
validation behavior, modify the wrapper in this step, change validate /
extract / micro_episode behavior, implement event durability, or provide
production readiness, real-data readiness, or model performance evidence.

## 33. Step-web-logger-040 Release-Quality Integration

Step-web-logger-040 adds release-quality wrapper integration for the
position-unit fixture contract target.

The check remains bounded to fixture contract validation. It does not
implement Rust schema behavior, implement Rust validation behavior, change
validate / extract / micro_episode behavior, create a status marker, create a
final safety review, implement event durability, or provide production
readiness, real-data readiness, or model performance evidence.

## 34. Step-web-logger-041 Run Record Workflow Design

Step-web-logger-041 adds
[Schema-Level Position Unit Fixture Validator Release Quality Remote/Manual Run Record Workflow](web_logger_schema_position_unit_fixture_validator_release_quality_remote_run_record_workflow.md).

The workflow design plans future status-marker evidence for the fixture
contract target only. It does not implement Rust schema behavior, implement
Rust validation behavior, change validate / extract / micro_episode behavior,
create a status marker, create a final safety review, implement event
durability, or provide production readiness, real-data readiness, or model
performance evidence.

## 35. Step-web-logger-042 Remote Status Marker

Step-web-logger-042 adds
[Schema-Level Position Unit Fixture Validator Release Quality Remote Run Status](status/web_logger_schema_position_unit_fixture_validator_release_quality_remote_run_status.md).

The marker records public-safe remote release-quality evidence for the fixture
contract target only. It does not implement Rust schema behavior, implement
Rust validation behavior, change validate / extract / micro_episode behavior,
create a final safety review, implement event durability, or provide
production readiness, real-data readiness, or model performance evidence.

## 36. Step-web-logger-043 Final Safety Review

Step-web-logger-043 adds
[Schema-Level Position Unit Fixture Validator Release Quality Chain Final Safety Review](web_logger_schema_position_unit_fixture_validator_release_quality_chain_final_safety_review.md).

The review accepts only the bounded fixture-contract validation boundary. It
does not implement Rust schema behavior, implement Rust validation behavior,
change validate / extract / micro_episode behavior, implement event
durability, or provide production readiness, real-data readiness, or model
performance evidence.

## 37. Step-web-logger-044 Rust Implementation Design

Step-web-logger-044 adds
[Rust Schema-Level Position Unit Policy Implementation Design](web_logger_rust_schema_position_unit_policy_implementation_design.md).

The design recommends a staged Rust path: first add schema field / parser
boundary for position_unit and target metadata, then implement validator
presence/value/version gating, and defer numeric UTF-16 metadata checks until a
shared helper strategy is designed. It does not implement Rust schema
behavior, implement Rust validation behavior, change validate / extract /
micro_episode behavior, implement event durability, or provide production
readiness, real-data readiness, or model performance evidence.

## 38. Step-web-logger-045 Rust Schema Boundary

Step-web-logger-045 implements the first Rust schema-stage boundary for this
policy. `kslog_schema::RawEvent` accepts optional raw `position_unit` and
`research_schema_target`, and `kslog_schema` exposes parser/accessor functions
for supported `utf16_code_unit`, missing value, unsupported value, schema
mismatch, and unknown schema version classification.

This remains a schema parser boundary only. Rust validator policy enforcement,
UTF-16 numeric metadata validation, validate / extract / micro_episode
integration, TypeScript logger changes, SHA-256 helper work, TypeScript/Rust
vector checks, event durability, production readiness, real-data readiness,
and model performance evidence remain future work.

## 39. Step-web-logger-046 Rust Validator Test Mapping Design

Step-web-logger-046 adds
[Rust Validator Position Unit Policy Test and Fixture Mapping Design](web_logger_rust_validator_position_unit_policy_test_fixture_mapping_design.md).

The design defines the next `kslog_validate` Phase 1 test and fixture mapping
for presence / value / schema-version gating. It explicitly defers UTF-16
numeric metadata validation, shared helper placement, extract / micro_episode
integration, TypeScript logger changes, event durability, production
readiness, real-data readiness, and model performance evidence.

## 40. Step-web-logger-047 Rust Validator Phase 1 Enforcement

Step-web-logger-047 adds the bounded `kslog_validate` Phase 1 enforcement for
this policy. Fixture-targeted Web logger v0.2-style events now require
explicit `position_unit=utf16_code_unit`; missing, unsupported,
schema-mismatch, and unknown-version cases fail with stable body-free reason
codes. Existing legacy synthetic fixtures are not made subject to a global
position-unit requirement.

This remains presence / value / schema-version gating only. UTF-16 numeric
metadata validation, `kslog_replay::utf16_offsets` dependency, extract /
micro_episode integration, TypeScript logger changes, fixture JSON changes,
Makefile / wrapper changes, event durability, production readiness,
real-data readiness, and model performance evidence remain outside Step047.

## 41. Step-web-logger-048 Rust Validator Phase 1 Makefile Target Design

Step-web-logger-048 adds
[Rust Validator Position Unit Phase 1 Makefile Target Design](web_logger_rust_validator_position_unit_phase1_makefile_target_design.md).

The design plans a future focused Makefile target for the Step047 validator
Phase 1 tests. It does not implement the target, does not add release-quality
integration, and does not change Phase 2 UTF-16 numeric validation, replay,
extract / micro_episode, TypeScript logger behavior, event durability,
production readiness, real-data readiness, or model performance evidence.

## 42. Step-web-logger-049 Rust Validator Phase 1 Makefile Target

Step-web-logger-049 adds Makefile target
`check-web-logger-rust-validator-position-unit-phase1` with command
`cargo test -p kslog_validate position_unit`. It exposes the Step047 focused
validator Phase 1 tests without expanding the policy to Phase 2 UTF-16
numeric validation.

Release-quality integration, extract / micro_episode integration, TypeScript
logger behavior, event durability, production readiness, real-data readiness,
and model performance evidence remain future work.

## 43. Step-web-logger-050 Rust Validator Phase 1 Release-Quality Integration Design

Step-web-logger-050 designs how the Step049 target should be added to the
future release-quality wrapper. The planned label is scoped to Rust validator
`position_unit` Phase 1 policy and should be inserted after the fixture
contract validation check and before Rust UTF-16 replay integration.

This does not make the full schema-level position_unit policy complete.
Phase 2 UTF-16 numeric validation, extract / micro_episode integration,
TypeScript logger behavior, event durability, production readiness, real-data
readiness, and model performance evidence remain future work.

## 44. Step-web-logger-051 Rust Validator Phase 1 Release-Quality Integration

Step-web-logger-051 integrates the Rust validator Phase 1 target into the
release-quality wrapper. The check remains scoped to presence / value /
schema-version gating and runs through
`make check-web-logger-rust-validator-position-unit-phase1`.

This still does not make the full schema-level position_unit policy complete.
Phase 2 UTF-16 numeric validation, extract / micro_episode integration,
TypeScript logger behavior, status marker evidence, final safety review,
event durability, production readiness, real-data readiness, and model
performance evidence remain future work.
