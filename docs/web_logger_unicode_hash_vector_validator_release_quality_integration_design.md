# Web Logger Unicode and Hash Vector Validator Release Quality Integration Design

## 1. Title

Web Logger Unicode and Hash Vector Validator Release Quality Integration Design

## 2. Scope

This step is release-quality-integration-design / docs-only.

It does not change:

- `scripts/check_release_quality.sh`
- Makefile
- CI workflow
- TypeScript code
- Rust code
- Python code
- tests
- fixture JSON
- package.json / Cargo.toml
- schema / runtime / replay implementation

It uses no real data and provides no production readiness proof, real-data readiness proof, or model performance proof.

## 3. Design Status

This document designs future release-quality integration for the shared Web logger Unicode/hash vector validator.

It does not modify `scripts/check_release_quality.sh`.

Existing inputs:

- Makefile target exists from Step-web-logger-008.
- Python validator exists from Step-web-logger-006.
- Fixture root exists from Step-web-logger-004.

Release-quality integration remains future work until Step-web-logger-010. TypeScript / Rust helper compatibility is not claimed.

## 4. Proposed Release-Quality Label

Proposed label:

```text
release_quality_check: web logger unicode hash vector fixture validation
```

The label should:

- appear before learner-state frozen policy generation target groups if the wrapper keeps a natural early fixture-validation section;
- not replace existing checks;
- be unique;
- clearly identify Web logger Unicode/hash shared vector validation;
- not imply TypeScript/Rust helper compatibility;
- not imply production readiness.

## 5. Proposed Release-Quality Command

Proposed command:

```bash
make check-web-logger-unicode-hash-vector-fixtures
```

The wrapper should call the Makefile target rather than duplicate the Python command. The command should rely on repository-relative paths already defined in Makefile, require no network access, require no real data, avoid modifying fixture JSON, avoid printing raw `source_text`, avoid printing selected raw text, and emit the validator's public-safe key=value summary.

## 6. Proposed Insertion Point in `scripts/check_release_quality.sh`

The current wrapper structure starts with general repository checks, shell checks, synthetic summary checks, manual markdown-link status, and Python checks. It then enters a long learner-state target sequence, followed later by config/scoring, Rust, synthetic policy, and logger-web checks.

Recommended future insertion point:

- after the existing `section "python checks"` block;
- before `section "learner-state audit fixtures"`;
- before learner-state frozen policy generation artifact / manifest chains;
- before downstream learner-state policy-generation checks;
- without moving or replacing existing checks.

Reason:

- the vector validator is Python-based and validates shared fixture data;
- the Makefile target is independent of learner-state generation chains;
- validating replay-critical Web logger fixture semantics before the learner-state-heavy release-quality sequence gives the check an early, bounded location;
- placing it near the late `logger-web checks` section would run it after many downstream checks and would not match its fixture-validation role.

## 7. Expected Release-Quality Output

Expected label:

```text
release_quality_check: web logger unicode hash vector fixture validation
```

Expected command line:

```text
command: make check-web-logger-unicode-hash-vector-fixtures
```

Expected validator summary includes at least:

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

Output must not contain:

- raw `source_text`
- raw selected text
- full fixture JSON body
- raw event payload body
- private / absolute local paths
- real participant data
- logits / probabilities
- performance metric body

## 8. Expected Failure Semantics

The future wrapper check should fail if the Makefile target exits nonzero.

Expected behavior:

- missing fixture file fails through validator `usage_error`;
- malformed JSON fails through validator `usage_error`;
- metadata mismatch fails through validator `fail_closed`;
- hash mismatch fails through validator `mismatch`;
- offset mapping mismatch fails through validator `mismatch`;
- forbidden content marker fails through validator `fail_closed`;
- wrapper does not repair fixture data;
- wrapper does not regenerate hashes;
- wrapper does not fallback to a weaker check.

## 9. Preconditions for Step-web-logger-010

Already satisfied:

- Python validator exists.
- Focused tests pass.
- Makefile target exists.
- Makefile target passes.
- Validator CLI passes.
- Vector fixture JSON validates.
- Target output is public-safe.
- Raw source text is suppressed.

Step-web-logger-010 should still verify:

- `make help` includes the target;
- `make check-web-logger-unicode-hash-vector-fixtures` passes;
- direct validator CLI passes;
- focused tests pass;
- compileall passes;
- `scripts/check_release_quality.sh` diff is limited to one label and one command;
- `make check-release-quality` passes after integration;
- output remains public-safe;
- forbidden claims are not introduced.

## 10. Proposed Step-web-logger-010 Implementation Scope

Step-web-logger-010 should:

- update `scripts/check_release_quality.sh` only as needed;
- add the release-quality label;
- call `make check-web-logger-unicode-hash-vector-fixtures`;
- update minimal docs;
- run `make check-release-quality`;
- not modify Makefile;
- not modify validator code;
- not modify tests;
- not modify fixture JSON;
- not modify TypeScript / Rust helpers;
- not implement event durability.

## 11. Relationship to Step-web-logger-008 Makefile Target

Step-web-logger-008 added the target.

Step-web-logger-009 only designs wrapper integration. It does not change the target.

Step-web-logger-010 may call the target from the wrapper. The Makefile target remains the source of the command.

## 12. Relationship to Step-web-logger-006 Validator Implementation

The validator implementation is already available.

Future release-quality integration will reuse the validator through Makefile. This design does not alter validator behavior. The validator remains Python-based, emits public-safe output, and does not prove TypeScript/Rust helper compatibility.

## 13. Relationship to TypeScript / Rust Helper Work

Release-quality integration of the Python validator does not implement:

- TypeScript SHA-256 helper
- Rust SHA-256 helper
- Rust UTF-16 to UTF-8 conversion helper

It does not prove TypeScript and Rust outputs match. Future TypeScript/Rust helper work should use the same vectors. Future cross-language checks should be separate targets.

## 14. Relationship to Event Durability

Release-quality integration of vector validation does not implement event durability.

Queue / IndexedDB / acknowledgement / retry / deduplication remain unimplemented. Event durability remains a separate P0 chain.

Unicode/hash vector validation stabilizes replay-critical semantics before durability integration.

## 15. Relationship to No-Oracle and Synthetic-Only Boundaries

The fixture is synthetic-only.

The check uses no:

- real participant data
- raw learner text
- `final_text`
- `observed_after_text`
- gold labels
- post-hoc annotation

It performs no model performance validation and does not relax no-oracle constraints.

## 16. Public-Safe Diagnostics

Normal output should be key=value metadata/count summary.

Forbidden output:

- raw source text
- raw selected text
- raw event payload body
- full fixture JSON body
- private paths
- absolute local paths
- logits / probabilities
- performance metric body

Allowed diagnostics may include:

- vector_id
- case_id
- field name
- reason_code
- counts
- booleans

Release-quality logs should remain public-safe.

## 17. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- Unicode correctness 実装完了
- hash compatibility 実装完了
- TypeScript / Rust vector check 実装完了
- TypeScript / Rust helper compatibility
- event durability 実装完了
- TypeScript と Rust の hash 出力が現時点で一致済みであること
- data collection readiness
- deployment readiness

## 18. Recommended Next Codex Step

Recommended next step:

Step-web-logger-010: integrate shared Unicode/hash vector validator into release-quality wrapper

Clarification:

- Step-web-logger-010 should modify `scripts/check_release_quality.sh` only as needed.
- Step-web-logger-010 should add one label and one command.
- Step-web-logger-010 should update minimal docs.
- Step-web-logger-010 should run `make check-release-quality`.
- Step-web-logger-010 should not modify Makefile.
- Step-web-logger-010 should not modify validator code.
- Step-web-logger-010 should not modify fixture JSON.
- Step-web-logger-010 should not implement TypeScript/Rust helpers.
- Step-web-logger-010 should not implement event durability.

## 19. Step-web-logger-010 Release-Quality Wrapper Integration Status

Step-web-logger-010 adds one release-quality wrapper check:

```text
release_quality_check: web logger unicode hash vector fixture validation
```

The wrapper command is:

```text
command: make check-web-logger-unicode-hash-vector-fixtures
```

The check is inserted after the existing `python checks` block and before `learner-state audit fixtures`, matching the Step-web-logger-009 design. It calls the Step-web-logger-008 Makefile target, which remains the source of truth for the validator command.

The check validates the shared Unicode/hash vector fixture through the Step-web-logger-006 Python validator. It covers fixture metadata, SHA-256 hashes, UTF-16 lengths, UTF-8 lengths, offset mappings, and expected invalid offset records with public-safe summary-only output.

Step-web-logger-010 does not change Makefile, validator behavior, fixture JSON, CI workflow, TypeScript/Rust helpers, schema/runtime/replay implementation, or event durability queue / IndexedDB / acknowledgement / retry / deduplication.

## 20. Step-web-logger-011 Remote/Manual Run Record Workflow Design

Step-web-logger-011 adds [Web Logger Unicode and Hash Vector Validator Release Quality Remote/Manual Run Record Workflow](web_logger_unicode_hash_vector_validator_release_quality_remote_run_record_workflow.md) as docs-only design for a future public-safe status marker after Step-web-logger-010 wrapper integration.

The workflow design defines the evidence hierarchy, future status marker path, public-safe metadata fields, target summary fields, missing metadata handling, non-equivalence cautions, and future Step-web-logger-012 / Step-web-logger-013 staging. It does not create the status marker, revise the wrapper, change Makefile, change validator code, change fixture JSON, implement TypeScript/Rust helpers, or implement event durability.

## 21. Step-web-logger-012 Remote Status Marker

Step-web-logger-012 adds [Web Logger Unicode and Hash Vector Validator Release Quality Remote Run Status](status/web_logger_unicode_hash_vector_validator_release_quality_remote_run_status.md). It records public-safe remote metadata for the Step-web-logger-010 wrapper check and the `make check-web-logger-unicode-hash-vector-fixtures` summary without changing wrapper, Makefile, validator code, fixture JSON, TypeScript/Rust helpers, CI workflow, or event durability.
