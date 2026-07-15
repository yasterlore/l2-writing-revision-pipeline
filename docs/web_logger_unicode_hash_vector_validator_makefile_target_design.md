# Web Logger Unicode and Hash Vector Validator Makefile Target Design

## 1. Title

Web Logger Unicode and Hash Vector Validator Makefile Target Design

## 2. Scope

This step is makefile-target-design / docs-only.

It does not change:

- Makefile
- release-quality wrapper
- CI workflow
- TypeScript code
- Rust code
- Python code
- tests
- fixture JSON
- package.json / Cargo.toml
- schema / runtime / validator implementation

It uses no real data and provides no production readiness proof, real-data readiness proof, or model performance proof.

## 3. Design Status

This document designs a future Makefile target for the Step-web-logger-006 Python validator.

It does not add the target. The validator implementation and focused tests already exist from Step-web-logger-006:

- `python/web_logger_unicode_hash_vector_validation.py`
- `python/test_support/tests/test_web_logger_unicode_hash_vector_validation.py`

Release-quality integration remains future work. This document does not claim TypeScript / Rust helper compatibility.

## 4. Proposed Makefile Target

Target name:

```text
check-web-logger-unicode-hash-vector-fixtures
```

Help text:

```text
Run web logger Unicode/hash vector fixture validation
```

Command:

```bash
PYTHONPATH=python python3 -m web_logger_unicode_hash_vector_validation --fixture tests/fixtures/web_logger_unicode_hash_vectors/vectors.json --summary-only
```

The target should be deterministic, require no network access, require no real data, and avoid modifying fixture JSON. It should not print `source_text`, selected raw text, or the full fixture JSON body. It should be safe for local and CI execution as a standalone fixture validation check.

## 5. Proposed Makefile Placement

The current Makefile has explicit `.PHONY` entries, explicit `make help` output, and grouped validation targets.

Recommended future placement:

- add `.PHONY: check-web-logger-unicode-hash-vector-fixtures` near the general logger / fixture validation entries, after `check-logger` or `check-fixtures`;
- add the help line near `check-logger` / `check-fixtures`, because the check validates Web logger fixture data with a Python validator;
- add the target body near the general validation target definitions after `check-fixtures`, before the learner-state-specific fixture/runtime target block.

Rationale:

- it is related to Web logger semantics, but the command is a Python fixture validator rather than an npm logger build/test target;
- it validates shared synthetic fixture data and should be discoverable alongside fixture validation checks;
- it should remain separate from release-quality ordering until a later wrapper integration step.

This step does not modify Makefile.

## 6. Expected Target Output

Expected public-safe summary fields include:

```text
mode=web_logger_unicode_hash_vector_validation
schema_version=web_logger_unicode_hash_vectors_v0.1
status=pass
reason_code=none
vector_count=15
valid_offset_case_count=35
expected_failure_count=11
hash_checked_count=15
utf16_length_checked_count=15
utf8_length_checked_count=15
offset_mapping_checked_count=35
content_suppressed=True
public_safe_output=True
production_readiness_claimed=False
real_data_readiness_claimed=False
performance_claims_present=False
```

Output must remain metadata/count-only. It must not contain raw `source_text`, raw selected text, full fixture JSON body, raw event payload body, private paths, absolute local paths, logits / probabilities, or performance metric bodies.

## 7. Expected Failure Semantics

The Makefile target should return nonzero exit on validator failure and should preserve the validator's failure categories.

Expected categories:

- missing fixture file -> `usage_error`
- malformed JSON -> `usage_error`
- unsupported schema version -> the validator's existing unsupported-version category
- metadata policy mismatch -> `fail_closed`
- hash mismatch -> `mismatch`
- offset mapping mismatch -> `mismatch`
- forbidden content marker -> `fail_closed`
- internal exception -> `fail_closed` with a public-safe reason

The target should not attempt to repair fixture data and should not regenerate hashes.

## 8. Required Preconditions Before Adding Target

Already satisfied from Step-web-logger-006:

- Python validator module exists.
- Focused tests exist.
- Current fixture validates with `status=pass`.
- CLI summary is public-safe.
- Raw source text is suppressed in normal summary output.
- 18 focused tests pass.

Remaining before Step-web-logger-008:

- decide the exact `.PHONY` placement;
- decide the exact `make help` placement;
- use repository-relative fixture path in the command;
- keep fixture JSON unchanged;
- run the new target after adding it in Step-web-logger-008.

## 9. Proposed Future Focused Checks for Step-web-logger-008

The future implementation step should run:

- `git status --short`
- `make help`, if available, and confirm the new target and help text are listed
- `make check-web-logger-unicode-hash-vector-fixtures`
- direct validator CLI:

```bash
PYTHONPATH=python python3 -m web_logger_unicode_hash_vector_validation --fixture tests/fixtures/web_logger_unicode_hash_vectors/vectors.json --summary-only
```

- focused validator tests:

```bash
PYTHONPATH=python python3 -m unittest python.test_support.tests.test_web_logger_unicode_hash_vector_validation
```

- compileall for the validator and focused test file
- targeted diff
- `git diff --check`
- conflict marker scan
- docs / code / output safety scan
- forbidden claims scan
- changed-file boundary check

## 10. Relationship to Step-web-logger-006 Validator Implementation

Step-web-logger-006 implemented the validator and focused tests.

Step-web-logger-007 only designs Makefile integration. It does not change validator code, tests, or fixture JSON.

Step-web-logger-008 should add the actual Makefile target if this design is accepted.

## 11. Relationship to Release-Quality Integration

Release-quality integration is not included in this step.

Release-quality integration should wait until the Makefile target exists and passes. A possible future label is:

```text
release_quality_check: web logger unicode hash vector fixture validation
```

That integration should be a separate later step. A release-quality pass for this target would validate the shared vector fixture through the Python validator, but would not prove TypeScript/Rust compatibility or production readiness.

## 12. Relationship to TypeScript / Rust Helper Work

The proposed Makefile target validates shared fixture data using the Python validator.

It does not implement:

- TypeScript SHA-256 helper
- Rust SHA-256 helper
- Rust UTF-16 to UTF-8 conversion helper

It does not prove TypeScript and Rust outputs match. Future TypeScript/Rust helper work should use the same vectors.

## 13. Relationship to Event Durability

This target does not implement event durability.

It adds no queue, IndexedDB persistence, acknowledgement, retry, deduplication, or seq reconciliation. Event durability remains a separate P0 chain.

Vector validation stabilizes replay-critical Unicode/hash semantics before durability integration.

## 14. Relationship to No-Oracle and Synthetic-Only Boundaries

The fixture remains synthetic-only.

The target does not use:

- real participant data
- raw learner text
- `final_text`
- `observed_after_text`
- gold labels
- post-hoc annotation

It does not validate model performance and does not relax no-oracle constraints.

## 15. Public-Safe Diagnostics

Normal output should be key=value metadata/count summary.

Allowed diagnostic fields include:

- vector_id
- case_id
- field name
- reason_code
- count summaries
- boolean safety flags
- schema version
- status

Forbidden diagnostic content includes:

- raw source text
- raw selected text
- raw event payload body
- full fixture JSON body
- private paths
- absolute local paths
- logits / probabilities
- performance metric body

## 16. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- Unicode correctness implementation completion
- hash compatibility implementation completion
- TypeScript / Rust vector check implementation completion
- Makefile target addition completion in this step
- release-quality integration completion
- event durability implementation completion
- current TypeScript and Rust hash outputs are already aligned
- data collection readiness
- deployment readiness

## 17. Recommended Next Codex Step

Recommended next step:

Step-web-logger-008: add shared Unicode/hash vector validator Makefile target

Clarification:

- Step-web-logger-008 should modify Makefile only, plus minimal docs.
- It should not modify validator code unless needed for target compatibility.
- It should not modify fixture JSON.
- It should not add release-quality integration yet.
- It should not implement TypeScript/Rust helpers.
- It should not implement event durability.

## 18. Step-web-logger-008 Makefile Target Implementation Status

Step-web-logger-008 adds the standalone Makefile target:

```text
check-web-logger-unicode-hash-vector-fixtures
```

The target command is:

```bash
PYTHONPATH=python python3 -m web_logger_unicode_hash_vector_validation --fixture tests/fixtures/web_logger_unicode_hash_vectors/vectors.json --summary-only
```

The help text is:

```text
Run web logger Unicode/hash vector fixture validation
```

The target is placed near the general logger / fixture validation checks: `.PHONY` and help listing are near `check-logger` / `check-fixtures`, and the target body is after `check-fixtures` and before learner-state-specific validation targets.

The target invokes the Step-web-logger-006 Python validator and validates the shared synthetic Unicode/hash fixture metadata, SHA-256 hashes, UTF-16 lengths, UTF-8 lengths, offset mappings, and expected invalid offset records. Its normal output is public-safe summary-only key=value metadata. It should not print raw source text, selected raw text, or the full fixture JSON body.

Step-web-logger-008 does not redesign validator code, change fixture JSON, add release-quality integration, add CI workflow integration, implement TypeScript/Rust helpers, or implement event durability queue / IndexedDB / acknowledgement / retry / deduplication.

## 19. Step-web-logger-009 Release-Quality Integration Design Handoff

Step-web-logger-009 is recorded in `docs/web_logger_unicode_hash_vector_validator_release_quality_integration_design.md`.

It designs future release-quality wrapper integration for `check-web-logger-unicode-hash-vector-fixtures`, including the proposed label, wrapper command, insertion point, expected public-safe output, failure semantics, Step-web-logger-010 preconditions, and safety boundaries. It remains release-quality-integration-design / docs-only and does not change `scripts/check_release_quality.sh`, Makefile, code, tests, fixture JSON, CI workflow, package metadata, Cargo metadata, or event durability.

## 20. Step-web-logger-010 Release-Quality Wrapper Integration

Step-web-logger-010 integrates the Makefile target into `scripts/check_release_quality.sh`.

The wrapper adds `release_quality_check: web logger unicode hash vector fixture validation` and runs `make check-web-logger-unicode-hash-vector-fixtures` after Python checks and before learner-state target groups. The Makefile target remains the command source of truth. Step-web-logger-010 does not change Makefile, validator code, tests, fixture JSON, TypeScript/Rust helpers, CI workflow, or event durability.

## 21. Step-web-logger-011 Remote/Manual Run Record Workflow Design

Step-web-logger-011 adds [Web Logger Unicode and Hash Vector Validator Release Quality Remote/Manual Run Record Workflow](web_logger_unicode_hash_vector_validator_release_quality_remote_run_record_workflow.md) as docs-only planning for a future status marker after release-quality wrapper integration. It records how future evidence should distinguish remote GitHub Actions metadata from local/manual fallback without changing the Makefile target, validator code, tests, fixture JSON, or release-quality wrapper.

## 22. Step-web-logger-012 Remote Status Marker

Step-web-logger-012 adds [Web Logger Unicode and Hash Vector Validator Release Quality Remote Run Status](status/web_logger_unicode_hash_vector_validator_release_quality_remote_run_status.md). The status marker records remote release-quality execution of the Makefile target with public-safe count-only metadata and keeps the Makefile target unchanged.

## 23. Step-web-logger-013 Final Safety Review

Step-web-logger-013 adds [Web Logger Unicode and Hash Vector Validator Release Quality Chain Final Safety Review](web_logger_unicode_hash_vector_validator_release_quality_chain_final_safety_review.md). The review accepts the Makefile target as part of the bounded remote-status-recorded fixture validator chain and does not change the target.
