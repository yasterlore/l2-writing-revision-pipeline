# Rust UTF-16 Offset Conversion Helper Makefile Target Design

## 1. Title

Rust UTF-16 Offset Conversion Helper Makefile Target Design

## 2. Scope

This is a makefile-target-design / docs-only step.

This step makes no Makefile changes, no Rust code changes, no TypeScript code changes, no Python code changes, no tests changes, no fixture JSON changes, no release-quality wrapper changes, no CI workflow changes, and no `package.json` / `Cargo.toml` / `Cargo.lock` changes.

This step does not add broader replay / validate / extract / micro_episode runtime integration, event durability implementation, production readiness proof, real-data readiness proof, or model performance proof.

## 3. Design Status

This doc designs a future Makefile target. It does not add the target.

The Rust UTF-16 offset helper already exists from Step-web-logger-015. Focused Rust tests already exist from Step-web-logger-015. Those focused tests already reuse the shared synthetic Unicode/hash vectors.

Release-quality integration remains future work. TypeScript/Rust hash compatibility is not claimed. Broader replay runtime integration is not claimed.

## 4. Proposed Makefile Target

Target name:

```text
check-web-logger-rust-utf16-offset-conversion
```

Help text:

```text
Run Rust UTF-16 offset conversion helper tests
```

Command:

```bash
cargo test -p kslog_replay utf16
```

The target should be deterministic, require no network access, require no real data, not modify fixture JSON, not print raw `source_text`, not print selected raw text, not print the full fixture JSON body, and be safe for local and CI execution.

The target should fail with a nonzero exit status when the focused Rust tests fail.

## 5. Proposed Optional Companion Command

The first Makefile target should run only:

```bash
cargo test -p kslog_replay utf16
```

`cargo fmt` and `cargo clippy` should remain covered by existing broader Rust checks. The focused target should not run `cargo clippy` in its first target step, should not run `cargo test --workspace`, and should avoid becoming unnecessarily slow.

Step-web-logger-017 may still run `cargo fmt --all -- --check`, `cargo clippy -p kslog_replay -- -D warnings`, and `cargo test -p kslog_replay` as verification commands after adding the target.

## 6. Proposed Makefile Placement

Current Makefile structure has a general `.PHONY` block, a `help` listing, broad checks such as `check-rust`, and the existing Web logger target:

```text
check-web-logger-unicode-hash-vector-fixtures
```

The conservative placement is:

- `.PHONY` entry immediately after `check-web-logger-unicode-hash-vector-fixtures`
- help listing immediately after the existing Web logger Unicode/hash vector fixture line
- target body immediately after `check-web-logger-unicode-hash-vector-fixtures`

This keeps Web logger-specific checks together, avoids moving existing targets, avoids replacing existing targets, and avoids reordering unrelated learner-state chains. It is more consistent than placing this focused helper target inside the broad `check-rust` body, because the target is Web logger-specific and reuses Web logger Unicode/hash vectors.

## 7. Expected Target Output

Expected normal output:

- `cargo test -p kslog_replay utf16` passes
- focused UTF-16 helper tests pass
- no raw `source_text` printed
- no selected raw text printed
- no full fixture JSON body printed
- no raw event payload body printed
- no private paths
- no absolute local paths
- no real participant data
- no raw learner text
- no logits / probabilities
- no performance metric body

Expected result summary for future reports:

```text
target_status=pass
crate=kslog_replay
test_filter=utf16
shared_vector_fixture_reused=yes
fixture_json_modified=no
content_suppressed_boundary=maintained
production_readiness_claimed=False
real_data_readiness_claimed=False
performance_claims_present=False
```

## 8. Expected Failure Semantics

Expected failure categories:

- helper test failure -> Makefile target nonzero
- invalid shared vector expectations -> Makefile target nonzero
- Rust compile error -> Makefile target nonzero
- Cargo invocation failure -> Makefile target nonzero
- fixture file missing during test -> Makefile target nonzero
- unsupported environment -> target fails rather than silently skipping

The Makefile target should not repair fixture data, regenerate shared vectors, rewrite expected offsets, fall back to weaker tests, or silently ignore missing shared vectors.

## 9. Required Preconditions Before Adding Target

Already satisfied from Step-web-logger-015:

- Rust helper exists
- focused Rust tests exist
- shared vectors are directly reused
- `cargo test -p kslog_replay utf16` passes
- `cargo test -p kslog_replay` passes
- `cargo fmt --all -- --check` passes
- `cargo clippy -p kslog_replay -- -D warnings` passes
- `cargo test --workspace` passes
- fixture JSON unchanged
- `Cargo.toml` / `Cargo.lock` unchanged

Remaining before Step-web-logger-017:

- decide exact Makefile placement
- decide whether `make help` needs updating
- ensure target command remains focused and deterministic
- ensure no fixture JSON changes
- run target after adding it in Step-web-logger-017

## 10. Proposed Future Focused Checks for Step-web-logger-017

Recommended checks for the future target implementation step:

- `make help`
- `make check-web-logger-rust-utf16-offset-conversion`
- `cargo test -p kslog_replay utf16`
- `cargo test -p kslog_replay`
- `cargo fmt --all -- --check`
- `cargo clippy -p kslog_replay -- -D warnings`
- optional `cargo test --workspace` if fast enough
- targeted diff
- `git diff --check`
- conflict marker scan
- code / docs / test output safety scan
- forbidden claims scan
- changed-file boundary check

## 11. Relationship to Step-web-logger-015 Rust Helper Implementation

Step-web-logger-015 implemented the Rust helper and focused tests.

Step-web-logger-016 only designs Makefile integration. It does not change Rust code, does not change tests, and does not modify fixture JSON.

Step-web-logger-017 should add the actual Makefile target if this design is accepted.

## 12. Relationship to Python Validator Chain

The Python validator chain validates the shared Unicode/hash fixture contract.

The Rust UTF-16 helper tests reuse the same vectors for Rust offset conversion. The Rust helper Makefile target is separate from the Python validator Makefile target.

Passing the Python validator target does not prove Rust helper correctness. Passing the Rust helper target does not prove Python validator correctness. The two targets are complementary.

## 13. Relationship to Release-Quality Integration

Release-quality integration is not included in this step.

Release-quality integration should not happen until the Makefile target exists and passes.

Future release-quality label may be:

```text
release_quality_check: web logger Rust UTF-16 offset conversion helper
```

A future release-quality pass would not prove TypeScript compatibility or production readiness. Release-quality integration should be a separate later step after Step-web-logger-017.

## 14. Relationship to Broader Replay / Validate / Extract Integration

This Makefile target would test the helper only.

It does not integrate the helper into replay runtime behavior, schema validation, revision extraction, or micro_episode context slicing.

Broader runtime integration should be a separate future chain.

## 15. Relationship to TypeScript / Rust Hash/Helper Work

The Rust UTF-16 offset helper target does not implement a Rust SHA-256 helper, a TypeScript SHA-256 helper, or TypeScript/Rust hash compatibility checks.

It does not prove that current TypeScript and Rust hash outputs match. Future TypeScript/Rust vector checks should be separate targets.

## 16. Relationship to Event Durability

This target does not implement event durability.

It does not implement queue / IndexedDB / ack / retry / dedup. It does not implement server-side idempotency / event_id dedup. It does not solve ordering or delivery durability.

Event durability remains a separate P0 chain.

## 17. Relationship to No-Oracle and Synthetic-Only Boundaries

Shared vectors are synthetic-only.

There is no real participant data, no raw learner text, no `final_text`, no `observed_after_text`, no gold labels, and no post-hoc annotation.

No model performance validation is performed. No-oracle constraints are not relaxed.

## 18. Public-Safe Diagnostics

Allowed diagnostics:

- reason_code
- test name
- numeric UTF-16 offset metadata
- numeric UTF-8 byte offset metadata
- vector_id / case_id when needed
- pass/fail count summary

Forbidden diagnostics:

- raw `source_text`
- raw selected text
- raw event payload body
- full fixture JSON body
- private paths
- absolute local paths
- raw learner text
- real participant data
- logits / probabilities
- performance metric body

## 19. Non-Equivalence Cautions

- Makefile target design is not a Makefile target addition.
- Focused Rust helper tests are not broader replay integration.
- Rust helper pass is not TypeScript compatibility.
- Rust helper pass is not Rust SHA-256 compatibility.
- Rust helper pass is not TypeScript logger hash correctness.
- Rust helper pass is not event durability.
- Shared vector reuse is not exhaustive Unicode coverage.
- Synthetic-only tests are not real-data readiness.
- Release-quality integration is not included in this step.

## 20. Non-Claims

This design does not claim:

- production readiness
- real-data readiness
- model performance
- F1 / accuracy / ECE / AURCC achievement
- broader Unicode correctness の実装完了
- hash compatibility の実装完了
- TypeScript / Rust vector check の実装完了
- TypeScript / Rust helper compatibility
- event durability の実装完了
- TypeScript と Rust の hash 出力が現時点で一致済みであること
- data collection readiness
- deployment readiness

## 21. Recommended Next Codex Step

Recommended next step:

Step-web-logger-017: add Rust UTF-16 offset conversion helper Makefile target

Clarification:

- Step-web-logger-017 should modify Makefile only, plus minimal docs.
- Step-web-logger-017 should add target `check-web-logger-rust-utf16-offset-conversion`.
- Step-web-logger-017 should not modify Rust helper code unless required for target compatibility.
- Step-web-logger-017 should not modify tests.
- Step-web-logger-017 should not modify fixture JSON.
- Step-web-logger-017 should not add release-quality integration yet.
- Step-web-logger-017 should not implement TypeScript/Rust hash checks.
- Step-web-logger-017 should not implement event durability.

## 22. Step-web-logger-017 Target Status

Step-web-logger-017 adds the standalone Makefile target:

```text
check-web-logger-rust-utf16-offset-conversion
```

The target runs:

```bash
cargo test -p kslog_replay utf16
```

The target is placed near the existing Web logger Unicode/hash vector fixture target, with help text:

```text
Run Rust UTF-16 offset conversion helper tests
```

This status update records Makefile target availability only. It does not change Rust helper code, focused Rust tests, fixture JSON, release-quality wrapper, CI workflow, broader replay / validate / extract / micro_episode runtime integration, Rust SHA-256 helper work, TypeScript SHA-256 helper work, TypeScript/Rust cross-language vector checks, or event durability.

## 23. Step-web-logger-018 Release-Quality Integration Design

Step-web-logger-018 adds [Rust UTF-16 Offset Conversion Helper Release Quality Integration Design](web_logger_rust_utf16_offset_conversion_helper_release_quality_integration_design.md).

The design proposes a future wrapper label, `release_quality_check: web logger Rust UTF-16 offset conversion helper`, and command, `make check-web-logger-rust-utf16-offset-conversion`. It does not change Makefile, wrapper, Rust code, tests, fixture JSON, CI workflow, broader runtime integration, TypeScript/Rust hash work, or event durability.
