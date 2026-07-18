# Web Logger Unicode and Hash Vector Fixture Validator Design

## 1. Title

Web Logger Unicode and Hash Vector Fixture Validator Design

## 2. Scope

This is a validator-design / docs-only step.

Out of scope:

- no validator implementation
- no TypeScript code changes
- no Rust code changes
- no Python code changes
- no tests changes
- no fixture JSON changes
- no schema implementation changes
- no runtime implementation changes
- no CI workflow changes
- no Makefile changes
- no release-quality wrapper changes
- no real data
- no raw learner text
- no production readiness proof
- no real-data readiness proof
- no model performance proof

## 3. Design Status

This document designs a future validator for the existing shared vector fixture at `tests/fixtures/web_logger_unicode_hash_vectors/vectors.json`.

This document does not:

- implement the validator
- modify `vectors.json`
- claim TypeScript / Rust helper compatibility
- create tests
- add a Makefile target
- add a release-quality check

Future implementation and focused tests are required before the validator can be used as repeatable evidence.

## 4. Validator Goals

The future validator should:

- ensure `vectors.json` is structurally valid
- ensure top-level metadata matches the schema clarification policy
- ensure all vector IDs are unique
- ensure all hashes match SHA-256 over decoded UTF-8 source text
- ensure UTF-16 code unit lengths are correct
- ensure UTF-8 byte lengths are correct
- ensure valid UTF-16 offsets map to expected UTF-8 byte offsets
- ensure invalid offsets are represented as expected failures
- ensure forbidden data surfaces are not present in the fixture
- ensure diagnostics are public-safe and metadata-only
- prepare future TypeScript / Rust cross-language checks

The validator should make the Step-web-logger-004 manual fixture checks repeatable without becoming a substitute for future TypeScript or Rust helper validation.

## 5. Proposed Future Validator Location

Option A: Python validator first

- `python/web_logger_unicode_hash_vector_validation.py`
- `python/test_support` helper if needed
- focused tests under `python/test_support/tests/` or a suitable existing test directory

Option B: Rust validator first

- `crates/kslog_validate` or a new Rust module
- Rust tests in the relevant crate

Option C: TypeScript validator first

- `apps/logger-web/src` or test utilities

Recommended first path: Option A.

Reason:

- A Python validator can validate fixture metadata, hashes, lengths, and offset expectations without changing replay or runtime code.
- It can be introduced as an isolated fixture validator before Rust and TypeScript helper work.
- Later Rust and TypeScript checks can reuse the fixture after the fixture contract is stable.

Step-web-logger-005 does not create these files.

## 6. Proposed Future CLI

Example future command:

```bash
PYTHONPATH=python python3 -m web_logger_unicode_hash_vector_validation \
  --fixture tests/fixtures/web_logger_unicode_hash_vectors/vectors.json \
  --summary-only
```

CLI requirements:

- parse JSON
- validate top-level metadata
- validate vector count
- validate hash values
- validate UTF-16 length
- validate UTF-8 length
- validate offset mappings
- validate expected failures
- scan for forbidden data markers
- emit public-safe summary only
- avoid raw source text in normal output
- exit nonzero on validation failure
- keep output deterministic

Proposed output fields:

- `mode`
- `schema_version`
- `status`
- `reason_code`
- `vector_count`
- `valid_offset_case_count`
- `expected_failure_count`
- `hash_checked_count`
- `utf16_length_checked_count`
- `utf8_length_checked_count`
- `offset_mapping_checked_count`
- `invalid_offset_case_count`
- `forbidden_content_detected_count`
- `real_data_marker_detected_count`
- `private_path_detected_count`
- `absolute_path_detected_count`
- `raw_payload_detected_count`
- `content_suppressed`
- `public_safe_output`
- `production_readiness_claimed`
- `real_data_readiness_claimed`
- `performance_claims_present`

The proposed summary should report counts and booleans only.

## 7. Top-Level Metadata Validation

The future validator must require:

- `vector_schema_version=web_logger_unicode_hash_vectors_v0.1`
- `position_unit=utf16_code_unit`
- `hash_algorithm=SHA-256`
- `hash_encoding=UTF-8`
- `unicode_normalization=none`
- `newline_normalization=none`
- `trailing_newline_policy=preserve_as_is`
- `hash_output_format=lowercase_hex`
- `source_text_policy=synthetic_minimal_text_only`
- `real_data_allowed=false`
- `vectors` is a non-empty array

Fail closed if:

- a required field is missing
- schema version is unsupported
- position unit is unsupported
- hash algorithm is unsupported
- encoding is unsupported
- normalization policy differs
- `real_data_allowed` is not false
- `vectors` is missing or empty

Unsupported schema version should be treated as `usage_error` when the file is clearly not for this validator, and as `fail_closed` when the validator cannot safely determine the intended policy.

## 8. Vector-Level Validation

Every vector must include:

- `vector_id`
- `category`
- `priority`
- `source_text`
- `source_text_description`
- `utf16_code_unit_length`
- `utf8_byte_length`
- `code_point_count`
- `hash_sha256_utf8_lowercase_hex`
- `offset_cases`
- `expected_failures`
- `notes`

Validate:

- `vector_id` values are unique
- `vector_id` uses a stable prefix such as `V001`
- `category` is non-empty
- `priority` is one of `P0`, `P1`, or `P2`
- `source_text` is a string
- `source_text_description` is public-safe
- `utf16_code_unit_length` matches decoded source text
- `utf8_byte_length` matches decoded source text
- `code_point_count` matches decoded source text
- hash matches SHA-256 over decoded UTF-8 bytes
- hash format is lowercase hex
- `offset_cases` is an array
- `expected_failures` is an array

Vector-level mismatches should produce metadata-only diagnostics with `vector_id`, field name, and reason code.

## 9. UTF-16 Length Calculation Policy

UTF-16 code unit length must match JavaScript-style UTF-16 length.

Recommended Python calculation:

```python
len(source_text.encode("utf-16-le")) // 2
```

Policy:

- no BOM is counted
- surrogate pair characters count as 2 UTF-16 code units
- BMP characters count as 1 UTF-16 code unit
- combining mark code points count according to UTF-16 code units, not grapheme clusters
- length validation uses the decoded JSON string

## 10. UTF-8 Byte Length Policy

UTF-8 byte length must be:

```python
len(source_text.encode("utf-8"))
```

Policy:

- no Unicode normalization
- no newline normalization
- trailing newline preserved
- hash and byte length use the same decoded source text
- validation must not hash or count JSON escape bytes

## 11. Hash Validation Policy

Expected hash must equal:

```python
sha256(source_text.encode("utf-8")).hexdigest()
```

Policy:

- no JSON escaping layer
- no salt
- lowercase hex only
- hash length must be 64 hex characters
- mismatch is a validation failure
- diagnostics must not print raw source text
- diagnostics may print `vector_id`, hash field name, and reason code

Reason codes may include:

- `hash_mismatch`
- `invalid_hash_format`
- `unsupported_hash_algorithm`
- `unsupported_hash_encoding`

## 12. Offset Case Validation Policy

For each valid offset case:

- `utf16_start` and `utf16_end` must be non-negative integers
- `utf16_start <= utf16_end`
- offsets must be within UTF-16 code unit length
- offsets must map to valid UTF-8 byte boundaries
- `expected_utf8_start_byte` and `expected_utf8_end_byte` must match computed mapping
- `expected_selected_text` should match the decoded source slice inside fixture validation
- normal output must not print `expected_selected_text`
- `expected_status` must be `pass` or `valid`
- `reason_code` should be `none`
- offsets must not be rounded or repaired

Recommended UTF-16 to UTF-8 mapping algorithm:

1. Iterate over the decoded `source_text` by Unicode scalar value.
2. Accumulate UTF-16 code unit length per scalar.
3. Accumulate UTF-8 byte length per scalar.
4. Add only scalar-boundary UTF-16 offsets to a valid boundary map.
5. Omit boundaries inside surrogate pairs.
6. Validate requested offsets are present in the boundary map.
7. Return byte offsets only for valid boundaries.

This validator mapping is a fixture-validation helper. It does not replace the future Rust replay-critical helper.

## 13. Expected Failure Validation Policy

For each expected failure:

- `failure_id` is required
- `utf16_start` / `utf16_end` are required when applicable
- `expected_status` must be `validation_error` or `fail_closed`
- `reason_code` is required
- `raw_text_emission_allowed` must be false
- `public_safe_note` is required
- the failure should actually be invalid under the stated policy when possible

Expected failure reason codes may include:

- `offset_beyond_utf16_length`
- `offset_out_of_range`
- `invalid_surrogate_boundary`
- `offset_inside_surrogate_pair`
- `start_greater_than_end`
- `offset_range_inverted`
- `missing_required_field`
- `unsupported_schema_version`
- `hash_mismatch`
- `unsupported_position_unit`
- `unsupported_hash_policy`

The validator should not treat expected failures as unexpected validator failures if they match the designed invalid condition.

## 14. Forbidden Content Scan Policy

Future validator should scan fixture text fields for obvious forbidden markers.

Scan categories:

- real participant data marker
- raw learner text marker
- private path marker
- absolute local path marker
- raw event payload body marker
- logits / probabilities marker
- performance metric body marker

Clarifications:

- The fixture may contain minimal synthetic `source_text`.
- Policy wording in README is not itself a violation.
- The validator should distinguish synthetic examples from forbidden real data markers.
- This scan is conservative and does not prove absence of all sensitive content.

## 15. Public-Safe Diagnostics

Allowed output:

- `vector_id`
- `case_id`
- field name
- `reason_code`
- count summaries
- boolean safety flags
- schema version
- status

Forbidden output:

- raw `source_text`
- raw selected text
- raw event payload
- full fixture JSON body
- private paths
- absolute local paths
- real participant text
- logits / probabilities
- performance metric body

Diagnostics should be suitable for local and CI output without exposing content-bearing fixture bodies.

## 16. Failure Semantics

Status categories:

- `pass`
- `usage_error`
- `fail_closed`
- `mismatch`

Examples:

- missing fixture file -> `usage_error`
- malformed JSON -> `usage_error`
- unsupported schema version -> `usage_error` when clearly unsupported, otherwise `fail_closed`
- metadata policy mismatch -> `fail_closed`
- hash mismatch -> `mismatch`
- offset mapping mismatch -> `mismatch`
- forbidden content marker -> `fail_closed`
- internal exception -> `fail_closed` with public-safe reason

The default posture should be fail-closed when the validator cannot safely classify the failure.

## 17. Proposed Tests for Future Implementation

Required future focused tests:

- valid current vectors fixture passes
- unsupported schema version fails
- missing top-level field fails
- unsupported position unit fails
- hash mismatch fails
- UTF-16 length mismatch fails
- UTF-8 byte length mismatch fails
- offset mapping mismatch fails
- surrogate pair internal offset in valid `offset_cases` fails
- expected failure inside surrogate pair is accepted as expected failure
- beyond-length expected failure is accepted as expected failure
- start greater than end expected failure is accepted as expected failure
- forbidden content marker fails
- output suppresses raw source text

Tests should use temporary fixture copies or in-memory modified data. They should not modify the canonical fixture JSON.

## 18. Proposed Makefile and Release-Quality Integration

Future Makefile target proposal:

- `check-web-logger-unicode-hash-vector-fixtures`

Possible future release-quality label:

- `release_quality_check: web logger unicode hash vector fixture validation`

Clarifications:

- Not added in this step.
- Makefile integration should happen only after validator implementation and focused tests pass.
- Release-quality integration should happen only after standalone target behavior is stable and reviewed.
- Output must remain public-safe and metadata-only.

## 19. Relationship to Step-web-logger-004 Fixture Root

The future validator will validate the fixture root created in Step-web-logger-004.

This step:

- does not modify vector fixture data
- does not regenerate hash values
- does not claim fixture correctness beyond prior manual checks
- designs repeatable validation for future implementation

The Step-web-logger-004 fixture currently records 15 vectors, 35 valid offset cases, and 11 expected failures.

## 20. Relationship to Future Rust / TypeScript Helpers

A Python validator, if implemented first, is not a substitute for the Rust UTF-16 offset conversion helper.

It is also not a substitute for the TypeScript SHA-256 helper or the Rust SHA-256 helper.

Rust and TypeScript implementations still require separate future steps. The shared fixture enables later cross-language consistency checks after helper implementations exist.

## 21. Relationship to Event Durability

This validator design does not implement queue, IndexedDB, acknowledgement, retry, or deduplication.

Event durability remains a separate P0 chain. Offset/hash fixture validation should be stabilized before event durability replay integration, because durable event transport still depends on unambiguous replay-critical event semantics.

Future durability tests may use separate failure injection fixtures.

## 22. Relationship to No-Oracle and Synthetic-Only Boundaries

The fixture remains synthetic-only.

This validator design does not introduce:

- real participant data
- raw learner text
- `final_text`
- `observed_after_text`
- gold labels
- post-hoc annotation
- model performance validation

It does not relax no-oracle constraints.

## 23. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- Unicode correctness implementation completion
- hash compatibility implementation completion
- TypeScript / Rust vector check implementation completion
- validator implementation completion
- event durability implementation completion
- current TypeScript and Rust hash outputs are already aligned
- data collection readiness
- deployment readiness

## 24. Public-Safe Documentation Policy

Documentation and future diagnostics must preserve:

- no raw learner text in docs
- no real participant data in docs
- no raw event payload bodies in docs
- no full fixture JSON body copied into docs
- no private paths
- no absolute local paths
- no logits / probabilities
- no performance metric bodies
- examples remain synthetic and minimal
- diagnostics remain metadata-only

## 25. Recommended Next Codex Step

Recommended next step:

Step-web-logger-006: implement shared Unicode/hash vector fixture validator

Clarification:

- Step-web-logger-006 should implement the validator and focused tests.
- It may add a Python module and tests.
- It should not yet add Makefile / release-quality integration unless explicitly scoped.
- It should not modify TypeScript / Rust helpers yet.
- It should not implement event durability yet.

## 26. Step-web-logger-006 Validator Implementation Status

Step-web-logger-006 adds `python/web_logger_unicode_hash_vector_validation.py` and focused tests at `python/test_support/tests/test_web_logger_unicode_hash_vector_validation.py`.

The validator checks the Step-web-logger-004 fixture at `tests/fixtures/web_logger_unicode_hash_vectors/vectors.json` for:

- top-level metadata policy
- vector-level required fields and unique IDs
- UTF-16 code unit lengths
- UTF-8 byte lengths
- code point counts
- SHA-256 UTF-8 lowercase-hex hashes over decoded source text
- valid UTF-16 offset to UTF-8 byte offset mappings
- expected invalid offset records
- conservative forbidden marker counts
- public-safe summary output

The CLI is:

```bash
PYTHONPATH=python python3 -m web_logger_unicode_hash_vector_validation \
  --fixture tests/fixtures/web_logger_unicode_hash_vectors/vectors.json \
  --summary-only
```

This implementation does not add a Makefile target, release-quality wrapper entry, CI workflow, TypeScript helper, Rust UTF-16 conversion helper, Rust hash helper, schema implementation change, replay/runtime implementation change, or event durability queue / IndexedDB / acknowledgement / retry / deduplication.

## 27. Step-web-logger-007 Makefile Target Design Handoff

Step-web-logger-007 is recorded in `docs/web_logger_unicode_hash_vector_validator_makefile_target_design.md`.

It designs the future standalone Makefile target `check-web-logger-unicode-hash-vector-fixtures` for the Step-web-logger-006 Python validator. It records the proposed help text, command, placement, expected public-safe output, failure semantics, preconditions, future focused checks, and release-quality staging. It remains makefile-target-design / docs-only and does not change Makefile, validator code, tests, fixture JSON, release-quality wrapper, CI workflow, TypeScript, Rust, or event durability implementation.

## 28. Step-web-logger-008 Makefile Target Implementation

Step-web-logger-008 adds `check-web-logger-unicode-hash-vector-fixtures` as a standalone Makefile target for the Step-web-logger-006 validator.

The target runs `PYTHONPATH=python python3 -m web_logger_unicode_hash_vector_validation --fixture tests/fixtures/web_logger_unicode_hash_vectors/vectors.json --summary-only`. It validates fixture metadata, SHA-256 hashes, UTF-16 lengths, UTF-8 lengths, offset mappings, and expected failures with public-safe summary-only output. It does not change validator code, fixture JSON, release-quality wrapper, CI workflow, TypeScript/Rust helpers, or event durability.

## 29. Step-web-logger-009 Release-Quality Integration Design

Step-web-logger-009 is recorded in `docs/web_logger_unicode_hash_vector_validator_release_quality_integration_design.md`.

It designs a future wrapper check for the Step-web-logger-008 Makefile target. The proposed label is `release_quality_check: web logger unicode hash vector fixture validation`, and the proposed command is `make check-web-logger-unicode-hash-vector-fixtures`. The step is docs-only and does not alter wrapper behavior, validator behavior, fixture data, TypeScript/Rust helpers, or event durability.

## 30. Step-web-logger-010 Release-Quality Wrapper Integration

Step-web-logger-010 adds the Step-web-logger-008 target to `scripts/check_release_quality.sh`.

The wrapper now calls `make check-web-logger-unicode-hash-vector-fixtures` under `release_quality_check: web logger unicode hash vector fixture validation`. It reuses the Python validator through Makefile and keeps validator behavior, fixture JSON, TypeScript/Rust helpers, CI workflow, and event durability unchanged.

## 31. Step-web-logger-011 Remote/Manual Run Record Workflow Design

Step-web-logger-011 adds [Web Logger Unicode and Hash Vector Validator Release Quality Remote/Manual Run Record Workflow](web_logger_unicode_hash_vector_validator_release_quality_remote_run_record_workflow.md). The workflow design is docs-only and describes how a future status marker should record public-safe release-quality metadata for the validator check without modifying validator implementation, fixture JSON, Makefile, wrapper code, TypeScript/Rust helpers, or event durability.

## 32. Step-web-logger-012 Remote Status Marker

Step-web-logger-012 adds [Web Logger Unicode and Hash Vector Validator Release Quality Remote Run Status](status/web_logger_unicode_hash_vector_validator_release_quality_remote_run_status.md). It records public-safe remote evidence that the release-quality wrapper executed the Python validator through Makefile and observed `status=pass` for the current 15-vector fixture. It does not modify validator behavior or prove TypeScript/Rust helper compatibility.

## 33. Step-web-logger-013 Final Safety Review

Step-web-logger-013 adds [Web Logger Unicode and Hash Vector Validator Release Quality Chain Final Safety Review](web_logger_unicode_hash_vector_validator_release_quality_chain_final_safety_review.md). The review accepts the Python validator chain with explicit boundary for the fixed 15-vector synthetic fixture contract and keeps TypeScript/Rust helper compatibility separate.

## 34. Step-web-logger-014 Rust UTF-16 Offset Conversion Helper Design

Step-web-logger-014 adds [Rust UTF-16 Offset Conversion Helper Design for Web Logger Events](web_logger_rust_utf16_offset_conversion_helper_design.md). The helper design builds on the validated fixture contract but remains design-only and does not modify the Python validator, Makefile target, release-quality integration, or fixture JSON.

## 35. Step-web-logger-015 Rust UTF-16 Offset Conversion Helper

Step-web-logger-015 adds a focused Rust UTF-16 offset conversion helper and tests in `kslog_replay`.

The Rust tests consume the shared vector fixture for offset expectations while leaving the Python validator, Makefile target, release-quality wrapper, and `vectors.json` unchanged. The helper does not replace the Python fixture validator, does not compute hashes, and does not prove TypeScript/Rust helper compatibility.

## 36. Step-web-logger-016 Rust Helper Makefile Target Design

Step-web-logger-016 adds [Rust UTF-16 Offset Conversion Helper Makefile Target Design](web_logger_rust_utf16_offset_conversion_helper_makefile_target_design.md).

The design is separate from the Python validator target. It proposes a future Rust helper test target while keeping the Python validator, Python Makefile target, release-quality wrapper, and `vectors.json` unchanged.

## 37. Step-web-logger-017 Rust Helper Makefile Target

Step-web-logger-017 adds `check-web-logger-rust-utf16-offset-conversion` as a separate Makefile target from the Python validator target.

The Rust helper target runs focused Rust offset conversion tests. The Python validator target continues to validate the shared fixture contract. The two targets remain complementary and neither target replaces the other.

## 38. Step-web-logger-018 Rust Helper Release-Quality Integration Design

Step-web-logger-018 adds [Rust UTF-16 Offset Conversion Helper Release Quality Integration Design](web_logger_rust_utf16_offset_conversion_helper_release_quality_integration_design.md).

The design proposes future release-quality execution of the Rust helper Makefile target while keeping the Python validator chain separate. It does not change validator behavior, Rust helper behavior, fixture JSON, Makefile, wrapper, TypeScript/Rust helper compatibility claims, or event durability.

## 39. Step-web-logger-019 Rust Helper Release-Quality Integration

Step-web-logger-019 adds the Rust helper target to the release-quality wrapper while keeping the Python validator chain separate.

The wrapper now contains both the Python Unicode/hash vector fixture validation check and the Rust UTF-16 helper focused test check. The two checks remain complementary; neither proves the other's correctness, and neither claims TypeScript/Rust helper compatibility or event durability.

## 40. Step-web-logger-020 Rust Helper Remote/Manual Run Record Workflow Design

Step-web-logger-020 adds [Rust UTF-16 Offset Conversion Helper Release Quality Remote/Manual Run Record Workflow](web_logger_rust_utf16_offset_conversion_helper_release_quality_remote_run_record_workflow.md).

The workflow design keeps the Python validator chain and Rust helper chain as separate evidence boundaries. It does not create a status marker, change validator behavior, change Rust helper behavior, change fixture JSON, change Makefile, change wrapper, claim TypeScript/Rust helper compatibility, or add event durability.
