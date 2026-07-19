# Rust UTF-16 Replay Integration Makefile Target Design

## 1. Title

Rust UTF-16 Replay Integration Makefile Target Design

## 2. Scope

This is a Makefile-target-design / docs-only step.

This step makes no Makefile changes, no release-quality wrapper changes, no Rust code changes, no TypeScript code changes, no Python code changes, no tests changes, no fixture JSON changes, no CI workflow changes, and no package.json / Cargo.toml / Cargo.lock changes.

This step does not integrate `kslog_validate`, `kslog_extract`, or `kslog_micro_episode`. It does not implement schema-level position_unit policy. It does not implement event durability.

This step does not provide production readiness proof, real-data readiness proof, or model performance proof.

## 3. Design Status

The Rust helper focused chain is already release-quality-integrated and remote-status-recorded.

Replay-focused integration exists from Step-web-logger-024.

The existing Makefile target currently runs:

```bash
cargo test -p kslog_replay utf16
```

After Step-web-logger-024, that command runs both helper-focused and replay-focused UTF-16 tests.

This doc designs future target semantics. It does not add or modify the target. Release-quality label update or a new label remains future work.

## 4. Current Target Audit

Current target name:

```text
check-web-logger-rust-utf16-offset-conversion
```

Current help text:

```text
Run Rust UTF-16 offset conversion helper tests
```

Current command:

```bash
cargo test -p kslog_replay utf16
```

After Step-web-logger-024, the target covers:

- replay-focused `utf16_replay_*` unit tests in `crates/kslog_replay/src/lib.rs`
- helper-focused tests whose names include `utf16` in `crates/kslog_replay/tests/utf16_offsets.rs`

The current release-quality wrapper calls this target under:

```text
release_quality_check: web logger Rust UTF-16 offset conversion helper
```

The target output remains normal Cargo test summary output. The inspected target does not print raw source text, selected text, full fixture JSON body, raw event payload body, real participant data, logits / probabilities, or performance metric body in normal output.

Fixture JSON remains unchanged.

## 5. Test Filter Audit

`cargo test -p kslog_replay utf16` captures helper-focused tests whose test names contain `utf16`.

`cargo test -p kslog_replay utf16` also captures the Step-web-logger-024 replay-focused tests because their names begin with `utf16_replay_`.

A replay-specific filter currently exists:

```bash
cargo test -p kslog_replay utf16_replay
```

That filter is stable for the new replay-focused unit tests as currently named.

A helper-only filter is not equivalently stable for all helper-focused tests because several helper tests do not include `utf16` in the test name, and the existing target has always used the broad `utf16` filter rather than a helper-only naming convention.

Adding a replay-specific target would not require renaming replay tests. However, it would create overlap with the existing target unless the existing target command, help text, or test naming strategy is also redesigned. Renaming tests should be avoided in this step because Step-web-logger-024 already passed with the current focused filter behavior.

## 6. Option A: Update Existing Target Semantics

Option A keeps the current target name:

```text
check-web-logger-rust-utf16-offset-conversion
```

Option A keeps the current command:

```bash
cargo test -p kslog_replay utf16
```

A future step would update the help text to:

```text
Run Rust UTF-16 offset conversion and replay integration tests
```

Docs would clarify that the target now covers both helper-focused and replay-focused tests. Later release-quality documentation, label wording, or status marker flow can be updated to avoid silently reusing the Step-web-logger-021 helper-focused remote status boundary.

Pros:

- minimal Makefile change
- no duplicate test execution
- preserves the existing release-quality wrapper command
- reflects the current actual behavior after Step-web-logger-024
- avoids test renaming

Cons:

- the old target name says offset conversion helper, not replay integration
- the existing release-quality label under-describes replay-focused coverage
- Step-web-logger-021 remote status marker only covers the pre-Step-web-logger-024 helper-focused remote run, not the new replay integration boundary

## 7. Option B: Add Separate Replay Integration Target

Possible new target name:

```text
check-web-logger-rust-utf16-replay-integration
```

Possible help text:

```text
Run Rust UTF-16 replay integration tests
```

Possible command if using the replay-specific filter:

```bash
cargo test -p kslog_replay utf16_replay
```

Possible fallback command if a replay-specific filter became unstable:

```bash
cargo test -p kslog_replay utf16
```

Pros:

- clearer evidence boundary for replay integration
- future release-quality label can clearly name replay integration
- future status marker can avoid confusing helper-focused and replay-focused evidence

Cons:

- the existing target already runs replay-focused tests because it uses the `utf16` filter
- adding the new target may duplicate replay test execution unless the old target semantics are also updated
- the helper-only filter is not stable enough to cleanly split the old helper target without a separate naming cleanup
- two overlapping targets could create label and status marker confusion
- additional release-quality staging would be required

## 8. Recommended Target Strategy

Recommendation: choose Option A for the next implementation step.

Although a replay-specific `utf16_replay` filter exists, the existing target already runs the replay-focused tests because it uses the broader `utf16` filter. A separate replay target would duplicate test execution unless the existing helper target is also reworked, and a helper-only filter is not currently stable for all helper-focused tests.

The safest next move is:

- do not add a duplicate target immediately
- update the existing target help text and docs to reflect helper + replay-focused UTF-16 coverage
- preserve the existing command `cargo test -p kslog_replay utf16`
- update or supplement release-quality documentation/status flow later so replay-focused evidence gets an explicit boundary
- create a later test-naming design step only if a clean split between helper-only and replay-only targets becomes necessary

## 9. Proposed Future Makefile Change

Step-web-logger-026 should:

- update the Makefile help text only, plus minimal docs
- keep target name `check-web-logger-rust-utf16-offset-conversion`
- keep target command `cargo test -p kslog_replay utf16`
- use help text `Run Rust UTF-16 offset conversion and replay integration tests`
- not change Rust code
- not change tests
- not change fixture JSON
- not change release-quality wrapper yet
- update README and full technical specification docs because Makefile-visible behavior changes

## 10. Proposed Future Release-Quality Staging

Recommended staging after Step-web-logger-026:

- Step-web-logger-027: release-quality integration design
- Step-web-logger-028: release-quality wrapper integration
- Step-web-logger-029: remote/manual status marker workflow design
- Step-web-logger-030: status marker
- Step-web-logger-031: final safety review

The helper-focused remote status marker from Step-web-logger-021 must not be silently reinterpreted as replay integration status.

Replay-focused evidence needs its own status marker or an explicitly updated boundary. A release-quality pass after Step-web-logger-024 does not yet equal remote-status-recorded replay integration unless a remote run/status marker is created.

Step-web-logger-029 adds [Rust UTF-16 Replay Integration Release Quality Remote/Manual Run Record Workflow](web_logger_rust_utf16_replay_integration_release_quality_remote_run_record_workflow.md) to design that future evidence path. It does not create the status marker or change the existing target.

Step-web-logger-030 adds [Rust UTF-16 Replay Integration Release Quality Remote Run Status](status/web_logger_rust_utf16_replay_integration_release_quality_remote_run_status.md) as that separate public-safe evidence boundary. It does not change the existing target.

Step-web-logger-031 adds [Rust UTF-16 Replay Integration Release Quality Chain Final Safety Review](web_logger_rust_utf16_replay_integration_release_quality_chain_final_safety_review.md). It accepts the existing target coverage only within the explicit `kslog_replay` replay-focused boundary.

## 11. Expected Target Output Boundary

Allowed target output:

- Cargo test names
- pass/fail counts
- crate name
- test filter
- reason_code names
- count summaries

Forbidden target output:

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

## 12. Failure Semantics

Expected failure behavior:

- helper test failure -> target nonzero
- replay-focused test failure -> target nonzero
- invalid UTF-16 offset behavior mismatch -> target nonzero
- compile error -> target nonzero
- missing fixture, if read -> target nonzero

The target must not repair fixtures, regenerate vectors, fallback to weaker tests, or suppress failures.

## 13. Relationship to Step-web-logger-024 Replay Integration

Step-web-logger-024 implemented replay-focused integration in `kslog_replay`.

Step-web-logger-025 only designs target semantics. It does not change implementation.

Replay integration remains limited to `kslog_replay`. Validate / extract / micro_episode integration remains unimplemented.

## 14. Relationship to Focused Helper Chain

Step-web-logger-014 through Step-web-logger-022 accepted the focused helper/test chain.

Replay-focused integration is a new evidence boundary. The helper-focused status marker should not be treated as replay-focused remote status.

The existing helper target may now include replay tests, but documentation must make the boundary explicit. Focused helper tests remain useful.

## 15. Relationship to Release-Quality Wrapper

The release-quality wrapper currently calls the existing target.

The wrapper label may under-describe expanded test coverage after Step-web-logger-024.

The wrapper should not be changed in this step. Future wrapper changes should be staged separately.

Any future release-quality label must not claim validate / extract / micro_episode integration.

## 16. Relationship to TypeScript / Rust Hash/Helper Work

This target design does not implement the Rust SHA-256 helper.

It does not implement the TypeScript SHA-256 helper. It does not implement TypeScript/Rust vector checks. It does not prove current TypeScript and Rust hashes match.

Hash compatibility remains separate.

## 17. Relationship to Event Durability

This target design does not implement event durability.

Queue / IndexedDB / ack / retry / dedup remain unimplemented. Server-side idempotency / event_id dedup remains unimplemented. Ordering / delivery durability is not solved.

## 18. Relationship to No-Oracle and Synthetic-Only Boundaries

No real participant data is introduced. No raw learner text is introduced.

No `final_text`, `observed_after_text`, gold labels, post-hoc annotation, or test-set tuning is introduced.

No model performance validation is performed. No-oracle constraints are not relaxed. Future target tests must remain synthetic-only.

## 19. Non-Equivalence Cautions

- Makefile target design is not Makefile implementation.
- Existing helper target pass is not automatically remote-status-recorded replay integration.
- Replay-focused tests are not validate integration.
- Replay-focused tests are not extract integration.
- Replay-focused tests are not micro_episode integration.
- Replay-focused tests are not schema-level position_unit policy completion.
- Replay-focused tests are not TypeScript/Rust compatibility.
- Replay-focused tests are not event durability.
- Synthetic-only tests are not real-data readiness.
- Release-quality wrapper pass is not production readiness.

## 20. Non-Claims

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
- current TypeScript and Rust hashes match
- event durability implementation
- data collection readiness
- deployment readiness

## 21. Recommended Next Codex Step

Recommended next step:

Step-web-logger-026: update Rust UTF-16 Makefile target help text and docs for replay-focused coverage

Clarification:

- Step-web-logger-026 should be an implementation step.
- It should modify Makefile only as needed, plus minimal docs.
- It should update the existing target help text rather than add a duplicate target.
- It should not modify Rust code unless a later test-filter cleanup is explicitly scoped.
- It should not modify tests unless a separate test-naming design justifies it.
- It should not modify fixture JSON.
- It should not modify the release-quality wrapper yet.
- It should not implement validate / extract / micro_episode integration.
- It should not implement TypeScript/Rust hash checks.
- It should not implement event durability.

## 22. Step-web-logger-026 Help Text Update Status

Step-web-logger-026 follows Option A from this design.

The existing target name remains `check-web-logger-rust-utf16-offset-conversion`, and the command remains `cargo test -p kslog_replay utf16`.

The Makefile help text is updated to `Run Rust UTF-16 offset conversion and replay integration tests` so the visible target description matches the post-Step-web-logger-024 behavior: helper-focused UTF-16 tests and replay-focused UTF-16 tests are both selected by the `utf16` filter.

No new target is added. `scripts/check_release_quality.sh` is not changed in this step, so its current label still uses helper-focused wording. The Step-web-logger-021 remote status marker remains helper-focused pre-Step-web-logger-024 evidence and is not reinterpreted as replay-focused remote status.

## 23. Step-web-logger-027 Release-Quality Label Update Design

Step-web-logger-027 adds [Rust UTF-16 Replay Integration Release Quality Label Update Design](web_logger_rust_utf16_replay_integration_release_quality_label_update_design.md).

The design keeps the existing Makefile target and command unchanged and proposes a future wrapper label update to `release_quality_check: web logger Rust UTF-16 offset conversion and replay integration`. It does not change Makefile, wrapper, Rust code, tests, fixture JSON, CI workflow, validate / extract / micro_episode behavior, schema-level position_unit behavior, TypeScript/Rust hash work, event durability, or replay-focused remote status.

## 24. Step-web-logger-028 Release-Quality Label Update

Step-web-logger-028 updates the existing wrapper label to `release_quality_check: web logger Rust UTF-16 offset conversion and replay integration`.

The Makefile target name, help text, and command remain unchanged. The wrapper command remains `make check-web-logger-rust-utf16-offset-conversion`, so this target design's Option A command source remains intact.
