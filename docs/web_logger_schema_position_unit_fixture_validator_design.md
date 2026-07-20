# Schema-Level Position Unit Fixture Validator Design

## 1. Title

Schema-Level Position Unit Fixture Validator Design

## 2. Scope

This is a fixture-validator-design / docs-only step.

This step makes no Rust code changes, no TypeScript code changes, no Python
code changes, no tests changes, no fixture JSON changes, no Makefile changes,
no release-quality wrapper changes, no CI workflow changes, and no
`package.json` / `Cargo.toml` / `Cargo.lock` changes.

This step makes no schema behavior changes, no validator behavior changes, no
replay behavior changes, no extract / micro_episode behavior changes, and no
event durability implementation. It provides no production readiness proof, no
real-data readiness proof, and no model performance proof.

## 3. Design Status

Step-web-logger-034 created schema-level `position_unit` fixtures under
`tests/fixtures/web_logger_position_unit_schema/`.

This document designs the future fixture validator for that fixture root. It
does not implement the validator, modify fixtures, implement schema /
validator behavior, or change the accepted focused `kslog_replay` replay
boundary. Schema-level validation remains future work.

## 4. Fixture Root Audit

Audited fixture root:

- fixture root: `tests/fixtures/web_logger_position_unit_schema/`
- README: `tests/fixtures/web_logger_position_unit_schema/README.md`
- case index: `tests/fixtures/web_logger_position_unit_schema/case_index.json`
- valid directory: `tests/fixtures/web_logger_position_unit_schema/valid/`
- invalid directory: `tests/fixtures/web_logger_position_unit_schema/invalid/`
- legacy directory: `tests/fixtures/web_logger_position_unit_schema/legacy/`

Observed public-safe counts:

- valid count: 5
- invalid count: 11
- legacy count: 1
- total case count: 17
- JSONL record count: 24

`case_index.json` uses public-safe metadata only. It does not embed raw event
bodies. The root is synthetic-only and no-oracle safe by design.

## 5. Existing Validator Pattern Audit

The existing Web logger Unicode/hash fixture validator provides the best local
pattern for this future validator:

- Python-first module under `python/`
- CLI entrypoint with `python3 -m ...`
- explicit fixture path argument
- required `--summary-only` output mode
- public-safe key=value summary output
- count fields and reason-code-like status fields
- forbidden content marker scan
- no raw fixture body emission
- focused tests under `python/test_support/tests/`
- Makefile target staging after the direct CLI is stable
- release-quality staging only after Makefile target success

The current Makefile groups Web logger fixture checks near
`check-web-logger-unicode-hash-vector-fixtures`, and the release-quality
wrapper runs Web logger checks before learner-state fixture chains.

## 6. Recommended Validator Implementation Strategy

Preferred implementation strategy:

- Python-first validator
- module path: `python/web_logger_position_unit_fixture_validation.py`
- future CLI:
  `PYTHONPATH=python python3 -m web_logger_position_unit_fixture_validation --fixture-root tests/fixtures/web_logger_position_unit_schema --summary-only`
- focused tests:
  `python/test_support/tests/test_web_logger_position_unit_fixture_validation.py`

The validator should validate the fixture contract only. It should not
implement full `kslog_validate` behavior, mutate fixtures, regenerate expected
values, read real data, or print raw fixture bodies.

Python-first is safer at this stage because the goal is fixture contract
validation and public-safe summary output, not Rust schema behavior. It also
matches the existing Unicode/hash fixture validator pattern and allows fast
focused tests before any Rust crate boundary changes.

## 7. Validator Input Contract

Required argument:

- `--fixture-root`

Recommended optional arguments:

- `--summary-only`
- `--strict`
- `--allow-legacy`, if needed
- `--json-output`, optional future only and not required initially

Default output should be a public-safe summary. The validator should fail
nonzero on mismatch, write no files, modify no fixture root content, and avoid
normal workflows that accept arbitrary production data paths. If a fixture path
is reported, output should use a repository-relative path or suppress the path
value.

## 8. case_index Validation Rules

The future validator should check `case_index.json` for:

- valid JSON
- required top-level keys
- `fixture_schema_version=web_logger_position_unit_schema_fixtures_v0.1`
- `fixture_root=tests/fixtures/web_logger_position_unit_schema`
- `synthetic_only=true`
- `no_oracle_safe=true`
- `content_suppressed_expected=true`
- `position_unit_policy` present
- `cases` is a non-empty list
- unique case IDs
- relative `fixture_path` values
- fixture paths exist under the fixture root
- fixture paths do not escape the fixture root
- `case_kind` in `valid`, `invalid`, or `legacy`
- `expected_status` in the allowed set
- `expected_reason_code` present
- `logger_schema_version` present
- `research_schema_target` present
- `expected_position_unit_policy` present
- `requires_text_context` is boolean
- `should_be_checked_by_schema` is boolean
- `should_be_checked_by_validator` is boolean
- `should_be_checked_by_replay` is boolean
- `synthetic_only=true` for all cases
- `no_oracle_safe=true` for all cases
- `content_suppressed_expected=true` for all cases
- no raw event body embedded in case_index
- no expected body / request body / pointer body style fields
- no private or absolute path values

## 9. Fixture File Validation Rules

The future validator should check JSONL files for:

- file exists
- `.jsonl` extension
- every non-empty line parses as a JSON object
- file is not empty
- record count per case is at least 1
- required base fields present according to fixture design
- `case_id` linkage if records later include it
- monotonic `seq` fields within a file when present
- no forbidden no-oracle fields
- no raw log or full job output content
- no private or absolute local path
- no logits / probabilities
- no performance metric body
- no `final_text`
- no `observed_after_text`
- no gold-label fields
- no post-hoc annotation fields
- no raw learner text markers
- short synthetic text only

The validator must not print full fixture bodies.

## 10. Position Unit Policy Checks

The fixture contract should check:

- Web logger v0.2+ valid / invalid cases explicitly represent the position
  unit policy
- valid cases use `position_unit=utf16_code_unit`
- the invalid missing-position case omits `position_unit`
- unsupported unit cases use unsupported values such as `byte_index` and
  `code_point`
- the legacy case is explicitly marked as legacy, not as a v0.2 valid case
- missing `position_unit` is allowed only for legacy case metadata
- position unit values in case_index and fixture records are consistent where
  applicable
- unsupported values align with `expected_reason_code=unsupported_position_unit`
- schema mismatch case aligns with
  `expected_reason_code=position_unit_schema_mismatch`

## 11. UTF-16 Metadata Checks

The future fixture validator should perform bounded fixture-contract checks,
not full replay:

- compute UTF-16 code unit length for short synthetic text fields where enough
  context is available
- check `doc_len_before` and `doc_len_after` against computed UTF-16 lengths
  where possible
- check cursor / selection offsets are within UTF-16 length where possible
- detect `selection_start > selection_end`
- detect obvious offset beyond UTF-16 length
- detect surrogate-pair internal offset when the relevant text context is
  available
- identify byte-index-as-UTF-16 misuse when detectable
- report reason-code metadata only
- avoid full replay
- avoid claims of full validator behavior
- avoid claims of exhaustive Unicode correctness

Metadata-only checks include case counts, expected status / reason-code
coverage, field presence, path containment, and safety marker scans. Checks
requiring synthetic text context include UTF-16 length, offset range, surrogate
boundary, and detectable byte-index misuse checks. Rust schema / validator
responsibility remains future work.

## 12. Expected reason_code Coverage

Required expected reason codes:

- `none`
- `missing_position_unit`
- `unsupported_position_unit`
- `position_unit_schema_mismatch`
- `doc_len_before_utf16_mismatch`
- `doc_len_after_utf16_mismatch`
- `start_greater_than_end`
- `offset_beyond_utf16_length`
- `offset_inside_surrogate_pair`
- `invalid_utf16_boundary`
- `unknown_schema_version`
- `legacy_position_unit_missing_allowed`

The validator should report:

- `expected_reason_code_counts`
- `observed_reason_code_counts`
- `mismatched_reason_code_cases`
- `missing_reason_code_cases`
- `unknown_reason_code_cases`

Failures must not print raw fixture bodies.

## 13. Expected Case Counts

Expected Step-web-logger-034 fixture root counts:

- `total_cases=17`
- `valid_cases=5`
- `invalid_cases=11`
- `legacy_cases=1`
- `jsonl_record_count=24`

In strict mode, any count mismatch should fail. Initial implementation may also
fail by default because this root is intended to be a fixed contract.

Recommended count fields:

- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `pass_cases`
- `fail_cases`
- `legacy_allowed_cases`
- `text_context_cases`
- `schema_check_cases`
- `validator_check_cases`
- `replay_check_cases`

## 14. Public-Safe Output Design

Default `--summary-only` output should be key=value and include:

- `mode=web_logger_position_unit_fixture_validation`
- `fixture_schema_version`
- `validation_status`
- `total_cases`
- `valid_cases`
- `invalid_cases`
- `legacy_cases`
- `jsonl_record_count`
- `matched_cases`
- `mismatched_cases`
- `input_error_cases`
- `expected_reason_code_counts`
- `observed_reason_code_counts`
- `position_unit_policy_checked=true`
- `utf16_length_checked_count`
- `offset_boundary_checked_count`
- `surrogate_boundary_checked_count`
- `legacy_policy_checked=true`
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

## 15. Failure Semantics

The validator should fail nonzero when:

- case_index JSON is invalid
- JSONL parsing fails
- required top-level metadata is missing
- case ID is duplicated
- fixture path is missing
- fixture path escapes root
- expected count mismatches
- expected status mismatches
- expected reason code mismatches
- forbidden no-oracle field is detected
- private or absolute path is detected
- raw log or full job output content is detected
- logits / probabilities are detected
- performance metric body is detected
- fixture body is embedded in case_index
- position unit policy mismatches
- unsupported unit is not paired with the expected unsupported reason
- UTF-16 length / offset expected mismatch is not represented correctly

The validator should not repair fixtures, rewrite fixture files, regenerate
metadata, fall back to weaker checks, suppress failures, or print raw fixture
bodies.

## 16. Focused Tests Design

Future focused test file:

- `python/test_support/tests/test_web_logger_position_unit_fixture_validation.py`

Future test categories:

- valid fixture root passes
- expected total counts match
- duplicate case ID fails
- missing fixture path fails
- fixture path escaping root fails
- invalid JSONL fails
- missing required metadata fails
- missing position unit case is recognized
- unsupported position unit cases are recognized
- `doc_len_before` mismatch case is recognized
- `doc_len_after` mismatch case is recognized
- `start_greater_than_end` case is recognized
- `offset_beyond_utf16_length` case is recognized
- surrogate internal offset case is recognized
- legacy missing position unit is explicitly gated
- forbidden no-oracle fields fail
- private / absolute path markers fail
- output suppresses raw fixture body
- summary-only output contains only public-safe fields

No tests are created in this step.

## 17. Relationship To Future Rust Schema / Validator Implementation

The fixture validator validates the fixture contract, not production schema
behavior. Passing it would not mean `kslog_schema` implements `position_unit`,
would not mean `kslog_validate` implements `position_unit`, and would not prove
Rust validator behavior.

Step-web-logger-035 does not change Rust crates. A future Step-web-logger-037
or later may use these fixtures for Rust validation after separately staged
implementation work.

## 18. Relationship To Step-web-logger-034 Fixture Root

Step-web-logger-034 created the fixture root. Step-web-logger-035 designs a
validator for that root and does not alter fixtures.

The future validator should preserve Step-web-logger-034 synthetic-only,
no-oracle, and public-safe boundaries.

## 19. Relationship To Step-web-logger-032 / Step-web-logger-033 Designs

Step-web-logger-032 defined the schema-level position-unit policy.
Step-web-logger-033 defined the fixture matrix. Step-web-logger-034 created the
fixtures. Step-web-logger-035 designs fixture validation. These boundaries
remain distinct.

## 20. Relationship To Step-web-logger-031 Replay Integration

Step-web-logger-031 accepted the replay-focused `kslog_replay` boundary. This
fixture validator design is a schema/fixture boundary.

Replay pass does not prove the fixture contract. Future fixture validator pass
will not prove replay correctness. Schema-level validation remains future
work.

## 21. Relationship To TypeScript / Rust Hash/Helper Work

This fixture validator design does not implement a Rust SHA-256 helper, a
TypeScript SHA-256 helper, or TypeScript/Rust vector checks. It does not prove
current TypeScript and Rust hashes match. Hash compatibility remains separate.

## 22. Relationship To Event Durability

This fixture validator design does not implement event durability. Queue /
IndexedDB / acknowledgement / retry / dedup remain unimplemented. Server-side
idempotency / event_id dedup remains unimplemented. Ordering and delivery
durability are not solved.

## 23. Relationship To No-Oracle And Synthetic-Only Boundaries

The validator must treat fixtures as synthetic-only and scan for no-oracle
forbidden fields. It must not introduce real participant data, print raw
learner text, introduce final/observed-after text fields, introduce gold-label
or post-hoc annotation fields, or perform model performance validation.

No-oracle constraints are not relaxed.

## 24. Proposed Future Implementation Staging

Recommended staging:

- Step-web-logger-036: implement schema-level position_unit fixture validator
- Step-web-logger-037: Makefile target design for schema position_unit fixture
  validation
- Step-web-logger-038: add Makefile target
- Step-web-logger-039: release-quality integration design
- Step-web-logger-040: release-quality wrapper integration
- Step-web-logger-041: remote/manual run record workflow design
- Step-web-logger-042: status marker
- Step-web-logger-043: final safety review
- Later separate chain: implement `kslog_schema` / `kslog_validate`
  position_unit policy using these fixtures

Do not jump directly to release-quality integration before validator
implementation and Makefile target staging.

## 25. Non-Equivalence Cautions

- Fixture validator design is not validator implementation.
- Fixture validator pass will not prove Rust schema implementation.
- Fixture validator pass will not prove Rust validator implementation.
- Fixture validator pass will not prove replay correctness.
- Fixture validator pass will not prove extract integration.
- Fixture validator pass will not prove micro_episode integration.
- Fixture validator pass will not prove TypeScript/Rust compatibility.
- Fixture validator pass will not prove hash compatibility.
- Fixture validator pass will not prove event durability.
- Synthetic-only fixture validation is not real-data readiness.
- Fixture validation is not production readiness.

## 26. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- broader Unicode correctness completion
- validate integration completion
- extract integration completion
- micro_episode integration completion
- schema-level position_unit policy is already implemented
- schema-level position_unit validator is already implemented
- hash compatibility implementation completion
- TypeScript / Rust vector check implementation
- current TypeScript/Rust hash equality
- event durability implementation
- data collection readiness
- deployment readiness

## 27. Recommended Next Codex Step

Recommended next step:

Step-web-logger-036: implement schema-level position_unit fixture validator

Clarification:

- Step-web-logger-036 should be an implementation step.
- It should add `python/web_logger_position_unit_fixture_validation.py`.
- It should add focused tests under `python/test_support/tests/`.
- It should not modify fixture JSON unless the validator reveals a fixture
  metadata bug; any such fix must be minimal and reported.
- It should not modify Rust code.
- It should not modify TypeScript code.
- It should not modify Makefile.
- It should not modify release-quality wrapper.
- It should update README and full technical specification related docs
  because validator implementation is an implementation artifact.
- It should not claim Rust schema / validator implementation.
- It should not claim production readiness or real-data readiness.

## 28. Step-web-logger-036 Implementation Note

Step-web-logger-036 implements this design's Python-first fixture contract
validator at `python/web_logger_position_unit_fixture_validation.py` with
focused tests at
`python/test_support/tests/test_web_logger_position_unit_fixture_validation.py`.

The implemented CLI is:

`PYTHONPATH=python python3 -m web_logger_position_unit_fixture_validation --fixture-root tests/fixtures/web_logger_position_unit_schema --summary-only`

The validator checks the Step-web-logger-034 fixture contract only:
`case_index.json`, JSONL syntax, fixed counts, position-unit metadata, bounded
UTF-16 metadata expectations, expected reason-code counts, and no-oracle /
public-safe safety markers. It does not implement Rust `kslog_schema` or
`kslog_validate` behavior, add a Makefile target, add release-quality
integration, change fixture JSON, or alter validate / extract / micro_episode
boundaries.

## 29. Step-web-logger-037 Makefile Target Design

Step-web-logger-037 adds
[Schema-Level Position Unit Fixture Validator Makefile Target Design](web_logger_schema_position_unit_fixture_validator_makefile_target_design.md).

The design plans a future Makefile target named
`check-web-logger-position-unit-fixtures` with help text
`Run Web logger position_unit fixture contract validation` and command
`PYTHONPATH=python python3 -m web_logger_position_unit_fixture_validation --fixture-root tests/fixtures/web_logger_position_unit_schema --summary-only`.

The proposed target is CLI-only: it validates the fixture root contract through
the Step-web-logger-036 validator and leaves focused unit tests in the Python
test suite. Step-web-logger-037 does not add the Makefile target, change the
validator, change tests, change fixtures, add release-quality integration, or
implement Rust schema / validator behavior.

## 30. Step-web-logger-038 Makefile Target Implementation

Step-web-logger-038 adds Makefile target
`check-web-logger-position-unit-fixtures`.

The target runs the Step-web-logger-036 validator CLI in summary-only mode:

`PYTHONPATH=python python3 -m web_logger_position_unit_fixture_validation --fixture-root tests/fixtures/web_logger_position_unit_schema --summary-only`

The target validates the fixture contract only and does not run focused tests,
change the validator, change fixtures, add release-quality integration, or
implement Rust schema / validator behavior.

## 31. Step-web-logger-039 Release-Quality Integration Design

Step-web-logger-039 adds
[Schema-Level Position Unit Fixture Validator Release Quality Integration Design](web_logger_schema_position_unit_fixture_validator_release_quality_integration_design.md).

The design plans future wrapper integration through Makefile target
`check-web-logger-position-unit-fixtures` without duplicating the Python
command. It does not change the validator, focused tests, fixtures,
release-quality wrapper, or Rust schema / validator behavior in this step.

## 32. Step-web-logger-040 Release-Quality Integration

Step-web-logger-040 adds release-quality wrapper integration for the fixture
contract validator target.

The wrapper now calls `make check-web-logger-position-unit-fixtures` under
label `release_quality_check: web logger position_unit fixture contract validation`.
It does not change the validator, focused tests, fixtures, Makefile, Rust
schema / validator behavior, status markers, or final safety review.
