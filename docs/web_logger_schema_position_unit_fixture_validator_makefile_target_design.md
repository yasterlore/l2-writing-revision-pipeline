# Schema-Level Position Unit Fixture Validator Makefile Target Design

## 1. Title

Schema-Level Position Unit Fixture Validator Makefile Target Design

## 2. Scope

This is a Makefile-target-design / docs-only step.

This step makes no Makefile changes, no release-quality wrapper changes, no
Rust code changes, no TypeScript code changes, no Python code changes, no
tests changes, no fixture JSON changes, no CI workflow changes, and no
`package.json` / `Cargo.toml` / `Cargo.lock` changes.

This step makes no schema behavior changes, no validator behavior changes, no
replay behavior changes, no extract / micro_episode behavior changes, and no
event durability implementation. It provides no production readiness proof, no
real-data readiness proof, and no model performance proof.

## 3. Design Status

Step-web-logger-034 created the schema-level `position_unit` fixture root.
Step-web-logger-036 implemented the Python-first fixture validator. The direct
validator CLI currently passes, and focused validator tests currently pass.

This document designs the future Makefile target only. It does not add the
target, does not add release-quality integration, and does not implement Rust
`kslog_schema` / `kslog_validate` position-unit behavior.

## 4. Current Validator Audit

Current validator:

- module path: `python/web_logger_position_unit_fixture_validation.py`
- fixture root: `tests/fixtures/web_logger_position_unit_schema`
- CLI command:
  `PYTHONPATH=python python3 -m web_logger_position_unit_fixture_validation --fixture-root tests/fixtures/web_logger_position_unit_schema --summary-only`
- output mode: summary-only key=value metadata
- focused test file:
  `python/test_support/tests/test_web_logger_position_unit_fixture_validation.py`
- focused test count: 19

Expected direct CLI summary includes:

- `validation_status=pass`
- `total_cases=17`
- `valid_cases=5`
- `invalid_cases=11`
- `legacy_cases=1`
- `jsonl_record_count=24`
- `matched_cases=17`
- `mismatched_cases=0`
- expected and observed reason-code count fields
- `position_unit_policy_checked=true`
- `content_suppressed=true`
- `fixture_body_suppressed=true`
- no-oracle and synthetic-only safety count fields

Reason-code coverage includes `none`, `missing_position_unit`,
`unsupported_position_unit`, `position_unit_schema_mismatch`,
`doc_len_before_utf16_mismatch`, `doc_len_after_utf16_mismatch`,
`start_greater_than_end`, `offset_beyond_utf16_length`,
`offset_inside_surrogate_pair`, `unknown_schema_version`, and
`legacy_position_unit_missing_allowed`.

The validator fails nonzero on fixture contract mismatch and emits public-safe
metadata only. It validates fixture contracts only; it does not prove Rust
schema behavior, Rust validator behavior, replay correctness, TypeScript/Rust
compatibility, event durability, production readiness, real-data readiness, or
model performance.

## 5. Existing Web Logger Makefile Target Audit

Existing Web logger fixture target:

- target: `check-web-logger-unicode-hash-vector-fixtures`
- help text: `Run web logger Unicode/hash vector fixture validation`
- command:
  `PYTHONPATH=python python3 -m web_logger_unicode_hash_vector_validation --fixture tests/fixtures/web_logger_unicode_hash_vectors/vectors.json --summary-only`

The existing Web logger UTF-16 Rust target is adjacent in the Makefile help
listing and target body area. The release-quality wrapper currently runs the
Unicode/hash fixture target, then the Rust UTF-16 offset conversion and replay
integration target, then learner-state fixture chains.

The naming pattern for Web logger fixture validation targets is
`check-web-logger-...-fixtures`, with commands delegated to the purpose-built
validator module rather than duplicated wrapper logic.

## 6. Recommended Target Name

Recommended target:

`check-web-logger-position-unit-fixtures`

Why this is safer:

- short enough for normal Makefile usage
- clearly scoped to Web logger
- clearly scoped to `position_unit`
- clearly scoped to fixture validation
- does not imply Rust schema implementation
- does not imply Rust validator implementation
- does not imply extract / micro_episode integration
- does not imply TypeScript/Rust compatibility
- does not imply production readiness

Rejected alternatives:

- `check-web-logger-position-unit-schema`: too easy to read as schema behavior.
- `check-web-logger-schema-position-unit-fixtures`: accurate but longer than
  needed.
- `check-position-unit`: too broad and not Web logger scoped.
- `check-web-logger-unicode-position-unit`: mixes this fixture contract with
  broader Unicode/hash work.

## 7. Recommended Help Text

Recommended help text:

`Run Web logger position_unit fixture contract validation`

The help text should mention fixture contract validation. It should not say
Rust schema implementation, production validation, or full Web logger Unicode
correctness.

## 8. Recommended Command

Recommended command:

`PYTHONPATH=python python3 -m web_logger_position_unit_fixture_validation --fixture-root tests/fixtures/web_logger_position_unit_schema --summary-only`

The command should call the Python validator module, use the dedicated fixture
root, and require `--summary-only`. It should not write files, regenerate
fixtures, run Rust schema validation, run replay, run extract / micro_episode,
print fixture bodies, or fall back to weaker checks.

## 9. Target Placement

Recommended placement:

- near existing Web logger fixture targets
- adjacent to `check-web-logger-unicode-hash-vector-fixtures`
- before learner-state-specific target groups
- grouped with Web logger validation targets in both help text and target body

The future implementation should not reorder unrelated targets, remove
existing targets, alter existing target commands, or alter release-quality
wrapper behavior in the Makefile-target implementation step.

## 10. Should Target Run Focused Tests?

Preferred recommendation: the Makefile target should run the validator CLI
only.

Focused unit tests should remain covered by Python unittest and later
release-quality Python checks. The target's job is to validate the fixture root
contract, while focused tests validate the validator implementation. Keeping
the target CLI-only mirrors the existing Web logger Unicode/hash vector target,
avoids duplicate runtime, and keeps output compact.

## 11. Expected Target Output

Expected public-safe output fields include:

- `mode=web_logger_position_unit_fixture_validation`
- `validation_status=pass`
- `total_cases=17`
- `valid_cases=5`
- `invalid_cases=11`
- `legacy_cases=1`
- `jsonl_record_count=24`
- `matched_cases=17`
- `mismatched_cases=0`
- `input_error_cases=0`
- `expected_reason_code_counts=...`
- `observed_reason_code_counts=...`
- `position_unit_policy_checked=true`
- `content_suppressed=true`
- `fixture_body_suppressed=true`
- `synthetic_only_checked=true`
- `no_oracle_checked=true`
- `private_path_detected_count=0`
- `absolute_path_detected_count=0`
- `raw_payload_detected_count=0`
- `raw_learner_text_detected_count=0`
- `real_data_marker_detected_count=0`
- `logits_or_probabilities_detected_count=0`
- `performance_metric_body_detected_count=0`
- `production_readiness_claimed=False`
- `real_data_readiness_claimed=False`
- `performance_claims_present=False`

Forbidden output:

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

## 12. Failure Semantics

The target should fail nonzero when the validator fails due to:

- invalid case_index JSON
- invalid JSONL
- missing fixture file
- duplicate case ID
- fixture path escaping root
- count mismatch
- expected reason-code mismatch
- forbidden no-oracle field
- private / absolute path marker
- raw log / full job output marker
- logits / probabilities marker
- performance metric body marker
- position-unit policy mismatch
- UTF-16 metadata mismatch

The target should not repair fixtures, rewrite fixture files, regenerate
metadata, fall back to weaker checks, suppress failures, or print raw fixture
bodies.

## 13. Proposed Future Step-web-logger-038 Scope

Step-web-logger-038 should:

- modify Makefile only as needed
- add `.PHONY` entry for `check-web-logger-position-unit-fixtures`
- add help text `Run Web logger position_unit fixture contract validation`
- add command:
  `PYTHONPATH=python python3 -m web_logger_position_unit_fixture_validation --fixture-root tests/fixtures/web_logger_position_unit_schema --summary-only`
- place the target near the existing Web logger fixture validation target
- not modify Python validator
- not modify tests
- not modify fixtures
- not modify Rust code
- not modify TypeScript code
- not modify release-quality wrapper
- update README and full technical specification related docs because
  Makefile-visible behavior changes
- run `make help`
- run `make check-web-logger-position-unit-fixtures`
- run the direct validator CLI
- run focused tests if useful, but not as part of the target design
- confirm public-safe output

## 14. Future Release-Quality Staging

Recommended later staging:

- Step-web-logger-039: release-quality integration design
- Step-web-logger-040: release-quality wrapper integration
- Step-web-logger-041: remote/manual run record workflow design
- Step-web-logger-042: status marker
- Step-web-logger-043: final safety review

Do not add release-quality wrapper integration in Step-web-logger-038. Do not
create a status marker before release-quality integration exists.
Release-quality pass after target integration should remain bounded to fixture
contract validation and should not claim Rust schema / validator behavior.

## 15. Relationship To Step-web-logger-036 Validator Implementation

Step-web-logger-036 implemented the fixture contract validator. The Makefile
target will expose the direct validator CLI and will not expand validator
scope. Target pass will not prove Rust schema behavior, Rust validator
behavior, replay correctness, or production readiness.

## 16. Relationship To Step-web-logger-034 Fixture Root

Step-web-logger-034 created the fixture root. The target validates that fixture
root contract. It should not mutate the fixture root, regenerate fixture
metadata, or relax synthetic-only / no-oracle / public-safe boundaries.

## 17. Relationship To Step-web-logger-031 Replay Integration

Step-web-logger-031 accepted the `kslog_replay` focused replay boundary. The
position-unit fixture target is a schema fixture contract boundary. Replay pass
does not prove fixture contract, and fixture target pass does not prove replay
correctness. These boundaries remain distinct.

## 18. Relationship To Future Rust Schema / Validator Implementation

The Makefile target validates fixture contract only. Rust `kslog_schema` /
`kslog_validate` implementation remains future work. Target pass should not be
described as completed schema-level policy behavior. The fixture target can
become a prerequisite for future Rust validator implementation.

## 19. Relationship To TypeScript / Rust Hash/Helper Work

This target design does not implement a Rust SHA-256 helper, a TypeScript
SHA-256 helper, or TypeScript/Rust vector checks. It does not prove current
TypeScript and Rust hashes match. Hash compatibility remains separate.

## 20. Relationship To Event Durability

This target design does not implement event durability. Queue / IndexedDB /
acknowledgement / retry / dedup remain unimplemented. Server-side idempotency /
event_id dedup remains unimplemented. Ordering and delivery durability are not
solved.

## 21. Relationship To No-Oracle And Synthetic-Only Boundaries

The target must validate the synthetic-only / no-oracle fixture contract. It
must not introduce real participant data, print raw learner text, introduce
final/observed-after text fields, introduce gold-label or post-hoc annotation
fields, or perform model performance validation. No-oracle constraints are not
relaxed.

## 22. Non-Equivalence Cautions

- Makefile target design is not Makefile implementation.
- Makefile target pass will not prove Rust schema implementation.
- Makefile target pass will not prove Rust validator implementation.
- Makefile target pass will not prove replay correctness.
- Makefile target pass will not prove extract integration.
- Makefile target pass will not prove micro_episode integration.
- Makefile target pass will not prove TypeScript/Rust compatibility.
- Makefile target pass will not prove hash compatibility.
- Makefile target pass will not prove event durability.
- Synthetic-only fixture validation is not real-data readiness.
- Fixture validation is not production readiness.

## 23. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- broader Unicode correctness completion
- validate integration completion
- extract integration completion
- micro_episode integration completion
- completed schema-level position-unit policy behavior
- release-quality integration for the position-unit fixture target
- Rust schema position-unit behavior
- Rust validator position-unit behavior
- hash compatibility implementation completion
- TypeScript / Rust vector check implementation
- current TypeScript/Rust hash equality
- event durability implementation
- data collection readiness
- deployment readiness

## 24. Recommended Next Codex Step

Recommended next step:

Step-web-logger-038: add schema-level position_unit fixture validator Makefile
target

Clarification:

- Step-web-logger-038 should be an implementation step.
- It should modify Makefile.
- It should not modify Python validator unless a bug is found.
- It should not modify focused tests unless a target-related issue is found.
- It should not modify fixture JSON.
- It should not modify Rust code.
- It should not modify TypeScript code.
- It should not modify release-quality wrapper.
- It should update README and full technical specification related docs because
  Makefile-visible behavior changes.
- It should not claim Rust schema / validator implementation.
- It should not claim production readiness or real-data readiness.

## 25. Step-web-logger-038 Implementation Note

Step-web-logger-038 implements this design by adding Makefile target
`check-web-logger-position-unit-fixtures`.

Implemented target details:

- help text: `Run Web logger position_unit fixture contract validation`
- command:
  `PYTHONPATH=python python3 -m web_logger_position_unit_fixture_validation --fixture-root tests/fixtures/web_logger_position_unit_schema --summary-only`
- placement: near the existing Web logger fixture validation targets
- scope: CLI-only fixture contract validation

The target does not run focused unit tests, mutate fixtures, regenerate
metadata, add release-quality wrapper integration, implement Rust schema /
validator behavior, change validate / extract / micro_episode behavior, add
TypeScript/Rust hash checks, implement event durability, or provide production
readiness, real-data readiness, or model performance evidence.
