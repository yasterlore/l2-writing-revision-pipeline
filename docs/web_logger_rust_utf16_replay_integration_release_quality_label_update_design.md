# Rust UTF-16 Replay Integration Release Quality Label Update Design

## 1. Title

Rust UTF-16 Replay Integration Release Quality Label Update Design

## 2. Scope

This is a release-quality-label-update-design / docs-only step.

This step does not change `scripts/check_release_quality.sh`, Makefile, Rust code, TypeScript code, Python code, tests, fixture JSON, CI workflow files, `package.json`, `Cargo.toml`, or `Cargo.lock`.

This step does not implement `kslog_validate`, `kslog_extract`, or `kslog_micro_episode` integration. It does not implement schema-level position_unit policy, event durability, production readiness proof, real-data readiness proof, or model performance proof.

## 3. Design Status

After Step-web-logger-024, the existing Makefile target runs helper-focused and replay-focused UTF-16 tests through the same `utf16` Cargo test filter.

Step-web-logger-026 updated the Makefile help text to `Run Rust UTF-16 offset conversion and replay integration tests`.

The release-quality wrapper still uses helper-focused label wording. This document designs a future label wording update only; it does not update the wrapper.

Replay-focused release-quality evidence remains future work. The Step-web-logger-021 remote status marker remains helper-focused pre-Step-web-logger-024 evidence and must not be reinterpreted as replay-focused remote status.

## 4. Current Release-Quality Wrapper Audit

Current label:

```text
release_quality_check: web logger Rust UTF-16 offset conversion helper
```

Current command:

```text
make check-web-logger-rust-utf16-offset-conversion
```

The check is currently placed after `release_quality_check: web logger unicode hash vector fixture validation` and before `release_quality_check: learner-state audit fixtures`.

The command should remain unchanged. The Makefile target remains the command source of truth, and the wrapper already calls that target rather than duplicating `cargo test -p kslog_replay utf16`.

The current insertion point should be preserved so the Web logger Unicode/hash fixture validation and Rust UTF-16 checks remain grouped without moving unrelated learner-state chains or existing Rust checks.

## 5. Current Target Semantics After Step-web-logger-026

Target name:

```text
check-web-logger-rust-utf16-offset-conversion
```

Updated help text:

```text
Run Rust UTF-16 offset conversion and replay integration tests
```

Command:

```text
cargo test -p kslog_replay utf16
```

After Step-web-logger-024 and Step-web-logger-026, this target covers both helper-focused UTF-16 offset conversion tests and replay-focused UTF-16 integration tests.

No new target was added. Fixture JSON remains unchanged. Output remains public-safe test summary output. Validate / extract / micro_episode integration remains out of scope.

## 6. Proposed Release-Quality Label Wording

Recommended future label:

```text
release_quality_check: web logger Rust UTF-16 offset conversion and replay integration
```

This label is better than the current helper-focused label because it preserves continuity with the existing target name while describing both helper-focused offset conversion coverage and replay-focused `kslog_replay` integration coverage.

The label does not imply validate / extract / micro_episode integration. It does not imply schema-level position_unit policy completion. It does not imply TypeScript/Rust compatibility, production readiness, real-data readiness, or model performance evidence.

Overly broad labels should be rejected:

- `release_quality_check: web logger Unicode correctness`
- `release_quality_check: web logger replay integration complete`
- `release_quality_check: web logger TypeScript Rust compatibility`

These labels are too broad because they imply wider Unicode correctness, complete replay integration, or TypeScript/Rust compatibility evidence that this target does not provide.

## 7. Proposed Release-Quality Command

Recommended command:

```text
make check-web-logger-rust-utf16-offset-conversion
```

The command should remain unchanged. The Makefile target remains the command source of truth.

The wrapper should not duplicate `cargo test -p kslog_replay utf16`, add a second target, run duplicate tests, or fallback to weaker tests.

## 8. Proposed Insertion Point

Preserve the current insertion point:

- after `release_quality_check: web logger unicode hash vector fixture validation`
- before `release_quality_check: learner-state audit fixtures`

This keeps Web logger Unicode/hash and Rust UTF-16 checks grouped. The future label update should not move unrelated learner-state checks, move existing Rust checks, remove existing checks, or reorder unrelated chains.

## 9. Proposed Future Wrapper Change

Step-web-logger-028 should modify `scripts/check_release_quality.sh` only as needed to change the existing Rust UTF-16 release-quality label wording.

Step-web-logger-028 should keep command `make check-web-logger-rust-utf16-offset-conversion`, preserve the insertion point, and avoid Makefile, Rust code, tests, fixture JSON, and CI workflow changes.

Because release-quality visible behavior changes, Step-web-logger-028 should update minimal docs plus README and full technical specification docs. It should run `make check-release-quality`, confirm the new label appears, and confirm final `release_quality_check: ok`.

## 10. Expected Release-Quality Output After Future Update

Expected label:

```text
release_quality_check: web logger Rust UTF-16 offset conversion and replay integration
```

Expected command:

```text
command: make check-web-logger-rust-utf16-offset-conversion
```

Expected behavior:

- focused helper UTF-16 tests pass
- replay-focused UTF-16 tests pass
- final `release_quality_check: ok` is observed

Expected public-safe summary:

- target_status=pass
- target_command=make check-web-logger-rust-utf16-offset-conversion
- underlying_command=cargo test -p kslog_replay utf16
- helper_focused_tests_observed=yes
- replay_focused_tests_observed=yes
- fixture_json_modified=no
- content_suppressed_boundary=maintained
- production_readiness_claimed=False
- real_data_readiness_claimed=False
- performance_claims_present=False

## 11. Expected Failure Semantics

The future wrapper should fail if the Makefile target exits nonzero.

Expected failure categories:

- helper-focused test failure -> release-quality failure
- replay-focused test failure -> release-quality failure
- compile error -> release-quality failure
- missing fixture, if read -> release-quality failure

The wrapper should not repair fixtures, regenerate vectors, fallback to weaker tests, suppress test failures, or treat partial pass as full pass.

## 12. Relationship to Step-web-logger-021 Status Marker

Step-web-logger-021 recorded the pre-Step-web-logger-024 helper-focused release-quality chain.

It must not be reinterpreted as replay-focused remote evidence.

After the future label update, a new run-record workflow and status marker are needed for replay-focused release-quality evidence. That future status marker should record the new label and helper + replay test coverage. The existing helper-focused status marker remains valid for its own boundary.

## 13. Relationship to Step-web-logger-024 Replay Integration

Step-web-logger-024 implemented replay-focused integration in `kslog_replay`.

Step-web-logger-027 only designs label wording. It does not change Rust replay implementation.

Replay integration remains limited to `kslog_replay`; validate / extract / micro_episode integration remains unimplemented.

## 14. Relationship to Step-web-logger-026 Target Help Update

Step-web-logger-026 updated the Makefile help text.

The current target command already covers helper-focused and replay-focused UTF-16 tests. The release-quality label should now align with those target semantics.

The target name and command remain unchanged.

## 15. Relationship to Focused Helper Chain

Step-web-logger-014 through Step-web-logger-022 accepted the focused helper/test/release-quality chain.

Replay-focused integration is a newer evidence boundary. The label update should not blur evidence boundaries.

Focused helper tests remain part of the target. Replay-focused evidence needs its own future status marker and final safety review.

## 16. Relationship to TypeScript / Rust Hash/Helper Work

The label update does not implement Rust SHA-256 helper work, TypeScript SHA-256 helper work, or TypeScript/Rust vector checks.

It does not prove current TypeScript/Rust hash equality. Hash compatibility remains separate.

## 17. Relationship to Event Durability

The label update does not implement event durability.

Queue / IndexedDB / acknowledgement / retry / dedup remain unimplemented. Server-side idempotency / event_id dedup remains unimplemented. Ordering / delivery durability is not solved.

## 18. Relationship to No-Oracle and Synthetic-Only Boundaries

No real participant data is introduced. No raw learner text is introduced.

No `final_text`, `observed_after_text`, gold labels, post-hoc annotation, or test-set tuning is introduced.

No model performance validation is performed. No-oracle constraints are not relaxed. Tests remain synthetic-only.

## 19. Public-Safe Output Boundary

Allowed:

- release-quality label
- command
- cargo test names
- pass/fail counts
- crate name
- test filter
- reason_code names
- count summaries

Forbidden:

- raw source text
- raw selected text
- full event payload body
- full fixture JSON body
- raw learner text
- real participant data
- private paths
- absolute local paths
- logits / probabilities
- performance metric body

## 20. Future Release-Quality Evidence Staging

Recommended staging after Step-web-logger-028:

- Step-web-logger-029: replay-focused release-quality remote/manual run record workflow design
- Step-web-logger-030: replay-focused release-quality status marker
- Step-web-logger-031: replay-focused release-quality final safety review

Step-web-logger-030 should use remote GitHub Actions metadata if available. If remote metadata is unavailable, local/manual fallback must be explicitly marked.

The final safety review may only accept bounded replay-focused release-quality status if evidence is sufficient.

Do not move directly to validate / extract / micro_episode integration without separate design.

## 21. Non-Equivalence Cautions

- Release-quality label update design is not wrapper implementation.
- Label update does not create replay-focused remote status marker.
- Label update does not create final safety review.
- Helper-focused remote status marker is not replay-focused remote status marker.
- Replay-focused tests are not validate integration.
- Replay-focused tests are not extract integration.
- Replay-focused tests are not micro_episode integration.
- Replay-focused tests are not schema-level position_unit policy completion.
- Replay-focused tests are not TypeScript/Rust compatibility.
- Replay-focused tests are not event durability.
- Synthetic-only tests are not real-data readiness.
- Release-quality pass is not production readiness.

## 22. Non-Claims

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
- replay integration remote status recording

## 23. Recommended Next Codex Step

Recommended next step:

Step-web-logger-028: update Rust UTF-16 replay integration release-quality label

Clarification:

- Step-web-logger-028 should be an implementation step.
- It should update only the existing label wording in `scripts/check_release_quality.sh`.
- It should keep command unchanged.
- It should keep insertion point unchanged.
- It should not modify Makefile.
- It should not modify Rust code.
- It should not modify tests.
- It should not modify fixture JSON.
- It should not modify CI workflow.
- It should update minimal docs.
- It should update README and full technical specification docs because release-quality visible behavior changes.
- It should run `make check-release-quality`.
- It should not implement validate / extract / micro_episode integration.
- It should not implement TypeScript/Rust hash checks.
- It should not implement event durability.
